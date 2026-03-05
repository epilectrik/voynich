#!/usr/bin/env python3
"""
Phase 512 Supplement: THERMAL DISAMBIGUATION

Disambiguates whether the thermal continuity signal (T5: e_frac rho=+0.230
between consecutive paragraphs) reflects:
  (A) PHYSICAL CONTINUITY - heat carries over sequentially, OR
  (B) SHARED ENVIRONMENT - all paragraphs in a folio have similar thermal profiles

Four tests:
  T1: Adjacent vs Non-Adjacent Within-Folio Correlation
  T2: Folio-Controlled Correlation (residualize by folio mean)
  T3: Lag Gradient (correlation at lag 1, 2, 3)
  T4: Random Shuffle Control (1000 shuffles within folio)

Output: phases/PARAGRAPH_STATE_DEPENDENT_ORDERING/results/thermal_disambiguation.json
"""

import sys
import os
import json
import numpy as np
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scripts.voynich import Transcript, Morphology
from scipy.stats import spearmanr

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


def compute_kernel_fracs(morphs):
    """Compute k_frac, e_frac from a list of morphology extractions."""
    n = len(morphs)
    if n == 0:
        return None
    k_count = sum(1 for m in morphs if m.middle and 'k' in m.middle)
    e_count = sum(1 for m in morphs if m.middle and 'e' in m.middle)
    return {
        'k_frac': k_count / n,
        'e_frac': e_count / n,
    }


def main():
    print("=" * 70)
    print("Phase 512 Supplement: THERMAL DISAMBIGUATION")
    print("=" * 70)
    print()
    print("Question: Does the T5 thermal continuity signal (rho=+0.230)")
    print("reflect PHYSICAL CONTINUITY or SHARED ENVIRONMENT?")
    print()

    # ============================================================
    # STEP 1: Load Phase 510 paragraph labels
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
        zone_lookup[key] = pl['cluster']

    # ============================================================
    # STEP 2: Load transcript, build paragraphs
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

    # Build paragraphs using par_initial markers (same as Phase 510/512)
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

    # ============================================================
    # STEP 3: Compute terminal and initial kernel features
    # ============================================================
    print("\nComputing terminal and initial kernel features...")

    for par in all_paragraphs:
        if par['zone'] is None:
            par['terminal_feats'] = None
            par['initial_feats'] = None
            continue

        lines = sorted(set(t.line for t in par['tokens']))
        if len(lines) < 2:
            par['terminal_feats'] = None
            par['initial_feats'] = None
            continue

        # Body lines = all except the first (header)
        body_lines = lines[1:]
        if len(body_lines) == 0:
            par['terminal_feats'] = None
            par['initial_feats'] = None
            continue

        # Terminal: last 2 body lines (or last 1 if only 1 body line)
        terminal_lines = set(body_lines[-2:]) if len(body_lines) >= 2 else set(body_lines[-1:])

        # Initial: first 2 body lines after header
        initial_lines = set(body_lines[:2]) if len(body_lines) >= 2 else set(body_lines[:1])

        # Extract morphology
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

        par['terminal_feats'] = compute_kernel_fracs(terminal_morphs)
        par['initial_feats'] = compute_kernel_fracs(initial_morphs)

    # ============================================================
    # STEP 4: Group by folio, keep only paragraphs with features
    # ============================================================
    folio_pars = defaultdict(list)
    for par in all_paragraphs:
        if (par['zone'] is not None and
                par['terminal_feats'] is not None and
                par['initial_feats'] is not None):
            folio_pars[par['folio']].append(par)

    # Sort by par_idx within each folio
    for f in folio_pars:
        folio_pars[f].sort(key=lambda p: p['par_idx'])

    # Keep only folios with 2+ paragraphs (needed for pairs)
    folio_pars = {f: pars for f, pars in folio_pars.items() if len(pars) >= 2}

    total_pars = sum(len(pars) for pars in folio_pars.values())
    print(f"Folios with 2+ paragraphs: {len(folio_pars)}")
    print(f"Total paragraphs in analysis: {total_pars}")

    # ============================================================
    # T1: ADJACENT vs NON-ADJACENT WITHIN-FOLIO CORRELATION
    # ============================================================
    print("\n" + "=" * 70)
    print("T1: ADJACENT vs NON-ADJACENT WITHIN-FOLIO CORRELATION")
    print("=" * 70)
    print()
    print("If physical continuity: adjacent >> non-adjacent")
    print("If shared environment: adjacent ~ non-adjacent")
    print()

    adjacent_terminal_e = []
    adjacent_initial_e = []
    adjacent_terminal_k = []
    adjacent_initial_k = []

    nonadj_terminal_e = []
    nonadj_initial_e = []
    nonadj_terminal_k = []
    nonadj_initial_k = []

    for folio, pars in folio_pars.items():
        n = len(pars)
        for i in range(n):
            for j in range(i + 1, n):
                te = pars[i]['terminal_feats']['e_frac']
                ie = pars[j]['initial_feats']['e_frac']
                tk = pars[i]['terminal_feats']['k_frac']
                ik = pars[j]['initial_feats']['k_frac']

                if j == i + 1:
                    # Adjacent pair (consecutive paragraphs)
                    adjacent_terminal_e.append(te)
                    adjacent_initial_e.append(ie)
                    adjacent_terminal_k.append(tk)
                    adjacent_initial_k.append(ik)
                else:
                    # Non-adjacent pair (skip >= 1 paragraph)
                    nonadj_terminal_e.append(te)
                    nonadj_initial_e.append(ie)
                    nonadj_terminal_k.append(tk)
                    nonadj_initial_k.append(ik)

    print(f"  Adjacent pairs: {len(adjacent_terminal_e)}")
    print(f"  Non-adjacent pairs: {len(nonadj_terminal_e)}")

    # Compute correlations
    rho_adj_e, p_adj_e = spearmanr(adjacent_terminal_e, adjacent_initial_e)
    rho_adj_k, p_adj_k = spearmanr(adjacent_terminal_k, adjacent_initial_k)

    if len(nonadj_terminal_e) >= 10:
        rho_nonadj_e, p_nonadj_e = spearmanr(nonadj_terminal_e, nonadj_initial_e)
        rho_nonadj_k, p_nonadj_k = spearmanr(nonadj_terminal_k, nonadj_initial_k)
    else:
        rho_nonadj_e, p_nonadj_e = float('nan'), float('nan')
        rho_nonadj_k, p_nonadj_k = float('nan'), float('nan')

    print(f"\n  e_frac terminal(N) -> initial(N+k):")
    print(f"    Adjacent (lag=1):     rho={rho_adj_e:+.4f}, p={p_adj_e:.4e}")
    print(f"    Non-adjacent (lag>1): rho={rho_nonadj_e:+.4f}, p={p_nonadj_e:.4e}")
    print(f"    Difference:           {rho_adj_e - rho_nonadj_e:+.4f}")

    print(f"\n  k_frac terminal(N) -> initial(N+k):")
    print(f"    Adjacent (lag=1):     rho={rho_adj_k:+.4f}, p={p_adj_k:.4e}")
    print(f"    Non-adjacent (lag>1): rho={rho_nonadj_k:+.4f}, p={p_nonadj_k:.4e}")
    print(f"    Difference:           {rho_adj_k - rho_nonadj_k:+.4f}")

    # Fisher z-transform test for difference between correlations
    def fisher_z_test(r1, n1, r2, n2):
        """Test whether two Spearman correlations differ significantly."""
        # Clip to avoid arctanh domain errors
        r1 = np.clip(r1, -0.9999, 0.9999)
        r2 = np.clip(r2, -0.9999, 0.9999)
        z1 = np.arctanh(r1)
        z2 = np.arctanh(r2)
        se = np.sqrt(1 / (n1 - 3) + 1 / (n2 - 3))
        z_diff = (z1 - z2) / se
        # Two-tailed p-value from standard normal
        from scipy.stats import norm
        p_val = 2 * norm.sf(abs(z_diff))
        return z_diff, p_val

    n_adj = len(adjacent_terminal_e)
    n_nonadj = len(nonadj_terminal_e)

    if not np.isnan(rho_nonadj_e):
        z_e, pz_e = fisher_z_test(rho_adj_e, n_adj, rho_nonadj_e, n_nonadj)
        z_k, pz_k = fisher_z_test(rho_adj_k, n_adj, rho_nonadj_k, n_nonadj)
        print(f"\n  Fisher z-test (adjacent vs non-adjacent):")
        print(f"    e_frac: z={z_e:+.3f}, p={pz_e:.4f}")
        print(f"    k_frac: z={z_k:+.3f}, p={pz_k:.4f}")
    else:
        z_e, pz_e = float('nan'), float('nan')
        z_k, pz_k = float('nan'), float('nan')

    # Verdict
    adj_stronger = (rho_adj_e > rho_nonadj_e + 0.05 and
                    not np.isnan(rho_nonadj_e))
    if adj_stronger and pz_e < 0.05:
        t1_verdict = "PHYSICAL_CONTINUITY"
        t1_interp = "Adjacent correlation significantly stronger than non-adjacent"
    elif abs(rho_adj_e - rho_nonadj_e) < 0.05 or (not np.isnan(pz_e) and pz_e >= 0.05):
        t1_verdict = "SHARED_ENVIRONMENT"
        t1_interp = "Adjacent and non-adjacent correlations are similar"
    else:
        t1_verdict = "AMBIGUOUS"
        t1_interp = "Direction suggests physical continuity but not statistically significant"

    print(f"\n  Verdict: {t1_verdict}")
    print(f"  Interpretation: {t1_interp}")

    t1_results = {
        'n_adjacent': n_adj,
        'n_nonadjacent': n_nonadj,
        'adjacent_e': {'rho': float(rho_adj_e), 'p': float(p_adj_e)},
        'nonadjacent_e': {'rho': float(rho_nonadj_e), 'p': float(p_nonadj_e)},
        'adjacent_k': {'rho': float(rho_adj_k), 'p': float(p_adj_k)},
        'nonadjacent_k': {'rho': float(rho_nonadj_k), 'p': float(p_nonadj_k)},
        'fisher_z_e': {'z': float(z_e), 'p': float(pz_e)},
        'fisher_z_k': {'z': float(z_k), 'p': float(pz_k)},
        'verdict': t1_verdict,
        'interpretation': t1_interp,
    }

    # ============================================================
    # T2: FOLIO-CONTROLLED CORRELATION
    # ============================================================
    print("\n" + "=" * 70)
    print("T2: FOLIO-CONTROLLED CORRELATION")
    print("=" * 70)
    print()
    print("Residualize by folio mean. If correlation vanishes,")
    print("the signal is shared environment (folio-level thermal state).")
    print()

    # Compute folio means for e_frac and k_frac (across all paragraphs)
    folio_mean_e = {}
    folio_mean_k = {}
    for folio, pars in folio_pars.items():
        # Use ALL paragraph features (both terminal and initial) for folio mean
        all_e = []
        all_k = []
        for p in pars:
            all_e.append(p['terminal_feats']['e_frac'])
            all_e.append(p['initial_feats']['e_frac'])
            all_k.append(p['terminal_feats']['k_frac'])
            all_k.append(p['initial_feats']['k_frac'])
        folio_mean_e[folio] = np.mean(all_e)
        folio_mean_k[folio] = np.mean(all_k)

    # Build adjacent pairs with folio-residualized values
    resid_terminal_e = []
    resid_initial_e = []
    resid_terminal_k = []
    resid_initial_k = []

    for folio, pars in folio_pars.items():
        for i in range(len(pars) - 1):
            te = pars[i]['terminal_feats']['e_frac'] - folio_mean_e[folio]
            ie = pars[i + 1]['initial_feats']['e_frac'] - folio_mean_e[folio]
            tk = pars[i]['terminal_feats']['k_frac'] - folio_mean_k[folio]
            ik = pars[i + 1]['initial_feats']['k_frac'] - folio_mean_k[folio]
            resid_terminal_e.append(te)
            resid_initial_e.append(ie)
            resid_terminal_k.append(tk)
            resid_initial_k.append(ik)

    n_resid = len(resid_terminal_e)
    rho_resid_e, p_resid_e = spearmanr(resid_terminal_e, resid_initial_e)
    rho_resid_k, p_resid_k = spearmanr(resid_terminal_k, resid_initial_k)

    # Also compute the raw (non-residualized) adjacent correlation for comparison
    raw_terminal_e = []
    raw_initial_e = []
    raw_terminal_k = []
    raw_initial_k = []
    for folio, pars in folio_pars.items():
        for i in range(len(pars) - 1):
            raw_terminal_e.append(pars[i]['terminal_feats']['e_frac'])
            raw_initial_e.append(pars[i + 1]['initial_feats']['e_frac'])
            raw_terminal_k.append(pars[i]['terminal_feats']['k_frac'])
            raw_initial_k.append(pars[i + 1]['initial_feats']['k_frac'])

    rho_raw_e, p_raw_e = spearmanr(raw_terminal_e, raw_initial_e)
    rho_raw_k, p_raw_k = spearmanr(raw_terminal_k, raw_initial_k)

    print(f"  Adjacent pairs: {n_resid}")
    print(f"\n  Raw (no folio control):")
    print(f"    e_frac: rho={rho_raw_e:+.4f}, p={p_raw_e:.4e}")
    print(f"    k_frac: rho={rho_raw_k:+.4f}, p={p_raw_k:.4e}")
    print(f"\n  Folio-residualized:")
    print(f"    e_frac: rho={rho_resid_e:+.4f}, p={p_resid_e:.4e}")
    print(f"    k_frac: rho={rho_resid_k:+.4f}, p={p_resid_k:.4e}")

    # Compute how much of the correlation is folio-level
    e_reduction = 1.0 - abs(rho_resid_e) / abs(rho_raw_e) if abs(rho_raw_e) > 0.001 else float('nan')
    k_reduction = 1.0 - abs(rho_resid_k) / abs(rho_raw_k) if abs(rho_raw_k) > 0.001 else float('nan')

    if not np.isnan(e_reduction):
        print(f"\n  Folio-level fraction of e_frac correlation: {e_reduction:.1%}")
    if not np.isnan(k_reduction):
        print(f"  Folio-level fraction of k_frac correlation: {k_reduction:.1%}")

    # Verdict
    if abs(rho_resid_e) < 0.05 and abs(rho_raw_e) > 0.10:
        t2_verdict = "SHARED_ENVIRONMENT"
        t2_interp = "Correlation vanishes after folio-mean removal"
    elif abs(rho_resid_e) > 0.10 and p_resid_e < 0.05:
        t2_verdict = "PHYSICAL_CONTINUITY"
        t2_interp = "Significant residual correlation survives folio control"
    elif abs(rho_resid_e) > 0.05 and abs(rho_resid_e) < abs(rho_raw_e) * 0.5:
        t2_verdict = "MIXED"
        t2_interp = "Correlation reduced but not eliminated by folio control"
    else:
        t2_verdict = "AMBIGUOUS"
        t2_interp = "Neither clear physical continuity nor pure shared environment"

    print(f"\n  Verdict: {t2_verdict}")
    print(f"  Interpretation: {t2_interp}")

    t2_results = {
        'n_pairs': n_resid,
        'raw_e': {'rho': float(rho_raw_e), 'p': float(p_raw_e)},
        'raw_k': {'rho': float(rho_raw_k), 'p': float(p_raw_k)},
        'residualized_e': {'rho': float(rho_resid_e), 'p': float(p_resid_e)},
        'residualized_k': {'rho': float(rho_resid_k), 'p': float(p_resid_k)},
        'e_folio_fraction': float(e_reduction) if not np.isnan(e_reduction) else None,
        'k_folio_fraction': float(k_reduction) if not np.isnan(k_reduction) else None,
        'verdict': t2_verdict,
        'interpretation': t2_interp,
    }

    # ============================================================
    # T3: LAG GRADIENT
    # ============================================================
    print("\n" + "=" * 70)
    print("T3: LAG GRADIENT")
    print("=" * 70)
    print()
    print("If physical continuity: correlation decays with lag (like ACF)")
    print("If shared environment: correlation flat across lags")
    print()

    # Build pairs at different lags within folios
    max_lag = 5
    lag_data_e = defaultdict(lambda: {'terminal': [], 'initial': []})
    lag_data_k = defaultdict(lambda: {'terminal': [], 'initial': []})

    for folio, pars in folio_pars.items():
        n = len(pars)
        for lag in range(1, min(max_lag + 1, n)):
            for i in range(n - lag):
                j = i + lag
                lag_data_e[lag]['terminal'].append(pars[i]['terminal_feats']['e_frac'])
                lag_data_e[lag]['initial'].append(pars[j]['initial_feats']['e_frac'])
                lag_data_k[lag]['terminal'].append(pars[i]['terminal_feats']['k_frac'])
                lag_data_k[lag]['initial'].append(pars[j]['initial_feats']['k_frac'])

    print(f"  {'Lag':>4s}  {'N':>5s}  {'rho(e)':>8s}  {'p(e)':>10s}  {'rho(k)':>8s}  {'p(k)':>10s}")
    print(f"  {'----':>4s}  {'-----':>5s}  {'--------':>8s}  {'----------':>10s}  {'--------':>8s}  {'----------':>10s}")

    lag_results = {}
    for lag in range(1, max_lag + 1):
        if lag not in lag_data_e or len(lag_data_e[lag]['terminal']) < 10:
            continue
        re, pe = spearmanr(lag_data_e[lag]['terminal'], lag_data_e[lag]['initial'])
        rk, pk = spearmanr(lag_data_k[lag]['terminal'], lag_data_k[lag]['initial'])
        n_lag = len(lag_data_e[lag]['terminal'])
        print(f"  {lag:4d}  {n_lag:5d}  {re:+8.4f}  {pe:10.4e}  {rk:+8.4f}  {pk:10.4e}")
        lag_results[str(lag)] = {
            'n': n_lag,
            'e_rho': float(re),
            'e_p': float(pe),
            'k_rho': float(rk),
            'k_p': float(pk),
        }

    # Check for decay pattern
    lag_rhos_e = [lag_results[str(lag)]['e_rho'] for lag in range(1, max_lag + 1)
                  if str(lag) in lag_results]
    lag_rhos_k = [lag_results[str(lag)]['k_rho'] for lag in range(1, max_lag + 1)
                  if str(lag) in lag_results]

    if len(lag_rhos_e) >= 3:
        # Check if lag 1 > lag 2 > lag 3 (monotonic decay)
        e_monotonic_decay = all(lag_rhos_e[i] > lag_rhos_e[i + 1]
                                for i in range(min(2, len(lag_rhos_e) - 1)))
        # Check if roughly flat (max - min < 0.05)
        e_flat = (max(lag_rhos_e[:3]) - min(lag_rhos_e[:3])) < 0.05
        # Check range of first 3 lags
        e_range = max(lag_rhos_e[:3]) - min(lag_rhos_e[:3])

        print(f"\n  e_frac lag-1 to lag-3 range: {e_range:.4f}")
        print(f"  Monotonic decay (first 3 lags): {e_monotonic_decay}")
        print(f"  Flat (range < 0.05): {e_flat}")
    else:
        e_monotonic_decay = False
        e_flat = True
        e_range = 0.0

    if len(lag_rhos_k) >= 3:
        k_range = max(lag_rhos_k[:3]) - min(lag_rhos_k[:3])
    else:
        k_range = 0.0

    # Verdict
    if len(lag_rhos_e) >= 3 and e_monotonic_decay and e_range > 0.05:
        t3_verdict = "PHYSICAL_CONTINUITY"
        t3_interp = "Correlation decays monotonically with lag"
    elif len(lag_rhos_e) >= 3 and e_flat:
        t3_verdict = "SHARED_ENVIRONMENT"
        t3_interp = "Correlation flat across lags (range < 0.05)"
    elif len(lag_rhos_e) >= 3 and not e_monotonic_decay and e_range < 0.10:
        t3_verdict = "SHARED_ENVIRONMENT"
        t3_interp = "No clear decay pattern; correlation approximately constant"
    else:
        t3_verdict = "AMBIGUOUS"
        t3_interp = "Neither clear decay nor flat pattern"

    print(f"\n  Verdict: {t3_verdict}")
    print(f"  Interpretation: {t3_interp}")

    t3_results = {
        'lags': lag_results,
        'e_lag_rhos_first3': lag_rhos_e[:3] if len(lag_rhos_e) >= 3 else lag_rhos_e,
        'k_lag_rhos_first3': lag_rhos_k[:3] if len(lag_rhos_k) >= 3 else lag_rhos_k,
        'e_range_first3': float(e_range),
        'k_range_first3': float(k_range),
        'e_monotonic_decay': bool(e_monotonic_decay) if len(lag_rhos_e) >= 3 else None,
        'verdict': t3_verdict,
        'interpretation': t3_interp,
    }

    # ============================================================
    # T4: RANDOM SHUFFLE CONTROL
    # ============================================================
    print("\n" + "=" * 70)
    print("T4: RANDOM SHUFFLE CONTROL (1000 shuffles)")
    print("=" * 70)
    print()
    print("Shuffle paragraph order within each folio, recompute adjacent")
    print("terminal->initial correlation. If observed is not significantly")
    print("stronger than shuffled, signal is folio-level.")
    print()

    N_SHUFFLES = 1000
    rng = np.random.RandomState(RANDOM_SEED)

    # Observed adjacent correlation
    obs_rho_e = rho_raw_e  # from T2
    obs_rho_k = rho_raw_k

    # Run shuffles
    shuffle_rhos_e = []
    shuffle_rhos_k = []

    for s in range(N_SHUFFLES):
        shuf_term_e = []
        shuf_init_e = []
        shuf_term_k = []
        shuf_init_k = []

        for folio, pars in folio_pars.items():
            # Shuffle paragraph order within folio
            indices = list(range(len(pars)))
            rng.shuffle(indices)
            shuffled_pars = [pars[idx] for idx in indices]

            # Build adjacent pairs from shuffled order
            for i in range(len(shuffled_pars) - 1):
                shuf_term_e.append(shuffled_pars[i]['terminal_feats']['e_frac'])
                shuf_init_e.append(shuffled_pars[i + 1]['initial_feats']['e_frac'])
                shuf_term_k.append(shuffled_pars[i]['terminal_feats']['k_frac'])
                shuf_init_k.append(shuffled_pars[i + 1]['initial_feats']['k_frac'])

        if len(shuf_term_e) >= 10:
            r_e, _ = spearmanr(shuf_term_e, shuf_init_e)
            r_k, _ = spearmanr(shuf_term_k, shuf_init_k)
            shuffle_rhos_e.append(r_e)
            shuffle_rhos_k.append(r_k)

    shuffle_rhos_e = np.array(shuffle_rhos_e)
    shuffle_rhos_k = np.array(shuffle_rhos_k)

    # Compute p-value: fraction of shuffles with rho >= observed
    p_shuf_e = np.mean(shuffle_rhos_e >= obs_rho_e)
    p_shuf_k = np.mean(shuffle_rhos_k >= obs_rho_k)

    print(f"  Observed adjacent rho(e): {obs_rho_e:+.4f}")
    print(f"  Shuffle mean rho(e):      {np.mean(shuffle_rhos_e):+.4f}")
    print(f"  Shuffle std rho(e):       {np.std(shuffle_rhos_e):.4f}")
    print(f"  Shuffle 95th pctile:      {np.percentile(shuffle_rhos_e, 95):+.4f}")
    print(f"  Permutation p-value (e):  {p_shuf_e:.4f}")
    print()
    print(f"  Observed adjacent rho(k): {obs_rho_k:+.4f}")
    print(f"  Shuffle mean rho(k):      {np.mean(shuffle_rhos_k):+.4f}")
    print(f"  Shuffle std rho(k):       {np.std(shuffle_rhos_k):.4f}")
    print(f"  Shuffle 95th pctile:      {np.percentile(shuffle_rhos_k, 95):+.4f}")
    print(f"  Permutation p-value (k):  {p_shuf_k:.4f}")

    # z-score of observed vs shuffle distribution
    z_shuf_e = (obs_rho_e - np.mean(shuffle_rhos_e)) / np.std(shuffle_rhos_e) if np.std(shuffle_rhos_e) > 0 else 0
    z_shuf_k = (obs_rho_k - np.mean(shuffle_rhos_k)) / np.std(shuffle_rhos_k) if np.std(shuffle_rhos_k) > 0 else 0
    print(f"\n  z-score vs shuffle (e): {z_shuf_e:+.3f}")
    print(f"  z-score vs shuffle (k): {z_shuf_k:+.3f}")

    # Verdict
    if p_shuf_e < 0.05 and z_shuf_e > 1.96:
        t4_verdict = "PHYSICAL_CONTINUITY"
        t4_interp = ("Observed adjacent correlation significantly exceeds "
                     "shuffled (ordering matters)")
    elif p_shuf_e >= 0.05:
        t4_verdict = "SHARED_ENVIRONMENT"
        t4_interp = ("Observed adjacent correlation NOT significantly better than "
                     "shuffled (folio-level signal only)")
    else:
        t4_verdict = "AMBIGUOUS"
        t4_interp = "Marginal result"

    print(f"\n  Verdict: {t4_verdict}")
    print(f"  Interpretation: {t4_interp}")

    t4_results = {
        'n_shuffles': N_SHUFFLES,
        'observed_e_rho': float(obs_rho_e),
        'shuffle_mean_e': float(np.mean(shuffle_rhos_e)),
        'shuffle_std_e': float(np.std(shuffle_rhos_e)),
        'shuffle_p95_e': float(np.percentile(shuffle_rhos_e, 95)),
        'permutation_p_e': float(p_shuf_e),
        'z_score_e': float(z_shuf_e),
        'observed_k_rho': float(obs_rho_k),
        'shuffle_mean_k': float(np.mean(shuffle_rhos_k)),
        'shuffle_std_k': float(np.std(shuffle_rhos_k)),
        'shuffle_p95_k': float(np.percentile(shuffle_rhos_k, 95)),
        'permutation_p_k': float(p_shuf_k),
        'z_score_k': float(z_shuf_k),
        'verdict': t4_verdict,
        'interpretation': t4_interp,
    }

    # ============================================================
    # SYNTHESIS
    # ============================================================
    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)

    verdicts = {
        'T1_adjacent_vs_nonadjacent': t1_verdict,
        'T2_folio_controlled': t2_verdict,
        'T3_lag_gradient': t3_verdict,
        'T4_shuffle_control': t4_verdict,
    }

    physical_count = sum(1 for v in verdicts.values() if v == 'PHYSICAL_CONTINUITY')
    shared_count = sum(1 for v in verdicts.values() if v == 'SHARED_ENVIRONMENT')
    mixed_count = sum(1 for v in verdicts.values() if v == 'MIXED')
    ambig_count = sum(1 for v in verdicts.values() if v == 'AMBIGUOUS')

    print(f"\n  PHYSICAL_CONTINUITY: {physical_count}/4")
    print(f"  SHARED_ENVIRONMENT:  {shared_count}/4")
    print(f"  MIXED:               {mixed_count}/4")
    print(f"  AMBIGUOUS:           {ambig_count}/4")

    for test, verdict in verdicts.items():
        print(f"    {test:40s}: {verdict}")

    # Overall determination
    if shared_count >= 3:
        overall = "SHARED_ENVIRONMENT"
        interpretation = (
            f"The T5 thermal continuity signal is FOLIO-LEVEL (shared environment). "
            f"{shared_count}/4 tests confirm that consecutive paragraphs have "
            f"similar thermal profiles because they belong to the same folio, "
            f"not because heat physically carries over from one paragraph to the next. "
            f"The correlation does not decay with lag, does not exceed shuffled controls, "
            f"and/or vanishes after folio-mean removal."
        )
    elif physical_count >= 3:
        overall = "PHYSICAL_CONTINUITY"
        interpretation = (
            f"The T5 thermal continuity signal reflects genuine PHYSICAL CONTINUITY. "
            f"{physical_count}/4 tests confirm that adjacent paragraphs specifically "
            f"(not just co-located paragraphs) share thermal state. The correlation "
            f"decays with lag, exceeds shuffled controls, and survives folio-mean removal."
        )
    elif shared_count >= 2 and physical_count <= 1:
        overall = "PREDOMINANTLY_SHARED_ENVIRONMENT"
        interpretation = (
            f"The T5 signal is predominantly folio-level. "
            f"{shared_count}/4 shared environment vs {physical_count}/4 physical continuity. "
            f"Most of the signal comes from paragraphs sharing a folio-level thermal "
            f"theme, with at most a weak sequential component."
        )
    elif physical_count >= 2 and shared_count <= 1:
        overall = "PREDOMINANTLY_PHYSICAL"
        interpretation = (
            f"The T5 signal has a genuine sequential component. "
            f"{physical_count}/4 physical continuity vs {shared_count}/4 shared environment. "
            f"Heat state partially carries over between consecutive paragraphs."
        )
    else:
        overall = "MIXED"
        interpretation = (
            f"The T5 signal is mixed: {physical_count}/4 physical, "
            f"{shared_count}/4 shared, {mixed_count}/4 mixed, {ambig_count}/4 ambiguous. "
            f"Both folio-level and sequential components contribute."
        )

    print(f"\n  OVERALL: {overall}")
    print(f"  {interpretation}")

    # ============================================================
    # SAVE RESULTS
    # ============================================================
    results = {
        'metadata': {
            'phase': 'Phase 512 Supplement: THERMAL DISAMBIGUATION',
            'question': 'Does T5 thermal continuity (rho=+0.230) reflect '
                       'physical continuity or shared environment?',
            'n_folios': len(folio_pars),
            'n_paragraphs': total_pars,
            'random_seed': RANDOM_SEED,
        },
        'T1_adjacent_vs_nonadjacent': t1_results,
        'T2_folio_controlled': t2_results,
        'T3_lag_gradient': t3_results,
        'T4_shuffle_control': t4_results,
        'synthesis': {
            'verdicts': verdicts,
            'physical_count': physical_count,
            'shared_count': shared_count,
            'mixed_count': mixed_count,
            'ambiguous_count': ambig_count,
            'overall': overall,
            'interpretation': interpretation,
        },
    }

    out_path = os.path.join(os.path.dirname(__file__), '..', 'results',
                            'thermal_disambiguation.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
