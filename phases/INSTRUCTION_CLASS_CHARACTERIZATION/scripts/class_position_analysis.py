"""
CLASS POSITION ANALYSIS

Research Question Q2: Class Positional Behavior
- Do classes have line-position preferences?
- Are certain classes line-initial or line-final specialists?
- Do classes show position shifts across sections?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript
from collections import defaultdict, Counter
import numpy as np
import json

tx = Transcript()

print("=" * 70)
print("CLASS POSITION ANALYSIS")
print("=" * 70)

# Load class mapping
with open('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
class_to_role = class_map['class_to_role']
class_to_tokens = class_map['class_to_tokens']

# =============================================================================
# STEP 1: Collect position data by line
# =============================================================================
print("\n[Step 1] Collecting position data...")

# Group tokens by folio/line - tokens arrive in order
line_tokens = defaultdict(list)
for token in tx.currier_b():
    if token.word and token.word in token_to_class:
        key = (token.folio, token.line)
        # Position is simply the order in which tokens appear
        position = len(line_tokens[key])
        line_tokens[key].append({
            'word': token.word,
            'class': token_to_class[token.word],
            'position': position
        })

# Calculate relative positions
class_positions = defaultdict(list)  # class -> list of (relative_pos, absolute_pos)
class_initial = Counter()  # class -> count at position 0
class_final = Counter()    # class -> count at final position
class_total = Counter()    # class -> total count

for (folio, line), tokens in line_tokens.items():
    if len(tokens) < 2:
        continue

    # Sort by position
    tokens = sorted(tokens, key=lambda x: x['position'])
    line_length = len(tokens)

    for i, t in enumerate(tokens):
        cls = t['class']
        relative_pos = i / (line_length - 1) if line_length > 1 else 0.5

        class_positions[cls].append((relative_pos, i, line_length))
        class_total[cls] += 1

        if i == 0:
            class_initial[cls] += 1
        if i == line_length - 1:
            class_final[cls] += 1

print(f"  Analyzed {len(line_tokens)} lines")

# =============================================================================
# STEP 2: Position preference summary
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: Position Preference Summary")
print("=" * 70)

class_stats = {}
for cls in range(1, 50):
    if cls not in class_total or class_total[cls] < 20:
        continue

    positions = [p[0] for p in class_positions[cls]]
    mean_pos = np.mean(positions)
    std_pos = np.std(positions)

    initial_rate = class_initial[cls] / class_total[cls]
    final_rate = class_final[cls] / class_total[cls]

    class_stats[cls] = {
        'mean_position': mean_pos,
        'std_position': std_pos,
        'initial_rate': initial_rate,
        'final_rate': final_rate,
        'count': class_total[cls]
    }

# Sort by mean position
sorted_by_position = sorted(class_stats.items(), key=lambda x: x[1]['mean_position'])

print("\n  Classes sorted by mean position (0=initial, 1=final):")
print("\n  LINE-INITIAL SPECIALISTS (mean < 0.35):")
for cls, stats in sorted_by_position:
    if stats['mean_position'] < 0.35:
        role = class_to_role.get(str(cls), 'UNKNOWN')
        tokens = class_to_tokens.get(str(cls), [])[:3]
        print(f"    Class {cls:2d} ({role[:4]}): mean={stats['mean_position']:.2f}, "
              f"initial={stats['initial_rate']:.1%}, n={stats['count']} - {tokens}")

print("\n  LINE-FINAL SPECIALISTS (mean > 0.65):")
for cls, stats in sorted_by_position:
    if stats['mean_position'] > 0.65:
        role = class_to_role.get(str(cls), 'UNKNOWN')
        tokens = class_to_tokens.get(str(cls), [])[:3]
        print(f"    Class {cls:2d} ({role[:4]}): mean={stats['mean_position']:.2f}, "
              f"final={stats['final_rate']:.1%}, n={stats['count']} - {tokens}")

print("\n  POSITION-NEUTRAL (0.35-0.65):")
neutral = [(cls, stats) for cls, stats in sorted_by_position
           if 0.35 <= stats['mean_position'] <= 0.65]
print(f"    {len(neutral)} classes are position-neutral")

# =============================================================================
# STEP 3: Extreme position specialists
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: Extreme Position Specialists")
print("=" * 70)

# High initial rate
sorted_by_initial = sorted(class_stats.items(), key=lambda x: x[1]['initial_rate'], reverse=True)
print("\n  Highest LINE-INITIAL rates:")
for cls, stats in sorted_by_initial[:10]:
    role = class_to_role.get(str(cls), 'UNKNOWN')
    tokens = class_to_tokens.get(str(cls), [])[:3]
    print(f"    Class {cls:2d} ({role[:4]}): {stats['initial_rate']:.1%} initial "
          f"(n={stats['count']}) - {tokens}")

# High final rate
sorted_by_final = sorted(class_stats.items(), key=lambda x: x[1]['final_rate'], reverse=True)
print("\n  Highest LINE-FINAL rates:")
for cls, stats in sorted_by_final[:10]:
    role = class_to_role.get(str(cls), 'UNKNOWN')
    tokens = class_to_tokens.get(str(cls), [])[:3]
    print(f"    Class {cls:2d} ({role[:4]}): {stats['final_rate']:.1%} final "
          f"(n={stats['count']}) - {tokens}")

# =============================================================================
# STEP 4: Position by Role
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: Position by Role")
print("=" * 70)

role_positions = defaultdict(list)
for cls, stats in class_stats.items():
    role = class_to_role.get(str(cls), 'UNKNOWN')
    role_positions[role].append((cls, stats))

for role in sorted(role_positions.keys()):
    classes = role_positions[role]
    mean_positions = [s['mean_position'] for _, s in classes]
    avg_mean = np.mean(mean_positions)

    initial_rates = [s['initial_rate'] for _, s in classes]
    final_rates = [s['final_rate'] for _, s in classes]

    print(f"\n  {role}:")
    print(f"    Average mean position: {avg_mean:.2f}")
    print(f"    Initial rate range: {min(initial_rates):.1%} - {max(initial_rates):.1%}")
    print(f"    Final rate range: {min(final_rates):.1%} - {max(final_rates):.1%}")

    # Show classes sorted by position within role
    sorted_role = sorted(classes, key=lambda x: x[1]['mean_position'])
    if len(sorted_role) <= 5:
        for cls, stats in sorted_role:
            tokens = class_to_tokens.get(str(cls), [])[:2]
            print(f"      Class {cls:2d}: mean={stats['mean_position']:.2f} - {tokens}")
    else:
        print(f"      Most initial: Class {sorted_role[0][0]} ({sorted_role[0][1]['mean_position']:.2f})")
        print(f"      Most final: Class {sorted_role[-1][0]} ({sorted_role[-1][1]['mean_position']:.2f})")

# =============================================================================
# STEP 5: Low-variance classes (rigid positioning)
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: Position Variance Analysis")
print("=" * 70)

sorted_by_variance = sorted(class_stats.items(), key=lambda x: x[1]['std_position'])

print("\n  RIGID positioning (low variance, appears in consistent positions):")
for cls, stats in sorted_by_variance[:10]:
    role = class_to_role.get(str(cls), 'UNKNOWN')
    tokens = class_to_tokens.get(str(cls), [])[:3]
    print(f"    Class {cls:2d} ({role[:4]}): std={stats['std_position']:.2f}, "
          f"mean={stats['mean_position']:.2f}, n={stats['count']} - {tokens}")

print("\n  FLEXIBLE positioning (high variance, appears anywhere):")
for cls, stats in sorted_by_variance[-10:]:
    role = class_to_role.get(str(cls), 'UNKNOWN')
    tokens = class_to_tokens.get(str(cls), [])[:3]
    print(f"    Class {cls:2d} ({role[:4]}): std={stats['std_position']:.2f}, "
          f"mean={stats['mean_position']:.2f}, n={stats['count']} - {tokens}")

# =============================================================================
# STEP 6: Section-specific position shifts
# =============================================================================
print("\n" + "=" * 70)
print("STEP 6: Section-Specific Position Shifts")
print("=" * 70)

# Get section for each folio
folio_section = {}
for token in tx.currier_b():
    if token.folio and token.folio not in folio_section:
        folio_section[token.folio] = getattr(token, 'section', 'unknown')

# Collect positions by section
section_class_positions = defaultdict(lambda: defaultdict(list))
for (folio, line), tokens in line_tokens.items():
    if len(tokens) < 2:
        continue

    section = folio_section.get(folio, 'unknown')
    tokens = sorted(tokens, key=lambda x: x['position'])
    line_length = len(tokens)

    for i, t in enumerate(tokens):
        cls = t['class']
        relative_pos = i / (line_length - 1) if line_length > 1 else 0.5
        section_class_positions[section][cls].append(relative_pos)

# Find classes with significant section shifts
print("\n  Classes with section-dependent positioning:")
significant_shifts = []

for cls in range(1, 50):
    section_means = {}
    for section in ['B', 'H', 'S', 'C']:
        if len(section_class_positions[section][cls]) >= 20:
            section_means[section] = np.mean(section_class_positions[section][cls])

    if len(section_means) >= 2:
        max_shift = max(section_means.values()) - min(section_means.values())
        if max_shift > 0.15:  # Significant shift threshold
            significant_shifts.append((cls, section_means, max_shift))

significant_shifts.sort(key=lambda x: x[2], reverse=True)

for cls, means, shift in significant_shifts[:10]:
    role = class_to_role.get(str(cls), 'UNKNOWN')
    tokens = class_to_tokens.get(str(cls), [])[:2]
    sections_str = ", ".join(f"{s}:{m:.2f}" for s, m in sorted(means.items()))
    print(f"    Class {cls:2d} ({role[:4]}): shift={shift:.2f} [{sections_str}] - {tokens}")

# =============================================================================
# SAVE RESULTS
# =============================================================================
import os
os.makedirs('results', exist_ok=True)

results = {
    'class_position_stats': {str(k): v for k, v in class_stats.items()},
    'significant_section_shifts': [
        {'class': cls, 'means': means, 'shift': shift}
        for cls, means, shift in significant_shifts
    ],
}

with open('results/class_positions.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("Saved results to results/class_positions.json")
print("=" * 70)
