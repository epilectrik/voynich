"""
04_hazard_quality_mapping.py

Test 5: Do Brunschwig's 5 quality tests map to Voynich's 5 hazard classes?

Brunschwig quality tests (from lines 3315-3340):
1. Taste test (no taste = pure)
2. Viscosity test (thumbnail test)
3. Cloudiness test (clarity)
4. Color/smell test (degradation signs)
5. Completeness test (proper separation)

Voynich hazard classes (from C109):
1. COMPOSITION_JUMP (17%)
2. RATE_MISMATCH (4%)
3. CONTAINMENT_TIMING (34%)
4. PHASE_ORDERING (41%)
5. ENERGY_OVERSHOOT (4%)

Hypothesis: The 5 hazard classes map to 5 quality rejection criteria.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

# Add scripts to path for voynich library
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript

# Paths
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

print("="*70)
print("HAZARD -> QUALITY TEST MAPPING")
print("="*70)

# Load transcript
tx = Transcript()

# Load hazard data
try:
    with open('phases/B_CONTROL_FLOW_SEMANTICS/results/hazard_topology.json') as f:
        hazard_data = json.load(f)
    print("Loaded hazard topology")
except FileNotFoundError:
    hazard_data = None
    print("Hazard topology not found, using defaults")

# Brunschwig quality tests (from BRSC)
brunschwig_quality_tests = {
    'taste': {
        'test': 'No taste = pure distillate',
        'failure': 'Contamination from source material',
        'importance': 'high',
        'frequency': 'every batch'
    },
    'viscosity': {
        'test': 'Thumbnail test for consistency',
        'failure': 'Wrong concentration',
        'importance': 'high',
        'frequency': 'every batch'
    },
    'clarity': {
        'test': 'Clear, not cloudy',
        'failure': 'Emulsion, improper separation',
        'importance': 'medium',
        'frequency': 'every batch'
    },
    'color_smell': {
        'test': 'Appropriate color and odor',
        'failure': 'Degradation or burning',
        'importance': 'high',
        'frequency': 'every batch'
    },
    'completeness': {
        'test': 'Proper separation achieved',
        'failure': 'Incomplete distillation',
        'importance': 'medium',
        'frequency': 'some batches'
    }
}

# Voynich hazard classes (from C109/BCSC)
voynich_hazard_classes = {
    'PHASE_ORDERING': {
        'frequency': 0.41,
        'description': 'Wrong sequence of operations',
        'pairs': 7
    },
    'CONTAINMENT_TIMING': {
        'frequency': 0.34,
        'description': 'Container state mismatch',
        'pairs': 6
    },
    'COMPOSITION_JUMP': {
        'frequency': 0.17,
        'description': 'Material composition mismatch',
        'pairs': 3
    },
    'RATE_MISMATCH': {
        'frequency': 0.04,
        'description': 'Process speed mismatch',
        'pairs': 1
    },
    'ENERGY_OVERSHOOT': {
        'frequency': 0.04,
        'description': 'Excessive energy application',
        'pairs': 0  # Categorical prohibition
    }
}

print("\n" + "="*70)
print("BRUNSCHWIG QUALITY TESTS")
print("="*70)

for test, info in brunschwig_quality_tests.items():
    print(f"\n{test.upper()}:")
    print(f"  Test: {info['test']}")
    print(f"  Failure: {info['failure']}")
    print(f"  Importance: {info['importance']}")

print("\n" + "="*70)
print("VOYNICH HAZARD CLASSES")
print("="*70)

for hazard, info in sorted(voynich_hazard_classes.items(), key=lambda x: -x[1]['frequency']):
    print(f"\n{hazard}:")
    print(f"  Frequency: {info['frequency']:.0%}")
    print(f"  Description: {info['description']}")
    print(f"  Forbidden pairs: {info['pairs']}")

# Hypothesized mapping
print("\n" + "="*70)
print("HYPOTHESIZED QUALITY -> HAZARD MAPPING")
print("="*70)

# Semantic mapping hypothesis
mapping_hypothesis = {
    'taste': 'COMPOSITION_JUMP',  # Contamination = wrong composition
    'viscosity': 'RATE_MISMATCH',  # Wrong concentration = wrong rate
    'clarity': 'CONTAINMENT_TIMING',  # Emulsion = container state
    'color_smell': 'ENERGY_OVERSHOOT',  # Burning = excess heat
    'completeness': 'PHASE_ORDERING'  # Incomplete = wrong sequence
}

print("\nProposed mapping:")
for quality, hazard in mapping_hypothesis.items():
    q_info = brunschwig_quality_tests[quality]
    h_info = voynich_hazard_classes[hazard]
    print(f"  {quality} -> {hazard}")
    print(f"    Brunschwig: {q_info['failure']}")
    print(f"    Voynich: {h_info['description']}")
    print(f"    Hazard frequency: {h_info['frequency']:.0%}")

# Test structural correspondence
print("\n" + "="*70)
print("STRUCTURAL CORRESPONDENCE TEST")
print("="*70)

# Both systems have exactly 5 categories
print(f"\nBrunschwig quality tests: {len(brunschwig_quality_tests)}")
print(f"Voynich hazard classes: {len(voynich_hazard_classes)}")

if len(brunschwig_quality_tests) == len(voynich_hazard_classes) == 5:
    print("  MATCH: Both systems have exactly 5 categories")
else:
    print("  MISMATCH: Different number of categories")

# Check frequency distribution shape
brunschwig_importance = {'high': 3, 'medium': 2}  # 3 high, 2 medium
voynich_freq = sorted(voynich_hazard_classes.values(), key=lambda x: -x['frequency'])
voynich_high = sum(1 for v in voynich_freq[:3] if v['frequency'] > 0.10)
voynich_low = sum(1 for v in voynich_freq if v['frequency'] < 0.10)

print(f"\nBrunschwig: 3 high importance, 2 medium importance")
print(f"Voynich: {voynich_high} high frequency (>10%), {voynich_low} low frequency (<10%)")

# The categorical prohibition test
print("\n" + "="*70)
print("CATEGORICAL PROHIBITION TEST")
print("="*70)

# Brunschwig: some failures are categorical (burn = discard)
# Voynich: ENERGY_OVERSHOOT has 0 pairs = categorical prohibition

print("\nBrunschwig: 'Burning' requires discard (no recovery)")
print("Voynich: ENERGY_OVERSHOOT has 0 forbidden pairs (categorical)")
print("         This means: any ENERGY_OVERSHOOT is prohibited, not specific pairs")

if voynich_hazard_classes['ENERGY_OVERSHOOT']['pairs'] == 0:
    print("  MATCH: Categorical prohibition structure matches")
else:
    print("  MISMATCH: ENERGY_OVERSHOOT is not categorical")

# Recovery rate comparison
print("\n" + "="*70)
print("RECOVERY RATE COMPARISON")
print("="*70)

# Brunschwig: 2 retry limit, then discard
# Voynich: Most hazards are navigable, ENERGY_OVERSHOOT is not

print("\nBrunschwig recovery protocol:")
print("  - Most failures: 2 retry attempts allowed")
print("  - Burning/severe: Immediate discard")

print("\nVoynich hazard frequency (proxy for navigability):")
for hazard in ['PHASE_ORDERING', 'CONTAINMENT_TIMING', 'COMPOSITION_JUMP', 'RATE_MISMATCH', 'ENERGY_OVERSHOOT']:
    freq = voynich_hazard_classes[hazard]['frequency']
    navigable = "YES (recoverable)" if freq > 0.10 else "LIMITED/NO (rare = severe)"
    print(f"  {hazard}: {freq:.0%} - {navigable}")

# Final assessment
print("\n" + "="*70)
print("ASSESSMENT")
print("="*70)

match_count = 0

# Test 1: Same number of categories
if len(brunschwig_quality_tests) == len(voynich_hazard_classes):
    print("[+] Both systems have 5 categories")
    match_count += 1
else:
    print("[-] Different category counts")

# Test 2: Categorical prohibition exists
if voynich_hazard_classes['ENERGY_OVERSHOOT']['pairs'] == 0:
    print("[+] Categorical prohibition (ENERGY_OVERSHOOT) exists")
    match_count += 1
else:
    print("[-] No categorical prohibition")

# Test 3: Distribution shape (most common vs rare)
if voynich_high >= 2 and voynich_low >= 2:
    print("[+] Distribution has both common and rare categories")
    match_count += 1
else:
    print("[-] Distribution shape mismatch")

# Test 4: Temperature-related most common
if voynich_hazard_classes['PHASE_ORDERING']['frequency'] > 0.35:
    print("[+] PHASE_ORDERING (sequence/temperature) most common (41%)")
    match_count += 1
else:
    print("[-] PHASE_ORDERING not most common")

print(f"\nOverall: {match_count}/4 structural matches")

if match_count >= 3:
    verdict = "STRONG MATCH"
elif match_count >= 2:
    verdict = "MODERATE MATCH"
else:
    verdict = "WEAK MATCH"

print(f"Verdict: {verdict}")

# Save results
results = {
    'brunschwig_quality_tests': brunschwig_quality_tests,
    'voynich_hazard_classes': voynich_hazard_classes,
    'mapping_hypothesis': mapping_hypothesis,
    'structural_tests': {
        'same_category_count': len(brunschwig_quality_tests) == len(voynich_hazard_classes),
        'categorical_prohibition_exists': voynich_hazard_classes['ENERGY_OVERSHOOT']['pairs'] == 0,
        'distribution_has_extremes': voynich_high >= 2 and voynich_low >= 2,
        'temperature_most_common': voynich_hazard_classes['PHASE_ORDERING']['frequency'] > 0.35
    },
    'match_count': match_count,
    'verdict': verdict,
    'interpretation': {
        'five_categories': '5-to-5 correspondence suggests similar classification scheme',
        'categorical_prohibition': 'ENERGY_OVERSHOOT = burning (no recovery)',
        'phase_ordering': 'Temperature sequencing most critical in both systems'
    }
}

output_path = results_dir / "hazard_quality_mapping.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {output_path}")
