#!/usr/bin/env python3
"""
Test 04: Kernel Mediation - Hazard vs Safe
Phase: RISK_PROFILE_MIGRATION

Purpose: Test whether the C965 kernel composition shift (h rises, e drops)
is concentrated in hazard-involved tokens, safe tokens, or both.

Method:
  1. Load Currier B tokens. Build paragraphs via par_initial field.
  2. Keep paragraphs with 5+ lines. Skip header (line 0).
  3. Load class_token_map.json. Split each line's tokens into HAZARD pool
     (class in {7,8,9,23,30,31}) and SAFE pool (class not in HAZARD_CLASSES
     and class != -1).
  4. For each pool, classify tokens by kernel (k, h, e). Skip None.
  5. Compute h_fraction and e_fraction per pool per line.
  6. Lines with <2 kernel-classifiable tokens in hazard pool: exclude from
     hazard analysis only.
  7. 4 metrics: hazard_h_frac, hazard_e_frac, safe_h_frac, safe_e_frac.
  8. Partial Spearman rho vs position, controlling for line_length.
  9. Quintile means. 1000-shuffle test (seed=42).
 10. Bonferroni alpha = 0.01 / 4 = 0.0025.

Verdict:
  PASS:    Kernel shift present in BOTH pools (h up or e down significant
           in each), OR significantly stronger in hazard pool.
  PARTIAL: Shift present in one pool only.
  FAIL:    Shift absent from hazard pool entirely.

Provenance: C965 (kernel composition shift), BCSC (kernel structure)
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
RESULTS_PATH = PROJECT_ROOT / "phases/RISK_PROFILE_MIGRATION/results/04_kernel_mediation_hazard_vs_safe.json"
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"

HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}

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
        if 'k' in prefix:
            return 'k'
        if 'ch' in prefix or 'sh' in prefix:
            return 'h'
        return 'e'
    else:
        if m.middle is not None and m.middle != '':
            return 'e'
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

    A = np.column_stack([confound, np.ones(len(confound))])
    coef_x, _, _, _ = np.linalg.lstsq(A, x, rcond=None)
    resid_x = x - A @ coef_x

    coef_y, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    resid_y = y - A @ coef_y

    return stats.spearmanr(resid_x, resid_y)


# ============================================================
# LOAD CLASS MAP
# ============================================================
with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
    class_data = json.load(f)

token_to_class = class_data["token_to_class"]

# ============================================================
# DATA LOADING: Build paragraphs from par_initial
# ============================================================
tx = Transcript()

# Collect line-level tokens with paragraph structure
line_tokens = defaultdict(list)       # (folio, line) -> [Token, ...]
line_meta = {}                        # (folio, line) -> metadata
folio_lines_ordered = defaultdict(list)

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

# Build paragraphs from par_initial / par_final markers
all_paragraphs = []

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
big_paragraphs = [p for p in all_paragraphs if len(p) >= 5]
n_big = len(big_paragraphs)

print("=" * 65)
print("Test 04: Kernel Mediation - Hazard vs Safe")
print("Phase: RISK_PROFILE_MIGRATION")
print("=" * 65)
print(f"\nTotal paragraphs: {total_paragraphs}")
print(f"Paragraphs with 5+ lines: {n_big}")

# ============================================================
# PER BODY LINE: Split into HAZARD and SAFE pools, compute kernel fractions
# ============================================================

# Structures for hazard pool metrics
hazard_positions = []
hazard_h_fracs = []
hazard_e_fracs = []
hazard_line_lengths = []

# Structures for safe pool metrics
safe_positions = []
safe_h_fracs = []
safe_e_fracs = []
safe_line_lengths = []

excluded_hazard_lines = 0
excluded_safe_lines = 0
total_body_lines = 0

for para_lines in big_paragraphs:
    body_lines = para_lines[1:]  # skip header (line 0)
    n_body = len(body_lines)
    if n_body < 2:
        continue

    for idx, key in enumerate(body_lines):
        total_body_lines += 1
        tokens = line_tokens[key]
        norm_pos = idx / (n_body - 1) if n_body > 1 else 0.5

        # Split tokens into hazard and safe pools
        hazard_kernels = []
        safe_kernels = []

        for t in tokens:
            word = t.word.replace("*", "").strip()
            if not word:
                continue

            # Look up class
            cls = token_to_class.get(word, -1)

            # Classify kernel
            kernel = classify_kernel(word)
            if kernel is None:
                continue

            if cls in HAZARD_CLASSES:
                hazard_kernels.append(kernel)
            elif cls != -1:
                # Safe: classifiable but not hazard
                safe_kernels.append(kernel)
            # cls == -1 (unclassified): skip entirely

        # Hazard pool: need >= 2 kernel-classifiable tokens
        if len(hazard_kernels) >= 2:
            hk_counts = Counter(hazard_kernels)
            n_hk = len(hazard_kernels)
            hazard_positions.append(norm_pos)
            hazard_h_fracs.append(hk_counts.get('h', 0) / n_hk)
            hazard_e_fracs.append(hk_counts.get('e', 0) / n_hk)
            hazard_line_lengths.append(n_hk)
        else:
            excluded_hazard_lines += 1

        # Safe pool: need >= 2 kernel-classifiable tokens
        if len(safe_kernels) >= 2:
            sk_counts = Counter(safe_kernels)
            n_sk = len(safe_kernels)
            safe_positions.append(norm_pos)
            safe_h_fracs.append(sk_counts.get('h', 0) / n_sk)
            safe_e_fracs.append(sk_counts.get('e', 0) / n_sk)
            safe_line_lengths.append(n_sk)
        else:
            excluded_safe_lines += 1

# Convert to numpy arrays
hazard_positions = np.array(hazard_positions)
hazard_h_fracs = np.array(hazard_h_fracs)
hazard_e_fracs = np.array(hazard_e_fracs)
hazard_line_lengths = np.array(hazard_line_lengths, dtype=float)

safe_positions = np.array(safe_positions)
safe_h_fracs = np.array(safe_h_fracs)
safe_e_fracs = np.array(safe_e_fracs)
safe_line_lengths = np.array(safe_line_lengths, dtype=float)

print(f"\nTotal body lines: {total_body_lines}")
print(f"Hazard pool lines (>= 2 kernel tokens): {len(hazard_positions)}")
print(f"  (excluded {excluded_hazard_lines} lines with < 2 hazard kernel tokens)")
print(f"Safe pool lines (>= 2 kernel tokens): {len(safe_positions)}")
print(f"  (excluded {excluded_safe_lines} lines with < 2 safe kernel tokens)")

# ============================================================
# ANALYSIS: 4 metrics
# ============================================================
METRICS = {
    'hazard_h_frac': (hazard_positions, hazard_h_fracs, hazard_line_lengths),
    'hazard_e_frac': (hazard_positions, hazard_e_fracs, hazard_line_lengths),
    'safe_h_frac': (safe_positions, safe_h_fracs, safe_line_lengths),
    'safe_e_frac': (safe_positions, safe_e_fracs, safe_line_lengths),
}

metric_results = {}

BONFERRONI_ALPHA = 0.01 / 4  # 0.0025

print(f"\n--- Partial Spearman (controlling for line_length) ---")

for name, (pos, vals, lengths) in METRICS.items():
    if len(pos) < 10:
        print(f"  {name:25s}: INSUFFICIENT DATA ({len(pos)} lines)")
        metric_results[name] = {
            'rho_partial': float('nan'),
            'p_partial': float('nan'),
            'n_lines': int(len(pos)),
            'insufficient': True,
        }
        continue

    rho_partial, p_partial = partial_spearman(pos, vals, lengths)

    metric_results[name] = {
        'rho_partial': float(rho_partial),
        'p_partial': float(p_partial),
        'n_lines': int(len(pos)),
        'insufficient': False,
    }
    print(f"  {name:25s} rho = {rho_partial:+.4f}, p = {p_partial:.6f} (n={len(pos)})")

# ============================================================
# QUINTILE MEANS
# ============================================================
quintile_labels = ["Q0", "Q1", "Q2", "Q3", "Q4"]
quintile_edges = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0001]

quintile_means = {}
for name, (pos, vals, _) in METRICS.items():
    qm = {}
    for qi in range(5):
        lo = quintile_edges[qi]
        hi = quintile_edges[qi + 1]
        mask = (pos >= lo) & (pos < hi)
        label = quintile_labels[qi]
        qm[label] = float(np.mean(vals[mask])) if mask.any() else 0.0
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

shuffle_rhos = {name: np.zeros(N_SHUFFLES) for name in METRICS}

print(f"\nRunning shuffle test ({N_SHUFFLES} iterations)...")

for i in range(N_SHUFFLES):
    for name, (pos, vals, lengths) in METRICS.items():
        if metric_results[name].get('insufficient', False):
            continue
        perm_pos = rng.permutation(pos)
        r_p, _ = partial_spearman(perm_pos, vals, lengths)
        shuffle_rhos[name][i] = r_p

# Compute empirical p-values
# For h_frac: we expect POSITIVE shift (h rises), so one-tailed positive
# For e_frac: we expect NEGATIVE shift (e drops), so one-tailed negative
shuffle_p = {}
for name in METRICS:
    if metric_results[name].get('insufficient', False):
        shuffle_p[name] = float('nan')
        continue

    observed = metric_results[name]['rho_partial']
    null_dist = shuffle_rhos[name]

    if 'h_frac' in name:
        # One-tailed: how often does null >= observed (h rising)
        shuffle_p[name] = float(np.mean(null_dist >= observed))
    else:
        # One-tailed: how often does null <= observed (e dropping)
        shuffle_p[name] = float(np.mean(null_dist <= observed))

print(f"\n--- Shuffle test results (empirical p-values) ---")
for name in METRICS:
    if metric_results[name].get('insufficient', False):
        print(f"  {name:25s}: INSUFFICIENT DATA")
        continue
    direction = "one-tailed positive (h rising)" if 'h_frac' in name else "one-tailed negative (e dropping)"
    sig = " ***" if shuffle_p[name] < BONFERRONI_ALPHA else ""
    print(f"  {name:25s} rho={metric_results[name]['rho_partial']:+.4f}  "
          f"shuffle_p={shuffle_p[name]:.4f}  [{direction}]{sig}")
print(f"  Bonferroni alpha: {BONFERRONI_ALPHA}")

# ============================================================
# VERDICT
# ============================================================
def is_significant_shift(name):
    """Check if a metric shows significant kernel shift."""
    if metric_results[name].get('insufficient', False):
        return False
    rho = metric_results[name]['rho_partial']
    p = shuffle_p[name]
    if 'h_frac' in name:
        return rho > 0 and p < BONFERRONI_ALPHA
    else:  # e_frac
        return rho < 0 and p < BONFERRONI_ALPHA


hazard_h_sig = is_significant_shift('hazard_h_frac')
hazard_e_sig = is_significant_shift('hazard_e_frac')
safe_h_sig = is_significant_shift('safe_h_frac')
safe_e_sig = is_significant_shift('safe_e_frac')

hazard_any = hazard_h_sig or hazard_e_sig
safe_any = safe_h_sig or safe_e_sig

if (hazard_any and safe_any):
    verdict = "PASS"
    verdict_detail = (
        "Kernel shift present in BOTH hazard and safe pools. "
        f"Hazard: h_sig={hazard_h_sig}, e_sig={hazard_e_sig}. "
        f"Safe: h_sig={safe_h_sig}, e_sig={safe_e_sig}."
    )
elif hazard_any and not safe_any:
    verdict = "PASS"
    verdict_detail = (
        "Kernel shift significantly stronger in hazard pool (present in hazard, absent in safe). "
        f"Hazard: h_sig={hazard_h_sig}, e_sig={hazard_e_sig}. "
        f"Safe: h_sig={safe_h_sig}, e_sig={safe_e_sig}."
    )
elif safe_any and not hazard_any:
    verdict = "PARTIAL"
    verdict_detail = (
        "Kernel shift present in safe pool ONLY, absent from hazard pool. "
        f"Hazard: h_sig={hazard_h_sig}, e_sig={hazard_e_sig}. "
        f"Safe: h_sig={safe_h_sig}, e_sig={safe_e_sig}."
    )
else:
    if not hazard_any:
        verdict = "FAIL"
        verdict_detail = (
            "Kernel shift absent from hazard pool entirely. "
            f"Hazard: h_sig={hazard_h_sig}, e_sig={hazard_e_sig}. "
            f"Safe: h_sig={safe_h_sig}, e_sig={safe_e_sig}."
        )
    else:
        verdict = "FAIL"
        verdict_detail = (
            "No significant kernel shift detected in either pool. "
            f"Hazard: h_sig={hazard_h_sig}, e_sig={hazard_e_sig}. "
            f"Safe: h_sig={safe_h_sig}, e_sig={safe_e_sig}."
        )

print(f"\n{'='*65}")
print(f"VERDICT: {verdict}")
print(verdict_detail)
print(f"{'='*65}")

# ============================================================
# OUTPUT JSON
# ============================================================
results = {
    "test": "04_kernel_mediation_hazard_vs_safe",
    "phase": "RISK_PROFILE_MIGRATION",
    "verdict": verdict,
    "verdict_detail": verdict_detail,
    "counts": {
        "total_paragraphs": total_paragraphs,
        "big_paragraphs": n_big,
        "total_body_lines": total_body_lines,
        "hazard_lines": int(len(hazard_positions)),
        "safe_lines": int(len(safe_positions)),
        "excluded_hazard_lines": excluded_hazard_lines,
        "excluded_safe_lines": excluded_safe_lines,
    },
    "bonferroni_alpha": BONFERRONI_ALPHA,
}

for name in METRICS:
    entry = {
        "n_lines": metric_results[name]['n_lines'],
        "insufficient": metric_results[name].get('insufficient', False),
    }
    if not entry['insufficient']:
        entry["partial_rho"] = round(metric_results[name]['rho_partial'], 6)
        entry["partial_p"] = round(metric_results[name]['p_partial'], 6)
        entry["shuffle_p"] = round(shuffle_p[name], 4)
        entry["significant"] = bool(is_significant_shift(name))
        entry["quintile_means"] = {
            k: round(v, 6) for k, v in quintile_means[name].items()
        }
    results[name] = entry

results["significance_summary"] = {
    "hazard_h_sig": hazard_h_sig,
    "hazard_e_sig": hazard_e_sig,
    "safe_h_sig": safe_h_sig,
    "safe_e_sig": safe_e_sig,
    "hazard_any": hazard_any,
    "safe_any": safe_any,
}

results["parameters"] = {
    "min_paragraph_lines": 5,
    "min_kernel_tokens_per_pool": 2,
    "hazard_classes": sorted(HAZARD_CLASSES),
    "n_shuffles": N_SHUFFLES,
    "random_seed": 42,
    "bonferroni_alpha": BONFERRONI_ALPHA,
}

RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: {RESULTS_PATH}")
