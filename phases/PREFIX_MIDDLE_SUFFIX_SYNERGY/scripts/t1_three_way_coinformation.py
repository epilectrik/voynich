"""
T1: Three-Way Co-Information (PID)
===================================
Phase: PREFIX_MIDDLE_SUFFIX_SYNERGY

Computes Co-Information for (PREFIX, MIDDLE, SUFFIX) → TARGET
  Co-I = I(full) - Σ(pairwise) + Σ(marginal)
  Negative = synergy; Positive = redundancy

Targets: ROLE (5 roles), REGIME (4), POSITION (5 bins), SECTION (5)

Pass: Co-I significantly negative on 2+ targets, magnitude >0.02 bits
Fail: Co-I positive or non-significant on all 4

Output: t1_three_way_coinformation.json
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

N_PERMS = 1000


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
    x_idx = {v: i for i, v in enumerate(x_vocab)}
    y_idx = {v: i for i, v in enumerate(y_vocab)}
    table = np.zeros((len(x_vocab), len(y_vocab)), dtype=float)
    for xi, yi in zip(x_labels, y_labels):
        if xi in x_idx and yi in y_idx:
            table[x_idx[xi], y_idx[yi]] += 1
    return table


def load_class_map():
    """Load 49-class mapping."""
    path = PROJECT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
    with open(path) as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    all_cls = sorted(set(token_to_class.values()))
    EN = ({8} | set(range(31, 50)) - {7, 30, 38, 40}) & set(all_cls)
    FL = {7, 30, 38, 40} & set(all_cls)
    CC = {10, 11, 12} & set(all_cls)
    FQ = {9, 13, 14, 23} & set(all_cls)
    AX = set(all_cls) - EN - FL - CC - FQ

    class_to_role = {}
    for c in all_cls:
        if c in CC: class_to_role[c] = 'CC'
        elif c in FQ: class_to_role[c] = 'FQ'
        elif c in EN: class_to_role[c] = 'EN'
        elif c in FL: class_to_role[c] = 'FL'
        elif c in AX: class_to_role[c] = 'AX'
    return token_to_class, class_to_role


def main():
    morph = Morphology()
    tx = Transcript()

    # ── Load external data ────────────────────────────────
    token_to_class, class_to_role = load_class_map()

    with open(PROJECT / 'data' / 'regime_folio_mapping.json') as f:
        regime_data = json.load(f)
    folio_to_regime = {
        f: d['regime']
        for f, d in regime_data['regime_assignments'].items()
    }

    # ── Build corpus features ─────────────────────────────
    print("Building feature table...")

    unique_words = set()
    for token in tx.currier_b():
        w = token.word.strip()
        if w and '*' not in w:
            unique_words.add(w)
    word_morph = {w: morph.extract(w) for w in unique_words}

    line_tokens = defaultdict(list)
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        line_tokens[(token.folio, token.line)].append(token)

    records = []
    for (folio, line), tokens in line_tokens.items():
        n = len(tokens)
        regime = folio_to_regime.get(folio, 'UNKNOWN')
        section = folio[0].upper() if folio else 'X'  # Rough section from folio prefix

        for i, tok in enumerate(tokens):
            w = tok.word.strip()
            m = word_morph.get(w)
            if m is None or not m.middle:
                continue

            prefix = m.prefix or 'BARE'
            middle = m.middle
            suffix = m.suffix or 'NONE'

            # 49-class and role
            cls = token_to_class.get(w)
            role = class_to_role.get(cls, 'UNKNOWN') if cls is not None else 'UNKNOWN'

            # Position quintile
            pos_q = min(4, int((i / max(n-1, 1)) * 5)) if n > 1 else 2

            records.append({
                'prefix': prefix,
                'middle': middle,
                'suffix': suffix,
                'role': role,
                'regime': regime,
                'position': str(pos_q),
                'section': section,
                'word': w,
            })

    # Filter to tokens with known class
    records = [r for r in records if r['role'] != 'UNKNOWN']
    print(f"  Records: {len(records)}")

    # Build vocabs
    prefix_vocab = sorted(set(r['prefix'] for r in records))
    # Use instruction class (via MIDDLE mapping) to keep tractable
    # Map MIDDLE to its most common class
    middle_class_map = defaultdict(Counter)
    for r in records:
        cls = token_to_class.get(r['word'])
        if cls is not None:
            middle_class_map[r['middle']][cls] += 1
    middle_to_class = {}
    for mid, cnt in middle_class_map.items():
        middle_to_class[mid] = str(cnt.most_common(1)[0][0])

    class_vocab = sorted(set(middle_to_class.values()))
    suffix_vocab = sorted(set(r['suffix'] for r in records))

    # Build label arrays
    pre_arr = [r['prefix'] for r in records]
    cls_arr = [middle_to_class.get(r['middle'], 'UNK') for r in records]
    suf_arr = [r['suffix'] for r in records]

    # Joint labels
    pc_arr = [f"{p}|{c}" for p, c in zip(pre_arr, cls_arr)]
    ps_arr = [f"{p}|{s}" for p, s in zip(pre_arr, suf_arr)]
    cs_arr = [f"{c}|{s}" for c, s in zip(cls_arr, suf_arr)]
    pcs_arr = [f"{p}|{c}|{s}" for p, c, s in zip(pre_arr, cls_arr, suf_arr)]

    pc_vocab = sorted(set(pc_arr))
    ps_vocab = sorted(set(ps_arr))
    cs_vocab = sorted(set(cs_arr))
    pcs_vocab = sorted(set(pcs_arr))

    print(f"  PREFIX vocab: {len(prefix_vocab)}")
    print(f"  CLASS vocab: {len(class_vocab)}")
    print(f"  SUFFIX vocab: {len(suffix_vocab)}")
    print(f"  PCS combos: {len(pcs_vocab)}")

    # ── Compute Co-Information for each target ─────────────
    targets = {
        'ROLE': {
            'labels': [r['role'] for r in records],
            'vocab': sorted(set(r['role'] for r in records)),
        },
        'REGIME': {
            'labels': [r['regime'] for r in records],
            'vocab': sorted(set(r['regime'] for r in records)),
        },
        'POSITION': {
            'labels': [r['position'] for r in records],
            'vocab': [str(i) for i in range(5)],
        },
        'SECTION': {
            'labels': [r['section'] for r in records],
            'vocab': sorted(set(r['section'] for r in records)),
        },
    }

    results = {}

    for target_name, target_info in targets.items():
        print(f"\n{'='*70}")
        print(f"TARGET: {target_name}")
        print(f"{'='*70}")

        y = target_info['labels']
        y_vocab = target_info['vocab']

        # Marginal MIs
        mi_p = mi_plugin(build_contingency(pre_arr, y, prefix_vocab, y_vocab))
        mi_c = mi_plugin(build_contingency(cls_arr, y, class_vocab, y_vocab))
        mi_s = mi_plugin(build_contingency(suf_arr, y, suffix_vocab, y_vocab))

        # Pairwise MIs
        mi_pc = mi_plugin(build_contingency(pc_arr, y, pc_vocab, y_vocab))
        mi_ps = mi_plugin(build_contingency(ps_arr, y, ps_vocab, y_vocab))
        mi_cs = mi_plugin(build_contingency(cs_arr, y, cs_vocab, y_vocab))

        # Full three-way MI
        mi_pcs = mi_plugin(build_contingency(pcs_arr, y, pcs_vocab, y_vocab))

        # Co-Information
        co_info = mi_pcs - (mi_pc + mi_ps + mi_cs) + (mi_p + mi_c + mi_s)

        print(f"  Marginal:  I(P)={mi_p:.4f}, I(C)={mi_c:.4f}, I(S)={mi_s:.4f}")
        print(f"  Pairwise:  I(PC)={mi_pc:.4f}, I(PS)={mi_ps:.4f}, I(CS)={mi_cs:.4f}")
        print(f"  Full:      I(PCS)={mi_pcs:.4f}")
        print(f"  Co-Info:   {co_info:+.4f} bits "
              f"({'SYNERGY' if co_info < 0 else 'REDUNDANCY'})")

        # Permutation null: shuffle SUFFIX to destroy three-way association
        print(f"  Running {N_PERMS} permutations...")
        rng = np.random.default_rng(42)
        null_co = np.zeros(N_PERMS)
        suf_np = np.array(suf_arr)

        for perm in range(N_PERMS):
            perm_suf = rng.permutation(suf_np)
            perm_ps = [f"{p}|{s}" for p, s in zip(pre_arr, perm_suf)]
            perm_cs = [f"{c}|{s}" for c, s in zip(cls_arr, perm_suf)]
            perm_pcs = [f"{p}|{c}|{s}" for p, c, s in zip(pre_arr, cls_arr, perm_suf)]

            # Recompute with permuted suffix (marginal MI_S stays same)
            mi_ps_p = mi_plugin(build_contingency(perm_ps, y,
                                sorted(set(perm_ps)), y_vocab))
            mi_cs_p = mi_plugin(build_contingency(perm_cs, y,
                                sorted(set(perm_cs)), y_vocab))
            mi_pcs_p = mi_plugin(build_contingency(perm_pcs, y,
                                 sorted(set(perm_pcs)), y_vocab))

            null_co[perm] = mi_pcs_p - (mi_pc + mi_ps_p + mi_cs_p) + (mi_p + mi_c + mi_s)

        null_mean = float(np.mean(null_co))
        null_std = float(np.std(null_co))
        # For synergy test: p = fraction of null values as extreme as observed
        if co_info < 0:
            p_value = float(np.mean(null_co <= co_info))
        else:
            p_value = float(np.mean(null_co >= co_info))

        print(f"  Null: mean={null_mean:+.4f}, std={null_std:.4f}")
        print(f"  p-value = {p_value:.4f}")

        is_significant = (co_info < -0.02 and p_value < 0.005)

        results[target_name] = {
            'marginal': {'prefix': mi_p, 'class': mi_c, 'suffix': mi_s},
            'pairwise': {'prefix_class': mi_pc, 'prefix_suffix': mi_ps,
                         'class_suffix': mi_cs},
            'full': mi_pcs,
            'co_information': co_info,
            'type': 'SYNERGY' if co_info < 0 else 'REDUNDANCY',
            'perm_null_mean': null_mean,
            'perm_null_std': null_std,
            'p_value': p_value,
            'significant_synergy': bool(is_significant),
        }

    # ── Summary ───────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")

    print(f"\n  {'Target':<12s} {'Co-Info':>10s} {'Type':<12s} {'p':>8s} {'Sig':>4s}")
    print(f"  {'-'*12} {'-'*10} {'-'*12} {'-'*8} {'-'*4}")
    for name, r in results.items():
        sig = '*' if r['significant_synergy'] else ''
        print(f"  {name:<12s} {r['co_information']:>+10.4f} {r['type']:<12s} "
              f"{r['p_value']:>8.4f} {sig}")

    sig_count = sum(1 for r in results.values() if r['significant_synergy'])

    if sig_count >= 2:
        verdict = 'THREE_WAY_SYNERGY_CONFIRMED'
        detail = (f'{sig_count}/4 targets show significant three-way synergy. '
                  f'TOKEN is a genuine three-way unit beyond pairwise components.')
    elif sig_count == 1:
        verdict = 'THREE_WAY_SYNERGY_MARGINAL'
        detail = (f'{sig_count}/4 targets show synergy. Weak evidence for '
                  f'three-way interaction.')
    else:
        verdict = 'NO_THREE_WAY_SYNERGY'
        detail = (f'Co-Information is non-negative or non-significant on all targets. '
                  f'TOKEN is well-described by pairwise component interactions.')

    print(f"\n  VERDICT: {verdict}")
    print(f"  {detail}")

    # ── Output ────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'PREFIX_MIDDLE_SUFFIX_SYNERGY',
            'test': 'T1_THREE_WAY_COINFORMATION',
            'n_permutations': N_PERMS,
        },
        'corpus': {
            'n_records': len(records),
        },
        'targets': results,
        'significant_synergy_count': sig_count,
        'verdict': verdict,
        'verdict_detail': detail,
    }

    out_path = RESULTS_DIR / 't1_three_way_coinformation.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
