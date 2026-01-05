# Memory and Tools Persistence

## Problem
Memory and tools generated during issue resolution were stored only in containers, preventing the agent from learning across multiple runs.

## Solution
The `merge_container_artifacts.py` script extracts memory and tools from Docker containers to the host machine after each run.

### How It Works
1. Scans all SWE-bench Docker containers (running or stopped)
2. Extracts `/testbed/memory/experiences.jsonl` from each container
3. Extracts `/testbed/tools/` directory from each container (if exists)
4. Merges memory records with deduplication by ID
5. Copies new or updated tools to host

### Integration
The script runs automatically after each evaluation via `run.sh`:

```bash
./run.sh  # Automatically calls merge_container_artifacts.py
```

## Usage

### Automatic (Recommended)
Run the full pipeline:

```bash
./run.sh
```

### Manual
To manually extract artifacts from existing containers:

```bash
python3 scripts/merge_container_artifacts.py
```

## How It Works

### Memory Persistence
- Memory records are stored in `./memory/experiences.jsonl` (JSONL format)
- Each record has a unique ID for deduplication
- Script uses `docker cp` to extract from containers
- Handles both running and stopped containers

### Tools Persistence
- Custom tools are stored in `./tools/` directory
- Tools are Python scripts created by the agent
- Newer versions overwrite older ones based on modification time
- Tools are made executable automatically

## Verification
Check that persistence is working:

```bash
# Check memory records
wc -l memory/experiences.jsonl

# Check tools
ls -la tools/

# Run merge script manually
python3 scripts/merge_container_artifacts.py
```

Expected output: "✓ Merged X memory records and Y tools from Z containers"

## Technical Details

### Container Detection
The script identifies SWE-bench containers by searching for "swe-bench" in the image name.

### Deduplication
Memory records are deduplicated by their `id` field to prevent duplicates across multiple runs.

### Error Handling
- Gracefully handles missing files/directories in containers
- Skips malformed JSON records
- Continues processing even if some containers fail
