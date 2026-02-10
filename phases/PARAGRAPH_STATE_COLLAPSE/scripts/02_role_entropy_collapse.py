#!/usr/bin/env python3
"""
Test 02: Role Entropy Collapse
Phase: PARAGRAPH_STATE_COLLAPSE

Purpose: Test whether Shannon entropy of prefix_role distribution decreases
across paragraph body lines. C963 proved role FRACTIONS are flat; this tests
whether role DIVERSITY (entropy, distinct count) shrinks -- an orthogonal measure.

Method:
  1. Load Currier B tokens. Build paragraphs via par_initial field.
  2. Keep paragraphs with 5+ lines. Skip header (line 0).
  3. For each body line: classify tokens by role, compute Shannon entropy
     of role distribution and n_distinct_roles.
  4. Spearman rho vs quintile position. Partial rho controlling for line_length.
  5. Shuffle test (1000x, seed=42). Bonferroni for 2 sub-tests.

Provenance: C963 (body homogeneity), C556 (role classification)
"""
import sys
import json
import math
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path("C:/git/voynich").resolve()
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
RESULTS_PATH = PROJECT_ROOT / "phases/PARAGRAPH_STATE_COLLAPSE/results/02_role_entropy_collapse.json"

# ============================================================
# ROLE CLASSIFICATION (from class map)
# ============================================================
with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
    class_data = json.load(f)
token_to_class = {k: int(v) for k, v in class_data["token_to_class"].items()}
class_to_role = {int(k): v for k, v in class_data["class_to_role"].items()}


def get_role(word):
    cls = token_to_class.get(word, -1)
    return class_to_role.get(cls, "UNKNOWN")


# ============================================================
# SHANNON ENTROPY
# ============================================================
def shannon_entropy(counts):
    """Shannon entropy in bits from a Counter/dict of counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counts.values() if c > 0]
    return -sum(p * math.log2(p) for p in probs)


# ============================================================
# PARTIAL SPEARMAN RHO (controlling for confound via OLS residuals)
# ============================================================
def partial_spearman(x, y, confound):
    """
    Partial Spearman rho of x vs y, controlling for confound.
    Residualize both x and y against confound using OLS, then correlate residuals.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    confound = np.asarray(confound, dtype=float)

    # OLS: residualize x against confound
    A = np.column_stack([confound, np.ones(len(confound))])
    coef_x, _, _, _ = np.linalg.lstsq(A, x, rcond=None)
    resid_x = x - A @ coef_x

    # OLS: residualize y against confound
    coef_y, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    resid_y = y - A @ coef_y

    return stats.spearmanr(resid_x, resid_y)


# ============================================================
# DATA LOADING: Build paragraphs from par_initial
# ============================================================
tx = Transcript()

# Step 1: Collect line-level data with paragraph structure
line_tokens = defaultdict(list)      # (folio, line) -> [Token, ...]
line_meta = {}                       # (folio, line) -> metadata
folio_lines_ordered = defaultdict(list)  # folio -> [(folio, line), ...]

for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    if key not in line_meta:
        line_meta[key] = {
            'folio': t.folio,
            'line': t.line,
            'par_initial': False,
            'par_final': False,
        }
        folio_lines_ordered[t.folio].append(key)
    if t.par_initial:
        line_meta[key]['par_initial'] = True
    if t.par_final:
        line_meta[key]['par_final'] = True

# Deduplicate folio line lists (preserve order)
for f in folio_lines_ordered:
    seen = set()
    deduped = []
    for k in folio_lines_ordered[f]:
        if k not in seen:
            seen.add(k)
            deduped.append(k)
    folio_lines_ordered[f] = deduped

# Step 2: Build paragraphs from par_initial / par_final markers
all_paragraphs = []  # list of lists of (folio, line) keys

for folio, keys in folio_lines_ordered.items():
    current_para = []
    for key in keys:
        meta = line_meta[key]
        if meta['par_initial'] and current_para:
            all_paragraphs.append(current_para)
            current_para = []
        current_para.append(key)
        if meta['par_final']:
            all_paragraphs.append(current_para)
            current_para = []
    if current_para:
        all_paragraphs.append(current_para)

total_paragraphs = len(all_paragraphs)

# Step 3: Filter to paragraphs with 5+ lines
big_paragraphs = [p for p in all_paragraphs if len(p) >= 5]
n_big = len(big_paragraphs)

print("=" * 65)
print("Test 02: Role Entropy Collapse")
print("Phase: PARAGRAPH_STATE_COLLAPSE")
print("=" * 65)
print(f"\nTotal paragraphs: {total_paragraphs}")
print(f"Paragraphs with 5+ lines: {n_big}")

# ============================================================
# PER BODY LINE: compute role entropy and n_distinct_roles
# ============================================================
# For each big paragraph, skip line 0 (header), keep body lines (1..N-1)
# Normalize body position to [0, 1]

positions = []       # normalized position within body
entropies = []       # Shannon entropy of role distribution
distinct_counts = [] # number of distinct roles
line_lengths = []    # number of tokens per line (confound)

for para_lines in big_paragraphs:
    # Skip header line (index 0). Body = lines 1..end
    body_lines = para_lines[1:]
    n_body = len(body_lines)
    if n_body < 2:
        continue

    for idx, key in enumerate(body_lines):
        tokens = line_tokens[key]
        words = [t.word for t in tokens]
        if not words:
            continue

        # Role classification
        roles = [get_role(w) for w in words]
        role_counts = Counter(roles)
        ent = shannon_entropy(role_counts)
        n_distinct = len(role_counts)
        n_tokens = len(words)

        # Normalized position: 0 = first body line, 1 = last body line
        norm_pos = idx / (n_body - 1) if n_body > 1 else 0.5

        positions.append(norm_pos)
        entropies.append(ent)
        distinct_counts.append(n_distinct)
        line_lengths.append(n_tokens)

positions = np.array(positions)
entropies = np.array(entropies)
distinct_counts = np.array(distinct_counts, dtype=float)
line_lengths = np.array(line_lengths, dtype=float)

n_body_lines = len(positions)
print(f"Body lines analyzed: {n_body_lines}")

# ============================================================
# ANALYSIS
# ============================================================
# 1. Raw Spearman rho
rho_ent_raw, p_ent_raw = stats.spearmanr(positions, entropies)
rho_dist_raw, p_dist_raw = stats.spearmanr(positions, distinct_counts)

# 2. Partial Spearman rho controlling for line_length
rho_ent_partial, p_ent_partial = partial_spearman(positions, entropies, line_lengths)
rho_dist_partial, p_dist_partial = partial_spearman(positions, distinct_counts, line_lengths)

print(f"\n--- Raw Spearman correlations ---")
print(f"  role_entropy vs position:     rho = {rho_ent_raw:+.4f}, p = {p_ent_raw:.6f}")
print(f"  n_distinct_roles vs position: rho = {rho_dist_raw:+.4f}, p = {p_dist_raw:.6f}")
print(f"\n--- Partial Spearman (controlling for line_length) ---")
print(f"  role_entropy vs position:     rho = {rho_ent_partial:+.4f}, p = {p_ent_partial:.6f}")
print(f"  n_distinct_roles vs position: rho = {rho_dist_partial:+.4f}, p = {p_dist_partial:.6f}")

# ============================================================
# QUINTILE MEANS
# ============================================================
quintile_labels = ["Q0", "Q1", "Q2", "Q3", "Q4"]
quintile_edges = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0001]

ent_quintile_means = {}
dist_quintile_means = {}

for qi in range(5):
    lo = quintile_edges[qi]
    hi = quintile_edges[qi + 1]
    mask = (positions >= lo) & (positions < hi)
    label = quintile_labels[qi]
    ent_quintile_means[label] = float(np.mean(entropies[mask])) if mask.any() else 0.0
    dist_quintile_means[label] = float(np.mean(distinct_counts[mask])) if mask.any() else 0.0

print(f"\n--- Quintile means: role_entropy ---")
for q in quintile_labels:
    print(f"  {q}: {ent_quintile_means[q]:.4f}")

print(f"\n--- Quintile means: n_distinct_roles ---")
for q in quintile_labels:
    print(f"  {q}: {dist_quintile_means[q]:.4f}")

# ============================================================
# SHUFFLE TEST (1000x, seed=42)
# ============================================================
N_SHUFFLES = 1000
rng = np.random.RandomState(42)

shuffle_rho_ent_raw = np.zeros(N_SHUFFLES)
shuffle_rho_ent_partial = np.zeros(N_SHUFFLES)
shuffle_rho_dist_raw = np.zeros(N_SHUFFLES)
shuffle_rho_dist_partial = np.zeros(N_SHUFFLES)

print(f"\nRunning shuffle test ({N_SHUFFLES} iterations)...")

for i in range(N_SHUFFLES):
    perm_positions = rng.permutation(positions)

    # Raw rhos under shuffle
    shuffle_rho_ent_raw[i], _ = stats.spearmanr(perm_positions, entropies)
    shuffle_rho_dist_raw[i], _ = stats.spearmanr(perm_positions, distinct_counts)

    # Partial rhos under shuffle
    r_ent_p, _ = partial_spearman(perm_positions, entropies, line_lengths)
    shuffle_rho_ent_partial[i] = r_ent_p

    r_dist_p, _ = partial_spearman(perm_positions, distinct_counts, line_lengths)
    shuffle_rho_dist_partial[i] = r_dist_p

# Empirical p-values (one-tailed: we test for NEGATIVE rho, i.e. collapse)
shuffle_p_ent_raw = float(np.mean(shuffle_rho_ent_raw <= rho_ent_raw))
shuffle_p_ent_partial = float(np.mean(shuffle_rho_ent_partial <= rho_ent_partial))
shuffle_p_dist_raw = float(np.mean(shuffle_rho_dist_raw <= rho_dist_raw))
shuffle_p_dist_partial = float(np.mean(shuffle_rho_dist_partial <= rho_dist_partial))

# Bonferroni correction: 2 sub-tests, alpha=0.01
bonferroni_alpha = 0.005

print(f"\n--- Shuffle test results (empirical p-values, one-tailed negative) ---")
print(f"  role_entropy raw:     shuffle_p = {shuffle_p_ent_raw:.4f}")
print(f"  role_entropy partial: shuffle_p = {shuffle_p_ent_partial:.4f}")
print(f"  n_distinct raw:       shuffle_p = {shuffle_p_dist_raw:.4f}")
print(f"  n_distinct partial:   shuffle_p = {shuffle_p_dist_partial:.4f}")
print(f"  Bonferroni alpha:     {bonferroni_alpha}")

# ============================================================
# VERDICT
# ============================================================
# A metric is significant if its length-controlled shuffle p < Bonferroni threshold
# AND the partial rho is negative (collapse direction)
significant_metrics = []

if rho_ent_partial < 0 and shuffle_p_ent_partial < bonferroni_alpha:
    significant_metrics.append("role_entropy")

if rho_dist_partial < 0 and shuffle_p_dist_partial < bonferroni_alpha:
    significant_metrics.append("n_distinct_roles")

if significant_metrics:
    verdict = "PASS"
else:
    verdict = "FAIL"

print(f"\n{'='*65}")
print(f"VERDICT: {verdict}")
if significant_metrics:
    print(f"  Significant metrics (negative partial rho, shuffle p < {bonferroni_alpha}):")
    for m in significant_metrics:
        print(f"    - {m}")
else:
    print(f"  Neither metric shows significant negative length-controlled rho.")
print(f"{'='*65}")

# ============================================================
# OUTPUT JSON
# ============================================================
results = {
    "test": "02_role_entropy_collapse",
    "phase": "PARAGRAPH_STATE_COLLAPSE",
    "verdict": verdict,
    "counts": {
        "total_paragraphs": total_paragraphs,
        "big_paragraphs": n_big,
        "body_lines": n_body_lines,
    },
    "role_entropy": {
        "raw_rho": round(float(rho_ent_raw), 6),
        "raw_p": round(float(p_ent_raw), 6),
        "partial_rho": round(float(rho_ent_partial), 6),
        "partial_p": round(float(p_ent_partial), 6),
        "shuffle_p_raw": round(shuffle_p_ent_raw, 4),
        "shuffle_p_partial": round(shuffle_p_ent_partial, 4),
        "quintile_means": {k: round(v, 6) for k, v in ent_quintile_means.items()},
    },
    "n_distinct_roles": {
        "raw_rho": round(float(rho_dist_raw), 6),
        "raw_p": round(float(p_dist_raw), 6),
        "partial_rho": round(float(rho_dist_partial), 6),
        "partial_p": round(float(p_dist_partial), 6),
        "shuffle_p_raw": round(shuffle_p_dist_raw, 4),
        "shuffle_p_partial": round(shuffle_p_dist_partial, 4),
        "quintile_means": {k: round(v, 6) for k, v in dist_quintile_means.items()},
    },
    "bonferroni_alpha": bonferroni_alpha,
    "significant_metrics": significant_metrics,
}

RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: {RESULTS_PATH}")
