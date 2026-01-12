"""
Currier A Sister-Pair Classifier Model (Target 2)

Tests hypothesis: ch vs sh (and ok vs ot) choice is determined by contextual features.

Success criteria:
- Classification accuracy >75% (vs 50% baseline)
- Feature hierarchy: MIDDLE > SUFFIX > context (matches C410)
"""

import json
import random
from collections import defaultdict, Counter
from pathlib import Path

# Known prefixes
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SUFFIXES = ['aiin', 'ain', 'ar', 'al', 'or', 'ol', 'am', 'an', 'in',
            'y', 'dy', 'ey', 'edy', 'eedy', 'chy', 'shy',
            'r', 'l', 's', 'd', 'n', 'm']
SUFFIX_PATTERNS = sorted(SUFFIXES, key=len, reverse=True)


def decompose_token(token):
    """Decompose token into PREFIX + MIDDLE + SUFFIX."""
    prefix = None
    remainder = token

    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            remainder = token[len(p):]
            break

    if not prefix:
        return None, None, None

    suffix = None
    middle = remainder

    for s in SUFFIX_PATTERNS:
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            middle = remainder[:-len(s)]
            break
        elif remainder == s:
            suffix = s
            middle = ''
            break

    if not suffix:
        if len(remainder) >= 2:
            suffix = remainder[-2:]
            middle = remainder[:-2]
        elif len(remainder) == 1:
            suffix = remainder
            middle = ''
        else:
            suffix = ''
            middle = ''

    return prefix, middle, suffix


def load_currier_a_with_context():
    """Load Currier A tokens with context for sister-pair analysis."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    # Load all A tokens in order
    all_tokens = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 11:
                currier = parts[6].strip('"').strip()
                if currier == 'A':
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                    quire = parts[4].strip('"').strip() if len(parts) > 4 else ''
                    line_num = parts[11].strip('"').strip()

                    if token:
                        prefix, middle, suffix = decompose_token(token)
                        all_tokens.append({
                            'token': token,
                            'prefix': prefix,
                            'middle': middle,
                            'suffix': suffix,
                            'folio': folio,
                            'section': section,
                            'quire': quire,
                            'line_num': line_num
                        })

    return all_tokens


def build_ch_sh_dataset(all_tokens):
    """Build dataset for ch/sh classification."""
    # Filter to ch/sh tokens
    dataset = []

    for i, t in enumerate(all_tokens):
        if t['prefix'] in ('ch', 'sh'):
            # Get preceding token info
            prev_prefix = None
            prev_middle = None
            if i > 0 and all_tokens[i-1]['folio'] == t['folio']:
                prev_prefix = all_tokens[i-1]['prefix']
                prev_middle = all_tokens[i-1]['middle']

            # Get following token info
            next_prefix = None
            if i < len(all_tokens) - 1 and all_tokens[i+1]['folio'] == t['folio']:
                next_prefix = all_tokens[i+1]['prefix']

            dataset.append({
                'label': 1 if t['prefix'] == 'ch' else 0,  # 1=ch, 0=sh
                'middle': t['middle'] or '_EMPTY_',
                'suffix': t['suffix'] or '_EMPTY_',
                'section': t['section'],
                'quire': t['quire'],
                'prev_prefix': prev_prefix or '_NONE_',
                'prev_is_ch': prev_prefix == 'ch' if prev_prefix in ('ch', 'sh') else None,
                'next_prefix': next_prefix or '_NONE_',
            })

    return dataset


def train_naive_bayes(train_data, feature_name):
    """Train a simple Naive Bayes classifier on a single feature."""
    # Count P(feature|class)
    class_counts = Counter(d['label'] for d in train_data)
    feature_given_class = {0: Counter(), 1: Counter()}

    for d in train_data:
        feature_given_class[d['label']][d[feature_name]] += 1

    # Convert to probabilities with Laplace smoothing
    vocab = set(d[feature_name] for d in train_data)
    alpha = 1.0  # Laplace smoothing

    probs = {}
    for label in [0, 1]:
        probs[label] = {}
        total = sum(feature_given_class[label].values()) + alpha * len(vocab)
        for feat in vocab:
            count = feature_given_class[label].get(feat, 0)
            probs[label][feat] = (count + alpha) / total

    # Prior P(class)
    total = len(train_data)
    prior = {0: class_counts[0] / total, 1: class_counts[1] / total}

    return probs, prior, vocab


def predict_naive_bayes(sample, probs, prior, vocab, feature_name):
    """Predict class using Naive Bayes."""
    feat = sample[feature_name]
    alpha = 1.0

    # Calculate P(class|feature) proportional to P(feature|class) * P(class)
    scores = {}
    for label in [0, 1]:
        if feat in probs[label]:
            p_feat = probs[label][feat]
        else:
            # Unseen feature - use smoothed probability
            total = sum(probs[label].values())
            p_feat = alpha / (total + alpha * len(vocab))
        scores[label] = p_feat * prior[label]

    return 1 if scores[1] > scores[0] else 0


def evaluate_single_feature(dataset, feature_name, n_folds=5):
    """Evaluate a single feature using cross-validation."""
    random.shuffle(dataset)
    fold_size = len(dataset) // n_folds

    accuracies = []
    for fold in range(n_folds):
        # Split
        test_start = fold * fold_size
        test_end = (fold + 1) * fold_size if fold < n_folds - 1 else len(dataset)
        test_data = dataset[test_start:test_end]
        train_data = dataset[:test_start] + dataset[test_end:]

        # Train
        probs, prior, vocab = train_naive_bayes(train_data, feature_name)

        # Test
        correct = sum(1 for d in test_data
                     if predict_naive_bayes(d, probs, prior, vocab, feature_name) == d['label'])
        accuracies.append(correct / len(test_data))

    return sum(accuracies) / len(accuracies)


def train_combined_model(train_data, features):
    """Train a model combining multiple features."""
    models = {}
    for feat in features:
        probs, prior, vocab = train_naive_bayes(train_data, feat)
        models[feat] = (probs, prior, vocab)
    return models


def predict_combined(sample, models, features, weights=None):
    """Predict using weighted combination of features."""
    if weights is None:
        weights = {f: 1.0 for f in features}

    log_scores = {0: 0.0, 1: 0.0}

    for feat in features:
        probs, prior, vocab = models[feat]
        val = sample[feat]

        for label in [0, 1]:
            if val in probs[label]:
                p = probs[label][val]
            else:
                p = 0.01  # Small probability for unseen
            log_scores[label] += weights[feat] * p

    return 1 if log_scores[1] > log_scores[0] else 0


def analyze_feature_importance(dataset, features):
    """Analyze which features are most predictive."""
    print("\n" + "=" * 60)
    print("FEATURE IMPORTANCE ANALYSIS")
    print("=" * 60)

    # Test each feature independently
    results = {}
    for feat in features:
        acc = evaluate_single_feature(dataset.copy(), feat)
        results[feat] = acc
        print(f"\n{feat}: {100*acc:.1f}% accuracy")

    # Rank features
    ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)
    print("\n\nFeature ranking by accuracy:")
    for i, (feat, acc) in enumerate(ranked, 1):
        print(f"  {i}. {feat}: {100*acc:.1f}%")

    return results


def main():
    print("=" * 60)
    print("CURRIER A SISTER-PAIR CLASSIFIER (Target 2)")
    print("=" * 60)

    # Load data
    all_tokens = load_currier_a_with_context()
    print(f"\nLoaded {len(all_tokens)} Currier A tokens")

    # Build ch/sh dataset
    dataset = build_ch_sh_dataset(all_tokens)
    print(f"ch/sh samples: {len(dataset)}")

    # Class distribution
    ch_count = sum(1 for d in dataset if d['label'] == 1)
    sh_count = len(dataset) - ch_count
    baseline = max(ch_count, sh_count) / len(dataset)
    print(f"\nClass distribution:")
    print(f"  ch: {ch_count} ({100*ch_count/len(dataset):.1f}%)")
    print(f"  sh: {sh_count} ({100*sh_count/len(dataset):.1f}%)")
    print(f"  Baseline (majority class): {100*baseline:.1f}%")

    # Features to test
    features = ['middle', 'suffix', 'section', 'quire', 'prev_prefix']

    # Analyze feature importance
    feature_accuracies = analyze_feature_importance(dataset, features)

    # Combined model evaluation
    print("\n" + "=" * 60)
    print("COMBINED MODEL EVALUATION")
    print("=" * 60)

    # Cross-validation for combined model
    random.shuffle(dataset)
    n_folds = 5
    fold_size = len(dataset) // n_folds

    combined_accuracies = []
    for fold in range(n_folds):
        test_start = fold * fold_size
        test_end = (fold + 1) * fold_size if fold < n_folds - 1 else len(dataset)
        test_data = dataset[test_start:test_end]
        train_data = dataset[:test_start] + dataset[test_end:]

        # Train combined model
        models = train_combined_model(train_data, features)

        # Predict
        correct = sum(1 for d in test_data
                     if predict_combined(d, models, features) == d['label'])
        combined_accuracies.append(correct / len(test_data))

    combined_acc = sum(combined_accuracies) / len(combined_accuracies)
    print(f"\nCombined model accuracy: {100*combined_acc:.1f}%")

    # Overall assessment
    print("\n" + "=" * 60)
    print("OVERALL ASSESSMENT")
    print("=" * 60)

    best_single = max(feature_accuracies.values())
    best_feature = max(feature_accuracies.keys(), key=lambda x: feature_accuracies[x])

    print(f"\nBaseline accuracy: {100*baseline:.1f}%")
    print(f"Target accuracy: >75%")
    print(f"Best single feature ({best_feature}): {100*best_single:.1f}%")
    print(f"Combined model: {100*combined_acc:.1f}%")

    # Check feature hierarchy (should be MIDDLE > SUFFIX > context)
    middle_acc = feature_accuracies.get('middle', 0)
    suffix_acc = feature_accuracies.get('suffix', 0)
    section_acc = feature_accuracies.get('section', 0)

    print(f"\n\nFeature hierarchy check (expected: MIDDLE > SUFFIX > section):")
    print(f"  MIDDLE: {100*middle_acc:.1f}%")
    print(f"  SUFFIX: {100*suffix_acc:.1f}%")
    print(f"  section: {100*section_acc:.1f}%")

    hierarchy_correct = middle_acc > suffix_acc > section_acc
    print(f"  Hierarchy matches C410: {'YES' if hierarchy_correct else 'NO'}")

    # Overall pass/fail
    passes_accuracy = combined_acc > 0.75
    print(f"\n\nAccuracy target (>75%): {'PASS' if passes_accuracy else 'FAIL'}")
    print(f"Hierarchy correct: {'PASS' if hierarchy_correct else 'FAIL'}")

    # Save results
    results = {
        'baseline_accuracy': baseline,
        'target_accuracy': 0.75,
        'best_single_feature': best_feature,
        'best_single_accuracy': best_single,
        'combined_accuracy': combined_acc,
        'feature_accuracies': feature_accuracies,
        'hierarchy_check': {
            'middle': middle_acc,
            'suffix': suffix_acc,
            'section': section_acc,
            'correct_order': hierarchy_correct
        },
        'passes_accuracy_target': passes_accuracy,
        'class_distribution': {'ch': ch_count, 'sh': sh_count},
        'total_samples': len(dataset)
    }

    output_path = Path(__file__).parent.parent.parent / 'results' / 'currier_a_sister_pair_classifier.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
