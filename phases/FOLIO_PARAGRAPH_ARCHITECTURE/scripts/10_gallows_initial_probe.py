"""
10_gallows_initial_probe.py - Investigate paragraph-initial gallows

Questions:
1. Are gallows part of a token or standalone?
2. Do they mark procedure type?
3. Do they always show up in same order?
4. Are there patterns within folios?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Gallows characters
GALLOWS = {'t', 'k', 'p', 'f'}
BENCH_GALLOWS = {'t', 'k'}  # More common
RARE_GALLOWS = {'p', 'f'}   # Less common

def extract_gallows(word):
    """Extract gallows character(s) from word."""
    gallows_found = []
    for i, c in enumerate(word):
        if c in GALLOWS:
            gallows_found.append((c, i))
    return gallows_found

def get_initial_gallows(word):
    """Get gallows if word starts with one (possibly after 'c' or 'q')."""
    if not word:
        return None, None

    # Direct gallows initial
    if word[0] in GALLOWS:
        return word[0], 'direct'

    # c + gallows (like 'ct', 'ck')
    if len(word) >= 2 and word[0] == 'c' and word[1] in GALLOWS:
        return word[1], 'c-prefixed'

    # q + gallows (like 'qk', 'qt')
    if len(word) >= 2 and word[0] == 'q' and word[1] in GALLOWS:
        return word[1], 'q-prefixed'

    # o + gallows (like 'ok', 'ot')
    if len(word) >= 2 and word[0] == 'o' and word[1] in GALLOWS:
        return word[1], 'o-prefixed'

    return None, None

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load census
    with open(results_dir / 'folio_paragraph_census.json') as f:
        census = json.load(f)

    # Load paragraph tokens
    par_results = Path(__file__).resolve().parents[2] / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Load paragraph inventory for line info
    with open(par_results / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    par_to_info = {p['par_id']: p for p in inventory['paragraphs']}

    print("=== PARAGRAPH-INITIAL GALLOWS PROBE ===\n")

    # Collect first tokens of each paragraph
    first_tokens = []
    gallows_initial_pars = []
    non_gallows_initial = []

    for folio_entry in census['folios']:
        for par_info in folio_entry['paragraphs']:
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])

            # Get first valid token
            first_token = None
            for t in tokens:
                word = t['word']
                if word and '*' not in word:
                    first_token = word
                    break

            if first_token:
                gallows, gtype = get_initial_gallows(first_token)
                first_tokens.append({
                    'par_id': par_id,
                    'folio': folio_entry['folio'],
                    'first_token': first_token,
                    'gallows': gallows,
                    'gallows_type': gtype
                })

                if gallows:
                    gallows_initial_pars.append(first_tokens[-1])
                else:
                    non_gallows_initial.append(first_tokens[-1])

    # === 1. GALLOWS INITIAL RATE ===
    print("--- 1. GALLOWS INITIAL RATE ---\n")

    total = len(first_tokens)
    gallows_count = len(gallows_initial_pars)

    print(f"Total paragraphs with first token: {total}")
    print(f"Gallows-initial: {gallows_count} ({gallows_count/total:.1%})")

    # By type
    type_counts = Counter(p['gallows_type'] for p in gallows_initial_pars)
    print(f"\nBy gallows position:")
    for gtype, count in type_counts.most_common():
        print(f"  {gtype}: {count} ({count/gallows_count:.1%})")

    # === 2. WHICH GALLOWS? ===
    print("\n--- 2. WHICH GALLOWS CHARACTER? ---\n")

    gallows_counts = Counter(p['gallows'] for p in gallows_initial_pars)
    print("Gallows frequency at paragraph start:")
    for g, count in gallows_counts.most_common():
        print(f"  {g}: {count} ({count/gallows_count:.1%})")

    # === 3. FULL TOKEN ANALYSIS ===
    print("\n--- 3. FIRST TOKEN PATTERNS ---\n")

    token_counts = Counter(p['first_token'] for p in gallows_initial_pars)
    print("Most common gallows-initial first tokens:")
    for token, count in token_counts.most_common(20):
        gallows, gtype = get_initial_gallows(token)
        print(f"  {token:15} ({gallows}/{gtype}): {count}")

    # === 4. NON-GALLOWS INITIAL ===
    print("\n--- 4. NON-GALLOWS INITIAL TOKENS ---\n")

    non_gallows_tokens = Counter(p['first_token'] for p in non_gallows_initial)
    print(f"Non-gallows initial paragraphs: {len(non_gallows_initial)} ({len(non_gallows_initial)/total:.1%})")
    print("\nMost common non-gallows first tokens:")
    for token, count in non_gallows_tokens.most_common(15):
        print(f"  {token:15}: {count}")

    # === 5. GALLOWS SEQUENCES WITHIN FOLIO ===
    print("\n--- 5. GALLOWS SEQUENCES WITHIN FOLIO ---\n")

    folio_sequences = defaultdict(list)
    for p in first_tokens:
        folio_sequences[p['folio']].append(p['gallows'] if p['gallows'] else '-')

    # Analyze sequences
    sequence_counts = Counter()
    for folio, seq in folio_sequences.items():
        if len(seq) >= 2:
            seq_str = ''.join(seq)
            sequence_counts[seq_str] += 1

    print("Most common folio gallows sequences:")
    for seq, count in sequence_counts.most_common(15):
        print(f"  {seq}: {count}")

    # Look for repeated patterns
    print("\n--- REPEATED GALLOWS WITHIN FOLIO ---")

    repeat_analysis = defaultdict(int)
    for folio, seq in folio_sequences.items():
        gallows_only = [g for g in seq if g != '-']
        if len(gallows_only) >= 2:
            # Check if same gallows repeats
            if len(set(gallows_only)) == 1:
                repeat_analysis['all_same'] += 1
            elif gallows_only[0] == gallows_only[-1]:
                repeat_analysis['first_last_same'] += 1
            else:
                repeat_analysis['varied'] += 1

    print(f"All paragraphs same gallows: {repeat_analysis['all_same']}")
    print(f"First/last same gallows: {repeat_analysis['first_last_same']}")
    print(f"Varied gallows: {repeat_analysis['varied']}")

    # === 6. GALLOWS ORDER PATTERNS ===
    print("\n--- 6. GALLOWS ORDER PATTERNS ---\n")

    # Check if there's a preferred order
    bigram_counts = Counter()
    for folio, seq in folio_sequences.items():
        gallows_only = [g for g in seq if g != '-']
        for i in range(len(gallows_only) - 1):
            bigram = gallows_only[i] + gallows_only[i+1]
            bigram_counts[bigram] += 1

    print("Gallows bigrams (consecutive paragraphs):")
    for bigram, count in bigram_counts.most_common(15):
        print(f"  {bigram[0]} -> {bigram[1]}: {count}")

    # Self-transitions
    print("\nSelf-transitions (same gallows consecutive):")
    for g in GALLOWS:
        self_count = bigram_counts[g+g]
        total_from_g = sum(bigram_counts[g+g2] for g2 in GALLOWS)
        if total_from_g > 0:
            print(f"  {g} -> {g}: {self_count}/{total_from_g} ({self_count/total_from_g:.1%})")

    # === 7. GALLOWS vs PARAGRAPH ORDINAL ===
    print("\n--- 7. GALLOWS BY PARAGRAPH ORDINAL ---\n")

    ordinal_gallows = defaultdict(Counter)
    for folio_entry in census['folios']:
        for i, par_info in enumerate(folio_entry['paragraphs']):
            par_id = par_info['par_id']
            match = next((p for p in first_tokens if p['par_id'] == par_id), None)
            if match and match['gallows']:
                ordinal = min(i + 1, 6)
                ordinal_gallows[ordinal][match['gallows']] += 1

    print(f"{'Ordinal':<10} {'t':>6} {'k':>6} {'p':>6} {'f':>6}")
    for ordinal in sorted(ordinal_gallows.keys()):
        counts = ordinal_gallows[ordinal]
        total_ord = sum(counts.values())
        row = f"{ordinal:<10}"
        for g in ['t', 'k', 'p', 'f']:
            pct = counts[g] / total_ord if total_ord > 0 else 0
            row += f" {pct:>5.1%}"
        print(row)

    # === 8. SECTION PATTERNS ===
    print("\n--- 8. GALLOWS BY SECTION ---\n")

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

    section_gallows = defaultdict(Counter)
    for p in gallows_initial_pars:
        section = get_section(p['folio'])
        section_gallows[section][p['gallows']] += 1

    print(f"{'Section':<12} {'t':>6} {'k':>6} {'p':>6} {'f':>6} {'Total':>8}")
    for section in sorted(section_gallows.keys()):
        counts = section_gallows[section]
        total_sec = sum(counts.values())
        row = f"{section:<12}"
        for g in ['t', 'k', 'p', 'f']:
            pct = counts[g] / total_sec if total_sec > 0 else 0
            row += f" {pct:>5.1%}"
        row += f" {total_sec:>8}"
        print(row)

    # === VERDICT ===
    print("\n=== VERDICT ===\n")

    # Is it standalone or part of token?
    standalone_like = sum(1 for p in gallows_initial_pars
                         if len(p['first_token']) <= 3 and p['gallows_type'] == 'direct')
    token_like = gallows_count - standalone_like

    print(f"Token structure: {token_like} integrated ({token_like/gallows_count:.1%}), "
          f"{standalone_like} possibly standalone ({standalone_like/gallows_count:.1%})")

    # Is order consistent?
    most_common_bigram = bigram_counts.most_common(1)[0] if bigram_counts else (None, 0)
    total_bigrams = sum(bigram_counts.values())

    if most_common_bigram[1] / total_bigrams > 0.3:
        print(f"Order: PREFERRED pattern {most_common_bigram[0]} ({most_common_bigram[1]/total_bigrams:.1%})")
    else:
        print("Order: NO dominant pattern")

    # Save results
    output = {
        'gallows_initial_rate': gallows_count / total,
        'gallows_distribution': dict(gallows_counts),
        'common_tokens': dict(token_counts.most_common(30)),
        'folio_sequences': {k: v for k, v in list(folio_sequences.items())[:20]},
        'bigram_counts': dict(bigram_counts),
        'ordinal_distribution': {k: dict(v) for k, v in ordinal_gallows.items()},
        'section_distribution': {k: dict(v) for k, v in section_gallows.items()}
    }

    with open(results_dir / 'gallows_initial_probe.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to gallows_initial_probe.json")

if __name__ == '__main__':
    main()
