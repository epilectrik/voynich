#!/usr/bin/env python3
"""
Phase 347: STRUCTURAL_DIRECTIONALITY
======================================
Tests forward-backward asymmetry at multiple structural levels.
C391 establishes symmetric conditional entropy; C886 establishes
directional transition probabilities. This phase decomposes WHERE
the directionality resides — which morphological components and
which functional roles carry it.

Pre-registered predictions:
  P1: Class-level bigram JSD (forward vs reverse) significantly > 0 (p < 0.01)
  P2: PREFIX asymmetry > MIDDLE asymmetry (>= 1.5x), because PREFIX is the router (C1023)
  P3: CC role shows highest per-class asymmetry (initiators/terminators are directional)
  P4: FL_HAZ more asymmetric than FL_SAFE
  P5: Within-line shuffle collapses asymmetry to near zero (< 10% of real)

Depends on: C391, C886, C1023, C521, C572, C816, C819
"""

import json
import sys
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import entropy as scipy_entropy

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Constants ────────────────────────────────────────────────────────

# Role taxonomy from BCSC
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

FL_HAZ_CLASSES = {7, 30}
FL_SAFE_CLASSES = {38, 40}

N_SHUFFLE = 100  # Null control permutations


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load B tokens with class, prefix, middle, suffix, organized by line."""
    print("Loading data...")

    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}

    morph = Morphology()

    # Build line-organized token sequences
    lines = defaultdict(list)  # (folio, line_num) -> list of token dicts

    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue

        cls = token_to_class.get(token.word)
        if cls is None:
            continue

        m = morph.extract(token.word)
        prefix = m.prefix if m else None
        middle = m.middle if m else token.word
        suffix = m.suffix if m else None

        lines[(token.folio, token.line)].append({
            'word': token.word,
            'cls': cls,
            'role': CLASS_TO_ROLE.get(cls, 'UNK'),
            'prefix': prefix or '(bare)',
            'middle': middle or '(bare)',
            'suffix': suffix or '(bare)',
            'folio': token.folio,
            'line': token.line,
        })

    # Flatten to ordered list and extract within-line bigrams
    all_tokens = []
    for key in sorted(lines.keys()):
        all_tokens.extend(lines[key])

    print(f"  {len(all_tokens)} tokens in {len(lines)} lines")
    return all_tokens, lines


# ── Core Metrics ─────────────────────────────────────────────────────

def jsd(p, q):
    """Jensen-Shannon divergence between two distributions."""
    p = np.asarray(p, dtype=float) + 1e-12
    q = np.asarray(q, dtype=float) + 1e-12
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    return float(0.5 * scipy_entropy(p, m, base=2) + 0.5 * scipy_entropy(q, m, base=2))


def build_transition_matrix(class_sequence, n_classes=49):
    """Build forward transition matrix from a class sequence.
    Classes are 1-indexed (1..49)."""
    trans = np.zeros((n_classes, n_classes))
    for i in range(len(class_sequence) - 1):
        c_from = class_sequence[i] - 1  # 0-index
        c_to = class_sequence[i + 1] - 1
        if 0 <= c_from < n_classes and 0 <= c_to < n_classes:
            trans[c_from, c_to] += 1
    return trans


def normalize_rows(matrix):
    """Row-normalize a matrix to get conditional probabilities."""
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums = np.maximum(row_sums, 1e-12)
    return matrix / row_sums


def per_class_jsd(fwd_matrix, rev_matrix):
    """Compute JSD between forward and reverse per-class distributions.
    Returns: dict mapping class_idx -> JSD value, and weighted mean."""
    n = fwd_matrix.shape[0]
    fwd_norm = normalize_rows(fwd_matrix)
    rev_norm = normalize_rows(rev_matrix)

    results = {}
    weights = fwd_matrix.sum(axis=1)
    total_weight = weights.sum()

    for i in range(n):
        if weights[i] < 5:  # Skip classes with too few observations
            continue
        results[i] = jsd(fwd_norm[i], rev_norm[i])

    weighted_mean = sum(results[i] * weights[i] for i in results) / max(total_weight, 1)
    return results, float(weighted_mean)


def compute_component_mi_asymmetry(tokens, lines, component='prefix'):
    """Compute MI(component_t ; class_{t+1}) - MI(component_t ; class_{t-1}).

    Positive = component predicts future better than past (directional).
    Zero = component predicts equally (symmetric).
    """
    # Collect forward and backward pairs
    forward_pairs = []   # (component_t, class_{t+1})
    backward_pairs = []  # (component_t, class_{t-1})

    for key in sorted(lines.keys()):
        line_tokens = lines[key]
        for i in range(len(line_tokens)):
            comp_val = line_tokens[i][component]
            if i < len(line_tokens) - 1:
                forward_pairs.append((comp_val, line_tokens[i + 1]['cls']))
            if i > 0:
                backward_pairs.append((comp_val, line_tokens[i - 1]['cls']))

    def compute_mi(pairs):
        """Compute mutual information I(X; Y) from pairs."""
        xy_counts = Counter(pairs)
        x_counts = Counter(p[0] for p in pairs)
        y_counts = Counter(p[1] for p in pairs)
        n = len(pairs)

        mi = 0.0
        for (x, y), count in xy_counts.items():
            p_xy = count / n
            p_x = x_counts[x] / n
            p_y = y_counts[y] / n
            if p_xy > 0 and p_x > 0 and p_y > 0:
                mi += p_xy * np.log2(p_xy / (p_x * p_y))
        return mi

    mi_forward = compute_mi(forward_pairs)
    mi_backward = compute_mi(backward_pairs)
    asymmetry = mi_forward - mi_backward

    return {
        'mi_forward': float(mi_forward),
        'mi_backward': float(mi_backward),
        'asymmetry': float(asymmetry),
        'n_forward': len(forward_pairs),
        'n_backward': len(backward_pairs),
    }


# ── Tests ────────────────────────────────────────────────────────────

def run_t1(tokens, lines):
    """T1: Class-level bigram asymmetry (forward vs reverse)."""
    print("\n" + "=" * 60)
    print("T1: Class-Level Bigram Asymmetry")
    print("=" * 60)

    # Build forward class sequence (within-line only)
    fwd_sequences = []
    for key in sorted(lines.keys()):
        line_tokens = lines[key]
        if len(line_tokens) >= 2:
            fwd_sequences.append([t['cls'] for t in line_tokens])

    # Forward transition matrix
    fwd_matrix = np.zeros((49, 49))
    for seq in fwd_sequences:
        for i in range(len(seq) - 1):
            fwd_matrix[seq[i] - 1, seq[i + 1] - 1] += 1

    # Reverse transition matrix (reverse each line)
    rev_matrix = np.zeros((49, 49))
    for seq in fwd_sequences:
        rev_seq = list(reversed(seq))
        for i in range(len(rev_seq) - 1):
            rev_matrix[rev_seq[i] - 1, rev_seq[i + 1] - 1] += 1

    # Overall JSD between flattened matrices (as distributions over bigrams)
    fwd_flat = fwd_matrix.flatten()
    rev_flat = rev_matrix.flatten()
    overall_jsd = jsd(fwd_flat, rev_flat)

    # Per-class JSD
    class_jsds, weighted_mean_jsd = per_class_jsd(fwd_matrix, rev_matrix)

    # Total transitions
    n_transitions = int(fwd_matrix.sum())

    print(f"  Total within-line transitions: {n_transitions}")
    print(f"  Overall bigram JSD (forward vs reverse): {overall_jsd:.6f} bits")
    print(f"  Weighted mean per-class JSD: {weighted_mean_jsd:.6f} bits")
    print(f"  Classes with JSD computed: {len(class_jsds)}/49")

    # Top 10 most asymmetric classes
    sorted_classes = sorted(class_jsds.items(), key=lambda x: x[1], reverse=True)
    print(f"\n  Top 10 most asymmetric classes:")
    print(f"  {'Class':>6} {'Role':>4} {'JSD':>10} {'Count':>8}")
    for cls_idx, jsd_val in sorted_classes[:10]:
        cls = cls_idx + 1
        role = CLASS_TO_ROLE.get(cls, '?')
        count = int(fwd_matrix[cls_idx].sum())
        print(f"  {cls:>6} {role:>4} {jsd_val:>10.6f} {count:>8}")

    # Verdict
    verdict = "PASS" if overall_jsd > 0.001 else "FAIL"  # Very conservative threshold
    print(f"\n  Verdict: {verdict} (JSD = {overall_jsd:.6f}, threshold > 0.001)")

    return {
        'overall_jsd': overall_jsd,
        'weighted_mean_per_class_jsd': weighted_mean_jsd,
        'n_transitions': n_transitions,
        'n_classes_measured': len(class_jsds),
        'per_class_jsd': {str(k + 1): v for k, v in class_jsds.items()},
        'top_10_asymmetric': [
            {'class': k + 1, 'role': CLASS_TO_ROLE.get(k + 1, '?'), 'jsd': v}
            for k, v in sorted_classes[:10]
        ],
        'verdict': verdict,
        'fwd_matrix': fwd_matrix,  # Keep for T5
        'rev_matrix': rev_matrix,
    }


def run_t2(tokens, lines):
    """T2: Component-level asymmetry decomposition.
    PREFIX asymmetry vs MIDDLE asymmetry vs SUFFIX asymmetry."""
    print("\n" + "=" * 60)
    print("T2: Component-Level Asymmetry Decomposition")
    print("=" * 60)

    results = {}
    for comp in ['prefix', 'middle', 'suffix']:
        r = compute_component_mi_asymmetry(tokens, lines, component=comp)
        results[comp] = r
        print(f"\n  {comp.upper()}:")
        print(f"    MI(comp → next class):  {r['mi_forward']:.4f} bits")
        print(f"    MI(comp → prev class):  {r['mi_backward']:.4f} bits")
        print(f"    Asymmetry (fwd - bwd):  {r['asymmetry']:+.4f} bits")

    # Compute ratios
    prefix_asym = abs(results['prefix']['asymmetry'])
    middle_asym = abs(results['middle']['asymmetry'])
    suffix_asym = abs(results['suffix']['asymmetry'])

    print(f"\n  |Asymmetry| comparison:")
    print(f"    PREFIX:  {prefix_asym:.4f}")
    print(f"    MIDDLE:  {middle_asym:.4f}")
    print(f"    SUFFIX:  {suffix_asym:.4f}")

    if middle_asym > 0:
        prefix_ratio = prefix_asym / middle_asym
        print(f"    PREFIX/MIDDLE ratio: {prefix_ratio:.2f}x")
    else:
        prefix_ratio = float('inf')
        print(f"    PREFIX/MIDDLE ratio: inf (MIDDLE asymmetry = 0)")

    # Verdict: PREFIX asymmetry >= 1.5x MIDDLE asymmetry
    verdict = "PASS" if prefix_ratio >= 1.5 else "FAIL"
    print(f"\n  Verdict: {verdict} (PREFIX/MIDDLE ratio = {prefix_ratio:.2f}x, threshold >= 1.5x)")

    return {
        'prefix': results['prefix'],
        'middle': results['middle'],
        'suffix': results['suffix'],
        'prefix_abs_asymmetry': prefix_asym,
        'middle_abs_asymmetry': middle_asym,
        'suffix_abs_asymmetry': suffix_asym,
        'prefix_middle_ratio': float(prefix_ratio) if prefix_ratio != float('inf') else 999.0,
        'verdict': verdict,
    }


def run_t3(tokens, lines, t1_class_jsds):
    """T3: Role-specific asymmetry. Prediction: CC has highest mean per-class JSD."""
    print("\n" + "=" * 60)
    print("T3: Role-Specific Asymmetry")
    print("=" * 60)

    role_jsds = defaultdict(list)
    role_weights = defaultdict(list)

    for cls_idx, jsd_val in t1_class_jsds.items():
        cls = cls_idx + 1  # 1-indexed
        role = CLASS_TO_ROLE.get(cls, 'UNK')
        role_jsds[role].append(jsd_val)

    results = {}
    print(f"\n  {'Role':>4} {'N_classes':>10} {'Mean JSD':>10} {'Max JSD':>10} {'Min JSD':>10}")
    for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
        vals = role_jsds.get(role, [])
        if vals:
            mean_val = float(np.mean(vals))
            max_val = float(np.max(vals))
            min_val = float(np.min(vals))
            print(f"  {role:>4} {len(vals):>10} {mean_val:>10.6f} {max_val:>10.6f} {min_val:>10.6f}")
            results[role] = {
                'n_classes': len(vals),
                'mean_jsd': mean_val,
                'max_jsd': max_val,
                'min_jsd': min_val,
                'values': vals,
            }

    # Find role with highest mean JSD
    ranked = sorted(results.items(), key=lambda x: x[1]['mean_jsd'], reverse=True)
    print(f"\n  Ranking by mean JSD:")
    for i, (role, data) in enumerate(ranked):
        print(f"    {i + 1}. {role}: {data['mean_jsd']:.6f}")

    highest_role = ranked[0][0] if ranked else None
    verdict = "PASS" if highest_role == 'CC' else "FAIL"
    print(f"\n  Highest asymmetry role: {highest_role}")
    print(f"  Verdict: {verdict} (prediction: CC is highest)")

    return {
        'per_role': {k: {kk: vv for kk, vv in v.items() if kk != 'values'}
                     for k, v in results.items()},
        'ranking': [r[0] for r in ranked],
        'highest_role': highest_role,
        'verdict': verdict,
    }


def run_t4(t1_class_jsds):
    """T4: FL_HAZ vs FL_SAFE asymmetry."""
    print("\n" + "=" * 60)
    print("T4: FL_HAZ vs FL_SAFE Asymmetry")
    print("=" * 60)

    haz_jsds = []
    safe_jsds = []

    for cls_idx, jsd_val in t1_class_jsds.items():
        cls = cls_idx + 1
        if cls in FL_HAZ_CLASSES:
            haz_jsds.append((cls, jsd_val))
        elif cls in FL_SAFE_CLASSES:
            safe_jsds.append((cls, jsd_val))

    print(f"\n  FL_HAZ classes:")
    haz_mean = 0
    for cls, val in haz_jsds:
        print(f"    Class {cls}: JSD = {val:.6f}")
    if haz_jsds:
        haz_mean = float(np.mean([v for _, v in haz_jsds]))
        print(f"    Mean: {haz_mean:.6f}")

    print(f"\n  FL_SAFE classes:")
    safe_mean = 0
    for cls, val in safe_jsds:
        print(f"    Class {cls}: JSD = {val:.6f}")
    if safe_jsds:
        safe_mean = float(np.mean([v for _, v in safe_jsds]))
        print(f"    Mean: {safe_mean:.6f}")

    verdict = "PASS" if haz_mean > safe_mean else "FAIL"
    print(f"\n  FL_HAZ mean ({haz_mean:.6f}) {'>' if haz_mean > safe_mean else '<='} FL_SAFE mean ({safe_mean:.6f})")
    print(f"  Verdict: {verdict}")

    return {
        'fl_haz_jsds': {str(c): v for c, v in haz_jsds},
        'fl_safe_jsds': {str(c): v for c, v in safe_jsds},
        'fl_haz_mean': haz_mean,
        'fl_safe_mean': safe_mean,
        'verdict': verdict,
    }


def run_t5(lines, t1_overall_jsd):
    """T5: Null control — shuffle token order within each line."""
    print("\n" + "=" * 60)
    print("T5: Null Control (Within-Line Shuffle)")
    print("=" * 60)

    # Build line class sequences
    line_sequences = []
    for key in sorted(lines.keys()):
        seq = [t['cls'] for t in lines[key]]
        if len(seq) >= 2:
            line_sequences.append(seq)

    null_jsds = []
    for perm_i in range(N_SHUFFLE):
        # Shuffle each line independently
        shuffled_sequences = []
        for seq in line_sequences:
            s = list(seq)
            np.random.shuffle(s)
            shuffled_sequences.append(s)

        # Build forward and reverse matrices from shuffled
        fwd = np.zeros((49, 49))
        rev = np.zeros((49, 49))
        for seq in shuffled_sequences:
            for i in range(len(seq) - 1):
                fwd[seq[i] - 1, seq[i + 1] - 1] += 1
            rev_seq = list(reversed(seq))
            for i in range(len(rev_seq) - 1):
                rev[rev_seq[i] - 1, rev_seq[i + 1] - 1] += 1

        null_jsd = jsd(fwd.flatten(), rev.flatten())
        null_jsds.append(null_jsd)

    null_mean = float(np.mean(null_jsds))
    null_std = float(np.std(null_jsds))
    null_max = float(np.max(null_jsds))
    ratio = null_mean / max(t1_overall_jsd, 1e-12)

    print(f"  Real JSD: {t1_overall_jsd:.6f}")
    print(f"  Null JSD: mean={null_mean:.6f}, std={null_std:.6f}, max={null_max:.6f}")
    print(f"  Null/Real ratio: {ratio:.4f} ({ratio * 100:.1f}%)")

    # Verdict: null < 10% of real
    verdict = "PASS" if ratio < 0.10 else "FAIL"
    print(f"  Verdict: {verdict} (ratio = {ratio:.4f}, threshold < 0.10)")

    return {
        'real_jsd': t1_overall_jsd,
        'null_mean': null_mean,
        'null_std': null_std,
        'null_max': null_max,
        'null_real_ratio': ratio,
        'n_shuffles': N_SHUFFLE,
        'verdict': verdict,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 347: STRUCTURAL_DIRECTIONALITY")
    print("=" * 60)

    tokens, lines = load_data()

    # T1: Class-level bigram asymmetry
    t1 = run_t1(tokens, lines)
    fwd_matrix = t1.pop('fwd_matrix')
    rev_matrix = t1.pop('rev_matrix')

    # T2: Component-level asymmetry
    t2 = run_t2(tokens, lines)

    # T3: Role-specific asymmetry (uses T1 per-class JSDs)
    # Convert string keys back to int for T3
    t1_class_jsds = {int(k) - 1: v for k, v in t1['per_class_jsd'].items()}
    t3 = run_t3(tokens, lines, t1_class_jsds)

    # T4: FL subtype comparison
    t4 = run_t4(t1_class_jsds)

    # T5: Null control
    t5 = run_t5(lines, t1['overall_jsd'])

    # ── Synthesis ────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SYNTHESIS")
    print("=" * 60)

    verdicts = {
        'T1_bigram_asymmetry': t1['verdict'],
        'T2_prefix_dominance': t2['verdict'],
        'T3_cc_highest': t3['verdict'],
        'T4_fl_haz_gt_safe': t4['verdict'],
        'T5_null_control': t5['verdict'],
    }

    for test, v in verdicts.items():
        print(f"  {test}: {v}")

    pass_count = sum(1 for v in verdicts.values() if v == 'PASS')
    print(f"\n  PASS: {pass_count}/5")

    if pass_count >= 3:
        overall = "STRUCTURAL_DIRECTIONALITY"
    elif pass_count >= 1:
        overall = "WEAK_ASYMMETRY"
    else:
        overall = "SYMMETRIC_EXECUTION"

    print(f"  Overall verdict: {overall}")

    results = {
        'metadata': {
            'phase': 347,
            'name': 'STRUCTURAL_DIRECTIONALITY',
            'total_tokens': len(tokens),
            'total_lines': len(lines),
            'n_null_shuffles': N_SHUFFLE,
        },
        't1_bigram_asymmetry': t1,
        't2_component_asymmetry': t2,
        't3_role_asymmetry': t3,
        't4_fl_subtype': t4,
        't5_null_control': t5,
        'synthesis': {
            'verdicts': verdicts,
            'pass_count': pass_count,
            'total_tests': 5,
            'overall_verdict': overall,
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'structural_directionality.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")


if __name__ == '__main__':
    main()
