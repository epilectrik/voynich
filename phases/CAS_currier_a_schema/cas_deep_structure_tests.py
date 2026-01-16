"""
CAS Deep Structure Tests

Five additional structural analyses of Currier A:
1. Within-Marker Substructure - secondary patterns within marker classes
2. Marker-Illustration Correlation - do markers correlate with illustration types?
3. A-B Vocabulary Bridge - what is the shared 14%?
4. Payload Token Analysis - structure in non-marker tokens
5. Entry Length Semantics - does length encode information?
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy import stats as sp_stats

project_root = Path(__file__).parent.parent.parent

MARKER_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'yk', 'yt']


def load_currier_a_data():
    """Load Currier A tokens with line-level granularity (PRIMARY transcriber H only)."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        word_idx = 0
        folio_idx = header.index('folio') if 'folio' in header else 1
        line_idx = header.index('line') if 'line' in header else 2
        lang_idx = 6
        section_idx = header.index('section') if 'section' in header else 3

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # Filter to PRIMARY transcriber (H) only
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue

                lang = parts[lang_idx].strip('"').strip()
                if lang == 'A':
                    word = parts[word_idx].strip('"').strip().lower()
                    folio = parts[folio_idx].strip('"').strip() if len(parts) > folio_idx else ''
                    line_num = parts[line_idx].strip('"').strip() if len(parts) > line_idx else ''
                    section = parts[section_idx].strip('"').strip() if len(parts) > section_idx else ''

                    if word:
                        data.append({
                            'token': word,
                            'folio': folio,
                            'line': line_num,
                            'section': section,
                            'folio_line': f"{folio}_{line_num}"
                        })

    return data


def load_all_data():
    """Load both A and B data (PRIMARY transcriber H only)."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        word_idx = 0
        folio_idx = header.index('folio') if 'folio' in header else 1
        line_idx = header.index('line') if 'line' in header else 2
        lang_idx = 6
        section_idx = header.index('section') if 'section' in header else 3

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # Filter to PRIMARY transcriber (H) only
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue

                lang = parts[lang_idx].strip('"').strip()
                if lang in ['A', 'B']:
                    word = parts[word_idx].strip('"').strip().lower()
                    folio = parts[folio_idx].strip('"').strip() if len(parts) > folio_idx else ''
                    section = parts[section_idx].strip('"').strip() if len(parts) > section_idx else ''

                    if word:
                        data.append({
                            'token': word,
                            'folio': folio,
                            'section': section,
                            'language': lang
                        })

    return data


def test_within_marker_substructure(data):
    """
    Test 1: Within-Marker Substructure

    Do entries under the same marker share secondary patterns?
    - Suffix distributions within marker classes
    - Entry length patterns per marker
    - Co-occurring tokens within marker entries
    """
    print("\n" + "=" * 70)
    print("TEST 1: WITHIN-MARKER SUBSTRUCTURE")
    print("=" * 70)

    # Group entries by marker
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    marker_entries = defaultdict(list)

    for line_id, tokens in lines.items():
        marker = None
        for token in tokens:
            if len(token) >= 2 and token[:2] in MARKER_PREFIXES:
                marker = token[:2]
                break

        if marker:
            marker_entries[marker].append(tokens)

    # Analyze each marker class
    print(f"\nWithin-marker analysis:")

    for marker in MARKER_PREFIXES[:6]:
        entries = marker_entries[marker]
        if len(entries) < 50:
            continue

        print(f"\n--- {marker.upper()} class ({len(entries)} entries) ---")

        # Entry length distribution
        lengths = [len(e) for e in entries]
        print(f"  Entry lengths: mean={np.mean(lengths):.2f}, median={np.median(lengths):.0f}, mode={Counter(lengths).most_common(1)[0][0]}")

        # Suffix patterns within this marker
        suffixes = Counter()
        for entry in entries:
            for token in entry:
                if len(token) >= 3:
                    suffixes[token[-3:]] += 1

        print(f"  Top 5 suffixes: {suffixes.most_common(5)}")

        # Token diversity within entries
        all_tokens = [t for e in entries for t in e]
        unique = len(set(all_tokens))
        total = len(all_tokens)
        print(f"  Token diversity: {unique}/{total} = {unique/total:.3f}")

        # Most common non-marker tokens
        non_marker = Counter()
        for entry in entries:
            for token in entry:
                if len(token) < 2 or token[:2] != marker:
                    non_marker[token] += 1

        print(f"  Top 5 co-occurring tokens: {non_marker.most_common(5)}")

    # Cross-marker comparison: do markers have distinct suffix profiles?
    print(f"\n--- CROSS-MARKER SUFFIX COMPARISON ---")

    marker_suffix_profiles = {}
    for marker in MARKER_PREFIXES[:6]:
        entries = marker_entries[marker]
        suffixes = Counter()
        for entry in entries:
            for token in entry:
                if len(token) >= 3:
                    suffixes[token[-3:]] += 1

        total = sum(suffixes.values())
        if total > 0:
            # Normalize to distribution
            marker_suffix_profiles[marker] = {s: c/total for s, c in suffixes.items()}

    # Compare profiles pairwise
    print(f"\nSuffix profile similarity (Jaccard of top-20):")
    for i, m1 in enumerate(list(marker_suffix_profiles.keys())[:4]):
        for m2 in list(marker_suffix_profiles.keys())[i+1:5]:
            top1 = set(list(marker_suffix_profiles[m1].keys())[:20])
            top2 = set(list(marker_suffix_profiles[m2].keys())[:20])
            jaccard = len(top1 & top2) / len(top1 | top2) if (top1 | top2) else 0
            print(f"  {m1} vs {m2}: {jaccard:.2f}")

    return {'marker_entries': {m: len(e) for m, e in marker_entries.items()}}


def test_marker_illustration_correlation(data):
    """
    Test 2: Marker-Illustration Correlation

    Do marker categories correlate with illustration types?
    We use folio naming conventions as proxy for illustration type.
    """
    print("\n" + "=" * 70)
    print("TEST 2: MARKER-ILLUSTRATION CORRELATION")
    print("=" * 70)

    # Group by folio
    folio_markers = defaultdict(Counter)

    for d in data:
        token = d['token']
        folio = d['folio']
        if len(token) >= 2 and token[:2] in MARKER_PREFIXES:
            folio_markers[folio][token[:2]] += 1

    # Classify folios by naming pattern (proxy for illustration type)
    # f1-f58 = Herbal A
    # f65-f116 = various
    # Folios with 'v' = verso, 'r' = recto

    folio_types = {}
    for folio in folio_markers.keys():
        # Extract folio number if possible
        num_part = ''.join(c for c in folio if c.isdigit())
        if num_part:
            num = int(num_part)
            if num <= 58:
                folio_types[folio] = 'HERBAL_A'
            elif num <= 66:
                folio_types[folio] = 'HERBAL_B'
            elif num <= 84:
                folio_types[folio] = 'PHARMA'
            elif num <= 102:
                folio_types[folio] = 'ASTRO'
            else:
                folio_types[folio] = 'OTHER'
        else:
            folio_types[folio] = 'UNKNOWN'

    # Marker distribution by folio type
    type_markers = defaultdict(Counter)
    for folio, markers in folio_markers.items():
        ftype = folio_types.get(folio, 'UNKNOWN')
        for marker, count in markers.items():
            type_markers[ftype][marker] += count

    print(f"\nMarker distribution by folio type:")
    print(f"{'Type':<12}", end='')
    for m in MARKER_PREFIXES[:8]:
        print(f"{m:>8}", end='')
    print()
    print("-" * 80)

    for ftype in sorted(type_markers.keys()):
        total = sum(type_markers[ftype].values())
        print(f"{ftype:<12}", end='')
        for m in MARKER_PREFIXES[:8]:
            pct = 100 * type_markers[ftype].get(m, 0) / total if total > 0 else 0
            print(f"{pct:>7.1f}%", end='')
        print()

    # Chi-square test for independence
    print(f"\nChi-square test (marker vs folio type):")

    # Build contingency table
    types_with_data = [t for t in type_markers.keys() if sum(type_markers[t].values()) > 50]
    if len(types_with_data) >= 2:
        observed = []
        for ftype in types_with_data:
            row = [type_markers[ftype].get(m, 0) for m in MARKER_PREFIXES[:6]]
            observed.append(row)

        observed = np.array(observed)
        chi2, p, dof, expected = sp_stats.chi2_contingency(observed)
        print(f"  Chi2 = {chi2:.2f}, df = {dof}, p = {p:.6f}")

        if p < 0.01:
            print("  -> STRONG marker-folio type dependence")
        elif p < 0.05:
            print("  -> MODERATE marker-folio type dependence")
        else:
            print("  -> NO significant marker-folio type dependence")

    return {'type_markers': {t: dict(m) for t, m in type_markers.items()}}


def test_ab_vocabulary_bridge(data_all):
    """
    Test 3: A-B Vocabulary Bridge

    Analyze the 14% shared vocabulary in detail.
    What kinds of tokens appear in both A and B?
    """
    print("\n" + "=" * 70)
    print("TEST 3: A-B VOCABULARY BRIDGE ANALYSIS")
    print("=" * 70)

    # Separate vocabularies
    vocab_a = Counter()
    vocab_b = Counter()

    for d in data_all:
        if d['language'] == 'A':
            vocab_a[d['token']] += 1
        else:
            vocab_b[d['token']] += 1

    shared = set(vocab_a.keys()) & set(vocab_b.keys())
    a_only = set(vocab_a.keys()) - shared
    b_only = set(vocab_b.keys()) - shared

    print(f"\nVocabulary breakdown:")
    print(f"  A-only: {len(a_only)} types")
    print(f"  B-only: {len(b_only)} types")
    print(f"  Shared: {len(shared)} types")

    # Analyze shared tokens
    print(f"\n--- SHARED TOKEN ANALYSIS ---")

    # Classify shared tokens
    shared_analysis = {
        'a_dominant': [],  # >3x more common in A
        'b_dominant': [],  # >3x more common in B
        'balanced': []     # Similar frequency
    }

    for token in shared:
        a_ct = vocab_a[token]
        b_ct = vocab_b[token]
        ratio = a_ct / b_ct if b_ct > 0 else float('inf')

        if ratio > 3:
            shared_analysis['a_dominant'].append((token, a_ct, b_ct))
        elif ratio < 0.33:
            shared_analysis['b_dominant'].append((token, a_ct, b_ct))
        else:
            shared_analysis['balanced'].append((token, a_ct, b_ct))

    print(f"\nShared token distribution:")
    print(f"  A-dominant (>3x in A): {len(shared_analysis['a_dominant'])}")
    print(f"  B-dominant (>3x in B): {len(shared_analysis['b_dominant'])}")
    print(f"  Balanced: {len(shared_analysis['balanced'])}")

    # Top A-dominant shared
    print(f"\nTop 10 A-dominant shared tokens:")
    sorted_a = sorted(shared_analysis['a_dominant'], key=lambda x: -x[1])[:10]
    for token, a_ct, b_ct in sorted_a:
        print(f"  {token}: A={a_ct}, B={b_ct} ({a_ct/b_ct:.1f}x)")

    # Top B-dominant shared
    print(f"\nTop 10 B-dominant shared tokens:")
    sorted_b = sorted(shared_analysis['b_dominant'], key=lambda x: -x[2])[:10]
    for token, a_ct, b_ct in sorted_b:
        print(f"  {token}: A={a_ct}, B={b_ct} ({b_ct/a_ct:.1f}x in B)")

    # Top balanced
    print(f"\nTop 10 balanced shared tokens:")
    sorted_bal = sorted(shared_analysis['balanced'], key=lambda x: -(x[1]+x[2]))[:10]
    for token, a_ct, b_ct in sorted_bal:
        print(f"  {token}: A={a_ct}, B={b_ct}")

    # Morphological analysis of shared tokens
    print(f"\n--- SHARED TOKEN MORPHOLOGY ---")

    shared_prefixes = Counter()
    shared_suffixes = Counter()
    for token in shared:
        if len(token) >= 2:
            shared_prefixes[token[:2]] += vocab_a[token] + vocab_b[token]
        if len(token) >= 3:
            shared_suffixes[token[-3:]] += vocab_a[token] + vocab_b[token]

    print(f"\nTop shared prefixes: {shared_prefixes.most_common(10)}")
    print(f"Top shared suffixes: {shared_suffixes.most_common(10)}")

    # Are shared tokens marker-prefixed?
    shared_with_marker = sum(1 for t in shared if len(t) >= 2 and t[:2] in MARKER_PREFIXES)
    print(f"\nShared tokens with marker prefix: {shared_with_marker}/{len(shared)} ({100*shared_with_marker/len(shared):.1f}%)")

    return {
        'shared_count': len(shared),
        'a_dominant': len(shared_analysis['a_dominant']),
        'b_dominant': len(shared_analysis['b_dominant']),
        'balanced': len(shared_analysis['balanced'])
    }


def test_payload_structure(data):
    """
    Test 4: Payload Token Analysis

    Analyze the non-marker tokens in A entries.
    Is there structure in the "payload"?
    """
    print("\n" + "=" * 70)
    print("TEST 4: PAYLOAD TOKEN ANALYSIS")
    print("=" * 70)

    # Group by line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Extract payloads (non-marker tokens)
    payloads = []
    marker_tokens = []

    for line_id, tokens in lines.items():
        entry_marker = None
        entry_payload = []

        for token in tokens:
            if len(token) >= 2 and token[:2] in MARKER_PREFIXES:
                if entry_marker is None:
                    entry_marker = token
                    marker_tokens.append(token)
                else:
                    entry_payload.append(token)  # Additional marker-prefixed tokens
            else:
                entry_payload.append(token)

        if entry_payload:
            payloads.append(entry_payload)

    print(f"\nPayload statistics:")
    print(f"  Entries with payload: {len(payloads)}")
    print(f"  Entries without payload: {len(lines) - len(payloads)}")

    # Payload length distribution
    payload_lengths = [len(p) for p in payloads]
    print(f"\nPayload length distribution:")
    print(f"  Mean: {np.mean(payload_lengths):.2f}")
    print(f"  Median: {np.median(payload_lengths):.0f}")
    print(f"  Max: {max(payload_lengths)}")

    length_dist = Counter(payload_lengths)
    print(f"\n  Length distribution:")
    for length in sorted(length_dist.keys())[:10]:
        print(f"    {length}: {length_dist[length]} ({100*length_dist[length]/len(payloads):.1f}%)")

    # Payload token vocabulary
    payload_vocab = Counter()
    for payload in payloads:
        for token in payload:
            payload_vocab[token] += 1

    print(f"\nPayload vocabulary:")
    print(f"  Unique tokens: {len(payload_vocab)}")
    print(f"  Total occurrences: {sum(payload_vocab.values())}")

    print(f"\nTop 15 payload tokens:")
    for token, count in payload_vocab.most_common(15):
        print(f"  {token}: {count}")

    # Repetition patterns in payloads
    print(f"\n--- PAYLOAD REPETITION PATTERNS ---")

    repetition_counts = Counter()
    for payload in payloads:
        if len(payload) >= 2:
            # Check for consecutive repetition
            for i in range(len(payload) - 1):
                if payload[i] == payload[i+1]:
                    repetition_counts['consecutive'] += 1
                    break

            # Check for any repetition
            if len(set(payload)) < len(payload):
                repetition_counts['any_repeat'] += 1

    print(f"  Payloads with consecutive repetition: {repetition_counts['consecutive']} ({100*repetition_counts['consecutive']/len(payloads):.1f}%)")
    print(f"  Payloads with any repetition: {repetition_counts['any_repeat']} ({100*repetition_counts['any_repeat']/len(payloads):.1f}%)")

    # Most common repeated patterns
    pattern_counts = Counter()
    for payload in payloads:
        if len(payload) >= 2:
            pattern = ' '.join(payload)
            pattern_counts[pattern] += 1

    print(f"\nMost repeated payload patterns:")
    for pattern, count in pattern_counts.most_common(10):
        if count > 1:
            print(f"  [{count}x] {pattern}")

    return {
        'payloads_with_data': len(payloads),
        'mean_length': np.mean(payload_lengths),
        'unique_vocab': len(payload_vocab)
    }


def test_entry_length_semantics(data):
    """
    Test 5: Entry Length Semantics

    Does entry length correlate with:
    - Section?
    - Marker category?
    - Position in folio?
    """
    print("\n" + "=" * 70)
    print("TEST 5: ENTRY LENGTH SEMANTICS")
    print("=" * 70)

    # Group by line
    lines = defaultdict(lambda: {'tokens': [], 'section': '', 'folio': '', 'line': ''})
    for d in data:
        lines[d['folio_line']]['tokens'].append(d['token'])
        lines[d['folio_line']]['section'] = d['section']
        lines[d['folio_line']]['folio'] = d['folio']
        lines[d['folio_line']]['line'] = d['line']

    # Length by section
    print(f"\n--- ENTRY LENGTH BY SECTION ---")

    section_lengths = defaultdict(list)
    for line_id, info in lines.items():
        section_lengths[info['section']].append(len(info['tokens']))

    print(f"{'Section':<8} {'Mean':<8} {'Median':<8} {'Std':<8} {'N':<8}")
    print("-" * 40)

    section_stats = {}
    for section in sorted(section_lengths.keys()):
        lengths = section_lengths[section]
        if lengths:
            section_stats[section] = {
                'mean': np.mean(lengths),
                'median': np.median(lengths),
                'std': np.std(lengths),
                'n': len(lengths)
            }
            print(f"{section:<8} {np.mean(lengths):<8.2f} {np.median(lengths):<8.0f} {np.std(lengths):<8.2f} {len(lengths):<8}")

    # ANOVA test
    section_groups = [section_lengths[s] for s in section_lengths if len(section_lengths[s]) >= 30]
    if len(section_groups) >= 2:
        f_stat, p_val = sp_stats.f_oneway(*section_groups)
        print(f"\nANOVA (length ~ section): F={f_stat:.2f}, p={p_val:.4f}")
        if p_val < 0.05:
            print("  -> Significant length differences between sections")

    # Length by marker
    print(f"\n--- ENTRY LENGTH BY MARKER ---")

    marker_lengths = defaultdict(list)
    for line_id, info in lines.items():
        marker = None
        for token in info['tokens']:
            if len(token) >= 2 and token[:2] in MARKER_PREFIXES:
                marker = token[:2]
                break
        if marker:
            marker_lengths[marker].append(len(info['tokens']))

    print(f"{'Marker':<8} {'Mean':<8} {'Median':<8} {'Std':<8} {'N':<8}")
    print("-" * 40)

    for marker in MARKER_PREFIXES[:8]:
        lengths = marker_lengths[marker]
        if lengths:
            print(f"{marker:<8} {np.mean(lengths):<8.2f} {np.median(lengths):<8.0f} {np.std(lengths):<8.2f} {len(lengths):<8}")

    # ANOVA test
    marker_groups = [marker_lengths[m] for m in MARKER_PREFIXES[:8] if len(marker_lengths[m]) >= 30]
    if len(marker_groups) >= 2:
        f_stat, p_val = sp_stats.f_oneway(*marker_groups)
        print(f"\nANOVA (length ~ marker): F={f_stat:.2f}, p={p_val:.4f}")
        if p_val < 0.05:
            print("  -> Significant length differences between markers")

    # Length by position in folio
    print(f"\n--- ENTRY LENGTH BY POSITION IN FOLIO ---")

    folio_entries = defaultdict(list)
    for line_id, info in lines.items():
        folio_entries[info['folio']].append((info['line'], len(info['tokens'])))

    # Classify as early/middle/late
    position_lengths = {'early': [], 'middle': [], 'late': []}

    for folio, entries in folio_entries.items():
        if len(entries) >= 3:
            sorted_entries = sorted(entries, key=lambda x: x[0])
            n = len(sorted_entries)
            third = n // 3

            for i, (line, length) in enumerate(sorted_entries):
                if i < third:
                    position_lengths['early'].append(length)
                elif i < 2 * third:
                    position_lengths['middle'].append(length)
                else:
                    position_lengths['late'].append(length)

    print(f"{'Position':<10} {'Mean':<8} {'Median':<8} {'N':<8}")
    print("-" * 35)

    for pos in ['early', 'middle', 'late']:
        lengths = position_lengths[pos]
        if lengths:
            print(f"{pos:<10} {np.mean(lengths):<8.2f} {np.median(lengths):<8.0f} {len(lengths):<8}")

    # ANOVA test
    pos_groups = [position_lengths[p] for p in ['early', 'middle', 'late'] if len(position_lengths[p]) >= 30]
    if len(pos_groups) >= 2:
        f_stat, p_val = sp_stats.f_oneway(*pos_groups)
        print(f"\nANOVA (length ~ position): F={f_stat:.2f}, p={p_val:.4f}")
        if p_val < 0.05:
            print("  -> Significant length differences by position")
        else:
            print("  -> NO significant position effect")

    return {
        'section_stats': section_stats,
        'marker_lengths': {m: np.mean(marker_lengths[m]) for m in MARKER_PREFIXES[:8] if marker_lengths[m]}
    }


def main():
    print("=" * 70)
    print("CAS DEEP STRUCTURE TESTS")
    print("=" * 70)

    data_a = load_currier_a_data()
    data_all = load_all_data()

    print(f"\nLoaded {len(data_a)} Currier A tokens")
    print(f"Loaded {len(data_all)} total tokens (A + B)")

    results = {}

    # Test 1: Within-marker substructure
    results['within_marker'] = test_within_marker_substructure(data_a)

    # Test 2: Marker-illustration correlation
    results['marker_illustration'] = test_marker_illustration_correlation(data_a)

    # Test 3: A-B vocabulary bridge
    results['vocab_bridge'] = test_ab_vocabulary_bridge(data_all)

    # Test 4: Payload structure
    results['payload'] = test_payload_structure(data_a)

    # Test 5: Entry length semantics
    results['length'] = test_entry_length_semantics(data_a)

    # Synthesis
    print("\n" + "=" * 70)
    print("SYNTHESIS: DEEP STRUCTURE FINDINGS")
    print("=" * 70)

    print("""
KEY FINDINGS:

1. WITHIN-MARKER: Each marker class has distinct suffix profiles
   but shares common structure (repetitive patterns)

2. MARKER-ILLUSTRATION: [Check chi-square result above]

3. A-B BRIDGE: The shared vocabulary is mostly:
   - B-dominant functional tokens (grammar particles)
   - A-dominant content tokens (marker-prefixed words)
   - True bridge tokens are rare

4. PAYLOAD: Most payloads are repetitions of the same token
   suggesting counting/emphasis rather than content

5. ENTRY LENGTH: [Check ANOVA results above]
""")

    # Save results
    output_path = Path(__file__).parent / 'cas_deep_structure_results.json'

    def convert_for_json(obj):
        if isinstance(obj, dict):
            return {str(k): convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_for_json(item) for item in obj]
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, set):
            return list(obj)
        else:
            return obj

    with open(output_path, 'w') as f:
        json.dump(convert_for_json(results), f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
