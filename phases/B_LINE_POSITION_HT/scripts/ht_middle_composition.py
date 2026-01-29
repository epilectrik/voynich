"""
Test: Line-1 HT vs Working HT MIDDLE Compositional Origin

Question: Do line-1 HT tokens derive from RI atoms while working HT derives from PP atoms?

Method:
1. Extract all HT tokens from B, separate by line position
2. For each group, extract MIDDLEs
3. Classify each MIDDLE: PP (shared), RI (A-exclusive), B-exclusive, or Novel
4. Check substring containment of PP and RI atoms in novel MIDDLEs
5. Compare distributions between line-1 HT and working HT
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

# Load data
tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

# Load MIDDLE classification (PP vs RI)
mc_path = PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json'
with open(mc_path, 'r', encoding='utf-8') as f:
    mc = json.load(f)

ri_middles = set(mc['a_exclusive_middles'])  # A-exclusive (RI)
# PP middles are shared - need to extract from a_shared list if available
# Otherwise compute from A and B vocabulary

# Load A and B vocabulary to compute PP middles
a_middles = set()
for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        a_middles.add(m.middle)

b_middles = set()
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_middles.add(m.middle)

pp_middles = a_middles & b_middles  # Shared between A and B
b_exclusive_middles = b_middles - a_middles  # B-only

print(f"MIDDLE Sets:")
print(f"  RI (A-exclusive): {len(ri_middles)}")
print(f"  PP (A-B shared): {len(pp_middles)}")
print(f"  B-exclusive: {len(b_exclusive_middles)}")
print()

# Collect HT tokens by line position
line1_ht = []  # HT tokens on line 1
working_ht = []  # HT tokens on lines 2+

# Group tokens by folio and line
folio_lines = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    folio_lines[token.folio][token.line].append({
        'word': w,
        'is_ht': w not in classified_tokens
    })

# Identify line 1 for each folio and categorize HT tokens
for folio, lines in folio_lines.items():
    sorted_lines = sorted(lines.keys())
    if not sorted_lines:
        continue
    first_line = sorted_lines[0]

    for line_num in sorted_lines:
        for tok in lines[line_num]:
            if tok['is_ht']:
                if line_num == first_line:
                    line1_ht.append(tok['word'])
                else:
                    working_ht.append(tok['word'])

print(f"HT Token Counts:")
print(f"  Line-1 HT: {len(line1_ht)}")
print(f"  Working HT: {len(working_ht)}")
print()

def classify_middle(middle, pp_set, ri_set, b_excl_set):
    """Classify a MIDDLE as PP, RI, B-exclusive, or Novel"""
    if middle in pp_set:
        return 'PP'
    elif middle in ri_set:
        return 'RI'
    elif middle in b_excl_set:
        return 'B_EXCL'
    else:
        return 'NOVEL'

def contains_atom(middle, atom_set, min_len=2):
    """Check if middle contains any atom from the set as substring"""
    for atom in atom_set:
        if len(atom) >= min_len and atom in middle:
            return True
    return False

def analyze_ht_group(tokens, label):
    """Analyze MIDDLE composition of an HT token group"""
    middles = []
    middle_classes = Counter()

    for word in tokens:
        m = morph.extract(word)
        if m.middle:
            middles.append(m.middle)
            cls = classify_middle(m.middle, pp_middles, ri_middles, b_exclusive_middles)
            middle_classes[cls] += 1

    total = len(middles)
    unique_middles = set(middles)

    # For novel MIDDLEs, check atom containment
    novel_middles = [mid for mid in unique_middles if classify_middle(mid, pp_middles, ri_middles, b_exclusive_middles) == 'NOVEL']
    novel_with_pp_atom = sum(1 for mid in novel_middles if contains_atom(mid, pp_middles))
    novel_with_ri_atom = sum(1 for mid in novel_middles if contains_atom(mid, ri_middles))
    novel_with_both = sum(1 for mid in novel_middles if contains_atom(mid, pp_middles) and contains_atom(mid, ri_middles))
    novel_with_neither = sum(1 for mid in novel_middles if not contains_atom(mid, pp_middles) and not contains_atom(mid, ri_middles))

    print(f"\n{label} ({total} tokens, {len(unique_middles)} unique MIDDLEs):")
    print(f"  MIDDLE Classification (token-level):")
    for cls in ['PP', 'RI', 'B_EXCL', 'NOVEL']:
        count = middle_classes[cls]
        pct = 100 * count / total if total > 0 else 0
        print(f"    {cls}: {count} ({pct:.1f}%)")

    print(f"  Novel MIDDLE Atom Containment ({len(novel_middles)} unique novel MIDDLEs):")
    if novel_middles:
        print(f"    Contains PP atom: {novel_with_pp_atom} ({100*novel_with_pp_atom/len(novel_middles):.1f}%)")
        print(f"    Contains RI atom: {novel_with_ri_atom} ({100*novel_with_ri_atom/len(novel_middles):.1f}%)")
        print(f"    Contains both: {novel_with_both} ({100*novel_with_both/len(novel_middles):.1f}%)")
        print(f"    Contains neither: {novel_with_neither} ({100*novel_with_neither/len(novel_middles):.1f}%)")

    return {
        'total_tokens': total,
        'unique_middles': len(unique_middles),
        'classification': {cls: middle_classes[cls] for cls in ['PP', 'RI', 'B_EXCL', 'NOVEL']},
        'classification_pct': {cls: 100 * middle_classes[cls] / total if total > 0 else 0 for cls in ['PP', 'RI', 'B_EXCL', 'NOVEL']},
        'novel_count': len(novel_middles),
        'novel_with_pp_atom': novel_with_pp_atom,
        'novel_with_ri_atom': novel_with_ri_atom,
        'novel_with_both': novel_with_both,
        'novel_with_neither': novel_with_neither
    }

# Analyze both groups
line1_results = analyze_ht_group(line1_ht, "LINE-1 HT")
working_results = analyze_ht_group(working_ht, "WORKING HT")

# Compare RI participation
print("\n" + "="*60)
print("COMPARISON: Line-1 HT vs Working HT")
print("="*60)

line1_ri_pct = line1_results['classification_pct']['RI']
working_ri_pct = working_results['classification_pct']['RI']
line1_pp_pct = line1_results['classification_pct']['PP']
working_pp_pct = working_results['classification_pct']['PP']

print(f"\nDirect MIDDLE Classification:")
print(f"  RI rate: Line-1 = {line1_ri_pct:.1f}%, Working = {working_ri_pct:.1f}%")
print(f"  PP rate: Line-1 = {line1_pp_pct:.1f}%, Working = {working_pp_pct:.1f}%")
print(f"  B_EXCL rate: Line-1 = {line1_results['classification_pct']['B_EXCL']:.1f}%, Working = {working_results['classification_pct']['B_EXCL']:.1f}%")
print(f"  NOVEL rate: Line-1 = {line1_results['classification_pct']['NOVEL']:.1f}%, Working = {working_results['classification_pct']['NOVEL']:.1f}%")

# Check if there's ANY RI content
if line1_results['classification']['RI'] > 0:
    print(f"\n*** FINDING: Line-1 HT has {line1_results['classification']['RI']} tokens with RI MIDDLEs! ***")
else:
    print(f"\nLine-1 HT has ZERO RI MIDDLEs (same as working HT)")

# Novel MIDDLE atom containment comparison
print(f"\nNovel MIDDLE Atom Containment:")
if line1_results['novel_count'] > 0:
    line1_ri_atom_pct = 100 * line1_results['novel_with_ri_atom'] / line1_results['novel_count']
else:
    line1_ri_atom_pct = 0
if working_results['novel_count'] > 0:
    working_ri_atom_pct = 100 * working_results['novel_with_ri_atom'] / working_results['novel_count']
else:
    working_ri_atom_pct = 0

print(f"  Contains RI atom: Line-1 = {line1_ri_atom_pct:.1f}%, Working = {working_ri_atom_pct:.1f}%")

# Verdict
print("\n" + "="*60)
print("VERDICT")
print("="*60)

if line1_ri_pct > 1.0 or line1_ri_atom_pct > working_ri_atom_pct * 1.5:
    verdict = "RI_DERIVATION_DETECTED"
    explanation = "Line-1 HT shows elevated RI participation compared to working HT"
elif line1_ri_pct == 0 and line1_ri_atom_pct <= working_ri_atom_pct * 1.2:
    verdict = "NO_RI_DERIVATION"
    explanation = "Line-1 HT and working HT both have zero direct RI MIDDLEs and similar atom containment"
else:
    verdict = "INCONCLUSIVE"
    explanation = "Mixed signals - needs further investigation"

print(f"\n{verdict}: {explanation}")

# Save results
results = {
    'line1_ht': line1_results,
    'working_ht': working_results,
    'comparison': {
        'line1_ri_pct': line1_ri_pct,
        'working_ri_pct': working_ri_pct,
        'line1_pp_pct': line1_pp_pct,
        'working_pp_pct': working_pp_pct,
        'line1_ri_atom_containment_pct': line1_ri_atom_pct,
        'working_ri_atom_containment_pct': working_ri_atom_pct
    },
    'verdict': verdict,
    'explanation': explanation
}

out_path = PROJECT_ROOT / 'phases' / 'B_LINE_POSITION_HT' / 'results' / 'ht_middle_composition.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
