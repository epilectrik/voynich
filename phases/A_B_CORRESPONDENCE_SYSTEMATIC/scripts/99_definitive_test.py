"""
99_definitive_test.py

THE DEFINITIVE TEST:

1. What is the best vocabulary coverage we can achieve matching A to B?
2. Is this better than random?
3. What does this tell us about A-B relationship?

We test at multiple levels:
- A paragraph -> B paragraph
- A paragraph -> B folio
- A folio -> B folio
- A folio -> B paragraph
"""

import sys
import json
import random
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("DEFINITIVE A-B CORRESPONDENCE TEST")
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

def coverage(a_pp, b_pp):
    if not b_pp:
        return 0
    return len(a_pp & b_pp) / len(b_pp)

# =============================================================
# BUILD STRUCTURES
# =============================================================
print("\nBuilding structures...")

# A paragraphs
a_by_folio_line = defaultdict(list)
for t in tx.currier_a():
    if t.word and '*' not in t.word:
        a_by_folio_line[(t.folio, t.line)].append(t)

a_paragraphs = []
current = {'tokens': [], 'folio': None}
current_folio = None
for (folio, line) in sorted(a_by_folio_line.keys()):
    tokens = a_by_folio_line[(folio, line)]
    if tokens and (starts_with_gallows(tokens[0].word) or folio != current_folio):
        if current['tokens']:
            a_paragraphs.append(current)
        current = {'tokens': [], 'folio': folio}
        current_folio = folio
    current['tokens'].extend(tokens)
if current['tokens']:
    a_paragraphs.append(current)

# B paragraphs
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

# A folios
a_folios = defaultdict(list)
for p in a_paragraphs:
    a_folios[p['folio']].extend(p['tokens'])
a_folios = [{'folio': f, 'tokens': t} for f, t in a_folios.items()]

# B folios
b_folios = defaultdict(list)
for p in b_paragraphs:
    b_folios[p['folio']].extend(p['tokens'])
b_folios = [{'folio': f, 'tokens': t} for f, t in b_folios.items()]

# Filter B paragraphs to substantial ones (>=10 PP)
b_paras_large = [p for p in b_paragraphs if len(get_pp_middles(p['tokens'])) >= 10]

print(f"A paragraphs: {len(a_paragraphs)}")
print(f"A folios: {len(a_folios)}")
print(f"B paragraphs: {len(b_paragraphs)}")
print(f"B paragraphs (>=10 PP): {len(b_paras_large)}")
print(f"B folios: {len(b_folios)}")

# =============================================================
# TEST 1: A paragraph -> B paragraph (large)
# =============================================================
print("\n" + "="*70)
print("TEST 1: A PARAGRAPH -> B PARAGRAPH (>=10 PP)")
print("="*70)

results_1 = []
for a in a_paragraphs:
    a_pp = get_pp_middles(a['tokens'])
    if not a_pp:
        continue

    best_cov = 0
    for b in b_paras_large:
        b_pp = get_pp_middles(b['tokens'])
        cov = coverage(a_pp, b_pp)
        if cov > best_cov:
            best_cov = cov
    results_1.append(best_cov)

# Null model
null_1 = []
for _ in range(500):
    a = random.choice(a_paragraphs)
    b = random.choice(b_paras_large)
    a_pp = get_pp_middles(a['tokens'])
    b_pp = get_pp_middles(b['tokens'])
    if a_pp and b_pp:
        null_1.append(coverage(a_pp, b_pp))

mean_1 = sum(results_1)/len(results_1)
null_mean_1 = sum(null_1)/len(null_1)
print(f"Best-match coverage: {mean_1:.1%}")
print(f"Random coverage: {null_mean_1:.1%}")
print(f"Lift: {mean_1/null_mean_1:.2f}x")

# =============================================================
# TEST 2: A paragraph -> B folio
# =============================================================
print("\n" + "="*70)
print("TEST 2: A PARAGRAPH -> B FOLIO")
print("="*70)

results_2 = []
for a in a_paragraphs:
    a_pp = get_pp_middles(a['tokens'])
    if not a_pp:
        continue

    best_cov = 0
    for b in b_folios:
        b_pp = get_pp_middles(b['tokens'])
        cov = coverage(a_pp, b_pp)
        if cov > best_cov:
            best_cov = cov
    results_2.append(best_cov)

null_2 = []
for _ in range(500):
    a = random.choice(a_paragraphs)
    b = random.choice(b_folios)
    a_pp = get_pp_middles(a['tokens'])
    b_pp = get_pp_middles(b['tokens'])
    if a_pp and b_pp:
        null_2.append(coverage(a_pp, b_pp))

mean_2 = sum(results_2)/len(results_2)
null_mean_2 = sum(null_2)/len(null_2)
print(f"Best-match coverage: {mean_2:.1%}")
print(f"Random coverage: {null_mean_2:.1%}")
print(f"Lift: {mean_2/null_mean_2:.2f}x")

# =============================================================
# TEST 3: A folio -> B folio
# =============================================================
print("\n" + "="*70)
print("TEST 3: A FOLIO -> B FOLIO")
print("="*70)

results_3 = []
for a in a_folios:
    a_pp = get_pp_middles(a['tokens'])
    if not a_pp:
        continue

    best_cov = 0
    for b in b_folios:
        b_pp = get_pp_middles(b['tokens'])
        cov = coverage(a_pp, b_pp)
        if cov > best_cov:
            best_cov = cov
    results_3.append(best_cov)

null_3 = []
for _ in range(500):
    a = random.choice(a_folios)
    b = random.choice(b_folios)
    a_pp = get_pp_middles(a['tokens'])
    b_pp = get_pp_middles(b['tokens'])
    if a_pp and b_pp:
        null_3.append(coverage(a_pp, b_pp))

mean_3 = sum(results_3)/len(results_3)
null_mean_3 = sum(null_3)/len(null_3)
print(f"Best-match coverage: {mean_3:.1%}")
print(f"Random coverage: {null_mean_3:.1%}")
print(f"Lift: {mean_3/null_mean_3:.2f}x")

# =============================================================
# TEST 4: A folio -> B paragraph (large)
# =============================================================
print("\n" + "="*70)
print("TEST 4: A FOLIO -> B PARAGRAPH (>=10 PP)")
print("="*70)

results_4 = []
for a in a_folios:
    a_pp = get_pp_middles(a['tokens'])
    if not a_pp:
        continue

    best_cov = 0
    for b in b_paras_large:
        b_pp = get_pp_middles(b['tokens'])
        cov = coverage(a_pp, b_pp)
        if cov > best_cov:
            best_cov = cov
    results_4.append(best_cov)

null_4 = []
for _ in range(500):
    a = random.choice(a_folios)
    b = random.choice(b_paras_large)
    a_pp = get_pp_middles(a['tokens'])
    b_pp = get_pp_middles(b['tokens'])
    if a_pp and b_pp:
        null_4.append(coverage(a_pp, b_pp))

mean_4 = sum(results_4)/len(results_4)
null_mean_4 = sum(null_4)/len(null_4)
print(f"Best-match coverage: {mean_4:.1%}")
print(f"Random coverage: {null_mean_4:.1%}")
print(f"Lift: {mean_4/null_mean_4:.2f}x")

# =============================================================
# TEST 5: Multiple A paragraphs -> B paragraph
# =============================================================
print("\n" + "="*70)
print("TEST 5: 2-5 A PARAGRAPHS -> B PARAGRAPH")
print("="*70)

for n_a in [2, 3, 5]:
    results_n = []
    for b in b_paras_large[:100]:  # Sample for speed
        b_pp = get_pp_middles(b['tokens'])
        if not b_pp:
            continue

        # Find best N A paragraphs
        a_scores = []
        for a in a_paragraphs:
            a_pp = get_pp_middles(a['tokens'])
            if a_pp:
                cov = coverage(a_pp, b_pp)
                a_scores.append((a, cov))

        a_scores.sort(key=lambda x: -x[1])
        top_n = a_scores[:n_a]

        # Combined coverage
        combined_pp = set()
        for a, _ in top_n:
            combined_pp.update(get_pp_middles(a['tokens']))

        combined_cov = coverage(combined_pp, b_pp)
        results_n.append(combined_cov)

    print(f"{n_a} A paragraphs: {sum(results_n)/len(results_n):.1%} coverage")

# =============================================================
# SUMMARY
# =============================================================
print("\n" + "="*70)
print("DEFINITIVE ANSWER")
print("="*70)

print(f"""
A-B VOCABULARY COVERAGE SUMMARY:

| A Unit | B Unit | Best-Match | Random | Lift |
|--------|--------|------------|--------|------|
| Paragraph | Paragraph (>=10) | {mean_1:.1%} | {null_mean_1:.1%} | {mean_1/null_mean_1:.2f}x |
| Paragraph | Folio | {mean_2:.1%} | {null_mean_2:.1%} | {mean_2/null_mean_2:.2f}x |
| Folio | Folio | {mean_3:.1%} | {null_mean_3:.1%} | {mean_3/null_mean_3:.2f}x |
| Folio | Paragraph (>=10) | {mean_4:.1%} | {null_mean_4:.1%} | {mean_4/null_mean_4:.2f}x |

INTERPRETATION:
""")

best_lift = max(mean_1/null_mean_1, mean_2/null_mean_2, mean_3/null_mean_3, mean_4/null_mean_4)
best_cov = max(mean_1, mean_2, mean_3, mean_4)

if best_lift > 2.0:
    print(f"STRONG SIGNAL: Best lift is {best_lift:.2f}x over random.")
    print("A and B have meaningful structural correspondence.")
elif best_lift > 1.5:
    print(f"MODERATE SIGNAL: Best lift is {best_lift:.2f}x over random.")
    print("A and B have weak but real correspondence.")
else:
    print(f"WEAK SIGNAL: Best lift is only {best_lift:.2f}x over random.")
    print("A and B have minimal structural correspondence.")

print(f"\nBest vocabulary coverage achieved: {best_cov:.1%}")
if best_cov > 0.8:
    print("-> A CAN provide sufficient vocabulary for B programs")
elif best_cov > 0.5:
    print("-> A provides PARTIAL vocabulary for B programs (~50%)")
else:
    print("-> A provides INSUFFICIENT vocabulary for B programs")

# Save results
out_path = Path(__file__).parent.parent / 'results' / 'definitive_test.json'
with open(out_path, 'w') as f:
    json.dump({
        'para_to_para': {'mean': mean_1, 'null': null_mean_1, 'lift': mean_1/null_mean_1},
        'para_to_folio': {'mean': mean_2, 'null': null_mean_2, 'lift': mean_2/null_mean_2},
        'folio_to_folio': {'mean': mean_3, 'null': null_mean_3, 'lift': mean_3/null_mean_3},
        'folio_to_para': {'mean': mean_4, 'null': null_mean_4, 'lift': mean_4/null_mean_4},
    }, f, indent=2)

print(f"\nSaved to {out_path.name}")
