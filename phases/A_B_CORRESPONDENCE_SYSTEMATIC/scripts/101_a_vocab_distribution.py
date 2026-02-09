"""
101_a_vocab_distribution.py

How is A vocabulary distributed across folios?
- Is some vocabulary universal (in all A folios)?
- Is some vocabulary specialized (only in specific A folios)?
- What fraction of the 404 PP MIDDLEs is in each A folio?
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("A VOCABULARY DISTRIBUTION ACROSS FOLIOS")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

# Build A folio vocabularies
a_folio_vocab = defaultdict(set)
for t in tx.currier_a():
    if t.word and '*' not in t.word:
        try:
            m = morph.extract(t.word)
            if m.middle and m.middle in pp_middles:
                a_folio_vocab[t.folio].add(m.middle)
        except:
            pass

print(f"\nA folios: {len(a_folio_vocab)}")

# Total PP vocabulary
all_pp = set()
for vocab in a_folio_vocab.values():
    all_pp.update(vocab)
print(f"Total PP MIDDLEs in A: {len(all_pp)}")

# Per-folio coverage
folio_sizes = [(f, len(v)) for f, v in a_folio_vocab.items()]
folio_sizes.sort(key=lambda x: -x[1])

print(f"\nVocabulary per A folio:")
print(f"  Mean: {sum(s for _, s in folio_sizes)/len(folio_sizes):.1f} ({sum(s for _, s in folio_sizes)/len(folio_sizes)/len(all_pp):.1%} of total)")
print(f"  Max:  {folio_sizes[0][1]} ({folio_sizes[0][0]})")
print(f"  Min:  {folio_sizes[-1][1]} ({folio_sizes[-1][0]})")

# Top folios
print(f"\nTop 10 A folios by vocabulary size:")
for f, s in folio_sizes[:10]:
    print(f"  {f}: {s} MIDDLEs ({s/len(all_pp):.1%})")

# Vocabulary universality: how many folios contain each MIDDLE?
middle_folio_count = defaultdict(int)
for folio, vocab in a_folio_vocab.items():
    for m in vocab:
        middle_folio_count[m] += 1

n_folios = len(a_folio_vocab)

print("\n" + "="*70)
print("VOCABULARY UNIVERSALITY")
print("="*70)

# Distribution
universal = [m for m, c in middle_folio_count.items() if c == n_folios]
widespread = [m for m, c in middle_folio_count.items() if c >= n_folios * 0.8]
common = [m for m, c in middle_folio_count.items() if c >= n_folios * 0.5]
rare = [m for m, c in middle_folio_count.items() if c <= n_folios * 0.1]
singleton = [m for m, c in middle_folio_count.items() if c == 1]

print(f"\nHow many folios contain each MIDDLE?")
print(f"  Universal (all {n_folios} folios): {len(universal)} MIDDLEs ({len(universal)/len(all_pp):.1%})")
print(f"  Widespread (>=80% folios): {len(widespread)} MIDDLEs ({len(widespread)/len(all_pp):.1%})")
print(f"  Common (>=50% folios): {len(common)} MIDDLEs ({len(common)/len(all_pp):.1%})")
print(f"  Rare (<=10% folios): {len(rare)} MIDDLEs ({len(rare)/len(all_pp):.1%})")
print(f"  Singleton (1 folio only): {len(singleton)} MIDDLEs ({len(singleton)/len(all_pp):.1%})")

# Mean folio count
counts = list(middle_folio_count.values())
print(f"\nMean folio count per MIDDLE: {sum(counts)/len(counts):.1f} out of {n_folios}")

# What's the B paragraph using?
print("\n" + "="*70)
print("WHAT VOCABULARY DO B PARAGRAPHS USE?")
print("="*70)

# Build B paragraphs
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

b_paras_large = [p for p in b_paragraphs if len(set(
    morph.extract(t.word).middle for t in p['tokens']
    if t.word and '*' not in t.word and morph.extract(t.word).middle in pp_middles
)) >= 10]

# For each B paragraph, what's the mean universality of its vocabulary?
print(f"\nFor each B paragraph, how 'universal' is its vocabulary?")

universality_scores = []
for b in b_paras_large[:100]:  # Sample
    b_vocab = set()
    for t in b['tokens']:
        if t.word and '*' not in t.word:
            try:
                m = morph.extract(t.word)
                if m.middle and m.middle in pp_middles:
                    b_vocab.add(m.middle)
            except:
                pass

    if b_vocab:
        # Mean folio count for vocabulary used
        mean_count = sum(middle_folio_count[m] for m in b_vocab) / len(b_vocab)
        universality_scores.append(mean_count / n_folios)

print(f"  Mean universality: {sum(universality_scores)/len(universality_scores):.1%}")
print(f"  Min: {min(universality_scores):.1%}")
print(f"  Max: {max(universality_scores):.1%}")

# Does B preferentially use universal or specialized vocabulary?
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

universal_frac = len(widespread) / len(all_pp)
print(f"""
VOCABULARY STRUCTURE:
- {len(widespread)} of {len(all_pp)} PP MIDDLEs ({universal_frac:.1%}) are widespread (>=80% of A folios)
- {len(rare)} of {len(all_pp)} PP MIDDLEs ({len(rare)/len(all_pp):.1%}) are rare (<=10% of A folios)

B PARAGRAPH BEHAVIOR:
- Mean universality of B vocabulary: {sum(universality_scores)/len(universality_scores):.1%}
""")

if sum(universality_scores)/len(universality_scores) > 0.7:
    print("-> B paragraphs preferentially use WIDESPREAD vocabulary")
    print("-> The 81% coverage is limited by the specialized 20-30% of vocabulary")
    print("-> A folio selection matters for that specialized fraction")
else:
    print("-> B paragraphs use a MIX of universal and specialized vocabulary")
    print("-> Folio selection matters significantly")
