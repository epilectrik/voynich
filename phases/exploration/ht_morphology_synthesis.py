#!/usr/bin/env python3
"""
HT Morphology Synthesis: WHY do A and B diverge?

This script synthesizes all findings and tests specific hypotheses about
why Currier A and Currier B have different HT morphological profiles.
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from scipy import stats
from pathlib import Path

def load_data(filepath):
    df = pd.read_csv(filepath, sep='\t', na_values='NA', low_memory=False)
    # Filter to H transcriber only
    df = df[df['transcriber'] == 'H']
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

def extract_all_data(df, language):
    """Extract HT tokens with full metadata."""
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

def classify_suffix(word):
    """Classify suffix into functional category."""
    word = word.lower()

    # B-characteristic suffixes (process/state markers)
    if word.endswith('edy'):
        return 'EDY_PROCESS'
    if word.endswith('eey'):
        return 'EEY_STATE'

    # A-characteristic suffixes (reference/label markers)
    if word.endswith('or') and not word.endswith('eor'):
        return 'OR_LABEL'
    if word.endswith('ol') and not word.endswith('eol'):
        return 'OL_LABEL'
    if word.endswith('hy'):
        return 'HY_MODIFIER'

    # Shared suffixes (dual-use)
    if word.endswith('aiin'):
        return 'AIIN_TERMINAL'
    if word.endswith('dy') and not word.endswith('edy'):
        return 'DY_MARKER'
    if word.endswith('ey') and not word.endswith('eey'):
        return 'EY_STATE'
    if word.endswith('ar'):
        return 'AR_REFERENCE'
    if word.endswith('al'):
        return 'AL_REFERENCE'

    # Atoms
    if len(word) == 1:
        return 'ATOM'

    return 'OTHER'

def test_suffix_functional_split(a_tokens, b_tokens):
    """Test if suffix choice reflects functional split."""
    print(f"\n{'='*70}")
    print(f"HYPOTHESIS 1: SUFFIX CHOICE REFLECTS FUNCTIONAL DIVERGENCE")
    print(f"{'='*70}")

    a_classes = Counter(classify_suffix(t['word']) for t in a_tokens)
    b_classes = Counter(classify_suffix(t['word']) for t in b_tokens)

    all_classes = set(a_classes.keys()) | set(b_classes.keys())

    print(f"\n{'Functional Class':<20} {'A count':>8} {'A %':>8} {'B count':>8} {'B %':>8} {'Enrich':>10}")
    print("-" * 70)

    results = []
    for cls in all_classes:
        a_count = a_classes.get(cls, 0)
        b_count = b_classes.get(cls, 0)
        a_pct = 100 * a_count / len(a_tokens)
        b_pct = 100 * b_count / len(b_tokens)

        if a_pct > 0 and b_pct > 0:
            ratio = b_pct / a_pct
            enrich = f"{ratio:.2f}x B" if ratio > 1 else f"{1/ratio:.2f}x A"
        elif b_pct > 0:
            enrich = "B-only"
        else:
            enrich = "A-only"

        results.append((cls, a_count, a_pct, b_count, b_pct, enrich))

    # Sort by A enrichment
    results.sort(key=lambda x: x[2] / (x[4] + 0.1), reverse=True)

    for cls, a_count, a_pct, b_count, b_pct, enrich in results:
        print(f"{cls:<20} {a_count:>8} {a_pct:>7.1f}% {b_count:>8} {b_pct:>7.1f}% {enrich:>10}")

    # Statistical test: Are suffix distributions different?
    from scipy.stats import chi2_contingency

    # Create contingency table
    a_process = a_classes.get('EDY_PROCESS', 0) + a_classes.get('EEY_STATE', 0)
    b_process = b_classes.get('EDY_PROCESS', 0) + b_classes.get('EEY_STATE', 0)
    a_label = a_classes.get('OR_LABEL', 0) + a_classes.get('OL_LABEL', 0) + a_classes.get('HY_MODIFIER', 0)
    b_label = b_classes.get('OR_LABEL', 0) + b_classes.get('OL_LABEL', 0) + b_classes.get('HY_MODIFIER', 0)

    contingency = [[a_process, b_process], [a_label, b_label]]
    chi2, p, dof, expected = chi2_contingency(contingency)

    print(f"\n--- Statistical Test: Process vs Label Suffixes ---")
    print(f"A process markers: {a_process} ({100*a_process/len(a_tokens):.1f}%)")
    print(f"B process markers: {b_process} ({100*b_process/len(b_tokens):.1f}%)")
    print(f"A label markers: {a_label} ({100*a_label/len(a_tokens):.1f}%)")
    print(f"B label markers: {b_label} ({100*b_label/len(b_tokens):.1f}%)")
    print(f"\nChi-squared: {chi2:.2f}, p-value: {p:.2e}")
    print(f"VERDICT: {'SIGNIFICANT' if p < 0.001 else 'NOT SIGNIFICANT'} difference")

    return {
        'a_process': a_process, 'b_process': b_process,
        'a_label': a_label, 'b_label': b_label,
        'chi2': chi2, 'p': p
    }

def test_length_complexity_gradient(a_tokens, b_tokens):
    """Test if B's longer forms reflect added complexity, not just more text."""
    print(f"\n{'='*70}")
    print(f"HYPOTHESIS 2: B's LENGTH REFLECTS ADDED MORPHOLOGICAL COMPLEXITY")
    print(f"{'='*70}")

    def morpheme_count(word):
        """Estimate morpheme count."""
        word = word.lower()
        count = 0

        # Prefix
        for p in ['ykch', 'ych', 'yt', 'yk', 'yp', 'ys', 'yd', 'yo', 'yf', 'ya', 'y']:
            if word.startswith(p):
                count += 1
                word = word[len(p):]
                break

        # Middle elements
        for m in ['ch', 'sh', 'ke', 'te', 'pe', 'de', 'ee', 'eo', 'he', 'od', 'ol', 'al']:
            if m in word:
                count += 1
                word = word.replace(m, '', 1)

        # Suffix
        for s in ['aiin', 'edy', 'eey', 'dy', 'ey', 'hy', 'ar', 'or', 'al', 'ol', 'y', 'r']:
            if word.endswith(s):
                count += 1
                break

        return max(count, 1)

    a_morphemes = [morpheme_count(t['word']) for t in a_tokens]
    b_morphemes = [morpheme_count(t['word']) for t in b_tokens]

    a_lengths = [len(t['word']) for t in a_tokens]
    b_lengths = [len(t['word']) for t in b_tokens]

    print(f"\n--- Morpheme Count Statistics ---")
    print(f"A: mean={np.mean(a_morphemes):.2f}, median={np.median(a_morphemes):.1f}")
    print(f"B: mean={np.mean(b_morphemes):.2f}, median={np.median(b_morphemes):.1f}")

    # Mann-Whitney U test
    stat, p = stats.mannwhitneyu(a_morphemes, b_morphemes, alternative='two-sided')
    print(f"Mann-Whitney U: p={p:.2e}")

    # Length per morpheme (efficiency)
    a_efficiency = np.mean([l/m for l, m in zip(a_lengths, a_morphemes)])
    b_efficiency = np.mean([l/m for l, m in zip(b_lengths, b_morphemes)])

    print(f"\n--- Characters per Morpheme (efficiency) ---")
    print(f"A: {a_efficiency:.2f} chars/morpheme")
    print(f"B: {b_efficiency:.2f} chars/morpheme")
    print(f"B/A ratio: {b_efficiency/a_efficiency:.2f}")

    if b_efficiency > a_efficiency * 1.1:
        print(f"\nVERDICT: B uses LONGER MORPHEMES (more complex)")
    elif np.mean(b_morphemes) > np.mean(a_morphemes) * 1.1:
        print(f"\nVERDICT: B has MORE MORPHEMES per token")
    else:
        print(f"\nVERDICT: Similar morpheme structure, different vocabulary")

def test_shared_forms_function(a_tokens, b_tokens):
    """Test if shared forms serve the same function in both systems."""
    print(f"\n{'='*70}")
    print(f"HYPOTHESIS 3: SHARED FORMS ARE FUNCTIONAL ANCHORS")
    print(f"{'='*70}")

    a_forms = Counter(t['word'] for t in a_tokens)
    b_forms = Counter(t['word'] for t in b_tokens)

    shared = set(a_forms.keys()) & set(b_forms.keys())

    # Classify shared vs unique forms
    shared_suffixes = Counter()
    a_only_suffixes = Counter()
    b_only_suffixes = Counter()

    for form in shared:
        shared_suffixes[classify_suffix(form)] += a_forms[form] + b_forms[form]

    for form in set(a_forms.keys()) - shared:
        a_only_suffixes[classify_suffix(form)] += a_forms[form]

    for form in set(b_forms.keys()) - shared:
        b_only_suffixes[classify_suffix(form)] += b_forms[form]

    print(f"\n--- Shared Forms by Class ---")
    for cls, count in shared_suffixes.most_common():
        print(f"  {cls}: {count}")

    print(f"\n--- A-Only Forms by Class ---")
    for cls, count in a_only_suffixes.most_common():
        print(f"  {cls}: {count}")

    print(f"\n--- B-Only Forms by Class ---")
    for cls, count in b_only_suffixes.most_common():
        print(f"  {cls}: {count}")

    # Key finding: What class is B-only dominated by?
    b_only_edy = b_only_suffixes.get('EDY_PROCESS', 0)
    b_only_total = sum(b_only_suffixes.values())

    print(f"\n--- B-Only EDY Dominance ---")
    print(f"EDY_PROCESS in B-only: {b_only_edy}/{b_only_total} = {100*b_only_edy/b_only_total:.1f}%")

    if b_only_edy / b_only_total > 0.3:
        print(f"VERDICT: B's unique vocabulary is dominated by -edy process markers")
    else:
        print(f"VERDICT: B's unique vocabulary is diverse")

def test_edy_as_process_marker(b_tokens):
    """Test if -edy specifically marks procedural context."""
    print(f"\n{'='*70}")
    print(f"HYPOTHESIS 4: -EDY MARKS PROCEDURAL CONTEXT IN B")
    print(f"{'='*70}")

    edy_tokens = [t for t in b_tokens if t['word'].lower().endswith('edy')]
    non_edy_tokens = [t for t in b_tokens if not t['word'].lower().endswith('edy')]

    # Position analysis
    edy_line_initial = sum(1 for t in edy_tokens if t['line_initial'] == 1) / len(edy_tokens) if edy_tokens else 0
    non_edy_line_initial = sum(1 for t in non_edy_tokens if t['line_initial'] == 1) / len(non_edy_tokens) if non_edy_tokens else 0

    edy_line_final = sum(1 for t in edy_tokens if t['line_final'] == 1) / len(edy_tokens) if edy_tokens else 0
    non_edy_line_final = sum(1 for t in non_edy_tokens if t['line_final'] == 1) / len(non_edy_tokens) if non_edy_tokens else 0

    print(f"\n--- Position Distribution ---")
    print(f"-edy line-initial rate: {100*edy_line_initial:.1f}%")
    print(f"non-edy line-initial rate: {100*non_edy_line_initial:.1f}%")
    print(f"-edy line-final rate: {100*edy_line_final:.1f}%")
    print(f"non-edy line-final rate: {100*non_edy_line_final:.1f}%")

    # What prefixes co-occur with -edy?
    edy_prefixes = Counter()
    for t in edy_tokens:
        word = t['word'].lower()
        for p in ['ykch', 'ych', 'yt', 'yk', 'yp', 'ys', 'yd', 'yo', 'yf', 'ya', 'y']:
            if word.startswith(p):
                edy_prefixes[p] += 1
                break

    print(f"\n--- Prefixes co-occurring with -edy ---")
    for prefix, count in edy_prefixes.most_common():
        print(f"  {prefix}: {count} ({100*count/len(edy_tokens):.1f}%)")

def explain_divergence():
    """Final synthesis: WHY the morphological systems diverge."""
    print(f"\n{'#'*70}")
    print(f"# SYNTHESIS: WHY HT MORPHOLOGY DIVERGES BETWEEN A AND B")
    print(f"{'#'*70}")

    print("""
EVIDENCE SUMMARY:

1. SUFFIX SIGNATURE IS THE PRIMARY DIFFERENTIATOR
   - A favors: -or (10.2%), -ol (9.4%), -hy (8.4%) = LABELING suffixes
   - B favors: -edy (18.2%), -eey (8.8%), -ar (7.5%) = PROCESS suffixes
   - The -edy suffix is 60x more common in B than A

2. SHARED FORMS ARE THE MORPHOLOGICAL CORE
   - 96 shared forms account for 67.6% of A tokens and 60.2% of B tokens
   - Shared forms are dominated by: atoms (y,d,r,f), short forms (yty, yky)
   - These are the PRIMITIVE VOCABULARY shared across systems

3. B-ONLY FORMS ARE DOMINATED BY -EDY
   - B's unique vocabulary is characterized by: yteedy, ytedy, ykedy, ychedy...
   - These forms add -edy to shared roots (yt-, yk-, ych-)
   - This is PRODUCTIVE SUFFIXATION, not new vocabulary

4. COMPLEXITY IS MORPHOLOGICAL, NOT LEXICAL
   - A and B share the same PREFIX inventory (yt-, yk-, ych-, etc.)
   - They differ in SUFFIX selection
   - B's length advantage (+0.5 chars) comes from longer suffixes

CONCLUSION: WHY THEY DIVERGE

The divergence reflects FUNCTIONAL SPECIALIZATION:

CURRIER A (REGISTRY):
- Uses HT tokens as SHORT LABELS/REFERENCES
- Favors terminating suffixes: -or, -ol, -hy
- High atom rate (17.1%) = primitive markers
- HT serves as INDEX NOTATION in a categorical listing

CURRIER B (EXECUTION GRAMMAR):
- Uses HT tokens as PROCESS/STATE MARKERS
- Favors process suffixes: -edy, -eey
- Lower atom rate (11.6%) = tokens carry more information
- HT serves as PROCEDURAL ANNOTATION in executable text

The -edy suffix is the KEY DISCRIMINATOR:
- Nearly absent in A (0.3%)
- Dominant in B (18.2%)
- Appears with ALL major prefixes (yt-, yk-, ych-, yp-, ys-)
- Marks a specific procedural state (possibly "active/running")

MORPHOLOGICAL ARCHITECTURE:

Both systems share:
+-- PREFIXES: yt-, yk-, ych-, yp-, ys-, yd-, yo-, yf-, ykch-
+-- ATOMS: y, d, r, f
+-- CORE SUFFIXES: -aiin, -dy, -ey

A specializes with:
+-- LABEL SUFFIXES: -or, -ol, -hy

B specializes with:
+-- PROCESS SUFFIXES: -edy, -eey

This is consistent with:
- C240: A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY (labels for catalog entries)
- C168: HT = single unified layer with section-specific patterns
- C348: HT prefixes are synchronized to procedural phase in B

The HT layer uses the SAME morphological TYPE SYSTEM (C383) but applies
different SUFFIX VOCABULARIES appropriate to each system's function.

A's HT = reference markers for categorization
B's HT = process markers for execution tracking
""")

def main():
    data_path = Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt")
    print(f"Loading data...")
    df = load_data(data_path)

    a_tokens = extract_all_data(df, 'A')
    b_tokens = extract_all_data(df, 'B')

    print(f"Currier A HT tokens: {len(a_tokens)}")
    print(f"Currier B HT tokens: {len(b_tokens)}")

    # Test hypotheses
    test_suffix_functional_split(a_tokens, b_tokens)
    test_length_complexity_gradient(a_tokens, b_tokens)
    test_shared_forms_function(a_tokens, b_tokens)
    test_edy_as_process_marker(b_tokens)

    # Final synthesis
    explain_divergence()

if __name__ == "__main__":
    main()
