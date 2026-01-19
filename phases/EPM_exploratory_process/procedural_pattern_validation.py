#!/usr/bin/env python3
"""
Procedural Pattern Validation

Test whether PLANT -> PROCESS -> BODY patterns are real semantic
relationships or artifacts of tagging methodology.

Four randomization tests with 100 trials each.
Success criterion: z-score >= 3 (p < 0.001)
"""

import csv
import json
import math
import random
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any


# Category mappings from previous analysis
CATEGORY_MAPPINGS = {
    # PLANT prefixes (HERBAL enriched)
    'ch': 'PLANT',
    'sh': 'PLANT',
    'da': 'PLANT',
    'ct': 'PLANT',

    # BODY prefixes (BIOLOGICAL enriched)
    'qo': 'BODY',
    'ol': 'BODY',
    'so': 'BODY',

    # PROCESS middles (gallows characters and heating)
    'ke': 'PROCESS',
    'lc': 'PROCESS',
    'tc': 'PROCESS',
    'kc': 'PROCESS',
    'ck': 'PROCESS',
    'pc': 'PROCESS',
    'dc': 'PROCESS',
    'sc': 'PROCESS',
    'fc': 'PROCESS',
    'cp': 'PROCESS',
    'cf': 'PROCESS',

    # TIME/CELESTIAL (ZODIAC enriched)
    'ot': 'TIME',
    'ok': 'TIME',
    'al': 'TIME',
    'ar': 'TIME',
}

# Get list of prefixes by category
PLANT_PREFIXES = [p for p, c in CATEGORY_MAPPINGS.items() if c == 'PLANT']
BODY_PREFIXES = [p for p, c in CATEGORY_MAPPINGS.items() if c == 'BODY']
PROCESS_PREFIXES = [p for p, c in CATEGORY_MAPPINGS.items() if c == 'PROCESS']
ALL_PREFIXES = list(CATEGORY_MAPPINGS.keys())
ALL_CATEGORIES = ['PLANT', 'BODY', 'PROCESS', 'TIME', 'OTHER']


def load_corpus() -> Tuple[List[Dict], Dict[str, List[Dict]]]:
    """Load corpus organized by folio."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'

    all_words = []
    by_folio = defaultdict(list)

    seen = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to H (PRIMARY) transcriber only
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            word = row.get('word', '').strip().strip('"')
            folio = row.get('folio', '').strip().strip('"')
            line_num = row.get('line_number', '').strip().strip('"')
            currier = row.get('language', '').strip().strip('"')

            if not word or word.startswith('*') or len(word) < 2:
                continue

            # Only use Currier B (where patterns are supposedly stronger)
            if currier != 'B':
                continue

            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                entry = {'word': word, 'folio': folio, 'line': line_num}
                all_words.append(entry)
                by_folio[folio].append(entry)

    return all_words, dict(by_folio)


def get_category(word: str, mappings: Dict[str, str] = None) -> str:
    """Get category for a word based on prefix."""
    if mappings is None:
        mappings = CATEGORY_MAPPINGS

    # Check longest matching prefix first
    for length in [3, 2]:
        if len(word) >= length:
            prefix = word[:length]
            if prefix in mappings:
                return mappings[prefix]

    return 'OTHER'


def extract_sequences(words: List[Dict]) -> List[List[str]]:
    """Extract word sequences by folio+line."""
    by_line = defaultdict(list)
    for w in words:
        key = (w['folio'], w['line'])
        by_line[key].append(w['word'])
    return list(by_line.values())


def count_ppb_patterns(sequences: List[List[str]], mappings: Dict[str, str] = None) -> int:
    """Count PLANT -> PROCESS -> BODY patterns in sequences."""
    if mappings is None:
        mappings = CATEGORY_MAPPINGS

    count = 0
    for seq in sequences:
        categories = [get_category(w, mappings) for w in seq]

        # Look for PLANT followed by PROCESS followed by BODY
        for i in range(len(categories) - 2):
            if categories[i] == 'PLANT':
                for j in range(i + 1, len(categories) - 1):
                    if categories[j] == 'PROCESS':
                        for k in range(j + 1, len(categories)):
                            if categories[k] == 'BODY':
                                count += 1
                                break
                        break

    return count


def count_adjacent_ppb_patterns(sequences: List[List[str]], mappings: Dict[str, str] = None) -> int:
    """Count adjacent PLANT-PROCESS-BODY trigrams."""
    if mappings is None:
        mappings = CATEGORY_MAPPINGS

    count = 0
    for seq in sequences:
        categories = [get_category(w, mappings) for w in seq]

        for i in range(len(categories) - 2):
            if (categories[i] == 'PLANT' and
                categories[i+1] == 'PROCESS' and
                categories[i+2] == 'BODY'):
                count += 1

    return count


def run_randomization_test(real_count: int, test_func, n_trials: int = 100) -> Dict:
    """Run randomization test and compute statistics."""
    random_counts = []

    for trial in range(n_trials):
        count = test_func()
        random_counts.append(count)

    if not random_counts:
        return {'error': 'No trials completed'}

    mean = sum(random_counts) / len(random_counts)
    variance = sum((x - mean) ** 2 for x in random_counts) / len(random_counts)
    std = math.sqrt(variance)

    z_score = (real_count - mean) / std if std > 0 else 0
    p_value = sum(1 for c in random_counts if c >= real_count) / len(random_counts)

    return {
        'real_count': real_count,
        'randomized_mean': round(mean, 2),
        'randomized_std': round(std, 2),
        'randomized_min': min(random_counts),
        'randomized_max': max(random_counts),
        'z_score': round(z_score, 2),
        'p_value': round(p_value, 4),
        'significant': z_score >= 3,
        'distribution_sample': sorted(random_counts)[:10] + sorted(random_counts)[-5:]
    }


# ============================================================================
# TEST 1: SHUFFLED CATEGORY LABELS
# ============================================================================

def test_shuffled_categories(sequences: List[List[str]], n_trials: int = 100) -> Dict:
    """Randomly reassign categories to prefixes and recount."""
    print("  Running Test 1: Shuffled Category Labels...")

    # Real count with real mappings
    real_count = count_ppb_patterns(sequences, CATEGORY_MAPPINGS)

    def shuffled_trial():
        # Create shuffled mapping
        categories = list(CATEGORY_MAPPINGS.values())
        random.shuffle(categories)
        shuffled_map = dict(zip(CATEGORY_MAPPINGS.keys(), categories))
        return count_ppb_patterns(sequences, shuffled_map)

    return run_randomization_test(real_count, shuffled_trial, n_trials)


# ============================================================================
# TEST 2: SHUFFLED WORD ORDER WITHIN FOLIOS
# ============================================================================

def test_shuffled_word_order(words: List[Dict], by_folio: Dict[str, List[Dict]], n_trials: int = 100) -> Dict:
    """Keep categories fixed, shuffle word order within each folio."""
    print("  Running Test 2: Shuffled Word Order Within Folios...")

    # Real count
    sequences = extract_sequences(words)
    real_count = count_ppb_patterns(sequences, CATEGORY_MAPPINGS)

    def shuffled_trial():
        # Shuffle words within each folio
        shuffled_by_folio = {}
        for folio, folio_words in by_folio.items():
            shuffled = list(folio_words)
            random.shuffle(shuffled)
            shuffled_by_folio[folio] = shuffled

        # Flatten back to list
        shuffled_words = []
        for folio, folio_words in shuffled_by_folio.items():
            shuffled_words.extend(folio_words)

        # Re-extract sequences
        shuffled_sequences = extract_sequences(shuffled_words)
        return count_ppb_patterns(shuffled_sequences, CATEGORY_MAPPINGS)

    return run_randomization_test(real_count, shuffled_trial, n_trials)


# ============================================================================
# TEST 3: SHUFFLED WORDS ACROSS FOLIOS
# ============================================================================

def test_shuffled_across_folios(words: List[Dict], by_folio: Dict[str, List[Dict]], n_trials: int = 100) -> Dict:
    """Pool all words and redistribute randomly to folios."""
    print("  Running Test 3: Shuffled Words Across Folios...")

    # Real count
    sequences = extract_sequences(words)
    real_count = count_ppb_patterns(sequences, CATEGORY_MAPPINGS)

    # Get folio sizes
    folio_sizes = {f: len(ws) for f, ws in by_folio.items()}
    all_word_texts = [w['word'] for w in words]

    def shuffled_trial():
        # Shuffle all words
        shuffled = list(all_word_texts)
        random.shuffle(shuffled)

        # Redistribute to folios
        idx = 0
        new_words = []
        for folio, size in folio_sizes.items():
            for i in range(size):
                if idx < len(shuffled):
                    new_words.append({'word': shuffled[idx], 'folio': folio, 'line': str(i)})
                    idx += 1

        shuffled_sequences = extract_sequences(new_words)
        return count_ppb_patterns(shuffled_sequences, CATEGORY_MAPPINGS)

    return run_randomization_test(real_count, shuffled_trial, n_trials)


# ============================================================================
# TEST 4: RANDOM CATEGORY ASSIGNMENT
# ============================================================================

def test_random_categories(words: List[Dict], n_trials: int = 100) -> Dict:
    """Assign random categories to each word (ignoring prefixes)."""
    print("  Running Test 4: Random Category Assignment...")

    sequences = extract_sequences(words)

    # Calculate real category base rates
    all_cats = []
    for seq in sequences:
        for w in seq:
            all_cats.append(get_category(w, CATEGORY_MAPPINGS))

    cat_counts = Counter(all_cats)
    total = len(all_cats)
    cat_probs = {c: cat_counts[c] / total for c in cat_counts}

    # Real count
    real_count = count_ppb_patterns(sequences, CATEGORY_MAPPINGS)

    def random_trial():
        # Create random mapping that assigns random categories to each word
        count = 0
        for seq in sequences:
            # Assign random categories
            categories = []
            for w in seq:
                r = random.random()
                cumsum = 0
                for cat, prob in cat_probs.items():
                    cumsum += prob
                    if r <= cumsum:
                        categories.append(cat)
                        break
                else:
                    categories.append('OTHER')

            # Count PLANT -> PROCESS -> BODY
            for i in range(len(categories) - 2):
                if categories[i] == 'PLANT':
                    for j in range(i + 1, len(categories) - 1):
                        if categories[j] == 'PROCESS':
                            for k in range(j + 1, len(categories)):
                                if categories[k] == 'BODY':
                                    count += 1
                                    break
                            break

        return count

    return run_randomization_test(real_count, random_trial, n_trials)


def main():
    print("=" * 70)
    print("PROCEDURAL PATTERN VALIDATION")
    print("Testing if PLANT -> PROCESS -> BODY patterns are real")
    print("Success criterion: z-score >= 3 (p < 0.001)")
    print("=" * 70)

    # Load corpus (Currier B only)
    print("\nLoading corpus (Currier B only)...")
    words, by_folio = load_corpus()
    print(f"Total words: {len(words)}")
    print(f"Folios: {len(by_folio)}")

    sequences = extract_sequences(words)
    print(f"Sequences: {len(sequences)}")

    # Calculate real pattern counts
    print("\nCalculating real pattern counts...")
    real_ppb = count_ppb_patterns(sequences, CATEGORY_MAPPINGS)
    real_adj_ppb = count_adjacent_ppb_patterns(sequences, CATEGORY_MAPPINGS)
    print(f"PLANT -> PROCESS -> BODY (any distance): {real_ppb}")
    print(f"PLANT-PROCESS-BODY (adjacent): {real_adj_ppb}")

    # Run tests
    print("\n" + "=" * 70)
    print("RUNNING RANDOMIZATION TESTS (100 trials each)")
    print("=" * 70)

    results = {}

    # Test 1
    results['test1_shuffled_categories'] = test_shuffled_categories(sequences, 100)

    # Test 2
    results['test2_shuffled_word_order'] = test_shuffled_word_order(words, by_folio, 100)

    # Test 3
    results['test3_shuffled_across_folios'] = test_shuffled_across_folios(words, by_folio, 100)

    # Test 4
    results['test4_random_categories'] = test_random_categories(words, 100)

    # Print results
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    print(f"\n{'Test':<35} {'Real':>8} {'Mean':>8} {'Std':>8} {'Z':>8} {'Sig?':>8}")
    print("-" * 75)

    test_names = {
        'test1_shuffled_categories': 'Shuffled category labels',
        'test2_shuffled_word_order': 'Shuffled word order (within folio)',
        'test3_shuffled_across_folios': 'Shuffled across folios',
        'test4_random_categories': 'Random category assignment'
    }

    all_significant = True
    for test_id, test_name in test_names.items():
        r = results[test_id]
        sig = 'YES' if r['significant'] else 'NO'
        if not r['significant']:
            all_significant = False
        print(f"{test_name:<35} {r['real_count']:>8} {r['randomized_mean']:>8.1f} {r['randomized_std']:>8.1f} {r['z_score']:>8.1f} {sig:>8}")

    # Final verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    significant_count = sum(1 for r in results.values() if r.get('significant', False))

    if significant_count == 4:
        verdict = 'PATTERNS ARE REAL'
        explanation = 'All 4 tests show z >= 3 (p < 0.001). Patterns survive all randomizations.'
    elif significant_count >= 3:
        verdict = 'PATTERNS LIKELY REAL'
        explanation = f'{significant_count}/4 tests significant. Most patterns survive randomization.'
    elif significant_count >= 2:
        verdict = 'INCONCLUSIVE'
        explanation = f'{significant_count}/4 tests significant. Some patterns may be artifacts.'
    else:
        verdict = 'PATTERNS ARE ARTIFACTS'
        explanation = f'Only {significant_count}/4 tests significant. Patterns do not survive randomization.'

    print(f"\nVerdict: {verdict}")
    print(f"Explanation: {explanation}")

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'methodology': 'Procedural pattern validation with 4 randomization tests',
        'corpus': {
            'section': 'Currier B only',
            'word_count': len(words),
            'folio_count': len(by_folio),
            'sequence_count': len(sequences)
        },
        'real_counts': {
            'ppb_any_distance': real_ppb,
            'ppb_adjacent': real_adj_ppb
        },
        'tests': results,
        'summary': {
            'significant_tests': significant_count,
            'verdict': verdict,
            'explanation': explanation
        }
    }

    with open('procedural_pattern_validation_report.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to procedural_pattern_validation_report.json")


if __name__ == '__main__':
    main()
