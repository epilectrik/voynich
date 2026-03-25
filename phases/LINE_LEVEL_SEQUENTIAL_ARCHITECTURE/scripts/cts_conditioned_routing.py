"""
Phase 623: LINE_LEVEL_SEQUENTIAL_ARCHITECTURE -- Script 2: CTS-Conditioned Routing

Tests whether terminal-to-HEAD line-crossing routing (C1563) activates
only at strong closure boundaries, reconciling with C1728's null.

Hypothesis: Terminal-to-HEAD routing grammar activates only at strong
closure boundaries and is dormant at weak ones.

Method:
  1. Extract consecutive body-line pairs from paragraphs with 5+ body lines.
  2. Record CTS of line N, TERM of last token of line N, HEAD of first token
     of line N+1.
  3. Partition by CTS tercile (LOW/MED/HIGH), compute categorical MI per tercile.
  4. Position-conditioned MI: quintiles Q0-Q4 of body position.
  5. Specific routing enrichment for known pairs (r->a, h->t, y->k).
  6. Unconditional baseline to replicate C1728's null.
"""

import json
import math
import random
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from phases.LINE_LEVEL_SEQUENTIAL_ARCHITECTURE.scripts.shared import (
    build_corpus, RNG, N_PERM, RESULTS_DIR, round_floats,
)


# ============================================================
# Categorical MI (for discrete TERM/HEAD atoms)
# ============================================================

def categorical_mi(x_vals, y_vals):
    """
    Compute mutual information I(X;Y) in bits for categorical variables.
    Applies Miller-Madow bias correction.

    Parameters:
        x_vals: list of hashable category labels
        y_vals: list of hashable category labels (same length)

    Returns:
        MI in bits (non-negative after bias correction)
    """
    n = len(x_vals)
    if n < 10 or len(y_vals) != n:
        return 0.0

    joint = Counter()
    mx = Counter()
    my = Counter()
    for xi, yi in zip(x_vals, y_vals):
        joint[(xi, yi)] += 1
        mx[xi] += 1
        my[yi] += 1

    mi = 0.0
    for (xi, yi), nxy in joint.items():
        if nxy > 0:
            pxy = nxy / n
            px = mx[xi] / n
            py = my[yi] / n
            if px > 0 and py > 0:
                mi += pxy * math.log2(pxy / (px * py))

    # Miller-Madow bias correction
    k_joint = sum(1 for v in joint.values() if v > 0)
    correction = (k_joint - 1) / (2 * n * math.log(2))
    mi_corrected = max(0.0, mi - correction)

    return mi_corrected


def categorical_permutation_test(x_vals, y_vals, group_labels, n_perm=N_PERM,
                                  rng=None):
    """
    Permutation test for categorical MI with paragraph-level shuffling.

    Shuffles line ordering within each paragraph (identified by group_labels),
    then re-extracts (TERM_last, HEAD_first) pairs from the shuffled order.

    Parameters:
        x_vals: list of TERM atoms (one per line pair)
        y_vals: list of HEAD atoms (one per line pair)
        group_labels: list of paragraph IDs (one per line pair)
        n_perm: number of permutations
        rng: random.Random instance

    Returns:
        dict with observed, null_mean, null_std, z_score, p_value
    """
    if rng is None:
        rng = RNG

    observed = categorical_mi(x_vals, y_vals)

    # For paragraph-shuffled null, we need the raw line data grouped by paragraph.
    # This is handled by the caller passing in paragraph-grouped data.
    # Here we do a simple shuffle of y within groups as an approximation.
    null_values = []
    y_arr = list(y_vals)
    group_arr = list(group_labels)

    # Build group indices
    group_indices = defaultdict(list)
    for i, g in enumerate(group_arr):
        group_indices[g].append(i)

    for _ in range(n_perm):
        y_shuffled = list(y_arr)
        # Shuffle y values within each paragraph group
        for g, indices in group_indices.items():
            vals = [y_arr[i] for i in indices]
            rng.shuffle(vals)
            for idx, val in zip(indices, vals):
                y_shuffled[idx] = val
        null_mi = categorical_mi(x_vals, y_shuffled)
        null_values.append(null_mi)

    null_mean = sum(null_values) / len(null_values) if null_values else 0.0
    null_std = (sum((v - null_mean) ** 2 for v in null_values)
                / len(null_values)) ** 0.5 if null_values else 0.0

    z_score = (observed - null_mean) / null_std if null_std > 0 else 0.0
    p_value = sum(1 for v in null_values if v >= observed) / len(null_values) if null_values else 1.0

    return {
        'mi': round(observed, 6),
        'null_mean': round(null_mean, 6),
        'null_std': round(null_std, 6),
        'z_score': round(z_score, 3),
        'p_value': round(p_value, 6),
    }


# ============================================================
# Full paragraph-shuffle permutation test
# ============================================================

def paragraph_shuffle_permutation_test(para_lines_map, n_perm=N_PERM, rng=None):
    """
    Proper paragraph-shuffled null: shuffle body line ordering within each
    paragraph, re-extract (TERM_last_N, HEAD_first_N+1) pairs, compute MI.

    Parameters:
        para_lines_map: dict of para_id -> list of line dicts (body lines in order)

    Returns:
        list of null MI values
    """
    if rng is None:
        rng = RNG

    null_values = []
    for _ in range(n_perm):
        x_perm = []
        y_perm = []
        for para_id, lines in para_lines_map.items():
            if len(lines) < 2:
                continue
            shuffled = list(lines)
            rng.shuffle(shuffled)
            for i in range(len(shuffled) - 1):
                line_n = shuffled[i]
                line_n1 = shuffled[i + 1]
                term_last = _get_term_last(line_n)
                head_first = _get_head_first(line_n1)
                if term_last is not None and head_first is not None:
                    x_perm.append(term_last)
                    y_perm.append(head_first)
        if len(x_perm) >= 10:
            null_values.append(categorical_mi(x_perm, y_perm))
        else:
            null_values.append(0.0)

    return null_values


# ============================================================
# Line pair extraction helpers
# ============================================================

def _get_term_last(line_dict):
    """Get TERM atom of the last token in a line."""
    tokens = line_dict['tokens']
    if not tokens:
        return None
    return tokens[-1].get('term', 'bare')


def _get_head_first(line_dict):
    """Get HEAD atom of the first token in a line."""
    tokens = line_dict['tokens']
    if not tokens:
        return None
    return tokens[0].get('head', '')


def extract_line_pairs(corpus):
    """
    Extract consecutive body-line pairs from paragraphs with 5+ body lines.

    Returns:
        list of dicts with keys: para_id, folio, cts, term_last, head_first,
                                  body_pos (0-indexed position of line N in body)
        dict of para_id -> list of body line dicts (for paragraph-shuffle null)
    """
    pairs = []
    para_lines_map = {}

    for folio, fdata in corpus.items():
        for para in fdata['paragraphs']:
            body = para['body_lines']
            if len(body) < 5:
                continue

            para_key = f"{folio}_{para['id']}"
            para_lines_map[para_key] = body

            for i in range(len(body) - 1):
                line_n = body[i]
                line_n1 = body[i + 1]

                term_last = _get_term_last(line_n)
                head_first = _get_head_first(line_n1)

                if term_last is None or head_first is None:
                    continue

                pairs.append({
                    'para_id': para_key,
                    'folio': folio,
                    'cts': line_n['cts'],
                    'term_last': term_last,
                    'head_first': head_first,
                    'body_pos': i,
                    'body_len': len(body),
                })

    return pairs, para_lines_map


# ============================================================
# CTS tercile partitioning
# ============================================================

def partition_terciles(pairs):
    """
    Partition pairs into LOW/MED/HIGH CTS terciles based on line N's CTS.

    Returns:
        dict of tercile_name -> list of pairs
        dict of tercile_name -> (lower_bound, upper_bound)
    """
    cts_values = sorted(set(p['cts'] for p in pairs))
    all_cts = sorted(p['cts'] for p in pairs)
    n = len(all_cts)

    # Tercile boundaries
    t1 = all_cts[n // 3]
    t2 = all_cts[2 * n // 3]

    terciles = {'LOW': [], 'MED': [], 'HIGH': []}
    bounds = {
        'LOW': (all_cts[0], t1),
        'MED': (t1, t2),
        'HIGH': (t2, all_cts[-1]),
    }

    for p in pairs:
        if p['cts'] <= t1:
            terciles['LOW'].append(p)
        elif p['cts'] <= t2:
            terciles['MED'].append(p)
        else:
            terciles['HIGH'].append(p)

    return terciles, bounds


# ============================================================
# Position quintile assignment
# ============================================================

def assign_position_quintile(pairs):
    """
    Assign each pair a quintile Q0-Q4 based on body_pos / body_len.

    body_pos is the position of line N (0-indexed) within the paragraph body.
    Quintile is computed as floor(5 * body_pos / (body_len - 1)) clamped to 0-4.
    """
    for p in pairs:
        if p['body_len'] <= 1:
            p['quintile'] = 'Q0'
        else:
            q = int(5 * p['body_pos'] / (p['body_len'] - 1))
            q = min(q, 4)
            p['quintile'] = f'Q{q}'


# ============================================================
# Routing enrichment
# ============================================================

def compute_routing_enrichment(pairs_subset):
    """
    For known routing pairs (r->a, h->t, y->k), compute enrichment ratio:
    observed / expected_under_independence.

    Returns:
        dict with r_to_a, h_to_t, y_to_k enrichment ratios
    """
    n = len(pairs_subset)
    if n < 10:
        return {'r_to_a': None, 'h_to_t': None, 'y_to_k': None}

    term_counts = Counter(p['term_last'] for p in pairs_subset)
    head_counts = Counter(p['head_first'] for p in pairs_subset)
    joint_counts = Counter((p['term_last'], p['head_first']) for p in pairs_subset)

    result = {}
    for term, head, key in [('r', 'a', 'r_to_a'), ('h', 't', 'h_to_t'), ('y', 'k', 'y_to_k')]:
        p_term = term_counts.get(term, 0) / n
        p_head = head_counts.get(head, 0) / n
        expected = p_term * p_head
        observed = joint_counts.get((term, head), 0) / n

        if expected > 0:
            result[key] = round(observed / expected, 3)
        else:
            result[key] = None

    return result


# ============================================================
# Main
# ============================================================

def main():
    print('=' * 60)
    print('Phase 623 Script 2: CTS-Conditioned Terminal Routing')
    print('=' * 60)

    # ----------------------------------------------------------
    # Step 1: Build corpus and extract pairs
    # ----------------------------------------------------------
    print('\n[1] Building corpus...')
    corpus = build_corpus()
    n_folios = len(corpus)
    n_paras = sum(len(fdata['paragraphs']) for fdata in corpus.values())
    print(f'    Corpus: {n_folios} folios, {n_paras} paragraphs')

    pairs, para_lines_map = extract_line_pairs(corpus)
    n_pairs = len(pairs)
    n_eligible_paras = len(para_lines_map)
    print(f'    Eligible paragraphs (5+ body lines): {n_eligible_paras}')
    print(f'    Consecutive body-line pairs: {n_pairs}')

    if n_pairs < 50:
        print('ERROR: Insufficient pairs for analysis.')
        return

    # ----------------------------------------------------------
    # Step 2: Unconditional baseline (should replicate C1728 null)
    # ----------------------------------------------------------
    print('\n[2] Unconditional TERM->HEAD MI (baseline)...')
    x_all = [p['term_last'] for p in pairs]
    y_all = [p['head_first'] for p in pairs]
    g_all = [p['para_id'] for p in pairs]

    observed_all = categorical_mi(x_all, y_all)
    null_all = paragraph_shuffle_permutation_test(para_lines_map, n_perm=N_PERM, rng=RNG)
    null_mean_all = sum(null_all) / len(null_all) if null_all else 0.0
    null_std_all = (sum((v - null_mean_all) ** 2 for v in null_all)
                    / len(null_all)) ** 0.5 if null_all else 0.0
    z_all = (observed_all - null_mean_all) / null_std_all if null_std_all > 0 else 0.0
    p_all = sum(1 for v in null_all if v >= observed_all) / len(null_all) if null_all else 1.0

    unconditional = {
        'n': n_pairs,
        'mi': round(observed_all, 6),
        'null_mean': round(null_mean_all, 6),
        'null_std': round(null_std_all, 6),
        'z_score': round(z_all, 3),
        'p_value': round(p_all, 6),
    }
    print(f'    MI = {unconditional["mi"]:.6f} bits, z = {z_all:.3f}, p = {p_all:.4f}')

    # ----------------------------------------------------------
    # Step 3: CTS tercile partitioning + per-tercile MI
    # ----------------------------------------------------------
    print('\n[3] CTS tercile analysis...')
    terciles, bounds = partition_terciles(pairs)
    print(f'    Tercile sizes: LOW={len(terciles["LOW"])}, '
          f'MED={len(terciles["MED"])}, HIGH={len(terciles["HIGH"])}')
    print(f'    CTS bounds: LOW=[{bounds["LOW"][0]:.3f}, {bounds["LOW"][1]:.3f}], '
          f'MED=({bounds["MED"][0]:.3f}, {bounds["MED"][1]:.3f}], '
          f'HIGH=({bounds["HIGH"][0]:.3f}, {bounds["HIGH"][1]:.3f}]')

    by_cts_tercile = {}
    for tercile_name in ['LOW', 'MED', 'HIGH']:
        subset = terciles[tercile_name]
        n_sub = len(subset)
        if n_sub < 10:
            by_cts_tercile[tercile_name] = {
                'n': n_sub, 'mi': 0.0, 'z_score': 0.0, 'p_value': 1.0,
            }
            continue

        x_sub = [p['term_last'] for p in subset]
        y_sub = [p['head_first'] for p in subset]

        obs_mi = categorical_mi(x_sub, y_sub)

        # Build paragraph-to-lines map for this tercile's paragraphs
        # Filter para_lines_map to lines whose CTS falls in this tercile
        # For proper null: shuffle all body lines in each paragraph, then
        # re-extract pairs, then filter to CTS tercile
        # Simpler approach: shuffle within paragraph group labels of this subset
        g_sub = [p['para_id'] for p in subset]

        # Use group-shuffled permutation for tercile
        test_result = categorical_permutation_test(
            x_sub, y_sub, g_sub, n_perm=N_PERM, rng=RNG
        )
        test_result['n'] = n_sub

        by_cts_tercile[tercile_name] = test_result
        print(f'    {tercile_name}: n={n_sub}, MI={test_result["mi"]:.6f}, '
              f'z={test_result["z_score"]:.3f}, p={test_result["p_value"]:.4f}')

    # ----------------------------------------------------------
    # Step 4: Position-conditioned MI (Q0, Q2, Q4)
    # ----------------------------------------------------------
    print('\n[4] Position-conditioned MI...')
    assign_position_quintile(pairs)

    by_position = {}
    for qname in ['Q0', 'Q1', 'Q2', 'Q3', 'Q4']:
        subset = [p for p in pairs if p['quintile'] == qname]
        n_sub = len(subset)
        if n_sub < 10:
            by_position[qname] = {
                'n': n_sub, 'mi': 0.0, 'z_score': 0.0, 'p_value': 1.0,
            }
            continue

        x_sub = [p['term_last'] for p in subset]
        y_sub = [p['head_first'] for p in subset]
        g_sub = [p['para_id'] for p in subset]

        test_result = categorical_permutation_test(
            x_sub, y_sub, g_sub, n_perm=N_PERM, rng=RNG
        )
        test_result['n'] = n_sub

        by_position[qname] = test_result
        print(f'    {qname}: n={n_sub}, MI={test_result["mi"]:.6f}, '
              f'z={test_result["z_score"]:.3f}, p={test_result["p_value"]:.4f}')

    # ----------------------------------------------------------
    # Step 5: Specific routing enrichment per CTS tercile
    # ----------------------------------------------------------
    print('\n[5] Routing enrichment (r->a, h->t, y->k) per CTS tercile...')
    routing_enrichment = {}
    for tercile_name in ['LOW', 'MED', 'HIGH']:
        subset = terciles[tercile_name]
        enrichment = compute_routing_enrichment(subset)
        routing_enrichment[tercile_name] = enrichment
        print(f'    {tercile_name}: r->a={enrichment["r_to_a"]}, '
              f'h->t={enrichment["h_to_t"]}, y->k={enrichment["y_to_k"]}')

    # Also compute overall enrichment
    overall_enrichment = compute_routing_enrichment(pairs)
    routing_enrichment['OVERALL'] = overall_enrichment
    print(f'    OVERALL: r->a={overall_enrichment["r_to_a"]}, '
          f'h->t={overall_enrichment["h_to_t"]}, y->k={overall_enrichment["y_to_k"]}')

    # ----------------------------------------------------------
    # Step 6: Distribution summaries
    # ----------------------------------------------------------
    print('\n[6] Distribution summaries...')
    term_dist = Counter(p['term_last'] for p in pairs)
    head_dist = Counter(p['head_first'] for p in pairs)
    print(f'    TERM distribution: {dict(term_dist.most_common())}')
    print(f'    HEAD distribution: {dict(head_dist.most_common())}')

    # CTS distribution stats
    cts_values = [p['cts'] for p in pairs]
    cts_mean = sum(cts_values) / len(cts_values)
    cts_std = (sum((v - cts_mean) ** 2 for v in cts_values) / len(cts_values)) ** 0.5
    print(f'    CTS: mean={cts_mean:.3f}, std={cts_std:.3f}, '
          f'min={min(cts_values):.3f}, max={max(cts_values):.3f}')

    # ----------------------------------------------------------
    # Step 7: Verdict
    # ----------------------------------------------------------
    print('\n[7] Verdict...')

    # Check if HIGH tercile shows significant MI while LOW does not
    high_sig = (by_cts_tercile['HIGH']['p_value'] < 0.01
                and by_cts_tercile['HIGH']['z_score'] > 2.0)
    low_null = by_cts_tercile['LOW']['p_value'] > 0.05
    med_intermediate = (by_cts_tercile['MED']['mi']
                        <= by_cts_tercile['HIGH']['mi'])

    # Check monotonic MI increase across terciles
    mi_values = [by_cts_tercile[t]['mi'] for t in ['LOW', 'MED', 'HIGH']]
    monotonic = mi_values[0] <= mi_values[1] <= mi_values[2]

    # Check routing enrichment gradient
    high_routing_active = False
    if routing_enrichment['HIGH']['r_to_a'] is not None:
        high_routing_active = (
            routing_enrichment['HIGH']['r_to_a'] > 1.5
            or routing_enrichment['HIGH']['h_to_t'] > 1.5
            or routing_enrichment['HIGH']['y_to_k'] > 1.5
        )

    if high_sig and low_null and monotonic:
        verdict = 'CTS_MODULATED_ROUTING'
        verdict_detail = (
            f'HIGH-CTS tercile shows MI={by_cts_tercile["HIGH"]["mi"]:.6f} bits '
            f'(z={by_cts_tercile["HIGH"]["z_score"]:.1f}, '
            f'p={by_cts_tercile["HIGH"]["p_value"]:.4f}). '
            f'LOW-CTS tercile is null (p={by_cts_tercile["LOW"]["p_value"]:.4f}). '
            f'Monotonic MI gradient across CTS terciles confirms '
            f'closure-gated routing hypothesis.'
        )
    elif high_sig:
        verdict = 'CTS_PARTIAL_MODULATION'
        verdict_detail = (
            f'HIGH-CTS tercile shows significant MI but pattern is not cleanly monotonic. '
            f'MI values: LOW={mi_values[0]:.6f}, MED={mi_values[1]:.6f}, HIGH={mi_values[2]:.6f}.'
        )
    else:
        verdict = 'NO_CTS_EFFECT'
        verdict_detail = (
            f'No CTS tercile shows significant TERM->HEAD MI. '
            f'Terminal routing is strictly token-local; '
            f'no line-level signal even at strong closure boundaries. '
            f'C1563 (token-level) and C1728 (line-level null) are '
            f'genuinely orthogonal scales.'
        )

    print(f'    Verdict: {verdict}')
    print(f'    Detail: {verdict_detail}')

    # ----------------------------------------------------------
    # Step 8: Predictions
    # ----------------------------------------------------------
    predictions = {
        'P10_cts_modulation': verdict == 'CTS_MODULATED_ROUTING',
        'c1728_null_replicated': unconditional['p_value'] > 0.05,
        'monotonic_mi_gradient': monotonic,
        'high_routing_enrichment': high_routing_active,
    }

    # ----------------------------------------------------------
    # Assemble results
    # ----------------------------------------------------------
    results = {
        'phase': 623,
        'name': 'cts_conditioned_routing',
        'n_pairs': n_pairs,
        'n_eligible_paragraphs': n_eligible_paras,
        'unconditional': unconditional,
        'by_cts_tercile': by_cts_tercile,
        'cts_bounds': {k: {'low': v[0], 'high': v[1]}
                       for k, v in bounds.items()},
        'by_position': by_position,
        'routing_enrichment': routing_enrichment,
        'distributions': {
            'term': dict(term_dist.most_common()),
            'head': dict(head_dist.most_common()),
            'cts_mean': round(cts_mean, 4),
            'cts_std': round(cts_std, 4),
        },
        'verdict': verdict,
        'verdict_detail': verdict_detail,
        'predictions': predictions,
    }

    results = round_floats(results)

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'cts_conditioned_routing.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f'\n    Results saved to {out_path}')
    print('=' * 60)
    print('DONE')
    print('=' * 60)


if __name__ == '__main__':
    main()
