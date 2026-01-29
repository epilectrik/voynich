"""
00_section_census.py - GATE: Section-level census

Why does PHARMA have 40% HT vs BIO 22%?
Build comprehensive section profiles to understand structural differences.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

def get_section(folio):
    """Classify folio into section."""
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
    results_dir.mkdir(parents=True, exist_ok=True)

    # Load class map
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    # Load B paragraph tokens
    par_results = Path(__file__).resolve().parents[3] / 'phases' / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Load paragraph inventory
    with open(par_results / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    par_to_info = {p['par_id']: p for p in inventory['paragraphs']}

    # Load folio census
    folio_census_path = Path(__file__).resolve().parents[3] / 'phases' / 'FOLIO_PARAGRAPH_ARCHITECTURE' / 'results' / 'folio_paragraph_census.json'
    with open(folio_census_path) as f:
        folio_census = json.load(f)

    print("=== SECTION CENSUS ===\n")

    # Build section profiles
    sections = defaultdict(lambda: {
        'folios': [],
        'paragraphs': 0,
        'tokens': 0,
        'ht_tokens': 0,
        'unique_words': set(),
        'unique_ht': set(),
        'classes': Counter(),
        'roles': Counter(),
        'lines': 0
    })

    # Role mapping from BCSC
    CLASS_TO_ROLE = {}
    for c in [10, 11, 12, 17]:
        CLASS_TO_ROLE[c] = 'CC'
    for c in [8] + list(range(31, 38)) + [39] + list(range(41, 50)):
        CLASS_TO_ROLE[c] = 'EN'
    for c in [1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29]:
        CLASS_TO_ROLE[c] = 'AX'
    for c in [9, 13, 14, 23]:
        CLASS_TO_ROLE[c] = 'FQ'
    for c in [7, 30, 38, 40]:
        CLASS_TO_ROLE[c] = 'FL'

    # Process each paragraph
    for par_id, tokens in tokens_by_par.items():
        par_info = par_to_info.get(par_id, {})
        folio = par_info.get('folio', 'unknown')
        section = get_section(folio)

        if folio not in sections[section]['folios']:
            sections[section]['folios'].append(folio)

        sections[section]['paragraphs'] += 1
        sections[section]['lines'] += len(par_info.get('lines', []))

        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue

            sections[section]['tokens'] += 1
            sections[section]['unique_words'].add(word)

            if word in class_map:
                cls = class_map[word]
                sections[section]['classes'][cls] += 1
                role = CLASS_TO_ROLE.get(cls, 'UNKNOWN')
                sections[section]['roles'][role] += 1
            else:
                sections[section]['ht_tokens'] += 1
                sections[section]['unique_ht'].add(word)
                sections[section]['roles']['HT'] += 1

    # === 1. BASIC STATISTICS ===
    print("--- 1. BASIC STATISTICS ---\n")

    print(f"{'Section':<12} {'Folios':>8} {'Pars':>8} {'Lines':>8} {'Tokens':>10} {'Unique':>10}")
    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B', 'OTHER']:
        s = sections[section]
        print(f"{section:<12} {len(s['folios']):>8} {s['paragraphs']:>8} {s['lines']:>8} {s['tokens']:>10} {len(s['unique_words']):>10}")

    # === 2. HT RATES ===
    print("\n--- 2. HT RATES BY SECTION ---\n")

    print(f"{'Section':<12} {'HT Rate':>10} {'HT Tokens':>12} {'Unique HT':>12} {'HT/Folio':>12}")
    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B', 'OTHER']:
        s = sections[section]
        ht_rate = s['ht_tokens'] / s['tokens'] if s['tokens'] > 0 else 0
        ht_per_folio = s['ht_tokens'] / len(s['folios']) if s['folios'] else 0
        print(f"{section:<12} {ht_rate:>10.1%} {s['ht_tokens']:>12} {len(s['unique_ht']):>12} {ht_per_folio:>12.1f}")

    # === 3. ROLE DISTRIBUTIONS ===
    print("\n--- 3. ROLE DISTRIBUTIONS ---\n")

    print(f"{'Section':<12} {'EN':>8} {'AX':>8} {'FQ':>8} {'CC':>8} {'FL':>8} {'HT':>8}")
    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B', 'OTHER']:
        s = sections[section]
        total = s['tokens']
        roles = s['roles']
        print(f"{section:<12} {roles['EN']/total:>8.1%} {roles['AX']/total:>8.1%} {roles['FQ']/total:>8.1%} {roles['CC']/total:>8.1%} {roles['FL']/total:>8.1%} {roles['HT']/total:>8.1%}")

    # === 4. TOKENS PER STRUCTURE ===
    print("\n--- 4. STRUCTURAL METRICS ---\n")

    print(f"{'Section':<12} {'Tok/Par':>10} {'Tok/Line':>10} {'Tok/Folio':>12} {'Par/Folio':>10}")
    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B', 'OTHER']:
        s = sections[section]
        tok_per_par = s['tokens'] / s['paragraphs'] if s['paragraphs'] > 0 else 0
        tok_per_line = s['tokens'] / s['lines'] if s['lines'] > 0 else 0
        tok_per_folio = s['tokens'] / len(s['folios']) if s['folios'] else 0
        par_per_folio = s['paragraphs'] / len(s['folios']) if s['folios'] else 0
        print(f"{section:<12} {tok_per_par:>10.1f} {tok_per_line:>10.1f} {tok_per_folio:>12.1f} {par_per_folio:>10.1f}")

    # === 5. VOCABULARY DENSITY ===
    print("\n--- 5. VOCABULARY DENSITY ---\n")

    print(f"{'Section':<12} {'Vocab':>10} {'Type/Token':>12} {'HT Vocab':>10} {'HT T/T':>10}")
    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B', 'OTHER']:
        s = sections[section]
        ttr = len(s['unique_words']) / s['tokens'] if s['tokens'] > 0 else 0
        ht_ttr = len(s['unique_ht']) / s['ht_tokens'] if s['ht_tokens'] > 0 else 0
        print(f"{section:<12} {len(s['unique_words']):>10} {ttr:>12.3f} {len(s['unique_ht']):>10} {ht_ttr:>10.3f}")

    # === 6. CLASS-LEVEL DETAIL ===
    print("\n--- 6. TOP CLASSES BY SECTION ---\n")

    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
        s = sections[section]
        total = sum(s['classes'].values())
        print(f"{section}:")
        for cls, count in s['classes'].most_common(8):
            role = CLASS_TO_ROLE.get(cls, '?')
            print(f"  Class {cls:2} ({role:2}): {count/total:>6.1%} ({count})")
        print()

    # === 7. PHARMA vs BIO COMPARISON ===
    print("--- 7. PHARMA vs BIO DETAILED COMPARISON ---\n")

    pharma = sections['PHARMA']
    bio = sections['BIO']

    print(f"{'Metric':<25} {'PHARMA':>12} {'BIO':>12} {'Ratio':>10}")

    # Basic
    print(f"{'Folios':<25} {len(pharma['folios']):>12} {len(bio['folios']):>12} {len(pharma['folios'])/len(bio['folios']):>10.2f}")
    print(f"{'Tokens':<25} {pharma['tokens']:>12} {bio['tokens']:>12} {pharma['tokens']/bio['tokens']:>10.2f}")
    print(f"{'Tokens per folio':<25} {pharma['tokens']/len(pharma['folios']):>12.1f} {bio['tokens']/len(bio['folios']):>12.1f} {(pharma['tokens']/len(pharma['folios']))/(bio['tokens']/len(bio['folios'])):>10.2f}")

    # HT
    pharma_ht_rate = pharma['ht_tokens'] / pharma['tokens']
    bio_ht_rate = bio['ht_tokens'] / bio['tokens']
    print(f"{'HT rate':<25} {pharma_ht_rate:>12.1%} {bio_ht_rate:>12.1%} {pharma_ht_rate/bio_ht_rate:>10.2f}")

    # Roles
    for role in ['EN', 'AX', 'FQ', 'CC', 'FL']:
        p_rate = pharma['roles'][role] / pharma['tokens']
        b_rate = bio['roles'][role] / bio['tokens']
        ratio = p_rate / b_rate if b_rate > 0 else 0
        print(f"{role + ' rate':<25} {p_rate:>12.1%} {b_rate:>12.1%} {ratio:>10.2f}")

    # === VERDICT ===
    print("\n=== VERDICT ===\n")

    # Find most and least HT-rich
    ht_rates = [(s, sections[s]['ht_tokens']/sections[s]['tokens'])
                for s in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B', 'OTHER']
                if sections[s]['tokens'] > 0]
    ht_rates.sort(key=lambda x: x[1], reverse=True)

    print(f"Most HT-rich: {ht_rates[0][0]} ({ht_rates[0][1]:.1%})")
    print(f"Least HT-rich: {ht_rates[-1][0]} ({ht_rates[-1][1]:.1%})")
    print(f"HT range: {ht_rates[0][1] - ht_rates[-1][1]:.1%} ({ht_rates[0][1]/ht_rates[-1][1]:.2f}x)")

    # Save
    output = {
        'sections': {
            section: {
                'folios': s['folios'],
                'paragraphs': s['paragraphs'],
                'lines': s['lines'],
                'tokens': s['tokens'],
                'ht_tokens': s['ht_tokens'],
                'ht_rate': s['ht_tokens'] / s['tokens'] if s['tokens'] > 0 else 0,
                'unique_words': len(s['unique_words']),
                'unique_ht': len(s['unique_ht']),
                'roles': dict(s['roles']),
                'classes': dict(s['classes'].most_common(20))
            }
            for section, s in sections.items()
        }
    }

    with open(results_dir / 'section_census.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to section_census.json")

if __name__ == '__main__':
    main()
