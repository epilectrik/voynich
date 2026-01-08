#!/usr/bin/env python3
"""
Phase Metrics Extractor

Scans a phase directory and extracts key metrics from markdown files.
Useful for quick phase analysis and constraint discovery.

Usage:
    python extract_phase_metrics.py PHASE_NAME
    python extract_phase_metrics.py phases/MORPH-CLOSE/
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent
PHASES_DIR = PROJECT_ROOT / "phases"

def extract_metrics(phase_path):
    """Extract metrics from markdown files in a phase directory."""

    metrics = {
        'percentages': [],
        'counts': [],
        'p_values': [],
        'correlations': [],
        'constraint_refs': [],
        'key_findings': [],
        'tier_mentions': [],
    }

    # Find all markdown files
    md_files = list(phase_path.glob("*.md"))

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
        except:
            continue

        # Extract percentages
        for match in re.finditer(r'(\d+\.?\d*)%', content):
            metrics['percentages'].append(f"{match.group(1)}%")

        # Extract p-values
        for match in re.finditer(r'p\s*[=<]\s*([\d.e-]+)', content, re.IGNORECASE):
            metrics['p_values'].append(f"p={match.group(1)}")

        # Extract correlations
        for match in re.finditer(r'(?:rho|r|ρ)\s*=\s*(-?[\d.]+)', content, re.IGNORECASE):
            metrics['correlations'].append(f"r={match.group(1)}")

        # Extract constraint references
        for match in re.finditer(r'\bC(\d{3,4})\b', content):
            ref = f"C{match.group(1)}"
            if ref not in metrics['constraint_refs']:
                metrics['constraint_refs'].append(ref)

        # Extract tier mentions
        for match in re.finditer(r'Tier\s*(\d)', content, re.IGNORECASE):
            tier = f"Tier {match.group(1)}"
            if tier not in metrics['tier_mentions']:
                metrics['tier_mentions'].append(tier)

        # Extract lines that look like findings (start with - or * and contain key words)
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith(('-', '*')) and any(kw in line.lower() for kw in
                ['confirmed', 'falsified', 'found', 'shows', 'proves', 'indicates', 'suggests']):
                if len(line) < 200:  # Skip very long lines
                    metrics['key_findings'].append(line)

    return metrics

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_phase_metrics.py <PHASE_NAME or path>")
        sys.exit(1)

    phase_arg = sys.argv[1]

    # Determine phase path
    if Path(phase_arg).exists():
        phase_path = Path(phase_arg)
    else:
        phase_path = PHASES_DIR / phase_arg
        if not phase_path.exists():
            # Try with common prefixes
            for prefix in ['', 'phases/']:
                test_path = PROJECT_ROOT / prefix / phase_arg
                if test_path.exists():
                    phase_path = test_path
                    break

    if not phase_path.exists():
        print(f"Phase not found: {phase_arg}")
        print(f"Looked in: {phase_path}")
        sys.exit(1)

    metrics = extract_metrics(phase_path)

    print(f"## Phase Metrics: {phase_path.name}")
    print()

    if metrics['constraint_refs']:
        print(f"**Constraints Referenced:** {', '.join(sorted(set(metrics['constraint_refs'])))}")

    if metrics['tier_mentions']:
        print(f"**Tiers Mentioned:** {', '.join(sorted(set(metrics['tier_mentions'])))}")

    if metrics['p_values']:
        print(f"**P-values:** {', '.join(metrics['p_values'][:10])}")

    if metrics['correlations']:
        print(f"**Correlations:** {', '.join(metrics['correlations'][:10])}")

    if metrics['percentages']:
        print(f"**Key Percentages:** {', '.join(metrics['percentages'][:10])}")

    if metrics['key_findings']:
        print()
        print("**Potential Findings:**")
        for finding in metrics['key_findings'][:10]:
            print(f"  {finding}")

if __name__ == '__main__':
    main()
