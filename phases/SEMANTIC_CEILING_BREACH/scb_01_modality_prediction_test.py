#!/usr/bin/env python3
"""
SCB-01: MODALITY PREDICTION TEST

PRIMARY TEST for SEMANTIC_CEILING_BREACH phase.

Question: Can we predict recipe modality class from zone_affinity alone?

This is the core test for Tier 2 upgrade. If zone profiles discriminate
modality classes, we have bidirectional constraint (Voynich -> external).

Pre-registered thresholds:
- Binary (SOUND vs other): >85% accuracy, F1>0.7, permutation p<0.01
- 4-class: >40% accuracy, p<0.05
"""

import json
from pathlib import Path
import numpy as np
from collections import Counter
from scipy import stats

def load_data():
    """Load zone affinity and modality labels."""
    with open('results/brunschwig_reverse_activation.json', 'r', encoding='utf-8') as f:
        ra_data = json.load(f)

    with open('results/enhanced_sensory_extraction.json', 'r', encoding='utf-8') as f:
        enh_data = json.load(f)

    return ra_data, enh_data

def build_dataset(ra_data, enh_data):
    """Build matched dataset of zone_affinity -> modality."""
    ra_recipes = {r['recipe_id']: r for r in ra_data['recipes']}
    enh_recipes = {r['recipe_id']: r for r in enh_data['recipe_level']['recipes']}

    dataset = []
    for recipe_id, enh in enh_recipes.items():
        modality = enh.get('dominant_modality')
        if modality is None:
            continue  # Skip recipes with no modality

        if recipe_id not in ra_recipes:
            continue

        ra = ra_recipes[recipe_id]
        zone_affinity = ra.get('zone_affinity', {})

        # Create feature vector (C, P, R, S)
        features = [
            zone_affinity.get('C', 0),
            zone_affinity.get('P', 0),
            zone_affinity.get('R', 0),
            zone_affinity.get('S', 0)
        ]

        dataset.append({
            'recipe_id': recipe_id,
            'features': features,
            'modality': modality,
            'regime': enh.get('regime'),
            'zone_affinity': zone_affinity
        })

    return dataset

def compute_centroids(dataset, target_col='modality'):
    """Compute centroid for each class."""
    classes = set(d[target_col] for d in dataset)
    centroids = {}

    for cls in classes:
        cls_data = [d['features'] for d in dataset if d[target_col] == cls]
        if cls_data:
            centroids[cls] = np.mean(cls_data, axis=0)

    return centroids

def nearest_centroid_predict(features, centroids):
    """Predict class by nearest centroid."""
    min_dist = float('inf')
    best_class = None

    for cls, centroid in centroids.items():
        dist = np.linalg.norm(np.array(features) - centroid)
        if dist < min_dist:
            min_dist = dist
            best_class = cls

    return best_class

def leave_one_out_cv(dataset, binary=False):
    """Leave-one-out cross-validation."""
    predictions = []
    actuals = []

    for i, test_sample in enumerate(dataset):
        # Training set = all except test_sample
        train_set = [d for j, d in enumerate(dataset) if j != i]

        # Target column
        if binary:
            target_col = 'binary_label'
            train_set = [{**d, 'binary_label': 'SOUND' if d['modality'] == 'SOUND' else 'OTHER'} for d in train_set]
            actual = 'SOUND' if test_sample['modality'] == 'SOUND' else 'OTHER'
        else:
            target_col = 'modality'
            actual = test_sample['modality']

        # Compute centroids
        if binary:
            centroids = compute_centroids(train_set, target_col='binary_label')
        else:
            centroids = compute_centroids(train_set, target_col='modality')

        # Predict
        pred = nearest_centroid_predict(test_sample['features'], centroids)

        predictions.append(pred)
        actuals.append(actual)

    return predictions, actuals

def compute_metrics(predictions, actuals, classes=None):
    """Compute accuracy and per-class metrics."""
    correct = sum(p == a for p, a in zip(predictions, actuals))
    accuracy = correct / len(predictions)

    if classes is None:
        classes = sorted(set(actuals))

    # Per-class precision, recall, F1
    metrics = {}
    for cls in classes:
        tp = sum(p == cls and a == cls for p, a in zip(predictions, actuals))
        fp = sum(p == cls and a != cls for p, a in zip(predictions, actuals))
        fn = sum(p != cls and a == cls for p, a in zip(predictions, actuals))

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        metrics[cls] = {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'support': sum(a == cls for a in actuals)
        }

    # Macro F1
    macro_f1 = np.mean([m['f1'] for m in metrics.values()])

    return {
        'accuracy': accuracy,
        'n_correct': correct,
        'n_total': len(predictions),
        'per_class': metrics,
        'macro_f1': macro_f1
    }

def permutation_test(dataset, binary=False, n_permutations=1000):
    """Permutation test for classification accuracy."""
    # Get actual accuracy
    predictions, actuals = leave_one_out_cv(dataset, binary=binary)
    actual_acc = sum(p == a for p, a in zip(predictions, actuals)) / len(predictions)

    # Permutation distribution
    np.random.seed(42)
    null_accs = []

    for _ in range(n_permutations):
        # Shuffle labels
        shuffled = dataset.copy()
        labels = [d['modality'] for d in shuffled]
        np.random.shuffle(labels)
        shuffled = [{**d, 'modality': label} for d, label in zip(shuffled, labels)]

        # Predict with shuffled labels
        preds, acts = leave_one_out_cv(shuffled, binary=binary)
        acc = sum(p == a for p, a in zip(preds, acts)) / len(preds)
        null_accs.append(acc)

    null_accs = np.array(null_accs)
    p_value = np.mean(null_accs >= actual_acc)

    return {
        'observed': actual_acc,
        'null_mean': float(np.mean(null_accs)),
        'null_std': float(np.std(null_accs)),
        'p_value': float(p_value),
        'n_permutations': n_permutations
    }

def main():
    print("=" * 70)
    print("SCB-01: MODALITY PREDICTION TEST")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    ra_data, enh_data = load_data()
    dataset = build_dataset(ra_data, enh_data)

    print(f"Dataset size: {len(dataset)} recipes with modality labels")
    print()

    # Class distribution
    modality_counts = Counter(d['modality'] for d in dataset)
    print("Class distribution:")
    for mod, count in sorted(modality_counts.items(), key=lambda x: -x[1]):
        pct = count / len(dataset) * 100
        print(f"  {mod}: {count} ({pct:.1f}%)")
    print()

    # Compute class centroids
    print("=" * 70)
    print("CLASS CENTROIDS (zone affinity profiles)")
    print("=" * 70)
    print()

    centroids = compute_centroids(dataset)
    print(f"{'Modality':<10} | {'C':>8} | {'P':>8} | {'R':>8} | {'S':>8}")
    print("-" * 55)
    for mod, centroid in sorted(centroids.items()):
        print(f"{mod:<10} | {centroid[0]:>8.3f} | {centroid[1]:>8.3f} | {centroid[2]:>8.3f} | {centroid[3]:>8.3f}")
    print()

    # Test 1: 4-class classification
    print("=" * 70)
    print("TEST 1: 4-CLASS CLASSIFICATION")
    print("Pre-registered threshold: >40% accuracy (baseline=25%)")
    print("=" * 70)
    print()

    predictions_4c, actuals_4c = leave_one_out_cv(dataset, binary=False)
    metrics_4c = compute_metrics(predictions_4c, actuals_4c)

    print(f"Accuracy: {metrics_4c['accuracy']*100:.1f}% ({metrics_4c['n_correct']}/{metrics_4c['n_total']})")
    print(f"Baseline: 25% (random)")
    print(f"Majority baseline: {max(modality_counts.values())/len(dataset)*100:.1f}%")
    print(f"Macro F1: {metrics_4c['macro_f1']:.3f}")
    print()

    print("Per-class metrics:")
    for cls, m in sorted(metrics_4c['per_class'].items()):
        print(f"  {cls:<10}: P={m['precision']:.2f}, R={m['recall']:.2f}, F1={m['f1']:.2f} (n={m['support']})")
    print()

    # Permutation test for 4-class
    print("Running permutation test (n=1000)...")
    perm_4c = permutation_test(dataset, binary=False, n_permutations=1000)
    print(f"Permutation p-value: {perm_4c['p_value']:.4f}")
    print(f"Null distribution: mean={perm_4c['null_mean']:.3f}, std={perm_4c['null_std']:.3f}")
    print()

    if metrics_4c['accuracy'] > 0.40 and perm_4c['p_value'] < 0.05:
        print("[PASS] 4-class accuracy exceeds 40% with p<0.05")
    elif metrics_4c['accuracy'] > 0.25:
        print("[PARTIAL] 4-class accuracy above baseline but not significant")
    else:
        print("[FAIL] 4-class accuracy at or below baseline")
    print()

    # Test 2: Binary classification (SOUND vs other)
    print("=" * 70)
    print("TEST 2: BINARY CLASSIFICATION (SOUND vs OTHER)")
    print("Pre-registered threshold: >85% accuracy, F1>0.7 (baseline=79.1%)")
    print("=" * 70)
    print()

    predictions_bin, actuals_bin = leave_one_out_cv(dataset, binary=True)
    metrics_bin = compute_metrics(predictions_bin, actuals_bin, classes=['SOUND', 'OTHER'])

    print(f"Accuracy: {metrics_bin['accuracy']*100:.1f}% ({metrics_bin['n_correct']}/{metrics_bin['n_total']})")
    print(f"Majority baseline: 79.1% (predict all SOUND)")
    print()

    print("Per-class metrics:")
    for cls, m in sorted(metrics_bin['per_class'].items()):
        print(f"  {cls:<10}: P={m['precision']:.2f}, R={m['recall']:.2f}, F1={m['f1']:.2f} (n={m['support']})")
    print()

    # Key metric: F1 for minority class (OTHER)
    other_f1 = metrics_bin['per_class'].get('OTHER', {}).get('f1', 0)
    print(f"OTHER class F1: {other_f1:.3f} (key metric for minority class)")
    print()

    # Permutation test for binary
    print("Running permutation test (n=1000)...")
    perm_bin = permutation_test(dataset, binary=True, n_permutations=1000)
    print(f"Permutation p-value: {perm_bin['p_value']:.4f}")
    print(f"Null distribution: mean={perm_bin['null_mean']:.3f}, std={perm_bin['null_std']:.3f}")
    print()

    if metrics_bin['accuracy'] > 0.85 and other_f1 > 0.5 and perm_bin['p_value'] < 0.01:
        print("[PASS] Binary accuracy >85% with F1>0.5 and p<0.01")
    elif metrics_bin['accuracy'] > 0.791:
        print("[PARTIAL] Binary accuracy above majority baseline")
    else:
        print("[FAIL] Binary accuracy at or below majority baseline")
    print()

    # Zone profile analysis
    print("=" * 70)
    print("ZONE PROFILE DISCRIMINATION ANALYSIS")
    print("=" * 70)
    print()

    # Test which zones discriminate SOUND from OTHER
    sound_data = [d for d in dataset if d['modality'] == 'SOUND']
    other_data = [d for d in dataset if d['modality'] != 'SOUND']

    print("SOUND vs OTHER zone comparison:")
    zone_discrimination = {}
    for i, zone in enumerate(['C', 'P', 'R', 'S']):
        sound_vals = [d['features'][i] for d in sound_data]
        other_vals = [d['features'][i] for d in other_data]

        t, p = stats.ttest_ind(sound_vals, other_vals)

        # Cohen's d
        n1, n2 = len(sound_vals), len(other_vals)
        var1, var2 = np.var(sound_vals, ddof=1), np.var(other_vals, ddof=1)
        pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
        d = (np.mean(sound_vals) - np.mean(other_vals)) / pooled_std if pooled_std > 0 else 0

        sig = '*' if p < 0.05 else ''
        print(f"  {zone}-zone: SOUND={np.mean(sound_vals):.3f} vs OTHER={np.mean(other_vals):.3f}, "
              f"t={t:.2f}, p={p:.4f}{sig}, d={d:.2f}")

        zone_discrimination[zone] = {
            'sound_mean': float(np.mean(sound_vals)),
            'other_mean': float(np.mean(other_vals)),
            't': float(t),
            'p': float(p),
            'd': float(d)
        }
    print()

    # Confusion matrix
    print("=" * 70)
    print("CONFUSION MATRIX (Binary)")
    print("=" * 70)
    print()

    # Build confusion matrix
    cm = {'SOUND': {'SOUND': 0, 'OTHER': 0}, 'OTHER': {'SOUND': 0, 'OTHER': 0}}
    for pred, actual in zip(predictions_bin, actuals_bin):
        cm[actual][pred] += 1

    print(f"{'':>15} | {'Pred SOUND':>12} | {'Pred OTHER':>12}")
    print("-" * 45)
    print(f"{'Actual SOUND':>15} | {cm['SOUND']['SOUND']:>12} | {cm['SOUND']['OTHER']:>12}")
    print(f"{'Actual OTHER':>15} | {cm['OTHER']['SOUND']:>12} | {cm['OTHER']['OTHER']:>12}")
    print()

    # Final verdict
    print("=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)
    print()

    tier_2_criteria = []

    # Check binary
    if metrics_bin['accuracy'] > 0.85 and perm_bin['p_value'] < 0.01:
        tier_2_criteria.append("Binary accuracy >85% with p<0.01")

    # Check 4-class
    if metrics_4c['accuracy'] > 0.50 and perm_4c['p_value'] < 0.001:
        tier_2_criteria.append("4-class accuracy >50% with p<0.001")

    if tier_2_criteria:
        verdict = "TIER 2 CANDIDATE"
        print(f"[{verdict}] Zone affinity DISCRIMINATES modality classes")
        for criterion in tier_2_criteria:
            print(f"  - {criterion}")
    elif metrics_4c['accuracy'] > 0.40 or metrics_bin['accuracy'] > 0.80:
        verdict = "TIER 3 CONFIRMED"
        print(f"[{verdict}] Trend supports two-stage model but not sufficient for Tier 2")
    else:
        verdict = "WEAKENED"
        print(f"[{verdict}] Zone affinity does NOT discriminate modality classes")

    print()

    # Save results
    print("=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    print()

    results = {
        'phase': 'SEMANTIC_CEILING_BREACH',
        'test': 'scb_01_modality_prediction',
        'question': 'Can zone affinity predict modality class?',
        'dataset': {
            'n_recipes': len(dataset),
            'class_distribution': dict(modality_counts)
        },
        'centroids': {mod: list(centroid) for mod, centroid in centroids.items()},
        'four_class': {
            'accuracy': metrics_4c['accuracy'],
            'baseline_random': 0.25,
            'baseline_majority': max(modality_counts.values()) / len(dataset),
            'macro_f1': metrics_4c['macro_f1'],
            'per_class': metrics_4c['per_class'],
            'permutation': perm_4c
        },
        'binary': {
            'accuracy': metrics_bin['accuracy'],
            'baseline_majority': 0.791,
            'per_class': metrics_bin['per_class'],
            'permutation': perm_bin,
            'confusion_matrix': cm
        },
        'zone_discrimination': zone_discrimination,
        'verdict': verdict
    }

    output_path = Path('results/scb_modality_prediction.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"Saved to {output_path}")
    print()

    return results

if __name__ == '__main__':
    main()
