"""
Test 02: Hazard Sub-Group Migration
Phase: RISK_PROFILE_MIGRATION

Purpose: Test whether the relative mix of hazard sub-groups shifts through
paragraph body lines. Each body line's hazard-involved tokens are classified
into four sub-groups (FL_HAZ, EN_CHSH, FQ_CONN, FQ_CLOSER) and their fractional
representation is tracked across normalized line position.

Method:
  1. Load Currier B tokens. Build paragraphs via par_initial field.
  2. Keep paragraphs with 5+ lines.
  3. Exclude line 1 (header per C840). Assign each body line a normalized position.
  4. For each body line: classify tokens by class, compute sub-group fractions
     among hazard-involved tokens only.
  5. Exclude lines with 0 hazard tokens (report exclusion rate).
  6. For each sub-group fraction: partial Spearman rho vs normalized position,
     controlling for line_length.
  7. 1000-shuffle test (seed=42) per sub-group.
  8. Bonferroni alpha = 0.01 / 4 = 0.0025.

Provenance: C601, C541, C586
"""

import sys
import json
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript

PROJECT_ROOT = Path("C:/git/voynich").resolve()
RESULTS_PATH = PROJECT_ROOT / "phases/RISK_PROFILE_MIGRATION/results/02_hazard_subgroup_migration.json"
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"


# ---------------------------------------------------------------------------
# SUB-GROUP DEFINITIONS (C601, C541, C586)
# ---------------------------------------------------------------------------
FL_HAZ = {7, 30}        # Flow hazard (initiator, 47%)
EN_CHSH = {8, 31}       # Energy ch/sh-prefixed (absorber, 58%)
FQ_CONN = {9}           # Frequent connector (relay)
FQ_CLOSER = {23}        # Frequent closer
HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}

SUBGROUP_NAMES = ["fl_haz", "en_chsh", "fq_conn", "fq_closer"]
SUBGROUP_SETS = [FL_HAZ, EN_CHSH, FQ_CONN, FQ_CLOSER]

BONFERRONI_ALPHA = 0.01 / 4  # 0.0025


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
print("Loading class token map...")
with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
    class_map_raw = json.load(f)

token_to_class = class_map_raw["token_to_class"]

print("Loading Currier B tokens...")
tx = Transcript()

# Build lines
from collections import defaultdict
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
line_lengths = []       # number of tokens per line (all tokens, not just hazard)
paragraph_ids = []      # paragraph index (for shuffle grouping)

# Per sub-group fractions
subgroup_fracs = {name: [] for name in SUBGROUP_NAMES}

total_body_lines = 0
excluded_lines = 0

for par_idx, par in enumerate(big_paragraphs):
    body_lines = par[1:]  # skip header (line 1, per C840)
    n_body = len(body_lines)
    if n_body < 2:
        continue

    for body_idx, (folio, line_num, toks) in enumerate(body_lines):
        total_body_lines += 1

        # Classify each token
        hazard_counts = {name: 0 for name in SUBGROUP_NAMES}
        total_hazard = 0
        n_tokens = 0

        for tok in toks:
            word = tok.word.replace("*", "").strip()
            if not word:
                continue
            n_tokens += 1

            cls = token_to_class.get(word)
            if cls is None:
                continue
            if cls not in HAZARD_CLASSES:
                continue

            total_hazard += 1
            for name, sg_set in zip(SUBGROUP_NAMES, SUBGROUP_SETS):
                if cls in sg_set:
                    hazard_counts[name] += 1

        # Exclude lines with 0 hazard tokens
        if total_hazard == 0:
            excluded_lines += 1
            continue

        # Normalized position
        norm_pos = body_idx / (n_body - 1)
        q = assign_quintile(body_idx, n_body)

        positions.append(norm_pos)
        quintiles.append(q)
        line_lengths.append(n_tokens)
        paragraph_ids.append(par_idx)

        for name in SUBGROUP_NAMES:
            subgroup_fracs[name].append(hazard_counts[name] / total_hazard)

# Convert to numpy arrays
positions = np.array(positions)
quintiles = np.array(quintiles)
line_lengths = np.array(line_lengths, dtype=float)
paragraph_ids = np.array(paragraph_ids)

frac_arrays = {name: np.array(subgroup_fracs[name]) for name in SUBGROUP_NAMES}

n_body_lines_total = len(positions)
exclusion_rate = excluded_lines / total_body_lines if total_body_lines > 0 else 0.0

print(f"Total body lines considered: {total_body_lines}")
print(f"Excluded (0 hazard tokens): {excluded_lines} ({exclusion_rate:.1%})")
print(f"Body lines analyzed: {n_body_lines_total}")


# ---------------------------------------------------------------------------
# PER-SUBGROUP ANALYSIS
# ---------------------------------------------------------------------------
unique_pars = np.unique(paragraph_ids)
par_indices = {pid: np.where(paragraph_ids == pid)[0] for pid in unique_pars}

N_SHUFFLES = 1000
rng = np.random.RandomState(42)

subgroup_results = {}

for sg_name in SUBGROUP_NAMES:
    fracs = frac_arrays[sg_name]

    # --- Raw Spearman ---
    rho_raw, pval_raw = stats.spearmanr(positions, fracs)

    # --- Partial Spearman: controlling for line_length ---
    slope_pos, intercept_pos, _, _, _ = stats.linregress(line_lengths, positions)
    pos_residuals = positions - (slope_pos * line_lengths + intercept_pos)

    slope_f, intercept_f, _, _, _ = stats.linregress(line_lengths, fracs)
    feat_residuals = fracs - (slope_f * line_lengths + intercept_f)

    rho_partial, pval_partial = stats.spearmanr(pos_residuals, feat_residuals)

    # --- Line length confound ---
    rho_len_frac, pval_len_frac = stats.spearmanr(line_lengths, fracs)

    # --- Quintile means ---
    quintile_means = {}
    for q in range(5):
        mask = quintiles == q
        if np.sum(mask) > 0:
            quintile_means[q] = float(np.mean(fracs[mask]))
        else:
            quintile_means[q] = 0.0

    # Spearman rho across 5 quintile means
    q_positions = np.array([0, 1, 2, 3, 4], dtype=float)
    q_values = np.array([quintile_means[q] for q in range(5)])
    quintile_rho, quintile_pval = stats.spearmanr(q_positions, q_values)

    # --- Shuffle test (1000x, seed already set per-subgroup via shared rng) ---
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
        slope_f_s, intercept_f_s, _, _, _ = stats.linregress(
            line_lengths, fracs
        )
        feat_resid_s = fracs - (slope_f_s * line_lengths + intercept_f_s)
        rho_p_s, _ = stats.spearmanr(pos_resid_s, feat_resid_s)
        shuffle_rhos_partial.append(rho_p_s)

    shuffle_rhos_partial = np.array(shuffle_rhos_partial)

    # Empirical p-value (two-sided)
    shuffle_p_partial = float(
        (np.sum(np.abs(shuffle_rhos_partial) >= abs(rho_partial)) + 1)
        / (N_SHUFFLES + 1)
    )

    is_significant = shuffle_p_partial < BONFERRONI_ALPHA

    print(f"\n--- {sg_name} ---")
    print(f"  Raw Spearman:     rho={rho_raw:+.6f}  p={pval_raw:.2e}")
    print(f"  Partial Spearman: rho={rho_partial:+.6f}  p={pval_partial:.2e}")
    print(f"  Shuffle p (partial): {shuffle_p_partial:.4f}  "
          f"{'SIGNIFICANT' if is_significant else 'not significant'} (alpha={BONFERRONI_ALPHA})")
    print(f"  Quintile means: {', '.join(f'Q{q}={quintile_means[q]:.4f}' for q in range(5))}")
    print(f"  Quintile rho: {quintile_rho:+.4f}")
    print(f"  Length confound: rho={rho_len_frac:+.6f}  p={pval_len_frac:.2e}")

    subgroup_results[sg_name] = {
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
            f"Q{q}": round(quintile_means[q], 6) for q in range(5)
        },
        "quintile_rho": round(float(quintile_rho), 6),
        "line_length_confound": {
            "rho_with_frac": round(float(rho_len_frac), 6),
            "p": float(pval_len_frac),
        },
        "shuffle_distribution": {
            "mean": round(float(np.mean(shuffle_rhos_partial)), 6),
            "std": round(float(np.std(shuffle_rhos_partial)), 6),
            "observed_rho": round(float(rho_partial), 6),
        },
        "significant": is_significant,
    }


# ---------------------------------------------------------------------------
# VERDICT
# ---------------------------------------------------------------------------
sig_subgroups = [name for name in SUBGROUP_NAMES if subgroup_results[name]["significant"]]
sig_rhos = {name: subgroup_results[name]["partial_spearman"]["rho"] for name in sig_subgroups}

n_sig = len(sig_subgroups)
has_positive = any(r > 0 for r in sig_rhos.values())
has_negative = any(r < 0 for r in sig_rhos.values())
complementary = has_positive and has_negative

if n_sig >= 2 and complementary:
    verdict = "PASS"
    pos_sgs = [n for n in sig_subgroups if sig_rhos[n] > 0]
    neg_sgs = [n for n in sig_subgroups if sig_rhos[n] < 0]
    verdict_detail = (
        f"Hazard sub-group migration confirmed: {n_sig} sub-groups significant "
        f"(Bonferroni alpha={BONFERRONI_ALPHA}) with complementary directions. "
        f"Increasing: {', '.join(f'{n}(rho={sig_rhos[n]:+.4f})' for n in pos_sgs)}. "
        f"Decreasing: {', '.join(f'{n}(rho={sig_rhos[n]:+.4f})' for n in neg_sgs)}."
    )
elif n_sig >= 1:
    verdict = "PARTIAL"
    sig_parts = []
    for n in sig_subgroups:
        sp = subgroup_results[n]["partial_spearman"]["shuffle_p"]
        sig_parts.append(f"{n}(rho={sig_rhos[n]:+.4f}, p={sp:.4f})")
    reason = "no complementary directions" if n_sig >= 2 else "need 2+ for full PASS"
    verdict_detail = (
        f"Partial evidence for hazard sub-group migration: {n_sig} sub-group(s) "
        f"significant ({', '.join(sig_parts)}), but {reason}."
    )
else:
    verdict = "FAIL"
    pval_parts = []
    for n in SUBGROUP_NAMES:
        sp = subgroup_results[n]["partial_spearman"]["shuffle_p"]
        pval_parts.append(f"{n}={sp:.4f}")
    verdict_detail = (
        f"No hazard sub-group fraction showed significant migration "
        f"(Bonferroni alpha={BONFERRONI_ALPHA}). "
        f"Shuffle p-values: {', '.join(pval_parts)}."
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
    "test": "02_hazard_subgroup_migration",
    "phase": "RISK_PROFILE_MIGRATION",
    "verdict": verdict,
    "verdict_detail": verdict_detail,
    "counts": {
        "total_paragraphs": len(paragraphs),
        "big_paragraphs": len(big_paragraphs),
        "total_body_lines": int(total_body_lines),
        "excluded_zero_hazard": int(excluded_lines),
        "exclusion_rate": round(exclusion_rate, 6),
        "body_lines_analyzed": int(n_body_lines_total),
        "unique_paragraphs_analyzed": int(len(unique_pars)),
    },
    "subgroups": subgroup_results,
    "significant_subgroups": sig_subgroups,
    "complementary_directions": complementary,
    "parameters": {
        "min_paragraph_lines": 5,
        "n_shuffles": N_SHUFFLES,
        "random_seed": 42,
        "bonferroni_alpha": BONFERRONI_ALPHA,
        "base_alpha": 0.01,
        "n_tests": 4,
        "hazard_classes": sorted(list(HAZARD_CLASSES)),
        "subgroup_definitions": {
            "fl_haz": sorted(list(FL_HAZ)),
            "en_chsh": sorted(list(EN_CHSH)),
            "fq_conn": sorted(list(FQ_CONN)),
            "fq_closer": sorted(list(FQ_CLOSER)),
        },
    },
}

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {RESULTS_PATH}")
