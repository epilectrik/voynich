#!/usr/bin/env python3
"""
Configuration for Comparative Query-Driven Visual Annotation System.

Contains:
- Question templates for Mode A (single-image) and Mode B (comparative)
- Response options and feature definitions
- Grouping logic constants
- Response time weighting rules
- Folio metadata (heading, prefix, hub status, cluster)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import json
import os


# =============================================================================
# MODE A QUESTIONS (Single-Image, Forced-Choice)
# =============================================================================

QUESTIONS_MODE_A = {
    "leaf_shape_primary": {
        "question_id": "leaf_shape_primary",
        "template": "Which description best fits MOST of the leaves in this image (ignoring size and orientation)?",
        "options": [
            ("NEEDLE", "thin, elongated"),
            ("ROUND", "circular or nearly so"),
            ("LOBED", "divided into rounded sections"),
            ("COMPOUND", "multiple leaflets per leaf"),
            ("LANCEOLATE", "pointed oval"),
            ("SERRATED", "toothed edges"),
            ("MIXED", "multiple types present"),
            ("NO_LEAVES_VISIBLE", ""),
            ("UNSURE", "")
        ],
        "target_feature": "leaf_shape",
        "hypothesis_link": "ko-leaf",
        "mutual_exclusivity": True,
        "priority": "HIGH"
    },

    "root_type_primary": {
        "question_id": "root_type_primary",
        "template": "Which description best fits the root system shown (if visible)?",
        "options": [
            ("BRANCHING", "divides into smaller roots"),
            ("BULBOUS", "swollen, rounded mass"),
            ("FIBROUS", "many thin, hair-like roots"),
            ("SINGLE", "one main taproot"),
            ("NO_ROOT_VISIBLE", ""),
            ("UNSURE", "")
        ],
        "target_feature": "root_type",
        "hypothesis_link": "po-root",
        "mutual_exclusivity": True,
        "priority": "HIGH"
    },

    "root_visible": {
        "question_id": "root_visible",
        "template": "Is the root system clearly visible in this illustration?",
        "options": [
            ("YES", ""),
            ("NO", ""),
            ("UNSURE", "")
        ],
        "target_feature": "root_present",
        "hypothesis_link": None,
        "mutual_exclusivity": True,
        "priority": "MEDIUM"
    },

    "flower_present": {
        "question_id": "flower_present",
        "template": "Is there a clearly visible flower or flowering structure?",
        "options": [
            ("YES", ""),
            ("NO", ""),
            ("UNSURE", "")
        ],
        "target_feature": "flower_present",
        "hypothesis_link": None,
        "mutual_exclusivity": True,
        "priority": "MEDIUM"
    },

    "symmetry_type": {
        "question_id": "symmetry_type",
        "template": "What is the overall symmetry of the plant form?",
        "options": [
            ("RADIAL", "circular symmetry"),
            ("BILATERAL", "mirror symmetry"),
            ("ASYMMETRIC", "no clear symmetry"),
            ("UNSURE", "")
        ],
        "target_feature": "plant_symmetry",
        "hypothesis_link": "ok-symmetry",
        "mutual_exclusivity": True,
        "priority": "MEDIUM"
    },

    "complexity_exploratory": {
        "question_id": "complexity_exploratory",
        "template": "How many distinct plant parts (root, stem, leaves, flowers, fruits) are clearly depicted?",
        "options": [
            ("1-2", "simple"),
            ("3-4", "moderate"),
            ("5+", "complex"),
            ("UNSURE", "")
        ],
        "target_feature": "overall_complexity",
        "hypothesis_link": None,
        "mutual_exclusivity": True,
        "priority": "LOW",
        "analysis_status": "EXPLORATORY_ONLY"
    }
}


# =============================================================================
# MODE B QUESTIONS (Comparative, Multi-Image)
# =============================================================================

QUESTIONS_MODE_B = {
    "outlier_detection": {
        "question_id": "outlier_detection",
        "template": "Does one image clearly NOT belong with the others based on overall plant appearance?",
        "options": [
            ("NONE_STAND_OUT", "all similar"),
            ("A", "Image A is different"),
            ("B", "Image B is different"),
            ("C", "Image C is different"),
            ("D", "Image D is different"),
            ("E", "Image E is different"),
            ("F", "Image F is different"),
            ("CANNOT_TELL", "")
        ],
        "grouping_basis": "HIDDEN",
        "priority": "HIGHEST"
    },

    "compare_leaf_similarity": {
        "question_id": "compare_leaf_similarity",
        "template": "Ignoring size and orientation, do MOST of these plants share a similar leaf shape?",
        "options": [
            ("YES_CLEARLY", "very similar leaves"),
            ("YES_SOMEWHAT", "somewhat similar"),
            ("NO", "different leaf shapes"),
            ("MIXED", "some similar, some not"),
            ("CANNOT_TELL", "")
        ],
        "grouping_basis": "HIDDEN",
        "priority": "HIGH"
    },

    "compare_root_similarity": {
        "question_id": "compare_root_similarity",
        "template": "Ignoring size, do MOST of these plants share a similar root structure?",
        "options": [
            ("YES_CLEARLY", "very similar roots"),
            ("YES_SOMEWHAT", "somewhat similar"),
            ("NO", "different root structures"),
            ("MIXED", "some similar, some not"),
            ("NO_ROOTS_VISIBLE", ""),
            ("CANNOT_TELL", "")
        ],
        "grouping_basis": "HIDDEN",
        "priority": "HIGH"
    },

    "best_leaf_description": {
        "question_id": "best_leaf_description",
        "template": "Which description best applies to MOST of these images (ignoring size and orientation)?",
        "options": [
            ("narrow/needle-like leaves", ""),
            ("broad/round leaves", ""),
            ("lobed/divided leaves", ""),
            ("compound leaves (multiple leaflets)", ""),
            ("mixed leaf forms", ""),
            ("no consistent leaf feature", ""),
            ("CANNOT_TELL", "")
        ],
        "grouping_basis": "HIDDEN",
        "priority": "MEDIUM"
    },

    "most_similar_pair": {
        "question_id": "most_similar_pair",
        "template": "Which two images are most visually similar overall?",
        "options": [
            ("A-B", ""), ("A-C", ""), ("A-D", ""),
            ("B-C", ""), ("B-D", ""), ("C-D", ""),
            ("NONE_SIMILAR", ""),
            ("ALL_SIMILAR", ""),
            ("CANNOT_TELL", "")
        ],
        "grouping_basis": "HIDDEN",
        "priority": "MEDIUM"
    }
}


# =============================================================================
# GROUP TYPES FOR MODE B
# =============================================================================

class GroupType(Enum):
    # Hypothesis-driven groups
    SAME_CATEGORY = "same_category"       # All folios with same heading
    SAME_HUB_TYPE = "same_hub_type"       # Folios from same functional role
    SAME_PREFIX = "same_prefix"           # Folios with same dominant prefix
    SAME_CLUSTER = "same_cluster"         # Folios from same classifier cluster

    # Null groups
    RANDOM = "random"                     # Random selection
    STRATIFIED_RANDOM = "stratified_random"  # Random within constraints

    # Foil groups (quality control)
    KNOWN_DIFFERENT = "known_different"   # Mix from categories known to differ


# Group selection weights (probability distribution)
GROUP_WEIGHTS = {
    # Hypothesis-driven: 50%
    GroupType.SAME_CATEGORY: 0.20,
    GroupType.SAME_HUB_TYPE: 0.15,
    GroupType.SAME_PREFIX: 0.10,
    GroupType.SAME_CLUSTER: 0.05,

    # Null: 40%
    GroupType.RANDOM: 0.30,
    GroupType.STRATIFIED_RANDOM: 0.10,

    # Foil: 10%
    GroupType.KNOWN_DIFFERENT: 0.10
}


# =============================================================================
# RESPONSE TIME WEIGHTING
# =============================================================================

def get_response_weight(response_time_ms: int) -> Tuple[float, List[str]]:
    """
    Calculate response weight based on response time.

    Returns: (weight, list_of_flags)
    """
    flags = []

    if response_time_ms < 1000:
        weight = 0.25
        flags.append("RUSHED")
    elif response_time_ms < 2000:
        weight = 0.5
    elif response_time_ms <= 15000:
        weight = 1.0  # Optimal range
    elif response_time_ms <= 30000:
        weight = 0.75
    elif response_time_ms <= 60000:
        weight = 0.5
        flags.append("HESITANT")
    else:
        weight = 0.5
        flags.append("HESITANT")
        flags.append("REVIEW")

    return weight, flags


# =============================================================================
# SESSION PARAMETERS
# =============================================================================

SESSION_CONFIG = {
    "max_questions_per_session": 50,
    "break_suggestion_at": 25,
    "consecutive_flags_to_end": 3,
    "min_delay_between_questions_ms": 2000,

    # Duplicate check rates
    "mode_a_duplicate_rate": 0.10,  # 10%
    "mode_b_duplicate_rate": 0.05,  # 5%

    # Foil injection rate for Mode B
    "foil_injection_rate": 0.10,  # 10%
}


# =============================================================================
# AGGREGATION THRESHOLDS
# =============================================================================

AGGREGATION_CONFIG = {
    # Mode A agreement thresholds
    "clear_threshold": 0.60,      # >= 60% = CLEAR
    "weak_threshold": 0.50,       # 50-59% = WEAK
    # < 50% = AMBIGUOUS

    # Mode B cohesion thresholds
    "cohesion_significant": 0.70,
    "cohesion_suggestive": 0.55,

    # Null comparison
    "null_p_value_threshold": 0.05,
    "permutation_iterations": 10000,

    # Reliability thresholds
    "intra_annotator_acceptable": 0.75,
    "intra_annotator_good": 0.85,
}


# =============================================================================
# FOLIO METADATA
# =============================================================================

@dataclass
class FolioMetadata:
    folio_id: str
    heading: str
    opening_prefix: str
    hub_status: str  # 'hub', 'mid', 'isolate'
    in_degree: int
    classifier_cluster_k5: int
    image_path: str
    category_role: Optional[str] = None  # 'opener', 'closer', 'support' for hubs


def load_folio_metadata() -> Dict[str, FolioMetadata]:
    """
    Load and build comprehensive folio metadata from existing data files.
    """
    metadata = {}

    # Base path for extracted images
    image_dir = r"C:\git\voynich\data\scans\extracted"

    # Priority folio definitions with known properties
    # From h2_2_hub_singleton_contrast.json and c2_2_classifier_clusters.json

    # Hub categories
    # NOTE: f96r excluded - it's a text-only page (Recipes section), no plant illustration
    hub_folios = {
        "f58v": ("tol", "to", "hub", 34, 4, "opener"),    # k=5 cluster 4
        "f22r": ("pol", "po", "hub", 25, 5, "closer"),    # k=5 cluster 5
        # "f96r": EXCLUDED - text-only page, no plant
        "f58r": ("kor", "ko", "hub", 10, 3, "support"),   # k=5 cluster 3
        "f35v": ("par", "pa", "hub", 9, 1, "opener"),     # k=5 cluster 1
        "f42r": ("sho", "sh", "hub", 19, 1, "support"),    # k=5 cluster 1 - SUPPORT role
        "f10v": ("paiin", "pa", "hub", 7, 3, "opener"),   # k=5 cluster 3 - OPENER role
        "f19r": ("pchor", "pc", "hub", 7, 3, "opener"),   # k=5 cluster 3 - OPENER role
        "f21r": ("pchor", "pc", "hub", 7, 3, "opener"),   # k=5 cluster 3 - OPENER role
        "f52v": ("pchor", "pc", "hub", 7, 3, "opener"),   # k=5 cluster 3 - OPENER role
    }

    # Mid-tier categories
    mid_folios = {
        "f8r": ("pshol", "ps", "mid", 2, 1, None),
        "f44v": ("tsho", "ts", "mid", 2, 2, None),
    }

    # Multi-folio categories (isolates)
    multi_category_isolates = {
        "f2v": ("kooiin", "ko", "isolate", 0, 1, None),
        "f29v": ("kooiin", "ko", "isolate", 0, 1, None),
        "f5r": ("kshody", "ks", "isolate", 0, 3, None),
        "f37v": ("kshody", "ks", "isolate", 0, 3, None),
        "f15r": ("tshor", "ts", "isolate", 0, 2, None),
        "f53v": ("tshor", "ts", "isolate", 0, 2, None),
    }

    # Other pilot folios (isolates with available images)
    other_pilot = {
        "f38r": ("tolor", "to", "isolate", 0, 1, None),
        "f25r": ("told", "to", "isolate", 0, 4, None),
        "f11r": ("tshol", "ts", "isolate", 0, 3, None),
        "f11v": ("poldchody", "po", "isolate", 0, 3, None),
        "f5v": ("kocheor", "ko", "isolate", 0, 5, None),
        "f38v": ("koaiin", "ko", "isolate", 0, 1, None),
        "f36r": ("faiis", "fa", "isolate", 0, 1, None),
        "f30v": ("fshody", "fs", "isolate", 0, 3, None),
        "f22v": ("pcheodar", "pc", "mid", 2, 3, None),
        "f9v": ("psheot", "ps", "isolate", 0, 1, None),
        "f32v": ("podaiin", "po", "mid", 3, 3, None),
        "f17r": ("okchesy", "ok", "isolate", 0, 1, None),
        "f18r": ("cthscthain", "ct", "isolate", 0, 1, None),
        "f9r": ("pchocthy", "pc", "isolate", 0, 3, None),
        "f20v": ("pysaiinor", "py", "isolate", 0, 5, None),
        "f2r": ("kydainy", "ky", "isolate", 0, 3, None),
        "f47v": ("tchodar", "tc", "isolate", 0, 1, None),
        "f24v": ("tsheos", "ts", "isolate", 0, 3, None),
        "f56r": ("kcheodaiin", "kc", "isolate", 0, 3, None),
        "f49v": ("fcholdy", "fc", "isolate", 0, 3, None),
        "f51v": ("pdrairdy", "pd", "isolate", 0, 3, None),
        "f45v": ("tydlo", "ty", "isolate", 0, 1, None),
        "f3v": ("koaiin", "ko", "isolate", 0, 1, None),
        "f4v": ("pchooiin", "pc", "isolate", 0, 1, None),
        "f23v": ("otchal", "ot", "isolate", 0, 1, None),
    }

    # Combine all
    all_folios = {**hub_folios, **mid_folios, **multi_category_isolates, **other_pilot}

    for folio_id, (heading, prefix, status, in_deg, cluster, role) in all_folios.items():
        image_path = os.path.join(image_dir, f"{folio_id}.png")
        if os.path.exists(image_path):
            metadata[folio_id] = FolioMetadata(
                folio_id=folio_id,
                heading=heading,
                opening_prefix=prefix,
                hub_status=status,
                in_degree=in_deg,
                classifier_cluster_k5=cluster,
                image_path=image_path,
                category_role=role
            )

    return metadata


# =============================================================================
# CATEGORY GROUPINGS (for Mode B)
# =============================================================================

def get_category_to_folios() -> Dict[str, List[str]]:
    """Get mapping from heading/category to list of folio IDs."""
    metadata = load_folio_metadata()
    category_map = {}

    for folio_id, meta in metadata.items():
        if meta.heading not in category_map:
            category_map[meta.heading] = []
        category_map[meta.heading].append(folio_id)

    return category_map


def get_multi_folio_categories() -> Dict[str, List[str]]:
    """Get categories with 2+ folios available."""
    category_map = get_category_to_folios()
    return {cat: folios for cat, folios in category_map.items() if len(folios) >= 2}


def get_hub_categories() -> Dict[str, List[str]]:
    """Get hub categories with available folios."""
    metadata = load_folio_metadata()
    hub_map = {}

    for folio_id, meta in metadata.items():
        if meta.hub_status == "hub":
            if meta.heading not in hub_map:
                hub_map[meta.heading] = []
            hub_map[meta.heading].append(folio_id)

    return hub_map


def get_prefix_groups() -> Dict[str, List[str]]:
    """Get folios grouped by opening prefix."""
    metadata = load_folio_metadata()
    prefix_map = {}

    for folio_id, meta in metadata.items():
        if meta.opening_prefix not in prefix_map:
            prefix_map[meta.opening_prefix] = []
        prefix_map[meta.opening_prefix].append(folio_id)

    return prefix_map


def get_cluster_groups() -> Dict[int, List[str]]:
    """Get folios grouped by classifier cluster (k=5)."""
    metadata = load_folio_metadata()
    cluster_map = {}

    for folio_id, meta in metadata.items():
        cluster = meta.classifier_cluster_k5
        if cluster not in cluster_map:
            cluster_map[cluster] = []
        cluster_map[cluster].append(folio_id)

    return cluster_map


def get_foil_pairs() -> List[Tuple[str, str]]:
    """
    Identify category pairs that should be visually different.
    Uses maximum cluster distance at k=5.

    Returns list of (category_a, category_b) pairs for foil groups.
    """
    # Based on c2_2_classifier_clusters.json at k=5:
    # Cluster 1: tolor, koaiin, sho, tcho, etc. (broad morphological)
    # Cluster 5: pol, pysaiinor, korary, kocheor, fochor (ko-prefix heavy)

    # Pairs from maximally different clusters
    # NOTE: ("tor", "pchor") removed - tor (f96r) is text-only, no plant
    foil_pairs = [
        ("tol", "pol"),      # Cluster 4 vs 5
        ("sho", "fochor"),   # Cluster 1 vs 5
        ("par", "korary"),   # Cluster 1 vs 5
    ]

    return foil_pairs


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_all_available_folios() -> List[str]:
    """Get list of all folio IDs with available images."""
    return list(load_folio_metadata().keys())


def get_mode_a_questions() -> List[str]:
    """Get list of Mode A question IDs."""
    return list(QUESTIONS_MODE_A.keys())


def get_mode_b_questions() -> List[str]:
    """Get list of Mode B question IDs."""
    return list(QUESTIONS_MODE_B.keys())


if __name__ == "__main__":
    # Test loading
    print("Loading folio metadata...")
    metadata = load_folio_metadata()
    print(f"Loaded {len(metadata)} folios with images\n")

    print("Folio summary by hub status:")
    hub_count = sum(1 for m in metadata.values() if m.hub_status == 'hub')
    mid_count = sum(1 for m in metadata.values() if m.hub_status == 'mid')
    iso_count = sum(1 for m in metadata.values() if m.hub_status == 'isolate')
    print(f"  Hub: {hub_count}")
    print(f"  Mid: {mid_count}")
    print(f"  Isolate: {iso_count}\n")

    print("Multi-folio categories:")
    for cat, folios in get_multi_folio_categories().items():
        print(f"  {cat}: {folios}")

    print("\nHub categories:")
    for cat, folios in get_hub_categories().items():
        print(f"  {cat}: {folios}")

    print("\nPrefix groups (>= 2 folios):")
    for prefix, folios in get_prefix_groups().items():
        if len(folios) >= 2:
            print(f"  {prefix}: {len(folios)} folios")

    print("\nCluster groups (k=5):")
    for cluster, folios in sorted(get_cluster_groups().items()):
        print(f"  Cluster {cluster}: {len(folios)} folios")

    print("\nFoil pairs:")
    for pair in get_foil_pairs():
        print(f"  {pair}")
