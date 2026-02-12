"""
T3: Suffix Sequential Grammar (Bigram Transitions)
===================================================
Phase: SUFFIX_POSITIONAL_STATE_MAPPING

Tests suffix→suffix transition structure for consecutive within-line tokens.
Parallel to C1001 T3 (PREFIX sequential grammar: chi²=2644, V=0.060).

Pass: chi² significant AND V>0.04, 5+ forbidden, 10+ enriched
Fail: V<0.02 or <3 forbidden

Output: t3_suffix_sequential_grammar.json
"""

import sys
import json
import functools
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats as sp_stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

SIGMA_FORBIDDEN = -3.0   # Z-score threshold for "forbidden"
SIGMA_ENRICHED = 3.0     # Z-score threshold for "enriched"


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


def entropy_plugin(counts):
    """Entropy in bits."""
    N = counts.sum()
    if N == 0:
        return 0.0
    p = counts / N
    p = p[p > 0]
    return -float(np.sum(p * np.log2(p)))


def main():
    morph = Morphology()
    tx = Transcript()

    # ── Build suffix sequences per line ───────────────────
    print("Building suffix sequences...")

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

    # Extract suffix sequences and bigrams
    bigrams = []
    suffix_seq_by_line = {}
    for (folio, line), tokens in line_tokens.items():
        suffixes = []
        for tok in tokens:
            w = tok.word.strip()
            m = word_morph.get(w)
            if m is None or not m.middle:
                continue
            suffixes.append(m.suffix or 'NONE')
        suffix_seq_by_line[(folio, line)] = suffixes
        for i in range(len(suffixes) - 1):
            bigrams.append((suffixes[i], suffixes[i+1]))

    print(f"  Lines: {len(suffix_seq_by_line)}")
    print(f"  Bigrams: {len(bigrams)}")

    # ══════════════════════════════════════════════════════
    # SUFFIX BIGRAM ANALYSIS
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"SUFFIX SEQUENTIAL GRAMMAR")
    print(f"{'='*70}")

    # Build transition matrix
    suffix_vocab = sorted(set(s for bg in bigrams for s in bg))
    suf_idx = {s: i for i, s in enumerate(suffix_vocab)}
    n_suf = len(suffix_vocab)

    count_matrix = np.zeros((n_suf, n_suf), dtype=float)
    for s1, s2 in bigrams:
        count_matrix[suf_idx[s1], suf_idx[s2]] += 1

    N = count_matrix.sum()
    row_sums = count_matrix.sum(axis=1)
    col_sums = count_matrix.sum(axis=0)

    # Expected under independence
    expected = np.outer(row_sums, col_sums) / N

    # Chi-squared
    mask = expected > 0
    chi2 = float(np.sum((count_matrix[mask] - expected[mask])**2 / expected[mask]))
    df = (n_suf - 1) * (n_suf - 1)
    chi2_p = float(sp_stats.chi2.sf(chi2, df))
    cramers_v = float(np.sqrt(chi2 / (N * (min(n_suf, n_suf) - 1))))

    print(f"\n  Chi² = {chi2:.1f}, df = {df}, p = {chi2_p:.2e}")
    print(f"  Cramer's V = {cramers_v:.4f}")
    print(f"  (C1001 PREFIX reference: chi²=2644, V=0.060)")

    # Z-scores for each bigram
    z_scores = np.zeros_like(count_matrix)
    for i in range(n_suf):
        for j in range(n_suf):
            if expected[i, j] > 0:
                z_scores[i, j] = (count_matrix[i, j] - expected[i, j]) / np.sqrt(expected[i, j])

    # Find forbidden (strong avoidance) and enriched
    forbidden = []
    enriched = []
    for i in range(n_suf):
        for j in range(n_suf):
            z = z_scores[i, j]
            obs = count_matrix[i, j]
            exp = expected[i, j]
            if exp < 5:  # Skip sparse cells
                continue
            if z < SIGMA_FORBIDDEN:
                forbidden.append((suffix_vocab[i], suffix_vocab[j],
                                  float(z), int(obs), float(exp)))
            elif z > SIGMA_ENRICHED:
                enriched.append((suffix_vocab[i], suffix_vocab[j],
                                 float(z), int(obs), float(exp)))

    forbidden.sort(key=lambda x: x[2])
    enriched.sort(key=lambda x: -x[2])

    print(f"\n  Forbidden transitions (z < {SIGMA_FORBIDDEN}): {len(forbidden)}")
    if forbidden:
        print(f"  {'From':<10s} {'To':<10s} {'Z':>8s} {'Obs':>6s} {'Exp':>8s}")
        print(f"  {'-'*10} {'-'*10} {'-'*8} {'-'*6} {'-'*8}")
        for s1, s2, z, obs, exp in forbidden[:20]:
            print(f"  {s1:<10s} {s2:<10s} {z:>+8.1f} {obs:>6d} {exp:>8.1f}")

    print(f"\n  Enriched transitions (z > {SIGMA_ENRICHED}): {len(enriched)}")
    if enriched:
        print(f"  {'From':<10s} {'To':<10s} {'Z':>8s} {'Obs':>6s} {'Exp':>8s}")
        print(f"  {'-'*10} {'-'*10} {'-'*8} {'-'*6} {'-'*8}")
        for s1, s2, z, obs, exp in enriched[:20]:
            print(f"  {s1:<10s} {s2:<10s} {z:>+8.1f} {obs:>6d} {exp:>8.1f}")

    # Sequential MI
    seq_mi = mi_plugin(count_matrix)
    suf_entropy = entropy_plugin(row_sums)
    frac_seq = seq_mi / suf_entropy if suf_entropy > 0 else 0.0

    print(f"\n  Sequential MI: I(SUFFIX_t; SUFFIX_{{t+1}}) = {seq_mi:.4f} bits")
    print(f"  H(SUFFIX) = {suf_entropy:.4f} bits")
    print(f"  Fraction: {frac_seq:.1%}")
    print(f"  (C1001 PREFIX reference: seq MI = 0.124 bits, 10.4% of MIDDLE)")

    # Cross-component: I(SUFFIX_t; PREFIX_{t+1}) and I(SUFFIX_t; MIDDLE_{t+1})
    print(f"\n  Cross-component sequential MI:")

    # Rebuild with component bigrams
    cross_bigrams_pre = []  # (suffix_t, prefix_{t+1})
    cross_bigrams_mid = []  # (suffix_t, middle_{t+1})
    for (folio, line), tokens in line_tokens.items():
        morphs = []
        for tok in tokens:
            w = tok.word.strip()
            m = word_morph.get(w)
            if m is None or not m.middle:
                continue
            morphs.append(m)
        for i in range(len(morphs) - 1):
            suf_t = morphs[i].suffix or 'NONE'
            pre_t1 = morphs[i+1].prefix or 'BARE'
            mid_t1 = morphs[i+1].middle
            cross_bigrams_pre.append((suf_t, pre_t1))
            cross_bigrams_mid.append((suf_t, mid_t1))

    # I(SUFFIX_t; PREFIX_{t+1})
    pre_vocab = sorted(set(b[1] for b in cross_bigrams_pre))
    ct_sp = np.zeros((n_suf, len(pre_vocab)))
    pre_idx = {p: i for i, p in enumerate(pre_vocab)}
    for s, p in cross_bigrams_pre:
        ct_sp[suf_idx[s], pre_idx[p]] += 1
    mi_suf_pre = mi_plugin(ct_sp)

    # I(SUFFIX_t; MIDDLE_{t+1})
    mid_vocab = sorted(set(b[1] for b in cross_bigrams_mid))
    ct_sm = np.zeros((n_suf, len(mid_vocab)))
    mid_idx = {m: i for i, m in enumerate(mid_vocab)}
    for s, m in cross_bigrams_mid:
        ct_sm[suf_idx[s], mid_idx[m]] += 1
    mi_suf_mid = mi_plugin(ct_sm)

    print(f"  I(SUFFIX_t; PREFIX_{{t+1}})  = {mi_suf_pre:.4f} bits")
    print(f"  I(SUFFIX_t; MIDDLE_{{t+1}})  = {mi_suf_mid:.4f} bits")
    print(f"  (C1001 ref: I(MIDDLE_t; PREFIX_{{t+1}}) = 0.499 bits)")

    # ── Verdict ───────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")

    if chi2_p < 0.001 and cramers_v > 0.04 and len(forbidden) >= 5 and len(enriched) >= 10:
        verdict = 'SUFFIX_SEQUENTIAL_GRAMMAR_CONFIRMED'
        detail = (f'chi²={chi2:.0f} (V={cramers_v:.4f}), '
                  f'{len(forbidden)} forbidden, {len(enriched)} enriched. '
                  f'SUFFIX transitions are structured.')
    elif chi2_p < 0.001 and (len(forbidden) >= 3 or len(enriched) >= 5):
        verdict = 'SUFFIX_SEQUENTIAL_GRAMMAR_PARTIAL'
        detail = (f'chi²={chi2:.0f} (V={cramers_v:.4f}), '
                  f'{len(forbidden)} forbidden, {len(enriched)} enriched. '
                  f'Some structure but weaker than PREFIX.')
    else:
        verdict = 'NO_SUFFIX_SEQUENTIAL_GRAMMAR'
        detail = (f'V={cramers_v:.4f} < 0.04 threshold or insufficient '
                  f'forbidden/enriched transitions.')

    print(f"\n  VERDICT: {verdict}")
    print(f"  {detail}")

    # ── Output ────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'SUFFIX_POSITIONAL_STATE_MAPPING',
            'test': 'T3_SUFFIX_SEQUENTIAL_GRAMMAR',
        },
        'corpus': {
            'n_bigrams': len(bigrams),
            'n_suffixes': n_suf,
        },
        'chi_squared': {
            'chi2': chi2, 'df': df, 'p': chi2_p, 'cramers_v': cramers_v,
        },
        'forbidden': [
            {'from': s1, 'to': s2, 'z': z, 'obs': obs, 'exp': exp}
            for s1, s2, z, obs, exp in forbidden
        ],
        'enriched': [
            {'from': s1, 'to': s2, 'z': z, 'obs': obs, 'exp': exp}
            for s1, s2, z, obs, exp in enriched
        ],
        'n_forbidden': len(forbidden),
        'n_enriched': len(enriched),
        'sequential_mi': {
            'suffix_to_suffix': seq_mi,
            'suffix_entropy': suf_entropy,
            'fraction': frac_seq,
            'suffix_to_next_prefix': mi_suf_pre,
            'suffix_to_next_middle': mi_suf_mid,
        },
        'verdict': verdict,
        'verdict_detail': detail,
    }

    out_path = RESULTS_DIR / 't3_suffix_sequential_grammar.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
