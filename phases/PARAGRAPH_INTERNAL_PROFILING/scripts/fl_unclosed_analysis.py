"""
fl_unclosed_analysis.py - What happens with paragraphs that end with hazard FL?

Questions:
1. Do they transition to something specific?
2. What follows hazard FL at paragraph end?
3. Does the next paragraph "inherit" an open flow state?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

FL_CLASSES = {7, 30, 38, 40}
HAZARD_FL = {7, 30}
SAFE_FL = {38, 40}

# Other role classes for comparison
CC_CLASSES = {10, 11, 12, 17}
EN_CLASSES = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}
FQ_CLASSES = {9, 13, 14, 23}

def get_role(cls):
    if cls in CC_CLASSES: return 'CC'
    if cls in EN_CLASSES: return 'EN'
    if cls in FL_CLASSES: return 'FL'
    if cls in FQ_CLASSES: return 'FQ'
    return 'AX'

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load class map
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    hazard_fl_tokens = {tok for tok, cls in class_map.items() if cls in HAZARD_FL}
    safe_fl_tokens = {tok for tok, cls in class_map.items() if cls in SAFE_FL}

    # Load B paragraphs
    with open(results_dir / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    with open(results_dir / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Build folio ordering
    folio_pars = defaultdict(list)
    for par in inventory['paragraphs']:
        folio_pars[par['folio']].append(par['par_id'])

    # Find paragraphs ending with hazard FL
    hazard_endings = []

    for par in inventory['paragraphs']:
        par_id = par['par_id']
        tokens = tokens_by_par[par_id]
        if not tokens:
            continue

        # Check last 3 tokens
        last_tokens = [t for t in tokens[-3:] if t['word'] and '*' not in t['word']]
        for t in last_tokens:
            if t['word'] in hazard_fl_tokens:
                hazard_endings.append({
                    'par_id': par_id,
                    'folio': par['folio'],
                    'last_hazard_token': t['word'],
                    'all_last_tokens': [x['word'] for x in last_tokens]
                })
                break

    print(f"Paragraphs ending with hazard FL: {len(hazard_endings)}")

    # What follows hazard FL endings?
    what_follows_final_token = Counter()
    what_starts_next_paragraph = Counter()
    next_par_has_fl = 0
    next_par_no_fl = 0

    for ending in hazard_endings:
        par_id = ending['par_id']
        folio = ending['folio']

        # Get index in folio
        par_list = folio_pars[folio]
        try:
            idx = par_list.index(par_id)
        except ValueError:
            continue

        # What's the token after the hazard FL in same paragraph?
        tokens = tokens_by_par[par_id]
        for i, t in enumerate(tokens):
            if t['word'] == ending['last_hazard_token']:
                if i + 1 < len(tokens):
                    next_tok = tokens[i + 1]['word']
                    if next_tok and '*' not in next_tok:
                        if next_tok in class_map:
                            role = get_role(class_map[next_tok])
                            what_follows_final_token[role] += 1
                        else:
                            what_follows_final_token['HT'] += 1
                else:
                    what_follows_final_token['END_OF_PAR'] += 1
                break

        # What starts next paragraph?
        if idx + 1 < len(par_list):
            next_par_id = par_list[idx + 1]
            next_tokens = tokens_by_par[next_par_id]
            if next_tokens:
                first_tokens = [t for t in next_tokens[:5] if t['word'] and '*' not in t['word']]
                if first_tokens:
                    first_tok = first_tokens[0]['word']
                    if first_tok in class_map:
                        role = get_role(class_map[first_tok])
                        what_starts_next_paragraph[role] += 1
                    else:
                        what_starts_next_paragraph['HT'] += 1

                    # Does next paragraph have any FL?
                    next_has_fl = any(t['word'] in hazard_fl_tokens or t['word'] in safe_fl_tokens
                                     for t in next_tokens if t['word'])
                    if next_has_fl:
                        next_par_has_fl += 1
                    else:
                        next_par_no_fl += 1

    print("\n--- WHAT FOLLOWS FINAL HAZARD FL TOKEN ---")
    for item, count in what_follows_final_token.most_common():
        print(f"  {item}: {count}")

    print("\n--- WHAT STARTS NEXT PARAGRAPH (after hazard-ending par) ---")
    for item, count in what_starts_next_paragraph.most_common():
        print(f"  {item}: {count}")

    print(f"\n--- NEXT PARAGRAPH FL STATUS ---")
    print(f"  Next par HAS FL: {next_par_has_fl}")
    print(f"  Next par NO FL: {next_par_no_fl}")

    if next_par_has_fl + next_par_no_fl > 0:
        fl_continuation = next_par_has_fl / (next_par_has_fl + next_par_no_fl)
        print(f"  FL continuation rate: {fl_continuation:.1%}")

    # Compare to baseline FL rate
    baseline_fl_rate = 362 / 585  # from previous analysis
    print(f"  Baseline FL rate: {baseline_fl_rate:.1%}")

    if next_par_has_fl + next_par_no_fl > 0:
        if fl_continuation > baseline_fl_rate * 1.2:
            print("  --> ELEVATED: hazard-ending pars followed by FL pars more than baseline")
        elif fl_continuation < baseline_fl_rate * 0.8:
            print("  --> REDUCED: hazard-ending pars NOT followed by FL pars")
        else:
            print("  --> BASELINE: no special relationship")

    # Check if safe FL ever appears in next paragraph's first line
    print("\n--- SAFE FL IN NEXT PARAGRAPH'S FIRST LINE ---")
    safe_in_next_first = 0
    for ending in hazard_endings:
        par_id = ending['par_id']
        folio = ending['folio']
        par_list = folio_pars[folio]
        try:
            idx = par_list.index(par_id)
        except ValueError:
            continue

        if idx + 1 < len(par_list):
            next_par_id = par_list[idx + 1]
            next_tokens = tokens_by_par[next_par_id]
            if next_tokens:
                next_par_info = next((p for p in inventory['paragraphs'] if p['par_id'] == next_par_id), None)
                if next_par_info and next_par_info['lines']:
                    first_line = next_par_info['lines'][0]
                    first_line_tokens = [t for t in next_tokens if t['line'] == first_line]
                    for t in first_line_tokens:
                        if t['word'] in safe_fl_tokens:
                            safe_in_next_first += 1
                            break

    print(f"  Safe FL in next paragraph's first line: {safe_in_next_first}/{len(hazard_endings)}")
    if len(hazard_endings) > 0:
        print(f"  Rate: {safe_in_next_first/len(hazard_endings):.1%}")

if __name__ == '__main__':
    main()
