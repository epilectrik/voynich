"""
Test 08: Paragraph-Internal Line Progression
Phase: LINE_CONTROL_BLOCK_GRAMMAR

Purpose: Test whether body lines within paragraphs show systematic progression
in compositional features as a function of position. If lines are control blocks
in a program, we expect progressive shifts in operator composition, complexity,
or prefix usage across the paragraph body.

Method:
  1. Load all Currier B tokens. Build paragraphs using par_initial field.
  2. Keep paragraphs with 5+ lines.
  3. Exclude line 1 of each paragraph (header per C840). Assign each body
     line a normalized position: (line_index - 1) / (n_body_lines - 1).
  4. Compute 7 features per line: EN/FL/CC fractions, mean MIDDLE length,
     line length, TTR, qo-prefix fraction.
  5. Spearman rho between normalized position and each feature.
  6. Partial Spearman rho controlling for line_length (via residuals).
  7. Shuffle test (1000x, seed=42): destroy progression within paragraphs.
  8. Bonferroni correction for 7 features. Pass if 3+ significant (p<0.01).

Provenance: C840 (header line), C813 (line structure), C807/C810
"""

import sys
import json
import math
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript, Morphology


# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path("C:/git/voynich").resolve()
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
RESULTS_PATH = PROJECT_ROOT / "phases/LINE_CONTROL_BLOCK_GRAMMAR/results/08_paragraph_line_progression.json"

# ---------------------------------------------------------------------------
# LOAD CLASS MAP
# ---------------------------------------------------------------------------
with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
    class_data = json.load(f)

token_to_class = {k: int(v) for k, v in class_data["token_to_class"].items()}
class_to_role = {int(k): v for k, v in class_data["class_to_role"].items()}


def get_role(word):
    """Map a word to its role via class assignment."""
    cls = token_to_class.get(word, -1)
    return class_to_role.get(cls, "UNKNOWN")


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
    lines[(t.folio, t.line)].append(t)

# ---------------------------------------------------------------------------
# BUILD PARAGRAPHS
# ---------------------------------------------------------------------------
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
# COMPUTE LINE FEATURES
# ---------------------------------------------------------------------------
feature_names = [
    "EN_fraction", "FL_fraction", "CC_fraction",
    "mean_middle_length", "line_length", "TTR", "qo_prefix_fraction"
]

length_controlled_features = [
    "EN_fraction", "FL_fraction", "CC_fraction", "qo_prefix_fraction"
]

positions = []
features_dict = {fn: [] for fn in feature_names}
paragraph_ids = []

for par_idx, par in enumerate(big_paragraphs):
    body_lines = par[1:]  # skip header (line 1)
    n_body = len(body_lines)
    if n_body < 2:
        continue

    for body_idx, (folio, line_num, toks) in enumerate(body_lines):
        norm_pos = body_idx / (n_body - 1)
        positions.append(norm_pos)
        paragraph_ids.append(par_idx)

        words = [t.word.replace("*", "").strip() for t in toks]
        words = [w for w in words if w]
        n_tokens = len(words)

        # Role fractions
        roles = [get_role(w) for w in words]
        en_count = sum(1 for r in roles if r == "ENERGY_OPERATOR")
        fl_count = sum(1 for r in roles if r == "FLOW_OPERATOR")
        cc_count = sum(1 for r in roles if r == "CORE_CONTROL")

        features_dict["EN_fraction"].append(
            en_count / n_tokens if n_tokens > 0 else 0.0
        )
        features_dict["FL_fraction"].append(
            fl_count / n_tokens if n_tokens > 0 else 0.0
        )
        features_dict["CC_fraction"].append(
            cc_count / n_tokens if n_tokens > 0 else 0.0
        )

        # Mean MIDDLE length
        middle_lengths = []
        for w in words:
            m = morph.extract(w)
            if m.middle:
                middle_lengths.append(len(m.middle))
        mean_ml = float(np.mean(middle_lengths)) if middle_lengths else 0.0
        features_dict["mean_middle_length"].append(mean_ml)

        # Line length
        features_dict["line_length"].append(n_tokens)

        # TTR (type-token ratio)
        unique = len(set(words))
        features_dict["TTR"].append(
            unique / n_tokens if n_tokens > 0 else 0.0
        )

        # qo-prefix fraction
        qo_count = 0
        for w in words:
            m = morph.extract(w)
            if m.prefix and m.prefix.startswith("qo"):
                qo_count += 1
        features_dict["qo_prefix_fraction"].append(
            qo_count / n_tokens if n_tokens > 0 else 0.0
        )

positions = np.array(positions)
paragraph_ids = np.array(paragraph_ids)
for fn in feature_names:
    features_dict[fn] = np.array(features_dict[fn])

n_body_lines_total = len(positions)
print(f"Total body lines analyzed: {n_body_lines_total}")

# ---------------------------------------------------------------------------
# RAW SPEARMAN RHO
# ---------------------------------------------------------------------------
raw_rhos = {}
raw_pvals = {}
for fn in feature_names:
    rho, pval = stats.spearmanr(positions, features_dict[fn])
    raw_rhos[fn] = rho
    raw_pvals[fn] = pval

print("\n--- Raw Spearman correlations ---")
for fn in feature_names:
    print(f"  {fn:25s}: rho={raw_rhos[fn]:+.4f}  p={raw_pvals[fn]:.2e}")

# ---------------------------------------------------------------------------
# PARTIAL SPEARMAN RHO (controlling for line_length)
# ---------------------------------------------------------------------------
line_lengths = features_dict["line_length"]

slope_pos, intercept_pos, _, _, _ = stats.linregress(line_lengths, positions)
pos_residuals = positions - (slope_pos * line_lengths + intercept_pos)

partial_rhos = {}
partial_pvals = {}
for fn in length_controlled_features:
    feat = features_dict[fn]
    slope_f, intercept_f, _, _, _ = stats.linregress(line_lengths, feat)
    feat_residuals = feat - (slope_f * line_lengths + intercept_f)
    rho, pval = stats.spearmanr(pos_residuals, feat_residuals)
    partial_rhos[fn] = rho
    partial_pvals[fn] = pval

print("\n--- Length-controlled partial Spearman ---")
for fn in length_controlled_features:
    print(f"  {fn:25s}: rho={partial_rhos[fn]:+.4f}  p={partial_pvals[fn]:.2e}")

# ---------------------------------------------------------------------------
# SHUFFLE TEST (1000x)
# ---------------------------------------------------------------------------
N_SHUFFLES = 1000
rng = np.random.RandomState(42)

unique_pars = np.unique(paragraph_ids)
par_indices = {pid: np.where(paragraph_ids == pid)[0] for pid in unique_pars}

shuffle_rhos = {fn: [] for fn in feature_names}
shuffle_partial_rhos = {fn: [] for fn in length_controlled_features}

for shuffle_i in range(N_SHUFFLES):
    # Shuffle body line order within each paragraph
    shuffled_positions = positions.copy()
    for pid, idxs in par_indices.items():
        perm = rng.permutation(len(idxs))
        shuffled_positions[idxs] = positions[idxs[perm]]

    # Raw rhos for all features
    for fn in feature_names:
        rho_s, _ = stats.spearmanr(shuffled_positions, features_dict[fn])
        shuffle_rhos[fn].append(rho_s)

    # Partial rhos for length-controlled features
    slope_pos_s, intercept_pos_s, _, _, _ = stats.linregress(
        line_lengths, shuffled_positions
    )
    pos_resid_s = shuffled_positions - (
        slope_pos_s * line_lengths + intercept_pos_s
    )
    for fn in length_controlled_features:
        feat = features_dict[fn]
        slope_f, intercept_f, _, _, _ = stats.linregress(line_lengths, feat)
        feat_resid = feat - (slope_f * line_lengths + intercept_f)
        rho_s, _ = stats.spearmanr(pos_resid_s, feat_resid)
        shuffle_partial_rhos[fn].append(rho_s)

# Empirical p-values (two-sided)
shuffle_pvals_raw = {}
for fn in feature_names:
    observed = abs(raw_rhos[fn])
    null_dist = np.array(shuffle_rhos[fn])
    p = (np.sum(np.abs(null_dist) >= observed) + 1) / (N_SHUFFLES + 1)
    shuffle_pvals_raw[fn] = p

shuffle_pvals_partial = {}
for fn in length_controlled_features:
    observed = abs(partial_rhos[fn])
    null_dist = np.array(shuffle_partial_rhos[fn])
    p = (np.sum(np.abs(null_dist) >= observed) + 1) / (N_SHUFFLES + 1)
    shuffle_pvals_partial[fn] = p

# ---------------------------------------------------------------------------
# BONFERRONI CORRECTION
# ---------------------------------------------------------------------------
n_tests = len(feature_names)  # 7
alpha = 0.01
bonferroni_alpha = alpha / n_tests

print(
    f"\n--- Shuffle p-values (raw) | "
    f"Bonferroni threshold={bonferroni_alpha:.4f} ---"
)
for fn in feature_names:
    p = shuffle_pvals_raw[fn]
    sig = p < bonferroni_alpha
    marker = " ***" if sig else ""
    print(f"  {fn:25s}: p={p:.4f}{marker}")

print(
    f"\n--- Shuffle p-values (length-controlled) | "
    f"Bonferroni threshold={bonferroni_alpha:.4f} ---"
)
for fn in length_controlled_features:
    p = shuffle_pvals_partial[fn]
    sig = p < bonferroni_alpha
    marker = " ***" if sig else ""
    print(f"  {fn:25s}: p={p:.4f}{marker}")

# Final significance: for fraction features use partial, for others use raw
sig_features = []
for fn in feature_names:
    if fn in length_controlled_features:
        if shuffle_pvals_partial[fn] < bonferroni_alpha:
            sig_features.append(fn)
    else:
        if shuffle_pvals_raw[fn] < bonferroni_alpha:
            sig_features.append(fn)

n_sig = len(sig_features)

# ---------------------------------------------------------------------------
# VERDICT
# ---------------------------------------------------------------------------
if n_sig >= 3:
    verdict = "PASS"
    verdict_detail = (
        f"{n_sig} features show significant progression after Bonferroni "
        f"correction (threshold p<{bonferroni_alpha:.4f}): "
        f"body lines are progressive."
    )
else:
    verdict = "FAIL"
    verdict_detail = (
        f"Only {n_sig} feature(s) significant after Bonferroni correction "
        f"(threshold p<{bonferroni_alpha:.4f}): body lines are homogeneous."
    )

sep = "=" * 60
print(f"\n{sep}")
print(f"VERDICT: {verdict}")
print(f"Significant features ({n_sig}): {sig_features}")
print(verdict_detail)
print(sep)

# ---------------------------------------------------------------------------
# SAVE RESULTS
# ---------------------------------------------------------------------------
results = {
    "test": "08_paragraph_line_progression",
    "phase": "LINE_CONTROL_BLOCK_GRAMMAR",
    "verdict": verdict,
    "verdict_detail": verdict_detail,
    "parameters": {
        "min_paragraph_lines": 5,
        "n_shuffles": N_SHUFFLES,
        "random_seed": 42,
        "alpha": alpha,
        "bonferroni_alpha": round(bonferroni_alpha, 6),
        "n_tests": n_tests,
    },
    "counts": {
        "total_paragraphs": len(paragraphs),
        "paragraphs_5plus_lines": len(big_paragraphs),
        "total_body_lines": int(n_body_lines_total),
        "unique_paragraphs_analyzed": int(len(unique_pars)),
    },
    "raw_spearman": {
        fn: {
            "rho": round(float(raw_rhos[fn]), 6),
            "analytic_p": float(raw_pvals[fn]),
            "shuffle_p": round(float(shuffle_pvals_raw[fn]), 6),
            "significant_bonferroni": bool(
                shuffle_pvals_raw[fn] < bonferroni_alpha
            ),
        }
        for fn in feature_names
    },
    "length_controlled_partial_spearman": {
        fn: {
            "partial_rho": round(float(partial_rhos[fn]), 6),
            "partial_analytic_p": float(partial_pvals[fn]),
            "shuffle_p": round(float(shuffle_pvals_partial[fn]), 6),
            "significant_bonferroni": bool(
                shuffle_pvals_partial[fn] < bonferroni_alpha
            ),
        }
        for fn in length_controlled_features
    },
    "significant_features_after_length_control": sig_features,
    "n_significant": n_sig,
    "shuffle_distributions": {
        fn: {
            "mean": round(float(np.mean(shuffle_rhos[fn])), 6),
            "std": round(float(np.std(shuffle_rhos[fn])), 6),
            "observed_rho": round(float(raw_rhos[fn]), 6),
        }
        for fn in feature_names
    },
}

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {RESULTS_PATH}")
