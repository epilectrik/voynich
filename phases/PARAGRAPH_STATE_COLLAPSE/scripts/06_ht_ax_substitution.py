#!/usr/bin/env python3
"""
Test 06: HT->AX Substitution
Phase: PARAGRAPH_STATE_COLLAPSE

Purpose: Test whether HT (high-frequency terminal) rate drops and AX (auxiliary)
rate rises through paragraph bodies, suggesting a substitution pattern.
C842 says HT is flat at ~26% in body. This tests if there's a subtle gradient
within that flat band, and whether HT and AX move in opposite directions.

Method:
  1. Load Currier B tokens. Build paragraphs via par_initial field.
  2. Keep paragraphs with 5+ lines. Skip header (line 0).
  3. For each body line: compute ht_rate (fraction of HT tokens via is_ht)
     and ax_rate (fraction of AUXILIARY tokens via class_token_map).
  4. Spearman rho vs normalized position. Partial rho controlling for line_length.
  5. Cross-correlation between HT rate and AX rate across all body lines.
  6. Shuffle test (1000x, seed=42). Bonferroni for 2 sub-tests.

Provenance: C842 (HT body rate), C556 (role classification), C963 (body homogeneity)
"""
import sys
import json
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript, TokenDictionary

PROJECT_ROOT = Path("C:/git/voynich").resolve()
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
RESULTS_PATH = PROJECT_ROOT / "phases/PARAGRAPH_STATE_COLLAPSE/results/06_ht_ax_substitution.json"

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
# HT CLASSIFICATION (from token dictionary, C740, C872)
# HT = tokens with role.primary == 'UNKNOWN' in token dictionary
# ============================================================
td = TokenDictionary()
ht_words = set()
for word, entry in td._load()['tokens'].items():
    if entry.get('role', {}).get('primary') == 'UNKNOWN':
        ht_words.add(word)


def is_ht(word):
    return word in ht_words


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
print("Test 06: HT->AX Substitution")
print("Phase: PARAGRAPH_STATE_COLLAPSE")
print("=" * 65)
print(f"\nTotal paragraphs: {total_paragraphs}")
print(f"Paragraphs with 5+ lines: {n_big}")

# ============================================================
# PER BODY LINE: compute ht_rate and ax_rate
# ============================================================
# For each big paragraph, skip line 0 (header), keep body lines (1..N-1)
# Normalize body position to [0, 1]

positions = []       # normalized position within body
ht_rates = []        # fraction of tokens that are HT
ax_rates = []        # fraction of tokens with role=AUXILIARY
line_lengths = []    # number of tokens per line (confound)

for para_lines in big_paragraphs:
    # Skip header line (index 0). Body = lines 1..end
    body_lines = para_lines[1:]
    n_body = len(body_lines)
    if n_body < 2:
        continue

    for idx, key in enumerate(body_lines):
        tokens = line_tokens[key]
        if not tokens:
            continue

        n_tokens = len(tokens)

        # HT rate: fraction of tokens that are HT (via token dictionary lookup)
        n_ht = sum(1 for t in tokens if is_ht(t.word))
        ht_rate = n_ht / n_tokens

        # AX rate: fraction of tokens with AUXILIARY role (via class_token_map)
        n_ax = sum(1 for t in tokens if get_role(t.word) == "AUXILIARY")
        ax_rate = n_ax / n_tokens

        # Normalized position: 0 = first body line, 1 = last body line
        norm_pos = idx / (n_body - 1) if n_body > 1 else 0.5

        positions.append(norm_pos)
        ht_rates.append(ht_rate)
        ax_rates.append(ax_rate)
        line_lengths.append(n_tokens)

positions = np.array(positions)
ht_rates = np.array(ht_rates)
ax_rates = np.array(ax_rates)
line_lengths = np.array(line_lengths, dtype=float)

n_body_lines = len(positions)
print(f"Body lines analyzed: {n_body_lines}")

# ============================================================
# ANALYSIS
# ============================================================
# 1. Raw Spearman rho
rho_ht_raw, p_ht_raw = stats.spearmanr(positions, ht_rates)
rho_ax_raw, p_ax_raw = stats.spearmanr(positions, ax_rates)

# 2. Partial Spearman rho controlling for line_length
rho_ht_partial, p_ht_partial = partial_spearman(positions, ht_rates, line_lengths)
rho_ax_partial, p_ax_partial = partial_spearman(positions, ax_rates, line_lengths)

# 3. Cross-correlation: HT rate vs AX rate across all body lines
rho_cross, p_cross = stats.spearmanr(ht_rates, ax_rates)

print(f"\n--- Raw Spearman correlations ---")
print(f"  ht_rate vs position:  rho = {rho_ht_raw:+.4f}, p = {p_ht_raw:.6f}")
print(f"  ax_rate vs position:  rho = {rho_ax_raw:+.4f}, p = {p_ax_raw:.6f}")
print(f"\n--- Partial Spearman (controlling for line_length) ---")
print(f"  ht_rate vs position:  rho = {rho_ht_partial:+.4f}, p = {p_ht_partial:.6f}")
print(f"  ax_rate vs position:  rho = {rho_ax_partial:+.4f}, p = {p_ax_partial:.6f}")
print(f"\n--- Cross-correlation (HT rate vs AX rate) ---")
print(f"  rho = {rho_cross:+.4f}, p = {p_cross:.6f}")

# ============================================================
# QUINTILE MEANS
# ============================================================
quintile_labels = ["Q0", "Q1", "Q2", "Q3", "Q4"]
quintile_edges = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0001]

ht_quintile_means = {}
ax_quintile_means = {}

for qi in range(5):
    lo = quintile_edges[qi]
    hi = quintile_edges[qi + 1]
    mask = (positions >= lo) & (positions < hi)
    label = quintile_labels[qi]
    ht_quintile_means[label] = float(np.mean(ht_rates[mask])) if mask.any() else 0.0
    ax_quintile_means[label] = float(np.mean(ax_rates[mask])) if mask.any() else 0.0

print(f"\n--- Quintile means: ht_rate ---")
for q in quintile_labels:
    print(f"  {q}: {ht_quintile_means[q]:.4f}")

print(f"\n--- Quintile means: ax_rate ---")
for q in quintile_labels:
    print(f"  {q}: {ax_quintile_means[q]:.4f}")

# ============================================================
# SHUFFLE TEST (1000x, seed=42)
# ============================================================
N_SHUFFLES = 1000
rng = np.random.RandomState(42)

shuffle_rho_ht_raw = np.zeros(N_SHUFFLES)
shuffle_rho_ht_partial = np.zeros(N_SHUFFLES)
shuffle_rho_ax_raw = np.zeros(N_SHUFFLES)
shuffle_rho_ax_partial = np.zeros(N_SHUFFLES)
shuffle_rho_cross = np.zeros(N_SHUFFLES)

print(f"\nRunning shuffle test ({N_SHUFFLES} iterations)...")

for i in range(N_SHUFFLES):
    perm_positions = rng.permutation(positions)

    # Raw rhos under shuffle
    shuffle_rho_ht_raw[i], _ = stats.spearmanr(perm_positions, ht_rates)
    shuffle_rho_ax_raw[i], _ = stats.spearmanr(perm_positions, ax_rates)

    # Partial rhos under shuffle
    r_ht_p, _ = partial_spearman(perm_positions, ht_rates, line_lengths)
    shuffle_rho_ht_partial[i] = r_ht_p

    r_ax_p, _ = partial_spearman(perm_positions, ax_rates, line_lengths)
    shuffle_rho_ax_partial[i] = r_ax_p

    # Cross-correlation under shuffle: shuffle HT rates, correlate with AX rates
    perm_ht = rng.permutation(ht_rates)
    shuffle_rho_cross[i], _ = stats.spearmanr(perm_ht, ax_rates)

# Empirical p-values
# For HT: test for NEGATIVE rho (HT drops)
shuffle_p_ht_raw = float(np.mean(shuffle_rho_ht_raw <= rho_ht_raw))
shuffle_p_ht_partial = float(np.mean(shuffle_rho_ht_partial <= rho_ht_partial))
# For AX: test for POSITIVE rho (AX rises)
shuffle_p_ax_raw = float(np.mean(shuffle_rho_ax_raw >= rho_ax_raw))
shuffle_p_ax_partial = float(np.mean(shuffle_rho_ax_partial >= rho_ax_partial))
# For cross-correlation: test for NEGATIVE rho (substitution)
shuffle_p_cross = float(np.mean(shuffle_rho_cross <= rho_cross))

# Bonferroni correction: 2 sub-tests (HT, AX), alpha=0.01
bonferroni_alpha = 0.005

print(f"\n--- Shuffle test results (empirical p-values) ---")
print(f"  ht_rate raw (one-tailed neg):     shuffle_p = {shuffle_p_ht_raw:.4f}")
print(f"  ht_rate partial (one-tailed neg):  shuffle_p = {shuffle_p_ht_partial:.4f}")
print(f"  ax_rate raw (one-tailed pos):      shuffle_p = {shuffle_p_ax_raw:.4f}")
print(f"  ax_rate partial (one-tailed pos):  shuffle_p = {shuffle_p_ax_partial:.4f}")
print(f"  cross-corr (one-tailed neg):       shuffle_p = {shuffle_p_cross:.4f}")
print(f"  Bonferroni alpha:                  {bonferroni_alpha}")

# ============================================================
# VERDICT
# ============================================================
# HT significant: negative partial rho, shuffle p < Bonferroni alpha
ht_significant = (rho_ht_partial < 0) and (shuffle_p_ht_partial < bonferroni_alpha)
# AX significant: positive partial rho, shuffle p < Bonferroni alpha
ax_significant = (rho_ax_partial > 0) and (shuffle_p_ax_partial < bonferroni_alpha)
# Cross-correlation significant: negative rho, shuffle p < 0.01
cross_significant = (rho_cross < 0) and (shuffle_p_cross < 0.01)

# Check opposite signs
opposite_signs = (rho_ht_partial < 0 and rho_ax_partial > 0) or (rho_ht_partial > 0 and rho_ax_partial < 0)

if opposite_signs and ht_significant and ax_significant and cross_significant:
    verdict = "PASS"
elif opposite_signs and (ht_significant or ax_significant):
    verdict = "PARTIAL"
elif (not opposite_signs) and cross_significant:
    verdict = "PARTIAL"
else:
    verdict = "FAIL"

significant_metrics = []
if ht_significant:
    significant_metrics.append("ht_rate")
if ax_significant:
    significant_metrics.append("ax_rate")
if cross_significant:
    significant_metrics.append("ht_ax_cross_correlation")

print(f"\n{'='*65}")
print(f"VERDICT: {verdict}")
print(f"  HT partial rho: {rho_ht_partial:+.4f} (significant={ht_significant})")
print(f"  AX partial rho: {rho_ax_partial:+.4f} (significant={ax_significant})")
print(f"  Opposite signs: {opposite_signs}")
print(f"  Cross-correlation: {rho_cross:+.4f} (significant={cross_significant})")
if significant_metrics:
    print(f"  Significant metrics:")
    for m in significant_metrics:
        print(f"    - {m}")
else:
    print(f"  No significant metrics.")
print(f"{'='*65}")

# ============================================================
# OUTPUT JSON
# ============================================================
results = {
    "test": "06_ht_ax_substitution",
    "phase": "PARAGRAPH_STATE_COLLAPSE",
    "verdict": verdict,
    "counts": {
        "total_paragraphs": total_paragraphs,
        "big_paragraphs": n_big,
        "body_lines": n_body_lines,
    },
    "ht_rate": {
        "raw_rho": round(float(rho_ht_raw), 6),
        "raw_p": round(float(p_ht_raw), 6),
        "partial_rho": round(float(rho_ht_partial), 6),
        "partial_p": round(float(p_ht_partial), 6),
        "shuffle_p_raw": round(shuffle_p_ht_raw, 4),
        "shuffle_p_partial": round(shuffle_p_ht_partial, 4),
        "quintile_means": {k: round(v, 6) for k, v in ht_quintile_means.items()},
    },
    "ax_rate": {
        "raw_rho": round(float(rho_ax_raw), 6),
        "raw_p": round(float(p_ax_raw), 6),
        "partial_rho": round(float(rho_ax_partial), 6),
        "partial_p": round(float(p_ax_partial), 6),
        "shuffle_p_raw": round(shuffle_p_ax_raw, 4),
        "shuffle_p_partial": round(shuffle_p_ax_partial, 4),
        "quintile_means": {k: round(v, 6) for k, v in ax_quintile_means.items()},
    },
    "ht_ax_cross_correlation": {
        "rho": round(float(rho_cross), 6),
        "p": round(float(p_cross), 6),
        "shuffle_p": round(shuffle_p_cross, 4),
    },
    "bonferroni_alpha": bonferroni_alpha,
    "significant_metrics": significant_metrics,
}

RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: {RESULTS_PATH}")
