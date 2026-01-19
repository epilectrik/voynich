#!/usr/bin/env python3
"""
HT Morphology Analysis: Currier A vs Currier B

Purpose: Investigate why HT tokens have different morphology in Currier A vs Currier B.

Background:
- Currier A prefers SIMPLEX HT forms: bare atoms (y, d, r), short forms
- Currier B prefers COMPLEX HT forms: multi-syllabic (ycheey, ytaiin, ykeedy)
- Only 22 HT forms are shared between A and B (out of 79 A-forms and 142 B-forms)

HT Token Definition:
- All tokens starting with 'y' OR single-char atoms (y, f, d, r)

Analysis:
1. Full morphological breakdown (prefix + core + suffix distribution)
2. Compositional complexity (length, character distribution)
3. The 22 shared forms - what are they?
4. Productive composition vs fixed vocabulary test
5. Hypothesis: A's simplex = registry labels, B's complex = execution annotations
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import re
from pathlib import Path

# =============================================================================
# DATA LOADING
# =============================================================================

def load_data(filepath):
    """Load the interlinear transcription data."""
    df = pd.read_csv(filepath, sep='\t', na_values='NA')
    # Filter to H transcriber only
    df = df[df['transcriber'] == 'H']
    return df

def get_folio_range(df, start, end):
    """Get tokens from folio range."""
    folios = df['folio'].unique()

    # Parse folio numbers
    def parse_folio(f):
        match = re.match(r'f(\d+)([rv])', str(f))
        if match:
            num = int(match.group(1))
            side = 0 if match.group(2) == 'r' else 0.5
            return num + side
        return 0

    start_val = parse_folio(start)
    end_val = parse_folio(end)

    mask = df['folio'].apply(lambda x: start_val <= parse_folio(x) <= end_val)
    return df[mask]

# =============================================================================
# HT TOKEN IDENTIFICATION
# =============================================================================

def is_ht_token(token):
    """
    HT tokens: All tokens starting with 'y' OR single-char atoms (y, f, d, r).
    Exclude tokens with transcription marks (* characters).
    """
    if not isinstance(token, str) or '*' in token:
        return False

    # Clean token
    token = token.strip().lower()

    # Single char atoms
    if token in ['y', 'f', 'd', 'r']:
        return True

    # y-initial tokens
    if token.startswith('y'):
        return True

    return False

def extract_ht_tokens(df, language_filter=None):
    """Extract HT tokens from dataframe."""
    # Use one transcriber to avoid duplicates (pick the most common)
    transcriber = df['transcriber'].mode().iloc[0] if not df['transcriber'].mode().empty else 'H'
    df_unique = df[df['transcriber'] == transcriber]

    if language_filter:
        df_unique = df_unique[df_unique['language'] == language_filter]

    # Get HT tokens
    ht_mask = df_unique['word'].apply(is_ht_token)
    ht_tokens = df_unique[ht_mask]['word'].tolist()

    return ht_tokens

# =============================================================================
# MORPHOLOGICAL DECOMPOSITION
# =============================================================================

# Known morphological patterns based on project constraints
HT_PREFIXES = ['ych', 'yk', 'yt', 'yp', 'yf', 'yd', 'ys', 'yo', 'ya', 'ykch', 'y']
COMMON_SUFFIXES = ['-aiin', '-ain', '-iin', '-in', '-dy', '-edy', '-ey', '-y', '-ar', '-or', '-r', '-al', '-ol', '-l', '-hy', '-eey']
COMMON_MIDDLES = ['ch', 'sh', 'k', 't', 'p', 'd', 'ke', 'te', 'pe', 'o', 'a', 'e', 'ol', 'al']

def decompose_ht_token(token):
    """
    Decompose HT token into PREFIX + MIDDLE + SUFFIX.
    Returns dict with components.
    """
    token = str(token).lower().strip()

    result = {
        'original': token,
        'prefix': '',
        'middle': '',
        'suffix': '',
        'length': len(token),
        'is_atom': len(token) == 1,
        'structure_type': 'UNKNOWN'
    }

    # Single char atoms
    if len(token) == 1:
        result['prefix'] = token
        result['structure_type'] = 'ATOM'
        return result

    # Try to match y-prefixes (longest first)
    remaining = token
    for prefix in sorted(HT_PREFIXES, key=len, reverse=True):
        if token.startswith(prefix):
            result['prefix'] = prefix
            remaining = token[len(prefix):]
            break

    if not result['prefix']:
        result['prefix'] = token[0] if token else ''
        remaining = token[1:]

    # Try to match suffixes (longest first)
    suffix_patterns = sorted(COMMON_SUFFIXES, key=len, reverse=True)
    for suffix in suffix_patterns:
        suffix_clean = suffix.lstrip('-')
        if remaining.endswith(suffix_clean):
            result['suffix'] = suffix_clean
            remaining = remaining[:-len(suffix_clean)]
            break

    result['middle'] = remaining

    # Classify structure type
    if result['is_atom']:
        result['structure_type'] = 'ATOM'
    elif not result['middle'] and not result['suffix']:
        result['structure_type'] = 'PREFIX_ONLY'
    elif not result['middle']:
        result['structure_type'] = 'PREFIX+SUFFIX'
    elif not result['suffix']:
        result['structure_type'] = 'PREFIX+MIDDLE'
    else:
        result['structure_type'] = 'FULL_COMPOSITIONAL'

    return result

# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def analyze_morphology(tokens, label=""):
    """Full morphological breakdown of HT tokens."""
    decomposed = [decompose_ht_token(t) for t in tokens]

    # Count unique tokens
    unique_tokens = list(set(tokens))

    # Statistics
    lengths = [d['length'] for d in decomposed]
    prefixes = Counter([d['prefix'] for d in decomposed])
    middles = Counter([d['middle'] for d in decomposed if d['middle']])
    suffixes = Counter([d['suffix'] for d in decomposed if d['suffix']])
    structures = Counter([d['structure_type'] for d in decomposed])

    print(f"\n{'='*60}")
    print(f"MORPHOLOGICAL ANALYSIS: {label}")
    print(f"{'='*60}")
    print(f"Total HT tokens: {len(tokens)}")
    print(f"Unique HT types: {len(unique_tokens)}")
    print(f"TTR (type/token): {len(unique_tokens)/len(tokens):.3f}" if tokens else "N/A")

    print(f"\n--- Length Statistics ---")
    print(f"Mean length: {np.mean(lengths):.2f}")
    print(f"Median length: {np.median(lengths):.1f}")
    print(f"Min: {min(lengths)}, Max: {max(lengths)}")
    print(f"Std dev: {np.std(lengths):.2f}")

    # Length distribution
    length_dist = Counter(lengths)
    print(f"\nLength distribution:")
    for length in sorted(length_dist.keys()):
        pct = 100 * length_dist[length] / len(tokens)
        print(f"  {length:2d} chars: {length_dist[length]:5d} ({pct:5.1f}%)")

    print(f"\n--- Structure Types ---")
    for stype, count in structures.most_common():
        pct = 100 * count / len(tokens)
        print(f"  {stype:20s}: {count:5d} ({pct:5.1f}%)")

    print(f"\n--- Top 15 Prefixes ---")
    for prefix, count in prefixes.most_common(15):
        pct = 100 * count / len(tokens)
        print(f"  {prefix:8s}: {count:5d} ({pct:5.1f}%)")

    print(f"\n--- Top 15 Suffixes ---")
    for suffix, count in suffixes.most_common(15):
        pct = 100 * count / len(tokens)
        print(f"  {suffix:8s}: {count:5d} ({pct:5.1f}%)")

    print(f"\n--- Top 15 Middles ---")
    for middle, count in middles.most_common(15):
        pct = 100 * count / len(tokens)
        print(f"  {middle:8s}: {count:5d} ({pct:5.1f}%)")

    return {
        'tokens': tokens,
        'unique_tokens': unique_tokens,
        'decomposed': decomposed,
        'prefixes': prefixes,
        'middles': middles,
        'suffixes': suffixes,
        'structures': structures,
        'mean_length': np.mean(lengths),
        'lengths': lengths
    }

def find_shared_forms(a_tokens, b_tokens):
    """Find HT forms shared between A and B."""
    a_unique = set(a_tokens)
    b_unique = set(b_tokens)
    shared = a_unique & b_unique

    print(f"\n{'='*60}")
    print(f"SHARED HT FORMS ANALYSIS")
    print(f"{'='*60}")
    print(f"A-only forms: {len(a_unique - shared)}")
    print(f"B-only forms: {len(b_unique - shared)}")
    print(f"Shared forms: {len(shared)}")

    if shared:
        print(f"\nShared forms list:")
        # Count frequency in each system
        a_counts = Counter(a_tokens)
        b_counts = Counter(b_tokens)

        shared_info = []
        for form in shared:
            shared_info.append({
                'form': form,
                'a_count': a_counts[form],
                'b_count': b_counts[form],
                'total': a_counts[form] + b_counts[form],
                'length': len(form)
            })

        # Sort by total frequency
        shared_info.sort(key=lambda x: -x['total'])

        print(f"\n{'Form':<15} {'A count':>8} {'B count':>8} {'Total':>8} {'Length':>6}")
        print("-" * 50)
        for s in shared_info:
            print(f"{s['form']:<15} {s['a_count']:>8} {s['b_count']:>8} {s['total']:>8} {s['length']:>6}")

    return shared, a_unique - shared, b_unique - shared

def analyze_composition_productivity(tokens, label=""):
    """
    Test whether complexity comes from PRODUCTIVE COMPOSITION or FIXED VOCABULARY.

    If productive: We should see systematic suffix/prefix patterns that combine freely.
    If fixed: We should see many unique atomic forms with low combinatorial structure.
    """
    decomposed = [decompose_ht_token(t) for t in tokens]
    unique_tokens = set(tokens)

    print(f"\n{'='*60}")
    print(f"COMPOSITION PRODUCTIVITY TEST: {label}")
    print(f"{'='*60}")

    # Test 1: Suffix productivity
    # Group by prefix and count unique suffixes per prefix
    prefix_suffixes = defaultdict(set)
    for d in decomposed:
        if d['suffix']:
            prefix_suffixes[d['prefix']].add(d['suffix'])

    print(f"\n--- Suffix Productivity by Prefix ---")
    productive_prefixes = 0
    for prefix in sorted(prefix_suffixes.keys(), key=lambda x: -len(prefix_suffixes[x])):
        suffix_count = len(prefix_suffixes[prefix])
        if suffix_count > 1:
            productive_prefixes += 1
        suffixes = sorted(prefix_suffixes[prefix])[:5]
        print(f"  {prefix:8s}: {suffix_count:2d} suffixes ({', '.join(suffixes[:5])}{'...' if len(prefix_suffixes[prefix]) > 5 else ''})")

    # Test 2: Combinatorial coverage
    # How many of the theoretically possible combinations are attested?
    all_prefixes = set(d['prefix'] for d in decomposed if d['prefix'])
    all_suffixes = set(d['suffix'] for d in decomposed if d['suffix'])

    theoretical_combinations = len(all_prefixes) * len(all_suffixes)
    observed_combinations = len(set((d['prefix'], d['suffix']) for d in decomposed if d['prefix'] and d['suffix']))

    print(f"\n--- Combinatorial Coverage ---")
    print(f"Unique prefixes: {len(all_prefixes)}")
    print(f"Unique suffixes: {len(all_suffixes)}")
    print(f"Theoretical combinations: {theoretical_combinations}")
    print(f"Observed combinations: {observed_combinations}")
    print(f"Coverage: {100*observed_combinations/theoretical_combinations:.1f}%" if theoretical_combinations > 0 else "N/A")

    # Test 3: Hapax ratio
    token_counts = Counter(tokens)
    hapax = sum(1 for c in token_counts.values() if c == 1)
    hapax_ratio = hapax / len(unique_tokens) if unique_tokens else 0

    print(f"\n--- Hapax Analysis ---")
    print(f"Hapax legomena (occur once): {hapax}")
    print(f"Hapax ratio: {100*hapax_ratio:.1f}%")

    # Interpretation
    print(f"\n--- Productivity Verdict ---")
    if productive_prefixes > 3 and observed_combinations > 20:
        print("PRODUCTIVE COMPOSITION: Multiple prefixes combine with multiple suffixes")
    elif hapax_ratio > 0.6:
        print("FIXED VOCABULARY: High hapax rate suggests many unique forms")
    else:
        print("MIXED: Some productivity with fixed elements")

    return {
        'productive_prefixes': productive_prefixes,
        'theoretical_combinations': theoretical_combinations,
        'observed_combinations': observed_combinations,
        'hapax_ratio': hapax_ratio
    }

def character_distribution_analysis(tokens_a, tokens_b):
    """Compare character-level distributions."""
    print(f"\n{'='*60}")
    print(f"CHARACTER DISTRIBUTION COMPARISON")
    print(f"{'='*60}")

    # Flatten to characters
    chars_a = [c for t in tokens_a for c in str(t)]
    chars_b = [c for t in tokens_b for c in str(t)]

    dist_a = Counter(chars_a)
    dist_b = Counter(chars_b)

    all_chars = sorted(set(dist_a.keys()) | set(dist_b.keys()))

    print(f"\n{'Char':<6} {'A count':>8} {'A %':>8} {'B count':>8} {'B %':>8} {'Diff':>8}")
    print("-" * 50)

    for char in all_chars:
        a_count = dist_a.get(char, 0)
        b_count = dist_b.get(char, 0)
        a_pct = 100 * a_count / len(chars_a) if chars_a else 0
        b_pct = 100 * b_count / len(chars_b) if chars_b else 0
        diff = b_pct - a_pct
        print(f"'{char}'  {a_count:>8} {a_pct:>7.1f}% {b_count:>8} {b_pct:>7.1f}% {diff:>+7.1f}%")

def test_truncation_hypothesis(a_tokens, b_tokens):
    """
    Test: Are A forms TRUNCATED versions of B forms?
    Or are they genuinely different vocabulary?
    """
    print(f"\n{'='*60}")
    print(f"TRUNCATION HYPOTHESIS TEST")
    print(f"{'='*60}")

    a_unique = set(a_tokens)
    b_unique = set(b_tokens)

    # Test 1: Are A forms prefixes of B forms?
    a_prefix_of_b = 0
    a_prefix_examples = []
    for a_form in a_unique:
        if len(a_form) <= 2:
            continue  # Skip atoms
        for b_form in b_unique:
            if b_form.startswith(a_form) and len(b_form) > len(a_form):
                a_prefix_of_b += 1
                if len(a_prefix_examples) < 10:
                    a_prefix_examples.append((a_form, b_form))
                break

    print(f"\nA forms that are prefixes of B forms: {a_prefix_of_b}/{len(a_unique)} ({100*a_prefix_of_b/len(a_unique):.1f}%)")
    if a_prefix_examples:
        print(f"Examples: {a_prefix_examples[:5]}")

    # Test 2: Are B forms extensions of A forms?
    b_extends_a = 0
    b_extends_examples = []
    for b_form in b_unique:
        for a_form in a_unique:
            if len(a_form) >= 2 and b_form.startswith(a_form) and len(b_form) > len(a_form):
                b_extends_a += 1
                if len(b_extends_examples) < 10:
                    b_extends_examples.append((a_form, b_form))
                break

    print(f"\nB forms that extend A forms: {b_extends_a}/{len(b_unique)} ({100*b_extends_a/len(b_unique):.1f}%)")
    if b_extends_examples:
        print(f"Examples: {b_extends_examples[:5]}")

    # Test 3: Shared morphological root analysis
    def get_root(token):
        """Extract root by removing common suffixes."""
        token = str(token)
        for suffix in ['aiin', 'ain', 'iin', 'in', 'dy', 'edy', 'ey', 'y', 'ar', 'or', 'r', 'al', 'ol', 'l']:
            if token.endswith(suffix) and len(token) > len(suffix):
                return token[:-len(suffix)]
        return token

    a_roots = set(get_root(t) for t in a_unique)
    b_roots = set(get_root(t) for t in b_unique)
    shared_roots = a_roots & b_roots

    print(f"\n--- Root Analysis ---")
    print(f"A unique roots: {len(a_roots)}")
    print(f"B unique roots: {len(b_roots)}")
    print(f"Shared roots: {len(shared_roots)}")

    if shared_roots:
        print(f"Sample shared roots: {sorted(shared_roots)[:15]}")

    # Verdict
    print(f"\n--- Truncation Verdict ---")
    if a_prefix_of_b / len(a_unique) > 0.3:
        print("TRUNCATION SUPPORTED: Many A forms are prefixes of B forms")
    elif len(shared_roots) / len(a_roots) > 0.3:
        print("SHARED ROOTS: A and B share morphological roots but different suffixation")
    else:
        print("DIFFERENT VOCABULARY: A and B use genuinely different HT forms")

def functional_hypothesis_test(a_analysis, b_analysis):
    """
    Test hypothesis: A's simplex = registry labels, B's complex = execution annotations
    """
    print(f"\n{'='*60}")
    print(f"FUNCTIONAL DIVERGENCE HYPOTHESIS")
    print(f"{'='*60}")

    # Compare structure types
    a_structures = a_analysis['structures']
    b_structures = b_analysis['structures']

    # Calculate proportions
    a_total = sum(a_structures.values())
    b_total = sum(b_structures.values())

    # Atoms (simplex forms)
    a_atom_pct = 100 * a_structures.get('ATOM', 0) / a_total if a_total else 0
    b_atom_pct = 100 * b_structures.get('ATOM', 0) / b_total if b_total else 0

    # Full compositional (complex forms)
    a_full_pct = 100 * a_structures.get('FULL_COMPOSITIONAL', 0) / a_total if a_total else 0
    b_full_pct = 100 * b_structures.get('FULL_COMPOSITIONAL', 0) / b_total if b_total else 0

    print(f"\n--- Simplex vs Complex Comparison ---")
    print(f"{'Metric':<25} {'Currier A':>12} {'Currier B':>12} {'Diff':>10}")
    print("-" * 60)
    print(f"{'ATOM (single char)':<25} {a_atom_pct:>11.1f}% {b_atom_pct:>11.1f}% {b_atom_pct-a_atom_pct:>+9.1f}%")
    print(f"{'FULL_COMPOSITIONAL':<25} {a_full_pct:>11.1f}% {b_full_pct:>11.1f}% {b_full_pct-a_full_pct:>+9.1f}%")
    print(f"{'Mean length':<25} {a_analysis['mean_length']:>12.2f} {b_analysis['mean_length']:>12.2f} {b_analysis['mean_length']-a_analysis['mean_length']:>+10.2f}")

    # Suffix diversity
    a_suffix_count = len(a_analysis['suffixes'])
    b_suffix_count = len(b_analysis['suffixes'])

    print(f"{'Unique suffixes':<25} {a_suffix_count:>12} {b_suffix_count:>12} {b_suffix_count-a_suffix_count:>+10}")
    print(f"{'Unique prefixes':<25} {len(a_analysis['prefixes']):>12} {len(b_analysis['prefixes']):>12}")

    # Interpretation
    print(f"\n--- Interpretation ---")
    if a_atom_pct > b_atom_pct * 1.5 and a_analysis['mean_length'] < b_analysis['mean_length']:
        print("HYPOTHESIS SUPPORTED:")
        print("  - A uses more simplex/atomic HT forms (short labels)")
        print("  - B uses more complex compositional HT forms (annotated procedures)")
        print("  - This matches A=registry vs B=execution grammar")
    else:
        print("HYPOTHESIS NEEDS REFINEMENT: Pattern not as clear as expected")

    # Specific comparisons
    print(f"\n--- Functional Role Evidence ---")

    # A-specific features
    a_only_prefixes = set(a_analysis['prefixes'].keys()) - set(b_analysis['prefixes'].keys())
    b_only_prefixes = set(b_analysis['prefixes'].keys()) - set(a_analysis['prefixes'].keys())

    print(f"A-only prefixes: {a_only_prefixes if len(a_only_prefixes) < 20 else f'{len(a_only_prefixes)} prefixes'}")
    print(f"B-only prefixes: {b_only_prefixes if len(b_only_prefixes) < 20 else f'{len(b_only_prefixes)} prefixes'}")

# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():
    # Load data
    data_path = Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt")
    print(f"Loading data from {data_path}...")
    df = load_data(data_path)
    print(f"Loaded {len(df)} records")

    # Define folio ranges
    # Currier A: f1r-f8v (early herbal)
    # Currier B: f103r-f108v (biological/balneological)

    # Filter by language column (A vs B)
    print(f"\nFiltering by Currier language designation...")
    df_a = df[df['language'] == 'A']
    df_b = df[df['language'] == 'B']

    print(f"Currier A records: {len(df_a)}")
    print(f"Currier B records: {len(df_b)}")

    # Also try specific folio ranges
    print(f"\nAlso checking specific folio ranges:")
    df_a_range = get_folio_range(df, 'f1r', 'f8v')
    df_b_range = get_folio_range(df, 'f103r', 'f108v')
    print(f"f1r-f8v (early herbal): {len(df_a_range)} records")
    print(f"f103r-f108v (biological): {len(df_b_range)} records")

    # Extract HT tokens
    print(f"\n{'#'*60}")
    print(f"# EXTRACTING HT TOKENS")
    print(f"{'#'*60}")

    # Use language designation for proper A vs B
    a_ht = extract_ht_tokens(df_a)
    b_ht = extract_ht_tokens(df_b)

    print(f"\nCurrier A HT tokens extracted: {len(a_ht)}")
    print(f"Currier B HT tokens extracted: {len(b_ht)}")

    if len(a_ht) < 50 or len(b_ht) < 50:
        print("WARNING: Low token counts. Using folio-range extraction as fallback.")
        a_ht_range = extract_ht_tokens(df_a_range)
        b_ht_range = extract_ht_tokens(df_b_range)
        print(f"Folio range A HT: {len(a_ht_range)}")
        print(f"Folio range B HT: {len(b_ht_range)}")

        # Merge if needed
        if len(a_ht_range) > len(a_ht):
            a_ht = a_ht_range
        if len(b_ht_range) > len(b_ht):
            b_ht = b_ht_range

    # ANALYSIS 1: Full morphological breakdown
    print(f"\n{'#'*60}")
    print(f"# ANALYSIS 1: MORPHOLOGICAL BREAKDOWN")
    print(f"{'#'*60}")

    a_analysis = analyze_morphology(a_ht, "CURRIER A")
    b_analysis = analyze_morphology(b_ht, "CURRIER B")

    # ANALYSIS 2: Character distribution
    print(f"\n{'#'*60}")
    print(f"# ANALYSIS 2: CHARACTER DISTRIBUTION")
    print(f"{'#'*60}")
    character_distribution_analysis(a_ht, b_ht)

    # ANALYSIS 3: Shared forms
    print(f"\n{'#'*60}")
    print(f"# ANALYSIS 3: SHARED FORMS")
    print(f"{'#'*60}")
    shared, a_only, b_only = find_shared_forms(a_ht, b_ht)

    # ANALYSIS 4: Truncation hypothesis
    print(f"\n{'#'*60}")
    print(f"# ANALYSIS 4: TRUNCATION HYPOTHESIS")
    print(f"{'#'*60}")
    test_truncation_hypothesis(a_ht, b_ht)

    # ANALYSIS 5: Composition productivity
    print(f"\n{'#'*60}")
    print(f"# ANALYSIS 5: COMPOSITION PRODUCTIVITY")
    print(f"{'#'*60}")
    a_prod = analyze_composition_productivity(a_ht, "CURRIER A")
    b_prod = analyze_composition_productivity(b_ht, "CURRIER B")

    # ANALYSIS 6: Functional hypothesis
    print(f"\n{'#'*60}")
    print(f"# ANALYSIS 6: FUNCTIONAL DIVERGENCE HYPOTHESIS")
    print(f"{'#'*60}")
    functional_hypothesis_test(a_analysis, b_analysis)

    # SUMMARY
    print(f"\n{'='*60}")
    print(f"EXECUTIVE SUMMARY")
    print(f"{'='*60}")

    print(f"""
Key Findings:

1. MORPHOLOGICAL COMPLEXITY:
   - Currier A mean HT length: {a_analysis['mean_length']:.2f} chars
   - Currier B mean HT length: {b_analysis['mean_length']:.2f} chars
   - Difference: {b_analysis['mean_length'] - a_analysis['mean_length']:+.2f} chars

2. VOCABULARY OVERLAP:
   - A unique HT types: {len(a_analysis['unique_tokens'])}
   - B unique HT types: {len(b_analysis['unique_tokens'])}
   - Shared types: {len(shared)}
   - Jaccard similarity: {len(shared)/(len(a_analysis['unique_tokens'])+len(b_analysis['unique_tokens'])-len(shared)):.3f}

3. STRUCTURE TYPE DISTRIBUTION:
   - A atoms: {100*a_analysis['structures'].get('ATOM',0)/len(a_ht):.1f}%
   - B atoms: {100*b_analysis['structures'].get('ATOM',0)/len(b_ht):.1f}%

4. PRODUCTIVITY:
   - A combinatorial coverage: {100*a_prod['observed_combinations']/a_prod['theoretical_combinations']:.1f}% (if applicable)
   - B combinatorial coverage: {100*b_prod['observed_combinations']/b_prod['theoretical_combinations']:.1f}% (if applicable)
   - A hapax ratio: {100*a_prod['hapax_ratio']:.1f}%
   - B hapax ratio: {100*b_prod['hapax_ratio']:.1f}%
""")

if __name__ == "__main__":
    main()
