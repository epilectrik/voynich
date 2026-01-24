#!/usr/bin/env python3
"""Extract recipe 201-225 source lines and German text for sensory analysis."""

import json

# Load the curated recipes
with open('data/brunschwig_curated_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

recipes = data['recipes']
target_recipes = [r for r in recipes if 201 <= r['id'] <= 225]

print(f"Found {len(target_recipes)} recipes in range 201-225\n")

# Get line ranges
for r in target_recipes:
    src = r.get('source_lines', {})
    start = src.get('start', 'N/A')
    end = src.get('end', 'N/A')
    proc = r.get('has_procedure', False)
    name = r.get('name_english', 'N/A')
    steps = r.get('procedural_steps', [])
    step_count = len(steps) if steps else 0
    print(f"ID {r['id']:3d}: {name:30s} | lines {start:5}-{end:5} | procedure: {proc} | steps: {step_count}")

# Determine overall line range
starts = [r['source_lines']['start'] for r in target_recipes if r.get('source_lines', {}).get('start')]
ends = [r['source_lines']['end'] for r in target_recipes if r.get('source_lines', {}).get('end')]

if starts and ends:
    min_line = min(starts)
    max_line = max(ends)
    print(f"\nTotal source range: lines {min_line} - {max_line}")
