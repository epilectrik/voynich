"""Structural Validation: Role Slot Induction and Generalization Testing.

Task 1: Analyze word sequences to identify recurring positional templates
Task 2: Train/test split to verify patterns generalize across manuscript
"""
import sys
import json
import random
from collections import defaultdict, Counter
from datetime import datetime

sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus

# =============================================================================
# CONSERVATIVE CATEGORY MAPPINGS
# =============================================================================

CONSERVATIVE_PREFIX = {
    'qo': 'BODY', 'ol': 'BODY', 'so': 'BODY', 'pc': 'BODY',
    'ch': 'PLANT', 'sh': 'PLANT', 'da': 'PLANT', 'sa': 'PLANT',
    'ct': 'LIQUID', 'cth': 'LIQUID', 'lk': 'LIQUID',
    'ot': 'TIME', 'ok': 'TIME', 'yk': 'TIME',
    'al': 'CELESTIAL', 'ar': 'CELESTIAL', 'or': 'CELESTIAL', 'yt': 'CELESTIAL',
    'op': 'PREPARATION',
}

CONSERVATIVE_GALLOWS = {
    'kch': 'PROCESS', 'ckh': 'PROCESS', 'tch': 'PROCESS',
    'pch': 'PROCESS', 'fch': 'PROCESS', 'cth': 'PROCESS',
    'cph': 'PROCESS', 'cfh': 'PROCESS', 'dch': 'PROCESS',
    'sch': 'PROCESS', 'kche': 'PROCESS', 'ckhe': 'PROCESS',
    'tche': 'PROCESS', 'pche': 'PROCESS', 'fche': 'PROCESS',
    'lch': 'PROCESS', 'lche': 'PROCESS',
}

# Section assignments based on folio numbers
def get_section(folio):
    """Assign section based on folio number."""
    if not folio:
        return 'UNKNOWN'

    # Extract folio number
    num_part = ''.join(c for c in folio if c.isdigit())
    if not num_part:
        return 'UNKNOWN'
    num = int(num_part)

    if num <= 66:
        return 'HERBAL'
    elif num <= 73:
        return 'ZODIAC'
    elif num <= 84:
        return 'BIOLOGICAL'
    elif num <= 86:
        return 'COSMOLOGICAL'
    else:
        return 'RECIPES'


def categorize_word(word):
    """Assign a conservative category to a word."""
    if not word:
        return 'OTHER'

    text = word.lower()

    # Check for gallows (PROCESS markers)
    for gallows in sorted(CONSERVATIVE_GALLOWS.keys(), key=len, reverse=True):
        if gallows in text:
            return 'PROCESS'

    # Check for prefix categories
    for prefix, category in sorted(CONSERVATIVE_PREFIX.items(), key=lambda x: len(x[0]), reverse=True):
        if text.startswith(prefix):
            return category

    return 'OTHER'


# =============================================================================
# TASK 1: ROLE SLOT INDUCTION
# =============================================================================

def extract_sequences(words_by_folio, min_len=3, max_len=5):
    """Extract all word sequences of specified lengths."""
    sequences = {n: [] for n in range(min_len, max_len + 1)}

    for folio, words in words_by_folio.items():
        section = get_section(folio)
        word_list = [w.text for w in words if w.text]

        for n in range(min_len, max_len + 1):
            for i in range(len(word_list) - n + 1):
                seq = word_list[i:i+n]
                cat_seq = tuple(categorize_word(w) for w in seq)
                sequences[n].append({
                    'folio': folio,
                    'section': section,
                    'words': seq,
                    'categories': cat_seq
                })

    return sequences


def build_transition_matrix(sequences):
    """Build transition probability matrix from sequences."""
    transitions = defaultdict(Counter)

    for seq_list in sequences.values():
        for seq in seq_list:
            cats = seq['categories']
            for i in range(len(cats) - 1):
                transitions[cats[i]][cats[i+1]] += 1

    # Convert to probabilities
    prob_matrix = {}
    for cat_a, following in transitions.items():
        total = sum(following.values())
        prob_matrix[cat_a] = {cat_b: count/total for cat_b, count in following.items()}

    return prob_matrix, transitions


def analyze_patterns(sequences, transitions):
    """Analyze common patterns and category relationships."""
    results = {}

    # Most common 3-category sequences
    seq_3_counts = Counter(seq['categories'] for seq in sequences[3])
    results['top_3_sequences'] = seq_3_counts.most_common(10)

    # Most common 4-category sequences
    seq_4_counts = Counter(seq['categories'] for seq in sequences[4])
    results['top_4_sequences'] = seq_4_counts.most_common(10)

    # What follows each category?
    results['what_follows'] = {}
    for cat in ['PLANT', 'BODY', 'PROCESS', 'TIME', 'LIQUID', 'CELESTIAL', 'OTHER']:
        if cat in transitions:
            following = transitions[cat]
            total = sum(following.values())
            results['what_follows'][cat] = {
                k: f"{v/total*100:.1f}%"
                for k, v in following.most_common(5)
            }

    # What precedes each category?
    preceding = defaultdict(Counter)
    for cat_a, following in transitions.items():
        for cat_b, count in following.items():
            preceding[cat_b][cat_a] += count

    results['what_precedes'] = {}
    for cat in ['PROCESS', 'BODY', 'PLANT']:
        if cat in preceding:
            prec = preceding[cat]
            total = sum(prec.values())
            results['what_precedes'][cat] = {
                k: f"{v/total*100:.1f}%"
                for k, v in prec.most_common(5)
            }

    return results


def analyze_by_section(sequences):
    """Check if patterns differ by section."""
    section_patterns = defaultdict(lambda: Counter())

    for seq in sequences[3]:
        section_patterns[seq['section']][seq['categories']] += 1

    # Find section-specific vs universal patterns
    all_sections = list(section_patterns.keys())

    # Get top patterns per section
    section_top = {}
    for section, counts in section_patterns.items():
        section_top[section] = counts.most_common(5)

    # Find patterns that appear in all sections vs section-specific
    all_patterns = set()
    for section, counts in section_patterns.items():
        all_patterns.update(counts.keys())

    universal = []
    section_specific = defaultdict(list)

    for pattern in all_patterns:
        sections_with_pattern = [s for s in all_sections if section_patterns[s][pattern] > 0]

        if len(sections_with_pattern) >= 4:  # Appears in most sections
            total = sum(section_patterns[s][pattern] for s in all_sections)
            universal.append((pattern, total))
        elif len(sections_with_pattern) == 1:  # Section-specific
            section = sections_with_pattern[0]
            section_specific[section].append((pattern, section_patterns[section][pattern]))

    return {
        'section_top_patterns': section_top,
        'universal_patterns': sorted(universal, key=lambda x: -x[1])[:10],
        'section_specific': {s: sorted(v, key=lambda x: -x[1])[:5] for s, v in section_specific.items()}
    }


# =============================================================================
# TASK 2: CROSS-MANUSCRIPT GENERALIZATION TEST
# =============================================================================

def split_folios(words_by_folio, test_ratio=0.2, seed=42):
    """Split folios into train/test ensuring each section is represented in test."""
    random.seed(seed)

    # Group folios by section
    section_folios = defaultdict(list)
    for folio in words_by_folio.keys():
        section = get_section(folio)
        if len(words_by_folio[folio]) > 0:  # Only include non-empty folios
            section_folios[section].append(folio)

    train_folios = []
    test_folios = []

    for section, folios in section_folios.items():
        if len(folios) == 0:
            continue

        random.shuffle(folios)

        # Ensure at least one test folio per section
        n_test = max(1, int(len(folios) * test_ratio))

        test_folios.extend(folios[:n_test])
        train_folios.extend(folios[n_test:])

    return train_folios, test_folios


def calculate_distributions(words_by_folio, folios):
    """Calculate category distributions for given folios."""
    section_dists = defaultdict(Counter)

    for folio in folios:
        if folio not in words_by_folio:
            continue
        section = get_section(folio)
        for w in words_by_folio[folio]:
            if w.text:
                cat = categorize_word(w.text)
                section_dists[section][cat] += 1

    # Normalize to probabilities
    section_probs = {}
    for section, counts in section_dists.items():
        total = sum(counts.values())
        if total > 0:
            section_probs[section] = {cat: count/total for cat, count in counts.items()}

    return section_probs


def build_transition_model(words_by_folio, folios):
    """Build transition model from training folios."""
    transitions = defaultdict(Counter)

    for folio in folios:
        if folio not in words_by_folio:
            continue

        words = [w.text for w in words_by_folio[folio] if w.text]
        cats = [categorize_word(w) for w in words]

        for i in range(len(cats) - 1):
            transitions[cats[i]][cats[i+1]] += 1

    # Convert to probabilities
    prob_matrix = {}
    for cat_a, following in transitions.items():
        total = sum(following.values())
        if total > 0:
            prob_matrix[cat_a] = {cat_b: count/total for cat_b, count in following.items()}

    return prob_matrix


def predict_distribution(train_probs, section):
    """Predict distribution for a section based on training data."""
    if section in train_probs:
        return train_probs[section]
    # Fall back to average across sections
    avg = defaultdict(float)
    for s_probs in train_probs.values():
        for cat, prob in s_probs.items():
            avg[cat] += prob
    n_sections = len(train_probs)
    if n_sections > 0:
        return {cat: prob/n_sections for cat, prob in avg.items()}
    return {}


def evaluate_predictions(words_by_folio, test_folios, train_probs, train_transitions):
    """Evaluate predictions on test folios."""
    results = []

    for folio in test_folios:
        if folio not in words_by_folio or len(words_by_folio[folio]) == 0:
            continue

        section = get_section(folio)
        words = [w.text for w in words_by_folio[folio] if w.text]

        if len(words) == 0:
            continue

        # Actual distribution
        actual_cats = [categorize_word(w) for w in words]
        actual_counts = Counter(actual_cats)
        total = sum(actual_counts.values())
        actual_dist = {cat: count/total for cat, count in actual_counts.items()}

        # Predicted distribution
        predicted_dist = predict_distribution(train_probs, section)

        # Calculate error (mean absolute difference)
        all_cats = set(actual_dist.keys()) | set(predicted_dist.keys())
        mae = sum(abs(actual_dist.get(cat, 0) - predicted_dist.get(cat, 0)) for cat in all_cats) / len(all_cats)

        # Transition accuracy
        actual_transitions = Counter()
        for i in range(len(actual_cats) - 1):
            actual_transitions[(actual_cats[i], actual_cats[i+1])] += 1

        transition_matches = 0
        transition_total = 0
        for (cat_a, cat_b), count in actual_transitions.items():
            if cat_a in train_transitions:
                predicted_prob = train_transitions[cat_a].get(cat_b, 0)
                actual_prob = count / sum(actual_transitions.values()) if actual_transitions else 0
                # Consider it a match if predicted is non-zero and actual > 0
                if predicted_prob > 0 and actual_prob > 0:
                    transition_matches += count
            transition_total += count

        transition_acc = transition_matches / transition_total if transition_total > 0 else 0

        results.append({
            'folio': folio,
            'section': section,
            'n_words': len(words),
            'distribution_error': mae,
            'transition_accuracy': transition_acc,
            'actual_dist': actual_dist,
            'predicted_dist': predicted_dist
        })

    return results


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 90)
    print("STRUCTURAL VALIDATION: ROLE SLOT INDUCTION & GENERALIZATION TEST")
    print("=" * 90)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Load corpus
    corpus = load_corpus('data/transcriptions')

    # Organize words by folio
    words_by_folio = defaultdict(list)
    for w in corpus.words:
        if w.text and w.folio:
            words_by_folio[w.folio].append(w)

    print(f"Loaded {len(corpus.words)} words across {len(words_by_folio)} folios")
    print()

    # =========================================================================
    # TASK 1: ROLE SLOT INDUCTION
    # =========================================================================

    print("=" * 90)
    print("TASK 1: ROLE SLOT INDUCTION")
    print("=" * 90)
    print()

    # Extract sequences
    sequences = extract_sequences(words_by_folio)
    print(f"Extracted sequences:")
    for n, seq_list in sequences.items():
        print(f"  {n}-word sequences: {len(seq_list)}")
    print()

    # Build transition matrix
    prob_matrix, transitions = build_transition_matrix(sequences)

    print("-" * 90)
    print("TRANSITION PROBABILITY MATRIX")
    print("-" * 90)
    print()

    categories = ['BODY', 'PLANT', 'TIME', 'CELESTIAL', 'LIQUID', 'PROCESS', 'PREPARATION', 'OTHER']

    # Print header
    print(f"{'FROM':<12}", end='')
    for cat in categories:
        print(f"{cat[:8]:>10}", end='')
    print()
    print("-" * 92)

    # Print rows
    for cat_a in categories:
        print(f"{cat_a:<12}", end='')
        for cat_b in categories:
            prob = prob_matrix.get(cat_a, {}).get(cat_b, 0)
            if prob > 0:
                print(f"{prob*100:>9.1f}%", end='')
            else:
                print(f"{'---':>10}", end='')
        print()
    print()

    # Analyze patterns
    patterns = analyze_patterns(sequences, transitions)

    print("-" * 90)
    print("TOP 10 THREE-CATEGORY SEQUENCES")
    print("-" * 90)
    for seq, count in patterns['top_3_sequences']:
        print(f"  {' -> '.join(seq):<50} ({count:,} occurrences)")
    print()

    print("-" * 90)
    print("TOP 10 FOUR-CATEGORY SEQUENCES")
    print("-" * 90)
    for seq, count in patterns['top_4_sequences']:
        print(f"  {' -> '.join(seq):<60} ({count:,} occurrences)")
    print()

    print("-" * 90)
    print("WHAT TYPICALLY FOLLOWS EACH CATEGORY?")
    print("-" * 90)
    for cat, following in patterns['what_follows'].items():
        print(f"  {cat}:")
        for next_cat, pct in following.items():
            print(f"    -> {next_cat}: {pct}")
    print()

    print("-" * 90)
    print("WHAT TYPICALLY PRECEDES KEY CATEGORIES?")
    print("-" * 90)
    for cat, preceding in patterns['what_precedes'].items():
        print(f"  {cat}:")
        for prev_cat, pct in preceding.items():
            print(f"    <- {prev_cat}: {pct}")
    print()

    # Section analysis
    section_analysis = analyze_by_section(sequences)

    print("-" * 90)
    print("SECTION-SPECIFIC PATTERNS")
    print("-" * 90)
    print()

    print("Universal patterns (appear in 4+ sections):")
    for pattern, count in section_analysis['universal_patterns'][:5]:
        print(f"  {' -> '.join(pattern)}: {count:,}")
    print()

    print("Section-specific patterns:")
    for section, patterns_list in section_analysis['section_specific'].items():
        if patterns_list:
            print(f"  {section}:")
            for pattern, count in patterns_list[:3]:
                print(f"    {' -> '.join(pattern)}: {count}")
    print()

    # Check for functional slot evidence
    print("-" * 90)
    print("EVIDENCE FOR FUNCTIONAL SLOTS")
    print("-" * 90)
    print()

    # Look for INGREDIENT -> PROCESS -> TARGET pattern
    ingredient_process = 0
    process_target = 0
    full_recipe = 0

    for seq in sequences[3]:
        cats = seq['categories']
        if cats[0] == 'PLANT' and cats[1] == 'PROCESS':
            ingredient_process += 1
        if cats[1] == 'PROCESS' and cats[2] == 'BODY':
            process_target += 1
        if cats[0] == 'PLANT' and cats[1] == 'PROCESS' and cats[2] == 'BODY':
            full_recipe += 1

    print(f"Pattern: PLANT -> PROCESS -> ?     : {ingredient_process:,} occurrences")
    print(f"Pattern: ? -> PROCESS -> BODY      : {process_target:,} occurrences")
    print(f"Pattern: PLANT -> PROCESS -> BODY  : {full_recipe:,} occurrences (INGREDIENT->ACTION->TARGET)")
    print()

    # Time-based patterns
    time_patterns = 0
    for seq in sequences[3]:
        cats = seq['categories']
        if 'TIME' in cats or 'CELESTIAL' in cats:
            time_patterns += 1

    print(f"Sequences containing TIME or CELESTIAL: {time_patterns:,}")
    print()

    # =========================================================================
    # TASK 2: CROSS-MANUSCRIPT GENERALIZATION TEST
    # =========================================================================

    print("=" * 90)
    print("TASK 2: CROSS-MANUSCRIPT GENERALIZATION TEST")
    print("=" * 90)
    print()

    # Split folios
    train_folios, test_folios = split_folios(words_by_folio, test_ratio=0.2)

    print(f"Training folios: {len(train_folios)}")
    print(f"Test folios: {len(test_folios)}")
    print()

    # Show test folio distribution by section
    test_sections = Counter(get_section(f) for f in test_folios)
    print("Test set section distribution:")
    for section, count in sorted(test_sections.items()):
        print(f"  {section}: {count} folios")
    print()

    # Build training model
    print("-" * 90)
    print("TRAINING MODEL")
    print("-" * 90)
    print()

    train_probs = calculate_distributions(words_by_folio, train_folios)
    train_transitions = build_transition_model(words_by_folio, train_folios)

    print("Training category distributions by section:")
    for section, probs in sorted(train_probs.items()):
        print(f"  {section}:")
        for cat, prob in sorted(probs.items(), key=lambda x: -x[1])[:5]:
            print(f"    {cat}: {prob*100:.1f}%")
    print()

    # Evaluate on test set
    print("-" * 90)
    print("TEST SET EVALUATION")
    print("-" * 90)
    print()

    results = evaluate_predictions(words_by_folio, test_folios, train_probs, train_transitions)

    print(f"{'Folio':<10} {'Section':<15} {'Words':<8} {'Dist Error':<12} {'Trans Acc':<12}")
    print("-" * 57)

    total_error = 0
    total_trans_acc = 0
    n_results = 0

    for r in sorted(results, key=lambda x: x['folio']):
        print(f"{r['folio']:<10} {r['section']:<15} {r['n_words']:<8} {r['distribution_error']:.4f}       {r['transition_accuracy']*100:.1f}%")
        total_error += r['distribution_error']
        total_trans_acc += r['transition_accuracy']
        n_results += 1

    print("-" * 57)
    if n_results > 0:
        print(f"{'AVERAGE':<10} {'':<15} {'':<8} {total_error/n_results:.4f}       {total_trans_acc/n_results*100:.1f}%")
    print()

    # Analyze failures
    print("-" * 90)
    print("PREDICTION FAILURES (Error > 0.15)")
    print("-" * 90)
    print()

    failures = [r for r in results if r['distribution_error'] > 0.15]
    if failures:
        for r in sorted(failures, key=lambda x: -x['distribution_error']):
            print(f"Folio {r['folio']} ({r['section']}):")
            print(f"  Predicted: {', '.join(f'{k}:{v*100:.1f}%' for k, v in sorted(r['predicted_dist'].items(), key=lambda x: -x[1])[:4])}")
            print(f"  Actual:    {', '.join(f'{k}:{v*100:.1f}%' for k, v in sorted(r['actual_dist'].items(), key=lambda x: -x[1])[:4])}")
            print()
    else:
        print("No significant failures (all errors < 0.15)")
    print()

    # =========================================================================
    # SUMMARY
    # =========================================================================

    print("=" * 90)
    print("SUMMARY")
    print("=" * 90)
    print()

    # Task 1 summary
    print("TASK 1 FINDINGS:")
    print("-" * 40)
    print()
    print("1. Most common transition: OTHER -> OTHER (expected for uncategorized words)")

    # Find strongest non-OTHER transition
    strongest = None
    strongest_prob = 0
    for cat_a in categories:
        if cat_a == 'OTHER':
            continue
        for cat_b, prob in prob_matrix.get(cat_a, {}).items():
            if cat_b != 'OTHER' and prob > strongest_prob:
                strongest = (cat_a, cat_b)
                strongest_prob = prob

    if strongest:
        print(f"2. Strongest content transition: {strongest[0]} -> {strongest[1]} ({strongest_prob*100:.1f}%)")

    print(f"3. Recipe pattern evidence: {full_recipe} PLANT->PROCESS->BODY sequences")
    print(f"4. Patterns are {'UNIVERSAL' if len(section_analysis['universal_patterns']) > len([p for patterns in section_analysis['section_specific'].values() for p in patterns]) else 'SECTION-SPECIFIC'}")
    print()

    # Task 2 summary
    print("TASK 2 FINDINGS:")
    print("-" * 40)
    print()
    avg_error = total_error / n_results if n_results > 0 else 0
    avg_trans = total_trans_acc / n_results if n_results > 0 else 0

    print(f"1. Average distribution prediction error: {avg_error:.4f}")
    print(f"2. Average transition accuracy: {avg_trans*100:.1f}%")
    print(f"3. Significant failures: {len(failures)} / {len(results)} test folios")

    if avg_error < 0.1:
        generalization = "STRONG"
    elif avg_error < 0.2:
        generalization = "MODERATE"
    else:
        generalization = "WEAK"

    print(f"4. Model generalization: {generalization}")
    print()

    print("CONCLUSION:")
    print("-" * 40)
    if generalization in ['STRONG', 'MODERATE'] and full_recipe > 50:
        print("Structural patterns are MANUSCRIPT-WIDE regularities, not page artifacts.")
        print("Evidence supports consistent functional slots (INGREDIENT -> PROCESS -> TARGET).")
    elif generalization in ['STRONG', 'MODERATE']:
        print("Category distributions generalize well, but recipe-like patterns are weak.")
        print("Structural regularity exists but may not follow medical recipe format.")
    else:
        print("Patterns show signs of OVERFITTING to training data.")
        print("Further investigation needed to determine if patterns are genuine.")
    print()

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'task1': {
            'top_3_sequences': [(list(s), c) for s, c in patterns['top_3_sequences']],
            'top_4_sequences': [(list(s), c) for s, c in patterns['top_4_sequences']],
            'transition_matrix': {k: dict(v) for k, v in prob_matrix.items()},
            'recipe_patterns': full_recipe,
            'universal_patterns': [(list(p), c) for p, c in section_analysis['universal_patterns'][:10]]
        },
        'task2': {
            'train_folios': len(train_folios),
            'test_folios': len(test_folios),
            'avg_distribution_error': avg_error,
            'avg_transition_accuracy': avg_trans,
            'generalization': generalization,
            'failures': [r['folio'] for r in failures]
        }
    }

    with open('structural_validation_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to structural_validation_results.json")


if __name__ == '__main__':
    main()
