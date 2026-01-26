"""
Script 1: AX MIDDLE Inventory

Full MIDDLE-level decomposition of AX vocabulary.
For each MIDDLE used by AX classes, determine:
- Pipeline classification (PP/RI/B-exclusive)
- How many AX classes use it
- Whether operational roles share it
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
MIDDLE_CLASSES = BASE / 'phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json'
RESULTS = BASE / 'phases/AX_FUNCTIONAL_ANATOMY/results'

# Load data
with open(CLASS_MAP) as f:
    class_data = json.load(f)

with open(MIDDLE_CLASSES) as f:
    mc = json.load(f)

ri_middles = set(mc['a_exclusive_middles'])
pp_middles = set(mc['a_shared_middles'])

# Role taxonomy (ICC-authoritative + C560 correction)
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

# AX subgroups from C563
AX_INIT = {4, 5, 6, 24, 26}
AX_MED = {1, 2, 3, 14, 16, 18, 27, 28, 29}
AX_FINAL = {15, 19, 20, 21, 22, 25}

def get_subgroup(cls_id):
    if cls_id in AX_INIT: return 'AX_INIT'
    if cls_id in AX_MED: return 'AX_MED'
    if cls_id in AX_FINAL: return 'AX_FINAL'
    return None

# Build class -> middles mapping
# Use class_token_map's own token_to_class and extract middles
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Build class -> middles from the token-level data
# Need to extract middles - use the class_data if it has class_to_middles, else extract
# Check what keys are available
print("class_data keys:", list(class_data.keys()))

# Build from token_to_class using voynich Morphology for consistency
from scripts.voynich import Morphology
morph = Morphology()

# Extract middles for all classified tokens
token_to_middle = {}
for tok in token_to_class:
    m = morph.extract(tok)
    token_to_middle[tok] = m.middle if m.middle else None

# Build class -> set of middles
class_to_middles = defaultdict(set)
class_to_tokens = defaultdict(list)
for tok, cls in token_to_class.items():
    mid = token_to_middle[tok]
    if mid:
        class_to_middles[cls].add(mid)
    class_to_tokens[cls].append(tok)

# Build role -> set of middles
role_to_middles = defaultdict(set)
for cls, middles in class_to_middles.items():
    role = get_role(cls)
    role_to_middles[role].update(middles)

# AX middles inventory
ax_middles = role_to_middles['AX']
print(f"\nTotal unique AX MIDDLEs: {len(ax_middles)}")

# Classify each AX MIDDLE
per_middle = {}
for mid in sorted(ax_middles):
    # Pipeline classification
    if mid in pp_middles:
        pipeline = 'PP'
    elif mid in ri_middles:
        pipeline = 'RI'
    else:
        pipeline = 'B_exclusive'

    # Which AX classes use it
    ax_cls_using = [cls for cls in AX_CLASSES if mid in class_to_middles.get(cls, set())]

    # Which AX subgroups
    subgroups = list(set(get_subgroup(c) for c in ax_cls_using if get_subgroup(c)))

    # Which non-AX roles also use it
    non_ax_roles = []
    non_ax_classes = []
    for cls, middles in class_to_middles.items():
        if cls not in AX_CLASSES and mid in middles:
            role = get_role(cls)
            if role not in non_ax_roles:
                non_ax_roles.append(role)
            non_ax_classes.append(cls)

    per_middle[mid] = {
        'pipeline_class': pipeline,
        'ax_class_count': len(ax_cls_using),
        'ax_classes': sorted(ax_cls_using),
        'ax_subgroups': sorted(subgroups),
        'non_ax_roles': sorted(set(non_ax_roles)),
        'non_ax_classes': sorted(non_ax_classes),
        'is_shared_with_operational': len(non_ax_roles) > 0
    }

# Pipeline breakdown
pipeline_counts = defaultdict(list)
for mid, info in per_middle.items():
    pipeline_counts[info['pipeline_class']].append(mid)

# Cross-role summary
shared_with_en = [m for m, i in per_middle.items() if 'EN' in i['non_ax_roles']]
shared_with_cc = [m for m, i in per_middle.items() if 'CC' in i['non_ax_roles']]
shared_with_fl = [m for m, i in per_middle.items() if 'FL' in i['non_ax_roles']]
shared_with_fq = [m for m, i in per_middle.items() if 'FQ' in i['non_ax_roles']]
ax_only = [m for m, i in per_middle.items() if not i['is_shared_with_operational']]

# Multi-class distribution
class_count_dist = defaultdict(int)
for mid, info in per_middle.items():
    n = info['ax_class_count']
    if n >= 3:
        class_count_dist['3+'] += 1
    else:
        class_count_dist[str(n)] += 1

# Per-AX-class MIDDLE inventory
per_class = {}
for cls in sorted(AX_CLASSES):
    middles = sorted(class_to_middles.get(cls, set()))
    tokens = class_to_tokens.get(cls, [])
    pp_count = sum(1 for m in middles if m in pp_middles)
    ri_count = sum(1 for m in middles if m in ri_middles)
    bx_count = sum(1 for m in middles if m not in pp_middles and m not in ri_middles)

    # Check which middles are shared with non-AX
    shared_count = sum(1 for m in middles if per_middle.get(m, {}).get('is_shared_with_operational', False))

    per_class[str(cls)] = {
        'token_count': len(tokens),
        'middle_count': len(middles),
        'middles': middles,
        'subgroup': get_subgroup(cls),
        'pp_middles': pp_count,
        'ri_middles': ri_count,
        'b_exclusive_middles': bx_count,
        'shared_with_operational': shared_count
    }

# Print summary
print(f"\n=== AX MIDDLE INVENTORY ===")
print(f"Total AX MIDDLEs: {len(ax_middles)}")
print(f"  PP (shared with A): {len(pipeline_counts.get('PP', []))}")
print(f"  RI (A-exclusive): {len(pipeline_counts.get('RI', []))}")
print(f"  B-exclusive: {len(pipeline_counts.get('B_exclusive', []))}")

print(f"\n=== CROSS-ROLE SHARING ===")
print(f"AX-only MIDDLEs: {len(ax_only)}")
print(f"Shared with any operational role: {len(ax_middles) - len(ax_only)}")
print(f"  Shared with EN: {len(shared_with_en)}")
print(f"  Shared with CC: {len(shared_with_cc)}")
print(f"  Shared with FL: {len(shared_with_fl)}")
print(f"  Shared with FQ: {len(shared_with_fq)}")

print(f"\n=== PER-CLASS SUMMARY ===")
for cls in sorted(AX_CLASSES):
    info = per_class[str(cls)]
    print(f"  Class {cls:2d} ({info['subgroup']:8s}): {info['middle_count']:2d} MIDDLEs "
          f"(PP={info['pp_middles']}, RI={info['ri_middles']}, "
          f"B_ex={info['b_exclusive_middles']}, shared_op={info['shared_with_operational']})")

print(f"\n=== AX-ONLY MIDDLEs ===")
for m in sorted(ax_only):
    info = per_middle[m]
    print(f"  {m:12s} pipeline={info['pipeline_class']:12s} classes={info['ax_classes']}")

print(f"\n=== SHARED MIDDLEs (used by AX + operational) ===")
shared = [m for m in sorted(per_middle) if per_middle[m]['is_shared_with_operational']]
for m in shared:
    info = per_middle[m]
    print(f"  {m:12s} pipeline={info['pipeline_class']:12s} "
          f"ax_classes={info['ax_classes']} non_ax={info['non_ax_roles']}")

# Save results
results = {
    'ax_middle_count': len(ax_middles),
    'pipeline_breakdown': {
        k: {'count': len(v), 'middles': sorted(v)}
        for k, v in pipeline_counts.items()
    },
    'per_middle': per_middle,
    'cross_role_summary': {
        'ax_only_middles': len(ax_only),
        'ax_only_list': sorted(ax_only),
        'shared_with_nonax': len(ax_middles) - len(ax_only),
        'shared_with_EN': len(shared_with_en),
        'shared_with_CC': len(shared_with_cc),
        'shared_with_FL': len(shared_with_fl),
        'shared_with_FQ': len(shared_with_fq),
        'shared_EN_list': sorted(shared_with_en),
        'shared_CC_list': sorted(shared_with_cc),
        'shared_FL_list': sorted(shared_with_fl),
        'shared_FQ_list': sorted(shared_with_fq),
    },
    'multi_class_distribution': dict(class_count_dist),
    'per_class': per_class,
    'all_role_middles': {
        role: {'count': len(middles), 'middles': sorted(middles)}
        for role, middles in role_to_middles.items()
    }
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'ax_middle_inventory.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'ax_middle_inventory.json'}")
