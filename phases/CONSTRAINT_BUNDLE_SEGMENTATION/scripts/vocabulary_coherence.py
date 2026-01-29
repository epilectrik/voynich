"""
CONSTRAINT_BUNDLE_SEGMENTATION - Script 2: Vocabulary Coherence
Tests T2.1-T2.4 (C699-C702)

Gate: 3/4 pass to proceed to Phase 3.

Tests:
  T2.1: Within-Bundle PP Coherence > Between-Bundle (C699)
  T2.2: Bundle PP Count > Random Groups (C700)
  T2.3: Bundle PP Diversity Structured (C701)
  T2.4: Vocabulary Discontinuity at Boundaries (C702)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as scipy_stats
from itertools import combinations

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from bundle_segmentation import segment_all_folios

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'

print("=" * 70)
print("CONSTRAINT_BUNDLE_SEGMENTATION - Script 2: Vocabulary Coherence")
print("=" * 70)

# ── Segment ──
bundles, ri_lines, metadata, shared = segment_all_folios(verbose=True)

morph = shared['morph']
analyzer = shared['analyzer']
folio_stats = metadata['folio_stats']
folios = sorted(folio_stats.keys())

results = {
    'metadata': {
        'phase': 'CONSTRAINT_BUNDLE_SEGMENTATION',
        'script': 'vocabulary_coherence.py',
        'tests': 'T2.1-T2.4 (C699-C702)',
        'n_bundles': len(bundles),
    },
}

pass_count = 0


def jaccard(set_a, set_b):
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def get_line_pp_middles(record):
    """Get set of PP MIDDLEs from a record."""
    middles = set()
    for t in record.tokens:
        if t.is_pp and t.middle:
            middles.add(t.middle)
    return middles


# ── Pre-compute per-line PP MIDDLE sets ──
# Build folio -> [(record, pp_middles)] for all lines
folio_line_data = defaultdict(list)
for fol in folios:
    records = analyzer.analyze_folio(fol)
    for rec in records:
        pp_mids = get_line_pp_middles(rec)
        folio_line_data[fol].append((rec, pp_mids))

# Build folio -> [bundle_indices] for bundles
folio_bundles = defaultdict(list)
for i, b in enumerate(bundles):
    folio_bundles[b.folio].append(i)


# ════════════════════════════════════════════════════════════════
# T2.1: Within-Bundle PP Coherence > Between-Bundle (C699)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T2.1: WITHIN-BUNDLE PP COHERENCE > BETWEEN-BUNDLE (C699)")
print("=" * 70)

within_jaccards = []
between_jaccards = []

for fol in folios:
    fol_bundle_ids = folio_bundles[fol]
    if len(fol_bundle_ids) < 2:
        continue

    # Within-bundle: pairs of lines in the same bundle
    for bid in fol_bundle_ids:
        b = bundles[bid]
        if b.size < 2:
            continue
        for i in range(len(b.lines)):
            for j in range(i + 1, len(b.lines)):
                mid_i = get_line_pp_middles(b.lines[i])
                mid_j = get_line_pp_middles(b.lines[j])
                if mid_i and mid_j:
                    within_jaccards.append(jaccard(mid_i, mid_j))

    # Between-bundle: pairs of lines from different bundles (same folio)
    for idx_a in range(len(fol_bundle_ids)):
        for idx_b in range(idx_a + 1, len(fol_bundle_ids)):
            b_a = bundles[fol_bundle_ids[idx_a]]
            b_b = bundles[fol_bundle_ids[idx_b]]
            # Sample line pairs (cap to avoid explosion)
            pairs = 0
            for line_a in b_a.lines:
                for line_b in b_b.lines:
                    mid_a = get_line_pp_middles(line_a)
                    mid_b = get_line_pp_middles(line_b)
                    if mid_a and mid_b:
                        between_jaccards.append(jaccard(mid_a, mid_b))
                        pairs += 1
                    if pairs >= 20:
                        break
                if pairs >= 20:
                    break

within_arr = np.array(within_jaccards)
between_arr = np.array(between_jaccards)

within_mean = float(np.mean(within_arr)) if len(within_arr) > 0 else 0
between_mean = float(np.mean(between_arr)) if len(between_arr) > 0 else 0
ratio_21 = within_mean / between_mean if between_mean > 0 else float('inf')

if len(within_arr) >= 5 and len(between_arr) >= 5:
    u_stat, u_p = scipy_stats.mannwhitneyu(within_arr, between_arr, alternative='greater')
else:
    u_stat, u_p = 0, 1.0

t21_pass = ratio_21 > 1.3 and u_p < 0.001

print(f"\n  Within-bundle pairs: {len(within_arr)}")
print(f"  Between-bundle pairs: {len(between_arr)}")
print(f"  Within mean Jaccard: {within_mean:.4f}")
print(f"  Between mean Jaccard: {between_mean:.4f}")
print(f"  Ratio: {ratio_21:.2f}x")
print(f"  Mann-Whitney U: {u_stat:.1f}, p: {u_p:.2e}")
print(f"\n  PASS (ratio > 1.3x AND p < 0.001): {t21_pass}")

if t21_pass:
    pass_count += 1

results['T2_1_within_vs_between'] = {
    'constraint': 'C699',
    'within_pairs': len(within_arr),
    'between_pairs': len(between_arr),
    'within_mean_jaccard': round(within_mean, 5),
    'between_mean_jaccard': round(between_mean, 5),
    'ratio': round(ratio_21, 3),
    'mann_whitney_u': float(u_stat),
    'mann_whitney_p': float(u_p),
    'pass': t21_pass,
}


# ════════════════════════════════════════════════════════════════
# T2.2: Bundle PP Count > Random Groups (C700)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T2.2: BUNDLE PP COUNT > RANDOM GROUPS (C700)")
print("=" * 70)

# For each bundle of size k: count distinct PP MIDDLEs (union)
# Null: sample k random lines from same folio, 1000 times

N_PERMS = 1000
rng = np.random.RandomState(42)

observed_pp_counts = []
null_pp_means = []
folio_pp_lines = {}  # folio -> list of pp_middle_sets for all lines

for fol in folios:
    fol_records = analyzer.analyze_folio(fol)
    folio_pp_lines[fol] = [get_line_pp_middles(rec) for rec in fol_records]

per_bundle_pvals = []
for b in bundles:
    if b.size < 2:
        continue

    obs_pp = len(b.pp_middles)
    observed_pp_counts.append(obs_pp)

    # Null: random k lines from same folio
    all_lines = folio_pp_lines[b.folio]
    if len(all_lines) < b.size:
        continue

    null_counts = []
    for _ in range(N_PERMS):
        indices = rng.choice(len(all_lines), size=b.size, replace=False)
        null_union = set()
        for idx in indices:
            null_union |= all_lines[idx]
        null_counts.append(len(null_union))

    null_arr = np.array(null_counts)
    null_pp_means.append(float(np.mean(null_arr)))

    # One-sided p: fraction of null >= observed
    p_val = np.mean(null_arr >= obs_pp)
    per_bundle_pvals.append(p_val)

obs_arr = np.array(observed_pp_counts)
null_mean_arr = np.array(null_pp_means)

obs_grand_mean = float(np.mean(obs_arr)) if len(obs_arr) > 0 else 0
null_grand_mean = float(np.mean(null_mean_arr)) if len(null_mean_arr) > 0 else 0

# Fisher's combined p
if per_bundle_pvals:
    # Clamp to avoid log(0)
    clamped = [max(p, 1e-300) for p in per_bundle_pvals]
    fisher_stat = -2 * sum(np.log(p) for p in clamped)
    fisher_df = 2 * len(clamped)
    fisher_p = scipy_stats.chi2.sf(fisher_stat, fisher_df)
else:
    fisher_p = 1.0

# Simpler test: paired comparison
if len(obs_arr) == len(null_mean_arr) and len(obs_arr) > 5:
    wilcox_stat, wilcox_p = scipy_stats.wilcoxon(obs_arr - null_mean_arr, alternative='greater')
else:
    wilcox_stat, wilcox_p = 0, 1.0

t22_pass = obs_grand_mean > null_grand_mean and fisher_p < 0.001

print(f"\n  Bundles tested (size>=2): {len(obs_arr)}")
print(f"  Observed mean PP MIDDLEs: {obs_grand_mean:.2f}")
print(f"  Null mean PP MIDDLEs: {null_grand_mean:.2f}")
print(f"  Ratio: {obs_grand_mean / null_grand_mean:.2f}x" if null_grand_mean > 0 else "  Ratio: N/A")
print(f"  Fisher combined p: {fisher_p:.2e}")
print(f"  Wilcoxon signed-rank p: {wilcox_p:.2e}")
print(f"  Per-bundle p-values: median={np.median(per_bundle_pvals):.4f}" if per_bundle_pvals else "  No p-values")
print(f"\n  PASS (observed > null, Fisher p < 0.001): {t22_pass}")

if t22_pass:
    pass_count += 1

results['T2_2_bundle_pp_vs_random'] = {
    'constraint': 'C700',
    'n_bundles_tested': len(obs_arr),
    'observed_mean_pp': round(obs_grand_mean, 3),
    'null_mean_pp': round(null_grand_mean, 3),
    'ratio': round(obs_grand_mean / null_grand_mean, 3) if null_grand_mean > 0 else None,
    'fisher_combined_p': float(fisher_p),
    'wilcoxon_p': float(wilcox_p),
    'n_permutations': N_PERMS,
    'pass': t22_pass,
}


# ════════════════════════════════════════════════════════════════
# T2.3: Bundle PP Diversity Structured (C701)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T2.3: BUNDLE PP DIVERSITY STRUCTURED (C701)")
print("=" * 70)

# PP MIDDLE diversity = unique MIDDLEs / total PP token instances per bundle
# Compare to shuffled baseline

observed_diversities = []
for b in bundles:
    if b.size < 2:
        continue
    pp_count = 0
    pp_unique = set()
    for rec in b.lines:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                pp_count += 1
                pp_unique.add(t.middle)
    if pp_count > 0:
        observed_diversities.append(len(pp_unique) / pp_count)

obs_diversity = np.array(observed_diversities)
obs_div_mean = float(np.mean(obs_diversity)) if len(obs_diversity) > 0 else 0

# Shuffled baseline: shuffle PP MIDDLEs across lines within folio, re-compute diversity
N_PERMS_DIV = 500
rng2 = np.random.RandomState(123)
shuffled_div_means = []

for perm_i in range(N_PERMS_DIV):
    perm_diversities = []

    for fol in folios:
        fol_bundle_ids = folio_bundles[fol]
        if not fol_bundle_ids:
            continue

        # Collect all PP middles per line position
        records = analyzer.analyze_folio(fol)
        all_pp_middles_flat = []
        line_pp_counts = []  # how many PP tokens per line
        for rec in records:
            pp_mids = []
            for t in rec.tokens:
                if t.is_pp and t.middle:
                    pp_mids.append(t.middle)
            all_pp_middles_flat.extend(pp_mids)
            line_pp_counts.append(len(pp_mids))

        # Shuffle
        rng2.shuffle(all_pp_middles_flat)

        # Redistribute to lines
        idx = 0
        line_pp_sets = []
        for n_pp in line_pp_counts:
            line_mids = all_pp_middles_flat[idx:idx + n_pp]
            line_pp_sets.append((set(line_mids), n_pp))
            idx += n_pp

        # Re-classify lines and re-segment
        # (We keep original segmentation structure, just recompute diversity
        #  with shuffled MIDDLEs within bundles' line positions)
        for bid in fol_bundle_ids:
            b = bundles[bid]
            if b.size < 2:
                continue

            # Find line indices in folio for this bundle
            total_pp = 0
            unique_pp = set()
            for rec in b.lines:
                # Find this record's index in folio
                rec_key = (rec.folio, rec.line)
                for li, r2 in enumerate(records):
                    if r2.folio == rec.folio and r2.line == rec.line:
                        uniq, cnt = line_pp_sets[li]
                        total_pp += cnt
                        unique_pp |= uniq
                        break

            if total_pp > 0:
                perm_diversities.append(len(unique_pp) / total_pp)

    if perm_diversities:
        shuffled_div_means.append(np.mean(perm_diversities))

shuffled_div_arr = np.array(shuffled_div_means)
shuffled_div_mean = float(np.mean(shuffled_div_arr)) if len(shuffled_div_arr) > 0 else 0

# Two-sided: is observed different from shuffled?
if len(shuffled_div_arr) > 0:
    # Count how many shuffled are as extreme as observed
    p_lower = np.mean(shuffled_div_arr <= obs_div_mean)
    p_upper = np.mean(shuffled_div_arr >= obs_div_mean)
    p_div = 2 * min(p_lower, p_upper)
    p_div = min(p_div, 1.0)
else:
    p_div = 1.0

t23_pass = p_div < 0.01

print(f"\n  Bundles tested (size>=2): {len(obs_diversity)}")
print(f"  Observed mean diversity: {obs_div_mean:.4f}")
print(f"  Shuffled mean diversity: {shuffled_div_mean:.4f} (+/- {np.std(shuffled_div_arr):.4f})" if len(shuffled_div_arr) > 0 else "  No shuffled data")
print(f"  Direction: {'lower' if obs_div_mean < shuffled_div_mean else 'higher'} (observed vs shuffled)")
print(f"  p-value (two-sided): {p_div:.4e}")
print(f"\n  PASS (differs from shuffled, p < 0.01): {t23_pass}")

if t23_pass:
    pass_count += 1

results['T2_3_pp_diversity'] = {
    'constraint': 'C701',
    'n_bundles': len(obs_diversity),
    'observed_mean_diversity': round(obs_div_mean, 5),
    'shuffled_mean_diversity': round(shuffled_div_mean, 5),
    'shuffled_std': round(float(np.std(shuffled_div_arr)), 5) if len(shuffled_div_arr) > 0 else None,
    'direction': 'lower' if obs_div_mean < shuffled_div_mean else 'higher',
    'p_value': float(p_div),
    'n_permutations': N_PERMS_DIV,
    'pass': t23_pass,
}


# ════════════════════════════════════════════════════════════════
# T2.4: Vocabulary Discontinuity at Boundaries (C702)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T2.4: VOCABULARY DISCONTINUITY AT BOUNDARIES (C702)")
print("=" * 70)

# Boundary Jaccard: PP MIDDLE similarity between last bundle line and adjacent RI-bearing line
# Interior Jaccard: PP MIDDLE similarity between consecutive lines within bundles

interior_jaccards = []
boundary_jaccards = []

for fol in folios:
    records = analyzer.analyze_folio(fol)
    if len(records) < 3:
        continue

    # Build line-level PP middle sets and classification
    line_data = []
    for rec in records:
        pp_mids = get_line_pp_middles(rec)
        is_ri_bearing = rec.ri_count > 0
        line_data.append((rec, pp_mids, is_ri_bearing))

    # Interior: consecutive lines within same bundle (both PP-pure)
    for i in range(len(line_data) - 1):
        _, mids_i, is_ri_i = line_data[i]
        _, mids_j, is_ri_j = line_data[i + 1]
        if not is_ri_i and not is_ri_j and mids_i and mids_j:
            interior_jaccards.append(jaccard(mids_i, mids_j))

    # Boundary: PP-pure line adjacent to RI-bearing line
    for i in range(len(line_data) - 1):
        _, mids_i, is_ri_i = line_data[i]
        _, mids_j, is_ri_j = line_data[i + 1]
        # One PP-pure, one RI-bearing, adjacent
        if is_ri_i != is_ri_j:
            pp_mids = mids_i if not is_ri_i else mids_j
            ri_mids = mids_j if is_ri_j else mids_i
            # Compare PP content of both lines
            if pp_mids and ri_mids:
                boundary_jaccards.append(jaccard(pp_mids, ri_mids))

interior_arr = np.array(interior_jaccards)
boundary_arr = np.array(boundary_jaccards)

int_mean = float(np.mean(interior_arr)) if len(interior_arr) > 0 else 0
bnd_mean = float(np.mean(boundary_arr)) if len(boundary_arr) > 0 else 0
ratio_24 = int_mean / bnd_mean if bnd_mean > 0 else float('inf')

if len(interior_arr) >= 5 and len(boundary_arr) >= 5:
    u_stat_24, u_p_24 = scipy_stats.mannwhitneyu(interior_arr, boundary_arr, alternative='greater')
else:
    u_stat_24, u_p_24 = 0, 1.0

t24_pass = ratio_24 > 1.5 and u_p_24 < 0.001

print(f"\n  Interior pairs (PP-PP consecutive): {len(interior_arr)}")
print(f"  Boundary pairs (PP-RI adjacent): {len(boundary_arr)}")
print(f"  Interior mean Jaccard: {int_mean:.4f}")
print(f"  Boundary mean Jaccard: {bnd_mean:.4f}")
print(f"  Ratio (interior/boundary): {ratio_24:.2f}x")
print(f"  Mann-Whitney U p: {u_p_24:.2e}")
print(f"\n  PASS (ratio > 1.5x AND p < 0.001): {t24_pass}")

if t24_pass:
    pass_count += 1

results['T2_4_boundary_discontinuity'] = {
    'constraint': 'C702',
    'interior_pairs': len(interior_arr),
    'boundary_pairs': len(boundary_arr),
    'interior_mean_jaccard': round(int_mean, 5),
    'boundary_mean_jaccard': round(bnd_mean, 5),
    'ratio': round(ratio_24, 3),
    'mann_whitney_u': float(u_stat_24),
    'mann_whitney_p': float(u_p_24),
    'pass': t24_pass,
}


# ════════════════════════════════════════════════════════════════
# GATE CHECK
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("GATE CHECK: Phase 2")
print("=" * 70)

tests = ['T2.1 (C699)', 'T2.2 (C700)', 'T2.3 (C701)', 'T2.4 (C702)']
passes = [
    results['T2_1_within_vs_between']['pass'],
    results['T2_2_bundle_pp_vs_random']['pass'],
    results['T2_3_pp_diversity']['pass'],
    results['T2_4_boundary_discontinuity']['pass'],
]

for test, passed in zip(tests, passes):
    status = "PASS" if passed else "FAIL"
    print(f"  {test}: {status}")

print(f"\n  Total passed: {pass_count}/4")
gate_passed = pass_count >= 3
print(f"  Gate (3/4): {'PASSED' if gate_passed else 'FAILED'}")

results['gate'] = {
    'threshold': '3/4',
    'passed': pass_count,
    'total': 4,
    'result': 'PASSED' if gate_passed else 'FAILED',
}

# ── Save ──
out_path = RESULTS_DIR / 'vocabulary_coherence.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n  Saved: {out_path}")
print("\nDone.")
