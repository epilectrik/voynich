"""Test 11: Prefix+Suffix Combination as Material Coordinate.

Question: Does the (PREFIX, SUFFIX) pair carry emergent section information
beyond either component alone?

Method:
  1. Extract PREFIX and SUFFIX for each Currier B token.
  2. Build contingency tables:
     - PREFIX x section
     - SUFFIX x section
     - (PREFIX, SUFFIX) pair x section
  3. Compute section-exclusivity at each level:
     - Fraction of types appearing in only 1 section
  4. Compare pair exclusivity against components:
     - Must exceed both by >10 percentage points
  5. Permutation test: shuffle section labels 1000 times,
     compute null pair exclusivity distribution.
  6. Compute Cramer's V at each level against section.
  7. Expected pair exclusivity under independence check.

Pass: Pair exclusivity exceeds both components by >10pp AND
      exceeds random baseline (permutation p < 0.01).
Fail: Pair exclusivity = product of components (independent combination).
"""

import json
import sys
import math
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

import numpy as np
from scipy.stats import chi2_contingency

sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology

# ============================================================
# SETUP
# ============================================================
tx = Transcript()
morph = Morphology()

SECTIONS = ['B', 'H', 'S', 'T', 'C']
MIN_TYPE_COUNT = 5  # Minimum tokens for a type to be included
N_PERMUTATIONS = 1000
np.random.seed(42)

# ============================================================
# STEP 1: Collect per-token data (single pass)
# ============================================================
tokens_data = []  # List of (prefix_str, suffix_str, section)

for token in tx.currier_b():
    section = token.section
    if section not in SECTIONS:
        continue

    m = morph.extract(token.word)
    pfx = m.prefix if m.prefix else 'NONE'
    sfx = m.suffix if m.suffix else 'NONE'

    tokens_data.append((pfx, sfx, section))

print(f"Total Currier B tokens (filtered): {len(tokens_data)}")

# ============================================================
# STEP 2: Build per-type section distributions
# ============================================================
# Count tokens per type
prefix_counts = Counter()
suffix_counts = Counter()
pair_counts = Counter()

prefix_section = defaultdict(Counter)  # prefix -> section -> count
suffix_section = defaultdict(Counter)  # suffix -> section -> count
pair_section = defaultdict(Counter)    # (prefix, suffix) -> section -> count

for pfx, sfx, sec in tokens_data:
    prefix_counts[pfx] += 1
    suffix_counts[sfx] += 1
    pair_counts[(pfx, sfx)] += 1
    prefix_section[pfx][sec] += 1
    suffix_section[sfx][sec] += 1
    pair_section[(pfx, sfx)][sec] += 1

# Filter to types with MIN_TYPE_COUNT
valid_prefixes = {p for p, c in prefix_counts.items() if c >= MIN_TYPE_COUNT}
valid_suffixes = {s for s, c in suffix_counts.items() if c >= MIN_TYPE_COUNT}
valid_pairs = {p for p, c in pair_counts.items() if c >= MIN_TYPE_COUNT}

print(f"\nType counts (>= {MIN_TYPE_COUNT} tokens):")
print(f"  Prefixes: {len(valid_prefixes)} (of {len(prefix_counts)} total)")
print(f"  Suffixes: {len(valid_suffixes)} (of {len(suffix_counts)} total)")
print(f"  (Prefix, Suffix) pairs: {len(valid_pairs)} (of {len(pair_counts)} total)")


# ============================================================
# STEP 3: Compute section-exclusivity at each level
# ============================================================
def compute_exclusivity(type_section_map, valid_types):
    """Fraction of types appearing in only 1 section."""
    exclusive_count = 0
    total = 0
    for t in valid_types:
        sections_present = set(s for s, c in type_section_map[t].items() if c > 0)
        total += 1
        if len(sections_present) == 1:
            exclusive_count += 1
    return exclusive_count / max(1, total), exclusive_count, total


prefix_excl, prefix_excl_n, prefix_total_n = compute_exclusivity(
    prefix_section, valid_prefixes)
suffix_excl, suffix_excl_n, suffix_total_n = compute_exclusivity(
    suffix_section, valid_suffixes)
pair_excl, pair_excl_n, pair_total_n = compute_exclusivity(
    pair_section, valid_pairs)

print(f"\nSection-exclusivity (fraction appearing in only 1 section):")
print(f"  PREFIX:  {prefix_excl:.3f} ({prefix_excl_n}/{prefix_total_n})")
print(f"  SUFFIX:  {suffix_excl:.3f} ({suffix_excl_n}/{suffix_total_n})")
print(f"  PAIR:    {pair_excl:.3f} ({pair_excl_n}/{pair_total_n})")

pair_vs_prefix_diff = (pair_excl - prefix_excl) * 100
pair_vs_suffix_diff = (pair_excl - suffix_excl) * 100
print(f"\n  Pair - Prefix: {pair_vs_prefix_diff:+.1f} pp")
print(f"  Pair - Suffix: {pair_vs_suffix_diff:+.1f} pp")
exceeds_both_by_10pp = pair_vs_prefix_diff > 10 and pair_vs_suffix_diff > 10


# ============================================================
# STEP 4: Expected pair exclusivity under independence
# ============================================================
# Under independence, a pair is section-exclusive if either:
# - The prefix is exclusive to section X AND the suffix appears in X (at least)
# - OR the suffix is exclusive to section X AND the prefix appears in X
# Approximate: P(pair exclusive) ~ P(prefix excl) + P(suffix excl) - P(both excl)
# This is an upper bound under independence (union bound).
expected_pair_excl_independence = prefix_excl + suffix_excl - (prefix_excl * suffix_excl)
independence_excess = pair_excl - expected_pair_excl_independence

print(f"\nExpected pair exclusivity under independence (union bound): {expected_pair_excl_independence:.3f}")
print(f"Observed - expected: {independence_excess:+.3f}")


# ============================================================
# STEP 5: Permutation test
# ============================================================
# Shuffle section labels among tokens, recompute pair exclusivity
section_labels = [sec for _, _, sec in tokens_data]
pfx_labels = [pfx for pfx, _, _ in tokens_data]
sfx_labels = [sfx for _, sfx, _ in tokens_data]

null_pair_exclusivities = []

for perm_i in range(N_PERMUTATIONS):
    if (perm_i + 1) % 200 == 0:
        print(f"  Permutation {perm_i + 1}/{N_PERMUTATIONS}...")

    shuffled_sections = np.random.permutation(section_labels)

    # Recompute pair section counts
    perm_pair_section = defaultdict(Counter)
    perm_pair_counts = Counter()

    for i in range(len(tokens_data)):
        pair_key = (pfx_labels[i], sfx_labels[i])
        perm_pair_section[pair_key][shuffled_sections[i]] += 1
        perm_pair_counts[pair_key] += 1

    # Valid pairs (same set as original, since pair identity doesn't change)
    perm_valid = {p for p, c in perm_pair_counts.items() if c >= MIN_TYPE_COUNT}

    excl, _, _ = compute_exclusivity(perm_pair_section, perm_valid)
    null_pair_exclusivities.append(excl)

null_mean = float(np.mean(null_pair_exclusivities))
null_std = float(np.std(null_pair_exclusivities))
# p-value: fraction of null >= observed
p_perm = float(np.mean([n >= pair_excl for n in null_pair_exclusivities]))

print(f"\nPermutation null distribution (pair exclusivity):")
print(f"  Mean: {null_mean:.4f}  Std: {null_std:.4f}")
print(f"  Observed: {pair_excl:.4f}")
print(f"  p-value (observed >= null): {p_perm:.4f}")


# ============================================================
# STEP 6: Cramer's V at each level against section
# ============================================================
def cramers_v_for_level(type_section_map, valid_types, all_sections):
    """Build contingency table (types x sections), compute Cramer's V."""
    types_list = sorted(valid_types)
    if len(types_list) < 2:
        return None

    # Build table: rows = types, cols = sections
    table = []
    for t in types_list:
        row = [type_section_map[t].get(s, 0) for s in all_sections]
        table.append(row)
    table = np.array(table, dtype=float)

    # Remove zero-sum rows/cols
    row_sums = table.sum(axis=1)
    col_sums = table.sum(axis=0)
    keep_rows = row_sums > 0
    keep_cols = col_sums > 0
    table = table[keep_rows][:, keep_cols]

    if table.shape[0] < 2 or table.shape[1] < 2:
        return None

    n = table.sum()
    if n < 5:
        return None

    try:
        chi2_stat, p, dof, expected = chi2_contingency(table)
    except ValueError:
        return None

    min_dim = min(table.shape[0], table.shape[1]) - 1
    if min_dim == 0 or n == 0:
        return None
    V = math.sqrt(chi2_stat / (n * min_dim))

    return {
        'chi2': float(chi2_stat),
        'p': float(p),
        'dof': int(dof),
        'V': float(V),
        'n': int(n),
        'table_shape': list(table.shape),
    }


print("\nCramer's V (type x section):")

prefix_v_result = cramers_v_for_level(prefix_section, valid_prefixes, SECTIONS)
if prefix_v_result:
    print(f"  PREFIX:  V={prefix_v_result['V']:.4f}  chi2={prefix_v_result['chi2']:.1f}  "
          f"p={prefix_v_result['p']:.2e}  shape={prefix_v_result['table_shape']}")
else:
    print(f"  PREFIX:  DEGENERATE")

suffix_v_result = cramers_v_for_level(suffix_section, valid_suffixes, SECTIONS)
if suffix_v_result:
    print(f"  SUFFIX:  V={suffix_v_result['V']:.4f}  chi2={suffix_v_result['chi2']:.1f}  "
          f"p={suffix_v_result['p']:.2e}  shape={suffix_v_result['table_shape']}")
else:
    print(f"  SUFFIX:  DEGENERATE")

# For pair, we need to use (pfx, sfx) as string keys
pair_section_str = {}
for (pfx, sfx), sec_counter in pair_section.items():
    key = f"{pfx}+{sfx}"
    pair_section_str[key] = sec_counter
valid_pairs_str = {f"{pfx}+{sfx}" for (pfx, sfx) in valid_pairs}

pair_v_result = cramers_v_for_level(pair_section_str, valid_pairs_str, SECTIONS)
if pair_v_result:
    print(f"  PAIR:    V={pair_v_result['V']:.4f}  chi2={pair_v_result['chi2']:.1f}  "
          f"p={pair_v_result['p']:.2e}  shape={pair_v_result['table_shape']}")
else:
    print(f"  PAIR:    DEGENERATE")


# ============================================================
# STEP 7: Additional detail - most exclusive pairs
# ============================================================
exclusive_pairs = []
for (pfx, sfx) in valid_pairs:
    sections_present = set(s for s, c in pair_section[(pfx, sfx)].items() if c > 0)
    if len(sections_present) == 1:
        sec = list(sections_present)[0]
        count = pair_counts[(pfx, sfx)]
        exclusive_pairs.append({
            'prefix': pfx,
            'suffix': sfx,
            'section': sec,
            'count': count,
        })

exclusive_pairs.sort(key=lambda x: -x['count'])

print(f"\nTop section-exclusive pairs (appearing in only 1 section):")
for ep in exclusive_pairs[:15]:
    print(f"  ({ep['prefix']}, {ep['suffix']}) -> {ep['section']}  n={ep['count']}")


# ============================================================
# STEP 8: Multi-section pairs - section distribution skew
# ============================================================
# For pairs in 2+ sections, compute max section share
multi_section_pairs = []
for (pfx, sfx) in valid_pairs:
    sec_counts = pair_section[(pfx, sfx)]
    sections_present = [s for s, c in sec_counts.items() if c > 0]
    if len(sections_present) >= 2:
        total = sum(sec_counts.values())
        max_sec = max(sec_counts, key=sec_counts.get)
        max_share = sec_counts[max_sec] / total
        multi_section_pairs.append({
            'prefix': pfx,
            'suffix': sfx,
            'n_sections': len(sections_present),
            'total': total,
            'max_section': max_sec,
            'max_share': round(max_share, 3),
        })

multi_section_pairs.sort(key=lambda x: -x['max_share'])

if multi_section_pairs:
    mean_max_share = float(np.mean([m['max_share'] for m in multi_section_pairs]))
    print(f"\nMulti-section pairs: {len(multi_section_pairs)}")
    print(f"Mean max-section share: {mean_max_share:.3f}")
    print(f"Top skewed pairs:")
    for mp in multi_section_pairs[:10]:
        print(f"  ({mp['prefix']}, {mp['suffix']}) -> {mp['max_section']} "
              f"({mp['max_share']:.1%})  total={mp['total']}  sections={mp['n_sections']}")


# ============================================================
# VERDICT
# ============================================================
permutation_significant = p_perm < 0.01

if exceeds_both_by_10pp and permutation_significant:
    verdict = 'PASS'
    verdict_reason = (
        f"Pair exclusivity ({pair_excl:.3f}) exceeds PREFIX ({prefix_excl:.3f}) "
        f"by {pair_vs_prefix_diff:.1f}pp and SUFFIX ({suffix_excl:.3f}) "
        f"by {pair_vs_suffix_diff:.1f}pp (both >10pp). "
        f"Permutation p={p_perm:.4f} < 0.01."
    )
elif not exceeds_both_by_10pp and not permutation_significant:
    verdict = 'FAIL'
    verdict_reason = (
        f"Pair exclusivity ({pair_excl:.3f}) does NOT exceed both components "
        f"by >10pp (vs PREFIX: {pair_vs_prefix_diff:+.1f}pp, vs SUFFIX: {pair_vs_suffix_diff:+.1f}pp). "
        f"Permutation p={p_perm:.4f} >= 0.01. "
        f"Combination is explainable by independent component effects."
    )
else:
    # Partial - one criterion met but not both
    verdict = 'PARTIAL'
    reasons = []
    if exceeds_both_by_10pp:
        reasons.append(f"Pair exclusivity exceeds both by >10pp")
    else:
        reasons.append(
            f"Pair exclusivity does NOT exceed both by >10pp "
            f"(vs PREFIX: {pair_vs_prefix_diff:+.1f}pp, vs SUFFIX: {pair_vs_suffix_diff:+.1f}pp)"
        )
    if permutation_significant:
        reasons.append(f"Permutation p={p_perm:.4f} < 0.01")
    else:
        reasons.append(f"Permutation p={p_perm:.4f} >= 0.01")
    verdict_reason = '; '.join(reasons)

print(f"\n{'='*60}")
print(f"VERDICT: {verdict}")
print(f"  {verdict_reason}")
print(f"{'='*60}")


# ============================================================
# OUTPUT
# ============================================================
output = {
    'test': 'prefix_suffix_combination',
    'description': 'Does the (PREFIX, SUFFIX) pair carry emergent section information beyond either component alone?',
    'timestamp': datetime.now().isoformat(),
    'parameters': {
        'min_type_count': MIN_TYPE_COUNT,
        'n_permutations': N_PERMUTATIONS,
        'sections': SECTIONS,
    },
    'counts': {
        'total_tokens': len(tokens_data),
        'prefix_types': len(valid_prefixes),
        'prefix_types_total': len(prefix_counts),
        'suffix_types': len(valid_suffixes),
        'suffix_types_total': len(suffix_counts),
        'pair_types': len(valid_pairs),
        'pair_types_total': len(pair_counts),
    },
    'exclusivity': {
        'prefix': round(prefix_excl, 4),
        'prefix_exclusive_n': prefix_excl_n,
        'prefix_total_n': prefix_total_n,
        'suffix': round(suffix_excl, 4),
        'suffix_exclusive_n': suffix_excl_n,
        'suffix_total_n': suffix_total_n,
        'pair': round(pair_excl, 4),
        'pair_exclusive_n': pair_excl_n,
        'pair_total_n': pair_total_n,
        'pair_minus_prefix_pp': round(pair_vs_prefix_diff, 1),
        'pair_minus_suffix_pp': round(pair_vs_suffix_diff, 1),
        'exceeds_both_by_10pp': exceeds_both_by_10pp,
    },
    'independence_model': {
        'expected_pair_excl': round(expected_pair_excl_independence, 4),
        'observed_minus_expected': round(independence_excess, 4),
    },
    'permutation_test': {
        'null_mean': round(null_mean, 4),
        'null_std': round(null_std, 4),
        'observed': round(pair_excl, 4),
        'p_value': round(p_perm, 4),
        'significant': permutation_significant,
        'n_permutations': N_PERMUTATIONS,
    },
    'cramers_v': {
        'prefix_v': round(prefix_v_result['V'], 4) if prefix_v_result else None,
        'prefix_chi2': round(prefix_v_result['chi2'], 1) if prefix_v_result else None,
        'prefix_p': prefix_v_result['p'] if prefix_v_result else None,
        'suffix_v': round(suffix_v_result['V'], 4) if suffix_v_result else None,
        'suffix_chi2': round(suffix_v_result['chi2'], 1) if suffix_v_result else None,
        'suffix_p': suffix_v_result['p'] if suffix_v_result else None,
        'pair_v': round(pair_v_result['V'], 4) if pair_v_result else None,
        'pair_chi2': round(pair_v_result['chi2'], 1) if pair_v_result else None,
        'pair_p': pair_v_result['p'] if pair_v_result else None,
    },
    'exclusive_pairs_top': exclusive_pairs[:20],
    'multi_section_pairs_top': multi_section_pairs[:20] if multi_section_pairs else [],
    'multi_section_mean_max_share': round(mean_max_share, 4) if multi_section_pairs else None,
    'verdict': verdict,
    'verdict_reason': verdict_reason,
}

out_path = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/results/prefix_suffix_combination.json')
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nOutput written to: {out_path}")
print("Done.")
