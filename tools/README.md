# Memory Module Tools

These tools implement the persistent memory system for mini-swe-agent.

## Tools

### 1. build_problem_signature.py
Extracts a normalized problem signature from issue details.

**Input (JSON via stdin):**
```json
{
  "issue_text": "Description of the issue",
  "repo": "owner/repo",
  "failing_tests": "test names",
  "trace": "error trace"
}
```

**Output:**
```json
{
  "signature": {...},
  "signature_text": "normalized text for similarity"
}
```

**Usage:**
```bash
echo '{"issue_text": "...", "repo": "...", ...}' | python tools/build_problem_signature.py
```

### 2. retrieve_experience.py
Retrieves similar past experiences from memory.

**Input (JSON via stdin):**
```json
{
  "signature": {"signature_text": "..."},
  "top_k": 5
}
```

**Output:**
```json
{
  "similar_success": [...],
  "similar_failures": [...],
  "do_and_dont": {"do": [...], "dont": [...]}
}
```

**Usage:**
```bash
echo '{"signature": {...}, "top_k": 5}' | python tools/retrieve_experience.py
```

### 3. distill_experience.py
Distills current trial into an experience record.

**Input (JSON via stdin):**
```json
{
  "signature": {...},
  "outcome": "success|failure",
  "run_log": "log text",
  "patch_summary": "changes made",
  "tests_run": "test results"
}
```

**Output:** Experience record (JSON)

**Usage:**
```bash
echo '{"signature": {...}, "outcome": "success", ...}' | python tools/distill_experience.py
```

### 4. write_experience.py
Persists experience record to ./memory/experiences.jsonl

**Input (JSON via stdin):**
```json
{
  "record": {...}
}
```

**Output:**
```json
{
  "status": "success",
  "message": "...",
  "record_id": "..."
}
```

**Usage:**
```bash
echo '{"record": {...}}' | python tools/write_experience.py
```

## Memory Workflow

**At START of each issue:**
1. Call `build_problem_signature.py` with issue details
2. Call `retrieve_experience.py` to get similar experiences
3. Use retrieved experience as guidance

**At END of each trial:**
1. Determine outcome (success/failure)
2. Call `distill_experience.py` to extract learnings
3. Call `write_experience.py` to persist

## Storage

- Memory is stored in `./memory/experiences.jsonl`
- Each line is a JSON experience record
- Simple keyword-based similarity for retrieval
