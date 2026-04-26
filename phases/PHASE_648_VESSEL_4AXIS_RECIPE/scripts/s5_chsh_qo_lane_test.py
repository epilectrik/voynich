"""
Phase 648 Step 5: Test the fire-side / vessel-side hypothesis.

Compute ch, sh, qo rates per folio alongside the o-prefix rates.
Test predictions:

USER HYPOTHESIS (fire-side / vessel-side):
- ch/sh + qo are FIRE-SIDE: should correlate with each other
- ok/ot/ol/or are VESSEL-SIDE: should correlate with each other
- Cross-block (chsh-qo vs o-prefix) should be near-zero

EXISTING ARCHITECTURE (action vs monitoring lanes):
- qo + o-prefixes are SAME LANE (energy operations): should correlate
- ch + sh are MONITORING LANE: should be distinct
- Cross-lane has structured MI=1.063 bits

The two readings predict different correlation patterns.
"""
import sys
import json
import math
sys.path.insert(0, '.')
from scripts.voynich import Transcript
from collections import defaultdict

tx = Transcript()

# Per-folio prefix counts (Currier B only)
folio_stats = defaultdict(lambda: {
    'total': 0,
    'ch': 0, 'sh': 0, 'qo': 0,
    'ok': 0, 'ot': 0, 'ol': 0, 'or': 0,
})

for t in tx.currier_b():
    f = t.folio
    folio_stats[f]['total'] += 1
    w = t.word
    # Leading-prefix detection (prefix is the leading 2 chars in our morphology)
    if w.startswith('ch'):
        folio_stats[f]['ch'] += 1
    elif w.startswith('sh'):
        folio_stats[f]['sh'] += 1
    elif w.startswith('qo'):
        folio_stats[f]['qo'] += 1
    elif len(w) >= 2 and w[0] == 'o' and w[1] in ('k','t','l','r'):
        folio_stats[f]['o' + w[1]] += 1

# Build profile: rate per folio
profile = {}
for f, s in folio_stats.items():
    if s['total'] < 30:
        continue
    profile[f] = {
        pref: s[pref] / s['total']
        for pref in ('ch','sh','qo','ok','ot','ol','or')
    }
    profile[f]['total'] = s['total']

# Pearson correlation
def pearson(xs, ys):
    n = len(xs)
    mx = sum(xs)/n; my = sum(ys)/n
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs))
    dy = math.sqrt(sum((y-my)**2 for y in ys))
    if dx*dy == 0: return float('nan')
    return num/(dx*dy)

prefixes = ['ch','sh','qo','ok','ot','ol','or']
folios = list(profile.keys())

print(f"Currier B folios profiled (>=30 tokens): {len(folios)}")
print()
print("Mean rate per prefix across folios:")
for pref in prefixes:
    mean = sum(profile[f][pref] for f in folios) / len(folios)
    print(f"  {pref}: {mean*100:5.2f}%")

print()
print("Pairwise Pearson correlation (across folios):")
print("        " + "  ".join(f"{p:>6s}" for p in prefixes))
for p1 in prefixes:
    row = [f"{p1:>4s}  "]
    for p2 in prefixes:
        if p1 == p2:
            row.append(f"{1.00:>6.2f}")
        else:
            xs = [profile[f][p1] for f in folios]
            ys = [profile[f][p2] for f in folios]
            row.append(f"{pearson(xs,ys):>+6.2f}")
    print("  ".join(row))

# Block-level summary
print()
print("="*72)
print("BLOCK SUMMARY")
print("="*72)

def block_corr(block1, block2):
    """Mean correlation between all pairs across two blocks (excluding same prefix)."""
    cs = []
    for p1 in block1:
        for p2 in block2:
            if p1 == p2: continue
            xs = [profile[f][p1] for f in folios]
            ys = [profile[f][p2] for f in folios]
            cs.append(pearson(xs, ys))
    return sum(cs)/len(cs) if cs else float('nan')

# User hypothesis blocks
fire_block = ['ch','sh','qo']
vessel_block = ['ok','ot','ol','or']

within_fire = block_corr(fire_block, fire_block)
within_vessel = block_corr(vessel_block, vessel_block)
cross_block = block_corr(fire_block, vessel_block)

print()
print("Under USER HYPOTHESIS (fire = ch/sh/qo, vessel = ok/ot/ol/or):")
print(f"  Mean within-fire correlation:   {within_fire:+.3f}")
print(f"  Mean within-vessel correlation: {within_vessel:+.3f}")
print(f"  Mean cross-block correlation:   {cross_block:+.3f}")
print(f"  Within-vs-cross differential:   {((within_fire+within_vessel)/2 - cross_block):+.3f}")
print()

# Existing architecture blocks
qo_lane = ['qo','ok','ot','ol','or']
chsh_lane = ['ch','sh']

within_qo = block_corr(qo_lane, qo_lane)
within_chsh = block_corr(chsh_lane, chsh_lane)
cross_qo_chsh = block_corr(qo_lane, chsh_lane)

print("Under EXISTING ARCHITECTURE (qo lane = qo/ok/ot/ol/or, chsh lane = ch/sh):")
print(f"  Mean within-qo-lane correlation:    {within_qo:+.3f}")
print(f"  Mean within-chsh-lane correlation:  {within_chsh:+.3f}")
print(f"  Mean cross-lane correlation:        {cross_qo_chsh:+.3f}")
print(f"  Within-vs-cross differential:       {((within_qo+within_chsh)/2 - cross_qo_chsh):+.3f}")

print()
print("="*72)
print("INTERPRETATION")
print("="*72)
print("""
The hypothesis with the LARGER within-block / cross-block differential
better partitions the data. If user hypothesis dominates, fire-side
(ch/sh/qo) and vessel-side (ok/ot/ol/or) operate as separable blocks.
If existing architecture dominates, qo travels with the o-prefixes (energy
operations) and ch/sh stand apart (monitoring).""")

# Save
with open('phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/chsh_qo_lane_test.json', 'w') as f:
    json.dump({
        'profile': profile,
        'block_correlations': {
            'user_hypothesis': {
                'within_fire': within_fire,
                'within_vessel': within_vessel,
                'cross': cross_block,
            },
            'existing_architecture': {
                'within_qo_lane': within_qo,
                'within_chsh_lane': within_chsh,
                'cross_lane': cross_qo_chsh,
            }
        }
    }, f, indent=2)
