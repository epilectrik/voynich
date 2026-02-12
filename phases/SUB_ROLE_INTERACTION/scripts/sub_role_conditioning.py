"""
SUB_ROLE_INTERACTION Script 2: Conditioning Analysis

Test whether sub-group routing depends on REGIME, line position,
specific trigger tokens (CC), AX scaffolding flow, and hazard context.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scripts.voynich import Transcript

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'data' / 'regime_folio_mapping.json'
HAZARD_FILE = BASE / 'phases/SMALL_ROLE_ANATOMY/results/sr_hazard_anatomy.json'
TRANS_RESULTS = BASE / 'phases/SUB_ROLE_INTERACTION/results/sub_role_transitions.json'
RESULTS = BASE / 'phases/SUB_ROLE_INTERACTION/results'

# Sub-group definitions (identical to Script 1)
ICC_CC = {10, 11, 12, 17}
ICC_EN = {8} | set(range(31, 50)) - {38, 40}
ICC_FL = {7, 30, 38, 40}
ICC_FQ = {9, 13, 14, 23}

SUBGROUP_MAP = {}

EN_QO = {32, 33, 36, 44, 45, 46, 49}
EN_CHSH = {8, 31, 34, 35, 37, 39, 42, 43, 47, 48}
EN_MINOR = {41}
for c in EN_QO: SUBGROUP_MAP[c] = ('EN', 'QO')
for c in EN_CHSH: SUBGROUP_MAP[c] = ('EN', 'CHSH')
for c in EN_MINOR: SUBGROUP_MAP[c] = ('EN', 'MINOR')

FQ_CONN = {9}
FQ_PAIR = {13, 14}
FQ_CLOSER = {23}
for c in FQ_CONN: SUBGROUP_MAP[c] = ('FQ', 'CONN')
for c in FQ_PAIR: SUBGROUP_MAP[c] = ('FQ', 'PAIR')
for c in FQ_CLOSER: SUBGROUP_MAP[c] = ('FQ', 'CLOSER')

FL_HAZ = {7, 30}
FL_SAFE = {38, 40}
for c in FL_HAZ: SUBGROUP_MAP[c] = ('FL', 'HAZ')
for c in FL_SAFE: SUBGROUP_MAP[c] = ('FL', 'SAFE')

AX_INIT = {4, 5, 6, 24, 26}
AX_MED = {1, 2, 3, 16, 18, 27, 28, 29}
AX_FINAL = {15, 19, 20, 21, 22, 25}
for c in AX_INIT: SUBGROUP_MAP[c] = ('AX', 'INIT')
for c in AX_MED: SUBGROUP_MAP[c] = ('AX', 'MED')
for c in AX_FINAL: SUBGROUP_MAP[c] = ('AX', 'FINAL')

CC_DAIIN = {10}
CC_OL = {11}
CC_OLD = {17}
for c in CC_DAIIN: SUBGROUP_MAP[c] = ('CC', 'DAIIN')
for c in CC_OL: SUBGROUP_MAP[c] = ('CC', 'OL')
for c in CC_OLD: SUBGROUP_MAP[c] = ('CC', 'OL_D')

OPERATIONAL_ROLES = {'EN', 'FQ', 'FL', 'CC'}

def get_subgroup_label(cls):
    if cls is None:
        return 'UN'
    sg = SUBGROUP_MAP.get(cls)
    if sg is None:
        return 'UN'
    return f"{sg[0]}_{sg[1]}"

def get_role(cls):
    if cls is None:
        return 'UN'
    sg = SUBGROUP_MAP.get(cls)
    if sg:
        return sg[0]
    return 'UN'

# ============================================================
# LOAD DATA
# ============================================================
print("=" * 70)
print("SUB-ROLE INTERACTION: CONDITIONING ANALYSIS")
print("=" * 70)

tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

with open(REGIME_FILE) as f:
    regime_data = json.load(f)
folio_regime = {folio: data['regime'] for folio, data in regime_data['regime_assignments'].items()}

with open(HAZARD_FILE) as f:
    hazard_data = json.load(f)

# Build line structures with position info
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    sg = get_subgroup_label(cls)
    role = get_role(cls)
    lines[(token.folio, token.line)].append({
        'word': word, 'class': cls, 'subgroup': sg, 'role': role,
        'folio': token.folio
    })

# Compute normalized positions within each line
for (folio, line_id), line_tokens in lines.items():
    n = len(line_tokens)
    for i, tok in enumerate(line_tokens):
        tok['position'] = i / (n - 1) if n > 1 else 0.5
        tok['is_initial'] = (i == 0)
        tok['is_final'] = (i == n - 1)
        tok['regime'] = folio_regime.get(folio, 'UNKNOWN')

results = {}

# ============================================================
# SECTION 1: REGIME-CONDITIONED TRANSITIONS
# ============================================================
print("\n" + "=" * 70)
print("SECTION 1: REGIME-CONDITIONED TRANSITIONS")
print("=" * 70)

# Focus on the 5 Bonferroni-significant pairs from Script 1:
# AX->EN, AX->FQ, EN->FQ, FQ->EN, CC->EN
FOCUS_PAIRS = [
    ('AX', 'EN', ['AX_INIT', 'AX_MED', 'AX_FINAL'], ['EN_QO', 'EN_CHSH']),
    ('AX', 'FQ', ['AX_INIT', 'AX_MED', 'AX_FINAL'], ['FQ_CONN', 'FQ_PAIR', 'FQ_CLOSER']),
    ('EN', 'FQ', ['EN_QO', 'EN_CHSH'], ['FQ_CONN', 'FQ_PAIR', 'FQ_CLOSER']),
    ('FQ', 'EN', ['FQ_CONN', 'FQ_PAIR', 'FQ_CLOSER'], ['EN_QO', 'EN_CHSH']),
    ('CC', 'EN', ['CC_DAIIN', 'CC_OL', 'CC_OL_D'], ['EN_QO', 'EN_CHSH']),
]

REGIMES = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']

regime_results = {}

for src_role, dst_role, src_sgs, dst_sgs in FOCUS_PAIRS:
    pair_key = f"{src_role}->{dst_role}"
    print(f"\n--- {pair_key} by REGIME ---")

    # Drop EN_MINOR from dst if present (too sparse)
    dst_sgs_clean = [d for d in dst_sgs if d != 'EN_MINOR']

    # Build per-REGIME matrices
    regime_matrices = {}
    for regime in REGIMES:
        mat = np.zeros((len(src_sgs), len(dst_sgs_clean)), dtype=int)
        for (folio, line_id), line_tokens in lines.items():
            if folio_regime.get(folio) != regime:
                continue
            for i in range(len(line_tokens) - 1):
                src = line_tokens[i]['subgroup']
                dst = line_tokens[i + 1]['subgroup']
                if src in src_sgs and dst in dst_sgs_clean:
                    si = src_sgs.index(src)
                    di = dst_sgs_clean.index(dst)
                    mat[si, di] += 1
        regime_matrices[regime] = mat

    # Print per-regime totals and enrichment patterns
    regime_pair_data = {}
    for regime in REGIMES:
        mat = regime_matrices[regime]
        total = mat.sum()
        if total < 10:
            print(f"  {regime}: n={total} (insufficient)")
            regime_pair_data[regime] = {'n': int(total), 'verdict': 'insufficient'}
            continue

        # Enrichment
        row_sums = mat.sum(axis=1)
        col_sums = mat.sum(axis=0)
        expected = np.outer(row_sums, col_sums) / total
        enr = np.where(expected > 0, mat / expected, 0)

        print(f"  {regime} (n={total}):")
        for i, s in enumerate(src_sgs):
            parts = []
            for j, d in enumerate(dst_sgs_clean):
                e = enr[i, j]
                marker = '+' if e > 1.3 else ('-' if e < 0.7 else ' ')
                parts.append(f"{d}={e:.2f}{marker}")
            print(f"    {s}: {', '.join(parts)}")

        regime_pair_data[regime] = {
            'n': int(total),
            'enrichment': {src_sgs[i]: {dst_sgs_clean[j]: round(float(enr[i, j]), 3)
                           for j in range(len(dst_sgs_clean))}
                           for i in range(len(src_sgs))}
        }

    # Homogeneity test: pool all REGIME matrices into one stacked contingency table
    # Flatten each regime's matrix to a 1D vector of proportions and compare
    pooled_matrices = []
    pooled_labels = []
    for regime in REGIMES:
        mat = regime_matrices[regime]
        if mat.sum() >= 10:
            pooled_matrices.append(mat)
            pooled_labels.append(regime)

    if len(pooled_matrices) >= 2:
        # Stack: rows = regimes, cols = flattened cells
        stacked = np.array([m.flatten() for m in pooled_matrices])
        # Chi-squared homogeneity: are the regime distributions the same?
        # Only use cells where total > 0
        col_mask = stacked.sum(axis=0) > 0
        stacked_filtered = stacked[:, col_mask]
        if stacked_filtered.shape[1] >= 2:
            try:
                chi2_h, p_h, dof_h, _ = stats.chi2_contingency(stacked_filtered)
                print(f"  Homogeneity: chi2={chi2_h:.2f}, df={dof_h}, p={p_h:.2e}")
                regime_pair_data['homogeneity'] = {
                    'chi2': round(float(chi2_h), 2),
                    'p': float(p_h),
                    'dof': int(dof_h),
                    'significant': bool(p_h < 0.05)
                }
            except ValueError:
                print(f"  Homogeneity: test failed (degenerate matrix)")
                regime_pair_data['homogeneity'] = {'verdict': 'degenerate'}
    else:
        regime_pair_data['homogeneity'] = {'verdict': 'insufficient_regimes'}

    regime_results[pair_key] = regime_pair_data

results['regime_conditioning'] = regime_results

# ============================================================
# SECTION 2: POSITIONAL CONDITIONING
# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: POSITIONAL CONDITIONING")
print("=" * 70)

# Split transitions by position zone of the SOURCE token
ZONES = {'INITIAL': (0, 0.2), 'MEDIAL': (0.2, 0.8), 'FINAL': (0.8, 1.01)}

positional_results = {}

for src_role, dst_role, src_sgs, dst_sgs in FOCUS_PAIRS[:3]:  # AX->EN, AX->FQ, EN->FQ
    pair_key = f"{src_role}->{dst_role}"
    dst_sgs_clean = [d for d in dst_sgs if d != 'EN_MINOR']
    print(f"\n--- {pair_key} by position zone ---")

    zone_data = {}
    for zone_name, (lo, hi) in ZONES.items():
        mat = np.zeros((len(src_sgs), len(dst_sgs_clean)), dtype=int)
        for (folio, line_id), line_tokens in lines.items():
            for i in range(len(line_tokens) - 1):
                pos = line_tokens[i]['position']
                if pos < lo or pos >= hi:
                    continue
                src = line_tokens[i]['subgroup']
                dst = line_tokens[i + 1]['subgroup']
                if src in src_sgs and dst in dst_sgs_clean:
                    si = src_sgs.index(src)
                    di = dst_sgs_clean.index(dst)
                    mat[si, di] += 1

        total = mat.sum()
        if total < 10:
            print(f"  {zone_name}: n={total} (insufficient)")
            zone_data[zone_name] = {'n': int(total), 'verdict': 'insufficient'}
            continue

        row_sums = mat.sum(axis=1)
        col_sums = mat.sum(axis=0)
        expected = np.outer(row_sums, col_sums) / total
        enr = np.where(expected > 0, mat / expected, 0)

        print(f"  {zone_name} (n={total}):")
        for i, s in enumerate(src_sgs):
            if row_sums[i] == 0:
                continue
            parts = []
            for j, d in enumerate(dst_sgs_clean):
                e = enr[i, j]
                marker = '+' if e > 1.3 else ('-' if e < 0.7 else ' ')
                parts.append(f"{d}={e:.2f}{marker}")
            print(f"    {s}: {', '.join(parts)}")

        zone_data[zone_name] = {
            'n': int(total),
            'enrichment': {src_sgs[i]: {dst_sgs_clean[j]: round(float(enr[i, j]), 3)
                           for j in range(len(dst_sgs_clean))}
                           for i in range(len(src_sgs)) if row_sums[i] > 0}
        }

    positional_results[pair_key] = zone_data

results['positional_conditioning'] = positional_results

# ============================================================
# SECTION 3: CC TRIGGER PROFILES
# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: CC TRIGGER PROFILES")
print("=" * 70)

# For each CC sub-group, what sub-group distribution follows?
cc_sgs = ['CC_DAIIN', 'CC_OL', 'CC_OL_D']
all_operational_sgs = [
    'EN_QO', 'EN_CHSH', 'EN_MINOR',
    'FQ_CONN', 'FQ_PAIR', 'FQ_CLOSER',
    'FL_HAZ', 'FL_SAFE',
]

# Follower distributions
cc_followers = {sg: Counter() for sg in cc_sgs}
non_cc_baseline = Counter()
total_non_cc = 0

for (folio, line_id), line_tokens in lines.items():
    for i in range(len(line_tokens) - 1):
        src = line_tokens[i]['subgroup']
        dst = line_tokens[i + 1]['subgroup']
        if src in cc_sgs and dst in all_operational_sgs:
            cc_followers[src][dst] += 1
        elif src not in cc_sgs and src != 'UN' and dst in all_operational_sgs:
            non_cc_baseline[dst] += 1
            total_non_cc += 1

# Print follower distributions
cc_trigger_results = {}
for cc_sg in cc_sgs:
    total = sum(cc_followers[cc_sg].values())
    print(f"\n{cc_sg} -> operational tokens (n={total}):")
    if total == 0:
        cc_trigger_results[cc_sg] = {'n': 0}
        continue

    dist = {}
    for op_sg in all_operational_sgs:
        count = cc_followers[cc_sg][op_sg]
        rate = count / total if total > 0 else 0
        base_rate = non_cc_baseline[op_sg] / total_non_cc if total_non_cc > 0 else 0
        enr = rate / base_rate if base_rate > 0 else 0
        marker = '+' if enr > 1.3 else ('-' if enr < 0.7 else ' ')
        if count > 0:
            print(f"  {op_sg:>12}: {count:>4} ({rate:.3f}) base={base_rate:.3f} enrich={enr:.2f}{marker}")
        dist[op_sg] = {'count': count, 'rate': round(rate, 4), 'enrichment': round(enr, 3)}

    cc_trigger_results[cc_sg] = {'n': total, 'distribution': dist}

# Chi-squared: are the CC sub-group follower distributions different?
# Build contingency: rows = CC sub-groups, cols = operational sub-groups
cc_obs = np.zeros((len(cc_sgs), len(all_operational_sgs)), dtype=int)
for i, cc_sg in enumerate(cc_sgs):
    for j, op_sg in enumerate(all_operational_sgs):
        cc_obs[i, j] = cc_followers[cc_sg][op_sg]

# Only keep columns with at least 1 observation
col_mask = cc_obs.sum(axis=0) > 0
cc_obs_filtered = cc_obs[:, col_mask]
op_sgs_filtered = [all_operational_sgs[j] for j in range(len(all_operational_sgs)) if col_mask[j]]

if cc_obs_filtered.sum() >= 20:
    chi2_cc, p_cc, dof_cc, _ = stats.chi2_contingency(cc_obs_filtered)
    print(f"\nCC sub-group follower independence: chi2={chi2_cc:.2f}, df={dof_cc}, p={p_cc:.2e}")
    cc_trigger_results['independence_test'] = {
        'chi2': round(float(chi2_cc), 2),
        'p': float(p_cc),
        'dof': int(dof_cc),
        'significant': bool(p_cc < 0.05)
    }

results['cc_triggers'] = cc_trigger_results

# ============================================================
# SECTION 4: AX SCAFFOLDING FLOW
# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: AX SCAFFOLDING FLOW")
print("=" * 70)

# For each AX sub-group, find the FIRST non-AX, non-UN token that follows
ax_sgs = ['AX_INIT', 'AX_MED', 'AX_FINAL']
operational_sgs_full = [
    'EN_QO', 'EN_CHSH', 'EN_MINOR',
    'FQ_CONN', 'FQ_PAIR', 'FQ_CLOSER',
    'FL_HAZ', 'FL_SAFE',
    'CC_DAIIN', 'CC_OL', 'CC_OL_D',
]

ax_flow = {sg: Counter() for sg in ax_sgs}

for (folio, line_id), line_tokens in lines.items():
    for i in range(len(line_tokens)):
        src = line_tokens[i]['subgroup']
        if src not in ax_sgs:
            continue
        # Find first non-AX, non-UN token after this one
        for j in range(i + 1, len(line_tokens)):
            dst = line_tokens[j]['subgroup']
            dst_role = dst.split('_')[0] if dst != 'UN' else 'UN'
            if dst_role not in ('AX', 'UN'):
                ax_flow[src][dst] += 1
                break

ax_flow_results = {}
print("\nAX sub-group -> first operational token:")
for ax_sg in ax_sgs:
    total = sum(ax_flow[ax_sg].values())
    print(f"\n  {ax_sg} (n={total}):")
    if total == 0:
        ax_flow_results[ax_sg] = {'n': 0}
        continue

    # Baseline: overall operational sub-group frequencies
    all_ops_total = sum(sum(ax_flow[s].values()) for s in ax_sgs)
    all_ops = Counter()
    for s in ax_sgs:
        all_ops += ax_flow[s]

    dist = {}
    for op_sg in operational_sgs_full:
        count = ax_flow[ax_sg][op_sg]
        rate = count / total if total > 0 else 0
        base_rate = all_ops[op_sg] / all_ops_total if all_ops_total > 0 else 0
        enr = rate / base_rate if base_rate > 0 else 0
        if count > 0:
            marker = '+' if enr > 1.3 else ('-' if enr < 0.7 else ' ')
            print(f"    {op_sg:>12}: {count:>4} ({rate:.3f}) enrich={enr:.2f}{marker}")
        dist[op_sg] = {'count': count, 'rate': round(rate, 4), 'enrichment': round(enr, 3)}

    ax_flow_results[ax_sg] = {'n': total, 'distribution': dist}

# Chi-squared: do AX sub-groups route differently?
ax_obs = np.zeros((len(ax_sgs), len(operational_sgs_full)), dtype=int)
for i, ax_sg in enumerate(ax_sgs):
    for j, op_sg in enumerate(operational_sgs_full):
        ax_obs[i, j] = ax_flow[ax_sg][op_sg]

col_mask = ax_obs.sum(axis=0) > 0
ax_obs_filtered = ax_obs[:, col_mask]

if ax_obs_filtered.sum() >= 20:
    chi2_ax, p_ax, dof_ax, _ = stats.chi2_contingency(ax_obs_filtered)
    print(f"\nAX routing independence: chi2={chi2_ax:.2f}, df={dof_ax}, p={p_ax:.2e}")
    ax_flow_results['independence_test'] = {
        'chi2': round(float(chi2_ax), 2),
        'p': float(p_ax),
        'dof': int(dof_ax),
        'significant': bool(p_ax < 0.05)
    }

results['ax_scaffolding'] = ax_flow_results

# ============================================================
# SECTION 5: HAZARD SUB-GROUP CONTEXT
# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: HAZARD SUB-GROUP CONTEXT")
print("=" * 70)

# Map each hazard event to sub-group pairs
hazard_events = hazard_data.get('hazard_events_sample', [])
print(f"\nHazard events in sample: {len(hazard_events)}")

hazard_subgroup_pairs = []
for event in hazard_events:
    cls_a = event['class_a']
    cls_b = event['class_b']
    sg_a = get_subgroup_label(cls_a)
    sg_b = get_subgroup_label(cls_b)
    hazard_subgroup_pairs.append({
        'source': sg_a,
        'target': sg_b,
        'hazard_class': event['hazard_class'],
        'section': event['section'],
        'folio': event['folio']
    })

# Count sub-group pairs
pair_counts = Counter()
for hp in hazard_subgroup_pairs:
    pair_counts[(hp['source'], hp['target'])] += 1

print(f"\nHazard sub-group pairs:")
for (src, dst), count in pair_counts.most_common():
    print(f"  {src:>12} -> {dst:<12}: {count}")

# Count by source sub-group
src_counts = Counter()
tgt_counts = Counter()
for hp in hazard_subgroup_pairs:
    src_counts[hp['source']] += 1
    tgt_counts[hp['target']] += 1

print(f"\nHazard sources by sub-group:")
for sg, count in src_counts.most_common():
    print(f"  {sg:>12}: {count}")

print(f"\nHazard targets by sub-group:")
for sg, count in tgt_counts.most_common():
    print(f"  {sg:>12}: {count}")

results['hazard_subgroups'] = {
    'n_events': len(hazard_subgroup_pairs),
    'pair_counts': {f"{s}->{t}": c for (s, t), c in pair_counts.most_common()},
    'source_counts': dict(src_counts),
    'target_counts': dict(tgt_counts),
    'events': hazard_subgroup_pairs
}

# ============================================================
# SECTION 6: CONTEXT CLASSIFIER
# ============================================================
print("\n" + "=" * 70)
print("SECTION 6: CONTEXT CLASSIFIER")
print("=" * 70)

# For each token, predict its sub-group from (left_subgroup, right_subgroup)
# Only predict for classified (non-UN) tokens
context_data = []
for (folio, line_id), line_tokens in lines.items():
    for i in range(len(line_tokens)):
        sg = line_tokens[i]['subgroup']
        if sg == 'UN':
            continue
        left_sg = line_tokens[i - 1]['subgroup'] if i > 0 else 'BOUNDARY'
        right_sg = line_tokens[i + 1]['subgroup'] if i < len(line_tokens) - 1 else 'BOUNDARY'
        context_data.append({
            'subgroup': sg,
            'left': left_sg,
            'right': right_sg
        })

# Majority baseline
sg_counts = Counter(d['subgroup'] for d in context_data)
majority_sg = sg_counts.most_common(1)[0][0]
majority_baseline = sg_counts.most_common(1)[0][1] / len(context_data)

# Weighted random
weighted_random = sum((c / len(context_data)) ** 2 for c in sg_counts.values())

# Rule-based classifier: for each (left, right) pair, predict most common sub-group
context_predictions = defaultdict(Counter)
for d in context_data:
    key = (d['left'], d['right'])
    context_predictions[key][d['subgroup']] += 1

correct = 0
for d in context_data:
    key = (d['left'], d['right'])
    predicted = context_predictions[key].most_common(1)[0][0]
    if predicted == d['subgroup']:
        correct += 1

accuracy = correct / len(context_data)
improvement_majority = accuracy - majority_baseline
improvement_weighted = accuracy - weighted_random

print(f"\nContext classifier (sub-group prediction):")
print(f"  Samples: {len(context_data)}")
print(f"  Sub-groups: {len(sg_counts)}")
print(f"  Majority baseline ({majority_sg}): {majority_baseline:.4f}")
print(f"  Weighted random: {weighted_random:.4f}")
print(f"  Accuracy: {accuracy:.4f}")
print(f"  Improvement over majority: {improvement_majority:+.4f}")
print(f"  Improvement over weighted: {improvement_weighted:+.4f}")

# Also test: predict ROLE (coarser) vs SUB-GROUP (finer)
# Role prediction
role_data = []
for d in context_data:
    role = d['subgroup'].split('_')[0]
    role_data.append({'role': role, 'left': d['left'], 'right': d['right']})

role_counts = Counter(d['role'] for d in role_data)
role_majority = role_counts.most_common(1)[0][1] / len(role_data)
role_weighted = sum((c / len(role_data)) ** 2 for c in role_counts.values())

role_predictions = defaultdict(Counter)
for d in role_data:
    key = (d['left'], d['right'])
    role_predictions[key][d['role']] += 1

role_correct = 0
for d in role_data:
    key = (d['left'], d['right'])
    predicted = role_predictions[key].most_common(1)[0][0]
    if predicted == d['role']:
        role_correct += 1

role_accuracy = role_correct / len(role_data)
role_improvement = role_accuracy - role_majority

print(f"\nRole-level prediction (coarser):")
print(f"  Majority baseline: {role_majority:.4f}")
print(f"  Accuracy: {role_accuracy:.4f}")
print(f"  Improvement: {role_improvement:+.4f}")
print(f"\n  Sub-group adds {improvement_majority - role_improvement:+.4f} over role")

results['context_classifier'] = {
    'n_samples': len(context_data),
    'n_subgroups': len(sg_counts),
    'majority_baseline': round(majority_baseline, 4),
    'weighted_random': round(weighted_random, 4),
    'accuracy': round(accuracy, 4),
    'improvement_majority': round(improvement_majority, 4),
    'improvement_weighted': round(improvement_weighted, 4),
    'role_majority_baseline': round(role_majority, 4),
    'role_accuracy': round(role_accuracy, 4),
    'role_improvement': round(role_improvement, 4),
    'subgroup_vs_role_delta': round(improvement_majority - role_improvement, 4)
}

# Save results
RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'sub_role_conditioning.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'sub_role_conditioning.json'}")
