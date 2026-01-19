"""
Role Classifier - Maps 49 instruction classes to 6 documented roles.

Per C411: ~40% of grammar is reducible, justifying role collapse.
Per BCSC: Role taxonomy is documented and constraint-grounded.

Roles are structural categories, not semantic labels.
"""

from enum import Enum
from typing import Set, Dict


class ControlRole(Enum):
    """Six documented control roles from BCSC."""
    KERNEL_ENERGY = "k"      # C103: k = ENERGY_MODULATOR
    KERNEL_PHASE = "h"       # C104: h = PHASE_MANAGER
    KERNEL_STABILITY = "e"   # C105: e = STABILITY_ANCHOR
    MONITORING = "link"      # C366: LINK marks monitoring boundary
    AUXILIARY = "aux"        # BCSC: 8 support classes
    HIGH_IMPACT = "high"     # BCSC: 3 major intervention classes


# Role display properties
ROLE_COLORS = {
    ControlRole.KERNEL_ENERGY: "#e07020",    # Orange - energy/heat
    ControlRole.KERNEL_PHASE: "#2070c0",     # Blue - phase
    ControlRole.KERNEL_STABILITY: "#20a050", # Green - stability
    ControlRole.MONITORING: "#808080",       # Gray - observation
    ControlRole.AUXILIARY: "#6090b0",        # Light blue - support
    ControlRole.HIGH_IMPACT: "#c04040",      # Red - major intervention
}

ROLE_LABELS = {
    ControlRole.KERNEL_ENERGY: "Energy (k)",
    ControlRole.KERNEL_PHASE: "Phase (h)",
    ControlRole.KERNEL_STABILITY: "Stability (e)",
    ControlRole.MONITORING: "Monitoring",
    ControlRole.AUXILIARY: "Auxiliary",
    ControlRole.HIGH_IMPACT: "High Impact",
}


class RoleClassifier:
    """
    Maps 49 instruction classes to 6 documented roles.

    This is a structural projection, not semantic interpretation.
    The mapping is derived from BCSC role taxonomy.
    """

    def __init__(self, data_store):
        """
        Initialize classifier from data store.

        Args:
            data_store: DataStore instance with instruction class info
        """
        self.data_store = data_store
        self._build_mappings()

    def _build_mappings(self):
        """Build class-to-role mappings from data store."""
        self._class_to_role: Dict[int, ControlRole] = {}
        self._role_to_classes: Dict[ControlRole, Set[int]] = {
            role: set() for role in ControlRole
        }

        for class_id in range(1, 50):
            role = self._determine_role(class_id)
            self._class_to_role[class_id] = role
            self._role_to_classes[role].add(class_id)

    def _determine_role(self, class_id: int) -> ControlRole:
        """
        Determine role for a given instruction class.

        Uses functional_role from instruction class data directly.
        Maps data roles to display roles per BCSC taxonomy.
        """
        ic = self.data_store.classes.get(class_id)
        if not ic or not ic.role:
            return ControlRole.AUXILIARY

        role = ic.role.upper()

        # Map data roles (from phase20a) to display roles
        if role == 'ENERGY_OPERATOR':
            return ControlRole.KERNEL_ENERGY  # Energy control (18 classes)
        elif role == 'FLOW_OPERATOR':
            return ControlRole.KERNEL_PHASE   # Phase/flow management (3 classes)
        elif role == 'CORE_CONTROL':
            return ControlRole.KERNEL_STABILITY  # Stability anchor: daiin, ol (2 classes)
        elif role == 'HIGH_IMPACT':
            return ControlRole.HIGH_IMPACT  # Major interventions (1 class)
        elif role == 'FREQUENT_OPERATOR':
            return ControlRole.AUXILIARY  # Common operations (6 classes)
        elif role == 'AUXILIARY':
            return ControlRole.AUXILIARY  # Support operations (18 classes)

        # Default fallback
        return ControlRole.AUXILIARY

    def classify(self, class_id: int) -> ControlRole:
        """
        Return the role for a given instruction class.

        Args:
            class_id: Instruction class ID (1-49)

        Returns:
            ControlRole for the class
        """
        return self._class_to_role.get(class_id, ControlRole.AUXILIARY)

    def get_classes_for_role(self, role: ControlRole) -> Set[int]:
        """
        Return all instruction classes belonging to a role.

        Args:
            role: ControlRole to query

        Returns:
            Set of class IDs in that role
        """
        return self._role_to_classes.get(role, set()).copy()

    def get_role_color(self, role: ControlRole) -> str:
        """Get display color for a role."""
        return ROLE_COLORS.get(role, "#808080")

    def get_role_label(self, role: ControlRole) -> str:
        """Get display label for a role."""
        return ROLE_LABELS.get(role, role.value)
