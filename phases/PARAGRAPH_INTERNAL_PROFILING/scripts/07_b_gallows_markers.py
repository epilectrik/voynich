"""
07_b_gallows_markers.py - B Gallows and Marker Prefixes

Metrics per B paragraph:
- first_token, first_char
- is_gallows_initial (p/t/k/f)
- gallows_char
- first_token_prefix
- marker_prefix_present (pch, po, sh)

Expected: 71.5% gallows-initial (C841), pch-/po- = 33.5% (C843)

Depends on: 00_build_paragraph_inventory.py
"""

import json
import sys
from pathlib import Path
from collections import Counter
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Morphology

GALLOWS = {'p', 't', 'k', 'f'}
MARKER_PREFIXES = {'pch', 'po', 'sh'}

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load inventory
    with open(results_dir / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    with open(results_dir / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    morph = Morphology()

    profiles = []
    first_char_counts = Counter()
    prefix_counts = Counter()
    gallows_char_counts = Counter()

    for par in inventory['paragraphs']:
        par_id = par['par_id']
        tokens = tokens_by_par[par_id]

        # Get first valid token
        first_token = None
        for t in tokens:
            if t['word'] and '*' not in t['word']:
                first_token = t['word']
                break

        if not first_token:
            profiles.append({
                'par_id': par_id,
                'folio': par['folio'],
                'section': par['section'],
                'folio_position': par['folio_position'],
                'initiation': {
                    'first_token': None,
                    'first_char': None,
                    'is_gallows_initial': False,
                    'gallows_char': None,
                    'first_token_prefix': None,
                    'marker_prefix_present': False
                }
            })
            continue

        first_char = first_token[0] if first_token else None
        is_gallows = first_char in GALLOWS

        # Extract prefix
        m = morph.extract(first_token)
        prefix = m.prefix or ''

        # Check articulator (might shift first char)
        if m.articulator:
            # Articulated token, check if underlying is gallows
            underlying = first_token[1:] if first_token else ''
            first_char = underlying[0] if underlying else first_char
            is_gallows = first_char in GALLOWS

        gallows_char = first_char if is_gallows else None
        marker_prefix = prefix in MARKER_PREFIXES

        first_char_counts[first_char] += 1
        if prefix:
            prefix_counts[prefix] += 1
        if gallows_char:
            gallows_char_counts[gallows_char] += 1

        profiles.append({
            'par_id': par_id,
            'folio': par['folio'],
            'section': par['section'],
            'folio_position': par['folio_position'],
            'initiation': {
                'first_token': first_token,
                'first_char': first_char,
                'is_gallows_initial': is_gallows,
                'gallows_char': gallows_char,
                'first_token_prefix': prefix if prefix else None,
                'marker_prefix_present': marker_prefix
            }
        })

    # Summary
    gallows_count = sum(1 for p in profiles if p['initiation']['is_gallows_initial'])
    marker_count = sum(1 for p in profiles if p['initiation']['marker_prefix_present'])

    summary = {
        'system': 'B',
        'paragraph_count': len(profiles),
        'gallows_initial': {
            'count': gallows_count,
            'rate': round(gallows_count / len(profiles), 3),
            'expected': 0.715  # C841
        },
        'gallows_char_distribution': dict(gallows_char_counts.most_common()),
        'marker_prefix': {
            'count': marker_count,
            'rate': round(marker_count / len(profiles), 3),
            'expected': 0.335  # C843: pch + po = 33.5%
        },
        'first_char_distribution': dict(first_char_counts.most_common(10)),
        'prefix_distribution': dict(prefix_counts.most_common(15))
    }

    # Print summary
    print("=== B PARAGRAPH GALLOWS AND MARKERS ===\n")
    print(f"Paragraphs: {summary['paragraph_count']}")

    print(f"\nGallows-initial: {gallows_count}/{len(profiles)} ({summary['gallows_initial']['rate']}) - expected {summary['gallows_initial']['expected']}")
    print("Gallows character distribution:")
    for char, count in gallows_char_counts.most_common():
        print(f"  {char}: {count} ({count/gallows_count:.1%})")

    print(f"\nMarker prefix (pch/po/sh): {marker_count}/{len(profiles)} ({summary['marker_prefix']['rate']}) - expected {summary['marker_prefix']['expected']}")

    print("\nFirst character distribution:")
    for char, count in first_char_counts.most_common(10):
        print(f"  {char}: {count} ({count/len(profiles):.1%})")

    print("\nPrefix distribution:")
    for prefix, count in prefix_counts.most_common(10):
        print(f"  {prefix}: {count}")

    # Save
    with open(results_dir / 'b_gallows_markers.json', 'w') as f:
        json.dump({
            'summary': summary,
            'profiles': profiles
        }, f, indent=2)

    print(f"\nSaved to {results_dir}/b_gallows_markers.json")

if __name__ == '__main__':
    main()
