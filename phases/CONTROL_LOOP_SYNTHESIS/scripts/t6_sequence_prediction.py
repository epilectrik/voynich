"""
T6: Sequence Prediction Analysis

Can we predict token position from phase membership?
- Does knowing KERNEL/LINK/FL help predict where a token appears?
- How much variance in position is explained by phase?
"""

import json
import sys
sys.path.insert(0, 'C:/git/voynich')

from collections import Counter, defaultdict
from scripts.voynich import Transcript
from scipy import stats
import numpy as np

# Load class mapping
with open('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_data = json.load(f)

token_to_role = class_data['token_to_role']

def is_link(word):
    return 'ol' in word.replace('*', '')

def is_fl(word):
    return token_to_role.get(word.replace('*', ''), 'HT') == 'FLOW_OPERATOR'

def is_ht(word):
    return token_to_role.get(word.replace('*', ''), 'HT') == 'HT'

def has_kernel(word):
    word = word.replace('*', '').lower()
    return 'k' in word or 'h' in word or 'e' in word

def get_phase(word):
    word_clean = word.replace('*', '')
    if is_fl(word_clean):
        return 'FL'
    elif is_link(word_clean) and not has_kernel(word_clean):
        return 'LINK_ONLY'
    elif has_kernel(word_clean) and not is_link(word_clean):
        return 'KERNEL_ONLY'
    elif has_kernel(word_clean) and is_link(word_clean):
        return 'KERNEL_LINK'
    elif is_ht(word_clean):
        return 'HT'
    else:
        return 'OTHER'

# Load transcript
tx = Transcript()
b_tokens = list(tx.currier_b())

lines = defaultdict(list)
for t in b_tokens:
    lines[(t.folio, t.line)].append(t)

# Collect data for prediction
positions_by_phase = defaultdict(list)
all_positions = []
all_phases = []

for key, tokens in lines.items():
    n = len(tokens)
    if n < 3:
        continue

    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if not word.strip():
            continue

        pos_norm = i / (n - 1)
        phase = get_phase(word)

        positions_by_phase[phase].append(pos_norm)
        all_positions.append(pos_norm)
        all_phases.append(phase)

print(f"Total tokens analyzed: {len(all_positions)}")

print(f"\n{'='*60}")
print(f"SEQUENCE PREDICTION ANALYSIS")
print(f"{'='*60}")

# Phase statistics
print(f"\n--- PHASE POSITION STATISTICS ---")
print(f"{'Phase':<15} {'N':>8} {'Mean':>8} {'Std':>8} {'Median':>8}")
print(f"{'-'*15} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

phase_means = {}
for phase in sorted(positions_by_phase.keys()):
    positions = positions_by_phase[phase]
    if len(positions) > 10:
        phase_means[phase] = np.mean(positions)
        print(f"{phase:<15} {len(positions):>8} {np.mean(positions):>7.3f} {np.std(positions):>7.3f} {np.median(positions):>7.3f}")

# ANOVA: Does phase explain position variance?
print(f"\n--- ANOVA: PHASE -> POSITION ---")
groups = [positions_by_phase[p] for p in positions_by_phase.keys() if len(positions_by_phase[p]) > 10]
f_stat, p_anova = stats.f_oneway(*groups)
print(f"F-statistic: {f_stat:.2f}")
print(f"p-value: {p_anova:.2e}")

# Effect size (eta-squared)
# SSB = sum of squares between groups
# SST = total sum of squares
all_pos = np.array(all_positions)
grand_mean = np.mean(all_pos)
ss_total = np.sum((all_pos - grand_mean) ** 2)

ss_between = 0
for phase, positions in positions_by_phase.items():
    if len(positions) > 10:
        group_mean = np.mean(positions)
        ss_between += len(positions) * (group_mean - grand_mean) ** 2

eta_squared = ss_between / ss_total
print(f"Eta-squared (variance explained): {eta_squared:.4f} ({eta_squared*100:.2f}%)")

# Prediction accuracy: Can we predict position from phase?
print(f"\n--- PREDICTION ACCURACY ---")

# Naive baseline: predict grand mean for all
baseline_mse = np.mean((all_pos - grand_mean) ** 2)
baseline_mae = np.mean(np.abs(all_pos - grand_mean))

# Phase-based prediction: predict group mean
predicted = np.array([phase_means.get(p, grand_mean) for p in all_phases])
phase_mse = np.mean((all_pos - predicted) ** 2)
phase_mae = np.mean(np.abs(all_pos - predicted))

print(f"Baseline (predict grand mean):")
print(f"  MSE: {baseline_mse:.4f}")
print(f"  MAE: {baseline_mae:.4f}")

print(f"\nPhase-based prediction (predict group mean):")
print(f"  MSE: {phase_mse:.4f}")
print(f"  MAE: {phase_mae:.4f}")

improvement_mse = (baseline_mse - phase_mse) / baseline_mse * 100
improvement_mae = (baseline_mae - phase_mae) / baseline_mae * 100
print(f"\nImprovement:")
print(f"  MSE reduction: {improvement_mse:.1f}%")
print(f"  MAE reduction: {improvement_mae:.1f}%")

# Position prediction by tercile
print(f"\n--- TERCILE PREDICTION ---")
# Can we predict if a token is in first/middle/last third?
tercile_correct = 0
tercile_total = 0

for i, (pos, phase) in enumerate(zip(all_positions, all_phases)):
    actual_tercile = 0 if pos < 0.33 else (1 if pos < 0.67 else 2)

    # Predict tercile from phase mean
    if phase in phase_means:
        pred_pos = phase_means[phase]
        pred_tercile = 0 if pred_pos < 0.33 else (1 if pred_pos < 0.67 else 2)

        tercile_total += 1
        if actual_tercile == pred_tercile:
            tercile_correct += 1

baseline_tercile = 1/3  # Random guess
phase_tercile_acc = tercile_correct / tercile_total if tercile_total > 0 else 0
print(f"Tercile prediction accuracy: {phase_tercile_acc*100:.1f}% (baseline: {baseline_tercile*100:.1f}%)")
print(f"Improvement over random: {(phase_tercile_acc - baseline_tercile)*100:.1f}pp")

# Most predictive phases
print(f"\n--- MOST PREDICTIVE PHASES ---")
print(f"Phases with strongest positional signal (furthest from 0.5):")
phase_deviations = [(p, abs(m - 0.5)) for p, m in phase_means.items()]
phase_deviations.sort(key=lambda x: -x[1])
for phase, dev in phase_deviations[:5]:
    n = len(positions_by_phase[phase])
    mean = phase_means[phase]
    print(f"  {phase}: mean={mean:.3f}, deviation={dev:.3f}, n={n}")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")

if eta_squared > 0.01:
    print(f"Phase membership DOES explain position variance (eta²={eta_squared:.4f})")
else:
    print(f"Phase membership does NOT strongly explain position variance (eta²={eta_squared:.4f})")

if improvement_mae > 5:
    print(f"Phase-based prediction is {improvement_mae:.1f}% better than baseline")
else:
    print(f"Phase-based prediction offers minimal improvement ({improvement_mae:.1f}%)")

print(f"\nConclusion:")
if eta_squared > 0.01 and p_anova < 0.001:
    print(f"  Phases have SIGNIFICANT positional preferences")
    print(f"  The control loop has spatial structure within lines")
else:
    print(f"  Phases are NOT strongly position-constrained")
    print(f"  Control loop operates more by sequence than by absolute position")
