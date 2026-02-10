"""
Test 07: Phase Interleaving Pattern
Phase: LINE_CONTROL_BLOCK_GRAMMAR

Purpose: Determine whether KERNEL, LINK, and FL phases within a line follow
strict sequential ordering (C813: LINK -> KERNEL -> FL) or are interleaved.
This tests whether lines are structured as sequential phase blocks or as
freely interleaved instruction streams.

Method:
  1. Build Currier B lines, assign each token a PHASE (KERNEL, LINK, FL, OTHER).
  2. For multi-phase lines (2+ distinct phases among KERNEL/LINK/FL):
     a. Count contiguous same-phase runs (phase-specific tokens only).
     b. Alternation rate = phase transitions / (n_phase_tokens - 1).
     c. Sequential compliance: all LINK before all KERNEL before all FL.
  3. Pairwise ordering strength for LINK-KERNEL, KERNEL-FL, LINK-FL.
  4. Shuffle test (1000x, seed=42): permute ALL token positions within each
     line, recompute alternation rate and sequential compliance.
  5. Verdict based on compliance vs shuffle and alternation rate significance.

Provenance: C813 (canonical phase ordering), C815 (phase flexibility),
            C807/C810 (LINK-FL inverse relationship)
"""

import sys
import json
import math
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript, Morphology


# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path("C:/git/voynich").resolve()
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
RESULTS_PATH = PROJECT_ROOT / "phases/LINE_CONTROL_BLOCK_GRAMMAR/results/07_phase_interleaving.json"

# ---------------------------------------------------------------------------
# LOAD CLASS MAP
# ---------------------------------------------------------------------------
with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
    class_data = json.load(f)

token_to_class = {k: int(v) for k, v in class_data["token_to_class"].items()}
class_to_role = {int(k): v for k, v in class_data["class_to_role"].items()}

# Phase assignment sets
ENERGY_CLASSES = {c for c, r in class_to_role.items() if r == "ENERGY_OPERATOR"}
FL_CLASSES = {c for c, r in class_to_role.items() if r == "FLOW_OPERATOR"}
LINK_CLASS = 29  # Class 29 is the LINK operator


# ---------------------------------------------------------------------------
# PHASE ASSIGNMENT
# ---------------------------------------------------------------------------
def assign_phase(word, token_to_class_map):
    """Assign a token to KERNEL, LINK, FL, or OTHER."""
    cls = token_to_class_map.get(word, -1)
    if cls == LINK_CLASS:
        return "LINK"
    if cls in ENERGY_CLASSES:
        return "KERNEL"
    if cls in FL_CLASSES:
        return "FL"
    return "OTHER"


# ---------------------------------------------------------------------------
# BUILD LINES
# ---------------------------------------------------------------------------
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

print("=" * 70)
print("TEST 07: PHASE INTERLEAVING PATTERN")
print("=" * 70)
print("  Total Currier B lines: %d" % n_lines)
print("  Total tokens: %d" % n_tokens)

# ---------------------------------------------------------------------------
# ASSIGN PHASES TO ALL TOKENS
# ---------------------------------------------------------------------------
# Pre-compute phase for each token type (O(1) lookup)
all_words = set()
for words in lines.values():
    all_words.update(words)

word_phase = {w: assign_phase(w, token_to_class) for w in all_words}

# Count phase distribution
phase_counts = Counter(word_phase.values())
print("\n  Phase distribution (unique token types):")
for phase in ["KERNEL", "LINK", "FL", "OTHER"]:
    print("    %s: %d types" % (phase, phase_counts.get(phase, 0)))

# Count token instances per phase
instance_counts = Counter()
for words in lines.values():
    for w in words:
        instance_counts[word_phase[w]] += 1

print("\n  Phase distribution (token instances):")
for phase in ["KERNEL", "LINK", "FL", "OTHER"]:
    cnt = instance_counts.get(phase, 0)
    pct = 100.0 * cnt / n_tokens if n_tokens > 0 else 0
    print("    %s: %d (%.1f%%)" % (phase, cnt, pct))

# ---------------------------------------------------------------------------
# IDENTIFY MULTI-PHASE LINES
# ---------------------------------------------------------------------------
PHASE_SET = {"KERNEL", "LINK", "FL"}

line_data = []
for key in sorted(lines.keys()):
    words = lines[key]
    phases = [word_phase[w] for w in words]

    # Extract only KERNEL/LINK/FL tokens with their positions
    phase_tokens = [(i, phases[i]) for i in range(len(phases)) if phases[i] in PHASE_SET]
    distinct_phases = set(p for _, p in phase_tokens)

    if len(distinct_phases) >= 2:
        line_data.append({
            "key": key,
            "words": words,
            "phases": phases,
            "phase_tokens": phase_tokens,
            "distinct_phases": distinct_phases,
        })

n_multi = len(line_data)
print("\n  Lines with 2+ distinct phases (KERNEL/LINK/FL): %d" % n_multi)

# Distribution of phase combinations
combo_counts = Counter()
for ld in line_data:
    combo = tuple(sorted(ld["distinct_phases"]))
    combo_counts[combo] += 1

print("  Phase combination distribution:")
for combo, cnt in combo_counts.most_common():
    print("    %s: %d lines" % ("-".join(combo), cnt))


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------
def count_phase_runs(phase_tokens):
    """Count contiguous runs of same-phase tokens."""
    if len(phase_tokens) <= 1:
        return len(phase_tokens)
    runs = 1
    for i in range(1, len(phase_tokens)):
        if phase_tokens[i][1] != phase_tokens[i - 1][1]:
            runs += 1
    return runs


def alternation_rate(phase_tokens):
    """Fraction of transitions between consecutive phase tokens that change phase."""
    if len(phase_tokens) < 2:
        return None
    transitions = 0
    for i in range(1, len(phase_tokens)):
        if phase_tokens[i][1] != phase_tokens[i - 1][1]:
            transitions += 1
    return transitions / (len(phase_tokens) - 1)


def is_sequentially_compliant(phase_tokens):
    """Check if phases follow strict LINK -> KERNEL -> FL ordering."""
    phase_order = {"LINK": 0, "KERNEL": 1, "FL": 2}
    phase_seq = [p for _, p in phase_tokens]
    for i in range(1, len(phase_seq)):
        if phase_order[phase_seq[i]] < phase_order[phase_seq[i - 1]]:
            return False
    return True


def pairwise_ordering_strength(phase_tokens, early_phase, late_phase):
    """Compute fraction of pairwise comparisons where early_phase appears before late_phase."""
    early_positions = [pos for pos, p in phase_tokens if p == early_phase]
    late_positions = [pos for pos, p in phase_tokens if p == late_phase]

    if not early_positions or not late_positions:
        return None, 0

    correct = 0
    total = 0
    for ep in early_positions:
        for lp in late_positions:
            total += 1
            if ep < lp:
                correct += 1

    return correct / total if total > 0 else None, total


# ---------------------------------------------------------------------------
# COMPUTE REAL METRICS
# ---------------------------------------------------------------------------
print("\n  Computing phase interleaving metrics...")

real_alternation_rates = []
real_compliance = []
real_runs = []

for ld in line_data:
    pt = ld["phase_tokens"]
    ar = alternation_rate(pt)
    if ar is not None:
        real_alternation_rates.append(ar)
    sc = is_sequentially_compliant(pt)
    real_compliance.append(sc)
    real_runs.append(count_phase_runs(pt))

mean_alt_rate = float(np.mean(real_alternation_rates)) if real_alternation_rates else 0.0
compliance_rate = sum(real_compliance) / len(real_compliance) if real_compliance else 0.0
mean_runs = float(np.mean(real_runs)) if real_runs else 0.0

print("  Mean alternation rate: %.4f" % mean_alt_rate)
print("  Sequential compliance (LINK->KERNEL->FL): %.4f (%.1f%%)" % (
    compliance_rate, 100 * compliance_rate))
print("  Mean phase-specific runs per line: %.2f" % mean_runs)

# ---------------------------------------------------------------------------
# PAIRWISE ORDERING STRENGTHS
# ---------------------------------------------------------------------------
print("\n  Pairwise ordering strengths:")
pair_names = [("LINK", "KERNEL"), ("KERNEL", "FL"), ("LINK", "FL")]
pair_strengths = {}

for early, late in pair_names:
    strengths = []
    total_pairs = 0
    for ld in line_data:
        pt = ld["phase_tokens"]
        s, n = pairwise_ordering_strength(pt, early, late)
        if s is not None:
            strengths.append(s)
            total_pairs += n

    if strengths:
        mean_s = float(np.mean(strengths))
        median_s = float(np.median(strengths))
        n_lines_with_pair = len(strengths)
    else:
        mean_s = None
        median_s = None
        n_lines_with_pair = 0

    pair_strengths["%s->%s" % (early, late)] = {
        "mean_strength": mean_s,
        "median_strength": median_s,
        "n_lines_with_pair": n_lines_with_pair,
        "total_pairwise_comparisons": total_pairs,
    }
    if mean_s is not None:
        print("    %s -> %s: mean=%.4f, median=%.4f, n_lines=%d, n_pairs=%d" % (
            early, late, mean_s, median_s, n_lines_with_pair, total_pairs))
    else:
        print("    %s -> %s: no data" % (early, late))


# ---------------------------------------------------------------------------
# SHUFFLE TEST (1000x, seed=42)
# ---------------------------------------------------------------------------
print("\n  Shuffle test (1000 iterations, seed=42)...")
N_SHUFFLES = 1000
rng = np.random.default_rng(42)

# Pre-build line structures for shuffling
shuffle_lines = []
for ld in line_data:
    words = ld["words"]
    phases = ld["phases"]
    shuffle_lines.append({
        "n": len(words),
        "phases": np.array(phases),
    })

shuffle_alt_rates = []
shuffle_compliances = []

for shuf_i in range(N_SHUFFLES):
    shuf_alt = []
    shuf_comp = []

    for sl in shuffle_lines:
        n = sl["n"]
        perm = rng.permutation(n)
        shuffled_phases = sl["phases"][perm]

        phase_tokens_shuf = []
        for pos in range(n):
            if shuffled_phases[pos] in PHASE_SET:
                phase_tokens_shuf.append((pos, shuffled_phases[pos]))

        if len(set(p for _, p in phase_tokens_shuf)) < 2:
            continue

        ar = alternation_rate(phase_tokens_shuf)
        if ar is not None:
            shuf_alt.append(ar)
        sc = is_sequentially_compliant(phase_tokens_shuf)
        shuf_comp.append(sc)

    if shuf_alt:
        shuffle_alt_rates.append(float(np.mean(shuf_alt)))
    if shuf_comp:
        shuffle_compliances.append(sum(shuf_comp) / len(shuf_comp))

shuffle_alt_rates = np.array(shuffle_alt_rates)
shuffle_compliances = np.array(shuffle_compliances)

shuf_alt_mean = float(np.mean(shuffle_alt_rates))
shuf_alt_std = float(np.std(shuffle_alt_rates))
shuf_comp_mean = float(np.mean(shuffle_compliances))
shuf_comp_std = float(np.std(shuffle_compliances))

# P-values
p_alt = float(np.mean(shuffle_alt_rates <= mean_alt_rate))
p_comp = float(np.mean(shuffle_compliances >= compliance_rate))

# Z-scores
z_alt = (mean_alt_rate - shuf_alt_mean) / shuf_alt_std if shuf_alt_std > 0 else 0.0
z_comp = (compliance_rate - shuf_comp_mean) / shuf_comp_std if shuf_comp_std > 0 else 0.0

print("  Alternation rate: real=%.4f, shuffle_mean=%.4f +/- %.4f, z=%.2f, p=%.4f" % (
    mean_alt_rate, shuf_alt_mean, shuf_alt_std, z_alt, p_alt))
print("  Compliance: real=%.4f, shuffle_mean=%.4f +/- %.4f, z=%.2f, p=%.4f" % (
    compliance_rate, shuf_comp_mean, shuf_comp_std, z_comp, p_comp))

compliance_excess = compliance_rate - shuf_comp_mean
compliance_excess_pct = 100.0 * compliance_excess

print("  Compliance excess over shuffle: %.4f (%.1f pp)" % (
    compliance_excess, compliance_excess_pct))


# ---------------------------------------------------------------------------
# DETAILED BREAKDOWN: Compliance by phase combination
# ---------------------------------------------------------------------------
print("\n  Compliance by phase combination:")
combo_compliance = defaultdict(list)
combo_alt_rates = defaultdict(list)

for ld, sc, ar in zip(line_data, real_compliance, real_alternation_rates):
    combo = tuple(sorted(ld["distinct_phases"]))
    combo_compliance[combo].append(sc)
    combo_alt_rates[combo].append(ar)

combo_details = {}
for combo in sorted(combo_compliance.keys()):
    n = len(combo_compliance[combo])
    comp = sum(combo_compliance[combo]) / n
    alt = float(np.mean(combo_alt_rates[combo]))
    combo_details["-".join(combo)] = {
        "n_lines": n,
        "compliance_rate": float(comp),
        "mean_alternation_rate": float(alt),
    }
    print("    %s: n=%d, compliance=%.4f, alternation=%.4f" % (
        "-".join(combo), n, comp, alt))

# ---------------------------------------------------------------------------
# RUN LENGTH DISTRIBUTION
# ---------------------------------------------------------------------------
run_dist = Counter(real_runs)
print("\n  Run count distribution:")
for n_runs, count in sorted(run_dist.items()):
    print("    %d runs: %d lines" % (n_runs, count))


# ---------------------------------------------------------------------------
# VERDICT
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

seq_pass = (compliance_excess > 0.30) and (p_alt < 0.001)
interleaved_pass = (compliance_excess < 0.15) and (p_alt > 0.05)
mixed = (0.15 <= compliance_excess <= 0.30)

if seq_pass:
    verdict = "PASS_SEQUENTIAL"
    detail = ("Sequential compliance %.1f%% exceeds shuffle by %.1f pp (>30pp required). "
              "Alternation rate significantly below shuffle (p=%.4f < 0.001). "
              "Lines follow canonical LINK->KERNEL->FL phase ordering.") % (
        100 * compliance_rate, compliance_excess_pct, p_alt)
elif interleaved_pass:
    verdict = "PASS_INTERLEAVED"
    detail = ("Sequential compliance excess %.1f pp (<15pp). "
              "Alternation rate not significantly different from shuffle (p=%.4f). "
              "Phases are freely interleaved within lines.") % (
        compliance_excess_pct, p_alt)
elif mixed:
    verdict = "MIXED"
    some_ordered = sum(1 for k, v in pair_strengths.items()
                       if v["mean_strength"] is not None and v["mean_strength"] > 0.60)
    detail = ("Compliance excess %.1f pp (15-30pp range). "
              "%d/3 phase pairs show ordering >0.60. "
              "Partial phase ordering exists but is not strict.") % (
        compliance_excess_pct, some_ordered)
else:
    if compliance_excess > 0.30 and p_alt >= 0.001:
        verdict = "PARTIAL_SEQUENTIAL"
        detail = ("High compliance excess %.1f pp but alternation rate "
                  "not significantly below shuffle (p=%.4f >= 0.001).") % (
            compliance_excess_pct, p_alt)
    elif compliance_excess < 0.15 and p_alt <= 0.05:
        verdict = "PARTIAL_INTERLEAVED"
        detail = ("Low compliance excess %.1f pp but alternation rate "
                  "significantly different from shuffle (p=%.4f).") % (
            compliance_excess_pct, p_alt)
    else:
        verdict = "INCONCLUSIVE"
        detail = ("Compliance excess %.1f pp, alternation p=%.4f. "
                  "No clear pattern detected.") % (compliance_excess_pct, p_alt)

print("  %s" % verdict)
print("  %s" % detail)

print("\n  Pair ordering summary:")
for pair_name, pair_data in pair_strengths.items():
    s = pair_data["mean_strength"]
    if s is not None:
        direction = "ORDERED" if s > 0.60 else ("REVERSED" if s < 0.40 else "NEUTRAL")
        print("    %s: %.4f [%s]" % (pair_name, s, direction))


# ---------------------------------------------------------------------------
# JSON OUTPUT
# ---------------------------------------------------------------------------
output = {
    "test": "07_phase_interleaving",
    "phase": "LINE_CONTROL_BLOCK_GRAMMAR",
    "purpose": ("Determine whether KERNEL, LINK, and FL phases within a line "
                "follow strict sequential ordering (C813) or are interleaved"),
    "provenance": ["C813", "C815", "C807", "C810"],
    "data": {
        "total_lines_currier_b": n_lines,
        "total_tokens": n_tokens,
        "phase_instance_counts": {p: int(c) for p, c in instance_counts.items()},
        "multi_phase_lines": n_multi,
        "phase_combination_distribution": {
            "-".join(combo): int(cnt) for combo, cnt in combo_counts.most_common()
        },
    },
    "phase_assignment": {
        "KERNEL": "ENERGY_OPERATOR role (classes: %s)" % sorted(ENERGY_CLASSES),
        "LINK": "Class 29",
        "FL": "FLOW_OPERATOR role (classes: %s)" % sorted(FL_CLASSES),
        "OTHER": "Everything else (AUXILIARY, CORE_CONTROL, FREQUENT_OPERATOR, UNK)",
    },
    "metrics": {
        "mean_alternation_rate": float(mean_alt_rate),
        "sequential_compliance_rate": float(compliance_rate),
        "mean_phase_runs_per_line": float(mean_runs),
        "run_count_distribution": {str(k): int(v) for k, v in sorted(run_dist.items())},
    },
    "pairwise_ordering": pair_strengths,
    "combo_details": combo_details,
    "shuffle_test": {
        "n_shuffles": N_SHUFFLES,
        "seed": 42,
        "method": "Permute ALL token positions within each line",
        "alternation_rate": {
            "real": float(mean_alt_rate),
            "shuffle_mean": float(shuf_alt_mean),
            "shuffle_std": float(shuf_alt_std),
            "z_score": float(z_alt),
            "p_value": float(p_alt),
        },
        "sequential_compliance": {
            "real": float(compliance_rate),
            "shuffle_mean": float(shuf_comp_mean),
            "shuffle_std": float(shuf_comp_std),
            "z_score": float(z_comp),
            "p_value": float(p_comp),
            "excess_over_shuffle": float(compliance_excess),
            "excess_pp": float(compliance_excess_pct),
        },
    },
    "verdict": verdict,
    "verdict_detail": detail,
    "pass_criteria": {
        "PASS_SEQUENTIAL": "Compliance >30pp above shuffle AND alternation p<0.001",
        "PASS_INTERLEAVED": "Compliance <15pp above shuffle AND alternation p>0.05",
        "MIXED": "Compliance 15-30pp, some pairs ordered",
    },
}

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print("\n  Results saved to %s" % RESULTS_PATH)
