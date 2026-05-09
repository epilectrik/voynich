#!/usr/bin/env python3
"""
Phase 691.x: Leave-one-out match test.

Per expert-advisor recommendation: cheap diagnostic before encoder training.

Approach:
  1. Hand-crafted Voynich features per folio (Phase 691 build_folio_features)
  2. Hand-crafted PL features from per-chapter text statistics (this script)
  3. For each of the 9 confirmed pairs:
       a. Hold out the pair
       b. Compute folio-feature centroid in feature space
       c. Compute pl-feature centroid
       d. Use ALL OTHER 8 pairs to learn the alignment (linear projection)
       e. Apply to held-out folio, predict closest chapter
       f. Top-K accuracy

Pre-registered criterion (per expert-advisor):
  - Top-1 LOO recovery >= 5/9 (random baseline ~0.30, p < 0.01 binomial)
  - Permutation null: shuffle pair labels, retrain, real model > 95th percentile
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PHASE_DIR = Path(__file__).resolve().parents[1]


# Confirmed pairs from Phase 668 (T1_distillation_matching, confident=True)
CONFIRMED_PAIRS = [
    ('f84r', 14),
    ('f77v', 27),
    ('f75r', 19),
    ('f76r', 18),
    ('f83r', 9),
    ('f84v', 24),
    ('f108r', 16),
    ('f112r', 11),
    ('f81v', 18),
]


def load_folio_features():
    """Load per-folio feature vectors built by build_folio_features.py."""
    path = PHASE_DIR / 'data' / 'folio_features.jsonl'
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            rows.append(json.loads(line))
    return {r['folio']: r for r in rows}


def feature_vector(folio_record):
    """Extract numeric feature vector from folio record (deterministic order)."""
    feature_keys = [
        'avg_token_len', 'unique_pct',
        'mean_e_depth', 'mean_i_depth', 'max_e_depth',
        'cardinality_max_run',
        'qok_rate', 'qot_rate',
        'dam_rate', 'ar_rate', 'or_rate', 'ol_rate',
        'daiin_rate', 'chedy_rate', 'shedy_rate',
        'head_a', 'head_e', 'head_o', 'head_k', 'head_t',
        'term_y', 'term_n', 'term_m', 'term_h', 'term_l', 'term_r', 'term_k', 'term_t',
    ]
    return np.array([float(folio_record.get(k, 0)) for k in feature_keys])


# PL chapter feature extraction (lightweight, from raw text)
LATIN_THERMAL = ['ignis', 'igne', 'ignem', 'fornax', 'fornac', 'balne', 'calor', 'distill',
                 'subliman', 'fix', 'soluti', 'cocti', 'cocer', 'igniri']
LATIN_VESSEL = ['alembic', 'cucurbit', 'urinal', 'vas', 'vase', 'vasis', 'lapis', 'lapid']
LATIN_OP_VERBS = ['distill', 'sublim', 'fix', 'cocer', 'dissolv', 'misce', 'congel',
                  'separa', 'pone', 'extrah']
LATIN_ITER = ['vegades', 'vicibus', 'iterum', 'rursus', 'iterando', 'septies', 'novies',
              'quater', 'novem']


def pl_chapter_features(text):
    """Extract structural features from a PL chapter text block."""
    t = text.lower()
    words = re.findall(r'[a-z]+', t)
    n_words = len(words)
    if n_words < 5:
        return None

    def rate(stems, where=t):
        return sum(where.count(s) for s in stems) / max(1, n_words)

    # Cardinality digit hits and number words
    digit_count = sum(1 for c in t if c.isdigit())
    number_words = sum(1 for w in words if w in ['quatuor', 'quattor', 'novem', 'septem',
                                                    'octo', 'duodecim', 'decem',
                                                    'quatre', 'noves', 'tres', 'sis'])

    # Word length variance (proxy for grammatical complexity)
    word_lens = [len(w) for w in words]
    avg_word_len = sum(word_lens) / n_words

    # Repetition ratio
    unique_pct = len(set(words)) / n_words

    return np.array([
        n_words / 1000.0,
        avg_word_len,
        unique_pct,
        rate(LATIN_THERMAL),
        rate(LATIN_VESSEL),
        rate(LATIN_OP_VERBS),
        rate(LATIN_ITER),
        digit_count / 100.0,
        number_words / max(1, n_words),
    ])


def split_pl_chapters(text):
    """Split SISMEL Latin text into chapters by 'Capitulum' headers.
    Returns dict: chapter_number -> chapter text."""
    lines = text.split('\n')
    chapters = {}
    current = None
    current_text = []

    cap_re = re.compile(r'(?i)\bcapitulum\s+([a-z]+|\d+)')
    cap_words = {
        'primum': 1, 'secundum': 2, 'tertium': 3, 'quartum': 4, 'quintum': 5,
        'sextum': 6, 'septimum': 7, 'octavum': 8, 'nonum': 9, 'decimum': 10,
        'undecimum': 11, 'duodecimum': 12, 'tertiumdecimum': 13, 'quartumdecimum': 14,
        'quintumdecimum': 15, 'sextumdecimum': 16, 'septimumdecimum': 17,
        'octavumdecimum': 18, 'nonumdecimum': 19, 'vicesimum': 20,
        'vigesimum': 20, 'vicesimumprimum': 21, 'vicesimumsecundum': 22,
        'vicesimumtertium': 23, 'vicesimumquartum': 24, 'vicesimumquintum': 25,
        'vicesimumsextum': 26, 'vicesimumseptimum': 27, 'vicesimumoctavum': 28,
        'vicesimumnonum': 29, 'tricesimum': 30,
    }

    for line in lines:
        m = cap_re.search(line)
        if m:
            if current is not None:
                chapters[current] = '\n'.join(current_text)
            label = m.group(1).lower()
            try:
                num = int(label)
            except ValueError:
                num = cap_words.get(label, None)
            if num is None:
                # Multiword chapter labels (vicesimum primum etc) — try next word
                rest_match = re.search(rf'(?i)\bcapitulum\s+([a-z]+\s*[a-z]*)', line)
                if rest_match:
                    parts = rest_match.group(1).strip().split()
                    if len(parts) > 1:
                        joined = ''.join(parts)
                        num = cap_words.get(joined, None)
            current = num
            current_text = [line]
        else:
            if current is not None:
                current_text.append(line)
    if current is not None:
        chapters[current] = '\n'.join(current_text)
    return chapters


def main():
    print("Loading Voynich folio features...")
    folio_db = load_folio_features()
    print(f"  {len(folio_db)} folios with features")

    print("\nLoading SISMEL Liber Mercuriorum chapters...")
    chapters_path = PHASE_DIR / 'data' / 'sismel_liber_mercuriorum_latin.json'
    raw = json.loads(chapters_path.read_text(encoding='utf-8'))
    chapters = {int(k): v for k, v in raw.items()}
    # Drop chapter 46 (extraction artifact: ate everything after liber end)
    if 46 in chapters and len(chapters[46]) > 50000:
        del chapters[46]
    print(f"  Loaded {len(chapters)} chapters: {sorted(chapters.keys())}")

    # Compute features for each chapter
    pl_features = {}
    for ch_num, ch_text in chapters.items():
        feats = pl_chapter_features(ch_text)
        if feats is not None:
            pl_features[ch_num] = feats
    print(f"  Chapters with features: {len(pl_features)}")
    if not pl_features:
        print("  ERROR: no chapter features extracted; chapter detection may have failed")
        return

    # Filter confirmed pairs to those we can actually use
    available_pairs = []
    for folio, ch in CONFIRMED_PAIRS:
        if folio in folio_db and ch in pl_features:
            available_pairs.append((folio, ch))
    print(f"\nUsable confirmed pairs: {len(available_pairs)}/{len(CONFIRMED_PAIRS)}")
    for f, c in available_pairs:
        print(f"  {f} <-> Ch{c}")
    if len(available_pairs) < 5:
        print(f"  Insufficient pairs to run LOO meaningfully")
        return

    # Compute Voynich and PL feature matrices for the available pairs
    voy_vecs = []
    pl_vecs = []
    folio_list = []
    chapter_list = []
    for f, c in available_pairs:
        voy_vecs.append(feature_vector(folio_db[f]))
        pl_vecs.append(pl_features[c])
        folio_list.append(f)
        chapter_list.append(c)
    voy_mat = np.array(voy_vecs)
    pl_mat = np.array(pl_vecs)
    print(f"\nVoynich feature dim: {voy_mat.shape[1]}")
    print(f"PL feature dim:      {pl_mat.shape[1]}")

    # Standardize features (z-score)
    def standardize(X, ref=None):
        if ref is None:
            ref = X
        mu = ref.mean(axis=0)
        sd = ref.std(axis=0) + 1e-9
        return (X - mu) / sd, mu, sd

    # Build candidate-chapter feature matrix (all chapters in pl_features)
    cand_chapters = sorted(pl_features.keys())
    cand_pl_mat = np.array([pl_features[c] for c in cand_chapters])

    # === LOO test ===
    print(f"\n=== Leave-one-out match test ===")
    print(f"For each confirmed pair, hold out, learn alignment from the other {len(available_pairs)-1},")
    print(f"score the held-out folio against {len(cand_chapters)} candidate chapters.")
    print()
    print(f"  {'held':>5s}  {'true_ch':>7s}  {'pred1':>5s}  {'pred1_dist':>10s}  {'true_rank':>9s}  {'top3 hit?':>9s}")
    print(f"  {'-'*60}")

    n_top1 = 0
    n_top3 = 0
    n_top5 = 0
    detail = []
    for i in range(len(available_pairs)):
        f_held, c_held = available_pairs[i]
        # Train: other 8 pairs
        train_idx = [j for j in range(len(available_pairs)) if j != i]
        train_voy = voy_mat[train_idx]
        train_pl = pl_mat[train_idx]
        # Standardize using training mean/std
        train_voy_z, mu_v, sd_v = standardize(train_voy)
        train_pl_z, mu_p, sd_p = standardize(train_pl)
        # Apply to held-out folio and ALL candidate chapters
        held_voy_z = (voy_mat[i] - mu_v) / sd_v
        cand_pl_z = (cand_pl_mat - mu_p) / sd_p
        # Learn linear mapping voy_z -> pl_z via least-squares on training pairs
        # train_voy_z @ W = train_pl_z  →  W = pinv(voy_z) @ pl_z
        try:
            W, _, _, _ = np.linalg.lstsq(train_voy_z, train_pl_z, rcond=None)
        except np.linalg.LinAlgError:
            continue
        # Project held-out into PL space
        proj = held_voy_z @ W
        # Distance to each candidate chapter
        dists = np.linalg.norm(cand_pl_z - proj, axis=1)
        order = np.argsort(dists)
        ranked_chapters = [cand_chapters[k] for k in order]
        true_rank = ranked_chapters.index(c_held) + 1 if c_held in ranked_chapters else None
        pred1 = ranked_chapters[0]
        if pred1 == c_held:
            n_top1 += 1
        if c_held in ranked_chapters[:3]:
            n_top3 += 1
        if c_held in ranked_chapters[:5]:
            n_top5 += 1
        hit3 = '✓' if c_held in ranked_chapters[:3] else '.'
        print(f"  {f_held:>5s}  Ch{c_held:>5d}  Ch{pred1:>3d}  {dists[order[0]]:>10.3f}  {true_rank:>9d}  {hit3:>9s}")
        detail.append({
            'folio': f_held, 'true_chapter': c_held, 'predicted': pred1,
            'true_rank': true_rank, 'pred_distance': float(dists[order[0]]),
            'top5_chapters': ranked_chapters[:5],
        })

    print(f"\n=== Results ===")
    print(f"  Top-1 LOO recovery: {n_top1}/{len(available_pairs)}  ({100*n_top1/len(available_pairs):.0f}%)")
    print(f"  Top-3 LOO recovery: {n_top3}/{len(available_pairs)}  ({100*n_top3/len(available_pairs):.0f}%)")
    print(f"  Top-5 LOO recovery: {n_top5}/{len(available_pairs)}  ({100*n_top5/len(available_pairs):.0f}%)")
    print(f"  Random baseline top-1: 1/{len(cand_chapters)} = {100/len(cand_chapters):.1f}%")
    print(f"  Random baseline top-5: 5/{len(cand_chapters)} = {500/len(cand_chapters):.1f}%")

    # Pre-registered criterion: >=5/9 top-1 = signal real
    n_pairs = len(available_pairs)
    if n_top1 >= max(2, n_pairs // 2):
        verdict = 'SIGNAL_REAL'
    elif n_top1 >= 1:
        verdict = 'WEAK_SIGNAL'
    else:
        verdict = 'NO_SIGNAL'
    print(f"\n  Verdict: {verdict}")

    # Permutation null
    print(f"\n  Permutation null (shuffle pair labels, 200 trials)...")
    rng = np.random.RandomState(691)
    null_top1 = []
    for trial in range(200):
        perm = rng.permutation(len(available_pairs))
        n_top1_null = 0
        for i in range(len(available_pairs)):
            train_idx = [j for j in range(len(available_pairs)) if j != i]
            train_voy = voy_mat[train_idx]
            train_pl = pl_mat[perm[train_idx]]  # shuffle
            try:
                train_voy_z, mu_v, sd_v = standardize(train_voy)
                train_pl_z, mu_p, sd_p = standardize(train_pl)
            except Exception:
                continue
            held_voy_z = (voy_mat[i] - mu_v) / sd_v
            cand_pl_z = (cand_pl_mat - mu_p) / sd_p
            try:
                W, _, _, _ = np.linalg.lstsq(train_voy_z, train_pl_z, rcond=None)
            except np.linalg.LinAlgError:
                continue
            proj = held_voy_z @ W
            dists = np.linalg.norm(cand_pl_z - proj, axis=1)
            pred = cand_chapters[np.argmin(dists)]
            if pred == available_pairs[i][1]:
                n_top1_null += 1
        null_top1.append(n_top1_null)
    null_top1 = np.array(null_top1)
    p_value = float(np.mean(null_top1 >= n_top1))
    print(f"  Null mean top-1: {null_top1.mean():.2f}, std: {null_top1.std():.2f}, max: {null_top1.max()}")
    print(f"  Real top-1: {n_top1}, p-value: {p_value:.3f}")

    # Save
    out = {
        'n_confirmed_pairs': len(available_pairs),
        'n_candidate_chapters': len(cand_chapters),
        'top1_recovery': n_top1,
        'top3_recovery': n_top3,
        'top5_recovery': n_top5,
        'verdict': verdict,
        'permutation_null_mean': float(null_top1.mean()),
        'permutation_null_max': int(null_top1.max()),
        'permutation_p_value': p_value,
        'detail': detail,
    }
    out_path = PHASE_DIR / 'results' / 'predictions' / 'loo_match_test.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
