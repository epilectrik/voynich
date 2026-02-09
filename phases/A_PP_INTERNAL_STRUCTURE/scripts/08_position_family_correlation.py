"""
08_position_family_correlation.py - Test if A position correlates with MIDDLE family

Building on C899 (A-B positional correspondence) and C908-C910 (MIDDLE semantic families):
- If A organizes entries by operation phase
- EARLY A should use k-family MIDDLEs (energy/heating)
- LATE A should use e-family MIDDLEs (stability/closure)

This would reveal if A is a registry sorted by procedural sequence.
"""

import numpy as np
from collections import defaultdict, Counter
from scipy import stats
import json
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# Define MIDDLE families from C908-C910
K_FAMILY = {'k', 'ke', 'ck', 'ek', 'eck', 'kch', 'lk', 'eek', 'ckh'}
E_FAMILY = {'e', 'ed', 'eed', 'eo', 'eeo', 'eod', 'eey', 'ey', 'ee'}
H_FAMILY = {'ch', 'sh', 'pch', 'opch', 'd'}
INFRA_FAMILY = {'iin', 'aiin', 'in', 'ain', 'l', 'r', 'ar', 'or', 'al', 'ol'}

# Load data
tx = Transcript()
morph = Morphology()

# Get Currier A tokens
a_tokens = list(tx.currier_a())
print(f"Total Currier A tokens: {len(a_tokens)}")

# Compute within-line position for each token
token_data = []
for t in a_tokens:
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    # Compute normalized position (0 = first, 1 = last)
    total_pos = t.line_initial + t.line_final - 1
    if total_pos > 0:
        norm_pos = (t.line_initial - 1) / total_pos
    else:
        norm_pos = 0.5  # Single-token line

    # Determine family
    mid = m.middle
    if mid in K_FAMILY:
        family = 'k-family'
    elif mid in E_FAMILY:
        family = 'e-family'
    elif mid in H_FAMILY:
        family = 'h-family'
    elif mid in INFRA_FAMILY:
        family = 'infra'
    else:
        family = 'other'

    token_data.append({
        'word': t.word,
        'middle': mid,
        'family': family,
        'position': norm_pos,
        'folio': t.folio,
        'section': t.section
    })

print(f"Tokens with MIDDLE: {len(token_data)}")

# Count by family
family_counts = Counter(t['family'] for t in token_data)
print(f"\nFamily distribution:")
for fam, count in family_counts.most_common():
    print(f"  {fam}: {count} ({100*count/len(token_data):.1f}%)")

# Compute mean position by family
print("\n" + "="*70)
print("MEAN POSITION BY MIDDLE FAMILY")
print("="*70)

family_positions = defaultdict(list)
for t in token_data:
    family_positions[t['family']].append(t['position'])

print(f"\n{'Family':<12} {'Mean Pos':>10} {'Std':>8} {'N':>8} {'Interpretation'}")
print("-"*60)

results = []
for fam in ['k-family', 'e-family', 'h-family', 'infra', 'other']:
    positions = family_positions[fam]
    if len(positions) > 10:
        mean_pos = np.mean(positions)
        std_pos = np.std(positions)

        if mean_pos < 0.4:
            interp = "EARLY-biased"
        elif mean_pos > 0.6:
            interp = "LATE-biased"
        else:
            interp = "MIDDLE"

        print(f"{fam:<12} {mean_pos:>10.3f} {std_pos:>8.3f} {len(positions):>8}  {interp}")
        results.append({'family': fam, 'mean': mean_pos, 'std': std_pos, 'n': len(positions)})

# Statistical test: ANOVA for position differences
print("\n" + "="*70)
print("STATISTICAL TESTS")
print("="*70)

# Compare k-family vs e-family positions
k_positions = family_positions['k-family']
e_positions = family_positions['e-family']
h_positions = family_positions['h-family']

if len(k_positions) > 10 and len(e_positions) > 10:
    t_stat, p_val = stats.ttest_ind(k_positions, e_positions)
    print(f"\nk-family vs e-family t-test:")
    print(f"  k-family mean: {np.mean(k_positions):.3f}")
    print(f"  e-family mean: {np.mean(e_positions):.3f}")
    print(f"  t-statistic: {t_stat:.3f}")
    print(f"  p-value: {p_val:.6f}")
    print(f"  Significant: {'YES' if p_val < 0.01 else 'NO'}")

# ANOVA across all families
groups = [family_positions[f] for f in ['k-family', 'e-family', 'h-family', 'infra'] if len(family_positions[f]) > 10]
if len(groups) >= 2:
    f_stat, p_anova = stats.f_oneway(*groups)
    print(f"\nOne-way ANOVA (all families):")
    print(f"  F-statistic: {f_stat:.3f}")
    print(f"  p-value: {p_anova:.6f}")
    print(f"  Significant: {'YES' if p_anova < 0.01 else 'NO'}")

# Position zone analysis
print("\n" + "="*70)
print("FAMILY DISTRIBUTION BY POSITION ZONE")
print("="*70)

zones = {
    'EARLY (0-0.33)': [t for t in token_data if t['position'] < 0.33],
    'MIDDLE (0.33-0.67)': [t for t in token_data if 0.33 <= t['position'] < 0.67],
    'LATE (0.67-1.0)': [t for t in token_data if t['position'] >= 0.67]
}

print(f"\n{'Zone':<20}", end="")
for fam in ['k-family', 'e-family', 'h-family', 'infra', 'other']:
    print(f"{fam:>12}", end="")
print(f"{'Total':>10}")
print("-"*90)

zone_data = {}
for zone_name, tokens in zones.items():
    zone_total = len(tokens)
    print(f"{zone_name:<20}", end="")

    zone_families = Counter(t['family'] for t in tokens)
    zone_data[zone_name] = {}

    for fam in ['k-family', 'e-family', 'h-family', 'infra', 'other']:
        count = zone_families[fam]
        pct = 100 * count / zone_total if zone_total > 0 else 0
        zone_data[zone_name][fam] = {'count': count, 'pct': pct}
        print(f"{pct:>11.1f}%", end="")
    print(f"{zone_total:>10}")

# Enrichment analysis
print("\n" + "="*70)
print("ENRICHMENT BY ZONE (vs overall baseline)")
print("="*70)

overall_rates = {fam: family_counts[fam] / len(token_data) for fam in family_counts}

print(f"\n{'Zone':<20}", end="")
for fam in ['k-family', 'e-family', 'h-family', 'infra']:
    print(f"{fam:>12}", end="")
print()
print("-"*70)

for zone_name, tokens in zones.items():
    zone_total = len(tokens)
    print(f"{zone_name:<20}", end="")

    zone_families = Counter(t['family'] for t in tokens)

    for fam in ['k-family', 'e-family', 'h-family', 'infra']:
        observed_rate = zone_families[fam] / zone_total if zone_total > 0 else 0
        expected_rate = overall_rates.get(fam, 0)
        enrichment = observed_rate / expected_rate if expected_rate > 0 else 0

        if enrichment > 1.2:
            marker = "*"
        elif enrichment < 0.8:
            marker = "_"
        else:
            marker = " "
        print(f"{marker}{enrichment:>10.2f}x", end="")
    print()

# Check specific MIDDLEs by position
print("\n" + "="*70)
print("TOP MIDDLEs BY POSITION ZONE")
print("="*70)

for zone_name, tokens in zones.items():
    print(f"\n--- {zone_name} ---")
    middle_counts = Counter(t['middle'] for t in tokens)
    for mid, count in middle_counts.most_common(10):
        # Determine family
        if mid in K_FAMILY:
            fam = '[k]'
        elif mid in E_FAMILY:
            fam = '[e]'
        elif mid in H_FAMILY:
            fam = '[h]'
        elif mid in INFRA_FAMILY:
            fam = '[i]'
        else:
            fam = '[?]'
        print(f"  {mid:<10} {fam:<4} {count}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

k_mean = np.mean(k_positions) if k_positions else 0
e_mean = np.mean(e_positions) if e_positions else 0
h_mean = np.mean(h_positions) if h_positions else 0

print(f"\nMean positions:")
print(f"  k-family: {k_mean:.3f}")
print(f"  e-family: {e_mean:.3f}")
print(f"  h-family: {h_mean:.3f}")

if k_mean < e_mean:
    print(f"\nk-family is EARLIER than e-family by {e_mean - k_mean:.3f}")
    print("This supports: A organizes EARLY → heating, LATE → stability")
else:
    print(f"\ne-family is EARLIER than k-family by {k_mean - e_mean:.3f}")
    print("This does NOT support the expected pattern")

# Save results
output = {
    'family_positions': {fam: {'mean': float(np.mean(pos)), 'std': float(np.std(pos)), 'n': len(pos)}
                         for fam, pos in family_positions.items() if len(pos) > 10},
    'zone_enrichment': zone_data,
    'statistical_tests': {
        'k_vs_e_ttest': {'t': float(t_stat), 'p': float(p_val)} if 'p_val' in dir() else None,
        'anova': {'f': float(f_stat), 'p': float(p_anova)} if 'p_anova' in dir() else None
    }
}

with open('C:/git/voynich/phases/A_PP_INTERNAL_STRUCTURE/results/position_family_correlation.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to position_family_correlation.json")
