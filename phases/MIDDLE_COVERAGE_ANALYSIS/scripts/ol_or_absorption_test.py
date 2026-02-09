"""
Test if ol/or are absorbed forms of o + l/r
"""
import sys
sys.path.insert(0, 'scripts')
from voynich import Transcript, Morphology
from collections import Counter

tx = Transcript()
morph = Morphology()

b_tokens = list(tx.currier_b())

print("=" * 70)
print("ol/or ABSORPTION TEST: Is 'o' a core MIDDLE?")
print("=" * 70)

# 1. Suffix patterns for o vs ol vs or
print("\n1. SUFFIX PATTERNS")
print("-" * 60)

for mid in ['o', 'ol', 'or']:
    tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).middle == mid]
    if tokens:
        suffixes = Counter(m.suffix or '(none)' for t, m in tokens)
        total = len(tokens)
        no_suffix = suffixes.get('(none)', 0)
        print(f"\n'{mid}' (n={total}):")
        print(f"  No suffix: {no_suffix/total*100:.1f}%")
        for s, count in suffixes.most_common(5):
            pct = count / total * 100
            print(f"    {s:<10} {count:>4} ({pct:>5.1f}%)")

# 2. PREFIX patterns
print("\n2. PREFIX PATTERNS")
print("-" * 60)

for mid in ['o', 'ol', 'or']:
    tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).middle == mid]
    if tokens:
        prefixes = Counter(m.prefix or '(none)' for t, m in tokens)
        total = len(tokens)
        print(f"\n'{mid}' (n={total}):")
        for p, count in prefixes.most_common(8):
            pct = count / total * 100
            print(f"    {p:<10} {count:>4} ({pct:>5.1f}%)")

# 3. Does 'o' take l/r as suffix?
print("\n3. DOES 'o' TAKE l/r AS SUFFIX?")
print("-" * 60)

o_tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).middle == 'o']
o_suffixes = Counter(m.suffix for t, m in o_tokens if m.suffix)

print(f"\n'o' suffix distribution:")
for s, count in o_suffixes.most_common():
    print(f"  {s}: {count}")

# Does o take 'l' or 'r' as suffix ever?
l_suffix = sum(1 for t, m in o_tokens if m.suffix and 'l' in m.suffix)
r_suffix = sum(1 for t, m in o_tokens if m.suffix and 'r' in m.suffix)
print(f"\n'o' with l-containing suffix: {l_suffix}")
print(f"'o' with r-containing suffix: {r_suffix}")

# 4. Most common tokens
print("\n4. MOST COMMON TOKENS")
print("-" * 60)

for mid in ['o', 'ol', 'or']:
    tokens = [t.word for t in b_tokens if morph.extract(t.word).middle == mid]
    token_counts = Counter(tokens)
    print(f"\n'{mid}':")
    for tok, count in token_counts.most_common(8):
        m = morph.extract(tok)
        print(f"  {tok:<15} {count:>4}  PRE={m.prefix or '-':<5} SUF={m.suffix or '-'}")

# 5. The al/ar pattern
print("\n" + "=" * 70)
print("5. THE al/ar PATTERN - Similar absorption?")
print("=" * 70)

for mid in ['al', 'ar']:
    tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).middle == mid]
    if tokens:
        suffixes = Counter(m.suffix or '(none)' for t, m in tokens)
        total = len(tokens)
        no_suffix = suffixes.get('(none)', 0)
        print(f"\n'{mid}' (n={total}):")
        print(f"  No suffix: {no_suffix/total*100:.1f}%")
        prefixes = Counter(m.prefix or '(none)' for t, m in tokens)
        print(f"  Top prefixes:")
        for p, count in prefixes.most_common(5):
            pct = count / total * 100
            print(f"    {p:<10} {count:>4} ({pct:>5.1f}%)")

# 6. Summary
print("\n" + "=" * 70)
print("6. ABSORPTION PATTERN SUMMARY")
print("=" * 70)

# All potential absorbed MIDDLEs
ABSORBED_CANDIDATES = {
    'e': ['edy', 'ey', 'eey', 'ed', 'eo', 'eol', 'ee', 'eeo'],
    'o': ['ol', 'or', 'ody', 'oey'],
    'a': ['al', 'ar', 'ain', 'aiin', 'am'],
}

print("\nAbsorption candidates by core:")
for core, absorbed in ABSORBED_CANDIDATES.items():
    core_count = len([t for t in b_tokens if morph.extract(t.word).middle == core])
    absorbed_count = sum(len([t for t in b_tokens if morph.extract(t.word).middle == m]) for m in absorbed)
    total = core_count + absorbed_count
    print(f"\n'{core}' family:")
    print(f"  Core '{core}': {core_count}")
    print(f"  Absorbed: {absorbed_count}")
    print(f"  Total: {total}")
    for m in absorbed:
        count = len([t for t in b_tokens if morph.extract(t.word).middle == m])
        if count > 50:
            print(f"    {m}: {count}")
