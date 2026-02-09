"""
103_singleton_analysis.py

Singleton vocabulary analysis:
- Which A folios have singleton MIDDLEs (vocabulary found nowhere else in A)?
- How many B paragraphs use that singleton vocabulary?
- Is there a "special" A folio that many B programs depend on?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("SINGLETON VOCABULARY ANALYSIS")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    return word and word[0] in GALLOWS

def get_pp_middles(tokens):
    pp = set()
    for t in tokens:
        word = t.word if hasattr(t, 'word') else t['word']
        try:
            m = morph.extract(word)
            if m.middle and m.middle in pp_middles:
                pp.add(m.middle)
        except:
            pass
    return pp

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

# Find singleton MIDDLEs (only in 1 A folio)
middle_to_folio = defaultdict(set)
for folio, vocab in a_folio_vocab.items():
    for m in vocab:
        middle_to_folio[m].add(folio)

singletons = {m: list(folios)[0] for m, folios in middle_to_folio.items() if len(folios) == 1}
print(f"\nSingleton MIDDLEs: {len(singletons)} (only appear in 1 A folio)")

# Which A folios have singletons?
folio_singletons = defaultdict(list)
for middle, folio in singletons.items():
    folio_singletons[folio].append(middle)

print(f"A folios with singletons: {len(folio_singletons)}")

# Top A folios by singleton count
folio_singleton_counts = [(f, len(m)) for f, m in folio_singletons.items()]
folio_singleton_counts.sort(key=lambda x: -x[1])

print(f"\nTop A folios by singleton vocabulary count:")
for f, count in folio_singleton_counts[:15]:
    print(f"  {f}: {count} singletons")

# Build B paragraphs
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

b_paras_large = [p for p in b_paragraphs if len(get_pp_middles(p['tokens'])) >= 10]

print(f"\nB paragraphs (>=10 PP): {len(b_paras_large)}")

# For each singleton MIDDLE, count how many B paragraphs use it
print("\n" + "="*70)
print("SINGLETON USAGE IN B")
print("="*70)

singleton_b_usage = Counter()
for middle in singletons:
    for b in b_paras_large:
        b_pp = get_pp_middles(b['tokens'])
        if middle in b_pp:
            singleton_b_usage[middle] += 1

# Most used singletons
print(f"\nMost frequently used singleton MIDDLEs in B:")
for middle, count in singleton_b_usage.most_common(20):
    source_folio = singletons[middle]
    print(f"  {middle}: used in {count} B paragraphs, only in A folio {source_folio}")

# How many B paragraphs use ANY singleton?
b_using_singletons = 0
for b in b_paras_large:
    b_pp = get_pp_middles(b['tokens'])
    if b_pp & set(singletons.keys()):
        b_using_singletons += 1

print(f"\nB paragraphs using singleton vocabulary: {b_using_singletons} ({b_using_singletons/len(b_paras_large):.1%})")

# Per A folio: how many B paragraphs need its singletons?
print("\n" + "="*70)
print("A FOLIO DEPENDENCIES (via singletons)")
print("="*70)

folio_b_dependents = defaultdict(set)
for b_idx, b in enumerate(b_paras_large):
    b_pp = get_pp_middles(b['tokens'])
    for middle in b_pp:
        if middle in singletons:
            source_folio = singletons[middle]
            folio_b_dependents[source_folio].add(b_idx)

# Sort by number of B dependents
folio_deps = [(f, len(deps)) for f, deps in folio_b_dependents.items()]
folio_deps.sort(key=lambda x: -x[1])

print(f"\nA folios by B paragraph dependencies (via singleton vocabulary):")
for f, count in folio_deps[:20]:
    n_singletons = len(folio_singletons[f])
    print(f"  {f}: {count} B paragraphs depend on it ({n_singletons} singletons)")

# Is there a dominant A folio?
if folio_deps:
    top_folio, top_count = folio_deps[0]
    print(f"\n" + "="*70)
    print(f"ANALYSIS OF TOP SINGLETON SOURCE: {top_folio}")
    print("="*70)

    its_singletons = folio_singletons[top_folio]
    print(f"\nSingleton MIDDLEs in {top_folio}: {len(its_singletons)}")
    print(f"  {its_singletons[:20]}{'...' if len(its_singletons) > 20 else ''}")

    # Which B paragraphs depend on it?
    dependent_b = list(folio_b_dependents[top_folio])
    print(f"\nB paragraphs depending on {top_folio}: {len(dependent_b)}")

    # What B folios are these?
    dependent_b_folios = set(b_paras_large[i]['folio'] for i in dependent_b)
    print(f"Spanning B folios: {len(dependent_b_folios)}")

    # Is the dependency strong or weak?
    # For each dependent B, what fraction of its vocab is singletons from this folio?
    singleton_fractions = []
    for b_idx in dependent_b:
        b_pp = get_pp_middles(b_paras_large[b_idx]['tokens'])
        singleton_overlap = len(b_pp & set(its_singletons))
        singleton_fractions.append(singleton_overlap / len(b_pp))

    print(f"\nDependency strength (fraction of B vocab that's singleton from this folio):")
    print(f"  Mean: {sum(singleton_fractions)/len(singleton_fractions):.1%}")
    print(f"  Max:  {max(singleton_fractions):.1%}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

total_singleton_uses = sum(singleton_b_usage.values())
print(f"""
SINGLETON VOCABULARY:
- {len(singletons)} singleton MIDDLEs (34% of PP vocabulary)
- Found in {len(folio_singletons)} different A folios
- Used {total_singleton_uses} times across B paragraphs

TOP SINGLETON SOURCES:
""")
for f, count in folio_deps[:5]:
    pct = count / len(b_paras_large) * 100
    print(f"  {f}: {count} B paragraphs ({pct:.1f}%)")
