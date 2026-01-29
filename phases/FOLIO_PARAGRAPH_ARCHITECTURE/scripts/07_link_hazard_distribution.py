"""
07_link_hazard_distribution.py - How LINK and hazard distribute within paragraphs

LINK = class 29 (monitoring phase marker)
Hazard = FL classes 7, 30
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Class definitions
LINK_CLASS = 29
HAZARD_FL_CLASSES = {7, 30}

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load census
    with open(results_dir / 'folio_paragraph_census.json') as f:
        census = json.load(f)

    # Load paragraph tokens and inventory
    par_results = Path(__file__).resolve().parents[2] / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    with open(par_results / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    # Load class map
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    # Build LINK and hazard token sets
    link_tokens = {tok for tok, cls in class_map.items() if cls == LINK_CLASS}
    hazard_tokens = {tok for tok, cls in class_map.items() if cls in HAZARD_FL_CLASSES}

    print(f"LINK tokens (class 29): {len(link_tokens)}")
    print(f"Hazard FL tokens (7, 30): {len(hazard_tokens)}")

    # Build paragraph info lookup
    par_info_map = {p['par_id']: p for p in inventory['paragraphs']}

    print("\n=== LINK AND HAZARD DISTRIBUTION ===\n")

    # Track by paragraph ordinal
    link_by_ordinal = defaultdict(list)  # ordinal -> [link rates]
    hazard_by_ordinal = defaultdict(list)  # ordinal -> [hazard rates]

    # Track within paragraph (header vs body)
    link_in_header = 0  # First line
    link_in_body = 0    # Other lines
    hazard_in_header = 0
    hazard_in_body = 0

    total_link = 0
    total_hazard = 0

    for folio_entry in census['folios']:
        for i, par_info in enumerate(folio_entry['paragraphs']):
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])
            full_par_info = par_info_map.get(par_id)

            if not tokens or not full_par_info:
                continue

            lines = full_par_info.get('lines', [])
            first_line = lines[0] if lines else None

            link_count = 0
            hazard_count = 0
            total = 0

            for t in tokens:
                word = t['word']
                if not word or '*' in word:
                    continue
                total += 1
                line = t.get('line')

                if word in link_tokens:
                    link_count += 1
                    total_link += 1
                    if line == first_line:
                        link_in_header += 1
                    else:
                        link_in_body += 1

                if word in hazard_tokens:
                    hazard_count += 1
                    total_hazard += 1
                    if line == first_line:
                        hazard_in_header += 1
                    else:
                        hazard_in_body += 1

            ordinal = min(i + 1, 8)
            if total > 0:
                link_by_ordinal[ordinal].append(link_count / total)
                hazard_by_ordinal[ordinal].append(hazard_count / total)

    print("--- LINK RATE BY PARAGRAPH ORDINAL ---")
    for ordinal in sorted(link_by_ordinal.keys()):
        rates = link_by_ordinal[ordinal]
        print(f"  Par {ordinal}: {statistics.mean(rates):.1%} LINK rate (n={len(rates)})")

    print(f"\n--- HAZARD RATE BY PARAGRAPH ORDINAL ---")
    for ordinal in sorted(hazard_by_ordinal.keys()):
        rates = hazard_by_ordinal[ordinal]
        print(f"  Par {ordinal}: {statistics.mean(rates):.1%} hazard rate (n={len(rates)})")

    print(f"\n--- LINK POSITION WITHIN PARAGRAPH ---")
    total_link_positioned = link_in_header + link_in_body
    if total_link_positioned > 0:
        print(f"  Header (line 1): {link_in_header} ({link_in_header/total_link_positioned:.1%})")
        print(f"  Body: {link_in_body} ({link_in_body/total_link_positioned:.1%})")

    print(f"\n--- HAZARD POSITION WITHIN PARAGRAPH ---")
    total_hazard_positioned = hazard_in_header + hazard_in_body
    if total_hazard_positioned > 0:
        print(f"  Header (line 1): {hazard_in_header} ({hazard_in_header/total_hazard_positioned:.1%})")
        print(f"  Body: {hazard_in_body} ({hazard_in_body/total_hazard_positioned:.1%})")

    # Specialization: do certain paragraphs concentrate LINK or hazard?
    print(f"\n--- PARAGRAPH SPECIALIZATION ---")

    link_rates = [statistics.mean(link_by_ordinal[o]) for o in sorted(link_by_ordinal.keys())]
    hazard_rates = [statistics.mean(hazard_by_ordinal[o]) for o in sorted(hazard_by_ordinal.keys())]

    if link_rates:
        link_cv = statistics.stdev(link_rates) / statistics.mean(link_rates) if statistics.mean(link_rates) > 0 else 0
        print(f"LINK rate CV across ordinals: {link_cv:.2f}")
        if link_cv > 0.3:
            print("--> LINK is concentrated in specific paragraph positions")
        else:
            print("--> LINK is evenly distributed across paragraphs")

    if hazard_rates:
        hazard_cv = statistics.stdev(hazard_rates) / statistics.mean(hazard_rates) if statistics.mean(hazard_rates) > 0 else 0
        print(f"Hazard rate CV across ordinals: {hazard_cv:.2f}")
        if hazard_cv > 0.3:
            print("--> Hazard is concentrated in specific paragraph positions")
        else:
            print("--> Hazard is evenly distributed across paragraphs")

    # Save results
    output = {
        'link_by_ordinal': {o: statistics.mean(r) for o, r in link_by_ordinal.items()},
        'hazard_by_ordinal': {o: statistics.mean(r) for o, r in hazard_by_ordinal.items()},
        'link_position': {
            'header': link_in_header,
            'body': link_in_body,
            'header_rate': link_in_header / total_link_positioned if total_link_positioned > 0 else 0
        },
        'hazard_position': {
            'header': hazard_in_header,
            'body': hazard_in_body,
            'header_rate': hazard_in_header / total_hazard_positioned if total_hazard_positioned > 0 else 0
        },
        'specialization': {
            'link_cv': link_cv if link_rates else 0,
            'hazard_cv': hazard_cv if hazard_rates else 0
        }
    }

    with open(results_dir / 'link_hazard_distribution.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to link_hazard_distribution.json")

if __name__ == '__main__':
    main()
