#!/usr/bin/env python3
"""
Test: Does AZC ring position correlate with B within-line position?

Hypothesis: Outer ring (S, R3) = late in B lines, Inner (C, P) = early in B lines

We already know AZC positions have within-AZC-line ordering.
This tests whether that ordering transfers to B procedures.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict
import numpy as np
from scipy import stats

def main():
    print("=" * 70)
    print("TEST: AZC Ring Position vs B Line Position")
    print("=" * 70)
    print()

    tx = Transcript()
    morph = Morphology()

    # Load AZC tokens with positions
    # Map positions to approximate ring order (outer to inner)
    # Based on physical layout: S = spoke/boundary, R = rings, C/P = center
    ring_order = {
        'S': 0, 'S0': 0, 'S1': 0.1, 'S2': 0.2,  # Spokes (boundary/outer)
        'R3': 0.3, 'R2': 0.5, 'R1': 0.7,         # Rings (outer to inner)
        'P': 0.85, 'C': 1.0, 'C1': 1.0, 'C2': 1.0  # Center (inner)
    }

    # Collect AZC MIDDLEs with their typical ring positions
    azc_middle_positions = defaultdict(list)

    # Read AZC tokens from transcript
    from pathlib import Path
    filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

    sys.path.insert(0, str(Path('C:/git/voynich/archive/scripts')))
    from archive.scripts.currier_a_token_generator import decompose_token

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue
                currier = parts[6].strip('"').strip()
                if currier == 'NA':  # AZC tokens
                    token = parts[0].strip('"').strip().lower()
                    placement = parts[10].strip('"').strip()

                    if token and placement:
                        result = decompose_token(token)
                        middle = result[1] if result[1] else ''

                        if middle and placement in ring_order:
                            azc_middle_positions[middle].append(ring_order[placement])

    # Compute mean ring position for each MIDDLE
    azc_ring_mean = {}
    for middle, positions in azc_middle_positions.items():
        if len(positions) >= 3:  # Require at least 3 occurrences
            azc_ring_mean[middle] = np.mean(positions)

    print(f"AZC MIDDLEs with ring positions: {len(azc_ring_mean)}")

    # Collect B MIDDLEs with their within-line positions
    # Group tokens by folio+line, tracking order of appearance
    b_lines = defaultdict(list)
    current_line_key = None
    line_pos = 0

    for t in tx.currier_b():
        if not t.word.strip():
            continue

        key = (t.folio, t.line)
        if key != current_line_key:
            current_line_key = key
            line_pos = 0
        else:
            line_pos += 1

        m = morph.extract(t.word)
        if m.middle:
            b_lines[key].append((line_pos, m.middle))

    # Now compute normalized positions
    b_middle_positions = defaultdict(list)
    for (folio, line), tokens in b_lines.items():
        n = len(tokens)
        for i, (pos, middle) in enumerate(tokens):
            if n > 1:
                norm_pos = pos / (n - 1) if n > 1 else 0.5
            else:
                norm_pos = 0.5
            b_middle_positions[middle].append(norm_pos)

    # Compute mean B position for each MIDDLE
    b_pos_mean = {}
    for middle, positions in b_middle_positions.items():
        if len(positions) >= 10:  # Require at least 10 B occurrences
            b_pos_mean[middle] = np.mean(positions)

    print(f"B MIDDLEs with line positions: {len(b_pos_mean)}")

    # Find shared MIDDLEs
    shared = set(azc_ring_mean.keys()) & set(b_pos_mean.keys())
    print(f"Shared MIDDLEs: {len(shared)}")
    print()

    if len(shared) < 10:
        print("Insufficient shared MIDDLEs for correlation")
        return

    # Compute correlation
    azc_vals = [azc_ring_mean[m] for m in shared]
    b_vals = [b_pos_mean[m] for m in shared]

    r, p = stats.pearsonr(azc_vals, b_vals)
    rho, p_rho = stats.spearmanr(azc_vals, b_vals)

    print("=" * 70)
    print("CORRELATION: AZC Ring Position vs B Line Position")
    print("=" * 70)
    print()
    print(f"Pearson r: {r:.3f} (p = {p:.4e})")
    print(f"Spearman rho: {rho:.3f} (p = {p_rho:.4e})")
    print()

    # Show examples
    print("=" * 70)
    print("EXAMPLES: MIDDLEs by ring position")
    print("=" * 70)
    print()

    # Sort by AZC ring position
    sorted_middles = sorted(shared, key=lambda m: azc_ring_mean[m])

    print(f"{'MIDDLE':<15} {'AZC Ring':>10} {'B Line Pos':>12} {'N(AZC)':>8} {'N(B)':>8}")
    print("-" * 55)

    # Show outer ring (first 10)
    print("\nOUTER RING (low AZC value = spokes/outer):")
    for m in sorted_middles[:10]:
        print(f"{m:<15} {azc_ring_mean[m]:>10.3f} {b_pos_mean[m]:>12.3f} {len(azc_middle_positions[m]):>8} {len(b_middle_positions[m]):>8}")

    # Show inner (last 10)
    print("\nINNER (high AZC value = center):")
    for m in sorted_middles[-10:]:
        print(f"{m:<15} {azc_ring_mean[m]:>10.3f} {b_pos_mean[m]:>12.3f} {len(azc_middle_positions[m]):>8} {len(b_middle_positions[m]):>8}")

    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if r > 0.3 and p < 0.001:
        print("POSITIVE CORRELATION: Inner ring → Later in B lines")
        print("Outer (S/R3) vocabulary appears early in B procedures")
        print("Inner (C/P) vocabulary appears late in B procedures")
    elif r < -0.3 and p < 0.001:
        print("NEGATIVE CORRELATION: Inner ring → Earlier in B lines")
        print("Inner (C/P) vocabulary appears early in B procedures")
        print("Outer (S/R3) vocabulary appears late in B procedures")
    elif abs(r) < 0.1:
        print("NO CORRELATION: Ring position does not predict B line position")
        print("AZC physical layout is independent of B procedural order")
    else:
        print(f"WEAK/INCONCLUSIVE: r = {r:.3f}")

if __name__ == "__main__":
    main()
