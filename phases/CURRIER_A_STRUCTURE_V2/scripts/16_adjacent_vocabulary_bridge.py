"""
16_adjacent_vocabulary_bridge.py

ADJACENT VOCABULARY BRIDGE TEST

Question: Do WITHOUT-RI paragraphs serve as "bridges" between adjacent paragraphs?

If WITHOUT-RI are bridging/linking records:
1. They should share vocabulary with BOTH adjacent paragraphs
2. Their vocabulary should be a UNION of neighbors
3. They might "bridge" materials that don't otherwise connect

Test: Compare vocabulary overlap patterns for WITHOUT-RI vs WITH-RI in MIDDLE position.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("ADJACENT VOCABULARY BRIDGE TEST")
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
# STEP 2: ANALYZE MIDDLE-POSITION PARAGRAPHS
# =============================================================
print("\n[2/3] Analyzing middle-position paragraphs...")

# We need paragraphs with both a predecessor and successor
bridge_analyses_with_ri = []
bridge_analyses_without_ri = []

for folio, paragraphs in folio_paragraphs.items():
    if len(paragraphs) < 3:
        continue

    # Only look at middle positions (not first or last)
    for i in range(1, len(paragraphs) - 1):
        prev_para = paragraphs[i - 1]
        curr_para = paragraphs[i]
        next_para = paragraphs[i + 1]

        prev_vocab = get_pp_middles(prev_para, analyzer, morph)
        curr_vocab = get_pp_middles(curr_para, analyzer, morph)
        next_vocab = get_pp_middles(next_para, analyzer, morph)

        if not prev_vocab or not curr_vocab or not next_vocab:
            continue

        # Calculate overlaps
        overlap_prev = len(curr_vocab & prev_vocab)
        overlap_next = len(curr_vocab & next_vocab)
        union_neighbors = prev_vocab | next_vocab
        curr_in_union = len(curr_vocab & union_neighbors)

        # Direct connection between prev and next (without middle)
        prev_next_overlap = len(prev_vocab & next_vocab)

        # Bridge score: does curr connect prev and next better than they connect directly?
        bridge_bonus = curr_in_union - prev_next_overlap

        analysis = {
            'folio': folio,
            'position': i,
            'curr_size': len(curr_vocab),
            'prev_size': len(prev_vocab),
            'next_size': len(next_vocab),
            'overlap_prev': overlap_prev,
            'overlap_next': overlap_next,
            'curr_in_union': curr_in_union,
            'prev_next_direct': prev_next_overlap,
            'bridge_bonus': bridge_bonus,
            'pct_in_union': 100 * curr_in_union / len(curr_vocab) if curr_vocab else 0,
            'connects_both': overlap_prev > 0 and overlap_next > 0
        }

        if has_initial_ri(curr_para, analyzer):
            bridge_analyses_with_ri.append(analysis)
        else:
            bridge_analyses_without_ri.append(analysis)

print(f"   Middle-position WITH-RI: {len(bridge_analyses_with_ri)}")
print(f"   Middle-position WITHOUT-RI: {len(bridge_analyses_without_ri)}")

# =============================================================
# STEP 3: COMPARE BRIDGE METRICS
# =============================================================
print("\n[3/3] Comparing bridge metrics...")

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

print(f"\nBRIDGE METRICS (middle-position paragraphs only):")
print(f"{'Metric':<35} {'WITH-RI':>12} {'WITHOUT-RI':>14} {'Ratio':>10}")
print("-" * 73)

# Overlap with previous
avg_with = avg([a['overlap_prev'] for a in bridge_analyses_with_ri])
avg_without = avg([a['overlap_prev'] for a in bridge_analyses_without_ri])
ratio = avg_without / avg_with if avg_with > 0 else 0
marker = ">> WITHOUT" if ratio > 1.2 else "<< WITH" if ratio < 0.8 else ""
print(f"{'Avg overlap with PREV:':<35} {avg_with:>12.2f} {avg_without:>14.2f} {ratio:>9.2f}x {marker}")

# Overlap with next
avg_with = avg([a['overlap_next'] for a in bridge_analyses_with_ri])
avg_without = avg([a['overlap_next'] for a in bridge_analyses_without_ri])
ratio = avg_without / avg_with if avg_with > 0 else 0
marker = ">> WITHOUT" if ratio > 1.2 else "<< WITH" if ratio < 0.8 else ""
print(f"{'Avg overlap with NEXT:':<35} {avg_with:>12.2f} {avg_without:>14.2f} {ratio:>9.2f}x {marker}")

# Vocabulary in union of neighbors
avg_with = avg([a['pct_in_union'] for a in bridge_analyses_with_ri])
avg_without = avg([a['pct_in_union'] for a in bridge_analyses_without_ri])
ratio = avg_without / avg_with if avg_with > 0 else 0
marker = ">> WITHOUT" if ratio > 1.2 else "<< WITH" if ratio < 0.8 else ""
print(f"{'% vocab in neighbor union:':<35} {avg_with:>11.1f}% {avg_without:>13.1f}% {ratio:>9.2f}x {marker}")

# Bridge bonus
avg_with = avg([a['bridge_bonus'] for a in bridge_analyses_with_ri])
avg_without = avg([a['bridge_bonus'] for a in bridge_analyses_without_ri])
print(f"{'Avg bridge bonus:':<35} {avg_with:>12.2f} {avg_without:>14.2f}")

# Connects both neighbors
pct_both_with = 100 * sum(1 for a in bridge_analyses_with_ri if a['connects_both']) / len(bridge_analyses_with_ri) if bridge_analyses_with_ri else 0
pct_both_without = 100 * sum(1 for a in bridge_analyses_without_ri if a['connects_both']) / len(bridge_analyses_without_ri) if bridge_analyses_without_ri else 0
print(f"{'% connects BOTH neighbors:':<35} {pct_both_with:>11.1f}% {pct_both_without:>13.1f}%")

# =============================================================
# DETAILED ANALYSIS
# =============================================================
print("\n" + "="*70)
print("BRIDGE FUNCTION ANALYSIS")
print("="*70)

# How many paragraphs connect neighbors that don't connect directly?
true_bridges_with = sum(1 for a in bridge_analyses_with_ri if a['prev_next_direct'] == 0 and a['connects_both'])
true_bridges_without = sum(1 for a in bridge_analyses_without_ri if a['prev_next_direct'] == 0 and a['connects_both'])

print(f"\nTrue bridges (connect neighbors that don't connect directly):")
print(f"   WITH-RI: {true_bridges_with}/{len(bridge_analyses_with_ri)} ({100*true_bridges_with/len(bridge_analyses_with_ri):.1f}%)" if bridge_analyses_with_ri else "   WITH-RI: 0")
print(f"   WITHOUT-RI: {true_bridges_without}/{len(bridge_analyses_without_ri)} ({100*true_bridges_without/len(bridge_analyses_without_ri):.1f}%)" if bridge_analyses_without_ri else "   WITHOUT-RI: 0")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("\nQuestion: Do WITHOUT-RI paragraphs serve as vocabulary bridges?")
print("-" * 60)

# Test 1: Higher union coverage?
avg_union_with = avg([a['pct_in_union'] for a in bridge_analyses_with_ri])
avg_union_without = avg([a['pct_in_union'] for a in bridge_analyses_without_ri])

if avg_union_without > avg_union_with * 1.1:
    print(f"+ WITHOUT-RI has HIGHER union coverage ({avg_union_without:.1f}% vs {avg_union_with:.1f}%)")
    union_test = True
else:
    print(f"- Similar union coverage ({avg_union_without:.1f}% vs {avg_union_with:.1f}%)")
    union_test = False

# Test 2: More true bridges?
pct_true_bridge_with = 100 * true_bridges_with / len(bridge_analyses_with_ri) if bridge_analyses_with_ri else 0
pct_true_bridge_without = 100 * true_bridges_without / len(bridge_analyses_without_ri) if bridge_analyses_without_ri else 0

if pct_true_bridge_without > pct_true_bridge_with * 1.5:
    print(f"+ WITHOUT-RI serves as TRUE BRIDGE more often ({pct_true_bridge_without:.1f}% vs {pct_true_bridge_with:.1f}%)")
    bridge_test = True
elif pct_true_bridge_with > pct_true_bridge_without * 1.5:
    print(f"- WITH-RI actually serves as bridge more often ({pct_true_bridge_with:.1f}% vs {pct_true_bridge_without:.1f}%)")
    bridge_test = False
else:
    print(f"= Similar bridging rate ({pct_true_bridge_without:.1f}% vs {pct_true_bridge_with:.1f}%)")
    bridge_test = None

print("\n" + "-"*60)
print("VERDICT:")

if union_test or bridge_test:
    print("""
WITHOUT-RI paragraphs DO serve a bridging function:
- Higher vocabulary overlap with neighbor union
- More likely to connect unconnected neighbors

This supports the "relational record" interpretation:
WITHOUT-RI paragraphs may be BRIDGING records that connect
materials/processes that don't directly share vocabulary.
""")
    verdict = "BRIDGE_FUNCTION_CONFIRMED"
else:
    print("""
WITHOUT-RI paragraphs do NOT show enhanced bridging function.
Both paragraph types have similar vocabulary overlap with neighbors.
""")
    verdict = "NO_BRIDGE_FUNCTION"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'ADJACENT_VOCABULARY_BRIDGE',
    'counts': {
        'middle_with_ri': len(bridge_analyses_with_ri),
        'middle_without_ri': len(bridge_analyses_without_ri)
    },
    'bridge_metrics': {
        'avg_overlap_prev_with': avg([a['overlap_prev'] for a in bridge_analyses_with_ri]),
        'avg_overlap_prev_without': avg([a['overlap_prev'] for a in bridge_analyses_without_ri]),
        'avg_union_coverage_with': avg_union_with,
        'avg_union_coverage_without': avg_union_without,
        'pct_true_bridge_with': pct_true_bridge_with,
        'pct_true_bridge_without': pct_true_bridge_without
    },
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'adjacent_vocabulary_bridge.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
