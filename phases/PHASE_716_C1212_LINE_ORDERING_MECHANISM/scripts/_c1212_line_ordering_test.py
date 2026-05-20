"""PHASE_716: Test C1212 multi-step chaining as mechanism for C1727 line-ordering smoothness.

Reproduce C1727 baseline (z=-6.05 line-ordering smoothness within paragraphs) and
test whether excluding the first N tokens of each line collapses the effect.

If C1212 cross-line multi-step chaining IS the mechanism, excluding first 3 tokens
should remove ~80% of the smoothness signal (since C2048 found C1212 extends lag+2/+3).
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, decompose_middle_hmt

OUT_PATH = ROOT / 'phases' / 'PHASE_716_C1212_LINE_ORDERING_MECHANISM' / 'results' / 'c1212_line_ordering_results.json'

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


def build_line_features(line_tokens, morph, skip_first_n=0, skip_last_n=0):
    """Build 15-dim feature vector for a body line, optionally skipping first/last N tokens."""
    # Apply skip
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
        return None

    head_frac = head_counts / n_valid
    term_frac = term_counts / n_valid
    mode = get_line_mode(suffixes)
    mode_val = 1.0 if mode == 'A' else 0.0 if mode == 'B' else 0.5
    line_len = float(len(line_tokens_used))

    return np.concatenate([head_frac, term_frac, [mode_val], [line_len]])


def sequential_structure_score(feature_matrix):
    """Sum of squared consecutive differences."""
    if len(feature_matrix) < 2:
        return 0.0
    diffs = np.diff(feature_matrix, axis=0)
    return float(np.sum(diffs ** 2))


def assemble_paragraphs():
    """Load Currier B paragraphs (folio = paragraph for this test)."""
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
    # Group lines by folio (treating folio as paragraph for this test)
    folio_lines = defaultdict(list)
    for (folio, line_num), tokens in sorted(lines_dict.items()):
        folio_lines[folio].append((line_num, tokens))
    # Filter folios with ≥3 lines
    paragraphs = {f: [t for _, t in lines] for f, lines in folio_lines.items() if len(lines) >= 3}
    return paragraphs, morph


def compute_c1727_score(paragraphs, morph, skip_first_n=0, skip_last_n=0):
    """Compute sequential_structure_score across all paragraphs."""
    total_score = 0.0
    n_pairs = 0
    for folio, line_token_lists in paragraphs.items():
        features = []
        for tokens in line_token_lists:
            f = build_line_features(tokens, morph, skip_first_n, skip_last_n)
            if f is not None:
                features.append(f)
        if len(features) >= 2:
            features = np.array(features)
            total_score += sequential_structure_score(features)
            n_pairs += len(features) - 1
    return total_score, n_pairs


def shuffle_null(paragraphs, morph, n_shuffles=N_SHUFFLES, skip_first_n=0, skip_last_n=0, seed=SEED):
    """Shuffle line order within each paragraph, recompute score."""
    rng = np.random.default_rng(seed)
    null_scores = []
    # Pre-compute features per paragraph
    para_features = {}
    for folio, line_token_lists in paragraphs.items():
        features = []
        for tokens in line_token_lists:
            f = build_line_features(tokens, morph, skip_first_n, skip_last_n)
            if f is not None:
                features.append(f)
        if len(features) >= 2:
            para_features[folio] = np.array(features)

    for trial in range(n_shuffles):
        trial_score = 0.0
        for folio, features in para_features.items():
            perm = rng.permutation(len(features))
            permuted = features[perm]
            trial_score += sequential_structure_score(permuted)
        null_scores.append(trial_score)
    return np.array(null_scores)


def run_variant(paragraphs, morph, skip_first_n=0, skip_last_n=0, label=""):
    """Run one exclusion variant: compute observed score + null distribution + z."""
    obs_score, n_pairs = compute_c1727_score(paragraphs, morph, skip_first_n, skip_last_n)
    nulls = shuffle_null(paragraphs, morph, n_shuffles=N_SHUFFLES,
                        skip_first_n=skip_first_n, skip_last_n=skip_last_n)
    null_mean = float(nulls.mean())
    null_std = float(nulls.std())
    z = (obs_score - null_mean) / null_std if null_std > 0 else 0.0
    p_emp = float(np.mean(nulls <= obs_score))
    print(f"  {label:<30} obs={obs_score:.4f}  null={null_mean:.4f}±{null_std:.4f}  z={z:+.3f}  p_emp={p_emp:.4f}  n_pairs={n_pairs}")
    return {
        'label': label,
        'skip_first_n': skip_first_n,
        'skip_last_n': skip_last_n,
        'observed_score': obs_score,
        'null_mean': null_mean,
        'null_std': null_std,
        'z_score': z,
        'p_empirical': p_emp,
        'n_pairs': n_pairs,
    }


def main():
    print("=" * 80)
    print("PHASE_716 C1212 LINE-ORDERING MECHANISM TEST")
    print("=" * 80)

    print("\nAssembling Currier B paragraphs (folios with ≥3 lines)...")
    paragraphs, morph = assemble_paragraphs()
    print(f"  N folios (paragraphs): {len(paragraphs)}")
    n_lines = sum(len(lts) for lts in paragraphs.values())
    print(f"  Total lines: {n_lines}")

    # ---- Run variants ----
    print("\n" + "=" * 80)
    print("VARIANT RESULTS")
    print("=" * 80)
    print(f"{'Variant':<32}{'observed':>12}{'null_mean':>12}{'null_std':>11}{'z':>9}{'p_emp':>9}")
    print("-" * 95)

    results = {}

    # Baseline (reproduces C1727)
    results['baseline'] = run_variant(paragraphs, morph, 0, 0, "Baseline (full lines)")

    # First-N exclusions
    for n in [1, 2, 3, 5]:
        results[f'skip_first_{n}'] = run_variant(paragraphs, morph, n, 0,
                                                  f"Skip first {n} tokens")

    # Last-N exclusions (symmetric control)
    for n in [1, 2, 3, 5]:
        results[f'skip_last_{n}'] = run_variant(paragraphs, morph, 0, n,
                                                 f"Skip last {n} tokens")

    # Combined (both ends)
    results['skip_both_3'] = run_variant(paragraphs, morph, 3, 3,
                                          "Skip first 3 + last 3 tokens")

    # ---- Analysis ----
    print("\n" + "=" * 80)
    print("MECHANISM ANALYSIS")
    print("=" * 80)

    z_baseline = results['baseline']['z_score']
    print(f"\nBaseline z (C1727 reproduction target ≈ -6.05): {z_baseline:+.3f}")

    print(f"\nFirst-N exclusion effect:")
    for n in [1, 2, 3, 5]:
        z_n = results[f'skip_first_{n}']['z_score']
        delta = z_baseline - z_n
        pct_collapse = abs(delta / z_baseline * 100) if z_baseline != 0 else 0
        if z_baseline < 0 and z_n < 0:
            magnitude_change = (z_n - z_baseline) / z_baseline * 100  # positive = closer to 0
        else:
            magnitude_change = 0
        print(f"  Skip first {n}: z={z_n:+.3f}, magnitude-collapse={magnitude_change:+.1f}%")

    print(f"\nLast-N exclusion effect (symmetric control):")
    for n in [1, 2, 3, 5]:
        z_n = results[f'skip_last_{n}']['z_score']
        if z_baseline < 0 and z_n < 0:
            magnitude_change = (z_n - z_baseline) / z_baseline * 100
        else:
            magnitude_change = 0
        print(f"  Skip last {n}: z={z_n:+.3f}, magnitude-collapse={magnitude_change:+.1f}%")

    print(f"\nCombined first-3 + last-3:")
    z_both = results['skip_both_3']['z_score']
    if z_baseline < 0 and z_both < 0:
        magnitude_change_both = (z_both - z_baseline) / z_baseline * 100
    else:
        magnitude_change_both = 0
    print(f"  z={z_both:+.3f}, magnitude-collapse={magnitude_change_both:+.1f}%")

    # ---- Pre-registered verdict ----
    print("\n" + "=" * 80)
    print("PRE-REGISTERED VERDICT")
    print("=" * 80)

    z_skip3 = results['skip_first_3']['z_score']
    if z_baseline < 0 and z_skip3 < 0:
        collapse_pct = abs((z_baseline - z_skip3) / z_baseline * 100)
    else:
        collapse_pct = 0

    if z_skip3 < z_baseline * 0.5 - 0.1:
        # z became more negative — pathological
        verdict = "PATHOLOGICAL — exclusion methodology has confound"
    elif collapse_pct >= 80:
        verdict = "C1212 DOMINANT MECHANISM — multi-step chaining IS the line-ordering signature"
    elif collapse_pct >= 50:
        verdict = "C1212 PARTIAL MECHANISM — accounts for substantial portion of smoothness but not all"
    else:
        verdict = "C1212 NOT MECHANISM — line-ordering smoothness has other structural drivers"

    print(f"\n  Baseline z: {z_baseline:+.3f}")
    print(f"  Skip-first-3 z: {z_skip3:+.3f}")
    print(f"  Magnitude collapse: {collapse_pct:.1f}%")
    print(f"  VERDICT: {verdict}")

    # Symmetric check
    z_last3 = results['skip_last_3']['z_score']
    if z_baseline < 0 and z_last3 < 0:
        last_collapse_pct = abs((z_baseline - z_last3) / z_baseline * 100)
    else:
        last_collapse_pct = 0
    print(f"\n  Last-3 collapse (control): {last_collapse_pct:.1f}%")
    print(f"  Asymmetry: {(collapse_pct - last_collapse_pct):+.1f}pp (first vs last)")

    # Save
    out = {
        'method': 'PHASE_716 C1212 as mechanism for C1727 line-ordering smoothness',
        'n_paragraphs': len(paragraphs),
        'n_lines': n_lines,
        'n_shuffles': N_SHUFFLES,
        'results_by_variant': results,
        'baseline_z': z_baseline,
        'skip_first_3_z': z_skip3,
        'skip_last_3_z': z_last3,
        'collapse_first_3_pct': collapse_pct,
        'collapse_last_3_pct': last_collapse_pct,
        'verdict': verdict,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
