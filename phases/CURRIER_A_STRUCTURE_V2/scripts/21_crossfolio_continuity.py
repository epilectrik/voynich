"""
21_crossfolio_continuity.py

CROSS-FOLIO CONTINUITY TEST

Question: When a WITHOUT-RI paragraph begins a folio, does it continue
from the previous folio?

Test:
1. Find folios where the FIRST paragraph is WITHOUT-RI
2. Check vocabulary overlap with the LAST paragraph of the PREVIOUS folio
3. Compare to baseline (WITH-RI first paragraphs vs previous folio)
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("CROSS-FOLIO CONTINUITY TEST")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD FOLIO-ORDERED PARAGRAPH INVENTORY
# =============================================================
print("\n[1/3] Building folio-ordered paragraph inventory...")

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

# Get ordered folio list
folio_order = list(folio_paragraphs.keys())
print(f"   Total folios: {len(folio_order)}")
print(f"   Folio order sample: {folio_order[:5]} ... {folio_order[-5:]}")

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

# =============================================================
# STEP 2: ANALYZE CROSS-FOLIO TRANSITIONS
# =============================================================
print("\n[2/3] Analyzing cross-folio transitions...")

# For each folio (except the first), check:
# - What type is the FIRST paragraph?
# - What's the vocabulary overlap with LAST paragraph of previous folio?

cross_folio_data = []

for i in range(1, len(folio_order)):
    prev_folio = folio_order[i - 1]
    curr_folio = folio_order[i]

    prev_paragraphs = folio_paragraphs[prev_folio]
    curr_paragraphs = folio_paragraphs[curr_folio]

    if not prev_paragraphs or not curr_paragraphs:
        continue

    # Last paragraph of previous folio
    prev_last = prev_paragraphs[-1]
    prev_last_type = 'WITH_RI' if has_initial_ri(prev_last, analyzer) else 'WITHOUT_RI'
    prev_last_vocab = get_pp_middles(prev_last, analyzer, morph)

    # First paragraph of current folio
    curr_first = curr_paragraphs[0]
    curr_first_type = 'WITH_RI' if has_initial_ri(curr_first, analyzer) else 'WITHOUT_RI'
    curr_first_vocab = get_pp_middles(curr_first, analyzer, morph)

    if not prev_last_vocab or not curr_first_vocab:
        continue

    # Compute overlap
    intersection = len(prev_last_vocab & curr_first_vocab)
    union = len(prev_last_vocab | curr_first_vocab)
    jaccard = intersection / union if union > 0 else 0

    cross_folio_data.append({
        'prev_folio': prev_folio,
        'curr_folio': curr_folio,
        'prev_last_type': prev_last_type,
        'curr_first_type': curr_first_type,
        'jaccard': jaccard,
        'overlap': intersection,
        'transition': f"{prev_last_type} -> {curr_first_type}"
    })

print(f"   Cross-folio transitions analyzed: {len(cross_folio_data)}")

# =============================================================
# STEP 3: COMPARE BY TRANSITION TYPE
# =============================================================
print("\n[3/3] Comparing by transition type...")

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

# Group by transition type
transitions = defaultdict(list)
for d in cross_folio_data:
    transitions[d['transition']].append(d)

print(f"\nCROSS-FOLIO VOCABULARY OVERLAP BY TRANSITION TYPE:")
print(f"{'Transition':<30} {'Count':>8} {'Avg Jaccard':>12}")
print("-" * 52)

for trans_type in sorted(transitions.keys()):
    data = transitions[trans_type]
    avg_jac = avg([d['jaccard'] for d in data])
    print(f"{trans_type:<30} {len(data):>8} {avg_jac:>12.3f}")

# Key comparison: Does WITHOUT-RI first show MORE overlap with previous folio?
without_ri_first = [d for d in cross_folio_data if d['curr_first_type'] == 'WITHOUT_RI']
with_ri_first = [d for d in cross_folio_data if d['curr_first_type'] == 'WITH_RI']

avg_without = avg([d['jaccard'] for d in without_ri_first])
avg_with = avg([d['jaccard'] for d in with_ri_first])

print(f"\n{'SUMMARY BY FIRST PARAGRAPH TYPE':<30}")
print("-" * 52)
print(f"{'WITHOUT-RI starts folio:':<30} {len(without_ri_first):>8} {avg_without:>12.3f}")
print(f"{'WITH-RI starts folio:':<30} {len(with_ri_first):>8} {avg_with:>12.3f}")

ratio = avg_without / avg_with if avg_with > 0 else 0
print(f"\nRatio (WITHOUT/WITH): {ratio:.2f}x")

# =============================================================
# COMPARE WITH WITHIN-FOLIO OVERLAP
# =============================================================
print("\n" + "="*70)
print("CROSS-FOLIO vs WITHIN-FOLIO COMPARISON")
print("="*70)

# Within-folio: overlap of paragraph with its SAME-FOLIO predecessor
within_folio_with = []
within_folio_without = []

for folio, paragraphs in folio_paragraphs.items():
    if len(paragraphs) < 2:
        continue

    for i in range(1, len(paragraphs)):
        prev_vocab = get_pp_middles(paragraphs[i-1], analyzer, morph)
        curr_vocab = get_pp_middles(paragraphs[i], analyzer, morph)

        if not prev_vocab or not curr_vocab:
            continue

        intersection = len(prev_vocab & curr_vocab)
        union = len(prev_vocab | curr_vocab)
        jaccard = intersection / union if union > 0 else 0

        if has_initial_ri(paragraphs[i], analyzer):
            within_folio_with.append(jaccard)
        else:
            within_folio_without.append(jaccard)

avg_within_with = avg(within_folio_with)
avg_within_without = avg(within_folio_without)

print(f"\n{'Context':<25} {'WITH-RI':>15} {'WITHOUT-RI':>15}")
print("-" * 57)
print(f"{'WITHIN-FOLIO:':<25} {avg_within_with:>15.3f} {avg_within_without:>15.3f}")
print(f"{'CROSS-FOLIO:':<25} {avg_with:>15.3f} {avg_without:>15.3f}")

print(f"\nCross-folio / Within-folio ratio:")
print(f"  WITH-RI: {avg_with/avg_within_with:.2f}x" if avg_within_with > 0 else "  WITH-RI: n/a")
print(f"  WITHOUT-RI: {avg_without/avg_within_without:.2f}x" if avg_within_without > 0 else "  WITHOUT-RI: n/a")

# =============================================================
# SPECIFIC EXAMPLES
# =============================================================
print("\n" + "="*70)
print("EXAMPLES: WITHOUT-RI STARTING FOLIO")
print("="*70)

# High overlap examples (potential continuations)
high_overlap = sorted(without_ri_first, key=lambda x: -x['jaccard'])[:10]
print(f"\nHIGHEST overlap (potential cross-folio continuations):")
for d in high_overlap:
    print(f"   {d['prev_folio']} ({d['prev_last_type']}) -> {d['curr_folio']}: Jaccard={d['jaccard']:.3f}")

# Low overlap examples (fresh starts)
low_overlap = sorted(without_ri_first, key=lambda x: x['jaccard'])[:10]
print(f"\nLOWEST overlap (fresh starts):")
for d in low_overlap:
    print(f"   {d['prev_folio']} ({d['prev_last_type']}) -> {d['curr_folio']}: Jaccard={d['jaccard']:.3f}")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("\nQuestion: When WITHOUT-RI starts a folio, is it continuing from previous folio?")
print("-" * 60)

# Test 1: Does WITHOUT-RI first show MORE cross-folio overlap?
if avg_without > avg_with * 1.2:
    print(f"+ WITHOUT-RI first has HIGHER cross-folio overlap ({avg_without:.3f} vs {avg_with:.3f})")
    print(f"  -> Suggests cross-folio continuation")
    continuity_test = "CONTINUATION"
elif avg_with > avg_without * 1.2:
    print(f"- WITH-RI first has HIGHER cross-folio overlap ({avg_with:.3f} vs {avg_without:.3f})")
    print(f"  -> WITHOUT-RI first are NOT continuations")
    continuity_test = "NOT_CONTINUATION"
else:
    print(f"= Similar cross-folio overlap ({avg_without:.3f} vs {avg_with:.3f})")
    continuity_test = "INCONCLUSIVE"

# Test 2: Is cross-folio overlap lower than within-folio?
if avg_without < avg_within_without * 0.8:
    print(f"+ Cross-folio overlap is LOWER than within-folio ({avg_without:.3f} vs {avg_within_without:.3f})")
    print(f"  -> Folio boundaries are meaningful breaks")
    boundary_test = "MEANINGFUL_BOUNDARY"
else:
    print(f"- Cross-folio overlap similar to within-folio")
    boundary_test = "NOT_MEANINGFUL"

print("\n" + "-"*60)
print("VERDICT:")

if continuity_test == "CONTINUATION":
    print("""
WITHOUT-RI paragraphs that begin folios DO appear to continue
from the previous folio. They show higher cross-folio vocabulary
overlap than WITH-RI paragraph starts.

This extends the "backward reference" pattern across folio boundaries.
""")
    verdict = "CROSS_FOLIO_CONTINUATION"
elif continuity_test == "NOT_CONTINUATION":
    print("""
WITHOUT-RI paragraphs that begin folios are NOT continuations.
They show LOWER cross-folio overlap than WITH-RI starts.

These may be:
- Folio-level "preamble" records (general setup)
- Independent process annotations
- Different function from non-first WITHOUT-RI
""")
    verdict = "INDEPENDENT_START"
else:
    print("""
Cross-folio continuity is INCONCLUSIVE.
Similar overlap patterns for both paragraph types.
Folio boundaries may not strongly affect continuity.
""")
    verdict = "INCONCLUSIVE"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'CROSSFOLIO_CONTINUITY',
    'cross_folio_overlap': {
        'without_ri_first': avg_without,
        'with_ri_first': avg_with,
        'ratio': ratio
    },
    'within_folio_overlap': {
        'without_ri': avg_within_without,
        'with_ri': avg_within_with
    },
    'transition_counts': {t: len(d) for t, d in transitions.items()},
    'transition_overlaps': {t: avg([x['jaccard'] for x in d]) for t, d in transitions.items()},
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'crossfolio_continuity.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
