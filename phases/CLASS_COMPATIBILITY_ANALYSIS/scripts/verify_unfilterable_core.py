"""
CLASS_COMPATIBILITY_ANALYSIS - Supplementary Test
Verify C503's "6 unfilterable core" classes under FULL morphology

Question: Do classes 7, 11, 9, 21, 22, 41 still survive in ALL A records
under full morphological filtering (PREFIX+MIDDLE+SUFFIX)?

C503 claimed these classes are "unfilterable" under MIDDLE-only filtering.
C509.c found 0 universal classes using PREFIX-based taxonomy.
This test reconciles: check original 49 classes under full morphology.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict
import json

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("VERIFY C503's 'UNFILTERABLE CORE' UNDER FULL MORPHOLOGY")
print("=" * 70)

# Step 1: Build B token data with C121 class assignments
# Load the original 49-class assignments from CLASS_COSURVIVAL_TEST
try:
    with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
        raw_data = json.load(f)
        class_data = raw_data.get('token_to_class', raw_data)
    print(f"\nLoaded C121 class assignments: {len(class_data)} tokens")
except FileNotFoundError:
    print("\nWARNING: class_token_map.json not found, will need alternative approach")
    class_data = None

# Get B tokens with morphology
b_tokens = {}
for token in tx.currier_b():
    word = token.word
    if word not in b_tokens:
        m = morph.extract(word)
        b_tokens[word] = {
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'class': None  # Will fill if we have class data
        }

# If we have class data, merge it
if class_data:
    matched = 0
    for word, info in b_tokens.items():
        if word in class_data:
            info['class'] = class_data[word]
            matched += 1
    print(f"Matched {matched} B tokens to C121 classes")

# Get class assignments for B tokens
class_to_tokens = defaultdict(list)
for word, info in b_tokens.items():
    if info['class'] is not None:
        class_to_tokens[info['class']].append(word)

print(f"\nB tokens: {len(b_tokens)}")
print(f"Classes with tokens: {len(class_to_tokens)}")

# Step 2: Build A records with morphology
a_records = defaultdict(list)
for token in tx.currier_a():
    key = (token.folio, token.line)
    a_records[key].append(token)

record_morphology = {}
for (folio, line), tokens in a_records.items():
    prefixes = set()
    middles = set()
    suffixes = set()
    for t in tokens:
        m = morph.extract(t.word)
        if m.prefix:
            prefixes.add(m.prefix)
        if m.middle:
            middles.add(m.middle)
        if m.suffix:
            suffixes.add(m.suffix)
    record_morphology[(folio, line)] = (prefixes, middles, suffixes)

print(f"A records: {len(record_morphology)}")

# B vocabulary sets for filtering
b_middles = set(info['middle'] for info in b_tokens.values() if info['middle'])
b_prefixes = set(info['prefix'] for info in b_tokens.values() if info['prefix'])
b_suffixes = set(info['suffix'] for info in b_tokens.values() if info['suffix'])

print(f"\nB vocabulary:")
print(f"  MIDDLEs: {len(b_middles)}")
print(f"  PREFIXes: {len(b_prefixes)}")
print(f"  SUFFIXes: {len(b_suffixes)}")

# Step 3: For each A record, determine which C121 classes survive under FULL morphology
print("\n" + "=" * 70)
print("CLASS SURVIVAL UNDER FULL MORPHOLOGY")
print("=" * 70)

unfilterable_classes = [7, 11, 9, 21, 22, 41]

record_surviving_classes = {}
for (folio, line), (prefixes, middles, suffixes) in record_morphology.items():
    # PP components (intersection with B vocabulary)
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    # Which classes survive?
    surviving = set()
    for word, info in b_tokens.items():
        if info['class'] is None:
            continue

        # MIDDLE filter
        if info['middle'] is None:
            middle_ok = True  # ATOMIC tokens (no MIDDLE) always pass
        else:
            middle_ok = info['middle'] in pp_middles

        # PREFIX filter
        if info['prefix'] is None:
            prefix_ok = True  # No PREFIX required
        else:
            prefix_ok = info['prefix'] in pp_prefixes

        # SUFFIX filter
        if info['suffix'] is None:
            suffix_ok = True  # No SUFFIX required
        else:
            suffix_ok = info['suffix'] in pp_suffixes

        if middle_ok and prefix_ok and suffix_ok:
            surviving.add(info['class'])

    record_surviving_classes[(folio, line)] = surviving

# Step 4: Check the 6 "unfilterable" classes
print("\n--- Checking C503's 6 'unfilterable' classes ---")
print("\nFor each class, how many A records include it?")

class_occurrence = defaultdict(int)
for classes in record_surviving_classes.values():
    for c in classes:
        class_occurrence[c] += 1

n_records = len(record_surviving_classes)

print(f"\nTotal A records: {n_records}")
print("\n'Unfilterable core' (C503) classes:")
for cls in unfilterable_classes:
    count = class_occurrence[cls]
    pct = 100 * count / n_records
    universal = "YES" if count == n_records else "NO"
    print(f"  Class {cls}: {count}/{n_records} records ({pct:.1f}%) - Universal: {universal}")

# Step 5: Which classes ARE truly universal?
print("\n" + "=" * 70)
print("TRULY UNIVERSAL CLASSES (appear in ALL records)")
print("=" * 70)

universal_classes = [c for c, count in class_occurrence.items() if count == n_records]
print(f"\nClasses in ALL {n_records} records: {len(universal_classes)}")
if universal_classes:
    for c in sorted(universal_classes):
        print(f"  Class {c}")
else:
    print("  NONE")

# Step 6: What's the coverage of the "unfilterable" classes?
print("\n" + "=" * 70)
print("HIGH-COVERAGE CLASSES (>90%)")
print("=" * 70)

high_coverage = [(c, count) for c, count in class_occurrence.items()
                 if count >= 0.9 * n_records]
high_coverage.sort(key=lambda x: -x[1])

for c, count in high_coverage[:15]:
    pct = 100 * count / n_records
    in_core = "(*)" if c in unfilterable_classes else ""
    print(f"  Class {c}: {pct:.1f}% {in_core}")

# Step 7: Examine the morphology of "unfilterable" classes
print("\n" + "=" * 70)
print("MORPHOLOGY OF 'UNFILTERABLE' CLASSES")
print("=" * 70)

for cls in unfilterable_classes:
    tokens = class_to_tokens.get(cls, [])
    if not tokens:
        print(f"\nClass {cls}: No tokens found in mapping")
        continue

    print(f"\nClass {cls}: {len(tokens)} tokens")

    # Collect morphology
    has_prefix = sum(1 for w in tokens if b_tokens[w]['prefix'])
    has_middle = sum(1 for w in tokens if b_tokens[w]['middle'])
    has_suffix = sum(1 for w in tokens if b_tokens[w]['suffix'])

    print(f"  With PREFIX: {has_prefix} ({100*has_prefix/len(tokens):.0f}%)")
    print(f"  With MIDDLE: {has_middle} ({100*has_middle/len(tokens):.0f}%)")
    print(f"  With SUFFIX: {has_suffix} ({100*has_suffix/len(tokens):.0f}%)")

    # Sample tokens
    print(f"  Sample tokens:")
    for w in tokens[:5]:
        info = b_tokens[w]
        print(f"    {w}: P={info['prefix']}, M={info['middle']}, S={info['suffix']}")

# Step 8: Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

if class_data:
    missing = n_records - min(class_occurrence[c] for c in unfilterable_classes if c in class_occurrence)

    print(f"""
C503 CLAIM: Classes 7, 11, 9, 21, 22, 41 are "unfilterable"

VERDICT UNDER FULL MORPHOLOGY:
""")
    for cls in unfilterable_classes:
        count = class_occurrence[cls]
        pct = 100 * count / n_records
        if count == n_records:
            status = "CONFIRMED universal"
        elif count >= 0.95 * n_records:
            status = "NEARLY universal (>95%)"
        elif count >= 0.90 * n_records:
            status = "HIGH coverage (>90%)"
        else:
            status = "NOT universal"
        print(f"  Class {cls}: {pct:.1f}% - {status}")

    universal_count = sum(1 for c in unfilterable_classes if class_occurrence[c] == n_records)
    print(f"""
CONCLUSION:
- {universal_count}/6 of C503's "unfilterable" classes are truly universal under full morphology
- The claim was based on MIDDLE-only filtering; full morphology adds PREFIX+SUFFIX constraints
- Even "MIDDLE=None" (ATOMIC) classes may require PREFIX or SUFFIX matches
""")
else:
    print("""
NOTE: Could not find C121 class assignments (equivalence_classes.json).
To complete this analysis, need the class-to-token mapping from Phase 20.
""")
