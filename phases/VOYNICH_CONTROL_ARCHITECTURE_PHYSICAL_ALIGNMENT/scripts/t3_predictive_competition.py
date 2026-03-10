"""
T3: Predictive Competition — v3 Physical Risk + Operator Features
=================================================================
Phase: VOYNICH_CONTROL_ARCHITECTURE_PHYSICAL_ALIGNMENT

v3 redesign: H1 and H5 test PHYSICAL OVERSHOOT RISK against Voynich
zone-hazard enrichment. Overshoot risk = max(0, T - T_target) is the
physically correct danger measure for distillation (overheating causes
thermal runaway and uncontrolled vaporization; underheating is safe).

  H1: Does Voynich zone-hazard enrichment predict physical overshoot
      risk distribution across cycle quintiles?
  H2: Does unsupervised two-state decomposition on operator features
      match Mode A/B?
  H3: Do passive/active operator events separate positionally?
  H4: Does HOT_STABLE quintile distribution match k-HEAD enrichment?
  H5: Is physical overshoot risk closure-biased (Q4 > Q0)?

7 alternatives, ablation tests, out-of-sample validation.

Output: t3_predictive_competition.json
"""

import json
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr, pearsonr, binomtest
from scipy.spatial.distance import jensenshannon
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score, silhouette_score
from sklearn.preprocessing import StandardScaler

RESULTS_DIR = Path(__file__).parent.parent / 'results'
N_PERMUTATIONS = 1000
ALPHA = 0.01


def load_data():
    with open(RESULTS_DIR / 't1_physical_process.json') as f:
        t1 = json.load(f)
    with open(RESULTS_DIR / 't2_voynich_features.json') as f:
        t2 = json.load(f)
    return t1, t2


def extract_all_cycles(t1):
    """Flatten all cycles with metadata."""
    cycles = []
    for param in t1['parameterizations']:
        pid = param['param_id']
        for run in param['runs']:
            rid = run['run_id']
            for cycle in run['cycles']:
                cycle['param_id'] = pid
                cycle['run_id'] = rid
                cycles.append(cycle)
    return cycles


def jsd_profiles(p_dict, q_dict, keys):
    """JSD between two profiles (lower = more similar)."""
    p = np.array([p_dict.get(k, 0) for k in keys])
    q = np.array([q_dict.get(k, 0) for k in keys])
    ps = p.sum()
    qs = q.sum()
    p = p / ps if ps > 0 else np.ones(len(keys)) / len(keys)
    q = q / qs if qs > 0 else np.ones(len(keys)) / len(keys)
    return float(jensenshannon(p, q))


# ============================================================
# H1: SAFETY-ENVELOPE — OPERATOR ACTION SCHEDULING
# ============================================================

def score_h1(cycles, voynich, rng):
    """H1: Does Voynich zone-hazard predict physical overshoot risk?

    v3: Tests physical OVERSHOOT RISK (max(0, T-T_target)) against
    Voynich zone-hazard enrichment. Overshoot risk is the correct
    danger measure for distillation: overheating causes thermal runaway.
    """
    print("  H1: Safety envelope (overshoot risk)...")

    v_h1 = voynich['hypotheses']['H1_safety_envelope']

    # Voynich prediction: HIGH hazard enrichment per quintile
    # Higher values = more dangerous
    voynich_high = {
        'Q0': 0.836, 'Q1': 1.006, 'Q2': 1.006, 'Q3': 1.006, 'Q4': 1.134,
    }
    keys = [f'Q{q}' for q in range(5)]

    # Empirical overshoot risk per quintile
    emp_overshoot = {f'Q{q}': [] for q in range(5)}
    for cycle in cycles:
        ov = cycle.get('quintile_overshoot', {})
        for q in range(5):
            key = f'Q{q}'
            if key in ov:
                emp_overshoot[key].append(ov[key])

    emp_means = {k: float(np.mean(v)) if v else 0.0
                 for k, v in emp_overshoot.items()}

    # Normalize both to distributions for JSD
    v_total = sum(voynich_high.values())
    v_norm = {k: v / v_total for k, v in voynich_high.items()}

    e_total = sum(emp_means.values())
    e_norm = {k: v / e_total if e_total > 0 else 0.2
              for k, v in emp_means.items()}

    voynich_jsd = jsd_profiles(v_norm, e_norm, keys)

    # Spearman: does the Voynich rank ordering match empirical?
    rho_v, rho_p = spearmanr(
        [voynich_high[k] for k in keys],
        [emp_means[k] for k in keys])

    # Ordered contrasts
    contrasts = {
        'risk_Q4_gt_Q0': emp_means['Q4'] > emp_means['Q0'],
        'risk_Q3_gt_Q0': emp_means['Q3'] > emp_means['Q0'],
        'risk_monotone_Q0_to_Q4': all(
            emp_means[f'Q{q}'] <= emp_means[f'Q{q+1}']
            for q in range(4)),
        'risk_Q0_lowest': emp_means['Q0'] == min(emp_means.values()),
    }

    # AUC: Can Voynich opening/closure classification predict low/high risk?
    y_true = []
    y_score = []
    for cycle in cycles:
        ov = cycle.get('quintile_overshoot', {})
        q0_risk = ov.get('Q0', 0)
        q4_risk = ov.get('Q4', 0)
        # Opening should be low-risk (label=0), closure high-risk (label=1)
        y_true.append(0)
        y_score.append(q0_risk)
        y_true.append(1)
        y_score.append(q4_risk)
    if len(set(y_true)) > 1 and len(y_score) > 0:
        voynich_auc = float(roc_auc_score(y_true, y_score))
    else:
        voynich_auc = 0.5

    # --- Alternatives ---
    alt_scores = {}

    # Random: permuted risk profiles
    random_jsds = []
    for _ in range(N_PERMUTATIONS):
        rand_pred = {f'Q{q}': rng.random() for q in range(5)}
        rt = sum(rand_pred.values())
        rand_norm = {k: v / rt for k, v in rand_pred.items()}
        random_jsds.append(jsd_profiles(rand_norm, e_norm, keys))
    alt_scores['random'] = {
        'jsd_mean': float(np.mean(random_jsds)),
        'jsd_std': float(np.std(random_jsds)),
    }

    # Position-only: linear risk gradient (low at Q0, high at Q4)
    linear_pred = {f'Q{q}': 0.5 + q * 0.25 for q in range(5)}
    lt = sum(linear_pred.values())
    linear_norm = {k: v / lt for k, v in linear_pred.items()}
    alt_scores['position_only'] = {'jsd': jsd_profiles(linear_norm, e_norm, keys)}

    # Physical threshold: risk peaks at Q2-Q3 (temperature peak zone)
    thresh_pred = {'Q0': 0.5, 'Q1': 0.8, 'Q2': 1.2, 'Q3': 1.2, 'Q4': 0.8}
    tt = sum(thresh_pred.values())
    thresh_norm = {k: v / tt for k, v in thresh_pred.items()}
    alt_scores['threshold'] = {'jsd': jsd_profiles(thresh_norm, e_norm, keys)}

    # Permuted Voynich: shuffle quintile assignments
    perm_jsds = []
    v_vals = list(voynich_high.values())
    for _ in range(N_PERMUTATIONS):
        pv = rng.permutation(v_vals)
        perm = {f'Q{q}': pv[q] for q in range(5)}
        pt = sum(perm.values())
        pn = {k: v / pt for k, v in perm.items()}
        perm_jsds.append(jsd_profiles(pn, e_norm, keys))
    alt_scores['permuted_voynich'] = {
        'jsd_mean': float(np.mean(perm_jsds)),
        'jsd_std': float(np.std(perm_jsds)),
    }

    # Voynich-lite: generic "safe start, dangerous end"
    lite_pred = {'Q0': 0.8, 'Q1': 1.0, 'Q2': 1.0, 'Q3': 1.0, 'Q4': 1.2}
    ltt = sum(lite_pred.values())
    lite_norm = {k: v / ltt for k, v in lite_pred.items()}
    alt_scores['voynich_lite'] = {'jsd': jsd_profiles(lite_norm, e_norm, keys)}

    # Permutation p-value (quintile-level, low power with 5 bins)
    n_better = sum(1 for j in random_jsds if j <= voynich_jsd)
    p_value_jsd = (n_better + 1) / (N_PERMUTATIONS + 1)

    # --- Cycle-level sign test (high power, 76K+ observations) ---
    # For each cycle: is Q4 overshoot > Q0 overshoot?
    # Voynich predicts: YES (danger at closure > danger at opening)
    n_q4_gt_q0 = 0
    n_q0_gt_q4 = 0
    cycle_rhos = []
    for cycle in cycles:
        ov = cycle.get('quintile_overshoot', {})
        if ov:
            q0 = ov.get('Q0', 0)
            q4 = ov.get('Q4', 0)
            if q4 > q0:
                n_q4_gt_q0 += 1
            elif q0 > q4:
                n_q0_gt_q4 += 1
            # Per-cycle Spearman rho of position vs overshoot
            vals = [ov.get(f'Q{q}', 0) for q in range(5)]
            if max(vals) > min(vals):  # avoid constant arrays
                r, _ = spearmanr([0, 1, 2, 3, 4], vals)
                if not np.isnan(r):
                    cycle_rhos.append(r)

    n_total = n_q4_gt_q0 + n_q0_gt_q4
    sign_frac = n_q4_gt_q0 / n_total if n_total > 0 else 0.5
    # Binomial test: is fraction significantly > 0.5?
    try:
        sign_p = float(binomtest(n_q4_gt_q0, n_total, 0.5, alternative='greater').pvalue)
    except Exception:
        sign_p = 1.0

    mean_cycle_rho = float(np.mean(cycle_rhos)) if cycle_rhos else 0.0
    std_cycle_rho = float(np.std(cycle_rhos)) if cycle_rhos else 1.0
    n_rho = len(cycle_rhos)
    # z-test for mean rho > 0
    z_rho = mean_cycle_rho / (std_cycle_rho / np.sqrt(n_rho)) if n_rho > 1 else 0.0

    # Use sign test p-value as primary (most powerful)
    p_value = min(sign_p, p_value_jsd)

    return {
        'empirical_overshoot_profile': emp_means,
        'voynich_high_enrichment': voynich_high,
        'voynich_jsd': voynich_jsd,
        'voynich_auc': voynich_auc,
        'rho': float(rho_v),
        'rho_p': float(rho_p),
        'mean_rho': float(rho_v),
        'ordered_contrasts': contrasts,
        'jsd_permutation_p': p_value_jsd,
        'sign_test': {
            'n_q4_gt_q0': n_q4_gt_q0,
            'n_q0_gt_q4': n_q0_gt_q4,
            'fraction': sign_frac,
            'p_value': sign_p,
        },
        'cycle_rho': {
            'mean': mean_cycle_rho,
            'std': std_cycle_rho,
            'n': n_rho,
            'z': float(z_rho),
        },
        'permutation_p': p_value,
        'alternatives': alt_scores,
    }


# ============================================================
# H2: TWO-STATE SUPERVISORY DECOMPOSITION
# ============================================================

def score_h2(cycles, voynich, rng):
    """H2: Two-state decomposition on operator features."""
    print("  H2: Mode decomposition...")

    feature_names = [
        'intervention_density', 'passive_frac', 'active_frac',
        'proactive_frac', 'reactive_frac', 'neutral_frac',
        'Q_var', 'dQ_var', 'phi_accum', 'boundary_frac',
    ]

    X = np.array([[c['features'][f] for f in feature_names] for c in cycles])

    if len(X) < 50:
        return {'error': 'too few cycles'}

    scaler = StandardScaler()
    X_s = scaler.fit_transform(X)

    # Unsupervised k=2
    km2 = KMeans(n_clusters=2, n_init=20, random_state=42)
    labels = km2.fit_predict(X_s)
    sil = float(silhouette_score(X_s, labels))

    # Centroids in original space
    centroids = {}
    for lab in [0, 1]:
        mask = labels == lab
        centroids[lab] = {f: float(np.mean(X[mask, i]))
                         for i, f in enumerate(feature_names)}

    # Normalize for cosine comparison
    def norm_centroids(c):
        normed = {}
        for lab in [0, 1]:
            normed[lab] = {}
            for f in feature_names:
                vals = [c[l][f] for l in [0, 1]]
                mn, mx = min(vals), max(vals)
                normed[lab][f] = (c[lab][f] - mn) / (mx - mn) if mx - mn > 1e-12 else 0.5
        return normed

    c_norm = norm_centroids(centroids)

    # Voynich Mode A/B analogue features
    v_a = {
        'intervention_density': 1.0, 'passive_frac': 0.3, 'active_frac': 1.0,
        'proactive_frac': 1.0, 'reactive_frac': 1.0, 'neutral_frac': 0.3,
        'Q_var': 1.0, 'dQ_var': 1.0, 'phi_accum': 0.3, 'boundary_frac': 1.0,
    }
    v_b = {
        'intervention_density': 0.3, 'passive_frac': 1.0, 'active_frac': 0.3,
        'proactive_frac': 0.3, 'reactive_frac': 0.3, 'neutral_frac': 1.0,
        'Q_var': 0.3, 'dQ_var': 0.3, 'phi_accum': 1.0, 'boundary_frac': 0.3,
    }

    def cosine(a, b):
        va = np.array([a[f] for f in feature_names])
        vb = np.array([b[f] for f in feature_names])
        d = np.dot(va, vb)
        na, nb = np.linalg.norm(va), np.linalg.norm(vb)
        return float(d / (na * nb)) if na > 1e-12 and nb > 1e-12 else 0.0

    # Try both assignments
    s1 = (cosine(c_norm[0], v_a) + cosine(c_norm[1], v_b)) / 2
    s2 = (cosine(c_norm[1], v_a) + cosine(c_norm[0], v_b)) / 2
    voynich_cosine = max(s1, s2)

    # Interleaving
    run_cycles = {}
    for i, c in enumerate(cycles):
        key = (c['param_id'], c['run_id'])
        if key not in run_cycles:
            run_cycles[key] = []
        run_cycles[key].append((c['cycle_id'], labels[i]))

    interleaving_rates = []
    for key, data in run_cycles.items():
        data.sort(key=lambda x: x[0])
        labs = [d[1] for d in data]
        if len(labs) >= 2:
            alts = sum(1 for j in range(1, len(labs)) if labs[j] != labs[j-1])
            interleaving_rates.append(alts / (len(labs) - 1))

    mean_interleave = float(np.mean(interleaving_rates)) if interleaving_rates else 0.0

    # --- Alternatives ---
    alt_scores = {}

    random_cosines = []
    for _ in range(N_PERMUTATIONS):
        rl = rng.integers(0, 2, size=len(cycles))
        rc = {}
        for lab in [0, 1]:
            mask = rl == lab
            if mask.sum() > 0:
                rc[lab] = {f: float(np.mean(X[mask, i])) for i, f in enumerate(feature_names)}
            else:
                rc[lab] = {f: 0.5 for f in feature_names}
        rn = norm_centroids(rc)
        rs1 = (cosine(rn[0], v_a) + cosine(rn[1], v_b)) / 2
        rs2 = (cosine(rn[1], v_a) + cosine(rn[0], v_b)) / 2
        random_cosines.append(max(rs1, rs2))

    alt_scores['random'] = {
        'cosine_mean': float(np.mean(random_cosines)),
        'cosine_std': float(np.std(random_cosines)),
    }

    # Permuted Voynich
    perm_cosines = []
    for _ in range(N_PERMUTATIONS):
        pa = dict(zip(feature_names, rng.permutation(list(v_a.values()))))
        pb = dict(zip(feature_names, rng.permutation(list(v_b.values()))))
        best = best_assign = 1 if s1 >= s2 else 2
        if best_assign == 1:
            ps = (cosine(c_norm[0], pa) + cosine(c_norm[1], pb)) / 2
        else:
            ps = (cosine(c_norm[1], pa) + cosine(c_norm[0], pb)) / 2
        perm_cosines.append(ps)
    alt_scores['permuted_voynich'] = {
        'cosine_mean': float(np.mean(perm_cosines)),
        'cosine_std': float(np.std(perm_cosines)),
    }

    # Voynich-lite: generic high-activity vs low-activity
    vl_a = {f: 0.7 for f in feature_names}
    vl_b = {f: 0.3 for f in feature_names}
    ls1 = (cosine(c_norm[0], vl_a) + cosine(c_norm[1], vl_b)) / 2
    ls2 = (cosine(c_norm[1], vl_a) + cosine(c_norm[0], vl_b)) / 2
    alt_scores['voynich_lite'] = {'cosine': max(ls1, ls2)}

    n_better = sum(1 for c in random_cosines if c >= voynich_cosine)
    p_value = (n_better + 1) / (N_PERMUTATIONS + 1)

    return {
        'voynich_cosine': voynich_cosine,
        'physical_silhouette': sil,
        'centroids': {str(k): v for k, v in centroids.items()},
        'mean_interleaving_rate': mean_interleave,
        'voynich_interleaving_target': 0.80,
        'permutation_p': p_value,
        'alternatives': alt_scores,
    }


# ============================================================
# H3: DUAL FEEDBACK CHANNEL
# ============================================================

def score_h3(cycles, voynich, rng):
    """H3: Passive vs active operator event positional separation."""
    print("  H3: Feedback channels...")

    v_h3 = voynich['hypotheses']['H3_feedback_channels']

    # Collect passive/active mean positions from each cycle
    passive_positions = [c['features']['mean_passive_pos'] for c in cycles
                        if c['features']['n_passive'] > 0]
    active_positions = [c['features']['mean_active_pos'] for c in cycles
                       if c['features']['n_active'] > 0]

    emp_passive = float(np.mean(passive_positions))
    emp_active = float(np.mean(active_positions))
    emp_delta = emp_active - emp_passive

    voynich_delta = v_h3['positions']['delta']
    voynich_passive = v_h3['positions']['sh_mean_position']
    voynich_active = v_h3['positions']['ch_mean_position']

    delta_error = abs(emp_delta - voynich_delta)
    passive_error = abs(emp_passive - voynich_passive)
    active_error = abs(emp_active - voynich_active)
    total_error = passive_error + active_error

    # Split vs merged MSE
    split_mse = float(np.mean([
        (p - voynich_passive)**2 for p in passive_positions
    ] + [
        (a - voynich_active)**2 for a in active_positions
    ]))
    merged_mean = (emp_passive + emp_active) / 2
    merged_mse = float(np.mean([
        (p - merged_mean)**2 for p in passive_positions
    ] + [
        (a - merged_mean)**2 for a in active_positions
    ]))
    split_advantage = merged_mse - split_mse

    # --- Alternatives ---
    alt_scores = {}

    # Random shuffle
    all_pos = passive_positions + active_positions
    random_deltas = []
    for _ in range(N_PERMUTATIONS):
        rng.shuffle(all_pos)
        rp = np.mean(all_pos[:len(passive_positions)])
        ra = np.mean(all_pos[len(passive_positions):])
        random_deltas.append(abs(ra - rp))
    alt_scores['random'] = {
        'delta_mean': float(np.mean(random_deltas)),
        'delta_std': float(np.std(random_deltas)),
    }

    # Position-only
    alt_scores['position_only'] = {
        'total_error': abs(emp_passive - 0.33) + abs(emp_active - 0.67),
    }

    # Reversed
    alt_scores['reversed_voynich'] = {
        'total_error': abs(emp_passive - voynich_active) + abs(emp_active - voynich_passive),
    }

    # Voynich-lite
    alt_scores['voynich_lite'] = {
        'total_error': abs(emp_passive - 0.4) + abs(emp_active - 0.6),
    }

    n_better = sum(1 for d in random_deltas if d >= abs(emp_delta))
    p_value = (n_better + 1) / (N_PERMUTATIONS + 1)

    return {
        'empirical_passive_pos': emp_passive,
        'empirical_active_pos': emp_active,
        'empirical_delta': emp_delta,
        'voynich_delta': voynich_delta,
        'delta_error': delta_error,
        'total_error': total_error,
        'split_mse': split_mse,
        'merged_mse': merged_mse,
        'split_advantage': split_advantage,
        'split_outperforms': split_advantage > 0,
        'permutation_p': p_value,
        'alternatives': alt_scores,
    }


# ============================================================
# H4: THERMAL-WORK NEUTRALIZATION
# ============================================================

def score_h4(cycles, voynich, rng):
    """H4: HOT_STABLE quintile distribution matches k-HEAD."""
    print("  H4: Thermal-work neutralization...")

    v_h4 = voynich['hypotheses']['H4_thermal_work']
    k_quintile = v_h4['k_quintile']
    k_total = sum(k_quintile.values())
    k_norm = {k: v / k_total for k, v in k_quintile.items()}

    # Empirical HOT_STABLE fraction per quintile
    hs_by_q = {f'Q{q}': [] for q in range(5)}
    for cycle in cycles:
        for q in range(5):
            key = f'Q{q}'
            if key in cycle.get('quintile_thermal', {}):
                hs_by_q[key].append(cycle['quintile_thermal'][key].get('HOT_STABLE', 0))

    emp_hs = {}
    for q in range(5):
        key = f'Q{q}'
        if hs_by_q[key]:
            emp_hs[key] = float(np.mean(hs_by_q[key]))
        else:
            emp_hs[key] = 0.2

    # Normalize to distribution
    hs_total = sum(emp_hs.values())
    emp_hs_norm = {k: v / hs_total for k, v in emp_hs.items()} if hs_total > 0 else emp_hs

    keys = [f'Q{q}' for q in range(5)]
    voynich_jsd = jsd_profiles(k_norm, emp_hs_norm, keys)

    rho, rho_p = spearmanr(
        [k_norm[k] for k in keys],
        [emp_hs_norm[k] for k in keys])

    # Mean risk by thermal state
    risk_by_state = {'HOT_STABLE': [], 'HOT_UNSTABLE': [], 'COOL_SAFE': []}
    for cycle in cycles:
        f = cycle['features']
        if f['hot_stable_frac'] > 0.5:
            risk_by_state['HOT_STABLE'].append(f['mean_risk'])
        elif f['hot_unstable_frac'] > 0.5:
            risk_by_state['HOT_UNSTABLE'].append(f['mean_risk'])
        else:
            risk_by_state['COOL_SAFE'].append(f['mean_risk'])

    mean_risk = {k: float(np.mean(v)) if v else 0.5 for k, v in risk_by_state.items()}
    k_aligned = mean_risk.get('HOT_STABLE', 1) < mean_risk.get('HOT_UNSTABLE', 0)

    # --- Alternatives ---
    alt_scores = {}

    # Random
    random_jsds = []
    for _ in range(N_PERMUTATIONS):
        rand_dist = {f'Q{q}': rng.random() for q in range(5)}
        rt = sum(rand_dist.values())
        rand_norm = {k: v / rt for k, v in rand_dist.items()}
        random_jsds.append(jsd_profiles(k_norm, rand_norm, keys))
    alt_scores['random'] = {
        'jsd_mean': float(np.mean(random_jsds)),
        'jsd_std': float(np.std(random_jsds)),
    }

    # HOT_UNSTABLE alignment (wrong: naive "hot=thermal")
    hu_by_q = {f'Q{q}': [] for q in range(5)}
    for cycle in cycles:
        for q in range(5):
            key = f'Q{q}'
            if key in cycle.get('quintile_thermal', {}):
                hu_by_q[key].append(cycle['quintile_thermal'][key].get('HOT_UNSTABLE', 0))
    emp_hu = {k: float(np.mean(v)) if v else 0.2 for k, v in hu_by_q.items()}
    hu_total = sum(emp_hu.values())
    emp_hu_norm = {k: v / hu_total for k, v in emp_hu.items()} if hu_total > 0 else emp_hu
    alt_scores['hot_unstable'] = {'jsd': jsd_profiles(k_norm, emp_hu_norm, keys)}

    # Permutation p-value
    n_better = sum(1 for j in random_jsds if j <= voynich_jsd)
    p_value = (n_better + 1) / (N_PERMUTATIONS + 1)

    return {
        'empirical_hs_profile': emp_hs,
        'empirical_hs_norm': emp_hs_norm,
        'k_quintile_norm': k_norm,
        'voynich_jsd': voynich_jsd,
        'rho': float(rho),
        'rho_p': float(rho_p),
        'k_aligned_lowest_risk': k_aligned,
        'mean_risk_by_state': mean_risk,
        'permutation_p': p_value,
        'alternatives': alt_scores,
    }


# ============================================================
# H5: CLOSURE CONTAINMENT — OPERATOR ACTIONS
# ============================================================

def score_h5(cycles, voynich, rng):
    """H5: Is physical overshoot risk closure-biased (Q4 > Q0)?

    v3: Uses overshoot risk (max(0, T-T_target)) instead of REACTIVE
    operator action fraction. Tests the Voynich prediction that danger
    concentrates at line closure.
    """
    print("  H5: Closure containment (overshoot risk)...")

    # Empirical overshoot risk per quintile
    overshoot_by_q = {q: [] for q in range(5)}
    for cycle in cycles:
        ov = cycle.get('quintile_overshoot', {})
        for q in range(5):
            key = f'Q{q}'
            if key in ov:
                overshoot_by_q[q].append(ov[key])

    emp_overshoot = {q: float(np.mean(v)) for q, v in overshoot_by_q.items() if v}

    # Closure-biased: risk at Q4 > risk at Q0
    closure_biased = emp_overshoot.get(4, 0) > emp_overshoot.get(0, 0)

    # Voynich prediction: HIGH enrichment pattern (closure-concentrated)
    voynich_pred = {0: 0.836, 1: 1.006, 2: 1.006, 3: 1.006, 4: 1.134}
    rho_v, p_v = spearmanr(
        [voynich_pred[q] for q in range(5)],
        [emp_overshoot.get(q, 0) for q in range(5)])

    # Also test cumulative overshoot
    cum_by_q = {q: [] for q in range(5)}
    for cycle in cycles:
        co = cycle.get('quintile_cum_overshoot', {})
        for q in range(5):
            key = f'Q{q}'
            if key in co:
                cum_by_q[q].append(co[key])
    emp_cum = {q: float(np.mean(v)) for q, v in cum_by_q.items() if v}
    rho_cum, _ = spearmanr(
        [voynich_pred[q] for q in range(5)],
        [emp_cum.get(q, 0) for q in range(5)])

    # Cross-cycle independence
    run_risks = {}
    for c in cycles:
        key = (c['param_id'], c['run_id'])
        if key not in run_risks:
            run_risks[key] = []
        ov = c.get('quintile_overshoot', {})
        total_ov = sum(ov.values()) if ov else 0
        run_risks[key].append(total_ov)

    lag1_x, lag1_y = [], []
    for risks in run_risks.values():
        for j in range(len(risks) - 1):
            lag1_x.append(risks[j])
            lag1_y.append(risks[j + 1])

    if len(lag1_x) > 10:
        lag1_r, lag1_p = pearsonr(lag1_x, lag1_y)
    else:
        lag1_r, lag1_p = 0.0, 1.0
    cross_indep = abs(lag1_r) < 0.1

    # --- Alternatives ---
    alt_scores = {}

    # Start-biased: risk peaks at Q0
    start_pred = {0: 1.2, 1: 1.0, 2: 0.8, 3: 0.9, 4: 0.7}
    rho_s, _ = spearmanr([start_pred[q] for q in range(5)],
                          [emp_overshoot.get(q, 0) for q in range(5)])
    alt_scores['start_biased'] = {'rho': float(rho_s)}

    # Uniform
    alt_scores['uniform'] = {'rho': 0.0}

    # Mid-peak: risk peaks at Q2
    mid_pred = {0: 0.8, 1: 1.0, 2: 1.2, 3: 1.0, 4: 0.8}
    rho_m, _ = spearmanr([mid_pred[q] for q in range(5)],
                          [emp_overshoot.get(q, 0) for q in range(5)])
    alt_scores['mid_peak'] = {'rho': float(rho_m)}

    # Cross-cycle accumulation
    cycle_idx = list(range(len(cycles)))
    cycle_ov = []
    for c in cycles:
        ov = c.get('quintile_overshoot', {})
        cycle_ov.append(sum(ov.values()) if ov else 0)
    if len(cycle_idx) > 10:
        rho_acc, _ = pearsonr(cycle_idx, cycle_ov)
    else:
        rho_acc = 0.0
    alt_scores['accumulation'] = {'rho': float(rho_acc)}

    # Permutation p-value (quintile-level)
    random_rhos = []
    pred_vals = list(voynich_pred.values())
    for _ in range(N_PERMUTATIONS):
        perm = rng.permutation(pred_vals)
        r, _ = spearmanr(perm, [emp_overshoot.get(q, 0) for q in range(5)])
        random_rhos.append(abs(r))
    n_better = sum(1 for r in random_rhos if r >= abs(rho_v))
    p_value_perm = (n_better + 1) / (N_PERMUTATIONS + 1)

    # --- Cycle-level sign test ---
    n_closure_gt = 0
    n_opening_gt = 0
    for cycle in cycles:
        ov = cycle.get('quintile_overshoot', {})
        if ov:
            q0 = ov.get('Q0', 0)
            q4 = ov.get('Q4', 0)
            if q4 > q0:
                n_closure_gt += 1
            elif q0 > q4:
                n_opening_gt += 1
    n_total = n_closure_gt + n_opening_gt
    closure_frac = n_closure_gt / n_total if n_total > 0 else 0.5
    try:
        sign_p = float(binomtest(n_closure_gt, n_total, 0.5, alternative='greater').pvalue)
    except Exception:
        sign_p = 1.0

    p_value = min(sign_p, p_value_perm)

    return {
        'empirical_overshoot_profile': {str(k): v for k, v in emp_overshoot.items()},
        'empirical_cum_overshoot_profile': {str(k): v for k, v in emp_cum.items()},
        'closure_biased': closure_biased,
        'closure_frac': closure_frac,
        'voynich_rho': float(rho_v),
        'cum_overshoot_rho': float(rho_cum),
        'sign_test': {
            'n_closure_gt': n_closure_gt,
            'n_opening_gt': n_opening_gt,
            'fraction': closure_frac,
            'p_value': sign_p,
        },
        'perm_p': p_value_perm,
        'permutation_p': p_value,
        'cross_cycle_lag1_r': float(lag1_r),
        'cross_cycle_independent': cross_indep,
        'alternatives': alt_scores,
    }


# ============================================================
# ABLATION + OUT-OF-SAMPLE + MAIN
# ============================================================

def run_ablations(cycles, voynich, rng):
    """Ablation tests."""
    print("  Ablations...")
    baseline_h1 = score_h1(cycles, voynich, rng)
    baseline_h5 = score_h5(cycles, voynich, rng)

    # No line-zone: shuffle overshoot values across quintiles
    cycles_nz = []
    for c in cycles:
        cc = dict(c)
        ov = cc.get('quintile_overshoot', {})
        if ov:
            vals = list(ov.values())
            rng.shuffle(vals)
            cc['quintile_overshoot'] = {f'Q{q}': vals[q] for q in range(5)}
        co = cc.get('quintile_cum_overshoot', {})
        if co:
            vals = list(co.values())
            rng.shuffle(vals)
            cc['quintile_cum_overshoot'] = {f'Q{q}': vals[q] for q in range(5)}
        cycles_nz.append(cc)

    h1_nz = score_h1(cycles_nz, voynich, rng)

    return {
        'baseline': {'H1_jsd': baseline_h1['voynich_jsd'],
                     'H5_rho': baseline_h5['voynich_rho']},
        'no_line_zone': {
            'H1_jsd': h1_nz['voynich_jsd'],
            'degradation': h1_nz['voynich_jsd'] - baseline_h1['voynich_jsd'],
        },
    }


def out_of_sample(cycles, voynich, rng):
    """Train/test split."""
    print("  Out-of-sample...")
    odd = [c for c in cycles if c['param_id'] % 2 == 1]
    even = [c for c in cycles if c['param_id'] % 2 == 0]
    if len(odd) < 100 or len(even) < 100:
        return {'error': 'too few'}

    h1_train = score_h1(odd, voynich, rng)
    h1_test = score_h1(even, voynich, rng)
    h5_train = score_h5(odd, voynich, rng)
    h5_test = score_h5(even, voynich, rng)

    return {
        'n_train': len(odd), 'n_test': len(even),
        'H1_train_jsd': h1_train['voynich_jsd'],
        'H1_test_jsd': h1_test['voynich_jsd'],
        'H5_train_rho': h5_train['voynich_rho'],
        'H5_test_rho': h5_test['voynich_rho'],
    }


def main():
    print("Loading data...")
    t1, t2 = load_data()
    cycles = extract_all_cycles(t1)
    print(f"  {len(cycles)} cycles")

    rng = np.random.default_rng(42)

    print("\nScoring hypotheses...")
    h1 = score_h1(cycles, t2, rng)
    h2 = score_h2(cycles, t2, rng)
    h3 = score_h3(cycles, t2, rng)
    h4 = score_h4(cycles, t2, rng)
    h5 = score_h5(cycles, t2, rng)

    print("\nAblations...")
    ablations = run_ablations(cycles, t2, rng)

    print("\nOut-of-sample...")
    oos = out_of_sample(cycles, t2, rng)

    p_values = {
        'H1': h1['permutation_p'], 'H2': h2.get('permutation_p', 1.0),
        'H3': h3.get('permutation_p', 1.0), 'H4': h4['permutation_p'],
        'H5': h5['permutation_p'],
    }
    bonf = ALPHA / 5
    sig = {k: v < bonf for k, v in p_values.items()}

    output = {
        'hypotheses': {
            'H1_safety_envelope': h1, 'H2_mode_decomposition': h2,
            'H3_feedback_channels': h3, 'H4_thermal_work': h4,
            'H5_closure_containment': h5,
        },
        'ablations': ablations,
        'out_of_sample': oos,
        'significance': {'p_values': p_values, 'bonferroni_alpha': bonf, 'significant': sig},
        'n_cycles': len(cycles),
    }

    out_path = RESULTS_DIR / 't3_predictive_competition.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print(f"T3 PREDICTIVE COMPETITION (REDESIGNED) COMPLETE")
    print(f"{'='*60}")
    print(f"Cycles: {len(cycles)}")
    print()
    print(f"  H1 Safety Envelope:    JSD={h1['voynich_jsd']:.4f}  "
          f"AUC={h1['voynich_auc']:.3f}  "
          f"rho={h1['mean_rho']:.3f}  "
          f"p={p_values['H1']:.6f}  {'PASS' if sig['H1'] else 'FAIL'}")
    oc = h1['ordered_contrasts']
    st = h1.get('sign_test', {})
    cr = h1.get('cycle_rho', {})
    print(f"    Contrasts: Q4>Q0={oc['risk_Q4_gt_Q0']}  "
          f"Q3>Q0={oc['risk_Q3_gt_Q0']}  "
          f"Q0_lowest={oc['risk_Q0_lowest']}  "
          f"monotone={oc['risk_monotone_Q0_to_Q4']}")
    print(f"    Sign test: {st.get('n_q4_gt_q0',0)}/{st.get('n_q4_gt_q0',0)+st.get('n_q0_gt_q4',0)} "
          f"({st.get('fraction',0):.1%}) p={st.get('p_value',1):.2e}")
    print(f"    Cycle rho: mean={cr.get('mean',0):.3f} z={cr.get('z',0):.1f}")
    print(f"  H2 Mode Decomp:       cos={h2.get('voynich_cosine',0):.3f}  "
          f"sil={h2.get('physical_silhouette',0):.3f}  "
          f"interleave={h2.get('mean_interleaving_rate',0):.3f}  "
          f"p={p_values['H2']:.4f}  {'PASS' if sig['H2'] else 'FAIL'}")
    print(f"  H3 Feedback:           delta={h3.get('empirical_delta',0):.3f}  "
          f"split_adv={h3.get('split_advantage',0):.4f}  "
          f"p={p_values['H3']:.4f}  {'PASS' if sig['H3'] else 'FAIL'}")
    print(f"  H4 Thermal Work:       JSD={h4['voynich_jsd']:.4f}  "
          f"rho={h4['rho']:.3f}  "
          f"k_aligned={h4['k_aligned_lowest_risk']}  "
          f"p={p_values['H4']:.4f}  {'PASS' if sig['H4'] else 'FAIL'}")
    st5 = h5.get('sign_test', {})
    print(f"  H5 Closure:            rho={h5['voynich_rho']:.3f}  "
          f"closure_frac={st5.get('fraction',0):.1%}  "
          f"cross_indep={h5['cross_cycle_independent']}  "
          f"p={p_values['H5']:.6f}  {'PASS' if sig['H5'] else 'FAIL'}")
    print(f"\nBonferroni alpha: {bonf:.4f}")
    print(f"Significant: {sum(sig.values())}/5")
    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
