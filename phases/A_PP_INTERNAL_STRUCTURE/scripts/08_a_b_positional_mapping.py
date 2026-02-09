#!/usr/bin/env python3
"""
Test 8: A-B Positional Mapping

Question: Does A's PP positional structure relate to B's procedural order?

Patterns to check:
1. Linear correlation (A-early = B-early)
2. Inverse correlation (A-early = B-late)
3. Zone mapping (A position zones map to B zones)
4. Hub position invariance (hubs same position in both?)
5. Position preservation vs scrambling
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

RI_PREFIXES = {'po', 'do', 'so', 'to', 'ko', 'qo', 'ch', 'sh'}

print("="*70)
print("TEST 8: A-B POSITIONAL MAPPING")
print("="*70)

# =========================================================================
# Pre-compute line structures (EFFICIENT)
# =========================================================================
print("\nPre-computing line structures...")

# Group tokens by line
a_lines = defaultdict(list)
b_lines = defaultdict(list)

for token in tx.currier_a():
    if '*' not in token.word:
        a_lines[(token.folio, token.line)].append(token.word)

for token in tx.currier_b():
    if '*' not in token.word:
        b_lines[(token.folio, token.line)].append(token.word)

print(f"  A lines: {len(a_lines)}")
print(f"  B lines: {len(b_lines)}")

# =========================================================================
# Collect positions from pre-computed lines
# =========================================================================
print("\nCollecting A PP positions...")

a_positions = defaultdict(list)
a_prefix_positions = defaultdict(list)

for (folio, line), tokens in a_lines.items():
    if len(tokens) < 2:
        continue
    for i, word in enumerate(tokens):
        try:
            m = morph.extract(word)
            if m.prefix not in RI_PREFIXES and m.middle:
                norm_pos = i / (len(tokens) - 1)
                a_positions[m.middle].append(norm_pos)
                if m.prefix:
                    a_prefix_positions[m.prefix].append(norm_pos)
        except:
            pass

print(f"  A MIDDLEs with positions: {len(a_positions)}")

print("\nCollecting B positions...")

b_positions = defaultdict(list)
b_prefix_positions = defaultdict(list)

for (folio, line), tokens in b_lines.items():
    if len(tokens) < 2:
        continue
    for i, word in enumerate(tokens):
        try:
            m = morph.extract(word)
            if m.middle:
                norm_pos = i / (len(tokens) - 1)
                b_positions[m.middle].append(norm_pos)
                if m.prefix:
                    b_prefix_positions[m.prefix].append(norm_pos)
        except:
            pass

print(f"  B MIDDLEs with positions: {len(b_positions)}")

# =========================================================================
# Find shared MIDDLEs with sufficient data
# =========================================================================
print("\n" + "="*70)
print("SHARED MIDDLE ANALYSIS")
print("="*70)

MIN_COUNT = 20
shared_middles = []

for middle in a_positions:
    if middle in b_positions:
        if len(a_positions[middle]) >= MIN_COUNT and len(b_positions[middle]) >= MIN_COUNT:
            a_mean = np.mean(a_positions[middle])
            b_mean = np.mean(b_positions[middle])
            shared_middles.append({
                'middle': middle,
                'a_mean': a_mean,
                'b_mean': b_mean,
                'a_n': len(a_positions[middle]),
                'b_n': len(b_positions[middle]),
            })

print(f"\nShared MIDDLEs with n>={MIN_COUNT} in both: {len(shared_middles)}")

def get_zone(pos):
    if pos < 0.33:
        return 'EARLY'
    elif pos < 0.67:
        return 'MIDDLE'
    else:
        return 'LATE'

if len(shared_middles) < 5:
    print("Insufficient shared MIDDLEs for analysis")
    verdict = "INSUFFICIENT DATA"
    findings = []
else:
    # Extract for correlation
    a_means = np.array([m['a_mean'] for m in shared_middles])
    b_means = np.array([m['b_mean'] for m in shared_middles])

    # =========================================================================
    # Pattern 1: Linear correlation
    # =========================================================================
    print("\n" + "-"*50)
    print("PATTERN 1: LINEAR CORRELATION")
    print("-"*50)

    r, p = stats.pearsonr(a_means, b_means)
    rho, rho_p = stats.spearmanr(a_means, b_means)

    print(f"\nPearson r = {r:.3f} (p = {p:.4f})")
    print(f"Spearman rho = {rho:.3f} (p = {rho_p:.4f})")

    if p < 0.05:
        if r > 0:
            print("** POSITIVE: A-early tends to be B-early **")
        else:
            print("** NEGATIVE: A-early tends to be B-late **")
    else:
        print("No significant linear relationship")

    # =========================================================================
    # Pattern 2: Zone mapping (categorical)
    # =========================================================================
    print("\n" + "-"*50)
    print("PATTERN 2: ZONE MAPPING")
    print("-"*50)

    zone_mapping = defaultdict(lambda: Counter())
    for m in shared_middles:
        a_zone = get_zone(m['a_mean'])
        b_zone = get_zone(m['b_mean'])
        zone_mapping[a_zone][b_zone] += 1

    print("\nA Zone -> B Zone distribution:")
    print(f"{'A Zone':<10} {'B-EARLY':<12} {'B-MIDDLE':<12} {'B-LATE':<12}")
    print("-"*46)
    for a_zone in ['EARLY', 'MIDDLE', 'LATE']:
        row = zone_mapping[a_zone]
        total = sum(row.values())
        if total > 0:
            print(f"{a_zone:<10} {row['EARLY']:<12} {row['MIDDLE']:<12} {row['LATE']:<12}")

    # Chi-square test for independence
    contingency = []
    for a_zone in ['EARLY', 'MIDDLE', 'LATE']:
        row = [zone_mapping[a_zone][b_zone] for b_zone in ['EARLY', 'MIDDLE', 'LATE']]
        if sum(row) > 0:
            contingency.append(row)

    chi_p = 1.0
    if len(contingency) >= 2 and all(sum(row) > 0 for row in contingency):
        try:
            chi2, chi_p, dof, expected = stats.chi2_contingency(contingency)
            print(f"\nChi-square test: chi2={chi2:.2f}, p={chi_p:.4f}")
            if chi_p < 0.05:
                print("** Zones are NOT independent - mapping exists **")
            else:
                print("Zones are independent - no categorical mapping")
        except:
            print("\nChi-square test: insufficient data")

    # =========================================================================
    # Pattern 3: Position preservation vs scrambling
    # =========================================================================
    print("\n" + "-"*50)
    print("PATTERN 3: POSITION PRESERVATION")
    print("-"*50)

    same_zone = sum(1 for m in shared_middles if get_zone(m['a_mean']) == get_zone(m['b_mean']))
    pct_same = 100 * same_zone / len(shared_middles)

    print(f"\nMIDDLEs in same zone (A and B): {same_zone}/{len(shared_middles)} ({pct_same:.1f}%)")
    print(f"Expected by chance: 33%")

    # Binomial test
    from scipy.stats import binomtest
    binom_result = binomtest(same_zone, len(shared_middles), 1/3, alternative='greater')
    binom_p = binom_result.pvalue
    print(f"Binomial test (same zone > chance): p = {binom_p:.4f}")

    if binom_p < 0.05:
        print("** Position is PRESERVED across A->B **")
    else:
        print("Position is scrambled (no preservation)")

    # =========================================================================
    # Pattern 4: Extreme position analysis
    # =========================================================================
    print("\n" + "-"*50)
    print("PATTERN 4: EXTREME POSITIONS")
    print("-"*50)

    sorted_by_a = sorted(shared_middles, key=lambda x: x['a_mean'])

    print("\nMost A-EARLY MIDDLEs and their B positions:")
    for m in sorted_by_a[:5]:
        print(f"  {m['middle']:<12} A={m['a_mean']:.3f} -> B={m['b_mean']:.3f}")

    print("\nMost A-LATE MIDDLEs and their B positions:")
    for m in sorted_by_a[-5:]:
        print(f"  {m['middle']:<12} A={m['a_mean']:.3f} -> B={m['b_mean']:.3f}")

    a_early_5 = sorted_by_a[:5]
    a_late_5 = sorted_by_a[-5:]

    a_early_b_mean = np.mean([m['b_mean'] for m in a_early_5])
    a_late_b_mean = np.mean([m['b_mean'] for m in a_late_5])

    print(f"\nA-EARLY (n=5) mean B position: {a_early_b_mean:.3f}")
    print(f"A-LATE (n=5) mean B position: {a_late_b_mean:.3f}")

    # Mann-Whitney test for extreme groups
    early_b = [m['b_mean'] for m in a_early_5]
    late_b = [m['b_mean'] for m in a_late_5]
    u_stat, mw_p = stats.mannwhitneyu(early_b, late_b, alternative='two-sided')
    print(f"Mann-Whitney (A-early vs A-late in B): p = {mw_p:.4f}")

    if a_early_b_mean < a_late_b_mean - 0.05:
        print("** Ordering PRESERVED: A-early->B-early, A-late->B-late **")
    elif a_early_b_mean > a_late_b_mean + 0.05:
        print("** Ordering INVERTED: A-early->B-late, A-late->B-early **")
    else:
        print("No clear ordering relationship at extremes")

    # =========================================================================
    # Pattern 5: Hub position analysis
    # =========================================================================
    print("\n" + "-"*50)
    print("PATTERN 5: HUB POSITION INVARIANCE")
    print("-"*50)

    hubs = ['iin', 'ol', 's', 'or', 'y']

    print("\nHub positions in A vs B:")
    print(f"{'Hub':<10} {'A pos':<10} {'B pos':<10} {'Diff':<10} {'Zone A':<10} {'Zone B':<10}")
    print("-"*60)

    hub_diffs = []
    hub_same_zone = 0
    for hub in hubs:
        if hub in a_positions and hub in b_positions:
            a_mean = np.mean(a_positions[hub])
            b_mean = np.mean(b_positions[hub])
            diff = abs(a_mean - b_mean)
            hub_diffs.append(diff)
            a_z = get_zone(a_mean)
            b_z = get_zone(b_mean)
            if a_z == b_z:
                hub_same_zone += 1
            print(f"{hub:<10} {a_mean:<10.3f} {b_mean:<10.3f} {diff:<10.3f} {a_z:<10} {b_z:<10}")

    if hub_diffs:
        mean_hub_diff = np.mean(hub_diffs)
        non_hub_diffs = [abs(m['a_mean'] - m['b_mean']) for m in shared_middles
                        if m['middle'] not in hubs]
        mean_non_hub_diff = np.mean(non_hub_diffs) if non_hub_diffs else 0

        print(f"\nMean position difference:")
        print(f"  Hubs: {mean_hub_diff:.3f}")
        print(f"  Non-hubs: {mean_non_hub_diff:.3f}")
        print(f"  Hubs in same zone: {hub_same_zone}/{len(hub_diffs)}")

    # =========================================================================
    # Pattern 6: Quadrant analysis
    # =========================================================================
    print("\n" + "-"*50)
    print("PATTERN 6: QUADRANT ANALYSIS")
    print("-"*50)

    # 2x2: A-early/late vs B-early/late
    quadrants = {'EE': 0, 'EL': 0, 'LE': 0, 'LL': 0}
    for m in shared_middles:
        a_half = 'E' if m['a_mean'] < 0.5 else 'L'
        b_half = 'E' if m['b_mean'] < 0.5 else 'L'
        quadrants[a_half + b_half] += 1

    print("\nQuadrant distribution (E=early half, L=late half):")
    print(f"  A-Early, B-Early (EE): {quadrants['EE']}")
    print(f"  A-Early, B-Late (EL): {quadrants['EL']}")
    print(f"  A-Late, B-Early (LE): {quadrants['LE']}")
    print(f"  A-Late, B-Late (LL): {quadrants['LL']}")

    diagonal = quadrants['EE'] + quadrants['LL']
    off_diagonal = quadrants['EL'] + quadrants['LE']
    total = diagonal + off_diagonal

    print(f"\nDiagonal (preserved): {diagonal}/{total} ({100*diagonal/total:.1f}%)")
    print(f"Off-diagonal (flipped): {off_diagonal}/{total} ({100*off_diagonal/total:.1f}%)")

    # Binomial test for diagonal dominance
    diag_result = binomtest(diagonal, total, 0.5, alternative='greater')
    diag_p = diag_result.pvalue
    print(f"Binomial test (diagonal > 50%): p = {diag_p:.4f}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "="*70)
    print("SUMMARY: A-B POSITIONAL MAPPING")
    print("="*70)

    findings = []

    if p < 0.05:
        if r > 0:
            findings.append(f"LINEAR POSITIVE: r={r:.2f}, p={p:.4f}")
        else:
            findings.append(f"LINEAR NEGATIVE: r={r:.2f}, p={p:.4f}")

    if binom_p < 0.05:
        findings.append(f"ZONE PRESERVATION: {pct_same:.0f}% same zone (vs 33% chance)")

    if diag_p < 0.05:
        findings.append(f"QUADRANT PRESERVATION: {100*diagonal/total:.0f}% diagonal")

    if mw_p < 0.05:
        if a_early_b_mean < a_late_b_mean:
            findings.append("EXTREME ORDERING PRESERVED")
        else:
            findings.append("EXTREME ORDERING INVERTED")

    if not findings:
        findings.append("NO MAPPING: A and B positions appear independent")

    print("\nKey findings:")
    for i, f in enumerate(findings, 1):
        print(f"  {i}. {f}")

    # Determine verdict
    if any('POSITIVE' in f or 'PRESERVATION' in f for f in findings):
        verdict = "CONFIRMED"
        explanation = "A positional structure relates to B procedural order"
    elif any('NEGATIVE' in f or 'INVERTED' in f for f in findings):
        verdict = "CONFIRMED (INVERSE)"
        explanation = "A positional structure inversely relates to B order"
    else:
        verdict = "NOT SUPPORTED"
        explanation = "A and B positional structures are independent"

    print(f"\nVERDICT: {verdict}")
    print(f"  {explanation}")

# =========================================================================
# PREFIX-level analysis
# =========================================================================
print("\n" + "="*70)
print("PREFIX POSITION ANALYSIS")
print("="*70)

shared_prefixes = []
for prefix in a_prefix_positions:
    if prefix in b_prefix_positions:
        if len(a_prefix_positions[prefix]) >= 10 and len(b_prefix_positions[prefix]) >= 10:
            shared_prefixes.append({
                'prefix': prefix,
                'a_mean': np.mean(a_prefix_positions[prefix]),
                'b_mean': np.mean(b_prefix_positions[prefix]),
            })

print(f"\nShared PREFIXes with sufficient data: {len(shared_prefixes)}")

if shared_prefixes:
    print(f"\n{'PREFIX':<10} {'A pos':<10} {'B pos':<10} {'A zone':<10} {'B zone':<10}")
    print("-"*50)

    for pf in sorted(shared_prefixes, key=lambda x: x['a_mean']):
        a_z = get_zone(pf['a_mean'])
        b_z = get_zone(pf['b_mean'])
        print(f"{pf['prefix']:<10} {pf['a_mean']:<10.3f} {pf['b_mean']:<10.3f} {a_z:<10} {b_z:<10}")

    if len(shared_prefixes) >= 5:
        a_p = [p['a_mean'] for p in shared_prefixes]
        b_p = [p['b_mean'] for p in shared_prefixes]
        r_prefix, p_prefix = stats.pearsonr(a_p, b_p)
        print(f"\nPREFIX position correlation: r = {r_prefix:.3f} (p = {p_prefix:.4f})")

# Save results
output = {
    'n_shared_middles': len(shared_middles),
    'patterns': {},
    'findings': findings if len(shared_middles) >= 5 else [],
    'verdict': verdict if len(shared_middles) >= 5 else "INSUFFICIENT DATA",
}

if len(shared_middles) >= 5:
    output['patterns'] = {
        'linear': {'r': float(r), 'p': float(p)},
        'zone_preservation_pct': float(pct_same),
        'quadrant_diagonal_pct': float(100*diagonal/total),
        'a_early_b_mean': float(a_early_b_mean),
        'a_late_b_mean': float(a_late_b_mean),
    }

output_path = Path(__file__).parent.parent / 'results' / 'a_b_positional_mapping.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to {output_path}")
