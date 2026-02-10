"""
Test 06: Risk-Kernel Cross-Correlation
Phase: RISK_PROFILE_MIGRATION

Purpose: Test whether hazard sub-group composition and kernel composition co-vary
across body lines, controlling for BOTH position and line length. This is the
central "in tandem" test -- if hazard sub-group mix and kernel mix change together
across lines, it implies a coordinated structural relationship between risk profile
and kernel selection.

Method:
  1. Load Currier B tokens. Build paragraphs via par_initial field.
  2. Keep paragraphs with 5+ lines. Skip header (line 0).
  3. For each body line:
     a. Classify tokens by instruction class (from class_token_map).
     b. Among hazard tokens: compute sub-group fractions (EN_CHSH share, FL_HAZ share).
     c. Among all tokens: classify kernel type (k, h, e) via morphology.
        Compute kernel fractions (h_fraction, e_fraction).
  4. Exclude lines with 0 hazard tokens.
  5. Double-partial Spearman (controlling for line_length AND body position):
     - en_chsh_share vs h_fraction
     - fl_haz_share vs e_fraction
  6. Single-partial Spearman (controlling for line_length only) for comparison.
  7. Quintile-level Spearman across 5 quintile means.
  8. Shuffle test (1000x, seed=42): permute hazard sub-group labels within lines.
  9. Bonferroni alpha = 0.01 / 2 = 0.005.

Verdict:
  PASS: Both cross-correlations significant (shuffle_p < 0.005) after double-partial
  PARTIAL: One significant, or both significant on single-partial but not double-partial
  FAIL: Neither cross-correlation significant

Provenance: C458 (design clamp), C541/C601 (hazard classes), BCSC (kernel structure)
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path("C:/git/voynich").resolve()
RESULTS_PATH = PROJECT_ROOT / "phases/RISK_PROFILE_MIGRATION/results/06_risk_kernel_cross_correlation.json"
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"

# Hazard sub-groups
FL_HAZ = {7, 30}
EN_CHSH = {8, 31}
HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}

BONFERRONI_ALPHA = 0.01 / 2  # 0.005 (2 primary tests)


# ---------------------------------------------------------------------------
# KERNEL CLASSIFICATION
# ---------------------------------------------------------------------------
morph = Morphology()


def classify_kernel(word):
    """
    Classify a token's kernel type based on its morphological prefix.
    Returns: 'k', 'h', 'e', or None (if unclassifiable).
    """
    m = morph.extract(word)
    prefix = m.prefix
    if prefix is not None:
        if 'k' in prefix:
            return 'k'
        if 'ch' in prefix or 'sh' in prefix:
            return 'h'
        return 'e'
    else:
        if m.middle is not None and m.middle != '':
            return 'e'
        return None


# ---------------------------------------------------------------------------
# DOUBLE-PARTIAL SPEARMAN
# ---------------------------------------------------------------------------
def double_partial_spearman(x, y, confound1, confound2):
    """Partial Spearman controlling for two confounds via OLS residualization."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    c1, c2 = np.asarray(confound1, float), np.asarray(confound2, float)
    A = np.column_stack([c1, c2, np.ones(len(c1))])
    coef_x, _, _, _ = np.linalg.lstsq(A, x, rcond=None)
    resid_x = x - A @ coef_x
    coef_y, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    resid_y = y - A @ coef_y
    return stats.spearmanr(resid_x, resid_y)


def single_partial_spearman(x, y, confound):
    """Partial Spearman controlling for one confound via OLS residualization."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    c = np.asarray(confound, float)
    A = np.column_stack([c, np.ones(len(c))])
    coef_x, _, _, _ = np.linalg.lstsq(A, x, rcond=None)
    resid_x = x - A @ coef_x
    coef_y, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    resid_y = y - A @ coef_y
    return stats.spearmanr(resid_x, resid_y)


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
positions = []          # normalized body position [0, 1]
quintiles = []          # quintile assignment [0-4]
en_chsh_shares = []     # EN_CHSH count / hazard token count
fl_haz_shares = []      # FL_HAZ count / hazard token count
h_fractions = []        # h-kernel / total kernel-classifiable
e_fractions = []        # e-kernel / total kernel-classifiable
line_lengths = []       # total classifiable tokens per line
hazard_token_counts = []  # raw hazard count per line
paragraph_ids = []      # paragraph index (for grouping)

# Per-line: lists of (token_word, class_id) for hazard tokens, for shuffle
line_hazard_classes = []   # list of lists of class_ids for hazard tokens per line

for par_idx, par in enumerate(big_paragraphs):
    body_lines = par[1:]  # skip header (line 0, per C840)
    n_body = len(body_lines)
    if n_body < 2:
        continue

    for body_idx, (folio, line_num, toks) in enumerate(body_lines):
        norm_pos = body_idx / (n_body - 1)
        q = assign_quintile(body_idx, n_body)

        # Classify tokens by instruction class
        hazard_class_list = []  # class ids of hazard tokens on this line
        n_fl = 0
        n_en_chsh = 0
        n_hazard = 0

        for tok in toks:
            word = tok.word.replace("*", "").strip()
            if not word:
                continue
            cls = token_to_class.get(word, -1)
            if cls == -1:
                continue
            if cls in HAZARD_CLASSES:
                n_hazard += 1
                hazard_class_list.append(cls)
                if cls in FL_HAZ:
                    n_fl += 1
                if cls in EN_CHSH:
                    n_en_chsh += 1

        # Skip lines with 0 hazard tokens
        if n_hazard == 0:
            continue

        # Compute hazard sub-group fractions
        en_chsh_share = n_en_chsh / n_hazard
        fl_haz_share = n_fl / n_hazard

        # Classify kernel types for all tokens on this line
        n_k = 0
        n_h = 0
        n_e = 0
        n_kernel_total = 0
        for tok in toks:
            word = tok.word.replace("*", "").strip()
            if not word:
                continue
            k = classify_kernel(word)
            if k is not None:
                n_kernel_total += 1
                if k == 'k':
                    n_k += 1
                elif k == 'h':
                    n_h += 1
                elif k == 'e':
                    n_e += 1

        # Skip lines with 0 kernel-classifiable tokens
        if n_kernel_total == 0:
            continue

        h_frac = n_h / n_kernel_total
        e_frac = n_e / n_kernel_total

        positions.append(norm_pos)
        quintiles.append(q)
        en_chsh_shares.append(en_chsh_share)
        fl_haz_shares.append(fl_haz_share)
        h_fractions.append(h_frac)
        e_fractions.append(e_frac)
        line_lengths.append(n_kernel_total)
        hazard_token_counts.append(n_hazard)
        paragraph_ids.append(par_idx)
        line_hazard_classes.append(hazard_class_list)

# Convert to numpy arrays
positions = np.array(positions)
quintiles = np.array(quintiles)
en_chsh_shares = np.array(en_chsh_shares)
fl_haz_shares = np.array(fl_haz_shares)
h_fractions = np.array(h_fractions)
e_fractions = np.array(e_fractions)
line_lengths = np.array(line_lengths, dtype=float)
hazard_token_counts = np.array(hazard_token_counts)
paragraph_ids = np.array(paragraph_ids)

n_lines = len(positions)
print(f"Body lines with hazard tokens: {n_lines}")
print(f"Mean en_chsh_share: {np.mean(en_chsh_shares):.4f}")
print(f"Mean fl_haz_share: {np.mean(fl_haz_shares):.4f}")
print(f"Mean h_fraction: {np.mean(h_fractions):.4f}")
print(f"Mean e_fraction: {np.mean(e_fractions):.4f}")


# ---------------------------------------------------------------------------
# CROSS-CORRELATION 1: en_chsh_share vs h_fraction
# ---------------------------------------------------------------------------
print("\n" + "=" * 65)
print("Cross-Correlation 1: en_chsh_share vs h_fraction")
print("=" * 65)

# Raw Spearman
rho_raw_1, pval_raw_1 = stats.spearmanr(en_chsh_shares, h_fractions)
print(f"  Raw Spearman:            rho = {rho_raw_1:+.6f}  p = {pval_raw_1:.2e}")

# Single-partial (controlling for line_length only)
rho_single_1, pval_single_1 = single_partial_spearman(
    en_chsh_shares, h_fractions, line_lengths
)
print(f"  Single-partial (length): rho = {rho_single_1:+.6f}  p = {pval_single_1:.2e}")

# Double-partial (controlling for line_length AND body position)
rho_double_1, pval_double_1 = double_partial_spearman(
    en_chsh_shares, h_fractions, line_lengths, positions
)
print(f"  Double-partial (len+pos): rho = {rho_double_1:+.6f}  p = {pval_double_1:.2e}")


# ---------------------------------------------------------------------------
# CROSS-CORRELATION 2: fl_haz_share vs e_fraction
# ---------------------------------------------------------------------------
print("\n" + "=" * 65)
print("Cross-Correlation 2: fl_haz_share vs e_fraction")
print("=" * 65)

# Raw Spearman
rho_raw_2, pval_raw_2 = stats.spearmanr(fl_haz_shares, e_fractions)
print(f"  Raw Spearman:            rho = {rho_raw_2:+.6f}  p = {pval_raw_2:.2e}")

# Single-partial (controlling for line_length only)
rho_single_2, pval_single_2 = single_partial_spearman(
    fl_haz_shares, e_fractions, line_lengths
)
print(f"  Single-partial (length): rho = {rho_single_2:+.6f}  p = {pval_single_2:.2e}")

# Double-partial (controlling for line_length AND body position)
rho_double_2, pval_double_2 = double_partial_spearman(
    fl_haz_shares, e_fractions, line_lengths, positions
)
print(f"  Double-partial (len+pos): rho = {rho_double_2:+.6f}  p = {pval_double_2:.2e}")


# ---------------------------------------------------------------------------
# QUINTILE-LEVEL ANALYSIS
# ---------------------------------------------------------------------------
print("\n" + "=" * 65)
print("Quintile-Level Analysis")
print("=" * 65)

quintile_en_chsh_means = {}
quintile_h_frac_means = {}
quintile_fl_haz_means = {}
quintile_e_frac_means = {}

for q in range(5):
    mask = quintiles == q
    if np.sum(mask) > 0:
        quintile_en_chsh_means[q] = float(np.mean(en_chsh_shares[mask]))
        quintile_h_frac_means[q] = float(np.mean(h_fractions[mask]))
        quintile_fl_haz_means[q] = float(np.mean(fl_haz_shares[mask]))
        quintile_e_frac_means[q] = float(np.mean(e_fractions[mask]))
    else:
        quintile_en_chsh_means[q] = 0.0
        quintile_h_frac_means[q] = 0.0
        quintile_fl_haz_means[q] = 0.0
        quintile_e_frac_means[q] = 0.0

print(f"\n  Quintile means (en_chsh_share vs h_fraction):")
for q in range(5):
    print(f"    Q{q}: en_chsh={quintile_en_chsh_means[q]:.4f}  "
          f"h_frac={quintile_h_frac_means[q]:.4f}")

q_positions = np.array([0, 1, 2, 3, 4], dtype=float)
q_en_chsh = np.array([quintile_en_chsh_means[q] for q in range(5)])
q_h_frac = np.array([quintile_h_frac_means[q] for q in range(5)])
quintile_rho_1, quintile_pval_1 = stats.spearmanr(q_en_chsh, q_h_frac)
print(f"  Quintile rho (en_chsh vs h_frac): {quintile_rho_1:+.4f}  p={quintile_pval_1:.4f}")

print(f"\n  Quintile means (fl_haz_share vs e_fraction):")
for q in range(5):
    print(f"    Q{q}: fl_haz={quintile_fl_haz_means[q]:.4f}  "
          f"e_frac={quintile_e_frac_means[q]:.4f}")

q_fl_haz = np.array([quintile_fl_haz_means[q] for q in range(5)])
q_e_frac = np.array([quintile_e_frac_means[q] for q in range(5)])
quintile_rho_2, quintile_pval_2 = stats.spearmanr(q_fl_haz, q_e_frac)
print(f"  Quintile rho (fl_haz vs e_frac): {quintile_rho_2:+.4f}  p={quintile_pval_2:.4f}")


# ---------------------------------------------------------------------------
# SHUFFLE TEST (1000x, seed=42)
# Shuffle: pool all hazard class labels across lines, permute, redistribute
# back to lines (preserving per-line hazard token count). This breaks the
# within-line sub-group composition while keeping line-level hazard counts fixed.
# ---------------------------------------------------------------------------
N_SHUFFLES = 1000
rng = np.random.RandomState(42)

shuffle_rhos_double_1 = np.zeros(N_SHUFFLES)
shuffle_rhos_double_2 = np.zeros(N_SHUFFLES)

# Pool all hazard class labels across all lines
all_hazard_labels = []
line_hazard_sizes = []
for j in range(n_lines):
    all_hazard_labels.extend(line_hazard_classes[j])
    line_hazard_sizes.append(len(line_hazard_classes[j]))
all_hazard_labels = np.array(all_hazard_labels)
line_hazard_sizes = np.array(line_hazard_sizes)
cumulative_sizes = np.cumsum(line_hazard_sizes)

print(f"\nRunning shuffle test ({N_SHUFFLES} iterations)...")
print(f"  Pooled hazard tokens: {len(all_hazard_labels)}")
print("  Shuffling hazard sub-group labels across lines...")

for i in range(N_SHUFFLES):
    # Permute the pooled hazard class labels
    shuffled_labels = rng.permutation(all_hazard_labels)

    # Redistribute to lines and compute sub-group shares
    shuffled_en_chsh = np.zeros(n_lines)
    shuffled_fl_haz = np.zeros(n_lines)

    start = 0
    for j in range(n_lines):
        end = cumulative_sizes[j]
        line_labels = shuffled_labels[start:end]
        n_haz = len(line_labels)
        n_en_s = np.sum(np.isin(line_labels, list(EN_CHSH)))
        n_fl_s = np.sum(np.isin(line_labels, list(FL_HAZ)))
        shuffled_en_chsh[j] = n_en_s / n_haz
        shuffled_fl_haz[j] = n_fl_s / n_haz
        start = end

    # Double-partial rho on shuffled hazard sub-group shares
    rho_s1, _ = double_partial_spearman(
        shuffled_en_chsh, h_fractions, line_lengths, positions
    )
    shuffle_rhos_double_1[i] = rho_s1

    rho_s2, _ = double_partial_spearman(
        shuffled_fl_haz, e_fractions, line_lengths, positions
    )
    shuffle_rhos_double_2[i] = rho_s2

# Empirical p-values (two-sided: |null| >= |observed|)
shuffle_p_1 = float(
    (np.sum(np.abs(shuffle_rhos_double_1) >= abs(rho_double_1)) + 1) / (N_SHUFFLES + 1)
)
shuffle_p_2 = float(
    (np.sum(np.abs(shuffle_rhos_double_2) >= abs(rho_double_2)) + 1) / (N_SHUFFLES + 1)
)

print(f"\n--- Shuffle test results ---")
print(f"  CC1 (en_chsh vs h_frac):")
print(f"    observed double-partial rho = {rho_double_1:+.6f}")
print(f"    shuffle_p = {shuffle_p_1:.4f}  (Bonferroni alpha = {BONFERRONI_ALPHA})")
print(f"    null distribution: mean={np.mean(shuffle_rhos_double_1):+.6f}  "
      f"std={np.std(shuffle_rhos_double_1):.6f}")
print(f"  CC2 (fl_haz vs e_frac):")
print(f"    observed double-partial rho = {rho_double_2:+.6f}")
print(f"    shuffle_p = {shuffle_p_2:.4f}  (Bonferroni alpha = {BONFERRONI_ALPHA})")
print(f"    null distribution: mean={np.mean(shuffle_rhos_double_2):+.6f}  "
      f"std={np.std(shuffle_rhos_double_2):.6f}")


# ---------------------------------------------------------------------------
# VERDICT
# ---------------------------------------------------------------------------
cc1_significant = shuffle_p_1 < BONFERRONI_ALPHA
cc2_significant = shuffle_p_2 < BONFERRONI_ALPHA

# Check single-partial for PARTIAL criterion
cc1_single_sig = pval_single_1 < BONFERRONI_ALPHA
cc2_single_sig = pval_single_2 < BONFERRONI_ALPHA

if cc1_significant and cc2_significant:
    verdict = "PASS"
    verdict_detail = (
        f"Both cross-correlations significant after double-partial control. "
        f"CC1 (en_chsh vs h_frac): rho={rho_double_1:+.4f}, shuffle_p={shuffle_p_1:.4f}. "
        f"CC2 (fl_haz vs e_frac): rho={rho_double_2:+.4f}, shuffle_p={shuffle_p_2:.4f}. "
        f"Hazard sub-group composition and kernel composition co-vary across body lines, "
        f"controlling for both line length and position."
    )
elif cc1_significant or cc2_significant:
    verdict = "PARTIAL"
    sig_label = "CC1" if cc1_significant else "CC2"
    nonsig_label = "CC2" if cc1_significant else "CC1"
    sig_p = shuffle_p_1 if cc1_significant else shuffle_p_2
    nonsig_p = shuffle_p_2 if cc1_significant else shuffle_p_1
    verdict_detail = (
        f"One cross-correlation significant after double-partial control. "
        f"{sig_label}: shuffle_p={sig_p:.4f} < {BONFERRONI_ALPHA}. "
        f"{nonsig_label}: shuffle_p={nonsig_p:.4f} >= {BONFERRONI_ALPHA}."
    )
elif cc1_single_sig and cc2_single_sig:
    verdict = "PARTIAL"
    verdict_detail = (
        f"Both cross-correlations significant on single-partial (length only) "
        f"but not on double-partial (length+position). "
        f"CC1 single-partial p={pval_single_1:.2e}, double shuffle_p={shuffle_p_1:.4f}. "
        f"CC2 single-partial p={pval_single_2:.2e}, double shuffle_p={shuffle_p_2:.4f}. "
        f"Position confound may explain cross-correlation."
    )
else:
    verdict = "FAIL"
    verdict_detail = (
        f"Neither cross-correlation significant. "
        f"CC1 (en_chsh vs h_frac): shuffle_p={shuffle_p_1:.4f}. "
        f"CC2 (fl_haz vs e_frac): shuffle_p={shuffle_p_2:.4f}. "
        f"No evidence that hazard sub-group composition and kernel composition co-vary "
        f"across body lines after controlling for confounds."
    )

sep = "=" * 65
print(f"\n{sep}")
print(f"VERDICT: {verdict}")
print(verdict_detail)
print(sep)


# ---------------------------------------------------------------------------
# SAVE RESULTS
# ---------------------------------------------------------------------------
RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

results = {
    "test": "06_risk_kernel_cross_correlation",
    "phase": "RISK_PROFILE_MIGRATION",
    "verdict": verdict,
    "verdict_detail": verdict_detail,
    "counts": {
        "total_paragraphs": len(paragraphs),
        "big_paragraphs": len(big_paragraphs),
        "body_lines_with_hazard": int(n_lines),
        "tokens_in_class_map": len(token_to_class),
        "mean_hazard_tokens_per_line": round(float(np.mean(hazard_token_counts)), 4),
        "mean_en_chsh_share": round(float(np.mean(en_chsh_shares)), 6),
        "mean_fl_haz_share": round(float(np.mean(fl_haz_shares)), 6),
        "mean_h_fraction": round(float(np.mean(h_fractions)), 6),
        "mean_e_fraction": round(float(np.mean(e_fractions)), 6),
    },
    "cross_correlation_1": {
        "description": "en_chsh_share vs h_fraction",
        "raw_spearman": {
            "rho": round(float(rho_raw_1), 6),
            "p": float(pval_raw_1),
        },
        "single_partial_spearman": {
            "rho": round(float(rho_single_1), 6),
            "p": float(pval_single_1),
            "controlled_for": "line_length",
        },
        "double_partial_spearman": {
            "rho": round(float(rho_double_1), 6),
            "p": float(pval_double_1),
            "controlled_for": ["line_length", "body_position"],
        },
        "shuffle_p": round(float(shuffle_p_1), 6),
        "shuffle_null": {
            "mean": round(float(np.mean(shuffle_rhos_double_1)), 6),
            "std": round(float(np.std(shuffle_rhos_double_1)), 6),
        },
        "significant": cc1_significant,
    },
    "cross_correlation_2": {
        "description": "fl_haz_share vs e_fraction",
        "raw_spearman": {
            "rho": round(float(rho_raw_2), 6),
            "p": float(pval_raw_2),
        },
        "single_partial_spearman": {
            "rho": round(float(rho_single_2), 6),
            "p": float(pval_single_2),
            "controlled_for": "line_length",
        },
        "double_partial_spearman": {
            "rho": round(float(rho_double_2), 6),
            "p": float(pval_double_2),
            "controlled_for": ["line_length", "body_position"],
        },
        "shuffle_p": round(float(shuffle_p_2), 6),
        "shuffle_null": {
            "mean": round(float(np.mean(shuffle_rhos_double_2)), 6),
            "std": round(float(np.std(shuffle_rhos_double_2)), 6),
        },
        "significant": cc2_significant,
    },
    "quintile_analysis": {
        "en_chsh_vs_h_frac": {
            "en_chsh_means": {f"Q{q}": round(quintile_en_chsh_means[q], 6) for q in range(5)},
            "h_frac_means": {f"Q{q}": round(quintile_h_frac_means[q], 6) for q in range(5)},
            "quintile_rho": round(float(quintile_rho_1), 6),
            "quintile_p": round(float(quintile_pval_1), 6),
        },
        "fl_haz_vs_e_frac": {
            "fl_haz_means": {f"Q{q}": round(quintile_fl_haz_means[q], 6) for q in range(5)},
            "e_frac_means": {f"Q{q}": round(quintile_e_frac_means[q], 6) for q in range(5)},
            "quintile_rho": round(float(quintile_rho_2), 6),
            "quintile_p": round(float(quintile_pval_2), 6),
        },
    },
    "hazard_subgroups": {
        "FL_HAZ": sorted(list(FL_HAZ)),
        "EN_CHSH": sorted(list(EN_CHSH)),
        "ALL_HAZARD": sorted(list(HAZARD_CLASSES)),
    },
    "parameters": {
        "min_paragraph_lines": 5,
        "n_shuffles": N_SHUFFLES,
        "random_seed": 42,
        "bonferroni_alpha": BONFERRONI_ALPHA,
        "shuffle_type": "pool hazard class labels across lines, permute, redistribute",
    },
}

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {RESULTS_PATH}")
