"""
05_fl_progression.py - FL type progression by paragraph position

Phase: B_PARAGRAPH_POSITION_STRUCTURE
Test E: Does FL type (INITIAL/LATE/TERMINAL) correlate with paragraph ordinal?

Question: Does FL state vocabulary track material progression across paragraphs?

Method:
1. Classify FL tokens by C777 categories: INITIAL (ar, r), LATE (al, l, ol), TERMINAL (aly, am, y)
2. Compute FL type distribution per paragraph position bin
3. Test for ordinal gradient (chi-square or trend)

Null model: Permute paragraphs within folios

Expected from annotation: TERMINAL FL should concentrate in late paragraphs
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology
import json
import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats

GALLOWS = {'k', 't', 'p', 'f'}

# FL categories from C777 - using suffix classification
FL_CATEGORIES = {
    # INITIAL - beginning of process
    'ar': 'INITIAL',
    'r': 'INITIAL',
    'or': 'INITIAL',
    # LATE - process ongoing
    'al': 'LATE',
    'l': 'LATE',
    'ol': 'LATE',
    'aiin': 'LATE',
    # TERMINAL - process complete
    'aly': 'TERMINAL',
    'am': 'TERMINAL',
    'y': 'TERMINAL',
    'dy': 'TERMINAL',
}

def has_gallows_initial(word):
    if not word or not word.strip():
        return False
    return word[0] in GALLOWS

def load_raw_data():
    data_path = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
    folio_lines = defaultdict(lambda: defaultdict(list))

    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row['transcriber'] == 'H' and row['language'] == 'B':
                folio = row['folio']
                line = row['line_number']
                word = row['word']
                if '*' in word:
                    continue
                folio_lines[folio][line].append(word)

    return folio_lines

def detect_paragraphs(folio_data):
    paragraphs = defaultdict(list)
    lines = sorted(folio_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))

    current_para = 1
    for i, line in enumerate(lines):
        tokens = folio_data[line]
        if not tokens:
            continue

        first_word = tokens[0]
        if i > 0 and has_gallows_initial(first_word):
            current_para += 1

        paragraphs[current_para].extend(tokens)

    return paragraphs

def classify_fl(suffix):
    """Classify FL type from suffix."""
    if not suffix:
        return None
    return FL_CATEGORIES.get(suffix, None)

def main():
    folio_data = load_raw_data()
    morph = Morphology()

    # Collect FL data by position
    fl_by_position = defaultdict(Counter)  # position_bin -> Counter of FL types
    token_counts_by_position = defaultdict(int)

    for folio in sorted(folio_data.keys()):
        paragraphs = detect_paragraphs(folio_data[folio])
        n_paras = len(paragraphs)
        if n_paras < 2:
            continue

        for para_num in sorted(paragraphs.keys()):
            rel_pos = (para_num - 1) / (n_paras - 1) if n_paras > 1 else 0
            position_bin = 'early' if rel_pos < 0.33 else ('late' if rel_pos > 0.67 else 'middle')

            tokens = paragraphs[para_num]
            token_counts_by_position[position_bin] += len(tokens)

            for word in tokens:
                m = morph.extract(word)
                if m and m.suffix:
                    fl_type = classify_fl(m.suffix)
                    if fl_type:
                        fl_by_position[position_bin][fl_type] += 1

    print("=" * 70)
    print("TEST E: FL TYPE PROGRESSION BY PARAGRAPH POSITION")
    print("=" * 70)

    # Compute rates
    print(f"\n--- FL Type Distribution by Position ---")
    print(f"{'Position':<10} {'INITIAL':<12} {'LATE':<12} {'TERMINAL':<12} {'Total FL':<10} {'Tokens':<10}")
    print("-" * 70)

    fl_rates = {}
    for pos in ['early', 'middle', 'late']:
        counts = fl_by_position[pos]
        total_fl = sum(counts.values())
        total_tok = token_counts_by_position[pos]

        fl_rates[pos] = {
            'INITIAL': counts['INITIAL'] / total_tok if total_tok > 0 else 0,
            'LATE': counts['LATE'] / total_tok if total_tok > 0 else 0,
            'TERMINAL': counts['TERMINAL'] / total_tok if total_tok > 0 else 0,
        }

        print(f"{pos:<10} {counts['INITIAL']:<5} ({fl_rates[pos]['INITIAL']:.1%})   "
              f"{counts['LATE']:<5} ({fl_rates[pos]['LATE']:.1%})   "
              f"{counts['TERMINAL']:<5} ({fl_rates[pos]['TERMINAL']:.1%})   "
              f"{total_fl:<10} {total_tok:<10}")

    # Chi-square test
    print(f"\n--- Statistical Tests ---")

    # Build contingency table
    contingency = []
    for pos in ['early', 'middle', 'late']:
        counts = fl_by_position[pos]
        contingency.append([counts['INITIAL'], counts['LATE'], counts['TERMINAL']])

    contingency = np.array(contingency)
    chi2, p_val, dof, expected = stats.chi2_contingency(contingency)

    print(f"\nChi-square test:")
    print(f"  chi2 = {chi2:.3f}")
    print(f"  p-value = {p_val:.4f}")
    print(f"  dof = {dof}")

    # Test for specific trends
    print(f"\n--- Trend Analysis ---")

    # Does TERMINAL FL increase from early to late?
    terminal_rates = [fl_rates['early']['TERMINAL'],
                      fl_rates['middle']['TERMINAL'],
                      fl_rates['late']['TERMINAL']]
    spearman_terminal = stats.spearmanr([0, 1, 2], terminal_rates)
    print(f"TERMINAL FL trend: {terminal_rates[0]:.1%} -> {terminal_rates[1]:.1%} -> {terminal_rates[2]:.1%}")
    print(f"  Spearman rho = {spearman_terminal.correlation:.3f}, p = {spearman_terminal.pvalue:.4f}")

    # Does INITIAL FL decrease from early to late?
    initial_rates = [fl_rates['early']['INITIAL'],
                     fl_rates['middle']['INITIAL'],
                     fl_rates['late']['INITIAL']]
    spearman_initial = stats.spearmanr([0, 1, 2], initial_rates)
    print(f"INITIAL FL trend: {initial_rates[0]:.1%} -> {initial_rates[1]:.1%} -> {initial_rates[2]:.1%}")
    print(f"  Spearman rho = {spearman_initial.correlation:.3f}, p = {spearman_initial.pvalue:.4f}")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if p_val < 0.05:
        print(f"\nSIGNIFICANT FL POSITION EFFECT (p={p_val:.4f}):")
        if spearman_terminal.correlation > 0 and spearman_terminal.pvalue < 0.05:
            print("  TERMINAL FL increases with paragraph position.")
            print("  Supports material progression hypothesis.")
        elif spearman_initial.correlation < 0 and spearman_initial.pvalue < 0.05:
            print("  INITIAL FL decreases with paragraph position.")
            print("  Supports material progression hypothesis.")
        else:
            print("  FL distribution varies but no clear gradient.")
    else:
        print(f"\nNO SIGNIFICANT FL POSITION EFFECT (p={p_val:.4f}):")
        print("  FL type distribution independent of paragraph position.")
        print("  No evidence for FL tracking material progression.")

    # Save results
    results = {
        'summary': {
            'chi2': float(chi2),
            'p_value': float(p_val),
            'terminal_trend_rho': float(spearman_terminal.correlation),
            'terminal_trend_p': float(spearman_terminal.pvalue),
            'initial_trend_rho': float(spearman_initial.correlation),
            'initial_trend_p': float(spearman_initial.pvalue),
        },
        'fl_rates_by_position': fl_rates,
        'raw_counts': {
            pos: {k: int(v) for k, v in fl_by_position[pos].items()}
            for pos in ['early', 'middle', 'late']
        },
        'token_counts': {k: int(v) for k, v in token_counts_by_position.items()}
    }

    output_path = Path('C:/git/voynich/phases/B_PARAGRAPH_POSITION_STRUCTURE/results/05_fl_progression.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results

if __name__ == '__main__':
    main()
