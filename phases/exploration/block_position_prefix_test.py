#!/usr/bin/env python3
"""
Statistical test for block-position prefix preferences.

Initial finding from record_structure_analysis.py:
- qo/sh prefer FIRST block position
- ch/ct prefer LAST block position

This script validates with chi-square test.
"""

import sys
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import chi2_contingency

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer/parsing')
from currier_a import parse_currier_a_token, MARKER_FAMILIES

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'

# DA prefix detection
DA_PREFIXES = {'da', 'dal', 'dam', 'dan', 'dar'}


def is_da_token(token):
    result = parse_currier_a_token(token)
    if result.prefix in DA_PREFIXES:
        return True
    if token.lower().startswith('daiin') or token.lower().startswith('dain'):
        return True
    return result.prefix and result.prefix.startswith('da')


def load_currier_a_entries():
    """Load Currier A entries."""
    entries = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        current_entry = None

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
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
                        entries.append(current_entry)
                    current_entry = {
                        'key': key,
                        'folio': folio,
                        'section': section,
                        'tokens': []
                    }

                current_entry['tokens'].append(word)

        if current_entry is not None and current_entry['tokens']:
            entries.append(current_entry)

    return entries


def segment_by_da(tokens):
    """Segment tokens into blocks using DA as delimiter."""
    blocks = []
    current = []

    for token in tokens:
        if is_da_token(token):
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(token)

    if current:
        blocks.append(current)

    return blocks


def get_dominant_prefix(tokens):
    """Get the most common prefix in a list of tokens."""
    prefixes = Counter()
    for token in tokens:
        result = parse_currier_a_token(token)
        if result.prefix:
            # Normalize extended prefixes
            pf = result.prefix
            if pf in ['dch', 'pch', 'kch', 'fch', 'sch', 'tch', 'rch', 'lch']:
                pf = pf[1:]  # Map to base ch
            prefixes[pf] += 1

    if prefixes:
        return prefixes.most_common(1)[0][0]
    return None


def main():
    print("=" * 70)
    print("BLOCK POSITION PREFIX PREFERENCE TEST")
    print("=" * 70)

    entries = load_currier_a_entries()
    print(f"\nLoaded {len(entries)} Currier A entries")

    # Only analyze multi-block entries (2+ blocks)
    multi_block_entries = []

    for entry in entries:
        blocks = segment_by_da(entry['tokens'])
        if len(blocks) >= 2:
            multi_block_entries.append({
                'id': entry['key'],
                'section': entry['section'],
                'blocks': blocks
            })

    print(f"Entries with 2+ blocks: {len(multi_block_entries)}")

    # Count dominant prefix by position (first vs last)
    first_block_prefixes = Counter()
    last_block_prefixes = Counter()
    middle_block_prefixes = Counter()

    for entry in multi_block_entries:
        blocks = entry['blocks']

        # First block
        first_pf = get_dominant_prefix(blocks[0])
        if first_pf:
            first_block_prefixes[first_pf] += 1

        # Last block
        last_pf = get_dominant_prefix(blocks[-1])
        if last_pf:
            last_block_prefixes[last_pf] += 1

        # Middle blocks (if 3+ blocks)
        if len(blocks) >= 3:
            for block in blocks[1:-1]:
                mid_pf = get_dominant_prefix(block)
                if mid_pf:
                    middle_block_prefixes[mid_pf] += 1

    # Display raw counts
    print("\n" + "-" * 60)
    print("Raw prefix counts by position:")
    print("-" * 60)

    all_prefixes = set(first_block_prefixes.keys()) | set(last_block_prefixes.keys())
    core_prefixes = ['ch', 'sh', 'qo', 'ct', 'ok', 'ot', 'ol']  # Main markers

    print(f"\n{'Prefix':<10} {'First':<10} {'Last':<10} {'Middle':<10}")
    print("-" * 40)

    first_total = sum(first_block_prefixes.values())
    last_total = sum(last_block_prefixes.values())
    middle_total = sum(middle_block_prefixes.values())

    for pf in core_prefixes:
        first_ct = first_block_prefixes.get(pf, 0)
        last_ct = last_block_prefixes.get(pf, 0)
        mid_ct = middle_block_prefixes.get(pf, 0)
        print(f"{pf:<10} {first_ct:<10} {last_ct:<10} {mid_ct:<10}")

    # Percentages
    print("\n" + "-" * 60)
    print("Percentage distribution by position:")
    print("-" * 60)

    print(f"\n{'Prefix':<10} {'First %':<12} {'Last %':<12} {'Middle %':<12} {'Delta (L-F)':<12}")
    print("-" * 60)

    deltas = {}
    for pf in core_prefixes:
        first_pct = 100 * first_block_prefixes.get(pf, 0) / first_total if first_total > 0 else 0
        last_pct = 100 * last_block_prefixes.get(pf, 0) / last_total if last_total > 0 else 0
        mid_pct = 100 * middle_block_prefixes.get(pf, 0) / middle_total if middle_total > 0 else 0
        delta = last_pct - first_pct
        deltas[pf] = delta
        print(f"{pf:<10} {first_pct:>8.1f}%    {last_pct:>8.1f}%    {mid_pct:>8.1f}%    {delta:>+8.1f}%")

    # Chi-square test: first vs last
    print("\n" + "-" * 60)
    print("Chi-square test: First position vs Last position")
    print("-" * 60)

    # Build contingency table for major prefixes
    table_prefixes = ['ch', 'sh', 'qo', 'ct', 'ok', 'ot']
    contingency = []

    for pf in table_prefixes:
        contingency.append([
            first_block_prefixes.get(pf, 0),
            last_block_prefixes.get(pf, 0)
        ])

    contingency = np.array(contingency)
    chi2, p, dof, expected = chi2_contingency(contingency)

    n = contingency.sum()
    min_dim = min(contingency.shape) - 1
    v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0

    print(f"\nContingency table (rows=prefixes, cols=position):")
    print(f"{'Prefix':<10} {'First':<10} {'Last':<10}")
    for i, pf in enumerate(table_prefixes):
        print(f"{pf:<10} {contingency[i,0]:<10} {contingency[i,1]:<10}")

    print(f"\nchi2 = {chi2:.1f}")
    print(f"p-value = {p:.2e}")
    print(f"Cramer's V = {v:.3f}")

    if p < 0.001:
        print("\n** RESULT: HIGHLY SIGNIFICANT **")
        print("Prefix distribution differs between first and last block positions.")
    elif p < 0.05:
        print("\n** RESULT: SIGNIFICANT **")
    else:
        print("\n** RESULT: NOT SIGNIFICANT **")

    # Summary of preferences
    print("\n" + "=" * 60)
    print("SUMMARY: POSITIONAL PREFIX PREFERENCES")
    print("=" * 60)

    first_preferring = [pf for pf, d in deltas.items() if d < -3.0]
    last_preferring = [pf for pf, d in deltas.items() if d > 3.0]

    print(f"\nFIRST-block preferring (delta < -3%): {', '.join(first_preferring) if first_preferring else 'none'}")
    print(f"LAST-block preferring (delta > +3%): {', '.join(last_preferring) if last_preferring else 'none'}")

    # Section breakdown
    print("\n" + "-" * 60)
    print("Section breakdown (first vs last, ch only):")
    print("-" * 60)

    for section in ['H', 'P', 'T']:
        section_entries = [e for e in multi_block_entries if e['section'] == section]
        if not section_entries:
            continue

        first_ch = sum(1 for e in section_entries if get_dominant_prefix(e['blocks'][0]) == 'ch')
        last_ch = sum(1 for e in section_entries if get_dominant_prefix(e['blocks'][-1]) == 'ch')
        total = len(section_entries)

        first_pct = 100 * first_ch / total
        last_pct = 100 * last_ch / total

        print(f"Section {section}: ch in first={first_pct:.1f}%, ch in last={last_pct:.1f}%, delta={last_pct-first_pct:+.1f}%")


if __name__ == "__main__":
    main()
