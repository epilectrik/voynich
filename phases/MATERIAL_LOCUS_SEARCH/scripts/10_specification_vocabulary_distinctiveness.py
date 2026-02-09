#!/usr/bin/env python3
"""
Test 10: Specification Vocabulary Distinctiveness by Section

Question: Is the specification vocabulary (early body) more section-discriminative
than execution vocabulary (late body)?

Background: If materials are encoded, the specification (early) vocabulary should
be more section-specific than execution (late) vocabulary, because early positions
contain specification/setup content while late positions contain execution content.

Method:
1. Load all Currier B tokens (H track, no labels, no uncertain).
2. Build paragraphs using par_initial boundaries; keep paragraphs with 10+ tokens.
3. For each paragraph, split into EARLY (first 33% of tokens) and LATE (last 33%).
4. Extract MIDDLE vocabulary for each partition.
5. Build presence/absence feature vectors from common MIDDLEs (appearing in 20+ paragraphs).
6. Classify section using leave-one-out cross-validation (KNN k=5 and NearestCentroid).
7. Compute Cramer's V for MIDDLE x section association in early vs late positions.
8. Compare early vs late section discriminative power.

Pass criteria: Early-body accuracy > late-body by >10 percentage points
Fail criteria: Equal -- specification gradient is operational (rarity), not material
"""

import sys
import json
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# ============================================================
# CONSTANTS
# ============================================================
RESULTS_DIR = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/results')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = RESULTS_DIR / 'specification_vocabulary_distinctiveness.json'

MIN_PARAGRAPH_TOKENS = 10
COMMON_MIDDLE_THRESHOLD = 20  # MIDDLE must appear in 20+ paragraphs
EARLY_FRACTION = 0.33
LATE_FRACTION = 0.33
np.random.seed(42)


def to_native(obj):
    """Convert numpy types to native Python for JSON serialization."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def clean_for_json(obj):
    """Recursively clean numpy types for JSON."""
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(v) for v in obj]
    else:
        return to_native(obj)


# ============================================================
# STEP 1: Load Currier B tokens and build paragraphs
# ============================================================
print("Loading Currier B tokens...")
tx = Transcript()
morph = Morphology()

# Collect all B tokens in file order (folio/line/position order)
all_tokens = []
for t in tx.currier_b():
    m = morph.extract(t.word)
    entry = {
        'word': t.word,
        'folio': t.folio,
        'line': t.line,
        'section': t.section,
        'middle': m.middle,
        'par_initial': t.par_initial,
    }
    all_tokens.append(entry)

print(f"Total Currier B tokens: {len(all_tokens)}")

# Build paragraphs using par_initial boundaries
paragraphs = []
current_par = None
par_num_by_folio = defaultdict(int)

for t in all_tokens:
    folio = t['folio']
    if t['par_initial']:
        # Start new paragraph
        par_num_by_folio[folio] += 1
        current_par = {
            'folio': folio,
            'section': t['section'],
            'par_num': par_num_by_folio[folio],
            'tokens': [],
        }
        paragraphs.append(current_par)

    if current_par is not None and current_par['folio'] == folio:
        current_par['tokens'].append(t)
    elif current_par is None or current_par['folio'] != folio:
        # Tokens before first par_initial in a new folio: create implicit paragraph
        par_num_by_folio[folio] += 1
        current_par = {
            'folio': folio,
            'section': t['section'],
            'par_num': par_num_by_folio[folio],
            'tokens': [t],
        }
        paragraphs.append(current_par)

total_paragraphs_raw = len(paragraphs)
print(f"Total paragraphs found: {total_paragraphs_raw}")

# Filter: minimum token count
paragraphs = [p for p in paragraphs if len(p['tokens']) >= MIN_PARAGRAPH_TOKENS]
print(f"Paragraphs with >= {MIN_PARAGRAPH_TOKENS} tokens: {len(paragraphs)}")


# ============================================================
# STEP 2: Split each paragraph into EARLY and LATE partitions
# ============================================================
print("\nSplitting paragraphs into EARLY (first 33%) and LATE (last 33%)...")

for p in paragraphs:
    n = len(p['tokens'])
    early_count = max(1, int(n * EARLY_FRACTION))
    late_count = max(1, int(n * LATE_FRACTION))

    early_tokens = p['tokens'][:early_count]
    late_tokens = p['tokens'][-late_count:]

    # Extract MIDDLE sets
    p['early_middles'] = set()
    p['early_middle_list'] = []
    for t in early_tokens:
        if t['middle'] and t['middle'] != '_EMPTY_':
            p['early_middles'].add(t['middle'])
            p['early_middle_list'].append(t['middle'])

    p['late_middles'] = set()
    p['late_middle_list'] = []
    for t in late_tokens:
        if t['middle'] and t['middle'] != '_EMPTY_':
            p['late_middles'].add(t['middle'])
            p['late_middle_list'].append(t['middle'])

    p['early_count'] = early_count
    p['late_count'] = late_count

# Report partition sizes
early_sizes = [p['early_count'] for p in paragraphs]
late_sizes = [p['late_count'] for p in paragraphs]
print(f"EARLY partition sizes: mean={np.mean(early_sizes):.1f}, "
      f"min={min(early_sizes)}, max={max(early_sizes)}")
print(f"LATE partition sizes:  mean={np.mean(late_sizes):.1f}, "
      f"min={min(late_sizes)}, max={max(late_sizes)}")

# Collect sections
sections = sorted(set(p['section'] for p in paragraphs))
n_sections = len(sections)
section_to_idx = {s: i for i, s in enumerate(sections)}

print(f"\nSections represented: {sections} ({n_sections} sections)")
section_counts = Counter(p['section'] for p in paragraphs)
for s in sections:
    print(f"  {s}: {section_counts[s]} paragraphs")

chance_level = 1.0 / n_sections
majority_section = section_counts.most_common(1)[0][0]
majority_fraction = section_counts[majority_section] / len(paragraphs)
print(f"Chance level (1/n_sections): {chance_level:.3f}")
print(f"Majority class baseline ({majority_section}): {majority_fraction:.3f}")


# ============================================================
# STEP 3: Build common MIDDLE vocabulary and feature vectors
# ============================================================
print("\nBuilding feature vectors...")

# Find MIDDLEs that appear in 20+ paragraphs (across ALL positions)
all_middle_par_count = Counter()
for p in paragraphs:
    all_middles_in_par = set()
    for t in p['tokens']:
        if t['middle'] and t['middle'] != '_EMPTY_':
            all_middles_in_par.add(t['middle'])
    for m in all_middles_in_par:
        all_middle_par_count[m] += 1

common_middles = sorted([m for m, c in all_middle_par_count.items()
                         if c >= COMMON_MIDDLE_THRESHOLD])
print(f"Total unique MIDDLEs across all paragraphs: {len(all_middle_par_count)}")
print(f"Common MIDDLEs (in {COMMON_MIDDLE_THRESHOLD}+ paragraphs): {len(common_middles)}")

mid_to_idx = {m: i for i, m in enumerate(common_middles)}
n_features = len(common_middles)

# Build feature matrices: presence/absence of each common MIDDLE
X_early = np.zeros((len(paragraphs), n_features), dtype=np.float64)
X_late = np.zeros((len(paragraphs), n_features), dtype=np.float64)

for i, p in enumerate(paragraphs):
    for m in p['early_middles']:
        if m in mid_to_idx:
            X_early[i, mid_to_idx[m]] = 1.0
    for m in p['late_middles']:
        if m in mid_to_idx:
            X_late[i, mid_to_idx[m]] = 1.0

# Labels
y = np.array([section_to_idx[p['section']] for p in paragraphs])

print(f"Feature matrix shape: ({len(paragraphs)}, {n_features})")
print(f"EARLY non-zero entries: {int(X_early.sum())} "
      f"({X_early.sum() / X_early.size * 100:.1f}% density)")
print(f"LATE non-zero entries: {int(X_late.sum())} "
      f"({X_late.sum() / X_late.size * 100:.1f}% density)")


# ============================================================
# STEP 4: Leave-one-out cross-validation classification
# ============================================================
print("\nRunning leave-one-out classification...")

from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from sklearn.model_selection import LeaveOneOut

loo = LeaveOneOut()


def loo_accuracy(X, y_labels, clf_class, **clf_kwargs):
    """Compute LOO-CV accuracy for a classifier."""
    correct = 0
    total = 0
    predictions = []

    for train_idx, test_idx in loo.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y_labels[train_idx], y_labels[test_idx]

        clf = clf_class(**clf_kwargs)
        try:
            clf.fit(X_train, y_train)
            pred = clf.predict(X_test)[0]
        except Exception:
            # If classifier fails, predict majority class
            pred = Counter(y_train.tolist()).most_common(1)[0][0]

        predictions.append(pred)
        if pred == y_test[0]:
            correct += 1
        total += 1

    return correct / total if total > 0 else 0.0, predictions


# EARLY partition classifiers
print("  KNN(k=5) on EARLY MIDDLEs...")
acc_early_knn, preds_early_knn = loo_accuracy(
    X_early, y, KNeighborsClassifier, n_neighbors=5)
print(f"    Accuracy: {acc_early_knn:.3f}")

print("  NearestCentroid on EARLY MIDDLEs...")
acc_early_nc, preds_early_nc = loo_accuracy(X_early, y, NearestCentroid)
print(f"    Accuracy: {acc_early_nc:.3f}")

# LATE partition classifiers
print("  KNN(k=5) on LATE MIDDLEs...")
acc_late_knn, preds_late_knn = loo_accuracy(
    X_late, y, KNeighborsClassifier, n_neighbors=5)
print(f"    Accuracy: {acc_late_knn:.3f}")

print("  NearestCentroid on LATE MIDDLEs...")
acc_late_nc, preds_late_nc = loo_accuracy(X_late, y, NearestCentroid)
print(f"    Accuracy: {acc_late_nc:.3f}")

# Best for each partition
best_early_acc = max(acc_early_knn, acc_early_nc)
best_early_method = 'KNN_k5' if acc_early_knn >= acc_early_nc else 'NearestCentroid'
best_late_acc = max(acc_late_knn, acc_late_nc)
best_late_method = 'KNN_k5' if acc_late_knn >= acc_late_nc else 'NearestCentroid'

early_late_diff = best_early_acc - best_late_acc

print(f"\nBest EARLY accuracy: {best_early_acc:.3f} ({best_early_method})")
print(f"Best LATE accuracy:  {best_late_acc:.3f} ({best_late_method})")
print(f"EARLY - LATE difference: {early_late_diff:+.3f} ({early_late_diff*100:+.1f} pp)")
print(f"Chance level: {chance_level:.3f}")
print(f"Majority baseline: {majority_fraction:.3f}")


# ============================================================
# STEP 5: Per-section accuracy breakdown
# ============================================================
print("\n=== Per-Section Accuracy Breakdown ===")

best_early_preds = preds_early_knn if best_early_method == 'KNN_k5' else preds_early_nc
best_late_preds = preds_late_knn if best_late_method == 'KNN_k5' else preds_late_nc

per_section_early = {}
per_section_late = {}
for s in sections:
    s_idx = section_to_idx[s]
    mask = y == s_idx
    total_s = int(mask.sum())

    early_correct = sum(1 for i in range(len(y))
                        if mask[i] and best_early_preds[i] == s_idx)
    late_correct = sum(1 for i in range(len(y))
                       if mask[i] and best_late_preds[i] == s_idx)

    early_acc = early_correct / total_s if total_s > 0 else 0.0
    late_acc = late_correct / total_s if total_s > 0 else 0.0

    per_section_early[s] = {
        'n': total_s, 'correct': early_correct,
        'accuracy': round(early_acc, 3)
    }
    per_section_late[s] = {
        'n': total_s, 'correct': late_correct,
        'accuracy': round(late_acc, 3)
    }
    diff = early_acc - late_acc
    print(f"  {s}: n={total_s}, EARLY={early_acc:.3f}, LATE={late_acc:.3f}, "
          f"diff={diff:+.3f}")


# ============================================================
# STEP 6: Cramer's V analysis -- MIDDLE x section in early vs late
# ============================================================
print("\n=== Cramer's V: MIDDLE x Section Association ===")

from scipy.stats import chi2_contingency

def cramers_v(contingency_table):
    """Compute Cramer's V from a contingency table."""
    chi2, p_val, dof, expected = chi2_contingency(contingency_table)
    n = contingency_table.sum()
    r, k = contingency_table.shape
    v = np.sqrt(chi2 / (n * (min(r, k) - 1))) if n > 0 and min(r, k) > 1 else 0.0
    return float(v), float(chi2), float(p_val)


# For each common MIDDLE, build contingency table: section x (present/absent)
# separately for EARLY and LATE
early_cramers = {}
late_cramers = {}

for m in common_middles:
    m_idx = mid_to_idx[m]

    # Count presence per section in EARLY
    early_contingency = np.zeros((2, n_sections), dtype=int)
    late_contingency = np.zeros((2, n_sections), dtype=int)

    for i, p in enumerate(paragraphs):
        s_idx = section_to_idx[p['section']]
        # EARLY
        if X_early[i, m_idx] > 0:
            early_contingency[0, s_idx] += 1
        else:
            early_contingency[1, s_idx] += 1
        # LATE
        if X_late[i, m_idx] > 0:
            late_contingency[0, s_idx] += 1
        else:
            late_contingency[1, s_idx] += 1

    early_present = early_contingency[0].sum()
    late_present = late_contingency[0].sum()

    # Only compute if MIDDLE appears in at least 5 paragraphs for that partition
    if early_present >= 5:
        try:
            v, chi2, p_val = cramers_v(early_contingency)
            early_cramers[m] = {
                'cramers_v': round(v, 4), 'chi2': round(chi2, 3),
                'p_value': p_val, 'n_present': int(early_present)
            }
        except ValueError:
            pass

    if late_present >= 5:
        try:
            v, chi2, p_val = cramers_v(late_contingency)
            late_cramers[m] = {
                'cramers_v': round(v, 4), 'chi2': round(chi2, 3),
                'p_value': p_val, 'n_present': int(late_present)
            }
        except ValueError:
            pass

# Compute mean Cramer's V for early vs late
early_v_values = [r['cramers_v'] for r in early_cramers.values()]
late_v_values = [r['cramers_v'] for r in late_cramers.values()]

mean_early_v = float(np.mean(early_v_values)) if early_v_values else 0.0
mean_late_v = float(np.mean(late_v_values)) if late_v_values else 0.0
median_early_v = float(np.median(early_v_values)) if early_v_values else 0.0
median_late_v = float(np.median(late_v_values)) if late_v_values else 0.0

# Significant MIDDLEs (p < 0.05) counts
early_sig = sum(1 for r in early_cramers.values() if r['p_value'] < 0.05)
late_sig = sum(1 for r in late_cramers.values() if r['p_value'] < 0.05)

print(f"MIDDLEs tested: EARLY={len(early_cramers)}, LATE={len(late_cramers)}")
print(f"Mean Cramer's V: EARLY={mean_early_v:.4f}, LATE={mean_late_v:.4f}")
print(f"Median Cramer's V: EARLY={median_early_v:.4f}, LATE={median_late_v:.4f}")
print(f"Significant (p<0.05): EARLY={early_sig}/{len(early_cramers)}, "
      f"LATE={late_sig}/{len(late_cramers)}")

# Compare paired Cramer's V for MIDDLEs that appear in both
shared_middles = set(early_cramers.keys()) & set(late_cramers.keys())
if shared_middles:
    paired_early_v = [early_cramers[m]['cramers_v'] for m in shared_middles]
    paired_late_v = [late_cramers[m]['cramers_v'] for m in shared_middles]
    paired_diff = [e - l for e, l in zip(paired_early_v, paired_late_v)]

    mean_paired_diff = float(np.mean(paired_diff))
    early_wins = sum(1 for d in paired_diff if d > 0)
    late_wins = sum(1 for d in paired_diff if d < 0)
    ties = sum(1 for d in paired_diff if d == 0)

    # Wilcoxon signed-rank test for paired comparison
    from scipy.stats import wilcoxon
    try:
        w_stat, w_p = wilcoxon(paired_early_v, paired_late_v)
        w_stat = float(w_stat)
        w_p = float(w_p)
    except ValueError:
        w_stat, w_p = 0.0, 1.0

    print(f"\nPaired Cramer's V comparison ({len(shared_middles)} shared MIDDLEs):")
    print(f"  Mean paired difference (early - late): {mean_paired_diff:+.4f}")
    print(f"  EARLY higher: {early_wins}, LATE higher: {late_wins}, ties: {ties}")
    print(f"  Wilcoxon signed-rank: W={w_stat:.1f}, p={w_p:.6f}")
else:
    mean_paired_diff = 0.0
    w_stat, w_p = 0.0, 1.0
    early_wins, late_wins, ties = 0, 0, 0
    print("\nNo shared MIDDLEs for paired comparison.")

# Top 10 most section-discriminative MIDDLEs in EARLY
early_sorted = sorted(early_cramers.items(),
                       key=lambda x: x[1]['cramers_v'], reverse=True)
print("\nTop 10 most section-discriminative MIDDLEs in EARLY:")
for m, r in early_sorted[:10]:
    sig = '*' if r['p_value'] < 0.05 else ''
    late_v = late_cramers[m]['cramers_v'] if m in late_cramers else 'N/A'
    print(f"  {m:15s} V={r['cramers_v']:.4f} (late V={late_v}) "
          f"n={r['n_present']} {sig}")


# ============================================================
# STEP 7: Permutation test for accuracy difference
# ============================================================
print("\n=== Permutation Test: Is EARLY > LATE statistically significant? ===")

# Permute early/late assignment within each paragraph to test if
# the difference is real. We shuffle which tokens are "early" vs "late"
N_PERM = 200

observed_diff = best_early_acc - best_late_acc
perm_diffs = []

# Use the best classifier type for the permutation test
# For speed, use NearestCentroid
print(f"Running {N_PERM} permutations (NearestCentroid)...")

for perm_i in range(N_PERM):
    # For each paragraph, randomly assign tokens to early/late
    X_perm_early = np.zeros((len(paragraphs), n_features), dtype=np.float64)
    X_perm_late = np.zeros((len(paragraphs), n_features), dtype=np.float64)

    for i, p in enumerate(paragraphs):
        n = len(p['tokens'])
        early_count = max(1, int(n * EARLY_FRACTION))
        late_count = max(1, int(n * LATE_FRACTION))

        # Shuffle tokens and take first early_count and last late_count
        shuffled_indices = np.random.permutation(n)
        perm_early_tokens = [p['tokens'][j] for j in shuffled_indices[:early_count]]
        perm_late_tokens = [p['tokens'][j] for j in shuffled_indices[-late_count:]]

        for t in perm_early_tokens:
            if t['middle'] and t['middle'] != '_EMPTY_' and t['middle'] in mid_to_idx:
                X_perm_early[i, mid_to_idx[t['middle']]] = 1.0
        for t in perm_late_tokens:
            if t['middle'] and t['middle'] != '_EMPTY_' and t['middle'] in mid_to_idx:
                X_perm_late[i, mid_to_idx[t['middle']]] = 1.0

    # LOO with NearestCentroid for speed
    perm_early_correct = 0
    perm_late_correct = 0
    for train_idx, test_idx in loo.split(X_perm_early):
        # EARLY
        clf_e = NearestCentroid()
        try:
            clf_e.fit(X_perm_early[train_idx], y[train_idx])
            pred_e = clf_e.predict(X_perm_early[test_idx])[0]
        except Exception:
            pred_e = Counter(y[train_idx].tolist()).most_common(1)[0][0]
        if pred_e == y[test_idx][0]:
            perm_early_correct += 1

        # LATE
        clf_l = NearestCentroid()
        try:
            clf_l.fit(X_perm_late[train_idx], y[train_idx])
            pred_l = clf_l.predict(X_perm_late[test_idx])[0]
        except Exception:
            pred_l = Counter(y[train_idx].tolist()).most_common(1)[0][0]
        if pred_l == y[test_idx][0]:
            perm_late_correct += 1

    perm_early_acc = perm_early_correct / len(y)
    perm_late_acc = perm_late_correct / len(y)
    perm_diffs.append(perm_early_acc - perm_late_acc)

    if (perm_i + 1) % 50 == 0:
        print(f"  Completed {perm_i + 1}/{N_PERM} permutations...")

perm_diffs = np.array(perm_diffs)
perm_mean_diff = float(np.mean(perm_diffs))
perm_std_diff = float(np.std(perm_diffs))
perm_p = float(np.mean(perm_diffs >= observed_diff))
z_score = ((observed_diff - perm_mean_diff) / perm_std_diff
           if perm_std_diff > 0 else 0.0)

print(f"\nObserved EARLY - LATE difference: {observed_diff:+.3f}")
print(f"Permutation mean difference: {perm_mean_diff:+.3f} +/- {perm_std_diff:.3f}")
print(f"Z-score: {z_score:.2f}")
print(f"Permutation p-value (one-sided, EARLY > LATE): {perm_p:.4f}")


# ============================================================
# STEP 8: Determine verdict
# ============================================================
print("\n" + "=" * 60)

# Pass: EARLY accuracy > LATE by >10 percentage points
# Fail: Equal (specification gradient is operational, not material)
passes_10pp = early_late_diff > 0.10
early_significantly_better = perm_p < 0.05
cramers_early_higher = mean_early_v > mean_late_v and w_p < 0.05

if passes_10pp and early_significantly_better:
    verdict = 'PASS'
    interpretation = (
        f"Early-body vocabulary is more section-discriminative than late-body "
        f"vocabulary. Best EARLY accuracy ({best_early_acc:.1%}) exceeds best LATE "
        f"accuracy ({best_late_acc:.1%}) by {early_late_diff*100:.1f} percentage points "
        f"(>{10} pp threshold). This difference is statistically significant "
        f"(permutation p={perm_p:.4f}). The specification gradient carries "
        f"material-relevant section information beyond operational patterns."
    )
elif early_late_diff > 0.05 and early_significantly_better:
    verdict = 'MARGINAL'
    interpretation = (
        f"Early-body vocabulary shows moderately higher section discrimination "
        f"than late-body vocabulary. Best EARLY accuracy ({best_early_acc:.1%}) "
        f"exceeds best LATE accuracy ({best_late_acc:.1%}) by "
        f"{early_late_diff*100:.1f} pp (below 10 pp threshold but above 5 pp). "
        f"The difference is statistically significant (permutation p={perm_p:.4f}) "
        f"but too small to clearly support a material-specification interpretation."
    )
else:
    verdict = 'FAIL'
    if early_late_diff <= 0:
        interpretation = (
            f"Early and late body vocabulary show no specification gradient. "
            f"Best EARLY accuracy ({best_early_acc:.1%}) does not exceed best LATE "
            f"accuracy ({best_late_acc:.1%}) (difference: {early_late_diff*100:+.1f} pp). "
            f"Section discrimination is equally distributed across paragraph positions, "
            f"consistent with the specification gradient being operational (rarity-based) "
            f"rather than material-specific."
        )
    else:
        interpretation = (
            f"Early-body vocabulary shows only weak section discrimination advantage. "
            f"Best EARLY accuracy ({best_early_acc:.1%}) exceeds best LATE accuracy "
            f"({best_late_acc:.1%}) by {early_late_diff*100:.1f} pp (below 10 pp "
            f"threshold). "
        )
        if not early_significantly_better:
            interpretation += (
                f"The difference is not statistically significant "
                f"(permutation p={perm_p:.4f}). "
            )
        interpretation += (
            f"The specification gradient is not strongly material-specific."
        )

print(f"=== VERDICT: {verdict} ===")
print(interpretation)

if cramers_early_higher:
    print(f"\nSupporting evidence: Mean Cramer's V is higher for EARLY "
          f"({mean_early_v:.4f}) than LATE ({mean_late_v:.4f}), "
          f"Wilcoxon p={w_p:.4f}.")
else:
    print(f"\nCramer's V comparison: EARLY mean={mean_early_v:.4f}, "
          f"LATE mean={mean_late_v:.4f}, Wilcoxon p={w_p:.4f}.")


# ============================================================
# STEP 9: Build output JSON
# ============================================================
output = {
    'test': 'specification_vocabulary_distinctiveness',
    'test_number': 10,
    'question': ('Is the specification vocabulary (early body) more '
                 'section-discriminative than execution vocabulary (late body)?'),
    'method': {
        'description': (
            'Split each paragraph into EARLY (first 33%) and LATE (last 33%) '
            'token partitions. Extract MIDDLE vocabulary for each. Build '
            'presence/absence feature vectors from common MIDDLEs (in 20+ '
            'paragraphs). Classify section using LOO-CV with KNN(k=5) and '
            'NearestCentroid. Compare early vs late accuracy. Also compute '
            'Cramer\'s V for MIDDLE x section in each position partition.'
        ),
        'min_paragraph_tokens': MIN_PARAGRAPH_TOKENS,
        'early_fraction': EARLY_FRACTION,
        'late_fraction': LATE_FRACTION,
        'common_middle_threshold': COMMON_MIDDLE_THRESHOLD,
        'n_permutations': N_PERM,
    },
    'data_summary': {
        'total_currier_b_tokens': len(all_tokens),
        'total_paragraphs_raw': total_paragraphs_raw,
        'paragraphs_after_filter': len(paragraphs),
        'sections': sections,
        'n_sections': n_sections,
        'section_distribution': {s: int(section_counts[s]) for s in sections},
        'n_common_middles': len(common_middles),
        'feature_density_early': round(X_early.sum() / X_early.size * 100, 2),
        'feature_density_late': round(X_late.sum() / X_late.size * 100, 2),
    },
    'classification_results': {
        'early_knn_k5_accuracy': round(acc_early_knn, 4),
        'early_nearest_centroid_accuracy': round(acc_early_nc, 4),
        'late_knn_k5_accuracy': round(acc_late_knn, 4),
        'late_nearest_centroid_accuracy': round(acc_late_nc, 4),
        'best_early_accuracy': round(best_early_acc, 4),
        'best_early_method': best_early_method,
        'best_late_accuracy': round(best_late_acc, 4),
        'best_late_method': best_late_method,
        'early_minus_late_pp': round(early_late_diff * 100, 2),
        'chance_level': round(chance_level, 4),
        'majority_baseline': round(majority_fraction, 4),
        'majority_class': majority_section,
    },
    'per_section_accuracy': {
        'early': per_section_early,
        'late': per_section_late,
    },
    'cramers_v_analysis': {
        'middles_tested_early': len(early_cramers),
        'middles_tested_late': len(late_cramers),
        'mean_cramers_v_early': round(mean_early_v, 4),
        'mean_cramers_v_late': round(mean_late_v, 4),
        'median_cramers_v_early': round(median_early_v, 4),
        'median_cramers_v_late': round(median_late_v, 4),
        'significant_early': early_sig,
        'significant_late': late_sig,
        'paired_comparison': {
            'n_shared_middles': len(shared_middles),
            'mean_paired_diff_early_minus_late': round(mean_paired_diff, 4),
            'early_higher_count': early_wins,
            'late_higher_count': late_wins,
            'ties': ties,
            'wilcoxon_W': round(w_stat, 1),
            'wilcoxon_p': round(w_p, 6),
        },
        'top_10_early_discriminative': {
            m: {**r, 'p_value': round(r['p_value'], 6)}
            for m, r in early_sorted[:10]
        },
    },
    'permutation_test': {
        'n_permutations': N_PERM,
        'observed_diff': round(observed_diff, 4),
        'permutation_mean_diff': round(perm_mean_diff, 4),
        'permutation_std_diff': round(perm_std_diff, 4),
        'z_score': round(z_score, 2),
        'p_value_one_sided': round(perm_p, 4),
    },
    'pass_criteria': {
        'early_late_diff_threshold_pp': 10,
        'permutation_significance': 0.05,
    },
    'verdict': verdict,
    'interpretation': interpretation,
}

output = clean_for_json(output)

with open(OUTPUT_PATH, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nOutput written to {OUTPUT_PATH}")
