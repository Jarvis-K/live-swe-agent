#!/usr/bin/env python3
"""Convert mini-swe-agent trajectory files to SWE-bench predictions format."""
import json
import sys
from pathlib import Path

def convert_trajectories_to_predictions(results_dir, model_name="mini-swe-agent"):
    """Convert .traj.json files to predictions format for evaluation."""
    results_path = Path(results_dir)
    predictions = []

    # Find all trajectory files
    traj_files = list(results_path.glob("**/*.traj.json"))

    if not traj_files:
        print(f"No trajectory files found in {results_dir}")
        return None

    print(f"Found {len(traj_files)} trajectory files")

    for traj_file in traj_files:
        try:
            with open(traj_file) as f:
                data = json.load(f)

            # Extract instance_id from filename (e.g., astropy__astropy-13453.traj.json)
            instance_id = traj_file.stem.replace(".traj", "")

            # Extract patch from submission
            submission = data.get("info", {}).get("submission", "")

            if submission:
                predictions.append({
                    "instance_id": instance_id,
                    "model_name_or_path": model_name,
                    "model_patch": submission
                })
                print(f"  ✓ {instance_id}")
            else:
                print(f"  ✗ {instance_id} (no submission)")

        except Exception as e:
            print(f"  ✗ {traj_file.name}: {e}")

    if not predictions:
        print("No valid predictions found")
        return None

    # Write predictions file
    predictions_file = results_path / "predictions.json"
    with open(predictions_file, "w") as f:
        json.dump(predictions, f, indent=2)

    print(f"\nWrote {len(predictions)} predictions to {predictions_file}")
    return predictions_file

if __name__ == "__main__":
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "./results"
    model_name = sys.argv[2] if len(sys.argv) > 2 else "mini-swe-agent"

    predictions_file = convert_trajectories_to_predictions(results_dir, model_name)
    if predictions_file:
        print(f"\nPredictions file: {predictions_file}")
    else:
        sys.exit(1)
