"""
Q11: Hazard Class Co-occurrence

Do hazard-adjacent classes cluster together or disperse across lines?
This tests whether the grammar actively manages hazard proximity.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Hazard classes from C109/C541
# These are classes involved in the 17 forbidden transitions
HAZARD_CLASSES = {
    # Gateway (hazard entry points)
    30,  # Class 30 = pure gateway
    # Terminal (hazard exit points)
    31,  # Class 31 = pure terminal
    # Hazard-adjacent classes (from C541 enumeration)
    7, 8, 32, 33, 34, 36,  # ENERGY operators near hazards
}

# More specifically, the 5 hazard failure classes from C109
FAILURE_CLASSES = {
    'PHASE_ORDERING': [32, 33],  # 41% of hazards
    'ENERGY_OVERFLOW': [8, 34],
    'FLOW_VIOLATION': [7, 30],
    'BOUNDARY_CROSS': [31, 36],
    'STATE_CONFLICT': [10, 11],
}

ALL_HAZARD_ADJACENT = set()
for classes in FAILURE_CLASSES.values():
    ALL_HAZARD_ADJACENT.update(classes)

print("=" * 70)
print("Q11: HAZARD CLASS CO-OCCURRENCE")
print("=" * 70)

print(f"\nHazard-adjacent classes: {sorted(ALL_HAZARD_ADJACENT)}")

# Group tokens by line
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    line = token.line
    cls = token_to_class.get(word)
    lines[(folio, line)].append({'word': word, 'class': cls})

print(f"Total lines: {len(lines)}")

# 1. HAZARD CLASS PRESENCE PER LINE
print("\n" + "-" * 70)
print("1. HAZARD CLASS PRESENCE PER LINE")
print("-" * 70)

hazard_counts_per_line = []
lines_with_hazard = 0
lines_with_multiple_hazard = 0

for (folio, line), word_data in lines.items():
    classes = [wd['class'] for wd in word_data if wd['class'] is not None]
    hazard_in_line = [c for c in classes if c in ALL_HAZARD_ADJACENT]
    hazard_counts_per_line.append(len(hazard_in_line))

    if hazard_in_line:
        lines_with_hazard += 1
    if len(hazard_in_line) > 1:
        lines_with_multiple_hazard += 1

print(f"\nLines with hazard-adjacent class: {lines_with_hazard} ({lines_with_hazard/len(lines)*100:.1f}%)")
print(f"Lines with 2+ hazard-adjacent classes: {lines_with_multiple_hazard} ({lines_with_multiple_hazard/len(lines)*100:.1f}%)")
print(f"Mean hazard classes per line: {np.mean(hazard_counts_per_line):.2f}")

# Distribution
print("\n| Hazard Count | Lines | % |")
print("|--------------|-------|---|")
for count in range(max(hazard_counts_per_line) + 1):
    n = sum(1 for c in hazard_counts_per_line if c == count)
    print(f"| {count:12d} | {n:5d} | {n/len(lines)*100:4.1f}% |")

# 2. PAIRWISE CO-OCCURRENCE
print("\n" + "-" * 70)
print("2. PAIRWISE HAZARD CLASS CO-OCCURRENCE")
print("-" * 70)

# Count co-occurrences
cooccurrence = defaultdict(lambda: defaultdict(int))
class_line_counts = defaultdict(int)

for (folio, line), word_data in lines.items():
    classes = set(wd['class'] for wd in word_data if wd['class'] is not None)
    hazard_in_line = classes & ALL_HAZARD_ADJACENT

    for c in hazard_in_line:
        class_line_counts[c] += 1

    for c1 in hazard_in_line:
        for c2 in hazard_in_line:
            if c1 <= c2:  # Avoid double counting
                cooccurrence[c1][c2] += 1

# Calculate expected co-occurrence under independence
total_lines = len(lines)
print("\nObserved vs Expected co-occurrence:")
print("| Pair | Observed | Expected | Enrichment | p-value |")
print("|------|----------|----------|------------|---------|")

significant_pairs = []
for c1 in sorted(ALL_HAZARD_ADJACENT):
    for c2 in sorted(ALL_HAZARD_ADJACENT):
        if c1 > c2:
            continue

        observed = cooccurrence[c1][c2]
        p1 = class_line_counts[c1] / total_lines
        p2 = class_line_counts[c2] / total_lines

        if c1 == c2:
            # Self co-occurrence: expected = p^2 * n for appearing twice
            # But we're counting lines with at least one, so expected = p1 * n
            expected = p1 * total_lines
        else:
            expected = p1 * p2 * total_lines

        if expected < 5:
            continue

        enrichment = observed / expected if expected > 0 else 0

        # Chi-square test
        chi2 = (observed - expected) ** 2 / expected
        p_value = 1 - stats.chi2.cdf(chi2, df=1)

        if p_value < 0.01 and c1 != c2:
            significant_pairs.append({
                'c1': c1, 'c2': c2,
                'observed': observed, 'expected': expected,
                'enrichment': enrichment, 'p_value': p_value
            })

        if enrichment > 1.3 or enrichment < 0.7 or c1 == c2:
            tag = "+" if enrichment > 1.3 else ("-" if enrichment < 0.7 else "")
            print(f"| {c1:2d}-{c2:2d} | {observed:8d} | {expected:8.1f} | {enrichment:9.2f}x{tag} | {p_value:.4f} |")

# 3. CLUSTERING VS DISPERSION
print("\n" + "-" * 70)
print("3. CLUSTERING VS DISPERSION TEST")
print("-" * 70)

# Compare observed variance of hazard counts to expected under random
observed_var = np.var(hazard_counts_per_line)
observed_mean = np.mean(hazard_counts_per_line)

# Under Poisson (random), variance = mean
expected_var = observed_mean

dispersion_index = observed_var / expected_var if expected_var > 0 else 1

print(f"\nMean hazard classes per line: {observed_mean:.3f}")
print(f"Variance: {observed_var:.3f}")
print(f"Expected variance (Poisson): {expected_var:.3f}")
print(f"Dispersion index: {dispersion_index:.3f}")

if dispersion_index > 1.2:
    print("-> CLUSTERED: Hazard classes appear together more than random")
elif dispersion_index < 0.8:
    print("-> DISPERSED: Hazard classes avoid each other")
else:
    print("-> RANDOM: Hazard classes distributed as expected")

# Chi-square test for dispersion
chi2_dispersion = (len(lines) - 1) * observed_var / expected_var
p_dispersion = 1 - stats.chi2.cdf(chi2_dispersion, df=len(lines)-1)
print(f"Chi-square test: chi2={chi2_dispersion:.1f}, p={'<0.001' if p_dispersion < 0.001 else f'{p_dispersion:.4f}'}")

# 4. FAILURE CLASS PAIRING
print("\n" + "-" * 70)
print("4. FAILURE CLASS PAIRING PATTERNS")
print("-" * 70)

print("\nDo failure class pairs (from same failure type) co-occur?")
print("| Failure Type | Pair | Observed | Expected | Enrichment |")
print("|--------------|------|----------|----------|------------|")

for failure_type, classes in FAILURE_CLASSES.items():
    if len(classes) < 2:
        continue
    c1, c2 = classes[0], classes[1]
    observed = cooccurrence[min(c1,c2)][max(c1,c2)]
    p1 = class_line_counts[c1] / total_lines
    p2 = class_line_counts[c2] / total_lines
    expected = p1 * p2 * total_lines
    enrichment = observed / expected if expected > 0 else 0

    print(f"| {failure_type:14s} | {c1:2d}-{c2:2d} | {observed:8d} | {expected:8.1f} | {enrichment:9.2f}x |")

# 5. GATEWAY-TERMINAL PAIRING
print("\n" + "-" * 70)
print("5. GATEWAY-TERMINAL PAIRING")
print("-" * 70)

# Class 30 (gateway) and Class 31 (terminal) pairing
gateway = 30
terminal = 31
observed = cooccurrence[gateway][terminal]
p_gw = class_line_counts[gateway] / total_lines
p_tm = class_line_counts[terminal] / total_lines
expected = p_gw * p_tm * total_lines
enrichment = observed / expected if expected > 0 else 0

print(f"\nGateway (30) - Terminal (31) co-occurrence:")
print(f"  Observed: {observed} lines")
print(f"  Expected: {expected:.1f} lines")
print(f"  Enrichment: {enrichment:.2f}x")

# Chi-square
chi2 = (observed - expected) ** 2 / expected if expected > 0 else 0
p_value = 1 - stats.chi2.cdf(chi2, df=1)
print(f"  Chi-square: {chi2:.1f}, p={p_value:.4f}")

if enrichment > 1:
    print("  -> Gateway and terminal CLUSTER together")
else:
    print("  -> Gateway and terminal DISPERSE")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
1. HAZARD PRESENCE:
   - {lines_with_hazard/len(lines)*100:.0f}% of lines contain hazard-adjacent classes
   - Mean {observed_mean:.1f} hazard classes per line

2. DISPERSION PATTERN:
   - Dispersion index: {dispersion_index:.2f}
   - Pattern: {'CLUSTERED' if dispersion_index > 1.2 else ('DISPERSED' if dispersion_index < 0.8 else 'RANDOM')}

3. GATEWAY-TERMINAL:
   - Co-occur {enrichment:.2f}x {'more' if enrichment > 1 else 'less'} than random
   - Consistent with C548 (manuscript-level envelope)

4. SIGNIFICANT PAIRS:
   - {len(significant_pairs)} pairs show significant co-occurrence
""")

# Save results
results = {
    'hazard_presence': {
        'lines_with_hazard': lines_with_hazard,
        'lines_with_multiple': lines_with_multiple_hazard,
        'mean_per_line': float(observed_mean)
    },
    'dispersion': {
        'variance': float(observed_var),
        'expected_variance': float(expected_var),
        'dispersion_index': float(dispersion_index)
    },
    'gateway_terminal': {
        'observed': observed,
        'expected': float(expected),
        'enrichment': float(enrichment)
    },
    'significant_pairs': significant_pairs
}

with open(RESULTS / 'hazard_class_cooccurrence.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'hazard_class_cooccurrence.json'}")
