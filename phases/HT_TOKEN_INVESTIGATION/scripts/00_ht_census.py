"""
00_ht_census.py - GATE: Census of HT (Human Track) tokens

HT tokens = tokens NOT in the instruction class map
f-initial paragraphs have 54% HT vs 33% elsewhere - why?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

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

    print("=== HT TOKEN CENSUS ===\n")

    # Collect all tokens, classify as HT or not
    all_tokens = []
    ht_tokens = []
    classified_tokens = []

    for par_id, tokens in tokens_by_par.items():
        par_info = par_to_info.get(par_id, {})
        folio = par_info.get('folio', 'unknown')

        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue

            token_data = {
                'word': word,
                'folio': folio,
                'par_id': par_id,
                'line': t.get('line', 0),
                'position': t.get('position', 0)
            }

            all_tokens.append(token_data)

            if word in class_map:
                classified_tokens.append(token_data)
            else:
                ht_tokens.append(token_data)

    print(f"Total B tokens: {len(all_tokens)}")
    print(f"Classified (in class map): {len(classified_tokens)} ({len(classified_tokens)/len(all_tokens):.1%})")
    print(f"HT (not in class map): {len(ht_tokens)} ({len(ht_tokens)/len(all_tokens):.1%})")

    # === 1. MOST COMMON HT TOKENS ===
    print("\n--- 1. MOST COMMON HT TOKENS ---\n")

    ht_word_counts = Counter(t['word'] for t in ht_tokens)
    print(f"Unique HT tokens: {len(ht_word_counts)}")
    print(f"\nTop 30 HT tokens:")
    for word, count in ht_word_counts.most_common(30):
        print(f"  {word:15}: {count:4}")

    # === 2. HT TOKEN LENGTH DISTRIBUTION ===
    print("\n--- 2. HT TOKEN LENGTH ---\n")

    ht_lengths = Counter(len(t['word']) for t in ht_tokens)
    class_lengths = Counter(len(t['word']) for t in classified_tokens)

    print(f"{'Length':<8} {'HT':>8} {'Classified':>12}")
    for length in sorted(set(ht_lengths.keys()) | set(class_lengths.keys())):
        ht_pct = ht_lengths[length] / len(ht_tokens) if ht_tokens else 0
        class_pct = class_lengths[length] / len(classified_tokens) if classified_tokens else 0
        print(f"{length:<8} {ht_pct:>8.1%} {class_pct:>12.1%}")

    # === 3. HT BY FOLIO ===
    print("\n--- 3. HT RATE BY FOLIO ---\n")

    folio_counts = defaultdict(lambda: {'ht': 0, 'total': 0})
    for t in all_tokens:
        folio_counts[t['folio']]['total'] += 1
    for t in ht_tokens:
        folio_counts[t['folio']]['ht'] += 1

    # Sort by HT rate
    folio_rates = [(f, d['ht']/d['total'] if d['total'] > 0 else 0, d['total'])
                   for f, d in folio_counts.items()]
    folio_rates.sort(key=lambda x: x[1], reverse=True)

    print("Highest HT rate folios:")
    for folio, rate, total in folio_rates[:10]:
        print(f"  {folio}: {rate:.1%} ({total} tokens)")

    print("\nLowest HT rate folios:")
    for folio, rate, total in folio_rates[-10:]:
        print(f"  {folio}: {rate:.1%} ({total} tokens)")

    # === 4. HT BY SECTION ===
    print("\n--- 4. HT RATE BY SECTION ---\n")

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

    section_counts = defaultdict(lambda: {'ht': 0, 'total': 0})
    for t in all_tokens:
        section = get_section(t['folio'])
        section_counts[section]['total'] += 1
    for t in ht_tokens:
        section = get_section(t['folio'])
        section_counts[section]['ht'] += 1

    print(f"{'Section':<12} {'HT Rate':>10} {'HT Count':>10} {'Total':>10}")
    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B', 'OTHER']:
        d = section_counts[section]
        rate = d['ht'] / d['total'] if d['total'] > 0 else 0
        print(f"{section:<12} {rate:>10.1%} {d['ht']:>10} {d['total']:>10}")

    # === 5. HT BY LINE POSITION ===
    print("\n--- 5. HT RATE BY LINE POSITION ---\n")

    line_counts = defaultdict(lambda: {'ht': 0, 'total': 0})
    for t in all_tokens:
        line = t['line']
        if isinstance(line, str):
            line = int(line) if line.isdigit() else 1
        line = min(line, 10)  # Cap at 10
        line_counts[line]['total'] += 1
    for t in ht_tokens:
        line = t['line']
        if isinstance(line, str):
            line = int(line) if line.isdigit() else 1
        line = min(line, 10)
        line_counts[line]['ht'] += 1

    print(f"{'Line':<8} {'HT Rate':>10} {'Total':>10}")
    for line in sorted(line_counts.keys()):
        d = line_counts[line]
        rate = d['ht'] / d['total'] if d['total'] > 0 else 0
        print(f"{line:<8} {rate:>10.1%} {d['total']:>10}")

    # === 6. HT MORPHOLOGY ===
    print("\n--- 6. HT TOKEN MORPHOLOGY ---\n")

    # Check starting patterns
    ht_starts = Counter()
    for t in ht_tokens:
        word = t['word']
        if len(word) >= 2:
            ht_starts[word[:2]] += 1
        elif len(word) == 1:
            ht_starts[word] += 1

    print("Most common HT token starts:")
    for start, count in ht_starts.most_common(15):
        pct = count / len(ht_tokens)
        print(f"  {start:8}: {count:4} ({pct:.1%})")

    # Check ending patterns
    ht_ends = Counter()
    for t in ht_tokens:
        word = t['word']
        if len(word) >= 2:
            ht_ends[word[-2:]] += 1

    print("\nMost common HT token ends:")
    for end, count in ht_ends.most_common(15):
        pct = count / len(ht_tokens)
        print(f"  {end:8}: {count:4} ({pct:.1%})")

    # === 7. SINGLETON vs REPEATED HT ===
    print("\n--- 7. HT TOKEN FREQUENCY DISTRIBUTION ---\n")

    singletons = sum(1 for w, c in ht_word_counts.items() if c == 1)
    rare = sum(1 for w, c in ht_word_counts.items() if c <= 3)
    common = sum(1 for w, c in ht_word_counts.items() if c >= 10)

    print(f"Singletons (appear once): {singletons} ({singletons/len(ht_word_counts):.1%})")
    print(f"Rare (appear 1-3 times): {rare} ({rare/len(ht_word_counts):.1%})")
    print(f"Common (appear 10+ times): {common} ({common/len(ht_word_counts):.1%})")

    # === 8. FOLIO-SPECIFIC HT ===
    print("\n--- 8. FOLIO-SPECIFIC HT TOKENS ---\n")

    # Count how many folios each HT token appears in
    ht_folio_spread = defaultdict(set)
    for t in ht_tokens:
        ht_folio_spread[t['word']].add(t['folio'])

    spread_dist = Counter(len(folios) for folios in ht_folio_spread.values())

    print("HT token folio spread:")
    for n_folios in sorted(spread_dist.keys())[:10]:
        count = spread_dist[n_folios]
        print(f"  Appears in {n_folios} folio(s): {count} tokens")

    # Highly folio-specific (appear in only 1-2 folios)
    folio_specific = [w for w, folios in ht_folio_spread.items()
                      if len(folios) <= 2 and ht_word_counts[w] >= 3]

    print(f"\nFolio-specific HT tokens (1-2 folios, 3+ occurrences): {len(folio_specific)}")
    print("Examples:")
    for word in folio_specific[:15]:
        folios = ht_folio_spread[word]
        count = ht_word_counts[word]
        print(f"  {word:15}: {count} in {sorted(folios)}")

    # Save results
    output = {
        'total_tokens': len(all_tokens),
        'ht_count': len(ht_tokens),
        'ht_rate': len(ht_tokens) / len(all_tokens),
        'unique_ht': len(ht_word_counts),
        'top_ht_tokens': dict(ht_word_counts.most_common(50)),
        'section_rates': {s: d['ht']/d['total'] if d['total'] > 0 else 0
                         for s, d in section_counts.items()},
        'folio_specific_count': len(folio_specific)
    }

    with open(results_dir / 'ht_census.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to ht_census.json")

if __name__ == '__main__':
    main()
