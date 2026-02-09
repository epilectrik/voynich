#!/usr/bin/env python3
"""
MATERIAL_LOCUS_SEARCH Phase - Test 5: RI Extension -> B-Section Outcome Correlation

Question: For the same PP base, do different RI extensions correlate with
different B sections?

Method:
  1. Build B vocabulary per section: for each B section, the set of MIDDLEs used.
  2. Classify Currier A tokens into RI/PP using RecordAnalyzer.
  3. For RI tokens, extract PP base and extension (RI = PP + extension).
  4. For each PP base that gets multiple extensions, check which B sections
     use that PP base (via MIDDLE overlap).
  5. Key discriminator: same extension on DIFFERENT PP bases -> same B sections
     means material (extension tags the material destination);
     different B sections means operational parameterization (per C917-C918).
  6. Chi-square / Cramer's V: extension type x B-section presence.
  7. Secondary: extension-prefix alignment (h->ct, k/t->qo) per C917.

Pass: Extension-base combo predicts B section (V > 0.15, p < 0.01).
Fail: Extension independent of B section -- operational parameterization per C917-C918.

References: C913 (RI derivational morphology), C917 (extension-prefix alignment),
            C918 (Currier A operational configuration layer).
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

import numpy as np
from scipy.stats import chi2_contingency

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology, RecordAnalyzer

# ============================================================
# 1. SETUP
# ============================================================
print("=" * 70)
print("Test 5: RI Extension -> B-Section Outcome Correlation")
print("=" * 70)

tx = Transcript()
morph = Morphology()

# B sections of interest
B_SECTIONS = ['B', 'H', 'S', 'T', 'C']

# ============================================================
# 2. BUILD B VOCABULARY PER SECTION
# ============================================================
print("\nBuilding B vocabulary per section...")

b_section_middles = defaultdict(set)   # section -> set of MIDDLEs
b_middle_sections = defaultdict(set)   # MIDDLE -> set of sections
b_middle_counts = defaultdict(Counter) # section -> Counter of MIDDLEs
all_b_middles = set()

for token in tx.currier_b():
    m = morph.extract(token.word)
    if m.middle and m.middle != '_EMPTY_':
        section = token.section
        b_section_middles[section].add(m.middle)
        b_middle_sections[m.middle].add(section)
        b_middle_counts[section][m.middle] += 1
        all_b_middles.add(m.middle)

for section in sorted(b_section_middles.keys()):
    print(f"  Section {section}: {len(b_section_middles[section])} unique MIDDLEs")
print(f"  Total B vocabulary: {len(all_b_middles)} unique MIDDLEs")

# PP middles sorted longest-first for greedy matching (same as RI_EXTENSION_MAPPING)
# Secondary sort by alphabetical for reproducibility
pp_sorted = sorted(all_b_middles, key=lambda x: (-len(x), x))

# ============================================================
# 3. EXTRACT RI EXTENSIONS FROM CURRIER A
# ============================================================
print("\nExtracting RI extensions from Currier A...")


def get_extension(ri_middle):
    """Find the PP base and extension for an RI MIDDLE.

    Mirrors the method from RI_EXTENSION_MAPPING/01_extension_distribution.py.
    """
    for pp in pp_sorted:
        if len(pp) >= 2:
            if ri_middle.startswith(pp) and len(ri_middle) > len(pp):
                return {
                    'pp_base': pp,
                    'extension': ri_middle[len(pp):],
                    'position': 'suffix'
                }
            elif ri_middle.endswith(pp) and len(ri_middle) > len(pp):
                return {
                    'pp_base': pp,
                    'extension': ri_middle[:-len(pp)],
                    'position': 'prefix'
                }
    return None


# Collect RI tokens with their extensions
ri_records = []

for token in tx.currier_a():
    m = morph.extract(token.word)
    if m.middle and m.middle != '_EMPTY_' and m.middle not in all_b_middles:
        # This is an RI MIDDLE (A-exclusive)
        ext_info = get_extension(m.middle)
        if ext_info is not None:
            ri_records.append({
                'word': token.word,
                'ri_middle': m.middle,
                'pp_base': ext_info['pp_base'],
                'extension': ext_info['extension'],
                'ext_position': ext_info['position'],
                'prefix': m.prefix,
                'suffix': m.suffix,
                'folio': token.folio,
                'section': token.section,
                'line': token.line,
            })

print(f"  RI tokens with PP base: {len(ri_records)}")

# Focus on single-character extensions (71.6% of all, per C913)
single_char_ri = [r for r in ri_records if len(r['extension']) == 1]
print(f"  Single-char extensions: {len(single_char_ri)}")

# Extension frequency
ext_counts = Counter(r['extension'] for r in single_char_ri)
print(f"  Extension types: {dict(ext_counts.most_common(10))}")

# ============================================================
# 4. PP BASE -> B SECTION MAPPING
# ============================================================
print("\nMapping PP bases to B sections...")

# For each PP base used in RI, determine which B sections use that PP base
pp_base_b_sections = {}
for r in single_char_ri:
    pp = r['pp_base']
    if pp not in pp_base_b_sections:
        pp_base_b_sections[pp] = b_middle_sections.get(pp, set())

# Count PP bases by number of B sections they appear in
section_spread = Counter(len(v) for v in pp_base_b_sections.values())
print(f"  PP bases in RI tokens: {len(pp_base_b_sections)}")
print(f"  Section spread: {dict(sorted(section_spread.items()))}")

# Only consider PP bases that appear in at least 2 B sections (needed for correlation)
multi_section_pp = {pp: secs for pp, secs in pp_base_b_sections.items()
                    if len(secs) >= 2}
print(f"  PP bases in 2+ B sections: {len(multi_section_pp)}")

# ============================================================
# 5. PRIMARY TEST: Extension Type x B-Section Presence
# ============================================================
print("\n" + "=" * 70)
print("PRIMARY TEST: Extension correlates with B-section presence of PP base")
print("=" * 70)

# Build contingency: for each extension, count how many of its PP bases
# are present in each B section
# Approach: each RI token votes for extension x section-of-pp-base

# For the chi-square test, we need a contingency table:
# Rows = extension types, Columns = B sections
# Cell value = count of RI tokens where that extension's PP base is in that section

# Only use extensions with n >= 10 for statistical power
MIN_EXT_COUNT = 10
eligible_extensions = [ext for ext, cnt in ext_counts.items() if cnt >= MIN_EXT_COUNT]
print(f"\nEligible extensions (n >= {MIN_EXT_COUNT}): {eligible_extensions}")

# Build contingency table
all_sections_in_data = sorted(set(s for secs in b_middle_sections.values()
                                   for s in secs if s in B_SECTIONS))
print(f"B sections present: {all_sections_in_data}")

# Method A: For each RI token, mark which B sections its PP base appears in
# This creates a token-level dataset: (extension, section_presence_vector)
ext_section_counts = defaultdict(Counter)  # extension -> Counter of sections

for r in single_char_ri:
    ext = r['extension']
    pp = r['pp_base']
    if ext in eligible_extensions:
        pp_sections = b_middle_sections.get(pp, set())
        for s in pp_sections:
            if s in B_SECTIONS:
                ext_section_counts[ext][s] += 1

# Build contingency table
contingency = []
row_labels = []
for ext in sorted(eligible_extensions):
    row = [ext_section_counts[ext].get(s, 0) for s in all_sections_in_data]
    if sum(row) > 0:
        contingency.append(row)
        row_labels.append(ext)

contingency = np.array(contingency)
print(f"\nContingency table ({len(row_labels)} extensions x {len(all_sections_in_data)} sections):")
print(f"  Extensions: {row_labels}")
print(f"  Sections: {all_sections_in_data}")
print(f"  Table:\n{contingency}")

# Chi-square test
if contingency.shape[0] >= 2 and contingency.shape[1] >= 2:
    chi2, p_value, dof, expected = chi2_contingency(contingency)
    n_total = contingency.sum()
    k = min(contingency.shape)
    cramers_v = math.sqrt(chi2 / (n_total * (k - 1))) if n_total > 0 else 0.0

    print(f"\n  Chi-square: {chi2:.2f}")
    print(f"  p-value: {p_value:.2e}")
    print(f"  Cramer's V: {cramers_v:.4f}")
    print(f"  DOF: {dof}")
else:
    chi2, p_value, cramers_v, dof = 0.0, 1.0, 0.0, 0
    print("  Insufficient dimensions for chi-square test")

# ============================================================
# 6. SECONDARY TEST: Same Extension, Different Bases -> Same B Sections?
# ============================================================
print("\n" + "=" * 70)
print("SECONDARY TEST: Same extension across different bases")
print("=" * 70)

# For each extension, collect the set of B sections per PP base
# If extension encodes material destination, same extension -> same B sections
# If extension encodes operational context (C917-C918), extension is B-section-independent

ext_base_section_profiles = defaultdict(list)  # extension -> list of (pp_base, section_set)

for r in single_char_ri:
    ext = r['extension']
    pp = r['pp_base']
    if ext in eligible_extensions:
        pp_secs = frozenset(b_middle_sections.get(pp, set()) & set(B_SECTIONS))
        ext_base_section_profiles[ext].append((pp, pp_secs))

# For each extension, compute consistency: do different bases land in similar sections?
ext_consistency = {}
for ext in eligible_extensions:
    profiles = ext_base_section_profiles.get(ext, [])
    # Unique bases
    unique_bases = set(pp for pp, _ in profiles)
    if len(unique_bases) < 2:
        continue

    # Section set per base
    base_sections = {}
    for pp, secs in profiles:
        if pp not in base_sections:
            base_sections[pp] = secs

    # Pairwise Jaccard of section sets
    bases_list = list(base_sections.keys())
    jaccard_scores = []
    for i in range(len(bases_list)):
        for j in range(i + 1, len(bases_list)):
            s1 = base_sections[bases_list[i]]
            s2 = base_sections[bases_list[j]]
            if s1 or s2:
                inter = len(s1 & s2)
                union = len(s1 | s2)
                jaccard_scores.append(inter / union if union > 0 else 0.0)

    if jaccard_scores:
        ext_consistency[ext] = {
            'n_bases': len(unique_bases),
            'mean_jaccard': float(np.mean(jaccard_scores)),
            'std_jaccard': float(np.std(jaccard_scores)),
            'n_pairs': len(jaccard_scores),
            'section_sets': {pp: sorted(secs) for pp, secs in base_sections.items()},
        }
        print(f"  Extension '{ext}': {len(unique_bases)} bases, "
              f"mean Jaccard={np.mean(jaccard_scores):.3f} +/- {np.std(jaccard_scores):.3f}")

# Overall consistency
all_jaccards = [v['mean_jaccard'] for v in ext_consistency.values()]
overall_consistency = float(np.mean(all_jaccards)) if all_jaccards else 0.0
print(f"\n  Overall mean Jaccard (across extensions): {overall_consistency:.3f}")
print(f"  High Jaccard (>0.7) means same extension -> same sections (material)")
print(f"  Low Jaccard (<0.5) means extension is section-independent (operational)")

# ============================================================
# 7. TERTIARY TEST: Extension x Section Enrichment Patterns
# ============================================================
print("\n" + "=" * 70)
print("TERTIARY TEST: Extension enrichment by B section")
print("=" * 70)

# For each extension, what is the section distribution of its PP bases?
# Compare to the baseline section distribution of ALL PP bases
baseline_section_dist = Counter()
for pp in all_b_middles:
    for s in b_middle_sections.get(pp, set()):
        if s in B_SECTIONS:
            baseline_section_dist[s] += 1

baseline_total = sum(baseline_section_dist.values())
baseline_rates = {s: baseline_section_dist[s] / baseline_total
                  for s in all_sections_in_data}

print(f"\nBaseline B-section distribution of all MIDDLEs:")
for s in all_sections_in_data:
    print(f"  Section {s}: {baseline_rates[s]:.3f} "
          f"({baseline_section_dist[s]}/{baseline_total})")

ext_enrichments = {}
for ext in eligible_extensions:
    ext_total = sum(ext_section_counts[ext].values())
    if ext_total == 0:
        continue

    ext_rates = {s: ext_section_counts[ext].get(s, 0) / ext_total
                 for s in all_sections_in_data}
    enrichment = {}
    for s in all_sections_in_data:
        if baseline_rates[s] > 0:
            enrichment[s] = round(ext_rates[s] / baseline_rates[s], 2)

    ext_enrichments[ext] = {
        'n_tokens': ext_total,
        'section_rates': {s: round(ext_rates[s], 3) for s in all_sections_in_data},
        'enrichment_ratios': enrichment,
    }

    # Find most enriched section
    max_section = max(enrichment, key=enrichment.get) if enrichment else 'none'
    max_ratio = enrichment.get(max_section, 0)
    print(f"  Extension '{ext}' (n={ext_total}): most enriched in "
          f"section {max_section} ({max_ratio:.2f}x)")

# ============================================================
# 8. C917 VALIDATION: Extension-Prefix Alignment in Our Data
# ============================================================
print("\n" + "=" * 70)
print("C917 VALIDATION: Extension-prefix alignment")
print("=" * 70)

# C917: h-extension -> 82% ct prefix; k/t-extension -> qo prefix
ext_prefix_counts = defaultdict(Counter)
for r in single_char_ri:
    ext = r['extension']
    prefix = r['prefix'] or 'NO_PREFIX'
    ext_prefix_counts[ext][prefix] += 1

print("\nExtension-prefix distribution:")
for ext in sorted(eligible_extensions):
    total = sum(ext_prefix_counts[ext].values())
    if total < 5:
        continue
    top_prefixes = ext_prefix_counts[ext].most_common(3)
    prefix_str = ", ".join(f"{p}={c} ({100*c/total:.0f}%)" for p, c in top_prefixes)
    print(f"  '{ext}' (n={total}): {prefix_str}")

# Specific C917 checks
h_ext_ct_rate = 0.0
h_total = sum(ext_prefix_counts['h'].values())
if h_total > 0:
    h_ext_ct_rate = ext_prefix_counts['h'].get('ct', 0) / h_total
    print(f"\n  C917 check: h-extension ct-prefix rate = "
          f"{100*h_ext_ct_rate:.1f}% (expected ~82%)")

kt_qo_rate = 0.0
k_total = sum(ext_prefix_counts.get('k', {}).values())
t_total = sum(ext_prefix_counts.get('t', {}).values())
kt_total = k_total + t_total
if kt_total > 0:
    kt_qo = (ext_prefix_counts.get('k', Counter()).get('qo', 0) +
              ext_prefix_counts.get('t', Counter()).get('qo', 0))
    kt_qo_rate = kt_qo / kt_total
    print(f"  C917 check: k/t-extension qo-prefix rate = "
          f"{100*kt_qo_rate:.1f}% (expected ~40-50%)")

# ============================================================
# 9. PERMUTATION NULL MODEL
# ============================================================
print("\n" + "=" * 70)
print("PERMUTATION NULL MODEL (1000 shuffles)")
print("=" * 70)

n_permutations = 1000
rng = np.random.RandomState(42)

# Null: shuffle extension labels across RI tokens, recompute chi-square
null_chi2 = np.zeros(n_permutations)
null_v = np.zeros(n_permutations)

# Prepare token-level data for shuffling
token_extensions = [r['extension'] for r in single_char_ri
                    if r['extension'] in eligible_extensions]
token_pp_bases = [r['pp_base'] for r in single_char_ri
                  if r['extension'] in eligible_extensions]

for perm in range(n_permutations):
    # Shuffle extensions relative to PP bases
    shuffled_exts = rng.permutation(token_extensions)

    # Rebuild contingency table
    perm_ext_section = defaultdict(Counter)
    for ext, pp in zip(shuffled_exts, token_pp_bases):
        pp_secs = b_middle_sections.get(pp, set())
        for s in pp_secs:
            if s in B_SECTIONS:
                perm_ext_section[ext][s] += 1

    perm_contingency = []
    for ext in row_labels:
        row = [perm_ext_section[ext].get(s, 0) for s in all_sections_in_data]
        perm_contingency.append(row)
    perm_contingency = np.array(perm_contingency)

    # Check minimum cell requirements
    if perm_contingency.sum() > 0 and perm_contingency.shape[0] >= 2:
        try:
            pchi2, _, _, _ = chi2_contingency(perm_contingency)
            pn = perm_contingency.sum()
            pk = min(perm_contingency.shape)
            null_chi2[perm] = pchi2
            null_v[perm] = math.sqrt(pchi2 / (pn * (pk - 1))) if pn > 0 else 0.0
        except ValueError:
            null_chi2[perm] = 0.0
            null_v[perm] = 0.0

p_chi2 = (np.sum(null_chi2 >= chi2) + 1) / (n_permutations + 1)
p_v = (np.sum(null_v >= cramers_v) + 1) / (n_permutations + 1)

print(f"  Observed chi2: {chi2:.2f}, null mean: {null_chi2.mean():.2f}")
print(f"  Observed V: {cramers_v:.4f}, null mean: {null_v.mean():.4f}")
print(f"  Permutation p (chi2): {p_chi2:.4f}")
print(f"  Permutation p (V): {p_v:.4f}")

# ============================================================
# 10. PER-EXTENSION CHI-SQUARE (extension x section, each base independently)
# ============================================================
print("\n" + "=" * 70)
print("PER-EXTENSION: Section prediction per extension type")
print("=" * 70)

# For each extension with enough bases, test if bases of THAT extension
# are non-uniformly distributed across B sections
per_ext_results = {}
for ext in eligible_extensions:
    # For this extension: each RI token contributes its PP base's section set
    ext_tokens = [r for r in single_char_ri if r['extension'] == ext]
    if len(ext_tokens) < 10:
        continue

    # Count section membership of PP bases for this extension
    section_counts = Counter()
    for r in ext_tokens:
        pp_secs = b_middle_sections.get(r['pp_base'], set())
        for s in pp_secs:
            if s in B_SECTIONS:
                section_counts[s] += 1

    total = sum(section_counts.values())
    if total == 0:
        continue

    # Compare to baseline distribution (goodness of fit)
    observed = np.array([section_counts.get(s, 0) for s in all_sections_in_data])
    expected_proportions = np.array([baseline_rates.get(s, 0) for s in all_sections_in_data])

    # Normalize expected to sum to observed total
    if expected_proportions.sum() > 0:
        expected = expected_proportions * total / expected_proportions.sum()
    else:
        continue

    # Chi-square goodness of fit (only where expected > 0)
    mask = expected > 0
    if mask.sum() >= 2:
        from scipy.stats import chisquare
        obs_filtered = observed[mask]
        exp_filtered = expected[mask]
        gof_chi2, gof_p = chisquare(obs_filtered, f_exp=exp_filtered)
    else:
        gof_chi2, gof_p = 0.0, 1.0

    per_ext_results[ext] = {
        'n_tokens': len(ext_tokens),
        'section_counts': {s: int(section_counts.get(s, 0)) for s in all_sections_in_data},
        'chi2_gof': round(float(gof_chi2), 2),
        'p_gof': float(gof_p),
        'deviation_from_baseline': {
            s: round(section_counts.get(s, 0) / total - baseline_rates.get(s, 0), 3)
            for s in all_sections_in_data
        },
    }
    sig_marker = '*' if gof_p < 0.01 else ''
    print(f"  Extension '{ext}' (n={len(ext_tokens)}): "
          f"chi2={gof_chi2:.1f}, p={gof_p:.3e} {sig_marker}")

# ============================================================
# 11. VERDICT
# ============================================================
print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

# Pass criteria: V > 0.15 and p < 0.01
# Fail criteria: extension independent of B section (operational per C917-C918)

# Count significant per-extension tests
n_sig = sum(1 for v in per_ext_results.values() if v['p_gof'] < 0.01)
n_tested = len(per_ext_results)
sig_fraction = n_sig / n_tested if n_tested > 0 else 0.0

if cramers_v > 0.15 and p_chi2 < 0.01:
    verdict = "PASS"
    verdict_detail = (
        f"Extension type predicts B-section distribution of PP bases "
        f"(V={cramers_v:.4f} > 0.15, permutation p={p_chi2:.4f} < 0.01). "
        f"{n_sig}/{n_tested} extensions individually significant. "
        f"Extensions carry section-specific material routing information."
    )
elif cramers_v < 0.10 or p_chi2 > 0.05:
    verdict = "FAIL"
    if p_chi2 < 0.01 and cramers_v < 0.10:
        verdict_detail = (
            f"Statistically detectable but negligible effect "
            f"(V={cramers_v:.4f} << 0.15 threshold, p={p_chi2:.4f}). "
            f"Cross-base Jaccard={overall_consistency:.3f} confirms low section "
            f"consistency. Extensions carry minimal section-routing information; "
            f"operational parameterization per C917-C918 dominates."
        )
    else:
        verdict_detail = (
            f"Extension type does NOT predict B-section distribution "
            f"(V={cramers_v:.4f}, p={p_chi2:.4f}). Extensions are "
            f"B-section-independent, consistent with operational parameterization "
            f"per C917-C918. Same extension + different base -> different sections."
        )
else:
    # Intermediate
    if overall_consistency > 0.6:
        verdict = "PARTIAL_PASS"
        verdict_detail = (
            f"Moderate effect (V={cramers_v:.4f}, p={p_chi2:.4f}). "
            f"Cross-base consistency is high (mean Jaccard={overall_consistency:.3f}), "
            f"suggesting extensions partially encode section routing. "
            f"{n_sig}/{n_tested} extensions individually significant."
        )
    else:
        verdict = "FAIL"
        verdict_detail = (
            f"Weak effect (V={cramers_v:.4f}, p={p_chi2:.4f}). "
            f"Cross-base consistency is low (mean Jaccard={overall_consistency:.3f}). "
            f"Extension-section relationship is weak, consistent with "
            f"operational parameterization per C917-C918."
        )

print(f"\n  VERDICT: {verdict}")
print(f"  {verdict_detail}")
print(f"\n  Key metrics:")
print(f"    Cramer's V (extension x section): {cramers_v:.4f}")
print(f"    Permutation p-value: {p_chi2:.4f}")
print(f"    Cross-base consistency (mean Jaccard): {overall_consistency:.3f}")
print(f"    Per-extension significance: {n_sig}/{n_tested} "
      f"({100*sig_fraction:.0f}%)")
print(f"    C917 h-extension ct rate: {100*h_ext_ct_rate:.1f}%")

# ============================================================
# 12. ASSEMBLE OUTPUT
# ============================================================
output = {
    "test": "ri_extension_b_outcome",
    "phase": "MATERIAL_LOCUS_SEARCH",
    "question": "For same PP base, do different RI extensions correlate with different B sections?",
    "timestamp": datetime.now().isoformat(),
    "method": {
        "description": (
            "Extract RI extensions from Currier A, map each PP base to its "
            "B-section presence, test extension x section contingency"
        ),
        "scope": "Currier A RI tokens -> Currier B section vocabulary",
        "n_ri_tokens": len(ri_records),
        "n_single_char_ri": len(single_char_ri),
        "n_eligible_extensions": len(eligible_extensions),
        "eligible_extensions": sorted(eligible_extensions),
        "n_pp_bases_in_ri": len(pp_base_b_sections),
        "n_multi_section_pp": len(multi_section_pp),
        "b_sections_tested": all_sections_in_data,
        "min_extension_count": MIN_EXT_COUNT,
        "n_permutations": n_permutations,
    },
    "primary_test": {
        "description": "Chi-square: extension type x B-section presence",
        "contingency_shape": list(contingency.shape),
        "extension_labels": row_labels,
        "section_labels": all_sections_in_data,
        "contingency_table": contingency.tolist(),
        "chi2": round(float(chi2), 2),
        "p_value": float(p_value),
        "cramers_v": round(float(cramers_v), 4),
        "dof": int(dof),
        "permutation_p_chi2": round(float(p_chi2), 4),
        "permutation_p_v": round(float(p_v), 4),
        "null_chi2_mean": round(float(null_chi2.mean()), 2),
        "null_v_mean": round(float(null_v.mean()), 4),
    },
    "cross_base_consistency": {
        "description": (
            "For same extension on different bases: Jaccard similarity of "
            "B-section membership. High = material routing, Low = operational"
        ),
        "overall_mean_jaccard": round(overall_consistency, 3),
        "per_extension": {
            ext: {
                "n_bases": v['n_bases'],
                "mean_jaccard": round(v['mean_jaccard'], 3),
                "std_jaccard": round(v['std_jaccard'], 3),
                "n_pairs": v['n_pairs'],
            }
            for ext, v in ext_consistency.items()
        },
    },
    "section_enrichment": {
        "description": "Per-extension B-section enrichment relative to baseline",
        "baseline_rates": {s: round(v, 3) for s, v in baseline_rates.items()},
        "per_extension": ext_enrichments,
    },
    "per_extension_tests": {
        "description": "Goodness-of-fit: each extension's section distribution vs baseline",
        "n_tested": n_tested,
        "n_significant_p01": n_sig,
        "significant_fraction": round(sig_fraction, 3),
        "results": per_ext_results,
    },
    "c917_validation": {
        "h_extension_ct_rate": round(h_ext_ct_rate, 3),
        "kt_extension_qo_rate": round(kt_qo_rate, 3),
        "extension_prefix_distributions": {
            ext: dict(ext_prefix_counts[ext].most_common(5))
            for ext in eligible_extensions
        },
    },
    "verdict": verdict,
    "verdict_detail": verdict_detail,
    "pass_criteria": "Cramer's V > 0.15, permutation p < 0.01",
    "fail_criteria": "Extension independent of B section - operational per C917-C918",
    "references": [
        "C913 (RI derivational morphology)",
        "C917 (extension-prefix operational alignment)",
        "C918 (Currier A operational configuration layer)",
    ],
}

# ============================================================
# 13. WRITE OUTPUT
# ============================================================
output_path = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/results/ri_extension_b_outcome.json')
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nOutput written to {output_path}")
print("Done.")
