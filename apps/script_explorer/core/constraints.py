"""
Constraints module - Loads and queries the 411+ validated constraints.

Parses the constraint index and individual constraint files from context/CLAIMS/.
Provides searchable access to constraint metadata and full text.

All constraints are Tier 0-2 (frozen/validated) unless marked otherwise.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ConstraintTier(Enum):
    """
    Constraint validation tier.

    Tier 0: Frozen facts - cannot be modified
    Tier 1: Falsified hypotheses - cannot be retried
    Tier 2: Validated findings - supported by evidence
    Tier 3: Speculative - plausible but unconfirmed
    Tier 4: Interpretive - specific interpretations
    """
    TIER_0 = 0  # Frozen
    TIER_1 = 1  # Falsified
    TIER_2 = 2  # Validated
    TIER_3 = 3  # Speculative
    TIER_4 = 4  # Interpretive


@dataclass
class Constraint:
    """A single validated constraint."""
    number: int                    # C-number (e.g., 074)
    description: str               # Short description
    tier: ConstraintTier           # Validation tier
    category: str = ""             # Category (e.g., "Executability", "Grammar")
    file_path: Optional[str] = None  # Path to individual file if exists
    registry: Optional[str] = None   # Grouped registry if not individual file
    full_text: str = ""            # Full constraint text (loaded on demand)
    keywords: List[str] = field(default_factory=list)  # Extracted keywords

    @property
    def id(self) -> str:
        """Get constraint ID (e.g., 'C074')."""
        return f"C{self.number:03d}"

    @property
    def is_frozen(self) -> bool:
        """Check if this is a frozen (Tier 0) constraint."""
        return self.tier == ConstraintTier.TIER_0

    @property
    def is_falsified(self) -> bool:
        """Check if this is a falsified hypothesis."""
        return self.tier == ConstraintTier.TIER_1


class ConstraintLoader:
    """
    Loads and indexes constraints from context/CLAIMS/.

    Provides:
    - Full constraint catalog (411+ constraints)
    - Search by number, keyword, tier, or category
    - Lazy loading of full text from individual files
    """

    def __init__(self, claims_path: Optional[str] = None):
        self.constraints: Dict[int, Constraint] = {}
        self._categories: Dict[str, List[int]] = {}
        self._keywords_index: Dict[str, List[int]] = {}

        # Find claims directory
        if claims_path:
            self.claims_path = Path(claims_path)
        else:
            self.claims_path = self._find_claims_path()

        if self.claims_path and self.claims_path.exists():
            self._load_index()

    def _find_claims_path(self) -> Optional[Path]:
        """Find the context/CLAIMS/ directory."""
        candidates = [
            Path(__file__).parent.parent.parent.parent / 'context' / 'CLAIMS',
            Path('C:/git/voynich/context/CLAIMS'),
            Path('context/CLAIMS'),
        ]
        for path in candidates:
            if path.exists():
                return path
        return None

    def _load_index(self):
        """Load constraints from INDEX.md."""
        index_path = self.claims_path / 'INDEX.md'
        if not index_path.exists():
            return

        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse sections and tables
        current_category = ""
        in_table = False

        # Pattern for table rows: | ### | Description | Tier | Status |
        row_pattern = re.compile(
            r'\|\s*\*{0,2}(\d{3})\*{0,2}\s*\|([^|]+)\|([^|]+)\|([^|]+)\|'
        )

        for line in content.split('\n'):
            # Check for section headers
            if line.startswith('## ') and not line.startswith('## How') and not line.startswith('## Grouped'):
                current_category = line[3:].strip()
                # Clean category name (remove C-number ranges)
                if '(' in current_category:
                    current_category = current_category.split('(')[0].strip()
                continue

            # Parse table rows
            match = row_pattern.match(line)
            if match:
                num_str = match.group(1)
                description = match.group(2).strip()
                tier_str = match.group(3).strip()
                status = match.group(4).strip()

                try:
                    number = int(num_str)
                except ValueError:
                    continue

                # Parse tier
                tier = self._parse_tier(tier_str)

                # Parse status for file/registry info
                file_path = None
                registry = None
                if '→' in status:
                    # Has individual file
                    file_match = re.search(r'\[([^\]]+\.md)\]', status)
                    if file_match:
                        file_path = file_match.group(1)
                elif '⊂' in status:
                    # In grouped registry
                    registry_match = re.search(r'⊂\s*(\w+)', status)
                    if registry_match:
                        registry = registry_match.group(1)

                # Extract keywords from description
                keywords = self._extract_keywords(description)

                constraint = Constraint(
                    number=number,
                    description=description,
                    tier=tier,
                    category=current_category,
                    file_path=file_path,
                    registry=registry,
                    keywords=keywords
                )

                self.constraints[number] = constraint

                # Index by category
                if current_category not in self._categories:
                    self._categories[current_category] = []
                self._categories[current_category].append(number)

                # Index by keywords
                for kw in keywords:
                    if kw not in self._keywords_index:
                        self._keywords_index[kw] = []
                    self._keywords_index[kw].append(number)

    def _parse_tier(self, tier_str: str) -> ConstraintTier:
        """Parse tier from string."""
        tier_str = tier_str.strip()
        if tier_str == '0':
            return ConstraintTier.TIER_0
        elif tier_str == '1':
            return ConstraintTier.TIER_1
        elif tier_str == '2':
            return ConstraintTier.TIER_2
        elif tier_str == '3':
            return ConstraintTier.TIER_3
        elif tier_str == '4':
            return ConstraintTier.TIER_4
        else:
            return ConstraintTier.TIER_2  # Default to validated

    def _extract_keywords(self, description: str) -> List[str]:
        """Extract searchable keywords from description."""
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', description.lower())
        words = text.split()

        # Filter stopwords and short words
        stopwords = {'the', 'a', 'an', 'is', 'are', 'in', 'of', 'to', 'for', 'and', 'or', 'not'}
        keywords = [w for w in words if len(w) > 2 and w not in stopwords]

        return list(set(keywords))

    def load_full_text(self, constraint: Constraint) -> str:
        """Load full text for a constraint from its file."""
        if constraint.full_text:
            return constraint.full_text

        if not constraint.file_path or not self.claims_path:
            return ""

        file_path = self.claims_path / constraint.file_path
        if not file_path.exists():
            return ""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                constraint.full_text = f.read()
        except Exception:
            constraint.full_text = ""

        return constraint.full_text

    def get(self, number: int) -> Optional[Constraint]:
        """Get constraint by number."""
        return self.constraints.get(number)

    def get_by_id(self, constraint_id: str) -> Optional[Constraint]:
        """Get constraint by ID string (e.g., 'C074')."""
        match = re.match(r'C(\d+)', constraint_id, re.IGNORECASE)
        if match:
            return self.get(int(match.group(1)))
        return None

    def search(self, query: str) -> List[Constraint]:
        """
        Search constraints by keyword or description.

        Args:
            query: Search query (keyword, phrase, or C-number)

        Returns:
            List of matching constraints
        """
        query = query.strip()

        # Check for C-number search
        if re.match(r'^C?\d+$', query, re.IGNORECASE):
            num = int(re.sub(r'\D', '', query))
            c = self.get(num)
            return [c] if c else []

        # Keyword search
        query_lower = query.lower()
        results = []
        seen = set()

        # Search in descriptions
        for c in self.constraints.values():
            if query_lower in c.description.lower():
                if c.number not in seen:
                    results.append(c)
                    seen.add(c.number)

        # Search in keywords
        for kw, numbers in self._keywords_index.items():
            if query_lower in kw:
                for num in numbers:
                    if num not in seen:
                        results.append(self.constraints[num])
                        seen.add(num)

        return sorted(results, key=lambda c: c.number)

    def get_by_tier(self, tier: ConstraintTier) -> List[Constraint]:
        """Get all constraints of a specific tier."""
        return [c for c in self.constraints.values() if c.tier == tier]

    def get_by_category(self, category: str) -> List[Constraint]:
        """Get all constraints in a category."""
        numbers = self._categories.get(category, [])
        return [self.constraints[n] for n in numbers if n in self.constraints]

    def get_frozen(self) -> List[Constraint]:
        """Get all Tier 0 (frozen) constraints."""
        return self.get_by_tier(ConstraintTier.TIER_0)

    def get_categories(self) -> List[str]:
        """Get list of all categories."""
        return sorted(self._categories.keys())

    def find_for_token(self, token: str) -> List[Constraint]:
        """Find constraints that mention a specific token."""
        results = []
        token_lower = token.lower()

        for c in self.constraints.values():
            if token_lower in c.description.lower():
                results.append(c)
            elif token_lower in c.keywords:
                results.append(c)

        return results

    @property
    def total_count(self) -> int:
        """Total number of constraints loaded."""
        return len(self.constraints)

    @property
    def frozen_count(self) -> int:
        """Number of Tier 0 constraints."""
        return len([c for c in self.constraints.values() if c.is_frozen])
