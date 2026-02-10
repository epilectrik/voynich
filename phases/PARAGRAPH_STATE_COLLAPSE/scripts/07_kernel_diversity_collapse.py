#!/usr/bin/env python3
"""
Test 07: Kernel Diversity Collapse
Phase: PARAGRAPH_STATE_COLLAPSE

Purpose: Test whether the diversity of kernel types (k, h, e) decreases
toward paragraph ends -- i.e., do late body lines become more mono-kernel?

Method:
  1. Load Currier B tokens. Build paragraphs via par_initial field.
  2. Keep paragraphs with 5+ lines. Skip header (line 0).
  3. For each body line: classify tokens by kernel type (k, h, e) based on
     morphological PREFIX. Compute kernel_entropy, n_distinct_kernels,
     and per-kernel fractions (k_fraction, h_fraction, e_fraction).
  4. Spearman rho vs normalized position. Partial rho controlling for line_length.
  5. Shuffle test (1000x, seed=42). Bonferroni for 5 sub-tests.

Kernel classification (from PREFIX):
  - k-kernel: prefix contains 'k' (e.g., 'ok', 'k', 'lk', 'yk', 'ke', 'ko', 'ka', etc.)
  - h-kernel: prefix contains 'ch' or 'sh' (e.g., 'ch', 'sh', 'pch', 'tch', 'lch', 'lsh', etc.)
  - e-kernel: prefix doesn't contain 'k', 'ch', or 'sh' -- or token has no prefix but has MIDDLE
  - no-kernel: tokens where kernel can't be determined (skipped)

Provenance: BCSC (kernel structure: k, h, e operators)
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
RESULTS_PATH = PROJECT_ROOT / "phases/PARAGRAPH_STATE_COLLAPSE/results/07_kernel_diversity_collapse.json"

# ============================================================
# KERNEL CLASSIFICATION (from morphological PREFIX)
# ============================================================
morph = Morphology()


def classify_kernel(word):
    """
    Classify a token's kernel type based on its morphological prefix.

    Returns: 'k', 'h', 'e', or None (if unclassifiable).
    """
    m = morph.extract(word)

    prefix = m.prefix
    if prefix is not None:
        # k-kernel: prefix contains 'k'
        if 'k' in prefix:
            return 'k'
        # h-kernel: prefix contains 'ch' or 'sh'
        if 'ch' in prefix or 'sh' in prefix:
            return 'h'
        # e-kernel: prefix exists but contains neither k, ch, nor sh
        return 'e'
    else:
        # No prefix found -- if token has a MIDDLE, classify as e-kernel
        if m.middle is not None and m.middle != '':
            return 'e'
        return None


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
print("Test 07: Kernel Diversity Collapse")
print("Phase: PARAGRAPH_STATE_COLLAPSE")
print("=" * 65)
print(f"\nTotal paragraphs: {total_paragraphs}")
print(f"Paragraphs with 5+ lines: {n_big}")

# ============================================================
# PER BODY LINE: compute kernel metrics
# ============================================================
# For each big paragraph, skip line 0 (header), keep body lines (1..N-1)
# Normalize body position to [0, 1]

positions = []         # normalized position within body
kernel_entropies = []  # Shannon entropy of kernel type distribution
distinct_counts = []   # number of distinct kernel types
k_fractions = []       # fraction of tokens that are k-kernel
h_fractions = []       # fraction of tokens that are h-kernel
e_fractions = []       # fraction of tokens that are e-kernel
line_lengths = []      # number of classifiable tokens per line (confound)

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

        # Kernel classification
        kernels = [classify_kernel(w) for w in words]
        # Filter out None (unclassifiable)
        valid_kernels = [k for k in kernels if k is not None]
        if not valid_kernels:
            continue

        kernel_counts = Counter(valid_kernels)
        ent = shannon_entropy(kernel_counts)
        n_distinct = len(kernel_counts)
        n_valid = len(valid_kernels)

        k_frac = kernel_counts.get('k', 0) / n_valid
        h_frac = kernel_counts.get('h', 0) / n_valid
        e_frac = kernel_counts.get('e', 0) / n_valid

        # Normalized position: 0 = first body line, 1 = last body line
        norm_pos = idx / (n_body - 1) if n_body > 1 else 0.5

        positions.append(norm_pos)
        kernel_entropies.append(ent)
        distinct_counts.append(n_distinct)
        k_fractions.append(k_frac)
        h_fractions.append(h_frac)
        e_fractions.append(e_frac)
        line_lengths.append(n_valid)

positions = np.array(positions)
kernel_entropies = np.array(kernel_entropies)
distinct_counts = np.array(distinct_counts, dtype=float)
k_fractions = np.array(k_fractions)
h_fractions = np.array(h_fractions)
e_fractions = np.array(e_fractions)
line_lengths = np.array(line_lengths, dtype=float)

n_body_lines = len(positions)
print(f"Body lines analyzed: {n_body_lines}")

# ============================================================
# ANALYSIS
# ============================================================
METRICS = {
    'n_distinct_kernels': distinct_counts,
    'kernel_entropy': kernel_entropies,
    'k_fraction': k_fractions,
    'h_fraction': h_fractions,
    'e_fraction': e_fractions,
}

metric_results = {}

for name, values in METRICS.items():
    # 1. Raw Spearman rho
    rho_raw, p_raw = stats.spearmanr(positions, values)

    # 2. Partial Spearman rho controlling for line_length
    rho_partial, p_partial = partial_spearman(positions, values, line_lengths)

    metric_results[name] = {
        'rho_raw': float(rho_raw),
        'p_raw': float(p_raw),
        'rho_partial': float(rho_partial),
        'p_partial': float(p_partial),
        'values': values,
    }

print(f"\n--- Raw Spearman correlations ---")
for name in METRICS:
    r = metric_results[name]
    print(f"  {name:25s} vs position:  rho = {r['rho_raw']:+.4f}, p = {r['p_raw']:.6f}")

print(f"\n--- Partial Spearman (controlling for line_length) ---")
for name in METRICS:
    r = metric_results[name]
    print(f"  {name:25s} vs position:  rho = {r['rho_partial']:+.4f}, p = {r['p_partial']:.6f}")

# ============================================================
# QUINTILE MEANS
# ============================================================
quintile_labels = ["Q0", "Q1", "Q2", "Q3", "Q4"]
quintile_edges = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0001]

quintile_means = {}
for name, values in METRICS.items():
    qm = {}
    for qi in range(5):
        lo = quintile_edges[qi]
        hi = quintile_edges[qi + 1]
        mask = (positions >= lo) & (positions < hi)
        label = quintile_labels[qi]
        qm[label] = float(np.mean(values[mask])) if mask.any() else 0.0
    quintile_means[name] = qm

for name in METRICS:
    print(f"\n--- Quintile means: {name} ---")
    for q in quintile_labels:
        print(f"  {q}: {quintile_means[name][q]:.4f}")

# ============================================================
# SHUFFLE TEST (1000x, seed=42)
# ============================================================
N_SHUFFLES = 1000
rng = np.random.RandomState(42)

shuffle_rhos_raw = {name: np.zeros(N_SHUFFLES) for name in METRICS}
shuffle_rhos_partial = {name: np.zeros(N_SHUFFLES) for name in METRICS}

print(f"\nRunning shuffle test ({N_SHUFFLES} iterations)...")

for i in range(N_SHUFFLES):
    perm_positions = rng.permutation(positions)

    for name, values in METRICS.items():
        # Raw rhos under shuffle
        shuffle_rhos_raw[name][i], _ = stats.spearmanr(perm_positions, values)

        # Partial rhos under shuffle
        r_p, _ = partial_spearman(perm_positions, values, line_lengths)
        shuffle_rhos_partial[name][i] = r_p

# Empirical p-values (one-tailed: we test for NEGATIVE rho, i.e. collapse)
shuffle_p_raw = {}
shuffle_p_partial = {}

for name in METRICS:
    observed_raw = metric_results[name]['rho_raw']
    observed_partial = metric_results[name]['rho_partial']
    shuffle_p_raw[name] = float(np.mean(shuffle_rhos_raw[name] <= observed_raw))
    shuffle_p_partial[name] = float(np.mean(shuffle_rhos_partial[name] <= observed_partial))

# Bonferroni correction: 5 sub-tests, alpha=0.01
bonferroni_alpha = 0.01 / 5  # 0.002

print(f"\n--- Shuffle test results (empirical p-values, one-tailed negative) ---")
for name in METRICS:
    print(f"  {name:25s} raw:     shuffle_p = {shuffle_p_raw[name]:.4f}")
    print(f"  {name:25s} partial: shuffle_p = {shuffle_p_partial[name]:.4f}")
print(f"  Bonferroni alpha:     {bonferroni_alpha}")

# ============================================================
# VERDICT
# ============================================================
# Primary criteria: n_distinct_kernels or kernel_entropy with significant negative
# partial rho (shuffle p < Bonferroni alpha)
significant_metrics = []
suggestive_metrics = []

for name in METRICS:
    rho_p = metric_results[name]['rho_partial']
    sp = shuffle_p_partial[name]
    if rho_p < 0 and sp < bonferroni_alpha:
        significant_metrics.append(name)
    elif rho_p < 0 and sp < 0.05:
        suggestive_metrics.append(name)

# Verdict based on diversity metrics (n_distinct_kernels, kernel_entropy)
diversity_significant = [m for m in significant_metrics if m in ('n_distinct_kernels', 'kernel_entropy')]
diversity_suggestive = [m for m in suggestive_metrics if m in ('n_distinct_kernels', 'kernel_entropy')]

if diversity_significant:
    verdict = "PASS"
elif diversity_suggestive:
    verdict = "PARTIAL"
else:
    verdict = "FAIL"

print(f"\n{'='*65}")
print(f"VERDICT: {verdict}")
if significant_metrics:
    print(f"  Significant metrics (negative partial rho, shuffle p < {bonferroni_alpha}):")
    for m in significant_metrics:
        print(f"    - {m} (rho={metric_results[m]['rho_partial']:+.4f}, shuffle_p={shuffle_p_partial[m]:.4f})")
if suggestive_metrics:
    print(f"  Suggestive metrics (negative partial rho, shuffle p < 0.05):")
    for m in suggestive_metrics:
        print(f"    - {m} (rho={metric_results[m]['rho_partial']:+.4f}, shuffle_p={shuffle_p_partial[m]:.4f})")
if not significant_metrics and not suggestive_metrics:
    print(f"  No metric shows significant negative length-controlled rho.")
print(f"{'='*65}")

# ============================================================
# OUTPUT JSON
# ============================================================
results = {
    "test": "07_kernel_diversity_collapse",
    "phase": "PARAGRAPH_STATE_COLLAPSE",
    "verdict": verdict,
    "counts": {
        "total_paragraphs": total_paragraphs,
        "big_paragraphs": n_big,
        "body_lines": n_body_lines,
    },
}

for name in METRICS:
    results[name] = {
        "raw_rho": round(metric_results[name]['rho_raw'], 6),
        "raw_p": round(metric_results[name]['p_raw'], 6),
        "partial_rho": round(metric_results[name]['rho_partial'], 6),
        "partial_p": round(metric_results[name]['p_partial'], 6),
        "shuffle_p_raw": round(shuffle_p_raw[name], 4),
        "shuffle_p_partial": round(shuffle_p_partial[name], 4),
        "quintile_means": {k: round(v, 6) for k, v in quintile_means[name].items()},
    }

results["bonferroni_alpha"] = bonferroni_alpha
results["significant_metrics"] = significant_metrics
results["suggestive_metrics"] = suggestive_metrics

RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: {RESULTS_PATH}")
