"""
B-Exclusive Vocabulary Breakdown

Question: The 34.4% of B vocabulary that's never legal under any A folio (C736) -
how much is HT/UN vs classified?

If mostly HT: Expected, since HT by definition uses non-PP MIDDLEs
If includes classified: Interesting - which classes? Why?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())
token_to_class = ctm['token_to_class']

print("=" * 70)
print("B-EXCLUSIVE VOCABULARY BREAKDOWN")
print("=" * 70)

# Get all A MIDDLEs (PP pool)
a_middles = set()
for token in tx.currier_a():
    w = token.word.strip()
    if w and '*' not in w:
        m = morph.extract(w)
        if m.middle:
            a_middles.add(m.middle)

print(f"\nA MIDDLEs (PP pool): {len(a_middles)}")

# Get all B tokens with their properties
b_tokens = {}  # word -> {middle, is_classified, class_id}
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    if w not in b_tokens:
        m = morph.extract(w)
        is_classified = w in classified_tokens
        class_id = token_to_class.get(w, None)
        b_tokens[w] = {
            'middle': m.middle,
            'is_classified': is_classified,
            'class_id': class_id
        }

print(f"B token types: {len(b_tokens)}")

# Partition by accessibility
# Token is "legal" if its MIDDLE is in the A pool (simplified C502.a - just MIDDLE axis)
legal_tokens = set()
exclusive_tokens = set()

for word, props in b_tokens.items():
    if props['middle'] and props['middle'] in a_middles:
        legal_tokens.add(word)
    else:
        exclusive_tokens.add(word)

print(f"\nAccessibility partition:")
print(f"  Legal (MIDDLE in PP): {len(legal_tokens)} ({100*len(legal_tokens)/len(b_tokens):.1f}%)")
print(f"  B-exclusive: {len(exclusive_tokens)} ({100*len(exclusive_tokens)/len(b_tokens):.1f}%)")

# Break down exclusive tokens
exclusive_classified = [w for w in exclusive_tokens if b_tokens[w]['is_classified']]
exclusive_ht = [w for w in exclusive_tokens if not b_tokens[w]['is_classified']]

print(f"\nB-exclusive breakdown:")
print(f"  Classified: {len(exclusive_classified)} ({100*len(exclusive_classified)/len(exclusive_tokens):.1f}% of exclusive)")
print(f"  HT/UN: {len(exclusive_ht)} ({100*len(exclusive_ht)/len(exclusive_tokens):.1f}% of exclusive)")

# Which classes are in B-exclusive?
if exclusive_classified:
    class_counts = Counter(b_tokens[w]['class_id'] for w in exclusive_classified)
    print(f"\nClassified B-exclusive by class:")
    for class_id, count in class_counts.most_common(15):
        print(f"  Class {class_id}: {count} types")

# Sanity check: Are there classified tokens with MIDDLEs NOT in PP?
print("\n" + "=" * 70)
print("SANITY CHECK: CLASSIFIED TOKENS WITH NON-PP MIDDLES")
print("=" * 70)

classified_middles = set()
classified_pp_middles = set()
classified_exclusive_middles = set()

for word in classified_tokens:
    if word in b_tokens:
        mid = b_tokens[word]['middle']
        if mid:
            classified_middles.add(mid)
            if mid in a_middles:
                classified_pp_middles.add(mid)
            else:
                classified_exclusive_middles.add(mid)

print(f"\nClassified token MIDDLEs: {len(classified_middles)}")
print(f"  In PP (shared A-B): {len(classified_pp_middles)} ({100*len(classified_pp_middles)/len(classified_middles):.1f}%)")
print(f"  B-exclusive: {len(classified_exclusive_middles)} ({100*len(classified_exclusive_middles)/len(classified_middles):.1f}%)")

if classified_exclusive_middles:
    print(f"\nB-exclusive classified MIDDLEs: {sorted(classified_exclusive_middles)[:20]}")

# Check HT MIDDLEs
print("\n" + "=" * 70)
print("HT/UN MIDDLE PROFILE")
print("=" * 70)

ht_middles = set()
ht_pp_middles = set()
ht_exclusive_middles = set()

for word in b_tokens:
    if not b_tokens[word]['is_classified']:
        mid = b_tokens[word]['middle']
        if mid:
            ht_middles.add(mid)
            if mid in a_middles:
                ht_pp_middles.add(mid)
            else:
                ht_exclusive_middles.add(mid)

print(f"\nHT token MIDDLEs: {len(ht_middles)}")
print(f"  In PP (shared A-B): {len(ht_pp_middles)} ({100*len(ht_pp_middles)/len(ht_middles):.1f}%)")
print(f"  B-exclusive: {len(ht_exclusive_middles)} ({100*len(ht_exclusive_middles)/len(ht_middles):.1f}%)")

# Verdict
print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

if len(exclusive_ht) > 0.9 * len(exclusive_tokens):
    print("""
B-EXCLUSIVE = HT/UN (as expected)

The 34.4% B-exclusive vocabulary is almost entirely HT/UN tokens.
This is expected because:
  - HT/UN by definition uses vocabulary outside the 479-type classified grammar
  - Most HT/UN MIDDLEs are B-exclusive (not shared with A)
  - The "autonomous B grammar" language in C736 is misleading -
    it's the non-operational HT layer, not classified grammar
""")
else:
    ht_pct = 100 * len(exclusive_ht) / len(exclusive_tokens)
    classified_pct = 100 * len(exclusive_classified) / len(exclusive_tokens)
    print(f"""
MIXED COMPOSITION

B-exclusive vocabulary is {ht_pct:.1f}% HT/UN, {classified_pct:.1f}% classified.

The classified B-exclusive tokens suggest:
  - Some classes use MIDDLEs not found in any A folio
  - These represent B's truly autonomous operations
  - C736's "autonomous grammar" interpretation may be partially correct
""")
