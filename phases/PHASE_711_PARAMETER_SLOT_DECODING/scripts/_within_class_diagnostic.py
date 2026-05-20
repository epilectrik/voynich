"""PHASE_711 follow-up: within-class diagnostic + feature importance.

Crazy-expert pre-registered two discriminating tests:

1. WITHIN-CLASS RETENTION: For top-N most-frequent classes, train an e-depth-only
   predictor of next-class WITHIN each fixed class. If parametric semantics:
   e-depth should retain >50% of full-slot-feature gain within class. If
   sub-class refinement: e-depth should retain <20% within class.

2. FEATURE IMPORTANCE: from the slot LogReg coefficient magnitudes:
   - If HEAD atom dominates → parametric reading favored
   - If prefix_category dominates → class-refinement reading favored

This script computes both, providing the discriminator promised in the INDEX.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

OUT_PATH = ROOT / 'phases' / 'PHASE_711_PARAMETER_SLOT_DECODING' / 'results' / 'within_class_diagnostic.json'


# Re-use feature extraction from main script
PREFIX_CATEGORIES = {
    'ch': 'ch', 'sh': 'sh', 'qo': 'qo', 'ok': 'ok', 'ot': 'ot',
    'ol': 'ol', 'ct': 'ct', 'da': 'da',
}
HEAD_ATOMS = set('aeokt')
TERM_ATOMS = set('ynmhlrkt')


def categorize_prefix(prefix):
    if not prefix:
        return 'NONE'
    if prefix in PREFIX_CATEGORIES:
        return PREFIX_CATEGORIES[prefix]
    return 'EXTENDED'


def extract_slot_features(token, morph_obj):
    if not token:
        return None
    try:
        m = morph_obj.extract(token)
    except Exception:
        return None
    middle = m.middle or ''
    prefix = m.prefix or ''
    suffix = m.suffix or ''
    e_count = middle.count('e')
    e_depth = min(e_count, 3)
    head_atom = 'NONE'
    if middle:
        head_atom = middle[0] if middle[0] in HEAD_ATOMS else 'PSEUDO_HEAD'
    term_atom = 'NONE'
    if middle and middle[-1] in TERM_ATOMS:
        term_atom = middle[-1]
    has_suffix = suffix != ''
    suffix_first = suffix[0] if suffix else 'NONE'
    return {
        'prefix_cat': categorize_prefix(prefix),
        'e_depth': e_depth,
        'head_atom': head_atom,
        'term_atom': term_atom,
        'has_suffix': int(has_suffix),
        'suffix_first': suffix_first,
    }


def build_pairs():
    tx = Transcript()
    morph = Morphology()
    class_map = json.loads(
        (ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json').read_text(encoding='utf-8')
    )['token_to_class']
    lines = defaultdict(list)
    for t in tx.all(h_only=True):
        if not t.word.strip() or '*' in t.word: continue
        if t.language != 'B': continue
        if not (t.placement and t.placement.startswith('P')): continue
        lines[(t.folio, t.line)].append(t)
    pairs = []
    for (folio, line), toks in lines.items():
        for i in range(len(toks) - 1):
            cur, nxt = toks[i], toks[i + 1]
            cw, nw = cur.word.lower(), nxt.word.lower()
            if cw not in class_map or nw not in class_map: continue
            feats = extract_slot_features(cw, morph)
            if feats is None: continue
            pairs.append({
                'folio': folio, 'cur_class': class_map[cw], 'next_class': class_map[nw],
                **feats,
            })
    return pairs


def cross_entropy(y_true, proba):
    eps = 1e-9
    p = proba[np.arange(len(y_true)), y_true].clip(eps, 1.0)
    return -np.mean(np.log2(p))


def top_k_accuracy(y_true, proba, k=1):
    top_k = np.argsort(-proba, axis=1)[:, :k]
    return np.mean([y_true[i] in top_k[i] for i in range(len(y_true))])


def empirical_baseline(y_train, n_classes, alpha=0.1):
    """Just predict the marginal distribution of next-class within this subset."""
    counts = np.zeros(n_classes) + alpha
    for y in y_train:
        counts[y] += 1
    counts /= counts.sum()
    return counts  # broadcasted to all test points


def fit_logreg_e_depth(e_depth_train, y_train, e_depth_test, n_classes):
    """Predict next-class from e-depth alone (4 levels: 0, 1, 2, 3+)."""
    from sklearn.linear_model import LogisticRegression
    X_train = np.eye(4)[e_depth_train]
    X_test = np.eye(4)[e_depth_test]
    clf = LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
    clf.fit(X_train, y_train)
    proba = clf.predict_proba(X_test)
    aligned = np.full((proba.shape[0], n_classes), 1e-9)
    for j, cls in enumerate(clf.classes_):
        aligned[:, cls] = proba[:, j]
    aligned /= aligned.sum(axis=1, keepdims=True)
    return aligned


def fit_logreg_full_slot(features_train, y_train, features_test, n_classes):
    """Predict next-class from full slot one-hot features (no current_class)."""
    from sklearn.linear_model import LogisticRegression
    clf = LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
    clf.fit(features_train, y_train)
    proba = clf.predict_proba(features_test)
    aligned = np.full((proba.shape[0], n_classes), 1e-9)
    for j, cls in enumerate(clf.classes_):
        aligned[:, cls] = proba[:, j]
    aligned /= aligned.sum(axis=1, keepdims=True)
    return aligned


def build_full_slot_feature_matrix(pairs, top_classes):
    """Build slot-only one-hot feature matrix (no current_class) for items in top_classes."""
    pfx_vals = sorted(set(p['prefix_cat'] for p in pairs))
    head_vals = sorted(set(p['head_atom'] for p in pairs))
    term_vals = sorted(set(p['term_atom'] for p in pairs))
    suff_vals = sorted(set(p['suffix_first'] for p in pairs))
    pfx_idx = {v: i for i, v in enumerate(pfx_vals)}
    head_idx = {v: i for i, v in enumerate(head_vals)}
    term_idx = {v: i for i, v in enumerate(term_vals)}
    suff_idx = {v: i for i, v in enumerate(suff_vals)}

    dim = len(pfx_vals) + 4 + len(head_vals) + len(term_vals) + 1 + len(suff_vals)
    n = len(pairs)
    X = np.zeros((n, dim), dtype=np.float32)
    e_depth = np.zeros(n, dtype=np.int32)
    for i, p in enumerate(pairs):
        off = 0
        X[i, off + pfx_idx[p['prefix_cat']]] = 1.0
        off += len(pfx_vals)
        X[i, off + p['e_depth']] = 1.0
        e_depth[i] = p['e_depth']
        off += 4
        X[i, off + head_idx[p['head_atom']]] = 1.0
        off += len(head_vals)
        X[i, off + term_idx[p['term_atom']]] = 1.0
        off += len(term_vals)
        X[i, off] = float(p['has_suffix'])
        off += 1
        X[i, off + suff_idx[p['suffix_first']]] = 1.0
    return X, e_depth, {
        'prefix_dim': len(pfx_vals), 'edepth_dim': 4,
        'head_dim': len(head_vals), 'term_dim': len(term_vals),
        'has_suffix_dim': 1, 'suffix_first_dim': len(suff_vals),
        'total_dim': dim,
        'pfx_vals': pfx_vals, 'head_vals': head_vals, 'term_vals': term_vals, 'suff_vals': suff_vals,
    }


# ---- Main ----

def main():
    print("=" * 90)
    print("PHASE_711 FOLLOW-UP DIAGNOSTICS: within-class retention + feature importance")
    print("=" * 90)

    pairs = build_pairs()
    print(f"\n  N pairs: {len(pairs)}")
    next_classes = sorted(set(p['next_class'] for p in pairs))
    n_classes = max(next_classes) + 1
    print(f"  N next-classes (max+1): {n_classes}")

    # ---- TEST 1: within-class e-depth retention ----
    print("\n" + "=" * 90)
    print("TEST 1: WITHIN-CLASS e-depth retention (crazy-expert pre-registered)")
    print("=" * 90)
    print("\nIf parametric: e-depth retains >50% of full-slot gain WITHIN fixed class")
    print("If class-refinement: e-depth retains <20% of full-slot gain WITHIN fixed class")

    cur_class_counts = Counter(p['cur_class'] for p in pairs)
    top10 = [cls for cls, _ in cur_class_counts.most_common(10)]
    print(f"\nTop 10 most-frequent current-classes (counts): {[(c, cur_class_counts[c]) for c in top10]}")

    folios_by_pair_idx = [p['folio'] for p in pairs]
    unique_folios = sorted(set(folios_by_pair_idx))
    rng = np.random.default_rng(42)
    folio_perm = rng.permutation(unique_folios)
    folio_folds = np.array_split(folio_perm, 5)

    within_class_results = []
    for target_class in top10:
        # Restrict to pairs where cur_class == target_class
        cls_indices = [i for i, p in enumerate(pairs) if p['cur_class'] == target_class]
        if len(cls_indices) < 100:
            continue

        # 5-fold folio-out CV on this subset
        baseline_ces = []
        edepth_ces = []
        fullslot_ces = []
        baseline_accs = []
        edepth_accs = []
        fullslot_accs = []
        for test_folios in folio_folds:
            test_set = set(test_folios)
            train_idx = [i for i in cls_indices if pairs[i]['folio'] not in test_set]
            test_idx = [i for i in cls_indices if pairs[i]['folio'] in test_set]
            if len(train_idx) < 50 or len(test_idx) < 10:
                continue

            y_train = np.array([pairs[i]['next_class'] for i in train_idx])
            y_test = np.array([pairs[i]['next_class'] for i in test_idx])
            e_depth_train = np.array([pairs[i]['e_depth'] for i in train_idx])
            e_depth_test = np.array([pairs[i]['e_depth'] for i in test_idx])

            # Baseline: marginal P(next_class) within this class
            marginal = empirical_baseline(y_train, n_classes, alpha=0.1)
            p_base = np.tile(marginal, (len(y_test), 1))
            ce_base = cross_entropy(y_test, p_base)
            acc_base = top_k_accuracy(y_test, p_base, 1)

            # e-depth model
            try:
                p_ed = fit_logreg_e_depth(e_depth_train, y_train, e_depth_test, n_classes)
                ce_ed = cross_entropy(y_test, p_ed)
                acc_ed = top_k_accuracy(y_test, p_ed, 1)
            except ValueError:
                # Only 1 class in y_train (degenerate)
                continue

            # Full slot model (no class — all tokens here share same class)
            X_train, _, _ = build_full_slot_feature_matrix(
                [pairs[i] for i in train_idx], [target_class]
            )
            X_test, _, _ = build_full_slot_feature_matrix(
                [pairs[i] for i in test_idx], [target_class]
            )
            try:
                p_full = fit_logreg_full_slot(X_train, y_train, X_test, n_classes)
                ce_full = cross_entropy(y_test, p_full)
                acc_full = top_k_accuracy(y_test, p_full, 1)
            except ValueError:
                continue

            baseline_ces.append(ce_base); edepth_ces.append(ce_ed); fullslot_ces.append(ce_full)
            baseline_accs.append(acc_base); edepth_accs.append(acc_ed); fullslot_accs.append(acc_full)

        if len(baseline_ces) < 3:
            continue
        ce_base_m = float(np.mean(baseline_ces))
        ce_ed_m = float(np.mean(edepth_ces))
        ce_full_m = float(np.mean(fullslot_ces))
        acc_base_m = float(np.mean(baseline_accs))
        acc_ed_m = float(np.mean(edepth_accs))
        acc_full_m = float(np.mean(fullslot_accs))

        full_gain = ce_base_m - ce_full_m
        edepth_gain = ce_base_m - ce_ed_m
        retention = edepth_gain / full_gain if full_gain > 0 else float('nan')

        within_class_results.append({
            'class': int(target_class),
            'n_pairs': len(cls_indices),
            'n_test_folds': len(baseline_ces),
            'ce_marginal_baseline': ce_base_m,
            'ce_edepth_only': ce_ed_m,
            'ce_full_slot': ce_full_m,
            'acc_baseline': acc_base_m,
            'acc_edepth': acc_ed_m,
            'acc_full_slot': acc_full_m,
            'full_slot_gain_ce': full_gain,
            'edepth_gain_ce': edepth_gain,
            'edepth_retention_ratio': retention,
        })

        print(f"\n  Class {target_class} (N_pairs={len(cls_indices)}):")
        print(f"    Marginal CE within class: {ce_base_m:.4f}")
        print(f"    Full slot CE:             {ce_full_m:.4f}  (gain={full_gain:+.4f})")
        print(f"    e-depth only CE:          {ce_ed_m:.4f}  (gain={edepth_gain:+.4f})")
        print(f"    e-depth retention ratio:  {retention:.2%}")
        print(f"    Acc: marginal={acc_base_m:.3f}, e-depth={acc_ed_m:.3f}, full={acc_full_m:.3f}")

    # Aggregate retention across classes
    valid = [r for r in within_class_results if not np.isnan(r['edepth_retention_ratio'])
             and r['full_slot_gain_ce'] > 0]
    if valid:
        mean_retention = np.mean([r['edepth_retention_ratio'] for r in valid])
        median_retention = np.median([r['edepth_retention_ratio'] for r in valid])
    else:
        mean_retention = median_retention = float('nan')

    print(f"\n  --- Aggregate across {len(valid)} classes with positive full-slot gain ---")
    print(f"    Mean e-depth retention ratio:   {mean_retention:.2%}")
    print(f"    Median e-depth retention ratio: {median_retention:.2%}")

    # Crazy-expert's pre-registered thresholds
    if mean_retention > 0.50:
        test1_verdict = "PARAMETRIC RETENTION SURVIVES (>50%)"
    elif mean_retention < 0.20:
        test1_verdict = "SUB-CLASS REFINEMENT WINS (<20%)"
    else:
        test1_verdict = "INDETERMINATE (between 20% and 50%)"
    print(f"    Verdict: {test1_verdict}")

    # ---- TEST 2: feature importance from full slot model on full corpus ----
    print("\n" + "=" * 90)
    print("TEST 2: FEATURE IMPORTANCE (crazy-expert pre-registered ordering)")
    print("=" * 90)
    print("\nCrazy-expert prediction if parametric:")
    print("  HEAD atom should dominate >> e-depth >> TERM atom >> suffix_first")
    print("If prefix_category dominates HEAD by >2x, parametric reading weakens.")

    # Train on full corpus, get coefficient magnitudes per feature group
    from sklearn.linear_model import LogisticRegression
    X_full, _, slot_meta = build_full_slot_feature_matrix(pairs, sorted(set(p['cur_class'] for p in pairs)))
    y_full = np.array([p['next_class'] for p in pairs])
    # Add current class as one-hot
    cur_classes = sorted(set(p['cur_class'] for p in pairs))
    cls_idx = {c: i for i, c in enumerate(cur_classes)}
    X_cls = np.zeros((len(pairs), len(cur_classes)), dtype=np.float32)
    for i, p in enumerate(pairs):
        X_cls[i, cls_idx[p['cur_class']]] = 1.0
    X_full_with_cls = np.hstack([X_cls, X_full])

    clf = LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
    clf.fit(X_full_with_cls, y_full)
    coef = clf.coef_  # (n_next_classes, n_features)

    # Compute L1 norm of coefficients per feature group
    n_cur = len(cur_classes)
    off = n_cur
    pfx_norm = float(np.abs(coef[:, off:off + slot_meta['prefix_dim']]).sum())
    off += slot_meta['prefix_dim']
    ed_norm = float(np.abs(coef[:, off:off + slot_meta['edepth_dim']]).sum())
    off += slot_meta['edepth_dim']
    head_norm = float(np.abs(coef[:, off:off + slot_meta['head_dim']]).sum())
    off += slot_meta['head_dim']
    term_norm = float(np.abs(coef[:, off:off + slot_meta['term_dim']]).sum())
    off += slot_meta['term_dim']
    has_suff_norm = float(np.abs(coef[:, off:off + slot_meta['has_suffix_dim']]).sum())
    off += slot_meta['has_suffix_dim']
    suff_first_norm = float(np.abs(coef[:, off:off + slot_meta['suffix_first_dim']]).sum())

    # Normalize by feature dimensionality for fair comparison
    pfx_per_dim = pfx_norm / slot_meta['prefix_dim']
    ed_per_dim = ed_norm / slot_meta['edepth_dim']
    head_per_dim = head_norm / slot_meta['head_dim']
    term_per_dim = term_norm / slot_meta['term_dim']
    suff_per_dim = suff_first_norm / slot_meta['suffix_first_dim']

    print(f"\n  Feature group | L1 norm | per-dim |")
    print(f"  prefix_cat    | {pfx_norm:>8.2f} | {pfx_per_dim:>7.2f}")
    print(f"  e_depth       | {ed_norm:>8.2f} | {ed_per_dim:>7.2f}")
    print(f"  head_atom     | {head_norm:>8.2f} | {head_per_dim:>7.2f}")
    print(f"  term_atom     | {term_norm:>8.2f} | {term_per_dim:>7.2f}")
    print(f"  has_suffix    | {has_suff_norm:>8.2f}")
    print(f"  suffix_first  | {suff_first_norm:>8.2f} | {suff_per_dim:>7.2f}")

    # Crazy-expert's predicted ordering
    ranked = sorted([
        ('HEAD atom', head_per_dim),
        ('e_depth', ed_per_dim),
        ('TERM atom', term_per_dim),
        ('prefix_cat', pfx_per_dim),
        ('suffix_first', suff_per_dim),
    ], key=lambda x: -x[1])
    print(f"\n  Observed ranking (by per-dim importance):")
    for r, (name, val) in enumerate(ranked):
        print(f"    {r+1}. {name}: {val:.2f}")

    # Crazy-expert pre-reg test: if prefix_cat > HEAD by >2x, parametric weakens
    head_vs_pfx_ratio = head_per_dim / pfx_per_dim if pfx_per_dim > 0 else float('inf')
    print(f"\n  Crazy-expert adversarial test:")
    print(f"    HEAD vs prefix_cat ratio: {head_vs_pfx_ratio:.2f}")
    if head_vs_pfx_ratio > 1.0:
        test2_verdict = "HEAD DOMINATES PREFIX (consistent with parametric)"
    elif head_vs_pfx_ratio > 0.5:
        test2_verdict = "HEAD AND PREFIX COMPARABLE (indeterminate)"
    else:
        test2_verdict = "PREFIX DOMINATES HEAD (consistent with class-refinement)"
    print(f"    Verdict: {test2_verdict}")

    # Save
    out = {
        "method": "PHASE_711 follow-up diagnostics — within-class retention + feature importance",
        "test_1_within_class_retention": {
            "results_by_class": within_class_results,
            "mean_edepth_retention_ratio": mean_retention,
            "median_edepth_retention_ratio": median_retention,
            "verdict": test1_verdict,
            "thresholds": {"parametric_lower": 0.50, "refinement_upper": 0.20},
        },
        "test_2_feature_importance": {
            "feature_norms_per_dim": {
                "prefix_cat": pfx_per_dim,
                "e_depth": ed_per_dim,
                "head_atom": head_per_dim,
                "term_atom": term_per_dim,
                "suffix_first": suff_per_dim,
            },
            "feature_norms_total": {
                "prefix_cat": pfx_norm,
                "e_depth": ed_norm,
                "head_atom": head_norm,
                "term_atom": term_norm,
                "has_suffix": has_suff_norm,
                "suffix_first": suff_first_norm,
            },
            "head_vs_prefix_ratio": head_vs_pfx_ratio,
            "verdict": test2_verdict,
            "ranking": [name for name, _ in ranked],
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
