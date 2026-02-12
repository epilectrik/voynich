"""
T4: Suffix as Predictor of Next-Token PREFIX
=============================================
Phase: SUFFIX_POSITIONAL_STATE_MAPPING

Measures I(SUFFIX_t; PREFIX_{t+1} | MIDDLE_t) — the conditional MI of
current suffix predicting next prefix, beyond what current MIDDLE provides.

Baselines:
  I(MIDDLE_t; PREFIX_{t+1}) = 0.499 bits (C1001)
  I(PP_t; NEXT_MIDDLE) = 0.0 bits (C1001)

Pass: conditional MI > 0.05 bits, permutation p < 0.001
Fail: < 0.02 bits

Output: t4_suffix_cross_token_prediction.json
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

N_PERMS = 2000


def mi_plugin(joint_counts):
    """MI in bits with Miller-Madow correction."""
    N = joint_counts.sum()
    if N == 0:
        return 0.0
    px = joint_counts.sum(axis=1) / N
    py = joint_counts.sum(axis=0) / N
    pxy = joint_counts / N

    mi = 0.0
    for i in range(pxy.shape[0]):
        for j in range(pxy.shape[1]):
            if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += pxy[i, j] * np.log2(pxy[i, j] / (px[i] * py[j]))

    nx = np.sum(px > 0)
    ny = np.sum(py > 0)
    correction = (nx - 1) * (ny - 1) / (2 * N * np.log(2))
    return max(0.0, mi - correction)


def build_contingency(x_labels, y_labels, x_vocab, y_vocab):
    """Build contingency table."""
    x_idx = {v: i for i, v in enumerate(x_vocab)}
    y_idx = {v: i for i, v in enumerate(y_vocab)}
    table = np.zeros((len(x_vocab), len(y_vocab)), dtype=float)
    for xi, yi in zip(x_labels, y_labels):
        if xi in x_idx and yi in y_idx:
            table[x_idx[xi], y_idx[yi]] += 1
    return table


def load_class_map():
    """Load 49-class mapping for dimensionality reduction."""
    path = PROJECT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
    with open(path) as f:
        ctm = json.load(f)
    return {t: str(c) for t, c in ctm['token_to_class'].items()}


def main():
    morph = Morphology()
    tx = Transcript()
    token_to_class = load_class_map()

    # ── Build consecutive token pairs ─────────────────────
    print("Building token pair data...")
    print("  Using 49-class MIDDLE (not raw MIDDLE) to avoid MI overcorrection")

    unique_words = set()
    for token in tx.currier_b():
        w = token.word.strip()
        if w and '*' not in w:
            unique_words.add(w)

    word_morph = {}
    for w in unique_words:
        word_morph[w] = morph.extract(w)

    line_tokens = defaultdict(list)
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        line_tokens[(token.folio, token.line)].append(token)

    # Extract consecutive pairs using 49-class for MIDDLE dimension
    pairs = []
    for (folio, line), tokens in line_tokens.items():
        tok_data = []
        for tok in tokens:
            w = tok.word.strip()
            m = word_morph.get(w)
            if m is None or not m.middle:
                continue
            cls = token_to_class.get(w)
            if cls is None:
                continue
            tok_data.append({
                'word': w,
                'prefix': m.prefix or 'BARE',
                'middle_class': cls,  # 49-class, not raw MIDDLE
                'suffix': m.suffix or 'NONE',
            })
        for i in range(len(tok_data) - 1):
            pairs.append({
                'prefix_t': tok_data[i]['prefix'],
                'middle_t': tok_data[i]['middle_class'],
                'suffix_t': tok_data[i]['suffix'],
                'prefix_t1': tok_data[i+1]['prefix'],
                'middle_t1': tok_data[i+1]['middle_class'],
                'suffix_t1': tok_data[i+1]['suffix'],
            })

    print(f"  Consecutive pairs: {len(pairs)}")

    # Build vocabs
    suffix_vocab = sorted(set(p['suffix_t'] for p in pairs))
    middle_vocab = sorted(set(p['middle_t'] for p in pairs))
    prefix_vocab_t1 = sorted(set(p['prefix_t1'] for p in pairs))
    middle_vocab_t1 = sorted(set(p['middle_t1'] for p in pairs))

    # ══════════════════════════════════════════════════════
    # MARGINAL MI: I(SUFFIX_t; PREFIX_{t+1})
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"MARGINAL MI: I(SUFFIX_t; PREFIX_{{t+1}})")
    print(f"{'='*70}")

    suf_t = [p['suffix_t'] for p in pairs]
    pre_t1 = [p['prefix_t1'] for p in pairs]

    ct_sp = build_contingency(suf_t, pre_t1, suffix_vocab, prefix_vocab_t1)
    mi_suf_pre = mi_plugin(ct_sp)
    print(f"  I(SUFFIX_t; PREFIX_{{t+1}}) = {mi_suf_pre:.4f} bits")

    # ══════════════════════════════════════════════════════
    # MARGINAL MI: I(MIDDLE_t; PREFIX_{t+1}) — replicate C1001 baseline
    # ══════════════════════════════════════════════════════
    mid_t = [p['middle_t'] for p in pairs]
    ct_mp = build_contingency(mid_t, pre_t1, middle_vocab, prefix_vocab_t1)
    mi_mid_pre = mi_plugin(ct_mp)
    print(f"  I(MIDDLE_t; PREFIX_{{t+1}}) = {mi_mid_pre:.4f} bits (C1001: 0.499)")

    # ══════════════════════════════════════════════════════
    # JOINT MI: I(MIDDLE_t, SUFFIX_t; PREFIX_{t+1})
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"JOINT MI: I(MIDDLE_t+SUFFIX_t; PREFIX_{{t+1}})")
    print(f"{'='*70}")

    # Create joint (MIDDLE, SUFFIX) labels
    ms_vocab = sorted(set((p['middle_t'], p['suffix_t']) for p in pairs))
    ms_str = [f"{m}|{s}" for m, s in ms_vocab]
    ms_labels = [f"{p['middle_t']}|{p['suffix_t']}" for p in pairs]

    ct_ms_pre = build_contingency(ms_labels, pre_t1, ms_str, prefix_vocab_t1)
    mi_ms_pre = mi_plugin(ct_ms_pre)

    # Conditional MI via chain rule
    mi_suf_pre_given_mid = mi_ms_pre - mi_mid_pre
    mi_mid_pre_given_suf = mi_ms_pre - mi_suf_pre
    redundancy = mi_suf_pre + mi_mid_pre - mi_ms_pre

    print(f"  I(MID+SUF; PREFIX_{{t+1}})         = {mi_ms_pre:.4f} bits")
    print(f"  I(SUF; PREFIX_{{t+1}} | MID)        = {mi_suf_pre_given_mid:.4f} bits")
    print(f"  I(MID; PREFIX_{{t+1}} | SUF)        = {mi_mid_pre_given_suf:.4f} bits")
    print(f"  Redundancy                        = {redundancy:.4f} bits")

    # ══════════════════════════════════════════════════════
    # SAME FOR NEXT MIDDLE: I(SUFFIX_t; MIDDLE_{t+1} | MIDDLE_t)
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"SUFFIX PREDICTING NEXT MIDDLE")
    print(f"{'='*70}")

    mid_t1 = [p['middle_t1'] for p in pairs]
    # Use top-50 + OTHER for next MIDDLE (avoid extreme sparsity)
    mid_t1_counts = Counter(mid_t1)
    top_50 = [m for m, _ in mid_t1_counts.most_common(50)]
    mid_t1_vocab = top_50 + ['OTHER']
    mid_t1_mapped = [m if m in top_50 else 'OTHER' for m in mid_t1]

    ct_suf_nmid = build_contingency(suf_t, mid_t1_mapped, suffix_vocab, mid_t1_vocab)
    mi_suf_nmid = mi_plugin(ct_suf_nmid)

    ct_mid_nmid = build_contingency(mid_t, mid_t1_mapped, middle_vocab, mid_t1_vocab)
    mi_mid_nmid = mi_plugin(ct_mid_nmid)

    ms_nmid_labels = ms_labels
    ct_ms_nmid = build_contingency(ms_nmid_labels, mid_t1_mapped, ms_str, mid_t1_vocab)
    mi_ms_nmid = mi_plugin(ct_ms_nmid)

    mi_suf_nmid_given_mid = mi_ms_nmid - mi_mid_nmid

    print(f"  I(SUFFIX_t; MIDDLE_{{t+1}})        = {mi_suf_nmid:.4f} bits")
    print(f"  I(MIDDLE_t; MIDDLE_{{t+1}})        = {mi_mid_nmid:.4f} bits")
    print(f"  I(MID+SUF; MIDDLE_{{t+1}})         = {mi_ms_nmid:.4f} bits")
    print(f"  I(SUF; MIDDLE_{{t+1}} | MID)       = {mi_suf_nmid_given_mid:.4f} bits")

    # ══════════════════════════════════════════════════════
    # PERMUTATION NULL for I(SUFFIX_t; PREFIX_{t+1} | MIDDLE_t)
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"PERMUTATION TEST ({N_PERMS} iterations)")
    print(f"{'='*70}")

    rng = np.random.default_rng(42)

    # Group pair indices by MIDDLE_t for within-MIDDLE shuffle
    middle_groups = defaultdict(list)
    for idx, p in enumerate(pairs):
        middle_groups[p['middle_t']].append(idx)

    suf_arr = np.array(suf_t)
    null_cmi = np.zeros(N_PERMS)

    for perm in range(N_PERMS):
        if perm % 500 == 0:
            print(f"  Permutation {perm}/{N_PERMS}...")

        perm_suf = suf_arr.copy()
        for m, indices in middle_groups.items():
            idx_arr = np.array(indices)
            perm_suf[idx_arr] = rng.permutation(perm_suf[idx_arr])

        # Recompute joint MI with permuted suffix
        perm_ms = [f"{pairs[i]['middle_t']}|{perm_suf[i]}" for i in range(len(pairs))]
        ct_perm = build_contingency(perm_ms, pre_t1, ms_str, prefix_vocab_t1)
        mi_perm = mi_plugin(ct_perm)
        null_cmi[perm] = mi_perm - mi_mid_pre

    null_mean = float(np.mean(null_cmi))
    null_std = float(np.std(null_cmi))
    p_value = float(np.mean(null_cmi >= mi_suf_pre_given_mid))
    z_score = (mi_suf_pre_given_mid - null_mean) / null_std if null_std > 0 else 0.0

    print(f"\n  Observed I(SUF; PREFIX_{{t+1}} | MID) = {mi_suf_pre_given_mid:.4f}")
    print(f"  Null mean = {null_mean:.4f}, std = {null_std:.4f}")
    print(f"  Z-score = {z_score:.2f}")
    print(f"  p-value = {p_value:.4f}")

    # Also permutation test for I(SUF; MIDDLE_{t+1} | MID)
    null_cmi_nmid = np.zeros(N_PERMS)
    for perm in range(N_PERMS):
        perm_suf = suf_arr.copy()
        for m, indices in middle_groups.items():
            idx_arr = np.array(indices)
            perm_suf[idx_arr] = rng.permutation(perm_suf[idx_arr])
        perm_ms = [f"{pairs[i]['middle_t']}|{perm_suf[i]}" for i in range(len(pairs))]
        ct_perm = build_contingency(perm_ms, mid_t1_mapped, ms_str, mid_t1_vocab)
        mi_perm = mi_plugin(ct_perm)
        null_cmi_nmid[perm] = mi_perm - mi_mid_nmid

    p_value_nmid = float(np.mean(null_cmi_nmid >= mi_suf_nmid_given_mid))
    print(f"\n  I(SUF; MIDDLE_{{t+1}} | MID): p = {p_value_nmid:.4f}")

    # ── Summary & Verdict ─────────────────────────────────
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  I(SUFFIX_t; PREFIX_{{t+1}} | MIDDLE_t) = {mi_suf_pre_given_mid:.4f} bits, "
          f"p = {p_value:.4f}")
    print(f"  I(SUFFIX_t; MIDDLE_{{t+1}} | MIDDLE_t) = {mi_suf_nmid_given_mid:.4f} bits, "
          f"p = {p_value_nmid:.4f}")
    print(f"  Baseline: I(MIDDLE_t; PREFIX_{{t+1}}) = {mi_mid_pre:.4f} bits")

    if mi_suf_pre_given_mid > 0.05 and p_value < 0.001:
        verdict = 'SUFFIX_CROSS_TOKEN_SIGNAL_CONFIRMED'
        detail = (f'SUFFIX adds {mi_suf_pre_given_mid:.4f} bits of next-PREFIX '
                  f'prediction beyond MIDDLE (p={p_value:.4f}). '
                  f'SUFFIX carries cross-token sequential state.')
    elif mi_suf_pre_given_mid > 0.02 and p_value < 0.01:
        verdict = 'SUFFIX_CROSS_TOKEN_SIGNAL_WEAK'
        detail = (f'SUFFIX adds {mi_suf_pre_given_mid:.4f} bits (p={p_value:.4f}). '
                  f'Detectable but modest cross-token signal.')
    else:
        verdict = 'NO_SUFFIX_CROSS_TOKEN_SIGNAL'
        detail = (f'I(SUF; PREFIX_{{t+1}} | MID) = {mi_suf_pre_given_mid:.4f} bits '
                  f'(p={p_value:.4f}). Suffix adds negligible next-token prediction.')

    print(f"\n  VERDICT: {verdict}")
    print(f"  {detail}")

    # ── Output ────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'SUFFIX_POSITIONAL_STATE_MAPPING',
            'test': 'T4_SUFFIX_CROSS_TOKEN_PREDICTION',
            'n_permutations': N_PERMS,
        },
        'corpus': {
            'n_pairs': len(pairs),
        },
        'marginal_mi': {
            'suffix_to_next_prefix': mi_suf_pre,
            'middle_to_next_prefix': mi_mid_pre,
            'suffix_to_next_middle': mi_suf_nmid,
            'middle_to_next_middle': mi_mid_nmid,
        },
        'joint_mi': {
            'ms_to_next_prefix': mi_ms_pre,
            'ms_to_next_middle': mi_ms_nmid,
        },
        'conditional_mi': {
            'suffix_given_middle_to_next_prefix': mi_suf_pre_given_mid,
            'suffix_given_middle_to_next_middle': mi_suf_nmid_given_mid,
            'middle_given_suffix_to_next_prefix': mi_mid_pre_given_suf,
            'redundancy_next_prefix': redundancy,
        },
        'permutation_test_next_prefix': {
            'null_mean': null_mean,
            'null_std': null_std,
            'z_score': z_score,
            'p_value': p_value,
        },
        'permutation_test_next_middle': {
            'p_value': p_value_nmid,
        },
        'verdict': verdict,
        'verdict_detail': detail,
    }

    out_path = RESULTS_DIR / 't4_suffix_cross_token_prediction.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
