"""
27_a_para_to_b_para.py

Hypothesis: B folios contain mini-programs (paragraphs).
A single A paragraph might cover a single B paragraph well.

Test:
1. Break B folios into paragraphs (gallows-initial blocks)
2. Compute PP vocabulary for each B paragraph
3. Test A paragraph -> B paragraph coverage
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("A PARAGRAPH -> B PARAGRAPH COVERAGE TEST")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    return word and word[0] in GALLOWS

# =============================================================
# STEP 1: Build B paragraphs
# =============================================================
print("\nSTEP 1: Building B paragraphs...")

b_by_folio_line = defaultdict(list)
for t in tx.currier_b():
    if t.word and '*' not in t.word:
        b_by_folio_line[(t.folio, t.line)].append(t)

b_paragraphs = []
current_para = {'tokens': [], 'folio': None}
current_folio = None

for (folio, line) in sorted(b_by_folio_line.keys()):
    tokens = b_by_folio_line[(folio, line)]

    # New paragraph on gallows-initial or new folio
    if tokens and (starts_with_gallows(tokens[0].word) or folio != current_folio):
        if current_para['tokens']:
            b_paragraphs.append(current_para)
        current_para = {'tokens': [], 'folio': folio}
        current_folio = folio

    current_para['tokens'].extend(tokens)

if current_para['tokens']:
    b_paragraphs.append(current_para)

print(f"B paragraphs: {len(b_paragraphs)}")
print(f"B folios: {len(set(p['folio'] for p in b_paragraphs))}")
print(f"Mean paragraphs per folio: {len(b_paragraphs) / len(set(p['folio'] for p in b_paragraphs)):.1f}")

# Extract PP for each B paragraph
b_para_pp = []
for i, para in enumerate(b_paragraphs):
    pp_set = set()
    for t in para['tokens']:
        try:
            m = morph.extract(t.word)
            if m.middle and m.middle in pp_middles:
                pp_set.add(m.middle)
        except:
            pass
    b_para_pp.append({
        'idx': i,
        'folio': para['folio'],
        'n_tokens': len(para['tokens']),
        'pp_middles': pp_set
    })

# Stats on B paragraph sizes
pp_counts = [len(p['pp_middles']) for p in b_para_pp]
print(f"\nB paragraph PP vocabulary sizes:")
print(f"  Mean: {sum(pp_counts)/len(pp_counts):.1f} PP MIDDLEs")
print(f"  Min: {min(pp_counts)}")
print(f"  Max: {max(pp_counts)}")

# =============================================================
# STEP 2: Build A paragraphs
# =============================================================
print("\n" + "="*70)
print("STEP 2: Building A paragraphs...")

a_by_folio_line = defaultdict(list)
for t in tx.currier_a():
    if t.word and '*' not in t.word:
        a_by_folio_line[(t.folio, t.line)].append(t)

a_paragraphs = []
current_para = {'tokens': [], 'folio': None}
current_folio = None

for (folio, line) in sorted(a_by_folio_line.keys()):
    tokens = a_by_folio_line[(folio, line)]

    if tokens and (starts_with_gallows(tokens[0].word) or folio != current_folio):
        if current_para['tokens']:
            a_paragraphs.append(current_para)
        current_para = {'tokens': [], 'folio': folio}
        current_folio = folio

    current_para['tokens'].extend(tokens)

if current_para['tokens']:
    a_paragraphs.append(current_para)

# Extract PP for each A paragraph
a_para_pp = []
for i, para in enumerate(a_paragraphs):
    pp_set = set()
    for t in para['tokens']:
        try:
            m = morph.extract(t.word)
            if m.middle and m.middle in pp_middles:
                pp_set.add(m.middle)
        except:
            pass
    a_para_pp.append({
        'idx': i,
        'folio': para['folio'],
        'n_tokens': len(para['tokens']),
        'pp_middles': pp_set
    })

print(f"A paragraphs: {len(a_paragraphs)}")

# =============================================================
# STEP 3: A paragraph -> B paragraph coverage
# =============================================================
print("\n" + "="*70)
print("STEP 3: A paragraph -> B paragraph coverage")
print("="*70)

def coverage(a_pp, b_pp):
    """What fraction of B paragraph PP is covered by A paragraph?"""
    if not b_pp:
        return 0
    return len(a_pp & b_pp) / len(b_pp)

# For each A paragraph, find best matching B paragraph
a_best_matches = []

for a in a_para_pp:
    if not a['pp_middles']:
        continue

    best_b_idx = -1
    best_cov = 0

    for b in b_para_pp:
        if not b['pp_middles']:
            continue
        cov = coverage(a['pp_middles'], b['pp_middles'])
        if cov > best_cov:
            best_cov = cov
            best_b_idx = b['idx']

    a_best_matches.append({
        'a_idx': a['idx'],
        'a_folio': a['folio'],
        'a_pp_count': len(a['pp_middles']),
        'best_b_idx': best_b_idx,
        'best_b_folio': b_para_pp[best_b_idx]['folio'] if best_b_idx >= 0 else None,
        'best_coverage': best_cov
    })

# Summary
coverages = [m['best_coverage'] for m in a_best_matches]
print(f"\nA paragraph -> best matching B paragraph:")
print(f"  Mean coverage: {sum(coverages)/len(coverages):.1%}")
print(f"  Max coverage: {max(coverages):.1%}")
print(f"  Min coverage: {min(coverages):.1%}")

# Distribution
print(f"\nCoverage distribution:")
bins = [(0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0), (1.0, 1.01)]
for low, high in bins:
    count = sum(1 for c in coverages if low <= c < high)
    pct = 100 * count / len(coverages)
    print(f"  {low:.0%}-{high:.0%}: {count} ({pct:.1f}%)")

# Top matches
print(f"\nTop A->B paragraph matches:")
sorted_matches = sorted(a_best_matches, key=lambda x: -x['best_coverage'])
for m in sorted_matches[:15]:
    print(f"  A_{m['a_idx']} ({m['a_folio']}) -> B_{m['best_b_idx']} ({m['best_b_folio']}): {m['best_coverage']:.1%}")

# =============================================================
# STEP 4: How many A paragraphs achieve >80% coverage of some B paragraph?
# =============================================================
print("\n" + "="*70)
print("STEP 4: High-coverage matches")
print("="*70)

high_cov = [m for m in a_best_matches if m['best_coverage'] >= 0.8]
print(f"\nA paragraphs with >=80% coverage of some B paragraph: {len(high_cov)}/{len(a_best_matches)}")

if high_cov:
    print(f"\nThese high-coverage matches:")
    for m in high_cov[:20]:
        b_para = b_para_pp[m['best_b_idx']]
        print(f"  A_{m['a_idx']} ({m['a_folio']}, {m['a_pp_count']} PP) -> B_{m['best_b_idx']} ({m['best_b_folio']}, {len(b_para['pp_middles'])} PP): {m['best_coverage']:.1%}")

# =============================================================
# STEP 5: Check if this is better than random
# =============================================================
print("\n" + "="*70)
print("STEP 5: Null model comparison")
print("="*70)

import random

# For each A paragraph, what coverage would we expect from random B paragraphs?
null_coverages = []
for a in a_para_pp[:100]:  # Sample for speed
    if not a['pp_middles']:
        continue

    # Random B paragraphs
    sample_covs = []
    for _ in range(100):
        rand_b = random.choice(b_para_pp)
        if rand_b['pp_middles']:
            sample_covs.append(coverage(a['pp_middles'], rand_b['pp_middles']))

    if sample_covs:
        null_coverages.append(sum(sample_covs) / len(sample_covs))

mean_null = sum(null_coverages) / len(null_coverages) if null_coverages else 0
mean_actual = sum(coverages) / len(coverages)

print(f"\nActual best-match coverage: {mean_actual:.1%}")
print(f"Random match coverage: {mean_null:.1%}")
print(f"Lift: {mean_actual / mean_null:.2f}x" if mean_null > 0 else "N/A")

# =============================================================
# STEP 6: Mutual best matches (A->B and B->A agree)
# =============================================================
print("\n" + "="*70)
print("STEP 6: Mutual best matches")
print("="*70)

# For each B paragraph, find best A
b_best_a = {}
for b in b_para_pp:
    if not b['pp_middles']:
        continue

    best_a_idx = -1
    best_cov = 0

    for a in a_para_pp:
        if not a['pp_middles']:
            continue
        cov = coverage(a['pp_middles'], b['pp_middles'])
        if cov > best_cov:
            best_cov = cov
            best_a_idx = a['idx']

    b_best_a[b['idx']] = best_a_idx

# Find mutual matches
mutual_matches = []
for m in a_best_matches:
    a_idx = m['a_idx']
    b_idx = m['best_b_idx']

    if b_idx >= 0 and b_best_a.get(b_idx) == a_idx:
        mutual_matches.append(m)

print(f"\nMutual best matches (A->B and B->A agree): {len(mutual_matches)}")

if mutual_matches:
    print(f"\nMutual matches with highest coverage:")
    for m in sorted(mutual_matches, key=lambda x: -x['best_coverage'])[:10]:
        print(f"  A_{m['a_idx']} ({m['a_folio']}) <-> B_{m['best_b_idx']} ({m['best_b_folio']}): {m['best_coverage']:.1%}")

# =============================================================
# SUMMARY
# =============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
A PARAGRAPH -> B PARAGRAPH COVERAGE:

B Structure:
  B paragraphs: {len(b_paragraphs)}
  Mean PP per B paragraph: {sum(pp_counts)/len(pp_counts):.1f} MIDDLEs

Coverage Results:
  Mean best-match coverage: {mean_actual:.1%}
  Max coverage: {max(coverages):.1%}
  >=80% coverage: {len(high_cov)} A paragraphs ({100*len(high_cov)/len(a_best_matches):.1f}%)

  vs Random: {mean_actual/mean_null:.2f}x lift

Mutual Matches:
  A->B and B->A agree: {len(mutual_matches)} pairs
""")

if mean_actual > 0.5:
    print("FINDING: A paragraphs cover B paragraphs well (>50%).")
    print("A paragraph -> B paragraph pairing is viable.")
elif mean_actual > 0.3:
    print("FINDING: A paragraphs cover B paragraphs moderately (30-50%).")
    print("Partial A->B paragraph correspondence exists.")
else:
    print("FINDING: A paragraphs still only partially cover B paragraphs.")
    print("Even at paragraph level, coverage is limited.")
