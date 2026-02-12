#!/usr/bin/env python3
"""
T8: Final Integrated Synthesis
DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)

Combine T1-T7 into a single architectural assessment.
Key question: Is the MIDDLE discrimination space a structural fingerprint
of a real constraint system, or an artifact of sparse graph statistics?
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
    print("T8: Final Integrated Synthesis")
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
    with open(RESULTS_DIR / 't5_synthesis.json') as f:
        t5 = json.load(f)
    with open(RESULTS_DIR / 't6_null_ensemble.json') as f:
        t6 = json.load(f)
    with open(RESULTS_DIR / 't7_bootstrap_stability.json') as f:
        t7 = json.load(f)

    # Section 1: Matrix characterization
    print("\n[1/4] Matrix Characterization")
    print(f"  MIDDLEs: {t1['n_middles']}")
    print(f"  Compatible pairs: {t1['n_compatible']} ({t1['pct_compatible']}%)")
    print(f"  Leading eigenvalue: {t1['eigenspectrum']['leading']:.1f}")
    print(f"  Effective rank: {t1['rank']['effective_rank']:.1f}")
    print(f"  Decay profile: {t1['decay']['decay_profile']}")

    # Section 2: Dimensionality
    print("\n[2/4] Dimensionality Assessment")
    print(f"  CV AUC converged: {'YES' if not t2['convergence']['still_rising'] else 'NO'}")
    print(f"  CV plateau: K≈{t2['convergence']['best_k']} (AUC={t2['convergence']['best_auc']:.4f})")
    print(f"  NMF elbow: K≈{t2['convergence']['nmf_elbow_k']}")
    print(f"  Morphological D (95%): {t4['morphological_d']}")
    print(f"  Median estimate: {t5['median_estimate']}")

    # Section 3: Null ensemble results
    print("\n[3/4] Null Ensemble Verdict")
    null_verdict = t6['verdict']
    print(f"  Configuration Model anomalous metrics: {t6['anomalous_cm']}/5")
    print(f"  Erdős-Rényi anomalous metrics: {t6['anomalous_er']}/5")
    print(f"  Null ensemble verdict: {null_verdict}")

    # Detail the comparison
    for key, comp in t6['comparison'].items():
        cm_flag = "**ANOMALOUS**" if comp['cm_anomalous'] else ""
        print(f"    {key}: real={comp['real']:.2f}, CM={comp['cm_mean']:.2f}±{comp['cm_std']:.2f}, z={comp['cm_z']:.1f} {cm_flag}")

    # Section 4: Stability
    print("\n[4/4] Bootstrap Stability")
    boot_verdict = t7['verdict']
    print(f"  Max CV at 20% removal: {t7['max_cv_at_20pct']:.4f}")
    print(f"  Stability verdict: {boot_verdict}")

    # Final integrated verdict
    print(f"\n{'='*70}")
    print("FINAL INTEGRATED VERDICT")
    print(f"{'='*70}")

    # Logic:
    # FINGERPRINT_CONFIRMED: null_rare + stable
    # FINGERPRINT_PARTIAL: null_rare + fragile, or null_partial + stable
    # GENERIC_SPARSE_GRAPH: null_not_rare (regardless of stability)

    if null_verdict == "RARE" and boot_verdict == "STABLE":
        final_verdict = "FINGERPRINT_CONFIRMED"
        explanation = (
            "The spectral profile of the MIDDLE discrimination space is "
            "ANOMALOUS under degree-preserving randomization AND STABLE "
            "under subsampling. This is a genuine structural fingerprint "
            "of the underlying constraint system, not an artifact of "
            "sparse graph statistics or sampling noise."
        )
    elif null_verdict == "NOT_RARE":
        final_verdict = "GENERIC_SPARSE_GRAPH"
        explanation = (
            "The spectral profile is GENERIC for graphs with this degree "
            "distribution. The hub-dominated structure and slow eigenvalue "
            "decay are artifacts of degree heterogeneity, not evidence of "
            "a specialized constraint architecture."
        )
    elif null_verdict == "RARE" and boot_verdict != "STABLE":
        final_verdict = "FINGERPRINT_PARTIAL"
        explanation = (
            "The spectral profile is anomalous under null models but "
            "shows some sensitivity to subsampling. The fingerprint is "
            "real but may be partially dependent on specific MIDDLEs."
        )
    elif null_verdict == "PARTIALLY_RARE" and boot_verdict == "STABLE":
        final_verdict = "FINGERPRINT_PARTIAL"
        explanation = (
            "Some spectral features are anomalous under degree-preserving "
            "randomization and the profile is stable under subsampling. "
            "Partial fingerprint — the structure goes beyond degree "
            "heterogeneity in specific measurable ways."
        )
    else:
        final_verdict = "FINGERPRINT_PARTIAL"
        explanation = (
            "Mixed evidence: some features are anomalous, some are generic. "
            "The discrimination space has genuine structure that partially "
            "exceeds what sparse graph statistics would produce."
        )

    print(f"\n  VERDICT: {final_verdict}")
    print(f"\n  {explanation}")

    # Architectural summary
    print(f"\n  Architecture of the discrimination space:")
    print(f"    Layer 1: Hub manifold (1 dominant eigenmode, λ=82)")
    print(f"    Layer 2: ~28 structured discrimination axes (above random)")
    print(f"    Layer 3: ~70 fine-grained axes (morphologically derivable)")
    print(f"    Layer 4: Long tail micro-axes (noise floor)")
    print(f"    Total effective: ~{t5['median_estimate']} dimensions")

    print(f"\n  Key structural properties:")
    print(f"    PREFIX enrichment: {t3['prefix_block']['enrichment']:.2f}x (soft prior)")
    print(f"    Character feature prediction: AUC={t4['prediction']['auc']:.2f} (partial)")
    print(f"    Spectral embedding prediction: AUC={t2['convergence']['best_auc']:.2f} (near-complete)")
    print(f"    Row-pair MI: {t4['information_content']['mean_row_pair_mi']:.4f} bits (near-independence)")

    results = {
        'test': 'T8_synthesis_update',
        'matrix': {
            'n_middles': t1['n_middles'],
            'pct_compatible': t1['pct_compatible'],
            'leading_eigenvalue': t1['eigenspectrum']['leading'],
            'effective_rank': t1['rank']['effective_rank'],
            'decay_profile': t1['decay']['decay_profile'],
        },
        'dimensionality': {
            'median_estimate': t5['median_estimate'],
            'cv_plateau_k': t2['convergence']['best_k'],
            'cv_best_auc': t2['convergence']['best_auc'],
            'morphological_d': t4['morphological_d'],
            'factored_estimate': t3['factored_dimensionality']['factored_estimate'],
        },
        'null_ensemble': {
            'verdict': null_verdict,
            'anomalous_cm': t6['anomalous_cm'],
            'anomalous_er': t6['anomalous_er'],
        },
        'stability': {
            'verdict': boot_verdict,
            'max_cv_20pct': t7['max_cv_at_20pct'],
        },
        'final_verdict': final_verdict,
        'explanation': explanation,
    }

    with open(RESULTS_DIR / 't8_synthesis_update.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't8_synthesis_update.json'}")


if __name__ == '__main__':
    run()
