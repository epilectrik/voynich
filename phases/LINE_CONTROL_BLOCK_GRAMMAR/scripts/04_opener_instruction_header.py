"""
LINE_CONTROL_BLOCK_GRAMMAR - Test 04: Opener-as-Instruction-Header

Purpose: Determine whether a line begins with *this kind of instruction*
(role-level) or *this specific instruction* (token-level). If the body of a
line is predictable from the opener token beyond what the opener role already
explains, the opener functions as a specific instruction header, not merely
a role marker.

Method:
  1. Build Currier B lines, identify opener token and its class/role.
  2. Group lines by opener ROLE. For each role with 30+ lines, compute
     normalized body token frequency vectors.
  3. For top 5 most common opener tokens: JSD between body of lines opened
     by that token vs lines opened by other tokens of same role.
  4. Nearest-centroid classifier (LOO cross-validation) at role and token
     level.
  5. Shuffle test (1000x, seed=42) for JSD significance.
  6. Verdict based on accuracy thresholds and JSD significance.
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript, Morphology

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path("C:/git/voynich").resolve()
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
RESULTS_PATH = PROJECT_ROOT / "phases/LINE_CONTROL_BLOCK_GRAMMAR/results/04_opener_instruction_header.json"

# ---------------------------------------------------------------------------
# LOAD CLASS MAP
# ---------------------------------------------------------------------------
with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
    class_data = json.load(f)

token_to_class = {k: int(v) for k, v in class_data["token_to_class"].items()}
token_to_role = class_data.get("token_to_role", {})
class_to_role = {int(k): v for k, v in class_data["class_to_role"].items()}


def get_role(word):
    """Get role for a word, checking token_to_role first, then class_to_role."""
    if word in token_to_role:
        return token_to_role[word]
    cls = token_to_class.get(word, -1)
    if cls >= 0 and cls in class_to_role:
        return class_to_role[cls]
    return "UNK"


# ---------------------------------------------------------------------------
# BUILD LINES
# ---------------------------------------------------------------------------
tx = Transcript()
lines = defaultdict(list)
for t in tx.currier_b():
    word = t.word.replace("*", "").strip()
    if not word:
        continue
    lines[(t.folio, t.line)].append(word)

# Filter to lines with at least 3 tokens (opener + 2 body)
line_keys = [k for k, v in lines.items() if len(v) >= 3]

print("=" * 70)
print("TEST 04: OPENER-AS-INSTRUCTION-HEADER")
print("=" * 70)
print("  Total lines (Currier B): %d" % len(lines))
print("  Lines with 3+ tokens: %d" % len(line_keys))

# ---------------------------------------------------------------------------
# IDENTIFY OPENER TOKEN AND ROLE FOR EACH LINE
# ---------------------------------------------------------------------------
line_info = []
for key in line_keys:
    words = lines[key]
    opener = words[0]
    role = get_role(opener)
    body = words[1:]
    line_info.append({
        "key": key,
        "opener": opener,
        "role": role,
        "body": body,
        "folio": key[0],
    })

# Count opener roles
role_counts = Counter(li["role"] for li in line_info)
print("\n  Opener role distribution:")
for role, cnt in role_counts.most_common():
    print("    %s: %d lines" % (role, cnt))

# Valid roles: 30+ lines
valid_roles = sorted(r for r, c in role_counts.items() if c >= 30 and r != "UNK")
print("\n  Roles with 30+ lines: %s" % valid_roles)

# Filter line_info to valid roles
line_info_valid = [li for li in line_info if li["role"] in valid_roles]
print("  Lines with valid-role openers: %d" % len(line_info_valid))

# ---------------------------------------------------------------------------
# TOP 5 MOST COMMON OPENER TOKENS (among valid-role lines)
# ---------------------------------------------------------------------------
opener_token_counts = Counter(li["opener"] for li in line_info_valid)
top5_openers = [tok for tok, _ in opener_token_counts.most_common(5)]
print("\n  Top 5 opener tokens:")
for tok in top5_openers:
    r = get_role(tok)
    print("    %r (role=%s, count=%d)" % (tok, r, opener_token_counts[tok]))

# ---------------------------------------------------------------------------
# JENSEN-SHANNON DIVERGENCE
# ---------------------------------------------------------------------------
def jsd(p, q):
    """Jensen-Shannon divergence between two probability distributions."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p_sum = p.sum()
    q_sum = q.sum()
    if p_sum == 0 or q_sum == 0:
        return 0.0
    p = p / p_sum
    q = q / q_sum
    m = 0.5 * (p + q)

    def kl(a, b):
        mask = (a > 0) & (b > 0)
        return np.sum(a[mask] * np.log2(a[mask] / b[mask]))

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


# Build global vocabulary from body tokens (appearing 5+ times)
all_body_tokens = Counter()
for li in line_info_valid:
    all_body_tokens.update(li["body"])

vocab = sorted(t for t, c in all_body_tokens.items() if c >= 5)
vocab_idx = {t: i for i, t in enumerate(vocab)}
V = len(vocab)
print("\n  Vocabulary size (body tokens with 5+ occurrences): %d" % V)


def body_to_vector(body_words):
    """Convert body word list to normalized frequency vector."""
    vec = np.zeros(V)
    for w in body_words:
        if w in vocab_idx:
            vec[vocab_idx[w]] += 1
    total = vec.sum()
    if total > 0:
        vec /= total
    return vec


def mean_body_vector(line_list):
    """Compute mean body vector from a list of line_info dicts."""
    if not line_list:
        return np.zeros(V)
    vectors = np.array([body_to_vector(li["body"]) for li in line_list])
    return vectors.mean(axis=0)


# Compute JSD for each top-5 opener
print("\n  Jensen-Shannon Divergence (top 5 openers vs same-role peers):")
jsd_results = {}
for tok in top5_openers:
    tok_role = get_role(tok)
    tok_lines = [li for li in line_info_valid if li["opener"] == tok]
    other_lines = [li for li in line_info_valid
                   if li["role"] == tok_role and li["opener"] != tok]
    if len(tok_lines) < 5 or len(other_lines) < 5:
        print("    %r: skipped (too few lines)" % tok)
        continue
    vec_tok = mean_body_vector(tok_lines)
    vec_other = mean_body_vector(other_lines)
    d = jsd(vec_tok, vec_other)
    jsd_results[tok] = {
        "jsd": float(d),
        "role": tok_role,
        "n_tok": len(tok_lines),
        "n_other": len(other_lines),
    }
    print("    %r (role=%s): JSD=%.6f  (n_tok=%d, n_other=%d)" % (
        tok, tok_role, d, len(tok_lines), len(other_lines)))

# ---------------------------------------------------------------------------
# NEAREST CENTROID CLASSIFIER (LOO)
# ---------------------------------------------------------------------------
print("\n  Building Nearest Centroid classifier (LOO)...")

X = np.zeros((len(line_info_valid), V))
role_labels = []
opener_labels = []
for i, li in enumerate(line_info_valid):
    X[i] = body_to_vector(li["body"])
    role_labels.append(li["role"])
    opener_labels.append(li["opener"])

role_labels = np.array(role_labels)
opener_labels = np.array(opener_labels)
unique_roles = sorted(valid_roles)
N = len(X)

# --- Role-level LOO ---
print("  Role-level classification (%d samples, %d roles)..." % (
    N, len(unique_roles)))
role_correct = 0
confusion_matrix = defaultdict(int)

# Pre-compute per-role sums and counts for efficient LOO
role_sums = {}
role_ns = {}
for r in unique_roles:
    mask = role_labels == r
    role_sums[r] = X[mask].sum(axis=0)
    role_ns[r] = int(mask.sum())

for i in range(N):
    true_role = role_labels[i]
    best_dist = float("inf")
    pred_role = None
    for r in unique_roles:
        if r == true_role:
            n_r = role_ns[r] - 1
            if n_r == 0:
                continue
            centroid = (role_sums[r] - X[i]) / n_r
        else:
            if role_ns[r] == 0:
                continue
            centroid = role_sums[r] / role_ns[r]
        dist = np.sum((X[i] - centroid) ** 2)
        if dist < best_dist:
            best_dist = dist
            pred_role = r
    if pred_role == true_role:
        role_correct += 1
    confusion_matrix[(true_role, pred_role)] += 1

role_accuracy = role_correct / N
role_chance = 1.0 / len(unique_roles)
print("  Role-level accuracy: %.4f (chance: %.4f)" % (role_accuracy, role_chance))

# Print confusion matrix
print("\n  Confusion matrix (role-level):")
header = "  TRUE\\PRED  " + "  ".join(
    "%8s" % r[:8] for r in unique_roles)
print(header)
for true_r in unique_roles:
    row = "  %8s  " % true_r[:8]
    for pred_r in unique_roles:
        cnt = confusion_matrix.get((true_r, pred_r), 0)
        row += "  %8d" % cnt
    print(row)

# --- Token-level LOO (top 5 openers only) ---
print("\n  Token-level classification (top 5 openers only)...")
top5_mask = np.array([o in top5_openers for o in opener_labels])
X_t5 = X[top5_mask]
opener_t5 = opener_labels[top5_mask]
unique_t5 = sorted(set(opener_t5))
N_t5 = len(X_t5)

if N_t5 > 0 and len(unique_t5) >= 2:
    tok_sums = {}
    tok_ns = {}
    for t in unique_t5:
        mask = opener_t5 == t
        tok_sums[t] = X_t5[mask].sum(axis=0)
        tok_ns[t] = int(mask.sum())

    tok_correct = 0
    for i in range(N_t5):
        true_tok = opener_t5[i]
        best_dist = float("inf")
        pred_tok = None
        for t in unique_t5:
            if t == true_tok:
                n_t = tok_ns[t] - 1
                if n_t == 0:
                    continue
                centroid = (tok_sums[t] - X_t5[i]) / n_t
            else:
                if tok_ns[t] == 0:
                    continue
                centroid = tok_sums[t] / tok_ns[t]
            dist = np.sum((X_t5[i] - centroid) ** 2)
            if dist < best_dist:
                best_dist = dist
                pred_tok = t
        if pred_tok == true_tok:
            tok_correct += 1

    token_accuracy = tok_correct / N_t5
    token_chance = 1.0 / len(unique_t5)
    print("  Token-level accuracy: %.4f (chance: %.4f, n=%d, classes=%d)" % (
        token_accuracy, token_chance, N_t5, len(unique_t5)))
else:
    token_accuracy = 0.0
    token_chance = 0.0
    print("  Token-level: insufficient data (n=%d)" % N_t5)

# ---------------------------------------------------------------------------
# SHUFFLE TEST (1000x, seed=42) - JSD significance
# ---------------------------------------------------------------------------
print("\n  Shuffle test (1000 iterations, seed=42)...")
rng = np.random.default_rng(42)
N_SHUFFLES = 1000

# Group all lines by folio for opener shuffle
folio_lines = defaultdict(list)
for li in line_info_valid:
    folio_lines[li["folio"]].append(li)

# For each top-5 opener, collect shuffle JSD values
shuffle_jsds = {tok: [] for tok in jsd_results}

for shuf_i in range(N_SHUFFLES):
    # Shuffle opener tokens across lines within same folio
    shuffled_info = []
    for folio, flines in folio_lines.items():
        openers = [li["opener"] for li in flines]
        perm = rng.permutation(len(openers))
        shuffled_openers = [openers[p] for p in perm]
        for li, new_opener in zip(flines, shuffled_openers):
            shuffled_info.append({
                "key": li["key"],
                "opener": new_opener,
                "role": get_role(new_opener),
                "body": li["body"],
                "folio": li["folio"],
            })

    for tok in jsd_results:
        tok_role = get_role(tok)
        tok_lines_s = [li for li in shuffled_info if li["opener"] == tok]
        other_lines_s = [li for li in shuffled_info
                         if li["role"] == tok_role and li["opener"] != tok]
        if len(tok_lines_s) < 2 or len(other_lines_s) < 2:
            shuffle_jsds[tok].append(0.0)
            continue
        vec_tok_s = mean_body_vector(tok_lines_s)
        vec_other_s = mean_body_vector(other_lines_s)
        d_s = jsd(vec_tok_s, vec_other_s)
        shuffle_jsds[tok].append(d_s)

# Compute p-values and ratios
print("\n  JSD significance (top 5 openers):")
jsd_significant_count = 0
for tok in jsd_results:
    obs_jsd = jsd_results[tok]["jsd"]
    shuf_vals = np.array(shuffle_jsds[tok])
    shuf_mean = float(np.mean(shuf_vals))
    shuf_std = float(np.std(shuf_vals))
    p_value = float(np.mean(shuf_vals >= obs_jsd))
    ratio = obs_jsd / shuf_mean if shuf_mean > 0 else float("inf")
    jsd_results[tok]["shuffle_mean"] = shuf_mean
    jsd_results[tok]["shuffle_std"] = shuf_std
    jsd_results[tok]["p_value"] = p_value
    jsd_results[tok]["ratio_to_shuffle"] = ratio
    sig = p_value < 0.01 and ratio > 2.0
    jsd_results[tok]["significant"] = sig
    if sig:
        jsd_significant_count += 1
    sig_str = "SIGNIFICANT" if sig else "not significant"
    print("    %r: JSD=%.6f, shuffle_mean=%.6f, ratio=%.2fx, p=%.4f [%s]" % (
        tok, obs_jsd, shuf_mean, ratio, p_value, sig_str))

# ---------------------------------------------------------------------------
# VERDICT
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

print("  Role-level accuracy: %.4f (threshold: >0.40, chance: %.4f)" % (
    role_accuracy, role_chance))
print("  Token-level accuracy: %.4f (chance: %.4f)" % (
    token_accuracy, token_chance))
print("  JSD significant (p<0.01 AND >2x shuffle): %d/%d" % (
    jsd_significant_count, len(jsd_results)))

role_pass = role_accuracy > 0.40
jsd_pass = jsd_significant_count >= 2
jsd_fail = all(
    jsd_results[tok].get("ratio_to_shuffle", 0) < 1.5
    for tok in jsd_results
)
classifier_near_chance = role_accuracy < role_chance * 1.3

if role_pass and jsd_pass:
    verdict = "PASS"
    detail = ("Role-level accuracy %.3f > 0.40 AND "
              "%d opener tokens with JSD > 2x shuffle (p<0.01)") % (
        role_accuracy, jsd_significant_count)
elif classifier_near_chance and jsd_fail:
    verdict = "FAIL"
    detail = ("Classifier near chance (%.3f) AND "
              "all JSD within 1.5x shuffle") % role_accuracy
elif role_pass and not jsd_pass:
    verdict = "PARTIAL"
    detail = ("Role-level prediction works (%.3f > 0.40) "
              "but token-level JSD not significant (%d/2 needed)") % (
        role_accuracy, jsd_significant_count)
elif not role_pass and jsd_pass:
    verdict = "PARTIAL"
    detail = ("JSD significant for %d openers but "
              "role-level accuracy below threshold (%.3f <= 0.40)") % (
        jsd_significant_count, role_accuracy)
else:
    verdict = "PARTIAL"
    detail = ("Mixed results: role_accuracy=%.3f, "
              "jsd_significant=%d") % (role_accuracy, jsd_significant_count)

print("\n  VERDICT: %s" % verdict)
print("  %s" % detail)

# ---------------------------------------------------------------------------
# CONFUSION MATRIX (readable format for JSON)
# ---------------------------------------------------------------------------
confusion_list = []
for (true_r, pred_r), cnt in sorted(confusion_matrix.items()):
    confusion_list.append({
        "true_role": true_r,
        "predicted_role": pred_r,
        "count": cnt,
    })

# ---------------------------------------------------------------------------
# JSON OUTPUT
# ---------------------------------------------------------------------------
output = {
    "test": "04_opener_instruction_header",
    "phase": "LINE_CONTROL_BLOCK_GRAMMAR",
    "purpose": ("Determine whether line openers function as specific "
                "instruction headers (token-level) or merely as role "
                "markers (role-level)"),
    "data": {
        "total_lines_currier_b": len(lines),
        "lines_with_3plus_tokens": len(line_keys),
        "lines_with_valid_role_opener": len(line_info_valid),
        "valid_roles": valid_roles,
        "vocabulary_size": V,
        "top5_openers": [
            {
                "token": tok,
                "role": get_role(tok),
                "count": int(opener_token_counts[tok]),
            }
            for tok in top5_openers
        ],
    },
    "role_level_classifier": {
        "accuracy": float(role_accuracy),
        "chance": float(role_chance),
        "n_samples": N,
        "n_roles": len(unique_roles),
        "confusion_matrix": confusion_list,
        "role_counts": {r: int(role_ns[r]) for r in unique_roles},
    },
    "token_level_classifier": {
        "accuracy": float(token_accuracy),
        "chance": float(token_chance),
        "n_samples": int(N_t5),
        "n_classes": len(unique_t5) if N_t5 > 0 else 0,
    },
    "jsd_analysis": {
        tok: {
            "jsd": res["jsd"],
            "role": res["role"],
            "n_tok": res["n_tok"],
            "n_other": res["n_other"],
            "shuffle_mean": res.get("shuffle_mean", None),
            "shuffle_std": res.get("shuffle_std", None),
            "p_value": res.get("p_value", None),
            "ratio_to_shuffle": res.get("ratio_to_shuffle", None),
            "significant": res.get("significant", False),
        }
        for tok, res in jsd_results.items()
    },
    "shuffle": {
        "n_shuffles": N_SHUFFLES,
        "seed": 42,
        "method": "Shuffle opener tokens across lines within same folio",
    },
    "verdict": verdict,
    "verdict_detail": detail,
    "pass_criteria": {
        "role_accuracy_threshold": 0.40,
        "jsd_significant_needed": 2,
        "jsd_p_threshold": 0.01,
        "jsd_ratio_threshold": 2.0,
    },
}

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print("\n  Results saved to %s" % RESULTS_PATH)
