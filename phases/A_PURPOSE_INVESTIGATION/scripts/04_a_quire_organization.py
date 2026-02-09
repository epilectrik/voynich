"""
04_a_quire_organization.py - Test if A organization correlates with quire structure

If A serves human operators, its organization might respect physical manuscript
structure (quires = binding units = potential work sessions).

Tests:
1. Does RI vocabulary cluster by quire?
2. Do linker connections respect or cross quire boundaries?
3. Does A vocabulary diversity vary by quire?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')
import pandas as pd
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
from scipy import stats
import json
import numpy as np

# Load transcript for quire info
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

# Build folio -> quire mapping
folio_quire = df.groupby('folio')['quire'].first().to_dict()

tx = Transcript()
morph = Morphology()

# Get A tokens
a_tokens = list(tx.currier_a())
print(f"Currier A tokens: {len(a_tokens)}")

# Get A folios and their quires
a_folios = sorted(set(t.folio for t in a_tokens))
print(f"A folios: {len(a_folios)}")

a_folio_quires = {f: folio_quire.get(f, 'Unknown') for f in a_folios}
print(f"\nA folios by quire:")
quire_counts = Counter(a_folio_quires.values())
for q in sorted(quire_counts.keys()):
    print(f"  Quire {q}: {quire_counts[q]} folios")

# ============================================================
# Test 1: RI vocabulary clustering by quire
# ============================================================
print("\n" + "="*70)
print("TEST 1: RI VOCABULARY CLUSTERING BY QUIRE")
print("="*70)

# Build B vocabulary to identify RI (A-exclusive)
b_tokens = list(tx.currier_b())
b_middles = set()
for t in b_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        b_middles.add(m.middle)

# Get RI vocabulary per A folio
a_folio_ri = defaultdict(set)
a_folio_pp = defaultdict(set)

for t in a_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        if m.middle in b_middles:
            a_folio_pp[t.folio].add(m.middle)
        else:
            a_folio_ri[t.folio].add(m.middle)

# Compute within-quire vs cross-quire RI Jaccard similarity
within_quire_ri = []
cross_quire_ri = []

a_folio_list = [f for f in a_folios if f in a_folio_ri and len(a_folio_ri[f]) > 0]

for i, f1 in enumerate(a_folio_list):
    for f2 in a_folio_list[i+1:]:
        ri1 = a_folio_ri[f1]
        ri2 = a_folio_ri[f2]

        if ri1 and ri2:
            jaccard = len(ri1 & ri2) / len(ri1 | ri2)

            q1 = a_folio_quires.get(f1)
            q2 = a_folio_quires.get(f2)

            if q1 == q2:
                within_quire_ri.append(jaccard)
            else:
                cross_quire_ri.append(jaccard)

print(f"\nRI Jaccard similarity:")
print(f"  Within-quire pairs: {len(within_quire_ri)}, mean={np.mean(within_quire_ri):.4f}")
print(f"  Cross-quire pairs: {len(cross_quire_ri)}, mean={np.mean(cross_quire_ri):.4f}")

if within_quire_ri and cross_quire_ri:
    ratio = np.mean(within_quire_ri) / np.mean(cross_quire_ri) if np.mean(cross_quire_ri) > 0 else float('inf')
    t_stat, p_val = stats.ttest_ind(within_quire_ri, cross_quire_ri)
    print(f"  Ratio (within/cross): {ratio:.2f}x")
    print(f"  t-test p-value: {p_val:.4f}")

    if ratio > 1.2 and p_val < 0.05:
        print("  -> RI clusters by quire (SUPPORTS human-interface hypothesis)")
        ri_quire_result = "SUPPORTS"
    elif ratio < 0.8 and p_val < 0.05:
        print("  -> RI anti-clusters by quire (unexpected)")
        ri_quire_result = "CONTRADICTS"
    else:
        print("  -> No significant quire effect on RI")
        ri_quire_result = "NEUTRAL"
else:
    ri_quire_result = "INSUFFICIENT_DATA"

# ============================================================
# Test 2: PP vocabulary clustering by quire
# ============================================================
print("\n" + "="*70)
print("TEST 2: PP VOCABULARY CLUSTERING BY QUIRE")
print("="*70)

within_quire_pp = []
cross_quire_pp = []

a_folio_list_pp = [f for f in a_folios if f in a_folio_pp and len(a_folio_pp[f]) > 0]

for i, f1 in enumerate(a_folio_list_pp):
    for f2 in a_folio_list_pp[i+1:]:
        pp1 = a_folio_pp[f1]
        pp2 = a_folio_pp[f2]

        if pp1 and pp2:
            jaccard = len(pp1 & pp2) / len(pp1 | pp2)

            q1 = a_folio_quires.get(f1)
            q2 = a_folio_quires.get(f2)

            if q1 == q2:
                within_quire_pp.append(jaccard)
            else:
                cross_quire_pp.append(jaccard)

print(f"\nPP Jaccard similarity:")
print(f"  Within-quire pairs: {len(within_quire_pp)}, mean={np.mean(within_quire_pp):.4f}")
print(f"  Cross-quire pairs: {len(cross_quire_pp)}, mean={np.mean(cross_quire_pp):.4f}")

if within_quire_pp and cross_quire_pp:
    ratio_pp = np.mean(within_quire_pp) / np.mean(cross_quire_pp) if np.mean(cross_quire_pp) > 0 else float('inf')
    t_stat_pp, p_val_pp = stats.ttest_ind(within_quire_pp, cross_quire_pp)
    print(f"  Ratio (within/cross): {ratio_pp:.2f}x")
    print(f"  t-test p-value: {p_val_pp:.4f}")

    if ratio_pp > 1.2 and p_val_pp < 0.05:
        print("  -> PP clusters by quire")
        pp_quire_result = "SUPPORTS"
    else:
        print("  -> No significant quire effect on PP")
        pp_quire_result = "NEUTRAL"
else:
    pp_quire_result = "INSUFFICIENT_DATA"

# ============================================================
# Test 3: A vocabulary diversity by quire
# ============================================================
print("\n" + "="*70)
print("TEST 3: A VOCABULARY DIVERSITY BY QUIRE")
print("="*70)

# Compute vocabulary diversity per quire
quire_vocab = defaultdict(set)
quire_ri_count = defaultdict(int)
quire_pp_count = defaultdict(int)

for t in a_tokens:
    quire = a_folio_quires.get(t.folio)
    if quire:
        m = morph.extract(t.word)
        if m and m.middle:
            quire_vocab[quire].add(m.middle)
            if m.middle in b_middles:
                quire_pp_count[quire] += 1
            else:
                quire_ri_count[quire] += 1

print(f"\nVocabulary per quire:")
print(f"{'Quire':<8} {'Vocab':<8} {'RI':<8} {'PP':<8} {'RI%':<8}")
print("-" * 40)

quire_data = []
for q in sorted(quire_vocab.keys()):
    vocab_size = len(quire_vocab[q])
    ri = quire_ri_count[q]
    pp = quire_pp_count[q]
    ri_pct = 100 * ri / (ri + pp) if (ri + pp) > 0 else 0
    print(f"{q:<8} {vocab_size:<8} {ri:<8} {pp:<8} {ri_pct:<7.1f}%")
    quire_data.append({'quire': q, 'vocab': vocab_size, 'ri': ri, 'pp': pp, 'ri_pct': ri_pct})

# Test if RI% varies significantly by quire
ri_pcts = [d['ri_pct'] for d in quire_data if d['ri'] + d['pp'] > 50]
if len(ri_pcts) >= 3:
    # Kruskal-Wallis test
    groups = []
    for q in sorted(set(a_folio_quires.values())):
        q_folios = [f for f in a_folios if a_folio_quires.get(f) == q]
        q_ri_pcts = []
        for f in q_folios:
            ri = len(a_folio_ri.get(f, set()))
            pp = len(a_folio_pp.get(f, set()))
            if ri + pp > 0:
                q_ri_pcts.append(100 * ri / (ri + pp))
        if len(q_ri_pcts) >= 2:
            groups.append(q_ri_pcts)

    if len(groups) >= 2:
        h_stat, p_kw = stats.kruskal(*groups)
        print(f"\nKruskal-Wallis test (RI% by quire):")
        print(f"  H-statistic: {h_stat:.2f}")
        print(f"  p-value: {p_kw:.4f}")
        if p_kw < 0.05:
            print("  -> Significant quire effect on RI proportion")
        else:
            print("  -> No significant quire effect on RI proportion")

# ============================================================
# Test 4: Linker destinations vs quires
# ============================================================
print("\n" + "="*70)
print("TEST 4: LINKER DESTINATIONS AND QUIRES")
print("="*70)

# Known linkers from C835
linkers = ['cthody', 'ctho', 'ctheody', 'qokoiiin']
linker_destinations = {'f93v': 5, 'f32r': 4}  # From C835

print(f"\nKnown linker hub destinations:")
for dest, count in linker_destinations.items():
    quire = folio_quire.get(dest, 'Unknown')
    print(f"  {dest} (quire {quire}): {count} incoming links")

# Check if destinations are at quire boundaries
print(f"\nQuire boundary analysis:")
for dest in linker_destinations:
    quire = folio_quire.get(dest)
    # Get folios in same quire
    same_quire = [f for f in folio_quire if folio_quire[f] == quire]
    same_quire_sorted = sorted(same_quire)
    if dest in same_quire_sorted:
        pos = same_quire_sorted.index(dest)
        is_boundary = pos == 0 or pos == len(same_quire_sorted) - 1
        print(f"  {dest}: position {pos+1}/{len(same_quire_sorted)} in quire {quire} {'(BOUNDARY)' if is_boundary else ''}")

# ============================================================
# Summary
# ============================================================
print("\n" + "="*70)
print("SUMMARY: A-QUIRE ORGANIZATION")
print("="*70)

print(f"""
RI vocabulary quire clustering: {ri_quire_result}
PP vocabulary quire clustering: {pp_quire_result}

If A serves human operators, we'd expect:
- RI to cluster by quire (work sessions)
- Linker hubs at strategic quire positions

""")

# Save results
output = {
    'ri_quire_test': {
        'within_mean': float(np.mean(within_quire_ri)) if within_quire_ri else None,
        'cross_mean': float(np.mean(cross_quire_ri)) if cross_quire_ri else None,
        'ratio': float(ratio) if 'ratio' in dir() else None,
        'p_value': float(p_val) if 'p_val' in dir() else None,
        'result': ri_quire_result
    },
    'pp_quire_test': {
        'within_mean': float(np.mean(within_quire_pp)) if within_quire_pp else None,
        'cross_mean': float(np.mean(cross_quire_pp)) if cross_quire_pp else None,
        'ratio': float(ratio_pp) if 'ratio_pp' in dir() else None,
        'result': pp_quire_result
    },
    'quire_data': quire_data
}

with open('C:/git/voynich/phases/A_PURPOSE_INVESTIGATION/results/a_quire_organization.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Results saved to a_quire_organization.json")
