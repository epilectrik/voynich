#!/usr/bin/env python3
"""
Compile hub folio visual features for feature discrimination analysis.

Workstream 2: Identify which visual features distinguish functional roles.
"""

import json
from collections import defaultdict
from datetime import datetime
from annotation_config import load_folio_metadata

# Visual features to analyze
VISUAL_FEATURES = [
    "root_present", "root_type", "root_prominence",
    "stem_count", "stem_type", "stem_thickness",
    "leaf_present", "leaf_count_category", "leaf_shape", "leaf_arrangement", "leaf_size_relative",
    "flower_present", "flower_count", "flower_position", "flower_shape",
    "plant_symmetry", "overall_complexity"
]


def load_visual_coding():
    """Load visual coding data."""
    with open("visual_coding_complete.json") as f:
        return json.load(f)


def get_hub_folios_by_role():
    """Get hub folios organized by functional role."""
    metadata = load_folio_metadata()
    roles = {"opener": [], "closer": [], "support": []}

    for folio_id, meta in metadata.items():
        if meta.hub_status == "hub" and meta.category_role:
            roles[meta.category_role].append({
                "folio_id": folio_id,
                "heading": meta.heading,
                "prefix": meta.opening_prefix
            })

    return roles


def extract_hub_features(visual_coding, roles):
    """Extract visual features for each hub folio."""
    hub_features = {}
    missing_visual = []

    for role, folios in roles.items():
        for folio_info in folios:
            folio_id = folio_info["folio_id"]

            if folio_id in visual_coding.get("folios", {}):
                folio_data = visual_coding["folios"][folio_id]
                features = folio_data.get("visual_features", {})

                hub_features[folio_id] = {
                    "role": role,
                    "heading": folio_info["heading"],
                    "prefix": folio_info["prefix"],
                    "features": {k: features.get(k, "UNKNOWN") for k in VISUAL_FEATURES},
                    "has_visual_coding": True
                }
            else:
                missing_visual.append(folio_id)
                hub_features[folio_id] = {
                    "role": role,
                    "heading": folio_info["heading"],
                    "prefix": folio_info["prefix"],
                    "features": {},
                    "has_visual_coding": False
                }

    return hub_features, missing_visual


def aggregate_by_role(hub_features):
    """Aggregate features by functional role."""
    role_profiles = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    role_counts = defaultdict(int)

    for folio_id, data in hub_features.items():
        if not data["has_visual_coding"]:
            continue

        role = data["role"]
        role_counts[role] += 1

        for feature, value in data["features"].items():
            role_profiles[role][feature][value] += 1

    # Compute mode and agreement for each feature
    aggregated = {}
    for role in ["opener", "closer", "support"]:
        aggregated[role] = {
            "folio_count": role_counts[role],
            "features": {}
        }

        for feature in VISUAL_FEATURES:
            if role in role_profiles and feature in role_profiles[role]:
                value_counts = role_profiles[role][feature]
                total = sum(value_counts.values())

                if total > 0:
                    mode_value = max(value_counts, key=value_counts.get)
                    mode_count = value_counts[mode_value]
                    agreement = mode_count / total

                    aggregated[role]["features"][feature] = {
                        "mode": mode_value,
                        "agreement": round(agreement, 3),
                        "distribution": dict(value_counts)
                    }
                else:
                    aggregated[role]["features"][feature] = {
                        "mode": None,
                        "agreement": 0,
                        "distribution": {}
                    }
            else:
                aggregated[role]["features"][feature] = {
                    "mode": None,
                    "agreement": 0,
                    "distribution": {}
                }

    return aggregated


def compute_feature_discrimination(hub_features):
    """
    Compute discrimination power for each feature.

    Higher discrimination = more useful for distinguishing roles.
    """
    discrimination = {}

    for feature in VISUAL_FEATURES:
        # Build contingency table: feature_value x role
        contingency = defaultdict(lambda: defaultdict(int))
        role_totals = defaultdict(int)

        for folio_id, data in hub_features.items():
            if not data["has_visual_coding"]:
                continue

            role = data["role"]
            value = data["features"].get(feature, "UNKNOWN")

            contingency[value][role] += 1
            role_totals[role] += 1

        # Compute discrimination score (variance across roles)
        # For each feature value, check if it's concentrated in one role
        total_folios = sum(role_totals.values())

        if total_folios == 0:
            discrimination[feature] = {
                "score": 0,
                "status": "NO_DATA",
                "contingency": {}
            }
            continue

        # Simple discrimination: max relative difference between roles
        role_dominant_values = {}
        max_diff = 0

        for value, role_counts in contingency.items():
            if value in ["UNKNOWN", "NA", "NONE"]:
                continue

            value_total = sum(role_counts.values())
            if value_total == 0:
                continue

            for role, count in role_counts.items():
                # Proportion of this value that appears in this role
                prop = count / value_total
                if prop > 0.6:  # Threshold for "dominance"
                    role_dominant_values[value] = role
                    max_diff = max(max_diff, prop)

        discrimination[feature] = {
            "score": round(max_diff, 3),
            "role_dominant_values": role_dominant_values,
            "contingency": {v: dict(r) for v, r in contingency.items()}
        }

    # Rank features by discrimination score
    ranked = sorted(discrimination.items(), key=lambda x: x[1]["score"], reverse=True)

    return {
        "ranked_features": [
            {"rank": i+1, "feature": f, **d}
            for i, (f, d) in enumerate(ranked)
        ],
        "by_feature": discrimination
    }


def main():
    """Compile hub folio features for discrimination analysis."""
    print("=" * 60)
    print("HUB FOLIO FEATURE COMPILATION")
    print("=" * 60)

    # Load data
    visual_coding = load_visual_coding()
    roles = get_hub_folios_by_role()

    print("\nHub folios by role:")
    for role, folios in roles.items():
        folio_ids = [f["folio_id"] for f in folios]
        print(f"  {role.upper()}: {folio_ids}")

    # Extract features
    hub_features, missing = extract_hub_features(visual_coding, roles)

    print(f"\nVisual coding status:")
    coded = [f for f, d in hub_features.items() if d["has_visual_coding"]]
    print(f"  With visual coding: {coded}")
    print(f"  Missing visual coding: {missing}")

    # Aggregate by role
    role_profiles = aggregate_by_role(hub_features)

    print("\nRole feature profiles:")
    for role, data in role_profiles.items():
        print(f"  {role.upper()} (N={data['folio_count']}):")
        for feature, stats in list(data["features"].items())[:3]:
            print(f"    {feature}: mode={stats['mode']} (agreement={stats['agreement']})")

    # Compute discrimination
    discrimination = compute_feature_discrimination(hub_features)

    print("\nTop discriminating features:")
    for item in discrimination["ranked_features"][:5]:
        print(f"  #{item['rank']} {item['feature']}: score={item['score']}")

    # Output
    output = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "visual_features_analyzed": len(VISUAL_FEATURES),
            "hub_folios_total": len(hub_features),
            "hub_folios_with_visual_coding": len(coded),
            "hub_folios_missing_visual_coding": missing
        },
        "hub_folio_features": hub_features,
        "role_feature_profiles": role_profiles,
        "feature_discrimination": discrimination,
        "priority_coding_needed": missing
    }

    output_path = "hub_features_compiled.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Output saved to: {output_path}")
    print(f"{'=' * 60}")

    if missing:
        print(f"\n** WARNING: {len(missing)} hub folios need visual coding **")
        print(f"   Priority: {missing}")

    return output


if __name__ == "__main__":
    main()
