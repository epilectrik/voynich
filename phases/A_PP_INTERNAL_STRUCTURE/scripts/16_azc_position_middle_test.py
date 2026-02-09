#!/usr/bin/env python3
"""
Test: Does AZC position have an effect BEYOND vocabulary composition?

If escape rate differences are purely due to MIDDLE composition:
- Different positions have different MIDDLEs
- Different MIDDLEs have different PREFIX preferences
- Therefore different positions have different PREFIX distributions

But if the SAME MIDDLEs appear at different positions with DIFFERENT PREFIX distributions,
then position has an independent effect.

This test checks: For MIDDLEs that appear at multiple positions,
does their PREFIX distribution vary by position?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict
from scipy import stats
import numpy as np

# Load AZC tokens directly
def load_azc_tokens():
    """Load AZC tokens with morphological decomposition."""
    sys.path.insert(0, str(Path('C:/git/voynich/archive/scripts/currier_a_token_generator')))
    from archive.scripts.currier_a_token_generator import decompose_token

    filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

    tokens = []
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
                    folio = parts[2].strip('"').strip()
                    placement = parts[10].strip('"').strip()

                    if token and placement:
                        result = decompose_token(token)
                        prefix = result[0] if result[0] else 'NONE'
                        middle = result[1] if result[1] else ''

                        if middle:
                            tokens.append({
                                'token': token,
                                'folio': folio,
                                'placement': placement,
                                'prefix': prefix,
                                'middle': middle
                            })
    return tokens

def main():
    print("=" * 70)
    print("TEST: Does AZC position affect PREFIX independently of MIDDLE?")
    print("=" * 70)
    print()

    tokens = load_azc_tokens()
    print(f"Loaded {len(tokens)} AZC tokens with valid MIDDLE")
    print()

    # Group by MIDDLE, then by position
    middle_position_prefix = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for t in tokens:
        middle_position_prefix[t['middle']][t['placement']][t['prefix']] += 1

    # Find MIDDLEs that appear at multiple positions with sufficient counts
    multi_position_middles = []

    for middle, positions in middle_position_prefix.items():
        if len(positions) >= 2:
            # Check if each position has enough samples
            valid_positions = {p: prefixes for p, prefixes in positions.items()
                              if sum(prefixes.values()) >= 10}
            if len(valid_positions) >= 2:
                multi_position_middles.append((middle, valid_positions))

    print(f"MIDDLEs appearing at 2+ positions (with n>=10 each): {len(multi_position_middles)}")
    print()

    # For each multi-position MIDDLE, test if PREFIX distribution varies by position
    print("=" * 70)
    print("Testing: Does PREFIX distribution vary by position for same MIDDLE?")
    print("=" * 70)
    print()

    significant_count = 0
    tested_count = 0

    results = []

    for middle, positions in multi_position_middles:
        # Build contingency table: rows = positions, cols = prefixes
        all_prefixes = set()
        for prefixes in positions.values():
            all_prefixes.update(prefixes.keys())
        all_prefixes = sorted(all_prefixes)

        if len(all_prefixes) < 2:
            continue

        # Build matrix
        matrix = []
        pos_labels = []
        for pos, prefixes in sorted(positions.items()):
            row = [prefixes.get(p, 0) for p in all_prefixes]
            if sum(row) >= 10:
                matrix.append(row)
                pos_labels.append(pos)

        if len(matrix) < 2:
            continue

        matrix = np.array(matrix)

        # Chi-squared test
        try:
            chi2, p, dof, expected = stats.chi2_contingency(matrix)
            tested_count += 1

            if p < 0.05:
                significant_count += 1
                results.append({
                    'middle': middle,
                    'positions': pos_labels,
                    'chi2': chi2,
                    'p': p,
                    'matrix': matrix.tolist(),
                    'prefixes': all_prefixes
                })
        except:
            pass

    print(f"Tested {tested_count} MIDDLEs")
    print(f"Significant position effect (p<0.05): {significant_count}")
    print(f"Percentage with position effect: {significant_count/tested_count*100:.1f}%")
    print()

    # Show examples of significant effects
    if results:
        print("=" * 70)
        print("MIDDLEs where position affects PREFIX distribution:")
        print("=" * 70)
        print()

        for r in sorted(results, key=lambda x: x['p'])[:10]:
            print(f"MIDDLE: {r['middle']}")
            print(f"  Positions: {r['positions']}")
            print(f"  Chi2: {r['chi2']:.1f}, p: {r['p']:.4f}")
            print(f"  Prefixes: {r['prefixes']}")
            print(f"  Counts: {r['matrix']}")
            print()

    # Overall conclusion
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print()

    if significant_count / tested_count > 0.20:
        print("POSITION HAS INDEPENDENT EFFECT on PREFIX distribution")
        print("The same MIDDLE shows different PREFIX preferences at different positions.")
        print("This suggests AZC position does something beyond vocabulary composition.")
    elif significant_count / tested_count > 0.05:
        print("WEAK POSITION EFFECT detected")
        print("Some MIDDLEs show position-dependent PREFIX preferences,")
        print("but the effect is not dominant.")
    else:
        print("NO SIGNIFICANT POSITION EFFECT")
        print("PREFIX distribution is determined by MIDDLE, not by position.")
        print("AZC position escape rates are purely vocabulary composition effects.")

if __name__ == "__main__":
    main()
