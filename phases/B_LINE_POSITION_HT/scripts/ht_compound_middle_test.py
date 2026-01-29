"""
Test: Are line-1 folio-unique MIDDLEs compound forms?

Question: Are the folio-unique identification MIDDLEs built by combining
simpler B MIDDLEs (compound/elaboration mechanism)?

Method:
1. Get all line-1 folio-unique MIDDLEs
2. Get the set of common B MIDDLEs (appear in 5+ folios)
3. Check if folio-unique MIDDLEs can be decomposed into combinations of common MIDDLEs
4. Compare length distributions
5. Look for concatenation patterns
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

# Build MIDDLE -> folios mapping
middle_to_folios = defaultdict(set)
middle_counts = Counter()

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        middle_to_folios[m.middle].add(token.folio)
        middle_counts[m.middle] += 1

# Classify MIDDLEs by folio spread
folio_unique_middles = {mid for mid, folios in middle_to_folios.items() if len(folios) == 1}
common_middles = {mid for mid, folios in middle_to_folios.items() if len(folios) >= 5}
core_middles = {mid for mid, folios in middle_to_folios.items() if len(folios) >= 20}

print(f"MIDDLE Population:")
print(f"  Total unique MIDDLEs: {len(middle_to_folios)}")
print(f"  Folio-unique (1 folio): {len(folio_unique_middles)}")
print(f"  Common (5+ folios): {len(common_middles)}")
print(f"  Core (20+ folios): {len(core_middles)}")
print()

# Collect line-1 HT folio-unique MIDDLEs
folio_lines = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    folio_lines[token.folio][token.line].append({
        'word': w,
        'is_ht': w not in classified_tokens
    })

line1_folio_unique_mids = []
line1_all_mids = []
working_folio_unique_mids = []

for folio, lines in folio_lines.items():
    sorted_lines = sorted(lines.keys())
    if not sorted_lines:
        continue
    first_line = sorted_lines[0]

    for line_num in sorted_lines:
        for tok in lines[line_num]:
            if tok['is_ht']:
                m = morph.extract(tok['word'])
                if m.middle:
                    if line_num == first_line:
                        line1_all_mids.append(m.middle)
                        if m.middle in folio_unique_middles:
                            line1_folio_unique_mids.append(m.middle)
                    else:
                        if m.middle in folio_unique_middles:
                            working_folio_unique_mids.append(m.middle)

print(f"Line-1 Folio-Unique MIDDLEs: {len(line1_folio_unique_mids)} tokens, {len(set(line1_folio_unique_mids))} unique")
print()

def find_substrings(target, candidate_set, min_len=2):
    """Find all MIDDLEs from candidate_set that appear as substrings in target"""
    found = []
    for mid in candidate_set:
        if len(mid) >= min_len and mid in target and mid != target:
            found.append(mid)
    return found

def find_decomposition(target, candidate_set, min_len=2):
    """Try to decompose target into concatenated MIDDLEs from candidate_set"""
    # Greedy: find longest matching prefix, recurse on remainder
    if len(target) < min_len:
        return None

    candidates = sorted([m for m in candidate_set if target.startswith(m) and len(m) >= min_len],
                       key=len, reverse=True)

    for c in candidates:
        remainder = target[len(c):]
        if not remainder:
            return [c]
        sub = find_decomposition(remainder, candidate_set, min_len)
        if sub is not None:
            return [c] + sub

    return None

# Analyze line-1 folio-unique MIDDLEs
unique_line1_fum = set(line1_folio_unique_mids)

print("="*60)
print("COMPOUND MIDDLE ANALYSIS")
print("="*60)

# Length comparison
line1_fum_lengths = [len(m) for m in unique_line1_fum]
common_lengths = [len(m) for m in common_middles]
core_lengths = [len(m) for m in core_middles]

print(f"\nMIDDLE Length Distribution:")
print(f"  Line-1 folio-unique: mean={sum(line1_fum_lengths)/len(line1_fum_lengths):.2f}, range={min(line1_fum_lengths)}-{max(line1_fum_lengths)}")
print(f"  Common (5+ folios): mean={sum(common_lengths)/len(common_lengths):.2f}, range={min(common_lengths)}-{max(common_lengths)}")
print(f"  Core (20+ folios): mean={sum(core_lengths)/len(core_lengths):.2f}, range={min(core_lengths)}-{max(core_lengths)}")

# Check for compound structure
print(f"\nCompound Structure Analysis:")

contains_common = 0
contains_core = 0
fully_decomposable = 0
decomposition_examples = []

for mid in unique_line1_fum:
    common_subs = find_substrings(mid, common_middles)
    core_subs = find_substrings(mid, core_middles)
    decomp = find_decomposition(mid, common_middles)

    if common_subs:
        contains_common += 1
    if core_subs:
        contains_core += 1
    if decomp and len(decomp) >= 2:
        fully_decomposable += 1
        if len(decomposition_examples) < 15:
            decomposition_examples.append((mid, decomp, core_subs))

print(f"  Contains common MIDDLE substring: {contains_common}/{len(unique_line1_fum)} ({100*contains_common/len(unique_line1_fum):.1f}%)")
print(f"  Contains core MIDDLE substring: {contains_core}/{len(unique_line1_fum)} ({100*contains_core/len(unique_line1_fum):.1f}%)")
print(f"  Fully decomposable into 2+ common MIDDLEs: {fully_decomposable}/{len(unique_line1_fum)} ({100*fully_decomposable/len(unique_line1_fum):.1f}%)")

# Show examples
print(f"\nExamples of Decomposable Line-1 Folio-Unique MIDDLEs:")
for mid, decomp, core_subs in decomposition_examples[:10]:
    print(f"  '{mid}' = {' + '.join(decomp)}")
    if core_subs:
        print(f"      (contains core: {core_subs[:3]})")

# Compare to working folio-unique
print("\n" + "="*60)
print("COMPARISON: Line-1 vs Working Folio-Unique MIDDLEs")
print("="*60)

unique_working_fum = set(working_folio_unique_mids)

working_contains_common = sum(1 for mid in unique_working_fum if find_substrings(mid, common_middles))
working_contains_core = sum(1 for mid in unique_working_fum if find_substrings(mid, core_middles))

print(f"\nContains common MIDDLE substring:")
print(f"  Line-1 folio-unique: {100*contains_common/len(unique_line1_fum):.1f}%")
print(f"  Working folio-unique: {100*working_contains_common/len(unique_working_fum):.1f}%")

print(f"\nContains core MIDDLE substring:")
print(f"  Line-1 folio-unique: {100*contains_core/len(unique_line1_fum):.1f}%")
print(f"  Working folio-unique: {100*working_contains_core/len(unique_working_fum):.1f}%")

# Show some actual line-1 folio-unique MIDDLEs
print("\n" + "="*60)
print("SAMPLE: Line-1 Folio-Unique MIDDLEs (by length)")
print("="*60)

sorted_by_len = sorted(unique_line1_fum, key=len, reverse=True)
print("\nLongest line-1 folio-unique MIDDLEs:")
for mid in sorted_by_len[:15]:
    core_subs = find_substrings(mid, core_middles)
    common_subs = find_substrings(mid, common_middles)
    print(f"  '{mid}' (len={len(mid)})")
    if core_subs:
        print(f"      core substrings: {core_subs[:5]}")

# Verdict
print("\n" + "="*60)
print("VERDICT")
print("="*60)

if contains_core / len(unique_line1_fum) > 0.7:
    verdict = "COMPOUND_CONFIRMED"
    explanation = "Line-1 folio-unique MIDDLEs are predominantly built from core B MIDDLEs"
elif contains_common / len(unique_line1_fum) > 0.5:
    verdict = "COMPOUND_LIKELY"
    explanation = "Line-1 folio-unique MIDDLEs frequently contain common B MIDDLE substrings"
else:
    verdict = "COMPOUND_WEAK"
    explanation = "Line-1 folio-unique MIDDLEs show limited compositional relationship to common MIDDLEs"

print(f"\n{verdict}: {explanation}")

# Save results
results = {
    'line1_folio_unique': {
        'count': len(unique_line1_fum),
        'mean_length': sum(line1_fum_lengths)/len(line1_fum_lengths),
        'contains_common_pct': 100*contains_common/len(unique_line1_fum),
        'contains_core_pct': 100*contains_core/len(unique_line1_fum),
        'fully_decomposable_pct': 100*fully_decomposable/len(unique_line1_fum)
    },
    'working_folio_unique': {
        'count': len(unique_working_fum),
        'contains_common_pct': 100*working_contains_common/len(unique_working_fum),
        'contains_core_pct': 100*working_contains_core/len(unique_working_fum)
    },
    'reference': {
        'common_mean_length': sum(common_lengths)/len(common_lengths),
        'core_mean_length': sum(core_lengths)/len(core_lengths)
    },
    'decomposition_examples': [(mid, decomp) for mid, decomp, _ in decomposition_examples],
    'verdict': verdict
}

out_path = PROJECT_ROOT / 'phases' / 'B_LINE_POSITION_HT' / 'results' / 'ht_compound_middle.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
