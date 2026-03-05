#!/usr/bin/env python3
"""
Phase 512: PARAGRAPH_STATE_DEPENDENT_ORDERING

Tests whether paragraph ordering within folios is STATE-DEPENDENT rather than
POSITION-DEPENDENT. Phase 511 showed no fixed ordering (no thermal-first ramp),
but zone inertia exists (self-transition O/E=2.02). The hypothesis: what comes
next depends on the physical state at the END of the current paragraph, not on
a predetermined sequence.

Uses Phase 510 zone labels (4 gradient zones from paragraph program typing).
Computes terminal state features from last 2 body lines of each paragraph.
Tests whether terminal state predicts the zone of the NEXT paragraph.

Output: phases/PARAGRAPH_STATE_DEPENDENT_ORDERING/results/state_dependent_ordering.json
"""

import sys
import os
import json
import numpy as np
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scripts.voynich import Transcript, Morphology
from scipy.stats import spearmanr, chi2_contingency, mannwhitneyu, kruskal
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# ============================================================
# ATOM-CATEGORY MAPPING (from Phase 510, C1250, C1195)
# ============================================================
ATOM_CATEGORY = {
    'k': 'THERMAL', 'e': 'THERMAL', 'h': 'MONITORING',
    'd': 'CONTAINMENT', 't': 'TRANSITION', 'y': 'CONTAINMENT',
    'n': 'OPERATION', 'i': 'OPERATION', 'a': 'STAGING',
    'm': 'MARKING', 'l': 'FLOW', 'o': 'STAGING',
    'r': 'FLOW', 'c': 'MONITORING', 'p': 'MARKING',
    's': 'STAGING', 'f': 'MARKING', 'q': 'THERMAL',
    'g': 'OPERATION', 'x': 'OPERATION',
}

CATEGORIES = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
              'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']

MODE_A_SUFFIXES = {'edy', 'dy', 'ey', 'eey', 'y', 'hy', 'ly', 'ry',
                   'chy', 'shy', 'ky', 'oky', 'oty'}

ZONE_NAMES = {
    0: 'THERMAL-QO',
    1: 'CONTAINMENT-Sealing',
    2: 'OPERATION-Iteration',
    3: 'MONITORING-Phase',
}

SECTION_NAMES = {
    'H': 'HERBAL', 'B': 'BIO', 'S': 'STARS_RECIPE',
    'C': 'COSMO', 'T': 'PHARMA'
}


def assign_category(middle):
    """Assign operational category to a MIDDLE via atom plurality vote."""
    if not middle:
        return None
    votes = Counter()
    for ch in middle:
        cat = ATOM_CATEGORY.get(ch)
        if cat:
            votes[cat] += 1
    if not votes:
        return None
    return votes.most_common(1)[0][0]


def compute_features_for_tokens(morphs):
    """Compute state features from a set of morphology extractions."""
    n = len(morphs)
    if n == 0:
        return None

    # Category profile (8 features)
    cat_counts = Counter()
    for m in morphs:
        cat = assign_category(m.middle)
        if cat:
            cat_counts[cat] += 1
    cat_total = sum(cat_counts.values()) or 1
    cat_fracs = {c: cat_counts.get(c, 0) / cat_total for c in CATEGORIES}

    # Kernel profile
    k_count = sum(1 for m in morphs if m.middle and 'k' in m.middle)
    e_count = sum(1 for m in morphs if m.middle and 'e' in m.middle)
    h_count = sum(1 for m in morphs if m.middle and 'h' in m.middle)

    # PREFIX channels
    qo_count = sum(1 for m in morphs if m.prefix and m.prefix.startswith('qo'))
    chsh_count = sum(1 for m in morphs if m.prefix and
                     (m.prefix.startswith('ch') or m.prefix.startswith('sh')))
    bare_count = sum(1 for m in morphs if not m.prefix)

    # Headless fraction (compound MIDDLEs with non-standard initial)
    compounds = [m for m in morphs if m.middle and len(m.middle) >= 2]
    n_headless = sum(1 for m in compounds
                     if m.middle[0] not in {'a', 'e', 'o', 'k', 't'})
    headless_frac = n_headless / len(compounds) if compounds else 0.0

    # Suffix mode
    mode_a_count = 0
    for m in morphs:
        if m.suffix and m.suffix in MODE_A_SUFFIXES:
            mode_a_count += 1
        elif m.suffix:
            mode_a_count += 1  # Any suffix = Mode A per Phase 510 logic
    bare_suffix_frac = sum(1 for m in morphs if not m.suffix) / n

    # dy fraction
    dy_count = sum(1 for m in morphs if m.middle == 'dy')

    return {
        # Category profile
        **cat_fracs,
        # Kernel
        'k_frac': k_count / n,
        'e_frac': e_count / n,
        'h_frac': h_count / n,
        # PREFIX channels
        'qo_frac': qo_count / n,
        'chsh_frac': chsh_count / n,
        'bare_frac': bare_count / n,
        # Other
        'headless_frac': headless_frac,
        'bare_suffix_frac': bare_suffix_frac,
        'dy_frac': dy_count / n,
    }


def main():
    print("=" * 70)
    print("Phase 512: PARAGRAPH_STATE_DEPENDENT_ORDERING")
    print("=" * 70)

    # ============================================================
    # STEP 1: Load Phase 510 paragraph labels and zone assignments
    # ============================================================
    p510_path = os.path.join(os.path.dirname(__file__), '..', '..',
                             'PARAGRAPH_PROGRAM_TYPING', 'results',
                             'paragraph_program_typing.json')
    with open(p510_path) as f:
        p510 = json.load(f)

    par_labels = p510['paragraph_labels']
    print(f"Phase 510 paragraph labels loaded: {len(par_labels)} paragraphs")

    # Build lookup: (folio, par_idx) -> zone
    zone_lookup = {}
    for pl in par_labels:
        key = (pl['folio'], pl['par_idx'])
        zone_lookup[key] = pl['cluster']  # cluster = zone (0-3)

    # ============================================================
    # STEP 2: Load transcript, build paragraphs, compute features
    # ============================================================
    tx = Transcript()
    morph = Morphology()
    tokens = list(tx.currier_b())
    print(f"Total Currier B tokens: {len(tokens)}")

    # Group tokens by folio
    folio_tokens = defaultdict(list)
    for t in tokens:
        folio_tokens[t.folio].append(t)

    # Sort within each folio by line
    for folio in folio_tokens:
        folio_tokens[folio].sort(key=lambda t: (t.line, 0))

    # Build paragraphs using par_initial markers (same as Phase 510)
    all_paragraphs = []
    for folio, toks in sorted(folio_tokens.items()):
        par_idx = 0
        current_par = []
        for t in toks:
            if t.par_initial and current_par:
                all_paragraphs.append({
                    'folio': folio,
                    'par_idx': par_idx,
                    'tokens': current_par,
                    'section': current_par[0].section,
                })
                par_idx += 1
                current_par = [t]
            else:
                current_par.append(t)
        if current_par:
            all_paragraphs.append({
                'folio': folio,
                'par_idx': par_idx,
                'tokens': current_par,
                'section': current_par[0].section,
            })

    print(f"Total paragraphs built: {len(all_paragraphs)}")

    # Match with Phase 510 zone labels
    matched = 0
    for par in all_paragraphs:
        key = (par['folio'], par['par_idx'])
        if key in zone_lookup:
            par['zone'] = zone_lookup[key]
            matched += 1
        else:
            par['zone'] = None

    print(f"Matched with Phase 510 zones: {matched}")

    # For each matched paragraph, compute line structure
    for par in all_paragraphs:
        lines = sorted(set(t.line for t in par['tokens']))
        par['lines'] = lines
        par['n_lines'] = len(lines)

    # ============================================================
    # STEP 3: Compute terminal state features (last 2 body lines)
    # and initial state features (first 2 body lines)
    # ============================================================
    print("\nComputing terminal and initial state features...")

    for par in all_paragraphs:
        if par['zone'] is None:
            par['terminal_features'] = None
            par['initial_features'] = None
            continue

        lines = par['lines']
        if len(lines) < 2:
            par['terminal_features'] = None
            par['initial_features'] = None
            continue

        # Body lines = all except the first (header)
        body_lines = lines[1:]
        if len(body_lines) == 0:
            par['terminal_features'] = None
            par['initial_features'] = None
            continue

        # Terminal: last 2 body lines (or last 1 if only 1 body line)
        terminal_lines = set(body_lines[-2:]) if len(body_lines) >= 2 else set(body_lines[-1:])

        # Initial: first 2 body lines
        initial_lines = set(body_lines[:2]) if len(body_lines) >= 2 else set(body_lines[:1])

        # Extract morphology for terminal tokens
        terminal_morphs = []
        initial_morphs = []
        for t in par['tokens']:
            w = t.word.strip()
            if not w or '*' in w:
                continue
            try:
                m = morph.extract(w)
            except Exception:
                continue
            if t.line in terminal_lines:
                terminal_morphs.append(m)
            if t.line in initial_lines:
                initial_morphs.append(m)

        par['terminal_features'] = compute_features_for_tokens(terminal_morphs)
        par['initial_features'] = compute_features_for_tokens(initial_morphs)

    # ============================================================
    # STEP 4: Build consecutive paragraph pairs
    # ============================================================
    # Group paragraphs by folio, filter to those with zones and features
    folio_pars = defaultdict(list)
    for par in all_paragraphs:
        if par['zone'] is not None and par['terminal_features'] is not None:
            folio_pars[par['folio']].append(par)

    # Sort by par_idx within each folio
    for f in folio_pars:
        folio_pars[f].sort(key=lambda p: p['par_idx'])

    # Build pairs
    pairs = []
    for folio, pars in sorted(folio_pars.items()):
        for i in range(len(pars) - 1):
            p_curr = pars[i]
            p_next = pars[i + 1]
            if p_next.get('initial_features') is not None:
                pairs.append({
                    'folio': folio,
                    'section': p_curr['section'],
                    'curr_zone': p_curr['zone'],
                    'next_zone': p_next['zone'],
                    'curr_terminal': p_curr['terminal_features'],
                    'next_initial': p_next['initial_features'],
                    'is_cross_zone': p_curr['zone'] != p_next['zone'],
                })

    n_pairs = len(pairs)
    n_cross = sum(1 for p in pairs if p['is_cross_zone'])
    n_same = n_pairs - n_cross
    print(f"\nConsecutive paragraph pairs: {n_pairs}")
    print(f"  Same-zone: {n_same} ({100*n_same/n_pairs:.1f}%)")
    print(f"  Cross-zone: {n_cross} ({100*n_cross/n_pairs:.1f}%)")

    # ============================================================
    # FEATURE NAMES for state vectors
    # ============================================================
    kernel_features = ['k_frac', 'e_frac', 'h_frac']
    category_features = CATEGORIES
    all_state_features = (category_features +
                          ['k_frac', 'e_frac', 'h_frac',
                           'qo_frac', 'chsh_frac', 'bare_frac',
                           'headless_frac', 'bare_suffix_frac', 'dy_frac'])

    def pair_to_kernel_vector(pair):
        tf = pair['curr_terminal']
        return [tf[f] for f in kernel_features]

    def pair_to_category_vector(pair):
        tf = pair['curr_terminal']
        return [tf[f] for f in category_features]

    def pair_to_full_vector(pair):
        tf = pair['curr_terminal']
        return [tf[f] for f in all_state_features]

    # ============================================================
    # T1: Terminal Kernel State -> Next Zone
    # ============================================================
    print("\n" + "=" * 70)
    print("T1: TERMINAL KERNEL STATE -> NEXT ZONE")
    print("=" * 70)

    X_kernel = np.array([pair_to_kernel_vector(p) for p in pairs])
    y_next_zone = np.array([p['next_zone'] for p in pairs])

    # Baseline: most frequent zone per folio
    folio_mode_zone = {}
    for f, pars_list in folio_pars.items():
        zones = [p['zone'] for p in pars_list]
        folio_mode_zone[f] = Counter(zones).most_common(1)[0][0]

    baseline_preds = np.array([folio_mode_zone[p['folio']] for p in pairs])
    baseline_acc = accuracy_score(y_next_zone, baseline_preds)

    # Overall most frequent zone baseline
    overall_mode = Counter(y_next_zone).most_common(1)[0][0]
    overall_baseline = accuracy_score(y_next_zone, [overall_mode] * len(y_next_zone))

    # Logistic regression with cross-validation
    scaler_k = StandardScaler()
    X_kernel_s = scaler_k.fit_transform(X_kernel)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

    lr_kernel = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
    lr_kernel_scores = cross_val_score(lr_kernel, X_kernel_s, y_next_zone,
                                       cv=cv, scoring='accuracy')

    rf_kernel = RandomForestClassifier(n_estimators=100, random_state=RANDOM_SEED,
                                        max_depth=3)
    rf_kernel_scores = cross_val_score(rf_kernel, X_kernel_s, y_next_zone,
                                        cv=cv, scoring='accuracy')

    print(f"  N pairs: {n_pairs}")
    print(f"  Overall mode baseline: {overall_baseline:.4f}")
    print(f"  Folio-mode baseline: {baseline_acc:.4f}")
    print(f"  Logistic Regression (kernel): {lr_kernel_scores.mean():.4f} "
          f"+/- {lr_kernel_scores.std():.4f}")
    print(f"  Random Forest (kernel): {rf_kernel_scores.mean():.4f} "
          f"+/- {rf_kernel_scores.std():.4f}")

    t1_verdict = "STATE_PREDICTIVE" if lr_kernel_scores.mean() > baseline_acc + 0.03 else "NOT_PREDICTIVE"
    print(f"  Verdict: {t1_verdict}")

    t1_results = {
        'n_pairs': n_pairs,
        'overall_mode_baseline': float(overall_baseline),
        'folio_mode_baseline': float(baseline_acc),
        'lr_kernel_mean': float(lr_kernel_scores.mean()),
        'lr_kernel_std': float(lr_kernel_scores.std()),
        'lr_kernel_folds': [float(x) for x in lr_kernel_scores],
        'rf_kernel_mean': float(rf_kernel_scores.mean()),
        'rf_kernel_std': float(rf_kernel_scores.std()),
        'rf_kernel_folds': [float(x) for x in rf_kernel_scores],
        'verdict': t1_verdict,
    }

    # ============================================================
    # T2: Terminal Category Profile -> Next Zone
    # ============================================================
    print("\n" + "=" * 70)
    print("T2: TERMINAL CATEGORY PROFILE -> NEXT ZONE")
    print("=" * 70)

    X_cat = np.array([pair_to_category_vector(p) for p in pairs])
    scaler_c = StandardScaler()
    X_cat_s = scaler_c.fit_transform(X_cat)

    lr_cat = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
    lr_cat_scores = cross_val_score(lr_cat, X_cat_s, y_next_zone,
                                     cv=cv, scoring='accuracy')

    rf_cat = RandomForestClassifier(n_estimators=100, random_state=RANDOM_SEED,
                                      max_depth=3)
    rf_cat_scores = cross_val_score(rf_cat, X_cat_s, y_next_zone,
                                      cv=cv, scoring='accuracy')

    print(f"  Logistic Regression (category): {lr_cat_scores.mean():.4f} "
          f"+/- {lr_cat_scores.std():.4f}")
    print(f"  Random Forest (category): {rf_cat_scores.mean():.4f} "
          f"+/- {rf_cat_scores.std():.4f}")

    t2_verdict = "STATE_PREDICTIVE" if lr_cat_scores.mean() > baseline_acc + 0.03 else "NOT_PREDICTIVE"
    print(f"  Verdict: {t2_verdict}")

    t2_results = {
        'lr_category_mean': float(lr_cat_scores.mean()),
        'lr_category_std': float(lr_cat_scores.std()),
        'lr_category_folds': [float(x) for x in lr_cat_scores],
        'rf_category_mean': float(rf_cat_scores.mean()),
        'rf_category_std': float(rf_cat_scores.std()),
        'rf_category_folds': [float(x) for x in rf_cat_scores],
        'verdict': t2_verdict,
    }

    # ============================================================
    # T3: Cross-Zone Transition State Prediction
    # ============================================================
    print("\n" + "=" * 70)
    print("T3: CROSS-ZONE TRANSITION STATE PREDICTION")
    print("=" * 70)

    cross_pairs = [p for p in pairs if p['is_cross_zone']]
    n_cross_pairs = len(cross_pairs)
    print(f"  Cross-zone pairs: {n_cross_pairs}")

    if n_cross_pairs >= 20:
        X_cross = np.array([pair_to_full_vector(p) for p in cross_pairs])
        y_cross = np.array([p['next_zone'] for p in cross_pairs])

        # Baseline for cross-zone transitions
        cross_mode = Counter(y_cross).most_common(1)[0][0]
        cross_baseline = accuracy_score(y_cross, [cross_mode] * len(y_cross))

        scaler_cross = StandardScaler()
        X_cross_s = scaler_cross.fit_transform(X_cross)

        # Use fewer folds if small N
        n_folds = min(5, min(Counter(y_cross).values()))
        if n_folds < 2:
            n_folds = 2

        cv_cross = StratifiedKFold(n_splits=n_folds, shuffle=True,
                                    random_state=RANDOM_SEED)

        lr_cross = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
        try:
            lr_cross_scores = cross_val_score(lr_cross, X_cross_s, y_cross,
                                               cv=cv_cross, scoring='accuracy')
            lr_cross_mean = float(lr_cross_scores.mean())
        except Exception as e:
            lr_cross_scores = np.array([cross_baseline])
            lr_cross_mean = float(cross_baseline)
            print(f"  LR cross failed: {e}")

        rf_cross = RandomForestClassifier(n_estimators=100, random_state=RANDOM_SEED,
                                            max_depth=3)
        try:
            rf_cross_scores = cross_val_score(rf_cross, X_cross_s, y_cross,
                                               cv=cv_cross, scoring='accuracy')
            rf_cross_mean = float(rf_cross_scores.mean())
        except Exception as e:
            rf_cross_scores = np.array([cross_baseline])
            rf_cross_mean = float(cross_baseline)
            print(f"  RF cross failed: {e}")

        print(f"  Cross-zone mode baseline: {cross_baseline:.4f}")
        print(f"  LR (full state): {lr_cross_mean:.4f}")
        print(f"  RF (full state): {rf_cross_mean:.4f}")

        t3_verdict = ("STATE_PREDICTIVE" if max(lr_cross_mean, rf_cross_mean) > cross_baseline + 0.05
                       else "NOT_PREDICTIVE")
    else:
        cross_baseline = 0
        lr_cross_mean = 0
        rf_cross_mean = 0
        lr_cross_scores = np.array([0])
        rf_cross_scores = np.array([0])
        t3_verdict = "INSUFFICIENT_DATA"

    print(f"  Verdict: {t3_verdict}")

    t3_results = {
        'n_cross_pairs': n_cross_pairs,
        'cross_mode_baseline': float(cross_baseline),
        'lr_cross_mean': lr_cross_mean,
        'lr_cross_folds': [float(x) for x in lr_cross_scores],
        'rf_cross_mean': rf_cross_mean,
        'rf_cross_folds': [float(x) for x in rf_cross_scores],
        'verdict': t3_verdict,
    }

    # ============================================================
    # T4: Terminal e/k Ratio by Transition Type
    # ============================================================
    print("\n" + "=" * 70)
    print("T4: TERMINAL e/k RATIO BY TRANSITION TYPE")
    print("=" * 70)

    transition_ek = defaultdict(list)
    transition_k = defaultdict(list)
    transition_e = defaultdict(list)
    for p in pairs:
        trans_type = f"{p['curr_zone']}->{p['next_zone']}"
        tf = p['curr_terminal']
        k_val = tf['k_frac']
        e_val = tf['e_frac']
        ek_ratio = e_val / (k_val + e_val + 0.001)  # e/(k+e), avoid div by 0
        transition_ek[trans_type].append(ek_ratio)
        transition_k[trans_type].append(k_val)
        transition_e[trans_type].append(e_val)

    print(f"\n  {'Transition':20s} {'N':>4s} {'Mean e/(k+e)':>12s} {'Mean k':>8s} {'Mean e':>8s}")
    print(f"  {'-'*20} {'----':>4s} {'-'*12:>12s} {'-'*8:>8s} {'-'*8:>8s}")

    t4_transitions = {}
    for trans in sorted(transition_ek.keys()):
        vals = transition_ek[trans]
        n = len(vals)
        mean_ek = np.mean(vals)
        mean_k = np.mean(transition_k[trans])
        mean_e = np.mean(transition_e[trans])
        print(f"  {trans:20s} {n:4d} {mean_ek:12.4f} {mean_k:8.4f} {mean_e:8.4f}")
        t4_transitions[trans] = {
            'n': n,
            'mean_ek_ratio': float(mean_ek),
            'mean_k': float(mean_k),
            'mean_e': float(mean_e),
            'std_ek_ratio': float(np.std(vals)),
        }

    # Test: does terminal e/k differ between same-zone and cross-zone transitions?
    same_zone_ek = [transition_ek[t] for t in transition_ek
                     if t.split('->')[0] == t.split('->')[1]]
    cross_zone_ek = [transition_ek[t] for t in transition_ek
                      if t.split('->')[0] != t.split('->')[1]]
    same_zone_ek_flat = [v for vl in same_zone_ek for v in vl]
    cross_zone_ek_flat = [v for vl in cross_zone_ek for v in vl]

    if same_zone_ek_flat and cross_zone_ek_flat:
        u_stat, u_p = mannwhitneyu(same_zone_ek_flat, cross_zone_ek_flat,
                                    alternative='two-sided')
        print(f"\n  Same-zone mean e/(k+e): {np.mean(same_zone_ek_flat):.4f} (n={len(same_zone_ek_flat)})")
        print(f"  Cross-zone mean e/(k+e): {np.mean(cross_zone_ek_flat):.4f} (n={len(cross_zone_ek_flat)})")
        print(f"  Mann-Whitney U={u_stat:.1f}, p={u_p:.4f}")
    else:
        u_stat, u_p = 0, 1.0

    # Kruskal-Wallis across transition types with sufficient data
    groups_for_kw = []
    group_labels = []
    for trans in sorted(transition_ek.keys()):
        if len(transition_ek[trans]) >= 5:
            groups_for_kw.append(transition_ek[trans])
            group_labels.append(trans)

    if len(groups_for_kw) >= 3:
        kw_H, kw_p = kruskal(*groups_for_kw)
        print(f"\n  Kruskal-Wallis across {len(groups_for_kw)} transition types "
              f"(n>=5 each): H={kw_H:.3f}, p={kw_p:.4f}")
    else:
        kw_H, kw_p = 0, 1.0

    t4_verdict = "THERMAL_STATE_VARIES" if kw_p < 0.05 else "NO_THERMAL_DIFFERENTIATION"
    print(f"  Verdict: {t4_verdict}")

    t4_results = {
        'transitions': t4_transitions,
        'same_vs_cross_U': float(u_stat),
        'same_vs_cross_p': float(u_p),
        'same_zone_mean_ek': float(np.mean(same_zone_ek_flat)) if same_zone_ek_flat else None,
        'cross_zone_mean_ek': float(np.mean(cross_zone_ek_flat)) if cross_zone_ek_flat else None,
        'kruskal_wallis_H': float(kw_H),
        'kruskal_wallis_p': float(kw_p),
        'kruskal_wallis_n_groups': len(groups_for_kw),
        'kruskal_wallis_group_labels': group_labels,
        'verdict': t4_verdict,
    }

    # ============================================================
    # T5: Cross-Paragraph Thermal Continuity
    # ============================================================
    print("\n" + "=" * 70)
    print("T5: CROSS-PARAGRAPH THERMAL CONTINUITY")
    print("=" * 70)

    terminal_e = [p['curr_terminal']['e_frac'] for p in pairs]
    initial_e = [p['next_initial']['e_frac'] for p in pairs]
    terminal_k = [p['curr_terminal']['k_frac'] for p in pairs]
    initial_k = [p['next_initial']['k_frac'] for p in pairs]
    terminal_h = [p['curr_terminal']['h_frac'] for p in pairs]
    initial_h = [p['next_initial']['h_frac'] for p in pairs]

    rho_e, p_e = spearmanr(terminal_e, initial_e)
    rho_k, p_k = spearmanr(terminal_k, initial_k)
    rho_h, p_h = spearmanr(terminal_h, initial_h)

    # Also correlate terminal qo/chsh fractions
    terminal_qo = [p['curr_terminal']['qo_frac'] for p in pairs]
    initial_qo = [p['next_initial']['qo_frac'] for p in pairs]
    terminal_chsh = [p['curr_terminal']['chsh_frac'] for p in pairs]
    initial_chsh = [p['next_initial']['chsh_frac'] for p in pairs]

    rho_qo, p_qo = spearmanr(terminal_qo, initial_qo)
    rho_chsh, p_chsh = spearmanr(terminal_chsh, initial_chsh)

    print(f"  Terminal -> Initial correlations (Spearman, n={n_pairs}):")
    print(f"    e_frac: rho={rho_e:.4f}, p={p_e:.4e}")
    print(f"    k_frac: rho={rho_k:.4f}, p={p_k:.4e}")
    print(f"    h_frac: rho={rho_h:.4f}, p={p_h:.4e}")
    print(f"    qo_frac: rho={rho_qo:.4f}, p={p_qo:.4e}")
    print(f"    chsh_frac: rho={rho_chsh:.4f}, p={p_chsh:.4e}")
    print(f"\n  Reference: within-paragraph B-track thermal continuity "
          f"rho=0.376 (C1260)")

    # Cross-zone only
    cross_pairs_filtered = [p for p in pairs if p['is_cross_zone']]
    if len(cross_pairs_filtered) >= 10:
        te_cross = [p['curr_terminal']['e_frac'] for p in cross_pairs_filtered]
        ie_cross = [p['next_initial']['e_frac'] for p in cross_pairs_filtered]
        tk_cross = [p['curr_terminal']['k_frac'] for p in cross_pairs_filtered]
        ik_cross = [p['next_initial']['k_frac'] for p in cross_pairs_filtered]

        rho_e_cross, p_e_cross = spearmanr(te_cross, ie_cross)
        rho_k_cross, p_k_cross = spearmanr(tk_cross, ik_cross)
        print(f"\n  Cross-zone only (n={len(cross_pairs_filtered)}):")
        print(f"    e_frac: rho={rho_e_cross:.4f}, p={p_e_cross:.4e}")
        print(f"    k_frac: rho={rho_k_cross:.4f}, p={p_k_cross:.4e}")
    else:
        rho_e_cross, p_e_cross = 0, 1
        rho_k_cross, p_k_cross = 0, 1

    any_sig = any(p < 0.05 for p in [p_e, p_k, p_h, p_qo, p_chsh])
    t5_verdict = "THERMAL_CONTINUITY" if (rho_e > 0.15 and p_e < 0.05) else "NO_CONTINUITY"
    print(f"  Verdict: {t5_verdict}")

    t5_results = {
        'n_pairs': n_pairs,
        'correlations': {
            'e_frac': {'rho': float(rho_e), 'p': float(p_e)},
            'k_frac': {'rho': float(rho_k), 'p': float(p_k)},
            'h_frac': {'rho': float(rho_h), 'p': float(p_h)},
            'qo_frac': {'rho': float(rho_qo), 'p': float(p_qo)},
            'chsh_frac': {'rho': float(rho_chsh), 'p': float(p_chsh)},
        },
        'cross_zone_n': len(cross_pairs_filtered),
        'cross_zone_e_rho': float(rho_e_cross),
        'cross_zone_e_p': float(p_e_cross),
        'cross_zone_k_rho': float(rho_k_cross),
        'cross_zone_k_p': float(p_k_cross),
        'reference_within_paragraph_rho': 0.376,
        'verdict': t5_verdict,
    }

    # ============================================================
    # T6: Tail Product Signature -> Next Zone (chi-squared)
    # ============================================================
    print("\n" + "=" * 70)
    print("T6: TAIL PRODUCT SIGNATURE -> NEXT ZONE")
    print("=" * 70)

    # Classify tail product type using k=3 clustering on terminal features
    # (mirrors C1232 tail product signatures)
    from sklearn.cluster import KMeans as KM

    tail_features = []
    tail_pairs_idx = []
    for i, p in enumerate(pairs):
        tf = p['curr_terminal']
        fv = [tf['k_frac'], tf['e_frac'], tf['h_frac'],
              tf['bare_suffix_frac'], tf['dy_frac']]
        tail_features.append(fv)
        tail_pairs_idx.append(i)

    X_tail = np.array(tail_features)
    scaler_tail = StandardScaler()
    X_tail_s = scaler_tail.fit_transform(X_tail)

    km_tail = KM(n_clusters=3, n_init=50, random_state=RANDOM_SEED)
    tail_labels = km_tail.fit_predict(X_tail_s)

    # Contingency table: tail type x next zone
    ct_tail = np.zeros((3, 4), dtype=int)
    for idx, pair_i in enumerate(tail_pairs_idx):
        tail_type = tail_labels[idx]
        next_z = pairs[pair_i]['next_zone']
        ct_tail[tail_type, next_z] += 1

    # Report tail type centroids
    tail_centroids = scaler_tail.inverse_transform(km_tail.cluster_centers_)
    tail_feature_names = ['k_frac', 'e_frac', 'h_frac', 'bare_suffix_frac', 'dy_frac']
    print(f"\n  Tail type centroids:")
    for ti in range(3):
        desc = ", ".join(f"{fn}={tail_centroids[ti, fi]:.3f}"
                         for fi, fn in enumerate(tail_feature_names))
        print(f"    Type {ti} (n={sum(ct_tail[ti])}): {desc}")

    print(f"\n  Contingency (tail_type x next_zone):")
    print(f"  {'':10s}" + "".join(f"  Z{z}" for z in range(4)))
    for ti in range(3):
        row = f"  Tail_{ti:>4d}" + "".join(f"  {ct_tail[ti, z]:3d}" for z in range(4))
        print(row)

    # Filter out rows/cols with all zeros
    row_sums = ct_tail.sum(axis=1)
    col_sums = ct_tail.sum(axis=0)
    valid_rows = row_sums > 0
    valid_cols = col_sums > 0
    ct_tail_f = ct_tail[valid_rows][:, valid_cols]

    if ct_tail_f.shape[0] >= 2 and ct_tail_f.shape[1] >= 2:
        chi2_tail, p_tail, dof_tail, _ = chi2_contingency(ct_tail_f)
        v_tail = np.sqrt(chi2_tail / (ct_tail_f.sum() * (min(ct_tail_f.shape) - 1)))
        print(f"\n  Chi-squared = {chi2_tail:.3f}, p = {p_tail:.4f}, V = {v_tail:.4f}")
    else:
        chi2_tail, p_tail, dof_tail, v_tail = 0, 1, 0, 0

    t6_verdict = "TAIL_PREDICTS_NEXT" if p_tail < 0.05 else "NO_PREDICTION"
    print(f"  Verdict: {t6_verdict}")

    t6_results = {
        'n_pairs': len(tail_pairs_idx),
        'tail_centroids': {
            str(ti): {fn: float(tail_centroids[ti, fi])
                      for fi, fn in enumerate(tail_feature_names)}
            for ti in range(3)
        },
        'contingency': {
            f"Tail_{ti}": {f"Z{z}": int(ct_tail[ti, z]) for z in range(4)}
            for ti in range(3)
        },
        'chi_squared': float(chi2_tail),
        'p_value': float(p_tail),
        'cramers_v': float(v_tail),
        'verdict': t6_verdict,
    }

    # ============================================================
    # T7: Combined State Model
    # ============================================================
    print("\n" + "=" * 70)
    print("T7: COMBINED STATE MODEL")
    print("=" * 70)

    X_full = np.array([pair_to_full_vector(p) for p in pairs])
    scaler_full = StandardScaler()
    X_full_s = scaler_full.fit_transform(X_full)

    # Current zone as one-hot feature
    curr_zones = np.array([p['curr_zone'] for p in pairs])
    X_zone = np.zeros((n_pairs, 4))
    for i, z in enumerate(curr_zones):
        X_zone[i, z] = 1

    # Model comparison:
    # 1. Overall mode baseline
    # 2. Folio-mode baseline
    # 3. Zone-only (current zone -> next zone via logistic reg)
    # 4. State-only (terminal features -> next zone)
    # 5. Combined (current zone + terminal features)

    print(f"\n  Model comparison (5-fold CV accuracy, n={n_pairs}):")

    # Zone-only
    lr_zone = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
    lr_zone_scores = cross_val_score(lr_zone, X_zone, y_next_zone,
                                      cv=cv, scoring='accuracy')

    # State-only (full features)
    lr_state = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
    lr_state_scores = cross_val_score(lr_state, X_full_s, y_next_zone,
                                       cv=cv, scoring='accuracy')

    # Combined
    X_combined = np.hstack([X_zone, X_full_s])
    lr_combined = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
    lr_combined_scores = cross_val_score(lr_combined, X_combined, y_next_zone,
                                          cv=cv, scoring='accuracy')

    # Random Forest combined
    rf_combined = RandomForestClassifier(n_estimators=200, random_state=RANDOM_SEED,
                                          max_depth=5)
    rf_combined_scores = cross_val_score(rf_combined, X_combined, y_next_zone,
                                          cv=cv, scoring='accuracy')

    models = {
        'Overall mode baseline': overall_baseline,
        'Folio-mode baseline': baseline_acc,
        'Zone-only (LR)': lr_zone_scores.mean(),
        'State-only (LR)': lr_state_scores.mean(),
        'Combined zone+state (LR)': lr_combined_scores.mean(),
        'Combined zone+state (RF)': rf_combined_scores.mean(),
    }

    for name, acc in models.items():
        marker = " ***" if acc == max(models.values()) else ""
        print(f"    {name:35s}: {acc:.4f}{marker}")

    # State incremental value over zone
    zone_to_combined_gain = lr_combined_scores.mean() - lr_zone_scores.mean()
    state_over_baseline = lr_state_scores.mean() - overall_baseline
    print(f"\n  State incremental over zone-only: {zone_to_combined_gain:+.4f}")
    print(f"  State over overall baseline: {state_over_baseline:+.4f}")

    t7_verdict = ("STATE_ADDS_VALUE" if zone_to_combined_gain > 0.02
                   else "ZONE_SUFFICIENT")
    print(f"  Verdict: {t7_verdict}")

    t7_results = {
        'models': {k: float(v) for k, v in models.items()},
        'lr_zone_folds': [float(x) for x in lr_zone_scores],
        'lr_state_folds': [float(x) for x in lr_state_scores],
        'lr_combined_folds': [float(x) for x in lr_combined_scores],
        'rf_combined_folds': [float(x) for x in rf_combined_scores],
        'zone_to_combined_gain': float(zone_to_combined_gain),
        'state_over_baseline': float(state_over_baseline),
        'verdict': t7_verdict,
    }

    # ============================================================
    # T8: Section-Controlled State Prediction
    # ============================================================
    print("\n" + "=" * 70)
    print("T8: SECTION-CONTROLLED STATE PREDICTION")
    print("=" * 70)

    section_results_t8 = {}
    for sec_code in ['B', 'H', 'S', 'C']:
        sec_pairs = [p for p in pairs if p['section'] == sec_code]
        n_sec = len(sec_pairs)
        if n_sec < 15:
            section_results_t8[SECTION_NAMES.get(sec_code, sec_code)] = {
                'n': n_sec, 'skipped': True, 'reason': 'insufficient data'
            }
            continue

        X_sec = np.array([pair_to_full_vector(p) for p in sec_pairs])
        y_sec = np.array([p['next_zone'] for p in sec_pairs])

        # Check if we have at least 2 classes
        n_classes = len(set(y_sec))
        if n_classes < 2:
            section_results_t8[SECTION_NAMES.get(sec_code, sec_code)] = {
                'n': n_sec, 'skipped': True, 'reason': 'single zone'
            }
            continue

        scaler_sec = StandardScaler()
        X_sec_s = scaler_sec.fit_transform(X_sec)

        sec_mode = Counter(y_sec).most_common(1)[0][0]
        sec_baseline = accuracy_score(y_sec, [sec_mode] * len(y_sec))

        # Zone-only within section
        curr_z_sec = np.array([p['curr_zone'] for p in sec_pairs])
        X_zone_sec = np.zeros((n_sec, 4))
        for i, z in enumerate(curr_z_sec):
            X_zone_sec[i, z] = 1

        n_folds_sec = min(5, min(Counter(y_sec).values()))
        if n_folds_sec < 2:
            n_folds_sec = 2
        cv_sec = StratifiedKFold(n_splits=n_folds_sec, shuffle=True,
                                  random_state=RANDOM_SEED)

        try:
            lr_z_sec_scores = cross_val_score(
                LogisticRegression(max_iter=1000, random_state=RANDOM_SEED),
                X_zone_sec, y_sec, cv=cv_sec, scoring='accuracy')
            zone_acc = float(lr_z_sec_scores.mean())
        except Exception:
            zone_acc = float(sec_baseline)

        # Combined within section
        X_comb_sec = np.hstack([X_zone_sec, X_sec_s])
        try:
            lr_c_sec_scores = cross_val_score(
                LogisticRegression(max_iter=1000, random_state=RANDOM_SEED),
                X_comb_sec, y_sec, cv=cv_sec, scoring='accuracy')
            combined_acc = float(lr_c_sec_scores.mean())
        except Exception:
            combined_acc = float(sec_baseline)

        gain = combined_acc - zone_acc
        sec_name = SECTION_NAMES.get(sec_code, sec_code)
        print(f"  {sec_name} (n={n_sec}): baseline={sec_baseline:.3f}, "
              f"zone={zone_acc:.3f}, combined={combined_acc:.3f}, "
              f"gain={gain:+.3f}")

        section_results_t8[sec_name] = {
            'n': n_sec,
            'n_classes': n_classes,
            'skipped': False,
            'mode_baseline': float(sec_baseline),
            'zone_only_acc': zone_acc,
            'combined_acc': combined_acc,
            'state_gain': float(gain),
        }

    # Summary
    gains = [v['state_gain'] for v in section_results_t8.values()
             if not v.get('skipped', True)]
    mean_gain = np.mean(gains) if gains else 0
    any_positive = any(g > 0.02 for g in gains)
    t8_verdict = "SECTION_CONTROLLED_GAIN" if any_positive else "NO_WITHIN_SECTION_GAIN"
    print(f"\n  Mean within-section gain: {mean_gain:+.4f}")
    print(f"  Verdict: {t8_verdict}")

    t8_results = {
        'sections': section_results_t8,
        'mean_gain': float(mean_gain),
        'verdict': t8_verdict,
    }

    # ============================================================
    # SYNTHESIS
    # ============================================================
    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)

    verdicts = {
        'T1_kernel_prediction': t1_verdict,
        'T2_category_prediction': t2_verdict,
        'T3_cross_zone_prediction': t3_verdict,
        'T4_thermal_differentiation': t4_verdict,
        'T5_thermal_continuity': t5_verdict,
        'T6_tail_product_prediction': t6_verdict,
        'T7_combined_model': t7_verdict,
        'T8_section_controlled': t8_verdict,
    }

    n_pass = sum(1 for v in verdicts.values()
                 if v in ('STATE_PREDICTIVE', 'THERMAL_STATE_VARIES',
                          'THERMAL_CONTINUITY', 'TAIL_PREDICTS_NEXT',
                          'STATE_ADDS_VALUE', 'SECTION_CONTROLLED_GAIN'))
    n_fail = sum(1 for v in verdicts.values()
                 if v in ('NOT_PREDICTIVE', 'NO_THERMAL_DIFFERENTIATION',
                          'NO_CONTINUITY', 'NO_PREDICTION',
                          'ZONE_SUFFICIENT', 'NO_WITHIN_SECTION_GAIN'))
    n_other = len(verdicts) - n_pass - n_fail

    print(f"\n  Results: {n_pass} PASS, {n_fail} FAIL, {n_other} OTHER")
    for test, verdict in verdicts.items():
        marker = "PASS" if verdict in ('STATE_PREDICTIVE', 'THERMAL_STATE_VARIES',
                                        'THERMAL_CONTINUITY', 'TAIL_PREDICTS_NEXT',
                                        'STATE_ADDS_VALUE', 'SECTION_CONTROLLED_GAIN') else "FAIL"
        if verdict == 'INSUFFICIENT_DATA':
            marker = 'SKIP'
        print(f"    {test:40s}: {verdict} ({marker})")

    # Overall interpretation
    if n_pass >= 5:
        overall = "STATE_DEPENDENT_ORDERING"
        interpretation = (
            f"Paragraph ordering IS state-dependent. {n_pass}/8 tests support "
            f"the hypothesis that terminal physical state predicts what zone follows. "
            f"Ordering is driven by the process state at paragraph end, not by "
            f"a predetermined sequence."
        )
    elif n_pass >= 3:
        overall = "PARTIAL_STATE_DEPENDENCE"
        interpretation = (
            f"PARTIAL state dependence detected. {n_pass}/8 tests show state signal, "
            f"but the effect is weak or confined to specific dimensions. "
            f"Zone inertia (C1399) may be the dominant mechanism, with state "
            f"providing modest additional routing information."
        )
    elif n_pass >= 1:
        overall = "WEAK_STATE_SIGNAL"
        interpretation = (
            f"Weak state signal. Only {n_pass}/8 tests positive. "
            f"Ordering is primarily driven by folio theme (zone inertia 2.02x), "
            f"not by terminal physical state. State carries minimal cross-paragraph "
            f"information."
        )
    else:
        overall = "NO_STATE_DEPENDENCE"
        interpretation = (
            f"NO state dependence detected. 0/8 tests positive. "
            f"Paragraph ordering is independent of terminal state. Zone inertia "
            f"is a folio-level theme effect, not a state-driven mechanism."
        )

    print(f"\n  OVERALL: {overall}")
    print(f"  {interpretation}")

    # ============================================================
    # SAVE RESULTS
    # ============================================================
    results = {
        'metadata': {
            'phase': 'PARAGRAPH_STATE_DEPENDENT_ORDERING (Phase 512)',
            'n_pairs': n_pairs,
            'n_cross_zone': n_cross,
            'n_same_zone': n_same,
            'cross_zone_fraction': float(n_cross / n_pairs),
            'random_seed': RANDOM_SEED,
            'feature_names': all_state_features,
            'zone_names': {str(k): v for k, v in ZONE_NAMES.items()},
        },
        'T1_kernel_prediction': t1_results,
        'T2_category_prediction': t2_results,
        'T3_cross_zone_prediction': t3_results,
        'T4_terminal_thermal_ratio': t4_results,
        'T5_thermal_continuity': t5_results,
        'T6_tail_product_prediction': t6_results,
        'T7_combined_model': t7_results,
        'T8_section_controlled': t8_results,
        'synthesis': {
            'verdicts': verdicts,
            'n_pass': n_pass,
            'n_fail': n_fail,
            'n_other': n_other,
            'overall': overall,
            'interpretation': interpretation,
        },
    }

    out_path = os.path.join(os.path.dirname(__file__), '..', 'results',
                            'state_dependent_ordering.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
