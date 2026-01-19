"""
Sufficiency Engine - REGIME Completeness Checking.

Per X.14 (Curriculum Completeness Model):
- REGIME_4: min_link_ratio >= 25% (monitoring completeness)
- REGIME_3: min_recovery_ops >= 2 (recovery completeness)
- REGIME_2/1: No minimum thresholds

This is Tier 3 interpretation. Sufficiency is surfaced, not enforced (OJLM-1).

The key distinction (expert-validated):
- LEGALITY: What's AZC-compatible (existing reachability status)
- SUFFICIENCY: Whether a folio meets completeness thresholds for its REGIME

"Programs may remain legal while becoming non-executable under stricter
completeness regimes. Such programs are not removed, only flagged."
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from core.data_loader import DataStore, FolioMetrics


class SufficiencyStatus(Enum):
    """Sufficiency status for a B folio under its REGIME."""
    SUFFICIENT = "SUFFICIENT"      # Meets all REGIME requirements
    INSUFFICIENT = "INSUFFICIENT"  # Below threshold for assigned REGIME
    NOT_APPLICABLE = "N/A"         # REGIME_2/1 have no thresholds


@dataclass
class FolioSufficiency:
    """
    Sufficiency result for a B folio.

    Contains both the status and the underlying metrics that
    determined it, enabling transparent display to the user.
    """
    folio: str
    regime: str
    status: SufficiencyStatus

    # Actual metrics
    link_density: float
    recovery_ops: int

    # Thresholds for display (None if no threshold applies)
    required_link: Optional[float]      # 0.25 for R4, None otherwise
    required_recovery: Optional[int]    # 2 for R3, None otherwise

    # Shortfall details (None if sufficient or N/A)
    missing_link_pct: Optional[float]   # How far below threshold
    missing_recovery: Optional[int]     # How many short


# REGIME completeness thresholds from X.14
# Per C179-C185: 4 stable regimes from OPS-2 K-Means clustering
# CEI ordering: REGIME_2 < REGIME_1 < REGIME_4 < REGIME_3
REGIME_THRESHOLDS = {
    "REGIME_2": {"link_density": None, "recovery_ops": None},
    "REGIME_1": {"link_density": None, "recovery_ops": None},
    "REGIME_4": {"link_density": 0.25, "recovery_ops": None},
    "REGIME_3": {"link_density": None, "recovery_ops": 2},
}


def compute_sufficiency(folio: str, data_store: DataStore) -> FolioSufficiency:
    """
    Compute sufficiency status for a B folio.

    Per X.14 (Curriculum Completeness Model):
    - REGIME_4 requires link_density >= 0.25 (monitoring completeness)
    - REGIME_3 requires recovery_ops_count >= 2 (recovery completeness)
    - REGIME_2/1 have no minimum thresholds

    This is Tier 3 interpretation. Sufficiency is surfaced, not enforced (OJLM-1).
    Per C197: Expert-only design means we surface info, we don't decide.
    Per C458: Risk is clamped globally; sufficiency varies locally.

    Args:
        folio: B folio name
        data_store: Loaded data store with metrics and REGIME assignments

    Returns:
        FolioSufficiency with status and supporting details
    """
    regime = data_store.regime_assignments.get(folio, "")
    metrics = data_store.folio_metrics.get(folio)

    # Handle missing data
    if not regime or not metrics:
        return FolioSufficiency(
            folio=folio,
            regime=regime or "UNKNOWN",
            status=SufficiencyStatus.NOT_APPLICABLE,
            link_density=metrics.link_density if metrics else 0.0,
            recovery_ops=metrics.recovery_ops_count if metrics else 0,
            required_link=None,
            required_recovery=None,
            missing_link_pct=None,
            missing_recovery=None
        )

    thresholds = REGIME_THRESHOLDS.get(regime, {})
    req_link = thresholds.get("link_density")
    req_recovery = thresholds.get("recovery_ops")

    # Check thresholds
    is_sufficient = True
    missing_link = None
    missing_recovery = None

    if req_link is not None and metrics.link_density < req_link:
        is_sufficient = False
        missing_link = req_link - metrics.link_density

    if req_recovery is not None and metrics.recovery_ops_count < req_recovery:
        is_sufficient = False
        missing_recovery = req_recovery - metrics.recovery_ops_count

    # REGIME_2/1 have no thresholds - always N/A
    if req_link is None and req_recovery is None:
        status = SufficiencyStatus.NOT_APPLICABLE
    else:
        status = SufficiencyStatus.SUFFICIENT if is_sufficient else SufficiencyStatus.INSUFFICIENT

    return FolioSufficiency(
        folio=folio,
        regime=regime,
        status=status,
        link_density=metrics.link_density,
        recovery_ops=metrics.recovery_ops_count,
        required_link=req_link,
        required_recovery=req_recovery,
        missing_link_pct=missing_link,
        missing_recovery=missing_recovery
    )


def compute_all_sufficiency(data_store: DataStore) -> dict[str, FolioSufficiency]:
    """
    Compute sufficiency for all B folios with REGIME assignments.

    Returns:
        Dict mapping folio name to FolioSufficiency
    """
    results = {}
    for folio in data_store.regime_assignments.keys():
        results[folio] = compute_sufficiency(folio, data_store)
    return results
