"""
Substitutability Test: Are ch/sh (and ok/ot) truly interchangeable?

If sister pairs are grammatical alternatives, we should see:
1. Same predecessor leads to both ch-token and sh-token options
2. Minimal pairs: tokens differing only in prefix (chedy vs shedy)
3. Similar suffix distributions when preceded by same context

Tier 4 - Exploratory
"""

from collections import defaultdict, Counter
import math

PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

def load_currier_b_sequences():
    """Load Currier B tokens as sequences per line."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    lines = defaultdict(list)
    seen = set()

    with open(filepath, 'r', encoding='latin-1') as f:
        header = None
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split('\t')
            parts = [p.strip('"') for p in parts]

            if header is None:
                header = parts
                continue

            if len(parts) < 14:
                continue

            token = parts[0]
            folio = parts[2]
            currier = parts[6]
            transcriber = parts[12]
            line_num = parts[11]

            if currier == 'B' and transcriber == 'H' and token and '*' not in token:
                key = (folio, line_num, len(lines[(folio, line_num)]))
                if key not in seen:
                    seen.add(key)
                    lines[(folio, line_num)].append(token)

    return lines

def get_prefix(token):
    """Extract prefix from token."""
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return p
    return None

def get_suffix(token, prefix):
    """Extract everything after prefix."""
    if prefix and token.startswith(prefix):
        return token[len(prefix):]
    return token

def test_substitutability(lines):
    """Test if sister pairs are substitutable."""

    print("=" * 70)
    print("SUBSTITUTABILITY TEST: Are ch/sh grammatically interchangeable?")
    print("=" * 70)

    # === TEST 1: Shared predecessor contexts ===
    print("\n" + "-" * 70)
    print("TEST 1: Shared predecessor contexts")
    print("-" * 70)
    print("(Same token precedes both ch-X and sh-X)")

    # Map: predecessor -> {prefix -> [tokens that follow]}
    pred_to_followers = defaultdict(lambda: defaultdict(list))

    for (folio, line_num), tokens in lines.items():
        for i in range(1, len(tokens)):
            pred = tokens[i-1]
            curr = tokens[i]
            prefix = get_prefix(curr)
            if prefix:
                pred_to_followers[pred][prefix].append(curr)

    # Find predecessors that lead to both ch and sh
    shared_ch_sh = []
    shared_ok_ot = []

    for pred, prefix_followers in pred_to_followers.items():
        ch_followers = prefix_followers.get('ch', [])
        sh_followers = prefix_followers.get('sh', [])
        ok_followers = prefix_followers.get('ok', [])
        ot_followers = prefix_followers.get('ot', [])

        if ch_followers and sh_followers:
            shared_ch_sh.append((pred, ch_followers, sh_followers))
        if ok_followers and ot_followers:
            shared_ok_ot.append((pred, ok_followers, ot_followers))

    print(f"\nPredecessors leading to BOTH ch and sh: {len(shared_ch_sh)}")
    print(f"Predecessors leading to BOTH ok and ot: {len(shared_ok_ot)}")

    # Show top examples
    shared_ch_sh.sort(key=lambda x: -(len(x[1]) + len(x[2])))

    print("\n--- Top 15 CH/SH shared contexts ---")
    print(f"{'Predecessor':<15} {'CH tokens':<30} {'SH tokens':<30}")
    print("-" * 75)

    for pred, ch_list, sh_list in shared_ch_sh[:15]:
        ch_unique = list(set(ch_list))[:3]
        sh_unique = list(set(sh_list))[:3]
        ch_str = ', '.join(ch_unique) + (f"... +{len(set(ch_list))-3}" if len(set(ch_list)) > 3 else "")
        sh_str = ', '.join(sh_unique) + (f"... +{len(set(sh_list))-3}" if len(set(sh_list)) > 3 else "")
        print(f"{pred:<15} {ch_str:<30} {sh_str:<30}")

    print("\n--- Top 10 OK/OT shared contexts ---")
    shared_ok_ot.sort(key=lambda x: -(len(x[1]) + len(x[2])))

    for pred, ok_list, ot_list in shared_ok_ot[:10]:
        ok_unique = list(set(ok_list))[:3]
        ot_unique = list(set(ot_list))[:3]
        ok_str = ', '.join(ok_unique)
        ot_str = ', '.join(ot_unique)
        print(f"{pred:<15} {ok_str:<30} {ot_str:<30}")

    # === TEST 2: Minimal pairs ===
    print("\n" + "-" * 70)
    print("TEST 2: Minimal pairs (tokens differing only in prefix)")
    print("-" * 70)

    # Collect all tokens by suffix
    suffix_to_tokens = defaultdict(lambda: defaultdict(int))

    for (folio, line_num), tokens in lines.items():
        for token in tokens:
            prefix = get_prefix(token)
            if prefix:
                suffix = get_suffix(token, prefix)
                suffix_to_tokens[suffix][prefix] += 1

    # Find suffixes that appear with both ch and sh
    ch_sh_pairs = []
    ok_ot_pairs = []

    for suffix, prefix_counts in suffix_to_tokens.items():
        if 'ch' in prefix_counts and 'sh' in prefix_counts:
            ch_sh_pairs.append((suffix, prefix_counts['ch'], prefix_counts['sh']))
        if 'ok' in prefix_counts and 'ot' in prefix_counts:
            ok_ot_pairs.append((suffix, prefix_counts['ok'], prefix_counts['ot']))

    ch_sh_pairs.sort(key=lambda x: -(x[1] + x[2]))
    ok_ot_pairs.sort(key=lambda x: -(x[1] + x[2]))

    print(f"\nCH/SH minimal pairs (same suffix): {len(ch_sh_pairs)}")
    print(f"OK/OT minimal pairs (same suffix): {len(ok_ot_pairs)}")

    print("\n--- Top 20 CH/SH minimal pairs ---")
    print(f"{'Suffix':<15} {'ch-X count':<15} {'sh-X count':<15} {'Ratio':<10}")
    print("-" * 55)

    for suffix, ch_count, sh_count in ch_sh_pairs[:20]:
        ratio = ch_count / sh_count if sh_count > 0 else float('inf')
        ch_token = f"ch{suffix}"
        sh_token = f"sh{suffix}"
        print(f"{suffix:<15} {ch_count:<15} {sh_count:<15} {ratio:<10.2f}")

    print("\n--- Top 15 OK/OT minimal pairs ---")
    for suffix, ok_count, ot_count in ok_ot_pairs[:15]:
        ratio = ok_count / ot_count if ot_count > 0 else float('inf')
        print(f"{suffix:<15} {ok_count:<15} {ot_count:<15} {ratio:<10.2f}")

    # === TEST 3: Context-specific suffix distributions ===
    print("\n" + "-" * 70)
    print("TEST 3: Suffix distribution after same predecessor")
    print("-" * 70)
    print("(When preceded by same token, do ch and sh have similar suffixes?)")

    # For top shared predecessors, compare suffix distributions
    def get_suffix_dist(token_list):
        suffixes = Counter()
        for token in token_list:
            prefix = get_prefix(token)
            if prefix:
                suffix = get_suffix(token, prefix)
                suffixes[suffix] += 1
        return suffixes

    print("\n--- Suffix distributions for top CH/SH shared contexts ---")

    for pred, ch_list, sh_list in shared_ch_sh[:5]:
        ch_suffixes = get_suffix_dist(ch_list)
        sh_suffixes = get_suffix_dist(sh_list)

        print(f"\nAfter '{pred}':")
        print(f"  CH ({len(ch_list)} tokens): {dict(ch_suffixes.most_common(5))}")
        print(f"  SH ({len(sh_list)} tokens): {dict(sh_suffixes.most_common(5))}")

        # Calculate overlap
        ch_top = set(s for s, _ in ch_suffixes.most_common(5))
        sh_top = set(s for s, _ in sh_suffixes.most_common(5))
        overlap = ch_top & sh_top
        print(f"  Overlap in top 5 suffixes: {overlap}")

    # === TEST 4: Bigram substitution test ===
    print("\n" + "-" * 70)
    print("TEST 4: Trigram substitution patterns")
    print("-" * 70)
    print("(Find A -> ch-X -> B and A -> sh-X -> B patterns)")

    # Build trigrams
    trigram_counts = defaultdict(lambda: defaultdict(int))

    for (folio, line_num), tokens in lines.items():
        for i in range(1, len(tokens) - 1):
            prev = tokens[i-1]
            curr = tokens[i]
            next_tok = tokens[i+1]
            prefix = get_prefix(curr)
            if prefix in ['ch', 'sh', 'ok', 'ot']:
                context = (prev, next_tok)
                trigram_counts[context][prefix] += 1

    # Find contexts with both ch and sh
    substitutable_contexts = []
    for context, prefix_counts in trigram_counts.items():
        if 'ch' in prefix_counts and 'sh' in prefix_counts:
            substitutable_contexts.append((context, prefix_counts['ch'], prefix_counts['sh']))

    substitutable_contexts.sort(key=lambda x: -(x[1] + x[2]))

    print(f"\nContexts (A, B) where both A->ch-X->B and A->sh-X->B occur: {len(substitutable_contexts)}")

    print("\n--- Top 15 substitutable trigram contexts ---")
    print(f"{'Context (A...B)':<35} {'ch':<8} {'sh':<8} {'Ratio':<10}")
    print("-" * 60)

    for (prev, next_tok), ch_c, sh_c in substitutable_contexts[:15]:
        context_str = f"{prev} ... {next_tok}"
        ratio = ch_c / sh_c if sh_c > 0 else float('inf')
        print(f"{context_str:<35} {ch_c:<8} {sh_c:<8} {ratio:<10.2f}")

    # === TEST 5: Are minimal pairs used in same folios? ===
    print("\n" + "-" * 70)
    print("TEST 5: Minimal pair folio distribution")
    print("-" * 70)
    print("(Do ch-X and sh-X appear in the same or different folios?)")

    # For top minimal pairs, check folio overlap
    token_folios = defaultdict(set)
    for (folio, line_num), tokens in lines.items():
        for token in tokens:
            token_folios[token].add(folio)

    print("\n--- Folio patterns for top minimal pairs ---")
    print(f"{'Pair':<25} {'CH folios':<12} {'SH folios':<12} {'Overlap':<12} {'Jaccard':<10}")
    print("-" * 70)

    for suffix, ch_count, sh_count in ch_sh_pairs[:15]:
        if ch_count >= 5 and sh_count >= 5:  # Only consider frequent pairs
            ch_token = f"ch{suffix}"
            sh_token = f"sh{suffix}"

            ch_folios = token_folios[ch_token]
            sh_folios = token_folios[sh_token]

            overlap = len(ch_folios & sh_folios)
            union = len(ch_folios | sh_folios)
            jaccard = overlap / union if union > 0 else 0

            print(f"ch{suffix}/sh{suffix:<15} {len(ch_folios):<12} {len(sh_folios):<12} {overlap:<12} {jaccard:<10.2f}")

    # === SUMMARY ===
    print("\n" + "=" * 70)
    print("SUMMARY: Substitutability Evidence")
    print("=" * 70)

    print(f"""
Key findings:

1. SHARED CONTEXTS: {len(shared_ch_sh)} predecessors lead to both ch-X and sh-X
   This is strong evidence for grammatical interchangeability.

2. MINIMAL PAIRS: {len(ch_sh_pairs)} suffixes appear with both ch- and sh-
   These are true "ch/sh alternations" like chedy/shedy.

3. TRIGRAM SUBSTITUTION: {len(substitutable_contexts)} contexts where ch and sh
   can substitute in the same A...B frame.

4. FOLIO DISTRIBUTION: Check Jaccard scores above.
   - High Jaccard (>0.5) = same folios use both = free variation
   - Low Jaccard (<0.3) = different folios prefer different forms = conditioned
""")

if __name__ == '__main__':
    lines = load_currier_b_sequences()
    print(f"Loaded {len(lines)} lines from Currier B")
    test_substitutability(lines)
