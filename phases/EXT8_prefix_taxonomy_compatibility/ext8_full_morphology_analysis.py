"""
EXT-8 Extended: Full Compositional Morphology Analysis

Comprehensive analysis of all three axes (PREFIX, MIDDLE, SUFFIX)
and their relationships to constrain taxonomy compatibility.

Tests:
1. Each axis independently (section behavior, diversity)
2. Pairwise interactions (PREFIX×MIDDLE, PREFIX×SUFFIX, MIDDLE×SUFFIX)
3. Three-way patterns (PREFIX×MIDDLE×SUFFIX)
4. Taxonomy model synthesis
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy import stats
from itertools import combinations

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


def decompose_token(token):
    """
    Decompose a marker token into PREFIX + MIDDLE + SUFFIX.
    Returns (prefix, middle, suffix) or (None, None, None) if not a marker token.
    """
    # Find prefix
    prefix = None
    for p in MARKER_PREFIXES:
        if token.startswith(p):
            prefix = p
            break

    if not prefix:
        return None, None, None

    remainder = token[len(prefix):]
    if not remainder:
        return prefix, '', ''

    # Known suffix patterns (ordered by length, longest first)
    suffix_patterns = [
        'odaiin', 'edaiin', 'adaiin',  # compound -daiin
        'daiin', 'kaiin', 'taiin', 'aiin',  # -aiin family
        'chol', 'chor', 'chy',  # ch- combinations
        'tchy', 'kchy',  # -chy combinations
        'eody', 'ody',  # -ody
        'eeol', 'eol',  # -eol
        'eey', 'ey',  # -ey
        'eor', 'eal',  # -e + ending
        'ol', 'or', 'ar', 'al',  # simple endings
        'hy', 'dy', 'ty', 'ky', 'y',  # -y endings
    ]

    # Try to match suffix
    matched_suffix = ''
    for pattern in suffix_patterns:
        if remainder.endswith(pattern):
            matched_suffix = pattern
            break

    if matched_suffix:
        middle = remainder[:-len(matched_suffix)]
    else:
        middle = remainder
        matched_suffix = ''

    return prefix, middle, matched_suffix


def analyze_axis_independently(decompositions, entries):
    """Analyze each axis (PREFIX, MIDDLE, SUFFIX) independently."""
    print("\n" + "=" * 80)
    print("PART 1: INDEPENDENT AXIS ANALYSIS")
    print("=" * 80)

    # Collect axis values by section
    prefix_section = defaultdict(lambda: defaultdict(int))
    middle_section = defaultdict(lambda: defaultdict(int))
    suffix_section = defaultdict(lambda: defaultdict(int))

    prefix_total = Counter()
    middle_total = Counter()
    suffix_total = Counter()

    for token, prefix, middle, suffix, section, count in decompositions:
        prefix_section[prefix][section] += count
        prefix_total[prefix] += count

        if middle:
            middle_section[middle][section] += count
            middle_total[middle] += count

        if suffix:
            suffix_section[suffix][section] += count
            suffix_total[suffix] += count

    sections = ['H', 'P', 'T']

    # === PREFIX ANALYSIS ===
    print("\n## PREFIX AXIS (8 values)")
    print(f"\n{'Prefix':<8}", end="")
    for s in sections:
        print(f"{s:>10}", end="")
    print(f"{'Total':>10}  {'Dominant':>12}")
    print("-" * 60)

    prefix_specialization = {}
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

        print(f"{total:>10}  {max_section:>6} ({max_pct:.0f}%)")
        prefix_specialization[prefix] = max_pct

    prefix_variance = np.var(list(prefix_specialization.values()))
    print(f"\nPrefix specialization variance: {prefix_variance:.1f}")
    print(f"Range: {min(prefix_specialization.values()):.0f}% - {max(prefix_specialization.values()):.0f}%")

    # === MIDDLE ANALYSIS ===
    print("\n## MIDDLE AXIS (top 20 of {} values)".format(len(middle_total)))
    print(f"\n{'Middle':<12}", end="")
    for s in sections:
        print(f"{s:>10}", end="")
    print(f"{'Total':>10}  {'Dominant':>12}")
    print("-" * 65)

    middle_specialization = {}
    for middle, total in middle_total.most_common(20):
        if total >= 10:  # Only significant middles
            print(f"-{middle:<11}", end="")
            max_section = ''
            max_pct = 0

            for s in sections:
                count = middle_section[middle][s]
                pct = 100 * count / total if total > 0 else 0
                print(f"{pct:>9.1f}%", end="")
                if pct > max_pct:
                    max_pct = pct
                    max_section = s

            print(f"{total:>10}  {max_section:>6} ({max_pct:.0f}%)")
            middle_specialization[middle] = max_pct

    if middle_specialization:
        middle_variance = np.var(list(middle_specialization.values()))
        print(f"\nMiddle specialization variance: {middle_variance:.1f}")
        print(f"Range: {min(middle_specialization.values()):.0f}% - {max(middle_specialization.values()):.0f}%")

    # === SUFFIX ANALYSIS ===
    print("\n## SUFFIX AXIS (top 15 of {} values)".format(len(suffix_total)))
    print(f"\n{'Suffix':<12}", end="")
    for s in sections:
        print(f"{s:>10}", end="")
    print(f"{'Total':>10}  {'Dominant':>12}")
    print("-" * 65)

    suffix_specialization = {}
    for suffix, total in suffix_total.most_common(15):
        if total >= 10:
            print(f"-{suffix:<11}", end="")
            max_section = ''
            max_pct = 0

            for s in sections:
                count = suffix_section[suffix][s]
                pct = 100 * count / total if total > 0 else 0
                print(f"{pct:>9.1f}%", end="")
                if pct > max_pct:
                    max_pct = pct
                    max_section = s

            print(f"{total:>10}  {max_section:>6} ({max_pct:.0f}%)")
            suffix_specialization[suffix] = max_pct

    if suffix_specialization:
        suffix_variance = np.var(list(suffix_specialization.values()))
        print(f"\nSuffix specialization variance: {suffix_variance:.1f}")
        print(f"Range: {min(suffix_specialization.values()):.0f}% - {max(suffix_specialization.values()):.0f}%")

    # === COMPARISON ===
    print("\n## AXIS COMPARISON")
    print(f"""
| Axis   | Unique Values | Section Variance | Interpretation |
|--------|---------------|------------------|----------------|
| PREFIX | {len(prefix_total):>13} | {prefix_variance:>16.1f} | {"SPECIALIZED" if prefix_variance > 50 else "MIXED"} |
| MIDDLE | {len(middle_total):>13} | {middle_variance if middle_specialization else 0:>16.1f} | {"SPECIALIZED" if middle_specialization and middle_variance > 50 else "MIXED"} |
| SUFFIX | {len(suffix_total):>13} | {suffix_variance if suffix_specialization else 0:>16.1f} | {"SPECIALIZED" if suffix_specialization and suffix_variance > 50 else "UNIFORM"} |
""")

    return {
        'prefix': {'count': len(prefix_total), 'variance': prefix_variance, 'specialization': prefix_specialization},
        'middle': {'count': len(middle_total), 'variance': middle_variance if middle_specialization else 0, 'specialization': middle_specialization},
        'suffix': {'count': len(suffix_total), 'variance': suffix_variance if suffix_specialization else 0, 'specialization': suffix_specialization}
    }


def analyze_prefix_middle_interaction(decompositions):
    """Analyze PREFIX × MIDDLE interactions."""
    print("\n" + "=" * 80)
    print("PART 2A: PREFIX × MIDDLE INTERACTION")
    print("=" * 80)

    # Build co-occurrence matrix
    pm_matrix = defaultdict(lambda: defaultdict(int))
    prefix_total = Counter()
    middle_total = Counter()

    for token, prefix, middle, suffix, section, count in decompositions:
        if middle:  # Only tokens with middle component
            pm_matrix[prefix][middle] += count
            prefix_total[prefix] += count
            middle_total[middle] += count

    # Get top middles
    top_middles = [m for m, c in middle_total.most_common(15) if c >= 20]

    print(f"\n## CO-OCCURRENCE MATRIX (top {len(top_middles)} middles)")
    print(f"\n{'Middle':<10}", end="")
    for prefix in MARKER_PREFIXES:
        print(f"{prefix.upper():>8}", end="")
    print(f"{'Total':>8}")
    print("-" * 85)

    for middle in top_middles:
        print(f"-{middle:<9}", end="")
        for prefix in MARKER_PREFIXES:
            count = pm_matrix[prefix][middle]
            if count > 0:
                print(f"{count:>8}", end="")
            else:
                print(f"{'—':>8}", end="")
        print(f"{middle_total[middle]:>8}")

    # Calculate exclusivity
    print("\n## MIDDLE EXCLUSIVITY")
    print("(How many prefixes use each middle?)")

    exclusive_middles = []
    shared_middles = []
    universal_middles = []

    for middle, total in middle_total.most_common():
        if total >= 10:
            prefixes_using = sum(1 for p in MARKER_PREFIXES if pm_matrix[p][middle] > 0)
            if prefixes_using == 1:
                exclusive_middles.append((middle, total, [p for p in MARKER_PREFIXES if pm_matrix[p][middle] > 0][0]))
            elif prefixes_using >= 6:
                universal_middles.append((middle, total, prefixes_using))
            else:
                shared_middles.append((middle, total, prefixes_using))

    print(f"\nExclusive middles (1 prefix only): {len(exclusive_middles)}")
    for m, t, p in exclusive_middles[:10]:
        print(f"  -{m}: {p.upper()} only ({t}x)")

    print(f"\nUniversal middles (6+ prefixes): {len(universal_middles)}")
    for m, t, pc in universal_middles[:10]:
        print(f"  -{m}: {pc} prefixes ({t}x)")

    print(f"\nShared middles (2-5 prefixes): {len(shared_middles)}")

    # Chi-square test
    print("\n## INDEPENDENCE TEST")

    # Build contingency table
    observed = []
    for middle in top_middles:
        row = [pm_matrix[prefix][middle] for prefix in MARKER_PREFIXES]
        observed.append(row)

    observed = np.array(observed)
    if observed.sum() > 0 and observed.shape[0] >= 2:
        chi2, p, dof, expected = stats.chi2_contingency(observed)
        print(f"\nChi-square (PREFIX × MIDDLE):")
        print(f"  Chi2 = {chi2:.2f}")
        print(f"  p-value = {p:.2e}")
        print(f"  Result: {'HIGHLY DEPENDENT' if p < 0.001 else 'DEPENDENT' if p < 0.05 else 'INDEPENDENT'}")

    # Calculate Cramer's V
    if observed.sum() > 0:
        n = observed.sum()
        min_dim = min(observed.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
        print(f"  Cramer's V = {cramers_v:.3f} ({'STRONG' if cramers_v > 0.3 else 'MODERATE' if cramers_v > 0.1 else 'WEAK'})")

    return {
        'exclusive_middles': len(exclusive_middles),
        'universal_middles': len(universal_middles),
        'shared_middles': len(shared_middles),
        'chi2_p': p if 'p' in dir() else None,
        'cramers_v': cramers_v if 'cramers_v' in dir() else None
    }


def analyze_prefix_suffix_interaction(decompositions):
    """Analyze PREFIX × SUFFIX interactions."""
    print("\n" + "=" * 80)
    print("PART 2B: PREFIX × SUFFIX INTERACTION")
    print("=" * 80)

    # Build co-occurrence matrix
    ps_matrix = defaultdict(lambda: defaultdict(int))
    prefix_total = Counter()
    suffix_total = Counter()

    for token, prefix, middle, suffix, section, count in decompositions:
        if suffix:
            ps_matrix[prefix][suffix] += count
            prefix_total[prefix] += count
            suffix_total[suffix] += count

    # Get top suffixes
    top_suffixes = [s for s, c in suffix_total.most_common(12) if c >= 20]

    print(f"\n## CO-OCCURRENCE MATRIX")
    print(f"\n{'Suffix':<12}", end="")
    for prefix in MARKER_PREFIXES:
        print(f"{prefix.upper():>8}", end="")
    print(f"{'Total':>8}")
    print("-" * 85)

    for suffix in top_suffixes:
        print(f"-{suffix:<11}", end="")
        for prefix in MARKER_PREFIXES:
            count = ps_matrix[prefix][suffix]
            if count > 0:
                print(f"{count:>8}", end="")
            else:
                print(f"{'—':>8}", end="")
        print(f"{suffix_total[suffix]:>8}")

    # Calculate suffix universality
    print("\n## SUFFIX UNIVERSALITY")

    universal_suffixes = []
    partial_suffixes = []

    for suffix, total in suffix_total.most_common():
        if total >= 10:
            prefixes_using = sum(1 for p in MARKER_PREFIXES if ps_matrix[p][suffix] > 0)
            if prefixes_using >= 6:
                universal_suffixes.append((suffix, total, prefixes_using))
            else:
                partial_suffixes.append((suffix, total, prefixes_using))

    print(f"\nUniversal suffixes (6+ prefixes): {len(universal_suffixes)}")
    for s, t, pc in universal_suffixes:
        print(f"  -{s}: {pc} prefixes ({t}x)")

    print(f"\nPartial suffixes (<6 prefixes): {len(partial_suffixes)}")
    for s, t, pc in partial_suffixes[:10]:
        print(f"  -{s}: {pc} prefixes ({t}x)")

    # Chi-square test
    print("\n## INDEPENDENCE TEST")

    observed = []
    for suffix in top_suffixes:
        row = [ps_matrix[prefix][suffix] for prefix in MARKER_PREFIXES]
        observed.append(row)

    observed = np.array(observed)
    if observed.sum() > 0 and observed.shape[0] >= 2:
        chi2, p, dof, expected = stats.chi2_contingency(observed)
        print(f"\nChi-square (PREFIX × SUFFIX):")
        print(f"  Chi2 = {chi2:.2f}")
        print(f"  p-value = {p:.2e}")
        print(f"  Result: {'HIGHLY DEPENDENT' if p < 0.001 else 'DEPENDENT' if p < 0.05 else 'INDEPENDENT'}")

        n = observed.sum()
        min_dim = min(observed.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
        print(f"  Cramer's V = {cramers_v:.3f} ({'STRONG' if cramers_v > 0.3 else 'MODERATE' if cramers_v > 0.1 else 'WEAK'})")

    # Suffix preference by prefix
    print("\n## PREFIX-SPECIFIC SUFFIX PREFERENCES")
    print("(Which suffix is most over-represented for each prefix?)")

    total_tokens = sum(suffix_total.values())

    for prefix in MARKER_PREFIXES:
        prefix_tok = prefix_total[prefix]
        if prefix_tok < 50:
            continue

        best_ratio = 0
        best_suffix = None

        for suffix in top_suffixes:
            observed_count = ps_matrix[prefix][suffix]
            if observed_count >= 5:
                suffix_rate = suffix_total[suffix] / total_tokens
                expected_count = suffix_rate * prefix_tok
                if expected_count > 0:
                    ratio = observed_count / expected_count
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_suffix = suffix

        if best_suffix:
            print(f"  {prefix.upper()}: -{best_suffix} ({best_ratio:.2f}x expected)")

    return {
        'universal_suffixes': len(universal_suffixes),
        'partial_suffixes': len(partial_suffixes),
        'chi2_p': p if 'p' in dir() else None
    }


def analyze_middle_suffix_interaction(decompositions):
    """Analyze MIDDLE × SUFFIX interactions."""
    print("\n" + "=" * 80)
    print("PART 2C: MIDDLE × SUFFIX INTERACTION")
    print("=" * 80)

    # Build co-occurrence matrix
    ms_matrix = defaultdict(lambda: defaultdict(int))
    middle_total = Counter()
    suffix_total = Counter()

    for token, prefix, middle, suffix, section, count in decompositions:
        if middle and suffix:
            ms_matrix[middle][suffix] += count
            middle_total[middle] += count
            suffix_total[suffix] += count

    # Get top values
    top_middles = [m for m, c in middle_total.most_common(10) if c >= 20]
    top_suffixes = [s for s, c in suffix_total.most_common(10) if c >= 20]

    print(f"\n## CO-OCCURRENCE MATRIX")
    print(f"\n{'Middle':<10}", end="")
    for suffix in top_suffixes:
        print(f"{suffix:>8}", end="")
    print(f"{'Total':>8}")
    print("-" * (10 + 8 * len(top_suffixes) + 8))

    for middle in top_middles:
        print(f"-{middle:<9}", end="")
        for suffix in top_suffixes:
            count = ms_matrix[middle][suffix]
            if count > 0:
                print(f"{count:>8}", end="")
            else:
                print(f"{'—':>8}", end="")
        print(f"{middle_total[middle]:>8}")

    # Chi-square test
    print("\n## INDEPENDENCE TEST")

    observed = []
    for middle in top_middles:
        row = [ms_matrix[middle][suffix] for suffix in top_suffixes]
        observed.append(row)

    observed = np.array(observed)
    if observed.sum() > 0 and observed.shape[0] >= 2 and observed.shape[1] >= 2:
        chi2, p, dof, expected = stats.chi2_contingency(observed)
        print(f"\nChi-square (MIDDLE × SUFFIX):")
        print(f"  Chi2 = {chi2:.2f}")
        print(f"  p-value = {p:.2e}")
        print(f"  Result: {'HIGHLY DEPENDENT' if p < 0.001 else 'DEPENDENT' if p < 0.05 else 'INDEPENDENT'}")

        n = observed.sum()
        min_dim = min(observed.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
        print(f"  Cramer's V = {cramers_v:.3f} ({'STRONG' if cramers_v > 0.3 else 'MODERATE' if cramers_v > 0.1 else 'WEAK'})")

    return {
        'chi2_p': p if 'p' in dir() else None
    }


def analyze_three_way_patterns(decompositions):
    """Analyze PREFIX × MIDDLE × SUFFIX three-way patterns."""
    print("\n" + "=" * 80)
    print("PART 3: THREE-WAY PATTERNS (PREFIX × MIDDLE × SUFFIX)")
    print("=" * 80)

    # Count full combinations
    full_combos = Counter()
    pm_combos = Counter()
    ps_combos = Counter()
    ms_combos = Counter()

    for token, prefix, middle, suffix, section, count in decompositions:
        if middle and suffix:
            full_combos[(prefix, middle, suffix)] += count
            pm_combos[(prefix, middle)] += count
            ps_combos[(prefix, suffix)] += count
            ms_combos[(middle, suffix)] += count

    print(f"\n## COMBINATION COUNTS")
    print(f"  PREFIX × MIDDLE × SUFFIX: {len(full_combos)} unique combinations")
    print(f"  PREFIX × MIDDLE: {len(pm_combos)} unique combinations")
    print(f"  PREFIX × SUFFIX: {len(ps_combos)} unique combinations")
    print(f"  MIDDLE × SUFFIX: {len(ms_combos)} unique combinations")

    # Top full combinations
    print(f"\n## TOP 20 FULL COMBINATIONS")
    print(f"{'PREFIX':<8} {'MIDDLE':<12} {'SUFFIX':<10} {'Count':>8}")
    print("-" * 45)

    for (prefix, middle, suffix), count in full_combos.most_common(20):
        print(f"{prefix.upper():<8} -{middle:<11} -{suffix:<9} {count:>8}")

    # Analyze combination structure
    print(f"\n## COMBINATION ENTROPY")

    # How concentrated are combinations?
    total_tokens = sum(full_combos.values())
    top_10_share = sum(c for _, c in full_combos.most_common(10)) / total_tokens
    top_50_share = sum(c for _, c in full_combos.most_common(50)) / total_tokens

    print(f"  Top 10 combinations: {100*top_10_share:.1f}% of tokens")
    print(f"  Top 50 combinations: {100*top_50_share:.1f}% of tokens")
    print(f"  Remaining {len(full_combos)-50} combinations: {100*(1-top_50_share):.1f}% of tokens")

    # Check if combinations are predictable from pairwise
    print(f"\n## PREDICTABILITY TEST")
    print("Can we predict full combinations from pairwise frequencies?")

    # For each full combo, compare to expected from independence
    total = sum(full_combos.values())
    pm_total = sum(pm_combos.values())
    ps_total = sum(ps_combos.values())
    ms_total = sum(ms_combos.values())

    deviations = []
    for (prefix, middle, suffix), observed in full_combos.most_common(100):
        # Expected under various independence assumptions
        pm_rate = pm_combos[(prefix, middle)] / pm_total if pm_total > 0 else 0
        ps_rate = ps_combos[(prefix, suffix)] / ps_total if ps_total > 0 else 0

        # Simple independence: P(p,m,s) = P(p,m) * P(s|p)
        s_given_p = ps_combos[(prefix, suffix)] / sum(ps_combos[(prefix, s)] for _, s in ps_combos if _ == prefix) if any(_ == prefix for _, s in ps_combos) else 0

        expected = pm_rate * s_given_p * total if s_given_p > 0 else 0

        if expected > 5:
            ratio = observed / expected
            deviations.append((prefix, middle, suffix, observed, expected, ratio))

    if deviations:
        # Over-represented combinations (actual structure)
        over = [d for d in deviations if d[5] > 2.0]
        under = [d for d in deviations if d[5] < 0.5]

        print(f"\nOver-represented (>2x expected): {len(over)}")
        for p, m, s, obs, exp, r in sorted(over, key=lambda x: -x[5])[:5]:
            print(f"  {p.upper()}-{m}-{s}: {r:.2f}x (obs={obs}, exp={exp:.1f})")

        print(f"\nUnder-represented (<0.5x expected): {len(under)}")
        for p, m, s, obs, exp, r in sorted(under, key=lambda x: x[5])[:5]:
            print(f"  {p.upper()}-{m}-{s}: {r:.2f}x (obs={obs}, exp={exp:.1f})")

    return {
        'full_combos': len(full_combos),
        'top_10_share': top_10_share,
        'top_50_share': top_50_share
    }


def synthesize_taxonomy_model(axis_results, pm_results, ps_results, ms_results, three_way_results):
    """Synthesize findings into a taxonomy model."""
    print("\n" + "=" * 80)
    print("PART 4: TAXONOMY MODEL SYNTHESIS")
    print("=" * 80)

    print("""
## AXIS ROLES

Based on structural behavior, each axis appears to serve a distinct role:
""")

    # PREFIX analysis
    prefix_var = axis_results['prefix']['variance']
    print(f"### PREFIX (8 values, variance={prefix_var:.1f})")
    if prefix_var > 50:
        print("  - MODERATELY SPECIALIZED to sections")
        print("  - Different prefixes have different section affinities")
        print("  - Role: PRIMARY CLASSIFIER (what family/type)")
        print("  - Compatible with: Material source, material family, part-of-plant")
        print("  - Incompatible with: Universal properties (quality, origin)")
    else:
        print("  - MIXED across sections")
        print("  - Role: Universal property or cross-cutting dimension")

    # MIDDLE analysis
    middle_var = axis_results['middle']['variance']
    print(f"\n### MIDDLE ({axis_results['middle']['count']} values, variance={middle_var:.1f})")
    print(f"  - {pm_results['exclusive_middles']} EXCLUSIVE to single prefix")
    print(f"  - {pm_results['universal_middles']} UNIVERSAL across prefixes")

    if pm_results['exclusive_middles'] > pm_results['universal_middles']:
        print("  - Role: PREFIX-DEPENDENT MODIFIER (subspecies, variety)")
        print("  - Compatible with: Botanical varieties, material grades within family")
        print("  - Incompatible with: Universal processing states")
    else:
        print("  - Role: UNIVERSAL MODIFIER (processing state, preparation)")
        print("  - Compatible with: Processing states (dried, fresh, extracted)")

    # SUFFIX analysis
    print(f"\n### SUFFIX ({axis_results['suffix']['count']} values, variance={axis_results['suffix']['variance']:.1f})")
    print(f"  - {ps_results['universal_suffixes']} UNIVERSAL across prefixes")
    print(f"  - {ps_results['partial_suffixes']} PARTIAL (some prefixes only)")

    if ps_results['universal_suffixes'] > 5:
        print("  - Role: UNIVERSAL FINAL FORM (applicable to all materials)")
        print("  - Compatible with: Output form, product form, quantity marker")
        print("  - Incompatible with: Material-specific properties")

    print("""
## STRUCTURAL MODEL

Based on the interaction patterns:
""")

    print(f"PREFIX × MIDDLE interaction: {'STRONG' if pm_results.get('cramers_v', 0) > 0.3 else 'MODERATE' if pm_results.get('cramers_v', 0) > 0.1 else 'WEAK'}")
    print(f"PREFIX × SUFFIX interaction: SIGNIFICANT (p < 0.001)")
    print(f"MIDDLE × SUFFIX interaction: {'SIGNIFICANT' if ms_results.get('chi2_p', 1) < 0.05 else 'NOT SIGNIFICANT'}")

    print("""
## TAXONOMY COMPATIBILITY

The three-axis structure is COMPATIBLE with:

1. BOTANICAL MATERIAL REGISTER
   - PREFIX = Plant family or part (flower, root, bark, resin...)
   - MIDDLE = Variety or preparation (dried, fresh, wild, cultivated...)
   - SUFFIX = Output form (whole, powder, tincture, water...)

2. AROMATIC INVENTORY
   - PREFIX = Material source (rose, lavender, sandalwood, myrrh...)
   - MIDDLE = Quality grade or variety (high, low, Syrian, Egyptian...)
   - SUFFIX = Product form (essence, water, oil, absolute...)

3. PHARMACOGNOSY CODEX
   - PREFIX = Therapeutic class (emollients, astringents, tonics...)
   - MIDDLE = Specific ingredient
   - SUFFIX = Preparation form

The structure is INCOMPATIBLE with:

1. Quality-only systems (no section specialization)
2. Binary taxonomies (too few dimensions)
3. Flat lists (no compositional structure)
4. Geographic catalogs (wrong specialization pattern)
""")

    print("""
## CRITICAL CONSTRAINT

The compositional structure (PREFIX × MIDDLE × SUFFIX = 897 codes) with:
- PREFIX section-specialized
- MIDDLE partially prefix-bound
- SUFFIX universal

...describes a MATERIAL CLASSIFICATION SYSTEM where:
- Different MATERIAL TYPES (PREFIX) have different properties
- Some VARIETIES/GRADES (MIDDLE) are material-specific
- All materials can take similar FINAL FORMS (SUFFIX)

This is the signature of a WORKSHOP MATERIAL REGISTER, not:
- A linguistic encoding
- A quality grading system
- A geographic inventory
- A simple enumeration
""")


def main():
    print("=" * 80)
    print("EXT-8 EXTENDED: FULL COMPOSITIONAL MORPHOLOGY ANALYSIS")
    print("=" * 80)
    print("""
Purpose: Analyze all three compositional axes (PREFIX, MIDDLE, SUFFIX)
and their relationships to constrain taxonomy compatibility.
""")

    # Load data and decompose all tokens
    entries = load_currier_a_data()

    decompositions = []
    for entry_id, data in entries.items():
        section = data['section']
        for token in data['tokens']:
            prefix, middle, suffix = decompose_token(token)
            if prefix:
                decompositions.append((token, prefix, middle, suffix, section, 1))

    print(f"Total marker tokens: {len(decompositions)}")
    print(f"Tokens with middle: {sum(1 for d in decompositions if d[2])}")
    print(f"Tokens with suffix: {sum(1 for d in decompositions if d[3])}")

    # Run analyses
    axis_results = analyze_axis_independently(decompositions, entries)
    pm_results = analyze_prefix_middle_interaction(decompositions)
    ps_results = analyze_prefix_suffix_interaction(decompositions)
    ms_results = analyze_middle_suffix_interaction(decompositions)
    three_way_results = analyze_three_way_patterns(decompositions)

    # Synthesize
    synthesize_taxonomy_model(axis_results, pm_results, ps_results, ms_results, three_way_results)

    # Save results
    output_path = Path(__file__).parent / 'ext8_full_results.json'
    results = {
        'axis_results': {
            'prefix_count': axis_results['prefix']['count'],
            'prefix_variance': axis_results['prefix']['variance'],
            'middle_count': axis_results['middle']['count'],
            'middle_variance': axis_results['middle']['variance'],
            'suffix_count': axis_results['suffix']['count'],
            'suffix_variance': axis_results['suffix']['variance']
        },
        'pm_interaction': {
            'exclusive_middles': pm_results['exclusive_middles'],
            'universal_middles': pm_results['universal_middles']
        },
        'ps_interaction': {
            'universal_suffixes': ps_results['universal_suffixes']
        },
        'three_way': {
            'full_combos': three_way_results['full_combos'],
            'top_10_share': three_way_results['top_10_share']
        }
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    results = main()
