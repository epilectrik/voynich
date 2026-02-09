"""
104_f58r_analysis.py

Is f58r special? It has the most singleton vocabulary and the most B dependencies.
- What section is it in?
- How large is it?
- What's its total vocabulary coverage potential?
- Is it a "hub" folio or just large?
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("f58r SPECIAL ANALYSIS")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

# Get f58r tokens
f58r_tokens = [t for t in tx.currier_a() if t.folio == 'f58r' and t.word and '*' not in t.word]

print(f"\nf58r basic stats:")
print(f"  Total tokens: {len(f58r_tokens)}")

# Section
sections = set(t.section for t in f58r_tokens if hasattr(t, 'section'))
print(f"  Section(s): {sections}")

# PP vocabulary
f58r_pp = set()
for t in f58r_tokens:
    try:
        m = morph.extract(t.word)
        if m.middle and m.middle in pp_middles:
            f58r_pp.add(m.middle)
    except:
        pass

print(f"  PP MIDDLEs: {len(f58r_pp)}")

# Compare to other A folios
a_folio_vocab = defaultdict(set)
a_folio_tokens = defaultdict(int)
for t in tx.currier_a():
    if t.word and '*' not in t.word:
        a_folio_tokens[t.folio] += 1
        try:
            m = morph.extract(t.word)
            if m.middle and m.middle in pp_middles:
                a_folio_vocab[t.folio].add(m.middle)
        except:
            pass

# Rank f58r
vocab_sizes = [(f, len(v)) for f, v in a_folio_vocab.items()]
vocab_sizes.sort(key=lambda x: -x[1])

f58r_rank = next(i for i, (f, _) in enumerate(vocab_sizes) if f == 'f58r') + 1
print(f"  Vocabulary rank: #{f58r_rank} of {len(vocab_sizes)} A folios")

token_sizes = [(f, c) for f, c in a_folio_tokens.items()]
token_sizes.sort(key=lambda x: -x[1])
f58r_token_rank = next(i for i, (f, _) in enumerate(token_sizes) if f == 'f58r') + 1
print(f"  Token count rank: #{f58r_token_rank}")

# What fraction of ALL B vocabulary can f58r cover?
all_b_pp = set()
for t in tx.currier_b():
    if t.word and '*' not in t.word:
        try:
            m = morph.extract(t.word)
            if m.middle and m.middle in pp_middles:
                all_b_pp.add(m.middle)
        except:
            pass

f58r_b_coverage = len(f58r_pp & all_b_pp) / len(all_b_pp)
print(f"\n  Coverage of ALL B PP vocabulary: {f58r_b_coverage:.1%}")

# Compare to other top folios
print(f"\nTop 10 A folios by PP vocabulary size:")
for f, size in vocab_sizes[:10]:
    b_coverage = len(a_folio_vocab[f] & all_b_pp) / len(all_b_pp)
    tokens = a_folio_tokens[f]
    print(f"  {f}: {size} MIDDLEs, {tokens} tokens, covers {b_coverage:.1%} of B")

# What makes f58r's vocabulary unique?
print("\n" + "="*70)
print("f58r's UNIQUE VOCABULARY")
print("="*70)

# Find vocabulary only in f58r
all_a_vocab = set()
for v in a_folio_vocab.values():
    all_a_vocab.update(v)

other_a_vocab = set()
for f, v in a_folio_vocab.items():
    if f != 'f58r':
        other_a_vocab.update(v)

f58r_unique = f58r_pp - other_a_vocab
print(f"\nMIDDLEs unique to f58r: {len(f58r_unique)}")
print(f"  {sorted(f58r_unique)}")

# How many B paragraphs use f58r-unique vocabulary?
GALLOWS = {'k', 't', 'p', 'f'}
def starts_with_gallows(word):
    return word and word[0] in GALLOWS

b_by_folio_line = defaultdict(list)
for t in tx.currier_b():
    if t.word and '*' not in t.word:
        b_by_folio_line[(t.folio, t.line)].append(t)

b_paragraphs = []
current = {'tokens': [], 'folio': None}
current_folio = None
for (folio, line) in sorted(b_by_folio_line.keys()):
    tokens = b_by_folio_line[(folio, line)]
    if tokens and (starts_with_gallows(tokens[0].word) or folio != current_folio):
        if current['tokens']:
            b_paragraphs.append(current)
        current = {'tokens': [], 'folio': folio}
        current_folio = folio
    current['tokens'].extend(tokens)
if current['tokens']:
    b_paragraphs.append(current)

def get_pp_middles(tokens):
    pp = set()
    for t in tokens:
        try:
            m = morph.extract(t.word)
            if m.middle and m.middle in pp_middles:
                pp.add(m.middle)
        except:
            pass
    return pp

b_using_f58r_unique = 0
for b in b_paragraphs:
    b_pp = get_pp_middles(b['tokens'])
    if b_pp & f58r_unique:
        b_using_f58r_unique += 1

print(f"\nB paragraphs using f58r-unique vocabulary: {b_using_f58r_unique} of {len(b_paragraphs)}")

# What section is f58r in?
print("\n" + "="*70)
print("WHAT IS f58r?")
print("="*70)

# Check quire/section info
print(f"\nLooking at f58r content...")
print(f"First 20 words: {[t.word for t in f58r_tokens[:20]]}")

# RI vs PP breakdown
f58r_ri = set()
for t in f58r_tokens:
    try:
        m = morph.extract(t.word)
        if m.middle and m.middle in ri_middles:
            f58r_ri.add(m.middle)
    except:
        pass

print(f"\nRI MIDDLEs in f58r: {len(f58r_ri)}")
print(f"PP MIDDLEs in f58r: {len(f58r_pp)}")

# Is f58r unusually RI-rich or PP-rich?
folio_ri_counts = {}
folio_pp_counts = {}
for f, tokens in [(f, [t for t in tx.currier_a() if t.folio == f and t.word and '*' not in t.word])
                   for f in a_folio_vocab.keys()]:
    ri = set()
    pp = set()
    for t in tokens:
        try:
            m = morph.extract(t.word)
            if m.middle:
                if m.middle in ri_middles:
                    ri.add(m.middle)
                if m.middle in pp_middles:
                    pp.add(m.middle)
        except:
            pass
    folio_ri_counts[f] = len(ri)
    folio_pp_counts[f] = len(pp)

mean_ri = sum(folio_ri_counts.values()) / len(folio_ri_counts)
mean_pp = sum(folio_pp_counts.values()) / len(folio_pp_counts)

print(f"\nComparison to mean A folio:")
print(f"  f58r RI: {folio_ri_counts.get('f58r', 0)} (mean: {mean_ri:.1f})")
print(f"  f58r PP: {folio_pp_counts.get('f58r', 0)} (mean: {mean_pp:.1f})")
