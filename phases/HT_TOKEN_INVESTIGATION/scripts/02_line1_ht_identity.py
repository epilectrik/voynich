"""
02_line1_ht_identity.py - What IS the Line-1 HT vocabulary?

Key finding from script 01: Line 1 has 47% HT (vs ~27% later).
Line-1 HT is gallows-enriched (ps, pc, po, op prefixes).

Questions:
1. Are Line-1 HT tokens folio-specific or shared?
2. Do they correlate with folio content type?
3. What is their relationship to paragraph gallows?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

def line_to_num(l):
    """Convert line like '4a' to numeric 4."""
    nums = ''.join(c for c in str(l) if c.isdigit())
    return int(nums) if nums else 1

def main():
    results_dir = Path(__file__).parent.parent / 'results'

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

    print("=== LINE-1 HT IDENTITY ===\n")

    # Collect Line-1 HT by folio
    folio_line1_ht = defaultdict(Counter)
    folio_later_ht = defaultdict(Counter)
    folio_line1_total = defaultdict(int)
    folio_later_total = defaultdict(int)

    for par_id, tokens in tokens_by_par.items():
        par_info = par_to_info.get(par_id, {})
        folio = par_info.get('folio', 'unknown')
        lines = par_info.get('lines', [])
        first_line = min(line_to_num(l) for l in lines) if lines else 1

        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue

            line = line_to_num(t.get('line', 1))
            is_ht = word not in class_map

            if line == first_line:
                folio_line1_total[folio] += 1
                if is_ht:
                    folio_line1_ht[folio][word] += 1
            else:
                folio_later_total[folio] += 1
                if is_ht:
                    folio_later_ht[folio][word] += 1

    # === 1. LINE-1 HT FOLIO SPREAD ===
    print("--- 1. LINE-1 HT TOKEN FOLIO SPREAD ---\n")

    all_line1_ht = Counter()
    for folio, ht_counts in folio_line1_ht.items():
        all_line1_ht.update(ht_counts)

    ht_folio_spread = defaultdict(set)
    for folio, ht_counts in folio_line1_ht.items():
        for word in ht_counts:
            ht_folio_spread[word].add(folio)

    spread_dist = Counter(len(folios) for folios in ht_folio_spread.values())

    print("How many folios does each Line-1 HT token appear in?")
    for n_folios in sorted(spread_dist.keys())[:10]:
        count = spread_dist[n_folios]
        pct = count / len(ht_folio_spread)
        print(f"  {n_folios} folio(s): {count} tokens ({pct:.1%})")

    # Highly spread vs singleton
    singletons = sum(1 for w, f in ht_folio_spread.items() if len(f) == 1)
    widespread = sum(1 for w, f in ht_folio_spread.items() if len(f) >= 5)

    print(f"\nSingletons (1 folio only): {singletons} ({singletons/len(ht_folio_spread):.1%})")
    print(f"Widespread (5+ folios): {widespread} ({widespread/len(ht_folio_spread):.1%})")

    # === 2. ARE LINE-1 HT TOKENS THE SAME AS THE PARAGRAPH OPENER? ===
    print("\n--- 2. LINE-1 HT vs PARAGRAPH OPENER ---\n")

    GALLOWS = {'t', 'k', 'p', 'f'}

    gallows_initial_ht = 0
    non_gallows_initial_ht = 0
    line1_is_opener = 0
    line1_not_opener = 0

    for par_id, tokens in tokens_by_par.items():
        par_info = par_to_info.get(par_id, {})
        lines = par_info.get('lines', [])
        first_line = min(line_to_num(l) for l in lines) if lines else 1

        # Get first token (paragraph opener)
        opener = None
        for t in tokens:
            word = t['word']
            if word and '*' not in word:
                opener = word
                break

        # Count Line-1 HT
        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue
            if word in class_map:
                continue  # Only HT

            line = line_to_num(t.get('line', 1))
            if line != first_line:
                continue  # Only Line 1

            if word[0] in GALLOWS:
                gallows_initial_ht += 1
            else:
                non_gallows_initial_ht += 1

            if word == opener:
                line1_is_opener += 1
            else:
                line1_not_opener += 1

    total_line1_ht = gallows_initial_ht + non_gallows_initial_ht
    print(f"Line-1 HT tokens that ARE gallows-initial: {gallows_initial_ht} ({gallows_initial_ht/total_line1_ht:.1%})")
    print(f"Line-1 HT tokens NOT gallows-initial: {non_gallows_initial_ht} ({non_gallows_initial_ht/total_line1_ht:.1%})")

    total_opener_check = line1_is_opener + line1_not_opener
    print(f"\nLine-1 HT that IS the paragraph opener: {line1_is_opener} ({line1_is_opener/total_opener_check:.1%})")
    print(f"Line-1 HT that is NOT the opener: {line1_not_opener} ({line1_not_opener/total_opener_check:.1%})")

    # === 3. LINE-1 HT BY SECTION ===
    print("\n--- 3. LINE-1 HT BY SECTION ---\n")

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

    section_line1_ht = defaultdict(lambda: {'ht': 0, 'total': 0})
    section_later_ht = defaultdict(lambda: {'ht': 0, 'total': 0})

    for folio in folio_line1_total:
        section = get_section(folio)
        section_line1_ht[section]['total'] += folio_line1_total[folio]
        section_line1_ht[section]['ht'] += sum(folio_line1_ht[folio].values())
        section_later_ht[section]['total'] += folio_later_total[folio]
        section_later_ht[section]['ht'] += sum(folio_later_ht[folio].values())

    print(f"{'Section':<12} {'Line-1 HT':>12} {'Later HT':>12} {'L1/Later':>10}")
    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B', 'OTHER']:
        l1 = section_line1_ht[section]
        later = section_later_ht[section]
        l1_rate = l1['ht'] / l1['total'] if l1['total'] > 0 else 0
        later_rate = later['ht'] / later['total'] if later['total'] > 0 else 0
        ratio = l1_rate / later_rate if later_rate > 0 else 0
        print(f"{section:<12} {l1_rate:>12.1%} {later_rate:>12.1%} {ratio:>10.2f}x")

    # === 4. WHAT CHARACTER PATTERNS DOMINATE LINE-1 HT? ===
    print("\n--- 4. LINE-1 HT CHARACTER PATTERNS ---\n")

    def get_pattern(word):
        """Extract initial pattern: gallows, prefix, or articulator."""
        if not word:
            return 'empty'
        if word[0] in GALLOWS:
            return f"G:{word[0]}"  # Gallows initial
        if len(word) >= 2:
            prefix = word[:2]
            if prefix in ['ch', 'sh', 'qo', 'ok', 'ot', 'ol', 'da', 'ct']:
                return f"P:{prefix}"
            # Check if starts with articulator
            if word[0] in ['y', 's', 'd', 'l', 'r', 'a', 'o', 'e', 'i']:
                return f"A:{word[0]}"
        return f"O:{word[:2]}"

    line1_patterns = Counter()
    later_patterns = Counter()

    for par_id, tokens in tokens_by_par.items():
        par_info = par_to_info.get(par_id, {})
        lines = par_info.get('lines', [])
        first_line = min(line_to_num(l) for l in lines) if lines else 1

        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue
            if word in class_map:
                continue  # Only HT

            line = line_to_num(t.get('line', 1))
            pattern = get_pattern(word)

            if line == first_line:
                line1_patterns[pattern] += 1
            else:
                later_patterns[pattern] += 1

    # Compare
    all_patterns = set(line1_patterns.keys()) | set(later_patterns.keys())
    total_l1 = sum(line1_patterns.values())
    total_later = sum(later_patterns.values())

    pattern_comparison = []
    for p in all_patterns:
        l1 = line1_patterns[p]
        later = later_patterns[p]
        if l1 + later >= 20:
            l1_pct = l1 / total_l1
            later_pct = later / total_later
            ratio = l1_pct / later_pct if later_pct > 0 else float('inf')
            pattern_comparison.append((p, l1, later, l1_pct, later_pct, ratio))

    pattern_comparison.sort(key=lambda x: x[5], reverse=True)

    print("Patterns ENRICHED in Line-1 HT:")
    for p, l1, later, l1_pct, later_pct, ratio in pattern_comparison[:15]:
        if ratio > 1.5:
            print(f"  {p:10}: {ratio:>5.1f}x  ({l1:4} L1, {later:4} later)")

    print("\nPatterns DEPLETED in Line-1 HT:")
    for p, l1, later, l1_pct, later_pct, ratio in reversed(pattern_comparison[-10:]):
        if ratio < 0.7:
            print(f"  {p:10}: {ratio:>5.2f}x  ({l1:4} L1, {later:4} later)")

    # === 5. LINE-1 HT TOKENS THAT ARE FOLIO-UNIQUE ===
    print("\n--- 5. LINE-1 HT TOKENS THAT ARE FOLIO-UNIQUE ---\n")

    # Count how many Line-1 HT tokens appear in only one folio's Line 1
    folio_unique_line1_ht = [w for w, folios in ht_folio_spread.items() if len(folios) == 1]

    print(f"Folio-unique Line-1 HT tokens: {len(folio_unique_line1_ht)}")
    print(f"As fraction of all Line-1 HT vocabulary: {len(folio_unique_line1_ht)/len(ht_folio_spread):.1%}")

    # Check if they're also unique to Line 1 (not appearing later)
    line1_only = Counter()
    for par_id, tokens in tokens_by_par.items():
        par_info = par_to_info.get(par_id, {})
        lines = par_info.get('lines', [])
        first_line = min(line_to_num(l) for l in lines) if lines else 1

        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue
            if word in class_map:
                continue

            line = line_to_num(t.get('line', 1))
            if line != first_line:
                if word in folio_unique_line1_ht:
                    line1_only[word] += 1

    truly_line1_only = [w for w in folio_unique_line1_ht if line1_only[w] == 0]
    print(f"\nFolio-unique AND Line-1 only: {len(truly_line1_only)}")
    print(f"These are identification tokens unique to specific folios")

    # === 6. HT TOKENS APPEARING IN MULTIPLE LINE-1s ===
    print("\n--- 6. WIDELY-USED LINE-1 HT TOKENS ---\n")

    widespread_line1_ht = [(w, len(folios)) for w, folios in ht_folio_spread.items() if len(folios) >= 5]
    widespread_line1_ht.sort(key=lambda x: x[1], reverse=True)

    print(f"Line-1 HT tokens appearing in 5+ folios: {len(widespread_line1_ht)}")
    print("\nTop 20 widespread Line-1 HT tokens:")
    for word, n_folios in widespread_line1_ht[:20]:
        print(f"  {word:15}: {n_folios} folios")

    # === VERDICT ===
    print("\n=== VERDICT ===\n")

    print(f"Total unique Line-1 HT vocabulary: {len(ht_folio_spread)}")
    print(f"Folio-singleton rate: {singletons/len(ht_folio_spread):.1%}")
    print(f"Gallows-initial rate: {gallows_initial_ht/total_line1_ht:.1%}")
    print(f"IS-opener rate: {line1_is_opener/total_opener_check:.1%}")

    # Save
    output = {
        'total_line1_ht_vocab': len(ht_folio_spread),
        'folio_singleton_rate': singletons / len(ht_folio_spread),
        'folio_unique_line1_only': len(truly_line1_only),
        'gallows_initial_rate': gallows_initial_ht / total_line1_ht,
        'is_opener_rate': line1_is_opener / total_opener_check,
        'widespread_line1_ht': dict(widespread_line1_ht[:30])
    }

    with open(results_dir / 'line1_ht_identity.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to line1_ht_identity.json")

if __name__ == '__main__':
    main()
