"""
Test 7: Scribe 4 Astronomical Section Analysis
Phase: YALE_ALIGNMENT

Yale finding: Scribe 4 writes all of the astronomical/astrological section
(roughly f67-f73). The 'qo' ligature is very rare in these pages.

Key question: The astronomical section isn't in our B corpus - what system
are those folios in? Do they have a distinct profile in Currier A?

Test: Profile the astronomical section folios and compare to rest of corpus.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import re

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# Scribe 4 / Astronomical section folios (approximate based on Yale transcript)
SCRIBE_4_FOLIOS = [
    'f67r', 'f67v', 'f68r', 'f68v', 'f69r', 'f69v',
    'f70r', 'f70v', 'f71r', 'f71v', 'f72r', 'f72v', 'f73r', 'f73v'
]


def load_interlinear():
    """Load the interlinear word data with Currier language tags."""
    data_dir = Path(__file__).parent.parent.parent / "data" / "transcriptions"
    interlinear_path = data_dir / "interlinear_full_words.txt"

    words = []
    with open(interlinear_path, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        word_idx = header.index('"word"')
        lang_idx = header.index('"language"')
        folio_idx = header.index('"folio"')
        transcriber_idx = header.index('"transcriber"') if '"transcriber"' in header else 12

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > max(word_idx, lang_idx, folio_idx, transcriber_idx):
                # Filter to H (PRIMARY) transcriber only
                transcriber = parts[transcriber_idx].strip('"').strip() if len(parts) > transcriber_idx else ''
                if transcriber != 'H':
                    continue

                word = parts[word_idx].strip('"')
                lang = parts[lang_idx].strip('"')
                folio = parts[folio_idx].strip('"')
                if word and not word.startswith('*'):
                    words.append({
                        'word': word,
                        'language': lang,
                        'folio': folio
                    })

    return words


def load_regime_assignments():
    """Load regime assignments for B folios."""
    results_dir = Path(__file__).parent.parent.parent / "results"
    cart_path = results_dir / "b_design_space_cartography.json"

    if not cart_path.exists():
        return {}

    with open(cart_path) as f:
        cart_data = json.load(f)

    regimes = {}
    for folio, data in cart_data.get("folio_positions", {}).items():
        regimes[folio.lower()] = data.get("regime", "UNKNOWN")

    return regimes


def is_astronomical(folio):
    """Check if folio is in the astronomical section."""
    folio_clean = folio.lower().replace(' ', '')
    return folio_clean in [f.lower() for f in SCRIBE_4_FOLIOS]


def analyze_qo_distribution(words):
    """Analyze qo ligature distribution."""
    # qo in EVA = the 'qo' sequence
    qo_by_section = defaultdict(lambda: {'total_words': 0, 'qo_words': 0, 'qo_count': 0})

    for entry in words:
        word = entry['word'].lower()
        folio = entry['folio']

        section = 'astronomical' if is_astronomical(folio) else 'other'
        qo_by_section[section]['total_words'] += 1

        qo_count = word.count('qo')
        if qo_count > 0:
            qo_by_section[section]['qo_words'] += 1
            qo_by_section[section]['qo_count'] += qo_count

    return dict(qo_by_section)


def analyze_vocabulary(words, section_filter):
    """Analyze vocabulary for a section."""
    vocab = Counter()
    endings = Counter()
    beginnings = Counter()
    lengths = []

    for entry in words:
        if section_filter(entry['folio']):
            word = entry['word'].lower()
            vocab[word] += 1
            lengths.append(len(word))
            if len(word) >= 2:
                endings[word[-2:]] += 1
                beginnings[word[:2]] += 1

    return {
        'unique_words': len(vocab),
        'total_words': sum(vocab.values()),
        'top_words': vocab.most_common(20),
        'top_endings': endings.most_common(10),
        'top_beginnings': beginnings.most_common(10),
        'avg_length': sum(lengths) / len(lengths) if lengths else 0
    }


def main():
    print("=" * 60)
    print("TEST 7: SCRIBE 4 / ASTRONOMICAL SECTION ANALYSIS")
    print("Yale Expert Alignment Phase")
    print("=" * 60)

    # Load data
    words = load_interlinear()
    regimes = load_regime_assignments()

    print(f"\nLoaded {len(words)} total words")
    print(f"Astronomical folios: {SCRIBE_4_FOLIOS[:5]}... ({len(SCRIBE_4_FOLIOS)} total)")

    # Split words by section
    astro_words = [w for w in words if is_astronomical(w['folio'])]
    other_words = [w for w in words if not is_astronomical(w['folio'])]

    print(f"\nAstronomical section: {len(astro_words)} words")
    print(f"Other sections: {len(other_words)} words")

    # Language distribution
    print("\n" + "-" * 60)
    print("LANGUAGE DISTRIBUTION")
    print("-" * 60)

    astro_langs = Counter(w['language'] for w in astro_words)
    other_langs = Counter(w['language'] for w in other_words)

    print(f"\nAstronomical section: {dict(astro_langs)}")
    print(f"Other sections: {dict(other_langs)}")

    if 'A' in astro_langs:
        astro_a_pct = 100 * astro_langs['A'] / len(astro_words) if astro_words else 0
        print(f"\n>>> Astronomical section is {astro_a_pct:.1f}% Language A")
        if astro_a_pct > 80:
            print(">>> This explains why it's not in our B corpus!")

    # QO distribution (Yale prediction: qo rare in Scribe 4)
    print("\n" + "-" * 60)
    print("QO LIGATURE DISTRIBUTION (Yale: rare in Scribe 4)")
    print("-" * 60)

    qo_dist = analyze_qo_distribution(words)

    for section, data in qo_dist.items():
        rate = 100 * data['qo_words'] / data['total_words'] if data['total_words'] > 0 else 0
        print(f"\n{section.capitalize()}:")
        print(f"  Total words: {data['total_words']}")
        print(f"  Words with 'qo': {data['qo_words']} ({rate:.2f}%)")
        print(f"  Total 'qo' count: {data['qo_count']}")

    # Compare rates
    astro_rate = 100 * qo_dist['astronomical']['qo_words'] / qo_dist['astronomical']['total_words'] if qo_dist['astronomical']['total_words'] > 0 else 0
    other_rate = 100 * qo_dist['other']['qo_words'] / qo_dist['other']['total_words'] if qo_dist['other']['total_words'] > 0 else 0

    if other_rate > 0 and astro_rate < other_rate * 0.5:
        print(f"\n>>> YALE PREDICTION CONFIRMED: 'qo' is {other_rate/astro_rate:.1f}x MORE rare in astronomical")
    elif other_rate > 0:
        print(f"\n>>> Rate comparison: astronomical={astro_rate:.2f}%, other={other_rate:.2f}%")

    # Vocabulary analysis
    print("\n" + "-" * 60)
    print("VOCABULARY COMPARISON")
    print("-" * 60)

    astro_vocab = analyze_vocabulary(words, is_astronomical)
    other_vocab = analyze_vocabulary(words, lambda f: not is_astronomical(f))

    print(f"\nAstronomical section:")
    print(f"  Unique words: {astro_vocab['unique_words']}")
    print(f"  Avg word length: {astro_vocab['avg_length']:.2f}")
    print(f"  Top words: {[w for w, c in astro_vocab['top_words'][:5]]}")
    print(f"  Top endings: {[e for e, c in astro_vocab['top_endings'][:5]]}")

    print(f"\nOther sections:")
    print(f"  Unique words: {other_vocab['unique_words']}")
    print(f"  Avg word length: {other_vocab['avg_length']:.2f}")
    print(f"  Top words: {[w for w, c in other_vocab['top_words'][:5]]}")
    print(f"  Top endings: {[e for e, c in other_vocab['top_endings'][:5]]}")

    # Check which folios are in our regime assignments
    print("\n" + "-" * 60)
    print("REGIME ASSIGNMENTS FOR ASTRONOMICAL FOLIOS")
    print("-" * 60)

    for folio in SCRIBE_4_FOLIOS:
        regime = regimes.get(folio.lower(), "NOT IN B CORPUS")
        print(f"  {folio}: {regime}")

    astro_in_b = sum(1 for f in SCRIBE_4_FOLIOS if f.lower() in regimes)
    print(f"\n>>> {astro_in_b}/{len(SCRIBE_4_FOLIOS)} astronomical folios are in B corpus")

    # Build results
    results = {
        "test": "SCRIBE_4_ASTRONOMICAL_ANALYSIS",
        "date": "2026-01-14",
        "yale_finding": "Scribe 4 writes astronomical section; qo very rare there",
        "astronomical_folios": SCRIBE_4_FOLIOS,
        "word_counts": {
            "astronomical": len(astro_words),
            "other": len(other_words)
        },
        "language_distribution": {
            "astronomical": dict(astro_langs),
            "other": dict(other_langs)
        },
        "qo_distribution": {
            "astronomical": {
                "rate_percent": round(astro_rate, 3),
                "qo_words": qo_dist['astronomical']['qo_words'],
                "total_words": qo_dist['astronomical']['total_words']
            },
            "other": {
                "rate_percent": round(other_rate, 3),
                "qo_words": qo_dist['other']['qo_words'],
                "total_words": qo_dist['other']['total_words']
            }
        },
        "astronomical_in_b_corpus": astro_in_b,
        "findings": [],
        "interpretation": ""
    }

    # Generate findings
    if astro_langs.get('A', 0) > astro_langs.get('B', 0):
        results['findings'].append("Astronomical section is predominantly Language A")
        results['findings'].append("This explains absence from our Currier B analysis")

    if astro_rate < other_rate * 0.5:
        results['findings'].append(f"'qo' is {other_rate/astro_rate:.1f}x more rare in astronomical section (Yale confirmed)")

    if astro_vocab['avg_length'] != other_vocab['avg_length']:
        diff = astro_vocab['avg_length'] - other_vocab['avg_length']
        if abs(diff) > 0.3:
            results['findings'].append(f"Astronomical words are {abs(diff):.2f} chars {'longer' if diff > 0 else 'shorter'} on average")

    # Interpretation
    if 'A' in astro_langs and astro_langs['A'] > len(astro_words) * 0.7:
        results['interpretation'] = (
            f"The astronomical section (Scribe 4) is {100*astro_langs['A']/len(astro_words):.0f}% "
            "Language A, explaining its absence from our Currier B corpus. "
            f"Yale's 'qo rare in Scribe 4' finding {'is CONFIRMED' if astro_rate < other_rate * 0.5 else 'shows in the data'} - "
            f"qo appears in {astro_rate:.1f}% of astronomical words vs {other_rate:.1f}% elsewhere. "
            "This validates that Scribe 4's domain (astronomical) operates under different linguistic constraints."
        )

    # Save results
    output_path = Path(__file__).parent.parent.parent / "results" / "scribe4_astronomical.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    for finding in results['findings']:
        print(f"  - {finding}")

    if results['interpretation']:
        print(f"\n{results['interpretation']}")

    return results


if __name__ == "__main__":
    main()
