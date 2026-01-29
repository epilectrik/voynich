#!/usr/bin/env python3
"""
UN COMPOSITIONAL MECHANICS - Script 2: Role Prediction

Predicts ICC role membership for UN tokens using morphological features.

Sections:
1. PREFIX-Based Role Assignment
2. PREFIX+SUFFIX Joint Prediction
3. MIDDLE-Based Role Assignment
4. Consensus Prediction (combined)
"""

import os
import sys
import json
import numpy as np
from collections import Counter, defaultdict

os.chdir('C:/git/voynich')
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

# ==============================================================================
# LOAD DATA
# ==============================================================================

print("=" * 70)
print("UN COMPOSITIONAL MECHANICS - Script 2: Role Prediction")
print("=" * 70)

tx = Transcript()
morph = Morphology()

b_tokens = list(tx.currier_b())
print(f"Total Currier B tokens: {len(b_tokens)}")

with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
class_to_role = class_map['class_to_role']

ROLE_ABBREV = {
    'CORE_CONTROL': 'CC',
    'ENERGY_OPERATOR': 'EN',
    'FLOW_OPERATOR': 'FL',
    'FREQUENT_OPERATOR': 'FQ',
    'AUXILIARY': 'AX',
}

# Build classified and UN token lists with morphology
classified = []  # (token, role, morph_analysis)
un_list = []     # (token, morph_analysis)

for t in b_tokens:
    m = morph.extract(t.word)
    if t.word in token_to_class:
        cls = str(token_to_class[t.word])
        role = ROLE_ABBREV.get(class_to_role.get(cls, ''), '?')
        classified.append((t, role, m))
    else:
        un_list.append((t, m))

print(f"Classified: {len(classified)}, UN: {len(un_list)}")

# ==============================================================================
# BUILD LOOKUP TABLES
# ==============================================================================

# PREFIX -> role distribution (from classified)
prefix_role_dist = defaultdict(Counter)
for t, role, m in classified:
    p = m.prefix if m.prefix else '_NONE_'
    prefix_role_dist[p][role] += 1

# SUFFIX -> role distribution (from classified)
suffix_role_dist = defaultdict(Counter)
for t, role, m in classified:
    s = m.suffix if m.suffix else '_NONE_'
    suffix_role_dist[s][role] += 1

# PREFIX+SUFFIX -> role distribution
prefix_suffix_role_dist = defaultdict(Counter)
for t, role, m in classified:
    p = m.prefix if m.prefix else '_NONE_'
    s = m.suffix if m.suffix else '_NONE_'
    prefix_suffix_role_dist[(p, s)][role] += 1

# MIDDLE -> role distribution
middle_role_dist = defaultdict(Counter)
for t, role, m in classified:
    if m.middle:
        middle_role_dist[m.middle][role] += 1

def predict_from_dist(dist):
    """Return (predicted_role, confidence, total) from a Counter."""
    if not dist:
        return None, 0.0, 0
    total = sum(dist.values())
    mode = dist.most_common(1)[0]
    return mode[0], mode[1] / total, total

# ==============================================================================
# SECTION 1: PREFIX-BASED ROLE ASSIGNMENT
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 1: PREFIX-BASED ROLE ASSIGNMENT")
print("=" * 70)

prefix_predictions = []
for t, m in un_list:
    p = m.prefix if m.prefix else '_NONE_'
    dist = prefix_role_dist.get(p)
    if dist:
        role, conf, n = predict_from_dist(dist)
        prefix_predictions.append((t.word, role, conf, n))
    else:
        prefix_predictions.append((t.word, None, 0.0, 0))

# Summary
prefix_assigned = Counter()
prefix_unassigned = 0
prefix_confidences = []
for word, role, conf, n in prefix_predictions:
    if role:
        prefix_assigned[role] += 1
        prefix_confidences.append(conf)
    else:
        prefix_unassigned += 1

total_assigned = sum(prefix_assigned.values())
print(f"\nPREFIX-based prediction:")
print(f"  Assigned:   {total_assigned} ({total_assigned/len(un_list)*100:.1f}%)")
print(f"  Unassigned: {prefix_unassigned} ({prefix_unassigned/len(un_list)*100:.1f}%)")

print(f"\n  {'Role':<6} {'Count':>8} {'% of UN':>10}")
print(f"  {'-'*28}")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    count = prefix_assigned.get(role, 0)
    pct = count / len(un_list) * 100
    print(f"  {role:<6} {count:>8} {pct:>9.1f}%")

if prefix_confidences:
    print(f"\n  Mean confidence: {np.mean(prefix_confidences):.3f}")
    print(f"  Median confidence: {np.median(prefix_confidences):.3f}")
    print(f"  >90% confidence: {sum(1 for c in prefix_confidences if c > 0.9)} ({sum(1 for c in prefix_confidences if c > 0.9)/len(prefix_confidences)*100:.1f}%)")
    print(f"  >70% confidence: {sum(1 for c in prefix_confidences if c > 0.7)} ({sum(1 for c in prefix_confidences if c > 0.7)/len(prefix_confidences)*100:.1f}%)")

# ==============================================================================
# SECTION 2: PREFIX+SUFFIX JOINT PREDICTION
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 2: PREFIX+SUFFIX JOINT PREDICTION")
print("=" * 70)

joint_predictions = []
for t, m in un_list:
    p = m.prefix if m.prefix else '_NONE_'
    s = m.suffix if m.suffix else '_NONE_'
    dist = prefix_suffix_role_dist.get((p, s))
    if dist:
        role, conf, n = predict_from_dist(dist)
        joint_predictions.append((t.word, role, conf, n))
    else:
        joint_predictions.append((t.word, None, 0.0, 0))

joint_assigned = Counter()
joint_unassigned = 0
joint_confidences = []
for word, role, conf, n in joint_predictions:
    if role:
        joint_assigned[role] += 1
        joint_confidences.append(conf)
    else:
        joint_unassigned += 1

total_joint = sum(joint_assigned.values())
print(f"\nPREFIX+SUFFIX joint prediction:")
print(f"  Assigned:   {total_joint} ({total_joint/len(un_list)*100:.1f}%)")
print(f"  Unassigned: {joint_unassigned} ({joint_unassigned/len(un_list)*100:.1f}%)")

print(f"\n  {'Role':<6} {'Count':>8} {'% of UN':>10}")
print(f"  {'-'*28}")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    count = joint_assigned.get(role, 0)
    pct = count / len(un_list) * 100
    print(f"  {role:<6} {count:>8} {pct:>9.1f}%")

if joint_confidences:
    print(f"\n  Mean confidence: {np.mean(joint_confidences):.3f}")
    print(f"  Median confidence: {np.median(joint_confidences):.3f}")
    print(f"  >90% confidence: {sum(1 for c in joint_confidences if c > 0.9)} ({sum(1 for c in joint_confidences if c > 0.9)/len(joint_confidences)*100:.1f}%)")
    print(f"  >70% confidence: {sum(1 for c in joint_confidences if c > 0.7)} ({sum(1 for c in joint_confidences if c > 0.7)/len(joint_confidences)*100:.1f}%)")

# Comparison: does joint improve over prefix-only?
agree = 0
disagree = 0
joint_better = 0
prefix_better = 0
for (_, p_role, p_conf, _), (_, j_role, j_conf, _) in zip(prefix_predictions, joint_predictions):
    if p_role and j_role:
        if p_role == j_role:
            agree += 1
        else:
            disagree += 1
            if j_conf > p_conf:
                joint_better += 1
            else:
                prefix_better += 1

print(f"\n  PREFIX vs JOINT agreement (both assigned):")
print(f"    Agree: {agree}")
print(f"    Disagree: {disagree}")
if disagree > 0:
    print(f"    Joint wins: {joint_better}, Prefix wins: {prefix_better}")

# ==============================================================================
# SECTION 3: MIDDLE-BASED ROLE ASSIGNMENT
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 3: MIDDLE-BASED ROLE ASSIGNMENT")
print("=" * 70)

middle_predictions = []
for t, m in un_list:
    if m.middle and m.middle in middle_role_dist:
        dist = middle_role_dist[m.middle]
        role, conf, n = predict_from_dist(dist)
        middle_predictions.append((t.word, role, conf, n, m.middle))
    else:
        middle_predictions.append((t.word, None, 0.0, 0, m.middle))

mid_assigned = Counter()
mid_unassigned = 0
mid_confidences = []
for word, role, conf, n, mid in middle_predictions:
    if role:
        mid_assigned[role] += 1
        mid_confidences.append(conf)
    else:
        mid_unassigned += 1

total_mid = sum(mid_assigned.values())
print(f"\nMIDDLE-based prediction:")
print(f"  Assigned (MIDDLE in classified vocab):   {total_mid} ({total_mid/len(un_list)*100:.1f}%)")
print(f"  Unassigned (novel MIDDLE):               {mid_unassigned} ({mid_unassigned/len(un_list)*100:.1f}%)")

print(f"\n  {'Role':<6} {'Count':>8} {'% of UN':>10}")
print(f"  {'-'*28}")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    count = mid_assigned.get(role, 0)
    pct = count / len(un_list) * 100
    print(f"  {role:<6} {count:>8} {pct:>9.1f}%")

if mid_confidences:
    print(f"\n  Mean confidence: {np.mean(mid_confidences):.3f}")
    print(f"  >90% confidence: {sum(1 for c in mid_confidences if c > 0.9)} ({sum(1 for c in mid_confidences if c > 0.9)/len(mid_confidences)*100:.1f}%)")

# ==============================================================================
# SECTION 4: CONSENSUS PREDICTION
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 4: CONSENSUS PREDICTION")
print("=" * 70)

# For each UN token, combine PREFIX, MIDDLE, and PREFIX+SUFFIX predictions
consensus = []
for i in range(len(un_list)):
    word = un_list[i][0].word

    p_role = prefix_predictions[i][1]
    p_conf = prefix_predictions[i][2]
    j_role = joint_predictions[i][1]
    j_conf = joint_predictions[i][2]
    m_role = middle_predictions[i][1]
    m_conf = middle_predictions[i][2]

    votes = {}
    if p_role:
        votes['prefix'] = (p_role, p_conf)
    if j_role:
        votes['joint'] = (j_role, j_conf)
    if m_role:
        votes['middle'] = (m_role, m_conf)

    if not votes:
        consensus.append((word, None, 'none', 0.0))
        continue

    # Count role votes
    role_votes = Counter()
    role_max_conf = {}
    for method, (role, conf) in votes.items():
        role_votes[role] += 1
        if role not in role_max_conf or conf > role_max_conf[role]:
            role_max_conf[role] = conf

    best_role = role_votes.most_common(1)[0][0]
    n_agree = role_votes[best_role]
    n_methods = len(votes)

    if n_methods >= 2 and n_agree == n_methods:
        level = 'high'
    elif n_methods >= 2 and n_agree >= 2:
        level = 'medium'
    elif n_methods == 1:
        level = 'single'
    else:
        level = 'low'

    consensus.append((word, best_role, level, role_max_conf[best_role]))

# Summary
consensus_roles = Counter()
confidence_levels = Counter()
for word, role, level, conf in consensus:
    if role:
        consensus_roles[role] += 1
    confidence_levels[level] += 1

print(f"\nConsensus prediction summary:")
print(f"  {'Level':<10} {'Count':>8} {'%':>8}")
print(f"  {'-'*30}")
for level in ['high', 'medium', 'single', 'low', 'none']:
    count = confidence_levels.get(level, 0)
    pct = count / len(un_list) * 100
    print(f"  {level:<10} {count:>8} {pct:>7.1f}%")

print(f"\nPredicted role distribution (all assigned):")
print(f"  {'Role':<6} {'Count':>8} {'% of UN':>10}")
print(f"  {'-'*28}")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    count = consensus_roles.get(role, 0)
    pct = count / len(un_list) * 100
    print(f"  {role:<6} {count:>8} {pct:>9.1f}%")

total_assigned_all = sum(consensus_roles.values())
print(f"\n  Total assigned: {total_assigned_all} ({total_assigned_all/len(un_list)*100:.1f}%)")
print(f"  Unassigned: {len(un_list) - total_assigned_all}")

# Combined distribution: classified + predicted UN
print(f"\n--- COMBINED DISTRIBUTION: Classified + Predicted UN ---")
cls_role_counts = Counter(role for _, role, _ in classified)
print(f"  {'Role':<6} {'Classified':>10} {'Predicted UN':>13} {'Combined':>10} {'% of B':>8}")
print(f"  {'-'*50}")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    cls_c = cls_role_counts.get(role, 0)
    un_c = consensus_roles.get(role, 0)
    combined = cls_c + un_c
    pct = combined / len(b_tokens) * 100
    print(f"  {role:<6} {cls_c:>10} {un_c:>13} {combined:>10} {pct:>7.1f}%")

unresolved = len(un_list) - total_assigned_all
print(f"  {'UN':>6} {'---':>10} {'---':>13} {unresolved:>10} {unresolved/len(b_tokens)*100:>7.1f}%")

# High-confidence only
print(f"\n--- HIGH-CONFIDENCE ONLY ---")
high_conf_roles = Counter()
for word, role, level, conf in consensus:
    if level == 'high' and role:
        high_conf_roles[role] += 1

print(f"  {'Role':<6} {'High-conf':>10} {'% of UN':>10}")
print(f"  {'-'*30}")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    count = high_conf_roles.get(role, 0)
    pct = count / len(un_list) * 100
    print(f"  {role:<6} {count:>10} {pct:>9.1f}%")
total_high = sum(high_conf_roles.values())
print(f"  Total high-confidence: {total_high} ({total_high/len(un_list)*100:.1f}%)")

# ==============================================================================
# SAVE RESULTS
# ==============================================================================

results = {
    'prefix_prediction': {
        'assigned': total_assigned,
        'assigned_pct': round(total_assigned / len(un_list) * 100, 1),
        'by_role': dict(prefix_assigned),
        'mean_confidence': round(float(np.mean(prefix_confidences)), 3) if prefix_confidences else 0,
    },
    'joint_prediction': {
        'assigned': total_joint,
        'assigned_pct': round(total_joint / len(un_list) * 100, 1),
        'by_role': dict(joint_assigned),
        'mean_confidence': round(float(np.mean(joint_confidences)), 3) if joint_confidences else 0,
    },
    'middle_prediction': {
        'assigned': total_mid,
        'assigned_pct': round(total_mid / len(un_list) * 100, 1),
        'by_role': dict(mid_assigned),
        'mean_confidence': round(float(np.mean(mid_confidences)), 3) if mid_confidences else 0,
    },
    'consensus': {
        'by_role': dict(consensus_roles),
        'confidence_levels': dict(confidence_levels),
        'total_assigned': total_assigned_all,
        'total_assigned_pct': round(total_assigned_all / len(un_list) * 100, 1),
        'high_confidence_by_role': dict(high_conf_roles),
        'high_confidence_total': total_high,
    },
}

output_path = 'phases/UN_COMPOSITIONAL_MECHANICS/results/un_role_prediction.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\n{'=' * 70}")
print("UN ROLE PREDICTION COMPLETE")
print(f"{'=' * 70}")
