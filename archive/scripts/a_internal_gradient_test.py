"""
A-INTERNAL GRADIENT STRESS TEST

Question: Does Currier A show internal ordering by frequency or complexity?

This is a STRESS TEST, not discovery. Either outcome is informative:
- Weak gradient -> possible pedagogical structure (Tier 2 if signal)
- Clean null -> strengthens flat registry model

STRICTLY FORBIDDEN:
- "Difficulty" language
- Pedagogical intent inference
- External cognitive models
- Forcing a narrative
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

def load_a_data():
    """Load Currier A data with folio and position info."""
    data = []
    folio_order = []  # Track folio order as encountered

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            if row.get('language') != 'A':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            folio = row['folio']
            section = row.get('section', '')

            if folio not in folio_order:
                folio_order.append(folio)

            data.append({
                'token': token,
                'folio': folio,
                'section': section,
                'folio_idx': folio_order.index(folio)
            })

    return data, folio_order

def test_frequency_vs_position(data, folio_order):
    """Test 1: Do high-frequency tokens appear earlier in manuscript?"""
    print("="*70)
    print("TEST 1: TOKEN FREQUENCY VS FOLIO POSITION")
    print("="*70)

    # Global token frequency
    token_freq = Counter(row['token'] for row in data)

    # For each token, compute mean folio position
    token_positions = defaultdict(list)
    for row in data:
        token_positions[row['token']].append(row['folio_idx'])

    token_mean_pos = {t: np.mean(positions) for t, positions in token_positions.items()}

    # Correlation: frequency vs mean position
    tokens = list(token_freq.keys())
    freqs = [token_freq[t] for t in tokens]
    positions = [token_mean_pos[t] for t in tokens]

    rho, p = spearmanr(freqs, positions)

    print(f"\nTokens analyzed: {len(tokens)}")
    print(f"Spearman correlation (freq vs position): rho={rho:.4f}, p={p:.2e}")

    # Interpretation
    if abs(rho) < 0.1:
        print("-> NULL: No relationship between frequency and position")
    elif rho < -0.1:
        print("-> GRADIENT: High-frequency tokens appear EARLIER")
    else:
        print("-> REVERSE: High-frequency tokens appear LATER")

    # Bin analysis: compare early vs late folios
    n_folios = len(folio_order)
    early_cutoff = n_folios // 3
    late_cutoff = 2 * n_folios // 3

    early_tokens = [row['token'] for row in data if row['folio_idx'] < early_cutoff]
    late_tokens = [row['token'] for row in data if row['folio_idx'] >= late_cutoff]

    early_freq = Counter(early_tokens)
    late_freq = Counter(late_tokens)

    # TTR comparison
    early_ttr = len(set(early_tokens)) / len(early_tokens) if early_tokens else 0
    late_ttr = len(set(late_tokens)) / len(late_tokens) if late_tokens else 0

    print(f"\nEarly third ({early_cutoff} folios): {len(early_tokens)} tokens, TTR={early_ttr:.3f}")
    print(f"Late third ({n_folios - late_cutoff} folios): {len(late_tokens)} tokens, TTR={late_ttr:.3f}")

    if early_ttr < late_ttr * 0.9:
        print("-> GRADIENT: Early folios have LOWER diversity (more repetition)")
    elif early_ttr > late_ttr * 1.1:
        print("-> REVERSE: Early folios have HIGHER diversity")
    else:
        print("-> NULL: No diversity gradient")

    return rho

def test_section_characteristics(data):
    """Test 2: Do sections H/P/T differ in vocabulary characteristics?"""
    print("\n" + "="*70)
    print("TEST 2: SECTION VOCABULARY CHARACTERISTICS")
    print("="*70)

    section_data = defaultdict(list)
    for row in data:
        section_data[row['section']].append(row['token'])

    print(f"\nSections found: {sorted(section_data.keys())}")

    for section in sorted(section_data.keys()):
        tokens = section_data[section]
        if len(tokens) < 100:
            continue

        freq = Counter(tokens)
        unique = len(freq)
        total = len(tokens)
        ttr = unique / total

        # Token length distribution
        lengths = [len(t) for t in tokens]
        mean_len = np.mean(lengths)

        # Top token concentration
        top_10_count = sum(c for _, c in freq.most_common(10))
        top_10_pct = top_10_count / total * 100

        print(f"\nSection {section}:")
        print(f"  Tokens: {total}, Unique: {unique}, TTR: {ttr:.3f}")
        print(f"  Mean token length: {mean_len:.2f}")
        print(f"  Top-10 concentration: {top_10_pct:.1f}%")

    # Compare sections
    if 'H' in section_data and 'P' in section_data:
        h_ttr = len(set(section_data['H'])) / len(section_data['H'])
        p_ttr = len(set(section_data['P'])) / len(section_data['P'])

        h_len = np.mean([len(t) for t in section_data['H']])
        p_len = np.mean([len(t) for t in section_data['P']])

        print(f"\nH vs P comparison:")
        print(f"  TTR: H={h_ttr:.3f}, P={p_ttr:.3f}")
        print(f"  Mean length: H={h_len:.2f}, P={p_len:.2f}")

        if abs(h_ttr - p_ttr) < 0.02 and abs(h_len - p_len) < 0.2:
            print("-> NULL: Sections have similar vocabulary characteristics")
        else:
            print("-> DIFFERENTIATED: Sections have distinct vocabulary profiles")

def test_morphological_complexity(data, folio_order):
    """Test 3: Does morphological complexity vary with position?"""
    print("\n" + "="*70)
    print("TEST 3: MORPHOLOGICAL COMPLEXITY VS POSITION")
    print("="*70)

    # Simple complexity metric: token length
    folio_complexity = defaultdict(list)
    for row in data:
        folio_complexity[row['folio']].append(len(row['token']))

    # Compute mean complexity per folio
    folio_mean_complexity = {}
    for folio in folio_order:
        if folio in folio_complexity:
            folio_mean_complexity[folio] = np.mean(folio_complexity[folio])

    # Correlation with position
    folios = [f for f in folio_order if f in folio_mean_complexity]
    positions = [folio_order.index(f) for f in folios]
    complexities = [folio_mean_complexity[f] for f in folios]

    rho, p = spearmanr(positions, complexities)

    print(f"\nFolios analyzed: {len(folios)}")
    print(f"Spearman (position vs mean token length): rho={rho:.4f}, p={p:.2e}")

    if abs(rho) < 0.1:
        print("-> NULL: No complexity gradient")
    elif rho > 0.1:
        print("-> GRADIENT: Later folios have LONGER tokens")
    else:
        print("-> REVERSE: Later folios have SHORTER tokens")

    # Component count (rough: count of common suffixes/prefixes)
    PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ol', 'al', 'sa', 'ct']
    SUFFIXES = ['edy', 'aiin', 'y', 'ar', 'ain', 'ey', 'dy', 'or', 'in', 'am']

    def count_components(token):
        count = 0
        for p in PREFIXES:
            if token.startswith(p):
                count += 1
                break
        for s in SUFFIXES:
            if token.endswith(s):
                count += 1
                break
        return count

    folio_components = defaultdict(list)
    for row in data:
        folio_components[row['folio']].append(count_components(row['token']))

    folio_mean_comp = {f: np.mean(c) for f, c in folio_components.items()}

    folios2 = [f for f in folio_order if f in folio_mean_comp]
    positions2 = [folio_order.index(f) for f in folios2]
    components = [folio_mean_comp[f] for f in folios2]

    rho2, p2 = spearmanr(positions2, components)

    print(f"\nSpearman (position vs component count): rho={rho2:.4f}, p={p2:.2e}")

    if abs(rho2) < 0.1:
        print("-> NULL: No compositional gradient")
    elif rho2 > 0.1:
        print("-> GRADIENT: Later folios have MORE components")
    else:
        print("-> REVERSE: Later folios have FEWER components")

    return rho, rho2

def test_first_occurrence_position(data, folio_order):
    """Test 4: Do common tokens appear earlier than rare tokens?"""
    print("\n" + "="*70)
    print("TEST 4: FIRST OCCURRENCE POSITION VS FREQUENCY")
    print("="*70)

    # Track first occurrence of each token
    token_first = {}
    for row in data:
        token = row['token']
        if token not in token_first:
            token_first[token] = row['folio_idx']

    # Global frequency
    token_freq = Counter(row['token'] for row in data)

    # Correlation: frequency vs first occurrence
    tokens = list(token_first.keys())
    freqs = [token_freq[t] for t in tokens]
    first_pos = [token_first[t] for t in tokens]

    rho, p = spearmanr(freqs, first_pos)

    print(f"\nTokens analyzed: {len(tokens)}")
    print(f"Spearman (frequency vs first occurrence): rho={rho:.4f}, p={p:.2e}")

    if abs(rho) < 0.1:
        print("-> NULL: First occurrence independent of frequency")
    elif rho < -0.1:
        print("-> GRADIENT: High-frequency tokens appear FIRST")
    else:
        print("-> REVERSE: High-frequency tokens appear LATER")

    return rho

def main():
    print("="*70)
    print("A-INTERNAL GRADIENT STRESS TEST")
    print("="*70)
    print("\nThis is a stress test, not discovery.")
    print("Either outcome (gradient or null) is informative.")

    data, folio_order = load_a_data()
    print(f"\nLoaded: {len(data)} tokens across {len(folio_order)} A folios")

    rho1 = test_frequency_vs_position(data, folio_order)
    test_section_characteristics(data)
    rho3a, rho3b = test_morphological_complexity(data, folio_order)
    rho4 = test_first_occurrence_position(data, folio_order)

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    correlations = {
        'Freq vs position': rho1,
        'Position vs length': rho3a,
        'Position vs components': rho3b,
        'Freq vs first occurrence': rho4
    }

    print("\nCorrelation summary:")
    for name, rho in correlations.items():
        strength = "NULL" if abs(rho) < 0.1 else ("WEAK" if abs(rho) < 0.2 else "MODERATE" if abs(rho) < 0.3 else "STRONG")
        print(f"  {name}: rho={rho:.4f} ({strength})")

    # Overall verdict
    significant_gradients = sum(1 for r in correlations.values() if abs(r) >= 0.15)

    print(f"\nSignificant gradients (|rho| >= 0.15): {significant_gradients}/4")

    if significant_gradients == 0:
        print("\n-> VERDICT: A is FLAT - no internal ordering by frequency or complexity")
        print("   Strengthens registry model.")
    elif significant_gradients <= 1:
        print("\n-> VERDICT: WEAK gradient - possible artifact, not structural")
    else:
        print("\n-> VERDICT: GRADIENT exists - document as Tier 2 finding")

if __name__ == '__main__':
    main()
