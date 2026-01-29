"""
T4: CC Positional Profile

Where do CC classes appear in lines?
Is there positional differentiation between Group A (10,11) and Group B (12,17)?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
token_to_class = ctm['token_to_class']

CC_CLASSES = [10, 11, 12, 17]
CC_GROUP_A = {10, 11}
CC_GROUP_B = {12, 17}

print("="*70)
print("CC POSITIONAL PROFILE")
print("="*70)

# Build line data with positions
lines_data = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    key = (token.folio, token.line)

    if w in token_to_class:
        cls = int(token_to_class[w])
    else:
        cls = None

    lines_data[key].append({
        'word': w,
        'class': cls
    })

# ============================================================
# NORMALIZED POSITION BY CC CLASS
# ============================================================
print("\n" + "="*70)
print("NORMALIZED POSITION BY CC CLASS")
print("="*70)

cc_positions = {cls: [] for cls in CC_CLASSES}

for key, tokens in lines_data.items():
    n = len(tokens)
    if n < 2:
        continue

    for i, tok in enumerate(tokens):
        if tok['class'] in CC_CLASSES:
            norm_pos = i / (n - 1)  # 0 = start, 1 = end
            cc_positions[tok['class']].append(norm_pos)

for cls in CC_CLASSES:
    positions = cc_positions[cls]
    if not positions:
        print(f"\nClass {cls}: No occurrences")
        continue

    mean_pos = np.mean(positions)
    std_pos = np.std(positions)
    median_pos = np.median(positions)

    print(f"\nClass {cls} (n={len(positions)}):")
    print(f"  Mean position: {mean_pos:.3f}")
    print(f"  Median position: {median_pos:.3f}")
    print(f"  Std dev: {std_pos:.3f}")

    # Position bins
    early = sum(1 for p in positions if p < 0.33)
    mid = sum(1 for p in positions if 0.33 <= p < 0.67)
    late = sum(1 for p in positions if p >= 0.67)
    n = len(positions)
    print(f"  Early (<0.33): {early} ({100*early/n:.1f}%)")
    print(f"  Mid (0.33-0.67): {mid} ({100*mid/n:.1f}%)")
    print(f"  Late (>=0.67): {late} ({100*late/n:.1f}%)")

# ============================================================
# GROUP A vs GROUP B POSITIONAL COMPARISON
# ============================================================
print("\n" + "="*70)
print("GROUP A vs GROUP B POSITIONAL COMPARISON")
print("="*70)

group_a_pos = []
group_b_pos = []

for cls in CC_GROUP_A:
    group_a_pos.extend(cc_positions[cls])

for cls in CC_GROUP_B:
    group_b_pos.extend(cc_positions[cls])

if group_a_pos:
    print(f"\nGroup A (10,11) - n={len(group_a_pos)}:")
    print(f"  Mean: {np.mean(group_a_pos):.3f}")
    print(f"  Median: {np.median(group_a_pos):.3f}")
    print(f"  Std: {np.std(group_a_pos):.3f}")

if group_b_pos:
    print(f"\nGroup B (12,17) - n={len(group_b_pos)}:")
    print(f"  Mean: {np.mean(group_b_pos):.3f}")
    print(f"  Median: {np.median(group_b_pos):.3f}")
    print(f"  Std: {np.std(group_b_pos):.3f}")

# Statistical comparison
if group_a_pos and group_b_pos:
    from scipy import stats
    stat, pval = stats.mannwhitneyu(group_a_pos, group_b_pos, alternative='two-sided')
    print(f"\nMann-Whitney U test: p = {pval:.4f}")
    if pval < 0.05:
        if np.mean(group_a_pos) < np.mean(group_b_pos):
            print("  -> Group A appears EARLIER in lines than Group B")
        else:
            print("  -> Group A appears LATER in lines than Group B")
    else:
        print("  -> No significant positional difference")

# ============================================================
# CC DENSITY BY LINE LENGTH
# ============================================================
print("\n" + "="*70)
print("CC DENSITY BY LINE LENGTH")
print("="*70)

line_lengths = defaultdict(list)
for key, tokens in lines_data.items():
    n = len(tokens)
    cc_count = sum(1 for t in tokens if t['class'] in CC_CLASSES)
    line_lengths[n].append(cc_count)

print("\nCC tokens per line by line length:")
for length in sorted(line_lengths.keys())[:15]:
    counts = line_lengths[length]
    mean_cc = np.mean(counts)
    print(f"  Length {length}: {mean_cc:.2f} CC tokens/line (n={len(counts)} lines)")

# ============================================================
# CC CO-OCCURRENCE WITHIN LINES
# ============================================================
print("\n" + "="*70)
print("CC CO-OCCURRENCE WITHIN LINES")
print("="*70)

cc_cooccur = Counter()
lines_with_cc = 0
lines_with_multiple_cc = 0

for key, tokens in lines_data.items():
    cc_in_line = [t['class'] for t in tokens if t['class'] in CC_CLASSES]
    if cc_in_line:
        lines_with_cc += 1
        if len(cc_in_line) > 1:
            lines_with_multiple_cc += 1
            # Count co-occurring pairs
            for i in range(len(cc_in_line)):
                for j in range(i+1, len(cc_in_line)):
                    pair = tuple(sorted([cc_in_line[i], cc_in_line[j]]))
                    cc_cooccur[pair] += 1

print(f"\nLines with any CC: {lines_with_cc}")
print(f"Lines with multiple CC: {lines_with_multiple_cc} ({100*lines_with_multiple_cc/lines_with_cc:.1f}%)")

print("\nCC class co-occurrence pairs:")
for pair, count in cc_cooccur.most_common(10):
    print(f"  {pair}: {count}")

# ============================================================
# FOLIO DISTRIBUTION
# ============================================================
print("\n" + "="*70)
print("CC CLASS DISTRIBUTION BY FOLIO (TOP 10)")
print("="*70)

cc_by_folio = {cls: Counter() for cls in CC_CLASSES}

for key, tokens in lines_data.items():
    folio = key[0]
    for tok in tokens:
        if tok['class'] in CC_CLASSES:
            cc_by_folio[tok['class']][folio] += 1

for cls in CC_CLASSES:
    if not cc_by_folio[cls]:
        continue
    total = sum(cc_by_folio[cls].values())
    n_folios = len(cc_by_folio[cls])
    print(f"\nClass {cls}: {total} occurrences across {n_folios} folios")
    print(f"  Top 5 folios: {cc_by_folio[cls].most_common(5)}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

# Positional differentiation
if group_a_pos and group_b_pos:
    mean_diff = abs(np.mean(group_a_pos) - np.mean(group_b_pos))
    if pval < 0.05:
        if np.mean(group_a_pos) < np.mean(group_b_pos):
            findings.append(f"POSITIONAL_DIFFERENTIATION: Group A earlier (mean {np.mean(group_a_pos):.3f}) vs Group B (mean {np.mean(group_b_pos):.3f}), p={pval:.4f}")
        else:
            findings.append(f"POSITIONAL_DIFFERENTIATION: Group A later (mean {np.mean(group_a_pos):.3f}) vs Group B (mean {np.mean(group_b_pos):.3f}), p={pval:.4f}")
    else:
        findings.append(f"NO_POSITIONAL_DIFFERENTIATION: Groups A and B have similar positions (p={pval:.4f})")

# Multi-CC lines
if lines_with_cc > 0:
    multi_rate = 100 * lines_with_multiple_cc / lines_with_cc
    findings.append(f"MULTI_CC_RATE: {multi_rate:.1f}% of CC-containing lines have multiple CC")

# Class-specific position
for cls in CC_CLASSES:
    if cc_positions[cls]:
        mean = np.mean(cc_positions[cls])
        if mean < 0.4:
            findings.append(f"CLASS_{cls}_EARLY_BIAS: Mean position {mean:.3f}")
        elif mean > 0.6:
            findings.append(f"CLASS_{cls}_LATE_BIAS: Mean position {mean:.3f}")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

# Save results
results = {
    'cc_positions': {cls: {
        'n': len(cc_positions[cls]),
        'mean': float(np.mean(cc_positions[cls])) if cc_positions[cls] else None,
        'median': float(np.median(cc_positions[cls])) if cc_positions[cls] else None,
        'std': float(np.std(cc_positions[cls])) if cc_positions[cls] else None
    } for cls in CC_CLASSES},
    'group_a_position': {
        'mean': float(np.mean(group_a_pos)) if group_a_pos else None,
        'n': len(group_a_pos)
    },
    'group_b_position': {
        'mean': float(np.mean(group_b_pos)) if group_b_pos else None,
        'n': len(group_b_pos)
    },
    'position_test_pvalue': float(pval) if group_a_pos and group_b_pos else None,
    'lines_with_cc': lines_with_cc,
    'lines_with_multiple_cc': lines_with_multiple_cc,
    'cc_cooccur': {str(k): v for k, v in cc_cooccur.most_common(20)},
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'CC_MECHANICS_DEEP_DIVE' / 'results' / 't4_cc_positional_profile.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
