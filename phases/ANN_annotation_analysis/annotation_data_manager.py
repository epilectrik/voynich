#!/usr/bin/env python3
"""
Data Manager for Comparative Annotation System.

Handles:
- Mode A and Mode B annotation record storage
- Auto-save on every response
- Response time logging and weighting
- Duplicate checking
- Session management
- Aggregation methods for analysis
"""

import json
import os
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Set
from collections import Counter, defaultdict

from annotation_config import (
    get_response_weight, AGGREGATION_CONFIG, SESSION_CONFIG,
    QUESTIONS_MODE_A, QUESTIONS_MODE_B
)


# =============================================================================
# DATA DIRECTORY
# =============================================================================

DATA_DIR = os.path.join(os.path.dirname(__file__), "annotation_data")


def ensure_data_dir():
    """Ensure data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)


# =============================================================================
# ANNOTATION RECORDS
# =============================================================================

@dataclass
class ModeARecord:
    """Single-image annotation record."""
    annotation_id: str
    mode: str  # Always "A"
    folio_id: str
    question_id: str
    response: str
    response_time_ms: int
    response_weight: float
    timestamp: str
    session_id: str
    is_duplicate_check: bool
    flags: List[str]


@dataclass
class ModeBRecord:
    """Comparative annotation record."""
    annotation_id: str
    mode: str  # Always "B"
    folio_ids: List[str]
    folio_positions: Dict[str, str]
    question_id: str
    response: str
    response_time_ms: int
    response_weight: float
    timestamp: str
    session_id: str
    group_type: str
    group_basis: str
    is_null_group: bool
    is_foil_group: bool
    is_duplicate_check: bool
    flags: List[str]


# =============================================================================
# DATA MANAGER
# =============================================================================

class AnnotationDataManager:
    """
    Manages all annotation data I/O and aggregation.
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize data manager.

        Args:
            session_id: Optional session ID. If not provided, generates new one.
        """
        ensure_data_dir()

        self.session_id = session_id or str(uuid.uuid4())
        self.session_start = datetime.now()

        # File paths
        self.mode_a_file = os.path.join(DATA_DIR, "mode_a_annotations.json")
        self.mode_b_file = os.path.join(DATA_DIR, "mode_b_annotations.json")
        self.session_log_file = os.path.join(DATA_DIR, "session_log.json")

        # Load existing data
        self.mode_a_records: List[ModeARecord] = self._load_mode_a()
        self.mode_b_records: List[ModeBRecord] = self._load_mode_b()
        self.session_log: Dict = self._load_session_log()

        # Track current session
        self.current_session_records: List = []
        self.duplicate_checks_passed = 0
        self.duplicate_checks_failed = 0

        # Track folio-question pairs for Mode A (to avoid repeats)
        self.session_folio_questions: Set[Tuple[str, str]] = set()

    def _load_mode_a(self) -> List[ModeARecord]:
        """Load existing Mode A records."""
        if not os.path.exists(self.mode_a_file):
            return []

        with open(self.mode_a_file, 'r') as f:
            data = json.load(f)

        return [ModeARecord(**r) for r in data.get('records', [])]

    def _load_mode_b(self) -> List[ModeBRecord]:
        """Load existing Mode B records."""
        if not os.path.exists(self.mode_b_file):
            return []

        with open(self.mode_b_file, 'r') as f:
            data = json.load(f)

        return [ModeBRecord(**r) for r in data.get('records', [])]

    def _load_session_log(self) -> Dict:
        """Load session log."""
        if not os.path.exists(self.session_log_file):
            return {"sessions": []}

        with open(self.session_log_file, 'r') as f:
            return json.load(f)

    def _save_mode_a(self):
        """Save Mode A records."""
        data = {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_records": len(self.mode_a_records)
            },
            "records": [asdict(r) for r in self.mode_a_records]
        }

        with open(self.mode_a_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_mode_b(self):
        """Save Mode B records."""
        data = {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_records": len(self.mode_b_records)
            },
            "records": [asdict(r) for r in self.mode_b_records]
        }

        with open(self.mode_b_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_session_log(self):
        """Save session log."""
        with open(self.session_log_file, 'w') as f:
            json.dump(self.session_log, f, indent=2)

    def record_mode_a(
        self,
        folio_id: str,
        question_id: str,
        response: str,
        response_time_ms: int,
        is_duplicate_check: bool = False
    ) -> ModeARecord:
        """
        Record a Mode A annotation.

        Args:
            folio_id: The folio being annotated
            question_id: The question being answered
            response: The selected response
            response_time_ms: Time taken to respond
            is_duplicate_check: Whether this is a duplicate check

        Returns:
            The created record
        """
        weight, flags = get_response_weight(response_time_ms)

        record = ModeARecord(
            annotation_id=str(uuid.uuid4()),
            mode="A",
            folio_id=folio_id,
            question_id=question_id,
            response=response,
            response_time_ms=response_time_ms,
            response_weight=weight,
            timestamp=datetime.now().isoformat(),
            session_id=self.session_id,
            is_duplicate_check=is_duplicate_check,
            flags=flags
        )

        self.mode_a_records.append(record)
        self.current_session_records.append(record)
        self.session_folio_questions.add((folio_id, question_id))

        # Auto-save
        self._save_mode_a()

        return record

    def record_mode_b(
        self,
        folio_ids: List[str],
        folio_positions: Dict[str, str],
        question_id: str,
        response: str,
        response_time_ms: int,
        group_type: str,
        group_basis: str,
        is_null_group: bool,
        is_foil_group: bool,
        is_duplicate_check: bool = False
    ) -> ModeBRecord:
        """
        Record a Mode B annotation.

        Args:
            folio_ids: List of folios in the group
            folio_positions: Mapping of folio_id to position label
            question_id: The question being answered
            response: The selected response
            response_time_ms: Time taken to respond
            group_type: Type of group (e.g., "same_category")
            group_basis: Basis for grouping (e.g., category name)
            is_null_group: Whether this is a null (random) group
            is_foil_group: Whether this is a foil (known-different) group
            is_duplicate_check: Whether this is a duplicate check

        Returns:
            The created record
        """
        weight, flags = get_response_weight(response_time_ms)

        record = ModeBRecord(
            annotation_id=str(uuid.uuid4()),
            mode="B",
            folio_ids=folio_ids,
            folio_positions=folio_positions,
            question_id=question_id,
            response=response,
            response_time_ms=response_time_ms,
            response_weight=weight,
            timestamp=datetime.now().isoformat(),
            session_id=self.session_id,
            group_type=group_type,
            group_basis=group_basis,
            is_null_group=is_null_group,
            is_foil_group=is_foil_group,
            is_duplicate_check=is_duplicate_check,
            flags=flags
        )

        self.mode_b_records.append(record)
        self.current_session_records.append(record)

        # Auto-save
        self._save_mode_b()

        return record

    def has_folio_question_in_session(self, folio_id: str, question_id: str) -> bool:
        """Check if this folio-question pair was already asked this session."""
        return (folio_id, question_id) in self.session_folio_questions

    def get_session_question_count(self) -> int:
        """Get number of questions answered in current session."""
        return len(self.current_session_records)

    def get_session_flag_count(self) -> int:
        """Get total flags in current session."""
        return sum(len(r.flags) for r in self.current_session_records)

    def get_recent_consecutive_flags(self, n: int = 3) -> int:
        """Get count of flags in last n responses."""
        recent = self.current_session_records[-n:]
        return sum(len(r.flags) for r in recent)

    def end_session(self):
        """Record session end and save session log."""
        session_info = {
            "session_id": self.session_id,
            "start_time": self.session_start.isoformat(),
            "end_time": datetime.now().isoformat(),
            "mode_a_count": sum(1 for r in self.current_session_records if r.mode == "A"),
            "mode_b_count": sum(1 for r in self.current_session_records if r.mode == "B"),
            "total_flags": self.get_session_flag_count(),
            "duplicate_checks_passed": self.duplicate_checks_passed,
            "duplicate_checks_failed": self.duplicate_checks_failed,
        }

        self.session_log["sessions"].append(session_info)
        self._save_session_log()

    # =========================================================================
    # AGGREGATION METHODS
    # =========================================================================

    def aggregate_mode_a(self) -> Dict[str, Dict[str, Dict]]:
        """
        Aggregate Mode A responses by folio and feature.

        Returns dict: {folio_id: {feature: {mode, agreement, status, responses}}}
        """
        # Group by (folio_id, question_id)
        grouped = defaultdict(list)
        for r in self.mode_a_records:
            if not r.is_duplicate_check:
                grouped[(r.folio_id, r.question_id)].append(r)

        results = defaultdict(dict)

        for (folio_id, question_id), records in grouped.items():
            # Get target feature from question config
            question_config = QUESTIONS_MODE_A.get(question_id, {})
            feature = question_config.get("target_feature", question_id)

            # Weighted vote
            weighted_votes = Counter()
            total_weight = 0

            for r in records:
                weighted_votes[r.response] += r.response_weight
                total_weight += r.response_weight

            if total_weight == 0:
                continue

            # Find mode
            mode_response, mode_weight = weighted_votes.most_common(1)[0]
            agreement = mode_weight / total_weight

            # Determine status
            if agreement >= AGGREGATION_CONFIG["clear_threshold"]:
                status = "CLEAR"
            elif agreement >= AGGREGATION_CONFIG["weak_threshold"]:
                status = "WEAK"
            else:
                status = "AMBIGUOUS"

            results[folio_id][feature] = {
                "mode": mode_response,
                "agreement": round(agreement, 3),
                "status": status,
                "n_responses": len(records),
                "total_weight": round(total_weight, 2),
                "all_responses": dict(weighted_votes)
            }

        return dict(results)

    def aggregate_mode_b_cohesion(self) -> Dict[str, Dict]:
        """
        Compute cohesion scores for Mode B groups.

        Returns dict: {group_type: {cohesion_score, outlier_rate, n_groups, ...}}
        """
        # Group by group_type
        by_type = defaultdict(list)
        for r in self.mode_b_records:
            if not r.is_duplicate_check:
                by_type[r.group_type].append(r)

        results = {}

        for group_type, records in by_type.items():
            # Separate by question type
            by_question = defaultdict(list)
            for r in records:
                by_question[r.question_id].append(r)

            # Compute cohesion for outlier detection
            outlier_records = by_question.get("outlier_detection", [])
            if outlier_records:
                # Cohesion = proportion NOT identifying an outlier
                coherent = sum(1 for r in outlier_records
                              if r.response in ["NONE_STAND_OUT", "ALL_SIMILAR"])
                outlier_rate = 1 - (coherent / len(outlier_records))
            else:
                outlier_rate = None

            # Compute cohesion for similarity questions
            similarity_questions = ["compare_leaf_similarity", "compare_root_similarity"]
            coherent_responses = 0
            total_similarity = 0

            for q in similarity_questions:
                for r in by_question.get(q, []):
                    total_similarity += 1
                    if r.response in ["YES_CLEARLY", "YES_SOMEWHAT"]:
                        coherent_responses += 1

            if total_similarity > 0:
                cohesion_score = coherent_responses / total_similarity
            else:
                cohesion_score = None

            results[group_type] = {
                "n_records": len(records),
                "cohesion_score": round(cohesion_score, 3) if cohesion_score else None,
                "outlier_rate": round(outlier_rate, 3) if outlier_rate else None,
                "is_hypothesis": not any(r.is_null_group for r in records),
                "is_foil": any(r.is_foil_group for r in records)
            }

        return results

    def compute_reliability(self) -> Dict:
        """
        Compute intra-annotator reliability from duplicate checks.

        Returns dict with consistency metrics.
        """
        # Find duplicate pairs in Mode A
        mode_a_duplicates = [r for r in self.mode_a_records if r.is_duplicate_check]

        # Match with original responses
        # Group non-duplicates by (folio, question)
        originals = defaultdict(list)
        for r in self.mode_a_records:
            if not r.is_duplicate_check:
                originals[(r.folio_id, r.question_id)].append(r.response)

        matches = 0
        total = 0

        for dup in mode_a_duplicates:
            key = (dup.folio_id, dup.question_id)
            if key in originals:
                # Check if duplicate response matches any original
                if dup.response in originals[key]:
                    matches += 1
                total += 1

        if total > 0:
            consistency = matches / total
        else:
            consistency = None

        # Determine status
        if consistency is None:
            status = "INSUFFICIENT_DATA"
        elif consistency >= AGGREGATION_CONFIG["intra_annotator_good"]:
            status = "GOOD"
        elif consistency >= AGGREGATION_CONFIG["intra_annotator_acceptable"]:
            status = "ACCEPTABLE"
        else:
            status = "BELOW_ACCEPTABLE"

        return {
            "intra_annotator_consistency": round(consistency, 3) if consistency else None,
            "duplicate_checks_total": total,
            "duplicate_checks_matched": matches,
            "status": status
        }

    def export_aggregated_features(self, output_file: Optional[str] = None) -> str:
        """
        Export aggregated features for pipeline integration.

        Args:
            output_file: Output path. If None, uses default.

        Returns:
            Path to output file.
        """
        output_file = output_file or os.path.join(DATA_DIR, "aggregated_features.json")

        aggregated = self.aggregate_mode_a()

        data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "source": "annotation_data_manager",
                "aggregation_thresholds": {
                    "clear": AGGREGATION_CONFIG["clear_threshold"],
                    "weak": AGGREGATION_CONFIG["weak_threshold"]
                }
            },
            "folios": aggregated
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        return output_file

    def export_cohesion_analysis(self, output_file: Optional[str] = None) -> str:
        """
        Export cohesion analysis for Mode B.

        Args:
            output_file: Output path. If None, uses default.

        Returns:
            Path to output file.
        """
        output_file = output_file or os.path.join(DATA_DIR, "cohesion_analysis.json")

        cohesion = self.aggregate_mode_b_cohesion()

        data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "source": "annotation_data_manager",
                "cohesion_thresholds": {
                    "significant": AGGREGATION_CONFIG["cohesion_significant"],
                    "suggestive": AGGREGATION_CONFIG["cohesion_suggestive"]
                }
            },
            "group_cohesion": cohesion
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        return output_file

    def export_reliability_report(self, output_file: Optional[str] = None) -> str:
        """
        Export reliability report.

        Args:
            output_file: Output path. If None, uses default.

        Returns:
            Path to output file.
        """
        output_file = output_file or os.path.join(DATA_DIR, "reliability_report.json")

        reliability = self.compute_reliability()

        data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "source": "annotation_data_manager",
                "thresholds": {
                    "acceptable": AGGREGATION_CONFIG["intra_annotator_acceptable"],
                    "good": AGGREGATION_CONFIG["intra_annotator_good"]
                }
            },
            "reliability": reliability
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        return output_file

    def get_statistics(self) -> Dict:
        """Get overall annotation statistics."""
        return {
            "mode_a_total": len(self.mode_a_records),
            "mode_b_total": len(self.mode_b_records),
            "mode_a_unique_folios": len(set(r.folio_id for r in self.mode_a_records)),
            "mode_b_unique_groups": len(set(
                tuple(sorted(r.folio_ids)) for r in self.mode_b_records
            )),
            "total_sessions": len(self.session_log.get("sessions", [])),
            "current_session_count": len(self.current_session_records)
        }


if __name__ == "__main__":
    # Test the data manager
    print("Testing AnnotationDataManager...")
    print("=" * 60)

    manager = AnnotationDataManager()

    print(f"Session ID: {manager.session_id}")
    print(f"\nCurrent statistics:")
    for key, value in manager.get_statistics().items():
        print(f"  {key}: {value}")

    # Simulate some annotations
    print("\n" + "=" * 60)
    print("Simulating annotations...")
    print("=" * 60)

    # Mode A
    record_a = manager.record_mode_a(
        folio_id="f38r",
        question_id="leaf_shape_primary",
        response="LOBED",
        response_time_ms=5000
    )
    print(f"\nRecorded Mode A: {record_a.annotation_id}")
    print(f"  Response weight: {record_a.response_weight}")
    print(f"  Flags: {record_a.flags}")

    # Mode B
    record_b = manager.record_mode_b(
        folio_ids=["f38r", "f25r", "f11r", "f42r"],
        folio_positions={"f38r": "A", "f25r": "B", "f11r": "C", "f42r": "D"},
        question_id="outlier_detection",
        response="NONE_STAND_OUT",
        response_time_ms=8000,
        group_type="same_category",
        group_basis="test",
        is_null_group=False,
        is_foil_group=False
    )
    print(f"\nRecorded Mode B: {record_b.annotation_id}")
    print(f"  Response weight: {record_b.response_weight}")
    print(f"  Flags: {record_b.flags}")

    print("\n" + "=" * 60)
    print("Updated statistics:")
    for key, value in manager.get_statistics().items():
        print(f"  {key}: {value}")

    # Test aggregation
    print("\n" + "=" * 60)
    print("Testing aggregation...")
    print("=" * 60)

    aggregated = manager.aggregate_mode_a()
    print(f"\nAggregated Mode A: {len(aggregated)} folios")

    cohesion = manager.aggregate_mode_b_cohesion()
    print(f"Mode B cohesion analysis: {len(cohesion)} group types")

    reliability = manager.compute_reliability()
    print(f"Reliability status: {reliability['status']}")

    print("\nData manager test complete.")
