"""
02_middle_cooccurrence.py - MIDDLE co-occurrence network analysis

Which MIDDLEs appear together vs never co-occur?
- Paragraph-level co-occurrence matrix
- Identify mutually exclusive pairs (incompatible operations)
- Identify strongly correlated pairs (operation sequences)
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from scipy import stats
from itertools import combinations
import json
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# Load data
tx = Transcript()
morph = Morphology()

# Get Currier B tokens
b_tokens = list(tx.currier_b())
print(f"Total Currier B tokens: {len(b_tokens)}")

# Build paragraph-level MIDDLE sets
paragraphs = defaultdict(set)
current_para = 0
current_folio = None

for t in b_tokens:
    if t.folio != current_folio:
        current_folio = t.folio
        current_para = 0
    if t.par_initial:
        current_para += 1

    m = morph.extract(t.word)
    if m and m.middle:
        key = (t.folio, current_para)
        paragraphs[key].add(m.middle)

print(f"Total paragraphs: {len(paragraphs)}")

# Count MIDDLE frequencies
middle_freq = Counter()
for middles in paragraphs.values():
    for m in middles:
        middle_freq[m] += 1

# Filter to common MIDDLEs (appear in at least 20 paragraphs)
MIN_PARA = 20
common_middles = [m for m, c in middle_freq.items() if c >= MIN_PARA]
print(f"MIDDLEs appearing in >= {MIN_PARA} paragraphs: {len(common_middles)}")

# Build co-occurrence matrix
cooccur = defaultdict(lambda: defaultdict(int))
for middles in paragraphs.values():
    # Filter to common MIDDLEs
    common_in_para = [m for m in middles if m in common_middles]
    # Count co-occurrences
    for m1, m2 in combinations(common_in_para, 2):
        cooccur[m1][m2] += 1
        cooccur[m2][m1] += 1

# Compute expected co-occurrence under independence
n_para = len(paragraphs)

def expected_cooccur(m1, m2):
    """Expected co-occurrence if independent"""
    p1 = middle_freq[m1] / n_para
    p2 = middle_freq[m2] / n_para
    return p1 * p2 * n_para

# Find significantly correlated and anti-correlated pairs
correlations = []

for m1, m2 in combinations(common_middles, 2):
    observed = cooccur[m1][m2]
    expected = expected_cooccur(m1, m2)

    if expected < 5:
        continue  # Skip pairs with low expected count

    # Chi-square-like ratio
    ratio = observed / expected if expected > 0 else 0

    # Compute phi coefficient for significance
    # a = cooccur, b = m1 only, c = m2 only, d = neither
    a = observed
    b = middle_freq[m1] - observed
    c = middle_freq[m2] - observed
    d = n_para - a - b - c

    # Phi coefficient
    denom = np.sqrt((a+b)*(c+d)*(a+c)*(b+d))
    phi = (a*d - b*c) / denom if denom > 0 else 0

    correlations.append({
        'm1': m1,
        'm2': m2,
        'observed': observed,
        'expected': expected,
        'ratio': ratio,
        'phi': phi,
        'freq_m1': middle_freq[m1],
        'freq_m2': middle_freq[m2]
    })

# Sort by phi coefficient
correlations.sort(key=lambda x: x['phi'], reverse=True)

print("\n" + "="*90)
print("STRONGLY CORRELATED PAIRS (phi > 0.15)")
print("="*90)
print(f"{'M1':<10} {'M2':<10} {'Obs':>6} {'Exp':>8} {'Ratio':>7} {'Phi':>7} {'Interpretation'}")
print("-"*90)

positive = [c for c in correlations if c['phi'] > 0.15]
for c in positive[:20]:
    interp = "Co-occurring operations"
    print(f"{c['m1']:<10} {c['m2']:<10} {c['observed']:>6} {c['expected']:>8.1f} {c['ratio']:>7.2f} {c['phi']:>7.3f}   {interp}")

print("\n" + "="*90)
print("ANTI-CORRELATED PAIRS (phi < -0.10)")
print("="*90)
print(f"{'M1':<10} {'M2':<10} {'Obs':>6} {'Exp':>8} {'Ratio':>7} {'Phi':>7} {'Interpretation'}")
print("-"*90)

# Sort by negative phi
correlations.sort(key=lambda x: x['phi'])
negative = [c for c in correlations if c['phi'] < -0.10]
for c in negative[:20]:
    interp = "Mutually exclusive"
    print(f"{c['m1']:<10} {c['m2']:<10} {c['observed']:>6} {c['expected']:>8.1f} {c['ratio']:>7.2f} {c['phi']:>7.3f}   {interp}")

# Cluster analysis - which MIDDLEs form groups?
print("\n" + "="*90)
print("MIDDLE CLUSTERS (by co-occurrence patterns)")
print("="*90)

# Find MIDDLEs that co-occur with k-family
k_family = ['k', 'ke', 'ck', 'ek', 'eck', 'kch']
e_family = ['e', 'ed', 'eed', 'eo', 'eeo', 'eey']
h_family = ['ch', 'sh', 'pch', 'd']

print("\n--- k-family co-occurrence partners ---")
k_partners = defaultdict(float)
for c in correlations:
    if c['m1'] in k_family and c['m2'] not in k_family:
        k_partners[c['m2']] += c['phi']
    elif c['m2'] in k_family and c['m1'] not in k_family:
        k_partners[c['m1']] += c['phi']

for m, score in sorted(k_partners.items(), key=lambda x: -x[1])[:10]:
    print(f"  {m}: {score:.3f}")

print("\n--- e-family co-occurrence partners ---")
e_partners = defaultdict(float)
for c in correlations:
    if c['m1'] in e_family and c['m2'] not in e_family:
        e_partners[c['m2']] += c['phi']
    elif c['m2'] in e_family and c['m1'] not in e_family:
        e_partners[c['m1']] += c['phi']

for m, score in sorted(e_partners.items(), key=lambda x: -x[1])[:10]:
    print(f"  {m}: {score:.3f}")

print("\n--- h-family co-occurrence partners ---")
h_partners = defaultdict(float)
for c in correlations:
    if c['m1'] in h_family and c['m2'] not in h_family:
        h_partners[c['m2']] += c['phi']
    elif c['m2'] in h_family and c['m1'] not in h_family:
        h_partners[c['m1']] += c['phi']

for m, score in sorted(h_partners.items(), key=lambda x: -x[1])[:10]:
    print(f"  {m}: {score:.3f}")

# Summary
print("\n" + "="*90)
print("SUMMARY")
print("="*90)
print(f"Total MIDDLE pairs analyzed: {len(correlations)}")
print(f"Strongly correlated pairs (phi > 0.15): {len(positive)}")
print(f"Anti-correlated pairs (phi < -0.10): {len(negative)}")

# Save results
output = {
    'parameters': {
        'min_paragraphs': MIN_PARA,
        'total_paragraphs': n_para,
        'middles_analyzed': len(common_middles)
    },
    'positive_correlations': positive[:30],
    'negative_correlations': negative[:30],
    'k_family_partners': dict(sorted(k_partners.items(), key=lambda x: -x[1])[:15]),
    'e_family_partners': dict(sorted(e_partners.items(), key=lambda x: -x[1])[:15]),
    'h_family_partners': dict(sorted(h_partners.items(), key=lambda x: -x[1])[:15])
}

with open('C:/git/voynich/phases/MIDDLE_SEMANTIC_DEEPENING/results/middle_cooccurrence.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to middle_cooccurrence.json")
