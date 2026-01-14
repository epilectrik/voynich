"""
Single-Token A Line Analysis

Question: Are single-token A lines structurally distinct from multi-token lines?

If DISTINCT: They may serve a different function (headers, anchors, references)
If SAME: They're just simple cases of compound-input (batch of 1)

Tests:
1. Positional patterns (folio-initial? line position in folio?)
2. Vocabulary comparison (different tokens used?)
3. Morphological profile (prefix/suffix distribution)
4. Folio distribution (concentrated or uniform?)
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"


def load_a_lines():
    """Load all Currier A lines with metadata."""
    a_lines = []

    # Group tokens by (folio, line_num)
    line_tokens = defaultdict(list)
    line_meta = {}

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            lang = row.get('language', '')
            if lang != 'A':
                continue

            folio = row['folio']
            line_num = row.get('line_number', '0')
            line_init = row.get('line_initial', '0')

            try:
                line_num = int(line_num)
            except:
                line_num = 0

            key = (folio, line_num)
            line_tokens[key].append(token)

            if key not in line_meta:
                line_meta[key] = {
                    'folio': folio,
                    'line_num': line_num,
                    'is_line_initial': line_init == '1'
                }

    # Build line records
    for key, tokens in line_tokens.items():
        meta = line_meta[key]
        a_lines.append({
            'folio': meta['folio'],
            'line_num': meta['line_num'],
            'tokens': tokens,
            'length': len(tokens),
            'is_single': len(tokens) == 1
        })

    return a_lines


def get_folio_max_lines(a_lines):
    """Get max line number per folio for normalization."""
    folio_max = defaultdict(int)
    for line in a_lines:
        folio_max[line['folio']] = max(folio_max[line['folio']], line['line_num'])
    return folio_max


def test_positional_patterns(a_lines, folio_max):
    """Test 1: Are single-token lines positionally distinct?"""
    print("="*70)
    print("TEST 1: POSITIONAL PATTERNS")
    print("="*70)

    single_lines = [l for l in a_lines if l['is_single']]
    multi_lines = [l for l in a_lines if not l['is_single']]

    print(f"\nSingle-token lines: {len(single_lines)}")
    print(f"Multi-token lines: {len(multi_lines)}")

    # Normalized position within folio (0 = first line, 1 = last line)
    single_positions = []
    multi_positions = []

    for line in single_lines:
        max_line = folio_max[line['folio']]
        if max_line > 0:
            norm_pos = line['line_num'] / max_line
            single_positions.append(norm_pos)

    for line in multi_lines:
        max_line = folio_max[line['folio']]
        if max_line > 0:
            norm_pos = line['line_num'] / max_line
            multi_positions.append(norm_pos)

    print(f"\nNormalized position in folio:")
    print(f"  Single-token: mean={np.mean(single_positions):.3f} ± {np.std(single_positions):.3f}")
    print(f"  Multi-token:  mean={np.mean(multi_positions):.3f} ± {np.std(multi_positions):.3f}")

    stat, p = stats.mannwhitneyu(single_positions, multi_positions, alternative='two-sided')
    print(f"  Mann-Whitney U p = {p:.4f}")
    print(f"  Interpretation: {'POSITIONALLY DISTINCT' if p < 0.05 else 'NO POSITIONAL DIFFERENCE'}")

    # Check folio-initial concentration
    single_initial = sum(1 for l in single_lines if l['line_num'] <= 2)
    multi_initial = sum(1 for l in multi_lines if l['line_num'] <= 2)

    single_initial_rate = single_initial / len(single_lines) if single_lines else 0
    multi_initial_rate = multi_initial / len(multi_lines) if multi_lines else 0

    print(f"\nFolio-initial (line 1-2) concentration:")
    print(f"  Single-token: {single_initial_rate:.1%} ({single_initial}/{len(single_lines)})")
    print(f"  Multi-token:  {multi_initial_rate:.1%} ({multi_initial}/{len(multi_lines)})")

    return {
        'single_mean_pos': np.mean(single_positions),
        'multi_mean_pos': np.mean(multi_positions),
        'position_p': p,
        'single_initial_rate': single_initial_rate,
        'multi_initial_rate': multi_initial_rate
    }


def test_vocabulary(a_lines):
    """Test 2: Do single-token lines use different vocabulary?"""
    print("\n" + "="*70)
    print("TEST 2: VOCABULARY COMPARISON")
    print("="*70)

    single_tokens = []
    multi_tokens = []

    for line in a_lines:
        if line['is_single']:
            single_tokens.extend(line['tokens'])
        else:
            multi_tokens.extend(line['tokens'])

    single_vocab = set(single_tokens)
    multi_vocab = set(multi_tokens)

    overlap = single_vocab & multi_vocab
    single_only = single_vocab - multi_vocab

    print(f"\nVocabulary sizes:")
    print(f"  Single-token lines: {len(single_vocab)} unique tokens")
    print(f"  Multi-token lines:  {len(multi_vocab)} unique tokens")
    print(f"  Overlap: {len(overlap)} ({100*len(overlap)/len(single_vocab):.1f}% of single vocab)")
    print(f"  Single-only: {len(single_only)} ({100*len(single_only)/len(single_vocab):.1f}% of single vocab)")

    # Top tokens in each category
    single_counts = Counter(single_tokens)
    multi_counts = Counter(multi_tokens)

    print(f"\nTop 10 single-token line tokens:")
    for token, count in single_counts.most_common(10):
        multi_count = multi_counts.get(token, 0)
        ratio = count / (multi_count + 1)
        print(f"  {token}: {count} (vs {multi_count} in multi, ratio={ratio:.2f})")

    # Tokens exclusive to single-token lines
    if single_only:
        print(f"\nTokens appearing ONLY in single-token lines:")
        exclusive_counts = [(t, single_counts[t]) for t in single_only]
        for token, count in sorted(exclusive_counts, key=lambda x: -x[1])[:10]:
            print(f"  {token}: {count}")

    return {
        'single_vocab_size': len(single_vocab),
        'multi_vocab_size': len(multi_vocab),
        'overlap': len(overlap),
        'single_only': len(single_only),
        'overlap_rate': len(overlap) / len(single_vocab) if single_vocab else 0
    }


def test_morphology(a_lines):
    """Test 3: Do single-token lines have different morphological profile?"""
    print("\n" + "="*70)
    print("TEST 3: MORPHOLOGICAL PROFILE")
    print("="*70)

    single_tokens = []
    multi_tokens = []

    for line in a_lines:
        if line['is_single']:
            single_tokens.extend(line['tokens'])
        else:
            multi_tokens.extend(line['tokens'])

    # Prefix analysis (first 2 chars)
    def get_prefix(token):
        if len(token) >= 2:
            return token[:2]
        return token

    single_prefixes = Counter(get_prefix(t) for t in single_tokens)
    multi_prefixes = Counter(get_prefix(t) for t in multi_tokens)

    # Normalize to proportions
    single_total = sum(single_prefixes.values())
    multi_total = sum(multi_prefixes.values())

    print(f"\nPrefix distribution comparison:")
    print(f"{'Prefix':<10} {'Single %':<12} {'Multi %':<12} {'Ratio':<10}")
    print("-"*45)

    all_prefixes = set(single_prefixes.keys()) | set(multi_prefixes.keys())
    prefix_diffs = []

    for prefix in sorted(all_prefixes, key=lambda p: -single_prefixes.get(p, 0)):
        single_pct = 100 * single_prefixes.get(prefix, 0) / single_total
        multi_pct = 100 * multi_prefixes.get(prefix, 0) / multi_total
        ratio = single_pct / multi_pct if multi_pct > 0 else float('inf')

        if single_pct >= 1 or multi_pct >= 1:  # Only show meaningful prefixes
            prefix_diffs.append((prefix, single_pct, multi_pct, ratio))

    # Sort by ratio to find distinctive prefixes
    prefix_diffs.sort(key=lambda x: -x[3])

    print("\nPrefixes OVER-represented in single-token lines:")
    for prefix, s_pct, m_pct, ratio in prefix_diffs[:5]:
        if ratio > 1.2:
            print(f"  {prefix:<10} {s_pct:>6.1f}%     {m_pct:>6.1f}%     {ratio:.2f}x")

    print("\nPrefixes UNDER-represented in single-token lines:")
    for prefix, s_pct, m_pct, ratio in sorted(prefix_diffs, key=lambda x: x[3])[:5]:
        if ratio < 0.8:
            print(f"  {prefix:<10} {s_pct:>6.1f}%     {m_pct:>6.1f}%     {ratio:.2f}x")

    return {
        'single_prefixes': dict(single_prefixes.most_common(10)),
        'multi_prefixes': dict(multi_prefixes.most_common(10))
    }


def test_folio_distribution(a_lines):
    """Test 4: Are single-token lines concentrated in specific folios?"""
    print("\n" + "="*70)
    print("TEST 4: FOLIO DISTRIBUTION")
    print("="*70)

    single_by_folio = defaultdict(int)
    multi_by_folio = defaultdict(int)

    for line in a_lines:
        if line['is_single']:
            single_by_folio[line['folio']] += 1
        else:
            multi_by_folio[line['folio']] += 1

    all_folios = set(single_by_folio.keys()) | set(multi_by_folio.keys())

    # Calculate single-token rate per folio
    folio_rates = []
    for folio in all_folios:
        single = single_by_folio[folio]
        multi = multi_by_folio[folio]
        total = single + multi
        if total > 0:
            rate = single / total
            folio_rates.append((folio, single, multi, rate))

    # Sort by rate
    folio_rates.sort(key=lambda x: -x[3])

    print(f"\nFolios with highest single-token line rate:")
    print(f"{'Folio':<10} {'Single':<8} {'Multi':<8} {'Rate':<10}")
    print("-"*40)
    for folio, single, multi, rate in folio_rates[:10]:
        print(f"{folio:<10} {single:<8} {multi:<8} {rate:.1%}")

    # Overall uniformity test
    rates = [r[3] for r in folio_rates if r[1] + r[2] >= 5]  # Folios with 5+ lines

    if len(rates) > 1:
        mean_rate = np.mean(rates)
        std_rate = np.std(rates)
        cv = std_rate / mean_rate if mean_rate > 0 else 0

        print(f"\nDistribution uniformity (folios with 5+ lines):")
        print(f"  Mean single-token rate: {mean_rate:.1%}")
        print(f"  Std dev: {std_rate:.3f}")
        print(f"  Coefficient of variation: {cv:.2f}")
        print(f"  Interpretation: {'CONCENTRATED' if cv > 0.5 else 'UNIFORM'}")

    return {
        'n_folios_with_single': len([f for f in single_by_folio if single_by_folio[f] > 0]),
        'total_folios': len(all_folios),
        'top_folio': folio_rates[0] if folio_rates else None
    }


def main():
    print("Loading Currier A lines...")
    a_lines = load_a_lines()

    single_count = sum(1 for l in a_lines if l['is_single'])
    print(f"Total A lines: {len(a_lines)}")
    print(f"Single-token lines: {single_count} ({100*single_count/len(a_lines):.1f}%)")

    folio_max = get_folio_max_lines(a_lines)

    # Run tests
    pos_results = test_positional_patterns(a_lines, folio_max)
    vocab_results = test_vocabulary(a_lines)
    morph_results = test_morphology(a_lines)
    folio_results = test_folio_distribution(a_lines)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY: ARE SINGLE-TOKEN LINES STRUCTURALLY DISTINCT?")
    print("="*70)

    distinct_signals = 0

    if pos_results['position_p'] < 0.05:
        print("\n[X] POSITIONAL: Single-token lines are positionally distinct")
        distinct_signals += 1
    else:
        print("\n[ ] POSITIONAL: No significant positional difference")

    if vocab_results['overlap_rate'] < 0.7:
        print("[X] VOCABULARY: Single-token lines use substantially different vocabulary")
        distinct_signals += 1
    else:
        print("[ ] VOCABULARY: High vocabulary overlap with multi-token lines")

    if folio_results['n_folios_with_single'] < folio_results['total_folios'] * 0.5:
        print("[X] DISTRIBUTION: Single-token lines concentrated in specific folios")
        distinct_signals += 1
    else:
        print("[ ] DISTRIBUTION: Single-token lines spread across folios")

    print(f"\n{'='*70}")
    if distinct_signals >= 2:
        print("VERDICT: Single-token lines appear STRUCTURALLY DISTINCT")
        print("         May serve different function (headers, anchors, references)")
    else:
        print("VERDICT: Single-token lines appear to be SIMPLE CASES of same mechanism")
        print("         Likely just 'batch of 1' under C482")
    print("="*70)


if __name__ == '__main__':
    main()
