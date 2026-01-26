"""
PARENT OPERATOR DOMAIN CLUSTERING

If unique MIDDLEs are parametric instances, do different sections
use different parent operators?

- Herbal folios might favor certain operators
- Pharmaceutical might favor others
- This would suggest domain-specific instantiation

Or are parent operators universally distributed?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("PARENT OPERATOR DOMAIN CLUSTERING")
print("=" * 70)

# Build B folio MIDDLEs with section info
b_folio_middles = defaultdict(set)
folio_sections = {}

for token in tx.currier_b():
    word = token.word
    if word:
        m = morph.extract(word)
        if m.middle:
            b_folio_middles[token.folio].add(m.middle)
            # Approximate section from folio number
            folio_num = token.folio

# Map folios to approximate sections (based on folio numbers)
# This is a rough approximation
def get_section(folio):
    """Approximate section from folio identifier."""
    # Extract numeric part
    import re
    match = re.search(r'f(\d+)', folio)
    if not match:
        return 'unknown'
    num = int(match.group(1))

    # Rough section boundaries (these are approximate)
    if num <= 57:
        return 'herbal_A'
    elif num <= 66:
        return 'astro_cosmo'
    elif num <= 73:
        return 'bio_balneo'
    elif num <= 84:
        return 'herbal_B'
    elif num <= 102:
        return 'pharma'
    else:
        return 'recipe_stars'

# Build core and unique sets
middle_folio_count = defaultdict(int)
for folio, middles in b_folio_middles.items():
    for m in middles:
        middle_folio_count[m] += 1

total_folios = len(b_folio_middles)
core_threshold = total_folios * 0.5
core_middles = {m for m, count in middle_folio_count.items() if count >= core_threshold}
unique_middles = {m for m, count in middle_folio_count.items() if count == 1}

# Find parents for unique MIDDLEs
def find_parent(unique_middle, cores):
    parents = [c for c in cores if c in unique_middle and c != unique_middle]
    if parents:
        return max(parents, key=len)
    return None

unique_parents = {um: find_parent(um, core_middles) for um in unique_middles}
unique_parents = {k: v for k, v in unique_parents.items() if v is not None}

# Build section -> parent distribution
section_parents = defaultdict(Counter)
for folio, middles in b_folio_middles.items():
    section = get_section(folio)
    for m in middles:
        if m in unique_parents:
            parent = unique_parents[m]
            section_parents[section][parent] += 1

print(f"\nSections found:")
for section in sorted(section_parents.keys()):
    total = sum(section_parents[section].values())
    n_parents = len(section_parents[section])
    print(f"  {section}: {total} unique MIDDLEs using {n_parents} parent operators")

# For each section, show top parent operators
print("\n" + "=" * 70)
print("TOP PARENT OPERATORS BY SECTION")
print("=" * 70)

for section in sorted(section_parents.keys()):
    print(f"\n{section}:")
    total = sum(section_parents[section].values())
    for parent, count in section_parents[section].most_common(8):
        pct = 100 * count / total
        print(f"  '{parent}': {count} ({pct:.1f}%)")

# Test: Do sections have different parent profiles?
# Compare parent distributions across sections using chi-square

from scipy import stats

print("\n" + "=" * 70)
print("SECTION DIFFERENTIATION TEST")
print("=" * 70)

# Build contingency table: sections x top_parents
all_parents = set()
for section in section_parents:
    all_parents.update(section_parents[section].keys())

# Use top 15 parents for the test
top_parents = Counter()
for section in section_parents:
    for parent, count in section_parents[section].items():
        top_parents[parent] += count
top_15 = [p for p, _ in top_parents.most_common(15)]

sections = sorted(section_parents.keys())
contingency = []
for section in sections:
    row = [section_parents[section].get(p, 0) for p in top_15]
    contingency.append(row)

contingency = np.array(contingency)
chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

print(f"\nChi-square test (sections x top-15 parents):")
print(f"  chi2 = {chi2:.1f}, df = {dof}, p = {p_value:.6f}")

if p_value < 0.001:
    print(f"\n  => HIGHLY SIGNIFICANT section differentiation")
    print(f"     Sections use DIFFERENT parent operators")
elif p_value < 0.05:
    print(f"\n  => SIGNIFICANT section differentiation")
else:
    print(f"\n  => NO significant differentiation")
    print(f"     Parent operators are uniformly distributed")

# Show which parents are over/under-represented in each section
print("\n" + "=" * 70)
print("SECTION-SPECIFIC PARENT BIAS")
print("=" * 70)

# Compute expected counts
row_totals = contingency.sum(axis=1)
col_totals = contingency.sum(axis=0)
grand_total = contingency.sum()

print(f"\nOver/under-represented parents by section (observed/expected ratio):")
for i, section in enumerate(sections):
    print(f"\n{section}:")
    biases = []
    for j, parent in enumerate(top_15):
        expected_val = row_totals[i] * col_totals[j] / grand_total
        observed = contingency[i, j]
        if expected_val > 1:
            ratio = observed / expected_val
            biases.append((parent, ratio, observed, expected_val))

    # Show top over-represented
    biases.sort(key=lambda x: -x[1])
    print("  Over-represented:")
    for parent, ratio, obs, exp in biases[:3]:
        if ratio > 1.2:
            print(f"    '{parent}': {ratio:.2f}x (obs={obs}, exp={exp:.1f})")
    print("  Under-represented:")
    for parent, ratio, obs, exp in biases[-3:]:
        if ratio < 0.8:
            print(f"    '{parent}': {ratio:.2f}x (obs={obs}, exp={exp:.1f})")

# Summary interpretation
print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

if p_value < 0.05:
    print(f"""
DOMAIN-SPECIFIC INSTANTIATION:

Different manuscript sections use different parent operators.
This suggests the unique vocabulary is DOMAIN-ANCHORED:

- Herbal sections favor certain abstract operators
- Pharma sections favor others
- Each section instantiates the relevant operators for its domain

The unique vocabulary is not arbitrary - it's domain-specific
parametric elaboration of the control grammar.

This supports a TWO-LAYER interpretation:
1. GRAMMAR LAYER: 49 classes, universal across all sections
2. DOMAIN LAYER: Section-specific parent operator preferences
   determine which instantiations appear

Each folio is a DOMAIN-SPECIFIC PROCEDURE using the universal grammar
but instantiating domain-relevant operators.
""")
else:
    print(f"""
UNIFORM DISTRIBUTION:

Parent operators are uniformly distributed across sections.
The unique vocabulary is NOT domain-specific - it's generic
elaboration of the control grammar.

All sections use the same abstract operators in similar proportions.
Domain differences come from something else, not parent selection.
""")
