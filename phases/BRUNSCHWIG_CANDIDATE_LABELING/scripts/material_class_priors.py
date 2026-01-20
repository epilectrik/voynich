#!/usr/bin/env python3
"""
PHASE 3: MATERIAL-CLASS PRIOR INFERENCE

Bayesian inference of material-class probabilities for registry-internal MIDDLEs
based on their procedural context (product type distribution).

Inference chain:
  token → folio appearances → product type distribution → material-class posterior

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

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

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

def get_middle(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

def entropy(probs):
    """Compute Shannon entropy of a probability distribution."""
    h = 0
    for p in probs:
        if p > 0:
            h -= p * math.log2(p)
    return h

# ============================================================
# DATA LOADING
# ============================================================

def load_registry_internal_middles():
    """Load registry-internal MIDDLEs from 2-track classification."""
    with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
        data = json.load(f)
    return set(data['a_exclusive_middles'])

def load_folio_classifications():
    """Load product type classification for each A folio."""
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['a_folio_classifications']

def load_folio_middles():
    """Load all MIDDLEs per folio from transcript."""
    folio_middles = defaultdict(list)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
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
            middle = get_middle(word)
            if middle and len(middle) > 1:
                folio_middles[folio].append(middle)

    return folio_middles

# ============================================================
# BAYESIAN INFERENCE
# ============================================================

def compute_product_type_distribution(middle, folio_middles, folio_classifications):
    """
    Compute P(product_type | token) based on folio appearances.
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
    Compute P(material_class | token) by marginalizing over product types.

    P(mc | token) = Σ P(mc | pt) * P(pt | token)
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
    print("PHASE 3: MATERIAL-CLASS PRIOR INFERENCE")
    print("=" * 70)
    print()
    print("Computing P(material_class | token) for registry-internal MIDDLEs")
    print("via Bayesian inference through procedural context (product types).")
    print()
    print("NOTE: All outputs are conditional on 'IF Brunschwig applies'.")
    print("      This is probabilistic projection, NOT semantic decoding.")
    print()

    # Load data
    print("Loading data...")
    registry_internal = load_registry_internal_middles()
    folio_classifications = load_folio_classifications()
    folio_middles = load_folio_middles()

    print(f"  Registry-internal MIDDLEs: {len(registry_internal)}")
    print(f"  Classified folios: {len(folio_classifications)}")
    print()

    # Compute priors for each registry-internal MIDDLE
    print("Computing material-class posteriors...")
    print()

    results = []
    n_with_data = 0
    n_without_data = 0

    for middle in sorted(registry_internal):
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

    print(f"  MIDDLEs with product-type data: {n_with_data}")
    print(f"  MIDDLEs without data: {n_without_data}")
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
        # Show top 3 material classes
        sorted_mc = sorted(r['material_class_posterior'].items(), key=lambda x: -x[1])
        top3 = [(mc, p) for mc, p in sorted_mc if p > 0.01][:3]
        print(f"    top classes: {', '.join(f'{mc}={p:.2f}' for mc, p in top3)}")
        print()

    # Show most dispersed (high entropy) examples
    print("=" * 70)
    print("MOST DISPERSED (HIGH ENTROPY) - Procedurally ambiguous")
    print("=" * 70)
    print()

    for r in results[-10:]:
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
    if not all_valid:
        bad = [(i, s) for i, s in enumerate(sums) if abs(s - 1.0) >= 0.001]
        print(f"  Invalid entries: {bad[:5]}")
    print()

    # Save results
    output = {
        'phase': 'MATERIAL_CLASS_PRIORS',
        'date': '2026-01-20',
        'method': 'Bayesian inference via procedural context',
        'conditional_on': 'IF Brunschwig material distributions apply',
        'n_middles_analyzed': n_with_data,
        'n_middles_no_data': n_without_data,
        'summary': {
            'mean_entropy': round(mean_entropy, 3),
            'min_entropy': round(min_entropy, 3),
            'max_entropy': round(max_entropy, 3),
            'dominant_class_distribution': dict(dominant_counts)
        },
        'results': results
    }

    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/material_class_priors.json', 'w') as f:
        json.dump(output, f, indent=2)

    # Save summary
    summary = {
        'phase': 'MATERIAL_CLASS_PRIORS',
        'date': '2026-01-20',
        'n_middles_analyzed': n_with_data,
        'mean_entropy': round(mean_entropy, 3),
        'entropy_range': [round(min_entropy, 3), round(max_entropy, 3)],
        'dominant_class_distribution': dict(dominant_counts),
        'most_concentrated': [
            {'middle': r['middle'], 'top_class': r['top_class'], 'probability': r['top_class_probability'], 'entropy': r['entropy']}
            for r in results[:20]
        ],
        'most_dispersed': [
            {'middle': r['middle'], 'top_class': r['top_class'], 'probability': r['top_class_probability'], 'entropy': r['entropy']}
            for r in results[-20:]
        ]
    }

    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/material_class_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()
    print("Low-entropy MIDDLEs appear in procedurally concentrated contexts.")
    print("Their material-class posteriors reflect which input materials")
    print("Brunschwig associates with those procedural outcomes.")
    print()
    print("High-entropy MIDDLEs appear across diverse procedural contexts.")
    print("Their material-class posteriors are dispersed, reflecting")
    print("procedural ambiguity (not semantic ambiguity).")
    print()
    print("REMINDER: These are conditional posteriors, not decoded meanings.")
    print("          'P(flower|token)=0.57' means 'IF Brunschwig applies,")
    print("          this token appears in flower-associated contexts 57%'.")
    print()
    print(f"Results saved to phases/BRUNSCHWIG_CANDIDATE_LABELING/results/material_class_priors.json")
    print(f"Summary saved to phases/BRUNSCHWIG_CANDIDATE_LABELING/results/material_class_summary.json")

if __name__ == '__main__':
    main()
