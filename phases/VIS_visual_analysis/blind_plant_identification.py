#!/usr/bin/env python3
"""
TASK 5: Blind Plant Identification Protocol

The expert warned that plant identification is dangerous for confirmation bias.

Implement blind dual-path analysis:
1. Path 1 (text-first): Decode procedures WITHOUT illustrations, predict functional class
2. Path 2 (illustration-first): Describe plant features WITHOUT text
3. Path 3 (convergence): Check for matches only after both paths complete

For each proposed identification:
- List two alternative possibilities
- Test if alternatives break procedural coherence
- Only accept if one plant clearly outperforms alternatives
"""

import json
from collections import defaultdict
from datetime import datetime

# =============================================================================
# KNOWN MORPHEME MAPPINGS (for text-first path)
# =============================================================================

PREFIX_MEANINGS = {
    'qo': 'womb/reproductive', 'ol': 'menstrual/fluid', 'ch': 'herb/plant',
    'sh': 'juice/sap', 'da': 'leaf', 'ct': 'water', 'cth': 'water/purify',
    'ot': 'time/season', 'ok': 'sky/celestial', 'ar': 'air',
    'so': 'health/body', 'sa': 'seed', 'or': 'gold/precious',
}

MIDDLE_MEANINGS = {
    'ke': 'heat/warm', 'kee': 'steam/boil', 'ol': 'oil/fatty',
    'or': 'benefit/help', 'ed': 'dry', 'ee': 'wet/moist',
    'lch': 'wash/cleanse', 'tch': 'prepare', 'cth': 'purify',
    'kch': 'potent/strong', 'ckh': 'treat/process', 'pch': 'apply',
    'eo': 'flow/move',
}

SUFFIX_MEANINGS = {
    'y': 'noun', 'dy': 'past/completed', 'ey': 'present/ongoing',
    'aiin': 'place/container', 'ain': 'action', 'hy': 'full-of',
}

# Humoral properties derived from decoded terms
HUMORAL_MARKERS = {
    'HOT': ['ke', 'kee', 'chol', 'kch'],  # heating, steaming, hot
    'COLD': ['cth', 'ct'],  # water, cooling
    'DRY': ['ed'],  # dried
    'WET': ['ee', 'ol'],  # moist, oily
}

# =============================================================================
# SAMPLE HERBAL FOLIOS WITH DECODED TEXT
# =============================================================================

HERBAL_FOLIOS = {
    'f1v': {
        'decoded_words': [
            'chedy', 'shedy', 'daiin', 'chol', 'qokedy', 'olkedy',
            'lchedy', 'tched', 'cthar', 'keedy', 'shol', 'chor',
        ],
        'word_contexts': {
            'chedy': 'dried-herb',
            'qokedy': 'womb-heated',
            'olkedy': 'menses-heated',
            'chol': 'HOT',
            'keedy': 'heating',
        }
    },
    'f2r': {
        'decoded_words': [
            'chedy', 'shedy', 'daiin', 'chor', 'shol', 'tchedy',
            'lchedy', 'cthedy', 'oleedy', 'kchedy',
        ],
        'word_contexts': {
            'chedy': 'dried-herb',
            'shol': 'juice-oil',
            'tchedy': 'prepared',
            'cthedy': 'purified',
        }
    },
    'f3v': {
        'decoded_words': [
            'chedy', 'shedy', 'qokedy', 'qokeedy', 'chol', 'chol',
            'olkedy', 'dain', 'kchedy', 'tched',
        ],
        'word_contexts': {
            'qokedy': 'womb-heated',
            'qokeedy': 'womb-steamed',
            'chol': 'HOT',
            'olkedy': 'menses-heated',
        }
    },
    'f5v': {
        'decoded_words': [
            'chedy', 'daiin', 'shedy', 'qokedy', 'chol', 'oleedy',
            'lchedy', 'shol', 'cthedy',
        ],
        'word_contexts': {
            'qokedy': 'womb-heated',
            'chol': 'HOT',
            'oleedy': 'moist-fluid',
            'lchedy': 'washed',
        }
    },
    'f6r': {
        'decoded_words': [
            'chedy', 'shedy', 'daiin', 'cthedy', 'lchedy', 'shol',
            'cthar', 'oleedy', 'tchedy',
        ],
        'word_contexts': {
            'cthedy': 'purified',
            'lchedy': 'washed',
            'cthar': 'water-agent',
            'oleedy': 'moist',
        }
    },
}

# =============================================================================
# ILLUSTRATION DESCRIPTIONS (from manuscript studies)
# =============================================================================

ILLUSTRATION_FEATURES = {
    'f1v': {
        'description': 'Plant with broad leaves, purple-tinged flowers, dark berries or fruits',
        'leaf_shape': 'ovate to elliptical, pointed tips',
        'root_type': 'thick tuberous root',
        'flower_color': 'purple or violet',
        'distinctive': 'berry-like fruits, dark colored',
    },
    'f2r': {
        'description': 'Plant with deeply divided leaves, yellow flowers',
        'leaf_shape': 'palmately divided, multiple lobes',
        'root_type': 'thick taproot',
        'flower_color': 'yellow',
        'distinctive': 'compound leaves, buttercup-like',
    },
    'f3v': {
        'description': 'Plant with large basal leaves, tall flowering stalk',
        'leaf_shape': 'large, palmate, deeply lobed',
        'root_type': 'thick black root',
        'flower_color': 'green or dark purple',
        'distinctive': 'very large leaves, dark root',
    },
    'f5v': {
        'description': 'Plant with rounded leaves, pink or white flowers',
        'leaf_shape': 'rounded, kidney-shaped',
        'root_type': 'fibrous root system',
        'flower_color': 'pink or white',
        'distinctive': 'soft fuzzy leaves, mucilaginous',
    },
    'f6r': {
        'description': 'Aquatic or water-associated plant, floating leaves',
        'leaf_shape': 'rounded, floating',
        'root_type': 'aquatic roots',
        'flower_color': 'white or pale',
        'distinctive': 'water habitat, lily-like',
    },
}

# =============================================================================
# KNOWN MEDIEVAL PLANTS AND THEIR PROPERTIES
# =============================================================================

MEDIEVAL_PLANTS = {
    'belladonna': {
        'latin': 'Atropa belladonna',
        'humoral': ['HOT', 'DRY'],
        'gynecological_uses': ['cervix dilation', 'pain relief', 'sedative'],
        'leaf_shape': 'ovate, pointed',
        'root_type': 'thick tuberous',
        'flower_color': 'purple',
        'distinctive': 'dark berries',
    },
    'hellebore': {
        'latin': 'Helleborus niger',
        'humoral': ['HOT', 'DRY'],
        'gynecological_uses': ['emmenagogue', 'abortifacient', 'purgative'],
        'leaf_shape': 'palmate, deeply divided',
        'root_type': 'black root',
        'flower_color': 'white, green, or purple',
        'distinctive': 'black root, highly toxic',
    },
    'mallow': {
        'latin': 'Malva sylvestris',
        'humoral': ['COLD', 'WET'],
        'gynecological_uses': ['emollient', 'birth canal softening', 'anti-inflammatory'],
        'leaf_shape': 'rounded, lobed',
        'root_type': 'fibrous',
        'flower_color': 'pink or white',
        'distinctive': 'mucilaginous, soft',
    },
    'waterlily': {
        'latin': 'Nymphaea alba',
        'humoral': ['COLD', 'WET'],
        'gynecological_uses': ['anaphrodisiac', 'cooling', 'reduce libido'],
        'leaf_shape': 'rounded, floating',
        'root_type': 'aquatic',
        'flower_color': 'white',
        'distinctive': 'aquatic, floating leaves',
    },
    'rue': {
        'latin': 'Ruta graveolens',
        'humoral': ['HOT', 'DRY'],
        'gynecological_uses': ['emmenagogue', 'abortifacient'],
        'leaf_shape': 'pinnate, bluish',
        'root_type': 'woody',
        'flower_color': 'yellow',
        'distinctive': 'strong smell, bluish leaves',
    },
    'mugwort': {
        'latin': 'Artemisia vulgaris',
        'humoral': ['HOT', 'DRY'],
        'gynecological_uses': ['emmenagogue', 'fumigation'],
        'leaf_shape': 'deeply divided',
        'root_type': 'rhizome',
        'flower_color': 'reddish-brown',
        'distinctive': 'aromatic, silvery underside',
    },
    'buttercup': {
        'latin': 'Ranunculus spp.',
        'humoral': ['HOT', 'DRY'],
        'gynecological_uses': ['vesicant', 'counter-irritant'],
        'leaf_shape': 'palmately divided',
        'root_type': 'fibrous',
        'flower_color': 'yellow',
        'distinctive': 'shiny yellow petals, caustic',
    },
}

# =============================================================================
# PATH 1: TEXT-FIRST ANALYSIS (blind to illustrations)
# =============================================================================

def analyze_text_blind(folio_id):
    """
    Analyze decoded text WITHOUT looking at illustration.
    Predict functional class only.
    """
    folio_data = HERBAL_FOLIOS.get(folio_id, {})
    words = folio_data.get('decoded_words', [])
    contexts = folio_data.get('word_contexts', {})

    analysis = {
        'folio': folio_id,
        'path': 'TEXT-FIRST',
        'humoral_indicators': {'HOT': 0, 'COLD': 0, 'DRY': 0, 'WET': 0},
        'gynecological_indicators': 0,
        'preparation_types': [],
        'predicted_class': None,
        'reasoning': [],
    }

    # Count humoral indicators
    for word in words:
        for quality, markers in HUMORAL_MARKERS.items():
            for marker in markers:
                if marker in word:
                    analysis['humoral_indicators'][quality] += 1

    # Count gynecological indicators
    gyn_markers = ['qo', 'ol', 'qoke', 'olke']
    for word in words:
        for marker in gyn_markers:
            if marker in word:
                analysis['gynecological_indicators'] += 1

    # Identify preparation types
    if any('lch' in w for w in words):
        analysis['preparation_types'].append('washing')
    if any('tch' in w for w in words):
        analysis['preparation_types'].append('preparing')
    if any('cth' in w for w in words):
        analysis['preparation_types'].append('purifying')
    if any('ke' in w for w in words):
        analysis['preparation_types'].append('heating')
    if any('kee' in w for w in words):
        analysis['preparation_types'].append('steaming')

    # Predict functional class
    hot = analysis['humoral_indicators']['HOT']
    cold = analysis['humoral_indicators']['COLD']
    dry = analysis['humoral_indicators']['DRY']
    wet = analysis['humoral_indicators']['WET']
    gyn = analysis['gynecological_indicators']

    if hot > cold and gyn > 2:
        analysis['predicted_class'] = 'HOT-GYNECOLOGICAL'
        analysis['reasoning'].append(f"HOT markers ({hot}) > COLD ({cold})")
        analysis['reasoning'].append(f"Strong gynecological focus ({gyn} markers)")
    elif cold > hot:
        analysis['predicted_class'] = 'COLD-MOISTENING'
        analysis['reasoning'].append(f"COLD markers ({cold}) > HOT ({hot})")
    elif hot > 0 and dry > wet:
        analysis['predicted_class'] = 'HOT-DRY'
        analysis['reasoning'].append(f"HOT ({hot}) and DRY ({dry}) dominant")
    elif wet > dry:
        analysis['predicted_class'] = 'MOISTENING'
        analysis['reasoning'].append(f"WET markers ({wet}) > DRY ({dry})")
    else:
        analysis['predicted_class'] = 'NEUTRAL'
        analysis['reasoning'].append("No clear humoral dominance")

    return analysis

# =============================================================================
# PATH 2: ILLUSTRATION-FIRST ANALYSIS (blind to text)
# =============================================================================

def analyze_illustration_blind(folio_id):
    """
    Describe plant features WITHOUT looking at decoded text.
    """
    features = ILLUSTRATION_FEATURES.get(folio_id, {})

    analysis = {
        'folio': folio_id,
        'path': 'ILLUSTRATION-FIRST',
        'observed_features': features,
        'matching_plants': [],
    }

    if not features:
        analysis['matching_plants'] = ['UNKNOWN - no illustration data']
        return analysis

    # Match against known plants
    for plant_name, plant_data in MEDIEVAL_PLANTS.items():
        match_score = 0
        match_reasons = []

        # Check leaf shape
        if features.get('leaf_shape') and plant_data.get('leaf_shape'):
            if any(word in features['leaf_shape'].lower() for word in plant_data['leaf_shape'].lower().split()):
                match_score += 2
                match_reasons.append(f"Leaf shape matches: {plant_data['leaf_shape']}")

        # Check root type
        if features.get('root_type') and plant_data.get('root_type'):
            if any(word in features['root_type'].lower() for word in plant_data['root_type'].lower().split()):
                match_score += 2
                match_reasons.append(f"Root type matches: {plant_data['root_type']}")

        # Check flower color
        if features.get('flower_color') and plant_data.get('flower_color'):
            if any(color in features['flower_color'].lower() for color in plant_data['flower_color'].lower().split()):
                match_score += 1
                match_reasons.append(f"Flower color matches: {plant_data['flower_color']}")

        # Check distinctive features
        if features.get('distinctive') and plant_data.get('distinctive'):
            if any(word in features['distinctive'].lower() for word in plant_data['distinctive'].lower().split()):
                match_score += 3
                match_reasons.append(f"Distinctive feature matches: {plant_data['distinctive']}")

        if match_score > 0:
            analysis['matching_plants'].append({
                'plant': plant_name,
                'score': match_score,
                'reasons': match_reasons,
            })

    # Sort by score
    analysis['matching_plants'].sort(key=lambda x: x['score'], reverse=True)

    return analysis

# =============================================================================
# PATH 3: CONVERGENCE CHECK
# =============================================================================

def check_convergence(text_analysis, illustration_analysis):
    """
    Check if text predictions match illustration-based plant identifications.
    Only after both paths are complete.
    """
    convergence = {
        'folio': text_analysis['folio'],
        'text_prediction': text_analysis['predicted_class'],
        'top_illustration_matches': illustration_analysis['matching_plants'][:3],
        'convergence_result': None,
        'proposed_identification': None,
        'alternatives': [],
        'coherence_check': None,
    }

    predicted_class = text_analysis['predicted_class']
    top_matches = illustration_analysis['matching_plants'][:3]

    if not top_matches:
        convergence['convergence_result'] = 'NO_ILLUSTRATION_MATCH'
        return convergence

    # Check if predicted class matches plant properties
    convergent_plants = []

    for match in top_matches:
        plant_name = match['plant']
        plant_data = MEDIEVAL_PLANTS.get(plant_name, {})
        plant_humoral = plant_data.get('humoral', [])

        # Check humoral match
        if 'HOT' in predicted_class and 'HOT' in plant_humoral:
            convergent_plants.append({
                'plant': plant_name,
                'illustration_score': match['score'],
                'humoral_match': True,
                'gyn_uses': plant_data.get('gynecological_uses', []),
            })
        elif 'COLD' in predicted_class and 'COLD' in plant_humoral:
            convergent_plants.append({
                'plant': plant_name,
                'illustration_score': match['score'],
                'humoral_match': True,
                'gyn_uses': plant_data.get('gynecological_uses', []),
            })
        elif 'MOISTENING' in predicted_class and 'WET' in plant_humoral:
            convergent_plants.append({
                'plant': plant_name,
                'illustration_score': match['score'],
                'humoral_match': True,
                'gyn_uses': plant_data.get('gynecological_uses', []),
            })

    if convergent_plants:
        best = convergent_plants[0]
        convergence['convergence_result'] = 'CONVERGENT'
        convergence['proposed_identification'] = best['plant']
        convergence['alternatives'] = [p['plant'] for p in convergent_plants[1:]]

        # Coherence check: do gynecological uses match the context?
        gyn_score = text_analysis['gynecological_indicators']
        if gyn_score > 2 and best['gyn_uses']:
            convergence['coherence_check'] = 'STRONG - gynecological uses match context'
        elif gyn_score > 0:
            convergence['coherence_check'] = 'MODERATE - some gynecological context'
        else:
            convergence['coherence_check'] = 'WEAK - no gynecological context'
    else:
        convergence['convergence_result'] = 'DIVERGENT'
        convergence['proposed_identification'] = None
        convergence['coherence_check'] = 'FAILED - text and illustration do not align'

    return convergence

def test_alternatives(convergence):
    """
    Test whether alternative identifications break procedural coherence.
    """
    assessment = {
        'folio': convergence['folio'],
        'proposed': convergence['proposed_identification'],
        'alternatives': convergence['alternatives'],
        'alternative_tests': [],
        'final_recommendation': None,
    }

    if not convergence['proposed_identification']:
        assessment['final_recommendation'] = 'NO IDENTIFICATION - insufficient convergence'
        return assessment

    proposed = convergence['proposed_identification']
    proposed_data = MEDIEVAL_PLANTS.get(proposed, {})

    for alt in convergence['alternatives']:
        alt_data = MEDIEVAL_PLANTS.get(alt, {})

        # Check if alternative breaks coherence
        test = {
            'alternative': alt,
            'humoral_same': proposed_data.get('humoral') == alt_data.get('humoral'),
            'gyn_overlap': bool(set(proposed_data.get('gynecological_uses', [])) &
                               set(alt_data.get('gynecological_uses', []))),
            'breaks_coherence': False,
        }

        # If humoral qualities differ significantly, coherence breaks
        if not test['humoral_same']:
            test['breaks_coherence'] = True
            test['break_reason'] = f"Humoral mismatch: {proposed_data.get('humoral')} vs {alt_data.get('humoral')}"

        assessment['alternative_tests'].append(test)

    # Final recommendation
    breaking_alts = [t for t in assessment['alternative_tests'] if t['breaks_coherence']]

    if len(breaking_alts) == len(assessment['alternative_tests']):
        assessment['final_recommendation'] = f"ACCEPT {proposed} - all alternatives break coherence"
    elif len(breaking_alts) > 0:
        non_breaking = [t['alternative'] for t in assessment['alternative_tests'] if not t['breaks_coherence']]
        assessment['final_recommendation'] = f"TENTATIVE {proposed} - alternatives {non_breaking} also viable"
    else:
        assessment['final_recommendation'] = f"UNCERTAIN - multiple plants fit equally well"

    return assessment

# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():
    print("=" * 70)
    print("BLIND PLANT IDENTIFICATION PROTOCOL")
    print("Dual-path analysis to avoid confirmation bias")
    print("=" * 70)

    results = []

    for folio_id in HERBAL_FOLIOS.keys():
        print(f"\n{'=' * 50}")
        print(f"ANALYZING FOLIO: {folio_id}")
        print(f"{'=' * 50}")

        # PATH 1: Text-first (blind to illustration)
        print(f"\n--- PATH 1: TEXT-FIRST ANALYSIS ---")
        print("(Decoding procedures WITHOUT looking at illustration)")
        text_analysis = analyze_text_blind(folio_id)
        print(f"  Humoral indicators: {text_analysis['humoral_indicators']}")
        print(f"  Gynecological markers: {text_analysis['gynecological_indicators']}")
        print(f"  Preparation types: {text_analysis['preparation_types']}")
        print(f"  PREDICTED CLASS: {text_analysis['predicted_class']}")
        for reason in text_analysis['reasoning']:
            print(f"    - {reason}")

        # PATH 2: Illustration-first (blind to text)
        print(f"\n--- PATH 2: ILLUSTRATION-FIRST ANALYSIS ---")
        print("(Describing plant features WITHOUT decoded text)")
        illust_analysis = analyze_illustration_blind(folio_id)
        if illust_analysis['observed_features']:
            print(f"  Description: {illust_analysis['observed_features'].get('description', 'N/A')}")
            print(f"  Leaf shape: {illust_analysis['observed_features'].get('leaf_shape', 'N/A')}")
            print(f"  Root type: {illust_analysis['observed_features'].get('root_type', 'N/A')}")
        print(f"  Top matching plants:")
        for match in illust_analysis['matching_plants'][:3]:
            print(f"    - {match['plant']} (score: {match['score']})")
            for reason in match.get('reasons', [])[:2]:
                print(f"        {reason}")

        # PATH 3: Convergence check
        print(f"\n--- PATH 3: CONVERGENCE CHECK ---")
        print("(Comparing text predictions to illustration matches)")
        convergence = check_convergence(text_analysis, illust_analysis)
        print(f"  Text prediction: {convergence['text_prediction']}")
        print(f"  Convergence result: {convergence['convergence_result']}")
        print(f"  Proposed identification: {convergence['proposed_identification']}")
        print(f"  Alternatives: {convergence['alternatives']}")
        print(f"  Coherence check: {convergence['coherence_check']}")

        # Test alternatives
        print(f"\n--- ALTERNATIVE TESTING ---")
        alt_test = test_alternatives(convergence)
        print(f"  FINAL RECOMMENDATION: {alt_test['final_recommendation']}")
        for test in alt_test['alternative_tests']:
            print(f"    {test['alternative']}: humoral_same={test['humoral_same']}, gyn_overlap={test['gyn_overlap']}, breaks={test['breaks_coherence']}")

        results.append({
            'folio': folio_id,
            'text_analysis': text_analysis,
            'illustration_analysis': illust_analysis,
            'convergence': convergence,
            'alternative_test': alt_test,
        })

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY OF BLIND IDENTIFICATIONS")
    print("=" * 70)

    print("\n| Folio | Text Prediction | Proposed Plant | Confidence |")
    print("|-------|-----------------|----------------|------------|")

    for r in results:
        folio = r['folio']
        pred = r['text_analysis']['predicted_class']
        plant = r['convergence']['proposed_identification'] or 'NONE'
        rec = r['alternative_test']['final_recommendation']

        if 'ACCEPT' in rec:
            conf = 'HIGH'
        elif 'TENTATIVE' in rec:
            conf = 'MEDIUM'
        else:
            conf = 'LOW'

        print(f"| {folio} | {pred:15} | {plant:14} | {conf:10} |")

    # Honest assessment
    print("\n" + "-" * 50)
    print("HONEST ASSESSMENT:")
    print("-" * 50)

    high_conf = sum(1 for r in results if 'ACCEPT' in r['alternative_test']['final_recommendation'])
    medium_conf = sum(1 for r in results if 'TENTATIVE' in r['alternative_test']['final_recommendation'])
    low_conf = sum(1 for r in results if 'UNCERTAIN' in r['alternative_test']['final_recommendation'])

    print(f"""
  High confidence identifications: {high_conf}/{len(results)}
  Medium confidence: {medium_conf}/{len(results)}
  Low confidence or none: {low_conf}/{len(results)}

  LIMITATIONS OF THIS ANALYSIS:
  1. Illustration descriptions are based on secondary sources, not direct examination
  2. Medieval plant illustrations are notoriously stylized and unreliable
  3. Many plants share similar features (e.g., multiple "hot" gynecological herbs)
  4. Our decoded text is itself uncertain (based on unvalidated framework)

  CONCLUSION:
  Even with blind dual-path analysis, plant identifications remain SPECULATIVE.
  The convergence between text and illustration is suggestive but not definitive.
  Any specific plant identification should be presented as a hypothesis, not a fact.
""")

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'methodology': 'Blind dual-path analysis',
        'folios_analyzed': len(results),
        'results': results,
        'summary': {
            'high_confidence': high_conf,
            'medium_confidence': medium_conf,
            'low_confidence': low_conf,
        },
    }

    with open('blind_plant_results.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to blind_plant_results.json")

    return output

if __name__ == "__main__":
    main()
