#!/usr/bin/env python3
"""
Data Recovery Phase, Task 3: Visual Data Join Infrastructure

Provides infrastructure for joining visual features to text features.
Includes tri-state coding, validation, and join operations.

Output: visual_data_template.csv, join functions for correlation analysis
"""

import csv
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter

# =============================================================================
# VISUAL FEATURE SCHEMA (28 Plant Features)
# =============================================================================

# Features use tri-state coding where applicable:
# - Feature values (categorical)
# - UNDETERMINED: Used when damage, ambiguity, or artistic style prevents determination

VISUAL_FEATURE_SCHEMA = {
    # Root features (4)
    'root_present': {
        'type': 'tri_state',
        'values': ['PRESENT', 'ABSENT', 'UNDETERMINED'],
        'description': 'Any root structure visible below stem/soil line'
    },
    'root_type': {
        'type': 'categorical',
        'values': ['NONE', 'SINGLE_TAPROOT', 'BRANCHING', 'BULBOUS', 'FIBROUS', 'UNDETERMINED'],
        'description': 'Root morphology type',
        'depends_on': {'root_present': 'PRESENT'}
    },
    'root_prominence': {
        'type': 'categorical',
        'values': ['SMALL', 'MEDIUM', 'LARGE', 'NA', 'UNDETERMINED'],
        'description': '<20% / 20-40% / >40% of plant height',
        'depends_on': {'root_present': 'PRESENT'}
    },
    'root_color_distinct': {
        'type': 'tri_state',
        'values': ['YES', 'NO', 'UNDETERMINED'],
        'description': 'Root colored differently from stem',
        'depends_on': {'root_present': 'PRESENT'}
    },

    # Stem features (4)
    'stem_count': {
        'type': 'categorical',
        'values': ['1', '2', '3_PLUS', 'UNDETERMINED'],
        'description': 'Number of main stems from root/base'
    },
    'stem_type': {
        'type': 'categorical',
        'values': ['STRAIGHT', 'CURVED', 'BRANCHING', 'TWINING', 'UNDETERMINED'],
        'description': 'Predominant stem pattern'
    },
    'stem_thickness': {
        'type': 'categorical',
        'values': ['THIN', 'MEDIUM', 'THICK', 'UNDETERMINED'],
        'description': 'Line-like / visible width / trunk-like'
    },
    'stem_color_distinct': {
        'type': 'tri_state',
        'values': ['YES', 'NO', 'UNDETERMINED'],
        'description': 'Stem differs from leaves in color'
    },

    # Leaf features (6)
    'leaf_present': {
        'type': 'tri_state',
        'values': ['PRESENT', 'ABSENT', 'UNDETERMINED'],
        'description': 'Any leaf structures visible'
    },
    'leaf_count_category': {
        'type': 'categorical',
        'values': ['NONE', 'FEW_1_5', 'MEDIUM_6_15', 'MANY_16_PLUS', 'UNDETERMINED'],
        'description': 'Count of distinct leaves',
        'depends_on': {'leaf_present': 'PRESENT'}
    },
    'leaf_shape': {
        'type': 'categorical',
        'values': ['ROUND', 'OVAL', 'LANCEOLATE', 'LOBED', 'COMPOUND', 'SERRATED', 'NEEDLE', 'MIXED', 'UNDETERMINED'],
        'description': 'Predominant leaf shape',
        'depends_on': {'leaf_present': 'PRESENT'}
    },
    'leaf_arrangement': {
        'type': 'categorical',
        'values': ['ALTERNATE', 'OPPOSITE', 'BASAL', 'WHORLED', 'SCATTERED', 'NA', 'UNDETERMINED'],
        'description': 'Leaf positioning pattern',
        'depends_on': {'leaf_present': 'PRESENT'}
    },
    'leaf_size_relative': {
        'type': 'categorical',
        'values': ['SMALL', 'MEDIUM', 'LARGE', 'MIXED', 'UNDETERMINED'],
        'description': 'Relative to overall plant',
        'depends_on': {'leaf_present': 'PRESENT'}
    },
    'leaf_color_uniform': {
        'type': 'tri_state',
        'values': ['YES', 'NO', 'UNDETERMINED'],
        'description': 'Single color vs multiple',
        'depends_on': {'leaf_present': 'PRESENT'}
    },

    # Flower features (5)
    'flower_present': {
        'type': 'tri_state',
        'values': ['PRESENT', 'ABSENT', 'UNDETERMINED'],
        'description': 'Any flower/bud visible'
    },
    'flower_count': {
        'type': 'categorical',
        'values': ['NONE', '1', '2_5', '6_PLUS', 'UNDETERMINED'],
        'description': 'Count of distinct flowers',
        'depends_on': {'flower_present': 'PRESENT'}
    },
    'flower_position': {
        'type': 'categorical',
        'values': ['NONE', 'TERMINAL', 'AXILLARY', 'THROUGHOUT', 'UNDETERMINED'],
        'description': 'Where flowers appear on plant',
        'depends_on': {'flower_present': 'PRESENT'}
    },
    'flower_color_distinct': {
        'type': 'tri_state',
        'values': ['YES', 'NO', 'UNDETERMINED'],
        'description': 'Flower differs from leaves in color',
        'depends_on': {'flower_present': 'PRESENT'}
    },
    'flower_shape': {
        'type': 'categorical',
        'values': ['NONE', 'SIMPLE', 'COMPOUND', 'RADIAL', 'IRREGULAR', 'UNDETERMINED'],
        'description': 'Flower structure type',
        'depends_on': {'flower_present': 'PRESENT'}
    },

    # Overall features (3)
    'plant_count': {
        'type': 'categorical',
        'values': ['1', '2', '3_PLUS', 'UNDETERMINED'],
        'description': 'Distinct plants on folio'
    },
    'container_present': {
        'type': 'tri_state',
        'values': ['PRESENT', 'ABSENT', 'UNDETERMINED'],
        'description': 'Plant in pot/container'
    },
    'plant_symmetry': {
        'type': 'categorical',
        'values': ['SYMMETRIC', 'ASYMMETRIC', 'UNDETERMINED'],
        'description': 'Left-right mirror symmetry'
    },

    # NOTE: Complexity features are EXCLUDED from correlation tests per protocol
    # but included for exploratory analysis
    'overall_complexity': {
        'type': 'categorical',
        'values': ['SIMPLE', 'MODERATE', 'COMPLEX', 'UNDETERMINED'],
        'description': '<5 / 5-15 / >15 distinct elements',
        'excluded_from_correlation': True,
        'exclusion_reason': 'Compound feature - not single visual dimension'
    },
    'identifiable_impression': {
        'type': 'categorical',
        'values': ['YES', 'NO', 'UNCERTAIN'],
        'description': 'Looks like a real plant',
        'excluded_from_correlation': True,
        'exclusion_reason': 'Subjective compound judgment'
    },
    'drawing_completeness': {
        'type': 'categorical',
        'values': ['COMPLETE', 'PARTIAL', 'FRAGMENTARY', 'UNDETERMINED'],
        'description': 'Drawing condition'
    }
}

# Features that should NOT be used in correlation tests
EXCLUDED_FROM_CORRELATION = [
    'overall_complexity',
    'identifiable_impression'
]

# Features that require tri-state (where UNDETERMINED vs ABSENT matters)
TRI_STATE_FEATURES = [
    'root_present', 'root_color_distinct',
    'stem_color_distinct',
    'leaf_present', 'leaf_color_uniform',
    'flower_present', 'flower_color_distinct',
    'container_present'
]

# Dependency rules for validation
DEPENDENCY_RULES = {
    'root_type': {'root_present': 'PRESENT'},
    'root_prominence': {'root_present': 'PRESENT'},
    'root_color_distinct': {'root_present': 'PRESENT'},
    'leaf_count_category': {'leaf_present': 'PRESENT'},
    'leaf_shape': {'leaf_present': 'PRESENT'},
    'leaf_arrangement': {'leaf_present': 'PRESENT'},
    'leaf_size_relative': {'leaf_present': 'PRESENT'},
    'leaf_color_uniform': {'leaf_present': 'PRESENT'},
    'flower_count': {'flower_present': 'PRESENT'},
    'flower_position': {'flower_present': 'PRESENT'},
    'flower_color_distinct': {'flower_present': 'PRESENT'},
    'flower_shape': {'flower_present': 'PRESENT'}
}


# =============================================================================
# DATA LOADING
# =============================================================================

def load_pilot_selection() -> List[str]:
    """Load the pilot folio selection."""
    with open('pilot_folio_selection.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['pilot_study_folios']


def load_pilot_text_features() -> Dict:
    """Load pilot folio text features."""
    with open('pilot_folio_text_features.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def load_visual_data(filepath: str = 'visual_coding_data.json') -> Optional[Dict]:
    """Load visual coding data if available."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


# =============================================================================
# TEMPLATE GENERATION
# =============================================================================

def generate_visual_template(pilot_folios: List[str], output_file: str = 'visual_data_template.csv'):
    """
    Generate CSV template for human visual coding.

    Each row is one folio. Each column is one visual feature.
    Includes coding instructions as header comments.
    """
    # Build feature list (28 features)
    feature_names = list(VISUAL_FEATURE_SCHEMA.keys())

    # CSV header row
    header = ['folio_id'] + feature_names + ['coder_notes']

    # Create instruction row (values for reference)
    instruction_row = ['INSTRUCTIONS:']
    for feat in feature_names:
        schema = VISUAL_FEATURE_SCHEMA[feat]
        values = schema['values']
        instruction_row.append('|'.join(values[:4]) + ('...' if len(values) > 4 else ''))
    instruction_row.append('Free text notes')

    # Create data rows (one per folio)
    rows = [header, instruction_row]

    for folio in pilot_folios:
        row = [folio] + [''] * len(feature_names) + ['']
        rows.append(row)

    # Write CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return output_file


def generate_coding_guide(output_file: str = 'visual_coding_guide.txt'):
    """Generate detailed coding guide as companion to template."""
    lines = [
        "=" * 70,
        "VISUAL CODING GUIDE FOR VOYNICH PILOT STUDY",
        "=" * 70,
        "",
        "This guide accompanies visual_data_template.csv",
        "Code each folio by entering values in the corresponding column.",
        "",
        "CRITICAL: Use UNDETERMINED when:",
        "  - Damage obscures the feature",
        "  - Artistic ambiguity prevents clear determination",
        "  - Feature falls between categories",
        "",
        "DO NOT use UNDETERMINED when:",
        "  - Feature is clearly absent (use ABSENT or NO)",
        "  - You're uncertain about identification (make best judgment)",
        "",
        "=" * 70,
        "FEATURE DEFINITIONS",
        "=" * 70,
        ""
    ]

    for feat, schema in VISUAL_FEATURE_SCHEMA.items():
        lines.append(f"--- {feat} ---")
        lines.append(f"Description: {schema['description']}")
        lines.append(f"Values: {', '.join(schema['values'])}")
        if schema.get('depends_on'):
            dep = schema['depends_on']
            dep_str = ', '.join(f"{k}={v}" for k, v in dep.items())
            lines.append(f"Only code if: {dep_str}")
        if schema.get('excluded_from_correlation'):
            lines.append(f"NOTE: {schema.get('exclusion_reason', 'Excluded from correlation tests')}")
        lines.append("")

    lines.extend([
        "=" * 70,
        "DECISION RULES",
        "=" * 70,
        "",
        "BRANCHING vs FIBROUS root:",
        "  BRANCHING: 2+ distinct thick branches",
        "  FIBROUS: Many thin similar roots",
        "",
        "LOBED vs COMPOUND leaf:",
        "  LOBED: Single leaf with deep indentations >25%",
        "  COMPOUND: Multiple distinct leaflets",
        "",
        "SERRATED vs LOBED:",
        "  SERRATED: Shallow teeth <25% into leaf",
        "  LOBED: Deep cuts >25%",
        "",
        "SIMPLE vs MODERATE complexity:",
        "  SIMPLE: <5 distinct elements",
        "  MODERATE: 5-15 elements",
        "  COMPLEX: >15 elements",
        "",
        "TERMINAL vs AXILLARY flower:",
        "  TERMINAL: At stem tips",
        "  AXILLARY: At leaf/stem junction",
        "",
        "=" * 70,
        "MANUSCRIPT ACCESS",
        "=" * 70,
        "",
        "Yale Digital Library: https://brbl-dl.library.yale.edu/vufind/Record/3519597",
        "Folio naming: 'f38r' = folio 38 recto, 'f38v' = folio 38 verso",
        "",
        "=" * 70
    ])

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return output_file


# =============================================================================
# VALIDATION
# =============================================================================

def validate_visual_data(visual_data: Dict) -> Dict:
    """
    Validate visual coding data for completeness and consistency.

    Returns validation report with issues and warnings.
    """
    issues = []
    warnings = []
    valid_count = 0
    invalid_count = 0

    for folio_id, features in visual_data.items():
        folio_issues = []

        # Check all required fields present
        for feat in VISUAL_FEATURE_SCHEMA.keys():
            if feat not in features:
                folio_issues.append(f"Missing field: {feat}")
            else:
                value = features[feat]
                schema = VISUAL_FEATURE_SCHEMA[feat]
                valid_values = schema['values']

                # Check value is valid
                if value and value not in valid_values:
                    folio_issues.append(f"Invalid value for {feat}: '{value}' (valid: {valid_values})")

        # Check dependency rules
        for dependent, requires in DEPENDENCY_RULES.items():
            if dependent in features and features.get(dependent):
                for req_field, req_value in requires.items():
                    actual = features.get(req_field)
                    if actual != req_value:
                        folio_issues.append(
                            f"Dependency violation: {dependent} requires {req_field}={req_value}, got {actual}"
                        )

        # Check impossible combinations
        # Example: flower_count > NONE but flower_present = ABSENT
        if features.get('flower_present') == 'ABSENT' and features.get('flower_count') not in ['NONE', '', None]:
            folio_issues.append("Impossible: flower_count specified but flower_present=ABSENT")

        if features.get('root_present') == 'ABSENT' and features.get('root_type') not in ['NONE', '', None]:
            folio_issues.append("Impossible: root_type specified but root_present=ABSENT")

        if features.get('leaf_present') == 'ABSENT' and features.get('leaf_shape') not in ['', None]:
            folio_issues.append("Impossible: leaf_shape specified but leaf_present=ABSENT")

        if folio_issues:
            issues.append({'folio': folio_id, 'issues': folio_issues})
            invalid_count += 1
        else:
            valid_count += 1

    # Calculate UNDETERMINED rates
    undetermined_rates = {}
    for feat in VISUAL_FEATURE_SCHEMA.keys():
        values = [visual_data[f].get(feat) for f in visual_data]
        undet_count = sum(1 for v in values if v == 'UNDETERMINED')
        rate = undet_count / len(values) if values else 0
        undetermined_rates[feat] = round(rate, 3)

        if rate > 0.3:
            warnings.append(f"HIGH UNDETERMINED rate for {feat}: {rate:.1%} (reduces statistical power)")

    return {
        'valid': len(issues) == 0,
        'valid_count': valid_count,
        'invalid_count': invalid_count,
        'issues': issues,
        'warnings': warnings,
        'undetermined_rates': undetermined_rates,
        'high_undetermined_features': [f for f, r in undetermined_rates.items() if r > 0.3]
    }


# =============================================================================
# JOIN OPERATIONS
# =============================================================================

def join_visual_text(visual_data: Dict, text_data: Dict, exclude_undetermined: bool = True) -> Dict:
    """
    Join visual features to text features on folio_id.

    Args:
        visual_data: Dict of {folio_id: {feature: value}}
        text_data: Dict containing 'pilot_folios' with text features
        exclude_undetermined: If True, UNDETERMINED values become None (excluded from tests)

    Returns:
        Merged dataset ready for correlation analysis
    """
    pilot_folios = text_data.get('pilot_folios', {})
    merged = {}

    for folio_id in pilot_folios.keys():
        if folio_id not in visual_data:
            continue

        visual = visual_data[folio_id]
        text = pilot_folios[folio_id]

        # Process visual features
        processed_visual = {}
        for feat, value in visual.items():
            if exclude_undetermined and value == 'UNDETERMINED':
                processed_visual[feat] = None  # Will be excluded from tests
            else:
                processed_visual[feat] = value

        merged[folio_id] = {
            'folio_id': folio_id,
            'text_features': text,
            'visual_features': processed_visual,
            'has_visual': True
        }

    return merged


def get_correlation_pairs(merged_data: Dict) -> List[Tuple[str, str]]:
    """
    Get all valid (visual_feature, text_feature) pairs for correlation testing.

    Excludes:
    - Features in EXCLUDED_FROM_CORRELATION
    - Features with >30% UNDETERMINED rate
    """
    # Get visual features (excluding compound features)
    visual_features = [
        f for f in VISUAL_FEATURE_SCHEMA.keys()
        if f not in EXCLUDED_FROM_CORRELATION
    ]

    # Calculate UNDETERMINED rates
    undetermined_rates = {}
    for feat in visual_features:
        values = [merged_data[f]['visual_features'].get(feat) for f in merged_data]
        none_count = sum(1 for v in values if v is None)
        rate = none_count / len(values) if values else 0
        undetermined_rates[feat] = rate

    # Filter out high-undetermined features
    valid_visual = [f for f in visual_features if undetermined_rates.get(f, 0) <= 0.3]

    # Text features for correlation
    text_features = [
        'word_count', 'unique_word_count', 'vocabulary_richness',
        'part1_dominant_prefix', 'part2_dominant_prefix', 'part3_dominant_prefix',
        'prefix_diversity', 'heading_prefix', 'heading_length'
    ]

    # Generate pairs
    pairs = []
    for v in valid_visual:
        for t in text_features:
            pairs.append((v, t))

    return pairs


def extract_feature_vectors(merged_data: Dict, visual_feature: str, text_feature: str) -> Tuple[List, List, List]:
    """
    Extract paired feature vectors for correlation testing.

    Returns: (visual_values, text_values, folio_ids)
    Only includes pairs where both values are non-None.
    """
    visual_values = []
    text_values = []
    folio_ids = []

    for folio_id, data in merged_data.items():
        v_val = data['visual_features'].get(visual_feature)
        t_val = data['text_features'].get(text_feature)

        if v_val is not None and t_val is not None:
            visual_values.append(v_val)
            text_values.append(t_val)
            folio_ids.append(folio_id)

    return visual_values, text_values, folio_ids


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Data Recovery Phase, Task 3: Visual Data Join Infrastructure")
    print("=" * 70)

    # Load pilot selection
    print("\n[1/4] Loading pilot folio selection...")
    pilot_folios = load_pilot_selection()
    print(f"  {len(pilot_folios)} pilot folios")

    # Generate template
    print("\n[2/4] Generating visual coding template...")
    template_file = generate_visual_template(pilot_folios)
    print(f"  Created: {template_file}")

    # Generate coding guide
    print("\n[3/4] Generating coding guide...")
    guide_file = generate_coding_guide()
    print(f"  Created: {guide_file}")

    # Check if visual data exists
    print("\n[4/4] Checking for existing visual data...")
    visual_data = load_visual_data()

    if visual_data:
        print(f"  Found visual data for {len(visual_data)} folios")
        validation = validate_visual_data(visual_data)
        print(f"  Validation: {validation['valid_count']} valid, {validation['invalid_count']} invalid")
        if validation['warnings']:
            print(f"  Warnings: {len(validation['warnings'])}")
    else:
        print("  No visual data found (visual_coding_data.json)")
        print("  Template ready for manual coding")
        validation = None

    # Save schema documentation
    schema_doc = {
        'metadata': {
            'title': 'Visual Feature Schema for Pilot Study',
            'phase': 'Data Recovery Phase, Task 3',
            'date': datetime.now().isoformat(),
            'feature_count': len(VISUAL_FEATURE_SCHEMA),
            'excluded_from_correlation': EXCLUDED_FROM_CORRELATION
        },
        'features': VISUAL_FEATURE_SCHEMA,
        'tri_state_features': TRI_STATE_FEATURES,
        'dependency_rules': DEPENDENCY_RULES,
        'validation_status': validation
    }

    with open('visual_join_schema.json', 'w', encoding='utf-8') as f:
        json.dump(schema_doc, f, indent=2)
    print(f"\n  Saved schema to: visual_join_schema.json")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nFiles created:")
    print(f"  1. {template_file} - CSV template for manual coding")
    print(f"  2. {guide_file} - Detailed coding instructions")
    print(f"  3. visual_join_schema.json - Feature schema documentation")
    print(f"\nFeatures: {len(VISUAL_FEATURE_SCHEMA)} total")
    print(f"  - Tri-state features: {len(TRI_STATE_FEATURES)}")
    print(f"  - Excluded from correlation: {len(EXCLUDED_FROM_CORRELATION)}")
    print(f"  - Valid for correlation: {len(VISUAL_FEATURE_SCHEMA) - len(EXCLUDED_FROM_CORRELATION)}")
    print(f"\nNext step: Complete visual coding, save as visual_coding_data.json")

    return schema_doc


if __name__ == '__main__':
    main()
