#!/usr/bin/env python3
"""
A_SECTION_T_CHARACTERIZATION - Test A: AZC Zone Distribution

Test whether Section T vocabulary concentrates in S-zone (boundary) positions
in AZC, which would explain why it appears in AZC but not B execution.

Zone semantics (from C443):
- C-zone: Setup/Loading (escape 1.4%)
- P-zone: Active work (escape 11.6%)
- R-zone: Progression/Restricting (escape declining to 0%)
- S-zone: Boundary/Collection (escape 0-3.8%, "no intervention permitted")
"""

import pandas as pd
import json
from pathlib import Path
from collections import Counter
from scipy import stats
import re

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
RESULTS_PATH = PROJECT_ROOT / 'phases' / 'A_SECTION_T_CHARACTERIZATION' / 'results'

# AZC folios
AZC_FOLIOS = ['f67r1', 'f67r2', 'f67v1', 'f67v2', 'f68r1', 'f68r2', 'f68r3',
              'f68v1', 'f68v2', 'f68v3', 'f69r1', 'f69r2', 'f69v1', 'f69v2',
              'f70r1', 'f70r2', 'f70v1', 'f70v2', 'f71r', 'f71v', 'f72r1',
              'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v']

SECTION_T_A_FOLIOS = ['f1r', 'f58r', 'f58v']

# Morphology parsing
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta',
    'al', 'ar', 'or',
]
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

SUFFIXES = [
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy',
    'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey',
    'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey',
    'chol', 'shol', 'kol', 'tol',
    'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool',
    'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]


def extract_middle(token):
    """Extract MIDDLE from token."""
    if pd.isna(token):
        return None
    token = str(token)

    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break

    if not prefix:
        return None

    remainder = token[len(prefix):]

    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break

    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder

    if middle == '':
        middle = '_EMPTY_'

    return middle


def classify_zone(placement):
    """Classify placement code into zone (C, P, R, S, or OTHER)."""
    if pd.isna(placement):
        return 'OTHER'

    placement = str(placement).upper()

    # C-zone: Center positions
    if placement.startswith('C'):
        return 'C'

    # P-zone: Paragraph/Active text
    if placement.startswith('P'):
        return 'P'

    # R-zone: Ring/Restricting positions (R1, R2, R3, etc.)
    if placement.startswith('R'):
        return 'R'

    # S-zone: Star/Boundary positions
    if placement.startswith('S'):
        return 'S'

    # L-zone: Labels (often boundary-like)
    if placement.startswith('L'):
        return 'L'

    return 'OTHER'


def main():
    print("=" * 70)
    print("TEST A: AZC ZONE DISTRIBUTION")
    print("=" * 70)
    print()

    # Load data
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H'].copy()

    # Parse MIDDLEs
    df['middle'] = df['word'].apply(extract_middle)

    # Get Section T MIDDLEs
    df_a = df[df['language'] == 'A']
    df_t = df_a[df_a['folio'].isin(SECTION_T_A_FOLIOS)]
    t_middles = set(df_t['middle'].dropna().unique())

    print(f"Section T unique MIDDLEs: {len(t_middles)}")

    # Get AZC data
    df_azc = df[df['folio'].isin(AZC_FOLIOS)].copy()
    df_azc['zone'] = df_azc['placement'].apply(classify_zone)

    print(f"Total AZC tokens: {len(df_azc)}")
    print()

    # Baseline zone distribution (all AZC)
    print("=== BASELINE AZC ZONE DISTRIBUTION ===")
    baseline_zones = df_azc['zone'].value_counts()
    baseline_total = len(df_azc)

    print("Zone distribution (all AZC tokens):")
    for zone in ['C', 'P', 'R', 'S', 'L', 'OTHER']:
        count = baseline_zones.get(zone, 0)
        pct = count / baseline_total * 100
        print(f"  {zone}: {count:,} ({pct:.1f}%)")
    print()

    # Section T MIDDLEs in AZC
    df_azc_t = df_azc[df_azc['middle'].isin(t_middles)].copy()

    print(f"=== SECTION T MIDDLEs IN AZC ===")
    print(f"AZC tokens with Section T MIDDLEs: {len(df_azc_t)}")
    print()

    # Zone distribution for Section T MIDDLEs
    t_zones = df_azc_t['zone'].value_counts()
    t_total = len(df_azc_t)

    print("Zone distribution (Section T MIDDLEs in AZC):")
    for zone in ['C', 'P', 'R', 'S', 'L', 'OTHER']:
        count = t_zones.get(zone, 0)
        pct = count / t_total * 100 if t_total > 0 else 0
        baseline_pct = baseline_zones.get(zone, 0) / baseline_total * 100
        ratio = pct / baseline_pct if baseline_pct > 0 else 0
        enrichment = "ENRICHED" if ratio > 1.5 else "DEPLETED" if ratio < 0.67 else ""
        print(f"  {zone}: {count:,} ({pct:.1f}%) [baseline: {baseline_pct:.1f}%] {ratio:.2f}x {enrichment}")
    print()

    # Statistical test: Is S-zone enriched?
    print("=== S-ZONE ENRICHMENT TEST ===")

    # Contingency table: [T_S, T_non-S], [baseline_S, baseline_non-S]
    t_s = t_zones.get('S', 0)
    t_non_s = t_total - t_s
    baseline_s = baseline_zones.get('S', 0)
    baseline_non_s = baseline_total - baseline_s

    # Fisher's exact
    contingency = [[t_s, t_non_s], [baseline_s, baseline_non_s]]
    odds_ratio, p_value = stats.fisher_exact(contingency)

    print(f"Section T in S-zone: {t_s} / {t_total} ({t_s/t_total*100:.1f}%)")
    print(f"Baseline in S-zone: {baseline_s} / {baseline_total} ({baseline_s/baseline_total*100:.1f}%)")
    print(f"Fisher's exact: OR={odds_ratio:.3f}, p={p_value:.4f}")
    print()

    # Also test L-zone (labels, often boundary-like)
    print("=== L-ZONE (LABEL) ENRICHMENT TEST ===")

    t_l = t_zones.get('L', 0)
    t_non_l = t_total - t_l
    baseline_l = baseline_zones.get('L', 0)
    baseline_non_l = baseline_total - baseline_l

    contingency_l = [[t_l, t_non_l], [baseline_l, baseline_non_l]]
    odds_ratio_l, p_value_l = stats.fisher_exact(contingency_l)

    print(f"Section T in L-zone: {t_l} / {t_total} ({t_l/t_total*100:.1f}%)")
    print(f"Baseline in L-zone: {baseline_l} / {baseline_total} ({baseline_l/baseline_total*100:.1f}%)")
    print(f"Fisher's exact: OR={odds_ratio_l:.3f}, p={p_value_l:.4f}")
    print()

    # Combined boundary zones (S + L)
    print("=== COMBINED BOUNDARY ZONE (S+L) TEST ===")

    t_boundary = t_s + t_l
    t_non_boundary = t_total - t_boundary
    baseline_boundary = baseline_s + baseline_l
    baseline_non_boundary = baseline_total - baseline_boundary

    contingency_b = [[t_boundary, t_non_boundary], [baseline_boundary, baseline_non_boundary]]
    odds_ratio_b, p_value_b = stats.fisher_exact(contingency_b)

    t_boundary_pct = t_boundary / t_total * 100 if t_total > 0 else 0
    baseline_boundary_pct = baseline_boundary / baseline_total * 100

    print(f"Section T in boundary (S+L): {t_boundary} / {t_total} ({t_boundary_pct:.1f}%)")
    print(f"Baseline in boundary (S+L): {baseline_boundary} / {baseline_total} ({baseline_boundary_pct:.1f}%)")
    print(f"Fisher's exact: OR={odds_ratio_b:.3f}, p={p_value_b:.4f}")
    print()

    # Interior zones (C + P + R) - these should propagate to B
    print("=== INTERIOR ZONE (C+P+R) TEST ===")

    t_interior = t_zones.get('C', 0) + t_zones.get('P', 0) + t_zones.get('R', 0)
    baseline_interior = baseline_zones.get('C', 0) + baseline_zones.get('P', 0) + baseline_zones.get('R', 0)

    t_interior_pct = t_interior / t_total * 100 if t_total > 0 else 0
    baseline_interior_pct = baseline_interior / baseline_total * 100

    print(f"Section T in interior (C+P+R): {t_interior} / {t_total} ({t_interior_pct:.1f}%)")
    print(f"Baseline in interior (C+P+R): {baseline_interior} / {baseline_total} ({baseline_interior_pct:.1f}%)")
    print()

    # Per-MIDDLE analysis: which Section T MIDDLEs appear in which zones?
    print("=== PER-MIDDLE ZONE PROFILE ===")

    middle_zone_profile = {}
    for mid in t_middles:
        mid_azc = df_azc[df_azc['middle'] == mid]
        if len(mid_azc) == 0:
            continue
        zones = mid_azc['zone'].value_counts().to_dict()
        total = len(mid_azc)
        middle_zone_profile[mid] = {
            'total': total,
            'zones': zones,
            's_pct': zones.get('S', 0) / total * 100,
            'l_pct': zones.get('L', 0) / total * 100,
            'boundary_pct': (zones.get('S', 0) + zones.get('L', 0)) / total * 100,
        }

    # Sort by boundary percentage
    sorted_middles = sorted(middle_zone_profile.items(),
                           key=lambda x: x[1]['boundary_pct'],
                           reverse=True)

    print("Top 20 Section T MIDDLEs by boundary zone concentration:")
    print(f"{'MIDDLE':<15} {'Total':<8} {'Boundary%':<12} {'S%':<8} {'L%':<8} Zones")
    print("-" * 70)
    for mid, profile in sorted_middles[:20]:
        zones_str = ", ".join(f"{z}:{c}" for z, c in sorted(profile['zones'].items()))
        print(f"{mid:<15} {profile['total']:<8} {profile['boundary_pct']:<12.1f} {profile['s_pct']:<8.1f} {profile['l_pct']:<8.1f} {zones_str}")
    print()

    # How many Section T MIDDLEs are boundary-dominant (>50% in S+L)?
    boundary_dominant = sum(1 for p in middle_zone_profile.values() if p['boundary_pct'] > 50)
    interior_dominant = sum(1 for p in middle_zone_profile.values() if p['boundary_pct'] < 50)

    print(f"Boundary-dominant MIDDLEs (>50% S+L): {boundary_dominant}")
    print(f"Interior-dominant MIDDLEs (<50% S+L): {interior_dominant}")
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    s_enriched = odds_ratio > 1.5 and p_value < 0.05
    l_enriched = odds_ratio_l > 1.5 and p_value_l < 0.05
    boundary_enriched = odds_ratio_b > 1.5 and p_value_b < 0.05

    print(f"S-zone enriched: {'YES' if s_enriched else 'NO'} (OR={odds_ratio:.2f}, p={p_value:.4f})")
    print(f"L-zone enriched: {'YES' if l_enriched else 'NO'} (OR={odds_ratio_l:.2f}, p={p_value_l:.4f})")
    print(f"Boundary (S+L) enriched: {'YES' if boundary_enriched else 'NO'} (OR={odds_ratio_b:.2f}, p={p_value_b:.4f})")
    print()

    if boundary_enriched:
        conclusion = "S_ZONE_HYPOTHESIS_SUPPORTED"
        explanation = "Section T vocabulary IS enriched in boundary zones (S+L), supporting the scaffold hypothesis."
    else:
        conclusion = "S_ZONE_HYPOTHESIS_NOT_SUPPORTED"
        explanation = "Section T vocabulary is NOT enriched in boundary zones. The B-exclusion requires alternative explanation."

    print(f"CONCLUSION: {conclusion}")
    print(f"  {explanation}")

    # Save results
    results = {
        'baseline_zone_distribution': {
            zone: {'count': int(baseline_zones.get(zone, 0)),
                   'pct': baseline_zones.get(zone, 0) / baseline_total * 100}
            for zone in ['C', 'P', 'R', 'S', 'L', 'OTHER']
        },
        'section_t_zone_distribution': {
            zone: {'count': int(t_zones.get(zone, 0)),
                   'pct': t_zones.get(zone, 0) / t_total * 100 if t_total > 0 else 0}
            for zone in ['C', 'P', 'R', 'S', 'L', 'OTHER']
        },
        's_zone_test': {
            'odds_ratio': odds_ratio,
            'p_value': p_value,
            'enriched': s_enriched,
        },
        'l_zone_test': {
            'odds_ratio': odds_ratio_l,
            'p_value': p_value_l,
            'enriched': l_enriched,
        },
        'boundary_test': {
            'odds_ratio': odds_ratio_b,
            'p_value': p_value_b,
            'enriched': boundary_enriched,
            't_boundary_pct': t_boundary_pct,
            'baseline_boundary_pct': baseline_boundary_pct,
        },
        'per_middle_profiles': {k: v for k, v in sorted_middles[:50]},
        'boundary_dominant_count': boundary_dominant,
        'interior_dominant_count': interior_dominant,
        'conclusion': conclusion,
        'explanation': explanation,
    }

    with open(RESULTS_PATH / 'azc_zone_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print()
    print(f"Results saved to {RESULTS_PATH / 'azc_zone_analysis.json'}")


if __name__ == '__main__':
    main()
