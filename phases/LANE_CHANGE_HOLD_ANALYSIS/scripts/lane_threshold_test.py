#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANE_CHANGE_HOLD_ANALYSIS - Script 3: Lane Threshold Investigation

Is lane switching threshold-driven, memoryless, or externally triggered?

Sections:
1. Load & Build EN Sequences
2. Hazard Function (conditional switch probability by run length)
3. CC Trigger Analysis
4. Inter-EN Gap Content Analysis
5. Summary & Verdict
"""

import json
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================
# SECTION 1: Load & Build EN Sequences
# ============================================================
print("=" * 60)
print("SECTION 1: Load & Build EN Sequences")
print("=" * 60)

# Load class token map
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)

token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
class_to_role[17] = 'CORE_CONTROL'  # C560/C581 correction
token_to_role = {}
for t, c in token_to_class.items():
    token_to_role[t] = class_to_role.get(c, 'UNKNOWN')

# Load EN census
with open(PROJECT_ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_census = json.load(f)
qo_classes = set(en_census['prefix_families']['QO'])
chsh_classes = set(en_census['prefix_families']['CH_SH'])
all_en_classes = qo_classes | chsh_classes

CC_CLASSES = {10, 11, 12, 17}
HAZ_CLASSES = {7, 30}
LINK_CLASSES = set()
# Find LINK class numbers (role = 'LINK')
for c, r in class_to_role.items():
    if r == 'LINK':
        LINK_CLASSES.add(c)

# Kernel map for CC sub-groups
KERNEL_MAP = {10: 'k', 11: 'h', 12: 'e', 17: 'k'}

# Load transcript and morphology
tx = Transcript()
morph = Morphology()

# Build line-organized B token data with full info
print("Building line-organized B token data...")
lines = defaultdict(list)

for token in tx.currier_b():
    cls = token_to_class.get(token.word)
    role = token_to_role.get(token.word, 'UNKNOWN')
    m = morph.extract(token.word)

    en_subfamily = None
    if cls is not None and cls in all_en_classes:
        if m.prefix == 'qo':
            en_subfamily = 'QO'
        elif m.prefix in ('ch', 'sh'):
            en_subfamily = 'CHSH'

    is_cc = cls in CC_CLASSES if cls is not None else False
    is_haz = cls in HAZ_CLASSES if cls is not None else False
    is_en = cls in all_en_classes if cls is not None else False
    is_link = cls in LINK_CLASSES if cls is not None else False

    # Determine CC sub-group
    cc_subgroup = None
    if is_cc and cls is not None:
        cc_subgroup = KERNEL_MAP.get(cls, 'unknown')

    lines[(token.folio, token.line)].append({
        'word': token.word,
        'class': cls,
        'role': role,
        'prefix': m.prefix,
        'middle': m.middle,
        'en_subfamily': en_subfamily,
        'is_cc': is_cc,
        'is_haz': is_haz,
        'is_en': is_en,
        'is_link': is_link,
        'cc_subgroup': cc_subgroup,
        'section': token.section,
    })

# Build EN sequences with positional info
MIN_EN = 4
en_line_data = []  # List of dicts with full line info

for (folio, line_num), toks in lines.items():
    en_positions = []
    for i, t in enumerate(toks):
        if t['en_subfamily'] is not None:
            en_positions.append({
                'pos': i,
                'subfamily': t['en_subfamily'],
                'middle': t['middle'],
                'class': t['class'],
            })

    if len(en_positions) >= MIN_EN:
        en_line_data.append({
            'folio': folio,
            'line': line_num,
            'section': toks[0]['section'],
            'all_tokens': toks,
            'en_positions': en_positions,
            'en_seq': [e['subfamily'] for e in en_positions],
        })

print(f"B lines: {len(lines)}")
print(f"Lines with >= {MIN_EN} EN tokens: {len(en_line_data)}")
total_en_pairs = sum(len(d['en_seq']) - 1 for d in en_line_data)
print(f"Total EN-to-EN transitions: {total_en_pairs}")

# ============================================================
# SECTION 2: Hazard Function (Conditional Switch Probability)
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: Hazard Function")
print("=" * 60)

# Collect all runs by subfamily
runs = {'QO': [], 'CHSH': []}
# Also track whether each run was terminated by a switch or by end-of-line
run_terminated = {'QO': [], 'CHSH': []}

for d in en_line_data:
    seq = d['en_seq']
    current = seq[0]
    length = 1
    for i in range(1, len(seq)):
        if seq[i] == current:
            length += 1
        else:
            runs[current].append(length)
            run_terminated[current].append(True)  # terminated by switch
            current = seq[i]
            length = 1
    # Final run (terminated by end-of-line, censored)
    runs[current].append(length)
    run_terminated[current].append(False)  # censored

# Report run length distributions
for sf in ['QO', 'CHSH']:
    r = runs[sf]
    t = run_terminated[sf]
    switched = [r[i] for i in range(len(r)) if t[i]]
    censored = [r[i] for i in range(len(r)) if not t[i]]
    print(f"\n{sf} runs: {len(r)} total ({len(switched)} switch-terminated, {len(censored)} censored)")
    c = Counter(r)
    for length in sorted(c.keys()):
        print(f"  Length {length}: {c[length]} ({c[length]/len(r)*100:.1f}%)")

# Compute hazard function: P(switch at position N | survived to N)
# Use only switch-terminated and censored runs together
print("\nHazard function (conditional switch probability):")
hazard_data = {}

for sf in ['QO', 'CHSH']:
    all_runs = runs[sf]
    terminated = run_terminated[sf]
    max_len = max(all_runs)

    hazard = {}
    for n in range(1, max_len + 1):
        # Runs alive at position N (length >= N)
        alive = sum(1 for r in all_runs if r >= n)
        # Runs that switched at exactly N (length == N AND terminated by switch)
        switched = sum(1 for i in range(len(all_runs))
                       if all_runs[i] == n and terminated[i])
        if alive >= 10:  # Minimum sample for reliable estimate
            hazard[n] = {
                'alive': alive,
                'switched': switched,
                'p_switch': switched / alive,
            }
    hazard_data[sf] = hazard

    print(f"\n{sf} hazard function:")
    print(f"  N   Alive  Switched  P(switch)")
    for n in sorted(hazard.keys()):
        h = hazard[n]
        print(f"  {n:3d}   {h['alive']:5d}    {h['switched']:5d}    {h['p_switch']:.4f}")

# Statistical test: is hazard function flat (geometric/memoryless)?
# Under geometric distribution, P(switch) = constant p for all N
# Test: correlation between run position N and P(switch at N)
print("\nMemoryless test (is hazard function flat?):")
hazard_test = {}

for sf in ['QO', 'CHSH']:
    hf = hazard_data[sf]
    if len(hf) < 3:
        print(f"  {sf}: insufficient data points for trend test")
        hazard_test[sf] = {'trend': 'INSUFFICIENT_DATA'}
        continue

    ns = sorted(hf.keys())
    ps = [hf[n]['p_switch'] for n in ns]
    weights = [hf[n]['alive'] for n in ns]

    # Weighted correlation (weight by sample size)
    # Spearman rank correlation (robust to non-linearity)
    rho, p_val = stats.spearmanr(ns, ps)

    # Also: chi-squared test against constant rate
    # Expected: overall switch rate across all positions
    total_alive = sum(hf[n]['alive'] for n in ns)
    total_switched = sum(hf[n]['switched'] for n in ns)
    overall_rate = total_switched / total_alive if total_alive > 0 else 0

    # Chi2: compare observed switches at each N to expected (alive * overall_rate)
    chi2 = 0
    dof = 0
    for n in ns:
        expected = hf[n]['alive'] * overall_rate
        if expected >= 5:  # standard chi2 requirement
            chi2 += (hf[n]['switched'] - expected) ** 2 / expected
            dof += 1
    dof = max(dof - 1, 1)  # subtract 1 for estimated rate
    chi2_p = 1 - stats.chi2.cdf(chi2, dof) if dof > 0 else 1.0

    trend = 'FLAT'
    if p_val < 0.05:
        trend = 'INCREASING' if rho > 0 else 'DECREASING'

    hazard_test[sf] = {
        'spearman_rho': float(rho),
        'spearman_p': float(p_val),
        'chi2': float(chi2),
        'chi2_dof': dof,
        'chi2_p': float(chi2_p),
        'overall_rate': float(overall_rate),
        'trend': trend,
        'n_positions': len(ns),
    }

    print(f"\n  {sf}:")
    print(f"    Overall switch rate: {overall_rate:.4f}")
    print(f"    Spearman rho: {rho:.4f}, p={p_val:.6f}")
    print(f"    Chi2 vs constant: {chi2:.3f}, dof={dof}, p={chi2_p:.6f}")
    print(f"    Trend: {trend}")

# ============================================================
# SECTION 3: CC Trigger Analysis
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: CC Trigger Analysis")
print("=" * 60)

# For each EN-to-EN transition, record:
# - switch or continuation
# - nearest upstream CC token (scanning backward from the second EN)
# - CC sub-group

transitions = []  # List of dicts

for d in en_line_data:
    toks = d['all_tokens']
    en_pos = d['en_positions']

    for idx in range(1, len(en_pos)):
        prev_en = en_pos[idx - 1]
        curr_en = en_pos[idx]
        is_switch = prev_en['subfamily'] != curr_en['subfamily']
        switch_direction = f"{prev_en['subfamily']}->{curr_en['subfamily']}" if is_switch else None

        # Scan backward from curr_en position to find nearest CC
        curr_pos = curr_en['pos']
        nearest_cc_dist = None
        nearest_cc_subgroup = None
        nearest_cc_class = None

        for scan_pos in range(curr_pos - 1, -1, -1):
            if toks[scan_pos]['is_cc']:
                nearest_cc_dist = curr_pos - scan_pos
                nearest_cc_subgroup = toks[scan_pos]['cc_subgroup']
                nearest_cc_class = toks[scan_pos]['class']
                break

        # Also check: is there a CC in the gap between prev and curr EN?
        gap_start = prev_en['pos'] + 1
        gap_end = curr_en['pos']
        cc_in_gap = any(toks[i]['is_cc'] for i in range(gap_start, gap_end))

        transitions.append({
            'is_switch': is_switch,
            'direction': switch_direction,
            'from_lane': prev_en['subfamily'],
            'to_lane': curr_en['subfamily'],
            'nearest_cc_dist': nearest_cc_dist,
            'nearest_cc_subgroup': nearest_cc_subgroup,
            'cc_in_gap': cc_in_gap,
            'section': d['section'],
        })

n_switches = sum(1 for t in transitions if t['is_switch'])
n_continues = sum(1 for t in transitions if not t['is_switch'])
print(f"Total transitions: {len(transitions)}")
print(f"  Switches: {n_switches} ({n_switches/len(transitions)*100:.1f}%)")
print(f"  Continuations: {n_continues} ({n_continues/len(transitions)*100:.1f}%)")

# Test 3a: CC proximity for switches vs continuations
switch_cc_dists = [t['nearest_cc_dist'] for t in transitions
                   if t['is_switch'] and t['nearest_cc_dist'] is not None]
cont_cc_dists = [t['nearest_cc_dist'] for t in transitions
                 if not t['is_switch'] and t['nearest_cc_dist'] is not None]

print(f"\nCC proximity:")
print(f"  Switches with upstream CC: {len(switch_cc_dists)}/{n_switches}")
print(f"  Continuations with upstream CC: {len(cont_cc_dists)}/{n_continues}")

if switch_cc_dists and cont_cc_dists:
    sw_mean = np.mean(switch_cc_dists)
    co_mean = np.mean(cont_cc_dists)
    u_stat, u_p = stats.mannwhitneyu(switch_cc_dists, cont_cc_dists, alternative='two-sided')
    n1, n2 = len(switch_cc_dists), len(cont_cc_dists)
    r_rb = 1 - (2 * u_stat) / (n1 * n2) if n1 > 0 and n2 > 0 else 0
    print(f"  Switch mean CC distance: {sw_mean:.2f}")
    print(f"  Continue mean CC distance: {co_mean:.2f}")
    print(f"  Mann-Whitney p={u_p:.6f}, r={r_rb:.4f}")
    cc_proximity_result = {
        'switch_mean': float(sw_mean),
        'continue_mean': float(co_mean),
        'u_p': float(u_p),
        'r_rb': float(r_rb),
    }
else:
    cc_proximity_result = {'note': 'insufficient data'}
    print("  Insufficient data for comparison")

# Test 3b: CC in gap predicts switch?
gap_cc_switch = sum(1 for t in transitions if t['is_switch'] and t['cc_in_gap'])
gap_cc_cont = sum(1 for t in transitions if not t['is_switch'] and t['cc_in_gap'])
gap_no_cc_switch = n_switches - gap_cc_switch
gap_no_cc_cont = n_continues - gap_cc_cont

print(f"\nCC-in-gap contingency:")
print(f"  CC in gap -> switch: {gap_cc_switch}, continue: {gap_cc_cont}")
print(f"  No CC in gap -> switch: {gap_no_cc_switch}, continue: {gap_no_cc_cont}")

table = np.array([[gap_cc_switch, gap_cc_cont],
                   [gap_no_cc_switch, gap_no_cc_cont]])
if table.min() >= 0 and table.sum() > 0:
    chi2_gap, p_gap, _, _ = stats.chi2_contingency(table, correction=True)
    # Effect size
    n_total = table.sum()
    v_gap = np.sqrt(chi2_gap / n_total) if n_total > 0 else 0
    print(f"  Chi2={chi2_gap:.3f}, p={p_gap:.6f}, V={v_gap:.4f}")

    # Switch rate with vs without CC in gap
    rate_with_cc = gap_cc_switch / (gap_cc_switch + gap_cc_cont) if (gap_cc_switch + gap_cc_cont) > 0 else 0
    rate_without_cc = gap_no_cc_switch / (gap_no_cc_switch + gap_no_cc_cont) if (gap_no_cc_switch + gap_no_cc_cont) > 0 else 0
    print(f"  Switch rate WITH CC in gap: {rate_with_cc:.4f}")
    print(f"  Switch rate WITHOUT CC in gap: {rate_without_cc:.4f}")
    cc_gap_result = {
        'chi2': float(chi2_gap),
        'p': float(p_gap),
        'v': float(v_gap),
        'rate_with_cc': float(rate_with_cc),
        'rate_without_cc': float(rate_without_cc),
    }
else:
    cc_gap_result = {'note': 'insufficient data'}

# Test 3c: CC sub-group predicts switch DIRECTION?
# Among switches, does the nearest upstream CC sub-group predict which lane we switch TO?
switch_subgroup_direction = defaultdict(lambda: Counter())
for t in transitions:
    if t['is_switch'] and t['nearest_cc_subgroup'] is not None:
        switch_subgroup_direction[t['nearest_cc_subgroup']][t['to_lane']] += 1

print(f"\nCC sub-group -> switch direction:")
for sg in sorted(switch_subgroup_direction.keys()):
    counts = switch_subgroup_direction[sg]
    total = sum(counts.values())
    qo_pct = counts.get('QO', 0) / total * 100 if total > 0 else 0
    chsh_pct = counts.get('CHSH', 0) / total * 100 if total > 0 else 0
    print(f"  {sg}: ->QO={counts.get('QO',0)} ({qo_pct:.1f}%), ->CHSH={counts.get('CHSH',0)} ({chsh_pct:.1f}%), n={total}")

# ============================================================
# SECTION 4: Inter-EN Gap Content Analysis
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: Inter-EN Gap Content Analysis")
print("=" * 60)

# For each EN-to-EN transition, characterize the gap
gap_data = []

for d in en_line_data:
    toks = d['all_tokens']
    en_pos = d['en_positions']

    for idx in range(1, len(en_pos)):
        prev_en = en_pos[idx - 1]
        curr_en = en_pos[idx]
        is_switch = prev_en['subfamily'] != curr_en['subfamily']

        gap_start = prev_en['pos'] + 1
        gap_end = curr_en['pos']
        gap_tokens = toks[gap_start:gap_end]

        # Gap features
        gap_len = len(gap_tokens)
        has_cc = any(t['is_cc'] for t in gap_tokens)
        has_haz = any(t['is_haz'] for t in gap_tokens)
        has_link = any(t['is_link'] for t in gap_tokens)
        has_ax = any(t['role'] == 'AUXILIARY' for t in gap_tokens)

        # Role counts in gap
        role_counts = Counter(t['role'] for t in gap_tokens)

        gap_data.append({
            'is_switch': is_switch,
            'gap_len': gap_len,
            'has_cc': has_cc,
            'has_haz': has_haz,
            'has_link': has_link,
            'has_ax': has_ax,
            'n_cc': role_counts.get('CORE_CONTROL', 0),
            'n_ax': role_counts.get('AUXILIARY', 0),
            'n_fl': role_counts.get('FLOW', 0),
            'n_link': role_counts.get('LINK', 0),
            'from_lane': prev_en['subfamily'],
        })

print(f"Total EN-to-EN gaps: {len(gap_data)}")
print(f"  Mean gap length: {np.mean([g['gap_len'] for g in gap_data]):.2f}")
print(f"  Gaps with CC: {sum(1 for g in gap_data if g['has_cc'])}")
print(f"  Gaps with hazard: {sum(1 for g in gap_data if g['has_haz'])}")
print(f"  Gaps with LINK: {sum(1 for g in gap_data if g['has_link'])}")

# Univariate tests: each feature vs switch
features = ['gap_len', 'has_cc', 'has_haz', 'has_link', 'has_ax', 'n_cc', 'n_ax']
feature_results = {}

for feat in features:
    sw_vals = [g[feat] for g in gap_data if g['is_switch']]
    co_vals = [g[feat] for g in gap_data if not g['is_switch']]

    if isinstance(sw_vals[0], bool):
        # Binary feature: chi-squared
        sw_true = sum(sw_vals)
        sw_false = len(sw_vals) - sw_true
        co_true = sum(co_vals)
        co_false = len(co_vals) - co_true
        tbl = np.array([[sw_true, co_true], [sw_false, co_false]])
        if tbl.min() >= 0 and tbl.sum() > 0 and sw_true + co_true > 0 and sw_false + co_false > 0:
            chi2_f, p_f, _, _ = stats.chi2_contingency(tbl, correction=True)
            v_f = np.sqrt(chi2_f / tbl.sum())
            rate_sw = sw_true / len(sw_vals) if len(sw_vals) > 0 else 0
            rate_co = co_true / len(co_vals) if len(co_vals) > 0 else 0
            print(f"\n  {feat}: switch rate with={rate_sw:.3f} without={rate_co:.3f} chi2={chi2_f:.3f} p={p_f:.6f} V={v_f:.4f}")
            feature_results[feat] = {
                'type': 'binary',
                'switch_rate': float(rate_sw),
                'continue_rate': float(rate_co),
                'chi2': float(chi2_f),
                'p': float(p_f),
                'v': float(v_f),
            }
        else:
            feature_results[feat] = {'type': 'binary', 'note': 'insufficient data'}
    else:
        # Continuous feature: Mann-Whitney
        sw_arr = np.array(sw_vals, dtype=float)
        co_arr = np.array(co_vals, dtype=float)
        u_stat, u_p = stats.mannwhitneyu(sw_arr, co_arr, alternative='two-sided')
        n1, n2 = len(sw_arr), len(co_arr)
        r_rb = 1 - (2 * u_stat) / (n1 * n2) if n1 > 0 and n2 > 0 else 0
        print(f"\n  {feat}: switch mean={sw_arr.mean():.3f} continue mean={co_arr.mean():.3f} "
              f"MW p={u_p:.6f} r={r_rb:.4f}")
        feature_results[feat] = {
            'type': 'continuous',
            'switch_mean': float(sw_arr.mean()),
            'continue_mean': float(co_arr.mean()),
            'u_p': float(u_p),
            'r_rb': float(r_rb),
        }

# Logistic regression: multivariate prediction of switch
print("\nLogistic regression: predict switch from gap features")
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, roc_auc_score

    # Build feature matrix
    X = np.array([[
        g['gap_len'],
        int(g['has_cc']),
        int(g['has_haz']),
        int(g['has_link']),
        int(g['has_ax']),
    ] for g in gap_data])
    y = np.array([int(g['is_switch']) for g in gap_data])

    # Fit full model
    lr_full = LogisticRegression(max_iter=1000, solver='lbfgs')
    lr_full.fit(X, y)
    y_pred = lr_full.predict(X)
    y_prob = lr_full.predict_proba(X)[:, 1]
    acc_full = accuracy_score(y, y_pred)

    # AUC
    try:
        auc_full = roc_auc_score(y, y_prob)
    except ValueError:
        auc_full = float('nan')

    # Null model (intercept only = base rate)
    base_rate = y.mean()
    acc_null = max(base_rate, 1 - base_rate)

    # McFadden's pseudo-R2
    ll_full = np.sum(y * np.log(y_prob + 1e-10) + (1 - y) * np.log(1 - y_prob + 1e-10))
    ll_null = np.sum(y * np.log(base_rate + 1e-10) + (1 - y) * np.log(1 - base_rate + 1e-10))
    pseudo_r2 = 1 - (ll_full / ll_null) if ll_null != 0 else 0

    feat_names = ['gap_len', 'has_cc', 'has_haz', 'has_link', 'has_ax']
    print(f"  Base switch rate: {base_rate:.4f}")
    print(f"  Null accuracy: {acc_null:.4f}")
    print(f"  Full accuracy: {acc_full:.4f}")
    print(f"  AUC: {auc_full:.4f}")
    print(f"  McFadden pseudo-R2: {pseudo_r2:.4f}")
    print(f"\n  Coefficients:")
    for name, coef in zip(feat_names, lr_full.coef_[0]):
        print(f"    {name:12s}: {coef:.4f}")
    print(f"    {'intercept':12s}: {lr_full.intercept_[0]:.4f}")

    logistic_result = {
        'base_rate': float(base_rate),
        'accuracy_null': float(acc_null),
        'accuracy_full': float(acc_full),
        'auc': float(auc_full),
        'pseudo_r2': float(pseudo_r2),
        'coefficients': {n: float(c) for n, c in zip(feat_names, lr_full.coef_[0])},
        'intercept': float(lr_full.intercept_[0]),
    }

except ImportError:
    print("  sklearn not available, skipping logistic regression")
    logistic_result = {'note': 'sklearn not available'}

# ============================================================
# SECTION 5: Summary & Verdict
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: Summary & Verdict")
print("=" * 60)

# Evaluate each model
scores = []

# 1. Memoryless test
qo_trend = hazard_test.get('QO', {}).get('trend', 'UNKNOWN')
chsh_trend = hazard_test.get('CHSH', {}).get('trend', 'UNKNOWN')
qo_chi2_p = hazard_test.get('QO', {}).get('chi2_p', 1.0)
chsh_chi2_p = hazard_test.get('CHSH', {}).get('chi2_p', 1.0)
hazard_flat = (qo_trend == 'FLAT' and chsh_trend == 'FLAT')

# 2. CC trigger
cc_gap_p = cc_gap_result.get('p', 1.0)
cc_gap_v = cc_gap_result.get('v', 0.0)
cc_explains = cc_gap_p < 0.05 and cc_gap_v > 0.05

# 3. Gap content
gap_pseudo_r2 = logistic_result.get('pseudo_r2', 0.0)
gap_auc = logistic_result.get('auc', 0.5)
gap_explains = gap_pseudo_r2 > 0.02

# Determine verdict
print("\n" + "-" * 60)
print("SCORECARD")
print("-" * 60)

verdicts = []

print(f"\n1. HAZARD FUNCTION (threshold test):")
print(f"   QO trend: {qo_trend} (Spearman p={hazard_test.get('QO',{}).get('spearman_p','N/A')})")
print(f"   CHSH trend: {chsh_trend} (Spearman p={hazard_test.get('CHSH',{}).get('spearman_p','N/A')})")
if hazard_flat:
    print(f"   -> MEMORYLESS: hazard function is flat for both lanes")
    verdicts.append('MEMORYLESS')
else:
    if qo_trend == 'INCREASING' or chsh_trend == 'INCREASING':
        print(f"   -> THRESHOLD: hazard function rises (accumulation detected)")
        verdicts.append('THRESHOLD')
    elif qo_trend == 'DECREASING' or chsh_trend == 'DECREASING':
        print(f"   -> INERTIA: hazard function falls (commitment/momentum)")
        verdicts.append('INERTIA')
    else:
        print(f"   -> MIXED: asymmetric trends")
        verdicts.append('MIXED_HAZARD')

print(f"\n2. CC TRIGGER:")
print(f"   CC-in-gap chi2 p={cc_gap_p:.6f}, V={cc_gap_v:.4f}")
if cc_explains:
    print(f"   -> CC-TRIGGERED: CC presence in gap predicts switching")
    verdicts.append('CC_TRIGGERED')
else:
    print(f"   -> CC does NOT significantly predict switching")

print(f"\n3. GAP CONTENT:")
print(f"   Logistic pseudo-R2={gap_pseudo_r2:.4f}, AUC={gap_auc:.4f}")
if gap_explains:
    print(f"   -> CONTEXT-DRIVEN: gap content predicts switching")
    verdicts.append('CONTEXT_DRIVEN')
else:
    print(f"   -> Gap content does NOT meaningfully predict switching (pseudo-R2 < 2%)")

print(f"\n{'=' * 60}")
print(f"OVERALL VERDICT: {' + '.join(verdicts) if verdicts else 'INDETERMINATE'}")
print(f"{'=' * 60}")

if 'MEMORYLESS' in verdicts and not cc_explains and not gap_explains:
    print("Lane switching is statistically memoryless. No thresholds, no triggers.")
    print("Each EN token selects its lane independently with a slight alternation bias.")
    overall = 'MEMORYLESS'
elif 'THRESHOLD' in verdicts:
    print("Evidence of threshold/accumulation behavior in lane switching.")
    overall = 'THRESHOLD'
elif cc_explains and not gap_explains:
    print("Lane switching is CC-triggered. CC tokens in the gap between EN tokens")
    print("predict whether a switch occurs, consistent with C600/C606.")
    overall = 'CC_TRIGGERED'
elif gap_explains:
    if cc_explains:
        print("Lane switching is context-driven, with CC as a contributing trigger.")
        overall = 'HYBRID_CC_CONTEXT'
    else:
        print("Lane switching is context-driven by gap content, not CC-specific.")
        overall = 'CONTEXT_DRIVEN'
else:
    print("No single model clearly explains lane switching.")
    overall = 'INDETERMINATE'

# Save results
results = {
    'line_selection': {
        'n_lines': len(en_line_data),
        'min_en': MIN_EN,
        'total_transitions': len(transitions),
        'n_switches': n_switches,
        'n_continuations': n_continues,
        'switch_rate': float(n_switches / len(transitions)),
    },
    'hazard_function': {
        'QO': {
            'run_counts': dict(Counter(runs['QO'])),
            'hazard': {str(n): v for n, v in hazard_data['QO'].items()},
            'test': hazard_test.get('QO', {}),
        },
        'CHSH': {
            'run_counts': dict(Counter(runs['CHSH'])),
            'hazard': {str(n): v for n, v in hazard_data['CHSH'].items()},
            'test': hazard_test.get('CHSH', {}),
        },
    },
    'cc_trigger': {
        'proximity': cc_proximity_result,
        'gap_contingency': cc_gap_result,
        'subgroup_direction': {
            sg: dict(counts)
            for sg, counts in switch_subgroup_direction.items()
        },
    },
    'gap_content': {
        'univariate': feature_results,
        'logistic': logistic_result,
    },
    'verdict': {
        'components': verdicts,
        'overall': overall,
    },
}

output_path = RESULTS_DIR / 'lane_threshold_test.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to {output_path}")
print("DONE.")
