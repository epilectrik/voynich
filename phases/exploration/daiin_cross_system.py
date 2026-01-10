#!/usr/bin/env python3
"""
daiin Cross-System Role Analysis

PURPOSE: Determine if daiin is a UNIVERSAL ARTICULATOR that adapts its
structural role by system context.

HYPOTHESIS:
- In A: Internal articulation punctuation (C422)
- In B: Line-initial boundary marker (CORE_CONTROL, 3-11x enriched)
- In AZC: ???

TESTS:
1. Position distribution in A, B, AZC
2. Frequency normalization across systems
3. Placement-class correlation (AZC only)

SUCCESS CRITERIA:
- Either: daiin is boundary-enriched in AZC (confirms universal articulator)
- Or: daiin breaks the pattern (documents exception)
"""

import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import List, Dict, Optional

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer/parsing')
from currier_a import parse_currier_a_token

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'

# DA family tokens (from C422)
DA_PREFIXES = {'da', 'dal', 'dam', 'dan', 'dar'}


@dataclass
class TokenRecord:
    """A token with its metadata."""
    word: str
    folio: str
    section: str
    language: str  # 'A', 'B', or 'AZC' (NA in data)
    placement: str
    line_number: str
    line_initial: bool
    line_final: bool
    is_da: bool


def is_da_token(token: str) -> bool:
    """Check if token is a DA family member."""
    token_lower = token.lower()

    # Direct DA prefix check
    result = parse_currier_a_token(token)
    if result.prefix in DA_PREFIXES:
        return True

    # Extended DA patterns
    if token_lower.startswith('daiin') or token_lower.startswith('dain'):
        return True

    # Any da- prefix
    if result.prefix and result.prefix.startswith('da'):
        return True

    return False


def load_all_tokens() -> List[TokenRecord]:
    """Load all tokens with metadata."""
    tokens = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()  # Skip header

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 15:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                section = parts[3].strip('"').strip()
                language_raw = parts[6].strip('"').strip()
                placement = parts[10].strip('"').strip() if len(parts) > 10 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''
                line_initial = parts[13].strip('"').strip() if len(parts) > 13 else ''
                line_final = parts[14].strip('"').strip() if len(parts) > 14 else ''

                # Normalize language
                if language_raw == 'NA' or language_raw == '':
                    language = 'AZC'
                else:
                    language = language_raw

                # Parse line position flags
                is_initial = line_initial == '1' or (line_initial.isdigit() and int(line_initial) == 1)
                is_final = line_final == '1' or (line_final.isdigit() and int(line_final) == 1)

                tokens.append(TokenRecord(
                    word=word,
                    folio=folio,
                    section=section,
                    language=language,
                    placement=placement,
                    line_number=line_num,
                    line_initial=is_initial,
                    line_final=is_final,
                    is_da=is_da_token(word)
                ))

    return tokens


def analyze_position_distribution(tokens: List[TokenRecord]) -> Dict:
    """Analyze DA position distribution by system."""
    results = {}

    for lang in ['A', 'B', 'AZC']:
        lang_tokens = [t for t in tokens if t.language == lang]
        da_tokens = [t for t in lang_tokens if t.is_da]

        # Position counts
        initial_da = sum(1 for t in da_tokens if t.line_initial)
        final_da = sum(1 for t in da_tokens if t.line_final)
        internal_da = sum(1 for t in da_tokens if not t.line_initial and not t.line_final)

        # Baseline for comparison
        initial_all = sum(1 for t in lang_tokens if t.line_initial)
        final_all = sum(1 for t in lang_tokens if t.line_final)
        internal_all = sum(1 for t in lang_tokens if not t.line_initial and not t.line_final)

        total_da = len(da_tokens)
        total_all = len(lang_tokens)

        results[lang] = {
            'total_tokens': total_all,
            'total_da': total_da,
            'da_rate': 100 * total_da / total_all if total_all > 0 else 0,
            'initial_da': initial_da,
            'final_da': final_da,
            'internal_da': internal_da,
            'initial_da_pct': 100 * initial_da / total_da if total_da > 0 else 0,
            'final_da_pct': 100 * final_da / total_da if total_da > 0 else 0,
            'internal_da_pct': 100 * internal_da / total_da if total_da > 0 else 0,
            # Baseline rates
            'initial_baseline': 100 * initial_all / total_all if total_all > 0 else 0,
            'final_baseline': 100 * final_all / total_all if total_all > 0 else 0,
            'internal_baseline': 100 * internal_all / total_all if total_all > 0 else 0,
        }

        # Enrichment ratios
        r = results[lang]
        r['initial_enrichment'] = r['initial_da_pct'] / r['initial_baseline'] if r['initial_baseline'] > 0 else 0
        r['final_enrichment'] = r['final_da_pct'] / r['final_baseline'] if r['final_baseline'] > 0 else 0
        r['internal_enrichment'] = r['internal_da_pct'] / r['internal_baseline'] if r['internal_baseline'] > 0 else 0

    return results


def analyze_placement_correlation(tokens: List[TokenRecord]) -> Dict:
    """Analyze DA × Placement correlation in AZC."""
    azc_tokens = [t for t in tokens if t.language == 'AZC']

    # Count by placement
    placement_counts = Counter(t.placement for t in azc_tokens if t.placement)
    da_by_placement = Counter(t.placement for t in azc_tokens if t.is_da and t.placement)

    results = {
        'placements': {},
        'total_azc': len(azc_tokens),
        'total_da': sum(1 for t in azc_tokens if t.is_da)
    }

    for placement, count in placement_counts.most_common():
        da_count = da_by_placement.get(placement, 0)
        da_rate = 100 * da_count / count if count > 0 else 0
        overall_rate = 100 * results['total_da'] / results['total_azc'] if results['total_azc'] > 0 else 0
        enrichment = da_rate / overall_rate if overall_rate > 0 else 0

        results['placements'][placement] = {
            'total': count,
            'da': da_count,
            'da_rate': da_rate,
            'enrichment': enrichment
        }

    return results


def analyze_specific_da_forms(tokens: List[TokenRecord]) -> Dict:
    """Analyze specific DA forms (daiin, dain, dar, etc.) by system."""
    results = {}

    for lang in ['A', 'B', 'AZC']:
        lang_tokens = [t for t in tokens if t.language == lang]
        da_tokens = [t for t in lang_tokens if t.is_da]

        # Count specific forms
        form_counts = Counter()
        for t in da_tokens:
            word = t.word.lower()
            if word.startswith('daiin'):
                form_counts['daiin*'] += 1
            elif word.startswith('dain'):
                form_counts['dain*'] += 1
            elif word.startswith('dar'):
                form_counts['dar*'] += 1
            elif word.startswith('dal'):
                form_counts['dal*'] += 1
            elif word.startswith('dam'):
                form_counts['dam*'] += 1
            elif word.startswith('dan'):
                form_counts['dan*'] += 1
            else:
                form_counts['da*other'] += 1

        total = len(da_tokens)
        results[lang] = {
            'total_da': total,
            'forms': {form: {'count': c, 'pct': 100 * c / total if total > 0 else 0}
                      for form, c in form_counts.most_common()}
        }

    return results


def report_position_analysis(results: Dict):
    """Report position distribution analysis."""
    print("\n" + "=" * 70)
    print("ANALYSIS 1: POSITION DISTRIBUTION BY SYSTEM")
    print("=" * 70)

    print("\n{:<8} {:>12} {:>10} {:>12} {:>12} {:>12} {:>12}".format(
        "System", "Total", "DA Count", "DA Rate %", "Initial %", "Internal %", "Final %"))
    print("-" * 82)

    for lang in ['A', 'B', 'AZC']:
        r = results[lang]
        print("{:<8} {:>12,} {:>10,} {:>12.2f} {:>12.1f} {:>12.1f} {:>12.1f}".format(
            lang, r['total_tokens'], r['total_da'], r['da_rate'],
            r['initial_da_pct'], r['internal_da_pct'], r['final_da_pct']))

    print("\n" + "-" * 70)
    print("ENRICHMENT RATIOS (DA position % / baseline position %)")
    print("-" * 70)

    print("\n{:<8} {:>15} {:>15} {:>15}".format(
        "System", "Initial", "Internal", "Final"))
    print("-" * 55)

    for lang in ['A', 'B', 'AZC']:
        r = results[lang]
        print("{:<8} {:>14.2f}x {:>14.2f}x {:>14.2f}x".format(
            lang, r['initial_enrichment'], r['internal_enrichment'], r['final_enrichment']))

    print("\n" + "-" * 70)
    print("INTERPRETATION:")
    print("-" * 70)

    # Compare patterns
    a_pattern = "internal" if results['A']['internal_enrichment'] > max(results['A']['initial_enrichment'], results['A']['final_enrichment']) else "boundary"
    b_pattern = "initial" if results['B']['initial_enrichment'] > max(results['B']['internal_enrichment'], results['B']['final_enrichment']) else "other"

    azc = results['AZC']
    azc_max = max(azc['initial_enrichment'], azc['internal_enrichment'], azc['final_enrichment'])
    if azc['initial_enrichment'] == azc_max:
        azc_pattern = "initial (B-like)"
    elif azc['internal_enrichment'] == azc_max:
        azc_pattern = "internal (A-like)"
    else:
        azc_pattern = "final (unique)"

    print(f"\n  Currier A: DA enriched at {a_pattern} positions")
    print(f"  Currier B: DA enriched at {b_pattern} positions")
    print(f"  AZC: DA enriched at {azc_pattern} positions")


def report_placement_analysis(results: Dict):
    """Report AZC placement correlation analysis."""
    print("\n" + "=" * 70)
    print("ANALYSIS 2: AZC PLACEMENT-CLASS CORRELATION")
    print("=" * 70)

    print(f"\nTotal AZC tokens: {results['total_azc']:,}")
    print(f"Total DA tokens in AZC: {results['total_da']:,}")
    print(f"Overall DA rate: {100 * results['total_da'] / results['total_azc']:.2f}%")

    print("\n{:<12} {:>10} {:>10} {:>12} {:>12}".format(
        "Placement", "Total", "DA", "DA Rate %", "Enrichment"))
    print("-" * 60)

    # Sort by enrichment
    sorted_placements = sorted(
        results['placements'].items(),
        key=lambda x: x[1]['enrichment'],
        reverse=True
    )

    for placement, data in sorted_placements:
        if data['total'] >= 10:  # Only show placements with sufficient data
            marker = "*" if data['enrichment'] > 1.5 else ("-" if data['enrichment'] < 0.5 else "")
            print("{:<12} {:>10,} {:>10,} {:>11.2f}% {:>11.2f}x {}".format(
                placement, data['total'], data['da'], data['da_rate'],
                data['enrichment'], marker))

    print("\n* = enriched (>1.5x), - = depleted (<0.5x)")


def report_form_analysis(results: Dict):
    """Report specific DA form distribution."""
    print("\n" + "=" * 70)
    print("ANALYSIS 3: SPECIFIC DA FORM DISTRIBUTION")
    print("=" * 70)

    for lang in ['A', 'B', 'AZC']:
        r = results[lang]
        print(f"\n{lang} (n={r['total_da']:,} DA tokens):")
        for form, data in r['forms'].items():
            print(f"  {form:<12}: {data['count']:>6,} ({data['pct']:>5.1f}%)")


def main():
    print("=" * 70)
    print("daiin CROSS-SYSTEM ROLE ANALYSIS")
    print("=" * 70)

    print("\nLoading all tokens...")
    tokens = load_all_tokens()

    total_by_lang = Counter(t.language for t in tokens)
    print(f"Total tokens loaded: {len(tokens):,}")
    for lang, count in sorted(total_by_lang.items()):
        print(f"  {lang}: {count:,}")

    # Analysis 1: Position distribution
    position_results = analyze_position_distribution(tokens)
    report_position_analysis(position_results)

    # Analysis 2: AZC placement correlation
    placement_results = analyze_placement_correlation(tokens)
    report_placement_analysis(placement_results)

    # Analysis 3: Specific DA forms
    form_results = analyze_specific_da_forms(tokens)
    report_form_analysis(form_results)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: UNIVERSAL ARTICULATOR HYPOTHESIS")
    print("=" * 70)

    a = position_results['A']
    b = position_results['B']
    azc = position_results['AZC']

    print(f"""
System Comparison:
                       A           B         AZC
  DA Rate:           {a['da_rate']:>5.2f}%      {b['da_rate']:>5.2f}%      {azc['da_rate']:>5.2f}%
  Initial Enrichment:{a['initial_enrichment']:>5.2f}x      {b['initial_enrichment']:>5.2f}x      {azc['initial_enrichment']:>5.2f}x
  Internal Enrichment:{a['internal_enrichment']:>4.2f}x      {b['internal_enrichment']:>5.2f}x      {azc['internal_enrichment']:>5.2f}x
  Final Enrichment:  {a['final_enrichment']:>5.2f}x      {b['final_enrichment']:>5.2f}x      {azc['final_enrichment']:>5.2f}x

Known patterns:
  A: DA = internal articulation (separates prefix runs)
  B: DA = line-initial boundary marker (3-11x enriched)
""")

    # Determine AZC pattern
    if azc['initial_enrichment'] > 1.5:
        print("AZC finding: DA shows B-LIKE initial enrichment")
        print("-> Confirms universal articulator with BOUNDARY function")
    elif azc['internal_enrichment'] > 1.5:
        print("AZC finding: DA shows A-LIKE internal enrichment")
        print("-> Confirms universal articulator with INTERNAL function")
    elif azc['final_enrichment'] > 1.5:
        print("AZC finding: DA shows UNIQUE final enrichment")
        print("-> Partial confirmation: articulator but with different position")
    else:
        print("AZC finding: DA shows NO CLEAR positional enrichment")
        print("-> Exception to universal articulator hypothesis")

    print("\n" + "=" * 70)
    print("CONSTRAINT STATUS: Descriptive finding only, no changes proposed")
    print("=" * 70)


if __name__ == "__main__":
    main()
