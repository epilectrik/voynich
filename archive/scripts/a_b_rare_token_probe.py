"""
Probe: Are there RARE tokens that show A->B entry-level specificity?

The main probe showed all B folios share the same A vocabulary.
But maybe rare tokens (appearing in few folios) show specificity.
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

def load_data():
    """Load A and B data with folio tracking."""
    a_folio_tokens = defaultdict(set)  # token -> set of A folios
    b_folio_tokens = defaultdict(set)  # token -> set of B folios

    a_token_freq = Counter()
    b_token_freq = Counter()

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
                a_folio_tokens[token].add(folio)
                a_token_freq[token] += 1
            elif lang == 'B':
                b_folio_tokens[token].add(folio)
                b_token_freq[token] += 1

    return a_folio_tokens, b_folio_tokens, a_token_freq, b_token_freq

def analyze_rare_token_specificity():
    """Look for rare tokens that might show A-B specificity."""
    print("="*70)
    print("RARE TOKEN A-B SPECIFICITY PROBE")
    print("="*70)

    a_folio_tokens, b_folio_tokens, a_freq, b_freq = load_data()

    # Find shared tokens
    shared_tokens = set(a_folio_tokens.keys()) & set(b_folio_tokens.keys())
    print(f"\nShared tokens: {len(shared_tokens)}")

    # Analyze by rarity
    print("\n" + "-"*70)
    print("RARITY ANALYSIS")
    print("-"*70)

    # Categorize shared tokens by A-folio spread
    rare_in_a = []  # appear in <=3 A folios
    medium_in_a = []  # 4-10 A folios
    common_in_a = []  # >10 A folios

    for token in shared_tokens:
        n_a = len(a_folio_tokens[token])
        n_b = len(b_folio_tokens[token])

        if n_a <= 3:
            rare_in_a.append((token, n_a, n_b))
        elif n_a <= 10:
            medium_in_a.append((token, n_a, n_b))
        else:
            common_in_a.append((token, n_a, n_b))

    print(f"\nA-folio spread distribution of shared tokens:")
    print(f"  Rare (<=3 A folios): {len(rare_in_a)} tokens")
    print(f"  Medium (4-10 A folios): {len(medium_in_a)} tokens")
    print(f"  Common (>10 A folios): {len(common_in_a)} tokens")

    # For rare tokens, check if B spread is also restricted
    print("\n" + "-"*70)
    print("RARE TOKEN COUPLING TEST")
    print("-"*70)
    print("\nIf entry-level coupling: rare A tokens should appear in few B folios")
    print("If type-system only: rare A tokens should appear in many B folios")

    if rare_in_a:
        b_spreads = [x[2] for x in rare_in_a]
        print(f"\nRare-in-A tokens ({len(rare_in_a)} tokens):")
        print(f"  B-folio spread: mean={np.mean(b_spreads):.1f}, median={np.median(b_spreads):.1f}")
        print(f"  Range: [{min(b_spreads)}, {max(b_spreads)}]")

        # Correlation between A-spread and B-spread for rare tokens
        a_spreads = [x[1] for x in rare_in_a]
        rho = np.corrcoef(a_spreads, b_spreads)[0,1] if len(rare_in_a) > 2 else 0
        print(f"  A-B spread correlation: {rho:.3f}")

    if medium_in_a:
        b_spreads = [x[2] for x in medium_in_a]
        print(f"\nMedium-in-A tokens ({len(medium_in_a)} tokens):")
        print(f"  B-folio spread: mean={np.mean(b_spreads):.1f}, median={np.median(b_spreads):.1f}")

    if common_in_a:
        b_spreads = [x[2] for x in common_in_a]
        print(f"\nCommon-in-A tokens ({len(common_in_a)} tokens):")
        print(f"  B-folio spread: mean={np.mean(b_spreads):.1f}, median={np.median(b_spreads):.1f}")

    # Show specific examples of rare tokens
    print("\n" + "-"*70)
    print("EXAMPLES: Rare-in-A tokens")
    print("-"*70)
    print(f"\n{'Token':<15} {'A folios':>10} {'B folios':>10} {'A freq':>10} {'B freq':>10}")
    print("-" * 60)

    # Sort by A spread, then B spread
    for token, n_a, n_b in sorted(rare_in_a, key=lambda x: (x[1], x[2]))[:20]:
        print(f"{token:<15} {n_a:>10} {n_b:>10} {a_freq[token]:>10} {b_freq[token]:>10}")

    # Look for TRUE entry-level candidates: rare in A AND rare in B
    print("\n" + "-"*70)
    print("CANDIDATE ENTRY-LEVEL TOKENS (rare in A AND rare in B)")
    print("-"*70)

    candidates = [(t, na, nb) for t, na, nb in rare_in_a if nb <= 5]
    print(f"\nTokens appearing in <=3 A folios AND <=5 B folios: {len(candidates)}")

    if candidates:
        print(f"\n{'Token':<15} {'A folios':>10} {'B folios':>10}")
        print("-" * 40)
        for token, n_a, n_b in sorted(candidates, key=lambda x: x[1])[:15]:
            a_fols = sorted(a_folio_tokens[token])[:3]
            b_fols = sorted(b_folio_tokens[token])[:3]
            print(f"{token:<15} {n_a:>10} {n_b:>10}")
            print(f"  A: {', '.join(a_fols)}")
            print(f"  B: {', '.join(b_fols)}")

    # Statistical test: are rare-A tokens restricted in B more than expected?
    print("\n" + "-"*70)
    print("STATISTICAL TEST")
    print("-"*70)

    # Baseline: how spread are common-in-A tokens in B?
    if common_in_a and rare_in_a:
        common_b_spread = np.mean([x[2] for x in common_in_a])
        rare_b_spread = np.mean([x[2] for x in rare_in_a])

        print(f"\nMean B-folio spread:")
        print(f"  Common-in-A tokens: {common_b_spread:.1f} B folios")
        print(f"  Rare-in-A tokens: {rare_b_spread:.1f} B folios")
        print(f"  Ratio: {rare_b_spread/common_b_spread:.2f}x")

        if rare_b_spread < common_b_spread * 0.5:
            print("\n-> ENTRY-LEVEL SIGNAL: Rare-A tokens are restricted in B")
        elif rare_b_spread < common_b_spread * 0.8:
            print("\n-> WEAK SIGNAL: Some A-rarity correlates with B-rarity")
        else:
            print("\n-> NO SIGNAL: A-rarity doesn't predict B-spread")

    # Final interpretation
    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)

if __name__ == '__main__':
    analyze_rare_token_specificity()
