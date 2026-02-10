"""
03_positional_anchoring_taxonomy.py

Test whether FL MIDDLEs partition into RIGID vs FLEXIBLE positional types.

Q: Do FL MIDDLEs partition into RIGID (tight position) vs FLEXIBLE (broad spread)?
- Classify each: RIGID if std < 0.20, FLEXIBLE if std > 0.30, MODERATE otherwise
- Test correlation with stage, character composition, hazard/safe class
- Pass: Clear partition into RIGID anchors and FLEXIBLE floaters
- Fail: All MIDDLEs have similar spread
"""
import sys
import json
import statistics
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.stats import kruskal, mannwhitneyu

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

# Hazard classes from C773
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

# Build FL records
fl_records = []
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            cls = token_to_class.get(t.word, -1)
            if cls in HAZARD_CLASSES:
                hazard_class = 'HAZARD'
            elif cls in SAFE_CLASSES:
                hazard_class = 'SAFE'
            else:
                hazard_class = 'OTHER'

            fl_records.append({
                'word': t.word,
                'middle': m.middle,
                'stage': FL_STAGE_MAP[m.middle][0],
                'expected_pos': FL_STAGE_MAP[m.middle][1],
                'actual_pos': idx / (n - 1),
                'hazard_class': hazard_class,
                'token_class': cls,
            })

print(f"Total FL records: {len(fl_records)}")

# ============================================================
# Classify each MIDDLE: RIGID / MODERATE / FLEXIBLE
# ============================================================
taxonomy = {}
for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
    positions = [r['actual_pos'] for r in fl_records if r['middle'] == mid]
    if len(positions) < 10:
        continue

    arr = np.array(positions)
    std = float(np.std(arr))
    mean = float(np.mean(arr))

    if std < 0.20:
        anchor_type = 'RIGID'
    elif std > 0.30:
        anchor_type = 'FLEXIBLE'
    else:
        anchor_type = 'MODERATE'

    # Character composition
    has_y = 'y' in mid
    has_i = 'i' in mid
    has_consonant = any(c in mid for c in 'rlnm')
    has_vowel_ao = any(c in mid for c in 'ao')

    # Hazard/safe breakdown
    hazard_n = sum(1 for r in fl_records if r['middle'] == mid and r['hazard_class'] == 'HAZARD')
    safe_n = sum(1 for r in fl_records if r['middle'] == mid and r['hazard_class'] == 'SAFE')
    other_n = sum(1 for r in fl_records if r['middle'] == mid and r['hazard_class'] == 'OTHER')

    taxonomy[mid] = {
        'n': len(positions),
        'mean': round(mean, 3),
        'std': round(std, 3),
        'anchor_type': anchor_type,
        'stage': FL_STAGE_MAP[mid][0],
        'stage_order': STAGE_ORDER[FL_STAGE_MAP[mid][0]],
        'chars': {
            'has_y': has_y, 'has_i': has_i,
            'has_consonant': has_consonant, 'has_vowel_ao': has_vowel_ao,
        },
        'hazard_safe': {
            'hazard': hazard_n, 'safe': safe_n, 'other': other_n,
        },
    }

    print(f"  {mid:>4} ({FL_STAGE_MAP[mid][0]:>10}): std={std:.3f} [{anchor_type:>10}] "
          f"n={len(positions):>4} haz={hazard_n} safe={safe_n} other={other_n}")

# ============================================================
# Test correlations
# ============================================================
print(f"\n{'='*60}")
print("ANCHOR TYPE SUMMARY")

type_counts = defaultdict(int)
for v in taxonomy.values():
    type_counts[v['anchor_type']] += 1

for t in ['RIGID', 'MODERATE', 'FLEXIBLE']:
    members = [mid for mid, v in taxonomy.items() if v['anchor_type'] == t]
    print(f"  {t}: {type_counts[t]} MIDDLEs — {members}")

# Stage correlation: do RIGID MIDDLEs cluster at specific stages?
print("\nAnchor type by stage:")
stage_type = defaultdict(lambda: defaultdict(int))
for mid, v in taxonomy.items():
    stage_type[v['stage']][v['anchor_type']] += 1
for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']:
    counts = stage_type.get(stage, {})
    print(f"  {stage:>10}: R={counts.get('RIGID', 0)} M={counts.get('MODERATE', 0)} F={counts.get('FLEXIBLE', 0)}")

# Character composition correlation
print("\nAnchor type by character features:")
for feat in ['has_y', 'has_i', 'has_consonant', 'has_vowel_ao']:
    for atype in ['RIGID', 'MODERATE', 'FLEXIBLE']:
        members = [mid for mid, v in taxonomy.items() if v['anchor_type'] == atype]
        feat_count = sum(1 for mid in members if taxonomy[mid]['chars'][feat])
        pct = feat_count / len(members) * 100 if members else 0
        print(f"  {atype:>10} {feat:>15}: {feat_count}/{len(members)} ({pct:.0f}%)")

# Hazard/safe concentration
print("\nHazard/safe ratio by anchor type:")
for atype in ['RIGID', 'MODERATE', 'FLEXIBLE']:
    members = [mid for mid, v in taxonomy.items() if v['anchor_type'] == atype]
    total_h = sum(taxonomy[m]['hazard_safe']['hazard'] for m in members)
    total_s = sum(taxonomy[m]['hazard_safe']['safe'] for m in members)
    total_o = sum(taxonomy[m]['hazard_safe']['other'] for m in members)
    total = total_h + total_s + total_o
    print(f"  {atype:>10}: hazard={total_h} ({total_h/total*100:.1f}%), "
          f"safe={total_s} ({total_s/total*100:.1f}%), other={total_o} ({total_o/total*100:.1f}%)")

# ============================================================
# Verdict
# ============================================================
rigid_count = type_counts['RIGID']
flexible_count = type_counts['FLEXIBLE']
total = sum(type_counts.values())

if rigid_count >= 2 and flexible_count >= 3:
    verdict = "CLEAR_PARTITION"
    explanation = (f"Clear RIGID/FLEXIBLE partition: {rigid_count} RIGID, "
                   f"{type_counts['MODERATE']} MODERATE, {flexible_count} FLEXIBLE")
elif rigid_count >= 1 and flexible_count >= 2:
    verdict = "WEAK_PARTITION"
    explanation = (f"Weak partition: {rigid_count} RIGID, {flexible_count} FLEXIBLE, "
                   f"but most are MODERATE ({type_counts['MODERATE']})")
else:
    verdict = "NO_PARTITION"
    explanation = f"No meaningful partition: all MIDDLEs have similar spread"

print(f"\n{'='*60}")
print(f"VERDICT: {verdict}")
print(f"  {explanation}")

result = {
    'total_fl_records': len(fl_records),
    'taxonomy': taxonomy,
    'type_counts': dict(type_counts),
    'stage_type_matrix': {s: dict(c) for s, c in stage_type.items()},
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "03_positional_anchoring_taxonomy.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
