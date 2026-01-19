#!/usr/bin/env python3
"""
SENSORY INPUT ANALYSIS

Check Brunschwig procedures for human sensory monitoring:
- Sight (color, appearance, visual cues)
- Smell (odor, aroma)
- Sound (boiling, hissing)
- Touch (temperature, texture)
- Taste (rarely, but possible)

These map to LINK class in Voynich grammar and potentially
correlate with Human Track (HT) operations.
"""

import json
import re
from collections import defaultdict

# Sensory keyword patterns (early modern German)
SENSORY_PATTERNS = {
    'SIGHT': {
        'keywords': [
            'farb', 'color', 'sieh', 'schau', 'blick', 'erschein',
            'rot', 'gelb', 'weiß', 'schwarz', 'grün', 'blau', 'braun',
            'klar', 'trüb', 'hell', 'dunkel', 'licht',
            'zeich', 'merk', 'erkenn'
        ],
        'patterns': [
            r'(?:wenn|bis|sobald).*(?:farb|erschein|sieh)',
            r'(?:rot|gelb|weiß|schwarz|grün)(?:e|er|es)?',
            r'(?:klar|trüb|hell|dunkel)',
        ]
    },
    'SMELL': {
        'keywords': [
            'riech', 'geruch', 'duft', 'stink', 'dampf',
            'rauch', 'dunst', 'arom'
        ],
        'patterns': [
            r'(?:wenn|bis).*riech',
            r'geruch|duft|stink',
        ]
    },
    'SOUND': {
        'keywords': [
            'hör', 'laut', 'still', 'sied', 'wall', 'brodel',
            'zisch', 'knack', 'knister', 'rausch'
        ],
        'patterns': [
            r'(?:wenn|bis).*(?:sied|wall|brodel)',
            r'(?:zisch|knack|knister)',
        ]
    },
    'TOUCH': {
        'keywords': [
            'fühl', 'warm', 'kalt', 'heiß', 'kühl',
            'weich', 'hart', 'feucht', 'trocken',
            'temperatur', 'grad'
        ],
        'patterns': [
            r'(?:wenn|bis).*(?:warm|kalt|heiß)',
            r'(?:weich|hart|feucht|trocken)',
        ]
    },
    'TASTE': {
        'keywords': [
            'schmeck', 'geschmack', 'süß', 'bitter', 'sauer',
            'salz', 'scharf'
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

def detect_sensory_content(text):
    """Detect sensory modalities in text."""
    normalized = normalize_text(text)
    found = {}

    for modality, rules in SENSORY_PATTERNS.items():
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

# Load data
print("=" * 70)
print("SENSORY INPUT ANALYSIS")
print("=" * 70)
print()

with open('data/brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

materials = data['materials']
print(f"Loaded {len(materials)} materials")
print()

# Analyze all procedural steps
print("=" * 70)
print("ANALYZING SENSORY CONTENT IN PROCEDURES")
print("=" * 70)
print()

total_steps = 0
steps_with_sensory = 0
modality_counts = defaultdict(int)
modality_step_examples = defaultdict(list)

for material in materials:
    for step in material.get('procedural_steps', []):
        total_steps += 1
        text = step.get('brunschwig_text', '')

        sensory = detect_sensory_content(text)
        if sensory:
            steps_with_sensory += 1
            step['sensory_content'] = sensory

            for modality in sensory:
                modality_counts[modality] += 1
                if len(modality_step_examples[modality]) < 3:
                    modality_step_examples[modality].append({
                        'recipe': material['recipe_id'],
                        'text': text[:100]
                    })
        else:
            step['sensory_content'] = {}

print(f"Total procedural steps: {total_steps}")
print(f"Steps with sensory content: {steps_with_sensory} ({100*steps_with_sensory/total_steps:.1f}%)")
print()

print("Sensory modality distribution:")
for modality in ['SIGHT', 'SMELL', 'SOUND', 'TOUCH', 'TASTE']:
    count = modality_counts[modality]
    pct = 100 * count / total_steps if total_steps > 0 else 0
    print(f"  {modality}: {count} steps ({pct:.1f}%)")

# Correlation with LINK class
print()
print("=" * 70)
print("SENSORY vs LINK CLASS CORRELATION")
print("=" * 70)
print()

link_with_sensory = 0
link_without_sensory = 0
sensory_with_link = 0
sensory_without_link = 0

for material in materials:
    for step in material.get('procedural_steps', []):
        is_link = step.get('instruction_class') == 'LINK'
        has_sensory = bool(step.get('sensory_content'))

        if is_link and has_sensory:
            link_with_sensory += 1
        elif is_link and not has_sensory:
            link_without_sensory += 1
        elif not is_link and has_sensory:
            sensory_without_link += 1

total_link = link_with_sensory + link_without_sensory
total_sensory = link_with_sensory + sensory_without_link

print(f"LINK steps total: {total_link}")
print(f"  - with sensory content: {link_with_sensory}")
print(f"  - without sensory content: {link_without_sensory}")
print()
print(f"Steps with sensory content: {total_sensory}")
print(f"  - classified as LINK: {link_with_sensory}")
print(f"  - classified as other: {sensory_without_link}")

if total_link > 0 and total_sensory > 0:
    overlap_pct = 100 * link_with_sensory / min(total_link, total_sensory)
    print()
    print(f"Overlap: {overlap_pct:.1f}% of smaller set")

# Examples by modality
print()
print("=" * 70)
print("EXAMPLES BY SENSORY MODALITY")
print("=" * 70)
print()

for modality in ['SIGHT', 'SMELL', 'SOUND', 'TOUCH', 'TASTE']:
    examples = modality_step_examples[modality]
    if examples:
        print(f"{modality}:")
        for ex in examples:
            # Truncate to avoid Unicode issues
            text = ex['text'].encode('ascii', 'replace').decode('ascii')[:80]
            print(f"  [{ex['recipe']}] {text}...")
        print()

# Sensory by REGIME
print("=" * 70)
print("SENSORY CONTENT BY REGIME")
print("=" * 70)
print()

sensory_by_regime = defaultdict(lambda: defaultdict(int))
total_by_regime = defaultdict(int)

for material in materials:
    regime = material.get('regime_assignment', {}).get('final_regime', 'UNKNOWN')
    for step in material.get('procedural_steps', []):
        total_by_regime[regime] += 1
        for modality in step.get('sensory_content', {}).keys():
            sensory_by_regime[regime][modality] += 1

print("Modality distribution by REGIME:")
print()
print("REGIME     | SIGHT | SMELL | SOUND | TOUCH | TASTE | Total Steps")
print("-" * 70)
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    row = sensory_by_regime[regime]
    total = total_by_regime[regime]
    print(f"{regime:10} | {row['SIGHT']:5d} | {row['SMELL']:5d} | {row['SOUND']:5d} | {row['TOUCH']:5d} | {row['TASTE']:5d} | {total:5d}")

# Save updated data
print()
print("=" * 70)
print("SAVING RESULTS")
print("=" * 70)
print()

data['summary']['sensory_analysis'] = {
    'total_steps': total_steps,
    'steps_with_sensory': steps_with_sensory,
    'modality_counts': dict(modality_counts),
    'sensory_by_regime': {r: dict(v) for r, v in sensory_by_regime.items()}
}

with open('data/brunschwig_materials_master.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Updated database with sensory annotations")
print()

# Anchor assessment
print("=" * 70)
print("SENSORY ANCHOR ASSESSMENT")
print("=" * 70)
print()

if steps_with_sensory / total_steps > 0.1:
    print(f"FINDING: {100*steps_with_sensory/total_steps:.1f}% of steps contain sensory monitoring")
    print()

    # Check if TOUCH dominates (temperature monitoring)
    if modality_counts['TOUCH'] > modality_counts['SIGHT']:
        print("TOUCH (temperature) is the dominant sensory modality")
        print("  -> Consistent with energy monitoring in control systems")
    elif modality_counts['SIGHT'] > modality_counts['TOUCH']:
        print("SIGHT (visual) is the dominant sensory modality")
        print("  -> Consistent with phase/color change monitoring")

    print()
    print("Potential anchor: Human sensory monitoring maps to LINK operations")
    print("  -> Requires validation against Voynich Human Track (HT) patterns")
else:
    print(f"Only {100*steps_with_sensory/total_steps:.1f}% of steps contain sensory content")
    print("  -> Insufficient for sensory anchor claim")
