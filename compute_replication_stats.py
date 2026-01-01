#!/usr/bin/env python3
"""
Compute replication statistics for SAME_HUB_TYPE validation.

Performs permutation testing to determine if the visual cohesion
finding from Phase D replicates with larger sample size.
"""

import json
import numpy as np
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple


def load_mode_b_annotations():
    """Load all Mode B annotations."""
    with open("annotation_data/mode_b_annotations.json") as f:
        data = json.load(f)
    return data.get("records", [])


def classify_cohesion(record: Dict) -> float:
    """
    Classify a Mode B response as cohesive (1) or not (0).

    Cohesive responses:
    - outlier_detection: "NONE_STAND_OUT" or "CANNOT_TELL"
    - compare_leaf_similarity: "YES_CLEARLY" or "YES_SOMEWHAT"
    - compare_root_similarity: "YES_CLEARLY" or "YES_SOMEWHAT"
    - other: treated as neutral (0.5)
    """
    question = record.get("question_id", "")
    response = record.get("response", "")

    if question == "outlier_detection":
        if response in ["NONE_STAND_OUT", "CANNOT_TELL"]:
            return 1.0
        else:
            return 0.0

    elif question in ["compare_leaf_similarity", "compare_root_similarity"]:
        if response in ["YES_CLEARLY", "YES_SOMEWHAT"]:
            return 1.0
        elif response == "MIXED":
            return 0.5
        else:
            return 0.0

    elif question == "best_leaf_description":
        if response not in ["no consistent leaf feature", "CANNOT_TELL"]:
            return 1.0
        else:
            return 0.0

    elif question == "most_similar_pair":
        if response == "ALL_SIMILAR":
            return 1.0
        elif response == "NONE_SIMILAR":
            return 0.0
        else:
            return 0.5  # Partial cohesion

    return 0.5  # Unknown question


def compute_group_cohesion(records: List[Dict]) -> Dict[str, Dict]:
    """
    Compute cohesion statistics by group type.

    Returns dict with:
    - n_records: number of records
    - cohesion_scores: list of individual scores
    - mean_cohesion: average cohesion
    """
    group_stats = defaultdict(lambda: {"records": [], "scores": []})

    for record in records:
        group_type = record.get("group_type", "unknown")
        score = classify_cohesion(record)
        weight = record.get("response_weight", 1.0)

        group_stats[group_type]["records"].append(record)
        group_stats[group_type]["scores"].append(score * weight)

    # Compute statistics
    result = {}
    for group_type, data in group_stats.items():
        scores = data["scores"]
        result[group_type] = {
            "n_records": len(scores),
            "cohesion_scores": scores,
            "mean_cohesion": float(np.mean(scores)) if scores else 0,
            "std_cohesion": float(np.std(scores)) if len(scores) > 1 else 0
        }

    return result


def permutation_test(hypothesis_scores: List[float],
                     null_scores: List[float],
                     n_permutations: int = 10000) -> Dict:
    """
    Perform permutation test comparing hypothesis vs null groups.

    Tests whether hypothesis groups have higher cohesion than null groups.
    """
    if not hypothesis_scores or not null_scores:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": "Need scores from both hypothesis and null groups"
        }

    # Observed difference
    obs_hyp_mean = np.mean(hypothesis_scores)
    obs_null_mean = np.mean(null_scores)
    obs_diff = obs_hyp_mean - obs_null_mean

    # Combine all scores
    combined = np.array(hypothesis_scores + null_scores)
    n_hyp = len(hypothesis_scores)

    # Permutation distribution
    perm_diffs = []
    rng = np.random.default_rng(42)

    for _ in range(n_permutations):
        perm = rng.permutation(combined)
        perm_hyp = perm[:n_hyp]
        perm_null = perm[n_hyp:]
        perm_diff = np.mean(perm_hyp) - np.mean(perm_null)
        perm_diffs.append(perm_diff)

    perm_diffs = np.array(perm_diffs)

    # P-value (one-tailed: hypothesis > null)
    p_value = np.mean(perm_diffs >= obs_diff)

    # Effect size (Cohen's d)
    pooled_std = np.sqrt((np.var(hypothesis_scores) + np.var(null_scores)) / 2)
    if pooled_std > 0:
        effect_size = obs_diff / pooled_std
    else:
        effect_size = float("inf") if obs_diff > 0 else 0

    # Percentile of observed difference in permutation distribution
    percentile = 100 * (1 - p_value)

    return {
        "hypothesis_mean": float(obs_hyp_mean),
        "null_mean": float(obs_null_mean),
        "observed_difference": float(obs_diff),
        "p_value": float(p_value),
        "effect_size": float(effect_size),
        "percentile": float(percentile),
        "n_permutations": n_permutations,
        "n_hypothesis": len(hypothesis_scores),
        "n_null": len(null_scores)
    }


def determine_replication_status(test_result: Dict) -> Tuple[str, str]:
    """
    Determine replication status based on test results.

    Returns: (status, interpretation)
    """
    if test_result.get("status") == "INSUFFICIENT_DATA":
        return "INSUFFICIENT_DATA", "Not enough data for statistical test"

    p = test_result.get("p_value", 1.0)
    effect = test_result.get("effect_size", 0)

    if p < 0.05 and effect > 1.0:
        return "CONFIRMED", "Replication successful: p < 0.05, large effect size"
    elif p < 0.10 and effect > 0.5:
        return "WEAKENED", "Partial replication: suggestive but not fully confirmed"
    else:
        return "FAILED", "Replication failed: p > 0.10 or small effect size"


def main():
    """Compute replication statistics."""
    print("=" * 60)
    print("REPLICATION STATISTICS")
    print("=" * 60)

    # Load data
    records = load_mode_b_annotations()
    print(f"\nTotal Mode B records: {len(records)}")

    # Compute cohesion by group type
    group_stats = compute_group_cohesion(records)

    print("\nCohesion by group type:")
    for group_type, stats in sorted(group_stats.items()):
        print(f"  {group_type}: N={stats['n_records']}, mean={stats['mean_cohesion']:.3f}")

    # Extract hypothesis and null scores
    hypothesis_types = ["same_hub_type", "same_category", "same_cluster", "same_prefix"]
    null_types = ["random", "stratified_random"]

    hypothesis_scores = []
    for t in hypothesis_types:
        if t in group_stats:
            hypothesis_scores.extend(group_stats[t]["cohesion_scores"])

    null_scores = []
    for t in null_types:
        if t in group_stats:
            null_scores.extend(group_stats[t]["cohesion_scores"])

    print(f"\nHypothesis scores: N={len(hypothesis_scores)}")
    print(f"Null scores: N={len(null_scores)}")

    # Permutation test: All hypothesis vs null
    print("\n" + "-" * 40)
    print("TEST 1: All hypothesis groups vs null")
    test_all = permutation_test(hypothesis_scores, null_scores)
    if "status" not in test_all:
        print(f"  Hypothesis mean: {test_all['hypothesis_mean']:.3f}")
        print(f"  Null mean: {test_all['null_mean']:.3f}")
        print(f"  Effect size: {test_all['effect_size']:.3f}")
        print(f"  p-value: {test_all['p_value']:.4f}")

    # Permutation test: SAME_HUB_TYPE only
    print("\n" + "-" * 40)
    print("TEST 2: SAME_HUB_TYPE vs random (PRIMARY)")
    hub_scores = group_stats.get("same_hub_type", {}).get("cohesion_scores", [])
    random_scores = group_stats.get("random", {}).get("cohesion_scores", [])

    test_hub = permutation_test(hub_scores, random_scores)
    if "status" not in test_hub:
        print(f"  SAME_HUB_TYPE mean: {test_hub['hypothesis_mean']:.3f}")
        print(f"  RANDOM mean: {test_hub['null_mean']:.3f}")
        print(f"  Effect size: {test_hub['effect_size']:.3f}")
        print(f"  p-value: {test_hub['p_value']:.4f}")
        print(f"  Percentile: {test_hub['percentile']:.1f}%")

    # Determine status
    status, interpretation = determine_replication_status(test_hub)
    print(f"\n  STATUS: {status}")
    print(f"  {interpretation}")

    # Permutation test: SAME_CATEGORY
    print("\n" + "-" * 40)
    print("TEST 3: SAME_CATEGORY vs random (SECONDARY)")
    cat_scores = group_stats.get("same_category", {}).get("cohesion_scores", [])

    test_cat = permutation_test(cat_scores, random_scores)
    if "status" not in test_cat:
        print(f"  SAME_CATEGORY mean: {test_cat['hypothesis_mean']:.3f}")
        print(f"  RANDOM mean: {test_cat['null_mean']:.3f}")
        print(f"  Effect size: {test_cat['effect_size']:.3f}")
        print(f"  p-value: {test_cat['p_value']:.4f}")

    cat_status, cat_interp = determine_replication_status(test_cat)
    print(f"\n  STATUS: {cat_status}")

    # Output
    output = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "total_mode_b_records": len(records)
        },
        "group_statistics": {
            k: {
                "n_records": v["n_records"],
                "mean_cohesion": v["mean_cohesion"],
                "std_cohesion": v["std_cohesion"]
            }
            for k, v in group_stats.items()
        },
        "tests": {
            "all_hypothesis_vs_null": test_all,
            "same_hub_type_vs_random": {
                **test_hub,
                "status": status,
                "interpretation": interpretation
            },
            "same_category_vs_random": {
                **test_cat,
                "status": cat_status,
                "interpretation": cat_interp
            }
        },
        "replication_result": {
            "primary_test": "same_hub_type_vs_random",
            "status": status,
            "interpretation": interpretation,
            "vocabulary_analysis_validity": "CONFIRMATORY" if status == "CONFIRMED" else "EXPLORATORY_ONLY"
        },
        "closer_role_status": {
            "status": "UNTESTABLE",
            "reason": "Only 1 folio available (f22r); f96r is text-only",
            "implication": "CLOSER visual coherence cannot be independently validated"
        }
    }

    # Save
    output_path = "replication_same_hub_type.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Output saved to: {output_path}")
    print(f"{'=' * 60}")

    # Summary
    print("\n" + "=" * 60)
    print("REPLICATION SUMMARY")
    print("=" * 60)
    print(f"\nPRIMARY TEST (SAME_HUB_TYPE):")
    print(f"  Status: {status}")
    print(f"  Vocabulary analysis: {output['replication_result']['vocabulary_analysis_validity']}")
    print(f"\nSECONDARY TEST (SAME_CATEGORY):")
    print(f"  Status: {cat_status}")

    return output


if __name__ == "__main__":
    main()
