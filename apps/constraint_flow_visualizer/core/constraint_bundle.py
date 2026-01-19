"""
Constraint Bundle - The Primary Unit of AZC Interaction

Per expert correction and C481 validation:
- The correct unit of analysis is the CONSTRAINT BUNDLE, not individual A records
- Many A records share the same bundle (this is by design, not a bug)
- Bundles map to LEGALITY PROFILES, not "search results"

Key constraint references:
- C473: A entry = constraint bundle
- C481: Survivor-set uniqueness (at bundle level)
- C469: Categorical ceiling (neutral entries are load-bearing)
- C475: Hub MIDDLEs are universal connectors
- C484: A channel bifurcation
"""

from dataclasses import dataclass, field
from typing import Set, FrozenSet, Optional, List, Dict, TYPE_CHECKING
from enum import Enum

from core.morphology import decompose_token, MorphologyResult, is_articulator

# Avoid circular import
if TYPE_CHECKING:
    from core.a_record_loader import ARecord


# =============================================================================
# CONSTANTS
# =============================================================================

# Hub MIDDLEs - too universal to discriminate (C475)
HUB_MIDDLES = frozenset({'a', 'o', 'e'})

# Infrastructure tokens - never activate AZC (C292, C422)
INFRASTRUCTURE_TOKENS = frozenset({
    'ol', 'or', 'ar', 'al',
    'daiin', 'dain', 'dar', 'dal', 'dam',
    'dy', 'ky', 'ty',
    'aiin', 'ain', 'an',
})


# =============================================================================
# BUNDLE TYPE CLASSIFICATION
# =============================================================================

class BundleType(Enum):
    """
    Classification of constraint bundles.

    Per C469, C484: These are distinct categories, not a spectrum.
    """
    NEUTRAL = "neutral"           # No azc_active MIDDLEs - legal everywhere
    ACTIVATING = "activating"     # Has azc_active MIDDLEs and compatible folios
    BLOCKED = "blocked"           # Has azc_active MIDDLEs but no compatible folios


# =============================================================================
# AZC CONSTRAINT BUNDLE (NEW - Canonical Unit)
# =============================================================================

@dataclass(frozen=True)
class AZCConstraintBundle:
    """
    The PRIMARY unit of AZC interaction.

    This is what C473 and the corrected reading of C481 actually refer to.
    Many A records may share the same bundle - this is EXPECTED behavior,
    not a bug. The registry is designed for reuse (C476, C478).

    Attributes:
        azc_active_middles: The restricted MIDDLEs that activate AZC constraints
        compatible_folios: AZC folios compatible with this bundle
        bundle_type: Classification (neutral/activating/blocked)
    """
    # Core identity (canonical key)
    azc_active_middles: FrozenSet[str]

    # Computed properties
    compatible_folios: FrozenSet[str] = field(default_factory=frozenset)
    bundle_type: BundleType = BundleType.NEUTRAL

    @property
    def bundle_id(self) -> str:
        """Canonical identifier for this bundle."""
        if not self.azc_active_middles:
            return "(neutral)"
        return "{" + ",".join(sorted(self.azc_active_middles)) + "}"

    @property
    def is_neutral(self) -> bool:
        """
        True if this bundle has no AZC-active discriminators.

        Per C469: Neutral entries are LOAD-BEARING, not useless.
        They represent operator judgment entirely external to AZC.
        """
        return len(self.azc_active_middles) == 0

    @property
    def is_activating(self) -> bool:
        """True if this bundle activates AZC constraints."""
        return len(self.azc_active_middles) > 0 and len(self.compatible_folios) > 0

    @property
    def is_blocked(self) -> bool:
        """True if this bundle is blocked (MIDDLEs exist in no single folio)."""
        return len(self.azc_active_middles) > 0 and len(self.compatible_folios) == 0

    @property
    def folio_signature(self) -> FrozenSet[str]:
        """The legal posture - which folios are permitted."""
        return self.compatible_folios

    def status_description(self) -> str:
        """Human-readable status description."""
        if self.is_neutral:
            return "Neutral Registry Entry - No legality-relevant discriminators"
        elif self.is_blocked:
            return f"Blocked - MIDDLEs {set(self.azc_active_middles)} not jointly in any folio"
        else:
            return f"Activating - Permits {len(self.compatible_folios)} folio(s)"

    def __hash__(self):
        return hash(self.azc_active_middles)

    def __eq__(self, other):
        if not isinstance(other, AZCConstraintBundle):
            return False
        return self.azc_active_middles == other.azc_active_middles


# =============================================================================
# LEGALITY PROFILE (Replaces misleading reachability framing)
# =============================================================================

@dataclass
class LegalityProfile:
    """
    The legality outcome of an AZC constraint bundle.

    This replaces the misleading "reachable/conditional/unreachable" framing.
    Shows WHEN commitment happens, not "which procedures match".
    """
    # Folio signature (the legal posture)
    folio_signature: FrozenSet[str]

    # Zone survival profile (when commitment happens)
    survives_C: bool = True
    survives_P: bool = True
    survives_R: bool = True
    survives_S: bool = True

    # Grammar impact
    suppressed_hazard_classes: Set[int] = field(default_factory=set)
    available_classes_at_S: Set[int] = field(default_factory=set)

    @property
    def commitment_zone(self) -> Optional[str]:
        """The zone where commitment occurs (first zone that doesn't fully survive)."""
        if not self.survives_C:
            return "C"
        if not self.survives_P:
            return "P"
        if not self.survives_R:
            return "R"
        if not self.survives_S:
            return "S"
        return None  # Survives all zones

    @property
    def execution_mode(self) -> str:
        """
        Describe the execution mode based on zone survival.

        Replaces "reachable/conditional/unreachable" with meaningful descriptions.
        """
        if self.commitment_zone is None:
            return "full_survival"  # Can complete through S
        elif self.commitment_zone == "S":
            return "late_commitment"  # Commits only at terminal zone
        elif self.commitment_zone in ("R",):
            return "mid_commitment"  # Commits at repetition zones
        elif self.commitment_zone == "P":
            return "early_commitment"  # Commits at prefix zone
        else:
            return "blocked"  # Blocked at C (initial)


# =============================================================================
# BUNDLE REGISTRY (Makes compression explicit)
# =============================================================================

@dataclass
class BundleRegistry:
    """
    Registry of all constraint bundles and the A records that share them.

    This makes the expected compression EXPLICIT:
    - Many A records share the same bundle (BY DESIGN, not a bug)
    - Bundles map to legality profiles

    Per C476, C478: Reuse is expected for coverage optimality.
    """
    # bundle_id -> list of record_ids
    bundle_to_records: Dict[str, List[str]] = field(default_factory=dict)

    # bundle_id -> AZCConstraintBundle
    bundles: Dict[str, AZCConstraintBundle] = field(default_factory=dict)

    # Statistics
    neutral_count: int = 0
    activating_count: int = 0
    blocked_count: int = 0

    def add_record(self, record_id: str, bundle: AZCConstraintBundle):
        """Add a record to the registry."""
        bid = bundle.bundle_id
        if bid not in self.bundle_to_records:
            self.bundle_to_records[bid] = []
            self.bundles[bid] = bundle

            if bundle.is_neutral:
                self.neutral_count += 1
            elif bundle.is_activating:
                self.activating_count += 1
            else:
                self.blocked_count += 1

        self.bundle_to_records[bid].append(record_id)

    def get_records_for_bundle(self, bundle_id: str) -> List[str]:
        """Get all records that share this bundle."""
        return self.bundle_to_records.get(bundle_id, [])

    def get_bundle(self, bundle_id: str) -> Optional[AZCConstraintBundle]:
        """Get the bundle object."""
        return self.bundles.get(bundle_id)

    @property
    def unique_bundle_count(self) -> int:
        return len(self.bundles)

    @property
    def total_record_count(self) -> int:
        return sum(len(recs) for recs in self.bundle_to_records.values())

    def summary(self) -> str:
        """Human-readable summary."""
        return (
            f"BundleRegistry: {self.unique_bundle_count} unique bundles from "
            f"{self.total_record_count} records | "
            f"Neutral: {self.neutral_count}, Activating: {self.activating_count}, "
            f"Blocked: {self.blocked_count}"
        )


# =============================================================================
# LEGACY CONSTRAINT BUNDLE (Backward compatibility)
# =============================================================================

@dataclass
class ConstraintBundle:
    """
    A constraint bundle representing a Currier A entry's signature.

    This is the LEGACY interface for backward compatibility.
    New code should use AZCConstraintBundle directly.
    """
    # Source (can be single token or full record)
    token: str  # Display string (all tokens joined)

    # Morphology decomposition
    prefix: Optional[str]
    prefix_family: Optional[str]
    middle: Optional[str]  # Display string for MIDDLEs
    suffix: Optional[str]

    # Constraint sets - THE KEY DATA
    middles: Set[str]  # Set of ALL MIDDLEs this entry contributes

    # Metadata
    is_valid: bool
    is_infrastructure: bool
    reason: str

    # Record-level fields
    source_tokens: List[str] = field(default_factory=list)
    prefix_families: Set[str] = field(default_factory=set)
    token_count: int = 1
    is_record_bundle: bool = False
    source_folio: Optional[str] = None
    source_line: Optional[str] = None

    # NEW: AZC-active classification
    azc_active: Set[str] = field(default_factory=set)
    universal_middles: Set[str] = field(default_factory=set)
    restricted_middles: Set[str] = field(default_factory=set)
    unknown_middles: Set[str] = field(default_factory=set)

    @property
    def has_middle(self) -> bool:
        return len(self.middles) > 0

    @property
    def is_hub(self) -> bool:
        """Hub entries have no restricted MIDDLEs (universal or no MIDDLEs)."""
        return len(self.azc_active) == 0

    @property
    def is_registry_entry(self) -> bool:
        return self.token_count >= 2

    @property
    def is_short_entry(self) -> bool:
        """Short entries have exactly 1 token (rare after label filtering)."""
        return self.token_count == 1

    @property
    def source_display(self) -> str:
        if self.source_folio and self.source_line:
            return f"{self.source_folio}.{self.source_line}"
        return self.token

    @property
    def bundle_type(self) -> BundleType:
        """Classify this bundle."""
        if len(self.azc_active) == 0:
            return BundleType.NEUTRAL
        # Note: can't determine BLOCKED without folio data
        return BundleType.ACTIVATING

    def to_azc_bundle(self, compatible_folios: FrozenSet[str]) -> AZCConstraintBundle:
        """Convert to the canonical AZCConstraintBundle."""
        azc_active = frozenset(self.azc_active)

        if not azc_active:
            bundle_type = BundleType.NEUTRAL
        elif compatible_folios:
            bundle_type = BundleType.ACTIVATING
        else:
            bundle_type = BundleType.BLOCKED

        return AZCConstraintBundle(
            azc_active_middles=azc_active,
            compatible_folios=compatible_folios,
            bundle_type=bundle_type
        )

    def description(self) -> str:
        if not self.is_valid:
            return f"Invalid: {self.reason}"
        if self.is_infrastructure:
            return f"Infrastructure token: {self.token}"

        parts = []
        if self.prefix_families:
            parts.append(f"PREFIX families: {{{', '.join(sorted(self.prefix_families))}}}")
        if self.azc_active:
            parts.append(f"AZC-active: {{{', '.join(sorted(self.azc_active))}}}")
        elif self.middles:
            parts.append(f"MIDDLEs (universal): {{{', '.join(sorted(self.middles))}}}")

        return " | ".join(parts) if parts else "Neutral entry (no discriminators)"


# =============================================================================
# EXTRACTION FUNCTIONS
# =============================================================================

def extract_azc_active_middles(tokens: List[str], data_store=None) -> Set[str]:
    """
    Extract AZC-active MIDDLEs from a list of tokens.

    Applies hardened criteria:
    - Must be restricted (spread 1-3)
    - Not infrastructure
    - Not hub MIDDLE
    - Not malformed
    """
    if data_store is None:
        from core.data_loader import get_data_store
        data_store = get_data_store()

    azc_active = set()

    for token in tokens:
        # Skip infrastructure tokens (C292, C422)
        if token in INFRASTRUCTURE_TOKENS:
            continue
        if len(token) <= 2:
            continue

        # Skip articulator tokens (C291-C292)
        # Articulators have ZERO discriminative capacity
        # Their MIDDLEs must NOT participate in AZC discrimination
        if is_articulator(token):
            continue

        # Decompose
        morph = decompose_token(token)
        middle = morph.middle if morph.middle else ""

        if not middle:
            continue

        # Skip hub MIDDLEs (C475)
        if middle in HUB_MIDDLES:
            continue

        # Skip malformed
        if '*' in middle or len(middle) > 6:
            continue

        # Check spread (must be restricted: 1-3)
        spread = data_store.middle_folio_spread.get(middle, 0)
        if 1 <= spread <= 3:
            azc_active.add(middle)

    return azc_active


def compute_bundle(token: str, data_store=None) -> ConstraintBundle:
    """Compute the constraint bundle for a single token."""
    if data_store is None:
        from core.data_loader import get_data_store
        data_store = get_data_store()

    morph = decompose_token(token)

    middles: Set[str] = set()
    azc_active: Set[str] = set()
    universal_middles: Set[str] = set()
    restricted_middles: Set[str] = set()
    unknown_middles: Set[str] = set()

    if morph.middle:
        middles.add(morph.middle)

        # Classify the MIDDLE
        if morph.middle in HUB_MIDDLES:
            universal_middles.add(morph.middle)
        elif '*' in morph.middle or len(morph.middle) > 6:
            unknown_middles.add(morph.middle)
        else:
            spread = data_store.middle_folio_spread.get(morph.middle, 0)
            if spread == 0:
                unknown_middles.add(morph.middle)
            elif spread <= 3:
                restricted_middles.add(morph.middle)
                azc_active.add(morph.middle)
            else:
                universal_middles.add(morph.middle)

    prefix_families: Set[str] = set()
    if morph.prefix_family:
        prefix_families.add(morph.prefix_family)

    return ConstraintBundle(
        token=token,
        prefix=morph.prefix,
        prefix_family=morph.prefix_family,
        middle=morph.middle,
        suffix=morph.suffix,
        middles=middles,
        is_valid=morph.is_valid,
        is_infrastructure=morph.is_infrastructure,
        reason=morph.reason,
        source_tokens=[token],
        prefix_families=prefix_families,
        token_count=1,
        is_record_bundle=False,
        azc_active=azc_active,
        universal_middles=universal_middles,
        restricted_middles=restricted_middles,
        unknown_middles=unknown_middles
    )


def merge_bundles(bundles: list) -> ConstraintBundle:
    """Merge multiple constraint bundles into a combined bundle."""
    if not bundles:
        return ConstraintBundle(
            token="(empty)",
            prefix=None,
            prefix_family=None,
            middle=None,
            suffix=None,
            middles=set(),
            is_valid=False,
            is_infrastructure=False,
            reason="No tokens provided",
        )

    if len(bundles) == 1:
        return bundles[0]

    # Aggregate across all tokens
    all_middles: Set[str] = set()
    all_azc_active: Set[str] = set()
    all_universal: Set[str] = set()
    all_restricted: Set[str] = set()
    all_unknown: Set[str] = set()
    all_prefix_families: Set[str] = set()
    all_tokens: List[str] = []
    all_valid = True

    for bundle in bundles:
        all_middles.update(bundle.middles)
        all_azc_active.update(bundle.azc_active)
        all_universal.update(bundle.universal_middles)
        all_restricted.update(bundle.restricted_middles)
        all_unknown.update(bundle.unknown_middles)
        all_prefix_families.update(bundle.prefix_families)
        all_tokens.extend(bundle.source_tokens if bundle.source_tokens else [bundle.token])
        if not bundle.is_valid:
            all_valid = False

    first = bundles[0]

    return ConstraintBundle(
        token=" ".join(all_tokens),
        prefix=first.prefix,
        prefix_family=first.prefix_family,
        middle="|".join(sorted(all_middles)) if all_middles else None,
        suffix=first.suffix,
        middles=all_middles,
        is_valid=all_valid,
        is_infrastructure=False,
        reason=f"Record with {len(bundles)} tokens",
        source_tokens=all_tokens,
        prefix_families=all_prefix_families,
        token_count=len(all_tokens),
        is_record_bundle=True,
        azc_active=all_azc_active,
        universal_middles=all_universal,
        restricted_middles=all_restricted,
        unknown_middles=all_unknown
    )


def compute_record_bundle(record: 'ARecord', data_store=None) -> ConstraintBundle:
    """
    Compute the constraint bundle for an entire Currier A record.

    This is the PRIMARY way to compute bundles, per:
    - C233: LINE_ATOMIC (each line is independent unit)
    - C473: Currier A Entry Defines a Constraint Bundle
    - C481: Survivor-Set Uniqueness (at bundle level)
    """
    if data_store is None:
        from core.data_loader import get_data_store
        data_store = get_data_store()

    token_bundles = [compute_bundle(t, data_store) for t in record.tokens]
    bundle = merge_bundles(token_bundles)

    bundle.source_folio = record.folio
    bundle.source_line = record.line_number

    return bundle


# =============================================================================
# BUNDLE REGISTRY BUILDER
# =============================================================================

def build_bundle_registry(records: List['ARecord'], data_store=None) -> BundleRegistry:
    """
    Build a complete bundle registry from A records.

    This implements Change #2 from expert recommendations:
    "Collapse A-records INTO bundles by design"

    The registry makes explicit that:
    - Many A records share the same bundle (BY DESIGN, not a bug)
    - Per C476, C478: Reuse is expected for coverage optimality
    - Bundle {} -> ~963 A records (neutral / legal-noop)
    - Bundle {d} -> ~44 A records
    - etc.

    Args:
        records: List of ARecord objects
        data_store: Optional data store (loaded if not provided)

    Returns:
        BundleRegistry with all bundles and their record mappings
    """
    if data_store is None:
        from core.data_loader import get_data_store
        data_store = get_data_store()

    registry = BundleRegistry()

    for record in records:
        # Extract azc_active MIDDLEs for this record
        azc_active = extract_azc_active_middles(record.tokens, data_store)

        # Compute compatible folios
        compatible_folios = compute_compatible_folios(
            frozenset(azc_active), data_store
        )

        # Determine bundle type
        if not azc_active:
            bundle_type = BundleType.NEUTRAL
        elif compatible_folios:
            bundle_type = BundleType.ACTIVATING
        else:
            bundle_type = BundleType.BLOCKED

        # Create the canonical bundle
        bundle = AZCConstraintBundle(
            azc_active_middles=frozenset(azc_active),
            compatible_folios=compatible_folios,
            bundle_type=bundle_type
        )

        # Register this record under the bundle
        registry.add_record(record.display_name, bundle)

    return registry


def compute_compatible_folios(
    azc_active: FrozenSet[str],
    data_store=None
) -> FrozenSet[str]:
    """
    Compute which AZC folios are compatible with a set of azc_active MIDDLEs.

    Per C442, C470: A folio is compatible if all restricted MIDDLEs are in its vocab.
    Neutral bundles (no azc_active) are compatible with ALL folios.

    Args:
        azc_active: The frozen set of azc_active MIDDLEs
        data_store: Optional data store

    Returns:
        FrozenSet of compatible folio IDs
    """
    if data_store is None:
        from core.data_loader import get_data_store
        data_store = get_data_store()

    if not azc_active:
        # Neutral bundle = compatible with all AZC folios
        return frozenset(data_store.azc_folio_middles.keys())

    compatible = set()
    for folio_id, folio_vocab in data_store.azc_folio_middles.items():
        # Check if all azc_active MIDDLEs are in this folio's vocabulary
        if azc_active <= folio_vocab:
            compatible.add(folio_id)

    return frozenset(compatible)


def compute_legality_profile(
    bundle: AZCConstraintBundle,
    data_store=None
) -> LegalityProfile:
    """
    Compute the legality profile for an AZC constraint bundle.

    This implements Change #3 from expert recommendations:
    "Reframe output to legality profiles"

    Shows WHEN commitment happens, not "which procedures match".

    Args:
        bundle: The AZC constraint bundle
        data_store: Optional data store

    Returns:
        LegalityProfile describing zone survival and grammar impact
    """
    if data_store is None:
        from core.data_loader import get_data_store
        data_store = get_data_store()

    # Neutral bundles survive all zones
    if bundle.is_neutral:
        return LegalityProfile(
            folio_signature=bundle.compatible_folios,
            survives_C=True,
            survives_P=True,
            survives_R=True,
            survives_S=True,
            suppressed_hazard_classes=set(),
            available_classes_at_S=set(range(1, 50))
        )

    # Blocked bundles survive nothing
    if bundle.is_blocked:
        return LegalityProfile(
            folio_signature=frozenset(),
            survives_C=False,
            survives_P=False,
            survives_R=False,
            survives_S=False,
            suppressed_hazard_classes=set(),
            available_classes_at_S=set()
        )

    # For activating bundles, compute zone survival
    # Need to check if MIDDLEs remain legal through each zone
    survives = {'C': True, 'P': True, 'R': True, 'S': True}

    for middle in bundle.azc_active_middles:
        legal_zones = data_store.middle_zone_legality.get(middle, {'C', 'P', 'R', 'S'})
        for zone in ['C', 'P', 'R', 'S']:
            if zone not in legal_zones:
                survives[zone] = False

    return LegalityProfile(
        folio_signature=bundle.compatible_folios,
        survives_C=survives['C'],
        survives_P=survives['P'],
        survives_R=survives['R'],
        survives_S=survives['S'],
        suppressed_hazard_classes=set(),  # Computed by reachability engine
        available_classes_at_S=set()  # Computed by reachability engine
    )


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("Constraint Bundle Test")
    print("=" * 60)

    test_tokens = ['chedy', 'qokaiin', 'daiin', 'shey', 'ol', 'ar']

    for token in test_tokens:
        bundle = compute_bundle(token)
        print(f"\n{token}:")
        print(f"  {bundle.description()}")
        print(f"  Type: {bundle.bundle_type.value}")
        print(f"  AZC-active: {bundle.azc_active or '(none)'}")

    print("\n" + "=" * 60)
    print("Record bundle test:")

    try:
        from core.a_record_loader import load_a_records
        store = load_a_records()
        if store.registry_entries:
            record = store.registry_entries[0]
            bundle = compute_record_bundle(record)
            print(f"  Record: {record.display_name}")
            print(f"  Tokens: {record.tokens}")
            print(f"  AZC-active: {bundle.azc_active}")
            print(f"  Type: {bundle.bundle_type.value}")
            print(f"  {bundle.description()}")

            # Test new bundle registry
            print("\n" + "=" * 60)
            print("Bundle Registry Test (first 20 records):")
            print("-" * 60)

            registry = build_bundle_registry(store.registry_entries[:100])
            print(f"  {registry.summary()}")

            print("\n  Sample bundles:")
            for bundle_id, azc_bundle in list(registry.bundles.items())[:5]:
                record_ids = registry.get_records_for_bundle(bundle_id)
                profile = compute_legality_profile(azc_bundle)
                print(f"    {bundle_id}: {len(record_ids)} records")
                print(f"      Type: {azc_bundle.bundle_type.value}")
                print(f"      Compatible folios: {len(azc_bundle.compatible_folios)}")
                print(f"      Execution mode: {profile.execution_mode}")

    except Exception as e:
        import traceback
        print(f"  Error: {e}")
        traceback.print_exc()
