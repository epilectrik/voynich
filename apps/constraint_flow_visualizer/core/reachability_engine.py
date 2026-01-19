"""
Reachability Engine - Zone-Dependent Grammar Reachability.

Computes which Currier B folios remain reachable under a given
AZC legality field.

FRAMING (per expert correction 2026-01):
- This is about LEGALITY PROFILES, not "search results"
- Shows WHEN commitment happens, not "which procedures match"
- Different A records -> different bundles -> different legality

Legacy classification (deprecated in new API):
- REACHABLE: All required classes reachable in all zones
- CONDITIONAL: Reachable in early zones only
- UNREACHABLE: Requires pruned classes

New classification (LegalityProfile):
- Zone survival: which zones permit completion
- Commitment zone: where legality first restricts
- Execution mode: full_survival, late/mid/early_commitment, blocked

Per the model:
> Currier B executes blind grammar within the shrinking reachable space.
> Grammar remains unchanged. Only what is reachable changes.
"""

from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional, Literal
from enum import Enum

from core.data_loader import (
    get_data_store,
    DataStore,
    is_atomic_hazard,
    is_decomposable_hazard
)
from core.sufficiency_engine import (
    FolioSufficiency,
    compute_sufficiency
)
from core.azc_projection import (
    ProjectionSummary,
    AZCProjectionResult,
    ZoneReachability,
    ZONES
)
from core.constraint_bundle import (
    AZCConstraintBundle,
    BundleType,
    LegalityProfile,
    BundleRegistry,
    compute_compatible_folios,
    compute_legality_profile
)
from pathlib import Path


# =============================================================================
# CONSTANTS
# =============================================================================

# All 49 instruction classes
ALL_CLASSES = set(range(1, 50))

# Number of forbidden transitions
N_FORBIDDEN_TRANSITIONS = 17

# Cached B folio list
_b_folios: list = None


def _load_b_folios() -> list:
    """Load actual Currier B folios from transcript."""
    global _b_folios
    if _b_folios is not None:
        return _b_folios

    # Find transcript file
    candidates = [
        Path(__file__).parent.parent.parent.parent / "data" / "transcriptions" / "interlinear_full_words.txt",
        Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt"),
    ]

    transcript_path = None
    for path in candidates:
        if path.exists():
            transcript_path = path
            break

    if not transcript_path:
        # Fallback to hardcoded list if file not found
        _b_folios = [f"f{n}v" for n in range(33, 50)] + [f"f{n}r" for n in range(75, 85)]
        return _b_folios

    # Parse transcript for B folios
    b_folios_set = set()
    with open(transcript_path, 'r', encoding='utf-8') as f:
        f.readline()  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 13:
                continue
            folio = parts[2].strip('"').strip()
            language = parts[6].strip('"').strip()
            transcriber = parts[12].strip('"').strip()
            if transcriber == 'H' and language == 'B':
                b_folios_set.add(folio)

    _b_folios = sorted(b_folios_set)
    return _b_folios


class ReachabilityStatus(Enum):
    """Binary reachability status for a B folio."""
    REACHABLE = "REACHABLE"        # All zones reachable
    CONDITIONAL = "CONDITIONAL"    # Early zones only
    UNREACHABLE = "UNREACHABLE"    # No zones reachable


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class GrammarState:
    """
    State of the grammar under a legality field.

    Shows baseline vs conditioned to demonstrate:
    "Grammar unchanged. Reachable subset contracts."
    """
    # Baseline (universal, always the same)
    baseline_classes: Set[int] = field(default_factory=lambda: set(range(1, 50)))
    baseline_forbidden_pairs: int = N_FORBIDDEN_TRANSITIONS

    # Conditioned (under legality field)
    reachable_classes: Set[int] = field(default_factory=set)
    pruned_classes: Set[int] = field(default_factory=set)

    # Hazard class breakdown
    atomic_hazards_reachable: Set[int] = field(default_factory=set)
    decomposable_hazards_reachable: Set[int] = field(default_factory=set)
    decomposable_hazards_pruned: Set[int] = field(default_factory=set)

    @property
    def n_reachable(self) -> int:
        return len(self.reachable_classes)

    @property
    def n_pruned(self) -> int:
        return len(self.pruned_classes)

    @property
    def reachability_ratio(self) -> float:
        """Ratio of reachable classes (0.0 to 1.0)."""
        return self.n_reachable / 49

    def summary(self) -> str:
        """Human-readable summary."""
        return (
            f"{self.n_reachable}/49 classes reachable | "
            f"{self.n_pruned} pruned | "
            f"Atomic hazards: {len(self.atomic_hazards_reachable)} | "
            f"Decomposable hazards: {len(self.decomposable_hazards_reachable)} reachable, "
            f"{len(self.decomposable_hazards_pruned)} pruned"
        )


@dataclass
class FolioReachability:
    """Reachability result for a single Currier B folio."""
    folio: str
    status: ReachabilityStatus
    reachable_zones: List[str]  # Which zones the folio is reachable in
    required_classes: Set[int]
    available_classes: Set[int]
    missing_classes: Set[int]
    coverage_pct: float  # Secondary metric

    # REGIME sufficiency (Tier 3: X.14)
    # Per OJLM-1: annotate, never prune
    # Per C458: risk clamped, sufficiency varies
    sufficiency: Optional[FolioSufficiency] = None

    @property
    def is_fully_reachable(self) -> bool:
        return self.status == ReachabilityStatus.REACHABLE

    @property
    def n_zones_reachable(self) -> int:
        return len(self.reachable_zones)


@dataclass
class ReachabilityResult:
    """Complete reachability result for a constraint bundle."""
    # Grammar state (baseline vs conditioned)
    grammar_state: GrammarState

    # Per-zone grammar states
    grammar_by_zone: Dict[str, GrammarState]

    # B folio reachability
    folio_results: Dict[str, FolioReachability]

    @property
    def reachable_folios(self) -> List[FolioReachability]:
        """B folios with REACHABLE status."""
        return [
            r for r in self.folio_results.values()
            if r.status == ReachabilityStatus.REACHABLE
        ]

    @property
    def conditional_folios(self) -> List[FolioReachability]:
        """B folios with CONDITIONAL status."""
        return [
            r for r in self.folio_results.values()
            if r.status == ReachabilityStatus.CONDITIONAL
        ]

    @property
    def unreachable_folios(self) -> List[FolioReachability]:
        """B folios with UNREACHABLE status."""
        return [
            r for r in self.folio_results.values()
            if r.status == ReachabilityStatus.UNREACHABLE
        ]


# =============================================================================
# GRAMMAR STATE COMPUTATION
# =============================================================================

def compute_grammar_state(
    zone_reachability: ZoneReachability,
    data_store: DataStore
) -> GrammarState:
    """
    Compute the grammar state for a given zone reachability.

    This shows which classes are reachable vs pruned.
    """
    reachable = zone_reachability.reachable_classes.copy()
    pruned = zone_reachability.pruned_classes.copy()

    # Categorize hazard classes
    atomic_reachable = set()
    decomposable_reachable = set()
    decomposable_pruned = set()

    for class_id in data_store.hazard_classes:
        if is_atomic_hazard(class_id):
            if class_id in reachable:
                atomic_reachable.add(class_id)
        elif is_decomposable_hazard(class_id):
            if class_id in reachable:
                decomposable_reachable.add(class_id)
            else:
                decomposable_pruned.add(class_id)

    return GrammarState(
        reachable_classes=reachable,
        pruned_classes=pruned,
        atomic_hazards_reachable=atomic_reachable,
        decomposable_hazards_reachable=decomposable_reachable,
        decomposable_hazards_pruned=decomposable_pruned
    )


def aggregate_grammar_state(
    projection_result: AZCProjectionResult,
    data_store: DataStore
) -> GrammarState:
    """
    Aggregate grammar state across all zones.

    For the overall state, a class is reachable if it's reachable
    in at least one zone.
    """
    all_reachable = set()
    for zone in ZONES:
        zr = projection_result.reachability_by_zone.get(zone)
        if zr:
            all_reachable.update(zr.reachable_classes)

    pruned = ALL_CLASSES - all_reachable

    # Categorize hazard classes
    atomic_reachable = set()
    decomposable_reachable = set()
    decomposable_pruned = set()

    for class_id in data_store.hazard_classes:
        if is_atomic_hazard(class_id):
            if class_id in all_reachable:
                atomic_reachable.add(class_id)
        elif is_decomposable_hazard(class_id):
            if class_id in all_reachable:
                decomposable_reachable.add(class_id)
            else:
                decomposable_pruned.add(class_id)

    return GrammarState(
        reachable_classes=all_reachable,
        pruned_classes=pruned,
        atomic_hazards_reachable=atomic_reachable,
        decomposable_hazards_reachable=decomposable_reachable,
        decomposable_hazards_pruned=decomposable_pruned
    )


# =============================================================================
# B FOLIO REACHABILITY
# =============================================================================

def get_folio_required_classes(folio: str, data_store: DataStore) -> Set[int]:
    """
    Get the instruction classes required by a Currier B folio.

    Uses actual class footprints computed from corpus tokens via
    MIDDLE -> class mapping. NOT derived from REGIME (that would
    be invented semantics per expert correction).

    Falls back to empty set if footprint data unavailable.
    """
    return data_store.b_folio_class_footprints.get(folio, set())


def classify_folio_reachability(
    folio: str,
    grammar_by_zone: Dict[str, GrammarState],
    data_store: DataStore
) -> FolioReachability:
    """
    Classify a B folio's reachability under the legality field.

    Binary classification FIRST (REACHABLE/CONDITIONAL/UNREACHABLE),
    then coverage as secondary metric.
    """
    required = get_folio_required_classes(folio, data_store)

    # Check which zones have all required classes
    reachable_zones = []
    best_zone = None
    best_coverage = 0.0

    for zone in ZONES:
        gs = grammar_by_zone.get(zone)
        if not gs:
            continue

        available = required & gs.reachable_classes
        coverage = len(available) / len(required) if required else 1.0

        if coverage > best_coverage:
            best_coverage = coverage
            best_zone = zone

        # Zone is reachable if ALL required classes are available
        if required <= gs.reachable_classes:
            reachable_zones.append(zone)

    # Binary classification
    if len(reachable_zones) == len(ZONES):
        status = ReachabilityStatus.REACHABLE
    elif len(reachable_zones) > 0:
        status = ReachabilityStatus.CONDITIONAL
    else:
        status = ReachabilityStatus.UNREACHABLE

    # Compute missing classes from best zone
    best_gs = grammar_by_zone.get(best_zone or 'C')
    available = required & best_gs.reachable_classes if best_gs else set()
    missing = required - available

    # Compute REGIME sufficiency (Tier 3: X.14)
    # Per OJLM-1: annotate, never prune
    sufficiency = compute_sufficiency(folio, data_store)

    return FolioReachability(
        folio=folio,
        status=status,
        reachable_zones=reachable_zones,
        required_classes=required,
        available_classes=available,
        missing_classes=missing,
        coverage_pct=best_coverage * 100,
        sufficiency=sufficiency
    )


# =============================================================================
# MAIN ENGINE
# =============================================================================

def compute_reachability(
    projection_summary: ProjectionSummary
) -> ReachabilityResult:
    """
    Compute full reachability result from an AZC projection.

    This is the main entry point after AZC projection.

    Per expert model (C441, C472): Different A entries activate different
    AZC folios via MIDDLE compatibility. B reachability is evaluated against
    the grammars of compatible folios.

    Args:
        projection_summary: Result from project_bundle()

    Returns:
        ReachabilityResult with grammar state and B folio classification
    """
    data_store = get_data_store()
    bundle = projection_summary.bundle

    # Find AZC folios compatible with this bundle's MIDDLEs
    # Per C472, C437, C481: A record should activate 1-2 AZC folios max
    #
    # COMPATIBILITY RULE (per expert ruling, C442, C470, C472):
    # - Restricted MIDDLEs (1-3 folios): CAN forbid compatibility if absent
    # - Universal MIDDLEs (4+ folios): CANNOT forbid compatibility
    #
    # Universal MIDDLEs still participate in grammar computation.
    # They just cannot disqualify a folio from being activated.
    bundle_middles = bundle.middles
    compatible_folios = []

    # Identify restricted MIDDLEs in this bundle
    # Per C472: 77% of MIDDLEs are restricted (appear in 1-3 folios)
    # Per C470: only restricted MIDDLEs carry folio specificity
    #
    # IMPORTANT: MIDDLEs with spread=0 are UNKNOWN (not in AZC vocab at all)
    # Unknown MIDDLEs cannot constrain - we have no information about them
    # Only MIDDLEs that ACTUALLY appear in 1-3 AZC folios are restrictive
    restricted_bundle_middles = {
        m for m in bundle_middles
        if 1 <= data_store.middle_folio_spread.get(m, 0) <= 3
    }

    for folio_id, projection in projection_summary.results.items():
        folio_vocab = data_store.azc_folio_middles.get(folio_id, set())

        # Compatibility fails ONLY if a RESTRICTED MIDDLE is absent from folio
        # Universal MIDDLEs cannot forbid, but still exist in the bundle
        # If no restricted MIDDLEs, all folios are compatible
        missing_restricted = restricted_bundle_middles - folio_vocab
        if not missing_restricted:
            compatible_folios.append((folio_id, projection))

    # If no compatible folios, record is invalid (expected for some A entries)
    # Use empty grammar (all classes pruned) rather than fallback
    if not compatible_folios:
        grammar_by_zone = {}
        for zone in ZONES:
            grammar_by_zone[zone] = GrammarState(
                reachable_classes=set(),
                pruned_classes=ALL_CLASSES.copy(),
                atomic_hazards_reachable=set(),
                decomposable_hazards_reachable=set(),
                decomposable_hazards_pruned=data_store.decomposable_hazard_classes.copy()
            )
        overall_grammar = grammar_by_zone['C']
        b_folios = _load_b_folios()
        folio_results = {}
        for folio in b_folios:
            folio_results[folio] = classify_folio_reachability(folio, grammar_by_zone, data_store)
        return ReachabilityResult(
            grammar_state=overall_grammar,
            grammar_by_zone=grammar_by_zone,
            folio_results=folio_results
        )

    # Per expert correction (2026-01-17): Use UNION, not intersection
    # AZC folios are ALTERNATIVE legality postures, not conjunctive constraints.
    # Intersection artificially over-restricts because folios are maximally
    # orthogonal by design (C437: Jaccard ≈ 0.056).
    #
    # effective_middles = ⋃ azc_folio_middles[f] for f in active_folios
    # Then zone legality subtracts from that (subtractive semantics preserved)
    effective_middles = set()
    for folio_id, projection in compatible_folios:
        folio_vocab = data_store.azc_folio_middles.get(folio_id, set())
        effective_middles |= folio_vocab  # UNION of vocabularies

    # Now compute grammar by zone using zone legality on effective_middles
    # Import zone functions
    from core.azc_projection import _get_consolidated_zone, ALL_ZONES, compute_reachable_classes

    grammar_by_zone = {}
    for zone in ZONES:
        # Apply zone legality to effective_middles
        legality_zone = _get_consolidated_zone(zone)
        zone_legal_middles = set()
        for middle in effective_middles:
            legal_zones = data_store.middle_zone_legality.get(middle, ALL_ZONES)
            if legality_zone in legal_zones:
                zone_legal_middles.add(middle)

        # Compute class reachability from zone-legal middles
        aggregated_reachable = compute_reachable_classes(zone_legal_middles, data_store)

        # Create aggregated grammar state
        pruned = ALL_CLASSES - aggregated_reachable
        atomic_hazards_reachable = aggregated_reachable & data_store.atomic_hazard_classes
        decomposable_hazards_reachable = aggregated_reachable & data_store.decomposable_hazard_classes
        decomposable_hazards_pruned = data_store.decomposable_hazard_classes - aggregated_reachable

        grammar_by_zone[zone] = GrammarState(
            reachable_classes=aggregated_reachable,
            pruned_classes=pruned,
            atomic_hazards_reachable=atomic_hazards_reachable,
            decomposable_hazards_reachable=decomposable_hazards_reachable,
            decomposable_hazards_pruned=decomposable_hazards_pruned
        )

    # Overall grammar = zone C (most permissive)
    overall_grammar = grammar_by_zone.get('C', grammar_by_zone.get(ZONES[0]))

    # Classify all actual B folios
    b_folios = _load_b_folios()

    folio_results = {}
    for folio in b_folios:
        folio_results[folio] = classify_folio_reachability(
            folio, grammar_by_zone, data_store
        )

    return ReachabilityResult(
        grammar_state=overall_grammar,
        grammar_by_zone=grammar_by_zone,
        folio_results=folio_results
    )


def _count_active_forbidden_pairs(reachable_classes: Set[int], data_store: DataStore) -> int:
    """Count forbidden class pairs where both classes are reachable."""
    count = 0
    for from_cls, to_cls in data_store.forbidden_class_pairs:
        if from_cls in reachable_classes and to_cls in reachable_classes:
            count += 1
    return count


# =============================================================================
# NEW API: LEGALITY-BASED B FOLIO CLASSIFICATION
# =============================================================================

@dataclass
class BFolioLegality:
    """
    Legality status for a B folio under a constraint bundle.

    This replaces the misleading "reachable/conditional/unreachable" framing.
    Shows zone survival and commitment timing instead of "match" semantics.
    """
    folio: str
    status: ReachabilityStatus  # Legacy, for backward compatibility
    survives_zones: List[str]  # Which zones permit this folio
    commitment_zone: Optional[str]  # First zone where commitment occurs
    required_classes: Set[int]
    available_classes_by_zone: Dict[str, Set[int]]
    missing_classes_at_S: Set[int]
    coverage_pct_at_S: float

    @property
    def execution_mode(self) -> str:
        """
        Describe execution mode based on zone survival.

        Replaces "reachable/conditional/unreachable" with:
        - full_survival: All zones permit completion
        - late_commitment: Commits at S (terminal)
        - mid_commitment: Commits at R zones
        - early_commitment: Commits at P
        - blocked: Cannot complete in any zone
        """
        if self.commitment_zone is None:
            return "full_survival"
        elif self.commitment_zone == 'S':
            return "late_commitment"
        elif self.commitment_zone.startswith('R'):
            return "mid_commitment"
        elif self.commitment_zone == 'P':
            return "early_commitment"
        else:
            return "blocked"

    def summary(self) -> str:
        """Human-readable summary."""
        if self.execution_mode == "full_survival":
            return f"{self.folio}: Full survival (all zones)"
        elif self.execution_mode == "blocked":
            return f"{self.folio}: Blocked (no zones permit)"
        else:
            zones_str = ", ".join(self.survives_zones)
            return f"{self.folio}: {self.execution_mode} (survives: {zones_str})"


@dataclass
class BundleLegalityResult:
    """
    Complete legality result for a constraint bundle.

    This is the new API that replaces ReachabilityResult.
    Shows the bundle's legality profile and B folio classification.
    """
    bundle: AZCConstraintBundle
    profile: LegalityProfile
    grammar_by_zone: Dict[str, GrammarState]
    folio_legality: Dict[str, BFolioLegality]

    @property
    def n_full_survival(self) -> int:
        """Count of B folios with full survival."""
        return sum(1 for fl in self.folio_legality.values()
                   if fl.execution_mode == "full_survival")

    @property
    def n_blocked(self) -> int:
        """Count of blocked B folios."""
        return sum(1 for fl in self.folio_legality.values()
                   if fl.execution_mode == "blocked")

    @property
    def n_committed(self) -> int:
        """Count of B folios with early/mid/late commitment."""
        return sum(1 for fl in self.folio_legality.values()
                   if fl.execution_mode in ("early_commitment", "mid_commitment", "late_commitment"))

    def summary(self) -> str:
        """Human-readable summary."""
        return (
            f"Bundle {self.bundle.bundle_id}: {self.bundle.bundle_type.value} | "
            f"Full: {self.n_full_survival}, Committed: {self.n_committed}, "
            f"Blocked: {self.n_blocked}"
        )


def compute_bundle_legality(bundle: AZCConstraintBundle) -> BundleLegalityResult:
    """
    Compute B folio legality for an AZC constraint bundle.

    This is the NEW API that uses the corrected legality framing.
    Replaces the old compute_reachability() for new code.

    Args:
        bundle: AZCConstraintBundle (canonical unit)

    Returns:
        BundleLegalityResult with legality profiles and B folio classification
    """
    data_store = get_data_store()

    # Get the bundle's legality profile
    profile = compute_legality_profile(bundle, data_store)

    # Handle neutral bundles - all folios fully available
    if bundle.is_neutral:
        grammar_by_zone = {}
        for zone in ZONES:
            grammar_by_zone[zone] = GrammarState(
                reachable_classes=ALL_CLASSES.copy(),
                pruned_classes=set()
            )

        b_folios = _load_b_folios()
        folio_legality = {}
        for folio in b_folios:
            required = get_folio_required_classes(folio, data_store)
            folio_legality[folio] = BFolioLegality(
                folio=folio,
                status=ReachabilityStatus.REACHABLE,
                survives_zones=list(ZONES),
                commitment_zone=None,
                required_classes=required,
                available_classes_by_zone={z: ALL_CLASSES.copy() for z in ZONES},
                missing_classes_at_S=set(),
                coverage_pct_at_S=100.0
            )

        return BundleLegalityResult(
            bundle=bundle,
            profile=profile,
            grammar_by_zone=grammar_by_zone,
            folio_legality=folio_legality
        )

    # Handle blocked bundles - no folios available
    if bundle.is_blocked:
        grammar_by_zone = {}
        for zone in ZONES:
            grammar_by_zone[zone] = GrammarState(
                reachable_classes=set(),
                pruned_classes=ALL_CLASSES.copy()
            )

        b_folios = _load_b_folios()
        folio_legality = {}
        for folio in b_folios:
            required = get_folio_required_classes(folio, data_store)
            folio_legality[folio] = BFolioLegality(
                folio=folio,
                status=ReachabilityStatus.UNREACHABLE,
                survives_zones=[],
                commitment_zone='C',  # Blocked at start
                required_classes=required,
                available_classes_by_zone={z: set() for z in ZONES},
                missing_classes_at_S=required,
                coverage_pct_at_S=0.0
            )

        return BundleLegalityResult(
            bundle=bundle,
            profile=profile,
            grammar_by_zone=grammar_by_zone,
            folio_legality=folio_legality
        )

    # Activating bundle - compute zone-specific legality
    from core.azc_projection import _get_consolidated_zone, ALL_ZONES, compute_reachable_classes

    # Compute effective vocabulary from compatible folios (UNION)
    effective_middles = set()
    for folio_id in bundle.compatible_folios:
        folio_vocab = data_store.azc_folio_middles.get(folio_id, set())
        effective_middles |= folio_vocab

    # Compute grammar by zone
    grammar_by_zone = {}
    for zone in ZONES:
        legality_zone = _get_consolidated_zone(zone)
        zone_legal_middles = set()
        for middle in effective_middles:
            legal_zones = data_store.middle_zone_legality.get(middle, ALL_ZONES)
            if legality_zone in legal_zones:
                zone_legal_middles.add(middle)

        aggregated_reachable = compute_reachable_classes(zone_legal_middles, data_store)
        pruned = ALL_CLASSES - aggregated_reachable

        grammar_by_zone[zone] = GrammarState(
            reachable_classes=aggregated_reachable,
            pruned_classes=pruned,
            atomic_hazards_reachable=aggregated_reachable & data_store.atomic_hazard_classes,
            decomposable_hazards_reachable=aggregated_reachable & data_store.decomposable_hazard_classes,
            decomposable_hazards_pruned=data_store.decomposable_hazard_classes - aggregated_reachable
        )

    # Classify B folios
    b_folios = _load_b_folios()
    folio_legality = {}

    for folio in b_folios:
        required = get_folio_required_classes(folio, data_store)
        available_by_zone = {}
        survives_zones = []

        for zone in ZONES:
            gs = grammar_by_zone.get(zone)
            if gs:
                available = required & gs.reachable_classes
                available_by_zone[zone] = available
                if required <= gs.reachable_classes:
                    survives_zones.append(zone)

        # Find commitment zone (first zone where folio doesn't survive)
        commitment_zone = None
        for zone in ZONES:
            if zone not in survives_zones:
                commitment_zone = zone
                break

        # Legacy status mapping
        if len(survives_zones) == len(ZONES):
            status = ReachabilityStatus.REACHABLE
        elif survives_zones:
            status = ReachabilityStatus.CONDITIONAL
        else:
            status = ReachabilityStatus.UNREACHABLE

        # Coverage at S
        s_gs = grammar_by_zone.get('S', grammar_by_zone.get(ZONES[-1]))
        s_available = required & s_gs.reachable_classes if s_gs else set()
        s_missing = required - s_available
        s_coverage = (len(s_available) / len(required) * 100) if required else 100.0

        folio_legality[folio] = BFolioLegality(
            folio=folio,
            status=status,
            survives_zones=survives_zones,
            commitment_zone=commitment_zone,
            required_classes=required,
            available_classes_by_zone=available_by_zone,
            missing_classes_at_S=s_missing,
            coverage_pct_at_S=s_coverage
        )

    return BundleLegalityResult(
        bundle=bundle,
        profile=profile,
        grammar_by_zone=grammar_by_zone,
        folio_legality=folio_legality
    )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_pruned_class_reasons(
    grammar_state: GrammarState,
    data_store: DataStore
) -> Dict[int, str]:
    """
    Get human-readable reasons for why classes were pruned.

    Mechanism note: Uses atomic/decomposable distinction to explain
    why some classes never disappear while others are context-tunable.
    """
    reasons = {}

    for class_id in grammar_state.pruned_classes:
        cls = data_store.classes.get(class_id)
        if not cls:
            reasons[class_id] = "Unknown class"
            continue

        if is_decomposable_hazard(class_id):
            middles = cls.middles
            reasons[class_id] = (
                f"Decomposable hazard class: MIDDLE-bearing members "
                f"({', '.join(sorted(middles)) if middles else 'none'}) "
                f"unavailable under legality field"
            )
        else:
            reasons[class_id] = (
                f"Class {class_id} ({cls.role}): Required MIDDLEs unavailable"
            )

    return reasons


if __name__ == "__main__":
    from .constraint_bundle import (
        compute_bundle, compute_record_bundle,
        build_bundle_registry, extract_azc_active_middles
    )
    from .azc_projection import project_bundle

    # Test reachability (legacy API)
    test_tokens = ['chedy', 'qokaiin', 'shey']

    print("Reachability Engine Test")
    print("=" * 70)
    print("\n--- LEGACY API (compute_reachability) ---")

    for token in test_tokens:
        bundle = compute_bundle(token)
        projection = project_bundle(bundle)
        result = compute_reachability(projection)

        print(f"\n{token} (MIDDLEs: {bundle.middles or 'none'}):")
        print(f"  Grammar: {result.grammar_state.summary()}")
        print(f"  B Folios:")
        print(f"    REACHABLE: {len(result.reachable_folios)}")
        print(f"    CONDITIONAL: {len(result.conditional_folios)}")
        print(f"    UNREACHABLE: {len(result.unreachable_folios)}")

        # Show a few examples
        for fr in result.reachable_folios[:2]:
            print(f"      {fr.folio}: {fr.status.value} ({fr.coverage_pct:.0f}% coverage)")
        for fr in result.conditional_folios[:2]:
            zones = ", ".join(fr.reachable_zones)
            print(f"      {fr.folio}: {fr.status.value} (zones: {zones})")

    # Test new API
    print("\n" + "=" * 70)
    print("\n--- NEW API (compute_bundle_legality) ---")

    try:
        from .a_record_loader import load_a_records

        store = load_a_records()
        if store.registry_entries:
            # Build registry from first 50 records
            registry = build_bundle_registry(store.registry_entries[:50])
            print(f"\n{registry.summary()}")

            # Test a few bundles
            print("\nSample bundle legality results:")
            for bundle_id, azc_bundle in list(registry.bundles.items())[:3]:
                result = compute_bundle_legality(azc_bundle)
                print(f"\n  {result.summary()}")

                # Show a few B folios
                for folio_id, fl in list(result.folio_legality.items())[:2]:
                    print(f"    {fl.summary()}")

    except Exception as e:
        import traceback
        print(f"  Error testing new API: {e}")
        traceback.print_exc()
