"""
T1: Conditional MI Decomposition
=================================
Phase: PP_INFORMATION_DECOMPOSITION

Decomposes the information content of PP tokens into PREFIX and MIDDLE
contributions using conditional mutual information.

Chain rule:
  I(PP; Y) = I(MIDDLE; Y) + I(PREFIX; Y | MIDDLE)
           = I(PREFIX; Y) + I(MIDDLE; Y | PREFIX)

Where:
  I(PREFIX; Y | MIDDLE) = PREFIX's unique contribution (given MIDDLE)
  I(MIDDLE; Y | PREFIX) = MIDDLE's unique contribution (given PREFIX)
  Redundancy = I(PREFIX; Y) + I(MIDDLE; Y) - I(PP; Y)
    > 0 means overlapping information
    < 0 means synergy (together they tell more than the sum)

Target variables:
  1. Next-MIDDLE    — bigram transition prediction within line
  2. SUFFIX         — suffix identity
  3. REGIME         — folio regime (4 regimes)
  4. POSITION       — line position bucket (initial / mid / final)

Permutation null: Shuffle PREFIX labels within each MIDDLE to destroy
PREFIX-target association while preserving MIDDLE-target.

Output: t1_conditional_mi_decomposition.json
"""

import sys
import json
import functools
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

MIN_PP_COUNT = 5       # Minimum tokens for a (PREFIX, MIDDLE) pair
N_PERMS = 2000         # Permutation iterations for null distribution


def mi_plugin(joint_counts):
    """Compute MI from a 2D contingency table (numpy array).
    Returns MI in bits with Miller-Madow bias correction."""
    N = joint_counts.sum()
    if N == 0:
        return 0.0

    # Marginals
    px = joint_counts.sum(axis=1) / N
    py = joint_counts.sum(axis=0) / N
    pxy = joint_counts / N

    mi = 0.0
    for i in range(pxy.shape[0]):
        for j in range(pxy.shape[1]):
            if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += pxy[i, j] * np.log2(pxy[i, j] / (px[i] * py[j]))

    # Miller-Madow correction: subtract (|X|-1)(|Y|-1) / (2*N*ln2)
    nx = np.sum(px > 0)
    ny = np.sum(py > 0)
    correction = (nx - 1) * (ny - 1) / (2 * N * np.log(2))

    return max(0.0, mi - correction)


def build_contingency(x_labels, y_labels, x_vocab, y_vocab):
    """Build contingency table from parallel label arrays."""
    x_idx = {v: i for i, v in enumerate(x_vocab)}
    y_idx = {v: i for i, v in enumerate(y_vocab)}
    table = np.zeros((len(x_vocab), len(y_vocab)), dtype=float)
    for xi, yi in zip(x_labels, y_labels):
        if xi in x_idx and yi in y_idx:
            table[x_idx[xi], y_idx[yi]] += 1
    return table


def entropy_plugin(counts):
    """Compute entropy in bits from a 1D count array."""
    N = counts.sum()
    if N == 0:
        return 0.0
    p = counts / N
    p = p[p > 0]
    return -float(np.sum(p * np.log2(p)))


def main():
    morph = Morphology()
    tx = Transcript()

    # ── Load regime mapping ──────────────────────────────
    with open(PROJECT / 'data' / 'regime_folio_mapping.json') as f:
        regime_data = json.load(f)
    folio_to_regime = {
        f: d['regime']
        for f, d in regime_data['regime_assignments'].items()
    }

    # ── Single corpus pass: extract all features ─────────
    print("Building corpus feature table...")

    # Pre-compute morphology for unique words
    unique_words = set()
    for token in tx.currier_b():
        w = token.word.strip()
        if w and '*' not in w:
            unique_words.add(w)

    word_morph = {}
    for w in unique_words:
        word_morph[w] = morph.extract(w)

    # Build line-grouped tokens for bigram extraction
    line_tokens = defaultdict(list)  # (folio, line) -> [token, ...]
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        line_tokens[(token.folio, token.line)].append(token)

    # Extract features per token (with next-MIDDLE for bigrams)
    records = []
    for (folio, line), tokens in line_tokens.items():
        n_tokens = len(tokens)
        regime = folio_to_regime.get(folio, 'UNKNOWN')

        for i, tok in enumerate(tokens):
            w = tok.word.strip()
            m = word_morph.get(w)
            if m is None or not m.middle:
                continue

            prefix = m.prefix or 'BARE'
            middle = m.middle
            suffix = m.suffix or 'NONE'

            # Position bucket
            if i == 0:
                pos_bucket = 'INITIAL'
            elif i == n_tokens - 1:
                pos_bucket = 'FINAL'
            else:
                pos_bucket = 'MID'

            # Next-MIDDLE (within same line)
            next_middle = None
            if i < n_tokens - 1:
                next_w = tokens[i + 1].word.strip()
                next_m = word_morph.get(next_w)
                if next_m and next_m.middle:
                    next_middle = next_m.middle

            records.append({
                'prefix': prefix,
                'middle': middle,
                'suffix': suffix,
                'regime': regime,
                'pos_bucket': pos_bucket,
                'next_middle': next_middle,
            })

    print(f"  Total records: {len(records)}")

    # ── Filter to PP pairs with sufficient frequency ─────
    pp_counts = Counter((r['prefix'], r['middle']) for r in records)
    valid_pp = {pp for pp, c in pp_counts.items() if c >= MIN_PP_COUNT}
    filtered = [r for r in records
                if (r['prefix'], r['middle']) in valid_pp]
    print(f"  After PP frequency filter (>={MIN_PP_COUNT}): {len(filtered)} tokens")
    print(f"  Valid (PREFIX, MIDDLE) pairs: {len(valid_pp)}")

    # ── Build vocabularies ───────────────────────────────
    prefix_vocab = sorted({r['prefix'] for r in filtered})
    middle_vocab = sorted({r['middle'] for r in filtered})
    pp_vocab = sorted({(r['prefix'], r['middle']) for r in filtered})
    pp_str = [f"{p}|{m}" for p, m in pp_vocab]
    suffix_vocab = sorted({r['suffix'] for r in filtered})
    regime_vocab = sorted({r['regime'] for r in filtered})
    pos_vocab = ['INITIAL', 'MID', 'FINAL']

    # Next-MIDDLE: use top-K + OTHER to avoid extreme sparsity
    next_mid_counts = Counter(r['next_middle'] for r in filtered
                              if r['next_middle'] is not None)
    TOP_K = 50
    top_next = [m for m, _ in next_mid_counts.most_common(TOP_K)]
    next_vocab = top_next + ['OTHER']

    def map_next(nm):
        if nm is None:
            return None
        return nm if nm in top_next else 'OTHER'

    print(f"\n  PREFIX vocab:  {len(prefix_vocab)}")
    print(f"  MIDDLE vocab:  {len(middle_vocab)}")
    print(f"  PP vocab:      {len(pp_vocab)}")
    print(f"  SUFFIX vocab:  {len(suffix_vocab)}")
    print(f"  REGIME vocab:  {len(regime_vocab)}")
    print(f"  NEXT-MID vocab: {len(next_vocab)} (top {TOP_K} + OTHER)")

    # ── Compute MI for each target ───────────────────────
    targets = {
        'SUFFIX': {
            'labels': [r['suffix'] for r in filtered],
            'vocab': suffix_vocab,
        },
        'REGIME': {
            'labels': [r['regime'] for r in filtered],
            'vocab': regime_vocab,
        },
        'POSITION': {
            'labels': [r['pos_bucket'] for r in filtered],
            'vocab': pos_vocab,
        },
        'NEXT_MIDDLE': {
            'labels': [map_next(r['next_middle']) for r in filtered],
            'vocab': next_vocab,
            'filter_none': True,
        },
    }

    # Arrays for PREFIX and MIDDLE
    prefix_arr = [r['prefix'] for r in filtered]
    middle_arr = [r['middle'] for r in filtered]
    pp_arr = [f"{r['prefix']}|{r['middle']}" for r in filtered]

    results = {}

    for target_name, target_info in targets.items():
        print(f"\n{'='*70}")
        print(f"TARGET: {target_name}")
        print(f"{'='*70}")

        y_labels = target_info['labels']
        y_vocab = target_info['vocab']

        # Filter out None targets (for NEXT_MIDDLE, line-final tokens)
        if target_info.get('filter_none'):
            mask = [y is not None for y in y_labels]
            y_filt = [y for y, m in zip(y_labels, mask) if m]
            pre_filt = [p for p, m in zip(prefix_arr, mask) if m]
            mid_filt = [mi for mi, m in zip(middle_arr, mask) if m]
            pp_filt = [pp for pp, m in zip(pp_arr, mask) if m]
            n_tokens = len(y_filt)
        else:
            y_filt = y_labels
            pre_filt = prefix_arr
            mid_filt = middle_arr
            pp_filt = pp_arr
            n_tokens = len(y_filt)

        print(f"  Tokens: {n_tokens}")

        # Contingency tables
        ct_prefix = build_contingency(pre_filt, y_filt, prefix_vocab, y_vocab)
        ct_middle = build_contingency(mid_filt, y_filt, middle_vocab, y_vocab)
        ct_pp = build_contingency(pp_filt, y_filt, pp_str, y_vocab)

        # MI values
        mi_prefix = mi_plugin(ct_prefix)
        mi_middle = mi_plugin(ct_middle)
        mi_pp = mi_plugin(ct_pp)

        # Chain rule decomposition
        mi_prefix_given_middle = mi_pp - mi_middle  # PREFIX's unique contribution
        mi_middle_given_prefix = mi_pp - mi_prefix  # MIDDLE's unique contribution
        redundancy = mi_prefix + mi_middle - mi_pp

        # Entropy of target
        y_counts = np.array([y_filt.count(v) for v in y_vocab], dtype=float)
        h_y = entropy_plugin(y_counts)

        # Fraction of target entropy explained
        frac_by_prefix = mi_prefix / h_y if h_y > 0 else 0.0
        frac_by_middle = mi_middle / h_y if h_y > 0 else 0.0
        frac_by_pp = mi_pp / h_y if h_y > 0 else 0.0

        print(f"\n  H({target_name})           = {h_y:.4f} bits")
        print(f"  I(PREFIX; {target_name:<8s})   = {mi_prefix:.4f} bits  "
              f"({frac_by_prefix:.1%} of H)")
        print(f"  I(MIDDLE; {target_name:<8s})   = {mi_middle:.4f} bits  "
              f"({frac_by_middle:.1%} of H)")
        print(f"  I(PP;     {target_name:<8s})   = {mi_pp:.4f} bits  "
              f"({frac_by_pp:.1%} of H)")
        print(f"\n  PREFIX unique  = I(PREFIX; {target_name} | MIDDLE) "
              f"= {mi_prefix_given_middle:.4f} bits")
        print(f"  MIDDLE unique  = I(MIDDLE; {target_name} | PREFIX) "
              f"= {mi_middle_given_prefix:.4f} bits")
        print(f"  Redundancy     = {redundancy:.4f} bits")

        # Dominance ratio
        if mi_prefix_given_middle + mi_middle_given_prefix > 0:
            prefix_dominance = (mi_prefix_given_middle /
                                (mi_prefix_given_middle + mi_middle_given_prefix))
        else:
            prefix_dominance = 0.5
        print(f"\n  PREFIX dominance = {prefix_dominance:.1%} "
              f"({'PREFIX-dominant' if prefix_dominance > 0.5 else 'MIDDLE-dominant'})")

        # ── Permutation null for PREFIX unique contribution ──
        print(f"\n  Running {N_PERMS} permutations...")
        rng = np.random.default_rng(42)

        # Group token indices by MIDDLE (for within-MIDDLE PREFIX shuffle)
        middle_groups = defaultdict(list)
        for idx, m in enumerate(mid_filt):
            middle_groups[m].append(idx)

        pre_filt_arr = np.array(pre_filt)
        null_prefix_unique = np.zeros(N_PERMS)

        for p in range(N_PERMS):
            # Shuffle PREFIX within each MIDDLE group
            perm_prefix = pre_filt_arr.copy()
            for m, indices in middle_groups.items():
                idx_arr = np.array(indices)
                perm_prefix[idx_arr] = rng.permutation(perm_prefix[idx_arr])

            # Recompute I(PP; Y) with permuted PREFIX
            pp_perm = [f"{perm_prefix[i]}|{mid_filt[i]}"
                       for i in range(n_tokens)]
            ct_pp_perm = build_contingency(pp_perm, y_filt, pp_str, y_vocab)
            mi_pp_perm = mi_plugin(ct_pp_perm)
            null_prefix_unique[p] = mi_pp_perm - mi_middle

        null_mean = float(np.mean(null_prefix_unique))
        null_std = float(np.std(null_prefix_unique))
        p_value = float(np.mean(null_prefix_unique >= mi_prefix_given_middle))

        print(f"  Null I(PREFIX; {target_name} | MIDDLE): "
              f"mean={null_mean:.4f}, std={null_std:.4f}")
        print(f"  Observed: {mi_prefix_given_middle:.4f}, p={p_value:.4f}")

        sig = 'SIGNIFICANT' if p_value < 0.05 else 'NOT_SIGNIFICANT'
        print(f"  PREFIX unique contribution: {sig}")

        results[target_name] = {
            'n_tokens': n_tokens,
            'H_target': float(h_y),
            'I_prefix': float(mi_prefix),
            'I_middle': float(mi_middle),
            'I_pp': float(mi_pp),
            'prefix_unique': float(mi_prefix_given_middle),
            'middle_unique': float(mi_middle_given_prefix),
            'redundancy': float(redundancy),
            'prefix_dominance': float(prefix_dominance),
            'frac_by_prefix': float(frac_by_prefix),
            'frac_by_middle': float(frac_by_middle),
            'frac_by_pp': float(frac_by_pp),
            'perm_null_mean': null_mean,
            'perm_null_std': null_std,
            'perm_p_value': float(p_value),
            'significant': sig == 'SIGNIFICANT',
        }

    # ── Overall verdict ──────────────────────────────────
    print(f"\n{'='*70}")
    print(f"OVERALL DECOMPOSITION SUMMARY")
    print(f"{'='*70}")

    print(f"\n  {'Target':<14s} {'I(PRE)':<8s} {'I(MID)':<8s} {'I(PP)':<8s} "
          f"{'PRE uniq':<10s} {'MID uniq':<10s} {'Redund':<8s} {'PRE dom':<8s} {'p':<8s}")
    print(f"  {'-'*14} {'-'*8} {'-'*8} {'-'*8} {'-'*10} {'-'*10} {'-'*8} {'-'*8} {'-'*8}")

    for target_name, r in results.items():
        sig = '*' if r['significant'] else ''
        print(f"  {target_name:<14s} {r['I_prefix']:<8.4f} {r['I_middle']:<8.4f} "
              f"{r['I_pp']:<8.4f} {r['prefix_unique']:<10.4f} "
              f"{r['middle_unique']:<10.4f} {r['redundancy']:<8.4f} "
              f"{r['prefix_dominance']:<7.1%} {r['perm_p_value']:<8.4f} {sig}")

    # Verdict
    sig_targets = sum(1 for r in results.values() if r['significant'])
    prefix_dom_targets = sum(1 for r in results.values()
                             if r['prefix_dominance'] > 0.5 and r['significant'])
    middle_dom_targets = sum(1 for r in results.values()
                             if r['prefix_dominance'] <= 0.5 and r['significant'])

    avg_prefix_dom = np.mean([r['prefix_dominance'] for r in results.values()])
    avg_prefix_frac = np.mean([r['frac_by_prefix'] for r in results.values()])
    avg_middle_frac = np.mean([r['frac_by_middle'] for r in results.values()])

    if sig_targets >= 3 and avg_prefix_dom > 0.6:
        verdict = 'PREFIX_IS_PRIMARY_OPERATOR'
        detail = (f'PREFIX carries more unique information than MIDDLE across '
                  f'{sig_targets}/4 targets (avg dominance {avg_prefix_dom:.1%}). '
                  f'PP should be read as PREFIX(MIDDLE), not MIDDLE+PREFIX.')
    elif sig_targets >= 3 and avg_prefix_dom < 0.4:
        verdict = 'MIDDLE_IS_PRIMARY_OPERATOR'
        detail = (f'MIDDLE carries more unique information than PREFIX across '
                  f'{sig_targets}/4 targets (avg dominance {avg_prefix_dom:.1%}). '
                  f'PREFIX modifies MIDDLE but MIDDLE is the primary unit.')
    elif sig_targets >= 2:
        verdict = 'DUAL_OPERATOR'
        detail = (f'Both PREFIX and MIDDLE carry significant unique information '
                  f'({sig_targets}/4 targets significant, '
                  f'avg dominance {avg_prefix_dom:.1%}). '
                  f'PP is a genuine two-component encoding.')
    elif sig_targets <= 1 and avg_prefix_frac < 0.05:
        verdict = 'PREFIX_REDUNDANT'
        detail = (f'PREFIX adds negligible unique information '
                  f'(avg {avg_prefix_frac:.1%} of target entropy). '
                  f'MIDDLE alone carries the signal.')
    else:
        verdict = 'WEAK_DECOMPOSITION'
        detail = (f'Decomposition is inconclusive ({sig_targets}/4 targets '
                  f'significant, avg PREFIX dominance {avg_prefix_dom:.1%}).')

    print(f"\n  VERDICT: {verdict}")
    print(f"  {detail}")

    # PREFIX entropy vs MIDDLE entropy (information capacity)
    pre_counts = Counter(pre_filt)
    mid_counts = Counter(mid_filt)
    h_prefix = entropy_plugin(np.array([pre_counts[v] for v in prefix_vocab], dtype=float))
    h_middle = entropy_plugin(np.array([mid_counts[v] for v in middle_vocab], dtype=float))
    print(f"\n  Information capacity:")
    print(f"    H(PREFIX) = {h_prefix:.4f} bits ({len(prefix_vocab)} types)")
    print(f"    H(MIDDLE) = {h_middle:.4f} bits ({len(middle_vocab)} types)")
    print(f"    Capacity ratio: {h_prefix / h_middle:.2f}x" if h_middle > 0 else "")

    # ── Output ───────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'PP_INFORMATION_DECOMPOSITION',
            'test': 'T1_CONDITIONAL_MI_DECOMPOSITION',
            'min_pp_count': MIN_PP_COUNT,
            'n_permutations': N_PERMS,
        },
        'corpus': {
            'total_records': len(records),
            'filtered_records': len(filtered),
            'valid_pp_pairs': len(valid_pp),
            'prefix_vocab_size': len(prefix_vocab),
            'middle_vocab_size': len(middle_vocab),
            'H_prefix': float(h_prefix),
            'H_middle': float(h_middle),
        },
        'targets': results,
        'verdict': verdict,
        'verdict_detail': detail,
        'avg_prefix_dominance': float(avg_prefix_dom),
        'significant_targets': sig_targets,
    }

    out_path = RESULTS_DIR / 't1_conditional_mi_decomposition.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
