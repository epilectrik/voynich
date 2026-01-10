#!/usr/bin/env python3
"""
HT Training Hypothesis Analysis

HYPOTHESIS: Currier A is where scribes were trained, explaining higher HT rates.

Background:
- A has MORE HT (5.50%) than B (3.76%)
- A is structurally simpler (registry vs execution programs)
- If A is a training context, we'd expect specific patterns

HT tokens definition (per user):
- All tokens starting with 'y' OR
- Single-char atoms (y, f, d, r)

Analysis tasks:
1. COMPLEXITY GRADIENT - Do early A folios have higher HT than later?
2. ERROR/CORRECTION PATTERNS - Do high-HT lines show more variants?
3. SCRIBE VARIATION - Different A sections have different HT signatures?
4. REPETITION AS PRACTICE - HT higher or lower in repeated entries?
5. B EARLY FOLIOS - Do early B folios also have higher HT?
6. TOKEN DIVERSITY - Is HT-heavy A text lower in vocabulary diversity?
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import re
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Load data
DATA_PATH = "C:/git/voynich/data/transcriptions/interlinear_full_words.txt"

def load_data():
    """Load and preprocess the transcription data."""
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
    # Clean column names (remove quotes if present)
    df.columns = [c.strip('"') for c in df.columns]
    # Clean string columns
    for col in ['word', 'folio', 'language', 'section']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip('"')
    return df

def is_ht_token(token):
    """
    Determine if a token is HT (Human Track).
    HT = tokens starting with 'y' OR single-char atoms (y, f, d, r)
    """
    if pd.isna(token) or token in ['NA', 'nan', '']:
        return False
    token = str(token).strip().lower()
    if len(token) == 0:
        return False
    # Single-char atoms
    if token in ['y', 'f', 'd', 'r']:
        return True
    # Tokens starting with 'y'
    if token.startswith('y'):
        return True
    return False

def extract_folio_number(folio):
    """Extract numeric portion of folio for ordering."""
    if pd.isna(folio):
        return (0, 0, '')
    folio = str(folio)
    # Pattern: f followed by number, optionally followed by r/v
    match = re.match(r'f(\d+)([rv]?)', folio.lower())
    if match:
        num = int(match.group(1))
        side = match.group(2) or ''
        side_ord = 0 if side == 'r' else 1 if side == 'v' else 2
        return (num, side_ord, folio)
    return (9999, 0, folio)

def analyze():
    print("=" * 80)
    print("HT TRAINING HYPOTHESIS ANALYSIS")
    print("=" * 80)

    df = load_data()
    print(f"\nTotal records: {len(df):,}")
    print(f"Columns: {list(df.columns)}")

    # Basic language distribution
    print("\n" + "=" * 80)
    print("0. BASIC DISTRIBUTION")
    print("=" * 80)

    lang_counts = df['language'].value_counts()
    print("\nLanguage distribution:")
    print(lang_counts)

    # Filter to A and B only
    df_ab = df[df['language'].isin(['A', 'B'])].copy()
    print(f"\nFiltered to A/B: {len(df_ab):,} records")

    # Mark HT tokens
    df_ab['is_ht'] = df_ab['word'].apply(is_ht_token)

    # Calculate HT rates by language
    ht_by_lang = df_ab.groupby('language').agg(
        total=('word', 'count'),
        ht_count=('is_ht', 'sum')
    )
    ht_by_lang['ht_rate'] = ht_by_lang['ht_count'] / ht_by_lang['total'] * 100
    print("\nHT rates by Currier language:")
    print(ht_by_lang)

    # Get A and B subsets
    df_a = df_ab[df_ab['language'] == 'A'].copy()
    df_b = df_ab[df_ab['language'] == 'B'].copy()

    print(f"\nCurrier A tokens: {len(df_a):,}")
    print(f"Currier B tokens: {len(df_b):,}")

    # =========================================================================
    # 1. COMPLEXITY GRADIENT
    # =========================================================================
    print("\n" + "=" * 80)
    print("1. COMPLEXITY GRADIENT")
    print("   Question: Are early A folios higher in HT than later A folios?")
    print("=" * 80)

    # Get unique folios for A
    a_folios = df_a['folio'].unique()
    a_folios_sorted = sorted(a_folios, key=extract_folio_number)
    print(f"\nCurrier A folios (sorted): {len(a_folios_sorted)}")
    print(f"First 10: {a_folios_sorted[:10]}")
    print(f"Last 10: {a_folios_sorted[-10:]}")

    # Calculate HT rate per folio for A
    folio_ht_a = df_a.groupby('folio').agg(
        total=('word', 'count'),
        ht_count=('is_ht', 'sum')
    ).reset_index()
    folio_ht_a['ht_rate'] = folio_ht_a['ht_count'] / folio_ht_a['total'] * 100
    folio_ht_a['order'] = folio_ht_a['folio'].apply(lambda x: extract_folio_number(x)[0])
    folio_ht_a = folio_ht_a.sort_values('order')

    # Split into thirds
    n = len(folio_ht_a)
    third = n // 3
    early_a = folio_ht_a.head(third)
    middle_a = folio_ht_a.iloc[third:2*third]
    late_a = folio_ht_a.tail(n - 2*third)

    print(f"\nEarly A folios ({len(early_a)}): {list(early_a['folio'].head(5))}...")
    print(f"  Mean HT rate: {early_a['ht_rate'].mean():.2f}%")
    print(f"  Median HT rate: {early_a['ht_rate'].median():.2f}%")

    print(f"\nMiddle A folios ({len(middle_a)}): {list(middle_a['folio'].head(5))}...")
    print(f"  Mean HT rate: {middle_a['ht_rate'].mean():.2f}%")
    print(f"  Median HT rate: {middle_a['ht_rate'].median():.2f}%")

    print(f"\nLate A folios ({len(late_a)}): {list(late_a['folio'].head(5))}...")
    print(f"  Mean HT rate: {late_a['ht_rate'].mean():.2f}%")
    print(f"  Median HT rate: {late_a['ht_rate'].median():.2f}%")

    # Statistical test
    kruskal = stats.kruskal(early_a['ht_rate'], middle_a['ht_rate'], late_a['ht_rate'])
    print(f"\nKruskal-Wallis test (early vs middle vs late): H={kruskal.statistic:.2f}, p={kruskal.pvalue:.4f}")

    # Correlation with folio order
    spearman = stats.spearmanr(folio_ht_a['order'], folio_ht_a['ht_rate'])
    print(f"Spearman correlation (folio order vs HT rate): rho={spearman.correlation:.3f}, p={spearman.pvalue:.4f}")

    if spearman.correlation < 0 and spearman.pvalue < 0.05:
        print(">>> SUPPORTS training hypothesis: HT DECREASES through A (learning improvement)")
    elif spearman.correlation > 0 and spearman.pvalue < 0.05:
        print(">>> CONTRADICTS training hypothesis: HT INCREASES through A")
    else:
        print(">>> NO significant gradient detected")

    # =========================================================================
    # 2. ERROR/CORRECTION PATTERNS
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. ERROR/CORRECTION PATTERNS")
    print("   Question: Do high-HT lines show more variant forms or shorter entries?")
    print("=" * 80)

    # Calculate metrics per line
    line_stats_a = df_a.groupby(['folio', 'line_number']).agg(
        total=('word', 'count'),
        ht_count=('is_ht', 'sum'),
        unique_tokens=('word', 'nunique'),
        mean_length=('word', lambda x: x.str.len().mean())
    ).reset_index()
    line_stats_a['ht_rate'] = line_stats_a['ht_count'] / line_stats_a['total'] * 100

    # Correlate HT rate with line length
    spearman_length = stats.spearmanr(line_stats_a['ht_rate'], line_stats_a['total'])
    print(f"\nHT rate vs line length (tokens): rho={spearman_length.correlation:.3f}, p={spearman_length.pvalue:.4f}")

    # Correlate HT rate with token length
    spearman_tok_len = stats.spearmanr(line_stats_a['ht_rate'], line_stats_a['mean_length'])
    print(f"HT rate vs mean token length: rho={spearman_tok_len.correlation:.3f}, p={spearman_tok_len.pvalue:.4f}")

    # Variant analysis: calculate type-token ratio per line
    line_stats_a['ttr'] = line_stats_a['unique_tokens'] / line_stats_a['total']
    spearman_ttr = stats.spearmanr(line_stats_a['ht_rate'], line_stats_a['ttr'])
    print(f"HT rate vs TTR (diversity): rho={spearman_ttr.correlation:.3f}, p={spearman_ttr.pvalue:.4f}")

    # High HT vs low HT lines
    high_ht_lines = line_stats_a[line_stats_a['ht_rate'] >= line_stats_a['ht_rate'].quantile(0.75)]
    low_ht_lines = line_stats_a[line_stats_a['ht_rate'] <= line_stats_a['ht_rate'].quantile(0.25)]

    print(f"\nHigh-HT lines (top 25%): {len(high_ht_lines)}")
    print(f"  Mean line length: {high_ht_lines['total'].mean():.1f} tokens")
    print(f"  Mean token length: {high_ht_lines['mean_length'].mean():.1f} chars")
    print(f"  Mean TTR: {high_ht_lines['ttr'].mean():.3f}")

    print(f"\nLow-HT lines (bottom 25%): {len(low_ht_lines)}")
    print(f"  Mean line length: {low_ht_lines['total'].mean():.1f} tokens")
    print(f"  Mean token length: {low_ht_lines['mean_length'].mean():.1f} chars")
    print(f"  Mean TTR: {low_ht_lines['ttr'].mean():.3f}")

    # =========================================================================
    # 3. SCRIBE VARIATION
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. SCRIBE VARIATION")
    print("   Question: Do different A sections have different HT signatures?")
    print("=" * 80)

    section_ht = df_a.groupby('section').agg(
        total=('word', 'count'),
        ht_count=('is_ht', 'sum')
    ).reset_index()
    section_ht['ht_rate'] = section_ht['ht_count'] / section_ht['total'] * 100
    section_ht = section_ht.sort_values('ht_rate', ascending=False)

    print("\nHT rate by section in Currier A:")
    print(section_ht.to_string(index=False))

    # Chi-square test
    if len(section_ht) > 1:
        observed = section_ht['ht_count'].values
        expected_rate = section_ht['ht_count'].sum() / section_ht['total'].sum()
        expected = (section_ht['total'] * expected_rate).values
        chi2, p = stats.chisquare(observed, expected)
        print(f"\nChi-square test for section variation: chi2={chi2:.2f}, p={p:.4f}")
        if p < 0.05:
            print(">>> SUPPORTS scribe variation: Sections have DIFFERENT HT rates")

    # =========================================================================
    # 4. REPETITION AS PRACTICE
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. REPETITION AS PRACTICE")
    print("   Question: Is HT higher or lower in repeated entries?")
    print("   (C250: 64.1% of A entries have repeating blocks)")
    print("=" * 80)

    # Identify repeated tokens within lines
    def count_repetitions(group):
        tokens = group['word'].tolist()
        counter = Counter(tokens)
        repeated = sum(1 for t, c in counter.items() if c > 1)
        unique = len(counter)
        return pd.Series({
            'tokens': len(tokens),
            'unique': unique,
            'repeated_types': repeated,
            'repetition_ratio': (len(tokens) - unique) / len(tokens) if len(tokens) > 0 else 0,
            'ht_count': group['is_ht'].sum(),
            'ht_rate': group['is_ht'].mean() * 100
        })

    line_rep = df_a.groupby(['folio', 'line_number']).apply(count_repetitions).reset_index()

    # Correlation between repetition and HT
    spearman_rep = stats.spearmanr(line_rep['repetition_ratio'], line_rep['ht_rate'])
    print(f"\nRepetition ratio vs HT rate: rho={spearman_rep.correlation:.3f}, p={spearman_rep.pvalue:.4f}")

    # High vs low repetition lines
    high_rep = line_rep[line_rep['repetition_ratio'] >= line_rep['repetition_ratio'].quantile(0.75)]
    low_rep = line_rep[line_rep['repetition_ratio'] <= line_rep['repetition_ratio'].quantile(0.25)]

    print(f"\nHigh-repetition lines (top 25%): {len(high_rep)}")
    print(f"  Mean HT rate: {high_rep['ht_rate'].mean():.2f}%")

    print(f"\nLow-repetition lines (bottom 25%): {len(low_rep)}")
    print(f"  Mean HT rate: {low_rep['ht_rate'].mean():.2f}%")

    mwu = stats.mannwhitneyu(high_rep['ht_rate'], low_rep['ht_rate'], alternative='two-sided')
    print(f"\nMann-Whitney U test: U={mwu.statistic:.0f}, p={mwu.pvalue:.4f}")

    if high_rep['ht_rate'].mean() > low_rep['ht_rate'].mean() and mwu.pvalue < 0.05:
        print(">>> HT is HIGHER in repeated entries (consistent with practice)")
    elif high_rep['ht_rate'].mean() < low_rep['ht_rate'].mean() and mwu.pvalue < 0.05:
        print(">>> HT is LOWER in repeated entries (mastered material)")
    else:
        print(">>> NO significant difference")

    # =========================================================================
    # 5. COMPARISON WITH B EARLY FOLIOS
    # =========================================================================
    print("\n" + "=" * 80)
    print("5. COMPARISON WITH B EARLY FOLIOS")
    print("   Question: Do early B folios also have higher HT?")
    print("=" * 80)

    # Get unique folios for B
    b_folios = df_b['folio'].unique()
    b_folios_sorted = sorted(b_folios, key=extract_folio_number)
    print(f"\nCurrier B folios (sorted): {len(b_folios_sorted)}")
    print(f"First 10: {b_folios_sorted[:10]}")
    print(f"Last 10: {b_folios_sorted[-10:]}")

    # Calculate HT rate per folio for B
    folio_ht_b = df_b.groupby('folio').agg(
        total=('word', 'count'),
        ht_count=('is_ht', 'sum')
    ).reset_index()
    folio_ht_b['ht_rate'] = folio_ht_b['ht_count'] / folio_ht_b['total'] * 100
    folio_ht_b['order'] = folio_ht_b['folio'].apply(lambda x: extract_folio_number(x)[0])
    folio_ht_b = folio_ht_b.sort_values('order')

    # Split B into thirds
    n_b = len(folio_ht_b)
    third_b = n_b // 3
    early_b = folio_ht_b.head(third_b)
    middle_b = folio_ht_b.iloc[third_b:2*third_b]
    late_b = folio_ht_b.tail(n_b - 2*third_b)

    print(f"\nEarly B folios ({len(early_b)}): {list(early_b['folio'].head(5))}...")
    print(f"  Mean HT rate: {early_b['ht_rate'].mean():.2f}%")

    print(f"\nMiddle B folios ({len(middle_b)}): {list(middle_b['folio'].head(5))}...")
    print(f"  Mean HT rate: {middle_b['ht_rate'].mean():.2f}%")

    print(f"\nLate B folios ({len(late_b)}): {list(late_b['folio'].head(5))}...")
    print(f"  Mean HT rate: {late_b['ht_rate'].mean():.2f}%")

    # Correlation with folio order for B
    spearman_b = stats.spearmanr(folio_ht_b['order'], folio_ht_b['ht_rate'])
    print(f"\nSpearman correlation (B folio order vs HT rate): rho={spearman_b.correlation:.3f}, p={spearman_b.pvalue:.4f}")

    # Compare A vs B gradient
    print("\n--- Gradient Comparison ---")
    print(f"A gradient: rho={spearman.correlation:.3f}, p={spearman.pvalue:.4f}")
    print(f"B gradient: rho={spearman_b.correlation:.3f}, p={spearman_b.pvalue:.4f}")

    # =========================================================================
    # 6. TOKEN DIVERSITY
    # =========================================================================
    print("\n" + "=" * 80)
    print("6. TOKEN DIVERSITY")
    print("   Question: Is HT-heavy A text lower in vocabulary diversity?")
    print("=" * 80)

    # Calculate TTR per folio
    folio_diversity = df_a.groupby('folio').agg(
        total=('word', 'count'),
        unique=('word', 'nunique'),
        ht_count=('is_ht', 'sum')
    ).reset_index()
    folio_diversity['ttr'] = folio_diversity['unique'] / folio_diversity['total']
    folio_diversity['ht_rate'] = folio_diversity['ht_count'] / folio_diversity['total'] * 100

    # Correlation between HT rate and TTR
    spearman_div = stats.spearmanr(folio_diversity['ht_rate'], folio_diversity['ttr'])
    print(f"\nHT rate vs TTR (vocabulary diversity): rho={spearman_div.correlation:.3f}, p={spearman_div.pvalue:.4f}")

    # Compare A vs B diversity overall
    a_tokens = df_a['word'].dropna().tolist()
    b_tokens = df_b['word'].dropna().tolist()

    a_ttr = len(set(a_tokens)) / len(a_tokens)
    b_ttr = len(set(b_tokens)) / len(b_tokens)

    print(f"\nOverall TTR:")
    print(f"  Currier A: {a_ttr:.4f} ({len(set(a_tokens)):,} types / {len(a_tokens):,} tokens)")
    print(f"  Currier B: {b_ttr:.4f} ({len(set(b_tokens)):,} types / {len(b_tokens):,} tokens)")

    # HT-specific analysis
    a_ht_tokens = df_a[df_a['is_ht']]['word'].tolist()
    b_ht_tokens = df_b[df_b['is_ht']]['word'].tolist()

    if len(a_ht_tokens) > 0 and len(b_ht_tokens) > 0:
        a_ht_ttr = len(set(a_ht_tokens)) / len(a_ht_tokens)
        b_ht_ttr = len(set(b_ht_tokens)) / len(b_ht_tokens)

        print(f"\nHT-only TTR:")
        print(f"  Currier A HT: {a_ht_ttr:.4f} ({len(set(a_ht_tokens)):,} types / {len(a_ht_tokens):,} tokens)")
        print(f"  Currier B HT: {b_ht_ttr:.4f} ({len(set(b_ht_tokens)):,} types / {len(b_ht_tokens):,} tokens)")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY: TRAINING HYPOTHESIS ASSESSMENT")
    print("=" * 80)

    print("\nPREDICTIONS IF A IS TRAINING CONTEXT:")
    print("1. Early A should have HIGHER HT than late A (learning curve)")
    print("2. High-HT lines should be simpler (practice on easy material)")
    print("3. Different sections = different skill levels")
    print("4. Repeated entries show practice pattern")
    print("5. B should NOT show same gradient (production context)")
    print("6. HT-heavy text should have lower diversity (limited practice set)")

    print("\n" + "-" * 80)
    print("FINDINGS:")
    print("-" * 80)

    findings = []

    # 1. Gradient
    if spearman.correlation < -0.1 and spearman.pvalue < 0.05:
        findings.append("1. SUPPORTS: HT decreases through A (learning improvement)")
    elif spearman.correlation > 0.1 and spearman.pvalue < 0.05:
        findings.append("1. CONTRADICTS: HT increases through A")
    else:
        findings.append(f"1. NEUTRAL: No significant gradient (rho={spearman.correlation:.3f}, p={spearman.pvalue:.3f})")

    # 2. Simplicity
    if spearman_length.correlation < -0.1 and spearman_length.pvalue < 0.05:
        findings.append("2. SUPPORTS: High-HT lines are shorter (simpler)")
    elif spearman_length.correlation > 0.1 and spearman_length.pvalue < 0.05:
        findings.append("2. CONTRADICTS: High-HT lines are longer")
    else:
        findings.append(f"2. NEUTRAL: No significant length pattern (rho={spearman_length.correlation:.3f})")

    # 3. Section variation
    if p < 0.05:
        findings.append("3. SUPPORTS: Sections have different HT rates (different scribes/skills)")
    else:
        findings.append("3. NEUTRAL: No significant section variation")

    # 4. Repetition
    if spearman_rep.correlation > 0.1 and spearman_rep.pvalue < 0.05:
        findings.append("4. SUPPORTS: HT correlates with repetition (practice pattern)")
    elif spearman_rep.correlation < -0.1 and spearman_rep.pvalue < 0.05:
        findings.append("4. MIXED: HT inversely correlates with repetition (mastery)")
    else:
        findings.append(f"4. NEUTRAL: No repetition-HT pattern (rho={spearman_rep.correlation:.3f})")

    # 5. B comparison
    if abs(spearman_b.correlation) < abs(spearman.correlation) and spearman.pvalue < 0.05:
        findings.append("5. SUPPORTS: B lacks the gradient A shows")
    elif spearman_b.pvalue < 0.05:
        findings.append(f"5. CONTRADICTS: B also shows gradient (rho={spearman_b.correlation:.3f})")
    else:
        findings.append("5. NEUTRAL: Neither shows clear gradient")

    # 6. Diversity
    if spearman_div.correlation < -0.1 and spearman_div.pvalue < 0.05:
        findings.append("6. SUPPORTS: HT-heavy folios have lower diversity")
    elif spearman_div.correlation > 0.1 and spearman_div.pvalue < 0.05:
        findings.append("6. CONTRADICTS: HT-heavy folios have higher diversity")
    else:
        findings.append(f"6. NEUTRAL: No diversity pattern (rho={spearman_div.correlation:.3f})")

    for f in findings:
        print(f)

    support = sum(1 for f in findings if "SUPPORTS" in f)
    contradict = sum(1 for f in findings if "CONTRADICTS" in f)
    neutral = sum(1 for f in findings if "NEUTRAL" in f)

    print(f"\n{'=' * 80}")
    print(f"VERDICT: {support}/6 SUPPORT, {contradict}/6 CONTRADICT, {neutral}/6 NEUTRAL")
    print("=" * 80)

    if support >= 4:
        print("\n>>> HYPOTHESIS SUPPORTED: Evidence consistent with A as training context")
    elif contradict >= 3:
        print("\n>>> HYPOTHESIS CONTRADICTED: Evidence inconsistent with training interpretation")
    else:
        print("\n>>> HYPOTHESIS INCONCLUSIVE: Mixed evidence, requires further investigation")

if __name__ == "__main__":
    analyze()
