"""
11_frequency_controlled_exclusivity.py - Frequency-Controlled Zone Exclusivity

Phase: MIDDLE_MATERIAL_SEMANTICS
Test 11: Does phase-exclusivity hold for middles with 3+ occurrences per folio?

This is a stricter version of Test 1 that eliminates the expert's hapax concern
by requiring 3+ occurrences per folio (not just 2+). This eliminates hapax
inflation entirely and tests whether zone-exclusivity is a genuine structural
property rather than a sampling artifact.

Method:
1. Load Currier B tokens (H transcriber, labels excluded, uncertain excluded)
2. Extract MIDDLEs via canonical Morphology
3. For each B folio, identify paragraph boundaries and assign zones:
   - SETUP (first paragraph), PROCESS (middle paragraphs), FINISH (final paragraph)
   - For folios with 1-2 paragraphs, use line-based 20/60/20 split
4. ONLY consider middles with 3+ occurrences per folio (strict frequency control)
5. Classify each qualifying MIDDLE as zone-exclusive or SHARED
6. Compare zone-exclusive rates between RARE (<15 folios) and COMMON (>=15 folios)
7. Mann-Whitney U test on binary exclusivity values
8. Permutation baseline: shuffle zone assignments 500 times, compute expected
   zone-exclusive rate under null hypothesis of no zone structure
9. Verdict: SUPPORTED if rare still more zone-exclusive than common (p < 0.05)
   AND observed rate exceeds permutation baseline
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')

import json
import random
import csv
from collections import defaultdict, Counter
from pathlib import Path
from voynich import Transcript, Morphology
from scipy.stats import mannwhitneyu
import math

# ============================================================
# CONFIGURATION
# ============================================================
RESULTS_DIR = Path('C:/git/voynich/phases/MIDDLE_MATERIAL_SEMANTICS/results')
RARITY_THRESHOLD = 15  # folios: <15 = RARE, >=15 = COMMON
MIN_FOLIO_OCCURRENCES = 3  # Stricter: 3+ occurrences per folio
N_PERMUTATIONS = 500
RANDOM_SEED = 42


# ============================================================
# DATA LOADING
# ============================================================
def load_b_tokens():
    """Load all Currier B tokens with line/paragraph metadata."""
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for tok in tx.currier_b():
        # We want text tokens only (P-prefixed placements)
        if not tok.placement.startswith('P'):
            continue

        m = morph.extract(tok.word)
        if m.middle is None or m.middle == '_EMPTY_':
            continue

        tokens.append({
            'word': tok.word,
            'middle': m.middle,
            'folio': tok.folio,
            'line': tok.line,
            'par_initial': tok.par_initial,
            'line_initial': tok.line_initial,
        })

    return tokens


# ============================================================
# PARAGRAPH BOUNDARY DETECTION
# ============================================================
def assign_paragraphs(folio_tokens):
    """
    Assign paragraph numbers to tokens within a folio.

    Uses par_initial field: when par_initial is True AND line_initial is True,
    a new paragraph starts.
    """
    current_para = 0
    para_assignments = []

    for tok in folio_tokens:
        if tok['par_initial'] and tok['line_initial']:
            current_para += 1

        para_assignments.append(current_para)

    return para_assignments


# ============================================================
# ZONE ASSIGNMENT
# ============================================================
def assign_zones(folio_tokens, para_assignments):
    """
    Assign SETUP/PROCESS/FINISH zones.

    If 3+ paragraphs: first=SETUP, last=FINISH, middle=PROCESS
    If 1-2 paragraphs: line-based 20/60/20 split
    """
    n_paras = max(para_assignments) if para_assignments else 0

    if n_paras >= 3:
        first_para = 1
        last_para = n_paras
        zones = []
        for p in para_assignments:
            if p == first_para:
                zones.append('SETUP')
            elif p == last_para:
                zones.append('FINISH')
            else:
                zones.append('PROCESS')
        return zones
    else:
        # Line-based 20/60/20 split
        lines = []
        seen = set()
        for tok in folio_tokens:
            if tok['line'] not in seen:
                lines.append(tok['line'])
                seen.add(tok['line'])

        n_lines = len(lines)
        if n_lines < 3:
            return ['PROCESS'] * len(folio_tokens)

        setup_end = max(1, int(n_lines * 0.2))
        finish_start = n_lines - max(1, int(n_lines * 0.2))

        setup_lines = set(lines[:setup_end])
        finish_lines = set(lines[finish_start:])

        zones = []
        for tok in folio_tokens:
            if tok['line'] in setup_lines:
                zones.append('SETUP')
            elif tok['line'] in finish_lines:
                zones.append('FINISH')
            else:
                zones.append('PROCESS')
        return zones


# ============================================================
# PERMUTATION TEST
# ============================================================
def compute_exclusivity_rate(folio_tokens_with_zones, middle_folio_freq):
    """
    Compute the overall zone-exclusive rate for middles with >= MIN_FOLIO_OCCURRENCES.

    Returns (overall_rate, rare_rate, common_rate, n_qualifying).
    """
    middle_zone_sets = defaultdict(set)
    for tok, zone in folio_tokens_with_zones:
        middle_zone_sets[tok['middle']].add(zone)

    n_exclusive = 0
    n_total = 0
    rare_exclusive = 0
    rare_total = 0
    common_exclusive = 0
    common_total = 0

    for mid, freq in middle_folio_freq.items():
        if freq < MIN_FOLIO_OCCURRENCES:
            continue

        zones_present = middle_zone_sets.get(mid, set())
        if not zones_present:
            continue

        is_exclusive = len(zones_present) == 1
        n_total += 1
        if is_exclusive:
            n_exclusive += 1

    rate = n_exclusive / n_total if n_total > 0 else 0
    return rate, n_exclusive, n_total


def run_permutation_test(folio_tokens_list, zones_list, middle_folio_freq,
                         observed_rate, n_perms, rng):
    """
    Shuffle zone assignments within each folio and compute zone-exclusive rate
    under the null hypothesis.

    Returns list of permuted rates.
    """
    permuted_rates = []

    for _ in range(n_perms):
        # Shuffle zones within this folio (preserving zone distribution)
        shuffled_zones = list(zones_list)
        rng.shuffle(shuffled_zones)

        # Recompute exclusivity with shuffled zones
        middle_zone_sets = defaultdict(set)
        for tok, zone in zip(folio_tokens_list, shuffled_zones):
            middle_zone_sets[tok['middle']].add(zone)

        n_exclusive = 0
        n_total = 0
        for mid, freq in middle_folio_freq.items():
            if freq < MIN_FOLIO_OCCURRENCES:
                continue
            zones_present = middle_zone_sets.get(mid, set())
            if not zones_present:
                continue
            n_total += 1
            if len(zones_present) == 1:
                n_exclusive += 1

        rate = n_exclusive / n_total if n_total > 0 else 0
        permuted_rates.append(rate)

    return permuted_rates


# ============================================================
# MAIN ANALYSIS
# ============================================================
def main():
    rng = random.Random(RANDOM_SEED)

    print("Loading Currier B tokens...")
    all_tokens = load_b_tokens()
    print(f"  Total B text tokens with valid MIDDLE: {len(all_tokens)}")

    # Group by folio
    folio_groups = defaultdict(list)
    for tok in all_tokens:
        folio_groups[tok['folio']].append(tok)

    print(f"  B folios: {len(folio_groups)}")

    # ---- Pre-compute: corpus-wide MIDDLE folio counts ----
    middle_folios = defaultdict(set)
    for tok in all_tokens:
        middle_folios[tok['middle']].add(tok['folio'])

    middle_folio_count = {m: len(fs) for m, fs in middle_folios.items()}

    # ---- Per-folio analysis ----
    per_folio_summary = {}
    middle_exclusivity = []  # (middle, folio) -> exclusivity record

    # Collect all folio-level token-zone pairs for permutation test
    all_folio_token_zone_pairs = {}  # folio -> [(tok, zone), ...]
    all_folio_middle_freq = {}  # folio -> {middle: count}

    for folio in sorted(folio_groups.keys()):
        ftokens = folio_groups[folio]

        # Assign paragraphs
        para_assignments = assign_paragraphs(ftokens)

        # Assign zones
        zones = assign_zones(ftokens, para_assignments)

        # Store for permutation test
        all_folio_token_zone_pairs[folio] = list(zip(ftokens, zones))

        # Count MIDDLEs per zone, and total per folio
        middle_zone_sets = defaultdict(set)
        middle_folio_freq = Counter()

        for tok, zone in zip(ftokens, zones):
            mid = tok['middle']
            middle_zone_sets[mid].add(zone)
            middle_folio_freq[mid] += 1

        all_folio_middle_freq[folio] = dict(middle_folio_freq)

        # Classify middles (3+ occurrences only)
        n_exclusive = 0
        n_shared = 0
        n_skipped = 0
        rare_exclusive = 0
        rare_total = 0
        common_exclusive = 0
        common_total = 0

        for mid, freq in middle_folio_freq.items():
            if freq < MIN_FOLIO_OCCURRENCES:
                n_skipped += 1
                continue

            zones_present = middle_zone_sets[mid]
            is_exclusive = len(zones_present) == 1
            corpus_folio_count = middle_folio_count.get(mid, 0)

            if is_exclusive:
                n_exclusive += 1
            else:
                n_shared += 1

            if corpus_folio_count < RARITY_THRESHOLD:
                rare_total += 1
                if is_exclusive:
                    rare_exclusive += 1
            else:
                common_total += 1
                if is_exclusive:
                    common_exclusive += 1

            middle_exclusivity.append({
                'middle': mid,
                'folio': folio,
                'is_exclusive': is_exclusive,
                'n_zones': len(zones_present),
                'zones': sorted(zones_present),
                'folio_freq': freq,
                'corpus_folio_count': corpus_folio_count,
                'is_rare': corpus_folio_count < RARITY_THRESHOLD,
            })

        total_classified = n_exclusive + n_shared
        per_folio_summary[folio] = {
            'n_paragraphs': max(para_assignments) if para_assignments else 0,
            'n_lines': len(set(t['line'] for t in ftokens)),
            'n_tokens': len(ftokens),
            'n_unique_middles': len(middle_folio_freq),
            'n_below_threshold_skipped': n_skipped,
            'n_classified': total_classified,
            'n_zone_exclusive': n_exclusive,
            'n_shared': n_shared,
            'zone_exclusive_rate': n_exclusive / total_classified if total_classified > 0 else None,
            'rare_exclusive': rare_exclusive,
            'rare_total': rare_total,
            'common_exclusive': common_exclusive,
            'common_total': common_total,
        }

    # ---- Aggregate statistics ----
    rare_records = [r for r in middle_exclusivity if r['is_rare']]
    common_records = [r for r in middle_exclusivity if not r['is_rare']]

    rare_exclusive_count = sum(1 for r in rare_records if r['is_exclusive'])
    common_exclusive_count = sum(1 for r in common_records if r['is_exclusive'])

    rare_exclusive_rate = rare_exclusive_count / len(rare_records) if rare_records else 0
    common_exclusive_rate = common_exclusive_count / len(common_records) if common_records else 0

    overall_exclusive_count = sum(1 for r in middle_exclusivity if r['is_exclusive'])
    overall_rate = overall_exclusive_count / len(middle_exclusivity) if middle_exclusivity else 0

    print(f"\n=== Frequency-Controlled Zone Exclusivity (>={MIN_FOLIO_OCCURRENCES} per folio) ===")
    print(f"  Total qualifying (middle, folio) pairs: {len(middle_exclusivity)}")
    print(f"  Overall zone-exclusive rate: {overall_rate:.4f}")
    print(f"  Rare middles (<{RARITY_THRESHOLD} folios): {rare_exclusive_count}/{len(rare_records)} zone-exclusive = {rare_exclusive_rate:.4f}")
    print(f"  Common middles (>={RARITY_THRESHOLD} folios): {common_exclusive_count}/{len(common_records)} zone-exclusive = {common_exclusive_rate:.4f}")

    # ---- Compare with Test 1 ----
    print(f"\n  (Test 1 used min_folio_occurrences=2, had 2455 pairs)")
    print(f"  (Test 11 uses min_folio_occurrences=3, has {len(middle_exclusivity)} pairs)")

    # ---- Mann-Whitney U test ----
    rare_values = [1 if r['is_exclusive'] else 0 for r in rare_records]
    common_values = [1 if r['is_exclusive'] else 0 for r in common_records]

    if len(rare_values) >= 5 and len(common_values) >= 5:
        u_stat, p_value_mw = mannwhitneyu(rare_values, common_values, alternative='greater')
        print(f"\n  Mann-Whitney U = {u_stat:.1f}, p = {p_value_mw:.6f}")
    else:
        u_stat = None
        p_value_mw = None
        print("\n  Insufficient data for Mann-Whitney U test")

    # ---- Effect size (Cohen's d) ----
    if rare_values and common_values:
        mean_rare = sum(rare_values) / len(rare_values)
        mean_common = sum(common_values) / len(common_values)

        var_rare = sum((x - mean_rare) ** 2 for x in rare_values) / max(1, len(rare_values) - 1)
        var_common = sum((x - mean_common) ** 2 for x in common_values) / max(1, len(common_values) - 1)

        pooled_std = math.sqrt(
            ((len(rare_values) - 1) * var_rare + (len(common_values) - 1) * var_common)
            / (len(rare_values) + len(common_values) - 2)
        )
        effect_size_d = (mean_rare - mean_common) / pooled_std if pooled_std > 0 else 0
        print(f"  Cohen's d = {effect_size_d:.4f}")
    else:
        effect_size_d = None

    # ---- Permutation test ----
    # For each folio, shuffle zone assignments and recompute overall exclusivity rate.
    # This tests whether the observed rate exceeds what random zone placement produces.
    print(f"\n  Running permutation test ({N_PERMUTATIONS} permutations)...")

    # We run a global permutation: for each permutation, shuffle zones within
    # every folio independently, then recompute the overall exclusive rate.
    permuted_overall_rates = []
    permuted_rare_rates = []
    permuted_common_rates = []

    for perm_i in range(N_PERMUTATIONS):
        perm_exclusive_total = 0
        perm_total = 0
        perm_rare_exclusive = 0
        perm_rare_total = 0
        perm_common_exclusive = 0
        perm_common_total = 0

        for folio in sorted(folio_groups.keys()):
            pairs = all_folio_token_zone_pairs[folio]
            ftokens_list = [p[0] for p in pairs]
            zones_list = [p[1] for p in pairs]
            freq_map = all_folio_middle_freq[folio]

            # Shuffle zones within this folio
            shuffled_zones = list(zones_list)
            rng.shuffle(shuffled_zones)

            # Recompute exclusivity
            middle_zone_sets = defaultdict(set)
            for tok, zone in zip(ftokens_list, shuffled_zones):
                middle_zone_sets[tok['middle']].add(zone)

            for mid, freq in freq_map.items():
                if freq < MIN_FOLIO_OCCURRENCES:
                    continue
                zones_present = middle_zone_sets.get(mid, set())
                if not zones_present:
                    continue
                is_exclusive = len(zones_present) == 1
                corpus_fc = middle_folio_count.get(mid, 0)

                perm_total += 1
                if is_exclusive:
                    perm_exclusive_total += 1

                if corpus_fc < RARITY_THRESHOLD:
                    perm_rare_total += 1
                    if is_exclusive:
                        perm_rare_exclusive += 1
                else:
                    perm_common_total += 1
                    if is_exclusive:
                        perm_common_exclusive += 1

        perm_rate = perm_exclusive_total / perm_total if perm_total > 0 else 0
        permuted_overall_rates.append(perm_rate)

        perm_rare_rate = perm_rare_exclusive / perm_rare_total if perm_rare_total > 0 else 0
        permuted_rare_rates.append(perm_rare_rate)

        perm_common_rate = perm_common_exclusive / perm_common_total if perm_common_total > 0 else 0
        permuted_common_rates.append(perm_common_rate)

    # Permutation p-value: fraction of permuted rates >= observed
    perm_p_overall = sum(1 for r in permuted_overall_rates if r >= overall_rate) / N_PERMUTATIONS
    perm_p_rare = sum(1 for r in permuted_rare_rates if r >= rare_exclusive_rate) / N_PERMUTATIONS
    perm_p_common = sum(1 for r in permuted_common_rates if r >= common_exclusive_rate) / N_PERMUTATIONS

    perm_mean_overall = sum(permuted_overall_rates) / len(permuted_overall_rates)
    perm_mean_rare = sum(permuted_rare_rates) / len(permuted_rare_rates)
    perm_mean_common = sum(permuted_common_rates) / len(permuted_common_rates)

    print(f"\n  Permutation results:")
    print(f"    Overall: observed={overall_rate:.4f}, permuted_mean={perm_mean_overall:.4f}, p={perm_p_overall:.4f}")
    print(f"    Rare:    observed={rare_exclusive_rate:.4f}, permuted_mean={perm_mean_rare:.4f}, p={perm_p_rare:.4f}")
    print(f"    Common:  observed={common_exclusive_rate:.4f}, permuted_mean={perm_mean_common:.4f}, p={perm_p_common:.4f}")

    # ---- Zone preference breakdown ----
    zone_preference = Counter()
    for r in middle_exclusivity:
        if r['is_exclusive']:
            zone_preference[r['zones'][0]] += 1

    rare_zone_pref = Counter()
    for r in rare_records:
        if r['is_exclusive']:
            rare_zone_pref[r['zones'][0]] += 1

    common_zone_pref = Counter()
    for r in common_records:
        if r['is_exclusive']:
            common_zone_pref[r['zones'][0]] += 1

    print(f"\n  Zone preference (all exclusive middles): {dict(zone_preference)}")
    print(f"  Zone preference (rare exclusive): {dict(rare_zone_pref)}")
    print(f"  Zone preference (common exclusive): {dict(common_zone_pref)}")

    # ---- Verdict ----
    # SUPPORTED if:
    # 1. Rare middles are significantly more zone-exclusive than common (MW p < 0.05)
    # 2. Observed overall rate exceeds permutation baseline (perm p < 0.05)
    mw_pass = p_value_mw is not None and p_value_mw < 0.05 and rare_exclusive_rate > common_exclusive_rate
    perm_pass = perm_p_overall < 0.05

    if mw_pass and perm_pass:
        verdict = "SUPPORTED"
    elif mw_pass or perm_pass:
        verdict = "PARTIAL"
    else:
        verdict = "NOT_SUPPORTED"

    print(f"\n  Mann-Whitney test: {'PASS' if mw_pass else 'FAIL'}")
    print(f"  Permutation test:  {'PASS' if perm_pass else 'FAIL'}")
    print(f"  Verdict: {verdict}")

    # ---- Save results ----
    results = {
        'test': 'Frequency-Controlled Zone Exclusivity',
        'test_number': 11,
        'phase': 'MIDDLE_MATERIAL_SEMANTICS',
        'question': 'Does phase-exclusivity hold for middles with 3+ occurrences per folio?',
        'relationship_to_test_1': 'Stricter version of Test 1 (min_folio_occurrences raised from 2 to 3)',
        'n_folios': len(folio_groups),
        'n_tokens_analyzed': len(all_tokens),
        'n_middle_folio_pairs': len(middle_exclusivity),
        'rarity_threshold_folios': RARITY_THRESHOLD,
        'min_folio_occurrences': MIN_FOLIO_OCCURRENCES,
        'overall_zone_exclusive_rate': round(overall_rate, 4),
        'overall_exclusive_count': overall_exclusive_count,
        'rare_zone_exclusive_rate': round(rare_exclusive_rate, 4),
        'common_zone_exclusive_rate': round(common_exclusive_rate, 4),
        'rare_count': len(rare_records),
        'common_count': len(common_records),
        'rare_exclusive_count': rare_exclusive_count,
        'common_exclusive_count': common_exclusive_count,
        'mann_whitney_u': round(u_stat, 2) if u_stat is not None else None,
        'mann_whitney_p_value': float(f'{p_value_mw:.2e}') if p_value_mw is not None else None,
        'mann_whitney_p_value_str': f'{p_value_mw:.2e}' if p_value_mw is not None else None,
        'effect_size_d': round(effect_size_d, 4) if effect_size_d is not None else None,
        'permutation_test': {
            'n_permutations': N_PERMUTATIONS,
            'random_seed': RANDOM_SEED,
            'overall': {
                'observed_rate': round(overall_rate, 4),
                'permuted_mean': round(perm_mean_overall, 4),
                'permuted_std': round(
                    math.sqrt(sum((r - perm_mean_overall) ** 2 for r in permuted_overall_rates) / max(1, N_PERMUTATIONS - 1)), 4
                ),
                'p_value': round(perm_p_overall, 4),
                'exceeds_baseline': overall_rate > perm_mean_overall,
            },
            'rare': {
                'observed_rate': round(rare_exclusive_rate, 4),
                'permuted_mean': round(perm_mean_rare, 4),
                'p_value': round(perm_p_rare, 4),
            },
            'common': {
                'observed_rate': round(common_exclusive_rate, 4),
                'permuted_mean': round(perm_mean_common, 4),
                'p_value': round(perm_p_common, 4),
            },
        },
        'verdict': verdict,
        'verdict_criteria': {
            'mann_whitney_pass': mw_pass,
            'permutation_pass': perm_pass,
            'rule': 'SUPPORTED if both pass, PARTIAL if one passes, NOT_SUPPORTED if neither',
        },
        'zone_preference_all': dict(zone_preference),
        'zone_preference_rare': dict(rare_zone_pref),
        'zone_preference_common': dict(common_zone_pref),
        'per_folio_summary': per_folio_summary,
        'notes': (
            f"Frequency-controlled zone-exclusivity test. MIDDLEs must occur {MIN_FOLIO_OCCURRENCES}+ times "
            f"per folio to qualify (eliminates hapax inflation entirely). "
            f"Zone-exclusive = MIDDLE appears in exactly 1 of 3 zones (SETUP/PROCESS/FINISH). "
            f"Zones assigned by paragraph (3+ paras) or line-based 20/60/20 split (1-2 paras). "
            f"RARE = appears in <{RARITY_THRESHOLD} folios across corpus. "
            f"Two statistical tests: (1) Mann-Whitney U tests whether rare middles have higher "
            f"zone-exclusivity than common, (2) permutation test ({N_PERMUTATIONS} shuffles) tests "
            f"whether observed exclusivity exceeds random baseline."
        ),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / 'frequency_controlled_exclusivity.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
