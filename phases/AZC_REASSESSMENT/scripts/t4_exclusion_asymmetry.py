"""
T4: Exclusion Asymmetry

H0: A->B filtering is symmetric (mutual vocabulary restriction)
H1: Specific A configurations exclude specific B instruction classes asymmetrically

Method: Test whether certain A folio types exclude specific B token roles/classes
Threshold: McNemar test p < 0.01 for class-specific exclusion

This tests whether filtering is "smart" (content-aware) or just size-based.
"""

import sys, json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=== T4: EXCLUSION ASYMMETRY ===\n")

# Load classified token set and roles
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)

token_to_class = ctm.get('token_to_class', {})
token_to_role = ctm.get('token_to_role', {})
classified_tokens = set(token_to_class.keys())

print(f"Loaded {len(classified_tokens)} classified tokens")
print(f"Roles: {Counter(token_to_role.values()).most_common()}")

# Build A folio component pools
print("\nBuilding A folio pools...")
a_folio_components = {}
a_folio_section = {}

a_data = defaultdict(list)
for t in tx.currier_a():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    a_data[t.folio].append(w)
    if t.folio not in a_folio_section:
        a_folio_section[t.folio] = t.section

for fol in sorted(a_data.keys()):
    mids, prefs, sufs = set(), set(), set()
    for w in a_data[fol]:
        m = morph.extract(w)
        if m.middle:
            mids.add(m.middle)
            if m.prefix:
                prefs.add(m.prefix)
            if m.suffix:
                sufs.add(m.suffix)
    a_folio_components[fol] = (mids, prefs, sufs)

a_folios = sorted(a_folio_components.keys())
print(f"  {len(a_folios)} A folios")

# Collect B tokens with their roles
b_tokens_with_role = []
for t in tx.currier_b():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    role = token_to_role.get(w, 'HT')  # HT = Human Track = unclassified
    b_tokens_with_role.append({
        'word': w,
        'folio': t.folio,
        'role': role,
        'morph': morph.extract(w),
    })

print(f"  {len(b_tokens_with_role)} B tokens with role assignment")

# Define role groups
roles = ['CORE_CONTROL', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR', 'ENERGY_OPERATOR', 'AUXILIARY', 'HT']

# For each A folio, compute survival rate per role
print("\nComputing role survival rates per A folio...")

def token_survives(tok_data, a_mids, a_prefs, a_sufs):
    """Check if token survives C502.a filter."""
    mo = tok_data['morph']
    if not mo.middle or mo.middle not in a_mids:
        return False
    if mo.prefix and mo.prefix not in a_prefs:
        return False
    if mo.suffix and mo.suffix not in a_sufs:
        return False
    return True

# Pre-group B tokens by role
b_by_role = defaultdict(list)
for tok in b_tokens_with_role:
    b_by_role[tok['role']].append(tok)

role_counts = {role: len(b_by_role[role]) for role in roles}
print(f"B tokens by role: {role_counts}")

# Compute survival matrix: A folio x role -> survival rate
survival_matrix = np.zeros((len(a_folios), len(roles)))

for i, a_fol in enumerate(a_folios):
    a_m, a_p, a_s = a_folio_components[a_fol]
    for j, role in enumerate(roles):
        tokens = b_by_role[role]
        if len(tokens) == 0:
            survival_matrix[i, j] = 0
            continue
        survived = sum(1 for tok in tokens if token_survives(tok, a_m, a_p, a_s))
        survival_matrix[i, j] = survived / len(tokens)

# Analyze: do small-pool A folios differentially exclude certain roles?
print("\n=== ROLE SURVIVAL BY A FOLIO POOL SIZE ===\n")

pool_sizes = np.array([len(a_folio_components[f][0]) for f in a_folios])

# Split A folios into tertiles by pool size
tertile_thresholds = np.percentile(pool_sizes, [33, 67])
small_mask = pool_sizes <= tertile_thresholds[0]
medium_mask = (pool_sizes > tertile_thresholds[0]) & (pool_sizes <= tertile_thresholds[1])
large_mask = pool_sizes > tertile_thresholds[1]

print(f"Pool size tertiles: small <= {tertile_thresholds[0]:.0f}, medium <= {tertile_thresholds[1]:.0f}, large > {tertile_thresholds[1]:.0f}")
print(f"Counts: small={small_mask.sum()}, medium={medium_mask.sum()}, large={large_mask.sum()}")

print(f"\n{'Role':<20s} {'Small':>10s} {'Medium':>10s} {'Large':>10s} {'Diff S-L':>10s}")
print("-" * 65)

role_asymmetries = {}
for j, role in enumerate(roles):
    small_rate = survival_matrix[small_mask, j].mean()
    medium_rate = survival_matrix[medium_mask, j].mean()
    large_rate = survival_matrix[large_mask, j].mean()
    diff = small_rate - large_rate

    print(f"{role:<20s} {small_rate*100:>9.1f}% {medium_rate*100:>9.1f}% {large_rate*100:>9.1f}% {diff*100:>+9.1f}pp")

    role_asymmetries[role] = {
        'small_rate': float(small_rate),
        'medium_rate': float(medium_rate),
        'large_rate': float(large_rate),
        'small_large_diff': float(diff),
    }

# Test: do different roles show different exclusion gradients?
# If routing is "smart", CORE_CONTROL should survive better than AUXILIARY under small pools
print("\n=== ROLE EXCLUSION GRADIENT TEST ===\n")

# Compute correlation of pool size with survival rate for each role
role_correlations = {}
for j, role in enumerate(roles):
    surv_col = survival_matrix[:, j]
    r, p = stats.spearmanr(pool_sizes, surv_col)
    role_correlations[role] = {'rho': float(r), 'p': float(p)}
    print(f"{role:<20s}: pool-survival rho = {r:.3f}, p = {p:.2e}")

# Test for differential gradients: is CORE_CONTROL gradient different from AUXILIARY?
if 'CORE_CONTROL' in role_correlations and 'AUXILIARY' in role_correlations:
    cc_rho = role_correlations['CORE_CONTROL']['rho']
    aux_rho = role_correlations['AUXILIARY']['rho']

    # Fisher z-transform to compare correlations
    def fisher_z(r):
        return 0.5 * np.log((1 + r) / (1 - r)) if abs(r) < 1 else 0

    z_cc = fisher_z(cc_rho)
    z_aux = fisher_z(aux_rho)
    se = np.sqrt(1/(len(a_folios)-3) + 1/(len(a_folios)-3))
    z_diff = (z_cc - z_aux) / se
    p_diff = 2 * (1 - stats.norm.cdf(abs(z_diff)))

    print(f"\nCORE_CONTROL vs AUXILIARY gradient comparison:")
    print(f"  CORE_CONTROL rho: {cc_rho:.3f}")
    print(f"  AUXILIARY rho: {aux_rho:.3f}")
    print(f"  z-test: z = {z_diff:.2f}, p = {p_diff:.4f}")

    gradient_diff_p = p_diff
else:
    gradient_diff_p = 1.0

# Test: McNemar-like test for paired exclusion
# For each A folio, does excluding CORE_CONTROL predict excluding AUXILIARY?
print("\n=== PAIRED EXCLUSION ANALYSIS ===\n")

# For each A folio, classify as "excludes most CORE_CONTROL" or not
cc_survival = survival_matrix[:, roles.index('CORE_CONTROL')] if 'CORE_CONTROL' in roles else np.zeros(len(a_folios))
aux_survival = survival_matrix[:, roles.index('AUXILIARY')] if 'AUXILIARY' in roles else np.zeros(len(a_folios))

# Binarize at median
cc_low = cc_survival < np.median(cc_survival)
aux_low = aux_survival < np.median(aux_survival)

# 2x2 contingency
a_both_low = (cc_low & aux_low).sum()
b_cc_low_aux_high = (cc_low & ~aux_low).sum()
c_cc_high_aux_low = (~cc_low & aux_low).sum()
d_both_high = (~cc_low & ~aux_low).sum()

print(f"2x2 table (CORE_CONTROL low/high x AUXILIARY low/high):")
print(f"  Both low: {a_both_low}")
print(f"  CC low, AUX high: {b_cc_low_aux_high}")
print(f"  CC high, AUX low: {c_cc_high_aux_low}")
print(f"  Both high: {d_both_high}")

# McNemar test
if b_cc_low_aux_high + c_cc_high_aux_low > 0:
    # McNemar statistic
    mcnemar_stat = (abs(b_cc_low_aux_high - c_cc_high_aux_low) - 1)**2 / (b_cc_low_aux_high + c_cc_high_aux_low)
    mcnemar_p = 1 - stats.chi2.cdf(mcnemar_stat, 1)
    print(f"\nMcNemar test: chi2 = {mcnemar_stat:.2f}, p = {mcnemar_p:.4f}")
else:
    mcnemar_p = 1.0
    print("\nInsufficient discordant pairs for McNemar test")

# If McNemar is significant, it means exclusion is NOT symmetric across roles
# (i.e., some A folios exclude CORE_CONTROL without excluding AUXILIARY or vice versa)

# Verdict
threshold_p = 0.01

if mcnemar_p < threshold_p:
    verdict = "ASYMMETRIC_EXCLUSION"
    explanation = f"McNemar p={mcnemar_p:.4f} < 0.01: role exclusion is asymmetric across A folios"
elif gradient_diff_p < threshold_p:
    verdict = "DIFFERENTIAL_GRADIENT"
    explanation = f"Gradient diff p={gradient_diff_p:.4f} < 0.01: different roles have different exclusion gradients"
else:
    verdict = "SYMMETRIC_EXCLUSION"
    explanation = f"p-values > 0.01: exclusion patterns are symmetric (size-driven, not role-aware)"

print(f"\n=== VERDICT: {verdict} ===")
print(f"  {explanation}")

# Save results
results = {
    'test': 'T4_exclusion_asymmetry',
    'role_counts': role_counts,
    'pool_tertiles': {
        'thresholds': tertile_thresholds.tolist(),
        'small_n': int(small_mask.sum()),
        'medium_n': int(medium_mask.sum()),
        'large_n': int(large_mask.sum()),
    },
    'role_asymmetries': role_asymmetries,
    'role_correlations': role_correlations,
    'gradient_comparison': {
        'p_value': float(gradient_diff_p),
    },
    'mcnemar_test': {
        'contingency': [[int(a_both_low), int(b_cc_low_aux_high)],
                        [int(c_cc_high_aux_low), int(d_both_high)]],
        'p_value': float(mcnemar_p),
    },
    'threshold_p': threshold_p,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / 't4_exclusion_asymmetry.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
