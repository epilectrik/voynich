"""
Phase 511: PARAGRAPH_ORDERING_WITHIN_FOLIOS

Tests whether paragraph operational zones appear in a preferred ORDER within folios.
Phase 510 (C1398) identified 4 gradient zones:
  Zone 0: THERMAL-QO (heat source management)
  Zone 1: CONTAINMENT-Sealing (d-sealing, dy-closure)
  Zone 2: OPERATION-Iteration (i-iteration, bare suffix)
  Zone 3: MONITORING-Phase (h-kernel, monitoring)

If thermal paragraphs systematically come first and monitoring last,
that implies a procedural sequence. If random, paragraphs are
independent subroutines.

Uses Phase 510 paragraph labels (264 paragraphs with 3+ body lines).
"""

import json
import sys
import os
import numpy as np
from collections import defaultdict, Counter
from scipy import stats

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

np.random.seed(42)

# ==============================================================================
# Load Phase 510 paragraph labels
# ==============================================================================

with open('phases/PARAGRAPH_PROGRAM_TYPING/results/paragraph_program_typing.json', 'r') as f:
    p510 = json.load(f)

labels = p510['paragraph_labels']
print(f"Loaded {len(labels)} paragraph labels from Phase 510")

ZONE_NAMES = {
    0: "THERMAL-QO",
    1: "CONTAINMENT-Sealing",
    2: "OPERATION-Iteration",
    3: "MONITORING-Phase"
}

# ==============================================================================
# Build folio-level paragraph sequences
# ==============================================================================

# Group paragraphs by folio, sorted by par_idx (paragraph ordinal within folio)
folio_paras = defaultdict(list)
for lab in labels:
    folio_paras[lab['folio']].append(lab)

# Sort within each folio by par_idx
for f in folio_paras:
    folio_paras[f].sort(key=lambda x: x['par_idx'])

# Map section names to normalized form
# Phase 510 uses 'section' field with values like 'B', 'H', 'S', 'C', 'T'
# Build section lookup from folio metadata
section_map = {}
for lab in labels:
    section_map[lab['folio']] = lab.get('section', 'UNK')

# Identify multi-paragraph folios and multi-zone folios
multi_para_folios = {f: ps for f, ps in folio_paras.items() if len(ps) >= 2}
multi_zone_folios = {f: ps for f, ps in folio_paras.items()
                     if len(set(p['cluster'] for p in ps)) >= 2}

print(f"Total folios: {len(folio_paras)}")
print(f"Multi-paragraph folios (2+): {len(multi_para_folios)}")
print(f"Multi-zone folios (2+ zones): {len(multi_zone_folios)}")

# Section distribution
section_counts = Counter(section_map[f] for f in folio_paras)
print(f"Section distribution: {dict(section_counts)}")

results = {
    "metadata": {
        "phase": "PARAGRAPH_ORDERING_WITHIN_FOLIOS (Phase 511)",
        "total_paragraphs": len(labels),
        "total_folios": len(folio_paras),
        "multi_para_folios": len(multi_para_folios),
        "multi_zone_folios": len(multi_zone_folios),
        "zone_names": ZONE_NAMES,
        "zone_sizes": dict(Counter(lab['cluster'] for lab in labels)),
        "random_seed": 42
    }
}

# ==============================================================================
# T1: Zone Ordinal Position Test
# ==============================================================================

print("\n" + "="*70)
print("T1: Zone Ordinal Position Test")
print("="*70)

# For each paragraph in a multi-paragraph folio, compute normalized ordinal
# 0 = first paragraph, 1 = last paragraph
zone_ordinals = defaultdict(list)

for f, ps in multi_para_folios.items():
    n_paras = len(ps)
    for i, p in enumerate(ps):
        norm_ord = i / (n_paras - 1) if n_paras > 1 else 0.5
        zone_ordinals[p['cluster']].append(norm_ord)

print(f"\nZone mean ordinal positions (0=first, 1=last):")
zone_means = {}
zone_medians = {}
zone_sds = {}
for z in sorted(zone_ordinals.keys()):
    vals = zone_ordinals[z]
    zone_means[z] = np.mean(vals)
    zone_medians[z] = np.median(vals)
    zone_sds[z] = np.std(vals)
    print(f"  Zone {z} ({ZONE_NAMES[z]}): mean={zone_means[z]:.3f}, "
          f"median={zone_medians[z]:.3f}, sd={zone_sds[z]:.3f}, n={len(vals)}")

# Kruskal-Wallis test
groups = [zone_ordinals[z] for z in sorted(zone_ordinals.keys())]
kw_stat, kw_p = stats.kruskal(*groups)
print(f"\nKruskal-Wallis: H={kw_stat:.3f}, p={kw_p:.6f}")

# Effect size: epsilon-squared = H / (n-1)
n_total = sum(len(g) for g in groups)
eps_sq = kw_stat / (n_total - 1)
print(f"Epsilon-squared: {eps_sq:.4f}")

# Pairwise Mann-Whitney for significant pairs
pairwise_mw = {}
zones_list = sorted(zone_ordinals.keys())
for i in range(len(zones_list)):
    for j in range(i+1, len(zones_list)):
        z_i, z_j = zones_list[i], zones_list[j]
        u_stat, u_p = stats.mannwhitneyu(zone_ordinals[z_i], zone_ordinals[z_j],
                                          alternative='two-sided')
        pairwise_mw[f"{z_i}_vs_{z_j}"] = {"U": float(u_stat), "p": float(u_p)}
        if u_p < 0.05:
            print(f"  Zone {z_i} vs {z_j}: U={u_stat:.1f}, p={u_p:.6f} *")

results["T1_zone_ordinal"] = {
    "zone_means": {str(k): float(v) for k, v in zone_means.items()},
    "zone_medians": {str(k): float(v) for k, v in zone_medians.items()},
    "zone_sds": {str(k): float(v) for k, v in zone_sds.items()},
    "zone_ns": {str(k): len(v) for k, v in zone_ordinals.items()},
    "kruskal_wallis_H": float(kw_stat),
    "kruskal_wallis_p": float(kw_p),
    "epsilon_squared": float(eps_sq),
    "pairwise_mann_whitney": pairwise_mw,
    "verdict": "SIGNIFICANT" if kw_p < 0.05 else "NOT_SIGNIFICANT",
    "interpretation": (
        f"Zones {'DO' if kw_p < 0.05 else 'do NOT'} have distinct positional preferences "
        f"within folios (KW H={kw_stat:.2f}, p={kw_p:.4f}, eps^2={eps_sq:.4f}). "
        f"Zone ordering: {' < '.join(f'{ZONE_NAMES[z]}({zone_means[z]:.3f})' for z in sorted(zone_means, key=zone_means.get))}"
    )
}

# ==============================================================================
# T2: First-Paragraph Zone Distribution
# ==============================================================================

print("\n" + "="*70)
print("T2: First-Paragraph Zone Distribution")
print("="*70)

# For multi-zone folios, what zone does the first paragraph fall into?
first_zones = []
for f, ps in multi_zone_folios.items():
    first_zones.append(ps[0]['cluster'])

first_zone_counts = Counter(first_zones)
n_multi_zone = len(first_zones)
expected_uniform = n_multi_zone / 4.0

print(f"\nFirst-paragraph zone distribution (n={n_multi_zone} multi-zone folios):")
for z in sorted(ZONE_NAMES.keys()):
    obs = first_zone_counts.get(z, 0)
    ratio = obs / expected_uniform if expected_uniform > 0 else 0
    print(f"  Zone {z} ({ZONE_NAMES[z]}): {obs} ({obs/n_multi_zone*100:.1f}%), "
          f"expected={expected_uniform:.1f}, O/E={ratio:.2f}")

# Chi-squared against uniform
observed = [first_zone_counts.get(z, 0) for z in range(4)]
expected = [expected_uniform] * 4
chi2_first, p_first = stats.chisquare(observed, expected)
print(f"\nChi-squared vs uniform: chi2={chi2_first:.3f}, p={p_first:.6f}")

# Also test against corpus zone proportions (more conservative)
zone_total = Counter(lab['cluster'] for lab in labels)
zone_props = {z: zone_total[z] / len(labels) for z in range(4)}
expected_prop = [zone_props[z] * n_multi_zone for z in range(4)]
chi2_first_prop, p_first_prop = stats.chisquare(observed, expected_prop)
print(f"Chi-squared vs corpus proportions: chi2={chi2_first_prop:.3f}, p={p_first_prop:.6f}")

results["T2_first_paragraph"] = {
    "n_multi_zone_folios": n_multi_zone,
    "observed": {str(z): first_zone_counts.get(z, 0) for z in range(4)},
    "expected_uniform": float(expected_uniform),
    "expected_proportional": {str(z): float(expected_prop[z]) for z in range(4)},
    "chi2_vs_uniform": float(chi2_first),
    "p_vs_uniform": float(p_first),
    "chi2_vs_proportional": float(chi2_first_prop),
    "p_vs_proportional": float(p_first_prop),
    "zone_0_enrichment_vs_proportional": float(
        (first_zone_counts.get(0, 0) / expected_prop[0]) if expected_prop[0] > 0 else 0
    ),
    "verdict": "SIGNIFICANT" if p_first_prop < 0.05 else "NOT_SIGNIFICANT"
}

# ==============================================================================
# T3: Last-Paragraph Zone Distribution
# ==============================================================================

print("\n" + "="*70)
print("T3: Last-Paragraph Zone Distribution")
print("="*70)

last_zones = []
for f, ps in multi_zone_folios.items():
    last_zones.append(ps[-1]['cluster'])

last_zone_counts = Counter(last_zones)

print(f"\nLast-paragraph zone distribution (n={n_multi_zone} multi-zone folios):")
for z in sorted(ZONE_NAMES.keys()):
    obs = last_zone_counts.get(z, 0)
    ratio = obs / expected_uniform if expected_uniform > 0 else 0
    print(f"  Zone {z} ({ZONE_NAMES[z]}): {obs} ({obs/n_multi_zone*100:.1f}%), "
          f"expected={expected_uniform:.1f}, O/E={ratio:.2f}")

observed_last = [last_zone_counts.get(z, 0) for z in range(4)]
chi2_last, p_last = stats.chisquare(observed_last, expected)
print(f"\nChi-squared vs uniform: chi2={chi2_last:.3f}, p={p_last:.6f}")

chi2_last_prop, p_last_prop = stats.chisquare(observed_last, expected_prop)
print(f"Chi-squared vs corpus proportions: chi2={chi2_last_prop:.3f}, p={p_last_prop:.6f}")

results["T3_last_paragraph"] = {
    "observed": {str(z): last_zone_counts.get(z, 0) for z in range(4)},
    "chi2_vs_uniform": float(chi2_last),
    "p_vs_uniform": float(p_last),
    "chi2_vs_proportional": float(chi2_last_prop),
    "p_vs_proportional": float(p_last_prop),
    "zone_3_enrichment_vs_proportional": float(
        (last_zone_counts.get(3, 0) / expected_prop[3]) if expected_prop[3] > 0 else 0
    ),
    "verdict": "SIGNIFICANT" if p_last_prop < 0.05 else "NOT_SIGNIFICANT"
}

# ==============================================================================
# T4: Zone Transition Matrix
# ==============================================================================

print("\n" + "="*70)
print("T4: Zone Transition Matrix")
print("="*70)

# Build transition counts from adjacent paragraphs within folios
trans_counts = np.zeros((4, 4), dtype=int)
total_transitions = 0

for f, ps in folio_paras.items():
    if len(ps) < 2:
        continue
    for i in range(len(ps) - 1):
        z_from = ps[i]['cluster']
        z_to = ps[i+1]['cluster']
        trans_counts[z_from][z_to] += 1
        total_transitions += 1

print(f"\nTotal adjacent-paragraph transitions: {total_transitions}")
print(f"\nTransition matrix (row=from, col=to):")
print(f"{'':>25}", end='')
for z in range(4):
    print(f"  Z{z:>4}", end='')
print()
for z_from in range(4):
    print(f"  Z{z_from} ({ZONE_NAMES[z_from][:18]:>18})", end='')
    for z_to in range(4):
        print(f"  {trans_counts[z_from][z_to]:>4}", end='')
    print()

# Chi-squared test for independence
chi2_trans, p_trans, dof_trans, expected_trans = stats.chi2_contingency(
    trans_counts + 1e-10  # avoid zeros
)
print(f"\nChi-squared for independence: chi2={chi2_trans:.3f}, p={p_trans:.6f}, dof={dof_trans}")
cramers_v_trans = np.sqrt(chi2_trans / (total_transitions * 3))
print(f"Cramer's V: {cramers_v_trans:.3f}")

results["T4_transition_matrix"] = {
    "total_transitions": total_transitions,
    "matrix": {str(z_from): {str(z_to): int(trans_counts[z_from][z_to])
               for z_to in range(4)} for z_from in range(4)},
    "chi2": float(chi2_trans),
    "p_value": float(p_trans),
    "dof": int(dof_trans),
    "cramers_v": float(cramers_v_trans),
    "verdict": "STRUCTURED" if p_trans < 0.05 else "INDEPENDENT"
}

# ==============================================================================
# T5: Zone Bigram Enrichment
# ==============================================================================

print("\n" + "="*70)
print("T5: Zone Bigram Enrichment")
print("="*70)

# Compute observed/expected ratios for each pair
row_sums = trans_counts.sum(axis=1)
col_sums = trans_counts.sum(axis=0)
total = trans_counts.sum()

print(f"\nO/E ratios (observed/expected under independence):")
print(f"{'':>25}", end='')
for z in range(4):
    print(f"  Z{z:>6}", end='')
print()

bigram_enrichment = {}
for z_from in range(4):
    print(f"  Z{z_from} ({ZONE_NAMES[z_from][:18]:>18})", end='')
    for z_to in range(4):
        if row_sums[z_from] > 0 and col_sums[z_to] > 0:
            expected = (row_sums[z_from] * col_sums[z_to]) / total
            oe = trans_counts[z_from][z_to] / expected if expected > 0 else 0
        else:
            oe = 0
        print(f"  {oe:>6.2f}", end='')
        bigram_enrichment[f"{z_from}->{z_to}"] = float(oe)
    print()

# Self-transition analysis
self_trans = sum(trans_counts[z][z] for z in range(4))
self_expected = sum((row_sums[z] * col_sums[z]) / total for z in range(4))
self_oe = self_trans / self_expected if self_expected > 0 else 0
print(f"\nSelf-transitions: observed={self_trans}, expected={self_expected:.1f}, O/E={self_oe:.2f}")

# Most enriched and depleted
sorted_bigrams = sorted(bigram_enrichment.items(), key=lambda x: x[1], reverse=True)
print(f"\nTop 5 enriched bigrams:")
for pair, oe in sorted_bigrams[:5]:
    z_from, z_to = pair.split('->')
    obs = trans_counts[int(z_from)][int(z_to)]
    print(f"  {pair} ({ZONE_NAMES[int(z_from)][:12]}->{ZONE_NAMES[int(z_to)][:12]}): "
          f"O/E={oe:.2f}, n={obs}")

print(f"\nTop 5 depleted bigrams:")
for pair, oe in sorted_bigrams[-5:]:
    z_from, z_to = pair.split('->')
    obs = trans_counts[int(z_from)][int(z_to)]
    print(f"  {pair} ({ZONE_NAMES[int(z_from)][:12]}->{ZONE_NAMES[int(z_to)][:12]}): "
          f"O/E={oe:.2f}, n={obs}")

results["T5_bigram_enrichment"] = {
    "enrichment_ratios": bigram_enrichment,
    "self_transition_observed": int(self_trans),
    "self_transition_expected": float(self_expected),
    "self_transition_OE": float(self_oe),
    "top_enriched": sorted_bigrams[:5],
    "top_depleted": sorted_bigrams[-5:]
}

# ==============================================================================
# T6: Monotonicity Test
# ==============================================================================

print("\n" + "="*70)
print("T6: Monotonicity Test")
print("="*70)

# Assign zone numbers 0-3 in thermal->containment->operation->monitoring order
# (already the cluster numbering). Compute Spearman rho between paragraph ordinal
# and zone number within each multi-zone folio.

folio_rhos = []
folio_rho_details = {}

for f, ps in multi_zone_folios.items():
    ordinals = list(range(len(ps)))
    zones = [p['cluster'] for p in ps]
    if len(set(zones)) < 2:
        continue  # Need variation in both
    if len(ordinals) < 3:
        # Spearman needs 3+ for meaningful test
        rho, p_val = stats.spearmanr(ordinals, zones)
        folio_rhos.append(rho)
        folio_rho_details[f] = {"rho": float(rho), "p": float(p_val), "n": len(ps)}
    else:
        rho, p_val = stats.spearmanr(ordinals, zones)
        folio_rhos.append(rho)
        folio_rho_details[f] = {"rho": float(rho), "p": float(p_val), "n": len(ps)}

mean_rho = np.mean(folio_rhos)
median_rho = np.median(folio_rhos)
n_positive = sum(1 for r in folio_rhos if r > 0)
n_negative = sum(1 for r in folio_rhos if r < 0)
n_zero = sum(1 for r in folio_rhos if r == 0)

# One-sample t-test: is mean rho different from 0?
t_stat, t_p = stats.ttest_1samp(folio_rhos, 0)

# Wilcoxon signed-rank test (non-parametric)
try:
    w_stat, w_p = stats.wilcoxon(folio_rhos)
except ValueError:
    w_stat, w_p = np.nan, np.nan

print(f"\nPer-folio Spearman rho (ordinal vs zone number):")
print(f"  N folios: {len(folio_rhos)}")
print(f"  Mean rho: {mean_rho:.3f}")
print(f"  Median rho: {median_rho:.3f}")
print(f"  Positive: {n_positive}, Negative: {n_negative}, Zero: {n_zero}")
print(f"  t-test vs 0: t={t_stat:.3f}, p={t_p:.6f}")
print(f"  Wilcoxon: W={w_stat:.1f}, p={w_p:.6f}" if not np.isnan(w_stat) else "  Wilcoxon: N/A")

results["T6_monotonicity"] = {
    "n_folios": len(folio_rhos),
    "mean_rho": float(mean_rho),
    "median_rho": float(median_rho),
    "n_positive": int(n_positive),
    "n_negative": int(n_negative),
    "n_zero": int(n_zero),
    "ttest_t": float(t_stat),
    "ttest_p": float(t_p),
    "wilcoxon_W": float(w_stat) if not np.isnan(w_stat) else None,
    "wilcoxon_p": float(w_p) if not np.isnan(w_p) else None,
    "verdict": "MONOTONIC" if t_p < 0.05 and mean_rho > 0 else "NOT_MONOTONIC",
    "interpretation": (
        f"Mean rho={mean_rho:.3f} is {'significantly' if t_p < 0.05 else 'not significantly'} "
        f"different from 0 (t={t_stat:.2f}, p={t_p:.4f}). "
        f"{n_positive}/{len(folio_rhos)} folios show positive correlation (thermal-early, monitoring-late)."
    )
}

# ==============================================================================
# T7: First-Half vs Second-Half Zone Composition
# ==============================================================================

print("\n" + "="*70)
print("T7: First-Half vs Second-Half Zone Composition")
print("="*70)

# Split each folio's paragraphs into first half and second half
first_half_zones = []
second_half_zones = []

for f, ps in multi_para_folios.items():
    n = len(ps)
    mid = n // 2
    if mid == 0:
        continue
    for p in ps[:mid]:
        first_half_zones.append(p['cluster'])
    for p in ps[mid:]:
        second_half_zones.append(p['cluster'])

first_half_counts = Counter(first_half_zones)
second_half_counts = Counter(second_half_zones)

print(f"\nFirst-half vs second-half zone distributions:")
print(f"{'Zone':>30}  {'First':>8}  {'Second':>8}  {'F%':>6}  {'S%':>6}  {'Ratio':>6}")
contingency_halves = np.zeros((2, 4), dtype=int)
for z in range(4):
    f_count = first_half_counts.get(z, 0)
    s_count = second_half_counts.get(z, 0)
    f_pct = f_count / len(first_half_zones) * 100 if first_half_zones else 0
    s_pct = s_count / len(second_half_zones) * 100 if second_half_zones else 0
    ratio = f_pct / s_pct if s_pct > 0 else float('inf')
    print(f"  Z{z} ({ZONE_NAMES[z]:>25}): {f_count:>6}  {s_count:>8}  "
          f"{f_pct:>5.1f}%  {s_pct:>5.1f}%  {ratio:>5.2f}")
    contingency_halves[0][z] = f_count
    contingency_halves[1][z] = s_count

# Chi-squared test
chi2_halves, p_halves, dof_halves, _ = stats.chi2_contingency(contingency_halves + 1e-10)
n_halves_total = len(first_half_zones) + len(second_half_zones)
cramers_v_halves = np.sqrt(chi2_halves / (n_halves_total * min(2-1, 4-1)))
print(f"\nChi-squared: chi2={chi2_halves:.3f}, p={p_halves:.6f}")
print(f"Cramer's V: {cramers_v_halves:.3f}")

results["T7_half_composition"] = {
    "first_half_n": len(first_half_zones),
    "second_half_n": len(second_half_zones),
    "first_half_counts": {str(z): first_half_counts.get(z, 0) for z in range(4)},
    "second_half_counts": {str(z): second_half_counts.get(z, 0) for z in range(4)},
    "first_half_pcts": {str(z): first_half_counts.get(z, 0) / len(first_half_zones) * 100
                        for z in range(4)},
    "second_half_pcts": {str(z): second_half_counts.get(z, 0) / len(second_half_zones) * 100
                         for z in range(4)},
    "chi2": float(chi2_halves),
    "p_value": float(p_halves),
    "cramers_v": float(cramers_v_halves),
    "verdict": "HALVES_DIFFER" if p_halves < 0.05 else "HALVES_EQUIVALENT"
}

# ==============================================================================
# T8: Section-Controlled Ordering
# ==============================================================================

print("\n" + "="*70)
print("T8: Section-Controlled Ordering")
print("="*70)

# Within each section, repeat T1 (zone ordinal position) and T6 (monotonicity)
sections = sorted(set(section_map[f] for f in multi_para_folios))
section_results = {}

for sec in sections:
    sec_folios = {f: ps for f, ps in multi_para_folios.items()
                  if section_map[f] == sec}

    if len(sec_folios) < 3:
        print(f"\nSection {sec}: Too few folios ({len(sec_folios)}), skipping")
        section_results[sec] = {"skipped": True, "n_folios": len(sec_folios)}
        continue

    # T1 within section
    sec_zone_ordinals = defaultdict(list)
    for f, ps in sec_folios.items():
        if len(ps) < 2:
            continue
        for i, p in enumerate(ps):
            norm_ord = i / (len(ps) - 1) if len(ps) > 1 else 0.5
            sec_zone_ordinals[p['cluster']].append(norm_ord)

    # Need at least 2 zones with data
    active_zones = [z for z in range(4) if len(sec_zone_ordinals[z]) >= 2]

    if len(active_zones) < 2:
        print(f"\nSection {sec}: Too few active zones ({len(active_zones)}), skipping")
        section_results[sec] = {"skipped": True, "n_folios": len(sec_folios),
                                 "n_active_zones": len(active_zones)}
        continue

    sec_groups = [sec_zone_ordinals[z] for z in active_zones]
    sec_kw_stat, sec_kw_p = stats.kruskal(*sec_groups)

    sec_means = {z: np.mean(sec_zone_ordinals[z]) for z in active_zones}

    # T6 within section: monotonicity
    sec_multi_zone = {f: ps for f, ps in sec_folios.items()
                       if len(set(p['cluster'] for p in ps)) >= 2}
    sec_rhos = []
    for f, ps in sec_multi_zone.items():
        ordinals = list(range(len(ps)))
        zones = [p['cluster'] for p in ps]
        if len(set(zones)) < 2:
            continue
        rho, _ = stats.spearmanr(ordinals, zones)
        sec_rhos.append(rho)

    sec_mean_rho = np.mean(sec_rhos) if sec_rhos else np.nan
    sec_t, sec_t_p = stats.ttest_1samp(sec_rhos, 0) if len(sec_rhos) >= 3 else (np.nan, np.nan)

    print(f"\nSection {sec} (n={len(sec_folios)} folios, {sum(len(ps) for ps in sec_folios.values())} paras):")
    print(f"  Zone ordinal means: ", end='')
    for z in active_zones:
        print(f"Z{z}={sec_means[z]:.3f}(n={len(sec_zone_ordinals[z])}) ", end='')
    print()
    print(f"  KW: H={sec_kw_stat:.3f}, p={sec_kw_p:.6f}")
    print(f"  Monotonicity: mean_rho={sec_mean_rho:.3f}, n={len(sec_rhos)} folios"
          + (f", t={sec_t:.2f}, p={sec_t_p:.4f}" if not np.isnan(sec_t) else ""))

    section_results[sec] = {
        "skipped": False,
        "n_folios": len(sec_folios),
        "n_paras": sum(len(ps) for ps in sec_folios.values()),
        "n_multi_zone_folios": len(sec_multi_zone),
        "zone_means": {str(z): float(sec_means[z]) for z in active_zones},
        "zone_ns": {str(z): len(sec_zone_ordinals[z]) for z in active_zones},
        "kw_H": float(sec_kw_stat),
        "kw_p": float(sec_kw_p),
        "monotonicity_mean_rho": float(sec_mean_rho) if not np.isnan(sec_mean_rho) else None,
        "monotonicity_n": len(sec_rhos),
        "monotonicity_t": float(sec_t) if not np.isnan(sec_t) else None,
        "monotonicity_p": float(sec_t_p) if not np.isnan(sec_t_p) else None,
        "zone_order_significant": bool(sec_kw_p < 0.05),
        "monotonicity_significant": bool(sec_t_p < 0.05) if not np.isnan(sec_t_p) else None
    }

results["T8_section_controlled"] = section_results

# ==============================================================================
# Summary and Interpretation
# ==============================================================================

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

# Count how many tests pass
tests_significant = []
tests_significant.append(("T1_zone_ordinal", kw_p < 0.05))
tests_significant.append(("T2_first_para", p_first_prop < 0.05))
tests_significant.append(("T3_last_para", p_last_prop < 0.05))
tests_significant.append(("T4_transition", p_trans < 0.05))
tests_significant.append(("T6_monotonicity", t_p < 0.05 and mean_rho > 0))
tests_significant.append(("T7_halves", p_halves < 0.05))

# Section-controlled: do any survive?
sec_ordering_survives = any(
    section_results[s].get("zone_order_significant", False)
    for s in section_results
    if not section_results[s].get("skipped", True)
)
sec_mono_survives = any(
    section_results[s].get("monotonicity_significant", False)
    for s in section_results
    if not section_results[s].get("skipped", True)
    and section_results[s].get("monotonicity_significant") is not None
)
tests_significant.append(("T8_section_ordering_survives", sec_ordering_survives))
tests_significant.append(("T8_section_monotonicity_survives", sec_mono_survives))

print(f"\nTest results:")
for name, sig in tests_significant:
    print(f"  {name}: {'PASS' if sig else 'FAIL'}")

n_pass = sum(1 for _, sig in tests_significant if sig)
print(f"\n{n_pass}/{len(tests_significant)} tests significant")

# Determine overall verdict
if n_pass >= 5 and sec_ordering_survives:
    overall = "STRONG_ORDERING"
    summary = ("Paragraphs show a strong preferred ordering within folios that "
               "survives section control. Zones have distinct positional preferences.")
elif n_pass >= 3:
    overall = "MODERATE_ORDERING"
    summary = ("Paragraphs show some positional preferences, but the effect may be "
               "partially confounded with section composition.")
elif n_pass >= 1:
    overall = "WEAK_ORDERING"
    summary = ("Paragraphs show weak positional tendencies that do not consistently "
               "survive controls. Ordering is present but not strong.")
else:
    overall = "NO_ORDERING"
    summary = ("Paragraphs show no preferred ordering within folios. "
               "Zones are independently positioned, consistent with parallel subroutines.")

print(f"\nOverall verdict: {overall}")
print(f"Summary: {summary}")

results["summary"] = {
    "test_verdicts": {name: sig for name, sig in tests_significant},
    "n_pass": n_pass,
    "n_total": len(tests_significant),
    "overall_verdict": overall,
    "summary": summary,
    "self_transition_enrichment": float(self_oe),
    "zone_order_by_mean_ordinal": [
        {"zone": z, "name": ZONE_NAMES[z], "mean_ordinal": float(zone_means[z])}
        for z in sorted(zone_means, key=zone_means.get)
    ]
}

# ==============================================================================
# Save results
# ==============================================================================

output_path = 'phases/PARAGRAPH_ORDERING_WITHIN_FOLIOS/results/paragraph_ordering.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {output_path}")
