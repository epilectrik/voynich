"""
HT_RECONCILIATION - Script 4: HT Coverage Impact
T6: Operational-only A-B coverage (does removing HT change routing?)
T7: HT concentration by B folio

Requires T1 PASS.
"""
import json, sys
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# --- Load classified set ---
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

# --- Build per-folio inventories ---
# A folios: PP pool (MIDDLE, PREFIX, SUFFIX sets)
a_folio_middles = defaultdict(set)
a_folio_prefixes = defaultdict(set)
a_folio_suffixes = defaultdict(set)

for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        a_folio_middles[token.folio].add(m.middle)
    if m.prefix:
        a_folio_prefixes[token.folio].add(m.prefix)
    if m.suffix:
        a_folio_suffixes[token.folio].add(m.suffix)

# B folios: full vocabulary and classified-only vocabulary
b_folio_tokens_full = defaultdict(set)      # All B token types
b_folio_tokens_cl = defaultdict(set)        # Classified-only B token types
b_folio_tokens_ht = defaultdict(set)        # HT-only B token types
b_folio_occ = defaultdict(lambda: Counter())  # word -> count per folio
b_folio_ht_occ = defaultdict(int)
b_folio_total_occ = defaultdict(int)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    folio = token.folio
    b_folio_tokens_full[folio].add(w)
    b_folio_occ[folio][w] += 1
    b_folio_total_occ[folio] += 1

    if w in classified_tokens:
        b_folio_tokens_cl[folio].add(w)
    else:
        b_folio_tokens_ht[folio].add(w)
        b_folio_ht_occ[folio] += 1

a_folios = sorted(a_folio_middles.keys())
b_folios = sorted(b_folio_tokens_full.keys())

print(f"A folios: {len(a_folios)}")
print(f"B folios: {len(b_folios)}")


def compute_coverage(a_folio, b_folio_vocab, morph_obj):
    """
    Compute fraction of B vocabulary legal under A folio.
    C502.a: legal if MIDDLE in A pool AND PREFIX (if any) shared AND SUFFIX (if any) shared.
    """
    a_mids = a_folio_middles[a_folio]
    a_pfxs = a_folio_prefixes[a_folio]
    a_sfxs = a_folio_suffixes[a_folio]

    legal = 0
    total = len(b_folio_vocab)
    if total == 0:
        return 0.0

    for w in b_folio_vocab:
        m = morph_obj.extract(w)
        if not m.middle:
            continue
        if m.middle not in a_mids:
            continue
        if m.prefix and m.prefix not in a_pfxs:
            continue
        if m.suffix and m.suffix not in a_sfxs:
            continue
        legal += 1

    return legal / total


# ===================================================================
# T6: Operational-Only A-B Coverage
# ===================================================================
print()
print("=== T6: Operational-Only A-B Coverage ===")

# Pre-extract morphology for all B tokens to avoid repeated extraction
b_token_morph = {}
for folio in b_folios:
    for w in b_folio_tokens_full[folio]:
        if w not in b_token_morph:
            b_token_morph[w] = morph.extract(w)

# Compute coverage matrices: full and classified-only
# Coverage = fraction of B folio vocabulary legal under A folio
full_matrix = np.zeros((len(a_folios), len(b_folios)))
cl_matrix = np.zeros((len(a_folios), len(b_folios)))

for ai, af in enumerate(a_folios):
    a_mids = a_folio_middles[af]
    a_pfxs = a_folio_prefixes[af]
    a_sfxs = a_folio_suffixes[af]

    for bi, bf in enumerate(b_folios):
        # Full vocabulary
        full_vocab = b_folio_tokens_full[bf]
        full_legal = 0
        for w in full_vocab:
            m = b_token_morph[w]
            if not m.middle or m.middle not in a_mids:
                continue
            if m.prefix and m.prefix not in a_pfxs:
                continue
            if m.suffix and m.suffix not in a_sfxs:
                continue
            full_legal += 1
        full_matrix[ai, bi] = full_legal / len(full_vocab) if full_vocab else 0

        # Classified-only vocabulary
        cl_vocab = b_folio_tokens_cl[bf]
        cl_legal = 0
        for w in cl_vocab:
            m = b_token_morph[w]
            if not m.middle or m.middle not in a_mids:
                continue
            if m.prefix and m.prefix not in a_pfxs:
                continue
            if m.suffix and m.suffix not in a_sfxs:
                continue
            cl_legal += 1
        cl_matrix[ai, bi] = cl_legal / len(cl_vocab) if cl_vocab else 0

# Compute summary metrics for both
def coverage_metrics(matrix, a_fols, b_fols):
    mean_cov = np.mean(matrix)

    # Variance decomposition: A-axis vs B-axis
    a_means = np.mean(matrix, axis=1)  # mean per A folio
    b_means = np.mean(matrix, axis=0)  # mean per B folio
    total_var = np.var(matrix)
    a_var = np.var(a_means)
    b_var = np.var(b_means)
    a_share = a_var / total_var * 100 if total_var > 0 else 0
    b_share = b_var / total_var * 100 if total_var > 0 else 0

    # Best-match lift: for each B folio, max coverage / mean coverage
    lifts = []
    for bi in range(len(b_fols)):
        col = matrix[:, bi]
        if np.mean(col) > 0:
            lifts.append(np.max(col) / np.mean(col))
    mean_lift = np.mean(lifts) if lifts else 0

    return {
        'mean_coverage': round(float(mean_cov), 6),
        'a_var_share_pct': round(float(a_share), 2),
        'b_var_share_pct': round(float(b_share), 2),
        'mean_lift': round(float(mean_lift), 4),
        'total_var': round(float(total_var), 8),
    }

full_metrics = coverage_metrics(full_matrix, a_folios, b_folios)
cl_metrics = coverage_metrics(cl_matrix, a_folios, b_folios)

print(f"\nFull vocabulary coverage:")
for k, v in full_metrics.items():
    print(f"  {k}: {v}")

print(f"\nClassified-only coverage:")
for k, v in cl_metrics.items():
    print(f"  {k}: {v}")

# Compute deltas
deltas = {}
for key in full_metrics:
    f_val = full_metrics[key]
    c_val = cl_metrics[key]
    if f_val != 0:
        delta_pct = abs(f_val - c_val) / abs(f_val) * 100
    else:
        delta_pct = 0 if c_val == 0 else 100
    deltas[key] = round(delta_pct, 2)

print(f"\nDeltas (|full - cl| / |full| * 100%):")
for k, v in deltas.items():
    print(f"  {k}: {v}%")

# Per-B-folio coverage correlation
full_b_means = np.mean(full_matrix, axis=0)
cl_b_means = np.mean(cl_matrix, axis=0)
if len(full_b_means) > 2:
    corr, corr_p = stats.pearsonr(full_b_means, cl_b_means)
    print(f"\nPer-B-folio mean coverage correlation: r={corr:.4f}, p={corr_p:.2e}")
else:
    corr, corr_p = 0, 1

# T6 verdict
max_delta = max(deltas.values())
if max_delta < 5:
    t6_verdict = "NEGLIGIBLE"
    t6_detail = f"Max delta {max_delta:.1f}% < 5% - HT removal negligible (confirms C404)"
elif max_delta < 20:
    t6_verdict = "MINOR"
    t6_detail = f"Max delta {max_delta:.1f}% between 5-20% - modest effect"
else:
    t6_verdict = "MATERIAL"
    t6_detail = f"Max delta {max_delta:.1f}% > 20% - HT materially affects routing (review C404)"

print(f"\nT6 VERDICT: {t6_verdict} - {t6_detail}")

# ===================================================================
# T7: HT Concentration by B Folio
# ===================================================================
print()
print("=== T7: HT Concentration by B Folio ===")

# Per-folio HT density
folio_ht_density = {}
for bf in b_folios:
    total = b_folio_total_occ[bf]
    ht = b_folio_ht_occ[bf]
    folio_ht_density[bf] = ht / total if total > 0 else 0

densities = np.array([folio_ht_density[bf] for bf in b_folios])
global_ht_density = sum(b_folio_ht_occ.values()) / sum(b_folio_total_occ.values())

print(f"Global HT density: {global_ht_density*100:.1f}%")
print(f"Per-folio HT density stats:")
print(f"  Mean: {np.mean(densities)*100:.1f}%")
print(f"  Std: {np.std(densities)*100:.1f}%")
print(f"  Min: {np.min(densities)*100:.1f}%")
print(f"  Max: {np.max(densities)*100:.1f}%")
print(f"  Median: {np.median(densities)*100:.1f}%")
q1, q3 = np.percentile(densities, [25, 75])
print(f"  IQR: [{q1*100:.1f}%, {q3*100:.1f}%]")

# Chi-squared goodness-of-fit: observed vs uniform density
# Expected: each folio has global_ht_density fraction of its tokens as HT
observed_ht = np.array([b_folio_ht_occ[bf] for bf in b_folios])
expected_ht = np.array([b_folio_total_occ[bf] * global_ht_density for bf in b_folios])

# Filter out folios with very small expected counts
mask = expected_ht >= 5
if np.sum(mask) > 2:
    chi2_gof, gof_p = stats.chisquare(observed_ht[mask], expected_ht[mask])
    print(f"\nChi-squared goodness-of-fit (uniform HT density):")
    print(f"  Folios tested: {np.sum(mask)}")
    print(f"  Chi2 = {chi2_gof:.2f}, p = {gof_p:.2e}")
else:
    chi2_gof, gof_p = 0, 1
    print("\nInsufficient data for chi-squared test")

# Correlations with folio properties
folio_total_tokens = np.array([b_folio_total_occ[bf] for bf in b_folios])
folio_cl_vocab = np.array([len(b_folio_tokens_cl[bf]) for bf in b_folios])

# Correlation: HT density vs folio size
if len(densities) > 2:
    r_size, p_size = stats.pearsonr(densities, folio_total_tokens)
    print(f"\nHT density vs folio size: r={r_size:.4f}, p={p_size:.4f}")
else:
    r_size, p_size = 0, 1

# Correlation: HT density vs classified vocabulary size
if len(densities) > 2:
    r_vocab, p_vocab = stats.pearsonr(densities, folio_cl_vocab)
    print(f"HT density vs classified vocab size: r={r_vocab:.4f}, p={p_vocab:.4f}")
else:
    r_vocab, p_vocab = 0, 1

# Correlation: HT density vs mean coverage from full matrix
if len(densities) > 2:
    r_cov, p_cov = stats.pearsonr(densities, full_b_means)
    print(f"HT density vs mean coverage: r={r_cov:.4f}, p={p_cov:.4f}")
else:
    r_cov, p_cov = 0, 1

# Top/bottom 5 folios by HT density
sorted_folios = sorted(b_folios, key=lambda bf: folio_ht_density[bf])
print(f"\nLowest HT density folios:")
for bf in sorted_folios[:5]:
    print(f"  {bf}: {folio_ht_density[bf]*100:.1f}% (n={b_folio_total_occ[bf]})")
print(f"\nHighest HT density folios:")
for bf in sorted_folios[-5:]:
    print(f"  {bf}: {folio_ht_density[bf]*100:.1f}% (n={b_folio_total_occ[bf]})")

# T7 verdict
if gof_p > 0.05:
    t7_verdict = "UNIFORM"
    t7_detail = f"Chi2={chi2_gof:.2f}, p={gof_p:.4f} - HT uniformly distributed across folios"
elif gof_p < 0.01:
    t7_verdict = "STRUCTURED"
    t7_detail = f"Chi2={chi2_gof:.2f}, p={gof_p:.2e} - HT density varies significantly by folio"
    if abs(r_cov) > 0.3 and p_cov < 0.05:
        if r_cov < 0:
            t7_detail += " | COMPENSATORY: HT fills coverage gaps (negative correlation with coverage)"
        else:
            t7_detail += " | CORRELATED: HT higher where coverage higher"
else:
    t7_verdict = "MARGINAL"
    t7_detail = f"Chi2={chi2_gof:.2f}, p={gof_p:.4f} - marginal variation"

print(f"\nT7 VERDICT: {t7_verdict} - {t7_detail}")

# --- Save results ---
results = {
    "metadata": {
        "phase": "HT_RECONCILIATION",
        "script": "ht_coverage_impact.py",
        "tests": ["T6", "T7"],
        "n_a_folios": len(a_folios),
        "n_b_folios": len(b_folios)
    },
    "T6_operational_coverage": {
        "full_metrics": full_metrics,
        "classified_only_metrics": cl_metrics,
        "deltas_pct": deltas,
        "max_delta_pct": max_delta,
        "per_b_folio_correlation": {
            "r": round(float(corr), 6),
            "p": float(corr_p)
        },
        "verdict": t6_verdict,
        "detail": t6_detail
    },
    "T7_ht_folio_distribution": {
        "global_ht_density": round(float(global_ht_density), 6),
        "density_stats": {
            "mean": round(float(np.mean(densities)), 6),
            "std": round(float(np.std(densities)), 6),
            "min": round(float(np.min(densities)), 6),
            "max": round(float(np.max(densities)), 6),
            "median": round(float(np.median(densities)), 6),
            "q1": round(float(q1), 6),
            "q3": round(float(q3), 6)
        },
        "chi_squared_gof": {
            "chi2": round(float(chi2_gof), 4),
            "p": float(gof_p),
            "n_folios_tested": int(np.sum(mask))
        },
        "correlations": {
            "density_vs_size": {"r": round(float(r_size), 6), "p": round(float(p_size), 6)},
            "density_vs_cl_vocab": {"r": round(float(r_vocab), 6), "p": round(float(p_vocab), 6)},
            "density_vs_coverage": {"r": round(float(r_cov), 6), "p": round(float(p_cov), 6)}
        },
        "lowest_density": {bf: round(folio_ht_density[bf], 6) for bf in sorted_folios[:5]},
        "highest_density": {bf: round(folio_ht_density[bf], 6) for bf in sorted_folios[-5:]},
        "verdict": t7_verdict,
        "detail": t7_detail
    }
}

out_path = PROJECT_ROOT / 'phases' / 'HT_RECONCILIATION' / 'results' / 'ht_coverage_impact.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print()
print(f"Results saved to {out_path}")
