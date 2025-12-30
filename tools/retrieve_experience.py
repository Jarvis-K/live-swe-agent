#!/usr/bin/env python3
import json
import sys
import os
from pathlib import Path

def compute_similarity(text1, text2):
    """Simple keyword-based similarity."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)

def retrieve_experiences(signature, top_k=5):
    """Retrieve similar experiences from memory."""
    memory_path = Path("./memory")
    if not memory_path.exists():
        return {
            "similar_success": [],
            "similar_failures": [],
            "do_and_dont": {"do": [], "dont": []}
        }
    
    experiences = []
    for jsonl_file in memory_path.glob("*.jsonl"):
        with open(jsonl_file) as f:
            for line in f:
                if line.strip():
                    experiences.append(json.loads(line))
    
    if not experiences:
        return {
            "similar_success": [],
            "similar_failures": [],
            "do_and_dont": {"do": [], "dont": []}
        }
    
    query_text = signature.get("signature_text", "")
    
    scored = []
    for exp in experiences:
        sim = compute_similarity(query_text, exp.get("embedding_text", ""))
        scored.append((sim, exp))
    
    scored.sort(reverse=True, key=lambda x: x[0])
    top_experiences = [exp for _, exp in scored[:top_k]]
    
    successes = [e for e in top_experiences if e.get("outcome") == "success"]
    failures = [e for e in top_experiences if e.get("outcome") == "failure"]
    
    do_list = []
    dont_list = []
    for exp in successes:
        do_list.extend(exp.get("what_worked_or_failed", [])[:2])
    for exp in failures:
        dont_list.extend(exp.get("what_worked_or_failed", [])[:2])
    
    return {
        "similar_success": successes[:3],
        "similar_failures": failures[:3],
        "do_and_dont": {
            "do": do_list[:5],
            "dont": dont_list[:5]
        }
    }

if __name__ == "__main__":
    data = json.load(sys.stdin)
    result = retrieve_experiences(
        data.get("signature", {}),
        data.get("top_k", 5)
    )
    print(json.dumps(result, indent=2))
