"""
ANIMAL FOLIO RECEPTION (Phase 3)

Goal: Full analysis of which B folios receive animal-compatible vocabulary.
Uses Phase 2 output to compute reception scores for all B folios.

Input: animal_compatible_vocabulary.json from Phase 2
Output: animal_folio_reception.json
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("PHASE 3: ANIMAL FOLIO RECEPTION ANALYSIS")
print("=" * 70)

# Load Phase 2 results
with open('phases/ANIMAL_RECIPE_TRACE/results/animal_compatible_vocabulary.json', 'r') as f:
    phase2 = json.load(f)

animal_middles = set(phase2['animal_compatible_middles'].keys())
enriched_middles = {e['middle'] for e in phase2['enriched_middles']}

print(f"\nLoaded {len(animal_middles)} animal-compatible MIDDLEs from Phase 2")
print(f"Of which {len(enriched_middles)} are enriched (>1.5x)")

# Build complete B folio vocabulary profiles
print("\nBuilding B folio vocabulary profiles...")

b_folio_data = defaultdict(lambda: {
    'middles': set(),
    'tokens': set(),
    'token_count': 0,
    'middle_counts': Counter(),
})

for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        folio = token.folio
        b_folio_data[folio]['tokens'].add(token.word)
        b_folio_data[folio]['token_count'] += 1
        if m.middle:
            b_folio_data[folio]['middles'].add(m.middle)
            b_folio_data[folio]['middle_counts'][m.middle] += 1

print(f"Total B folios: {len(b_folio_data)}")

# Compute reception scores for each folio
print("\nComputing animal reception scores...")

folio_reception = {}
for folio, data in b_folio_data.items():
    all_middles = data['middles']
    animal_compatible = all_middles & animal_middles
    enriched_present = all_middles & enriched_middles

    # Basic reception rate
    reception_rate = len(animal_compatible) / len(all_middles) if all_middles else 0

    # Enriched reception rate (stronger signal)
    enriched_rate = len(enriched_present) / len(all_middles) if all_middles else 0

    # Weighted reception (by MIDDLE frequency in folio)
    weighted_animal = sum(data['middle_counts'][m] for m in animal_compatible)
    total_middle_tokens = sum(data['middle_counts'].values())
    weighted_rate = weighted_animal / total_middle_tokens if total_middle_tokens else 0

    folio_reception[folio] = {
        'total_middles': len(all_middles),
        'animal_compatible': len(animal_compatible),
        'reception_rate': reception_rate,
        'enriched_present': len(enriched_present),
        'enriched_rate': enriched_rate,
        'weighted_rate': weighted_rate,
        'token_count': data['token_count'],
        'animal_compatible_middles': list(animal_compatible),
        'enriched_middles_present': list(enriched_present),
    }

# Sort by reception rate
sorted_folios = sorted(folio_reception.items(), key=lambda x: -x[1]['reception_rate'])

# Statistics
reception_rates = [v['reception_rate'] for v in folio_reception.values()]
enriched_rates = [v['enriched_rate'] for v in folio_reception.values()]

print(f"\nReception rate statistics:")
print(f"  Mean: {np.mean(reception_rates):.3f}")
print(f"  Std: {np.std(reception_rates):.3f}")
print(f"  Min: {min(reception_rates):.3f}")
print(f"  Max: {max(reception_rates):.3f}")

print(f"\nEnriched rate statistics:")
print(f"  Mean: {np.mean(enriched_rates):.3f}")
print(f"  Std: {np.std(enriched_rates):.3f}")
print(f"  Min: {min(enriched_rates):.3f}")
print(f"  Max: {max(enriched_rates):.3f}")

# Top and bottom folios
print("\n" + "=" * 70)
print("TOP 15 ANIMAL-RECEIVING FOLIOS")
print("=" * 70)

print(f"\n{'Folio':<12} {'Reception':<12} {'Enriched':<12} {'A-Mid/Total':<15}")
print("-" * 50)
for folio, data in sorted_folios[:15]:
    print(f"{folio:<12} {data['reception_rate']:.3f}        {data['enriched_rate']:.3f}        {data['animal_compatible']}/{data['total_middles']}")

print("\n" + "=" * 70)
print("BOTTOM 15 ANIMAL-RECEIVING FOLIOS")
print("=" * 70)

print(f"\n{'Folio':<12} {'Reception':<12} {'Enriched':<12} {'A-Mid/Total':<15}")
print("-" * 50)
for folio, data in sorted_folios[-15:]:
    print(f"{folio:<12} {data['reception_rate']:.3f}        {data['enriched_rate']:.3f}        {data['animal_compatible']}/{data['total_middles']}")

# Test for non-uniform distribution
print("\n" + "=" * 70)
print("STATISTICAL TESTS")
print("=" * 70)

# Test if top folios are significantly different from bottom
top_10_rates = [v['reception_rate'] for _, v in sorted_folios[:10]]
bottom_10_rates = [v['reception_rate'] for _, v in sorted_folios[-10:]]

t_stat, p_value = stats.ttest_ind(top_10_rates, bottom_10_rates)
print(f"\nTop 10 vs Bottom 10 reception rates:")
print(f"  Top 10 mean: {np.mean(top_10_rates):.3f}")
print(f"  Bottom 10 mean: {np.mean(bottom_10_rates):.3f}")
print(f"  Ratio: {np.mean(top_10_rates)/np.mean(bottom_10_rates):.2f}x")
print(f"  t-statistic: {t_stat:.3f}")
print(f"  p-value: {p_value:.6f}")

# Test enriched MIDDLE concentration
top_10_enriched = [v['enriched_rate'] for _, v in sorted_folios[:10]]
bottom_10_enriched = [v['enriched_rate'] for _, v in sorted_folios[-10:]]

t_stat_e, p_value_e = stats.ttest_ind(top_10_enriched, bottom_10_enriched)
print(f"\nEnriched MIDDLE concentration (Top 10 vs Bottom 10):")
print(f"  Top 10 mean enriched rate: {np.mean(top_10_enriched):.3f}")
print(f"  Bottom 10 mean enriched rate: {np.mean(bottom_10_enriched):.3f}")
print(f"  Ratio: {np.mean(top_10_enriched)/np.mean(bottom_10_enriched):.2f}x if bottom_10 > 0 else 'inf'")
print(f"  t-statistic: {t_stat_e:.3f}")
print(f"  p-value: {p_value_e:.6f}")

# Check folio clustering by section
print("\n" + "=" * 70)
print("SECTION ANALYSIS")
print("=" * 70)

# Group folios by section (using folio number ranges)
def get_section(folio):
    """Rough section assignment based on folio number."""
    # Extract number from folio (e.g., 'f33v' -> 33)
    try:
        num = int(''.join(c for c in folio if c.isdigit()))
        if num <= 25:
            return 'herbal_a'
        elif num <= 56:
            return 'herbal_b'
        elif num <= 66:
            return 'pharma'
        elif num <= 84:
            return 'astro'
        elif num <= 86:
            return 'cosmo'
        else:
            return 'recipe'
    except:
        return 'unknown'

section_reception = defaultdict(list)
for folio, data in folio_reception.items():
    section = get_section(folio)
    section_reception[section].append(data['reception_rate'])

print(f"\nMean reception rate by section:")
for section, rates in sorted(section_reception.items(), key=lambda x: -np.mean(x[1])):
    print(f"  {section:<12}: {np.mean(rates):.3f} (n={len(rates)})")

# Identify high-reception cluster
threshold_high = np.mean(reception_rates) + 0.5 * np.std(reception_rates)
high_reception_folios = [(f, d) for f, d in sorted_folios if d['reception_rate'] >= threshold_high]

print(f"\nHigh-reception cluster (threshold: {threshold_high:.3f}):")
print(f"  Count: {len(high_reception_folios)} folios")
if high_reception_folios:
    sections = [get_section(f) for f, _ in high_reception_folios]
    section_counts = Counter(sections)
    print(f"  Section distribution: {dict(section_counts)}")

# Save results
results = {
    'metadata': {
        'phase': 3,
        'description': 'Animal folio reception analysis',
        'animal_middles_used': len(animal_middles),
        'enriched_middles_used': len(enriched_middles),
        'b_folios_analyzed': len(folio_reception),
    },
    'statistics': {
        'reception_rate_mean': float(np.mean(reception_rates)),
        'reception_rate_std': float(np.std(reception_rates)),
        'reception_rate_min': float(min(reception_rates)),
        'reception_rate_max': float(max(reception_rates)),
        'enriched_rate_mean': float(np.mean(enriched_rates)),
        'enriched_rate_std': float(np.std(enriched_rates)),
        'top_bottom_ratio': float(np.mean(top_10_rates)/np.mean(bottom_10_rates)),
        'top_bottom_p_value': float(p_value),
        'enriched_top_bottom_p_value': float(p_value_e),
    },
    'high_reception_threshold': float(threshold_high),
    'high_reception_folios': [
        {
            'folio': f,
            'reception_rate': d['reception_rate'],
            'enriched_rate': d['enriched_rate'],
            'section': get_section(f),
        }
        for f, d in high_reception_folios
    ],
    'section_analysis': {
        section: {
            'mean_reception': float(np.mean(rates)),
            'count': len(rates),
        }
        for section, rates in section_reception.items()
    },
    'all_folios': {
        folio: {
            'reception_rate': data['reception_rate'],
            'enriched_rate': data['enriched_rate'],
            'animal_compatible': data['animal_compatible'],
            'total_middles': data['total_middles'],
            'enriched_present': data['enriched_present'],
        }
        for folio, data in sorted_folios
    },
}

output_path = 'phases/ANIMAL_RECIPE_TRACE/results/animal_folio_reception.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")

# Summary
print("\n" + "=" * 70)
print("PHASE 3 COMPLETE - SUMMARY FOR CHECKPOINT")
print("=" * 70)

print(f"""
Key Results:
- B folios analyzed: {len(folio_reception)}
- Reception rate range: {min(reception_rates):.3f} to {max(reception_rates):.3f}
- Top/Bottom ratio: {np.mean(top_10_rates)/np.mean(bottom_10_rates):.2f}x
- Statistical significance: p={p_value:.6f}
- High-reception folios (>{threshold_high:.3f}): {len(high_reception_folios)}

Top 5 animal-receiving folios:
""")
for i, (folio, data) in enumerate(sorted_folios[:5]):
    print(f"  {i+1}. {folio}: {data['reception_rate']:.3f} ({data['animal_compatible']}/{data['total_middles']} MIDDLEs)")

print(f"""
Next Step: Phase 4 - Check REGIME clustering of high-reception folios.
           Do they cluster in REGIME_1/REGIME_2 (low-fire, careful control)?
""")
