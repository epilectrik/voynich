#!/usr/bin/env python3
"""
PHASE 3: MATERIAL-CLASS PRIOR INFERENCE (v2 - FIXED EXTRACTION)

Bayesian inference of material-class probabilities for registry-internal MIDDLEs
based on their procedural context (product type distribution).

FIX: v2 properly extracts MIDDLE cores by stripping BOTH PREFIX and SUFFIX.
     v1 only stripped PREFIX, inflating MIDDLE count with suffix variants.

Inference chain:
  token -> MIDDLE core -> folio appearances -> product type distribution -> material-class posterior

This is NOT semantic decoding. It is probabilistic projection through an external
interpretive frame (Brunschwig). All outputs are conditional on "IF Brunschwig applies."

Constraints respected:
- C384: Aggregate/statistical analysis, not entry-level coupling
- Semantic ceiling: Procedural context associations, not semantic content
- No hard labels, no winner-take-all, no clustering into "flower tokens"
"""

import csv
import json
import math
from collections import defaultdict, Counter
from pathlib import Path

PROJECT_ROOT = Path('.')

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['eedy', 'edy', 'aiy', 'dy', 'ey', 'y', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

# Brunschwig material-class distributions per product type
# From brunschwig_materials_master.json (197 with procedures)
BRUNSCHWIG_MATERIAL_DISTRIBUTIONS = {
    'WATER_GENTLE': {
        'cold_moist_flower': 0.521,  # 25/48
        'fruit': 0.333,              # 16/48
        'dangerous_herb': 0.146      # 7/48
    },
    'OIL_RESIN': {
        'hot_dry_herb': 0.943,       # 33/35
        'hot_dry_root': 0.057        # 2/35
    },
    'WATER_STANDARD': {
        'herb': 0.863,               # 360/417
        'hot_flower': 0.055,         # 23/417
        'moderate_herb': 0.048,      # 20/417
        'moist_root': 0.022,         # 9/417
        'leaf': 0.012                # 5/417
    },
    'PRECISION': {
        'animal': 1.000              # 9/9
    }
}

# All material classes
ALL_MATERIAL_CLASSES = sorted(set(
    mc for dist in BRUNSCHWIG_MATERIAL_DISTRIBUTIONS.values()
    for mc in dist.keys()
))

def extract_middle_core(token):
    """
    Extract true MIDDLE core by stripping BOTH PREFIX and SUFFIX.

    v1 bug: Only stripped PREFIX, so 'chaldey' -> 'aldey' (MIDDLE+SUFFIX)
    v2 fix: Strip both, so 'chaldey' -> 'ald' (true MIDDLE core)
    """
    if not token:
        return None

    working = token

    # Strip prefix (longest match first)
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if working.startswith(p):
            working = working[len(p):]
            break

    # Strip suffix (longest match first)
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if working.endswith(s) and len(working) > len(s):
            working = working[:-len(s)]
            break

    return working if working else None

def entropy(probs):
    """Compute Shannon entropy of a probability distribution."""
    h = 0
    for p in probs:
        if p > 0:
            h -= p * math.log2(p)
    return h

# ============================================================
# DATA LOADING (FIXED)
# ============================================================

def derive_ri_middles_from_transcript():
    """
    Derive RI MIDDLEs directly from transcript.
    RI = appears in Currier A but NOT in Currier B (A-exclusive).

    Uses proper MIDDLE core extraction (PREFIX and SUFFIX stripped).
    """
    a_middles = set()
    b_middles = set()

    with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
            word = row.get('word', '').strip()
            language = row.get('language', '').strip()
            if not word or '*' in word:
                continue
            if word.startswith('[') or word.startswith('<'):
                continue

            middle = extract_middle_core(word)
            if middle and len(middle) > 0:
                if language == 'A':
                    a_middles.add(middle)
                elif language == 'B':
                    b_middles.add(middle)

    # RI = A-exclusive
    ri_middles = a_middles - b_middles
    # PP = shared
    pp_middles = a_middles & b_middles

    return ri_middles, pp_middles, a_middles, b_middles

def load_folio_classifications():
    """Load product type classification for each A folio."""
    with open(PROJECT_ROOT / 'results' / 'exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['a_folio_classifications']

def load_folio_middles():
    """
    Load all MIDDLE cores per folio from transcript.
    Uses proper extraction (PREFIX and SUFFIX stripped).
    """
    folio_middles = defaultdict(list)

    with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            middle = extract_middle_core(word)
            if middle and len(middle) > 0:
                folio_middles[folio].append(middle)

    return folio_middles

# ============================================================
# BAYESIAN INFERENCE
# ============================================================

def compute_product_type_distribution(middle, folio_middles, folio_classifications):
    """
    Compute P(product_type | middle) based on folio appearances.
    """
    # Find all folios where this MIDDLE appears
    folios_with_middle = []
    for folio, middles in folio_middles.items():
        if middle in middles:
            folios_with_middle.append(folio)

    if not folios_with_middle:
        return {}, 0

    # Count by product type
    pt_counts = Counter()
    for folio in folios_with_middle:
        pt = folio_classifications.get(folio, 'UNKNOWN')
        if pt in BRUNSCHWIG_MATERIAL_DISTRIBUTIONS:
            pt_counts[pt] += 1

    total = sum(pt_counts.values())
    if total == 0:
        return {}, len(folios_with_middle)

    # Normalize to probability distribution
    pt_distribution = {pt: count / total for pt, count in pt_counts.items()}

    return pt_distribution, len(folios_with_middle)

def compute_material_class_posterior(pt_distribution):
    """
    Compute P(material_class | middle) by marginalizing over product types.

    P(mc | middle) = sum_pt P(mc | pt) * P(pt | middle)
    """
    mc_posterior = {mc: 0.0 for mc in ALL_MATERIAL_CLASSES}

    for pt, p_pt in pt_distribution.items():
        if pt in BRUNSCHWIG_MATERIAL_DISTRIBUTIONS:
            for mc, p_mc_given_pt in BRUNSCHWIG_MATERIAL_DISTRIBUTIONS[pt].items():
                mc_posterior[mc] += p_mc_given_pt * p_pt

    return mc_posterior

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("PHASE 3: MATERIAL-CLASS PRIOR INFERENCE (v2 - FIXED)")
    print("=" * 70)
    print()
    print("Computing P(material_class | middle) for registry-internal MIDDLEs")
    print("via Bayesian inference through procedural context (product types).")
    print()
    print("FIX: v2 properly extracts MIDDLE cores (PREFIX + SUFFIX stripped).")
    print("     v1 only stripped PREFIX, inflating count with suffix variants.")
    print()
    print("NOTE: All outputs are conditional on 'IF Brunschwig applies'.")
    print("      This is probabilistic projection, NOT semantic decoding.")
    print()

    # Derive RI MIDDLEs directly from transcript
    print("Deriving RI MIDDLEs from transcript...")
    ri_middles, pp_middles, a_middles, b_middles = derive_ri_middles_from_transcript()

    print(f"  A MIDDLEs (unique cores): {len(a_middles)}")
    print(f"  B MIDDLEs (unique cores): {len(b_middles)}")
    print(f"  RI (A-exclusive): {len(ri_middles)}")
    print(f"  PP (shared A&B): {len(pp_middles)}")
    print()

    # Load folio data
    print("Loading folio data...")
    folio_classifications = load_folio_classifications()
    folio_middles = load_folio_middles()

    print(f"  Classified folios: {len(folio_classifications)}")
    print(f"  Folios with MIDDLE data: {len(folio_middles)}")
    print()

    # Compute priors for each RI MIDDLE
    print("Computing material-class posteriors for RI MIDDLEs...")
    print()

    results = []
    n_with_data = 0
    n_without_data = 0

    for middle in sorted(ri_middles):
        pt_dist, n_folios = compute_product_type_distribution(
            middle, folio_middles, folio_classifications
        )

        if not pt_dist:
            n_without_data += 1
            continue

        n_with_data += 1
        mc_posterior = compute_material_class_posterior(pt_dist)

        # Find top class
        top_class = max(mc_posterior.items(), key=lambda x: x[1])

        # Compute entropy
        probs = [p for p in mc_posterior.values() if p > 0]
        h = entropy(probs)

        results.append({
            'middle': middle,
            'n_folios': n_folios,
            'product_type_distribution': pt_dist,
            'material_class_posterior': mc_posterior,
            'top_class': top_class[0],
            'top_class_probability': round(top_class[1], 3),
            'entropy': round(h, 3)
        })

    print(f"  RI MIDDLEs with product-type data: {n_with_data}")
    print(f"  RI MIDDLEs without data: {n_without_data}")
    print(f"  Coverage: {100*n_with_data/len(ri_middles):.1f}%")
    print()

    # Sort by entropy (low entropy = more concentrated = more informative)
    results.sort(key=lambda x: x['entropy'])

    # Summary statistics
    print("=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print()

    entropies = [r['entropy'] for r in results]
    mean_entropy = sum(entropies) / len(entropies) if entropies else 0
    min_entropy = min(entropies) if entropies else 0
    max_entropy = max(entropies) if entropies else 0

    print(f"  Mean entropy: {mean_entropy:.2f} bits")
    print(f"  Min entropy: {min_entropy:.2f} bits (most concentrated)")
    print(f"  Max entropy: {max_entropy:.2f} bits (most dispersed)")
    print()

    # Count by dominant class
    dominant_counts = Counter(r['top_class'] for r in results)
    print("  Dominant material class distribution:")
    for mc, count in dominant_counts.most_common():
        pct = 100 * count / len(results)
        print(f"    {mc}: {count} ({pct:.1f}%)")
    print()

    # High-confidence counts
    high_conf = [r for r in results if r['top_class_probability'] >= 0.7]
    print(f"  High-confidence (P >= 0.7): {len(high_conf)} ({100*len(high_conf)/len(results):.1f}%)")

    high_conf_by_class = Counter(r['top_class'] for r in high_conf)
    for mc, count in high_conf_by_class.most_common():
        print(f"    {mc}: {count}")
    print()

    # Show most concentrated (low entropy) examples
    print("=" * 70)
    print("MOST CONCENTRATED (LOW ENTROPY) - High confidence")
    print("=" * 70)
    print()

    for r in results[:15]:
        print(f"  {r['middle']}:")
        print(f"    n_folios: {r['n_folios']}")
        print(f"    top_class: {r['top_class']} (P={r['top_class_probability']:.2f})")
        print(f"    entropy: {r['entropy']:.2f} bits")
        sorted_mc = sorted(r['material_class_posterior'].items(), key=lambda x: -x[1])
        top3 = [(mc, p) for mc, p in sorted_mc if p > 0.01][:3]
        print(f"    top classes: {', '.join(f'{mc}={p:.2f}' for mc, p in top3)}")
        print()

    # Verify probability vectors sum to ~1.0
    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print()

    sums = [sum(r['material_class_posterior'].values()) for r in results]
    all_valid = all(abs(s - 1.0) < 0.001 for s in sums)
    print(f"  All probability vectors sum to 1.0: {all_valid}")
    print()

    # Save results
    output = {
        'phase': 'MATERIAL_CLASS_PRIORS_V2',
        'date': '2026-01-24',
        'method': 'Bayesian inference via procedural context (FIXED extraction)',
        'extraction_fix': 'v2 strips both PREFIX and SUFFIX to get true MIDDLE cores',
        'conditional_on': 'IF Brunschwig material distributions apply',
        'ri_population': {
            'total_ri_middles': len(ri_middles),
            'with_data': n_with_data,
            'without_data': n_without_data,
            'coverage_pct': round(100*n_with_data/len(ri_middles), 1)
        },
        'summary': {
            'mean_entropy': round(mean_entropy, 3),
            'min_entropy': round(min_entropy, 3),
            'max_entropy': round(max_entropy, 3),
            'dominant_class_distribution': dict(dominant_counts),
            'high_confidence_count': len(high_conf),
            'high_confidence_by_class': dict(high_conf_by_class)
        },
        'results': results
    }

    with open(PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors_v2.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("=" * 70)
    print("COMPARISON WITH v1")
    print("=" * 70)
    print()
    print("  v1 (PREFIX-stripped only): 349 'MIDDLEs', 128 analyzed (36.7%)")
    print(f"  v2 (proper extraction):    {len(ri_middles)} MIDDLEs, {n_with_data} analyzed ({100*n_with_data/len(ri_middles):.1f}%)")
    print()
    print(f"Results saved to phases/BRUNSCHWIG_CANDIDATE_LABELING/results/material_class_priors_v2.json")

if __name__ == '__main__':
    main()
