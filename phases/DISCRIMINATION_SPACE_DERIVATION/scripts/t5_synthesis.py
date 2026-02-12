#!/usr/bin/env python3
"""
T5: Synthesis
DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)

Synthesize T1-T4 into a coherent picture of the discrimination space.
"""

import sys
import json
import functools
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def run():
    print("=" * 70)
    print("T5: Synthesis")
    print("DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)")
    print("=" * 70)

    # Load all results
    with open(RESULTS_DIR / 't1_definitive_matrix.json') as f:
        t1 = json.load(f)
    with open(RESULTS_DIR / 't2_dimensionality_convergence.json') as f:
        t2 = json.load(f)
    with open(RESULTS_DIR / 't3_structural_decomposition.json') as f:
        t3 = json.load(f)
    with open(RESULTS_DIR / 't4_morphological_derivation.json') as f:
        t4 = json.load(f)

    print("\n[1/3] Assembling dimensionality estimates")

    # Collect all dimensionality estimates
    estimates = {
        'spectral_eigenvalues_gt1': t4['spectral_d'],
        'effective_rank_spectral_entropy': round(t1['rank']['effective_rank']),
        'cv_plateau_k': t2['convergence']['plateau_k'],
        'cv_elbow_k': t2['convergence']['elbow_k'],
        'nmf_elbow_k': t2['convergence'].get('nmf_elbow_k', 0),
        'morphological_k95': t4['morphological_d'],
        'factored_estimate': round(t3['factored_dimensionality']['factored_estimate']),
    }

    print(f"  Dimensionality estimates:")
    for name, val in estimates.items():
        print(f"    {name}: {val}")

    # Consensus estimate
    valid_estimates = [v for v in estimates.values() if v > 0]
    if valid_estimates:
        median_estimate = int(sorted(valid_estimates)[len(valid_estimates) // 2])
        mean_estimate = int(round(sum(valid_estimates) / len(valid_estimates)))
    else:
        median_estimate = 128
        mean_estimate = 128

    print(f"\n  Median estimate: {median_estimate}")
    print(f"  Mean estimate: {mean_estimate}")

    # Check if AUC converged
    converged = not t2['convergence']['still_rising']
    best_auc = t2['convergence']['best_auc']

    print(f"\n[2/3] Cross-method consistency")

    # Does structure decompose?
    structure = t3['structure_verdict']
    prefix_enrichment = t3['prefix_block']['enrichment']
    prefix_alignment = t3['prefix_spectral_alignment']['alignment']

    print(f"  Structure: {structure}")
    print(f"  PREFIX enrichment: {prefix_enrichment:.2f}x")
    print(f"  PREFIX-spectral alignment: {prefix_alignment}")

    # Can features predict compatibility?
    feature_auc = t4['prediction']['auc']
    feature_sufficiency = t4['feature_sufficiency']
    print(f"  Feature prediction AUC: {feature_auc:.4f}")
    print(f"  Feature sufficiency: {feature_sufficiency}")

    print(f"\n[3/3] Final assessment")

    # Determine the nature of the space
    if feature_sufficiency == "SUFFICIENT":
        nature = "MORPHOLOGICALLY_DERIVED"
        explanation = ("The discrimination space is fully determined by character-level "
                       "morphological features. The ~128D space decomposes into independent "
                       "binary morphological tests.")
    elif feature_sufficiency == "PARTIAL" and prefix_enrichment > 2.0:
        nature = "PARTIALLY_FACTORED"
        explanation = ("The discrimination space is partially structured by PREFIX "
                       f"(enrichment={prefix_enrichment:.1f}x) with additional within-PREFIX "
                       "dimensions. Character features explain most but not all compatibility.")
    elif structure == "PREFIX_INDEPENDENT":
        nature = "HOLISTIC_HIGH_DIMENSIONAL"
        explanation = ("The discrimination space does not decompose by PREFIX or by "
                       "simple morphological features. Compatibility is determined by "
                       "complex whole-MIDDLE relationships requiring high-dimensional "
                       "representation.")
    else:
        nature = "STRUCTURED_HIGH_DIMENSIONAL"
        explanation = ("The discrimination space has internal structure (PREFIX influence, "
                       "degree stratification) but remains high-dimensional. Not reducible "
                       "to a small number of named axes.")

    # Matrix characterization
    decay_profile = t1['decay']['decay_profile']
    mp_above = t1['marchenko_pastur']['n_above_random_99th']
    mean_pr = t1['participation_ratio']['mean_pr']

    print(f"  Eigenvalue decay: {decay_profile}")
    print(f"  Eigenvalues above random: {mp_above}")
    print(f"  Mean participation ratio: {mean_pr:.1f}")
    print(f"  Nature: {nature}")
    print(f"  {explanation}")

    # Verdict
    print(f"\n{'='*70}")
    print("VERDICT")
    print(f"{'='*70}")

    if median_estimate < 50:
        dimensionality_class = "MODERATE"
    elif median_estimate < 200:
        dimensionality_class = "HIGH"
    else:
        dimensionality_class = "VERY_HIGH"

    print(f"\n  Dimensionality class: {dimensionality_class}")
    print(f"  Best estimate: {median_estimate} dimensions (median of {len(valid_estimates)} methods)")
    print(f"  CV AUC converged: {'YES' if converged else 'NO'}")
    print(f"  Nature: {nature}")

    results = {
        'test': 'T5_synthesis',
        'dimensionality_estimates': estimates,
        'median_estimate': median_estimate,
        'mean_estimate': mean_estimate,
        'cv_converged': converged,
        'best_cv_auc': best_auc,
        'structure_verdict': structure,
        'prefix_enrichment': prefix_enrichment,
        'prefix_alignment': prefix_alignment,
        'feature_prediction_auc': feature_auc,
        'feature_sufficiency': feature_sufficiency,
        'matrix_characterization': {
            'decay_profile': decay_profile,
            'eigenvalues_above_random': mp_above,
            'mean_participation_ratio': mean_pr,
        },
        'nature': nature,
        'explanation': explanation,
        'dimensionality_class': dimensionality_class,
        'verdict': {
            'D_estimate': median_estimate,
            'class': dimensionality_class,
            'nature': nature,
            'converged': converged,
        },
    }

    with open(RESULTS_DIR / 't5_synthesis.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't5_synthesis.json'}")


if __name__ == '__main__':
    run()
