"""Two-Layer Model Formal Specification for Voynich Manuscript.

This document formalizes our understanding of the Voynich encoding system:
- Layer 1 (Shorthand): Compositional medical notation
- Layer 2 (Cipher): Character substitution obscuring the shorthand

This serves as the reference decoder specification.
"""
import sys
import json
from datetime import datetime
from collections import defaultdict, Counter

sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus

# =============================================================================
# LAYER 1: SHORTHAND SYSTEM - COMPOSITIONAL MEDICAL NOTATION
# =============================================================================

# PREFIX MAPPINGS - Semantic domain markers
# Confidence: HIGH = validated by section enrichment + propagation
#             MEDIUM = section enrichment but limited propagation
#             LOW = inferred from context only
#             SPECULATIVE = best guess, needs validation

PREFIX_MAPPINGS = {
    # BODY domain - enriched in BIOLOGICAL section
    'qo': {
        'category': 'BODY',
        'meaning': 'womb/uterus',
        'latin': 'matrix/uterus',
        'confidence': 'HIGH',
        'evidence': 'BIOLOGICAL 2.60x enrichment, propagates to HERBAL/RECIPES',
        'alternatives': ['internal cavity', 'receptacle']
    },
    'ol': {
        'category': 'BODY',
        'meaning': 'menstrual flow',
        'latin': 'menstruum/fluxus',
        'confidence': 'MEDIUM',
        'evidence': 'BIOLOGICAL 2.1x enrichment',
        'alternatives': ['bodily fluid', 'humor']
    },
    'so': {
        'category': 'BODY',
        'meaning': 'health/healing',
        'latin': 'salus',
        'confidence': 'MEDIUM',
        'evidence': 'HERBAL co-occurrence with plant terms',
        'alternatives': ['state', 'condition']
    },
    'pc': {
        'category': 'BODY',
        'meaning': 'chest/pectoral',
        'latin': 'pectus',
        'confidence': 'LOW',
        'evidence': 'Phonetic similarity to Latin',
        'alternatives': ['vessel', 'container']
    },

    # PLANT domain - enriched in HERBAL section
    'ch': {
        'category': 'PLANT',
        'meaning': 'herb/plant',
        'latin': 'herba',
        'confidence': 'HIGH',
        'evidence': 'HERBAL section dominant (57%+)',
        'alternatives': ['material', 'substance']
    },
    'sh': {
        'category': 'PLANT',
        'meaning': 'juice/sap',
        'latin': 'succus',
        'confidence': 'HIGH',
        'evidence': 'Liquid context, HERBAL enriched',
        'alternatives': ['extract', 'essence']
    },
    'da': {
        'category': 'PLANT',
        'meaning': 'leaf',
        'latin': 'folium',
        'confidence': 'HIGH',
        'evidence': 'HERBAL 1.5x enrichment',
        'alternatives': ['green part', 'foliage']
    },
    'sa': {
        'category': 'PLANT',
        'meaning': 'seed',
        'latin': 'semen',
        'confidence': 'MEDIUM',
        'evidence': 'Context inference',
        'alternatives': ['small part', 'grain']
    },

    # TIME domain - enriched in ZODIAC section
    'ot': {
        'category': 'TIME',
        'meaning': 'time/season',
        'latin': 'tempus',
        'confidence': 'HIGH',
        'evidence': 'ZODIAC 2.4x enrichment',
        'alternatives': ['cycle', 'period']
    },
    'ok': {
        'category': 'TIME',
        'meaning': 'sky/celestial',
        'latin': 'caelum',
        'confidence': 'MEDIUM',
        'evidence': 'ZODIAC 1.9x enrichment',
        'alternatives': ['sequence', 'order']
    },
    'yk': {
        'category': 'TIME',
        'meaning': 'cycle',
        'latin': 'cyclus',
        'confidence': 'MEDIUM',
        'evidence': 'ZODIAC enriched',
        'alternatives': ['return', 'repetition']
    },

    # CELESTIAL domain - enriched in ZODIAC/COSMOLOGICAL
    'al': {
        'category': 'CELESTIAL',
        'meaning': 'star',
        'latin': 'stella',
        'confidence': 'MEDIUM',
        'evidence': 'ZODIAC 3.7x enrichment',
        'alternatives': ['light', 'point']
    },
    'ar': {
        'category': 'CELESTIAL',
        'meaning': 'air',
        'latin': 'aer',
        'confidence': 'MEDIUM',
        'evidence': 'ZODIAC 2.0x enrichment',
        'alternatives': ['breath', 'spirit']
    },
    'or': {
        'category': 'CELESTIAL',
        'meaning': 'gold/sun',
        'latin': 'aurum/sol',
        'confidence': 'LOW',
        'evidence': 'COSMOLOGICAL enriched',
        'alternatives': ['benefit', 'value']
    },
    'yt': {
        'category': 'CELESTIAL',
        'meaning': 'world',
        'latin': 'mundus',
        'confidence': 'LOW',
        'evidence': 'COSMOLOGICAL 3.1x enrichment',
        'alternatives': ['realm', 'sphere']
    },

    # LIQUID domain - enriched in HERBAL (preparations)
    'ct': {
        'category': 'LIQUID',
        'meaning': 'water',
        'latin': 'aqua',
        'confidence': 'HIGH',
        'evidence': 'HERBAL 2.4x enrichment',
        'alternatives': ['dilution medium']
    },
    'cth': {
        'category': 'LIQUID',
        'meaning': 'purified water',
        'latin': 'aqua pura',
        'confidence': 'MEDIUM',
        'evidence': 'Water-related prefix variant',
        'alternatives': ['cleansing liquid']
    },
    'lk': {
        'category': 'LIQUID',
        'meaning': 'liquid/liquor',
        'latin': 'liquor',
        'confidence': 'MEDIUM',
        'evidence': 'RECIPES 2.8x enrichment',
        'alternatives': ['solution', 'mixture']
    },
}

# MIDDLE ELEMENT MAPPINGS - Process/action/state markers
# These include gallows characters (tall letters) and non-gallows middles

MIDDLE_MAPPINGS = {
    # GALLOWS - Pharmaceutical process verbs (HIGH confidence group)
    'lch': {
        'category': 'PROCESS',
        'meaning': 'wash/cleanse',
        'latin': 'lavare',
        'confidence': 'HIGH',
        'evidence': 'BIOLOGICAL 2.01x (bathing procedures)',
        'alternatives': ['prepare wet']
    },
    'lche': {
        'category': 'PROCESS',
        'meaning': 'wash/cleanse',
        'latin': 'lavare',
        'confidence': 'HIGH',
        'evidence': 'BIOLOGICAL 2.31x enrichment',
        'alternatives': ['rinse thoroughly']
    },
    'cth': {
        'category': 'PROCESS',
        'meaning': 'purify',
        'latin': 'purificare',
        'confidence': 'MEDIUM',
        'evidence': 'RECIPES 1.96x, HERBAL 53%',
        'alternatives': ['dilute', 'thin']
    },
    'tch': {
        'category': 'PROCESS',
        'meaning': 'prepare/treat',
        'latin': 'praeparare',
        'confidence': 'MEDIUM',
        'evidence': 'HERBAL 1.74x (63%)',
        'alternatives': ['process generic']
    },
    'tche': {
        'category': 'PROCESS',
        'meaning': 'prepare/treat',
        'latin': 'praeparare',
        'confidence': 'MEDIUM',
        'evidence': 'HERBAL 1.53x',
        'alternatives': ['process']
    },
    'ckh': {
        'category': 'PROCESS',
        'meaning': 'process/work',
        'latin': 'laborare',
        'confidence': 'MEDIUM',
        'evidence': 'RECIPES 2.26x (42%)',
        'alternatives': ['transform']
    },
    'ckhe': {
        'category': 'PROCESS',
        'meaning': 'treated',
        'latin': 'tractare',
        'confidence': 'MEDIUM',
        'evidence': 'RECIPES 2.09x',
        'alternatives': ['worked']
    },
    'kch': {
        'category': 'PROCESS',
        'meaning': 'potent/strengthen',
        'latin': 'potens',
        'confidence': 'LOW',
        'evidence': 'HERBAL 1.54x (57%)',
        'alternatives': ['intensify']
    },
    'kche': {
        'category': 'PROCESS',
        'meaning': 'potent',
        'latin': 'potens',
        'confidence': 'LOW',
        'evidence': 'HERBAL 1.44x',
        'alternatives': ['strong']
    },
    'pch': {
        'category': 'PROCESS',
        'meaning': 'apply (to body)',
        'latin': 'applicare',
        'confidence': 'MEDIUM',
        'evidence': 'Often followed by BODY terms',
        'alternatives': ['administer']
    },
    'pche': {
        'category': 'PROCESS',
        'meaning': 'apply',
        'latin': 'applicare',
        'confidence': 'MEDIUM',
        'evidence': 'Body application context',
        'alternatives': ['place on']
    },
    'dch': {
        'category': 'PROCESS',
        'meaning': 'grind/crush',
        'latin': 'terere',
        'confidence': 'LOW',
        'evidence': 'HERBAL 1.60x, appears with plant terms',
        'alternatives': ['break down']
    },
    'sch': {
        'category': 'PROCESS',
        'meaning': 'processed',
        'latin': 'conficere',
        'confidence': 'LOW',
        'evidence': 'General processing context',
        'alternatives': ['finished']
    },
    'fch': {
        'category': 'PROCESS',
        'meaning': 'filter/strain',
        'latin': 'colare',
        'confidence': 'LOW',
        'evidence': 'Appears with liquid terms',
        'alternatives': ['sieve']
    },
    'fche': {
        'category': 'PROCESS',
        'meaning': 'filtered',
        'latin': 'colatus',
        'confidence': 'LOW',
        'evidence': 'Liquid context',
        'alternatives': ['strained']
    },
    'cph': {
        'category': 'PROCESS',
        'meaning': 'press/extract',
        'latin': 'premere',
        'confidence': 'LOW',
        'evidence': 'Pressing context inferred',
        'alternatives': ['squeeze']
    },
    'cfh': {
        'category': 'PROCESS',
        'meaning': 'well-treated',
        'latin': 'bene tractatus',
        'confidence': 'LOW',
        'evidence': 'Variant of ckh',
        'alternatives': ['thoroughly processed']
    },

    # NON-GALLOWS MIDDLES - State and property markers
    'ke': {
        'category': 'STATE',
        'meaning': 'heat/heated',
        'latin': 'calefacere',
        'confidence': 'HIGH',
        'evidence': 'BIOLOGICAL 2.2x (heating procedures)',
        'alternatives': ['warm']
    },
    'kee': {
        'category': 'STATE',
        'meaning': 'steam/steamed',
        'latin': 'vaporare',
        'confidence': 'HIGH',
        'evidence': 'BIOLOGICAL 2.3x (fumigation)',
        'alternatives': ['vapor']
    },
    'ol': {
        'category': 'STATE',
        'meaning': 'oil',
        'latin': 'oleum',
        'confidence': 'HIGH',
        'evidence': 'HERBAL 1.7x, medium context',
        'alternatives': ['fat', 'grease']
    },
    'or': {
        'category': 'STATE',
        'meaning': 'benefit',
        'latin': 'prodesse',
        'confidence': 'MEDIUM',
        'evidence': 'HERBAL 1.9x',
        'alternatives': ['value', 'virtue']
    },
    'ed': {
        'category': 'STATE',
        'meaning': 'dry',
        'latin': 'siccus',
        'confidence': 'MEDIUM',
        'evidence': 'Context inference',
        'alternatives': ['dried out']
    },
    'ee': {
        'category': 'STATE',
        'meaning': 'moist/wet',
        'latin': 'madidus',
        'confidence': 'MEDIUM',
        'evidence': 'Context inference',
        'alternatives': ['damp']
    },
    'eo': {
        'category': 'STATE',
        'meaning': 'flow',
        'latin': 'fluere',
        'confidence': 'MEDIUM',
        'evidence': 'ZODIAC 3.4x (celestial/menstrual motion)',
        'alternatives': ['movement']
    },
    'o': {
        'category': 'STATE',
        'meaning': 'whole/complete',
        'latin': 'totus',
        'confidence': 'LOW',
        'evidence': 'ZODIAC 2.1x',
        'alternatives': ['full', 'circle']
    },
    'a': {
        'category': 'STATE',
        'meaning': 'one/single',
        'latin': 'unus',
        'confidence': 'LOW',
        'evidence': 'Grammatical marker',
        'alternatives': ['unit']
    },
}

# SUFFIX MAPPINGS - Grammatical completion markers
# These follow Latin-style grammatical endings

SUFFIX_MAPPINGS = {
    'y': {
        'function': 'noun ending',
        'latin': '-um (neuter)',
        'confidence': 'HIGH',
        'evidence': '41% of all words end in -y',
        'notes': 'Most common ending, marks noun completion'
    },
    'dy': {
        'function': 'past participle',
        'latin': '-tus/-ta/-tum',
        'confidence': 'HIGH',
        'evidence': 'Consistent with done/completed sense',
        'notes': 'Marks action as completed'
    },
    'ey': {
        'function': 'present participle',
        'latin': '-ens/-ans',
        'confidence': 'HIGH',
        'evidence': 'Consistent with ongoing/current sense',
        'notes': 'Marks action in progress'
    },
    'aiin': {
        'function': 'place/container',
        'latin': '-arium',
        'confidence': 'HIGH',
        'evidence': 'Appears with location terms',
        'notes': 'Marks a place where X is kept/done'
    },
    'ain': {
        'function': 'action noun',
        'latin': '-atio/-atio',
        'confidence': 'MEDIUM',
        'evidence': 'Process nominalization',
        'notes': 'Converts verb to noun (the act of X)'
    },
    'iin': {
        'function': 'substance',
        'latin': '-ium',
        'confidence': 'MEDIUM',
        'evidence': 'Material context',
        'notes': 'Marks a substance or thing'
    },
    'hy': {
        'function': 'full of',
        'latin': '-osus',
        'confidence': 'MEDIUM',
        'evidence': 'Adjectival context',
        'notes': 'Marks abundance'
    },
    'ky': {
        'function': 'relating to',
        'latin': '-icus',
        'confidence': 'MEDIUM',
        'evidence': 'Adjectival context',
        'notes': 'Forms adjective from noun'
    },
    'ar': {
        'function': 'agent/doer',
        'latin': '-or/-tor',
        'confidence': 'LOW',
        'evidence': 'Inferred from context',
        'notes': 'One who does X'
    },
    'al': {
        'function': 'adjectival',
        'latin': '-alis',
        'confidence': 'LOW',
        'evidence': 'Inferred',
        'notes': 'Relating to'
    },
}

# =============================================================================
# LAYER 2: CIPHER LAYER - CHARACTER SUBSTITUTION
# =============================================================================

# The cipher layer maps Voynich characters to shorthand elements
# This mapping is NOT fully recovered - we know the patterns but not all values

CIPHER_NOTES = """
CIPHER LAYER UNDERSTANDING:

1. Character Position Constraints:
   - 'q' appears 99% in first position (prefix marker)
   - 'i', 'h', 'e' appear 100% in middle positions
   - 'n', 'm', 'y' appear >94% in final position (suffix markers)

2. Character Classes (hypothesized):
   - Initial class: q, c, s, d, a, o (domain markers)
   - Medial class: o, l, k, t, p, f, e, i, h (process/state markers)
   - Final class: y, n, m, r, l, d (grammatical markers)

3. Gallows Characters:
   - Tall letters (k, t, p, f with h combinations) function as process verbs
   - They appear to be ligatures or special markers for medical procedures

4. The cipher is NOT simple substitution:
   - Same plaintext may use different ciphertext in different positions
   - Context affects which cipher variant is used
   - This is consistent with medieval steganographic practices
"""

# =============================================================================
# TRANSITION GRAMMAR - WHAT FOLLOWS WHAT
# =============================================================================

TRANSITION_GRAMMAR = {
    'rules': [
        'PLANT follows BODY (32.2% - strongest content transition)',
        'PROCESS follows PLANT (ingredient -> action)',
        'BODY follows PROCESS (action -> target)',
        'TIME/CELESTIAL can appear after any content category',
        'OTHER can appear anywhere (uncategorized words)',
    ],
    'procedural_templates': {
        'PREPARATION': 'PLANT + PROCESS + STATE',
        'APPLICATION': 'PROCESS + BODY + TIMING',
        'COMPOUND': 'PLANT + PROCESS + BODY + TIME',
        'FULL_RECIPE': 'PLANT + PROCESS + BODY (274 occurrences validated)',
    },
    'forbidden_sequences': [
        'TIME + TIME (rare)',
        'CELESTIAL + CELESTIAL (rare)',
    ]
}

# =============================================================================
# KNOWN VOCABULARY - High-confidence word mappings
# =============================================================================

KNOWN_VOCABULARY = {
    # Plant terms
    'chedy': {'meaning': 'dried herb', 'confidence': 'HIGH'},
    'shedy': {'meaning': 'herb juice', 'confidence': 'HIGH'},
    'daiin': {'meaning': 'leaves', 'confidence': 'HIGH'},
    'dain': {'meaning': 'leaf', 'confidence': 'HIGH'},
    'chor': {'meaning': 'herb benefit', 'confidence': 'MEDIUM'},
    'shey': {'meaning': 'juice/sap', 'confidence': 'MEDIUM'},
    'chol': {'meaning': 'hot herb', 'confidence': 'MEDIUM'},

    # Body terms
    'qokedy': {'meaning': 'womb heated/fumigated', 'confidence': 'HIGH'},
    'qokeedy': {'meaning': 'womb steamed', 'confidence': 'HIGH'},
    'qokain': {'meaning': 'womb treatment (action)', 'confidence': 'HIGH'},
    'qokaiin': {'meaning': 'womb place', 'confidence': 'MEDIUM'},

    # Time terms
    'otaiin': {'meaning': 'time/season place', 'confidence': 'HIGH'},
    'okaiin': {'meaning': 'sky/constellation place', 'confidence': 'MEDIUM'},
    'otar': {'meaning': 'at time', 'confidence': 'MEDIUM'},

    # Liquid terms
    'cthy': {'meaning': 'water', 'confidence': 'HIGH'},
    'dol': {'meaning': 'oil from', 'confidence': 'MEDIUM'},
}

# =============================================================================
# CONFIDENCE STATISTICS
# =============================================================================

def calculate_confidence_stats():
    """Calculate overall confidence distribution."""
    stats = {
        'prefix': Counter(),
        'middle': Counter(),
        'suffix': Counter(),
        'vocabulary': Counter()
    }

    for p in PREFIX_MAPPINGS.values():
        stats['prefix'][p['confidence']] += 1

    for m in MIDDLE_MAPPINGS.values():
        stats['middle'][m['confidence']] += 1

    for s in SUFFIX_MAPPINGS.values():
        stats['suffix'][s['confidence']] += 1

    for v in KNOWN_VOCABULARY.values():
        stats['vocabulary'][v['confidence']] += 1

    return stats

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 90)
    print("TWO-LAYER MODEL FORMAL SPECIFICATION")
    print("Voynich Manuscript Decoder Reference")
    print("=" * 90)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Layer 1 Summary
    print("=" * 90)
    print("LAYER 1: SHORTHAND SYSTEM (Compositional Medical Notation)")
    print("=" * 90)
    print()

    print("-" * 90)
    print("PREFIX MAPPINGS (Semantic Domains)")
    print("-" * 90)
    print(f"{'PREFIX':<8} {'CATEGORY':<12} {'MEANING':<20} {'LATIN':<15} {'CONFIDENCE':<10}")
    print("-" * 90)

    for prefix, data in sorted(PREFIX_MAPPINGS.items()):
        print(f"{prefix:<8} {data['category']:<12} {data['meaning']:<20} {data['latin']:<15} {data['confidence']:<10}")
    print()

    print("-" * 90)
    print("MIDDLE MAPPINGS (Process/State)")
    print("-" * 90)
    print(f"{'MIDDLE':<8} {'CATEGORY':<12} {'MEANING':<20} {'LATIN':<15} {'CONFIDENCE':<10}")
    print("-" * 90)

    # Show HIGH and MEDIUM confidence only to keep it readable
    for middle, data in sorted(MIDDLE_MAPPINGS.items()):
        if data['confidence'] in ['HIGH', 'MEDIUM']:
            print(f"{middle:<8} {data['category']:<12} {data['meaning']:<20} {data['latin']:<15} {data['confidence']:<10}")
    print()

    print("-" * 90)
    print("SUFFIX MAPPINGS (Grammar)")
    print("-" * 90)
    print(f"{'SUFFIX':<8} {'FUNCTION':<20} {'LATIN':<15} {'CONFIDENCE':<10}")
    print("-" * 90)

    for suffix, data in sorted(SUFFIX_MAPPINGS.items()):
        print(f"{suffix:<8} {data['function']:<20} {data['latin']:<15} {data['confidence']:<10}")
    print()

    # Layer 2 Summary
    print("=" * 90)
    print("LAYER 2: CIPHER LAYER (Character Substitution)")
    print("=" * 90)
    print(CIPHER_NOTES)
    print()

    # Transition Grammar
    print("=" * 90)
    print("TRANSITION GRAMMAR")
    print("=" * 90)
    print()
    print("Rules:")
    for rule in TRANSITION_GRAMMAR['rules']:
        print(f"  - {rule}")
    print()
    print("Procedural Templates:")
    for name, template in TRANSITION_GRAMMAR['procedural_templates'].items():
        print(f"  {name}: {template}")
    print()

    # Confidence Statistics
    print("=" * 90)
    print("CONFIDENCE STATISTICS")
    print("=" * 90)
    print()

    stats = calculate_confidence_stats()

    for category, counts in stats.items():
        total = sum(counts.values())
        print(f"{category.upper()}:")
        for conf, count in sorted(counts.items(), key=lambda x: ['HIGH', 'MEDIUM', 'LOW', 'SPECULATIVE'].index(x[0]) if x[0] in ['HIGH', 'MEDIUM', 'LOW', 'SPECULATIVE'] else 99):
            pct = count / total * 100 if total > 0 else 0
            print(f"  {conf}: {count} ({pct:.1f}%)")
        print()

    # Calculate overall HIGH confidence
    total_high = sum(stats[cat]['HIGH'] for cat in stats)
    total_all = sum(sum(counts.values()) for counts in stats.values())

    print(f"OVERALL HIGH CONFIDENCE: {total_high}/{total_all} ({total_high/total_all*100:.1f}%)")
    print()

    # Known Vocabulary
    print("=" * 90)
    print("KNOWN VOCABULARY (HIGH/MEDIUM Confidence)")
    print("=" * 90)
    print()
    print(f"{'WORD':<15} {'MEANING':<35} {'CONFIDENCE':<10}")
    print("-" * 60)

    for word, data in sorted(KNOWN_VOCABULARY.items()):
        print(f"{word:<15} {data['meaning']:<35} {data['confidence']:<10}")
    print()

    # Save full specification
    spec = {
        'timestamp': datetime.now().isoformat(),
        'layer1_shorthand': {
            'prefixes': PREFIX_MAPPINGS,
            'middles': MIDDLE_MAPPINGS,
            'suffixes': SUFFIX_MAPPINGS
        },
        'layer2_cipher': {
            'notes': CIPHER_NOTES,
            'position_constraints': {
                'initial': ['q', 'c', 's', 'd', 'a', 'o'],
                'medial': ['o', 'l', 'k', 't', 'p', 'f', 'e', 'i', 'h'],
                'final': ['y', 'n', 'm', 'r', 'l', 'd']
            }
        },
        'transition_grammar': TRANSITION_GRAMMAR,
        'known_vocabulary': KNOWN_VOCABULARY,
        'confidence_stats': {cat: dict(counts) for cat, counts in stats.items()}
    }

    with open('two_layer_specification.json', 'w') as f:
        json.dump(spec, f, indent=2)

    print(f"Full specification saved to two_layer_specification.json")
    print()

    print("=" * 90)
    print("SPECIFICATION COMPLETE")
    print("=" * 90)


if __name__ == '__main__':
    main()
