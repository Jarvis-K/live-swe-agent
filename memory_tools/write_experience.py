#!/usr/bin/env python3
import sys
import json
from pathlib import Path

def write_experience(record):
    """Persist experience to memory."""
    memory_dir = Path("./memory")
    memory_dir.mkdir(exist_ok=True)

    memory_file = memory_dir / "experiences.jsonl"

    with open(memory_file, "a") as f:
        f.write(json.dumps(record) + "\n")

    return {"status": "success", "file": str(memory_file)}

if __name__ == "__main__":
    data = json.load(sys.stdin)
    result = write_experience(data.get("record", {}))
    print(json.dumps(result))
