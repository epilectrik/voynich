"""
Data loader for Constraint Flow Visualizer.

Loads all required data files and builds lookup indices for:
- 49 instruction classes
- MIDDLE -> class mapping
- Hazard class profiles (atomic vs decomposable)
- AZC folio list
- Forbidden transitions
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional, Tuple
from enum import Enum


# Project root - navigate from app location
APP_DIR = Path(__file__).parent.parent
PROJECT_ROOT = APP_DIR.parent.parent


class HazardType(Enum):
    """Hazard class taxonomy from AZC_REACHABILITY_SUPPRESSION phase."""
    ATOMIC = "atomic"  # No MIDDLE involvement - universal enforcement
    DECOMPOSABLE = "decomposable"  # MIDDLE-bearing - context-tunable


@dataclass
class InstructionClass:
    """A single instruction equivalence class."""
    class_id: int
    members: List[str]
    role: str
    middles: Set[str]
    prefixes: Set[str]
    is_hazard_involved: bool = False
    hazard_type: Optional[HazardType] = None


@dataclass
class ForbiddenTransition:
    """A forbidden transition in the hazard topology."""
    from_class: int
    to_class: int
    from_token: str
    to_token: str
    hazard_class: str
    severity: float


@dataclass
class AZCFolio:
    """An AZC folio with its characteristics."""
    folio: str
    section: str  # Z, A, C, H
    token_count: int
    unique_types: int
    # Zone occupancy (simplified: C, P, R, S)
    zone_occupancy: Dict[str, float]


@dataclass
class FolioMetrics:
    """
    Per-folio metrics for sufficiency checking.

    Per X.14 (Curriculum Completeness Model):
    - link_density: Fraction of LINK tokens (monitoring completeness)
    - recovery_ops_count: Number of e-operator instances (recovery completeness)

    Used to determine if a B folio has sufficient procedural completeness
    for its assigned REGIME. This is Tier 3 interpretation - sufficiency
    is surfaced, not enforced (OJLM-1).
    """
    link_density: float
    recovery_ops_count: int


@dataclass
class DataStore:
    """Central data store for all loaded data."""
    # Instruction classes
    classes: Dict[int, InstructionClass] = field(default_factory=dict)

    # MIDDLE -> classes mapping
    middle_to_classes: Dict[str, Set[int]] = field(default_factory=dict)

    # Hazard-involved classes
    hazard_classes: Set[int] = field(default_factory=set)
    atomic_hazard_classes: Set[int] = field(default_factory=set)
    decomposable_hazard_classes: Set[int] = field(default_factory=set)

    # Forbidden transitions
    forbidden_transitions: List[ForbiddenTransition] = field(default_factory=list)
    forbidden_class_pairs: Set[Tuple[int, int]] = field(default_factory=set)

    # AZC folios
    azc_folios: Dict[str, AZCFolio] = field(default_factory=dict)

    # Zone definitions
    zones: List[str] = field(default_factory=lambda: ['C', 'P', 'R1', 'R2', 'R3', 'S'])

    # MIDDLE zone legality (binary: which zones is each MIDDLE legal in)
    # Per C313, C443, C475: legality is categorical, not probabilistic
    middle_zone_legality: Dict[str, Set[str]] = field(default_factory=dict)

    # B folio class footprints (actual classes used by each B folio)
    b_folio_class_footprints: Dict[str, Set[int]] = field(default_factory=dict)

    # AZC folio MIDDLE vocabulary (compatibility domain per folio)
    # Per C441, C472: AZC constraints are vocabulary-activated
    azc_folio_middles: Dict[str, Set[str]] = field(default_factory=dict)

    # Kernel/boundary classes - NEVER pruned by AZC
    # Per C085, C089, C107, C171, C485: kernel operators are load-bearing
    # These classes are always reachable regardless of MIDDLE availability
    kernel_classes: Set[int] = field(default_factory=set)

    # MIDDLE folio spread (number of AZC folios each MIDDLE appears in)
    # Per C472: 77% of MIDDLEs appear in only 1 folio
    middle_folio_spread: Dict[str, int] = field(default_factory=dict)

    # Universal MIDDLEs (4+ folios) - cannot forbid compatibility
    # Per C470: universal MIDDLEs span 50.6 B folios on average (12.7x vs restricted)
    # These MIDDLEs still participate in grammar, but cannot disqualify a folio
    universal_middles: Set[str] = field(default_factory=set)

    # REGIME assignments for B folios
    # Per C179-C185: 4 stable regimes based on OPS-2 K-Means clustering
    # Observational categorization for visualization, NOT structural constraint
    regime_assignments: Dict[str, str] = field(default_factory=dict)

    # Per-folio metrics for sufficiency checking
    # Per X.14: REGIME_4 needs 25% LINK, REGIME_3 needs 2+ recovery ops
    # This is Tier 3 interpretation - surfaced, not enforced (OJLM-1)
    folio_metrics: Dict[str, FolioMetrics] = field(default_factory=dict)


def load_instruction_classes(data_store: DataStore) -> None:
    """Load 49 instruction classes from phase20a_operator_equivalence.json."""
    path = PROJECT_ROOT / "phases" / "01-09_early_hypothesis" / "phase20a_operator_equivalence.json"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    classes = data.get('classes', data.get('equivalence_classes', []))

    for cls_data in classes:
        class_id = cls_data.get('class_id', cls_data.get('id'))
        members = cls_data.get('members', [])
        role = cls_data.get('functional_role', cls_data.get('role', 'UNKNOWN'))

        data_store.classes[class_id] = InstructionClass(
            class_id=class_id,
            members=members,
            role=role,
            middles=set(),
            prefixes=set()
        )


def load_middle_class_index(data_store: DataStore) -> None:
    """Load MIDDLE -> class mapping from middle_class_index.json."""
    path = PROJECT_ROOT / "phases" / "AZC_REACHABILITY_SUPPRESSION" / "middle_class_index.json"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Load middle_to_classes mapping
    for middle, class_ids in data.get('middle_to_classes', {}).items():
        data_store.middle_to_classes[middle] = set(class_ids)

    # Invert to get class_to_middles (populate class.middles)
    for middle, class_ids in data_store.middle_to_classes.items():
        for class_id in class_ids:
            if class_id in data_store.classes:
                data_store.classes[class_id].middles.add(middle)

    # Load class morphology (MIDDLEs per class) - supplements/overrides above
    for class_id_str, class_morph in data.get('class_morphology', {}).items():
        class_id = int(class_id_str)
        if class_id in data_store.classes:
            data_store.classes[class_id].middles = set(class_morph.get('middles', []))
            data_store.classes[class_id].prefixes = set(class_morph.get('prefixes', []))

    # Load hazard class profiles
    hazard_profiles = data.get('hazard_class_profiles', {})
    for class_id_str, profile in hazard_profiles.items():
        class_id = int(class_id_str)
        data_store.hazard_classes.add(class_id)

        if class_id in data_store.classes:
            data_store.classes[class_id].is_hazard_involved = True

            # Determine if atomic or decomposable based on MIDDLE involvement
            # Atomic: no MIDDLEs (classes 7, 9, 23 in this corpus)
            # Decomposable: has MIDDLEs
            exclusive = profile.get('exclusive_middles', 0)
            shared = profile.get('shared_middles', 0)

            if exclusive == 0 and shared == 0:
                data_store.classes[class_id].hazard_type = HazardType.ATOMIC
                data_store.atomic_hazard_classes.add(class_id)
            else:
                data_store.classes[class_id].hazard_type = HazardType.DECOMPOSABLE
                data_store.decomposable_hazard_classes.add(class_id)


def load_forbidden_transitions(data_store: DataStore) -> None:
    """Load forbidden transitions from phase1_results.json."""
    path = PROJECT_ROOT / "phases" / "AZC_REACHABILITY_SUPPRESSION" / "phase1_results.json"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Parse class transitions
    for pair_key, trans_data in data.get('class_transitions', {}).items():
        from_class = trans_data.get('from_class')
        to_class = trans_data.get('to_class')

        if from_class is not None and to_class is not None:
            data_store.forbidden_class_pairs.add((from_class, to_class))

            for token_trans in trans_data.get('token_transitions', []):
                data_store.forbidden_transitions.append(ForbiddenTransition(
                    from_class=from_class,
                    to_class=to_class,
                    from_token=token_trans.get('from_token', ''),
                    to_token=token_trans.get('to_token', ''),
                    hazard_class=token_trans.get('hazard_class', ''),
                    severity=token_trans.get('severity', 0.0)
                ))


def load_azc_folios(data_store: DataStore) -> None:
    """Load AZC folio data from azc_folio_features.json."""
    path = PROJECT_ROOT / "results" / "azc_folio_features.json"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for folio_id, folio_data in data.get('folios', {}).items():
        # Aggregate zone occupancy from placement_vector
        placement = folio_data.get('placement_vector', {})

        # Simplify zones: C, P, R (aggregating R1-R4), S (aggregating S1-S2)
        zone_occupancy = {
            'C': placement.get('C', 0) + placement.get('C1', 0),
            'P': placement.get('P', 0) + placement.get('P1', 0),
            'R1': placement.get('R1', 0),
            'R2': placement.get('R2', 0),
            'R3': placement.get('R3', 0) + placement.get('R4', 0),  # Combine R3+R4
            'S': placement.get('S', 0) + placement.get('S1', 0) + placement.get('S2', 0)
        }

        data_store.azc_folios[folio_id] = AZCFolio(
            folio=folio_id,
            section=folio_data.get('section', 'U'),
            token_count=folio_data.get('token_count', 0),
            unique_types=folio_data.get('unique_types', 0),
            zone_occupancy=zone_occupancy
        )


def load_middle_zone_legality(data_store: DataStore) -> None:
    """
    Load binary zone legality from per-MIDDLE occurrence data.

    Source: results/middle_zone_legality.json
    Generated by: scripts/compute_middle_zone_legality.py

    NOT from middle_zone_survival.json cluster means (those erase zeros).
    Per expert diagnosis: Zeros are the signal. Cluster means hide them.

    Per C313, C443, C475: All legality is categorical.
    count > 0 = legal in that zone.
    count == 0 = illegal in that zone.
    """
    path = PROJECT_ROOT / "results" / "middle_zone_legality.json"

    if not path.exists():
        print(f"WARNING: {path} not found.")
        print("Run: python apps/constraint_flow_visualizer/scripts/compute_middle_zone_legality.py")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for middle, legality_data in data.items():
        legal_zones = set(legality_data.get('legal_zones', []))
        data_store.middle_zone_legality[middle] = legal_zones

    # Show zone collapse statistics for verification
    zone_patterns = {}
    for middle, zones in data_store.middle_zone_legality.items():
        pattern = tuple(sorted(zones))
        zone_patterns[pattern] = zone_patterns.get(pattern, 0) + 1

    print(f"Loaded zone legality for {len(data_store.middle_zone_legality)} MIDDLEs")
    print(f"  Zone patterns: {len(zone_patterns)} distinct")

    # Verify we have actual zeros (not all-legal)
    all_legal = sum(1 for zones in data_store.middle_zone_legality.values()
                    if zones == {'C', 'P', 'R', 'S'})
    partial = len(data_store.middle_zone_legality) - all_legal
    print(f"  All-zone legal: {all_legal}, Partial legality: {partial}")


def load_b_folio_class_footprints(data_store: DataStore) -> None:
    """
    Load pre-computed B folio class footprints.

    These are the actual instruction classes used by each B folio,
    computed from corpus tokens via MIDDLE -> class mapping.

    NOT derived from REGIME (that would be invented semantics).
    """
    path = PROJECT_ROOT / "results" / "b_folio_class_footprints.json"

    if not path.exists():
        print(f"WARNING: {path} not found. Run compute_b_folio_footprints.py first.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for folio, classes in data.items():
        data_store.b_folio_class_footprints[folio] = set(classes)


def load_azc_folio_middles(data_store: DataStore) -> None:
    """
    Load the MIDDLE vocabulary for each AZC folio.

    This defines the compatibility domain each folio represents.
    Per C441, C472: AZC constraints are vocabulary-activated.

    Different A entries activate different AZC folios (via MIDDLE compatibility),
    and each folio has its own vocabulary that restricts class reachability.
    """
    from collections import defaultdict
    from core.morphology import decompose_token

    transcript_path = PROJECT_ROOT / "data" / "transcriptions" / "interlinear_full_words.txt"

    if not transcript_path.exists():
        print(f"WARNING: {transcript_path} not found.")
        return

    folio_middles = defaultdict(set)

    with open(transcript_path, 'r', encoding='utf-8') as f:
        f.readline()  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 13:
                continue

            token = parts[0].strip('"').strip()
            folio = parts[2].strip('"').strip()
            language = parts[6].strip('"').strip()
            transcriber = parts[12].strip('"').strip()

            # AZC only (language == 'NA'), H-track only
            if transcriber != 'H' or language != 'NA':
                continue

            morph = decompose_token(token)
            if morph.middle:
                folio_middles[folio].add(morph.middle)

    data_store.azc_folio_middles = dict(folio_middles)
    print(f"Loaded MIDDLE vocabulary for {len(data_store.azc_folio_middles)} AZC folios")

    # Show vocabulary sizes for verification
    sizes = [len(v) for v in data_store.azc_folio_middles.values()]
    if sizes:
        print(f"  Vocabulary sizes: min={min(sizes)}, max={max(sizes)}, avg={sum(sizes)/len(sizes):.1f}")


def compute_middle_folio_spread(data_store: DataStore) -> None:
    """
    Compute how many AZC folios each MIDDLE appears in.

    Per C472: 77% of MIDDLEs appear in exactly 1 AZC folio (discriminative).
    Per C470: Universal MIDDLEs span 50.6 B folios on average (12.7x vs restricted).

    Classification (per expert ruling):
    - Restricted (1-3 folios): Decisive constraint carriers - CAN forbid compatibility
    - Universal (4+ folios): Non-restrictive backbone - CANNOT forbid compatibility

    IMPORTANT: Universal MIDDLEs still participate in grammar computation.
    They just cannot disqualify a folio from compatibility.
    This implements the asymmetric filter per C442, C470, C472.
    """
    from collections import Counter

    if not data_store.azc_folio_middles:
        print("WARNING: Cannot compute MIDDLE folio spread - no AZC folio vocabularies loaded")
        return

    # Count how many folios each MIDDLE appears in
    middle_folios = Counter()
    for folio_id, vocab in data_store.azc_folio_middles.items():
        for middle in vocab:
            middle_folios[middle] += 1

    # Store spread data
    data_store.middle_folio_spread = dict(middle_folios)

    # Classify universal MIDDLEs (4+ folios)
    # Per C470: these have "broad survival" and cannot forbid compatibility
    data_store.universal_middles = {
        m for m, count in middle_folios.items() if count >= 4
    }

    # Statistics for verification
    total = len(middle_folios)
    if total == 0:
        print("WARNING: No MIDDLEs found in AZC folio vocabularies")
        return

    restricted = [m for m, c in middle_folios.items() if c <= 3]
    universal = list(data_store.universal_middles)

    print(f"MIDDLE folio spread computed:")
    print(f"  Total MIDDLEs: {total}")
    print(f"  Restricted (1-3 folios): {len(restricted)} ({100*len(restricted)/total:.0f}%)")
    print(f"  Universal (4+ folios): {len(universal)} ({100*len(universal)/total:.0f}%)")
    if universal:
        print(f"  Universal examples: {sorted(universal)[:10]}")


# Infrastructure classes per C396.a (BCI characterization 2026-01-18):
# These AUXILIARY roles mediate kernel access and must not be pruned
# by AZC vocabulary filtering. See TIER3/b_execution_infrastructure_characterization.md
# Coverage: 44 (98%), 46 (99%), 42 (85%), 36 (96%) of B folios
INFRASTRUCTURE_CLASSES = {44, 46, 42, 36}


def identify_kernel_classes(data_store: DataStore) -> None:
    """
    Identify classes that must NEVER be pruned by AZC vocabulary filtering.

    Per C089, C109, C396.a - protection is structurally defined, not frequency-based:
    1. Atomic hazard classes (no MIDDLE involvement) - AZC cannot affect them
    2. Infrastructure classes (AUXILIARY roles) - mediate kernel access

    Per C411: ~40% of classes are deliberately reducible.
    Over-protecting defeats the grammar's built-in flexibility.

    NOTE: The previous implementation incorrectly marked "classes in ALL B folios"
    as kernel (35/49 classes). This violated C089 (kernel = k,h,e only) and C411
    (~40% reducible). Both internal and external experts confirmed this was wrong.
    """
    # Start with atomic hazard classes (already computed in load_middle_class_index)
    # These have NO MIDDLE involvement - AZC vocabulary filtering cannot affect them
    # Per C109, X.20: classes {7, 9, 23}
    protected = set(data_store.atomic_hazard_classes)

    # Add infrastructure classes (AUXILIARY roles per C396.a)
    # These mediate kernel access and are execution-critical
    protected |= INFRASTRUCTURE_CLASSES

    data_store.kernel_classes = protected

    # Report what was identified
    n_pruneable = 49 - len(protected)
    print(f"Identified {len(protected)} protected classes:")
    print(f"  Atomic hazards (C109): {sorted(data_store.atomic_hazard_classes)}")
    print(f"  Infrastructure (C396.a): {sorted(INFRASTRUCTURE_CLASSES)}")
    print(f"  Total protected: {sorted(protected)}")
    print(f"  Subject to MIDDLE-based pruning: {n_pruneable} classes (~{100*n_pruneable/49:.0f}%)")


def load_regime_assignments(data_store: DataStore) -> None:
    """
    Load REGIME classifications for B folios.

    Source: OPS-2 K-Means clustering on 33 control metrics (C179-C185)
    NOT a structural constraint - observational categorization for visualization.

    REGIMEs encode procedural COMPLETENESS, not intensity (per X.14):
    - REGIME_2: Gentle, high-waiting - introductory procedures
    - REGIME_1: Moderate - standard execution
    - REGIME_4: Precision-constrained - tight control required
    - REGIME_3: Aggressive, transient - advanced/high-risk
    """
    path = PROJECT_ROOT / "results" / "regime_folio_mapping.json"

    if not path.exists():
        print(f"WARNING: {path} not found. REGIME display will be unavailable.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    # Invert: {"REGIME_1": [folios...]} -> {folio: "REGIME_1"}
    for regime, folios in mapping.items():
        for folio in folios:
            data_store.regime_assignments[folio] = regime

    print(f"Loaded REGIME assignments for {len(data_store.regime_assignments)} B folios")

    # Show distribution for verification
    from collections import Counter
    dist = Counter(data_store.regime_assignments.values())
    print(f"  Distribution: {dict(sorted(dist.items()))}")


def load_folio_metrics(data_store: DataStore) -> None:
    """
    Load per-folio metrics for sufficiency checking.

    Source: results/unified_folio_profiles.json
    Contains link_density and recovery_ops_count per B folio.

    Per X.14 (Curriculum Completeness Model):
    - REGIME_4 requires link_density >= 0.25 (monitoring completeness)
    - REGIME_3 requires recovery_ops_count >= 2 (recovery completeness)

    This is Tier 3 interpretation. Sufficiency is surfaced, not enforced (OJLM-1).
    """
    path = PROJECT_ROOT / "results" / "unified_folio_profiles.json"

    if not path.exists():
        print(f"WARNING: {path} not found. Sufficiency display will be unavailable.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Profiles are under 'profiles' key, not top-level
    profiles = data.get('profiles', {})

    for folio_name, profile in profiles.items():
        # Only B folios have b_metrics
        b_metrics = profile.get('b_metrics')
        if b_metrics:
            data_store.folio_metrics[folio_name] = FolioMetrics(
                link_density=b_metrics.get('link_density', 0.0),
                recovery_ops_count=b_metrics.get('recovery_ops_count', 0)
            )

    print(f"Loaded folio metrics for {len(data_store.folio_metrics)} B folios")

    # Show sample statistics for verification
    if data_store.folio_metrics:
        link_densities = [m.link_density for m in data_store.folio_metrics.values()]
        recovery_counts = [m.recovery_ops_count for m in data_store.folio_metrics.values()]
        print(f"  Link density: min={min(link_densities):.3f}, max={max(link_densities):.3f}")
        print(f"  Recovery ops: min={min(recovery_counts)}, max={max(recovery_counts)}")


def load_all_data() -> DataStore:
    """Load all required data and return a populated DataStore."""
    data_store = DataStore()

    # Load in dependency order
    load_instruction_classes(data_store)
    load_middle_class_index(data_store)
    load_forbidden_transitions(data_store)
    load_azc_folios(data_store)
    load_middle_zone_legality(data_store)
    load_b_folio_class_footprints(data_store)
    load_azc_folio_middles(data_store)

    # Compute MIDDLE folio spread (must be after AZC folio vocabularies loaded)
    # Per C470, C472: classifies restricted vs universal MIDDLEs
    compute_middle_folio_spread(data_store)

    # Identify kernel classes (must be after B folio footprints loaded)
    identify_kernel_classes(data_store)

    # Load REGIME assignments (observational categorization for visualization)
    load_regime_assignments(data_store)

    # Load folio metrics for sufficiency checking (Tier 3: X.14)
    load_folio_metrics(data_store)

    return data_store


# Module-level singleton for cached data
_data_store: Optional[DataStore] = None


def get_data_store() -> DataStore:
    """Get the cached data store, loading if necessary."""
    global _data_store
    if _data_store is None:
        _data_store = load_all_data()
    return _data_store


# Convenience accessors
def get_class(class_id: int) -> Optional[InstructionClass]:
    """Get an instruction class by ID."""
    return get_data_store().classes.get(class_id)


def get_classes_for_middle(middle: str) -> Set[int]:
    """Get all classes that use a given MIDDLE."""
    return get_data_store().middle_to_classes.get(middle, set())


def get_middles_for_class(class_id: int) -> Set[str]:
    """Get all MIDDLEs used by a given class."""
    cls = get_class(class_id)
    return cls.middles if cls else set()


def is_atomic_hazard(class_id: int) -> bool:
    """Check if a class is an atomic hazard class (no MIDDLE involvement)."""
    return class_id in get_data_store().atomic_hazard_classes


def is_decomposable_hazard(class_id: int) -> bool:
    """Check if a class is a decomposable hazard class (MIDDLE-bearing)."""
    return class_id in get_data_store().decomposable_hazard_classes


def is_kernel_class(class_id: int) -> bool:
    """
    Check if a class is a kernel/boundary class (never pruned).

    Per C085, C089, C107, C171, C485: Kernel classes are load-bearing
    and cannot be removed by AZC restriction.
    """
    return class_id in get_data_store().kernel_classes


def get_all_azc_folios() -> List[str]:
    """Get list of all AZC folio IDs."""
    return list(get_data_store().azc_folios.keys())


def get_azc_folio(folio_id: str) -> Optional[AZCFolio]:
    """Get AZC folio data by ID."""
    return get_data_store().azc_folios.get(folio_id)


if __name__ == "__main__":
    # Test data loading
    print("Loading data...")
    store = load_all_data()

    print(f"\nLoaded {len(store.classes)} instruction classes")
    print(f"Loaded {len(store.middle_to_classes)} MIDDLE types")
    print(f"Loaded {len(store.forbidden_transitions)} forbidden transitions")
    print(f"Loaded {len(store.azc_folios)} AZC folios")

    print(f"\nHazard classes: {len(store.hazard_classes)}")
    print(f"  Atomic: {store.atomic_hazard_classes}")
    print(f"  Decomposable: {store.decomposable_hazard_classes}")

    print(f"\nForbidden class pairs: {len(store.forbidden_class_pairs)}")
    for pair in sorted(store.forbidden_class_pairs):
        print(f"  {pair[0]} -> {pair[1]}")
