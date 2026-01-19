#!/usr/bin/env python3
"""
ENHANCED SENSORY EXTRACTION

Expands keyword lists to capture missing sensory instances:
- SMELL: verdampf, verflüchtig, qualm, dünstung, brand, etc.
- TOUCH: wallend, erkalt, dickflüssig, dünnflüssig, kristallin, etc.
- SIGHT: verfärbung, absatz, ausschlag, trübung, belag, etc.

Does NOT modify original database - outputs to results/.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

# ENHANCED sensory keyword patterns
ENHANCED_SENSORY_PATTERNS = {
    'SIGHT': {
        'keywords': [
            # Original (21)
            'farb', 'color', 'sieh', 'schau', 'blick', 'erschein',
            'rot', 'gelb', 'weiß', 'schwarz', 'grün', 'blau', 'braun',
            'klar', 'trüb', 'hell', 'dunkel', 'licht',
            'zeich', 'merk', 'erkenn',
            # NEW (11) - visual process indicators
            'verfärb', 'absatz', 'ausschlag', 'trübung', 'belag',
            'schaum', 'glanz', 'durchsichtig', 'ölfleck', 'übergang',
            'feuchtigkeit'
        ],
        'patterns': [
            r'(?:wenn|bis|sobald).*(?:farb|erschein|sieh)',
            r'(?:rot|gelb|weiß|schwarz|grün)(?:e|er|es)?',
            r'(?:klar|trüb|hell|dunkel)',
            # NEW patterns
            r'(?:verfärb|ausschlag|trübung)',
            r'(?:schaum|belag|glanz)',
        ]
    },
    'SMELL': {
        'keywords': [
            # Original (8)
            'riech', 'geruch', 'duft', 'stink', 'dampf',
            'rauch', 'dunst', 'arom',
            # NEW (12) - volatilization & olfactory
            'verdampf', 'verflüchtig', 'qualm', 'dünstung', 'brand',
            'balsamisch', 'würzig', 'muffig', 'verfault', 'geruchlos',
            'ausdünst', 'ausgasung'
        ],
        'patterns': [
            r'(?:wenn|bis).*riech',
            r'geruch|duft|stink',
            # NEW patterns
            r'(?:verdampf|verflüchtig|qualm)',
            r'(?:balsamisch|würzig|muffig)',
        ]
    },
    'SOUND': {
        'keywords': [
            # Original (10)
            'hör', 'laut', 'still', 'sied', 'wall', 'brodel',
            'zisch', 'knack', 'knister', 'rausch',
            # NEW (4) - additional sound cues
            'gurgel', 'blubb', 'pfeif', 'spritz'
        ],
        'patterns': [
            r'(?:wenn|bis).*(?:sied|wall|brodel)',
            r'(?:zisch|knack|knister)',
            # NEW pattern
            r'(?:gurgel|blubb|pfeif)',
        ]
    },
    'TOUCH': {
        'keywords': [
            # Original (11)
            'fühl', 'warm', 'kalt', 'heiß', 'kühl',
            'weich', 'hart', 'feucht', 'trocken',
            'temperatur', 'grad',
            # NEW (14) - temperature & texture variants
            'wallend', 'erkalt', 'erkalten', 'abkühlung',
            'dickflüssig', 'dünnflüssig', 'kristallin', 'ölig',
            'gelatinös', 'schlammig', 'körnig', 'pulverig',
            'siedhitze', 'gluthitze'
        ],
        'patterns': [
            r'(?:wenn|bis).*(?:warm|kalt|heiß)',
            r'(?:weich|hart|feucht|trocken)',
            # NEW patterns
            r'(?:wallend|erkalt|abkühl)',
            r'(?:dickflüssig|dünnflüssig|kristallin|ölig)',
        ]
    },
    'TASTE': {
        'keywords': [
            # Original (7)
            'schmeck', 'geschmack', 'süß', 'bitter', 'sauer',
            'salz', 'scharf',
            # NEW (4) - taste testing
            'kostversuch', 'prob', 'zung', 'laugen'
        ],
        'patterns': [
            r'schmeck|geschmack',
            r'(?:süß|bitter|sauer|salz)',
        ]
    }
}

def normalize_text(text):
    """Normalize early modern German."""
    text = text.lower()
    text = text.replace('ſ', 's')
    text = text.replace('ꝛ', 'r')
    text = text.replace('ů', 'u')
    text = text.replace('ẽ', 'en')
    return text

def detect_sensory_content(text, patterns=ENHANCED_SENSORY_PATTERNS):
    """Detect sensory modalities in text."""
    normalized = normalize_text(text)
    found = {}

    for modality, rules in patterns.items():
        score = 0
        matches = []

        # Check keywords
        for kw in rules['keywords']:
            if kw in normalized:
                score += 1
                matches.append(kw)

        # Check patterns
        for pattern in rules['patterns']:
            if re.search(pattern, normalized, re.IGNORECASE):
                score += 2
                matches.append(f'pattern:{pattern[:20]}')

        if score > 0:
            found[modality] = {'score': score, 'matches': matches}

    return found

def main():
    print("=" * 70)
    print("ENHANCED SENSORY EXTRACTION")
    print("=" * 70)
    print()

    # Load data
    with open('data/brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    materials = data['materials']
    print(f"Loaded {len(materials)} materials")

    # Count original keywords
    original_keywords = sum(
        len(v['keywords']) for v in {
            'SIGHT': {'keywords': ['farb', 'color', 'sieh', 'schau', 'blick', 'erschein',
                'rot', 'gelb', 'weiß', 'schwarz', 'grün', 'blau', 'braun',
                'klar', 'trüb', 'hell', 'dunkel', 'licht', 'zeich', 'merk', 'erkenn']},
            'SMELL': {'keywords': ['riech', 'geruch', 'duft', 'stink', 'dampf', 'rauch', 'dunst', 'arom']},
            'SOUND': {'keywords': ['hör', 'laut', 'still', 'sied', 'wall', 'brodel', 'zisch', 'knack', 'knister', 'rausch']},
            'TOUCH': {'keywords': ['fühl', 'warm', 'kalt', 'heiß', 'kühl', 'weich', 'hart', 'feucht', 'trocken', 'temperatur', 'grad']},
            'TASTE': {'keywords': ['schmeck', 'geschmack', 'süß', 'bitter', 'sauer', 'salz', 'scharf']}
        }.values()
    )
    enhanced_keywords = sum(len(v['keywords']) for v in ENHANCED_SENSORY_PATTERNS.values())
    print(f"Original keywords: {original_keywords}")
    print(f"Enhanced keywords: {enhanced_keywords} (+{enhanced_keywords - original_keywords})")
    print()

    # ORIGINAL extraction (for comparison)
    print("Running ORIGINAL extraction...")
    original_counts = defaultdict(int)
    original_steps_with_sensory = 0

    ORIGINAL_PATTERNS = {
        'SIGHT': {
            'keywords': ['farb', 'color', 'sieh', 'schau', 'blick', 'erschein',
                'rot', 'gelb', 'weiß', 'schwarz', 'grün', 'blau', 'braun',
                'klar', 'trüb', 'hell', 'dunkel', 'licht', 'zeich', 'merk', 'erkenn'],
            'patterns': [r'(?:wenn|bis|sobald).*(?:farb|erschein|sieh)', r'(?:rot|gelb|weiß|schwarz|grün)(?:e|er|es)?', r'(?:klar|trüb|hell|dunkel)']
        },
        'SMELL': {
            'keywords': ['riech', 'geruch', 'duft', 'stink', 'dampf', 'rauch', 'dunst', 'arom'],
            'patterns': [r'(?:wenn|bis).*riech', r'geruch|duft|stink']
        },
        'SOUND': {
            'keywords': ['hör', 'laut', 'still', 'sied', 'wall', 'brodel', 'zisch', 'knack', 'knister', 'rausch'],
            'patterns': [r'(?:wenn|bis).*(?:sied|wall|brodel)', r'(?:zisch|knack|knister)']
        },
        'TOUCH': {
            'keywords': ['fühl', 'warm', 'kalt', 'heiß', 'kühl', 'weich', 'hart', 'feucht', 'trocken', 'temperatur', 'grad'],
            'patterns': [r'(?:wenn|bis).*(?:warm|kalt|heiß)', r'(?:weich|hart|feucht|trocken)']
        },
        'TASTE': {
            'keywords': ['schmeck', 'geschmack', 'süß', 'bitter', 'sauer', 'salz', 'scharf'],
            'patterns': [r'schmeck|geschmack', r'(?:süß|bitter|sauer|salz)']
        }
    }

    for material in materials:
        for step in material.get('procedural_steps', []):
            text = step.get('brunschwig_text', '')
            sensory = detect_sensory_content(text, ORIGINAL_PATTERNS)
            if sensory:
                original_steps_with_sensory += 1
                for modality in sensory:
                    original_counts[modality] += 1

    # ENHANCED extraction
    print("Running ENHANCED extraction...")
    enhanced_counts = defaultdict(int)
    enhanced_steps_with_sensory = 0
    total_steps = 0

    # Store enhanced results per recipe
    enhanced_recipes = []
    new_detections = defaultdict(list)  # Track what the new keywords found

    for material in materials:
        recipe_sensory = defaultdict(int)

        for step in material.get('procedural_steps', []):
            total_steps += 1
            text = step.get('brunschwig_text', '')

            # Original detection
            original_sensory = detect_sensory_content(text, ORIGINAL_PATTERNS)

            # Enhanced detection
            enhanced_sensory = detect_sensory_content(text, ENHANCED_SENSORY_PATTERNS)

            if enhanced_sensory:
                enhanced_steps_with_sensory += 1
                for modality, details in enhanced_sensory.items():
                    enhanced_counts[modality] += 1
                    recipe_sensory[modality] += 1

                    # Track NEW detections (in enhanced but not original)
                    if modality not in original_sensory:
                        new_detections[modality].append({
                            'recipe': material.get('recipe_id', 'unknown'),
                            'text': text[:100],
                            'matches': details['matches']
                        })

        # Determine dominant modality for recipe
        dominant = None
        if recipe_sensory:
            dominant = max(recipe_sensory.keys(), key=lambda k: recipe_sensory[k])

        enhanced_recipes.append({
            'recipe_id': material.get('recipe_id', 'unknown'),
            'recipe_name': material.get('recipe_name', 'unknown'),
            'regime': material.get('regime_assignment', {}).get('final_regime', 'UNKNOWN'),
            'sensory_counts': dict(recipe_sensory),
            'dominant_modality': dominant,
            'total_sensory_steps': sum(recipe_sensory.values())
        })

    # Compare results
    print()
    print("=" * 70)
    print("COMPARISON: Original vs Enhanced")
    print("=" * 70)
    print()
    print(f"Total steps analyzed: {total_steps}")
    print()
    print(f"{'Modality':<10} | {'Original':>10} | {'Enhanced':>10} | {'Delta':>10} | {'Change':>10}")
    print("-" * 60)

    for modality in ['SIGHT', 'SMELL', 'SOUND', 'TOUCH', 'TASTE']:
        orig = original_counts[modality]
        enh = enhanced_counts[modality]
        delta = enh - orig
        change = f"+{100*delta/orig:.1f}%" if orig > 0 else f"+{enh}"
        print(f"{modality:<10} | {orig:>10} | {enh:>10} | {delta:>+10} | {change:>10}")

    print("-" * 60)
    print(f"{'TOTAL':<10} | {original_steps_with_sensory:>10} | {enhanced_steps_with_sensory:>10} | {enhanced_steps_with_sensory - original_steps_with_sensory:>+10} |")
    print()

    # Recipes by dominant modality
    print("=" * 70)
    print("RECIPES BY DOMINANT MODALITY")
    print("=" * 70)
    print()

    modality_recipe_counts = defaultdict(int)
    for r in enhanced_recipes:
        if r['dominant_modality']:
            modality_recipe_counts[r['dominant_modality']] += 1
        else:
            modality_recipe_counts['NONE'] += 1

    for modality in ['SOUND', 'SIGHT', 'TOUCH', 'SMELL', 'TASTE', 'NONE']:
        count = modality_recipe_counts[modality]
        print(f"  {modality}: {count} recipes")

    # Sample new detections
    print()
    print("=" * 70)
    print("SAMPLE NEW DETECTIONS (not in original)")
    print("=" * 70)
    print()

    for modality in ['SMELL', 'TOUCH', 'SIGHT']:
        detections = new_detections[modality][:3]
        if detections:
            print(f"{modality} - {len(new_detections[modality])} new detections:")
            for d in detections:
                text = d['text'].encode('ascii', 'replace').decode('ascii')[:60]
                print(f"  [{d['recipe']}] {text}...")
                print(f"    Matched: {d['matches'][:3]}")
            print()

    # Save results
    print("=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    print()

    results = {
        'phase': 'ZONE_MODALITY_VALIDATION',
        'extraction_type': 'enhanced',
        'keyword_counts': {
            'original': original_keywords,
            'enhanced': enhanced_keywords,
            'added': enhanced_keywords - original_keywords
        },
        'step_level': {
            'total_steps': total_steps,
            'original': {
                'steps_with_sensory': original_steps_with_sensory,
                'modality_counts': dict(original_counts)
            },
            'enhanced': {
                'steps_with_sensory': enhanced_steps_with_sensory,
                'modality_counts': dict(enhanced_counts)
            },
            'improvement': {
                'additional_steps': enhanced_steps_with_sensory - original_steps_with_sensory,
                'by_modality': {
                    mod: enhanced_counts[mod] - original_counts[mod]
                    for mod in ['SIGHT', 'SMELL', 'SOUND', 'TOUCH', 'TASTE']
                }
            }
        },
        'recipe_level': {
            'total_recipes': len(enhanced_recipes),
            'by_dominant_modality': dict(modality_recipe_counts),
            'recipes': enhanced_recipes
        },
        'new_detections': {
            mod: len(dets) for mod, dets in new_detections.items()
        },
        'sample_new_detections': {
            mod: dets[:5] for mod, dets in new_detections.items()
        }
    }

    output_path = Path('results/enhanced_sensory_extraction.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Saved to {output_path}")
    print()

    # Assessment
    print("=" * 70)
    print("ASSESSMENT")
    print("=" * 70)
    print()

    smell_improved = enhanced_counts['SMELL'] - original_counts['SMELL']
    touch_improved = enhanced_counts['TOUCH'] - original_counts['TOUCH']

    if smell_improved > 5:
        print(f"[PASS] SMELL improved by {smell_improved} instances")
    else:
        print(f"[WARN] SMELL only improved by {smell_improved} instances (target: >5)")

    if touch_improved > 5:
        print(f"[PASS] TOUCH improved by {touch_improved} instances")
    else:
        print(f"[WARN] TOUCH only improved by {touch_improved} instances (target: >5)")

    # Check if we now have n>=15 for underpowered modalities
    touch_recipes = modality_recipe_counts['TOUCH']
    smell_recipes = modality_recipe_counts['SMELL']

    print()
    print("Recipe-level sample sizes:")
    print(f"  TOUCH: {touch_recipes} recipes (target: >=15)")
    print(f"  SMELL: {smell_recipes} recipes (target: >=15)")

    if touch_recipes >= 15:
        print("  [PASS] TOUCH has adequate sample size")
    else:
        print(f"  [WARN] TOUCH underpowered ({touch_recipes} < 15)")

    if smell_recipes >= 15:
        print("  [PASS] SMELL has adequate sample size")
    else:
        print(f"  [WARN] SMELL underpowered ({smell_recipes} < 15)")

if __name__ == '__main__':
    main()
