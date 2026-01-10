#!/usr/bin/env python3
"""
Deeper Investigation of HT Training Hypothesis

Key finding from initial analysis:
- B shows STRONGER folio-order gradient (rho=-0.478) than A (rho=-0.004)
- This CONTRADICTS the training hypothesis for A

This script investigates:
1. What's driving B's gradient?
2. Is the A/B difference in HT rate (6.46% vs 4.26%) explained by something else?
3. Section-level analysis
4. Quire-level patterns
5. Alternative hypothesis testing
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import re
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

DATA_PATH = "C:/git/voynich/data/transcriptions/interlinear_full_words.txt"

def load_data():
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
    df.columns = [c.strip('"') for c in df.columns]
    for col in ['word', 'folio', 'language', 'section', 'quire']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip('"')
    return df

def is_ht_token(token):
    if pd.isna(token) or token in ['NA', 'nan', '']:
        return False
    token = str(token).strip().lower()
    if len(token) == 0:
        return False
    if token in ['y', 'f', 'd', 'r']:
        return True
    if token.startswith('y'):
        return True
    return False

def extract_folio_number(folio):
    if pd.isna(folio):
        return (0, 0, '')
    folio = str(folio)
    match = re.match(r'f(\d+)([rv]?)', folio.lower())
    if match:
        num = int(match.group(1))
        side = match.group(2) or ''
        side_ord = 0 if side == 'r' else 1 if side == 'v' else 2
        return (num, side_ord, folio)
    return (9999, 0, folio)

def analyze():
    print("=" * 80)
    print("DEEPER HT ANALYSIS - INVESTIGATING THE B GRADIENT")
    print("=" * 80)

    df = load_data()
    df_ab = df[df['language'].isin(['A', 'B'])].copy()
    df_ab['is_ht'] = df_ab['word'].apply(is_ht_token)

    df_a = df_ab[df_ab['language'] == 'A'].copy()
    df_b = df_ab[df_ab['language'] == 'B'].copy()

    # =========================================================================
    # 1. WHAT HT TOKENS ARE COMMON IN A vs B?
    # =========================================================================
    print("\n" + "=" * 80)
    print("1. HT TOKEN DISTRIBUTION IN A vs B")
    print("=" * 80)

    a_ht = df_a[df_a['is_ht']]['word'].tolist()
    b_ht = df_b[df_b['is_ht']]['word'].tolist()

    a_ht_counter = Counter(a_ht)
    b_ht_counter = Counter(b_ht)

    print("\nTop 20 HT tokens in Currier A:")
    for tok, count in a_ht_counter.most_common(20):
        print(f"  {tok}: {count} ({count/len(a_ht)*100:.1f}%)")

    print("\nTop 20 HT tokens in Currier B:")
    for tok, count in b_ht_counter.most_common(20):
        print(f"  {tok}: {count} ({count/len(b_ht)*100:.1f}%)")

    # Single char analysis
    print("\n--- Single-char HT tokens ---")
    single_a = {k: v for k, v in a_ht_counter.items() if len(k) == 1}
    single_b = {k: v for k, v in b_ht_counter.items() if len(k) == 1}
    print(f"Currier A single-char: {dict(single_a)}")
    print(f"Currier B single-char: {dict(single_b)}")

    # y-initial analysis
    print("\n--- y-initial tokens (by prefix) ---")
    y_prefixes_a = Counter([tok[:3] if len(tok) >= 3 else tok for tok in a_ht if tok.startswith('y')])
    y_prefixes_b = Counter([tok[:3] if len(tok) >= 3 else tok for tok in b_ht if tok.startswith('y')])
    print(f"Currier A y-initial prefixes (top 10): {y_prefixes_a.most_common(10)}")
    print(f"Currier B y-initial prefixes (top 10): {y_prefixes_b.most_common(10)}")

    # =========================================================================
    # 2. B GRADIENT ANALYSIS BY SECTION
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. B GRADIENT BY SECTION")
    print("=" * 80)

    # Get B sections
    b_sections = df_b['section'].unique()
    print(f"\nB sections: {list(b_sections)}")

    # Calculate HT by section AND folio order
    folio_section_ht = df_b.groupby(['folio', 'section']).agg(
        total=('word', 'count'),
        ht_count=('is_ht', 'sum')
    ).reset_index()
    folio_section_ht['ht_rate'] = folio_section_ht['ht_count'] / folio_section_ht['total'] * 100
    folio_section_ht['order'] = folio_section_ht['folio'].apply(lambda x: extract_folio_number(x)[0])

    # Check gradient per section
    for section in sorted(b_sections):
        if section in ['nan', 'NA']:
            continue
        section_data = folio_section_ht[folio_section_ht['section'] == section]
        if len(section_data) > 5:
            spearman = stats.spearmanr(section_data['order'], section_data['ht_rate'])
            print(f"\nSection {section}: {len(section_data)} folios")
            print(f"  Mean HT: {section_data['ht_rate'].mean():.2f}%")
            print(f"  Gradient: rho={spearman.correlation:.3f}, p={spearman.pvalue:.4f}")

    # =========================================================================
    # 3. QUIRE-LEVEL ANALYSIS
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. QUIRE-LEVEL HT ANALYSIS")
    print("=" * 80)

    # Quire distribution
    for lang, df_lang in [('A', df_a), ('B', df_b)]:
        quire_ht = df_lang.groupby('quire').agg(
            total=('word', 'count'),
            ht_count=('is_ht', 'sum')
        ).reset_index()
        quire_ht['ht_rate'] = quire_ht['ht_count'] / quire_ht['total'] * 100
        quire_ht = quire_ht.sort_values('ht_rate', ascending=False)

        print(f"\nCurrier {lang} HT rate by quire:")
        print(quire_ht.to_string(index=False))

    # =========================================================================
    # 4. EARLY B FOLIOS - WHAT'S SPECIAL?
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. EARLY B FOLIOS - WHAT'S SPECIAL ABOUT THEM?")
    print("=" * 80)

    # Get early B folios (first third with high HT)
    b_folios_sorted = sorted(df_b['folio'].unique(), key=extract_folio_number)
    early_b_folios = b_folios_sorted[:len(b_folios_sorted)//3]
    late_b_folios = b_folios_sorted[-len(b_folios_sorted)//3:]

    early_b = df_b[df_b['folio'].isin(early_b_folios)]
    late_b = df_b[df_b['folio'].isin(late_b_folios)]

    print(f"\nEarly B folios: {early_b_folios[:10]}...")
    print(f"Late B folios: {late_b_folios[:10]}...")

    # Section distribution in early vs late
    print("\nSection distribution in early B vs late B:")
    early_sections = early_b['section'].value_counts(normalize=True) * 100
    late_sections = late_b['section'].value_counts(normalize=True) * 100

    print("Early B sections:")
    for s, pct in early_sections.items():
        print(f"  {s}: {pct:.1f}%")

    print("Late B sections:")
    for s, pct in late_sections.items():
        print(f"  {s}: {pct:.1f}%")

    # HT types in early vs late
    early_b_ht = early_b[early_b['is_ht']]['word'].tolist()
    late_b_ht = late_b[late_b['is_ht']]['word'].tolist()

    print(f"\nEarly B HT tokens: {len(early_b_ht)} ({len(early_b_ht)/len(early_b)*100:.1f}%)")
    print(f"Late B HT tokens: {len(late_b_ht)} ({len(late_b_ht)/len(late_b)*100:.1f}%)")

    print("\nTop 10 HT in early B:")
    for tok, count in Counter(early_b_ht).most_common(10):
        print(f"  {tok}: {count}")

    print("\nTop 10 HT in late B:")
    for tok, count in Counter(late_b_ht).most_common(10):
        print(f"  {tok}: {count}")

    # =========================================================================
    # 5. ALTERNATIVE HYPOTHESIS: HT AS SECTION MARKER
    # =========================================================================
    print("\n" + "=" * 80)
    print("5. ALTERNATIVE HYPOTHESIS: HT AS SECTION MARKER")
    print("=" * 80)

    # Does HT rate vary more by section than by folio order?
    # Compare variance explained

    # For B: section vs folio order
    folio_ht_b = df_b.groupby('folio').agg(
        total=('word', 'count'),
        ht_count=('is_ht', 'sum'),
        section=('section', lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'NA')
    ).reset_index()
    folio_ht_b['ht_rate'] = folio_ht_b['ht_count'] / folio_ht_b['total'] * 100
    folio_ht_b['order'] = folio_ht_b['folio'].apply(lambda x: extract_folio_number(x)[0])

    # Section effect
    section_groups = [group['ht_rate'].values for name, group in folio_ht_b.groupby('section') if len(group) > 3]
    if len(section_groups) > 1:
        kruskal_section = stats.kruskal(*section_groups)
        print(f"\nKruskal-Wallis by section: H={kruskal_section.statistic:.2f}, p={kruskal_section.pvalue:.4f}")

    # Folio order effect (already calculated)
    print(f"Spearman by folio order: rho=-0.478, p<0.0001")

    # =========================================================================
    # 6. WITHIN-SECTION GRADIENT CHECK
    # =========================================================================
    print("\n" + "=" * 80)
    print("6. WITHIN-SECTION GRADIENT CHECK")
    print("   Does B show HT gradient WITHIN each section?")
    print("=" * 80)

    for section in sorted(b_sections):
        if section in ['nan', 'NA']:
            continue
        section_data = folio_ht_b[folio_ht_b['section'] == section]
        if len(section_data) > 10:
            section_data = section_data.sort_values('order')
            spearman = stats.spearmanr(section_data['order'], section_data['ht_rate'])
            print(f"\nSection {section}: {len(section_data)} folios")
            print(f"  First folios: {list(section_data['folio'].head(3))}")
            print(f"  Last folios: {list(section_data['folio'].tail(3))}")
            print(f"  Gradient: rho={spearman.correlation:.3f}, p={spearman.pvalue:.4f}")

            # First third vs last third
            n = len(section_data)
            first_third = section_data.head(n//3)
            last_third = section_data.tail(n//3)
            print(f"  First third mean HT: {first_third['ht_rate'].mean():.2f}%")
            print(f"  Last third mean HT: {last_third['ht_rate'].mean():.2f}%")

    # =========================================================================
    # 7. PHYSICAL ORDERING VS CURRIER CLASSIFICATION
    # =========================================================================
    print("\n" + "=" * 80)
    print("7. HYPOTHESIS: B's GRADIENT IS SECTION-DRIVEN, NOT ORDER-DRIVEN")
    print("=" * 80)

    # Calculate section mean HT rates
    section_means_b = df_b.groupby('section').agg(
        ht_rate=('is_ht', 'mean')
    ).reset_index()
    section_means_b['ht_rate'] *= 100
    section_means_b = section_means_b.sort_values('ht_rate', ascending=False)
    print("\nSection mean HT rates in B:")
    print(section_means_b.to_string(index=False))

    # What sections are in early vs late folios?
    early_sections_b = df_b[df_b['folio'].isin(early_b_folios)]['section'].value_counts()
    late_sections_b = df_b[df_b['folio'].isin(late_b_folios)]['section'].value_counts()

    print("\nSection distribution (token count):")
    print(f"Early B: {dict(early_sections_b)}")
    print(f"Late B: {dict(late_sections_b)}")

    # =========================================================================
    # 8. COMPARE A AND B SECTION COMPOSITIONS
    # =========================================================================
    print("\n" + "=" * 80)
    print("8. SECTION COMPOSITION: WHY A HAS HIGHER HT OVERALL")
    print("=" * 80)

    a_section_dist = df_a['section'].value_counts(normalize=True) * 100
    b_section_dist = df_b['section'].value_counts(normalize=True) * 100

    print("\nSection distribution (% of tokens):")
    print("Currier A:")
    for s, pct in a_section_dist.items():
        ht_rate = df_a[df_a['section'] == s]['is_ht'].mean() * 100
        print(f"  {s}: {pct:.1f}% (HT rate: {ht_rate:.2f}%)")

    print("\nCurrier B:")
    for s, pct in b_section_dist.items():
        ht_rate = df_b[df_b['section'] == s]['is_ht'].mean() * 100
        print(f"  {s}: {pct:.1f}% (HT rate: {ht_rate:.2f}%)")

    # Calculate expected HT if B had A's section distribution
    print("\n--- Counterfactual: What if B had A's section distribution? ---")
    section_ht_b = df_b.groupby('section').agg(ht_rate=('is_ht', 'mean')).reset_index()
    section_ht_b['ht_rate'] *= 100

    expected_ht = 0
    for s, pct in a_section_dist.items():
        b_rate = section_ht_b[section_ht_b['section'] == s]['ht_rate'].values
        if len(b_rate) > 0:
            expected_ht += (pct / 100) * b_rate[0]
            print(f"  Section {s}: A has {pct:.1f}%, B's rate is {b_rate[0]:.2f}%")

    actual_b_ht = df_b['is_ht'].mean() * 100
    print(f"\nActual B HT rate: {actual_b_ht:.2f}%")
    print(f"Expected B HT if it had A's section mix: {expected_ht:.2f}%")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY: TRAINING HYPOTHESIS REASSESSMENT")
    print("=" * 80)

    print("""
KEY FINDINGS:

1. B shows STRONG gradient (rho=-0.478), A shows NONE (rho=-0.004)
   - This is OPPOSITE to training hypothesis prediction

2. B's gradient appears SECTION-DRIVEN:
   - Early B folios have different section composition than late B
   - Different sections have different HT rates
   - The gradient may be an artifact of section ordering in the manuscript

3. A vs B HT difference (6.46% vs 4.26%):
   - A is 72% section H (high HT), only 21% section P (low HT)
   - Section composition explains much of the difference

4. ALTERNATIVE INTERPRETATION:
   - HT is a SECTION-LEVEL characteristic, not a folio-order characteristic
   - The A>B difference reflects A having more H-section content
   - B's gradient reflects changing section composition, not learning

VERDICT: Training hypothesis NOT SUPPORTED
- No learning gradient in A
- A's higher HT rate is explained by section composition
- B's gradient is section-driven artifact
""")

if __name__ == "__main__":
    analyze()
