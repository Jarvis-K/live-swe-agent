#!/usr/bin/env python3
"""Generate memory module tools if they don't exist."""
import os
from pathlib import Path

TOOLS_DIR = Path("./memory_tools")
MEMORY_DIR = Path("./memory")

TOOLS = {
    "build_problem_signature.py": '''#!/usr/bin/env python3
import sys
import json
import re

def build_problem_signature(issue_text, repo, failing_tests="", trace=""):
    """Extract problem signature from issue."""
    # Infer area from issue text
    area = "unknown"
    for keyword in ["print", "parse", "solve", "simplify", "integrate", "diff"]:
        if keyword in issue_text.lower():
            area = keyword
            break

    # Infer error type
    error_type = "test_failure"
    if "exception" in trace.lower() or "error" in trace.lower():
        error_type = "exception"
    elif "wrong" in issue_text.lower() or "incorrect" in issue_text.lower():
        error_type = "wrong_output"

    # Extract key symbols
    key_symbols = re.findall(r'`([a-zA-Z_][a-zA-Z0-9_]*)`', issue_text)[:5]

    signature = {
        "repo": repo,
        "area": area,
        "error_type": error_type,
        "key_symbols": key_symbols,
        "failure_trace_summary": trace[:200] if trace else issue_text[:200],
        "constraints": "python"
    }

    signature_text = f"{repo} {area} {error_type} {' '.join(key_symbols)}"

    return {"signature": signature, "signature_text": signature_text}

if __name__ == "__main__":
    data = json.load(sys.stdin)
    result = build_problem_signature(
        data.get("issue_text", ""),
        data.get("repo", ""),
        data.get("failing_tests", ""),
        data.get("trace", "")
    )
    print(json.dumps(result))
''',

    "retrieve_experience.py": '''#!/usr/bin/env python3
import sys
import json
from pathlib import Path

def retrieve_experience(signature, top_k=5):
    """Retrieve similar experiences from memory."""
    memory_file = Path("./memory/experiences.jsonl")

    if not memory_file.exists():
        return {
            "similar_success": [],
            "similar_failures": [],
            "do_and_dont": {"do": [], "dont": []}
        }

    experiences = []
    with open(memory_file) as f:
        for line in f:
            if line.strip():
                experiences.append(json.loads(line))

    # Simple keyword matching
    sig_text = signature.get("signature_text", "").lower()
    keywords = set(sig_text.split())

    scored = []
    for exp in experiences:
        exp_text = exp.get("embedding_text", "").lower()
        exp_keywords = set(exp_text.split())
        score = len(keywords & exp_keywords) / max(len(keywords), 1)
        if score > 0.15:
            scored.append((score, exp))

    scored.sort(reverse=True, key=lambda x: x[0])
    top = scored[:top_k]

    successes = [exp for _, exp in top if exp["outcome"] == "success"]
    failures = [exp for _, exp in top if exp["outcome"] == "failure"]

    do_list = []
    dont_list = []
    for exp in successes[:3]:
        do_list.extend(exp.get("what_worked_or_failed", [])[:2])
    for exp in failures[:3]:
        dont_list.extend(exp.get("what_worked_or_failed", [])[:2])

    return {
        "similar_success": successes,
        "similar_failures": failures,
        "do_and_dont": {"do": do_list[:5], "dont": dont_list[:5]}
    }

if __name__ == "__main__":
    data = json.load(sys.stdin)
    result = retrieve_experience(data.get("signature", {}), data.get("top_k", 5))
    print(json.dumps(result))
''',

    "distill_experience.py": '''#!/usr/bin/env python3
import sys
import json
import uuid
from datetime import datetime

def distill_experience(signature, outcome, run_log, patch_summary, tests_run):
    """Distill trial into experience record."""
    # Extract key learnings from log
    learnings = []
    if outcome == "success":
        if "edit" in run_log.lower():
            learnings.append("Successfully edited source files to fix issue")
        if "test" in run_log.lower():
            learnings.append("Verified fix with test execution")
    else:
        if "error" in run_log.lower():
            learnings.append("Encountered errors during execution")
        if "timeout" in run_log.lower():
            learnings.append("Command timed out, need different approach")

    # Limit to 6 bullets
    learnings = learnings[:6]

    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "outcome": outcome,
        "problem_signature": signature,
        "what_worked_or_failed": learnings,
        "root_cause_hypothesis": patch_summary[:200] if patch_summary else "No clear root cause identified",
        "fix_or_attempt_summary": [patch_summary[:100]] if patch_summary else [],
        "verification": tests_run[:100] if tests_run else "No tests run",
        "tags": [signature.get("area", ""), signature.get("error_type", "")],
        "embedding_text": f"{signature.get('repo', '')} {signature.get('area', '')} {signature.get('error_type', '')} {' '.join(learnings)}"
    }

    return record

if __name__ == "__main__":
    data = json.load(sys.stdin)
    result = distill_experience(
        data.get("signature", {}),
        data.get("outcome", "failure"),
        data.get("run_log", ""),
        data.get("patch_summary", ""),
        data.get("tests_run", "")
    )
    print(json.dumps(result))
''',

    "write_experience.py": '''#!/usr/bin/env python3
import sys
import json
from pathlib import Path

def write_experience(record):
    """Persist experience to memory."""
    memory_dir = Path("./memory")
    memory_dir.mkdir(exist_ok=True)

    memory_file = memory_dir / "experiences.jsonl"

    with open(memory_file, "a") as f:
        f.write(json.dumps(record) + "\\n")

    return {"status": "success", "file": str(memory_file)}

if __name__ == "__main__":
    data = json.load(sys.stdin)
    result = write_experience(data.get("record", {}))
    print(json.dumps(result))
'''
}

def main():
    """Generate memory tools."""
    TOOLS_DIR.mkdir(exist_ok=True)
    MEMORY_DIR.mkdir(exist_ok=True)

    print("Generating memory tools...")
    for name, content in TOOLS.items():
        tool_path = TOOLS_DIR / name
        if tool_path.exists():
            print(f"  ✓ {name} already exists")
        else:
            tool_path.write_text(content)
            tool_path.chmod(0o755)
            print(f"  + Created {name}")

    print(f"\nMemory tools ready in {TOOLS_DIR}/")
    print(f"Memory storage ready in {MEMORY_DIR}/")

if __name__ == "__main__":
    main()
