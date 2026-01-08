"""
HIGHER-ORDER SEQUENCE ANALYSIS

Do trigrams and 4-grams reveal structure beyond bigrams?

Tests:
1. Trigram entropy vs expected from bigram model
2. Most frequent trigrams (are there preferred 3-sequences?)
3. 4-gram analysis (diminishing returns expected)
4. Sequence compression (fewer patterns than expected = structure)

STRICTLY FORBIDDEN:
- Semantic inference
- External process mapping
- "Discovery" language
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from math import log2

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

def load_b_tokens():
    """Load Currier B tokens in sequence."""
    tokens_by_folio = defaultdict(list)

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            if row.get('language') != 'B':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            folio = row['folio']
            tokens_by_folio[folio].append(token)

    return tokens_by_folio

def compute_ngrams(tokens_by_folio, n):
    """Compute n-gram counts."""
    ngram_counts = Counter()
    total = 0

    for folio, tokens in tokens_by_folio.items():
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i+n])
            ngram_counts[ngram] += 1
            total += 1

    return ngram_counts, total

def compute_entropy(counts, total):
    """Compute entropy of distribution."""
    entropy = 0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * log2(p)
    return entropy

def analyze_ngram_level(tokens_by_folio, n, name):
    """Analyze n-grams at level n."""
    print(f"\n{'='*70}")
    print(f"{name.upper()} ANALYSIS (n={n})")
    print("="*70)

    ngram_counts, total = compute_ngrams(tokens_by_folio, n)

    print(f"\nTotal {name}s: {total}")
    print(f"Unique {name}s: {len(ngram_counts)}")

    # Entropy
    entropy = compute_entropy(ngram_counts, total)
    max_entropy = log2(len(ngram_counts)) if len(ngram_counts) > 0 else 0

    print(f"Entropy: {entropy:.3f} bits")
    print(f"Max possible: {max_entropy:.3f} bits")
    print(f"Efficiency: {entropy/max_entropy:.3f}" if max_entropy > 0 else "N/A")

    # Top n-grams
    print(f"\nTop 20 {name}s:")
    for ngram, count in ngram_counts.most_common(20):
        pct = 100 * count / total
        gram_str = " -> ".join(ngram)
        if len(gram_str) > 50:
            gram_str = gram_str[:47] + "..."
        print(f"  {count:>5} ({pct:>5.2f}%): {gram_str}")

    # Concentration
    top_10_count = sum(c for _, c in ngram_counts.most_common(10))
    top_50_count = sum(c for _, c in ngram_counts.most_common(50))
    top_100_count = sum(c for _, c in ngram_counts.most_common(100))

    print(f"\nConcentration:")
    print(f"  Top 10 cover: {100*top_10_count/total:.1f}%")
    print(f"  Top 50 cover: {100*top_50_count/total:.1f}%")
    print(f"  Top 100 cover: {100*top_100_count/total:.1f}%")

    # Hapax analysis
    hapax = sum(1 for c in ngram_counts.values() if c == 1)
    print(f"\nHapax (appear once): {hapax} ({100*hapax/len(ngram_counts):.1f}%)")

    return ngram_counts, total, entropy

def analyze_conditional_entropy(tokens_by_folio):
    """Compute conditional entropies to measure predictability gain."""
    print("\n" + "="*70)
    print("CONDITIONAL ENTROPY ANALYSIS")
    print("="*70)

    # Unigram entropy
    uni_counts, uni_total = compute_ngrams(tokens_by_folio, 1)
    h1 = compute_entropy(uni_counts, uni_total)

    # Bigram entropy
    bi_counts, bi_total = compute_ngrams(tokens_by_folio, 2)
    h2 = compute_entropy(bi_counts, bi_total)

    # Trigram entropy
    tri_counts, tri_total = compute_ngrams(tokens_by_folio, 3)
    h3 = compute_entropy(tri_counts, tri_total)

    # 4-gram entropy
    quad_counts, quad_total = compute_ngrams(tokens_by_folio, 4)
    h4 = compute_entropy(quad_counts, quad_total)

    # Conditional entropies
    # H(X_n | X_1...X_{n-1}) = H(X_1...X_n) - H(X_1...X_{n-1})
    h_1 = h1  # H(X_1)
    h_2_given_1 = h2 - h1  # H(X_2 | X_1)
    h_3_given_12 = h3 - h2  # H(X_3 | X_1, X_2)
    h_4_given_123 = h4 - h3  # H(X_4 | X_1, X_2, X_3)

    print("\nEntropy at each n-gram level:")
    print(f"  H(1-gram): {h1:.3f} bits")
    print(f"  H(2-gram): {h2:.3f} bits")
    print(f"  H(3-gram): {h3:.3f} bits")
    print(f"  H(4-gram): {h4:.3f} bits")

    print("\nConditional entropies (predictability of next token):")
    print(f"  H(X): {h_1:.3f} bits (no context)")
    print(f"  H(X | prev 1): {h_2_given_1:.3f} bits (1-token context)")
    print(f"  H(X | prev 2): {h_3_given_12:.3f} bits (2-token context)")
    print(f"  H(X | prev 3): {h_4_given_123:.3f} bits (3-token context)")

    print("\nPredictability gain from context:")
    print(f"  From 0->1 token context: {h_1 - h_2_given_1:.3f} bits ({100*(h_1 - h_2_given_1)/h_1:.1f}% reduction)")
    print(f"  From 1->2 token context: {h_2_given_1 - h_3_given_12:.3f} bits ({100*(h_2_given_1 - h_3_given_12)/h_2_given_1:.1f}% reduction)")
    print(f"  From 2->3 token context: {h_3_given_12 - h_4_given_123:.3f} bits ({100*(h_3_given_12 - h_4_given_123)/h_3_given_12:.1f}% reduction)")

    return {
        'h1': h1, 'h2': h2, 'h3': h3, 'h4': h4,
        'h_2_given_1': h_2_given_1,
        'h_3_given_12': h_3_given_12,
        'h_4_given_123': h_4_given_123
    }

def analyze_repeated_sequences(tokens_by_folio):
    """Find repeated sequences of varying lengths."""
    print("\n" + "="*70)
    print("REPEATED SEQUENCE ANALYSIS")
    print("="*70)

    for n in range(3, 8):
        ngram_counts, total = compute_ngrams(tokens_by_folio, n)
        repeated = sum(1 for c in ngram_counts.values() if c >= 2)
        frequent = sum(1 for c in ngram_counts.values() if c >= 5)
        very_frequent = sum(1 for c in ngram_counts.values() if c >= 10)

        print(f"\n{n}-grams: {len(ngram_counts)} unique, {total} total")
        print(f"  Repeated (>=2): {repeated} ({100*repeated/len(ngram_counts):.1f}%)")
        print(f"  Frequent (>=5): {frequent} ({100*frequent/len(ngram_counts):.1f}%)")
        print(f"  Very frequent (>=10): {very_frequent}")

        if n <= 5:
            print(f"  Top 5:")
            for ngram, count in ngram_counts.most_common(5):
                gram_str = " -> ".join(ngram)
                print(f"    {count:>4}x: {gram_str}")

def analyze_cross_folio_sequences(tokens_by_folio):
    """Check if certain sequences appear across multiple folios."""
    print("\n" + "="*70)
    print("CROSS-FOLIO SEQUENCE ANALYSIS")
    print("="*70)

    # Trigrams per folio
    trigram_folios = defaultdict(set)

    for folio, tokens in tokens_by_folio.items():
        for i in range(len(tokens) - 2):
            trigram = tuple(tokens[i:i+3])
            trigram_folios[trigram].add(folio)

    # Count by folio coverage
    coverage_counts = Counter(len(folios) for folios in trigram_folios.values())

    print("\nTrigram cross-folio distribution:")
    for n_folios in sorted(coverage_counts.keys())[:15]:
        count = coverage_counts[n_folios]
        print(f"  In {n_folios:>2} folios: {count:>5} trigrams")

    # Universal trigrams (appear in many folios)
    n_folios = len(tokens_by_folio)
    universal = [(tri, len(folios)) for tri, folios in trigram_folios.items()
                 if len(folios) >= n_folios * 0.3]

    print(f"\nUniversal trigrams (in >=30% of folios, n>={int(n_folios*0.3)}):")
    for tri, n in sorted(universal, key=lambda x: -x[1])[:15]:
        tri_str = " -> ".join(tri)
        print(f"  {n:>2} folios: {tri_str}")

def summarize(entropies):
    """Summarize findings."""
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print("\nKey findings:")

    # Diminishing returns
    gain_1_to_2 = entropies['h1'] - entropies['h_2_given_1']
    gain_2_to_3 = entropies['h_2_given_1'] - entropies['h_3_given_12']
    gain_3_to_4 = entropies['h_3_given_12'] - entropies['h_4_given_123']

    print(f"\n1. Predictability gain from context:")
    print(f"   - 1-token context: {gain_1_to_2:.3f} bits")
    print(f"   - 2-token context: +{gain_2_to_3:.3f} bits (additional)")
    print(f"   - 3-token context: +{gain_3_to_4:.3f} bits (additional)")

    if gain_2_to_3 < gain_1_to_2 * 0.3:
        print("   -> BIGRAM-DOMINANT: Most structure captured by adjacent pairs")
    elif gain_3_to_4 < gain_2_to_3 * 0.3:
        print("   -> TRIGRAM-RELEVANT: 2-token context adds meaningful structure")
    else:
        print("   -> LONG-RANGE: Significant structure beyond trigrams")

def main():
    print("="*70)
    print("HIGHER-ORDER SEQUENCE ANALYSIS")
    print("="*70)

    tokens_by_folio = load_b_tokens()
    print(f"\nLoaded {len(tokens_by_folio)} Currier B folios")

    # Analyze each level
    uni_counts, uni_total, h1 = analyze_ngram_level(tokens_by_folio, 1, "unigram")
    bi_counts, bi_total, h2 = analyze_ngram_level(tokens_by_folio, 2, "bigram")
    tri_counts, tri_total, h3 = analyze_ngram_level(tokens_by_folio, 3, "trigram")
    quad_counts, quad_total, h4 = analyze_ngram_level(tokens_by_folio, 4, "4-gram")

    # Conditional entropy analysis
    entropies = analyze_conditional_entropy(tokens_by_folio)

    # Repeated sequences
    analyze_repeated_sequences(tokens_by_folio)

    # Cross-folio patterns
    analyze_cross_folio_sequences(tokens_by_folio)

    # Summary
    summarize(entropies)

    print("\n" + "="*70)
    print("INTERPRETATION PENDING")
    print("="*70)

if __name__ == '__main__':
    main()
