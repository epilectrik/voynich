#!/usr/bin/env python3
"""
Generate replication groups for parallel validation.

Creates:
- SAME_HUB_TYPE groups for OPENER and SUPPORT roles
- RANDOM groups for null comparison
- SAME_CATEGORY expansion groups
"""

import json
import random
from itertools import combinations
from datetime import datetime
from annotation_config import load_folio_metadata, get_all_available_folios

def get_folios_by_role():
    """Get hub folios organized by functional role."""
    metadata = load_folio_metadata()
    roles = {"opener": [], "closer": [], "support": []}

    for folio_id, meta in metadata.items():
        if meta.hub_status == "hub" and meta.category_role:
            roles[meta.category_role].append(folio_id)

    return roles

def get_multi_folio_categories():
    """Get categories with 2+ folios."""
    metadata = load_folio_metadata()
    categories = {}

    for folio_id, meta in metadata.items():
        if meta.heading not in categories:
            categories[meta.heading] = []
        categories[meta.heading].append(folio_id)

    return {cat: folios for cat, folios in categories.items() if len(folios) >= 2}

def generate_same_hub_type_groups(roles, target_n=7, group_size=4):
    """
    Generate SAME_HUB_TYPE groups.

    For roles with enough folios, create groups from combinations.
    For roles with few folios, create all possible groups.
    """
    groups = []

    # OPENER groups - we have 6 folios, can make many groups
    opener_folios = roles["opener"]
    if len(opener_folios) >= group_size:
        # Generate unique combinations
        opener_combos = list(combinations(opener_folios, group_size))
        # Shuffle and take what we need
        random.shuffle(opener_combos)
        for combo in opener_combos[:5]:  # Target 5 OPENER groups
            groups.append({
                "group_type": "same_hub_type",
                "group_basis": "opener",
                "folio_ids": list(combo),
                "is_null_group": False,
                "is_foil_group": False
            })

    # SUPPORT groups - only 2 folios (f42r, f58r)
    # Can't form a 4-folio group from 2 folios
    # We'll need to include related folios or use smaller group size
    support_folios = roles["support"]
    if len(support_folios) >= 2:
        # For SUPPORT, we can test with 2-folio comparison
        # or include other high-similarity folios
        # For now, generate pairs for comparative questions
        groups.append({
            "group_type": "same_hub_type",
            "group_basis": "support",
            "folio_ids": support_folios,  # Just the 2 support folios
            "is_null_group": False,
            "is_foil_group": False,
            "note": "SUPPORT has only 2 folios - limited test"
        })

    return groups

def generate_random_groups(all_folios, existing_groups, target_n=9, group_size=4):
    """Generate RANDOM groups for null comparison."""
    groups = []
    used_combos = set()

    # Avoid exact overlaps with existing groups
    for g in existing_groups:
        if "folio_ids" in g:
            used_combos.add(frozenset(g["folio_ids"]))

    attempts = 0
    max_attempts = 1000

    while len(groups) < target_n and attempts < max_attempts:
        combo = tuple(sorted(random.sample(all_folios, group_size)))
        if frozenset(combo) not in used_combos:
            used_combos.add(frozenset(combo))
            groups.append({
                "group_type": "random",
                "group_basis": "random",
                "folio_ids": list(combo),
                "is_null_group": True,
                "is_foil_group": False
            })
        attempts += 1

    return groups

def generate_same_category_groups(categories, target_n=8, group_size=4):
    """Generate SAME_CATEGORY groups for expansion."""
    groups = []

    for category, folios in categories.items():
        if len(folios) >= 2:
            # If category has 2 folios, pad with random from same cluster
            if len(folios) < group_size:
                # Use what we have
                groups.append({
                    "group_type": "same_category",
                    "group_basis": category,
                    "folio_ids": folios,
                    "is_null_group": False,
                    "is_foil_group": False,
                    "note": f"Category has only {len(folios)} folios"
                })
            else:
                # Can make full-size groups
                combos = list(combinations(folios, group_size))
                for combo in combos[:2]:  # Max 2 per category
                    groups.append({
                        "group_type": "same_category",
                        "group_basis": category,
                        "folio_ids": list(combo),
                        "is_null_group": False,
                        "is_foil_group": False
                    })

        if len(groups) >= target_n:
            break

    return groups

def main():
    """Generate all replication groups."""
    random.seed(42)  # Reproducibility

    print("=" * 60)
    print("REPLICATION GROUP GENERATOR")
    print("=" * 60)

    # Load data
    roles = get_folios_by_role()
    categories = get_multi_folio_categories()
    all_folios = get_all_available_folios()

    print(f"\nHub folios by role:")
    for role, folios in roles.items():
        print(f"  {role.upper()}: {folios} (N={len(folios)})")

    print(f"\nMulti-folio categories:")
    for cat, folios in categories.items():
        print(f"  {cat}: {folios}")

    print(f"\nTotal available folios: {len(all_folios)}")

    # Generate groups
    print("\n" + "-" * 40)
    print("Generating groups...")

    hub_groups = generate_same_hub_type_groups(roles)
    print(f"  SAME_HUB_TYPE groups: {len(hub_groups)}")

    random_groups = generate_random_groups(all_folios, hub_groups)
    print(f"  RANDOM groups: {len(random_groups)}")

    category_groups = generate_same_category_groups(categories)
    print(f"  SAME_CATEGORY groups: {len(category_groups)}")

    # Combine all groups
    all_groups = hub_groups + random_groups + category_groups

    # Output structure
    output = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "total_groups": len(all_groups),
            "by_type": {
                "same_hub_type": len(hub_groups),
                "random": len(random_groups),
                "same_category": len(category_groups)
            },
            "closer_role_status": "UNTESTABLE",
            "closer_reason": "Only 1 folio available (f22r); f96r is text-only",
            "closer_implication": "CLOSER visual coherence cannot be independently validated"
        },
        "hub_role_summary": {
            "OPENER": {
                "folios": roles["opener"],
                "count": len(roles["opener"]),
                "testable": len(roles["opener"]) >= 4
            },
            "CLOSER": {
                "folios": roles["closer"],
                "count": len(roles["closer"]),
                "testable": False
            },
            "SUPPORT": {
                "folios": roles["support"],
                "count": len(roles["support"]),
                "testable": len(roles["support"]) >= 2
            }
        },
        "groups": all_groups
    }

    # Save
    output_path = "annotation_data/replication_groups.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Output saved to: {output_path}")
    print(f"{'=' * 60}")

    # Summary
    print("\nGROUP SUMMARY:")
    print("-" * 40)
    for group in all_groups:
        print(f"  {group['group_type']} ({group['group_basis']}): {group['folio_ids']}")

    return output

if __name__ == "__main__":
    main()
