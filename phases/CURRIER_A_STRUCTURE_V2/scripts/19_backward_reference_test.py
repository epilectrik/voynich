"""
19_backward_reference_test.py

BACKWARD REFERENCE TEST

Question: Do WITHOUT-RI paragraphs share more PP with PRECEDING paragraphs?

We found:
- WITHOUT-RI has 0.53x overlap with NEXT (not forward bridging)
- Material reference is "implicit"

Test: Compare vocabulary overlap with PRECEDING paragraph.
If WITHOUT-RI shares more with PRECEDING, they reference materials backward.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("BACKWARD REFERENCE TEST")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD PARAGRAPH INVENTORY
# =============================================================
print("\n[1/3] Building paragraph inventory...")

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

# =============================================================
# STEP 2: COMPUTE BACKWARD OVERLAP
# =============================================================
print("\n[2/3] Computing backward overlap...")

# For paragraphs that have a predecessor, compute overlap
with_ri_backward = []  # WITH-RI paragraph overlap with preceding
without_ri_backward = []  # WITHOUT-RI paragraph overlap with preceding

# Also track what TYPE the predecessor is
without_ri_after_with_ri = []
without_ri_after_without_ri = []
with_ri_after_with_ri = []
with_ri_after_without_ri = []

for folio, paragraphs in folio_paragraphs.items():
    if len(paragraphs) < 2:
        continue

    # Compute vocabulary for each paragraph
    para_vocab = []
    para_type = []
    for para in paragraphs:
        vocab = get_pp_middles(para, analyzer, morph)
        is_with_ri = has_initial_ri(para, analyzer)
        para_vocab.append(vocab)
        para_type.append('WITH_RI' if is_with_ri else 'WITHOUT_RI')

    # For each paragraph (except first), compute overlap with predecessor
    for i in range(1, len(paragraphs)):
        prev_vocab = para_vocab[i - 1]
        curr_vocab = para_vocab[i]
        prev_type = para_type[i - 1]
        curr_type = para_type[i]

        if not prev_vocab or not curr_vocab:
            continue

        # Jaccard overlap
        intersection = len(prev_vocab & curr_vocab)
        union = len(prev_vocab | curr_vocab)
        jaccard = intersection / union if union > 0 else 0

        # Raw overlap count
        overlap = intersection

        entry = {
            'folio': folio,
            'position': i,
            'overlap': overlap,
            'jaccard': jaccard,
            'curr_size': len(curr_vocab),
            'prev_size': len(prev_vocab),
            'prev_type': prev_type
        }

        if curr_type == 'WITH_RI':
            with_ri_backward.append(entry)
            if prev_type == 'WITH_RI':
                with_ri_after_with_ri.append(entry)
            else:
                with_ri_after_without_ri.append(entry)
        else:
            without_ri_backward.append(entry)
            if prev_type == 'WITH_RI':
                without_ri_after_with_ri.append(entry)
            else:
                without_ri_after_without_ri.append(entry)

print(f"   WITH-RI paragraphs with predecessor: {len(with_ri_backward)}")
print(f"   WITHOUT-RI paragraphs with predecessor: {len(without_ri_backward)}")

# =============================================================
# STEP 3: COMPARE BACKWARD OVERLAP
# =============================================================
print("\n[3/3] Comparing backward overlap...")

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

print(f"\nBACKWARD OVERLAP (with preceding paragraph):")
print(f"{'Metric':<35} {'WITH-RI':>12} {'WITHOUT-RI':>14} {'Ratio':>10}")
print("-" * 73)

# Jaccard overlap
avg_with = avg([e['jaccard'] for e in with_ri_backward])
avg_without = avg([e['jaccard'] for e in without_ri_backward])
ratio = avg_without / avg_with if avg_with > 0 else 0
marker = ">> WITHOUT" if ratio > 1.2 else "<< WITH" if ratio < 0.8 else ""
print(f"{'Avg Jaccard with PRECEDING:':<35} {avg_with:>12.3f} {avg_without:>14.3f} {ratio:>9.2f}x {marker}")

# Raw overlap count
avg_with = avg([e['overlap'] for e in with_ri_backward])
avg_without = avg([e['overlap'] for e in without_ri_backward])
ratio = avg_without / avg_with if avg_with > 0 else 0
marker = ">> WITHOUT" if ratio > 1.2 else "<< WITH" if ratio < 0.8 else ""
print(f"{'Avg overlap count with PRECEDING:':<35} {avg_with:>12.1f} {avg_without:>14.1f} {ratio:>9.2f}x {marker}")

# =============================================================
# BREAKDOWN BY PREDECESSOR TYPE
# =============================================================
print("\n" + "="*70)
print("BREAKDOWN BY PREDECESSOR TYPE")
print("="*70)

print(f"\nWITHOUT-RI paragraphs following...")
print(f"  After WITH-RI: {len(without_ri_after_with_ri)} paragraphs, avg Jaccard={avg([e['jaccard'] for e in without_ri_after_with_ri]):.3f}")
print(f"  After WITHOUT-RI: {len(without_ri_after_without_ri)} paragraphs, avg Jaccard={avg([e['jaccard'] for e in without_ri_after_without_ri]):.3f}")

print(f"\nWITH-RI paragraphs following...")
print(f"  After WITH-RI: {len(with_ri_after_with_ri)} paragraphs, avg Jaccard={avg([e['jaccard'] for e in with_ri_after_with_ri]):.3f}")
print(f"  After WITHOUT-RI: {len(with_ri_after_without_ri)} paragraphs, avg Jaccard={avg([e['jaccard'] for e in with_ri_after_without_ri]):.3f}")

# Key comparison: Does WITHOUT-RI share MORE with preceding WITH-RI?
without_after_with_jaccard = avg([e['jaccard'] for e in without_ri_after_with_ri])
with_after_with_jaccard = avg([e['jaccard'] for e in with_ri_after_with_ri])

print(f"\nKey comparison:")
print(f"  WITHOUT-RI after WITH-RI: {without_after_with_jaccard:.3f}")
print(f"  WITH-RI after WITH-RI: {with_after_with_jaccard:.3f}")
if without_after_with_jaccard > with_after_with_jaccard * 1.1:
    print(f"  -> WITHOUT-RI shares MORE with preceding WITH-RI ({without_after_with_jaccard/with_after_with_jaccard:.2f}x)")
elif with_after_with_jaccard > without_after_with_jaccard * 1.1:
    print(f"  -> WITH-RI shares MORE with preceding WITH-RI ({with_after_with_jaccard/without_after_with_jaccard:.2f}x)")
else:
    print(f"  -> Similar overlap rates")

# =============================================================
# COMPARE WITH FORWARD OVERLAP
# =============================================================
print("\n" + "="*70)
print("BACKWARD vs FORWARD COMPARISON")
print("="*70)

# From test 16, we found WITHOUT-RI has 0.53x overlap with NEXT
# Now compare with PRECEDING

backward_without = avg([e['jaccard'] for e in without_ri_backward])
# We need to compute forward overlap too
forward_with_ri = []
forward_without_ri = []

for folio, paragraphs in folio_paragraphs.items():
    if len(paragraphs) < 2:
        continue

    para_vocab = []
    para_type = []
    for para in paragraphs:
        vocab = get_pp_middles(para, analyzer, morph)
        is_with_ri = has_initial_ri(para, analyzer)
        para_vocab.append(vocab)
        para_type.append('WITH_RI' if is_with_ri else 'WITHOUT_RI')

    for i in range(len(paragraphs) - 1):
        curr_vocab = para_vocab[i]
        next_vocab = para_vocab[i + 1]
        curr_type = para_type[i]

        if not curr_vocab or not next_vocab:
            continue

        intersection = len(curr_vocab & next_vocab)
        union = len(curr_vocab | next_vocab)
        jaccard = intersection / union if union > 0 else 0

        if curr_type == 'WITH_RI':
            forward_with_ri.append(jaccard)
        else:
            forward_without_ri.append(jaccard)

backward_without = avg([e['jaccard'] for e in without_ri_backward])
forward_without = avg(forward_without_ri)
backward_with = avg([e['jaccard'] for e in with_ri_backward])
forward_with = avg(forward_with_ri)

print(f"\n{'Direction':<25} {'WITH-RI':>12} {'WITHOUT-RI':>14}")
print("-" * 53)
print(f"{'BACKWARD (with PREV):':<25} {backward_with:>12.3f} {backward_without:>14.3f}")
print(f"{'FORWARD (with NEXT):':<25} {forward_with:>12.3f} {forward_without:>14.3f}")

# Asymmetry test
print(f"\nAsymmetry (BACKWARD/FORWARD):")
print(f"  WITH-RI: {backward_with/forward_with:.2f}x")
print(f"  WITHOUT-RI: {backward_without/forward_without:.2f}x" if forward_without > 0 else "  WITHOUT-RI: n/a")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("\nQuestion: Do WITHOUT-RI paragraphs reference materials backward?")
print("-" * 60)

# Test 1: Higher backward overlap?
if backward_without > backward_with * 1.1:
    print(f"+ WITHOUT-RI has HIGHER backward overlap ({backward_without:.3f} vs {backward_with:.3f})")
    backward_higher = True
elif backward_with > backward_without * 1.1:
    print(f"- WITH-RI has HIGHER backward overlap ({backward_with:.3f} vs {backward_without:.3f})")
    backward_higher = False
else:
    print(f"= Similar backward overlap ({backward_without:.3f} vs {backward_with:.3f})")
    backward_higher = None

# Test 2: Backward vs forward asymmetry
if backward_without > forward_without * 1.2:
    print(f"+ WITHOUT-RI has BACKWARD BIAS ({backward_without:.3f} vs {forward_without:.3f})")
    backward_bias = True
else:
    print(f"- WITHOUT-RI does NOT have backward bias ({backward_without:.3f} vs {forward_without:.3f})")
    backward_bias = False

# Test 3: Without-RI after With-RI specifically
if without_after_with_jaccard > with_after_with_jaccard * 1.1:
    print(f"+ WITHOUT-RI shares MORE with preceding WITH-RI material records")
    material_reference = True
else:
    print(f"- WITHOUT-RI does NOT share more with preceding WITH-RI")
    material_reference = False

print("\n" + "-"*60)
print("VERDICT:")

if backward_higher or material_reference:
    print("""
WITHOUT-RI paragraphs DO reference materials backward:
- Higher vocabulary overlap with preceding paragraph
- Especially when preceding paragraph is WITH-RI (material record)

IMPLICIT REFERENCE MECHANISM: Sequential convention
- WITHOUT-RI applies to materials identified in preceding WITH-RI
- The process instructions reference the just-identified material
""")
    verdict = "BACKWARD_REFERENCE"
else:
    print("""
WITHOUT-RI paragraphs do NOT show clear backward reference pattern.
Material reference mechanism may be:
- Folio-level context (applies to all materials in folio)
- PP vocabulary itself encodes applicability
""")
    verdict = "NO_CLEAR_REFERENCE"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'BACKWARD_REFERENCE_TEST',
    'backward_overlap': {
        'with_ri': backward_with,
        'without_ri': backward_without
    },
    'forward_overlap': {
        'with_ri': forward_with,
        'without_ri': forward_without
    },
    'by_predecessor': {
        'without_ri_after_with_ri': without_after_with_jaccard,
        'without_ri_after_without_ri': avg([e['jaccard'] for e in without_ri_after_without_ri]),
        'with_ri_after_with_ri': with_after_with_jaccard,
        'with_ri_after_without_ri': avg([e['jaccard'] for e in with_ri_after_without_ri])
    },
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'backward_reference_test.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
