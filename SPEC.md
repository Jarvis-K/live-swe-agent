# Live-SWE-Agent Specification

## Overview

Live-SWE-Agent is a **learning-focused** AI software engineering agent designed to continuously improve performance on SWE-bench through experience accumulation. The core innovation is a memory-augmented learning system that gathers experiences, distills useful knowledge, and generates custom tools to achieve better results on future issues.

## Primary Goal

**Improve SWE-bench performance through continuous learning** by:
1. Gathering experiences from every issue resolution attempt
2. Distilling concrete, actionable knowledge from successes and failures
3. Generating custom tools that enhance problem-solving capabilities
4. Retrieving and applying relevant past experiences to new issues

## Learning System (Core Innovation)

### Three-Pillar Learning Approach

#### 1. Experience Gathering
Every issue resolution generates an experience record containing:
- **Problem signature**: Repo, area, error type, key symbols, failure traces
- **What worked/failed**: Max 6 concrete bullets (no generic advice)
- **Root cause hypothesis**: 1-3 sentence explanation
- **Fix summary**: Specific edits made
- **Verification results**: Tests run and outcomes
- **Tags**: Categorization for retrieval

#### 2. Knowledge Distillation
Distillation happens at end of each trial via `distill_experience()`:
- Extracts actionable insights from execution logs
- Identifies patterns in successful vs failed approaches
- Filters out generic advice, keeps concrete specifics
- Stores in append-only JSONL format (`./memory/experiences.jsonl`)

#### 3. Tool Generation
Agent creates custom Python tools during execution:
- **Memory tools** (mandatory): 4 tools for experience management
- **Task-specific tools**: Custom utilities for current problem
- **Edit tools**: Specialized file manipulation helpers
- Tools persist across sessions and improve workflow efficiency

### Mandatory Memory Tools

Four auto-generated tools enable the learning loop:

1. **`build_problem_signature.py`**
   - Input: Issue text, repo, failing tests, trace
   - Output: Structured problem signature for retrieval
   - Extracts: Area, error type, key symbols, constraints

2. **`retrieve_experience.py`**
   - Input: Problem signature, top_k (default: 5)
   - Output: Similar past experiences ranked by relevance
   - Uses: Keyword-based similarity matching (min_similarity: 0.15)
   - Deduplicates results

3. **`distill_experience.py`**
   - Input: Signature, outcome, run_log, patch_summary, tests_run
   - Output: Distilled experience record
   - Enforces: Max 6 bullets, concrete details only

4. **`write_experience.py`**
   - Input: Experience record
   - Output: Persisted to `./memory/experiences.jsonl`
   - Format: Append-only JSONL with UUID and timestamp

### Memory-Augmented Workflow

#### At START of Each Issue:
1. Create 4 memory tools if they don't exist
2. Call `build_problem_signature()` with issue details
3. Call `retrieve_experience()` to get top-5 similar experiences
4. Inject retrieved experiences into THOUGHT as guidance:
   ```
   ## Retrieved Experience (Guidance Only)
   Similar successes:
   - [S1] repo/area: bullet points of what worked
   Similar failures:
   - [F1] repo/area: bullet points of what failed
   DO: [actionable advice from successes]
   DON'T: [pitfalls from failures]
   ```

#### During Issue Resolution:
- Agent can retrieve experiences at 3 points:
  - `start` - Initial context gathering
  - `after_fail` - After failed attempts
  - `before_validate` - Before final validation
- Create custom tools as needed for current task
- Follow iterative THOUGHT → COMMAND → OBSERVATION loop

#### At END of Each Trial:
1. Determine outcome (success if tests pass, failure otherwise)
2. Call `distill_experience()` to extract learnings from run log
3. Call `write_experience()` to persist to memory
4. Tools and experiences available for next issue

### Memory Configuration

```yaml
memory:
  enabled: true
  path: "./memory"
  backend: "jsonl"
  retrieve_top_k: 5
  min_similarity: 0.15
  distill_on_every_trial: true
  retrieval_points: [start, after_fail, before_validate]
  dedupe: true
  max_entry_bullets: 6
```

## Agent Execution Model

### Interactive Loop
Agent operates in continuous THOUGHT → COMMAND → OBSERVATION cycle:
1. **THOUGHT**: Reasoning, analysis, retrieved experience guidance
2. **COMMAND**: Single bash command (or chained with && / ||)
3. **OBSERVATION**: Command output, return code, reflection prompt

### Response Format (Mandatory)
```
THOUGHT: Reasoning and analysis here

```bash
single_command_here
```
```

**Critical Rules:**
- Exactly ONE bash code block per response
- Exactly ONE command (or chained commands)
- Each command runs in fresh subshell (no persistent state)
- Must include THOUGHT section explaining reasoning

### Recommended Workflow
1. Analyze codebase by finding and reading relevant files
2. Create script to reproduce the issue
3. Edit source code to resolve the issue
4. Verify fix works by running script again
5. Test edge cases to ensure robustness

### Operational Constraints
- **Step limit**: 250 commands per issue
- **Timeout**: 60 seconds per command
- **Cost limit**: $3 per issue
- **Working directory**: `/testbed` (all commands execute here)
- **Environment**: Docker container, fresh subshell per command
- **Modifiable**: Source code files only
- **Non-modifiable**: Tests, configuration files (pyproject.toml, setup.cfg)

### Tool Creation Philosophy
Agent is **encouraged to create custom tools** rather than rely solely on bash:
- Create edit tools for effective file manipulation
- Build task-specific utilities for current problem
- Tools should have informative outputs and error messages
- Tools can be specialized, not necessarily general-purpose
- Example: Custom viewer for selective line display instead of head/tail

## Experience Record Schema

```json
{
  "id": "uuid",
  "timestamp": "ISO-8601",
  "outcome": "success|failure",
  "problem_signature": {
    "repo": "owner/repo",
    "area": "module_name",
    "error_type": "test_failure|exception|wrong_output|performance|build",
    "key_symbols": ["function_name", "class_name"],
    "failure_trace_summary": "brief description",
    "constraints": "python version, dependencies"
  },
  "what_worked_or_failed": [
    "concrete bullet 1",
    "concrete bullet 2"
  ],
  "root_cause_hypothesis": "1-3 sentence explanation",
  "fix_or_attempt_summary": [
    "edit 1: file.py:123 changed X to Y",
    "edit 2: added validation in function Z"
  ],
  "verification": "ran test_foo.py::test_bar - passed",
  "tags": ["tag1", "tag2"],
  "embedding_text": "text for similarity search"
}
```

**Quality Requirements:**
- Max 6 bullets in `what_worked_or_failed`
- No generic advice (e.g., "check logs", "read docs")
- Concrete specifics only (e.g., "added null check at line 45")
- No raw logs or secrets
- Treat as guidance, not ground truth

## Two-Phase Execution Pipeline

### Phase 1: Inference (Patch Generation)
1. Load issue dataset (SWE-bench Verified/Lite/Pro)
2. Initialize memory system
3. For each issue:
   - **START**: Retrieve experiences, create memory tools
   - Execute agent in Docker container (THOUGHT → COMMAND → OBSERVATION)
   - Generate patch and trajectory
   - **END**: Distill and persist new experience
4. Convert trajectories to predictions format

### Phase 2: Evaluation (Patch Testing)
1. Load generated predictions
2. Apply patches to repositories
3. Run test suites in isolated Docker environments
4. Generate `report.json` with pass/fail results

## Configuration Details

### Agent Configuration (`config/livesweagent_swebench.yaml`)

**System Template:**
- Agent is helpful assistant interacting with computer shell
- Must respond with exactly ONE bash code block
- Must include THOUGHT section before command
- Failure to follow format causes rejection

**Instance Template:**
- Provides PR description as task
- Explains interactive process (think → command → observe)
- Defines boundaries (modify source, don't modify tests)
- Includes recommended workflow
- Emphasizes tool creation instructions
- **Mandates memory module usage**

**Action Observation Template:**
- Shows return code and output
- Prompts reflection on tool creation after each command
- Truncates output over 10,000 characters (shows head/tail)

**Limits:**
- `step_limit: 250`
- `cost_limit: 3.0`
- `timeout: 60` seconds

**Model:**
- `temperature: 0.0` (deterministic)
- Model name configurable (Claude Opus 4.5, Gemini 3 Pro)

## Output Artifacts

### Trajectory Files (`.traj.json`)
Complete execution logs including:
- All thoughts and commands
- Observations and outputs
- Tool usage and results
- Memory retrievals and distillations

### Predictions Format
```json
{
  "instance_id": "repo__issue-123",
  "model_patch": "diff content",
  "model_name_or_path": "model-id"
}
```

### Evaluation Report (`report.json`)
```json
{
  "instance_id": "repo__issue-123",
  "resolved": true/false
}
```

### Memory Storage (`memory/experiences.jsonl`)
Append-only JSONL file with accumulated experiences

## Performance Benchmarks

**Current Results:**
- **SWE-bench Verified**: 79.2% (Claude Opus 4.5), 77.4% (Gemini 3 Pro)
- **SWE-bench Pro**: 45.8%

**Performance Improvement Strategy:**
1. Accumulate experiences across many issues
2. Distill concrete, actionable patterns
3. Generate specialized tools for common tasks
4. Retrieve and apply relevant experiences to new issues
5. Continuous learning loop improves results over time

## Usage

### Generate Patches
```bash
./run_gen.sh
```

### Evaluate Patches
```bash
./run_eval.sh
```

### Full Pipeline
```bash
./run.sh
```

### Analyze Results
```bash
python scripts/analyze_results.py
```

### Generate Memory Tools
```bash
python scripts/generate_memory_tools.py
```

## Key Design Principles

### 1. Learning-First Architecture
The system is designed around continuous improvement:
- Every issue contributes to knowledge base
- Failures are learning opportunities
- Success patterns are captured and reused
- Tools evolve based on needs

### 2. Concrete Over Generic
Experience records must be specific:
- "Added null check at line 45" ✓
- "Check for edge cases" ✗
- "Changed loop condition from < to <=" ✓
- "Fix the logic" ✗

### 3. Tool Generation Encouraged
Agent should create tools proactively:
- Don't rely solely on basic bash commands
- Build utilities that improve workflow
- Specialize tools for current task
- Persist tools for future use

### 4. Experience as Guidance
Retrieved experiences inform but don't dictate:
- Use as starting point, not ground truth
- Adapt to current context
- Combine insights from multiple experiences
- Override when current situation differs

## Extension Points

### Custom Memory Backends
Modify `memory.backend` to use different storage (currently JSONL)

### Custom Retrieval Strategies
Adjust `retrieve_top_k`, `min_similarity` for different retrieval behavior

### Custom Datasets
Set `DATASET` and `SPLIT` environment variables for different SWE-bench datasets

### Model Selection
Update `model.model_name` in config for different LLMs

### Retrieval Points
Modify `memory.retrieval_points` to retrieve at different stages:
- `start` - Beginning of issue
- `after_fail` - After failed attempts
- `before_validate` - Before final validation
