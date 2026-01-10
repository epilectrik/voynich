#!/usr/bin/env python
"""
Sister-Pair Micro-Conditioning Analysis.

Priority 3 investigation after DA punctuation and MIDDLE census.

Existing constraints:
- C408: ch-sh/ok-ot form EQUIVALENCE CLASSES
- C409: Sister pairs MUTUALLY EXCLUSIVE but substitutable
- C410: Sister choice is SECTION-CONDITIONED
- C412: ch-preference anticorrelated with qo-escape density

New questions:
1. Does MIDDLE influence sister choice?
2. Does position within entry matter?
3. Does DA context (post-DA position) affect choice?
4. Do certain suffixes prefer one sister?
5. Does adjacent token context influence choice?

Goal: Identify micro-level conditioning factors beyond section.
"""
import sys
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import parse_currier_a_token, MARKER_FAMILIES

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'

# Sister pairs
SISTER_PAIRS = {
    'ch': 'sh', 'sh': 'ch',
    'ok': 'ot', 'ot': 'ok'
}

CH_SH = {'ch', 'sh'}
OK_OT = {'ok', 'ot'}


def load_currier_a_entries():
    """Load Currier A entries with full metadata."""
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
                        'line': line_num,
                        'tokens': []
                    }

                current_entry['tokens'].append(word)

        if current_entry is not None and current_entry['tokens']:
            entries.append(current_entry)

    return entries


def is_da_token(token):
    return token.lower().startswith('da')


def get_sister_pair(prefix):
    """Return which sister pair this prefix belongs to, or None."""
    if prefix in CH_SH:
        return 'ch-sh'
    elif prefix in OK_OT:
        return 'ok-ot'
    return None


def cramers_v(contingency_table):
    """Calculate Cramer's V for effect size."""
    chi2, p, dof, expected = chi2_contingency(contingency_table)
    n = contingency_table.sum()
    min_dim = min(contingency_table.shape) - 1
    if min_dim == 0 or n == 0:
        return 0
    return np.sqrt(chi2 / (n * min_dim))


# =============================================================================
# TEST 1: SECTION CONDITIONING (BASELINE - CONFIRM C410)
# =============================================================================

def test_section_conditioning(entries):
    """Confirm C410: Sister choice is section-conditioned."""

    print("=" * 70)
    print("TEST 1: SECTION CONDITIONING (Baseline - confirms C410)")
    print("=" * 70)

    # Count sister usage by section
    section_sister = defaultdict(Counter)

    for entry in entries:
        section = entry['section']
        for token in entry['tokens']:
            result = parse_currier_a_token(token)
            if result.prefix in SISTER_PAIRS:
                section_sister[section][result.prefix] += 1

    print(f"\n{'Section':<10} {'ch':<8} {'sh':<8} {'ch%':<10} {'ok':<8} {'ot':<8} {'ok%':<10}")
    print("-" * 62)

    for section in ['H', 'P', 'T']:
        counts = section_sister[section]
        ch, sh = counts.get('ch', 0), counts.get('sh', 0)
        ok, ot = counts.get('ok', 0), counts.get('ot', 0)
        ch_pct = 100 * ch / (ch + sh) if (ch + sh) > 0 else 0
        ok_pct = 100 * ok / (ok + ot) if (ok + ot) > 0 else 0
        print(f"{section:<10} {ch:<8} {sh:<8} {ch_pct:<10.1f} {ok:<8} {ot:<8} {ok_pct:<10.1f}")

    # Chi-square for ch-sh by section
    ch_sh_table = np.array([
        [section_sister['H']['ch'], section_sister['H']['sh']],
        [section_sister['P']['ch'], section_sister['P']['sh']],
        [section_sister['T']['ch'], section_sister['T']['sh']]
    ])

    chi2, p, dof, expected = chi2_contingency(ch_sh_table)
    v = cramers_v(ch_sh_table)

    print(f"\nch-sh by section: chi2={chi2:.1f}, p={p:.2e}, V={v:.3f}")

    return section_sister


# =============================================================================
# TEST 2: MIDDLE CONDITIONING
# =============================================================================

def test_middle_conditioning(entries):
    """Does MIDDLE influence sister choice?"""

    print("\n" + "=" * 70)
    print("TEST 2: MIDDLE CONDITIONING")
    print("=" * 70)
    print("\nQuestion: Do certain MIDDLEs prefer ch over sh (or ok over ot)?")

    # For each MIDDLE that appears with both sisters, compute preference
    middle_sister = defaultdict(Counter)

    for entry in entries:
        for token in entry['tokens']:
            result = parse_currier_a_token(token)
            if result.prefix in SISTER_PAIRS and result.middle:
                pair = get_sister_pair(result.prefix)
                middle_sister[(pair, result.middle)][result.prefix] += 1

    # Find MIDDLEs that appear with BOTH sisters of a pair
    shared_middles_ch_sh = []
    shared_middles_ok_ot = []

    for (pair, middle), counts in middle_sister.items():
        if pair == 'ch-sh' and 'ch' in counts and 'sh' in counts:
            total = counts['ch'] + counts['sh']
            if total >= 10:  # Minimum sample
                ch_pct = 100 * counts['ch'] / total
                shared_middles_ch_sh.append((middle, counts['ch'], counts['sh'], ch_pct, total))
        elif pair == 'ok-ot' and 'ok' in counts and 'ot' in counts:
            total = counts['ok'] + counts['ot']
            if total >= 10:
                ok_pct = 100 * counts['ok'] / total
                shared_middles_ok_ot.append((middle, counts['ok'], counts['ot'], ok_pct, total))

    print(f"\nMIDDLEs shared by ch-sh (n>=10): {len(shared_middles_ch_sh)}")

    if shared_middles_ch_sh:
        # Sort by deviation from 50%
        shared_middles_ch_sh.sort(key=lambda x: abs(x[3] - 50), reverse=True)

        print(f"\nTop 10 ch-sh MIDDLEs with strongest preference:")
        print(f"{'MIDDLE':<15} {'ch':<8} {'sh':<8} {'ch%':<10} {'total':<8}")
        print("-" * 49)
        for middle, ch, sh, pct, total in shared_middles_ch_sh[:10]:
            print(f"{middle:<15} {ch:<8} {sh:<8} {pct:<10.1f} {total:<8}")

        # Overall distribution of preferences
        preferences = [x[3] for x in shared_middles_ch_sh]
        print(f"\nch% distribution across shared MIDDLEs:")
        print(f"  Mean: {np.mean(preferences):.1f}%")
        print(f"  Std: {np.std(preferences):.1f}%")
        print(f"  Range: {min(preferences):.1f}% - {max(preferences):.1f}%")

        # Test if preferences are uniformly distributed or biased
        if len(preferences) >= 5:
            # Deviation from uniform (50%)
            deviations = [abs(p - 50) for p in preferences]
            mean_deviation = np.mean(deviations)
            print(f"  Mean deviation from 50%: {mean_deviation:.1f}%")

            if mean_deviation > 15:
                print("  -> STRONG MIDDLE-level conditioning detected")
            elif mean_deviation > 8:
                print("  -> MODERATE MIDDLE-level conditioning")
            else:
                print("  -> WEAK/NO MIDDLE-level conditioning")

    print(f"\nMIDDLEs shared by ok-ot (n>=10): {len(shared_middles_ok_ot)}")

    if shared_middles_ok_ot:
        shared_middles_ok_ot.sort(key=lambda x: abs(x[3] - 50), reverse=True)

        print(f"\nTop 10 ok-ot MIDDLEs with strongest preference:")
        print(f"{'MIDDLE':<15} {'ok':<8} {'ot':<8} {'ok%':<10} {'total':<8}")
        print("-" * 49)
        for middle, ok, ot, pct, total in shared_middles_ok_ot[:10]:
            print(f"{middle:<15} {ok:<8} {ot:<8} {pct:<10.1f} {total:<8}")

    return shared_middles_ch_sh, shared_middles_ok_ot


# =============================================================================
# TEST 3: POSITIONAL CONDITIONING
# =============================================================================

def test_positional_conditioning(entries):
    """Does position within entry affect sister choice?"""

    print("\n" + "=" * 70)
    print("TEST 3: POSITIONAL CONDITIONING")
    print("=" * 70)
    print("\nQuestion: Does position within entry affect sister choice?")

    # Position buckets: first, middle, last
    position_sister = defaultdict(Counter)

    for entry in entries:
        tokens = entry['tokens']
        n = len(tokens)

        for i, token in enumerate(tokens):
            result = parse_currier_a_token(token)
            if result.prefix in SISTER_PAIRS:
                # Determine position bucket
                if i == 0:
                    pos = 'first'
                elif i == n - 1:
                    pos = 'last'
                else:
                    pos = 'middle'

                position_sister[pos][result.prefix] += 1

    print(f"\n{'Position':<12} {'ch':<8} {'sh':<8} {'ch%':<10} {'ok':<8} {'ot':<8} {'ok%':<10}")
    print("-" * 66)

    for pos in ['first', 'middle', 'last']:
        counts = position_sister[pos]
        ch, sh = counts.get('ch', 0), counts.get('sh', 0)
        ok, ot = counts.get('ok', 0), counts.get('ot', 0)
        ch_pct = 100 * ch / (ch + sh) if (ch + sh) > 0 else 0
        ok_pct = 100 * ok / (ok + ot) if (ok + ot) > 0 else 0
        print(f"{pos:<12} {ch:<8} {sh:<8} {ch_pct:<10.1f} {ok:<8} {ot:<8} {ok_pct:<10.1f}")

    # Chi-square test
    ch_sh_table = np.array([
        [position_sister['first']['ch'], position_sister['first']['sh']],
        [position_sister['middle']['ch'], position_sister['middle']['sh']],
        [position_sister['last']['ch'], position_sister['last']['sh']]
    ])

    chi2, p, dof, expected = chi2_contingency(ch_sh_table)
    v = cramers_v(ch_sh_table)

    print(f"\nch-sh by position: chi2={chi2:.1f}, p={p:.2e}, V={v:.3f}")

    if v < 0.1:
        print("-> WEAK/NO positional conditioning")
    elif v < 0.2:
        print("-> SMALL positional effect")
    else:
        print("-> NOTABLE positional conditioning")

    return position_sister


# =============================================================================
# TEST 4: DA CONTEXT CONDITIONING
# =============================================================================

def test_da_context(entries):
    """Does position relative to DA affect sister choice?"""

    print("\n" + "=" * 70)
    print("TEST 4: DA CONTEXT CONDITIONING")
    print("=" * 70)
    print("\nQuestion: Does position relative to DA affect sister choice?")

    # Categories: immediately after DA, not after DA
    da_context = defaultdict(Counter)

    for entry in entries:
        tokens = entry['tokens']

        for i, token in enumerate(tokens):
            result = parse_currier_a_token(token)
            if result.prefix in SISTER_PAIRS:
                # Check if previous token was DA
                if i > 0 and is_da_token(tokens[i-1]):
                    context = 'post_DA'
                else:
                    context = 'not_post_DA'

                da_context[context][result.prefix] += 1

    print(f"\n{'Context':<15} {'ch':<8} {'sh':<8} {'ch%':<10} {'ok':<8} {'ot':<8} {'ok%':<10}")
    print("-" * 69)

    for ctx in ['post_DA', 'not_post_DA']:
        counts = da_context[ctx]
        ch, sh = counts.get('ch', 0), counts.get('sh', 0)
        ok, ot = counts.get('ok', 0), counts.get('ot', 0)
        ch_pct = 100 * ch / (ch + sh) if (ch + sh) > 0 else 0
        ok_pct = 100 * ok / (ok + ot) if (ok + ot) > 0 else 0
        print(f"{ctx:<15} {ch:<8} {sh:<8} {ch_pct:<10.1f} {ok:<8} {ot:<8} {ok_pct:<10.1f}")

    # Chi-square test for ch-sh
    ch_sh_table = np.array([
        [da_context['post_DA']['ch'], da_context['post_DA']['sh']],
        [da_context['not_post_DA']['ch'], da_context['not_post_DA']['sh']]
    ])

    chi2, p, dof, expected = chi2_contingency(ch_sh_table)
    v = cramers_v(ch_sh_table)

    print(f"\nch-sh by DA context: chi2={chi2:.1f}, p={p:.2e}, V={v:.3f}")

    return da_context


# =============================================================================
# TEST 5: SUFFIX CONDITIONING
# =============================================================================

def test_suffix_conditioning(entries):
    """Do certain suffixes prefer one sister over another?"""

    print("\n" + "=" * 70)
    print("TEST 5: SUFFIX CONDITIONING")
    print("=" * 70)
    print("\nQuestion: Do certain suffixes prefer ch over sh?")

    suffix_sister = defaultdict(Counter)

    for entry in entries:
        for token in entry['tokens']:
            result = parse_currier_a_token(token)
            if result.prefix in CH_SH and result.suffix:
                suffix_sister[result.suffix][result.prefix] += 1

    # Find suffixes that appear with both ch and sh
    shared_suffixes = []
    for suffix, counts in suffix_sister.items():
        if 'ch' in counts and 'sh' in counts:
            total = counts['ch'] + counts['sh']
            if total >= 20:  # Minimum sample
                ch_pct = 100 * counts['ch'] / total
                shared_suffixes.append((suffix, counts['ch'], counts['sh'], ch_pct, total))

    shared_suffixes.sort(key=lambda x: abs(x[3] - 50), reverse=True)

    print(f"\nSuffixes shared by ch-sh (n>=20): {len(shared_suffixes)}")
    print(f"\n{'SUFFIX':<12} {'ch':<8} {'sh':<8} {'ch%':<10} {'total':<8}")
    print("-" * 46)

    for suffix, ch, sh, pct, total in shared_suffixes[:15]:
        print(f"{suffix:<12} {ch:<8} {sh:<8} {pct:<10.1f} {total:<8}")

    if shared_suffixes:
        preferences = [x[3] for x in shared_suffixes]
        deviations = [abs(p - 50) for p in preferences]
        print(f"\nMean deviation from 50%: {np.mean(deviations):.1f}%")

        if np.mean(deviations) > 15:
            print("-> STRONG suffix-level conditioning")
        elif np.mean(deviations) > 8:
            print("-> MODERATE suffix-level conditioning")
        else:
            print("-> WEAK/NO suffix-level conditioning")

    return shared_suffixes


# =============================================================================
# TEST 6: ADJACENT TOKEN CONDITIONING
# =============================================================================

def test_adjacent_conditioning(entries):
    """Does the preceding token's prefix influence sister choice?"""

    print("\n" + "=" * 70)
    print("TEST 6: ADJACENT TOKEN CONDITIONING")
    print("=" * 70)
    print("\nQuestion: Does preceding token's prefix influence sister choice?")

    prev_prefix_sister = defaultdict(Counter)

    for entry in entries:
        tokens = entry['tokens']

        for i, token in enumerate(tokens):
            result = parse_currier_a_token(token)
            if result.prefix in CH_SH and i > 0:
                # Get previous token's prefix
                prev_result = parse_currier_a_token(tokens[i-1])
                if prev_result.prefix:
                    prev_prefix_sister[prev_result.prefix][result.prefix] += 1

    print(f"\n{'Prev prefix':<12} {'ch':<8} {'sh':<8} {'ch%':<10} {'total':<8}")
    print("-" * 46)

    results = []
    for prev_prefix in sorted(MARKER_FAMILIES):
        counts = prev_prefix_sister[prev_prefix]
        ch, sh = counts.get('ch', 0), counts.get('sh', 0)
        total = ch + sh
        if total >= 20:
            ch_pct = 100 * ch / total
            results.append((prev_prefix, ch, sh, ch_pct, total))
            print(f"{prev_prefix:<12} {ch:<8} {sh:<8} {ch_pct:<10.1f} {total:<8}")

    if results:
        preferences = [x[3] for x in results]
        print(f"\nch% range by preceding prefix: {min(preferences):.1f}% - {max(preferences):.1f}%")
        print(f"Spread: {max(preferences) - min(preferences):.1f}%")

        if max(preferences) - min(preferences) > 20:
            print("-> NOTABLE adjacent-prefix conditioning")
        else:
            print("-> WEAK adjacent-prefix conditioning")

    return prev_prefix_sister


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("Loading Currier A entries...")
    entries = load_currier_a_entries()
    print(f"Loaded {len(entries)} entries\n")

    section_data = test_section_conditioning(entries)
    middle_ch_sh, middle_ok_ot = test_middle_conditioning(entries)
    position_data = test_positional_conditioning(entries)
    da_data = test_da_context(entries)
    suffix_data = test_suffix_conditioning(entries)
    adjacent_data = test_adjacent_conditioning(entries)

    print("\n" + "=" * 70)
    print("SUMMARY: SISTER-PAIR CONDITIONING FACTORS")
    print("=" * 70)
    print("""
Conditioning hierarchy (strongest to weakest):

1. SECTION (C410 confirmed) - Primary driver
2. [Results from tests above]
3. [Results from tests above]
...

Key finding:
Sister choice is primarily section-conditioned, with [X] as secondary factor.
""")
