"""Three-tier autocorrelation test (post-hoc to s2 killer test).

Discriminates "operational compactness" reading from "continuous-state" reading
of C1994's e-depth autocorrelation.

Per crazy-expert design:
  Tier A: near-relatives (Levenshtein <= 1 OR same MIDDLE-stem)
  Tier B: same-PREFIX, different MIDDLE
  Tier C: cross-PREFIX (genuinely operationally distinct)

Predictions:
  Compactness only:   A strong, B weak, C null
  Continuous-state:   A strong, B moderate, C weak-but-nonzero in S, ~0 in B
  Mixed:              A strong, B intermediate, C null
"""
import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()


def levenshtein(a, b):
    if len(a) < len(b):
        return levenshtein(b, a)
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        cur = [i + 1]
        for j, cb in enumerate(b):
            cur.append(min(cur[j] + 1, prev[j + 1] + 1, prev[j] + (ca != cb)))
        prev = cur
    return prev[-1]


# Build sequences with prefix/middle info per token
folio_paragraph_seq = defaultdict(list)
folio_section = {}
folio_para_counter = defaultdict(int)
for t in tx.currier_b():
    if not t.placement.startswith('P'):
        continue
    if not t.word or '*' in t.word:
        continue
    a = morph.atomize(t.word)
    m = morph.extract(t.word)
    e_depth = a.e_depth
    prefix = m.prefix or ''
    middle = m.middle or ''
    if getattr(t, 'par_initial', False):
        folio_para_counter[t.folio] += 1
    para = folio_para_counter[t.folio]
    folio_paragraph_seq[t.folio].append((para, t.word, e_depth, prefix, middle))
    folio_section[t.folio] = t.section


def classify_pair(t1, t2, mid1, mid2, pre1, pre2):
    """Classify a token pair into Tier A / B / C."""
    if t1 == t2:
        return None  # already excluded in killer
    # Tier A: near-relatives (Levenshtein <=1 OR same MIDDLE)
    if mid1 == mid2 or levenshtein(t1, t2) <= 1:
        return 'A'
    # Tier B: same PREFIX, different MIDDLE
    if pre1 == pre2 and mid1 != mid2:
        return 'B'
    # Tier C: cross-PREFIX
    return 'C'


def tier_z(seq, tier_label, n_perm=500, seed=0):
    """Compute lag-1 autocorr z for a specific tier."""
    pairs = []
    for i in range(len(seq) - 1):
        p1, t1, e1, pre1, mid1 = seq[i]
        p2, t2, e2, pre2, mid2 = seq[i + 1]
        if p1 != p2:
            continue  # within-paragraph only
        if t1 == t2:
            continue  # cross-token only
        cls = classify_pair(t1, t2, mid1, mid2, pre1, pre2)
        if cls != tier_label:
            continue
        pairs.append((e1, e2))
    if len(pairs) < 20:
        return None, None, len(pairs)
    e1s = np.array([p[0] for p in pairs], dtype=float)
    e2s = np.array([p[1] for p in pairs], dtype=float)
    if np.std(e1s) == 0 or np.std(e2s) == 0:
        return None, None, len(pairs)
    actual = float(np.corrcoef(e1s, e2s)[0, 1])

    # Marginal-preserving null on the full folio sequence
    all_e = np.array([e for p, t, e, pre, mid in seq], dtype=float)
    rng = np.random.default_rng(seed)
    null_corrs = []
    for _ in range(n_perm):
        shuf = all_e.copy()
        rng.shuffle(shuf)
        pe1, pe2 = [], []
        for i in range(len(seq) - 1):
            p1, t1, _, pre1, mid1 = seq[i]
            p2, t2, _, pre2, mid2 = seq[i + 1]
            if p1 != p2 or t1 == t2:
                continue
            cls = classify_pair(t1, t2, mid1, mid2, pre1, pre2)
            if cls != tier_label:
                continue
            pe1.append(shuf[i])
            pe2.append(shuf[i + 1])
        if len(pe1) < 2:
            null_corrs.append(0.0)
            continue
        a1, a2 = np.array(pe1), np.array(pe2)
        if np.std(a1) == 0 or np.std(a2) == 0:
            null_corrs.append(0.0)
            continue
        null_corrs.append(float(np.corrcoef(a1, a2)[0, 1]))
    null_mean = float(np.mean(null_corrs))
    null_std = float(np.std(null_corrs))
    z = (actual - null_mean) / null_std if null_std > 0 else 0.0
    return actual, z, len(pairs)


# Pair-count sanity per section
print("Pair-count breakdown by tier (corpus):")
tier_counts = defaultdict(int)
for f, seq in folio_paragraph_seq.items():
    for i in range(len(seq) - 1):
        p1, t1, e1, pre1, mid1 = seq[i]
        p2, t2, e2, pre2, mid2 = seq[i + 1]
        if p1 != p2 or t1 == t2:
            continue
        cls = classify_pair(t1, t2, mid1, mid2, pre1, pre2)
        if cls:
            tier_counts[(folio_section[f], cls)] += 1
total_pairs = sum(tier_counts.values())
for (sec, cls), n in sorted(tier_counts.items()):
    print(f"  sec={sec} tier={cls}: {n}  ({n/total_pairs*100:.1f}%)")

# Run three-tier z for each folio
print()
print("Running three-tier z per folio...")
results = []
for f, seq in folio_paragraph_seq.items():
    if len(seq) < 60:
        continue
    sec = folio_section[f]
    row = {'folio': f, 'section': sec, 'n_tokens': len(seq)}
    for tier in ['A', 'B', 'C']:
        actual, z, np_ = tier_z(seq, tier, n_perm=300, seed=hash(f + tier) % 2**31)
        row[f'lag1_{tier}'] = actual
        row[f'z_{tier}'] = z
        row[f'n_pairs_{tier}'] = np_
    results.append(row)

# Section-level summary per tier
print()
print("Mean z per tier per section (folios with sufficient pairs in tier):")
print(f"  {'sec':<3}  {'tier':<4}  {'n':>3}  {'mean_z':>8}  {'sig_z>2':>9}")
for sec in ['B', 'S', 'H', 'C', 'T']:
    for tier in ['A', 'B', 'C']:
        zs = [r[f'z_{tier}'] for r in results if r['section'] == sec and r[f'z_{tier}'] is not None]
        if not zs:
            continue
        sig = sum(1 for z in zs if z > 2)
        print(f"  {sec:<3}  {tier:<4}  {len(zs):>3}  {np.mean(zs):>+8.2f}  {sig:>3}/{len(zs):<3}")

# S vs B permutation test for each tier
print()
print("S vs B permutation test (per tier):")
for tier in ['A', 'B', 'C']:
    s_zs = [r[f'z_{tier}'] for r in results if r['section'] == 'S' and r[f'z_{tier}'] is not None]
    b_zs = [r[f'z_{tier}'] for r in results if r['section'] == 'B' and r[f'z_{tier}'] is not None]
    if not s_zs or not b_zs:
        print(f"  Tier {tier}: insufficient data")
        continue
    actual_diff = np.mean(s_zs) - np.mean(b_zs)
    pooled = list(s_zs) + list(b_zs)
    n_s = len(s_zs)
    rng = np.random.default_rng(42)
    null = []
    for _ in range(10000):
        rng.shuffle(pooled)
        null.append(np.mean(pooled[:n_s]) - np.mean(pooled[n_s:]))
    p = sum(1 for d in null if d >= actual_diff) / len(null)
    print(f"  Tier {tier}: S={np.mean(s_zs):+.2f} (n={len(s_zs)})  B={np.mean(b_zs):+.2f} (n={len(b_zs)})  diff={actual_diff:+.3f}  p={p:.4f}")

# Top folios per tier
print()
print("Top S folios per tier (z):")
for tier in ['A', 'B', 'C']:
    print(f"  Tier {tier}:")
    s_results = [(r['folio'], r[f'z_{tier}'], r[f'n_pairs_{tier}']) for r in results
                 if r['section'] == 'S' and r[f'z_{tier}'] is not None]
    for f, z, np_ in sorted(s_results, key=lambda x: -x[1])[:5]:
        print(f"    {f:8s}  z={z:+.2f}  n_pairs={np_}")

# Verdict
print()
print("="*70)
print("VERDICT")
print("="*70)

s_a = [r['z_A'] for r in results if r['section'] == 'S' and r['z_A'] is not None]
s_b_t = [r['z_B'] for r in results if r['section'] == 'S' and r['z_B'] is not None]
s_c = [r['z_C'] for r in results if r['section'] == 'S' and r['z_C'] is not None]
b_c = [r['z_C'] for r in results if r['section'] == 'B' and r['z_C'] is not None]

print(f"  S Tier A mean z: {np.mean(s_a):+.2f}")
print(f"  S Tier B mean z: {np.mean(s_b_t):+.2f}")
print(f"  S Tier C mean z: {np.mean(s_c):+.2f}")
print(f"  B Tier C mean z: {np.mean(b_c):+.2f}")
print()

# Discriminator: does Tier C light up in S where it doesn't in B?
s_c_mean = np.mean(s_c)
b_c_mean = np.mean(b_c)
s_c_sig_frac = sum(1 for z in s_c if z > 2) / len(s_c) if s_c else 0
print(f"  Tier C discriminator:")
print(f"    S mean: {s_c_mean:+.2f}, B mean: {b_c_mean:+.2f}, S frac z>2: {s_c_sig_frac*100:.1f}%")
if s_c_mean > 1.5 and abs(b_c_mean) < 0.5:
    print(f"    -> CONTINUOUS-STATE survives in non-trivial form (cross-PREFIX coupling in S, none in B)")
elif s_c_mean < 0.5 and b_c_mean < 0.5:
    print(f"    -> OPERATIONAL COMPACTNESS wins (Tier C collapses; signal was stem-locality)")
else:
    print(f"    -> MIXED (both effects contribute)")

# Save results
out = Path(__file__).resolve().parents[1] / 'results' / 'three_tier_results.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump({
        'description': 'Three-tier autocorrelation test discriminating operational compactness from continuous-state',
        'tiers': {
            'A': 'near-relatives (Levenshtein<=1 OR same MIDDLE)',
            'B': 'same-PREFIX, different MIDDLE',
            'C': 'cross-PREFIX (operationally distinct)',
        },
        'n_perm_per_folio': 300,
        'folios': results,
    }, f, indent=2, ensure_ascii=False)
print(f"\n  Saved to {out}")
