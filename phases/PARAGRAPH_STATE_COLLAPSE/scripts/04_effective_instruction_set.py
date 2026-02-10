#!/usr/bin/env python3
"""
Test 04: Effective Instruction Set Shrinkage
Phase: PARAGRAPH_STATE_COLLAPSE

Purpose: Test whether the number of distinct structural options shrinks as
paragraphs progress, even when compositional proportions stay stable.

Measures 4 metrics per line:
  1. n_unique_roles     -- distinct roles (AUXILIARY, ENERGY_OPERATOR, etc.)
  2. n_unique_classes   -- distinct instruction classes (int from token_to_class)
  3. n_unique_middles   -- distinct MIDDLEs (via Morphology.extract)
  4. n_unique_suffixes  -- distinct suffixes (via Morphology.extract, None = own category)

For each metric, two versions:
  - raw:  metric value
  - rate: metric / n_tokens (controls for line length mechanically)

Each version gets raw Spearman rho, partial Spearman rho (OLS residualized
controlling for line_length), and shuffle p-values (1000x, seed=42).

Verdict:
  Bonferroni alpha = 0.01 / 8 = 0.00125 (4 metrics x 2 versions)
  PASS:    2+ metrics significant on BOTH residualized and rate versions
  PARTIAL: 1 metric significant on both, or 2+ on one version only
  FAIL:    otherwise

Provenance: C963 (body homogeneity), C556 (role classification)
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path("C:/git/voynich").resolve()
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
RESULTS_PATH = PROJECT_ROOT / "phases/PARAGRAPH_STATE_COLLAPSE/results/04_effective_instruction_set.json"

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


def get_class(word):
    return token_to_class.get(word, -1)


# ============================================================
# MORPHOLOGY
# ============================================================
morph = Morphology()


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
print("Test 04: Effective Instruction Set Shrinkage")
print("Phase: PARAGRAPH_STATE_COLLAPSE")
print("=" * 65)
print(f"\nTotal paragraphs: {total_paragraphs}")
print(f"Paragraphs with 5+ lines: {n_big}")

# ============================================================
# PER BODY LINE: compute 4 metrics
# ============================================================
# For each big paragraph, skip line 0 (header), keep body lines (1..N-1)
# Normalize body position to [0, 1]

positions = []        # normalized position within body
n_unique_roles = []   # distinct roles per line
n_unique_classes = [] # distinct instruction classes per line
n_unique_middles = [] # distinct MIDDLEs per line
n_unique_suffixes = []# distinct suffixes per line (None = own category)
line_lengths = []     # number of tokens per line (confound)

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

        # Metric 1: n_unique_roles
        roles = set(get_role(w) for w in words)
        # Metric 2: n_unique_classes
        classes = set(get_class(w) for w in words)
        # Metric 3: n_unique_middles
        middles = set()
        suffixes = set()
        for w in words:
            m = morph.extract(w)
            middles.add(m.middle)
            suffixes.add(m.suffix)  # None is a valid value

        # Normalized position: 0 = first body line, 1 = last body line
        norm_pos = idx / (n_body - 1) if n_body > 1 else 0.5

        positions.append(norm_pos)
        n_unique_roles.append(len(roles))
        n_unique_classes.append(len(classes))
        n_unique_middles.append(len(middles))
        n_unique_suffixes.append(len(suffixes))
        line_lengths.append(n_tokens)

positions = np.array(positions)
line_lengths = np.array(line_lengths, dtype=float)

# Build metric arrays
metrics = {
    "n_unique_roles": np.array(n_unique_roles, dtype=float),
    "n_unique_classes": np.array(n_unique_classes, dtype=float),
    "n_unique_middles": np.array(n_unique_middles, dtype=float),
    "n_unique_suffixes": np.array(n_unique_suffixes, dtype=float),
}

n_body_lines = len(positions)
print(f"Body lines analyzed: {n_body_lines}")

# ============================================================
# QUINTILE SETUP
# ============================================================
quintile_labels = ["Q0", "Q1", "Q2", "Q3", "Q4"]
quintile_edges = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0001]

quintile_masks = {}
for qi in range(5):
    lo = quintile_edges[qi]
    hi = quintile_edges[qi + 1]
    quintile_masks[quintile_labels[qi]] = (positions >= lo) & (positions < hi)

# ============================================================
# ANALYSIS: For each metric, compute raw and rate versions
# ============================================================
N_SHUFFLES = 1000
rng = np.random.RandomState(42)

# Pre-generate all permutations (for consistency across metrics)
all_permutations = [rng.permutation(len(positions)) for _ in range(N_SHUFFLES)]

metric_results = {}

for metric_name, metric_arr in metrics.items():
    # Rate version: metric / n_tokens
    rate_arr = metric_arr / line_lengths

    for version_name, values in [("raw", metric_arr), ("rate", rate_arr)]:
        key = f"{metric_name}_{version_name}"
        print(f"\n--- {key} ---")

        # 1. Raw Spearman rho
        rho_raw, p_raw = stats.spearmanr(positions, values)

        # 2. Partial Spearman rho controlling for line_length
        rho_partial, p_partial = partial_spearman(positions, values, line_lengths)

        print(f"  Raw Spearman:     rho = {rho_raw:+.4f}, p = {p_raw:.6f}")
        print(f"  Partial Spearman: rho = {rho_partial:+.4f}, p = {p_partial:.6f}")

        # 3. Quintile means
        q_means = {}
        for ql in quintile_labels:
            mask = quintile_masks[ql]
            q_means[ql] = float(np.mean(values[mask])) if mask.any() else 0.0

        # 4. Shuffle test (1000x)
        shuffle_rho_raw = np.zeros(N_SHUFFLES)
        shuffle_rho_partial = np.zeros(N_SHUFFLES)

        for i in range(N_SHUFFLES):
            perm_positions = positions[all_permutations[i]]

            shuffle_rho_raw[i], _ = stats.spearmanr(perm_positions, values)
            r_p, _ = partial_spearman(perm_positions, values, line_lengths)
            shuffle_rho_partial[i] = r_p

        # Empirical p-values (one-tailed: test for NEGATIVE rho, i.e. shrinkage)
        shuffle_p_raw = float(np.mean(shuffle_rho_raw <= rho_raw))
        shuffle_p_partial = float(np.mean(shuffle_rho_partial <= rho_partial))

        print(f"  Shuffle p (raw):     {shuffle_p_raw:.4f}")
        print(f"  Shuffle p (partial): {shuffle_p_partial:.4f}")

        metric_results[key] = {
            "raw_rho": round(float(rho_raw), 6),
            "raw_p": round(float(p_raw), 6),
            "partial_rho": round(float(rho_partial), 6),
            "partial_p": round(float(p_partial), 6),
            "shuffle_p_raw": round(shuffle_p_raw, 4),
            "shuffle_p_partial": round(shuffle_p_partial, 4),
            "quintile_means": {k: round(v, 6) for k, v in q_means.items()},
        }

# ============================================================
# VERDICT
# ============================================================
# Bonferroni alpha = 0.01 / 8 = 0.00125 (4 metrics x 2 versions)
bonferroni_alpha = 0.01 / 8  # 0.00125

print(f"\nBonferroni alpha: {bonferroni_alpha}")

# A metric is significant on a version if:
#   partial rho < 0 AND shuffle_p_partial < bonferroni_alpha
# Check which metrics pass on residualized (partial) and rate versions

sig_partial = set()  # metrics significant on raw+partial (residualized)
sig_rate = set()     # metrics significant on rate+partial (rate version)

for metric_name in metrics:
    raw_key = f"{metric_name}_raw"
    rate_key = f"{metric_name}_rate"

    # Check residualized version (raw metric, partial rho)
    r = metric_results[raw_key]
    if r["partial_rho"] < 0 and r["shuffle_p_partial"] < bonferroni_alpha:
        sig_partial.add(metric_name)

    # Check rate version (rate metric, partial rho)
    r = metric_results[rate_key]
    if r["partial_rho"] < 0 and r["shuffle_p_partial"] < bonferroni_alpha:
        sig_rate.add(metric_name)

sig_both = sig_partial & sig_rate  # significant on BOTH versions

if len(sig_both) >= 2:
    verdict = "PASS"
elif len(sig_both) >= 1 or len(sig_partial) >= 2 or len(sig_rate) >= 2:
    verdict = "PARTIAL"
else:
    verdict = "FAIL"

print(f"\n{'='*65}")
print(f"VERDICT: {verdict}")
print(f"  Metrics significant on residualized (partial): {sorted(sig_partial) if sig_partial else 'none'}")
print(f"  Metrics significant on rate version:           {sorted(sig_rate) if sig_rate else 'none'}")
print(f"  Metrics significant on BOTH:                   {sorted(sig_both) if sig_both else 'none'}")
print(f"{'='*65}")

# ============================================================
# OUTPUT JSON
# ============================================================
results = {
    "test": "04_effective_instruction_set",
    "phase": "PARAGRAPH_STATE_COLLAPSE",
    "verdict": verdict,
    "counts": {
        "total_paragraphs": total_paragraphs,
        "big_paragraphs": n_big,
        "body_lines": n_body_lines,
    },
    "metrics": metric_results,
    "bonferroni_alpha": round(bonferroni_alpha, 6),
    "significant_residualized": sorted(sig_partial),
    "significant_rate": sorted(sig_rate),
    "significant_both": sorted(sig_both),
}

RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: {RESULTS_PATH}")
