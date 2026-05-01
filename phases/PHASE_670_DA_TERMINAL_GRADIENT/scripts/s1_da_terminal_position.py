"""
Phase 670 Script 1: da-prefix terminal position analysis (Currier B).

For each da-prefix family token (dar, dal, dam, daiin, dain, dair):
  - Compute mean normalized line-position (0=start, 1=end)
  - Permutation test (10,000 within-line shuffles) for positional non-randomness
  - Length control (token length vs position)
  - Cross-system check (Currier A means)

Also: terminal-atom positional summary across ALL B tokens (y, n, l, r, m, o, s, d).

Output: phases/PHASE_670_DA_TERMINAL_GRADIENT/results/da_terminal_position.json
"""

import json
import random
from collections import defaultdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript

random.seed(42)

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "da_terminal_position.json"

DA_TOKENS = ["dar", "dal", "dam", "daiin", "dain", "dair"]
TERMINALS = ["y", "n", "l", "r", "m", "o", "s", "d"]


def gather_lines(tokens, min_len=4):
    by_line = defaultdict(list)
    for t in tokens:
        if "*" in t.word or not t.word.strip():
            continue
        if t.is_label:
            continue
        by_line[(t.folio, t.line)].append(t.word)
    return {k: v for k, v in by_line.items() if len(v) >= min_len}


def position_stats(lines, target):
    positions = []
    for words in lines.values():
        n = len(words)
        for i, w in enumerate(words):
            if w == target:
                positions.append(i / (n - 1))
    if not positions:
        return None
    n = len(positions)
    mean = sum(positions) / n
    start = sum(1 for p in positions if p < 1 / 3) / n
    mid = sum(1 for p in positions if 1 / 3 <= p < 2 / 3) / n
    end = sum(1 for p in positions if p >= 2 / 3) / n
    return {"n": n, "mean": mean, "start_pct": start, "mid_pct": mid, "end_pct": end}


def permutation_test(lines, target, n_perm=10000):
    actual = position_stats(lines, target)
    if actual is None:
        return None
    actual_mean = actual["mean"]
    extreme = 0
    rand_means = []
    for _ in range(n_perm):
        positions = []
        for words in lines.values():
            shuffled = words[:]
            random.shuffle(shuffled)
            n = len(shuffled)
            for i, w in enumerate(shuffled):
                if w == target:
                    positions.append(i / (n - 1))
        if not positions:
            continue
        rm = sum(positions) / len(positions)
        rand_means.append(rm)
        if abs(rm - 0.5) >= abs(actual_mean - 0.5):
            extreme += 1
    rand_mean_avg = sum(rand_means) / len(rand_means)
    return {
        "actual_mean": actual_mean,
        "random_mean": rand_mean_avg,
        "diff": actual_mean - rand_mean_avg,
        "p_value": extreme / n_perm,
    }


def terminal_atom_stats(lines):
    out = {}
    for term in TERMINALS:
        positions = []
        for words in lines.values():
            n = len(words)
            for i, w in enumerate(words):
                if w.endswith(term) and len(w) >= 2:
                    positions.append(i / (n - 1))
        if not positions:
            continue
        n = len(positions)
        mean = sum(positions) / n
        start = sum(1 for p in positions if p < 1 / 3) / n
        mid = sum(1 for p in positions if 1 / 3 <= p < 2 / 3) / n
        end = sum(1 for p in positions if p >= 2 / 3) / n
        out[term] = {"n": n, "mean": mean, "start_pct": start, "mid_pct": mid, "end_pct": end}
    return out


def main():
    tx = Transcript()
    b_tokens = list(tx.currier_b())
    a_tokens = list(tx.currier_a())

    b_lines = gather_lines(b_tokens)
    a_lines = gather_lines(a_tokens)

    results = {
        "currier_b": {"da_tokens": {}, "terminals_all": terminal_atom_stats(b_lines)},
        "currier_a": {"da_tokens": {}},
        "permutation_tests": {},
        "length_control": {},
    }

    for tok in DA_TOKENS:
        results["currier_b"]["da_tokens"][tok] = position_stats(b_lines, tok)
        results["currier_a"]["da_tokens"][tok] = position_stats(a_lines, tok)
        results["permutation_tests"][tok] = permutation_test(b_lines, tok, n_perm=10000)
        results["length_control"][tok] = {"length_chars": len(tok)}

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(results, indent=2))
    print(f"Wrote {OUT_PATH}")

    print("\n=== DA-PREFIX TERMINAL POSITION (Currier B, lines >= 4 tokens) ===")
    print(f"{'Token':<10} {'N':>5} {'Mean':>6}  {'Start%':>6}  {'Mid%':>6}  {'End%':>6}")
    for tok in DA_TOKENS:
        s = results["currier_b"]["da_tokens"][tok]
        if s:
            print(f"{tok:<10} {s['n']:>5} {s['mean']:>6.3f}  {s['start_pct']*100:>5.1f}%  {s['mid_pct']*100:>5.1f}%  {s['end_pct']*100:>5.1f}%")

    print("\n=== PERMUTATION TEST (10,000 shuffles) ===")
    print(f"{'Token':<10} {'Actual':>7} {'Random':>7} {'Diff':>7} {'p-val':>8}")
    for tok in DA_TOKENS:
        p = results["permutation_tests"][tok]
        if p:
            print(f"{tok:<10} {p['actual_mean']:>7.3f} {p['random_mean']:>7.3f} {p['diff']:>+7.3f} {p['p_value']:>8.4f}")


if __name__ == "__main__":
    main()
