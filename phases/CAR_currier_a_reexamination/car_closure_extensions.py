"""
CAR Phase: Closure State Extension Analysis

Three investigations suggested by expert review:
1. Closure × HT - Does closure state appear more before HT phase resets?
2. Closure × AZC - Does closure pattern vary by AZC family?
3. Entry shape variance - What's the distribution of entry lengths/complexity?

"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

# Use the phase data loader
from car_data_loader import CARDataLoader


def load_currier_a_data():
    """Load Currier A data with H-only filter."""
    loader = CARDataLoader()
    return loader.get_currier_a()


def get_section_families(df):
    """
    Get section-based families for Currier A folios.

    Within Currier A, the meaningful distinction is:
    - Herbal A section (f1-f57): Earlier folios
    - Herbal C section (f87-f102): Later folios

    NOTE: Zodiac (Z section) is NOT part of Currier A - it's a separate
    language category in the AZC system. This analysis compares
    Herbal A vs Herbal C within Currier A.
    """
    herbal_a = set()  # f1-f57 range
    herbal_c = set()  # f87-f102 range

    for folio in df['folio'].unique():
        # Extract folio number
        import re
        match = re.search(r'f(\d+)', folio)
        if match:
            num = int(match.group(1))
            if num <= 57:
                herbal_a.add(folio)
            elif num >= 87:
                herbal_c.add(folio)
            # folios 58-86 are ambiguous/mixed, exclude

    return herbal_a, herbal_c


def detect_ht_tokens(tokens):
    """Detect HT (Head-Tail) pattern tokens."""
    # HT markers based on existing constraints
    # H-initial tokens typically start with specific patterns
    # T-final tokens have characteristic endings

    ht_markers = {
        'h_initial': ['qo', 'cho', 'sho', 'do'],  # Common H-initial prefixes
        't_final': ['dy', 'y', 'ry', 'ly', 'ty']   # Common T-final suffixes
    }

    h_tokens = []
    t_tokens = []

    for token in tokens:
        # Check for H-initial
        for h in ht_markers['h_initial']:
            if token.startswith(h):
                h_tokens.append(token)
                break

        # Check for T-final
        for t in ht_markers['t_final']:
            if token.endswith(t):
                t_tokens.append(token)
                break

    return h_tokens, t_tokens


def get_da_family_tokens():
    """Get tokens that belong to DA-family (closure markers)."""
    # DA-family prefixes identified in deep analysis
    da_prefixes = ['da', 'd']
    return da_prefixes


def is_da_family(token):
    """Check if token belongs to DA-family."""
    da_prefixes = ['da', 'd']
    for prefix in da_prefixes:
        if token.startswith(prefix):
            return True
    return False


def has_closure_ending(token):
    """Check if token has closure morphology (-y, -n, -m endings)."""
    return token.endswith('y') or token.endswith('n') or token.endswith('m')


def analyze_closure_ht(df):
    """
    Investigation 1: Closure × HT

    Question: Does closure state appear more before HT phase resets?

    If closure is about "returning to neutral", we might expect:
    - Higher closure rate before H-initial tokens (phase reset)
    - Lower closure rate before T-final sequences (continuing phase)
    """
    print("\n" + "="*70)
    print("INVESTIGATION 1: Closure × HT Relationship")
    print("="*70)

    results = {
        'test': 'closure_ht_relationship',
        'question': 'Does closure state appear more before HT phase resets?'
    }

    # Group by folio and line to get sequences
    lines_data = []
    for (folio, line_num), group in df.groupby(['folio', 'line_number']):
        tokens = group['word'].tolist()
        if len(tokens) >= 1:
            lines_data.append({
                'folio': folio,
                'line': line_num,
                'tokens': tokens,
                'first_token': tokens[0],
                'last_token': tokens[-1] if tokens else None
            })

    # Sort by folio and line
    lines_data.sort(key=lambda x: (x['folio'], x['line']))

    # Analyze: what comes AFTER closure tokens?
    # If closure resets to neutral, next line should show more H-initial tokens

    closure_then_h = 0  # Closure token at end, next line starts with H-initial
    closure_then_not_h = 0
    no_closure_then_h = 0
    no_closure_then_not_h = 0

    h_initial_prefixes = ['qo', 'cho', 'sho', 'do', 'o']

    for i in range(len(lines_data) - 1):
        curr = lines_data[i]
        next_line = lines_data[i + 1]

        # Only compare within same folio
        if curr['folio'] != next_line['folio']:
            continue

        # Check if current line ends with closure
        last_token = curr['last_token']
        has_closure = is_da_family(last_token) or has_closure_ending(last_token)

        # Check if next line starts with H-initial
        first_token = next_line['first_token']
        is_h_initial = any(first_token.startswith(h) for h in h_initial_prefixes)

        if has_closure and is_h_initial:
            closure_then_h += 1
        elif has_closure and not is_h_initial:
            closure_then_not_h += 1
        elif not has_closure and is_h_initial:
            no_closure_then_h += 1
        else:
            no_closure_then_not_h += 1

    # Calculate rates
    total_closure = closure_then_h + closure_then_not_h
    total_no_closure = no_closure_then_h + no_closure_then_not_h

    if total_closure > 0:
        h_after_closure = closure_then_h / total_closure
    else:
        h_after_closure = 0

    if total_no_closure > 0:
        h_after_no_closure = no_closure_then_h / total_no_closure
    else:
        h_after_no_closure = 0

    # Chi-square test
    contingency = [[closure_then_h, closure_then_not_h],
                   [no_closure_then_h, no_closure_then_not_h]]

    if min(closure_then_h, closure_then_not_h, no_closure_then_h, no_closure_then_not_h) >= 5:
        chi2, p_value = stats.chi2_contingency(contingency)[:2]
    else:
        chi2, p_value = 0, 1.0

    print(f"\nClosure -> H-initial transition analysis:")
    print(f"  Lines ending with closure: {total_closure}")
    print(f"  Lines NOT ending with closure: {total_no_closure}")
    print(f"\n  H-initial rate after closure: {h_after_closure:.1%}")
    print(f"  H-initial rate after non-closure: {h_after_no_closure:.1%}")
    print(f"  Ratio: {h_after_closure/h_after_no_closure:.2f}x" if h_after_no_closure > 0 else "  Ratio: N/A")
    print(f"\n  Chi-square: {chi2:.2f}, p = {p_value:.4f}")

    results['counts'] = {
        'closure_then_h': closure_then_h,
        'closure_then_not_h': closure_then_not_h,
        'no_closure_then_h': no_closure_then_h,
        'no_closure_then_not_h': no_closure_then_not_h
    }
    results['rates'] = {
        'h_after_closure': h_after_closure,
        'h_after_no_closure': h_after_no_closure,
        'ratio': h_after_closure / h_after_no_closure if h_after_no_closure > 0 else None
    }
    results['chi2'] = chi2
    results['p_value'] = p_value

    # Also check: closure at T-final positions
    print("\n" + "-"*50)
    print("Secondary: Closure morphology at line-final by HT phase")

    # Count closure endings by whether line has HT structure
    lines_with_ht = 0
    lines_without_ht = 0
    closure_in_ht_lines = 0
    closure_in_non_ht_lines = 0

    for line_info in lines_data:
        tokens = line_info['tokens']
        h_tokens, t_tokens = detect_ht_tokens(tokens)

        has_ht = len(h_tokens) > 0 and len(t_tokens) > 0
        last_has_closure = is_da_family(tokens[-1]) or has_closure_ending(tokens[-1])

        if has_ht:
            lines_with_ht += 1
            if last_has_closure:
                closure_in_ht_lines += 1
        else:
            lines_without_ht += 1
            if last_has_closure:
                closure_in_non_ht_lines += 1

    ht_closure_rate = closure_in_ht_lines / lines_with_ht if lines_with_ht > 0 else 0
    non_ht_closure_rate = closure_in_non_ht_lines / lines_without_ht if lines_without_ht > 0 else 0

    print(f"\n  Lines with HT structure: {lines_with_ht}")
    print(f"  Lines without HT structure: {lines_without_ht}")
    print(f"\n  Closure rate in HT lines: {ht_closure_rate:.1%}")
    print(f"  Closure rate in non-HT lines: {non_ht_closure_rate:.1%}")

    results['ht_closure'] = {
        'lines_with_ht': lines_with_ht,
        'lines_without_ht': lines_without_ht,
        'closure_in_ht': closure_in_ht_lines,
        'closure_in_non_ht': closure_in_non_ht_lines,
        'ht_closure_rate': ht_closure_rate,
        'non_ht_closure_rate': non_ht_closure_rate
    }

    # Verdict
    if p_value < 0.05 and h_after_closure > h_after_no_closure:
        verdict = "CLOSURE_ENABLES_RESET"
        print(f"\n  VERDICT: {verdict}")
        print("  Closure tokens increase H-initial probability in following line")
    elif p_value < 0.05:
        verdict = "CLOSURE_SUPPRESSES_RESET"
        print(f"\n  VERDICT: {verdict}")
        print("  Closure tokens decrease H-initial probability (unexpected)")
    else:
        verdict = "NO_HT_RELATIONSHIP"
        print(f"\n  VERDICT: {verdict}")
        print("  Closure state is independent of HT phase structure")

    results['verdict'] = verdict
    return results


def analyze_closure_azc(df):
    """
    Investigation 2: Closure × Section

    Question: Does closure pattern vary by manuscript section?

    Within Currier A, compare Herbal A (early folios) vs Herbal C (late folios).
    NOTE: Zodiac is NOT part of Currier A - it's a separate language category.
    """
    print("\n" + "="*70)
    print("INVESTIGATION 2: Closure × Section (Herbal A vs Herbal C)")
    print("="*70)

    results = {
        'test': 'closure_section_relationship',
        'question': 'Does closure pattern vary by section (Herbal A vs Herbal C)?'
    }

    herbal_a_folios, herbal_c_folios = get_section_families(df)

    print(f"\nFolio counts:")
    print(f"  Herbal A folios (f1-f57): {len(herbal_a_folios)}")
    print(f"  Herbal C folios (f87-f102): {len(herbal_c_folios)}")

    # Separate data by section
    herbal_a_df = df[df['folio'].isin(herbal_a_folios)]
    herbal_c_df = df[df['folio'].isin(herbal_c_folios)]

    def get_closure_stats(family_df, family_name):
        """Calculate closure statistics for a family."""
        stats_dict = {
            'family': family_name,
            'total_lines': 0,
            'da_family_final': 0,
            'y_ending_final': 0,
            'n_ending_final': 0,
            'm_ending_final': 0,
            'any_closure_final': 0,
            'da_family_initial': 0,
            'no_prefix_initial': 0
        }

        standard_prefixes = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'o', 'y', 's', 'k', 'l', 't', 'p', 'f', 'c']

        for (folio, line_num), group in family_df.groupby(['folio', 'line_number']):
            tokens = group['word'].tolist()
            if not tokens:
                continue

            stats_dict['total_lines'] += 1

            first_token = tokens[0]
            last_token = tokens[-1]

            # Final position analysis
            if is_da_family(last_token):
                stats_dict['da_family_final'] += 1
            if last_token.endswith('y'):
                stats_dict['y_ending_final'] += 1
            if last_token.endswith('n'):
                stats_dict['n_ending_final'] += 1
            if last_token.endswith('m'):
                stats_dict['m_ending_final'] += 1
            if is_da_family(last_token) or has_closure_ending(last_token):
                stats_dict['any_closure_final'] += 1

            # Initial position analysis
            if is_da_family(first_token):
                stats_dict['da_family_initial'] += 1

            has_standard_prefix = any(first_token.startswith(p) for p in standard_prefixes)
            if not has_standard_prefix:
                stats_dict['no_prefix_initial'] += 1

        return stats_dict

    herbal_a_stats = get_closure_stats(herbal_a_df, 'Herbal_A')
    herbal_c_stats = get_closure_stats(herbal_c_df, 'Herbal_C')

    print("\n" + "-"*50)
    print("Closure rates by section:")
    print("-"*50)

    print(f"\n{'Metric':<30} {'Herbal A':>12} {'Herbal C':>12} {'Ratio':>10}")
    print("-"*64)

    metrics = [
        ('DA-family at final', 'da_family_final'),
        ('-y ending at final', 'y_ending_final'),
        ('-n ending at final', 'n_ending_final'),
        ('-m ending at final', 'm_ending_final'),
        ('Any closure at final', 'any_closure_final'),
        ('DA-family at initial', 'da_family_initial'),
        ('No prefix at initial', 'no_prefix_initial')
    ]

    comparison = {}
    for label, key in metrics:
        ha_rate = herbal_a_stats[key] / herbal_a_stats['total_lines'] if herbal_a_stats['total_lines'] > 0 else 0
        hc_rate = herbal_c_stats[key] / herbal_c_stats['total_lines'] if herbal_c_stats['total_lines'] > 0 else 0
        ratio = ha_rate / hc_rate if hc_rate > 0 else float('inf')

        print(f"{label:<30} {ha_rate:>11.1%} {hc_rate:>11.1%} {ratio:>9.2f}x")
        comparison[key] = {
            'herbal_a_rate': ha_rate,
            'herbal_c_rate': hc_rate,
            'ratio': ratio
        }

    results['herbal_a_stats'] = herbal_a_stats
    results['herbal_c_stats'] = herbal_c_stats
    results['comparison'] = comparison

    # Chi-square test for any_closure_final
    ha_closure = herbal_a_stats['any_closure_final']
    ha_no_closure = herbal_a_stats['total_lines'] - ha_closure
    hc_closure = herbal_c_stats['any_closure_final']
    hc_no_closure = herbal_c_stats['total_lines'] - hc_closure

    if min(ha_closure, ha_no_closure, hc_closure, hc_no_closure) >= 5:
        contingency = [[ha_closure, ha_no_closure], [hc_closure, hc_no_closure]]
        chi2, p_value = stats.chi2_contingency(contingency)[:2]
    else:
        chi2, p_value = 0, 1.0

    print(f"\nChi-square test (any closure at final):")
    print(f"  Chi-square: {chi2:.2f}, p = {p_value:.4f}")

    results['chi2'] = chi2
    results['p_value'] = p_value

    # Verdict
    if p_value < 0.05:
        ha_rate = comparison['any_closure_final']['herbal_a_rate']
        hc_rate = comparison['any_closure_final']['herbal_c_rate']
        if ha_rate > hc_rate:
            verdict = "HERBAL_A_MORE_CLOSURE"
            print(f"\n  VERDICT: {verdict}")
            print("  Herbal A folios have significantly higher closure rate")
        else:
            verdict = "HERBAL_C_MORE_CLOSURE"
            print(f"\n  VERDICT: {verdict}")
            print("  Herbal C folios have significantly higher closure rate")
    else:
        verdict = "NO_SECTION_DIFFERENCE"
        print(f"\n  VERDICT: {verdict}")
        print("  Closure pattern is consistent across sections")

    results['verdict'] = verdict
    return results


def analyze_entry_shape(df):
    """
    Investigation 3: Entry Shape Variance

    Question: What's the distribution of entry lengths/complexity?

    Understanding entry shape helps contextualize when closure matters.
    """
    print("\n" + "="*70)
    print("INVESTIGATION 3: Entry Shape Variance")
    print("="*70)

    results = {
        'test': 'entry_shape_variance',
        'question': 'What is the distribution of entry lengths/complexity?'
    }

    # Collect entry-level metrics
    entries = []
    for (folio, line_num), group in df.groupby(['folio', 'line_number']):
        tokens = group['word'].tolist()
        if not tokens:
            continue

        # Extract MIDDLEs (simplified: remove common prefixes/suffixes)
        middles = set()
        for token in tokens:
            # Strip known prefixes
            middle = token
            for prefix in ['qo', 'cho', 'sho', 'ch', 'sh', 'da', 'ok', 'ot', 'ol', 'ct', 'o', 'd']:
                if middle.startswith(prefix):
                    middle = middle[len(prefix):]
                    break
            # Strip known suffixes
            for suffix in ['dy', 'y', 'n', 'm', 'l', 'r', 's']:
                if middle.endswith(suffix) and len(middle) > len(suffix):
                    middle = middle[:-len(suffix)]
                    break
            if middle:
                middles.add(middle)

        # Count DA markers
        da_count = sum(1 for t in tokens if 'da' in t.lower() or t == 'd')

        # Detect closure at final
        last_token = tokens[-1]
        has_closure = is_da_family(last_token) or has_closure_ending(last_token)

        # Detect opener (no standard prefix)
        first_token = tokens[0]
        standard_prefixes = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
        has_opener = not any(first_token.startswith(p) for p in standard_prefixes)

        entries.append({
            'folio': folio,
            'line': line_num,
            'token_count': len(tokens),
            'unique_tokens': len(set(tokens)),
            'middle_count': len(middles),
            'da_count': da_count,
            'has_closure': has_closure,
            'has_opener': has_opener
        })

    # Calculate distributions
    token_counts = [e['token_count'] for e in entries]
    unique_counts = [e['unique_tokens'] for e in entries]
    middle_counts = [e['middle_count'] for e in entries]
    da_counts = [e['da_count'] for e in entries]

    print(f"\nEntry count: {len(entries)}")

    print("\n" + "-"*50)
    print("Token count distribution:")
    print("-"*50)
    print(f"  Min: {min(token_counts)}")
    print(f"  Max: {max(token_counts)}")
    print(f"  Mean: {np.mean(token_counts):.2f}")
    print(f"  Median: {np.median(token_counts):.1f}")
    print(f"  Std: {np.std(token_counts):.2f}")

    # Token count histogram
    token_bins = Counter()
    for tc in token_counts:
        if tc <= 3:
            token_bins['1-3'] += 1
        elif tc <= 6:
            token_bins['4-6'] += 1
        elif tc <= 9:
            token_bins['7-9'] += 1
        elif tc <= 12:
            token_bins['10-12'] += 1
        else:
            token_bins['13+'] += 1

    print("\n  Distribution:")
    for bin_name in ['1-3', '4-6', '7-9', '10-12', '13+']:
        count = token_bins[bin_name]
        pct = count / len(entries) * 100
        bar = '#' * int(pct / 2)
        print(f"    {bin_name:>5}: {count:>4} ({pct:>5.1f}%) {bar}")

    results['token_count'] = {
        'min': min(token_counts),
        'max': max(token_counts),
        'mean': float(np.mean(token_counts)),
        'median': float(np.median(token_counts)),
        'std': float(np.std(token_counts)),
        'distribution': dict(token_bins)
    }

    print("\n" + "-"*50)
    print("MIDDLE count distribution:")
    print("-"*50)
    print(f"  Min: {min(middle_counts)}")
    print(f"  Max: {max(middle_counts)}")
    print(f"  Mean: {np.mean(middle_counts):.2f}")
    print(f"  Median: {np.median(middle_counts):.1f}")

    results['middle_count'] = {
        'min': min(middle_counts),
        'max': max(middle_counts),
        'mean': float(np.mean(middle_counts)),
        'median': float(np.median(middle_counts))
    }

    print("\n" + "-"*50)
    print("DA articulation distribution:")
    print("-"*50)
    da_bins = Counter(da_counts)
    for da_val in sorted(da_bins.keys())[:8]:
        count = da_bins[da_val]
        pct = count / len(entries) * 100
        bar = '#' * int(pct / 2)
        print(f"    DA={da_val}: {count:>4} ({pct:>5.1f}%) {bar}")

    results['da_count'] = {
        'distribution': {str(k): v for k, v in dict(da_bins).items()},
        'mean': float(np.mean(da_counts)),
        'entries_with_da': sum(1 for d in da_counts if d > 0)
    }

    print("\n" + "-"*50)
    print("Closure × Entry Length:")
    print("-"*50)

    # Do longer entries have more closure?
    closure_by_length = defaultdict(lambda: {'closure': 0, 'total': 0})
    for e in entries:
        if e['token_count'] <= 3:
            bin_name = 'short (1-3)'
        elif e['token_count'] <= 6:
            bin_name = 'medium (4-6)'
        else:
            bin_name = 'long (7+)'

        closure_by_length[bin_name]['total'] += 1
        if e['has_closure']:
            closure_by_length[bin_name]['closure'] += 1

    print(f"\n  {'Length':<15} {'Closure Rate':>15} {'Count':>10}")
    print("  " + "-"*42)

    closure_length_data = {}
    for bin_name in ['short (1-3)', 'medium (4-6)', 'long (7+)']:
        data = closure_by_length[bin_name]
        rate = data['closure'] / data['total'] if data['total'] > 0 else 0
        print(f"  {bin_name:<15} {rate:>14.1%} {data['total']:>10}")
        closure_length_data[bin_name] = {'rate': rate, 'total': data['total']}

    results['closure_by_length'] = closure_length_data

    # Correlation: token count vs closure
    closure_binary = [1 if e['has_closure'] else 0 for e in entries]
    if len(set(closure_binary)) > 1:
        corr, p_corr = stats.pointbiserialr(closure_binary, token_counts)
        print(f"\n  Token count × Closure correlation: r = {corr:.3f}, p = {p_corr:.4f}")
        results['length_closure_correlation'] = {'r': float(corr), 'p': float(p_corr)}

    print("\n" + "-"*50)
    print("Entry Grammar Conformance:")
    print("-"*50)

    # How many entries follow [opener] + [content] + [closer] pattern?
    full_grammar = sum(1 for e in entries if e['has_opener'] and e['has_closure'])
    opener_only = sum(1 for e in entries if e['has_opener'] and not e['has_closure'])
    closer_only = sum(1 for e in entries if not e['has_opener'] and e['has_closure'])
    neither = sum(1 for e in entries if not e['has_opener'] and not e['has_closure'])

    print(f"\n  Full grammar (opener + closer): {full_grammar:>5} ({full_grammar/len(entries)*100:.1f}%)")
    print(f"  Opener only:                    {opener_only:>5} ({opener_only/len(entries)*100:.1f}%)")
    print(f"  Closer only:                    {closer_only:>5} ({closer_only/len(entries)*100:.1f}%)")
    print(f"  Neither:                        {neither:>5} ({neither/len(entries)*100:.1f}%)")

    results['grammar_conformance'] = {
        'full_grammar': full_grammar,
        'opener_only': opener_only,
        'closer_only': closer_only,
        'neither': neither,
        'full_grammar_rate': full_grammar / len(entries)
    }

    # Verdict
    print(f"\n  VERDICT: ENTRY_SHAPE_CHARACTERIZED")
    print(f"  - Typical entry: {np.median(token_counts):.0f} tokens (median)")
    print(f"  - {results['grammar_conformance']['full_grammar_rate']*100:.1f}% follow full opener+closer grammar")
    print(f"  - Closure is {'length-independent' if abs(corr) < 0.1 else 'length-associated'}")

    results['verdict'] = 'ENTRY_SHAPE_CHARACTERIZED'
    return results


def main():
    print("="*70)
    print("CAR Phase: Closure State Extension Analysis")
    print("="*70)

    # Load data
    print("\nLoading Currier A data (H-only)...")
    df = load_currier_a_data()
    print(f"Loaded {len(df)} tokens from {df['folio'].nunique()} folios")

    # Run all three investigations
    results = {}

    results['closure_ht'] = analyze_closure_ht(df)
    results['closure_azc'] = analyze_closure_azc(df)
    results['entry_shape'] = analyze_entry_shape(df)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print(f"\n1. Closure × HT: {results['closure_ht']['verdict']}")
    print(f"2. Closure × AZC: {results['closure_azc']['verdict']}")
    print(f"3. Entry Shape: {results['entry_shape']['verdict']}")

    # Save results
    output_path = Path(__file__).parent / 'car_closure_extensions_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
