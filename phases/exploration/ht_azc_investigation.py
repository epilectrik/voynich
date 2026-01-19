"""
HT-AZC Investigation: Third Anchoring Pressure?

Question: Does HT in AZC align with:
- Registry layout (like A)?
- Execution phase (like B)?
- Diagram geometry (something new)?

Using correct data source: interlinear_full_words.txt
"""

import csv
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
import numpy as np

DATA_PATH = Path(r"C:\git\voynich\data\transcriptions\interlinear_full_words.txt")

# HT definitions from C347/hierarchy
def is_ht_token(token):
    """Check if token is Human Track"""
    if not token:
        return False
    t = token.lower()
    # y-initial tokens (productive HT carrier)
    if t.startswith('y'):
        return True
    # Single-char atoms
    if len(t) == 1 and t in 'ydfr':
        return True
    return False

print("Loading data...")
records = []
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        transcriber = row.get('transcriber', '').strip().strip('"')
        if transcriber != 'H':
            continue
        word = row.get('word', '').strip().lower()
        if word and word != 'na' and '*' not in word:
            records.append({
                'token': word,
                'folio': row.get('folio', ''),
                'section': row.get('section', ''),
                'language': row.get('language', ''),
                'placement': row.get('placement', ''),
                'line': row.get('line_number', ''),
                'line_initial': row.get('line_initial', '') == '1',
                'line_final': row.get('line_final', '') == '1',
                'is_ht': is_ht_token(word)
            })

print(f"Loaded {len(records)} tokens")

# Identify AZC by section Z or diagram placements
DIAGRAM_PLACEMENTS = {'R', 'R1', 'R2', 'R3', 'C', 'S', 'S1', 'S2', 'Q', 'L', 'L1', 'L2', 'X', 'Y', 'T'}

records_a = [r for r in records if r['language'] == 'A' and r['placement'] not in DIAGRAM_PLACEMENTS]
records_b = [r for r in records if r['language'] == 'B' and r['placement'] not in DIAGRAM_PLACEMENTS]
records_azc = [r for r in records if r['section'] == 'Z' or r['placement'] in DIAGRAM_PLACEMENTS]

print(f"\nA: {len(records_a)} tokens")
print(f"B: {len(records_b)} tokens")
print(f"AZC: {len(records_azc)} tokens")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 1: HT DENSITY BY SYSTEM")
print("=" * 70)

def ht_density(tokens):
    ht = sum(1 for r in tokens if r['is_ht'])
    return ht / len(tokens) if tokens else 0

a_ht = ht_density(records_a)
b_ht = ht_density(records_b)
azc_ht = ht_density(records_azc)

print(f"\nHT density:")
print(f"  A: {100*a_ht:.2f}%")
print(f"  B: {100*b_ht:.2f}%")
print(f"  AZC: {100*azc_ht:.2f}%")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 2: HT POSITIONAL PATTERNS")
print("=" * 70)

def ht_positional(tokens, label):
    ht_tokens = [r for r in tokens if r['is_ht']]
    if not ht_tokens:
        print(f"\n{label}: No HT tokens")
        return {}

    initial = sum(1 for r in ht_tokens if r['line_initial'])
    final = sum(1 for r in ht_tokens if r['line_final'])
    total = len(ht_tokens)

    # Compare to baseline (all tokens)
    all_initial = sum(1 for r in tokens if r['line_initial'])
    all_final = sum(1 for r in tokens if r['line_final'])

    init_enrich = (initial/total) / (all_initial/len(tokens)) if all_initial else 0
    fin_enrich = (final/total) / (all_final/len(tokens)) if all_final else 0

    print(f"\n{label} ({total} HT tokens):")
    print(f"  Line-initial: {initial} ({100*initial/total:.1f}%) - enrichment: {init_enrich:.2f}x")
    print(f"  Line-final: {final} ({100*final/total:.1f}%) - enrichment: {fin_enrich:.2f}x")

    return {'initial': initial/total, 'final': final/total,
            'init_enrich': init_enrich, 'fin_enrich': fin_enrich}

a_pos = ht_positional(records_a, "Currier A")
b_pos = ht_positional(records_b, "Currier B")
azc_pos = ht_positional(records_azc, "AZC")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 3: HT BY PLACEMENT CODE (AZC-specific)")
print("=" * 70)

azc_by_placement = defaultdict(list)
for r in records_azc:
    azc_by_placement[r['placement']].append(r)

print("\nHT density by placement code:")
placement_ht = {}
for placement in sorted(azc_by_placement.keys()):
    tokens = azc_by_placement[placement]
    if len(tokens) >= 20:
        ht = ht_density(tokens)
        placement_ht[placement] = ht
        print(f"  {placement}: {100*ht:.1f}% HT ({len(tokens)} tokens)")

# Is there significant variation by placement?
if len(placement_ht) >= 3:
    values = list(placement_ht.values())
    print(f"\n  Range: {100*min(values):.1f}% - {100*max(values):.1f}%")
    print(f"  Std dev: {100*np.std(values):.2f}%")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 4: HT VOCABULARY IN AZC")
print("=" * 70)

azc_ht_tokens = [r['token'] for r in records_azc if r['is_ht']]
a_ht_tokens = [r['token'] for r in records_a if r['is_ht']]
b_ht_tokens = [r['token'] for r in records_b if r['is_ht']]

azc_ht_types = set(azc_ht_tokens)
a_ht_types = set(a_ht_tokens)
b_ht_types = set(b_ht_tokens)

print(f"\nHT type counts:")
print(f"  A: {len(a_ht_types)} types")
print(f"  B: {len(b_ht_types)} types")
print(f"  AZC: {len(azc_ht_types)} types")

print(f"\nAZC HT overlap:")
print(f"  With A: {len(azc_ht_types & a_ht_types)} ({100*len(azc_ht_types & a_ht_types)/len(azc_ht_types):.1f}%)")
print(f"  With B: {len(azc_ht_types & b_ht_types)} ({100*len(azc_ht_types & b_ht_types)/len(azc_ht_types):.1f}%)")
print(f"  AZC-only: {len(azc_ht_types - a_ht_types - b_ht_types)}")

print("\nTop AZC HT tokens:")
for t, c in Counter(azc_ht_tokens).most_common(15):
    in_a = t in a_ht_types
    in_b = t in b_ht_types
    source = "A+B" if (in_a and in_b) else ("A" if in_a else ("B" if in_b else "AZC-only"))
    print(f"  {t}: {c} [{source}]")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 5: HT × PLACEMENT CORRELATION")
print("=" * 70)

# Does HT presence correlate with specific placements?
placement_codes = list(set(r['placement'] for r in records_azc if r['placement']))
if len(placement_codes) >= 2:
    # Chi-square test
    contingency = defaultdict(lambda: {'ht': 0, 'non_ht': 0})
    for r in records_azc:
        p = r['placement'] if r['placement'] else 'NONE'
        if r['is_ht']:
            contingency[p]['ht'] += 1
        else:
            contingency[p]['non_ht'] += 1

    # Filter to placements with enough data
    valid = {p: v for p, v in contingency.items() if v['ht'] + v['non_ht'] >= 20}

    if len(valid) >= 2:
        table = [[v['ht'], v['non_ht']] for v in valid.values()]
        chi2, p, dof, expected = stats.chi2_contingency(table)
        n = sum(sum(row) for row in table)
        cramers_v = np.sqrt(chi2 / (n * (min(len(table), 2) - 1)))

        print(f"\nHT × Placement association:")
        print(f"  Chi-square: {chi2:.1f}")
        print(f"  p-value: {p:.2e}")
        print(f"  Cramer's V: {cramers_v:.3f}")
        print(f"  Interpretation: {'STRONG' if cramers_v > 0.3 else 'MODERATE' if cramers_v > 0.15 else 'WEAK'}")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 6: HT MORPHOLOGY COMPARISON")
print("=" * 70)

def analyze_ht_morphology(tokens, label):
    ht = [r['token'] for r in tokens if r['is_ht']]
    if not ht:
        return {}

    # Prefix analysis (first 2 chars)
    prefixes = Counter(t[:2] if len(t) >= 2 else t for t in ht)

    # Length distribution
    lengths = Counter(len(t) for t in ht)
    mean_len = sum(l * c for l, c in lengths.items()) / sum(lengths.values())

    # Simplex vs complex
    simplex = sum(1 for t in ht if len(t) <= 2)

    print(f"\n{label}:")
    print(f"  Mean length: {mean_len:.2f}")
    print(f"  Simplex (len<=2): {100*simplex/len(ht):.1f}%")
    print(f"  Top prefixes: {dict(prefixes.most_common(5))}")

    return {'mean_len': mean_len, 'simplex_rate': simplex/len(ht), 'prefixes': prefixes}

a_morph = analyze_ht_morphology(records_a, "Currier A")
b_morph = analyze_ht_morphology(records_b, "Currier B")
azc_morph = analyze_ht_morphology(records_azc, "AZC")

# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY: WHICH PATTERN DOES AZC FOLLOW?")
print("=" * 70)

print("\n| Metric | A | B | AZC | AZC follows |")
print("|--------|---|---|-----|-------------|")

# Density
azc_density_like = "A" if abs(azc_ht - a_ht) < abs(azc_ht - b_ht) else "B"
print(f"| HT density | {100*a_ht:.1f}% | {100*b_ht:.1f}% | {100*azc_ht:.1f}% | {azc_density_like} |")

# Line-initial
if a_pos and b_pos and azc_pos:
    azc_init_like = "A" if abs(azc_pos['init_enrich'] - a_pos['init_enrich']) < abs(azc_pos['init_enrich'] - b_pos['init_enrich']) else "B"
    print(f"| Line-initial enrich | {a_pos['init_enrich']:.2f}x | {b_pos['init_enrich']:.2f}x | {azc_pos['init_enrich']:.2f}x | {azc_init_like} |")

# Morphology
if a_morph and b_morph and azc_morph:
    azc_len_like = "A" if abs(azc_morph['mean_len'] - a_morph['mean_len']) < abs(azc_morph['mean_len'] - b_morph['mean_len']) else "B"
    print(f"| HT mean length | {a_morph['mean_len']:.2f} | {b_morph['mean_len']:.2f} | {azc_morph['mean_len']:.2f} | {azc_len_like} |")

    azc_simp_like = "A" if abs(azc_morph['simplex_rate'] - a_morph['simplex_rate']) < abs(azc_morph['simplex_rate'] - b_morph['simplex_rate']) else "B"
    print(f"| Simplex rate | {100*a_morph['simplex_rate']:.1f}% | {100*b_morph['simplex_rate']:.1f}% | {100*azc_morph['simplex_rate']:.1f}% | {azc_simp_like} |")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)
