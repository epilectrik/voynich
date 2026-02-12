"""
T3: PREFIX Sequential Grammar
==============================
Phase: PP_INFORMATION_DECOMPOSITION

Tests whether PREFIX follows sequential rules within lines.
If PREFIX is a positional grammar marker, consecutive PREFIXes should
show transition preferences (some sequences enriched, others forbidden).

Tests:
  3a: PREFIX bigram transition matrix within lines
      Chi-square on full matrix vs independence
  3b: Forbidden PREFIX transitions (observed << expected)
      Enriched PREFIX transitions (observed >> expected)
  3c: PREFIX run analysis — consecutive same-PREFIX tokens
  3d: PREFIX vs MIDDLE sequential information
      I(PREFIX_t; PREFIX_{t+1}) vs I(MIDDLE_t; MIDDLE_{t+1})

Output: t3_prefix_sequential_grammar.json
"""

import sys
import json
import functools
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

MIN_BIGRAM_EXPECTED = 5.0  # Minimum expected count for chi-square cell


def mi_from_contingency(table):
    """Compute MI in bits from 2D contingency table."""
    N = table.sum()
    if N == 0:
        return 0.0
    px = table.sum(axis=1) / N
    py = table.sum(axis=0) / N
    pxy = table / N
    mi = 0.0
    for i in range(pxy.shape[0]):
        for j in range(pxy.shape[1]):
            if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += pxy[i, j] * np.log2(pxy[i, j] / (px[i] * py[j]))
    return max(0.0, mi)


def main():
    morph = Morphology()
    tx = Transcript()

    # ── Single corpus pass ───────────────────────────────
    print("Building sequential data...")

    # Pre-compute morphology
    unique_words = set()
    for token in tx.currier_b():
        w = token.word.strip()
        if w and '*' not in w:
            unique_words.add(w)

    word_morph = {}
    for w in unique_words:
        word_morph[w] = morph.extract(w)

    # Group tokens by line
    line_tokens = defaultdict(list)
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        line_tokens[(token.folio, token.line)].append(token)

    # Extract PREFIX and MIDDLE sequences per line
    line_sequences = []
    for (folio, line), tokens in line_tokens.items():
        seq = []
        for tok in tokens:
            w = tok.word.strip()
            m = word_morph.get(w)
            if m and m.middle:
                seq.append((m.prefix or 'BARE', m.middle))
        if len(seq) >= 2:
            line_sequences.append(seq)

    # Build bigram arrays
    prefix_bigrams = []
    middle_bigrams = []
    for seq in line_sequences:
        for i in range(len(seq) - 1):
            prefix_bigrams.append((seq[i][0], seq[i+1][0]))
            middle_bigrams.append((seq[i][1], seq[i+1][1]))

    print(f"  Lines: {len(line_sequences)}")
    print(f"  Bigrams: {len(prefix_bigrams)}")

    # ══════════════════════════════════════════════════════
    # TEST 3a: PREFIX BIGRAM TRANSITION MATRIX
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T3a: PREFIX BIGRAM TRANSITION MATRIX")
    print(f"{'='*70}")

    # Count PREFIX bigrams
    pre_bigram_counts = Counter(prefix_bigrams)
    pre_unigram_counts = Counter()
    for p1, p2 in prefix_bigrams:
        pre_unigram_counts[p1] += 1

    # Build vocab (top PREFIXes by unigram count)
    pre_vocab = sorted(pre_unigram_counts.keys(),
                       key=lambda p: -pre_unigram_counts[p])

    # Build transition matrix
    n_pre = len(pre_vocab)
    pre_idx = {p: i for i, p in enumerate(pre_vocab)}
    trans_matrix = np.zeros((n_pre, n_pre), dtype=float)
    for (p1, p2), count in pre_bigram_counts.items():
        if p1 in pre_idx and p2 in pre_idx:
            trans_matrix[pre_idx[p1], pre_idx[p2]] = count

    N_bigrams = trans_matrix.sum()

    # Expected under independence
    row_sums = trans_matrix.sum(axis=1)
    col_sums = trans_matrix.sum(axis=0)
    expected = np.outer(row_sums, col_sums) / N_bigrams

    # Chi-square on cells with expected >= MIN_BIGRAM_EXPECTED
    valid_mask = expected >= MIN_BIGRAM_EXPECTED
    if valid_mask.sum() > 0:
        obs_valid = trans_matrix[valid_mask]
        exp_valid = expected[valid_mask]
        chi2 = float(np.sum((obs_valid - exp_valid) ** 2 / exp_valid))
        df = int(valid_mask.sum()) - n_pre  # approximate df
        chi2_p = float(stats.chi2.sf(chi2, max(1, df)))
    else:
        chi2, chi2_p, df = 0.0, 1.0, 0

    # Cramér's V
    min_dim = min(n_pre, n_pre) - 1
    cramers_v = np.sqrt(chi2 / (N_bigrams * min_dim)) if min_dim > 0 else 0.0

    print(f"\n  PREFIX vocabulary: {n_pre}")
    print(f"  Total bigrams: {int(N_bigrams)}")
    print(f"  Chi-square: {chi2:.2f}, df≈{df}, p={chi2_p:.2e}")
    print(f"  Cramér's V: {cramers_v:.4f}")

    # Print top 10 transition matrix rows
    top_n = min(12, n_pre)
    header = "  " + f"{'From/To':<8s}" + "".join(
        f"{pre_vocab[j]:>8s}" for j in range(top_n))
    print(f"\n{header}")
    print("  " + "-" * 8 + "-" * (8 * top_n))
    for i in range(top_n):
        row = f"  {pre_vocab[i]:<8s}"
        for j in range(top_n):
            obs = int(trans_matrix[i, j])
            row += f"{obs:>8d}"
        print(row)

    # ══════════════════════════════════════════════════════
    # TEST 3b: FORBIDDEN / ENRICHED PREFIX TRANSITIONS
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T3b: FORBIDDEN / ENRICHED PREFIX TRANSITIONS")
    print(f"{'='*70}")

    # Standardized residuals: (O - E) / sqrt(E)
    std_residuals = np.zeros_like(trans_matrix)
    for i in range(n_pre):
        for j in range(n_pre):
            if expected[i, j] > 0:
                std_residuals[i, j] = ((trans_matrix[i, j] - expected[i, j]) /
                                       np.sqrt(expected[i, j]))

    # Forbidden: expected >= 5, observed = 0 or std_residual < -3
    forbidden_transitions = []
    enriched_transitions = []

    for i in range(n_pre):
        for j in range(n_pre):
            if expected[i, j] >= MIN_BIGRAM_EXPECTED:
                if trans_matrix[i, j] == 0:
                    forbidden_transitions.append({
                        'from': pre_vocab[i], 'to': pre_vocab[j],
                        'observed': 0, 'expected': float(expected[i, j]),
                        'std_residual': float(std_residuals[i, j]),
                    })
                elif std_residuals[i, j] < -3.0:
                    forbidden_transitions.append({
                        'from': pre_vocab[i], 'to': pre_vocab[j],
                        'observed': int(trans_matrix[i, j]),
                        'expected': float(expected[i, j]),
                        'std_residual': float(std_residuals[i, j]),
                    })
                elif std_residuals[i, j] > 3.0:
                    enriched_transitions.append({
                        'from': pre_vocab[i], 'to': pre_vocab[j],
                        'observed': int(trans_matrix[i, j]),
                        'expected': float(expected[i, j]),
                        'std_residual': float(std_residuals[i, j]),
                    })

    print(f"\n  FORBIDDEN (expected>={MIN_BIGRAM_EXPECTED}, std_res<-3 or obs=0):")
    print(f"  {'From':<8s} {'To':<8s} {'Obs':>6s} {'Exp':>8s} {'StdRes':>8s}")
    print(f"  {'-'*8} {'-'*8} {'-'*6} {'-'*8} {'-'*8}")
    forbidden_transitions.sort(key=lambda x: x['std_residual'])
    for ft in forbidden_transitions[:20]:
        print(f"  {ft['from']:<8s} {ft['to']:<8s} {ft['observed']:>6d} "
              f"{ft['expected']:>8.1f} {ft['std_residual']:>8.2f}")

    print(f"\n  ENRICHED (std_res > 3):")
    print(f"  {'From':<8s} {'To':<8s} {'Obs':>6s} {'Exp':>8s} {'StdRes':>8s}")
    print(f"  {'-'*8} {'-'*8} {'-'*6} {'-'*8} {'-'*8}")
    enriched_transitions.sort(key=lambda x: -x['std_residual'])
    for et in enriched_transitions[:20]:
        print(f"  {et['from']:<8s} {et['to']:<8s} {et['observed']:>6d} "
              f"{et['expected']:>8.1f} {et['std_residual']:>8.2f}")

    print(f"\n  Total forbidden: {len(forbidden_transitions)}")
    print(f"  Total enriched: {len(enriched_transitions)}")

    # ══════════════════════════════════════════════════════
    # TEST 3c: PREFIX RUN ANALYSIS
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T3c: PREFIX RUN ANALYSIS")
    print(f"{'='*70}")

    # Count runs of same PREFIX within lines
    run_lengths = defaultdict(list)  # prefix -> [run_length, ...]
    total_runs = 0
    for seq in line_sequences:
        if not seq:
            continue
        current_prefix = seq[0][0]
        current_run = 1
        for i in range(1, len(seq)):
            if seq[i][0] == current_prefix:
                current_run += 1
            else:
                run_lengths[current_prefix].append(current_run)
                total_runs += 1
                current_prefix = seq[i][0]
                current_run = 1
        run_lengths[current_prefix].append(current_run)
        total_runs += 1

    # Self-transition rate (observed vs expected)
    self_trans_observed = {}
    self_trans_expected = {}
    for p in pre_vocab:
        i = pre_idx[p]
        self_trans_observed[p] = int(trans_matrix[i, i])
        self_trans_expected[p] = float(expected[i, i])

    print(f"\n  Total runs: {total_runs}")
    print(f"\n  {'PREFIX':<8s} {'Runs':>6s} {'MeanLen':>8s} {'MaxLen':>7s} "
          f"{'Self_O':>7s} {'Self_E':>7s} {'Ratio':>7s}")
    print(f"  {'-'*8} {'-'*6} {'-'*8} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")

    run_stats = {}
    for p in sorted(run_lengths.keys(),
                    key=lambda x: -len(run_lengths[x]))[:15]:
        runs = run_lengths[p]
        mean_len = float(np.mean(runs))
        max_len = max(runs)
        self_o = self_trans_observed.get(p, 0)
        self_e = self_trans_expected.get(p, 0)
        ratio = self_o / self_e if self_e > 0 else 0

        run_stats[p] = {
            'n_runs': len(runs),
            'mean_length': mean_len,
            'max_length': max_len,
            'self_observed': self_o,
            'self_expected': float(self_e),
            'self_ratio': float(ratio),
        }

        print(f"  {p:<8s} {len(runs):>6d} {mean_len:>8.2f} {max_len:>7d} "
              f"{self_o:>7d} {self_e:>7.1f} {ratio:>7.2f}")

    # ══════════════════════════════════════════════════════
    # TEST 3d: PREFIX vs MIDDLE SEQUENTIAL INFORMATION
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T3d: PREFIX vs MIDDLE SEQUENTIAL INFORMATION")
    print(f"{'='*70}")

    # MI(PREFIX_t; PREFIX_{t+1})
    mi_pre_seq = mi_from_contingency(trans_matrix)

    # MI(MIDDLE_t; MIDDLE_{t+1})
    mid_bigram_counts = Counter(middle_bigrams)
    mid_unigram_counts = Counter()
    for m1, m2 in middle_bigrams:
        mid_unigram_counts[m1] += 1

    mid_vocab = sorted(mid_unigram_counts.keys(),
                       key=lambda m: -mid_unigram_counts[m])
    n_mid = len(mid_vocab)
    mid_idx = {m: i for i, m in enumerate(mid_vocab)}

    mid_trans = np.zeros((n_mid, n_mid), dtype=float)
    for (m1, m2), count in mid_bigram_counts.items():
        if m1 in mid_idx and m2 in mid_idx:
            mid_trans[mid_idx[m1], mid_idx[m2]] = count

    mi_mid_seq = mi_from_contingency(mid_trans)

    # MI(PREFIX_t; MIDDLE_{t+1})  — cross-component
    cross_bigrams = [(pb[0], mb[1]) for pb, mb in
                     zip(prefix_bigrams, middle_bigrams)]
    cross_counts = Counter(cross_bigrams)
    cross_matrix = np.zeros((n_pre, n_mid), dtype=float)
    for (p, m), count in cross_counts.items():
        if p in pre_idx and m in mid_idx:
            cross_matrix[pre_idx[p], mid_idx[m]] = count

    mi_cross = mi_from_contingency(cross_matrix)

    # MI(MIDDLE_t; PREFIX_{t+1})  — reverse cross
    rev_cross_bigrams = [(mb[0], pb[1]) for pb, mb in
                         zip(prefix_bigrams, middle_bigrams)]
    rev_cross_counts = Counter(rev_cross_bigrams)
    rev_cross_matrix = np.zeros((n_mid, n_pre), dtype=float)
    for (m, p), count in rev_cross_counts.items():
        if m in mid_idx and p in pre_idx:
            rev_cross_matrix[mid_idx[m], pre_idx[p]] = count

    mi_rev_cross = mi_from_contingency(rev_cross_matrix)

    # Permutation null for PREFIX sequential MI
    rng = np.random.default_rng(42)
    n_perms = 1000
    null_pre_seq = np.zeros(n_perms)
    pre_bigrams_arr = np.array([(pre_idx[p1], pre_idx[p2])
                                 for p1, p2 in prefix_bigrams
                                 if p1 in pre_idx and p2 in pre_idx])
    all_pre_indices = pre_bigrams_arr[:, 1].copy()

    for perm in range(n_perms):
        perm_targets = rng.permutation(all_pre_indices)
        perm_matrix = np.zeros((n_pre, n_pre), dtype=float)
        for k in range(len(pre_bigrams_arr)):
            perm_matrix[pre_bigrams_arr[k, 0], perm_targets[k]] += 1
        null_pre_seq[perm] = mi_from_contingency(perm_matrix)

    null_mean = float(np.mean(null_pre_seq))
    null_std = float(np.std(null_pre_seq))
    p_pre_seq = float(np.mean(null_pre_seq >= mi_pre_seq))

    print(f"\n  I(PREFIX_t; PREFIX_{{t+1}})  = {mi_pre_seq:.4f} bits "
          f"(null: {null_mean:.4f}±{null_std:.4f}, p={p_pre_seq:.4f})")
    print(f"  I(MIDDLE_t; MIDDLE_{{t+1}})  = {mi_mid_seq:.4f} bits")
    print(f"  I(PREFIX_t; MIDDLE_{{t+1}})  = {mi_cross:.4f} bits")
    print(f"  I(MIDDLE_t; PREFIX_{{t+1}})  = {mi_rev_cross:.4f} bits")

    seq_ratio = mi_pre_seq / mi_mid_seq if mi_mid_seq > 0 else 0
    print(f"\n  PREFIX/MIDDLE sequential MI ratio: {seq_ratio:.3f}")

    # ── Summary and Verdict ──────────────────────────────
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Transition matrix chi²: {chi2:.1f}, V={cramers_v:.4f}")
    print(f"  Forbidden transitions: {len(forbidden_transitions)}")
    print(f"  Enriched transitions: {len(enriched_transitions)}")
    print(f"  PREFIX sequential MI: {mi_pre_seq:.4f} bits (p={p_pre_seq:.4f})")
    print(f"  MIDDLE sequential MI: {mi_mid_seq:.4f} bits")
    print(f"  Cross MI (PRE→MID): {mi_cross:.4f} bits")
    print(f"  Cross MI (MID→PRE): {mi_rev_cross:.4f} bits")

    if (cramers_v > 0.1 and len(forbidden_transitions) >= 3
            and p_pre_seq < 0.05):
        seq_verdict = 'PREFIX_SEQUENTIAL_GRAMMAR_CONFIRMED'
        seq_detail = (f'PREFIX transitions show significant structure '
                      f'(V={cramers_v:.4f}, {len(forbidden_transitions)} '
                      f'forbidden, MI p={p_pre_seq:.4f}). '
                      f'PREFIXes follow sequential rules within lines.')
    elif cramers_v > 0.05 or len(forbidden_transitions) >= 2:
        seq_verdict = 'PREFIX_SEQUENTIAL_GRAMMAR_PARTIAL'
        seq_detail = (f'Some PREFIX sequential structure exists '
                      f'(V={cramers_v:.4f}, {len(forbidden_transitions)} '
                      f'forbidden) but not strongly grammatical.')
    else:
        seq_verdict = 'NO_PREFIX_SEQUENTIAL_GRAMMAR'
        seq_detail = (f'PREFIX transitions are approximately independent '
                      f'(V={cramers_v:.4f}). No sequential grammar.')

    print(f"\n  VERDICT: {seq_verdict}")
    print(f"  {seq_detail}")

    # ── Output ───────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'PP_INFORMATION_DECOMPOSITION',
            'test': 'T3_PREFIX_SEQUENTIAL_GRAMMAR',
        },
        'corpus': {
            'n_lines': len(line_sequences),
            'n_bigrams': len(prefix_bigrams),
            'prefix_vocab_size': n_pre,
            'middle_vocab_size': n_mid,
        },
        'transition_matrix': {
            'chi2': chi2, 'df': df, 'p': chi2_p,
            'cramers_v': float(cramers_v),
        },
        'forbidden_transitions': forbidden_transitions,
        'enriched_transitions': enriched_transitions,
        'run_stats': run_stats,
        'sequential_mi': {
            'prefix_to_prefix': float(mi_pre_seq),
            'middle_to_middle': float(mi_mid_seq),
            'prefix_to_middle': float(mi_cross),
            'middle_to_prefix': float(mi_rev_cross),
            'prefix_seq_perm_p': float(p_pre_seq),
            'prefix_seq_null_mean': null_mean,
            'seq_ratio': float(seq_ratio),
        },
        'verdict': seq_verdict,
        'verdict_detail': seq_detail,
    }

    out_path = RESULTS_DIR / 't3_prefix_sequential_grammar.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
