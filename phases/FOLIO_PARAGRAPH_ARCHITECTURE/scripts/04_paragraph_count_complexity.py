"""
04_paragraph_count_complexity.py - Does paragraph count reflect folio complexity?

Tests correlations between paragraph count and vocabulary, role diversity, etc.
"""

import json
import sys
from pathlib import Path
from collections import Counter
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

def spearman_rho(x, y):
    """Simple Spearman rank correlation."""
    n = len(x)
    if n < 3:
        return 0

    # Rank the values
    def rank(vals):
        sorted_idx = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0] * len(vals)
        for r, i in enumerate(sorted_idx):
            ranks[i] = r + 1
        return ranks

    rx = rank(x)
    ry = rank(y)

    # Spearman formula
    d_squared = sum((rx[i] - ry[i])**2 for i in range(n))
    rho = 1 - (6 * d_squared) / (n * (n**2 - 1))
    return rho

def role_entropy(role_counts):
    """Shannon entropy of role distribution."""
    total = sum(role_counts.values())
    if total == 0:
        return 0
    entropy = 0
    for count in role_counts.values():
        if count > 0:
            p = count / total
            entropy -= p * (p and (p > 0) and statistics.log(p, 2) if hasattr(statistics, 'log') else 0)
    # Simplified: use standard deviation proxy for diversity
    return statistics.stdev(list(role_counts.values())) if len(role_counts) > 1 else 0

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load census
    with open(results_dir / 'folio_paragraph_census.json') as f:
        census = json.load(f)

    # Load paragraph tokens
    par_results = Path(__file__).resolve().parents[2] / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Load class map
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    print("=== PARAGRAPH COUNT vs COMPLEXITY ===\n")

    # Collect folio-level metrics
    par_counts = []
    vocab_sizes = []
    token_counts = []
    role_diversities = []
    sections = []

    for folio_entry in census['folios']:
        par_count = folio_entry['paragraph_count']
        unique_words = folio_entry['unique_words']
        total_tokens = folio_entry['total_tokens']
        section = folio_entry['section']

        # Role diversity: count classes used
        folio_classes = set()
        for par_info in folio_entry['paragraphs']:
            tokens = tokens_by_par.get(par_info['par_id'], [])
            for t in tokens:
                word = t['word']
                if word and '*' not in word and word in class_map:
                    folio_classes.add(class_map[word])

        par_counts.append(par_count)
        vocab_sizes.append(unique_words)
        token_counts.append(total_tokens)
        role_diversities.append(len(folio_classes))
        sections.append(section)

    # Correlations
    print("--- SPEARMAN CORRELATIONS ---")
    rho_vocab = spearman_rho(par_counts, vocab_sizes)
    print(f"Paragraph count vs vocabulary size: rho = {rho_vocab:.3f}")

    rho_tokens = spearman_rho(par_counts, token_counts)
    print(f"Paragraph count vs total tokens: rho = {rho_tokens:.3f}")

    rho_diversity = spearman_rho(par_counts, role_diversities)
    print(f"Paragraph count vs role diversity: rho = {rho_diversity:.3f}")

    # Interpretation
    print(f"\n--- INTERPRETATION ---")
    if rho_vocab > 0.5:
        print("Strong positive: more paragraphs = richer vocabulary")
    elif rho_vocab > 0.3:
        print("Moderate positive: some vocabulary growth with paragraphs")
    elif rho_vocab > 0:
        print("Weak positive: slight vocabulary growth with paragraphs")
    else:
        print("No/negative: paragraph count doesn't predict vocabulary")

    # By section
    print(f"\n--- PARAGRAPH COUNT BY SECTION ---")
    section_counts = {}
    for s, c in zip(sections, par_counts):
        if s not in section_counts:
            section_counts[s] = []
        section_counts[s].append(c)

    for section in sorted(section_counts.keys()):
        counts = section_counts[section]
        print(f"  {section}: mean {statistics.mean(counts):.1f}, stdev {statistics.stdev(counts):.1f}" if len(counts) > 1 else f"  {section}: mean {statistics.mean(counts):.1f}")

    # ANOVA proxy: section effect
    overall_mean = statistics.mean(par_counts)
    between_var = sum(len(section_counts[s]) * (statistics.mean(section_counts[s]) - overall_mean)**2
                     for s in section_counts) / (len(section_counts) - 1) if len(section_counts) > 1 else 0
    within_var = sum(sum((c - statistics.mean(section_counts[s]))**2 for c in section_counts[s])
                    for s in section_counts if len(section_counts[s]) > 1)
    within_var /= (len(par_counts) - len(section_counts)) if len(par_counts) > len(section_counts) else 1

    f_ratio = between_var / within_var if within_var > 0 else 0
    print(f"\nSection effect F-ratio: {f_ratio:.2f}")
    if f_ratio > 3:
        print("--> SECTIONS DIFFER significantly in paragraph count")
    else:
        print("--> Sections have SIMILAR paragraph counts")

    # Verdict
    print(f"\n--- COMPLEXITY VERDICT ---")
    if rho_vocab > 0.5 and rho_diversity > 0.3:
        print("Paragraph count REFLECTS complexity (vocabulary + diversity)")
        verdict = "COMPLEXITY_PROXY"
    elif rho_tokens > 0.7:
        print("Paragraph count reflects LENGTH, not complexity")
        verdict = "LENGTH_PROXY"
    else:
        print("Paragraph count is INDEPENDENT of complexity")
        verdict = "INDEPENDENT"

    # Save results
    output = {
        'correlations': {
            'par_count_vs_vocab': rho_vocab,
            'par_count_vs_tokens': rho_tokens,
            'par_count_vs_diversity': rho_diversity
        },
        'section_means': {s: statistics.mean(c) for s, c in section_counts.items()},
        'section_f_ratio': f_ratio,
        'verdict': verdict
    }

    with open(results_dir / 'complexity_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to complexity_analysis.json")

if __name__ == '__main__':
    main()
