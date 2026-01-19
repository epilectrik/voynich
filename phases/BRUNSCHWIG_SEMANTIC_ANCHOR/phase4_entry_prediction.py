#!/usr/bin/env python3
"""
PHASE 4: ENTRY-LEVEL SEMANTIC PREDICTION

Question: Can we predict an A entry's product affinity from its structure?

Method:
1. Load A entries and their folio-level product classifications
2. Extract PREFIX + MIDDLE decomposition per entry
3. Score each entry against product-discriminating MIDDLEs
4. Test prediction accuracy against actual folio classification

Success criterion: >60% accuracy (above 25% baseline for 4 classes)
"""

import csv
import json
from collections import defaultdict, Counter
import random

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

def decompose_token(token):
    """Extract MIDDLE from token."""
    if not token or len(token) < 2:
        return ('', token, '')

    prefix = ''
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    return (prefix, token, '')

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("PHASE 4: ENTRY-LEVEL SEMANTIC PREDICTION")
print("=" * 70)
print()

# Load A folio classifications
with open('results/exclusive_middle_backprop.json', 'r') as f:
    backprop_data = json.load(f)

a_folio_classifications = backprop_data['a_folio_classifications']
print(f"Loaded {len(a_folio_classifications)} A folio classifications")

# Load discriminating MIDDLEs from Phase 2
with open('results/phase2_discriminating_middles.json', 'r') as f:
    phase2_data = json.load(f)

discriminating_middles = phase2_data['discriminating_middles']
print(f"Loaded discriminating MIDDLEs for {len(discriminating_middles)} products")

# Build product scoring sets (top discriminators)
product_discriminators = {}
for product, middles in discriminating_middles.items():
    product_discriminators[product] = set(middles)

# Load all A entries
a_entries = []

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue

        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        language = row.get('language', '').strip()

        if language != 'A':
            continue

        if not word or word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        if folio not in a_folio_classifications:
            continue

        prefix, middle, _ = decompose_token(word)

        a_entries.append({
            'token': word,
            'folio': folio,
            'prefix': prefix,
            'middle': middle,
            'true_product': a_folio_classifications[folio]
        })

print(f"Loaded {len(a_entries)} A entries from classified folios")
print()

# ============================================================
# ENTRY-LEVEL PREDICTION
# ============================================================

print("=" * 70)
print("PREDICTING PRODUCT TYPE FROM ENTRY STRUCTURE")
print("=" * 70)
print()

def predict_product(entry):
    """
    Predict product type based on MIDDLE membership in discriminating sets.
    Returns the product with highest score, or None if no signal.
    """
    middle = entry['middle']

    scores = {}
    for product, disc_set in product_discriminators.items():
        # Score based on MIDDLE match
        if middle in disc_set:
            scores[product] = 1.0
        else:
            scores[product] = 0.0

    if not scores or max(scores.values()) == 0:
        return None

    # Return product with highest score (tie-break randomly)
    max_score = max(scores.values())
    candidates = [p for p, s in scores.items() if s == max_score]
    return random.choice(candidates)

# Run prediction
predictions = []
for entry in a_entries:
    pred = predict_product(entry)
    predictions.append({
        'entry': entry,
        'predicted': pred,
        'correct': pred == entry['true_product'] if pred else None
    })

# Count results
has_prediction = [p for p in predictions if p['predicted'] is not None]
correct = [p for p in has_prediction if p['correct']]

print(f"Entries with prediction: {len(has_prediction)}/{len(predictions)} = {100*len(has_prediction)/len(predictions):.1f}%")

if has_prediction:
    accuracy = len(correct) / len(has_prediction)
    print(f"Correct predictions: {len(correct)}/{len(has_prediction)} = {100*accuracy:.1f}%")
else:
    accuracy = 0

print()

# ============================================================
# BREAKDOWN BY PRODUCT TYPE
# ============================================================

print("=" * 70)
print("BREAKDOWN BY PRODUCT TYPE")
print("=" * 70)
print()

product_stats = defaultdict(lambda: {'total': 0, 'has_pred': 0, 'correct': 0})

for p in predictions:
    true_prod = p['entry']['true_product']
    product_stats[true_prod]['total'] += 1
    if p['predicted'] is not None:
        product_stats[true_prod]['has_pred'] += 1
        if p['correct']:
            product_stats[true_prod]['correct'] += 1

print(f"{'Product':<20} {'Total':<10} {'Has Pred':<10} {'Correct':<10} {'Accuracy':<10}")
print("-" * 60)

for product in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']:
    stats = product_stats[product]
    if stats['has_pred'] > 0:
        acc = 100 * stats['correct'] / stats['has_pred']
    else:
        acc = 0
    print(f"{product:<20} {stats['total']:<10} {stats['has_pred']:<10} {stats['correct']:<10} {acc:.1f}%")

# ============================================================
# CONFUSION MATRIX
# ============================================================

print()
print("=" * 70)
print("CONFUSION MATRIX (rows=true, cols=predicted)")
print("=" * 70)
print()

products = ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']
confusion = defaultdict(Counter)

for p in predictions:
    if p['predicted'] is not None:
        confusion[p['entry']['true_product']][p['predicted']] += 1

# Header
print(f"{'True/Pred':<20}", end='')
for prod in products:
    print(f"{prod[:6]:<10}", end='')
print()
print("-" * 60)

for true_prod in products:
    print(f"{true_prod:<20}", end='')
    for pred_prod in products:
        print(f"{confusion[true_prod][pred_prod]:<10}", end='')
    print()

# ============================================================
# ALTERNATIVE: FOLIO-LEVEL PREDICTION
# ============================================================

print()
print("=" * 70)
print("ALTERNATIVE: FOLIO-LEVEL MAJORITY VOTE")
print("=" * 70)
print()

# Aggregate predictions at folio level
folio_predictions = defaultdict(Counter)

for p in predictions:
    if p['predicted'] is not None:
        folio_predictions[p['entry']['folio']][p['predicted']] += 1

folio_correct = 0
folio_total = 0

for folio, pred_counts in folio_predictions.items():
    if pred_counts:
        predicted = pred_counts.most_common(1)[0][0]
        true_prod = a_folio_classifications[folio]
        if predicted == true_prod:
            folio_correct += 1
        folio_total += 1

if folio_total > 0:
    folio_accuracy = 100 * folio_correct / folio_total
    print(f"Folio-level accuracy: {folio_correct}/{folio_total} = {folio_accuracy:.1f}%")
else:
    folio_accuracy = 0
    print("No folio-level predictions available")

# ============================================================
# SUCCESS CRITERION CHECK
# ============================================================

print()
print("=" * 70)
print("SUCCESS CRITERION CHECK")
print("=" * 70)
print()

THRESHOLD = 60.0
BASELINE = 25.0

entry_accuracy = 100 * accuracy if accuracy else 0
print(f"Entry-level accuracy: {entry_accuracy:.1f}% (threshold: {THRESHOLD}%, baseline: {BASELINE}%)")
print(f"Folio-level accuracy: {folio_accuracy:.1f}%")

status = "PASS" if (entry_accuracy >= THRESHOLD or folio_accuracy >= THRESHOLD) else "FAIL"
print(f"\nOverall Status: {status}")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    'phase': 'phase4_entry_prediction',
    'question': 'Can we predict product type from entry structure?',
    'method': 'MIDDLE match against product-discriminating MIDDLEs',
    'summary': {
        'total_entries': len(predictions),
        'entries_with_prediction': len(has_prediction),
        'correct_predictions': len(correct),
        'entry_accuracy': accuracy,
        'folio_accuracy': folio_accuracy / 100 if folio_total > 0 else 0,
        'baseline': BASELINE / 100,
        'threshold': THRESHOLD / 100
    },
    'by_product': {
        product: {
            'total': product_stats[product]['total'],
            'has_prediction': product_stats[product]['has_pred'],
            'correct': product_stats[product]['correct'],
            'accuracy': product_stats[product]['correct'] / product_stats[product]['has_pred']
                        if product_stats[product]['has_pred'] > 0 else 0
        }
        for product in products
    },
    'confusion_matrix': {
        true_prod: dict(confusion[true_prod])
        for true_prod in products
    },
    'status': status
}

with open('results/phase4_entry_prediction.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to results/phase4_entry_prediction.json")
