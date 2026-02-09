"""
Inventory what token patterns we HAVE mapped vs what remains unexplained.
Then examine a specific B folio to see what's not understood.
"""
import sys
sys.path.insert(0, 'scripts')
from voynich import Transcript, Morphology
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()

b_tokens = list(tx.currier_b())

print("=" * 70)
print("TOKEN PATTERN INVENTORY: MAPPED vs UNMAPPED")
print("=" * 70)

# What we've mapped
MAPPED_MIDDLES = {
    # Preparation tier
    'te', 'pch', 'lch', 'tch', 'ksh',
    # Core tier
    'k', 't', 'e',
    # Extended tier
    'ke', 'kch'
}

# Count tokens by whether their MIDDLE is mapped
mapped_count = 0
unmapped_middles = Counter()
all_middles = Counter()

for t in b_tokens:
    m = morph.extract(t.word)
    if m.middle:
        all_middles[m.middle] += 1
        if m.middle in MAPPED_MIDDLES:
            mapped_count += 1
        else:
            unmapped_middles[m.middle] += 1

total = len(b_tokens)
print(f"\nTotal B tokens: {total}")
print(f"Tokens with MAPPED MIDDLEs: {mapped_count} ({mapped_count/total*100:.1f}%)")
print(f"Tokens with UNMAPPED MIDDLEs: {sum(unmapped_middles.values())} ({sum(unmapped_middles.values())/total*100:.1f}%)")

print(f"\nUnique MIDDLEs total: {len(all_middles)}")
print(f"Mapped MIDDLEs: {len(MAPPED_MIDDLES)}")
print(f"Unmapped MIDDLEs: {len(unmapped_middles)}")

# Top unmapped MIDDLEs
print("\n" + "=" * 70)
print("TOP 30 UNMAPPED MIDDLEs (by frequency)")
print("=" * 70)

for mid, count in unmapped_middles.most_common(30):
    pct = count / total * 100
    print(f"  {mid:<15} {count:>5} ({pct:>5.2f}%)")

# What categories might these fall into?
print("\n" + "=" * 70)
print("CATEGORIZING UNMAPPED MIDDLEs")
print("=" * 70)

# Infrastructure candidates (from existing knowledge)
INFRA_CANDIDATES = {'aiin', 'ain', 'al', 'ar', 'ol', 'or', 'y', 'dy', 'edy', 'ey'}
# These look like pure suffixes used as MIDDLEs - structural markers

# Check overlap
infra_in_unmapped = [m for m in INFRA_CANDIDATES if m in unmapped_middles]
print(f"\nInfrastructure candidates in unmapped: {infra_in_unmapped}")
infra_count = sum(unmapped_middles[m] for m in infra_in_unmapped)
print(f"Infrastructure token count: {infra_count} ({infra_count/total*100:.1f}%)")

# Compound MIDDLEs (contain mapped MIDDLEs as substrings)
print("\n" + "=" * 70)
print("COMPOUND MIDDLEs (contain mapped MIDDLEs)")
print("=" * 70)

compound_middles = []
for mid in unmapped_middles:
    contained = [m for m in MAPPED_MIDDLES if m in mid and m != mid]
    if contained:
        compound_middles.append((mid, contained, unmapped_middles[mid]))

compound_middles.sort(key=lambda x: -x[2])
print("\nTop 20 compound MIDDLEs:")
for mid, contained, count in compound_middles[:20]:
    print(f"  {mid:<15} contains {contained} (n={count})")

# Now let's look at a specific folio
print("\n" + "=" * 70)
print("EXAMINING A SPECIFIC B FOLIO: f103r (HERBAL_B)")
print("=" * 70)

folio_tokens = [t for t in b_tokens if t.folio == 'f103r']
print(f"\nTokens on f103r: {len(folio_tokens)}")

# Group by line
by_line = defaultdict(list)
for t in folio_tokens:
    by_line[t.line].append(t)

# Show first 10 lines with analysis
print("\nFirst 10 lines with token analysis:")
print("-" * 70)

for line_num in sorted(by_line.keys(), key=lambda x: int(x) if x.isdigit() else 0)[:10]:
    tokens = by_line[line_num]
    print(f"\nLine {line_num}:")

    for t in tokens:
        m = morph.extract(t.word)

        # Categorize
        if m.middle in MAPPED_MIDDLES:
            if m.middle in {'te', 'pch', 'lch', 'tch', 'ksh'}:
                category = "PREP"
            elif m.middle in {'k', 't', 'e'}:
                category = "CORE"
            elif m.middle in {'ke', 'kch'}:
                category = "EXT"
            else:
                category = "MAPPED"
        elif m.middle in INFRA_CANDIDATES:
            category = "INFRA?"
        elif any(mapped in m.middle for mapped in MAPPED_MIDDLES):
            category = "COMPOUND?"
        else:
            category = "???"

        print(f"  {t.word:<15} MID={m.middle:<8} PRE={m.prefix or '-':<5} SUF={m.suffix or '-':<5} [{category}]")

# Summary of folio
print("\n" + "=" * 70)
print("f103r CATEGORY SUMMARY")
print("=" * 70)

folio_categories = Counter()
for t in folio_tokens:
    m = morph.extract(t.word)
    if m.middle in MAPPED_MIDDLES:
        if m.middle in {'te', 'pch', 'lch', 'tch', 'ksh'}:
            folio_categories['PREP'] += 1
        elif m.middle in {'k', 't', 'e'}:
            folio_categories['CORE'] += 1
        elif m.middle in {'ke', 'kch'}:
            folio_categories['EXT'] += 1
    elif m.middle in INFRA_CANDIDATES:
        folio_categories['INFRA'] += 1
    elif any(mapped in (m.middle or '') for mapped in MAPPED_MIDDLES):
        folio_categories['COMPOUND'] += 1
    else:
        folio_categories['UNKNOWN'] += 1

print()
for cat, count in folio_categories.most_common():
    pct = count / len(folio_tokens) * 100
    print(f"  {cat:<12} {count:>4} ({pct:>5.1f}%)")

# What are the UNKNOWN tokens?
print("\n" + "=" * 70)
print("f103r UNKNOWN TOKENS (not yet categorized)")
print("=" * 70)

unknown_tokens = []
for t in folio_tokens:
    m = morph.extract(t.word)
    if m.middle not in MAPPED_MIDDLES and m.middle not in INFRA_CANDIDATES:
        if not any(mapped in (m.middle or '') for mapped in MAPPED_MIDDLES):
            unknown_tokens.append((t.word, m.middle))

unknown_middles = Counter(mid for word, mid in unknown_tokens)
print(f"\nUnknown tokens: {len(unknown_tokens)}")
print(f"Unique unknown MIDDLEs: {len(unknown_middles)}")
print("\nTop unknown MIDDLEs on f103r:")
for mid, count in unknown_middles.most_common(15):
    examples = [word for word, m in unknown_tokens if m == mid][:3]
    print(f"  {mid:<12} {count:>3}  examples: {examples}")
