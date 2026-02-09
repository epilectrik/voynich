"""
102_gap_analysis.py

What is the 19% gap made of?

When an A folio covers 81% of a B paragraph, what's the 19% it misses?
- Is it universal vocabulary the A folio happens to lack?
- Is it specialized vocabulary from other A folios?
- Does B always need vocabulary from multiple A sources?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("GAP ANALYSIS: WHAT IS THE 19% MADE OF?")
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

# Count how many folios have each MIDDLE
middle_folio_count = defaultdict(int)
for folio, vocab in a_folio_vocab.items():
    for m in vocab:
        middle_folio_count[m] += 1

n_a_folios = len(a_folio_vocab)

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

print(f"\nA folios: {n_a_folios}")
print(f"B paragraphs (>=10 PP): {len(b_paras_large)}")

# For each B paragraph, find best A folio and analyze gap
print("\n" + "="*70)
print("ANALYZING GAPS")
print("="*70)

gap_universalities = []  # How common is the missed vocabulary?
gap_sizes = []
covered_sizes = []

for b in b_paras_large:
    b_pp = get_pp_middles(b['tokens'])
    if not b_pp:
        continue

    # Find best A folio
    best_a = None
    best_coverage = 0
    for a_folio, a_vocab in a_folio_vocab.items():
        cov = len(a_vocab & b_pp) / len(b_pp)
        if cov > best_coverage:
            best_coverage = cov
            best_a = a_folio

    if best_a is None:
        continue

    a_vocab = a_folio_vocab[best_a]
    covered = a_vocab & b_pp
    gap = b_pp - a_vocab

    gap_sizes.append(len(gap))
    covered_sizes.append(len(covered))

    # How universal is the gap vocabulary?
    if gap:
        gap_universality = sum(middle_folio_count[m] for m in gap) / (len(gap) * n_a_folios)
        gap_universalities.append(gap_universality)

print(f"\nGap statistics:")
print(f"  Mean gap size: {sum(gap_sizes)/len(gap_sizes):.1f} MIDDLEs")
print(f"  Mean covered: {sum(covered_sizes)/len(covered_sizes):.1f} MIDDLEs")
print(f"  Mean gap %: {sum(gap_sizes)/sum(gap_sizes + covered_sizes)*100:.1f}%")

print(f"\nGap vocabulary universality:")
print(f"  Mean: {sum(gap_universalities)/len(gap_universalities):.1%} of A folios have the missed vocab")

# Categorize gap vocabulary
print("\n" + "="*70)
print("GAP VOCABULARY CATEGORIZATION")
print("="*70)

all_gaps = Counter()
for b in b_paras_large:
    b_pp = get_pp_middles(b['tokens'])
    if not b_pp:
        continue

    # Find best A folio
    best_a = None
    best_coverage = 0
    for a_folio, a_vocab in a_folio_vocab.items():
        cov = len(a_vocab & b_pp) / len(b_pp)
        if cov > best_coverage:
            best_coverage = cov
            best_a = a_folio

    if best_a:
        gap = b_pp - a_folio_vocab[best_a]
        all_gaps.update(gap)

# Most commonly missed MIDDLEs
print(f"\nMost frequently missed MIDDLEs:")
for middle, count in all_gaps.most_common(15):
    universality = middle_folio_count[middle] / n_a_folios
    print(f"  {middle}: missed in {count} B paragraphs, in {middle_folio_count[middle]} A folios ({universality:.1%})")

# Categorize by universality
gap_by_category = {'universal': 0, 'common': 0, 'rare': 0, 'singleton': 0}
for middle, count in all_gaps.items():
    folio_pct = middle_folio_count[middle] / n_a_folios
    if folio_pct >= 0.8:
        gap_by_category['universal'] += count
    elif folio_pct >= 0.5:
        gap_by_category['common'] += count
    elif folio_pct > 0.01:  # More than 1 folio
        gap_by_category['rare'] += count
    else:
        gap_by_category['singleton'] += count

total_gap = sum(gap_by_category.values())
print(f"\nGap vocabulary by universality:")
print(f"  Universal (>=80% folios): {gap_by_category['universal']} ({gap_by_category['universal']/total_gap:.1%})")
print(f"  Common (50-80% folios): {gap_by_category['common']} ({gap_by_category['common']/total_gap:.1%})")
print(f"  Rare (2-50% folios): {gap_by_category['rare']} ({gap_by_category['rare']/total_gap:.1%})")
print(f"  Singleton (1 folio): {gap_by_category['singleton']} ({gap_by_category['singleton']/total_gap:.1%})")

# Key question: does ADDING a second A folio fill most gaps?
print("\n" + "="*70)
print("DOES A SECOND A FOLIO HELP?")
print("="*70)

two_folio_coverages = []
for b in b_paras_large[:100]:  # Sample
    b_pp = get_pp_middles(b['tokens'])
    if not b_pp:
        continue

    # Find best single A folio
    folio_scores = []
    for a_folio, a_vocab in a_folio_vocab.items():
        cov = len(a_vocab & b_pp) / len(b_pp)
        folio_scores.append((a_folio, cov, a_vocab))

    folio_scores.sort(key=lambda x: -x[1])
    best1 = folio_scores[0]

    # Find best SECOND folio (most complementary)
    best2_cov = best1[1]
    for a_folio, _, a_vocab in folio_scores[1:]:
        combined = best1[2] | a_vocab
        cov = len(combined & b_pp) / len(b_pp)
        if cov > best2_cov:
            best2_cov = cov
            best2 = (a_folio, cov, a_vocab)

    two_folio_coverages.append(best2_cov)

print(f"\nWith best 2 A folios combined:")
print(f"  Mean coverage: {sum(two_folio_coverages)/len(two_folio_coverages):.1%}")
print(f"  Improvement over 1 folio: {sum(two_folio_coverages)/len(two_folio_coverages) - 0.812:.1%}")
