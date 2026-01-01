#!/usr/bin/env python3
"""
Phase 18, Task 1 Helper: Select 30 Pilot Folios for Visual Correlation Study

Selection criteria:
- Currier A only
- Herbal section (H) only - exclude zodiac, biological, pharmaceutical
- Diverse word counts (10 short, 10 medium, 10 long)
- Diverse heading prefixes
- No prior plant identification assumptions

Output: List of 30 folio IDs with rationale
"""

import json
from collections import Counter

def load_database():
    with open('folio_feature_database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def select_pilot_folios():
    db = load_database()

    # Get all Currier A folios
    a_folios = db['currier_a']

    # Filter for herbal section only (section H)
    # Also accept section "" or missing as potentially herbal
    herbal_folios = []
    section_counts = Counter()

    for folio_id, data in a_folios.items():
        section = data.get('section', 'H')
        section_counts[section] += 1

        # Include only H (herbal) - exclude P, B, S, C, T
        if section == 'H' or section == '':
            word_count = data['text_features']['word_count']
            opening_word = data['text_features']['opening_word']
            opening_prefix = data['text_features']['opening_prefix']
            herbal_folios.append({
                'folio_id': folio_id,
                'section': section,
                'word_count': word_count,
                'opening_word': opening_word,
                'opening_prefix': opening_prefix,
                'heading_candidates': data['text_features'].get('heading_candidates', [])
            })

    print("=" * 70)
    print("Currier A Section Distribution:")
    print("=" * 70)
    for section, count in sorted(section_counts.items()):
        print(f"  Section {section}: {count} folios")

    print(f"\nHerbal folios available: {len(herbal_folios)}")

    # Sort by word count
    herbal_folios.sort(key=lambda x: x['word_count'])

    # Calculate terciles
    n = len(herbal_folios)
    short_cutoff = herbal_folios[n // 3]['word_count']
    long_cutoff = herbal_folios[2 * n // 3]['word_count']

    print(f"\nWord count distribution:")
    print(f"  Min: {herbal_folios[0]['word_count']}")
    print(f"  Short cutoff (33%): {short_cutoff}")
    print(f"  Long cutoff (67%): {long_cutoff}")
    print(f"  Max: {herbal_folios[-1]['word_count']}")

    # Categorize
    short_folios = [f for f in herbal_folios if f['word_count'] <= short_cutoff]
    medium_folios = [f for f in herbal_folios if short_cutoff < f['word_count'] <= long_cutoff]
    long_folios = [f for f in herbal_folios if f['word_count'] > long_cutoff]

    print(f"\n  Short entries (<={short_cutoff} words): {len(short_folios)}")
    print(f"  Medium entries ({short_cutoff+1}-{long_cutoff} words): {len(medium_folios)}")
    print(f"  Long entries (>{long_cutoff} words): {len(long_folios)}")

    # Select 10 from each category, maximizing prefix diversity
    def select_diverse(folios, n, used_prefixes):
        """Select n folios with diverse prefixes."""
        selected = []
        remaining = folios.copy()

        # First pass: prioritize unseen prefixes
        while len(selected) < n and remaining:
            # Find folios with unseen prefix
            for f in remaining:
                if f['opening_prefix'] not in used_prefixes and len(selected) < n:
                    selected.append(f)
                    used_prefixes.add(f['opening_prefix'])
                    remaining.remove(f)
                    break
            else:
                # No unseen prefixes, take any remaining
                if remaining:
                    selected.append(remaining.pop(0))

        return selected

    used_prefixes = set()

    # Select from each category
    selected_short = select_diverse(short_folios, 10, used_prefixes)
    selected_medium = select_diverse(medium_folios, 10, used_prefixes)
    selected_long = select_diverse(long_folios, 10, used_prefixes)

    all_selected = selected_short + selected_medium + selected_long

    print("\n" + "=" * 70)
    print("SELECTED 30 PILOT FOLIOS")
    print("=" * 70)

    print("\n--- SHORT ENTRIES (10) ---")
    for f in selected_short:
        print(f"  {f['folio_id']:10s} | {f['word_count']:3d} words | prefix: {f['opening_prefix']:3s} | {f['opening_word']}")

    print("\n--- MEDIUM ENTRIES (10) ---")
    for f in selected_medium:
        print(f"  {f['folio_id']:10s} | {f['word_count']:3d} words | prefix: {f['opening_prefix']:3s} | {f['opening_word']}")

    print("\n--- LONG ENTRIES (10) ---")
    for f in selected_long:
        print(f"  {f['folio_id']:10s} | {f['word_count']:3d} words | prefix: {f['opening_prefix']:3s} | {f['opening_word']}")

    # Summary statistics
    prefixes = [f['opening_prefix'] for f in all_selected]
    prefix_counts = Counter(prefixes)

    print("\n" + "=" * 70)
    print("PREFIX DIVERSITY")
    print("=" * 70)
    print(f"Unique prefixes: {len(prefix_counts)}")
    for prefix, count in sorted(prefix_counts.items()):
        print(f"  {prefix}: {count}")

    # Export selection
    selection = {
        'pilot_study_folios': [f['folio_id'] for f in all_selected],
        'selection_criteria': {
            'population': 'Currier A',
            'section': 'Herbal (H)',
            'total_available': len(herbal_folios),
            'selected': 30,
            'short_entries': [f['folio_id'] for f in selected_short],
            'medium_entries': [f['folio_id'] for f in selected_medium],
            'long_entries': [f['folio_id'] for f in selected_long],
            'word_count_range': {
                'short_cutoff': short_cutoff,
                'long_cutoff': long_cutoff
            },
            'prefix_diversity': len(prefix_counts)
        },
        'folio_details': all_selected
    }

    with open('pilot_folio_selection.json', 'w', encoding='utf-8') as f:
        json.dump(selection, f, indent=2)

    print(f"\nSelection saved to: pilot_folio_selection.json")

    return all_selected

if __name__ == '__main__':
    select_pilot_folios()
