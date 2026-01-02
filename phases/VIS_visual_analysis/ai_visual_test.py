#!/usr/bin/env python3
"""
AI-based visual cohesion test for replication validation.

This script:
1. Verifies folio-to-image alignment
2. Loads replication groups
3. Outputs groups for AI visual assessment
"""

import json
import csv
import os
from collections import defaultdict


def get_first_words():
    """Get first word of each folio from transcription."""
    first_words = {}
    with open("data/transcriptions/interlinear_full_words.txt", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            folio = row.get("folio", "")
            if folio and folio not in first_words:
                first_words[folio] = row.get("word", "")
    return first_words


def verify_alignment():
    """Verify folio ID to image alignment."""
    hub_folios = {
        "f42r": "sho",      # support
        "f58v": "tol",      # opener
        "f10v": "paiin",    # opener
        "f19r": "pchor",    # opener
        "f21r": "pchor",    # opener
        "f52v": "pchor",    # opener
        "f58r": "kor",      # support
        "f35v": "par",      # opener
        "f22r": "pol",      # closer
    }

    first_words = get_first_words()

    print("=" * 60)
    print("DATA ALIGNMENT VERIFICATION")
    print("=" * 60)
    print("\nHub Folio Alignment Check:")
    print("-" * 40)

    all_match = True
    for folio, expected_heading in hub_folios.items():
        actual = first_words.get(folio, "NOT_FOUND")
        match = "MATCH" if actual == expected_heading else "MISMATCH"
        if actual != expected_heading:
            all_match = False
        print(f"  {folio}: expected={expected_heading}, actual={actual} -> {match}")

    print("-" * 40)
    print(f"Overall alignment: {'VERIFIED' if all_match else 'ISSUES DETECTED'}")

    return all_match


def load_groups():
    """Load replication groups."""
    with open("annotation_data/replication_groups.json") as f:
        data = json.load(f)
    return data["groups"]


def check_images_exist():
    """Check if image files exist for all folios in groups."""
    groups = load_groups()
    image_dir = "data/scans/extracted"

    all_folios = set()
    for g in groups:
        all_folios.update(g["folio_ids"])

    print(f"\nImage File Check ({len(all_folios)} unique folios):")
    print("-" * 40)

    missing = []
    for folio in sorted(all_folios):
        path = os.path.join(image_dir, f"{folio}.png")
        if not os.path.exists(path):
            missing.append(folio)
            print(f"  MISSING: {path}")

    if missing:
        print(f"\nMissing images: {len(missing)}")
    else:
        print("  All images present!")

    return len(missing) == 0


def output_groups_for_ai():
    """Output group info for AI assessment."""
    groups = load_groups()

    print("\n" + "=" * 60)
    print("GROUPS FOR AI VISUAL ASSESSMENT")
    print("=" * 60)

    same_hub = [g for g in groups if g["group_type"] == "same_hub_type"]
    random_g = [g for g in groups if g["group_type"] == "random"]
    same_cat = [g for g in groups if g["group_type"] == "same_category"]

    print(f"\nSAME_HUB_TYPE groups: {len(same_hub)}")
    for i, g in enumerate(same_hub):
        print(f"  Group {i+1} ({g['group_basis']}): {g['folio_ids']}")

    print(f"\nRANDOM groups: {len(random_g)}")
    for i, g in enumerate(random_g):
        print(f"  Group {i+1}: {g['folio_ids']}")

    print(f"\nSAME_CATEGORY groups: {len(same_cat)}")
    for i, g in enumerate(same_cat):
        print(f"  Group {i+1} ({g['group_basis']}): {g['folio_ids']}")

    return groups


def main():
    """Run verification and output groups."""
    align_ok = verify_alignment()
    images_ok = check_images_exist()

    if align_ok and images_ok:
        output_groups_for_ai()
        print("\n" + "=" * 60)
        print("Ready for AI visual assessment")
        print("=" * 60)
    else:
        print("\nFix alignment/image issues before proceeding")


if __name__ == "__main__":
    main()
