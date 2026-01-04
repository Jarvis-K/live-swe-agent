#!/bin/bash
set -e

# Configuration
CONFIG="${CONFIG:-config/livesweagent_swebench.yaml}"
MODEL="${MODEL:-openai/gpt-5.2}"
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
echo "=========================================="
echo "Running evaluation..."
echo "=========================================="

# Check if evaluation should be skipped
if [ "${SKIP_EVAL:-0}" = "1" ]; then
    echo "Skipping evaluation (SKIP_EVAL=1)"
else
    # Determine dataset name based on subset
    DATASET="princeton-nlp/SWE-bench_Verified"
    if [ "$SUBSET" = "lite" ]; then
        DATASET="princeton-nlp/SWE-bench_Lite"
    fi

    # Run evaluation
    if python3 scripts/run_evaluation.py "$OUTPUT/predictions.json" \
        --dataset "$DATASET" \
        --split "$SPLIT" \
        --max-workers "$WORKERS" \
        --timeout 1800 \
        --run-id "$(basename $OUTPUT)"; then
        echo ""
        echo "Evaluation completed successfully"
    else
        echo ""
        echo "Evaluation failed"
        echo "You can run it manually later with:"
        echo "  python3 scripts/run_evaluation.py $OUTPUT/predictions.json"
    fi
fi

echo ""
echo "=========================================="
echo "Analyzing results..."
echo "=========================================="
python3 scripts/analyze_results.py "$OUTPUT"

echo ""
echo "=========================================="
echo "Execution completed"
echo "=========================================="
echo "Results stored in: $OUTPUT"
echo "Memory accumulated in: ./memory/"
