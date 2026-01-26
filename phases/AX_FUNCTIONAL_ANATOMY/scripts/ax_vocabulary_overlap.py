"""
Script 3: AX Vocabulary Overlap

Quantify MIDDLE-level overlap between AX and each operational role.
Determine whether AX MIDDLEs are a subset, superset, or independent
vocabulary. Test whether PREFIX alone differentiates shared MIDDLEs.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
from scripts.voynich import Morphology

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
INVENTORY = BASE / 'phases/AX_FUNCTIONAL_ANATOMY/results/ax_middle_inventory.json'
RESULTS = BASE / 'phases/AX_FUNCTIONAL_ANATOMY/results'

# Load data
with open(CLASS_MAP) as f:
    class_data = json.load(f)

with open(INVENTORY) as f:
    inv_data = json.load(f)

morph = Morphology()

# Role taxonomy
ICC_CC = {10, 11, 12, 17}
ICC_EN = {8} | set(range(31, 50))
ICC_FL = {7, 30, 38, 40}
ICC_FQ = {9, 13, 23}
AX_CLASSES = {1, 2, 3, 4, 5, 6, 14, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29}

def get_role(cls_id):
    if cls_id in ICC_CC: return 'CC'
    if cls_id in ICC_EN: return 'EN'
    if cls_id in ICC_FL: return 'FL'
    if cls_id in ICC_FQ: return 'FQ'
    if cls_id in AX_CLASSES: return 'AX'
    return 'UNKNOWN'

# Build role -> MIDDLE sets from inventory
role_middles = {}
for role_name, info in inv_data['all_role_middles'].items():
    role_middles[role_name] = set(info['middles'])

ax_set = role_middles.get('AX', set())
en_set = role_middles.get('EN', set())
cc_set = role_middles.get('CC', set())
fl_set = role_middles.get('FL', set())
fq_set = role_middles.get('FQ', set())
all_operational = en_set | cc_set | fl_set | fq_set

# Pairwise overlap analysis
def overlap_analysis(set_a, name_a, set_b, name_b):
    intersection = set_a & set_b
    a_only = set_a - set_b
    b_only = set_b - set_a
    union = set_a | set_b
    jaccard = len(intersection) / len(union) if union else 0
    return {
        'intersection': len(intersection),
        'intersection_middles': sorted(intersection),
        f'{name_a}_only': len(a_only),
        f'{name_b}_only': len(b_only),
        'jaccard': round(jaccard, 4),
    }

pairwise = {
    'AX_vs_EN': overlap_analysis(ax_set, 'AX', en_set, 'EN'),
    'AX_vs_CC': overlap_analysis(ax_set, 'AX', cc_set, 'CC'),
    'AX_vs_FL': overlap_analysis(ax_set, 'AX', fl_set, 'FL'),
    'AX_vs_FQ': overlap_analysis(ax_set, 'AX', fq_set, 'FQ'),
    'AX_vs_ALL_OP': overlap_analysis(ax_set, 'AX', all_operational, 'operational'),
}

# Subset analysis
ax_in_op = ax_set & all_operational
ax_exclusive = ax_set - all_operational
is_subset = ax_set <= all_operational
is_superset = all_operational <= ax_set

# PREFIX differentiation for shared MIDDLEs
# For each MIDDLE in (AX & operational), find all tokens and their prefixes
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

shared_middles = ax_set & all_operational
prefix_analysis = []

for mid in sorted(shared_middles):
    ax_tokens = []
    nonax_tokens = []

    for tok, cls in token_to_class.items():
        m = morph.extract(tok)
        if m.middle != mid:
            continue
        role = get_role(cls)
        entry = {
            'token': tok,
            'prefix': m.prefix,
            'articulator': m.articulator,
            'class': cls,
            'role': role,
        }
        if role == 'AX':
            ax_tokens.append(entry)
        else:
            nonax_tokens.append(entry)

    ax_prefixes = set(t['prefix'] for t in ax_tokens)
    nonax_prefixes = set(t['prefix'] for t in nonax_tokens)
    overlap_prefixes = ax_prefixes & nonax_prefixes
    is_diff = len(overlap_prefixes) == 0

    # Check if articulators differentiate where prefixes overlap
    art_differentiated = False
    if overlap_prefixes:
        for pfx in overlap_prefixes:
            ax_with_pfx = [t for t in ax_tokens if t['prefix'] == pfx]
            nonax_with_pfx = [t for t in nonax_tokens if t['prefix'] == pfx]
            ax_arts = set(t['articulator'] for t in ax_with_pfx)
            nonax_arts = set(t['articulator'] for t in nonax_with_pfx)
            if ax_arts != nonax_arts and not (ax_arts & nonax_arts):
                art_differentiated = True

    prefix_analysis.append({
        'middle': mid,
        'ax_count': len(ax_tokens),
        'nonax_count': len(nonax_tokens),
        'ax_prefixes': sorted(str(p) for p in ax_prefixes),
        'nonax_prefixes': sorted(str(p) for p in nonax_prefixes),
        'prefix_overlap': sorted(str(p) for p in overlap_prefixes),
        'is_prefix_differentiated': is_diff,
        'articulator_differentiated': art_differentiated if not is_diff else None,
        'ax_roles': sorted(set(t['role'] for t in ax_tokens)),
        'nonax_roles': sorted(set(t['role'] for t in nonax_tokens)),
    })

prefix_diff_count = sum(1 for p in prefix_analysis if p['is_prefix_differentiated'])
art_diff_count = sum(1 for p in prefix_analysis
                     if not p['is_prefix_differentiated'] and p.get('articulator_differentiated'))

# Print results
print("=== AX VOCABULARY OVERLAP ===")
print(f"\nRole MIDDLE set sizes:")
for role, middles in sorted(role_middles.items()):
    print(f"  {role:5s}: {len(middles)} MIDDLEs")

print(f"\n=== PAIRWISE OVERLAP ===")
for pair, info in pairwise.items():
    print(f"  {pair}: intersection={info['intersection']}, jaccard={info['jaccard']:.3f}")

print(f"\n=== SUBSET ANALYSIS ===")
print(f"AX MIDDLEs: {len(ax_set)}")
print(f"All operational MIDDLEs: {len(all_operational)}")
print(f"AX in operational: {len(ax_in_op)} ({100*len(ax_in_op)/len(ax_set):.1f}%)")
print(f"AX exclusive: {len(ax_exclusive)} ({100*len(ax_exclusive)/len(ax_set):.1f}%)")
print(f"AX is subset of operational: {is_subset}")
print(f"Operational is subset of AX: {is_superset}")
print(f"AX-exclusive MIDDLEs: {sorted(ax_exclusive)}")

print(f"\n=== PREFIX DIFFERENTIATION FOR SHARED MIDDLEs ===")
print(f"Total shared MIDDLEs: {len(shared_middles)}")
print(f"Fully prefix-differentiated: {prefix_diff_count}/{len(prefix_analysis)} "
      f"({100*prefix_diff_count/len(prefix_analysis):.1f}%)")
print(f"Articulator-differentiated (where prefix overlaps): {art_diff_count}")

print(f"\nDetailed overlap cases:")
for p in prefix_analysis:
    if not p['is_prefix_differentiated']:
        print(f"  OVERLAP: {p['middle']:12s} ax_pfx={p['ax_prefixes']} "
              f"nonax_pfx={p['nonax_prefixes']} overlap={p['prefix_overlap']} "
              f"art_diff={p.get('articulator_differentiated')}")

print(f"\n=== KEY FINDING ===")
if len(ax_exclusive) == 0:
    print("AX MIDDLEs are a PURE SUBSET of operational MIDDLEs.")
    print("AX uses exactly the same vocabulary material, differentiated by PREFIX.")
elif len(ax_exclusive) < len(ax_set) * 0.3:
    print(f"AX MIDDLEs are MOSTLY shared ({100*len(ax_in_op)/len(ax_set):.0f}%) with operational roles.")
    print(f"Only {len(ax_exclusive)} MIDDLEs ({100*len(ax_exclusive)/len(ax_set):.0f}%) are AX-exclusive.")
    print("AX primarily re-uses operational vocabulary in different PREFIX contexts.")
else:
    print(f"AX has substantial independent vocabulary ({len(ax_exclusive)} exclusive MIDDLEs).")

# Save results
results = {
    'role_middle_counts': {role: len(mids) for role, mids in role_middles.items()},
    'pairwise_overlap': pairwise,
    'subset_analysis': {
        'ax_count': len(ax_set),
        'operational_count': len(all_operational),
        'ax_in_operational': len(ax_in_op),
        'ax_in_operational_rate': round(len(ax_in_op) / len(ax_set), 4),
        'ax_exclusive_count': len(ax_exclusive),
        'ax_exclusive_rate': round(len(ax_exclusive) / len(ax_set), 4),
        'ax_exclusive_middles': sorted(ax_exclusive),
        'is_subset': is_subset,
        'is_superset': is_superset,
    },
    'prefix_differentiation': {
        'total_shared': len(shared_middles),
        'prefix_differentiated': prefix_diff_count,
        'prefix_differentiated_rate': round(prefix_diff_count / len(prefix_analysis), 4) if prefix_analysis else 0,
        'articulator_differentiated': art_diff_count,
        'details': prefix_analysis,
    },
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'ax_vocabulary_overlap.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'ax_vocabulary_overlap.json'}")
