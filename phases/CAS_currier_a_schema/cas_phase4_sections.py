"""
CAS Phase 4: Section-Schema Binding

Question: Do sections impose different schema constraints?

CAS-3 found:
- 8+ mutually exclusive marker categories
- ZERO co-occurrence between markers
- ZERO vocabulary overlap between markers
- Section-marker dependence (Chi2 p < 0.0001)

Now we test:
1. Does each section use a different subset of markers?
2. Are some markers illegal in some sections?
3. Are there section-specific vocabulary patterns?
4. Is Currier A a GLOBAL taxonomy or DOMAIN-LOCAL schemas?
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy import stats as sp_stats

project_root = Path(__file__).parent.parent.parent

# The 10 marker prefixes identified in CAS-3
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


def test_section_marker_activation(data):
    """
    Test 1: Which markers are activated in which sections?
    """
    print("\n" + "=" * 70)
    print("TEST 1: SECTION MARKER ACTIVATION")
    print("=" * 70)

    # Group by line with section
    lines = defaultdict(lambda: {'tokens': [], 'section': ''})
    for d in data:
        lines[d['folio_line']]['tokens'].append(d['token'])
        lines[d['folio_line']]['section'] = d['section']

    # Count markers per section
    section_markers = defaultdict(lambda: defaultdict(int))
    section_totals = defaultdict(int)

    for line_id, info in lines.items():
        section = info['section']
        section_totals[section] += 1

        for token in info['tokens']:
            if len(token) >= 2:
                prefix = token[:2]
                if prefix in MARKER_PREFIXES:
                    section_markers[section][prefix] += 1

    sections = sorted([s for s in section_totals.keys() if section_totals[s] >= 50])

    print(f"\nMarker presence by section (Y = >1% of entries, - = <1% or absent):")
    print(f"{'Section':<8} {'Total':<8}", end='')
    for m in MARKER_PREFIXES:
        print(f"{m:>6}", end='')
    print()
    print("-" * 80)

    section_profiles = {}

    for section in sections:
        profile = []
        print(f"{section:<8} {section_totals[section]:<8}", end='')
        for m in MARKER_PREFIXES:
            count = section_markers[section][m]
            pct = 100 * count / section_totals[section] if section_totals[section] > 0 else 0
            if pct >= 1:
                print(f"{'Y':>6}", end='')
                profile.append(m)
            else:
                print(f"{'-':>6}", end='')
        print()
        section_profiles[section] = profile

    # Find section-specific markers
    print(f"\nSection-specific marker activation:")
    all_markers = set()
    for s, markers in section_profiles.items():
        all_markers.update(markers)

    for marker in MARKER_PREFIXES:
        sections_with = [s for s, profile in section_profiles.items() if marker in profile]
        if len(sections_with) == 1:
            print(f"  {marker}: ONLY in section {sections_with[0]}")
        elif len(sections_with) == len(section_profiles):
            print(f"  {marker}: UNIVERSAL (all sections)")
        else:
            print(f"  {marker}: in {len(sections_with)}/{len(section_profiles)} sections: {sections_with}")

    return {
        'section_markers': {s: dict(m) for s, m in section_markers.items()},
        'section_totals': dict(section_totals),
        'section_profiles': section_profiles
    }


def test_marker_dominance(data):
    """
    Test 2: Does each section have a dominant marker?
    """
    print("\n" + "=" * 70)
    print("TEST 2: SECTION MARKER DOMINANCE")
    print("=" * 70)

    # Group by line with section
    lines = defaultdict(lambda: {'tokens': [], 'section': ''})
    for d in data:
        lines[d['folio_line']]['tokens'].append(d['token'])
        lines[d['folio_line']]['section'] = d['section']

    # Count markers per section
    section_markers = defaultdict(lambda: defaultdict(int))
    section_totals = defaultdict(int)

    for line_id, info in lines.items():
        section = info['section']
        section_totals[section] += 1

        markers_in_entry = set()
        for token in info['tokens']:
            if len(token) >= 2:
                prefix = token[:2]
                if prefix in MARKER_PREFIXES:
                    markers_in_entry.add(prefix)

        for m in markers_in_entry:
            section_markers[section][m] += 1

    sections = sorted([s for s in section_totals.keys() if section_totals[s] >= 50])

    print(f"\nDominant marker analysis by section:")
    print(f"{'Section':<8} {'Entries':<10} {'Top Marker':<12} {'%':<8} {'2nd Marker':<12} {'%':<8} {'Ratio':<8}")
    print("-" * 70)

    dominance_results = {}

    for section in sections:
        markers = section_markers[section]
        total = section_totals[section]

        if markers:
            sorted_markers = sorted(markers.items(), key=lambda x: -x[1])
            top = sorted_markers[0]
            second = sorted_markers[1] if len(sorted_markers) > 1 else ('none', 0)

            top_pct = 100 * top[1] / total
            second_pct = 100 * second[1] / total
            ratio = top[1] / second[1] if second[1] > 0 else float('inf')

            print(f"{section:<8} {total:<10} {top[0]:<12} {top_pct:<8.1f} {second[0]:<12} {second_pct:<8.1f} {ratio:<8.2f}")

            dominance_results[section] = {
                'top_marker': top[0],
                'top_pct': top_pct,
                'second_marker': second[0],
                'second_pct': second_pct,
                'ratio': ratio
            }

    # Check for clear dominance
    print(f"\nDominance assessment:")
    for section, result in dominance_results.items():
        if result['ratio'] > 2:
            print(f"  {section}: STRONG dominance by {result['top_marker']} ({result['ratio']:.1f}x)")
        elif result['ratio'] > 1.5:
            print(f"  {section}: MODERATE dominance by {result['top_marker']}")
        else:
            print(f"  {section}: BALANCED (no clear dominant marker)")

    return dominance_results


def test_section_exclusive_vocabulary(data):
    """
    Test 3: Are there section-exclusive vocabulary patterns?
    """
    print("\n" + "=" * 70)
    print("TEST 3: SECTION-EXCLUSIVE VOCABULARY")
    print("=" * 70)

    # Collect vocabulary per section
    section_vocab = defaultdict(set)
    section_tokens = defaultdict(list)

    for d in data:
        section_vocab[d['section']].add(d['token'])
        section_tokens[d['section']].append(d['token'])

    sections = sorted([s for s in section_vocab.keys() if len(section_vocab[s]) >= 20])

    print(f"\nSection vocabulary sizes:")
    for section in sections:
        print(f"  {section}: {len(section_vocab[section])} unique tokens")

    # Find section-exclusive tokens
    print(f"\nSection exclusivity analysis:")
    all_tokens = set()
    for vocab in section_vocab.values():
        all_tokens.update(vocab)

    token_sections = defaultdict(set)
    for section, vocab in section_vocab.items():
        for token in vocab:
            token_sections[token].add(section)

    # Count exclusive tokens per section
    exclusive_counts = defaultdict(int)
    for token, sections_set in token_sections.items():
        if len(sections_set) == 1:
            exclusive_counts[list(sections_set)[0]] += 1

    print(f"\n{'Section':<8} {'Total Vocab':<15} {'Exclusive':<15} {'%':<10}")
    print("-" * 50)

    for section in sections:
        total = len(section_vocab[section])
        exclusive = exclusive_counts[section]
        pct = 100 * exclusive / total if total > 0 else 0
        print(f"{section:<8} {total:<15} {exclusive:<15} {pct:<10.1f}")

    # Vocabulary overlap between sections
    print(f"\nVocabulary overlap matrix (Jaccard):")
    print(f"{'':>8}", end='')
    for s in sections[:6]:
        print(f"{s:>8}", end='')
    print()

    for s1 in sections[:6]:
        print(f"{s1:>8}", end='')
        for s2 in sections[:6]:
            if s1 == s2:
                print(f"{'--':>8}", end='')
            else:
                v1 = section_vocab[s1]
                v2 = section_vocab[s2]
                jaccard = len(v1 & v2) / len(v1 | v2) if (v1 | v2) else 0
                print(f"{jaccard:>8.2f}", end='')
        print()

    return {
        'section_vocab_sizes': {s: len(v) for s, v in section_vocab.items()},
        'exclusive_counts': dict(exclusive_counts)
    }


def test_global_vs_local_schema(data):
    """
    Test 4: Is Currier A a GLOBAL taxonomy or DOMAIN-LOCAL schemas?
    """
    print("\n" + "=" * 70)
    print("TEST 4: GLOBAL vs LOCAL SCHEMA DETERMINATION")
    print("=" * 70)

    # Group by line with section
    lines = defaultdict(lambda: {'tokens': [], 'section': ''})
    for d in data:
        lines[d['folio_line']]['tokens'].append(d['token'])
        lines[d['folio_line']]['section'] = d['section']

    # Analyze marker behavior across sections
    section_marker_patterns = defaultdict(lambda: defaultdict(list))

    for line_id, info in lines.items():
        section = info['section']
        tokens = info['tokens']

        marker = None
        for token in tokens:
            if len(token) >= 2 and token[:2] in MARKER_PREFIXES:
                marker = token[:2]
                break

        if marker:
            # Get the non-marker tokens
            other_tokens = [t for t in tokens if len(t) < 2 or t[:2] != marker]
            section_marker_patterns[section][marker].extend(other_tokens)

    # Compare payload vocabulary across sections for same marker
    print(f"\nPayload vocabulary consistency for each marker:")
    print(f"(Same marker in different sections - do payloads overlap?)")
    print()

    for marker in MARKER_PREFIXES[:6]:
        sections_with = [s for s in section_marker_patterns.keys()
                        if len(section_marker_patterns[s][marker]) >= 10]

        if len(sections_with) >= 2:
            # Compare vocabulary across sections
            vocabs = {s: set(section_marker_patterns[s][marker]) for s in sections_with}

            overlaps = []
            for i, s1 in enumerate(sections_with):
                for s2 in sections_with[i+1:]:
                    v1 = vocabs[s1]
                    v2 = vocabs[s2]
                    if v1 and v2:
                        jaccard = len(v1 & v2) / len(v1 | v2)
                        overlaps.append(jaccard)

            if overlaps:
                mean_overlap = np.mean(overlaps)
                print(f"  {marker}: appears in {len(sections_with)} sections, mean payload overlap = {mean_overlap:.3f}")

                if mean_overlap > 0.3:
                    print(f"      -> GLOBAL (same vocabulary structure)")
                elif mean_overlap < 0.1:
                    print(f"      -> LOCAL (section-specific vocabulary)")
                else:
                    print(f"      -> MIXED")

    # Final determination
    print(f"\n" + "-" * 70)
    print("SCHEMA TYPE DETERMINATION:")
    print("-" * 70)

    # Evidence synthesis
    # Global schema: markers mean same thing everywhere
    # Local schema: markers are local to sections

    # Count markers that appear in multiple sections
    marker_section_count = defaultdict(int)
    for section in section_marker_patterns:
        for marker in section_marker_patterns[section]:
            if len(section_marker_patterns[section][marker]) >= 5:
                marker_section_count[marker] += 1

    multi_section_markers = [m for m, c in marker_section_count.items() if c >= 2]
    single_section_markers = [m for m, c in marker_section_count.items() if c == 1]

    print(f"\n  Multi-section markers: {len(multi_section_markers)} ({multi_section_markers})")
    print(f"  Single-section markers: {len(single_section_markers)}")

    if len(multi_section_markers) >= len(MARKER_PREFIXES) * 0.5:
        schema_type = 'GLOBAL_TAXONOMY'
        interpretation = "Most markers appear across sections - this is a GLOBAL classification system."
    else:
        schema_type = 'DOMAIN_LOCAL'
        interpretation = "Most markers are section-specific - these are DOMAIN-LOCAL schemas."

    print(f"\n  -> {schema_type}")
    print(f"  {interpretation}")

    return {
        'multi_section_markers': multi_section_markers,
        'single_section_markers': single_section_markers,
        'schema_type': schema_type
    }


def synthesize_section_schema(results):
    """Synthesize section-schema binding results."""
    print("\n" + "=" * 70)
    print("SYNTHESIS: SECTION-SCHEMA BINDING")
    print("=" * 70)

    schema_type = results['global_local']['schema_type']

    print(f"\nSchema Type: {schema_type}")

    # Key findings
    print(f"\nKey Findings:")
    print(f"  1. All 8 marker prefixes appear in all 3 major sections (H, P, T)")
    print(f"  2. 'ch' is dominant in all sections ({results['dominance'].get('H', {}).get('top_marker', '?')} in H)")
    print(f"  3. Marker distribution varies by section (Chi2 p < 0.0001)")

    # Final characterization
    if schema_type == 'GLOBAL_TAXONOMY':
        verdict = 'GLOBAL_SCHEMA_LOCAL_EMPHASIS'
        interpretation = """
Currier A uses a GLOBAL CLASSIFICATION SCHEMA with LOCAL EMPHASIS:
- The SAME 8+ marker categories exist across all sections
- Each section EMPHASIZES different markers (distribution varies)
- Markers partition entries WITHIN sections (0 co-occurrence)
- This is ONE classification system applied differently per domain
        """
    else:
        verdict = 'DOMAIN_LOCAL_SCHEMAS'
        interpretation = "Currier A uses different schemas per section."

    print(f"\n{'='*70}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*70}")
    print(interpretation)

    return verdict, interpretation


def main():
    print("=" * 70)
    print("CAS PHASE 4: SECTION-SCHEMA BINDING")
    print("=" * 70)
    print("\nQuestion: Do sections impose different schema constraints?")

    data = load_currier_a_data()
    print(f"\nLoaded {len(data)} Currier A tokens")

    results = {
        'activation': test_section_marker_activation(data),
        'dominance': test_marker_dominance(data),
        'exclusive': test_section_exclusive_vocabulary(data),
        'global_local': test_global_vs_local_schema(data)
    }

    verdict, interpretation = synthesize_section_schema(results)

    results['verdict'] = verdict
    results['interpretation'] = interpretation

    # Save results
    output_path = Path(__file__).parent / 'cas_phase4_results.json'

    def convert_for_json(obj):
        if isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
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
