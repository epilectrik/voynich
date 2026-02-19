"""
region_vocabulary_overlap.py

Tests whether Rosettes region vocabularies show adjacency-based overlap patterns.

Hypothesis: Corner rosettes represent "intersections" of adjacent cardinals.
If true, corner region MIDDLE vocabularies should overlap more with their
adjacent cardinal vocabularies than with non-adjacent ones.

Run from project root:
    python phases/ROSETTES_FUNCTIONAL_ANATOMY/scripts/region_vocabulary_overlap.py
"""

import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, RosettesAnalyzer


def get_region_middles(ra, morph, folio, region):
    """Get unique MIDDLE set for a single f85v2 region."""
    tokens = ra.get_tokens(folio, region)
    middles = set()
    for t in tokens:
        if not t.word or not t.word.strip():
            continue
        if '*' in t.word:
            continue
        r = morph.extract(t.word)
        if r.middle and r.middle != '_EMPTY_':
            middles.add(r.middle)
    return middles


def jaccard(set_a, set_b):
    """Compute Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    if union == 0:
        return 0.0
    return intersection / union


def print_matrix(labels, matrix, title):
    """Print a pairwise Jaccard matrix in ASCII-safe format."""
    print()
    print(title)
    print('-' * len(title))
    col_w = max(len(lb) for lb in labels)
    row_label_w = col_w

    # Header
    header = ' ' * (row_label_w + 2)
    for lb in labels:
        header += lb.rjust(col_w + 1)
    print(header)

    for i, row_lb in enumerate(labels):
        row = row_lb.rjust(row_label_w) + '  '
        for j, _ in enumerate(labels):
            val = matrix[i][j]
            row += f'{val:.3f}'.rjust(col_w + 1)
        print(row)


def main():
    print('Loading data...')

    # Load bridge middles
    bridge_path = ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(bridge_path, 'r', encoding='utf-8') as f:
        bridge_data = json.load(f)
    bridge_middles = set(bridge_data['t5_structural_profile']['bridge_middles'])
    print(f'Bridge middles loaded: {len(bridge_middles)}')

    ra = RosettesAnalyzer()
    morph = Morphology()

    folio = 'f85v2'
    all_regions = ['B1', 'B2', 'B3', 'C2', 'D1', 'M1', 'M2', 'M3',
                   'N1', 'N2', 'U1', 'U2', 'U3', 'V1', 'V2', 'W1']

    print(f'\nExtracting MIDDLE vocabularies for all {len(all_regions)} regions of {folio}...')

    region_middles = {}
    for region in all_regions:
        middles = get_region_middles(ra, morph, folio, region)
        region_middles[region] = middles
        print(f'  {region:4s}: {len(middles):3d} unique MIDDLEs  (from {len(ra.get_tokens(folio, region))} tokens)')

    # --- Pairwise Jaccard: individual regions ---
    print()
    print('PAIRWISE JACCARD (individual regions):')
    print('-' * 40)
    region_labels = all_regions
    n = len(region_labels)
    region_matrix = [[jaccard(region_middles[region_labels[i]], region_middles[region_labels[j]])
                      for j in range(n)] for i in range(n)]
    print_matrix(region_labels, region_matrix, 'Individual Region Jaccard Matrix')

    # --- Group-level MIDDLE sets (union of all regions in group) ---
    # Groups by letter prefix
    group_map = {}
    for region in all_regions:
        prefix = region[0]
        if prefix not in group_map:
            group_map[prefix] = set()
        group_map[prefix] |= region_middles[region]

    group_order = sorted(group_map.keys())

    print()
    print('GROUP-LEVEL MIDDLE SETS (union of all regions in group):')
    print('-' * 50)
    for g in group_order:
        regions_in_group = [r for r in all_regions if r[0] == g]
        print(f'  Group {g}  (regions: {", ".join(regions_in_group)}):  {len(group_map[g])} unique MIDDLEs')

    # --- Pairwise Jaccard: group level ---
    g_labels = group_order
    gn = len(g_labels)
    group_matrix = [[jaccard(group_map[g_labels[i]], group_map[g_labels[j]])
                     for j in range(gn)] for i in range(gn)]
    print_matrix(g_labels, group_matrix, 'Group-Level Jaccard Matrix')

    # --- DESCRIPTION regions: C2, N1+N2 combined, V1+V2 combined ---
    desc_regions = {
        'CENTER(C2)': region_middles['C2'],
        'NORTH(N1+N2)': region_middles['N1'] | region_middles['N2'],
        'SOUTH(V1+V2)': region_middles['V1'] | region_middles['V2'],
    }
    desc_labels = list(desc_regions.keys())
    dn = len(desc_labels)
    desc_matrix = [[jaccard(list(desc_regions.values())[i], list(desc_regions.values())[j])
                    for j in range(dn)] for i in range(dn)]
    print_matrix(desc_labels, desc_matrix, 'Description Regions Jaccard Matrix (C2, N1+N2, V1+V2)')

    # --- Closest/furthest group to CENTER (C2) ---
    center_middles = region_middles['C2']
    print()
    print('PROXIMITY TO CENTER (C2) - group-level Jaccard:')
    print('-' * 50)
    proximity = []
    for g in group_order:
        if g == 'C':
            continue  # skip self
        j_val = jaccard(center_middles, group_map[g])
        proximity.append((g, j_val))
    proximity.sort(key=lambda x: x[1], reverse=True)
    for rank, (g, j_val) in enumerate(proximity, 1):
        regions_in_group = [r for r in all_regions if r[0] == g]
        label = f'Group {g} ({", ".join(regions_in_group)})'
        print(f'  #{rank:2d}  {label:35s}  Jaccard={j_val:.4f}')

    closest_g, closest_j = proximity[0]
    furthest_g, furthest_j = proximity[-1]
    print()
    print(f'  Closest to CENTER:  Group {closest_g}  (Jaccard={closest_j:.4f})')
    print(f'  Furthest from CENTER: Group {furthest_g}  (Jaccard={furthest_j:.4f})')

    # --- Bridge middle overlap per region ---
    print()
    print('BRIDGE MIDDLE OVERLAP PER REGION:')
    print('-' * 50)
    for region in all_regions:
        middles = region_middles[region]
        if not middles:
            brate = 0.0
            n_bridge = 0
        else:
            n_bridge = len(middles & bridge_middles)
            brate = n_bridge / len(middles)
        print(f'  {region:4s}: {n_bridge:3d}/{len(middles):3d} bridge middles  ({brate*100:.1f}%)')

    # --- Summary: within-group vs between-group Jaccard ---
    print()
    print('WITHIN-GROUP vs BETWEEN-GROUP JACCARD (non-singleton groups):')
    print('-' * 60)
    multi_groups = [g for g in group_order if len([r for r in all_regions if r[0] == g]) > 1]
    for g in multi_groups:
        members = [r for r in all_regions if r[0] == g]
        if len(members) < 2:
            continue
        within_vals = []
        for i in range(len(members)):
            for j in range(i+1, len(members)):
                within_vals.append(jaccard(region_middles[members[i]], region_middles[members[j]]))
        avg_within = sum(within_vals) / len(within_vals) if within_vals else 0.0
        # Between: group vs all other groups
        other_groups = [og for og in multi_groups if og != g]
        between_vals = []
        for og in other_groups:
            between_vals.append(jaccard(group_map[g], group_map[og]))
        avg_between = sum(between_vals) / len(between_vals) if between_vals else 0.0
        print(f'  Group {g} (regions: {", ".join(members)}):')
        print(f'    avg within-group Jaccard:   {avg_within:.4f}')
        print(f'    avg between-group Jaccard:  {avg_between:.4f}')

    print()
    print('Done.')


if __name__ == '__main__':
    main()
