# Running Memory-Augmented Mini-SWE-Agent

This guide explains how to test the memory-augmented agent on SWE-bench problems.

## Quick Start

Run the agent on a small test set (first 3 problems from SWE-bench Verified):

```bash
./run.sh
```

## Configuration Options

Customize the run using environment variables:

### Basic Options

```bash
# Test on more problems (first 10)
SLICE=0:10 ./run.sh

# Use a different model
MODEL=claude-opus-4 ./run.sh

# Test on SWE-bench Lite instead of Verified
SUBSET=lite ./run.sh

# Use multiple workers for parallel processing
WORKERS=4 ./run.sh
```

### Advanced Options

```bash
# Full custom run
CONFIG=config/livesweagent_swebench.yaml \
MODEL=claude-sonnet-4 \
SUBSET=verified \
SPLIT=test \
SLICE=0:20 \
OUTPUT=./my_results \
WORKERS=2 \
./run.sh
```

## Available Subsets

- `verified` - SWE-bench Verified (500 high-quality problems)
- `lite` - SWE-bench Lite (300 problems)
- `test` - Full SWE-bench test set (2,294 problems)

## Memory System

The agent will automatically:
1. **At START**: Build problem signature and retrieve similar past experiences
2. **During execution**: Use retrieved experiences as guidance
3. **At END**: Distill learnings and persist to `./memory/experiences.jsonl`

### Viewing Memory

Check accumulated experiences:

```bash
cat memory/experiences.jsonl | jq .
```

Count experiences:

```bash
wc -l memory/experiences.jsonl
```

View specific experience:

```bash
cat memory/experiences.jsonl | jq 'select(.outcome == "success")'
```

## Results

Results are saved to `./results/` (or custom `$OUTPUT` directory):
- Trajectories (full agent interactions)
- Patches (code changes)
- Evaluation results

## Example Workflows

### 1. Quick Test (3 problems)
```bash
./run.sh
```

### 2. Small Evaluation (10 problems)
```bash
SLICE=0:10 WORKERS=2 ./run.sh
```

### 3. Full Verified Set (500 problems)
```bash
SLICE=0:500 WORKERS=8 OUTPUT=./results_full ./run.sh
```

### 4. Specific Problem Range
```bash
SLICE=10:20 ./run.sh
```

## Monitoring Progress

Watch memory accumulation in real-time:

```bash
watch -n 5 'wc -l memory/experiences.jsonl'
```

View latest experience:

```bash
tail -1 memory/experiences.jsonl | jq .
```

## Troubleshooting

### mini-swe-agent not found
Install mini-swe-agent first:
```bash
pip install mini-swe-agent
```

### Out of memory
Reduce workers:
```bash
WORKERS=1 ./run.sh
```

### API rate limits
Reduce slice size and add delays between runs:
```bash
SLICE=0:5 ./run.sh
sleep 60
SLICE=5:10 ./run.sh
```

## Memory Tool Testing

Test individual memory tools:

```bash
# Test build_problem_signature
echo '{"issue_text": "Fix bug", "repo": "test/repo", "failing_tests": "", "trace": ""}' | \
  python tools/build_problem_signature.py

# Test retrieve_experience
echo '{"signature": {"signature_text": "test"}, "top_k": 5}' | \
  python tools/retrieve_experience.py

# Test distill_experience
echo '{"signature": {"repo": "test"}, "outcome": "success", "run_log": "Fixed", "patch_summary": "Updated", "tests_run": "Passed"}' | \
  python tools/distill_experience.py

# Test write_experience
echo '{"record": {"id": "test", "outcome": "success"}}' | \
  python tools/write_experience.py
```
