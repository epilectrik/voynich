"""
LINE_CONTROL_BLOCK_GRAMMAR - Test 05: Opening/Closing Constraint Set Identification

Purpose: Determine whether line-initial (OPENER) and line-final (CLOSER)
positions in Currier B are governed by constrained token sets.  If a small
number of tokens dominate boundary positions, this implies grammatical
constraints on what can open or close a control block.

Method:
  1. Build Currier B lines (2+ tokens).  Collect OPENER (first token) and
     CLOSER (last token) for each line.
  2. For each boundary position compute:
     a. Frequency-ranked token list
     b. Coverage curve (cumulative line-fraction vs. rank)
     c. Gini coefficient of the frequency distribution
  3. Identify mandatory set -- tokens with observed boundary frequency > 2x
     expected from corpus base-rate.
  4. For each mandatory token compute boundary commitment = fraction of its
     total occurrences at that boundary position.
  5. Report role composition (CC, EN, AX, FQ, FL) for opener and closer.
  6. Shuffle test (1000x, seed=42): permute tokens within each line,
     recompute Gini for initial/final positions.
  7. Pass:  Gini > 0.6 AND > 2x shuffle Gini; 3+ tokens commit > 0.40.
     Fail:  Gini < 0.3 or within 1.5x shuffle.
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript, Morphology

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path("C:/git/voynich").resolve()
CLASS_MAP_PATH = (
    PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
)
RESULTS_PATH = (
    PROJECT_ROOT
    / "phases/LINE_CONTROL_BLOCK_GRAMMAR/results/05_opener_closer_constraint_sets.json"
)

# ---------------------------------------------------------------------------
# LOAD CLASS MAP
# ---------------------------------------------------------------------------
with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
    class_data = json.load(f)

token_to_class = {k: int(v) for k, v in class_data["token_to_class"].items()}
token_to_role = class_data.get("token_to_role", {})
class_to_role = {int(k): v for k, v in class_data["class_to_role"].items()}

# Short role labels for display
ROLE_SHORT = {
    "CORE_CONTROL": "CC",
    "ENERGY_OPERATOR": "EN",
    "AUXILIARY": "AX",
    "FREQUENT_OPERATOR": "FQ",
    "FLOW_OPERATOR": "FL",
    "UNK": "UNK",
}


def get_role(word):
    """Get role for a word, checking token_to_role first, then class_to_role."""
    if word in token_to_role:
        return token_to_role[word]
    cls = token_to_class.get(word, -1)
    if cls >= 0 and cls in class_to_role:
        return class_to_role[cls]
    return "UNK"


def role_short(word):
    return ROLE_SHORT.get(get_role(word), "UNK")


# ---------------------------------------------------------------------------
# GINI COEFFICIENT
# ---------------------------------------------------------------------------
def compute_gini(values):
    arr = np.array(sorted(values), dtype=float)
    n = len(arr)
    if n == 0 or arr.sum() == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return float((2 * np.sum(index * arr) - (n + 1) * arr.sum()) / (n * arr.sum()))


# ---------------------------------------------------------------------------
# BUILD LINES
# ---------------------------------------------------------------------------
tx = Transcript()
lines_dict = defaultdict(list)
for t in tx.currier_b():
    word = t.word.replace("*", "").strip()
    if not word:
        continue
    lines_dict[(t.folio, t.line)].append(word)

# Filter to lines with 2+ tokens
line_keys = sorted(k for k, v in lines_dict.items() if len(v) >= 2)
n_lines = len(line_keys)

# Collect all tokens (for base rate computation)
all_words = []
for k in line_keys:
    all_words.extend(lines_dict[k])
total_token_count = len(all_words)
corpus_freq = Counter(all_words)

print("=" * 70)
print("TEST 05: OPENING/CLOSING CONSTRAINT SET IDENTIFICATION")
print("=" * 70)
print("  Total Currier B lines:     %d" % len(lines_dict))
print("  Lines with 2+ tokens:      %d" % n_lines)
print("  Total tokens in those:     %d" % total_token_count)
print("  Unique token types:        %d" % len(corpus_freq))

# ---------------------------------------------------------------------------
# EXTRACT OPENERS AND CLOSERS
# ---------------------------------------------------------------------------
openers = [lines_dict[k][0] for k in line_keys]
closers = [lines_dict[k][-1] for k in line_keys]

opener_freq = Counter(openers)
closer_freq = Counter(closers)

print("")
print("  Unique opener types:       %d" % len(opener_freq))
print("  Unique closer types:       %d" % len(closer_freq))


# ---------------------------------------------------------------------------
# COVERAGE CURVE + STATS
# ---------------------------------------------------------------------------
def coverage_analysis(freq_counter, n_total, label):
    """Compute coverage curve and key metrics for a boundary position."""
    ranked = freq_counter.most_common()
    cumulative = 0
    coverage_points = []
    tokens_80 = None
    tokens_95 = None

    for i, (tok, cnt) in enumerate(ranked, 1):
        cumulative += cnt
        frac = cumulative / n_total
        coverage_points.append({"rank": i, "token": tok, "count": cnt,
                                "cum_fraction": round(frac, 6)})
        if tokens_80 is None and frac >= 0.80:
            tokens_80 = i
        if tokens_95 is None and frac >= 0.95:
            tokens_95 = i

    gini = compute_gini(list(freq_counter.values()))

    return {
        "coverage_points": coverage_points,
        "tokens_for_80pct": tokens_80,
        "tokens_for_95pct": tokens_95,
        "gini": round(gini, 6),
        "n_unique": len(freq_counter),
        "n_total": n_total,
        "label": label,
    }


opener_stats = coverage_analysis(opener_freq, n_lines, "OPENER")
closer_stats = coverage_analysis(closer_freq, n_lines, "CLOSER")


# ---------------------------------------------------------------------------
# MANDATORY SET (frequency > 2x expected)
# ---------------------------------------------------------------------------
def find_mandatory_set(boundary_freq, corpus_freq_map, n_lines_total,
                       total_tokens, label):
    """Identify tokens whose boundary frequency exceeds 2x corpus base-rate
    expectation.  Also compute boundary commitment."""
    mandatory = []

    for tok, obs_count in boundary_freq.most_common():
        tok_total = corpus_freq_map.get(tok, 0)
        if tok_total == 0:
            continue
        expected = (tok_total / total_tokens) * n_lines_total
        if expected == 0:
            continue
        ratio = obs_count / expected
        commitment = obs_count / tok_total
        if ratio > 2.0:
            mandatory.append({
                "token": tok,
                "boundary_count": obs_count,
                "corpus_count": tok_total,
                "expected": round(expected, 2),
                "enrichment_ratio": round(ratio, 4),
                "boundary_commitment": round(commitment, 4),
                "role": get_role(tok),
                "role_short": role_short(tok),
            })

    # Sort by enrichment ratio descending
    mandatory.sort(key=lambda x: -x["enrichment_ratio"])
    return mandatory


opener_mandatory = find_mandatory_set(
    opener_freq, corpus_freq, n_lines, total_token_count, "OPENER"
)
closer_mandatory = find_mandatory_set(
    closer_freq, corpus_freq, n_lines, total_token_count, "CLOSER"
)

# Count tokens with commitment > 0.40
opener_high_commit = [m for m in opener_mandatory if m["boundary_commitment"] > 0.40]
closer_high_commit = [m for m in closer_mandatory if m["boundary_commitment"] > 0.40]


# ---------------------------------------------------------------------------
# ROLE COMPOSITION
# ---------------------------------------------------------------------------
def role_composition(freq_counter):
    """Fraction of boundary occurrences from each role."""
    role_counts = Counter()
    total = 0
    for tok, cnt in freq_counter.items():
        r = role_short(tok)
        role_counts[r] += cnt
        total += cnt
    result = {}
    for r in sorted(role_counts, key=lambda x: -role_counts[x]):
        result[r] = {
            "count": role_counts[r],
            "fraction": round(role_counts[r] / total, 4) if total > 0 else 0.0,
        }
    return result


opener_roles = role_composition(opener_freq)
closer_roles = role_composition(closer_freq)


# ---------------------------------------------------------------------------
# SHUFFLE TEST (1000x, seed=42)
# ---------------------------------------------------------------------------
print("")
print("  Running shuffle test (1000 permutations) ...")
rng = np.random.RandomState(42)
N_SHUFFLES = 1000

shuffle_opener_ginis = []
shuffle_closer_ginis = []

# Pre-build line arrays for fast shuffling
line_arrays = [list(lines_dict[k]) for k in line_keys]

for i in range(N_SHUFFLES):
    shuf_opener_freq = Counter()
    shuf_closer_freq = Counter()
    for arr in line_arrays:
        perm = rng.permutation(len(arr))
        shuf_opener_freq[arr[perm[0]]] += 1
        shuf_closer_freq[arr[perm[-1]]] += 1
    shuffle_opener_ginis.append(compute_gini(list(shuf_opener_freq.values())))
    shuffle_closer_ginis.append(compute_gini(list(shuf_closer_freq.values())))

mean_shuf_opener_gini = float(np.mean(shuffle_opener_ginis))
mean_shuf_closer_gini = float(np.mean(shuffle_closer_ginis))
std_shuf_opener_gini = float(np.std(shuffle_opener_ginis))
std_shuf_closer_gini = float(np.std(shuffle_closer_ginis))

opener_gini_ratio = (
    opener_stats["gini"] / mean_shuf_opener_gini
    if mean_shuf_opener_gini > 0 else float("inf")
)
closer_gini_ratio = (
    closer_stats["gini"] / mean_shuf_closer_gini
    if mean_shuf_closer_gini > 0 else float("inf")
)


# ---------------------------------------------------------------------------
# VERDICT
# ---------------------------------------------------------------------------
# Pass: Gini > 0.6 AND > 2x shuffle Gini; 3+ tokens with commitment > 0.40
# Fail: Gini < 0.3 or within 1.5x shuffle

opener_gini_pass = opener_stats["gini"] > 0.6 and opener_gini_ratio > 2.0
closer_gini_pass = closer_stats["gini"] > 0.6 and closer_gini_ratio > 2.0
opener_commit_pass = len(opener_high_commit) >= 3
closer_commit_pass = len(closer_high_commit) >= 3

opener_gini_fail = opener_stats["gini"] < 0.3 or opener_gini_ratio < 1.5
closer_gini_fail = closer_stats["gini"] < 0.3 or closer_gini_ratio < 1.5

# Overall: both positions must pass; if either fails -> FAIL
if (opener_gini_pass and opener_commit_pass and
        closer_gini_pass and closer_commit_pass):
    verdict = "PASS"
elif opener_gini_fail or closer_gini_fail:
    verdict = "FAIL"
else:
    verdict = "PARTIAL"

# ---------------------------------------------------------------------------
# PRINT RESULTS
# ---------------------------------------------------------------------------
print("")
print("-" * 70)
print("COVERAGE CURVES")
print("-" * 70)

for stats, label in [(opener_stats, "OPENER"), (closer_stats, "CLOSER")]:
    print("")
    print("  %s:" % label)
    print("    Unique types:         %d" % stats["n_unique"])
    print("    Gini coefficient:     %.4f" % stats["gini"])
    print("    Tokens for 80%% cov:   %s" % stats["tokens_for_80pct"])
    print("    Tokens for 95%% cov:   %s" % stats["tokens_for_95pct"])
    print("    Top 10 by frequency:")
    for pt in stats["coverage_points"][:10]:
        print("      %3d. %-16s  count=%4d  cum=%.3f  role=%s" % (
            pt["rank"], pt["token"], pt["count"], pt["cum_fraction"],
            role_short(pt["token"])))

print("")
print("-" * 70)
print("MANDATORY SETS (enrichment > 2x expected)")
print("-" * 70)

for mset, label in [(opener_mandatory, "OPENER"), (closer_mandatory, "CLOSER")]:
    print("")
    print("  %s mandatory tokens: %d" % (label, len(mset)))
    high = [m for m in mset if m["boundary_commitment"] > 0.40]
    print("  With commitment > 0.40:  %d" % len(high))
    print("    Top 15:")
    for m in mset[:15]:
        flag = " ***" if m["boundary_commitment"] > 0.40 else ""
        print("      %-16s  bnd=%4d  corpus=%5d  enrich=%.2f  commit=%.3f  %s%s" % (
            m["token"], m["boundary_count"], m["corpus_count"],
            m["enrichment_ratio"], m["boundary_commitment"],
            m["role_short"], flag))

print("")
print("-" * 70)
print("ROLE COMPOSITION")
print("-" * 70)

for rc, label in [(opener_roles, "OPENER"), (closer_roles, "CLOSER")]:
    print("")
    print("  %s:" % label)
    for role, info in rc.items():
        print("    %-4s  count=%5d  fraction=%.4f" % (
            role, info["count"], info["fraction"]))

print("")
print("-" * 70)
print("SHUFFLE TEST (1000 permutations)")
print("-" * 70)

print("")
print("  OPENER:")
print("    Real Gini:          %.4f" % opener_stats["gini"])
print("    Shuffle mean Gini:  %.4f +/- %.4f" % (
    mean_shuf_opener_gini, std_shuf_opener_gini))
print("    Ratio (real/shuf):  %.4f" % opener_gini_ratio)
print("    Gini > 0.6:         %s" % (opener_stats["gini"] > 0.6))
print("    Ratio > 2.0:        %s" % (opener_gini_ratio > 2.0))

print("")
print("  CLOSER:")
print("    Real Gini:          %.4f" % closer_stats["gini"])
print("    Shuffle mean Gini:  %.4f +/- %.4f" % (
    mean_shuf_closer_gini, std_shuf_closer_gini))
print("    Ratio (real/shuf):  %.4f" % closer_gini_ratio)
print("    Gini > 0.6:         %s" % (closer_stats["gini"] > 0.6))
print("    Ratio > 2.0:        %s" % (closer_gini_ratio > 2.0))

print("")
print("-" * 70)
print("VERDICT: %s" % verdict)
print("-" * 70)

detail_parts = []
if opener_gini_pass and opener_commit_pass:
    detail_parts.append(
        "OPENER: Gini=%.3f (%.1fx shuffle), %d tokens commit>0.40 -> PASS" % (
            opener_stats["gini"], opener_gini_ratio, len(opener_high_commit)))
elif opener_gini_fail:
    detail_parts.append(
        "OPENER: Gini=%.3f (%.1fx shuffle) -> FAIL" % (
            opener_stats["gini"], opener_gini_ratio))
else:
    detail_parts.append(
        "OPENER: Gini=%.3f (%.1fx shuffle), %d tokens commit>0.40 -> PARTIAL" % (
            opener_stats["gini"], opener_gini_ratio, len(opener_high_commit)))

if closer_gini_pass and closer_commit_pass:
    detail_parts.append(
        "CLOSER: Gini=%.3f (%.1fx shuffle), %d tokens commit>0.40 -> PASS" % (
            closer_stats["gini"], closer_gini_ratio, len(closer_high_commit)))
elif closer_gini_fail:
    detail_parts.append(
        "CLOSER: Gini=%.3f (%.1fx shuffle) -> FAIL" % (
            closer_stats["gini"], closer_gini_ratio))
else:
    detail_parts.append(
        "CLOSER: Gini=%.3f (%.1fx shuffle), %d tokens commit>0.40 -> PARTIAL" % (
            closer_stats["gini"], closer_gini_ratio, len(closer_high_commit)))

for p in detail_parts:
    print("  %s" % p)

# ---------------------------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------------------------
result = {
    "test": "05_opener_closer_constraint_sets",
    "phase": "LINE_CONTROL_BLOCK_GRAMMAR",
    "verdict": verdict,
    "summary": {
        "n_lines": n_lines,
        "total_tokens": total_token_count,
        "unique_tokens": len(corpus_freq),
    },
    "opener": {
        "n_unique": opener_stats["n_unique"],
        "gini": opener_stats["gini"],
        "tokens_for_80pct": opener_stats["tokens_for_80pct"],
        "tokens_for_95pct": opener_stats["tokens_for_95pct"],
        "gini_ratio_vs_shuffle": round(opener_gini_ratio, 4),
        "shuffle_gini_mean": round(mean_shuf_opener_gini, 6),
        "shuffle_gini_std": round(std_shuf_opener_gini, 6),
        "mandatory_count": len(opener_mandatory),
        "high_commitment_count": len(opener_high_commit),
        "gini_pass": opener_gini_pass,
        "commitment_pass": opener_commit_pass,
        "top_tokens": opener_stats["coverage_points"][:30],
        "mandatory_set": opener_mandatory[:30],
        "role_composition": opener_roles,
    },
    "closer": {
        "n_unique": closer_stats["n_unique"],
        "gini": closer_stats["gini"],
        "tokens_for_80pct": closer_stats["tokens_for_80pct"],
        "tokens_for_95pct": closer_stats["tokens_for_95pct"],
        "gini_ratio_vs_shuffle": round(closer_gini_ratio, 4),
        "shuffle_gini_mean": round(mean_shuf_closer_gini, 6),
        "shuffle_gini_std": round(std_shuf_closer_gini, 6),
        "mandatory_count": len(closer_mandatory),
        "high_commitment_count": len(closer_high_commit),
        "gini_pass": closer_gini_pass,
        "commitment_pass": closer_commit_pass,
        "top_tokens": closer_stats["coverage_points"][:30],
        "mandatory_set": closer_mandatory[:30],
        "role_composition": closer_roles,
    },
    "pass_criteria": {
        "gini_threshold": 0.6,
        "gini_ratio_threshold": 2.0,
        "commitment_threshold": 0.40,
        "min_high_commitment_tokens": 3,
        "fail_gini_below": 0.3,
        "fail_ratio_below": 1.5,
    },
}

RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=True)

print("")
print("  Results saved to: %s" % RESULTS_PATH)
print("=" * 70)
