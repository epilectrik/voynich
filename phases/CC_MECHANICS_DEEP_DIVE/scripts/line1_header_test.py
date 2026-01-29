"""
Test: Do LINE-1 HT compound MIDDLEs specifically encode THAT folio's vocabulary?

Per C766 and C747-C750:
- Line-1 has 50.2% HT (vs 29.8% rest)
- Line-1 HT is 95.9% unique types
- UN/HT is derived by compounding base MIDDLEs
- UN has 64.5% folio-unique rate

Hypothesis: PP atoms in line-1 HT tokens should predict the vocabulary
used on lines 2+ of the SAME folio (not other folios).
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

print("="*70)
print("LINE-1 HT HEADER TEST")
print("="*70)

# ============================================================
# COLLECT DATA BY FOLIO AND LINE
# ============================================================

# Get all A MIDDLEs (to identify PP)
all_a_middles = set()
for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        all_a_middles.add(m.middle)

# Collect B tokens by folio and line
b_data_by_folio = defaultdict(lambda: {'line1': [], 'rest': []})

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    folio = token.folio
    line = str(token.line)  # Line is a string!
    is_ht = w not in classified_tokens
    m = morph.extract(w)

    entry = {
        'word': w,
        'middle': m.middle,
        'is_ht': is_ht
    }

    if line == '1':  # String comparison
        b_data_by_folio[folio]['line1'].append(entry)
    else:
        b_data_by_folio[folio]['rest'].append(entry)

# Get all B MIDDLEs
all_b_middles = set()
for folio, data in b_data_by_folio.items():
    for entry in data['line1'] + data['rest']:
        if entry['middle']:
            all_b_middles.add(entry['middle'])

# PP = shared between A and B
pp_middles = all_a_middles & all_b_middles

print(f"\nInventory:")
print(f"  B folios: {len(b_data_by_folio)}")
print(f"  PP (shared A-B): {len(pp_middles)}")

# ============================================================
# ANALYZE LINE-1 HT TOKENS
# ============================================================
print("\n" + "="*70)
print("LINE-1 HT TOKENS")
print("="*70)

folio_line1_ht = {}  # folio -> list of HT MIDDLEs on line 1
folio_line1_pp_atoms = {}  # folio -> PP atoms contained in line-1 HT MIDDLEs

for folio, data in b_data_by_folio.items():
    line1_ht_middles = [e['middle'] for e in data['line1'] if e['is_ht'] and e['middle']]
    folio_line1_ht[folio] = line1_ht_middles

    # Extract PP atoms from these HT MIDDLEs
    pp_atoms = set()
    for mid in line1_ht_middles:
        for pp in pp_middles:
            if pp in mid and pp != mid:
                pp_atoms.add(pp)
    folio_line1_pp_atoms[folio] = pp_atoms

# Sample
sample_folios = list(b_data_by_folio.keys())[:5]
for folio in sample_folios:
    n_ht = len(folio_line1_ht[folio])
    n_pp = len(folio_line1_pp_atoms[folio])
    print(f"\n{folio}: {n_ht} line-1 HT MIDDLEs, {n_pp} PP atoms embedded")
    if folio_line1_ht[folio]:
        print(f"  HT MIDDLEs: {folio_line1_ht[folio][:5]}")
    if folio_line1_pp_atoms[folio]:
        print(f"  PP atoms: {list(folio_line1_pp_atoms[folio])[:10]}")

# ============================================================
# ANALYZE REST-OF-FOLIO VOCABULARY
# ============================================================
print("\n" + "="*70)
print("REST-OF-FOLIO (LINES 2+) PP VOCABULARY")
print("="*70)

folio_rest_pp = {}  # folio -> PP MIDDLEs on lines 2+

for folio, data in b_data_by_folio.items():
    rest_middles = set(e['middle'] for e in data['rest'] if e['middle'])
    folio_rest_pp[folio] = rest_middles & pp_middles

# ============================================================
# KEY TEST: Do line-1 PP atoms predict SAME-folio rest vocabulary?
# ============================================================
print("\n" + "="*70)
print("SAME-FOLIO PREDICTION TEST")
print("="*70)

# For each folio: what fraction of line-1 PP atoms appear in that folio's lines 2+?
same_folio_results = []

for folio in b_data_by_folio:
    line1_pp = folio_line1_pp_atoms[folio]
    rest_pp = folio_rest_pp[folio]

    if not line1_pp:
        continue

    # Same-folio match
    same_match = line1_pp & rest_pp
    same_rate = len(same_match) / len(line1_pp)

    # Other-folio match (average)
    other_rates = []
    for other_folio in b_data_by_folio:
        if other_folio != folio:
            other_pp = folio_rest_pp[other_folio]
            other_match = line1_pp & other_pp
            other_rates.append(len(other_match) / len(line1_pp))

    mean_other = np.mean(other_rates) if other_rates else 0
    lift = same_rate / mean_other if mean_other > 0 else float('inf')

    same_folio_results.append({
        'folio': folio,
        'n_line1_pp': len(line1_pp),
        'same_rate': same_rate,
        'other_rate': mean_other,
        'lift': lift
    })

if same_folio_results:
    same_rates = [r['same_rate'] for r in same_folio_results]
    other_rates = [r['other_rate'] for r in same_folio_results]
    lifts = [r['lift'] for r in same_folio_results if r['lift'] != float('inf')]

    print(f"\nLine-1 HT PP atoms match SAME folio's rest:")
    print(f"  Mean: {np.mean(same_rates):.3f} ({100*np.mean(same_rates):.1f}%)")

    print(f"\nLine-1 HT PP atoms match OTHER folios' rest (baseline):")
    print(f"  Mean: {np.mean(other_rates):.3f} ({100*np.mean(other_rates):.1f}%)")

    print(f"\nLift (same vs other):")
    print(f"  Mean: {np.mean(lifts):.2f}x")
    print(f"  Median: {np.median(lifts):.2f}x")

    # Statistical test
    from scipy import stats
    stat, pval = stats.wilcoxon([r['same_rate'] for r in same_folio_results],
                                 [r['other_rate'] for r in same_folio_results])
    print(f"\nWilcoxon test (same > other): p = {pval:.6f}")

# ============================================================
# REVERSE TEST: Does folio's rest PP predict line-1 HT content?
# ============================================================
print("\n" + "="*70)
print("REVERSE TEST: Does folio vocabulary predict line-1 HT?")
print("="*70)

# For each folio: what fraction of rest PP atoms appear in line-1 HT?
reverse_results = []

for folio in b_data_by_folio:
    line1_pp = folio_line1_pp_atoms[folio]
    rest_pp = folio_rest_pp[folio]

    if not rest_pp or not line1_pp:
        continue

    # What fraction of rest PP is "covered" by line-1?
    covered = rest_pp & line1_pp
    coverage = len(covered) / len(rest_pp)

    reverse_results.append({
        'folio': folio,
        'n_rest_pp': len(rest_pp),
        'n_line1_pp': len(line1_pp),
        'coverage': coverage
    })

if reverse_results:
    coverages = [r['coverage'] for r in reverse_results]
    print(f"\nFraction of folio vocabulary 'covered' by line-1 HT:")
    print(f"  Mean: {np.mean(coverages):.3f} ({100*np.mean(coverages):.1f}%)")
    print(f"  Median: {np.median(coverages):.3f}")
    print(f"  Max: {np.max(coverages):.3f}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

if same_folio_results and lifts:
    mean_lift = np.mean(lifts)
    if mean_lift > 1.2 and pval < 0.05:
        findings.append(f"SAME_FOLIO_ENRICHED: Line-1 HT PP atoms {mean_lift:.2f}x more likely in same folio (p={pval:.4f})")
    elif mean_lift > 1.1:
        findings.append(f"WEAK_ENRICHMENT: Line-1 HT PP atoms {mean_lift:.2f}x in same folio")
    else:
        findings.append(f"NO_ENRICHMENT: Line-1 HT PP atoms only {mean_lift:.2f}x in same folio")

if reverse_results:
    mean_cov = np.mean(coverages)
    findings.append(f"COVERAGE: Line-1 HT 'covers' {100*mean_cov:.1f}% of folio vocabulary")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

if same_folio_results and reverse_results and lifts:
    mean_lift = np.mean(lifts)
    mean_cov = np.mean(coverages)
    print(f"""

LINE-1 HEADER HYPOTHESIS:

If line-1 HT tokens are "headers" that compress folio vocabulary:
1. PP atoms embedded in line-1 HT should be enriched for same-folio vocabulary
2. Line-1 HT should "cover" a significant portion of the folio's PP usage

Results:
  - Same-folio match: {100*np.mean(same_rates):.1f}% vs {100*np.mean(other_rates):.1f}% baseline
  - Lift: {mean_lift:.2f}x (p={pval:.4f})
  - Coverage of folio vocabulary: {100*mean_cov:.1f}%

{'SUPPORTS HEADER HYPOTHESIS' if mean_lift > 1.2 and pval < 0.05 else
 'PARTIAL SUPPORT' if mean_lift > 1.1 else
 'DOES NOT SUPPORT'}
""")
