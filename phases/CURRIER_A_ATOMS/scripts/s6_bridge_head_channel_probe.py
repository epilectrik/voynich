#!/usr/bin/env python3
"""
s6_bridge_head_channel_probe.py — Probe whether bridge MIDDLE HEAD-channel
features create specific A-to-B folio links.

Background:
  - s5 tested bridge MIDDLE Jaccard overlap: p=1.0 (no specific links)
  - C1860: A->B bridge is FEATURE-CHANNELED through HEAD atoms
    (head_e rho=0.675, head_o rho=0.617)
  - C1861: HEAD redistribution is non-random (chi2=115, V=0.675)
  - C1507: A selects o-HEAD/headless, B selects e/k-HEAD
  - C1867: 4 parallel HEAD channels

Question: Does characterizing A folios by their bridge MIDDLE HEAD composition
predict B folio operational profiles better than raw Jaccard?

Tests:
  1. HEAD-channel cosine similarity (6D vector per folio)
  2. Per-channel Spearman correlation
  3. Specificity permutation test (1000 shuffles)
  4. e_depth channel correlation
"""

import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

import math
import numpy as np
from collections import defaultdict, Counter
from scipy import stats

from scripts.voynich import Transcript, Morphology

# ── Data loading ──────────────────────────────────────────────
tx = Transcript()
morph = Morphology()

# Build DataFrame-like structures from token iterators
HEAD_CHANNELS = ['a', 'e', 'o', 'k', 't', 'headless']
MIN_BRIDGE_TOKENS = 10  # Skip folios with too few bridge tokens

# Collect tokens by folio for A and B
a_tokens = defaultdict(list)  # folio -> [word, ...]
b_tokens = defaultdict(list)

for tok in tx.currier_a():
    a_tokens[tok.folio].append(tok.word)

for tok in tx.currier_b():
    b_tokens[tok.folio].append(tok.word)

print(f"A folios: {len(a_tokens)}, B folios: {len(b_tokens)}")

# ── Step 1: Extract MIDDLEs, identify bridge MIDDLEs ─────────
a_middles_by_folio = defaultdict(list)  # folio -> [(word, middle), ...]
b_middles_by_folio = defaultdict(list)

all_a_middles = set()
all_b_middles = set()

for folio, words in a_tokens.items():
    for w in words:
        m = morph.extract(w)
        if m.middle and m.middle != '_EMPTY_':
            a_middles_by_folio[folio].append((w, m.middle))
            all_a_middles.add(m.middle)

for folio, words in b_tokens.items():
    for w in words:
        m = morph.extract(w)
        if m.middle and m.middle != '_EMPTY_':
            b_middles_by_folio[folio].append((w, m.middle))
            all_b_middles.add(m.middle)

bridge_middles = all_a_middles & all_b_middles
print(f"Unique A MIDDLEs: {len(all_a_middles)}, B MIDDLEs: {len(all_b_middles)}, Bridge: {len(bridge_middles)}")

# ── Step 2: Build HEAD-channel profiles per folio ────────────

def get_head_channel(word):
    """Get HEAD channel for a word: a, e, o, k, t, or headless."""
    aa = morph.atomize(word)
    h = aa.head
    if h is None:
        return 'headless'
    return h

def build_head_profile(folio_middles, bridge_set):
    """Build 6D HEAD-channel distribution vector for bridge tokens on a folio.
    Returns (vector, count) where vector is normalized fractions."""
    counts = Counter()
    total = 0
    for word, middle in folio_middles:
        if middle in bridge_set:
            ch = get_head_channel(word)
            counts[ch] += 1
            total += 1
    if total < MIN_BRIDGE_TOKENS:
        return None, total
    vec = np.array([counts.get(ch, 0) / total for ch in HEAD_CHANNELS])
    return vec, total


a_profiles = {}  # folio -> (vec, count)
b_profiles = {}

for folio, mids in a_middles_by_folio.items():
    vec, cnt = build_head_profile(mids, bridge_middles)
    if vec is not None:
        a_profiles[folio] = (vec, cnt)

for folio, mids in b_middles_by_folio.items():
    vec, cnt = build_head_profile(mids, bridge_middles)
    if vec is not None:
        b_profiles[folio] = (vec, cnt)

print(f"\nA folios with >= {MIN_BRIDGE_TOKENS} bridge tokens: {len(a_profiles)}")
print(f"B folios with >= {MIN_BRIDGE_TOKENS} bridge tokens: {len(b_profiles)}")

# ── Cosine similarity function ────────────────────────────────
def cosine_sim(a, b):
    dot = np.dot(a, b)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

# ── Test 1: HEAD-channel cosine for recipe B folios ──────────
print("\n" + "="*70)
print("TEST 1: HEAD-channel cosine similarity to recipe B folios")
print("="*70)

recipe_folios = ['f75r', 'f76r', 'f77v', 'f84r']
test1_results = {}

for bf in recipe_folios:
    if bf not in b_profiles:
        print(f"  {bf}: not enough bridge tokens, skipping")
        continue
    bvec, bcnt = b_profiles[bf]
    print(f"\n  {bf} (n={bcnt}) HEAD profile: " +
          ", ".join(f"{ch}={bvec[i]:.3f}" for i, ch in enumerate(HEAD_CHANNELS)))

    # Compute cosine to all A folios
    sims = []
    for af, (avec, acnt) in sorted(a_profiles.items()):
        sim = cosine_sim(avec, bvec)
        sims.append((af, sim, acnt))
    sims.sort(key=lambda x: -x[1])

    print(f"  Top 5 A-folio matches:")
    match_list = []
    for af, sim, acnt in sims[:5]:
        avec = a_profiles[af][0]
        print(f"    {af} (n={acnt}): cosine={sim:.4f}  HEAD: " +
              ", ".join(f"{ch}={avec[i]:.3f}" for i, ch in enumerate(HEAD_CHANNELS)))
        match_list.append({'folio': af, 'cosine': round(sim, 4), 'n': acnt})

    # Also show worst match for context
    worst = sims[-1]
    print(f"  Worst: {worst[0]} cosine={worst[1]:.4f}")

    test1_results[bf] = {
        'n_bridge_tokens': bcnt,
        'head_profile': {ch: round(bvec[i], 4) for i, ch in enumerate(HEAD_CHANNELS)},
        'top5_matches': match_list,
        'worst_cosine': round(worst[1], 4),
        'mean_cosine': round(np.mean([s[1] for s in sims]), 4),
        'std_cosine': round(np.std([s[1] for s in sims]), 4),
    }

# ── Test 2: Per-channel Spearman correlation ─────────────────
print("\n" + "="*70)
print("TEST 2: Per-channel Spearman correlation (A-folio rate vs best-B rate)")
print("="*70)

# For each A folio, find best-matching B folio by cosine
a_best_b = {}
for af, (avec, _) in a_profiles.items():
    best_bf = None
    best_sim = -1
    for bf, (bvec, _) in b_profiles.items():
        sim = cosine_sim(avec, bvec)
        if sim > best_sim:
            best_sim = sim
            best_bf = bf
    a_best_b[af] = best_bf

# Now for each HEAD channel, correlate A-folio rate with its best-B-folio rate
test2_results = {}
shared_a_folios = [af for af in a_profiles if a_best_b[af] in b_profiles]

for i, ch in enumerate(HEAD_CHANNELS):
    a_rates = [a_profiles[af][0][i] for af in shared_a_folios]
    b_rates = [b_profiles[a_best_b[af]][0][i] for af in shared_a_folios]

    if len(set(a_rates)) < 3 or len(set(b_rates)) < 3:
        print(f"  {ch:>8s}: insufficient variation (skipped)")
        test2_results[ch] = {'rho': None, 'p': None, 'note': 'insufficient variation'}
        continue

    rho, p = stats.spearmanr(a_rates, b_rates)
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  {ch:>8s}: rho={rho:+.4f}  p={p:.4f} {sig}")
    test2_results[ch] = {'rho': round(rho, 4), 'p': round(p, 4)}

# Also do a global correlation: all A-folio channels vs all B-folio channels
print("\n  Global correlation (all A vs all B folios, all channels):")
# For every (A folio, B folio) pair, correlate their HEAD profiles
all_a_vecs = np.array([a_profiles[af][0] for af in sorted(a_profiles)])
all_b_vecs = np.array([b_profiles[bf][0] for bf in sorted(b_profiles)])

# Mean profiles
mean_a = all_a_vecs.mean(axis=0)
mean_b = all_b_vecs.mean(axis=0)
print(f"  Mean A profile: " + ", ".join(f"{ch}={mean_a[i]:.3f}" for i, ch in enumerate(HEAD_CHANNELS)))
print(f"  Mean B profile: " + ", ".join(f"{ch}={mean_b[i]:.3f}" for i, ch in enumerate(HEAD_CHANNELS)))

# Channel-level correlation across the 6 channels between mean A and mean B
rho_mean, p_mean = stats.spearmanr(mean_a, mean_b)
print(f"  Mean profile Spearman: rho={rho_mean:+.4f}, p={p_mean:.4f}")

# ── Test 3: Specificity permutation test ─────────────────────
print("\n" + "="*70)
print("TEST 3: Specificity permutation (is best A-B cosine better than chance?)")
print("="*70)

N_PERM = 1000
a_folio_list = sorted(a_profiles.keys())
b_folio_list = sorted(b_profiles.keys())
a_vecs = np.array([a_profiles[f][0] for f in a_folio_list])
b_vecs = np.array([b_profiles[f][0] for f in b_folio_list])

# Observed: max cosine for each B folio to any A folio
obs_max_cosines = {}
for j, bf in enumerate(b_folio_list):
    sims = [cosine_sim(a_vecs[i], b_vecs[j]) for i in range(len(a_folio_list))]
    obs_max_cosines[bf] = max(sims)

# Global observed statistic: mean of max cosines
obs_stat = np.mean(list(obs_max_cosines.values()))
print(f"  Observed mean-of-max-cosine: {obs_stat:.4f}")

# Permutation: shuffle A folio labels
np.random.seed(42)
null_stats = []
for _ in range(N_PERM):
    perm_idx = np.random.permutation(len(a_folio_list))
    perm_a_vecs = a_vecs[perm_idx]
    perm_maxes = []
    for j in range(len(b_folio_list)):
        sims = [cosine_sim(perm_a_vecs[i], b_vecs[j]) for i in range(len(a_folio_list))]
        perm_maxes.append(max(sims))
    null_stats.append(np.mean(perm_maxes))

null_stats = np.array(null_stats)
p_perm = np.mean(null_stats >= obs_stat)
print(f"  Null mean: {null_stats.mean():.4f} +/- {null_stats.std():.4f}")
print(f"  p-value (permutation): {p_perm:.4f}")
print(f"  z-score: {(obs_stat - null_stats.mean()) / null_stats.std():.2f}")

test3_results = {
    'observed_mean_max_cosine': round(obs_stat, 4),
    'null_mean': round(float(null_stats.mean()), 4),
    'null_std': round(float(null_stats.std()), 4),
    'p_value': round(float(p_perm), 4),
    'z_score': round(float((obs_stat - null_stats.mean()) / null_stats.std()), 2),
    'n_permutations': N_PERM,
}

# ── Test 4: e_depth channel ──────────────────────────────────
print("\n" + "="*70)
print("TEST 4: e_depth channel (does A-side e_depth predict B-side?)")
print("="*70)

def compute_edepth_profile(folio_middles, bridge_set):
    """Mean e_depth for bridge tokens on a folio."""
    depths = []
    for word, middle in folio_middles:
        if middle in bridge_set:
            aa = morph.atomize(word)
            depths.append(aa.e_depth)
    if len(depths) < MIN_BRIDGE_TOKENS:
        return None, len(depths)
    return np.mean(depths), len(depths)

a_edepth = {}
b_edepth = {}

for folio, mids in a_middles_by_folio.items():
    val, cnt = compute_edepth_profile(mids, bridge_middles)
    if val is not None:
        a_edepth[folio] = val

for folio, mids in b_middles_by_folio.items():
    val, cnt = compute_edepth_profile(mids, bridge_middles)
    if val is not None:
        b_edepth[folio] = val

print(f"  A folios with e_depth data: {len(a_edepth)}")
print(f"  B folios with e_depth data: {len(b_edepth)}")

# Cross-correlation: for each A folio, find best-B by cosine, correlate e_depths
shared = [af for af in a_edepth if af in a_best_b and a_best_b[af] in b_edepth]
if len(shared) >= 5:
    a_ed = [a_edepth[af] for af in shared]
    b_ed = [b_edepth[a_best_b[af]] for af in shared]
    rho_ed, p_ed = stats.spearmanr(a_ed, b_ed)
    print(f"  e_depth correlation (A vs best-B match): rho={rho_ed:+.4f}, p={p_ed:.4f}")
else:
    rho_ed, p_ed = None, None
    print(f"  Not enough shared folios ({len(shared)}) for correlation")

# Also: global A mean e_depth vs global B mean e_depth
a_mean_ed = np.mean(list(a_edepth.values()))
b_mean_ed = np.mean(list(b_edepth.values()))
print(f"  Mean e_depth: A={a_mean_ed:.3f}, B={b_mean_ed:.3f}")

# All-pairs: every A folio vs every B folio
a_ed_all = np.array([a_edepth[f] for f in sorted(a_edepth)])
b_ed_all = np.array([b_edepth[f] for f in sorted(b_edepth)])
print(f"  A e_depth range: [{a_ed_all.min():.3f}, {a_ed_all.max():.3f}]")
print(f"  B e_depth range: [{b_ed_all.min():.3f}, {b_ed_all.max():.3f}]")

test4_results = {
    'a_folios': len(a_edepth),
    'b_folios': len(b_edepth),
    'a_mean_edepth': round(float(a_mean_ed), 4),
    'b_mean_edepth': round(float(b_mean_ed), 4),
    'matched_correlation': {
        'rho': round(float(rho_ed), 4) if rho_ed is not None else None,
        'p': round(float(p_ed), 4) if p_ed is not None else None,
        'n_folios': len(shared),
    },
    'a_edepth_range': [round(float(a_ed_all.min()), 4), round(float(a_ed_all.max()), 4)],
    'b_edepth_range': [round(float(b_ed_all.min()), 4), round(float(b_ed_all.max()), 4)],
}

# ── Summary ──────────────────────────────────────────────────
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
Bridge MIDDLEs: {len(bridge_middles)}
A folios profiled: {len(a_profiles)}
B folios profiled: {len(b_profiles)}

Test 1 (HEAD-channel cosine):
  Recipe B folios show {'specific' if any(r.get('std_cosine',0) > 0.05 for r in test1_results.values()) else 'uniform'} A-folio preferences
  Cosine spread indicates {'differential' if any(r.get('std_cosine',0) > 0.05 for r in test1_results.values()) else 'flat'} matching signal

Test 2 (Per-channel Spearman):
  Best channels: {', '.join(f"{ch} rho={test2_results[ch]['rho']:+.3f}" for ch in HEAD_CHANNELS if test2_results[ch].get('rho') is not None)}

Test 3 (Permutation):
  p={test3_results['p_value']}, z={test3_results['z_score']}
  {'SIGNIFICANT: HEAD-channel structure creates specific A-B links' if test3_results['p_value'] < 0.05 else 'NOT SIGNIFICANT: HEAD-channel cosine no better than random matching'}

Test 4 (e_depth):
  A mean={a_mean_ed:.3f}, B mean={b_mean_ed:.3f}
  {'Correlated' if rho_ed and rho_ed > 0.3 else 'Not correlated'} through bridge vocabulary
""")

# ── Save results ─────────────────────────────────────────────
results = {
    'test': 's6_bridge_head_channel_probe',
    'description': 'Probe whether bridge MIDDLE HEAD-channel features create specific A-to-B folio links',
    'bridge_middle_count': len(bridge_middles),
    'a_folios_profiled': len(a_profiles),
    'b_folios_profiled': len(b_profiles),
    'min_bridge_tokens': MIN_BRIDGE_TOKENS,
    'test1_head_cosine': test1_results,
    'test2_per_channel_spearman': test2_results,
    'test3_permutation': test3_results,
    'test4_edepth': test4_results,
    'mean_a_head_profile': {ch: round(float(mean_a[i]), 4) for i, ch in enumerate(HEAD_CHANNELS)},
    'mean_b_head_profile': {ch: round(float(mean_b[i]), 4) for i, ch in enumerate(HEAD_CHANNELS)},
    'mean_profile_spearman': {'rho': round(float(rho_mean), 4), 'p': round(float(p_mean), 4)},
}

out_path = os.path.join(os.path.dirname(__file__), '..', 'results', 's6_bridge_head_channel_probe.json')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Results saved to {os.path.abspath(out_path)}")
