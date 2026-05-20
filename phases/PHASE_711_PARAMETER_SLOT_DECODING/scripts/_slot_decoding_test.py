"""PHASE_711: Parameter-slot decoding predictivity test.

Does atom-level slot decomposition add predictive information about next-instruction-class
beyond what the current 49-class label already captures?

Pre-registered in PHASE_711 INDEX.md. Decision rules locked before any model training.
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

OUT_PATH = ROOT / 'phases' / 'PHASE_711_PARAMETER_SLOT_DECODING' / 'results' / 'slot_decoding_results.json'

random.seed(42)
np.random.seed(42)


# ---- Feature extraction ----

PREFIX_CATEGORIES = {
    'ch': 'ch', 'sh': 'sh', 'qo': 'qo', 'ok': 'ok', 'ot': 'ot',
    'ol': 'ol', 'ct': 'ct', 'da': 'da',
}

HEAD_ATOMS = set('aeokt')
TERM_ATOMS = set('ynmhlrkt')


def categorize_prefix(prefix):
    if prefix is None or prefix == '':
        return 'NONE'
    if prefix in PREFIX_CATEGORIES:
        return PREFIX_CATEGORIES[prefix]
    return 'EXTENDED'


def extract_slot_features(token, morph_obj):
    """Extract slot-decomposition features for one token.

    Returns dict of features.
    """
    if not token:
        return None
    try:
        m = morph_obj.extract(token)
        a = morph_obj.atomize(token)
    except Exception:
        return None

    middle = m.middle or ''
    prefix = m.prefix or ''
    suffix = m.suffix or ''

    # e-depth: count of 'e' atoms in MIDDLE (capped at 3+)
    e_count = middle.count('e')
    e_depth = min(e_count, 3)

    # HEAD atom (first atom of middle, after prefix)
    head_atom = 'NONE'
    if middle:
        if middle[0] in HEAD_ATOMS:
            head_atom = middle[0]
        else:
            head_atom = 'PSEUDO_HEAD'

    # TERM atom (last atom of middle)
    term_atom = 'NONE'
    if middle and middle[-1] in TERM_ATOMS:
        term_atom = middle[-1]

    # Suffix
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


# ---- Build data ----

def build_pairs():
    """Build (current_token, slot_features, current_class, next_class, folio) records.
    Only within-line adjacent pairs, both tokens classified.
    """
    print("Loading Currier B P-placement tokens...")
    tx = Transcript()
    morph = Morphology()

    class_map = json.loads(
        (ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json').read_text(encoding='utf-8')
    )['token_to_class']

    # Group by (folio, line)
    lines = defaultdict(list)
    for t in tx.all(h_only=True):
        if not t.word.strip() or '*' in t.word:
            continue
        if t.language != 'B':
            continue
        if not (t.placement and t.placement.startswith('P')):
            continue
        # Use folio + line as key; we need a line identifier
        line_key = (t.folio, t.line)
        lines[line_key].append(t)

    print(f"  N lines: {len(lines)}")

    # Build within-line pairs (both classified)
    pairs = []
    total_tokens = 0
    classified_tokens = 0
    for (folio, line), toks in lines.items():
        # Sort by token position (already in order)
        for i in range(len(toks) - 1):
            cur, nxt = toks[i], toks[i + 1]
            cur_word = cur.word.lower()
            nxt_word = nxt.word.lower()
            total_tokens += 1
            if cur_word not in class_map or nxt_word not in class_map:
                continue
            classified_tokens += 1
            slot_feats = extract_slot_features(cur_word, morph)
            if slot_feats is None:
                continue
            pairs.append({
                'folio': folio,
                'line': line,
                'cur_word': cur_word,
                'cur_class': class_map[cur_word],
                'next_class': class_map[nxt_word],
                **slot_feats,
            })
    print(f"  Total within-line adjacent pairs: {total_tokens}")
    print(f"  Both classified pairs: {classified_tokens}")
    print(f"  With slot features extracted: {len(pairs)}")
    return pairs


# ---- One-hot encoder ----

def one_hot_features(pairs):
    """Convert features to one-hot matrices.
    Returns (X_class, X_class_plus_slot, y, folios) numpy arrays.
    """
    # Get all unique values per feature
    cur_classes = sorted(set(p['cur_class'] for p in pairs))
    next_classes = sorted(set(p['next_class'] for p in pairs))
    prefix_cats = sorted(set(p['prefix_cat'] for p in pairs))
    head_atoms = sorted(set(p['head_atom'] for p in pairs))
    term_atoms = sorted(set(p['term_atom'] for p in pairs))
    suffix_firsts = sorted(set(p['suffix_first'] for p in pairs))

    n = len(pairs)
    n_cur_cls = len(cur_classes)
    cur_cls_idx = {c: i for i, c in enumerate(cur_classes)}
    nxt_cls_idx = {c: i for i, c in enumerate(next_classes)}

    pfx_idx = {v: i for i, v in enumerate(prefix_cats)}
    head_idx = {v: i for i, v in enumerate(head_atoms)}
    term_idx = {v: i for i, v in enumerate(term_atoms)}
    suff_idx = {v: i for i, v in enumerate(suffix_firsts)}

    # X_class: one-hot of current class only
    X_class = np.zeros((n, n_cur_cls), dtype=np.float32)
    # X_slot: class one-hot + slot features
    n_slot_dim = n_cur_cls + len(prefix_cats) + 4 + len(head_atoms) + len(term_atoms) + 1 + len(suffix_firsts)
    # e_depth as 4-dim one-hot (0,1,2,3+)
    X_slot = np.zeros((n, n_slot_dim), dtype=np.float32)
    y = np.zeros(n, dtype=np.int32)
    folios = []

    for i, p in enumerate(pairs):
        ci = cur_cls_idx[p['cur_class']]
        X_class[i, ci] = 1.0
        X_slot[i, ci] = 1.0
        off = n_cur_cls
        X_slot[i, off + pfx_idx[p['prefix_cat']]] = 1.0
        off += len(prefix_cats)
        X_slot[i, off + p['e_depth']] = 1.0
        off += 4
        X_slot[i, off + head_idx[p['head_atom']]] = 1.0
        off += len(head_atoms)
        X_slot[i, off + term_idx[p['term_atom']]] = 1.0
        off += len(term_atoms)
        X_slot[i, off] = float(p['has_suffix'])
        off += 1
        X_slot[i, off + suff_idx[p['suffix_first']]] = 1.0
        y[i] = nxt_cls_idx[p['next_class']]
        folios.append(p['folio'])

    return X_class, X_slot, y, np.array(folios), cur_classes, next_classes


# ---- Models ----

def class_only_baseline(X_class_train, y_train, X_class_test, n_next_classes, alpha=0.1):
    """Empirical P(next_class | current_class) with Laplace smoothing.

    X_class_train: (n, n_cur_classes) one-hot
    Returns: predicted prob matrix (n_test, n_next_classes)
    """
    n_cur = X_class_train.shape[1]
    # Transition counts
    counts = np.zeros((n_cur, n_next_classes), dtype=np.float64)
    cur_idx = X_class_train.argmax(axis=1)
    for i in range(len(y_train)):
        counts[cur_idx[i], y_train[i]] += 1
    counts += alpha  # Laplace smoothing
    counts /= counts.sum(axis=1, keepdims=True)

    cur_idx_test = X_class_test.argmax(axis=1)
    return counts[cur_idx_test]


def slot_model_predict(X_train, y_train, X_test, n_next_classes):
    """Multinomial logistic regression with L2 regularization — calibrated probabilities."""
    from sklearn.linear_model import LogisticRegression
    clf = LogisticRegression(
        penalty='l2', C=1.0, solver='lbfgs', max_iter=1000,
        multi_class='multinomial', random_state=42,
    )
    clf.fit(X_train, y_train)
    proba = clf.predict_proba(X_test)
    aligned = np.full((proba.shape[0], n_next_classes), 1e-9)
    for j, cls in enumerate(clf.classes_):
        aligned[:, cls] = proba[:, j]
    aligned /= aligned.sum(axis=1, keepdims=True)
    return aligned


def class_only_logreg_baseline(X_class_train, y_train, X_class_test, n_next_classes):
    """SAME architecture as slot model, only class features. Apples-to-apples CE comparison."""
    return slot_model_predict(X_class_train, y_train, X_class_test, n_next_classes)


def cross_entropy(y_true, proba):
    """Bits per prediction."""
    eps = 1e-9
    p = proba[np.arange(len(y_true)), y_true].clip(eps, 1.0)
    return -np.mean(np.log2(p))


def top_k_accuracy(y_true, proba, k=1):
    top_k = np.argsort(-proba, axis=1)[:, :k]
    return np.mean([y_true[i] in top_k[i] for i in range(len(y_true))])


# ---- Main evaluation ----

def run_fold(fold_idx, train_idx, test_idx, X_class, X_slot, y, n_next_classes):
    """Run one CV fold. Returns dict of metrics for each model."""
    X_cls_tr, X_cls_te = X_class[train_idx], X_class[test_idx]
    X_slo_tr, X_slo_te = X_slot[train_idx], X_slot[test_idx]
    y_tr, y_te = y[train_idx], y[test_idx]

    # Baseline (Markov empirical — calibrated reference)
    p_base = class_only_baseline(X_cls_tr, y_tr, X_cls_te, n_next_classes)
    ce_base = cross_entropy(y_te, p_base)
    acc1_base = top_k_accuracy(y_te, p_base, 1)
    acc3_base = top_k_accuracy(y_te, p_base, 3)

    # Baseline2 (LogReg class-only — SAME architecture as slot, apples-to-apples)
    p_base2 = class_only_logreg_baseline(X_cls_tr, y_tr, X_cls_te, n_next_classes)
    ce_base2 = cross_entropy(y_te, p_base2)
    acc1_base2 = top_k_accuracy(y_te, p_base2, 1)
    acc3_base2 = top_k_accuracy(y_te, p_base2, 3)

    # Slot model
    p_slot = slot_model_predict(X_slo_tr, y_tr, X_slo_te, n_next_classes)
    ce_slot = cross_entropy(y_te, p_slot)
    acc1_slot = top_k_accuracy(y_te, p_slot, 1)
    acc3_slot = top_k_accuracy(y_te, p_slot, 3)

    # Shuffle control: shuffle the SLOT-only portion of X_slot in train
    n_cur = X_class.shape[1]
    X_slo_tr_shuf = X_slo_tr.copy()
    perm = np.random.permutation(len(X_slo_tr_shuf))
    # Shuffle only the slot portion (after class one-hot)
    X_slo_tr_shuf[:, n_cur:] = X_slo_tr_shuf[perm, n_cur:]
    p_shuf = slot_model_predict(X_slo_tr_shuf, y_tr, X_slo_te, n_next_classes)
    ce_shuf = cross_entropy(y_te, p_shuf)
    acc1_shuf = top_k_accuracy(y_te, p_shuf, 1)
    acc3_shuf = top_k_accuracy(y_te, p_shuf, 3)

    return {
        'fold': fold_idx,
        'n_test': len(y_te),
        'ce_baseline': ce_base, 'acc1_baseline': acc1_base, 'acc3_baseline': acc3_base,
        'ce_baseline_logreg': ce_base2, 'acc1_baseline_logreg': acc1_base2, 'acc3_baseline_logreg': acc3_base2,
        'ce_slot': ce_slot, 'acc1_slot': acc1_slot, 'acc3_slot': acc3_slot,
        'ce_shuffle': ce_shuf, 'acc1_shuffle': acc1_shuf, 'acc3_shuffle': acc3_shuf,
    }


def main():
    print("=" * 90)
    print("PHASE_711 PARAMETER-SLOT DECODING PREDICTIVITY TEST")
    print("=" * 90)

    pairs = build_pairs()
    if len(pairs) < 1000:
        print("Insufficient pairs; aborting")
        return

    X_class, X_slot, y, folios, cur_classes, next_classes = one_hot_features(pairs)
    n_next_classes = len(next_classes)
    print(f"\n  Feature dims: class-only={X_class.shape[1]}, slot={X_slot.shape[1]}")
    print(f"  N next classes: {n_next_classes}")

    # 5-fold folio-out CV
    unique_folios = sorted(set(folios))
    n_folios = len(unique_folios)
    print(f"  N folios: {n_folios}")
    rng = np.random.default_rng(42)
    folio_perm = rng.permutation(unique_folios)
    folio_folds = np.array_split(folio_perm, 5)

    fold_results = []
    for fold_idx, test_folios in enumerate(folio_folds):
        test_folio_set = set(test_folios)
        test_mask = np.array([f in test_folio_set for f in folios])
        train_idx = np.where(~test_mask)[0]
        test_idx = np.where(test_mask)[0]
        print(f"\n  Fold {fold_idx+1}/5: train={len(train_idx)}, test={len(test_idx)}, "
              f"test_folios={len(test_folios)}")
        result = run_fold(fold_idx, train_idx, test_idx, X_class, X_slot, y, n_next_classes)
        print(f"    Baseline(Markov):  CE={result['ce_baseline']:.4f}  acc1={result['acc1_baseline']:.4f}  acc3={result['acc3_baseline']:.4f}")
        print(f"    Baseline(LogReg):  CE={result['ce_baseline_logreg']:.4f}  acc1={result['acc1_baseline_logreg']:.4f}  acc3={result['acc3_baseline_logreg']:.4f}")
        print(f"    Slot:              CE={result['ce_slot']:.4f}  acc1={result['acc1_slot']:.4f}  acc3={result['acc3_slot']:.4f}")
        print(f"    Shuffle:           CE={result['ce_shuffle']:.4f}  acc1={result['acc1_shuffle']:.4f}  acc3={result['acc3_shuffle']:.4f}")
        fold_results.append(result)

    # Aggregate
    def agg(key):
        return float(np.mean([r[key] for r in fold_results]))

    mean_ce_base = agg('ce_baseline')
    mean_ce_base2 = agg('ce_baseline_logreg')
    mean_ce_slot = agg('ce_slot')
    mean_ce_shuf = agg('ce_shuffle')
    mean_acc1_base = agg('acc1_baseline')
    mean_acc1_base2 = agg('acc1_baseline_logreg')
    mean_acc1_slot = agg('acc1_slot')
    mean_acc1_shuf = agg('acc1_shuffle')

    # Primary verdict: apples-to-apples comparison (slot LogReg vs class-only LogReg)
    ce_improvement = mean_ce_base2 - mean_ce_slot  # positive = slot better
    shuf_improvement = mean_ce_base2 - mean_ce_shuf
    real_gain = mean_ce_shuf - mean_ce_slot  # slot beating shuffle (both same architecture)

    print("\n" + "=" * 90)
    print("AGGREGATE RESULTS (5-fold mean)")
    print("=" * 90)
    print(f"\n  Cross-entropy (bits/pred, lower is better):")
    print(f"    Baseline Markov (reference):   {mean_ce_base:.4f}")
    print(f"    Baseline LogReg class-only:    {mean_ce_base2:.4f}  (apples-to-apples vs slot)")
    print(f"    Slot LogReg:                   {mean_ce_slot:.4f}  (Δ vs LR baseline: {-ce_improvement:+.4f})")
    print(f"    Shuffle (LR slot-shuffled):    {mean_ce_shuf:.4f}  (Δ vs LR baseline: {-shuf_improvement:+.4f})")
    print(f"    Slot - Shuffle gap:            {real_gain:+.4f} bits (positive = slot beats shuffle)")

    print(f"\n  Top-1 accuracy:")
    print(f"    Baseline Markov:               {mean_acc1_base:.4f}")
    print(f"    Baseline LogReg class-only:    {mean_acc1_base2:.4f}")
    print(f"    Slot LogReg:                   {mean_acc1_slot:.4f}  (Δ vs LR baseline: {mean_acc1_slot-mean_acc1_base2:+.4f})")
    print(f"    Shuffle:                       {mean_acc1_shuf:.4f}  (Δ vs LR baseline: {mean_acc1_shuf-mean_acc1_base2:+.4f})")

    # Decision (pre-registered)
    print("\n" + "=" * 90)
    print("VERDICT EVALUATION (pre-registered)")
    print("=" * 90)

    ce_thresh = 0.05
    shuf_diff_thresh = 0.04

    slot_beats_baseline = ce_improvement >= ce_thresh
    slot_beats_shuffle = real_gain >= shuf_diff_thresh

    if slot_beats_baseline and slot_beats_shuffle:
        verdict = "PARAMETER-SLOT INFORMATIVE"
        rationale = (f"Slot model improves CE by {ce_improvement:.4f} bits (≥{ce_thresh} threshold) "
                     f"AND beats shuffle by {real_gain:.4f} bits (≥{shuf_diff_thresh} threshold). "
                     f"Atom-level slot features carry forward-predictive information beyond class label.")
    elif slot_beats_baseline and not slot_beats_shuffle:
        verdict = "OVERFITTING"
        rationale = (f"Slot model improves CE by {ce_improvement:.4f} bits but shuffle control "
                     f"also improves by {shuf_improvement:.4f}. Real gain only {real_gain:.4f} bits "
                     f"(below {shuf_diff_thresh} threshold). Gain is memorization, not informative.")
    elif ce_improvement < 0:
        verdict = "PATHOLOGICAL"
        rationale = f"Slot model DEGRADES CE by {-ce_improvement:.4f} bits. Test broken."
    else:
        verdict = "SLOT FEATURES NOT INFORMATIVE"
        rationale = (f"Slot model improves CE by only {ce_improvement:.4f} bits (below {ce_thresh} threshold). "
                     f"Atom identity adds no significant forward-predictive value beyond class label.")

    print(f"\n  VERDICT: {verdict}")
    print(f"  Rationale: {rationale}")

    out = {
        "method": "PHASE_711 parameter-slot decoding predictivity test",
        "n_pairs": len(pairs),
        "n_folios": n_folios,
        "n_classes_current": len(cur_classes),
        "n_classes_next": n_next_classes,
        "feature_dim_class_only": int(X_class.shape[1]),
        "feature_dim_slot": int(X_slot.shape[1]),
        "fold_results": fold_results,
        "aggregate": {
            "ce_baseline": mean_ce_base,
            "ce_slot": mean_ce_slot,
            "ce_shuffle": mean_ce_shuf,
            "ce_improvement_slot_vs_baseline": ce_improvement,
            "ce_improvement_shuffle_vs_baseline": shuf_improvement,
            "real_gain_slot_minus_shuffle": real_gain,
            "acc1_baseline": mean_acc1_base,
            "acc1_slot": mean_acc1_slot,
            "acc1_shuffle": mean_acc1_shuf,
        },
        "thresholds": {"ce_improvement": ce_thresh, "shuf_diff": shuf_diff_thresh},
        "verdict": verdict,
        "rationale": rationale,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
