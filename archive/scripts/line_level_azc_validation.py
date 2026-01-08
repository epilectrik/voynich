"""
Quick AZC Line-Level Validation

Checks if AZC shows the same line patterns as Currier B, or uses different logic.
Expected: AZC uses different line logic (diagram annotation, not control stages)
"""

import json
import csv
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from scipy import stats
import random

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

# LINK tokens
LINK_TOKENS = {'ol', 'al', 'or', 'ar', 'aiin', 'daiin', 'chol', 'chor', 'shol', 'shor'}

# B boundary markers (from LINE phase)
B_LINE_INITIAL = {'daiin', 'saiin', 'sain', 'dain'}
B_LINE_FINAL = {'am', 'oly', 'dy'}

def load_transcription():
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            data.append(row)
    return data

def get_azc_data(data):
    """Get AZC sections (not classified as A or B by Currier)."""
    # AZC sections are in sections A, Z, C (Astronomical, Zodiac, Cosmological)
    azc_sections = {'A', 'Z', 'C'}
    azc_data = []
    for row in data:
        if row.get('section') in azc_sections and row.get('transcriber') == 'H':
            azc_data.append(row)
    return azc_data

def get_currier_a_data(data):
    """Get Currier A data."""
    a_data = []
    for row in data:
        if row.get('language') == 'A' and row.get('transcriber') == 'H':
            a_data.append(row)
    return a_data

def reconstruct_lines(token_data):
    """Reconstruct line structure."""
    lines = defaultdict(list)
    for row in token_data:
        key = (row['folio'], row.get('line_number', '1'))
        lines[key].append(row)
    return dict(lines)

def analyze_line_regularity(lines, label):
    """Check line length regularity (CV test)."""
    folio_lines = defaultdict(list)
    for (folio, line_num), tokens in lines.items():
        folio_lines[folio].append(len(tokens))

    folio_cvs = {}
    for folio, lengths in folio_lines.items():
        if len(lengths) >= 3:
            mean_len = np.mean(lengths)
            std_len = np.std(lengths)
            cv = std_len / mean_len if mean_len > 0 else 0
            folio_cvs[folio] = cv

    if not folio_cvs:
        return None

    observed_cv = np.mean(list(folio_cvs.values()))

    # Quick null estimate
    all_lengths = []
    for lengths in folio_lines.values():
        all_lengths.extend(lengths)

    return {
        'label': label,
        'folios': len(folio_cvs),
        'observed_cv': observed_cv,
        'mean_line_length': np.mean(all_lengths),
        'std_line_length': np.std(all_lengths),
        'total_lines': len(lines)
    }

def analyze_boundary_markers(lines, label):
    """Check for B-style boundary markers."""
    line_initial = []
    line_final = []

    for key, tokens in lines.items():
        if len(tokens) >= 2:
            line_initial.append(tokens[0]['word'])
            line_final.append(tokens[-1]['word'])

    # Check B boundary markers
    b_initial_count = sum(1 for t in line_initial if t in B_LINE_INITIAL)
    b_final_count = sum(1 for t in line_final if t in B_LINE_FINAL)

    b_initial_rate = b_initial_count / len(line_initial) if line_initial else 0
    b_final_rate = b_final_count / len(line_final) if line_final else 0

    # Top tokens at boundaries
    initial_counter = Counter(line_initial)
    final_counter = Counter(line_final)

    return {
        'label': label,
        'total_lines': len(line_initial),
        'b_initial_markers': b_initial_count,
        'b_initial_rate': b_initial_rate,
        'b_final_markers': b_final_count,
        'b_final_rate': b_final_rate,
        'top_initial': initial_counter.most_common(5),
        'top_final': final_counter.most_common(5)
    }

def main():
    print("="*60)
    print("AZC & Currier A Line-Level Validation")
    print("="*60)
    print("\nQuestion: Do AZC/A show B-like line patterns?")
    print("Expected: NO - they use different line logic")

    data = load_transcription()

    # Get data for each category
    azc_data = get_azc_data(data)
    a_data = get_currier_a_data(data)

    print(f"\nData loaded:")
    print(f"  AZC tokens: {len(azc_data)}")
    print(f"  Currier A tokens: {len(a_data)}")

    # Reconstruct lines
    azc_lines = reconstruct_lines(azc_data)
    a_lines = reconstruct_lines(a_data)

    print(f"  AZC lines: {len(azc_lines)}")
    print(f"  Currier A lines: {len(a_lines)}")

    # Compare regularity
    print("\n" + "="*60)
    print("LINE LENGTH REGULARITY (CV)")
    print("="*60)
    print("\nReference: Currier B CV = 0.263 (3.3x more regular than random)")

    azc_reg = analyze_line_regularity(azc_lines, "AZC")
    a_reg = analyze_line_regularity(a_lines, "Currier A")

    for reg in [azc_reg, a_reg]:
        if reg:
            print(f"\n{reg['label']}:")
            print(f"  Folios: {reg['folios']}")
            print(f"  Lines: {reg['total_lines']}")
            print(f"  Mean line length: {reg['mean_line_length']:.1f}")
            print(f"  CV: {reg['observed_cv']:.3f}")

            if reg['observed_cv'] < 0.35:
                print(f"  -> SIMILAR to B (deliberate chunking)")
            elif reg['observed_cv'] > 0.6:
                print(f"  -> DIFFERENT from B (less regular)")
            else:
                print(f"  -> INTERMEDIATE")

    # Compare boundary markers
    print("\n" + "="*60)
    print("B-STYLE BOUNDARY MARKERS")
    print("="*60)
    print("\nB markers: initial={daiin,saiin,sain,dain}, final={am,oly,dy}")
    print("Reference: B uses these at 8-10% rate with high enrichment")

    azc_bound = analyze_boundary_markers(azc_lines, "AZC")
    a_bound = analyze_boundary_markers(a_lines, "Currier A")

    for bound in [azc_bound, a_bound]:
        print(f"\n{bound['label']}:")
        print(f"  Lines analyzed: {bound['total_lines']}")
        print(f"  B-style initial markers: {bound['b_initial_markers']} ({bound['b_initial_rate']:.1%})")
        print(f"  B-style final markers: {bound['b_final_markers']} ({bound['b_final_rate']:.1%})")
        print(f"  Top 5 line-initial: {bound['top_initial']}")
        print(f"  Top 5 line-final: {bound['top_final']}")

        if bound['b_initial_rate'] > 0.05 or bound['b_final_rate'] > 0.05:
            print(f"  -> SHARES some B boundary vocabulary")
        else:
            print(f"  -> DIFFERENT boundary vocabulary from B")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    azc_like_b = (azc_reg and azc_reg['observed_cv'] < 0.4) or (azc_bound['b_initial_rate'] > 0.05)
    a_like_b = (a_reg and a_reg['observed_cv'] < 0.4) or (a_bound['b_initial_rate'] > 0.05)

    print(f"\nAZC line structure similar to B: {'YES' if azc_like_b else 'NO'}")
    print(f"Currier A line structure similar to B: {'YES' if a_like_b else 'NO'}")

    if not azc_like_b and not a_like_b:
        conclusion = "CONFIRMED: AZC and A use DIFFERENT line logic than B. No additional constraints needed."
    elif azc_like_b and not a_like_b:
        conclusion = "AZC shows B-like patterns - may need additional analysis."
    elif a_like_b and not azc_like_b:
        conclusion = "Currier A shows unexpected B-like patterns - investigate."
    else:
        conclusion = "Both show B-like patterns - unexpected, needs investigation."

    print(f"\n{conclusion}")

if __name__ == '__main__':
    main()
