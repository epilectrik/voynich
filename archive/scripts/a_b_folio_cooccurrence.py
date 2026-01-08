"""
Test: Do specific A folios predict specific B folios via shared rare tokens?

If ENTRY-LEVEL coupling: tokens appearing in A-folio X should cluster in specific B folios
If FREQUENCY artifact: tokens are just rare everywhere, no A-B folio relationship
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from itertools import combinations

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

def load_data():
    """Load token-folio mappings."""
    a_folio_tokens = defaultdict(set)  # folio -> set of tokens
    b_folio_tokens = defaultdict(set)  # folio -> set of tokens
    token_a_folios = defaultdict(set)  # token -> set of A folios
    token_b_folios = defaultdict(set)  # token -> set of B folios

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            folio = row['folio']
            lang = row.get('language', '')

            if lang == 'A':
                a_folio_tokens[folio].add(token)
                token_a_folios[token].add(folio)
            elif lang == 'B':
                b_folio_tokens[folio].add(token)
                token_b_folios[token].add(folio)

    return a_folio_tokens, b_folio_tokens, token_a_folios, token_b_folios

def test_folio_coupling():
    """Test if A-B folio pairs share more rare tokens than expected."""
    print("="*70)
    print("A-B FOLIO CO-OCCURRENCE TEST")
    print("="*70)

    a_folio_tokens, b_folio_tokens, token_a_folios, token_b_folios = load_data()

    # Find shared vocabulary
    all_a_tokens = set(token_a_folios.keys())
    all_b_tokens = set(token_b_folios.keys())
    shared_tokens = all_a_tokens & all_b_tokens

    # Identify rare shared tokens (<=3 A folios, <=5 B folios)
    rare_tokens = set()
    for token in shared_tokens:
        if len(token_a_folios[token]) <= 3 and len(token_b_folios[token]) <= 5:
            rare_tokens.add(token)

    print(f"\nShared tokens: {len(shared_tokens)}")
    print(f"Rare shared tokens: {len(rare_tokens)}")

    # Build A-B folio co-occurrence matrix via rare tokens
    print("\n" + "-"*70)
    print("A-B FOLIO PAIRING VIA RARE TOKENS")
    print("-"*70)

    # For each A folio, count which B folios share rare tokens
    a_b_rare_overlap = defaultdict(Counter)

    for token in rare_tokens:
        a_fols = token_a_folios[token]
        b_fols = token_b_folios[token]
        for a_f in a_fols:
            for b_f in b_fols:
                a_b_rare_overlap[a_f][b_f] += 1

    # Analyze: are there "hot" A-B pairs?
    pair_counts = []
    for a_f, b_counts in a_b_rare_overlap.items():
        for b_f, count in b_counts.items():
            pair_counts.append((a_f, b_f, count))

    if pair_counts:
        counts_only = [x[2] for x in pair_counts]
        print(f"\nA-B pairs with rare token overlap: {len(pair_counts)}")
        print(f"Rare token overlap per pair: mean={np.mean(counts_only):.2f}, max={max(counts_only)}")

        # Top pairs
        print(f"\nTop 15 A-B folio pairs by rare token overlap:")
        print(f"{'A folio':<12} {'B folio':<12} {'Overlap':>10}")
        print("-" * 40)
        for a_f, b_f, count in sorted(pair_counts, key=lambda x: -x[2])[:15]:
            print(f"{a_f:<12} {b_f:<12} {count:>10}")

        # Distribution analysis
        print(f"\nOverlap distribution:")
        for threshold in [1, 2, 3, 5, 10]:
            n = sum(1 for c in counts_only if c >= threshold)
            print(f"  Pairs with >={threshold} shared rare tokens: {n}")

    # Test: Is overlap more concentrated than expected?
    print("\n" + "-"*70)
    print("CONCENTRATION TEST")
    print("-"*70)

    # If entry-level: some A folios should have HIGH overlap with few B folios
    # If random: overlap should be uniform across B folios

    concentration_scores = []
    for a_f, b_counts in a_b_rare_overlap.items():
        if not b_counts:
            continue
        total = sum(b_counts.values())
        top_5 = sum(c for _, c in b_counts.most_common(5))
        concentration = top_5 / total if total > 0 else 0
        concentration_scores.append({
            'a_folio': a_f,
            'total_overlap': total,
            'n_b_folios': len(b_counts),
            'concentration': concentration
        })

    if concentration_scores:
        concs = [x['concentration'] for x in concentration_scores]
        n_b = [x['n_b_folios'] for x in concentration_scores]

        print(f"\nA folios with rare token B-overlap: {len(concentration_scores)}")
        print(f"B folios per A folio: mean={np.mean(n_b):.1f}, std={np.std(n_b):.1f}")
        print(f"Top-5 B concentration: mean={np.mean(concs):.1%}, std={np.std(concs):.1%}")

        # Expected if uniform across ~82 B folios
        expected_conc = min(5 / np.mean(n_b), 1.0)
        print(f"\nExpected concentration if uniform: {expected_conc:.1%}")
        print(f"Observed/Expected: {np.mean(concs)/expected_conc:.2f}x")

    # One-to-one test: for tokens in exactly 1 A folio and 1 B folio
    print("\n" + "-"*70)
    print("ONE-TO-ONE TOKEN TEST")
    print("-"*70)

    one_to_one = []
    for token in rare_tokens:
        if len(token_a_folios[token]) == 1 and len(token_b_folios[token]) == 1:
            a_f = list(token_a_folios[token])[0]
            b_f = list(token_b_folios[token])[0]
            one_to_one.append((token, a_f, b_f))

    print(f"\nTokens appearing in exactly 1 A folio and 1 B folio: {len(one_to_one)}")

    if one_to_one:
        # Count unique A-B pairs
        unique_pairs = set((a, b) for _, a, b in one_to_one)
        print(f"Unique A-B pairs from 1:1 tokens: {len(unique_pairs)}")

        # If entry-level: same A-B pair should appear multiple times
        # If random: pairs should be scattered

        pair_freq = Counter((a, b) for _, a, b in one_to_one)
        print(f"\n1:1 token pairs by frequency:")
        for threshold in [1, 2, 3, 4, 5]:
            n = sum(1 for c in pair_freq.values() if c >= threshold)
            print(f"  Pairs with >={threshold} 1:1 tokens: {n}")

        # Top pairs
        print(f"\nTop A-B pairs by 1:1 token count:")
        print(f"{'A folio':<12} {'B folio':<12} {'1:1 tokens':>12}")
        print("-" * 40)
        for (a_f, b_f), count in pair_freq.most_common(10):
            if count > 1:
                print(f"{a_f:<12} {b_f:<12} {count:>12}")

        # Show example tokens for top pairs
        if pair_freq.most_common(1)[0][1] > 1:
            print(f"\nExample tokens for top pair:")
            top_pair = pair_freq.most_common(1)[0][0]
            examples = [t for t, a, b in one_to_one if (a, b) == top_pair][:5]
            for token in examples:
                print(f"  {token}")

    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)

if __name__ == '__main__':
    test_folio_coupling()
