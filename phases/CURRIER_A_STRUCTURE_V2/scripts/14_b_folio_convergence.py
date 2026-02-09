"""
14_b_folio_convergence.py

B FOLIO CONVERGENCE TEST

Question: Do WITHOUT-RI paragraphs point to DIFFERENT B folios than WITH-RI?

If WITHOUT-RI are cross-reference/index records, their PP vocabulary might:
1. Appear in MORE B folios (wider coverage)
2. Appear in DIFFERENT B folios than WITH-RI PP vocabulary
3. Show less specific convergence (linking broadly rather than specific products)
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("B FOLIO CONVERGENCE TEST")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD B FOLIO PP VOCABULARY INDEX
# =============================================================
print("\n[1/4] Building B folio PP vocabulary index...")

# Collect PP MIDDLEs per B folio
b_folio_middles = defaultdict(set)
for t in tx.currier_b():
    if t.word and '*' not in t.word:
        try:
            m = morph.extract(t.word)
            if m.middle:
                b_folio_middles[t.folio].add(m.middle)
        except:
            pass

print(f"   Total B folios: {len(b_folio_middles)}")
print(f"   Sample B folios: {list(b_folio_middles.keys())[:5]}")

# Build reverse index: MIDDLE -> which B folios contain it
middle_to_b_folios = defaultdict(set)
for folio, middles in b_folio_middles.items():
    for middle in middles:
        middle_to_b_folios[middle].add(folio)

print(f"   Unique MIDDLEs in B: {len(middle_to_b_folios)}")

# =============================================================
# STEP 2: BUILD A PARAGRAPH INVENTORY
# =============================================================
print("\n[2/4] Building A paragraph inventory...")

folio_paragraphs = defaultdict(list)
current_para_tokens = []
current_folio = None

for t in tx.currier_a():
    if not t.word or '*' in t.word:
        continue

    if t.folio != current_folio:
        if current_para_tokens:
            folio_paragraphs[current_folio].append(current_para_tokens)
        current_folio = t.folio
        current_para_tokens = []

    if t.par_initial and current_para_tokens:
        folio_paragraphs[current_folio].append(current_para_tokens)
        current_para_tokens = []

    current_para_tokens.append(t)

if current_para_tokens and current_folio:
    folio_paragraphs[current_folio].append(current_para_tokens)

def has_initial_ri(para_tokens, analyzer):
    if not para_tokens:
        return False
    folio = para_tokens[0].folio
    first_line = para_tokens[0].line
    try:
        record = analyzer.analyze_record(folio, first_line)
        if record:
            for t in record.tokens:
                if t.token_class == 'RI':
                    return True
    except:
        pass
    return False

def get_pp_middles(para_tokens, analyzer, morph):
    """Get PP MIDDLEs from a paragraph."""
    if not para_tokens:
        return set()

    folio = para_tokens[0].folio
    lines = sorted(set(t.line for t in para_tokens))
    middles = set()

    for line in lines:
        try:
            record = analyzer.analyze_record(folio, line)
            if record:
                for t in record.tokens:
                    if t.token_class == 'PP' and t.word:
                        try:
                            m = morph.extract(t.word)
                            if m.middle:
                                middles.add(m.middle)
                        except:
                            pass
        except:
            pass
    return middles

# Classify paragraphs and collect PP middles
with_ri_paras = []
without_ri_paras = []

for folio, paragraphs in folio_paragraphs.items():
    for para_tokens in paragraphs:
        if not para_tokens:
            continue

        pp_middles = get_pp_middles(para_tokens, analyzer, morph)

        entry = {
            'folio': folio,
            'pp_middles': pp_middles
        }

        if has_initial_ri(para_tokens, analyzer):
            with_ri_paras.append(entry)
        else:
            without_ri_paras.append(entry)

print(f"   WITH-RI paragraphs: {len(with_ri_paras)}")
print(f"   WITHOUT-RI paragraphs: {len(without_ri_paras)}")

# =============================================================
# STEP 3: COMPUTE B FOLIO CONVERGENCE
# =============================================================
print("\n[3/4] Computing B folio convergence...")

def compute_b_convergence(para, middle_to_b_folios):
    """Compute which B folios this paragraph's PP vocabulary appears in."""
    pp_middles = para['pp_middles']
    if not pp_middles:
        return set()

    b_folios = set()
    for middle in pp_middles:
        b_folios.update(middle_to_b_folios.get(middle, set()))

    return b_folios

# Compute for all paragraphs
with_ri_convergences = [compute_b_convergence(p, middle_to_b_folios) for p in with_ri_paras]
without_ri_convergences = [compute_b_convergence(p, middle_to_b_folios) for p in without_ri_paras]

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

# Average number of B folios
avg_with = avg([len(c) for c in with_ri_convergences])
avg_without = avg([len(c) for c in without_ri_convergences])

print(f"\nAVERAGE B FOLIO CONVERGENCE:")
print(f"   WITH-RI paragraphs: {avg_with:.1f} B folios")
print(f"   WITHOUT-RI paragraphs: {avg_without:.1f} B folios")
print(f"   Ratio: {avg_without/avg_with:.2f}x")

# =============================================================
# STEP 4: ANALYZE SPECIFIC B FOLIOS
# =============================================================
print("\n[4/4] Analyzing specific B folios...")

# Count how many paragraphs converge to each B folio
b_folio_with_ri_count = Counter()
b_folio_without_ri_count = Counter()

for conv in with_ri_convergences:
    b_folio_with_ri_count.update(conv)

for conv in without_ri_convergences:
    b_folio_without_ri_count.update(conv)

# Total paragraphs pointing to each B folio type
print(f"\nB FOLIO COVERAGE:")
print(f"   B folios reached by WITH-RI: {len(b_folio_with_ri_count)}")
print(f"   B folios reached by WITHOUT-RI: {len(b_folio_without_ri_count)}")

# Overlap
shared_b = set(b_folio_with_ri_count.keys()) & set(b_folio_without_ri_count.keys())
only_with_ri_b = set(b_folio_with_ri_count.keys()) - set(b_folio_without_ri_count.keys())
only_without_ri_b = set(b_folio_without_ri_count.keys()) - set(b_folio_with_ri_count.keys())

print(f"   Shared B folios: {len(shared_b)}")
print(f"   B folios ONLY from WITH-RI: {len(only_with_ri_b)}")
print(f"   B folios ONLY from WITHOUT-RI: {len(only_without_ri_b)}")

# Jaccard of B folio sets
all_b = set(b_folio_with_ri_count.keys()) | set(b_folio_without_ri_count.keys())
jaccard_b = len(shared_b) / len(all_b) if all_b else 0
print(f"   Jaccard similarity of B folio targets: {jaccard_b:.3f}")

# Top B folios for each type
print(f"\nTop B folios targeted by WITH-RI paragraphs:")
for folio, count in b_folio_with_ri_count.most_common(10):
    pct = 100 * count / len(with_ri_paras)
    print(f"   {folio}: {count} ({pct:.1f}%)")

print(f"\nTop B folios targeted by WITHOUT-RI paragraphs:")
for folio, count in b_folio_without_ri_count.most_common(10):
    pct = 100 * count / len(without_ri_paras)
    print(f"   {folio}: {count} ({pct:.1f}%)")

# =============================================================
# STEP 5: SPECIFICITY ANALYSIS
# =============================================================
print("\n" + "="*70)
print("SPECIFICITY ANALYSIS")
print("="*70)

# Do WITHOUT-RI paragraphs converge to MORE B folios (less specific)?
# Or FEWER (more specific)?

# Distribution of convergence counts
with_ri_counts = [len(c) for c in with_ri_convergences if c]
without_ri_counts = [len(c) for c in without_ri_convergences if c]

print(f"\nConvergence distribution:")
print(f"   WITH-RI median: {sorted(with_ri_counts)[len(with_ri_counts)//2] if with_ri_counts else 0}")
print(f"   WITHOUT-RI median: {sorted(without_ri_counts)[len(without_ri_counts)//2] if without_ri_counts else 0}")
print(f"   WITH-RI max: {max(with_ri_counts) if with_ri_counts else 0}")
print(f"   WITHOUT-RI max: {max(without_ri_counts) if without_ri_counts else 0}")

# Paragraphs with no B convergence
with_no_conv = sum(1 for c in with_ri_convergences if not c)
without_no_conv = sum(1 for c in without_ri_convergences if not c)

print(f"\nParagraphs with NO B folio convergence:")
print(f"   WITH-RI: {with_no_conv}/{len(with_ri_paras)} ({100*with_no_conv/len(with_ri_paras):.1f}%)")
print(f"   WITHOUT-RI: {without_no_conv}/{len(without_ri_paras)} ({100*without_no_conv/len(without_ri_paras):.1f}%)")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("\nQuestion: Do WITHOUT-RI paragraphs target DIFFERENT B folios?")
print("-" * 60)

# Test 1: Coverage breadth
if avg_without > avg_with * 1.1:
    print(f"+ WITHOUT-RI has BROADER coverage ({avg_without:.1f} vs {avg_with:.1f} B folios)")
    broader = True
elif avg_with > avg_without * 1.1:
    print(f"- WITH-RI has BROADER coverage ({avg_with:.1f} vs {avg_without:.1f} B folios)")
    broader = False
else:
    print(f"= Similar coverage breadth ({avg_without:.1f} vs {avg_with:.1f})")
    broader = None

# Test 2: Target overlap
if jaccard_b < 0.7:
    print(f"+ B folio targets are DISTINCT (Jaccard={jaccard_b:.3f})")
    distinct = True
else:
    print(f"- B folio targets OVERLAP significantly (Jaccard={jaccard_b:.3f})")
    distinct = False

# Test 3: Exclusive targets
if only_without_ri_b:
    print(f"+ {len(only_without_ri_b)} B folios ONLY reachable via WITHOUT-RI")
else:
    print(f"- No B folios exclusively from WITHOUT-RI")

print("\n" + "-"*60)
print("VERDICT:")

if broader or distinct:
    print("""
WITHOUT-RI paragraphs have DIFFERENT B convergence patterns:
- This supports the hypothesis that they serve a cross-referencing function
- They may be "index" records pointing to a wider range of products
""")
    verdict = "DIFFERENT_CONVERGENCE"
else:
    print("""
WITHOUT-RI and WITH-RI paragraphs target SIMILAR B folios.
Both paragraph types reference the same product space.
""")
    verdict = "SIMILAR_CONVERGENCE"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'B_FOLIO_CONVERGENCE',
    'convergence': {
        'avg_b_folios_with_ri': avg_with,
        'avg_b_folios_without_ri': avg_without
    },
    'coverage': {
        'b_folios_from_with_ri': len(b_folio_with_ri_count),
        'b_folios_from_without_ri': len(b_folio_without_ri_count),
        'shared_b_folios': len(shared_b),
        'jaccard_b': jaccard_b
    },
    'exclusive_targets': {
        'only_with_ri': list(only_with_ri_b)[:20],
        'only_without_ri': list(only_without_ri_b)[:20]
    },
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'b_folio_convergence.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
