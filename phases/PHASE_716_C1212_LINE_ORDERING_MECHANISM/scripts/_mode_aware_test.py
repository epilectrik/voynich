"""PHASE_716 extension: Mode-aware refinement.

Test whether C1727 line-ordering smoothness is driven by mode A/B coherence
rather than cross-line C1212 chaining.

Three tests:
  T1: Within-mode vs cross-mode line-pair squared feature distance
  T2: Residualize by mode mean, recompute smoothness — does signal collapse?
  T3: Are line-boundary tokens (first/last 3) overrepresented in mode-transition lines?
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, decompose_middle_hmt

OUT_PATH = ROOT / 'phases' / 'PHASE_716_C1212_LINE_ORDERING_MECHANISM' / 'results' / 'mode_aware_results.json'

HEAD_TYPES = ['a', 'e', 'o', 'k', 't', 'headless']
TERM_TYPES = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']
HEAD_IDX = {h: i for i, h in enumerate(HEAD_TYPES)}
TERM_IDX = {t: i for i, t in enumerate(TERM_TYPES)}

MODE_A_ATOMS = {'d', 'e', 'ee', 'h', 'y'}
MODE_B_ATOMS = {'a', 'i', 'ii', 'l', 'm', 'n', 'o', 'r', 's'}

N_SHUFFLES = 1000
SEED = 42


def atomize_suffix(suffix):
    if not suffix:
        return []
    atoms = []
    i = 0
    while i < len(suffix):
        if i + 1 < len(suffix) and suffix[i] == suffix[i+1] and suffix[i] in ('e', 'i'):
            atoms.append(suffix[i:i+2])
            i += 2
        else:
            atoms.append(suffix[i])
            i += 1
    return atoms


def get_line_mode(tokens_with_suffix):
    a_count = 0
    b_count = 0
    for suffix in tokens_with_suffix:
        if suffix:
            for atom in atomize_suffix(suffix):
                if atom in MODE_A_ATOMS:
                    a_count += 1
                elif atom in MODE_B_ATOMS:
                    b_count += 1
    if a_count + b_count == 0:
        return None
    return 'A' if a_count > b_count else 'B'


def build_line_features_and_mode(line_tokens, morph, skip_first_n=0, skip_last_n=0):
    """Return (features_15, mode_label) or (None, None) if no valid tokens."""
    line_tokens_used = line_tokens
    if skip_first_n > 0:
        line_tokens_used = line_tokens_used[skip_first_n:]
    if skip_last_n > 0 and len(line_tokens_used) > skip_last_n:
        line_tokens_used = line_tokens_used[:-skip_last_n]

    head_counts = np.zeros(len(HEAD_TYPES))
    term_counts = np.zeros(len(TERM_TYPES))
    suffixes = []
    n_valid = 0

    for tok in line_tokens_used:
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m.middle:
            head, mods, term, frame = decompose_middle_hmt(m.middle)
            head = head if head else 'headless'
            if head in HEAD_IDX:
                head_counts[HEAD_IDX[head]] += 1
            if term in TERM_IDX:
                term_counts[TERM_IDX[term]] += 1
            n_valid += 1
        suffixes.append(m.suffix if m else None)

    if n_valid == 0:
        return None, None

    head_frac = head_counts / n_valid
    term_frac = term_counts / n_valid
    mode = get_line_mode(suffixes)
    mode_val = 1.0 if mode == 'A' else 0.0 if mode == 'B' else 0.5
    line_len = float(len(line_tokens_used))

    features = np.concatenate([head_frac, term_frac, [mode_val], [line_len]])
    return features, mode


def assemble_paragraphs():
    tx = Transcript()
    morph = Morphology()
    lines_dict = defaultdict(list)
    for t in tx.currier_b():
        w = t.word.strip()
        if not w:
            continue
        if t.placement.startswith('L'):
            continue
        lines_dict[(t.folio, t.line)].append(t)
    folio_lines = defaultdict(list)
    for (folio, line_num), tokens in sorted(lines_dict.items()):
        folio_lines[folio].append((line_num, tokens))
    paragraphs = {f: [t for _, t in lines] for f, lines in folio_lines.items() if len(lines) >= 3}
    return paragraphs, morph


# ---- Test 1: Within-mode vs cross-mode pair distances ----

def test_within_mode_pair_distances(paragraphs, morph):
    """For each consecutive line pair, classify by mode-pair type and measure feature distance."""
    pair_distances = defaultdict(list)
    line_mode_counts = Counter()

    for folio, line_token_lists in paragraphs.items():
        features = []
        modes = []
        for tokens in line_token_lists:
            f, m = build_line_features_and_mode(tokens, morph)
            if f is not None:
                features.append(f)
                modes.append(m if m else 'U')
                line_mode_counts[m if m else 'U'] += 1
        if len(features) < 2:
            continue
        for i in range(len(features) - 1):
            pair_type = f"{modes[i]}-{modes[i+1]}"
            dist = float(np.sum((features[i+1] - features[i]) ** 2))
            pair_distances[pair_type].append(dist)

    # Aggregate
    summary = {}
    for pair_type, dists in pair_distances.items():
        if dists:
            summary[pair_type] = {
                'n_pairs': len(dists),
                'mean_squared_dist': float(np.mean(dists)),
                'median_squared_dist': float(np.median(dists)),
                'std_squared_dist': float(np.std(dists)),
            }
    return summary, dict(line_mode_counts)


# ---- Test 2: Residualize by mode, recompute smoothness ----

def compute_mode_means(paragraphs, morph):
    """Compute mean feature vector across all mode-A lines, and across all mode-B lines."""
    mode_a_features = []
    mode_b_features = []
    mode_u_features = []
    for folio, line_token_lists in paragraphs.items():
        for tokens in line_token_lists:
            f, m = build_line_features_and_mode(tokens, morph)
            if f is None:
                continue
            if m == 'A':
                mode_a_features.append(f)
            elif m == 'B':
                mode_b_features.append(f)
            else:
                mode_u_features.append(f)
    means = {}
    if mode_a_features:
        means['A'] = np.mean(np.array(mode_a_features), axis=0)
    if mode_b_features:
        means['B'] = np.mean(np.array(mode_b_features), axis=0)
    if mode_u_features:
        means['U'] = np.mean(np.array(mode_u_features), axis=0)
    return means


def compute_smoothness_score(paragraphs, morph, residualize=False, mode_means=None):
    """Compute sum of squared consecutive differences across paragraphs.
    If residualize=True, subtract mode_mean from each line's features first.
    """
    total = 0.0
    n_pairs = 0
    for folio, line_token_lists in paragraphs.items():
        features = []
        for tokens in line_token_lists:
            f, m = build_line_features_and_mode(tokens, morph)
            if f is not None:
                if residualize and mode_means and m:
                    mode_key = m if m in mode_means else 'U'
                    if mode_key in mode_means:
                        f = f - mode_means[mode_key]
                features.append(f)
        if len(features) >= 2:
            features = np.array(features)
            diffs = np.diff(features, axis=0)
            total += float(np.sum(diffs ** 2))
            n_pairs += len(features) - 1
    return total, n_pairs


def shuffle_null_score(paragraphs, morph, n_shuffles=N_SHUFFLES, residualize=False, mode_means=None, seed=SEED):
    rng = np.random.default_rng(seed)
    # Pre-compute features per paragraph
    para_features = {}
    for folio, line_token_lists in paragraphs.items():
        features = []
        for tokens in line_token_lists:
            f, m = build_line_features_and_mode(tokens, morph)
            if f is None:
                continue
            if residualize and mode_means and m:
                mode_key = m if m in mode_means else 'U'
                if mode_key in mode_means:
                    f = f - mode_means[mode_key]
            features.append(f)
        if len(features) >= 2:
            para_features[folio] = np.array(features)

    null_scores = []
    for trial in range(n_shuffles):
        trial_total = 0.0
        for folio, feats in para_features.items():
            perm = rng.permutation(len(feats))
            permuted = feats[perm]
            diffs = np.diff(permuted, axis=0)
            trial_total += float(np.sum(diffs ** 2))
        null_scores.append(trial_total)
    return np.array(null_scores)


# ---- Test 3: Boundary tokens vs mode-transitions ----

def test_boundary_mode_transitions(paragraphs, morph):
    """For mode-transition line pairs vs same-mode line pairs, what's the difference
    in line-boundary structure (first/last 3 tokens)?"""
    # For each line, classify first-3 vs body atom composition
    transition_pair_count = 0
    same_pair_count = 0
    for folio, line_token_lists in paragraphs.items():
        prev_mode = None
        for i, tokens in enumerate(line_token_lists):
            f, m = build_line_features_and_mode(tokens, morph)
            if m is None:
                prev_mode = None
                continue
            if prev_mode is not None:
                if prev_mode != m:
                    transition_pair_count += 1
                else:
                    same_pair_count += 1
            prev_mode = m
    return {
        'n_transition_pairs': transition_pair_count,
        'n_same_mode_pairs': same_pair_count,
        'transition_rate': transition_pair_count / max(transition_pair_count + same_pair_count, 1),
    }


def main():
    print("=" * 80)
    print("PHASE_716 MODE-AWARE EXTENSION")
    print("=" * 80)

    print("\nAssembling Currier B paragraphs...")
    paragraphs, morph = assemble_paragraphs()
    print(f"  N paragraphs: {len(paragraphs)}")

    # ---- Test 1: Within-mode vs cross-mode pair distances ----
    print("\n" + "=" * 80)
    print("TEST 1: Line-pair squared feature distance by mode-pair type")
    print("=" * 80)
    pair_summary, mode_counts = test_within_mode_pair_distances(paragraphs, morph)

    print(f"\n  Line mode distribution: {dict(mode_counts)}")
    print(f"\n  Pair-type summary:")
    print(f"  {'Type':<10}{'N pairs':>10}{'mean d²':>12}{'median d²':>12}{'std d²':>12}")
    print(f"  {'-'*56}")
    for pair_type in sorted(pair_summary.keys()):
        d = pair_summary[pair_type]
        print(f"  {pair_type:<10}{d['n_pairs']:>10}{d['mean_squared_dist']:>12.4f}"
              f"{d['median_squared_dist']:>12.4f}{d['std_squared_dist']:>12.4f}")

    # Within-mode (A-A, B-B) vs cross-mode (A-B, B-A) comparison
    within_mode_d = []
    cross_mode_d = []
    for pair_type, d in pair_summary.items():
        if pair_type in ('A-A', 'B-B'):
            within_mode_d.append((d['n_pairs'], d['mean_squared_dist']))
        elif pair_type in ('A-B', 'B-A'):
            cross_mode_d.append((d['n_pairs'], d['mean_squared_dist']))

    if within_mode_d and cross_mode_d:
        # Weighted mean
        wm_total_n = sum(n for n, _ in within_mode_d)
        wm_mean = sum(n * d for n, d in within_mode_d) / wm_total_n
        cm_total_n = sum(n for n, _ in cross_mode_d)
        cm_mean = sum(n * d for n, d in cross_mode_d) / cm_total_n
        print(f"\n  Within-mode (A-A + B-B): n={wm_total_n}, mean d²={wm_mean:.4f}")
        print(f"  Cross-mode (A-B + B-A): n={cm_total_n}, mean d²={cm_mean:.4f}")
        print(f"  Ratio cross/within: {cm_mean/wm_mean:.3f}")
        if cm_mean > wm_mean * 1.20:
            print(f"  >> CROSS-MODE PAIRS HAVE ≥20% LARGER FEATURE DISTANCE (suggests mode-coherence drives smoothness)")
        else:
            print(f"  >> Within/cross distances comparable (mode-coherence weak/absent)")

    # ---- Test 2: Residualize by mode, recompute smoothness ----
    print("\n" + "=" * 80)
    print("TEST 2: Mode-residualization effect on smoothness")
    print("=" * 80)

    # Baseline (no residualization)
    obs_base, n_pairs_base = compute_smoothness_score(paragraphs, morph, residualize=False)
    nulls_base = shuffle_null_score(paragraphs, morph, n_shuffles=N_SHUFFLES, residualize=False)
    z_base = (obs_base - nulls_base.mean()) / nulls_base.std()
    print(f"\n  Baseline: obs={obs_base:.2f}, null_mean={nulls_base.mean():.2f}, "
          f"null_std={nulls_base.std():.2f}, z={z_base:+.3f}")

    # Mode-residualized
    mode_means = compute_mode_means(paragraphs, morph)
    print(f"  Mode means computed: {list(mode_means.keys())}")
    obs_resid, n_pairs_resid = compute_smoothness_score(paragraphs, morph, residualize=True, mode_means=mode_means)
    nulls_resid = shuffle_null_score(paragraphs, morph, n_shuffles=N_SHUFFLES, residualize=True, mode_means=mode_means)
    z_resid = (obs_resid - nulls_resid.mean()) / nulls_resid.std()
    print(f"  Mode-residualized: obs={obs_resid:.2f}, null_mean={nulls_resid.mean():.2f}, "
          f"null_std={nulls_resid.std():.2f}, z={z_resid:+.3f}")

    # Collapse calculation
    if z_base < 0 and z_resid < 0:
        collapse_pct = abs((z_base - z_resid) / z_base * 100)
    elif z_base < 0:
        collapse_pct = 100  # z_resid went non-negative or positive
    else:
        collapse_pct = 0
    print(f"  z magnitude collapse after mode residualization: {collapse_pct:.1f}%")

    if collapse_pct >= 80:
        verdict = "MODE-COHERENCE IS THE MECHANISM (≥80% collapse)"
    elif collapse_pct >= 50:
        verdict = "MODE-COHERENCE PARTIAL MECHANISM (50-80% collapse)"
    elif collapse_pct >= 20:
        verdict = "MODE-COHERENCE WEAK MECHANISM (20-50% collapse)"
    else:
        verdict = "MODE-COHERENCE NOT MAIN MECHANISM (<20% collapse)"
    print(f"  VERDICT: {verdict}")

    # ---- Test 3: Mode-transition rate ----
    print("\n" + "=" * 80)
    print("TEST 3: Mode-transition rate between consecutive lines")
    print("=" * 80)
    trans = test_boundary_mode_transitions(paragraphs, morph)
    print(f"\n  Same-mode pairs: {trans['n_same_mode_pairs']}")
    print(f"  Mode-transition pairs: {trans['n_transition_pairs']}")
    print(f"  Transition rate: {trans['transition_rate']:.4f}")

    if trans['transition_rate'] < 0.30:
        print(f"  >> Most pairs same-mode ({1-trans['transition_rate']:.2%}); paragraphs are mode-coherent")
    elif trans['transition_rate'] > 0.50:
        print(f"  >> Most pairs cross-mode; paragraphs are mode-alternating")
    else:
        print(f"  >> Mixed: paragraphs have moderate mode-switching")

    # ---- Save ----
    out = {
        'method': 'PHASE_716 mode-aware extension',
        'n_paragraphs': len(paragraphs),
        'n_shuffles': N_SHUFFLES,
        'test_1_pair_distances': pair_summary,
        'line_mode_counts': dict(mode_counts),
        'test_2_residualization': {
            'baseline': {
                'observed': obs_base, 'null_mean': float(nulls_base.mean()),
                'null_std': float(nulls_base.std()), 'z': z_base, 'n_pairs': n_pairs_base,
            },
            'mode_residualized': {
                'observed': obs_resid, 'null_mean': float(nulls_resid.mean()),
                'null_std': float(nulls_resid.std()), 'z': z_resid, 'n_pairs': n_pairs_resid,
            },
            'collapse_pct': collapse_pct,
            'verdict': verdict,
        },
        'test_3_transition_rate': trans,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
