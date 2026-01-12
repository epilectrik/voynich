"""
A-Type Navigation Through AZC

Trace how specific Currier A vocabulary navigates through AZC's positional structure.

Questions:
1. When A-types appear in AZC, which positions do they occupy?
2. Do certain A morphological classes cluster in certain AZC positions?
3. Is there a pattern to how A's deep structure maps to AZC's positional grammar?
"""

import json
from collections import defaultdict, Counter
from pathlib import Path
import csv


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'item'):
            return obj.item()
        return super().default(obj)


# Common prefixes for morphological analysis
KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

# Common middles (high-frequency cores)
CORE_MIDDLES = ['ai', 'ee', 'eo', 'e', 'o', 'a', 'ol', 'or', 'ar', 'al']

# Common suffixes
KNOWN_SUFFIXES = ['y', 'dy', 'n', 'in', 'iin', 'aiin', 'l', 'm', 'r', 's', 'g']


def decompose_simple(token):
    """Simple morphological decomposition."""
    if not token or len(token) < 2:
        return {'prefix': '', 'middle': token, 'suffix': ''}

    prefix = ''
    suffix = ''

    # Extract prefix
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    # Extract suffix
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break

    return {'prefix': prefix, 'middle': token, 'suffix': suffix}


def load_data_with_placement(filepath):
    """Load tokens with Currier classification and AZC placement codes."""
    a_types = set()
    azc_data = []  # list of (token, folio, placement, section)

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            section = row.get('section', '').strip()
            placement = row.get('placement', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # Collect A vocabulary
            if language == 'A' and section not in ('Z', 'A', 'C'):
                a_types.add(word)

            # Collect AZC tokens with placement
            is_azc = section in ('Z', 'A', 'C') or language not in ('A', 'B')
            if is_azc and placement:
                azc_data.append({
                    'token': word,
                    'folio': folio,
                    'placement': placement,
                    'section': section
                })

    return a_types, azc_data


def analyze_a_type_placement(a_types, azc_data):
    """Analyze where A-types appear in AZC placement structure."""
    # Filter to A-types that appear in AZC
    a_in_azc = []
    for record in azc_data:
        if record['token'] in a_types:
            a_in_azc.append(record)

    print(f"\nA-types appearing in AZC: {len(set(r['token'] for r in a_in_azc))} types")
    print(f"Total A-type occurrences in AZC: {len(a_in_azc)} tokens")

    # Placement distribution for A-types
    placement_dist = Counter(r['placement'] for r in a_in_azc)

    print("\nA-type placement distribution in AZC:")
    print(f"{'Placement':<10} {'Count':>8} {'%':>8}")
    print("-"*30)
    for placement, count in placement_dist.most_common():
        pct = count / len(a_in_azc) * 100
        print(f"{placement:<10} {count:>8} {pct:>7.1f}%")

    return a_in_azc, placement_dist


def analyze_morphology_by_placement(a_in_azc):
    """Analyze morphological patterns by AZC placement."""
    # Group by placement
    by_placement = defaultdict(list)
    for record in a_in_azc:
        by_placement[record['placement']].append(record['token'])

    print("\n" + "="*60)
    print("MORPHOLOGICAL ANALYSIS BY PLACEMENT")
    print("="*60)

    results = {}

    for placement in sorted(by_placement.keys()):
        tokens = by_placement[placement]
        if len(tokens) < 10:
            continue

        # Decompose all tokens
        decomps = [decompose_simple(t) for t in tokens]

        # Count prefixes
        prefix_counts = Counter(d['prefix'] for d in decomps if d['prefix'])
        # Count suffixes
        suffix_counts = Counter(d['suffix'] for d in decomps if d['suffix'])

        # Calculate escape rate (qo prefix)
        qo_count = sum(1 for t in tokens if t.startswith('qo'))
        escape_rate = qo_count / len(tokens) * 100

        results[placement] = {
            'token_count': len(tokens),
            'escape_rate': round(escape_rate, 2),
            'top_prefixes': prefix_counts.most_common(5),
            'top_suffixes': suffix_counts.most_common(5),
            'unique_types': len(set(tokens))
        }

        print(f"\n{placement}: {len(tokens)} tokens, {len(set(tokens))} types")
        print(f"  Escape rate: {escape_rate:.1f}%")
        print(f"  Top prefixes: {prefix_counts.most_common(3)}")
        print(f"  Top suffixes: {suffix_counts.most_common(3)}")

    return results


def trace_specific_types(a_in_azc, high_freq_types):
    """Trace specific high-frequency A-types through AZC positions."""
    print("\n" + "="*60)
    print("TRACING SPECIFIC A-TYPES THROUGH AZC")
    print("="*60)

    results = {}

    for target_type in high_freq_types:
        occurrences = [r for r in a_in_azc if r['token'] == target_type]
        if not occurrences:
            continue

        placement_dist = Counter(r['placement'] for r in occurrences)
        folio_dist = Counter(r['folio'] for r in occurrences)

        results[target_type] = {
            'total_occurrences': len(occurrences),
            'unique_placements': len(placement_dist),
            'unique_folios': len(folio_dist),
            'placement_distribution': dict(placement_dist),
            'concentrated': len(placement_dist) <= 3
        }

        decomp = decompose_simple(target_type)

        print(f"\n'{target_type}' ({decomp['prefix']}|{decomp['middle']}|{decomp['suffix']})")
        print(f"  Occurrences: {len(occurrences)}")
        print(f"  Placements: {len(placement_dist)} unique")
        print(f"  Folios: {len(folio_dist)} unique")
        print(f"  Distribution: {dict(placement_dist.most_common(5))}")

        # Is it concentrated or distributed?
        if len(placement_dist) == 1:
            print(f"  --> LOCKED to {list(placement_dist.keys())[0]}")
        elif len(placement_dist) <= 3:
            print(f"  --> CONCENTRATED in few positions")
        else:
            print(f"  --> DISTRIBUTED across positions")

    return results


def analyze_prefix_class_placement(a_in_azc):
    """Analyze if A morphological classes cluster in AZC positions."""
    print("\n" + "="*60)
    print("PREFIX CLASS x PLACEMENT CROSS-TABULATION")
    print("="*60)

    # Build cross-tabulation
    crosstab = defaultdict(lambda: defaultdict(int))

    for record in a_in_azc:
        decomp = decompose_simple(record['token'])
        prefix = decomp['prefix'] if decomp['prefix'] else 'NULL'
        placement = record['placement']
        crosstab[prefix][placement] += 1

    # Get all placements
    all_placements = sorted(set(p for prefix_data in crosstab.values() for p in prefix_data.keys()))

    # Print header
    print(f"\n{'Prefix':<8}", end='')
    for p in all_placements[:8]:  # Limit to first 8 placements
        print(f"{p:>8}", end='')
    print()
    print("-" * (8 + 8*8))

    # Print rows
    for prefix in sorted(crosstab.keys(), key=lambda x: sum(crosstab[x].values()), reverse=True)[:15]:
        print(f"{prefix:<8}", end='')
        total = sum(crosstab[prefix].values())
        for p in all_placements[:8]:
            count = crosstab[prefix].get(p, 0)
            pct = count / total * 100 if total > 0 else 0
            print(f"{pct:>7.1f}%", end='')
        print()

    return dict(crosstab)


def main():
    data_path = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    print("Loading data...")
    a_types, azc_data = load_data_with_placement(data_path)

    print(f"  A vocabulary: {len(a_types)} types")
    print(f"  AZC records: {len(azc_data)} tokens")

    # Analysis 1: A-type placement distribution
    print("\n" + "="*60)
    print("ANALYSIS 1: A-TYPE PLACEMENT IN AZC")
    print("="*60)
    a_in_azc, placement_dist = analyze_a_type_placement(a_types, azc_data)

    # Analysis 2: Morphology by placement
    morph_results = analyze_morphology_by_placement(a_in_azc)

    # Analysis 3: Trace specific high-frequency A-types
    # These are the types that appear in many AZC folios (from F-AZC-011)
    high_freq = ['daiin', 'aiin', 'dar', 'ar', 'al', 'chol', 'or', 'dy', 'okal', 'dal']
    trace_results = trace_specific_types(a_in_azc, high_freq)

    # Analysis 4: Prefix class x placement
    crosstab = analyze_prefix_class_placement(a_in_azc)

    # Build output
    output = {
        'summary': {
            'a_types_in_azc': len(set(r['token'] for r in a_in_azc)),
            'a_occurrences_in_azc': len(a_in_azc),
            'placement_distribution': dict(placement_dist)
        },
        'morphology_by_placement': morph_results,
        'traced_types': trace_results,
        'interpretation': {}
    }

    # Interpret findings
    # Check if certain placements have higher/lower escape rates
    escape_by_placement = {p: v['escape_rate'] for p, v in morph_results.items()}
    if escape_by_placement:
        max_escape = max(escape_by_placement.values())
        min_escape = min(escape_by_placement.values())
        output['interpretation']['escape_variance'] = round(max_escape - min_escape, 2)

    # Check if types are concentrated or distributed
    concentrated = sum(1 for v in trace_results.values() if v.get('concentrated', False))
    distributed = len(trace_results) - concentrated
    output['interpretation']['concentrated_types'] = concentrated
    output['interpretation']['distributed_types'] = distributed

    # Save
    results_path = Path(__file__).parent.parent.parent / 'results' / 'azc_a_navigation.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)

    print(f"\n\nResults saved to {results_path}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  A-types in AZC: {output['summary']['a_types_in_azc']}")
    print(f"  Escape variance by placement: {output['interpretation'].get('escape_variance', 'N/A')}pp")
    print(f"  Concentrated types: {concentrated}/{len(trace_results)}")
    print(f"  Distributed types: {distributed}/{len(trace_results)}")


if __name__ == '__main__':
    main()
