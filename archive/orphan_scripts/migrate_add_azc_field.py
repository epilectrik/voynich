#!/usr/bin/env python3
"""
Migrate token_dictionary.json to add AZC position fields.

This script:
1. Loads existing token_dictionary.json (preserving all notes)
2. Adds empty 'azc' field structure to all tokens
3. Pre-populates AZC positions from transcript for AZC tokens
4. Updates meta version

Run once to migrate existing dictionary.
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
DICT_PATH = PROJECT_ROOT / 'data' / 'token_dictionary.json'
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'


def collect_azc_positions():
    """Collect AZC positions from transcript."""
    positions = defaultdict(lambda: {
        'positions': set(),
        'by_folio': defaultdict(set)
    })

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            # Filter to H transcriber
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            word = row.get('word', '').strip()
            if not word:
                continue

            language = row.get('language', '').strip()
            folio = row.get('folio', '').strip()
            placement = row.get('placement', '').strip()

            # Only process AZC tokens (language=NA)
            if language == 'NA' and placement and not placement.startswith('L'):
                positions[word]['positions'].add(placement)
                if folio:
                    positions[word]['by_folio'][folio].add(placement)

    return positions


def migrate():
    """Add AZC fields to existing dictionary."""
    print("Loading existing token dictionary...")
    with open(DICT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Found {len(data['tokens'])} tokens")

    # Collect AZC positions from transcript
    print("Collecting AZC positions from transcript...")
    azc_positions = collect_azc_positions()
    print(f"Found AZC position data for {len(azc_positions)} tokens")

    # Track changes
    added_empty = 0
    added_with_data = 0

    for word, entry in data['tokens'].items():
        if 'azc' not in entry:
            # Check if we have position data for this token
            if word in azc_positions:
                pos_data = azc_positions[word]
                entry['azc'] = {
                    'positions': sorted(list(pos_data['positions'])),
                    'by_folio': {f: sorted(list(positions))
                                 for f, positions in pos_data['by_folio'].items()}
                }
                added_with_data += 1
            else:
                # Add empty structure
                entry['azc'] = {
                    'positions': [],
                    'by_folio': {}
                }
                added_empty += 1

    # Update meta
    data['meta']['version'] = '4.0'
    data['meta']['schema_notes'] = 'v4: Added azc{positions[], by_folio{}} for AZC diagram positions. v3: locations[], role, notes.'
    data['meta']['migrated'] = datetime.now().strftime('%Y-%m-%d')

    # Save
    print(f"\nSaving migrated dictionary...")
    with open(DICT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"\nMigration complete:")
    print(f"  Tokens with AZC position data: {added_with_data}")
    print(f"  Tokens with empty azc field: {added_empty}")
    print(f"  Total tokens: {len(data['tokens'])}")


if __name__ == '__main__':
    migrate()
