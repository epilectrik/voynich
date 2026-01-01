#!/usr/bin/env python3
"""
Analysis Integration for Comparative Annotation System.

Provides:
- Hypothesis testing for Mode B cohesion
- Permutation tests comparing hypothesis vs null groups
- Foil calibration analysis
- Integration with existing correlation pipeline
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass
import numpy as np

from annotation_config import AGGREGATION_CONFIG, GroupType
from annotation_data_manager import AnnotationDataManager, DATA_DIR


@dataclass
class HypothesisTestResult:
    """Result of a hypothesis test."""
    group_type: str
    n_hypothesis_groups: int
    n_null_groups: int
    hypothesis_cohesion: float
    null_cohesion: float
    effect_size: float
    null_percentile: float
    p_value: float
    significant: bool


class AnnotationAnalyzer:
    """
    Performs statistical analysis on annotation data.
    """

    def __init__(self, data_manager: Optional[AnnotationDataManager] = None):
        """
        Initialize analyzer.

        Args:
            data_manager: Data manager instance. If None, loads fresh.
        """
        self.data_manager = data_manager or AnnotationDataManager()

    def compute_mode_b_statistics(self) -> Dict[str, Dict]:
        """
        Compute detailed Mode B statistics by group type.

        Returns:
            Dict with statistics per group type
        """
        records = self.data_manager.mode_b_records

        # Group by group_type
        by_type = defaultdict(list)
        for r in records:
            if not r.is_duplicate_check:
                by_type[r.group_type].append(r)

        results = {}

        for group_type, group_records in by_type.items():
            # Outlier detection analysis
            outlier_responses = [
                r for r in group_records
                if r.question_id == "outlier_detection"
            ]

            if outlier_responses:
                none_stand_out = sum(
                    1 for r in outlier_responses
                    if r.response in ["NONE_STAND_OUT", "ALL_SIMILAR", "CANNOT_TELL"]
                )
                coherent_rate = none_stand_out / len(outlier_responses)
                outlier_detected_rate = 1 - coherent_rate
            else:
                coherent_rate = None
                outlier_detected_rate = None

            # Similarity question analysis
            similarity_responses = [
                r for r in group_records
                if r.question_id in ["compare_leaf_similarity", "compare_root_similarity"]
            ]

            if similarity_responses:
                yes_responses = sum(
                    1 for r in similarity_responses
                    if r.response in ["YES_CLEARLY", "YES_SOMEWHAT"]
                )
                similarity_cohesion = yes_responses / len(similarity_responses)
            else:
                similarity_cohesion = None

            # Compute overall cohesion score
            if coherent_rate is not None and similarity_cohesion is not None:
                cohesion_score = (coherent_rate + similarity_cohesion) / 2
            elif coherent_rate is not None:
                cohesion_score = coherent_rate
            elif similarity_cohesion is not None:
                cohesion_score = similarity_cohesion
            else:
                cohesion_score = None

            # Response time statistics
            response_times = [r.response_time_ms for r in group_records]
            avg_response_time = np.mean(response_times) if response_times else None

            results[group_type] = {
                "n_records": len(group_records),
                "coherent_rate": round(coherent_rate, 3) if coherent_rate else None,
                "outlier_detected_rate": round(outlier_detected_rate, 3) if outlier_detected_rate else None,
                "similarity_cohesion": round(similarity_cohesion, 3) if similarity_cohesion else None,
                "overall_cohesion": round(cohesion_score, 3) if cohesion_score else None,
                "avg_response_time_ms": round(avg_response_time, 1) if avg_response_time else None,
                "is_hypothesis": group_type in [
                    gt.value for gt in [
                        GroupType.SAME_CATEGORY, GroupType.SAME_HUB_TYPE,
                        GroupType.SAME_PREFIX, GroupType.SAME_CLUSTER
                    ]
                ]
            }

        return results

    def permutation_test(
        self,
        hypothesis_type: str,
        null_type: str = "random",
        n_permutations: int = 10000,
        seed: Optional[int] = None
    ) -> Optional[HypothesisTestResult]:
        """
        Perform permutation test comparing hypothesis vs null groups.

        Args:
            hypothesis_type: The hypothesis group type to test
            null_type: The null group type for comparison
            n_permutations: Number of permutations for null distribution
            seed: Random seed

        Returns:
            HypothesisTestResult or None if insufficient data
        """
        rng = random.Random(seed)

        records = self.data_manager.mode_b_records
        non_dup = [r for r in records if not r.is_duplicate_check]

        # Get hypothesis and null groups
        hypothesis_records = [r for r in non_dup if r.group_type == hypothesis_type]
        null_records = [r for r in non_dup if r.group_type == null_type]

        if len(hypothesis_records) < 5 or len(null_records) < 5:
            return None

        # Compute observed cohesion scores
        def compute_cohesion(records: List) -> float:
            coherent = sum(
                1 for r in records
                if (r.question_id == "outlier_detection" and
                    r.response in ["NONE_STAND_OUT", "ALL_SIMILAR"]) or
                   (r.question_id in ["compare_leaf_similarity", "compare_root_similarity"] and
                    r.response in ["YES_CLEARLY", "YES_SOMEWHAT"])
            )
            relevant = sum(
                1 for r in records
                if r.question_id in ["outlier_detection", "compare_leaf_similarity", "compare_root_similarity"]
            )
            return coherent / relevant if relevant > 0 else 0.5

        observed_hypothesis = compute_cohesion(hypothesis_records)
        observed_null = compute_cohesion(null_records)
        observed_diff = observed_hypothesis - observed_null

        # Permutation test
        all_records = hypothesis_records + null_records
        n_hyp = len(hypothesis_records)

        null_diffs = []
        for _ in range(n_permutations):
            rng.shuffle(all_records)
            perm_hyp = all_records[:n_hyp]
            perm_null = all_records[n_hyp:]
            null_diff = compute_cohesion(perm_hyp) - compute_cohesion(perm_null)
            null_diffs.append(null_diff)

        # Compute p-value (one-tailed: hypothesis > null)
        null_diffs = np.array(null_diffs)
        p_value = np.mean(null_diffs >= observed_diff)
        percentile = np.mean(null_diffs <= observed_diff) * 100

        # Effect size (Cohen's d approximation)
        if np.std(null_diffs) > 0:
            effect_size = observed_diff / np.std(null_diffs)
        else:
            effect_size = 0

        return HypothesisTestResult(
            group_type=hypothesis_type,
            n_hypothesis_groups=len(hypothesis_records),
            n_null_groups=len(null_records),
            hypothesis_cohesion=round(observed_hypothesis, 3),
            null_cohesion=round(observed_null, 3),
            effect_size=round(effect_size, 3),
            null_percentile=round(percentile, 1),
            p_value=round(p_value, 4),
            significant=p_value < AGGREGATION_CONFIG["null_p_value_threshold"]
        )

    def analyze_foil_calibration(self) -> Dict:
        """
        Analyze foil group performance for quality control.

        Returns:
            Dict with foil calibration metrics
        """
        records = self.data_manager.mode_b_records

        foil_records = [
            r for r in records
            if r.is_foil_group and not r.is_duplicate_check
        ]

        if not foil_records:
            return {
                "status": "NO_FOIL_DATA",
                "message": "No foil group responses recorded"
            }

        # Outlier detection in foil groups
        outlier_responses = [
            r for r in foil_records
            if r.question_id == "outlier_detection"
        ]

        if outlier_responses:
            # In foil groups, we EXPECT outliers to be detected
            outlier_detected = sum(
                1 for r in outlier_responses
                if r.response not in ["NONE_STAND_OUT", "ALL_SIMILAR", "CANNOT_TELL"]
            )
            detection_rate = outlier_detected / len(outlier_responses)

            # Threshold: at least 50% should detect outliers
            calibration_passed = detection_rate >= 0.5

            return {
                "status": "CALIBRATION_PASSED" if calibration_passed else "CALIBRATION_FAILED",
                "outlier_detection_rate": round(detection_rate, 3),
                "n_foil_responses": len(outlier_responses),
                "threshold": 0.5,
                "interpretation": (
                    "Human discrimination is reliable" if calibration_passed
                    else "Human discrimination may be unreliable - interpret results cautiously"
                )
            }

        return {
            "status": "NO_OUTLIER_QUESTIONS",
            "n_foil_responses": len(foil_records)
        }

    def run_full_analysis(self) -> Dict:
        """
        Run complete analysis pipeline.

        Returns:
            Dict with all analysis results
        """
        # Mode A aggregation
        mode_a_aggregated = self.data_manager.aggregate_mode_a()

        # Mode B statistics
        mode_b_stats = self.compute_mode_b_statistics()

        # Hypothesis tests for each hypothesis type vs random
        hypothesis_tests = {}
        for hyp_type in [
            GroupType.SAME_CATEGORY.value,
            GroupType.SAME_HUB_TYPE.value,
            GroupType.SAME_PREFIX.value,
            GroupType.SAME_CLUSTER.value
        ]:
            result = self.permutation_test(
                hypothesis_type=hyp_type,
                null_type=GroupType.RANDOM.value,
                n_permutations=AGGREGATION_CONFIG["permutation_iterations"]
            )
            if result:
                hypothesis_tests[hyp_type] = {
                    "hypothesis_cohesion": result.hypothesis_cohesion,
                    "null_cohesion": result.null_cohesion,
                    "effect_size": result.effect_size,
                    "percentile": result.null_percentile,
                    "p_value": result.p_value,
                    "significant": result.significant,
                    "n_hypothesis": result.n_hypothesis_groups,
                    "n_null": result.n_null_groups
                }

        # Foil calibration
        foil_calibration = self.analyze_foil_calibration()

        # Reliability
        reliability = self.data_manager.compute_reliability()

        # Success criteria evaluation
        success = self._evaluate_success_criteria(
            mode_a_aggregated, mode_b_stats, hypothesis_tests, foil_calibration, reliability
        )

        return {
            "mode_a_aggregated": mode_a_aggregated,
            "mode_b_statistics": mode_b_stats,
            "hypothesis_tests": hypothesis_tests,
            "foil_calibration": foil_calibration,
            "reliability": reliability,
            "success_criteria": success
        }

    def _evaluate_success_criteria(
        self,
        mode_a: Dict,
        mode_b: Dict,
        hypothesis_tests: Dict,
        foil: Dict,
        reliability: Dict
    ) -> Dict:
        """Evaluate pre-registered success criteria."""
        criteria = {
            "mode_a_reliability": False,
            "mode_a_clear_majority": False,
            "mode_b_category_significant": False,
            "mode_b_prefix_significant": False,
            "foil_calibration_passed": False
        }

        # Mode A reliability >= 75%
        if reliability.get("intra_annotator_consistency"):
            criteria["mode_a_reliability"] = (
                reliability["intra_annotator_consistency"] >= 0.75
            )

        # Mode A clear majority >= 70% of folios
        if mode_a:
            clear_count = 0
            total_count = 0
            for folio_data in mode_a.values():
                for feature_data in folio_data.values():
                    total_count += 1
                    if feature_data.get("status") == "CLEAR":
                        clear_count += 1
            if total_count > 0:
                criteria["mode_a_clear_majority"] = (clear_count / total_count) >= 0.70

        # Mode B SAME_CATEGORY significant
        if "same_category" in hypothesis_tests:
            criteria["mode_b_category_significant"] = hypothesis_tests["same_category"]["significant"]

        # Mode B SAME_PREFIX significant
        if "same_prefix" in hypothesis_tests:
            criteria["mode_b_prefix_significant"] = hypothesis_tests["same_prefix"]["significant"]

        # Foil calibration passed
        criteria["foil_calibration_passed"] = foil.get("status") == "CALIBRATION_PASSED"

        # Overall
        criteria["overall_success"] = all([
            criteria["mode_a_reliability"],
            criteria["mode_b_category_significant"] or criteria["mode_b_prefix_significant"]
        ])

        return criteria

    def export_full_analysis(self, output_dir: Optional[str] = None) -> str:
        """
        Export complete analysis to JSON file.

        Args:
            output_dir: Output directory. Defaults to annotation_data/.

        Returns:
            Path to output file.
        """
        output_dir = output_dir or DATA_DIR
        output_file = os.path.join(output_dir, "full_analysis_results.json")

        analysis = self.run_full_analysis()

        # Convert any numpy types to Python native
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(v) for v in obj]
            return obj

        analysis = convert_numpy(analysis)

        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)

        return output_file


def main():
    """Test the analyzer."""
    print("Testing AnnotationAnalyzer...")
    print("=" * 60)

    analyzer = AnnotationAnalyzer()

    print("\nRunning full analysis...")
    analysis = analyzer.run_full_analysis()

    print("\n--- MODE A SUMMARY ---")
    mode_a = analysis["mode_a_aggregated"]
    print(f"Folios with features: {len(mode_a)}")
    for folio_id, features in list(mode_a.items())[:3]:
        print(f"  {folio_id}:")
        for feature, data in features.items():
            print(f"    {feature}: {data['mode']} ({data['status']})")

    print("\n--- MODE B STATISTICS ---")
    for group_type, stats in analysis["mode_b_statistics"].items():
        print(f"  {group_type}:")
        print(f"    Records: {stats['n_records']}")
        print(f"    Cohesion: {stats['overall_cohesion']}")

    print("\n--- HYPOTHESIS TESTS ---")
    for hyp_type, result in analysis["hypothesis_tests"].items():
        print(f"  {hyp_type}:")
        print(f"    p-value: {result['p_value']} {'*' if result['significant'] else ''}")
        print(f"    Effect size: {result['effect_size']}")

    print("\n--- FOIL CALIBRATION ---")
    print(f"  Status: {analysis['foil_calibration']['status']}")

    print("\n--- RELIABILITY ---")
    print(f"  Consistency: {analysis['reliability']['intra_annotator_consistency']}")
    print(f"  Status: {analysis['reliability']['status']}")

    print("\n--- SUCCESS CRITERIA ---")
    for criterion, passed in analysis["success_criteria"].items():
        status = "PASS" if passed else "FAIL"
        print(f"  {criterion}: {status}")

    # Export
    output_path = analyzer.export_full_analysis()
    print(f"\nAnalysis exported to: {output_path}")


if __name__ == "__main__":
    main()
