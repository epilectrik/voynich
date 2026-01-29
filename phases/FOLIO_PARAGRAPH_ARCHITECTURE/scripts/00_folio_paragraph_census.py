"""
00_folio_paragraph_census.py - GATE: Build folio-paragraph mappings

Creates comprehensive folio→paragraph mappings with derived metrics.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load paragraph inventory from previous phase
    par_results = Path(__file__).resolve().parents[2] / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'

    with open(par_results / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Load class map for MIDDLE extraction
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    # Section definitions (from C552)
    def get_section(folio):
        num = int(''.join(c for c in folio if c.isdigit()))
        if 74 <= num <= 84:
            return 'BIO'
        elif 26 <= num <= 56:
            return 'HERBAL_B'
        elif 57 <= num <= 67:
            return 'PHARMA'
        elif num >= 103:
            return 'RECIPE_B'
        else:
            return 'OTHER'

    # Build folio census
    folio_data = defaultdict(lambda: {
        'paragraphs': [],
        'total_tokens': 0,
        'total_lines': 0,
        'all_middles': set()
    })

    for par in inventory['paragraphs']:
        folio = par['folio']
        par_id = par['par_id']
        tokens = tokens_by_par.get(par_id, [])

        # Extract MIDDLEs from tokens
        par_middles = set()
        valid_tokens = 0
        for t in tokens:
            word = t['word']
            if word and '*' not in word:
                valid_tokens += 1
                # Simple MIDDLE extraction (word minus common prefixes/suffixes)
                par_middles.add(word)

        par_info = {
            'par_id': par_id,
            'lines': len(par['lines']),
            'tokens': valid_tokens,
            'unique_words': len(par_middles)
        }

        folio_data[folio]['paragraphs'].append(par_info)
        folio_data[folio]['total_tokens'] += valid_tokens
        folio_data[folio]['total_lines'] += len(par['lines'])
        folio_data[folio]['all_middles'] |= par_middles

    # Build output
    census = []
    for folio in sorted(folio_data.keys()):
        data = folio_data[folio]
        entry = {
            'folio': folio,
            'section': get_section(folio),
            'paragraph_count': len(data['paragraphs']),
            'total_tokens': data['total_tokens'],
            'total_lines': data['total_lines'],
            'unique_words': len(data['all_middles']),
            'paragraphs': data['paragraphs']
        }
        census.append(entry)

    # Summary stats
    total_folios = len(census)
    total_pars = sum(e['paragraph_count'] for e in census)

    print("=== FOLIO-PARAGRAPH CENSUS ===\n")
    print(f"Total B folios: {total_folios}")
    print(f"Total paragraphs: {total_pars}")
    print(f"Mean paragraphs per folio: {total_pars/total_folios:.1f}")

    # Distribution
    par_counts = [e['paragraph_count'] for e in census]
    print(f"\nParagraph count distribution:")
    print(f"  Min: {min(par_counts)}, Max: {max(par_counts)}")
    print(f"  Median: {sorted(par_counts)[len(par_counts)//2]}")

    # By section
    print(f"\nBy section:")
    by_section = defaultdict(list)
    for e in census:
        by_section[e['section']].append(e['paragraph_count'])

    for section in sorted(by_section.keys()):
        counts = by_section[section]
        print(f"  {section}: {len(counts)} folios, mean {sum(counts)/len(counts):.1f} pars/folio")

    # Save
    output = {
        'summary': {
            'total_folios': total_folios,
            'total_paragraphs': total_pars,
            'mean_pars_per_folio': total_pars / total_folios
        },
        'folios': census
    }

    with open(results_dir / 'folio_paragraph_census.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to folio_paragraph_census.json")

if __name__ == '__main__':
    main()
