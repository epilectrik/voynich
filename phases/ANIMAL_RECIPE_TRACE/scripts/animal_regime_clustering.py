"""
ANIMAL REGIME CLUSTERING (Phase 4)

Goal: Test if high animal-reception folios cluster in specific REGIMEs.
Hypothesis: Animal-receiving folios should cluster in REGIME_1/REGIME_2
(low-fire, careful control per Brunschwig animal procedure patterns).

Input: animal_folio_reception.json from Phase 3, regime_folio_mapping.json
Output: animal_regime_clustering.json
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from collections import Counter
import json
import numpy as np
from scipy import stats

print("=" * 70)
print("PHASE 4: ANIMAL REGIME CLUSTERING")
print("=" * 70)

# Load Phase 3 results
with open('phases/ANIMAL_RECIPE_TRACE/results/animal_folio_reception.json', 'r') as f:
    phase3 = json.load(f)

# Load REGIME mapping
with open('results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

# Invert mapping: folio -> REGIME
folio_to_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        folio_to_regime[folio] = regime

print(f"\nREGIME assignments loaded:")
for regime in sorted(regime_mapping.keys()):
    print(f"  {regime}: {len(regime_mapping[regime])} folios")

# Get high-reception folios from Phase 3
high_reception = phase3['high_reception_folios']
threshold = phase3['high_reception_threshold']

print(f"\nHigh-reception folios (threshold: {threshold:.3f}): {len(high_reception)}")

# Map to REGIMEs
print("\n" + "=" * 70)
print("HIGH-RECEPTION FOLIO REGIME DISTRIBUTION")
print("=" * 70)

high_reception_regimes = []
unassigned = []

for entry in high_reception:
    folio = entry['folio']
    if folio in folio_to_regime:
        high_reception_regimes.append(folio_to_regime[folio])
    else:
        unassigned.append(folio)

if unassigned:
    print(f"\nFolios without REGIME assignment: {unassigned}")

regime_counts = Counter(high_reception_regimes)

print(f"\nREGIME distribution of {len(high_reception_regimes)} high-reception folios:")
for regime in sorted(regime_counts.keys()):
    pct = 100 * regime_counts[regime] / len(high_reception_regimes)
    print(f"  {regime}: {regime_counts[regime]} ({pct:.1f}%)")

# Compare to baseline (all B folios with REGIME assignment)
print("\n" + "=" * 70)
print("BASELINE COMPARISON")
print("=" * 70)

all_folios = list(phase3['all_folios'].keys())
all_regimes = [folio_to_regime.get(f) for f in all_folios if f in folio_to_regime]
baseline_counts = Counter(all_regimes)

print(f"\nBaseline REGIME distribution ({len(all_regimes)} folios):")
for regime in sorted(baseline_counts.keys()):
    pct = 100 * baseline_counts[regime] / len(all_regimes)
    print(f"  {regime}: {baseline_counts[regime]} ({pct:.1f}%)")

# Chi-square test: Is the distribution of high-reception folios different from baseline?
print("\n" + "=" * 70)
print("STATISTICAL TESTS")
print("=" * 70)

# Compute expected counts for high-reception folios based on baseline proportions
regimes = sorted(set(all_regimes))
observed = [regime_counts.get(r, 0) for r in regimes]
expected_proportions = [baseline_counts.get(r, 0) / len(all_regimes) for r in regimes]
expected = [p * len(high_reception_regimes) for p in expected_proportions]

print(f"\nObserved vs Expected (high-reception folios):")
print(f"{'REGIME':<12} {'Observed':<10} {'Expected':<10} {'Ratio':<10}")
print("-" * 45)
for r, obs, exp in zip(regimes, observed, expected):
    ratio = obs / exp if exp > 0 else 0
    print(f"{r:<12} {obs:<10} {exp:.1f}       {ratio:.2f}x")

# Chi-square test
chi2, p_value = stats.chisquare(observed, expected)
print(f"\nChi-square test:")
print(f"  Chi-square statistic: {chi2:.3f}")
print(f"  p-value: {p_value:.6f}")
print(f"  Significant (p<0.05): {'YES' if p_value < 0.05 else 'NO'}")

# Identify which REGIME(s) are over-represented
print("\n" + "=" * 70)
print("REGIME ENRICHMENT ANALYSIS")
print("=" * 70)

enrichments = {}
for r, obs, exp in zip(regimes, observed, expected):
    if exp > 0:
        enrichment = obs / exp
        enrichments[r] = {
            'observed': obs,
            'expected': exp,
            'enrichment': enrichment,
        }

print(f"\nREGIME enrichment in high-reception folios:")
for r in sorted(enrichments.keys(), key=lambda x: -enrichments[x]['enrichment']):
    e = enrichments[r]
    direction = "OVER" if e['enrichment'] > 1.2 else ("UNDER" if e['enrichment'] < 0.8 else "NEUTRAL")
    print(f"  {r}: {e['enrichment']:.2f}x ({direction})")

# Detailed breakdown: Which specific folios in each REGIME?
print("\n" + "=" * 70)
print("HIGH-RECEPTION FOLIOS BY REGIME")
print("=" * 70)

for regime in sorted(regime_mapping.keys()):
    regime_high = [(e['folio'], e['reception_rate']) for e in high_reception
                   if e['folio'] in regime_mapping[regime]]
    if regime_high:
        print(f"\n{regime} ({len(regime_high)} high-reception folios):")
        for folio, rate in sorted(regime_high, key=lambda x: -x[1]):
            print(f"  {folio}: {rate:.3f}")

# Average reception rate by REGIME
print("\n" + "=" * 70)
print("MEAN RECEPTION RATE BY REGIME")
print("=" * 70)

regime_rates = {}
for regime, folios in regime_mapping.items():
    rates = []
    for f in folios:
        if f in phase3['all_folios']:
            rates.append(phase3['all_folios'][f]['reception_rate'])
    if rates:
        regime_rates[regime] = {
            'mean': np.mean(rates),
            'std': np.std(rates),
            'count': len(rates),
        }

print(f"\n{'REGIME':<12} {'Mean Rate':<12} {'Std':<10} {'Count':<8}")
print("-" * 45)
for regime in sorted(regime_rates.keys(), key=lambda x: -regime_rates[x]['mean']):
    r = regime_rates[regime]
    print(f"{regime:<12} {r['mean']:.3f}        {r['std']:.3f}     {r['count']}")

# ANOVA test: Do REGIMEs differ significantly in reception rate?
regime_rate_lists = []
regime_labels = []
for regime, folios in regime_mapping.items():
    rates = [phase3['all_folios'][f]['reception_rate'] for f in folios
             if f in phase3['all_folios']]
    if rates:
        regime_rate_lists.append(rates)
        regime_labels.append(regime)

f_stat, anova_p = stats.f_oneway(*regime_rate_lists)
print(f"\nANOVA test (reception rate across REGIMEs):")
print(f"  F-statistic: {f_stat:.3f}")
print(f"  p-value: {anova_p:.6f}")
print(f"  Significant (p<0.05): {'YES' if anova_p < 0.05 else 'NO'}")

# Save results
results = {
    'metadata': {
        'phase': 4,
        'description': 'Animal REGIME clustering',
        'high_reception_threshold': threshold,
        'high_reception_folios_count': len(high_reception),
        'folios_with_regime_assignment': len(high_reception_regimes),
    },
    'regime_distribution': {
        'high_reception': dict(regime_counts),
        'baseline': dict(baseline_counts),
    },
    'statistical_tests': {
        'chi_square': float(chi2),
        'chi_square_p_value': float(p_value),
        'anova_f': float(f_stat),
        'anova_p_value': float(anova_p),
    },
    'regime_enrichment': enrichments,
    'regime_mean_reception': {
        regime: {
            'mean': r['mean'],
            'std': r['std'],
            'count': r['count'],
        }
        for regime, r in regime_rates.items()
    },
    'high_reception_by_regime': {
        regime: [(e['folio'], e['reception_rate']) for e in high_reception
                 if e['folio'] in regime_mapping[regime]]
        for regime in regime_mapping.keys()
    },
}

output_path = 'phases/ANIMAL_RECIPE_TRACE/results/animal_regime_clustering.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")

# Summary
print("\n" + "=" * 70)
print("PHASE 4 COMPLETE - SUMMARY FOR CHECKPOINT")
print("=" * 70)

# Find most enriched REGIME
most_enriched = max(enrichments.keys(), key=lambda x: enrichments[x]['enrichment'])
most_enriched_val = enrichments[most_enriched]['enrichment']

# Find highest mean reception REGIME
highest_reception = max(regime_rates.keys(), key=lambda x: regime_rates[x]['mean'])
highest_reception_val = regime_rates[highest_reception]['mean']

print(f"""
Key Results:
- Chi-square test p-value: {p_value:.6f} ({'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'})
- ANOVA test p-value: {anova_p:.6f} ({'SIGNIFICANT' if anova_p < 0.05 else 'NOT SIGNIFICANT'})
- Most enriched REGIME: {most_enriched} ({most_enriched_val:.2f}x)
- Highest mean reception: {highest_reception} (rate={highest_reception_val:.3f})

REGIME enrichment in high-reception folios:
""")
for r in sorted(enrichments.keys(), key=lambda x: -enrichments[x]['enrichment']):
    e = enrichments[r]
    print(f"  {r}: {e['enrichment']:.2f}x")

print(f"""
Brunschwig prediction: Animal procedures use REGIME_1/REGIME_2 (low-fire, careful control)
Actual finding: {most_enriched} is most enriched in animal-receiving folios

Next Step: Phase 5 - Compare REGIME characteristics to Brunschwig animal procedure profile.
""")
