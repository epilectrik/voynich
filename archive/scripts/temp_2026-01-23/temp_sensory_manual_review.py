#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual review of sensory keywords in context for recipes 201-225.

The goal is to verify whether sensory keywords appear in PROCEDURAL INSTRUCTIONS
(distillation/preparation) vs. merely in USAGE/DESCRIPTION sections.

Conservative rule: Only mark sensory monitoring if the operator must USE that sense
during the PROCEDURE (gathering, preparation, distillation timing).
"""

import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('data/brunschwig_curated_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('sources/brunschwig_1500_text.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

recipes = [r for r in data['recipes'] if 201 <= r['id'] <= 225]

recipe_ranges = {
    201: (18768, 18776),
    202: (18779, 18801),
    203: (18803, 18943),
    204: (18946, 18986),
    205: (18989, 19027),
    206: (19033, 19120),
    207: (19131, 19217),
    208: (19229, 19254),
    209: (19260, 19297),
    210: (19304, 19353),
    211: (19356, 19410),
    212: (19412, 19426),
    213: (19429, 19459),
    214: (19462, 19516),
    215: (19525, 19784),
    216: (19787, 19869),
    217: (19879, 19947),
    218: (19949, 19979),
    219: (19996, 20054),
    220: (20057, 20152),
    221: (20186, 20270),
    222: (20273, 20305),
    223: (20308, 20368),
    224: (20390, 20535),
    225: (20538, 20601),
}

# Key patterns to look for in PROCEDURAL context only
# Look for "Das beste teil vnd zit" section - this is the distillation procedure instruction

for recipe in recipes:
    rid = recipe['id']
    name = recipe.get('name_english', 'N/A')
    has_proc = recipe.get('has_procedure', False)

    start, end = recipe_ranges.get(rid, (0, 0))
    german_text = ''.join(lines[start-1:end]) if start > 0 else ""

    print(f"\n{'='*80}")
    print(f"Recipe {rid}: {name}")
    print(f"Has procedure: {has_proc}")
    print("="*80)

    # Find the procedure section (typically starts with "Das beste teil" or "beſte teil")
    # and ends before the uses section (marked by letters A, B, C...)

    # Print the relevant procedure portion
    proc_match = re.search(r'(Das |Daz |das |beſte|beste).{0,20}(teil|zyt|zit).{0,200}(gebꝛant|bꝛant|distill)', german_text, re.IGNORECASE)

    if proc_match:
        # Get context around the match
        match_start = max(0, proc_match.start() - 50)
        match_end = min(len(german_text), proc_match.end() + 200)
        proc_context = german_text[match_start:match_end]
        print(f"\nPROCEDURE SECTION EXTRACT:")
        print(proc_context.replace('\n', ' ').strip())
    else:
        print("\nNo clear procedure section found")
        # Print first 500 chars for manual review
        print(f"\nFIRST 500 CHARS:")
        print(german_text[:500].replace('\n', ' ').strip())
