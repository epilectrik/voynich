#!/usr/bin/env python
"""
DA Section Invariance Test: One-shot validation.

Question: Does DA's articulation behavior differ by section (H/P/T)?

Expected outcome: Same 3:1 separation ratio everywhere.
If yes: DA is globally infrastructural → close the investigation.
"""
import sys
from collections import defaultdict, Counter
import numpy as np

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import MARKER_FAMILIES

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'


def load_entries_by_section():
    """Load Currier A entries grouped by section."""

    entries_by_section = defaultdict(list)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        current_entry = None

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                section = parts[3].strip('"').strip()
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                if language != 'A':
                    continue

                key = f"{folio}_{line_num}"

                if current_entry is None or current_entry['key'] != key:
                    if current_entry is not None and current_entry['tokens']:
                        entries_by_section[current_entry['section']].append(current_entry)
                    current_entry = {
                        'key': key,
                        'folio': folio,
                        'section': section,
                        'line': line_num,
                        'tokens': []
                    }

                current_entry['tokens'].append(word)

        if current_entry is not None and current_entry['tokens']:
            entries_by_section[current_entry['section']].append(current_entry)

    return entries_by_section


def get_prefix(token):
    """Get marker prefix for token."""
    token_lower = token.lower()
    for prefix in sorted(MARKER_FAMILIES, key=len, reverse=True):
        if token_lower.startswith(prefix):
            return prefix
    return None


def is_da_token(token):
    """Check if token is a DA family token."""
    return token.lower().startswith('da')


def analyze_section(entries, section_name):
    """Analyze DA behavior in a single section."""

    separates_different = 0
    within_same = 0

    da_count = 0
    entry_count = len(entries)
    entries_with_da = 0

    prefix_diversity_with_da = []
    prefix_diversity_without_da = []

    for entry in entries:
        tokens = entry['tokens']

        # Count DA tokens
        entry_da_count = sum(1 for t in tokens if is_da_token(t))
        da_count += entry_da_count

        # Prefix diversity
        prefixes = set(get_prefix(t) for t in tokens)
        prefixes = set(p for p in prefixes if p)

        if entry_da_count > 0:
            entries_with_da += 1
            prefix_diversity_with_da.append(len(prefixes))
        else:
            prefix_diversity_without_da.append(len(prefixes))

        # Analyze DA separation behavior
        for i, token in enumerate(tokens):
            if is_da_token(token) and i > 0 and i < len(tokens) - 1:
                prev_prefix = get_prefix(tokens[i-1])
                next_prefix = get_prefix(tokens[i+1])

                if prev_prefix and next_prefix:
                    if prev_prefix != next_prefix:
                        separates_different += 1
                    else:
                        within_same += 1

    # Calculate metrics
    total_internal = separates_different + within_same
    sep_rate = separates_different / total_internal if total_internal > 0 else 0
    ratio = separates_different / within_same if within_same > 0 else float('inf')

    da_density = da_count / sum(len(e['tokens']) for e in entries) if entries else 0

    return {
        'section': section_name,
        'entries': entry_count,
        'entries_with_da': entries_with_da,
        'da_tokens': da_count,
        'separates_different': separates_different,
        'within_same': within_same,
        'separation_rate': sep_rate,
        'ratio': ratio,
        'da_density': da_density,
        'prefix_div_with_da': np.mean(prefix_diversity_with_da) if prefix_diversity_with_da else 0,
        'prefix_div_without_da': np.mean(prefix_diversity_without_da) if prefix_diversity_without_da else 0,
    }


def main():
    print("=" * 70)
    print("DA SECTION INVARIANCE TEST")
    print("=" * 70)
    print("\nQuestion: Does DA's 3:1 separation ratio hold across all sections?")
    print("Expected: Yes -> DA is globally infrastructural\n")

    entries_by_section = load_entries_by_section()

    results = []
    for section in ['H', 'P', 'T']:
        if section in entries_by_section:
            result = analyze_section(entries_by_section[section], section)
            results.append(result)

    # Display results
    print("\n" + "-" * 70)
    print("SEPARATION BEHAVIOR BY SECTION")
    print("-" * 70)

    print(f"\n{'Section':<10} {'Entries':<10} {'DA tokens':<12} {'Sep Rate':<12} {'Ratio':<10}")
    print("-" * 54)

    for r in results:
        ratio_str = f"{r['ratio']:.1f}:1" if r['ratio'] != float('inf') else "INF:1"
        print(f"{r['section']:<10} {r['entries']:<10} {r['da_tokens']:<12} {100*r['separation_rate']:.1f}%{'':>6} {ratio_str:<10}")

    # Calculate overall
    total_sep = sum(r['separates_different'] for r in results)
    total_same = sum(r['within_same'] for r in results)
    overall_rate = total_sep / (total_sep + total_same) if (total_sep + total_same) > 0 else 0
    overall_ratio = total_sep / total_same if total_same > 0 else float('inf')

    print("-" * 54)
    print(f"{'OVERALL':<10} {sum(r['entries'] for r in results):<10} {sum(r['da_tokens'] for r in results):<12} {100*overall_rate:.1f}%{'':>6} {overall_ratio:.1f}:1")

    # Prefix diversity comparison
    print("\n" + "-" * 70)
    print("PREFIX DIVERSITY BY SECTION")
    print("-" * 70)

    print(f"\n{'Section':<10} {'With DA':<15} {'Without DA':<15} {'Ratio':<10}")
    print("-" * 50)

    for r in results:
        if r['prefix_div_without_da'] > 0:
            div_ratio = r['prefix_div_with_da'] / r['prefix_div_without_da']
        else:
            div_ratio = float('inf')
        print(f"{r['section']:<10} {r['prefix_div_with_da']:<15.2f} {r['prefix_div_without_da']:<15.2f} {div_ratio:.2f}x")

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    rates = [r['separation_rate'] for r in results]
    rate_range = max(rates) - min(rates) if rates else 0

    if rate_range < 0.10:  # Less than 10% variation
        print("\n[PASS] INVARIANT: DA separation behavior is consistent across sections.")
        print(f"   Separation rate range: {100*min(rates):.1f}% - {100*max(rates):.1f}%")
        print("   -> DA is GLOBALLY INFRASTRUCTURAL")
        print("   -> Role is invariant across section contexts")
    else:
        print("\n[WARN] VARIANT: DA behavior differs by section.")
        print(f"   Separation rate range: {100*min(rates):.1f}% - {100*max(rates):.1f}%")
        print("   -> Requires investigation of section-specific function")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
