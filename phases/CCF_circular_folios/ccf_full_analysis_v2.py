# CCF Full Analysis v2 - Circular Control Folio Structural Analysis
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
print("CIRCULAR CONTROL FOLIO (CCF) ANALYSIS v2")
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
            data = json.load(f)
        # Build member-to-class mapping
        member_to_class = {}
        class_info = {}
        for cls in data.get('classes', []):
            class_id = cls['class_id']
            class_info[class_id] = cls
            for member in cls.get('members', []):
                if member:  # Skip empty strings
                    member_to_class[member] = class_id
        return {'member_to_class': member_to_class, 'class_info': class_info}
    except Exception as e:
        print(f"  Warning: Could not load grammar: {e}")
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
    """Segment circular folio records into sectors using line numbers."""
    by_line = defaultdict(list)
    for r in folio_records:
        try:
            line_num = int(r['line'])
        except:
            line_num = 0
        by_line[line_num].append(r)

    sectors = []
    for line_num in sorted(by_line.keys()):
        tokens = [r['word'] for r in by_line[line_num]]
        if tokens:
            sectors.append({
                'sector_id': line_num,
                'tokens': tokens,
                'records': by_line[line_num]
            })
    return sectors

# =============================================================================
# TOKEN -> INSTRUCTION CLASS MAPPING
# =============================================================================

def get_token_class(token, equiv_data):
    """Map token to its instruction class."""
    if equiv_data is None:
        return None

    member_to_class = equiv_data.get('member_to_class', {})

    # Direct lookup
    if token in member_to_class:
        return member_to_class[token]

    # Try prefix matching (token might have affix not in classes)
    for member in member_to_class:
        if len(member) >= 3:
            if token.startswith(member) or member.startswith(token):
                return member_to_class[member]

    return None

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
        for i in range(len(tokens) - 1):
            edge = (tokens[i], tokens[i+1])
            edges[edge] += 1
            within_sector[edge] += 1

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
    """Test for non-local dependencies across sectors."""
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

        edges, within, cross = build_adjacency_graph(sectors)
        total_edges = sum(edges.values())
        cross_edges = sum(cross.values())
        observed_density = cross_edges / max(total_edges, 1)
        results['observed_cross_sector_density'].append(observed_density)

        null_densities = []
        for _ in range(n_permutations):
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
        p_value = sum(1 for nd in null_densities if nd >= observed_density) / len(null_densities)
        results['p_values'].append(p_value)

        results['per_folio'][folio] = {
            'n_sectors': len(sectors),
            'total_edges': int(total_edges),
            'cross_sector_edges': int(cross_edges),
            'observed_density': float(observed_density),
            'null_mean': float(np.mean(null_densities)),
            'null_std': float(np.std(null_densities)),
            'p_value': float(p_value)
        }

        print(f"  {folio}: {len(sectors)} sectors, cross-density={observed_density:.4f}, p={p_value:.4f}")

    mean_observed = float(np.mean(results['observed_cross_sector_density']))
    mean_null = float(np.mean(results['null_distribution']))
    significant_count = sum(1 for p in results['p_values'] if p < 0.05)

    results['summary'] = {
        'mean_observed_density': mean_observed,
        'mean_null_density': mean_null,
        'density_ratio': float(mean_observed / max(mean_null, 0.0001)),
        'significant_folios': int(significant_count),
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

def test_class_novelty(circular_folios, all_folios, equiv_data):
    """Test whether CCF tokens map to existing instruction classes."""
    print("\n" + "=" * 70)
    print("TEST 2: CLASS NOVELTY TEST")
    print("=" * 70)

    if equiv_data is None:
        print("  ERROR: Cannot run test - no equivalence classes loaded")
        return {'VERDICT': 'INCONCLUSIVE', 'error': 'No equivalence data'}

    circular_folio_set = set(circular_folios.keys())

    ccf_tokens = Counter()
    non_ccf_tokens = Counter()

    for folio, records in all_folios.items():
        target = ccf_tokens if folio in circular_folio_set else non_ccf_tokens
        for r in records:
            target[r['word']] += 1

    # Map tokens to classes
    classified = 0
    unclassified = 0
    class_distribution = Counter()
    unclassified_tokens = []

    for token, count in ccf_tokens.items():
        cls = get_token_class(token, equiv_data)
        if cls is not None:
            classified += count
            class_distribution[cls] += count
        else:
            unclassified += count
            unclassified_tokens.append(token)

    total = classified + unclassified
    classified_rate = classified / max(total, 1)
    unclassified_rate = unclassified / max(total, 1)

    results = {
        'total_ccf_token_types': len(ccf_tokens),
        'total_ccf_occurrences': int(total),
        'classified_occurrences': int(classified),
        'unclassified_occurrences': int(unclassified),
        'classified_rate': float(classified_rate),
        'unclassified_rate': float(unclassified_rate),
        'n_classes_used': len(class_distribution),
        'top_classes': dict(class_distribution.most_common(10)),
        'sample_unclassified': unclassified_tokens[:30]
    }

    # Verdict based on classification rate
    if classified_rate >= 0.7:
        results['VERDICT'] = 'PASS'
        results['interpretation'] = 'Majority of CCF tokens map to existing instruction classes'
    elif classified_rate >= 0.5:
        results['VERDICT'] = 'INCONCLUSIVE'
        results['interpretation'] = 'Mixed classification - tokens partially map to existing classes'
    else:
        results['VERDICT'] = 'FAIL'
        results['interpretation'] = 'Majority of CCF tokens do not map to existing classes'

    print(f"  Total CCF token types: {len(ccf_tokens)}")
    print(f"  Total CCF occurrences: {total}")
    print(f"  Classified: {classified} ({classified_rate:.1%})")
    print(f"  Unclassified: {unclassified} ({unclassified_rate:.1%})")
    print(f"  Classes used: {len(class_distribution)}")
    print(f"  VERDICT: {results['VERDICT']}")

    return results

# =============================================================================
# TEST 3: CIRCULAR EXECUTABILITY TEST
# =============================================================================

def test_circular_executability(circular_folios, grammar, n_trials=100):
    """Test whether circular order is executably required."""
    print("\n" + "=" * 70)
    print("TEST 3: CIRCULAR EXECUTABILITY TEST")
    print("=" * 70)

    if grammar is None:
        print("  ERROR: Cannot run test - no grammar loaded")
        return {'VERDICT': 'INCONCLUSIVE', 'error': 'No grammar data'}

    # Extract forbidden transitions
    forbidden = set()
    forbidden_list = grammar.get('forbidden_transitions', grammar.get('forbidden_sequences', []))
    for trans in forbidden_list:
        if isinstance(trans, list) and len(trans) >= 2:
            forbidden.add((trans[0], trans[1]))
        elif isinstance(trans, dict):
            forbidden.add((trans.get('from', ''), trans.get('to', '')))
        elif isinstance(trans, str):
            # String format like "a->b"
            parts = trans.split('->')
            if len(parts) == 2:
                forbidden.add((parts[0].strip(), parts[1].strip()))

    print(f"  Loaded {len(forbidden)} forbidden transitions")

    def compute_legality(sequence, forbidden_set):
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

        original_seq = []
        for s in sectors:
            original_seq.extend(s['tokens'])

        original_legality = compute_legality(original_seq, forbidden)
        results['original_legality'].append(original_legality)

        rotation_legalities = []
        for rotation in range(1, len(sectors)):
            rotated_sectors = sectors[rotation:] + sectors[:rotation]
            rotated_seq = []
            for s in rotated_sectors:
                rotated_seq.extend(s['tokens'])
            rotation_legalities.append(compute_legality(rotated_seq, forbidden))

        mean_rotation = np.mean(rotation_legalities) if rotation_legalities else original_legality
        results['rotation_legality'].append(mean_rotation)

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
            'original': float(original_legality),
            'rotation_mean': float(mean_rotation),
            'random_mean': float(mean_random),
            'rotation_robust': bool(abs(original_legality - mean_rotation) < 0.05),
            'random_robust': bool(abs(original_legality - mean_random) < 0.05)
        }

        print(f"  {folio}: original={original_legality:.3f}, rotation={mean_rotation:.3f}, random={mean_random:.3f}")

    mean_original = float(np.mean(results['original_legality']))
    mean_rotation = float(np.mean(results['rotation_legality']))
    mean_random = float(np.mean(results['random_legality']))

    rotation_robust = abs(mean_original - mean_rotation) < 0.05
    random_robust = abs(mean_original - mean_random) < 0.05

    if rotation_robust and not random_robust:
        verdict = 'CYCLIC_CONTROL'
        interpretation = 'Rotation-robust but adjacency-dependent -> cyclic control layout'
    elif rotation_robust and random_robust:
        verdict = 'VISUAL_BUNDLING'
        interpretation = 'Fully reorder-robust -> visual bundling of independent runs'
    else:
        verdict = 'ORDER_DEPENDENT'
        interpretation = 'Not rotation-robust -> order matters'

    results['summary'] = {
        'mean_original': mean_original,
        'mean_rotation': mean_rotation,
        'mean_random': mean_random,
        'rotation_robust': bool(rotation_robust),
        'random_robust': bool(random_robust),
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
    """Test whether labels cluster near hazard boundaries."""
    print("\n" + "=" * 70)
    print("TEST 4: BOUNDARY CLUSTERING TEST")
    print("=" * 70)

    # Define hazard-adjacent tokens
    hazard_adjacent = set()
    if hazard_data:
        transitions = hazard_data.get('forbidden_transitions', hazard_data.get('transitions', []))
        for trans in transitions:
            if isinstance(trans, dict):
                hazard_adjacent.add(trans.get('from', ''))
                hazard_adjacent.add(trans.get('to', ''))
            elif isinstance(trans, list) and len(trans) >= 2:
                hazard_adjacent.add(trans[0])
                hazard_adjacent.add(trans[1])

    boundary_tokens = set(kernel_nodes) | hazard_adjacent
    print(f"  Boundary tokens: {list(boundary_tokens)[:10]}...")

    results = {
        'per_folio': {},
        'observed_density': [],
        'null_density': []
    }

    for folio, records in sorted(circular_folios.items()):
        tokens = [r['word'] for r in records]
        if not tokens:
            continue

        # Count tokens that contain kernel characters
        boundary_count = sum(1 for t in tokens if any(b in t for b in boundary_tokens))
        observed_density = boundary_count / len(tokens)
        results['observed_density'].append(observed_density)

        # Null model
        all_tokens = list(set(tokens))
        null_densities = []
        for _ in range(500):
            random_sample = random.choices(all_tokens, k=len(tokens))
            null_count = sum(1 for t in random_sample if any(b in t for b in boundary_tokens))
            null_densities.append(null_count / len(random_sample))

        null_mean = np.mean(null_densities)
        null_std = np.std(null_densities)
        z_score = (observed_density - null_mean) / max(null_std, 0.0001)

        results['null_density'].extend(null_densities)

        results['per_folio'][folio] = {
            'n_tokens': len(tokens),
            'boundary_count': int(boundary_count),
            'observed_density': float(observed_density),
            'null_mean': float(null_mean),
            'null_std': float(null_std),
            'z_score': float(z_score)
        }

        print(f"  {folio}: density={observed_density:.3f}, null={null_mean:.3f}, z={z_score:.2f}")

    mean_observed = float(np.mean(results['observed_density']))
    mean_null = float(np.mean(results['null_density']))
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
        'pooled_z_score': float(pooled_z),
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

equiv_data = load_frozen_grammar()
grammar = load_transition_grammar()
hazard_data = load_hazard_data()
kernel_data = load_kernel_data()
kernel_nodes = kernel_data.get('kernel_nodes', ['k', 'h', 'e'])

if equiv_data:
    print(f"    Loaded {len(equiv_data.get('member_to_class', {}))} class members")
print(f"    Kernel nodes: {kernel_nodes}")

# Run all tests
test1_results = test_locality_violation(circular_folios)
test2_results = test_class_novelty(circular_folios, all_folios, equiv_data)
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

# Determine KILL conditions
kill_conditions = []
if verdicts['Test 1 (Locality)'] == 'FAIL':
    kill_conditions.append("Persistent non-local dependencies detected")
if verdicts['Test 2 (Class Novelty)'] == 'FAIL':
    kill_conditions.append("Novel instruction classes may exist")

# Overall assessment
pass_count = sum(1 for v in verdicts.values() if v == 'PASS')
fail_count = sum(1 for v in verdicts.values() if v == 'FAIL')

if kill_conditions:
    overall = 'REQUIRES_INVESTIGATION'
elif pass_count >= 3:
    overall = 'CONFIRMS_CONTROL_GRAMMAR'
else:
    overall = 'INCONCLUSIVE'

print(f"\n  Overall: {overall}")
if kill_conditions:
    print(f"  Kill conditions triggered:")
    for kc in kill_conditions:
        print(f"    - {kc}")

# Save results
all_results = {
    'metadata': {
        'timestamp': datetime.now().isoformat(),
        'n_circular_folios': len(circular_folios),
        'n_records': sum(len(v) for v in circular_folios.values())
    },
    'test1_locality': {
        'summary': test1_results.get('summary', {}),
        'per_folio': test1_results.get('per_folio', {})
    },
    'test2_class_novelty': test2_results,
    'test3_circular_exec': {
        'summary': test3_results.get('summary', {}),
        'per_folio': test3_results.get('per_folio', {})
    },
    'test4_boundary': {
        'summary': test4_results.get('summary', {}),
        'per_folio': test4_results.get('per_folio', {})
    },
    'verdicts': verdicts,
    'kill_conditions': kill_conditions,
    'overall': overall
}

with open('C:/git/voynich/ccf_metrics.json', 'w') as f:
    json.dump(all_results, f, indent=2)

print("\n  Results saved to ccf_metrics.json")

# Generate report
report = f"""# Circular Control Folio (CCF) Analysis Report

*Generated: {datetime.now().isoformat()}*

---

## Executive Summary

| Test | Verdict |
|------|---------|
| Test 1: Locality Violation | {verdicts['Test 1 (Locality)']} |
| Test 2: Class Novelty | {verdicts['Test 2 (Class Novelty)']} |
| Test 3: Circular Executability | {verdicts['Test 3 (Circular Exec)']} |
| Test 4: Boundary Clustering | {verdicts['Test 4 (Boundary)']} |

**Overall Assessment:** {overall}

---

## Q1: LOCALITY - Do sector labels exert non-local influence?

**Method:** Compare cross-sector dependency density against null model (permuted sectors).

**Results:**
- Mean observed cross-sector density: {test1_results.get('summary', {}).get('mean_observed_density', 0):.4f}
- Mean null density: {test1_results.get('summary', {}).get('mean_null_density', 0):.4f}
- Significant deviations (p<0.05): {test1_results.get('summary', {}).get('significant_folios', 0)}/{test1_results.get('summary', {}).get('total_folios', 0)}

**VERDICT:** {verdicts['Test 1 (Locality)']}

**Interpretation:** {'Sectors operate primarily with local dependencies. No persistent cross-sector influence detected.' if verdicts['Test 1 (Locality)'] == 'PASS' else 'Non-local dependencies detected across sectors. This triggers a KILL condition.'}

---

## Q2: CLASS MEMBERSHIP - Are labels new instruction classes?

**Method:** Map all CCF tokens to frozen 49 classes.

**Results:**
- Total CCF occurrences: {test2_results.get('total_ccf_occurrences', 0)}
- Classified: {test2_results.get('classified_occurrences', 0)} ({test2_results.get('classified_rate', 0):.1%})
- Unclassified: {test2_results.get('unclassified_occurrences', 0)} ({test2_results.get('unclassified_rate', 0):.1%})
- Classes used: {test2_results.get('n_classes_used', 0)}

**VERDICT:** {verdicts['Test 2 (Class Novelty)']}

**Interpretation:** {test2_results.get('interpretation', 'N/A')}

---

## Q3: CIRCULAR ORDER - Is circular ordering executably required?

**Method:** Compare transition legality under original order, rotations, and random reordering.

**Results:**
- Mean original legality: {test3_results.get('summary', {}).get('mean_original', 0):.4f}
- Mean rotation legality: {test3_results.get('summary', {}).get('mean_rotation', 0):.4f}
- Mean random legality: {test3_results.get('summary', {}).get('mean_random', 0):.4f}

**VERDICT:** {verdicts['Test 3 (Circular Exec)']}

**Interpretation:** {test3_results.get('summary', {}).get('interpretation', 'N/A')}

---

## Q4: BOUNDARY FUNCTION - Do labels cluster near hazard boundaries?

**Method:** Measure label density as function of hazard/kernel proximity.

**Results:**
- Mean observed boundary density: {test4_results.get('summary', {}).get('mean_observed_density', 0):.4f}
- Mean null density: {test4_results.get('summary', {}).get('mean_null_density', 0):.4f}
- Pooled Z-score: {test4_results.get('summary', {}).get('pooled_z_score', 0):.2f}

**VERDICT:** {verdicts['Test 4 (Boundary)']}

**Interpretation:** {test4_results.get('summary', {}).get('interpretation', 'N/A')}

---

## Kill Conditions

{'**No kill conditions triggered.**' if not kill_conditions else chr(10).join(['- ' + kc for kc in kill_conditions])}

---

## Interpretive Firewall Statement

> All findings describe operational roles, structural functions, and execution constraints.
> No semantic interpretation (astronomy, months, symbols, zodiac) has been applied.
> Domain nouns have been strictly avoided per pre-registration.
> This behavior is classified based purely on structural and statistical properties.

---

*Report generated by CCF Analysis Suite v2.0*
"""

with open('C:/git/voynich/ccf_analysis_report.md', 'w') as f:
    f.write(report)

print("  Report saved to ccf_analysis_report.md")
print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
