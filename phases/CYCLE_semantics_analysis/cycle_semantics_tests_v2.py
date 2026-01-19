#!/usr/bin/env python3
"""
DIRECTION F: CYCLE SEMANTICS ANALYSIS (v2 - Efficient)

Bounded analysis of 4-cycles vs 3-cycles in the kernel topology.
Uses efficient sampling approach rather than exhaustive search.

Tests:
F-1: Cycle topology characterization (what tokens form cycles?)
F-2: Cycle-kernel relationship (k, h, e composition?)
F-3: Cycle-folio distribution (program type correlation?)

STOP CONDITIONS:
- Insufficient cycle data
- No kernel relationship -> cycles incidental
- Max 2 Tier 2 constraints
"""

import os
import json
import numpy as np
from collections import Counter, defaultdict

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
        # Filter to PRIMARY transcriber (H) only
        if row.get('transcriber', '').strip() != 'H':
            continue
        all_tokens.append(row)

# Currier B only
b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']
b_words = [t.get('word', '') for t in b_tokens if t.get('word', '')]

print(f"Currier B tokens: {len(b_words)}")

# ==========================================================================
# BUILD TRANSITION GRAPH (CORE VOCABULARY ONLY)
# ==========================================================================

print("\nBuilding transition graph from core vocabulary...")

# Focus on top 200 tokens by frequency for efficient cycle detection
word_freq = Counter(b_words)
core_vocab = set(w for w, c in word_freq.most_common(200))

print(f"Core vocabulary: {len(core_vocab)} tokens")

# Build transitions within core vocab
transitions = defaultdict(set)  # adjacency list
transition_counts = Counter()

for i in range(len(b_words) - 1):
    w1 = b_words[i]
    w2 = b_words[i + 1]
    if w1 in core_vocab and w2 in core_vocab:
        transitions[w1].add(w2)
        transition_counts[(w1, w2)] += 1

print(f"Core transitions: {len(transition_counts)}")

# ==========================================================================
# F-1: EFFICIENT CYCLE DETECTION
# ==========================================================================

print("\n" + "=" * 70)
print("F-1: CYCLE DETECTION")
print("Question: What tokens form 3-cycles vs 4-cycles?")
print("=" * 70)

# Find 3-cycles: A -> B -> C -> A
three_cycles = set()
for a in core_vocab:
    for b in transitions[a]:
        if b == a:
            continue
        for c in transitions[b]:
            if c in [a, b]:
                continue
            if a in transitions[c]:  # C -> A completes the cycle
                cycle = tuple(sorted([a, b, c]))
                three_cycles.add(cycle)

print(f"\n3-cycles found: {len(three_cycles)}")

# Find 4-cycles: A -> B -> C -> D -> A
four_cycles = set()
for a in core_vocab:
    for b in transitions[a]:
        if b == a:
            continue
        for c in transitions[b]:
            if c in [a, b]:
                continue
            for d in transitions[c]:
                if d in [a, b, c]:
                    continue
                if a in transitions[d]:  # D -> A completes the cycle
                    cycle = tuple(sorted([a, b, c, d]))
                    four_cycles.add(cycle)

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
    all_cycle_tokens = three_cycle_tokens | four_cycle_tokens
    overlap_pct = 100 * len(both_cycle_tokens) / len(all_cycle_tokens) if all_cycle_tokens else 0
    print(f"Overlap percentage: {overlap_pct:.1f}%")
else:
    overlap_pct = 0

# Show some example cycles
if three_cycles:
    print(f"\nExample 3-cycles: {list(three_cycles)[:5]}")
if four_cycles:
    print(f"Example 4-cycles: {list(four_cycles)[:5]}")

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
core_kernel = Counter(get_kernel_class(t) for t in core_vocab)

print(f"\nKernel composition (% of tokens):")
print(f"{'Type':<15} {'k':<10} {'h':<10} {'e':<10} {'None':<10}")
print("-" * 55)

for label, counter, total_set in [
    ("3-cycles", three_kernel, three_cycle_tokens),
    ("4-cycles", four_kernel, four_cycle_tokens),
    ("Core vocab", core_kernel, core_vocab)
]:
    total = len(total_set) if total_set else 1
    k_pct = 100 * counter.get('k', 0) / total
    h_pct = 100 * counter.get('h', 0) / total
    e_pct = 100 * counter.get('e', 0) / total
    none_pct = 100 * counter.get(None, 0) / total
    print(f"{label:<15} {k_pct:.1f}%     {h_pct:.1f}%     {e_pct:.1f}%     {none_pct:.1f}%")

# Calculate kernel enrichment
def kernel_enrichment(cycle_kernel, baseline_kernel, cycle_set, baseline_set):
    """Calculate enrichment of kernel classes in cycles vs baseline."""
    results = {}
    for k in ['k', 'h', 'e', None]:
        cycle_pct = cycle_kernel.get(k, 0) / len(cycle_set) if cycle_set else 0
        baseline_pct = baseline_kernel.get(k, 0) / len(baseline_set) if baseline_set else 0
        ratio = cycle_pct / baseline_pct if baseline_pct > 0 else 0
        results[k] = ratio
    return results

if three_cycle_tokens:
    three_enrichment = kernel_enrichment(three_kernel, core_kernel, three_cycle_tokens, core_vocab)
    print(f"\n3-cycle kernel enrichment vs baseline:")
    for k, ratio in three_enrichment.items():
        status = "ENRICHED" if ratio > 1.5 else "DEPLETED" if ratio < 0.67 else "NORMAL"
        print(f"  {k}: {ratio:.2f}x ({status})")

if four_cycle_tokens:
    four_enrichment = kernel_enrichment(four_kernel, core_kernel, four_cycle_tokens, core_vocab)
    print(f"\n4-cycle kernel enrichment vs baseline:")
    for k, ratio in four_enrichment.items():
        status = "ENRICHED" if ratio > 1.5 else "DEPLETED" if ratio < 0.67 else "NORMAL"
        print(f"  {k}: {ratio:.2f}x ({status})")

# Determine verdict
f2_verdict = "NOT_TESTED"
if three_cycle_tokens and four_cycle_tokens:
    # Check if 3 and 4 cycles have different kernel profiles
    three_e_pct = three_kernel.get('e', 0) / len(three_cycle_tokens)
    four_e_pct = four_kernel.get('e', 0) / len(four_cycle_tokens)
    diff = abs(three_e_pct - four_e_pct)

    if diff > 0.1:  # More than 10% difference in 'e' composition
        f2_verdict = "KERNEL_DIFFERS"
        print(f"\nVERDICT: Kernel composition DIFFERS (e: {100*three_e_pct:.1f}% vs {100*four_e_pct:.1f}%)")
    else:
        f2_verdict = "KERNEL_SIMILAR"
        print(f"\nVERDICT: Kernel composition SIMILAR")

# ==========================================================================
# F-3: CYCLE-FOLIO DISTRIBUTION
# ==========================================================================

print("\n" + "=" * 70)
print("F-3: CYCLE-FOLIO DISTRIBUTION")
print("Question: Does cycle density vary by folio?")
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
folio_any_cycle_density = {}

for folio, words in folio_tokens.items():
    unique_words = set(words)
    if unique_words:
        three_in_folio = len(three_cycle_tokens & unique_words)
        four_in_folio = len(four_cycle_tokens & unique_words)
        any_cycle = len((three_cycle_tokens | four_cycle_tokens) & unique_words)

        folio_3cycle_density[folio] = three_in_folio / len(unique_words)
        folio_4cycle_density[folio] = four_in_folio / len(unique_words)
        folio_any_cycle_density[folio] = any_cycle / len(unique_words)

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
    from scipy.stats import spearmanr
    folios = list(folio_3cycle_density.keys())
    d3 = [folio_3cycle_density[f] for f in folios]
    d4 = [folio_4cycle_density[f] for f in folios]

    r, p = spearmanr(d3, d4)
    print(f"\nCorrelation between 3-cycle and 4-cycle density:")
    print(f"  Spearman r = {r:.3f}, p = {p:.6f}")

    if r > 0.5 and p < 0.05:
        print("  RESULT: Densities are CORRELATED (folios have consistent cycle profiles)")
        f3_corr = "CORRELATED"
    elif r < -0.5 and p < 0.05:
        print("  RESULT: Densities are ANTI-CORRELATED (folios specialize in cycle type)")
        f3_corr = "ANTI_CORRELATED"
    else:
        print("  RESULT: Densities are INDEPENDENT")
        f3_corr = "INDEPENDENT"
else:
    f3_corr = "NOT_TESTED"

# Variance analysis
print(f"\nFolio-level variance analysis:")
if densities_3 and densities_4:
    cv_3 = np.std(densities_3) / np.mean(densities_3) if np.mean(densities_3) > 0 else 0
    cv_4 = np.std(densities_4) / np.mean(densities_4) if np.mean(densities_4) > 0 else 0
    print(f"  3-cycle coefficient of variation: {cv_3:.2f}")
    print(f"  4-cycle coefficient of variation: {cv_4:.2f}")

    if cv_3 > 0.5 or cv_4 > 0.5:
        print("  RESULT: HIGH variance - folios differ substantially in cycle density")
        f3_variance = "HIGH"
    else:
        print("  RESULT: LOW variance - folios have similar cycle density")
        f3_variance = "LOW"
else:
    f3_variance = "NOT_TESTED"

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
        'overlap_pct': overlap_pct
    },
    'f2_kernel': {
        'verdict': f2_verdict,
        'three_kernel': dict(three_kernel),
        'four_kernel': dict(four_kernel)
    },
    'f3_folio': {
        'correlation': f3_corr,
        'variance': f3_variance,
        'mean_3': np.mean(densities_3) if densities_3 else 0,
        'mean_4': np.mean(densities_4) if densities_4 else 0
    }
}

# Determine findings
findings = []

if len(three_cycles) < 5:
    findings.append(f"F-1: Insufficient 3-cycles ({len(three_cycles)}) for robust analysis")

if overlap_pct > 80:
    findings.append(f"F-1: Cycle populations HIGHLY OVERLAPPING ({overlap_pct:.1f}%) - same tokens in both")
elif overlap_pct < 30:
    findings.append(f"F-1: Cycle populations DISTINCT ({overlap_pct:.1f}%) - different token sets")
else:
    findings.append(f"F-1: Cycle populations PARTIALLY OVERLAPPING ({overlap_pct:.1f}%)")

if f2_verdict == "KERNEL_DIFFERS":
    findings.append("F-2: 3-cycles and 4-cycles have DIFFERENT kernel composition")
elif f2_verdict == "KERNEL_SIMILAR":
    findings.append("F-2: 3-cycles and 4-cycles have SIMILAR kernel composition")

if f3_corr == "CORRELATED":
    findings.append("F-3: Cycle densities CORRELATED across folios")
elif f3_corr == "ANTI_CORRELATED":
    findings.append("F-3: Cycle densities ANTI-CORRELATED - folios specialize")

if f3_variance == "HIGH":
    findings.append("F-3: HIGH variance in cycle density across folios")

print(f"\nFINDINGS:")
for f in findings:
    print(f"  - {f}")

# Hard stop evaluation
print(f"\nHARD STOP EVALUATION:")

constraints = []

if len(three_cycles) < 5 or len(four_cycles) < 5:
    print("  STOP: Insufficient cycle data")
    overall_verdict = "INSUFFICIENT_DATA"
elif overlap_pct > 90 and f2_verdict == "KERNEL_SIMILAR":
    print("  STOP 1: Cycle populations identical, no kernel distinction -> TRIGGERED")
    overall_verdict = "NO_DISTINCTION"
else:
    print("  Structural distinctions found -> NOT stopped")
    overall_verdict = "STRUCTURE_EXISTS"

    if overlap_pct < 50:
        constraints.append(f"3-cycle and 4-cycle populations are DISTINCT ({overlap_pct:.0f}% overlap)")

    if f3_corr == "CORRELATED" or f3_variance == "HIGH":
        constraints.append(f"Cycle density varies by folio (CV={cv_3:.2f}/{cv_4:.2f}); programs have distinct cycle profiles")

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

results_json = {
    'f1_topology': results['f1_topology'],
    'f2_kernel': {
        'three_kernel': {str(k): v for k, v in results['f2_kernel']['three_kernel'].items()},
        'four_kernel': {str(k): v for k, v in results['f2_kernel']['four_kernel'].items()},
        'verdict': results['f2_kernel']['verdict']
    },
    'f3_folio': results['f3_folio'],
    'overall_verdict': overall_verdict,
    'constraints': constraints
}

with open('phases/CYCLE_semantics_analysis/cycle_semantics_results.json', 'w') as f:
    json.dump(results_json, f, indent=2)

print("\nResults saved to phases/CYCLE_semantics_analysis/cycle_semantics_results.json")
