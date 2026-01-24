#!/usr/bin/env python3
"""
Investigate: What is the scope of PP MIDDLE effects?

Does a single PP MIDDLE affect:
- ALL classes (universal)?
- A specific subset of classes (scoped)?
- Random classes (no structure)?
"""

import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path('.')

# Load class-token map
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
token_to_middle = class_map['token_to_middle']
class_to_tokens = class_map['class_to_tokens']

# Build MIDDLE → classes mapping
middle_to_classes = defaultdict(set)
middle_to_tokens = defaultdict(list)

for token, middle in token_to_middle.items():
    if middle:
        cls = token_to_class.get(token)
        if cls:
            middle_to_classes[middle].add(cls)
            middle_to_tokens[middle].append((token, cls))

print("="*70)
print("PP MIDDLE SCOPE ANALYSIS")
print("="*70)

total_classes = len(class_to_tokens)
print(f"\nTotal instruction classes: {total_classes}")
print(f"Total PP MIDDLEs: {len(middle_to_classes)}")

# Distribution of class coverage per MIDDLE
coverage_dist = Counter(len(classes) for classes in middle_to_classes.values())
print(f"\n--- Class coverage distribution ---")
print(f"{'Classes covered':>15} {'MIDDLEs':>10} {'%':>8}")
for n_classes in sorted(coverage_dist.keys()):
    count = coverage_dist[n_classes]
    pct = 100 * count / len(middle_to_classes)
    print(f"{n_classes:>15} {count:>10} {pct:>7.1f}%")

# Summary stats
coverages = [len(classes) for classes in middle_to_classes.values()]
avg_coverage = sum(coverages) / len(coverages)
max_coverage = max(coverages)
min_coverage = min(coverages)

print(f"\nCoverage statistics:")
print(f"  Min: {min_coverage} classes")
print(f"  Max: {max_coverage} classes ({100*max_coverage/total_classes:.1f}% of all)")
print(f"  Avg: {avg_coverage:.1f} classes ({100*avg_coverage/total_classes:.1f}% of all)")

# Find the high-span MIDDLEs
print(f"\n--- High-span MIDDLEs (10+ classes) ---")
high_span = [(m, classes) for m, classes in middle_to_classes.items() if len(classes) >= 10]
high_span.sort(key=lambda x: -len(x[1]))

for middle, classes in high_span:
    print(f"\n  MIDDLE '{middle}': {len(classes)} classes")
    print(f"    Classes: {sorted(classes)}")

# Find the low-span MIDDLEs (1-2 classes)
print(f"\n--- Low-span MIDDLEs (1-2 classes) ---")
low_span = [(m, classes) for m, classes in middle_to_classes.items() if len(classes) <= 2]
print(f"  Count: {len(low_span)} MIDDLEs")
for middle, classes in low_span[:15]:
    tokens = middle_to_tokens[middle]
    tok_str = ", ".join([f"{t}(c{c})" for t,c in tokens[:3]])
    print(f"    '{middle}': classes {sorted(classes)} → {tok_str}")

# Check for class clustering - do high-span MIDDLEs share similar class sets?
print(f"\n--- Class overlap between high-span MIDDLEs ---")
if len(high_span) >= 2:
    for i in range(min(5, len(high_span))):
        for j in range(i+1, min(5, len(high_span))):
            m1, c1 = high_span[i]
            m2, c2 = high_span[j]
            overlap = len(c1 & c2)
            union = len(c1 | c2)
            jacc = overlap / union if union else 0
            print(f"  '{m1}' ∩ '{m2}': {overlap}/{union} classes (Jaccard={jacc:.2f})")

# Check which classes are covered by most MIDDLEs
print(f"\n--- Class coverage by MIDDLEs ---")
class_middle_count = Counter()
for middle, classes in middle_to_classes.items():
    for cls in classes:
        class_middle_count[cls] += 1

print(f"{'Class':>6} {'#MIDDLEs':>10} {'% of all':>10}")
for cls, count in class_middle_count.most_common(15):
    pct = 100 * count / len(middle_to_classes)
    print(f"{cls:>6} {count:>10} {pct:>9.1f}%")

print(f"\n...")
for cls, count in class_middle_count.most_common()[-10:]:
    pct = 100 * count / len(middle_to_classes)
    print(f"{cls:>6} {count:>10} {pct:>9.1f}%")

# Are there classes that are NEVER covered by high-span MIDDLEs?
high_span_classes = set()
for m, classes in high_span:
    high_span_classes.update(classes)

all_classes = set(int(c) for c in class_to_tokens.keys())
uncovered = all_classes - high_span_classes

print(f"\n--- Classes NOT covered by any high-span (10+) MIDDLE ---")
print(f"  Count: {len(uncovered)} of {len(all_classes)}")
if uncovered:
    print(f"  Classes: {sorted(uncovered)}")

# Final interpretation
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

universal_threshold = total_classes * 0.8  # 80% = universal
if max_coverage >= universal_threshold:
    print(f"""
Some MIDDLEs are NEAR-UNIVERSAL ({max_coverage}/{total_classes} = {100*max_coverage/total_classes:.0f}% coverage).
These likely represent core infrastructure variants.
""")
else:
    print(f"""
No MIDDLE reaches universal coverage (max = {max_coverage}/{total_classes} = {100*max_coverage/total_classes:.0f}%).
MIDDLEs have SCOPED effects - each affects a subset of classes.
""")

if avg_coverage < total_classes * 0.3:
    print(f"""
Average coverage is LOW ({avg_coverage:.1f}/{total_classes} = {100*avg_coverage/total_classes:.0f}%).
Most PP MIDDLEs affect only a SMALL subset of the grammar.
This suggests SPECIALIZED variants, not universal modifiers.
""")
