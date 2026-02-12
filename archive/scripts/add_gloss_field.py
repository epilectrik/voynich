"""
Migration script: Add gloss field to token_dictionary.json

This adds an empty 'gloss' field to every token entry for Tier 3-4
interpretive content. Glosses will be populated incrementally as we
decode folios.

Run once: python scripts/add_gloss_field.py
"""
import json
from pathlib import Path

DICT_PATH = Path(__file__).parent.parent / 'data' / 'token_dictionary.json'

def migrate():
    print(f"Loading {DICT_PATH}...")
    with open(DICT_PATH, 'r', encoding='utf-8') as f:
        d = json.load(f)

    added = 0
    for token, entry in d['tokens'].items():
        if 'gloss' not in entry:
            entry['gloss'] = None
            added += 1

    # Update version
    old_version = d['meta'].get('version', 'unknown')
    d['meta']['version'] = '5.0'
    d['meta']['schema_notes'] = d['meta'].get('schema_notes', '') + ' v5: Added gloss field for Tier 3-4 interpretive content.'

    print(f"Writing updated dictionary...")
    with open(DICT_PATH, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

    print(f"Done. Added gloss field to {added} tokens.")
    print(f"Version: {old_version} -> 5.0")
    print(f"Total tokens: {len(d['tokens'])}")

if __name__ == '__main__':
    migrate()
