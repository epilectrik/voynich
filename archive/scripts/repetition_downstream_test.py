"""
Coffin-nail test: Does repetition magnitude correlate with anything downstream?

If NO correlation: Repetition is ORDINAL EMPHASIS only
If correlation: Would suggest quantitative meaning

Tests:
1. Repetition count vs HT density (per line)
2. Repetition count vs HT morphological diversity
3. Repetition count vs line position in folio
4. Repetition count vs token diversity in line

Prediction: NO correlation (repetition is emphasis, not quantity)
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

# Known HT prefixes (from context system)
HT_PREFIXES = {'s', 'd', 'y', 'o', 'q', 'l', 'r', 'p', 'f', 'm', 'n'}


def load_data():
    """Load A lines with HT information."""
    a_lines = defaultdict(list)  # (folio, line_num) -> [tokens]
    ht_by_line = defaultdict(list)  # (folio, line_num) -> [ht_tokens]

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
            line_num = row.get('line_number', '0')

            try:
                line_num = int(line_num)
            except:
                line_num = 0

            if lang == 'A':
                a_lines[(folio, line_num)].append(token)

            # Check if this is an HT token (simplified: unusual prefix in A context)
            # Actually, let's look for HT tokens in the same line
            # HT tokens are typically in B but can mark A lines too

    return a_lines


def compute_line_metrics(a_lines):
    """Compute repetition and other metrics per line."""
    metrics = []

    for (folio, line_num), tokens in a_lines.items():
        if len(tokens) < 2:
            continue

        token_counts = Counter(tokens)
        max_rep = max(token_counts.values())
        total_rep = sum(c for c in token_counts.values() if c > 1)
        n_repeated_types = sum(1 for c in token_counts.values() if c > 1)

        # Token diversity
        unique_tokens = len(set(tokens))
        type_token_ratio = unique_tokens / len(tokens)

        # Morphological diversity (prefix entropy)
        prefixes = [t[0] if t else '' for t in tokens]
        prefix_counts = Counter(prefixes)
        prefix_entropy = -sum((c/len(tokens)) * np.log2(c/len(tokens))
                              for c in prefix_counts.values() if c > 0)

        # Position in folio (normalized)
        # This would need folio max line, approximate with line_num

        metrics.append({
            'folio': folio,
            'line_num': line_num,
            'n_tokens': len(tokens),
            'max_repetition': max_rep,
            'total_repetition': total_rep,
            'n_repeated_types': n_repeated_types,
            'has_repetition': 1 if max_rep > 1 else 0,
            'unique_tokens': unique_tokens,
            'type_token_ratio': type_token_ratio,
            'prefix_entropy': prefix_entropy
        })

    return metrics


def test_correlations(metrics):
    """Test if repetition correlates with downstream measures."""
    print("="*70)
    print("REPETITION DOWNSTREAM CORRELATION TEST")
    print("="*70)

    # Filter to lines with repetition for magnitude tests
    rep_lines = [m for m in metrics if m['has_repetition']]
    all_lines = metrics

    print(f"\nTotal lines: {len(all_lines)}")
    print(f"Lines with repetition: {len(rep_lines)}")

    # Test 1: Max repetition vs type-token ratio
    print("\n" + "-"*70)
    print("TEST 1: Repetition magnitude vs Type-Token Ratio")
    print("-"*70)

    if len(rep_lines) > 10:
        x = [m['max_repetition'] for m in rep_lines]
        y = [m['type_token_ratio'] for m in rep_lines]

        rho, p = stats.spearmanr(x, y)
        print(f"Spearman rho = {rho:.3f}, p = {p:.4f}")
        print(f"Interpretation: {'CORRELATION' if p < 0.05 else 'NO CORRELATION'}")

    # Test 2: Max repetition vs prefix entropy
    print("\n" + "-"*70)
    print("TEST 2: Repetition magnitude vs Morphological Diversity")
    print("-"*70)

    if len(rep_lines) > 10:
        x = [m['max_repetition'] for m in rep_lines]
        y = [m['prefix_entropy'] for m in rep_lines]

        rho, p = stats.spearmanr(x, y)
        print(f"Spearman rho = {rho:.3f}, p = {p:.4f}")
        print(f"Interpretation: {'CORRELATION' if p < 0.05 else 'NO CORRELATION'}")

    # Test 3: Max repetition vs line length
    print("\n" + "-"*70)
    print("TEST 3: Repetition magnitude vs Line Length")
    print("-"*70)

    if len(rep_lines) > 10:
        x = [m['max_repetition'] for m in rep_lines]
        y = [m['n_tokens'] for m in rep_lines]

        rho, p = stats.spearmanr(x, y)
        print(f"Spearman rho = {rho:.3f}, p = {p:.4f}")
        print(f"Interpretation: {'CORRELATION' if p < 0.05 else 'NO CORRELATION'}")

        # This one might correlate simply because longer lines have more chance for repetition
        # Control for this
        print("\n  (Note: Correlation here is expected due to opportunity effect)")

    # Test 4: Max repetition vs line position
    print("\n" + "-"*70)
    print("TEST 4: Repetition magnitude vs Line Position")
    print("-"*70)

    if len(rep_lines) > 10:
        x = [m['max_repetition'] for m in rep_lines]
        y = [m['line_num'] for m in rep_lines]

        rho, p = stats.spearmanr(x, y)
        print(f"Spearman rho = {rho:.3f}, p = {p:.4f}")
        print(f"Interpretation: {'CORRELATION' if p < 0.05 else 'NO CORRELATION'}")

    # Test 5: Compare repeated vs non-repeated lines
    print("\n" + "-"*70)
    print("TEST 5: Repeated vs Non-Repeated Lines (downstream differences)")
    print("-"*70)

    rep_ttr = [m['type_token_ratio'] for m in rep_lines]
    norep_ttr = [m['type_token_ratio'] for m in metrics if not m['has_repetition']]

    if len(rep_ttr) > 10 and len(norep_ttr) > 10:
        stat, p = stats.mannwhitneyu(rep_ttr, norep_ttr, alternative='two-sided')
        print(f"\nType-Token Ratio:")
        print(f"  Repeated lines: {np.mean(rep_ttr):.3f} ± {np.std(rep_ttr):.3f}")
        print(f"  Non-repeated:   {np.mean(norep_ttr):.3f} ± {np.std(norep_ttr):.3f}")
        print(f"  Mann-Whitney U p = {p:.4f}")
        print(f"  Interpretation: {'DIFFERENT' if p < 0.05 else 'NO DIFFERENCE'}")

    rep_ent = [m['prefix_entropy'] for m in rep_lines]
    norep_ent = [m['prefix_entropy'] for m in metrics if not m['has_repetition']]

    if len(rep_ent) > 10 and len(norep_ent) > 10:
        stat, p = stats.mannwhitneyu(rep_ent, norep_ent, alternative='two-sided')
        print(f"\nPrefix Entropy:")
        print(f"  Repeated lines: {np.mean(rep_ent):.3f} ± {np.std(rep_ent):.3f}")
        print(f"  Non-repeated:   {np.mean(norep_ent):.3f} ± {np.std(norep_ent):.3f}")
        print(f"  Mann-Whitney U p = {p:.4f}")
        print(f"  Interpretation: {'DIFFERENT' if p < 0.05 else 'NO DIFFERENCE'}")

    # Test 6: Does 2x vs 3x vs 4x matter?
    print("\n" + "-"*70)
    print("TEST 6: Does Repetition MAGNITUDE Matter? (2x vs 3x vs 4x+)")
    print("-"*70)

    by_magnitude = defaultdict(list)
    for m in rep_lines:
        mag = min(m['max_repetition'], 4)  # Group 4+ together
        by_magnitude[mag].append(m)

    print(f"\nSample sizes by magnitude:")
    for mag in sorted(by_magnitude.keys()):
        print(f"  {mag}x: {len(by_magnitude[mag])} lines")

    # Compare TTR across magnitudes
    if len(by_magnitude[2]) > 10 and len(by_magnitude[3]) >= 5:
        ttr_2x = [m['type_token_ratio'] for m in by_magnitude[2]]
        ttr_3x = [m['type_token_ratio'] for m in by_magnitude[3]]

        stat, p = stats.mannwhitneyu(ttr_2x, ttr_3x, alternative='two-sided')
        print(f"\n2x vs 3x Type-Token Ratio:")
        print(f"  2x: {np.mean(ttr_2x):.3f} ± {np.std(ttr_2x):.3f}")
        print(f"  3x: {np.mean(ttr_3x):.3f} ± {np.std(ttr_3x):.3f}")
        print(f"  Mann-Whitney U p = {p:.4f}")
        print(f"  Interpretation: {'MAGNITUDE MATTERS' if p < 0.05 else 'MAGNITUDE DOES NOT MATTER'}")

    return by_magnitude


def main():
    print("Loading data...")
    a_lines = load_data()
    print(f"Loaded {len(a_lines)} A lines")

    print("\nComputing metrics...")
    metrics = compute_line_metrics(a_lines)

    by_magnitude = test_correlations(metrics)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print("""
If repetition encoded QUANTITATIVE information, we would expect:
- Magnitude to correlate with downstream structure
- 2x vs 3x to produce measurably different effects
- Repeated lines to differ structurally from non-repeated

If repetition encodes ORDINAL EMPHASIS only:
- Magnitude should NOT correlate with structure
- 2x vs 3x should be interchangeable (just "emphasized")
- The distinction is MARKED vs UNMARKED, not quantity
""")


if __name__ == '__main__':
    main()
