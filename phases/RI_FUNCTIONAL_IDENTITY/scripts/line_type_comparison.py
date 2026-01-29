"""
RI_FUNCTIONAL_IDENTITY - Line Type Comparison

Compares PP-pure lines (ri_count==0) vs RI-bearing lines (ri_count>0)
across structural dimensions to test the hypothesis:
  - PP-pure lines = "toolbox" (shared vocabulary definition)
  - RI-bearing lines = "product entries" (identifier + material references)

Tests:
  T1: Token count distribution (do RI-bearing lines have more tokens?)
  T2: PP density (fraction of tokens that are PP)
  T3: INFRA content (do RI-bearing lines have more INFRA?)
  T4: PP MIDDLE overlap (do both line types share the same PP vocabulary?)
  T5: PP MIDDLE exclusivity (are some PP MIDDLEs exclusive to one type?)
  T6: Positional properties (where do line types appear within folios?)
  T7: PP diversity per line (type/token ratio)
  T8: RI-bearing line PP composition (what PP accompanies RI?)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats as scipy_stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology, RecordAnalyzer

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'

print("=" * 70)
print("RI_FUNCTIONAL_IDENTITY - PP-pure vs RI-bearing Line Comparison")
print("=" * 70)

# -- Load data --
tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

folios = analyzer.get_folios()
print(f"A folios: {len(folios)}")

# -- Pre-compute ALL records, classified --
folio_records = {}  # folio -> list of RecordAnalysis
all_records = []
for fol in folios:
    records = analyzer.analyze_folio(fol)
    folio_records[fol] = records
    all_records.extend(records)

print(f"Total A records: {len(all_records)}")

# -- Classify lines into PP-pure vs RI-bearing --
pp_pure_lines = []    # ri_count == 0
ri_bearing_lines = [] # ri_count > 0

for rec in all_records:
    if rec.ri_count > 0:
        ri_bearing_lines.append(rec)
    else:
        pp_pure_lines.append(rec)

print(f"PP-pure lines: {len(pp_pure_lines)} ({100*len(pp_pure_lines)/len(all_records):.1f}%)")
print(f"RI-bearing lines: {len(ri_bearing_lines)} ({100*len(ri_bearing_lines)/len(all_records):.1f}%)")
print()

# -- Pre-compute per-line metrics (O(n) pass, then O(1) lookups) --

# Per-line: token count, PP count, RI count, INFRA count, PP middles set
def line_metrics(rec):
    """Extract all metrics from a record in a single pass."""
    n_tok = len(rec.tokens)
    n_pp = rec.pp_count
    n_ri = rec.ri_count
    n_infra = rec.infra_count
    pp_middles = set()
    pp_prefixes = set()
    pp_suffixes = set()
    ri_middles = set()
    for t in rec.tokens:
        if t.is_pp and t.middle:
            pp_middles.add(t.middle)
            if t.prefix:
                pp_prefixes.add(t.prefix)
            if t.suffix:
                pp_suffixes.add(t.suffix)
        if t.is_ri and t.middle:
            ri_middles.add(t.middle)
    pp_density = n_pp / n_tok if n_tok > 0 else 0.0
    pp_diversity = len(pp_middles) / n_pp if n_pp > 0 else 0.0
    return {
        'n_tok': n_tok,
        'n_pp': n_pp,
        'n_ri': n_ri,
        'n_infra': n_infra,
        'pp_density': pp_density,
        'pp_diversity': pp_diversity,
        'pp_middles': pp_middles,
        'pp_prefixes': pp_prefixes,
        'pp_suffixes': pp_suffixes,
        'ri_middles': ri_middles,
    }

# Pre-compute all line metrics in one pass
pp_pure_metrics = [line_metrics(rec) for rec in pp_pure_lines]
ri_bearing_metrics = [line_metrics(rec) for rec in ri_bearing_lines]

# Pre-compute folio -> line positions for positional test
folio_line_positions = {}  # folio -> list of (line_index, is_ri_bearing)
for fol in folios:
    recs = folio_records[fol]
    n = len(recs)
    positions = []
    for i, rec in enumerate(recs):
        rel_pos = i / (n - 1) if n > 1 else 0.5
        positions.append((rel_pos, rec.ri_count > 0))
    folio_line_positions[fol] = positions

results = {
    'metadata': {
        'phase': 'RI_FUNCTIONAL_IDENTITY',
        'script': 'line_type_comparison.py',
        'tests': 'T1-T8 (PP-pure vs RI-bearing comparison)',
        'n_folios': len(folios),
        'n_records': len(all_records),
        'n_pp_pure': len(pp_pure_lines),
        'n_ri_bearing': len(ri_bearing_lines),
        'hypothesis': 'PP-pure = toolbox, RI-bearing = product entries',
    },
}

# ============================================================
# T1: Token Count Distribution
# ============================================================
print("-" * 60)
print("T1: Token Count Distribution")
print("-" * 60)

pp_tok_counts = np.array([m['n_tok'] for m in pp_pure_metrics])
ri_tok_counts = np.array([m['n_tok'] for m in ri_bearing_metrics])

pp_mean = float(np.mean(pp_tok_counts))
ri_mean = float(np.mean(ri_tok_counts))
pp_median = float(np.median(pp_tok_counts))
ri_median = float(np.median(ri_tok_counts))

u_stat, u_p = scipy_stats.mannwhitneyu(pp_tok_counts, ri_tok_counts, alternative='two-sided')

print(f"  PP-pure:    mean={pp_mean:.2f}, median={pp_median:.1f}")
print(f"  RI-bearing: mean={ri_mean:.2f}, median={ri_median:.1f}")
print(f"  Mann-Whitney U p={u_p:.4e}")
print(f"  Ratio (RI/PP): {ri_mean/pp_mean:.3f}")

results['T1_token_count'] = {
    'pp_pure_mean': round(pp_mean, 2),
    'pp_pure_median': round(pp_median, 1),
    'ri_bearing_mean': round(ri_mean, 2),
    'ri_bearing_median': round(ri_median, 1),
    'ratio_ri_over_pp': round(ri_mean / pp_mean, 3),
    'mann_whitney_p': float(u_p),
}

# ============================================================
# T2: PP Density (fraction of tokens that are PP)
# ============================================================
print()
print("-" * 60)
print("T2: PP Density (PP tokens / total tokens)")
print("-" * 60)

pp_density_pure = np.array([m['pp_density'] for m in pp_pure_metrics])
pp_density_ri = np.array([m['pp_density'] for m in ri_bearing_metrics])

pp_d_mean = float(np.mean(pp_density_pure))
ri_d_mean = float(np.mean(pp_density_ri))

u2, p2 = scipy_stats.mannwhitneyu(pp_density_pure, pp_density_ri, alternative='two-sided')

print(f"  PP-pure lines:    PP density mean={pp_d_mean:.4f}")
print(f"  RI-bearing lines: PP density mean={ri_d_mean:.4f}")
print(f"  Mann-Whitney U p={p2:.4e}")
print(f"  Ratio (pure/RI): {pp_d_mean/ri_d_mean:.3f}" if ri_d_mean > 0 else "  RI density=0")

# Also compute: what fraction of RI-bearing tokens are PP vs RI?
ri_line_pp_counts = np.array([m['n_pp'] for m in ri_bearing_metrics])
ri_line_ri_counts = np.array([m['n_ri'] for m in ri_bearing_metrics])
ri_line_infra_counts = np.array([m['n_infra'] for m in ri_bearing_metrics])

ri_pp_frac = float(np.sum(ri_line_pp_counts)) / float(np.sum(ri_tok_counts)) if np.sum(ri_tok_counts) > 0 else 0
ri_ri_frac = float(np.sum(ri_line_ri_counts)) / float(np.sum(ri_tok_counts)) if np.sum(ri_tok_counts) > 0 else 0
ri_infra_frac = float(np.sum(ri_line_infra_counts)) / float(np.sum(ri_tok_counts)) if np.sum(ri_tok_counts) > 0 else 0

print(f"  RI-bearing token composition: PP={ri_pp_frac:.3f}, RI={ri_ri_frac:.3f}, INFRA={ri_infra_frac:.3f}")

results['T2_pp_density'] = {
    'pp_pure_density_mean': round(pp_d_mean, 4),
    'ri_bearing_density_mean': round(ri_d_mean, 4),
    'ratio_pure_over_ri': round(pp_d_mean / ri_d_mean, 3) if ri_d_mean > 0 else None,
    'mann_whitney_p': float(p2),
    'ri_bearing_composition': {
        'pp_fraction': round(ri_pp_frac, 3),
        'ri_fraction': round(ri_ri_frac, 3),
        'infra_fraction': round(ri_infra_frac, 3),
    },
}

# ============================================================
# T3: INFRA Content Comparison
# ============================================================
print()
print("-" * 60)
print("T3: INFRA Content")
print("-" * 60)

pp_infra = np.array([m['n_infra'] for m in pp_pure_metrics])
ri_infra = np.array([m['n_infra'] for m in ri_bearing_metrics])

pp_infra_mean = float(np.mean(pp_infra))
ri_infra_mean = float(np.mean(ri_infra))

# Fraction of lines with any INFRA
pp_has_infra = float(np.mean(pp_infra > 0))
ri_has_infra = float(np.mean(ri_infra > 0))

u3, p3 = scipy_stats.mannwhitneyu(pp_infra, ri_infra, alternative='two-sided')

print(f"  PP-pure:    mean INFRA/line={pp_infra_mean:.3f}, has-INFRA={pp_has_infra:.3f}")
print(f"  RI-bearing: mean INFRA/line={ri_infra_mean:.3f}, has-INFRA={ri_has_infra:.3f}")
print(f"  Mann-Whitney U p={p3:.4e}")

results['T3_infra_content'] = {
    'pp_pure_infra_mean': round(pp_infra_mean, 3),
    'ri_bearing_infra_mean': round(ri_infra_mean, 3),
    'pp_pure_has_infra_frac': round(pp_has_infra, 3),
    'ri_bearing_has_infra_frac': round(ri_has_infra, 3),
    'mann_whitney_p': float(p3),
}

# ============================================================
# T4: PP MIDDLE Overlap (do both types share the same PP vocabulary?)
# ============================================================
print()
print("-" * 60)
print("T4: PP MIDDLE Overlap Between Line Types")
print("-" * 60)

# Global PP MIDDLE sets by line type
pp_pure_all_middles = set()
ri_bearing_all_middles = set()

for m in pp_pure_metrics:
    pp_pure_all_middles |= m['pp_middles']

for m in ri_bearing_metrics:
    ri_bearing_all_middles |= m['pp_middles']

overlap = pp_pure_all_middles & ri_bearing_all_middles
only_pure = pp_pure_all_middles - ri_bearing_all_middles
only_ri = ri_bearing_all_middles - pp_pure_all_middles
union = pp_pure_all_middles | ri_bearing_all_middles

jaccard = len(overlap) / len(union) if len(union) > 0 else 0
overlap_frac_of_pure = len(overlap) / len(pp_pure_all_middles) if len(pp_pure_all_middles) > 0 else 0
overlap_frac_of_ri = len(overlap) / len(ri_bearing_all_middles) if len(ri_bearing_all_middles) > 0 else 0

print(f"  PP-pure PP MIDDLEs:    {len(pp_pure_all_middles)}")
print(f"  RI-bearing PP MIDDLEs: {len(ri_bearing_all_middles)}")
print(f"  Overlap:               {len(overlap)}")
print(f"  Only in PP-pure:       {len(only_pure)}")
print(f"  Only in RI-bearing:    {len(only_ri)}")
print(f"  Jaccard:               {jaccard:.4f}")
print(f"  Overlap as %% of PP-pure:    {overlap_frac_of_pure:.4f}")
print(f"  Overlap as %% of RI-bearing: {overlap_frac_of_ri:.4f}")

# Per-folio analysis: within each folio, Jaccard of PP MIDDLEs from the two types
folio_jaccards = []
for fol in folios:
    pure_mids = set()
    ri_mids = set()
    for rec in folio_records[fol]:
        pp_mids_this = set(t.middle for t in rec.tokens if t.is_pp and t.middle)
        if rec.ri_count > 0:
            ri_mids |= pp_mids_this
        else:
            pure_mids |= pp_mids_this
    if pure_mids and ri_mids:
        j = len(pure_mids & ri_mids) / len(pure_mids | ri_mids)
        folio_jaccards.append(j)

mean_folio_jaccard = float(np.mean(folio_jaccards)) if folio_jaccards else 0
print(f"  Per-folio PP MIDDLE Jaccard (pure vs RI): mean={mean_folio_jaccard:.4f} (n={len(folio_jaccards)})")

results['T4_pp_middle_overlap'] = {
    'pp_pure_types': len(pp_pure_all_middles),
    'ri_bearing_types': len(ri_bearing_all_middles),
    'overlap': len(overlap),
    'only_pp_pure': len(only_pure),
    'only_ri_bearing': len(only_ri),
    'jaccard_global': round(jaccard, 4),
    'overlap_frac_of_pure': round(overlap_frac_of_pure, 4),
    'overlap_frac_of_ri': round(overlap_frac_of_ri, 4),
    'per_folio_jaccard_mean': round(mean_folio_jaccard, 4),
    'per_folio_n': len(folio_jaccards),
}

# ============================================================
# T5: PP MIDDLE Exclusivity (frequency-weighted)
# ============================================================
print()
print("-" * 60)
print("T5: PP MIDDLE Exclusivity (frequency-weighted)")
print("-" * 60)

# Count how many times each PP MIDDLE appears in each line type
pp_mid_count_pure = Counter()
pp_mid_count_ri = Counter()

for rec in pp_pure_lines:
    for t in rec.tokens:
        if t.is_pp and t.middle:
            pp_mid_count_pure[t.middle] += 1

for rec in ri_bearing_lines:
    for t in rec.tokens:
        if t.is_pp and t.middle:
            pp_mid_count_ri[t.middle] += 1

all_pp_middles = set(pp_mid_count_pure.keys()) | set(pp_mid_count_ri.keys())

# For each PP MIDDLE, compute bias = count_in_pure / (count_in_pure + count_in_ri)
# Bias near 1.0 = exclusive to PP-pure; near 0.0 = exclusive to RI-bearing; near 0.63 = proportional
# (0.63 because PP-pure lines are 63% of lines)
expected_bias = len(pp_pure_lines) / len(all_records)

biases = {}
for mid in all_pp_middles:
    cp = pp_mid_count_pure.get(mid, 0)
    cr = pp_mid_count_ri.get(mid, 0)
    total = cp + cr
    if total > 0:
        biases[mid] = cp / total

bias_values = np.array(list(biases.values()))
strongly_pure = sum(1 for b in bias_values if b > 0.9)
strongly_ri = sum(1 for b in bias_values if b < 0.1)
balanced = sum(1 for b in bias_values if 0.3 < b < 0.8)

print(f"  Total PP MIDDLE types: {len(all_pp_middles)}")
print(f"  Expected proportional bias: {expected_bias:.3f}")
print(f"  Observed mean bias: {float(np.mean(bias_values)):.3f}")
print(f"  Observed median bias: {float(np.median(bias_values)):.3f}")
print(f"  Strongly PP-pure (>0.9): {strongly_pure}")
print(f"  Strongly RI-bearing (<0.1): {strongly_ri}")
print(f"  Balanced (0.3-0.8): {balanced}")

# Chi-squared: are PP MIDDLEs distributed proportionally across line types?
# For top-50 most frequent PP MIDDLEs
top_pp_middles = sorted(all_pp_middles, key=lambda m: pp_mid_count_pure.get(m, 0) + pp_mid_count_ri.get(m, 0), reverse=True)[:50]

observed_pure = np.array([pp_mid_count_pure.get(m, 0) for m in top_pp_middles])
observed_ri = np.array([pp_mid_count_ri.get(m, 0) for m in top_pp_middles])
totals = observed_pure + observed_ri

expected_pure = totals * expected_bias
expected_ri = totals * (1 - expected_bias)

# Chi-squared across all top-50
chi2_stat = float(np.sum((observed_pure - expected_pure)**2 / np.where(expected_pure > 0, expected_pure, 1) +
                         (observed_ri - expected_ri)**2 / np.where(expected_ri > 0, expected_ri, 1)))
chi2_df = len(top_pp_middles) - 1
chi2_p = float(scipy_stats.chi2.sf(chi2_stat, chi2_df))

print(f"  Chi-squared (top-50 MIDDLEs vs proportional): chi2={chi2_stat:.2f}, df={chi2_df}, p={chi2_p:.4e}")

results['T5_pp_middle_exclusivity'] = {
    'total_pp_middle_types': len(all_pp_middles),
    'expected_proportional_bias': round(expected_bias, 3),
    'observed_mean_bias': round(float(np.mean(bias_values)), 3),
    'observed_median_bias': round(float(np.median(bias_values)), 3),
    'strongly_pp_pure_gt09': int(strongly_pure),
    'strongly_ri_bearing_lt01': int(strongly_ri),
    'balanced_03_08': int(balanced),
    'chi2_top50': round(chi2_stat, 2),
    'chi2_df': chi2_df,
    'chi2_p': float(chi2_p),
}

# ============================================================
# T6: Positional Properties (where in the folio do line types appear?)
# ============================================================
print()
print("-" * 60)
print("T6: Positional Properties Within Folios")
print("-" * 60)

pure_positions = []
ri_positions = []

for fol in folios:
    for rel_pos, is_ri in folio_line_positions[fol]:
        if is_ri:
            ri_positions.append(rel_pos)
        else:
            pure_positions.append(rel_pos)

pure_positions = np.array(pure_positions)
ri_positions = np.array(ri_positions)

pp_pos_mean = float(np.mean(pure_positions))
ri_pos_mean = float(np.mean(ri_positions))

ks_stat, ks_p = scipy_stats.ks_2samp(pure_positions, ri_positions)

print(f"  PP-pure mean relative position: {pp_pos_mean:.4f}")
print(f"  RI-bearing mean relative position: {ri_pos_mean:.4f}")
print(f"  KS test: D={ks_stat:.4f}, p={ks_p:.4e}")

# Are RI-bearing lines more common at start/end of folios?
first_third = sum(1 for p in ri_positions if p < 0.333) / len(ri_positions)
middle_third = sum(1 for p in ri_positions if 0.333 <= p < 0.667) / len(ri_positions)
last_third = sum(1 for p in ri_positions if p >= 0.667) / len(ri_positions)

print(f"  RI-bearing positional thirds: first={first_third:.3f}, middle={middle_third:.3f}, last={last_third:.3f}")
print(f"  (Uniform expectation: 0.333 each)")

# First-line and last-line statistics
first_line_ri = 0
last_line_ri = 0
total_folios_with_lines = 0
for fol in folios:
    recs = folio_records[fol]
    if len(recs) > 0:
        total_folios_with_lines += 1
        if recs[0].ri_count > 0:
            first_line_ri += 1
        if recs[-1].ri_count > 0:
            last_line_ri += 1

print(f"  First line is RI-bearing: {first_line_ri}/{total_folios_with_lines} ({100*first_line_ri/total_folios_with_lines:.1f}%)")
print(f"  Last line is RI-bearing:  {last_line_ri}/{total_folios_with_lines} ({100*last_line_ri/total_folios_with_lines:.1f}%)")

results['T6_positional'] = {
    'pp_pure_mean_position': round(pp_pos_mean, 4),
    'ri_bearing_mean_position': round(ri_pos_mean, 4),
    'ks_D': round(ks_stat, 4),
    'ks_p': float(ks_p),
    'ri_bearing_thirds': {
        'first': round(first_third, 3),
        'middle': round(middle_third, 3),
        'last': round(last_third, 3),
    },
    'first_line_ri_frac': round(first_line_ri / total_folios_with_lines, 3),
    'last_line_ri_frac': round(last_line_ri / total_folios_with_lines, 3),
}

# ============================================================
# T7: PP Diversity Per Line (type/token ratio)
# ============================================================
print()
print("-" * 60)
print("T7: PP Diversity Per Line (unique MIDDLEs / PP token count)")
print("-" * 60)

pp_div_pure = np.array([m['pp_diversity'] for m in pp_pure_metrics if m['n_pp'] > 0])
pp_div_ri = np.array([m['pp_diversity'] for m in ri_bearing_metrics if m['n_pp'] > 0])

if len(pp_div_pure) > 0 and len(pp_div_ri) > 0:
    div_pure_mean = float(np.mean(pp_div_pure))
    div_ri_mean = float(np.mean(pp_div_ri))
    u7, p7 = scipy_stats.mannwhitneyu(pp_div_pure, pp_div_ri, alternative='two-sided')
    print(f"  PP-pure mean diversity:    {div_pure_mean:.4f} (n={len(pp_div_pure)})")
    print(f"  RI-bearing mean diversity: {div_ri_mean:.4f} (n={len(pp_div_ri)})")
    print(f"  Mann-Whitney U p={p7:.4e}")
else:
    div_pure_mean = 0
    div_ri_mean = 0
    p7 = 1.0
    print("  Insufficient data")

# Also: PP token count per line (not diversity, raw count)
pp_count_pure = np.array([m['n_pp'] for m in pp_pure_metrics])
pp_count_ri = np.array([m['n_pp'] for m in ri_bearing_metrics])

pp_ct_pure_mean = float(np.mean(pp_count_pure))
pp_ct_ri_mean = float(np.mean(pp_count_ri))
u7b, p7b = scipy_stats.mannwhitneyu(pp_count_pure, pp_count_ri, alternative='two-sided')

print(f"  PP tokens/line (pure):  mean={pp_ct_pure_mean:.2f}")
print(f"  PP tokens/line (RI):    mean={pp_ct_ri_mean:.2f}")
print(f"  Mann-Whitney U p={p7b:.4e}")

results['T7_pp_diversity'] = {
    'pp_pure_diversity_mean': round(div_pure_mean, 4),
    'ri_bearing_diversity_mean': round(div_ri_mean, 4),
    'diversity_mann_whitney_p': float(p7),
    'pp_count_pure_mean': round(pp_ct_pure_mean, 2),
    'pp_count_ri_mean': round(pp_ct_ri_mean, 2),
    'pp_count_mann_whitney_p': float(p7b),
}

# ============================================================
# T8: RI-bearing Line PP Composition
# What PP MIDDLEs accompany RI tokens? Are they the same as PP-pure lines
# or a specialized subset?
# ============================================================
print()
print("-" * 60)
print("T8: RI-bearing Line PP Composition Analysis")
print("-" * 60)

# For each folio: what fraction of the folio's PP MIDDLE pool
# appears on PP-pure lines vs RI-bearing lines?
folio_coverage_pure = []   # fraction of folio PP pool covered by PP-pure lines
folio_coverage_ri = []     # fraction of folio PP pool covered by RI-bearing lines

for fol in folios:
    pure_mids = set()
    ri_pp_mids = set()
    all_pp_mids = set()
    for rec in folio_records[fol]:
        pp_mids_this = set(t.middle for t in rec.tokens if t.is_pp and t.middle)
        all_pp_mids |= pp_mids_this
        if rec.ri_count > 0:
            ri_pp_mids |= pp_mids_this
        else:
            pure_mids |= pp_mids_this
    if all_pp_mids:
        folio_coverage_pure.append(len(pure_mids) / len(all_pp_mids))
        folio_coverage_ri.append(len(ri_pp_mids) / len(all_pp_mids))

cov_pure_mean = float(np.mean(folio_coverage_pure))
cov_ri_mean = float(np.mean(folio_coverage_ri))

print(f"  Folio PP pool coverage by PP-pure lines:    {cov_pure_mean:.4f}")
print(f"  Folio PP pool coverage by RI-bearing lines: {cov_ri_mean:.4f}")

# How many PP MIDDLEs per line on RI-bearing lines? (already computed above)
# What is the PP MIDDLE repertoire size on RI-bearing lines vs PP-pure lines?
ri_pp_mid_per_line = np.array([len(m['pp_middles']) for m in ri_bearing_metrics])
pp_pp_mid_per_line = np.array([len(m['pp_middles']) for m in pp_pure_metrics])

ri_pp_mid_mean = float(np.mean(ri_pp_mid_per_line))
pp_pp_mid_mean = float(np.mean(pp_pp_mid_per_line))
u8, p8 = scipy_stats.mannwhitneyu(pp_pp_mid_per_line, ri_pp_mid_per_line, alternative='two-sided')

print(f"  Unique PP MIDDLEs/line (PP-pure):    {pp_pp_mid_mean:.2f}")
print(f"  Unique PP MIDDLEs/line (RI-bearing): {ri_pp_mid_mean:.2f}")
print(f"  Mann-Whitney U p={p8:.4e}")

# Do RI-bearing lines have PP MIDDLEs that PP-pure lines don't (within same folio)?
folio_ri_exclusive = []  # per folio: count of PP MIDDLEs on RI-bearing lines not on PP-pure lines
for fol in folios:
    pure_mids = set()
    ri_pp_mids = set()
    for rec in folio_records[fol]:
        pp_mids_this = set(t.middle for t in rec.tokens if t.is_pp and t.middle)
        if rec.ri_count > 0:
            ri_pp_mids |= pp_mids_this
        else:
            pure_mids |= pp_mids_this
    if ri_pp_mids:
        exclusive = ri_pp_mids - pure_mids
        folio_ri_exclusive.append(len(exclusive) / len(ri_pp_mids))

ri_excl_mean = float(np.mean(folio_ri_exclusive)) if folio_ri_exclusive else 0

print(f"  Mean fraction of RI-line PP MIDDLEs NOT on PP-pure lines (per folio): {ri_excl_mean:.4f}")

results['T8_ri_pp_composition'] = {
    'folio_coverage_by_pure_mean': round(cov_pure_mean, 4),
    'folio_coverage_by_ri_mean': round(cov_ri_mean, 4),
    'unique_pp_middles_per_line_pure': round(pp_pp_mid_mean, 2),
    'unique_pp_middles_per_line_ri': round(ri_pp_mid_mean, 2),
    'pp_middles_per_line_mann_whitney_p': float(p8),
    'ri_exclusive_pp_middles_frac': round(ri_excl_mean, 4),
}

# ============================================================
# Summary
# ============================================================
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

summary_lines = [
    f"PP-pure lines: {len(pp_pure_lines)} ({100*len(pp_pure_lines)/len(all_records):.1f}%)",
    f"RI-bearing lines: {len(ri_bearing_lines)} ({100*len(ri_bearing_lines)/len(all_records):.1f}%)",
    "",
    "T1 Token count:  RI-bearing {:.2f} vs PP-pure {:.2f} (ratio {:.3f})".format(
        ri_mean, pp_mean, ri_mean / pp_mean),
    "T2 PP density:   PP-pure {:.4f} vs RI-bearing {:.4f}".format(pp_d_mean, ri_d_mean),
    "   RI-bearing composition: PP={:.1f}% RI={:.1f}% INFRA={:.1f}%".format(
        ri_pp_frac*100, ri_ri_frac*100, ri_infra_frac*100),
    "T3 INFRA: PP-pure {:.3f}/line vs RI-bearing {:.3f}/line".format(pp_infra_mean, ri_infra_mean),
    "T4 PP MIDDLE overlap: Jaccard={:.4f} (global), {:.4f} (per-folio mean)".format(
        jaccard, mean_folio_jaccard),
    "   Only in PP-pure: {}, Only in RI-bearing: {}, Overlap: {}".format(
        len(only_pure), len(only_ri), len(overlap)),
    "T5 Exclusivity: mean bias={:.3f} (expected {:.3f}), chi2 p={:.4e}".format(
        float(np.mean(bias_values)), expected_bias, chi2_p),
    "T6 Position: PP-pure mean={:.4f}, RI-bearing mean={:.4f}, KS p={:.4e}".format(
        pp_pos_mean, ri_pos_mean, ks_p),
    "T7 PP diversity: pure={:.4f} vs RI={:.4f}; PP count: pure={:.2f} vs RI={:.2f}".format(
        div_pure_mean, div_ri_mean, pp_ct_pure_mean, pp_ct_ri_mean),
    "T8 Coverage: pure covers {:.1f}% of folio pool, RI covers {:.1f}%".format(
        cov_pure_mean*100, cov_ri_mean*100),
    "   RI-exclusive PP MIDDLEs (not on PP-pure within folio): {:.1f}%".format(ri_excl_mean*100),
]

for line in summary_lines:
    print(f"  {line}")

# Key conclusion
print()
pp_same_vocab = jaccard > 0.7 and mean_folio_jaccard > 0.5
if pp_same_vocab:
    print("  CONCLUSION: PP-pure and RI-bearing lines share SAME PP vocabulary.")
    print("  -> Both line types contribute to the SAME folio PP pool.")
    print("  -> The distinction is RI presence, not PP content.")
    conclusion = "SAME_VOCABULARY"
elif jaccard < 0.3:
    print("  CONCLUSION: PP-pure and RI-bearing lines have DIFFERENT PP vocabularies.")
    print("  -> Supports toolbox/product-entry distinction.")
    conclusion = "DIFFERENT_VOCABULARY"
else:
    print("  CONCLUSION: PP vocabulary overlap is PARTIAL.")
    print("  -> Some shared, some specialized vocabulary per line type.")
    conclusion = "PARTIAL_OVERLAP"

results['summary'] = {
    'conclusion': conclusion,
    'key_numbers': {
        'pp_pure_fraction': round(len(pp_pure_lines) / len(all_records), 3),
        'ri_bearing_fraction': round(len(ri_bearing_lines) / len(all_records), 3),
        'global_pp_jaccard': round(jaccard, 4),
        'per_folio_pp_jaccard': round(mean_folio_jaccard, 4),
        'ri_bearing_pp_fraction': round(ri_pp_frac, 3),
        'ri_bearing_ri_fraction': round(ri_ri_frac, 3),
        'token_count_ratio': round(ri_mean / pp_mean, 3),
    },
}

# -- Save results --
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
output_path = RESULTS_DIR / 'line_type_comparison.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print()
print(f"Results saved to {output_path}")
