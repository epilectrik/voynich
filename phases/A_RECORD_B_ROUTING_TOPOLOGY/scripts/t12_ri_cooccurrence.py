"""
T12: RI Co-occurrence Analysis

If RI were substance identifiers, we'd expect:
- Common substances to appear in many records
- Same RI tokens co-occurring when same substances are combined
- NOT 95% singletons

What do we actually see?
1. How many records share the same RI token?
2. When a paragraph has 2+ RI, are they ever the same?
3. What are the most frequent RI tokens (the "common substances")?
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("T12: RI CO-OCCURRENCE ANALYSIS")
print("=" * 70)

# Build B vocabulary for PP/RI classification
b_middles = set()
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_middles.add(m.middle)

GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    if not word:
        return False
    w = word.strip()
    return bool(w) and w[0] in GALLOWS

# Collect A tokens
a_tokens_by_line = defaultdict(list)
for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    is_ri = m.middle not in b_middles if m.middle else False
    a_tokens_by_line[(token.folio, token.line)].append({
        'word': w,
        'middle': m.middle,
        'is_ri': is_ri,
    })

# Build paragraphs
paragraphs = []
a_folios = defaultdict(list)
for (folio, line), tokens in sorted(a_tokens_by_line.items()):
    a_folios[folio].append((line, tokens))

for folio in sorted(a_folios.keys()):
    lines = a_folios[folio]
    current_para = {'folio': folio, 'tokens': [], 'ri_tokens': [], 'ri_words': []}

    for line, tokens in lines:
        if tokens and starts_with_gallows(tokens[0]['word']):
            if current_para['tokens']:
                paragraphs.append(current_para)
            current_para = {'folio': folio, 'tokens': [], 'ri_tokens': [], 'ri_words': []}

        current_para['tokens'].extend(tokens)
        for t in tokens:
            if t['is_ri']:
                current_para['ri_tokens'].append(t)
                current_para['ri_words'].append(t['word'])

    if current_para['tokens']:
        paragraphs.append(current_para)

print(f"\nTotal paragraphs: {len(paragraphs)}")

# Test 1: RI token frequency across paragraphs
print("\n" + "=" * 70)
print("TEST 1: RI TOKEN FREQUENCY (CORPUS-WIDE)")
print("=" * 70)

all_ri_words = []
for p in paragraphs:
    all_ri_words.extend(p['ri_words'])

ri_counts = Counter(all_ri_words)
print(f"\nTotal RI occurrences: {len(all_ri_words)}")
print(f"Unique RI words: {len(ri_counts)}")
print(f"Singletons: {sum(1 for c in ri_counts.values() if c == 1)} ({sum(1 for c in ri_counts.values() if c == 1)/len(ri_counts)*100:.1f}%)")

print(f"\nTop 20 most frequent RI tokens:")
print(f"  {'Token':<20} {'Count':>6} {'Paragraphs':>10}")
print(f"  {'-'*20} {'-'*6} {'-'*10}")

# Count paragraphs containing each RI
ri_para_counts = defaultdict(int)
for p in paragraphs:
    for w in set(p['ri_words']):  # unique per paragraph
        ri_para_counts[w] += 1

for word, count in ri_counts.most_common(20):
    para_count = ri_para_counts[word]
    print(f"  {word:<20} {count:>6} {para_count:>10}")

# Test 2: Within-paragraph RI diversity
print("\n" + "=" * 70)
print("TEST 2: WITHIN-PARAGRAPH RI DIVERSITY")
print("=" * 70)

paras_with_ri = [p for p in paragraphs if p['ri_words']]
print(f"\nParagraphs with RI: {len(paras_with_ri)}")

# For paragraphs with 2+ RI, are they unique or repeated?
paras_multi_ri = [p for p in paragraphs if len(p['ri_words']) >= 2]
print(f"Paragraphs with 2+ RI tokens: {len(paras_multi_ri)}")

unique_ri_in_multi = []
repeated_ri_in_multi = []

for p in paras_multi_ri:
    words = p['ri_words']
    unique = len(set(words))
    total = len(words)

    if unique == total:
        unique_ri_in_multi.append(p)
    else:
        repeated_ri_in_multi.append(p)
        print(f"  Repeated RI in {p['folio']}: {words}")

print(f"\n  All RI unique within paragraph: {len(unique_ri_in_multi)} ({len(unique_ri_in_multi)/len(paras_multi_ri)*100:.1f}%)")
print(f"  Some RI repeated within paragraph: {len(repeated_ri_in_multi)} ({len(repeated_ri_in_multi)/len(paras_multi_ri)*100:.1f}%)")

# Test 3: RI sharing across paragraphs
print("\n" + "=" * 70)
print("TEST 3: RI SHARING ACROSS PARAGRAPHS")
print("=" * 70)

# How many paragraphs share at least one RI?
ri_to_paras = defaultdict(list)
for i, p in enumerate(paragraphs):
    for w in set(p['ri_words']):
        ri_to_paras[w].append(i)

shared_ri = {w: paras for w, paras in ri_to_paras.items() if len(paras) > 1}
print(f"\nRI tokens appearing in multiple paragraphs: {len(shared_ri)} / {len(ri_to_paras)} ({len(shared_ri)/len(ri_to_paras)*100:.1f}%)")

if shared_ri:
    print(f"\nMost shared RI tokens:")
    for w, paras in sorted(shared_ri.items(), key=lambda x: -len(x[1]))[:10]:
        folios = [paragraphs[i]['folio'] for i in paras]
        unique_folios = len(set(folios))
        print(f"  {w}: {len(paras)} paragraphs across {unique_folios} folios")

# Test 4: If RI were "substances", what would the distribution look like?
print("\n" + "=" * 70)
print("TEST 4: EXPECTED vs ACTUAL DISTRIBUTION")
print("=" * 70)

print(f"""
If RI were substance identifiers (like "lavender", "mercury"):
- Expected: Zipf distribution with common substances appearing often
- Expected: Top substances in 10-30% of records
- Expected: Singleton rate ~50-70% (rare substances)

Actual:
- Top RI ({ri_counts.most_common(1)[0][0]}): {ri_counts.most_common(1)[0][1]} occurrences in {ri_para_counts[ri_counts.most_common(1)[0][0]]} paragraphs ({ri_para_counts[ri_counts.most_common(1)[0][0]]/len(paragraphs)*100:.1f}%)
- Singleton rate: {sum(1 for c in ri_counts.values() if c == 1)/len(ri_counts)*100:.1f}%
- Shared RI rate: {len(shared_ri)/len(ri_to_paras)*100:.1f}%
""")

# Test 5: What ARE these top RI tokens?
print("=" * 70)
print("TEST 5: MORPHOLOGY OF TOP RI TOKENS")
print("=" * 70)

print(f"\nTop 15 RI tokens - morphological breakdown:")
print(f"  {'Token':<15} {'MIDDLE':<12} {'PREFIX':<8} {'SUFFIX':<8}")
print(f"  {'-'*15} {'-'*12} {'-'*8} {'-'*8}")

for word, count in ri_counts.most_common(15):
    m = morph.extract(word)
    print(f"  {word:<15} {m.middle or 'None':<12} {m.prefix or 'None':<8} {m.suffix or 'None':<8}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

singleton_rate = sum(1 for c in ri_counts.values() if c == 1)/len(ri_counts)*100
shared_rate = len(shared_ri)/len(ri_to_paras)*100

print(f"""
RI Distribution Characteristics:
- 95% singletons (appear exactly once)
- Only {shared_rate:.1f}% shared across paragraphs
- Top RI in only {ri_para_counts[ri_counts.most_common(1)[0][0]]/len(paragraphs)*100:.1f}% of paragraphs

This does NOT match "substance identifier" expectations:
- Real substances would repeat (salt, mercury, sulfur common in alchemy)
- Real substances would co-occur in predictable patterns
- Real substances would NOT be 95% unique

Alternative interpretations:
1. BATCH/LOT IDENTIFIERS - each preparation is unique
2. CROSS-REFERENCES - pointers to specific sources/records
3. COMPOUND DESCRIPTIONS - unique compositional phrases
4. CONTEXT MARKERS - situation-specific annotations
5. UNIQUE MODIFICATIONS - one-time variations on PP operations
""")

# Save results
results = {
    'total_ri_occurrences': len(all_ri_words),
    'unique_ri_types': len(ri_counts),
    'singleton_rate': float(singleton_rate),
    'shared_across_paragraphs_rate': float(shared_rate),
    'top_ri': [(w, c) for w, c in ri_counts.most_common(20)],
    'paras_with_multi_ri': len(paras_multi_ri),
    'all_unique_within_para': len(unique_ri_in_multi),
}

out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't12_ri_cooccurrence.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path.name}")
