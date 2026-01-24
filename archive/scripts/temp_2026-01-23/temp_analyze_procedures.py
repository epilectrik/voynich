#!/usr/bin/env python3
"""Analyze Brunschwig recipe procedures for sensory patterns."""

import json

with open('data/brunschwig_curated_v2.json', encoding='utf-8') as f:
    data = json.load(f)

# Find recipes WITH procedures
with_proc = [r for r in data['recipes'] if r.get('has_procedure')]
without_proc = [r for r in data['recipes'] if not r.get('has_procedure')]

print(f'Recipes with procedures: {len(with_proc)}')
print(f'Recipes without procedures: {len(without_proc)}')

# Show sample procedural steps to understand the German text
print('\n=== Sample procedural German text ===')
for r in with_proc[:20]:
    print(f"\n{r['id']}. {r['name_german']} ({r['name_english']})")
    if r.get('procedural_steps'):
        for s in r['procedural_steps']:
            print(f"  {s['step']}. {s['action']}: {s.get('german_text', 'N/A')}")

# Look for potential sensory keywords in procedural steps
print('\n=== Searching for sensory patterns ===')
sensory_terms = ['farb', 'riech', 'geruch', 'warm', 'kalt', 'heiß', 'sied', 'schmeck',
                 'klar', 'trüb', 'dick', 'dünn', 'sieh', 'schau', 'fühl', 'bis',
                 'erkenn', 'zeich', 'merk']

for r in data['recipes']:
    if not r.get('procedural_steps'):
        continue
    for s in r['procedural_steps']:
        german = s.get('german_text', '').lower()
        notes = s.get('notes', '').lower()
        combined = f"{german} {notes}"

        for term in sensory_terms:
            if term in combined:
                print(f"\nRecipe {r['id']} ({r['name_german']}), step {s['step']}:")
                print(f"  German: {s.get('german_text', '')}")
                print(f"  Notes: {s.get('notes', '')}")
                print(f"  Hit: '{term}'")
                break
