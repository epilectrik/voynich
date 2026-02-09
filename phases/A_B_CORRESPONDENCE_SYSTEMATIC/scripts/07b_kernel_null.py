"""
07b_kernel_null.py

Verify kernel matching correlation with null model.
Like lane balance, kernel matching correlation might be artifact of best-match.
"""

import sys
import json
import random
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("KERNEL MATCHING - NULL MODEL VERIFICATION")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    return word and word[0] in GALLOWS

def build_paragraphs(tokens_iter):
    by_folio_line = defaultdict(list)
    for t in tokens_iter:
        if t.word and '*' not in t.word:
            by_folio_line[(t.folio, t.line)].append(t)

    paragraphs = []
    current_para = {'tokens': [], 'folio': None}
    current_folio = None

    for (folio, line) in sorted(by_folio_line.keys()):
        tokens = by_folio_line[(folio, line)]
        if tokens and (starts_with_gallows(tokens[0].word) or folio != current_folio):
            if current_para['tokens']:
                paragraphs.append(current_para)
            current_para = {'tokens': [], 'folio': folio}
            current_folio = folio
        current_para['tokens'].extend(tokens)

    if current_para['tokens']:
        paragraphs.append(current_para)

    return paragraphs

def compute_kernel(tokens):
    k, h, e, n = 0, 0, 0, 0
    for t in tokens:
        word = t.word if hasattr(t, 'word') else t['word']
        try:
            m = morph.extract(word)
            if m.middle:
                n += 1
                if 'k' in m.middle: k += 1
                if 'h' in m.middle: h += 1
                if 'e' in m.middle: e += 1
        except:
            pass
    return (k/n if n else 0, h/n if n else 0, e/n if n else 0)

def get_pp_middles(para):
    pp = set()
    for t in para['tokens']:
        try:
            m = morph.extract(t.word)
            if m.middle and m.middle in pp_middles:
                pp.add(m.middle)
        except:
            pass
    return pp

def kernel_distance(k1, k2):
    return ((k1[0]-k2[0])**2 + (k1[1]-k2[1])**2 + (k1[2]-k2[2])**2) ** 0.5

# Build paragraphs
a_paras = build_paragraphs(tx.currier_a())
b_paras = build_paragraphs(tx.currier_b())

# Compute kernels
a_kernels = [compute_kernel(p['tokens']) for p in a_paras]
b_kernels = [compute_kernel(p['tokens']) for p in b_paras]

print(f"A paragraphs: {len(a_paras)}")
print(f"B paragraphs: {len(b_paras)}")

# =============================================================
# KEY TEST: Vocabulary overlap with kernel-matched B
# =============================================================
print("\n" + "="*70)
print("VOCABULARY OVERLAP TEST")
print("="*70)

kernel_match_overlaps = []
random_match_overlaps = []

for i, a_para in enumerate(a_paras):
    a_pp = get_pp_middles(a_para)
    if not a_pp:
        continue

    a_kernel = a_kernels[i]

    # Best kernel match
    best_b_idx = min(range(len(b_paras)), key=lambda j: kernel_distance(a_kernel, b_kernels[j]))
    best_b_pp = get_pp_middles(b_paras[best_b_idx])
    if best_b_pp:
        overlap = len(a_pp & best_b_pp) / len(best_b_pp)
        kernel_match_overlaps.append(overlap)

    # Random B
    rand_b_idx = random.randint(0, len(b_paras) - 1)
    rand_b_pp = get_pp_middles(b_paras[rand_b_idx])
    if rand_b_pp:
        overlap = len(a_pp & rand_b_pp) / len(rand_b_pp)
        random_match_overlaps.append(overlap)

kernel_mean = sum(kernel_match_overlaps)/len(kernel_match_overlaps)
random_mean = sum(random_match_overlaps)/len(random_match_overlaps)
lift = kernel_mean / random_mean

print(f"\nPP vocabulary overlap:")
print(f"  Kernel-matched B: {kernel_mean:.1%}")
print(f"  Random B: {random_mean:.1%}")
print(f"  Lift: {lift:.2f}x")

# =============================================================
# COMPARE TO BEST VOCABULARY MATCH
# =============================================================
print("\n" + "="*70)
print("COMPARE: KERNEL vs VOCABULARY MATCHING")
print("="*70)

vocab_match_overlaps = []

for i, a_para in enumerate(a_paras):
    a_pp = get_pp_middles(a_para)
    if not a_pp:
        continue

    # Best vocabulary match
    best_overlap = 0
    for j, b_para in enumerate(b_paras):
        b_pp = get_pp_middles(b_para)
        if b_pp:
            overlap = len(a_pp & b_pp) / len(b_pp)
            if overlap > best_overlap:
                best_overlap = overlap
    vocab_match_overlaps.append(best_overlap)

vocab_mean = sum(vocab_match_overlaps)/len(vocab_match_overlaps)

print(f"\nBest-match vocabulary overlap:")
print(f"  Kernel-matched: {kernel_mean:.1%}")
print(f"  Vocabulary-matched: {vocab_mean:.1%}")
print(f"  Ratio: {kernel_mean/vocab_mean:.2f}x")

# =============================================================
# SUMMARY
# =============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
QUESTION: Does kernel matching produce better A-B correspondence?

VOCABULARY OVERLAP:
  Kernel-matched: {kernel_mean:.1%}
  Random: {random_mean:.1%}
  Best vocabulary match: {vocab_mean:.1%}

LIFT VS RANDOM: {lift:.2f}x
""")

if lift > 1.3:
    print(f"FINDING: Kernel matching produces {lift:.2f}x better vocabulary overlap.")
    print("Kernel profile IS a meaningful predictor of A-B correspondence.")
elif lift > 1.1:
    print(f"FINDING: Kernel matching produces marginal improvement ({lift:.2f}x).")
    print("Weak signal, may not be practically useful.")
else:
    print(f"FINDING: Kernel matching produces only {lift:.2f}x vocabulary overlap.")
    print("Kernel profile is NOT a meaningful predictor - similar to random.")
