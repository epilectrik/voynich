#!/usr/bin/env python3
"""
ats_07_szone_bterminal.py - H7: S-Zone to B-Terminal Vocabulary Overlap

Tests whether S-zone MIDDLEs preferentially appear in STATE-C terminal B programs.

Threshold: Odds ratio >= 2.0, Fisher's exact p < 0.05
"""

import json
import sqlite3
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
DATA_DIR = PROJECT_ROOT / "data"

# S-zone positions
S_ZONES = ['S', 'S1', 'S2', 'S0']


def load_vocabulary_by_region():
    """
    Load vocabulary sets for S-zone (AZC) and B terminal programs.
    """
    transcript_path = DATA_DIR / "transcriptions" / "interlinear_full_words.txt"

    s_zone_vocab = set()
    b_terminal_vocab = set()
    b_nonterminal_vocab = set()

    # Track B folio line positions to identify terminal lines
    b_folio_lines = defaultdict(list)

    if not transcript_path.exists():
        return s_zone_vocab, b_terminal_vocab, b_nonterminal_vocab

    # First pass: collect all lines per B folio
    with open(transcript_path, 'r', encoding='utf-8') as f:
        header = True
        for line in f:
            if header:
                header = False
                continue

            parts = line.strip().split('\t')
            if len(parts) < 13:
                continue

            word = parts[0].strip('"')
            folio = parts[2].strip('"')
            currier = parts[6].strip('"')
            placement = parts[10].strip('"')
            line_num = parts[11].strip('"')
            transcriber = parts[12].strip('"')

            if transcriber != 'H':
                continue

            if currier == 'B':
                b_folio_lines[folio].append((line_num, word))

    # Identify terminal lines (last 2 lines per folio)
    terminal_lines = set()
    for folio, lines in b_folio_lines.items():
        if lines:
            unique_lines = sorted(set(ln for ln, _ in lines))
            if len(unique_lines) >= 2:
                terminal_lines.add((folio, unique_lines[-1]))
                terminal_lines.add((folio, unique_lines[-2]))
            elif len(unique_lines) == 1:
                terminal_lines.add((folio, unique_lines[0]))

    # Second pass: categorize vocabulary
    with open(transcript_path, 'r', encoding='utf-8') as f:
        header = True
        for line in f:
            if header:
                header = False
                continue

            parts = line.strip().split('\t')
            if len(parts) < 13:
                continue

            word = parts[0].strip('"')
            folio = parts[2].strip('"')
            currier = parts[6].strip('"')
            placement = parts[10].strip('"')
            line_num = parts[11].strip('"')
            transcriber = parts[12].strip('"')

            if transcriber != 'H':
                continue

            # S-zone vocabulary (AZC tokens in S positions)
            if currier == 'NA' and placement in S_ZONES:
                s_zone_vocab.add(word)

            # B vocabulary
            if currier == 'B':
                if (folio, line_num) in terminal_lines:
                    b_terminal_vocab.add(word)
                else:
                    b_nonterminal_vocab.add(word)

    return s_zone_vocab, b_terminal_vocab, b_nonterminal_vocab


def main():
    print("=" * 70)
    print("AZC_TRAJECTORY_SHAPE: H7 - S-Zone to B-Terminal Overlap")
    print("=" * 70)
    print()
    print("Prediction: S-zone vocabulary enriched in B terminal programs")
    print("Threshold: Odds ratio >= 2.0, Fisher's exact p < 0.05")
    print()

    # Load vocabulary
    s_zone, b_terminal, b_nonterminal = load_vocabulary_by_region()

    print("-" * 70)
    print("VOCABULARY SIZES")
    print("-" * 70)
    print(f"\nS-zone unique words: {len(s_zone)}")
    print(f"B-terminal unique words: {len(b_terminal)}")
    print(f"B-nonterminal unique words: {len(b_nonterminal)}")

    # Compute overlap
    s_in_terminal = s_zone & b_terminal
    s_in_nonterminal = s_zone & b_nonterminal
    s_not_in_b = s_zone - (b_terminal | b_nonterminal)

    print("\n" + "-" * 70)
    print("S-ZONE VOCABULARY DISTRIBUTION IN B")
    print("-" * 70)
    print(f"\nS-zone words appearing in B-terminal: {len(s_in_terminal)}")
    print(f"S-zone words appearing in B-nonterminal: {len(s_in_nonterminal)}")
    print(f"S-zone words not in B: {len(s_not_in_b)}")

    if s_in_terminal:
        print(f"\nS-zone in B-terminal sample: {list(s_in_terminal)[:10]}")

    # Contingency table for Fisher's exact test
    # Rows: In S-zone vs Not in S-zone
    # Cols: In B-terminal vs In B-nonterminal

    # Words in B-terminal that are in S-zone
    a = len(s_in_terminal)
    # Words in B-nonterminal that are in S-zone
    b = len(s_in_nonterminal)
    # Words in B-terminal that are NOT in S-zone
    c = len(b_terminal - s_zone)
    # Words in B-nonterminal that are NOT in S-zone
    d = len(b_nonterminal - s_zone)

    print("\n" + "-" * 70)
    print("CONTINGENCY TABLE")
    print("-" * 70)
    print(f"\n              B-terminal    B-nonterminal")
    print(f"In S-zone        {a:5d}          {b:5d}")
    print(f"Not in S-zone    {c:5d}          {d:5d}")

    # Fisher's exact test
    contingency = [[a, b], [c, d]]
    odds_ratio, fisher_p = stats.fisher_exact(contingency)

    print("\n" + "-" * 70)
    print("STATISTICAL TESTS")
    print("-" * 70)
    print(f"\nFisher's exact test:")
    print(f"  Odds ratio = {odds_ratio:.4f}")
    print(f"  p-value = {fisher_p:.4f}")

    # Also compute enrichment ratio
    if len(b_terminal) > 0 and len(b_nonterminal) > 0:
        terminal_rate = len(s_in_terminal) / len(b_terminal)
        nonterminal_rate = len(s_in_nonterminal) / len(b_nonterminal)
        enrichment = terminal_rate / nonterminal_rate if nonterminal_rate > 0 else float('inf')
    else:
        enrichment = 0

    print(f"\nEnrichment ratio (terminal/nonterminal rate): {enrichment:.4f}")

    # Hypothesis evaluation
    print("\n" + "=" * 70)
    print("HYPOTHESIS EVALUATION")
    print("=" * 70)

    or_threshold = odds_ratio >= 2.0
    significance = fisher_p < 0.05

    print(f"\nOdds ratio >= 2.0: {'PASS' if or_threshold else 'FAIL'}")
    print(f"  Odds ratio = {odds_ratio:.4f}")

    print(f"\nStatistical significance (p < 0.05): {'PASS' if significance else 'FAIL'}")
    print(f"  p-value = {fisher_p:.4f}")

    passed = or_threshold and significance
    print("\n" + "-" * 70)
    print(f"H7 VERDICT: {'PASS' if passed else 'FAIL'}")
    print("-" * 70)

    # Save results
    results = {
        'hypothesis': 'H7',
        'name': 'S-Zone to B-Terminal Vocabulary Overlap',
        'prediction': 'S-zone MIDDLEs enriched in B-terminal programs',
        'threshold': 'Odds ratio >= 2.0, Fisher p < 0.05',
        'vocabulary_sizes': {
            's_zone': len(s_zone),
            'b_terminal': len(b_terminal),
            'b_nonterminal': len(b_nonterminal),
        },
        'overlap': {
            's_in_terminal': len(s_in_terminal),
            's_in_nonterminal': len(s_in_nonterminal),
            's_not_in_b': len(s_not_in_b),
        },
        'contingency_table': {
            'a_s_terminal': a,
            'b_s_nonterminal': b,
            'c_not_s_terminal': c,
            'd_not_s_nonterminal': d,
        },
        'statistics': {
            'odds_ratio': float(odds_ratio),
            'fisher_p': float(fisher_p),
            'enrichment_ratio': float(enrichment) if enrichment != float('inf') else None,
        },
        'evaluation': {
            'odds_ratio_met': bool(or_threshold),
            'significant': bool(significance),
            'passed': bool(passed),
        },
        's_zone_in_terminal': list(s_in_terminal),
    }

    output_path = RESULTS_DIR / "ats_szone_bterminal.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
