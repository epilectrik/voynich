"""
CAS Phase 5: Redundancy & Normalization Tests

Question: Does Currier A behave like a database?

Tests:
1. Token reuse across entries (are tokens repeated?)
2. Normalized vs expanded forms (do patterns compress?)
3. Key-value patterns (marker + payload structure)
4. Reference patterns (do entries point to each other?)
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np

project_root = Path(__file__).parent.parent.parent

MARKER_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'yk', 'yt']


def load_currier_a_data():
    """Load Currier A tokens with line-level granularity."""
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
            if len(parts) > lang_idx:
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


def test_token_reuse(data):
    """
    Test 1: Token reuse patterns

    How many times does each token appear?
    High reuse = registry/reference pattern
    Low reuse = unique entries
    """
    print("\n" + "=" * 70)
    print("TEST 1: TOKEN REUSE PATTERNS")
    print("=" * 70)

    # Count token frequencies
    token_counts = Counter(d['token'] for d in data)
    total_tokens = len(data)
    unique_tokens = len(token_counts)

    print(f"\nBasic counts:")
    print(f"  Total tokens: {total_tokens}")
    print(f"  Unique tokens: {unique_tokens}")
    print(f"  Type-Token Ratio: {unique_tokens/total_tokens:.3f}")

    # Frequency distribution
    freq_dist = Counter(token_counts.values())
    hapax = sum(1 for c in token_counts.values() if c == 1)
    dis = sum(1 for c in token_counts.values() if c == 2)

    print(f"\nFrequency distribution:")
    print(f"  Hapax legomena (appear 1x): {hapax} ({100*hapax/unique_tokens:.1f}%)")
    print(f"  Dis legomena (appear 2x): {dis} ({100*dis/unique_tokens:.1f}%)")
    print(f"  High-frequency (>10x): {sum(1 for c in token_counts.values() if c > 10)}")
    print(f"  Very high (>50x): {sum(1 for c in token_counts.values() if c > 50)}")

    # Top tokens
    print(f"\nTop 15 most frequent tokens:")
    for token, count in token_counts.most_common(15):
        pct = 100 * count / total_tokens
        print(f"  {token}: {count} ({pct:.2f}%)")

    # Zipf analysis
    sorted_counts = sorted(token_counts.values(), reverse=True)
    top_10_coverage = sum(sorted_counts[:10]) / total_tokens
    top_50_coverage = sum(sorted_counts[:50]) / total_tokens
    top_100_coverage = sum(sorted_counts[:100]) / total_tokens

    print(f"\nVocabulary concentration:")
    print(f"  Top 10 tokens cover: {100*top_10_coverage:.1f}%")
    print(f"  Top 50 tokens cover: {100*top_50_coverage:.1f}%")
    print(f"  Top 100 tokens cover: {100*top_100_coverage:.1f}%")

    return {
        'total_tokens': total_tokens,
        'unique_tokens': unique_tokens,
        'ttr': unique_tokens / total_tokens,
        'hapax_pct': hapax / unique_tokens,
        'top_10_coverage': top_10_coverage,
        'top_50_coverage': top_50_coverage
    }


def test_entry_patterns(data):
    """
    Test 2: Entry pattern analysis

    Do entries follow templates?
    """
    print("\n" + "=" * 70)
    print("TEST 2: ENTRY PATTERN TEMPLATES")
    print("=" * 70)

    # Group by line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Extract entry patterns
    # Pattern = marker + number of additional tokens
    entry_patterns = Counter()
    marker_payload_counts = defaultdict(list)

    for line_id, tokens in lines.items():
        marker = None
        payload = []

        for token in tokens:
            if len(token) >= 2 and token[:2] in MARKER_PREFIXES:
                marker = token[:2]
            else:
                payload.append(token)

        if marker:
            pattern = f"{marker}+{len(payload)}"
            entry_patterns[pattern] += 1
            marker_payload_counts[marker].append(len(payload))
        else:
            pattern = f"nomarker+{len(tokens)}"
            entry_patterns[pattern] += 1

    print(f"\nTop 15 entry patterns (marker + payload count):")
    for pattern, count in entry_patterns.most_common(15):
        print(f"  {pattern}: {count}")

    # Payload size analysis
    print(f"\nPayload size per marker (non-marker tokens in entry):")
    for marker in MARKER_PREFIXES[:8]:
        payloads = marker_payload_counts[marker]
        if payloads:
            mean_p = np.mean(payloads)
            median_p = np.median(payloads)
            print(f"  {marker}: mean={mean_p:.2f}, median={median_p:.0f}, range=[{min(payloads)}-{max(payloads)}]")

    # Check for stereotyped patterns
    total_entries = len(lines)
    top_5_patterns = sum(c for _, c in entry_patterns.most_common(5))
    pattern_concentration = top_5_patterns / total_entries

    print(f"\nPattern concentration:")
    print(f"  Top 5 patterns cover: {100*pattern_concentration:.1f}% of entries")

    if pattern_concentration > 0.5:
        print("  -> HIGHLY STEREOTYPED (few templates)")
    elif pattern_concentration > 0.3:
        print("  -> MODERATELY stereotyped")
    else:
        print("  -> LOW stereotypy (diverse patterns)")

    return {
        'top_patterns': entry_patterns.most_common(10),
        'pattern_concentration': pattern_concentration
    }


def test_key_value_structure(data):
    """
    Test 3: Key-value structure

    Does each entry follow marker:payload structure?
    """
    print("\n" + "=" * 70)
    print("TEST 3: KEY-VALUE STRUCTURE")
    print("=" * 70)

    # Group by line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Analyze structure
    structures = {
        'marker_only': 0,       # Just marker, no payload
        'marker_payload': 0,    # Marker + payload
        'no_marker': 0,         # No marker
        'multi_marker': 0       # Multiple markers (shouldn't happen)
    }

    marker_positions = Counter()  # Where does marker appear?

    for line_id, tokens in lines.items():
        markers = []
        marker_positions_in_entry = []

        for i, token in enumerate(tokens):
            if len(token) >= 2 and token[:2] in MARKER_PREFIXES:
                markers.append(token)
                marker_positions_in_entry.append(i)

        if len(markers) == 0:
            structures['no_marker'] += 1
        elif len(markers) == 1:
            if len(tokens) == 1:
                structures['marker_only'] += 1
            else:
                structures['marker_payload'] += 1

            # Record position
            pos = marker_positions_in_entry[0]
            if pos == 0:
                marker_positions['first'] += 1
            elif pos == len(tokens) - 1:
                marker_positions['last'] += 1
            else:
                marker_positions['middle'] += 1
        else:
            structures['multi_marker'] += 1

    total = len(lines)

    print(f"\nEntry structure distribution:")
    for struct, count in structures.items():
        pct = 100 * count / total
        print(f"  {struct}: {count} ({pct:.1f}%)")

    print(f"\nMarker position in marker_payload entries:")
    mp_total = structures['marker_payload']
    for pos, count in marker_positions.items():
        pct = 100 * count / mp_total if mp_total > 0 else 0
        print(f"  {pos}: {count} ({pct:.1f}%)")

    # Key-value assessment
    kv_pct = (structures['marker_only'] + structures['marker_payload']) / total

    print(f"\nKey-value assessment:")
    print(f"  Entries with key-value structure: {kv_pct:.1%}")

    if kv_pct > 0.7:
        print("  -> STRONG key-value pattern")
    elif kv_pct > 0.5:
        print("  -> MODERATE key-value pattern")
    else:
        print("  -> WEAK key-value pattern")

    return {
        'structures': structures,
        'marker_positions': dict(marker_positions),
        'kv_pct': kv_pct
    }


def test_cross_reference(data):
    """
    Test 4: Cross-reference patterns

    Do entries reference each other?
    """
    print("\n" + "=" * 70)
    print("TEST 4: CROSS-REFERENCE PATTERNS")
    print("=" * 70)

    # Group by line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Look for repeated exact sequences
    sequence_counts = Counter()
    for line_id, tokens in lines.items():
        if len(tokens) >= 2:
            seq = ' '.join(tokens)
            sequence_counts[seq] += 1

    # Repeated sequences
    repeated = {seq: count for seq, count in sequence_counts.items() if count > 1}

    print(f"\nExact sequence repetition:")
    print(f"  Total unique sequences: {len(sequence_counts)}")
    print(f"  Repeated sequences (>1x): {len(repeated)}")
    print(f"  Repetition rate: {len(repeated)/len(sequence_counts):.1%}")

    if repeated:
        print(f"\nTop 10 repeated sequences:")
        for seq, count in sorted(repeated.items(), key=lambda x: -x[1])[:10]:
            print(f"  [{count}x] {seq}")

    # Look for subsequence sharing
    # Extract 2-token subsequences
    bigrams = Counter()
    for tokens in lines.values():
        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]} {tokens[i+1]}"
            bigrams[bigram] += 1

    repeated_bigrams = sum(1 for c in bigrams.values() if c > 1)
    bigram_reuse_rate = repeated_bigrams / len(bigrams) if bigrams else 0

    print(f"\nBigram (2-token) analysis:")
    print(f"  Total unique bigrams: {len(bigrams)}")
    print(f"  Bigrams appearing >1x: {repeated_bigrams} ({bigram_reuse_rate:.1%})")

    print(f"\nTop 10 repeated bigrams:")
    for bigram, count in bigrams.most_common(10):
        print(f"  [{count}x] {bigram}")

    # Cross-reference assessment
    if bigram_reuse_rate > 0.3:
        print(f"\n  -> HIGH cross-reference (formulaic)")
    elif bigram_reuse_rate > 0.15:
        print(f"\n  -> MODERATE cross-reference")
    else:
        print(f"\n  -> LOW cross-reference (unique entries)")

    return {
        'unique_sequences': len(sequence_counts),
        'repeated_sequences': len(repeated),
        'bigram_reuse_rate': bigram_reuse_rate
    }


def synthesize_normalization(results):
    """Synthesize normalization results."""
    print("\n" + "=" * 70)
    print("SYNTHESIS: DATABASE-LIKE PROPERTIES")
    print("=" * 70)

    # Collect evidence
    ttr = results['reuse']['ttr']
    hapax = results['reuse']['hapax_pct']
    kv_pct = results['kv']['kv_pct']
    bigram_reuse = results['reference']['bigram_reuse_rate']
    pattern_conc = results['patterns']['pattern_concentration']

    print(f"\nKey metrics:")
    print(f"  Type-Token Ratio: {ttr:.3f} (lower = more repetition)")
    print(f"  Hapax rate: {hapax:.1%} (lower = more reuse)")
    print(f"  Key-value structure: {kv_pct:.1%}")
    print(f"  Bigram reuse rate: {bigram_reuse:.1%}")
    print(f"  Pattern concentration: {pattern_conc:.1%}")

    # Scoring
    db_score = 0

    if ttr < 0.15:
        db_score += 1
        print(f"\n[+] Low TTR -> vocabulary is reused (database-like)")

    if kv_pct > 0.5:
        db_score += 1
        print(f"[+] High key-value structure -> record format")

    if bigram_reuse > 0.15:
        db_score += 1
        print(f"[+] Bigram reuse -> formulaic patterns")

    if pattern_conc > 0.3:
        db_score += 1
        print(f"[+] Pattern concentration -> stereotyped templates")

    # Verdict
    print(f"\nDatabase-like score: {db_score}/4")

    if db_score >= 3:
        verdict = 'DATABASE_LIKE'
        interpretation = """
Currier A behaves like a DATABASE or REGISTRY:
- Low type-token ratio (vocabulary is heavily reused)
- Clear key-value structure (marker + payload)
- Formulaic patterns (repeated templates)
- This is a CATALOG or INDEX, not free text
        """
    elif db_score >= 2:
        verdict = 'SEMI_STRUCTURED'
        interpretation = "Currier A shows some database-like properties but also variability."
    else:
        verdict = 'FREE_TEXT'
        interpretation = "Currier A does not show strong database-like properties."

    print(f"\n{'='*70}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*70}")
    print(interpretation)

    return verdict, interpretation


def main():
    print("=" * 70)
    print("CAS PHASE 5: REDUNDANCY & NORMALIZATION")
    print("=" * 70)
    print("\nQuestion: Does Currier A behave like a database?")

    data = load_currier_a_data()
    print(f"\nLoaded {len(data)} Currier A tokens")

    results = {
        'reuse': test_token_reuse(data),
        'patterns': test_entry_patterns(data),
        'kv': test_key_value_structure(data),
        'reference': test_cross_reference(data)
    }

    verdict, interpretation = synthesize_normalization(results)

    results['verdict'] = verdict
    results['interpretation'] = interpretation

    # Save results
    output_path = Path(__file__).parent / 'cas_phase5_results.json'

    def convert_for_json(obj):
        if isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_for_json(item) for item in obj]
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        else:
            return obj

    with open(output_path, 'w') as f:
        json.dump(convert_for_json(results), f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
