"""PHASE_712: Thermodynamic kinetics test for kernel.

Test whether kernel dynamics (k/h excitation → e recovery) follow Newton's law
of cooling — specific exponential-approach-to-equilibrium signature.

Three sub-tests pre-registered in INDEX.md:
  A. Cooling-curve shape (exponential vs linear vs constant)
  B. Excursion-magnitude → recovery-time scaling (log vs linear)
  C. Onset-vs-recovery asymmetry

Compared across:
  - Voynich Currier B (target)
  - Voynich shuffled within-line (null)
  - Mensural duration streams (non-thermal structured-symbolic floor)
  - Synthetic Newton's cooling (positive control)
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

OUT_PATH = ROOT / 'phases' / 'PHASE_712_THERMO_KINETICS' / 'results' / 'thermo_kinetics_results.json'

random.seed(42)
np.random.seed(42)

MAX_LAG = 12


# ---- Label construction ----

def label_token_voynich(token, morph_obj=None):
    """Label per PHYS kernel classification (phases/PHYS_physics_stress_test/check_kernel.py):
      excited (k-class): token ends with 'k' OR is in {'ok','yk','ak','ek'}
      excited (h-class): token ends with 'h' OR is in {'oh','yh','ah','eh'}
      stable (e-class): token ends with 'ey','eey','edy','dy' (recognizable e-closure suffixes)
      none: anything else
    Kernel state is determined by TERMINAL closure pattern, not MIDDLE composition.
    """
    if not token:
        return 'none'
    w = token.lower()
    if w.endswith('k') or w in {'ok', 'yk', 'ak', 'ek'}:
        return 'excited'  # k-terminal excitation
    if w.endswith('h') or w in {'oh', 'yh', 'ah', 'eh'}:
        return 'excited'  # h-terminal excitation
    if w.endswith('ey') or w.endswith('eey') or w.endswith('edy') or w.endswith('dy'):
        return 'stable'   # e-suffix closure
    return 'none'


def build_voynich_labels(currier='B'):
    """Build per-line label sequences for Currier B P-placement."""
    tx = Transcript()
    morph = Morphology()
    lines = defaultdict(list)
    for t in tx.all(h_only=True):
        if not t.word.strip() or '*' in t.word:
            continue
        if t.language != currier:
            continue
        if not (t.placement and t.placement.startswith('P')):
            continue
        lines[(t.folio, t.line)].append(t.word.lower())
    # Convert to label sequences
    seqs = []
    for key in sorted(lines.keys()):
        seq = [label_token_voynich(w, morph) for w in lines[key]]
        if len(seq) >= 5:
            seqs.append(seq)
    return seqs


def build_voynich_shuffled_labels(seqs):
    """Within-line shuffle of label sequences (preserves composition, breaks order)."""
    out = []
    for seq in seqs:
        s = seq.copy()
        random.shuffle(s)
        out.append(s)
    return out


def build_mensural_labels():
    """Mensural duration streams: classify by duration value.
    excited = LON or MAX (long durations); stable = SMN/FUS/SFS (short); none = BRE/SBR/MIN (mid)
    """
    p = ROOT / 'phases' / 'MENSURAL_NOTATION_HYPOTHESIS' / 'results' / 'mensural_streams.json'
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding='utf-8'))
    seqs = []
    excited_set = {'LON', 'MAX'}
    stable_set = {'SMN', 'FUS', 'SFS'}
    for motet, voices in data.get('per_motet', {}).items():
        for vid, voice in voices.items():
            seq = []
            for tok in voice.get('dur', []):
                if tok.endswith('R'):
                    continue  # skip rests
                cls = tok.rstrip('+-')
                if cls in excited_set:
                    seq.append('excited')
                elif cls in stable_set:
                    seq.append('stable')
                else:
                    seq.append('none')
            if len(seq) >= 5:
                seqs.append(seq)
    return seqs


def build_synthetic_newton(n_total_tokens=30000, mean_line_len=15,
                            tau=2.0, excit_rate=0.008, baseline_stable=0.36):
    """Generate synthetic stream with Newton's-cooling-style recovery dynamics.
    After each excitation event, P(stable) recovers exponentially from 0 to baseline.
    """
    rng = np.random.default_rng(42)
    seqs = []
    tokens_made = 0
    while tokens_made < n_total_tokens:
        line_len = max(5, int(rng.poisson(mean_line_len)))
        seq = []
        last_excit_pos = -100  # far in past = full baseline
        for i in range(line_len):
            # Decide excitation
            if rng.random() < excit_rate:
                seq.append('excited')
                last_excit_pos = i
                continue
            # Time since last excitation
            t_since = i - last_excit_pos
            # P(stable) recovers exponentially toward baseline
            p_stable = baseline_stable * (1 - math.exp(-t_since / tau))
            if rng.random() < p_stable:
                seq.append('stable')
            else:
                seq.append('none')
        seqs.append(seq)
        tokens_made += len(seq)
    return seqs


# ---- Test A: Cooling curve ----

def compute_cooling_curve(seqs, max_lag=MAX_LAG):
    """For each excited token, measure stable-fraction at lags 1..max_lag forward.
    Returns: (curve, n_events, baseline_stable_rate)
    """
    counts = np.zeros(max_lag)
    totals = np.zeros(max_lag)
    n_events = 0
    all_labels = [lab for seq in seqs for lab in seq]
    baseline = sum(1 for l in all_labels if l == 'stable') / len(all_labels) if all_labels else 0

    for seq in seqs:
        n = len(seq)
        for i, lab in enumerate(seq):
            if lab != 'excited':
                continue
            n_events += 1
            for lag in range(1, max_lag + 1):
                if i + lag >= n:
                    break
                totals[lag - 1] += 1
                if seq[i + lag] == 'stable':
                    counts[lag - 1] += 1
    fracs = counts / np.maximum(totals, 1)
    return fracs, n_events, baseline


def fit_exponential_recovery(curve, baseline):
    """Fit e(t) = baseline + (e_0 - baseline) * exp(-t/tau).
    Returns: tau, e_0, sse, params
    """
    from scipy.optimize import curve_fit
    t = np.arange(1, len(curve) + 1, dtype=float)
    def model(t, e0, tau):
        return baseline + (e0 - baseline) * np.exp(-t / tau)
    try:
        popt, _ = curve_fit(model, t, curve, p0=[curve[0], 2.0],
                            bounds=([0, 0.1], [1, 50]), maxfev=5000)
        e_0, tau = popt
        pred = model(t, *popt)
        sse = float(np.sum((curve - pred) ** 2))
        return {'tau': float(tau), 'e_0': float(e_0), 'sse': sse,
                'fit_curve': pred.tolist(),
                'n_params': 2}
    except Exception as ex:
        return {'error': str(ex), 'n_params': 2, 'sse': float('inf')}


def fit_linear(curve, baseline):
    """Fit e(t) = baseline + slope * t (simple linear).
    Returns: slope, intercept, sse
    """
    t = np.arange(1, len(curve) + 1, dtype=float)
    A = np.vstack([t, np.ones_like(t)]).T
    slope, intercept = np.linalg.lstsq(A, curve, rcond=None)[0]
    pred = slope * t + intercept
    sse = float(np.sum((curve - pred) ** 2))
    return {'slope': float(slope), 'intercept': float(intercept),
            'sse': sse, 'fit_curve': pred.tolist(), 'n_params': 2}


def fit_constant(curve, baseline):
    """Fit e(t) = c (constant — no kinetic structure)."""
    c = float(np.mean(curve))
    pred = np.full_like(curve, c)
    sse = float(np.sum((curve - pred) ** 2))
    return {'constant': c, 'sse': sse, 'fit_curve': pred.tolist(), 'n_params': 1}


def aic(sse, n_obs, n_params):
    """AIC = 2k + n*log(SSE/n)."""
    if sse <= 0:
        return float('inf')
    return 2 * n_params + n_obs * math.log(sse / n_obs)


# ---- Test B: Excursion magnitude vs recovery time ----

def measure_excursion_episodes(seqs):
    """Cluster consecutive excited tokens into episodes.
    Return list of (magnitude, recovery_time) tuples.
    """
    episodes = []
    for seq in seqs:
        n = len(seq)
        i = 0
        while i < n:
            if seq[i] != 'excited':
                i += 1
                continue
            # Start of excursion
            start = i
            while i < n and seq[i] == 'excited':
                i += 1
            end = i  # first non-excited position
            magnitude = end - start

            # Recovery: find first position where we see 3 consecutive stable tokens
            recovery = None
            stable_run = 0
            for j in range(end, n):
                if seq[j] == 'stable':
                    stable_run += 1
                    if stable_run >= 3:
                        recovery = j - end - 2  # position of FIRST of the 3 stable
                        break
                else:
                    stable_run = 0
            if recovery is None:
                # Fallback: first single stable token
                for j in range(end, n):
                    if seq[j] == 'stable':
                        recovery = j - end
                        break
            if recovery is not None:
                episodes.append({'magnitude': magnitude, 'recovery_time': recovery})
    return episodes


def regression_scaling(episodes):
    """Test recovery_time ~ log(magnitude+1) vs recovery_time ~ magnitude."""
    if len(episodes) < 5:
        return {'error': 'too few episodes', 'n_episodes': len(episodes)}
    mags = np.array([e['magnitude'] for e in episodes], dtype=float)
    recs = np.array([e['recovery_time'] for e in episodes], dtype=float)

    # Linear regression: recovery_time ~ a*log(magnitude+1) + b
    x_log = np.log(mags + 1)
    A_log = np.vstack([x_log, np.ones_like(x_log)]).T
    coeffs_log, _, _, _ = np.linalg.lstsq(A_log, recs, rcond=None)
    pred_log = A_log @ coeffs_log
    ss_res_log = np.sum((recs - pred_log) ** 2)
    ss_tot = np.sum((recs - np.mean(recs)) ** 2)
    r2_log = 1 - ss_res_log / max(ss_tot, 1e-9)

    # Linear regression: recovery_time ~ a*magnitude + b
    A_lin = np.vstack([mags, np.ones_like(mags)]).T
    coeffs_lin, _, _, _ = np.linalg.lstsq(A_lin, recs, rcond=None)
    pred_lin = A_lin @ coeffs_lin
    ss_res_lin = np.sum((recs - pred_lin) ** 2)
    r2_lin = 1 - ss_res_lin / max(ss_tot, 1e-9)

    return {
        'n_episodes': len(episodes),
        'mean_magnitude': float(mags.mean()),
        'max_magnitude': float(mags.max()),
        'mean_recovery_time': float(recs.mean()),
        'r2_log_scaling': float(r2_log),
        'r2_linear_scaling': float(r2_lin),
        'log_slope': float(coeffs_log[0]),
        'linear_slope': float(coeffs_lin[0]),
    }


# ---- Test C: Onset vs recovery asymmetry ----

def measure_onset_recovery_asymmetry(seqs):
    """For each excursion episode, compute onset (tokens since last stable) and
    recovery (tokens until next stable)."""
    onsets = []
    recoveries = []
    for seq in seqs:
        n = len(seq)
        i = 0
        while i < n:
            if seq[i] != 'excited':
                i += 1
                continue
            start = i
            while i < n and seq[i] == 'excited':
                i += 1
            end = i

            # Onset = tokens since last stable BEFORE start
            onset = None
            for j in range(start - 1, -1, -1):
                if seq[j] == 'stable':
                    onset = start - j - 1
                    break
            # Recovery = tokens until next stable AFTER end
            recovery = None
            for j in range(end, n):
                if seq[j] == 'stable':
                    recovery = j - end
                    break

            if onset is not None and recovery is not None:
                onsets.append(onset)
                recoveries.append(recovery)
    if not onsets:
        return None
    return {
        'n_events': len(onsets),
        'mean_onset': float(np.mean(onsets)),
        'mean_recovery': float(np.mean(recoveries)),
        'median_onset': float(np.median(onsets)),
        'median_recovery': float(np.median(recoveries)),
        'onset_recovery_ratio_mean': float(np.mean(onsets) / max(np.mean(recoveries), 1e-9)),
        'onset_recovery_ratio_median': float(np.median(onsets) / max(np.median(recoveries), 1e-9)),
    }


# ---- Per-corpus runner ----

def run_corpus(label, seqs):
    print(f"\n{'='*70}\n{label}\n{'='*70}")
    if not seqs:
        return {'label': label, 'error': 'no data'}

    n_lines = len(seqs)
    n_tokens = sum(len(s) for s in seqs)
    n_excited = sum(1 for s in seqs for lab in s if lab == 'excited')
    n_stable = sum(1 for s in seqs for lab in s if lab == 'stable')
    n_none = n_tokens - n_excited - n_stable
    print(f"  N lines: {n_lines}, N tokens: {n_tokens}")
    print(f"  excited: {n_excited} ({n_excited/n_tokens:.2%}), "
          f"stable: {n_stable} ({n_stable/n_tokens:.2%}), "
          f"none: {n_none} ({n_none/n_tokens:.2%})")

    # ---- Test A: Cooling curve ----
    curve, n_events, baseline = compute_cooling_curve(seqs)
    print(f"\n  Cooling curve (lag 1..{MAX_LAG} stable-fraction, baseline={baseline:.4f}):")
    print(f"    {[f'{x:.3f}' for x in curve]}")
    print(f"    n_escalation_events={n_events}")

    fit_exp = fit_exponential_recovery(curve, baseline)
    fit_lin = fit_linear(curve, baseline)
    fit_con = fit_constant(curve, baseline)

    aic_exp = aic(fit_exp.get('sse', float('inf')), len(curve), fit_exp.get('n_params', 2))
    aic_lin = aic(fit_lin['sse'], len(curve), fit_lin['n_params'])
    aic_con = aic(fit_con['sse'], len(curve), fit_con['n_params'])
    if 'error' in fit_exp:
        print(f"    Exp fit FAILED: {fit_exp['error']}")
    else:
        print(f"    Exp fit:    tau={fit_exp['tau']:.3f}, e_0={fit_exp['e_0']:.4f}, SSE={fit_exp['sse']:.6f}, AIC={aic_exp:.2f}")
    print(f"    Lin fit:    slope={fit_lin['slope']:+.4f}, SSE={fit_lin['sse']:.6f}, AIC={aic_lin:.2f}")
    print(f"    Const fit:  c={fit_con['constant']:.4f}, SSE={fit_con['sse']:.6f}, AIC={aic_con:.2f}")
    delta_aic_vs_lin = aic_lin - aic_exp
    delta_aic_vs_con = aic_con - aic_exp
    print(f"    ΔAIC (lin - exp): {delta_aic_vs_lin:+.2f}  (positive = exponential better)")
    print(f"    ΔAIC (con - exp): {delta_aic_vs_con:+.2f}  (positive = exponential better)")
    test_a_pass_strong = (delta_aic_vs_lin >= 10) and (delta_aic_vs_con >= 10)
    test_a_pass_weak = (delta_aic_vs_lin >= 4) and (delta_aic_vs_con >= 4)
    print(f"    Test A strong PASS (ΔAIC≥10 both): {test_a_pass_strong}")
    print(f"    Test A weak PASS (ΔAIC≥4 both):    {test_a_pass_weak}")

    # Determine direction of approach
    if 'error' not in fit_exp:
        if fit_exp['e_0'] < baseline - 0.02:
            direction = 'DEPLETED→RECOVERY (Newton)'
        elif fit_exp['e_0'] > baseline + 0.02:
            direction = 'ELEVATED→DECAY (overshoot)'
        else:
            direction = 'No initial perturbation'
    else:
        direction = 'fit failed'
    print(f"    Curve shape: {direction}")

    # ---- Test B: Scaling ----
    episodes = measure_excursion_episodes(seqs)
    scaling = regression_scaling(episodes)
    print(f"\n  Excursion episodes: {scaling.get('n_episodes', 0)}")
    if 'error' not in scaling:
        print(f"    mean_magnitude={scaling['mean_magnitude']:.2f}, max={scaling['max_magnitude']:.0f}")
        print(f"    mean_recovery_time={scaling['mean_recovery_time']:.2f}")
        print(f"    R² log(mag+1) → recovery: {scaling['r2_log_scaling']:+.3f}")
        print(f"    R² magnitude → recovery:  {scaling['r2_linear_scaling']:+.3f}")
        test_b_pass = scaling['r2_log_scaling'] >= 0.3
        print(f"    Test B PASS (R² log ≥ 0.3): {test_b_pass}")
    else:
        test_b_pass = False

    # ---- Test C: Asymmetry ----
    asym = measure_onset_recovery_asymmetry(seqs)
    if asym:
        print(f"\n  Onset-vs-recovery asymmetry:")
        print(f"    mean_onset={asym['mean_onset']:.2f}, mean_recovery={asym['mean_recovery']:.2f}")
        print(f"    median_onset={asym['median_onset']:.2f}, median_recovery={asym['median_recovery']:.2f}")
        print(f"    ratio (median onset/recovery): {asym['onset_recovery_ratio_median']:.3f}")
        ratio = asym['onset_recovery_ratio_median']
        test_c_pass = (ratio < 0.8) or (ratio > 1.2)
        print(f"    Test C PASS (ratio outside [0.8, 1.2]): {test_c_pass}")
    else:
        test_c_pass = False

    return {
        'label': label,
        'n_lines': n_lines,
        'n_tokens': n_tokens,
        'n_excited': n_excited,
        'n_stable': n_stable,
        'baseline_stable_rate': baseline,
        'n_escalation_events': n_events,
        'cooling_curve': curve.tolist(),
        'fit_exponential': fit_exp,
        'fit_linear': fit_lin,
        'fit_constant': fit_con,
        'aic_exponential': aic_exp,
        'aic_linear': aic_lin,
        'aic_constant': aic_con,
        'delta_aic_exp_vs_linear': delta_aic_vs_lin,
        'delta_aic_exp_vs_constant': delta_aic_vs_con,
        'curve_shape_direction': direction,
        'test_A_strong': test_a_pass_strong,
        'test_A_weak': test_a_pass_weak,
        'scaling': scaling,
        'test_B_pass': test_b_pass,
        'asymmetry': asym,
        'test_C_pass': test_c_pass,
    }


def main():
    print("=" * 70)
    print("PHASE_712 THERMODYNAMIC KINETICS TEST FOR KERNEL")
    print("=" * 70)

    print("\nBuilding label sequences...")
    voy_seqs = build_voynich_labels('B')
    voy_shuf = build_voynich_shuffled_labels(voy_seqs)
    mens_seqs = build_mensural_labels()
    synth_seqs = build_synthetic_newton()

    results = {}
    results['voynich_B'] = run_corpus('Voynich Currier B', voy_seqs)
    results['voynich_shuffled'] = run_corpus('Voynich Shuffled (within-line)', voy_shuf)
    if mens_seqs is not None:
        results['mensural'] = run_corpus('Mensural duration streams', mens_seqs)
    results['synthetic_newton'] = run_corpus('Synthetic Newton τ=2', synth_seqs)

    # ---- Cross-corpus verdict ----
    print("\n" + "=" * 70)
    print("CROSS-CORPUS VERDICT")
    print("=" * 70)
    print(f"\n{'Corpus':<32}{'ΔAIC(exp-lin)':>14}{'ΔAIC(exp-con)':>14}{'shape':>30}{'R²log':>8}{'asym':>8}")
    print("-" * 110)
    for key, r in results.items():
        if 'error' in r:
            print(f"{r['label']:<32}  ERROR")
            continue
        shape = r['curve_shape_direction'][:28]
        r2 = r['scaling'].get('r2_log_scaling', float('nan')) if 'error' not in r.get('scaling', {}) else float('nan')
        ratio = r['asymmetry'].get('onset_recovery_ratio_median', float('nan')) if r['asymmetry'] else float('nan')
        print(f"{r['label']:<32}{r['delta_aic_exp_vs_linear']:>+14.2f}"
              f"{r['delta_aic_exp_vs_constant']:>+14.2f}{shape:>30}{r2:>+8.2f}{ratio:>8.2f}")

    # Verdict logic
    voy_r = results['voynich_B']
    mens_r = results.get('mensural')
    synth_r = results['synthetic_newton']

    print("\n" + "=" * 70)
    print("PRE-REGISTERED VERDICT")
    print("=" * 70)

    voy_passes_A = voy_r['test_A_strong']
    voy_passes_A_weak = voy_r['test_A_weak']
    voy_passes_B = voy_r['test_B_pass']
    voy_passes_C = voy_r['test_C_pass']
    mens_passes_A = mens_r['test_A_strong'] if mens_r and 'error' not in mens_r else False
    synth_passes_A = synth_r['test_A_strong'] if 'error' not in synth_r else False

    print(f"\n  Voynich Test A (cooling-curve exp wins):")
    print(f"    strong (ΔAIC≥10 vs both): {voy_passes_A}")
    print(f"    weak (ΔAIC≥4 vs both):    {voy_passes_A_weak}")
    print(f"  Voynich Test B (log scaling R²≥0.3): {voy_passes_B}")
    print(f"  Voynich Test C (asymmetry outside [0.8,1.2]): {voy_passes_C}")
    print(f"  Mensural Test A (NL-floor check — should FAIL for thermal-specific signature): "
          f"strong={mens_passes_A}")
    print(f"  Synthetic Test A (positive control — should PASS for methodology validity): "
          f"strong={synth_passes_A}")

    if voy_passes_A and voy_passes_B and voy_passes_C and not mens_passes_A and synth_passes_A:
        verdict = "THERMAL SIGNATURE CONFIRMED"
        rationale = "All three Voynich tests pass; mensural floor fails (not a generic structured-symbolic floor); synthetic positive control passes (methodology valid)."
    elif voy_passes_A and synth_passes_A and not mens_passes_A:
        verdict = "DAMPED CONTROL SIGNATURE (cooling-curve only)"
        rationale = f"Voynich cooling curve fits exponential (ΔAIC vs lin={voy_r['delta_aic_exp_vs_linear']:.1f}, vs const={voy_r['delta_aic_exp_vs_constant']:.1f}); mensural floor fails. But scaling test {('passes' if voy_passes_B else 'fails')} and asymmetry {('passes' if voy_passes_C else 'fails')} — generic damped relaxation, not specifically thermal."
    elif mens_passes_A and voy_passes_A:
        verdict = "FLOOR — exponential recovery is generic"
        rationale = "Both Voynich and mensural show exponential recovery curves; cooling-curve shape is a generic property of structured-symbolic systems, not thermal-specific."
    elif not voy_passes_A:
        verdict = "NO KINETIC STRUCTURE"
        rationale = f"Voynich cooling curve does not fit exponential significantly better than linear (ΔAIC={voy_r['delta_aic_exp_vs_linear']:.1f}) or constant (ΔAIC={voy_r['delta_aic_exp_vs_constant']:.1f}). PHYS findings should be reframed as statistical regression-to-mean."
    else:
        verdict = "MIXED — partial pattern"
        rationale = "Some tests pass, others fail; no clean verdict matches pre-registered criteria."

    print(f"\n  VERDICT: {verdict}")
    print(f"  Rationale: {rationale}")

    out = {
        'method': 'PHASE_712 thermodynamic kinetics test for kernel',
        'max_lag': MAX_LAG,
        'results_by_corpus': results,
        'verdict': verdict,
        'rationale': rationale,
        'voy_passes_A': voy_passes_A,
        'voy_passes_A_weak': voy_passes_A_weak,
        'voy_passes_B': voy_passes_B,
        'voy_passes_C': voy_passes_C,
        'mens_passes_A': mens_passes_A,
        'synth_passes_A': synth_passes_A,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
