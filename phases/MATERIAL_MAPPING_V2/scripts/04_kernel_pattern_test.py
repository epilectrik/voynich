"""
04_kernel_pattern_test.py

Test BRSC kernel predictions against Voynich data.

BRSC predictions:
- Degree 1 (gentle/balneum marie) -> high e, low k (cooling/equilibration dominant)
- Degree 2 (standard) -> balanced kernel distribution
- Degree 3 (intense) -> high k, low h (energy-dominant)
- Degree 4 (precision/animal) -> specific pattern (ESCAPE+AUX for animals)

Test: Do validated mappings show expected kernel patterns?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

# Add scripts to path for voynich library
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript

# Paths
results_dir = Path(__file__).parent.parent / "results"

print("="*70)
print("KERNEL PATTERN PREDICTION TEST")
print("="*70)

# Load validated mappings
with open(results_dir / "validated_mappings.json", encoding='utf-8') as f:
    validation_data = json.load(f)

# Load Brunschwig signatures for predictions
with open(results_dir / "brunschwig_signatures.json", encoding='utf-8') as f:
    sig_data = json.load(f)

signatures_by_name = {s['name_english']: s for s in sig_data['signatures']}

# BRSC kernel predictions by fire degree
KERNEL_PREDICTIONS = {
    1: {'e': 'HIGH', 'h': 'LOW', 'k': 'MEDIUM'},   # Gentle - cooling dominant
    2: {'e': 'MEDIUM', 'h': 'MEDIUM', 'k': 'MEDIUM'},  # Standard - balanced
    3: {'e': 'LOW', 'h': 'MEDIUM', 'k': 'HIGH'},   # Intense - energy dominant
    4: {'e': 'HIGH', 'h': 'LOW', 'k': 'HIGH'},     # Precision - ESCAPE pattern
}

# Threshold definitions
def classify_rate(rate):
    """Classify kernel rate as HIGH/MEDIUM/LOW."""
    if rate > 0.4:
        return 'HIGH'
    elif rate > 0.2:
        return 'MEDIUM'
    else:
        return 'LOW'

# Load transcript for kernel analysis
tx = Transcript()

# Build B folio kernel profiles
print("\nBuilding B folio kernel profiles...")
folio_kernels = defaultdict(lambda: {'e': 0, 'h': 0, 'k': 0, 'total': 0})

for token in tx.currier_b():
    if '*' in token.word or not token.word.strip():
        continue

    folio = token.folio
    word = token.word

    # Count kernels in word
    for char in word:
        if char == 'e':
            folio_kernels[folio]['e'] += 1
            folio_kernels[folio]['total'] += 1
        elif char == 'h':
            folio_kernels[folio]['h'] += 1
            folio_kernels[folio]['total'] += 1
        elif char == 'k':
            folio_kernels[folio]['k'] += 1
            folio_kernels[folio]['total'] += 1

# Compute rates
for folio, counts in folio_kernels.items():
    total = counts['total']
    if total > 0:
        counts['e_rate'] = counts['e'] / total
        counts['h_rate'] = counts['h'] / total
        counts['k_rate'] = counts['k'] / total
    else:
        counts['e_rate'] = counts['h_rate'] = counts['k_rate'] = 0

print(f"  Profiled {len(folio_kernels)} B folios")

# Load REGIME mapping to group folios
regime_mapping_path = Path(__file__).parent.parent.parent / "REGIME_SEMANTIC_INTERPRETATION" / "results" / "regime_folio_mapping.json"
with open(regime_mapping_path) as f:
    REGIME_FOLIOS = json.load(f)

# Compute REGIME kernel profiles
print("\n" + "="*70)
print("REGIME KERNEL PROFILES")
print("="*70)

regime_profiles = {}
for regime_name, folios in REGIME_FOLIOS.items():
    regime_num = int(regime_name.split('_')[1])

    totals = {'e': 0, 'h': 0, 'k': 0, 'total': 0}
    for folio in folios:
        if folio in folio_kernels:
            for k in ['e', 'h', 'k', 'total']:
                totals[k] += folio_kernels[folio][k]

    if totals['total'] > 0:
        e_rate = totals['e'] / totals['total']
        h_rate = totals['h'] / totals['total']
        k_rate = totals['k'] / totals['total']
    else:
        e_rate = h_rate = k_rate = 0

    regime_profiles[regime_num] = {
        'e_rate': e_rate,
        'h_rate': h_rate,
        'k_rate': k_rate,
        'e_class': classify_rate(e_rate),
        'h_class': classify_rate(h_rate),
        'k_class': classify_rate(k_rate),
        'n_folios': len(folios),
    }

    pred = KERNEL_PREDICTIONS.get(regime_num, {})
    print(f"\n{regime_name}:")
    print(f"  e: {e_rate:.3f} ({classify_rate(e_rate)}) - predicted {pred.get('e', 'N/A')}")
    print(f"  h: {h_rate:.3f} ({classify_rate(h_rate)}) - predicted {pred.get('h', 'N/A')}")
    print(f"  k: {k_rate:.3f} ({classify_rate(k_rate)}) - predicted {pred.get('k', 'N/A')}")

    # Check prediction match
    matches = 0
    for kernel in ['e', 'h', 'k']:
        actual = regime_profiles[regime_num][f'{kernel}_class']
        predicted = pred.get(kernel, 'N/A')
        if actual == predicted:
            matches += 1

    print(f"  Prediction match: {matches}/3")

# Test validated mappings
print("\n" + "="*70)
print("VALIDATED MAPPING KERNEL TESTS")
print("="*70)

validated = validation_data['validated_mappings']
kernel_test_results = []

for mapping in validated:
    recipe_name = mapping['recipe']
    record_id = mapping['record_id']
    fire_degree = mapping['fire_degree']

    sig = signatures_by_name.get(recipe_name, {})
    kernel_exp = sig.get('kernel_expectation', {})

    # Get expected REGIME
    expected_regime = sig.get('expected_regime', 2)

    # Get actual REGIME kernel profile
    actual_profile = regime_profiles.get(expected_regime, {})

    # Compare
    result = {
        'recipe': recipe_name,
        'record_id': record_id,
        'fire_degree': fire_degree,
        'expected_regime': expected_regime,
        'predicted_kernels': KERNEL_PREDICTIONS.get(fire_degree, {}),
        'actual_kernels': {
            'e': actual_profile.get('e_class', 'N/A'),
            'h': actual_profile.get('h_class', 'N/A'),
            'k': actual_profile.get('k_class', 'N/A'),
        },
        'matches': 0,
    }

    # Count matches
    pred = KERNEL_PREDICTIONS.get(fire_degree, {})
    for kernel in ['e', 'h', 'k']:
        if actual_profile.get(f'{kernel}_class') == pred.get(kernel):
            result['matches'] += 1

    kernel_test_results.append(result)

# Summarize results
print("\nKernel prediction results for validated mappings:")
total_matches = sum(r['matches'] for r in kernel_test_results)
total_tests = len(kernel_test_results) * 3

print(f"\nOverall: {total_matches}/{total_tests} kernel predictions correct")
print(f"Accuracy: {100 * total_matches / total_tests:.1f}%")

# Group by fire degree
by_degree = defaultdict(list)
for r in kernel_test_results:
    by_degree[r['fire_degree']].append(r)

print("\nBy fire degree:")
for degree in sorted(by_degree.keys()):
    results = by_degree[degree]
    matches = sum(r['matches'] for r in results)
    tests = len(results) * 3
    print(f"  Degree {degree}: {matches}/{tests} ({100*matches/tests:.1f}%)")

# Detailed results for animal mappings
print("\n" + "="*70)
print("ANIMAL MAPPING KERNEL DETAILS")
print("="*70)

animal_results = [r for r in kernel_test_results
                  if 'chicken' in r['recipe'].lower()
                  or 'ox' in r['recipe'].lower()
                  or 'earthworm' in r['recipe'].lower()
                  or 'snail' in r['recipe'].lower()]

for r in animal_results[:10]:
    print(f"\n{r['recipe']} -> {r['record_id']}")
    print(f"  Fire degree: {r['fire_degree']} -> expected REGIME_{r['expected_regime']}")
    print(f"  Predicted: e={r['predicted_kernels'].get('e', 'N/A')}, "
          f"h={r['predicted_kernels'].get('h', 'N/A')}, "
          f"k={r['predicted_kernels'].get('k', 'N/A')}")
    print(f"  Actual: e={r['actual_kernels']['e']}, "
          f"h={r['actual_kernels']['h']}, "
          f"k={r['actual_kernels']['k']}")
    print(f"  Match: {r['matches']}/3")

# Save results
output = {
    'regime_profiles': regime_profiles,
    'kernel_predictions': KERNEL_PREDICTIONS,
    'kernel_test_results': kernel_test_results,
    'summary': {
        'total_correct': total_matches,
        'total_tests': total_tests,
        'accuracy': total_matches / total_tests if total_tests > 0 else 0,
    },
    'by_fire_degree': {
        degree: {
            'correct': sum(r['matches'] for r in results),
            'total': len(results) * 3,
        }
        for degree, results in by_degree.items()
    }
}

output_path = results_dir / "kernel_pattern_test.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {output_path}")
