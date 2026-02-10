"""
08_forward_bias_decomposition.py

Decompose C786's forward bias by FL subtype.

Q: Does C786's forward bias differ for hazard FL vs safe FL, or early vs late stage?
- Replicate C786 analysis stratified by hazard/safe class, FL stage
- Compute forward/same/backward ratios per stratum
- Key question: is the forward bias uniform, or does one subtype drive it?
"""
import sys
import json
import statistics
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

FL_STAGE_MAP = {
    'ii': ('INITIAL', 0.299), 'i': ('INITIAL', 0.345),
    'in': ('EARLY', 0.421),
    'r': ('MEDIAL', 0.507), 'ar': ('MEDIAL', 0.545),
    'al': ('LATE', 0.606), 'l': ('LATE', 0.618), 'ol': ('LATE', 0.643),
    'o': ('FINAL', 0.751), 'ly': ('FINAL', 0.785), 'am': ('FINAL', 0.802),
    'm': ('TERMINAL', 0.861), 'dy': ('TERMINAL', 0.908),
    'ry': ('TERMINAL', 0.913), 'y': ('TERMINAL', 0.942),
}

STAGE_ORDER = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'FINAL': 4, 'TERMINAL': 5}
STAGE_GROUP = {
    'INITIAL': 'EARLY_STAGES', 'EARLY': 'EARLY_STAGES',
    'MEDIAL': 'MEDIAL_STAGES',
    'LATE': 'LATE_STAGES', 'FINAL': 'LATE_STAGES', 'TERMINAL': 'LATE_STAGES',
}

HAZARD_CLASSES = {7, 30}
SAFE_CLASSES = {38, 40}

tx = Transcript()
morph = Morphology()

# Load class map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = {k: int(v) for k, v in class_data['token_to_class'].items()}

# Collect tokens by line
line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Build FL records per line
fl_by_line = defaultdict(list)
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            cls = token_to_class.get(t.word, -1)
            if cls in HAZARD_CLASSES:
                haz_class = 'HAZARD'
            elif cls in SAFE_CLASSES:
                haz_class = 'SAFE'
            else:
                haz_class = 'OTHER'

            stage = FL_STAGE_MAP[m.middle][0]
            fl_by_line[line_key].append({
                'middle': m.middle,
                'stage': stage,
                'stage_order': STAGE_ORDER[stage],
                'stage_group': STAGE_GROUP[stage],
                'hazard_class': haz_class,
                'idx': idx,
            })

# ============================================================
# Extract FL->FL transitions (adjacent FL pairs in same line)
# ============================================================
transitions = []
for line_key, fl_seq in fl_by_line.items():
    if len(fl_seq) < 2:
        continue
    fl_sorted = sorted(fl_seq, key=lambda x: x['idx'])
    for i in range(len(fl_sorted) - 1):
        a = fl_sorted[i]
        b = fl_sorted[i + 1]
        ord_a = a['stage_order']
        ord_b = b['stage_order']

        if ord_b > ord_a:
            direction = 'forward'
        elif ord_b < ord_a:
            direction = 'backward'
        else:
            direction = 'same'

        transitions.append({
            'from_middle': a['middle'],
            'to_middle': b['middle'],
            'from_stage': a['stage'],
            'to_stage': b['stage'],
            'from_hazard': a['hazard_class'],
            'to_hazard': b['hazard_class'],
            'from_group': a['stage_group'],
            'direction': direction,
        })

print(f"Total FL->FL transitions: {len(transitions)}")

def compute_bias(trans_list):
    """Compute forward/backward/same ratios."""
    fwd = sum(1 for t in trans_list if t['direction'] == 'forward')
    bwd = sum(1 for t in trans_list if t['direction'] == 'backward')
    same = sum(1 for t in trans_list if t['direction'] == 'same')
    total = len(trans_list)
    ratio = fwd / bwd if bwd > 0 else float('inf')
    return {
        'n': total,
        'forward': fwd,
        'backward': bwd,
        'same': same,
        'fwd_rate': round(fwd / total, 4) if total > 0 else 0,
        'bwd_rate': round(bwd / total, 4) if total > 0 else 0,
        'same_rate': round(same / total, 4) if total > 0 else 0,
        'fwd_bwd_ratio': round(ratio, 2) if ratio != float('inf') else 'inf',
    }

# ============================================================
# Global bias
# ============================================================
global_bias = compute_bias(transitions)
print(f"\nGlobal: fwd={global_bias['forward']} bwd={global_bias['backward']} "
      f"same={global_bias['same']} ratio={global_bias['fwd_bwd_ratio']}:1")

# ============================================================
# By hazard class of FIRST token in pair
# ============================================================
print(f"\n{'='*60}")
print("FORWARD BIAS BY HAZARD CLASS (of source FL)")
hazard_bias = {}
for hclass in ['HAZARD', 'SAFE', 'OTHER']:
    subset = [t for t in transitions if t['from_hazard'] == hclass]
    if len(subset) < 10:
        continue
    bias = compute_bias(subset)
    hazard_bias[hclass] = bias
    print(f"  {hclass:>8}: n={bias['n']:>4} fwd={bias['forward']:>3} "
          f"bwd={bias['backward']:>3} same={bias['same']:>3} ratio={bias['fwd_bwd_ratio']}:1")

# ============================================================
# By stage group of FIRST token
# ============================================================
print(f"\n{'='*60}")
print("FORWARD BIAS BY STAGE GROUP (of source FL)")
stage_bias = {}
for group in ['EARLY_STAGES', 'MEDIAL_STAGES', 'LATE_STAGES']:
    subset = [t for t in transitions if t['from_group'] == group]
    if len(subset) < 10:
        continue
    bias = compute_bias(subset)
    stage_bias[group] = bias
    print(f"  {group:>15}: n={bias['n']:>4} fwd={bias['forward']:>3} "
          f"bwd={bias['backward']:>3} same={bias['same']:>3} ratio={bias['fwd_bwd_ratio']}:1")

# ============================================================
# By individual stage
# ============================================================
print(f"\n{'='*60}")
print("FORWARD BIAS BY INDIVIDUAL STAGE (of source FL)")
per_stage_bias = {}
for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']:
    subset = [t for t in transitions if t['from_stage'] == stage]
    if len(subset) < 5:
        continue
    bias = compute_bias(subset)
    per_stage_bias[stage] = bias
    print(f"  {stage:>10}: n={bias['n']:>4} fwd={bias['forward']:>3} "
          f"bwd={bias['backward']:>3} same={bias['same']:>3} ratio={bias['fwd_bwd_ratio']}:1")

# ============================================================
# Cross-tabulation: hazard x direction
# ============================================================
print(f"\n{'='*60}")
print("HAZARD x DIRECTION CROSS-TAB")
for from_h in ['HAZARD', 'SAFE', 'OTHER']:
    for to_h in ['HAZARD', 'SAFE', 'OTHER']:
        subset = [t for t in transitions
                  if t['from_hazard'] == from_h and t['to_hazard'] == to_h]
        if len(subset) < 3:
            continue
        bias = compute_bias(subset)
        print(f"  {from_h:>8}->{to_h:<8}: n={bias['n']:>3} fwd={bias['forward']:>3} "
              f"bwd={bias['backward']:>3} ratio={bias['fwd_bwd_ratio']}:1")

# ============================================================
# Verdict
# ============================================================
hazard_ratio = hazard_bias.get('HAZARD', {}).get('fwd_bwd_ratio', 0)
safe_ratio = hazard_bias.get('SAFE', {}).get('fwd_bwd_ratio', 0)
other_ratio = hazard_bias.get('OTHER', {}).get('fwd_bwd_ratio', 0)

# Convert 'inf' to large number for comparison
def safe_float(v):
    return 999 if v == 'inf' else float(v)

ratios = {k: safe_float(v.get('fwd_bwd_ratio', 0)) for k, v in hazard_bias.items()}

if len(ratios) >= 2:
    max_ratio = max(ratios.values())
    min_ratio = min(ratios.values())
    ratio_spread = max_ratio / min_ratio if min_ratio > 0 else float('inf')
else:
    ratio_spread = 1.0

if ratio_spread > 3.0:
    verdict = "SUBTYPE_DRIVEN"
    explanation = (f"Forward bias varies >3x across hazard classes "
                   f"(spread={ratio_spread:.1f}x). "
                   f"Ratios: {', '.join(f'{k}={v}' for k, v in hazard_bias.items() if 'fwd_bwd_ratio' in v)}")
elif ratio_spread > 1.5:
    verdict = "MODERATELY_UNEVEN"
    explanation = f"Moderate variation across subtypes (spread={ratio_spread:.1f}x)"
else:
    verdict = "UNIFORM_BIAS"
    explanation = f"Forward bias is uniform across subtypes (spread={ratio_spread:.1f}x)"

print(f"\n{'='*60}")
print(f"VERDICT: {verdict}")
print(f"  {explanation}")

result = {
    'total_transitions': len(transitions),
    'global_bias': global_bias,
    'by_hazard_class': hazard_bias,
    'by_stage_group': stage_bias,
    'by_individual_stage': per_stage_bias,
    'ratio_spread': round(ratio_spread, 2) if ratio_spread != float('inf') else 'inf',
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "08_forward_bias_decomposition.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
