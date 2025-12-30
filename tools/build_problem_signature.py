#!/usr/bin/env python3
import json
import sys
import re

def extract_key_symbols(text):
    """Extract function/class names from text."""
    symbols = set()
    symbols.update(re.findall(r'\b[A-Z][a-zA-Z0-9_]*\b', text))
    symbols.update(re.findall(r'\b[a-z_][a-z0-9_]*\([^)]*\)', text))
    return sorted(list(symbols))[:10]

def infer_error_type(text):
    """Infer error type from text."""
    text_lower = text.lower()
    if 'test' in text_lower and 'fail' in text_lower:
        return 'test_failure'
    elif 'exception' in text_lower or 'error' in text_lower:
        return 'exception'
    elif 'performance' in text_lower or 'slow' in text_lower:
        return 'performance'
    elif 'build' in text_lower or 'compile' in text_lower:
        return 'build'
    else:
        return 'wrong_output'

def build_signature(issue_text, repo, failing_tests, trace):
    """Build problem signature from issue details."""
    combined = f"{issue_text} {failing_tests} {trace}"
    
    area = "unknown"
    if '/' in repo:
        area_match = re.search(r'/([^/]+)/', combined)
        if area_match:
            area = area_match.group(1)
    
    signature = {
        "repo": repo,
        "area": area,
        "error_type": infer_error_type(combined),
        "key_symbols": extract_key_symbols(combined),
        "failure_trace_summary": trace[:200] if trace else "No trace",
        "constraints": "Python 3.x"
    }
    
    signature_text = f"{repo} {area} {signature['error_type']} {' '.join(signature['key_symbols'][:5])}"
    
    return {
        "signature": signature,
        "signature_text": signature_text
    }

if __name__ == "__main__":
    data = json.load(sys.stdin)
    result = build_signature(
        data.get("issue_text", ""),
        data.get("repo", ""),
        data.get("failing_tests", ""),
        data.get("trace", "")
    )
    print(json.dumps(result, indent=2))
