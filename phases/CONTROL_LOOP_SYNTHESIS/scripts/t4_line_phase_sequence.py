"""
T4: Line Phase Sequence Analysis

What's the phase order within lines?
- Do KERNEL, LINK, FL have canonical positions?
- Is there a typical execution sequence?
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

def has_kernel(word):
    word = word.replace('*', '').lower()
    return 'k' in word or 'h' in word or 'e' in word

def get_phase(word):
    """Assign token to one of three phases"""
    word_clean = word.replace('*', '')
    if is_fl(word_clean):
        return 'FL'
    elif is_link(word_clean):
        return 'LINK'
    elif has_kernel(word_clean):
        return 'KERNEL'
    else:
        return 'OTHER'

# Load transcript
tx = Transcript()
b_tokens = list(tx.currier_b())

lines = defaultdict(list)
for t in b_tokens:
    lines[(t.folio, t.line)].append(t)

print(f"Total B tokens: {len(b_tokens)}")
print(f"Total lines: {len(lines)}")

# Collect positions by phase
kernel_positions = []
link_positions = []
fl_positions = []
other_positions = []

# Count phase tokens
phase_counts = Counter()

for key, tokens in lines.items():
    n = len(tokens)
    if n < 3:  # Need at least 3 tokens for meaningful position
        continue

    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if not word.strip():
            continue

        pos_norm = i / (n - 1)  # Normalize to 0-1
        phase = get_phase(word)
        phase_counts[phase] += 1

        if phase == 'KERNEL':
            kernel_positions.append(pos_norm)
        elif phase == 'LINK':
            link_positions.append(pos_norm)
        elif phase == 'FL':
            fl_positions.append(pos_norm)
        else:
            other_positions.append(pos_norm)

print(f"\n{'='*60}")
print(f"LINE PHASE SEQUENCE ANALYSIS")
print(f"{'='*60}")

print(f"\n--- PHASE COUNTS ---")
for phase, count in sorted(phase_counts.items(), key=lambda x: -x[1]):
    print(f"  {phase}: {count} ({100*count/sum(phase_counts.values()):.1f}%)")

print(f"\n--- MEAN POSITIONS (0=start, 1=end) ---")
print(f"  KERNEL: {np.mean(kernel_positions):.3f} (n={len(kernel_positions)})")
print(f"  LINK:   {np.mean(link_positions):.3f} (n={len(link_positions)})")
print(f"  FL:     {np.mean(fl_positions):.3f} (n={len(fl_positions)})")
print(f"  OTHER:  {np.mean(other_positions):.3f} (n={len(other_positions)})")

# Statistical comparison
print(f"\n--- POSITION COMPARISONS ---")
# KERNEL vs LINK
if kernel_positions and link_positions:
    u, p = stats.mannwhitneyu(kernel_positions, link_positions)
    print(f"KERNEL vs LINK: p={p:.4f} ({'KERNEL earlier' if np.mean(kernel_positions) < np.mean(link_positions) else 'LINK earlier'})")

# KERNEL vs FL
if kernel_positions and fl_positions:
    u, p = stats.mannwhitneyu(kernel_positions, fl_positions)
    print(f"KERNEL vs FL: p={p:.4f} ({'KERNEL earlier' if np.mean(kernel_positions) < np.mean(fl_positions) else 'FL earlier'})")

# LINK vs FL
if link_positions and fl_positions:
    u, p = stats.mannwhitneyu(link_positions, fl_positions)
    print(f"LINK vs FL: p={p:.4f} ({'LINK earlier' if np.mean(link_positions) < np.mean(fl_positions) else 'FL earlier'})")

# Quintile distribution
print(f"\n--- QUINTILE DISTRIBUTION ---")
bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
bin_labels = ['0.0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0']

kernel_hist, _ = np.histogram(kernel_positions, bins=bins)
link_hist, _ = np.histogram(link_positions, bins=bins)
fl_hist, _ = np.histogram(fl_positions, bins=bins)

print(f"{'Quintile':<12} {'KERNEL%':>10} {'LINK%':>10} {'FL%':>10}")
print(f"{'-'*12} {'-'*10} {'-'*10} {'-'*10}")
for i, label in enumerate(bin_labels):
    k_pct = 100 * kernel_hist[i] / len(kernel_positions) if kernel_positions else 0
    l_pct = 100 * link_hist[i] / len(link_positions) if link_positions else 0
    f_pct = 100 * fl_hist[i] / len(fl_positions) if fl_positions else 0
    print(f"{label:<12} {k_pct:>9.1f}% {l_pct:>9.1f}% {f_pct:>9.1f}%")

# Line-level phase ordering
print(f"\n--- LINE-LEVEL PHASE ORDERING ---")
# For each line, determine average position of each phase
line_orderings = Counter()

for key, tokens in lines.items():
    n = len(tokens)
    if n < 5:
        continue

    phase_positions = defaultdict(list)
    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if not word.strip():
            continue
        phase = get_phase(word)
        if phase != 'OTHER':
            phase_positions[phase].append(i / (n - 1))

    # Skip if missing phases
    if len(phase_positions) < 2:
        continue

    # Determine ordering by mean position
    phase_means = {p: np.mean(pos) for p, pos in phase_positions.items()}
    ordering = tuple(sorted(phase_means.keys(), key=lambda x: phase_means[x]))
    line_orderings[ordering] += 1

print(f"Most common phase orderings (by mean position in line):")
for ordering, count in line_orderings.most_common(10):
    print(f"  {' -> '.join(ordering)}: {count} lines ({100*count/sum(line_orderings.values()):.1f}%)")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")

# Determine canonical ordering
mean_positions = [
    ('KERNEL', np.mean(kernel_positions)),
    ('LINK', np.mean(link_positions)),
    ('FL', np.mean(fl_positions))
]
mean_positions.sort(key=lambda x: x[1])

print(f"Canonical phase ordering by mean position:")
print(f"  {' -> '.join([p[0] for p in mean_positions])}")
print(f"  ({' -> '.join([f'{p[1]:.3f}' for p in mean_positions])})")

if mean_positions[0][0] == 'LINK' and mean_positions[-1][0] == 'FL':
    print(f"\nLINK->...->FL ordering suggests: LINK early (monitoring setup), FL late (escape if needed)")
elif mean_positions[0][0] == 'KERNEL':
    print(f"\nKERNEL-first ordering suggests: Processing before monitoring/escape")
