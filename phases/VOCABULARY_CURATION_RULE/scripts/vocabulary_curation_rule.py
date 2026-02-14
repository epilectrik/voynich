#!/usr/bin/env python3
"""
Phase 351: VOCABULARY_CURATION_RULE
=====================================
PREFIX × MIDDLE × SUFFIX compositional product space generates more types than
actually exist in the B corpus. What determines which combinations are allowed?

Approach:
  1. Extract all B token types and their morphological decompositions
  2. Build the full product space: observed_PREFIXes × observed_MIDDLEs × observed_SUFFIXes
  3. Mark which combinations actually exist
  4. Extract features for each combination
  5. Train classifiers (decision tree, logistic regression) on exists/doesn't-exist
  6. Analyze the decision boundary

Features:
  - PREFIX frequency (log), MIDDLE frequency (log), SUFFIX frequency (log)
  - PREFIX × MIDDLE co-occurrence count (has the pair ever been seen together?)
  - MIDDLE × SUFFIX co-occurrence count
  - PREFIX length, MIDDLE length, SUFFIX length, total length
  - Whether PREFIX × MIDDLE is in C911 forbidden list (102 forbidden pairs)
  - Role of MIDDLE's most common class
  - Macro-state of MIDDLE's most common class
  - Is MIDDLE compound (contains sub-MIDDLEs)?
  - Is MIDDLE a kernel character (k, h, e)?
  - Suffix stratum of the MIDDLE's class role

Depends on: C1025 (M4 hallucination), C911 (PREFIX×MIDDLE selectivity),
            C267 (morphological decomposition), C1003 (pairwise compositionality)
"""

import json
import sys
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(351)


# ── Constants ────────────────────────────────────────────────────────

MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}
CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state

ROLE_CLASSES = {
    'CC':  {10, 11, 12, 17},
    'EN':  {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49},
    'FL':  {7, 30, 38, 40},
    'FQ':  {9, 13, 14, 23},
    'AX':  {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29},
}
CLASS_TO_ROLE = {}
for role, classes in ROLE_CLASSES.items():
    for c in classes:
        CLASS_TO_ROLE[c] = role

KERNEL_MIDDLES = {'k', 'h', 'e', 'ke', 'kch', 'he', 'eke'}


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load B corpus and build morphological inventory."""
    print("Loading data...")

    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}

    morph = Morphology()

    # Collect all B token types with morphological decomposition
    token_types = {}    # word -> {prefix, middle, suffix, count, class}
    prefix_counts = Counter()
    middle_counts = Counter()
    suffix_counts = Counter()
    prefix_middle_cooc = Counter()   # (prefix, middle) -> count
    middle_suffix_cooc = Counter()   # (middle, suffix) -> count
    middle_class_dist = defaultdict(Counter)  # middle -> {class: count}

    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue
        cls = token_to_class.get(token.word)
        if cls is None:
            continue

        m = morph.extract(token.word)
        prefix = m.prefix if m else ''
        middle = m.middle if m else token.word
        suffix = m.suffix if m else ''

        # Normalize: empty string for absent components
        prefix = prefix or ''
        middle = middle or ''
        suffix = suffix or ''

        if token.word not in token_types:
            token_types[token.word] = {
                'prefix': prefix, 'middle': middle, 'suffix': suffix,
                'cls': cls, 'count': 0,
            }
        token_types[token.word]['count'] += 1

        prefix_counts[prefix] += 1
        middle_counts[middle] += 1
        suffix_counts[suffix] += 1
        prefix_middle_cooc[(prefix, middle)] += 1
        middle_suffix_cooc[(middle, suffix)] += 1
        middle_class_dist[middle][cls] += 1

    # Get unique morphological components
    all_prefixes = sorted(set(t['prefix'] for t in token_types.values()))
    all_middles = sorted(set(t['middle'] for t in token_types.values()))
    all_suffixes = sorted(set(t['suffix'] for t in token_types.values()))

    print(f"  {len(token_types)} unique B token types")
    print(f"  {len(all_prefixes)} unique PREFIXes (incl. bare)")
    print(f"  {len(all_middles)} unique MIDDLEs")
    print(f"  {len(all_suffixes)} unique SUFFIXes (incl. bare)")

    # Most common class for each MIDDLE
    middle_primary_class = {}
    for mid, class_counts in middle_class_dist.items():
        middle_primary_class[mid] = class_counts.most_common(1)[0][0]

    return {
        'token_types': token_types,
        'all_prefixes': all_prefixes,
        'all_middles': all_middles,
        'all_suffixes': all_suffixes,
        'prefix_counts': prefix_counts,
        'middle_counts': middle_counts,
        'suffix_counts': suffix_counts,
        'prefix_middle_cooc': prefix_middle_cooc,
        'middle_suffix_cooc': middle_suffix_cooc,
        'middle_primary_class': middle_primary_class,
        'middle_class_dist': middle_class_dist,
        'morph': morph,
    }


# ── Build Product Space ──────────────────────────────────────────────

def build_product_space(data):
    """Enumerate all PREFIX × MIDDLE × SUFFIX combinations and check existence."""
    print("\nBuilding product space...")

    token_types = data['token_types']
    all_prefixes = data['all_prefixes']
    all_middles = data['all_middles']
    all_suffixes = data['all_suffixes']

    # Build set of existing (prefix, middle, suffix) triples
    existing_triples = set()
    for word, info in token_types.items():
        existing_triples.add((info['prefix'], info['middle'], info['suffix']))

    # Full product space
    full_space_size = len(all_prefixes) * len(all_middles) * len(all_suffixes)
    print(f"  Full product space: {len(all_prefixes)} × {len(all_middles)} × {len(all_suffixes)} = {full_space_size}")
    print(f"  Existing triples: {len(existing_triples)}")
    print(f"  Missing: {full_space_size - len(existing_triples)}")

    # The full product space is too large for most MIDDLE inventories.
    # Focus on the PRODUCTIVE combinations: only PREFIXes, MIDDLEs, and SUFFIXes
    # that appear at least N times, so we're testing compositional rules,
    # not rare singletons.

    MIN_PREFIX_COUNT = 10
    MIN_MIDDLE_COUNT = 5
    MIN_SUFFIX_COUNT = 10

    productive_prefixes = [p for p in all_prefixes if data['prefix_counts'][p] >= MIN_PREFIX_COUNT]
    productive_middles = [m for m in all_middles if data['middle_counts'][m] >= MIN_MIDDLE_COUNT]
    productive_suffixes = [s for s in all_suffixes if data['suffix_counts'][s] >= MIN_SUFFIX_COUNT]

    print(f"\n  Productive components (count >= threshold):")
    print(f"    PREFIXes: {len(productive_prefixes)} (threshold {MIN_PREFIX_COUNT})")
    print(f"    MIDDLEs: {len(productive_middles)} (threshold {MIN_MIDDLE_COUNT})")
    print(f"    SUFFIXes: {len(productive_suffixes)} (threshold {MIN_SUFFIX_COUNT})")

    productive_space_size = len(productive_prefixes) * len(productive_middles) * len(productive_suffixes)
    print(f"  Productive product space: {productive_space_size}")

    # Enumerate
    product_space = []
    n_exists = 0
    for prefix in productive_prefixes:
        for middle in productive_middles:
            for suffix in productive_suffixes:
                exists = (prefix, middle, suffix) in existing_triples
                product_space.append({
                    'prefix': prefix,
                    'middle': middle,
                    'suffix': suffix,
                    'exists': exists,
                })
                if exists:
                    n_exists += 1

    missing = productive_space_size - n_exists
    hallucination_pct = missing / max(productive_space_size, 1) * 100
    print(f"  Existing in productive space: {n_exists}")
    print(f"  Missing (hallucinations): {missing}")
    print(f"  Occupancy: {n_exists/max(productive_space_size,1):.1%}")
    print(f"  Hallucination rate: {hallucination_pct:.1f}%")

    return product_space, productive_prefixes, productive_middles, productive_suffixes


# ── Feature Extraction ───────────────────────────────────────────────

def extract_features(product_space, data):
    """Extract features for each combination in the product space."""
    print("\nExtracting features...")

    prefix_counts = data['prefix_counts']
    middle_counts = data['middle_counts']
    suffix_counts = data['suffix_counts']
    pm_cooc = data['prefix_middle_cooc']
    ms_cooc = data['middle_suffix_cooc']
    mid_primary_cls = data['middle_primary_class']

    feature_names = [
        'log_prefix_freq', 'log_middle_freq', 'log_suffix_freq',
        'pm_cooc_exists', 'ms_cooc_exists',
        'pm_cooc_count', 'ms_cooc_count',
        'prefix_len', 'middle_len', 'suffix_len', 'total_len',
        'is_bare_prefix', 'is_bare_suffix',
        'is_kernel_middle',
        'middle_role_CC', 'middle_role_EN', 'middle_role_FL',
        'middle_role_FQ', 'middle_role_AX',
        'middle_state_AXM', 'middle_state_FQ', 'middle_state_CC',
        'middle_state_FL_HAZ', 'middle_state_FL_SAFE', 'middle_state_AXm',
        'log_pm_pointwise_mi', 'log_ms_pointwise_mi',
    ]

    total_tokens = sum(prefix_counts.values())

    X = np.zeros((len(product_space), len(feature_names)))
    y = np.zeros(len(product_space), dtype=int)

    for i, combo in enumerate(product_space):
        prefix = combo['prefix']
        middle = combo['middle']
        suffix = combo['suffix']

        pf = prefix_counts[prefix]
        mf = middle_counts[middle]
        sf = suffix_counts[suffix]

        pm_co = pm_cooc.get((prefix, middle), 0)
        ms_co = ms_cooc.get((middle, suffix), 0)

        # Pointwise MI: log(P(pair) / (P(a) * P(b)))
        if pm_co > 0 and pf > 0 and mf > 0:
            pmi_pm = np.log2((pm_co / total_tokens) / ((pf / total_tokens) * (mf / total_tokens)))
        else:
            pmi_pm = -5.0  # floor for never-seen pairs

        if ms_co > 0 and mf > 0 and sf > 0:
            pmi_ms = np.log2((ms_co / total_tokens) / ((mf / total_tokens) * (sf / total_tokens)))
        else:
            pmi_ms = -5.0

        # Role and state of MIDDLE
        mid_cls = mid_primary_cls.get(middle, 1)
        mid_role = CLASS_TO_ROLE.get(mid_cls, 'AX')
        mid_state = CLASS_TO_STATE.get(mid_cls, 'AXM')

        X[i] = [
            np.log1p(pf), np.log1p(mf), np.log1p(sf),
            1 if pm_co > 0 else 0,
            1 if ms_co > 0 else 0,
            np.log1p(pm_co),
            np.log1p(ms_co),
            len(prefix), len(middle), len(suffix),
            len(prefix) + len(middle) + len(suffix),
            1 if prefix == '' else 0,
            1 if suffix == '' else 0,
            1 if middle in KERNEL_MIDDLES else 0,
            1 if mid_role == 'CC' else 0,
            1 if mid_role == 'EN' else 0,
            1 if mid_role == 'FL' else 0,
            1 if mid_role == 'FQ' else 0,
            1 if mid_role == 'AX' else 0,
            1 if mid_state == 'AXM' else 0,
            1 if mid_state == 'FQ' else 0,
            1 if mid_state == 'CC' else 0,
            1 if mid_state == 'FL_HAZ' else 0,
            1 if mid_state == 'FL_SAFE' else 0,
            1 if mid_state == 'AXm' else 0,
            pmi_pm,
            pmi_ms,
        ]
        y[i] = 1 if combo['exists'] else 0

    print(f"  Feature matrix: {X.shape}")
    print(f"  Positive (exists): {y.sum()}, Negative (missing): {len(y) - y.sum()}")
    print(f"  Class balance: {y.mean():.3f}")

    return X, y, feature_names


# ── Train Classifiers ────────────────────────────────────────────────

def train_classifiers(X, y, feature_names):
    """Train decision tree and logistic regression, evaluate via cross-validation."""
    print("\n=== CLASSIFIER TRAINING ===")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=351)

    results = {}

    # ── Decision Tree (depth 3) ──────────────────────────────
    print("\n--- Decision Tree (max_depth=3) ---")
    dt3 = DecisionTreeClassifier(max_depth=3, random_state=351, class_weight='balanced')
    dt3_scores = cross_val_score(dt3, X, y, cv=cv, scoring='accuracy')
    dt3.fit(X, y)
    dt3_pred = dt3.predict(X)

    print(f"  CV accuracy: {dt3_scores.mean():.4f} (+/- {dt3_scores.std():.4f})")
    print(f"  Training accuracy: {(dt3_pred == y).mean():.4f}")
    print(f"\n  Tree structure:")
    tree_text = export_text(dt3, feature_names=feature_names, max_depth=5)
    print(tree_text)

    # Feature importance
    importances = dt3.feature_importances_
    top_features = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)[:10]
    print(f"  Top features (depth-3 tree):")
    for feat, imp in top_features:
        if imp > 0:
            print(f"    {feat}: {imp:.4f}")

    cm3 = confusion_matrix(y, dt3_pred)
    results['dt3'] = {
        'cv_accuracy': round(float(dt3_scores.mean()), 4),
        'cv_std': round(float(dt3_scores.std()), 4),
        'train_accuracy': round(float((dt3_pred == y).mean()), 4),
        'confusion_matrix': cm3.tolist(),
        'tree_text': tree_text,
        'feature_importances': {f: round(float(i), 6) for f, i in top_features if i > 0},
    }

    # ── Decision Tree (depth 5) ──────────────────────────────
    print("\n--- Decision Tree (max_depth=5) ---")
    dt5 = DecisionTreeClassifier(max_depth=5, random_state=351, class_weight='balanced')
    dt5_scores = cross_val_score(dt5, X, y, cv=cv, scoring='accuracy')
    dt5.fit(X, y)
    dt5_pred = dt5.predict(X)

    print(f"  CV accuracy: {dt5_scores.mean():.4f} (+/- {dt5_scores.std():.4f})")
    print(f"  Training accuracy: {(dt5_pred == y).mean():.4f}")

    importances5 = dt5.feature_importances_
    top_features5 = sorted(zip(feature_names, importances5), key=lambda x: x[1], reverse=True)[:10]
    print(f"  Top features (depth-5 tree):")
    for feat, imp in top_features5:
        if imp > 0:
            print(f"    {feat}: {imp:.4f}")

    cm5 = confusion_matrix(y, dt5_pred)
    results['dt5'] = {
        'cv_accuracy': round(float(dt5_scores.mean()), 4),
        'cv_std': round(float(dt5_scores.std()), 4),
        'train_accuracy': round(float((dt5_pred == y).mean()), 4),
        'confusion_matrix': cm5.tolist(),
        'feature_importances': {f: round(float(i), 6) for f, i in top_features5 if i > 0},
    }

    # ── Decision Tree (unlimited depth) ──────────────────────
    print("\n--- Decision Tree (unlimited depth) ---")
    dt_full = DecisionTreeClassifier(random_state=351, class_weight='balanced')
    dt_full_scores = cross_val_score(dt_full, X, y, cv=cv, scoring='accuracy')
    dt_full.fit(X, y)
    dt_full_pred = dt_full.predict(X)

    print(f"  CV accuracy: {dt_full_scores.mean():.4f} (+/- {dt_full_scores.std():.4f})")
    print(f"  Training accuracy: {(dt_full_pred == y).mean():.4f}")
    print(f"  Tree depth: {dt_full.get_depth()}, leaves: {dt_full.get_n_leaves()}")

    cm_full = confusion_matrix(y, dt_full_pred)
    results['dt_full'] = {
        'cv_accuracy': round(float(dt_full_scores.mean()), 4),
        'cv_std': round(float(dt_full_scores.std()), 4),
        'train_accuracy': round(float((dt_full_pred == y).mean()), 4),
        'tree_depth': dt_full.get_depth(),
        'tree_leaves': dt_full.get_n_leaves(),
        'confusion_matrix': cm_full.tolist(),
    }

    # ── Logistic Regression ──────────────────────────────────
    print("\n--- Logistic Regression ---")
    lr = LogisticRegression(max_iter=1000, random_state=351, class_weight='balanced')
    lr_scores = cross_val_score(lr, X, y, cv=cv, scoring='accuracy')
    lr.fit(X, y)
    lr_pred = lr.predict(X)

    print(f"  CV accuracy: {lr_scores.mean():.4f} (+/- {lr_scores.std():.4f})")
    print(f"  Training accuracy: {(lr_pred == y).mean():.4f}")

    # Top coefficients
    coefs = sorted(zip(feature_names, lr.coef_[0]), key=lambda x: abs(x[1]), reverse=True)[:10]
    print(f"  Top coefficients:")
    for feat, coef in coefs:
        print(f"    {feat}: {coef:+.4f}")

    cm_lr = confusion_matrix(y, lr_pred)
    results['logistic'] = {
        'cv_accuracy': round(float(lr_scores.mean()), 4),
        'cv_std': round(float(lr_scores.std()), 4),
        'train_accuracy': round(float((lr_pred == y).mean()), 4),
        'confusion_matrix': cm_lr.tolist(),
        'top_coefficients': {f: round(float(c), 6) for f, c in coefs},
    }

    # ── Baseline: co-occurrence only ─────────────────────────
    print("\n--- Baseline: PREFIX×MIDDLE co-occurrence only ---")
    # Predict exists=1 if both PREFIX×MIDDLE AND MIDDLE×SUFFIX have been seen
    baseline_pred = ((X[:, feature_names.index('pm_cooc_exists')] == 1) &
                     (X[:, feature_names.index('ms_cooc_exists')] == 1)).astype(int)
    baseline_acc = (baseline_pred == y).mean()
    cm_base = confusion_matrix(y, baseline_pred)
    baseline_precision = cm_base[1, 1] / max(cm_base[:, 1].sum(), 1)
    baseline_recall = cm_base[1, 1] / max(cm_base[1, :].sum(), 1)

    print(f"  Accuracy: {baseline_acc:.4f}")
    print(f"  Precision: {baseline_precision:.4f}")
    print(f"  Recall: {baseline_recall:.4f}")
    print(f"  Confusion matrix: {cm_base.tolist()}")

    results['baseline_cooc'] = {
        'accuracy': round(float(baseline_acc), 4),
        'precision': round(float(baseline_precision), 4),
        'recall': round(float(baseline_recall), 4),
        'confusion_matrix': cm_base.tolist(),
    }

    return results, dt3, dt5, lr


# ── Analysis: What makes a combination illegal? ─────────────────────

def analyze_boundaries(product_space, X, y, feature_names, dt3, data):
    """Analyze what distinguishes existing from non-existing combinations."""
    print("\n=== BOUNDARY ANALYSIS ===")

    results = {}

    # 1. Co-occurrence gating: how much does pairwise co-occurrence explain?
    pm_exists = X[:, feature_names.index('pm_cooc_exists')]
    ms_exists = X[:, feature_names.index('ms_cooc_exists')]

    # Among combos where both pairs have been seen, what fraction exists?
    both_seen = (pm_exists == 1) & (ms_exists == 1)
    neither_seen = (pm_exists == 0) & (ms_exists == 0)
    only_pm = (pm_exists == 1) & (ms_exists == 0)
    only_ms = (pm_exists == 0) & (ms_exists == 1)

    print(f"\n  Pairwise co-occurrence gating:")
    for label, mask in [('Both PM+MS seen', both_seen), ('Only PM seen', only_pm),
                         ('Only MS seen', only_ms), ('Neither seen', neither_seen)]:
        n = mask.sum()
        if n > 0:
            exists_rate = y[mask].mean()
            print(f"    {label}: {n} combos, {exists_rate:.3f} exist rate")
            results[f'cooc_{label.replace(" ", "_").lower()}'] = {
                'n': int(n), 'exists_rate': round(float(exists_rate), 4),
            }

    # 2. PMI analysis: what's the PMI distribution for real vs hallucinated?
    pmi_pm_idx = feature_names.index('log_pm_pointwise_mi')
    pmi_ms_idx = feature_names.index('log_ms_pointwise_mi')

    real_pmi_pm = X[y == 1, pmi_pm_idx]
    fake_pmi_pm = X[y == 0, pmi_pm_idx]
    real_pmi_ms = X[y == 1, pmi_ms_idx]
    fake_pmi_ms = X[y == 0, pmi_ms_idx]

    print(f"\n  PMI distributions:")
    print(f"    PREFIX×MIDDLE PMI: real={real_pmi_pm.mean():.3f}, missing={fake_pmi_pm.mean():.3f}")
    print(f"    MIDDLE×SUFFIX PMI: real={real_pmi_ms.mean():.3f}, missing={fake_pmi_ms.mean():.3f}")

    results['pmi'] = {
        'pm_real_mean': round(float(real_pmi_pm.mean()), 4),
        'pm_missing_mean': round(float(fake_pmi_pm.mean()), 4),
        'ms_real_mean': round(float(real_pmi_ms.mean()), 4),
        'ms_missing_mean': round(float(fake_pmi_ms.mean()), 4),
    }

    # 3. Role/state analysis: do missing combos concentrate in specific roles?
    print(f"\n  Existence rate by MIDDLE role:")
    for role_feat in ['middle_role_CC', 'middle_role_EN', 'middle_role_FL',
                      'middle_role_FQ', 'middle_role_AX']:
        idx = feature_names.index(role_feat)
        mask = X[:, idx] == 1
        if mask.sum() > 0:
            rate = y[mask].mean()
            print(f"    {role_feat}: {rate:.3f} ({y[mask].sum()}/{mask.sum()})")

    # 4. Bare prefix/suffix analysis
    print(f"\n  Existence rate by bare status:")
    bare_pfx = X[:, feature_names.index('is_bare_prefix')] == 1
    bare_sfx = X[:, feature_names.index('is_bare_suffix')] == 1
    print(f"    Bare prefix: {y[bare_pfx].mean():.3f} ({y[bare_pfx].sum()}/{bare_pfx.sum()})")
    print(f"    Non-bare prefix: {y[~bare_pfx].mean():.3f} ({y[~bare_pfx].sum()}/{(~bare_pfx).sum()})")
    print(f"    Bare suffix: {y[bare_sfx].mean():.3f} ({y[bare_sfx].sum()}/{bare_sfx.sum()})")
    print(f"    Non-bare suffix: {y[~bare_sfx].mean():.3f} ({y[~bare_sfx].sum()}/{(~bare_sfx).sum()})")

    # 5. What's the simplest sufficient rule?
    # Test: "exists if and only if PREFIX×MIDDLE has been seen together"
    pm_only_pred = (pm_exists == 1).astype(int)
    pm_only_acc = (pm_only_pred == y).mean()
    pm_only_precision = y[(pm_only_pred == 1)].mean() if (pm_only_pred == 1).sum() > 0 else 0
    pm_only_recall = pm_only_pred[y == 1].mean() if y.sum() > 0 else 0

    print(f"\n  Simplest rule test: 'exists iff PREFIX×MIDDLE has been seen'")
    print(f"    Accuracy: {pm_only_acc:.4f}")
    print(f"    Precision: {pm_only_precision:.4f}")
    print(f"    Recall: {pm_only_recall:.4f}")

    results['pm_only_rule'] = {
        'accuracy': round(float(pm_only_acc), 4),
        'precision': round(float(pm_only_precision), 4),
        'recall': round(float(pm_only_recall), 4),
    }

    # 6. Misclassification analysis: what do the classifiers get wrong?
    dt3_pred = dt3.predict(X)
    false_positives = (dt3_pred == 1) & (y == 0)  # predicted exists but doesn't
    false_negatives = (dt3_pred == 0) & (y == 1)  # predicted missing but exists

    print(f"\n  Decision tree (depth 3) errors:")
    print(f"    False positives: {false_positives.sum()} (predicted exists, actually missing)")
    print(f"    False negatives: {false_negatives.sum()} (predicted missing, actually exists)")

    results['dt3_errors'] = {
        'false_positives': int(false_positives.sum()),
        'false_negatives': int(false_negatives.sum()),
    }

    return results


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("Phase 351: VOCABULARY_CURATION_RULE")
    print("=" * 60)

    data = load_data()
    product_space, prod_prefixes, prod_middles, prod_suffixes = build_product_space(data)

    X, y, feature_names = extract_features(product_space, data)

    classifier_results, dt3, dt5, lr = train_classifiers(X, y, feature_names)
    boundary_results = analyze_boundaries(product_space, X, y, feature_names, dt3, data)

    # ── Summary ──────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    best_cv = max(
        ('dt3', classifier_results['dt3']['cv_accuracy']),
        ('dt5', classifier_results['dt5']['cv_accuracy']),
        ('dt_full', classifier_results['dt_full']['cv_accuracy']),
        ('logistic', classifier_results['logistic']['cv_accuracy']),
        key=lambda x: x[1]
    )

    baseline_acc = classifier_results['baseline_cooc']['accuracy']
    pm_only_acc = boundary_results['pm_only_rule']['accuracy']

    print(f"\n  Product space: {len(product_space)} combinations")
    print(f"  Existing: {int(y.sum())} ({y.mean():.1%})")
    print(f"  Missing: {int(len(y) - y.sum())} ({1-y.mean():.1%})")
    print(f"\n  Classifier performance (5-fold CV):")
    print(f"    Decision tree depth 3: {classifier_results['dt3']['cv_accuracy']:.4f}")
    print(f"    Decision tree depth 5: {classifier_results['dt5']['cv_accuracy']:.4f}")
    print(f"    Decision tree full:    {classifier_results['dt_full']['cv_accuracy']:.4f}")
    print(f"    Logistic regression:   {classifier_results['logistic']['cv_accuracy']:.4f}")
    print(f"    Baseline (PM+MS cooc): {baseline_acc:.4f}")
    print(f"    PM-only rule:          {pm_only_acc:.4f}")

    # Determine verdict
    if best_cv[1] > 0.90:
        verdict = "LEARNABLE_SIMPLE"
        desc = f"A simple {best_cv[0]} achieves >{best_cv[1]:.0%} CV accuracy — token existence follows a learnable rule"
    elif best_cv[1] > 0.80:
        verdict = "LEARNABLE_MODERATE"
        desc = f"Best classifier {best_cv[0]} at {best_cv[1]:.0%} — partial rule with residual unpredictability"
    elif best_cv[1] > baseline_acc + 0.02:
        verdict = "WEAKLY_LEARNABLE"
        desc = f"Classifier ({best_cv[1]:.0%}) barely beats co-occurrence baseline ({baseline_acc:.0%})"
    else:
        verdict = "NOT_LEARNABLE"
        desc = f"No classifier beats co-occurrence baseline — existence is determined by pairwise compatibility, not a higher rule"

    print(f"\n  VERDICT: {verdict}")
    print(f"  {desc}")

    results = {
        'metadata': {
            'phase': 351,
            'name': 'VOCABULARY_CURATION_RULE',
            'product_space_size': len(product_space),
            'n_existing': int(y.sum()),
            'n_missing': int(len(y) - y.sum()),
            'occupancy_rate': round(float(y.mean()), 4),
            'n_productive_prefixes': len(prod_prefixes),
            'n_productive_middles': len(prod_middles),
            'n_productive_suffixes': len(prod_suffixes),
        },
        'classifiers': classifier_results,
        'boundary_analysis': boundary_results,
        'summary': {
            'verdict': verdict,
            'description': desc,
            'best_classifier': best_cv[0],
            'best_cv_accuracy': best_cv[1],
            'baseline_accuracy': baseline_acc,
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'vocabulary_curation_rule.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
