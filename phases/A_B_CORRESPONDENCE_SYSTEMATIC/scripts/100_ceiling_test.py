"""
100_ceiling_test.py

What is the THEORETICAL CEILING for A->B coverage?

If we use ALL of Currier A vocabulary, what fraction of B paragraph
vocabulary can we cover? This tells us:
- If ceiling is ~100%: A provides B vocabulary
- If ceiling is ~85%: 15% of B vocabulary is B-only
- If ceiling is ~80%: Our 81% folio result is already at ceiling
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("THEORETICAL CEILING TEST: ALL A -> B PARAGRAPH")
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

# Build ALL A vocabulary
print("\nBuilding A vocabulary (all tokens)...")
all_a_pp = set()
for t in tx.currier_a():
    if t.word and '*' not in t.word:
        try:
            m = morph.extract(t.word)
            if m.middle and m.middle in pp_middles:
                all_a_pp.add(m.middle)
        except:
            pass

print(f"Total A PP MIDDLEs: {len(all_a_pp)}")

# Build B paragraphs
print("\nBuilding B paragraphs...")
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

# Filter to large B paragraphs
b_paras_large = [p for p in b_paragraphs if len(get_pp_middles(p['tokens'])) >= 10]
print(f"B paragraphs (>=10 PP): {len(b_paras_large)}")

# Test ceiling: ALL A -> each B paragraph
print("\n" + "="*70)
print("CEILING TEST: ALL A VOCABULARY -> B PARAGRAPHS")
print("="*70)

coverages = []
b_only_counts = []

for b in b_paras_large:
    b_pp = get_pp_middles(b['tokens'])
    if not b_pp:
        continue

    covered = len(all_a_pp & b_pp)
    total = len(b_pp)
    coverage = covered / total
    coverages.append(coverage)

    b_only = b_pp - all_a_pp
    b_only_counts.append(len(b_only))

mean_coverage = sum(coverages) / len(coverages)
min_coverage = min(coverages)
max_coverage = max(coverages)

print(f"\nALL A -> B paragraph coverage:")
print(f"  Mean: {mean_coverage:.1%}")
print(f"  Min:  {min_coverage:.1%}")
print(f"  Max:  {max_coverage:.1%}")

# How many B paragraphs have 100% coverage from A?
perfect = sum(1 for c in coverages if c >= 0.999)
high = sum(1 for c in coverages if c >= 0.95)
print(f"\n  100% coverage: {perfect} paragraphs ({perfect/len(coverages):.1%})")
print(f"  >=95% coverage: {high} paragraphs ({high/len(coverages):.1%})")

# What's the B-only vocabulary?
print("\n" + "="*70)
print("B-ONLY VOCABULARY ANALYSIS")
print("="*70)

all_b_pp = set()
for b in b_paras_large:
    all_b_pp.update(get_pp_middles(b['tokens']))

b_only_vocab = all_b_pp - all_a_pp
shared_vocab = all_b_pp & all_a_pp

print(f"\nVocabulary breakdown:")
print(f"  B paragraph PP vocabulary: {len(all_b_pp)}")
print(f"  Shared with A: {len(shared_vocab)} ({len(shared_vocab)/len(all_b_pp):.1%})")
print(f"  B-only: {len(b_only_vocab)} ({len(b_only_vocab)/len(all_b_pp):.1%})")

if b_only_vocab:
    print(f"\nB-only PP MIDDLEs (sample): {list(b_only_vocab)[:20]}")

# Per-paragraph B-only
print(f"\nPer-paragraph B-only MIDDLEs:")
print(f"  Mean: {sum(b_only_counts)/len(b_only_counts):.1f}")
print(f"  Max:  {max(b_only_counts)}")
print(f"  Zero B-only: {sum(1 for c in b_only_counts if c == 0)} paragraphs")

# Compare to our 81% finding
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print(f"""
THEORETICAL CEILING: {mean_coverage:.1%}
BEST A FOLIO:        81.2%
GAP FROM CEILING:    {mean_coverage - 0.812:.1%}

If ceiling is ~{mean_coverage:.0%}:
""")

if mean_coverage > 0.95:
    print("-> A vocabulary FULLY covers B (ceiling near 100%)")
    print("-> Our 81% folio result has room to improve with better matching")
    print("-> The 19% gap is from folio selection, not B-only vocabulary")
elif mean_coverage > 0.85:
    print("-> A vocabulary MOSTLY covers B (small B-only component)")
    print(f"-> ~{100-mean_coverage*100:.0f}% of B vocabulary is B-only")
    print(f"-> Our 81% is {0.812/mean_coverage:.0%} of theoretical max")
else:
    print("-> Significant B-only vocabulary exists")
    print("-> Our 81% may already be near ceiling")
    print("-> A does NOT fully provide B vocabulary")
