"""
Test 01: Total Hazard Rate Flatness
Phase: RISK_PROFILE_MIGRATION

Purpose: Verify that the total hazard-involved token fraction is flat across
paragraph body lines, confirming C458 design clamp at paragraph level. The
hazard classes (7, 8, 9, 23, 30, 31) represent only 6 of 49 instruction
classes. If hazard rate is flat across body position, hazard is uniformly
distributed -- not concentrated at paragraph start or end.

Method:
  1. Load Currier B tokens. Build paragraphs via par_initial field.
  2. Keep paragraphs with 5+ lines.
  3. Exclude line 0 (header per C840). Assign each body line a quintile (0-4).
  4. For each body line: classify tokens by instruction class (from class_token_map),
     compute hazard_fraction = hazard_count / classifiable_tokens.
  5. Spearman rho of hazard_fraction vs quintile position.
  6. Partial Spearman rho controlling for line_length.
  7. Shuffle test (1000x, seed=42): permute line positions within paragraphs.
  8. Quintile means: compute mean hazard_fraction per quintile.

Verdict (inverted -- PASS means flatness):
  PASS: |partial_rho| < 0.05 AND shuffle_p > 0.10
  PARTIAL: one criterion met
  FAIL: |partial_rho| >= 0.05 AND shuffle_p < 0.01

Provenance: C458 (design clamp), C601, C541 (hazard classes)
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
RESULTS_PATH = PROJECT_ROOT / "phases/RISK_PROFILE_MIGRATION/results/01_total_hazard_rate_flatness.json"
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"

HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def assign_quintile(body_idx, n_body):
    """Assign a body line (0-indexed) to a quintile (0-4)."""
    if n_body <= 1:
        return 0
    return min(int((body_idx / (n_body - 1)) * 5), 4)


# ---------------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------------
print("Loading class_token_map...")
with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
    class_map_data = json.load(f)

token_to_class = class_map_data["token_to_class"]
# Convert string class values to int
token_to_class = {k: int(v) for k, v in token_to_class.items()}

print(f"Tokens in class map: {len(token_to_class)}")

print("Loading Currier B tokens...")
tx = Transcript()

# Build lines
lines = defaultdict(list)
for t in tx.currier_b():
    word = t.word.replace("*", "").strip()
    if not word:
        continue
    lines[(t.folio, t.line)].append(t)

# Build paragraphs using par_initial field
folio_lines = defaultdict(list)
for (f, l), toks in sorted(lines.items()):
    folio_lines[f].append((l, toks))

paragraphs = []
for f in sorted(folio_lines):
    curr_par = []
    for l, toks in folio_lines[f]:
        if toks[0].par_initial and curr_par:
            paragraphs.append(curr_par)
            curr_par = []
        curr_par.append((f, l, toks))
    if curr_par:
        paragraphs.append(curr_par)

print(f"Total paragraphs: {len(paragraphs)}")
big_paragraphs = [p for p in paragraphs if len(p) >= 5]
print(f"Paragraphs with 5+ lines: {len(big_paragraphs)}")


# ---------------------------------------------------------------------------
# COMPUTE PER-LINE FEATURES
# ---------------------------------------------------------------------------
positions = []          # normalized position [0, 1]
quintiles = []          # quintile assignment [0-4]
hazard_fractions = []   # hazard_count / classifiable tokens
hazard_counts = []      # raw hazard token count
line_lengths = []       # number of classifiable tokens per line
paragraph_ids = []      # paragraph index (for shuffle grouping)

for par_idx, par in enumerate(big_paragraphs):
    body_lines = par[1:]  # skip header (line 0, per C840)
    n_body = len(body_lines)
    if n_body < 2:
        continue

    for body_idx, (folio, line_num, toks) in enumerate(body_lines):
        # Normalized position
        norm_pos = body_idx / (n_body - 1)
        q = assign_quintile(body_idx, n_body)

        # Classify tokens on this line
        n_classifiable = 0
        n_hazard = 0
        for tok in toks:
            word = tok.word.replace("*", "").strip()
            if not word:
                continue
            cls = token_to_class.get(word, -1)
            if cls == -1:
                continue  # not classifiable
            n_classifiable += 1
            if cls in HAZARD_CLASSES:
                n_hazard += 1

        # Skip lines with no classifiable tokens
        if n_classifiable == 0:
            continue

        haz_frac = n_hazard / n_classifiable

        positions.append(norm_pos)
        quintiles.append(q)
        hazard_fractions.append(haz_frac)
        hazard_counts.append(n_hazard)
        line_lengths.append(n_classifiable)
        paragraph_ids.append(par_idx)

# Convert to numpy arrays
positions = np.array(positions)
quintiles = np.array(quintiles)
hazard_fractions = np.array(hazard_fractions)
hazard_counts_arr = np.array(hazard_counts)
line_lengths = np.array(line_lengths, dtype=float)
paragraph_ids = np.array(paragraph_ids)

n_body_lines_total = len(positions)
print(f"Total body lines analyzed: {n_body_lines_total}")
print(f"Mean hazard fraction: {np.mean(hazard_fractions):.4f}")
print(f"Mean hazard count per line: {np.mean(hazard_counts_arr):.2f}")


# ---------------------------------------------------------------------------
# RAW SPEARMAN: hazard_fraction vs normalized position
# ---------------------------------------------------------------------------
rho_raw, pval_raw = stats.spearmanr(positions, hazard_fractions)
print(f"\n--- Raw Spearman (hazard_fraction vs position) ---")
print(f"  rho = {rho_raw:+.6f}  p = {pval_raw:.2e}")


# ---------------------------------------------------------------------------
# PARTIAL SPEARMAN: controlling for line_length
# ---------------------------------------------------------------------------
# Regress out line_length from both position and hazard_fraction
slope_pos, intercept_pos, _, _, _ = stats.linregress(line_lengths, positions)
pos_residuals = positions - (slope_pos * line_lengths + intercept_pos)

slope_f, intercept_f, _, _, _ = stats.linregress(line_lengths, hazard_fractions)
feat_residuals = hazard_fractions - (slope_f * line_lengths + intercept_f)

rho_partial, pval_partial = stats.spearmanr(pos_residuals, feat_residuals)
print(f"\n--- Partial Spearman (length-controlled) ---")
print(f"  rho = {rho_partial:+.6f}  p = {pval_partial:.2e}")


# ---------------------------------------------------------------------------
# LINE LENGTH CONFOUND CHECK
# ---------------------------------------------------------------------------
rho_len_haz, pval_len_haz = stats.spearmanr(line_lengths, hazard_fractions)
print(f"\n--- Line length vs hazard_fraction confound ---")
print(f"  rho = {rho_len_haz:+.6f}  p = {pval_len_haz:.2e}")


# ---------------------------------------------------------------------------
# QUINTILE MEANS
# ---------------------------------------------------------------------------
quintile_hazfrac_means = {}
quintile_hazcount_means = {}
for q in range(5):
    mask = quintiles == q
    if np.sum(mask) > 0:
        quintile_hazfrac_means[q] = float(np.mean(hazard_fractions[mask]))
        quintile_hazcount_means[q] = float(np.mean(hazard_counts_arr[mask]))
    else:
        quintile_hazfrac_means[q] = 0.0
        quintile_hazcount_means[q] = 0.0

print(f"\n--- Quintile mean hazard_fraction ---")
for q in range(5):
    print(f"  Q{q}: hazard_frac={quintile_hazfrac_means[q]:.4f}  "
          f"hazard_count={quintile_hazcount_means[q]:.2f}")

# Spearman rho across 5 quintile means
q_positions = np.array([0, 1, 2, 3, 4], dtype=float)
q_haz_values = np.array([quintile_hazfrac_means[q] for q in range(5)])
quintile_rho, quintile_pval = stats.spearmanr(q_positions, q_haz_values)
print(f"  Quintile rho: {quintile_rho:+.4f}  p={quintile_pval:.4f}")


# ---------------------------------------------------------------------------
# SHUFFLE TEST (1000x, seed=42)
# ---------------------------------------------------------------------------
N_SHUFFLES = 1000
rng = np.random.RandomState(42)

unique_pars = np.unique(paragraph_ids)
par_indices = {pid: np.where(paragraph_ids == pid)[0] for pid in unique_pars}

shuffle_rhos_raw = []
shuffle_rhos_partial = []

print(f"\nRunning {N_SHUFFLES} shuffle iterations...")
for _ in range(N_SHUFFLES):
    # Permute line positions within each paragraph
    shuffled_positions = positions.copy()
    for pid, idxs in par_indices.items():
        perm = rng.permutation(len(idxs))
        shuffled_positions[idxs] = positions[idxs[perm]]

    # Raw rho on shuffled positions
    rho_s, _ = stats.spearmanr(shuffled_positions, hazard_fractions)
    shuffle_rhos_raw.append(rho_s)

    # Partial rho on shuffled positions (control for line_length)
    slope_pos_s, intercept_pos_s, _, _, _ = stats.linregress(
        line_lengths, shuffled_positions
    )
    pos_resid_s = shuffled_positions - (
        slope_pos_s * line_lengths + intercept_pos_s
    )
    # feat_residuals for hazard_fraction are the same (line_length -> hazard unchanged)
    # but we recompute from scratch for correctness
    slope_f_s, intercept_f_s, _, _, _ = stats.linregress(
        line_lengths, hazard_fractions
    )
    feat_resid_s = hazard_fractions - (slope_f_s * line_lengths + intercept_f_s)
    rho_p_s, _ = stats.spearmanr(pos_resid_s, feat_resid_s)
    shuffle_rhos_partial.append(rho_p_s)

shuffle_rhos_raw = np.array(shuffle_rhos_raw)
shuffle_rhos_partial = np.array(shuffle_rhos_partial)

# Empirical p-values (two-sided: |null| >= |observed|)
shuffle_p_raw = float(
    (np.sum(np.abs(shuffle_rhos_raw) >= abs(rho_raw)) + 1) / (N_SHUFFLES + 1)
)
shuffle_p_partial = float(
    (np.sum(np.abs(shuffle_rhos_partial) >= abs(rho_partial)) + 1)
    / (N_SHUFFLES + 1)
)

print(f"\n--- Shuffle test results ---")
print(f"  Raw:     observed rho={rho_raw:+.6f}  shuffle_p={shuffle_p_raw:.4f}")
print(f"  Partial: observed rho={rho_partial:+.6f}  shuffle_p={shuffle_p_partial:.4f}")
print(f"  Null raw distribution:     mean={np.mean(shuffle_rhos_raw):+.6f}  "
      f"std={np.std(shuffle_rhos_raw):.6f}")
print(f"  Null partial distribution: mean={np.mean(shuffle_rhos_partial):+.6f}  "
      f"std={np.std(shuffle_rhos_partial):.6f}")


# ---------------------------------------------------------------------------
# VERDICT (inverted: PASS means flatness)
# ---------------------------------------------------------------------------
# PASS: |partial_rho| < 0.05 AND shuffle_p > 0.10 (flat confirmed)
# PARTIAL: one criterion met
# FAIL: |partial_rho| >= 0.05 AND shuffle_p < 0.01 (significant trend)

criterion_flat_rho = abs(rho_partial) < 0.05
criterion_flat_p = shuffle_p_partial > 0.10

if criterion_flat_rho and criterion_flat_p:
    verdict = "PASS"
    verdict_detail = (
        f"Hazard rate flatness confirmed: |partial rho|={abs(rho_partial):.4f} "
        f"(< 0.05) and shuffle p={shuffle_p_partial:.4f} (> 0.10). "
        f"Hazard-involved token fraction does not vary systematically with "
        f"paragraph body position. Confirms C458 design clamp at paragraph level."
    )
elif criterion_flat_rho or criterion_flat_p:
    verdict = "PARTIAL"
    met = []
    unmet = []
    if criterion_flat_rho:
        met.append(f"|partial_rho|={abs(rho_partial):.4f} < 0.05")
    else:
        unmet.append(f"|partial_rho|={abs(rho_partial):.4f} >= 0.05")
    if criterion_flat_p:
        met.append(f"shuffle_p={shuffle_p_partial:.4f} > 0.10")
    else:
        unmet.append(f"shuffle_p={shuffle_p_partial:.4f} <= 0.10")
    verdict_detail = (
        f"Partial evidence for hazard rate flatness. "
        f"Met: {'; '.join(met)}. Unmet: {'; '.join(unmet)}."
    )
else:
    verdict = "FAIL"
    verdict_detail = (
        f"Hazard rate flatness NOT confirmed: |partial rho|={abs(rho_partial):.4f} "
        f"(>= 0.05) and shuffle p={shuffle_p_partial:.4f} (<= 0.10). "
        f"Hazard-involved token fraction shows a significant positional trend, "
        f"contradicting C458 uniform distribution expectation."
    )

sep = "=" * 60
print(f"\n{sep}")
print(f"VERDICT: {verdict}")
print(verdict_detail)
print(sep)


# ---------------------------------------------------------------------------
# SAVE RESULTS
# ---------------------------------------------------------------------------
RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

results = {
    "test": "01_total_hazard_rate_flatness",
    "phase": "RISK_PROFILE_MIGRATION",
    "verdict": verdict,
    "verdict_detail": verdict_detail,
    "counts": {
        "total_paragraphs": len(paragraphs),
        "big_paragraphs": len(big_paragraphs),
        "body_lines": int(n_body_lines_total),
        "unique_paragraphs_analyzed": int(len(unique_pars)),
        "tokens_in_class_map": len(token_to_class),
        "mean_hazard_fraction": round(float(np.mean(hazard_fractions)), 6),
        "mean_hazard_count_per_line": round(float(np.mean(hazard_counts_arr)), 4),
    },
    "raw_spearman": {
        "rho": round(float(rho_raw), 6),
        "analytic_p": float(pval_raw),
        "shuffle_p": round(float(shuffle_p_raw), 6),
    },
    "partial_spearman": {
        "rho": round(float(rho_partial), 6),
        "analytic_p": float(pval_partial),
        "shuffle_p": round(float(shuffle_p_partial), 6),
    },
    "quintile_means": {
        f"Q{q}": round(quintile_hazfrac_means[q], 6) for q in range(5)
    },
    "quintile_rho": round(float(quintile_rho), 6),
    "quintile_hazcount_means": {
        f"Q{q}": round(quintile_hazcount_means[q], 4) for q in range(5)
    },
    "shuffle_distribution": {
        "raw": {
            "mean": round(float(np.mean(shuffle_rhos_raw)), 6),
            "std": round(float(np.std(shuffle_rhos_raw)), 6),
            "observed_rho": round(float(rho_raw), 6),
        },
        "partial": {
            "mean": round(float(np.mean(shuffle_rhos_partial)), 6),
            "std": round(float(np.std(shuffle_rhos_partial)), 6),
            "observed_rho": round(float(rho_partial), 6),
        },
    },
    "line_length_confound": {
        "rho_with_hazard_fraction": round(float(rho_len_haz), 6),
        "p": float(pval_len_haz),
    },
    "hazard_classes": sorted(list(HAZARD_CLASSES)),
    "parameters": {
        "min_paragraph_lines": 5,
        "n_shuffles": N_SHUFFLES,
        "random_seed": 42,
        "pass_threshold_partial_rho": 0.05,
        "pass_threshold_shuffle_p": 0.10,
    },
}

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {RESULTS_PATH}")
