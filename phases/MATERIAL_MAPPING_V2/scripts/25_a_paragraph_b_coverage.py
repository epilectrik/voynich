"""
25_a_paragraph_b_coverage.py

Direct question: Does a single A paragraph contain enough PP vocabulary
to make a B program usable?

From expert:
- Classified B vocabulary = 479 token types in 49-class grammar
- All classified B = PP (100% shared with A)
- 88 classified MIDDLEs

Test: For each A paragraph, what % of classified B vocabulary does it cover?
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("A PARAGRAPH -> B PROGRAM USABILITY TEST")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

# =============================================================
# STEP 1: Get classified B vocabulary (PP MIDDLEs only)
# =============================================================
print("\nSTEP 1: Building classified B vocabulary...")

# B PP MIDDLEs (the operational vocabulary)
b_pp_middles = set()
b_pp_by_folio = defaultdict(set)

for t in tx.currier_b():
    if not t.word or '*' in t.word:
        continue
    try:
        m = morph.extract(t.word)
        if m.middle and m.middle in pp_middles:
            b_pp_middles.add(m.middle)
            b_pp_by_folio[t.folio].add(m.middle)
    except:
        pass

print(f"Classified B PP MIDDLEs: {len(b_pp_middles)}")
print(f"B folios: {len(b_pp_by_folio)}")

# =============================================================
# STEP 2: Build A paragraphs with PP vocabulary
# =============================================================
print("\n" + "="*70)
print("STEP 2: Building A paragraph PP vocabulary...")

# Load paragraph structure
para_results = Path(__file__).parent.parent.parent / "PARAGRAPH_INTERNAL_PROFILING" / "results"
para_file = para_results / "a_paragraph_tokens.json"

if para_file.exists():
    with open(para_file) as f:
        para_tokens = json.load(f)
    print(f"Loaded {len(para_tokens)} A paragraphs from cache")
else:
    print("Building paragraphs from scratch...")
    # Build paragraphs manually
    GALLOWS = {'k', 't', 'p', 'f'}

    def starts_with_gallows(word):
        return word and word[0] in GALLOWS

    a_by_folio_line = defaultdict(list)
    for t in tx.currier_a():
        if t.word and '*' not in t.word:
            a_by_folio_line[(t.folio, t.line)].append(t)

    para_tokens = {}
    para_idx = 0
    current_para = []
    current_folio = None

    for (folio, line) in sorted(a_by_folio_line.keys()):
        tokens = a_by_folio_line[(folio, line)]

        # New paragraph on gallows-initial or new folio
        if tokens and (starts_with_gallows(tokens[0].word) or folio != current_folio):
            if current_para:
                para_tokens[f"A_{para_idx}"] = [{'word': t.word, 'folio': t.folio} for t in current_para]
                para_idx += 1
            current_para = []
            current_folio = folio

        current_para.extend(tokens)

    if current_para:
        para_tokens[f"A_{para_idx}"] = [{'word': t.word, 'folio': t.folio} for t in current_para]

    print(f"Built {len(para_tokens)} A paragraphs")

# Extract PP MIDDLEs for each paragraph
para_pp = {}
for para_id, tokens in para_tokens.items():
    pp_set = set()
    for t in tokens:
        word = t.get('word', '') if isinstance(t, dict) else t.word
        if not word or '*' in word:
            continue
        try:
            m = morph.extract(word)
            if m.middle and m.middle in pp_middles:
                pp_set.add(m.middle)
        except:
            pass
    para_pp[para_id] = pp_set

print(f"Paragraphs with PP vocabulary: {sum(1 for p in para_pp.values() if p)}")

# =============================================================
# STEP 3: Compute coverage of classified B vocabulary
# =============================================================
print("\n" + "="*70)
print("STEP 3: A paragraph coverage of classified B vocabulary")
print("="*70)

def b_coverage(a_pp_set):
    """What % of classified B PP MIDDLEs does this A paragraph cover?"""
    if not b_pp_middles:
        return 0
    return len(a_pp_set & b_pp_middles) / len(b_pp_middles)

para_coverages = {}
for para_id, pp_set in para_pp.items():
    para_coverages[para_id] = {
        'pp_count': len(pp_set),
        'b_coverage': b_coverage(pp_set),
        'shared_count': len(pp_set & b_pp_middles)
    }

# Summary stats
coverages = [p['b_coverage'] for p in para_coverages.values()]
mean_cov = sum(coverages) / len(coverages)
max_cov = max(coverages)
min_cov = min(coverages)

print(f"\nA paragraph coverage of classified B vocabulary:")
print(f"  Mean: {mean_cov:.1%}")
print(f"  Max: {max_cov:.1%}")
print(f"  Min: {min_cov:.1%}")

# Distribution
print(f"\nCoverage distribution:")
bins = [(0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.4), (0.4, 0.5), (0.5, 1.0)]
for low, high in bins:
    count = sum(1 for c in coverages if low <= c < high)
    print(f"  {low:.0%}-{high:.0%}: {count} paragraphs")

# Best paragraphs
print(f"\nTop 10 A paragraphs by B coverage:")
sorted_paras = sorted(para_coverages.items(), key=lambda x: -x[1]['b_coverage'])
for para_id, stats in sorted_paras[:10]:
    folio = para_tokens[para_id][0].get('folio', '?') if para_tokens[para_id] else '?'
    print(f"  {para_id} ({folio}): {stats['b_coverage']:.1%} ({stats['shared_count']}/{len(b_pp_middles)} PP MIDDLEs)")

# =============================================================
# STEP 4: What about per-B-folio coverage?
# =============================================================
print("\n" + "="*70)
print("STEP 4: A paragraph coverage of specific B folios")
print("="*70)

# For the best A paragraph, how well does it cover each B folio?
best_para_id = sorted_paras[0][0]
best_para_pp = para_pp[best_para_id]

print(f"\nBest A paragraph: {best_para_id}")
print(f"PP MIDDLEs in this paragraph: {len(best_para_pp)}")

b_folio_coverages = []
for b_folio, b_folio_pp in b_pp_by_folio.items():
    if b_folio_pp:
        cov = len(best_para_pp & b_folio_pp) / len(b_folio_pp)
        b_folio_coverages.append((b_folio, cov, len(b_folio_pp)))

b_folio_coverages.sort(key=lambda x: -x[1])

print(f"\nB folio coverage by best A paragraph:")
print(f"  Best B folios:")
for bf, cov, size in b_folio_coverages[:5]:
    print(f"    {bf}: {cov:.1%} ({int(cov*size)}/{size} PP MIDDLEs)")

print(f"  Worst B folios:")
for bf, cov, size in b_folio_coverages[-5:]:
    print(f"    {bf}: {cov:.1%} ({int(cov*size)}/{size} PP MIDDLEs)")

mean_b_folio_cov = sum(c for _, c, _ in b_folio_coverages) / len(b_folio_coverages)
print(f"\n  Mean B folio coverage: {mean_b_folio_cov:.1%}")

# =============================================================
# STEP 5: How many A paragraphs needed for 80% coverage?
# =============================================================
print("\n" + "="*70)
print("STEP 5: How many A paragraphs for 80% B coverage?")
print("="*70)

# Greedy: keep adding paragraphs until we hit 80%
remaining_paras = list(para_pp.items())
covered = set()
selected = []

while remaining_paras and len(covered) < 0.8 * len(b_pp_middles):
    # Find paragraph that adds most new coverage
    best_gain = 0
    best_idx = 0
    for i, (para_id, pp_set) in enumerate(remaining_paras):
        gain = len((pp_set & b_pp_middles) - covered)
        if gain > best_gain:
            best_gain = gain
            best_idx = i

    if best_gain == 0:
        break

    para_id, pp_set = remaining_paras.pop(best_idx)
    covered.update(pp_set & b_pp_middles)
    selected.append((para_id, len(covered) / len(b_pp_middles)))

print(f"\nGreedy selection to reach 80% coverage:")
for i, (para_id, cum_cov) in enumerate(selected[:20]):
    print(f"  {i+1}. {para_id}: cumulative {cum_cov:.1%}")
    if cum_cov >= 0.8:
        print(f"\n  -> Reached 80% with {i+1} paragraphs")
        break

if selected and selected[-1][1] < 0.8:
    print(f"\n  -> Max coverage with all paragraphs: {selected[-1][1]:.1%}")

# =============================================================
# SUMMARY
# =============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
QUESTION: Does a single A paragraph make B usable?

FINDINGS:

1. Classified B vocabulary: {len(b_pp_middles)} PP MIDDLEs

2. Single A paragraph coverage:
   - Mean: {mean_cov:.1%}
   - Best: {max_cov:.1%}
   - Most paragraphs cover {mean_cov:.1%} of B vocabulary

3. Best A paragraph covers {mean_b_folio_cov:.1%} of an average B folio

4. To reach 80% coverage: {len([s for s in selected if s[1] < 0.8]) + 1} paragraphs needed
""")

if max_cov > 0.5:
    print("CONCLUSION: Best A paragraphs cover >50% of B vocabulary.")
    print("A single paragraph provides substantial B coverage.")
elif max_cov > 0.3:
    print("CONCLUSION: Best A paragraphs cover 30-50% of B vocabulary.")
    print("A single paragraph is PARTIAL - need multiple for full coverage.")
else:
    print("CONCLUSION: A paragraphs cover <30% of B vocabulary each.")
    print("A single paragraph is INSUFFICIENT for B usability.")
