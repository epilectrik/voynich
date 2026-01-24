#!/usr/bin/env python3
"""
Add sensory modality field to curated Brunschwig JSON.

Searches german_text in procedural_steps for sensory keywords,
assigns dominant modality to each recipe.
"""

import json
import re
from collections import Counter
from pathlib import Path

# Sensory keyword patterns (from enhanced_sensory_extraction.py)
SENSORY_KEYWORDS = {
    'SIGHT': [
        'farb', 'color', 'sieh', 'schau', 'blick', 'erschein',
        'rot', 'gelb', 'weiß', 'weiss', 'schwarz', 'grün', 'blau', 'braun',
        'klar', 'trüb', 'hell', 'dunkel', 'licht',
        'zeich', 'merk', 'erkenn',
        'verfärb', 'absatz', 'ausschlag', 'trübung', 'belag',
        'schaum', 'glanz', 'durchsichtig', 'ölfleck', 'übergang'
    ],
    'SMELL': [
        'riech', 'geruch', 'duft', 'stink', 'dampf',
        'rauch', 'dunst', 'arom',
        'verdampf', 'verflüchtig', 'qualm', 'dünstung', 'brand',
        'balsamisch', 'würzig', 'muffig', 'verfault', 'geruchlos',
        'ausdünst', 'ausgasung'
    ],
    'SOUND': [
        'hör', 'laut', 'still', 'sied', 'wall', 'brodel',
        'zisch', 'knack', 'knister', 'rausch',
        'gurgel', 'blubb', 'pfeif', 'spritz'
    ],
    'TOUCH': [
        'fühl', 'warm', 'kalt', 'heiß', 'heiss', 'kühl',
        'weich', 'hart', 'feucht', 'trocken',
        'temperatur', 'grad',
        'wallend', 'erkalt', 'erkalten', 'abkühlung',
        'dickflüssig', 'dünnflüssig', 'kristallin', 'ölig',
        'gelatinös', 'schlammig', 'körnig', 'pulverig',
        'siedhitze', 'gluthitze'
    ],
    'TASTE': [
        'schmeck', 'geschmack', 'süß', 'suess', 'bitter', 'sauer',
        'salz', 'scharf',
        'kostversuch', 'prob', 'zung', 'laugen'
    ]
}

def extract_sensory_from_text(text):
    """Extract sensory modality counts from German text."""
    if not text:
        return Counter()

    text_lower = text.lower()
    counts = Counter()

    for modality, keywords in SENSORY_KEYWORDS.items():
        for keyword in keywords:
            # Count occurrences of keyword
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            matches = pattern.findall(text_lower)
            counts[modality] += len(matches)

    return counts

def analyze_recipe(recipe):
    """Analyze a recipe for sensory modalities."""
    total_counts = Counter()
    step_details = []

    # Get procedural steps
    steps = recipe.get('procedural_steps') or []

    for step in steps:
        german_text = step.get('german_text', '')
        notes = step.get('notes', '')

        # Combine text sources
        combined = f"{german_text} {notes}"

        step_counts = extract_sensory_from_text(combined)
        total_counts += step_counts

        if step_counts:
            step_details.append({
                'step': step.get('step'),
                'action': step.get('action'),
                'sensory_hits': dict(step_counts)
            })

    # Determine dominant modality
    if total_counts:
        dominant = total_counts.most_common(1)[0][0]
        dominant_count = total_counts.most_common(1)[0][1]
    else:
        dominant = None
        dominant_count = 0

    return {
        'sensory_counts': dict(total_counts),
        'dominant_modality': dominant,
        'total_sensory_hits': sum(total_counts.values()),
        'step_details': step_details if step_details else None
    }

def main():
    # Load curated data
    input_path = Path('data/brunschwig_curated_v2.json')
    with open(input_path, encoding='utf-8') as f:
        data = json.load(f)

    print(f"Processing {len(data['recipes'])} recipes...")

    # Track statistics
    modality_counts = Counter()

    # Process each recipe
    for recipe in data['recipes']:
        sensory_info = analyze_recipe(recipe)

        # Add sensory fields to recipe
        recipe['sensory_modality'] = sensory_info['dominant_modality']
        recipe['sensory_counts'] = sensory_info['sensory_counts']
        recipe['sensory_total_hits'] = sensory_info['total_sensory_hits']

        # Track for statistics
        modality_counts[sensory_info['dominant_modality'] or 'NONE'] += 1

    # Update metadata
    data['notes'] = data.get('notes', '') + ' | Sensory modality added via add_sensory_to_brunschwig.py'

    # Save updated data
    output_path = Path('data/brunschwig_curated_v3.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to {output_path}")
    print("\nSensory modality distribution:")
    for modality, count in modality_counts.most_common():
        pct = 100 * count / len(data['recipes'])
        print(f"  {modality}: {count} ({pct:.1f}%)")

    # Show some examples
    print("\nSample recipes with sensory data:")
    for recipe in data['recipes'][:5]:
        name = recipe.get('name_english', recipe.get('id'))
        mod = recipe.get('sensory_modality', 'NONE')
        counts = recipe.get('sensory_counts', {})
        print(f"  {name}: {mod} {counts}")

if __name__ == '__main__':
    main()
