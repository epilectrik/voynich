#!/usr/bin/env python3
"""
Analyze HT token affinity for specific prefix families in Currier A.

Questions:
1. What prefix families appear adjacent to HT tokens?
2. Are certain prefixes enriched/depleted near HT?
3. What's the dominant prefix of blocks containing HT?
"""

import sys
from collections import Counter, defaultdict

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer/parsing')
from currier_a import parse_currier_a_token, MARKER_FAMILIES

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'

# HT prefixes (from C347)
HT_PREFIXES = {'yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc', 'ta', 'do'}
DA_PREFIXES = {'da', 'dal', 'dam', 'dan', 'dar'}


def get_prefix(token):
    """Get normalized prefix family for a token."""
    token_lower = token.lower()
    result = parse_currier_a_token(token)

    if result.prefix:
        pf = result.prefix
        # Normalize extended prefixes
        if len(pf) == 3 and pf.endswith('ch'):
            return 'ch'
        elif len(pf) == 3 and pf.endswith('sh'):
            return 'sh'
        return pf
    return None


def is_da(token):
    """Check if token is DA family."""
    token_lower = token.lower()
    result = parse_currier_a_token(token)
    if result.prefix in DA_PREFIXES:
        return True
    if token_lower.startswith('daiin') or token_lower.startswith('dain'):
        return True
    return result.prefix and result.prefix.startswith('da')


def is_ht(token):
    """Check if token is HT."""
    token_lower = token.lower()
    result = parse_currier_a_token(token)

    # Skip DA
    if is_da(token):
        return False

    # Check HT prefix
    for ht_pf in HT_PREFIXES:
        if token_lower.startswith(ht_pf) and not result.is_prefix_legal:
            return True
    return False


def load_entries():
    """Load Currier A entries."""
    entries = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        current = None

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                language = parts[6].strip('"').strip()
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                if language != 'A':
                    continue

                key = f"{folio}_{line_num}"

                if current is None or current['key'] != key:
                    if current and current['tokens']:
                        entries.append(current)
                    current = {'key': key, 'tokens': []}

                current['tokens'].append(word)

        if current and current['tokens']:
            entries.append(current)

    return entries


def analyze_ht_adjacency(entries):
    """Analyze what prefixes appear adjacent to HT tokens."""

    # Counters for tokens BEFORE HT
    before_ht = Counter()
    before_ht_prefix = Counter()

    # Counters for tokens AFTER HT
    after_ht = Counter()
    after_ht_prefix = Counter()

    # Baseline: all token prefixes
    all_prefixes = Counter()

    # Block-level: dominant prefix of blocks containing HT
    ht_block_prefixes = Counter()
    non_ht_block_prefixes = Counter()

    total_ht = 0

    for entry in entries:
        tokens = entry['tokens']

        # Count all prefixes for baseline
        for t in tokens:
            pf = get_prefix(t)
            if pf and pf not in DA_PREFIXES:
                all_prefixes[pf] += 1

        # Find HT positions
        for i, token in enumerate(tokens):
            if is_ht(token):
                total_ht += 1

                # Token before HT
                if i > 0:
                    prev = tokens[i-1]
                    before_ht[prev] += 1
                    pf = get_prefix(prev)
                    if pf:
                        before_ht_prefix[pf] += 1

                # Token after HT
                if i < len(tokens) - 1:
                    next_t = tokens[i+1]
                    after_ht[next_t] += 1
                    pf = get_prefix(next_t)
                    if pf:
                        after_ht_prefix[pf] += 1

        # Block-level analysis: segment by DA
        blocks = []
        current_block = []
        for t in tokens:
            if is_da(t):
                if current_block:
                    blocks.append(current_block)
                    current_block = []
            else:
                current_block.append(t)
        if current_block:
            blocks.append(current_block)

        # For each block, determine dominant prefix and HT presence
        for block in blocks:
            prefix_counts = Counter()
            has_ht = False
            for t in block:
                if is_ht(t):
                    has_ht = True
                else:
                    pf = get_prefix(t)
                    if pf:
                        prefix_counts[pf] += 1

            if prefix_counts:
                dominant = prefix_counts.most_common(1)[0][0]
                if has_ht:
                    ht_block_prefixes[dominant] += 1
                else:
                    non_ht_block_prefixes[dominant] += 1

    return {
        'total_ht': total_ht,
        'before_prefix': before_ht_prefix,
        'after_prefix': after_ht_prefix,
        'all_prefixes': all_prefixes,
        'ht_block_prefixes': ht_block_prefixes,
        'non_ht_block_prefixes': non_ht_block_prefixes
    }


def report(results):
    """Report findings."""
    print("=" * 70)
    print("HT TOKEN AFFINITY FOR PREFIX FAMILIES")
    print("=" * 70)

    print(f"\nTotal HT tokens analyzed: {results['total_ht']:,}")

    # Adjacency analysis
    print("\n" + "-" * 60)
    print("PREFIX IMMEDIATELY BEFORE HT")
    print("-" * 60)

    total_before = sum(results['before_prefix'].values())
    total_all = sum(results['all_prefixes'].values())

    print(f"\n{'Prefix':<10} {'Before HT':<12} {'Before %':<10} {'Baseline %':<12} {'Enrichment':<12}")
    print("-" * 60)

    core_prefixes = ['ch', 'sh', 'qo', 'ok', 'ot', 'ol', 'ct', 'da']

    for pf in core_prefixes:
        before = results['before_prefix'].get(pf, 0)
        baseline = results['all_prefixes'].get(pf, 0)

        before_pct = 100 * before / total_before if total_before > 0 else 0
        baseline_pct = 100 * baseline / total_all if total_all > 0 else 0
        enrichment = before_pct / baseline_pct if baseline_pct > 0 else 0

        marker = "**" if enrichment > 1.3 else ("--" if enrichment < 0.7 else "")
        print(f"{pf:<10} {before:<12} {before_pct:<10.1f} {baseline_pct:<12.1f} {enrichment:<10.2f}x {marker}")

    # After HT
    print("\n" + "-" * 60)
    print("PREFIX IMMEDIATELY AFTER HT")
    print("-" * 60)

    total_after = sum(results['after_prefix'].values())

    print(f"\n{'Prefix':<10} {'After HT':<12} {'After %':<10} {'Baseline %':<12} {'Enrichment':<12}")
    print("-" * 60)

    for pf in core_prefixes:
        after = results['after_prefix'].get(pf, 0)
        baseline = results['all_prefixes'].get(pf, 0)

        after_pct = 100 * after / total_after if total_after > 0 else 0
        baseline_pct = 100 * baseline / total_all if total_all > 0 else 0
        enrichment = after_pct / baseline_pct if baseline_pct > 0 else 0

        marker = "**" if enrichment > 1.3 else ("--" if enrichment < 0.7 else "")
        print(f"{pf:<10} {after:<12} {after_pct:<10.1f} {baseline_pct:<12.1f} {enrichment:<10.2f}x {marker}")

    # Block-level
    print("\n" + "-" * 60)
    print("BLOCKS WITH HT vs WITHOUT HT (by dominant prefix)")
    print("-" * 60)

    total_ht_blocks = sum(results['ht_block_prefixes'].values())
    total_non_ht_blocks = sum(results['non_ht_block_prefixes'].values())

    print(f"\n{'Prefix':<10} {'HT Blocks':<12} {'HT %':<10} {'Non-HT %':<12} {'Ratio':<12}")
    print("-" * 60)

    for pf in core_prefixes:
        ht_blocks = results['ht_block_prefixes'].get(pf, 0)
        non_ht_blocks = results['non_ht_block_prefixes'].get(pf, 0)

        ht_pct = 100 * ht_blocks / total_ht_blocks if total_ht_blocks > 0 else 0
        non_ht_pct = 100 * non_ht_blocks / total_non_ht_blocks if total_non_ht_blocks > 0 else 0
        ratio = ht_pct / non_ht_pct if non_ht_pct > 0 else 0

        marker = "**" if ratio > 1.3 else ("--" if ratio < 0.7 else "")
        print(f"{pf:<10} {ht_blocks:<12} {ht_pct:<10.1f} {non_ht_pct:<12.1f} {ratio:<10.2f}x {marker}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Find enriched/depleted
    before_enriched = []
    before_depleted = []
    for pf in core_prefixes:
        before = results['before_prefix'].get(pf, 0)
        baseline = results['all_prefixes'].get(pf, 0)
        before_pct = 100 * before / total_before if total_before > 0 else 0
        baseline_pct = 100 * baseline / total_all if total_all > 0 else 0
        enrichment = before_pct / baseline_pct if baseline_pct > 0 else 0
        if enrichment > 1.3:
            before_enriched.append((pf, enrichment))
        elif enrichment < 0.7:
            before_depleted.append((pf, enrichment))

    print(f"\nEnriched BEFORE HT: {', '.join(f'{pf} ({e:.2f}x)' for pf, e in before_enriched) if before_enriched else 'none'}")
    print(f"Depleted BEFORE HT: {', '.join(f'{pf} ({e:.2f}x)' for pf, e in before_depleted) if before_depleted else 'none'}")


if __name__ == "__main__":
    entries = load_entries()
    print(f"Loaded {len(entries)} entries")
    results = analyze_ht_adjacency(entries)
    report(results)
