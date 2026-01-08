"""
TRANSITION ENRICHMENT PROBE

We know 17 transitions are FORBIDDEN. But what transitions are ENRICHED?

This probe identifies:
1. Which token-pair transitions occur MORE than expected by chance
2. Whether enrichment patterns reveal grammatical structure
3. If there's a small set of "preferred" transitions (like there's a small set of forbidden)

STRICTLY FORBIDDEN:
- Semantic inference from enrichment
- External process mapping
- Forcing "discovery"
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import chi2_contingency
import json

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

def compute_enrichment(tokens_by_folio):
    """Compute transition enrichment ratios."""
    print("="*70)
    print("TRANSITION ENRICHMENT ANALYSIS")
    print("="*70)

    # Build transition counts
    bigram_counts = Counter()
    unigram_counts = Counter()
    total_bigrams = 0

    for folio, tokens in tokens_by_folio.items():
        for i, token in enumerate(tokens):
            unigram_counts[token] += 1
            if i > 0:
                prev = tokens[i-1]
                bigram_counts[(prev, token)] += 1
                total_bigrams += 1

    total_unigrams = sum(unigram_counts.values())

    print(f"\nCorpus: {len(tokens_by_folio)} folios")
    print(f"Unigrams: {total_unigrams} tokens, {len(unigram_counts)} types")
    print(f"Bigrams: {total_bigrams} transitions, {len(bigram_counts)} types")

    # Compute expected frequencies under independence
    # P(A->B) = P(A) * P(B) under independence
    enrichment = {}

    for (t1, t2), observed in bigram_counts.items():
        p1 = unigram_counts[t1] / total_unigrams
        p2 = unigram_counts[t2] / total_unigrams
        expected = p1 * p2 * total_bigrams

        if expected > 0:
            ratio = observed / expected
            enrichment[(t1, t2)] = {
                'observed': observed,
                'expected': expected,
                'ratio': ratio,
                't1_freq': unigram_counts[t1],
                't2_freq': unigram_counts[t2]
            }

    return enrichment, bigram_counts, unigram_counts, total_bigrams

def analyze_enrichment(enrichment, bigram_counts, unigram_counts, total_bigrams):
    """Analyze enrichment patterns."""
    print("\n" + "-"*70)
    print("ENRICHMENT DISTRIBUTION")
    print("-"*70)

    ratios = [e['ratio'] for e in enrichment.values()]

    print(f"\nEnrichment ratio statistics:")
    print(f"  Min: {min(ratios):.3f}")
    print(f"  Max: {max(ratios):.3f}")
    print(f"  Mean: {np.mean(ratios):.3f}")
    print(f"  Median: {np.median(ratios):.3f}")
    print(f"  Std: {np.std(ratios):.3f}")

    # Count by enrichment level
    print(f"\nEnrichment distribution:")
    for threshold in [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]:
        n_above = sum(1 for r in ratios if r >= threshold)
        print(f"  >= {threshold:5.1f}x: {n_above:5d} ({100*n_above/len(ratios):5.1f}%)")

    # Top enriched transitions (with minimum support)
    print("\n" + "-"*70)
    print("TOP ENRICHED TRANSITIONS (min 10 occurrences)")
    print("-"*70)

    filtered = [(k, v) for k, v in enrichment.items() if v['observed'] >= 10]
    sorted_enriched = sorted(filtered, key=lambda x: -x[1]['ratio'])

    print(f"\n{'Transition':<25} {'Observed':>8} {'Expected':>8} {'Ratio':>8}")
    print("-" * 55)
    for (t1, t2), data in sorted_enriched[:30]:
        trans = f"{t1} -> {t2}"
        print(f"{trans:<25} {data['observed']:>8} {data['expected']:>8.1f} {data['ratio']:>8.1f}x")

    # Self-transitions
    print("\n" + "-"*70)
    print("SELF-TRANSITIONS (token -> same token)")
    print("-"*70)

    self_trans = [(k, v) for k, v in enrichment.items() if k[0] == k[1] and v['observed'] >= 5]
    self_trans_sorted = sorted(self_trans, key=lambda x: -x[1]['ratio'])

    print(f"\n{'Token':<20} {'Observed':>8} {'Expected':>8} {'Ratio':>8}")
    print("-" * 50)
    for (t1, _), data in self_trans_sorted[:20]:
        print(f"{t1:<20} {data['observed']:>8} {data['expected']:>8.1f} {data['ratio']:>8.1f}x")

    # Average self-transition enrichment
    self_ratios = [v['ratio'] for k, v in enrichment.items() if k[0] == k[1] and v['observed'] >= 3]
    if self_ratios:
        print(f"\nSelf-transition enrichment: mean={np.mean(self_ratios):.2f}x, median={np.median(self_ratios):.2f}x")

    return sorted_enriched

def analyze_suppression(enrichment):
    """Analyze suppressed (avoided) transitions."""
    print("\n" + "-"*70)
    print("SUPPRESSED TRANSITIONS (avoided more than expected)")
    print("-"*70)

    # Look for transitions with low enrichment (but enough data to be meaningful)
    suppressed = [(k, v) for k, v in enrichment.items()
                  if v['expected'] >= 5 and v['ratio'] < 0.5]
    suppressed_sorted = sorted(suppressed, key=lambda x: x[1]['ratio'])

    print(f"\nTransitions with expected >= 5 and ratio < 0.5:")
    print(f"Found: {len(suppressed_sorted)}")

    if suppressed_sorted:
        print(f"\n{'Transition':<25} {'Observed':>8} {'Expected':>8} {'Ratio':>8}")
        print("-" * 55)
        for (t1, t2), data in suppressed_sorted[:30]:
            trans = f"{t1} -> {t2}"
            print(f"{trans:<25} {data['observed']:>8} {data['expected']:>8.1f} {data['ratio']:>8.3f}x")

def analyze_prefix_transitions(tokens_by_folio, enrichment):
    """Analyze enrichment at prefix level."""
    print("\n" + "-"*70)
    print("PREFIX-LEVEL TRANSITION ENRICHMENT")
    print("-"*70)

    PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ol', 'al', 'sa', 'ct']

    def get_prefix(token):
        for p in sorted(PREFIXES, key=len, reverse=True):
            if token.startswith(p):
                return p
        return 'OTHER'

    # Build prefix transition matrix
    prefix_bigrams = Counter()
    prefix_unigrams = Counter()
    total = 0

    for folio, tokens in tokens_by_folio.items():
        for i, token in enumerate(tokens):
            p = get_prefix(token)
            prefix_unigrams[p] += 1
            if i > 0:
                prev_p = get_prefix(tokens[i-1])
                prefix_bigrams[(prev_p, p)] += 1
                total += 1

    # Compute prefix enrichment
    print(f"\n{'From':<8} {'To':<8} {'Observed':>8} {'Expected':>8} {'Ratio':>8}")
    print("-" * 50)

    prefix_enrichment = {}
    for p1 in PREFIXES + ['OTHER']:
        for p2 in PREFIXES + ['OTHER']:
            obs = prefix_bigrams.get((p1, p2), 0)
            exp = (prefix_unigrams[p1] / sum(prefix_unigrams.values())) * \
                  (prefix_unigrams[p2] / sum(prefix_unigrams.values())) * total
            if exp > 0:
                ratio = obs / exp
                prefix_enrichment[(p1, p2)] = ratio
                if (obs >= 100 or ratio > 2 or ratio < 0.5) and p1 != 'OTHER' and p2 != 'OTHER':
                    print(f"{p1:<8} {p2:<8} {obs:>8} {exp:>8.1f} {ratio:>8.2f}x")

    # Build and display matrix
    print("\n" + "-"*70)
    print("PREFIX TRANSITION MATRIX (enrichment ratios)")
    print("-"*70)

    headers = PREFIXES[:8]  # Top 8 prefixes
    print(f"\n{'':>8}", end="")
    for h in headers:
        print(f"{h:>8}", end="")
    print()

    for p1 in headers:
        print(f"{p1:>8}", end="")
        for p2 in headers:
            ratio = prefix_enrichment.get((p1, p2), 0)
            if ratio >= 2:
                marker = "+"
            elif ratio <= 0.5:
                marker = "-"
            else:
                marker = " "
            print(f"{ratio:>7.2f}{marker}", end="")
        print()

    return prefix_enrichment

def summarize_findings(sorted_enriched, prefix_enrichment):
    """Summarize key findings."""
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    # Count highly enriched
    n_highly_enriched = sum(1 for _, v in sorted_enriched if v['ratio'] >= 10)
    n_moderately_enriched = sum(1 for _, v in sorted_enriched if 5 <= v['ratio'] < 10)

    print(f"\nHighly enriched (>=10x): {n_highly_enriched}")
    print(f"Moderately enriched (5-10x): {n_moderately_enriched}")

    # Prefix patterns
    print("\nPrefix-level patterns:")
    enriched_pairs = [(k, v) for k, v in prefix_enrichment.items() if v >= 2.0 and k[0] != 'OTHER' and k[1] != 'OTHER']
    avoided_pairs = [(k, v) for k, v in prefix_enrichment.items() if v <= 0.5 and k[0] != 'OTHER' and k[1] != 'OTHER']

    print(f"  Enriched prefix pairs (>=2x): {len(enriched_pairs)}")
    for (p1, p2), r in sorted(enriched_pairs, key=lambda x: -x[1])[:10]:
        print(f"    {p1} -> {p2}: {r:.2f}x")

    print(f"\n  Avoided prefix pairs (<=0.5x): {len(avoided_pairs)}")
    for (p1, p2), r in sorted(avoided_pairs, key=lambda x: x[1])[:10]:
        print(f"    {p1} -> {p2}: {r:.3f}x")

def main():
    tokens_by_folio = load_b_tokens()
    enrichment, bigram_counts, unigram_counts, total_bigrams = compute_enrichment(tokens_by_folio)
    sorted_enriched = analyze_enrichment(enrichment, bigram_counts, unigram_counts, total_bigrams)
    analyze_suppression(enrichment)
    prefix_enrichment = analyze_prefix_transitions(tokens_by_folio, enrichment)
    summarize_findings(sorted_enriched, prefix_enrichment)

    print("\n" + "="*70)
    print("INTERPRETATION PENDING")
    print("="*70)

if __name__ == '__main__':
    main()
