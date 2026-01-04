#!/usr/bin/env python3
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
