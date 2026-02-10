"""
Test 01: Positional Token Exclusivity Census
Phase: LINE_CONTROL_BLOCK_GRAMMAR
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import fisher_exact

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path("C:/git/voynich").resolve()
OUTPUT_PATH = PROJECT_ROOT / "phases/LINE_CONTROL_BLOCK_GRAMMAR/results/01_positional_token_exclusivity.json"

class_map_path = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path, "r", encoding="utf-8") as f:
    class_map = json.load(f)
token_to_class = class_map.get("token_to_class", {})
class_to_role = class_map.get("class_to_role", {})

tx = Transcript()
morph = Morphology()

lines = defaultdict(list)
for t in tx.currier_b():
    word = t.word.replace("*", "").strip()
    if not word:
        continue
    lines[(t.folio, t.line)].append(word)

n_lines = len(lines)
n_tokens = sum(len(v) for v in lines.values())
print("Loaded %d lines, %d tokens" % (n_lines, n_tokens))


def assign_zones(line_tokens):
    n = len(line_tokens)
    if n == 0:
        return []
    if n == 1:
        return [(line_tokens[0], "INITIAL")]
    if n == 2:
        return [(line_tokens[0], "INITIAL"), (line_tokens[1], "FINAL")]
    result = [(line_tokens[0], "INITIAL")]
    for tok in line_tokens[1:-1]:
        result.append((tok, "MEDIAL"))
    result.append((line_tokens[-1], "FINAL"))
    return result


def suffix_strip(word):
    m = morph.extract(word)
    parts = []
    if m.prefix:
        parts.append(m.prefix)
    if m.middle:
        parts.append(m.middle)
    result = "".join(parts)
    return result if result else word


all_observations = []
for key, tokens in lines.items():
    for tok, zone in assign_zones(tokens):
        all_observations.append((tok, zone, key[0], key))


def compute_exclusivity(observations, min_count=10, label="raw"):
    token_total = Counter()
    zone_counts = defaultdict(lambda: {"INITIAL": 0, "MEDIAL": 0, "FINAL": 0})

    for tok, zone, _, _ in observations:
        token_total[tok] += 1
        zone_counts[tok][zone] += 1

    qualified = {tok: cnt for tok, cnt in token_total.items() if cnt >= min_count}
    n_qual = len(qualified)
    print("\n[%s] Qualified tokens (>=%d occurrences): %d" % (label, min_count, n_qual))

    exclusive_tokens = {}
    for tok in qualified:
        zc = zone_counts[tok]
        zero_zones = [z for z in ["INITIAL", "MEDIAL", "FINAL"] if zc[z] == 0]
        if zero_zones:
            cls_id = token_to_class.get(tok, None)
            cls_str = str(cls_id) if cls_id is not None else ""
            exclusive_tokens[tok] = {
                "total": qualified[tok],
                "INITIAL": zc["INITIAL"],
                "MEDIAL": zc["MEDIAL"],
                "FINAL": zc["FINAL"],
                "zero_zones": zero_zones,
                "class": cls_id,
                "role": class_to_role.get(cls_str, None)
            }

    n_excl = len(exclusive_tokens)
    print("[%s] Exclusive tokens (zero in >=1 zone): %d" % (label, n_excl))

    total_per_zone = {"INITIAL": 0, "MEDIAL": 0, "FINAL": 0}
    for tok, zone, _, _ in observations:
        total_per_zone[zone] += 1

    fisher_results = {}
    for tok, info in exclusive_tokens.items():
        if info["total"] < 20:
            continue
        for zone in info["zero_zones"]:
            a = info[zone]
            b = info["total"] - a
            c = total_per_zone[zone] - a
            d = sum(total_per_zone[z] for z in total_per_zone if z != zone) - b
            table = np.array([[a, b], [c, d]])
            _, p_value = fisher_exact(table, alternative="two-sided")
            if tok not in fisher_results:
                fisher_results[tok] = {}
            fisher_results[tok][zone] = {
                "p_value": float(p_value),
                "table": [[int(a), int(b)], [int(c), int(d)]]
            }

    fisher_sig_count = sum(
        1 for tok, zones in fisher_results.items()
        if any(v["p_value"] < 0.01 for v in zones.values())
    )
    print("[%s] Fisher significant (p<0.01, >=20 occ): %d" % (label, fisher_sig_count))

    return {
        "qualified_count": len(qualified),
        "exclusive_tokens": exclusive_tokens,
        "exclusive_count": len(exclusive_tokens),
        "fisher_results": fisher_results,
        "fisher_sig_count": fisher_sig_count,
        "total_per_zone": total_per_zone,
        "zone_counts": {tok: dict(zone_counts[tok]) for tok in qualified}
    }


print("=" * 60)
print("PASS (a): RAW TOKEN IDENTITY")
print("=" * 60)
raw_result = compute_exclusivity(all_observations, min_count=10, label="raw")

print("\n" + "=" * 60)
print("PASS (b): SUFFIX-STRIPPED (PREFIX+MIDDLE)")
print("=" * 60)

stripped_observations = []
for tok, zone, folio, key in all_observations:
    stripped = suffix_strip(tok)
    stripped_observations.append((stripped, zone, folio, key))

stripped_result = compute_exclusivity(stripped_observations, min_count=10, label="stripped")

raw_exclusive_set = set(raw_result["exclusive_tokens"].keys())
survived_stripping = []
lost_by_stripping = []
strip_map = {}
for tok in raw_exclusive_set:
    stripped = suffix_strip(tok)
    strip_map[tok] = stripped
    if stripped in stripped_result["exclusive_tokens"]:
        survived_stripping.append(tok)
    else:
        lost_by_stripping.append(tok)

n_survived = len(survived_stripping)
n_lost = len(lost_by_stripping)
print("\nExclusivity survival after suffix-stripping:")
print("  Survived (true lexical positioning): %d" % n_survived)
print("  Lost (suffix-driven decoration):     %d" % n_lost)


print("\n" + "=" * 60)
print("SHUFFLE NULL MODEL (1000 permutations, seed=42)")
print("=" * 60)

rng = np.random.RandomState(42)
n_shuffles = 1000

line_keys_ordered = sorted(lines.keys())
line_token_lists = [lines[k][:] for k in line_keys_ordered]

token_total_raw = Counter()
for tok, zone, _, _ in all_observations:
    token_total_raw[tok] += 1
qualified_tokens = {tok for tok, cnt in token_total_raw.items() if cnt >= 10}

shuffle_exclusive_counts = []
for i in range(n_shuffles):
    if (i + 1) % 200 == 0:
        print("  Shuffle %d/%d..." % (i + 1, n_shuffles))

    shuf_zone_counts = defaultdict(lambda: {"INITIAL": 0, "MEDIAL": 0, "FINAL": 0})

    for tokens in line_token_lists:
        n = len(tokens)
        if n == 0:
            continue
        perm = rng.permutation(n)
        shuffled = [tokens[j] for j in perm]
        for tok, zone in assign_zones(shuffled):
            if tok in qualified_tokens:
                shuf_zone_counts[tok][zone] += 1

    excl_count = 0
    for tok in qualified_tokens:
        zc = shuf_zone_counts[tok]
        if zc["INITIAL"] == 0 or zc["MEDIAL"] == 0 or zc["FINAL"] == 0:
            excl_count += 1
    shuffle_exclusive_counts.append(excl_count)

shuffle_mean = float(np.mean(shuffle_exclusive_counts))
shuffle_std = float(np.std(shuffle_exclusive_counts))
observed_exclusive = raw_result["exclusive_count"]

p_value_shuffle = float(np.mean(np.array(shuffle_exclusive_counts) >= observed_exclusive))

ratio = observed_exclusive / shuffle_mean if shuffle_mean > 0 else float("inf")

shuf_max = max(shuffle_exclusive_counts)
shuf_min = min(shuffle_exclusive_counts)
print("\nObserved exclusive tokens: %d" % observed_exclusive)
print("Shuffle mean:             %.2f +/- %.2f" % (shuffle_mean, shuffle_std))
print("Ratio (observed/mean):    %.2fx" % ratio)
print("Shuffle p-value:          %.6f" % p_value_shuffle)
print("Shuffle max:              %d" % shuf_max)
print("Shuffle min:              %d" % shuf_min)


print("\n" + "=" * 60)
print("VERDICT")
print("=" * 60)

pass_criteria_1 = ratio > 2.0 and p_value_shuffle < 0.001
fisher_sig = raw_result["fisher_sig_count"]
pass_criteria_2 = fisher_sig >= 5
fail_criteria = ratio <= 1.5

if pass_criteria_1 and pass_criteria_2:
    verdict = "PASS"
    verdict_detail = (
        "Exclusive count %d is %.2fx shuffle mean "
        "(p=%.6f), %d Fisher-significant tokens"
    ) % (observed_exclusive, ratio, p_value_shuffle, fisher_sig)
elif fail_criteria:
    verdict = "FAIL"
    verdict_detail = (
        "Exclusive count %d is only %.2fx shuffle mean "
        "(within 1.5x threshold)"
    ) % (observed_exclusive, ratio)
else:
    verdict = "PARTIAL"
    detail_parts = []
    if not pass_criteria_1:
        detail_parts.append("ratio %.2fx or p=%.6f insufficient" % (ratio, p_value_shuffle))
    if not pass_criteria_2:
        detail_parts.append("only %d Fisher-sig tokens (need 5+)" % fisher_sig)
    verdict_detail = "; ".join(detail_parts)

print("Verdict: %s" % verdict)
print("Detail:  %s" % verdict_detail)


print("\n" + "=" * 60)
print("TOP EXCLUSIVE TOKENS (raw, sorted by total count)")
print("=" * 60)
sorted_exclusive = sorted(
    raw_result["exclusive_tokens"].items(),
    key=lambda x: x[1]["total"],
    reverse=True
)
hdr = "Token".ljust(20) + "Total".rjust(6) + "INIT".rjust(6) + "MED".rjust(6) + "FIN".rjust(6) + "  " + "Zero Zones".ljust(20) + "Role".ljust(20)
print(hdr)
print("-" * 90)
for tok, info in sorted_exclusive[:30]:
    zero_str = ",".join(info["zero_zones"])
    role_str = info["role"] or "?"
    row = tok.ljust(20) + str(info["total"]).rjust(6) + str(info["INITIAL"]).rjust(6) + str(info["MEDIAL"]).rjust(6) + str(info["FINAL"]).rjust(6) + "  " + zero_str.ljust(20) + role_str.ljust(20)
    print(row)

print("\n" + "=" * 60)
print("FISHER EXACT TEST RESULTS (>=20 occ, p<0.05)")
print("=" * 60)
fisher_entries = []
for tok, zones in raw_result["fisher_results"].items():
    for zone, data in zones.items():
        if data["p_value"] < 0.05:
            fisher_entries.append((tok, zone, data["p_value"]))

fisher_entries.sort(key=lambda x: x[2])
print("Token".ljust(20) + "Zone".ljust(10) + "p-value".rjust(12))
print("-" * 45)
for tok, zone, pv in fisher_entries[:25]:
    print(tok.ljust(20) + zone.ljust(10) + ("%.6e" % pv).rjust(12))


print("\n" + "=" * 60)
print("SUFFIX-STRIPPED PASS SUMMARY")
print("=" * 60)
strip_excl = stripped_result["exclusive_count"]
print("Raw exclusive tokens:      %d" % observed_exclusive)
print("Stripped exclusive tokens:  %d" % strip_excl)
print("Survived stripping:        %d" % n_survived)
print("Lost by stripping:         %d" % n_lost)

if survived_stripping:
    print("\nSurvived (true lexical positioning):")
    for tok in sorted(survived_stripping, key=lambda t: raw_result["exclusive_tokens"][t]["total"], reverse=True)[:15]:
        info = raw_result["exclusive_tokens"][tok]
        sm = strip_map[tok]
        tot = info["total"]
        zz = info["zero_zones"]
        print("  %-20s -> %-15s total=%d zones=%s" % (tok, sm, tot, zz))

if lost_by_stripping:
    print("\nLost (suffix-driven decoration):")
    for tok in sorted(lost_by_stripping, key=lambda t: raw_result["exclusive_tokens"][t]["total"], reverse=True)[:15]:
        info = raw_result["exclusive_tokens"][tok]
        sm = strip_map[tok]
        tot = info["total"]
        zz = info["zero_zones"]
        print("  %-20s -> %-15s total=%d zones=%s" % (tok, sm, tot, zz))


output = {
    "test": "01_positional_token_exclusivity",
    "phase": "LINE_CONTROL_BLOCK_GRAMMAR",
    "verdict": verdict,
    "verdict_detail": verdict_detail,
    "summary": {
        "total_lines": len(lines),
        "total_tokens": sum(len(v) for v in lines.values()),
        "total_per_zone": raw_result["total_per_zone"],
    },
    "raw_pass": {
        "qualified_tokens": raw_result["qualified_count"],
        "exclusive_count": raw_result["exclusive_count"],
        "fisher_sig_count": raw_result["fisher_sig_count"],
        "top_exclusive": [
            {
                "token": tok,
                "total": info["total"],
                "INITIAL": info["INITIAL"],
                "MEDIAL": info["MEDIAL"],
                "FINAL": info["FINAL"],
                "zero_zones": info["zero_zones"],
                "class": info["class"],
                "role": info["role"]
            }
            for tok, info in sorted_exclusive
        ],
        "fisher_results": {
            tok: {
                zone: {"p_value": data["p_value"], "table": data["table"]}
                for zone, data in zones.items()
            }
            for tok, zones in raw_result["fisher_results"].items()
        }
    },
    "stripped_pass": {
        "qualified_tokens": stripped_result["qualified_count"],
        "exclusive_count": stripped_result["exclusive_count"],
        "fisher_sig_count": stripped_result["fisher_sig_count"],
        "survived_stripping": len(survived_stripping),
        "lost_by_stripping": len(lost_by_stripping),
        "survived_tokens": survived_stripping,
        "lost_tokens": lost_by_stripping,
        "top_stripped_exclusive": [
            {
                "stem": tok,
                "total": info["total"],
                "INITIAL": info["INITIAL"],
                "MEDIAL": info["MEDIAL"],
                "FINAL": info["FINAL"],
                "zero_zones": info["zero_zones"]
            }
            for tok, info in sorted(
                stripped_result["exclusive_tokens"].items(),
                key=lambda x: x[1]["total"],
                reverse=True
            )[:30]
        ]
    },
    "shuffle_null": {
        "n_shuffles": n_shuffles,
        "seed": 42,
        "observed_exclusive": observed_exclusive,
        "shuffle_mean": shuffle_mean,
        "shuffle_std": shuffle_std,
        "ratio": ratio,
        "p_value": p_value_shuffle,
        "shuffle_min": int(min(shuffle_exclusive_counts)),
        "shuffle_max": int(max(shuffle_exclusive_counts)),
        "distribution_percentiles": {
            "5": float(np.percentile(shuffle_exclusive_counts, 5)),
            "25": float(np.percentile(shuffle_exclusive_counts, 25)),
            "50": float(np.percentile(shuffle_exclusive_counts, 50)),
            "75": float(np.percentile(shuffle_exclusive_counts, 75)),
            "95": float(np.percentile(shuffle_exclusive_counts, 95)),
        }
    },
    "pass_criteria": {
        "ratio_gt_2x": bool(ratio > 2.0),
        "shuffle_p_lt_0.001": bool(p_value_shuffle < 0.001),
        "fisher_sig_ge_5": bool(raw_result["fisher_sig_count"] >= 5),
        "ratio_le_1.5_fail": bool(ratio <= 1.5)
    }
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=True)

print("\nResults saved to: %s" % OUTPUT_PATH)
print("Done.")
