"""
02_vocabulary_distribution.py - How folio unique vocabulary distributes to paragraphs

Key question: Concentrated in Par 1 (template) or spread (parallel)?
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

def gini_coefficient(values):
    """Compute Gini coefficient (0 = equal distribution, 1 = concentrated)."""
    if not values or sum(values) == 0:
        return 0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    cumsum = 0
    total = sum(sorted_vals)
    for i, v in enumerate(sorted_vals):
        cumsum += v
    # Gini formula
    numer = sum((2 * (i + 1) - n - 1) * v for i, v in enumerate(sorted_vals))
    return numer / (n * total) if total > 0 else 0

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load census
    with open(results_dir / 'folio_paragraph_census.json') as f:
        census = json.load(f)

    # Load paragraph tokens
    par_results = Path(__file__).resolve().parents[2] / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Build per-paragraph vocabulary
    par_vocab = {}
    for folio_entry in census['folios']:
        for par_info in folio_entry['paragraphs']:
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])
            vocab = set()
            for t in tokens:
                word = t['word']
                if word and '*' not in word:
                    vocab.add(word)
            par_vocab[par_id] = vocab

    print("=== VOCABULARY DISTRIBUTION ACROSS PARAGRAPHS ===\n")

    # Per-folio analysis
    par1_unique_rates = []
    gini_coefficients = []
    cumulative_by_ordinal = defaultdict(list)  # ordinal -> list of cumulative rates

    folio_details = []

    for folio_entry in census['folios']:
        pars = folio_entry['paragraphs']
        if len(pars) < 2:
            continue

        # Compute folio vocabulary (all unique words in folio)
        folio_vocab = set()
        for par_info in pars:
            folio_vocab |= par_vocab[par_info['par_id']]

        if not folio_vocab:
            continue

        # Per-paragraph contribution to folio unique vocab
        # A word is "folio-unique" if it appears in only one paragraph within folio
        word_to_pars = defaultdict(set)
        for par_info in pars:
            pid = par_info['par_id']
            for word in par_vocab[pid]:
                word_to_pars[word].add(pid)

        # Words unique to exactly one paragraph
        folio_unique_words = {w for w, p in word_to_pars.items() if len(p) == 1}

        # How much folio-unique vocab does each paragraph contain?
        par_unique_counts = []
        for i, par_info in enumerate(pars):
            pid = par_info['par_id']
            unique_in_par = len(par_vocab[pid] & folio_unique_words)
            par_unique_counts.append(unique_in_par)

        if sum(par_unique_counts) > 0:
            # Fraction of folio-unique vocab in paragraph 1
            par1_rate = par_unique_counts[0] / sum(par_unique_counts)
            par1_unique_rates.append(par1_rate)

            # Gini coefficient of distribution
            gini = gini_coefficient(par_unique_counts)
            gini_coefficients.append(gini)

            # Cumulative unique vocab by ordinal
            cumulative = 0
            for i, count in enumerate(par_unique_counts):
                cumulative += count
                rate = cumulative / sum(par_unique_counts)
                ordinal = min(i + 1, 8)  # Cap at 8
                cumulative_by_ordinal[ordinal].append(rate)

            folio_details.append({
                'folio': folio_entry['folio'],
                'par1_unique_rate': par1_rate,
                'gini': gini,
                'unique_counts': par_unique_counts
            })

    print(f"Folios analyzed: {len(par1_unique_rates)}")
    print(f"\n--- PARAGRAPH 1 CONCENTRATION ---")
    print(f"Mean unique vocab in Par 1: {statistics.mean(par1_unique_rates):.1%}")
    print(f"Median: {statistics.median(par1_unique_rates):.1%}")

    print(f"\n--- GINI COEFFICIENT (concentration) ---")
    print(f"Mean Gini: {statistics.mean(gini_coefficients):.3f}")
    print(f"(0 = equal distribution, 1 = all in one paragraph)")

    # Interpretation
    mean_gini = statistics.mean(gini_coefficients)
    if mean_gini < 0.3:
        print("--> DISTRIBUTED: folio-unique vocab spread across paragraphs")
    elif mean_gini > 0.5:
        print("--> CONCENTRATED: folio-unique vocab in few paragraphs")
    else:
        print("--> MODERATE: some concentration, some spread")

    print(f"\n--- CUMULATIVE UNIQUE VOCAB BY ORDINAL ---")
    for ordinal in sorted(cumulative_by_ordinal.keys()):
        rates = cumulative_by_ordinal[ordinal]
        if rates:
            print(f"  By Par {ordinal}: {statistics.mean(rates):.1%} of folio-unique vocab")

    # Template vs Parallel verdict
    print(f"\n--- DISTRIBUTION VERDICT ---")
    par1_mean = statistics.mean(par1_unique_rates)
    if par1_mean > 0.5:
        print(f"Par 1 has {par1_mean:.1%} of unique vocab --> TEMPLATE MODEL")
    elif par1_mean < 0.25:
        print(f"Par 1 has only {par1_mean:.1%} of unique vocab --> PARALLEL MODEL")
    else:
        print(f"Par 1 has {par1_mean:.1%} of unique vocab --> MIXED MODEL")

    # Save results
    output = {
        'par1_unique_rate_mean': statistics.mean(par1_unique_rates),
        'par1_unique_rate_median': statistics.median(par1_unique_rates),
        'gini_mean': statistics.mean(gini_coefficients),
        'gini_stdev': statistics.stdev(gini_coefficients) if len(gini_coefficients) > 1 else 0,
        'cumulative_by_ordinal': {k: statistics.mean(v) for k, v in cumulative_by_ordinal.items()},
        'verdict': 'DISTRIBUTED' if mean_gini < 0.3 else ('CONCENTRATED' if mean_gini > 0.5 else 'MODERATE'),
        'folio_details': folio_details
    }

    with open(results_dir / 'vocabulary_distribution.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to vocabulary_distribution.json")

if __name__ == '__main__':
    main()
