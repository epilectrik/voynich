"""
AZC Projection Engine - Zone-Indexed Legality Projection.

Projects a Currier A constraint bundle through AZC legality fields
to determine zone-dependent reachability.

Per the model:
> AZC projects constraint bundles into position-indexed legality fields.
> AZC is not just "what's allowed" but WHEN it is allowed.

Key constraint: C313 - Position constrains legality, not prediction.
"""

from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional
from enum import Enum

from core.constraint_bundle import ConstraintBundle
from core.data_loader import (
    get_data_store,
    get_all_azc_folios,
    get_azc_folio,
    get_classes_for_middle,
    DataStore
)


# =============================================================================
# ZONE DEFINITIONS
# =============================================================================

# Standard zone progression (C -> P -> R1 -> R2 -> R3 -> S)
ZONES = ['C', 'P', 'R1', 'R2', 'R3', 'S']

# Default legality for MIDDLEs without explicit zone restrictions
# Per C313, C469, C472: Missing zone data = unrestricted carrier (legal everywhere)
ALL_ZONES = frozenset({'C', 'P', 'R', 'S'})

# Zone survival profiles (simplified from middle_zone_survival.json)
# These represent typical MIDDLE survival patterns by zone
# Cluster 1: S-dominant (survive longest)
# Cluster 2: P-dominant (fade after P)
# Cluster 3: R-dominant (fade in later R zones)


class ZoneStatus(Enum):
    """Status of a MIDDLE in a zone."""
    AVAILABLE = "available"      # MIDDLE is legal in this zone
    FADING = "fading"           # MIDDLE is becoming restricted
    UNAVAILABLE = "unavailable"  # MIDDLE is not legal


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ZoneReachability:
    """Reachability state for a single zone within an AZC folio."""
    zone: str
    available_middles: Set[str]
    unavailable_middles: Set[str]
    reachable_classes: Set[int]
    pruned_classes: Set[int]

    @property
    def is_fully_available(self) -> bool:
        """Check if all MIDDLEs are available in this zone."""
        return len(self.unavailable_middles) == 0

    @property
    def availability_ratio(self) -> float:
        """Ratio of available MIDDLEs (0.0 to 1.0)."""
        total = len(self.available_middles) + len(self.unavailable_middles)
        if total == 0:
            return 1.0  # No MIDDLEs to restrict = fully available
        return len(self.available_middles) / total


@dataclass
class AZCProjectionResult:
    """Complete projection result for one AZC folio."""
    folio: str
    section: str
    reachability_by_zone: Dict[str, ZoneReachability]

    @property
    def zones(self) -> List[str]:
        """Get zones in order."""
        return ZONES

    @property
    def is_fully_reachable(self) -> bool:
        """Check if all zones are fully available."""
        return all(
            zr.is_fully_available
            for zr in self.reachability_by_zone.values()
        )

    @property
    def reachable_through_zone(self) -> Optional[str]:
        """Get the last zone that is fully reachable."""
        last_reachable = None
        for zone in ZONES:
            zr = self.reachability_by_zone.get(zone)
            if zr and zr.is_fully_available:
                last_reachable = zone
            else:
                break
        return last_reachable

    def get_zone_status(self, zone: str) -> ZoneStatus:
        """Get the status of a zone."""
        zr = self.reachability_by_zone.get(zone)
        if not zr:
            return ZoneStatus.UNAVAILABLE
        if zr.is_fully_available:
            return ZoneStatus.AVAILABLE
        if zr.availability_ratio > 0:
            return ZoneStatus.FADING
        return ZoneStatus.UNAVAILABLE


@dataclass
class ProjectionSummary:
    """Summary of projection across all AZC folios."""
    bundle: ConstraintBundle
    results: Dict[str, AZCProjectionResult]

    @property
    def fully_reachable_folios(self) -> List[str]:
        """Folios where all zones are reachable."""
        return [
            folio for folio, result in self.results.items()
            if result.is_fully_reachable
        ]

    @property
    def partially_reachable_folios(self) -> List[str]:
        """Folios where some but not all zones are reachable."""
        return [
            folio for folio, result in self.results.items()
            if not result.is_fully_reachable and result.reachable_through_zone is not None
        ]

    @property
    def unreachable_folios(self) -> List[str]:
        """Folios where no zones are reachable."""
        return [
            folio for folio, result in self.results.items()
            if result.reachable_through_zone is None
        ]


# =============================================================================
# PROJECTION ENGINE
# =============================================================================

def _get_consolidated_zone(zone: str) -> str:
    """
    Consolidate fine-grained zones for legality lookup.

    R1, R2, R3 -> 'R' for legality
    C, P, S remain as-is
    """
    if zone.startswith('R'):
        return 'R'
    if zone.startswith('S'):
        return 'S'
    return zone


def compute_zone_reachability(
    bundle: ConstraintBundle,
    folio: str,
    zone: str,
    data_store: DataStore
) -> ZoneReachability:
    """
    Compute reachability for a single zone within an AZC folio.

    Uses three-set model per expert correction:
    1. Zone-legal MIDDLEs (ambient legality per zone)
    2. AZC folio vocabulary (compatibility domain)
    3. Effective = intersection (what constrains B grammar)

    Per C441, C442, C468, C470, C472, C473:
    AZC constraints are vocabulary-activated and bundle-specific, not global.

    The bundle selects which AZC folio compatibility region is active.
    Different A entries -> different folios -> different B reachability.
    """
    # Consolidate zone for legality lookup (R1/R2/R3 -> R)
    legality_zone = _get_consolidated_zone(zone)

    # 1. AZC folio vocabulary (compatibility domain for this folio)
    folio_middles = data_store.azc_folio_middles.get(folio, set())

    # 2. Compute effective legal MIDDLEs from folio vocabulary
    # Per C313, C469, C472: Missing zone legality = unrestricted carrier (legal everywhere)
    # Zone-restricting MIDDLEs are exceptional; non-restricting MIDDLEs are the default
    effective_legal_middles = set()
    for middle in folio_middles:
        legal_zones = data_store.middle_zone_legality.get(middle, ALL_ZONES)
        if legality_zone in legal_zones:
            effective_legal_middles.add(middle)

    # Track bundle's view (for display purposes)
    bundle_middles = bundle.middles
    bundle_available = bundle_middles & effective_legal_middles
    bundle_unavailable = bundle_middles - effective_legal_middles

    # Compute reachable classes from effective domain
    reachable = compute_reachable_classes(effective_legal_middles, data_store)
    pruned = set(range(1, 50)) - reachable

    return ZoneReachability(
        zone=zone,
        available_middles=bundle_available,
        unavailable_middles=bundle_unavailable,
        reachable_classes=reachable,
        pruned_classes=pruned
    )


def compute_reachable_classes(
    available_middles: Set[str],
    data_store: DataStore
) -> Set[int]:
    """
    Compute which instruction classes are reachable given available MIDDLEs.

    Three-category model per C085, C089, C107, C171, C485:
    1. Kernel/Boundary classes = ALWAYS reachable (load-bearing, cannot be removed)
    2. Atomic classes (no MIDDLEs) = always reachable
    3. Decomposable classes = pruned if ALL their non-empty MIDDLEs are unavailable

    The MIDDLE association on kernel classes is morphological, not a gating dependency.
    Only decomposable hazard classes lose membership when their MIDDLEs become illegal.
    """
    reachable = set(range(1, 50))  # Start with all 49 classes

    for class_id in list(reachable):
        class_obj = data_store.classes.get(class_id)
        if not class_obj:
            continue

        # CATEGORY 1: Kernel/Boundary classes - NEVER pruned
        # Per C085, C089, C107, C171, C485: these are load-bearing
        if class_id in data_store.kernel_classes:
            continue  # Always reachable

        class_middles = class_obj.middles
        if not class_middles:
            # CATEGORY 2: Atomic class (no MIDDLEs) = always reachable
            continue

        # Filter out empty string MIDDLEs - these represent "null MIDDLE" tokens
        # which don't impose any specific MIDDLE requirement
        effective_class_middles = {m for m in class_middles if m}

        if not effective_class_middles:
            # Class only has null MIDDLE = no specific MIDDLE requirement = always reachable
            continue

        # CATEGORY 3: Decomposable class - pruned if NO effective middles are available
        if not (effective_class_middles & available_middles):
            reachable.discard(class_id)

    return reachable


def project_to_folio(
    bundle: ConstraintBundle,
    folio: str,
    data_store: DataStore
) -> AZCProjectionResult:
    """
    Project a constraint bundle through a single AZC folio.

    Computes zone-indexed reachability for all zones.
    """
    azc_folio = get_azc_folio(folio)
    section = azc_folio.section if azc_folio else 'U'

    reachability_by_zone = {}
    for zone in ZONES:
        reachability_by_zone[zone] = compute_zone_reachability(
            bundle, folio, zone, data_store
        )

    return AZCProjectionResult(
        folio=folio,
        section=section,
        reachability_by_zone=reachability_by_zone
    )


def project_bundle(bundle: ConstraintBundle) -> ProjectionSummary:
    """
    Project a constraint bundle through all AZC folios.

    This is the main entry point for AZC projection.

    Args:
        bundle: The constraint bundle from a Currier A entry

    Returns:
        ProjectionSummary with results for all AZC folios
    """
    data_store = get_data_store()
    results = {}

    for folio in get_all_azc_folios():
        results[folio] = project_to_folio(bundle, folio, data_store)

    return ProjectionSummary(bundle=bundle, results=results)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_zone_availability_summary(
    summary: ProjectionSummary
) -> Dict[str, Dict[str, ZoneStatus]]:
    """
    Get a summary of zone availability across all folios.

    Returns a dict mapping folio -> zone -> status
    """
    result = {}
    for folio, projection in summary.results.items():
        result[folio] = {
            zone: projection.get_zone_status(zone)
            for zone in ZONES
        }
    return result


if __name__ == "__main__":
    from .constraint_bundle import compute_bundle

    # Test projection
    test_tokens = ['chedy', 'qokaiin', 'shey', 'ol']

    print("AZC Projection Test")
    print("=" * 70)

    for token in test_tokens:
        bundle = compute_bundle(token)
        summary = project_bundle(bundle)

        print(f"\n{token} (MIDDLEs: {bundle.middles or 'none'}):")
        print(f"  Fully reachable: {len(summary.fully_reachable_folios)} folios")
        print(f"  Partially reachable: {len(summary.partially_reachable_folios)} folios")
        print(f"  Unreachable: {len(summary.unreachable_folios)} folios")

        # Show first few results
        for i, (folio, result) in enumerate(list(summary.results.items())[:3]):
            status_str = " ".join([
                f"{z}:{result.get_zone_status(z).name[:3]}"
                for z in ZONES
            ])
            print(f"    {folio}: {status_str}")
