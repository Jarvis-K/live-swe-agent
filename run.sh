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
RUNS="${RUNS:-3 }"

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
echo "Runs:     $RUNS"
echo "=========================================="
echo ""

# Check if mini-swe-agent is installed
if ! command -v mini-extra &> /dev/null; then
    echo "Error: mini-swe-agent is not installed"
    echo "Please install it first: https://github.com/SWE-agent/mini-swe-agent"
    exit 1
fi

# Create base output directory
mkdir -p "$OUTPUT"

# Run multiple iterations
for ((run=1; run<=RUNS; run++)); do
    echo ""
    echo "=========================================="
    echo "Starting Run $run of $RUNS"
    echo "=========================================="

    # Generate/update memory tools before each run
    echo "Generating memory tools (accumulating from previous runs)..."
    python3 scripts/generate_memory_tools.py

    # Create run-specific output directory
    RUN_OUTPUT="$OUTPUT/run_$run"
    mkdir -p "$RUN_OUTPUT"

    echo ""
    echo "Running mini-swe-agent (Run $run)..."

    # Run mini-swe-agent on SWE-bench
    mini-extra swebench \
        --config "$CONFIG" \
        --model "$MODEL" \
        --subset "$SUBSET" \
        --split "$SPLIT" \
        --slice "$SLICE" \
        --output "$RUN_OUTPUT" \
        --workers "$WORKERS"

    echo ""
    echo "Run $run completed. Memory and tools available for next run."
done

echo ""
echo "=========================================="
echo "Post-processing all runs..."
echo "=========================================="

# Process each run's results
for ((run=1; run<=RUNS; run++)); do
    RUN_OUTPUT="$OUTPUT/run_$run"

    echo ""
    echo "Converting Run $run to predictions format..."
    python3 scripts/convert_to_predictions.py "$RUN_OUTPUT" "$MODEL"
done

# Use the last run for evaluation (most improved)
FINAL_RUN="$OUTPUT/run_$RUNS"

echo ""
echo "=========================================="
echo "Running evaluation on final run..."
echo "=========================================="
echo "NOTE: Evaluation requires GitHub access and can take 30+ min per instance"
echo "Set SKIP_EVAL=1 to skip evaluation, or press Ctrl+C to skip"
echo ""

# Check if evaluation should be skipped
if [ "${SKIP_EVAL:-0}" = "1" ]; then
    echo "Skipping evaluation (SKIP_EVAL=1)"
else
    # Determine dataset name based on subset
    DATASET="princeton-nlp/SWE-bench_Verified"
    if [ "$SUBSET" = "lite" ]; then
        DATASET="princeton-nlp/SWE-bench_Lite"
    fi

    # Run evaluation (allow user to skip with Ctrl+C)
    if python3 scripts/run_evaluation.py "$FINAL_RUN/predictions.json" \
        --dataset "$DATASET" \
        --split "$SPLIT" \
        --max-workers "$WORKERS" \
        --timeout 1800 \
        --run-id "$(basename $OUTPUT)_run_$RUNS"; then
        echo ""
        echo "Evaluation completed successfully"
    else
        echo ""
        echo "Evaluation was skipped or failed"
        echo "Common issues:"
        echo "  - Network connectivity to GitHub (see NETWORK_ISSUE.md)"
        echo "  - Docker build failures"
        echo ""
        echo "You can run it manually later with:"
        echo "  python3 scripts/run_evaluation.py $FINAL_RUN/predictions.json"
    fi
fi

echo ""
echo "=========================================="
echo "Analyzing results across all runs..."
echo "=========================================="

# Analyze each run
for ((run=1; run<=RUNS; run++)); do
    RUN_OUTPUT="$OUTPUT/run_$run"
    echo ""
    echo "--- Run $run Results ---"
    python3 scripts/analyze_results.py "$RUN_OUTPUT"
done

echo ""
echo "=========================================="
echo "Multi-run execution completed"
echo "=========================================="
echo "Total runs: $RUNS"
echo "Results stored in: $OUTPUT/run_1 through $OUTPUT/run_$RUNS"
echo "Memory accumulated in: ./memory/"
echo ""
echo "To run with different settings, use environment variables:"
echo "  CONFIG=config/livesweagent_swebench.yaml \\"
echo "  MODEL=claude-sonnet-4 \\"
echo "  SUBSET=verified \\"
echo "  SLICE=0:10 \\"
echo "  RUNS=3 \\"
echo "  ./run.sh"
