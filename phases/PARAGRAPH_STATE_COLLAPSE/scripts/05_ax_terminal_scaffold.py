#!/usr/bin/env python3
"""
Test 05: AX Terminal Scaffold
Phase: PARAGRAPH_STATE_COLLAPSE

Purpose: Test whether AUXILIARY (AX) tokens, especially the AX_FINAL subgroup,
increase toward paragraph ends. If AX_FINAL fraction rises with normalized
position, it suggests a terminal scaffolding pattern in paragraph structure.

Method:
  1. Load Currier B tokens. Build paragraphs via par_initial field.
  2. Keep paragraphs with 5+ lines. Skip header (line 0).
  3. For each body line: compute ax_fraction, ax_init_fraction,
     ax_medial_fraction, ax_final_fraction.
  4. Spearman rho vs normalized position. Partial rho controlling for line_length.
  5. Shuffle test (1000x, seed=42). Bonferroni for 4 sub-tests.

Provenance: C963 (body homogeneity), C556 (role classification),
            AUXILIARY_STRATIFICATION phase (subgroup membership)
"""
import sys
import json
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript

PROJECT_ROOT = Path("C:/git/voynich").resolve()
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
AX_TRANS_PATH = PROJECT_ROOT / "phases/AUXILIARY_STRATIFICATION/results/ax_transitions.json"
RESULTS_PATH = PROJECT_ROOT / "phases/PARAGRAPH_STATE_COLLAPSE/results/05_ax_terminal_scaffold.json"

# ============================================================
# ROLE + SUBGROUP CLASSIFICATION
# ============================================================
with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
    class_data = json.load(f)
token_to_class = {k: int(v) for k, v in class_data["token_to_class"].items()}
class_to_role = {int(k): v for k, v in class_data["class_to_role"].items()}

with open(AX_TRANS_PATH, "r", encoding="utf-8") as f:
    ax_data = json.load(f)
subgroup_membership = ax_data["subgroup_membership"]

# Build class -> subgroup lookup
AX_INIT_CLASSES = set(subgroup_membership["INIT"])
AX_FINAL_CLASSES = set(subgroup_membership["FINAL"])
AX_MEDIAL_CLASSES = set(subgroup_membership["MEDIAL"])


def get_role(word):
    cls = token_to_class.get(word, -1)
    return class_to_role.get(cls, "UNKNOWN")


def get_ax_subgroup(word):
    """Return 'INIT', 'FINAL', 'MEDIAL', or None."""
    cls = token_to_class.get(word, -1)
    if cls in AX_INIT_CLASSES:
        return "INIT"
    if cls in AX_FINAL_CLASSES:
        return "FINAL"
    if cls in AX_MEDIAL_CLASSES:
        return "MEDIAL"
    return None


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
line_tokens = defaultdict(list)          # (folio, line) -> [Token, ...]
line_meta = {}                           # (folio, line) -> metadata
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
print("Test 05: AX Terminal Scaffold")
print("Phase: PARAGRAPH_STATE_COLLAPSE")
print("=" * 65)
print(f"\nTotal paragraphs: {total_paragraphs}")
print(f"Paragraphs with 5+ lines: {n_big}")

# ============================================================
# PER BODY LINE: compute AX fractions by subgroup
# ============================================================
# For each big paragraph, skip line 0 (header), keep body lines (1..N-1)
# Normalize body position to [0, 1]

METRICS = ["ax_fraction", "ax_init_fraction", "ax_medial_fraction", "ax_final_fraction"]

positions = []       # normalized position within body
metric_values = {m: [] for m in METRICS}
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

        n_tokens = len(words)

        # Count AX tokens and subgroup tokens
        n_ax = 0
        n_init = 0
        n_medial = 0
        n_final = 0

        for w in words:
            role = get_role(w)
            if role == "AUXILIARY":
                n_ax += 1
            subgroup = get_ax_subgroup(w)
            if subgroup == "INIT":
                n_init += 1
            elif subgroup == "MEDIAL":
                n_medial += 1
            elif subgroup == "FINAL":
                n_final += 1

        # Normalized position: 0 = first body line, 1 = last body line
        norm_pos = idx / (n_body - 1) if n_body > 1 else 0.5

        positions.append(norm_pos)
        metric_values["ax_fraction"].append(n_ax / n_tokens)
        metric_values["ax_init_fraction"].append(n_init / n_tokens)
        metric_values["ax_medial_fraction"].append(n_medial / n_tokens)
        metric_values["ax_final_fraction"].append(n_final / n_tokens)
        line_lengths.append(n_tokens)

positions = np.array(positions)
line_lengths = np.array(line_lengths, dtype=float)
for m in METRICS:
    metric_values[m] = np.array(metric_values[m])

n_body_lines = len(positions)
print(f"Body lines analyzed: {n_body_lines}")

# ============================================================
# ANALYSIS
# ============================================================
metric_results = {}

for m in METRICS:
    vals = metric_values[m]

    # 1. Raw Spearman rho
    rho_raw, p_raw = stats.spearmanr(positions, vals)

    # 2. Partial Spearman rho controlling for line_length
    rho_partial, p_partial = partial_spearman(positions, vals, line_lengths)

    metric_results[m] = {
        "rho_raw": float(rho_raw),
        "p_raw": float(p_raw),
        "rho_partial": float(rho_partial),
        "p_partial": float(p_partial),
    }

print(f"\n--- Raw Spearman correlations ---")
for m in METRICS:
    r = metric_results[m]
    print(f"  {m:25s} vs position: rho = {r['rho_raw']:+.4f}, p = {r['p_raw']:.6f}")

print(f"\n--- Partial Spearman (controlling for line_length) ---")
for m in METRICS:
    r = metric_results[m]
    print(f"  {m:25s} vs position: rho = {r['rho_partial']:+.4f}, p = {r['p_partial']:.6f}")

# ============================================================
# QUINTILE MEANS
# ============================================================
quintile_labels = ["Q0", "Q1", "Q2", "Q3", "Q4"]
quintile_edges = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0001]

quintile_means = {m: {} for m in METRICS}

for qi in range(5):
    lo = quintile_edges[qi]
    hi = quintile_edges[qi + 1]
    mask = (positions >= lo) & (positions < hi)
    label = quintile_labels[qi]
    for m in METRICS:
        quintile_means[m][label] = float(np.mean(metric_values[m][mask])) if mask.any() else 0.0

for m in METRICS:
    print(f"\n--- Quintile means: {m} ---")
    for q in quintile_labels:
        print(f"  {q}: {quintile_means[m][q]:.6f}")

# ============================================================
# SHUFFLE TEST (1000x, seed=42)
# ============================================================
N_SHUFFLES = 1000
rng = np.random.RandomState(42)

shuffle_rhos_raw = {m: np.zeros(N_SHUFFLES) for m in METRICS}
shuffle_rhos_partial = {m: np.zeros(N_SHUFFLES) for m in METRICS}

print(f"\nRunning shuffle test ({N_SHUFFLES} iterations)...")

for i in range(N_SHUFFLES):
    perm_positions = rng.permutation(positions)

    for m in METRICS:
        vals = metric_values[m]
        # Raw rho under shuffle
        shuffle_rhos_raw[m][i], _ = stats.spearmanr(perm_positions, vals)
        # Partial rho under shuffle
        r_p, _ = partial_spearman(perm_positions, vals, line_lengths)
        shuffle_rhos_partial[m][i] = r_p

# Empirical p-values (one-tailed POSITIVE: we test for increasing AX toward paragraph end)
shuffle_p = {}
for m in METRICS:
    r = metric_results[m]
    shuffle_p[m] = {
        "raw": float(np.mean(shuffle_rhos_raw[m] >= r["rho_raw"])),
        "partial": float(np.mean(shuffle_rhos_partial[m] >= r["rho_partial"])),
    }

# Bonferroni correction: 4 sub-tests, alpha=0.01
bonferroni_alpha = 0.01 / 4  # = 0.0025

print(f"\n--- Shuffle test results (empirical p-values, one-tailed positive) ---")
for m in METRICS:
    sp = shuffle_p[m]
    print(f"  {m:25s} raw: shuffle_p = {sp['raw']:.4f}")
    print(f"  {m:25s} partial: shuffle_p = {sp['partial']:.4f}")
print(f"  Bonferroni alpha: {bonferroni_alpha}")

# ============================================================
# VERDICT
# ============================================================
# PASS: AX_FINAL shows significant positive partial rho (p < Bonferroni)
#       AND total AX shows significant positive partial rho
# PARTIAL: only one of the two significant
# FAIL: neither significant

ax_final_sig = (
    metric_results["ax_final_fraction"]["rho_partial"] > 0
    and shuffle_p["ax_final_fraction"]["partial"] < bonferroni_alpha
)
ax_total_sig = (
    metric_results["ax_fraction"]["rho_partial"] > 0
    and shuffle_p["ax_fraction"]["partial"] < bonferroni_alpha
)

if ax_final_sig and ax_total_sig:
    verdict = "PASS"
elif ax_final_sig or ax_total_sig:
    verdict = "PARTIAL"
else:
    verdict = "FAIL"

significant_metrics = []
for m in METRICS:
    if (metric_results[m]["rho_partial"] > 0
            and shuffle_p[m]["partial"] < bonferroni_alpha):
        significant_metrics.append(m)

print(f"\n{'='*65}")
print(f"VERDICT: {verdict}")
if significant_metrics:
    print(f"  Significant metrics (positive partial rho, shuffle p < {bonferroni_alpha}):")
    for m in significant_metrics:
        r = metric_results[m]
        print(f"    - {m}: rho={r['rho_partial']:+.4f}, shuffle_p={shuffle_p[m]['partial']:.4f}")
else:
    print(f"  No metric shows significant positive length-controlled rho.")
if verdict == "PARTIAL":
    which = "ax_final_fraction" if ax_final_sig else "ax_fraction"
    print(f"  Only {which} is significant; the other is not.")
print(f"{'='*65}")

# ============================================================
# OUTPUT JSON
# ============================================================
results = {
    "test": "05_ax_terminal_scaffold",
    "phase": "PARAGRAPH_STATE_COLLAPSE",
    "verdict": verdict,
    "counts": {
        "total_paragraphs": total_paragraphs,
        "big_paragraphs": n_big,
        "body_lines": n_body_lines,
    },
}

for m in METRICS:
    r = metric_results[m]
    results[m] = {
        "raw_rho": round(r["rho_raw"], 6),
        "raw_p": round(r["p_raw"], 6),
        "partial_rho": round(r["rho_partial"], 6),
        "partial_p": round(r["p_partial"], 6),
        "shuffle_p_raw": round(shuffle_p[m]["raw"], 4),
        "shuffle_p_partial": round(shuffle_p[m]["partial"], 4),
        "quintile_means": {k: round(v, 6) for k, v in quintile_means[m].items()},
    }

results["bonferroni_alpha"] = bonferroni_alpha
results["significant_metrics"] = significant_metrics
results["subgroup_classes"] = {
    "INIT": sorted(AX_INIT_CLASSES),
    "FINAL": sorted(AX_FINAL_CLASSES),
    "MEDIAL": sorted(AX_MEDIAL_CLASSES),
}

RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: {RESULTS_PATH}")
