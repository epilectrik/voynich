#!/usr/bin/env python3
"""
Specific analysis of 'sor' - the most line-initial s-prefix token.

sor has 78% line-initial rate, which is extreme even among AX openers.
Is sor behaviorally distinct from other s-prefix tokens?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

# Load class map
class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    import json
    class_data = json.load(f)
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()

# Build line data
folio_lines = defaultdict(lambda: defaultdict(list))
folio_section = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_lines[token.folio][token.line].append(token.word)
    if token.folio not in folio_section:
        folio_section[token.folio] = token.section

print("="*70)
print("SOR SPECIFIC ANALYSIS")
print("="*70)

# Find all sor occurrences
sor_lines = []
for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        if 'sor' in words:
            pos = words.index('sor')
            sor_lines.append({
                'folio': folio,
                'section': folio_section.get(folio, '?'),
                'line': line,
                'pos': pos,
                'total': len(words),
                'words': words
            })

print(f"\nTotal sor occurrences: {len(sor_lines)}")

# Positional analysis
positions = [l['pos'] for l in sor_lines]
line_initial = sum(1 for p in positions if p == 0)
print(f"Line-initial: {line_initial} ({100*line_initial/len(positions):.1f}%)")

# What follows sor?
print(f"\n{'='*70}")
print("WHAT FOLLOWS SOR?")
print("="*70)

followers = []
for l in sor_lines:
    pos = l['pos']
    words = l['words']
    if pos + 1 < len(words):
        follower = words[pos + 1]
        followers.append(follower)

follower_counts = Counter(followers)
print(f"\nMost common tokens following sor:")
for word, count in follower_counts.most_common(15):
    role = token_to_role.get(word, '?')
    print(f"  {word:<15} {count:<5} {role}")

# Follower role distribution
follower_roles = Counter(token_to_role.get(f, 'UNKNOWN') for f in followers)
print(f"\nFollower role distribution:")
for role, count in follower_roles.most_common():
    print(f"  {role:<25} {count:<5} ({100*count/len(followers):.1f}%)")

# Compare to daiin followers (from C557: 47.1% ENERGY)
# sor follower EN rate:
en_followers = sum(1 for f in followers if token_to_role.get(f) == 'ENERGY_OPERATOR')
print(f"\nENERGY followers: {en_followers}/{len(followers)} = {100*en_followers/len(followers):.1f}%")
print("(Compare to daiin: 47.1% ENERGY per C557)")

# Section distribution
print(f"\n{'='*70}")
print("SOR BY SECTION")
print("="*70)

section_counts = Counter(l['section'] for l in sor_lines)
for section, count in section_counts.most_common():
    print(f"  {section}: {count}")

# What's on the rest of the line?
print(f"\n{'='*70}")
print("LINE COMPOSITION WHEN SOR IS INITIAL")
print("="*70)

sor_initial_lines = [l for l in sor_lines if l['pos'] == 0]
print(f"\nAnalyzing {len(sor_initial_lines)} sor-initial lines")

# Average line length
avg_len = np.mean([l['total'] for l in sor_initial_lines])
print(f"Average line length: {avg_len:.1f}")

# Role composition
line_roles = Counter()
for l in sor_initial_lines:
    for word in l['words'][1:]:  # Exclude sor itself
        role = token_to_role.get(word, 'UNKNOWN')
        line_roles[role] += 1

total_words = sum(line_roles.values())
print(f"\nRole composition (excluding sor):")
for role, count in line_roles.most_common():
    print(f"  {role:<25} {count:<5} ({100*count/total_words:.1f}%)")

# Kernel content on sor-initial lines
print(f"\n{'='*70}")
print("KERNEL CONTENT ON SOR-INITIAL LINES")
print("="*70)

k_chars = 0
h_chars = 0
e_chars = 0
total_chars = 0

for l in sor_initial_lines:
    for word in l['words'][1:]:
        k_chars += word.count('k')
        h_chars += word.count('h')
        e_chars += word.count('e')
        total_chars += len(word)

print(f"\nKernel character rates on sor-initial lines:")
print(f"  k: {100*k_chars/total_chars:.2f}%")
print(f"  h: {100*h_chars/total_chars:.2f}%")
print(f"  e: {100*e_chars/total_chars:.2f}%")
print(f"  Total kernel: {100*(k_chars+h_chars+e_chars)/total_chars:.2f}%")

# Compare to baseline (all B lines)
baseline_k = 0
baseline_h = 0
baseline_e = 0
baseline_total = 0

for folio in folio_lines:
    for line in folio_lines[folio]:
        for word in folio_lines[folio][line]:
            baseline_k += word.count('k')
            baseline_h += word.count('h')
            baseline_e += word.count('e')
            baseline_total += len(word)

print(f"\nBaseline (all B lines):")
print(f"  k: {100*baseline_k/baseline_total:.2f}%")
print(f"  h: {100*baseline_h/baseline_total:.2f}%")
print(f"  e: {100*baseline_e/baseline_total:.2f}%")

# Summary
print(f"\n{'='*70}")
print("SUMMARY: IS SOR APPARATUS-LIKE?")
print("="*70)

print("""
Apparatus-like indicators:
1. Extreme line-initial rate: 78% (highest among AX)
2. Zero kernel in 'sor' itself: YES
3. Specific follower pattern: ?
4. Section concentration: ?
5. Kernel on sor-lines vs baseline: ?

If sor-initial lines have LOWER kernel content than baseline,
this supports the apparatus hypothesis (non-process lines).

If similar or higher, sor is just another operational opener.
""")
