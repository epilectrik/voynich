"""
Script 6: AX Prefix Derivation Test

Test whether AX class membership is entirely predictable from morphological
form (specifically the prefix). If prefix alone determines whether a token
is AX, then AX is not a functional role but a morphological category.
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
MIDDLE_CLASSES = BASE / 'phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json'
RESULTS = BASE / 'phases/AX_FUNCTIONAL_ANATOMY/results'

# Load data
with open(CLASS_MAP) as f:
    class_data = json.load(f)

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

# Extract morphology for all tokens
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

token_morph = []
for tok, cls in token_to_class.items():
    m = morph.extract(tok)
    role = get_role(cls)
    token_morph.append({
        'token': tok,
        'class': cls,
        'role': role,
        'is_ax': role == 'AX',
        'articulator': m.articulator,
        'prefix': m.prefix,
        'middle': m.middle,
        'suffix': m.suffix,
        'has_articulator': m.has_articulator,
    })

# Build prefix -> role distribution
prefix_role_dist = defaultdict(lambda: defaultdict(int))
for tm in token_morph:
    pfx = tm['prefix'] if tm['prefix'] else 'NONE'
    prefix_role_dist[pfx][tm['role']] += 1

# Build articulator -> role distribution
art_role_dist = defaultdict(lambda: defaultdict(int))
for tm in token_morph:
    art = 'has_art' if tm['has_articulator'] else 'no_art'
    art_role_dist[art][tm['role']] += 1

# Prefix-based classifier
# Strategy: for each prefix, assign the majority role
prefix_majority = {}
for pfx, roles in prefix_role_dist.items():
    best_role = max(roles, key=roles.get)
    total = sum(roles.values())
    prefix_majority[pfx] = {
        'predicted_role': best_role,
        'count': total,
        'accuracy': roles[best_role] / total,
        'distribution': dict(roles),
    }

# Evaluate classifier
correct = 0
total = len(token_morph)
confusion = defaultdict(lambda: defaultdict(int))
violations = []

for tm in token_morph:
    pfx = tm['prefix'] if tm['prefix'] else 'NONE'
    predicted = prefix_majority[pfx]['predicted_role']
    actual = tm['role']
    confusion[actual][predicted] += 1
    if predicted == actual:
        correct += 1
    else:
        violations.append({
            'token': tm['token'],
            'prefix': pfx,
            'actual_role': actual,
            'predicted_role': predicted,
            'class': tm['class'],
        })

accuracy = correct / total

# Simplify to binary: AX vs non-AX
ax_correct = 0
ax_tp = 0  # predicted AX, is AX
ax_fp = 0  # predicted AX, not AX
ax_fn = 0  # predicted non-AX, is AX
ax_tn = 0  # predicted non-AX, not AX

for tm in token_morph:
    pfx = tm['prefix'] if tm['prefix'] else 'NONE'
    predicted_ax = prefix_majority[pfx]['predicted_role'] == 'AX'
    actual_ax = tm['is_ax']

    if predicted_ax and actual_ax: ax_tp += 1
    elif predicted_ax and not actual_ax: ax_fp += 1
    elif not predicted_ax and actual_ax: ax_fn += 1
    else: ax_tn += 1

binary_accuracy = (ax_tp + ax_tn) / total
ax_precision = ax_tp / (ax_tp + ax_fp) if (ax_tp + ax_fp) > 0 else 0
ax_recall = ax_tp / (ax_tp + ax_fn) if (ax_tp + ax_fn) > 0 else 0
ax_f1 = 2 * ax_precision * ax_recall / (ax_precision + ax_recall) if (ax_precision + ax_recall) > 0 else 0

# Identify prefix categories
ax_exclusive_prefixes = []
nonax_exclusive_prefixes = []
ambiguous_prefixes = []

for pfx, info in prefix_majority.items():
    dist = info['distribution']
    has_ax = dist.get('AX', 0) > 0
    has_nonax = any(v > 0 for k, v in dist.items() if k != 'AX')

    if has_ax and not has_nonax:
        ax_exclusive_prefixes.append(pfx)
    elif not has_ax and has_nonax:
        nonax_exclusive_prefixes.append(pfx)
    else:
        ambiguous_prefixes.append(pfx)

# Same-MIDDLE-different-role analysis
# Find MIDDLEs that appear in both AX and non-AX tokens
middle_roles = defaultdict(lambda: {'AX': [], 'non_AX': []})
for tm in token_morph:
    mid = tm['middle']
    if mid:
        if tm['is_ax']:
            middle_roles[mid]['AX'].append({
                'token': tm['token'],
                'prefix': tm['prefix'],
                'class': tm['class'],
            })
        else:
            middle_roles[mid]['non_AX'].append({
                'token': tm['token'],
                'prefix': tm['prefix'],
                'class': tm['class'],
                'role': tm['role'],
            })

shared_middles = {mid: info for mid, info in middle_roles.items()
                  if info['AX'] and info['non_AX']}

# For shared middles, check prefix differentiation
prefix_diff_results = []
all_prefix_diff = True
for mid, info in sorted(shared_middles.items()):
    ax_prefixes = set(t['prefix'] for t in info['AX'])
    nonax_prefixes = set(t['prefix'] for t in info['non_AX'])
    overlap = ax_prefixes & nonax_prefixes
    is_differentiated = len(overlap) == 0
    if not is_differentiated:
        all_prefix_diff = False

    prefix_diff_results.append({
        'middle': mid,
        'ax_prefixes': sorted(str(p) for p in ax_prefixes),
        'nonax_prefixes': sorted(str(p) for p in nonax_prefixes),
        'prefix_overlap': sorted(str(p) for p in overlap),
        'is_prefix_differentiated': is_differentiated,
        'ax_token_count': len(info['AX']),
        'nonax_token_count': len(info['non_AX']),
    })

prefix_diff_count = sum(1 for r in prefix_diff_results if r['is_prefix_differentiated'])

# Print results
print("=== AX PREFIX DERIVATION TEST ===")
print(f"\nTotal classified tokens: {total}")
print(f"AX tokens: {sum(1 for t in token_morph if t['is_ax'])}")
print(f"Non-AX tokens: {sum(1 for t in token_morph if not t['is_ax'])}")

print(f"\n=== PREFIX -> ROLE MAPPING ===")
for pfx in sorted(prefix_role_dist):
    info = prefix_majority[pfx]
    dist_str = str(dict(prefix_role_dist[pfx]))
    print(f"  {pfx:8s}: {dist_str:40s} -> {info['predicted_role']} "
          f"({info['accuracy']:.1%} of {info['count']})")

print(f"\n=== MULTI-CLASS ACCURACY ===")
print(f"Accuracy: {accuracy:.1%} ({correct}/{total})")

print(f"\n=== BINARY AX vs NON-AX ===")
print(f"Binary accuracy: {binary_accuracy:.1%}")
print(f"AX Precision: {ax_precision:.3f}")
print(f"AX Recall: {ax_recall:.3f}")
print(f"AX F1: {ax_f1:.3f}")
print(f"  TP={ax_tp} FP={ax_fp} FN={ax_fn} TN={ax_tn}")

print(f"\n=== PREFIX CATEGORIES ===")
print(f"AX-exclusive prefixes ({len(ax_exclusive_prefixes)}): {sorted(ax_exclusive_prefixes)}")
print(f"Non-AX-exclusive prefixes ({len(nonax_exclusive_prefixes)}): {sorted(nonax_exclusive_prefixes)}")
print(f"Ambiguous prefixes ({len(ambiguous_prefixes)}): {sorted(ambiguous_prefixes)}")

print(f"\n=== SAME MIDDLE, DIFFERENT ROLE ===")
print(f"Shared MIDDLEs (appear in both AX and non-AX): {len(shared_middles)}")
print(f"Fully prefix-differentiated: {prefix_diff_count}/{len(prefix_diff_results)}")
print(f"All prefix-differentiated: {all_prefix_diff}")

for r in prefix_diff_results:
    diff_mark = 'DIFF' if r['is_prefix_differentiated'] else 'OVERLAP'
    print(f"  {r['middle']:12s} AX={r['ax_prefixes']} nonAX={r['nonax_prefixes']} "
          f"overlap={r['prefix_overlap']} [{diff_mark}]")

print(f"\n=== VIOLATIONS (predicted != actual) ===")
print(f"Total violations: {len(violations)}")
for v in violations[:20]:
    print(f"  {v['token']:16s} prefix={v['prefix']:6s} actual={v['actual_role']} "
          f"predicted={v['predicted_role']} class={v['class']}")

# Verdict
print(f"\n=== VERDICT ===")
if binary_accuracy > 0.90:
    print(f"AX membership is {binary_accuracy:.1%} predictable from prefix alone.")
    print("AX appears to be a MORPHOLOGICAL CATEGORY, not an independent functional role.")
elif binary_accuracy > 0.75:
    print(f"AX membership is {binary_accuracy:.1%} predictable from prefix.")
    print("AX is PARTIALLY morphologically determined with some independent structure.")
else:
    print(f"AX membership is only {binary_accuracy:.1%} predictable from prefix.")
    print("AX appears to be an INDEPENDENT FUNCTIONAL ROLE, not prefix-determined.")

# Save results
results = {
    'total_tokens': total,
    'ax_tokens': sum(1 for t in token_morph if t['is_ax']),
    'prefix_role_mapping': {
        pfx: prefix_majority[pfx] for pfx in sorted(prefix_majority)
    },
    'multiclass_accuracy': round(accuracy, 4),
    'binary_classification': {
        'accuracy': round(binary_accuracy, 4),
        'precision': round(ax_precision, 4),
        'recall': round(ax_recall, 4),
        'f1': round(ax_f1, 4),
        'tp': ax_tp, 'fp': ax_fp, 'fn': ax_fn, 'tn': ax_tn,
    },
    'prefix_categories': {
        'ax_exclusive': sorted(ax_exclusive_prefixes),
        'nonax_exclusive': sorted(nonax_exclusive_prefixes),
        'ambiguous': sorted(ambiguous_prefixes),
    },
    'same_middle_different_role': {
        'shared_middle_count': len(shared_middles),
        'prefix_differentiated_count': prefix_diff_count,
        'all_prefix_differentiated': all_prefix_diff,
        'details': prefix_diff_results,
    },
    'violations': violations[:50],
    'confusion_matrix': {k: dict(v) for k, v in confusion.items()},
    'verdict': {
        'binary_accuracy': round(binary_accuracy, 4),
        'is_morphologically_derivable': binary_accuracy > 0.90,
        'interpretation': (
            'AX is a morphological category (prefix-determined)'
            if binary_accuracy > 0.90
            else 'AX has partial independence from prefix'
            if binary_accuracy > 0.75
            else 'AX is an independent functional role'
        )
    }
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'ax_prefix_derivation_test.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'ax_prefix_derivation_test.json'}")
