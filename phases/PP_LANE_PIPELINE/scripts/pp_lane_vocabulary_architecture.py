"""
PP_LANE_PIPELINE Script 1: PP Lane Vocabulary Architecture
Tests 1-3: Character census, AZC filtering asymmetry, discriminator pathway analysis.

Tests whether the PP vocabulary landscape has lane-structured character composition,
whether AZC filtering modifies that composition, and whether C646 discriminators
concentrate in one pipeline pathway.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from math import log, exp, sqrt

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

# ============================================================
# SECTION 1: Load & Prepare
# ============================================================

print("=" * 70)
print("PP_LANE_PIPELINE Script 1: PP Lane Vocabulary Architecture")
print("=" * 70)

# 1. PP/RI MIDDLE lists
with open(PROJECT_ROOT / 'phases/A_INTERNAL_STRATIFICATION/results/middle_classes_v2_backup.json') as f:
    mid_classes = json.load(f)
pp_set = set(mid_classes['a_shared_middles'])
ri_set = set(mid_classes['a_exclusive_middles'])
print(f"Loaded PP={len(pp_set)}, RI={len(ri_set)} MIDDLEs")

# 2. AZC-Med / B-Native split
with open(PROJECT_ROOT / 'phases/A_TO_B_ROLE_PROJECTION/results/pp_role_foundation.json') as f:
    role_data = json.load(f)
azc_med_set = set(role_data['azc_split']['azc_mediated'])
b_native_set = set(role_data['azc_split']['b_native'])
print(f"AZC-Med={len(azc_med_set)}, B-Native={len(b_native_set)}")

# 3. Material class per PP MIDDLE
with open(PROJECT_ROOT / 'phases/PP_CLASSIFICATION/results/pp_classification.json') as f:
    pp_class_data = json.load(f)
pp_material = {}
for m, d in pp_class_data['pp_classification'].items():
    pp_material[m] = d['material_class']

# 4. C646 discrimination results
with open(PROJECT_ROOT / 'phases/LANE_CHANGE_HOLD_ANALYSIS/results/lane_pp_discrimination.json') as f:
    disc_data = json.load(f)

# 5. EN census
with open(PROJECT_ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_census = json.load(f)
qo_classes = set(en_census['prefix_families']['QO'])
chsh_classes = set(en_census['prefix_families']['CH_SH'])
all_en_classes = qo_classes | chsh_classes
en_exclusive_middles = set(en_census['middle_inventory']['en_exclusive_middles'])

# 6. Class token map
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)
token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
class_to_role[17] = 'CORE_CONTROL'  # C560/C581

# 7. Transcript + Morphology
tx = Transcript()
morph = Morphology()


# ---- Lane prediction function (C649 rule) ----
def lane_prediction(middle):
    """C649 initial character rule: k/t/p -> QO, e/o -> CHSH, else neutral."""
    if not middle:
        return 'neutral'
    c = middle[0]
    if c in ('k', 't', 'p'):
        return 'QO'
    elif c in ('e', 'o'):
        return 'CHSH'
    return 'neutral'


# ---- Build B-side frequency map (C640 control) ----
print("\nBuilding B-side PP frequency map...")
b_middle_freq = Counter()
for token in tx.currier_b():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    if m.middle and m.middle in pp_set:
        b_middle_freq[m.middle] += 1
print(f"  {len(b_middle_freq)} PP MIDDLEs found in B with total {sum(b_middle_freq.values())} tokens")


# ---- Pre-classify all PP MIDDLEs ----
pp_lane_pred = {mid: lane_prediction(mid) for mid in pp_set}


# ---- Helper: safe chi-squared ----
def safe_chi2(table):
    """Chi-squared test with Fisher's exact fallback for 2x2 tables.
    table: list of lists [[a,b],[c,d],...]
    Returns (stat, p, method, cramers_v)
    """
    from scipy import stats as sp_stats

    rows = len(table)
    cols = len(table[0])
    total = sum(sum(row) for row in table)
    if total == 0:
        return (0.0, 1.0, 'empty', 0.0)

    # Check expected values
    row_sums = [sum(row) for row in table]
    col_sums = [sum(table[r][c] for r in range(rows)) for c in range(cols)]
    min_expected = float('inf')
    for r in range(rows):
        for c in range(cols):
            exp_val = row_sums[r] * col_sums[c] / total if total > 0 else 0
            if exp_val < min_expected:
                min_expected = exp_val

    # 2x2 with small expected -> Fisher's exact
    if rows == 2 and cols == 2 and min_expected < 5:
        odds, p = sp_stats.fisher_exact(table)
        v = cramers_v_from_table(table)
        return (odds, p, 'fisher_exact', v)

    # Chi-squared
    chi2, p, dof, expected = sp_stats.chi2_contingency(table, correction=(rows == 2 and cols == 2))
    v = cramers_v_from_table(table)
    return (chi2, p, 'chi2_yates' if (rows == 2 and cols == 2) else 'chi2', v)


def cramers_v_from_table(table):
    """Compute Cramer's V from contingency table."""
    from scipy import stats as sp_stats
    rows = len(table)
    cols = len(table[0])
    total = sum(sum(row) for row in table)
    if total == 0:
        return 0.0
    try:
        chi2, _, _, _ = sp_stats.chi2_contingency(table, correction=False)
        k = min(rows, cols)
        if k <= 1:
            return 0.0
        return sqrt(chi2 / (total * (k - 1)))
    except Exception:
        return 0.0


def odds_ratio_ci(a, b, c, d, alpha=0.05):
    """Compute odds ratio and 95% CI from 2x2 table [[a,b],[c,d]]."""
    # Add continuity correction if any cell is 0
    if 0 in (a, b, c, d):
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    OR = (a * d) / (b * c)
    log_OR = log(OR)
    se = sqrt(1.0/a + 1.0/b + 1.0/c + 1.0/d)
    z = 1.96
    ci_low = exp(log_OR - z * se)
    ci_high = exp(log_OR + z * se)
    return OR, ci_low, ci_high


# ============================================================
# SECTION 2: Test 1 -- PP Character Census
# ============================================================

print("\n" + "=" * 70)
print("TEST 1: PP Character Census")
print("=" * 70)

from scipy import stats as sp_stats

# --- Type-level census ---
type_counts = Counter(pp_lane_pred[mid] for mid in pp_set)
n_qo_type = type_counts['QO']
n_chsh_type = type_counts['CHSH']
n_neutral_type = type_counts['neutral']
n_lane_pred_type = n_qo_type + n_chsh_type
qo_frac_type = n_qo_type / n_lane_pred_type if n_lane_pred_type > 0 else 0

binom_result_type = sp_stats.binomtest(n_qo_type, n_lane_pred_type, 0.5)

print(f"Type-level: QO={n_qo_type}, CHSH={n_chsh_type}, Neutral={n_neutral_type}")
print(f"  QO fraction (of lane-predicting): {qo_frac_type:.3f}")
print(f"  Binomial test vs 0.5: p={binom_result_type.pvalue:.2e}")

# --- Token-level census ---
tok_qo = sum(b_middle_freq.get(mid, 0) for mid in pp_set if pp_lane_pred[mid] == 'QO')
tok_chsh = sum(b_middle_freq.get(mid, 0) for mid in pp_set if pp_lane_pred[mid] == 'CHSH')
tok_neutral = sum(b_middle_freq.get(mid, 0) for mid in pp_set if pp_lane_pred[mid] == 'neutral')
tok_lane_pred = tok_qo + tok_chsh
qo_frac_tok = tok_qo / tok_lane_pred if tok_lane_pred > 0 else 0

binom_result_tok = sp_stats.binomtest(tok_qo, tok_lane_pred, 0.5)

print(f"\nToken-level: QO={tok_qo}, CHSH={tok_chsh}, Neutral={tok_neutral}")
print(f"  QO fraction (of lane-predicting): {qo_frac_tok:.3f}")
print(f"  Binomial test vs 0.5: p={binom_result_tok.pvalue:.2e}")

# --- By material class (type-level, lane-predicting only) ---
material_x_lane = defaultdict(lambda: {'QO': 0, 'CHSH': 0})
for mid in pp_set:
    pred = pp_lane_pred[mid]
    if pred == 'neutral':
        continue
    mat = pp_material.get(mid, 'UNKNOWN')
    material_x_lane[mat][pred] += 1

print("\nBy material class (type-level, lane-predicting only):")
mat_table_rows = []
mat_labels = sorted(material_x_lane.keys())
for mat in mat_labels:
    qo = material_x_lane[mat]['QO']
    chsh = material_x_lane[mat]['CHSH']
    frac = qo / (qo + chsh) if (qo + chsh) > 0 else 0
    print(f"  {mat}: QO={qo}, CHSH={chsh}, QO_frac={frac:.3f}")
    mat_table_rows.append([qo, chsh])

# Chi-squared: material x lane
if len(mat_table_rows) >= 2:
    mat_chi2, mat_p, mat_method, mat_v = safe_chi2(mat_table_rows)
    print(f"  Material x Lane: {mat_method} stat={mat_chi2:.3f}, p={mat_p:.4f}, V={mat_v:.3f}")
else:
    mat_chi2, mat_p, mat_method, mat_v = 0.0, 1.0, 'insufficient', 0.0

# --- By pathway (type-level, lane-predicting only) ---
pathway_x_lane = {'AZC-Med': {'QO': 0, 'CHSH': 0}, 'B-Native': {'QO': 0, 'CHSH': 0}}
for mid in pp_set:
    pred = pp_lane_pred[mid]
    if pred == 'neutral':
        continue
    if mid in azc_med_set:
        pathway_x_lane['AZC-Med'][pred] += 1
    elif mid in b_native_set:
        pathway_x_lane['B-Native'][pred] += 1

print("\nBy pathway (type-level, lane-predicting only):")
for pw in ['AZC-Med', 'B-Native']:
    qo = pathway_x_lane[pw]['QO']
    chsh = pathway_x_lane[pw]['CHSH']
    frac = qo / (qo + chsh) if (qo + chsh) > 0 else 0
    print(f"  {pw}: QO={qo}, CHSH={chsh}, QO_frac={frac:.3f}")

# Build results
test1_results = {
    'total_pp': len(pp_set),
    'type_level': {
        'qo_predicting': n_qo_type,
        'chsh_predicting': n_chsh_type,
        'neutral': n_neutral_type,
        'qo_fraction_of_lane_predicting': round(qo_frac_type, 4),
        'binom_p_vs_equal': binom_result_type.pvalue,
    },
    'token_level': {
        'qo_tokens': tok_qo,
        'chsh_tokens': tok_chsh,
        'neutral_tokens': tok_neutral,
        'qo_fraction_of_lane_predicting': round(qo_frac_tok, 4),
        'binom_p_vs_equal': binom_result_tok.pvalue,
    },
    'by_material': {
        mat: {
            'qo': material_x_lane[mat]['QO'],
            'chsh': material_x_lane[mat]['CHSH'],
            'qo_frac': round(material_x_lane[mat]['QO'] / max(1, material_x_lane[mat]['QO'] + material_x_lane[mat]['CHSH']), 4)
        }
        for mat in mat_labels
    },
    'material_x_lane_test': {
        'method': mat_method,
        'stat': round(mat_chi2, 4),
        'p': round(mat_p, 6),
        'cramers_v': round(mat_v, 4),
    },
    'by_pathway': {
        pw: {
            'qo': pathway_x_lane[pw]['QO'],
            'chsh': pathway_x_lane[pw]['CHSH'],
            'qo_frac': round(pathway_x_lane[pw]['QO'] / max(1, pathway_x_lane[pw]['QO'] + pathway_x_lane[pw]['CHSH']), 4)
        }
        for pw in ['AZC-Med', 'B-Native']
    },
}

# ============================================================
# SECTION 3: Test 2 -- AZC Lane Filtering Asymmetry
# ============================================================

print("\n" + "=" * 70)
print("TEST 2: AZC Lane Filtering Asymmetry")
print("=" * 70)

# --- Type-level 2x2: pathway x lane ---
a_qo = pathway_x_lane['AZC-Med']['QO']
a_chsh = pathway_x_lane['AZC-Med']['CHSH']
n_qo_bn = pathway_x_lane['B-Native']['QO']
n_chsh_bn = pathway_x_lane['B-Native']['CHSH']

type_table = [[a_qo, a_chsh], [n_qo_bn, n_chsh_bn]]
type_chi2, type_p, type_method, type_v = safe_chi2(type_table)
type_or, type_or_lo, type_or_hi = odds_ratio_ci(a_qo, a_chsh, n_qo_bn, n_chsh_bn)

print(f"Type-level 2x2:")
print(f"  AZC-Med:  QO={a_qo}, CHSH={a_chsh}")
print(f"  B-Native: QO={n_qo_bn}, CHSH={n_chsh_bn}")
print(f"  {type_method}: stat={type_chi2:.3f}, p={type_p:.4f}, V={type_v:.3f}")
print(f"  OR={type_or:.3f} [{type_or_lo:.3f}, {type_or_hi:.3f}]")

# --- Token-level 2x2 ---
tok_azc_qo = sum(b_middle_freq.get(mid, 0) for mid in azc_med_set if pp_lane_pred.get(mid) == 'QO')
tok_azc_chsh = sum(b_middle_freq.get(mid, 0) for mid in azc_med_set if pp_lane_pred.get(mid) == 'CHSH')
tok_bn_qo = sum(b_middle_freq.get(mid, 0) for mid in b_native_set if pp_lane_pred.get(mid) == 'QO')
tok_bn_chsh = sum(b_middle_freq.get(mid, 0) for mid in b_native_set if pp_lane_pred.get(mid) == 'CHSH')

tok_table = [[tok_azc_qo, tok_azc_chsh], [tok_bn_qo, tok_bn_chsh]]
tok_chi2, tok_p, tok_method, tok_v = safe_chi2(tok_table)
tok_or, tok_or_lo, tok_or_hi = odds_ratio_ci(tok_azc_qo, tok_azc_chsh, tok_bn_qo, tok_bn_chsh)

print(f"\nToken-level 2x2:")
print(f"  AZC-Med:  QO={tok_azc_qo}, CHSH={tok_azc_chsh}")
print(f"  B-Native: QO={tok_bn_qo}, CHSH={tok_bn_chsh}")
print(f"  {tok_method}: stat={tok_chi2:.3f}, p={tok_p:.4f}, V={tok_v:.3f}")
print(f"  OR={tok_or:.3f} [{tok_or_lo:.3f}, {tok_or_hi:.3f}]")

# Interpretation
if type_p < 0.05 and tok_p < 0.05:
    asym_interp = "AZC filtering is asymmetric at both type and token level"
elif type_p < 0.05:
    asym_interp = "AZC filtering is asymmetric at type level; token level NS (C640 frequency confound)"
elif tok_p < 0.05:
    asym_interp = "AZC filtering is asymmetric at token level only; type level NS"
else:
    asym_interp = "No significant AZC filtering asymmetry detected"
print(f"\n  Interpretation: {asym_interp}")

test2_results = {
    'type_level': {
        'azc_med': {'qo': a_qo, 'chsh': a_chsh,
                    'qo_frac': round(a_qo / max(1, a_qo + a_chsh), 4)},
        'b_native': {'qo': n_qo_bn, 'chsh': n_chsh_bn,
                     'qo_frac': round(n_qo_bn / max(1, n_qo_bn + n_chsh_bn), 4)},
        'table': type_table,
        'test': {'method': type_method, 'stat': round(type_chi2, 4), 'p': round(type_p, 6)},
        'odds_ratio': round(type_or, 4),
        'or_ci_95': [round(type_or_lo, 4), round(type_or_hi, 4)],
        'cramers_v': round(type_v, 4),
    },
    'token_level': {
        'azc_med': {'qo_tokens': tok_azc_qo, 'chsh_tokens': tok_azc_chsh,
                    'qo_frac': round(tok_azc_qo / max(1, tok_azc_qo + tok_azc_chsh), 4)},
        'b_native': {'qo_tokens': tok_bn_qo, 'chsh_tokens': tok_bn_chsh,
                     'qo_frac': round(tok_bn_qo / max(1, tok_bn_qo + tok_bn_chsh), 4)},
        'table': tok_table,
        'test': {'method': tok_method, 'stat': round(tok_chi2, 4), 'p': round(tok_p, 6)},
        'odds_ratio': round(tok_or, 4),
        'or_ci_95': [round(tok_or_lo, 4), round(tok_or_hi, 4)],
        'cramers_v': round(tok_v, 4),
    },
    'interpretation': asym_interp,
}

# ============================================================
# SECTION 4: Test 3 -- Discriminator Pathway Analysis
# ============================================================

print("\n" + "=" * 70)
print("TEST 3: Discriminator Pathway Analysis")
print("=" * 70)

all_results = disc_data['discrimination_test']['all_results']

# Extract significant discriminators (FDR < 0.05)
sig_discriminators = []
for mid, info in all_results.items():
    if info['fdr'] < 0.05:
        sig_discriminators.append({
            'middle': mid,
            'pathway': info.get('azc_type', 'UNKNOWN'),
            'direction': info['direction'],
            'r': info['r'],
            'abs_r': abs(info['r']),
            'fdr': info['fdr'],
            'material_class': info.get('material_class', 'UNKNOWN'),
            'en_subfamily': info.get('en_subfamily', 'none'),
            'has_en_association': info.get('has_en_association', False),
            'b_role': info.get('b_role', 'UNKNOWN'),
        })

print(f"Found {len(sig_discriminators)} significant discriminators (FDR < 0.05)")

# Pathway x direction table
pathway_counts = {'AZC-Med': {'QO': 0, 'CHSH': 0}, 'B-Native': {'QO': 0, 'CHSH': 0}}
pathway_abs_r = {'AZC-Med': [], 'B-Native': []}

for d in sig_discriminators:
    pw = d['pathway']
    if pw not in pathway_counts:
        pathway_counts[pw] = {'QO': 0, 'CHSH': 0}
        pathway_abs_r[pw] = []
    pathway_counts[pw][d['direction']] += 1
    pathway_abs_r[pw].append(d['abs_r'])

print("\nBy pathway:")
for pw in ['AZC-Med', 'B-Native']:
    n = pathway_counts[pw]['QO'] + pathway_counts[pw]['CHSH']
    mean_r = sum(pathway_abs_r[pw]) / len(pathway_abs_r[pw]) if pathway_abs_r[pw] else 0
    print(f"  {pw}: n={n}, QO={pathway_counts[pw]['QO']}, CHSH={pathway_counts[pw]['CHSH']}, mean|r|={mean_r:.3f}")

# Fisher's exact on 2x2
fisher_table = [
    [pathway_counts['AZC-Med']['QO'], pathway_counts['AZC-Med']['CHSH']],
    [pathway_counts['B-Native']['QO'], pathway_counts['B-Native']['CHSH']]
]

# Guard: check if either pathway has < 3 discriminators
azc_n = sum(fisher_table[0])
bn_n = sum(fisher_table[1])

if azc_n >= 3 and bn_n >= 3:
    fisher_odds, fisher_p = sp_stats.fisher_exact(fisher_table)
    fisher_method = 'fisher_exact'
    print(f"\nFisher's exact: OR={fisher_odds:.3f}, p={fisher_p:.4f}")
else:
    fisher_odds, fisher_p = float('nan'), float('nan')
    fisher_method = 'underpowered'
    print(f"\nFisher's exact: UNDERPOWERED (AZC-Med n={azc_n}, B-Native n={bn_n})")

# Mann-Whitney on |r| by pathway
if len(pathway_abs_r['AZC-Med']) >= 3 and len(pathway_abs_r['B-Native']) >= 3:
    mw_u, mw_p = sp_stats.mannwhitneyu(
        pathway_abs_r['AZC-Med'], pathway_abs_r['B-Native'],
        alternative='two-sided'
    )
    mw_method = 'mann_whitney'
    print(f"Mann-Whitney |r|: U={mw_u:.1f}, p={mw_p:.4f}")
else:
    mw_u, mw_p = float('nan'), float('nan')
    mw_method = 'underpowered'
    print("Mann-Whitney |r|: UNDERPOWERED")

# EN breakdown
en_breakdown = {'AZC-Med': {'en': 0, 'non_en': 0}, 'B-Native': {'en': 0, 'non_en': 0}}
for d in sig_discriminators:
    pw = d['pathway']
    if pw in en_breakdown:
        if d['has_en_association']:
            en_breakdown[pw]['en'] += 1
        else:
            en_breakdown[pw]['non_en'] += 1

print("\nEN association breakdown:")
for pw in ['AZC-Med', 'B-Native']:
    print(f"  {pw}: EN-associated={en_breakdown[pw]['en']}, non-EN={en_breakdown[pw]['non_en']}")

# Detailed list
print("\nDetailed discriminators:")
for d in sorted(sig_discriminators, key=lambda x: x['abs_r'], reverse=True):
    print(f"  {d['middle']:8s} {d['pathway']:10s} {d['direction']:4s} r={d['r']:+.3f} "
          f"mat={d['material_class']:8s} EN={d['has_en_association']}")

test3_results = {
    'n_discriminators': len(sig_discriminators),
    'by_pathway': {
        pw: {
            'n': pathway_counts[pw]['QO'] + pathway_counts[pw]['CHSH'],
            'qo': pathway_counts[pw]['QO'],
            'chsh': pathway_counts[pw]['CHSH'],
            'mean_abs_r': round(sum(pathway_abs_r[pw]) / max(1, len(pathway_abs_r[pw])), 4),
        }
        for pw in ['AZC-Med', 'B-Native']
    },
    'pathway_x_direction_table': fisher_table,
    'fisher_test': {
        'method': fisher_method,
        'odds_ratio': round(fisher_odds, 4) if not (fisher_odds != fisher_odds) else None,
        'p': round(fisher_p, 4) if not (fisher_p != fisher_p) else None,
    },
    'abs_r_comparison': {
        'method': mw_method,
        'u_stat': round(mw_u, 1) if not (mw_u != mw_u) else None,
        'p': round(mw_p, 4) if not (mw_p != mw_p) else None,
    },
    'en_breakdown': en_breakdown,
    'detailed_discriminators': sig_discriminators,
}


# ============================================================
# SECTION 5: Also report all tested PP MIDDLEs by pathway
# ============================================================

# For completeness: mean |r| across ALL tested PP (not just significant)
all_tested_abs_r = {'AZC-Med': [], 'B-Native': []}
for mid, info in all_results.items():
    pw = info.get('azc_type', 'UNKNOWN')
    if pw in all_tested_abs_r:
        all_tested_abs_r[pw].append(abs(info['r']))

all_tested_comparison = {}
for pw in ['AZC-Med', 'B-Native']:
    vals = all_tested_abs_r[pw]
    all_tested_comparison[pw] = {
        'n_tested': len(vals),
        'mean_abs_r': round(sum(vals) / max(1, len(vals)), 4),
    }

if len(all_tested_abs_r['AZC-Med']) >= 5 and len(all_tested_abs_r['B-Native']) >= 5:
    all_mw_u, all_mw_p = sp_stats.mannwhitneyu(
        all_tested_abs_r['AZC-Med'], all_tested_abs_r['B-Native'],
        alternative='two-sided'
    )
    all_tested_comparison['mann_whitney'] = {
        'u_stat': round(all_mw_u, 1),
        'p': round(all_mw_p, 4),
    }
    print(f"\nAll tested PP |r| by pathway:")
    print(f"  AZC-Med: n={all_tested_comparison['AZC-Med']['n_tested']}, mean|r|={all_tested_comparison['AZC-Med']['mean_abs_r']:.4f}")
    print(f"  B-Native: n={all_tested_comparison['B-Native']['n_tested']}, mean|r|={all_tested_comparison['B-Native']['mean_abs_r']:.4f}")
    print(f"  Mann-Whitney: U={all_mw_u:.1f}, p={all_mw_p:.4f}")

test3_results['all_tested_comparison'] = all_tested_comparison


# ============================================================
# SECTION 6: Summary & Save
# ============================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Verdicts
census_verdict = 'CHSH_BIASED' if qo_frac_type < 0.35 else ('QO_BIASED' if qo_frac_type > 0.65 else 'BALANCED')
filtering_verdict = 'AZC_ASYMMETRIC' if type_p < 0.05 else 'AZC_SYMMETRIC'
disc_verdict = ('PATHWAY_DIFFERENTIAL' if (fisher_method == 'fisher_exact' and fisher_p < 0.05)
                else ('UNDERPOWERED' if fisher_method == 'underpowered' else 'PATHWAY_UNIFORM'))

print(f"Test 1 (Census):       {census_verdict} (QO frac = {qo_frac_type:.3f} type, {qo_frac_tok:.3f} token)")
print(f"Test 2 (AZC Asym):     {filtering_verdict} (type p={type_p:.4f}, token p={tok_p:.4f})")
print(f"Test 3 (Disc Pathway): {disc_verdict}")

results = {
    'metadata': {
        'phase': 'PP_LANE_PIPELINE',
        'script': 'pp_lane_vocabulary_architecture',
        'description': 'PP vocabulary lane character architecture: census, AZC asymmetry, discriminator pathways',
    },
    'pp_character_census': test1_results,
    'azc_filtering_asymmetry': test2_results,
    'discriminator_pathway_analysis': test3_results,
    'verdicts': {
        'census': census_verdict,
        'filtering': filtering_verdict,
        'discriminators': disc_verdict,
    },
}

output_path = PROJECT_ROOT / 'phases/PP_LANE_PIPELINE/results/pp_lane_vocabulary_architecture.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to {output_path}")
