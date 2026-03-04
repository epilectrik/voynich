"""
Composition Grammar Accuracy Test

Compare 4 models for predicting compound MIDDLE category:
  M1: Random baseline (most common category)
  M2: Head-only (first atom's default category)
  M3: Head + dominance override (known injector atoms)
  M4: Full composition grammar (head + modifier + terminal rules)

Ground truth: classify each compound MIDDLE by its PREFIX distribution.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict
import numpy as np
import json

ATOMS = set('kehyinamdtlocpfsgrx')

# Atom default categories from deep dives
ATOM_CAT = {
    'k': 'THERMAL', 'e': 'THERMAL', 'h': 'THERMAL',
    'y': 'THERMAL', 'n': 'THERMAL', 'm': 'THERMAL',
    'a': 'FLOW', 'i': 'FLOW', 't': 'FLOW', 'r': 'FLOW',
    'o': 'STAGING', 'l': 'STAGING', 's': 'STAGING',
    'c': 'MONITORING', 'd': 'MARKING', 'p': 'MARKING', 'f': 'MARKING',
}

# Positional roles from atom_position_preferences.py
HEAD_ATOMS = set('aeo')
MODIFIER_ATOMS = set('pcidfs')
TERMINAL_ATOMS = set('lrhymn')
FREE_ATOMS = set('kt')

# PREFIX -> category
PREFIX_CATEGORY = {
    'qo': 'THERMAL', 'ok': 'THERMAL', 'qok': 'THERMAL',
    'ch': 'MONITORING', 'sh': 'MONITORING', 'cph': 'MONITORING', 'ot': 'MONITORING',
    'da': 'FLOW', 'ar': 'FLOW', 'or': 'FLOW',
    'sa': 'STAGING', 'ol': 'STAGING',
    'op': 'TRANSITION',
}

CATEGORIES = ['THERMAL', 'FLOW', 'STAGING', 'MONITORING', 'MARKING', 'CONTAINMENT', 'OPERATION', 'TRANSITION']

tx = Transcript()
morph = Morphology()

# Build PREFIX distributions per MIDDLE
prefix_by_middle = defaultdict(Counter)
for token in tx.currier_b():
    w = token.word
    if not w.strip() or '*' in w:
        continue
    m = morph.extract(w)
    if not m.middle:
        continue
    pfx = m.prefix if m.prefix else '_NONE_'
    prefix_by_middle[m.middle][pfx] += 1

def classify_middle(mid):
    pfx_counts = prefix_by_middle.get(mid, Counter())
    if not pfx_counts:
        return None
    cat_counts = Counter()
    for pfx, count in pfx_counts.items():
        if pfx in PREFIX_CATEGORY:
            cat_counts[PREFIX_CATEGORY[pfx]] += count
    if not cat_counts:
        return None
    return cat_counts.most_common(1)[0][0]

def get_atom_sequence(middle):
    return [ch for ch in middle if ch in ATOMS]

# Collect all classifiable compound MIDDLEs
compounds = []
category_counts = Counter()

for mid in prefix_by_middle:
    seq = get_atom_sequence(mid)
    if len(seq) < 2:
        continue

    true_cat = classify_middle(mid)
    if not true_cat:
        continue

    token_count = sum(prefix_by_middle[mid].values())
    if token_count < 3:
        continue

    compounds.append({
        'middle': mid,
        'atoms': seq,
        'head': seq[0],
        'terminal': seq[-1],
        'modifiers': seq[1:-1] if len(seq) > 2 else [],
        'true_cat': true_cat,
        'tokens': token_count
    })
    category_counts[true_cat] += 1

print(f"Total classifiable compounds (N>=3): {len(compounds)}")
print(f"Category distribution: {dict(category_counts)}")

# Most common category for baseline
most_common_cat = category_counts.most_common(1)[0][0]
print(f"Most common category: {most_common_cat}")

# MODEL 1: Random baseline (predict most common category)
def model_baseline(comp):
    return most_common_cat

# MODEL 2: Head-only (predict head atom's category)
def model_head_only(comp):
    head = comp['head']
    return ATOM_CAT.get(head, most_common_cat)

# MODEL 3: Head + dominance override
def model_head_dominance(comp):
    head = comp['head']
    all_atoms = comp['atoms']

    # Start with head prediction
    pred = ATOM_CAT.get(head, most_common_cat)

    # Override rules based on known dominant atoms
    # p is the strongest injector - overrides when first
    if all_atoms[0] == 'p':
        return 'MARKING'
    # f as first also pushes MARKING
    if all_atoms[0] == 'f':
        return 'MARKING'
    # c as first pushes MONITORING
    if all_atoms[0] == 'c':
        return 'MONITORING'
    # s as first pushes STAGING
    if all_atoms[0] == 's':
        return 'STAGING'

    return pred

# MODEL 4: Full composition grammar
def model_composition(comp):
    head = comp['head']
    terminal = comp['terminal']
    modifiers = comp['modifiers']
    all_atoms = comp['atoms']

    # Start with head's category
    head_cat = ATOM_CAT.get(head, None)
    terminal_cat = ATOM_CAT.get(terminal, None)

    if not head_cat:
        return most_common_cat

    pred = head_cat

    # Rule 1: If head is a standard HEAD atom, its category dominates
    if head in HEAD_ATOMS:
        pred = head_cat

    # Rule 2: If head is a FREE atom (k, t), use its category
    elif head in FREE_ATOMS:
        pred = head_cat

    # Rule 3: If head is a MODIFIER atom (unusual - modifier in head position)
    # This means the modifier IS the domain setter (c, p, s, etc.)
    elif head in MODIFIER_ATOMS:
        pred = head_cat

    # Rule 4: If head is a TERMINAL atom (unusual - terminal in head position)
    elif head in TERMINAL_ATOMS:
        pred = head_cat

    # Modifier adjustments
    for mod in modifiers:
        # c in middle shifts toward MONITORING
        if mod == 'c' and pred in ('THERMAL', 'FLOW'):
            pred = 'MONITORING'
        # p in middle shifts toward MARKING
        if mod == 'p' and pred != 'MARKING':
            pred = 'MARKING'  # p dominates from any position

    # h-terminal shifts: if terminal is h and head is a modifier, lean MONITORING
    if terminal == 'h' and head in MODIFIER_ATOMS:
        if pred not in ('MARKING',):  # p still overrides
            pred = 'MONITORING'

    return pred

# Run all models
models = {
    'M1_baseline': model_baseline,
    'M2_head_only': model_head_only,
    'M3_head_dominance': model_head_dominance,
    'M4_composition': model_composition,
}

print(f"\n{'='*70}")
print(f"MODEL COMPARISON: COMPOUND CATEGORY PREDICTION")
print(f"{'='*70}")

for name, model_fn in models.items():
    correct = 0
    correct_weighted = 0
    total_tokens = 0

    confusion = defaultdict(Counter)  # true -> predicted -> count

    for comp in compounds:
        pred = model_fn(comp)
        is_correct = pred == comp['true_cat']

        if is_correct:
            correct += 1
            correct_weighted += comp['tokens']

        total_tokens += comp['tokens']
        confusion[comp['true_cat']][pred] += 1

    acc = 100 * correct / len(compounds)
    w_acc = 100 * correct_weighted / total_tokens

    print(f"\n  {name}:")
    print(f"    Type-level accuracy:  {correct}/{len(compounds)} = {acc:.1f}%")
    print(f"    Token-level accuracy: {correct_weighted}/{total_tokens} = {w_acc:.1f}%")

    # Show confusion for this model
    if name in ('M2_head_only', 'M4_composition'):
        print(f"    Confusion matrix (true -> predicted):")
        for true_cat in sorted(confusion.keys()):
            preds = confusion[true_cat]
            total = sum(preds.values())
            parts = ', '.join(f"{p}:{c}" for p, c in sorted(preds.items(), key=lambda x: -x[1]))
            print(f"      {true_cat:<14} (N={total:>3}) -> {parts}")

# Detailed per-compound analysis for M4 misses
print(f"\n{'='*70}")
print(f"MODEL 4 MISSES (for debugging composition rules)")
print(f"{'='*70}")

misses = []
for comp in compounds:
    pred = model_composition(comp)
    if pred != comp['true_cat']:
        misses.append({
            'middle': comp['middle'],
            'atoms': ''.join(comp['atoms']),
            'head': comp['head'],
            'terminal': comp['terminal'],
            'true_cat': comp['true_cat'],
            'pred_cat': pred,
            'tokens': comp['tokens']
        })

misses.sort(key=lambda x: -x['tokens'])
for m in misses[:15]:
    print(f"  {m['middle']:<12} atoms={m['atoms']:<8}  TRUE={m['true_cat']:<12} PRED={m['pred_cat']:<12} "
          f"head={m['head']}({ATOM_CAT.get(m['head'],'?')}) term={m['terminal']}({ATOM_CAT.get(m['terminal'],'?')}) N={m['tokens']}")

# Additional analysis: per-head-atom accuracy for M2 vs M4
print(f"\n{'='*70}")
print(f"PER-HEAD-ATOM ACCURACY (M2 vs M4)")
print(f"{'='*70}")

head_stats = defaultdict(lambda: {'m2_correct': 0, 'm4_correct': 0, 'total': 0, 'tokens': 0})
for comp in compounds:
    h = comp['head']
    head_stats[h]['total'] += 1
    head_stats[h]['tokens'] += comp['tokens']
    if model_head_only(comp) == comp['true_cat']:
        head_stats[h]['m2_correct'] += 1
    if model_composition(comp) == comp['true_cat']:
        head_stats[h]['m4_correct'] += 1

print(f"  {'Head':<6} {'N':>4}  {'M2_acc':>8}  {'M4_acc':>8}  {'Delta':>8}  {'Default_cat':<12}")
for h in sorted(head_stats.keys(), key=lambda x: -head_stats[x]['total']):
    s = head_stats[h]
    if s['total'] < 3:
        continue
    m2_acc = 100 * s['m2_correct'] / s['total']
    m4_acc = 100 * s['m4_correct'] / s['total']
    delta = m4_acc - m2_acc
    print(f"  {h:<6} {s['total']:>4}  {m2_acc:>7.1f}%  {m4_acc:>7.1f}%  {delta:>+7.1f}%  {ATOM_CAT.get(h, '?'):<12}")

# Save results
output_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'composition_grammar_accuracy.json')
os.makedirs(os.path.dirname(output_path), exist_ok=True)

save = {
    'n_compounds': len(compounds),
    'category_distribution': dict(category_counts),
    'most_common_category': most_common_cat,
    'models': {}
}
for name, model_fn in models.items():
    correct = sum(1 for c in compounds if model_fn(c) == c['true_cat'])
    correct_w = sum(c['tokens'] for c in compounds if model_fn(c) == c['true_cat'])
    total_w = sum(c['tokens'] for c in compounds)
    save['models'][name] = {
        'type_accuracy': round(100 * correct / len(compounds), 1),
        'token_accuracy': round(100 * correct_w / total_w, 1),
        'correct': correct,
        'total': len(compounds)
    }

# Convert misses for JSON serialization
save['misses_top15'] = misses[:15]

with open(output_path, 'w') as f:
    json.dump(save, f, indent=2)
print(f"\nResults saved to {output_path}")
