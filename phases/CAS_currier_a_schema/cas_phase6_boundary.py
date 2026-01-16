"""
CAS Phase 6: A/B Interaction Boundary

Question: Is A/B separation designed or accidental?

Tests:
1. A-B adjacency patterns (do they appear near each other?)
2. Boundary strictness (hard vs soft transitions)
3. Vocabulary sharing (do A and B share tokens?)
4. Transition patterns at boundaries
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np

project_root = Path(__file__).parent.parent.parent


def load_all_data():
    """Load all tokens with language designation (PRIMARY transcriber H only)."""
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
                    line_num = parts[line_idx].strip('"').strip() if len(parts) > line_idx else ''
                    section = parts[section_idx].strip('"').strip() if len(parts) > section_idx else ''

                    if word:
                        data.append({
                            'token': word,
                            'folio': folio,
                            'line': line_num,
                            'section': section,
                            'language': lang,
                            'folio_line': f"{folio}_{line_num}"
                        })

    return data


def test_adjacency_patterns(data):
    """
    Test 1: A-B adjacency patterns

    Do A and B tokens appear adjacent to each other?
    """
    print("\n" + "=" * 70)
    print("TEST 1: A-B ADJACENCY PATTERNS")
    print("=" * 70)

    # Count transitions
    transitions = Counter()
    prev_lang = None

    for d in data:
        curr_lang = d['language']
        if prev_lang:
            transitions[(prev_lang, curr_lang)] += 1
        prev_lang = curr_lang

    total = sum(transitions.values())

    print(f"\nToken-to-token transitions:")
    print(f"  A -> A: {transitions[('A','A')]} ({100*transitions[('A','A')]/total:.1f}%)")
    print(f"  A -> B: {transitions[('A','B')]} ({100*transitions[('A','B')]/total:.1f}%)")
    print(f"  B -> A: {transitions[('B','A')]} ({100*transitions[('B','A')]/total:.1f}%)")
    print(f"  B -> B: {transitions[('B','B')]} ({100*transitions[('B','B')]/total:.1f}%)")

    # Cross-language transitions
    cross = transitions[('A','B')] + transitions[('B','A')]
    same = transitions[('A','A')] + transitions[('B','B')]

    print(f"\n  Cross-language transitions: {cross} ({100*cross/total:.1f}%)")
    print(f"  Same-language transitions: {same} ({100*same/total:.1f}%)")

    # If perfectly separated, cross should be near 0
    if cross / total < 0.01:
        print("  -> HARD BOUNDARY (A and B never adjacent)")
    elif cross / total < 0.05:
        print("  -> SOFT BOUNDARY (rare adjacency)")
    else:
        print("  -> INTERMIXED (frequent adjacency)")

    return {
        'transitions': dict(transitions),
        'cross_pct': cross / total,
        'same_pct': same / total
    }


def test_boundary_locations(data):
    """
    Test 2: Where do A/B boundaries occur?
    """
    print("\n" + "=" * 70)
    print("TEST 2: BOUNDARY LOCATION ANALYSIS")
    print("=" * 70)

    # Group by folio
    folio_langs = defaultdict(lambda: {'A': 0, 'B': 0})

    for d in data:
        folio_langs[d['folio']][d['language']] += 1

    # Classify folios
    pure_a = []
    pure_b = []
    mixed = []

    for folio, counts in folio_langs.items():
        if counts['A'] > 0 and counts['B'] == 0:
            pure_a.append(folio)
        elif counts['B'] > 0 and counts['A'] == 0:
            pure_b.append(folio)
        else:
            mixed.append(folio)

    total_folios = len(folio_langs)

    print(f"\nFolio classification:")
    print(f"  Pure A folios: {len(pure_a)} ({100*len(pure_a)/total_folios:.1f}%)")
    print(f"  Pure B folios: {len(pure_b)} ({100*len(pure_b)/total_folios:.1f}%)")
    print(f"  Mixed folios: {len(mixed)} ({100*len(mixed)/total_folios:.1f}%)")

    if mixed:
        print(f"\nMixed folios (first 20): {mixed[:20]}")

        # Analyze mixing patterns in mixed folios
        print(f"\nMixing patterns in mixed folios:")
        for folio in mixed[:5]:
            counts = folio_langs[folio]
            a_pct = 100 * counts['A'] / (counts['A'] + counts['B'])
            print(f"  {folio}: A={counts['A']} ({a_pct:.0f}%), B={counts['B']}")

    # Boundary strictness
    if len(mixed) / total_folios < 0.05:
        print(f"\n  -> STRICT separation (A/B boundaries align with folios)")
    elif len(mixed) / total_folios < 0.20:
        print(f"\n  -> MOSTLY strict (few mixed folios)")
    else:
        print(f"\n  -> LOOSE separation (many mixed folios)")

    return {
        'pure_a': len(pure_a),
        'pure_b': len(pure_b),
        'mixed': len(mixed),
        'mixed_pct': len(mixed) / total_folios
    }


def test_vocabulary_sharing(data):
    """
    Test 3: Do A and B share vocabulary?
    """
    print("\n" + "=" * 70)
    print("TEST 3: VOCABULARY SHARING")
    print("=" * 70)

    # Collect vocabulary by language
    vocab_a = set()
    vocab_b = set()

    for d in data:
        if d['language'] == 'A':
            vocab_a.add(d['token'])
        else:
            vocab_b.add(d['token'])

    shared = vocab_a & vocab_b
    a_only = vocab_a - vocab_b
    b_only = vocab_b - vocab_a

    print(f"\nVocabulary comparison:")
    print(f"  A vocabulary: {len(vocab_a)} unique tokens")
    print(f"  B vocabulary: {len(vocab_b)} unique tokens")
    print(f"  Shared: {len(shared)} ({100*len(shared)/len(vocab_a|vocab_b):.1f}%)")
    print(f"  A-only: {len(a_only)} ({100*len(a_only)/len(vocab_a):.1f}% of A)")
    print(f"  B-only: {len(b_only)} ({100*len(b_only)/len(vocab_b):.1f}% of B)")

    # Jaccard similarity
    jaccard = len(shared) / len(vocab_a | vocab_b)
    print(f"\n  Jaccard similarity: {jaccard:.3f}")

    # Top shared tokens
    print(f"\nTop 15 shared tokens (by A frequency):")
    a_counts = Counter(d['token'] for d in data if d['language'] == 'A')
    shared_sorted = sorted(shared, key=lambda t: a_counts[t], reverse=True)

    for token in shared_sorted[:15]:
        a_ct = a_counts[token]
        b_ct = sum(1 for d in data if d['token'] == token and d['language'] == 'B')
        print(f"  {token}: A={a_ct}, B={b_ct}")

    # Sharing interpretation
    if jaccard < 0.1:
        print(f"\n  -> DISJOINT vocabularies (A and B are separate systems)")
    elif jaccard < 0.3:
        print(f"\n  -> LOW overlap (some shared functional tokens)")
    else:
        print(f"\n  -> SIGNIFICANT overlap (shared vocabulary base)")

    return {
        'vocab_a': len(vocab_a),
        'vocab_b': len(vocab_b),
        'shared': len(shared),
        'jaccard': jaccard,
        'top_shared': shared_sorted[:20]
    }


def test_section_separation(data):
    """
    Test 4: How does A/B distribution vary by section?
    """
    print("\n" + "=" * 70)
    print("TEST 4: SECTION-LEVEL SEPARATION")
    print("=" * 70)

    # Count by section and language
    section_langs = defaultdict(lambda: {'A': 0, 'B': 0})

    for d in data:
        section_langs[d['section']][d['language']] += 1

    sections = sorted(section_langs.keys())

    print(f"\nLanguage distribution by section:")
    print(f"{'Section':<10} {'A':<10} {'B':<10} {'A%':<10} {'Status':<15}")
    print("-" * 55)

    for section in sections:
        a_ct = section_langs[section]['A']
        b_ct = section_langs[section]['B']
        total = a_ct + b_ct
        a_pct = 100 * a_ct / total if total > 0 else 0

        if a_pct > 90:
            status = "A-DOMINANT"
        elif a_pct < 10:
            status = "B-DOMINANT"
        elif a_pct > 60:
            status = "A-LEANING"
        elif a_pct < 40:
            status = "B-LEANING"
        else:
            status = "MIXED"

        print(f"{section:<10} {a_ct:<10} {b_ct:<10} {a_pct:<10.1f} {status:<15}")

    return {
        'section_langs': {s: dict(l) for s, l in section_langs.items()}
    }


def synthesize_boundary(results):
    """Synthesize A/B boundary analysis."""
    print("\n" + "=" * 70)
    print("SYNTHESIS: A/B BOUNDARY CHARACTERIZATION")
    print("=" * 70)

    cross_pct = results['adjacency']['cross_pct']
    mixed_pct = results['boundary']['mixed_pct']
    jaccard = results['vocab']['jaccard']

    print(f"\nKey metrics:")
    print(f"  Cross-language adjacency: {cross_pct:.1%}")
    print(f"  Mixed folios: {mixed_pct:.1%}")
    print(f"  Vocabulary Jaccard: {jaccard:.3f}")

    # Scoring
    designed_score = 0

    if cross_pct < 0.05:
        designed_score += 1
        print(f"\n[+] Low adjacency -> separation is deliberate")

    if mixed_pct < 0.20:
        designed_score += 1
        print(f"[+] Few mixed folios -> boundaries are structural")

    if jaccard < 0.3:
        designed_score += 1
        print(f"[+] Low vocabulary overlap -> distinct systems")

    print(f"\nDesigned separation score: {designed_score}/3")

    if designed_score >= 2:
        verdict = 'DESIGNED_SEPARATION'
        interpretation = """
The A/B separation appears DESIGNED, not accidental:
- A and B rarely appear adjacent
- Boundaries align with folio/section structure
- Vocabularies are largely disjoint
- This suggests TWO INTENTIONAL SYSTEMS, not author drift
        """
    else:
        verdict = 'ACCIDENTAL_VARIATION'
        interpretation = "A/B separation appears to be gradual variation, not designed boundary."

    print(f"\n{'='*70}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*70}")
    print(interpretation)

    return verdict, interpretation


def main():
    print("=" * 70)
    print("CAS PHASE 6: A/B INTERACTION BOUNDARY")
    print("=" * 70)
    print("\nQuestion: Is A/B separation designed or accidental?")

    data = load_all_data()
    print(f"\nLoaded {len(data)} tokens (A + B)")

    a_count = sum(1 for d in data if d['language'] == 'A')
    b_count = sum(1 for d in data if d['language'] == 'B')
    print(f"  A: {a_count} ({100*a_count/len(data):.1f}%)")
    print(f"  B: {b_count} ({100*b_count/len(data):.1f}%)")

    results = {
        'adjacency': test_adjacency_patterns(data),
        'boundary': test_boundary_locations(data),
        'vocab': test_vocabulary_sharing(data),
        'section': test_section_separation(data)
    }

    verdict, interpretation = synthesize_boundary(results)

    results['verdict'] = verdict
    results['interpretation'] = interpretation

    # Save results
    output_path = Path(__file__).parent / 'cas_phase6_results.json'

    def convert_for_json(obj):
        if isinstance(obj, dict):
            # Convert tuple keys to strings
            return {str(k) if isinstance(k, tuple) else k: convert_for_json(v) for k, v in obj.items()}
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
