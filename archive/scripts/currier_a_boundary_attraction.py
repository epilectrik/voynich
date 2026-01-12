"""
F-A-007: Forbidden-Zone Attraction Fit

Tests whether Currier A entries cluster near structural boundaries
(exclusive prefix-MIDDLE territory) rather than interior points of
the legal type space.

Core question: Does the registry preferentially record edge-cases?

Boundary definition (from C276/C423):
- MIDDLE is PREFIX-BOUND: 80% of MIDDLEs are prefix-exclusive
- A token is "near boundary" if its MIDDLE works with few prefixes
- A token is "interior" if its MIDDLE works with many prefixes

Pre-declared outcomes:
- If attraction exists cross-section → F2: "A preferentially records edge-cases"
- If attraction exists only in H → F1: "Boundary sensitivity is domain-specific"
- If no attraction → F1: "Registry samples broadly, not frontier-biased"

Tier F2 if cross-section, F1 otherwise.
"""

import os
import json
from collections import defaultdict, Counter
import math
import random

# Known prefixes from CAS-MORPH phase
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# Extended suffixes for decomposition
SUFFIXES = ['aiin', 'ain', 'ar', 'al', 'or', 'ol', 'am', 'an', 'in',
            'y', 'dy', 'ey', 'edy', 'eedy', 'chy', 'shy',
            'r', 'l', 's', 'd', 'n', 'm']
SUFFIX_PATTERNS = sorted(SUFFIXES, key=len, reverse=True)


def load_currier_a_full():
    """Load Currier A tokens with full metadata."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    tokens = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 11:
                currier = parts[6].strip('"').strip()
                if currier == 'A':
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    section = parts[3].strip('"').strip() if len(parts) > 3 else ''

                    # Skip damaged tokens
                    if token and '*' not in token:
                        tokens.append({
                            'token': token,
                            'folio': folio,
                            'section': section
                        })

    return tokens


def decompose_token(token):
    """Decompose token into PREFIX + MIDDLE + SUFFIX."""
    prefix = None
    remainder = token

    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            remainder = token[len(p):]
            break

    if not prefix:
        return None, None, None

    suffix = None
    middle = remainder

    for s in SUFFIX_PATTERNS:
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            middle = remainder[:-len(s)]
            break
        elif remainder == s:
            suffix = s
            middle = ''
            break

    if not suffix:
        if len(remainder) >= 2:
            suffix = remainder[-2:]
            middle = remainder[:-2]
        elif len(remainder) == 1:
            suffix = remainder
            middle = ''
        else:
            suffix = ''
            middle = ''

    return prefix, middle, suffix


def build_legality_map():
    """Build map of legal (prefix, middle) pairs and their exclusivity."""
    data_path = r'C:\git\voynich\results\currier_a_modeling_data.json'

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    p_middle_given_prefix = data['target_1_token_census']['p_middle_given_prefix']

    # Build set of legal (prefix, middle) pairs
    legal_pairs = set()
    middles_by_prefix = defaultdict(set)

    for prefix in PREFIXES:
        if prefix in p_middle_given_prefix:
            for middle, prob in p_middle_given_prefix[prefix].items():
                if prob > 0:  # Attested
                    legal_pairs.add((prefix, middle))
                    middles_by_prefix[prefix].add(middle)

    # For each MIDDLE, count how many prefixes can take it
    middle_prefix_count = defaultdict(int)
    middle_to_prefixes = defaultdict(set)

    all_middles = set()
    for prefix in PREFIXES:
        all_middles.update(middles_by_prefix[prefix])

    for middle in all_middles:
        for prefix in PREFIXES:
            if (prefix, middle) in legal_pairs:
                middle_prefix_count[middle] += 1
                middle_to_prefixes[middle].add(prefix)

    return legal_pairs, middle_prefix_count, middle_to_prefixes, middles_by_prefix


def compute_boundary_distance(prefix, middle, middle_prefix_count):
    """
    Compute boundary distance for a (prefix, middle) pair.

    Boundary distance = number of alternative prefixes that can take this MIDDLE
    - Low distance (1) = exclusive territory (near boundary)
    - High distance (8) = universal territory (interior)

    Normalized: 0 = maximally exclusive, 1 = maximally universal
    """
    if middle not in middle_prefix_count:
        return 0.0  # Unknown middle = exclusive

    count = middle_prefix_count[middle]
    # Normalize: (count - 1) / (max_count - 1) where max is 8 prefixes
    # count=1 → 0.0 (exclusive), count=8 → 1.0 (universal)
    if count <= 1:
        return 0.0
    return (count - 1) / (len(PREFIXES) - 1)


def generate_random_composites(middles_by_prefix, n_samples, section_distribution):
    """Generate random legal composites matched to section distribution."""
    composites = []

    sections = list(section_distribution.keys())
    section_weights = [section_distribution[s] for s in sections]

    for _ in range(n_samples):
        # Pick random prefix
        prefix = random.choice(PREFIXES)
        # Pick random legal middle for this prefix
        if middles_by_prefix[prefix]:
            middle = random.choice(list(middles_by_prefix[prefix]))
        else:
            middle = ''
        # Pick random section weighted by distribution
        section = random.choices(sections, weights=section_weights)[0]

        composites.append({
            'prefix': prefix,
            'middle': middle,
            'section': section
        })

    return composites


def generate_interior_composites(middle_prefix_count, middles_by_prefix, n_samples, section_distribution):
    """Generate composites biased toward interior (shared MIDDLEs)."""
    composites = []

    # Find MIDDLEs that work with 4+ prefixes (interior)
    interior_middles = [m for m, c in middle_prefix_count.items() if c >= 4]

    if not interior_middles:
        interior_middles = [m for m, c in middle_prefix_count.items() if c >= 2]

    sections = list(section_distribution.keys())
    section_weights = [section_distribution[s] for s in sections]

    for _ in range(n_samples):
        # Pick random interior middle
        middle = random.choice(interior_middles)
        # Pick random prefix that can take this middle
        valid_prefixes = [p for p in PREFIXES if middle in middles_by_prefix[p]]
        if valid_prefixes:
            prefix = random.choice(valid_prefixes)
        else:
            prefix = random.choice(PREFIXES)

        section = random.choices(sections, weights=section_weights)[0]

        composites.append({
            'prefix': prefix,
            'middle': middle,
            'section': section
        })

    return composites


def mann_whitney_u(x, y):
    """Compute Mann-Whitney U test statistic and approximate p-value."""
    nx, ny = len(x), len(y)

    # Rank all values
    combined = [(v, 'x', i) for i, v in enumerate(x)] + [(v, 'y', i) for i, v in enumerate(y)]
    combined.sort(key=lambda t: t[0])

    # Assign ranks (handle ties by averaging)
    ranks = {}
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2  # Average rank for ties
        for k in range(i, j):
            group, idx = combined[k][1], combined[k][2]
            if group == 'x':
                ranks[('x', idx)] = avg_rank
            else:
                ranks[('y', idx)] = avg_rank
        i = j

    # Sum of ranks for x
    r1 = sum(ranks[('x', i)] for i in range(nx))

    # U statistic
    u1 = r1 - nx * (nx + 1) / 2
    u2 = nx * ny - u1
    u = min(u1, u2)

    # Normal approximation for p-value
    mu = nx * ny / 2
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12)

    if sigma == 0:
        return u, 1.0

    z = (u - mu) / sigma

    # Two-tailed p-value using normal approximation
    from math import erf
    p = 2 * (1 - 0.5 * (1 + erf(abs(z) / math.sqrt(2))))

    return u, p


def run_analysis():
    """Main analysis function."""
    print("=" * 70)
    print("F-A-007: FORBIDDEN-ZONE ATTRACTION FIT")
    print("=" * 70)
    print()

    # Set random seed for reproducibility
    random.seed(42)

    # Step 1: Build legality map
    print("Step 1: Building legality map from existing modeling data...")
    legal_pairs, middle_prefix_count, middle_to_prefixes, middles_by_prefix = build_legality_map()

    print(f"  Total legal (prefix, middle) pairs: {len(legal_pairs)}")
    print(f"  Total unique MIDDLEs: {len(middle_prefix_count)}")

    # Classify MIDDLEs by exclusivity
    exclusive_count = sum(1 for c in middle_prefix_count.values() if c == 1)
    shared_count = sum(1 for c in middle_prefix_count.values() if c >= 2)
    universal_count = sum(1 for c in middle_prefix_count.values() if c >= 6)

    print(f"\nMIDDLE exclusivity breakdown:")
    print(f"  Exclusive (1 prefix): {exclusive_count} ({100*exclusive_count/len(middle_prefix_count):.1f}%)")
    print(f"  Shared (2-5 prefixes): {shared_count - universal_count} ({100*(shared_count-universal_count)/len(middle_prefix_count):.1f}%)")
    print(f"  Universal (6+ prefixes): {universal_count} ({100*universal_count/len(middle_prefix_count):.1f}%)")

    # Step 2: Load and decompose Currier A tokens
    print("\nStep 2: Loading and decomposing Currier A tokens...")
    tokens = load_currier_a_full()
    print(f"  Total clean tokens: {len(tokens)}")

    # Decompose and compute boundary distance
    observed_data = []
    section_counts = Counter()

    for t in tokens:
        prefix, middle, suffix = decompose_token(t['token'])
        if prefix:
            bd = compute_boundary_distance(prefix, middle, middle_prefix_count)
            observed_data.append({
                'token': t['token'],
                'prefix': prefix,
                'middle': middle,
                'section': t['section'],
                'boundary_distance': bd
            })
            section_counts[t['section']] += 1

    print(f"  Decomposed tokens: {len(observed_data)}")

    # Section distribution for baselines
    total = sum(section_counts.values())
    section_distribution = {s: c/total for s, c in section_counts.items()}
    print(f"\nSection distribution:")
    for s, p in sorted(section_distribution.items(), key=lambda x: -x[1]):
        print(f"  {s}: {100*p:.1f}%")

    # Step 3: Generate baseline composites
    print("\nStep 3: Generating baseline composites...")
    n_samples = len(observed_data)

    random_composites = generate_random_composites(middles_by_prefix, n_samples, section_distribution)
    interior_composites = generate_interior_composites(middle_prefix_count, middles_by_prefix, n_samples, section_distribution)

    # Compute boundary distances for baselines
    for c in random_composites:
        c['boundary_distance'] = compute_boundary_distance(c['prefix'], c['middle'], middle_prefix_count)

    for c in interior_composites:
        c['boundary_distance'] = compute_boundary_distance(c['prefix'], c['middle'], middle_prefix_count)

    print(f"  Generated {len(random_composites)} random composites")
    print(f"  Generated {len(interior_composites)} interior-biased composites")

    # Step 4: Compare distributions
    print("\n" + "-" * 50)
    print("Step 4: Comparing boundary distance distributions...")

    obs_distances = [d['boundary_distance'] for d in observed_data]
    rand_distances = [d['boundary_distance'] for d in random_composites]
    int_distances = [d['boundary_distance'] for d in interior_composites]

    obs_mean = sum(obs_distances) / len(obs_distances)
    rand_mean = sum(rand_distances) / len(rand_distances)
    int_mean = sum(int_distances) / len(int_distances)

    print(f"\nMean boundary distance (0=exclusive, 1=universal):")
    print(f"  Observed A entries:     {obs_mean:.4f}")
    print(f"  Random legal composites: {rand_mean:.4f}")
    print(f"  Interior-biased composites: {int_mean:.4f}")

    # Statistical tests
    u_obs_rand, p_obs_rand = mann_whitney_u(obs_distances, rand_distances)
    u_obs_int, p_obs_int = mann_whitney_u(obs_distances, int_distances)

    print(f"\nMann-Whitney U tests:")
    print(f"  Observed vs Random: U={u_obs_rand:.0f}, p={p_obs_rand:.4f}")
    print(f"  Observed vs Interior: U={u_obs_int:.0f}, p={p_obs_int:.4f}")

    # Direction of effect
    if obs_mean < rand_mean:
        direction = "BOUNDARY ATTRACTION (A is closer to exclusive territory)"
    else:
        direction = "INTERIOR PREFERENCE (A is closer to shared territory)"

    print(f"\nDirection: {direction}")
    print(f"  Difference (Obs - Random): {obs_mean - rand_mean:+.4f}")

    # Step 5: Section-stratified analysis
    print("\n" + "-" * 50)
    print("Step 5: Section-stratified analysis...")

    section_results = {}
    significant_sections = 0

    sections = defaultdict(list)
    for d in observed_data:
        sections[d['section']].append(d['boundary_distance'])

    # Section-specific random baselines
    for section, distances in sorted(sections.items()):
        if len(distances) < 10:
            continue

        # Generate section-matched random composites
        section_random = []
        for _ in range(len(distances)):
            prefix = random.choice(PREFIXES)
            if middles_by_prefix[prefix]:
                middle = random.choice(list(middles_by_prefix[prefix]))
            else:
                middle = ''
            section_random.append(compute_boundary_distance(prefix, middle, middle_prefix_count))

        sec_mean = sum(distances) / len(distances)
        rand_sec_mean = sum(section_random) / len(section_random)

        u, p = mann_whitney_u(distances, section_random)

        section_results[section] = {
            'n': len(distances),
            'mean_obs': sec_mean,
            'mean_rand': rand_sec_mean,
            'diff': sec_mean - rand_sec_mean,
            'u': u,
            'p': p
        }

        if p < 0.05 and sec_mean < rand_sec_mean:
            significant_sections += 1

        print(f"\n{section} (n={len(distances)}):")
        print(f"  Mean observed: {sec_mean:.4f}, Mean random: {rand_sec_mean:.4f}")
        print(f"  Difference: {sec_mean - rand_sec_mean:+.4f}")
        print(f"  Mann-Whitney p={p:.4f} {'*' if p < 0.05 else ''}")

    # Step 6: Exclusivity breakdown
    print("\n" + "-" * 50)
    print("Step 6: Exclusivity category breakdown...")

    obs_exclusive = sum(1 for d in obs_distances if d == 0.0) / len(obs_distances)
    rand_exclusive = sum(1 for d in rand_distances if d == 0.0) / len(rand_distances)

    obs_universal = sum(1 for d in obs_distances if d >= 0.7) / len(obs_distances)
    rand_universal = sum(1 for d in rand_distances if d >= 0.7) / len(rand_distances)

    print(f"\nExclusive MIDDLEs (boundary_distance=0):")
    print(f"  Observed: {100*obs_exclusive:.1f}%")
    print(f"  Random:   {100*rand_exclusive:.1f}%")
    print(f"  Difference: {100*(obs_exclusive - rand_exclusive):+.1f} percentage points")

    print(f"\nUniversal MIDDLEs (boundary_distance>=0.7):")
    print(f"  Observed: {100*obs_universal:.1f}%")
    print(f"  Random:   {100*rand_universal:.1f}%")
    print(f"  Difference: {100*(obs_universal - rand_universal):+.1f} percentage points")

    # Step 7: Determine fit tier
    print("\n" + "=" * 70)
    print("RESULT SUMMARY")
    print("=" * 70)

    # Pre-declared criteria
    # Attraction = obs_mean < rand_mean with p < 0.05
    has_overall_attraction = obs_mean < rand_mean and p_obs_rand < 0.05
    has_section_robustness = significant_sections >= 2

    print(f"\nPre-declared outcome conditions:")
    print(f"  1. Overall attraction (obs < random, p < 0.05): {'YES' if has_overall_attraction else 'NO'}")
    print(f"     Mean difference: {obs_mean - rand_mean:+.4f}, p={p_obs_rand:.4f}")
    print(f"  2. Section robustness (>=2 significant sections): {'YES' if has_section_robustness else 'NO'}")
    print(f"     Significant sections: {significant_sections}")

    if has_overall_attraction and has_section_robustness:
        fit_tier = "F2"
        result = "SUCCESS"
        interpretation = "A preferentially records edge-cases: registry entries cluster near exclusive territory."
    elif has_overall_attraction and not has_section_robustness:
        fit_tier = "F1"
        result = "PARTIAL"
        interpretation = "Boundary sensitivity is domain-specific: attraction exists but not robust across sections."
    else:
        fit_tier = "F1"
        result = "NULL"
        interpretation = "No attraction: registry samples control space broadly, not frontier-biased."

    print(f"\n{'='*50}")
    print(f"FIT TIER: {fit_tier}")
    print(f"RESULT: {result}")
    print(f"{'='*50}")
    print(f"\nInterpretation: {interpretation}")

    # Compile results
    results = {
        'fit_id': 'F-A-007',
        'fit_name': 'Forbidden-Zone Attraction',
        'fit_tier': fit_tier,
        'result': result,
        'date': '2026-01-10',
        'legality_summary': {
            'total_legal_pairs': len(legal_pairs),
            'total_middles': len(middle_prefix_count),
            'exclusive_middles': exclusive_count,
            'shared_middles': shared_count - universal_count,
            'universal_middles': universal_count
        },
        'boundary_distances': {
            'observed_mean': float(obs_mean),
            'random_mean': float(rand_mean),
            'interior_mean': float(int_mean),
            'difference_obs_rand': float(obs_mean - rand_mean)
        },
        'statistical_tests': {
            'obs_vs_random': {'u': float(u_obs_rand), 'p': float(p_obs_rand)},
            'obs_vs_interior': {'u': float(u_obs_int), 'p': float(p_obs_int)}
        },
        'section_results': {
            k: {kk: float(vv) if isinstance(vv, float) else vv for kk, vv in v.items()}
            for k, v in section_results.items()
        },
        'exclusivity_breakdown': {
            'observed_exclusive_rate': float(obs_exclusive),
            'random_exclusive_rate': float(rand_exclusive),
            'observed_universal_rate': float(obs_universal),
            'random_universal_rate': float(rand_universal)
        },
        'criteria_check': {
            'has_overall_attraction': has_overall_attraction,
            'has_section_robustness': has_section_robustness
        },
        'interpretation': interpretation,
        'supports_constraints': ['C276', 'C423'] if has_overall_attraction else [],
        'introduces_new_constraints': False
    }

    # Save results
    output_path = r'C:\git\voynich\results\currier_a_boundary_attraction.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    run_analysis()
