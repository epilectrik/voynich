#!/usr/bin/env python3
"""
CLUSTER PROPERTY CORRELATION

Question: Do within-type clusters correlate with any observable structural properties?

We found clusters in WATER_GENTLE:
  Cluster 1: {f32r, f45v}
  Cluster 2: {f52v, f99v}

Can we identify what distinguishes these clusters WITHOUT asserting semantic labels?

Approach:
1. Look at the MIDDLEs shared WITHIN each cluster but NOT across clusters
2. Look at PREFIX profiles of clustered vs non-clustered folios
3. Look at token/line metrics as potential structural differentiators
4. Check if clusters share MIDDLEs with specific OTHER product types
"""

import csv
import json
from collections import defaultdict, Counter

# ============================================================
# LOAD DATA
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

def get_prefix(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return p
    return ''

def get_middle(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

def load_folio_data():
    """Load detailed per-folio data."""
    folio_tokens = defaultdict(list)
    folio_lines = defaultdict(set)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only - CRITICAL for clean data
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            line_num = row.get('line', '')

            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            folio_tokens[folio].append(word)
            if line_num:
                folio_lines[folio].add(line_num)

    return folio_tokens, folio_lines

def load_classifications():
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['a_folio_classifications']

# ============================================================
# ANALYSIS
# ============================================================

def analyze_cluster_properties(cluster, folio_tokens, folio_lines, all_type_middles, type_middles_by_folio):
    """Analyze structural properties of a cluster."""

    # 1. Basic metrics
    metrics = {}
    for folio in cluster:
        tokens = folio_tokens.get(folio, [])
        lines = folio_lines.get(folio, set())

        prefix_counts = Counter(get_prefix(t) for t in tokens)
        middle_counts = Counter(get_middle(t) for t in tokens)

        metrics[folio] = {
            'n_tokens': len(tokens),
            'n_lines': len(lines),
            'tokens_per_line': len(tokens) / len(lines) if lines else 0,
            'unique_middles': len(middle_counts),
            'prefix_profile': dict(prefix_counts),
            'top_prefixes': prefix_counts.most_common(5),
            'middles': set(middle_counts.keys()),
        }

    # 2. Shared MIDDLEs within cluster
    if len(cluster) >= 2:
        shared_middles = metrics[cluster[0]]['middles']
        for folio in cluster[1:]:
            shared_middles = shared_middles & metrics[folio]['middles']
    else:
        shared_middles = set()

    # 3. Check overlap with other types
    type_overlap = {}
    for ptype, type_mids in all_type_middles.items():
        overlap = len(shared_middles & type_mids)
        type_overlap[ptype] = overlap

    return {
        'folio_metrics': metrics,
        'shared_middles': list(shared_middles)[:20],
        'n_shared': len(shared_middles),
        'type_overlap': type_overlap,
    }

def main():
    print("=" * 70)
    print("CLUSTER PROPERTY CORRELATION")
    print("=" * 70)
    print()
    print("Analyzing structural properties of WATER_GENTLE clusters")
    print()

    # Load data
    folio_tokens, folio_lines = load_folio_data()
    classifications = load_classifications()

    # Get all product type MIDDLE inventories
    all_type_middles = defaultdict(set)
    type_middles_by_folio = defaultdict(lambda: defaultdict(set))

    for folio in folio_tokens:
        ptype = classifications.get(folio)
        if ptype:
            for token in folio_tokens[folio]:
                middle = get_middle(token)
                if middle and len(middle) > 1:
                    all_type_middles[ptype].add(middle)
                    type_middles_by_folio[ptype][folio].add(middle)

    # Define clusters (from previous analysis)
    cluster1 = ['f32r', 'f45v']
    cluster2 = ['f52v', 'f99v']
    singletons = ['f17r', 'f90v2']

    gentle_folios = cluster1 + cluster2 + singletons

    print("WATER_GENTLE folios and clusters:")
    print(f"  Cluster 1: {cluster1}")
    print(f"  Cluster 2: {cluster2}")
    print(f"  Singletons: {singletons}")
    print()

    # Analyze each cluster
    print("=" * 70)
    print("CLUSTER 1 ANALYSIS")
    print("=" * 70)
    print()

    c1_analysis = analyze_cluster_properties(cluster1, folio_tokens, folio_lines,
                                              all_type_middles, type_middles_by_folio)

    for folio in cluster1:
        m = c1_analysis['folio_metrics'][folio]
        print(f"{folio}:")
        print(f"  Tokens: {m['n_tokens']}, Lines: {m['n_lines']}, Tokens/line: {m['tokens_per_line']:.1f}")
        print(f"  Top prefixes: {m['top_prefixes']}")
        print()

    print(f"Shared MIDDLEs within cluster: {c1_analysis['n_shared']}")
    print(f"  Examples: {c1_analysis['shared_middles'][:10]}")
    print()

    print("Cluster 1 overlap with other types:")
    for ptype, count in sorted(c1_analysis['type_overlap'].items(), key=lambda x: -x[1]):
        if ptype != 'WATER_GENTLE':
            print(f"  {ptype}: {count} shared MIDDLEs")
    print()

    print("=" * 70)
    print("CLUSTER 2 ANALYSIS")
    print("=" * 70)
    print()

    c2_analysis = analyze_cluster_properties(cluster2, folio_tokens, folio_lines,
                                              all_type_middles, type_middles_by_folio)

    for folio in cluster2:
        m = c2_analysis['folio_metrics'][folio]
        print(f"{folio}:")
        print(f"  Tokens: {m['n_tokens']}, Lines: {m['n_lines']}, Tokens/line: {m['tokens_per_line']:.1f}")
        print(f"  Top prefixes: {m['top_prefixes']}")
        print()

    print(f"Shared MIDDLEs within cluster: {c2_analysis['n_shared']}")
    print(f"  Examples: {c2_analysis['shared_middles'][:10]}")
    print()

    print("Cluster 2 overlap with other types:")
    for ptype, count in sorted(c2_analysis['type_overlap'].items(), key=lambda x: -x[1]):
        if ptype != 'WATER_GENTLE':
            print(f"  {ptype}: {count} shared MIDDLEs")
    print()

    # Compare clusters
    print("=" * 70)
    print("CLUSTER COMPARISON")
    print("=" * 70)
    print()

    # Metric comparison
    c1_avg_tpl = sum(c1_analysis['folio_metrics'][f]['tokens_per_line'] for f in cluster1) / len(cluster1)
    c2_avg_tpl = sum(c2_analysis['folio_metrics'][f]['tokens_per_line'] for f in cluster2) / len(cluster2)

    print(f"Average tokens/line:")
    print(f"  Cluster 1: {c1_avg_tpl:.1f}")
    print(f"  Cluster 2: {c2_avg_tpl:.1f}")
    print()

    # Shared MIDDLEs between clusters
    c1_shared = set(c1_analysis['shared_middles'])
    c2_shared = set(c2_analysis['shared_middles'])
    between_clusters = c1_shared & c2_shared

    print(f"MIDDLEs shared BETWEEN clusters: {len(between_clusters)}")
    if between_clusters:
        print(f"  {list(between_clusters)[:10]}")
    print()

    # Type affinity
    print("Type affinity (which cluster is closer to which other type?):")
    print()

    for ptype in ['WATER_STANDARD', 'OIL_RESIN', 'PRECISION']:
        c1_overlap = c1_analysis['type_overlap'].get(ptype, 0)
        c2_overlap = c2_analysis['type_overlap'].get(ptype, 0)

        if c1_overlap > c2_overlap:
            closer = "Cluster 1"
        elif c2_overlap > c1_overlap:
            closer = "Cluster 2"
        else:
            closer = "Equal"

        print(f"  {ptype}: C1={c1_overlap}, C2={c2_overlap} -> {closer}")
    print()

    # Singleton analysis
    print("=" * 70)
    print("SINGLETON ANALYSIS")
    print("=" * 70)
    print()

    for folio in singletons:
        tokens = folio_tokens.get(folio, [])
        lines = folio_lines.get(folio, set())
        middles = set(get_middle(t) for t in tokens if len(get_middle(t)) > 1)

        print(f"{folio}:")
        print(f"  Tokens: {len(tokens)}, Lines: {len(lines)}")

        # Which cluster is it closer to?
        c1_overlap = len(middles & set(c1_analysis['shared_middles']))
        c2_overlap = len(middles & set(c2_analysis['shared_middles']))

        print(f"  Overlap with Cluster 1 shared: {c1_overlap}")
        print(f"  Overlap with Cluster 2 shared: {c2_overlap}")

        if c1_overlap > c2_overlap:
            print(f"  -> Closer to Cluster 1")
        elif c2_overlap > c1_overlap:
            print(f"  -> Closer to Cluster 2")
        else:
            print(f"  -> Equidistant")
        print()

    # Structural interpretation
    print("=" * 70)
    print("STRUCTURAL INTERPRETATION (no semantic labels)")
    print("=" * 70)
    print()

    # Check for patterns
    c1_precision = c1_analysis['type_overlap'].get('PRECISION', 0)
    c1_oil = c1_analysis['type_overlap'].get('OIL_RESIN', 0)
    c1_standard = c1_analysis['type_overlap'].get('WATER_STANDARD', 0)

    c2_precision = c2_analysis['type_overlap'].get('PRECISION', 0)
    c2_oil = c2_analysis['type_overlap'].get('OIL_RESIN', 0)
    c2_standard = c2_analysis['type_overlap'].get('WATER_STANDARD', 0)

    print("Cluster 1 profile:")
    print(f"  WATER_STANDARD affinity: {c1_standard}")
    print(f"  PRECISION affinity: {c1_precision}")
    print(f"  OIL_RESIN affinity: {c1_oil}")
    print()

    print("Cluster 2 profile:")
    print(f"  WATER_STANDARD affinity: {c2_standard}")
    print(f"  PRECISION affinity: {c2_precision}")
    print(f"  OIL_RESIN affinity: {c2_oil}")
    print()

    # Interpretation
    if c1_standard > c2_standard and c1_precision > c2_precision:
        print("Pattern: Cluster 1 is structurally closer to WATER_STANDARD/PRECISION")
        print("         Cluster 2 is more isolated within WATER_GENTLE")
        print()
        print("Possible interpretation:")
        print("  Cluster 1: 'gentle materials that share some standard procedures'")
        print("  Cluster 2: 'distinctly gentle materials with unique vocabulary'")
    elif c2_standard > c1_standard:
        print("Pattern: Cluster 2 is closer to WATER_STANDARD")
        print("         Cluster 1 is more isolated")
    else:
        print("Pattern: Mixed or unclear clustering basis")

    print()

    # Final verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()

    if c1_analysis['n_shared'] > 10 and c2_analysis['n_shared'] > 10:
        print("SUB-CLASS STRUCTURE CONFIRMED")
        print()
        print("WATER_GENTLE contains at least 2 structural sub-classes:")
        print(f"  Sub-class A: {cluster1} (share {c1_analysis['n_shared']} MIDDLEs)")
        print(f"  Sub-class B: {cluster2} (share {c2_analysis['n_shared']} MIDDLEs)")
        print()
        print("These sub-classes differ in:")
        print("  - Shared vocabulary (cluster-internal MIDDLEs)")
        print("  - Type affinity (which other product types they overlap with)")
        print()
        print("This supports the hypothesis that A registers specify at")
        print("SUB-CLASS level, not individual material or broad class level.")
        verdict = "SUBCLASS_CONFIRMED"
    else:
        print("Weak clustering - sub-class structure not strongly supported")
        verdict = "WEAK"

    # Save results
    output = {
        'test': 'CLUSTER_PROPERTY_CORRELATION',
        'clusters': {
            'cluster1': cluster1,
            'cluster2': cluster2,
            'singletons': singletons
        },
        'cluster1_analysis': {
            'n_shared_middles': c1_analysis['n_shared'],
            'type_overlap': c1_analysis['type_overlap'],
        },
        'cluster2_analysis': {
            'n_shared_middles': c2_analysis['n_shared'],
            'type_overlap': c2_analysis['type_overlap'],
        },
        'verdict': verdict,
    }

    with open('results/cluster_property_correlation.json', 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Results saved to results/cluster_property_correlation.json")

if __name__ == '__main__':
    main()
