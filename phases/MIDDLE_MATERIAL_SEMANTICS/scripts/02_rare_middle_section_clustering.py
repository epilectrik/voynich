"""
02_rare_middle_section_clustering.py - Cross-Folio Rare MIDDLE Section Clustering

Question: Do rare MIDDLEs (appearing in 2-15 folios) cluster by manuscript section?

Method:
1. Extract MIDDLEs from all Currier B, H-track tokens
2. Build MIDDLE-to-folios mapping
3. Select RARE middles: those appearing in 2-15 folios
4. For each rare MIDDLE, compute section concentration vs expected
5. Chi-square test per MIDDLE, Bonferroni correction
6. Compare rare vs common MIDDLE section concentration (Mann-Whitney U)
"""

import json
import sys
from collections import defaultdict, Counter

import numpy as np
from scipy import stats

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# ============================================================
# LOAD DATA
# ============================================================
tx = Transcript()
morph = Morphology()

# Collect all Currier B tokens (H-track, no labels, no uncertain, no empty)
b_tokens = list(tx.currier_b())
print(f"Total Currier B tokens: {len(b_tokens)}")

# ============================================================
# EXTRACT MIDDLEs AND BUILD MAPPINGS
# ============================================================

# Pre-compute morphology for all tokens at once
token_middles = []
for t in b_tokens:
    m = morph.extract(t.word)
    if m and m.middle and m.middle != '_EMPTY_':
        token_middles.append((m.middle, t.folio, t.section))

print(f"Tokens with valid MIDDLE: {len(token_middles)}")

# Build MIDDLE -> set of folios, and MIDDLE -> list of sections
middle_to_folios = defaultdict(set)
middle_to_sections = defaultdict(list)

for mid, folio, section in token_middles:
    middle_to_folios[mid].add(folio)
    middle_to_sections[mid].append(section)

print(f"Unique MIDDLEs: {len(middle_to_folios)}")

# ============================================================
# COMPUTE SECTION SIZES (for expected proportions)
# ============================================================

# Count folios per section (each folio counted once)
folio_to_section = {}
for t in b_tokens:
    if t.folio not in folio_to_section:
        folio_to_section[t.folio] = t.section

section_folio_counts = Counter(folio_to_section.values())
total_folios = len(folio_to_section)
sections_sorted = sorted(section_folio_counts.keys())

print(f"\nSection sizes (folios):")
for sec in sections_sorted:
    print(f"  {sec}: {section_folio_counts[sec]} folios ({100*section_folio_counts[sec]/total_folios:.1f}%)")

# Expected section proportions (by folio count)
section_proportions = {sec: section_folio_counts[sec] / total_folios for sec in sections_sorted}

# ============================================================
# CLASSIFY MIDDLEs BY FOLIO SPREAD
# ============================================================

RARE_MIN = 2
RARE_MAX = 15
COMMON_MIN = 16  # > RARE_MAX

rare_middles = {mid: folios for mid, folios in middle_to_folios.items()
                if RARE_MIN <= len(folios) <= RARE_MAX}
common_middles = {mid: folios for mid, folios in middle_to_folios.items()
                  if len(folios) >= COMMON_MIN}

print(f"\nRare MIDDLEs (2-15 folios): {len(rare_middles)}")
print(f"Common MIDDLEs (>= 16 folios): {len(common_middles)}")

# ============================================================
# COMPUTE SECTION CONCENTRATION
# ============================================================

def section_concentration(folio_set, folio_to_section_map):
    """
    Compute max(section_count / total_folio_count) for a set of folios.
    This measures how concentrated the folios are in a single section.
    """
    section_counts = Counter()
    for f in folio_set:
        sec = folio_to_section_map.get(f)
        if sec:
            section_counts[sec] += 1
    n = sum(section_counts.values())
    if n == 0:
        return 0.0
    return max(section_counts.values()) / n


def expected_concentration(n_folios, section_props):
    """
    Compute expected max section concentration under random assignment.
    For n folios drawn randomly with section proportions, the expected
    max proportion is computed analytically for the dominant section.

    Approximation: for random multinomial draws, the expected max is
    biased toward the largest section proportion but diluted by n.
    We use simulation for accuracy.
    """
    if n_folios <= 0:
        return 0.0
    # Monte Carlo estimate
    rng = np.random.default_rng(42)
    secs = list(section_props.keys())
    probs = np.array([section_props[s] for s in secs])

    n_sims = 5000
    max_props = []
    for _ in range(n_sims):
        draws = rng.choice(len(secs), size=n_folios, p=probs)
        counts = np.bincount(draws, minlength=len(secs))
        max_props.append(counts.max() / n_folios)
    return np.mean(max_props)


# Compute section concentration for each rare MIDDLE
rare_concentrations = {}
for mid, folios in rare_middles.items():
    conc = section_concentration(folios, folio_to_section)
    rare_concentrations[mid] = conc

# Compute section concentration for each common MIDDLE
common_concentrations = {}
for mid, folios in common_middles.items():
    conc = section_concentration(folios, folio_to_section)
    common_concentrations[mid] = conc

mean_rare = np.mean(list(rare_concentrations.values()))
mean_common = np.mean(list(common_concentrations.values())) if common_concentrations else 0.0

print(f"\nMean section concentration:")
print(f"  Rare MIDDLEs:   {mean_rare:.4f}")
print(f"  Common MIDDLEs: {mean_common:.4f}")

# ============================================================
# MANN-WHITNEY U: rare vs common concentration
# ============================================================

rare_vals = list(rare_concentrations.values())
common_vals = list(common_concentrations.values())

if len(common_vals) >= 2 and len(rare_vals) >= 2:
    mw_u, mw_p = stats.mannwhitneyu(rare_vals, common_vals, alternative='greater')
    print(f"\nMann-Whitney U test (rare > common):")
    print(f"  U = {mw_u:.1f}, p = {mw_p:.6f}")
else:
    mw_u, mw_p = float('nan'), float('nan')
    print("\nInsufficient data for Mann-Whitney U test")

# ============================================================
# CHI-SQUARE TESTS PER RARE MIDDLE
# ============================================================

# For each rare MIDDLE with >= 4 folios, test whether its section distribution
# deviates from the expected section proportions.

MIN_FOLIOS_FOR_TEST = 4
testable = {mid: folios for mid, folios in rare_middles.items()
            if len(folios) >= MIN_FOLIOS_FOR_TEST}

print(f"\nTestable rare MIDDLEs (>= {MIN_FOLIOS_FOR_TEST} folios): {len(testable)}")

chi_results = []
for mid, folios in testable.items():
    # Observed section counts for this MIDDLE's folios
    section_counts = Counter()
    for f in folios:
        sec = folio_to_section.get(f)
        if sec:
            section_counts[sec] += 1

    n = sum(section_counts.values())
    observed = np.array([section_counts.get(sec, 0) for sec in sections_sorted])
    expected = np.array([section_proportions[sec] * n for sec in sections_sorted])

    # Merge small expected categories (< 1) to avoid chi-square issues
    # Combine categories with expected < 1 into "other"
    mask = expected >= 1.0
    if mask.sum() < 2:
        # Not enough categories for chi-square
        continue

    if not mask.all():
        obs_merged = np.append(observed[mask], observed[~mask].sum())
        exp_merged = np.append(expected[mask], expected[~mask].sum())
    else:
        obs_merged = observed
        exp_merged = expected

    if len(obs_merged) < 2 or exp_merged.min() < 0.5:
        continue

    chi2, p_val = stats.chisquare(obs_merged, exp_merged)
    conc = rare_concentrations[mid]

    chi_results.append({
        'middle': mid,
        'n_folios': n,
        'concentration': conc,
        'chi2': chi2,
        'p_value': p_val,
        'section_counts': {sec: section_counts.get(sec, 0) for sec in sections_sorted},
        'dominant_section': max(section_counts, key=section_counts.get)
    })

print(f"Chi-square tests computed: {len(chi_results)}")

# Bonferroni correction
n_tests = len(chi_results)
alpha = 0.05
bonferroni_threshold = alpha / n_tests if n_tests > 0 else alpha

n_significant = sum(1 for r in chi_results if r['p_value'] < bonferroni_threshold)
pct_concentrated = 100 * n_significant / n_tests if n_tests > 0 else 0.0

print(f"\nBonferroni threshold: {bonferroni_threshold:.6f}")
print(f"Significant (Bonferroni): {n_significant}/{n_tests} ({pct_concentrated:.1f}%)")

# ============================================================
# TOP CONCENTRATED MIDDLES
# ============================================================

chi_results.sort(key=lambda x: x['p_value'])
top_concentrated = []
for r in chi_results[:20]:
    top_concentrated.append({
        'middle': r['middle'],
        'n_folios': r['n_folios'],
        'concentration': round(r['concentration'], 4),
        'dominant_section': r['dominant_section'],
        'chi2': round(r['chi2'], 4),
        'p_value': r['p_value'],
        'section_counts': r['section_counts']
    })

print("\nTop 20 most section-concentrated rare MIDDLEs:")
print(f"{'MIDDLE':<16} {'N_fol':>6} {'Conc':>8} {'Dom':>5} {'chi2':>10} {'p_value':>12}")
print("-" * 65)
for r in top_concentrated:
    print(f"{r['middle']:<16} {r['n_folios']:>6} {r['concentration']:>8.3f} "
          f"{r['dominant_section']:>5} {r['chi2']:>10.2f} {r['p_value']:>12.6f}")

# ============================================================
# EXPECTED CONCENTRATION COMPARISON
# ============================================================

# Compute expected concentration for each folio-count level among rare middles
# to see if observed concentrations exceed chance
folio_count_groups = defaultdict(list)
for mid, folios in rare_middles.items():
    folio_count_groups[len(folios)].append(rare_concentrations[mid])

print("\nConcentration by folio count (rare MIDDLEs):")
print(f"{'N_folios':>10} {'N_middles':>10} {'Mean_conc':>10} {'Expected':>10} {'Excess':>10}")
print("-" * 55)
for n_fol in sorted(folio_count_groups.keys()):
    vals = folio_count_groups[n_fol]
    mean_obs = np.mean(vals)
    exp = expected_concentration(n_fol, section_proportions)
    excess = mean_obs - exp
    print(f"{n_fol:>10} {len(vals):>10} {mean_obs:>10.4f} {exp:>10.4f} {excess:>+10.4f}")

# ============================================================
# VERDICT
# ============================================================

# SUPPORTED if:
# 1. Rare middles are significantly more section-concentrated than common
#    (Mann-Whitney p < 0.05)
# 2. OR a substantial fraction (>= 10%) of testable rare middles are
#    significantly section-clustered after Bonferroni

condition1 = mw_p < 0.05 if not np.isnan(mw_p) else False
condition2 = pct_concentrated >= 10.0

verdict = "SUPPORTED" if (condition1 or condition2) else "NOT_SUPPORTED"

print(f"\nVerdict: {verdict}")
print(f"  Condition 1 (rare > common, MW p < 0.05): {condition1} (p={mw_p:.6f})")
print(f"  Condition 2 (>= 10% Bonferroni sig): {condition2} ({pct_concentrated:.1f}%)")

# ============================================================
# SAVE RESULTS
# ============================================================

output = {
    "test": "Rare MIDDLE Section Clustering",
    "n_rare_middles": len(rare_middles),
    "n_testable": len(chi_results),
    "n_significant_bonferroni": n_significant,
    "pct_section_concentrated": round(pct_concentrated, 2),
    "mean_section_concentration_rare": round(mean_rare, 4),
    "mean_section_concentration_common": round(mean_common, 4),
    "mann_whitney_u": round(float(mw_u), 2) if not np.isnan(mw_u) else None,
    "p_value": round(float(mw_p), 6) if not np.isnan(mw_p) else None,
    "verdict": verdict,
    "top_concentrated_middles": top_concentrated,
    "section_sizes": {sec: section_folio_counts[sec] for sec in sections_sorted},
    "notes": (
        f"Rare = 2-15 folios ({len(rare_middles)} MIDDLEs). "
        f"Common = >= 16 folios ({len(common_middles)} MIDDLEs). "
        f"Chi-square requires >= {MIN_FOLIOS_FOR_TEST} folios. "
        f"Bonferroni alpha = {bonferroni_threshold:.6f} over {n_tests} tests. "
        f"Section proportions based on folio counts."
    )
}

output_path = 'C:/git/voynich/phases/MIDDLE_MATERIAL_SEMANTICS/results/rare_middle_section_clustering.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
