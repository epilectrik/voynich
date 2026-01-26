"""Quick check on token 'k' - why does it have 0% coverage?"""

import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import Counter

tx = Transcript()
morph = Morphology()

print("=== Token 'k' in Currier B ===")
k_count = sum(1 for t in tx.currier_b() if t.word == 'k')
print(f"Occurrences in B: {k_count}")

m = morph.extract('k')
print(f"Morphology: prefix={m.prefix}, middle={m.middle}, suffix={m.suffix}")

print("\n=== MIDDLE 'k' in Currier A ===")
a_middles = Counter()
for t in tx.currier_a():
    m = morph.extract(t.word)
    if m.middle:
        a_middles[m.middle] += 1

print(f"MIDDLE 'k' count in A: {a_middles.get('k', 0)}")

# Top middles in A
print("\nTop 20 MIDDLEs in A:")
for mid, count in a_middles.most_common(20):
    print(f"  {mid}: {count}")

print("\n=== Token 'k' in Currier A ===")
k_in_a = sum(1 for t in tx.currier_a() if t.word == 'k')
print(f"Occurrences in A: {k_in_a}")

print("\n=== What 'k' needs to survive ===")
m = morph.extract('k')
print(f"k has MIDDLE={m.middle}, PREFIX={m.prefix}, SUFFIX={m.suffix}")
print(f"For k to survive: A record needs MIDDLE 'k' in its PP vocabulary")
print(f"But MIDDLE 'k' appears {a_middles.get('k', 0)} times total in A")

# Check B middles
print("\n=== Is 'k' a valid B MIDDLE? ===")
b_middles = set()
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m.middle:
        b_middles.add(m.middle)

print(f"'k' in B MIDDLE vocabulary: {'k' in b_middles}")
print(f"Total unique B MIDDLEs: {len(b_middles)}")
