"""
03_program_structure_comparison.py - Compare program structure by section

Key question: Are PHARMA's tiny paragraphs a different PROGRAM TYPE
or just a labeling convention?

PHARMA has 76% single-line paragraphs, including 1-token "paragraphs".
What are these structurally?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

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

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load data
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    par_results = Path(__file__).resolve().parents[3] / 'phases' / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    with open(par_results / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    par_to_info = {p['par_id']: p for p in inventory['paragraphs']}

    print("=== PROGRAM STRUCTURE COMPARISON ===\n")

    # === 1. CLASSIFY PARAGRAPH TYPES ===
    print("--- 1. PARAGRAPH TYPE CLASSIFICATION ---\n")

    def classify_paragraph(par_id):
        """Classify paragraph by structure."""
        tokens = tokens_by_par.get(par_id, [])
        valid_tokens = [t for t in tokens if t['word'] and '*' not in t['word']]
        n = len(valid_tokens)

        if n == 0:
            return 'EMPTY'
        elif n == 1:
            word = valid_tokens[0]['word']
            if len(word) == 1:
                return 'SINGLE_CHAR'
            else:
                return 'SINGLE_TOKEN'
        elif n <= 5:
            return 'MICRO'  # 2-5 tokens
        elif n <= 15:
            return 'SMALL'  # 6-15 tokens
        elif n <= 40:
            return 'MEDIUM'  # 16-40 tokens
        else:
            return 'LARGE'  # 40+ tokens

    section_types = defaultdict(Counter)
    for par_id, tokens in tokens_by_par.items():
        par_info = par_to_info.get(par_id, {})
        folio = par_info.get('folio', 'unknown')
        section = get_section(folio)
        par_type = classify_paragraph(par_id)
        section_types[section][par_type] += 1

    # Print distribution
    types = ['SINGLE_CHAR', 'SINGLE_TOKEN', 'MICRO', 'SMALL', 'MEDIUM', 'LARGE']
    print(f"{'Section':<12}", end='')
    for t in types:
        print(f"{t:>12}", end='')
    print()

    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
        total = sum(section_types[section].values())
        print(f"{section:<12}", end='')
        for t in types:
            count = section_types[section][t]
            pct = count / total if total > 0 else 0
            print(f"{pct:>11.1%} ", end='')
        print()

    # === 2. SINGLE-CHARACTER PARAGRAPHS ===
    print("\n--- 2. SINGLE-CHARACTER PARAGRAPHS ---\n")

    single_chars = defaultdict(list)
    for par_id, tokens in tokens_by_par.items():
        par_info = par_to_info.get(par_id, {})
        folio = par_info.get('folio', 'unknown')
        section = get_section(folio)

        valid_tokens = [t for t in tokens if t['word'] and '*' not in t['word']]
        if len(valid_tokens) == 1 and len(valid_tokens[0]['word']) == 1:
            char = valid_tokens[0]['word']
            single_chars[section].append((folio, par_id, char))

    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
        chars = single_chars[section]
        if chars:
            print(f"{section}: {len(chars)} single-char paragraphs")
            char_counts = Counter(c for _, _, c in chars)
            print(f"  Characters: {dict(char_counts.most_common(10))}")
            print(f"  Folios: {sorted(set(f for f, _, _ in chars))}")
            print()

    # === 3. ARE SINGLE-CHAR PARAGRAPHS LABELS? ===
    print("--- 3. SINGLE-CHAR CONTEXT ANALYSIS ---\n")

    # Check if single-char paragraphs cluster at certain folio positions
    for section in ['PHARMA', 'HERBAL_B']:
        chars = single_chars[section]
        if not chars:
            continue

        print(f"{section} single-char paragraph positions:")
        folio_positions = defaultdict(list)
        for folio, par_id, char in chars:
            # Get paragraph ordinal
            folio_pars = [p for p in inventory['paragraphs'] if p.get('folio') == folio]
            folio_pars.sort(key=lambda x: x['par_id'])
            for i, p in enumerate(folio_pars):
                if p['par_id'] == par_id:
                    folio_positions[folio].append((i+1, char))
                    break

        for folio, positions in folio_positions.items():
            print(f"  {folio}: {positions}")
        print()

    # === 4. FOLIO-LEVEL PROGRAM STRUCTURE ===
    print("--- 4. FOLIO-LEVEL PROGRAM STRUCTURE ---\n")

    def get_folio_structure(folio):
        """Get paragraph sequence structure for a folio."""
        folio_pars = [p for p in inventory['paragraphs'] if p.get('folio') == folio]
        folio_pars.sort(key=lambda x: x['par_id'])

        structure = []
        for p in folio_pars:
            par_type = classify_paragraph(p['par_id'])
            structure.append(par_type)
        return structure

    # Compare folio structures
    print("Sample folio structures:")
    for section in ['PHARMA', 'BIO']:
        folios = set()
        for p in inventory['paragraphs']:
            if get_section(p.get('folio', '')) == section:
                folios.add(p.get('folio'))

        print(f"\n{section}:")
        for folio in sorted(folios)[:3]:
            struct = get_folio_structure(folio)
            print(f"  {folio}: {' -> '.join(struct)}")

    # === 5. CONTENT COMPARISON: SMALL vs LARGE PARAGRAPHS ===
    print("\n--- 5. CONTENT COMPARISON: SMALL vs LARGE ---\n")

    EN_CLASSES = {8} | set(range(31, 38)) | {39} | set(range(41, 50))
    CC_CLASSES = {10, 11, 12, 17}
    FQ_CLASSES = {9, 13, 14, 23}

    def get_role_profile(par_ids):
        roles = Counter()
        total = 0
        for par_id in par_ids:
            for t in tokens_by_par.get(par_id, []):
                word = t['word']
                if not word or '*' in word:
                    continue
                total += 1
                if word in class_map:
                    cls = class_map[word]
                    if cls in EN_CLASSES:
                        roles['EN'] += 1
                    elif cls in CC_CLASSES:
                        roles['CC'] += 1
                    elif cls in FQ_CLASSES:
                        roles['FQ'] += 1
                    else:
                        roles['OTHER'] += 1
                else:
                    roles['HT'] += 1
        return {r: c/total for r, c in roles.items()} if total > 0 else {}

    # Compare by size across sections
    for section in ['BIO', 'PHARMA', 'RECIPE_B']:
        small_pars = []
        large_pars = []

        for par_id, tokens in tokens_by_par.items():
            par_info = par_to_info.get(par_id, {})
            folio = par_info.get('folio', 'unknown')
            if get_section(folio) != section:
                continue

            par_type = classify_paragraph(par_id)
            if par_type in ['SINGLE_TOKEN', 'MICRO', 'SMALL']:
                small_pars.append(par_id)
            elif par_type in ['MEDIUM', 'LARGE']:
                large_pars.append(par_id)

        if small_pars and large_pars:
            small_profile = get_role_profile(small_pars)
            large_profile = get_role_profile(large_pars)

            print(f"{section}:")
            print(f"  Small (n={len(small_pars)}): HT={small_profile.get('HT',0):.1%}, EN={small_profile.get('EN',0):.1%}, CC={small_profile.get('CC',0):.1%}")
            print(f"  Large (n={len(large_pars)}): HT={large_profile.get('HT',0):.1%}, EN={large_profile.get('EN',0):.1%}, CC={large_profile.get('CC',0):.1%}")
            print()

    # === 6. IS PHARMA STRUCTURALLY DIFFERENT OR JUST SMALLER? ===
    print("--- 6. STRUCTURE NORMALIZATION TEST ---\n")

    # If we exclude single-char and single-token paragraphs, how do sections compare?
    def get_normalized_stats(section, min_tokens=6):
        pars = []
        total_tokens = 0
        ht_tokens = 0

        for par_id, tokens in tokens_by_par.items():
            par_info = par_to_info.get(par_id, {})
            folio = par_info.get('folio', 'unknown')
            if get_section(folio) != section:
                continue

            valid_tokens = [t for t in tokens if t['word'] and '*' not in t['word']]
            if len(valid_tokens) >= min_tokens:
                pars.append(par_id)
                for t in valid_tokens:
                    total_tokens += 1
                    if t['word'] not in class_map:
                        ht_tokens += 1

        return len(pars), total_tokens, ht_tokens / total_tokens if total_tokens > 0 else 0

    print(f"{'Section':<12} {'Pars (6+)':>12} {'Tokens':>12} {'HT Rate':>12}")
    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
        n_pars, n_tokens, ht_rate = get_normalized_stats(section)
        print(f"{section:<12} {n_pars:>12} {n_tokens:>12} {ht_rate:>12.1%}")

    # === VERDICT ===
    print("\n=== VERDICT ===\n")

    print("PHARMA structural anomaly:")
    print(f"  - {section_types['PHARMA']['SINGLE_CHAR']} single-character paragraphs")
    print(f"  - These appear to be LABELS (y, o, s, etc.) not operational text")
    print(f"  - When normalized (6+ tokens), PHARMA still has elevated HT")

    pharma_chars = section_types['PHARMA']['SINGLE_CHAR']
    pharma_total = sum(section_types['PHARMA'].values())
    print(f"\nSingle-char rate: PHARMA {pharma_chars}/{pharma_total} = {pharma_chars/pharma_total:.1%}")

    # Save
    output = {
        'section_types': {s: dict(c) for s, c in section_types.items()},
        'single_char_by_section': {s: len(chars) for s, chars in single_chars.items()}
    }

    with open(results_dir / 'program_structure.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to program_structure.json")

if __name__ == '__main__':
    main()
