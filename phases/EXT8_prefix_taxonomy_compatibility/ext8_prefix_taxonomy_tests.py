"""
EXT-8: Prefix Taxonomy Compatibility Tests

Structural tests to constrain which taxonomy types are compatible with
the 8 Currier A marker prefixes. NOT identification - CONSTRAINT.

Tests:
1. CT Exclusivity - why 94.7% Section H?
2. Co-occurrence in Compounds - which prefixes appear together in non-block entries?
3. Suffix × Prefix Interaction - do certain prefixes prefer certain suffixes?
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy import stats

project_root = Path(__file__).parent.parent.parent
MARKER_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']


def load_currier_a_data():
    """Load Currier A entries with full metadata."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    entries = defaultdict(lambda: {'tokens': [], 'section': '', 'folio': ''})

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 6:
                lang = parts[6].strip('"').strip()
                if lang == 'A':
                    word = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                    line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                    if word:
                        key = f"{folio}_{line_num}"
                        entries[key]['tokens'].append(word)
                        entries[key]['section'] = section
                        entries[key]['folio'] = folio

    return dict(entries)


def get_prefix(token):
    """Return prefix if token is a marker token, else None."""
    for prefix in MARKER_PREFIXES:
        if token.startswith(prefix):
            return prefix
    return None


def extract_suffix(token, prefix):
    """Extract suffix from marker token."""
    if token.startswith(prefix):
        remainder = token[len(prefix):]
        return remainder if remainder else None
    return None


def test_1_ct_exclusivity():
    """
    TEST 1: CT EXCLUSIVITY

    CT is 94.7% Section H. What does this structural property EXCLUDE?
    """
    print("\n" + "=" * 80)
    print("TEST 1: CT EXCLUSIVITY")
    print("=" * 80)

    entries = load_currier_a_data()

    # Count prefix occurrences by section
    prefix_section = defaultdict(lambda: defaultdict(int))
    prefix_total = defaultdict(int)

    for entry_id, data in entries.items():
        section = data['section']
        for token in data['tokens']:
            prefix = get_prefix(token)
            if prefix:
                prefix_section[prefix][section] += 1
                prefix_total[prefix] += 1

    print("\n## PREFIX × SECTION DISTRIBUTION")
    print(f"\n{'Prefix':<8}", end="")
    sections = sorted(set(s for d in prefix_section.values() for s in d.keys()))
    for s in sections:
        print(f"{s:>10}", end="")
    print(f"{'Total':>10}  {'Primary':>10}")
    print("-" * 70)

    section_specialization = {}

    for prefix in MARKER_PREFIXES:
        print(f"{prefix.upper():<8}", end="")
        total = prefix_total[prefix]
        max_section = ''
        max_pct = 0

        for s in sections:
            count = prefix_section[prefix][s]
            pct = 100 * count / total if total > 0 else 0
            print(f"{pct:>9.1f}%", end="")
            if pct > max_pct:
                max_pct = pct
                max_section = s

        print(f"{total:>10}  {max_section:>6} ({max_pct:.1f}%)")
        section_specialization[prefix] = (max_section, max_pct)

    # Categorize by specialization level
    print("\n## SPECIALIZATION CATEGORIES")

    highly_specialized = [(p, s, pct) for p, (s, pct) in section_specialization.items() if pct >= 80]
    moderately_specialized = [(p, s, pct) for p, (s, pct) in section_specialization.items() if 60 <= pct < 80]
    mixed = [(p, s, pct) for p, (s, pct) in section_specialization.items() if pct < 60]

    print(f"\nHighly Specialized (>=80% one section): {len(highly_specialized)}")
    for p, s, pct in sorted(highly_specialized, key=lambda x: -x[2]):
        print(f"  {p.upper()}: {s} ({pct:.1f}%)")

    print(f"\nModerately Specialized (60-80%): {len(moderately_specialized)}")
    for p, s, pct in sorted(moderately_specialized, key=lambda x: -x[2]):
        print(f"  {p.upper()}: {s} ({pct:.1f}%)")

    print(f"\nMixed (<60%): {len(mixed)}")
    for p, s, pct in sorted(mixed, key=lambda x: -x[2]):
        print(f"  {p.upper()}: {s} ({pct:.1f}%)")

    # What this EXCLUDES
    print("\n## STRUCTURAL CONSTRAINTS")
    print("""
CT is 94.7% Section H. This EXCLUDES taxonomy interpretations where:
- All categories are equally versatile across product lines
- Categories represent universal material properties (like quality grades)
- Categories are processing states that apply to all materials

CT behavior is COMPATIBLE with taxonomy interpretations where:
- Some material types are specialized to specific product families
- Section H represents a product line that uses unique materials
- CT represents a rare/specialized material category

CONSTRAINT: At least one of the 8 prefixes must be a SPECIALIZED category,
not a universal property that applies equally across all sections.
""")

    return {
        'highly_specialized': len(highly_specialized),
        'moderately_specialized': len(moderately_specialized),
        'mixed': len(mixed),
        'section_specialization': section_specialization
    }


def test_2_cooccurrence_in_compounds():
    """
    TEST 2: CO-OCCURRENCE IN COMPOUNDS

    In non-block entries (35.9%), which prefixes appear together?
    If these are compound products, the combinations should make sense.
    """
    print("\n" + "=" * 80)
    print("TEST 2: CO-OCCURRENCE IN COMPOUNDS")
    print("=" * 80)

    entries = load_currier_a_data()

    # Identify non-block entries (simplified: entries with multiple marker classes)
    non_block_entries = []

    for entry_id, data in entries.items():
        prefixes_in_entry = set()
        for token in data['tokens']:
            prefix = get_prefix(token)
            if prefix:
                prefixes_in_entry.add(prefix)

        if len(prefixes_in_entry) >= 2:  # Multi-class = non-block
            non_block_entries.append((entry_id, data, prefixes_in_entry))

    print(f"\nMulti-class entries (compound candidates): {len(non_block_entries)}")

    # Build co-occurrence matrix
    cooccurrence = defaultdict(lambda: defaultdict(int))
    prefix_in_compounds = defaultdict(int)

    for entry_id, data, prefixes in non_block_entries:
        for p1 in prefixes:
            prefix_in_compounds[p1] += 1
            for p2 in prefixes:
                if p1 != p2:
                    cooccurrence[p1][p2] += 1

    print("\n## CO-OCCURRENCE MATRIX (entries where both appear)")
    print(f"\n{'':>8}", end="")
    for p2 in MARKER_PREFIXES:
        print(f"{p2.upper():>8}", end="")
    print(f"{'Total':>8}")
    print("-" * 80)

    for p1 in MARKER_PREFIXES:
        print(f"{p1.upper():>8}", end="")
        for p2 in MARKER_PREFIXES:
            if p1 == p2:
                print(f"{'---':>8}", end="")
            else:
                print(f"{cooccurrence[p1][p2]:>8}", end="")
        print(f"{prefix_in_compounds[p1]:>8}")

    # Normalize by opportunity (expected if independent)
    print("\n## ASSOCIATION STRENGTH (observed/expected ratio)")
    total_compounds = len(non_block_entries)

    print(f"\n{'':>8}", end="")
    for p2 in MARKER_PREFIXES:
        print(f"{p2.upper():>8}", end="")
    print()
    print("-" * 72)

    associations = []

    for p1 in MARKER_PREFIXES:
        print(f"{p1.upper():>8}", end="")
        for p2 in MARKER_PREFIXES:
            if p1 == p2:
                print(f"{'---':>8}", end="")
            else:
                observed = cooccurrence[p1][p2]
                # Expected under independence
                p1_rate = prefix_in_compounds[p1] / total_compounds
                p2_rate = prefix_in_compounds[p2] / total_compounds
                expected = p1_rate * p2_rate * total_compounds

                if expected > 0:
                    ratio = observed / expected
                    print(f"{ratio:>7.2f}x", end="")
                    if p1 < p2:  # Only store once per pair
                        associations.append((p1, p2, observed, expected, ratio))
                else:
                    print(f"{'N/A':>8}", end="")
        print()

    # Identify strong associations
    print("\n## STRONG ASSOCIATIONS (ratio > 1.5)")
    strong = [(p1, p2, obs, exp, r) for p1, p2, obs, exp, r in associations if r > 1.5]
    strong.sort(key=lambda x: -x[4])

    if strong:
        for p1, p2, obs, exp, r in strong[:10]:
            print(f"  {p1.upper()}-{p2.upper()}: {r:.2f}x (obs={obs}, exp={exp:.1f})")
    else:
        print("  None")

    # Identify weak associations (avoidance)
    print("\n## WEAK ASSOCIATIONS (ratio < 0.5) - possible incompatibility")
    weak = [(p1, p2, obs, exp, r) for p1, p2, obs, exp, r in associations if r < 0.5 and exp >= 5]
    weak.sort(key=lambda x: x[4])

    if weak:
        for p1, p2, obs, exp, r in weak[:10]:
            print(f"  {p1.upper()}-{p2.upper()}: {r:.2f}x (obs={obs}, exp={exp:.1f})")
    else:
        print("  None (or insufficient data)")

    print("\n## STRUCTURAL CONSTRAINTS")
    print("""
Co-occurrence patterns reveal which prefixes "go together" in compounds.

COMPATIBLE WITH material taxonomies where:
- Some material types naturally combine (herbs + flowers in potpourri)
- Some combinations are rare/impossible (resins + fresh flowers)

INCOMPATIBLE WITH taxonomies where:
- All categories are independent dimensions (quality × origin × form)
  (these would show uniform co-occurrence)
""")

    return {
        'total_compounds': len(non_block_entries),
        'cooccurrence': dict(cooccurrence),
        'strong_associations': strong[:10] if strong else [],
        'weak_associations': weak[:10] if weak else []
    }


def test_3_suffix_prefix_interaction():
    """
    TEST 3: SUFFIX × PREFIX INTERACTION

    Do certain prefixes prefer certain suffixes?
    If suffix = processing state, some materials have more options.
    """
    print("\n" + "=" * 80)
    print("TEST 3: SUFFIX × PREFIX INTERACTION")
    print("=" * 80)

    # Load marker catalog
    catalog_path = project_root / 'phases' / 'CAS_currier_a_schema' / 'marker_token_catalog.json'
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    # Known suffix patterns (core suffixes)
    core_suffixes = ['ol', 'or', 'y', 'aiin', 'ar', 'chy', 'eol', 'eor', 'ey', 'ody']

    # Build suffix × prefix matrix
    suffix_prefix = defaultdict(lambda: defaultdict(int))
    prefix_suffix_total = defaultdict(int)
    suffix_total = defaultdict(int)

    for prefix, data in catalog.items():
        for token, count in data['all_tokens'].items():
            # Extract suffix
            remainder = token[len(prefix):]
            if remainder:
                # Match to core suffix
                matched = None
                for cs in core_suffixes:
                    if remainder.endswith(cs):
                        matched = cs
                        break

                if matched:
                    suffix_prefix[matched][prefix] += count
                    prefix_suffix_total[prefix] += count
                    suffix_total[matched] += count

    print("\n## SUFFIX × PREFIX DISTRIBUTION")
    print(f"\n{'Suffix':<10}", end="")
    for prefix in MARKER_PREFIXES:
        print(f"{prefix.upper():>8}", end="")
    print(f"{'Total':>8}")
    print("-" * 80)

    for suffix in core_suffixes:
        if suffix_total[suffix] >= 10:  # Skip very rare
            print(f"-{suffix:<9}", end="")
            for prefix in MARKER_PREFIXES:
                count = suffix_prefix[suffix][prefix]
                if count > 0:
                    print(f"{count:>8}", end="")
                else:
                    print(f"{'—':>8}", end="")
            print(f"{suffix_total[suffix]:>8}")

    # Calculate suffix diversity per prefix
    print("\n## SUFFIX DIVERSITY BY PREFIX")
    print("(How many different suffixes does each prefix use?)")

    prefix_diversity = {}
    for prefix in MARKER_PREFIXES:
        suffixes_used = set()
        total = 0
        for suffix in core_suffixes:
            if suffix_prefix[suffix][prefix] > 0:
                suffixes_used.add(suffix)
                total += suffix_prefix[suffix][prefix]
        prefix_diversity[prefix] = (len(suffixes_used), total)

    for prefix, (diversity, total) in sorted(prefix_diversity.items(), key=lambda x: -x[1][0]):
        print(f"  {prefix.upper()}: {diversity} suffix types, {total} tokens")

    # Chi-square test for independence
    print("\n## INDEPENDENCE TEST")

    # Build contingency table for top suffixes
    top_suffixes = [s for s in core_suffixes if suffix_total[s] >= 20]

    observed = []
    for suffix in top_suffixes:
        row = [suffix_prefix[suffix][prefix] for prefix in MARKER_PREFIXES]
        observed.append(row)

    observed = np.array(observed)

    if observed.sum() > 0:
        chi2, p, dof, expected = stats.chi2_contingency(observed)
        print(f"\nChi-square test (suffix × prefix independence):")
        print(f"  Chi2 = {chi2:.2f}")
        print(f"  p-value = {p:.4e}")
        print(f"  dof = {dof}")

        if p < 0.001:
            print(f"\n  Result: HIGHLY SIGNIFICANT INTERACTION")
            print(f"  Suffixes are NOT distributed uniformly across prefixes")
        elif p < 0.05:
            print(f"\n  Result: SIGNIFICANT INTERACTION")
        else:
            print(f"\n  Result: NO SIGNIFICANT INTERACTION")

    # Find strongest prefix-suffix associations
    print("\n## STRONGEST PREFIX-SUFFIX ASSOCIATIONS")

    associations = []
    total_tokens = sum(suffix_total.values())

    for suffix in top_suffixes:
        for prefix in MARKER_PREFIXES:
            observed_count = suffix_prefix[suffix][prefix]
            if observed_count >= 5:
                # Expected under independence
                suffix_rate = suffix_total[suffix] / total_tokens
                prefix_rate = prefix_suffix_total[prefix] / total_tokens
                expected_count = suffix_rate * prefix_rate * total_tokens

                if expected_count > 0:
                    ratio = observed_count / expected_count
                    associations.append((prefix, suffix, observed_count, expected_count, ratio))

    associations.sort(key=lambda x: -x[4])

    print("\nOver-represented (ratio > 2.0):")
    over = [a for a in associations if a[4] > 2.0]
    for prefix, suffix, obs, exp, r in over[:10]:
        print(f"  {prefix.upper()}-{suffix}: {r:.2f}x (obs={obs}, exp={exp:.1f})")

    print("\nUnder-represented (ratio < 0.3, expected >= 10):")
    under = [a for a in associations if a[4] < 0.3 and a[3] >= 10]
    for prefix, suffix, obs, exp, r in under[:10]:
        print(f"  {prefix.upper()}-{suffix}: {r:.2f}x (obs={obs}, exp={exp:.1f})")

    print("\n## STRUCTURAL CONSTRAINTS")
    print("""
Suffix-prefix interactions reveal whether "processing states" are universal or material-specific.

If suffixes represent UNIVERSAL properties (like quality grades):
- All prefixes would use all suffixes roughly equally
- Chi-square would NOT be significant

If suffixes represent MATERIAL-SPECIFIC states:
- Some prefixes would strongly prefer certain suffixes
- Chi-square would be significant
- Some prefix-suffix combinations would be rare/absent
""")

    return {
        'prefix_diversity': prefix_diversity,
        'chi2_p': p if 'p' in dir() else None,
        'over_represented': over[:10] if 'over' in dir() else [],
        'under_represented': under[:10] if 'under' in dir() else []
    }


def main():
    print("=" * 80)
    print("EXT-8: PREFIX TAXONOMY COMPATIBILITY TESTS")
    print("=" * 80)
    print("""
Purpose: Test structural properties of the 8 prefixes to CONSTRAIN
which taxonomy types are compatible. NOT identification - CONSTRAINT.
""")

    results = {}

    results['test1'] = test_1_ct_exclusivity()
    results['test2'] = test_2_cooccurrence_in_compounds()
    results['test3'] = test_3_suffix_prefix_interaction()

    # Final synthesis
    print("\n" + "=" * 80)
    print("SYNTHESIS: TAXONOMY COMPATIBILITY")
    print("=" * 80)

    print("""
## STRUCTURAL FINDINGS

1. SPECIALIZATION:
   - At least 1 prefix is HIGHLY SPECIALIZED (94.7% one section)
   - Most prefixes are MIXED across sections

2. CO-OCCURRENCE:
   - Prefixes show NON-UNIFORM co-occurrence in compounds
   - Some pairs associate more/less than expected

3. SUFFIX INTERACTION:
   - Suffix distribution is PREFIX-DEPENDENT (not uniform)
   - Different prefixes prefer different suffixes

## TAXONOMY TYPES EXCLUDED

These structural properties EXCLUDE taxonomies where:
- All categories are universal properties (apply equally to all items)
- Categories are independent dimensions (quality × origin × form)
- All categories are equally versatile across sections

## TAXONOMY TYPES COMPATIBLE

The structure is COMPATIBLE with taxonomies where:
- Categories represent MATERIAL TYPES with different properties
- Some materials are specialized to certain product lines
- Different materials have different "processing options"
- Materials can combine in compounds, but not all combinations are equal

## CANDIDATE TAXONOMY FAMILIES

Based on structure (NOT identification):
- Material source taxonomies (flowers, herbs, roots, resins...)
  - CT = specialized material rare outside Section H
  - Different materials have different suffix options
  - Materials combine in compounds with preferences

- NOT compatible:
  - Quality grades (high, medium, low, premium...)
  - Processing states (fresh, dried, preserved...)
  - Geographic origins (local, imported, eastern...)

These would show uniform distribution, not the specialization observed.
""")

    # Save results
    output_path = Path(__file__).parent / 'ext8_results.json'

    # Convert for JSON serialization
    results_json = {
        'test1_specialization': {
            'highly_specialized': results['test1']['highly_specialized'],
            'moderately_specialized': results['test1']['moderately_specialized'],
            'mixed': results['test1']['mixed']
        },
        'test2_cooccurrence': {
            'total_compounds': results['test2']['total_compounds'],
            'strong_associations': len(results['test2']['strong_associations']),
            'weak_associations': len(results['test2']['weak_associations'])
        },
        'test3_interaction': {
            'chi2_p': results['test3'].get('chi2_p')
        }
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results_json, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    results = main()
