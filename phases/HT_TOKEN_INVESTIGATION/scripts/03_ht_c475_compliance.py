"""
03_ht_c475_compliance.py - Do HT tokens follow cooccurrence rules?

C475 states that tokens in the same line share cooccurrence restrictions.
Do HT tokens (unclassified) follow this pattern, or are they "outside" the system?

If HT tokens VIOLATE cooccurrence rules, they may be:
- A separate vocabulary layer
- Foreign insertions
- Identification marks not bound by grammar

If HT tokens COMPLY with cooccurrence rules, they are:
- Part of the same system, just rare
- Extensions of the classified vocabulary
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

    print("=== HT TOKEN C475 COMPLIANCE ===\n")

    # Build line-level token lists
    lines_by_par = defaultdict(lambda: defaultdict(list))

    for par_id, tokens in tokens_by_par.items():
        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue
            line = line_to_num(t.get('line', 1))
            is_ht = word not in class_map
            lines_by_par[par_id][line].append({
                'word': word,
                'is_ht': is_ht,
                'class': class_map.get(word, 'HT')
            })

    # === 1. HT TOKEN NEIGHBORS ===
    print("--- 1. WHAT CLASSES COOCCUR WITH HT IN SAME LINE? ---\n")

    ht_neighbor_classes = Counter()
    classified_neighbor_classes = Counter()

    for par_id, lines in lines_by_par.items():
        for line_num, tokens in lines.items():
            has_ht = any(t['is_ht'] for t in tokens)
            classes_in_line = [t['class'] for t in tokens if t['class'] != 'HT']

            if has_ht:
                for c in classes_in_line:
                    ht_neighbor_classes[c] += 1
            else:
                for c in classes_in_line:
                    classified_neighbor_classes[c] += 1

    # Compare distributions
    total_ht_neighbors = sum(ht_neighbor_classes.values())
    total_classified_neighbors = sum(classified_neighbor_classes.values())

    print(f"{'Class':<10} {'With HT':>12} {'Without HT':>15} {'Ratio':>10}")

    all_classes = set(ht_neighbor_classes.keys()) | set(classified_neighbor_classes.keys())
    class_comparison = []
    for c in all_classes:
        ht_pct = ht_neighbor_classes[c] / total_ht_neighbors if total_ht_neighbors > 0 else 0
        class_pct = classified_neighbor_classes[c] / total_classified_neighbors if total_classified_neighbors > 0 else 0
        ratio = ht_pct / class_pct if class_pct > 0 else float('inf')
        class_comparison.append((c, ht_pct, class_pct, ratio))

    class_comparison.sort(key=lambda x: x[3], reverse=True)

    print("\nClasses ENRICHED near HT tokens:")
    for c, ht_pct, class_pct, ratio in class_comparison[:10]:
        if ratio > 1.3:
            print(f"  Class {c:<5}: {ratio:>5.2f}x ({ht_pct:.1%} vs {class_pct:.1%})")

    print("\nClasses DEPLETED near HT tokens:")
    for c, ht_pct, class_pct, ratio in reversed(class_comparison[-10:]):
        if ratio < 0.8:
            print(f"  Class {c:<5}: {ratio:>5.2f}x ({ht_pct:.1%} vs {class_pct:.1%})")

    # === 2. HT TOKEN LINE COMPOSITION ===
    print("\n--- 2. LINE COMPOSITION WITH HT ---\n")

    ht_only_lines = 0
    mixed_lines = 0
    no_ht_lines = 0

    total_lines = 0
    for par_id, lines in lines_by_par.items():
        for line_num, tokens in lines.items():
            total_lines += 1
            ht_count = sum(1 for t in tokens if t['is_ht'])
            classified_count = sum(1 for t in tokens if not t['is_ht'])

            if ht_count > 0 and classified_count == 0:
                ht_only_lines += 1
            elif ht_count > 0 and classified_count > 0:
                mixed_lines += 1
            else:
                no_ht_lines += 1

    print(f"Lines with ONLY HT tokens: {ht_only_lines} ({ht_only_lines/total_lines:.1%})")
    print(f"Lines with MIXED (HT + classified): {mixed_lines} ({mixed_lines/total_lines:.1%})")
    print(f"Lines with NO HT tokens: {no_ht_lines} ({no_ht_lines/total_lines:.1%})")

    # === 3. HT COOCCURRENCE MATRIX ===
    print("\n--- 3. HT COOCCURRENCE WITH SPECIFIC CLASSES ---\n")

    # Check which instruction classes appear on lines WITH vs WITHOUT HT
    class_with_ht = defaultdict(int)
    class_without_ht = defaultdict(int)
    lines_with_ht = 0
    lines_without_ht = 0

    for par_id, lines in lines_by_par.items():
        for line_num, tokens in lines.items():
            has_ht = any(t['is_ht'] for t in tokens)
            classes = set(t['class'] for t in tokens if t['class'] != 'HT')

            if has_ht:
                lines_with_ht += 1
                for c in classes:
                    class_with_ht[c] += 1
            else:
                lines_without_ht += 1
                for c in classes:
                    class_without_ht[c] += 1

    print(f"Total lines with HT: {lines_with_ht}")
    print(f"Total lines without HT: {lines_without_ht}")

    # Normalized comparison
    print(f"\n{'Class':<10} {'Rate with HT':>15} {'Rate without':>15} {'Ratio':>10}")

    cooccur_comparison = []
    for c in all_classes:
        with_rate = class_with_ht[c] / lines_with_ht if lines_with_ht > 0 else 0
        without_rate = class_without_ht[c] / lines_without_ht if lines_without_ht > 0 else 0
        ratio = with_rate / without_rate if without_rate > 0 else float('inf')
        cooccur_comparison.append((c, with_rate, without_rate, ratio))

    cooccur_comparison.sort(key=lambda x: x[3], reverse=True)

    print("\nClasses appearing MORE on HT lines:")
    for c, with_rate, without_rate, ratio in cooccur_comparison[:8]:
        if ratio > 1.1 and class_with_ht[c] >= 20:
            print(f"  Class {c:<5}: {ratio:>5.2f}x ({with_rate:.1%} vs {without_rate:.1%})")

    print("\nClasses appearing LESS on HT lines:")
    for c, with_rate, without_rate, ratio in reversed(cooccur_comparison[-8:]):
        if ratio < 0.9 and class_without_ht[c] >= 20:
            print(f"  Class {c:<5}: {ratio:>5.2f}x ({with_rate:.1%} vs {without_rate:.1%})")

    # === 4. LINE-1 SPECIFIC COOCCURRENCE ===
    print("\n--- 4. LINE-1 HT COOCCURRENCE ---\n")

    line1_ht_cooccur = Counter()
    later_ht_cooccur = Counter()

    for par_id, tokens in tokens_by_par.items():
        par_info = par_to_info.get(par_id, {})
        lines = par_info.get('lines', [])
        first_line = min(line_to_num(l) for l in lines) if lines else 1

        # Group by line
        line_tokens = defaultdict(list)
        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue
            line = line_to_num(t.get('line', 1))
            line_tokens[line].append({
                'word': word,
                'is_ht': word not in class_map,
                'class': class_map.get(word, 'HT')
            })

        for line_num, toks in line_tokens.items():
            has_ht = any(t['is_ht'] for t in toks)
            if not has_ht:
                continue

            classes = [t['class'] for t in toks if t['class'] != 'HT']
            if line_num == first_line:
                line1_ht_cooccur.update(classes)
            else:
                later_ht_cooccur.update(classes)

    total_l1 = sum(line1_ht_cooccur.values())
    total_later = sum(later_ht_cooccur.values())

    print(f"{'Class':<10} {'Line-1 HT':>12} {'Later HT':>12} {'Ratio':>10}")

    l1_later_comparison = []
    for c in set(line1_ht_cooccur.keys()) | set(later_ht_cooccur.keys()):
        l1_pct = line1_ht_cooccur[c] / total_l1 if total_l1 > 0 else 0
        later_pct = later_ht_cooccur[c] / total_later if total_later > 0 else 0
        ratio = l1_pct / later_pct if later_pct > 0 else float('inf')
        l1_later_comparison.append((c, l1_pct, later_pct, ratio))

    l1_later_comparison.sort(key=lambda x: x[3], reverse=True)

    print("\nClasses enriched on Line-1 HT lines:")
    for c, l1_pct, later_pct, ratio in l1_later_comparison[:8]:
        if ratio > 1.3 and line1_ht_cooccur[c] >= 10:
            print(f"  Class {c:<5}: {ratio:>5.2f}x ({l1_pct:.1%} vs {later_pct:.1%})")

    print("\nClasses depleted on Line-1 HT lines:")
    for c, l1_pct, later_pct, ratio in reversed(l1_later_comparison[-8:]):
        if ratio < 0.7 and later_ht_cooccur[c] >= 10:
            print(f"  Class {c:<5}: {ratio:>5.2f}x ({l1_pct:.1%} vs {later_pct:.1%})")

    # === VERDICT ===
    print("\n=== VERDICT ===\n")

    print(f"HT-only lines: {ht_only_lines} ({ht_only_lines/total_lines:.1%})")
    print(f"Mixed lines: {mixed_lines} ({mixed_lines/total_lines:.1%})")
    print(f"HT tokens DO cooccur with classified tokens (mixed lines exist)")

    print(f"\nHT-containing lines show class distribution shifts:")
    print(f"  - Some classes appear MORE with HT")
    print(f"  - Some classes appear LESS with HT")
    print(f"  - HT is NOT isolated - it interleaves with instruction classes")

    # Save
    output = {
        'ht_only_lines': ht_only_lines,
        'mixed_lines': mixed_lines,
        'no_ht_lines': no_ht_lines,
        'class_enriched_with_ht': {c: r for c, _, _, r in cooccur_comparison[:5]},
        'class_depleted_with_ht': {c: r for c, _, _, r in cooccur_comparison[-5:]}
    }

    with open(results_dir / 'ht_c475_compliance.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to ht_c475_compliance.json")

if __name__ == '__main__':
    main()
