#!/usr/bin/env python3
"""
s5_bridge_ab_connection.py — Investigate whether B recipe folios reference
specific A material entries through shared (bridge) MIDDLEs.

Bridge MIDDLEs = MIDDLEs that appear in both Currier A and Currier B.
We test whether specific B folios (decoded recipes) share bridge MIDDLEs
with specific A folios more than expected by chance.

Phase: CURRIER_A_ATOMS / Script 5
"""

import sys
import os
import json
import random
from collections import Counter, defaultdict

# Windows stdout encoding fix
sys.stdout.reconfigure(encoding='utf-8')

# Run from repo root
os.chdir(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

# ---------------------------------------------------------------------------
# Data setup
# ---------------------------------------------------------------------------
tx = Transcript()
morph = Morphology()

# Load tokens via iterator API (already filters H-track, labels, uncertain)
a_tokens = list(tx.currier_a())
b_tokens = list(tx.currier_b())

# Filter empty words
a_tokens = [t for t in a_tokens if t.word.strip()]
b_tokens = [t for t in b_tokens if t.word.strip()]

print(f"Currier A tokens: {len(a_tokens)}")
print(f"Currier B tokens: {len(b_tokens)}")

# ---------------------------------------------------------------------------
# Cluster definitions (from s2)
# ---------------------------------------------------------------------------
CLUSTERS = {
    1: {
        'name': 'Thermal/Pharma',
        'folios': ['f87r','f87v','f88v','f89r1','f89r2','f89v1','f89v2',
                   'f90r2','f90v1','f90v2','f93v','f96v','f99r','f99v',
                   'f101r1','f101v2','f102r1','f102r2','f102v1','f102v2',
                   'f27r','f51r','f51v','f52v','f53v','f58r','f58v']
    },
    2: {
        'name': 'Arrangement',
        'folios': ['f100r','f100v','f17r','f1v','f24r','f24v','f3r','f3v',
                   'f45v','f52r','f53r','f54r','f6v','f88r','f90r1','f93r','f96r']
    },
    3: {
        'name': 'Stripped-down',
        'folios': ['f1r','f2r','f2v','f4r','f5v','f6r','f8r','f8v','f9r','f9v',
                   'f10v','f11r','f13v','f15r','f15v','f17v','f18r','f20v',
                   'f22r','f22v','f23r','f23v','f25r','f25v','f28v','f29v',
                   'f32r','f32v','f35r','f35v','f36r','f36v','f37r','f37v',
                   'f38r','f38v','f42r','f44v','f45r','f47r','f54v']
    },
    4: {
        'name': 'Closure-heavy',
        'folios': ['f10r','f11v','f13r','f14r','f14v','f16r','f16v','f18v',
                   'f19r','f19v','f20r','f21r','f21v','f27v','f28r','f29r',
                   'f30r','f30v','f42v','f44r','f47v','f49r','f49v','f4v',
                   'f56r','f56v','f5r','f7r','f7v']
    }
}

# Reverse lookup: folio -> cluster
folio_to_cluster = {}
for cid, cinfo in CLUSTERS.items():
    for f in cinfo['folios']:
        folio_to_cluster[f] = (cid, cinfo['name'])

DECODED_B_FOLIOS = ['f75r', 'f76r', 'f77v', 'f84r']

# ---------------------------------------------------------------------------
# Extract MIDDLEs for all tokens
# ---------------------------------------------------------------------------
def get_middle(word):
    """Extract MIDDLE from a word, returning None if extraction fails."""
    try:
        m = morph.extract(word)
        if m is not None and m.middle and m.middle.strip():
            return m.middle
    except Exception:
        pass
    return None

print("\nExtracting MIDDLEs...")

# A folios -> set of MIDDLEs; also store (folio, word) for later lookups
a_folio_middles = defaultdict(set)
a_middle_counter = Counter()
a_token_by_folio = defaultdict(list)  # folio -> [(word, middle), ...]
for t in a_tokens:
    mid = get_middle(t.word)
    if mid:
        a_folio_middles[t.folio].add(mid)
        a_middle_counter[mid] += 1
        a_token_by_folio[t.folio].append((t.word, mid))

# B folios -> set of MIDDLEs
b_folio_middles = defaultdict(set)
b_middle_counter = Counter()
b_token_by_folio = defaultdict(list)
for t in b_tokens:
    mid = get_middle(t.word)
    if mid:
        b_folio_middles[t.folio].add(mid)
        b_middle_counter[mid] += 1
        b_token_by_folio[t.folio].append((t.word, mid))

print(f"A folios with MIDDLEs: {len(a_folio_middles)}")
print(f"B folios with MIDDLEs: {len(b_folio_middles)}")
print(f"Unique A MIDDLEs: {len(a_middle_counter)}")
print(f"Unique B MIDDLEs: {len(b_middle_counter)}")

# ---------------------------------------------------------------------------
# 1. Bridge MIDDLE inventory
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("1. BRIDGE MIDDLE INVENTORY")
print("="*70)

a_middles_set = set(a_middle_counter.keys())
b_middles_set = set(b_middle_counter.keys())
bridge_middles = a_middles_set & b_middles_set

print(f"\nA-only MIDDLEs: {len(a_middles_set - b_middles_set)}")
print(f"B-only MIDDLEs: {len(b_middles_set - a_middles_set)}")
print(f"Bridge MIDDLEs (shared): {len(bridge_middles)}")

# Sort by combined frequency
bridge_freq = [(m, a_middle_counter[m], b_middle_counter[m],
                a_middle_counter[m] + b_middle_counter[m])
               for m in bridge_middles]
bridge_freq.sort(key=lambda x: -x[3])

print(f"\nTop 30 bridge MIDDLEs by combined frequency:")
print(f"{'MIDDLE':<16} {'A freq':>8} {'B freq':>8} {'Total':>8}")
print("-" * 44)
for mid, af, bf, tot in bridge_freq[:30]:
    print(f"{mid:<16} {af:>8} {bf:>8} {tot:>8}")

# ---------------------------------------------------------------------------
# 2. Per-folio bridge MIDDLE sets
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("2. PER-FOLIO BRIDGE MIDDLE SETS")
print("="*70)

# Filter to only bridge MIDDLEs per folio
a_folio_bridge = {f: mids & bridge_middles for f, mids in a_folio_middles.items()}
b_folio_bridge = {f: mids & bridge_middles for f, mids in b_folio_middles.items()}

a_bridge_counts = sorted([(f, len(s)) for f, s in a_folio_bridge.items()],
                         key=lambda x: -x[1])
b_bridge_counts = sorted([(f, len(s)) for f, s in b_folio_bridge.items()],
                         key=lambda x: -x[1])

print(f"\nA folios with most bridge MIDDLEs:")
for f, c in a_bridge_counts[:15]:
    cl = folio_to_cluster.get(f, (0, 'unknown'))
    print(f"  {f:<10} {c:>3} bridge MIDDLEs  (Cluster {cl[0]}: {cl[1]})")

print(f"\nDecoded B folios - bridge MIDDLE counts:")
for bf in DECODED_B_FOLIOS:
    c = len(b_folio_bridge.get(bf, set()))
    print(f"  {bf:<10} {c:>3} bridge MIDDLEs")

# ---------------------------------------------------------------------------
# 3. B→A matching for decoded recipe folios
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("3. B→A MATCHING FOR DECODED RECIPE FOLIOS")
print("="*70)

def jaccard(s1, s2):
    if not s1 and not s2:
        return 0.0
    union = s1 | s2
    if not union:
        return 0.0
    return len(s1 & s2) / len(union)

b_to_a_matches = {}

for bf in DECODED_B_FOLIOS:
    b_bridges = b_folio_bridge.get(bf, set())
    if not b_bridges:
        print(f"\n{bf}: No bridge MIDDLEs found")
        continue

    print(f"\n{'='*50}")
    print(f"  {bf} — {len(b_bridges)} bridge MIDDLEs: {sorted(b_bridges)}")
    print(f"{'='*50}")

    # Compute Jaccard with all A folios
    scores = []
    for af, a_bridges in a_folio_bridge.items():
        if not a_bridges:
            continue
        j = jaccard(b_bridges, a_bridges)
        shared = b_bridges & a_bridges
        if shared:
            scores.append((af, j, shared))

    scores.sort(key=lambda x: -x[1])

    print(f"\n  Top 10 A folios by Jaccard similarity:")
    print(f"  {'A folio':<10} {'Jaccard':>8} {'Shared':>6} {'Cluster':<22} Shared MIDDLEs")
    print(f"  {'-'*80}")

    top_matches = []
    for af, j, shared in scores[:10]:
        cl = folio_to_cluster.get(af, (0, 'unknown'))
        cl_str = f"C{cl[0]}: {cl[1]}"
        print(f"  {af:<10} {j:>8.3f} {len(shared):>6} {cl_str:<22} {sorted(shared)}")
        top_matches.append({
            'a_folio': af,
            'jaccard': round(j, 4),
            'shared_count': len(shared),
            'shared_middles': sorted(shared),
            'cluster': cl[0],
            'cluster_name': cl[1]
        })

    b_to_a_matches[bf] = {
        'bridge_middles': sorted(b_bridges),
        'bridge_count': len(b_bridges),
        'top_a_matches': top_matches
    }

# ---------------------------------------------------------------------------
# 4. Reverse: A→B matching
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("4. REVERSE: A→B MATCHING (sample A folios per cluster)")
print("="*70)

# Pick 2 folios per cluster with most bridge MIDDLEs
sample_a_folios = []
for cid in sorted(CLUSTERS.keys()):
    cluster_folios = [(f, len(a_folio_bridge.get(f, set())))
                      for f in CLUSTERS[cid]['folios']
                      if len(a_folio_bridge.get(f, set())) > 0]
    cluster_folios.sort(key=lambda x: -x[1])
    sample_a_folios.extend([f for f, _ in cluster_folios[:2]])

a_to_b_matches = {}
for af in sample_a_folios:
    a_bridges = a_folio_bridge.get(af, set())
    if not a_bridges:
        continue

    cl = folio_to_cluster.get(af, (0, 'unknown'))
    print(f"\n  {af} (C{cl[0]}: {cl[1]}) — {len(a_bridges)} bridge MIDDLEs")

    scores = []
    for bf, b_bridges in b_folio_bridge.items():
        if not b_bridges:
            continue
        j = jaccard(a_bridges, b_bridges)
        shared = a_bridges & b_bridges
        if shared:
            scores.append((bf, j, shared))

    scores.sort(key=lambda x: -x[1])

    print(f"  Top 5 B folios:")
    for bf, j, shared in scores[:5]:
        decoded_mark = " *** DECODED" if bf in DECODED_B_FOLIOS else ""
        print(f"    {bf:<10} Jaccard={j:.3f}  shared={len(shared)}  {sorted(shared)}{decoded_mark}")

    a_to_b_matches[af] = {
        'cluster': cl[0],
        'bridge_count': len(a_bridges),
        'top_b_matches': [
            {'b_folio': bf, 'jaccard': round(j, 4), 'shared': sorted(shared),
             'is_decoded': bf in DECODED_B_FOLIOS}
            for bf, j, shared in scores[:5]
        ]
    }

# ---------------------------------------------------------------------------
# 5. Bridge MIDDLE atom profiles
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("5. BRIDGE MIDDLE ATOM PROFILES (top 20 by frequency)")
print("="*70)

# We need a dummy word to atomize — construct prefix + middle + suffix
# Actually, we just need to atomize the middle as if it were the core
# Let's use morph.atomize on a token that contains each middle

# Better: collect actual tokens per bridge middle from A and B
# and atomize one representative token
print(f"\n{'MIDDLE':<16} {'A freq':>6} {'B freq':>6} {'Gloss':<50}")
print("-" * 82)

# Pre-build middle -> example word lookup (first occurrence in B, then A)
middle_example_word = {}
for t in b_tokens:
    mid_t = get_middle(t.word)
    if mid_t and mid_t not in middle_example_word:
        middle_example_word[mid_t] = t.word
for t in a_tokens:
    mid_t = get_middle(t.word)
    if mid_t and mid_t not in middle_example_word:
        middle_example_word[mid_t] = t.word

bridge_atom_profiles = []
for mid, af, bf, tot in bridge_freq[:20]:
    gloss_str = "—"
    found_word = middle_example_word.get(mid)

    if found_word:
        try:
            at = morph.atomize(found_word)
            if at and hasattr(at, 'gloss'):
                gloss_str = at.gloss
        except Exception:
            pass

    print(f"{mid:<16} {af:>6} {bf:>6} {gloss_str:<50}")
    bridge_atom_profiles.append({
        'middle': mid,
        'a_freq': af,
        'b_freq': bf,
        'example_word': found_word,
        'gloss': gloss_str
    })

# ---------------------------------------------------------------------------
# 6. Same MIDDLE, different context (PREFIX comparison)
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("6. SAME MIDDLE, DIFFERENT PREFIX CONTEXT (top 5 bridge MIDDLEs)")
print("="*70)

# Build prefix -> middle mapping per system
a_prefix_by_middle = defaultdict(lambda: Counter())
b_prefix_by_middle = defaultdict(lambda: Counter())

for t in a_tokens:
    try:
        m = morph.extract(t.word)
        if m and m.middle and m.middle.strip():
            pfx = m.prefix if m.prefix else '(none)'
            a_prefix_by_middle[m.middle][pfx] += 1
    except Exception:
        pass

for t in b_tokens:
    try:
        m = morph.extract(t.word)
        if m and m.middle and m.middle.strip():
            pfx = m.prefix if m.prefix else '(none)'
            b_prefix_by_middle[m.middle][pfx] += 1
    except Exception:
        pass

prefix_comparison = []
for mid, af, bf, tot in bridge_freq[:5]:
    print(f"\n  MIDDLE: {mid}")
    a_pfx = a_prefix_by_middle[mid]
    b_pfx = b_prefix_by_middle[mid]
    print(f"    A prefixes: {dict(a_pfx.most_common(10))}")
    print(f"    B prefixes: {dict(b_pfx.most_common(10))}")

    # Overlap
    a_pfx_set = set(a_pfx.keys())
    b_pfx_set = set(b_pfx.keys())
    shared_pfx = a_pfx_set & b_pfx_set
    a_only_pfx = a_pfx_set - b_pfx_set
    b_only_pfx = b_pfx_set - a_pfx_set
    print(f"    Shared prefixes: {sorted(shared_pfx)}")
    print(f"    A-only prefixes: {sorted(a_only_pfx)}")
    print(f"    B-only prefixes: {sorted(b_only_pfx)}")

    prefix_comparison.append({
        'middle': mid,
        'a_prefixes': dict(a_pfx.most_common()),
        'b_prefixes': dict(b_pfx.most_common()),
        'shared_prefixes': sorted(shared_pfx),
        'a_only_prefixes': sorted(a_only_pfx),
        'b_only_prefixes': sorted(b_only_pfx)
    })

# ---------------------------------------------------------------------------
# 7. Specificity test (permutation)
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("7. SPECIFICITY TEST — Permutation analysis")
print("="*70)

random.seed(42)
N_PERMS = 1000

a_folios_list = [f for f in a_folio_bridge.keys() if a_folio_bridge[f]]

specificity_results = {}
for bf in DECODED_B_FOLIOS:
    b_bridges = b_folio_bridge.get(bf, set())
    if not b_bridges:
        print(f"\n  {bf}: No bridge MIDDLEs, skipping")
        continue

    # Actual max Jaccard
    actual_jaccards = []
    for af in a_folios_list:
        j = jaccard(b_bridges, a_folio_bridge[af])
        actual_jaccards.append((af, j))
    actual_jaccards.sort(key=lambda x: -x[1])
    actual_max_j = actual_jaccards[0][1]
    actual_best_af = actual_jaccards[0][0]

    # Permutation: shuffle A folio bridge sets and compute max Jaccard
    a_bridge_sets_list = [a_folio_bridge[f] for f in a_folios_list]
    perm_max_jaccards = []
    for _ in range(N_PERMS):
        # Shuffle the bridge sets among A folios
        shuffled = list(a_bridge_sets_list)
        random.shuffle(shuffled)
        max_j = 0.0
        for s in shuffled:
            j = jaccard(b_bridges, s)
            if j > max_j:
                max_j = j
        perm_max_jaccards.append(max_j)

    # p-value: fraction of permutations with max Jaccard >= actual
    p_value = sum(1 for pj in perm_max_jaccards if pj >= actual_max_j) / N_PERMS
    mean_perm = sum(perm_max_jaccards) / len(perm_max_jaccards)

    cl = folio_to_cluster.get(actual_best_af, (0, 'unknown'))
    print(f"\n  {bf}:")
    print(f"    Best A match: {actual_best_af} (C{cl[0]}: {cl[1]})")
    print(f"    Actual max Jaccard:   {actual_max_j:.4f}")
    print(f"    Permutation mean max: {mean_perm:.4f}")
    print(f"    p-value:              {p_value:.4f}")
    print(f"    {'SIGNIFICANT (p<0.05)' if p_value < 0.05 else 'Not significant'}")

    specificity_results[bf] = {
        'best_a_folio': actual_best_af,
        'best_cluster': cl[0],
        'actual_max_jaccard': round(actual_max_j, 4),
        'perm_mean_max_jaccard': round(mean_perm, 4),
        'p_value': round(p_value, 4),
        'significant': p_value < 0.05
    }

# ---------------------------------------------------------------------------
# 8. Network summary
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("8. NETWORK SUMMARY — Decoded B folios and their A connections")
print("="*70)

network_summary = []
for bf in DECODED_B_FOLIOS:
    info = b_to_a_matches.get(bf, {})
    if not info:
        continue

    print(f"\n  {bf} ({info['bridge_count']} bridge MIDDLEs)")
    print(f"  {'─'*60}")

    for match in info['top_a_matches'][:5]:
        # Gloss the shared MIDDLEs
        glosses = []
        for mid in match['shared_middles']:
            gloss = mid  # fallback
            # Use pre-built example word lookup
            example = middle_example_word.get(mid)
            if example:
                try:
                    at = morph.atomize(example)
                    if at and hasattr(at, 'gloss'):
                        gloss = at.gloss
                except Exception:
                    pass
            glosses.append(gloss)

        cl_str = f"C{match['cluster']}: {match['cluster_name']}"
        print(f"    → {match['a_folio']:<10} J={match['jaccard']:.3f}  "
              f"({cl_str})")
        print(f"      Shared: {match['shared_middles']}")
        for g in glosses[:3]:
            print(f"        gloss: {g}")

        network_summary.append({
            'b_folio': bf,
            'a_folio': match['a_folio'],
            'jaccard': match['jaccard'],
            'cluster': match['cluster'],
            'cluster_name': match['cluster_name'],
            'shared_middles': match['shared_middles'],
            'glosses': glosses
        })

# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

# Which clusters do decoded B folios connect to most?
cluster_connections = Counter()
for entry in network_summary:
    cluster_connections[entry['cluster']] += 1

print(f"\nCluster connection frequency (across all decoded B folio matches):")
for cid in sorted(CLUSTERS.keys()):
    print(f"  Cluster {cid} ({CLUSTERS[cid]['name']}): "
          f"{cluster_connections.get(cid, 0)} connections")

print(f"\nBridge MIDDLE count: {len(bridge_middles)}")
print(f"A folios with bridge MIDDLEs: {len(a_folio_bridge)}")
print(f"B folios with bridge MIDDLEs: {len(b_folio_bridge)}")

# ---------------------------------------------------------------------------
# Save JSON
# ---------------------------------------------------------------------------
output = {
    'bridge_middle_count': len(bridge_middles),
    'bridge_middles': sorted(bridge_middles),
    'bridge_freq_top30': [
        {'middle': m, 'a_freq': af, 'b_freq': bf, 'total': t}
        for m, af, bf, t in bridge_freq[:30]
    ],
    'b_to_a_matches': b_to_a_matches,
    'a_to_b_matches': a_to_b_matches,
    'bridge_atom_profiles': bridge_atom_profiles,
    'prefix_comparison': prefix_comparison,
    'specificity_tests': specificity_results,
    'network_summary': network_summary,
    'cluster_connections': {str(k): v for k, v in cluster_connections.items()}
}

out_path = 'phases/CURRIER_A_ATOMS/results/s5_bridge_ab_connection.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to {out_path}")
