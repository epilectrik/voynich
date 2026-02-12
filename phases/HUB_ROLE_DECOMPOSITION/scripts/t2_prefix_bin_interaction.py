"""
T2: PREFIX x Bin Interaction
============================
Phase: HUB_ROLE_DECOMPOSITION

Tests whether PREFIX differentiates behavior WITHIN affordance bins,
focusing on HUB_UNIVERSAL (Bin 6).

Tests:
  2a: PREFIX-conditioned lane distributions within HUB
  2b: Safety buffer PREFIX prediction (Fisher's exact)
  2c: PREFIX x bin mutual information on instruction class

Output: t2_prefix_bin_interaction.json
"""

import sys
import json
import functools
import math
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

HUB_BIN = 6
FUNCTIONAL_BINS = [0, 1, 2, 3, 5, 6, 7, 8, 9]


def lane_prediction(middle):
    """C649 rule: initial character determines lane."""
    if not middle:
        return 'NEUTRAL'
    first = middle[0]
    if first in ('k', 't', 'p'):
        return 'QO'
    elif first in ('e', 'o'):
        return 'CHSH'
    return 'NEUTRAL'


def jsd(p, q):
    """Jensen-Shannon divergence between two probability distributions."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    p = p / p.sum() if p.sum() > 0 else p
    q = q / q.sum() if q.sum() > 0 else q
    m = 0.5 * (p + q)
    # Avoid log(0)
    kl_pm = np.sum(p * np.log2(np.where(p > 0, p / np.where(m > 0, m, 1), 1)))
    kl_qm = np.sum(q * np.log2(np.where(q > 0, q / np.where(m > 0, m, 1), 1)))
    return float(0.5 * kl_pm + 0.5 * kl_qm)


def mutual_information(contingency):
    """Compute MI from a contingency table (Counter of (x, y) -> count)."""
    # Build joint and marginals
    x_counts = Counter()
    y_counts = Counter()
    total = 0
    for (x, y), c in contingency.items():
        x_counts[x] += c
        y_counts[y] += c
        total += c
    if total == 0:
        return 0.0
    mi = 0.0
    for (x, y), c in contingency.items():
        p_xy = c / total
        p_x = x_counts[x] / total
        p_y = y_counts[y] / total
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi


def main():
    morph = Morphology()

    # ── Load affordance table ──────────────────────────────
    with open(PROJECT / 'data' / 'middle_affordance_table.json') as f:
        aff = json.load(f)

    middle_to_bin = {}
    hub_middles = set()
    for mid, data in aff['middles'].items():
        middle_to_bin[mid] = data['affordance_bin']
        if data['affordance_bin'] == HUB_BIN:
            hub_middles.add(mid)

    # ── Load safety buffer data ────────────────────────────
    with open(PROJECT / 'phases' / 'BIN_HAZARD_NECESSITY' / 'results' /
              'safety_buffer_scan.json') as f:
        buf_data = json.load(f)

    buffer_tokens = set()
    buffer_prefixes = Counter()
    for buf in buf_data['safety_buffers']:
        buffer_tokens.add((buf['folio'], buf['line'], buf['position']))
        m = morph.extract(buf['token'])
        pfx = m.prefix or 'BARE'
        buffer_prefixes[pfx] += 1

    # ── Load instruction class map ─────────────────────────
    class_map_path = (PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' /
                      'results' / 'class_token_map.json')
    token_to_class = {}
    if class_map_path.exists():
        with open(class_map_path) as f:
            cm = json.load(f)
        # Invert: class -> [tokens] to token -> class
        for cls_id, tokens in cm.items():
            if isinstance(tokens, list):
                for tok in tokens:
                    token_to_class[tok] = cls_id

    # ── Pre-compute word -> (prefix, middle) for all unique words ──
    tx = Transcript()
    unique_words = set()
    corpus_tokens = []  # [(word, folio, line, position_in_line), ...]

    # First pass: collect unique words and build corpus list
    line_tokens = defaultdict(list)  # (folio, line) -> [word, ...]
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        unique_words.add(w)
        line_tokens[(token.folio, token.line)].append(w)

    word_to_morph = {}
    for w in unique_words:
        m = morph.extract(w)
        word_to_morph[w] = (m.prefix or 'BARE', m.middle or '')

    # ── Single corpus pass: build contingency tables ───────
    # For test 2a: (prefix, lane) within HUB
    hub_prefix_lane = Counter()      # (prefix, lane) -> count
    # For test 2b: prefix counts for HUB tokens (buffer vs non-buffer)
    hub_buffer_prefix = Counter()    # prefix -> count (buffer HUB tokens)
    hub_nonbuffer_prefix = Counter() # prefix -> count (non-buffer HUB tokens)
    # For test 2c: (bin, class) and (prefix_bin, class) contingencies
    bin_class = Counter()            # (bin, class) -> count
    prefix_bin_class = Counter()     # ((prefix, bin), class) -> count
    # Track total HUB tokens by prefix
    hub_prefix_total = Counter()

    for (folio, line), words in line_tokens.items():
        for pos, w in enumerate(words):
            pfx, mid = word_to_morph.get(w, ('BARE', ''))
            b = middle_to_bin.get(mid, -1)

            if b == HUB_BIN:
                lane = lane_prediction(mid)
                hub_prefix_lane[(pfx, lane)] += 1
                hub_prefix_total[pfx] += 1

                # Check if this is a buffer token (by position)
                is_buffer = (folio, line, pos) in buffer_tokens
                if is_buffer:
                    hub_buffer_prefix[pfx] += 1
                else:
                    hub_nonbuffer_prefix[pfx] += 1

            # Instruction class (all bins)
            cls = token_to_class.get(w, None)
            if cls is not None and b in FUNCTIONAL_BINS:
                bin_class[(b, cls)] += 1
                prefix_bin_class[((pfx, b), cls)] += 1

    # ══════════════════════════════════════════════════════
    # TEST 2a: PREFIX-conditioned lane distributions within HUB
    # ══════════════════════════════════════════════════════
    print(f"{'='*70}")
    print(f"T2a: PREFIX-CONDITIONED LANE DISTRIBUTIONS (HUB)")
    print(f"{'='*70}")

    # Build per-prefix lane distributions
    lanes = ['QO', 'CHSH', 'NEUTRAL']
    prefix_list = sorted(hub_prefix_total.keys(),
                         key=lambda p: -hub_prefix_total[p])
    # Only prefixes with >= 10 tokens for meaningful comparison
    testable_prefixes = [p for p in prefix_list if hub_prefix_total[p] >= 10]

    print(f"\n{'PREFIX':<10s} {'Total':>6s} {'QO':>6s} {'CHSH':>6s} "
          f"{'NEUT':>6s} {'QO%':>6s} {'CHSH%':>6s}")
    print(f"{'-'*10} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")

    prefix_lane_data = {}
    for pfx in prefix_list[:15]:  # Show top 15
        total = hub_prefix_total[pfx]
        qo = hub_prefix_lane.get((pfx, 'QO'), 0)
        chsh = hub_prefix_lane.get((pfx, 'CHSH'), 0)
        neut = hub_prefix_lane.get((pfx, 'NEUTRAL'), 0)
        prefix_lane_data[pfx] = {
            'total': total, 'QO': qo, 'CHSH': chsh, 'NEUTRAL': neut
        }
        qo_pct = qo / total * 100 if total > 0 else 0
        chsh_pct = chsh / total * 100 if total > 0 else 0
        print(f"  {pfx:<8s} {total:>6d} {qo:>6d} {chsh:>6d} {neut:>6d} "
              f"{qo_pct:>5.1f}% {chsh_pct:>5.1f}%")

    # Chi-square on testable prefixes x lanes
    if len(testable_prefixes) >= 2:
        obs_matrix = []
        for pfx in testable_prefixes:
            row = [hub_prefix_lane.get((pfx, lane), 0) for lane in lanes]
            obs_matrix.append(row)
        obs_arr = np.array(obs_matrix)
        # Remove zero columns
        col_mask = obs_arr.sum(axis=0) > 0
        obs_arr = obs_arr[:, col_mask]
        if obs_arr.shape[1] >= 2:
            chi2, p_chi2, dof, _ = stats.chi2_contingency(obs_arr)
            n_total = obs_arr.sum()
            k_min = min(obs_arr.shape) - 1
            cramers_v = float(np.sqrt(chi2 / (n_total * k_min))) if n_total > 0 and k_min > 0 else 0.0
        else:
            chi2, p_chi2, cramers_v = 0.0, 1.0, 0.0
    else:
        chi2, p_chi2, cramers_v = 0.0, 1.0, 0.0

    print(f"\n  Chi-square (testable PREFIXes x lanes): chi2={chi2:.2f}, "
          f"p={p_chi2:.4e}, Cramer's V={cramers_v:.3f}")

    # JSD between top 2 prefixes
    jsd_pairs = {}
    if len(testable_prefixes) >= 2:
        for i in range(min(3, len(testable_prefixes))):
            for j in range(i + 1, min(4, len(testable_prefixes))):
                p1, p2 = testable_prefixes[i], testable_prefixes[j]
                dist1 = np.array([hub_prefix_lane.get((p1, l), 0)
                                  for l in lanes], dtype=float)
                dist2 = np.array([hub_prefix_lane.get((p2, l), 0)
                                  for l in lanes], dtype=float)
                j_val = jsd(dist1, dist2)
                jsd_pairs[f"{p1}_vs_{p2}"] = float(j_val)
                print(f"  JSD({p1} vs {p2}) = {j_val:.4f}")

    test_2a = {
        'chi2': float(chi2),
        'p': float(p_chi2),
        'cramers_v': float(cramers_v),
        'testable_prefixes': len(testable_prefixes),
        'prefix_lane_data': prefix_lane_data,
        'jsd_pairs': jsd_pairs,
    }

    # ══════════════════════════════════════════════════════
    # TEST 2b: SAFETY BUFFER PREFIX PREDICTION
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T2b: SAFETY BUFFER PREFIX PREDICTION")
    print(f"{'='*70}")

    # Fisher's exact: qo-prefix in buffers vs non-buffers
    total_buffers_hub = sum(hub_buffer_prefix.values())
    total_nonbuffers_hub = sum(hub_nonbuffer_prefix.values())
    qo_in_buf = hub_buffer_prefix.get('qo', 0)
    qo_in_nonbuf = hub_nonbuffer_prefix.get('qo', 0)
    nonqo_in_buf = total_buffers_hub - qo_in_buf
    nonqo_in_nonbuf = total_nonbuffers_hub - qo_in_nonbuf

    # 2x2 table: [[qo_buf, qo_nonbuf], [nonqo_buf, nonqo_nonbuf]]
    table_2x2 = np.array([[qo_in_buf, qo_in_nonbuf],
                           [nonqo_in_buf, nonqo_in_nonbuf]])

    if total_buffers_hub > 0 and total_nonbuffers_hub > 0:
        odds_ratio, fisher_p = stats.fisher_exact(table_2x2)
    else:
        odds_ratio, fisher_p = float('nan'), 1.0

    qo_rate_buf = qo_in_buf / total_buffers_hub if total_buffers_hub > 0 else 0
    qo_rate_nonbuf = qo_in_nonbuf / total_nonbuffers_hub if total_nonbuffers_hub > 0 else 0

    print(f"  HUB safety buffers: {total_buffers_hub}")
    print(f"  HUB non-buffers:    {total_nonbuffers_hub}")
    print(f"  QO-prefix in buffers:     {qo_in_buf}/{total_buffers_hub} "
          f"= {qo_rate_buf:.1%}")
    print(f"  QO-prefix in non-buffers: {qo_in_nonbuf}/{total_nonbuffers_hub} "
          f"= {qo_rate_nonbuf:.1%}")
    print(f"  Fisher's exact: OR={odds_ratio:.2f}, p={fisher_p:.4f}")
    print(f"\n  Buffer PREFIX distribution:")
    for pfx, count in buffer_prefixes.most_common():
        print(f"    {pfx:<8s}: {count}")

    test_2b = {
        'total_hub_buffers': total_buffers_hub,
        'total_hub_nonbuffers': total_nonbuffers_hub,
        'qo_rate_in_buffers': float(qo_rate_buf),
        'qo_rate_in_nonbuffers': float(qo_rate_nonbuf),
        'fishers_p': float(fisher_p),
        'odds_ratio': float(odds_ratio),
        'buffer_prefix_counts': dict(buffer_prefixes),
        'contingency_table': table_2x2.tolist(),
    }

    # ══════════════════════════════════════════════════════
    # TEST 2c: PREFIX x BIN MUTUAL INFORMATION
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T2c: PREFIX x BIN MUTUAL INFORMATION ON CLASS")
    print(f"{'='*70}")

    mi_bin_class = mutual_information(bin_class)
    mi_prefixbin_class = mutual_information(prefix_bin_class)
    mi_gain = mi_prefixbin_class - mi_bin_class
    mi_gain_pct = mi_gain / mi_bin_class * 100 if mi_bin_class > 0 else 0

    print(f"  I(class; bin)          = {mi_bin_class:.4f} bits")
    print(f"  I(class; PREFIX x bin) = {mi_prefixbin_class:.4f} bits")
    print(f"  MI gain                = {mi_gain:.4f} bits ({mi_gain_pct:.1f}%)")

    # Per-bin MI gain
    print(f"\n  Per-bin MI gain:")
    per_bin_mi = {}
    for b in FUNCTIONAL_BINS:
        # Bin-only: I(class; bin=b) is just the class entropy for this bin
        bin_only = Counter()
        prefix_conditioned = Counter()
        for (key, cls), c in bin_class.items():
            if key == b:
                bin_only[cls] += c
        for ((pfx, bn), cls), c in prefix_bin_class.items():
            if bn == b:
                prefix_conditioned[((pfx, bn), cls)] += c

        bin_label = aff['_metadata']['affordance_bins'].get(
            str(b), {}).get('label', f'Bin{b}')
        bin_total = sum(bin_only.values())

        # MI within this bin: does knowing PREFIX help predict class?
        within_bin_joint = Counter()
        for ((pfx, bn), cls), c in prefix_bin_class.items():
            if bn == b:
                within_bin_joint[(pfx, cls)] += c

        mi_within = mutual_information(within_bin_joint) if bin_total > 0 else 0
        per_bin_mi[b] = {'label': bin_label, 'tokens': bin_total,
                         'mi_prefix_class': float(mi_within)}
        print(f"    Bin {b} ({bin_label:<24s}): {bin_total:>5d} tokens, "
              f"I(class; PREFIX | bin={b}) = {mi_within:.4f} bits")

    test_2c = {
        'MI_bin_class': float(mi_bin_class),
        'MI_prefixbin_class': float(mi_prefixbin_class),
        'MI_gain': float(mi_gain),
        'MI_gain_pct': float(mi_gain_pct),
        'per_bin_mi': per_bin_mi,
    }

    # ── Overall verdict ────────────────────────────────────
    prefix_differentiates = (
        p_chi2 < 0.001 and cramers_v > 0.15 and mi_gain_pct > 10
    )
    prefix_partial = (
        p_chi2 < 0.05 or fisher_p < 0.05 or mi_gain_pct > 5
    )

    if prefix_differentiates:
        verdict = 'PREFIX_DIFFERENTIATES'
        detail = (f'PREFIX significantly differentiates lane within HUB '
                  f'(chi2 p={p_chi2:.2e}, V={cramers_v:.3f}) and adds '
                  f'{mi_gain_pct:.1f}% MI for class prediction.')
    elif prefix_partial:
        verdict = 'PREFIX_PARTIAL'
        detail = ('PREFIX shows partial differentiation within HUB on some '
                  'dimensions but not strong enough for clear sub-role '
                  'isolation.')
    else:
        verdict = 'PREFIX_NEUTRAL'
        detail = ('PREFIX does not significantly differentiate behavior '
                  'within HUB. Bin identity alone captures the relevant '
                  'structure.')

    print(f"\nVERDICT: {verdict}")
    print(f"  {detail}")

    # ── Output ─────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'HUB_ROLE_DECOMPOSITION',
            'test': 'T2_PREFIX_BIN_INTERACTION',
        },
        'test_2a_prefix_lane': test_2a,
        'test_2b_safety_buffer_prefix': test_2b,
        'test_2c_mutual_information': test_2c,
        'verdict': verdict,
        'verdict_detail': detail,
    }

    out_path = RESULTS_DIR / 't2_prefix_bin_interaction.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
