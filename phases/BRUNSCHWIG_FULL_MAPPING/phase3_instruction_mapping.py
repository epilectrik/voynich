#!/usr/bin/env python3
"""
PHASE 3: INSTRUCTION CLASS MAPPING

Translate Brunschwig operations to Voynich 49-class grammar.

Based on C493 (Brunschwig Grammar Embedding), the mapping is:
- AUX (AUXILIARY): Preparation, setup, sealing
- FLOW: Loading, material movement, output
- k (ENERGY): Heat application, energy changes
- h (HAZARD): Phase transitions, hazardous operations
- e (ESCAPE): Cooling, recovery, completion
- LINK: Monitoring, observation, adjustment

Pre-registered mapping rules (defined BEFORE analysis):
| Brunschwig Pattern | Voynich Class |
|-------------------|---------------|
| hack/chop/prepare | AUX |
| load/setup/attach | FLOW |
| seal/close | AUX |
| heat/warm/fire | k (ENERGY) |
| distill/vapor/condense | h (HAZARD) |
| monitor/watch/observe | LINK |
| collect/gather/receive | FLOW |
| cool/reduce/complete | e (ESCAPE) |
| if/when/caution | Recovery sequence |
"""

import re
import json
from pathlib import Path

# ============================================================
# INSTRUCTION CLASS MAPPING RULES
# ============================================================

# These rules are PRE-REGISTERED before analysis
# Based on C493 validated mapping

INSTRUCTION_MAPPING = {
    'AUX': {
        'keywords': [
            'hack', 'schneid', 'zerklein', 'stoß', 'zerstoß',
            'wasch', 'reinig', 'sammel', 'pflück',
            'versieg', 'verschließ', 'verkleb', 'lutier',
            'bereit', 'mach', 'rüst', 'ordne',
            'attach', 'befestig', 'setz auf',
            'pack', 'füll', 'leg ein'
        ],
        'patterns': [
            r'gehackt|gestossen|zerklein',
            r'ge(?:wa|ae)schen',
            r'bereit|vorbereitung',
        ]
    },
    'FLOW': {
        'keywords': [
            'gieß', 'schütt', 'thu', 'leg', 'setz in',
            'nimm', 'fang', 'empfang',
            'laß', 'fließ', 'lauf',
            'sammel', 'behalt', 'bewahr',
            'cucurbit', 'glas', 'gefäß'
        ],
        'patterns': [
            r'in\s+(?:das|den|die|ein)',
            r'darein|darin|hinein',
            r'(?:her)?auß|darauß',
        ]
    },
    'k_ENERGY': {
        'keywords': [
            'feuer', 'feur', 'warm', 'hitz', 'heiz',
            'balneum', 'bad', 'wasserbad',
            'kohl', 'glut', 'brand', 'brenn',
            'sied', 'koch', 'brod',
            'gemach', 'lind', 'sanft', 'gelind',
            'stark', 'heiß', 'groß feuer'
        ],
        'patterns': [
            r'(?:gelind|sanft|lind)(?:em|es|er)?\s+feuer',
            r'(?:stark|groß|heiß)(?:em|es|er)?\s+feuer',
            r'balneum\s+mari[ae]',
            r'(?:warm|hitz|heiz)',
        ]
    },
    'h_HAZARD': {
        'keywords': [
            'distillier', 'destillier', 'brenn',
            'dampf', 'dunst', 'rauch',
            'kondensier', 'niederschlag',
            'übergeh', 'steig', 'aufsteig',
            'siedend', 'wallen', 'brodelnd',
            'giftig', 'gefährlich', 'schädlich'
        ],
        'patterns': [
            r'di[sſ]tillier',
            r'dampff?|dunst',
            r'(?:auf)?steig|über(?:geh|tritt)',
        ]
    },
    'e_ESCAPE': {
        'keywords': [
            'kühl', 'kalt', 'abkühl', 'erkalt',
            'ablösch', 'auslösch',
            'minder', 'verminder', 'reduzier',
            'aufhör', 'end', 'vollend', 'fertig',
            'ruhen', 'stehen', 'absetzen',
            'rectific', 'reinig', 'klär'
        ],
        'patterns': [
            r'(?:ab|er)?(?:kü|ka)lt|kalt',
            r'aufhör|vollend|fertig',
            r'(?:ver)?minder|reduzier',
        ]
    },
    'LINK': {
        'keywords': [
            'wart', 'schau', 'sieh', 'beobacht', 'acht',
            'merk', 'erkenn', 'zeich',
            'farb', 'riech', 'schmeck', 'fühle',
            'prüf', 'test', 'versuch',
            'wann', 'bis', 'sobald', 'wenn erscheint'
        ],
        'patterns': [
            r'wart(?:e|en)?|schau(?:e|en)?',
            r'(?:be)?(?:acht|obacht)',
            r'farb|riech|geruch',
            r'bis\s+(?:das|die|der)',
        ]
    },
    'RECOVERY': {
        'keywords': [
            'wenn', 'so', 'aber', 'falls', 'sofern',
            'hüt', 'vermeide', 'acht geb',
            'gefahr', 'vorsicht', 'warnung',
            'überlauf', 'überkochen', 'spritz',
            'zu viel', 'zu stark', 'zu heiß',
            'nicht', 'niemals', 'kein'
        ],
        'patterns': [
            r'wenn\s+(?:es|das|die|der)',
            r'(?:ver)?meid|hüt(?:e|en)?',
            r'(?:zu\s+)?(?:viel|stark|heiß|lang)',
            r'gefahr|vorsicht|warnung',
        ]
    }
}

# Hazard class mapping (from C109)
HAZARD_MAPPING = {
    'PHASE_ORDERING': ['reihenfolge', 'erst', 'dann', 'vor', 'nach', 'bevor'],
    'COMPOSITION_JUMP': ['misch', 'zusammen', 'verbind', 'vereinig'],
    'CONTAINMENT_TIMING': ['versieg', 'verschließ', 'öffne', 'deckel', 'helm'],
    'RATE_MISMATCH': ['schnell', 'langsam', 'plötzlich', 'allmählich', 'rate'],
    'ENERGY_OVERSHOOT': ['zu heiß', 'überhitz', 'verbrennt', 'zu stark'],
}

# ============================================================
# MAPPING FUNCTIONS
# ============================================================

def normalize_text(text):
    """Normalize early modern German for matching."""
    text = text.lower()
    text = text.replace('ſ', 's')
    text = text.replace('ꝛ', 'r')
    text = text.replace('ů', 'u')
    text = text.replace('ẽ', 'en')
    return text

def map_to_instruction_class(step_text):
    """Map a procedural step to Voynich instruction class."""
    normalized = normalize_text(step_text)

    scores = {cls: 0 for cls in INSTRUCTION_MAPPING.keys()}

    for cls, rules in INSTRUCTION_MAPPING.items():
        # Check keywords
        for kw in rules['keywords']:
            if kw.lower() in normalized:
                scores[cls] += 1

        # Check patterns
        for pattern in rules['patterns']:
            if re.search(pattern, normalized, re.IGNORECASE):
                scores[cls] += 2  # Patterns weight more

    # Return class with highest score, or 'UNKNOWN' if no match
    max_score = max(scores.values())
    if max_score == 0:
        return 'UNKNOWN'

    best_classes = [cls for cls, score in scores.items() if score == max_score]
    return best_classes[0]

def map_to_hazard_class(step_text):
    """Map a step to potential hazard exposure."""
    normalized = normalize_text(step_text)

    for hazard, keywords in HAZARD_MAPPING.items():
        for kw in keywords:
            if kw.lower() in normalized:
                return hazard

    return 'NONE'

def is_intervention_required(step_text, instruction_class):
    """Determine if step requires intervention."""
    # Hazard operations and certain energy operations require intervention
    return instruction_class in ['h_HAZARD', 'RECOVERY']

def is_recovery_permitted(instruction_class):
    """Determine if recovery is permitted from this step."""
    # Recovery is permitted from most states except mid-hazard
    return instruction_class not in ['h_HAZARD']

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("PHASE 3: INSTRUCTION CLASS MAPPING")
print("=" * 70)
print()

# Load materials database
with open('data/brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

materials = data['materials']
print(f"Loaded {len(materials)} materials")

# Count materials with procedures
with_procedures = [m for m in materials if m['procedural_steps']]
print(f"Materials with procedural steps: {len(with_procedures)}")
print()

# ============================================================
# MAP INSTRUCTION CLASSES
# ============================================================

print("=" * 70)
print("MAPPING INSTRUCTION CLASSES")
print("=" * 70)
print()

total_steps = 0
mapped_steps = 0
class_counts = {}

for material in materials:
    for step in material['procedural_steps']:
        total_steps += 1

        # Map to instruction class
        instruction_class = map_to_instruction_class(step['brunschwig_text'])
        step['instruction_class'] = instruction_class

        # Map hazard exposure
        step['hazard_exposure'] = map_to_hazard_class(step['brunschwig_text'])

        # Determine intervention and recovery
        step['intervention_required'] = is_intervention_required(
            step['brunschwig_text'], instruction_class
        )
        step['recovery_permitted'] = is_recovery_permitted(instruction_class)

        # Count
        class_counts[instruction_class] = class_counts.get(instruction_class, 0) + 1
        if instruction_class != 'UNKNOWN':
            mapped_steps += 1

print(f"Total steps processed: {total_steps}")
print(f"Successfully mapped: {mapped_steps} ({100*mapped_steps/total_steps:.1f}%)")
print()

print("Instruction class distribution:")
for cls in ['AUX', 'FLOW', 'k_ENERGY', 'h_HAZARD', 'e_ESCAPE', 'LINK', 'RECOVERY', 'UNKNOWN']:
    count = class_counts.get(cls, 0)
    pct = 100 * count / total_steps if total_steps > 0 else 0
    print(f"  {cls}: {count} ({pct:.1f}%)")

# ============================================================
# COMPUTE SEQUENCES
# ============================================================

print()
print("=" * 70)
print("COMPUTING INSTRUCTION SEQUENCES")
print("=" * 70)
print()

# For each material, create a simplified instruction sequence
for material in materials:
    if material['procedural_steps']:
        sequence = [step['instruction_class'] for step in material['procedural_steps']]
        material['instruction_sequence'] = sequence

        # Simplified sequence (collapse repeats)
        simplified = []
        for cls in sequence:
            if not simplified or simplified[-1] != cls:
                simplified.append(cls)
        material['instruction_sequence_simplified'] = simplified
    else:
        material['instruction_sequence'] = []
        material['instruction_sequence_simplified'] = []

# Find common sequences
sequence_counts = {}
for m in materials:
    if m['instruction_sequence_simplified']:
        seq_str = ' -> '.join(m['instruction_sequence_simplified'])
        sequence_counts[seq_str] = sequence_counts.get(seq_str, 0) + 1

print("Most common instruction sequences:")
for seq, count in sorted(sequence_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"  {count}x: {seq}")

# ============================================================
# HAZARD ANALYSIS
# ============================================================

print()
print("=" * 70)
print("HAZARD EXPOSURE ANALYSIS")
print("=" * 70)
print()

hazard_counts = {}
for m in materials:
    for step in m['procedural_steps']:
        h = step['hazard_exposure']
        hazard_counts[h] = hazard_counts.get(h, 0) + 1

print("Hazard exposure distribution:")
for hazard in ['NONE', 'PHASE_ORDERING', 'COMPOSITION_JUMP', 'CONTAINMENT_TIMING', 'RATE_MISMATCH', 'ENERGY_OVERSHOOT']:
    count = hazard_counts.get(hazard, 0)
    pct = 100 * count / total_steps if total_steps > 0 else 0
    print(f"  {hazard}: {count} ({pct:.1f}%)")

# ============================================================
# SAVE UPDATED DATABASE
# ============================================================

print()
print("=" * 70)
print("SAVING UPDATED DATABASE")
print("=" * 70)
print()

# Update summary
data['summary']['instruction_class_counts'] = class_counts
data['summary']['hazard_counts'] = hazard_counts
data['summary']['mapping_rate'] = mapped_steps / total_steps if total_steps > 0 else 0

# Save
output_path = Path('data/brunschwig_materials_master.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated database saved to {output_path}")

# ============================================================
# SAMPLE OUTPUT
# ============================================================

print()
print("=" * 70)
print("SAMPLE MAPPED PROCEDURES")
print("=" * 70)
print()

# Find materials with good mapping
good_samples = [m for m in materials
                if len(m['procedural_steps']) >= 3
                and 'UNKNOWN' not in m.get('instruction_sequence', [])][:3]

for m in good_samples:
    name = m['name_normalized']
    print(f"Recipe: {m['recipe_id']} ({name})")
    print(f"  Product: {m['predicted_product_type']}")
    print(f"  Sequence: {' -> '.join(m.get('instruction_sequence_simplified', []))}")
    print("  Steps:")
    for step in m['procedural_steps'][:4]:
        cls = step['instruction_class']
        hazard = step['hazard_exposure']
        text = step['brunschwig_text'][:50].replace('\n', ' ')
        print(f"    [{cls}] {text}... (hazard: {hazard})")
    print()
