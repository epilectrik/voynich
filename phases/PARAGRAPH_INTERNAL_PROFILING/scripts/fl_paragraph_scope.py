"""
fl_paragraph_scope.py - Investigate FL scope within/across paragraphs

Questions:
1. Do paragraphs with FL both start and end with FL?
2. Is FL contained within paragraphs or does it span?
3. What's the FL pattern within a paragraph (first line, body, last line)?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# FL classes from BCSC
FL_CLASSES = {7, 30, 38, 40}
HAZARD_FL = {7, 30}
SAFE_FL = {38, 40}

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load class_token_map
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    # Build FL token set
    fl_tokens = {tok for tok, cls in class_map.items() if cls in FL_CLASSES}
    hazard_fl_tokens = {tok for tok, cls in class_map.items() if cls in HAZARD_FL}
    safe_fl_tokens = {tok for tok, cls in class_map.items() if cls in SAFE_FL}

    print(f"FL tokens: {len(fl_tokens)}")
    print(f"  Hazard FL (7, 30): {len(hazard_fl_tokens)}")
    print(f"  Safe FL (38, 40): {len(safe_fl_tokens)}")

    # Load B paragraphs
    with open(results_dir / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    with open(results_dir / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Analyze FL patterns in paragraphs
    stats = {
        'total_pars': 0,
        'pars_with_fl': 0,
        'pars_with_hazard_fl': 0,
        'pars_with_safe_fl': 0,
        'pars_with_both': 0,
        'fl_in_first_line': 0,
        'fl_in_last_line': 0,
        'fl_in_body': 0,
        'hazard_first_safe_last': 0,  # Key pattern: hazard opens, safe closes
        'safe_fl_not_in_last_line': 0,
        'hazard_fl_in_last_line': 0,
    }

    # Track FL position within paragraph
    fl_positions = []  # normalized 0-1

    for par in inventory['paragraphs']:
        par_id = par['par_id']
        tokens = tokens_by_par[par_id]
        lines = par['lines']

        if not lines or not tokens:
            continue

        stats['total_pars'] += 1

        # Get FL tokens per line
        first_line = lines[0]
        last_line = lines[-1] if len(lines) > 1 else first_line

        fl_in_par = []
        fl_by_line = defaultdict(list)

        for i, t in enumerate(tokens):
            word = t['word']
            line = t['line']
            if word and '*' not in word and word in fl_tokens:
                fl_in_par.append({
                    'word': word,
                    'line': line,
                    'pos': i,
                    'is_hazard': word in hazard_fl_tokens,
                    'is_safe': word in safe_fl_tokens
                })
                fl_by_line[line].append(word)
                # Normalized position within paragraph
                fl_positions.append(i / len(tokens))

        if not fl_in_par:
            continue

        stats['pars_with_fl'] += 1

        has_hazard = any(f['is_hazard'] for f in fl_in_par)
        has_safe = any(f['is_safe'] for f in fl_in_par)

        if has_hazard:
            stats['pars_with_hazard_fl'] += 1
        if has_safe:
            stats['pars_with_safe_fl'] += 1
        if has_hazard and has_safe:
            stats['pars_with_both'] += 1

        # Check FL in first/last/body lines
        if first_line in fl_by_line:
            stats['fl_in_first_line'] += 1
        if last_line in fl_by_line and len(lines) > 1:
            stats['fl_in_last_line'] += 1

        body_lines = set(lines) - {first_line, last_line}
        if any(line in fl_by_line for line in body_lines):
            stats['fl_in_body'] += 1

        # Key pattern: hazard FL opens paragraph, safe FL closes it
        first_fl = fl_in_par[0]
        last_fl = fl_in_par[-1]

        if first_fl['is_hazard'] and last_fl['is_safe']:
            stats['hazard_first_safe_last'] += 1

        # Safe FL not in last line?
        safe_tokens = [f for f in fl_in_par if f['is_safe']]
        if safe_tokens:
            safe_not_last = [f for f in safe_tokens if f['line'] != last_line]
            if safe_not_last:
                stats['safe_fl_not_in_last_line'] += 1

        # Hazard FL in last line?
        hazard_tokens = [f for f in fl_in_par if f['is_hazard']]
        if hazard_tokens:
            hazard_in_last = [f for f in hazard_tokens if f['line'] == last_line]
            if hazard_in_last:
                stats['hazard_fl_in_last_line'] += 1

    # Print results
    print("\n=== FL PARAGRAPH SCOPE ANALYSIS ===\n")
    print(f"Total B paragraphs: {stats['total_pars']}")
    print(f"Paragraphs with any FL: {stats['pars_with_fl']} ({stats['pars_with_fl']/stats['total_pars']:.1%})")
    print(f"  With hazard FL (7,30): {stats['pars_with_hazard_fl']}")
    print(f"  With safe FL (38,40): {stats['pars_with_safe_fl']}")
    print(f"  With BOTH hazard and safe: {stats['pars_with_both']} ({stats['pars_with_both']/stats['pars_with_fl']:.1%} of FL paragraphs)")

    print(f"\n--- FL LINE POSITION WITHIN PARAGRAPH ---")
    print(f"FL in first line: {stats['fl_in_first_line']} ({stats['fl_in_first_line']/stats['pars_with_fl']:.1%})")
    print(f"FL in body lines: {stats['fl_in_body']} ({stats['fl_in_body']/stats['pars_with_fl']:.1%})")
    print(f"FL in last line: {stats['fl_in_last_line']} ({stats['fl_in_last_line']/stats['pars_with_fl']:.1%})")

    print(f"\n--- FL OPEN/CLOSE PATTERN ---")
    print(f"Hazard FL first -> Safe FL last: {stats['hazard_first_safe_last']} ({stats['hazard_first_safe_last']/stats['pars_with_both']:.1%} of both-FL paragraphs)" if stats['pars_with_both'] > 0 else "No both-FL paragraphs")
    print(f"Safe FL NOT in last line: {stats['safe_fl_not_in_last_line']} (escape from expected position)")
    print(f"Hazard FL IN last line: {stats['hazard_fl_in_last_line']} (unclosed flow?)")

    # FL position distribution
    if fl_positions:
        import statistics
        print(f"\n--- FL POSITION DISTRIBUTION ---")
        print(f"Mean FL position (normalized): {statistics.mean(fl_positions):.3f}")
        print(f"Median FL position: {statistics.median(fl_positions):.3f}")

        # Quartiles
        fl_positions.sort()
        n = len(fl_positions)
        print(f"Q1: {fl_positions[n//4]:.3f}, Q3: {fl_positions[3*n//4]:.3f}")

    # Cross-paragraph FL continuity?
    print("\n--- CROSS-PARAGRAPH FL CONTINUITY ---")

    # Check adjacent paragraphs in same folio
    folio_pars = defaultdict(list)
    for par in inventory['paragraphs']:
        folio_pars[par['folio']].append(par['par_id'])

    fl_handoff = 0  # Previous par ends with FL, next starts with FL
    fl_to_no_fl = 0  # Previous par ends with FL, next has no FL
    total_adjacent = 0

    for folio, par_ids in folio_pars.items():
        for i in range(len(par_ids) - 1):
            par1_tokens = tokens_by_par[par_ids[i]]
            par2_tokens = tokens_by_par[par_ids[i + 1]]

            if not par1_tokens or not par2_tokens:
                continue

            total_adjacent += 1

            # Last token of par1
            last_words = [t['word'] for t in par1_tokens[-5:] if t['word']]
            last_fl = any(w in fl_tokens for w in last_words)

            # First token of par2
            first_words = [t['word'] for t in par2_tokens[:5] if t['word']]
            first_fl = any(w in fl_tokens for w in first_words)

            if last_fl and first_fl:
                fl_handoff += 1
            elif last_fl and not first_fl:
                fl_to_no_fl += 1

    print(f"Adjacent paragraph pairs: {total_adjacent}")
    print(f"FL handoff (par ends FL, next starts FL): {fl_handoff}")
    print(f"FL terminates (par ends FL, next no FL): {fl_to_no_fl}")

    if fl_handoff + fl_to_no_fl > 0:
        termination_rate = fl_to_no_fl / (fl_handoff + fl_to_no_fl)
        print(f"\nFL termination rate at paragraph boundary: {termination_rate:.1%}")
        if termination_rate > 0.7:
            print("  --> FL appears to be PARAGRAPH-SCOPED (high termination rate)")
        else:
            print("  --> FL may SPAN paragraphs (low termination rate)")

if __name__ == '__main__':
    main()
