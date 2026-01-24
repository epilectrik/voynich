#!/usr/bin/env python3
"""
Scan all recipes and propose instruction sequence corrections.
Uses refined rules distinguishing harvest timing from procedural steps.
"""

import json
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

# Instruction detection patterns
# REFINED to avoid false positives
INSTRUCTION_PATTERNS = {
    'k_ENERGY': {
        'keywords': ['balneum', 'balneo', 'water bath', 'ventre equino', 'sand bath',
                     'feuer', 'fire', 'hitz', 'heat', 'sied', 'boil', 'koch', 'cook',
                     'glut', 'ember', 'redistill', 'rectif'],
        'description': 'Heat application (water bath, fire, redistillation)'
    },
    'FLOW': {
        # More specific patterns to avoid false positives
        'keywords': ['collected', 'collect from', 'collection', 'samm', 'pour on',
                     'pour it', 'gieß', 'schütt', 'filter', 'filtered',
                     'seih', 'strain', ' sap ', 'saft '],
        'description': 'Collection/transfer operations'
    },
    'h_HAZARD': {
        'keywords': ['dung', 'mist', 'manure', 'horse dung', 'pferd', 'buried',
                     'bury in', 'vergrab', 'ferment', 'rotting', 'ant hill', 'ameisen'],
        'description': 'Hazardous/fermentation procedures'
    },
    'LINK': {
        # ONLY clear procedural waiting - use specific patterns
        'keywords': ['let stand', 'steeped', 'steep', 'soak', 'overnight',
                     '8 days', '14 days', '40 days', '5-6 days', ' days,',
                     'until liquef', 'place in sun'],
        # Exclude patterns that are harvest timing
        'exclude_context': ['end of', 'im end', 'dog days', 'mary day', 'lady day',
                           'when flower', 'wann blüm', 'beginning of', 'anfang',
                           'around may', 'between the two', 'mid-may', 'mid-june',
                           'standard'],
        'description': 'Procedural waiting steps (NOT harvest timing)'
    }
}

def detect_instructions(procedure_text):
    """Detect instruction types from procedure text."""
    if not procedure_text:
        return []

    text_lower = procedure_text.lower()
    detected = set()
    reasons = {}

    for inst_type, config in INSTRUCTION_PATTERNS.items():
        for kw in config['keywords']:
            if kw.lower() in text_lower:
                # Check exclusions for LINK
                if inst_type == 'LINK':
                    excluded = False
                    for exc in config.get('exclude_context', []):
                        if exc.lower() in text_lower:
                            excluded = True
                            break
                    if excluded:
                        continue

                detected.add(inst_type)
                if inst_type not in reasons:
                    reasons[inst_type] = []
                reasons[inst_type].append(kw)

    return detected, reasons

def build_sequence(current_seq, detected):
    """Build corrected sequence maintaining order."""
    # Standard order: AUX -> FLOW -> h_HAZARD -> LINK -> k_ENERGY -> e_ESCAPE
    order = ['AUX', 'FLOW', 'h_HAZARD', 'LINK', 'k_ENERGY', 'e_ESCAPE', 'RECOVERY']

    # Start with current base (usually [AUX, e_ESCAPE])
    base = set(current_seq) if current_seq else {'AUX', 'e_ESCAPE'}

    # Add detected
    all_types = base | detected

    # Order them
    new_seq = [t for t in order if t in all_types]

    return new_seq

# Load data
with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 80)
print("INSTRUCTION SEQUENCE SCAN")
print("=" * 80)
print()

corrections = []
unchanged = 0

for r in data['recipes']:
    proc = r.get('procedure_summary', '') or ''
    current_seq = r.get('instruction_sequence') or []

    if not proc or proc.startswith('NO PROCEDURE') or proc.startswith('OCR'):
        continue

    detected, reasons = detect_instructions(proc)

    if detected:
        # Check if current sequence already has these
        missing = detected - set(current_seq)

        if missing:
            new_seq = build_sequence(current_seq, detected)
            corrections.append({
                'id': r['id'],
                'name': r['name_german'],
                'english': r.get('name_english', ''),
                'old_seq': current_seq,
                'new_seq': new_seq,
                'detected': detected,
                'reasons': reasons,
                'procedure': proc[:200]
            })
        else:
            unchanged += 1
    else:
        unchanged += 1

print(f"Total recipes with procedures: {len([r for r in data['recipes'] if r.get('procedure_summary')])}")
print(f"Unchanged (no new instructions detected): {unchanged}")
print(f"Corrections needed: {len(corrections)}")
print()

# Group by detected type
print("=" * 80)
print("CORRECTIONS BY TYPE")
print("=" * 80)

by_type = {}
for c in corrections:
    for t in c['detected']:
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(c)

for t, items in sorted(by_type.items()):
    print(f"\n### {t} ({len(items)} recipes)")
    print("-" * 40)
    for c in items[:5]:  # Show first 5 of each type
        print(f"#{c['id']} {c['name']}")
        print(f"  Old: {c['old_seq']}")
        print(f"  New: {c['new_seq']}")
        print(f"  Keywords: {c['reasons'].get(t, [])}")
        print(f"  Procedure: {c['procedure'][:100]}...")
        print()
    if len(items) > 5:
        print(f"  ... and {len(items)-5} more")

# Full correction list
print()
print("=" * 80)
print("FULL CORRECTION LIST")
print("=" * 80)
print()

for c in corrections:
    print(f"#{c['id']:3d} {c['name']:30s}: {c['old_seq']} -> {c['new_seq']}")

# Summary
print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print(f"Total corrections needed: {len(corrections)}")
for t, items in sorted(by_type.items()):
    print(f"  {t}: {len(items)} recipes")

# Output as JSON for easy application
output_file = PROJECT_ROOT / 'phases' / 'ANIMAL_PRECISION_CORRELATION' / 'results' / 'sequence_corrections.json'
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'corrections': [{
            'id': c['id'],
            'name': c['name'],
            'old_seq': c['old_seq'],
            'new_seq': c['new_seq'],
            'reasons': {k: list(v) for k, v in c['reasons'].items()}
        } for c in corrections]
    }, f, indent=2, ensure_ascii=False)

print()
print(f"Corrections saved to: {output_file}")
