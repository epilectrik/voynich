"""
14_gallows_morphology_probe.py - Analyze full morphology of gallows tokens

Structure: GALLOWS + POST + MIDDLE + SUFFIX
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import re

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

GALLOWS = {'t', 'k', 'p', 'f'}

# Known suffixes (ordered by length for greedy matching)
SUFFIXES = ['aiin', 'oiin', 'ain', 'iin', 'ar', 'or', 'al', 'ol', 'an', 'in', 'dy', 'edy', 'ody', 'y', 'r', 'l', 's']

# Known post-gallows elements
POSTS = ['ch', 'sh', 'o', 'a', 'e']

def parse_gallows_token(word):
    """Parse a gallows-initial token into morphological components."""
    if not word or word[0] not in GALLOWS:
        return None

    original = word
    gallows = word[0]
    remainder = word[1:]

    # Extract POST
    post = ''
    for p in ['ch', 'sh', 'o', 'a', 'e']:
        if remainder.startswith(p):
            post = p
            remainder = remainder[len(p):]
            break

    # Extract SUFFIX (from end)
    suffix = ''
    for s in SUFFIXES:
        if remainder.endswith(s):
            suffix = s
            remainder = remainder[:-len(s)]
            break

    # What's left is MIDDLE
    middle = remainder

    return {
        'original': original,
        'gallows': gallows,
        'post': post or '-',
        'middle': middle or '-',
        'suffix': suffix or '-',
        'template': f"{gallows}+{post or '-'}+M+{suffix or '-'}"
    }

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load census
    with open(results_dir / 'folio_paragraph_census.json') as f:
        census = json.load(f)

    # Load paragraph tokens
    par_results = Path(__file__).resolve().parents[2] / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    print("=== GALLOWS TOKEN MORPHOLOGY ===\n")

    # Collect all gallows-initial first tokens
    parsed_tokens = []

    for folio_entry in census['folios']:
        for par_info in folio_entry['paragraphs']:
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])

            for t in tokens:
                word = t['word']
                if word and '*' not in word and word[0] in GALLOWS:
                    parsed = parse_gallows_token(word)
                    if parsed:
                        parsed['folio'] = folio_entry['folio']
                        parsed_tokens.append(parsed)
                    break

    print(f"Total gallows-initial first tokens: {len(parsed_tokens)}\n")

    # === 1. TEMPLATE PATTERNS ===
    print("--- 1. MORPHOLOGICAL TEMPLATES ---\n")

    template_counts = Counter(p['template'] for p in parsed_tokens)
    print("Most common templates (GALLOWS+POST+M+SUFFIX):")
    for template, count in template_counts.most_common(20):
        print(f"  {template:20}: {count:4} ({count/len(parsed_tokens):.1%})")

    # === 2. POST BY GALLOWS ===
    print("\n--- 2. POST ELEMENT BY GALLOWS ---\n")

    post_by_gallows = defaultdict(Counter)
    for p in parsed_tokens:
        post_by_gallows[p['gallows']][p['post']] += 1

    print(f"{'Gallows':<8} {'ch':>8} {'sh':>8} {'o':>8} {'a':>8} {'e':>8} {'-':>8}")
    for g in ['p', 't', 'k', 'f']:
        counts = post_by_gallows[g]
        total = sum(counts.values())
        row = f"{g:<8}"
        for post in ['ch', 'sh', 'o', 'a', 'e', '-']:
            pct = counts[post] / total if total > 0 else 0
            row += f" {pct:>7.1%}"
        print(row)

    # === 3. SUFFIX BY GALLOWS ===
    print("\n--- 3. SUFFIX BY GALLOWS ---\n")

    suffix_by_gallows = defaultdict(Counter)
    for p in parsed_tokens:
        suffix_by_gallows[p['gallows']][p['suffix']] += 1

    # Get top suffixes
    all_suffixes = Counter()
    for p in parsed_tokens:
        all_suffixes[p['suffix']] += 1
    top_suffixes = [s for s, _ in all_suffixes.most_common(8)]

    print(f"{'Gallows':<8}", end='')
    for s in top_suffixes:
        print(f" {s:>7}", end='')
    print()

    for g in ['p', 't', 'k', 'f']:
        counts = suffix_by_gallows[g]
        total = sum(counts.values())
        row = f"{g:<8}"
        for s in top_suffixes:
            pct = counts[s] / total if total > 0 else 0
            row += f" {pct:>7.1%}"
        print(row)

    # === 4. MIDDLE PATTERNS ===
    print("\n--- 4. MIDDLE PATTERNS BY GALLOWS ---\n")

    middle_by_gallows = defaultdict(Counter)
    for p in parsed_tokens:
        if p['middle'] != '-':
            middle_by_gallows[p['gallows']][p['middle']] += 1

    for g in ['p', 't', 'k', 'f']:
        print(f"Most common MIDDLEs for '{g}':")
        for middle, count in middle_by_gallows[g].most_common(8):
            print(f"  {middle:12}: {count}")
        print()

    # === 5. COMPLETE TOKEN PATTERNS ===
    print("--- 5. FULL TOKEN PATTERNS ---\n")

    # Group by gallows and show most common full tokens
    tokens_by_gallows = defaultdict(Counter)
    for p in parsed_tokens:
        tokens_by_gallows[p['gallows']][p['original']] += 1

    for g in ['p', 't', 'k', 'f']:
        print(f"Top '{g}'-initial tokens with morphology:")
        for token, count in tokens_by_gallows[g].most_common(5):
            parsed = parse_gallows_token(token)
            print(f"  {token:15} = {parsed['gallows']}+{parsed['post']}+{parsed['middle']}+{parsed['suffix']} ({count})")
        print()

    # === 6. GALLOWS-SPECIFIC PATTERNS ===
    print("--- 6. DISTINCTIVE PATTERNS BY GALLOWS ---\n")

    # Find POST+SUFFIX combinations that are gallows-specific
    combo_by_gallows = defaultdict(Counter)
    for p in parsed_tokens:
        combo = f"{p['post']}...{p['suffix']}"
        combo_by_gallows[p['gallows']][combo] += 1

    # Find combinations that strongly prefer one gallows
    all_combos = set()
    for counts in combo_by_gallows.values():
        all_combos.update(counts.keys())

    print("POST+SUFFIX combinations with gallows preference:")
    for combo in sorted(all_combos):
        counts = {g: combo_by_gallows[g][combo] for g in GALLOWS}
        total = sum(counts.values())
        if total >= 10:
            max_g = max(counts, key=counts.get)
            if counts[max_g] / total >= 0.6:
                print(f"  {combo:15} prefers '{max_g}' ({counts[max_g]}/{total} = {counts[max_g]/total:.0%})")

    # === 7. MIDDLE SHARING ===
    print("\n--- 7. DO DIFFERENT GALLOWS SHARE MIDDLES? ---\n")

    # For each MIDDLE, which gallows use it?
    middle_to_gallows = defaultdict(set)
    middle_counts = Counter()
    for p in parsed_tokens:
        if p['middle'] != '-' and len(p['middle']) >= 2:
            middle_to_gallows[p['middle']].add(p['gallows'])
            middle_counts[p['middle']] += 1

    # Count MIDDLEs by number of gallows that use them
    shared_counts = Counter(len(gs) for gs in middle_to_gallows.values())
    print("MIDDLE sharing across gallows types:")
    for n_gallows, count in sorted(shared_counts.items()):
        print(f"  Used by {n_gallows} gallows type(s): {count} MIDDLEs")

    # Show examples of highly shared MIDDLEs
    print("\nMIDDLEs used by 3+ gallows types:")
    for middle, gallows_set in sorted(middle_to_gallows.items(), key=lambda x: -len(x[1])):
        if len(gallows_set) >= 3 and middle_counts[middle] >= 5:
            print(f"  {middle:12} used by {sorted(gallows_set)} ({middle_counts[middle]} times)")

    # === 8. TOKEN LENGTH ANALYSIS ===
    print("\n--- 8. TOKEN LENGTH BY COMPONENT ---\n")

    for g in ['p', 't', 'k', 'f']:
        tokens = [p for p in parsed_tokens if p['gallows'] == g]
        if tokens:
            avg_len = sum(len(p['original']) for p in tokens) / len(tokens)
            avg_middle = sum(len(p['middle']) for p in tokens if p['middle'] != '-') / max(1, sum(1 for p in tokens if p['middle'] != '-'))
            has_post = sum(1 for p in tokens if p['post'] != '-') / len(tokens)
            has_suffix = sum(1 for p in tokens if p['suffix'] != '-') / len(tokens)
            print(f"'{g}': len={avg_len:.1f}, middle={avg_middle:.1f}, has_post={has_post:.0%}, has_suffix={has_suffix:.0%}")

    # === VERDICT ===
    print("\n=== MORPHOLOGICAL VERDICT ===\n")

    # Summarize key differences
    print("Key morphological differences by gallows:\n")

    for g in ['p', 't', 'k', 'f']:
        counts = post_by_gallows[g]
        total = sum(counts.values())
        top_post = counts.most_common(1)[0] if counts else ('-', 0)

        suf_counts = suffix_by_gallows[g]
        top_suffix = suf_counts.most_common(1)[0] if suf_counts else ('-', 0)

        mid_counts = middle_by_gallows[g]
        top_middle = mid_counts.most_common(1)[0] if mid_counts else ('-', 0)

        print(f"'{g}': POST={top_post[0]}({top_post[1]/total:.0%}), "
              f"SUFFIX={top_suffix[0]}({top_suffix[1]/sum(suf_counts.values()):.0%}), "
              f"MIDDLE={top_middle[0]}({top_middle[1]})")

    # Save results
    output = {
        'template_counts': dict(template_counts.most_common(30)),
        'post_by_gallows': {g: dict(c) for g, c in post_by_gallows.items()},
        'suffix_by_gallows': {g: dict(c) for g, c in suffix_by_gallows.items()},
        'middle_sharing': {
            'by_1_gallows': shared_counts[1],
            'by_2_gallows': shared_counts[2],
            'by_3_gallows': shared_counts[3],
            'by_4_gallows': shared_counts.get(4, 0)
        }
    }

    with open(results_dir / 'gallows_morphology.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to gallows_morphology.json")

if __name__ == '__main__':
    main()
