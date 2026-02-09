#!/usr/bin/env python3
"""
Analyze S-position (spoke) vocabulary in AZC.

C443 says S1, S2 have 0% escape rate.
C496 says S-positions have 75% o-prefixes (ok, ot, o).

What's the actual vocabulary composition at S positions?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter

def load_azc_tokens():
    """Load AZC tokens with morphological decomposition."""
    sys.path.insert(0, str(Path('C:/git/voynich/archive/scripts')))
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
    print("S-POSITION (SPOKE) VOCABULARY ANALYSIS")
    print("=" * 70)
    print()

    tokens = load_azc_tokens()

    # Group by placement
    by_placement = defaultdict(list)
    for t in tokens:
        by_placement[t['placement']].append(t)

    # Show all placements and counts
    print("All AZC placements:")
    for p in sorted(by_placement.keys()):
        print(f"  {p}: {len(by_placement[p])} tokens")
    print()

    # Focus on S-series
    s_placements = [p for p in by_placement.keys() if p.startswith('S')]

    print("=" * 70)
    print("S-SERIES POSITIONS")
    print("=" * 70)
    print()

    for placement in sorted(s_placements):
        toks = by_placement[placement]
        print(f"Position {placement}: {len(toks)} tokens")

        # PREFIX distribution
        prefix_counts = Counter(t['prefix'] for t in toks)
        print(f"  PREFIX distribution:")
        for prefix, count in prefix_counts.most_common():
            pct = count / len(toks) * 100
            print(f"    {prefix}: {count} ({pct:.1f}%)")

        # MIDDLE distribution
        middle_counts = Counter(t['middle'] for t in toks if t['middle'])
        print(f"  Top MIDDLEs:")
        for middle, count in middle_counts.most_common(5):
            pct = count / len(toks) * 100
            print(f"    {middle}: {count} ({pct:.1f}%)")

        # Escape rate (qo/ct)
        escape_count = sum(1 for t in toks if t['prefix'] in {'qo', 'ct'})
        escape_rate = escape_count / len(toks) * 100 if toks else 0
        print(f"  Escape rate (qo/ct): {escape_rate:.1f}%")

        # o-prefix rate (ok/ot/o)
        o_count = sum(1 for t in toks if t['prefix'] in {'ok', 'ot', 'o'})
        o_rate = o_count / len(toks) * 100 if toks else 0
        print(f"  o-prefix rate (ok/ot/o): {o_rate:.1f}%")
        print()

    # Compare S vs R positions
    print("=" * 70)
    print("S-SERIES vs R-SERIES COMPARISON")
    print("=" * 70)
    print()

    r_placements = [p for p in by_placement.keys() if p.startswith('R')]

    s_tokens = [t for p in s_placements for t in by_placement[p]]
    r_tokens = [t for p in r_placements for t in by_placement[p]]

    print(f"S-series total: {len(s_tokens)} tokens")
    print(f"R-series total: {len(r_tokens)} tokens")
    print()

    # PREFIX comparison
    s_prefixes = Counter(t['prefix'] for t in s_tokens)
    r_prefixes = Counter(t['prefix'] for t in r_tokens)

    all_prefixes = set(s_prefixes.keys()) | set(r_prefixes.keys())

    print(f"{'PREFIX':<10} {'S-series':>12} {'R-series':>12}")
    print("-" * 36)
    for prefix in sorted(all_prefixes):
        s_pct = s_prefixes.get(prefix, 0) / len(s_tokens) * 100 if s_tokens else 0
        r_pct = r_prefixes.get(prefix, 0) / len(r_tokens) * 100 if r_tokens else 0
        print(f"{prefix:<10} {s_pct:>11.1f}% {r_pct:>11.1f}%")

    print()

    # MIDDLE comparison - unique to each
    s_middles = set(t['middle'] for t in s_tokens if t['middle'])
    r_middles = set(t['middle'] for t in r_tokens if t['middle'])

    s_only = s_middles - r_middles
    r_only = r_middles - s_middles
    shared = s_middles & r_middles

    print(f"MIDDLEs unique to S-series: {len(s_only)}")
    print(f"MIDDLEs unique to R-series: {len(r_only)}")
    print(f"MIDDLEs shared: {len(shared)}")

    if s_middles | r_middles:
        jaccard = len(shared) / len(s_middles | r_middles)
        print(f"Jaccard similarity: {jaccard:.3f}")

    print()
    print("S-only MIDDLEs:", sorted(s_only)[:15])
    print("R-only MIDDLEs:", sorted(r_only)[:15])

if __name__ == "__main__":
    main()
