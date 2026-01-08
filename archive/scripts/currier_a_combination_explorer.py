"""
Currier A Combination Explorer

Exploratory analysis of the 897 compositional patterns in Currier A.
Questions:
1. How many MIDDLEs appear with multiple PREFIXes?
2. What's the PREFIX x SUFFIX frequency matrix?
3. Is there clustering structure among combinations?

Tier 4 - Exploratory
"""

import os
import re
from collections import defaultdict, Counter
import math

# Known prefixes and suffixes from CAS-MORPH phase
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SUFFIXES = ['aiin', 'ain', 'ar', 'al', 'or', 'ol', 'am', 'an', 'in', 'y', 'dy', 'ey', 'edy', 'eedy', 'chy', 'shy', 'r', 'l', 's', 'd', 'n', 'm']

# Extended suffixes for better coverage
SUFFIX_PATTERNS = sorted(SUFFIXES, key=len, reverse=True)

def load_currier_a_tokens():
    """Load tokens from Currier A folios."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    tokens = []
    seen = set()  # For deduplication

    with open(filepath, 'r', encoding='latin-1') as f:
        header = None
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Handle quoted TSV format
            parts = line.split('\t')
            parts = [p.strip('"') for p in parts]

            if header is None:
                header = parts
                continue

            if len(parts) < 7:
                continue

            token = parts[0]      # "word" column
            folio = parts[2]      # "folio" column
            section = parts[3]    # "section" column (H, P, T, etc.)
            currier = parts[6]    # "language" column (A or B)
            transcriber = parts[12] if len(parts) > 12 else ''  # transcriber

            # Filter to Currier A, hand H (primary), skip damaged tokens
            if currier == 'A' and transcriber == 'H' and token and '*' not in token:
                key = (folio, token)
                if key not in seen:
                    seen.add(key)
                    tokens.append({'folio': folio, 'token': token, 'section': section})

    return tokens

def decompose_token(token):
    """Decompose token into PREFIX + MIDDLE + SUFFIX."""
    # Try each prefix
    prefix = None
    remainder = token

    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            remainder = token[len(p):]
            break

    if not prefix:
        return None, None, None

    # Try each suffix
    suffix = None
    middle = remainder

    for s in SUFFIX_PATTERNS:
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            middle = remainder[:-len(s)]
            break
        elif remainder == s:
            suffix = s
            middle = ''
            break

    if not suffix:
        # No recognized suffix - take last 1-2 chars as suffix
        if len(remainder) >= 2:
            suffix = remainder[-2:]
            middle = remainder[:-2]
        elif len(remainder) == 1:
            suffix = remainder
            middle = ''
        else:
            suffix = ''
            middle = ''

    return prefix, middle, suffix

def analyze_combinations(tokens):
    """Analyze all combinations."""

    # Decompose all tokens
    decomposed = []
    for t in tokens:
        prefix, middle, suffix = decompose_token(t['token'])
        if prefix:
            decomposed.append({
                'token': t['token'],
                'folio': t['folio'],
                'prefix': prefix,
                'middle': middle,
                'suffix': suffix
            })

    print(f"Total Currier A tokens: {len(tokens)}")
    print(f"Successfully decomposed: {len(decomposed)} ({100*len(decomposed)/len(tokens):.1f}%)")
    print()

    # === ANALYSIS 1: MIDDLE cross-family usage ===
    print("=" * 60)
    print("ANALYSIS 1: MIDDLE Cross-Family Usage")
    print("=" * 60)

    middle_to_prefixes = defaultdict(set)
    middle_counts = Counter()

    for d in decomposed:
        if d['middle']:  # Non-empty middle
            middle_to_prefixes[d['middle']].add(d['prefix'])
            middle_counts[d['middle']] += 1

    # Categorize middles
    exclusive_middles = []  # Only with 1 prefix
    shared_middles = []     # With 2+ prefixes

    for middle, prefixes in middle_to_prefixes.items():
        if len(prefixes) == 1:
            exclusive_middles.append((middle, list(prefixes)[0], middle_counts[middle]))
        else:
            shared_middles.append((middle, prefixes, middle_counts[middle]))

    print(f"\nTotal unique MIDDLEs: {len(middle_to_prefixes)}")
    print(f"PREFIX-exclusive MIDDLEs: {len(exclusive_middles)} ({100*len(exclusive_middles)/len(middle_to_prefixes):.1f}%)")
    print(f"Cross-family MIDDLEs: {len(shared_middles)} ({100*len(shared_middles)/len(middle_to_prefixes):.1f}%)")

    print("\n--- Top 20 CROSS-FAMILY MIDDLEs (appear with multiple prefixes) ---")
    shared_middles.sort(key=lambda x: x[2], reverse=True)
    for middle, prefixes, count in shared_middles[:20]:
        prefix_str = ', '.join(sorted(prefixes))
        print(f"  -{middle}- : {len(prefixes)} prefixes ({prefix_str}), {count} occurrences")

    print("\n--- PREFIX-exclusive MIDDLEs by prefix ---")
    by_prefix = defaultdict(list)
    for middle, prefix, count in exclusive_middles:
        by_prefix[prefix].append((middle, count))

    for prefix in PREFIXES:
        middles = by_prefix[prefix]
        middles.sort(key=lambda x: x[1], reverse=True)
        total = sum(c for _, c in middles)
        print(f"  {prefix}: {len(middles)} exclusive middles, {total} total occurrences")
        if middles[:3]:
            top3 = ', '.join(f"-{m}-({c})" for m, c in middles[:3])
            print(f"       Top 3: {top3}")

    # === ANALYSIS 2: PREFIX x SUFFIX matrix ===
    print("\n" + "=" * 60)
    print("ANALYSIS 2: PREFIX x SUFFIX Frequency Matrix")
    print("=" * 60)

    prefix_suffix_counts = defaultdict(Counter)
    suffix_totals = Counter()
    prefix_totals = Counter()

    for d in decomposed:
        prefix_suffix_counts[d['prefix']][d['suffix']] += 1
        suffix_totals[d['suffix']] += 1
        prefix_totals[d['prefix']] += 1

    # Get top suffixes
    top_suffixes = [s for s, _ in suffix_totals.most_common(12)]

    # Print matrix
    print(f"\n{'PREFIX':<8}", end='')
    for suffix in top_suffixes:
        print(f"{suffix:>8}", end='')
    print(f"{'TOTAL':>8}")
    print("-" * (8 + 8 * (len(top_suffixes) + 1)))

    for prefix in PREFIXES:
        print(f"{prefix:<8}", end='')
        for suffix in top_suffixes:
            count = prefix_suffix_counts[prefix][suffix]
            print(f"{count:>8}", end='')
        print(f"{prefix_totals[prefix]:>8}")

    print("-" * (8 + 8 * (len(top_suffixes) + 1)))
    print(f"{'TOTAL':<8}", end='')
    for suffix in top_suffixes:
        print(f"{suffix_totals[suffix]:>8}", end='')
    print(f"{sum(prefix_totals.values()):>8}")

    # === ANALYSIS 3: Parallel entries ===
    print("\n" + "=" * 60)
    print("ANALYSIS 3: Parallel Entries (same MIDDLE+SUFFIX, different PREFIX)")
    print("=" * 60)

    middle_suffix_to_prefixes = defaultdict(lambda: defaultdict(int))

    for d in decomposed:
        key = (d['middle'], d['suffix'])
        middle_suffix_to_prefixes[key][d['prefix']] += 1

    # Find parallel entries (same middle+suffix with 2+ prefixes)
    parallels = []
    for (middle, suffix), prefix_counts in middle_suffix_to_prefixes.items():
        if len(prefix_counts) >= 2:
            total = sum(prefix_counts.values())
            parallels.append((middle, suffix, dict(prefix_counts), total))

    parallels.sort(key=lambda x: x[3], reverse=True)

    print(f"\nParallel entry patterns found: {len(parallels)}")
    print("\n--- Top 20 Parallel Patterns ---")
    for middle, suffix, prefix_counts, total in parallels[:20]:
        if middle:
            pattern = f"-{middle}-{suffix}"
        else:
            pattern = f"-{suffix}"
        prefix_str = ', '.join(f"{p}({c})" for p, c in sorted(prefix_counts.items(), key=lambda x: -x[1]))
        print(f"  {pattern:<20} : {prefix_str}")

    # === ANALYSIS 4: Unique complete combinations ===
    print("\n" + "=" * 60)
    print("ANALYSIS 4: Unique Combinations Summary")
    print("=" * 60)

    unique_tokens = set(d['token'] for d in decomposed)
    unique_combos = set((d['prefix'], d['middle'], d['suffix']) for d in decomposed)

    print(f"\nUnique tokens: {len(unique_tokens)}")
    print(f"Unique (PREFIX, MIDDLE, SUFFIX) combinations: {len(unique_combos)}")

    # Combination richness by prefix
    print("\n--- Combinations by PREFIX ---")
    combos_by_prefix = defaultdict(set)
    for d in decomposed:
        combos_by_prefix[d['prefix']].add((d['middle'], d['suffix']))

    for prefix in PREFIXES:
        combos = combos_by_prefix[prefix]
        print(f"  {prefix}: {len(combos)} unique MIDDLE+SUFFIX combinations")

    # === ANALYSIS 5: Suffix meaning speculation ===
    print("\n" + "=" * 60)
    print("ANALYSIS 5: Suffix Distribution Patterns (Speculation)")
    print("=" * 60)

    # Calculate enrichment ratios for each prefix-suffix pair
    total_tokens = len(decomposed)

    print("\nEnrichment ratios (observed/expected) for top prefix-suffix pairs:")
    print("Values > 1.5 suggest ATTRACTION, < 0.5 suggest AVOIDANCE\n")

    enrichments = []
    for prefix in PREFIXES:
        p_rate = prefix_totals[prefix] / total_tokens
        for suffix in top_suffixes[:8]:
            s_rate = suffix_totals[suffix] / total_tokens
            expected = p_rate * s_rate * total_tokens
            observed = prefix_suffix_counts[prefix][suffix]
            if expected > 0:
                ratio = observed / expected
                enrichments.append((prefix, suffix, observed, expected, ratio))

    # Print notable enrichments
    print("STRONG ATTRACTIONS (ratio > 2.0):")
    for prefix, suffix, obs, exp, ratio in sorted(enrichments, key=lambda x: -x[4]):
        if ratio > 2.0 and obs > 50:
            print(f"  {prefix}+{suffix}: {ratio:.2f}x ({obs} obs, {exp:.0f} exp)")

    print("\nSTRONG AVOIDANCES (ratio < 0.5):")
    for prefix, suffix, obs, exp, ratio in sorted(enrichments, key=lambda x: x[4]):
        if ratio < 0.5 and exp > 50:
            print(f"  {prefix}+{suffix}: {ratio:.2f}x ({obs} obs, {exp:.0f} exp)")

    # === ANALYSIS 6: Are there "synonym" patterns? ===
    print("\n" + "=" * 60)
    print("ANALYSIS 6: Potential Synonyms (different tokens, same distribution)")
    print("=" * 60)

    # Group tokens by their folio distribution
    token_folios = defaultdict(set)
    for d in decomposed:
        token_folios[d['token']].add(d['folio'])

    # Find tokens with identical folio sets
    folio_sig_to_tokens = defaultdict(list)
    for token, folios in token_folios.items():
        sig = tuple(sorted(folios))
        folio_sig_to_tokens[sig].append(token)

    # Find groups with multiple tokens
    synonym_candidates = [(folios, tokens) for folios, tokens in folio_sig_to_tokens.items()
                          if len(tokens) > 1 and len(folios) >= 2]

    synonym_candidates.sort(key=lambda x: -len(x[0]))

    print(f"\nToken groups with identical folio distribution: {len(synonym_candidates)}")
    print("\n--- Top 10 'Synonym' Candidates ---")
    for folios, tokens in synonym_candidates[:10]:
        print(f"  Folios: {len(folios)} | Tokens: {', '.join(sorted(tokens)[:5])}" +
              (f"... +{len(tokens)-5} more" if len(tokens) > 5 else ""))

    return decomposed, middle_to_prefixes, shared_middles

if __name__ == '__main__':
    tokens = load_currier_a_tokens()
    decomposed, middle_to_prefixes, shared_middles = analyze_combinations(tokens)
