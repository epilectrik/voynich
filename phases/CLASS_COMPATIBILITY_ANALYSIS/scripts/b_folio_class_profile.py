"""
What distinguishes high vs low compatibility B folios?

High compatibility folios (~45%): f31r, f33v, f66r
Low compatibility folios (~31%): f48r, f105r, f50r

Question: Is it about which classes they use?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("B FOLIO CLASS PROFILE ANALYSIS")
print("What distinguishes high vs low compatibility folios?")
print("=" * 70)

# Build B tokens with classes
b_tokens = {}
for token in tx.currier_b():
    word = token.word
    if word and word not in b_tokens:
        m = morph.extract(word)
        if m.prefix:
            cls = f"P_{m.prefix}"
        elif m.suffix:
            cls = f"S_{m.suffix}"
        else:
            cls = "BARE"
        b_tokens[word] = {'class': cls, 'prefix': m.prefix}

# B folio class distributions
b_folio_classes = defaultdict(Counter)
b_folio_total = Counter()

for token in tx.currier_b():
    word = token.word
    if word and word in b_tokens:
        folio = token.folio
        cls = b_tokens[word]['class']
        b_folio_classes[folio][cls] += 1
        b_folio_total[folio] += 1

# High and low compatibility folios
high_compat = ['f31r', 'f33v', 'f66r', 'f95r1', 'f33r']
low_compat = ['f48r', 'f105r', 'f50r', 'f107v', 'f105v']

print("\n--- HIGH COMPATIBILITY FOLIOS (~45%) ---")
for folio in high_compat:
    if folio in b_folio_classes:
        total = b_folio_total[folio]
        classes = b_folio_classes[folio]
        print(f"\n{folio}: {total} tokens, {len(classes)} classes")
        # Top classes
        for cls, count in classes.most_common(10):
            pct = 100 * count / total
            print(f"  {cls}: {count} ({pct:.1f}%)")

print("\n--- LOW COMPATIBILITY FOLIOS (~31%) ---")
for folio in low_compat:
    if folio in b_folio_classes:
        total = b_folio_total[folio]
        classes = b_folio_classes[folio]
        print(f"\n{folio}: {total} tokens, {len(classes)} classes")
        for cls, count in classes.most_common(10):
            pct = 100 * count / total
            print(f"  {cls}: {count} ({pct:.1f}%)")

# Compare BARE usage
print("\n" + "=" * 70)
print("BARE CLASS COMPARISON")
print("=" * 70)

print("\nBARE (no PREFIX) usage:")
print("\nHigh compatibility folios:")
for folio in high_compat:
    if folio in b_folio_classes:
        bare_count = b_folio_classes[folio].get('BARE', 0)
        total = b_folio_total[folio]
        print(f"  {folio}: {bare_count}/{total} ({100*bare_count/total:.1f}% BARE)")

print("\nLow compatibility folios:")
for folio in low_compat:
    if folio in b_folio_classes:
        bare_count = b_folio_classes[folio].get('BARE', 0)
        total = b_folio_total[folio]
        print(f"  {folio}: {bare_count}/{total} ({100*bare_count/total:.1f}% BARE)")

# Compare PREFIX class concentration
print("\n" + "=" * 70)
print("PREFIX CLASS CONCENTRATION")
print("=" * 70)

# How concentrated are PREFIX classes?
def gini(values):
    """Gini coefficient - 0 = perfectly equal, 1 = perfectly concentrated"""
    if not values or sum(values) == 0:
        return 0
    values = sorted(values)
    n = len(values)
    total = sum(values)
    cum = 0
    gini_sum = 0
    for i, v in enumerate(values):
        cum += v
        gini_sum += cum
    return 1 - 2 * gini_sum / (n * total) + 1/n

print("\nClass distribution concentration (Gini):")
print("\nHigh compatibility folios:")
for folio in high_compat:
    if folio in b_folio_classes:
        values = list(b_folio_classes[folio].values())
        g = gini(values)
        print(f"  {folio}: Gini={g:.3f} ({len(b_folio_classes[folio])} classes)")

print("\nLow compatibility folios:")
for folio in low_compat:
    if folio in b_folio_classes:
        values = list(b_folio_classes[folio].values())
        g = gini(values)
        print(f"  {folio}: Gini={g:.3f} ({len(b_folio_classes[folio])} classes)")

# Compare specific PREFIX classes
print("\n" + "=" * 70)
print("COMMON PREFIX CLASS USAGE")
print("=" * 70)

common_prefixes = ['P_ch', 'P_sh', 'P_qo', 'P_da', 'P_ok', 'P_ot', 'P_ol']

print("\nUsage of common PREFIX classes (% of folio tokens):")
print("\n" + "High compatibility:".ljust(20) + "".join(p.ljust(10) for p in common_prefixes))
for folio in high_compat:
    if folio in b_folio_classes:
        total = b_folio_total[folio]
        row = folio.ljust(20)
        for p in common_prefixes:
            count = b_folio_classes[folio].get(p, 0)
            pct = 100 * count / total
            row += f"{pct:.1f}%".ljust(10)
        print(row)

print("\n" + "Low compatibility:".ljust(20) + "".join(p.ljust(10) for p in common_prefixes))
for folio in low_compat:
    if folio in b_folio_classes:
        total = b_folio_total[folio]
        row = folio.ljust(20)
        for p in common_prefixes:
            count = b_folio_classes[folio].get(p, 0)
            pct = 100 * count / total
            row += f"{pct:.1f}%".ljust(10)
        print(row)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Average BARE for high vs low
high_bare_pct = []
low_bare_pct = []
for folio in high_compat:
    if folio in b_folio_classes:
        bare = b_folio_classes[folio].get('BARE', 0)
        total = b_folio_total[folio]
        high_bare_pct.append(100 * bare / total)

for folio in low_compat:
    if folio in b_folio_classes:
        bare = b_folio_classes[folio].get('BARE', 0)
        total = b_folio_total[folio]
        low_bare_pct.append(100 * bare / total)

print(f"""
HIGH vs LOW COMPATIBILITY FOLIOS:

BARE class usage:
  High compat: {sum(high_bare_pct)/len(high_bare_pct):.1f}% mean BARE
  Low compat: {sum(low_bare_pct)/len(low_bare_pct):.1f}% mean BARE

INTERPRETATION:
  BARE tokens (no PREFIX required) are accessible from almost all A records
  (BARE class has 96.8% A record coverage per C509.c).

  B folios with MORE BARE tokens are more universally accessible.
  B folios with MORE PREFIX-specific tokens are less accessible.
""")
