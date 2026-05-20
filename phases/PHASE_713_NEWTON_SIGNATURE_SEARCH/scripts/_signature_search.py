"""PHASE_713: Hypothesis-free Newton's cooling signature search.

Don't assume which token-property marks operational excitation. Instead, search
the candidate signature space for ANY signature whose post-event dynamics fit
Newton's exponential cooling, with null-distribution control and cross-validation.

Per user's correction: only some tokens participate as operational events; the
kinetics-bearing subset must be identified, not assumed.
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

OUT_PATH = ROOT / 'phases' / 'PHASE_713_NEWTON_SIGNATURE_SEARCH' / 'results' / 'newton_signature_search.json'

random.seed(42)
np.random.seed(42)

MAX_LAG = 8
N_NULL = 500
HEAD_ATOMS = set('aeokt')
TERM_ATOMS = set('ynmhlrkt')


# ---- Feature extraction ----

def extract_token_features(token, morph_obj):
    """Return dict of all relevant signature features for a token."""
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
    return {
        'prefix': prefix if prefix else 'NONE',
        'has_prefix': prefix != '',
        'middle': middle,
        'suffix': suffix,
        'e_depth': e_depth,
        'head_atom': head_atom,
        'term_atom': term_atom,
        'has_suffix': has_suffix,
        'middle_len': len(middle),
        # e_density = fraction of e in middle (continuous)
        'e_density': e_count / max(len(middle), 1),
        # MIDDLE bigram presence
        'has_kh_in_mid': 'kh' in middle,
        'has_ke_in_mid': 'ke' in middle,
        'has_ck_in_mid': 'ck' in middle,
        'has_ch_in_mid': 'ch' in middle,
        'has_cth_in_mid': 'cth' in middle,
    }


def build_tokens_per_line(currier='B'):
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
    empty_feats = {
        'prefix': 'NONE', 'has_prefix': False, 'middle': '', 'suffix': '',
        'e_depth': 0, 'head_atom': 'NONE', 'term_atom': 'NONE',
        'has_suffix': False, 'middle_len': 0, 'e_density': 0,
        'has_kh_in_mid': False, 'has_ke_in_mid': False, 'has_ck_in_mid': False,
        'has_ch_in_mid': False, 'has_cth_in_mid': False,
    }
    line_features = []
    for key in sorted(lines.keys()):
        feats = []
        for w in lines[key]:
            f = extract_token_features(w, morph)
            if f is None:
                f = empty_feats.copy()
            feats.append({'word': w, **f})
        if len(feats) >= 5:
            line_features.append(feats)
    return line_features


# ---- Signature predicates ----

def make_signature_predicates():
    """Return list of (signature_name, predicate_function) tuples."""
    preds = []

    # PREFIX classes
    for pfx in ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'ct', 'da', 'NONE']:
        preds.append((f'PREFIX={pfx}', lambda f, p=pfx: f.get('prefix', 'NONE') == p))

    # HEAD atoms (of MIDDLE)
    for ha in ['a', 'e', 'o', 'k', 't', 'PSEUDO_HEAD', 'NONE']:
        preds.append((f'HEAD={ha}', lambda f, h=ha: f.get('head_atom', 'NONE') == h))

    # TERM atoms (last of MIDDLE)
    for ta in ['y', 'n', 'm', 'h', 'l', 'r', 'k', 't', 'NONE']:
        preds.append((f'TERM={ta}', lambda f, t=ta: f.get('term_atom', 'NONE') == t))

    # e-depth values
    for ed in [0, 1, 2, 3]:
        preds.append((f'e_depth={ed}', lambda f, e=ed: f.get('e_depth', 0) == e))

    # MIDDLE bigram presence
    for bg in ['kh', 'ke', 'ck', 'ch', 'cth']:
        preds.append((f'has_{bg}_in_MID', lambda f, b=bg: f.get(f'has_{b}_in_mid', False)))

    # PREFIX × HEAD selective combinations
    for pfx in ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'NONE']:
        for ha in ['k', 't', 'e', 'a', 'o']:
            preds.append((
                f'PREFIX={pfx}+HEAD={ha}',
                lambda f, p=pfx, h=ha: (f.get('prefix', 'NONE') == p and f.get('head_atom', 'NONE') == h)
            ))

    # PREFIX × TERM selective combinations
    for pfx in ['qo', 'ch', 'sh', 'ok']:
        for ta in ['y', 'r', 'h']:
            preds.append((
                f'PREFIX={pfx}+TERM={ta}',
                lambda f, p=pfx, t=ta: (f.get('prefix', 'NONE') == p and f.get('term_atom', 'NONE') == t)
            ))

    return preds


# ---- Cooling curve computation ----

def cooling_curve_for_signature(line_features, predicate, max_lag=MAX_LAG, target_metric='e_density'):
    """For each event token (matching predicate), compute target metric at lag 1..max_lag.
    Returns (curve, n_events, baseline).
    """
    sums = np.zeros(max_lag)
    counts = np.zeros(max_lag)
    n_events = 0
    all_targets = []
    for line in line_features:
        for f in line:
            all_targets.append(f.get(target_metric, 0))
    baseline = float(np.mean(all_targets)) if all_targets else 0

    for line in line_features:
        n = len(line)
        for i, f in enumerate(line):
            if not predicate(f):
                continue
            n_events += 1
            for lag in range(1, max_lag + 1):
                if i + lag >= n:
                    break
                target = line[i + lag].get(target_metric, 0)
                sums[lag - 1] += target
                counts[lag - 1] += 1
    curve = sums / np.maximum(counts, 1)
    return curve, n_events, baseline


# ---- Newton's fit ----

def fit_newton(curve, baseline):
    """Fit e(t) = e_inf + (e_0 - e_inf) * exp(-t/tau).
    Returns dict with tau, e_0, e_inf, sse.
    """
    from scipy.optimize import curve_fit
    t = np.arange(1, len(curve) + 1, dtype=float)
    def model(t, e0, einf, tau):
        return einf + (e0 - einf) * np.exp(-t / tau)
    try:
        # Bound tau to 0.1-50, e0 and einf to [0, 1]
        popt, _ = curve_fit(model, t, curve, p0=[curve[0], baseline, 2.0],
                            bounds=([0, 0, 0.1], [1, 1, 50]), maxfev=5000)
        e0, einf, tau = popt
        pred = model(t, *popt)
        sse = float(np.sum((curve - pred) ** 2))
        return {'tau': float(tau), 'e_0': float(e0), 'e_inf': float(einf),
                'sse_newton': sse, 'fit_curve': pred.tolist()}
    except Exception as e:
        return {'error': str(e), 'sse_newton': float('inf')}


def fit_constant(curve):
    c = float(np.mean(curve))
    sse = float(np.sum((curve - c) ** 2))
    return {'constant': c, 'sse_const': sse}


def delta_aic(sse_newton, sse_const, n_obs, n_p_newton=3, n_p_const=1):
    """ΔAIC = AIC(const) - AIC(newton). Positive = newton wins."""
    if sse_newton <= 0 or sse_const <= 0:
        return 0.0
    aic_n = 2 * n_p_newton + n_obs * math.log(sse_newton / n_obs)
    aic_c = 2 * n_p_const + n_obs * math.log(sse_const / n_obs)
    return float(aic_c - aic_n)


def score_signature(line_features, predicate, name, target_metric='e_density'):
    """Score one signature: compute curve, fit Newton's, return diagnostics."""
    curve, n_events, baseline = cooling_curve_for_signature(line_features, predicate, target_metric=target_metric)
    if n_events < 50:
        return None  # too few events
    n_fit = fit_newton(curve, baseline)
    c_fit = fit_constant(curve)
    dAIC = delta_aic(n_fit.get('sse_newton', float('inf')), c_fit['sse_const'], len(curve))
    return {
        'name': name,
        'n_events': n_events,
        'baseline': baseline,
        'curve': curve.tolist(),
        'newton_fit': n_fit,
        'constant_fit': c_fit,
        'delta_aic': dAIC,
    }


# ---- Null distribution ----

def null_distribution_for_size(line_features, n_size, n_null=N_NULL, target_metric='e_density'):
    """Generate K random subsets of n_size random event positions; compute their ΔAIC.
    Returns array of ΔAIC values.
    """
    # Flatten positions into (line_idx, token_idx) tuples
    all_positions = [(li, ti) for li, line in enumerate(line_features) for ti in range(len(line))]
    if len(all_positions) < n_size:
        return np.array([])

    # Compute baseline once
    baseline = float(np.mean([f.get(target_metric, 0) for line in line_features for f in line]))

    daics = []
    rng = np.random.default_rng(42)
    for trial in range(n_null):
        sampled_indices = rng.choice(len(all_positions), size=n_size, replace=False)
        sampled_positions = [all_positions[i] for i in sampled_indices]
        # Compute cooling curve for these random "event tokens"
        sums = np.zeros(MAX_LAG)
        counts = np.zeros(MAX_LAG)
        for (li, ti) in sampled_positions:
            line = line_features[li]
            n_line = len(line)
            for lag in range(1, MAX_LAG + 1):
                if ti + lag >= n_line:
                    break
                target = line[ti + lag].get(target_metric, 0)
                sums[lag - 1] += target
                counts[lag - 1] += 1
        curve = sums / np.maximum(counts, 1)
        n_fit = fit_newton(curve, baseline)
        c_fit = fit_constant(curve)
        dAIC = delta_aic(n_fit.get('sse_newton', float('inf')), c_fit['sse_const'], len(curve))
        daics.append(dAIC)
    return np.array(daics)


# ---- Main ----

def main():
    print("=" * 80)
    print("PHASE_713 HYPOTHESIS-FREE NEWTON'S COOLING SIGNATURE SEARCH")
    print("=" * 80)

    print("\n[1/4] Building line features (Currier B P-placement)...")
    line_features = build_tokens_per_line('B')
    print(f"  N lines: {len(line_features)}, N tokens: {sum(len(l) for l in line_features)}")

    # Compute corpus baseline
    all_e_density = [f.get('e_density', 0) for line in line_features for f in line]
    corpus_baseline = float(np.mean(all_e_density))
    print(f"  Corpus baseline e_density: {corpus_baseline:.4f}")

    # ---- Score all signatures ----
    print("\n[2/4] Scoring all candidate signatures...")
    predicates = make_signature_predicates()
    print(f"  N candidate signatures: {len(predicates)}")

    sig_results = []
    for name, pred in predicates:
        result = score_signature(line_features, pred, name)
        if result:
            sig_results.append(result)
    print(f"  N signatures with ≥50 events: {len(sig_results)}")

    # Sort by ΔAIC
    sig_results.sort(key=lambda r: -r['delta_aic'])

    print(f"\n  Top 15 signatures by ΔAIC (Newton's wins over constant):")
    print(f"  {'Rank':<5}{'Signature':<35}{'N_events':>10}{'ΔAIC':>10}{'tau':>8}{'e_0':>8}{'e_inf':>8}")
    print("  " + "-" * 88)
    for rank, r in enumerate(sig_results[:15]):
        nf = r['newton_fit']
        tau = nf.get('tau', float('nan'))
        e0 = nf.get('e_0', float('nan'))
        einf = nf.get('e_inf', float('nan'))
        print(f"  {rank+1:<5}{r['name']:<35}{r['n_events']:>10}{r['delta_aic']:>+10.2f}"
              f"{tau:>8.2f}{e0:>8.3f}{einf:>8.3f}")

    # ---- Null distribution for top candidates ----
    print("\n[3/4] Computing null distributions for top candidates...")
    top_K = min(5, len(sig_results))
    null_results = []
    for rank, r in enumerate(sig_results[:top_K]):
        n_size = r['n_events']
        print(f"  Top-{rank+1}: {r['name']} (n_events={n_size})")
        nulls = null_distribution_for_size(line_features, n_size, n_null=N_NULL)
        if len(nulls) == 0:
            continue
        p99 = float(np.percentile(nulls, 99))
        p95 = float(np.percentile(nulls, 95))
        p_emp = float(np.mean(nulls >= r['delta_aic']))
        passes_null = r['delta_aic'] > p99
        print(f"    null mean={nulls.mean():.2f}, p95={p95:.2f}, p99={p99:.2f}, "
              f"observed={r['delta_aic']:.2f}, p_emp={p_emp:.3f}, passes_null={passes_null}")
        null_results.append({
            'rank': rank + 1,
            'signature': r['name'],
            'n_events': n_size,
            'observed_delta_aic': r['delta_aic'],
            'null_mean': float(nulls.mean()),
            'null_p95': p95,
            'null_p99': p99,
            'p_empirical': p_emp,
            'passes_null': passes_null,
            'newton_fit': r['newton_fit'],
            'curve': r['curve'],
        })

    # ---- Cross-validation ----
    print("\n[4/4] Cross-validating top candidates (split lines random 50/50)...")
    rng = np.random.default_rng(42)
    n_lines = len(line_features)
    line_perm = rng.permutation(n_lines)
    half_a = [line_features[i] for i in line_perm[:n_lines // 2]]
    half_b = [line_features[i] for i in line_perm[n_lines // 2:]]

    cv_results = []
    for rank, r in enumerate(sig_results[:top_K]):
        # Find the predicate object by name
        pred = next((p for nm, p in predicates if nm == r['name']), None)
        if pred is None:
            continue
        result_a = score_signature(half_a, pred, r['name'])
        result_b = score_signature(half_b, pred, r['name'])
        cv = {
            'rank': rank + 1,
            'signature': r['name'],
            'half_A': result_a,
            'half_B': result_b,
        }
        cv_results.append(cv)
        if result_a and result_b:
            print(f"  {r['name']}: A_dAIC={result_a['delta_aic']:+.2f}  B_dAIC={result_b['delta_aic']:+.2f}  "
                  f"A_tau={result_a['newton_fit'].get('tau', 0):.2f}  B_tau={result_b['newton_fit'].get('tau', 0):.2f}")
        else:
            print(f"  {r['name']}: CV split underpowered")

    # ---- Final verdict ----
    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)

    surviving = [n for n in null_results if n['passes_null']]
    cv_passing = []
    for s in surviving:
        cv = next((c for c in cv_results if c['signature'] == s['signature']), None)
        if cv and cv['half_A'] and cv['half_B']:
            a_dAIC = cv['half_A']['delta_aic']
            b_dAIC = cv['half_B']['delta_aic']
            if a_dAIC > 3 and b_dAIC > 3:  # both halves show some Newton's fit
                cv_passing.append(s)

    print(f"\n  Signatures passing null (>99th percentile): {len(surviving)}")
    for s in surviving:
        print(f"    {s['signature']}: dAIC={s['observed_delta_aic']:+.2f} > p99={s['null_p99']:.2f}, "
              f"tau={s['newton_fit'].get('tau', 0):.2f}, "
              f"e_0={s['newton_fit'].get('e_0', 0):.3f}, "
              f"e_inf={s['newton_fit'].get('e_inf', 0):.3f}")

    print(f"\n  Signatures passing null AND cross-validation: {len(cv_passing)}")
    for s in cv_passing:
        print(f"    {s['signature']}")

    if cv_passing:
        # Check if e_0 is meaningfully different from e_inf (real perturbation)
        meaningful = []
        for s in cv_passing:
            e0 = s['newton_fit'].get('e_0', 0)
            einf = s['newton_fit'].get('e_inf', 0)
            tau = s['newton_fit'].get('tau', 0)
            if abs(e0 - einf) > 0.02 and 0.5 <= tau <= 10:
                meaningful.append(s)
        if meaningful:
            verdict = "OPERATIONAL EXCITATION SIGNATURE DISCOVERED"
            rationale = (f"{len(meaningful)} signature(s) pass null AND cross-validation AND show "
                         f"physical-interpretable Newton's parameters (|e_0 - e_inf| > 0.02, tau in [0.5, 10]).")
        else:
            verdict = "WEAK SIGNATURE — Newton's fit but not physically meaningful"
            rationale = ("Signatures pass null and CV but Newton's parameters are degenerate "
                         "(no real perturbation or implausible tau).")
    else:
        verdict = "NO DISCOVERED KINETIC SIGNATURE"
        rationale = "No token signature shows Newton's cooling above null AND cross-validates."

    print(f"\n  VERDICT: {verdict}")
    print(f"  Rationale: {rationale}")

    out = {
        'method': 'PHASE_713 hypothesis-free Newton signature search',
        'n_lines': len(line_features),
        'n_tokens': sum(len(l) for l in line_features),
        'corpus_baseline_e_density': corpus_baseline,
        'n_candidate_signatures': len(predicates),
        'n_scored_signatures': len(sig_results),
        'top_signatures_by_dAIC': sig_results[:15],
        'null_results': null_results,
        'cv_results': [{'rank': c['rank'], 'signature': c['signature'],
                       'half_A_dAIC': c['half_A']['delta_aic'] if c['half_A'] else None,
                       'half_B_dAIC': c['half_B']['delta_aic'] if c['half_B'] else None,
                       'half_A_tau': c['half_A']['newton_fit'].get('tau') if c['half_A'] else None,
                       'half_B_tau': c['half_B']['newton_fit'].get('tau') if c['half_B'] else None,
                       } for c in cv_results],
        'surviving_signatures': surviving,
        'cv_passing_signatures': [s['signature'] for s in cv_passing],
        'verdict': verdict,
        'rationale': rationale,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
