#!/usr/bin/env python3
"""
Key question: Do articulator-prefixed tokens share MIDDLEs with non-articulator tokens?

If y+ch+MIDDLE and ch+MIDDLE produce the SAME MIDDLE, then:
- Articulators are truly optional (C291: "100% removable without identity loss")
- Our extended prefix extraction is correct

If they produce DIFFERENT MIDDLEs, we're over-parsing.
"""

import csv
from collections import defaultdict, Counter

# Extended prefix list with articulators
ARTICULATOR_PREFIXES = ['ych', 'ysh', 'yda', 'yok', 'yke', 'yte', 'yto', 'yta', 'yko', 'yka', 'ytch', 'ykch', 'ypch']
CORE_PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES_NOART = ['pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
                           'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
                           'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']

ALL_PREFIXES = ARTICULATOR_PREFIXES + CORE_PREFIXES + EXTENDED_PREFIXES_NOART
ALL_PREFIXES = sorted(set(ALL_PREFIXES), key=len, reverse=True)

NON_ARTICULATOR_PREFIXES = CORE_PREFIXES + EXTENDED_PREFIXES_NOART
NON_ARTICULATOR_PREFIXES = sorted(set(NON_ARTICULATOR_PREFIXES), key=len, reverse=True)

SUFFIXES = ['daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
            'chedy', 'shedy', 'tedy', 'kedy', 'cheey', 'sheey', 'chey', 'shey',
            'chol', 'shol', 'chor', 'shor', 'eedy', 'edy', 'eey',
            'iin', 'ain', 'oin', 'ein', 'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
            'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
            'in', 'an', 'on', 'en', 'y', 'l', 'r', 'm', 'n', 's']
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)

def extract_middle(token, prefix_list):
    if not token:
        return None, None
    working = token
    prefix = None
    for p in prefix_list:
        if working.startswith(p) and len(working) > len(p):
            prefix = p
            working = working[len(p):]
            break
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            working = working[:-len(s)]
            break
    return prefix, working if working else None

# Collect MIDDLEs by prefix type
articulator_middles = defaultdict(set)  # prefix -> set of MIDDLEs
non_articulator_middles = defaultdict(set)

articulator_examples = defaultdict(list)
non_articulator_examples = defaultdict(list)

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        prefix, middle = extract_middle(word, ALL_PREFIXES)
        if middle:
            if prefix in ARTICULATOR_PREFIXES:
                articulator_middles[prefix].add(middle)
                if len(articulator_examples[prefix]) < 5:
                    articulator_examples[prefix].append((word, middle))
            elif prefix in NON_ARTICULATOR_PREFIXES:
                non_articulator_middles[prefix].add(middle)
                if len(non_articulator_examples[prefix]) < 5:
                    non_articulator_examples[prefix].append((word, middle))

print("="*70)
print("ARTICULATOR vs NON-ARTICULATOR MIDDLE SHARING")
print("="*70)

# Check: do ych MIDDLEs overlap with ch MIDDLEs?
# If C291 is correct (articulators removable without identity loss),
# then ych tokens should use the SAME MIDDLEs as ch tokens

pairs_to_check = [
    ('ych', 'ch'),
    ('ysh', 'sh'),
    ('yda', 'da'),
    ('yto', 'to'),
    ('yta', 'ta'),
    ('yke', 'ke'),
    ('yte', 'te'),
    ('yko', 'ko'),
    ('yka', 'ka'),
    ('ytch', 'tch'),
    ('ykch', 'kch'),
]

print("\nMIDDLE OVERLAP: articulator-prefix vs base-prefix")
print("-" * 70)

total_art_middles = set()
total_overlap = 0
total_art_only = 0

for art_p, base_p in pairs_to_check:
    art_set = articulator_middles.get(art_p, set())
    base_set = non_articulator_middles.get(base_p, set())

    if not art_set:
        continue

    overlap = art_set & base_set
    art_only = art_set - base_set

    total_art_middles.update(art_set)
    total_overlap += len(overlap)
    total_art_only += len(art_only)

    overlap_pct = 100 * len(overlap) / len(art_set) if art_set else 0

    print(f"\n{art_p} vs {base_p}:")
    print(f"  {art_p} MIDDLEs: {len(art_set)}")
    print(f"  {base_p} MIDDLEs: {len(base_set)}")
    print(f"  Shared: {len(overlap)} ({overlap_pct:.1f}%)")
    print(f"  {art_p}-only: {len(art_only)}")

    if overlap:
        print(f"  Shared examples: {sorted(overlap)[:5]}")
    if art_only:
        print(f"  {art_p}-only examples: {sorted(art_only)[:5]}")

    # Show token examples
    print(f"  {art_p} token examples:")
    for token, mid in articulator_examples.get(art_p, [])[:3]:
        print(f"    {token} -> middle={mid}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
Total articulator-prefix MIDDLEs: {len(total_art_middles)}
Shared with base-prefix: {total_overlap}
Articulator-only: {total_art_only}
""")

if total_overlap > total_art_only:
    print("CONCLUSION: Articulator tokens SHARE most MIDDLEs with non-articulator tokens")
    print("  -> C291 confirmed: articulators are 'removable without identity loss'")
    print("  -> Extended prefix extraction is CORRECT")
else:
    print("CONCLUSION: Articulator tokens have UNIQUE MIDDLEs")
    print("  -> Articulators may be part of the MIDDLE identity")
    print("  -> Original extraction may be better")

# ============================================================
# ADDITIONAL CHECK: What about tokens with NO prefix?
# ============================================================
print("\n" + "="*70)
print("TOKENS WITH NO RECOGNIZED PREFIX")
print("="*70)

no_prefix_middles = set()
no_prefix_examples = []

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        prefix, middle = extract_middle(word, ALL_PREFIXES)
        if prefix is None and middle:
            no_prefix_middles.add(middle)
            if len(no_prefix_examples) < 20:
                no_prefix_examples.append((word, middle))

print(f"\nTokens with no prefix: produces {len(no_prefix_middles)} unique MIDDLEs")
print(f"\nExamples of prefix-less tokens:")
for token, mid in no_prefix_examples[:15]:
    print(f"  {token} -> middle={mid}")

# Check overlap with prefixed tokens
all_prefixed_middles = set()
for mset in articulator_middles.values():
    all_prefixed_middles.update(mset)
for mset in non_articulator_middles.values():
    all_prefixed_middles.update(mset)

overlap_with_prefixed = no_prefix_middles & all_prefixed_middles
no_prefix_only = no_prefix_middles - all_prefixed_middles

print(f"\nNo-prefix MIDDLEs that also appear with prefix: {len(overlap_with_prefixed)}")
print(f"No-prefix-only MIDDLEs: {len(no_prefix_only)}")
