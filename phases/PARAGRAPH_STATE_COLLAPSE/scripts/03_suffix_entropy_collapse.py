"""
Test 03: Suffix Entropy Collapse
Phase: PARAGRAPH_STATE_COLLAPSE

Purpose: Test whether Shannon entropy of suffix distribution per line decreases
across paragraph body positions. C932 showed terminal suffix fraction decreases
and bare suffix fraction increases -- this formalizes whether suffix DIVERSITY shrinks.

Method:
  1. Load Currier B tokens. Build paragraphs via par_initial.
  2. Keep paragraphs with 5+ lines. Skip header.
  3. Per body line: extract suffixes, compute Shannon entropy and n_distinct_suffixes.
  4. Spearman rho vs quintile position. Partial rho controlling for line_length.
  5. Shuffle test (1000x, seed=42). Bonferroni for 2 sub-tests.

Provenance: C932 (suffix composition shift), C963 (body homogeneity)
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
RESULTS_PATH = (
    PROJECT_ROOT
    / "phases/PARAGRAPH_STATE_COLLAPSE/results/03_suffix_entropy_collapse.json"
)


# ---------------------------------------------------------------------------
# SHANNON ENTROPY
# ---------------------------------------------------------------------------
def shannon_entropy(counts):
    """Compute Shannon entropy (bits) from a Counter or dict of counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counts.values() if c > 0]
    return -sum(p * math.log2(p) for p in probs)


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
# COMPUTE PER-LINE SUFFIX METRICS
# ---------------------------------------------------------------------------
positions = []
suffix_entropies = []
n_distinct_list = []
line_lengths = []
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

        # Extract suffixes -- use 'NONE' for tokens without a suffix
        suffixes = []
        for w in words:
            m = morph.extract(w)
            suffix = m.suffix or "NONE"
            suffixes.append(suffix)

        suffix_counts = Counter(suffixes)
        suffix_entropies.append(shannon_entropy(suffix_counts))
        n_distinct_list.append(len(suffix_counts))
        line_lengths.append(n_tokens)

positions = np.array(positions)
paragraph_ids = np.array(paragraph_ids)
suffix_entropies = np.array(suffix_entropies)
n_distinct_arr = np.array(n_distinct_list, dtype=float)
line_lengths = np.array(line_lengths, dtype=float)

n_body_lines_total = len(positions)
print(f"Total body lines analyzed: {n_body_lines_total}")

# ---------------------------------------------------------------------------
# METRICS MAP
# ---------------------------------------------------------------------------
metrics = {
    "suffix_entropy": suffix_entropies,
    "n_distinct_suffixes": n_distinct_arr,
}

# ---------------------------------------------------------------------------
# RAW SPEARMAN RHO
# ---------------------------------------------------------------------------
raw_rhos = {}
raw_pvals = {}
for name, values in metrics.items():
    rho, pval = stats.spearmanr(positions, values)
    raw_rhos[name] = rho
    raw_pvals[name] = pval

print("\n--- Raw Spearman correlations ---")
for name in metrics:
    print(f"  {name:25s}: rho={raw_rhos[name]:+.4f}  p={raw_pvals[name]:.2e}")

# ---------------------------------------------------------------------------
# PARTIAL SPEARMAN RHO (controlling for line_length)
# ---------------------------------------------------------------------------
slope_pos, intercept_pos, _, _, _ = stats.linregress(line_lengths, positions)
pos_residuals = positions - (slope_pos * line_lengths + intercept_pos)

partial_rhos = {}
partial_pvals = {}
for name, values in metrics.items():
    slope_f, intercept_f, _, _, _ = stats.linregress(line_lengths, values)
    feat_residuals = values - (slope_f * line_lengths + intercept_f)
    rho, pval = stats.spearmanr(pos_residuals, feat_residuals)
    partial_rhos[name] = rho
    partial_pvals[name] = pval

print("\n--- Length-controlled partial Spearman ---")
for name in metrics:
    print(f"  {name:25s}: rho={partial_rhos[name]:+.4f}  p={partial_pvals[name]:.2e}")

# ---------------------------------------------------------------------------
# SHUFFLE TEST (1000x)
# ---------------------------------------------------------------------------
N_SHUFFLES = 1000
rng = np.random.RandomState(42)

unique_pars = np.unique(paragraph_ids)
par_indices = {pid: np.where(paragraph_ids == pid)[0] for pid in unique_pars}

shuffle_rhos = {"suffix_entropy": [], "n_distinct_suffixes": []}
shuffle_partial_rhos = {"suffix_entropy": [], "n_distinct_suffixes": []}

for _ in range(N_SHUFFLES):
    # Shuffle body line order within each paragraph
    shuffled_positions = positions.copy()
    for pid, idxs in par_indices.items():
        perm = rng.permutation(len(idxs))
        shuffled_positions[idxs] = positions[idxs[perm]]

    # Raw rhos
    for name, values in metrics.items():
        rho_s, _ = stats.spearmanr(shuffled_positions, values)
        shuffle_rhos[name].append(rho_s)

    # Partial rhos
    slope_pos_s, intercept_pos_s, _, _, _ = stats.linregress(
        line_lengths, shuffled_positions
    )
    pos_resid_s = shuffled_positions - (
        slope_pos_s * line_lengths + intercept_pos_s
    )
    for name, values in metrics.items():
        slope_f, intercept_f, _, _, _ = stats.linregress(line_lengths, values)
        feat_resid = values - (slope_f * line_lengths + intercept_f)
        rho_s, _ = stats.spearmanr(pos_resid_s, feat_resid)
        shuffle_partial_rhos[name].append(rho_s)

# Empirical p-values (two-sided)
shuffle_pvals_raw = {}
for name in metrics:
    observed = abs(raw_rhos[name])
    null_dist = np.array(shuffle_rhos[name])
    p = (np.sum(np.abs(null_dist) >= observed) + 1) / (N_SHUFFLES + 1)
    shuffle_pvals_raw[name] = p

shuffle_pvals_partial = {}
for name in metrics:
    observed = abs(partial_rhos[name])
    null_dist = np.array(shuffle_partial_rhos[name])
    p = (np.sum(np.abs(null_dist) >= observed) + 1) / (N_SHUFFLES + 1)
    shuffle_pvals_partial[name] = p

# ---------------------------------------------------------------------------
# BONFERRONI CORRECTION (2 sub-tests)
# ---------------------------------------------------------------------------
n_tests = 2
alpha = 0.01
bonferroni_alpha = alpha / n_tests  # 0.005

print(
    f"\n--- Shuffle p-values (raw) | "
    f"Bonferroni threshold={bonferroni_alpha:.4f} ---"
)
for name in metrics:
    p = shuffle_pvals_raw[name]
    sig = p < bonferroni_alpha
    marker = " ***" if sig else ""
    print(f"  {name:25s}: p={p:.4f}{marker}")

print(
    f"\n--- Shuffle p-values (length-controlled) | "
    f"Bonferroni threshold={bonferroni_alpha:.4f} ---"
)
for name in metrics:
    p = shuffle_pvals_partial[name]
    sig = p < bonferroni_alpha
    marker = " ***" if sig else ""
    print(f"  {name:25s}: p={p:.4f}{marker}")

# Significance: use partial (length-controlled) rho for verdict
significant_metrics = []
for name in metrics:
    if shuffle_pvals_partial[name] < bonferroni_alpha and partial_rhos[name] < 0:
        significant_metrics.append(name)

n_sig = len(significant_metrics)

# ---------------------------------------------------------------------------
# QUINTILE MEANS
# ---------------------------------------------------------------------------
quintile_labels = ["Q0", "Q1", "Q2", "Q3", "Q4"]
quintile_bounds = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0001]

quintile_means = {}
for name, values in metrics.items():
    qmeans = {}
    for qi in range(5):
        lo = quintile_bounds[qi]
        hi = quintile_bounds[qi + 1]
        mask = (positions >= lo) & (positions < hi)
        if np.any(mask):
            qmeans[quintile_labels[qi]] = round(float(np.mean(values[mask])), 4)
        else:
            qmeans[quintile_labels[qi]] = None
    quintile_means[name] = qmeans

print("\n--- Quintile means ---")
for name in metrics:
    print(f"  {name}:")
    for ql in quintile_labels:
        val = quintile_means[name][ql]
        print(f"    {ql}: {val}")

# ---------------------------------------------------------------------------
# VERDICT
# ---------------------------------------------------------------------------
if n_sig >= 1:
    verdict = "PASS"
    verdict_detail = (
        f"{n_sig} metric(s) show significant negative length-controlled "
        f"rho (shuffle p < {bonferroni_alpha}): suffix diversity collapses "
        f"across paragraph body."
    )
else:
    verdict = "FAIL"
    verdict_detail = (
        f"Neither metric shows significant negative length-controlled rho "
        f"(shuffle p < {bonferroni_alpha}): no suffix entropy collapse."
    )

sep = "=" * 60
print(f"\n{sep}")
print(f"VERDICT: {verdict}")
print(f"Significant metrics ({n_sig}): {significant_metrics}")
print(verdict_detail)
print(sep)

# ---------------------------------------------------------------------------
# SAVE RESULTS
# ---------------------------------------------------------------------------
results = {
    "test": "03_suffix_entropy_collapse",
    "phase": "PARAGRAPH_STATE_COLLAPSE",
    "verdict": verdict,
    "counts": {
        "total_paragraphs": len(paragraphs),
        "big_paragraphs": len(big_paragraphs),
        "body_lines": int(n_body_lines_total),
    },
    "suffix_entropy": {
        "raw_rho": round(float(raw_rhos["suffix_entropy"]), 6),
        "partial_rho": round(float(partial_rhos["suffix_entropy"]), 6),
        "shuffle_p_raw": round(float(shuffle_pvals_raw["suffix_entropy"]), 6),
        "shuffle_p_partial": round(
            float(shuffle_pvals_partial["suffix_entropy"]), 6
        ),
        "quintile_means": quintile_means["suffix_entropy"],
    },
    "n_distinct_suffixes": {
        "raw_rho": round(float(raw_rhos["n_distinct_suffixes"]), 6),
        "partial_rho": round(float(partial_rhos["n_distinct_suffixes"]), 6),
        "shuffle_p_raw": round(
            float(shuffle_pvals_raw["n_distinct_suffixes"]), 6
        ),
        "shuffle_p_partial": round(
            float(shuffle_pvals_partial["n_distinct_suffixes"]), 6
        ),
        "quintile_means": quintile_means["n_distinct_suffixes"],
    },
    "bonferroni_alpha": bonferroni_alpha,
    "significant_metrics": significant_metrics,
}

RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {RESULTS_PATH}")
