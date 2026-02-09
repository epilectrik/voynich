"""
08_null_permutation_test.py - Null Permutation Test

Phase: MIDDLE_MATERIAL_SEMANTICS
Test 8: Is the observed phase-exclusivity statistically significant vs random?

Method:
1. Load Currier B tokens (H transcriber, labels excluded, uncertain excluded)
2. Extract MIDDLEs via canonical Morphology
3. For each B folio, assign zones: SETUP/PROCESS/FINISH
   - 3+ paragraphs: first=SETUP, last=FINISH, middle=PROCESS
   - 1-2 paragraphs: line-based 20/60/20 split
4. Compute zone-exclusive rate for rare middles (<15 folios, 2+ per folio)
5. Permutation null: For each folio, shuffle zone assignments (1000 times),
   recompute zone-exclusive rate each time
6. p-value: fraction of permutation rates >= observed
7. Global p-value: compare corpus-wide observed rate vs permutation distribution

Expected: p < 0.05
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')

import json
import random
import csv
from collections import defaultdict, Counter
from pathlib import Path
from voynich import Transcript, Morphology
import math
import numpy as np

RESULTS_DIR = Path('C:/git/voynich/phases/MIDDLE_MATERIAL_SEMANTICS/results')
N_PERMUTATIONS = 1000
RARITY_THRESHOLD = 15
MIN_FOLIO_OCCURRENCES = 2


# ============================================================
# DATA LOADING (matches Test 1 exactly)
# ============================================================
def load_b_tokens():
    """Load all Currier B tokens with line/paragraph metadata."""
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for tok in tx.currier_b():
        # Text tokens only (P-prefixed placements)
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
# PARAGRAPH BOUNDARY DETECTION (matches Test 1 exactly)
# ============================================================
def assign_paragraphs(folio_tokens):
    """
    Assign paragraph numbers to tokens within a folio.
    par_initial==True on a line-initial token signals paragraph start.
    """
    current_para = 0
    para_assignments = []

    for tok in folio_tokens:
        if tok['par_initial'] and tok['line_initial']:
            current_para += 1
        para_assignments.append(current_para)

    return para_assignments


# ============================================================
# ZONE ASSIGNMENT (matches Test 1 exactly)
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
# ZONE-EXCLUSIVE RATE COMPUTATION
# ============================================================
def compute_zone_exclusive_rate(middles_with_zones, middle_folio_count,
                                rarity_threshold, min_occurrences):
    """
    Compute zone-exclusive rate for rare middles on a single folio.

    Args:
        middles_with_zones: list of (middle, zone) tuples for one folio
        middle_folio_count: dict of middle -> corpus-wide folio count
        rarity_threshold: max folios for a middle to be "rare"
        min_occurrences: minimum occurrences per folio to count

    Returns:
        (rare_exclusive, rare_total, all_exclusive, all_total)
    """
    # Count each middle's zone set and frequency on this folio
    middle_zone_sets = defaultdict(set)
    middle_freq = Counter()

    for mid, zone in middles_with_zones:
        middle_zone_sets[mid].add(zone)
        middle_freq[mid] += 1

    rare_exclusive = 0
    rare_total = 0
    all_exclusive = 0
    all_total = 0

    for mid, freq in middle_freq.items():
        if freq < min_occurrences:
            continue

        is_exclusive = len(middle_zone_sets[mid]) == 1
        folio_count = middle_folio_count.get(mid, 0)

        all_total += 1
        if is_exclusive:
            all_exclusive += 1

        if folio_count < rarity_threshold:
            rare_total += 1
            if is_exclusive:
                rare_exclusive += 1

    return rare_exclusive, rare_total, all_exclusive, all_total


# ============================================================
# MAIN ANALYSIS
# ============================================================
def main():
    random.seed(42)
    np.random.seed(42)

    print("Loading Currier B tokens...")
    all_tokens = load_b_tokens()
    print(f"  Total B text tokens with valid MIDDLE: {len(all_tokens)}")

    # Group by folio
    folio_groups = defaultdict(list)
    for tok in all_tokens:
        folio_groups[tok['folio']].append(tok)

    print(f"  B folios: {len(folio_groups)}")

    # Pre-compute corpus-wide MIDDLE folio counts
    middle_folios = defaultdict(set)
    for tok in all_tokens:
        middle_folios[tok['middle']].add(tok['folio'])
    middle_folio_count = {m: len(fs) for m, fs in middle_folios.items()}

    # ---- Step 1: Compute observed zone-exclusive rates per folio ----
    print("\nComputing observed zone-exclusive rates...")

    # Store per-folio data for permutation
    folio_data = {}  # folio -> { middles: [...], zones: [...], obs_stats }

    # Global accumulators for observed
    obs_rare_exclusive_total = 0
    obs_rare_total_total = 0
    obs_all_exclusive_total = 0
    obs_all_total_total = 0

    for folio in sorted(folio_groups.keys()):
        ftokens = folio_groups[folio]
        para_assignments = assign_paragraphs(ftokens)
        zones = assign_zones(ftokens, para_assignments)

        middles = [tok['middle'] for tok in ftokens]
        middles_with_zones = list(zip(middles, zones))

        rare_exc, rare_tot, all_exc, all_tot = compute_zone_exclusive_rate(
            middles_with_zones, middle_folio_count,
            RARITY_THRESHOLD, MIN_FOLIO_OCCURRENCES
        )

        obs_rare_exclusive_total += rare_exc
        obs_rare_total_total += rare_tot
        obs_all_exclusive_total += all_exc
        obs_all_total_total += all_tot

        folio_data[folio] = {
            'middles': middles,
            'zones': zones,
            'obs_rare_exclusive': rare_exc,
            'obs_rare_total': rare_tot,
            'obs_all_exclusive': all_exc,
            'obs_all_total': all_tot,
        }

    # Observed corpus-wide rates
    obs_rare_rate = (obs_rare_exclusive_total / obs_rare_total_total
                     if obs_rare_total_total > 0 else 0.0)
    obs_all_rate = (obs_all_exclusive_total / obs_all_total_total
                    if obs_all_total_total > 0 else 0.0)

    print(f"  Observed rare zone-exclusive: {obs_rare_exclusive_total}/{obs_rare_total_total} = {obs_rare_rate:.4f}")
    print(f"  Observed all zone-exclusive:  {obs_all_exclusive_total}/{obs_all_total_total} = {obs_all_rate:.4f}")

    # ---- Step 2: Permutation test ----
    print(f"\nRunning {N_PERMUTATIONS} permutations...")

    perm_rare_rates = []
    perm_all_rates = []

    # Per-folio permutation p-value accumulators
    per_folio_perm_exceed_rare = defaultdict(int)
    per_folio_perm_exceed_all = defaultdict(int)

    for perm_i in range(N_PERMUTATIONS):
        if (perm_i + 1) % 200 == 0:
            print(f"  Permutation {perm_i + 1}/{N_PERMUTATIONS}...")

        perm_rare_exc_total = 0
        perm_rare_tot_total = 0
        perm_all_exc_total = 0
        perm_all_tot_total = 0

        for folio, fd in folio_data.items():
            middles = fd['middles']
            zones = fd['zones']

            # Shuffle zones (keep same zone sizes, randomize assignment)
            shuffled_zones = list(zones)
            random.shuffle(shuffled_zones)

            middles_with_zones = list(zip(middles, shuffled_zones))

            rare_exc, rare_tot, all_exc, all_tot = compute_zone_exclusive_rate(
                middles_with_zones, middle_folio_count,
                RARITY_THRESHOLD, MIN_FOLIO_OCCURRENCES
            )

            perm_rare_exc_total += rare_exc
            perm_rare_tot_total += rare_tot
            perm_all_exc_total += all_exc
            perm_all_tot_total += all_tot

            # Track per-folio exceedance for rare
            if fd['obs_rare_total'] > 0 and rare_tot > 0:
                perm_folio_rare_rate = rare_exc / rare_tot
                obs_folio_rare_rate = fd['obs_rare_exclusive'] / fd['obs_rare_total']
                if perm_folio_rare_rate >= obs_folio_rare_rate:
                    per_folio_perm_exceed_rare[folio] += 1

            # Track per-folio exceedance for all middles
            if fd['obs_all_total'] > 0 and all_tot > 0:
                perm_folio_all_rate = all_exc / all_tot
                obs_folio_all_rate = fd['obs_all_exclusive'] / fd['obs_all_total']
                if perm_folio_all_rate >= obs_folio_all_rate:
                    per_folio_perm_exceed_all[folio] += 1

        perm_rare_rate = (perm_rare_exc_total / perm_rare_tot_total
                          if perm_rare_tot_total > 0 else 0.0)
        perm_all_rate = (perm_all_exc_total / perm_all_tot_total
                         if perm_all_tot_total > 0 else 0.0)

        perm_rare_rates.append(perm_rare_rate)
        perm_all_rates.append(perm_all_rate)

    # ---- Step 3: Compute p-values ----
    perm_rare_rates = np.array(perm_rare_rates)
    perm_all_rates = np.array(perm_all_rates)

    # Global p-value: fraction of permutations where rate >= observed
    p_value_rare = float(np.mean(perm_rare_rates >= obs_rare_rate))
    p_value_all = float(np.mean(perm_all_rates >= obs_all_rate))

    # Permutation distribution statistics
    perm_rare_mean = float(np.mean(perm_rare_rates))
    perm_rare_sd = float(np.std(perm_rare_rates, ddof=1))
    perm_all_mean = float(np.mean(perm_all_rates))
    perm_all_sd = float(np.std(perm_all_rates, ddof=1))

    # Z-score (observed vs permutation distribution)
    z_score_rare = ((obs_rare_rate - perm_rare_mean) / perm_rare_sd
                    if perm_rare_sd > 0 else float('inf'))
    z_score_all = ((obs_all_rate - perm_all_mean) / perm_all_sd
                   if perm_all_sd > 0 else float('inf'))

    print(f"\n=== Permutation Test Results ===")
    print(f"\n  RARE middles (<{RARITY_THRESHOLD} folios):")
    print(f"    Observed rate:    {obs_rare_rate:.4f}")
    print(f"    Permutation mean: {perm_rare_mean:.4f}")
    print(f"    Permutation SD:   {perm_rare_sd:.4f}")
    print(f"    Z-score:          {z_score_rare:.2f}")
    print(f"    p-value:          {p_value_rare:.4f}")

    print(f"\n  ALL middles:")
    print(f"    Observed rate:    {obs_all_rate:.4f}")
    print(f"    Permutation mean: {perm_all_mean:.4f}")
    print(f"    Permutation SD:   {perm_all_sd:.4f}")
    print(f"    Z-score:          {z_score_all:.2f}")
    print(f"    p-value:          {p_value_all:.4f}")

    # ---- Step 4: Per-folio p-values ----
    per_folio_results = {}
    n_folio_significant_rare = 0
    n_folio_tested_rare = 0
    n_folio_significant_all = 0
    n_folio_tested_all = 0

    for folio in sorted(folio_data.keys()):
        fd = folio_data[folio]
        folio_result = {
            'obs_rare_exclusive': fd['obs_rare_exclusive'],
            'obs_rare_total': fd['obs_rare_total'],
            'obs_all_exclusive': fd['obs_all_exclusive'],
            'obs_all_total': fd['obs_all_total'],
        }

        # Rare p-value for this folio
        if fd['obs_rare_total'] > 0:
            folio_p_rare = per_folio_perm_exceed_rare[folio] / N_PERMUTATIONS
            folio_result['p_value_rare'] = round(folio_p_rare, 4)
            folio_result['obs_rare_rate'] = round(
                fd['obs_rare_exclusive'] / fd['obs_rare_total'], 4)
            n_folio_tested_rare += 1
            if folio_p_rare < 0.05:
                n_folio_significant_rare += 1
        else:
            folio_result['p_value_rare'] = None
            folio_result['obs_rare_rate'] = None

        # All-middle p-value for this folio
        if fd['obs_all_total'] > 0:
            folio_p_all = per_folio_perm_exceed_all[folio] / N_PERMUTATIONS
            folio_result['p_value_all'] = round(folio_p_all, 4)
            folio_result['obs_all_rate'] = round(
                fd['obs_all_exclusive'] / fd['obs_all_total'], 4)
            n_folio_tested_all += 1
            if folio_p_all < 0.05:
                n_folio_significant_all += 1
        else:
            folio_result['p_value_all'] = None
            folio_result['obs_all_rate'] = None

        per_folio_results[folio] = folio_result

    pct_folio_sig_rare = (100 * n_folio_significant_rare / n_folio_tested_rare
                          if n_folio_tested_rare > 0 else 0.0)
    pct_folio_sig_all = (100 * n_folio_significant_all / n_folio_tested_all
                         if n_folio_tested_all > 0 else 0.0)

    print(f"\n  Per-folio significance (p < 0.05):")
    print(f"    Rare: {n_folio_significant_rare}/{n_folio_tested_rare} folios ({pct_folio_sig_rare:.1f}%)")
    print(f"    All:  {n_folio_significant_all}/{n_folio_tested_all} folios ({pct_folio_sig_all:.1f}%)")

    # ---- Step 5: Verdict ----
    # SUPPORTED if global p-value for rare middles < 0.05
    if p_value_rare < 0.05:
        verdict = "SUPPORTED"
    else:
        verdict = "NOT_SUPPORTED"

    print(f"\n  Verdict: {verdict}")

    # ---- Step 6: Save results ----
    results = {
        'test': 'Null Permutation Test',
        'n_folios': len(folio_groups),
        'n_tokens_analyzed': len(all_tokens),
        'n_permutations': N_PERMUTATIONS,
        'rarity_threshold_folios': RARITY_THRESHOLD,
        'min_folio_occurrences': MIN_FOLIO_OCCURRENCES,
        'rare_middles': {
            'observed_rate': round(obs_rare_rate, 4),
            'observed_exclusive': obs_rare_exclusive_total,
            'observed_total': obs_rare_total_total,
            'permutation_mean': round(perm_rare_mean, 4),
            'permutation_sd': round(perm_rare_sd, 4),
            'z_score': round(z_score_rare, 4) if not math.isinf(z_score_rare) else None,
            'p_value': round(p_value_rare, 4),
        },
        'all_middles': {
            'observed_rate': round(obs_all_rate, 4),
            'observed_exclusive': obs_all_exclusive_total,
            'observed_total': obs_all_total_total,
            'permutation_mean': round(perm_all_mean, 4),
            'permutation_sd': round(perm_all_sd, 4),
            'z_score': round(z_score_all, 4) if not math.isinf(z_score_all) else None,
            'p_value': round(p_value_all, 4),
        },
        'per_folio_significance': {
            'rare_tested': n_folio_tested_rare,
            'rare_significant': n_folio_significant_rare,
            'rare_pct_significant': round(pct_folio_sig_rare, 2),
            'all_tested': n_folio_tested_all,
            'all_significant': n_folio_significant_all,
            'all_pct_significant': round(pct_folio_sig_all, 2),
        },
        'verdict': verdict,
        'per_folio_detail': per_folio_results,
        'notes': (
            f"Permutation null model: for each folio, zone assignments are shuffled "
            f"(keeping zone sizes fixed) {N_PERMUTATIONS} times. Zone-exclusive rate "
            f"is recomputed each time. p-value = fraction of permutations where "
            f"zone-exclusive rate >= observed. RARE = MIDDLE appears in <{RARITY_THRESHOLD} "
            f"folios. Hapax middles ({MIN_FOLIO_OCCURRENCES-1} occurrence per folio) excluded. "
            f"Zones: SETUP (first paragraph), PROCESS (middle), FINISH (final paragraph). "
            f"For folios with 1-2 paragraphs, line-based 20/60/20 split used."
        ),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / 'null_permutation_test.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
