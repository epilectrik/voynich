"""
F-AZC-014: A Morphology × AZC Structure Cross-Tabulation

PRE-REGISTERED HYPOTHESES:

H1 (PREFIX × AZC_FOLIO):
    Expected: WEAK/NULL correlation
    Rationale: C274 (prefixes combine freely), C441 (vocabulary-activated, not class-activated)
    If STRONG: Revise - material-class determines compatibility (coarse)
    If WEAK: Confirm - compatibility is finer-grained (MIDDLE-level)

H2 (MIDDLE × AZC_FOLIO):
    Expected: MODERATE-STRONG correlation
    Rationale: C423 (80% MIDDLEs prefix-exclusive), C442 (compatibility filter)
    If STRONG: Confirm - AZC filters at variant level
    If WEAK: Revise - compatibility is full-token emergent only

H3 (SUFFIX × AZC_POSITION):
    Expected: UNKNOWN (most important test)
    Rationale: Tests if decision archetypes are phase-indexed
    If STRONG: SUFFIXes encode phase-shaped decision types
    If WEAK: Phase binding happens entirely in AZC, not A

H4 (CLUSTER_STATUS × AZC_OVERLAP):
    Expected: MODERATE enrichment for clustered entries
    Rationale: C326 (1.31x A-reference sharing within clusters)
    If STRONG: A clustering reflects compatibility structure
    If WEAK: A clustering is registry ergonomics only

SUCCESS CRITERIA:
- Not looking for single "yes"
- Looking for WHERE THE SIGNAL LIVES
- Each outcome informs how to project A through AZC
"""

import json
import csv
from collections import defaultdict, Counter
from pathlib import Path
import math
from typing import Dict, List, Set, Tuple


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'item'):
            return obj.item()
        return super().default(obj)


# Morphological components (from existing analysis)
KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']
KNOWN_SUFFIXES = ['y', 'dy', 'n', 'in', 'iin', 'aiin', 'l', 'm', 'r', 's', 'g', 'am', 'an', 'ain']


def decompose_token(token: str) -> Dict[str, str]:
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return {'prefix': '', 'middle': token, 'suffix': ''}

    original = token
    prefix = ''
    suffix = ''

    # Extract prefix (longest match first)
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    # Extract suffix (longest match first)
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break

    return {'prefix': prefix, 'middle': token, 'suffix': suffix, 'original': original}


def load_data(filepath: Path) -> Tuple[List[Dict], Set[str]]:
    """Load all tokens with morphology, AZC info, and A-type status."""
    records = []
    a_types = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            section = row.get('section', '').strip()
            placement = row.get('placement', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # Track A-types (from non-AZC sections)
            if language == 'A' and section not in ('Z', 'A', 'C'):
                a_types.add(word)

            # Record AZC tokens
            is_azc = section in ('Z', 'A', 'C') or language not in ('A', 'B')
            if is_azc and placement:
                decomp = decompose_token(word)
                records.append({
                    'token': word,
                    'folio': folio,
                    'placement': placement,
                    'section': section,
                    'prefix': decomp['prefix'],
                    'middle': decomp['middle'],
                    'suffix': decomp['suffix']
                })

    return records, a_types


def load_a_clustering_status(filepath: Path) -> Dict[str, bool]:
    """
    Determine which A entries are clustered vs singleton.
    Clustered = adjacent entries share vocabulary.
    """
    # This requires reading A entries in order and checking adjacency
    # For now, we'll approximate using the existing clustering analysis
    # A proper implementation would trace entry boundaries

    # Placeholder - would need to implement from scratch or load from existing analysis
    return {}


def cramers_v(contingency: Dict[str, Dict[str, int]]) -> float:
    """Calculate Cramér's V for a contingency table."""
    # Flatten to get totals
    row_totals = {}
    col_totals = defaultdict(int)
    grand_total = 0

    for row_key, col_dict in contingency.items():
        row_totals[row_key] = sum(col_dict.values())
        for col_key, count in col_dict.items():
            col_totals[col_key] += count
            grand_total += count

    if grand_total == 0:
        return 0.0

    # Calculate chi-squared
    chi2 = 0.0
    for row_key, col_dict in contingency.items():
        for col_key, observed in col_dict.items():
            expected = (row_totals[row_key] * col_totals[col_key]) / grand_total
            if expected > 0:
                chi2 += (observed - expected) ** 2 / expected

    n_rows = len(row_totals)
    n_cols = len(col_totals)

    if n_rows <= 1 or n_cols <= 1:
        return 0.0

    return math.sqrt(chi2 / (grand_total * (min(n_rows, n_cols) - 1)))


def shannon_entropy(counts: Dict[str, int]) -> float:
    """Calculate Shannon entropy in bits."""
    total = sum(counts.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    return entropy


def mutual_information(contingency: Dict[str, Dict[str, int]]) -> float:
    """Calculate mutual information between two variables."""
    # Get marginals
    row_totals = {}
    col_totals = defaultdict(int)
    grand_total = 0

    for row_key, col_dict in contingency.items():
        row_totals[row_key] = sum(col_dict.values())
        for col_key, count in col_dict.items():
            col_totals[col_key] += count
            grand_total += count

    if grand_total == 0:
        return 0.0

    mi = 0.0
    for row_key, col_dict in contingency.items():
        for col_key, joint in col_dict.items():
            if joint > 0:
                p_joint = joint / grand_total
                p_row = row_totals[row_key] / grand_total
                p_col = col_totals[col_key] / grand_total
                mi += p_joint * math.log2(p_joint / (p_row * p_col))

    return mi


def jaccard_similarity(set1: Set, set2: Set) -> float:
    """Calculate Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def test_h1_prefix_folio(records: List[Dict], a_types: Set[str]) -> Dict:
    """
    H1: PREFIX × AZC_FOLIO correlation
    Expected: WEAK/NULL
    """
    print("\n" + "="*60)
    print("H1: PREFIX × AZC_FOLIO")
    print("Expected: WEAK/NULL (compatibility is finer than material-class)")
    print("="*60)

    # Filter to A-types in AZC
    a_in_azc = [r for r in records if r['token'] in a_types and r['prefix']]

    # Build contingency table: prefix × folio
    contingency = defaultdict(lambda: defaultdict(int))
    for r in a_in_azc:
        contingency[r['prefix']][r['folio']] += 1

    # Calculate Cramér's V
    v = cramers_v(dict(contingency))

    # Calculate per-prefix folio spread
    prefix_folio_counts = {}
    for prefix, folio_dict in contingency.items():
        n_folios = len(folio_dict)
        n_tokens = sum(folio_dict.values())
        prefix_folio_counts[prefix] = {'n_folios': n_folios, 'n_tokens': n_tokens}

    print(f"\nA-types with prefix in AZC: {len(a_in_azc)} tokens")
    print(f"Unique prefixes: {len(contingency)}")
    print(f"Cramér's V: {v:.4f}")

    # Interpret
    if v < 0.1:
        interpretation = "CONFIRMED: PREFIX has negligible association with AZC folio"
        signal = "NULL"
    elif v < 0.2:
        interpretation = "WEAK: PREFIX has weak association with AZC folio"
        signal = "WEAK"
    elif v < 0.3:
        interpretation = "MODERATE: PREFIX has moderate association - needs investigation"
        signal = "MODERATE"
    else:
        interpretation = "STRONG: PREFIX determines AZC folio - REVISES model"
        signal = "STRONG"

    print(f"\nInterpretation: {interpretation}")

    return {
        'hypothesis': 'PREFIX × AZC_FOLIO',
        'expected': 'WEAK/NULL',
        'n_tokens': len(a_in_azc),
        'n_prefixes': len(contingency),
        'cramers_v': round(v, 4),
        'signal': signal,
        'interpretation': interpretation,
        'prefix_folio_spread': prefix_folio_counts
    }


def test_h2_middle_folio(records: List[Dict], a_types: Set[str]) -> Dict:
    """
    H2: MIDDLE × AZC_FOLIO correlation
    Expected: MODERATE-STRONG
    """
    print("\n" + "="*60)
    print("H2: MIDDLE × AZC_FOLIO")
    print("Expected: MODERATE-STRONG (AZC filters at variant level)")
    print("="*60)

    # Filter to A-types in AZC
    a_in_azc = [r for r in records if r['token'] in a_types and r['middle']]

    # Build contingency table: middle × folio
    contingency = defaultdict(lambda: defaultdict(int))
    for r in a_in_azc:
        contingency[r['middle']][r['folio']] += 1

    # For MIDDLEs, we expect high sparsity - most appear in few folios
    # Calculate distribution of folio counts per MIDDLE
    folio_counts_per_middle = [len(folio_dict) for folio_dict in contingency.values()]

    # What fraction of MIDDLEs appear in only 1-3 folios?
    singleton_middles = sum(1 for c in folio_counts_per_middle if c <= 3)
    pct_restricted = singleton_middles / len(folio_counts_per_middle) * 100

    # Mutual information
    mi = mutual_information(dict(contingency))

    # For reference: entropy of folio distribution
    folio_totals = defaultdict(int)
    for r in a_in_azc:
        folio_totals[r['folio']] += 1
    folio_entropy = shannon_entropy(dict(folio_totals))

    # Normalized MI
    nmi = mi / folio_entropy if folio_entropy > 0 else 0

    print(f"\nA-types with MIDDLE in AZC: {len(a_in_azc)} tokens")
    print(f"Unique MIDDLEs: {len(contingency)}")
    print(f"MIDDLEs in <=3 folios: {singleton_middles} ({pct_restricted:.1f}%)")
    print(f"Mutual Information: {mi:.4f} bits")
    print(f"Normalized MI: {nmi:.4f}")

    # Interpret based on folio restriction
    if pct_restricted > 70:
        interpretation = "STRONG: Most MIDDLEs are folio-restricted - AZC filters at variant level"
        signal = "STRONG"
    elif pct_restricted > 50:
        interpretation = "MODERATE: Many MIDDLEs are folio-restricted"
        signal = "MODERATE"
    else:
        interpretation = "WEAK: MIDDLEs spread across folios - compatibility is token-emergent"
        signal = "WEAK"

    print(f"\nInterpretation: {interpretation}")

    return {
        'hypothesis': 'MIDDLE × AZC_FOLIO',
        'expected': 'MODERATE-STRONG',
        'n_tokens': len(a_in_azc),
        'n_middles': len(contingency),
        'middles_in_1_3_folios': singleton_middles,
        'pct_restricted': round(pct_restricted, 2),
        'mutual_information': round(mi, 4),
        'normalized_mi': round(nmi, 4),
        'signal': signal,
        'interpretation': interpretation
    }


def test_h3_suffix_position(records: List[Dict], a_types: Set[str]) -> Dict:
    """
    H3: SUFFIX × AZC_POSITION correlation
    Expected: UNKNOWN (most important test)
    """
    print("\n" + "="*60)
    print("H3: SUFFIX × AZC_POSITION")
    print("Expected: UNKNOWN (tests if decision archetypes are phase-indexed)")
    print("="*60)

    # Filter to A-types in AZC with suffix
    a_in_azc = [r for r in records if r['token'] in a_types and r['suffix']]

    # Normalize placement to major categories
    def normalize_placement(p):
        if p.startswith('C'):
            return 'C'
        elif p.startswith('P'):
            return 'P'
        elif p.startswith('R'):
            return 'R'
        elif p.startswith('S'):
            return 'S'
        else:
            return p

    # Build contingency table: suffix × position
    contingency = defaultdict(lambda: defaultdict(int))
    for r in a_in_azc:
        pos = normalize_placement(r['placement'])
        contingency[r['suffix']][pos] += 1

    # Calculate Cramér's V
    v = cramers_v(dict(contingency))

    # Calculate per-suffix position profile
    suffix_profiles = {}
    for suffix, pos_dict in contingency.items():
        total = sum(pos_dict.values())
        profile = {pos: count/total*100 for pos, count in pos_dict.items()}
        suffix_profiles[suffix] = {'total': total, 'profile': profile}

    # Check for position-concentrated suffixes
    position_dominant = []
    for suffix, data in suffix_profiles.items():
        if data['total'] >= 20:  # Minimum sample
            for pos, pct in data['profile'].items():
                if pct >= 60:  # 60%+ in one position
                    position_dominant.append((suffix, pos, pct))

    print(f"\nA-types with SUFFIX in AZC: {len(a_in_azc)} tokens")
    print(f"Unique suffixes: {len(contingency)}")
    print(f"Cramér's V: {v:.4f}")
    print(f"Position-dominant suffixes (>=60% in one position): {len(position_dominant)}")

    if position_dominant:
        print("\nPosition-dominant suffixes:")
        for suffix, pos, pct in sorted(position_dominant, key=lambda x: -x[2])[:10]:
            print(f"  -{suffix}: {pos} ({pct:.1f}%)")

    # Interpret
    if v >= 0.2 and len(position_dominant) >= 3:
        interpretation = "STRONG: SUFFIXes show phase-indexing - decision archetypes are position-gated"
        signal = "STRONG"
    elif v >= 0.1 or len(position_dominant) >= 2:
        interpretation = "MODERATE: Some SUFFIX × position structure exists"
        signal = "MODERATE"
    else:
        interpretation = "WEAK: SUFFIXes are position-independent - phase binding is AZC-only"
        signal = "WEAK"

    print(f"\nInterpretation: {interpretation}")

    return {
        'hypothesis': 'SUFFIX × AZC_POSITION',
        'expected': 'UNKNOWN',
        'n_tokens': len(a_in_azc),
        'n_suffixes': len(contingency),
        'cramers_v': round(v, 4),
        'n_position_dominant': len(position_dominant),
        'position_dominant_suffixes': [(s, p, round(pct, 1)) for s, p, pct in position_dominant],
        'signal': signal,
        'interpretation': interpretation,
        'suffix_profiles': {k: {'total': v['total'], 'profile': {pk: round(pv, 1) for pk, pv in v['profile'].items()}}
                          for k, v in suffix_profiles.items() if v['total'] >= 10}
    }


def test_h4_cluster_overlap(records: List[Dict], a_types: Set[str], data_path: Path) -> Dict:
    """
    H4: CLUSTER_STATUS × AZC_OVERLAP
    Expected: MODERATE enrichment for clustered entries

    Requires determining which A entries are clustered vs singleton.
    We approximate by looking at token co-occurrence patterns.
    """
    print("\n" + "="*60)
    print("H4: CLUSTER_STATUS × AZC_OVERLAP")
    print("Expected: MODERATE (clustered entries share more AZC folios)")
    print("="*60)

    # Build A-type to AZC folio mapping
    a_type_folios = defaultdict(set)
    for r in records:
        if r['token'] in a_types:
            a_type_folios[r['token']].add(r['folio'])

    # Filter to A-types that appear in AZC
    a_in_azc = {t: folios for t, folios in a_type_folios.items() if folios}

    if len(a_in_azc) < 10:
        return {
            'hypothesis': 'CLUSTER_STATUS × AZC_OVERLAP',
            'expected': 'MODERATE',
            'status': 'INSUFFICIENT_DATA',
            'n_a_types_in_azc': len(a_in_azc)
        }

    # Calculate pairwise Jaccard similarities
    a_types_list = list(a_in_azc.keys())

    # For computational efficiency, sample if too large
    if len(a_types_list) > 500:
        import random
        random.seed(42)
        a_types_list = random.sample(a_types_list, 500)

    similarities = []
    for i in range(len(a_types_list)):
        for j in range(i+1, len(a_types_list)):
            t1, t2 = a_types_list[i], a_types_list[j]
            sim = jaccard_similarity(a_in_azc[t1], a_in_azc[t2])
            similarities.append(sim)

    mean_jaccard = sum(similarities) / len(similarities) if similarities else 0

    # Count tokens by folio count
    folio_count_dist = Counter(len(folios) for folios in a_in_azc.values())

    # Tokens in 1 folio (most restricted) vs many folios (least restricted)
    restricted = sum(1 for folios in a_in_azc.values() if len(folios) <= 2)
    unrestricted = sum(1 for folios in a_in_azc.values() if len(folios) >= 10)

    print(f"\nA-types appearing in AZC: {len(a_in_azc)}")
    print(f"Mean pairwise Jaccard (folio overlap): {mean_jaccard:.4f}")
    print(f"Restricted (<=2 folios): {restricted} ({restricted/len(a_in_azc)*100:.1f}%)")
    print(f"Unrestricted (>=10 folios): {unrestricted} ({unrestricted/len(a_in_azc)*100:.1f}%)")

    # Without actual cluster labels, we can test if morphologically similar tokens
    # (same prefix or same suffix) share more AZC folios

    # Group by prefix
    by_prefix = defaultdict(list)
    for t in a_types_list:
        decomp = decompose_token(t)
        if decomp['prefix']:
            by_prefix[decomp['prefix']].append(t)

    # Calculate within-prefix vs between-prefix Jaccard
    within_prefix_sims = []
    for prefix, tokens in by_prefix.items():
        if len(tokens) >= 2:
            for i in range(len(tokens)):
                for j in range(i+1, len(tokens)):
                    sim = jaccard_similarity(a_in_azc[tokens[i]], a_in_azc[tokens[j]])
                    within_prefix_sims.append(sim)

    mean_within = sum(within_prefix_sims) / len(within_prefix_sims) if within_prefix_sims else 0

    print(f"\nWithin-prefix mean Jaccard: {mean_within:.4f}")
    print(f"Overall mean Jaccard: {mean_jaccard:.4f}")
    print(f"Enrichment ratio: {mean_within/mean_jaccard:.2f}x" if mean_jaccard > 0 else "N/A")

    enrichment = mean_within / mean_jaccard if mean_jaccard > 0 else 0

    if enrichment >= 1.5:
        interpretation = "STRONG: Same-prefix tokens share AZC folios more than random"
        signal = "STRONG"
    elif enrichment >= 1.2:
        interpretation = "MODERATE: Weak prefix-based AZC clustering"
        signal = "MODERATE"
    else:
        interpretation = "WEAK: No prefix-based AZC clustering - compatibility is token-level"
        signal = "WEAK"

    print(f"\nInterpretation: {interpretation}")

    return {
        'hypothesis': 'CLUSTER_STATUS × AZC_OVERLAP',
        'expected': 'MODERATE',
        'n_a_types_in_azc': len(a_in_azc),
        'mean_pairwise_jaccard': round(mean_jaccard, 4),
        'within_prefix_jaccard': round(mean_within, 4),
        'enrichment_ratio': round(enrichment, 2),
        'pct_restricted': round(restricted/len(a_in_azc)*100, 1),
        'pct_unrestricted': round(unrestricted/len(a_in_azc)*100, 1),
        'folio_count_distribution': dict(folio_count_dist.most_common(10)),
        'signal': signal,
        'interpretation': interpretation
    }


def synthesize_results(h1: Dict, h2: Dict, h3: Dict, h4: Dict) -> Dict:
    """Synthesize all results into actionable interpretation."""

    print("\n" + "="*60)
    print("SYNTHESIS: WHERE DOES THE SIGNAL LIVE?")
    print("="*60)

    signals = {
        'PREFIX -> FOLIO': h1['signal'],
        'MIDDLE -> FOLIO': h2['signal'],
        'SUFFIX -> POSITION': h3['signal'],
        'CLUSTER -> OVERLAP': h4.get('signal', 'UNKNOWN')
    }

    print("\nSignal Summary:")
    for test, signal in signals.items():
        marker = {'STRONG': '[***]', 'MODERATE': '[** ]', 'WEAK': '[*  ]', 'NULL': '[   ]', 'UNKNOWN': '[???]'}
        print(f"  {test}: {marker.get(signal, '[???]')} {signal}")

    # Determine compatibility granularity
    if signals['PREFIX -> FOLIO'] in ['STRONG', 'MODERATE']:
        granularity = 'COARSE (material-class level)'
    elif signals['MIDDLE -> FOLIO'] in ['STRONG', 'MODERATE']:
        granularity = 'FINE (variant level)'
    else:
        granularity = 'EMERGENT (full-token only)'

    # Determine phase-indexing
    if signals['SUFFIX -> POSITION'] in ['STRONG', 'MODERATE']:
        phase_indexing = 'YES - decision archetypes are phase-gated'
    else:
        phase_indexing = 'NO - phase binding is AZC-only'

    # Determine clustering significance
    if signals['CLUSTER -> OVERLAP'] in ['STRONG', 'MODERATE']:
        clustering = 'MEANINGFUL - A clustering reflects compatibility'
    else:
        clustering = 'ERGONOMIC - A clustering is organizational only'

    synthesis = {
        'compatibility_granularity': granularity,
        'phase_indexing': phase_indexing,
        'clustering_significance': clustering,
        'signals': signals
    }

    print(f"\nCompatibility Granularity: {granularity}")
    print(f"Phase-Indexing: {phase_indexing}")
    print(f"Clustering Significance: {clustering}")

    # Recommendations for next steps
    recommendations = []
    if signals['MIDDLE -> FOLIO'] == 'STRONG':
        recommendations.append("Proceed with MIDDLE-level compatibility mapping")
    if signals['SUFFIX -> POSITION'] == 'STRONG':
        recommendations.append("Map SUFFIX archetypes to workflow phases")
    if signals['PREFIX -> FOLIO'] == 'WEAK' and signals['MIDDLE -> FOLIO'] == 'WEAK':
        recommendations.append("Compatibility may be full-token emergent - test full token x folio")

    synthesis['recommendations'] = recommendations

    print("\nRecommendations:")
    for r in recommendations:
        print(f"  -> {r}")

    return synthesis


def main():
    data_path = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    print("F-AZC-014: A Morphology × AZC Structure Cross-Tabulation")
    print("="*60)
    print("\nLoading data...")

    records, a_types = load_data(data_path)

    print(f"  Total AZC records: {len(records)}")
    print(f"  A vocabulary types: {len(a_types)}")

    # Run all four tests
    h1_result = test_h1_prefix_folio(records, a_types)
    h2_result = test_h2_middle_folio(records, a_types)
    h3_result = test_h3_suffix_position(records, a_types)
    h4_result = test_h4_cluster_overlap(records, a_types, data_path)

    # Synthesize
    synthesis = synthesize_results(h1_result, h2_result, h3_result, h4_result)

    # Build output
    output = {
        'fit_id': 'F-AZC-014',
        'title': 'A Morphology × AZC Structure Cross-Tabulation',
        'purpose': 'Determine where compatibility signal lives before A-through-AZC projection',
        'tests': {
            'H1_prefix_folio': h1_result,
            'H2_middle_folio': h2_result,
            'H3_suffix_position': h3_result,
            'H4_cluster_overlap': h4_result
        },
        'synthesis': synthesis
    }

    # Save
    results_path = Path(__file__).parent.parent.parent / 'results' / 'azc_a_morphology_crosstab.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)

    print(f"\n\nResults saved to {results_path}")


if __name__ == '__main__':
    main()
