#!/bin/bash
set -e

# Configuration
CONFIG="${CONFIG:-config/livesweagent_swebench.yaml}"
MODEL="${MODEL:-openai/gpt-5.2}"
SUBSET="${SUBSET:-verified}"
SPLIT="${SPLIT:-test}"
SLICE="${SLICE:-0:5}"
OUTPUT="${OUTPUT:-./results}"
WORKERS="${WORKERS:-1}"

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
echo "=========================================="
echo "Run completed! Results saved to: $OUTPUT"
echo "=========================================="
echo ""
echo "Memory experiences saved to: ./memory/experiences.jsonl"
echo ""
echo "To run with different settings, use environment variables:"
echo "  CONFIG=config/livesweagent_swebench.yaml \\"
echo "  MODEL=claude-sonnet-4 \\"
echo "  SUBSET=verified \\"
echo "  SLICE=0:10 \\"
echo "  ./run.sh"
