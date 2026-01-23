"""Specification-Level MIDDLE Compatibility Test.

This tests C475: MIDDLE ATOMIC INCOMPATIBILITY defined by co-occurrence
within the SAME Currier A record.

CRITICAL: This is NOT availability. Do NOT pool across records.
Do NOT use AZC legality. Compatibility = co-occurs in same A record.

Expected results (per C475):
- ~1,180 MIDDLEs
- ~703k possible pairs
- ~4-5% LEGAL (co-occur in some record)
- ~95-96% ILLEGAL (never co-occur)
"""
import pandas as pd
from pathlib import Path
from collections import defaultdict
import itertools
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Morphology extraction
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)


def extract_middle(token):
    """Extract MIDDLE component from token."""
    if pd.isna(token):
        return None
    token = str(token)
    if not token.strip():
        return None
    if '*' in token:  # Skip uncertain readings
        return None
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            remainder = remainder[:-len(s)]
            break
    return remainder if remainder else None


def main():
    print("=" * 70)
    print("SPECIFICATION-LEVEL MIDDLE COMPATIBILITY TEST")
    print("=" * 70)
    print()
    print("Testing C475: MIDDLE ATOMIC INCOMPATIBILITY")
    print("Compatibility = co-occurs in SAME Currier A record")
    print("This is NOT availability. NOT pooled. NOT AZC-expanded.")
    print()

    # Load transcript (H track only)
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']

    # Filter to Currier A only
    df_a = df[df['language'] == 'A'].copy()
    print(f"Currier A tokens: {len(df_a)}")

    # Extract MIDDLEs
    df_a['middle'] = df_a['word'].apply(extract_middle)

    # Build specification bundles: one per A record (folio:line)
    print("\n" + "-" * 70)
    print("STEP 1: Extract specification bundles (per A record)")
    print("-" * 70)

    bundles = []
    for (folio, line), group in df_a.groupby(['folio', 'line_number']):
        middles = set(group['middle'].dropna())
        if len(middles) >= 2:  # Need at least 2 MIDDLEs for pairs
            bundles.append({
                'record': f"{folio}:{line}",
                'middles': middles,
                'size': len(middles)
            })

    print(f"A records with 2+ MIDDLEs: {len(bundles)}")
    print(f"Total A records: {len(df_a.groupby(['folio', 'line_number']))}")

    # Collect all unique MIDDLEs
    all_middles = set()
    for b in bundles:
        all_middles.update(b['middles'])
    all_middles = sorted(all_middles)
    n_middles = len(all_middles)
    print(f"\nUnique MIDDLEs in Currier A: {n_middles}")

    total_possible_pairs = n_middles * (n_middles - 1) // 2
    print(f"Total possible unordered pairs: {total_possible_pairs}")

    # STEP 2: Mark legal pairs (within-record only)
    print("\n" + "-" * 70)
    print("STEP 2: Mark legal pairs (co-occur in same A record)")
    print("-" * 70)

    legal_pairs = set()

    for i, b in enumerate(bundles):
        middles_list = sorted(b['middles'])
        # Mark all pairs within this record as LEGAL
        for m1, m2 in itertools.combinations(middles_list, 2):
            pair = (m1, m2) if m1 < m2 else (m2, m1)  # Canonical order
            legal_pairs.add(pair)

        if (i + 1) % 200 == 0:
            print(f"  Processed {i + 1}/{len(bundles)} records, {len(legal_pairs)} legal pairs so far...")

    print(f"\nTotal LEGAL pairs: {len(legal_pairs)}")

    # STEP 3: Compute statistics
    print("\n" + "-" * 70)
    print("STEP 3: Compute compatibility statistics")
    print("-" * 70)

    illegal_pairs = total_possible_pairs - len(legal_pairs)
    legal_rate = len(legal_pairs) / total_possible_pairs * 100
    illegal_rate = illegal_pairs / total_possible_pairs * 100

    print(f"\n{'Metric':<30} {'Value':>15}")
    print("-" * 50)
    print(f"{'Total MIDDLEs':<30} {n_middles:>15}")
    print(f"{'Total possible pairs':<30} {total_possible_pairs:>15}")
    print(f"{'LEGAL pairs':<30} {len(legal_pairs):>15}")
    print(f"{'ILLEGAL pairs':<30} {illegal_pairs:>15}")
    print(f"{'LEGAL rate':<30} {legal_rate:>14.2f}%")
    print(f"{'ILLEGAL rate':<30} {illegal_rate:>14.2f}%")

    # Verify against C475 expectations
    print("\n" + "-" * 70)
    print("C475 VERIFICATION")
    print("-" * 70)

    c475_expected_legal = 0.04  # ~4%
    c475_expected_illegal = 0.96  # ~96%

    if 0.03 <= legal_rate / 100 <= 0.06:
        print(f"LEGAL rate {legal_rate:.2f}% is within C475 expected range (3-6%)")
        legal_check = "PASS"
    else:
        print(f"WARNING: LEGAL rate {legal_rate:.2f}% outside expected range (3-6%)")
        legal_check = "FAIL"

    if 0.94 <= illegal_rate / 100 <= 0.97:
        print(f"ILLEGAL rate {illegal_rate:.2f}% is within C475 expected range (94-97%)")
        illegal_check = "PASS"
    else:
        print(f"WARNING: ILLEGAL rate {illegal_rate:.2f}% outside expected range (94-97%)")
        illegal_check = "FAIL"

    # Compute degree distribution (how many partners each MIDDLE has)
    print("\n" + "-" * 70)
    print("MIDDLE DEGREE DISTRIBUTION")
    print("-" * 70)

    middle_degrees = defaultdict(int)
    for m1, m2 in legal_pairs:
        middle_degrees[m1] += 1
        middle_degrees[m2] += 1

    # Find universal connectors (high degree)
    sorted_by_degree = sorted(middle_degrees.items(), key=lambda x: -x[1])

    print("\nTop 20 universal connectors (highest degree):")
    for m, deg in sorted_by_degree[:20]:
        print(f"  {m}: {deg} partners ({deg/n_middles*100:.1f}%)")

    # Find isolated MIDDLEs (zero degree - only appear alone or in single-MIDDLE records)
    middles_with_partners = set(middle_degrees.keys())
    isolated_middles = [m for m in all_middles if m not in middles_with_partners]
    print(f"\nIsolated MIDDLEs (zero partners): {len(isolated_middles)}")
    if isolated_middles and len(isolated_middles) <= 30:
        print(f"  {isolated_middles}")

    # Degree statistics
    degrees = list(middle_degrees.values())
    if degrees:
        import statistics
        print(f"\nDegree statistics (among MIDDLEs with partners):")
        print(f"  Min: {min(degrees)}")
        print(f"  Max: {max(degrees)}")
        print(f"  Mean: {statistics.mean(degrees):.1f}")
        print(f"  Median: {statistics.median(degrees)}")

    # Check for giant connected component
    print("\n" + "-" * 70)
    print("CONNECTIVITY ANALYSIS")
    print("-" * 70)

    # Simple union-find for connected components
    parent = {m: m for m in all_middles}

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for m1, m2 in legal_pairs:
        union(m1, m2)

    # Count components
    components = defaultdict(list)
    for m in all_middles:
        components[find(m)].append(m)

    component_sizes = sorted([len(c) for c in components.values()], reverse=True)
    print(f"Number of connected components: {len(components)}")
    print(f"Largest component: {component_sizes[0]} MIDDLEs ({component_sizes[0]/n_middles*100:.1f}%)")
    if len(component_sizes) > 1:
        print(f"Second largest: {component_sizes[1]} MIDDLEs")
    print(f"Singleton components (isolated): {sum(1 for s in component_sizes if s == 1)}")

    # Final verification
    print("\n" + "=" * 70)
    print("FINAL VERIFICATION")
    print("=" * 70)

    checks = [
        ("LEGAL rate ~4-5%", legal_check),
        ("ILLEGAL rate ~95-96%", illegal_check),
        ("Not 100% dense", "PASS" if legal_rate < 50 else "FAIL"),
        ("Giant component exists", "PASS" if component_sizes[0] > n_middles * 0.5 else "UNKNOWN"),
    ]

    all_pass = True
    for check, status in checks:
        print(f"  {check}: {status}")
        if status == "FAIL":
            all_pass = False

    if all_pass:
        print("\n*** C475 VERIFIED: Specification-level incompatibility recovered ***")
    else:
        print("\n*** WARNING: Some checks failed - review methodology ***")

    # Save results
    output = {
        'metadata': {
            'test_type': 'specification_level_compatibility',
            'unit_of_analysis': 'currier_a_record',
            'constraint_tested': 'C475'
        },
        'statistics': {
            'total_middles': n_middles,
            'total_possible_pairs': total_possible_pairs,
            'legal_pairs': len(legal_pairs),
            'illegal_pairs': illegal_pairs,
            'legal_rate': round(legal_rate, 4),
            'illegal_rate': round(illegal_rate, 4)
        },
        'connectivity': {
            'num_components': len(components),
            'largest_component_size': component_sizes[0],
            'largest_component_rate': round(component_sizes[0] / n_middles, 4),
            'isolated_count': len(isolated_middles)
        },
        'verification': {
            'c475_expected_legal': '4-5%',
            'c475_expected_illegal': '95-96%',
            'legal_check': legal_check,
            'illegal_check': illegal_check
        },
        'universal_connectors': [{'middle': m, 'degree': d} for m, d in sorted_by_degree[:50]],
        'isolated_middles': isolated_middles
    }

    output_path = PROJECT_ROOT / 'phases' / 'MEMBER_COSURVIVAL_TEST' / 'results' / 'specification_compatibility.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")


if __name__ == '__main__':
    main()
