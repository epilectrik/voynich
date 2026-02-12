#!/usr/bin/env python3
"""
T1: Build Transition Data
MINIMAL_STATE_AUTOMATON phase

Extracts 49x49 class-level and 5x5 role-level transition matrices from B corpus.
Computes counts, probabilities, marginals, stationary distribution.
"""

import sys
import json
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = Path(__file__).parent.parent / 'results'


def load_class_map():
    path = PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
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
    role_names = ['CC', 'FQ', 'EN', 'FL', 'AX']
    for c in all_cls:
        if c in CC: class_to_role[c] = 'CC'
        elif c in FQ: class_to_role[c] = 'FQ'
        elif c in EN: class_to_role[c] = 'EN'
        elif c in FL: class_to_role[c] = 'FL'
        elif c in AX: class_to_role[c] = 'AX'

    return token_to_class, all_cls, class_to_role, role_names


def run():
    t_start = time.time()
    print("=" * 70)
    print("T1: Build Transition Data")
    print("MINIMAL_STATE_AUTOMATON phase")
    print("=" * 70)

    # Load
    print("\n[1/4] Loading data...")
    token_to_class, all_classes, class_to_role, role_names = load_class_map()
    n = len(all_classes)
    cls_to_idx = {c: i for i, c in enumerate(all_classes)}
    role_to_idx = {r: i for i, r in enumerate(role_names)}

    tx = Transcript()
    lines = []
    current_key = None
    current_seq = []

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        cls = token_to_class.get(w)
        if cls is None:
            continue
        key = (token.folio, token.line)
        if key != current_key:
            if current_seq:
                lines.append(current_seq)
            current_seq = []
            current_key = key
        current_seq.append(cls)

    if current_seq:
        lines.append(current_seq)

    total_tokens = sum(len(s) for s in lines)
    print(f"  {len(lines)} lines, {total_tokens} tokens, {n} classes")

    # 49x49 count matrix
    print("\n[2/4] Building 49x49 transition matrix...")
    counts = np.zeros((n, n), dtype=int)
    for seq in lines:
        for i in range(len(seq) - 1):
            a, b = cls_to_idx[seq[i]], cls_to_idx[seq[i + 1]]
            counts[a][b] += 1

    total_transitions = int(counts.sum())
    print(f"  {total_transitions} transitions")

    # Row-normalized probability matrix
    row_sums = counts.sum(axis=1, keepdims=True).astype(float)
    probs = np.divide(counts, row_sums, where=row_sums > 0,
                      out=np.zeros_like(counts, dtype=float))

    # Marginal frequencies
    class_freq = Counter()
    for seq in lines:
        for c in seq:
            class_freq[c] += 1
    marginals = np.array([class_freq.get(c, 0) for c in all_classes], dtype=float)
    marginals /= marginals.sum()

    # Stationary distribution (eigenvector of P^T for eigenvalue 1)
    eigvals, eigvecs = np.linalg.eig(probs.T)
    idx_one = np.argmin(np.abs(eigvals - 1.0))
    stationary = np.abs(eigvecs[:, idx_one])
    stationary /= stationary.sum()

    print(f"  Stationary dist entropy: {-np.sum(stationary * np.log2(stationary + 1e-15)):.2f} bits")
    print(f"  Zero entries: {int((counts == 0).sum())} / {n*n} ({(counts == 0).sum()/(n*n):.1%})")

    # 5x5 role matrix
    print("\n[3/4] Building 5x5 role-level matrix...")
    n_roles = len(role_names)
    role_counts = np.zeros((n_roles, n_roles), dtype=int)
    for seq in lines:
        for i in range(len(seq) - 1):
            r_a = role_to_idx[class_to_role[seq[i]]]
            r_b = role_to_idx[class_to_role[seq[i + 1]]]
            role_counts[r_a][r_b] += 1

    role_row_sums = role_counts.sum(axis=1, keepdims=True).astype(float)
    role_probs = np.divide(role_counts, role_row_sums, where=role_row_sums > 0,
                           out=np.zeros_like(role_counts, dtype=float))

    print("  Role transition matrix:")
    header = "        " + "  ".join(f"{r:>6}" for r in role_names)
    print(header)
    for i, r in enumerate(role_names):
        row = "  ".join(f"{role_probs[i][j]:>6.3f}" for j in range(n_roles))
        print(f"  {r:>5} {row}")

    # Role marginals
    role_freq = Counter()
    for seq in lines:
        for c in seq:
            role_freq[class_to_role[c]] += 1
    role_marginals = {r: role_freq.get(r, 0) / total_tokens for r in role_names}
    print(f"\n  Role marginals: {', '.join(f'{r}={v:.3f}' for r, v in role_marginals.items())}")

    # Per-class details
    print("\n[4/4] Per-class summary...")
    class_details = {}
    for c in all_classes:
        i = cls_to_idx[c]
        out_degree = int((counts[i] > 0).sum())
        in_degree = int((counts[:, i] > 0).sum())
        class_details[str(c)] = {
            'role': class_to_role[c],
            'frequency': int(class_freq.get(c, 0)),
            'marginal': round(float(marginals[i]), 6),
            'stationary': round(float(stationary[i]), 6),
            'out_degree': out_degree,
            'in_degree': in_degree,
        }

    # Top 10 most frequent
    top10 = sorted(class_details.items(), key=lambda x: -x[1]['frequency'])[:10]
    print("  Top 10 classes:")
    for cid, d in top10:
        print(f"    Class {cid:>3} ({d['role']:>2}): freq={d['frequency']:>4}, "
              f"out={d['out_degree']:>2}, in={d['in_degree']:>2}")

    # Save
    print("\nSaving...")
    results = {
        'test': 'T1_build_transition_data',
        'n_classes': n,
        'n_lines': len(lines),
        'n_tokens': total_tokens,
        'n_transitions': total_transitions,
        'classes': [int(c) for c in all_classes],
        'class_to_role': {str(c): class_to_role[c] for c in all_classes},
        'role_names': role_names,
        'counts_49x49': counts.tolist(),
        'probs_49x49': [[round(float(x), 6) for x in row] for row in probs],
        'marginals': [round(float(x), 6) for x in marginals],
        'stationary': [round(float(x), 6) for x in stationary],
        'role_counts_5x5': role_counts.tolist(),
        'role_probs_5x5': [[round(float(x), 4) for x in row] for row in role_probs],
        'role_marginals': role_marginals,
        'class_details': class_details,
        'zero_fraction': round(float((counts == 0).sum()) / (n * n), 4),
        'line_lengths': [len(s) for s in lines],
        'elapsed_seconds': round(time.time() - t_start, 1),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't1_transition_data.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {RESULTS_DIR / 't1_transition_data.json'}")
    print(f"Total time: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    run()
