"""
Reachability Computer - Computes role-level connectivity under AZC legality.

Per C468: Legality profiles propagate causally.
Per C444: Illegal paths are absent (vanishing semantics).
Per C111: 65% of transitions are asymmetric (directed).
"""

from typing import Dict, Set, Tuple, Optional
from dataclasses import dataclass

from .role_classifier import ControlRole, RoleClassifier


@dataclass
class RoleReachability:
    """Reachability state at role level."""
    # Which role pairs have legal transitions
    legal_transitions: Dict[Tuple[ControlRole, ControlRole], bool]
    # Edge counts per role pair
    edge_counts: Dict[Tuple[ControlRole, ControlRole], int]
    # Total legal edges
    total_legal_edges: int
    # Total possible edges (baseline)
    total_possible_edges: int
    # Reachable class count
    reachable_classes: int
    # Pruned class count
    pruned_classes: int


@dataclass
class HazardStatus:
    """Status of hazard classes under current legality."""
    # Per failure class: active count
    active_by_class: Dict[str, int]
    # Per failure class: total count
    total_by_class: Dict[str, int]
    # Atomic hazards (always active)
    atomic_active: int
    atomic_total: int
    # Decomposable hazards (AZC-tunable)
    decomposable_active: int
    decomposable_total: int


class ReachabilityComputer:
    """
    Computes legal role-to-role connectivity under AZC legality.

    Implements vanishing semantics: illegal paths are absent, not greyed.
    """

    def __init__(self, data_store, role_classifier: RoleClassifier):
        """
        Initialize computer.

        Args:
            data_store: DataStore with grammar information
            role_classifier: RoleClassifier for 49->6 mapping
        """
        self.data_store = data_store
        self.classifier = role_classifier
        self._baseline_edges = self._compute_baseline_edges()

    def _compute_baseline_edges(self) -> Set[Tuple[int, int]]:
        """Compute all legal edges in baseline (unconstrained) grammar."""
        forbidden = self.data_store.forbidden_class_pairs
        edges = set()
        for i in range(1, 50):
            for j in range(1, 50):
                if (i, j) not in forbidden:
                    edges.add((i, j))
        return edges

    def compute_reachability(
        self,
        reachable_classes: Optional[Set[int]] = None
    ) -> RoleReachability:
        """
        Compute role-level reachability under given legality.

        Args:
            reachable_classes: Set of legal class IDs, or None for baseline

        Returns:
            RoleReachability with connectivity information
        """
        if reachable_classes is None:
            reachable_classes = set(range(1, 50))

        # Compute legal edges at class level
        legal_edges = set()
        for (i, j) in self._baseline_edges:
            if i in reachable_classes and j in reachable_classes:
                legal_edges.add((i, j))

        # Aggregate to role level
        role_transitions: Dict[Tuple[ControlRole, ControlRole], bool] = {}
        role_edge_counts: Dict[Tuple[ControlRole, ControlRole], int] = {}

        # Initialize all pairs as False/0
        for role_a in ControlRole:
            for role_b in ControlRole:
                pair = (role_a, role_b)
                role_transitions[pair] = False
                role_edge_counts[pair] = 0

        # Count edges per role pair
        for (i, j) in legal_edges:
            role_i = self.classifier.classify(i)
            role_j = self.classifier.classify(j)
            pair = (role_i, role_j)
            role_edge_counts[pair] += 1
            if role_edge_counts[pair] > 0:
                role_transitions[pair] = True

        # Count pruned classes
        pruned = set(range(1, 50)) - reachable_classes

        return RoleReachability(
            legal_transitions=role_transitions,
            edge_counts=role_edge_counts,
            total_legal_edges=len(legal_edges),
            total_possible_edges=len(self._baseline_edges),
            reachable_classes=len(reachable_classes),
            pruned_classes=len(pruned)
        )

    def compute_hazard_status(
        self,
        reachable_classes: Optional[Set[int]] = None,
        folio_classes: Optional[Set[int]] = None
    ) -> HazardStatus:
        """
        Compute hazard class active/suppressed counts.

        Per C109: 17 hazards in 5 failure classes.
        Atomic hazards (7, 9, 23) are always active.
        Decomposable hazards are AZC-tunable via MIDDLE availability.

        Args:
            reachable_classes: Set of legal class IDs, or None for baseline
            folio_classes: Optional set of classes used by a specific B folio.
                          If provided, computes Stage 2 (folio-specific) hazard status.

        Returns:
            HazardStatus with per-class counts
        """
        if reachable_classes is None:
            reachable_classes = set(range(1, 50))

        # Failure class totals (from C109)
        failure_classes = {
            "PHASE_ORDERING": 7,      # 41%
            "COMPOSITION_JUMP": 4,    # 24%
            "CONTAINMENT_TIMING": 4,  # 24%
            "RATE_MISMATCH": 1,       # 6%
            "ENERGY_OVERSHOOT": 1,    # 6%
        }

        # For now, compute based on which hazard-involved classes are reachable
        atomic = self.data_store.atomic_hazard_classes
        decomposable = self.data_store.decomposable_hazard_classes

        # If folio_classes provided, filter to only hazards the folio uses (Stage 2)
        if folio_classes is not None:
            folio_atomic = atomic & folio_classes
            folio_decomposable = decomposable & folio_classes
        else:
            folio_atomic = atomic
            folio_decomposable = decomposable

        # Atomic are always active (but only count those relevant to folio)
        atomic_active = len(folio_atomic)
        atomic_total = len(folio_atomic)

        # Decomposable depend on class reachability
        decomposable_active = len(folio_decomposable & reachable_classes)
        decomposable_suppressed = len(folio_decomposable) - decomposable_active
        decomposable_total = len(folio_decomposable)

        # Distribute suppression across failure classes proportionally
        # (simplified - in reality would need forbidden pair analysis)
        total_suppression_rate = decomposable_suppressed / max(decomposable_total, 1)

        active_by_class = {}
        total_by_class = {}
        for cls_name, total in failure_classes.items():
            total_by_class[cls_name] = total
            # Atomic hazards don't suppress; distribute suppression to others
            if cls_name == "PHASE_ORDERING":
                # Mostly atomic-adjacent, less suppressible
                active_by_class[cls_name] = max(3, int(total * (1 - total_suppression_rate * 0.5)))
            else:
                active_by_class[cls_name] = max(0, int(total * (1 - total_suppression_rate)))

        return HazardStatus(
            active_by_class=active_by_class,
            total_by_class=total_by_class,
            atomic_active=atomic_active,
            atomic_total=atomic_total,
            decomposable_active=decomposable_active,
            decomposable_total=decomposable_total
        )
