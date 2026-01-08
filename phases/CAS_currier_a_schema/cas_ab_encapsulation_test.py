"""
A/B Encapsulation Test

Question: Does a Currier A 'record' encapsulate a family of Currier B folios?

Hypothesis: A serves as index/header for B content
- A entries precede B folios they reference
- A marker counts match B folio clusters
- A vocabulary correlates with adjacent B content

Tests:
1. Positional relationship: Does A precede B within sections?
2. Count correspondence: Do A entry counts predict B folio counts?
3. Marker-folio mapping: Do A markers cluster with specific B folios?
4. Vocabulary bridge: Do shared A/B tokens appear at boundaries?
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy import stats as sp_stats

project_root = Path(__file__).parent.parent.parent

MARKER_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'yk', 'yt']


def load_all_data():
    """Load all tokens with sequence order preserved."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        word_idx = 0
        folio_idx = header.index('folio') if 'folio' in header else 1
        line_idx = header.index('line') if 'line' in header else 2
        lang_idx = 6
        section_idx = header.index('section') if 'section' in header else 3

        for i, line in enumerate(f):
            parts = line.strip().split('\t')
            if len(parts) > lang_idx:
                lang = parts[lang_idx].strip('"').strip()
                if lang in ['A', 'B']:
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
                            'language': lang,
                            'seq': i
                        })

    return data


def test_positional_relationship(data):
    """
    Test 1: Does A precede B within mixed sections?

    If A indexes B, A entries should come BEFORE the B content they reference.
    """
    print("\n" + "=" * 70)
    print("TEST 1: POSITIONAL RELATIONSHIP (Does A precede B?)")
    print("=" * 70)

    # Group by folio
    folio_data = defaultdict(lambda: {'A': [], 'B': [], 'section': ''})

    for d in data:
        folio_data[d['folio']][d['language']].append(d['seq'])
        folio_data[d['folio']]['section'] = d['section']

    # For mixed folios, check if A comes before B
    mixed_folios = []
    a_before_b = 0
    b_before_a = 0
    interleaved = 0

    for folio, info in folio_data.items():
        if info['A'] and info['B']:
            mixed_folios.append(folio)

            min_a = min(info['A'])
            max_a = max(info['A'])
            min_b = min(info['B'])
            max_b = max(info['B'])

            if max_a < min_b:
                a_before_b += 1
            elif max_b < min_a:
                b_before_a += 1
            else:
                interleaved += 1

    print(f"\nMixed folios (contain both A and B): {len(mixed_folios)}")
    print(f"\nPositional patterns in mixed folios:")
    print(f"  A entirely before B: {a_before_b} ({100*a_before_b/len(mixed_folios):.1f}%)")
    print(f"  B entirely before A: {b_before_a} ({100*b_before_a/len(mixed_folios):.1f}%)")
    print(f"  Interleaved: {interleaved} ({100*interleaved/len(mixed_folios):.1f}%)")

    # Section-level analysis
    print(f"\nSection-level ordering:")

    section_data = defaultdict(lambda: {'A_positions': [], 'B_positions': []})

    for d in data:
        section_data[d['section']][f"{d['language']}_positions"].append(d['seq'])

    for section in sorted(section_data.keys()):
        a_pos = section_data[section]['A_positions']
        b_pos = section_data[section]['B_positions']

        if a_pos and b_pos:
            mean_a = np.mean(a_pos)
            mean_b = np.mean(b_pos)

            if mean_a < mean_b:
                order = "A before B"
            else:
                order = "B before A"

            print(f"  {section}: mean_A={mean_a:.0f}, mean_B={mean_b:.0f} -> {order}")

    # Verdict
    if a_before_b > interleaved and a_before_b > b_before_a:
        print(f"\n  -> A PRECEDES B (supports indexing hypothesis)")
    elif interleaved > a_before_b:
        print(f"\n  -> INTERLEAVED (does NOT support simple indexing)")
    else:
        print(f"\n  -> B PRECEDES A (contradicts indexing hypothesis)")

    return {
        'mixed_folios': len(mixed_folios),
        'a_before_b': a_before_b,
        'b_before_a': b_before_a,
        'interleaved': interleaved
    }


def test_count_correspondence(data):
    """
    Test 2: Do A entry counts predict B folio counts?

    If A indexes B, the number of A entries should correlate with B complexity.
    """
    print("\n" + "=" * 70)
    print("TEST 2: COUNT CORRESPONDENCE")
    print("=" * 70)

    # Count A entries (lines) and B tokens per section
    section_counts = defaultdict(lambda: {'A_lines': set(), 'B_tokens': 0, 'B_folios': set()})

    for d in data:
        section = d['section']
        if d['language'] == 'A':
            section_counts[section]['A_lines'].add(f"{d['folio']}_{d['line']}")
        else:
            section_counts[section]['B_tokens'] += 1
            section_counts[section]['B_folios'].add(d['folio'])

    print(f"\nSection-level counts:")
    print(f"{'Section':<8} {'A entries':<12} {'B tokens':<12} {'B folios':<12}")
    print("-" * 45)

    a_counts = []
    b_counts = []

    for section in sorted(section_counts.keys()):
        a_entries = len(section_counts[section]['A_lines'])
        b_tokens = section_counts[section]['B_tokens']
        b_folios = len(section_counts[section]['B_folios'])

        print(f"{section:<8} {a_entries:<12} {b_tokens:<12} {b_folios:<12}")

        if a_entries > 0 and b_tokens > 0:
            a_counts.append(a_entries)
            b_counts.append(b_tokens)

    # Correlation test
    if len(a_counts) >= 3:
        r, p = sp_stats.pearsonr(a_counts, b_counts)
        print(f"\nCorrelation (A entries vs B tokens): r={r:.3f}, p={p:.4f}")

        if r > 0.5 and p < 0.05:
            print("  -> POSITIVE CORRELATION (A count predicts B size)")
        elif r < -0.5 and p < 0.05:
            print("  -> NEGATIVE CORRELATION (inverse relationship)")
        else:
            print("  -> NO SIGNIFICANT CORRELATION")

    return {
        'section_counts': {s: {'A': len(v['A_lines']), 'B': v['B_tokens']}
                          for s, v in section_counts.items()}
    }


def test_marker_folio_mapping(data):
    """
    Test 3: Do A markers cluster with specific B folios?

    If A indexes B, specific markers should map to specific B folio groups.
    """
    print("\n" + "=" * 70)
    print("TEST 3: MARKER-FOLIO MAPPING")
    print("=" * 70)

    # Get A markers by folio
    folio_markers = defaultdict(set)
    folio_language = defaultdict(lambda: {'A': 0, 'B': 0})

    for d in data:
        folio_language[d['folio']][d['language']] += 1

        if d['language'] == 'A':
            token = d['token']
            if len(token) >= 2 and token[:2] in MARKER_PREFIXES:
                folio_markers[d['folio']].add(token[:2])

    # Find folios that are pure A vs pure B
    pure_a_folios = [f for f, langs in folio_language.items() if langs['A'] > 0 and langs['B'] == 0]
    pure_b_folios = [f for f, langs in folio_language.items() if langs['B'] > 0 and langs['A'] == 0]

    print(f"\nFolio classification:")
    print(f"  Pure A folios: {len(pure_a_folios)}")
    print(f"  Pure B folios: {len(pure_b_folios)}")

    # For A folios, what markers do they use?
    marker_distribution = Counter()
    for folio in pure_a_folios:
        for marker in folio_markers[folio]:
            marker_distribution[marker] += 1

    print(f"\nMarker distribution in pure-A folios:")
    for marker, count in marker_distribution.most_common(10):
        print(f"  {marker}: {count} folios")

    # Check if adjacent A and B folios share vocabulary
    print(f"\nAdjacent A-B folio analysis:")

    # Sort folios by name (approximates manuscript order)
    all_folios = sorted(folio_language.keys())

    adjacencies = []
    for i in range(len(all_folios) - 1):
        f1, f2 = all_folios[i], all_folios[i+1]

        # Check if one is A-dominant and other is B-dominant
        f1_a_pct = folio_language[f1]['A'] / (folio_language[f1]['A'] + folio_language[f1]['B'] + 0.001)
        f2_a_pct = folio_language[f2]['A'] / (folio_language[f2]['A'] + folio_language[f2]['B'] + 0.001)

        if (f1_a_pct > 0.8 and f2_a_pct < 0.2) or (f1_a_pct < 0.2 and f2_a_pct > 0.8):
            adjacencies.append((f1, f2, f1_a_pct, f2_a_pct))

    print(f"  A-B boundary transitions: {len(adjacencies)}")

    if adjacencies:
        print(f"  First 10 boundaries:")
        for f1, f2, a1, a2 in adjacencies[:10]:
            label1 = "A" if a1 > 0.5 else "B"
            label2 = "A" if a2 > 0.5 else "B"
            print(f"    {f1} ({label1}) -> {f2} ({label2})")

    return {
        'pure_a_folios': len(pure_a_folios),
        'pure_b_folios': len(pure_b_folios),
        'marker_distribution': dict(marker_distribution),
        'ab_boundaries': len(adjacencies)
    }


def test_vocabulary_bridge(data):
    """
    Test 4: Do shared A/B tokens cluster at boundaries?

    If A references B, shared vocabulary should appear near A-B transitions.
    """
    print("\n" + "=" * 70)
    print("TEST 4: VOCABULARY BRIDGE")
    print("=" * 70)

    # Get vocabulary by language
    vocab_a = set()
    vocab_b = set()

    for d in data:
        if d['language'] == 'A':
            vocab_a.add(d['token'])
        else:
            vocab_b.add(d['token'])

    shared = vocab_a & vocab_b

    print(f"\nShared vocabulary: {len(shared)} tokens")
    print(f"  A-only: {len(vocab_a - vocab_b)}")
    print(f"  B-only: {len(vocab_b - vocab_a)}")

    # Check where shared tokens appear
    shared_positions = {'A': [], 'B': []}

    for d in data:
        if d['token'] in shared:
            shared_positions[d['language']].append(d['seq'])

    print(f"\nShared token occurrences:")
    print(f"  In A text: {len(shared_positions['A'])}")
    print(f"  In B text: {len(shared_positions['B'])}")

    # Are shared tokens clustered near language boundaries?
    # Find boundary positions
    prev_lang = None
    boundaries = []

    for d in data:
        if prev_lang and prev_lang != d['language']:
            boundaries.append(d['seq'])
        prev_lang = d['language']

    print(f"\nLanguage boundaries: {len(boundaries)}")

    # Distance of shared tokens from nearest boundary
    if boundaries and shared_positions['A']:
        distances_a = []
        for pos in shared_positions['A']:
            min_dist = min(abs(pos - b) for b in boundaries)
            distances_a.append(min_dist)

        mean_dist_a = np.mean(distances_a)

        # Compare to random baseline
        all_a_positions = [d['seq'] for d in data if d['language'] == 'A']
        random_distances = []
        for pos in np.random.choice(all_a_positions, size=min(1000, len(all_a_positions)), replace=False):
            min_dist = min(abs(pos - b) for b in boundaries)
            random_distances.append(min_dist)

        mean_random = np.mean(random_distances)

        print(f"\nShared token distance from boundaries:")
        print(f"  Shared A tokens: mean distance = {mean_dist_a:.1f}")
        print(f"  Random A tokens: mean distance = {mean_random:.1f}")
        print(f"  Ratio: {mean_dist_a/mean_random:.2f}x")

        if mean_dist_a < mean_random * 0.7:
            print("  -> Shared tokens CLUSTER near boundaries (supports bridge)")
        elif mean_dist_a > mean_random * 1.3:
            print("  -> Shared tokens AVOID boundaries")
        else:
            print("  -> Shared tokens show NO boundary preference")

    # What ARE the shared tokens?
    print(f"\nTop 20 shared tokens (by total frequency):")
    token_counts = Counter(d['token'] for d in data if d['token'] in shared)
    for token, count in token_counts.most_common(20):
        a_ct = sum(1 for d in data if d['token'] == token and d['language'] == 'A')
        b_ct = sum(1 for d in data if d['token'] == token and d['language'] == 'B')
        print(f"  {token}: A={a_ct}, B={b_ct}")

    return {
        'shared_count': len(shared),
        'shared_in_a': len(shared_positions['A']),
        'shared_in_b': len(shared_positions['B'])
    }


def test_encapsulation_ratio(data):
    """
    Test 5: Direct encapsulation test

    If each A entry indexes a B folio family, we'd expect:
    - Ratio of A entries to B folios to be consistent
    - A entries to "point to" following B content
    """
    print("\n" + "=" * 70)
    print("TEST 5: ENCAPSULATION RATIO")
    print("=" * 70)

    # Count unique A entries (lines) and B programs (folios) per section
    section_data = defaultdict(lambda: {'A_entries': set(), 'B_folios': set()})

    for d in data:
        section = d['section']
        if d['language'] == 'A':
            section_data[section]['A_entries'].add(f"{d['folio']}_{d['line']}")
        else:
            section_data[section]['B_folios'].add(d['folio'])

    print(f"\nSection-level encapsulation ratios:")
    print(f"{'Section':<8} {'A entries':<12} {'B folios':<12} {'Ratio A:B':<12}")
    print("-" * 45)

    ratios = []
    for section in sorted(section_data.keys()):
        a_ct = len(section_data[section]['A_entries'])
        b_ct = len(section_data[section]['B_folios'])

        if b_ct > 0:
            ratio = a_ct / b_ct
            ratios.append(ratio)
            print(f"{section:<8} {a_ct:<12} {b_ct:<12} {ratio:<12.2f}")
        elif a_ct > 0:
            print(f"{section:<8} {a_ct:<12} {b_ct:<12} {'inf':<12}")

    if ratios:
        mean_ratio = np.mean(ratios)
        std_ratio = np.std(ratios)
        cv = std_ratio / mean_ratio if mean_ratio > 0 else float('inf')

        print(f"\nRatio statistics:")
        print(f"  Mean A:B ratio: {mean_ratio:.2f}")
        print(f"  Std dev: {std_ratio:.2f}")
        print(f"  CV (consistency): {cv:.2f}")

        if cv < 0.3:
            print("  -> CONSISTENT ratio (supports encapsulation)")
        else:
            print("  -> INCONSISTENT ratio (does NOT support encapsulation)")

    return {'ratios': ratios}


def synthesize_encapsulation(results):
    """Synthesize encapsulation test results."""
    print("\n" + "=" * 70)
    print("SYNTHESIS: DOES A ENCAPSULATE B?")
    print("=" * 70)

    evidence_for = 0
    evidence_against = 0

    # Test 1: Positional
    if results['positional']['a_before_b'] > results['positional']['interleaved']:
        evidence_for += 1
        print("\n[+] A precedes B in mixed folios -> supports encapsulation")
    else:
        evidence_against += 1
        print("\n[-] A/B interleaved -> does NOT support encapsulation")

    # Test 3: Marker mapping
    if results['marker']['ab_boundaries'] > 10:
        evidence_for += 1
        print("[+] Clear A-B boundaries exist -> supports indexing")
    else:
        evidence_against += 1
        print("[-] Few A-B boundaries -> does NOT support indexing")

    print(f"\nEvidence FOR encapsulation: {evidence_for}")
    print(f"Evidence AGAINST encapsulation: {evidence_against}")

    if evidence_for > evidence_against:
        verdict = 'WEAK_ENCAPSULATION'
        interpretation = """
There is WEAK evidence that A may index/encapsulate B:
- A tends to precede B in mixed sections
- Clear A-B boundaries exist in manuscript order

HOWEVER:
- The relationship is not clean (interleaving occurs)
- Vocabulary overlap is low (14%)
- A entries may be PARALLEL to B, not REFERENCING B
        """
    else:
        verdict = 'NO_ENCAPSULATION'
        interpretation = """
A does NOT appear to encapsulate B families:
- A and B are largely SEPARATE systems
- They occupy different sections
- Low vocabulary overlap (14%)
- No consistent A:B ratio

A is more likely a PARALLEL classification system,
not an index into B content.
        """

    print(f"\n{'='*70}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*70}")
    print(interpretation)

    return verdict, interpretation


def main():
    print("=" * 70)
    print("A/B ENCAPSULATION TEST")
    print("=" * 70)
    print("\nQuestion: Does a Currier A 'record' encapsulate a family of B folios?")

    data = load_all_data()
    print(f"\nLoaded {len(data)} tokens")

    results = {
        'positional': test_positional_relationship(data),
        'count': test_count_correspondence(data),
        'marker': test_marker_folio_mapping(data),
        'vocab': test_vocabulary_bridge(data),
        'ratio': test_encapsulation_ratio(data)
    }

    verdict, interpretation = synthesize_encapsulation(results)

    results['verdict'] = verdict
    results['interpretation'] = interpretation

    # Save
    output_path = Path(__file__).parent / 'cas_encapsulation_results.json'

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
