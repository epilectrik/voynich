"""
Test 01: Vocabulary Entropy Collapse
Phase: PARAGRAPH_STATE_COLLAPSE

Purpose: Test whether Shannon entropy of MIDDLE vocabulary per line decreases
as paragraph body lines progress from start to finish. This is distinct from
C932 (which measures rarity fraction shift) -- here we measure the DIVERSITY
of MIDDLEs per line.

Method:
  1. Load Currier B tokens. Build paragraphs via par_initial field.
  2. Keep paragraphs with 5+ lines.
  3. Exclude line 1 (header per C840). Assign each body line a quintile (0-4).
  4. For each body line: extract MIDDLEs, compute Shannon entropy of MIDDLE dist.
  5. Spearman rho of entropy vs quintile position.
  6. Partial Spearman rho controlling for line_length.
  7. Shuffle test (1000x, seed=42): permute line positions within paragraphs.
  8. Quintile means: compute mean entropy per quintile, test monotonic trend.

Provenance: C932 (vocabulary rarity gradient), C963 (body homogeneity),
            C677 (line shortening)
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
RESULTS_PATH = PROJECT_ROOT / "phases/PARAGRAPH_STATE_COLLAPSE/results/01_vocabulary_entropy_collapse.json"


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def shannon_entropy(counter):
    """Compute Shannon entropy (bits) from a Counter of counts."""
    total = sum(counter.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counter.values() if c > 0]
    return -sum(p * math.log2(p) for p in probs)


def assign_quintile(body_idx, n_body):
    """Assign a body line (0-indexed) to a quintile (0-4)."""
    if n_body <= 1:
        return 0
    return min(int((body_idx / (n_body - 1)) * 5), 4)


# ---------------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------------
print("Loading Currier B tokens...")
tx = Transcript()
morph = Morphology()

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
entropies = []          # Shannon entropy of MIDDLE distribution
n_unique_middles = []   # distinct MIDDLE count per line
line_lengths = []       # number of tokens per line
paragraph_ids = []      # paragraph index (for shuffle grouping)

for par_idx, par in enumerate(big_paragraphs):
    body_lines = par[1:]  # skip header (line 1, per C840)
    n_body = len(body_lines)
    if n_body < 2:
        continue

    for body_idx, (folio, line_num, toks) in enumerate(body_lines):
        # Normalized position
        norm_pos = body_idx / (n_body - 1)
        q = assign_quintile(body_idx, n_body)

        # Extract MIDDLEs for all tokens on this line
        middle_counter = Counter()
        for tok in toks:
            word = tok.word.replace("*", "").strip()
            if not word:
                continue
            m = morph.extract(word)
            if m.middle:
                middle_counter[m.middle] += 1

        # Shannon entropy of MIDDLE distribution
        h = shannon_entropy(middle_counter)
        n_unique = len(middle_counter)
        n_tokens = sum(middle_counter.values())

        # Skip lines with no extractable MIDDLEs
        if n_tokens == 0:
            continue

        positions.append(norm_pos)
        quintiles.append(q)
        entropies.append(h)
        n_unique_middles.append(n_unique)
        line_lengths.append(n_tokens)
        paragraph_ids.append(par_idx)

# Convert to numpy arrays
positions = np.array(positions)
quintiles = np.array(quintiles)
entropies = np.array(entropies)
n_unique_arr = np.array(n_unique_middles)
line_lengths = np.array(line_lengths, dtype=float)
paragraph_ids = np.array(paragraph_ids)

n_body_lines_total = len(positions)
print(f"Total body lines analyzed: {n_body_lines_total}")


# ---------------------------------------------------------------------------
# RAW SPEARMAN: entropy vs normalized position
# ---------------------------------------------------------------------------
rho_raw, pval_raw = stats.spearmanr(positions, entropies)
print(f"\n--- Raw Spearman (entropy vs position) ---")
print(f"  rho = {rho_raw:+.6f}  p = {pval_raw:.2e}")


# ---------------------------------------------------------------------------
# PARTIAL SPEARMAN: controlling for line_length
# ---------------------------------------------------------------------------
# Regress out line_length from both position and entropy
slope_pos, intercept_pos, _, _, _ = stats.linregress(line_lengths, positions)
pos_residuals = positions - (slope_pos * line_lengths + intercept_pos)

slope_f, intercept_f, _, _, _ = stats.linregress(line_lengths, entropies)
feat_residuals = entropies - (slope_f * line_lengths + intercept_f)

rho_partial, pval_partial = stats.spearmanr(pos_residuals, feat_residuals)
print(f"\n--- Partial Spearman (length-controlled) ---")
print(f"  rho = {rho_partial:+.6f}  p = {pval_partial:.2e}")


# ---------------------------------------------------------------------------
# LINE LENGTH CONFOUND CHECK
# ---------------------------------------------------------------------------
rho_len_ent, pval_len_ent = stats.spearmanr(line_lengths, entropies)
print(f"\n--- Line length vs entropy confound ---")
print(f"  rho = {rho_len_ent:+.6f}  p = {pval_len_ent:.2e}")


# ---------------------------------------------------------------------------
# QUINTILE MEANS
# ---------------------------------------------------------------------------
quintile_entropy_means = {}
quintile_n_unique_means = {}
for q in range(5):
    mask = quintiles == q
    if np.sum(mask) > 0:
        quintile_entropy_means[q] = float(np.mean(entropies[mask]))
        quintile_n_unique_means[q] = float(np.mean(n_unique_arr[mask]))
    else:
        quintile_entropy_means[q] = 0.0
        quintile_n_unique_means[q] = 0.0

print(f"\n--- Quintile mean entropy ---")
for q in range(5):
    print(f"  Q{q}: entropy={quintile_entropy_means[q]:.4f}  "
          f"n_unique={quintile_n_unique_means[q]:.2f}")

# Spearman rho across 5 quintile means
q_positions = np.array([0, 1, 2, 3, 4], dtype=float)
q_ent_values = np.array([quintile_entropy_means[q] for q in range(5)])
quintile_rho, quintile_pval = stats.spearmanr(q_positions, q_ent_values)
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
    rho_s, _ = stats.spearmanr(shuffled_positions, entropies)
    shuffle_rhos_raw.append(rho_s)

    # Partial rho on shuffled positions (control for line_length)
    slope_pos_s, intercept_pos_s, _, _, _ = stats.linregress(
        line_lengths, shuffled_positions
    )
    pos_resid_s = shuffled_positions - (
        slope_pos_s * line_lengths + intercept_pos_s
    )
    # feat_residuals for entropy are the same (line_length -> entropy unchanged)
    # but we recompute from scratch for correctness
    slope_f_s, intercept_f_s, _, _, _ = stats.linregress(
        line_lengths, entropies
    )
    feat_resid_s = entropies - (slope_f_s * line_lengths + intercept_f_s)
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
# VERDICT
# ---------------------------------------------------------------------------
# PASS: length-controlled partial shuffle_p < 0.01 AND |quintile_rho| > 0.80
# PARTIAL: only one criterion met
# FAIL: neither

criterion_shuffle = shuffle_p_partial < 0.01
criterion_quintile = abs(quintile_rho) > 0.80

if criterion_shuffle and criterion_quintile:
    verdict = "PASS"
    verdict_detail = (
        f"Entropy collapse confirmed: partial shuffle p={shuffle_p_partial:.4f} "
        f"(< 0.01) and quintile rho={quintile_rho:+.4f} (|rho| > 0.80). "
        f"MIDDLE vocabulary diversity decreases systematically through paragraph body."
    )
elif criterion_shuffle or criterion_quintile:
    verdict = "PARTIAL"
    met = []
    unmet = []
    if criterion_shuffle:
        met.append(f"shuffle_p={shuffle_p_partial:.4f} < 0.01")
    else:
        unmet.append(f"shuffle_p={shuffle_p_partial:.4f} >= 0.01")
    if criterion_quintile:
        met.append(f"|quintile_rho|={abs(quintile_rho):.4f} > 0.80")
    else:
        unmet.append(f"|quintile_rho|={abs(quintile_rho):.4f} <= 0.80")
    verdict_detail = (
        f"Partial evidence for entropy collapse. "
        f"Met: {'; '.join(met)}. Unmet: {'; '.join(unmet)}."
    )
else:
    verdict = "FAIL"
    verdict_detail = (
        f"No entropy collapse detected: partial shuffle p={shuffle_p_partial:.4f} "
        f"(>= 0.01) and |quintile_rho|={abs(quintile_rho):.4f} (<= 0.80). "
        f"MIDDLE vocabulary diversity does not systematically change through "
        f"paragraph body."
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
    "test": "01_vocabulary_entropy_collapse",
    "phase": "PARAGRAPH_STATE_COLLAPSE",
    "verdict": verdict,
    "verdict_detail": verdict_detail,
    "counts": {
        "total_paragraphs": len(paragraphs),
        "big_paragraphs": len(big_paragraphs),
        "body_lines": int(n_body_lines_total),
        "unique_paragraphs_analyzed": int(len(unique_pars)),
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
        f"Q{q}": round(quintile_entropy_means[q], 6) for q in range(5)
    },
    "quintile_rho": round(float(quintile_rho), 6),
    "quintile_n_unique_means": {
        f"Q{q}": round(quintile_n_unique_means[q], 4) for q in range(5)
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
        "rho_with_entropy": round(float(rho_len_ent), 6),
        "p": float(pval_len_ent),
    },
    "parameters": {
        "min_paragraph_lines": 5,
        "n_shuffles": N_SHUFFLES,
        "random_seed": 42,
        "pass_threshold_shuffle_p": 0.01,
        "pass_threshold_quintile_rho": 0.80,
    },
}

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {RESULTS_PATH}")
