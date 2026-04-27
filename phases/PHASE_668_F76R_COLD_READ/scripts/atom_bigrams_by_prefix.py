"""
Test whether "soft" atoms (d, o, c, p, s, f, r) have stable bigram
profiles across prefix classes, or whether their co-occurrence patterns
shift by prefix context.

If atom meaning is prefix-independent: bigram profile should be similar.
If prefix acts as cipher selector: bigram profile should diverge.
"""
import sys, io, json, math
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

FIRE = {'qo', 'ch', 'sh'}
VESSEL = {'ok', 'ot', 'ol', 'or'}
SOFT_ATOMS = set('docpsfr')
UNIVERSAL = set('kehy')

prefix_bigrams = defaultdict(lambda: defaultdict(Counter))

for t in tx.currier_b():
    a = morph.atomize(t.word)
    pfx = a.prefix
    if not pfx or pfx not in (FIRE | VESSEL):
        continue

    atoms = [at[0] for at in a.atoms]
    for i, atom in enumerate(atoms):
        if atom not in SOFT_ATOMS:
            continue
        if i > 0:
            prefix_bigrams[pfx][atom]['L_' + atoms[i-1]] += 1
        if i < len(atoms) - 1:
            prefix_bigrams[pfx][atom]['R_' + atoms[i+1]] += 1

def cosine_sim(c1, c2):
    keys = set(c1.keys()) | set(c2.keys())
    if not keys:
        return 0.0
    dot = sum(c1.get(k, 0) * c2.get(k, 0) for k in keys)
    m1 = math.sqrt(sum(v**2 for v in c1.values()))
    m2 = math.sqrt(sum(v**2 for v in c2.values()))
    return dot / (m1 * m2) if m1 * m2 > 0 else 0.0

print('=== Atom bigram profile similarity across prefix classes ===\n')
print('Cosine similarity of bigram vectors (1.0 = identical profile, 0.0 = no overlap)\n')

channels = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol']

for atom in sorted(SOFT_ATOMS):
    print(f'--- Atom: {atom} ---')

    # Show top bigrams per channel
    for pfx in channels:
        bg = prefix_bigrams[pfx][atom]
        total = sum(bg.values())
        if total < 10:
            continue
        top3 = bg.most_common(4)
        top_str = ', '.join(f'{k}={v}' for k, v in top3)
        print(f'  {pfx:>3}: n={total:>4}  top: {top_str}')

    # Pairwise cosine similarity
    pairs = []
    for i, p1 in enumerate(channels):
        for p2 in channels[i+1:]:
            b1 = prefix_bigrams[p1][atom]
            b2 = prefix_bigrams[p2][atom]
            if sum(b1.values()) < 10 or sum(b2.values()) < 10:
                continue
            sim = cosine_sim(b1, b2)
            pairs.append((p1, p2, sim))

    if pairs:
        mean_sim = sum(s for _, _, s in pairs) / len(pairs)
        min_pair = min(pairs, key=lambda x: x[2])
        max_pair = max(pairs, key=lambda x: x[2])
        print(f'  Mean cosine: {mean_sim:.3f}  '
              f'min: {min_pair[0]}-{min_pair[1]}={min_pair[2]:.3f}  '
              f'max: {max_pair[0]}-{max_pair[1]}={max_pair[2]:.3f}')

    # Fire vs vessel comparison
    fire_agg = Counter()
    vessel_agg = Counter()
    for pfx in FIRE:
        fire_agg += prefix_bigrams[pfx][atom]
    for pfx in VESSEL:
        vessel_agg += prefix_bigrams[pfx][atom]
    if sum(fire_agg.values()) >= 20 and sum(vessel_agg.values()) >= 20:
        fv_sim = cosine_sim(fire_agg, vessel_agg)
        print(f'  Fire vs Vessel aggregate cosine: {fv_sim:.3f}')
    print()

# Also check universal atoms as control
print('\n=== CONTROL: Universal atoms (should show HIGH similarity) ===\n')
for atom in sorted(UNIVERSAL):
    pairs = []
    for i, p1 in enumerate(channels):
        for p2 in channels[i+1:]:
            b1 = prefix_bigrams[p1].get(atom, Counter())
            b2 = prefix_bigrams[p2].get(atom, Counter())
            if sum(b1.values()) < 10 or sum(b2.values()) < 10:
                continue
            sim = cosine_sim(b1, b2)
            pairs.append((p1, p2, sim))

    if pairs:
        mean_sim = sum(s for _, _, s in pairs) / len(pairs)
        print(f'  {atom}: mean cosine = {mean_sim:.3f} (n={len(pairs)} pairs)')
    else:
        print(f'  {atom}: insufficient data')
