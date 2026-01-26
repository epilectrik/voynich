"""
CLASS MORPHOLOGY ANALYSIS

Research Question Q4: Class Morphological Structure
- What PREFIX/SUFFIX patterns distinguish classes within a role?
- Do classes differ by morphological complexity?
- Are there class-specific MIDDLE patterns?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("CLASS MORPHOLOGY ANALYSIS")
print("=" * 70)

# Load class mapping
with open('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
class_to_role = class_map['class_to_role']
class_to_tokens = class_map['class_to_tokens']

# =============================================================================
# STEP 1: Extract morphology for each class
# =============================================================================
print("\n[Step 1] Extracting morphology for each class...")

class_morphology = defaultdict(lambda: {
    'articulators': Counter(),
    'prefixes': Counter(),
    'middles': Counter(),
    'suffixes': Counter(),
    'has_articulator': 0,
    'has_prefix': 0,
    'has_suffix': 0,
    'total': 0,
    'complexity_sum': 0,  # Sum of component counts
})

for token in tx.currier_b():
    if token.word and token.word in token_to_class:
        cls = token_to_class[token.word]
        m = morph.extract(token.word)

        class_morphology[cls]['total'] += 1

        if m.articulator:
            class_morphology[cls]['articulators'][m.articulator] += 1
            class_morphology[cls]['has_articulator'] += 1

        if m.prefix:
            class_morphology[cls]['prefixes'][m.prefix] += 1
            class_morphology[cls]['has_prefix'] += 1

        if m.middle:
            class_morphology[cls]['middles'][m.middle] += 1

        if m.suffix:
            class_morphology[cls]['suffixes'][m.suffix] += 1
            class_morphology[cls]['has_suffix'] += 1

        # Count complexity
        complexity = sum([
            1 if m.articulator else 0,
            1 if m.prefix else 0,
            1 if m.middle else 0,
            1 if m.suffix else 0
        ])
        class_morphology[cls]['complexity_sum'] += complexity

print(f"  Analyzed {sum(d['total'] for d in class_morphology.values())} tokens")

# =============================================================================
# STEP 2: Class morphological profiles
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: Class Morphological Profiles")
print("=" * 70)

class_profiles = {}

for cls in range(1, 50):
    if class_morphology[cls]['total'] < 10:
        continue

    total = class_morphology[cls]['total']

    articulator_rate = class_morphology[cls]['has_articulator'] / total
    prefix_rate = class_morphology[cls]['has_prefix'] / total
    suffix_rate = class_morphology[cls]['has_suffix'] / total
    avg_complexity = class_morphology[cls]['complexity_sum'] / total

    top_prefix = class_morphology[cls]['prefixes'].most_common(1)
    top_suffix = class_morphology[cls]['suffixes'].most_common(1)
    top_articulator = class_morphology[cls]['articulators'].most_common(1)
    top_middle = class_morphology[cls]['middles'].most_common(1)

    class_profiles[cls] = {
        'articulator_rate': articulator_rate,
        'prefix_rate': prefix_rate,
        'suffix_rate': suffix_rate,
        'avg_complexity': avg_complexity,
        'top_prefix': top_prefix[0][0] if top_prefix else None,
        'top_suffix': top_suffix[0][0] if top_suffix else None,
        'top_articulator': top_articulator[0][0] if top_articulator else None,
        'top_middle': top_middle[0][0] if top_middle else None,
        'total': total
    }

# =============================================================================
# STEP 3: Within-role differentiation
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: Within-Role Differentiation")
print("=" * 70)

role_classes = defaultdict(list)
for cls, profile in class_profiles.items():
    role = class_to_role.get(str(cls), 'UNKNOWN')
    role_classes[role].append((cls, profile))

for role in sorted(role_classes.keys()):
    classes = role_classes[role]
    if len(classes) < 2:
        continue

    print(f"\n  {role} ({len(classes)} classes):")

    # Sort by prefix rate
    classes.sort(key=lambda x: x[1]['prefix_rate'], reverse=True)

    for cls, prof in classes:
        tokens = class_to_tokens.get(str(cls), [])[:3]
        print(f"    Class {cls:2d}: ART={prof['articulator_rate']:.0%} "
              f"PRE={prof['prefix_rate']:.0%} SUF={prof['suffix_rate']:.0%} "
              f"cmplx={prof['avg_complexity']:.1f} - {tokens}")

        # Show dominant morphemes
        details = []
        if prof['top_articulator']:
            details.append(f"art:{prof['top_articulator']}")
        if prof['top_prefix']:
            details.append(f"pre:{prof['top_prefix']}")
        if prof['top_suffix']:
            details.append(f"suf:{prof['top_suffix']}")
        if details:
            print(f"             {', '.join(details)}")

# =============================================================================
# STEP 4: Prefix patterns by class
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: Prefix Patterns")
print("=" * 70)

# Group classes by dominant prefix
prefix_to_classes = defaultdict(list)
for cls, prof in class_profiles.items():
    if prof['prefix_rate'] > 0.5 and prof['top_prefix']:
        prefix_to_classes[prof['top_prefix']].append((cls, prof))

print("\n  Classes grouped by dominant prefix (>50% usage):")
for prefix in sorted(prefix_to_classes.keys()):
    classes = prefix_to_classes[prefix]
    print(f"\n  PREFIX '{prefix}':")
    for cls, prof in classes:
        role = class_to_role.get(str(cls), 'UNK')
        tokens = class_to_tokens.get(str(cls), [])[:3]
        print(f"    Class {cls:2d} ({role[:4]}): {prof['prefix_rate']:.0%} - {tokens}")

# =============================================================================
# STEP 5: Suffix patterns by class
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: Suffix Patterns")
print("=" * 70)

# Group classes by dominant suffix
suffix_to_classes = defaultdict(list)
for cls, prof in class_profiles.items():
    if prof['suffix_rate'] > 0.5 and prof['top_suffix']:
        suffix_to_classes[prof['top_suffix']].append((cls, prof))

print("\n  Classes grouped by dominant suffix (>50% usage):")
for suffix in sorted(suffix_to_classes.keys()):
    classes = suffix_to_classes[suffix]
    print(f"\n  SUFFIX '{suffix}':")
    for cls, prof in classes:
        role = class_to_role.get(str(cls), 'UNK')
        tokens = class_to_tokens.get(str(cls), [])[:3]
        print(f"    Class {cls:2d} ({role[:4]}): {prof['suffix_rate']:.0%} - {tokens}")

# =============================================================================
# STEP 6: Complexity analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 6: Complexity Analysis")
print("=" * 70)

sorted_by_complexity = sorted(class_profiles.items(), key=lambda x: x[1]['avg_complexity'], reverse=True)

print("\n  Highest complexity classes (most morphemes):")
for cls, prof in sorted_by_complexity[:10]:
    role = class_to_role.get(str(cls), 'UNK')
    tokens = class_to_tokens.get(str(cls), [])[:3]
    print(f"    Class {cls:2d} ({role[:4]}): complexity={prof['avg_complexity']:.2f} - {tokens}")

print("\n  Lowest complexity classes (fewest morphemes):")
for cls, prof in sorted_by_complexity[-10:]:
    role = class_to_role.get(str(cls), 'UNK')
    tokens = class_to_tokens.get(str(cls), [])[:3]
    print(f"    Class {cls:2d} ({role[:4]}): complexity={prof['avg_complexity']:.2f} - {tokens}")

# =============================================================================
# STEP 7: Articulator analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 7: Articulator Analysis")
print("=" * 70)

# Classes with high articulator usage
articulated_classes = [(cls, prof) for cls, prof in class_profiles.items() if prof['articulator_rate'] > 0.3]
articulated_classes.sort(key=lambda x: x[1]['articulator_rate'], reverse=True)

print("\n  Classes with >30% articulator usage:")
for cls, prof in articulated_classes:
    role = class_to_role.get(str(cls), 'UNK')
    tokens = class_to_tokens.get(str(cls), [])[:3]
    print(f"    Class {cls:2d} ({role[:4]}): {prof['articulator_rate']:.0%} "
          f"(dominant: '{prof['top_articulator']}') - {tokens}")

# =============================================================================
# STEP 8: MIDDLE-based class groupings
# =============================================================================
print("\n" + "=" * 70)
print("STEP 8: MIDDLE-Based Groupings")
print("=" * 70)

# Find classes sharing the same dominant MIDDLE
middle_to_classes = defaultdict(list)
for cls, prof in class_profiles.items():
    if prof['top_middle']:
        middle_to_classes[prof['top_middle']].append((cls, prof))

# Focus on MIDDLEs shared by multiple classes
print("\n  MIDDLEs shared by multiple classes:")
shared_middles = [(mid, cls_list) for mid, cls_list in middle_to_classes.items() if len(cls_list) >= 2]
shared_middles.sort(key=lambda x: len(x[1]), reverse=True)

for middle, classes in shared_middles[:15]:
    print(f"\n  MIDDLE '{middle}' ({len(classes)} classes):")
    for cls, prof in classes:
        role = class_to_role.get(str(cls), 'UNK')
        tokens = class_to_tokens.get(str(cls), [])[:2]
        print(f"    Class {cls:2d} ({role[:4]}): PRE={prof['top_prefix'] or '-'} SUF={prof['top_suffix'] or '-'} - {tokens}")

# =============================================================================
# SAVE RESULTS
# =============================================================================
import os
os.makedirs('results', exist_ok=True)

results = {
    'class_profiles': {str(k): v for k, v in class_profiles.items()},
    'prefix_groups': {
        prefix: [(cls, class_to_role.get(str(cls), 'UNK'))
                 for cls, _ in classes]
        for prefix, classes in prefix_to_classes.items()
    },
    'suffix_groups': {
        suffix: [(cls, class_to_role.get(str(cls), 'UNK'))
                 for cls, _ in classes]
        for suffix, classes in suffix_to_classes.items()
    },
}

with open('results/class_morphology.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("Saved results to results/class_morphology.json")
print("=" * 70)
