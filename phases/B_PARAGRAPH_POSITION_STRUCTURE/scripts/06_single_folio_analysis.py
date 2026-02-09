"""
06_single_folio_analysis.py - Within-folio paragraph structure analysis

Check if paragraph position effects exist WITHIN individual folios
that might be masked by cross-folio aggregation.

Focus on annotated folios: f103r, f104r, f105r, f41v, f43r
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

FL_CATEGORIES = {
    'ar': 'INITIAL', 'r': 'INITIAL', 'or': 'INITIAL',
    'al': 'LATE', 'l': 'LATE', 'ol': 'LATE', 'aiin': 'LATE',
    'aly': 'TERMINAL', 'am': 'TERMINAL', 'y': 'TERMINAL', 'dy': 'TERMINAL',
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

def analyze_single_folio(folio, folio_data, morph):
    """Comprehensive analysis of a single folio's paragraph structure."""
    paragraphs = detect_paragraphs(folio_data)
    n_paras = len(paragraphs)

    if n_paras < 2:
        return None

    result = {
        'folio': folio,
        'n_paragraphs': n_paras,
        'paragraphs': [],
        'fl_by_position': {},
        'vocabulary_progression': {}
    }

    # Analyze each paragraph
    para_vocabs = {}
    for para_num in sorted(paragraphs.keys()):
        tokens = paragraphs[para_num]
        n_tokens = len(tokens)

        # Position classification
        rel_pos = (para_num - 1) / (n_paras - 1) if n_paras > 1 else 0
        position = 'early' if rel_pos < 0.33 else ('late' if rel_pos > 0.67 else 'middle')

        # Morphological analysis
        middles = set()
        prefixes = Counter()
        suffixes = Counter()
        fl_counts = Counter()

        for word in tokens:
            m = morph.extract(word)
            if m:
                if m.middle:
                    middles.add(m.middle)
                if m.prefix:
                    prefixes[m.prefix] += 1
                if m.suffix:
                    suffixes[m.suffix] += 1
                    fl_type = FL_CATEGORIES.get(m.suffix)
                    if fl_type:
                        fl_counts[fl_type] += 1

        para_vocabs[para_num] = middles

        # Compute rates
        gallows_rate = sum(1 for w in tokens if has_gallows_initial(w)) / n_tokens if n_tokens > 0 else 0

        result['paragraphs'].append({
            'number': para_num,
            'position': position,
            'tokens': n_tokens,
            'unique_middles': len(middles),
            'gallows_rate': gallows_rate,
            'top_prefixes': prefixes.most_common(3),
            'top_suffixes': suffixes.most_common(3),
            'fl_initial': fl_counts.get('INITIAL', 0),
            'fl_late': fl_counts.get('LATE', 0),
            'fl_terminal': fl_counts.get('TERMINAL', 0),
            'fl_initial_rate': fl_counts.get('INITIAL', 0) / n_tokens if n_tokens > 0 else 0,
            'fl_late_rate': fl_counts.get('LATE', 0) / n_tokens if n_tokens > 0 else 0,
            'fl_terminal_rate': fl_counts.get('TERMINAL', 0) / n_tokens if n_tokens > 0 else 0,
        })

    # Vocabulary survival from P1
    p1_vocab = para_vocabs.get(1, set())
    for para_num in sorted(paragraphs.keys()):
        if para_num > 1 and p1_vocab:
            survival = len(p1_vocab & para_vocabs[para_num]) / len(p1_vocab)
            result['vocabulary_progression'][f'P1_to_P{para_num}'] = survival

    # FL progression summary
    fl_by_pos = {'early': Counter(), 'middle': Counter(), 'late': Counter()}
    tok_by_pos = {'early': 0, 'middle': 0, 'late': 0}

    for p in result['paragraphs']:
        pos = p['position']
        fl_by_pos[pos]['INITIAL'] += p['fl_initial']
        fl_by_pos[pos]['LATE'] += p['fl_late']
        fl_by_pos[pos]['TERMINAL'] += p['fl_terminal']
        tok_by_pos[pos] += p['tokens']

    for pos in ['early', 'middle', 'late']:
        n = tok_by_pos[pos]
        if n > 0:
            result['fl_by_position'][pos] = {
                'INITIAL': fl_by_pos[pos]['INITIAL'] / n,
                'LATE': fl_by_pos[pos]['LATE'] / n,
                'TERMINAL': fl_by_pos[pos]['TERMINAL'] / n,
                'n_tokens': n
            }

    return result

def main():
    folio_data = load_raw_data()
    morph = Morphology()

    target_folios = ['f103r', 'f104r', 'f105r', 'f41v', 'f43r', 'f46r', 'f46v']

    print("=" * 80)
    print("SINGLE-FOLIO PARAGRAPH STRUCTURE ANALYSIS")
    print("=" * 80)

    all_results = []

    for folio in target_folios:
        if folio not in folio_data:
            print(f"\n{folio}: NOT FOUND")
            continue

        result = analyze_single_folio(folio, folio_data[folio], morph)
        if result is None:
            print(f"\n{folio}: < 2 paragraphs, skipping")
            continue

        all_results.append(result)

        print(f"\n{'='*80}")
        print(f"FOLIO: {folio} ({result['n_paragraphs']} paragraphs)")
        print("=" * 80)

        # Paragraph details
        print(f"\n--- Paragraph Structure ---")
        print(f"{'#':<3} {'Pos':<7} {'Tok':<5} {'Mid':<5} {'Gall%':<6} {'FL_I':<5} {'FL_L':<5} {'FL_T':<5}")
        print("-" * 50)

        for p in result['paragraphs']:
            print(f"P{p['number']:<2} {p['position']:<7} {p['tokens']:<5} {p['unique_middles']:<5} "
                  f"{p['gallows_rate']:.0%}   {p['fl_initial']:<5} {p['fl_late']:<5} {p['fl_terminal']:<5}")

        # FL rates by position
        print(f"\n--- FL Rates by Position ---")
        for pos in ['early', 'middle', 'late']:
            if pos in result['fl_by_position']:
                fl = result['fl_by_position'][pos]
                print(f"  {pos}: INITIAL={fl['INITIAL']:.1%}, LATE={fl['LATE']:.1%}, TERMINAL={fl['TERMINAL']:.1%} (n={fl['n_tokens']})")

        # Vocabulary survival
        if result['vocabulary_progression']:
            print(f"\n--- Vocabulary Survival from P1 ---")
            for key, val in result['vocabulary_progression'].items():
                print(f"  {key}: {val:.1%}")

        # Check for TERMINAL FL gradient
        paras = result['paragraphs']
        terminal_rates = [p['fl_terminal_rate'] for p in paras]
        if len(terminal_rates) >= 3:
            # Spearman correlation with position
            positions = list(range(len(terminal_rates)))
            rho, p_val = stats.spearmanr(positions, terminal_rates)
            trend = "INCREASING" if rho > 0.3 else ("DECREASING" if rho < -0.3 else "FLAT")
            print(f"\n--- TERMINAL FL Trend ---")
            print(f"  Spearman rho = {rho:.2f} (p={p_val:.3f})")
            print(f"  Trend: {trend}")
            print(f"  Values: {' -> '.join(f'{r:.1%}' for r in terminal_rates)}")

    # Cross-folio summary
    print("\n" + "=" * 80)
    print("CROSS-FOLIO SUMMARY")
    print("=" * 80)

    # Check if any folios show TERMINAL FL increase
    increasing_terminal = 0
    decreasing_terminal = 0
    flat_terminal = 0

    for result in all_results:
        paras = result['paragraphs']
        terminal_rates = [p['fl_terminal_rate'] for p in paras]
        if len(terminal_rates) >= 3:
            rho, _ = stats.spearmanr(range(len(terminal_rates)), terminal_rates)
            if rho > 0.3:
                increasing_terminal += 1
            elif rho < -0.3:
                decreasing_terminal += 1
            else:
                flat_terminal += 1

    print(f"\nTERMINAL FL trend across folios:")
    print(f"  Increasing (late > early): {increasing_terminal}")
    print(f"  Decreasing (early > late): {decreasing_terminal}")
    print(f"  Flat (no trend): {flat_terminal}")

    # Save results
    output_path = Path('C:/git/voynich/phases/B_PARAGRAPH_POSITION_STRUCTURE/results/06_single_folio_analysis.json')

    # Clean for JSON
    clean_results = []
    for r in all_results:
        clean = {
            'folio': r['folio'],
            'n_paragraphs': r['n_paragraphs'],
            'paragraphs': [
                {k: (v if not isinstance(v, (list, tuple)) or not v or not isinstance(v[0], tuple)
                     else [(x[0], int(x[1])) for x in v])
                 for k, v in p.items()}
                for p in r['paragraphs']
            ],
            'fl_by_position': r['fl_by_position'],
            'vocabulary_progression': r['vocabulary_progression']
        }
        clean_results.append(clean)

    with open(output_path, 'w') as f:
        json.dump({'folios': clean_results}, f, indent=2)

    print(f"\nResults saved to: {output_path}")

if __name__ == '__main__':
    main()
