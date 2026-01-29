"""
02_pharma_deep_dive.py - What makes PHARMA structurally different?

PHARMA has:
- Only 3 folios (f57r, f66r, f66v)
- 40% HT (vs 22% BIO)
- 12.6 tokens/paragraph (vs 46 BIO)
- 14 paragraphs per folio (vs 7.5 BIO)

Why tiny HT-rich paragraphs?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

GALLOWS = {'t', 'k', 'p', 'f'}

def line_to_num(l):
    nums = ''.join(c for c in str(l) if c.isdigit())
    return int(nums) if nums else 1

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

    print("=== PHARMA DEEP DIVE ===\n")

    # Identify PHARMA and BIO paragraphs
    pharma_pars = []
    bio_pars = []

    for par_id, tokens in tokens_by_par.items():
        par_info = par_to_info.get(par_id, {})
        folio = par_info.get('folio', 'unknown')
        section = get_section(folio)

        if section == 'PHARMA':
            pharma_pars.append(par_id)
        elif section == 'BIO':
            bio_pars.append(par_id)

    print(f"PHARMA paragraphs: {len(pharma_pars)}")
    print(f"BIO paragraphs: {len(bio_pars)}")

    # === 1. PARAGRAPH SIZE DISTRIBUTION ===
    print("\n--- 1. PARAGRAPH SIZE DISTRIBUTION ---\n")

    def get_sizes(par_ids):
        sizes = []
        for par_id in par_ids:
            count = sum(1 for t in tokens_by_par.get(par_id, [])
                       if t['word'] and '*' not in t['word'])
            if count > 0:
                sizes.append(count)
        return sizes

    pharma_sizes = get_sizes(pharma_pars)
    bio_sizes = get_sizes(bio_pars)

    print(f"{'Metric':<20} {'PHARMA':>12} {'BIO':>12}")
    print(f"{'Mean tokens':<20} {sum(pharma_sizes)/len(pharma_sizes):>12.1f} {sum(bio_sizes)/len(bio_sizes):>12.1f}")
    print(f"{'Median tokens':<20} {sorted(pharma_sizes)[len(pharma_sizes)//2]:>12} {sorted(bio_sizes)[len(bio_sizes)//2]:>12}")
    print(f"{'Min tokens':<20} {min(pharma_sizes):>12} {min(bio_sizes):>12}")
    print(f"{'Max tokens':<20} {max(pharma_sizes):>12} {max(bio_sizes):>12}")

    # Size bins
    print("\nSize distribution:")
    print(f"{'Size Bin':<15} {'PHARMA':>12} {'BIO':>12}")
    for low, high in [(1, 10), (11, 20), (21, 30), (31, 50), (51, 100), (101, 200)]:
        p_count = sum(1 for s in pharma_sizes if low <= s <= high)
        b_count = sum(1 for s in bio_sizes if low <= s <= high)
        p_pct = p_count / len(pharma_sizes) if pharma_sizes else 0
        b_pct = b_count / len(bio_sizes) if bio_sizes else 0
        print(f"{str(low)+'-'+str(high):<15} {p_pct:>12.1%} {b_pct:>12.1%}")

    # === 2. LINE STRUCTURE ===
    print("\n--- 2. LINE STRUCTURE ---\n")

    def get_line_stats(par_ids):
        single_line = 0
        multi_line = 0
        total_lines = 0

        for par_id in par_ids:
            par_info = par_to_info.get(par_id, {})
            lines = par_info.get('lines', [])
            n_lines = len(lines)
            total_lines += n_lines

            if n_lines == 1:
                single_line += 1
            else:
                multi_line += 1

        return single_line, multi_line, total_lines / len(par_ids) if par_ids else 0

    p_single, p_multi, p_mean_lines = get_line_stats(pharma_pars)
    b_single, b_multi, b_mean_lines = get_line_stats(bio_pars)

    print(f"{'Metric':<25} {'PHARMA':>12} {'BIO':>12}")
    print(f"{'Single-line paragraphs':<25} {p_single:>12} ({p_single/len(pharma_pars):.1%}) {b_single:>12} ({b_single/len(bio_pars):.1%})")
    print(f"{'Multi-line paragraphs':<25} {p_multi:>12} {b_multi:>12}")
    print(f"{'Mean lines per paragraph':<25} {p_mean_lines:>12.1f} {b_mean_lines:>12.1f}")

    # === 3. GALLOWS PATTERNS ===
    print("\n--- 3. GALLOWS PATTERNS ---\n")

    def get_gallows_dist(par_ids):
        gallows_counts = Counter()
        for par_id in par_ids:
            tokens = tokens_by_par.get(par_id, [])
            for t in tokens:
                word = t['word']
                if word and '*' not in word:
                    if word[0] in GALLOWS:
                        gallows_counts[word[0]] += 1
                    else:
                        gallows_counts['none'] += 1
                    break
        return gallows_counts

    p_gallows = get_gallows_dist(pharma_pars)
    b_gallows = get_gallows_dist(bio_pars)

    print(f"{'Gallows':<10} {'PHARMA':>12} {'BIO':>12}")
    for g in ['p', 't', 'k', 'f', 'none']:
        p_rate = p_gallows[g] / len(pharma_pars) if pharma_pars else 0
        b_rate = b_gallows[g] / len(bio_pars) if bio_pars else 0
        print(f"{g:<10} {p_rate:>12.1%} {b_rate:>12.1%}")

    # === 4. HT IN HEADER vs BODY ===
    print("\n--- 4. HT IN HEADER vs BODY ---\n")

    def get_ht_by_position(par_ids):
        line1_ht = 0
        line1_total = 0
        body_ht = 0
        body_total = 0

        for par_id in par_ids:
            par_info = par_to_info.get(par_id, {})
            lines = par_info.get('lines', [])
            first_line = min(line_to_num(l) for l in lines) if lines else 1

            for t in tokens_by_par.get(par_id, []):
                word = t['word']
                if not word or '*' in word:
                    continue

                line = line_to_num(t.get('line', 1))
                is_ht = word not in class_map

                if line == first_line:
                    line1_total += 1
                    if is_ht:
                        line1_ht += 1
                else:
                    body_total += 1
                    if is_ht:
                        body_ht += 1

        return (line1_ht / line1_total if line1_total > 0 else 0,
                body_ht / body_total if body_total > 0 else 0,
                line1_total, body_total)

    p_l1_ht, p_body_ht, p_l1_n, p_body_n = get_ht_by_position(pharma_pars)
    b_l1_ht, b_body_ht, b_l1_n, b_body_n = get_ht_by_position(bio_pars)

    print(f"{'Position':<15} {'PHARMA HT':>12} {'BIO HT':>12} {'Ratio':>10}")
    print(f"{'Line 1':<15} {p_l1_ht:>12.1%} {b_l1_ht:>12.1%} {p_l1_ht/b_l1_ht if b_l1_ht > 0 else 0:>10.2f}")
    print(f"{'Body':<15} {p_body_ht:>12.1%} {b_body_ht:>12.1%} {p_body_ht/b_body_ht if b_body_ht > 0 else 0:>10.2f}")

    print(f"\nPHARMA body tokens: {p_body_n} (vs Line 1: {p_l1_n})")
    print(f"BIO body tokens: {b_body_n} (vs Line 1: {b_l1_n})")

    # === 5. VOCABULARY OVERLAP ===
    print("\n--- 5. VOCABULARY OVERLAP ---\n")

    def get_vocab(par_ids):
        words = set()
        ht_words = set()
        for par_id in par_ids:
            for t in tokens_by_par.get(par_id, []):
                word = t['word']
                if word and '*' not in word:
                    words.add(word)
                    if word not in class_map:
                        ht_words.add(word)
        return words, ht_words

    p_vocab, p_ht_vocab = get_vocab(pharma_pars)
    b_vocab, b_ht_vocab = get_vocab(bio_pars)

    overlap = len(p_vocab & b_vocab)
    ht_overlap = len(p_ht_vocab & b_ht_vocab)

    print(f"PHARMA vocabulary: {len(p_vocab)} ({len(p_ht_vocab)} HT)")
    print(f"BIO vocabulary: {len(b_vocab)} ({len(b_ht_vocab)} HT)")
    print(f"Shared vocabulary: {overlap} ({overlap/len(p_vocab):.1%} of PHARMA)")
    print(f"Shared HT vocabulary: {ht_overlap} ({ht_overlap/len(p_ht_vocab):.1%} of PHARMA HT)")

    # === 6. WHAT TOKENS ARE PHARMA-SPECIFIC? ===
    print("\n--- 6. PHARMA-SPECIFIC VOCABULARY ---\n")

    pharma_only = p_vocab - b_vocab
    pharma_only_ht = p_ht_vocab - b_ht_vocab

    # Count occurrences
    pharma_only_counts = Counter()
    for par_id in pharma_pars:
        for t in tokens_by_par.get(par_id, []):
            word = t['word']
            if word in pharma_only:
                pharma_only_counts[word] += 1

    print(f"PHARMA-only vocabulary: {len(pharma_only)} tokens")
    print(f"PHARMA-only HT: {len(pharma_only_ht)} tokens")

    print("\nMost common PHARMA-only tokens:")
    for word, count in pharma_only_counts.most_common(20):
        is_ht = "HT" if word not in class_map else "PP"
        print(f"  {word:15}: {count:3} ({is_ht})")

    # === 7. PARAGRAPH CONTENT SAMPLES ===
    print("\n--- 7. SAMPLE PHARMA PARAGRAPHS ---\n")

    for par_id in pharma_pars[:5]:
        par_info = par_to_info.get(par_id, {})
        tokens = tokens_by_par.get(par_id, [])
        folio = par_info.get('folio', '?')

        words = [t['word'] for t in tokens if t['word'] and '*' not in t['word']]
        ht_count = sum(1 for w in words if w not in class_map)

        print(f"{par_id} ({folio}): {len(words)} tokens, {ht_count} HT ({ht_count/len(words):.1%})")
        print(f"  {' '.join(words[:15])}...")
        print()

    # === VERDICT ===
    print("=== VERDICT ===\n")

    print("PHARMA structural profile:")
    print(f"  - Tiny paragraphs: {sum(pharma_sizes)/len(pharma_sizes):.1f} tokens (vs {sum(bio_sizes)/len(bio_sizes):.1f} BIO)")
    print(f"  - High single-line rate: {p_single/len(pharma_pars):.1%} (vs {b_single/len(bio_pars):.1%} BIO)")
    print(f"  - Elevated f-initial: {p_gallows['f']/len(pharma_pars):.1%} (vs {b_gallows['f']/len(bio_pars):.1%} BIO)")
    print(f"  - Body HT elevated: {p_body_ht:.1%} (vs {b_body_ht:.1%} BIO)")
    print(f"  - Low vocabulary overlap: {overlap/len(p_vocab):.1%} shared with BIO")

    # Save
    output = {
        'pharma_mean_size': sum(pharma_sizes) / len(pharma_sizes),
        'bio_mean_size': sum(bio_sizes) / len(bio_sizes),
        'pharma_single_line_rate': p_single / len(pharma_pars),
        'bio_single_line_rate': b_single / len(bio_pars),
        'pharma_line1_ht': p_l1_ht,
        'pharma_body_ht': p_body_ht,
        'bio_line1_ht': b_l1_ht,
        'bio_body_ht': b_body_ht,
        'vocabulary_overlap': overlap / len(p_vocab),
        'ht_vocabulary_overlap': ht_overlap / len(p_ht_vocab)
    }

    with open(results_dir / 'pharma_deep_dive.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to pharma_deep_dive.json")

if __name__ == '__main__':
    main()
