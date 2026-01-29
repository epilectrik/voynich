"""
Test: Does RI function as a "header" that compresses/predicts B folio vocabulary?

Hypothesis: PP atoms contained in A folio's RI should predict which B vocabulary
that A folio makes legal.

If RI is a manifest, then:
  PP_atoms_in_RI(A_folio) ≈ B_vocabulary_made_legal_by(A_folio)
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

print("="*70)
print("RI HEADER HYPOTHESIS TEST")
print("="*70)

# ============================================================
# COLLECT ALL MIDDLES BY SYSTEM AND FOLIO
# ============================================================

# Get all A MIDDLEs by folio
a_middles_by_folio = defaultdict(set)
for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        a_middles_by_folio[token.folio].add(m.middle)

# Get all B MIDDLEs by folio
b_middles_by_folio = defaultdict(set)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_middles_by_folio[token.folio].add(m.middle)

# Get all A and B MIDDLEs
all_a_middles = set()
for mids in a_middles_by_folio.values():
    all_a_middles.update(mids)

all_b_middles = set()
for mids in b_middles_by_folio.values():
    all_b_middles.update(mids)

# PP = shared between A and B
pp_middles = all_a_middles & all_b_middles

# RI = A-exclusive
ri_middles = all_a_middles - all_b_middles

print(f"\nInventory:")
print(f"  A folios: {len(a_middles_by_folio)}")
print(f"  B folios: {len(b_middles_by_folio)}")
print(f"  PP (shared): {len(pp_middles)}")
print(f"  RI (A-exclusive): {len(ri_middles)}")

# ============================================================
# FOR EACH A FOLIO: EXTRACT RI AND PP ATOMS IN RI
# ============================================================
print("\n" + "="*70)
print("A FOLIO RI STRUCTURE")
print("="*70)

a_folio_ri = {}  # A folio -> set of RI MIDDLEs in that folio
a_folio_pp_in_ri = {}  # A folio -> set of PP atoms contained in that folio's RI

for folio, middles in a_middles_by_folio.items():
    # RI in this folio
    folio_ri = middles & ri_middles
    a_folio_ri[folio] = folio_ri

    # PP atoms contained in this folio's RI
    pp_atoms = set()
    for ri in folio_ri:
        for pp in pp_middles:
            if pp in ri and pp != ri:
                pp_atoms.add(pp)
    a_folio_pp_in_ri[folio] = pp_atoms

# Sample output
sample_folios = list(a_middles_by_folio.keys())[:5]
for folio in sample_folios:
    ri_count = len(a_folio_ri[folio])
    pp_atom_count = len(a_folio_pp_in_ri[folio])
    print(f"\n{folio}:")
    print(f"  RI MIDDLEs: {ri_count}")
    print(f"  PP atoms in RI: {pp_atom_count}")
    if a_folio_pp_in_ri[folio]:
        print(f"    Sample: {list(a_folio_pp_in_ri[folio])[:10]}")

# ============================================================
# FOR EACH B FOLIO: GET EXCLUSIVE VOCABULARY
# ============================================================
print("\n" + "="*70)
print("B FOLIO EXCLUSIVE VOCABULARY")
print("="*70)

# B vocabulary shared with any A = PP subset that appears in that B folio
b_folio_pp = {}  # B folio -> PP MIDDLEs used in that folio

for folio, middles in b_middles_by_folio.items():
    b_folio_pp[folio] = middles & pp_middles

# Sample output
sample_b = list(b_middles_by_folio.keys())[:5]
for folio in sample_b:
    pp_count = len(b_folio_pp[folio])
    total = len(b_middles_by_folio[folio])
    print(f"\n{folio}:")
    print(f"  Total MIDDLEs: {total}")
    print(f"  PP MIDDLEs: {pp_count} ({100*pp_count/total:.1f}%)")

# ============================================================
# TEST: DO PP ATOMS IN A FOLIO'S RI PREDICT B VOCABULARY?
# ============================================================
print("\n" + "="*70)
print("COVERAGE TEST: PP atoms in RI vs B folio vocabulary")
print("="*70)

# For each A folio, compare:
#   - PP atoms contained in that A folio's RI
#   - PP vocabulary actually used in each B folio

# Build coverage matrix: how much of B folio's PP vocabulary is "predicted" by A folio's RI PP atoms?
coverage_data = []

for a_folio, pp_atoms in a_folio_pp_in_ri.items():
    if not pp_atoms:
        continue
    for b_folio, b_pp in b_folio_pp.items():
        if not b_pp:
            continue
        # How many of B's PP are in A's RI PP atoms?
        overlap = pp_atoms & b_pp
        coverage = len(overlap) / len(b_pp) if b_pp else 0
        coverage_data.append({
            'a_folio': a_folio,
            'b_folio': b_folio,
            'a_pp_count': len(pp_atoms),
            'b_pp_count': len(b_pp),
            'overlap': len(overlap),
            'coverage': coverage
        })

if coverage_data:
    coverages = [d['coverage'] for d in coverage_data]
    print(f"\nOverall RI->B prediction coverage:")
    print(f"  Mean: {np.mean(coverages):.3f}")
    print(f"  Median: {np.median(coverages):.3f}")
    print(f"  Min: {np.min(coverages):.3f}")
    print(f"  Max: {np.max(coverages):.3f}")

# ============================================================
# FOLIO-LEVEL CORRELATION
# ============================================================
print("\n" + "="*70)
print("A FOLIO RI SIZE vs B COVERAGE")
print("="*70)

# Does having more PP atoms in RI correlate with higher B coverage?
a_folio_mean_coverage = {}
for a_folio in a_folio_pp_in_ri:
    folio_coverages = [d['coverage'] for d in coverage_data if d['a_folio'] == a_folio]
    if folio_coverages:
        a_folio_mean_coverage[a_folio] = np.mean(folio_coverages)

if a_folio_mean_coverage:
    ri_sizes = [len(a_folio_pp_in_ri[f]) for f in a_folio_mean_coverage]
    mean_covs = [a_folio_mean_coverage[f] for f in a_folio_mean_coverage]

    from scipy import stats
    rho, pval = stats.spearmanr(ri_sizes, mean_covs)

    print(f"\nCorrelation: RI PP-atom count vs mean B coverage:")
    print(f"  Spearman rho: {rho:.3f}")
    print(f"  p-value: {pval:.4f}")

# ============================================================
# SELF-COVERAGE: Does A folio's RI predict SAME B folio?
# ============================================================
print("\n" + "="*70)
print("SELF-COVERAGE: A folio RI -> corresponding B sections?")
print("="*70)

# Note: A and B folios don't have 1:1 mapping, but we can look at sections
# that might correspond

# For now, just compare aggregate statistics
print("\nNote: A-B folio mapping is not 1:1. Testing aggregate patterns.")

# ============================================================
# ALTERNATIVE: Does RI PP content match specific B folios better?
# ============================================================
print("\n" + "="*70)
print("SPECIFICITY: Do A folios have 'best match' B folios?")
print("="*70)

# For each A folio, find the B folio with highest coverage
a_best_match = {}
for a_folio in a_folio_pp_in_ri:
    folio_data = [d for d in coverage_data if d['a_folio'] == a_folio]
    if folio_data:
        best = max(folio_data, key=lambda x: x['coverage'])
        a_best_match[a_folio] = {
            'b_folio': best['b_folio'],
            'coverage': best['coverage'],
            'mean_coverage': np.mean([d['coverage'] for d in folio_data])
        }

# Compute lift: best match vs mean
lifts = []
for a_folio, match in a_best_match.items():
    if match['mean_coverage'] > 0:
        lift = match['coverage'] / match['mean_coverage']
        lifts.append(lift)

if lifts:
    print(f"\nBest-match lift (vs mean):")
    print(f"  Mean lift: {np.mean(lifts):.2f}x")
    print(f"  Median lift: {np.median(lifts):.2f}x")
    print(f"  Max lift: {np.max(lifts):.2f}x")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

if coverage_data:
    mean_cov = np.mean(coverages)
    if mean_cov > 0.5:
        findings.append(f"HIGH_PREDICTION: RI PP atoms predict {mean_cov:.1%} of B PP vocabulary")
    elif mean_cov > 0.3:
        findings.append(f"MODERATE_PREDICTION: RI PP atoms predict {mean_cov:.1%} of B PP vocabulary")
    else:
        findings.append(f"LOW_PREDICTION: RI PP atoms predict only {mean_cov:.1%} of B PP vocabulary")

if 'rho' in dir() and pval < 0.05:
    findings.append(f"RI_SIZE_CORRELATES: Larger RI PP inventory -> higher B coverage (rho={rho:.3f})")

if lifts:
    mean_lift = np.mean(lifts)
    if mean_lift > 1.5:
        findings.append(f"SPECIFICITY_CONFIRMED: Best-match B folio has {mean_lift:.2f}x coverage vs average")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

print(f"""

RI HEADER HYPOTHESIS:

If RI functions as a "manifest" that compresses B vocabulary, we expect:
1. PP atoms in RI should predict B PP vocabulary (high coverage)
2. Larger RI -> higher B coverage (positive correlation)
3. Specific A-B pairings should have better matches (specificity)

Results:
  - Mean coverage: {np.mean(coverages):.1%} of B vocabulary predicted by RI PP atoms
  - Correlation: rho={rho:.3f} (p={pval:.4f})
  - Best-match lift: {np.mean(lifts):.2f}x vs average

{'SUPPORTS HEADER HYPOTHESIS' if mean_cov > 0.5 and rho > 0.3 else
 'PARTIAL SUPPORT' if mean_cov > 0.3 or rho > 0.3 else
 'DOES NOT SUPPORT HEADER HYPOTHESIS'}
""")
