#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T3: CC Routing Gate Estimation

Characterizes the CC trigger effect on lane initialization and tests
CC-hazard gate interaction.

Method:
  - Classify CC tokens by subtype (DAIIN, OL, OL_DERIVED, OTHER_CC)
  - Track EN lane at offsets +1, +2, +3 after each CC
  - Compare lane distributions to T1 baseline
  - Estimate P(lane | cc_type, offset) -- the CC routing gate
  - Test rapid decay: routing effect should decay to baseline by offset +2 (C817)
  - CC-HAZARD INTERACTION: Find cases where both CC and hazard precede an EN token

Targets (C817):
  - DAIIN->CHSH at offset +1: ~91%
  - OL->CHSH at offset +1: ~93%
  - OL_DERIVED->QO at offset +1: ~57%
  - Decay to baseline by offset +2
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================
# SECTION 1: Load & Prepare
# ============================================================
print("=" * 60)
print("T3: CC Routing Gate Estimation")
print("=" * 60)

# Load class token map
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)

token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
class_to_role[17] = 'CORE_CONTROL'  # C560/C581 correction

# Load EN census
with open(PROJECT_ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_census = json.load(f)
qo_classes = set(en_census['prefix_families']['QO'])
chsh_classes = set(en_census['prefix_families']['CH_SH'])
all_en_classes = qo_classes | chsh_classes

CC_CLASSES = {10, 11, 12, 17}
HAZ_CLASSES = {7, 30}

# Load T1 baseline results
with open(RESULTS_DIR / 't1_transition_matrices.json') as f:
    t1_results = json.load(f)

# Baseline lane distribution from T1 unfiltered matrix stationary distribution
# Use unfiltered as "general population" baseline
uf = t1_results['unfiltered_matrix']
# Stationary: pi_QO = P(CHSH->QO) / (P(QO->CHSH) + P(CHSH->QO))
baseline_pi_qo = uf['CHSH_to_QO'] / (uf['QO_to_CHSH'] + uf['CHSH_to_QO'])
baseline_pi_chsh = 1 - baseline_pi_qo

print(f"Baseline lane distribution (T1 stationary): QO={baseline_pi_qo:.4f}, CHSH={baseline_pi_chsh:.4f}")

# Load transcript and morphology
tx = Transcript()
morph = Morphology()


def get_lane(word):
    """Determine lane from PREFIX."""
    m = morph.extract(word)
    prefix = m.prefix or ''
    if prefix == 'qo':
        return 'QO'
    elif prefix in ('ch', 'sh'):
        return 'CHSH'
    return None


def classify_cc(word, cls):
    """Classify CC subtype."""
    if cls is None or cls not in CC_CLASSES:
        return None
    if word == 'daiin':
        return 'DAIIN'
    elif word == 'ol':
        return 'OL'
    elif cls == 17:
        return 'OL_DERIVED'
    else:
        return 'OTHER_CC'


# Build line-organized B token data with full annotations
print("\nBuilding line-organized B token data...")
lines = defaultdict(list)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    cls = token_to_class.get(w)

    en_lane = None
    if cls is not None and cls in all_en_classes:
        en_lane = get_lane(w)

    is_cc = cls in CC_CLASSES if cls is not None else False
    is_haz = cls in HAZ_CLASSES if cls is not None else False
    cc_type = classify_cc(w, cls)

    lines[(token.folio, token.line)].append({
        'word': w,
        'class': cls,
        'en_lane': en_lane,
        'is_cc': is_cc,
        'is_haz': is_haz,
        'cc_type': cc_type,
    })

print(f"B lines: {len(lines)}")


# ============================================================
# SECTION 2: CC Routing Gate - Lane at Offsets from CC
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: CC Routing Gate Estimation")
print("=" * 60)

# For each CC token, find EN tokens at offsets +1, +2, +3 (counting EN tokens only)
# offset = count of EN tokens encountered after the CC within the same line
MAX_OFFSET = 3
CC_TYPES = ['DAIIN', 'OL', 'OL_DERIVED', 'OTHER_CC']

# gate_counts[cc_type][offset] = Counter({'QO': n, 'CHSH': n})
gate_counts = {ct: {off: Counter() for off in range(1, MAX_OFFSET + 1)} for ct in CC_TYPES}

for (folio, line_num), toks in lines.items():
    for i, t in enumerate(toks):
        if t['cc_type'] is None:
            continue
        cc_type = t['cc_type']

        # Count EN tokens after this CC in the same line
        en_offset = 0
        for j in range(i + 1, len(toks)):
            if toks[j]['en_lane'] is not None:
                en_offset += 1
                if en_offset <= MAX_OFFSET:
                    gate_counts[cc_type][en_offset][toks[j]['en_lane']] += 1
                else:
                    break

# Print and analyze gate distributions
print("\nCC Routing Gate: P(lane | cc_type, offset)")
print("-" * 50)

gate_results = {}
for cc_type in CC_TYPES:
    print(f"\n  {cc_type}:")
    gate_results[cc_type] = {}

    for offset in range(1, MAX_OFFSET + 1):
        counts = gate_counts[cc_type][offset]
        n_qo = counts['QO']
        n_chsh = counts['CHSH']
        n_total = n_qo + n_chsh

        if n_total < 5:
            print(f"    Offset +{offset}: n={n_total} (too few, skipping)")
            gate_results[cc_type][f'offset_{offset}'] = {
                'n': int(n_total), 'qo': int(n_qo), 'chsh': int(n_chsh),
                'skip': True, 'reason': 'too_few'
            }
            continue

        p_qo = n_qo / n_total
        p_chsh = n_chsh / n_total

        # Chi-squared vs baseline (expected from stationary distribution)
        expected_qo = n_total * baseline_pi_qo
        expected_chsh = n_total * baseline_pi_chsh
        chi2 = ((n_qo - expected_qo) ** 2 / expected_qo +
                (n_chsh - expected_chsh) ** 2 / expected_chsh)
        p_val = 1 - stats.chi2.cdf(chi2, df=1)
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "NS"

        # Effect size: deviation from baseline
        deviation_qo = p_qo - baseline_pi_qo
        deviation_chsh = p_chsh - baseline_pi_chsh

        print(f"    Offset +{offset}: QO={n_qo}({p_qo*100:.1f}%) CHSH={n_chsh}({p_chsh*100:.1f}%) "
              f"n={n_total}  chi2={chi2:.2f} {sig}")

        gate_results[cc_type][f'offset_{offset}'] = {
            'n': int(n_total),
            'qo': int(n_qo),
            'chsh': int(n_chsh),
            'p_qo': float(p_qo),
            'p_chsh': float(p_chsh),
            'chi2_vs_baseline': float(chi2),
            'p_value': float(p_val),
            'significant': bool(p_val < 0.05),
            'deviation_from_baseline_qo': float(deviation_qo),
            'deviation_from_baseline_chsh': float(deviation_chsh),
            'skip': False,
        }


# ============================================================
# SECTION 3: Decay Analysis (C817)
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: Decay Analysis (C817)")
print("=" * 60)
print("C817 predicts: routing effect decays to baseline by offset +2")

decay_results = {}
for cc_type in CC_TYPES:
    print(f"\n  {cc_type}:")
    decay_results[cc_type] = {}

    off1 = gate_results[cc_type].get('offset_1', {})
    off2 = gate_results[cc_type].get('offset_2', {})

    if off1.get('skip', True) or off2.get('skip', True):
        print(f"    Insufficient data for decay test")
        decay_results[cc_type] = {'testable': False}
        continue

    # The key question: is offset+2 significantly different from baseline?
    # If NOT significant at offset+2 -> decay confirmed
    off2_sig = off2['significant']
    off1_sig = off1['significant']

    # Also check if offset+1 deviation magnitude > offset+2 deviation magnitude
    off1_dev = max(abs(off1['deviation_from_baseline_qo']),
                   abs(off1['deviation_from_baseline_chsh']))
    off2_dev = max(abs(off2['deviation_from_baseline_qo']),
                   abs(off2['deviation_from_baseline_chsh']))

    decay_confirmed = not off2_sig  # offset+2 not significantly different from baseline
    magnitude_decays = off2_dev < off1_dev

    print(f"    Offset +1: sig={off1_sig}, max_dev={off1_dev:.4f}")
    print(f"    Offset +2: sig={off2_sig}, max_dev={off2_dev:.4f}")
    print(f"    Decay to baseline by +2: {'YES' if decay_confirmed else 'NO'}")
    print(f"    Magnitude decreases: {'YES' if magnitude_decays else 'NO'}")

    decay_results[cc_type] = {
        'testable': True,
        'offset_1_significant': bool(off1_sig),
        'offset_1_max_deviation': float(off1_dev),
        'offset_2_significant': bool(off2_sig),
        'offset_2_max_deviation': float(off2_dev),
        'decay_to_baseline_by_2': bool(decay_confirmed),
        'magnitude_decays': bool(magnitude_decays),
    }


# ============================================================
# SECTION 4: C817 Target Comparison
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: C817 Target Comparison")
print("=" * 60)

targets = {
    'DAIIN': {'lane': 'CHSH', 'target': 0.91},
    'OL': {'lane': 'CHSH', 'target': 0.93},
    'OL_DERIVED': {'lane': 'QO', 'target': 0.57},
}

target_results = {}
for cc_type, spec in targets.items():
    off1 = gate_results[cc_type].get('offset_1', {})
    if off1.get('skip', True):
        print(f"\n  {cc_type}: insufficient data for target comparison")
        target_results[cc_type] = {'testable': False}
        continue

    if spec['lane'] == 'CHSH':
        actual = off1['p_chsh']
    else:
        actual = off1['p_qo']

    delta = abs(actual - spec['target'])
    match = delta < 0.10  # Within 10pp of target

    print(f"\n  {cc_type} -> {spec['lane']} at offset +1:")
    print(f"    Target: {spec['target']*100:.0f}%")
    print(f"    Actual: {actual*100:.1f}%")
    print(f"    Delta:  {delta*100:.1f}pp")
    print(f"    Match:  {'YES' if match else 'NO'} (threshold: 10pp)")

    target_results[cc_type] = {
        'testable': True,
        'expected_lane': spec['lane'],
        'target_rate': float(spec['target']),
        'actual_rate': float(actual),
        'delta': float(delta),
        'within_10pp': bool(match),
    }


# ============================================================
# SECTION 5: CC-HAZARD Interaction
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: CC-HAZARD Interaction")
print("=" * 60)

# Find EN tokens where BOTH a CC and a hazard token precede them
# within 2 absolute positions in the same line
interaction_cases = []  # list of {cc_type, en_lane, cc_dist, haz_dist}

# Also collect CC-only and HAZ-only cases for comparison
cc_only_lanes = Counter()
haz_only_lanes = Counter()
both_lanes = Counter()

for (folio, line_num), toks in lines.items():
    for i, t in enumerate(toks):
        if t['en_lane'] is None:
            continue

        # Look back up to 2 positions for CC and hazard tokens
        cc_found = None  # (cc_type, distance)
        haz_found = None  # distance
        for lookback in range(1, 3):  # 1 and 2 positions back
            j = i - lookback
            if j < 0:
                break
            if toks[j]['cc_type'] is not None and cc_found is None:
                cc_found = (toks[j]['cc_type'], lookback)
            if toks[j]['is_haz'] and haz_found is None:
                haz_found = lookback

        if cc_found is not None and haz_found is not None:
            # Both CC and hazard precede this EN token
            interaction_cases.append({
                'folio': folio,
                'line': line_num,
                'en_pos': i,
                'en_lane': t['en_lane'],
                'cc_type': cc_found[0],
                'cc_dist': cc_found[1],
                'haz_dist': haz_found,
            })
            both_lanes[t['en_lane']] += 1
        elif cc_found is not None:
            cc_only_lanes[t['en_lane']] += 1
        elif haz_found is not None:
            haz_only_lanes[t['en_lane']] += 1

n_interaction = len(interaction_cases)
print(f"\nEN tokens with BOTH CC and hazard within 2 positions: {n_interaction}")
print(f"EN tokens with CC only within 2 positions: {sum(cc_only_lanes.values())}")
print(f"EN tokens with hazard only within 2 positions: {sum(haz_only_lanes.values())}")

# Analyze interaction cases
print(f"\nCC-HAZARD interaction lane distribution:")
if n_interaction > 0:
    n_both_qo = both_lanes.get('QO', 0)
    n_both_chsh = both_lanes.get('CHSH', 0)
    n_both_total = n_both_qo + n_both_chsh
    if n_both_total > 0:
        p_both_qo = n_both_qo / n_both_total
        p_both_chsh = n_both_chsh / n_both_total
        print(f"  Both present: QO={n_both_qo}({p_both_qo*100:.1f}%) CHSH={n_both_chsh}({p_both_chsh*100:.1f}%) n={n_both_total}")
    else:
        p_both_qo = 0.0
        p_both_chsh = 0.0

    # CC-only distribution
    n_cc_qo = cc_only_lanes.get('QO', 0)
    n_cc_chsh = cc_only_lanes.get('CHSH', 0)
    n_cc_total = n_cc_qo + n_cc_chsh
    if n_cc_total > 0:
        p_cc_qo = n_cc_qo / n_cc_total
        p_cc_chsh = n_cc_chsh / n_cc_total
        print(f"  CC only:      QO={n_cc_qo}({p_cc_qo*100:.1f}%) CHSH={n_cc_chsh}({p_cc_chsh*100:.1f}%) n={n_cc_total}")
    else:
        p_cc_qo = 0.0
        p_cc_chsh = 0.0

    # HAZ-only distribution
    n_haz_qo = haz_only_lanes.get('QO', 0)
    n_haz_chsh = haz_only_lanes.get('CHSH', 0)
    n_haz_total = n_haz_qo + n_haz_chsh
    if n_haz_total > 0:
        p_haz_qo = n_haz_qo / n_haz_total
        p_haz_chsh = n_haz_chsh / n_haz_total
        print(f"  HAZ only:     QO={n_haz_qo}({p_haz_qo*100:.1f}%) CHSH={n_haz_chsh}({p_haz_chsh*100:.1f}%) n={n_haz_total}")
    else:
        p_haz_qo = 0.0
        p_haz_chsh = 0.0

    # Interaction breakdown by CC type
    print(f"\n  Interaction breakdown by CC type:")
    interaction_by_cc = defaultdict(Counter)
    for case in interaction_cases:
        interaction_by_cc[case['cc_type']][case['en_lane']] += 1

    for ct in CC_TYPES:
        counts = interaction_by_cc.get(ct, Counter())
        ct_total = counts['QO'] + counts['CHSH']
        if ct_total > 0:
            print(f"    {ct}: QO={counts['QO']} CHSH={counts['CHSH']} n={ct_total}")

    # Determine interaction model
    # If CC dominates hazard -> deterministic priority (CC wins)
    # If hazard shifts CC routing -> stochastic interaction
    # Compare: P(lane | both) vs P(lane | cc_only) -- if similar, CC dominates
    if n_both_total >= 5 and n_cc_total >= 5:
        # Fisher exact test: does adding hazard shift the distribution?
        table = np.array([[n_both_qo, n_both_chsh],
                          [n_cc_qo, n_cc_chsh]])
        _, fisher_p = stats.fisher_exact(table)

        # Effect size: difference in QO rates
        qo_shift = p_both_qo - p_cc_qo

        print(f"\n  Interaction model test:")
        print(f"    P(QO | both) = {p_both_qo:.4f}")
        print(f"    P(QO | cc_only) = {p_cc_qo:.4f}")
        print(f"    Shift: {qo_shift:+.4f}")
        print(f"    Fisher exact p = {fisher_p:.4f}")

        if fisher_p > 0.05:
            interaction_model = 'CC_PRIORITY'
            model_desc = 'CC dominates: hazard presence does not significantly alter CC routing'
        elif abs(qo_shift) < 0.10:
            interaction_model = 'WEAK_INTERACTION'
            model_desc = f'Weak stochastic interaction: hazard shifts QO rate by {qo_shift:+.3f}'
        else:
            interaction_model = 'STOCHASTIC_INTERACTION'
            model_desc = f'Stochastic interaction: hazard shifts QO rate by {qo_shift:+.3f}'

        print(f"    Model: {interaction_model}")
        print(f"    {model_desc}")

        # Estimate hierarchical weight
        # If CC alone gives P(QO) = p_cc, and both gives P(QO) = p_both,
        # then hazard_weight = (p_both - p_cc) / (p_haz - p_cc) if denominator nonzero
        if n_haz_total >= 5 and abs(p_haz_qo - p_cc_qo) > 0.01:
            hazard_weight = (p_both_qo - p_cc_qo) / (p_haz_qo - p_cc_qo)
            hazard_weight = max(0.0, min(1.0, hazard_weight))  # clamp [0,1]
            cc_weight = 1.0 - hazard_weight
            print(f"    Estimated weights: CC={cc_weight:.3f}, HAZ={hazard_weight:.3f}")
        else:
            hazard_weight = None
            cc_weight = None
            print(f"    Cannot estimate weights (insufficient hazard-only data)")
    else:
        interaction_model = 'INSUFFICIENT_DATA'
        model_desc = f'Too few cases (both={n_both_total}, cc_only={n_cc_total})'
        fisher_p = None
        qo_shift = None
        hazard_weight = None
        cc_weight = None
        print(f"\n  Interaction model: {model_desc}")
else:
    interaction_model = 'NO_CASES'
    model_desc = 'No cases where both CC and hazard precede same EN token'
    n_both_total = 0
    p_both_qo = 0.0
    p_both_chsh = 0.0
    n_cc_total = sum(cc_only_lanes.values())
    p_cc_qo = 0.0
    p_cc_chsh = 0.0
    n_haz_total = sum(haz_only_lanes.values())
    p_haz_qo = 0.0
    p_haz_chsh = 0.0
    fisher_p = None
    qo_shift = None
    hazard_weight = None
    cc_weight = None
    print(f"  {model_desc}")


# ============================================================
# SECTION 6: Estimated Gate Parameters
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: Estimated Gate Parameters")
print("=" * 60)

gate_params = {}
for cc_type in CC_TYPES:
    off1 = gate_results[cc_type].get('offset_1', {})
    if off1.get('skip', True):
        print(f"\n  {cc_type}: insufficient data")
        gate_params[cc_type] = {'estimable': False}
        continue

    p_qo = off1['p_qo']
    p_chsh = off1['p_chsh']
    n = off1['n']

    # Dominant lane at offset +1
    dominant = 'QO' if p_qo > p_chsh else 'CHSH'
    strength = max(p_qo, p_chsh)

    # 95% CI for dominant lane rate (Wilson score interval)
    z = 1.96
    p_hat = strength
    denom = 1 + z ** 2 / n
    center = (p_hat + z ** 2 / (2 * n)) / denom
    margin = z * np.sqrt(p_hat * (1 - p_hat) / n + z ** 2 / (4 * n ** 2)) / denom
    ci_low = max(0.0, center - margin)
    ci_high = min(1.0, center + margin)

    print(f"\n  {cc_type}:")
    print(f"    Dominant lane: {dominant}")
    print(f"    P({dominant} | {cc_type}, +1) = {strength:.4f}  95% CI [{ci_low:.4f}, {ci_high:.4f}]")
    print(f"    n = {n}")

    gate_params[cc_type] = {
        'estimable': True,
        'dominant_lane': dominant,
        'p_dominant': float(strength),
        'p_qo': float(p_qo),
        'p_chsh': float(p_chsh),
        'ci_95': [float(ci_low), float(ci_high)],
        'n': int(n),
    }


# ============================================================
# SECTION 7: Verdict
# ============================================================
print("\n" + "=" * 60)
print("SECTION 7: Verdict")
print("=" * 60)

# Checks:
# 1. DAIIN routes to CHSH at +1 with high probability
# 2. OL routes to CHSH at +1 with high probability
# 3. OL_DERIVED routes to QO at +1 with moderate probability
# 4. Decay to baseline by +2

check_daiin_routing = (
    target_results.get('DAIIN', {}).get('testable', False) and
    target_results['DAIIN']['actual_rate'] > 0.70
)
check_ol_routing = (
    target_results.get('OL', {}).get('testable', False) and
    target_results['OL']['actual_rate'] > 0.70
)
check_old_routing = (
    target_results.get('OL_DERIVED', {}).get('testable', False) and
    target_results['OL_DERIVED']['actual_rate'] > 0.50
)

# Decay check: count how many CC types decay to baseline by +2
decay_pass_count = 0
decay_testable_count = 0
for cc_type in CC_TYPES:
    dr = decay_results.get(cc_type, {})
    if dr.get('testable', False):
        decay_testable_count += 1
        if dr['decay_to_baseline_by_2']:
            decay_pass_count += 1

check_decay = decay_testable_count > 0 and decay_pass_count >= decay_testable_count / 2

checks = {
    'daiin_routes_chsh': bool(check_daiin_routing),
    'ol_routes_chsh': bool(check_ol_routing),
    'ol_derived_routes_qo': bool(check_old_routing),
    'decay_to_baseline': bool(check_decay),
}

n_pass = sum(checks.values())
n_total_checks = len(checks)

if n_pass == n_total_checks:
    verdict = 'PASS'
elif n_pass >= n_total_checks - 1:
    verdict = 'STRONG'
elif n_pass >= 2:
    verdict = 'PARTIAL'
else:
    verdict = 'FAIL'

print(f"\nChecks:")
for name, passed in checks.items():
    print(f"  {name}: {'PASS' if passed else 'FAIL'}")
print(f"\nT3 VERDICT: {verdict} ({n_pass}/{n_total_checks} checks passed)")


# ============================================================
# SECTION 8: Save Results
# ============================================================
print("\n" + "=" * 60)
print("SECTION 8: Save Results")
print("=" * 60)

results = {
    'test': 'T3_cc_routing_gate_estimation',
    'description': 'CC routing gate estimation: P(lane | cc_type, offset) with CC-hazard interaction',
    'baseline': {
        'source': 't1_transition_matrices.json',
        'stationary_QO': float(baseline_pi_qo),
        'stationary_CHSH': float(baseline_pi_chsh),
    },
    'gate_distributions': {},
    'c817_targets': {},
    'decay_analysis': {},
    'gate_parameters': {},
    'cc_hazard_interaction': {},
    'checks': checks,
    'verdict': verdict,
}

# Gate distributions per CC type, per offset
for cc_type in CC_TYPES:
    results['gate_distributions'][cc_type] = {}
    for offset in range(1, MAX_OFFSET + 1):
        key = f'offset_{offset}'
        if key in gate_results[cc_type]:
            results['gate_distributions'][cc_type][key] = gate_results[cc_type][key]

# C817 targets
results['c817_targets'] = target_results

# Decay analysis
results['decay_analysis'] = decay_results
results['decay_analysis']['summary'] = {
    'testable_types': int(decay_testable_count),
    'decay_confirmed_types': int(decay_pass_count),
}

# Gate parameters
results['gate_parameters'] = gate_params

# CC-hazard interaction
interaction_result = {
    'n_both': int(n_both_total),
    'n_cc_only': int(sum(cc_only_lanes.values())),
    'n_haz_only': int(sum(haz_only_lanes.values())),
    'both_lane_dist': {
        'QO': int(both_lanes.get('QO', 0)),
        'CHSH': int(both_lanes.get('CHSH', 0)),
    },
    'cc_only_lane_dist': {
        'QO': int(cc_only_lanes.get('QO', 0)),
        'CHSH': int(cc_only_lanes.get('CHSH', 0)),
    },
    'haz_only_lane_dist': {
        'QO': int(haz_only_lanes.get('QO', 0)),
        'CHSH': int(haz_only_lanes.get('CHSH', 0)),
    },
    'interaction_model': interaction_model,
    'model_description': model_desc,
}

if fisher_p is not None:
    interaction_result['fisher_p'] = float(fisher_p)
if qo_shift is not None:
    interaction_result['qo_shift_with_hazard'] = float(qo_shift)
if hazard_weight is not None:
    interaction_result['estimated_hazard_weight'] = float(hazard_weight)
    interaction_result['estimated_cc_weight'] = float(cc_weight)

# Breakdown by CC type
interaction_by_cc_result = {}
interaction_by_cc_data = defaultdict(Counter)
for case in interaction_cases:
    interaction_by_cc_data[case['cc_type']][case['en_lane']] += 1
for ct in CC_TYPES:
    counts = interaction_by_cc_data.get(ct, Counter())
    ct_total = counts['QO'] + counts['CHSH']
    if ct_total > 0:
        interaction_by_cc_result[ct] = {
            'QO': int(counts['QO']),
            'CHSH': int(counts['CHSH']),
            'n': int(ct_total),
            'p_qo': float(counts['QO'] / ct_total),
            'p_chsh': float(counts['CHSH'] / ct_total),
        }

interaction_result['by_cc_type'] = interaction_by_cc_result
results['cc_hazard_interaction'] = interaction_result

out_path = RESULTS_DIR / 't3_cc_routing_gate.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved: {out_path}")
