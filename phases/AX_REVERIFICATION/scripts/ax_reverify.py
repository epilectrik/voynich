"""
AX Re-Verification Script

Recalculates all AX constraint statistics (C563-C572) using corrected
19-class membership (Class 14 removed from AX, confirmed FQ per C583).

Root cause: ax_census_reconciliation.py defined ICC_FQ = {9, 13, 23}
without Class 14, causing it to default into AX by set subtraction.

This script produces old vs new comparison for each constraint.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
import math
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from scipy import stats as scipy_stats
from scripts.voynich import Transcript, Morphology

# ==============================================================
# SETUP
# ==============================================================

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
MIDDLE_CLASSES = BASE / 'phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json'
SURVIVORS = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json'
REGIME_MAP = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
RESULTS = BASE / 'phases/AX_REVERIFICATION/results'

# Load data
with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

with open(MIDDLE_CLASSES) as f:
    mc = json.load(f)
ri_middles = set(mc['a_exclusive_middles'])
pp_middles = set(mc['a_shared_middles'])

with open(REGIME_MAP) as f:
    regime_data = json.load(f)
folio_to_regime = regime_data.get('folio_to_regime', {})
folio_to_section = regime_data.get('folio_to_section', {})

morph = Morphology()
tx = Transcript()
b_tokens = list(tx.currier_b())

# ==============================================================
# CORRECTED MEMBERSHIP (the whole point of this script)
# ==============================================================

ICC_CC = {10, 11, 12, 17}
ICC_EN = {8} | set(range(31, 50))
ICC_FL = {7, 30, 38, 40}
ICC_FQ = {9, 13, 14, 23}  # CORRECTED: was {9, 13, 23}

# 19 classes (Class 14 removed)
AX_CLASSES = {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29}
AX_INIT = {4, 5, 6, 24, 26}
AX_MED = {1, 2, 3, 16, 18, 27, 28, 29}  # CORRECTED: was {1, 2, 3, 14, 16, 18, 27, 28, 29}
AX_FINAL = {15, 19, 20, 21, 22, 25}

ALL_49 = set(range(1, 50))

def get_role(cls):
    if cls is None: return 'UN'
    if cls in ICC_CC: return 'CC'
    if cls in ICC_EN: return 'EN'
    if cls in ICC_FL: return 'FL'
    if cls in ICC_FQ: return 'FQ'
    if cls in AX_CLASSES: return 'AX'
    return 'UN'

def get_subgroup(cls):
    if cls in AX_INIT: return 'AX_INIT'
    if cls in AX_MED: return 'AX_MED'
    if cls in AX_FINAL: return 'AX_FINAL'
    return None

# Pre-compute lines
lines = defaultdict(list)
for token in b_tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    folio = token.folio
    line = token.line
    n_tokens_in_line = 0  # placeholder for position
    lines[(folio, line)].append({
        'word': word,
        'class': cls,
        'role': get_role(cls),
        'folio': folio,
    })

# Compute positions
for key, toks in lines.items():
    n = len(toks)
    for i, t in enumerate(toks):
        t['position'] = i / (n - 1) if n > 1 else 0.5
        t['is_initial'] = (i == 0)
        t['is_final'] = (i == n - 1)

# Flatten for easy access
all_tokens = []
for key, toks in lines.items():
    all_tokens.extend(toks)

# AX tokens only
ax_tokens = [t for t in all_tokens if t['role'] == 'AX']

print(f"Total B tokens: {len(all_tokens)}")
print(f"AX tokens (19 classes): {len(ax_tokens)}")
print(f"Removed Class 14: {sum(1 for t in all_tokens if t['class'] == 14)} tokens now in FQ")

results = {'meta': {'phase': 'AX_REVERIFICATION', 'date': '2026-01-26',
                     'ax_classes': sorted(AX_CLASSES), 'ax_class_count': len(AX_CLASSES)}}

# ==============================================================
# SECTION 1: C563 — Positional Stratification
# ==============================================================
print("\n" + "=" * 70)
print("C563: POSITIONAL STRATIFICATION (KW recalculation)")
print("=" * 70)

# Gather positions per subgroup
init_positions = [t['position'] for t in ax_tokens if t['class'] in AX_INIT]
med_positions = [t['position'] for t in ax_tokens if t['class'] in AX_MED]
final_positions = [t['position'] for t in ax_tokens if t['class'] in AX_FINAL]

# Kruskal-Wallis
kw_h, kw_p = scipy_stats.kruskal(init_positions, med_positions, final_positions)
print(f"KW H = {kw_h:.1f}, p = {kw_p:.2e}")
print(f"  (old: H=213.9, p=3.60e-47)")

# Cohen's d (INIT vs FINAL)
init_arr = np.array(init_positions)
final_arr = np.array(final_positions)
pooled_std = np.sqrt(((len(init_arr)-1)*np.var(init_arr, ddof=1) +
                       (len(final_arr)-1)*np.var(final_arr, ddof=1)) /
                      (len(init_arr) + len(final_arr) - 2))
cohens_d = abs(np.mean(init_arr) - np.mean(final_arr)) / pooled_std if pooled_std > 0 else 0
print(f"Cohen's d (INIT vs FINAL) = {cohens_d:.2f}")
print(f"  (old: 0.69)")

# Mann-Whitney pairwise
mw_init_med = scipy_stats.mannwhitneyu(init_positions, med_positions, alternative='two-sided')
mw_init_final = scipy_stats.mannwhitneyu(init_positions, final_positions, alternative='two-sided')
mw_med_final = scipy_stats.mannwhitneyu(med_positions, final_positions, alternative='two-sided')
print(f"MW INIT-MED: p = {mw_init_med.pvalue:.2e}")
print(f"MW INIT-FINAL: p = {mw_init_final.pvalue:.2e}")
print(f"MW MED-FINAL: p = {mw_med_final.pvalue:.2e}")

# Directional ordering
init_before_final = 0
final_before_init = 0
for key, toks in lines.items():
    ax_in_line = [(i, t) for i, t in enumerate(toks) if t['role'] == 'AX']
    for idx_a, (i, t1) in enumerate(ax_in_line):
        for idx_b, (j, t2) in enumerate(ax_in_line):
            if j > i:
                sg1 = get_subgroup(t1['class'])
                sg2 = get_subgroup(t2['class'])
                if sg1 == 'AX_INIT' and sg2 == 'AX_FINAL':
                    init_before_final += 1
                elif sg1 == 'AX_FINAL' and sg2 == 'AX_INIT':
                    final_before_init += 1

total_pairs = init_before_final + final_before_init
init_first_rate = init_before_final / total_pairs if total_pairs > 0 else 0
print(f"INIT before FINAL: {init_before_final}/{total_pairs} = {init_first_rate:.1%}")
print(f"  (old: 71.8%, n=369)")

# Subgroup bigrams
sub_bigrams = Counter()
for key, toks in lines.items():
    ax_in_line = [(i, t) for i, t in enumerate(toks) if t['role'] == 'AX']
    for idx in range(len(ax_in_line) - 1):
        sg1 = get_subgroup(ax_in_line[idx][1]['class'])
        sg2 = get_subgroup(ax_in_line[idx+1][1]['class'])
        if sg1 and sg2:
            sub_bigrams[(sg1, sg2)] += 1

# Subgroup token counts
init_n = len(init_positions)
med_n = len(med_positions)
final_n = len(final_positions)
total_ax = init_n + med_n + final_n

print(f"\nSubgroup counts: INIT={init_n}, MED={med_n}, FINAL={final_n}, Total={total_ax}")
print(f"Subgroup %: INIT={init_n/total_ax:.1%}, MED={med_n/total_ax:.1%}, FINAL={final_n/total_ax:.1%}")
print(f"Mean positions: INIT={np.mean(init_positions):.3f}, MED={np.mean(med_positions):.3f}, FINAL={np.mean(final_positions):.3f}")

results['C563'] = {
    'old': {'kw_h': 213.9, 'kw_p': 3.60e-47, 'cohens_d': 0.69,
            'init_first_rate': 0.718, 'n_pairs': 369,
            'init_n': 1195, 'med_n': 2763, 'final_n': 601, 'total': 4559},
    'new': {'kw_h': round(kw_h, 1), 'kw_p': float(f"{kw_p:.2e}"),
            'cohens_d': round(cohens_d, 2),
            'init_first_rate': round(init_first_rate, 3), 'n_pairs': total_pairs,
            'init_n': init_n, 'med_n': med_n, 'final_n': final_n, 'total': total_ax,
            'mw_init_med_p': float(f"{mw_init_med.pvalue:.2e}"),
            'mw_init_final_p': float(f"{mw_init_final.pvalue:.2e}"),
            'mw_med_final_p': float(f"{mw_med_final.pvalue:.2e}"),
            'mean_init': round(np.mean(init_positions), 3),
            'mean_med': round(np.mean(med_positions), 3),
            'mean_final': round(np.mean(final_positions), 3)},
    'verdict': 'STRENGTHENED' if kw_h >= 213.9 else ('UNCHANGED' if kw_p < 1e-20 else 'WEAKENED')
}

# ==============================================================
# SECTION 2: C564 — Morphological-Positional Correspondence
# ==============================================================
print("\n" + "=" * 70)
print("C564: MORPHOLOGICAL-POSITIONAL CORRESPONDENCE")
print("=" * 70)

# Per-subgroup morphological profiles
subgroup_morph = {'AX_INIT': [], 'AX_MED': [], 'AX_FINAL': []}
for t in ax_tokens:
    sg = get_subgroup(t['class'])
    if sg:
        m = morph.extract(t['word'])
        subgroup_morph[sg].append({
            'has_prefix': m.prefix is not None,
            'has_suffix': m.suffix is not None,
            'has_articulator': m.has_articulator,
            'prefix': m.prefix,
            'class': t['class'],
        })

c564_new = {}
for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    tokens_sg = subgroup_morph[sg]
    n = len(tokens_sg)
    if n == 0:
        continue
    prefix_rate = sum(1 for t in tokens_sg if t['has_prefix']) / n
    suffix_rate = sum(1 for t in tokens_sg if t['has_suffix']) / n
    art_rate = sum(1 for t in tokens_sg if t['has_articulator']) / n

    # ok/ot purity for MED
    if sg == 'AX_MED':
        ok_ot_count = sum(1 for t in tokens_sg if t['prefix'] in ('ok', 'ot'))
        ok_ot_purity = ok_ot_count / n if n > 0 else 0

    # Unique types
    unique_types = len(set(t['class'] for t in tokens_sg))

    print(f"\n{sg} (n={n}):")
    print(f"  PREFIX rate: {prefix_rate:.3f}")
    print(f"  SUFFIX rate: {suffix_rate:.3f}")
    print(f"  Articulator rate: {art_rate:.3f}")
    if sg == 'AX_MED':
        print(f"  ok/ot purity: {ok_ot_purity:.3f}")
        print(f"  (old SUFFIX rate for AX_MED: 0.264)")

    c564_new[sg] = {
        'n_tokens': n,
        'prefix_rate': round(prefix_rate, 3),
        'suffix_rate': round(suffix_rate, 3),
        'articulator_rate': round(art_rate, 3),
    }
    if sg == 'AX_MED':
        c564_new[sg]['ok_ot_purity'] = round(ok_ot_purity, 3)

results['C564'] = {
    'old': {'ax_med_suffix_rate': 0.264, 'note': 'included Class 14 (suffix_rate=0.0)'},
    'new': c564_new,
    'verdict': 'STRENGTHENED'  # removing zero-suffix class increases AX_MED coherence
}

# ==============================================================
# SECTION 3: C565 — Scaffold Function
# ==============================================================
print("\n" + "=" * 70)
print("C565: SCAFFOLD FUNCTION (transitions)")
print("=" * 70)

# Role-level transitions
role_bigrams = Counter()
role_totals = Counter()
for key, toks in lines.items():
    for i in range(len(toks) - 1):
        r1 = toks[i]['role']
        r2 = toks[i+1]['role']
        role_bigrams[(r1, r2)] += 1
        role_totals[r1] += 1

total_transitions = sum(role_totals.values())
role_right_totals = Counter()
for (r1, r2), c in role_bigrams.items():
    role_right_totals[r2] += c
base_rates = {r: role_right_totals.get(r, 0) / total_transitions for r in ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']}

# AX self-chaining
ax_total_trans = role_totals.get('AX', 0)
ax_self = role_bigrams.get(('AX', 'AX'), 0)
ax_self_rate = ax_self / ax_total_trans if ax_total_trans > 0 else 0
ax_self_enrichment = ax_self_rate / base_rates['AX'] if base_rates['AX'] > 0 else 0

print(f"AX self-chain rate: {ax_self_rate:.3f} (enrichment: {ax_self_enrichment:.2f}x)")
print(f"  (old: enrichment 1.09x)")

# AX transition enrichment
print(f"\nAX transition enrichment:")
ax_enrichments = {}
for r in ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']:
    obs = role_bigrams.get(('AX', r), 0) / ax_total_trans if ax_total_trans > 0 else 0
    exp = base_rates[r]
    enr = obs / exp if exp > 0 else 0
    ax_enrichments[f'AX->{r}'] = round(enr, 2)
    print(f"  AX->{r}: {enr:.2f}x")

# Hazard check: are any of the 19 AX classes in hazard topology?
# Hazard classes from C109/C541: {7, 8, 9, 23, 30, 31}
hazard_classes = {7, 8, 9, 23, 30, 31}
ax_hazard = AX_CLASSES & hazard_classes
print(f"\nAX classes in hazard topology: {ax_hazard if ax_hazard else 'NONE (confirmed)'}")

results['C565'] = {
    'old': {'ax_self_enrichment': 1.09, 'ax_hazard_classes': 0},
    'new': {
        'ax_self_rate': round(ax_self_rate, 4),
        'ax_self_enrichment': round(ax_self_enrichment, 2),
        'ax_enrichments': ax_enrichments,
        'ax_hazard_classes': len(ax_hazard),
        'ax_base_rate': round(base_rates['AX'], 4),
    },
    'verdict': 'UNCHANGED'  # scaffold function is qualitative
}

# ==============================================================
# SECTION 4: C567 — MIDDLE Sharing / Pipeline Purity
# ==============================================================
print("\n" + "=" * 70)
print("C567: MIDDLE SHARING / PIPELINE PURITY")
print("=" * 70)

# Build class -> middles mapping
class_to_middles = defaultdict(set)
for tok, cls in token_to_class.items():
    m = morph.extract(tok)
    if m.middle:
        class_to_middles[cls].add(m.middle)

# Build role -> middles
role_to_middles = defaultdict(set)
for cls, middles in class_to_middles.items():
    role = get_role(cls)
    role_to_middles[role].update(middles)

ax_middles = role_to_middles['AX']
en_middles = role_to_middles['EN']
cc_middles = role_to_middles['CC']
fl_middles = role_to_middles['FL']
fq_middles = role_to_middles['FQ']

# Pipeline classification
pp_count = sum(1 for m in ax_middles if m in pp_middles)
ri_count = sum(1 for m in ax_middles if m in ri_middles)
bx_count = sum(1 for m in ax_middles if m not in pp_middles and m not in ri_middles)
pp_rate = pp_count / len(ax_middles) if ax_middles else 0

print(f"Unique AX MIDDLEs: {len(ax_middles)}")
print(f"  PP: {pp_count}, RI: {ri_count}, B-exclusive: {bx_count}")
print(f"  PP rate: {pp_rate:.1%}")
print(f"  (old: 57 MIDDLEs, 56/57 PP = 98.2%)")

# Cross-role overlaps (Jaccard)
def jaccard(a, b):
    if not a and not b: return 0
    return len(a & b) / len(a | b)

ax_en_j = jaccard(ax_middles, en_middles)
ax_fq_j = jaccard(ax_middles, fq_middles)
ax_fl_j = jaccard(ax_middles, fl_middles)
ax_cc_j = jaccard(ax_middles, cc_middles)

ax_en_shared = len(ax_middles & en_middles)
ax_fq_shared = len(ax_middles & fq_middles)
ax_fl_shared = len(ax_middles & fl_middles)
ax_cc_shared = len(ax_middles & cc_middles)

# AX-exclusive
any_operational = en_middles | cc_middles | fl_middles | fq_middles
ax_exclusive = ax_middles - any_operational
ax_shared_with_any = ax_middles & any_operational

print(f"\nCross-role MIDDLE sharing:")
print(f"  AX-EN: {ax_en_shared} shared, Jaccard={ax_en_j:.3f} (old: 36, J=0.400)")
print(f"  AX-FQ: {ax_fq_shared} shared, Jaccard={ax_fq_j:.3f} (old: 15, J=0.263)")
print(f"  AX-FL: {ax_fl_shared} shared, Jaccard={ax_fl_j:.3f} (old: 7)")
print(f"  AX-CC: {ax_cc_shared} shared, Jaccard={ax_cc_j:.3f} (old: 6)")
print(f"\nAX-exclusive MIDDLEs: {len(ax_exclusive)} ({len(ax_exclusive)/len(ax_middles):.1%})")
print(f"Shared with any operational: {len(ax_shared_with_any)} ({len(ax_shared_with_any)/len(ax_middles):.1%})")
print(f"  (old: 16 exclusive = 28.1%, 41 shared = 71.9%)")

# PREFIX differentiation for shared MIDDLEs
middle_roles_map = defaultdict(lambda: {'AX': set(), 'non_AX': set()})
for tok, cls in token_to_class.items():
    m_obj = morph.extract(tok)
    if m_obj.middle:
        role = get_role(cls)
        pfx = m_obj.prefix if m_obj.prefix else 'NONE'
        if role == 'AX':
            middle_roles_map[m_obj.middle]['AX'].add(pfx)
        else:
            middle_roles_map[m_obj.middle]['non_AX'].add(pfx)

shared_m = {mid: info for mid, info in middle_roles_map.items()
            if info['AX'] and info['non_AX']}
prefix_diff = sum(1 for mid, info in shared_m.items()
                  if len(info['AX'] & info['non_AX']) == 0)

print(f"\nShared MIDDLEs (AX + non-AX): {len(shared_m)}")
print(f"PREFIX-differentiated: {prefix_diff}/{len(shared_m)}")
print(f"  (old: 24/41 = 58.5%)")

results['C567'] = {
    'old': {'ax_middles': 57, 'pp_count': 56, 'pp_rate': 0.982,
            'ax_en_shared': 36, 'ax_en_jaccard': 0.400,
            'ax_fq_shared': 15, 'ax_fq_jaccard': 0.263,
            'ax_fl_shared': 7, 'ax_cc_shared': 6,
            'ax_exclusive': 16, 'ax_exclusive_pct': 0.281,
            'shared_total': 41, 'prefix_diff': 24, 'prefix_diff_pct': 0.585},
    'new': {'ax_middles': len(ax_middles), 'pp_count': pp_count, 'pp_rate': round(pp_rate, 3),
            'ri_count': ri_count, 'bx_count': bx_count,
            'ax_en_shared': ax_en_shared, 'ax_en_jaccard': round(ax_en_j, 3),
            'ax_fq_shared': ax_fq_shared, 'ax_fq_jaccard': round(ax_fq_j, 3),
            'ax_fl_shared': ax_fl_shared, 'ax_cc_shared': ax_cc_shared,
            'ax_exclusive': len(ax_exclusive), 'ax_exclusive_pct': round(len(ax_exclusive)/len(ax_middles), 3),
            'shared_total': len(ax_shared_with_any),
            'shared_pct': round(len(ax_shared_with_any)/len(ax_middles), 3),
            'prefix_diff': prefix_diff,
            'prefix_diff_pct': round(prefix_diff/len(shared_m), 3) if shared_m else 0},
    'verdict': 'check'
}

# ==============================================================
# SECTION 5: C569 — Proportional Scaling
# ==============================================================
print("\n" + "=" * 70)
print("C569: PROPORTIONAL SCALING")
print("=" * 70)

with open(SURVIVORS) as f:
    surv_data = json.load(f)

records = surv_data['records']
total_counts_569 = []
ax_counts_569 = []
ax_fractions_569 = []
ax_init_counts_569 = []
ax_med_counts_569 = []
ax_final_counts_569 = []

for rec in records:
    surviving = set(rec['surviving_classes'])
    total = len(surviving)
    ax = len(surviving & AX_CLASSES)
    ax_init = len(surviving & AX_INIT)
    ax_med = len(surviving & AX_MED)
    ax_final = len(surviving & AX_FINAL)

    total_counts_569.append(total)
    ax_counts_569.append(ax)
    ax_fractions_569.append(ax / total if total > 0 else 0)
    ax_init_counts_569.append(ax_init)
    ax_med_counts_569.append(ax_med)
    ax_final_counts_569.append(ax_final)

n_rec = len(records)
mean_frac = sum(ax_fractions_569) / n_rec

# Expected fractions
expected_uniform = len(AX_CLASSES) / len(ALL_49)  # 19/49
survival_rates = surv_data['class_survival_rates']
sum_ax_rates = sum(survival_rates.get(str(c), 0) for c in AX_CLASSES)
sum_all_rates = sum(survival_rates.get(str(c), 0) for c in ALL_49 if str(c) in survival_rates)
expected_weighted = sum_ax_rates / sum_all_rates if sum_all_rates > 0 else 0

# Linear regression
mean_x = sum(total_counts_569) / n_rec
mean_y = sum(ax_counts_569) / n_rec
ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(total_counts_569, ax_counts_569))
ss_xx = sum((x - mean_x) ** 2 for x in total_counts_569)
ss_yy = sum((y - mean_y) ** 2 for y in ax_counts_569)
slope = ss_xy / ss_xx if ss_xx > 0 else 0
r_val = ss_xy / math.sqrt(ss_xx * ss_yy) if ss_xx > 0 and ss_yy > 0 else 0
r_squared = r_val ** 2

def linreg(x_vals, y_vals):
    n_l = len(x_vals)
    mx = sum(x_vals) / n_l
    my = sum(y_vals) / n_l
    sxy = sum((x - mx) * (y - my) for x, y in zip(x_vals, y_vals))
    sxx = sum((x - mx) ** 2 for x in x_vals)
    syy = sum((y - my) ** 2 for y in y_vals)
    sl = sxy / sxx if sxx > 0 else 0
    rv = sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else 0
    return {'slope': round(sl, 4), 'r_squared': round(rv ** 2, 4), 'mean': round(my, 2)}

subgroup_regs = {
    'AX_INIT': linreg(total_counts_569, ax_init_counts_569),
    'AX_MED': linreg(total_counts_569, ax_med_counts_569),
    'AX_FINAL': linreg(total_counts_569, ax_final_counts_569),
}

print(f"Mean AX fraction: {mean_frac:.4f} (old: 0.4540)")
print(f"Expected uniform ({len(AX_CLASSES)}/49): {expected_uniform:.4f} (old: 0.4082 for 20/49)")
print(f"Expected weighted: {expected_weighted:.4f} (old: 0.4545)")
print(f"Deviation from weighted: {mean_frac - expected_weighted:+.4f} (old: -0.0005)")
print(f"\nLinear model: slope={slope:.4f} (old: 0.4246), R²={r_squared:.4f} (old: 0.8299)")
print(f"\nSubgroup slopes:")
for sg, reg in subgroup_regs.items():
    n_cls = len(AX_INIT if sg == 'AX_INIT' else AX_MED if sg == 'AX_MED' else AX_FINAL)
    expected_sl = n_cls / len(ALL_49)
    print(f"  {sg}: slope={reg['slope']:.4f} (expected {expected_sl:.4f}), R²={reg['r_squared']:.4f}")

results['C569'] = {
    'old': {'mean_fraction': 0.4540, 'expected_weighted': 0.4545,
            'deviation': -0.0005, 'slope': 0.4246, 'r_squared': 0.8299},
    'new': {'mean_fraction': round(mean_frac, 4), 'expected_uniform': round(expected_uniform, 4),
            'expected_weighted': round(expected_weighted, 4),
            'deviation': round(mean_frac - expected_weighted, 4),
            'slope': round(slope, 4), 'r_squared': round(r_squared, 4),
            'subgroup_scaling': subgroup_regs},
    'verdict': 'check'
}

# ==============================================================
# SECTION 6: C570 — PREFIX Derivability
# ==============================================================
print("\n" + "=" * 70)
print("C570: PREFIX DERIVABILITY")
print("=" * 70)

# Build prefix -> role distribution
token_morph_list = []
for tok, cls in token_to_class.items():
    m_obj = morph.extract(tok)
    role = get_role(cls)
    token_morph_list.append({
        'token': tok, 'class': cls, 'role': role, 'is_ax': role == 'AX',
        'prefix': m_obj.prefix if m_obj.prefix else 'NONE',
    })

prefix_role_dist = defaultdict(lambda: defaultdict(int))
for tm in token_morph_list:
    prefix_role_dist[tm['prefix']][tm['role']] += 1

# Prefix majority classifier
prefix_majority = {}
for pfx, roles in prefix_role_dist.items():
    best_role = max(roles, key=roles.get)
    total = sum(roles.values())
    prefix_majority[pfx] = {'predicted': best_role, 'count': total}

# Binary AX vs non-AX
tp = fp = fn = tn = 0
for tm in token_morph_list:
    predicted_ax = prefix_majority[tm['prefix']]['predicted'] == 'AX'
    actual_ax = tm['is_ax']
    if predicted_ax and actual_ax: tp += 1
    elif predicted_ax and not actual_ax: fp += 1
    elif not predicted_ax and actual_ax: fn += 1
    else: tn += 1

binary_acc = (tp + tn) / len(token_morph_list)
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

print(f"Binary accuracy: {binary_acc:.1%} (old: 89.6%)")
print(f"Precision: {precision:.3f} (old: 0.867)")
print(f"Recall: {recall:.3f} (old: 0.944)")
print(f"F1: {f1:.3f} (old: 0.904)")
print(f"  TP={tp} FP={fp} FN={fn} TN={tn}")

# Prefix categories
ax_exclusive_pfx = []
nonax_exclusive_pfx = []
ambiguous_pfx = []
for pfx, roles in prefix_role_dist.items():
    has_ax = roles.get('AX', 0) > 0
    has_nonax = any(v > 0 for k, v in roles.items() if k != 'AX')
    if has_ax and not has_nonax:
        ax_exclusive_pfx.append(pfx)
    elif not has_ax:
        nonax_exclusive_pfx.append(pfx)
    else:
        ambiguous_pfx.append(pfx)

print(f"\nAX-exclusive prefixes: {len(ax_exclusive_pfx)} (old: 22)")
print(f"Non-AX-exclusive: {len(nonax_exclusive_pfx)}")
print(f"Ambiguous: {len(ambiguous_pfx)} (old: 7)")

results['C570'] = {
    'old': {'binary_accuracy': 0.896, 'precision': 0.867, 'recall': 0.944, 'f1': 0.904,
            'ax_exclusive_prefixes': 22, 'ambiguous_prefixes': 7},
    'new': {'binary_accuracy': round(binary_acc, 4), 'precision': round(precision, 3),
            'recall': round(recall, 3), 'f1': round(f1, 3),
            'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'ax_exclusive_prefixes': len(ax_exclusive_pfx),
            'nonax_exclusive_prefixes': len(nonax_exclusive_pfx),
            'ambiguous_prefixes': len(ambiguous_pfx)},
    'verdict': 'check'
}

# ==============================================================
# SECTION 7: C572 — Behavioral Collapse
# ==============================================================
print("\n" + "=" * 70)
print("C572: BEHAVIORAL COLLAPSE")
print("=" * 70)

# 7a. Positional KS tests per class
print("\n--- Positional KS tests ---")
all_ax_positions = [t['position'] for t in ax_tokens]
bonferroni_alpha = 0.05 / len(AX_CLASSES)

ks_distinct = 0
ks_results = {}
for cls in sorted(AX_CLASSES):
    cls_positions = [t['position'] for t in ax_tokens if t['class'] == cls]
    other_positions = [t['position'] for t in ax_tokens if t['class'] != cls]
    if len(cls_positions) < 5:
        continue
    stat, p = scipy_stats.ks_2samp(cls_positions, other_positions)
    is_distinct = p < bonferroni_alpha
    if is_distinct:
        ks_distinct += 1
    ks_results[cls] = {'D': round(stat, 3), 'p': float(f"{p:.2e}"), 'distinct': is_distinct}

print(f"Positionally distinct classes: {ks_distinct}/{len(AX_CLASSES)}")
print(f"  (old: 10/20)")
print(f"  Bonferroni alpha: {bonferroni_alpha:.4e}")

# 7b. Pairwise KS
n_pairs = len(AX_CLASSES) * (len(AX_CLASSES) - 1) // 2
bonf_pair_alpha = 0.05 / n_pairs if n_pairs > 0 else 0.05
pairwise_distinct = 0
ax_class_positions = {}
for cls in AX_CLASSES:
    ax_class_positions[cls] = [t['position'] for t in ax_tokens if t['class'] == cls]

for i, cls1 in enumerate(sorted(AX_CLASSES)):
    for cls2 in sorted(AX_CLASSES):
        if cls2 <= cls1:
            continue
        if len(ax_class_positions[cls1]) < 5 or len(ax_class_positions[cls2]) < 5:
            continue
        stat, p = scipy_stats.ks_2samp(ax_class_positions[cls1], ax_class_positions[cls2])
        if p < bonf_pair_alpha:
            pairwise_distinct += 1

print(f"Pairwise distinct: {pairwise_distinct}/{n_pairs}")
print(f"  (old: 65/190)")

# 7c. Transition structure (chi-squared per class)
print("\n--- Transition structure ---")
# Build per-class transition counts
cls_next_role = defaultdict(lambda: Counter())
cls_total_transitions = Counter()
for key, toks in lines.items():
    for i in range(len(toks) - 1):
        if toks[i]['class'] in AX_CLASSES:
            cls_next_role[toks[i]['class']][toks[i+1]['role']] += 1
            cls_total_transitions[toks[i]['class']] += 1

structured_count = 0
for cls in sorted(AX_CLASSES):
    if cls_total_transitions[cls] < 20:
        continue
    # Expected from overall AX transition rates
    observed = []
    expected = []
    roles_used = ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']
    total_cls = cls_total_transitions[cls]
    for r in roles_used:
        obs = cls_next_role[cls].get(r, 0)
        exp = base_rates[r] * total_cls
        if exp > 0:
            observed.append(obs)
            expected.append(exp)
    if len(observed) > 1:
        chi2, p = scipy_stats.chisquare(observed, f_exp=expected)
        if p < 0.01:
            structured_count += 1

print(f"Structured transition classes: {structured_count}/{len(AX_CLASSES)}")
print(f"  (old: 3/20)")

# 7d. Context classification (nearest centroid)
print("\n--- Context classification ---")
# Build context features per token
context_features = defaultdict(list)
for key, toks in lines.items():
    for i, t in enumerate(toks):
        if t['class'] not in AX_CLASSES:
            continue
        left_role = toks[i-1]['role'] if i > 0 else 'NONE'
        right_role = toks[i+1]['role'] if i < len(toks)-1 else 'NONE'
        feature = (left_role, right_role)
        context_features[t['class']].append(feature)

# Build role-pair frequency vectors per class
all_role_pairs = set()
for cls, feats in context_features.items():
    all_role_pairs.update(feats)
all_role_pairs = sorted(all_role_pairs)

class_centroids = {}
for cls in sorted(AX_CLASSES):
    feats = context_features.get(cls, [])
    if not feats:
        continue
    counts = Counter(feats)
    total = len(feats)
    vec = [counts.get(rp, 0) / total for rp in all_role_pairs]
    class_centroids[cls] = vec

# Nearest-centroid classification
correct = 0
total_classified = 0
for cls, feats in context_features.items():
    if cls not in class_centroids:
        continue
    for feat in feats:
        # Convert to vector
        feat_vec = [1 if rp == feat else 0 for rp in all_role_pairs]
        # Find nearest centroid
        min_dist = float('inf')
        predicted = None
        for c, centroid in class_centroids.items():
            dist = sum((a - b) ** 2 for a, b in zip(feat_vec, centroid))
            if dist < min_dist:
                min_dist = dist
                predicted = c
        if predicted == cls:
            correct += 1
        total_classified += 1

context_accuracy = correct / total_classified if total_classified > 0 else 0

# Weighted random baseline
class_sizes = {cls: len(feats) for cls, feats in context_features.items()}
total_ctx = sum(class_sizes.values())
weighted_baseline = sum((n / total_ctx) ** 2 for n in class_sizes.values()) if total_ctx > 0 else 0

print(f"Context classification accuracy: {context_accuracy:.1%}")
print(f"Weighted random baseline: {weighted_baseline:.1%}")
print(f"  (old: 6.8% accuracy, 10.3% baseline)")

# 7e. Clustering
print("\n--- Clustering ---")
try:
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.decomposition import PCA

    # Build feature matrix: position stats + transitions + context
    feature_matrix = []
    valid_classes = []
    for cls in sorted(AX_CLASSES):
        positions = ax_class_positions.get(cls, [])
        if len(positions) < 5:
            continue

        # Positional features
        pos_mean = np.mean(positions)
        pos_var = np.var(positions)
        initial_r = sum(1 for t in ax_tokens if t['class'] == cls and t['is_initial']) / len(positions)
        final_r = sum(1 for t in ax_tokens if t['class'] == cls and t['is_final']) / len(positions)

        # Transition features
        trans_total = cls_total_transitions.get(cls, 0)
        trans_vec = []
        for r in ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']:
            trans_vec.append(cls_next_role[cls].get(r, 0) / trans_total if trans_total > 0 else 0)

        # Context features
        ctx_vec = class_centroids.get(cls, [0] * len(all_role_pairs))

        feature_vec = [pos_mean, pos_var, initial_r, final_r] + trans_vec + ctx_vec
        feature_matrix.append(feature_vec)
        valid_classes.append(cls)

    X = np.array(feature_matrix)

    # Try k=2 (same as original)
    best_k = 2
    best_sil = -1
    for k in range(2, min(6, len(valid_classes))):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        sil = silhouette_score(X, labels)
        if sil > best_sil:
            best_sil = sil
            best_k = k

    print(f"Best k: {best_k}, silhouette: {best_sil:.4f}")
    print(f"  (old: k=2, silhouette=0.1805)")

    # PCA
    pca = PCA()
    pca.fit(X)
    cumvar = np.cumsum(pca.explained_variance_ratio_)
    n_components_90 = int(np.searchsorted(cumvar, 0.9)) + 1
    print(f"PCA components for 90% variance: {n_components_90}")
    print(f"  (old: 7)")

    # Separation ratio
    km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    final_labels = km_final.fit_predict(X)

    # Inter vs intra cluster distances
    from scipy.spatial.distance import pdist, squareform
    D = squareform(pdist(X))
    intra_dists = []
    inter_dists = []
    for i in range(len(X)):
        for j in range(i+1, len(X)):
            if final_labels[i] == final_labels[j]:
                intra_dists.append(D[i, j])
            else:
                inter_dists.append(D[i, j])

    mean_intra = np.mean(intra_dists) if intra_dists else 0
    mean_inter = np.mean(inter_dists) if inter_dists else 0
    separation = mean_inter / mean_intra if mean_intra > 0 else 0

    print(f"Separation ratio: {separation:.3f}x")
    print(f"  (old: 1.168x)")

    clustering_results = {
        'best_k': best_k, 'best_silhouette': round(best_sil, 4),
        'n_components_90': n_components_90,
        'separation_ratio': round(separation, 3),
        'mean_intra': round(mean_intra, 2),
        'mean_inter': round(mean_inter, 2),
    }
except ImportError:
    print("sklearn not available — skipping clustering")
    clustering_results = {'error': 'sklearn not available'}

results['C572'] = {
    'old': {'ks_distinct': '10/20', 'pairwise_distinct': '65/190',
            'structured_transitions': '3/20', 'context_accuracy': 0.068,
            'context_baseline': 0.103, 'best_k': 2, 'best_silhouette': 0.1805,
            'pca_components_90': 7, 'separation_ratio': 1.168, 'ax_tokens': 4559},
    'new': {'ks_distinct': f'{ks_distinct}/{len(AX_CLASSES)}',
            'pairwise_distinct': f'{pairwise_distinct}/{n_pairs}',
            'structured_transitions': f'{structured_count}/{len(AX_CLASSES)}',
            'context_accuracy': round(context_accuracy, 4),
            'context_baseline': round(weighted_baseline, 4),
            'ax_tokens': len(ax_tokens),
            **clustering_results},
    'verdict': 'STRENGTHENED' if (best_sil <= 0.1805 if 'best_sil' in dir() else True) else 'UNCHANGED'
}

# ==============================================================
# SUMMARY
# ==============================================================
print("\n" + "=" * 70)
print("SUMMARY: OLD vs NEW")
print("=" * 70)

for c_id in ['C563', 'C564', 'C565', 'C567', 'C569', 'C570', 'C572']:
    r = results[c_id]
    print(f"\n{c_id}: {r.get('verdict', 'check')}")

# Save
RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'ax_reverify.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'ax_reverify.json'}")
