"""
08_continuation_test.py

DEEPER TEST: Are WITHOUT-RI paragraphs continuations?

If WITHOUT-RI paragraphs are continuations of previous paragraphs:
1. They should follow WITH-RI paragraphs more often than expected
2. They should share more vocabulary with preceding paragraphs
3. They should appear in specific positions (not first in folio)

Alternative: They are independent relational records (cross-reference pages)
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("CONTINUATION TEST: Are WITHOUT-RI paragraphs continuations?")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD PARAGRAPH SEQUENCE WITH OPENING TYPES
# =============================================================
print("\n[1/4] Building paragraph sequences...")

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

# Classify each paragraph
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

# Build sequence of opening types per folio
folio_sequences = {}
for folio, paragraphs in folio_paragraphs.items():
    sequence = []
    for para_tokens in paragraphs:
        opening = 'WITH_RI' if has_initial_ri(para_tokens, analyzer) else 'WITHOUT_RI'
        sequence.append(opening)
    folio_sequences[folio] = sequence

# =============================================================
# STEP 2: TRANSITION ANALYSIS
# =============================================================
print("\n[2/4] Analyzing paragraph transitions...")

# Count transitions
transitions = Counter()
for folio, seq in folio_sequences.items():
    for i in range(len(seq) - 1):
        prev_type = seq[i]
        curr_type = seq[i+1]
        transitions[(prev_type, curr_type)] += 1

total_transitions = sum(transitions.values())

print(f"\nParagraph transitions (what follows what):")
print(f"{'Transition':<30} {'Count':>8} {'%':>8}")
print("-" * 48)

for (prev, curr), count in sorted(transitions.items()):
    pct = 100 * count / total_transitions if total_transitions > 0 else 0
    print(f"{prev} -> {curr:<15} {count:>8} {pct:>7.1f}%")

# Test: Do WITHOUT_RI paragraphs follow WITH_RI more than expected?
with_ri_total = sum(1 for seq in folio_sequences.values() for t in seq if t == 'WITH_RI')
without_ri_total = sum(1 for seq in folio_sequences.values() for t in seq if t == 'WITHOUT_RI')
total_paras = with_ri_total + without_ri_total

expected_without_after_with = (with_ri_total / total_paras) * (without_ri_total / total_paras) * total_transitions
observed_without_after_with = transitions[('WITH_RI', 'WITHOUT_RI')]

print(f"\nExpected WITHOUT_RI after WITH_RI (random): {expected_without_after_with:.1f}")
print(f"Observed WITHOUT_RI after WITH_RI: {observed_without_after_with}")
print(f"Enrichment: {observed_without_after_with / expected_without_after_with:.2f}x")

# =============================================================
# STEP 3: POSITION ANALYSIS
# =============================================================
print("\n[3/4] Analyzing folio position...")

# What position do WITHOUT_RI paragraphs appear?
position_dist = {'WITH_RI': Counter(), 'WITHOUT_RI': Counter()}

for folio, seq in folio_sequences.items():
    n = len(seq)
    for i, opening in enumerate(seq):
        if n == 1:
            position = 'ONLY'
        elif i == 0:
            position = 'FIRST'
        elif i == n - 1:
            position = 'LAST'
        else:
            position = 'MIDDLE'
        position_dist[opening][position] += 1

print(f"\nPosition distribution by opening type:")
print(f"{'Position':<12} {'WITH_RI':>12} {'WITHOUT_RI':>14} {'Ratio':>10}")
print("-" * 50)

for pos in ['FIRST', 'MIDDLE', 'LAST', 'ONLY']:
    with_ct = position_dist['WITH_RI'][pos]
    without_ct = position_dist['WITHOUT_RI'][pos]
    with_pct = 100 * with_ct / with_ri_total if with_ri_total > 0 else 0
    without_pct = 100 * without_ct / without_ri_total if without_ri_total > 0 else 0
    ratio = without_pct / with_pct if with_pct > 0 else float('inf')
    ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "inf"
    print(f"{pos:<12} {with_pct:>11.1f}% {without_pct:>13.1f}% {ratio_str:>9}")

# Key test: Are WITHOUT_RI ever FIRST?
without_ri_first = position_dist['WITHOUT_RI']['FIRST']
without_ri_first_pct = 100 * without_ri_first / without_ri_total if without_ri_total > 0 else 0

# =============================================================
# STEP 4: VOCABULARY OVERLAP WITH PRECEDING PARAGRAPH
# =============================================================
print("\n[4/4] Analyzing vocabulary overlap with preceding paragraph...")

def get_pp_vocab(para_tokens, analyzer, morph):
    """Get PP MIDDLE vocabulary from a paragraph."""
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

# Calculate vocabulary overlap with preceding paragraph
overlaps_with_ri = []  # WITH_RI paragraph following any paragraph
overlaps_without_ri = []  # WITHOUT_RI paragraph following any paragraph

for folio, paragraphs in folio_paragraphs.items():
    seq = folio_sequences[folio]

    for i in range(1, len(paragraphs)):  # Start from second paragraph
        prev_vocab = get_pp_vocab(paragraphs[i-1], analyzer, morph)
        curr_vocab = get_pp_vocab(paragraphs[i], analyzer, morph)

        if prev_vocab and curr_vocab:
            overlap = len(prev_vocab & curr_vocab)
            union = len(prev_vocab | curr_vocab)
            jaccard = overlap / union if union > 0 else 0

            if seq[i] == 'WITH_RI':
                overlaps_with_ri.append(jaccard)
            else:
                overlaps_without_ri.append(jaccard)

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

avg_overlap_with = avg(overlaps_with_ri)
avg_overlap_without = avg(overlaps_without_ri)

print(f"\nAvg Jaccard overlap with preceding paragraph:")
print(f"  WITH_RI paragraphs: {avg_overlap_with:.3f} (n={len(overlaps_with_ri)})")
print(f"  WITHOUT_RI paragraphs: {avg_overlap_without:.3f} (n={len(overlaps_without_ri)})")

if avg_overlap_without > avg_overlap_with * 1.1:
    print(f"  WITHOUT_RI has {avg_overlap_without/avg_overlap_with:.2f}x MORE overlap -> CONTINUATIONS")
    overlap_verdict = "CONTINUATION_SUPPORTED"
elif avg_overlap_with > avg_overlap_without * 1.1:
    print(f"  WITH_RI has {avg_overlap_with/avg_overlap_without:.2f}x MORE overlap -> NOT CONTINUATIONS")
    overlap_verdict = "CONTINUATION_NOT_SUPPORTED"
else:
    print(f"  Similar overlap -> NO CLEAR PATTERN")
    overlap_verdict = "INCONCLUSIVE"

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION: Are WITHOUT-RI paragraphs continuations?")
print("="*70)

print("\nEvidence:")

# 1. Transition pattern
if observed_without_after_with / expected_without_after_with > 1.2:
    print(f"  + WITHOUT_RI follows WITH_RI {observed_without_after_with / expected_without_after_with:.1f}x more than expected")
    trans_verdict = "SUPPORTS"
else:
    print(f"  - WITHOUT_RI does NOT preferentially follow WITH_RI")
    trans_verdict = "CONTRADICTS"

# 2. Position pattern
if without_ri_first_pct < 15:
    print(f"  + WITHOUT_RI rarely appears FIRST ({without_ri_first_pct:.1f}%) -> suggests continuation")
    pos_verdict = "SUPPORTS"
else:
    print(f"  - WITHOUT_RI often appears FIRST ({without_ri_first_pct:.1f}%) -> NOT continuations")
    pos_verdict = "CONTRADICTS"

# 3. Vocabulary overlap
print(f"  {'+ ' if overlap_verdict == 'CONTINUATION_SUPPORTED' else '- '}", end="")
print(f"Vocabulary overlap: {overlap_verdict.replace('_', ' ')}")

# Overall verdict
supports = sum([trans_verdict == "SUPPORTS", pos_verdict == "SUPPORTS", overlap_verdict == "CONTINUATION_SUPPORTED"])

print("\n" + "-"*60)
print("VERDICT:")
if supports >= 2:
    print("  CONTINUATIONS HYPOTHESIS SUPPORTED")
    print("  WITHOUT-RI paragraphs appear to be continuations of previous content")
    verdict = "CONTINUATIONS"
elif supports == 0:
    print("  CONTINUATIONS HYPOTHESIS REJECTED")
    print("  WITHOUT-RI paragraphs are INDEPENDENT records (relational/cross-reference)")
    verdict = "INDEPENDENT_RECORDS"
else:
    print("  MIXED EVIDENCE - Cannot determine definitively")
    verdict = "INCONCLUSIVE"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'CONTINUATION_TEST',
    'transitions': {f"{k[0]}->{k[1]}": v for k, v in transitions.items()},
    'position_distribution': {
        'WITH_RI': dict(position_dist['WITH_RI']),
        'WITHOUT_RI': dict(position_dist['WITHOUT_RI'])
    },
    'vocabulary_overlap': {
        'avg_with_ri': avg_overlap_with,
        'avg_without_ri': avg_overlap_without
    },
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'continuation_test.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
