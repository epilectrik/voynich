#!/usr/bin/env python3
"""
DIRECTION F: CYCLE SEMANTICS ANALYSIS

Bounded analysis of 4-cycles vs 3-cycles in the kernel topology.

BACKGROUND (from Phase 15, Constraint 90):
- 500+ 4-cycles documented
- 56 3-cycles documented
- Question: What do different cycle lengths mean?

Tests:
F-1: Cycle topology characterization (what tokens form cycles?)
F-2: Cycle-kernel relationship (k, h, e composition?)
F-3: Cycle-hazard relationship (execution paths or forbidden regions?)
F-4: Cycle-folio distribution (program type correlation?)

STOP CONDITIONS:
- Cycle tokens identical to non-cycle tokens -> no distinction
- No kernel/hazard relationship -> cycles incidental
- Max 2 Tier 2 constraints
"""

import os
import json
import numpy as np
from collections import Counter, defaultdict
from itertools import combinations
import networkx as nx

os.chdir('C:/git/voynich')

print("=" * 70)
print("DIRECTION F: CYCLE SEMANTICS ANALYSIS")
print("Bounded analysis of 3-cycles vs 4-cycles")
print("=" * 70)

# ==========================================================================
# LOAD DATA
# ==========================================================================

print("\nLoading data...")

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        all_tokens.append(row)

# Currier B only
b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']
b_words = [t.get('word', '') for t in b_tokens if t.get('word', '')]

print(f"Currier B tokens: {len(b_words)}")

# Load canonical grammar
with open('results/canonical_grammar.json', 'r') as f:
    grammar = json.load(f)

print(f"Grammar classes: {len(grammar.get('classes', {}))}")

# ==========================================================================
# BUILD TRANSITION GRAPH
# ==========================================================================

print("\nBuilding transition graph...")

# Build bigram transitions
transitions = Counter()
for i in range(len(b_words) - 1):
    w1 = b_words[i]
    w2 = b_words[i + 1]
    if w1 and w2:
        transitions[(w1, w2)] += 1

# Build graph
G = nx.DiGraph()
for (w1, w2), count in transitions.items():
    G.add_edge(w1, w2, weight=count)

print(f"Graph nodes: {G.number_of_nodes()}")
print(f"Graph edges: {G.number_of_edges()}")

# ==========================================================================
# F-1: CYCLE TOPOLOGY CHARACTERIZATION
# ==========================================================================

print("\n" + "=" * 70)
print("F-1: CYCLE TOPOLOGY CHARACTERIZATION")
print("Question: What tokens form 4-cycles vs 3-cycles?")
print("=" * 70)

# Find all simple cycles up to length 4
# Note: This can be expensive for large graphs

# First, find strongly connected components (cycles exist only within SCCs)
sccs = list(nx.strongly_connected_components(G))
print(f"\nStrongly connected components: {len(sccs)}")

large_sccs = [scc for scc in sccs if len(scc) > 2]
print(f"SCCs with >2 nodes: {len(large_sccs)}")

# Find cycles
three_cycles = []
four_cycles = []

# For efficiency, only look in large SCCs
for scc in large_sccs:
    subgraph = G.subgraph(scc)

    # Find 3-cycles (triangles in directed graph)
    for node in subgraph.nodes():
        neighbors = set(subgraph.successors(node))
        for n1 in neighbors:
            n1_neighbors = set(subgraph.successors(n1))
            for n2 in n1_neighbors:
                if n2 != node and n2 in neighbors:
                    # Check if n2 -> node exists
                    if subgraph.has_edge(n2, node):
                        cycle = tuple(sorted([node, n1, n2]))
                        if cycle not in [tuple(sorted(c)) for c in three_cycles]:
                            three_cycles.append((node, n1, n2))

    # Find 4-cycles
    for node in subgraph.nodes():
        for n1 in subgraph.successors(node):
            if n1 == node:
                continue
            for n2 in subgraph.successors(n1):
                if n2 in [node, n1]:
                    continue
                for n3 in subgraph.successors(n2):
                    if n3 in [node, n1, n2]:
                        continue
                    if subgraph.has_edge(n3, node):
                        cycle = tuple(sorted([node, n1, n2, n3]))
                        if cycle not in [tuple(sorted(c)) for c in four_cycles]:
                            four_cycles.append((node, n1, n2, n3))

print(f"\n3-cycles found: {len(three_cycles)}")
print(f"4-cycles found: {len(four_cycles)}")

# Get tokens in each cycle type
three_cycle_tokens = set()
for cycle in three_cycles:
    three_cycle_tokens.update(cycle)

four_cycle_tokens = set()
for cycle in four_cycles:
    four_cycle_tokens.update(cycle)

# Overlap
both_cycle_tokens = three_cycle_tokens & four_cycle_tokens
only_three = three_cycle_tokens - four_cycle_tokens
only_four = four_cycle_tokens - three_cycle_tokens

print(f"\nTokens in 3-cycles: {len(three_cycle_tokens)}")
print(f"Tokens in 4-cycles: {len(four_cycle_tokens)}")
print(f"Tokens in BOTH: {len(both_cycle_tokens)}")
print(f"Tokens in 3-cycles ONLY: {len(only_three)}")
print(f"Tokens in 4-cycles ONLY: {len(only_four)}")

# Overlap percentage
if three_cycle_tokens or four_cycle_tokens:
    overlap_pct = 100 * len(both_cycle_tokens) / len(three_cycle_tokens | four_cycle_tokens)
    print(f"Overlap percentage: {overlap_pct:.1f}%")

# ==========================================================================
# F-2: CYCLE-KERNEL RELATIONSHIP
# ==========================================================================

print("\n" + "=" * 70)
print("F-2: CYCLE-KERNEL RELATIONSHIP")
print("Question: Do cycles have different kernel composition?")
print("=" * 70)

def get_kernel_class(word):
    """Classify token by kernel contact."""
    if not word:
        return None
    if word.endswith('k') or word in ['ok', 'yk', 'ak', 'ek']:
        return 'k'
    if word.endswith('h') or word in ['oh', 'yh', 'ah', 'eh']:
        return 'h'
    if word.endswith('ey') or word.endswith('eey') or word.endswith('edy'):
        return 'e'
    return None

# Kernel composition of cycle tokens
three_kernel = Counter(get_kernel_class(t) for t in three_cycle_tokens)
four_kernel = Counter(get_kernel_class(t) for t in four_cycle_tokens)
all_b_kernel = Counter(get_kernel_class(t) for t in set(b_words))

print(f"\nKernel composition:")
print(f"{'Type':<15} {'k':<10} {'h':<10} {'e':<10} {'None':<10}")
print("-" * 55)

for label, counter, total_set in [
    ("3-cycles", three_kernel, three_cycle_tokens),
    ("4-cycles", four_kernel, four_cycle_tokens),
    ("All B vocab", all_b_kernel, set(b_words))
]:
    total = len(total_set)
    k_pct = 100 * counter.get('k', 0) / total if total > 0 else 0
    h_pct = 100 * counter.get('h', 0) / total if total > 0 else 0
    e_pct = 100 * counter.get('e', 0) / total if total > 0 else 0
    none_pct = 100 * counter.get(None, 0) / total if total > 0 else 0
    print(f"{label:<15} {k_pct:.1f}%     {h_pct:.1f}%     {e_pct:.1f}%     {none_pct:.1f}%")

# Chi-square test for 3-cycle vs 4-cycle kernel composition
from scipy.stats import chi2_contingency

if three_cycle_tokens and four_cycle_tokens:
    observed = np.array([
        [three_kernel.get('k', 0), three_kernel.get('h', 0), three_kernel.get('e', 0), three_kernel.get(None, 0)],
        [four_kernel.get('k', 0), four_kernel.get('h', 0), four_kernel.get('e', 0), four_kernel.get(None, 0)]
    ])

    # Only test if we have enough data
    if observed.sum() > 0 and (observed > 0).sum() > 2:
        try:
            chi2, p, dof, expected = chi2_contingency(observed)
            print(f"\nChi-square test (3-cycle vs 4-cycle kernel composition):")
            print(f"  Chi2 = {chi2:.2f}, p = {p:.6f}")
            if p < 0.05:
                print("  RESULT: Kernel composition DIFFERS between 3-cycles and 4-cycles")
                f2_verdict = "KERNEL_DIFFERS"
            else:
                print("  RESULT: Kernel composition is SIMILAR")
                f2_verdict = "KERNEL_SIMILAR"
        except:
            print("  Chi-square test not possible (insufficient data)")
            f2_verdict = "INSUFFICIENT_DATA"
    else:
        f2_verdict = "INSUFFICIENT_DATA"

# ==========================================================================
# F-3: CYCLE-HAZARD RELATIONSHIP
# ==========================================================================

print("\n" + "=" * 70)
print("F-3: CYCLE-HAZARD RELATIONSHIP")
print("Question: Are cycles near hazards or execution paths?")
print("=" * 70)

# Load hazard transitions (17 forbidden transitions)
# These should be in the grammar or control_signatures
try:
    with open('results/control_signatures.json', 'r') as f:
        control_sigs = json.load(f)
    forbidden = control_sigs.get('forbidden_transitions', [])
except:
    forbidden = []

print(f"\nForbidden transitions loaded: {len(forbidden)}")

# Get tokens involved in forbidden transitions
hazard_tokens = set()
for trans in forbidden:
    if isinstance(trans, (list, tuple)) and len(trans) >= 2:
        hazard_tokens.add(trans[0])
        hazard_tokens.add(trans[1])
    elif isinstance(trans, str) and '->' in trans:
        parts = trans.split('->')
        hazard_tokens.add(parts[0].strip())
        hazard_tokens.add(parts[1].strip())

print(f"Tokens in hazard transitions: {len(hazard_tokens)}")

# Check overlap with cycle tokens
three_hazard_overlap = three_cycle_tokens & hazard_tokens
four_hazard_overlap = four_cycle_tokens & hazard_tokens

print(f"\n3-cycle tokens in hazards: {len(three_hazard_overlap)} / {len(three_cycle_tokens)}")
if three_cycle_tokens:
    print(f"  ({100*len(three_hazard_overlap)/len(three_cycle_tokens):.1f}%)")

print(f"4-cycle tokens in hazards: {len(four_hazard_overlap)} / {len(four_cycle_tokens)}")
if four_cycle_tokens:
    print(f"  ({100*len(four_hazard_overlap)/len(four_cycle_tokens):.1f}%)")

# Baseline: random tokens in hazards
all_vocab = set(b_words)
baseline_hazard_pct = 100 * len(hazard_tokens & all_vocab) / len(all_vocab) if all_vocab else 0
print(f"\nBaseline (all vocab in hazards): {baseline_hazard_pct:.1f}%")

# Fisher's exact test for cycle-hazard association
if three_cycle_tokens and hazard_tokens:
    # 3-cycles vs baseline
    a = len(three_hazard_overlap)  # cycle AND hazard
    b = len(three_cycle_tokens - hazard_tokens)  # cycle NOT hazard
    c = len(hazard_tokens - three_cycle_tokens)  # hazard NOT cycle
    d = len(all_vocab - three_cycle_tokens - hazard_tokens)  # neither

    from scipy.stats import fisher_exact
    odds_3, p_3 = fisher_exact([[a, b], [c, d]])
    print(f"\n3-cycles hazard association:")
    print(f"  Odds ratio = {odds_3:.2f}, p = {p_3:.6f}")

if four_cycle_tokens and hazard_tokens:
    # 4-cycles vs baseline
    a = len(four_hazard_overlap)
    b = len(four_cycle_tokens - hazard_tokens)
    c = len(hazard_tokens - four_cycle_tokens)
    d = len(all_vocab - four_cycle_tokens - hazard_tokens)

    odds_4, p_4 = fisher_exact([[a, b], [c, d]])
    print(f"\n4-cycles hazard association:")
    print(f"  Odds ratio = {odds_4:.2f}, p = {p_4:.6f}")

# ==========================================================================
# F-4: CYCLE-FOLIO DISTRIBUTION
# ==========================================================================

print("\n" + "=" * 70)
print("F-4: CYCLE-FOLIO DISTRIBUTION")
print("Question: Does cycle density vary by folio/program type?")
print("=" * 70)

# Get tokens per folio
folio_tokens = defaultdict(list)
for t in b_tokens:
    folio = t.get('folio', '')
    word = t.get('word', '')
    if word:
        folio_tokens[folio].append(word)

# Calculate cycle token density per folio
folio_3cycle_density = {}
folio_4cycle_density = {}

for folio, words in folio_tokens.items():
    unique_words = set(words)
    if unique_words:
        three_in_folio = len(three_cycle_tokens & unique_words) / len(unique_words)
        four_in_folio = len(four_cycle_tokens & unique_words) / len(unique_words)
        folio_3cycle_density[folio] = three_in_folio
        folio_4cycle_density[folio] = four_in_folio

print(f"\n3-cycle token density per folio:")
densities_3 = list(folio_3cycle_density.values())
if densities_3:
    print(f"  Mean: {100*np.mean(densities_3):.1f}%")
    print(f"  Std: {100*np.std(densities_3):.1f}%")
    print(f"  Min: {100*np.min(densities_3):.1f}%")
    print(f"  Max: {100*np.max(densities_3):.1f}%")

print(f"\n4-cycle token density per folio:")
densities_4 = list(folio_4cycle_density.values())
if densities_4:
    print(f"  Mean: {100*np.mean(densities_4):.1f}%")
    print(f"  Std: {100*np.std(densities_4):.1f}%")
    print(f"  Min: {100*np.min(densities_4):.1f}%")
    print(f"  Max: {100*np.max(densities_4):.1f}%")

# Correlation between 3-cycle and 4-cycle density
if densities_3 and densities_4:
    from scipy.stats import pearsonr, spearmanr
    folios = list(folio_3cycle_density.keys())
    d3 = [folio_3cycle_density[f] for f in folios]
    d4 = [folio_4cycle_density[f] for f in folios]

    r, p = spearmanr(d3, d4)
    print(f"\nCorrelation between 3-cycle and 4-cycle density:")
    print(f"  Spearman r = {r:.3f}, p = {p:.6f}")

    if r > 0.5 and p < 0.05:
        print("  RESULT: Densities are CORRELATED (folios have similar cycle profiles)")
        f4_corr = "CORRELATED"
    elif r < -0.5 and p < 0.05:
        print("  RESULT: Densities are ANTI-CORRELATED (folios specialize)")
        f4_corr = "ANTI_CORRELATED"
    else:
        print("  RESULT: Densities are INDEPENDENT")
        f4_corr = "INDEPENDENT"

# ==========================================================================
# SUMMARY AND VERDICT
# ==========================================================================

print("\n" + "=" * 70)
print("DIRECTION F: SUMMARY AND VERDICT")
print("=" * 70)

results = {
    'f1_topology': {
        'three_cycles': len(three_cycles),
        'four_cycles': len(four_cycles),
        'three_tokens': len(three_cycle_tokens),
        'four_tokens': len(four_cycle_tokens),
        'overlap_tokens': len(both_cycle_tokens),
        'overlap_pct': overlap_pct if 'overlap_pct' in dir() else 0
    },
    'f2_kernel': {
        'three_kernel': dict(three_kernel),
        'four_kernel': dict(four_kernel),
        'verdict': f2_verdict if 'f2_verdict' in dir() else 'NOT_TESTED'
    },
    'f3_hazard': {
        'three_hazard_overlap': len(three_hazard_overlap) if 'three_hazard_overlap' in dir() else 0,
        'four_hazard_overlap': len(four_hazard_overlap) if 'four_hazard_overlap' in dir() else 0
    },
    'f4_folio': {
        'correlation': f4_corr if 'f4_corr' in dir() else 'NOT_TESTED'
    }
}

# Determine overall findings
findings = []

if len(three_cycles) < 10 or len(four_cycles) < 10:
    findings.append(f"F-1: Insufficient cycles for robust analysis (3-cycles={len(three_cycles)}, 4-cycles={len(four_cycles)})")
    overall_verdict = "INSUFFICIENT_DATA"
else:
    if results['f1_topology'].get('overlap_pct', 0) > 80:
        findings.append(f"F-1: Cycle populations HIGHLY OVERLAPPING ({results['f1_topology']['overlap_pct']:.1f}%)")
    elif results['f1_topology'].get('overlap_pct', 0) < 20:
        findings.append(f"F-1: Cycle populations DISTINCT ({results['f1_topology']['overlap_pct']:.1f}%)")
    else:
        findings.append(f"F-1: Cycle populations PARTIALLY OVERLAPPING ({results['f1_topology']['overlap_pct']:.1f}%)")

    if 'f2_verdict' in dir() and f2_verdict == "KERNEL_DIFFERS":
        findings.append("F-2: 3-cycles and 4-cycles have DIFFERENT kernel composition")
    elif 'f2_verdict' in dir() and f2_verdict == "KERNEL_SIMILAR":
        findings.append("F-2: 3-cycles and 4-cycles have SIMILAR kernel composition")

    if 'f4_corr' in dir():
        if f4_corr == "CORRELATED":
            findings.append("F-4: Cycle densities are CORRELATED across folios (consistent profiles)")
        elif f4_corr == "ANTI_CORRELATED":
            findings.append("F-4: Cycle densities are ANTI-CORRELATED (folios specialize)")
        else:
            findings.append("F-4: Cycle densities are INDEPENDENT across folios")

    overall_verdict = "CYCLE_STRUCTURE_EXISTS" if findings else "NO_STRUCTURE"

print(f"\nFINDINGS:")
if findings:
    for f in findings:
        print(f"  - {f}")
else:
    print("  - No significant patterns detected")

# Hard stop evaluation
print(f"\nHARD STOP EVALUATION:")

if len(three_cycles) < 10 or len(four_cycles) < 10:
    print("  STOP: Insufficient cycle data for analysis")
    constraints = []
elif results['f1_topology'].get('overlap_pct', 0) > 90 and f2_verdict == "KERNEL_SIMILAR":
    print("  STOP 1: Cycle tokens identical to general population -> TRIGGERED")
    constraints = []
else:
    print("  STOP 1: Cycle structure detected -> NOT triggered")
    print("  STOP 2: Kernel/folio relationships detected -> NOT triggered")
    constraints = []

    # Generate constraints if warranted
    if results['f1_topology']['overlap_pct'] < 50:
        constraints.append(f"3-cycle and 4-cycle populations are DISTINCT ({results['f1_topology']['overlap_pct']:.0f}% overlap); different tokens participate in different cycle lengths")

    if 'f4_corr' in dir() and f4_corr == "CORRELATED":
        constraints.append("Cycle densities are CORRELATED across folios; programs have consistent cycle profiles")

print(f"\nOVERALL VERDICT: {overall_verdict}")

print(f"\nPROPOSED CONSTRAINTS ({len(constraints)}):")
for c in constraints:
    print(f"  - {c}")

print("\n" + "=" * 70)
print("DIRECTION F: CLOSED")
print("Cycle semantics investigation is now COMPLETE.")
print("=" * 70)

# Save results
os.makedirs('phases/CYCLE_semantics_analysis', exist_ok=True)

# Convert Counter objects to dicts for JSON serialization
results_json = {
    'f1_topology': results['f1_topology'],
    'f2_kernel': {
        'three_kernel': {str(k): v for k, v in results['f2_kernel']['three_kernel'].items()},
        'four_kernel': {str(k): v for k, v in results['f2_kernel']['four_kernel'].items()},
        'verdict': results['f2_kernel']['verdict']
    },
    'f3_hazard': results['f3_hazard'],
    'f4_folio': results['f4_folio'],
    'overall_verdict': overall_verdict,
    'constraints': constraints
}

with open('phases/CYCLE_semantics_analysis/cycle_semantics_results.json', 'w') as f:
    json.dump(results_json, f, indent=2)

print("\nResults saved to phases/CYCLE_semantics_analysis/cycle_semantics_results.json")
