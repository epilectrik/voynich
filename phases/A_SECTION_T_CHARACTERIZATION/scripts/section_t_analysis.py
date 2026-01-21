#!/usr/bin/env python3
"""
A_SECTION_T_CHARACTERIZATION Phase

Test whether Section T's B-absence is explained by existing constraints (C498)
or represents a new structural phenomenon.

Tests:
1. Registry-internal fraction (C498 compliance)
2. AZC participation rate
3. Control operator inventory (C484)
4. PREFIX distribution (Fisher's exact)
5. Folio spread comparison
"""

import pandas as pd
import json
from pathlib import Path
from collections import Counter
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
RESULTS_PATH = PROJECT_ROOT / 'phases' / 'A_SECTION_T_CHARACTERIZATION' / 'results'

# Morphology parsing (from established codebase)
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta',
    'al', 'ar', 'or',
]
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

SUFFIXES = [
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy',
    'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey',
    'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey',
    'chol', 'shol', 'kol', 'tol',
    'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool',
    'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]

# Control operator prefixes (C484)
CONTROL_OP_PREFIXES = ['yd', 'so', 'ke', 'sa']

# AZC folios
AZC_FOLIOS = ['f67r1', 'f67r2', 'f67v1', 'f67v2', 'f68r1', 'f68r2', 'f68r3',
              'f68v1', 'f68v2', 'f68v3', 'f69r1', 'f69r2', 'f69v1', 'f69v2',
              'f70r1', 'f70r2', 'f70v1', 'f70v2', 'f71r', 'f71v', 'f72r1',
              'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v']

# Section T Currier-A folios
SECTION_T_A_FOLIOS = ['f1r', 'f58r', 'f58v']


def extract_morphology(token):
    """Extract PREFIX, MIDDLE, SUFFIX from token."""
    if pd.isna(token):
        return None, None, None
    token = str(token)

    # Find prefix
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break

    if not prefix:
        return None, None, None

    remainder = token[len(prefix):]

    # Find suffix
    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break

    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder

    if middle == '':
        middle = '_EMPTY_'

    return prefix, middle, suffix


def main():
    print("=" * 70)
    print("A_SECTION_T_CHARACTERIZATION")
    print("=" * 70)
    print()

    # Load data
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H'].copy()  # PRIMARY track only

    # Parse morphology
    df[['prefix', 'middle', 'suffix']] = df['word'].apply(
        lambda x: pd.Series(extract_morphology(x))
    )

    # Identify corpora
    df_a = df[df['language'] == 'A'].copy()
    df_b = df[df['language'] == 'B'].copy()
    df_azc = df[df['folio'].isin(AZC_FOLIOS)].copy()

    # Section T (Currier A only)
    df_t = df_a[df_a['folio'].isin(SECTION_T_A_FOLIOS)].copy()

    # Section H and P for comparison
    df_h = df_a[df_a['section'] == 'H'].copy()
    df_p = df_a[df_a['section'] == 'P'].copy()

    print("=== DATA SUMMARY ===")
    print(f"Total A tokens: {len(df_a):,}")
    print(f"Section T (A only) tokens: {len(df_t):,} ({len(df_t)/len(df_a)*100:.1f}%)")
    print(f"Section T folios: {SECTION_T_A_FOLIOS}")
    print(f"Section H tokens: {len(df_h):,}")
    print(f"Section P tokens: {len(df_p):,}")
    print()

    # Get MIDDLE vocabularies
    t_middles = set(df_t['middle'].dropna().unique())
    a_middles = set(df_a['middle'].dropna().unique())
    b_middles = set(df_b['middle'].dropna().unique())
    azc_middles = set(df_azc['middle'].dropna().unique())
    h_middles = set(df_h['middle'].dropna().unique())
    p_middles = set(df_p['middle'].dropna().unique())

    print(f"Section T unique MIDDLEs: {len(t_middles)}")
    print(f"Section H unique MIDDLEs: {len(h_middles)}")
    print(f"Section P unique MIDDLEs: {len(p_middles)}")
    print()

    results = {
        'data_summary': {
            'section_t_tokens': len(df_t),
            'section_t_folios': SECTION_T_A_FOLIOS,
            'section_t_middles': len(t_middles),
            'section_h_tokens': len(df_h),
            'section_p_tokens': len(df_p),
        },
        'tests': {}
    }

    # =========================================================================
    # TEST 1: Registry-Internal Fraction
    # =========================================================================
    print("=" * 70)
    print("TEST 1: REGISTRY-INTERNAL FRACTION")
    print("=" * 70)
    print()

    # C498 criteria for registry-internal:
    # - A-exclusive (not in B)
    # - Folio-localized (appears in few folios)

    # Classify each MIDDLE
    def classify_middle(mid, df_source, b_middles, azc_middles):
        """Classify MIDDLE as RI or PP."""
        if mid in b_middles:
            if mid in azc_middles:
                return 'AZC-Mediated'
            else:
                return 'B-Native-Overlap'
        else:
            return 'Registry-Internal'

    t_classification = {}
    for mid in t_middles:
        t_classification[mid] = classify_middle(mid, df_t, b_middles, azc_middles)

    ri_count = sum(1 for c in t_classification.values() if c == 'Registry-Internal')
    azc_med_count = sum(1 for c in t_classification.values() if c == 'AZC-Mediated')
    bn_count = sum(1 for c in t_classification.values() if c == 'B-Native-Overlap')

    print("Section T MIDDLE Classification:")
    print(f"  Registry-Internal (RI): {ri_count} ({ri_count/len(t_middles)*100:.1f}%)")
    print(f"  AZC-Mediated: {azc_med_count} ({azc_med_count/len(t_middles)*100:.1f}%)")
    print(f"  B-Native-Overlap: {bn_count} ({bn_count/len(t_middles)*100:.1f}%)")
    print()

    # Compare to overall A baseline (C498: 56.6% RI)
    a_classification = {}
    for mid in a_middles:
        a_classification[mid] = classify_middle(mid, df_a, b_middles, azc_middles)

    a_ri_count = sum(1 for c in a_classification.values() if c == 'Registry-Internal')
    a_ri_pct = a_ri_count / len(a_middles) * 100
    t_ri_pct = ri_count / len(t_middles) * 100

    print(f"Baseline (all A): {a_ri_pct:.1f}% Registry-Internal")
    print(f"Section T: {t_ri_pct:.1f}% Registry-Internal")
    print(f"Enrichment: {t_ri_pct / a_ri_pct:.2f}x")
    print()

    # Fisher's exact test
    # Contingency: [T_RI, T_non-RI], [A_RI, A_non-RI]
    t_non_ri = len(t_middles) - ri_count
    a_non_ri = len(a_middles) - a_ri_count
    contingency = [[ri_count, t_non_ri], [a_ri_count, a_non_ri]]
    odds_ratio, p_value = stats.fisher_exact(contingency)

    print(f"Fisher's exact test (T vs A baseline):")
    print(f"  Odds ratio: {odds_ratio:.3f}")
    print(f"  p-value: {p_value:.4f}")

    test1_verdict = "ENRICHED" if t_ri_pct > a_ri_pct and p_value < 0.05 else "NOT ENRICHED"
    print(f"  Verdict: {test1_verdict}")
    print()

    results['tests']['test1_ri_fraction'] = {
        'section_t_ri_pct': t_ri_pct,
        'baseline_ri_pct': a_ri_pct,
        'enrichment': t_ri_pct / a_ri_pct if a_ri_pct > 0 else None,
        'odds_ratio': odds_ratio,
        'p_value': p_value,
        'verdict': test1_verdict,
        'classification': {
            'registry_internal': ri_count,
            'azc_mediated': azc_med_count,
            'b_native_overlap': bn_count,
        }
    }

    # =========================================================================
    # TEST 2: AZC Participation Rate
    # =========================================================================
    print("=" * 70)
    print("TEST 2: AZC PARTICIPATION RATE")
    print("=" * 70)
    print()

    t_in_azc = t_middles & azc_middles
    t_azc_rate = len(t_in_azc) / len(t_middles) * 100 if t_middles else 0

    # Baseline: what % of all A MIDDLEs appear in AZC?
    a_in_azc = a_middles & azc_middles
    a_azc_rate = len(a_in_azc) / len(a_middles) * 100 if a_middles else 0

    print(f"Section T MIDDLEs in AZC: {len(t_in_azc)} / {len(t_middles)} ({t_azc_rate:.1f}%)")
    print(f"Baseline (all A in AZC): {len(a_in_azc)} / {len(a_middles)} ({a_azc_rate:.1f}%)")
    print()

    if t_in_azc:
        print("Section T MIDDLEs appearing in AZC:")
        for mid in sorted(t_in_azc)[:20]:
            print(f"  {mid}")
        if len(t_in_azc) > 20:
            print(f"  ... and {len(t_in_azc) - 20} more")
    print()

    # Fisher's exact
    t_not_azc = len(t_middles) - len(t_in_azc)
    a_not_azc = len(a_middles) - len(a_in_azc)
    contingency2 = [[len(t_in_azc), t_not_azc], [len(a_in_azc), a_not_azc]]
    odds_ratio2, p_value2 = stats.fisher_exact(contingency2)

    print(f"Fisher's exact test (T vs A baseline):")
    print(f"  Odds ratio: {odds_ratio2:.3f}")
    print(f"  p-value: {p_value2:.4f}")

    test2_verdict = "REDUCED" if t_azc_rate < a_azc_rate and p_value2 < 0.05 else "NOT SIGNIFICANTLY DIFFERENT"
    print(f"  Verdict: {test2_verdict}")
    print()

    results['tests']['test2_azc_participation'] = {
        'section_t_azc_pct': t_azc_rate,
        'baseline_azc_pct': a_azc_rate,
        't_in_azc_count': len(t_in_azc),
        't_in_azc_list': sorted(list(t_in_azc))[:50],
        'odds_ratio': odds_ratio2,
        'p_value': p_value2,
        'verdict': test2_verdict,
    }

    # =========================================================================
    # TEST 3: Control Operator Inventory (C484)
    # =========================================================================
    print("=" * 70)
    print("TEST 3: CONTROL OPERATOR INVENTORY (C484)")
    print("=" * 70)
    print()

    # C484: Single-token entries with yd-/so-/ke-/sa- prefixes
    # Boundary-enriched (folio start/end)

    # Find single-token lines in Section T
    t_line_counts = df_t.groupby(['folio', 'line_number']).size()
    single_token_lines = t_line_counts[t_line_counts == 1].index.tolist()

    print(f"Single-token lines in Section T: {len(single_token_lines)}")

    # Check which have control operator prefixes
    control_ops = []
    for folio, line_num in single_token_lines:
        row = df_t[(df_t['folio'] == folio) & (df_t['line_number'] == line_num)].iloc[0]
        word = row['word']
        prefix = row['prefix']
        if prefix in CONTROL_OP_PREFIXES:
            control_ops.append({
                'folio': folio,
                'line': line_num,
                'word': word,
                'prefix': prefix,
            })

    print(f"Control operator candidates (yd-/so-/ke-/sa- prefix): {len(control_ops)}")
    print()

    if control_ops:
        print("Control operators found:")
        for op in control_ops:
            print(f"  {op['folio']} line {op['line']}: {op['word']} (prefix: {op['prefix']})")
    else:
        print("No control operators found in Section T.")
    print()

    # Check boundary positions
    for folio in SECTION_T_A_FOLIOS:
        folio_df = df_t[df_t['folio'] == folio]
        if len(folio_df) == 0:
            continue
        min_line = folio_df['line_number'].min()
        max_line = folio_df['line_number'].max()

        # Check first and last lines
        first_line = folio_df[folio_df['line_number'] == min_line]
        last_line = folio_df[folio_df['line_number'] == max_line]

        print(f"{folio}:")
        print(f"  First line ({min_line}): {len(first_line)} tokens - {list(first_line['word'].values)[:5]}")
        print(f"  Last line ({max_line}): {len(last_line)} tokens - {list(last_line['word'].values)[:5]}")
    print()

    results['tests']['test3_control_operators'] = {
        'single_token_lines': len(single_token_lines),
        'control_operators_found': len(control_ops),
        'control_operators': control_ops,
    }

    # =========================================================================
    # TEST 4: PREFIX Distribution
    # =========================================================================
    print("=" * 70)
    print("TEST 4: PREFIX DISTRIBUTION")
    print("=" * 70)
    print()

    # Get prefix distributions
    t_prefixes = df_t['prefix'].dropna().value_counts()
    h_prefixes = df_h['prefix'].dropna().value_counts()
    p_prefixes = df_p['prefix'].dropna().value_counts()
    hp_prefixes = pd.concat([df_h, df_p])['prefix'].dropna().value_counts()

    print("Section T PREFIX distribution:")
    for prefix, count in t_prefixes.items():
        pct = count / len(df_t[df_t['prefix'].notna()]) * 100
        print(f"  {prefix}: {count} ({pct:.1f}%)")
    print()

    # Test for ct-prefix enrichment (C498 marker)
    t_ct = t_prefixes.get('ct', 0)
    t_total = df_t['prefix'].notna().sum()
    hp_ct = hp_prefixes.get('ct', 0)
    hp_total = len(pd.concat([df_h, df_p])['prefix'].dropna())

    t_ct_pct = t_ct / t_total * 100 if t_total > 0 else 0
    hp_ct_pct = hp_ct / hp_total * 100 if hp_total > 0 else 0

    print(f"CT-prefix (C498 RI marker):")
    print(f"  Section T: {t_ct} / {t_total} ({t_ct_pct:.1f}%)")
    print(f"  Sections H+P: {hp_ct} / {hp_total} ({hp_ct_pct:.1f}%)")
    print()

    # Fisher's exact for ct enrichment
    contingency4 = [[t_ct, t_total - t_ct], [hp_ct, hp_total - hp_ct]]
    odds_ratio4, p_value4 = stats.fisher_exact(contingency4)

    print(f"Fisher's exact test (ct-prefix enrichment):")
    print(f"  Odds ratio: {odds_ratio4:.3f}")
    print(f"  p-value: {p_value4:.4f}")

    test4_verdict = "CT-ENRICHED" if t_ct_pct > hp_ct_pct and p_value4 < 0.05 else "NOT CT-ENRICHED"
    print(f"  Verdict: {test4_verdict}")
    print()

    results['tests']['test4_prefix_distribution'] = {
        'section_t_ct_pct': t_ct_pct,
        'baseline_ct_pct': hp_ct_pct,
        'odds_ratio': odds_ratio4,
        'p_value': p_value4,
        'verdict': test4_verdict,
        'section_t_prefixes': t_prefixes.to_dict(),
    }

    # =========================================================================
    # TEST 5: Folio Spread
    # =========================================================================
    print("=" * 70)
    print("TEST 5: FOLIO SPREAD")
    print("=" * 70)
    print()

    # C498 baselines: RI = 1.34 folios, PP = 7.96 folios

    # Calculate folio spread for each Section T MIDDLE
    t_folio_spreads = {}
    for mid in t_middles:
        folios = df_a[df_a['middle'] == mid]['folio'].nunique()
        t_folio_spreads[mid] = folios

    mean_spread = sum(t_folio_spreads.values()) / len(t_folio_spreads) if t_folio_spreads else 0

    print(f"Section T MIDDLE folio spread:")
    print(f"  Mean: {mean_spread:.2f} folios")
    print(f"  C498 RI baseline: 1.34 folios")
    print(f"  C498 PP baseline: 7.96 folios")
    print()

    # Distribution
    spread_dist = Counter(t_folio_spreads.values())
    print("Distribution:")
    for spread, count in sorted(spread_dist.items()):
        pct = count / len(t_folio_spreads) * 100
        print(f"  {spread} folios: {count} MIDDLEs ({pct:.1f}%)")
    print()

    # How many are highly localized (1-2 folios)?
    localized = sum(1 for s in t_folio_spreads.values() if s <= 2)
    localized_pct = localized / len(t_folio_spreads) * 100 if t_folio_spreads else 0

    print(f"Highly localized (1-2 folios): {localized} ({localized_pct:.1f}%)")

    test5_verdict = "RI-LIKE" if mean_spread < 3.0 else "PP-LIKE"
    print(f"Verdict: {test5_verdict} (mean {mean_spread:.2f} vs RI=1.34, PP=7.96)")
    print()

    results['tests']['test5_folio_spread'] = {
        'mean_spread': mean_spread,
        'ri_baseline': 1.34,
        'pp_baseline': 7.96,
        'localized_count': localized,
        'localized_pct': localized_pct,
        'verdict': test5_verdict,
        'distribution': dict(spread_dist),
    }

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    verdicts = {
        'Test 1 (RI Fraction)': results['tests']['test1_ri_fraction']['verdict'],
        'Test 2 (AZC Participation)': results['tests']['test2_azc_participation']['verdict'],
        'Test 3 (Control Operators)': f"{results['tests']['test3_control_operators']['control_operators_found']} found",
        'Test 4 (PREFIX/ct)': results['tests']['test4_prefix_distribution']['verdict'],
        'Test 5 (Folio Spread)': results['tests']['test5_folio_spread']['verdict'],
    }

    print("| Test | Verdict |")
    print("|------|---------|")
    for test, verdict in verdicts.items():
        print(f"| {test} | {verdict} |")
    print()

    # Decision logic
    ri_enriched = results['tests']['test1_ri_fraction']['verdict'] == 'ENRICHED'
    azc_reduced = results['tests']['test2_azc_participation']['verdict'] == 'REDUCED'
    ri_like_spread = results['tests']['test5_folio_spread']['verdict'] == 'RI-LIKE'

    if ri_enriched or azc_reduced or ri_like_spread:
        conclusion = "C498_EXPLAINS_EXCLUSION"
        explanation = "Section T's B-absence is predicted by existing constraints - vocabulary is predominantly registry-internal."
    else:
        conclusion = "FURTHER_INVESTIGATION_NEEDED"
        explanation = "Section T vocabulary does not appear predominantly registry-internal - the B-absence requires additional explanation."

    print(f"CONCLUSION: {conclusion}")
    print(f"  {explanation}")
    print()

    results['conclusion'] = {
        'verdict': conclusion,
        'explanation': explanation,
        'verdicts': verdicts,
    }

    # Save results
    RESULTS_PATH.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH / 'section_t_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"Results saved to {RESULTS_PATH / 'section_t_analysis.json'}")


if __name__ == '__main__':
    main()
