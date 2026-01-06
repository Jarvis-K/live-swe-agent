#!/usr/bin/env python3
"""Analyze SWE-bench results and show statistics."""
import json
import sys
import argparse
from pathlib import Path

def analyze_results(output_dir, baseline_dir=None, compare_with_baseline=False):
    """Analyze results and show statistics."""
    output_path = Path(output_dir)

    # Check for evaluation report first
    report_file = output_path / "report.json"
    if report_file.exists():
        print("\n" + "="*50)
        print("EVALUATION RESULTS")
        print("="*50)
        try:
            with open(report_file) as f:
                report = json.load(f)

            resolved = report.get("resolved", 0)
            total = report.get("total", 0)
            failed = total - resolved
            success_rate = (resolved / total * 100) if total > 0 else 0

            print(f"\nTotal Issues: {total}")
            print(f"Resolved: {resolved}")
            print(f"Failed: {failed}")
            print(f"Success Rate: {success_rate:.1f}%")

            # Show per-instance results if available
            if "resolved_ids" in report:
                print(f"\nResolved instances: {len(report['resolved_ids'])}")
                for instance_id in report["resolved_ids"][:5]:
                    print(f"  ✓ {instance_id}")
                if len(report["resolved_ids"]) > 5:
                    print(f"  ... and {len(report['resolved_ids']) - 5} more")
        except Exception as e:
            print(f"Error reading evaluation report: {e}")
    else:
        # Fall back to trajectory analysis
        print("\n" + "="*50)
        print("TRAJECTORY ANALYSIS (No evaluation results yet)")
        print("="*50)

        # Find all trajectory files
        traj_files = list(output_path.glob("**/*.traj.json"))

        if not traj_files:
            print("No trajectory files found")
            return

        total = len(traj_files)
        submitted = 0

        for traj_file in traj_files:
            try:
                with open(traj_file) as f:
                    data = json.load(f)

                exit_status = data.get("info", {}).get("exit_status", "")
                if exit_status == "Submitted":
                    submitted += 1
            except Exception as e:
                print(f"Error reading {traj_file}: {e}")

        print(f"\nTotal Issues: {total}")
        print(f"Patches Submitted: {submitted}")
        print(f"Not Submitted: {total - submitted}")
        print("\nNote: Run evaluation to get actual success rate")
        print("  python3 run_evaluation.py ./results/predictions.json")

    # Memory statistics
    memory_file = Path("./memory/experiences.jsonl")
    if memory_file.exists():
        with open(memory_file) as f:
            experiences = [json.loads(line) for line in f if line.strip()]

        success_exp = sum(1 for e in experiences if e.get("outcome") == "success")
        failure_exp = sum(1 for e in experiences if e.get("outcome") == "failure")

        print("\n" + "="*50)
        print("MEMORY STATISTICS")
        print("="*50)
        print(f"Total Experiences: {len(experiences)}")
        print(f"Success Experiences: {success_exp}")
        print(f"Failure Experiences: {failure_exp}")
        print(f"Memory File: {memory_file}")
    else:
        print("\n" + "="*50)
        print("MEMORY STATISTICS")
        print("="*50)
        print("No memory file found (./memory/experiences.jsonl)")

    print("="*50 + "\n")

    # Baseline comparison if requested
    if baseline_dir and compare_with_baseline:
        baseline_path = Path(baseline_dir)
        baseline_report = baseline_path / "report.json"

        if baseline_report.exists() and report_file.exists():
            print("\n" + "="*50)
            print("BASELINE COMPARISON")
            print("="*50)

            with open(baseline_report) as f:
                baseline_data = json.load(f)
            with open(report_file) as f:
                memory_data = json.load(f)

            baseline_rate = (baseline_data.get("resolved", 0) / baseline_data.get("total", 1)) * 100
            memory_rate = (memory_data.get("resolved", 0) / memory_data.get("total", 1)) * 100
            improvement = memory_rate - baseline_rate

            print(f"\nBaseline Success Rate: {baseline_rate:.1f}%")
            print(f"Memory-Augmented Success Rate: {memory_rate:.1f}%")
            print(f"Improvement: {improvement:+.1f}%")

            if improvement > 0:
                print("\n✓ Memory system shows improvement!")
            else:
                print("\n✗ No improvement detected. Consider adjusting memory generation.")
            print("="*50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze SWE-bench results")
    parser.add_argument("output_dir", nargs="?", default="./results", help="Results directory")
    parser.add_argument("--baseline", dest="baseline_dir", help="Baseline results directory for comparison")
    parser.add_argument("--compare-with-baseline", action="store_true", help="Compare with baseline")

    args = parser.parse_args()
    analyze_results(args.output_dir, args.baseline_dir, args.compare_with_baseline)
