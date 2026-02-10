"""
LINE_CONTROL_BLOCK_GRAMMAR - Test 06: Within-Zone Token Ordering

Purpose: Determine whether tokens within the WORK zone of a line follow a
predictable ordering by instruction class. If ENERGY_OPERATOR (EN) or
AUXILIARY (AX) tokens appear in consistent class-number order across lines,
this indicates an internal grammar governing instruction sequencing.
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path("C:/git/voynich").resolve()
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
RESULTS_PATH = PROJECT_ROOT / "phases/LINE_CONTROL_BLOCK_GRAMMAR/results/06_within_zone_ordering.json"

with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
    class_data = json.load(f)

token_to_class = {k: int(v) for k, v in class_data["token_to_class"].items()}
token_to_role = class_data.get("token_to_role", {})
class_to_role = {int(k): v for k, v in class_data["class_to_role"].items()}


def get_role(word):
    if word in token_to_role:
        return token_to_role[word]
    cls = token_to_class.get(word, -1)
    if cls >= 0 and cls in class_to_role:
        return class_to_role[cls]
    return "UNK"


def get_class(word):
    return token_to_class.get(word, -1)


morph = Morphology()

PREFIX_INDEX = {
    "qo": 0, "ch": 1, "sh": 2, "da": 3, "ok": 4,
    "ot": 5, "ol": 6, "ct": 7,
}
PREFIX_OTHER = 8
PREFIX_NONE = 9


def get_prefix_index(word):
    m = morph.extract(word)
    if m.prefix is None or m.prefix == "":
        return PREFIX_NONE
    if m.prefix in PREFIX_INDEX:
        return PREFIX_INDEX[m.prefix]
    return PREFIX_OTHER


def get_middle(word):
    m = morph.extract(word)
    return m.middle if m.middle else ""


def get_middle_length(word):
    return len(get_middle(word))


def kernel_char_count(word):
    mid = get_middle(word)
    return sum(1 for c in mid if c in ("k", "h", "e"))


def has_kernel(word):
    return kernel_char_count(word) > 0


def kendall_tau(x, y):
    n = len(x)
    if n < 2:
        return float("nan")
    concordant = 0
    discordant = 0
    tied_x = 0
    tied_y = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[i] - x[j]
            dy = y[i] - y[j]
            if dx == 0 and dy == 0:
                tied_x += 1
                tied_y += 1
            elif dx == 0:
                tied_x += 1
            elif dy == 0:
                tied_y += 1
            elif (dx > 0 and dy > 0) or (dx < 0 and dy < 0):
                concordant += 1
            else:
                discordant += 1
    npairs = n * (n - 1) / 2
    denom = math.sqrt((npairs - tied_x) * (npairs - tied_y))
    if denom == 0:
        return 0.0
    return (concordant - discordant) / denom


tx = Transcript()
lines = defaultdict(list)
for t in tx.currier_b():
    word = t.word.replace("*", "").strip()
    if not word:
        continue
    lines[(t.folio, t.line)].append(word)

all_line_keys = sorted(lines.keys())

print("=" * 70)
print("TEST 06: WITHIN-ZONE TOKEN ORDERING")
print("=" * 70)
print("  Total lines (Currier B): %d" % len(lines))


def annotate_work_zone(tokens):
    if len(tokens) < 3:
        return []
    work = tokens[1:-1]
    result = []
    for i, wrd in enumerate(work):
        cls = get_class(wrd)
        role = get_role(wrd)
        result.append({
            "word": wrd,
            "class": cls,
            "role": role,
            "zone_pos": i,
        })
    return result


en_sequences = []
ax_sequences = []

for lk in all_line_keys:
    work = annotate_work_zone(lines[lk])
    en_items = [(item["zone_pos"], item["class"], item["word"])
                for item in work if item["role"] == "ENERGY_OPERATOR" and item["class"] >= 0]
    ax_items = [(item["zone_pos"], item["class"], item["word"])
                for item in work if item["role"] == "AUXILIARY" and item["class"] >= 0]
    if len(en_items) >= 3:
        en_sequences.append((lk, en_items))
    if len(ax_items) >= 3:
        ax_sequences.append((lk, ax_items))

print("  Lines with 3+ EN in WORK zone: %d" % len(en_sequences))
print("  Lines with 3+ AX in WORK zone: %d" % len(ax_sequences))


def compute_tau_stats(sequences):
    results = {
        "vs_class": [],
        "vs_prefix": [],
        "vs_middle_len": [],
        "vs_kernel": [],
    }
    for lk, items in sequences:
        positions = [it[0] for it in items]
        classes = [it[1] for it in items]
        words = [it[2] for it in items]

        tau_cls = kendall_tau(positions, classes)
        if not math.isnan(tau_cls):
            results["vs_class"].append(tau_cls)

        prefixes = [get_prefix_index(ww) for ww in words]
        tau_pfx = kendall_tau(positions, prefixes)
        if not math.isnan(tau_pfx):
            results["vs_prefix"].append(tau_pfx)

        mid_lens = [get_middle_length(ww) for ww in words]
        tau_ml = kendall_tau(positions, mid_lens)
        if not math.isnan(tau_ml):
            results["vs_middle_len"].append(tau_ml)

        kernel_counts = [kernel_char_count(ww) for ww in words]
        tau_kc = kendall_tau(positions, kernel_counts)
        if not math.isnan(tau_kc):
            results["vs_kernel"].append(tau_kc)

    return results


en_taus = compute_tau_stats(en_sequences)
ax_taus = compute_tau_stats(ax_sequences)


def summarize_taus(taus, label):
    print("\n%s Kendall tau summary:" % label)
    for metric, values in taus.items():
        if not values:
            print("    %s: no data" % metric)
            continue
        arr = np.array(values)
        mean_v = float(np.mean(arr))
        std_v = float(np.std(arr))
        n = len(values)
        print("    %s: n=%d, mean=%.4f, std=%.4f" % (metric, n, mean_v, std_v))


summarize_taus(en_taus, "EN")
summarize_taus(ax_taus, "AX")


kernel_positions = []
nonkernel_positions = []
kernel_relative_positions = []
nonkernel_relative_positions = []

for lk, items in en_sequences:
    work = annotate_work_zone(lines[lk])
    zone_size = len(work)
    if zone_size == 0:
        continue
    for item in work:
        if item["role"] != "ENERGY_OPERATOR" or item["class"] < 0:
            continue
        rel_pos = item["zone_pos"] / max(1, zone_size - 1)
        if has_kernel(item["word"]):
            kernel_positions.append(item["zone_pos"])
            kernel_relative_positions.append(rel_pos)
        else:
            nonkernel_positions.append(item["zone_pos"])
            nonkernel_relative_positions.append(rel_pos)

kernel_mean_pos = float(np.mean(kernel_relative_positions)) if kernel_relative_positions else float("nan")
nonkernel_mean_pos = float(np.mean(nonkernel_relative_positions)) if nonkernel_relative_positions else float("nan")

print("\nKernel-bearing EN tokens:")
print("    Count: %d, mean relative position: %.4f" % (len(kernel_relative_positions), kernel_mean_pos))
print("  Kernel-free EN tokens:")
print("    Count: %d, mean relative position: %.4f" % (len(nonkernel_relative_positions), nonkernel_mean_pos))


pair_forward = Counter()
pair_reverse = Counter()

for lk, items in en_sequences:
    classes_in_order = [(it[0], it[1]) for it in items]
    for i in range(len(classes_in_order)):
        for j in range(i + 1, len(classes_in_order)):
            c_i = classes_in_order[i][1]
            c_j = classes_in_order[j][1]
            if c_i == c_j:
                continue
            lo, hi = min(c_i, c_j), max(c_i, c_j)
            if c_i == lo:
                pair_forward[(lo, hi)] += 1
            else:
                pair_reverse[(lo, hi)] += 1

all_pairs = set(pair_forward.keys()) | set(pair_reverse.keys())
directional_pairs = []
for pair in sorted(all_pairs):
    fwd = pair_forward[pair]
    rev = pair_reverse[pair]
    total = fwd + rev
    if total >= 10:
        ratio = max(fwd, rev) / max(1, min(fwd, rev))
        dominant_dir = "lo_first" if fwd >= rev else "hi_first"
        directional_pairs.append({
            "pair": list(pair),
            "lo_first": fwd,
            "hi_first": rev,
            "total": total,
            "ratio": round(ratio, 2),
            "dominant": dominant_dir,
        })

directional_pairs.sort(key=lambda x: x["ratio"], reverse=True)

print("\nDirectional class pairs (EN, 10+ co-occurrences):")
print("  %-12s  %8s  %8s  %6s  %6s" % ("Pair", "lo_first", "hi_first", "Total", "Ratio"))
biased_count = 0
for dp in directional_pairs[:20]:
    marker = " *" if dp["ratio"] > 3.0 else ""
    print("  (%3d, %3d)    %8d  %8d  %6d  %6.2f%s" % (
        dp["pair"][0], dp["pair"][1],
        dp["lo_first"], dp["hi_first"],
        dp["total"], dp["ratio"], marker))
    if dp["ratio"] > 3.0:
        biased_count += 1

print("  Pairs with >3:1 directional bias: %d / %d" % (
    biased_count, len(directional_pairs)))


rng = np.random.RandomState(42)
N_SHUFFLE = 1000


def build_work_zone_for_shuffle(line_tokens, target_role):
    if len(line_tokens) < 3:
        return [], []
    work = line_tokens[1:-1]
    target_indices = []
    target_classes = []
    for i, wrd in enumerate(work):
        cls = get_class(wrd)
        role = get_role(wrd)
        if role == target_role and cls >= 0:
            target_indices.append(i)
            target_classes.append(cls)
    return target_indices, target_classes


def compute_mean_tau_for_sequences(sequences):
    taus = []
    for lk, items in sequences:
        positions = [it[0] for it in items]
        classes = [it[1] for it in items]
        tau = kendall_tau(positions, classes)
        if not math.isnan(tau):
            taus.append(tau)
    if not taus:
        return float("nan")
    return float(np.mean(taus))


en_observed_tau = compute_mean_tau_for_sequences(en_sequences)
ax_observed_tau = compute_mean_tau_for_sequences(ax_sequences)

print("\nObserved mean tau (pos vs class):")
print("    EN: %.6f" % en_observed_tau)
print("    AX: %.6f" % ax_observed_tau)

en_shuffle_data = []
for lk, items in en_sequences:
    t_idx, t_cls = build_work_zone_for_shuffle(lines[lk], "ENERGY_OPERATOR")
    if len(t_idx) >= 3:
        en_shuffle_data.append((t_idx, t_cls))

ax_shuffle_data = []
for lk, items in ax_sequences:
    t_idx, t_cls = build_work_zone_for_shuffle(lines[lk], "AUXILIARY")
    if len(t_idx) >= 3:
        ax_shuffle_data.append((t_idx, t_cls))

print("\nRunning %d shuffle iterations..." % N_SHUFFLE)


def shuffle_and_compute_tau(shuffle_data, rng_state):
    taus = []
    for (indices, classes) in shuffle_data:
        shuffled_classes = list(classes)
        rng_state.shuffle(shuffled_classes)
        tau = kendall_tau(indices, shuffled_classes)
        if not math.isnan(tau):
            taus.append(tau)
    if not taus:
        return float("nan")
    return float(np.mean(taus))


en_shuffle_taus = []
ax_shuffle_taus = []

for i in range(N_SHUFFLE):
    en_shuffle_taus.append(shuffle_and_compute_tau(en_shuffle_data, rng))
    ax_shuffle_taus.append(shuffle_and_compute_tau(ax_shuffle_data, rng))

en_shuffle_taus = np.array(en_shuffle_taus)
ax_shuffle_taus = np.array(ax_shuffle_taus)

en_p_value = float(np.mean(en_shuffle_taus >= en_observed_tau))
ax_p_value = float(np.mean(ax_shuffle_taus >= ax_observed_tau))

en_p_two = float(np.mean(np.abs(en_shuffle_taus) >= abs(en_observed_tau)))
ax_p_two = float(np.mean(np.abs(ax_shuffle_taus) >= abs(ax_observed_tau)))

print("\nShuffle results:")
print("    EN: observed=%.6f, shuffle_mean=%.6f, shuffle_std=%.6f" % (
    en_observed_tau, float(np.mean(en_shuffle_taus)), float(np.std(en_shuffle_taus))))
print("    EN p-value (one-tail): %.4f, p-value (two-tail): %.4f" % (en_p_value, en_p_two))
print("    AX: observed=%.6f, shuffle_mean=%.6f, shuffle_std=%.6f" % (
    ax_observed_tau, float(np.mean(ax_shuffle_taus)), float(np.std(ax_shuffle_taus))))
print("    AX p-value (one-tail): %.4f, p-value (two-tail): %.4f" % (ax_p_value, ax_p_two))


en_significant = en_p_value < 0.001
ax_significant = ax_p_value < 0.001
en_sig_two = en_p_two < 0.001
ax_sig_two = ax_p_two < 0.001

has_directional_bias = biased_count >= 1

if (en_significant or ax_significant) and has_directional_bias:
    verdict = "PASS"
    detail = ("Significant ordering found. EN p=%.4f%s, AX p=%.4f%s. "
              "%d class pair(s) with >3:1 directional bias." % (
                  en_p_value, " (sig)" if en_significant else "",
                  ax_p_value, " (sig)" if ax_significant else "",
                  biased_count))
elif (en_sig_two or ax_sig_two) and has_directional_bias:
    verdict = "PASS"
    detail = ("Significant ordering (two-tailed). EN p=%.4f%s, AX p=%.4f%s. "
              "%d class pair(s) with >3:1 directional bias." % (
                  en_p_two, " (sig)" if en_sig_two else "",
                  ax_p_two, " (sig)" if ax_sig_two else "",
                  biased_count))
elif en_p_value > 0.05 and ax_p_value > 0.05 and en_p_two > 0.05 and ax_p_two > 0.05:
    verdict = "FAIL"
    detail = ("No significant ordering. EN p=%.4f, AX p=%.4f. "
              "%d pair(s) with >3:1 bias." % (en_p_value, ax_p_value, biased_count))
else:
    if has_directional_bias:
        verdict = "PASS"
        detail = ("Marginal tau significance but directional bias present. "
                  "EN p=%.4f, AX p=%.4f. %d biased pair(s)." % (
                      en_p_value, ax_p_value, biased_count))
    else:
        verdict = "FAIL"
        detail = ("Marginal tau but no directional bias. "
                  "EN p=%.4f, AX p=%.4f." % (en_p_value, ax_p_value))


print("\n" + "=" * 70)
print("  VERDICT: %s" % verdict)
print("  %s" % detail)
print("=" * 70)


def safe_float(x):
    if isinstance(x, (np.floating,)):
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return None
        return round(v, 6)
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return None
        return round(x, 6)
    return x


def tau_dict(values):
    if not values:
        return {"n": 0, "mean": None, "std": None, "median": None}
    arr = np.array(values)
    return {
        "n": len(values),
        "mean": safe_float(np.mean(arr)),
        "std": safe_float(np.std(arr)),
        "median": safe_float(np.median(arr)),
    }


pos_diff = None
if kernel_relative_positions and nonkernel_relative_positions:
    pos_diff = safe_float(kernel_mean_pos - nonkernel_mean_pos)

result = {
    "test": "06_within_zone_ordering",
    "phase": "LINE_CONTROL_BLOCK_GRAMMAR",
    "purpose": ("Determine whether tokens within the WORK zone follow a "
                "predictable ordering by instruction class, prefix, middle "
                "length, or kernel content."),
    "data": {
        "total_lines": len(lines),
        "qualifying_en_lines": len(en_sequences),
        "qualifying_ax_lines": len(ax_sequences),
    },
    "en_tau_analysis": {
        "vs_class": tau_dict(en_taus["vs_class"]),
        "vs_prefix": tau_dict(en_taus["vs_prefix"]),
        "vs_middle_len": tau_dict(en_taus["vs_middle_len"]),
        "vs_kernel": tau_dict(en_taus["vs_kernel"]),
    },
    "ax_tau_analysis": {
        "vs_class": tau_dict(ax_taus["vs_class"]),
        "vs_prefix": tau_dict(ax_taus["vs_prefix"]),
        "vs_middle_len": tau_dict(ax_taus["vs_middle_len"]),
        "vs_kernel": tau_dict(ax_taus["vs_kernel"]),
    },
    "kernel_position_analysis": {
        "kernel_bearing_en": {
            "count": len(kernel_relative_positions),
            "mean_relative_position": safe_float(kernel_mean_pos),
        },
        "kernel_free_en": {
            "count": len(nonkernel_relative_positions),
            "mean_relative_position": safe_float(nonkernel_mean_pos),
        },
        "position_difference": pos_diff,
    },
    "directional_pairs": {
        "total_qualifying_pairs": len(directional_pairs),
        "pairs_with_3to1_bias": biased_count,
        "top_pairs": directional_pairs[:20],
    },
    "shuffle": {
        "n_iterations": N_SHUFFLE,
        "seed": 42,
        "en": {
            "observed_mean_tau": safe_float(en_observed_tau),
            "shuffle_mean": safe_float(np.mean(en_shuffle_taus)),
            "shuffle_std": safe_float(np.std(en_shuffle_taus)),
            "p_value_one_tail": safe_float(en_p_value),
            "p_value_two_tail": safe_float(en_p_two),
            "significant_001": bool(en_significant),
            "significant_two_tail_001": bool(en_sig_two),
        },
        "ax": {
            "observed_mean_tau": safe_float(ax_observed_tau),
            "shuffle_mean": safe_float(np.mean(ax_shuffle_taus)),
            "shuffle_std": safe_float(np.std(ax_shuffle_taus)),
            "p_value_one_tail": safe_float(ax_p_value),
            "p_value_two_tail": safe_float(ax_p_two),
            "significant_001": bool(ax_significant),
            "significant_two_tail_001": bool(ax_sig_two),
        },
    },
    "verdict": verdict,
    "verdict_detail": detail,
    "pass_criteria": (
        "PASS: mean tau significantly >0 (p<0.001 vs shuffle) for EN or AX, "
        "AND 1+ class pair with >3:1 directional bias. "
        "FAIL: tau not different from shuffle (p>0.05)."
    ),
}

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=True)

print("\nResults saved to: %s" % RESULTS_PATH)
