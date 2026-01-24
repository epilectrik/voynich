#!/usr/bin/env python3
"""Find recipes that are likely misclassified as generic [AUX, e_ESCAPE]."""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Instruction type keywords
INSTRUCTION_KEYWORDS = {
    'k_ENERGY': ['balneum', 'balneo', 'warm', 'feuer', 'fire', 'heat', 'hitz', 'sied', 'koch',
                 'redistill', 'rectific'],
    'FLOW': ['gieß', 'schütt', 'pour', 'collect', 'samm', 'nimm', 'setz'],
    'h_HAZARD': ['dung', 'mist', 'horse', 'pferd', 'buried', 'vergrab', 'ferment',
                 'gefahr', 'gift', 'poison'],
    'LINK': ['tag', 'day', 'stund', 'hour', 'woch', 'week', 'nacht', 'night',
             'wart', 'wait', 'beobacht', 'watch']
}

print("=" * 70)
print("MISCLASSIFIED RECIPE ANALYSIS")
print("=" * 70)
print()

generic_recipes = [r for r in data['recipes']
                   if r.get('instruction_sequence') == ['AUX', 'e_ESCAPE']]

print(f"Total generic [AUX, e_ESCAPE] recipes: {len(generic_recipes)}")
print()

# Find recipes that should have additional instruction types
misclassified = []

for r in generic_recipes:
    proc = (r.get('procedure_summary', '') or '').lower()
    if not proc:
        continue

    found_types = []
    for inst_type, keywords in INSTRUCTION_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in proc:
                found_types.append((inst_type, kw))
                break  # Only count each type once

    if found_types:
        misclassified.append({
            'id': r['id'],
            'name': r['name_german'],
            'english': r['name_english'],
            'procedure': proc,
            'missing_types': found_types,
            'current_seq': r.get('instruction_sequence')
        })

print(f"Recipes with additional instruction keywords: {len(misclassified)}")
print()

print("=" * 70)
print("DETAILED MISCLASSIFICATION LIST")
print("=" * 70)
print()

for m in misclassified:
    print(f"#{m['id']} {m['name']} ({m['english']})")
    print(f"   Current: {m['current_seq']}")
    print(f"   Missing: {[t for t, kw in m['missing_types']]}")
    print(f"   Keywords found: {[(t, kw) for t, kw in m['missing_types']]}")
    print(f"   Procedure: {m['procedure'][:300]}...")
    print()

# Summary
print("=" * 70)
print("SUMMARY BY MISSING TYPE")
print("=" * 70)
print()

from collections import Counter
type_counts = Counter()
for m in misclassified:
    for t, kw in m['missing_types']:
        type_counts[t] += 1

for t, count in type_counts.most_common():
    print(f"  {t}: {count} recipes should have this added")

print()
print(f"Total recipes needing reclassification: {len(misclassified)}")
print(f"This would reduce generic [AUX, e_ESCAPE] from {len(generic_recipes)} to {len(generic_recipes) - len(misclassified)}")
