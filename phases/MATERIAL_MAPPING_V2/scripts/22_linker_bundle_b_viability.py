"""
22_linker_bundle_b_viability.py

TEST: Do linker-aggregated A bundles have better B correspondence than individual records?

Hypothesis:
- Individual A records → ~20% B viability (established)
- Linker-aggregated bundles → higher B viability?

Method:
1. Identify aggregated bundles from C835 (linked A folios)
2. Pool PP vocabulary from linked folios
3. Test B viability with pooled vocabulary
4. Compare to individual folio viability
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

print("="*70)
print("LINKER-AGGREGATED BUNDLE B VIABILITY TEST")
print("="*70)

tx = Transcript()
morph = Morphology()

# =============================================================
# STEP 1: Define the linker bundles from C835
# =============================================================
print("\nSTEP 1: Defining linker bundles from C835...")

# From C835: Linkers create convergent topology
# Format: collector_folio -> [source_folios]
linker_bundles = {
    'f93v': ['f21r', 'f53v', 'f54r', 'f87r', 'f89v1'],  # cthody links
    'f32r': ['f27r', 'f30v', 'f42r', 'f93r'],           # ctho links
    'f87r': ['f53v', 'f87r'],                            # ctheody links (self-loop)
    'f37v': ['f89v1'],                                   # qokoiiin links
}

print("\nLinker bundles:")
for collector, sources in linker_bundles.items():
    print(f"  {collector} <- {sources}")

# =============================================================
# STEP 2: Build vocabulary sets
# =============================================================
print("\n" + "="*70)
print("STEP 2: Building vocabulary sets...")

# Get A folio vocabulary (MIDDLEs)
a_folio_vocab = defaultdict(set)
a_folio_tokens = defaultdict(list)

for t in tx.currier_a():
    if not t.word or '*' in t.word:
        continue
    try:
        m = morph.extract(t.word)
        if m.middle:
            a_folio_vocab[t.folio].add(m.middle)
            a_folio_tokens[t.folio].append(t.word)
    except:
        pass

# Get B folio vocabulary (MIDDLEs)
b_folio_vocab = defaultdict(set)

for t in tx.currier_b():
    if not t.word or '*' in t.word:
        continue
    try:
        m = morph.extract(t.word)
        if m.middle:
            b_folio_vocab[t.folio].add(m.middle)
    except:
        pass

a_folios = sorted(a_folio_vocab.keys())
b_folios = sorted(b_folio_vocab.keys())

print(f"A folios with vocabulary: {len(a_folios)}")
print(f"B folios with vocabulary: {len(b_folios)}")

# =============================================================
# STEP 3: Compute B coverage for individual A folios
# =============================================================
print("\n" + "="*70)
print("STEP 3: Individual A folio B coverage...")

def b_coverage(a_vocab, b_vocab):
    """What fraction of B vocabulary is covered by A?"""
    if not b_vocab:
        return 0
    return len(a_vocab & b_vocab) / len(b_vocab)

def mean_b_coverage(a_vocab):
    """Mean coverage across all B folios"""
    coverages = [b_coverage(a_vocab, b_folio_vocab[bf]) for bf in b_folios]
    return sum(coverages) / len(coverages) if coverages else 0

# Individual folio coverages
individual_coverages = {}
for af in a_folios:
    individual_coverages[af] = mean_b_coverage(a_folio_vocab[af])

mean_individual = sum(individual_coverages.values()) / len(individual_coverages)
print(f"\nMean B coverage for individual A folios: {mean_individual:.3f}")

# Show some examples
print("\nIndividual A folio coverages (sample):")
sorted_indiv = sorted(individual_coverages.items(), key=lambda x: -x[1])
for af, cov in sorted_indiv[:5]:
    print(f"  {af}: {cov:.3f} ({len(a_folio_vocab[af])} MIDDLEs)")

# =============================================================
# STEP 4: Compute B coverage for linker bundles
# =============================================================
print("\n" + "="*70)
print("STEP 4: Linker bundle B coverage...")

bundle_results = {}

for collector, sources in linker_bundles.items():
    # Pool vocabulary from all source folios + collector
    all_folios = sources + [collector]
    pooled_vocab = set()

    for af in all_folios:
        if af in a_folio_vocab:
            pooled_vocab.update(a_folio_vocab[af])

    # Compute coverage
    bundle_coverage = mean_b_coverage(pooled_vocab)

    # Individual coverage of collector alone
    collector_coverage = individual_coverages.get(collector, 0)

    # Improvement
    improvement = bundle_coverage / collector_coverage if collector_coverage > 0 else 0

    bundle_results[collector] = {
        'sources': sources,
        'n_folios': len(all_folios),
        'pooled_middles': len(pooled_vocab),
        'bundle_coverage': bundle_coverage,
        'collector_coverage': collector_coverage,
        'improvement': improvement
    }

    print(f"\n{collector} bundle:")
    print(f"  Sources: {sources}")
    print(f"  Pooled MIDDLEs: {len(pooled_vocab)}")
    print(f"  Bundle coverage: {bundle_coverage:.3f}")
    print(f"  Collector alone: {collector_coverage:.3f}")
    print(f"  Improvement: {improvement:.2f}x")

# =============================================================
# STEP 5: Compare to random aggregation (null model)
# =============================================================
print("\n" + "="*70)
print("STEP 5: Null model - random aggregation...")

import random

# For each bundle size, what's the expected coverage from random folio selection?
null_results = {}

for collector, result in bundle_results.items():
    n_folios = result['n_folios']

    # Sample random bundles of same size
    random_coverages = []
    for _ in range(500):
        random_folios = random.sample(a_folios, min(n_folios, len(a_folios)))
        pooled = set()
        for af in random_folios:
            pooled.update(a_folio_vocab[af])
        random_coverages.append(mean_b_coverage(pooled))

    mean_random = sum(random_coverages) / len(random_coverages)

    # How does the actual bundle compare?
    actual = result['bundle_coverage']
    p_value = sum(1 for r in random_coverages if r >= actual) / len(random_coverages)

    null_results[collector] = {
        'actual': actual,
        'random_mean': mean_random,
        'lift': actual / mean_random if mean_random > 0 else 0,
        'p_value': p_value
    }

    print(f"\n{collector} bundle ({n_folios} folios):")
    print(f"  Actual coverage: {actual:.3f}")
    print(f"  Random mean: {mean_random:.3f}")
    print(f"  Lift: {actual/mean_random:.2f}x")
    print(f"  p-value: {p_value:.3f}")

# =============================================================
# STEP 6: Test specific B folio matching
# =============================================================
print("\n" + "="*70)
print("STEP 6: Do linker bundles match specific B folios better?")

# For each bundle, find best-matching B folios
for collector, result in bundle_results.items():
    sources = result['sources']
    all_folios = sources + [collector]

    pooled_vocab = set()
    for af in all_folios:
        if af in a_folio_vocab:
            pooled_vocab.update(a_folio_vocab[af])

    # Score each B folio
    b_scores = []
    for bf in b_folios:
        cov = b_coverage(pooled_vocab, b_folio_vocab[bf])
        b_scores.append((bf, cov))

    b_scores.sort(key=lambda x: -x[1])

    print(f"\n{collector} bundle best B matches:")
    for bf, cov in b_scores[:5]:
        print(f"  {bf}: {cov:.3f} coverage")

# =============================================================
# STEP 7: Compare bundle vs individual for same collector
# =============================================================
print("\n" + "="*70)
print("STEP 7: Bundle improvement analysis")

print("\nSummary: Does aggregation via linkers improve B correspondence?")
print()
print(f"{'Collector':<10} {'Individual':<12} {'Bundle':<12} {'Improvement':<12} {'vs Random':<12}")
print("-" * 58)

improvements = []
for collector, result in bundle_results.items():
    indiv = result['collector_coverage']
    bundle = result['bundle_coverage']
    improve = result['improvement']
    lift = null_results[collector]['lift']
    improvements.append(improve)

    print(f"{collector:<10} {indiv:<12.3f} {bundle:<12.3f} {improve:<12.2f}x {lift:<12.2f}x")

mean_improvement = sum(improvements) / len(improvements)

# =============================================================
# SUMMARY
# =============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
QUESTION: Do linker-aggregated A bundles have better B correspondence?

RESULTS:

1. Mean individual A folio B coverage: {mean_individual:.3f}

2. Linker bundle improvements:
""")

for collector, result in bundle_results.items():
    null = null_results[collector]
    print(f"   {collector}: {result['collector_coverage']:.3f} -> {result['bundle_coverage']:.3f} ({result['improvement']:.2f}x)")
    print(f"           vs random {null['random_mean']:.3f} (lift {null['lift']:.2f}x, p={null['p_value']:.3f})")

print(f"""
3. Mean improvement from aggregation: {mean_improvement:.2f}x

INTERPRETATION:
""")

if mean_improvement > 1.5:
    print("Linker aggregation SIGNIFICANTLY improves B coverage.")
    print("The linker network creates structured bundles with better B correspondence.")
else:
    print("Linker aggregation provides MODEST improvement.")

# Check if better than random
lifts = [null_results[c]['lift'] for c in bundle_results]
mean_lift = sum(lifts) / len(lifts)

if mean_lift > 1.1:
    print(f"Bundles are {mean_lift:.2f}x better than random aggregation of same size.")
    print("The linking structure is MEANINGFUL, not just pool-size effect.")
else:
    print(f"Bundles are only {mean_lift:.2f}x vs random (same size).")
    print("Improvement is mostly pool-size effect, not linker specificity.")
