#!/usr/bin/env python3
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
