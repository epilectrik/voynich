#!/usr/bin/env python3
"""
F-AZC-003: Family Membership Classifier (CONFIRMATORY)

Question: Can we predict Zodiac vs A/C membership from token morphology alone?

Method:
- Features: PREFIX, MIDDLE, SUFFIX distributions
- Target: Family (Zodiac vs A/C)
- Model: Naive Bayes classifier
- Identify discriminating features

Success Criteria:
- Accuracy > 80% (vs 61% baseline for A/C majority)
- Identify which prefixes/suffixes are family-diagnostic

Why This Matters:
Not a discovery fit - a convergence check. If morphology alone predicts family:
"Zodiac vs A/C are not just layout regimes - they are two tuned legality systems acting on shared type space."
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
            if len(parts) > 6:
                currier = parts[6].strip('"').strip()
                if currier == 'NA':  # AZC tokens
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip()

                    if not token:
                        continue

                    result = decompose_token(token)
                    if not result[0]:
                        continue

                    prefix, middle, suffix = result

                    if folio in ZODIAC_FAMILY:
                        family = 'zodiac'
                    elif folio in AC_FAMILY:
                        family = 'ac'
                    else:
                        continue  # Skip unknown family

                    tokens.append({
                        'token': token,
                        'folio': folio,
                        'family': family,
                        'prefix': prefix,
                        'middle': middle,
                        'suffix': suffix
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
        self.feature_vocabs = {}

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

        # Collect vocabularies
        for f in self.feature_names:
            vocab = set()
            for c in self.classes:
                vocab.update(self.feature_probs[c][f].keys())
            self.feature_vocabs[f] = vocab

        # Convert to probabilities with Laplace smoothing
        for c in self.classes:
            for f in self.feature_names:
                vocab_size = len(self.feature_vocabs[f])
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

    def get_feature_importance(self):
        """Calculate feature importance based on class discrimination."""
        importance = {}

        for f in self.feature_names:
            # Calculate KL divergence between class distributions
            vocab = self.feature_vocabs[f]
            kl_div = 0.0

            for v in vocab:
                p = self.feature_probs[self.classes[0]][f].get(v, self.feature_probs[self.classes[0]][f]['__UNKNOWN__'])
                q = self.feature_probs[self.classes[1]][f].get(v, self.feature_probs[self.classes[1]][f]['__UNKNOWN__'])

                if p > 0 and q > 0:
                    kl_div += p * log2(p / q)

            importance[f] = kl_div

        return importance


def identify_diagnostic_features(tokens):
    """Identify features that discriminate between families."""

    # Count features by family
    family_features = {
        'zodiac': {'prefixes': Counter(), 'suffixes': Counter(), 'middles': Counter()},
        'ac': {'prefixes': Counter(), 'suffixes': Counter(), 'middles': Counter()}
    }

    for t in tokens:
        family_features[t['family']]['prefixes'][t['prefix']] += 1
        family_features[t['family']]['suffixes'][t['suffix']] += 1
        family_features[t['family']]['middles'][t['middle']] += 1

    # Calculate totals
    z_total = sum(family_features['zodiac']['prefixes'].values())
    ac_total = sum(family_features['ac']['prefixes'].values())

    # Find discriminating features
    diagnostics = []

    for feature_type in ['prefixes', 'suffixes']:
        z_counts = family_features['zodiac'][feature_type]
        ac_counts = family_features['ac'][feature_type]

        all_features = set(z_counts.keys()) | set(ac_counts.keys())

        for f in all_features:
            z_pct = z_counts.get(f, 0) / z_total * 100 if z_total > 0 else 0
            ac_pct = ac_counts.get(f, 0) / ac_total * 100 if ac_total > 0 else 0

            if z_pct == 0 and ac_pct == 0:
                continue

            # Calculate lift
            if ac_pct > 0:
                z_lift = z_pct / ac_pct
            else:
                z_lift = float('inf') if z_pct > 0 else 1.0

            if z_pct > 0:
                ac_lift = ac_pct / z_pct
            else:
                ac_lift = float('inf') if ac_pct > 0 else 1.0

            # Which family does this feature favor?
            if z_lift > 1.5 or ac_lift > 1.5:
                favors = 'zodiac' if z_lift > ac_lift else 'ac'
                lift = max(z_lift, ac_lift)

                diagnostics.append({
                    'feature': f,
                    'type': feature_type.rstrip('s'),
                    'zodiac_pct': z_pct,
                    'ac_pct': ac_pct,
                    'favors': favors,
                    'lift': lift
                })

    return sorted(diagnostics, key=lambda x: -x['lift'])[:20]


def main():
    print("=" * 60)
    print("F-AZC-003: Family Membership Classifier (CONFIRMATORY)")
    print("=" * 60)
    print()

    # Load data
    tokens = load_azc_tokens()

    zodiac_count = sum(1 for t in tokens if t['family'] == 'zodiac')
    ac_count = sum(1 for t in tokens if t['family'] == 'ac')

    print(f"Total decomposed AZC tokens: {len(tokens)}")
    print(f"Zodiac tokens: {zodiac_count} ({zodiac_count/len(tokens)*100:.1f}%)")
    print(f"A/C tokens: {ac_count} ({ac_count/len(tokens)*100:.1f}%)")
    print()

    # Baseline (majority class)
    baseline = max(zodiac_count, ac_count) / len(tokens)
    majority_class = 'ac' if ac_count > zodiac_count else 'zodiac'
    print(f"Baseline (majority class '{majority_class}'): {baseline:.1%}")
    print()

    # Prepare features
    features = []
    labels = []

    for t in tokens:
        features.append({
            'prefix': t['prefix'],
            'middle': t['middle'],
            'suffix': t['suffix']
        })
        labels.append(t['family'])

    # Train/test split (80/20)
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

    # Train classifier
    print("=" * 60)
    print("Classification Results")
    print("=" * 60)
    print()

    clf = NaiveBayesClassifier()
    clf.fit(X_train, y_train)

    # Predictions
    predictions = [clf.predict(x) for x in X_test]

    # Accuracy
    correct = sum(1 for p, t in zip(predictions, y_test) if p == t)
    accuracy = correct / len(y_test)

    # Per-class metrics
    tp = {'zodiac': 0, 'ac': 0}
    fp = {'zodiac': 0, 'ac': 0}
    fn = {'zodiac': 0, 'ac': 0}

    for p, t in zip(predictions, y_test):
        if p == t:
            tp[t] += 1
        else:
            fp[p] += 1
            fn[t] += 1

    precision = {c: tp[c] / (tp[c] + fp[c]) if (tp[c] + fp[c]) > 0 else 0 for c in ['zodiac', 'ac']}
    recall = {c: tp[c] / (tp[c] + fn[c]) if (tp[c] + fn[c]) > 0 else 0 for c in ['zodiac', 'ac']}
    f1 = {c: 2 * precision[c] * recall[c] / (precision[c] + recall[c]) if (precision[c] + recall[c]) > 0 else 0 for c in ['zodiac', 'ac']}

    print(f"Accuracy: {accuracy:.1%}")
    print(f"Lift over baseline: {accuracy / baseline:.2f}x")
    print()

    print(f"{'Class':<10} {'Precision':>10} {'Recall':>10} {'F1':>10}")
    print("-" * 40)
    for c in ['zodiac', 'ac']:
        print(f"{c:<10} {precision[c]:>10.1%} {recall[c]:>10.1%} {f1[c]:>10.1%}")
    print()

    # Feature importance
    print("=" * 60)
    print("Feature Importance (KL divergence)")
    print("=" * 60)
    print()

    importance = clf.get_feature_importance()
    for f, imp in sorted(importance.items(), key=lambda x: -x[1]):
        print(f"  {f}: {imp:.3f}")
    print()

    # Diagnostic features
    print("=" * 60)
    print("Diagnostic Features")
    print("=" * 60)
    print()

    diagnostics = identify_diagnostic_features(tokens)

    print(f"{'Feature':<12} {'Type':<8} {'Zodiac%':>8} {'A/C%':>8} {'Favors':>8} {'Lift':>8}")
    print("-" * 60)
    for d in diagnostics[:15]:
        lift_str = f"{d['lift']:.1f}x" if d['lift'] != float('inf') else "INF"
        print(f"{d['feature']:<12} {d['type']:<8} {d['zodiac_pct']:>7.1f}% {d['ac_pct']:>7.1f}% {d['favors']:>8} {lift_str:>8}")
    print()

    # Interpretation
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print()

    success = accuracy > 0.80

    if success:
        interpretation = "Morphology PREDICTS family - Zodiac and A/C are tuned legality systems"
        fit_tier = "F2"
    elif accuracy > baseline * 1.2:
        interpretation = "Morphology PARTIALLY predicts family - weak but detectable tuning"
        fit_tier = "F3"
    else:
        interpretation = "Morphology does NOT predict family - families differ only in layout"
        fit_tier = "F4"

    print(f"Success criterion: accuracy > 80%")
    print(f"Achieved: {accuracy:.1%}")
    print(f"Result: {'SUCCESS' if success else 'PARTIAL' if accuracy > baseline * 1.2 else 'FAILED'}")
    print()
    print(f"Finding: {interpretation}")
    print(f"Fit tier: {fit_tier}")

    # Prepare output
    output = {
        'fit_id': 'F-AZC-003',
        'question': 'Can morphology predict Zodiac vs A/C family membership?',
        'metadata': {
            'total_tokens': len(tokens),
            'zodiac_tokens': zodiac_count,
            'ac_tokens': ac_count,
            'train_size': len(X_train),
            'test_size': len(X_test)
        },
        'baseline': {
            'majority_class': majority_class,
            'accuracy': round(baseline, 4)
        },
        'classification': {
            'accuracy': round(accuracy, 4),
            'lift_over_baseline': round(accuracy / baseline, 2),
            'per_class': {
                c: {
                    'precision': round(precision[c], 4),
                    'recall': round(recall[c], 4),
                    'f1': round(f1[c], 4)
                }
                for c in ['zodiac', 'ac']
            }
        },
        'feature_importance': {k: round(v, 4) for k, v in importance.items()},
        'diagnostic_features': [
            {
                'feature': d['feature'],
                'type': d['type'],
                'zodiac_pct': round(d['zodiac_pct'], 2),
                'ac_pct': round(d['ac_pct'], 2),
                'favors': d['favors'],
                'lift': round(d['lift'], 2) if d['lift'] != float('inf') else 'INF'
            }
            for d in diagnostics[:15]
        ],
        'success_criteria': {
            'target': 0.80,
            'achieved': round(accuracy, 4),
            'met': success
        },
        'interpretation': {
            'finding': interpretation,
            'fit_tier': fit_tier
        }
    }

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_family_classifier.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == '__main__':
    main()
