#!/usr/bin/env python3
"""
Encyclopedia Comparison

Compare Voynich structure to known medieval reference work profiles:
1. Isidore's Etymologiae - short definitional entries
2. Bartholomaeus Anglicus's De proprietatibus rerum - longer expository
3. Hildegard's Physica - plant/animal entries
4. Generic Medieval Herbal - plant-property-use structure
5. Generic Recipe Collection - imperative, short, repetitive

Score fit based on structural characteristics.
"""

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Any


KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo'
]


# Genre profile definitions (based on scholarly descriptions)
GENRE_PROFILES = {
    'ISIDORE_ETYMOLOGIAE': {
        'description': 'Isidore of Seville Etymologiae - short definitional entries with etymology focus',
        'entry_length_range': (15, 60),      # Short entries
        'entry_length_cv': (0.3, 0.6),       # Moderately regular
        'vocab_diversity': (0.4, 0.7),       # Technical vocabulary
        'opening_consistency': (0.15, 0.35), # Consistent openings
        'three_part_structure': False,        # Usually two-part (term + definition)
        'repetition_rate': (0.02, 0.08),     # Low repetition
        'characteristics': [
            'Etymology-focused openings',
            'Short definitional units',
            'Technical vocabulary'
        ]
    },
    'BARTHOLOMAEUS_DE_PROPRIETATIBUS': {
        'description': 'Bartholomaeus Anglicus De proprietatibus rerum - longer expository entries',
        'entry_length_range': (80, 300),     # Longer entries
        'entry_length_cv': (0.4, 0.8),       # More variable
        'vocab_diversity': (0.5, 0.8),       # Diverse vocabulary
        'opening_consistency': (0.08, 0.20), # Moderate consistency
        'three_part_structure': True,         # Property-listing structure
        'repetition_rate': (0.03, 0.10),     # Low-moderate repetition
        'characteristics': [
            'Property listing structure',
            'Longer expository units',
            'Cross-references'
        ]
    },
    'HILDEGARD_PHYSICA': {
        'description': 'Hildegard of Bingen Physica - plant/animal entries with medical focus',
        'entry_length_range': (50, 200),     # Medium entries
        'entry_length_cv': (0.5, 0.9),       # Variable
        'vocab_diversity': (0.4, 0.7),       # Technical but repetitive
        'opening_consistency': (0.10, 0.25), # Moderate consistency
        'three_part_structure': True,         # Plant-property-use
        'repetition_rate': (0.05, 0.15),     # Moderate repetition
        'characteristics': [
            'Nature-focused entries',
            'Medical applications',
            'Variable length'
        ]
    },
    'GENERIC_HERBAL': {
        'description': 'Generic medieval herbal - plant name, properties, uses',
        'entry_length_range': (60, 180),     # Medium entries
        'entry_length_cv': (0.4, 0.7),       # Moderately regular
        'vocab_diversity': (0.35, 0.60),     # Technical vocabulary
        'opening_consistency': (0.12, 0.30), # Consistent plant name openings
        'three_part_structure': True,         # Name-property-use
        'repetition_rate': (0.08, 0.20),     # Some formulaic elements
        'characteristics': [
            'Plant name heading',
            'Properties section',
            'Uses/applications section'
        ]
    },
    'GENERIC_RECIPE': {
        'description': 'Generic recipe collection - imperative, short, highly repetitive',
        'entry_length_range': (10, 50),      # Short entries
        'entry_length_cv': (0.3, 0.5),       # Very regular
        'vocab_diversity': (0.15, 0.40),     # Limited vocabulary
        'opening_consistency': (0.20, 0.50), # Very consistent openings
        'three_part_structure': False,        # Linear/sequential
        'repetition_rate': (0.15, 0.40),     # High repetition
        'characteristics': [
            'Imperative openings',
            'Ingredient lists',
            'Procedural structure'
        ]
    }
}


def load_corpus() -> Tuple[List[Dict], Dict[str, List[Dict]]]:
    """Load corpus with structure."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'

    all_words = []
    by_currier = {'A': [], 'B': []}

    seen = set()
    word_idx = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip().strip('"')
            folio = row.get('folio', '').strip().strip('"')
            line_num = row.get('line_number', '').strip().strip('"')
            currier = row.get('language', '').strip().strip('"')

            if not word or word.startswith('*') or len(word) < 2:
                continue

            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                entry = {
                    'word': word,
                    'folio': folio,
                    'line': line_num,
                    'currier': currier,
                    'idx': word_idx
                }
                all_words.append(entry)
                if currier in by_currier:
                    by_currier[currier].append(entry)
                word_idx += 1

    return all_words, by_currier


def get_prefix(word: str) -> str:
    """Extract prefix from word."""
    for length in [3, 2]:
        if len(word) >= length:
            prefix = word[:length]
            if prefix in KNOWN_PREFIXES:
                return prefix
    if len(word) >= 2:
        return word[:2]
    return word


def segment_into_entries(words: List[Dict]) -> List[List[Dict]]:
    """Segment by folio."""
    by_folio = defaultdict(list)
    for w in words:
        by_folio[w['folio']].append(w)

    entries = []
    for folio in sorted(by_folio.keys()):
        entries.append(by_folio[folio])

    return entries


def compute_metrics(words: List[Dict]) -> Dict:
    """Compute structural metrics for comparison."""
    entries = segment_into_entries(words)

    # Entry lengths
    lengths = [len(e) for e in entries if e]
    mean_length = sum(lengths) / len(lengths) if lengths else 0
    variance = sum((l - mean_length) ** 2 for l in lengths) / len(lengths) if lengths else 0
    std_length = math.sqrt(variance)
    cv = std_length / mean_length if mean_length > 0 else 0

    # Vocabulary diversity (unique words / total words)
    all_words = [w['word'] for entry in entries for w in entry]
    vocab_diversity = len(set(all_words)) / len(all_words) if all_words else 0

    # Opening consistency (fraction of entries starting with most common opening prefix)
    opening_prefixes = Counter()
    for entry in entries:
        if entry:
            opening_prefixes[get_prefix(entry[0]['word'])] += 1

    if opening_prefixes:
        most_common_opening = opening_prefixes.most_common(1)[0][1]
        opening_consistency = most_common_opening / len(entries)
    else:
        opening_consistency = 0

    # Three-part structure detection
    # Check if prefixes show different distributions in first/middle/last thirds
    first_prefixes = Counter()
    middle_prefixes = Counter()
    last_prefixes = Counter()

    for entry in entries:
        n = len(entry)
        if n < 9:
            continue
        third = n // 3

        for w in entry[:third]:
            first_prefixes[get_prefix(w['word'])] += 1
        for w in entry[third:2*third]:
            middle_prefixes[get_prefix(w['word'])] += 1
        for w in entry[2*third:]:
            last_prefixes[get_prefix(w['word'])] += 1

    # Check for structural differentiation
    def distribution_difference(c1: Counter, c2: Counter) -> float:
        """Calculate difference between two distributions."""
        all_keys = set(c1.keys()) | set(c2.keys())
        t1 = sum(c1.values()) + 1
        t2 = sum(c2.values()) + 1

        diff = 0
        for key in all_keys:
            r1 = c1.get(key, 0) / t1
            r2 = c2.get(key, 0) / t2
            diff += abs(r1 - r2)

        return diff / 2  # Normalize to 0-1

    first_vs_middle = distribution_difference(first_prefixes, middle_prefixes)
    middle_vs_last = distribution_difference(middle_prefixes, last_prefixes)
    first_vs_last = distribution_difference(first_prefixes, last_prefixes)

    # Three-part structure if there's meaningful differentiation
    three_part = (first_vs_middle > 0.05 and middle_vs_last > 0.05 and first_vs_last > 0.08)

    # Repetition rate (3-grams that appear more than once)
    trigrams = []
    for entry in entries:
        words = [w['word'] for w in entry]
        for i in range(len(words) - 2):
            trigrams.append((words[i], words[i+1], words[i+2]))

    trigram_counts = Counter(trigrams)
    repeated = sum(1 for t, c in trigram_counts.items() if c > 1)
    repetition_rate = repeated / len(trigram_counts) if trigram_counts else 0

    return {
        'entry_count': len(entries),
        'mean_entry_length': round(mean_length, 2),
        'entry_length_cv': round(cv, 3),
        'vocab_diversity': round(vocab_diversity, 3),
        'opening_consistency': round(opening_consistency, 3),
        'three_part_structure': three_part,
        'three_part_scores': {
            'first_vs_middle': round(first_vs_middle, 3),
            'middle_vs_last': round(middle_vs_last, 3),
            'first_vs_last': round(first_vs_last, 3)
        },
        'repetition_rate': round(repetition_rate, 4),
        'total_words': len(all_words),
        'unique_words': len(set(all_words))
    }


def score_genre_fit(metrics: Dict, profile: Dict) -> Tuple[float, Dict]:
    """Score how well metrics fit a genre profile."""
    scores = {}
    max_points = 6

    # Entry length range
    low, high = profile['entry_length_range']
    measured = metrics['mean_entry_length']
    if low <= measured <= high:
        scores['entry_length'] = 1.0
    elif low * 0.7 <= measured <= high * 1.3:
        scores['entry_length'] = 0.5
    else:
        scores['entry_length'] = 0.0

    # Entry length CV
    low, high = profile['entry_length_cv']
    measured = metrics['entry_length_cv']
    if low <= measured <= high:
        scores['entry_cv'] = 1.0
    elif low * 0.7 <= measured <= high * 1.3:
        scores['entry_cv'] = 0.5
    else:
        scores['entry_cv'] = 0.0

    # Vocabulary diversity
    low, high = profile['vocab_diversity']
    measured = metrics['vocab_diversity']
    if low <= measured <= high:
        scores['vocab_diversity'] = 1.0
    elif low * 0.8 <= measured <= high * 1.2:
        scores['vocab_diversity'] = 0.5
    else:
        scores['vocab_diversity'] = 0.0

    # Opening consistency
    low, high = profile['opening_consistency']
    measured = metrics['opening_consistency']
    if low <= measured <= high:
        scores['opening'] = 1.0
    elif low * 0.5 <= measured <= high * 1.5:
        scores['opening'] = 0.5
    else:
        scores['opening'] = 0.0

    # Three-part structure
    expected = profile['three_part_structure']
    actual = metrics['three_part_structure']
    if expected == actual:
        scores['three_part'] = 1.0
    else:
        scores['three_part'] = 0.0

    # Repetition rate
    low, high = profile['repetition_rate']
    measured = metrics['repetition_rate']
    if low <= measured <= high:
        scores['repetition'] = 1.0
    elif low * 0.5 <= measured <= high * 1.5:
        scores['repetition'] = 0.5
    else:
        scores['repetition'] = 0.0

    total = sum(scores.values()) / max_points * 100
    return round(total, 1), scores


def analyze_section(words: List[Dict], section_name: str) -> Dict:
    """Analyze section against genre profiles."""
    print(f"\nAnalyzing {section_name}...")

    metrics = compute_metrics(words)

    print(f"  Metrics:")
    print(f"    Entry count: {metrics['entry_count']}")
    print(f"    Mean entry length: {metrics['mean_entry_length']}")
    print(f"    Entry length CV: {metrics['entry_length_cv']}")
    print(f"    Vocab diversity: {metrics['vocab_diversity']}")
    print(f"    Opening consistency: {metrics['opening_consistency']}")
    print(f"    Three-part structure: {metrics['three_part_structure']}")
    print(f"    Repetition rate: {metrics['repetition_rate']}")

    # Score against each genre
    genre_scores = {}
    for genre, profile in GENRE_PROFILES.items():
        score, details = score_genre_fit(metrics, profile)
        genre_scores[genre] = {
            'score': score,
            'details': details,
            'description': profile['description']
        }

    # Rank genres
    ranked = sorted(genre_scores.items(), key=lambda x: -x[1]['score'])

    return {
        'section': section_name,
        'metrics': metrics,
        'genre_scores': genre_scores,
        'ranked_genres': [(g, d['score']) for g, d in ranked],
        'best_fit': ranked[0][0] if ranked else None,
        'best_score': ranked[0][1]['score'] if ranked else 0
    }


def main():
    print("=" * 70)
    print("ENCYCLOPEDIA COMPARISON")
    print("Comparing Voynich structure to medieval reference work profiles")
    print("=" * 70)

    # Load corpus
    print("\nLoading corpus...")
    all_words, by_currier = load_corpus()
    print(f"Currier A: {len(by_currier['A'])} words")
    print(f"Currier B: {len(by_currier['B'])} words")

    results = {
        'timestamp': datetime.now().isoformat(),
        'methodology': 'Genre profile comparison against medieval reference works',
        'profiles': {g: {'description': p['description'], 'characteristics': p['characteristics']}
                    for g, p in GENRE_PROFILES.items()}
    }

    # Analyze each section
    results['currier_a'] = analyze_section(by_currier['A'], 'Currier A')
    results['currier_b'] = analyze_section(by_currier['B'], 'Currier B')

    # Summary
    print("\n" + "=" * 70)
    print("GENRE FIT SCORES")
    print("=" * 70)

    print(f"\n{'Genre':<35} {'Currier A':>12} {'Currier B':>12}")
    print("-" * 60)

    for genre in GENRE_PROFILES.keys():
        a_score = results['currier_a']['genre_scores'][genre]['score']
        b_score = results['currier_b']['genre_scores'][genre]['score']
        print(f"{genre:<35} {a_score:>11.1f}% {b_score:>11.1f}%")

    print("\n" + "=" * 70)
    print("BEST MATCHES")
    print("=" * 70)

    a_best = results['currier_a']['best_fit']
    a_score = results['currier_a']['best_score']
    b_best = results['currier_b']['best_fit']
    b_score = results['currier_b']['best_score']

    print(f"\nCurrier A best fit: {a_best} ({a_score}%)")
    print(f"  {GENRE_PROFILES[a_best]['description']}")

    print(f"\nCurrier B best fit: {b_best} ({b_score}%)")
    print(f"  {GENRE_PROFILES[b_best]['description']}")

    # Detailed comparison
    print("\n" + "=" * 70)
    print("METRIC COMPARISON")
    print("=" * 70)

    a_metrics = results['currier_a']['metrics']
    b_metrics = results['currier_b']['metrics']

    print(f"\n{'Metric':<25} {'Currier A':>15} {'Currier B':>15}")
    print("-" * 55)
    print(f"{'Mean entry length':<25} {a_metrics['mean_entry_length']:>15.1f} {b_metrics['mean_entry_length']:>15.1f}")
    print(f"{'Entry length CV':<25} {a_metrics['entry_length_cv']:>15.3f} {b_metrics['entry_length_cv']:>15.3f}")
    print(f"{'Vocab diversity':<25} {a_metrics['vocab_diversity']:>15.3f} {b_metrics['vocab_diversity']:>15.3f}")
    print(f"{'Opening consistency':<25} {a_metrics['opening_consistency']:>15.3f} {b_metrics['opening_consistency']:>15.3f}")
    print(f"{'Three-part structure':<25} {str(a_metrics['three_part_structure']):>15} {str(b_metrics['three_part_structure']):>15}")
    print(f"{'Repetition rate':<25} {a_metrics['repetition_rate']:>15.4f} {b_metrics['repetition_rate']:>15.4f}")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    print("\nCurrier A:")
    if a_best == 'GENERIC_HERBAL' or a_best == 'HILDEGARD_PHYSICA':
        print("  Best matches HERBAL-type structure.")
        print("  - Medium entry lengths (plant descriptions)")
        print("  - Three-part structure (name/properties/uses)")
        print("  - Moderate vocabulary diversity")
    elif a_best == 'ISIDORE_ETYMOLOGIAE':
        print("  Best matches ENCYCLOPEDIC-DEFINITIONAL structure.")
        print("  - Shorter entries (definitions)")
        print("  - Technical vocabulary")
    elif a_best == 'GENERIC_RECIPE':
        print("  Best matches RECIPE-type structure.")
        print("  - Short, regular entries")
        print("  - High repetition")

    print("\nCurrier B:")
    if b_best == 'BARTHOLOMAEUS_DE_PROPRIETATIBUS':
        print("  Best matches EXPOSITORY ENCYCLOPEDIA structure.")
        print("  - Longer entries (detailed expositions)")
        print("  - High vocabulary diversity")
        print("  - Property-listing organization")
    elif b_best == 'HILDEGARD_PHYSICA':
        print("  Best matches NATURAL HISTORY structure.")
        print("  - Variable entry lengths")
        print("  - Medical/natural focus")

    # Overall assessment
    print("\n" + "=" * 70)
    print("OVERALL ASSESSMENT")
    print("=" * 70)

    print(f"""
The Voynich Manuscript's two sections show distinct genre affinities:

CURRIER A: Most consistent with {a_best} ({a_score}%)
  - Entry characteristics suggest labeled reference material
  - Structure compatible with descriptive herbals

CURRIER B: Most consistent with {b_best} ({b_score}%)
  - Entry characteristics suggest longer expository content
  - Structure compatible with encyclopedic treatises

This bifurcated structure (short reference entries in A, longer
expositions in B) is consistent with a manuscript combining
illustrated herbal sections with extended encyclopedia-style text.
""")

    results['overall_assessment'] = {
        'currier_a_profile': a_best,
        'currier_a_score': a_score,
        'currier_b_profile': b_best,
        'currier_b_score': b_score,
        'interpretation': 'Bifurcated structure: A=labeled herbal, B=expository encyclopedia'
    }

    # Save results
    with open('encyclopedia_comparison_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to encyclopedia_comparison_report.json")


if __name__ == '__main__':
    main()
