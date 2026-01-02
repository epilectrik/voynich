#!/usr/bin/env python3
"""
Group Generator for Comparative Annotation System.

Handles:
- Group type selection (hypothesis-driven, null, foil)
- Folio selection per group type
- Position randomization
- Group history tracking to avoid immediate repeats
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum

from annotation_config import (
    GroupType, GROUP_WEIGHTS,
    load_folio_metadata, FolioMetadata,
    get_category_to_folios, get_multi_folio_categories,
    get_hub_categories, get_prefix_groups, get_cluster_groups,
    get_foil_pairs, get_all_available_folios
)


@dataclass
class GroupResult:
    """Result of group generation."""
    group_type: GroupType
    group_basis: str  # The category/prefix/cluster/etc that defines the group
    folio_ids: List[str]  # Actual folio IDs in the group
    position_mapping: Dict[str, str]  # folio_id -> position label (A, B, C, etc.)
    is_hypothesis_driven: bool
    is_null: bool
    is_foil: bool


class GroupGenerator:
    """
    Generates groups for Mode B comparative questions.

    Maintains state to avoid immediate repeats and track coverage.
    """

    def __init__(self, target_group_size: int = 4, seed: Optional[int] = None):
        """
        Initialize group generator.

        Args:
            target_group_size: Number of images per group (default 4)
            seed: Random seed for reproducibility
        """
        self.target_group_size = target_group_size
        self.rng = random.Random(seed)

        # Load data
        self.folio_metadata = load_folio_metadata()
        self.all_folios = list(self.folio_metadata.keys())

        # Build grouping indices
        self.category_to_folios = get_category_to_folios()
        self.multi_folio_categories = get_multi_folio_categories()
        self.hub_categories = get_hub_categories()
        self.prefix_groups = get_prefix_groups()
        self.cluster_groups = get_cluster_groups()
        self.foil_pairs = get_foil_pairs()

        # Filter to groups with enough folios
        self.viable_categories = {
            cat: folios for cat, folios in self.category_to_folios.items()
            if len(folios) >= 2
        }
        self.viable_prefixes = {
            prefix: folios for prefix, folios in self.prefix_groups.items()
            if len(folios) >= target_group_size
        }
        self.viable_clusters = {
            cluster: folios for cluster, folios in self.cluster_groups.items()
            if len(folios) >= target_group_size
        }

        # Hub role groupings
        self.hub_roles = self._build_hub_role_groups()

        # History tracking
        self.recent_groups: List[Set[str]] = []
        self.max_history = 5

    def _build_hub_role_groups(self) -> Dict[str, List[str]]:
        """Build groups based on hub functional roles."""
        role_groups = {"opener": [], "closer": [], "support": []}

        for folio_id, meta in self.folio_metadata.items():
            if meta.category_role:
                role_groups[meta.category_role].append(folio_id)

        # Filter to roles with enough folios
        return {
            role: folios for role, folios in role_groups.items()
            if len(folios) >= 2
        }

    def _select_group_type(self) -> GroupType:
        """Select group type based on configured weights."""
        types = list(GROUP_WEIGHTS.keys())
        weights = list(GROUP_WEIGHTS.values())
        return self.rng.choices(types, weights=weights, k=1)[0]

    def _get_position_labels(self, n: int) -> List[str]:
        """Get position labels for n images."""
        labels = ['A', 'B', 'C', 'D', 'E', 'F']
        return labels[:n]

    def _randomize_positions(self, folio_ids: List[str]) -> Dict[str, str]:
        """Randomly assign position labels to folios."""
        shuffled = folio_ids.copy()
        self.rng.shuffle(shuffled)
        labels = self._get_position_labels(len(shuffled))
        return {folio: label for folio, label in zip(shuffled, labels)}

    def _is_repeat(self, folio_set: Set[str]) -> bool:
        """Check if this group was recently generated."""
        for recent in self.recent_groups:
            # Consider it a repeat if significant overlap
            overlap = len(folio_set & recent) / len(folio_set)
            if overlap >= 0.75:
                return True
        return False

    def _record_group(self, folio_ids: List[str]) -> None:
        """Record group in history."""
        self.recent_groups.append(set(folio_ids))
        if len(self.recent_groups) > self.max_history:
            self.recent_groups.pop(0)

    def generate_same_category_group(self) -> Optional[GroupResult]:
        """Generate group from same heading/category."""
        if not self.viable_categories:
            return None

        # Select a category with multiple folios
        category = self.rng.choice(list(self.viable_categories.keys()))
        folios = self.viable_categories[category].copy()

        # Pad with random folios if needed
        while len(folios) < self.target_group_size and len(self.all_folios) > len(folios):
            additional = [f for f in self.all_folios if f not in folios]
            if additional:
                folios.append(self.rng.choice(additional))
            else:
                break

        # Limit to target size
        if len(folios) > self.target_group_size:
            folios = self.rng.sample(folios, self.target_group_size)

        if self._is_repeat(set(folios)):
            return None

        self._record_group(folios)

        return GroupResult(
            group_type=GroupType.SAME_CATEGORY,
            group_basis=category,
            folio_ids=folios,
            position_mapping=self._randomize_positions(folios),
            is_hypothesis_driven=True,
            is_null=False,
            is_foil=False
        )

    def generate_same_hub_type_group(self) -> Optional[GroupResult]:
        """Generate group from same hub functional role."""
        if not self.hub_roles:
            return None

        role = self.rng.choice(list(self.hub_roles.keys()))
        folios = self.hub_roles[role].copy()

        # Pad if needed
        while len(folios) < self.target_group_size and len(self.all_folios) > len(folios):
            additional = [f for f in self.all_folios if f not in folios]
            if additional:
                folios.append(self.rng.choice(additional))
            else:
                break

        if len(folios) > self.target_group_size:
            folios = self.rng.sample(folios, self.target_group_size)

        if self._is_repeat(set(folios)):
            return None

        self._record_group(folios)

        return GroupResult(
            group_type=GroupType.SAME_HUB_TYPE,
            group_basis=role,
            folio_ids=folios,
            position_mapping=self._randomize_positions(folios),
            is_hypothesis_driven=True,
            is_null=False,
            is_foil=False
        )

    def generate_same_prefix_group(self) -> Optional[GroupResult]:
        """Generate group from same dominant prefix."""
        if not self.viable_prefixes:
            return None

        prefix = self.rng.choice(list(self.viable_prefixes.keys()))
        folios = self.rng.sample(
            self.viable_prefixes[prefix],
            min(self.target_group_size, len(self.viable_prefixes[prefix]))
        )

        if self._is_repeat(set(folios)):
            return None

        self._record_group(folios)

        return GroupResult(
            group_type=GroupType.SAME_PREFIX,
            group_basis=prefix,
            folio_ids=folios,
            position_mapping=self._randomize_positions(folios),
            is_hypothesis_driven=True,
            is_null=False,
            is_foil=False
        )

    def generate_same_cluster_group(self) -> Optional[GroupResult]:
        """Generate group from same classifier cluster."""
        if not self.viable_clusters:
            return None

        cluster = self.rng.choice(list(self.viable_clusters.keys()))
        folios = self.rng.sample(
            self.viable_clusters[cluster],
            min(self.target_group_size, len(self.viable_clusters[cluster]))
        )

        if self._is_repeat(set(folios)):
            return None

        self._record_group(folios)

        return GroupResult(
            group_type=GroupType.SAME_CLUSTER,
            group_basis=f"cluster_{cluster}",
            folio_ids=folios,
            position_mapping=self._randomize_positions(folios),
            is_hypothesis_driven=True,
            is_null=False,
            is_foil=False
        )

    def generate_random_group(self) -> Optional[GroupResult]:
        """Generate purely random group."""
        if len(self.all_folios) < self.target_group_size:
            return None

        folios = self.rng.sample(self.all_folios, self.target_group_size)

        if self._is_repeat(set(folios)):
            return None

        self._record_group(folios)

        return GroupResult(
            group_type=GroupType.RANDOM,
            group_basis="random",
            folio_ids=folios,
            position_mapping=self._randomize_positions(folios),
            is_hypothesis_driven=False,
            is_null=True,
            is_foil=False
        )

    def generate_stratified_random_group(self) -> Optional[GroupResult]:
        """Generate random group stratified by hub status."""
        # Try to get one from each status
        statuses = ['hub', 'mid', 'isolate']
        folios = []

        for status in statuses:
            matching = [
                f for f, m in self.folio_metadata.items()
                if m.hub_status == status and f not in folios
            ]
            if matching:
                folios.append(self.rng.choice(matching))

        # Pad to target size
        remaining = [f for f in self.all_folios if f not in folios]
        while len(folios) < self.target_group_size and remaining:
            choice = self.rng.choice(remaining)
            folios.append(choice)
            remaining.remove(choice)

        if len(folios) < self.target_group_size:
            return None

        if self._is_repeat(set(folios)):
            return None

        self._record_group(folios)

        return GroupResult(
            group_type=GroupType.STRATIFIED_RANDOM,
            group_basis="stratified",
            folio_ids=folios,
            position_mapping=self._randomize_positions(folios),
            is_hypothesis_driven=False,
            is_null=True,
            is_foil=False
        )

    def generate_foil_group(self) -> Optional[GroupResult]:
        """Generate group from maximally different categories."""
        if not self.foil_pairs:
            return self.generate_random_group()

        # Pick a foil pair
        cat_a, cat_b = self.rng.choice(self.foil_pairs)

        # Get folios from each category
        folios_a = self.category_to_folios.get(cat_a, [])
        folios_b = self.category_to_folios.get(cat_b, [])

        if not folios_a or not folios_b:
            return self.generate_random_group()

        folios = []

        # Take from each category
        if folios_a:
            folios.append(self.rng.choice(folios_a))
        if folios_b:
            folios.append(self.rng.choice(folios_b))

        # Pad with random from other categories
        used_cats = {cat_a, cat_b}
        other_folios = [
            f for f, m in self.folio_metadata.items()
            if m.heading not in used_cats and f not in folios
        ]

        while len(folios) < self.target_group_size and other_folios:
            choice = self.rng.choice(other_folios)
            folios.append(choice)
            other_folios.remove(choice)

        if len(folios) < self.target_group_size:
            return None

        if self._is_repeat(set(folios)):
            return None

        self._record_group(folios)

        return GroupResult(
            group_type=GroupType.KNOWN_DIFFERENT,
            group_basis=f"{cat_a}_vs_{cat_b}",
            folio_ids=folios,
            position_mapping=self._randomize_positions(folios),
            is_hypothesis_driven=False,
            is_null=False,
            is_foil=True
        )

    def generate_group(self, max_attempts: int = 10) -> Optional[GroupResult]:
        """
        Generate a group based on configured weights.

        Args:
            max_attempts: Maximum attempts before giving up

        Returns:
            GroupResult or None if generation fails
        """
        for _ in range(max_attempts):
            group_type = self._select_group_type()

            generators = {
                GroupType.SAME_CATEGORY: self.generate_same_category_group,
                GroupType.SAME_HUB_TYPE: self.generate_same_hub_type_group,
                GroupType.SAME_PREFIX: self.generate_same_prefix_group,
                GroupType.SAME_CLUSTER: self.generate_same_cluster_group,
                GroupType.RANDOM: self.generate_random_group,
                GroupType.STRATIFIED_RANDOM: self.generate_stratified_random_group,
                GroupType.KNOWN_DIFFERENT: self.generate_foil_group,
            }

            generator = generators.get(group_type)
            if generator:
                result = generator()
                if result:
                    return result

        # Fallback to random
        return self.generate_random_group()

    def generate_specific_group(self, group_type: GroupType) -> Optional[GroupResult]:
        """Generate a group of a specific type."""
        generators = {
            GroupType.SAME_CATEGORY: self.generate_same_category_group,
            GroupType.SAME_HUB_TYPE: self.generate_same_hub_type_group,
            GroupType.SAME_PREFIX: self.generate_same_prefix_group,
            GroupType.SAME_CLUSTER: self.generate_same_cluster_group,
            GroupType.RANDOM: self.generate_random_group,
            GroupType.STRATIFIED_RANDOM: self.generate_stratified_random_group,
            GroupType.KNOWN_DIFFERENT: self.generate_foil_group,
        }

        generator = generators.get(group_type)
        if generator:
            return generator()
        return None

    def get_statistics(self) -> Dict:
        """Get statistics about available groupings."""
        return {
            "total_folios": len(self.all_folios),
            "multi_folio_categories": len(self.viable_categories),
            "viable_prefixes": len(self.viable_prefixes),
            "viable_clusters": len(self.viable_clusters),
            "hub_roles_available": list(self.hub_roles.keys()),
            "foil_pairs_available": len(self.foil_pairs),
        }


if __name__ == "__main__":
    # Test the grouper
    print("Testing GroupGenerator...")
    print("=" * 60)

    generator = GroupGenerator(target_group_size=4, seed=42)

    print("\nGrouping Statistics:")
    stats = generator.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Generating sample groups...")
    print("=" * 60)

    # Generate one of each type
    for group_type in GroupType:
        print(f"\n{group_type.value}:")
        result = generator.generate_specific_group(group_type)
        if result:
            print(f"  Basis: {result.group_basis}")
            print(f"  Folios: {result.folio_ids}")
            print(f"  Positions: {result.position_mapping}")
            print(f"  Hypothesis: {result.is_hypothesis_driven}, Null: {result.is_null}, Foil: {result.is_foil}")
        else:
            print("  [Could not generate]")

    print("\n" + "=" * 60)
    print("Generating 10 random groups (weighted selection)...")
    print("=" * 60)

    type_counts = {}
    for i in range(10):
        result = generator.generate_group()
        if result:
            t = result.group_type.value
            type_counts[t] = type_counts.get(t, 0) + 1
            print(f"\n  Group {i+1}: {t} - {result.group_basis}")
            print(f"    Folios: {result.folio_ids}")

    print("\n  Type distribution:")
    for t, count in sorted(type_counts.items()):
        print(f"    {t}: {count}")
