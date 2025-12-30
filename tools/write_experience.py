#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def write_experience(record):
    """Write experience record to memory."""
    memory_path = Path("./memory")
    memory_path.mkdir(exist_ok=True)
    
    experiences_file = memory_path / "experiences.jsonl"
    
    with open(experiences_file, "a") as f:
        f.write(json.dumps(record) + "\n")
    
    return {
        "status": "success",
        "message": f"Experience {record.get('id', 'unknown')} written to {experiences_file}",
        "record_id": record.get("id")
    }

if __name__ == "__main__":
    data = json.load(sys.stdin)
    result = write_experience(data.get("record", data))
    print(json.dumps(result, indent=2))
