"""
Test 03: Risk Type Migration
Phase: RISK_PROFILE_MIGRATION

Purpose: Maps from hazard sub-groups to failure class exposure and tests whether
the dominant failure class shifts through body lines. Each hazard class
participates in specific failure types (from C541, C109). We test whether
the per-line failure class profile migrates systematically with position.

Method:
  1. Load Currier B tokens. Build paragraphs via par_initial field.
  2. Keep paragraphs with 5+ lines.
  3. Exclude line 1 (header per C840). Assign each body line a quintile (0-4).
  4. For each body line: look up hazard tokens, distribute weight across failure types.
     - Class -> failure types (uniform: weight = 1/N per failure type)
     - Normalize to get per-line failure class fractions (sum to 1.0).
  5. Exclude lines with 0 hazard tokens.
  6. For each failure class fraction:
     - Partial Spearman rho vs position, controlling for line_length.
     - Quintile means.
     - 1000-shuffle test (seed=42).
     - Bonferroni alpha = 0.01 / 4 = 0.0025.
  7. Verdict:
     - PASS: 2+ failure classes significant (shuffle_p < 0.0025) with complementary directions
     - PARTIAL: 1 failure class significant
     - FAIL: no failure class shifts

Provenance: C541 (hazard topology), C109 (forbidden transitions)
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
RESULTS_PATH = PROJECT_ROOT / "phases/RISK_PROFILE_MIGRATION/results/03_risk_type_migration.json"
CLASS_TOKEN_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"


# ---------------------------------------------------------------------------
# CLASS -> FAILURE TYPE MAPPING (from C541, C109)
# ---------------------------------------------------------------------------
# Each hazard class participates in specific failure types.
# Uniform weighting: each class contributes 1.0 to each of its failure types.
CLASS_FAILURE_TYPES = {
    7:  {'PHASE_ORDERING', 'RATE_MISMATCH'},
    8:  {'COMPOSITION_JUMP', 'PHASE_ORDERING', 'CONTAINMENT_TIMING'},
    9:  {'PHASE_ORDERING', 'COMPOSITION_JUMP', 'CONTAINMENT_TIMING'},
    23: {'PHASE_ORDERING', 'CONTAINMENT_TIMING'},
    30: {'CONTAINMENT_TIMING', 'RATE_MISMATCH'},
    31: {'PHASE_ORDERING'},  # 6 instances, all PHASE_ORDERING
}
# ENERGY_OVERSHOOT has 1 forbidden transition but no clear class assignment --
# treat as absent from per-token analysis
ALL_FAILURE_TYPES = ['PHASE_ORDERING', 'COMPOSITION_JUMP', 'CONTAINMENT_TIMING', 'RATE_MISMATCH']

HAZARD_CLASSES = set(CLASS_FAILURE_TYPES.keys())

# Bonferroni corrected alpha
BONFERRONI_ALPHA = 0.01 / len(ALL_FAILURE_TYPES)  # 0.0025


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
with open(CLASS_TOKEN_MAP_PATH, "r", encoding="utf-8") as f:
    class_token_map = json.load(f)

# Build word -> class lookup (only hazard classes)
token_to_class = class_token_map["token_to_class"]
word_to_hazard_class = {}
for word, cls in token_to_class.items():
    if cls in HAZARD_CLASSES:
        word_to_hazard_class[word] = cls

print(f"Hazard vocabulary size: {len(word_to_hazard_class)} tokens across classes {sorted(HAZARD_CLASSES)}")

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
# COMPUTE PER-LINE FAILURE TYPE FRACTIONS
# ---------------------------------------------------------------------------
positions = []          # normalized position [0, 1]
quintiles = []          # quintile assignment [0-4]
failure_fractions = []  # list of dicts {failure_type: fraction}
line_lengths = []       # number of tokens per line
paragraph_ids = []      # paragraph index (for shuffle grouping)
hazard_counts = []      # number of hazard tokens per line

for par_idx, par in enumerate(big_paragraphs):
    body_lines = par[1:]  # skip header (line 1, per C840)
    n_body = len(body_lines)
    if n_body < 2:
        continue

    for body_idx, (folio, line_num, toks) in enumerate(body_lines):
        # Normalized position
        norm_pos = body_idx / (n_body - 1)
        q = assign_quintile(body_idx, n_body)

        # Count tokens and accumulate failure type weights
        n_tokens = 0
        ft_weights = {ft: 0.0 for ft in ALL_FAILURE_TYPES}
        n_hazard = 0

        for tok in toks:
            word = tok.word.replace("*", "").strip()
            if not word:
                continue
            n_tokens += 1

            cls = word_to_hazard_class.get(word)
            if cls is not None:
                n_hazard += 1
                ft_set = CLASS_FAILURE_TYPES[cls]
                w = 1.0 / len(ft_set)
                for ft in ft_set:
                    ft_weights[ft] += w

        # Skip lines with no hazard tokens
        if n_hazard == 0:
            continue

        # Normalize to fractions (sum to 1.0)
        total_weight = sum(ft_weights.values())
        if total_weight > 0:
            ft_fracs = {ft: ft_weights[ft] / total_weight for ft in ALL_FAILURE_TYPES}
        else:
            continue

        positions.append(norm_pos)
        quintiles.append(q)
        failure_fractions.append(ft_fracs)
        line_lengths.append(n_tokens)
        paragraph_ids.append(par_idx)
        hazard_counts.append(n_hazard)

# Convert to numpy arrays
positions = np.array(positions)
quintiles = np.array(quintiles)
line_lengths = np.array(line_lengths, dtype=float)
paragraph_ids = np.array(paragraph_ids)
hazard_counts = np.array(hazard_counts)

# Build per-failure-type arrays
ft_arrays = {}
for ft in ALL_FAILURE_TYPES:
    ft_arrays[ft] = np.array([ff[ft] for ff in failure_fractions])

n_body_lines_total = len(positions)
print(f"Total body lines with hazard tokens: {n_body_lines_total}")
print(f"Mean hazard tokens per line: {np.mean(hazard_counts):.2f}")


# ---------------------------------------------------------------------------
# PER-FAILURE-TYPE ANALYSIS
# ---------------------------------------------------------------------------
unique_pars = np.unique(paragraph_ids)
par_indices = {pid: np.where(paragraph_ids == pid)[0] for pid in unique_pars}

N_SHUFFLES = 1000
rng = np.random.RandomState(42)

ft_results = {}

for ft in ALL_FAILURE_TYPES:
    ft_vals = ft_arrays[ft]
    print(f"\n{'='*60}")
    print(f"Failure type: {ft}")
    print(f"{'='*60}")

    # --- Raw Spearman ---
    rho_raw, pval_raw = stats.spearmanr(positions, ft_vals)
    print(f"  Raw Spearman: rho={rho_raw:+.6f}  p={pval_raw:.2e}")

    # --- Partial Spearman: controlling for line_length ---
    slope_pos, intercept_pos, _, _, _ = stats.linregress(line_lengths, positions)
    pos_residuals = positions - (slope_pos * line_lengths + intercept_pos)

    slope_f, intercept_f, _, _, _ = stats.linregress(line_lengths, ft_vals)
    feat_residuals = ft_vals - (slope_f * line_lengths + intercept_f)

    rho_partial, pval_partial = stats.spearmanr(pos_residuals, feat_residuals)
    print(f"  Partial Spearman (length-controlled): rho={rho_partial:+.6f}  p={pval_partial:.2e}")

    # --- Quintile means ---
    quintile_means = {}
    for q_val in range(5):
        mask = quintiles == q_val
        if np.sum(mask) > 0:
            quintile_means[q_val] = float(np.mean(ft_vals[mask]))
        else:
            quintile_means[q_val] = 0.0

    print(f"  Quintile means: " + "  ".join(
        f"Q{q_val}={quintile_means[q_val]:.4f}" for q_val in range(5)
    ))

    q_positions_arr = np.array([0, 1, 2, 3, 4], dtype=float)
    q_values_arr = np.array([quintile_means[q_val] for q_val in range(5)])
    quintile_rho, quintile_pval = stats.spearmanr(q_positions_arr, q_values_arr)
    print(f"  Quintile rho: {quintile_rho:+.4f}  p={quintile_pval:.4f}")

    # --- Shuffle test (1000x, seed=42 shared RNG) ---
    shuffle_rhos_partial = []
    for _ in range(N_SHUFFLES):
        shuffled_positions = positions.copy()
        for pid, idxs in par_indices.items():
            perm = rng.permutation(len(idxs))
            shuffled_positions[idxs] = positions[idxs[perm]]

        # Partial rho on shuffled positions
        slope_pos_s, intercept_pos_s, _, _, _ = stats.linregress(
            line_lengths, shuffled_positions
        )
        pos_resid_s = shuffled_positions - (
            slope_pos_s * line_lengths + intercept_pos_s
        )
        rho_p_s, _ = stats.spearmanr(pos_resid_s, feat_residuals)
        shuffle_rhos_partial.append(rho_p_s)

    shuffle_rhos_partial = np.array(shuffle_rhos_partial)

    # Empirical p-value (two-sided)
    shuffle_p_partial = float(
        (np.sum(np.abs(shuffle_rhos_partial) >= abs(rho_partial)) + 1)
        / (N_SHUFFLES + 1)
    )

    significant = shuffle_p_partial < BONFERRONI_ALPHA
    print(f"  Shuffle p (partial): {shuffle_p_partial:.4f}  "
          f"(threshold={BONFERRONI_ALPHA:.4f})  "
          f"{'SIGNIFICANT' if significant else 'not significant'}")
    print(f"  Null distribution: mean={np.mean(shuffle_rhos_partial):+.6f}  "
          f"std={np.std(shuffle_rhos_partial):.6f}")

    ft_results[ft] = {
        "raw_spearman": {
            "rho": round(float(rho_raw), 6),
            "analytic_p": float(pval_raw),
        },
        "partial_spearman": {
            "rho": round(float(rho_partial), 6),
            "analytic_p": float(pval_partial),
            "shuffle_p": round(float(shuffle_p_partial), 6),
        },
        "quintile_means": {
            f"Q{q_val}": round(quintile_means[q_val], 6) for q_val in range(5)
        },
        "quintile_rho": round(float(quintile_rho), 6),
        "significant": significant,
        "direction": "positive" if rho_partial > 0 else "negative",
        "shuffle_distribution": {
            "mean": round(float(np.mean(shuffle_rhos_partial)), 6),
            "std": round(float(np.std(shuffle_rhos_partial)), 6),
            "observed_rho": round(float(rho_partial), 6),
        },
    }


# ---------------------------------------------------------------------------
# VERDICT
# ---------------------------------------------------------------------------
sig_types = [ft for ft in ALL_FAILURE_TYPES if ft_results[ft]["significant"]]
sig_directions = [ft_results[ft]["direction"] for ft in sig_types]

n_significant = len(sig_types)
has_complementary = len(set(sig_directions)) > 1 if n_significant >= 2 else False

if n_significant >= 2 and has_complementary:
    verdict = "PASS"
    dir_parts = [ft + "=" + ft_results[ft]["direction"] for ft in sig_types]
    verdict_detail = (
        f"Risk type migration confirmed: {n_significant} failure classes significant "
        f"(Bonferroni alpha={BONFERRONI_ALPHA:.4f}) with complementary directions. "
        f"Significant types: {', '.join(sig_types)}. "
        f"Directions: {', '.join(dir_parts)}. "
        f"Failure class exposure profile shifts systematically through body lines."
    )
elif n_significant >= 1:
    verdict = "PARTIAL"
    verdict_detail = (
        f"Partial risk type migration: {n_significant} failure class(es) significant "
        f"(Bonferroni alpha={BONFERRONI_ALPHA:.4f}). "
        f"Significant: {', '.join(sig_types) if sig_types else 'none'}. "
        f"{'Complementary directions present.' if has_complementary else 'No complementary directions (or only 1 significant).'}"
    )
else:
    verdict = "FAIL"
    verdict_detail = (
        f"No failure class shifts detected: 0 of {len(ALL_FAILURE_TYPES)} failure types "
        f"reached significance (Bonferroni alpha={BONFERRONI_ALPHA:.4f}). "
        f"Failure class exposure profile does not shift systematically through body lines."
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
    "test": "03_risk_type_migration",
    "phase": "RISK_PROFILE_MIGRATION",
    "verdict": verdict,
    "verdict_detail": verdict_detail,
    "counts": {
        "total_paragraphs": len(paragraphs),
        "big_paragraphs": len(big_paragraphs),
        "body_lines_with_hazard_tokens": int(n_body_lines_total),
        "unique_paragraphs_analyzed": int(len(unique_pars)),
        "mean_hazard_tokens_per_line": round(float(np.mean(hazard_counts)), 4),
    },
    "failure_type_results": ft_results,
    "significant_count": n_significant,
    "significant_types": sig_types,
    "has_complementary_directions": has_complementary,
    "class_failure_type_mapping": {
        str(cls): sorted(list(fts)) for cls, fts in CLASS_FAILURE_TYPES.items()
    },
    "parameters": {
        "min_paragraph_lines": 5,
        "n_shuffles": N_SHUFFLES,
        "random_seed": 42,
        "bonferroni_alpha": BONFERRONI_ALPHA,
        "base_alpha": 0.01,
        "n_failure_types": len(ALL_FAILURE_TYPES),
        "hazard_classes": sorted(list(HAZARD_CLASSES)),
    },
}

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {RESULTS_PATH}")
