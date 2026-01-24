#!/usr/bin/env python3
"""Extract a batch of recipes for manual verification."""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

# Get batch range from command line
if len(sys.argv) >= 3:
    start_id = int(sys.argv[1])
    end_id = int(sys.argv[2])
else:
    start_id = 1
    end_id = 10

with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Extracting recipes #{start_id} to #{end_id}")
print("=" * 80)

for r in data['recipes']:
    if start_id <= r['id'] <= end_id:
        print()
        print(f"### #{r['id']} {r['name_german']} ({r.get('name_english', 'N/A')})")
        print(f"**Class**: {r.get('material_class', 'N/A')} | **Fire**: {r.get('fire_degree', 'N/A')}")
        print(f"**Has Procedure**: {r.get('has_procedure', False)}")
        print(f"**Current Sequence**: {r.get('instruction_sequence', [])}")
        print()
        print(f"**Procedure Summary**:")
        proc = r.get('procedure_summary', 'N/A')
        print(f"  {proc}")
        print()

        # Show source lines if available
        src = r.get('source_lines', {})
        if src:
            print(f"**Source**: lines {src.get('start', '?')}-{src.get('end', '?')}")
        print("-" * 80)
