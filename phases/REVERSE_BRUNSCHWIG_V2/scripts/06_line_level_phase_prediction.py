"""
Test 6: Line-Level Phase Prediction (Critical Test)

Question: Can we predict Brunschwig procedural phase from Voynich line content?

This is the CRITICAL test: if the three-tier MIDDLE structure reflects procedural
phases, then individual LINES (not just folio aggregates) should be classifiable
by their MIDDLE tier distribution.

Method:
1. Classify each B line by dominant MIDDLE tier
2. Test if early-tier lines actually appear earlier in folios
3. Compute prediction accuracy: line tier predicts folio position
"""
import sys
sys.path.insert(0, 'scripts')
from voynich import Transcript, Morphology
from collections import defaultdict
import json
import re
from scipy import stats
import numpy as np

tx = Transcript()
morph = Morphology()
b_tokens = list(tx.currier_b())

HT_PREFIXES = {'yk', 'op', 'yt', 'sa', 'pc', 'do', 'ta'}

# Define tiers
EARLY_MIDDLES = {'ksh', 'lch', 'tch', 'pch', 'te'}
MID_MIDDLES = {'k', 't', 'e'}
LATE_MIDDLES = {'ke', 'kch'}

def safe_int(s):
    try:
        return int(s)
    except:
        match = re.match(r'(\d+)', str(s))
        return int(match.group(1)) if match else 0

# Group tokens by folio-line
by_folio_line = defaultdict(list)
for t in b_tokens:
    m = morph.extract(t.word)
    if m.prefix and m.prefix in HT_PREFIXES:
        continue
    key = (t.folio, t.line)
    by_folio_line[key].append((t, m))

# Classify each line by dominant tier
line_classifications = []

for (folio, line), tokens in by_folio_line.items():
    early_count = 0
    mid_count = 0
    late_count = 0

    for t, m in tokens:
        if not m.middle:
            continue
        if m.middle in EARLY_MIDDLES:
            early_count += 1
        elif m.middle in MID_MIDDLES:
            mid_count += 1
        elif m.middle in LATE_MIDDLES:
            late_count += 1

    total = early_count + mid_count + late_count
    if total < 2:
        continue

    # Determine dominant tier
    if early_count > mid_count and early_count > late_count:
        dominant = 'EARLY'
    elif late_count > mid_count and late_count > early_count:
        dominant = 'LATE'
    elif mid_count > 0:
        dominant = 'MID'
    else:
        dominant = 'MIXED'

    line_classifications.append({
        'folio': folio,
        'line': line,
        'line_int': safe_int(line),
        'early': early_count,
        'mid': mid_count,
        'late': late_count,
        'total': total,
        'dominant': dominant
    })

# Calculate folio positions for each line
folio_line_counts = defaultdict(int)
for lc in line_classifications:
    folio_line_counts[lc['folio']] = max(folio_line_counts[lc['folio']], lc['line_int'])

for lc in line_classifications:
    max_line = folio_line_counts[lc['folio']]
    if max_line > 0:
        lc['folio_position'] = lc['line_int'] / max_line
    else:
        lc['folio_position'] = 0.5

print("=" * 70)
print("TEST 6: LINE-LEVEL PHASE PREDICTION")
print("=" * 70)
print()
print("Question: Do lines with EARLY-dominant MIDDLEs appear earlier in folios?")
print()

# Analyze by dominant tier
tier_positions = defaultdict(list)
for lc in line_classifications:
    if lc['dominant'] != 'MIXED':
        tier_positions[lc['dominant']].append(lc['folio_position'])

print("FOLIO POSITION BY LINE TIER:")
print("-" * 60)
print(f"{'Tier':<12} {'N Lines':<12} {'Mean Pos':<12} {'Std Dev':<12}")
print("-" * 60)

tier_stats = {}
for tier in ['EARLY', 'MID', 'LATE']:
    positions = tier_positions[tier]
    if positions:
        mean = np.mean(positions)
        std = np.std(positions)
        print(f"{tier:<12} {len(positions):<12} {mean:<12.3f} {std:<12.3f}")
        tier_stats[tier] = {'n': len(positions), 'mean': mean, 'std': std}

print()

# Statistical tests
print("STATISTICAL TESTS:")
print("-" * 60)

# ANOVA
if all(tier in tier_positions for tier in ['EARLY', 'MID', 'LATE']):
    f_stat, p_anova = stats.f_oneway(
        tier_positions['EARLY'],
        tier_positions['MID'],
        tier_positions['LATE']
    )
    print(f"ANOVA (EARLY vs MID vs LATE): F={f_stat:.2f}, p={p_anova:.6f}")
else:
    f_stat, p_anova = None, None

# Pairwise comparisons
if 'EARLY' in tier_positions and 'LATE' in tier_positions:
    t_stat, p_ttest = stats.ttest_ind(tier_positions['EARLY'], tier_positions['LATE'])
    print(f"t-test (EARLY vs LATE): t={t_stat:.2f}, p={p_ttest:.6f}")

    # Effect size (Cohen's d)
    early_mean = np.mean(tier_positions['EARLY'])
    late_mean = np.mean(tier_positions['LATE'])
    pooled_std = np.sqrt((np.var(tier_positions['EARLY']) + np.var(tier_positions['LATE'])) / 2)
    cohens_d = (early_mean - late_mean) / pooled_std if pooled_std > 0 else 0
    print(f"Cohen's d (EARLY vs LATE): {cohens_d:.3f}")
else:
    cohens_d = None

print()

# Correlation: tier score vs position
# Assign numeric tier: EARLY=1, MID=2, LATE=3
tier_scores = []
positions = []
for lc in line_classifications:
    if lc['dominant'] == 'EARLY':
        tier_scores.append(1)
        positions.append(lc['folio_position'])
    elif lc['dominant'] == 'MID':
        tier_scores.append(2)
        positions.append(lc['folio_position'])
    elif lc['dominant'] == 'LATE':
        tier_scores.append(3)
        positions.append(lc['folio_position'])

if tier_scores:
    rho, p_corr = stats.spearmanr(tier_scores, positions)
    print(f"Spearman correlation (tier vs position): rho={rho:.3f}, p={p_corr:.6f}")
else:
    rho, p_corr = None, None

print()

# Prediction accuracy: if EARLY tier, predict first third; if LATE tier, predict last third
correct = 0
total_pred = 0
for lc in line_classifications:
    if lc['dominant'] == 'EARLY':
        if lc['folio_position'] < 0.4:
            correct += 1
        total_pred += 1
    elif lc['dominant'] == 'LATE':
        if lc['folio_position'] > 0.6:
            correct += 1
        total_pred += 1

if total_pred > 0:
    accuracy = correct / total_pred * 100
    print(f"Position prediction accuracy (EARLY->first40%, LATE->last40%): {accuracy:.1f}%")
    print(f"  (Baseline random: 40%)")
else:
    accuracy = None

print()

# Verdict
significant = False
if p_anova and p_anova < 0.05:
    significant = True
if rho and rho > 0.1 and p_corr and p_corr < 0.05:
    significant = True

if significant and rho and rho > 0.15:
    verdict = "CONFIRMED"
elif significant:
    verdict = "SUPPORT"
elif rho and rho > 0.05:
    verdict = "WEAK"
else:
    verdict = "NOT SUPPORTED"

print("=" * 70)
print(f"VERDICT: {verdict}")
print("=" * 70)

if verdict in ["CONFIRMED", "SUPPORT"]:
    print("\nInterpretation: Line MIDDLE tier predicts folio position.")
    print("Lines with EARLY-dominant MIDDLEs appear earlier in folios,")
    print("supporting the procedural phase interpretation.")

# Output JSON
output = {
    "test": "Line-Level Phase Prediction",
    "question": "Can line MIDDLE tier predict folio position?",
    "tier_stats": tier_stats,
    "statistics": {
        "anova_f": f_stat,
        "anova_p": p_anova,
        "cohens_d": cohens_d,
        "spearman_rho": rho,
        "spearman_p": p_corr
    },
    "prediction_accuracy": accuracy,
    "verdict": verdict
}

with open('phases/REVERSE_BRUNSCHWIG_V2/results/line_level_phase_prediction.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nOutput saved to phases/REVERSE_BRUNSCHWIG_V2/results/line_level_phase_prediction.json")
