#!/usr/bin/env python3
"""Run SWE-bench evaluation on generated predictions."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

def run_evaluation(
    predictions_path,
    dataset_name="princeton-nlp/SWE-bench_Verified",
    split="test",
    max_workers=1,
    timeout=1800,
    run_id="evaluation",
    output_dir=None
):
    """Run SWE-bench evaluation harness."""
    predictions_file = Path(predictions_path)

    if not predictions_file.exists():
        print(f"Error: Predictions file not found: {predictions_file}")
        return False

    # Load predictions to get instance IDs
    with open(predictions_file) as f:
        predictions = json.load(f)

    instance_ids = [p["instance_id"] for p in predictions]

    print("=" * 50)
    print("RUNNING SWE-BENCH EVALUATION")
    print("=" * 50)
    print(f"Dataset: {dataset_name}")
    print(f"Split: {split}")
    print(f"Predictions: {predictions_file}")
    print(f"Instances: {len(instance_ids)}")
    print(f"Max Workers: {max_workers}")
    print(f"Timeout: {timeout}s")
    print(f"Run ID: {run_id}")
    print("=" * 50)
    print()

    # Change to output directory if specified
    original_dir = None
    if output_dir:
        original_dir = Path.cwd()
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        import os
        os.chdir(output_path)

    # Build evaluation command
    cmd = [
        "python", "-m", "swebench.harness.run_evaluation",
        "--dataset_name", dataset_name,
        "--split", split,
        "--predictions_path", str(predictions_file),
        "--max_workers", str(max_workers),
        "--timeout", str(timeout),
        "--run_id", run_id,
        "--cache_level", "env",
    ]

    # Add instance IDs
    cmd.extend(["--instance_ids"] + instance_ids)

    print(f"Running: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("EVALUATION COMPLETED SUCCESSFULLY")
        print("=" * 50)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n" + "=" * 50)
        print(f"EVALUATION FAILED: {e}")
        print("=" * 50)
        return False
    except KeyboardInterrupt:
        print("\n\nEvaluation interrupted by user")
        return False
    finally:
        # Restore original directory
        if original_dir:
            import os
            os.chdir(original_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SWE-bench evaluation")
    parser.add_argument("predictions_path", help="Path to predictions JSON file")
    parser.add_argument("--dataset", default="princeton-nlp/SWE-bench_Verified",
                        help="Dataset name")
    parser.add_argument("--split", default="test", help="Dataset split")
    parser.add_argument("--max-workers", type=int, default=1,
                        help="Maximum number of workers")
    parser.add_argument("--timeout", type=int, default=1800,
                        help="Timeout per instance in seconds")
    parser.add_argument("--run-id", default="evaluation",
                        help="Run ID for this evaluation")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory for evaluation results")

    args = parser.parse_args()

    success = run_evaluation(
        args.predictions_path,
        args.dataset,
        args.split,
        args.max_workers,
        args.timeout,
        args.run_id,
        args.output_dir
    )

    sys.exit(0 if success else 1)
