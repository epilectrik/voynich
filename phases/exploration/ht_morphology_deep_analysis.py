#!/usr/bin/env python3
"""
HT Morphology Deep Analysis: Focus on -edy and other key differentiators

The initial analysis showed:
- -edy is 18.2% in B but only 0.3% in A (60x ratio!)
- A has more atoms (17.1% vs 11.6%)
- B has more FULL_COMPOSITIONAL (41.4% vs 35.5%)

This script investigates:
1. The -edy phenomenon specifically
2. What suffixes A uses instead
3. Whether B's complexity is from genuine enrichment or different suffix vocabulary
4. Context analysis of shared vs unique forms
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import re
from pathlib import Path

def load_data(filepath):
    df = pd.read_csv(filepath, sep='\t', na_values='NA', low_memory=False)
    return df

def is_ht_token(token):
    if not isinstance(token, str) or '*' in token:
        return False
    token = token.strip().lower()
    if token in ['y', 'f', 'd', 'r']:
        return True
    if token.startswith('y'):
        return True
    return False

def extract_ht_with_context(df, language):
    """Extract HT tokens with positional context."""
    transcriber = df['transcriber'].mode().iloc[0]
    df_filtered = df[(df['transcriber'] == transcriber) & (df['language'] == language)]

    results = []
    for _, row in df_filtered.iterrows():
        word = row['word']
        if is_ht_token(word):
            results.append({
                'word': word,
                'folio': row['folio'],
                'line_number': row['line_number'],
                'line_initial': row['line_initial'],
                'line_final': row['line_final'],
                'section': row.get('section', 'UNK')
            })
    return results

def analyze_suffix_distribution(tokens, label):
    """Detailed suffix analysis."""
    # Define suffixes from longest to shortest
    suffixes_ordered = [
        'aiin', 'aiir', 'oiin',
        'ain', 'iin', 'eey', 'edy', 'oly',
        'dy', 'ey', 'hy', 'ar', 'or', 'al', 'ol',
        'y', 'r', 'l', 'n', 'o', 'm'
    ]

    suffix_counts = Counter()
    suffix_tokens = defaultdict(list)

    for t in tokens:
        word = t['word'].lower()
        matched_suffix = None
        for suffix in suffixes_ordered:
            if word.endswith(suffix) and len(word) > len(suffix):
                matched_suffix = suffix
                break
        if matched_suffix:
            suffix_counts[matched_suffix] += 1
            suffix_tokens[matched_suffix].append(word)
        else:
            suffix_counts['NO_SUFFIX'] += 1

    print(f"\n{'='*60}")
    print(f"SUFFIX DISTRIBUTION: {label}")
    print(f"{'='*60}")

    total = sum(suffix_counts.values())
    for suffix, count in suffix_counts.most_common(20):
        pct = 100 * count / total
        examples = list(set(suffix_tokens[suffix]))[:5]
        print(f"  -{suffix:8s}: {count:5d} ({pct:5.1f}%) e.g. {examples}")

    return suffix_counts, suffix_tokens

def analyze_edy_phenomenon(a_tokens, b_tokens):
    """Deep dive into the -edy suffix."""
    print(f"\n{'='*60}")
    print(f"-EDY PHENOMENON ANALYSIS")
    print(f"{'='*60}")

    # Find all -edy tokens
    a_edy = [t for t in a_tokens if t['word'].endswith('edy')]
    b_edy = [t for t in b_tokens if t['word'].endswith('edy')]

    print(f"\nA -edy tokens: {len(a_edy)}")
    print(f"B -edy tokens: {len(b_edy)}")

    if a_edy:
        print(f"\nA -edy forms: {set(t['word'] for t in a_edy)}")

    if b_edy:
        b_edy_forms = Counter(t['word'] for t in b_edy)
        print(f"\nB -edy forms (top 15):")
        for form, count in b_edy_forms.most_common(15):
            print(f"  {form}: {count}")

    # What does A use instead?
    # Compare prefix distributions for tokens ending in -dy family
    a_dy = [t for t in a_tokens if t['word'].endswith('dy') and not t['word'].endswith('edy')]
    b_dy = [t for t in b_tokens if t['word'].endswith('dy') and not t['word'].endswith('edy')]

    print(f"\n--- -dy (non -edy) comparison ---")
    print(f"A -dy tokens: {len(a_dy)}")
    print(f"B -dy tokens: {len(b_dy)}")

    # -eey comparison (another B-enriched suffix)
    a_eey = [t for t in a_tokens if t['word'].endswith('eey')]
    b_eey = [t for t in b_tokens if t['word'].endswith('eey')]

    print(f"\n--- -eey comparison ---")
    print(f"A -eey tokens: {len(a_eey)} ({100*len(a_eey)/len(a_tokens):.1f}%)")
    print(f"B -eey tokens: {len(b_eey)} ({100*len(b_eey)/len(b_tokens):.1f}%)")

    # -or vs -ar (A-enriched)
    a_or = [t for t in a_tokens if t['word'].endswith('or')]
    b_or = [t for t in b_tokens if t['word'].endswith('or')]
    a_ar = [t for t in a_tokens if t['word'].endswith('ar') and not t['word'].endswith('ear')]
    b_ar = [t for t in b_tokens if t['word'].endswith('ar') and not t['word'].endswith('ear')]

    print(f"\n--- -or comparison (A-enriched?) ---")
    print(f"A -or tokens: {len(a_or)} ({100*len(a_or)/len(a_tokens):.1f}%)")
    print(f"B -or tokens: {len(b_or)} ({100*len(b_or)/len(b_tokens):.1f}%)")

    print(f"\n--- -ar comparison ---")
    print(f"A -ar tokens: {len(a_ar)} ({100*len(a_ar)/len(a_tokens):.1f}%)")
    print(f"B -ar tokens: {len(b_ar)} ({100*len(b_ar)/len(b_tokens):.1f}%)")

    # -ol (A-enriched)
    a_ol = [t for t in a_tokens if t['word'].endswith('ol')]
    b_ol = [t for t in b_tokens if t['word'].endswith('ol')]

    print(f"\n--- -ol comparison (A-enriched?) ---")
    print(f"A -ol tokens: {len(a_ol)} ({100*len(a_ol)/len(a_tokens):.1f}%)")
    print(f"B -ol tokens: {len(b_ol)} ({100*len(b_ol)/len(b_tokens):.1f}%)")

def analyze_positional_differences(a_tokens, b_tokens):
    """See if HT distribution differs by line position."""
    print(f"\n{'='*60}")
    print(f"POSITIONAL DISTRIBUTION")
    print(f"{'='*60}")

    # Line initial rates
    a_initial = sum(1 for t in a_tokens if t['line_initial'] == 1)
    b_initial = sum(1 for t in b_tokens if t['line_initial'] == 1)

    a_final = sum(1 for t in a_tokens if t['line_final'] == 1)
    b_final = sum(1 for t in b_tokens if t['line_final'] == 1)

    print(f"\nLine-initial HT tokens:")
    print(f"  A: {a_initial}/{len(a_tokens)} ({100*a_initial/len(a_tokens):.1f}%)")
    print(f"  B: {b_initial}/{len(b_tokens)} ({100*b_initial/len(b_tokens):.1f}%)")

    print(f"\nLine-final HT tokens:")
    print(f"  A: {a_final}/{len(a_tokens)} ({100*a_final/len(a_tokens):.1f}%)")
    print(f"  B: {b_final}/{len(b_tokens)} ({100*b_final/len(b_tokens):.1f}%)")

    # What suffixes appear at line-final?
    def suffix_at_position(tokens, position_col, position_val):
        filtered = [t for t in tokens if t.get(position_col) == position_val]
        suffixes = Counter()
        for t in filtered:
            word = t['word'].lower()
            for suffix in ['aiin', 'edy', 'eey', 'dy', 'ey', 'hy', 'ar', 'or', 'al', 'ol', 'y', 'r']:
                if word.endswith(suffix):
                    suffixes[suffix] += 1
                    break
        return suffixes

    print(f"\n--- Suffixes at line-final (A) ---")
    a_final_suffixes = suffix_at_position(a_tokens, 'line_final', 1)
    for s, c in a_final_suffixes.most_common(10):
        print(f"  -{s}: {c}")

    print(f"\n--- Suffixes at line-final (B) ---")
    b_final_suffixes = suffix_at_position(b_tokens, 'line_final', 1)
    for s, c in b_final_suffixes.most_common(10):
        print(f"  -{s}: {c}")

def analyze_prefix_combinations(a_tokens, b_tokens):
    """Which prefix+suffix combinations differ most?"""
    print(f"\n{'='*60}")
    print(f"PREFIX+SUFFIX COMBINATION ANALYSIS")
    print(f"{'='*60}")

    prefixes = ['yt', 'yk', 'ych', 'yp', 'ys', 'yd', 'yo', 'yf', 'ykch']
    suffixes = ['edy', 'eey', 'dy', 'ey', 'aiin', 'ain', 'ar', 'or', 'ol', 'al', 'y', 'hy']

    def count_combinations(tokens):
        combos = Counter()
        for t in tokens:
            word = t['word'].lower()
            prefix_match = None
            suffix_match = None

            for p in sorted(prefixes, key=len, reverse=True):
                if word.startswith(p):
                    prefix_match = p
                    break

            for s in sorted(suffixes, key=len, reverse=True):
                if word.endswith(s):
                    suffix_match = s
                    break

            if prefix_match and suffix_match:
                combos[(prefix_match, suffix_match)] += 1

        return combos

    a_combos = count_combinations(a_tokens)
    b_combos = count_combinations(b_tokens)

    all_combos = set(a_combos.keys()) | set(b_combos.keys())

    print(f"\n{'Combination':<15} {'A count':>8} {'B count':>8} {'A %':>8} {'B %':>8} {'Ratio':>8}")
    print("-" * 60)

    results = []
    for combo in all_combos:
        a_count = a_combos.get(combo, 0)
        b_count = b_combos.get(combo, 0)
        a_pct = 100 * a_count / len(a_tokens) if a_tokens else 0
        b_pct = 100 * b_count / len(b_tokens) if b_tokens else 0
        ratio = (b_pct / a_pct) if a_pct > 0 else float('inf') if b_pct > 0 else 0
        results.append((combo, a_count, b_count, a_pct, b_pct, ratio))

    # Sort by absolute difference
    results.sort(key=lambda x: abs(x[3] - x[4]), reverse=True)

    for combo, a_count, b_count, a_pct, b_pct, ratio in results[:25]:
        prefix, suffix = combo
        ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "B-only"
        print(f"{prefix}+{suffix:<6} {a_count:>8} {b_count:>8} {a_pct:>7.1f}% {b_pct:>7.1f}% {ratio_str:>8}")

def detailed_shared_form_analysis(a_tokens, b_tokens):
    """Analyze the 96 shared forms in detail."""
    print(f"\n{'='*60}")
    print(f"DETAILED SHARED FORM ANALYSIS")
    print(f"{'='*60}")

    a_forms = Counter(t['word'] for t in a_tokens)
    b_forms = Counter(t['word'] for t in b_tokens)

    shared = set(a_forms.keys()) & set(b_forms.keys())

    # Categorize shared forms
    atoms = [f for f in shared if len(f) == 1]
    short = [f for f in shared if 2 <= len(f) <= 3]
    medium = [f for f in shared if 4 <= len(f) <= 5]
    long_forms = [f for f in shared if len(f) >= 6]

    print(f"\nShared form categories:")
    print(f"  Atoms (1 char): {len(atoms)} - {atoms}")
    print(f"  Short (2-3 chars): {len(short)} - {short}")
    print(f"  Medium (4-5 chars): {len(medium)}")
    print(f"  Long (6+ chars): {len(long_forms)}")

    # Are shared forms the most frequent?
    a_total = sum(a_forms.values())
    b_total = sum(b_forms.values())

    shared_a_count = sum(a_forms[f] for f in shared)
    shared_b_count = sum(b_forms[f] for f in shared)

    print(f"\n--- Frequency contribution of shared forms ---")
    print(f"Shared forms account for:")
    print(f"  A: {shared_a_count}/{a_total} = {100*shared_a_count/a_total:.1f}% of tokens")
    print(f"  B: {shared_b_count}/{b_total} = {100*shared_b_count/b_total:.1f}% of tokens")

    # What are the most frequent A-only forms?
    a_only = set(a_forms.keys()) - shared
    b_only = set(b_forms.keys()) - shared

    print(f"\n--- Most frequent A-only forms (top 15) ---")
    a_only_ranked = sorted([(f, a_forms[f]) for f in a_only], key=lambda x: -x[1])
    for form, count in a_only_ranked[:15]:
        print(f"  {form}: {count}")

    print(f"\n--- Most frequent B-only forms (top 15) ---")
    b_only_ranked = sorted([(f, b_forms[f]) for f in b_only], key=lambda x: -x[1])
    for form, count in b_only_ranked[:15]:
        print(f"  {form}: {count}")

def morpheme_substitution_test(a_tokens, b_tokens):
    """Test if A and B use different morphemes for same functional slots."""
    print(f"\n{'='*60}")
    print(f"MORPHEME SUBSTITUTION ANALYSIS")
    print(f"{'='*60}")

    # Group forms by prefix (ignoring suffix)
    def group_by_prefix(tokens):
        groups = defaultdict(Counter)
        for t in tokens:
            word = t['word'].lower()
            # Extract prefix
            for prefix in ['ykch', 'ych', 'yt', 'yk', 'yp', 'ys', 'yd', 'yo', 'yf', 'ya', 'y']:
                if word.startswith(prefix):
                    remainder = word[len(prefix):]
                    groups[prefix][remainder] += 1
                    break
        return groups

    a_groups = group_by_prefix(a_tokens)
    b_groups = group_by_prefix(b_tokens)

    print(f"\n--- What follows each prefix? ---")
    for prefix in ['yt', 'yk', 'ych', 'ys']:
        a_suffixes = a_groups.get(prefix, Counter())
        b_suffixes = b_groups.get(prefix, Counter())

        print(f"\n{prefix}- prefix:")
        print(f"  A most common: {a_suffixes.most_common(5)}")
        print(f"  B most common: {b_suffixes.most_common(5)}")

def main():
    data_path = Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt")
    print(f"Loading data...")
    df = load_data(data_path)

    a_tokens = extract_ht_with_context(df, 'A')
    b_tokens = extract_ht_with_context(df, 'B')

    print(f"Currier A HT tokens: {len(a_tokens)}")
    print(f"Currier B HT tokens: {len(b_tokens)}")

    # Detailed suffix analysis
    a_suffixes, a_suffix_tokens = analyze_suffix_distribution(a_tokens, "CURRIER A")
    b_suffixes, b_suffix_tokens = analyze_suffix_distribution(b_tokens, "CURRIER B")

    # -edy deep dive
    analyze_edy_phenomenon(a_tokens, b_tokens)

    # Positional analysis
    analyze_positional_differences(a_tokens, b_tokens)

    # Combination analysis
    analyze_prefix_combinations(a_tokens, b_tokens)

    # Shared form deep dive
    detailed_shared_form_analysis(a_tokens, b_tokens)

    # Morpheme substitution
    morpheme_substitution_test(a_tokens, b_tokens)

    # Summary
    print(f"\n{'#'*60}")
    print(f"# KEY DIVERGENCE SUMMARY")
    print(f"{'#'*60}")

    print(f"""
SUFFIX SIGNATURE DIFFERENCES:

A-ENRICHED (Registry-style):
- -or: {100*a_suffixes.get('or',0)/len(a_tokens):.1f}% vs {100*b_suffixes.get('or',0)/len(b_tokens):.1f}%
- -ol: {100*a_suffixes.get('ol',0)/len(a_tokens):.1f}% vs {100*b_suffixes.get('ol',0)/len(b_tokens):.1f}%
- -y (bare): {100*a_suffixes.get('y',0)/len(a_tokens):.1f}% vs {100*b_suffixes.get('y',0)/len(b_tokens):.1f}%
- -hy: {100*a_suffixes.get('hy',0)/len(a_tokens):.1f}% vs {100*b_suffixes.get('hy',0)/len(b_tokens):.1f}%

B-ENRICHED (Execution-style):
- -edy: {100*a_suffixes.get('edy',0)/len(a_tokens):.1f}% vs {100*b_suffixes.get('edy',0)/len(b_tokens):.1f}%
- -eey: {100*a_suffixes.get('eey',0)/len(a_tokens):.1f}% vs {100*b_suffixes.get('eey',0)/len(b_tokens):.1f}%
- -ar: {100*a_suffixes.get('ar',0)/len(a_tokens):.1f}% vs {100*b_suffixes.get('ar',0)/len(b_tokens):.1f}%

INTERPRETATION:
- A's simpler suffixes (-or, -ol, -y) suggest LABELING/INDEXING function
- B's complex suffixes (-edy, -eey) suggest PROCESS/STATE annotation
- The -edy suffix is nearly B-exclusive and may mark a specific procedural state
""")

if __name__ == "__main__":
    main()
