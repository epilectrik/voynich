#!/usr/bin/env python3
"""
ats_05_elimination_order.py - H5: Judgment Elimination Order Differs by Family

Tests whether Zodiac and A/C families eliminate judgment types in different orders.

Threshold: Kendall's tau < 0.6, p < 0.05
"""

import json
from pathlib import Path
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

ZODIAC_FAMILY = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}

AC_FAMILY = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}

# Judgment matrix from TRAJECTORY_SEMANTICS (13 judgment types x 4 zones)
# Values: 2=REQUIRED, 1=PERMITTED, 0=IMPOSSIBLE
JUDGMENT_MATRIX = {
    # Watch Closely (6)
    'TEMPERATURE': {'C': 1, 'P': 1, 'R': 2, 'S': 0},
    'PHASE_TRANSITION': {'C': 1, 'P': 2, 'R': 2, 'S': 0},
    'QUALITY_PURITY': {'C': 1, 'P': 2, 'R': 1, 'S': 2},
    'TIMING': {'C': 1, 'P': 2, 'R': 1, 'S': 2},
    'MATERIAL_STATE': {'C': 2, 'P': 2, 'R': 1, 'S': 0},
    'STABILITY': {'C': 1, 'P': 2, 'R': 2, 'S': 0},

    # Forbidden Intervention (3)
    'EQUILIBRIUM_WAIT': {'C': 0, 'P': 0, 'R': 2, 'S': 2},
    'CYCLE_COMPLETION': {'C': 0, 'P': 0, 'R': 2, 'S': 2},
    'PURIFICATION_PATIENCE': {'C': 0, 'P': 0, 'R': 2, 'S': 2},

    # Recovery Decision (4)
    'ABORT_DECISION': {'C': 1, 'P': 2, 'R': 1, 'S': 0},
    'CORRECTION_DECISION': {'C': 1, 'P': 2, 'R': 1, 'S': 0},
    'CONTINUATION_DECISION': {'C': 1, 'P': 2, 'R': 1, 'S': 0},
    'COLLECTION_DECISION': {'C': 1, 'P': 2, 'R': 1, 'S': 0},
}

ZONE_ORDER = ['C', 'P', 'R', 'S']

# For Zodiac, we map R1/R2/R3 -> R and S1/S2 -> S
ZODIAC_TO_CANONICAL = {
    'R1': 'R', 'R2': 'R', 'R3': 'R',
    'S1': 'S', 'S2': 'S',
}


def compute_elimination_zone(judgment_name):
    """Find the zone where a judgment becomes IMPOSSIBLE."""
    row = JUDGMENT_MATRIX[judgment_name]
    for i, zone in enumerate(ZONE_ORDER):
        if row[zone] == 0:
            return i
    return 4  # Never eliminated


def compute_family_weighted_elimination(placement_vector, family):
    """
    Compute elimination order weighted by family's zone distribution.
    Returns an elimination score for each judgment based on the family's
    zone occupancy pattern.
    """
    elimination_scores = {}

    for judgment, zone_values in JUDGMENT_MATRIX.items():
        # Weighted score: higher = later elimination (more available)
        score = 0
        total_weight = 0

        for zone, availability in zone_values.items():
            # Get placement weight for this zone
            if family == 'zodiac':
                # Sum all subscripted positions that map to this zone
                weight = 0
                for sub_zone, canonical in ZODIAC_TO_CANONICAL.items():
                    if canonical == zone:
                        weight += placement_vector.get(sub_zone, 0)
            else:
                weight = placement_vector.get(zone, 0)

            # Weight the availability by zone presence
            if availability > 0:  # PERMITTED or REQUIRED
                score += weight * availability
            total_weight += weight

        elimination_scores[judgment] = score

    return elimination_scores


def main():
    print("=" * 70)
    print("AZC_TRAJECTORY_SHAPE: H5 - Judgment Elimination Order Differs")
    print("=" * 70)
    print()
    print("Prediction: Families eliminate judgments in different orders")
    print("Threshold: Kendall's tau < 0.6, p < 0.05")
    print()

    # Load folio features
    features_path = RESULTS_DIR / "azc_folio_features.json"
    with open(features_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    folios = data['folios']

    # Compute average elimination scores by family
    zodiac_scores = {j: [] for j in JUDGMENT_MATRIX.keys()}
    ac_scores = {j: [] for j in JUDGMENT_MATRIX.keys()}

    for folio_id, folio_data in folios.items():
        placement = folio_data.get('placement_vector', {})

        if folio_id in ZODIAC_FAMILY:
            scores = compute_family_weighted_elimination(placement, 'zodiac')
            for j, s in scores.items():
                zodiac_scores[j].append(s)
        elif folio_id in AC_FAMILY:
            scores = compute_family_weighted_elimination(placement, 'ac')
            for j, s in scores.items():
                ac_scores[j].append(s)

    # Compute mean scores and rank
    zodiac_means = {j: np.mean(v) for j, v in zodiac_scores.items() if v}
    ac_means = {j: np.mean(v) for j, v in ac_scores.items() if v}

    # Rank by elimination score (higher score = later elimination)
    zodiac_ranked = sorted(zodiac_means.keys(), key=lambda x: zodiac_means[x], reverse=True)
    ac_ranked = sorted(ac_means.keys(), key=lambda x: ac_means[x], reverse=True)

    # Convert to rank vectors for Kendall's tau
    judgments = list(JUDGMENT_MATRIX.keys())
    zodiac_ranks = [zodiac_ranked.index(j) for j in judgments]
    ac_ranks = [ac_ranked.index(j) for j in judgments]

    # Results
    print("-" * 70)
    print("ELIMINATION RANKINGS BY FAMILY")
    print("-" * 70)

    print("\nZodiac (most persistent -> first eliminated):")
    for i, j in enumerate(zodiac_ranked):
        print(f"  {i+1}. {j} (score: {zodiac_means[j]:.4f})")

    print("\nA/C (most persistent -> first eliminated):")
    for i, j in enumerate(ac_ranked):
        print(f"  {i+1}. {j} (score: {ac_means[j]:.4f})")

    # Kendall's tau
    print("\n" + "-" * 70)
    print("STATISTICAL TESTS")
    print("-" * 70)

    tau, tau_pvalue = stats.kendalltau(zodiac_ranks, ac_ranks)
    print(f"\nKendall's tau:")
    print(f"  tau = {tau:.4f}, p = {tau_pvalue:.4f}")

    # Hypothesis evaluation
    print("\n" + "=" * 70)
    print("HYPOTHESIS EVALUATION")
    print("=" * 70)

    tau_threshold = tau < 0.6
    significance = tau_pvalue < 0.05

    print(f"\nKendall's tau < 0.6 (orders differ): {'PASS' if tau_threshold else 'FAIL'}")
    print(f"  tau = {tau:.4f}")

    print(f"\nStatistical significance (p < 0.05): {'PASS' if significance else 'FAIL'}")
    print(f"  p-value: {tau_pvalue:.4f}")

    # For pass, tau should be LOW (indicating different orders)
    # and significance indicates the difference is real
    passed = tau_threshold and significance
    print("\n" + "-" * 70)
    print(f"H5 VERDICT: {'PASS' if passed else 'FAIL'}")
    print("-" * 70)

    # Save results
    results = {
        'hypothesis': 'H5',
        'name': 'Judgment Elimination Order Differs',
        'prediction': 'Families eliminate judgments in different orders',
        'threshold': 'Kendall tau < 0.6, p < 0.05',
        'zodiac': {
            'ranking': zodiac_ranked,
            'mean_scores': zodiac_means,
        },
        'ac': {
            'ranking': ac_ranked,
            'mean_scores': ac_means,
        },
        'statistics': {
            'kendalls_tau': float(tau),
            'tau_pvalue': float(tau_pvalue),
        },
        'evaluation': {
            'tau_threshold_met': bool(tau_threshold),
            'significant': bool(significance),
            'passed': bool(passed),
        },
    }

    output_path = RESULTS_DIR / "ats_elimination_order.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
