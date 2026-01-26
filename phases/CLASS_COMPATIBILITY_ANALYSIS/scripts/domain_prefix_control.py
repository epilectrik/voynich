"""
DOMAIN OPERATOR PREFERENCES - PREFIX CONTROL

The expert noted that section-specific operator preferences might be a
downstream effect of PREFIX-section associations (C374, C423).

Test: Do domain-specific parent operator preferences survive when
controlling for PREFIX distribution?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
import re

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("DOMAIN OPERATOR PREFERENCES - PREFIX CONTROL")
print("=" * 70)

# Build data
token_data = []
for token in tx.currier_b():
    word = token.word
    if word:
        m = morph.extract(word)
        if m.middle:
            token_data.append({
                'folio': token.folio,
                'middle': m.middle,
                'prefix': m.prefix or 'NONE',
            })

# Get section
def get_section(folio):
    match = re.search(r'f(\d+)', folio)
    if not match:
        return 'unknown'
    num = int(match.group(1))
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

# Build folio MIDDLEs and identify unique/core
folio_middles = defaultdict(set)
for t in token_data:
    folio_middles[t['folio']].add(t['middle'])

middle_folio_count = Counter()
for folio, middles in folio_middles.items():
    for m in middles:
        middle_folio_count[m] += 1

total_folios = len(folio_middles)
core_middles = {m for m, c in middle_folio_count.items() if c >= total_folios * 0.5}
unique_middles = {m for m, c in middle_folio_count.items() if c == 1}

# Find parent for each unique MIDDLE
def find_parent(um, cores):
    parents = [c for c in cores if c in um and c != um]
    return max(parents, key=len) if parents else None

unique_parents = {um: find_parent(um, core_middles) for um in unique_middles}
unique_parents = {k: v for k, v in unique_parents.items() if v}

# Build MIDDLE -> PREFIX mapping
middle_prefixes = defaultdict(Counter)
for t in token_data:
    middle_prefixes[t['middle']][t['prefix']] += 1

# For each unique MIDDLE, get its dominant PREFIX
def get_dominant_prefix(middle):
    counts = middle_prefixes[middle]
    if counts:
        return counts.most_common(1)[0][0]
    return 'NONE'

# Build section -> (parent, prefix) distribution
section_parent_prefix = defaultdict(lambda: defaultdict(Counter))
for folio, middles in folio_middles.items():
    section = get_section(folio)
    for m in middles:
        if m in unique_parents:
            parent = unique_parents[m]
            prefix = get_dominant_prefix(m)
            section_parent_prefix[section][prefix][parent] += 1

# Section -> PREFIX distribution
section_prefix_counts = defaultdict(Counter)
for section, prefix_parent in section_parent_prefix.items():
    for prefix, parent_counts in prefix_parent.items():
        section_prefix_counts[section][prefix] += sum(parent_counts.values())

print("\n" + "=" * 70)
print("SECTION PREFIX DISTRIBUTIONS")
print("=" * 70)

for section in sorted(section_prefix_counts.keys()):
    print(f"\n{section}:")
    total = sum(section_prefix_counts[section].values())
    for prefix, count in section_prefix_counts[section].most_common(5):
        pct = 100 * count / total
        print(f"  {prefix}: {count} ({pct:.1f}%)")

# Now the key test: WITHIN each PREFIX stratum, do sections differ?
print("\n" + "=" * 70)
print("PREFIX-CONTROLLED SECTION DIFFERENTIATION")
print("=" * 70)

# For each major PREFIX, test if sections have different parent distributions
major_prefixes = ['NONE', 'ch', 'o', 'qo', 'sh']

for prefix in major_prefixes:
    print(f"\n--- PREFIX = '{prefix}' ---")

    # Build contingency: sections x top parents for this PREFIX
    sections = sorted(section_parent_prefix.keys())

    # Get top parents for this prefix
    all_parents_this_prefix = Counter()
    for section in sections:
        all_parents_this_prefix.update(section_parent_prefix[section][prefix])

    if sum(all_parents_this_prefix.values()) < 20:
        print(f"  Insufficient data ({sum(all_parents_this_prefix.values())} obs)")
        continue

    top_parents = [p for p, _ in all_parents_this_prefix.most_common(8)]

    contingency = []
    for section in sections:
        row = [section_parent_prefix[section][prefix].get(p, 0) for p in top_parents]
        if sum(row) > 0:
            contingency.append((section, row))

    if len(contingency) < 2:
        print(f"  Insufficient sections")
        continue

    section_names = [c[0] for c in contingency]
    matrix = np.array([c[1] for c in contingency])

    # Remove columns that are all zeros
    col_sums = matrix.sum(axis=0)
    nonzero_cols = col_sums > 0
    if nonzero_cols.sum() < 2:
        print(f"  Insufficient parent variation")
        continue

    matrix = matrix[:, nonzero_cols]
    filtered_parents = [p for p, keep in zip(top_parents, nonzero_cols) if keep]

    # Remove rows that are all zeros
    row_sums = matrix.sum(axis=1)
    nonzero_rows = row_sums > 0
    matrix = matrix[nonzero_rows, :]
    filtered_sections = [s for s, keep in zip(section_names, nonzero_rows) if keep]

    if matrix.shape[0] < 2 or matrix.shape[1] < 2:
        print(f"  Insufficient variation after filtering")
        continue

    try:
        chi2, p_value, dof, expected = stats.chi2_contingency(matrix)
        print(f"  Chi-square: {chi2:.1f}, df={dof}, p={p_value:.4f}")

        if p_value < 0.05:
            print(f"  => SIGNIFICANT: Sections differ even within this PREFIX")
        else:
            print(f"  => NOT significant: Section differences explained by PREFIX")
    except ValueError as e:
        print(f"  Chi-square failed: {e}")

# Overall test: Combine across prefixes with stratified analysis
print("\n" + "=" * 70)
print("STRATIFIED ANALYSIS (Cochran-Mantel-Haenszel approach)")
print("=" * 70)

# For each prefix stratum, compute observed vs expected section-parent associations
# Then pool across strata

# Simplified: Count how many PREFIX strata show significant section effects
significant_strata = 0
total_strata = 0

for prefix in section_parent_prefix[list(section_parent_prefix.keys())[0]].keys():
    all_parents = Counter()
    for section in section_parent_prefix:
        all_parents.update(section_parent_prefix[section][prefix])

    if sum(all_parents.values()) < 30:
        continue

    total_strata += 1

    # Quick chi-square
    sections = sorted(section_parent_prefix.keys())
    top_parents = [p for p, _ in all_parents.most_common(6)]

    contingency = []
    for section in sections:
        row = [section_parent_prefix[section][prefix].get(p, 0) for p in top_parents]
        contingency.append(row)

    matrix = np.array(contingency)

    # Filter zeros
    col_nonzero = matrix.sum(axis=0) > 0
    row_nonzero = matrix.sum(axis=1) > 0
    matrix = matrix[row_nonzero][:, col_nonzero]

    if matrix.shape[0] >= 2 and matrix.shape[1] >= 2:
        try:
            chi2, p, _, _ = stats.chi2_contingency(matrix)
            if p < 0.05:
                significant_strata += 1
        except:
            pass

print(f"\nPREFIX strata with significant section differences: {significant_strata}/{total_strata}")
expected_by_chance = total_strata * 0.05
print(f"Expected by chance (5%): {expected_by_chance:.1f}")

if significant_strata > expected_by_chance * 2:
    print(f"\n=> SECTION EFFECTS SURVIVE PREFIX CONTROL")
    print(f"   Domain-specific operator preferences are REAL, not PREFIX artifacts")
else:
    print(f"\n=> SECTION EFFECTS LARGELY EXPLAINED BY PREFIX")
    print(f"   Domain preferences may be downstream of PREFIX-section associations")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
PREFIX CONTROL TEST:

The expert noted that section-specific operator preferences might be
downstream of PREFIX-section associations (C374, C423).

Results:
- {significant_strata}/{total_strata} PREFIX strata show significant section differences
- Expected by chance: {expected_by_chance:.1f}

If section effects survive within PREFIX strata, the domain-specific
operator preferences are an independent phenomenon, not just PREFIX confounding.
""")
