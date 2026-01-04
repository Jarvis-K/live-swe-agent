# Live-SWE-Agent Documentation

## Table of Contents
- [Setup Guide](#setup-guide)
- [Usage](#usage)
- [Evaluation Workflow](#evaluation-workflow)
- [Memory System](#memory-system)
- [Troubleshooting](#troubleshooting)

## Setup Guide

Live-SWE-agent is built on top of [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent).

### Installation

1. Install mini-swe-agent:
```bash
pip install mini-swe-agent
```

2. Install SWE-bench (for evaluation):
```bash
pip install swebench
```

3. Ensure Docker is running (required for evaluation):
```bash
docker ps
```

## Usage

### Quick Start

Run the agent on a small test set:
```bash
./run.sh
```

### Configuration Options

Customize runs using environment variables:

```bash
# Test on more problems
SLICE=0:10 ./run.sh

# Use a different model
MODEL=claude-opus-4 ./run.sh

# Test on different subsets
SUBSET=lite ./run.sh  # SWE-bench Lite (300 problems)
SUBSET=verified ./run.sh  # SWE-bench Verified (500 problems)

# Use multiple workers
WORKERS=4 ./run.sh

# Full custom run
CONFIG=config/livesweagent_swebench.yaml \
MODEL=claude-sonnet-4 \
SUBSET=verified \
SLICE=0:20 \
OUTPUT=./my_results \
WORKERS=2 \
./run.sh
```

## Evaluation Workflow

### Understanding the Two-Phase Process

SWE-bench evaluation has two distinct phases:

1. **Inference Phase** (patch generation):
   - Tool: `mini-extra swebench`
   - Generates patches for issues
   - Output: `.traj.json` files with execution logs
   - Does NOT test if patches work

2. **Evaluation Phase** (patch testing):
   - Tool: `swebench.harness.run_evaluation`
   - Applies patches and runs test suites
   - Output: `report.json` with pass/fail results
   - Requires Docker and network access

### Running Complete Workflow

The `run.sh` script handles both phases:
```bash
./run.sh
```

This will:
1. Generate memory tools (if needed)
2. Run agent to generate patches
3. Convert trajectories to predictions format
4. Run evaluation to test patches
5. Analyze and display results

### Running Phases Separately

**Agent only (no evaluation):**
```bash
mini-extra swebench --config config/livesweagent_swebench.yaml \
    --model openai/gpt-5.2 --subset verified --slice 0:5 --output ./results
```

**Evaluate existing results:**
```bash
# 1. Convert trajectories to predictions
python3 scripts/convert_to_predictions.py ./results

# 2. Run evaluation
python3 scripts/run_evaluation.py ./results/predictions.json

# 3. Show results
python3 scripts/analyze_results.py ./results
```

### Output Files

| File | Content |
|------|---------|
| `results/*/*.traj.json` | Agent execution logs |
| `results/predictions.json` | Predictions for evaluation |
| `results/report.json` | Evaluation results (pass/fail) |
| `memory/experiences.jsonl` | Agent memory |

## Memory System

The agent maintains persistent memory to improve performance over time.

### How It Works

1. **At START**: Build problem signature and retrieve similar past experiences
2. **During execution**: Use retrieved experiences as guidance
3. **At END**: Distill learnings and persist to `./memory/experiences.jsonl`

### Memory Components

The memory system uses 4 tools (auto-generated in `./memory_tools/`):
- `build_problem_signature.py` - Extract problem signature from issue
- `retrieve_experience.py` - Retrieve similar past experiences
- `distill_experience.py` - Distill current trial into experience
- `write_experience.py` - Persist experience to memory

### Viewing Memory

Check accumulated experiences:
```bash
cat memory/experiences.jsonl | jq .
```

Count experiences:
```bash
wc -l memory/experiences.jsonl
```

View successful experiences only:
```bash
cat memory/experiences.jsonl | jq 'select(.outcome == "success")'
```

Monitor in real-time:
```bash
watch -n 5 'wc -l memory/experiences.jsonl'
```

## Troubleshooting

### "No evaluation results yet"
Evaluation hasn't been run. Run:
```bash
python3 scripts/run_evaluation.py ./results/predictions.json
```

### Docker errors
- Ensure Docker is running: `docker ps`
- Check disk space: `df -h`
- Try with fewer workers: `WORKERS=1 ./run.sh`

### Evaluation timeout
- Increase timeout in `run_evaluation.py` or use `--timeout 3600`
- Some instances may legitimately timeout if tests are slow

### Network connectivity issues
If you cannot access GitHub (common in restricted regions):

**Option 1: Use GitHub mirror**
```bash
./setup_github_mirror.sh
```

**Option 2: Configure proxy**
```bash
# Edit with your proxy settings
nano setup_git_proxy.sh
./setup_git_proxy.sh
```

**Option 3: Skip evaluation**
```bash
# Just analyze generated patches
python3 scripts/analyze_results.py ./results
```

### Memory not accumulating
- Check if `memory/experiences.jsonl` exists
- Verify agent is calling memory tools (check trajectory files)
- Ensure `generate_memory_tools.py` ran successfully

### mini-swe-agent not found
Install mini-swe-agent:
```bash
pip install mini-swe-agent
```

### Out of memory
Reduce workers:
```bash
WORKERS=1 ./run.sh
```

### API rate limits
Reduce slice size and add delays:
```bash
SLICE=0:5 ./run.sh
sleep 60
SLICE=5:10 ./run.sh
```

## Agent Instructions (for Claude)

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

### Session Completion Workflow

When ending a work session, complete ALL steps:

1. File issues for remaining work
2. Run quality gates (tests, linters, builds)
3. Update issue status
4. **PUSH TO REMOTE** (MANDATORY):
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. Clean up (stashes, prune branches)
6. Verify all changes committed AND pushed
7. Hand off context for next session

**CRITICAL**: Work is NOT complete until `git push` succeeds.
