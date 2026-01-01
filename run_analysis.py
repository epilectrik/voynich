#!/usr/bin/env python3
"""
Voynich Manuscript Analysis Runner

Runs all statistical analyses and saves results.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def run_analysis(script_name: str, output_file: str):
    """Run an analysis script and save output."""
    script_path = PROJECT_ROOT / "analysis" / "statistical" / script_name
    output_path = PROJECT_ROOT / "results" / output_file

    print(f"Running {script_name}...")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=300
        )
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
            if result.stderr:
                f.write("\n\n--- ERRORS ---\n")
                f.write(result.stderr)
        print(f"  -> Saved to {output_file}")
    except Exception as e:
        print(f"  -> Error: {e}")


def main():
    print("=" * 60)
    print("VOYNICH MANUSCRIPT ANALYSIS SUITE")
    print("=" * 60)
    print()

    # Ensure results directory exists
    results_dir = PROJECT_ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    # Run all analyses
    analyses = [
        ("stats.py", "baseline_statistics.txt"),
        ("compare_languages.py", "language_comparison.txt"),
        ("position_constraints.py", "position_constraints.txt"),
    ]

    for script, output in analyses:
        run_analysis(script, output)

    print()
    print("=" * 60)
    print("Analysis complete! Results saved to ./results/")
    print("=" * 60)


if __name__ == "__main__":
    main()
