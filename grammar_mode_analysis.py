#!/usr/bin/env python3
"""
Grammar Mode Analysis

Determine if Voynich text is PRESCRIPTIVE (instructional) or DESCRIPTIVE (explanatory)
based on structural patterns.

PRESCRIPTIVE signatures:
- PROCESS at sequence start (imperative-like)
- Short, self-contained units
- High repetition of action sequences
- Low conditional complexity

DESCRIPTIVE signatures:
- PLANT or BODY at sequence start (topic establishment)
- Longer, connected units
- Embedded relationships with intervening material
- Higher structural complexity
"""

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Any


# Category mappings
CATEGORY_MAPPINGS = {
    # PLANT prefixes
    'ch': 'PLANT',
    'sh': 'PLANT',
    'da': 'PLANT',
    'ct': 'PLANT',

    # BODY prefixes
    'qo': 'BODY',
    'ol': 'BODY',
    'so': 'BODY',

    # PROCESS middles
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

    # TIME/CELESTIAL
    'ot': 'TIME',
    'ok': 'TIME',
    'al': 'TIME',
    'ar': 'TIME',
}


def load_corpus() -> Tuple[List[Dict], Dict[str, List[Dict]]]:
    """Load corpus organized by folio."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'

    all_words = []
    by_folio = defaultdict(list)

    seen = set()
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
                entry = {'word': word, 'folio': folio, 'line': line_num, 'currier': currier}
                all_words.append(entry)
                by_folio[folio].append(entry)

    return all_words, dict(by_folio)


def get_category(word: str) -> str:
    """Get category for a word based on prefix."""
    for length in [3, 2]:
        if len(word) >= length:
            prefix = word[:length]
            if prefix in CATEGORY_MAPPINGS:
                return CATEGORY_MAPPINGS[prefix]
    return 'OTHER'


def extract_sequences(words: List[Dict]) -> List[List[Dict]]:
    """Extract word sequences by folio+line."""
    by_line = defaultdict(list)
    for w in words:
        key = (w['folio'], w['line'])
        by_line[key].append(w)
    return list(by_line.values())


# ============================================================================
# ANALYSIS 1: SEQUENCE OPENING ANALYSIS
# ============================================================================

def analyze_sequence_openings(sequences: List[List[Dict]]) -> Dict:
    """
    What category most often starts sequences?

    Prescriptive: PROCESS-initial (imperative commands)
    Descriptive: PLANT or BODY-initial (topic establishment)
    """
    print("  Analyzing sequence openings...")

    first_word_categories = Counter()
    first_word_examples = defaultdict(list)

    for seq in sequences:
        if not seq:
            continue
        first_word = seq[0]['word']
        category = get_category(first_word)
        first_word_categories[category] += 1
        if len(first_word_examples[category]) < 10:
            first_word_examples[category].append(first_word)

    total = sum(first_word_categories.values())
    category_rates = {cat: count / total for cat, count in first_word_categories.items()}

    # Calculate prescriptive vs descriptive score
    process_rate = category_rates.get('PROCESS', 0)
    topic_rate = category_rates.get('PLANT', 0) + category_rates.get('BODY', 0)

    if process_rate > topic_rate:
        verdict = 'PRESCRIPTIVE'
        explanation = f'PROCESS-initial ({process_rate:.1%}) > TOPIC-initial ({topic_rate:.1%})'
    else:
        verdict = 'DESCRIPTIVE'
        explanation = f'TOPIC-initial ({topic_rate:.1%}) > PROCESS-initial ({process_rate:.1%})'

    return {
        'category_counts': dict(first_word_categories),
        'category_rates': {k: round(v, 4) for k, v in category_rates.items()},
        'examples': dict(first_word_examples),
        'process_initial_rate': round(process_rate, 4),
        'topic_initial_rate': round(topic_rate, 4),
        'verdict': verdict,
        'explanation': explanation
    }


# ============================================================================
# ANALYSIS 2: EMBEDDING DEPTH
# ============================================================================

def analyze_embedding_depth(sequences: List[List[Dict]]) -> Dict:
    """
    Words between PLANT, PROCESS, BODY elements.

    Prescriptive: Adjacent (0-2 words)
    Descriptive: Variable, distant (3+ words)
    """
    print("  Analyzing embedding depth...")

    distances = []
    adjacent_count = 0
    distant_count = 0

    target_categories = {'PLANT', 'PROCESS', 'BODY'}

    for seq in sequences:
        categories = [(i, get_category(w['word'])) for i, w in enumerate(seq)]
        target_positions = [(i, cat) for i, cat in categories if cat in target_categories]

        # Calculate distances between consecutive target elements
        for j in range(len(target_positions) - 1):
            pos1, cat1 = target_positions[j]
            pos2, cat2 = target_positions[j + 1]
            distance = pos2 - pos1 - 1  # Words between
            distances.append(distance)

            if distance <= 2:
                adjacent_count += 1
            else:
                distant_count += 1

    if not distances:
        return {'error': 'No patterns found'}

    mean_distance = sum(distances) / len(distances)

    # Calculate distribution
    distance_dist = Counter(distances)

    # Prescriptive vs descriptive
    total = adjacent_count + distant_count
    adjacent_rate = adjacent_count / total if total > 0 else 0

    if adjacent_rate > 0.6:
        verdict = 'PRESCRIPTIVE'
        explanation = f'{adjacent_rate:.1%} of patterns are adjacent (0-2 words between)'
    elif adjacent_rate < 0.4:
        verdict = 'DESCRIPTIVE'
        explanation = f'Only {adjacent_rate:.1%} adjacent, {1-adjacent_rate:.1%} have 3+ words between'
    else:
        verdict = 'MIXED'
        explanation = f'{adjacent_rate:.1%} adjacent - no clear pattern'

    return {
        'mean_distance': round(mean_distance, 2),
        'adjacent_count': adjacent_count,
        'distant_count': distant_count,
        'adjacent_rate': round(adjacent_rate, 4),
        'distance_distribution': dict(sorted(distance_dist.items())[:15]),
        'verdict': verdict,
        'explanation': explanation
    }


# ============================================================================
# ANALYSIS 3: SEQUENCE CONNECTIVITY
# ============================================================================

def analyze_sequence_connectivity(sequences: List[List[Dict]]) -> Dict:
    """
    Do sequences share elements?

    Prescriptive: Self-contained units
    Descriptive: Cross-references, returning topics
    """
    print("  Analyzing sequence connectivity...")

    # Track which words appear in which sequences
    word_to_sequences = defaultdict(set)
    for i, seq in enumerate(sequences):
        for w in seq:
            word_to_sequences[w['word']].add(i)

    # Count words that appear in multiple sequences
    multi_sequence_words = {w: seqs for w, seqs in word_to_sequences.items() if len(seqs) > 1}

    # Calculate connectivity score
    total_words = len(word_to_sequences)
    connected_words = len(multi_sequence_words)
    connectivity_rate = connected_words / total_words if total_words > 0 else 0

    # Average sequences per connected word
    avg_sequences = (sum(len(s) for s in multi_sequence_words.values()) /
                    len(multi_sequence_words) if multi_sequence_words else 0)

    # Most connected words
    most_connected = sorted(
        [(w, len(s)) for w, s in multi_sequence_words.items()],
        key=lambda x: -x[1]
    )[:20]

    # Calculate category distribution of connected words
    connected_categories = Counter()
    for word in multi_sequence_words:
        connected_categories[get_category(word)] += 1

    # Verdict
    if connectivity_rate < 0.3:
        verdict = 'PRESCRIPTIVE'
        explanation = f'Low connectivity ({connectivity_rate:.1%}) - self-contained units'
    elif connectivity_rate > 0.5:
        verdict = 'DESCRIPTIVE'
        explanation = f'High connectivity ({connectivity_rate:.1%}) - cross-references'
    else:
        verdict = 'MIXED'
        explanation = f'Moderate connectivity ({connectivity_rate:.1%})'

    return {
        'total_unique_words': total_words,
        'words_in_multiple_sequences': connected_words,
        'connectivity_rate': round(connectivity_rate, 4),
        'avg_sequences_per_word': round(avg_sequences, 2),
        'most_connected': most_connected,
        'connected_by_category': dict(connected_categories),
        'verdict': verdict,
        'explanation': explanation
    }


# ============================================================================
# ANALYSIS 4: RELATIONAL MARKERS
# ============================================================================

def analyze_relational_markers(sequences: List[List[Dict]]) -> Dict:
    """
    Words that appear BETWEEN category words.
    Potential relational markers ("when," "if," "because" equivalents).
    """
    print("  Analyzing relational markers...")

    target_categories = {'PLANT', 'PROCESS', 'BODY'}
    between_words = Counter()

    for seq in sequences:
        categories = [get_category(w['word']) for w in seq]
        words = [w['word'] for w in seq]

        # Find words between target categories
        in_between = False
        start_cat = None

        for i, (word, cat) in enumerate(zip(words, categories)):
            if cat in target_categories:
                in_between = True
                start_cat = cat
            elif in_between:
                # Check if next target category exists
                for j in range(i + 1, len(categories)):
                    if categories[j] in target_categories:
                        between_words[word] += 1
                        break

    # Analyze the between words
    total_between = sum(between_words.values())

    # Get categories of between words
    between_categories = Counter()
    for word, count in between_words.items():
        between_categories[get_category(word)] += count

    # Most common between words (potential relational markers)
    top_between = between_words.most_common(30)

    # Calculate "OTHER" rate - these are most likely to be relational markers
    other_rate = between_categories.get('OTHER', 0) / total_between if total_between > 0 else 0

    return {
        'total_between_words': total_between,
        'unique_between_words': len(between_words),
        'between_category_distribution': dict(between_categories),
        'other_category_rate': round(other_rate, 4),
        'top_potential_markers': top_between,
        'interpretation': 'Words in OTHER category between semantic units may be relational markers'
    }


# ============================================================================
# ANALYSIS 5: SEQUENCE LENGTH PATTERNS
# ============================================================================

def analyze_sequence_lengths(sequences: List[List[Dict]]) -> Dict:
    """
    Prescriptive: Short, uniform lengths (recipe steps)
    Descriptive: Variable, longer lengths (explanatory prose)
    """
    print("  Analyzing sequence length patterns...")

    lengths = [len(seq) for seq in sequences if seq]

    if not lengths:
        return {'error': 'No sequences'}

    mean_len = sum(lengths) / len(lengths)
    variance = sum((x - mean_len) ** 2 for x in lengths) / len(lengths)
    std_len = math.sqrt(variance)

    # Coefficient of variation
    cv = std_len / mean_len if mean_len > 0 else 0

    # Length distribution
    length_dist = Counter(lengths)

    # Verdict
    if mean_len < 8 and cv < 0.5:
        verdict = 'PRESCRIPTIVE'
        explanation = f'Short (mean={mean_len:.1f}) and uniform (CV={cv:.2f}) - recipe-like'
    elif mean_len > 12 or cv > 0.6:
        verdict = 'DESCRIPTIVE'
        explanation = f'Longer (mean={mean_len:.1f}) and variable (CV={cv:.2f}) - prose-like'
    else:
        verdict = 'MIXED'
        explanation = f'Mean={mean_len:.1f}, CV={cv:.2f} - moderate'

    return {
        'mean_length': round(mean_len, 2),
        'std_length': round(std_len, 2),
        'coefficient_of_variation': round(cv, 4),
        'min_length': min(lengths),
        'max_length': max(lengths),
        'length_distribution': dict(sorted(length_dist.items())[:20]),
        'verdict': verdict,
        'explanation': explanation
    }


def main():
    print("=" * 70)
    print("GRAMMAR MODE ANALYSIS")
    print("Testing PRESCRIPTIVE (instructional) vs DESCRIPTIVE (explanatory)")
    print("=" * 70)

    # Load corpus
    print("\nLoading corpus...")
    words, by_folio = load_corpus()
    print(f"Total words: {len(words)}")

    # Split by Currier
    currier_a = [w for w in words if w['currier'] == 'A']
    currier_b = [w for w in words if w['currier'] == 'B']
    print(f"Currier A: {len(currier_a)} words")
    print(f"Currier B: {len(currier_b)} words")

    results = {
        'timestamp': datetime.now().isoformat(),
        'methodology': 'Prescriptive vs Descriptive grammar analysis'
    }

    # Analyze both sections
    for name, corpus in [('currier_a', currier_a), ('currier_b', currier_b)]:
        print(f"\n{'=' * 50}")
        print(f"ANALYZING {name.upper()}")
        print("=" * 50)

        sequences = extract_sequences(corpus)
        print(f"Sequences: {len(sequences)}")

        section_results = {
            'word_count': len(corpus),
            'sequence_count': len(sequences)
        }

        # Run all analyses
        section_results['sequence_openings'] = analyze_sequence_openings(sequences)
        section_results['embedding_depth'] = analyze_embedding_depth(sequences)
        section_results['sequence_connectivity'] = analyze_sequence_connectivity(sequences)
        section_results['relational_markers'] = analyze_relational_markers(sequences)
        section_results['sequence_lengths'] = analyze_sequence_lengths(sequences)

        results[name] = section_results

    # Aggregate verdicts
    print("\n" + "=" * 70)
    print("VERDICT SUMMARY")
    print("=" * 70)

    analyses = ['sequence_openings', 'embedding_depth', 'sequence_connectivity', 'sequence_lengths']

    for section in ['currier_a', 'currier_b']:
        print(f"\n--- {section.upper()} ---")
        prescriptive_count = 0
        descriptive_count = 0

        for analysis in analyses:
            verdict = results[section][analysis].get('verdict', 'UNKNOWN')
            explanation = results[section][analysis].get('explanation', '')
            print(f"  {analysis}: {verdict}")
            print(f"    {explanation}")

            if verdict == 'PRESCRIPTIVE':
                prescriptive_count += 1
            elif verdict == 'DESCRIPTIVE':
                descriptive_count += 1

        # Overall verdict
        if prescriptive_count > descriptive_count:
            overall = 'PRESCRIPTIVE'
        elif descriptive_count > prescriptive_count:
            overall = 'DESCRIPTIVE'
        else:
            overall = 'MIXED'

        results[section]['overall_verdict'] = overall
        results[section]['prescriptive_score'] = prescriptive_count
        results[section]['descriptive_score'] = descriptive_count

        print(f"\n  OVERALL: {overall} ({prescriptive_count} prescriptive, {descriptive_count} descriptive)")

    # Final comparison
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)

    a_verdict = results['currier_a']['overall_verdict']
    b_verdict = results['currier_b']['overall_verdict']

    if a_verdict == b_verdict:
        print(f"\nBoth sections are {a_verdict}")
        final_verdict = a_verdict
    else:
        print(f"\nCurrier A: {a_verdict}")
        print(f"Currier B: {b_verdict}")
        final_verdict = 'MIXED'

    results['final_verdict'] = final_verdict
    results['interpretation'] = {
        'PRESCRIPTIVE': 'Text follows instructional/imperative patterns (recipes, procedures)',
        'DESCRIPTIVE': 'Text follows explanatory/declarative patterns (treatises, descriptions)',
        'MIXED': 'Text shows elements of both instructional and explanatory patterns'
    }

    # Save results
    with open('grammar_mode_analysis_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to grammar_mode_analysis_report.json")


if __name__ == '__main__':
    main()
