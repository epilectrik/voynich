"""
11_gallows_token_structure.py - Analyze structure of gallows-initial tokens

Questions:
1. What follows the gallows? (ch, sh, o, etc.)
2. Are there gallows-specific patterns?
3. Does gallows predict the rest of the token?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import re

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

GALLOWS = {'t', 'k', 'p', 'f'}

def parse_gallows_token(word):
    """Parse a gallows-initial token into components."""
    if not word or word[0] not in GALLOWS:
        return None

    gallows = word[0]
    remainder = word[1:]

    # Identify what follows gallows
    if not remainder:
        return {'gallows': gallows, 'post': '', 'middle': '', 'suffix': ''}

    # Common post-gallows patterns
    post = ''
    if remainder.startswith('ch'):
        post = 'ch'
        remainder = remainder[2:]
    elif remainder.startswith('sh'):
        post = 'sh'
        remainder = remainder[2:]
    elif remainder.startswith('o'):
        post = 'o'
        remainder = remainder[1:]
    elif remainder.startswith('a'):
        post = 'a'
        remainder = remainder[1:]

    # Try to identify suffix
    suffix = ''
    for suf in ['aiin', 'ain', 'iin', 'in', 'ar', 'or', 'al', 'ol', 'an', 'y', 'dy', 'edy', 'ody']:
        if remainder.endswith(suf):
            suffix = suf
            remainder = remainder[:-len(suf)]
            break

    return {
        'gallows': gallows,
        'post': post,
        'middle': remainder,
        'suffix': suffix,
        'full_post': word[1:]
    }

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load previous probe results
    with open(results_dir / 'gallows_initial_probe.json') as f:
        probe_data = json.load(f)

    # Load paragraph tokens
    par_results = Path(__file__).resolve().parents[2] / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Load census for folio info
    with open(results_dir / 'folio_paragraph_census.json') as f:
        census = json.load(f)

    print("=== GALLOWS TOKEN STRUCTURE ANALYSIS ===\n")

    # Collect all gallows-initial first tokens
    first_tokens = []
    for folio_entry in census['folios']:
        for par_info in folio_entry['paragraphs']:
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])

            for t in tokens:
                word = t['word']
                if word and '*' not in word and word[0] in GALLOWS:
                    first_tokens.append({
                        'token': word,
                        'folio': folio_entry['folio'],
                        'par_id': par_id
                    })
                    break

    print(f"Gallows-initial first tokens: {len(first_tokens)}\n")

    # === 1. POST-GALLOWS PATTERNS ===
    print("--- 1. WHAT FOLLOWS GALLOWS? ---\n")

    post_by_gallows = defaultdict(Counter)
    for entry in first_tokens:
        parsed = parse_gallows_token(entry['token'])
        if parsed:
            post_by_gallows[parsed['gallows']][parsed['post'] or '(none)'] += 1

    for g in ['p', 't', 'k', 'f']:
        print(f"After '{g}':")
        total = sum(post_by_gallows[g].values())
        for post, count in post_by_gallows[g].most_common(6):
            print(f"  {post:8}: {count:4} ({count/total:.1%})")
        print()

    # === 2. FULL SUFFIX PATTERNS ===
    print("--- 2. SUFFIX PATTERNS ---\n")

    suffix_by_gallows = defaultdict(Counter)
    for entry in first_tokens:
        parsed = parse_gallows_token(entry['token'])
        if parsed:
            suffix_by_gallows[parsed['gallows']][parsed['suffix'] or '(none)'] += 1

    for g in ['p', 't', 'k', 'f']:
        print(f"Suffixes for '{g}'-initial tokens:")
        total = sum(suffix_by_gallows[g].values())
        for suffix, count in suffix_by_gallows[g].most_common(8):
            print(f"  {suffix:8}: {count:4} ({count/total:.1%})")
        print()

    # === 3. GALLOWS + POST COMBINATIONS ===
    print("--- 3. GALLOWS + POST COMBINATIONS ---\n")

    combo_counts = Counter()
    for entry in first_tokens:
        parsed = parse_gallows_token(entry['token'])
        if parsed:
            combo = parsed['gallows'] + (parsed['post'] or '-')
            combo_counts[combo] += 1

    print("Most common gallows+post combinations:")
    total = sum(combo_counts.values())
    for combo, count in combo_counts.most_common(15):
        print(f"  {combo:8}: {count:4} ({count/total:.1%})")

    # === 4. TOKEN LENGTH BY GALLOWS ===
    print("\n--- 4. TOKEN LENGTH BY GALLOWS ---\n")

    lengths_by_gallows = defaultdict(list)
    for entry in first_tokens:
        g = entry['token'][0]
        lengths_by_gallows[g].append(len(entry['token']))

    for g in ['p', 't', 'k', 'f']:
        lengths = lengths_by_gallows[g]
        if lengths:
            avg = sum(lengths) / len(lengths)
            print(f"  '{g}': mean length {avg:.1f}, range {min(lengths)}-{max(lengths)}")

    # === 5. UNIQUE TOKENS BY GALLOWS ===
    print("\n--- 5. VOCABULARY SIZE BY GALLOWS ---\n")

    vocab_by_gallows = defaultdict(set)
    for entry in first_tokens:
        g = entry['token'][0]
        vocab_by_gallows[g].add(entry['token'])

    for g in ['p', 't', 'k', 'f']:
        vocab = vocab_by_gallows[g]
        occurrences = sum(1 for e in first_tokens if e['token'][0] == g)
        print(f"  '{g}': {len(vocab)} unique tokens, {occurrences} occurrences, "
              f"reuse rate {occurrences/len(vocab):.1f}x")

    # === 6. MOST COMMON BY GALLOWS ===
    print("\n--- 6. MOST COMMON TOKENS BY GALLOWS ---\n")

    tokens_by_gallows = defaultdict(Counter)
    for entry in first_tokens:
        g = entry['token'][0]
        tokens_by_gallows[g][entry['token']] += 1

    for g in ['p', 't', 'k', 'f']:
        print(f"Most common '{g}'-initial:")
        for token, count in tokens_by_gallows[g].most_common(8):
            print(f"  {token:15}: {count}")
        print()

    # === 7. SECTION-SPECIFIC TOKENS ===
    print("--- 7. SECTION-SPECIFIC GALLOWS TOKENS ---\n")

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

    section_tokens = defaultdict(lambda: defaultdict(Counter))
    for entry in first_tokens:
        section = get_section(entry['folio'])
        g = entry['token'][0]
        section_tokens[section][g][entry['token']] += 1

    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
        print(f"{section}:")
        for g in ['p', 't', 'k', 'f']:
            tokens = section_tokens[section][g]
            if tokens:
                top = tokens.most_common(3)
                top_str = ', '.join(f"{t}({c})" for t, c in top)
                print(f"  {g}: {top_str}")
        print()

    # === 8. DOES GALLOWS PREDICT TOKEN CONTENT? ===
    print("--- 8. GALLOWS-CONTENT CORRELATION ---\n")

    # Check if certain MIDDLEs prefer certain gallows
    middle_by_gallows = defaultdict(Counter)
    for entry in first_tokens:
        parsed = parse_gallows_token(entry['token'])
        if parsed and parsed['middle']:
            middle_by_gallows[parsed['gallows']][parsed['middle']] += 1

    # Find middles that strongly prefer one gallows
    all_middles = set()
    for g_middles in middle_by_gallows.values():
        all_middles.update(g_middles.keys())

    gallows_specific_middles = []
    for middle in all_middles:
        counts = {g: middle_by_gallows[g][middle] for g in GALLOWS}
        total = sum(counts.values())
        if total >= 5:
            max_g = max(counts, key=counts.get)
            if counts[max_g] / total > 0.7:
                gallows_specific_middles.append((middle, max_g, counts[max_g]/total, total))

    gallows_specific_middles.sort(key=lambda x: x[2], reverse=True)

    print("MIDDLEs that prefer specific gallows (>70%):")
    for middle, g, pct, total in gallows_specific_middles[:15]:
        print(f"  {middle:10} prefers '{g}' ({pct:.0%} of {total})")

    # === VERDICT ===
    print("\n=== VERDICT ===\n")

    # Most common combo
    top_combo = combo_counts.most_common(1)[0]
    print(f"Most common structure: {top_combo[0]} ({top_combo[1]/total:.1%})")

    # Gallows specificity
    if gallows_specific_middles:
        print(f"Gallows-specific MIDDLEs found: {len(gallows_specific_middles)}")
        print("  -> Gallows DOES influence token content")
    else:
        print("  -> Gallows does NOT strongly predict content")

    # Save results
    output = {
        'post_by_gallows': {g: dict(c) for g, c in post_by_gallows.items()},
        'suffix_by_gallows': {g: dict(c) for g, c in suffix_by_gallows.items()},
        'combo_counts': dict(combo_counts),
        'vocab_by_gallows': {g: list(v) for g, v in vocab_by_gallows.items()},
        'gallows_specific_middles': gallows_specific_middles[:20]
    }

    with open(results_dir / 'gallows_token_structure.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to gallows_token_structure.json")

if __name__ == '__main__':
    main()
