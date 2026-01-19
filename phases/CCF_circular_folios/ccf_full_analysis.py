# CCF Full Analysis - Circular Control Folio Structural Analysis
# Pre-registered falsification tests for circular folios
# NO semantic interpretation - purely operational analysis

import json
import re
import random
import math
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime
from scipy import stats

print("=" * 70)
print("CIRCULAR CONTROL FOLIO (CCF) ANALYSIS")
print("Pre-registered structural test suite")
print("Generated:", datetime.now().isoformat())
print("=" * 70)

# =============================================================================
# DATA LOADING
# =============================================================================

def load_corpus():
    """Load corpus and identify circular folios."""
    records = []
    with open('C:/git/voynich/data/transcriptions/interlinear_full_words.txt', 'r', encoding='latin-1') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 12:
                # CRITICAL: Filter to H-only transcriber track
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                parts = [p.strip('"') for p in parts]
                records.append({
                    'word': parts[0],
                    'folio': parts[2],
                    'section': parts[3],
                    'language': parts[6] if len(parts) > 6 else 'U',
                    'line': parts[11] if len(parts) > 11 else '0',
                    'placement': parts[10] if len(parts) > 10 else 'P1'
                })
    return records

def identify_circular_folios(records):
    """Identify circular folios from the corpus."""
    circular_pattern = re.compile(r'^f(67|68|69|70|71|72|73)')
    circular_folios = defaultdict(list)
    all_folios = defaultdict(list)

    for r in records:
        folio = r['folio']
        all_folios[folio].append(r)
        if circular_pattern.match(folio):
            circular_folios[folio].append(r)

    return circular_folios, all_folios

def load_frozen_grammar():
    """Load the 49 frozen instruction classes."""
    try:
        with open('C:/git/voynich/phase20a_operator_equivalence.json', 'r') as f:
            return json.load(f)
    except:
        return None

def load_transition_grammar():
    """Load canonical grammar with forbidden transitions."""
    try:
        with open('C:/git/voynich/phase20d_canonical_grammar.json', 'r') as f:
            return json.load(f)
    except:
        return None

def load_kernel_data():
    """Load kernel node data (k, h, e)."""
    try:
        with open('C:/git/voynich/phase17e_role_synthesis.json', 'r') as f:
            return json.load(f)
    except:
        return {'kernel_nodes': ['k', 'h', 'e']}

def load_hazard_data():
    """Load forbidden transitions / hazard data."""
    try:
        with open('C:/git/voynich/phase18a_forbidden_inventory.json', 'r') as f:
            return json.load(f)
    except:
        return None

# =============================================================================
# SECTOR SEGMENTATION
# =============================================================================

def segment_into_sectors(folio_records):
    """
    Segment circular folio records into sectors.
    Uses line numbers and placement to infer sector boundaries.
    """
    # Group by line number first
    by_line = defaultdict(list)
    for r in folio_records:
        try:
            line_num = int(r['line'])
        except:
            line_num = 0
        by_line[line_num].append(r)

    # Treat each line as a potential sector
    sectors = []
    for line_num in sorted(by_line.keys()):
        tokens = [r['word'] for r in by_line[line_num]]
        if tokens:  # Only include non-empty sectors
            sectors.append({
                'sector_id': line_num,
                'tokens': tokens,
                'records': by_line[line_num]
            })

    return sectors

# =============================================================================
# TOKEN -> INSTRUCTION CLASS MAPPING
# =============================================================================

def get_token_class(token, equiv_classes):
    """Map token to its instruction class."""
    if equiv_classes is None:
        return 'UNKNOWN'

    # Search equivalence classes
    classes = equiv_classes.get('equivalence_classes', {})
    for class_id, members in classes.items():
        if token in members:
            return class_id

    # Check if token starts with known class prefixes
    for class_id, members in classes.items():
        for member in members:
            if token.startswith(member) or member.startswith(token):
                return class_id

    return 'UNCLASSIFIED'

# =============================================================================
# DEPENDENCY GRAPH CONSTRUCTION
# =============================================================================

def build_adjacency_graph(sectors):
    """Build token adjacency graph within and across sectors."""
    edges = defaultdict(int)
    within_sector = defaultdict(int)
    cross_sector = defaultdict(int)

    for sector in sectors:
        tokens = sector['tokens']
        sector_id = sector['sector_id']

        # Within-sector edges (sequential)
        for i in range(len(tokens) - 1):
            edge = (tokens[i], tokens[i+1])
            edges[edge] += 1
            within_sector[edge] += 1

    # Cross-sector edges (last token of sector N to first token of sector N+1)
    for i in range(len(sectors) - 1):
        if sectors[i]['tokens'] and sectors[i+1]['tokens']:
            edge = (sectors[i]['tokens'][-1], sectors[i+1]['tokens'][0])
            edges[edge] += 1
            cross_sector[edge] += 1

    return edges, within_sector, cross_sector

# =============================================================================
# TEST 1: LOCALITY VIOLATION TEST
# =============================================================================

def test_locality_violation(circular_folios, n_permutations=1000):
    """
    Test for non-local dependencies across sectors.
    Null model: randomly permute sector labels while preserving structure.
    """
    print("\n" + "=" * 70)
    print("TEST 1: LOCALITY VIOLATION TEST")
    print("=" * 70)

    results = {
        'observed_cross_sector_density': [],
        'null_distribution': [],
        'p_values': [],
        'per_folio': {}
    }

    for folio, records in sorted(circular_folios.items()):
        sectors = segment_into_sectors(records)
        if len(sectors) < 2:
            continue

        # Build observed graphs
        edges, within, cross = build_adjacency_graph(sectors)

        # Calculate cross-sector density
        total_edges = sum(edges.values())
        cross_edges = sum(cross.values())
        observed_density = cross_edges / max(total_edges, 1)

        results['observed_cross_sector_density'].append(observed_density)

        # Generate null distribution
        null_densities = []
        for _ in range(n_permutations):
            # Permute tokens within each sector
            permuted_sectors = []
            for s in sectors:
                tokens_copy = s['tokens'][:]
                random.shuffle(tokens_copy)
                permuted_sectors.append({
                    'sector_id': s['sector_id'],
                    'tokens': tokens_copy,
                    'records': s['records']
                })

            _, _, null_cross = build_adjacency_graph(permuted_sectors)
            null_cross_edges = sum(null_cross.values())
            null_density = null_cross_edges / max(total_edges, 1)
            null_densities.append(null_density)

        results['null_distribution'].extend(null_densities)

        # Calculate p-value
        p_value = sum(1 for nd in null_densities if nd >= observed_density) / len(null_densities)
        results['p_values'].append(p_value)

        results['per_folio'][folio] = {
            'n_sectors': len(sectors),
            'total_edges': total_edges,
            'cross_sector_edges': cross_edges,
            'observed_density': observed_density,
            'null_mean': np.mean(null_densities),
            'null_std': np.std(null_densities),
            'p_value': p_value
        }

        print(f"  {folio}: {len(sectors)} sectors, cross-density={observed_density:.4f}, p={p_value:.4f}")

    # Aggregate results
    mean_observed = np.mean(results['observed_cross_sector_density'])
    mean_null = np.mean(results['null_distribution'])

    # Statistical test
    significant_count = sum(1 for p in results['p_values'] if p < 0.05)

    results['summary'] = {
        'mean_observed_density': mean_observed,
        'mean_null_density': mean_null,
        'density_ratio': mean_observed / max(mean_null, 0.0001),
        'significant_folios': significant_count,
        'total_folios': len(results['p_values']),
        'VERDICT': 'PASS' if significant_count < len(results['p_values']) * 0.1 else 'FAIL'
    }

    print(f"\n  Summary:")
    print(f"    Mean observed cross-sector density: {mean_observed:.4f}")
    print(f"    Mean null density: {mean_null:.4f}")
    print(f"    Significant deviations (p<0.05): {significant_count}/{len(results['p_values'])}")
    print(f"    VERDICT: {results['summary']['VERDICT']}")

    return results

# =============================================================================
# TEST 2: CLASS NOVELTY TEST
# =============================================================================

def test_class_novelty(circular_folios, all_folios, equiv_classes):
    """
    Test whether circular folio tokens form new instruction classes
    or are variants of existing classes.
    """
    print("\n" + "=" * 70)
    print("TEST 2: CLASS NOVELTY TEST")
    print("=" * 70)

    if equiv_classes is None:
        print("  ERROR: Cannot run test - no equivalence classes loaded")
        return {'VERDICT': 'INCONCLUSIVE', 'error': 'No equivalence data'}

    # Collect all tokens from circular vs non-circular folios
    ccf_tokens = Counter()
    non_ccf_tokens = Counter()

    circular_folio_set = set(circular_folios.keys())

    for folio, records in all_folios.items():
        token_counter = ccf_tokens if folio in circular_folio_set else non_ccf_tokens
        for r in records:
            token_counter[r['word']] += 1

    # Find tokens unique to circular folios
    ccf_unique = set(ccf_tokens.keys()) - set(non_ccf_tokens.keys())

    # Map all CCF tokens to classes
    class_mapping = {}
    unclassified = []

    for token in ccf_tokens:
        cls = get_token_class(token, equiv_classes)
        class_mapping[token] = cls
        if cls == 'UNCLASSIFIED':
            unclassified.append(token)

    # Analyze class distribution
    ccf_classes = Counter(class_mapping.values())

    # Behavioral distance: check if unclassified tokens cluster together
    # (would indicate a new class)
    unclassified_freq = sum(ccf_tokens[t] for t in unclassified)
    total_freq = sum(ccf_tokens.values())
    unclassified_rate = unclassified_freq / max(total_freq, 1)

    results = {
        'total_ccf_tokens': len(ccf_tokens),
        'unique_to_ccf': len(ccf_unique),
        'unclassified_count': len(unclassified),
        'unclassified_rate': unclassified_rate,
        'class_distribution': dict(ccf_classes),
        'sample_unclassified': list(unclassified)[:20],
        'per_token_classes': class_mapping
    }

    # VERDICT: If unclassified rate < 10%, tokens map to existing classes
    # KILL condition: stable, behaviorally distinct cluster
    if unclassified_rate < 0.10:
        results['VERDICT'] = 'PASS'
        results['interpretation'] = 'CCF tokens map to existing instruction classes'
    elif unclassified_rate < 0.25:
        results['VERDICT'] = 'INCONCLUSIVE'
        results['interpretation'] = 'Moderate unclassified rate - requires further analysis'
    else:
        results['VERDICT'] = 'FAIL'
        results['interpretation'] = 'High unclassified rate may indicate novel classes'

    print(f"  Total CCF tokens: {len(ccf_tokens)}")
    print(f"  Unique to CCF: {len(ccf_unique)}")
    print(f"  Unclassified: {len(unclassified)} ({unclassified_rate:.1%})")
    print(f"  Classes found: {len(ccf_classes)}")
    print(f"  VERDICT: {results['VERDICT']}")

    return results

# =============================================================================
# TEST 3: CIRCULAR EXECUTABILITY TEST
# =============================================================================

def test_circular_executability(circular_folios, grammar, n_trials=100):
    """
    Test whether circular order is executably required.
    Compare: original order vs rotations vs random reordering.
    """
    print("\n" + "=" * 70)
    print("TEST 3: CIRCULAR EXECUTABILITY TEST")
    print("=" * 70)

    if grammar is None:
        print("  ERROR: Cannot run test - no grammar loaded")
        return {'VERDICT': 'INCONCLUSIVE', 'error': 'No grammar data'}

    # Get forbidden transitions
    forbidden = set()
    if 'forbidden_transitions' in grammar:
        for trans in grammar['forbidden_transitions']:
            if isinstance(trans, list) and len(trans) >= 2:
                forbidden.add((trans[0], trans[1]))
            elif isinstance(trans, dict):
                forbidden.add((trans.get('from', ''), trans.get('to', '')))

    def compute_legality(sequence, forbidden_set):
        """Count legal transitions in sequence."""
        if len(sequence) < 2:
            return 1.0
        legal = 0
        total = 0
        for i in range(len(sequence) - 1):
            total += 1
            if (sequence[i], sequence[i+1]) not in forbidden_set:
                legal += 1
        return legal / max(total, 1)

    results = {
        'per_folio': {},
        'original_legality': [],
        'rotation_legality': [],
        'random_legality': []
    }

    for folio, records in sorted(circular_folios.items()):
        sectors = segment_into_sectors(records)
        if len(sectors) < 3:
            continue

        # Original circular order
        original_seq = []
        for s in sectors:
            original_seq.extend(s['tokens'])

        original_legality = compute_legality(original_seq, forbidden)
        results['original_legality'].append(original_legality)

        # Rotation tests
        rotation_legalities = []
        for rotation in range(1, len(sectors)):
            rotated_sectors = sectors[rotation:] + sectors[:rotation]
            rotated_seq = []
            for s in rotated_sectors:
                rotated_seq.extend(s['tokens'])
            rotation_legalities.append(compute_legality(rotated_seq, forbidden))

        mean_rotation = np.mean(rotation_legalities) if rotation_legalities else original_legality
        results['rotation_legality'].append(mean_rotation)

        # Random reordering tests
        random_legalities = []
        for _ in range(n_trials):
            random_sectors = sectors[:]
            random.shuffle(random_sectors)
            random_seq = []
            for s in random_sectors:
                random_seq.extend(s['tokens'])
            random_legalities.append(compute_legality(random_seq, forbidden))

        mean_random = np.mean(random_legalities)
        results['random_legality'].append(mean_random)

        results['per_folio'][folio] = {
            'n_sectors': len(sectors),
            'original': original_legality,
            'rotation_mean': mean_rotation,
            'random_mean': mean_random,
            'rotation_robust': abs(original_legality - mean_rotation) < 0.05,
            'random_robust': abs(original_legality - mean_random) < 0.05
        }

        print(f"  {folio}: original={original_legality:.3f}, rotation={mean_rotation:.3f}, random={mean_random:.3f}")

    # Summary
    mean_original = np.mean(results['original_legality'])
    mean_rotation = np.mean(results['rotation_legality'])
    mean_random = np.mean(results['random_legality'])

    rotation_robust = abs(mean_original - mean_rotation) < 0.05
    random_robust = abs(mean_original - mean_random) < 0.05

    if rotation_robust and not random_robust:
        verdict = 'CYCLIC_CONTROL'
        interpretation = 'Rotation-robust but adjacency-dependent -> cyclic control layout'
    elif rotation_robust and random_robust:
        verdict = 'VISUAL_BUNDLING'
        interpretation = 'Fully reorder-robust -> visual bundling of independent runs'
    else:
        verdict = 'INCONCLUSIVE'
        interpretation = 'Order dependency pattern unclear'

    results['summary'] = {
        'mean_original': mean_original,
        'mean_rotation': mean_rotation,
        'mean_random': mean_random,
        'rotation_robust': rotation_robust,
        'random_robust': random_robust,
        'VERDICT': verdict,
        'interpretation': interpretation
    }

    print(f"\n  Summary:")
    print(f"    Mean original legality: {mean_original:.4f}")
    print(f"    Mean rotation legality: {mean_rotation:.4f}")
    print(f"    Mean random legality: {mean_random:.4f}")
    print(f"    VERDICT: {verdict}")
    print(f"    Interpretation: {interpretation}")

    return results

# =============================================================================
# TEST 4: BOUNDARY CLUSTERING TEST
# =============================================================================

def test_boundary_clustering(circular_folios, hazard_data, kernel_nodes):
    """
    Test whether labels cluster near hazard boundaries.
    """
    print("\n" + "=" * 70)
    print("TEST 4: BOUNDARY CLUSTERING TEST")
    print("=" * 70)

    # Define hazard-adjacent tokens
    hazard_adjacent = set()
    if hazard_data and 'forbidden_transitions' in hazard_data:
        for trans in hazard_data['forbidden_transitions']:
            if isinstance(trans, dict):
                hazard_adjacent.add(trans.get('from', ''))
                hazard_adjacent.add(trans.get('to', ''))
            elif isinstance(trans, list) and len(trans) >= 2:
                hazard_adjacent.add(trans[0])
                hazard_adjacent.add(trans[1])

    # Use kernel nodes as boundary markers
    boundary_tokens = set(kernel_nodes) | hazard_adjacent

    results = {
        'per_folio': {},
        'observed_density': [],
        'null_density': []
    }

    for folio, records in sorted(circular_folios.items()):
        tokens = [r['word'] for r in records]
        if not tokens:
            continue

        # Count boundary-adjacent tokens
        boundary_count = sum(1 for t in tokens if any(t.startswith(b) or b in t for b in boundary_tokens))
        observed_density = boundary_count / len(tokens)

        results['observed_density'].append(observed_density)

        # Null model: matched-count random placement
        # Use all folio vocabulary as baseline
        all_tokens = list(set(tokens))
        null_densities = []
        for _ in range(1000):
            random_sample = random.choices(all_tokens, k=len(tokens))
            null_count = sum(1 for t in random_sample if any(t.startswith(b) or b in t for b in boundary_tokens))
            null_densities.append(null_count / len(random_sample))

        null_mean = np.mean(null_densities)
        null_std = np.std(null_densities)
        z_score = (observed_density - null_mean) / max(null_std, 0.0001)

        results['null_density'].extend(null_densities)

        results['per_folio'][folio] = {
            'n_tokens': len(tokens),
            'boundary_count': boundary_count,
            'observed_density': observed_density,
            'null_mean': null_mean,
            'null_std': null_std,
            'z_score': z_score
        }

        print(f"  {folio}: density={observed_density:.3f}, null={null_mean:.3f}, z={z_score:.2f}")

    # Summary
    mean_observed = np.mean(results['observed_density'])
    mean_null = np.mean(results['null_density'])

    # Calculate overall z-score
    pooled_z = (mean_observed - mean_null) / max(np.std(results['null_density']), 0.0001)

    if pooled_z > 2.0:
        verdict = 'BOUNDARY_CLUSTERED'
        interpretation = 'Labels disproportionately occur near hazard/kernel boundaries'
    elif pooled_z < -2.0:
        verdict = 'BOUNDARY_AVOIDED'
        interpretation = 'Labels avoid hazard/kernel boundaries'
    else:
        verdict = 'NO_CLUSTERING'
        interpretation = 'No significant clustering pattern detected'

    results['summary'] = {
        'mean_observed_density': mean_observed,
        'mean_null_density': mean_null,
        'pooled_z_score': pooled_z,
        'boundary_tokens_used': list(boundary_tokens)[:20],
        'VERDICT': verdict,
        'interpretation': interpretation
    }

    print(f"\n  Summary:")
    print(f"    Mean observed boundary density: {mean_observed:.4f}")
    print(f"    Mean null density: {mean_null:.4f}")
    print(f"    Pooled Z-score: {pooled_z:.2f}")
    print(f"    VERDICT: {verdict}")

    return results

# =============================================================================
# MAIN EXECUTION
# =============================================================================

print("\n[1] Loading data...")
records = load_corpus()
print(f"    Loaded {len(records)} records")

circular_folios, all_folios = identify_circular_folios(records)
print(f"    Found {len(circular_folios)} circular folios with {sum(len(v) for v in circular_folios.values())} records")

equiv_classes = load_frozen_grammar()
grammar = load_transition_grammar()
hazard_data = load_hazard_data()
kernel_data = load_kernel_data()
kernel_nodes = kernel_data.get('kernel_nodes', ['k', 'h', 'e'])

print(f"    Kernel nodes: {kernel_nodes}")

# Run all tests
test1_results = test_locality_violation(circular_folios)
test2_results = test_class_novelty(circular_folios, all_folios, equiv_classes)
test3_results = test_circular_executability(circular_folios, grammar)
test4_results = test_boundary_clustering(circular_folios, hazard_data, kernel_nodes)

# =============================================================================
# FINAL VERDICT
# =============================================================================

print("\n" + "=" * 70)
print("FINAL VERDICT")
print("=" * 70)

verdicts = {
    'Test 1 (Locality)': test1_results.get('summary', {}).get('VERDICT', 'UNKNOWN'),
    'Test 2 (Class Novelty)': test2_results.get('VERDICT', 'UNKNOWN'),
    'Test 3 (Circular Exec)': test3_results.get('summary', {}).get('VERDICT', 'UNKNOWN'),
    'Test 4 (Boundary)': test4_results.get('summary', {}).get('VERDICT', 'UNKNOWN')
}

for test, verdict in verdicts.items():
    print(f"  {test}: {verdict}")

# Aggregate metrics
all_results = {
    'metadata': {
        'timestamp': datetime.now().isoformat(),
        'n_circular_folios': len(circular_folios),
        'n_records': sum(len(v) for v in circular_folios.values())
    },
    'test1_locality': test1_results,
    'test2_class_novelty': test2_results,
    'test3_circular_exec': test3_results,
    'test4_boundary': test4_results,
    'verdicts': verdicts
}

# Save results
with open('C:/git/voynich/ccf_metrics.json', 'w') as f:
    # Convert numpy types for JSON serialization
    def convert(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(i) for i in obj]
        return obj
    json.dump(convert(all_results), f, indent=2)

print("\n  Results saved to ccf_metrics.json")

# Generate report
report = f"""# Circular Control Folio (CCF) Analysis Report

*Generated: {datetime.now().isoformat()}*

---

## Summary

| Test | Verdict |
|------|---------|
| Test 1: Locality Violation | {verdicts['Test 1 (Locality)']} |
| Test 2: Class Novelty | {verdicts['Test 2 (Class Novelty)']} |
| Test 3: Circular Executability | {verdicts['Test 3 (Circular Exec)']} |
| Test 4: Boundary Clustering | {verdicts['Test 4 (Boundary)']} |

---

## Test 1: Locality Violation Test

**Question:** Do label tokens on a given sector exert non-local influence?

**Method:** Compare cross-sector dependency density against null model (permuted sectors).

**Results:**
- Mean observed cross-sector density: {test1_results.get('summary', {}).get('mean_observed_density', 'N/A'):.4f}
- Mean null density: {test1_results.get('summary', {}).get('mean_null_density', 'N/A'):.4f}
- Significant deviations (p<0.05): {test1_results.get('summary', {}).get('significant_folios', 'N/A')}/{test1_results.get('summary', {}).get('total_folios', 'N/A')}

**VERDICT:** {verdicts['Test 1 (Locality)']}

---

## Test 2: Class Novelty Test

**Question:** Do any label tokens form new instruction classes?

**Method:** Map all CCF tokens to frozen 49 classes, measure unclassified rate.

**Results:**
- Total CCF tokens: {test2_results.get('total_ccf_tokens', 'N/A')}
- Unique to CCF: {test2_results.get('unique_to_ccf', 'N/A')}
- Unclassified rate: {test2_results.get('unclassified_rate', 0):.1%}

**VERDICT:** {verdicts['Test 2 (Class Novelty)']}

---

## Test 3: Circular Executability Test

**Question:** Is the circular order executably required?

**Method:** Compare transition legality under original order, rotations, and random reordering.

**Results:**
- Mean original legality: {test3_results.get('summary', {}).get('mean_original', 'N/A'):.4f}
- Mean rotation legality: {test3_results.get('summary', {}).get('mean_rotation', 'N/A'):.4f}
- Mean random legality: {test3_results.get('summary', {}).get('mean_random', 'N/A'):.4f}

**Interpretation:** {test3_results.get('summary', {}).get('interpretation', 'N/A')}

**VERDICT:** {verdicts['Test 3 (Circular Exec)']}

---

## Test 4: Boundary Clustering Test

**Question:** Do labels disproportionately occur near hazard boundaries?

**Method:** Measure label density as function of hazard/kernel proximity, compare to null model.

**Results:**
- Mean observed boundary density: {test4_results.get('summary', {}).get('mean_observed_density', 'N/A'):.4f}
- Mean null density: {test4_results.get('summary', {}).get('mean_null_density', 'N/A'):.4f}
- Pooled Z-score: {test4_results.get('summary', {}).get('pooled_z_score', 'N/A'):.2f}

**VERDICT:** {verdicts['Test 4 (Boundary)']}

---

## Overall Interpretation

Based on the pre-registered tests:

1. **Locality:** {'Sectors operate primarily with local dependencies.' if verdicts['Test 1 (Locality)'] == 'PASS' else 'Non-local dependencies detected across sectors.'}

2. **Class Novelty:** {'CCF tokens map to existing instruction classes.' if verdicts['Test 2 (Class Novelty)'] == 'PASS' else 'Novel instruction classes may exist.'}

3. **Circular Order:** {test3_results.get('summary', {}).get('interpretation', 'Order dependency unclear.')}

4. **Boundary Function:** {test4_results.get('summary', {}).get('interpretation', 'Clustering pattern unclear.')}

---

## Interpretive Firewall Statement

> All findings describe operational roles, structural functions, and execution constraints.
> No semantic interpretation (astronomy, months, symbols) has been applied.
> Domain nouns have been strictly avoided per pre-registration.

---

*Report generated by CCF Analysis Suite v1.0*
"""

with open('C:/git/voynich/ccf_analysis_report.md', 'w') as f:
    f.write(report)

print("  Report saved to ccf_analysis_report.md")
print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
