"""
23_layer_class_mapping.py

Map the hierarchical nesting layers to the known 49-class system.
Do specific instruction classes preferentially occupy specific layers?
Is the nesting structure visible through the class lens?
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2_contingency, fisher_exact

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

FL_STAGE_MAP = {
    'ii': ('INITIAL', 0.299), 'i': ('INITIAL', 0.345),
    'in': ('EARLY', 0.421),
    'r': ('MEDIAL', 0.507), 'ar': ('MEDIAL', 0.545),
    'al': ('LATE', 0.606), 'l': ('LATE', 0.618), 'ol': ('LATE', 0.643),
    'o': ('FINAL', 0.751), 'ly': ('FINAL', 0.785), 'am': ('FINAL', 0.802),
    'm': ('TERMINAL', 0.861), 'dy': ('TERMINAL', 0.908),
    'ry': ('TERMINAL', 0.913), 'y': ('TERMINAL', 0.942),
}

tx = Transcript()
morph = Morphology()
MIN_N = 50

class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = class_data['token_to_class']
token_to_role = class_data['token_to_role']

line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Fit GMMs
per_middle_positions = defaultdict(list)
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            per_middle_positions[m.middle].append(idx / (n - 1))

gmm_models = {}
for mid, positions in per_middle_positions.items():
    if len(positions) < MIN_N:
        continue
    X = np.array(positions).reshape(-1, 1)
    gmm = GaussianMixture(n_components=2, random_state=42, n_init=10)
    gmm.fit(X)
    if gmm.means_[0] > gmm.means_[1]:
        gmm_models[mid] = {'model': gmm, 'swap': True}
    else:
        gmm_models[mid] = {'model': gmm, 'swap': False}

# ============================================================
# Build layered gap tokens
# ============================================================
outer_left_tokens = []
outer_right_tokens = []
center_tokens = []

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue

    fl_info = []
    all_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        mode = None
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'

        cls = token_to_class.get(t.word, None)
        role = token_to_role.get(t.word, 'UNKNOWN')
        entry = {'word': t.word, 'idx': idx, 'pos': pos, 'is_fl': is_fl,
                 'mode': mode, 'class': cls, 'role': role}
        all_info.append(entry)
        if is_fl and mode:
            fl_info.append(entry)

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    max_low_idx = max(f['idx'] for f in low_fls)
    min_high_idx = min(f['idx'] for f in high_fls)
    gap = [t for t in all_info if not t['is_fl']
           and t['idx'] > max_low_idx and t['idx'] < min_high_idx]

    if len(gap) < 3:
        continue

    outer_left_tokens.append(gap[0])
    outer_right_tokens.append(gap[-1])
    for t in gap[1:-1]:
        center_tokens.append(t)

print(f"Outer-left: {len(outer_left_tokens)}")
print(f"Outer-right: {len(outer_right_tokens)}")
print(f"Center: {len(center_tokens)}")

# ============================================================
# TEST 1: Class distribution by layer
# ============================================================
print(f"\n{'='*60}")
print("TEST 1: CLASS DISTRIBUTION BY LAYER")
print(f"{'='*60}")

# Get all classes that appear
all_classes = set()
for tokens in [outer_left_tokens, outer_right_tokens, center_tokens]:
    for t in tokens:
        if t['class'] is not None:
            all_classes.add(t['class'])

# Count classes per layer
for label, tokens in [('Outer-left', outer_left_tokens),
                       ('Outer-right', outer_right_tokens),
                       ('Center', center_tokens)]:
    cls_counts = Counter(t['class'] for t in tokens if t['class'] is not None)
    total_classified = sum(cls_counts.values())
    total = len(tokens)
    unclassified = sum(1 for t in tokens if t['class'] is None)
    print(f"\n  {label} (n={total}, classified={total_classified}, unclassified={unclassified}):")
    for cls, count in cls_counts.most_common(15):
        pct = count / total_classified * 100
        print(f"    Class {cls:>3}: {count:>5} ({pct:.1f}%)")

# ============================================================
# TEST 2: Chi-squared: layer x class
# ============================================================
print(f"\n{'='*60}")
print("TEST 2: LAYER x CLASS ASSOCIATION")
print(f"{'='*60}")

# Use classes with at least 10 tokens total
class_totals = Counter()
for tokens in [outer_left_tokens, outer_right_tokens, center_tokens]:
    for t in tokens:
        if t['class'] is not None:
            class_totals[t['class']] += 1

top_classes = [c for c, n in class_totals.most_common() if n >= 10]
print(f"  Classes with n>=10: {len(top_classes)}")

layer_class_table = []
for tokens in [outer_left_tokens, outer_right_tokens, center_tokens]:
    cls_counts = Counter(t['class'] for t in tokens if t['class'] is not None)
    layer_class_table.append([cls_counts.get(c, 0) for c in top_classes])

table = np.array(layer_class_table)
chi2, p_val, dof, _ = chi2_contingency(table)
v = np.sqrt(chi2 / (table.sum() * (min(table.shape) - 1)))
print(f"  chi2={chi2:.1f}, p={p_val:.2e}, Cramer's V={v:.3f}, dof={dof}")

# ============================================================
# TEST 3: Layer-preferring classes
# ============================================================
print(f"\n{'='*60}")
print("TEST 3: LAYER-PREFERRING CLASSES")
print(f"{'='*60}")

# For each class, compute enrichment ratio per layer
# Expected: class_total * layer_total / grand_total
layer_totals = [sum(row) for row in layer_class_table]
grand_total = sum(layer_totals)

print(f"\n  {'Class':>6} {'Total':>6} {'OL obs':>7} {'OL exp':>7} {'OL ratio':>8} "
      f"{'OR obs':>7} {'OR exp':>7} {'OR ratio':>8} "
      f"{'C obs':>7} {'C exp':>7} {'C ratio':>8}  Preferred")
print(f"  {'-'*100}")

layer_preferring = {'outer_left': [], 'outer_right': [], 'center': []}

for j, cls in enumerate(top_classes):
    col_total = sum(table[i][j] for i in range(3))
    if col_total < 15:
        continue

    ratios = []
    obs_vals = []
    exp_vals = []
    for i in range(3):
        observed = table[i][j]
        expected = col_total * layer_totals[i] / grand_total
        ratio = observed / expected if expected > 0 else 0
        ratios.append(ratio)
        obs_vals.append(observed)
        exp_vals.append(expected)

    # Which layer is most enriched?
    max_layer = np.argmax(ratios)
    layer_names = ['OL', 'OR', 'C']
    layer_keys = ['outer_left', 'outer_right', 'center']

    # Only report if enrichment > 1.3x
    if max(ratios) > 1.3:
        preferred = layer_names[max_layer]
        layer_preferring[layer_keys[max_layer]].append((cls, ratios[max_layer]))
    else:
        preferred = '-'

    print(f"  {cls:>6} {col_total:>6} "
          f"{obs_vals[0]:>7} {exp_vals[0]:>7.1f} {ratios[0]:>8.2f} "
          f"{obs_vals[1]:>7} {exp_vals[1]:>7.1f} {ratios[1]:>8.2f} "
          f"{obs_vals[2]:>7} {exp_vals[2]:>7.1f} {ratios[2]:>8.2f}  {preferred}")

print(f"\n  Layer-preferring classes:")
for layer, classes in layer_preferring.items():
    if classes:
        sorted_cls = sorted(classes, key=lambda x: -x[1])
        cls_str = ', '.join(f"C{c}({r:.2f}x)" for c, r in sorted_cls[:8])
        print(f"    {layer}: {cls_str}")

# ============================================================
# TEST 4: Do outer-left classes differ from outer-right?
# ============================================================
print(f"\n{'='*60}")
print("TEST 4: OUTER-LEFT vs OUTER-RIGHT CLASS PROFILES")
print(f"{'='*60}")

ol_cls = Counter(t['class'] for t in outer_left_tokens if t['class'] is not None)
or_cls = Counter(t['class'] for t in outer_right_tokens if t['class'] is not None)

# Find classes that differ most
shared_classes = set(ol_cls.keys()) | set(or_cls.keys())
ol_total = sum(ol_cls.values())
or_total = sum(or_cls.values())

asymmetric = []
for cls in shared_classes:
    ol_pct = ol_cls.get(cls, 0) / ol_total
    or_pct = or_cls.get(cls, 0) / or_total
    diff = ol_pct - or_pct
    if ol_cls.get(cls, 0) + or_cls.get(cls, 0) >= 10:
        asymmetric.append((cls, ol_pct, or_pct, diff))

asymmetric.sort(key=lambda x: -abs(x[3]))
print(f"\n  Most asymmetric classes (OL vs OR):")
print(f"  {'Class':>6} {'OL%':>7} {'OR%':>7} {'Diff':>7}")
for cls, ol_p, or_p, diff in asymmetric[:15]:
    marker = '<--OL' if diff > 0.02 else ('OR-->' if diff < -0.02 else '')
    print(f"  {cls:>6} {ol_p*100:>7.1f} {or_p*100:>7.1f} {diff*100:>+7.1f}  {marker}")

# ============================================================
# TEST 5: Kernel structure by layer
# ============================================================
print(f"\n{'='*60}")
print("TEST 5: KERNEL STRUCTURE BY LAYER")
print(f"{'='*60}")

# Check how kernel-related roles map to layers
# kernel roles: ENERGY_OPERATOR (k-type), CORE_CONTROL, FREQUENT_OPERATOR
for label, tokens in [('Outer-left', outer_left_tokens),
                       ('Outer-right', outer_right_tokens),
                       ('Center', center_tokens)]:
    total = len(tokens)
    # Check for specific important words
    word_counts = Counter(t['word'] for t in tokens)
    top10 = word_counts.most_common(10)
    print(f"\n  {label} top words:")
    for w, c in top10:
        cls = token_to_class.get(w, '?')
        role = token_to_role.get(w, '?')
        print(f"    {w:>12} ({c:>3}, {c/total*100:.1f}%) class={cls} role={role}")

# ============================================================
# TEST 6: Unclassified token analysis
# ============================================================
print(f"\n{'='*60}")
print("TEST 6: UNCLASSIFIED TOKEN ANALYSIS")
print(f"{'='*60}")

for label, tokens in [('Outer-left', outer_left_tokens),
                       ('Outer-right', outer_right_tokens),
                       ('Center', center_tokens)]:
    unclassified = [t for t in tokens if t['class'] is None]
    total = len(tokens)
    pct = len(unclassified) / total * 100
    words = Counter(t['word'] for t in unclassified)
    top5 = words.most_common(5)
    top_str = ', '.join(f"{w}({c})" for w, c in top5)
    print(f"  {label:>12}: {len(unclassified)}/{total} ({pct:.1f}%) unclassified")
    print(f"               Top: {top_str}")

# ============================================================
# TEST 7: Does class predict layer? (reverse direction)
# ============================================================
print(f"\n{'='*60}")
print("TEST 7: CLASS-CONDITIONAL LAYER DISTRIBUTION")
print(f"{'='*60}")

# For each common class, where do its tokens appear?
print(f"\n  {'Class':>6} {'Role':>20} {'OL%':>6} {'OR%':>6} {'C%':>6} {'n':>5}  Pattern")
print(f"  {'-'*75}")

for cls in sorted(top_classes):
    if class_totals[cls] < 15:
        continue

    ol_n = sum(1 for t in outer_left_tokens if t['class'] == cls)
    or_n = sum(1 for t in outer_right_tokens if t['class'] == cls)
    c_n = sum(1 for t in center_tokens if t['class'] == cls)
    total = ol_n + or_n + c_n
    if total == 0:
        continue

    ol_pct = ol_n / total * 100
    or_pct = or_n / total * 100
    c_pct = c_n / total * 100

    # Expected: OL ~21%, OR ~21%, C ~58% (based on token counts)
    # Classify pattern
    if ol_pct > 30:
        pattern = "OUTER-LEFT biased"
    elif or_pct > 30:
        pattern = "OUTER-RIGHT biased"
    elif c_pct > 70:
        pattern = "CENTER concentrated"
    elif ol_pct + or_pct > 50:
        pattern = "OUTER biased"
    else:
        pattern = "uniform"

    # Get representative role
    role_for_cls = None
    for t in outer_left_tokens + outer_right_tokens + center_tokens:
        if t['class'] == cls:
            role_for_cls = t['role']
            break

    print(f"  {cls:>6} {role_for_cls:>20} {ol_pct:>6.1f} {or_pct:>6.1f} {c_pct:>6.1f} {total:>5}  {pattern}")

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*60}")
print("VERDICT")
print(f"{'='*60}")

# Is class distribution significantly different across layers?
if p_val < 0.01 and v > 0.10:
    class_stratified = True
    print(f"  Class x Layer: SIGNIFICANT (V={v:.3f}, p={p_val:.2e})")
else:
    class_stratified = False
    print(f"  Class x Layer: NOT SIGNIFICANT (V={v:.3f}, p={p_val:.2e})")

# Are there clearly layer-preferring classes?
n_preferring = sum(len(v) for v in layer_preferring.values())
if n_preferring >= 5:
    has_preferences = True
    print(f"  Layer-preferring classes: {n_preferring}")
else:
    has_preferences = False
    print(f"  Few layer-preferring classes: {n_preferring}")

# Do outer layers differ from each other?
if asymmetric and abs(asymmetric[0][3]) > 0.03:
    outer_asymmetry = True
    print(f"  Outer asymmetry: YES (max diff={asymmetric[0][3]*100:.1f}pp)")
else:
    outer_asymmetry = False
    print(f"  Outer asymmetry: NO")

if class_stratified and has_preferences and outer_asymmetry:
    verdict = "CLASS_STRATIFIED_NESTING"
    explanation = "Specific classes preferentially occupy specific nesting layers, with L/R asymmetry"
elif class_stratified and has_preferences:
    verdict = "CLASS_STRATIFIED"
    explanation = "Classes show layer preferences but outer layers are symmetric"
elif class_stratified:
    verdict = "WEAK_STRATIFICATION"
    explanation = "Statistical association but no clear class-to-layer mapping"
else:
    verdict = "NO_CLASS_STRATIFICATION"
    explanation = "Classes distribute uniformly across layers"

print(f"\n  VERDICT: {verdict}")
print(f"  {explanation}")

# Save
result = {
    'n_outer_left': len(outer_left_tokens),
    'n_outer_right': len(outer_right_tokens),
    'n_center': len(center_tokens),
    'layer_class_cramers_v': round(float(v), 3),
    'layer_class_p': float(p_val),
    'n_layer_preferring_classes': n_preferring,
    'outer_max_asymmetry': round(float(abs(asymmetric[0][3])) if asymmetric else 0, 3),
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "23_layer_class_mapping.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
