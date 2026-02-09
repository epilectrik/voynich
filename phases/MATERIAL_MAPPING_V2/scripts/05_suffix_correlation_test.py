"""
05_suffix_correlation_test.py

Test BRSC suffix predictions.

BRSC predictions:
- Fire degree correlates with EN suffix rate
- Degree 1 (gentle) -> high suffix concentration (EN-rich)
- Degree 3 (intense) -> low suffix concentration (EN-poor)

Test: Do fire degrees show expected suffix patterns?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

# Add scripts to path for voynich library
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

# Paths
results_dir = Path(__file__).parent.parent / "results"

print("="*70)
print("SUFFIX CORRELATION TEST")
print("="*70)

# Load transcript and morphology
tx = Transcript()
morph = Morphology()

# Load REGIME mapping
regime_mapping_path = Path(__file__).parent.parent.parent / "REGIME_SEMANTIC_INTERPRETATION" / "results" / "regime_folio_mapping.json"
with open(regime_mapping_path) as f:
    REGIME_FOLIOS = json.load(f)

# Fire degree -> REGIME mapping (from BRSC)
FIRE_TO_REGIME = {
    1: 2,  # Gentle -> REGIME_2
    2: 1,  # Standard -> REGIME_1
    3: 3,  # Intense -> REGIME_3
    4: 4,  # Precision -> REGIME_4
}

# BRSC suffix predictions
SUFFIX_PREDICTIONS = {
    1: 'HIGH',    # Gentle - more careful processing, more suffixes
    2: 'MEDIUM',  # Standard
    3: 'LOW',     # Intense - quick processing, fewer suffixes
    4: 'HIGH',    # Precision - careful, requires completion markers
}

# Build folio suffix profiles
print("\nBuilding folio suffix profiles...")
folio_suffix_data = defaultdict(lambda: {'total': 0, 'with_suffix': 0, 'suffix_types': Counter()})

for token in tx.currier_b():
    if '*' in token.word or not token.word.strip():
        continue

    folio = token.folio
    folio_suffix_data[folio]['total'] += 1

    try:
        m = morph.extract(token.word)
        if m.suffix:
            folio_suffix_data[folio]['with_suffix'] += 1
            folio_suffix_data[folio]['suffix_types'][m.suffix] += 1
    except:
        pass

# Compute rates
for folio, data in folio_suffix_data.items():
    if data['total'] > 0:
        data['suffix_rate'] = data['with_suffix'] / data['total']
    else:
        data['suffix_rate'] = 0

print(f"  Profiled {len(folio_suffix_data)} B folios")

# Group by REGIME
print("\n" + "="*70)
print("REGIME SUFFIX PROFILES")
print("="*70)

regime_suffix_profiles = {}
for regime_name, folios in REGIME_FOLIOS.items():
    regime_num = int(regime_name.split('_')[1])

    total = 0
    with_suffix = 0
    suffix_types = Counter()

    for folio in folios:
        if folio in folio_suffix_data:
            data = folio_suffix_data[folio]
            total += data['total']
            with_suffix += data['with_suffix']
            suffix_types.update(data['suffix_types'])

    if total > 0:
        suffix_rate = with_suffix / total
    else:
        suffix_rate = 0

    # Classify
    if suffix_rate > 0.35:
        suffix_class = 'HIGH'
    elif suffix_rate > 0.25:
        suffix_class = 'MEDIUM'
    else:
        suffix_class = 'LOW'

    regime_suffix_profiles[regime_num] = {
        'suffix_rate': suffix_rate,
        'suffix_class': suffix_class,
        'total_tokens': total,
        'tokens_with_suffix': with_suffix,
        'top_suffixes': suffix_types.most_common(5),
    }

    # Find corresponding fire degree
    fire_degree = [fd for fd, rn in FIRE_TO_REGIME.items() if rn == regime_num]
    fire_str = f"Fire {fire_degree[0]}" if fire_degree else "N/A"
    predicted = SUFFIX_PREDICTIONS.get(fire_degree[0], 'N/A') if fire_degree else 'N/A'

    print(f"\n{regime_name} ({fire_str}):")
    print(f"  Suffix rate: {suffix_rate:.3f} ({suffix_class})")
    print(f"  Predicted: {predicted}")
    print(f"  Match: {'YES' if suffix_class == predicted else 'NO'}")
    print(f"  Top suffixes: {suffix_types.most_common(3)}")

# Correlation analysis
print("\n" + "="*70)
print("FIRE DEGREE vs SUFFIX RATE CORRELATION")
print("="*70)

# Map fire degree to suffix rate via REGIME
fire_suffix_data = []
for fire_degree in [1, 2, 3, 4]:
    regime = FIRE_TO_REGIME[fire_degree]
    if regime in regime_suffix_profiles:
        fire_suffix_data.append({
            'fire_degree': fire_degree,
            'regime': regime,
            'suffix_rate': regime_suffix_profiles[regime]['suffix_rate'],
        })

fire_degrees = [d['fire_degree'] for d in fire_suffix_data]
suffix_rates = [d['suffix_rate'] for d in fire_suffix_data]

print("\nFire degree -> Suffix rate:")
for d in fire_suffix_data:
    print(f"  Degree {d['fire_degree']} (REGIME_{d['regime']}): {d['suffix_rate']:.3f}")

# Compute correlation
if len(fire_degrees) >= 3:
    r, p = stats.pearsonr(fire_degrees, suffix_rates)
    print(f"\nCorrelation: r = {r:.3f}, p = {p:.3f}")

    # Expected: negative correlation (higher degree = lower suffix rate)
    # Actually: BRSC says degree 1 and 4 both HIGH, so non-linear
    # Let's test the specific predictions
    print(f"\nNote: BRSC predicts non-linear relationship:")
    print("  Degree 1 (gentle) -> HIGH suffix")
    print("  Degree 3 (intense) -> LOW suffix")

# Test individual predictions
print("\n" + "="*70)
print("SUFFIX PREDICTION ACCURACY")
print("="*70)

correct = 0
total = len(fire_suffix_data)

for d in fire_suffix_data:
    predicted = SUFFIX_PREDICTIONS.get(d['fire_degree'], 'N/A')
    regime = d['regime']
    actual = regime_suffix_profiles[regime]['suffix_class']

    match = predicted == actual
    if match:
        correct += 1

    marker = 'OK' if match else 'MISS'
    print(f"  Fire {d['fire_degree']}: predicted={predicted}, actual={actual} [{marker}]")

print(f"\nAccuracy: {correct}/{total} ({100*correct/total:.1f}%)")

# Degree 1 vs 3 specific test
print("\n" + "="*70)
print("DEGREE 1 vs DEGREE 3 CONTRAST")
print("="*70)

degree_1_regime = FIRE_TO_REGIME[1]
degree_3_regime = FIRE_TO_REGIME[3]

suffix_1 = regime_suffix_profiles[degree_1_regime]['suffix_rate']
suffix_3 = regime_suffix_profiles[degree_3_regime]['suffix_rate']

print(f"\nDegree 1 (gentle, REGIME_{degree_1_regime}): {suffix_1:.3f}")
print(f"Degree 3 (intense, REGIME_{degree_3_regime}): {suffix_3:.3f}")

if suffix_1 > suffix_3:
    print("\nPREDICTION CONFIRMED: Degree 1 > Degree 3 suffix rate")
    contrast_result = 'CONFIRMED'
else:
    print("\nPrediction FAILED: Expected Degree 1 > Degree 3")
    contrast_result = 'FAILED'

# Save results
output = {
    'regime_suffix_profiles': {
        k: {**v, 'top_suffixes': list(v['top_suffixes'])}
        for k, v in regime_suffix_profiles.items()
    },
    'fire_suffix_mapping': fire_suffix_data,
    'suffix_predictions': SUFFIX_PREDICTIONS,
    'prediction_accuracy': {
        'correct': correct,
        'total': total,
        'accuracy': correct / total if total > 0 else 0,
    },
    'degree_1_vs_3_contrast': {
        'degree_1_suffix_rate': suffix_1,
        'degree_3_suffix_rate': suffix_3,
        'result': contrast_result,
    },
}

output_path = results_dir / "suffix_correlation_test.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {output_path}")
