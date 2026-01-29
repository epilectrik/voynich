"""
T1: Survey all Zodiac folio ring compositions.

Question: Do other Zodiac folios have single-char dominated rings like f57v R2?
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Load data
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

# Zodiac family folios (per C430): all 12 Z + f57v
# Z folios are section='Z' in the transcript
zodiac_folios = sorted(df[df['section'] == 'Z']['folio'].unique().tolist())
zodiac_folios.append('f57v')  # Add f57v (section C but Zodiac family by grammar)
zodiac_folios = sorted(set(zodiac_folios))

print("="*70)
print("T1: ZODIAC FOLIO RING COMPOSITION SURVEY")
print("="*70)
print(f"\nZodiac family folios ({len(zodiac_folios)}): {zodiac_folios}")

# Analyze each folio
results = {}
for folio in zodiac_folios:
    fdf = df[df['folio'] == folio]
    placements = fdf['placement'].unique()

    # Get R-series placements
    r_placements = [p for p in placements if str(p).startswith('R')]

    if not r_placements:
        continue

    results[folio] = {'rings': {}}

    print(f"\n{'='*50}")
    print(f"FOLIO: {folio}")
    print(f"{'='*50}")
    print(f"R-placements: {sorted(r_placements)}")

    for ring in sorted(r_placements):
        subset = fdf[fdf['placement'] == ring]
        words = [str(w) for w in subset['word'].tolist() if str(w) != 'nan' and str(w) != '*']

        if not words:
            continue

        single_chars = [w for w in words if len(w) == 1]
        multi_chars = [w for w in words if len(w) > 1]
        single_pct = 100 * len(single_chars) / len(words) if words else 0

        results[folio]['rings'][ring] = {
            'total': len(words),
            'single_char': len(single_chars),
            'multi_char': len(multi_chars),
            'single_pct': round(single_pct, 1)
        }

        # Flag anomalous rings (>70% single char)
        flag = " *** ANOMALOUS" if single_pct > 70 else ""
        print(f"  {ring}: {len(words)} tokens, {single_pct:.0f}% single-char{flag}")

        if single_pct > 70:
            # Show the sequence
            seq = subset.sort_values('line_number')['word'].tolist()
            clean = [str(w) for w in seq if str(w) != '*' and str(w) != 'nan']
            print(f"      Sequence: {' '.join(clean[:30])}{'...' if len(clean) > 30 else ''}")

# Summary
print("\n" + "="*70)
print("SUMMARY: SINGLE-CHAR DOMINATED RINGS (>70%)")
print("="*70)

anomalous = []
for folio, data in results.items():
    for ring, stats in data['rings'].items():
        if stats['single_pct'] > 70:
            anomalous.append((folio, ring, stats['single_pct'], stats['total']))

if anomalous:
    print(f"\nFound {len(anomalous)} anomalous rings:")
    for folio, ring, pct, n in sorted(anomalous, key=lambda x: -x[2]):
        print(f"  {folio} {ring}: {pct:.0f}% single-char (n={n})")
else:
    print("\nNo anomalous rings found outside f57v.")

# Save results
output = {
    'zodiac_folios': zodiac_folios,
    'ring_data': results,
    'anomalous_rings': [{'folio': f, 'ring': r, 'single_pct': p, 'n': n}
                        for f, r, p, n in anomalous],
    'verdict': 'F57V_UNIQUE' if len([a for a in anomalous if a[0] == 'f57v']) == len(anomalous) else 'PATTERN_SHARED'
}

output_path = PROJECT_ROOT / 'phases' / 'F57V_COORDINATE_RING' / 'results' / 't1_zodiac_ring_survey.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to: {output_path}")
