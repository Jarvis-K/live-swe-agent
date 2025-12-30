#!/usr/bin/env python3
import json
import sys
import uuid
from datetime import datetime

def extract_bullets(text, max_bullets=6):
    """Extract actionable bullets from text."""
    lines = text.split('\n')
    bullets = []
    for line in lines:
        line = line.strip()
        if line and len(line) > 10 and len(line) < 200:
            if any(keyword in line.lower() for keyword in ['fix', 'change', 'add', 'remove', 'update', 'modify', 'use', 'avoid']):
                bullets.append(line)
                if len(bullets) >= max_bullets:
                    break
    return bullets[:max_bullets]

def distill_experience(signature, outcome, run_log, patch_summary, tests_run):
    """Distill trial into experience record."""
    bullets = extract_bullets(f"{run_log}\n{patch_summary}")
    if not bullets:
        bullets = ["No specific actionable insights extracted"]
    
    root_cause = "Unknown"
    if outcome == "success":
        root_cause = "Issue resolved through code changes"
    else:
        root_cause = "Issue not fully resolved or tests failed"
    
    tags = []
    sig = signature.get("signature", signature)
    if isinstance(sig, dict):
        tags.append(sig.get("area", "unknown"))
        tags.append(sig.get("error_type", "unknown"))
    
    embedding_text = f"{sig.get('repo', '')} {sig.get('area', '')} {sig.get('error_type', '')} {' '.join(bullets)}"
    
    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "outcome": outcome,
        "problem_signature": sig,
        "what_worked_or_failed": bullets,
        "root_cause_hypothesis": root_cause,
        "fix_or_attempt_summary": [patch_summary[:500]] if patch_summary else [],
        "verification": tests_run[:200] if tests_run else "No tests run",
        "tags": tags,
        "embedding_text": embedding_text
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
    print(json.dumps(result, indent=2))
