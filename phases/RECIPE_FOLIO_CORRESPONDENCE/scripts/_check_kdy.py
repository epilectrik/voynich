"""Quick check: does k+dy (without intervening e) exist in Currier B?"""
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript
from collections import Counter

tx = Transcript()

# Find ALL tokens ending in 'dy' and classify by whether there's an 'e' before 'dy'
kdy_no_e = Counter()  # k immediately before dy
kedy = Counter()      # ke before dy
keedy = Counter()     # kee before dy

for t in tx.currier_b():
    w = t.word
    if not w.endswith('dy'):
        continue
    # Find position of 'dy' at end
    stem = w[:-2]  # everything before 'dy'
    if not stem:
        continue

    if stem.endswith('k'):
        kdy_no_e[w] += 1
    elif stem.endswith('ke') and not stem.endswith('kee'):
        kedy[w] += 1
    elif stem.endswith('kee'):
        keedy[w] += 1

print("=== k + dy (NO intervening e) ===")
print(f"Unique tokens: {len(kdy_no_e)}")
for w, c in kdy_no_e.most_common(20):
    print(f"  {w}: {c}")

print(f"\n=== ke + dy (one e) ===")
print(f"Unique tokens: {len(kedy)}")
for w, c in kedy.most_common(20):
    print(f"  {w}: {c}")

print(f"\n=== kee + dy (two e's) ===")
print(f"Unique tokens: {len(keedy)}")
for w, c in keedy.most_common(20):
    print(f"  {w}: {c}")

print(f"\n=== Summary ===")
print(f"k+dy (no e): {sum(kdy_no_e.values())} tokens, {len(kdy_no_e)} types")
print(f"ke+dy (one e): {sum(kedy.values())} tokens, {len(kedy)} types")
print(f"kee+dy (two e): {sum(keedy.values())} tokens, {len(keedy)} types")
