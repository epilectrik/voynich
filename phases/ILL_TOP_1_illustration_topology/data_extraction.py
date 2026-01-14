#!/usr/bin/env python3
"""
ILL-TOP-1: Data Extraction for Visual-MIDDLE Correspondence Tests

Extracts per-folio MIDDLE and PREFIX distributions for the 29 visually-coded folios.

Data sources:
- phases/VIS_visual_analysis/visual_coding_complete.json - visual features
- phases/ANN_annotation_analysis/h3_2_visual_neighborhoods.json - visual clusters
- data/transcriptions/interlinear_full_words.txt - token data

Outputs:
- folio_middle_distributions.json - MIDDLE counts per folio
- folio_prefix_distributions.json - PREFIX counts per folio
- folio_metadata.json - section, Currier type, visual cluster, schematic score
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
VISUAL_CODING_FILE = BASE_PATH / "phases" / "VIS_visual_analysis" / "visual_coding_complete.json"
VISUAL_CLUSTERS_FILE = BASE_PATH / "phases" / "ANN_annotation_analysis" / "h3_2_visual_neighborhoods.json"
OUTPUT_DIR = Path(__file__).parent

# PREFIX definitions (from MIDDLE_INCOMPATIBILITY)
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# SUFFIX definitions
SUFFIXES = [
    'aiin', 'aiiin', 'ain', 'iin', 'in',
    'ar', 'or', 'al', 'ol', 'am', 'an',
    'dy', 'edy', 'eedy', 'chy', 'shy', 'ty', 'ky', 'ly', 'ry', 'y',
    'r', 'l', 's', 'd', 'n', 'm'
]

# Hub MIDDLEs (from SSD-PHY-1a)
HUB_MIDDLES = {'a', 'o', 'e', 'ee', 'eo'}


def decompose_token(token: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Decompose token into PREFIX, MIDDLE, SUFFIX.
    Returns (prefix, middle, suffix) - any can be None.
    """
    if not token or len(token) < 2:
        return None, None, None

    # Skip invalid tokens
    if token.startswith('[') or token.startswith('<') or '*' in token:
        return None, None, None

    # Find prefix (longest match first)
    prefix = None
    rest = token
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            rest = token[len(p):]
            break

    # Find suffix (longest match first)
    suffix = None
    middle = rest
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    # Middle must be non-empty
    if not middle:
        middle = None

    return prefix, middle, suffix


def load_visual_data():
    """Load visual coding and cluster data."""
    # Visual coding
    with open(VISUAL_CODING_FILE, 'r', encoding='utf-8') as f:
        visual_coding = json.load(f)

    # Visual clusters
    with open(VISUAL_CLUSTERS_FILE, 'r', encoding='utf-8') as f:
        visual_clusters = json.load(f)

    # Build folio -> cluster mapping
    folio_to_cluster = {}
    for cluster_id, folios in visual_clusters['visual_clusters'].items():
        for item in folios:
            folio_to_cluster[item['folio']] = int(cluster_id)

    return visual_coding, folio_to_cluster


def compute_schematic_score(visual_features: dict) -> int:
    """
    Compute schematic score from internal visual features only.

    Score = sum of:
    - 1 if overall_complexity == "SIMPLE"
    - 1 if plant_symmetry == "SYMMETRIC"
    - 1 if identifiable_impression == "NO"

    Higher score = more schematic/generic
    """
    score = 0

    if visual_features.get('overall_complexity') == 'SIMPLE':
        score += 1
    if visual_features.get('plant_symmetry') == 'SYMMETRIC':
        score += 1
    if visual_features.get('identifiable_impression') == 'NO':
        score += 1

    return score


def extract_folio_data(coded_folios: Set[str]):
    """
    Extract MIDDLE and PREFIX distributions for coded folios.
    """
    folio_middles = defaultdict(Counter)  # folio -> {middle: count}
    folio_prefixes = defaultdict(Counter)  # folio -> {prefix: count}
    folio_sections = {}  # folio -> section
    folio_currier = {}  # folio -> Currier type (A/B)
    folio_tokens = defaultdict(list)  # folio -> [tokens]

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Handle quoted column names
            word = row.get('"word"', row.get('word', '')).strip().strip('"')
            folio = row.get('"folio"', row.get('folio', '')).strip().strip('"')
            section = row.get('"section"', row.get('section', '')).strip().strip('"')
            language = row.get('"language"', row.get('language', '')).strip().strip('"')

            # Only coded folios
            if folio not in coded_folios:
                continue

            # Track metadata
            folio_sections[folio] = section
            folio_currier[folio] = language
            folio_tokens[folio].append(word)

            # Decompose token
            prefix, middle, suffix = decompose_token(word)

            if middle:
                folio_middles[folio][middle] += 1
            if prefix:
                folio_prefixes[folio][prefix] += 1

    return folio_middles, folio_prefixes, folio_sections, folio_currier, folio_tokens


def compute_hub_density(middle_counts: Counter) -> float:
    """
    Compute fraction of tokens using hub MIDDLEs.
    """
    total = sum(middle_counts.values())
    if total == 0:
        return 0.0

    hub_count = sum(middle_counts.get(m, 0) for m in HUB_MIDDLES)
    return hub_count / total


def main():
    print("ILL-TOP-1 Data Extraction")
    print("=" * 50)

    # Load visual data
    print("\n1. Loading visual data...")
    visual_coding, folio_to_cluster = load_visual_data()

    coded_folios = set(visual_coding['folios'].keys())
    print(f"   Coded folios: {len(coded_folios)}")
    print(f"   Visual clusters: {len(set(folio_to_cluster.values()))}")

    # Extract corpus data
    print("\n2. Extracting corpus data...")
    folio_middles, folio_prefixes, folio_sections, folio_currier, folio_tokens = extract_folio_data(coded_folios)

    # Build metadata
    print("\n3. Building metadata...")
    folio_metadata = {}

    for folio in coded_folios:
        visual_features = visual_coding['folios'][folio].get('visual_features', {})

        folio_metadata[folio] = {
            'section': folio_sections.get(folio, 'UNKNOWN'),
            'currier_type': folio_currier.get(folio, 'UNKNOWN'),
            'visual_cluster': folio_to_cluster.get(folio, -1),
            'schematic_score': compute_schematic_score(visual_features),
            'hub_density': compute_hub_density(folio_middles[folio]),
            'token_count': len(folio_tokens.get(folio, [])),
            'unique_middles': len(folio_middles[folio]),
            'unique_prefixes': len(folio_prefixes[folio]),
            # Visual features for reference
            'overall_complexity': visual_features.get('overall_complexity', 'UNKNOWN'),
            'plant_symmetry': visual_features.get('plant_symmetry', 'UNKNOWN'),
            'identifiable_impression': visual_features.get('identifiable_impression', 'UNKNOWN'),
        }

    # Print summary
    print("\n4. Summary statistics:")
    print(f"   Folios with corpus data: {len(folio_middles)}")
    print(f"   Total unique MIDDLEs across folios: {len(set().union(*[set(m.keys()) for m in folio_middles.values()]))}")

    # Currier type distribution
    currier_dist = Counter(m['currier_type'] for m in folio_metadata.values())
    print(f"   Currier distribution: {dict(currier_dist)}")

    # Section distribution
    section_dist = Counter(m['section'] for m in folio_metadata.values())
    print(f"   Section distribution: {dict(section_dist)}")

    # Visual cluster distribution
    cluster_dist = Counter(m['visual_cluster'] for m in folio_metadata.values())
    print(f"   Visual cluster distribution: {dict(cluster_dist)}")

    # Schematic score distribution
    schematic_dist = Counter(m['schematic_score'] for m in folio_metadata.values())
    print(f"   Schematic score distribution: {dict(schematic_dist)}")

    # Hub density stats
    hub_densities = [m['hub_density'] for m in folio_metadata.values()]
    if hub_densities:
        print(f"   Hub density: mean={sum(hub_densities)/len(hub_densities):.3f}, "
              f"min={min(hub_densities):.3f}, max={max(hub_densities):.3f}")

    # Save outputs
    print("\n5. Saving outputs...")

    # Convert Counter to dict for JSON
    folio_middles_json = {f: dict(m) for f, m in folio_middles.items()}
    folio_prefixes_json = {f: dict(p) for f, p in folio_prefixes.items()}

    with open(OUTPUT_DIR / 'folio_middle_distributions.json', 'w', encoding='utf-8') as f:
        json.dump(folio_middles_json, f, indent=2)
    print(f"   Saved folio_middle_distributions.json")

    with open(OUTPUT_DIR / 'folio_prefix_distributions.json', 'w', encoding='utf-8') as f:
        json.dump(folio_prefixes_json, f, indent=2)
    print(f"   Saved folio_prefix_distributions.json")

    with open(OUTPUT_DIR / 'folio_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(folio_metadata, f, indent=2)
    print(f"   Saved folio_metadata.json")

    print("\n" + "=" * 50)
    print("Data extraction complete.")

    return folio_middles_json, folio_prefixes_json, folio_metadata


if __name__ == '__main__':
    main()
