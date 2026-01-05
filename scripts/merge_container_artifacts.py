#!/usr/bin/env python3
"""Extract and merge memory and tools from Docker containers to host."""
import json
import shutil
import subprocess
from pathlib import Path
from typing import Set

def get_swebench_containers():
    """Get all SWE-bench Docker container IDs."""
    result = subprocess.run(
        ["docker", "ps", "-a", "--format", "{{.ID}}\t{{.Image}}"],
        capture_output=True, text=True
    )
    containers = []
    for line in result.stdout.strip().split('\n'):
        if line and 'swe-bench' in line:
            containers.append(line.split('\t')[0])
    return containers

def extract_from_container(container_id: str, src_path: str, dest_path: Path) -> bool:
    """Extract file/directory from container to host."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["docker", "cp", f"{container_id}:{src_path}", str(dest_path)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def merge_memory(container_memory: Path, host_memory: Path) -> int:
    """Merge container memory into host memory, deduplicating by ID."""
    if not container_memory.exists():
        return 0

    host_memory.parent.mkdir(parents=True, exist_ok=True)
    existing_ids: Set[str] = set()

    if host_memory.exists():
        with open(host_memory) as f:
            for line in f:
                if line.strip():
                    try:
                        existing_ids.add(json.loads(line)["id"])
                    except (json.JSONDecodeError, KeyError):
                        continue

    merged = 0
    with open(host_memory, "a") as out:
        with open(container_memory) as inp:
            for line in inp:
                if line.strip():
                    try:
                        record = json.loads(line)
                        if record["id"] not in existing_ids:
                            out.write(line)
                            existing_ids.add(record["id"])
                            merged += 1
                    except (json.JSONDecodeError, KeyError):
                        continue
    return merged

def merge_tools(container_tools: Path, host_tools: Path) -> int:
    """Merge container tools into host tools directory."""
    if not container_tools.exists() or not container_tools.is_dir():
        return 0

    host_tools.mkdir(parents=True, exist_ok=True)
    merged = 0

    for tool_file in container_tools.glob("*.py"):
        dest = host_tools / tool_file.name
        if not dest.exists() or tool_file.stat().st_mtime > dest.stat().st_mtime:
            shutil.copy2(tool_file, dest)
            dest.chmod(0o755)
            merged += 1
    return merged

def main():
    host_memory = Path("./memory/experiences.jsonl")
    host_tools = Path("./tools")
    temp_dir = Path("/tmp/container_artifacts")

    total_memory = 0
    total_tools = 0

    containers = get_swebench_containers()

    for container_id in containers:
        temp_container = temp_dir / container_id
        temp_container.mkdir(parents=True, exist_ok=True)

        # Extract memory
        temp_memory = temp_container / "experiences.jsonl"
        if extract_from_container(container_id, "/testbed/memory/experiences.jsonl", temp_memory):
            total_memory += merge_memory(temp_memory, host_memory)

        # Extract tools directory
        temp_tools = temp_container / "tools"
        if extract_from_container(container_id, "/testbed/tools", temp_tools):
            total_tools += merge_tools(temp_tools, host_tools)

    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    if total_memory > 0 or total_tools > 0:
        print(f"✓ Merged {total_memory} memory records and {total_tools} tools from {len(containers)} containers")
    else:
        print(f"✓ Checked {len(containers)} containers, no new artifacts found")

if __name__ == "__main__":
    main()
