"""
04_line_coupling_by_position.py - Line-to-line coupling by paragraph position

Phase: B_PARAGRAPH_POSITION_STRUCTURE
Test D: Do early paragraphs show different line-to-line coupling than late paragraphs?

Question: Does vocabulary coupling vary by paragraph position?

Method:
1. Segment all lines by paragraph-position stratum (early, middle, late)
2. Within each stratum, measure adjacent-line vocabulary overlap (Jaccard)
3. Compare to within-stratum permuted baseline

Tests the hypothesis: Material-prep paragraphs (early) might show sequential coupling,
thermal-operation paragraphs (middle) might show independent assessments
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology
import json
import csv
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

GALLOWS = {'k', 't', 'p', 'f'}

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

def detect_paragraphs_with_lines(folio_data):
    """Return paragraphs with their lines preserved."""
    paragraphs = defaultdict(list)  # para_num -> list of (line_num, tokens)
    lines = sorted(folio_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))

    current_para = 1
    for i, line in enumerate(lines):
        tokens = folio_data[line]
        if not tokens:
            continue

        first_word = tokens[0]
        if i > 0 and has_gallows_initial(first_word):
            current_para += 1

        paragraphs[current_para].append((line, tokens))

    return paragraphs

def extract_middles(tokens, morph):
    """Extract MIDDLEs from token list."""
    middles = set()
    for token in tokens:
        m = morph.extract(token)
        if m and m.middle:
            middles.add(m.middle)
    return middles

def jaccard(set1, set2):
    if not set1 and not set2:
        return 0.0
    union = set1 | set2
    if not union:
        return 0.0
    return len(set1 & set2) / len(union)

def main():
    folio_data = load_raw_data()
    morph = Morphology()

    # Collect lines with position metadata
    all_lines = []  # list of (folio, line_num, tokens, position_bin, para_num)

    for folio in sorted(folio_data.keys()):
        paragraphs = detect_paragraphs_with_lines(folio_data[folio])
        n_paras = len(paragraphs)
        if n_paras < 2:
            continue

        for para_num in sorted(paragraphs.keys()):
            rel_pos = (para_num - 1) / (n_paras - 1) if n_paras > 1 else 0
            position_bin = 'early' if rel_pos < 0.33 else ('late' if rel_pos > 0.67 else 'middle')

            for line_num, tokens in paragraphs[para_num]:
                all_lines.append({
                    'folio': folio,
                    'line': line_num,
                    'tokens': tokens,
                    'middles': extract_middles(tokens, morph),
                    'position_bin': position_bin,
                    'para_num': para_num
                })

    print("=" * 70)
    print("TEST D: LINE-TO-LINE COUPLING BY PARAGRAPH POSITION")
    print("=" * 70)
    print(f"\nTotal lines analyzed: {len(all_lines)}")

    # Group by folio and paragraph for adjacent-line analysis
    folio_para_lines = defaultdict(list)
    for line_info in all_lines:
        key = (line_info['folio'], line_info['para_num'])
        folio_para_lines[key].append(line_info)

    # Compute adjacent-line Jaccard within each paragraph
    coupling_by_position = defaultdict(list)

    for (folio, para_num), lines in folio_para_lines.items():
        if len(lines) < 2:
            continue

        # Sort by line number
        lines = sorted(lines, key=lambda x: int(x['line']) if x['line'].isdigit() else 0)
        position_bin = lines[0]['position_bin']

        # Compute adjacent Jaccard
        for i in range(len(lines) - 1):
            j = jaccard(lines[i]['middles'], lines[i+1]['middles'])
            coupling_by_position[position_bin].append(j)

    # Summary
    print(f"\n--- Adjacent-Line Coupling by Position ---")
    for pos in ['early', 'middle', 'late']:
        vals = coupling_by_position[pos]
        if vals:
            print(f"{pos}: mean={np.mean(vals):.3f}, sd={np.std(vals):.3f}, n={len(vals)}")

    # Statistical comparison
    print(f"\n--- Statistical Tests ---")

    # ANOVA
    groups = [coupling_by_position['early'], coupling_by_position['middle'], coupling_by_position['late']]
    f_stat, p_val = stats.f_oneway(*[g for g in groups if len(g) > 0])
    print(f"ANOVA: F={f_stat:.3f}, p={p_val:.4f}")

    # Pairwise t-tests
    for pos1, pos2 in [('early', 'middle'), ('middle', 'late'), ('early', 'late')]:
        if coupling_by_position[pos1] and coupling_by_position[pos2]:
            t, p = stats.ttest_ind(coupling_by_position[pos1], coupling_by_position[pos2])
            print(f"  {pos1} vs {pos2}: t={t:.2f}, p={p:.4f}")

    # Effect sizes
    print(f"\n--- Effect Sizes ---")
    early_mean = np.mean(coupling_by_position['early']) if coupling_by_position['early'] else 0
    middle_mean = np.mean(coupling_by_position['middle']) if coupling_by_position['middle'] else 0
    late_mean = np.mean(coupling_by_position['late']) if coupling_by_position['late'] else 0

    # Pooled SD
    all_vals = coupling_by_position['early'] + coupling_by_position['middle'] + coupling_by_position['late']
    pooled_sd = np.std(all_vals) if all_vals else 1

    if pooled_sd > 0:
        d_early_late = (early_mean - late_mean) / pooled_sd
        d_early_middle = (early_mean - middle_mean) / pooled_sd
        print(f"Cohen's d (early vs late): {d_early_late:.3f}")
        print(f"Cohen's d (early vs middle): {d_early_middle:.3f}")
    else:
        d_early_late = 0
        d_early_middle = 0

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if p_val < 0.05 and abs(d_early_late) > 0.2:
        if early_mean > late_mean:
            print(f"\nEARLY PARAGRAPHS SHOW STRONGER LINE COUPLING:")
            print("  Adjacent lines in early paragraphs share more vocabulary.")
            print("  Consistent with sequential material-prep hypothesis.")
        else:
            print(f"\nLATE PARAGRAPHS SHOW STRONGER LINE COUPLING:")
            print("  Adjacent lines in late paragraphs share more vocabulary.")
            print("  Suggests sequential completion phase.")
    else:
        print(f"\nNO SIGNIFICANT COUPLING VARIATION BY POSITION:")
        print("  Line-to-line coupling is similar across paragraph positions.")
        print("  Consistent with C670 (folio-mediated, not state-transfer).")

    # Save results
    results = {
        'summary': {
            'total_lines': len(all_lines),
            'anova_f': float(f_stat),
            'anova_p': float(p_val),
            'effect_size_early_late': float(d_early_late)
        },
        'coupling_by_position': {
            pos: {
                'mean': float(np.mean(vals)) if vals else 0,
                'std': float(np.std(vals)) if vals else 0,
                'n': len(vals)
            }
            for pos, vals in coupling_by_position.items()
        }
    }

    output_path = Path('C:/git/voynich/phases/B_PARAGRAPH_POSITION_STRUCTURE/results/04_line_coupling_by_position.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results

if __name__ == '__main__':
    main()
