#!/usr/bin/env python3
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
