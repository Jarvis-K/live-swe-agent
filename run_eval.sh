#!/bin/bash
set -e

# Configuration
OUTPUT="${OUTPUT:-./results}"
SUBSET="${SUBSET:-verified}"
SPLIT="${SPLIT:-test}"
WORKERS="${WORKERS:-8}"

echo "=========================================="
echo "Running evaluation..."
echo "=========================================="

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
    --run-id "$(basename $OUTPUT)" \
    --output-dir "$OUTPUT"; then
    echo ""
    echo "Evaluation completed successfully"
else
    echo ""
    echo "Evaluation failed"
    echo "You can run it manually later with:"
    echo "  python3 scripts/run_evaluation.py $OUTPUT/predictions.json"
    exit 1
fi

echo ""
echo "=========================================="
echo "Analyzing results..."
echo "=========================================="
python3 scripts/analyze_results.py "$OUTPUT"

echo ""
echo "=========================================="
echo "Evaluation completed"
echo "=========================================="
echo "Results stored in: $OUTPUT"
