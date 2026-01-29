"""
Test: Line-1 HT vs Working HT MIDDLE Compositional Origin (v2)

Extended version: also checks B-exclusive MIDDLEs for RI/PP atom containment
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
folio_lines = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    folio_lines[token.folio][token.line].append({
        'word': w,
        'is_ht': w not in classified_tokens
    })

line1_ht = []
working_ht = []

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
    """Classify a MIDDLE as PP, RI, or B-exclusive"""
    if middle in pp_set:
        return 'PP'
    elif middle in ri_set:
        return 'RI'
    elif middle in b_excl_set:
        return 'B_EXCL'
    else:
        return 'UNKNOWN'

def contains_atom(middle, atom_set, min_len=2):
    """Check if middle contains any atom from the set as substring"""
    for atom in atom_set:
        if len(atom) >= min_len and atom in middle:
            return True
    return False

def get_contained_atoms(middle, atom_set, min_len=2):
    """Get list of atoms from the set that are contained in middle"""
    found = []
    for atom in atom_set:
        if len(atom) >= min_len and atom in middle:
            found.append(atom)
    return found

def analyze_ht_group(tokens, label):
    """Analyze MIDDLE composition of an HT token group"""
    middle_classes = Counter()
    b_excl_middles_found = []

    for word in tokens:
        m = morph.extract(word)
        if m.middle:
            cls = classify_middle(m.middle, pp_middles, ri_middles, b_exclusive_middles)
            middle_classes[cls] += 1
            if cls == 'B_EXCL':
                b_excl_middles_found.append(m.middle)

    total = sum(middle_classes.values())
    unique_b_excl = set(b_excl_middles_found)

    # For B-exclusive MIDDLEs, check RI and PP atom containment
    b_excl_with_pp_atom = sum(1 for mid in unique_b_excl if contains_atom(mid, pp_middles))
    b_excl_with_ri_atom = sum(1 for mid in unique_b_excl if contains_atom(mid, ri_middles))
    b_excl_with_both = sum(1 for mid in unique_b_excl if contains_atom(mid, pp_middles) and contains_atom(mid, ri_middles))
    b_excl_with_neither = sum(1 for mid in unique_b_excl if not contains_atom(mid, pp_middles) and not contains_atom(mid, ri_middles))

    print(f"\n{label} ({total} tokens):")
    print(f"  MIDDLE Classification (token-level):")
    for cls in ['PP', 'RI', 'B_EXCL', 'UNKNOWN']:
        count = middle_classes[cls]
        pct = 100 * count / total if total > 0 else 0
        print(f"    {cls}: {count} ({pct:.1f}%)")

    print(f"  B-Exclusive MIDDLE Atom Containment ({len(unique_b_excl)} unique B-excl MIDDLEs):")
    if unique_b_excl:
        print(f"    Contains PP atom: {b_excl_with_pp_atom} ({100*b_excl_with_pp_atom/len(unique_b_excl):.1f}%)")
        print(f"    Contains RI atom: {b_excl_with_ri_atom} ({100*b_excl_with_ri_atom/len(unique_b_excl):.1f}%)")
        print(f"    Contains both: {b_excl_with_both} ({100*b_excl_with_both/len(unique_b_excl):.1f}%)")
        print(f"    Contains neither: {b_excl_with_neither} ({100*b_excl_with_neither/len(unique_b_excl):.1f}%)")

    return {
        'total_tokens': total,
        'classification': {cls: middle_classes[cls] for cls in ['PP', 'RI', 'B_EXCL', 'UNKNOWN']},
        'classification_pct': {cls: 100 * middle_classes[cls] / total if total > 0 else 0 for cls in ['PP', 'RI', 'B_EXCL', 'UNKNOWN']},
        'b_excl_unique_count': len(unique_b_excl),
        'b_excl_with_pp_atom': b_excl_with_pp_atom,
        'b_excl_with_ri_atom': b_excl_with_ri_atom,
        'b_excl_with_both': b_excl_with_both,
        'b_excl_with_neither': b_excl_with_neither
    }

# Analyze both groups
line1_results = analyze_ht_group(line1_ht, "LINE-1 HT")
working_results = analyze_ht_group(working_ht, "WORKING HT")

# Compare
print("\n" + "="*60)
print("COMPARISON: Line-1 HT vs Working HT")
print("="*60)

print(f"\nDirect MIDDLE Classification:")
print(f"  PP rate: Line-1 = {line1_results['classification_pct']['PP']:.1f}%, Working = {working_results['classification_pct']['PP']:.1f}%")
print(f"  RI rate: Line-1 = {line1_results['classification_pct']['RI']:.1f}%, Working = {working_results['classification_pct']['RI']:.1f}%")
print(f"  B_EXCL rate: Line-1 = {line1_results['classification_pct']['B_EXCL']:.1f}%, Working = {working_results['classification_pct']['B_EXCL']:.1f}%")

print(f"\nB-Exclusive MIDDLE Atom Containment:")
if line1_results['b_excl_unique_count'] > 0:
    line1_ri_atom = 100 * line1_results['b_excl_with_ri_atom'] / line1_results['b_excl_unique_count']
    line1_pp_atom = 100 * line1_results['b_excl_with_pp_atom'] / line1_results['b_excl_unique_count']
else:
    line1_ri_atom = 0
    line1_pp_atom = 0

if working_results['b_excl_unique_count'] > 0:
    working_ri_atom = 100 * working_results['b_excl_with_ri_atom'] / working_results['b_excl_unique_count']
    working_pp_atom = 100 * working_results['b_excl_with_pp_atom'] / working_results['b_excl_unique_count']
else:
    working_ri_atom = 0
    working_pp_atom = 0

print(f"  Contains RI atom: Line-1 = {line1_ri_atom:.1f}%, Working = {working_ri_atom:.1f}%")
print(f"  Contains PP atom: Line-1 = {line1_pp_atom:.1f}%, Working = {working_pp_atom:.1f}%")

# If there's elevated RI atom containment in line-1, investigate
if line1_ri_atom > working_ri_atom + 5:
    print(f"\n*** ELEVATED RI ATOM CONTAINMENT IN LINE-1 B-EXCL MIDDLEs ***")
    print(f"  Line-1: {line1_ri_atom:.1f}% vs Working: {working_ri_atom:.1f}%")

# List example B-exclusive MIDDLEs with RI atoms from line-1
print("\n" + "="*60)
print("SAMPLE: Line-1 B-Exclusive MIDDLEs with RI atom containment")
print("="*60)

line1_b_excl_with_ri = []
for word in line1_ht:
    m = morph.extract(word)
    if m.middle and classify_middle(m.middle, pp_middles, ri_middles, b_exclusive_middles) == 'B_EXCL':
        ri_atoms = get_contained_atoms(m.middle, ri_middles)
        if ri_atoms:
            line1_b_excl_with_ri.append((word, m.middle, ri_atoms))

if line1_b_excl_with_ri:
    for word, middle, atoms in line1_b_excl_with_ri[:10]:
        print(f"  {word}: MIDDLE='{middle}', RI atoms: {atoms}")
else:
    print("  (None found)")

# Verdict
print("\n" + "="*60)
print("VERDICT")
print("="*60)

ri_direct = line1_results['classification']['RI']
ri_atom_diff = line1_ri_atom - working_ri_atom

if ri_direct > 0:
    verdict = "DIRECT_RI_FOUND"
    explanation = f"Line-1 HT has {ri_direct} tokens with direct RI MIDDLEs"
elif ri_atom_diff > 10:
    verdict = "RI_ATOM_ELEVATED"
    explanation = f"Line-1 HT B-exclusive MIDDLEs have elevated RI atom containment (+{ri_atom_diff:.1f}pp)"
elif ri_atom_diff > 5:
    verdict = "RI_ATOM_SLIGHT_ELEVATION"
    explanation = f"Line-1 HT B-exclusive MIDDLEs show slight RI atom elevation (+{ri_atom_diff:.1f}pp)"
else:
    verdict = "NO_RI_DERIVATION"
    explanation = "No evidence of RI derivation pathway in line-1 HT"

print(f"\n{verdict}: {explanation}")

# Key insight
b_excl_diff = line1_results['classification_pct']['B_EXCL'] - working_results['classification_pct']['B_EXCL']
if b_excl_diff > 5:
    print(f"\nKEY FINDING: Line-1 HT has MORE B-exclusive MIDDLEs (+{b_excl_diff:.1f}pp)")
    print(f"  This means line-1 draws from vocabulary unique to B, not from A vocabulary")

# Save results
results = {
    'line1_ht': line1_results,
    'working_ht': working_results,
    'comparison': {
        'pp_rate_delta': line1_results['classification_pct']['PP'] - working_results['classification_pct']['PP'],
        'b_excl_rate_delta': b_excl_diff,
        'ri_atom_containment_delta': ri_atom_diff
    },
    'verdict': verdict,
    'explanation': explanation
}

out_path = PROJECT_ROOT / 'phases' / 'B_LINE_POSITION_HT' / 'results' / 'ht_middle_composition.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
