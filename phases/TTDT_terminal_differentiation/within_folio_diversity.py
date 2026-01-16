#!/usr/bin/env python3
"""
Within-Folio Output Diversity Test

Question: How many distinct outputs can each B folio produce?

If each B folio handles one material class with multiple product variants,
we'd expect:
- Multiple distinct MIDDLEs per folio (MIDDLE = variant discriminator)
- ~4-5+ MIDDLEs per folio would support "83 materials x N products" model

Method:
1. For each B folio, count distinct MIDDLEs
2. Analyze distribution of MIDDLE counts
3. Estimate total output capacity (83 folios x avg MIDDLEs)
"""

import json
import csv
import statistics
from pathlib import Path
from collections import defaultdict, Counter

BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
RESULTS_PATH = BASE_PATH / "results"
OUTPUT_FILE = RESULTS_PATH / "within_folio_diversity.json"

# Morphological parsing (from existing code)
PREFIXES = ['qo', 'ch', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'lk', 'lch', 'yk', 'yt', 'ke', 'sa', 'so', 'al', 'op', 'lo']
SUFFIXES = [
    'aiin', 'aiiin', 'ain', 'iin', 'in',
    'ar', 'or', 'al', 'ol', 'am', 'an',
    'dy', 'edy', 'eedy', 'chy', 'shy', 'ty', 'ky', 'ly', 'ry', 'y',
    'r', 'l', 's', 'd', 'n', 'm'
]


def decompose_token(token):
    """Extract MIDDLE from token."""
    if not token or len(token) < 2:
        return None
    if token.startswith('[') or token.startswith('<') or '*' in token:
        return None

    rest = token
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            rest = token[len(p):]
            break

    middle = rest
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            middle = rest[:-len(s)]
            break

    return middle if middle else None


def load_b_folios():
    """Load B folio tokens."""
    # Get B folio list
    with open(RESULTS_PATH / "unified_folio_profiles.json") as f:
        profiles = json.load(f)
    b_folios = set(f for f, p in profiles["profiles"].items() if p.get("system") == "B")

    # Load tokens per B folio
    folio_tokens = defaultdict(list)
    with open(DATA_FILE, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            folio = row['folio']
            word = row['word'].strip('"')
            lang = row['language']
            if lang == 'B' and folio in b_folios:
                folio_tokens[folio].append(word)

    return folio_tokens, b_folios


def main():
    print("=" * 70)
    print("WITHIN-FOLIO OUTPUT DIVERSITY TEST")
    print("=" * 70)

    folio_tokens, b_folios = load_b_folios()

    print(f"\nB folios with tokens: {len(folio_tokens)}")
    print(f"Total B folios: {len(b_folios)}")

    # Count MIDDLEs per folio
    folio_middles = {}
    folio_middle_counts = {}

    for folio, tokens in folio_tokens.items():
        middles = set()
        middle_counter = Counter()

        for token in tokens:
            middle = decompose_token(token)
            if middle:
                middles.add(middle)
                middle_counter[middle] += 1

        folio_middles[folio] = middles
        folio_middle_counts[folio] = {
            'n_distinct': len(middles),
            'n_tokens': len(tokens),
            'top_middles': middle_counter.most_common(5)
        }

    # Summary statistics
    n_middles = [v['n_distinct'] for v in folio_middle_counts.values()]

    print("\n" + "-" * 70)
    print("MIDDLE DIVERSITY PER B FOLIO")
    print("-" * 70)

    print(f"\n  Distinct MIDDLEs per folio:")
    print(f"    Min:    {min(n_middles)}")
    print(f"    Max:    {max(n_middles)}")
    print(f"    Mean:   {statistics.mean(n_middles):.1f}")
    print(f"    Median: {statistics.median(n_middles)}")
    print(f"    Std:    {statistics.stdev(n_middles):.1f}")

    # Distribution
    middle_dist = Counter(n_middles)
    print(f"\n  Distribution of MIDDLE counts:")
    for n in sorted(middle_dist.keys()):
        bar = '#' * (middle_dist[n])
        print(f"    {n:2d} MIDDLEs: {middle_dist[n]:2d} folios {bar}")

    # Total output capacity
    total_middles = sum(n_middles)
    unique_middles_global = set()
    for middles in folio_middles.values():
        unique_middles_global.update(middles)

    print("\n" + "-" * 70)
    print("OUTPUT CAPACITY ESTIMATE")
    print("-" * 70)

    print(f"\n  Total MIDDLE slots across all folios: {total_middles}")
    print(f"  Unique MIDDLEs globally: {len(unique_middles_global)}")
    print(f"  Average MIDDLEs per folio: {total_middles / len(folio_tokens):.1f}")

    # If each MIDDLE = one output variant
    print(f"\n  If each MIDDLE = one output variant:")
    print(f"    83 folios x {statistics.mean(n_middles):.1f} MIDDLEs/folio")
    print(f"    = ~{int(83 * statistics.mean(n_middles))} potential output pathways")

    # Compare to Puff
    print("\n" + "-" * 70)
    print("COMPARISON TO PUFF")
    print("-" * 70)

    print(f"\n  Puff: 83 chapters, each with ~1-3 preparations")
    print(f"  Voynich: 83 folios x {statistics.mean(n_middles):.1f} MIDDLEs")
    print(f"  Ratio: ~{statistics.mean(n_middles):.0f}x more output variants in Voynich")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    avg_middles = statistics.mean(n_middles)
    if avg_middles >= 10:
        verdict = "STRONG SUPPORT for multi-output model"
        interpretation = f"Each B folio handles ~{avg_middles:.0f} distinct variants"
    elif avg_middles >= 4:
        verdict = "PARTIAL SUPPORT for multi-output model"
        interpretation = f"Each B folio handles ~{avg_middles:.0f} variants (matches 4-5 expectation)"
    else:
        verdict = "WEAK SUPPORT"
        interpretation = f"Only ~{avg_middles:.0f} MIDDLEs per folio - limited output diversity"

    print(f"\n  {verdict}")
    print(f"  {interpretation}")

    # Does this explain 83:83?
    print(f"\n  Does this explain 83:83?")
    if avg_middles >= 4:
        print(f"    YES - If 83 materials with ~{avg_middles:.0f} products each,")
        print(f"    then 83 B folios make sense as material-specialized procedures")
    else:
        print(f"    NO - Insufficient output diversity to justify 83 folios")

    # Save results
    results = {
        'test': 'WITHIN_FOLIO_DIVERSITY',
        'question': 'How many distinct outputs can each B folio produce?',
        'data': {
            'n_folios': len(folio_tokens),
            'n_unique_middles_global': len(unique_middles_global)
        },
        'middle_stats': {
            'min': min(n_middles),
            'max': max(n_middles),
            'mean': statistics.mean(n_middles),
            'median': statistics.median(n_middles),
            'std': statistics.stdev(n_middles),
            'total_slots': total_middles
        },
        'distribution': dict(middle_dist),
        'output_capacity': {
            'avg_per_folio': statistics.mean(n_middles),
            'total_pathways': int(83 * statistics.mean(n_middles))
        },
        'verdict': verdict,
        'interpretation': interpretation,
        'folio_details': {
            folio: {'n_middles': v['n_distinct'], 'n_tokens': v['n_tokens']}
            for folio, v in sorted(folio_middle_counts.items(), key=lambda x: -x[1]['n_distinct'])[:20]
        }
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {OUTPUT_FILE}")

    return results


if __name__ == '__main__':
    main()
