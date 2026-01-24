#!/usr/bin/env python3
"""Check if instruction sequence extraction is correct."""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Count sequence patterns
from collections import Counter
seq_counter = Counter()
no_seq = []
generic_examples = []

for r in data['recipes']:
    seq = r.get('instruction_sequence')
    proc = r.get('procedure_summary', '')
    has_proc = r.get('has_procedure', False)

    if seq is None or seq == []:
        no_seq.append((r['id'], r['name_german'], has_proc, proc[:100] if proc else 'NO PROCEDURE'))
        seq_counter['NO_SEQUENCE'] += 1
    else:
        seq_tuple = tuple(seq)
        seq_counter[seq_tuple] += 1

        # Collect examples of generic [AUX, e_ESCAPE]
        if seq == ['AUX', 'e_ESCAPE'] and len(generic_examples) < 10:
            generic_examples.append({
                'id': r['id'],
                'name': r['name_german'],
                'english': r['name_english'],
                'procedure': proc[:200] if proc else 'NO PROCEDURE'
            })

print("=" * 70)
print("INSTRUCTION SEQUENCE ANALYSIS")
print("=" * 70)
print()

print(f"Total recipes: {len(data['recipes'])}")
print(f"Recipes with has_procedure=True: {sum(1 for r in data['recipes'] if r.get('has_procedure'))}")
print()

print("Sequence distribution:")
for seq, count in seq_counter.most_common():
    print(f"  {list(seq) if isinstance(seq, tuple) else seq}: {count}")
print()

print("=" * 70)
print("RECIPES WITHOUT INSTRUCTION SEQUENCE")
print("=" * 70)
for id_, name, has_proc, proc in no_seq[:20]:
    print(f"#{id_:3d} {name:25s} has_procedure={has_proc}")
    print(f"     {proc}...")
    print()

print()
print("=" * 70)
print("EXAMPLES OF GENERIC [AUX, e_ESCAPE]")
print("=" * 70)
print()
print("Are these procedures really all the same?")
print()

for ex in generic_examples:
    print(f"#{ex['id']} {ex['name']} ({ex['english']})")
    print(f"   Procedure: {ex['procedure']}")
    print()

# Now let's look at the actual procedure text diversity
print("=" * 70)
print("PROCEDURE TEXT ANALYSIS")
print("=" * 70)
print()

# Check for keywords that might indicate different instruction types
keywords = {
    'balneum': 0,  # water bath = k_ENERGY
    'feuer': 0,    # fire = k_ENERGY
    'warm': 0,     # warm = k_ENERGY
    'kalt': 0,     # cold = e_ESCAPE related
    'gieß': 0,     # pour = FLOW
    'schütt': 0,   # pour = FLOW
    'wart': 0,     # wait = LINK
    'tag': 0,      # day (time) = LINK
    'stund': 0,    # hour = LINK
    'nacht': 0,    # night = LINK
    'gefahr': 0,   # danger = h_HAZARD
    'gift': 0,     # poison = h_HAZARD
    'dung': 0,     # dung = h_HAZARD (fermentation)
    'mist': 0,     # manure = h_HAZARD
    'rectific': 0, # rectify = e_ESCAPE
    'redistill': 0, # redistill = k_ENERGY
}

generic_procs = [r for r in data['recipes']
                 if r.get('instruction_sequence') == ['AUX', 'e_ESCAPE']]

for r in generic_procs:
    proc = (r.get('procedure_summary', '') or '').lower()
    for kw in keywords:
        if kw in proc:
            keywords[kw] += 1

print(f"Keyword frequency in {len(generic_procs)} 'generic' [AUX, e_ESCAPE] recipes:")
print()
for kw, count in sorted(keywords.items(), key=lambda x: -x[1]):
    if count > 0:
        print(f"  '{kw}': {count} recipes ({count/len(generic_procs)*100:.1f}%)")

print()
print("This suggests we may be UNDER-CLASSIFYING instruction types!")
