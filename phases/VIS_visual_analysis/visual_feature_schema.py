#!/usr/bin/env python3
"""
Phase 17, Task 3: Visual Feature Coding Schema

This script defines objective, reproducible coding schemas for visual features
of Voynich Manuscript illustrations. Features are coded WITHOUT semantic
interpretation - only observable visual properties.

Output: visual_feature_schema.json
"""

import json
from datetime import datetime

# =============================================================================
# PLANT FEATURE SCHEMA (Currier A Herbal Pages)
# =============================================================================

PLANT_FEATURE_SCHEMA = {
    'description': 'Objective coding schema for plant illustrations in Currier A herbal folios',

    'root': {
        'description': 'Root system features',
        'features': {
            'root_present': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if any root structure is visible below stem/soil line'
            },
            'root_type': {
                'type': 'categorical',
                'values': ['NONE', 'SINGLE', 'BRANCHING', 'BULBOUS', 'TUBEROUS', 'FIBROUS'],
                'coding_rules': {
                    'NONE': 'No root visible',
                    'SINGLE': 'Single unbranched root (taproot)',
                    'BRANCHING': 'Root divides into 2+ distinct branches',
                    'BULBOUS': 'Round swelling at root base (like onion)',
                    'TUBEROUS': 'Elongated swelling (like carrot/radish)',
                    'FIBROUS': 'Many thin roots of similar size'
                }
            },
            'root_prominence': {
                'type': 'ordinal',
                'values': ['SMALL', 'MEDIUM', 'LARGE'],
                'coding_rules': {
                    'SMALL': 'Root <20% of total plant height',
                    'MEDIUM': 'Root 20-40% of total plant height',
                    'LARGE': 'Root >40% of total plant height'
                }
            },
            'root_color_distinct': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if root is colored differently from stem'
            }
        }
    },

    'stem': {
        'description': 'Stem/stalk features',
        'features': {
            'stem_count': {
                'type': 'categorical',
                'values': ['1', '2', '3_PLUS'],
                'coding_rule': 'Count main stems emerging from root/base'
            },
            'stem_type': {
                'type': 'categorical',
                'values': ['STRAIGHT', 'CURVED', 'ZIGZAG', 'BRANCHING', 'CLIMBING'],
                'coding_rules': {
                    'STRAIGHT': 'Stem grows in straight line',
                    'CURVED': 'Stem has gradual curve',
                    'ZIGZAG': 'Stem changes direction sharply',
                    'BRANCHING': 'Main stem divides into branches',
                    'CLIMBING': 'Stem appears to wrap or climb'
                }
            },
            'stem_thickness': {
                'type': 'ordinal',
                'values': ['THIN', 'MEDIUM', 'THICK'],
                'coding_rules': {
                    'THIN': 'Line-like, minimal width',
                    'MEDIUM': 'Visible width, intermediate',
                    'THICK': 'Substantial width, trunk-like'
                }
            },
            'stem_nodes': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if stem shows visible joints/nodes'
            }
        }
    },

    'leaf': {
        'description': 'Leaf features',
        'features': {
            'leaf_present': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if any leaf structures visible'
            },
            'leaf_count_category': {
                'type': 'categorical',
                'values': ['NONE', 'FEW_1_5', 'MEDIUM_6_15', 'MANY_16_PLUS'],
                'coding_rule': 'Count distinct leaf structures'
            },
            'leaf_shape': {
                'type': 'categorical',
                'values': ['ROUND', 'OVAL', 'LANCEOLATE', 'HEART', 'LOBED', 'COMPOUND', 'SERRATED', 'PALMATE', 'NEEDLE', 'OTHER'],
                'coding_rules': {
                    'ROUND': 'Circular outline',
                    'OVAL': 'Elliptical outline',
                    'LANCEOLATE': 'Long and narrow, tapering',
                    'HEART': 'Heart-shaped (cordate)',
                    'LOBED': 'Deep indentations >25% into leaf',
                    'COMPOUND': 'Multiple distinct leaflets',
                    'SERRATED': 'Toothed/jagged margin',
                    'PALMATE': 'Fan-like, radiating segments',
                    'NEEDLE': 'Very thin, needle-like',
                    'OTHER': 'Does not fit above categories'
                }
            },
            'leaf_arrangement': {
                'type': 'categorical',
                'values': ['ALTERNATE', 'OPPOSITE', 'WHORLED', 'BASAL', 'RANDOM'],
                'coding_rules': {
                    'ALTERNATE': 'Single leaf at each node, alternating sides',
                    'OPPOSITE': 'Two leaves at each node, facing',
                    'WHORLED': 'Three+ leaves at each node',
                    'BASAL': 'Leaves emerge from base/ground level',
                    'RANDOM': 'No clear pattern'
                }
            },
            'leaf_color_variation': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if leaves show multiple colors/shading'
            }
        }
    },

    'flower': {
        'description': 'Flower/reproductive structure features',
        'features': {
            'flower_present': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if any flower/bud structures visible'
            },
            'flower_count': {
                'type': 'categorical',
                'values': ['NONE', '1', '2_5', '6_PLUS'],
                'coding_rule': 'Count distinct flower structures'
            },
            'flower_position': {
                'type': 'categorical',
                'values': ['TERMINAL', 'AXILLARY', 'THROUGHOUT', 'BASAL'],
                'coding_rules': {
                    'TERMINAL': 'At stem tips only',
                    'AXILLARY': 'In leaf axils (where leaf meets stem)',
                    'THROUGHOUT': 'Distributed along stem',
                    'BASAL': 'At base of plant'
                }
            },
            'flower_shape': {
                'type': 'categorical',
                'values': ['ROUND', 'STAR', 'TUBULAR', 'COMPOSITE', 'UMBEL', 'OTHER'],
                'coding_rules': {
                    'ROUND': 'Circular/radial symmetry',
                    'STAR': 'Star-shaped with distinct petals',
                    'TUBULAR': 'Tube or funnel shaped',
                    'COMPOSITE': 'Cluster of small flowers (like daisy center)',
                    'UMBEL': 'Umbrella-like cluster',
                    'OTHER': 'Does not fit above'
                }
            },
            'flower_color_distinct': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if flower colored differently from leaves'
            }
        }
    },

    'overall': {
        'description': 'Overall plant characteristics',
        'features': {
            'plant_count': {
                'type': 'categorical',
                'values': ['1', '2', '3_PLUS'],
                'coding_rule': 'Count distinct plants on folio'
            },
            'container_present': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if plant shown in pot/container'
            },
            'symmetry': {
                'type': 'categorical',
                'values': ['SYMMETRIC', 'ASYMMETRIC', 'PARTIAL'],
                'coding_rules': {
                    'SYMMETRIC': 'Left-right mirror symmetry',
                    'ASYMMETRIC': 'No apparent symmetry',
                    'PARTIAL': 'Some symmetric elements'
                }
            },
            'complexity': {
                'type': 'ordinal',
                'values': ['SIMPLE', 'MODERATE', 'COMPLEX'],
                'coding_rules': {
                    'SIMPLE': 'Few elements, clear structure',
                    'MODERATE': 'Multiple elements, organized',
                    'COMPLEX': 'Many elements, intricate detail'
                }
            },
            'artistic_style': {
                'type': 'categorical',
                'values': ['NATURALISTIC', 'STYLIZED', 'SCHEMATIC'],
                'coding_rules': {
                    'NATURALISTIC': 'Appears to represent real plant',
                    'STYLIZED': 'Decorative/artistic interpretation',
                    'SCHEMATIC': 'Diagram-like, abstract'
                }
            },
            'text_integration': {
                'type': 'categorical',
                'values': ['SEPARATE', 'WRAPPED', 'INTERSPERSED'],
                'coding_rules': {
                    'SEPARATE': 'Text in distinct block',
                    'WRAPPED': 'Text flows around plant',
                    'INTERSPERSED': 'Text mixed with plant elements'
                }
            }
        }
    }
}

# =============================================================================
# BIOLOGICAL SECTION SCHEMA (Currier B)
# =============================================================================

BIOLOGICAL_FEATURE_SCHEMA = {
    'description': 'Coding schema for biological/bathing section (Currier B)',

    'figures': {
        'description': 'Human figure features',
        'features': {
            'figure_count': {
                'type': 'categorical',
                'values': ['NONE', '1', '2_5', '6_15', '16_PLUS'],
                'coding_rule': 'Count distinct human figures'
            },
            'figure_arrangement': {
                'type': 'categorical',
                'values': ['LINEAR', 'CIRCULAR', 'SCATTERED', 'CLUSTERED', 'PAIRED'],
                'coding_rules': {
                    'LINEAR': 'Figures in line/row',
                    'CIRCULAR': 'Figures in circular arrangement',
                    'SCATTERED': 'No clear arrangement',
                    'CLUSTERED': 'Grouped together',
                    'PAIRED': 'In pairs'
                }
            },
            'figure_pose': {
                'type': 'categorical',
                'values': ['STANDING', 'SEATED', 'RECLINING', 'BATHING', 'MIXED'],
                'coding_rule': 'Predominant pose of figures'
            },
            'figure_connectivity': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if figures connected by lines/tubes'
            }
        }
    },

    'containers': {
        'description': 'Container/pool features',
        'features': {
            'pool_present': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if pool/tub visible'
            },
            'pool_count': {
                'type': 'categorical',
                'values': ['NONE', '1', '2_3', '4_PLUS'],
                'coding_rule': 'Count distinct pools'
            },
            'pool_shape': {
                'type': 'categorical',
                'values': ['ROUND', 'OVAL', 'RECTANGULAR', 'IRREGULAR'],
                'coding_rule': 'Predominant pool shape'
            },
            'pipe_present': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if pipes/tubes visible'
            },
            'pipe_network': {
                'type': 'categorical',
                'values': ['NONE', 'SIMPLE', 'BRANCHING', 'COMPLEX'],
                'coding_rules': {
                    'NONE': 'No pipes',
                    'SIMPLE': 'Single/few pipes',
                    'BRANCHING': 'Pipes with branches',
                    'COMPLEX': 'Intricate pipe network'
                }
            }
        }
    },

    'overall': {
        'description': 'Overall page characteristics',
        'features': {
            'layout_type': {
                'type': 'categorical',
                'values': ['SINGLE_SCENE', 'MULTI_PANEL', 'CONTINUOUS', 'SCHEMATIC'],
                'coding_rule': 'Overall page organization'
            },
            'text_presence': {
                'type': 'categorical',
                'values': ['NONE', 'MINIMAL', 'MODERATE', 'EXTENSIVE'],
                'coding_rule': 'Amount of text relative to illustration'
            }
        }
    }
}

# =============================================================================
# ZODIAC SECTION SCHEMA
# =============================================================================

ZODIAC_FEATURE_SCHEMA = {
    'description': 'Coding schema for zodiac/astronomical pages',

    'central_figure': {
        'description': 'Central medallion features',
        'features': {
            'central_type': {
                'type': 'categorical',
                'values': ['ANIMAL', 'HUMAN', 'SYMBOL', 'EMPTY', 'OTHER'],
                'coding_rule': 'Type of central figure'
            },
            'zodiac_identifiable': {
                'type': 'categorical',
                'values': ['YES_CLEAR', 'YES_POSSIBLE', 'NO', 'UNSURE'],
                'coding_rule': 'Can central figure be identified as zodiac sign?'
            }
        }
    },

    'surrounding_figures': {
        'description': 'Figures around central medallion',
        'features': {
            'surrounding_count': {
                'type': 'categorical',
                'values': ['NONE', '1_10', '11_20', '21_30', '31_PLUS'],
                'coding_rule': 'Count of surrounding figures'
            },
            'surrounding_type': {
                'type': 'categorical',
                'values': ['HUMAN', 'STAR', 'MIXED', 'OTHER'],
                'coding_rule': 'Predominant type of surrounding figures'
            },
            'radial_arrangement': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if figures arranged radially around center'
            }
        }
    },

    'overall': {
        'description': 'Overall page features',
        'features': {
            'circular_structure': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if dominant circular structure present'
            },
            'concentric_rings': {
                'type': 'categorical',
                'values': ['NONE', '1', '2', '3_PLUS'],
                'coding_rule': 'Count of concentric rings'
            },
            'star_symbols': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if star symbols present'
            },
            'text_in_rings': {
                'type': 'binary',
                'values': ['YES', 'NO'],
                'coding_rule': 'YES if text appears within ring structure'
            }
        }
    }
}

# =============================================================================
# CODING INSTRUCTIONS
# =============================================================================

CODING_INSTRUCTIONS = {
    'general_principles': [
        'Code ONLY what is visually observable - no interpretation',
        'Use UNSURE when feature is ambiguous',
        'Code the PREDOMINANT pattern when multiple exist',
        'Each folio should be coded independently',
        'Record coder ID and date for reproducibility'
    ],

    'decision_rules': {
        'lobed_vs_serrated': 'LOBED: indentations >25% into leaf. SERRATED: shallow teeth <25%',
        'branching_vs_fibrous': 'BRANCHING: distinct branches visible. FIBROUS: many similar thin roots',
        'naturalistic_vs_stylized': 'NATURALISTIC: proportions match real plants. STYLIZED: exaggerated/decorative',
        'simple_vs_complex': 'SIMPLE: <5 distinct elements. COMPLEX: >15 elements or intricate detail'
    },

    'inter_rater_reliability': {
        'recommended_process': [
            'Two independent coders code same folios',
            'Compare coding, resolve disagreements',
            'Calculate Cohen\'s kappa for each feature',
            'Target kappa > 0.7 for all features'
        ]
    }
}

# =============================================================================
# OUTPUT
# =============================================================================

def generate_schema():
    """Generate the complete visual feature schema."""

    schema = {
        'metadata': {
            'title': 'Voynich Manuscript Visual Feature Coding Schema',
            'version': '1.0',
            'date': datetime.now().isoformat(),
            'purpose': 'Objective coding of illustration features for text-image correlation analysis',
            'principles': [
                'No semantic interpretation - only observable features',
                'Reproducible coding with explicit decision rules',
                'Categorical/ordinal values for statistical analysis',
                'Section-specific schemas for different illustration types'
            ]
        },

        'schemas': {
            'plant_features': PLANT_FEATURE_SCHEMA,
            'biological_features': BIOLOGICAL_FEATURE_SCHEMA,
            'zodiac_features': ZODIAC_FEATURE_SCHEMA
        },

        'coding_instructions': CODING_INSTRUCTIONS,

        'feature_summary': {
            'plant_schema': {
                'total_features': sum(len(cat['features']) for cat in PLANT_FEATURE_SCHEMA.values() if 'features' in cat),
                'categories': list(PLANT_FEATURE_SCHEMA.keys())
            },
            'biological_schema': {
                'total_features': sum(len(cat['features']) for cat in BIOLOGICAL_FEATURE_SCHEMA.values() if 'features' in cat),
                'categories': list(BIOLOGICAL_FEATURE_SCHEMA.keys())
            },
            'zodiac_schema': {
                'total_features': sum(len(cat['features']) for cat in ZODIAC_FEATURE_SCHEMA.values() if 'features' in cat),
                'categories': list(ZODIAC_FEATURE_SCHEMA.keys())
            }
        },

        'usage': {
            'for_correlation_analysis': [
                'Code visual features for each folio',
                'Link to folio_feature_database.json',
                'Test correlations between text features and visual features',
                'Use chi-square/mutual information for statistical significance'
            ],
            'hypotheses_to_test': [
                'Do entries with bulbous roots have distinct vocabulary?',
                'Do flowering plants have different Part 3 vocabulary?',
                'Does plant complexity correlate with entry length?',
                'Do certain prefixes predict leaf shape?'
            ]
        }
    }

    return schema

def main():
    print("=" * 70)
    print("Phase 17, Task 3: Visual Feature Coding Schema")
    print("=" * 70)

    schema = generate_schema()

    # Save schema
    output_file = 'visual_feature_schema.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    print(f"\nSchema generated:")
    print(f"  Plant features: {schema['feature_summary']['plant_schema']['total_features']} features")
    print(f"  Biological features: {schema['feature_summary']['biological_schema']['total_features']} features")
    print(f"  Zodiac features: {schema['feature_summary']['zodiac_schema']['total_features']} features")
    print(f"\nResults saved to: {output_file}")

    # Print sample feature definitions
    print("\n" + "=" * 70)
    print("SAMPLE FEATURE DEFINITIONS (Plant Schema)")
    print("=" * 70)
    for category, data in list(PLANT_FEATURE_SCHEMA.items())[:3]:
        if 'features' in data:
            print(f"\n{category.upper()}:")
            for feature, spec in list(data['features'].items())[:2]:
                print(f"  - {feature}: {spec['values']}")

    return schema

if __name__ == '__main__':
    main()
