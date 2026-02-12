"""
Phase 3: Full Token Transition Depth
=====================================
Phase: FULL_TOKEN_TRANSITION_DEPTH

Tests whether SUFFIX encodes hidden sequential state invisible at 49-class level.
Phase 1 T4 FAILED (suffix adds zero cross-token prediction), so expectations
are calibrated toward confirming 49-class sufficiency.

T1: Three-scale transition perplexity (6-state vs 49-class vs top-100 tokens)
T3: Within-class suffix hidden state (JSD of transition distributions)
T5: Suffix transition entropy reduction

Output: t1_transition_perplexity.json, t3_within_class_jsd.json,
        t5_suffix_entropy_reduction.json
"""

import sys
import json
import functools
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats as sp_stats
from scipy.spatial.distance import jensenshannon

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

N_FOLDS = 5
N_PERMS = 1000


def load_class_map():
    path = PROJECT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
    with open(path) as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
    all_cls = sorted(set(token_to_class.values()))

    # Macro-state mapping (from C976)
    EN = ({8} | set(range(31, 50)) - {7, 30, 38, 40}) & set(all_cls)
    FL = {7, 30, 38, 40} & set(all_cls)
    CC = {10, 11, 12} & set(all_cls)
    FQ = {9, 13, 14, 23} & set(all_cls)
    AX = set(all_cls) - EN - FL - CC - FQ
    FL_HAZ = {7, 30} & set(all_cls)
    FL_SAFE = {38, 40} & set(all_cls)

    # 6-state macro mapping
    class_to_macro = {}
    for c in all_cls:
        if c in FL_HAZ: class_to_macro[c] = 0
        elif c in FQ: class_to_macro[c] = 1
        elif c in CC: class_to_macro[c] = 2
        elif c in AX and c in {3, 5, 18, 19, 42, 45}: class_to_macro[c] = 3
        elif c in FL_SAFE: class_to_macro[c] = 5
        else: class_to_macro[c] = 4  # AXM (main mass)

    return token_to_class, all_cls, class_to_macro


def build_line_sequences():
    """Build token sequences per line with class + suffix annotations."""
    morph = Morphology()
    tx = Transcript()
    token_to_class, all_cls, class_to_macro = load_class_map()

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

    lines = []
    for (folio, line), tokens in line_tokens.items():
        seq = []
        for tok in tokens:
            w = tok.word.strip()
            cls = token_to_class.get(w)
            if cls is None:
                continue
            m = word_morph.get(w)
            suffix = (m.suffix or 'NONE') if m else 'NONE'
            macro = class_to_macro.get(cls, 4)
            seq.append({
                'word': w,
                'class': cls,
                'macro': macro,
                'suffix': suffix,
                'has_suffix': suffix != 'NONE',
            })
        if len(seq) >= 2:
            lines.append(seq)

    return lines, all_cls, class_to_macro


def markov_perplexity_cv(sequences, state_fn, n_states, n_folds=5):
    """5-fold CV perplexity for first-order Markov model."""
    rng = np.random.default_rng(42)
    indices = rng.permutation(len(sequences))
    fold_size = len(indices) // n_folds

    perplexities = []
    for fold in range(n_folds):
        test_idx = set(range(fold * fold_size, min((fold+1) * fold_size, len(indices))))
        train_seqs = [sequences[indices[i]] for i in range(len(indices)) if i not in test_idx]
        test_seqs = [sequences[indices[i]] for i in sorted(test_idx)]

        # Build transition matrix with Laplace smoothing
        counts = np.ones((n_states, n_states))  # Laplace
        for seq in train_seqs:
            states = [state_fn(t) for t in seq]
            for i in range(len(states) - 1):
                if states[i] < n_states and states[i+1] < n_states:
                    counts[states[i], states[i+1]] += 1

        probs = counts / counts.sum(axis=1, keepdims=True)

        # Test perplexity
        total_ll = 0.0
        total_transitions = 0
        for seq in test_seqs:
            states = [state_fn(t) for t in seq]
            for i in range(len(states) - 1):
                s1, s2 = states[i], states[i+1]
                if s1 < n_states and s2 < n_states:
                    total_ll += np.log2(max(probs[s1, s2], 1e-30))
                    total_transitions += 1

        if total_transitions > 0:
            perplexity = 2 ** (-total_ll / total_transitions)
            perplexities.append(perplexity)

    return perplexities


def run_t1(lines, all_cls, class_to_macro):
    """T1: Three-scale transition perplexity."""
    print(f"\n{'='*70}")
    print(f"T1: THREE-SCALE TRANSITION PERPLEXITY")
    print(f"{'='*70}")

    # Build token vocab (top 100 + OTHER)
    word_counts = Counter()
    for seq in lines:
        for t in seq:
            word_counts[t['word']] += 1
    top_100 = [w for w, _ in word_counts.most_common(100)]
    top_set = set(top_100)
    word_to_idx = {w: i for i, w in enumerate(top_100)}
    other_idx = 100
    n_token_states = 101

    cls_to_idx = {c: i for i, c in enumerate(all_cls)}
    n_class = len(all_cls)
    n_macro = 6

    # 6-state perplexity
    pp_macro = markov_perplexity_cv(
        lines, lambda t: t['macro'], n_macro)

    # 49-class perplexity
    pp_class = markov_perplexity_cv(
        lines, lambda t: cls_to_idx.get(t['class'], 0), n_class)

    # Token-level perplexity
    pp_token = markov_perplexity_cv(
        lines, lambda t: word_to_idx.get(t['word'], other_idx), n_token_states)

    mean_macro = np.mean(pp_macro)
    mean_class = np.mean(pp_class)
    mean_token = np.mean(pp_token)

    print(f"\n  {'Scale':<20s} {'States':>7s} {'Mean PPL':>10s} {'Std':>8s}")
    print(f"  {'-'*20} {'-'*7} {'-'*10} {'-'*8}")
    print(f"  {'6-state macro':<20s} {n_macro:>7d} {mean_macro:>10.4f} "
          f"{np.std(pp_macro):>8.4f}")
    print(f"  {'49-class':<20s} {n_class:>7d} {mean_class:>10.4f} "
          f"{np.std(pp_class):>8.4f}")
    print(f"  {'Top-100 token':<20s} {n_token_states:>7d} {mean_token:>10.4f} "
          f"{np.std(pp_token):>8.4f}")

    improvement = (mean_class - mean_token) / mean_class * 100
    print(f"\n  Token vs class improvement: {improvement:+.2f}%")
    print(f"  C966 baseline perplexity: 1.961")

    if improvement > 3:
        t1_verdict = 'TOKEN_LEVEL_IMPROVEMENT_SIGNIFICANT'
    elif improvement > 1:
        t1_verdict = 'TOKEN_LEVEL_IMPROVEMENT_MARGINAL'
    else:
        t1_verdict = 'NO_TOKEN_LEVEL_IMPROVEMENT'

    print(f"  VERDICT: {t1_verdict}")

    result = {
        'macro_perplexities': [float(p) for p in pp_macro],
        'class_perplexities': [float(p) for p in pp_class],
        'token_perplexities': [float(p) for p in pp_token],
        'mean_macro': float(mean_macro),
        'mean_class': float(mean_class),
        'mean_token': float(mean_token),
        'improvement_pct': float(improvement),
        'verdict': t1_verdict,
    }
    with open(RESULTS_DIR / 't1_transition_perplexity.json', 'w') as f:
        json.dump(result, f, indent=2)
    return result


def run_t3(lines, all_cls):
    """T3: Within-class suffix hidden state (JSD)."""
    print(f"\n{'='*70}")
    print(f"T3: WITHIN-CLASS SUFFIX HIDDEN STATE (JSD)")
    print(f"{'='*70}")

    cls_to_idx = {c: i for i, c in enumerate(all_cls)}
    n_cls = len(all_cls)

    # Build transition data split by suffix presence
    trans_suffixed = defaultdict(lambda: np.zeros(n_cls))
    trans_bare = defaultdict(lambda: np.zeros(n_cls))

    for seq in lines:
        for i in range(len(seq) - 1):
            src_cls = seq[i]['class']
            dst_cls = seq[i+1]['class']
            dst_idx = cls_to_idx[dst_cls]
            if seq[i]['has_suffix']:
                trans_suffixed[src_cls][dst_idx] += 1
            else:
                trans_bare[src_cls][dst_idx] += 1

    # Test classes with both suffixed and bare tokens (N >= 30 each)
    testable = []
    for cls in all_cls:
        n_suf = trans_suffixed[cls].sum()
        n_bare = trans_bare[cls].sum()
        if n_suf >= 30 and n_bare >= 30:
            testable.append(cls)

    print(f"  Testable classes (both >=30): {len(testable)}")

    print(f"\n  {'Class':>6s} {'N_suf':>7s} {'N_bare':>7s} {'JSD':>8s} {'p':>10s}")
    print(f"  {'-'*6} {'-'*7} {'-'*7} {'-'*8} {'-'*10}")

    jsd_results = []
    rng = np.random.default_rng(42)

    for cls in testable:
        dist_suf = trans_suffixed[cls]
        dist_bare = trans_bare[cls]
        n_suf = int(dist_suf.sum())
        n_bare = int(dist_bare.sum())

        # Normalize
        p_suf = dist_suf / dist_suf.sum()
        p_bare = dist_bare / dist_bare.sum()

        jsd = float(jensenshannon(p_suf, p_bare) ** 2)  # JSD (squared JS distance)

        # Permutation test: merge and reshuffle
        merged = np.zeros((n_suf + n_bare, 1), dtype=int)
        merged_dst = []
        for seq in lines:
            for i in range(len(seq) - 1):
                if seq[i]['class'] == cls:
                    merged_dst.append(cls_to_idx[seq[i+1]['class']])

        null_jsd = np.zeros(N_PERMS)
        merged_labels = np.array([1]*n_suf + [0]*n_bare)  # 1=suffixed, 0=bare
        merged_dst_arr = np.array(merged_dst[:n_suf + n_bare])

        for perm in range(N_PERMS):
            perm_labels = rng.permutation(merged_labels)
            perm_suf = np.zeros(n_cls)
            perm_bare = np.zeros(n_cls)
            for j, label in enumerate(perm_labels):
                if j < len(merged_dst_arr):
                    if label == 1:
                        perm_suf[merged_dst_arr[j]] += 1
                    else:
                        perm_bare[merged_dst_arr[j]] += 1
            if perm_suf.sum() > 0 and perm_bare.sum() > 0:
                null_jsd[perm] = jensenshannon(
                    perm_suf / perm_suf.sum(),
                    perm_bare / perm_bare.sum()) ** 2

        p_val = float(np.mean(null_jsd >= jsd))
        bonf_p = p_val * len(testable)

        jsd_results.append({
            'class': cls,
            'n_suffixed': n_suf,
            'n_bare': n_bare,
            'jsd': jsd,
            'p_raw': p_val,
            'p_bonferroni': min(1.0, bonf_p),
            'significant': bonf_p < 0.01,
        })

        sig = '*' if bonf_p < 0.01 else ''
        print(f"  {cls:>6d} {n_suf:>7d} {n_bare:>7d} {jsd:>8.4f} "
              f"{p_val:>10.4f} {sig}")

    sig_count = sum(1 for r in jsd_results if r['significant'])
    mean_jsd = np.mean([r['jsd'] for r in jsd_results]) if jsd_results else 0.0

    print(f"\n  Significant classes (Bonferroni p<0.01): {sig_count}/{len(testable)}")
    print(f"  Mean JSD: {mean_jsd:.4f}")

    if sig_count >= 5 and mean_jsd > 0.05:
        t3_verdict = 'SUFFIX_HIDDEN_STATE_CONFIRMED'
    elif sig_count >= 2:
        t3_verdict = 'SUFFIX_HIDDEN_STATE_WEAK'
    else:
        t3_verdict = 'NO_SUFFIX_HIDDEN_STATE'

    print(f"  VERDICT: {t3_verdict}")

    result = {
        'testable_classes': len(testable),
        'significant_count': sig_count,
        'mean_jsd': float(mean_jsd),
        'class_results': jsd_results,
        'verdict': t3_verdict,
    }
    with open(RESULTS_DIR / 't3_within_class_jsd.json', 'w') as f:
        json.dump(result, f, indent=2)
    return result


def run_t5(lines, all_cls):
    """T5: Suffix transition entropy reduction."""
    print(f"\n{'='*70}")
    print(f"T5: SUFFIX TRANSITION ENTROPY REDUCTION")
    print(f"{'='*70}")

    cls_to_idx = {c: i for i, c in enumerate(all_cls)}
    n_cls = len(all_cls)

    # H(NEXT_CLASS | CLASS) — unconditional on suffix
    trans_all = defaultdict(lambda: np.zeros(n_cls))
    for seq in lines:
        for i in range(len(seq) - 1):
            src = seq[i]['class']
            dst_idx = cls_to_idx[seq[i+1]['class']]
            trans_all[src][dst_idx] += 1

    def conditional_entropy(trans_dict):
        """H(NEXT | CURRENT) weighted by P(CURRENT)."""
        total = sum(d.sum() for d in trans_dict.values())
        h = 0.0
        for src, dst_counts in trans_dict.items():
            n = dst_counts.sum()
            if n == 0:
                continue
            p_src = n / total
            p_dst = dst_counts / n
            p_dst = p_dst[p_dst > 0]
            h += p_src * (-np.sum(p_dst * np.log2(p_dst)))
        return h

    h_unconditional = conditional_entropy(trans_all)
    print(f"  H(NEXT_CLASS | CLASS) = {h_unconditional:.4f} bits")

    # H(NEXT_CLASS | CLASS, SUFFIX) — conditioned on suffix
    trans_by_suffix = defaultdict(lambda: defaultdict(lambda: np.zeros(n_cls)))
    for seq in lines:
        for i in range(len(seq) - 1):
            src = seq[i]['class']
            suf = seq[i]['suffix']
            dst_idx = cls_to_idx[seq[i+1]['class']]
            trans_by_suffix[(src, suf)][src][dst_idx] += 1

    # Compute H(NEXT | CLASS, SUFFIX)
    total = sum(d.sum() for v in trans_by_suffix.values() for d in v.values())
    h_conditioned = 0.0
    for (src, suf), src_dict in trans_by_suffix.items():
        for s, dst_counts in src_dict.items():
            n = dst_counts.sum()
            if n == 0:
                continue
            p = n / total
            p_dst = dst_counts / n
            p_dst = p_dst[p_dst > 0]
            h_conditioned += p * (-np.sum(p_dst * np.log2(p_dst)))

    reduction = h_unconditional - h_conditioned
    pct_reduction = (reduction / h_unconditional * 100) if h_unconditional > 0 else 0

    print(f"  H(NEXT_CLASS | CLASS, SUFFIX) = {h_conditioned:.4f} bits")
    print(f"  Reduction: {reduction:.4f} bits ({pct_reduction:.2f}%)")
    print(f"  C966 baseline H: ~{np.log2(1.961):.4f} bits (from perplexity 1.961)")

    # Per-suffix contribution
    suffix_counts = Counter()
    suffix_reduction = defaultdict(float)
    for seq in lines:
        for i in range(len(seq) - 1):
            suffix_counts[seq[i]['suffix']] += 1

    print(f"\n  Per-suffix analysis:")
    print(f"  {'SUFFIX':<10s} {'N':>6s} {'H_with':>8s}")
    print(f"  {'-'*10} {'-'*6} {'-'*8}")

    # For each suffix, compute average entropy of next-class given (class, that suffix)
    for suf in sorted(suffix_counts.keys(), key=lambda s: -suffix_counts[s]):
        if suffix_counts[suf] < 30:
            continue
        suf_trans = {k: v for (k, s), v in trans_by_suffix.items() if s == suf}
        if suf_trans:
            total_suf = sum(d.sum() for v in suf_trans.values() for d in v.values() if isinstance(v, dict))
            # Simpler: just count transitions with this suffix
            n_trans = 0
            h_suf = 0.0
            for (src, s), src_dict in trans_by_suffix.items():
                if s != suf:
                    continue
                for s2, dst_counts in src_dict.items():
                    n = dst_counts.sum()
                    if n == 0:
                        continue
                    n_trans += n
                    p_dst = dst_counts / n
                    p_dst = p_dst[p_dst > 0]
                    h_suf += n * (-np.sum(p_dst * np.log2(p_dst)))

            if n_trans > 0:
                h_avg = h_suf / n_trans
                print(f"  {suf:<10s} {int(n_trans):>6d} {h_avg:>8.4f}")

    if reduction > 0.08:
        t5_verdict = 'SUFFIX_ENTROPY_REDUCTION_SIGNIFICANT'
    elif reduction > 0.03:
        t5_verdict = 'SUFFIX_ENTROPY_REDUCTION_MARGINAL'
    else:
        t5_verdict = 'NO_SUFFIX_ENTROPY_REDUCTION'

    print(f"\n  VERDICT: {t5_verdict}")

    result = {
        'h_unconditional': float(h_unconditional),
        'h_conditioned': float(h_conditioned),
        'reduction_bits': float(reduction),
        'reduction_pct': float(pct_reduction),
        'verdict': t5_verdict,
    }
    with open(RESULTS_DIR / 't5_suffix_entropy_reduction.json', 'w') as f:
        json.dump(result, f, indent=2)
    return result


def main():
    print("Building sequences...")
    lines, all_cls, class_to_macro = build_line_sequences()
    total_tokens = sum(len(s) for s in lines)
    print(f"  {len(lines)} lines, {total_tokens} tokens")

    t1 = run_t1(lines, all_cls, class_to_macro)
    t3 = run_t3(lines, all_cls)
    t5 = run_t5(lines, all_cls)

    print(f"\n{'='*70}")
    print(f"PHASE 3 COMPLETE")
    print(f"{'='*70}")
    print(f"  T1: {t1['verdict']} (token vs class: {t1['improvement_pct']:+.2f}%)")
    print(f"  T3: {t3['verdict']} ({t3['significant_count']}/{t3['testable_classes']} sig)")
    print(f"  T5: {t5['verdict']} ({t5['reduction_bits']:.4f} bits)")

    # Composite verdict
    passes = sum([
        t1['verdict'] != 'NO_TOKEN_LEVEL_IMPROVEMENT',
        t3['verdict'] != 'NO_SUFFIX_HIDDEN_STATE',
        t5['verdict'] != 'NO_SUFFIX_ENTROPY_REDUCTION',
    ])

    if passes >= 2:
        composite = 'HIDDEN_STATE_EXISTS'
    elif passes == 1:
        composite = 'WEAK_HIDDEN_STATE'
    else:
        composite = 'NO_HIDDEN_STATE_49CLASS_SUFFICIENT'

    print(f"\n  COMPOSITE VERDICT: {composite}")
    print(f"  {passes}/3 tests show structure beyond 49-class")

    with open(RESULTS_DIR / 'composite_verdict.json', 'w') as f:
        json.dump({
            't1': t1['verdict'], 't3': t3['verdict'], 't5': t5['verdict'],
            'passes': passes, 'composite': composite,
        }, f, indent=2)


if __name__ == '__main__':
    main()
