"""
Test 05: Hazard-Escape Positional Dynamics
Phase: RISK_PROFILE_MIGRATION

Purpose: Test whether FL (escape/flow) operations change their sub-group composition
through body lines -- specifically whether hazard FL vs safe FL shifts as paragraphs
progress.

Method:
  1. Load Currier B tokens. Build paragraphs via par_initial field.
  2. Keep paragraphs with 5+ lines.
  3. Exclude line 1 (header per C840). Assign each body line a quintile (0-4).
  4. For each body line: classify all tokens by class using class_token_map.json.
  5. Compute three metrics:
     - fl_haz_rate: FL_HAZ token count / total classifiable tokens
     - fl_safe_rate: FL_SAFE token count / total classifiable tokens
     - fl_haz_frac_of_fl: FL_HAZ token count / total FL token count (skip 0-FL lines)
  6. For each metric: partial Spearman rho vs position controlling for line_length,
     1000-shuffle test (seed=42), quintile means.
  7. Bonferroni alpha = 0.01 / 3 = 0.0033.

Provenance: C586 (FL sub-groups), class_token_map.json
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
RESULTS_PATH = PROJECT_ROOT / "phases/RISK_PROFILE_MIGRATION/results/05_hazard_escape_positional_dynamics.json"
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"

# FL sub-groups (C586)
FL_HAZ = {7, 30}    # Hazard FL: medial positions, initiator
FL_SAFE = {38, 40}  # Safe FL: final positions, completion markers
ALL_FL = FL_HAZ | FL_SAFE

BONFERRONI_ALPHA = 0.01 / 3  # 0.003333...


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def assign_quintile(body_idx, n_body):
    """Assign a body line (0-indexed) to a quintile (0-4)."""
    if n_body <= 1:
        return 0
    return min(int((body_idx / (n_body - 1)) * 5), 4)


def partial_spearman(positions, feature, line_lengths):
    """Compute partial Spearman rho of feature vs position, controlling for line_length."""
    slope_pos, intercept_pos, _, _, _ = stats.linregress(line_lengths, positions)
    pos_residuals = positions - (slope_pos * line_lengths + intercept_pos)

    slope_f, intercept_f, _, _, _ = stats.linregress(line_lengths, feature)
    feat_residuals = feature - (slope_f * line_lengths + intercept_f)

    rho, pval = stats.spearmanr(pos_residuals, feat_residuals)
    return rho, pval, pos_residuals, feat_residuals


# ---------------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------------
print("Loading class token map...")
with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
    class_map = json.load(f)

token_to_class = class_map["token_to_class"]
class_to_role = class_map["class_to_role"]

# Verify FL classes: check that all FLOW_OPERATOR classes match our sets
fl_classes_from_data = {int(c) for c, role in class_to_role.items() if role == "FLOW_OPERATOR"}
print(f"FL classes from class_to_role: {sorted(fl_classes_from_data)}")
print(f"Expected ALL_FL: {sorted(ALL_FL)}")
assert fl_classes_from_data == ALL_FL, (
    f"FL class mismatch! Data has {fl_classes_from_data}, expected {ALL_FL}"
)

print("\nLoading Currier B tokens...")
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
fl_haz_rates = []       # FL_HAZ count / total classifiable
fl_safe_rates = []      # FL_SAFE count / total classifiable
fl_haz_fracs = []       # FL_HAZ count / total FL count (only for lines with FL > 0)
line_lengths = []       # number of classifiable tokens per line
paragraph_ids = []      # paragraph index (for shuffle grouping)

# Separate tracking for fl_haz_frac (different subset: only lines with FL > 0)
frac_positions = []
frac_quintiles = []
frac_line_lengths = []
frac_paragraph_ids = []

for par_idx, par in enumerate(big_paragraphs):
    body_lines = par[1:]  # skip header (line 1, per C840)
    n_body = len(body_lines)
    if n_body < 2:
        continue

    for body_idx, (folio, line_num, toks) in enumerate(body_lines):
        norm_pos = body_idx / (n_body - 1)
        q = assign_quintile(body_idx, n_body)

        # Classify all tokens on this line
        n_classifiable = 0
        n_fl_haz = 0
        n_fl_safe = 0
        n_fl_total = 0

        for tok in toks:
            word = tok.word.replace("*", "").strip()
            if not word:
                continue
            if word not in token_to_class:
                continue
            cls = token_to_class[word]
            n_classifiable += 1

            if cls in FL_HAZ:
                n_fl_haz += 1
                n_fl_total += 1
            elif cls in FL_SAFE:
                n_fl_safe += 1
                n_fl_total += 1

        # Skip lines with no classifiable tokens
        if n_classifiable == 0:
            continue

        haz_rate = n_fl_haz / n_classifiable
        safe_rate = n_fl_safe / n_classifiable

        positions.append(norm_pos)
        quintiles.append(q)
        fl_haz_rates.append(haz_rate)
        fl_safe_rates.append(safe_rate)
        line_lengths.append(n_classifiable)
        paragraph_ids.append(par_idx)

        # Only include in frac analysis if there are FL tokens
        if n_fl_total > 0:
            fl_haz_fracs.append(n_fl_haz / n_fl_total)
            frac_positions.append(norm_pos)
            frac_quintiles.append(q)
            frac_line_lengths.append(n_classifiable)
            frac_paragraph_ids.append(par_idx)

# Convert to numpy arrays
positions = np.array(positions)
quintiles = np.array(quintiles)
fl_haz_rates = np.array(fl_haz_rates)
fl_safe_rates = np.array(fl_safe_rates)
line_lengths = np.array(line_lengths, dtype=float)
paragraph_ids = np.array(paragraph_ids)

frac_positions = np.array(frac_positions)
frac_quintiles = np.array(frac_quintiles)
fl_haz_fracs = np.array(fl_haz_fracs)
frac_line_lengths = np.array(frac_line_lengths, dtype=float)
frac_paragraph_ids = np.array(frac_paragraph_ids)

n_body_lines_total = len(positions)
n_frac_lines = len(frac_positions)
print(f"Total body lines analyzed: {n_body_lines_total}")
print(f"Lines with FL > 0 (for frac metric): {n_frac_lines}")


# ---------------------------------------------------------------------------
# ANALYSIS: 3 metrics
# ---------------------------------------------------------------------------
METRICS = [
    ("fl_haz_rate", fl_haz_rates, positions, line_lengths, paragraph_ids, quintiles),
    ("fl_safe_rate", fl_safe_rates, positions, line_lengths, paragraph_ids, quintiles),
    ("fl_haz_frac_of_fl", fl_haz_fracs, frac_positions, frac_line_lengths, frac_paragraph_ids, frac_quintiles),
]

N_SHUFFLES = 1000
rng = np.random.RandomState(42)

metric_results = {}

for metric_name, feature, m_positions, m_lengths, m_par_ids, m_quintiles in METRICS:
    print(f"\n{'='*60}")
    print(f"METRIC: {metric_name} (n={len(feature)})")
    print(f"{'='*60}")

    # --- Partial Spearman ---
    rho_partial, pval_partial, pos_residuals, feat_residuals = partial_spearman(
        m_positions, feature, m_lengths
    )
    print(f"  Partial Spearman rho = {rho_partial:+.6f}  p = {pval_partial:.2e}")

    # --- Quintile means ---
    quintile_means = {}
    for q in range(5):
        mask = m_quintiles == q
        if np.sum(mask) > 0:
            quintile_means[q] = float(np.mean(feature[mask]))
        else:
            quintile_means[q] = 0.0

    print(f"  Quintile means:")
    for q in range(5):
        print(f"    Q{q}: {quintile_means[q]:.6f}")

    q_positions = np.array([0, 1, 2, 3, 4], dtype=float)
    q_values = np.array([quintile_means[q] for q in range(5)])
    quintile_rho, quintile_pval = stats.spearmanr(q_positions, q_values)
    print(f"  Quintile rho: {quintile_rho:+.4f}  p={quintile_pval:.4f}")

    # --- Shuffle test (1000x, seed uses shared rng) ---
    unique_pars = np.unique(m_par_ids)
    par_indices = {pid: np.where(m_par_ids == pid)[0] for pid in unique_pars}

    shuffle_rhos = []
    for _ in range(N_SHUFFLES):
        shuffled_positions = m_positions.copy()
        for pid, idxs in par_indices.items():
            perm = rng.permutation(len(idxs))
            shuffled_positions[idxs] = m_positions[idxs[perm]]

        # Partial rho on shuffled positions
        slope_pos_s, intercept_pos_s, _, _, _ = stats.linregress(
            m_lengths, shuffled_positions
        )
        pos_resid_s = shuffled_positions - (slope_pos_s * m_lengths + intercept_pos_s)

        slope_f_s, intercept_f_s, _, _, _ = stats.linregress(m_lengths, feature)
        feat_resid_s = feature - (slope_f_s * m_lengths + intercept_f_s)

        rho_s, _ = stats.spearmanr(pos_resid_s, feat_resid_s)
        shuffle_rhos.append(rho_s)

    shuffle_rhos = np.array(shuffle_rhos)

    # Empirical p-value (two-sided)
    shuffle_p = float(
        (np.sum(np.abs(shuffle_rhos) >= abs(rho_partial)) + 1) / (N_SHUFFLES + 1)
    )

    print(f"  Shuffle test: observed rho={rho_partial:+.6f}  shuffle_p={shuffle_p:.4f}")
    print(f"  Null distribution: mean={np.mean(shuffle_rhos):+.6f}  std={np.std(shuffle_rhos):.6f}")

    is_significant = shuffle_p < BONFERRONI_ALPHA
    print(f"  Significant (p < {BONFERRONI_ALPHA:.4f})? {is_significant}")

    metric_results[metric_name] = {
        "n_lines": int(len(feature)),
        "partial_spearman": {
            "rho": round(float(rho_partial), 6),
            "analytic_p": float(pval_partial),
            "shuffle_p": round(float(shuffle_p), 6),
        },
        "quintile_means": {f"Q{q}": round(quintile_means[q], 6) for q in range(5)},
        "quintile_rho": round(float(quintile_rho), 6),
        "shuffle_distribution": {
            "mean": round(float(np.mean(shuffle_rhos)), 6),
            "std": round(float(np.std(shuffle_rhos)), 6),
            "observed_rho": round(float(rho_partial), 6),
        },
        "significant": is_significant,
    }


# ---------------------------------------------------------------------------
# VERDICT
# ---------------------------------------------------------------------------
haz_sig = metric_results["fl_haz_rate"]["significant"]
safe_sig = metric_results["fl_safe_rate"]["significant"]
frac_sig = metric_results["fl_haz_frac_of_fl"]["significant"]

# Check complementary: one up and one down
haz_rho = metric_results["fl_haz_rate"]["partial_spearman"]["rho"]
safe_rho = metric_results["fl_safe_rate"]["partial_spearman"]["rho"]
complementary = haz_sig and safe_sig and (haz_rho * safe_rho < 0)  # opposite signs

n_significant = sum([haz_sig, safe_sig, frac_sig])

if complementary or frac_sig:
    verdict = "PASS"
    reasons = []
    if complementary:
        reasons.append(
            f"FL_HAZ and FL_SAFE show complementary significant trends "
            f"(haz rho={haz_rho:+.4f}, safe rho={safe_rho:+.4f})"
        )
    if frac_sig:
        frac_rho = metric_results["fl_haz_frac_of_fl"]["partial_spearman"]["rho"]
        frac_p = metric_results["fl_haz_frac_of_fl"]["partial_spearman"]["shuffle_p"]
        reasons.append(
            f"fl_haz_frac_of_fl shows significant trend "
            f"(rho={frac_rho:+.4f}, shuffle_p={frac_p:.4f} < {BONFERRONI_ALPHA:.4f})"
        )
    verdict_detail = (
        f"FL sub-type shift confirmed. {' AND '.join(reasons)}. "
        f"Hazard FL composition changes systematically through paragraph body."
    )
elif n_significant == 1:
    verdict = "PARTIAL"
    sig_names = []
    if haz_sig:
        sig_names.append("fl_haz_rate")
    if safe_sig:
        sig_names.append("fl_safe_rate")
    if frac_sig:
        sig_names.append("fl_haz_frac_of_fl")
    verdict_detail = (
        f"Partial evidence for FL sub-type shift. "
        f"1 metric significant ({', '.join(sig_names)}), "
        f"but no complementary trend or frac significance."
    )
else:
    verdict = "FAIL"
    verdict_detail = (
        f"No FL sub-type shift detected. "
        f"{n_significant} of 3 metrics significant "
        f"(Bonferroni alpha={BONFERRONI_ALPHA:.4f}). "
        f"Hazard FL composition does not systematically change through paragraph body."
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
    "test": "05_hazard_escape_positional_dynamics",
    "phase": "RISK_PROFILE_MIGRATION",
    "verdict": verdict,
    "verdict_detail": verdict_detail,
    "counts": {
        "total_paragraphs": len(paragraphs),
        "big_paragraphs": len(big_paragraphs),
        "body_lines": int(n_body_lines_total),
        "fl_lines": int(n_frac_lines),
    },
    "fl_classes": {
        "FL_HAZ": sorted(FL_HAZ),
        "FL_SAFE": sorted(FL_SAFE),
        "ALL_FL": sorted(ALL_FL),
    },
    "bonferroni_alpha": round(BONFERRONI_ALPHA, 6),
    "metrics": metric_results,
    "parameters": {
        "min_paragraph_lines": 5,
        "n_shuffles": N_SHUFFLES,
        "random_seed": 42,
        "bonferroni_alpha": round(BONFERRONI_ALPHA, 6),
    },
}

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {RESULTS_PATH}")
