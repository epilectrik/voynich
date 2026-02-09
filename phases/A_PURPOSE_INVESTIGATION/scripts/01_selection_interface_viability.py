"""
01_selection_interface_viability.py - Test if A is a selection interface for B

Hypothesis H4b: A is a selection interface. Operators consult A to find
constraint profiles that filter B to viable procedure subsets.

Test: Do A-filtered B subsets preserve operational completeness?

If A is functional as a selection interface:
- Filtered B should retain core kernel operators (k, h, e)
- Filtered B should have viable state transitions
- Different A folios should produce meaningfully different B subsets
"""

import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import numpy as np

tx = Transcript()
morph = Morphology()

# Get all tokens
a_tokens = list(tx.currier_a())
b_tokens = list(tx.currier_b())

print(f"Currier A tokens: {len(a_tokens)}")
print(f"Currier B tokens: {len(b_tokens)}")

# ============================================================
# Build A folio vocabulary profiles
# ============================================================
print("\n" + "="*70)
print("BUILDING A FOLIO VOCABULARY PROFILES")
print("="*70)

a_folio_vocab = defaultdict(set)  # folio -> set of MIDDLEs
a_folio_pp = defaultdict(set)     # folio -> PP MIDDLEs only

for t in a_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        a_folio_vocab[t.folio].add(m.middle)
        # All A MIDDLEs are potentially PP (shared vocabulary)
        a_folio_pp[t.folio].add(m.middle)

print(f"A folios with vocabulary: {len(a_folio_vocab)}")
print(f"Mean MIDDLEs per A folio: {np.mean([len(v) for v in a_folio_vocab.values()]):.1f}")

# ============================================================
# Build B baseline vocabulary
# ============================================================
print("\n" + "="*70)
print("BUILDING B BASELINE VOCABULARY")
print("="*70)

b_all_middles = set()
b_folio_vocab = defaultdict(set)

for t in b_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        b_all_middles.add(m.middle)
        b_folio_vocab[t.folio].add(m.middle)

print(f"Total unique B MIDDLEs: {len(b_all_middles)}")
print(f"B folios: {len(b_folio_vocab)}")

# Define kernel operators
KERNEL_MIDDLES = {'k', 'h', 'e'}
kernel_in_b = KERNEL_MIDDLES & b_all_middles
print(f"Kernel MIDDLEs in B: {kernel_in_b}")

# ============================================================
# Test A folio filtering
# ============================================================
print("\n" + "="*70)
print("TESTING A FOLIO FILTERING ON B")
print("="*70)

results = []

for a_folio in sorted(a_folio_pp.keys()):
    a_vocab = a_folio_pp[a_folio]

    # Filter B to only MIDDLEs present in this A folio
    filtered_b = b_all_middles & a_vocab

    # Compute metrics
    coverage = len(filtered_b) / len(b_all_middles) if b_all_middles else 0
    kernel_retained = KERNEL_MIDDLES & filtered_b
    kernel_coverage = len(kernel_retained) / len(KERNEL_MIDDLES)

    results.append({
        'a_folio': a_folio,
        'a_vocab_size': len(a_vocab),
        'filtered_b_size': len(filtered_b),
        'b_coverage': coverage,
        'kernel_retained': list(kernel_retained),
        'kernel_coverage': kernel_coverage
    })

# Summary statistics
coverages = [r['b_coverage'] for r in results]
kernel_coverages = [r['kernel_coverage'] for r in results]

print(f"\nA folios tested: {len(results)}")
print(f"\nB coverage when filtered by single A folio:")
print(f"  Min: {min(coverages):.1%}")
print(f"  Max: {max(coverages):.1%}")
print(f"  Mean: {np.mean(coverages):.1%}")
print(f"  Median: {np.median(coverages):.1%}")

print(f"\nKernel coverage (k, h, e retained):")
print(f"  Full kernel (100%): {sum(1 for k in kernel_coverages if k == 1.0)} folios")
print(f"  Partial kernel: {sum(1 for k in kernel_coverages if 0 < k < 1.0)} folios")
print(f"  No kernel (0%): {sum(1 for k in kernel_coverages if k == 0)} folios")

# ============================================================
# Test aggregated A filtering (folio-level)
# ============================================================
print("\n" + "="*70)
print("AGGREGATED A FILTERING (CUMULATIVE)")
print("="*70)

# Sort A folios and accumulate vocabulary
a_folios_sorted = sorted(a_folio_pp.keys())
cumulative_vocab = set()
cumulative_results = []

for i, a_folio in enumerate(a_folios_sorted):
    cumulative_vocab |= a_folio_pp[a_folio]
    filtered_b = b_all_middles & cumulative_vocab
    coverage = len(filtered_b) / len(b_all_middles)
    kernel_coverage = len(KERNEL_MIDDLES & filtered_b) / len(KERNEL_MIDDLES)

    cumulative_results.append({
        'folios_included': i + 1,
        'cumulative_vocab': len(cumulative_vocab),
        'filtered_b_size': len(filtered_b),
        'b_coverage': coverage,
        'kernel_coverage': kernel_coverage
    })

print(f"\nCumulative coverage progression:")
checkpoints = [1, 5, 10, 20, 50, len(cumulative_results)]
for cp in checkpoints:
    if cp <= len(cumulative_results):
        r = cumulative_results[cp-1]
        print(f"  {r['folios_included']:3d} A folios: {r['b_coverage']:.1%} B coverage, {r['kernel_coverage']:.0%} kernel")

# ============================================================
# Test filter uniqueness (different A -> different B subsets?)
# ============================================================
print("\n" + "="*70)
print("FILTER UNIQUENESS ANALYSIS")
print("="*70)

# Compute filtered B sets for each A folio
filter_signatures = {}
for a_folio in a_folio_pp:
    filtered = frozenset(b_all_middles & a_folio_pp[a_folio])
    filter_signatures[a_folio] = filtered

# Count unique signatures
unique_signatures = set(filter_signatures.values())
print(f"A folios: {len(filter_signatures)}")
print(f"Unique B filter signatures: {len(unique_signatures)}")
print(f"Uniqueness rate: {len(unique_signatures)/len(filter_signatures):.1%}")

# Pairwise Jaccard similarity between A folio filters
jaccards = []
a_folio_list = list(filter_signatures.keys())
for i in range(len(a_folio_list)):
    for j in range(i+1, len(a_folio_list)):
        s1 = filter_signatures[a_folio_list[i]]
        s2 = filter_signatures[a_folio_list[j]]
        if s1 or s2:
            jaccard = len(s1 & s2) / len(s1 | s2) if (s1 | s2) else 0
            jaccards.append(jaccard)

print(f"\nPairwise Jaccard similarity between A folio filters:")
print(f"  Min: {min(jaccards):.3f}")
print(f"  Max: {max(jaccards):.3f}")
print(f"  Mean: {np.mean(jaccards):.3f}")
print(f"  Median: {np.median(jaccards):.3f}")

# ============================================================
# Operational viability check
# ============================================================
print("\n" + "="*70)
print("OPERATIONAL VIABILITY OF FILTERED B")
print("="*70)

# For a filtered B to be "operationally viable", it should have:
# 1. At least one kernel operator
# 2. Sufficient vocabulary diversity

viable_folios = []
for r in results:
    has_kernel = r['kernel_coverage'] > 0
    has_diversity = r['filtered_b_size'] >= 10  # arbitrary threshold

    if has_kernel and has_diversity:
        viable_folios.append(r['a_folio'])

print(f"A folios producing viable B filters:")
print(f"  Has kernel (any of k,h,e): {sum(1 for r in results if r['kernel_coverage'] > 0)}")
print(f"  Has diversity (10+ MIDDLEs): {sum(1 for r in results if r['filtered_b_size'] >= 10)}")
print(f"  Both (viable): {len(viable_folios)} ({len(viable_folios)/len(results):.1%})")

# ============================================================
# Summary
# ============================================================
print("\n" + "="*70)
print("SUMMARY: SELECTION INTERFACE HYPOTHESIS")
print("="*70)

mean_coverage = np.mean(coverages)
mean_kernel = np.mean(kernel_coverages)
uniqueness = len(unique_signatures)/len(filter_signatures)
viability = len(viable_folios)/len(results)

print(f"""
Single A folio filtering:
  Mean B coverage: {mean_coverage:.1%}
  Mean kernel retention: {mean_kernel:.1%}
  Filter uniqueness: {uniqueness:.1%}
  Viability rate: {viability:.1%}

Interpretation:
""")

if mean_coverage > 0.3 and mean_kernel > 0.5 and viability > 0.5:
    verdict = "SUPPORTS"
    print("  SUPPORTS selection interface hypothesis")
    print("  - A folios produce operationally viable B filters")
    print("  - Kernel operators largely retained")
    print("  - Different A folios select different B subsets")
elif mean_coverage < 0.1 or mean_kernel < 0.3:
    verdict = "CONTRADICTS"
    print("  CONTRADICTS selection interface hypothesis")
    print("  - Filtered B is too impoverished for operation")
    print("  - Core kernel lost in filtering")
else:
    verdict = "INCONCLUSIVE"
    print("  INCONCLUSIVE")
    print("  - Partial operational capability retained")
    print("  - May require multiple A records for viable selection")

# Save results
output = {
    'single_folio_results': results,
    'cumulative_results': cumulative_results,
    'summary': {
        'mean_b_coverage': float(mean_coverage),
        'mean_kernel_retention': float(mean_kernel),
        'filter_uniqueness': float(uniqueness),
        'viability_rate': float(viability),
        'pairwise_jaccard_mean': float(np.mean(jaccards)),
        'verdict': verdict
    }
}

with open('C:/git/voynich/phases/A_PURPOSE_INVESTIGATION/results/selection_interface_viability.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to selection_interface_viability.json")
