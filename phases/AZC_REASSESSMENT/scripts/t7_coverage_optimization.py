"""
T7: Coverage Optimization Test

Hypothesis: A folio homogeneity serves coverage optimization (C476).
A folios are deliberately similar to maximize total vocabulary availability,
not discriminative targeting.

Tests:
1. Do A folios overlap more than random expectation?
2. Does adding A folios follow diminishing returns (greedy coverage)?
3. Is the overlap pattern consistent with coverage maximization?
"""

import sys, json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
rng = np.random.RandomState(42)

print("=== T7: COVERAGE OPTIMIZATION TEST ===\n")

# Build A folio MIDDLE inventories
print("Building A folio data...")
a_folio_middles = {}
a_folio_section = {}

for t in tx.currier_a():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if t.folio not in a_folio_middles:
        a_folio_middles[t.folio] = set()
        a_folio_section[t.folio] = t.section
    if m.middle:
        a_folio_middles[t.folio].add(m.middle)

a_folios = sorted(a_folio_middles.keys())
print(f"  {len(a_folios)} A folios")

# Get all unique MIDDLEs across A
all_a_middles = set()
for fol in a_folios:
    all_a_middles.update(a_folio_middles[fol])
print(f"  {len(all_a_middles)} unique MIDDLEs in A")

# Get B MIDDLEs for PP identification
b_middles = set()
for t in tx.currier_b():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_middles.add(m.middle)

pp_middles = all_a_middles & b_middles
print(f"  {len(pp_middles)} PP MIDDLEs (shared A-B)")

# ============================================================
# Test 1: Pairwise overlap analysis
# ============================================================
print("\n=== TEST 1: PAIRWISE OVERLAP ANALYSIS ===\n")

# Compute pairwise Jaccard similarities
n = len(a_folios)
jaccard_matrix = np.zeros((n, n))
overlap_matrix = np.zeros((n, n))

for i in range(n):
    for j in range(n):
        set_i = a_folio_middles[a_folios[i]]
        set_j = a_folio_middles[a_folios[j]]
        intersection = len(set_i & set_j)
        union = len(set_i | set_j)
        jaccard_matrix[i, j] = intersection / union if union > 0 else 0
        overlap_matrix[i, j] = intersection

# Get upper triangle (exclude diagonal)
upper_idx = np.triu_indices(n, k=1)
real_jaccards = jaccard_matrix[upper_idx]
real_overlaps = overlap_matrix[upper_idx]

print(f"Real A folio pairwise Jaccard:")
print(f"  Mean: {real_jaccards.mean():.4f}")
print(f"  Median: {np.median(real_jaccards):.4f}")
print(f"  Std: {real_jaccards.std():.4f}")
print(f"  Min: {real_jaccards.min():.4f}")
print(f"  Max: {real_jaccards.max():.4f}")

# Compare to random: generate synthetic A folios with same size distribution
print("\nGenerating synthetic A folios for comparison...")
pool_sizes = [len(a_folio_middles[f]) for f in a_folios]
all_middles_list = list(all_a_middles)

n_trials = 100
synthetic_mean_jaccards = []

for trial in range(n_trials):
    # Generate synthetic folios
    synthetic_folios = []
    for size in pool_sizes:
        sampled = set(rng.choice(all_middles_list, size=min(size, len(all_middles_list)), replace=False))
        synthetic_folios.append(sampled)

    # Compute pairwise Jaccard
    synth_jaccards = []
    for i in range(n):
        for j in range(i+1, n):
            set_i = synthetic_folios[i]
            set_j = synthetic_folios[j]
            intersection = len(set_i & set_j)
            union = len(set_i | set_j)
            jac = intersection / union if union > 0 else 0
            synth_jaccards.append(jac)

    synthetic_mean_jaccards.append(np.mean(synth_jaccards))

synthetic_mean_jaccards = np.array(synthetic_mean_jaccards)

print(f"\nSynthetic A folio pairwise Jaccard (mean of {n_trials} trials):")
print(f"  Mean: {synthetic_mean_jaccards.mean():.4f}")
print(f"  Std: {synthetic_mean_jaccards.std():.4f}")
print(f"  5th percentile: {np.percentile(synthetic_mean_jaccards, 5):.4f}")
print(f"  95th percentile: {np.percentile(synthetic_mean_jaccards, 95):.4f}")

real_mean_jaccard = real_jaccards.mean()
percentile_real = stats.percentileofscore(synthetic_mean_jaccards, real_mean_jaccard)
z_score = (real_mean_jaccard - synthetic_mean_jaccards.mean()) / synthetic_mean_jaccards.std()

print(f"\nComparison:")
print(f"  Real mean Jaccard: {real_mean_jaccard:.4f}")
print(f"  Percentile in synthetic: {percentile_real:.1f}%")
print(f"  z-score: {z_score:.2f}")

if percentile_real > 95:
    overlap_verdict = "HIGHER_THAN_RANDOM"
    overlap_explanation = f"Real overlap ({real_mean_jaccard:.3f}) > 95th percentile: A folios are MORE similar than random"
elif percentile_real < 5:
    overlap_verdict = "LOWER_THAN_RANDOM"
    overlap_explanation = f"Real overlap ({real_mean_jaccard:.3f}) < 5th percentile: A folios are LESS similar than random"
else:
    overlap_verdict = "SIMILAR_TO_RANDOM"
    overlap_explanation = f"Real overlap at {percentile_real:.0f}th percentile: indistinguishable from random"

print(f"\nVerdict: {overlap_verdict}")
print(f"  {overlap_explanation}")

# ============================================================
# Test 2: Cumulative coverage curve (greedy addition)
# ============================================================
print("\n=== TEST 2: CUMULATIVE COVERAGE CURVE ===\n")

# Add A folios one by one (by pool size, largest first) and track cumulative coverage
sorted_by_size = sorted(a_folios, key=lambda f: len(a_folio_middles[f]), reverse=True)

cumulative_coverage = []
current_union = set()
for fol in sorted_by_size:
    current_union = current_union | a_folio_middles[fol]
    cumulative_coverage.append(len(current_union))

# Also compute for PP-only
cumulative_pp_coverage = []
current_pp_union = set()
for fol in sorted_by_size:
    fol_pp = a_folio_middles[fol] & pp_middles
    current_pp_union = current_pp_union | fol_pp
    cumulative_pp_coverage.append(len(current_pp_union))

print(f"Cumulative coverage (largest-first addition):")
print(f"  After 1 folio: {cumulative_coverage[0]} MIDDLEs ({cumulative_pp_coverage[0]} PP)")
print(f"  After 5 folios: {cumulative_coverage[4]} MIDDLEs ({cumulative_pp_coverage[4]} PP)")
print(f"  After 10 folios: {cumulative_coverage[9]} MIDDLEs ({cumulative_pp_coverage[9]} PP)")
print(f"  After 20 folios: {cumulative_coverage[19]} MIDDLEs ({cumulative_pp_coverage[19]} PP)")
print(f"  After 50 folios: {cumulative_coverage[49]} MIDDLEs ({cumulative_pp_coverage[49]} PP)")
print(f"  After all {len(a_folios)} folios: {cumulative_coverage[-1]} MIDDLEs ({cumulative_pp_coverage[-1]} PP)")

# Compute marginal gain at each step
marginal_gains = [cumulative_coverage[0]] + [cumulative_coverage[i] - cumulative_coverage[i-1] for i in range(1, len(cumulative_coverage))]

print(f"\nMarginal gains (new MIDDLEs per added folio):")
print(f"  First 5: {marginal_gains[:5]}")
print(f"  Folios 10-14: {marginal_gains[9:14]}")
print(f"  Folios 50-54: {marginal_gains[49:54]}")
print(f"  Last 5: {marginal_gains[-5:]}")

# What fraction of coverage is achieved by first N folios?
total_middles = cumulative_coverage[-1]
print(f"\nCoverage saturation:")
print(f"  First 10 folios cover: {cumulative_coverage[9]/total_middles*100:.1f}% of all A MIDDLEs")
print(f"  First 20 folios cover: {cumulative_coverage[19]/total_middles*100:.1f}%")
print(f"  First 50 folios cover: {cumulative_coverage[49]/total_middles*100:.1f}%")

# For PP specifically
total_pp = cumulative_pp_coverage[-1]
print(f"\n  First 10 folios cover: {cumulative_pp_coverage[9]/total_pp*100:.1f}% of all PP MIDDLEs")
print(f"  First 20 folios cover: {cumulative_pp_coverage[19]/total_pp*100:.1f}%")
print(f"  First 50 folios cover: {cumulative_pp_coverage[49]/total_pp*100:.1f}%")

# ============================================================
# Test 3: Hub structure analysis
# ============================================================
print("\n=== TEST 3: HUB STRUCTURE ANALYSIS ===\n")

# How many MIDDLEs appear in many folios (hubs)?
middle_folio_counts = Counter()
for fol in a_folios:
    for mid in a_folio_middles[fol]:
        middle_folio_counts[mid] += 1

# Distribution of folio counts per MIDDLE
count_dist = Counter(middle_folio_counts.values())

print(f"MIDDLE frequency distribution (how many folios contain each MIDDLE):")
for count in sorted(count_dist.keys())[:10]:
    print(f"  In {count} folios: {count_dist[count]} MIDDLEs")
if max(count_dist.keys()) > 10:
    print(f"  ...")
    for count in sorted(count_dist.keys())[-3:]:
        print(f"  In {count} folios: {count_dist[count]} MIDDLEs")

# What fraction of MIDDLEs are "hubs" (appear in >50% of folios)?
hub_threshold = len(a_folios) // 2
hub_middles = [mid for mid, count in middle_folio_counts.items() if count >= hub_threshold]
print(f"\nHub MIDDLEs (in >= {hub_threshold} folios): {len(hub_middles)} ({len(hub_middles)/len(all_a_middles)*100:.1f}%)")

# Are hub MIDDLEs preferentially PP?
hub_pp = [mid for mid in hub_middles if mid in pp_middles]
print(f"  Of which are PP: {len(hub_pp)} ({len(hub_pp)/len(hub_middles)*100:.1f}% of hubs)")

# Expected if random?
expected_pp_rate = len(pp_middles) / len(all_a_middles)
print(f"  Expected PP rate (null): {expected_pp_rate*100:.1f}%")

# Binomial test
from scipy.stats import binomtest
if len(hub_middles) > 0:
    binom_result = binomtest(len(hub_pp), len(hub_middles), expected_pp_rate, alternative='greater')
    print(f"  Binomial test (hubs preferentially PP): p = {binom_result.pvalue:.4f}")
    hub_pp_p = binom_result.pvalue
else:
    hub_pp_p = 1.0

# ============================================================
# Test 4: Coverage efficiency
# ============================================================
print("\n=== TEST 4: COVERAGE EFFICIENCY ===\n")

# If A folios were optimally designed for coverage, we'd expect:
# - High overlap on common (hub) MIDDLEs
# - Diversity on rare MIDDLEs to capture them all

# Compute: for rare MIDDLEs (in <5 folios), how many folios contain them?
rare_threshold = 5
rare_middles = [mid for mid, count in middle_folio_counts.items() if count < rare_threshold]
print(f"Rare MIDDLEs (in <{rare_threshold} folios): {len(rare_middles)}")

# What's the total coverage contribution of rare vs hub MIDDLEs?
rare_total_occurrences = sum(middle_folio_counts[mid] for mid in rare_middles)
hub_total_occurrences = sum(middle_folio_counts[mid] for mid in hub_middles)
all_total_occurrences = sum(middle_folio_counts.values())

print(f"\nOccurrence distribution:")
print(f"  Rare MIDDLEs: {rare_total_occurrences} occurrences ({rare_total_occurrences/all_total_occurrences*100:.1f}%)")
print(f"  Hub MIDDLEs: {hub_total_occurrences} occurrences ({hub_total_occurrences/all_total_occurrences*100:.1f}%)")

# Coverage efficiency: how quickly does the union grow vs raw token count?
# If optimized: union grows fast initially, then saturates
# If random: union grows proportionally to added tokens

raw_token_counts = [len(a_folio_middles[f]) for f in sorted_by_size]
cumulative_tokens = np.cumsum(raw_token_counts)

efficiency_curve = [cumulative_coverage[i] / cumulative_tokens[i] for i in range(len(cumulative_coverage))]

print(f"\nCoverage efficiency (union / cumulative tokens):")
print(f"  After 1 folio: {efficiency_curve[0]:.3f}")
print(f"  After 10 folios: {efficiency_curve[9]:.3f}")
print(f"  After 50 folios: {efficiency_curve[49]:.3f}")
print(f"  After all folios: {efficiency_curve[-1]:.3f}")

# ============================================================
# Summary
# ============================================================
print("\n=== SUMMARY ===\n")

# Verdict based on all tests
if percentile_real > 95:
    coverage_verdict = "COVERAGE_OPTIMIZED"
    coverage_explanation = "A folios show higher-than-random overlap, consistent with deliberate coverage optimization"
elif percentile_real > 50 and cumulative_pp_coverage[9]/total_pp > 0.8:
    coverage_verdict = "COVERAGE_SATURATED"
    coverage_explanation = "10 A folios cover >80% of PP vocabulary, consistent with redundant coverage design"
else:
    coverage_verdict = "NO_OPTIMIZATION_SIGNAL"
    coverage_explanation = "A folio overlap is indistinguishable from random"

print(f"Verdict: {coverage_verdict}")
print(f"  {coverage_explanation}")

# Key finding
print(f"\nKey finding:")
if cumulative_pp_coverage[9]/total_pp > 0.8:
    print(f"  The first 10 A folios (by size) cover {cumulative_pp_coverage[9]/total_pp*100:.1f}% of all PP vocabulary.")
    print(f"  The remaining 104 folios add only {100 - cumulative_pp_coverage[9]/total_pp*100:.1f}% more coverage.")
    print(f"  This is consistent with C476 (Coverage Optimality) - A folios maximize vocabulary availability.")

# Save results
results = {
    'test': 'T7_coverage_optimization',
    'pairwise_overlap': {
        'real_mean_jaccard': float(real_mean_jaccard),
        'synthetic_mean': float(synthetic_mean_jaccards.mean()),
        'synthetic_std': float(synthetic_mean_jaccards.std()),
        'percentile': float(percentile_real),
        'z_score': float(z_score),
        'verdict': overlap_verdict,
    },
    'cumulative_coverage': {
        'after_10': int(cumulative_coverage[9]),
        'after_20': int(cumulative_coverage[19]),
        'after_50': int(cumulative_coverage[49]),
        'total': int(cumulative_coverage[-1]),
        'pp_after_10': int(cumulative_pp_coverage[9]),
        'pp_total': int(cumulative_pp_coverage[-1]),
        'pp_saturation_at_10': float(cumulative_pp_coverage[9]/total_pp),
    },
    'hub_structure': {
        'hub_threshold': hub_threshold,
        'n_hub_middles': len(hub_middles),
        'hub_pp_rate': float(len(hub_pp)/len(hub_middles)) if hub_middles else 0,
        'expected_pp_rate': float(expected_pp_rate),
        'hub_pp_p': float(hub_pp_p),
    },
    'verdict': coverage_verdict,
    'explanation': coverage_explanation,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / 't7_coverage_optimization.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
