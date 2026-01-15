#!/usr/bin/env python3
"""
MIDDLE PROPERTY ANALYSIS

Question: Do MIDDLEs in A registers correlate with material PROPERTIES
          (aromatic, delicate, medicinal) rather than specific species?

Approach:
1. Extract all MIDDLEs from WATER_GENTLE A registers
2. Categorize MIDDLEs: shared (appear in 2+ registers) vs unique
3. Look for clustering patterns
4. Check if shared MIDDLEs could encode common properties

If CLASS/PROPERTY level:
- Many shared MIDDLEs encoding properties
- Unique MIDDLEs distinguish sub-classes

If INDIVIDUAL level:
- Few shared MIDDLEs
- Most MIDDLEs unique to each register
"""

import csv
import json
from collections import defaultdict, Counter
import math

# ============================================================
# LOAD DATA
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

def get_middle(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

def load_folio_middles():
    """Get MIDDLE tokens and their counts per A folio."""
    folio_middles = defaultdict(Counter)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()

            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            middle = get_middle(word)
            if middle and len(middle) > 1:
                folio_middles[folio][middle] += 1

    return folio_middles

def load_classifications():
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['a_folio_classifications']

# ============================================================
# ANALYSIS
# ============================================================

def main():
    print("=" * 70)
    print("MIDDLE PROPERTY ANALYSIS")
    print("=" * 70)
    print()
    print("Do MIDDLEs encode material PROPERTIES or individual IDENTITY?")
    print()

    # Load data
    folio_middles = load_folio_middles()
    classifications = load_classifications()

    # Get WATER_GENTLE folios
    gentle_folios = sorted([f for f, t in classifications.items() if t == 'WATER_GENTLE'])

    print(f"WATER_GENTLE A registers: {gentle_folios}")
    print()

    # Build MIDDLE inventory
    print("=" * 70)
    print("MIDDLE INVENTORY")
    print("=" * 70)
    print()

    # Collect all MIDDLEs and their folio distribution
    middle_to_folios = defaultdict(set)
    folio_to_middles = {}

    for folio in gentle_folios:
        middles = set(folio_middles[folio].keys())
        folio_to_middles[folio] = middles
        for m in middles:
            middle_to_folios[m].add(folio)

    # Categorize MIDDLEs by sharing
    all_middles = set(middle_to_folios.keys())

    shared_by_all = [m for m in all_middles if len(middle_to_folios[m]) == len(gentle_folios)]
    shared_by_most = [m for m in all_middles if 2 <= len(middle_to_folios[m]) < len(gentle_folios)]
    unique_to_one = [m for m in all_middles if len(middle_to_folios[m]) == 1]

    print(f"Total unique MIDDLEs across WATER_GENTLE: {len(all_middles)}")
    print()
    print(f"Shared by ALL {len(gentle_folios)} registers: {len(shared_by_all)}")
    print(f"Shared by 2-{len(gentle_folios)-1} registers: {len(shared_by_most)}")
    print(f"Unique to ONE register: {len(unique_to_one)}")
    print()

    # Percentages
    pct_shared_all = 100 * len(shared_by_all) / len(all_middles)
    pct_shared_some = 100 * len(shared_by_most) / len(all_middles)
    pct_unique = 100 * len(unique_to_one) / len(all_middles)

    print(f"Shared by all: {pct_shared_all:.1f}%")
    print(f"Shared by some: {pct_shared_some:.1f}%")
    print(f"Unique: {pct_unique:.1f}%")
    print()

    # Show shared MIDDLEs (potential property markers)
    print("=" * 70)
    print("SHARED MIDDLEs (potential PROPERTY markers)")
    print("=" * 70)
    print()

    if shared_by_all:
        print(f"MIDDLEs in ALL {len(gentle_folios)} WATER_GENTLE registers:")
        print(f"  {shared_by_all[:20]}")
        if len(shared_by_all) > 20:
            print(f"  ... and {len(shared_by_all) - 20} more")
        print()
        print("  These could encode: 'gentle processing required', 'first degree heat',")
        print("  'delicate material', etc. - properties COMMON to all gentle waters")
    else:
        print("  No MIDDLEs appear in ALL registers")
    print()

    if shared_by_most:
        print(f"MIDDLEs shared by 2-{len(gentle_folios)-1} registers:")
        # Group by sharing count
        by_count = defaultdict(list)
        for m in shared_by_most:
            by_count[len(middle_to_folios[m])].append(m)

        for count in sorted(by_count.keys(), reverse=True):
            middles = by_count[count]
            print(f"  Shared by {count}: {len(middles)} MIDDLEs")
            print(f"    Examples: {middles[:10]}")
        print()
        print("  These could encode SUB-CLASS properties (e.g., 'aromatic' vs 'medicinal')")
    print()

    # Unique MIDDLEs per register (distinguishing features)
    print("=" * 70)
    print("UNIQUE MIDDLEs (distinguishing features)")
    print("=" * 70)
    print()

    for folio in gentle_folios:
        unique = [m for m in folio_to_middles[folio] if len(middle_to_folios[m]) == 1]
        total = len(folio_to_middles[folio])
        pct = 100 * len(unique) / total if total > 0 else 0

        print(f"{folio}: {len(unique)}/{total} unique ({pct:.0f}%)")
        print(f"  Examples: {unique[:8]}")
        print()

    # Clustering analysis
    print("=" * 70)
    print("CLUSTERING ANALYSIS")
    print("=" * 70)
    print()

    print("Which registers share the most MIDDLEs? (potential sub-class groupings)")
    print()

    # Pairwise overlap
    overlaps = []
    for i, f1 in enumerate(gentle_folios):
        for f2 in gentle_folios[i+1:]:
            shared = len(folio_to_middles[f1] & folio_to_middles[f2])
            union = len(folio_to_middles[f1] | folio_to_middles[f2])
            jaccard = shared / union if union > 0 else 0
            overlaps.append((f1, f2, shared, jaccard))

    # Sort by overlap
    overlaps.sort(key=lambda x: -x[2])

    print("Highest overlaps (potential sub-class pairs):")
    for f1, f2, shared, jaccard in overlaps[:5]:
        print(f"  {f1} + {f2}: {shared} shared MIDDLEs (Jaccard {jaccard:.2f})")
    print()

    print("Lowest overlaps (most distinct):")
    for f1, f2, shared, jaccard in overlaps[-3:]:
        print(f"  {f1} + {f2}: {shared} shared MIDDLEs (Jaccard {jaccard:.2f})")
    print()

    # Try to identify clusters
    print("=" * 70)
    print("INFERRED SUB-CLASS STRUCTURE")
    print("=" * 70)
    print()

    # Find highest overlap pair as first cluster
    if overlaps:
        top = overlaps[0]
        cluster1 = {top[0], top[1]}

        # Find second cluster from remaining
        remaining = [f for f in gentle_folios if f not in cluster1]

        if len(remaining) >= 2:
            remaining_overlaps = [(f1, f2, s, j) for f1, f2, s, j in overlaps
                                  if f1 in remaining and f2 in remaining]
            if remaining_overlaps:
                top2 = max(remaining_overlaps, key=lambda x: x[2])
                cluster2 = {top2[0], top2[1]}
                remaining = [f for f in remaining if f not in cluster2]
            else:
                cluster2 = set()
        else:
            cluster2 = set(remaining)
            remaining = []

        print(f"Cluster 1 (highest internal overlap): {sorted(cluster1)}")
        print(f"Cluster 2: {sorted(cluster2)}")
        if remaining:
            print(f"Unclustered: {remaining}")
        print()

        # What do clusters share?
        if len(cluster1) >= 2:
            c1_folios = sorted(cluster1)
            c1_shared = folio_to_middles[c1_folios[0]]
            for f in c1_folios[1:]:
                c1_shared = c1_shared & folio_to_middles[f]
            print(f"Cluster 1 shared MIDDLEs: {len(c1_shared)}")
            print(f"  Examples: {list(c1_shared)[:10]}")
            print()

        if len(cluster2) >= 2:
            c2_folios = sorted(cluster2)
            c2_shared = folio_to_middles[c2_folios[0]]
            for f in c2_folios[1:]:
                c2_shared = c2_shared & folio_to_middles[f]
            print(f"Cluster 2 shared MIDDLEs: {len(c2_shared)}")
            print(f"  Examples: {list(c2_shared)[:10]}")

    print()

    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    # Decision logic
    if pct_shared_all > 30:
        print("HIGH shared-by-all rate ({:.0f}%) suggests:".format(pct_shared_all))
        print("  Strong COMMON PROPERTY encoding (e.g., 'gentle processing')")
        print("  MIDDLEs encode WHAT KIND of processing, shared across the class")
    elif pct_shared_all > 10:
        print("MODERATE shared-by-all rate ({:.0f}%) suggests:".format(pct_shared_all))
        print("  Some common property encoding with differentiation")
    else:
        print("LOW shared-by-all rate ({:.0f}%) suggests:".format(pct_shared_all))
        print("  Each register is highly specialized")
    print()

    if pct_unique > 50:
        print("HIGH unique rate ({:.0f}%) suggests:".format(pct_unique))
        print("  Strong DISTINGUISHING features per register")
        print("  Each A register has specific configuration vocabulary")
    else:
        print("MODERATE unique rate ({:.0f}%) suggests:".format(pct_unique))
        print("  Some specialization but significant vocabulary overlap")
    print()

    # Final verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()

    if pct_shared_all > 20 and pct_unique > 30:
        verdict = "PROPERTY-BASED CONFIGURATION"
        print("FINDING: MIDDLEs encode BOTH:")
        print("  1. Common properties (shared MIDDLEs) - 'this is gentle processing'")
        print("  2. Specific configuration (unique MIDDLEs) - 'for THIS sub-class'")
        print()
        print("A registers appear to specify MATERIAL PROPERTIES + SUB-CLASS,")
        print("not individual species identity.")
    elif pct_unique > 60:
        verdict = "INDIVIDUAL CONFIGURATION"
        print("FINDING: High uniqueness suggests individual-level specification")
        print("Each A register may configure for a specific material.")
    else:
        verdict = "MIXED / SUB-CLASS"
        print("FINDING: Moderate overlap suggests SUB-CLASS level specification")
        print("A registers group similar materials by processing requirements.")

    print()
    print(f"Verdict: {verdict}")

    # Save
    output = {
        'test': 'MIDDLE_PROPERTY_ANALYSIS',
        'water_gentle_folios': gentle_folios,
        'middle_counts': {
            'total': len(all_middles),
            'shared_by_all': len(shared_by_all),
            'shared_by_some': len(shared_by_most),
            'unique': len(unique_to_one),
        },
        'percentages': {
            'shared_all': pct_shared_all,
            'shared_some': pct_shared_some,
            'unique': pct_unique,
        },
        'verdict': verdict,
    }

    with open('results/middle_property_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to results/middle_property_analysis.json")

if __name__ == '__main__':
    main()
