#!/usr/bin/env python3
"""
F-AZC-001: Placement Prediction Model

Question: Can we predict which placement code a token receives from its morphology?

Method (per expert guidance):
1. Stage 1: Run ONE global model (all AZC)
2. Stage 2: Split by family ONLY IF accuracy is high

Features: PREFIX, MIDDLE, SUFFIX, token length
Target: Placement code (C, P, R, R1, R2, R3, S, S1, S2, etc.)
Model: Naive Bayes or Decision Tree (interpretability > accuracy)

Success Criteria:
- Accuracy > 50% (vs ~10% random baseline for 10 placements)
- Identify which morphological features drive placement
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from math import log2
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from archive.scripts.currier_a_token_generator import decompose_token

# AZC family assignments
ZODIAC_FAMILY = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}

AC_FAMILY = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}


def load_azc_tokens():
    """Load all AZC tokens with morphological decomposition."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    tokens = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # Filter to PRIMARY transcriber (H) only
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue
                currier = parts[6].strip('"').strip()
                if currier == 'NA':  # AZC tokens
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip()
                    placement = parts[10].strip('"').strip()

                    if token and placement:
                        result = decompose_token(token)
                        if result[0]:  # Successfully decomposed
                            prefix, middle, suffix = result

                            if folio in ZODIAC_FAMILY:
                                family = 'zodiac'
                            elif folio in AC_FAMILY:
                                family = 'ac'
                            else:
                                family = 'unknown'

                            tokens.append({
                                'token': token,
                                'folio': folio,
                                'family': family,
                                'placement': placement,
                                'prefix': prefix,
                                'middle': middle,
                                'suffix': suffix,
                                'length': len(token)
                            })
    return tokens


class NaiveBayesClassifier:
    """Simple Naive Bayes for categorical features."""

    def __init__(self, laplace_smoothing=1.0):
        self.laplace = laplace_smoothing
        self.class_priors = {}
        self.feature_probs = {}
        self.classes = []
        self.feature_names = []

    def fit(self, X, y):
        """Fit the classifier."""
        self.classes = list(set(y))
        self.feature_names = list(X[0].keys()) if X else []

        # Count class occurrences
        class_counts = Counter(y)
        total = len(y)

        for c in self.classes:
            self.class_priors[c] = class_counts[c] / total

        # Count feature occurrences per class
        self.feature_probs = {c: {f: defaultdict(int) for f in self.feature_names} for c in self.classes}
        feature_totals = {c: {f: 0 for f in self.feature_names} for c in self.classes}

        for xi, yi in zip(X, y):
            for f, v in xi.items():
                self.feature_probs[yi][f][v] += 1
                feature_totals[yi][f] += 1

        # Convert to probabilities with Laplace smoothing
        for c in self.classes:
            for f in self.feature_names:
                vocab_size = len(set(self.feature_probs[c][f].keys()))
                total_f = feature_totals[c][f]

                for v in self.feature_probs[c][f]:
                    self.feature_probs[c][f][v] = (
                        (self.feature_probs[c][f][v] + self.laplace) /
                        (total_f + self.laplace * (vocab_size + 1))
                    )

                # Unknown value probability
                self.feature_probs[c][f]['__UNKNOWN__'] = self.laplace / (total_f + self.laplace * (vocab_size + 1))

    def predict_proba(self, x):
        """Predict class probabilities for a single instance."""
        probs = {}
        for c in self.classes:
            log_prob = log2(self.class_priors[c])
            for f, v in x.items():
                if v in self.feature_probs[c][f]:
                    log_prob += log2(self.feature_probs[c][f][v])
                else:
                    log_prob += log2(self.feature_probs[c][f]['__UNKNOWN__'])
            probs[c] = log_prob

        # Convert log probs to normalized probabilities
        max_log = max(probs.values())
        probs = {c: 2 ** (p - max_log) for c, p in probs.items()}
        total = sum(probs.values())
        return {c: p / total for c, p in probs.items()}

    def predict(self, x):
        """Predict class for a single instance."""
        probs = self.predict_proba(x)
        return max(probs, key=probs.get)


def evaluate_classifier(tokens, use_family_split=False):
    """Evaluate placement prediction accuracy."""

    # Prepare features
    features = []
    labels = []

    for t in tokens:
        features.append({
            'prefix': t['prefix'],
            'middle': t['middle'],
            'suffix': t['suffix'],
            'length_bin': 'short' if t['length'] <= 5 else 'medium' if t['length'] <= 8 else 'long'
        })
        labels.append(t['placement'])

    # Simple train/test split (80/20)
    n = len(features)
    np.random.seed(42)
    indices = np.random.permutation(n)
    train_size = int(0.8 * n)

    train_idx = indices[:train_size]
    test_idx = indices[train_size:]

    X_train = [features[i] for i in train_idx]
    y_train = [labels[i] for i in train_idx]
    X_test = [features[i] for i in test_idx]
    y_test = [labels[i] for i in test_idx]

    # Train and evaluate
    clf = NaiveBayesClassifier()
    clf.fit(X_train, y_train)

    # Predictions
    predictions = [clf.predict(x) for x in X_test]

    # Accuracy
    correct = sum(1 for p, t in zip(predictions, y_test) if p == t)
    accuracy = correct / len(y_test)

    # Per-class accuracy
    class_correct = defaultdict(int)
    class_total = defaultdict(int)

    for p, t in zip(predictions, y_test):
        class_total[t] += 1
        if p == t:
            class_correct[t] += 1

    class_accuracy = {c: class_correct[c] / class_total[c] for c in class_total}

    # Random baseline
    label_dist = Counter(labels)
    random_baseline = max(label_dist.values()) / len(labels)

    return {
        'accuracy': accuracy,
        'random_baseline': random_baseline,
        'n_train': len(X_train),
        'n_test': len(y_test),
        'n_classes': len(set(labels)),
        'class_accuracy': class_accuracy,
        'class_distribution': {c: n / len(labels) for c, n in label_dist.items()}
    }


def analyze_feature_importance(tokens):
    """Analyze which features best discriminate placements."""

    placement_features = defaultdict(lambda: {
        'prefixes': Counter(),
        'middles': Counter(),
        'suffixes': Counter()
    })

    for t in tokens:
        p = t['placement']
        placement_features[p]['prefixes'][t['prefix']] += 1
        placement_features[p]['middles'][t['middle']] += 1
        placement_features[p]['suffixes'][t['suffix']] += 1

    # Find discriminating features
    discriminators = []

    for placement, features in placement_features.items():
        total = sum(features['prefixes'].values())
        if total < 20:  # Skip rare placements
            continue

        # Top prefix
        top_prefix = features['prefixes'].most_common(1)
        if top_prefix:
            prefix, count = top_prefix[0]
            pct = count / total * 100
            discriminators.append({
                'placement': placement,
                'feature_type': 'prefix',
                'feature': prefix,
                'count': count,
                'pct': pct
            })

        # Top suffix
        top_suffix = features['suffixes'].most_common(1)
        if top_suffix:
            suffix, count = top_suffix[0]
            pct = count / total * 100
            discriminators.append({
                'placement': placement,
                'feature_type': 'suffix',
                'feature': suffix,
                'count': count,
                'pct': pct
            })

    return discriminators


def main():
    print("=" * 60)
    print("F-AZC-001: Placement Prediction Model")
    print("=" * 60)
    print()

    # Load data
    tokens = load_azc_tokens()
    print(f"Total decomposed AZC tokens: {len(tokens)}")
    print()

    # Stage 1: Global model (all AZC)
    print("=" * 60)
    print("STAGE 1: Global Model (All AZC)")
    print("=" * 60)
    print()

    global_results = evaluate_classifier(tokens)

    print(f"Accuracy: {global_results['accuracy']:.1%}")
    print(f"Random baseline: {global_results['random_baseline']:.1%}")
    print(f"Lift over random: {global_results['accuracy'] / global_results['random_baseline']:.2f}x")
    print(f"Classes: {global_results['n_classes']}")
    print()

    print("Per-class accuracy:")
    for c, acc in sorted(global_results['class_accuracy'].items(), key=lambda x: -x[1]):
        dist = global_results['class_distribution'].get(c, 0)
        print(f"  {c:6s}: {acc:.1%} (support: {dist:.1%})")
    print()

    # Stage 2: Family split (only if global accuracy is reasonable)
    zodiac_tokens = [t for t in tokens if t['family'] == 'zodiac']
    ac_tokens = [t for t in tokens if t['family'] == 'ac']

    print("=" * 60)
    print("STAGE 2: Family-Split Models")
    print("=" * 60)
    print()

    print(f"Zodiac tokens: {len(zodiac_tokens)}")
    print(f"A/C tokens: {len(ac_tokens)}")
    print()

    zodiac_results = None
    ac_results = None

    if len(zodiac_tokens) > 100:
        zodiac_results = evaluate_classifier(zodiac_tokens)
        print(f"Zodiac accuracy: {zodiac_results['accuracy']:.1%} (baseline: {zodiac_results['random_baseline']:.1%})")
    else:
        print("Zodiac: Insufficient data for separate model")

    if len(ac_tokens) > 100:
        ac_results = evaluate_classifier(ac_tokens)
        print(f"A/C accuracy: {ac_results['accuracy']:.1%} (baseline: {ac_results['random_baseline']:.1%})")
    else:
        print("A/C: Insufficient data for separate model")
    print()

    # Feature importance
    print("=" * 60)
    print("Feature Discriminators")
    print("=" * 60)
    print()

    discriminators = analyze_feature_importance(tokens)

    print("Top features by placement:")
    for d in sorted(discriminators, key=lambda x: -x['pct'])[:15]:
        print(f"  {d['placement']:6s} <- {d['feature_type']:6s} '{d['feature']}' ({d['pct']:.1f}%)")
    print()

    # Interpretation
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print()

    success = global_results['accuracy'] > 0.5

    if success:
        interpretation = "Morphology PREDICTS placement - AZC is a legality mapper keyed to token roles"
        fit_tier = "F2"
    elif global_results['accuracy'] > global_results['random_baseline'] * 1.5:
        interpretation = "Morphology PARTIALLY predicts placement - weak but detectable rule structure"
        fit_tier = "F3"
    else:
        interpretation = "Morphology does NOT predict placement - placement is diagrammatic only"
        fit_tier = "F4"

    print(f"Finding: {interpretation}")
    print(f"Fit tier: {fit_tier}")

    # Prepare output
    output = {
        'fit_id': 'F-AZC-001',
        'question': 'Can morphology predict placement?',
        'metadata': {
            'total_tokens': len(tokens),
            'zodiac_tokens': len(zodiac_tokens),
            'ac_tokens': len(ac_tokens)
        },
        'stage_1_global': {
            'accuracy': round(global_results['accuracy'], 4),
            'random_baseline': round(global_results['random_baseline'], 4),
            'lift': round(global_results['accuracy'] / global_results['random_baseline'], 2),
            'n_classes': global_results['n_classes'],
            'class_accuracy': {k: round(v, 4) for k, v in global_results['class_accuracy'].items()},
            'class_distribution': {k: round(v, 4) for k, v in global_results['class_distribution'].items()}
        },
        'stage_2_split': {
            'zodiac': {
                'accuracy': round(zodiac_results['accuracy'], 4) if zodiac_results else None,
                'baseline': round(zodiac_results['random_baseline'], 4) if zodiac_results else None
            },
            'ac': {
                'accuracy': round(ac_results['accuracy'], 4) if ac_results else None,
                'baseline': round(ac_results['random_baseline'], 4) if ac_results else None
            }
        },
        'feature_discriminators': [
            {
                'placement': d['placement'],
                'feature_type': d['feature_type'],
                'feature': d['feature'],
                'pct': round(d['pct'], 1)
            }
            for d in sorted(discriminators, key=lambda x: -x['pct'])[:20]
        ],
        'success_criteria': {
            'target': 0.50,
            'achieved': round(global_results['accuracy'], 4),
            'met': success
        },
        'interpretation': {
            'finding': interpretation,
            'fit_tier': fit_tier
        }
    }

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_placement_prediction.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == '__main__':
    main()
