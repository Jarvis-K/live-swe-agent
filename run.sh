#!/bin/bash
set -e

# Configuration
CONFIG="${CONFIG:-config/livesweagent_swebench.yaml}"
MODEL="${MODEL:-openai/gpt-5.1-codex-mini}"
SUBSET="${SUBSET:-verified}"
SPLIT="${SPLIT:-test}"
SLICE="${SLICE:-0:5}"
OUTPUT="${OUTPUT:-./results}"
WORKERS="${WORKERS:-8}"
GENERATE_MEMORY="${GENERATE_MEMORY:-1}"

echo "=========================================="
echo "Running Memory-Augmented Mini-SWE-Agent"
echo "=========================================="
echo "Config:   $CONFIG"
echo "Model:    $MODEL"
echo "Subset:   $SUBSET"
echo "Split:    $SPLIT"
echo "Slice:    $SLICE"
echo "Output:   $OUTPUT"
echo "Workers:  $WORKERS"
echo "=========================================="
echo ""

# Check if mini-swe-agent is installed
if ! command -v mini-extra &> /dev/null; then
    echo "Error: mini-swe-agent is not installed"
    echo "Please install it first: https://github.com/SWE-agent/mini-swe-agent"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT"

# Generate memory tools
if [ "$GENERATE_MEMORY" = "1" ]; then
    echo "Generating memory tools..."
    python3 scripts/generate_memory_tools.py
else
    echo "Skipping memory tools generation (GENERATE_MEMORY=0)"
fi

echo ""
echo "Running mini-swe-agent with parallel workers..."

# Run mini-swe-agent on SWE-bench
mini-extra swebench \
    --config "$CONFIG" \
    --model "$MODEL" \
    --subset "$SUBSET" \
    --split "$SPLIT" \
    --slice "$SLICE" \
    --output "$OUTPUT" \
    --workers "$WORKERS"

echo ""
echo "Converting to predictions format..."
python3 scripts/convert_to_predictions.py "$OUTPUT" "$MODEL"

echo ""
echo "Merging container artifacts to host..."
python3 scripts/merge_container_artifacts.py

echo ""
echo "=========================================="
echo "Generation completed"
echo "=========================================="
echo "Results stored in: $OUTPUT"
echo "Memory accumulated in: ./memory/"

# Run evaluation unless skipped
if [ "${SKIP_EVAL:-0}" != "1" ]; then
    echo ""
    ./run_eval.sh
fi
