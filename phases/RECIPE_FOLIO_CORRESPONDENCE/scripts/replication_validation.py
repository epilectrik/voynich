"""
Phase 628 Script 2: Replication & Permutation Validation

T1: Cross-family replication (SAME 8D features, NO re-tuning)
T2: Wrong-regime null tests
T3: Random chapter specificity
T4: Within-family permutation test (THE decisive test)
T5: Known 4D baseline comparison
"""

import sys
import json
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from shared_628 import (
    load_family_chapters,
    load_regime_folios,
    load_pl_channel_features,
    load_b_operational_profiles,
    load_b_deployment_features,
    residual_match,
    cv_stability,
    permutation_test,
    round_floats,
    TUNED_DIMS,
    KNOWN_DIMS,
    RESULTS_DIR,
    N_PERM,
    N_CV,
)


# ============================================================
# Helpers
# ============================================================

def strip_internals(result: dict) -> dict:
    """Remove non-serializable internal arrays from a residual_match result."""
    return {k: v for k, v in result.items()
            if k not in ('dmat', 'pl_std', 'v_std')}


def print_match_table(result: dict, indent: int = 2) -> None:
    """Print a compact match table from a residual_match result."""
    pad = ' ' * indent
    print(f'{pad}{"Ch#":>4} {"Folio":<8} {"Dist":>7} {"2nd":>7} '
          f'{"Ratio":>6} {"Conf":>5}')
    print(f'{pad}{"----":>4} {"-----":<8} {"----":>7} {"---":>7} '
          f'{"-----":>6} {"----":>5}')
    for m in result['match_table']:
        conf = 'Y' if m['confident'] else ''
        print(f'{pad}{m["chapter_number"]:>4} {m["folio"]:<8} '
              f'{m["distance"]:7.4f} {m["second_distance"]:7.4f} '
              f'{m["ratio"]:6.3f} {conf:>5}')


def print_summary_line(label: str, result: dict, indent: int = 2) -> None:
    """Print a one-line summary of a residual_match result."""
    pad = ' ' * indent
    print(f'{pad}{label}: n_confident={result["n_confident"]}/{result["n_pl"]}, '
          f'mean_ratio={result["mean_ratio"]:.3f}, '
          f'mean_dist={result["mean_distance"]:.4f}, '
          f'unique_NN={result["n_unique_nn"]}/{result["n_v"]}')


# ============================================================
# T1: Cross-family replication
# ============================================================

def run_t1(op_profiles, deploy_features):
    """T1: Cross-family replication with frozen 8D features."""
    print('=' * 70)
    print('T1: CROSS-FAMILY REPLICATION (frozen 8D, no re-tuning)')
    print('=' * 70)
    print()

    families = [
        ('sublimation', 'REGIME_3'),
        ('fixation',    'REGIME_3'),
        ('dissolution', 'REGIME_1'),
    ]

    t1_out = {}

    for family, regime in families:
        chs = load_family_chapters(family)
        fols = load_regime_folios(regime)
        label = f'{family}_{regime}'
        print(f'  --- {family} ({len(chs)} chapters) -> {regime} ({len(fols)} folios) ---')

        result = residual_match(chs, fols, TUNED_DIMS, op_profiles, deploy_features)
        print_summary_line('Match', result, indent=4)
        print()
        print_match_table(result, indent=4)
        print()

        # CV stability
        cv = cv_stability(chs, fols, TUNED_DIMS,
                          op_profiles=op_profiles,
                          deploy_features=deploy_features)
        print(f'    CV consensus (>40%): {cv["n_consensus"]} / {cv["n_chapters"]}')
        print()

        t1_out[label] = {
            'matching': strip_internals(result),
            'cv': cv,
        }

    return t1_out


# ============================================================
# T2: Wrong-regime null tests
# ============================================================

def run_t2(op_profiles, deploy_features):
    """T2: Wrong-regime null tests -- distillation matched to wrong regimes."""
    print('=' * 70)
    print('T2: WRONG-REGIME NULL TESTS')
    print('=' * 70)
    print()

    dist_chs = load_family_chapters('distillation')

    tests = [
        ('REGIME_3', 'distillation_R3'),
        ('REGIME_4', 'distillation_R4'),
    ]

    t2_out = {}

    for regime, label in tests:
        fols = load_regime_folios(regime)
        print(f'  --- distillation ({len(dist_chs)} chapters) -> {regime} '
              f'({len(fols)} folios) ---')

        if len(fols) == 0:
            print(f'    WARNING: No folios in {regime}. Skipping.')
            t2_out[label] = {'error': f'No folios in {regime}'}
            print()
            continue

        result = residual_match(dist_chs, fols, TUNED_DIMS,
                                op_profiles, deploy_features)
        print_summary_line('Match', result, indent=4)
        print()
        print_match_table(result, indent=4)
        print()

        t2_out[label] = strip_internals(result)

    # Compare against training baseline
    print('  --- Comparison to training (distillation -> R1) ---')
    r1_fols = load_regime_folios('REGIME_1')
    train = residual_match(dist_chs, r1_fols, TUNED_DIMS,
                           op_profiles, deploy_features)
    print(f'    Training:  n_confident={train["n_confident"]}/{train["n_pl"]}, '
          f'mean_ratio={train["mean_ratio"]:.3f}')
    for label, data in t2_out.items():
        if 'error' in data:
            print(f'    {label}: (no folios)')
        else:
            print(f'    {label}: n_confident={data["n_confident"]}/{data["n_pl"]}, '
                  f'mean_ratio={data["mean_ratio"]:.3f}')
    print()

    return t2_out


# ============================================================
# T3: Random chapter specificity
# ============================================================

def run_t3(op_profiles, deploy_features):
    """T3: Random chapter specificity -- 100 trials of random chapters vs R1."""
    print('=' * 70)
    print('T3: RANDOM CHAPTER SPECIFICITY')
    print('=' * 70)
    print()

    # Load all non-theoretical chapters
    pl_feats = load_pl_channel_features()
    per_ch = pl_feats['T5_channel_signatures']['per_chapter']
    all_chs = [ch for ch in per_ch if ch.get('family') != 'theoretical']
    r1_fols = load_regime_folios('REGIME_1')

    n_sample = 16  # Same size as distillation family
    n_trials = 100

    print(f'  All non-theoretical chapters: {len(all_chs)}')
    print(f'  Sample size per trial: {n_sample}')
    print(f'  Target: REGIME_1 ({len(r1_fols)} folios)')
    print(f'  Trials: {n_trials}')
    print()

    rng = random.Random(628_777)
    trial_confident = []
    trial_ratios = []

    for trial in range(n_trials):
        sample = rng.sample(all_chs, n_sample)
        result = residual_match(sample, r1_fols, TUNED_DIMS,
                                op_profiles, deploy_features)
        trial_confident.append(result['n_confident'])
        trial_ratios.append(result['mean_ratio'])

        if (trial + 1) % 10 == 0:
            print(f'    Trial {trial + 1:3d}/{n_trials}: '
                  f'n_confident={result["n_confident"]}, '
                  f'mean_ratio={result["mean_ratio"]:.3f}')

    print()

    # Summary statistics
    mean_confident = sum(trial_confident) / n_trials
    mean_ratio = sum(trial_ratios) / n_trials
    max_confident = max(trial_confident)
    min_confident = min(trial_confident)
    training_confident = 9
    training_ratio = 1.284

    print(f'  Random trials summary:')
    print(f'    Mean confident:     {mean_confident:.2f}')
    print(f'    Mean ratio:         {mean_ratio:.3f}')
    print(f'    Max confident:      {max_confident}')
    print(f'    Min confident:      {min_confident}')
    print(f'    Training confident: {training_confident}')
    print(f'    Training ratio:     {training_ratio:.3f}')
    print()

    # Histogram of confident counts
    from collections import Counter
    hist = Counter(trial_confident)
    max_bin = max(hist.keys())
    min_bin = min(hist.keys())
    print(f'  Histogram of confident counts (n={n_trials}):')
    for val in range(min_bin, max_bin + 1):
        count = hist.get(val, 0)
        bar = '#' * count
        marker = ' <-- TRAINING' if val == training_confident else ''
        print(f'    {val:3d}: {count:3d} {bar}{marker}')

    # How many random trials meet or exceed training?
    n_exceed_confident = sum(1 for c in trial_confident if c >= training_confident)
    n_exceed_ratio = sum(1 for r in trial_ratios if r >= training_ratio)
    print()
    print(f'  Random >= training confident ({training_confident}): '
          f'{n_exceed_confident}/{n_trials} '
          f'(p={n_exceed_confident / n_trials:.3f})')
    print(f'  Random >= training ratio ({training_ratio:.3f}): '
          f'{n_exceed_ratio}/{n_trials} '
          f'(p={n_exceed_ratio / n_trials:.3f})')
    print()

    return {
        'n_trials': n_trials,
        'n_sample_per_trial': n_sample,
        'mean_confident': round(mean_confident, 2),
        'mean_ratio': round(mean_ratio, 3),
        'max_confident': max_confident,
        'min_confident': min_confident,
        'training_confident': training_confident,
        'training_ratio': training_ratio,
        'n_exceed_confident': n_exceed_confident,
        'n_exceed_ratio': n_exceed_ratio,
        'p_confident': round(n_exceed_confident / n_trials, 4),
        'p_ratio': round(n_exceed_ratio / n_trials, 4),
        'trial_confident': trial_confident,
        'trial_ratios': [round(r, 4) for r in trial_ratios],
    }


# ============================================================
# T4: Within-family permutation test (THE decisive test)
# ============================================================

def run_t4(op_profiles, deploy_features):
    """T4: Permutation test -- shuffled chapter-folio assignments."""
    print('=' * 70)
    print('T4: WITHIN-FAMILY PERMUTATION TEST (THE DECISIVE TEST)')
    print('=' * 70)
    print()

    dist_chs = load_family_chapters('distillation')
    r1_fols = load_regime_folios('REGIME_1')

    print(f'  Family: distillation ({len(dist_chs)} chapters)')
    print(f'  Regime: REGIME_1 ({len(r1_fols)} folios)')
    print(f'  Permutations: {N_PERM}')
    print(f'  Pass criterion: p < 0.05 (real in top 5%)')
    print()
    print(f'  Running {N_PERM} permutations (this may take a while)...')

    perm = permutation_test(dist_chs, r1_fols, TUNED_DIMS,
                            n_perm=N_PERM,
                            op_profiles=op_profiles,
                            deploy_features=deploy_features)

    print()
    print(f'  Results:')
    print(f'    {"Metric":<25} {"Real":>10} {"Null mean":>10} {"p-value":>10} '
          f'{"Pctile":>8}')
    print(f'    {"-" * 25} {"-" * 10} {"-" * 10} {"-" * 10} {"-" * 8}')

    print(f'    {"mean_ratio":<25} {perm["real_mean_ratio"]:10.4f} '
          f'{perm["perm_mean_ratio_mean"]:10.4f} '
          f'{perm["p_ratio"]:10.4f} '
          f'{perm["percentile_ratio"]:7.1f}%')

    print(f'    {"n_confident":<25} {perm["real_n_confident"]:10d} '
          f'{perm["perm_mean_confident_mean"]:10.2f} '
          f'{perm["p_confident"]:10.4f} '
          f'{perm["percentile_confident"]:7.1f}%')

    print(f'    {"mean_distance":<25} {perm["real_mean_distance"]:10.4f} '
          f'{perm["perm_mean_distance_mean"]:10.4f} '
          f'{perm["p_distance"]:10.4f} '
          f'{"":>8}')

    print()

    # Verdict
    passed_ratio = perm['p_ratio'] < 0.05
    passed_confident = perm['p_confident'] < 0.05

    if passed_ratio and passed_confident:
        verdict = 'PASS -- both ratio and confident p < 0.05'
    elif passed_ratio or passed_confident:
        metric = 'ratio' if passed_ratio else 'confident'
        verdict = f'PARTIAL -- {metric} passes (p < 0.05), other does not'
    else:
        verdict = 'FAIL -- neither metric reaches p < 0.05'

    print(f'  VERDICT: {verdict}')
    print(f'    p(ratio):     {perm["p_ratio"]:.4f} '
          f'{"< 0.05 PASS" if passed_ratio else ">= 0.05 FAIL"}')
    print(f'    p(confident): {perm["p_confident"]:.4f} '
          f'{"< 0.05 PASS" if passed_confident else ">= 0.05 FAIL"}')
    print()

    return perm


# ============================================================
# T5: Known 4D baseline comparison
# ============================================================

def run_t5(op_profiles, deploy_features):
    """T5: Compare 4D known-channel baseline to 8D tuned dimensions."""
    print('=' * 70)
    print('T5: KNOWN 4D BASELINE vs TUNED 8D')
    print('=' * 70)
    print()

    dist_chs = load_family_chapters('distillation')
    r1_fols = load_regime_folios('REGIME_1')

    print(f'  Distillation ({len(dist_chs)} chapters) -> R1 ({len(r1_fols)} folios)')
    print(f'  Known 4D dims: {len(KNOWN_DIMS)}')
    print(f'  Tuned 8D dims: {len(TUNED_DIMS)}')
    print()

    # 4D matching
    print('  --- 4D Matching (known channels only) ---')
    result_4d = residual_match(dist_chs, r1_fols, KNOWN_DIMS,
                               op_profiles, deploy_features)
    print_summary_line('4D', result_4d, indent=4)
    print()
    print_match_table(result_4d, indent=4)
    print()

    # 4D CV stability
    cv_4d = cv_stability(dist_chs, r1_fols, KNOWN_DIMS,
                         op_profiles=op_profiles,
                         deploy_features=deploy_features)
    print(f'    4D CV consensus (>40%): {cv_4d["n_consensus"]} / {cv_4d["n_chapters"]}')
    print()

    # 8D matching (for comparison)
    print('  --- 8D Matching (tuned dimensions) ---')
    result_8d = residual_match(dist_chs, r1_fols, TUNED_DIMS,
                               op_profiles, deploy_features)
    print_summary_line('8D', result_8d, indent=4)
    print()

    cv_8d = cv_stability(dist_chs, r1_fols, TUNED_DIMS,
                         op_profiles=op_profiles,
                         deploy_features=deploy_features)
    print(f'    8D CV consensus (>40%): {cv_8d["n_consensus"]} / {cv_8d["n_chapters"]}')
    print()

    # Comparison table
    print('  --- Comparison ---')
    print(f'    {"Metric":<25} {"4D":>10} {"8D":>10} {"Delta":>10}')
    print(f'    {"-" * 25} {"-" * 10} {"-" * 10} {"-" * 10}')

    metrics = [
        ('n_confident', result_4d['n_confident'], result_8d['n_confident']),
        ('mean_ratio', result_4d['mean_ratio'], result_8d['mean_ratio']),
        ('mean_distance', result_4d['mean_distance'], result_8d['mean_distance']),
        ('unique_NN', result_4d['n_unique_nn'], result_8d['n_unique_nn']),
        ('CV_consensus', cv_4d['n_consensus'], cv_8d['n_consensus']),
    ]

    for name, val_4d, val_8d in metrics:
        if isinstance(val_4d, int):
            delta = val_8d - val_4d
            print(f'    {name:<25} {val_4d:10d} {val_8d:10d} {delta:+10d}')
        else:
            delta = val_8d - val_4d
            print(f'    {name:<25} {val_4d:10.3f} {val_8d:10.3f} {delta:+10.3f}')

    print()

    # Check which folios differ between 4D and 8D assignments
    matches_4d = {m['chapter_number']: m['folio'] for m in result_4d['match_table']}
    matches_8d = {m['chapter_number']: m['folio'] for m in result_8d['match_table']}
    all_ch_nums = sorted(set(matches_4d.keys()) | set(matches_8d.keys()))

    n_same = sum(1 for ch in all_ch_nums
                 if matches_4d.get(ch) == matches_8d.get(ch))
    n_diff = len(all_ch_nums) - n_same

    print(f'  Assignment agreement: {n_same}/{len(all_ch_nums)} same, '
          f'{n_diff}/{len(all_ch_nums)} differ')

    if n_diff > 0:
        print(f'  Changed assignments:')
        for ch in all_ch_nums:
            f4 = matches_4d.get(ch, '-')
            f8 = matches_8d.get(ch, '-')
            if f4 != f8:
                print(f'    Ch{ch}: {f4} (4D) -> {f8} (8D)')
    print()

    return {
        'matching_4d': strip_internals(result_4d),
        'cv_4d': cv_4d,
        'matching_8d': strip_internals(result_8d),
        'cv_8d': cv_8d,
        'comparison': {
            'n_same_assignment': n_same,
            'n_different_assignment': n_diff,
            'n_total': len(all_ch_nums),
        },
    }


# ============================================================
# Main
# ============================================================

def main():
    print('Phase 628 Script 2: Replication & Permutation Validation')
    print('=' * 70)
    print()

    # Pre-load shared data ONCE
    print('Loading operational profiles and deployment features...')
    op_profiles = load_b_operational_profiles()
    deploy_features, _ = load_b_deployment_features()
    print('Done.')
    print()

    # T1: Cross-family replication
    t1_out = run_t1(op_profiles, deploy_features)

    # T2: Wrong-regime null tests
    t2_out = run_t2(op_profiles, deploy_features)

    # T3: Random chapter specificity
    t3_out = run_t3(op_profiles, deploy_features)

    # T4: Within-family permutation test
    t4_out = run_t4(op_profiles, deploy_features)

    # T5: Known 4D baseline comparison
    t5_out = run_t5(op_profiles, deploy_features)

    # ---- Save output ----
    output = {
        'T1_cross_family_replication': round_floats(t1_out, 4),
        'T2_wrong_regime_null': round_floats(t2_out, 4),
        'T3_random_specificity': round_floats(t3_out, 4),
        'T4_permutation_test': round_floats(t4_out, 4),
        'T5_known_4d_baseline': round_floats(t5_out, 4),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'replication_validation.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f'Output saved: {out_path}')
    print()

    # ---- Final summary ----
    print('=' * 70)
    print('FINAL SUMMARY')
    print('=' * 70)
    print()

    # T1 summary
    print('T1 Cross-family replication:')
    for key, data in t1_out.items():
        m = data['matching']
        cv = data['cv']
        print(f'  {key}: confident={m["n_confident"]}/{m["n_pl"]}, '
              f'ratio={m["mean_ratio"]:.3f}, '
              f'CV_consensus={cv["n_consensus"]}/{cv["n_chapters"]}')
    print()

    # T2 summary
    print('T2 Wrong-regime null:')
    for key, data in t2_out.items():
        if 'error' in data:
            print(f'  {key}: {data["error"]}')
        else:
            print(f'  {key}: confident={data["n_confident"]}/{data["n_pl"]}, '
                  f'ratio={data["mean_ratio"]:.3f}')
    print()

    # T3 summary
    print(f'T3 Random specificity ({t3_out["n_trials"]} trials):')
    print(f'  Random mean confident: {t3_out["mean_confident"]:.2f} '
          f'(training: {t3_out["training_confident"]})')
    print(f'  Random mean ratio:     {t3_out["mean_ratio"]:.3f} '
          f'(training: {t3_out["training_ratio"]:.3f})')
    print(f'  p(confident >= training): {t3_out["p_confident"]:.4f}')
    print(f'  p(ratio >= training):     {t3_out["p_ratio"]:.4f}')
    print()

    # T4 summary
    print('T4 Permutation test (DECISIVE):')
    print(f'  Real mean_ratio:  {t4_out["real_mean_ratio"]:.4f} '
          f'(null: {t4_out["perm_mean_ratio_mean"]:.4f})')
    print(f'  Real n_confident: {t4_out["real_n_confident"]} '
          f'(null: {t4_out["perm_mean_confident_mean"]:.2f})')
    print(f'  p(ratio):     {t4_out["p_ratio"]:.4f}')
    print(f'  p(confident): {t4_out["p_confident"]:.4f}')

    passed = t4_out['p_ratio'] < 0.05 or t4_out['p_confident'] < 0.05
    print(f'  VERDICT: {"PASS" if passed else "FAIL"}')
    print()

    # T5 summary
    t5_comp = t5_out['comparison']
    m4 = t5_out['matching_4d']
    m8 = t5_out['matching_8d']
    print('T5 Known 4D vs Tuned 8D:')
    print(f'  4D: confident={m4["n_confident"]}/{m4["n_pl"]}, '
          f'ratio={m4["mean_ratio"]:.3f}')
    print(f'  8D: confident={m8["n_confident"]}/{m8["n_pl"]}, '
          f'ratio={m8["mean_ratio"]:.3f}')
    print(f'  Assignment agreement: '
          f'{t5_comp["n_same_assignment"]}/{t5_comp["n_total"]}')
    print()

    print('Done.')


if __name__ == '__main__':
    main()
