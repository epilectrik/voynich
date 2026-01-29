"""
01_ht_gallows_connection.py - Connect HT tokens to gallows patterns

f-initial paragraphs have 54% HT. Line 1 has 48% HT.
What's the relationship?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

GALLOWS = {'t', 'k', 'p', 'f'}

def line_to_num(l):
    """Convert line like '4a' to numeric 4."""
    nums = ''.join(c for c in str(l) if c.isdigit())
    return int(nums) if nums else 1

def get_initial_gallows(word):
    if not word:
        return None
    if word[0] in GALLOWS:
        return word[0]
    return None

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

    # Load folio census for paragraph gallows
    folio_census_path = Path(__file__).resolve().parents[3] / 'phases' / 'FOLIO_PARAGRAPH_ARCHITECTURE' / 'results' / 'folio_paragraph_census.json'
    with open(folio_census_path) as f:
        folio_census = json.load(f)

    print("=== HT-GALLOWS CONNECTION ===\n")

    # Build paragraph to gallows mapping
    par_gallows = {}
    for folio_entry in folio_census['folios']:
        for par_info in folio_entry['paragraphs']:
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])

            # Get gallows from first token
            for t in tokens:
                word = t['word']
                if word and '*' not in word:
                    par_gallows[par_id] = get_initial_gallows(word)
                    break

    # === 1. HT RATE BY GALLOWS TYPE ===
    print("--- 1. HT RATE BY PARAGRAPH GALLOWS TYPE ---\n")

    gallows_ht = defaultdict(lambda: {'ht': 0, 'total': 0})

    for par_id, tokens in tokens_by_par.items():
        gallows = par_gallows.get(par_id)
        if not gallows:
            gallows = 'none'

        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue
            gallows_ht[gallows]['total'] += 1
            if word not in class_map:
                gallows_ht[gallows]['ht'] += 1

    print(f"{'Gallows':<10} {'HT Rate':>10} {'HT Count':>10} {'Total':>10}")
    for g in ['p', 't', 'k', 'f', 'none']:
        d = gallows_ht[g]
        rate = d['ht'] / d['total'] if d['total'] > 0 else 0
        print(f"{g:<10} {rate:>10.1%} {d['ht']:>10} {d['total']:>10}")

    # === 2. HT BY LINE WITHIN PARAGRAPH (by gallows) ===
    print("\n--- 2. HT RATE BY LINE WITHIN PARAGRAPH (by gallows) ---\n")

    gallows_line_ht = defaultdict(lambda: defaultdict(lambda: {'ht': 0, 'total': 0}))

    for par_id, tokens in tokens_by_par.items():
        gallows = par_gallows.get(par_id, 'none')
        par_info = par_to_info.get(par_id, {})
        lines = par_info.get('lines', [])
        first_line = min(line_to_num(l) for l in lines) if lines else 1

        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue

            line = line_to_num(t.get('line', 1))

            # Relative line within paragraph
            rel_line = 'line1' if line == first_line else 'later'

            gallows_line_ht[gallows][rel_line]['total'] += 1
            if word not in class_map:
                gallows_line_ht[gallows][rel_line]['ht'] += 1

    print(f"{'Gallows':<10} {'Line 1 HT':>12} {'Later HT':>12} {'Ratio':>10}")
    for g in ['p', 't', 'k', 'f', 'none']:
        line1 = gallows_line_ht[g]['line1']
        later = gallows_line_ht[g]['later']
        l1_rate = line1['ht'] / line1['total'] if line1['total'] > 0 else 0
        later_rate = later['ht'] / later['total'] if later['total'] > 0 else 0
        ratio = l1_rate / later_rate if later_rate > 0 else 0
        print(f"{g:<10} {l1_rate:>12.1%} {later_rate:>12.1%} {ratio:>10.2f}x")

    # === 3. WHAT ARE THE HT TOKENS IN F-INITIAL PARAGRAPHS? ===
    print("\n--- 3. HT TOKENS IN F-INITIAL PARAGRAPHS ---\n")

    f_ht_tokens = Counter()
    f_classified_tokens = Counter()

    for par_id, tokens in tokens_by_par.items():
        if par_gallows.get(par_id) != 'f':
            continue
        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue
            if word in class_map:
                f_classified_tokens[word] += 1
            else:
                f_ht_tokens[word] += 1

    print(f"F-initial paragraphs: {sum(1 for g in par_gallows.values() if g == 'f')}")
    print(f"HT tokens in f-paragraphs: {sum(f_ht_tokens.values())} ({len(f_ht_tokens)} unique)")
    print(f"\nMost common HT in f-paragraphs:")
    for word, count in f_ht_tokens.most_common(15):
        print(f"  {word:15}: {count}")

    # === 4. HT IN LINE 1 OF PARAGRAPHS ===
    print("\n--- 4. WHAT ARE THE LINE-1 HT TOKENS? ---\n")

    line1_ht = Counter()
    line1_classified = Counter()

    for par_id, tokens in tokens_by_par.items():
        par_info = par_to_info.get(par_id, {})
        lines = par_info.get('lines', [])
        first_line = min(line_to_num(l) for l in lines) if lines else 1

        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue

            line = line_to_num(t.get('line', 1))

            if line == first_line:
                if word in class_map:
                    line1_classified[word] += 1
                else:
                    line1_ht[word] += 1

    print(f"Line-1 HT tokens: {sum(line1_ht.values())} ({len(line1_ht)} unique)")
    print(f"\nMost common line-1 HT tokens:")
    for word, count in line1_ht.most_common(20):
        print(f"  {word:15}: {count}")

    # === 5. COMPARE LINE-1 HT TO REST ===
    print("\n--- 5. LINE-1 HT vs REST ---\n")

    later_ht = Counter()
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
                later_ht[word] += 1

    # Find line-1 specific HT
    line1_specific = []
    for word, count in line1_ht.items():
        later_count = later_ht.get(word, 0)
        if count >= 3 and (later_count == 0 or count / (count + later_count) > 0.7):
            line1_specific.append((word, count, later_count))

    line1_specific.sort(key=lambda x: x[1], reverse=True)

    print(f"Line-1 specific HT tokens (>70% in line 1, 3+ occurrences): {len(line1_specific)}")
    print("\nExamples:")
    for word, l1_count, later_count in line1_specific[:15]:
        pct = l1_count / (l1_count + later_count) if (l1_count + later_count) > 0 else 0
        print(f"  {word:15}: {l1_count:3} in line 1, {later_count:3} later ({pct:.0%} line-1)")

    # === 6. HT MORPHOLOGY BY CONTEXT ===
    print("\n--- 6. HT TOKEN MORPHOLOGY: LINE-1 vs LATER ---\n")

    def get_prefix(word):
        for p in ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct']:
            if word.startswith(p):
                return p
        return word[:2] if len(word) >= 2 else word

    line1_prefixes = Counter(get_prefix(w) for w in line1_ht.elements())
    later_prefixes = Counter(get_prefix(w) for w in later_ht.elements())

    all_prefixes = set(line1_prefixes.keys()) | set(later_prefixes.keys())
    prefix_comparison = []
    for prefix in all_prefixes:
        l1 = line1_prefixes[prefix]
        later = later_prefixes[prefix]
        total = l1 + later
        if total >= 20:
            l1_pct = l1 / sum(line1_prefixes.values())
            later_pct = later / sum(later_prefixes.values())
            ratio = l1_pct / later_pct if later_pct > 0 else float('inf')
            prefix_comparison.append((prefix, l1_pct, later_pct, ratio, total))

    prefix_comparison.sort(key=lambda x: x[3], reverse=True)

    print("Prefixes enriched in LINE-1 HT:")
    for prefix, l1_pct, later_pct, ratio, total in prefix_comparison[:10]:
        if ratio > 1.2:
            print(f"  {prefix:8}: {ratio:.2f}x ({l1_pct:.1%} vs {later_pct:.1%})")

    print("\nPrefixes depleted in LINE-1 HT:")
    for prefix, l1_pct, later_pct, ratio, total in reversed(prefix_comparison[-10:]):
        if ratio < 0.8:
            print(f"  {prefix:8}: {ratio:.2f}x ({l1_pct:.1%} vs {later_pct:.1%})")

    # === VERDICT ===
    print("\n=== VERDICT ===\n")

    f_rate = gallows_ht['f']['ht'] / gallows_ht['f']['total']
    p_rate = gallows_ht['p']['ht'] / gallows_ht['p']['total']

    print(f"f-initial paragraph HT rate: {f_rate:.1%}")
    print(f"p-initial paragraph HT rate: {p_rate:.1%}")
    print(f"f/p HT ratio: {f_rate/p_rate:.2f}x")

    l1_total = gallows_line_ht['f']['line1']['ht'] + gallows_line_ht['f']['line1']['total'] - gallows_line_ht['f']['line1']['ht']
    print(f"\nLine-1 specific HT tokens: {len(line1_specific)}")
    print(f"Most common: {', '.join(w for w, _, _ in line1_specific[:5])}")

    # Save
    output = {
        'gallows_ht_rates': {g: d['ht']/d['total'] if d['total'] > 0 else 0
                            for g, d in gallows_ht.items()},
        'f_ht_tokens': dict(f_ht_tokens.most_common(30)),
        'line1_ht_tokens': dict(line1_ht.most_common(30)),
        'line1_specific': [(w, l1, later) for w, l1, later in line1_specific[:30]]
    }

    with open(results_dir / 'ht_gallows_connection.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to ht_gallows_connection.json")

if __name__ == '__main__':
    main()
