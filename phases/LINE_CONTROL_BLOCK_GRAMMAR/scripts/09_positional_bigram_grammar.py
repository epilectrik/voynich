"""
Test 09: Positional Bigram Grammar - Zone-Specific
Phase: LINE_CONTROL_BLOCK_GRAMMAR

Purpose: Determine whether CLASS-level bigram transition probabilities vary by
positional zone within Currier B lines.  Lines are divided into 4 simplified
zones (INITIAL_TRANSITION, EARLY_MEDIAL, CORE, LATE_TRANSITION) and zone-
specific bigram matrices are compared against the global (all within-line
bigrams) matrix using KL divergence.

Method:
  1. Build Currier B lines, annotate each token with its instruction class.
  2. Filter to lines with 8+ tokens.
  3. Divide each line into positional zones and collect zone-specific bigrams.
  4. Compute KL divergence of each zone matrix vs. global matrix.
  5. Identify zone-enriched (>3x) and zone-depleted (<0.33x) bigrams.
  6. Shuffle test (1000x, seed=42): permute non-boundary tokens, recompute
     zone-specific KL divergences.
  7. Verdict based on KL magnitudes and significance vs shuffle.
"""

import sys
import json
import math
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path("C:/git/voynich").resolve()
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
RESULTS_PATH = PROJECT_ROOT / "phases/LINE_CONTROL_BLOCK_GRAMMAR/results/09_positional_bigram_grammar.json"

with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
    class_data = json.load(f)

token_to_class = {k: int(v) for k, v in class_data["token_to_class"].items()}
class_to_role = {int(k): v for k, v in class_data["class_to_role"].items()}
VALID_CLASSES = sorted(class_to_role.keys())
N_CLASSES = max(VALID_CLASSES) + 1

tx = Transcript()
lines_raw = defaultdict(list)
for t in tx.currier_b():
    word = t.word.replace("*", "").strip()
    if not word:
        continue
    lines_raw[(t.folio, t.line)].append(word)

line_data = []
for (folio, line_id), words in sorted(lines_raw.items()):
    classes = [token_to_class.get(w, -1) for w in words]
    line_data.append((folio, line_id, classes))

qualified_lines = [(f, lid, cs) for f, lid, cs in line_data if len(cs) >= 8]

print("=" * 70)
print("  Test 09: Positional Bigram Grammar - Zone-Specific")
print("=" * 70)
print()
print("  Total Currier B lines: %d" % len(line_data))
print("  Lines with 8+ tokens:  %d" % len(qualified_lines))

ZONE_NAMES = ["INITIAL_TRANSITION", "EARLY_MEDIAL", "CORE", "LATE_TRANSITION"]


def get_zone_bigrams(cls_seq):
    """Return zone-labeled bigrams for a class sequence."""
    n = len(cls_seq)
    zones = {z: [] for z in ZONE_NAMES}
    for i in range(n - 1):
        a, b = cls_seq[i], cls_seq[i + 1]
        if a < 0 or b < 0:
            continue
        if i == 0:
            zone = "INITIAL_TRANSITION"
        elif i in (1, 2):
            zone = "EARLY_MEDIAL"
        elif i >= n - 3:
            zone = "LATE_TRANSITION"
        else:
            zone = "CORE"
        zones[zone].append((a, b))
    return zones


def get_all_bigrams(cls_seq):
    """Return all within-line bigrams for valid classes."""
    bigrams = []
    for i in range(len(cls_seq) - 1):
        a, b = cls_seq[i], cls_seq[i + 1]
        if a >= 0 and b >= 0:
            bigrams.append((a, b))
    return bigrams


zone_bigrams = {z: [] for z in ZONE_NAMES}
global_bigrams = []

for folio, lid, cls_seq in qualified_lines:
    zb = get_zone_bigrams(cls_seq)
    for z in ZONE_NAMES:
        zone_bigrams[z].extend(zb[z])
    global_bigrams.extend(get_all_bigrams(cls_seq))

print()
print("  Bigram counts by zone:")
for z in ZONE_NAMES:
    print("    %-25s %6d" % (z, len(zone_bigrams[z])))
print("    %-25s %6d" % ("GLOBAL", len(global_bigrams)))

EPSILON = 1e-10


def bigrams_to_prob_matrix(bigram_list):
    """Convert list of (a, b) pairs to a probability matrix."""
    counts = Counter(bigram_list)
    total = sum(counts.values())
    if total == 0:
        return None, counts, total
    matrix = np.full((N_CLASSES, N_CLASSES), EPSILON)
    for (a, b), c in counts.items():
        matrix[a, b] = c / total
    matrix /= matrix.sum()
    return matrix, counts, total


def kl_divergence(p, q):
    """Compute KL(P || Q) = sum(P * log(P/Q))."""
    mask = p > EPSILON
    return float(np.sum(p[mask] * np.log(p[mask] / q[mask])))


global_matrix, global_counts, global_total = bigrams_to_prob_matrix(global_bigrams)
zone_matrices = {}
zone_kl = {}
zone_counts = {}
zone_totals = {}

for z in ZONE_NAMES:
    mat, cnt, tot = bigrams_to_prob_matrix(zone_bigrams[z])
    zone_matrices[z] = mat
    zone_counts[z] = cnt
    zone_totals[z] = tot
    if mat is not None and global_matrix is not None:
        zone_kl[z] = kl_divergence(mat, global_matrix)
    else:
        zone_kl[z] = 0.0

print()
print("  KL divergence (zone || global):")
for z in ZONE_NAMES:
    print("    %-25s %.6f bits" % (z, zone_kl[z]))


def find_enriched_depleted(zone_cnt, zone_total, gcnt, gtotal,
                           enrich_thresh=3.0, deplete_thresh=0.33, min_count=3):
    """Find enriched and depleted bigrams in a zone vs global."""
    enriched = []
    depleted = []
    if zone_total == 0 or gtotal == 0:
        return enriched, depleted
    all_pairs = set(zone_cnt.keys()) | set(gcnt.keys())
    for pair in all_pairs:
        zc = zone_cnt.get(pair, 0)
        gc = gcnt.get(pair, 0)
        zf = zc / zone_total if zone_total > 0 else 0
        gf = gc / gtotal if gtotal > 0 else 0
        if gf > 0 and zc >= min_count:
            ratio = zf / gf
            cls_a, cls_b = pair
            role_a = class_to_role.get(cls_a, "UNK")
            role_b = class_to_role.get(cls_b, "UNK")
            if ratio >= enrich_thresh:
                enriched.append({
                    "class_pair": [int(cls_a), int(cls_b)],
                    "role_pair": [role_a, role_b],
                    "zone_freq": round(zf, 6),
                    "global_freq": round(gf, 6),
                    "ratio": round(ratio, 3),
                    "zone_count": int(zc),
                })
            elif ratio <= deplete_thresh and gc >= min_count:
                depleted.append({
                    "class_pair": [int(cls_a), int(cls_b)],
                    "role_pair": [role_a, role_b],
                    "zone_freq": round(zf, 6),
                    "global_freq": round(gf, 6),
                    "ratio": round(ratio, 3),
                    "zone_count": int(zc),
                    "global_count": int(gc),
                })
    enriched.sort(key=lambda x: -x["ratio"])
    depleted.sort(key=lambda x: x["ratio"])
    return enriched, depleted


zone_enriched = {}
zone_depleted = {}

print()
print("  Zone-specific enriched/depleted bigrams (>3x / <0.33x):")
for z in ZONE_NAMES:
    enriched, depleted = find_enriched_depleted(
        zone_counts[z], zone_totals[z], global_counts, global_total
    )
    zone_enriched[z] = enriched
    zone_depleted[z] = depleted
    print("    %-25s enriched=%d  depleted=%d" % (z, len(enriched), len(depleted)))

print()
print("  Top enriched bigrams per zone (top 3):")
for z in ZONE_NAMES:
    top = zone_enriched[z][:3]
    if top:
        print("    %s:" % z)
        for item in top:
            print("      class %d->%d (%s->%s): %.3fx  (n=%d)" % (
                item["class_pair"][0], item["class_pair"][1],
                item["role_pair"][0], item["role_pair"][1],
                item["ratio"], item["zone_count"]))
    else:
        print("    %s: (none)" % z)

# ---------------------------------------------------------------------------
# SHUFFLE TEST (1000x, seed=42)
# ---------------------------------------------------------------------------
N_SHUFFLES = 1000
rng = np.random.RandomState(42)

print()
print("  Running shuffle test (%d iterations)..." % N_SHUFFLES)

qual_seqs = [cls_seq for _, _, cls_seq in qualified_lines]
shuffle_kl = {z: [] for z in ZONE_NAMES}

for si in range(N_SHUFFLES):
    shuf_zone_bigrams = {z: [] for z in ZONE_NAMES}
    shuf_global_bigrams = []
    for cls_seq in qual_seqs:
        n = len(cls_seq)
        shuffled = list(cls_seq)
        if n > 2:
            inner = list(cls_seq[1:n-1])
            rng.shuffle(inner)
            shuffled[1:n-1] = inner
        zb = get_zone_bigrams(shuffled)
        for z in ZONE_NAMES:
            shuf_zone_bigrams[z].extend(zb[z])
        shuf_global_bigrams.extend(get_all_bigrams(shuffled))
    shuf_global_mat, _, _ = bigrams_to_prob_matrix(shuf_global_bigrams)
    for z in ZONE_NAMES:
        shuf_mat, _, _ = bigrams_to_prob_matrix(shuf_zone_bigrams[z])
        if shuf_mat is not None and shuf_global_mat is not None:
            shuffle_kl[z].append(kl_divergence(shuf_mat, shuf_global_mat))
        else:
            shuffle_kl[z].append(0.0)

shuffle_stats = {}
for z in ZONE_NAMES:
    shuf_arr = np.array(shuffle_kl[z])
    shuf_mean = float(np.mean(shuf_arr))
    shuf_std = float(np.std(shuf_arr))
    real_kl = zone_kl[z]
    if shuf_std > 0:
        z_score = (real_kl - shuf_mean) / shuf_std
    else:
        z_score = 0.0
    p_value = float(np.mean(shuf_arr >= real_kl))
    shuffle_stats[z] = {
        "real_kl": round(real_kl, 6),
        "shuffle_mean": round(shuf_mean, 6),
        "shuffle_std": round(shuf_std, 6),
        "z_score": round(z_score, 3),
        "p_value": float(p_value),
        "n_shuffles_exceeding": int(np.sum(shuf_arr >= real_kl)),
    }

print()
print("  Shuffle comparison (real KL vs shuffle distribution):")
print("    %-25s %10s %10s %10s %8s %8s" % ("Zone", "Real KL", "Shuf Mean", "Shuf Std", "Z-score", "p-value"))
for z in ZONE_NAMES:
    s = shuffle_stats[z]
    print("    %-25s %10.6f %10.6f %10.6f %8.3f %8.4f" % (
        z, s["real_kl"], s["shuffle_mean"], s["shuffle_std"],
        s["z_score"], s["p_value"]))

# ---------------------------------------------------------------------------
# VERDICT
# ---------------------------------------------------------------------------
zones_above_005 = [z for z in ZONE_NAMES if zone_kl[z] > 0.05]
zones_significant = [z for z in ZONE_NAMES if shuffle_stats[z]["p_value"] < 0.001]
zones_pass = [z for z in ZONE_NAMES if z in zones_above_005 and z in zones_significant]
all_below_002 = all(zone_kl[z] < 0.02 for z in ZONE_NAMES)

if len(zones_pass) >= 2:
    verdict = "PASS"
    detail = ("KL > 0.05 bits AND p < 0.001 for %d zones: %s. "
              "Zone-specific bigram grammar is strongly differentiated from "
              "global baseline." % (len(zones_pass), ", ".join(zones_pass)))
elif all_below_002:
    verdict = "FAIL"
    detail = ("KL < 0.02 for all zone transitions. No zone-specific bigram "
              "grammar detected.")
else:
    n_above = len(zones_above_005)
    n_sig = len(zones_significant)
    verdict = "WEAK"
    detail = ("KL > 0.05 for %d zones, p < 0.001 for %d zones, but fewer "
              "than 2 zones pass both thresholds. Partial zone-specificity "
              "detected." % (n_above, n_sig))

print()
print("  Zones with KL > 0.05:   %d  %s" % (len(zones_above_005), zones_above_005))
print("  Zones with p < 0.001:   %d  %s" % (len(zones_significant), zones_significant))
print("  Zones passing both:     %d  %s" % (len(zones_pass), zones_pass))
print()
print("  VERDICT: %s" % verdict)
print("  %s" % detail)

# ---------------------------------------------------------------------------
# DETAILED 7-ZONE ANALYSIS (for JSON output)
# ---------------------------------------------------------------------------
ZONE_7_NAMES = [
    "INITIAL_TO_EARLY",
    "WITHIN_EARLY_MED",
    "EARLY_TO_CORE",
    "WITHIN_CORE",
    "CORE_TO_LATE",
    "WITHIN_LATE",
    "LATE_TO_FINAL",
]


def get_7zone_bigrams(cls_seq):
    """Assign bigrams to the detailed 7-zone scheme."""
    n = len(cls_seq)
    zones = {z: [] for z in ZONE_7_NAMES}
    for i in range(n - 1):
        a, b = cls_seq[i], cls_seq[i + 1]
        if a < 0 or b < 0:
            continue
        if i == 0:
            zone = "INITIAL_TO_EARLY"
        elif i == 1:
            zone = "WITHIN_EARLY_MED"
        elif i == 2:
            zone = "EARLY_TO_CORE"
        elif i == n - 2:
            zone = "LATE_TO_FINAL"
        elif i == n - 3:
            zone = "WITHIN_LATE"
        elif i == n - 4:
            zone = "CORE_TO_LATE"
        else:
            zone = "WITHIN_CORE"
        zones[zone].append((a, b))
    return zones


zone7_bigrams = {z: [] for z in ZONE_7_NAMES}
for folio, lid, cls_seq in qualified_lines:
    zb7 = get_7zone_bigrams(cls_seq)
    for z in ZONE_7_NAMES:
        zone7_bigrams[z].extend(zb7[z])

zone7_kl = {}
for z in ZONE_7_NAMES:
    mat7, _, _ = bigrams_to_prob_matrix(zone7_bigrams[z])
    if mat7 is not None and global_matrix is not None:
        zone7_kl[z] = round(kl_divergence(mat7, global_matrix), 6)
    else:
        zone7_kl[z] = 0.0

print()
print("  Detailed 7-zone KL divergences:")
for z in ZONE_7_NAMES:
    print("    %-25s %.6f bits  (n=%d)" % (z, zone7_kl[z], len(zone7_bigrams[z])))

# ---------------------------------------------------------------------------
# TOP GLOBAL BIGRAMS (for context)
# ---------------------------------------------------------------------------
top_global = global_counts.most_common(15)
top_global_info = []
for (a, b), cnt in top_global:
    top_global_info.append({
        "class_pair": [int(a), int(b)],
        "role_pair": [class_to_role.get(a, "UNK"), class_to_role.get(b, "UNK")],
        "count": int(cnt),
        "freq": round(cnt / global_total, 6),
    })

# ---------------------------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------------------------
output = {
    "test": "09_positional_bigram_grammar",
    "phase": "LINE_CONTROL_BLOCK_GRAMMAR",
    "purpose": "Determine whether CLASS-level bigram transition probabilities vary by positional zone within Currier B lines (8+ tokens)",
    "data": {
        "total_currier_b_lines": len(line_data),
        "qualifying_lines_8plus": len(qualified_lines),
        "total_global_bigrams": int(global_total),
        "n_instruction_classes": len(VALID_CLASSES),
        "line_length_stats": {
            "mean": round(float(np.mean([len(s) for _, _, s in qualified_lines])), 2),
            "median": round(float(np.median([len(s) for _, _, s in qualified_lines])), 2),
            "min": int(min(len(s) for _, _, s in qualified_lines)),
            "max": int(max(len(s) for _, _, s in qualified_lines)),
        },
    },
    "zone_definition": {
        "simplified_4_zones": {
            "INITIAL_TRANSITION": "Bigram from position 0 to 1",
            "EARLY_MEDIAL": "Bigrams at positions 1->2 and 2->3",
            "CORE": "All bigrams within positions 3 to N-4",
            "LATE_TRANSITION": "Bigrams from position N-3 to N-1",
        },
        "detailed_7_zones": {
            "INITIAL_TO_EARLY": "pos 0->1",
            "WITHIN_EARLY_MED": "pos 1->2",
            "EARLY_TO_CORE": "pos 2->3",
            "WITHIN_CORE": "all bigrams pos 3 to N-5",
            "CORE_TO_LATE": "pos N-4 -> N-3",
            "WITHIN_LATE": "pos N-3 -> N-2",
            "LATE_TO_FINAL": "pos N-2 -> N-1",
        },
    },
    "zone_bigram_counts_4zone": {z: len(zone_bigrams[z]) for z in ZONE_NAMES},
    "zone_bigram_counts_7zone": {z: len(zone7_bigrams[z]) for z in ZONE_7_NAMES},
    "kl_divergence_4zone": {z: round(zone_kl[z], 6) for z in ZONE_NAMES},
    "kl_divergence_7zone": zone7_kl,
    "enriched_bigrams": {z: zone_enriched[z][:10] for z in ZONE_NAMES},
    "depleted_bigrams": {z: zone_depleted[z][:10] for z in ZONE_NAMES},
    "enrichment_summary": {z: {"n_enriched_3x": len(zone_enriched[z]), "n_depleted_033x": len(zone_depleted[z])} for z in ZONE_NAMES},
    "top_global_bigrams": top_global_info,
    "shuffle_test": {
        "n_shuffles": N_SHUFFLES,
        "seed": 42,
        "method": "Permute non-boundary tokens (keep first and last fixed)",
        "zone_results": shuffle_stats,
    },
    "verdict": verdict,
    "verdict_detail": detail,
    "pass_criteria": {
        "PASS": "KL > 0.05 bits for at least 2 zones AND p < 0.001 vs shuffle",
        "FAIL": "KL < 0.02 for all zone transitions",
        "WEAK": "Some signal but fewer than 2 zones pass both thresholds",
    },
}

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print()
print("  Results saved to %s" % RESULTS_PATH)
