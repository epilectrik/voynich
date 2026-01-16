"""
Grammar module - Instruction classes and operator roles.

CONSTRAINT-COMPLIANT VERSION
- Structural labels only, no semantic interpretation
- Based on frozen canonical grammar (49 instruction classes)
- All facts traceable to constraint numbers
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
import json


class OperatorRole(Enum):
    """
    Operator roles from the canonical grammar.
    These are STRUCTURAL labels derived from corpus statistics, NOT semantic meanings.

    Constraint reference: C098 (49-class grammar taxonomy)
    """
    ENERGY_OPERATOR = auto()      # Statistical cluster with high k-content
    FLOW_OPERATOR = auto()        # Statistical cluster with high h-content
    CORE_CONTROL = auto()         # High-frequency control tokens (daiin, ol)
    HIGH_IMPACT = auto()          # Low-frequency, high-effect tokens
    FREQUENT_OPERATOR = auto()    # Common operations
    AUXILIARY = auto()            # Support operations
    LINK = auto()                 # Tokens with LINK behavior (C105)
    MODIFIER = auto()             # Parameter modifiers
    TERMINAL = auto()             # Sequence terminators


@dataclass
class InstructionClass:
    """
    Represents one of the 49 instruction equivalence classes.

    Constraint reference: C098 (9.8x compression to 49 classes)
    """
    id: int
    symbol: str                   # EVA symbol (e.g., 'qokaiin', 'chey')
    role: OperatorRole
    display_label: str            # Human-readable role label
    aggressiveness: float         # 0.0-1.0, derived from frequency rank (structural)
    is_link: bool = False         # Whether this is a LINK instruction (C105)

    # Members of this equivalence class
    members: List[str] = None

    def __post_init__(self):
        if self.members is None:
            self.members = [self.symbol]


class Grammar:
    """
    The frozen control grammar.

    Defines instruction classes, their roles, and structural properties.
    Loads from Phase 20A equivalence class data for complete token coverage.

    Constraint references:
    - C098: 49-class grammar (9.8x compression)
    - C099: Forbidden transition pairs
    - C105: LINK density and behavior
    """

    # Role string to enum mapping
    ROLE_MAP = {
        'ENERGY_OPERATOR': OperatorRole.ENERGY_OPERATOR,
        'FLOW_OPERATOR': OperatorRole.FLOW_OPERATOR,
        'CORE_CONTROL': OperatorRole.CORE_CONTROL,
        'HIGH_IMPACT': OperatorRole.HIGH_IMPACT,
        'FREQUENT_OPERATOR': OperatorRole.FREQUENT_OPERATOR,
        'AUXILIARY': OperatorRole.AUXILIARY,
        'LINK': OperatorRole.LINK,
        'MODIFIER': OperatorRole.MODIFIER,
        'TERMINAL': OperatorRole.TERMINAL,
    }

    # Role display labels
    ROLE_LABELS = {
        OperatorRole.ENERGY_OPERATOR: 'ENERGY_OP',
        OperatorRole.FLOW_OPERATOR: 'FLOW_OP',
        OperatorRole.CORE_CONTROL: 'CORE_CONTROL',
        OperatorRole.HIGH_IMPACT: 'HIGH_IMPACT',
        OperatorRole.FREQUENT_OPERATOR: 'FREQUENT',
        OperatorRole.AUXILIARY: 'AUXILIARY',
        OperatorRole.LINK: 'LINK',
        OperatorRole.MODIFIER: 'MODIFIER',
        OperatorRole.TERMINAL: 'TERMINAL',
    }

    def __init__(self):
        self._classes: Dict[int, InstructionClass] = {}
        self._by_symbol: Dict[str, InstructionClass] = {}
        self._forbidden_pairs: List[tuple] = []  # (from_token, to_token, severity)
        self._load_canonical_grammar()
        self._load_forbidden_pairs()

    def _load_canonical_grammar(self):
        """Load the canonical 49-class grammar from Phase 20A data."""
        json_path = self._find_phase20a_file()

        if json_path and json_path.exists():
            self._load_from_json(json_path)
        else:
            self._load_fallback_grammar()

    def _find_phase20a_file(self) -> Optional[Path]:
        """Find the Phase 20A equivalence class JSON."""
        candidates = [
            Path(__file__).parent.parent.parent.parent / 'phases' / '01-09_early_hypothesis' / 'phase20a_operator_equivalence.json',
            Path('C:/git/voynich/phases/01-09_early_hypothesis/phase20a_operator_equivalence.json'),
            Path('phases/01-09_early_hypothesis/phase20a_operator_equivalence.json'),
        ]

        for path in candidates:
            if path.exists():
                return path
        return None

    def _load_from_json(self, json_path: Path):
        """Load grammar from Phase 20A JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for cls_data in data.get('classes', []):
            class_id = cls_data['class_id']
            representative = cls_data['representative']
            role_str = cls_data['functional_role']
            members = cls_data.get('members', [representative])

            role = self.ROLE_MAP.get(role_str, OperatorRole.AUXILIARY)
            is_link = (role == OperatorRole.LINK)
            display_label = self.ROLE_LABELS.get(role, 'UNKNOWN')

            # Aggressiveness from frequency rank (structural, not semantic)
            sig = cls_data.get('behavioral_signature', {})
            aggressiveness = sig.get('mean_frequency_rank', 0.5)

            instr = InstructionClass(
                id=class_id,
                symbol=representative,
                role=role,
                display_label=display_label,
                aggressiveness=aggressiveness,
                is_link=is_link,
                members=members
            )

            self._classes[class_id] = instr

            for member in members:
                if member:
                    self._by_symbol[member.lower()] = instr

    def _load_fallback_grammar(self):
        """Fallback to hardcoded minimal grammar if JSON not found."""
        definitions = [
            (7, 'qokaiin', OperatorRole.ENERGY_OPERATOR, 'ENERGY_OP', 0.7, False),
            (10, 'chey', OperatorRole.ENERGY_OPERATOR, 'ENERGY_OP', 0.3, False),
            (12, 'cheey', OperatorRole.ENERGY_OPERATOR, 'ENERGY_OP', 0.4, False),
            (31, 'chedy', OperatorRole.ENERGY_OPERATOR, 'ENERGY_OP', 0.6, False),
            (29, 'dar', OperatorRole.AUXILIARY, 'AUXILIARY', 0.3, False),  # da- prefix + -r suffix = kernel-light auxiliary
            (30, 'chol', OperatorRole.FLOW_OPERATOR, 'FLOW_OP', 0.4, False),
            (32, 'daiin', OperatorRole.CORE_CONTROL, 'CORE_CONTROL', 0.5, False),
            (33, 'ol', OperatorRole.CORE_CONTROL, 'CORE_CONTROL', 0.2, False),
            (34, 'aiin', OperatorRole.HIGH_IMPACT, 'HIGH_IMPACT', 0.8, False),
            (38, 'okaiin', OperatorRole.FREQUENT_OPERATOR, 'FREQUENT', 0.5, False),
            (44, 'saiin', OperatorRole.AUXILIARY, 'AUXILIARY', 0.3, False),
            (28, 'dy', OperatorRole.FREQUENT_OPERATOR, 'FREQUENT', 0.5, False),
        ]

        for defn in definitions:
            id_, symbol, role, label, aggr, is_link = defn
            instr = InstructionClass(
                id=id_,
                symbol=symbol,
                role=role,
                display_label=label,
                aggressiveness=aggr,
                is_link=is_link
            )
            self._classes[id_] = instr
            self._by_symbol[symbol] = instr

    def _load_forbidden_pairs(self):
        """
        Load forbidden transition pairs from hazards data.

        Constraint reference: C099 (forbidden bigram pairs)
        """
        # Try to load from hazards.py data file
        hazards_paths = [
            Path(__file__).parent.parent.parent.parent / 'vee' / 'app' / 'core' / 'hazards.py',
            Path('C:/git/voynich/vee/app/core/hazards.py'),
        ]

        # For now, use a minimal set - will expand when hazards.py is parsed
        # These are from C099 forbidden pairs
        self._forbidden_pairs = []

    def get_by_id(self, id_: int) -> Optional[InstructionClass]:
        """Get instruction class by ID."""
        return self._classes.get(id_)

    def get_by_symbol(self, symbol: str) -> Optional[InstructionClass]:
        """Get instruction class by EVA symbol."""
        return self._by_symbol.get(symbol.lower() if symbol else None)

    def get_all_classes(self) -> List[InstructionClass]:
        """Get all instruction classes."""
        return list(self._classes.values())

    def get_by_role(self, role: OperatorRole) -> List[InstructionClass]:
        """Get all instruction classes with a specific role."""
        return [c for c in self._classes.values() if c.role == role]

    def get_link_classes(self) -> List[InstructionClass]:
        """Get all LINK instruction classes."""
        return [c for c in self._classes.values() if c.is_link]

    def get_forbidden_successors(self, token: str) -> List[str]:
        """
        Get tokens that cannot follow the given token.

        Constraint reference: C099
        """
        return [to_tok for from_tok, to_tok, _ in self._forbidden_pairs
                if from_tok.lower() == token.lower()]

    def is_forbidden_transition(self, from_token: str, to_token: str) -> bool:
        """Check if a transition is forbidden."""
        from_lower = from_token.lower() if from_token else ''
        to_lower = to_token.lower() if to_token else ''
        return any(f.lower() == from_lower and t.lower() == to_lower
                   for f, t, _ in self._forbidden_pairs)

    @property
    def class_count(self) -> int:
        """Number of instruction classes."""
        return len(self._classes)

    @property
    def token_count(self) -> int:
        """Number of tokens mapped to classes."""
        return len(self._by_symbol)
