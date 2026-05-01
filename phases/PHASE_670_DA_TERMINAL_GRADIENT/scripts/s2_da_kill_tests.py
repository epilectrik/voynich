"""
Phase 670 Script 2: kill tests for da-prefix positional gradient.

TEST 1: Bimodality check (does a "uniform" mean hide a U-shape?)
        Decile distribution + bimodality coefficient.

TEST 2: Body-only analysis (exclude line 1 of each folio).
        Confirms gradient is not driven by paragraph-initial enrichment.

TEST 3: dal-dam adjacency confound. Does dal's late position only hold
        when dam is in the same line?

TEST 4: Folio-level permutation. Shuffle tokens within each folio
        (across lines) — tests if the within-line permutation null is
        too narrow.

Output: phases/PHASE_670_DA_TERMINAL_GRADIENT/results/da_kill_tests.json
"""

import json
import random
from collections import defaultdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript

random.seed(42)

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "da_kill_tests.json"
DA_TOKENS = ["dar", "dal", "dam", "daiin", "dain", "dair"]


def gather_lines(tokens, min_len=4):
    by_line = defaultdict(list)
    for t in tokens:
        if "*" in t.word or not t.word.strip():
            continue
        if t.is_label:
            continue
        by_line[(t.folio, t.line)].append((t.word, t.line))
    return {k: v for k, v in by_line.items() if len(v) >= min_len}


def get_positions(lines, target):
    out = []
    for (folio, _), words in lines.items():
        n = len(words)
        for i, (w, _) in enumerate(words):
            if w == target:
                out.append((folio, i / (n - 1), [x[0] for x in words]))
    return out


def deciles(values):
    bins = [0] * 10
    for v in values:
        b = min(9, int(v * 10))
        bins[b] += 1
    total = len(values)
    return [b / total * 100 for b in bins]


def variance(values):
    n = len(values)
    m = sum(values) / n
    return sum((v - m) ** 2 for v in values) / n, m


def skew_kurt(values):
    n = len(values)
    m = sum(values) / n
    var = sum((v - m) ** 2 for v in values) / n
    std = var ** 0.5
    if std == 0:
        return 0, 0
    skew = sum(((v - m) / std) ** 3 for v in values) / n
    kurt = sum(((v - m) / std) ** 4 for v in values) / n
    return skew, kurt


def bimod_coef(values):
    skew, kurt = skew_kurt(values)
    return (skew * skew + 1) / kurt if kurt > 0 else 0


def folio_permutation(b_tokens, target, n_perm=10000):
    """Shuffle tokens within each folio (across lines), measure mean position."""
    by_folio_line = defaultdict(lambda: defaultdict(list))
    for t in b_tokens:
        if "*" in t.word or not t.word.strip():
            continue
        if t.is_label:
            continue
        by_folio_line[t.folio][t.line].append(t.word)

    folios = {}
    for folio, lines in by_folio_line.items():
        all_words = []
        line_lens = []
        for line_id, words in lines.items():
            if len(words) >= 4:
                all_words.extend(words)
                line_lens.append(len(words))
        if all_words and line_lens:
            folios[folio] = (all_words, line_lens)

    def measure(folios_data):
        positions = []
        for folio, (words, line_lens) in folios_data.items():
            idx = 0
            for ll in line_lens:
                line = words[idx:idx + ll]
                idx += ll
                for i, w in enumerate(line):
                    if w == target:
                        positions.append(i / (ll - 1))
        return sum(positions) / len(positions) if positions else None

    actual = measure(folios)
    if actual is None:
        return None

    extreme = 0
    rand_means = []
    for _ in range(n_perm):
        shuffled_folios = {}
        for folio, (words, line_lens) in folios.items():
            sw = words[:]
            random.shuffle(sw)
            shuffled_folios[folio] = (sw, line_lens)
        rm = measure(shuffled_folios)
        if rm is not None:
            rand_means.append(rm)
            if abs(rm - 0.5) >= abs(actual - 0.5):
                extreme += 1

    return {
        "actual_mean": actual,
        "random_mean": sum(rand_means) / len(rand_means) if rand_means else None,
        "p_value": extreme / n_perm,
    }


def main():
    tx = Transcript()
    b_tokens = list(tx.currier_b())
    lines = gather_lines(b_tokens)

    results = {"bimodality": {}, "body_only": {}, "dal_dam_adjacency": {}, "folio_permutation": {}}

    print("=== TEST 1: BIMODALITY CHECK ===")
    for tok in DA_TOKENS:
        positions = [p for _, p, _ in get_positions(lines, tok)]
        if not positions:
            continue
        var, m = variance(positions)
        std = var ** 0.5
        decs = deciles(positions)
        skew, kurt = skew_kurt(positions)
        bc = bimod_coef(positions)
        results["bimodality"][tok] = {
            "n": len(positions), "mean": m, "std": std, "var": var,
            "deciles_pct": decs, "skew": skew, "kurt": kurt, "bimod_coef": bc,
            "bimodal": bc > 0.555,
        }
        flag = " (bimodal!)" if bc > 0.555 else ""
        print(f"{tok:<8} n={len(positions):>4}  mean={m:.3f}  std={std:.3f}  bimod_coef={bc:.3f}{flag}")
        print(f"           deciles: " + "  ".join(f"{d:4.1f}" for d in decs))

    print("\n=== TEST 2: BODY-ONLY ANALYSIS (exclude line 1 of each folio) ===")
    # Identify line-1 of each folio: the first line by line_number sort within each folio
    folio_lines = defaultdict(list)
    for (folio, line_id) in lines.keys():
        folio_lines[folio].append(line_id)
    line1_keys = set()
    for folio, line_ids in folio_lines.items():
        # line_ids may be like "1", "2", "1.1" etc; pick the lexicographically smallest numeric one
        try:
            sorted_lines = sorted(line_ids, key=lambda x: (int(x.split(".")[0]) if x.split(".")[0].isdigit() else 999, x))
            if sorted_lines:
                line1_keys.add((folio, sorted_lines[0]))
        except Exception:
            pass
    body_lines_clean = {k: v for k, v in lines.items() if k not in line1_keys}
    for tok in DA_TOKENS:
        all_pos = [p for _, p, _ in get_positions(lines, tok)]
        body_pos = [p for _, p, _ in get_positions(body_lines_clean, tok)]
        if all_pos and body_pos:
            results["body_only"][tok] = {
                "all_mean": sum(all_pos) / len(all_pos),
                "body_mean": sum(body_pos) / len(body_pos),
                "diff": sum(body_pos) / len(body_pos) - sum(all_pos) / len(all_pos),
            }

    print("\n=== TEST 3: DAL-DAM ADJACENCY ===")
    dal_with = []
    dal_without = []
    for (folio, _), words in lines.items():
        word_list = [w for w, _ in words]
        has_dam = "dam" in word_list
        n = len(word_list)
        for i, w in enumerate(word_list):
            if w == "dal":
                if has_dam:
                    dal_with.append(i / (n - 1))
                else:
                    dal_without.append(i / (n - 1))
    results["dal_dam_adjacency"] = {
        "dal_with_dam_n": len(dal_with),
        "dal_with_dam_mean": sum(dal_with) / len(dal_with) if dal_with else None,
        "dal_without_dam_n": len(dal_without),
        "dal_without_dam_mean": sum(dal_without) / len(dal_without) if dal_without else None,
    }

    print("\n=== TEST 4: FOLIO-LEVEL PERMUTATION ===")
    for tok in DA_TOKENS:
        r = folio_permutation(b_tokens, tok, n_perm=10000)
        if r:
            results["folio_permutation"][tok] = r
            print(f"{tok:<8} actual={r['actual_mean']:.3f} rand={r['random_mean']:.3f} p={r['p_value']:.4f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(results, indent=2))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
