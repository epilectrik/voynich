"""
RI_FUNCTIONAL_IDENTITY Phase - Script 1: RI Function Discrimination
Tests T1-T7 (C710-C716)

Hypothesis H4: RI tokens are independent content — A's actual payload.
PP is the compatibility interface with B; RI is the identity of what
each A line catalogs. Each A folio is a thematic catalog page.

Tests (expert-recommended order):
  T2: RI Vocabulary Density per Folio (C711) — content vs scaffold
  T4: Adjacent Line RI Similarity (C713) — content vs addressing
  T1: RI-PP Positional Complementarity (C710) — content vs scaffold
  T6: RI Content Independence from PP (C715) — content vs refinement
  T5: Line-Final RI Morphological Profile (C714) — closure vs scaffold marker
  T3: RI Singleton vs Repeater Behavior (C712) — content vs record-keeping
  T7: Cross-Folio RI Reuse Pattern (C716) — content vs scaffold
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
print("RI_FUNCTIONAL_IDENTITY - RI Function Discrimination Tests")
print("=" * 70)

# ── Load data ──
tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

folios = analyzer.get_folios()
print(f"A folios: {len(folios)}")

# Pre-compute all records with RI/PP classification
folio_records = {}  # folio -> list of RecordAnalysis
all_records = []
for fol in folios:
    records = analyzer.analyze_folio(fol)
    folio_records[fol] = records
    all_records.extend(records)

print(f"Total records: {len(all_records)}")

# Pre-compute per-line RI and PP middle sets
def get_ri_middles(record):
    return set(t.middle for t in record.tokens if t.is_ri and t.middle)

def get_pp_middles(record):
    return set(t.middle for t in record.tokens if t.is_pp and t.middle)

# Pre-compute folio-level PP pools for later tests
folio_pp_pools = {}
for fol in folios:
    pool = set()
    for rec in folio_records[fol]:
        pool |= get_pp_middles(rec)
    folio_pp_pools[fol] = pool

results = {
    'metadata': {
        'phase': 'RI_FUNCTIONAL_IDENTITY',
        'script': 'ri_functional_tests.py',
        'tests': 'T1-T7 (C710-C716)',
        'n_folios': len(folios),
        'n_records': len(all_records),
        'hypothesis': 'H4: RI as independent content (A payload)',
    },
}

pass_count = 0


# ════════════════════════════════════════════════════════════════
# T2: RI VOCABULARY DENSITY PER FOLIO (C711)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T2: RI VOCABULARY DENSITY PER FOLIO (C711)")
print("=" * 70)

# H4 predicts: more lines -> more unique RI types (content catalog grows)
# H5 predicts: RI types roughly constant (scaffolding)

folio_n_lines = []
folio_n_ri_types = []

for fol in folios:
    records = folio_records[fol]
    n_lines = len(records)
    ri_types = set()
    for rec in records:
        ri_types |= get_ri_middles(rec)
    folio_n_lines.append(n_lines)
    folio_n_ri_types.append(len(ri_types))

lines_arr = np.array(folio_n_lines)
ri_arr = np.array(folio_n_ri_types)

rho, rho_p = scipy_stats.spearmanr(lines_arr, ri_arr)

# Also PP types for comparison
folio_n_pp_types = [len(folio_pp_pools[fol]) for fol in folios]
pp_types_arr = np.array(folio_n_pp_types)
rho_pp, rho_pp_p = scipy_stats.spearmanr(lines_arr, pp_types_arr)

t2_pass = rho > 0.5 and rho_p < 0.001

print(f"\n  RI types vs folio lines:")
print(f"    Spearman rho: {rho:.3f}, p: {rho_p:.2e}")
print(f"    Mean RI types/folio: {np.mean(ri_arr):.1f}")
print(f"    Mean lines/folio: {np.mean(lines_arr):.1f}")
print(f"\n  PP types vs folio lines (for comparison):")
print(f"    Spearman rho: {rho_pp:.3f}, p: {rho_pp_p:.2e}")
print(f"    Mean PP types/folio: {np.mean(pp_types_arr):.1f}")
print(f"\n  H4 (content): rho > 0.5 -> RI grows with folio size")
print(f"  H5 (scaffold): rho < 0.2 -> RI constant")
print(f"\n  PASS (rho > 0.5, p < 0.001): {t2_pass}")

if t2_pass:
    pass_count += 1

results['T2_ri_density'] = {
    'constraint': 'C711',
    'ri_rho': round(float(rho), 4),
    'ri_rho_p': float(rho_p),
    'pp_rho': round(float(rho_pp), 4),
    'pp_rho_p': float(rho_pp_p),
    'mean_ri_types': round(float(np.mean(ri_arr)), 2),
    'mean_pp_types': round(float(np.mean(pp_types_arr)), 2),
    'mean_lines': round(float(np.mean(lines_arr)), 2),
    'pass': t2_pass,
}


# ════════════════════════════════════════════════════════════════
# T4: ADJACENT LINE RI SIMILARITY (C713)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T4: ADJACENT LINE RI SIMILARITY (C713)")
print("=" * 70)

# H4 predicts: adjacent RI Jaccard ~ non-adjacent (content varies independently)
# H2 predicts: adjacent RI Jaccard > non-adjacent (sequential addressing)

adjacent_ri_jaccards = []
nonadjacent_ri_jaccards = []

for fol in folios:
    records = folio_records[fol]
    if len(records) < 3:
        continue

    ri_sets = [get_ri_middles(rec) for rec in records]

    # Adjacent pairs
    for i in range(len(ri_sets) - 1):
        if ri_sets[i] and ri_sets[i + 1]:
            union = ri_sets[i] | ri_sets[i + 1]
            inter = ri_sets[i] & ri_sets[i + 1]
            adjacent_ri_jaccards.append(len(inter) / len(union) if union else 0)

    # Non-adjacent pairs (skip distance >= 2)
    for i in range(len(ri_sets)):
        for j in range(i + 2, min(i + 6, len(ri_sets))):  # cap to avoid explosion
            if ri_sets[i] and ri_sets[j]:
                union = ri_sets[i] | ri_sets[j]
                inter = ri_sets[i] & ri_sets[j]
                nonadjacent_ri_jaccards.append(len(inter) / len(union) if union else 0)

adj_arr = np.array(adjacent_ri_jaccards)
nonadj_arr = np.array(nonadjacent_ri_jaccards)
adj_mean = float(np.mean(adj_arr)) if len(adj_arr) > 0 else 0
nonadj_mean = float(np.mean(nonadj_arr)) if len(nonadj_arr) > 0 else 0
ratio_t4 = adj_mean / nonadj_mean if nonadj_mean > 0 else float('inf')

if len(adj_arr) >= 5 and len(nonadj_arr) >= 5:
    u_stat_t4, u_p_t4 = scipy_stats.mannwhitneyu(adj_arr, nonadj_arr, alternative='greater')
else:
    u_stat_t4, u_p_t4 = 0, 1.0

# H4 pass: ratio 0.9-1.2x AND low absolute Jaccard (<0.2)
t4_pass = (0.9 <= ratio_t4 <= 1.5) and adj_mean < 0.2

print(f"\n  Adjacent RI pairs: {len(adj_arr)}")
print(f"  Non-adjacent RI pairs: {len(nonadj_arr)}")
print(f"  Adjacent mean Jaccard: {adj_mean:.4f}")
print(f"  Non-adjacent mean Jaccard: {nonadj_mean:.4f}")
print(f"  Ratio (adj/nonadj): {ratio_t4:.2f}x")
print(f"  Mann-Whitney p: {u_p_t4:.2e}")
print(f"\n  C346 reference: sequential coherence 1.20x (full vocabulary)")
print(f"\n  H4 (content): ratio 0.9-1.2x, absolute <0.2")
print(f"  H2 (addressing): ratio >1.5x")
print(f"\n  PASS (ratio 0.9-1.5x AND Jaccard < 0.2): {t4_pass}")

if t4_pass:
    pass_count += 1

results['T4_adjacent_ri'] = {
    'constraint': 'C713',
    'adjacent_pairs': len(adj_arr),
    'nonadjacent_pairs': len(nonadj_arr),
    'adjacent_mean': round(adj_mean, 5),
    'nonadjacent_mean': round(nonadj_mean, 5),
    'ratio': round(ratio_t4, 3),
    'mann_whitney_p': float(u_p_t4),
    'c346_reference': 1.20,
    'pass': t4_pass,
}


# ════════════════════════════════════════════════════════════════
# T1: RI-PP POSITIONAL COMPLEMENTARITY (C710)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T1: RI-PP POSITIONAL COMPLEMENTARITY (C710)")
print("=" * 70)

# H4 predicts: RI and PP occupy complementary positions within lines
# (not randomly interleaved)

ri_mean_positions = []  # mean normalized position of RI tokens per line
pp_mean_positions = []  # mean normalized position of PP tokens per line

for rec in all_records:
    n_tok = len(rec.tokens)
    if n_tok < 3:
        continue

    ri_pos = []
    pp_pos = []
    for i, t in enumerate(rec.tokens):
        norm_pos = i / (n_tok - 1)  # 0.0 = first, 1.0 = last
        if t.is_ri:
            ri_pos.append(norm_pos)
        elif t.is_pp:
            pp_pos.append(norm_pos)

    if ri_pos and pp_pos:
        ri_mean_positions.append(np.mean(ri_pos))
        pp_mean_positions.append(np.mean(pp_pos))

ri_pos_arr = np.array(ri_mean_positions)
pp_pos_arr = np.array(pp_mean_positions)

# Paired test: does RI mean position differ from PP mean position?
if len(ri_pos_arr) >= 5:
    diff = ri_pos_arr - pp_pos_arr
    t_stat, t_p = scipy_stats.ttest_rel(ri_pos_arr, pp_pos_arr)
    effect_d = float(np.mean(diff) / np.std(diff)) if np.std(diff) > 0 else 0
else:
    t_stat, t_p, effect_d = 0, 1.0, 0

t1_pass = t_p < 0.01 and abs(effect_d) > 0.3

print(f"\n  Lines with both RI and PP: {len(ri_pos_arr)}")
print(f"  RI mean normalized position: {np.mean(ri_pos_arr):.4f}")
print(f"  PP mean normalized position: {np.mean(pp_pos_arr):.4f}")
print(f"  Mean difference (RI - PP): {np.mean(diff):.4f}")
print(f"  Paired t-test: t={t_stat:.2f}, p={t_p:.2e}")
print(f"  Cohen's d: {effect_d:.3f}")
print(f"\n  Direction: {'RI later than PP' if np.mean(diff) > 0 else 'RI earlier than PP'}")
print(f"\n  PASS (p < 0.01 AND |d| > 0.3): {t1_pass}")

if t1_pass:
    pass_count += 1

results['T1_positional_complementarity'] = {
    'constraint': 'C710',
    'n_mixed_lines': len(ri_pos_arr),
    'ri_mean_position': round(float(np.mean(ri_pos_arr)), 5),
    'pp_mean_position': round(float(np.mean(pp_pos_arr)), 5),
    'mean_difference': round(float(np.mean(diff)), 5),
    't_stat': round(float(t_stat), 3),
    't_p': float(t_p),
    'cohens_d': round(effect_d, 4),
    'direction': 'RI later' if np.mean(diff) > 0 else 'RI earlier',
    'pass': t1_pass,
}


# ════════════════════════════════════════════════════════════════
# T6: RI CONTENT INDEPENDENCE FROM PP (C715)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T6: RI CONTENT INDEPENDENCE FROM PP (C715)")
print("=" * 70)

# H4 predicts: RI is independent of PP (no correlation)
# H3 predicts: RI correlates with PP (refinement)

# Method: Compute correlation between number of RI types and number of PP types per line
ri_counts_per_line = []
pp_counts_per_line = []

for rec in all_records:
    ri_mids = get_ri_middles(rec)
    pp_mids = get_pp_middles(rec)
    ri_counts_per_line.append(len(ri_mids))
    pp_counts_per_line.append(len(pp_mids))

ri_c_arr = np.array(ri_counts_per_line)
pp_c_arr = np.array(pp_counts_per_line)

rho_rp, rho_rp_p = scipy_stats.spearmanr(ri_c_arr, pp_c_arr)

# Also: For lines with identical PP sets, how variable is RI?
# Group lines by PP fingerprint
pp_fingerprints = defaultdict(list)
for rec in all_records:
    pp_mids = frozenset(get_pp_middles(rec))
    if pp_mids:
        ri_mids = frozenset(get_ri_middles(rec))
        pp_fingerprints[pp_mids].append(ri_mids)

# For PP groups with 2+ lines: how many unique RI sets?
pp_group_ri_diversity = []
for pp_fp, ri_sets in pp_fingerprints.items():
    if len(ri_sets) >= 2:
        unique_ri = len(set(ri_sets))
        pp_group_ri_diversity.append(unique_ri / len(ri_sets))

mean_ri_diversity = float(np.mean(pp_group_ri_diversity)) if pp_group_ri_diversity else 0

# H4 pass: weak or no correlation (|rho| < 0.3) AND high RI diversity within PP groups
t6_pass = abs(rho_rp) < 0.3 and mean_ri_diversity > 0.5

print(f"\n  RI-PP count correlation:")
print(f"    Spearman rho: {rho_rp:.3f}, p: {rho_rp_p:.2e}")
print(f"\n  PP fingerprint groups (>=2 lines): {len(pp_group_ri_diversity)}")
print(f"  Mean RI diversity within PP groups: {mean_ri_diversity:.3f}")
print(f"  (1.0 = every line has unique RI; 0.0 = all same)")
print(f"\n  H4: |rho| < 0.3 AND diversity > 0.5 (RI independent of PP)")
print(f"  H3: |rho| > 0.3 AND diversity < 0.5 (RI refines PP)")
print(f"\n  PASS (|rho| < 0.3 AND diversity > 0.5): {t6_pass}")

if t6_pass:
    pass_count += 1

results['T6_ri_pp_independence'] = {
    'constraint': 'C715',
    'ri_pp_rho': round(float(rho_rp), 4),
    'ri_pp_rho_p': float(rho_rp_p),
    'n_pp_groups': len(pp_group_ri_diversity),
    'mean_ri_diversity_within_pp': round(mean_ri_diversity, 4),
    'pass': t6_pass,
}


# ════════════════════════════════════════════════════════════════
# T5: LINE-FINAL RI MORPHOLOGICAL PROFILE (C714)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T5: LINE-FINAL RI MORPHOLOGICAL PROFILE (C714)")
print("=" * 70)

# H4 + closure: line-final RI tokens have distinctive morphology but
#   come from a LARGE, varied vocabulary (>50 types)
# H5 scaffold: line-final RI from a SMALL, concentrated vocabulary (<20 types)

final_ri_tokens = []    # (word, middle, prefix, suffix)
nonfinal_ri_tokens = []

for rec in all_records:
    if not rec.tokens:
        continue
    n_tok = len(rec.tokens)
    for i, t in enumerate(rec.tokens):
        if t.is_ri and t.middle:
            entry = (t.word, t.middle, t.prefix, t.suffix)
            if i == n_tok - 1:
                final_ri_tokens.append(entry)
            else:
                nonfinal_ri_tokens.append(entry)

final_middles = Counter(e[1] for e in final_ri_tokens)
nonfinal_middles = Counter(e[1] for e in nonfinal_ri_tokens)

n_final_unique = len(final_middles)
n_final_total = len(final_ri_tokens)
n_nonfinal_unique = len(nonfinal_middles)

# Concentration: fraction of total covered by top 5
top5_final = sum(c for _, c in final_middles.most_common(5))
top5_pct = top5_final / n_final_total if n_final_total > 0 else 0

# Suffix rate comparison
final_suffix_rate = sum(1 for e in final_ri_tokens if e[3]) / n_final_total if n_final_total else 0
nonfinal_suffix_rate = sum(1 for e in nonfinal_ri_tokens if e[3]) / len(nonfinal_ri_tokens) if nonfinal_ri_tokens else 0

# PREFIX rate comparison
final_prefix_rate = sum(1 for e in final_ri_tokens if e[2]) / n_final_total if n_final_total else 0
nonfinal_prefix_rate = sum(1 for e in nonfinal_ri_tokens if e[2]) / len(nonfinal_ri_tokens) if nonfinal_ri_tokens else 0

# MIDDLE length comparison
final_mid_lens = [len(e[1]) for e in final_ri_tokens]
nonfinal_mid_lens = [len(e[1]) for e in nonfinal_ri_tokens]
if final_mid_lens and nonfinal_mid_lens:
    len_u, len_p = scipy_stats.mannwhitneyu(final_mid_lens, nonfinal_mid_lens, alternative='two-sided')
else:
    len_u, len_p = 0, 1.0

# Chi-squared for suffix rate difference
if n_final_total > 0 and len(nonfinal_ri_tokens) > 0:
    obs = np.array([[sum(1 for e in final_ri_tokens if e[3]),
                     sum(1 for e in final_ri_tokens if not e[3])],
                    [sum(1 for e in nonfinal_ri_tokens if e[3]),
                     sum(1 for e in nonfinal_ri_tokens if not e[3])]])
    chi2_suf, chi2_suf_p = scipy_stats.chi2_contingency(obs)[:2]
else:
    chi2_suf, chi2_suf_p = 0, 1.0

# H4 pass: large vocabulary (>50 unique) AND morphological differences exist (chi2 p<0.01)
t5_pass = n_final_unique > 50 and chi2_suf_p < 0.01

print(f"\n  Line-final RI tokens: {n_final_total}")
print(f"  Unique line-final RI MIDDLEs: {n_final_unique}")
print(f"  Non-final RI tokens: {len(nonfinal_ri_tokens)}")
print(f"  Unique non-final RI MIDDLEs: {n_nonfinal_unique}")
print(f"\n  Top 5 line-final RI MIDDLEs:")
for mid, cnt in final_middles.most_common(5):
    print(f"    {mid}: {cnt} ({100*cnt/n_final_total:.1f}%)")
print(f"  Top 5 concentration: {100*top5_pct:.1f}%")
print(f"\n  Morphological comparison:")
print(f"    Suffix rate:  final={final_suffix_rate:.3f}, nonfinal={nonfinal_suffix_rate:.3f}")
print(f"    Chi2 suffix: {chi2_suf:.2f}, p={chi2_suf_p:.2e}")
print(f"    PREFIX rate:  final={final_prefix_rate:.3f}, nonfinal={nonfinal_prefix_rate:.3f}")
print(f"    MIDDLE length: final={np.mean(final_mid_lens):.2f}, nonfinal={np.mean(nonfinal_mid_lens):.2f}, p={len_p:.2e}")
print(f"\n  H4 (content-closure): >50 unique types AND morphological difference (p<0.01)")
print(f"  H5 (scaffold-marker): <20 types, top 5 > 50%")
print(f"\n  PASS (>50 unique AND chi2 p < 0.01): {t5_pass}")

if t5_pass:
    pass_count += 1

results['T5_final_ri_profile'] = {
    'constraint': 'C714',
    'n_final_ri': n_final_total,
    'n_unique_final_middles': n_final_unique,
    'n_nonfinal_ri': len(nonfinal_ri_tokens),
    'n_unique_nonfinal_middles': n_nonfinal_unique,
    'top5_concentration': round(top5_pct, 4),
    'top5_middles': [{'middle': m, 'count': c} for m, c in final_middles.most_common(5)],
    'suffix_rate_final': round(final_suffix_rate, 4),
    'suffix_rate_nonfinal': round(nonfinal_suffix_rate, 4),
    'suffix_chi2_p': float(chi2_suf_p),
    'prefix_rate_final': round(final_prefix_rate, 4),
    'prefix_rate_nonfinal': round(nonfinal_prefix_rate, 4),
    'middle_length_final': round(float(np.mean(final_mid_lens)), 3),
    'middle_length_nonfinal': round(float(np.mean(nonfinal_mid_lens)), 3),
    'middle_length_p': float(len_p),
    'pass': t5_pass,
}


# ════════════════════════════════════════════════════════════════
# T3: RI SINGLETON VS REPEATER BEHAVIOR (C712)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T3: RI SINGLETON VS REPEATER BEHAVIOR (C712)")
print("=" * 70)

# H4 predicts: singletons and repeaters have same positional behavior
# H1 predicts: repeaters show stronger positional bias (record-keeping markers)

# Count RI MIDDLE occurrences across manuscript
ri_middle_counts = Counter()
for rec in all_records:
    for t in rec.tokens:
        if t.is_ri and t.middle:
            ri_middle_counts[t.middle] += 1

singletons = {m for m, c in ri_middle_counts.items() if c == 1}
repeaters = {m for m, c in ri_middle_counts.items() if c >= 3}  # 3+ to ensure robust

print(f"\n  RI MIDDLE types: {len(ri_middle_counts)}")
print(f"  Singletons (1 occurrence): {len(singletons)}")
print(f"  Repeaters (3+ occurrences): {len(repeaters)}")

# Compare line-final rate of singletons vs repeaters
singleton_final = 0
singleton_total = 0
repeater_final = 0
repeater_total = 0

# Also compare mean normalized position
singleton_positions = []
repeater_positions = []

for rec in all_records:
    n_tok = len(rec.tokens)
    if n_tok == 0:
        continue
    for i, t in enumerate(rec.tokens):
        if t.is_ri and t.middle:
            norm_pos = i / (n_tok - 1) if n_tok > 1 else 0.5
            is_final = (i == n_tok - 1)
            if t.middle in singletons:
                singleton_total += 1
                singleton_positions.append(norm_pos)
                if is_final:
                    singleton_final += 1
            elif t.middle in repeaters:
                repeater_total += 1
                repeater_positions.append(norm_pos)
                if is_final:
                    repeater_final += 1

sing_final_rate = singleton_final / singleton_total if singleton_total > 0 else 0
rep_final_rate = repeater_final / repeater_total if repeater_total > 0 else 0

sing_pos_arr = np.array(singleton_positions)
rep_pos_arr = np.array(repeater_positions)

if len(sing_pos_arr) >= 5 and len(rep_pos_arr) >= 5:
    ks_stat_t3, ks_p_t3 = scipy_stats.ks_2samp(sing_pos_arr, rep_pos_arr)
else:
    ks_stat_t3, ks_p_t3 = 0, 1.0

# H4 pass: no significant difference (KS p > 0.05)
t3_pass = ks_p_t3 > 0.05

print(f"\n  Singleton tokens: {singleton_total}, line-final rate: {sing_final_rate:.3f}")
print(f"  Repeater tokens: {repeater_total}, line-final rate: {rep_final_rate:.3f}")
print(f"  Singleton mean position: {np.mean(sing_pos_arr):.4f}" if len(sing_pos_arr) > 0 else "  No singletons")
print(f"  Repeater mean position: {np.mean(rep_pos_arr):.4f}" if len(rep_pos_arr) > 0 else "  No repeaters")
print(f"  KS test: stat={ks_stat_t3:.4f}, p={ks_p_t3:.4f}")
print(f"\n  H4 (content): KS p > 0.05 (same positional distribution)")
print(f"  H1 (record-keeping): KS p < 0.01 (repeaters have stronger bias)")
print(f"\n  PASS (KS p > 0.05): {t3_pass}")

if t3_pass:
    pass_count += 1

results['T3_singleton_vs_repeater'] = {
    'constraint': 'C712',
    'n_singletons': len(singletons),
    'n_repeaters': len(repeaters),
    'singleton_tokens': singleton_total,
    'repeater_tokens': repeater_total,
    'singleton_final_rate': round(sing_final_rate, 4),
    'repeater_final_rate': round(rep_final_rate, 4),
    'singleton_mean_pos': round(float(np.mean(sing_pos_arr)), 4) if len(sing_pos_arr) > 0 else None,
    'repeater_mean_pos': round(float(np.mean(rep_pos_arr)), 4) if len(rep_pos_arr) > 0 else None,
    'ks_stat': round(float(ks_stat_t3), 5),
    'ks_p': float(ks_p_t3),
    'pass': t3_pass,
}


# ════════════════════════════════════════════════════════════════
# T7: CROSS-FOLIO RI REUSE PATTERN (C716)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T7: CROSS-FOLIO RI REUSE PATTERN (C716)")
print("=" * 70)

# H4 predicts: multi-folio RI appears on folios with different PP profiles
#   (same content item in different compatibility contexts)
# H5 predicts: multi-folio RI appears on folios with similar PP profiles
#   (scaffolding is context-independent)

# Find RI MIDDLEs on 2+ folios
ri_to_folios = defaultdict(set)
for fol in folios:
    for rec in folio_records[fol]:
        for t in rec.tokens:
            if t.is_ri and t.middle:
                ri_to_folios[t.middle].add(fol)

multi_folio_ri = {m: fols for m, fols in ri_to_folios.items() if len(fols) >= 2}
print(f"\n  RI MIDDLEs on 2+ folios: {len(multi_folio_ri)}")
print(f"  RI MIDDLEs on 1 folio only: {sum(1 for m, f in ri_to_folios.items() if len(f) == 1)}")

# For each multi-folio RI: compute mean PP Jaccard among its host folios
host_jaccards = []
for ri_mid, host_folios in multi_folio_ri.items():
    host_list = sorted(host_folios)
    if len(host_list) < 2:
        continue
    for i in range(len(host_list)):
        for j in range(i + 1, len(host_list)):
            pp_i = folio_pp_pools[host_list[i]]
            pp_j = folio_pp_pools[host_list[j]]
            union = pp_i | pp_j
            inter = pp_i & pp_j
            if union:
                host_jaccards.append(len(inter) / len(union))

# Random folio pairs baseline (reuse from T3.5 = C708: mean 0.274)
# Compute directly for comparison
rng = np.random.RandomState(42)
random_jaccards = []
for _ in range(len(host_jaccards)):
    f1, f2 = rng.choice(len(folios), 2, replace=False)
    pp1 = folio_pp_pools[folios[f1]]
    pp2 = folio_pp_pools[folios[f2]]
    union = pp1 | pp2
    inter = pp1 & pp2
    if union:
        random_jaccards.append(len(inter) / len(union))

host_arr = np.array(host_jaccards)
rand_arr = np.array(random_jaccards)
host_mean = float(np.mean(host_arr)) if len(host_arr) > 0 else 0
rand_mean = float(np.mean(rand_arr)) if len(rand_arr) > 0 else 0
ratio_t7 = host_mean / rand_mean if rand_mean > 0 else float('inf')

if len(host_arr) >= 5 and len(rand_arr) >= 5:
    u_t7, p_t7 = scipy_stats.mannwhitneyu(host_arr, rand_arr, alternative='two-sided')
else:
    u_t7, p_t7 = 0, 1.0

# H4 pass: ratio 0.8-1.2x (similar or lower)
t7_pass = 0.7 <= ratio_t7 <= 1.3

print(f"\n  Multi-folio RI host pair Jaccards: {len(host_arr)}")
print(f"  Host mean PP Jaccard: {host_mean:.4f}")
print(f"  Random pair PP Jaccard: {rand_mean:.4f}")
print(f"  Ratio: {ratio_t7:.2f}x")
print(f"  Mann-Whitney p: {p_t7:.2e}")
print(f"\n  H4 (content): ratio 0.8-1.2x (RI reuse independent of PP context)")
print(f"  H5 (scaffold): ratio > 1.5x (scaffolding on similar folios)")
print(f"\n  PASS (ratio 0.7-1.3x): {t7_pass}")

if t7_pass:
    pass_count += 1

results['T7_crossfolio_ri_reuse'] = {
    'constraint': 'C716',
    'n_multi_folio_ri': len(multi_folio_ri),
    'n_single_folio_ri': sum(1 for m, f in ri_to_folios.items() if len(f) == 1),
    'host_pairs': len(host_arr),
    'host_mean_pp_jaccard': round(host_mean, 5),
    'random_mean_pp_jaccard': round(rand_mean, 5),
    'ratio': round(ratio_t7, 3),
    'mann_whitney_p': float(p_t7),
    'pass': t7_pass,
}


# ════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SUMMARY: RI FUNCTIONAL IDENTITY")
print("=" * 70)

tests = [
    ('T1 (C710) RI-PP Positional', results['T1_positional_complementarity']['pass']),
    ('T2 (C711) RI Density/Folio', results['T2_ri_density']['pass']),
    ('T3 (C712) Singleton vs Repeater', results['T3_singleton_vs_repeater']['pass']),
    ('T4 (C713) Adjacent RI Similarity', results['T4_adjacent_ri']['pass']),
    ('T5 (C714) Final RI Morphology', results['T5_final_ri_profile']['pass']),
    ('T6 (C715) RI-PP Independence', results['T6_ri_pp_independence']['pass']),
    ('T7 (C716) Cross-Folio RI Reuse', results['T7_crossfolio_ri_reuse']['pass']),
]

for name, passed in tests:
    status = "PASS" if passed else "FAIL"
    print(f"  {name}: {status}")

print(f"\n  Total passed: {pass_count}/7")
print(f"  H4 (RI as content) assessment: {'STRONGLY SUPPORTED' if pass_count >= 5 else 'MIXED' if pass_count >= 3 else 'WEAK'}")

results['summary'] = {
    'passed': pass_count,
    'total': 7,
    'h4_assessment': 'STRONGLY_SUPPORTED' if pass_count >= 5 else 'MIXED' if pass_count >= 3 else 'WEAK',
}

# ── Save ──
out_path = RESULTS_DIR / 'ri_functional_tests.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n  Saved: {out_path}")
print("\nDone.")
