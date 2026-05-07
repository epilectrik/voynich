#!/usr/bin/env python3
"""
T3: Token class predicts successor entropy.

Hypothesis (one-sided): E[H_succ | INFRA] < E[H_succ | RI] at MWU p<0.01,
with mean difference > 0.3 bits.

H_succ(s) = -sum_s' p(s'|s) log_2 p(s'|s)
Computed per token TYPE with n>=3 occurrences in Currier B.
"""
import sys
import json
import math
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import (
    Transcript, Morphology, TokenClass, load_middle_classes,
)


# Same INFRA prefix set used by RecordAnalyzer
INFRA_PREFIXES = {'da', 'do', 'sa', 'so'}


def classify(word, morph_engine, ri_middles, pp_middles):
    """Apply RecordAnalyzer.classify_token logic to a Currier B token."""
    morph = morph_engine.extract(word)
    prefix = morph.prefix
    middle = morph.middle

    if prefix in INFRA_PREFIXES:
        if middle and len(middle) <= 3:
            return TokenClass.INFRA
    if middle in ri_middles:
        return TokenClass.RI
    if middle in pp_middles:
        return TokenClass.PP
    return TokenClass.UNKNOWN


def filter_currier_b():
    """All Currier B tokens, H-only, no labels, no asterisks."""
    tx = Transcript()
    tokens = []
    for tok in tx.currier_b():  # already excludes labels and uncertain
        if not tok.word:
            continue
        tokens.append(tok.word)
    return tokens


def compute_hsucc(tokens, min_count=3):
    """
    Compute successor entropy per token TYPE.

    For each type s with count >= min_count, compute:
      H_succ(s) = -sum_s' p(s'|s) log_2 p(s'|s)

    Where p(s'|s) is the empirical distribution of next-token given s.
    Final-position occurrences (where s is the last token) contribute no
    successor and are excluded from the conditional distribution.

    Returns: dict {type: {n, n_with_successor, h_succ, distinct_succ}}
    """
    successor_counts = defaultdict(Counter)
    type_counts = Counter(tokens)

    for i in range(len(tokens) - 1):
        cur = tokens[i]
        nxt = tokens[i+1]
        successor_counts[cur][nxt] += 1

    out = {}
    for tok_type, count in type_counts.items():
        if count < min_count:
            continue
        succ_counter = successor_counts.get(tok_type)
        if not succ_counter:
            continue
        total_with_succ = sum(succ_counter.values())
        if total_with_succ < 2:  # need at least 2 successor instances for H to be meaningful
            continue
        h = 0.0
        for c in succ_counter.values():
            p = c / total_with_succ
            if p > 0:
                h -= p * math.log2(p)
        out[tok_type] = {
            'n': count,
            'n_with_successor': total_with_succ,
            'h_succ': h,
            'distinct_succ': len(succ_counter),
        }
    return out


def mannwhitney_u(x, y):
    """Compute Mann-Whitney U test statistic and approximate one-sided p
    (testing whether x is stochastically less than y).

    Returns (u_x, mean_x, mean_y, p_one_sided_x_lt_y).
    """
    n_x, n_y = len(x), len(y)
    combined = [(v, 'x') for v in x] + [(v, 'y') for v in y]
    combined.sort(key=lambda t: t[0])

    # Assign ranks (with average for ties)
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0  # 1-indexed average
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    rank_sum_x = sum(r for r, (_, label) in zip(ranks, combined) if label == 'x')
    u_x = rank_sum_x - n_x * (n_x + 1) / 2.0
    u_y = n_x * n_y - u_x

    # Normal approximation for p-value
    mean_u = n_x * n_y / 2.0
    std_u = math.sqrt(n_x * n_y * (n_x + n_y + 1) / 12.0)
    z = (u_x - mean_u) / std_u

    # One-sided p (x stochastically smaller than y => smaller ranks => smaller U_x)
    # P(Z <= z) for z computed above; smaller z => smaller p
    p_one_sided = 0.5 * (1 + math.erf(z / math.sqrt(2)))

    mean_x = sum(x) / n_x
    mean_y = sum(y) / n_y
    return u_x, mean_x, mean_y, p_one_sided


def main():
    print("Loading Currier B tokens (H-only, no labels, no asterisks)...")
    tokens = filter_currier_b()
    print(f"  Total Currier B tokens: {len(tokens)}")
    print(f"  Unique types: {len(set(tokens))}")

    print("\nComputing H_succ per token type (min count = 3)...")
    h_data = compute_hsucc(tokens, min_count=3)
    print(f"  Token types with H_succ: {len(h_data)}")

    print("\nClassifying token types via Morphology + RI/PP middle classes...")
    ri_middles, pp_middles = load_middle_classes()
    print(f"  Loaded {len(ri_middles)} RI middles, {len(pp_middles)} PP middles")
    morph_engine = Morphology()

    by_class = defaultdict(list)
    examples = defaultdict(list)
    for tok_type, info in h_data.items():
        cls = classify(tok_type, morph_engine, ri_middles, pp_middles)
        info['class'] = cls
        by_class[cls].append(info['h_succ'])
        if len(examples[cls]) < 5:
            examples[cls].append((tok_type, info['h_succ'], info['n']))

    print(f"\n  Class distribution (token types with n>=3):")
    for cls in ['INFRA', 'RI', 'PP', 'UNKNOWN']:
        n = len(by_class[cls])
        if n > 0:
            mean_h = sum(by_class[cls]) / n
            print(f"    {cls}: {n} types, mean H_succ = {mean_h:.3f}")
            print(f"      examples: {examples[cls][:5]}")

    # T3: INFRA vs RI
    infra_h = by_class['INFRA']
    ri_h = by_class['RI']

    if len(infra_h) < 3 or len(ri_h) < 3:
        print(f"\n  WARNING: insufficient sample size for MWU test")
        print(f"    INFRA n={len(infra_h)}, RI n={len(ri_h)}")
        verdict = 'INSUFFICIENT_DATA'
        u_stat = None
        p_one_sided = None
        mean_infra = sum(infra_h)/len(infra_h) if infra_h else None
        mean_ri = sum(ri_h)/len(ri_h) if ri_h else None
        diff = (mean_ri - mean_infra) if (mean_ri is not None and mean_infra is not None) else None
    else:
        u_stat, mean_infra, mean_ri, p_one_sided = mannwhitney_u(infra_h, ri_h)
        diff = mean_ri - mean_infra
        print(f"\n  T3 statistic:")
        print(f"    n(INFRA) = {len(infra_h)}, n(RI) = {len(ri_h)}")
        print(f"    mean H_succ INFRA = {mean_infra:.3f}")
        print(f"    mean H_succ RI    = {mean_ri:.3f}")
        print(f"    Diff (RI - INFRA) = {diff:.3f} bits")
        print(f"    MWU U(INFRA) = {u_stat:.1f}")
        print(f"    One-sided p (INFRA < RI) = {p_one_sided:.6f}")

        pass_p = p_one_sided < 0.01
        pass_diff = diff > 0.3
        pass_dir = mean_infra < mean_ri
        verdict = "PASS" if (pass_p and pass_diff and pass_dir) else "FAIL"

        print(f"\n  Pre-reg threshold: MWU p<0.01 AND |diff|>0.3 AND INFRA<RI")
        print(f"  Verdict: {verdict}")

    out = {
        'test': 'T3',
        'hypothesis': 'E[H_succ|INFRA] < E[H_succ|RI], MWU p<0.01, diff>0.3 bits',
        'min_token_count': 3,
        'corpus': 'Currier B',
        'n_currier_b_tokens': len(tokens),
        'n_currier_b_types': len(set(tokens)),
        'n_types_with_hsucc': len(h_data),
        'class_counts': {cls: len(by_class[cls]) for cls in ['INFRA','RI','PP','UNKNOWN']},
        'class_means': {
            cls: (sum(by_class[cls])/len(by_class[cls])) if by_class[cls] else None
            for cls in ['INFRA','RI','PP','UNKNOWN']
        },
        'mwu_u_infra': u_stat,
        'mean_infra': mean_infra,
        'mean_ri': mean_ri,
        'diff_ri_minus_infra': diff,
        'p_one_sided_infra_lt_ri': p_one_sided,
        'verdict': verdict,
    }

    out_path = Path(__file__).resolve().parent.parent / 'results' / 't3_hsucc_by_class.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
