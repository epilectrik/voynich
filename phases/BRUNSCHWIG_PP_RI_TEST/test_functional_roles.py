#!/usr/bin/env python3
"""
PP/RI FUNCTIONAL ROLE TEST
==========================

Testing the practitioner-perspective model:
- PP = "What can I DO with this?" (procedural affordances)
- RI = "What IS this specifically?" (material identity)

Tests:
1. PP Profile by Fire Degree - fire degrees should cluster by PP profile
2. RI Diversity Within Categories - same category shares PP, differs in RI
3. PP as Procedural Gate - materials compatible with procedure have required PP

Phase: BRUNSCHWIG_PP_RI_TEST
Date: 2026-01-24
"""

import json
import csv
from collections import defaultdict, Counter
from pathlib import Path
import statistics
import math

PROJECT_ROOT = Path(__file__).parent.parent.parent

# ============================================================
# MORPHOLOGY HELPERS
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_middle(token):
    """Extract MIDDLE from token."""
    if not token or not isinstance(token, str):
        return None
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break
    return token if token else None

# ============================================================
# DATA LOADING
# ============================================================

def load_brunschwig():
    """Load Brunschwig recipe database."""
    with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['recipes']

def load_pp_ri_classification():
    """Load PP vs RI MIDDLE classification."""
    with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
        data = json.load(f)
    pp_middles = set(data['a_shared_middles'])
    ri_middles = set(data['a_exclusive_middles'])
    return pp_middles, ri_middles

def load_folio_classifications():
    """Load product type classification for A folios."""
    with open(PROJECT_ROOT / 'results' / 'exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['a_folio_classifications']

def load_folio_middles():
    """Load MIDDLEs per folio."""
    folio_middles = defaultdict(list)

    with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip() != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            placement = row.get('placement', '').strip()

            if language != 'A' or not word or '*' in word:
                continue
            if placement.startswith('L'):
                continue

            middle = extract_middle(word)
            if middle and len(middle) > 0:
                folio_middles[folio].append(middle)

    return dict(folio_middles)

def recipe_to_product_type(recipe):
    """Map Brunschwig recipe to product type."""
    fire_degree = recipe.get('fire_degree', 2)
    material_class = recipe.get('material_class', 'herb')

    if fire_degree == 4 or material_class == 'animal':
        return 'PRECISION'
    elif fire_degree == 3:
        return 'OIL_RESIN'
    elif fire_degree == 1:
        return 'WATER_GENTLE'
    else:
        return 'WATER_STANDARD'

# ============================================================
# STATISTICAL HELPERS
# ============================================================

def jaccard_similarity(set1, set2):
    """Compute Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def cosine_similarity(counter1, counter2):
    """Compute cosine similarity between two frequency distributions."""
    all_keys = set(counter1.keys()) | set(counter2.keys())
    if not all_keys:
        return 0.0

    dot_product = sum(counter1.get(k, 0) * counter2.get(k, 0) for k in all_keys)
    norm1 = math.sqrt(sum(v**2 for v in counter1.values()))
    norm2 = math.sqrt(sum(v**2 for v in counter2.values()))

    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

def chi_square_test(observed, expected):
    """Simple chi-square test."""
    if len(observed) != len(expected):
        return None, None

    chi2 = sum((o - e)**2 / e for o, e in zip(observed, expected) if e > 0)
    df = len(observed) - 1

    # Rough p-value approximation
    if df <= 0:
        return chi2, 1.0

    # Using approximation for p-value
    p = math.exp(-chi2/2) if chi2 < 20 else 0.001
    return chi2, p

# ============================================================
# TEST 1: PP PROFILE BY FIRE DEGREE
# ============================================================

def test_pp_profile_by_fire_degree(recipes, folio_classifications, folio_middles, pp_middles, ri_middles):
    """
    Test: Fire degrees should cluster by PP profile.

    If PP encodes procedural affordances, then:
    - Materials with same fire degree tolerance have similar PP profiles
    - Fire degree groups should have distinct PP signatures
    """
    print("\n" + "="*70)
    print("TEST 1: PP Profile by Fire Degree")
    print("="*70)
    print("Hypothesis: If PP encodes procedural affordances, fire degrees should")
    print("            cluster by PP profile (same fire degree = similar PP)")
    print()

    # Group recipes by fire degree
    fire_degree_recipes = defaultdict(list)
    for recipe in recipes:
        fd = recipe.get('fire_degree', 2)
        fire_degree_recipes[fd].append(recipe)

    print("Brunschwig recipes by fire degree:")
    for fd in sorted(fire_degree_recipes.keys()):
        print(f"  Fire degree {fd}: {len(fire_degree_recipes[fd])} recipes")

    # Get PP profiles for folios associated with each fire degree
    # Fire degree -> Product type -> Folios -> PP MIDDLEs
    fire_degree_pp_profiles = {}

    for fd, fd_recipes in fire_degree_recipes.items():
        # Get dominant product type for this fire degree
        product_types = [recipe_to_product_type(r) for r in fd_recipes]
        dominant_type = Counter(product_types).most_common(1)[0][0]

        # Get folios of this product type
        pp_counter = Counter()
        ri_counter = Counter()
        total_tokens = 0

        for folio, ftype in folio_classifications.items():
            if ftype == dominant_type and folio in folio_middles:
                for middle in folio_middles[folio]:
                    if middle in pp_middles:
                        pp_counter[middle] += 1
                    elif middle in ri_middles:
                        ri_counter[middle] += 1
                    total_tokens += 1

        fire_degree_pp_profiles[fd] = {
            'pp_counter': pp_counter,
            'ri_counter': ri_counter,
            'pp_types': set(pp_counter.keys()),
            'ri_types': set(ri_counter.keys()),
            'pp_total': sum(pp_counter.values()),
            'ri_total': sum(ri_counter.values()),
            'dominant_type': dominant_type
        }

    # Compute pairwise PP profile similarities
    print("\n" + "-"*70)
    print("PP Profile Similarity (Cosine) by Fire Degree:")
    print("-"*70)

    fire_degrees = sorted(fire_degree_pp_profiles.keys())

    print(f"\n{'FD':<6}", end="")
    for fd2 in fire_degrees:
        print(f"{fd2:<8}", end="")
    print()

    similarities = []
    for fd1 in fire_degrees:
        print(f"{fd1:<6}", end="")
        for fd2 in fire_degrees:
            sim = cosine_similarity(
                fire_degree_pp_profiles[fd1]['pp_counter'],
                fire_degree_pp_profiles[fd2]['pp_counter']
            )
            print(f"{sim:<8.3f}", end="")
            if fd1 < fd2:
                similarities.append((fd1, fd2, sim))
        print()

    # Check if adjacent fire degrees are more similar than distant ones
    adjacent_sims = [s for fd1, fd2, s in similarities if abs(fd1 - fd2) == 1]
    distant_sims = [s for fd1, fd2, s in similarities if abs(fd1 - fd2) > 1]

    print(f"\nAdjacent fire degree similarity: {statistics.mean(adjacent_sims):.3f}" if adjacent_sims else "")
    print(f"Distant fire degree similarity: {statistics.mean(distant_sims):.3f}" if distant_sims else "")

    # Show top PP MIDDLEs per fire degree
    print("\n" + "-"*70)
    print("Top PP MIDDLEs by Fire Degree:")
    print("-"*70)

    for fd in fire_degrees:
        profile = fire_degree_pp_profiles[fd]
        print(f"\nFire Degree {fd} (via {profile['dominant_type']}):")
        print(f"  PP tokens: {profile['pp_total']}, RI tokens: {profile['ri_total']}")
        print(f"  PP types: {len(profile['pp_types'])}, RI types: {len(profile['ri_types'])}")

        top_pp = profile['pp_counter'].most_common(5)
        if top_pp:
            print(f"  Top PP: {', '.join(f'{m}({c})' for m, c in top_pp)}")

    # Statistical test: Do fire degrees have different PP profiles?
    # Using Jaccard on PP type sets
    print("\n" + "-"*70)
    print("PP Type Overlap (Jaccard) by Fire Degree:")
    print("-"*70)

    print(f"\n{'FD':<6}", end="")
    for fd2 in fire_degrees:
        print(f"{fd2:<8}", end="")
    print()

    for fd1 in fire_degrees:
        print(f"{fd1:<6}", end="")
        for fd2 in fire_degrees:
            jacc = jaccard_similarity(
                fire_degree_pp_profiles[fd1]['pp_types'],
                fire_degree_pp_profiles[fd2]['pp_types']
            )
            print(f"{jacc:<8.3f}", end="")
        print()

    # Interpretation
    print("\n" + "-"*70)
    print("INTERPRETATION:")
    print("-"*70)

    # Check if fire degree 4 (PRECISION) is distinct
    if 4 in fire_degree_pp_profiles and 2 in fire_degree_pp_profiles:
        fd4_fd2_sim = cosine_similarity(
            fire_degree_pp_profiles[4]['pp_counter'],
            fire_degree_pp_profiles[2]['pp_counter']
        )
        print(f"\nFire degree 4 vs 2 PP similarity: {fd4_fd2_sim:.3f}")

        if fd4_fd2_sim < 0.8:
            print("  -> SUPPORTS: Fire degree 4 (PRECISION) has distinct PP profile")
        else:
            print("  -> WEAK: Fire degrees share similar PP profiles")

    return fire_degree_pp_profiles

# ============================================================
# TEST 2: RI DIVERSITY WITHIN CATEGORIES
# ============================================================

def test_ri_diversity_within_categories(recipes, folio_classifications, folio_middles, pp_middles, ri_middles):
    """
    Test: Same-category materials should share PP but differ in RI.

    If RI encodes material identity, then:
    - Materials in same Brunschwig category have similar PP (same procedures)
    - But different RI (different specific identities)
    """
    print("\n" + "="*70)
    print("TEST 2: RI Diversity Within Material Categories")
    print("="*70)
    print("Hypothesis: If RI encodes material identity, same-category materials")
    print("            should share PP (same procedures) but differ in RI (identity)")
    print()

    # Group recipes by material_class
    material_classes = defaultdict(list)
    for recipe in recipes:
        mc = recipe.get('material_class', 'unknown')
        material_classes[mc].append(recipe)

    print("Brunschwig recipes by material class:")
    for mc, recs in sorted(material_classes.items(), key=lambda x: -len(x[1])):
        if len(recs) >= 3:
            print(f"  {mc}: {len(recs)} recipes")

    # For each material class, compute within-class PP and RI variance
    print("\n" + "-"*70)
    print("Within-Class PP vs RI Variance:")
    print("-"*70)

    results = []

    for mc, mc_recipes in material_classes.items():
        if len(mc_recipes) < 5:  # Need enough recipes for meaningful comparison
            continue

        # Get product types for this material class
        product_types = [recipe_to_product_type(r) for r in mc_recipes]
        type_counts = Counter(product_types)

        # Collect PP and RI profiles for folios of each type
        all_pp_sets = []
        all_ri_sets = []

        for ptype, count in type_counts.items():
            if count < 2:
                continue

            pp_set = set()
            ri_set = set()

            for folio, ftype in folio_classifications.items():
                if ftype == ptype and folio in folio_middles:
                    for middle in folio_middles[folio]:
                        if middle in pp_middles:
                            pp_set.add(middle)
                        elif middle in ri_middles:
                            ri_set.add(middle)

            if pp_set:
                all_pp_sets.append(pp_set)
            if ri_set:
                all_ri_sets.append(ri_set)

        if len(all_pp_sets) < 2 or len(all_ri_sets) < 2:
            continue

        # Compute mean pairwise Jaccard within class
        pp_jaccards = []
        ri_jaccards = []

        for i in range(len(all_pp_sets)):
            for j in range(i+1, len(all_pp_sets)):
                pp_jaccards.append(jaccard_similarity(all_pp_sets[i], all_pp_sets[j]))

        for i in range(len(all_ri_sets)):
            for j in range(i+1, len(all_ri_sets)):
                ri_jaccards.append(jaccard_similarity(all_ri_sets[i], all_ri_sets[j]))

        if pp_jaccards and ri_jaccards:
            mean_pp_jacc = statistics.mean(pp_jaccards)
            mean_ri_jacc = statistics.mean(ri_jaccards)

            print(f"\n{mc} ({len(mc_recipes)} recipes):")
            print(f"  Within-class PP Jaccard: {mean_pp_jacc:.3f}")
            print(f"  Within-class RI Jaccard: {mean_ri_jacc:.3f}")
            print(f"  PP - RI difference: {mean_pp_jacc - mean_ri_jacc:+.3f}")

            results.append({
                'class': mc,
                'pp_jaccard': mean_pp_jacc,
                'ri_jaccard': mean_ri_jacc,
                'diff': mean_pp_jacc - mean_ri_jacc
            })

    # Summary
    print("\n" + "-"*70)
    print("SUMMARY:")
    print("-"*70)

    if results:
        pp_higher = sum(1 for r in results if r['diff'] > 0)
        ri_higher = sum(1 for r in results if r['diff'] < 0)

        mean_pp = statistics.mean(r['pp_jaccard'] for r in results)
        mean_ri = statistics.mean(r['ri_jaccard'] for r in results)

        print(f"\nAcross {len(results)} material classes:")
        print(f"  Mean within-class PP Jaccard: {mean_pp:.3f}")
        print(f"  Mean within-class RI Jaccard: {mean_ri:.3f}")
        print(f"  Classes where PP > RI: {pp_higher}")
        print(f"  Classes where RI > PP: {ri_higher}")

        print("\n" + "-"*70)
        print("INTERPRETATION:")
        print("-"*70)

        if mean_pp > mean_ri + 0.05:
            print("\n  -> SUPPORTS: Within same material class, PP is more consistent")
            print("               than RI. Same procedures, different identities.")
        elif mean_ri > mean_pp + 0.05:
            print("\n  -> CONTRADICTS: RI is more consistent than PP within classes.")
        else:
            print("\n  -> INCONCLUSIVE: PP and RI show similar within-class variance.")

    return results

# ============================================================
# TEST 3: PP AS PROCEDURAL GATE
# ============================================================

def test_pp_as_procedural_gate(recipes, folio_classifications, folio_middles, pp_middles, ri_middles):
    """
    Test: Materials compatible with a procedure should have required PP atoms.

    If PP encodes procedural affordances, then:
    - Different procedures require different PP profiles
    - Materials that CAN undergo a procedure have the required PP atoms
    """
    print("\n" + "="*70)
    print("TEST 3: PP as Procedural Gate")
    print("="*70)
    print("Hypothesis: If PP encodes procedural affordances, different output types")
    print("            should require different PP profiles")
    print()

    # Group recipes by output type (approximated by product type)
    output_types = {
        'WATER_GENTLE': 'Aqueous (gentle)',
        'WATER_STANDARD': 'Aqueous (standard)',
        'OIL_RESIN': 'Oil/Resin',
        'PRECISION': 'Precision/Special'
    }

    # Get PP profiles for each output type
    type_pp_profiles = {}

    for ptype in output_types.keys():
        pp_counter = Counter()
        total = 0

        for folio, ftype in folio_classifications.items():
            if ftype == ptype and folio in folio_middles:
                for middle in folio_middles[folio]:
                    if middle in pp_middles:
                        pp_counter[middle] += 1
                        total += 1

        type_pp_profiles[ptype] = {
            'counter': pp_counter,
            'types': set(pp_counter.keys()),
            'total': total
        }

    print("PP profiles by output type:")
    for ptype, profile in type_pp_profiles.items():
        print(f"\n  {output_types[ptype]}:")
        print(f"    PP tokens: {profile['total']}")
        print(f"    PP types: {len(profile['types'])}")
        top = profile['counter'].most_common(5)
        if top:
            print(f"    Top PP: {', '.join(f'{m}({c})' for m, c in top)}")

    # Find PP atoms that are REQUIRED for each type (appear in >50% of tokens)
    print("\n" + "-"*70)
    print("Type-Specific PP Atoms (>10% of type's PP tokens):")
    print("-"*70)

    type_signatures = {}

    for ptype, profile in type_pp_profiles.items():
        total = profile['total']
        if total < 100:
            continue

        signature = set()
        print(f"\n{output_types[ptype]}:")

        for middle, count in profile['counter'].most_common(20):
            pct = 100 * count / total
            if pct >= 10:
                signature.add(middle)

                # Check if this PP is enriched vs other types
                other_pcts = []
                for other_type, other_profile in type_pp_profiles.items():
                    if other_type != ptype and other_profile['total'] > 100:
                        other_pct = 100 * other_profile['counter'].get(middle, 0) / other_profile['total']
                        other_pcts.append(other_pct)

                if other_pcts:
                    mean_other = statistics.mean(other_pcts)
                    enrichment = pct / mean_other if mean_other > 0 else float('inf')
                    marker = "*" if enrichment > 1.5 else ""
                    print(f"    {middle}: {pct:.1f}% (vs {mean_other:.1f}% other, {enrichment:.1f}x){marker}")
                else:
                    print(f"    {middle}: {pct:.1f}%")

        type_signatures[ptype] = signature

    # Check if types have distinct signatures
    print("\n" + "-"*70)
    print("Type Signature Overlap:")
    print("-"*70)

    types_with_sigs = [t for t in type_signatures if type_signatures[t]]

    print(f"\n{'Type':<20}", end="")
    for t2 in types_with_sigs:
        print(f"{t2:<15}", end="")
    print()

    for t1 in types_with_sigs:
        print(f"{t1:<20}", end="")
        for t2 in types_with_sigs:
            jacc = jaccard_similarity(type_signatures[t1], type_signatures[t2])
            print(f"{jacc:<15.3f}", end="")
        print()

    # Find PP atoms unique to each type
    print("\n" + "-"*70)
    print("Type-Exclusive PP Atoms:")
    print("-"*70)

    for ptype, sig in type_signatures.items():
        other_sigs = set()
        for other_type, other_sig in type_signatures.items():
            if other_type != ptype:
                other_sigs |= other_sig

        exclusive = sig - other_sigs
        if exclusive:
            print(f"\n{output_types[ptype]} exclusive: {exclusive}")

    # Interpretation
    print("\n" + "-"*70)
    print("INTERPRETATION:")
    print("-"*70)

    # Calculate average between-type Jaccard
    between_jaccards = []
    for i, t1 in enumerate(types_with_sigs):
        for t2 in types_with_sigs[i+1:]:
            between_jaccards.append(jaccard_similarity(type_signatures[t1], type_signatures[t2]))

    if between_jaccards:
        mean_between = statistics.mean(between_jaccards)
        print(f"\nMean between-type PP signature Jaccard: {mean_between:.3f}")

        if mean_between < 0.5:
            print("  -> SUPPORTS: Output types have distinct PP signatures")
            print("               PP encodes type-specific procedural affordances")
        elif mean_between < 0.7:
            print("  -> PARTIAL: Some differentiation in PP signatures by type")
        else:
            print("  -> CONTRADICTS: Output types share similar PP signatures")

    return type_pp_profiles, type_signatures

# ============================================================
# MAIN
# ============================================================

def main():
    print("PP/RI FUNCTIONAL ROLE TEST")
    print("="*70)
    print("Testing the practitioner-perspective model:")
    print("  PP = 'What can I DO with this?' (procedural affordances)")
    print("  RI = 'What IS this specifically?' (material identity)")
    print("="*70)

    # Load data
    print("\nLoading data...")
    recipes = load_brunschwig()
    pp_middles, ri_middles = load_pp_ri_classification()
    folio_classifications = load_folio_classifications()
    folio_middles = load_folio_middles()

    print(f"  Brunschwig recipes: {len(recipes)}")
    print(f"  PP MIDDLEs: {len(pp_middles)}")
    print(f"  RI MIDDLEs: {len(ri_middles)}")
    print(f"  Classified folios: {len(folio_classifications)}")

    # Run tests
    results = {}

    results['test1'] = test_pp_profile_by_fire_degree(
        recipes, folio_classifications, folio_middles, pp_middles, ri_middles
    )

    results['test2'] = test_ri_diversity_within_categories(
        recipes, folio_classifications, folio_middles, pp_middles, ri_middles
    )

    results['test3'] = test_pp_as_procedural_gate(
        recipes, folio_classifications, folio_middles, pp_middles, ri_middles
    )

    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print("""
The practitioner-perspective model predicts:

1. PP encodes PROCEDURAL AFFORDANCES (what you can DO)
   - Same fire degree -> similar PP profile
   - Different output types -> different PP signatures

2. RI encodes MATERIAL IDENTITY (what it IS)
   - Same category materials share PP (same procedures)
   - But differ in RI (different specific identities)

Results above should be interpreted in this framework.
""")

    # Save results
    output_dir = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_PP_RI_TEST' / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        'phase': 'BRUNSCHWIG_PP_RI_TEST',
        'test': 'FUNCTIONAL_ROLES',
        'date': '2026-01-24',
        'model': {
            'PP': 'Procedural affordances - what you can DO with this',
            'RI': 'Material identity - what this IS specifically'
        }
    }

    with open(output_dir / 'functional_roles_test.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to: {output_dir / 'functional_roles_test.json'}")

if __name__ == '__main__':
    main()
