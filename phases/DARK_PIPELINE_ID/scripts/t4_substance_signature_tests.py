"""
Three tests to determine whether dark MIDDLEs carry substance-specific
PREFIX signatures or just reflect their host folio's operational profile.

T4a: Does eet's PREFIX profile differ from its host folios' PREFIX profiles?
     If eet is always sh/ch even on qo-dominant folios, it's selecting
     into specific channels, not riding the baseline.

T4b: Do atom-similar dark MIDDLEs have different PREFIX profiles?
     If eet, eek, eed have DIFFERENT PREFIX signatures despite similar
     atoms, the referent (not the atom composition) drives the PREFIX.

T4c: Individual-level PREFIX concentration test.
     Do individual dark MIDDLEs have more concentrated PREFIX profiles
     than individual bridge MIDDLEs at matched frequency?
     (The T1 aggregate version failed; this tests per-MIDDLE.)
"""

import sys, os, io, json, math, random
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES

tx = Transcript()
morph = Morphology()

with open(ROOT / 'data' / 'dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

from scripts.voynich import load_middle_classes
ri_middles, pp_middles = load_middle_classes()
bridge_set = pp_middles - dp_set

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]

# ═══ PRECOMPUTE ═══
# Per-folio PREFIX profile (all tokens)
folio_pre_profile = defaultdict(Counter)
# Per-MIDDLE PREFIX profile
mid_pre_profile = defaultdict(Counter)
mid_total = Counter()

for t in all_b:
    m = morph.extract(t.word)
    pre = m.prefix or 'BARE'
    folio_pre_profile[t.folio][pre] += 1
    if m.middle:
        mid_pre_profile[m.middle][pre] += 1
        mid_total[m.middle] += 1

# Normalize folio profiles to proportions
def normalize(counter):
    total = sum(counter.values())
    if total == 0:
        return {}
    return {k: v/total for k, v in counter.items()}

def cosine_sim(d1, d2):
    keys = set(d1.keys()) | set(d2.keys())
    dot = sum(d1.get(k, 0) * d2.get(k, 0) for k in keys)
    n1 = sum(v**2 for v in d1.values()) ** 0.5
    n2 = sum(v**2 for v in d2.values()) ** 0.5
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)

def concentration(counter):
    total = sum(counter.values())
    if total == 0:
        return 0.0
    return max(counter.values()) / total


# ═══ T4a: eet PREFIX profile vs host folio profiles ═══
print("=" * 100)
print("T4a: Does eet SELECT into specific PREFIX channels?")
print("     Compare eet's PREFIX profile to its host folios' baseline")
print("=" * 100)

test_mids = ['eet', 'ksh', 'lsh']

for test_mid in test_mids:
    atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in test_mid)
    mid_profile = normalize(mid_pre_profile[test_mid])

    # Which folios does it appear on?
    mid_folios = set()
    for t in all_b:
        m = morph.extract(t.word)
        if m.middle == test_mid:
            mid_folios.add(t.folio)

    if not mid_folios:
        continue

    # Average folio PREFIX profile across those folios
    avg_folio_profile = Counter()
    for f in mid_folios:
        for pre, ct in folio_pre_profile[f].items():
            avg_folio_profile[pre] += ct
    avg_folio_norm = normalize(avg_folio_profile)

    # Cosine similarity between dark MIDDLE profile and host folio average
    cos = cosine_sim(mid_profile, avg_folio_norm)

    # Key PREFIX comparisons
    print(f"\n  {test_mid} ({atoms}) on {len(mid_folios)} folios:")
    print(f"    Cosine similarity (mid profile vs host folio avg): {cos:.3f}")
    print(f"    {'(SIMILAR = riding baseline)' if cos > 0.85 else '(DIFFERENT = selecting into channels)' if cos < 0.7 else '(MODERATE)'}")

    # Show top prefixes side by side
    all_pres = sorted(set(list(mid_profile.keys()) + list(avg_folio_norm.keys())),
                      key=lambda p: -(mid_profile.get(p, 0) + avg_folio_norm.get(p, 0)))
    print(f"    {'PREFIX':>8s} {'dark mid%':>10s} {'folio avg%':>11s} {'ratio':>7s}")
    print(f"    {'-'*40}")
    for pre in all_pres[:10]:
        mp = 100 * mid_profile.get(pre, 0)
        fp = 100 * avg_folio_norm.get(pre, 0)
        ratio = mp / fp if fp > 0 else 99.9
        marker = ' ***' if ratio > 2.0 or ratio < 0.5 else ''
        print(f"    {pre:>8s} {mp:10.1f} {fp:11.1f} {ratio:7.2f}{marker}")


# ═══ T4b: Atom-similar dark MIDDLEs with different PREFIX profiles ═══
print("\n\n" + "=" * 100)
print("T4b: Do atom-similar dark MIDDLEs have DIFFERENT PREFIX profiles?")
print("     If atoms determine PREFIX, similar atoms = similar profiles")
print("     If referent determines PREFIX, similar atoms can differ")
print("=" * 100)

# Find e-initial dark MIDDLEs with 5+ tokens
e_dark = []
for mid in dp_set:
    if mid and mid[0] == 'e' and mid_total[mid] >= 5:
        profile = normalize(mid_pre_profile[mid])
        e_dark.append((mid, profile, mid_total[mid]))

e_dark.sort(key=lambda x: -x[2])

print(f"\n  e-initial dark MIDDLEs with 5+ tokens: {len(e_dark)}")
print(f"\n  {'MIDDLE':>8s} {'N':>4s} {'sh%':>5s} {'ch%':>5s} {'qo%':>5s} {'ok%':>5s} {'BARE%':>6s} {'TopPre':>8s} {'Conc':>5s} {'Atoms':>25s}")
print(f"  {'-'*95}")

for mid, profile, n in e_dark:
    atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in mid)
    sh_pct = 100 * profile.get('sh', 0)
    ch_pct = 100 * profile.get('ch', 0)
    qo_pct = 100 * profile.get('qo', 0)
    ok_pct = 100 * profile.get('ok', 0)
    bare_pct = 100 * profile.get('BARE', 0)
    top_pre = max(profile, key=profile.get) if profile else '?'
    conc = concentration(mid_pre_profile[mid])
    print(f"  {mid:>8s} {n:4d} {sh_pct:5.1f} {ch_pct:5.1f} {qo_pct:5.1f} {ok_pct:5.1f} {bare_pct:6.1f} {top_pre:>8s} {conc:5.2f} {atoms:>25s}")

# Pairwise cosine similarity between e-initial dark MIDDLEs
if len(e_dark) >= 2:
    print(f"\n  Pairwise cosine similarity between e-initial dark MIDDLEs:")
    pairs = []
    for i in range(len(e_dark)):
        for j in range(i+1, len(e_dark)):
            cos = cosine_sim(e_dark[i][1], e_dark[j][1])
            pairs.append((e_dark[i][0], e_dark[j][0], cos))
    pairs.sort(key=lambda x: x[2])

    print(f"    Most DIFFERENT pairs (lowest cosine):")
    for m1, m2, cos in pairs[:5]:
        a1 = '.'.join(ATOM_GLOSSES.get(c, '?') for c in m1)
        a2 = '.'.join(ATOM_GLOSSES.get(c, '?') for c in m2)
        print(f"      {m1}({a1}) vs {m2}({a2}): cos={cos:.3f}")

    print(f"    Most SIMILAR pairs (highest cosine):")
    for m1, m2, cos in pairs[-5:]:
        a1 = '.'.join(ATOM_GLOSSES.get(c, '?') for c in m1)
        a2 = '.'.join(ATOM_GLOSSES.get(c, '?') for c in m2)
        print(f"      {m1}({a1}) vs {m2}({a2}): cos={cos:.3f}")

    mean_cos = sum(c for _, _, c in pairs) / len(pairs)
    print(f"\n    Mean pairwise cosine: {mean_cos:.3f}")
    print(f"    {'DIVERSE PREFIX profiles (supports referent model)' if mean_cos < 0.6 else 'SIMILAR PREFIX profiles (supports operational model)'}")

# Also do k-initial for comparison
k_dark = []
for mid in dp_set:
    if mid and mid[0] == 'k' and mid_total[mid] >= 5:
        profile = normalize(mid_pre_profile[mid])
        k_dark.append((mid, profile, mid_total[mid]))

if k_dark:
    k_dark.sort(key=lambda x: -x[2])
    print(f"\n  k-initial dark MIDDLEs with 5+ tokens: {len(k_dark)}")
    print(f"  {'MIDDLE':>8s} {'N':>4s} {'qo%':>5s} {'sh%':>5s} {'ch%':>5s} {'BARE%':>6s} {'TopPre':>8s} {'Conc':>5s}")
    print(f"  {'-'*55}")
    for mid, profile, n in k_dark:
        qo_pct = 100 * profile.get('qo', 0)
        sh_pct = 100 * profile.get('sh', 0)
        ch_pct = 100 * profile.get('ch', 0)
        bare_pct = 100 * profile.get('BARE', 0)
        top_pre = max(profile, key=profile.get) if profile else '?'
        conc = concentration(mid_pre_profile[mid])
        print(f"  {mid:>8s} {n:4d} {qo_pct:5.1f} {sh_pct:5.1f} {ch_pct:5.1f} {bare_pct:6.1f} {top_pre:>8s} {conc:5.2f}")


# ═══ T4c: Individual-level PREFIX concentration ═══
print("\n\n" + "=" * 100)
print("T4c: Individual dark MIDDLEs vs individual bridge MIDDLEs")
print("     Frequency-matched, per-MIDDLE concentration comparison")
print("=" * 100)

# For each dark MIDDLE, find bridge MIDDLEs in same frequency band
# Compare their concentrations INDIVIDUALLY
MIN_TOK = 5

dark_items = [(mid, concentration(mid_pre_profile[mid]), mid_total[mid])
              for mid in dp_set if mid_total[mid] >= MIN_TOK]
bridge_items = [(mid, concentration(mid_pre_profile[mid]), mid_total[mid])
                for mid in bridge_set if mid_total[mid] >= MIN_TOK]

# For each frequency band, compare dark vs bridge
bands = [(5, 10), (10, 20), (20, 50), (50, 100), (100, 500)]

print(f"\n  {'Band':>10s} {'N_dark':>7s} {'N_bridge':>9s} {'Dark conc':>10s} {'Bridge conc':>12s} {'Delta':>7s}")
print(f"  {'-'*60}")

for lo, hi in bands:
    d_concs = [c for _, c, n in dark_items if lo <= n < hi]
    b_concs = [c for _, c, n in bridge_items if lo <= n < hi]
    if d_concs and b_concs:
        d_mean = sum(d_concs) / len(d_concs)
        b_mean = sum(b_concs) / len(b_concs)
        delta = d_mean - b_mean
        print(f"  {lo:>4d}-{hi:<4d} {len(d_concs):>7d} {len(b_concs):>9d} {d_mean:>10.3f} {b_mean:>12.3f} {delta:>+7.3f}")

# Overall paired comparison: for each dark MIDDLE, find closest-frequency bridge
# and compare concentrations
wins = 0
losses = 0
ties = 0
for mid, d_conc_val, d_n in dark_items:
    # Find bridge MIDDLE closest in frequency
    best_bridge = None
    best_dist = float('inf')
    for b_mid, b_conc_val, b_n in bridge_items:
        dist = abs(d_n - b_n)
        if dist < best_dist:
            best_dist = dist
            best_bridge = (b_mid, b_conc_val, b_n)
    if best_bridge:
        if d_conc_val > best_bridge[1] + 0.01:
            wins += 1
        elif d_conc_val < best_bridge[1] - 0.01:
            losses += 1
        else:
            ties += 1

total_paired = wins + losses + ties
print(f"\n  Paired comparison (dark vs closest-frequency bridge):")
print(f"    Dark MORE concentrated: {wins}/{total_paired} ({100*wins/total_paired:.0f}%)")
print(f"    Bridge MORE concentrated: {losses}/{total_paired} ({100*losses/total_paired:.0f}%)")
print(f"    Tied (within 0.01): {ties}/{total_paired} ({100*ties/total_paired:.0f}%)")

# Sign test
from math import comb
if wins + losses > 0:
    n_test = wins + losses
    p_sign = sum(comb(n_test, k) * 0.5**n_test for k in range(max(wins, losses), n_test + 1))
    print(f"    Sign test p = {p_sign:.4f} ({'SIGNIFICANT' if p_sign < 0.05 else 'NOT SIGNIFICANT'})")


# ═══ VERDICT ═══
print("\n\n" + "=" * 100)
print("VERDICT")
print("=" * 100)
