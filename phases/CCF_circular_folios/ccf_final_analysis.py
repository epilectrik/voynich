# CCF Final Analysis - Circular Control Folio Structural Analysis
# Pre-registered falsification tests for circular folios
# NO semantic interpretation - purely operational analysis

import json
import re
import random
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime

print("=" * 70)
print("CIRCULAR CONTROL FOLIO (CCF) ANALYSIS - FINAL")
print("Pre-registered structural test suite")
print("Generated:", datetime.now().isoformat())
print("=" * 70)

# =============================================================================
# DATA LOADING
# =============================================================================

def load_corpus():
    records = []
    with open('C:/git/voynich/data/transcriptions/interlinear_full_words.txt', 'r', encoding='latin-1') as f:
        f.readline()  # skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 12:
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
    try:
        with open('C:/git/voynich/phase20a_operator_equivalence.json', 'r') as f:
            data = json.load(f)
        member_to_class = {}
        class_info = {}
        for cls in data.get('classes', []):
            class_id = cls['class_id']
            class_info[class_id] = cls
            for member in cls.get('members', []):
                if member:
                    member_to_class[member] = class_id
        return {'member_to_class': member_to_class, 'class_info': class_info}
    except Exception as e:
        print(f"  Warning: Could not load grammar: {e}")
        return None

def load_forbidden_transitions():
    """Load forbidden transitions from phase18a."""
    forbidden = set()
    hazard_nodes = set()
    try:
        with open('C:/git/voynich/phase18a_forbidden_inventory.json', 'r') as f:
            data = json.load(f)
        for trans in data.get('transitions', []):
            source = trans.get('source', '')
            target = trans.get('target', '')
            if source and target:
                forbidden.add((source, target))
                hazard_nodes.add(source)
                hazard_nodes.add(target)
        print(f"    Loaded {len(forbidden)} forbidden transitions")
        print(f"    Hazard-adjacent nodes: {len(hazard_nodes)}")
        return forbidden, hazard_nodes
    except Exception as e:
        print(f"    Warning: Could not load forbidden transitions: {e}")
        return set(), set()

# =============================================================================
# SECTOR SEGMENTATION
# =============================================================================

def segment_into_sectors(folio_records):
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
    if equiv_data is None:
        return None
    member_to_class = equiv_data.get('member_to_class', {})
    if token in member_to_class:
        return member_to_class[token]
    for member in member_to_class:
        if len(member) >= 3 and (token.startswith(member) or member.startswith(token)):
            return member_to_class[member]
    return None

# =============================================================================
# DEPENDENCY GRAPH CONSTRUCTION
# =============================================================================

def build_adjacency_graph(sectors):
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
    print("\n" + "=" * 70)
    print("TEST 1: LOCALITY VIOLATION TEST")
    print("=" * 70)

    results = {'per_folio': {}, 'observed': [], 'null': [], 'p_values': []}

    for folio, records in sorted(circular_folios.items()):
        sectors = segment_into_sectors(records)
        if len(sectors) < 2:
            continue

        edges, within, cross = build_adjacency_graph(sectors)
        total_edges = sum(edges.values())
        cross_edges = sum(cross.values())
        observed_density = cross_edges / max(total_edges, 1)
        results['observed'].append(observed_density)

        null_densities = []
        for _ in range(n_permutations):
            permuted = []
            for s in sectors:
                tokens_copy = s['tokens'][:]
                random.shuffle(tokens_copy)
                permuted.append({'sector_id': s['sector_id'], 'tokens': tokens_copy})
            _, _, null_cross = build_adjacency_graph(permuted)
            null_cross_edges = sum(null_cross.values())
            null_densities.append(null_cross_edges / max(total_edges, 1))

        results['null'].extend(null_densities)
        p_value = sum(1 for nd in null_densities if nd >= observed_density) / len(null_densities)
        results['p_values'].append(p_value)

        results['per_folio'][folio] = {
            'n_sectors': len(sectors),
            'observed_density': float(observed_density),
            'null_mean': float(np.mean(null_densities)),
            'p_value': float(p_value)
        }
        print(f"  {folio}: {len(sectors)} sectors, cross={observed_density:.4f}, p={p_value:.4f}")

    mean_obs = float(np.mean(results['observed']))
    mean_null = float(np.mean(results['null']))
    sig_count = sum(1 for p in results['p_values'] if p < 0.05)

    verdict = 'PASS' if sig_count < len(results['p_values']) * 0.1 else 'FAIL'

    results['summary'] = {
        'mean_observed': mean_obs,
        'mean_null': mean_null,
        'significant_folios': sig_count,
        'total_folios': len(results['p_values']),
        'VERDICT': verdict
    }

    print(f"\n  Mean observed: {mean_obs:.4f}, Mean null: {mean_null:.4f}")
    print(f"  Significant (p<0.05): {sig_count}/{len(results['p_values'])}")
    print(f"  VERDICT: {verdict}")

    return results

# =============================================================================
# TEST 2: CLASS NOVELTY TEST
# =============================================================================

def test_class_novelty(circular_folios, all_folios, equiv_data):
    print("\n" + "=" * 70)
    print("TEST 2: CLASS NOVELTY TEST")
    print("=" * 70)

    if equiv_data is None:
        return {'VERDICT': 'INCONCLUSIVE', 'error': 'No data'}

    circular_set = set(circular_folios.keys())
    ccf_tokens = Counter()
    non_ccf_tokens = Counter()

    for folio, records in all_folios.items():
        target = ccf_tokens if folio in circular_set else non_ccf_tokens
        for r in records:
            target[r['word']] += 1

    classified = 0
    unclassified = 0
    class_dist = Counter()
    unclassified_list = []

    for token, count in ccf_tokens.items():
        cls = get_token_class(token, equiv_data)
        if cls is not None:
            classified += count
            class_dist[cls] += count
        else:
            unclassified += count
            if len(unclassified_list) < 50:
                unclassified_list.append(token)

    total = classified + unclassified
    classified_rate = classified / max(total, 1)

    if classified_rate >= 0.7:
        verdict = 'PASS'
        interp = 'CCF tokens map to existing instruction classes (positional variants)'
    elif classified_rate >= 0.5:
        verdict = 'INCONCLUSIVE'
        interp = 'Mixed classification - partial mapping to existing classes'
    else:
        verdict = 'FAIL'
        interp = 'KILL: Majority of CCF tokens may form novel classes'

    results = {
        'total_types': len(ccf_tokens),
        'total_occurrences': int(total),
        'classified': int(classified),
        'unclassified': int(unclassified),
        'classified_rate': float(classified_rate),
        'n_classes_used': len(class_dist),
        'sample_unclassified': unclassified_list[:20],
        'VERDICT': verdict,
        'interpretation': interp
    }

    print(f"  Total types: {len(ccf_tokens)}, Occurrences: {total}")
    print(f"  Classified: {classified} ({classified_rate:.1%})")
    print(f"  Classes used: {len(class_dist)}/49")
    print(f"  VERDICT: {verdict}")

    return results

# =============================================================================
# TEST 3: CIRCULAR EXECUTABILITY TEST
# =============================================================================

def test_circular_executability(circular_folios, forbidden, n_trials=100):
    print("\n" + "=" * 70)
    print("TEST 3: CIRCULAR EXECUTABILITY TEST")
    print("=" * 70)

    if not forbidden:
        print("  No forbidden transitions available")
        return {'VERDICT': 'INCONCLUSIVE', 'error': 'No forbidden transitions'}

    def compute_legality(sequence):
        if len(sequence) < 2:
            return 1.0
        violations = 0
        for i in range(len(sequence) - 1):
            if (sequence[i], sequence[i+1]) in forbidden:
                violations += 1
        return 1.0 - (violations / (len(sequence) - 1))

    results = {'per_folio': {}, 'original': [], 'rotation': [], 'random': []}

    for folio, records in sorted(circular_folios.items()):
        sectors = segment_into_sectors(records)
        if len(sectors) < 3:
            continue

        original_seq = []
        for s in sectors:
            original_seq.extend(s['tokens'])

        orig_legal = compute_legality(original_seq)
        results['original'].append(orig_legal)

        rot_legalities = []
        for r in range(1, len(sectors)):
            rotated = sectors[r:] + sectors[:r]
            rot_seq = []
            for s in rotated:
                rot_seq.extend(s['tokens'])
            rot_legalities.append(compute_legality(rot_seq))

        mean_rot = np.mean(rot_legalities) if rot_legalities else orig_legal
        results['rotation'].append(mean_rot)

        rand_legalities = []
        for _ in range(n_trials):
            shuffled = sectors[:]
            random.shuffle(shuffled)
            rand_seq = []
            for s in shuffled:
                rand_seq.extend(s['tokens'])
            rand_legalities.append(compute_legality(rand_seq))

        mean_rand = np.mean(rand_legalities)
        results['random'].append(mean_rand)

        results['per_folio'][folio] = {
            'n_sectors': len(sectors),
            'original': float(orig_legal),
            'rotation_mean': float(mean_rot),
            'random_mean': float(mean_rand)
        }

        print(f"  {folio}: orig={orig_legal:.3f}, rot={mean_rot:.3f}, rand={mean_rand:.3f}")

    mean_orig = float(np.mean(results['original']))
    mean_rot = float(np.mean(results['rotation']))
    mean_rand = float(np.mean(results['random']))

    rot_robust = abs(mean_orig - mean_rot) < 0.05
    rand_robust = abs(mean_orig - mean_rand) < 0.05

    if rot_robust and rand_robust:
        verdict = 'VISUAL_BUNDLING'
        interp = 'Fully reorder-robust: circular layout is visual bundling of independent linear runs'
    elif rot_robust and not rand_robust:
        verdict = 'CYCLIC_CONTROL'
        interp = 'Rotation-robust but adjacency-dependent: cyclic control layout'
    else:
        verdict = 'ORDER_DEPENDENT'
        interp = 'Not rotation-robust: specific circular order required'

    results['summary'] = {
        'mean_original': mean_orig,
        'mean_rotation': mean_rot,
        'mean_random': mean_rand,
        'rotation_robust': bool(rot_robust),
        'random_robust': bool(rand_robust),
        'VERDICT': verdict,
        'interpretation': interp
    }

    print(f"\n  Mean: orig={mean_orig:.4f}, rot={mean_rot:.4f}, rand={mean_rand:.4f}")
    print(f"  VERDICT: {verdict}")
    print(f"  Interpretation: {interp}")

    return results

# =============================================================================
# TEST 4: BOUNDARY CLUSTERING TEST
# =============================================================================

def test_boundary_clustering(circular_folios, hazard_nodes):
    print("\n" + "=" * 70)
    print("TEST 4: BOUNDARY CLUSTERING TEST")
    print("=" * 70)

    if not hazard_nodes:
        print("  No hazard nodes available")
        return {'VERDICT': 'INCONCLUSIVE', 'error': 'No hazard data'}

    print(f"  Hazard-adjacent tokens: {sorted(list(hazard_nodes))}")

    results = {'per_folio': {}, 'observed': [], 'null': []}

    for folio, records in sorted(circular_folios.items()):
        tokens = [r['word'] for r in records]
        if not tokens:
            continue

        # Count exact matches to hazard nodes
        hazard_count = sum(1 for t in tokens if t in hazard_nodes)
        observed_density = hazard_count / len(tokens)
        results['observed'].append(observed_density)

        # Null: random sampling from folio vocabulary
        vocab = list(set(tokens))
        null_densities = []
        for _ in range(500):
            sample = random.choices(vocab, k=len(tokens))
            null_count = sum(1 for t in sample if t in hazard_nodes)
            null_densities.append(null_count / len(sample))

        null_mean = np.mean(null_densities)
        null_std = np.std(null_densities)
        z = (observed_density - null_mean) / max(null_std, 0.0001)

        results['null'].extend(null_densities)
        results['per_folio'][folio] = {
            'n_tokens': len(tokens),
            'hazard_count': int(hazard_count),
            'observed_density': float(observed_density),
            'null_mean': float(null_mean),
            'z_score': float(z)
        }

        print(f"  {folio}: hazard={hazard_count}/{len(tokens)} ({observed_density:.3f}), z={z:.2f}")

    mean_obs = float(np.mean(results['observed']))
    mean_null = float(np.mean(results['null']))
    pooled_z = (mean_obs - mean_null) / max(np.std(results['null']), 0.0001)

    if pooled_z > 2.0:
        verdict = 'BOUNDARY_CLUSTERED'
        interp = 'Labels disproportionately occur at hazard boundaries'
    elif pooled_z < -2.0:
        verdict = 'BOUNDARY_AVOIDED'
        interp = 'Labels avoid hazard boundaries'
    else:
        verdict = 'NO_CLUSTERING'
        interp = 'No significant clustering pattern at hazard boundaries'

    results['summary'] = {
        'mean_observed': mean_obs,
        'mean_null': mean_null,
        'pooled_z': float(pooled_z),
        'hazard_nodes': sorted(list(hazard_nodes)),
        'VERDICT': verdict,
        'interpretation': interp
    }

    print(f"\n  Mean observed: {mean_obs:.4f}, Mean null: {mean_null:.4f}")
    print(f"  Pooled Z: {pooled_z:.2f}")
    print(f"  VERDICT: {verdict}")

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
forbidden, hazard_nodes = load_forbidden_transitions()

if equiv_data:
    print(f"    Loaded {len(equiv_data.get('member_to_class', {}))} class members")

# Run all tests
test1 = test_locality_violation(circular_folios)
test2 = test_class_novelty(circular_folios, all_folios, equiv_data)
test3 = test_circular_executability(circular_folios, forbidden)
test4 = test_boundary_clustering(circular_folios, hazard_nodes)

# =============================================================================
# FINAL VERDICT
# =============================================================================

print("\n" + "=" * 70)
print("FINAL VERDICT")
print("=" * 70)

verdicts = {
    'Q1_Locality': test1.get('summary', {}).get('VERDICT', 'UNKNOWN'),
    'Q2_ClassNovelty': test2.get('VERDICT', 'UNKNOWN'),
    'Q3_CircularOrder': test3.get('summary', {}).get('VERDICT', 'UNKNOWN'),
    'Q4_Boundary': test4.get('summary', {}).get('VERDICT', 'UNKNOWN')
}

for q, v in verdicts.items():
    status = "PASS" if v in ['PASS', 'VISUAL_BUNDLING', 'NO_CLUSTERING'] else "INVESTIGATE" if v == 'INCONCLUSIVE' else "FAIL"
    print(f"  {q}: {v} [{status}]")

# Kill conditions
kill_conditions = []
if verdicts['Q1_Locality'] == 'FAIL':
    kill_conditions.append("Non-local dependencies persist across sectors")
if verdicts['Q2_ClassNovelty'] == 'FAIL':
    kill_conditions.append("Novel instruction classes detected")

if kill_conditions:
    print(f"\n  KILL CONDITIONS TRIGGERED:")
    for kc in kill_conditions:
        print(f"    - {kc}")
    overall = 'REQUIRES_MODEL_REVISION'
else:
    overall = 'CONFIRMS_EXISTING_GRAMMAR'

print(f"\n  OVERALL: {overall}")

# Save results
all_results = {
    'metadata': {
        'timestamp': datetime.now().isoformat(),
        'n_circular_folios': len(circular_folios),
        'n_records': sum(len(v) for v in circular_folios.values())
    },
    'test1_locality': test1,
    'test2_class_novelty': test2,
    'test3_circular_order': test3,
    'test4_boundary': test4,
    'verdicts': verdicts,
    'kill_conditions': kill_conditions,
    'overall': overall
}

with open('C:/git/voynich/ccf_metrics.json', 'w') as f:
    json.dump(all_results, f, indent=2)
print("\n  Saved: ccf_metrics.json")

# Generate report
report = f"""# Circular Control Folio (CCF) Analysis Report

*Generated: {datetime.now().isoformat()}*

---

## Executive Summary

| Question | Test | Verdict |
|----------|------|---------|
| Q1: Locality | Do sector labels exert non-local influence? | **{verdicts['Q1_Locality']}** |
| Q2: Class Membership | Are labels new instruction classes? | **{verdicts['Q2_ClassNovelty']}** |
| Q3: Circular Order | Is circular ordering executably required? | **{verdicts['Q3_CircularOrder']}** |
| Q4: Boundary Function | Do labels cluster at hazard boundaries? | **{verdicts['Q4_Boundary']}** |

**Overall Assessment:** {overall}

{'**KILL CONDITIONS TRIGGERED:** ' + ', '.join(kill_conditions) if kill_conditions else '**No kill conditions triggered.**'}

---

## Test 1: LOCALITY VIOLATION

**Question:** Do label tokens on a given sector exert non-local influence?

**Method:** Compare cross-sector dependency density against null model (within-sector permutation).

**Results:**
- Mean observed cross-sector density: {test1.get('summary', {}).get('mean_observed', 0):.4f}
- Mean null density: {test1.get('summary', {}).get('mean_null', 0):.4f}
- Significant deviations (p<0.05): {test1.get('summary', {}).get('significant_folios', 0)}/{test1.get('summary', {}).get('total_folios', 0)}

**VERDICT:** {verdicts['Q1_Locality']}

**Interpretation:** {'Sectors operate with local dependencies only. No persistent cross-sector influence detected.' if verdicts['Q1_Locality'] == 'PASS' else 'KILL: Persistent non-local dependencies detected.'}

---

## Test 2: CLASS NOVELTY

**Question:** Do any label tokens form new instruction classes, or are they positional variants of existing classes?

**Method:** Map all CCF tokens to frozen 49-class grammar.

**Results:**
- Total CCF token types: {test2.get('total_types', 0)}
- Total occurrences: {test2.get('total_occurrences', 0)}
- Classified to existing classes: {test2.get('classified', 0)} ({test2.get('classified_rate', 0):.1%})
- Unclassified: {test2.get('unclassified', 0)}
- Classes used: {test2.get('n_classes_used', 0)}/49

**VERDICT:** {verdicts['Q2_ClassNovelty']}

**Interpretation:** {test2.get('interpretation', 'N/A')}

---

## Test 3: CIRCULAR EXECUTABILITY

**Question:** Is the circular order executably required, or merely visual bundling?

**Method:** Compare transition legality under original order, rotations, and random reordering.

**Results:**
- Mean original legality: {test3.get('summary', {}).get('mean_original', 0):.4f}
- Mean rotation legality: {test3.get('summary', {}).get('mean_rotation', 0):.4f}
- Mean random legality: {test3.get('summary', {}).get('mean_random', 0):.4f}
- Rotation-robust: {test3.get('summary', {}).get('rotation_robust', False)}
- Random-robust: {test3.get('summary', {}).get('random_robust', False)}

**VERDICT:** {verdicts['Q3_CircularOrder']}

**Interpretation:** {test3.get('summary', {}).get('interpretation', 'N/A')}

---

## Test 4: BOUNDARY CLUSTERING

**Question:** Do labels disproportionately occur near hazard boundaries or stability bottlenecks?

**Method:** Measure hazard-node density compared to null model (matched-count random placement).

**Results:**
- Mean observed hazard density: {test4.get('summary', {}).get('mean_observed', 0):.4f}
- Mean null density: {test4.get('summary', {}).get('mean_null', 0):.4f}
- Pooled Z-score: {test4.get('summary', {}).get('pooled_z', 0):.2f}
- Hazard nodes tested: {', '.join(test4.get('summary', {}).get('hazard_nodes', [])[:10])}...

**VERDICT:** {verdicts['Q4_Boundary']}

**Interpretation:** {test4.get('summary', {}).get('interpretation', 'N/A')}

---

## Conclusions

1. **Locality:** {'The circular layout does NOT impose non-local constraints. Each sector operates as an independent linear run.' if verdicts['Q1_Locality'] == 'PASS' else 'Non-local dependencies detected - requires investigation.'}

2. **Class Membership:** {'CCF labels are positional variants of existing instruction classes, not novel constructs.' if verdicts['Q2_ClassNovelty'] == 'PASS' else test2.get('interpretation', '')}

3. **Circular Order:** {test3.get('summary', {}).get('interpretation', '')}

4. **Boundary Function:** {'No special clustering at hazard boundaries - labels are distributed normally within folio vocabulary.' if verdicts['Q4_Boundary'] == 'NO_CLUSTERING' else test4.get('summary', {}).get('interpretation', '')}

---

## Interpretive Firewall Statement

> All findings describe operational roles, structural functions, and execution constraints only.
> No semantic interpretation (astronomy, months, zodiac, symbols) has been applied.
> Domain nouns have been strictly avoided per pre-registration.
>
> If interpretation pressure arises: "This behavior is unclassifiable at present without violating semantic constraints."

---

*Report generated by CCF Analysis Suite - Final Version*
"""

with open('C:/git/voynich/ccf_analysis_report.md', 'w') as f:
    f.write(report)
print("  Saved: ccf_analysis_report.md")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
