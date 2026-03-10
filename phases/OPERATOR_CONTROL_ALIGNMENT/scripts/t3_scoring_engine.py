"""
T3: Scoring Engine — Phase 556: OPERATOR_CONTROL_ALIGNMENT
===========================================================

Scores 6 hypotheses against T1 empirical data using T2 predictions.
Loads per-cycle data from compact numpy arrays (t1_cycles.npz).
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats
from scipy.spatial.distance import jensenshannon

RESULTS_DIR = Path(__file__).parent.parent / 'results'

ACTION_NAMES = [
    'INCREASE_BELOW', 'INCREASE_ABOVE', 'DECREASE_ABOVE',
    'DECREASE_BELOW', 'HOLD_AT', 'HOLD_OFF', 'CHECK',
]
IB, IA, DA, DB, HA, HO, CK = range(7)
N_ACTIONS = 7
N_Q = 5
N_PERM = 1000


def load_data():
    summary = json.load(open(RESULTS_DIR / 't1_operator_events.json'))
    t2 = json.load(open(RESULTS_DIR / 't2_voynich_predictions.json'))
    npz = np.load(RESULTS_DIR / 't1_cycles.npz')
    return summary, npz, t2


def jsd(p, q):
    p = np.array(p, dtype=float) + 1e-10
    q = np.array(q, dtype=float) + 1e-10
    p /= p.sum()
    q /= q.sum()
    return float(jensenshannon(p, q) ** 2)


def score_h1(qa, rng, predictions):
    """H1: Three-Phase Operator Scheduling."""
    pred = predictions['H1']
    n = qa.shape[0]

    # Aggregate quintile action profile
    agg = qa.mean(axis=0)  # (5, 7)

    # INCREASE_BELOW profile
    emp_ib = agg[:, IB]
    q1_peak = int(np.argmax(emp_ib)) == 1
    q1_peak_quintile = int(np.argmax(emp_ib))

    # Closure discontinuity
    q_jsds = [jsd(agg[q], agg[q+1]) for q in range(N_Q - 1)]
    closure_ratio = q_jsds[3] / max(q_jsds[2], 1e-10) if len(q_jsds) >= 4 else 0

    # Asymmetry
    ib_asymmetry = float((agg[0, IB] + agg[1, IB]) / 2 - (agg[3, IB] + agg[4, IB]) / 2)
    da_asymmetry = float((agg[3, DA] + agg[4, DA]) / 2 - (agg[0, DA] + agg[1, DA]) / 2)

    # Normalize empirical
    emp_norm = agg / (agg.sum(axis=1, keepdims=True) + 1e-10)

    # Voynich predicted profile
    voynich_p = np.ones((N_Q, N_ACTIONS))
    enrich = pred['enrichment_profile']
    for q in range(N_Q):
        qk = f'Q{q}'
        if qk in enrich:
            for act, val in enrich[qk].items():
                if act in ACTION_NAMES:
                    voynich_p[q, ACTION_NAMES.index(act)] = val
    voynich_p /= voynich_p.sum(axis=1, keepdims=True)
    voynich_jsd = float(np.mean([jsd(emp_norm[q], voynich_p[q]) for q in range(N_Q)]))

    # Position-only: linear gradient
    pos_p = np.zeros((N_Q, N_ACTIONS))
    for q in range(N_Q):
        t = q / 4.0
        pos_p[q, IB] = 1.0 - t
        pos_p[q, DA] = t
        pos_p[q, HA] = 0.3
        pos_p[q, CK] = 0.2
    pos_p /= pos_p.sum(axis=1, keepdims=True)
    position_jsd = float(np.mean([jsd(emp_norm[q], pos_p[q]) for q in range(N_Q)]))

    # Flat
    flat_p = np.ones((N_Q, N_ACTIONS)) / N_ACTIONS
    flat_jsd = float(np.mean([jsd(emp_norm[q], flat_p[q]) for q in range(N_Q)]))

    # Voynich-lite
    lite_p = np.ones((N_Q, N_ACTIONS))
    lite_p[0, HA] = 1.2; lite_p[0, DB] = 1.1
    lite_p[4, DA] = 1.1; lite_p[4, HO] = 1.1
    lite_p /= lite_p.sum(axis=1, keepdims=True)
    lite_jsd = float(np.mean([jsd(emp_norm[q], lite_p[q]) for q in range(N_Q)]))

    # Equal-complexity
    ec_p = np.ones((N_Q, N_ACTIONS))
    ec_p[0, IB] = 1.311; ec_p[3, DA] = 1.05; ec_p[4, DA] = 1.10
    ec_p /= ec_p.sum(axis=1, keepdims=True)
    ec_jsd = float(np.mean([jsd(emp_norm[q], ec_p[q]) for q in range(N_Q)]))

    # Permutation test: shuffle quintile rows
    perm_jsds = []
    for _ in range(N_PERM):
        perm_agg = agg[rng.permutation(N_Q)]
        pn = perm_agg / (perm_agg.sum(axis=1, keepdims=True) + 1e-10)
        perm_jsds.append(np.mean([jsd(pn[q], voynich_p[q]) for q in range(N_Q)]))
    perm_p = float(np.mean(np.array(perm_jsds) <= voynich_jsd))

    # Ablation: replace Voynich with linear
    ablation_jsd = position_jsd
    ablation_deg = ablation_jsd - voynich_jsd

    # OOS
    mid = n // 2
    train_agg = qa[:mid].mean(axis=0)
    test_agg = qa[mid:].mean(axis=0)
    tn = lambda a: a / (a.sum(axis=1, keepdims=True) + 1e-10)
    train_jsd = float(np.mean([jsd(tn(train_agg)[q], voynich_p[q]) for q in range(N_Q)]))
    test_jsd = float(np.mean([jsd(tn(test_agg)[q], voynich_p[q]) for q in range(N_Q)]))

    return {
        'empirical_quintile_actions': agg.tolist(),
        'empirical_ib_profile': emp_ib.tolist(),
        'q1_peak': q1_peak,
        'q1_peak_quintile': q1_peak_quintile,
        'closure_ratio': float(closure_ratio),
        'adjacent_jsds': [float(x) for x in q_jsds],
        'ib_asymmetry': ib_asymmetry,
        'da_asymmetry': da_asymmetry,
        'voynich_jsd': voynich_jsd,
        'position_jsd': position_jsd,
        'flat_jsd': flat_jsd,
        'voynich_lite_jsd': lite_jsd,
        'equal_complexity_jsd': ec_jsd,
        'voynich_beats_position': voynich_jsd < position_jsd,
        'voynich_beats_lite': voynich_jsd < lite_jsd,
        'voynich_beats_ec': voynich_jsd < ec_jsd,
        'permutation_p': perm_p,
        'ablation_jsd': float(ablation_jsd),
        'ablation_degradation': float(ablation_deg),
        'oos_train_jsd': train_jsd,
        'oos_test_jsd': test_jsd,
        'n_cycles': n,
    }


def score_h2(hmm_interleaving, hmm_persistence, hmm_nc, hmm_k, summary, predictions, rng):
    """H2: Inferred Supervisory Decomposition."""
    pred = predictions['H2']
    hmm_k_dist = summary.get('hmm_bic_k_distribution', {})

    # Filter to cycles that have HMM data
    valid = hmm_interleaving >= 0
    n_valid = valid.sum()
    if n_valid < 10:
        return {'error': 'insufficient HMM data', 'n_hmm_cycles': int(n_valid)}

    il = hmm_interleaving[valid]
    pers = hmm_persistence[valid]
    nc = hmm_nc[valid]

    mean_il = float(il.mean())
    mean_pers = float(pers.mean())
    nc_frac = float(nc.mean())

    pers_range = pred['persistence_range']
    pers_in_range = pers_range[0] <= mean_pers <= pers_range[1]

    # Permutation: shuffle nc labels
    perm_nc_fracs = []
    for _ in range(N_PERM):
        perm_nc_fracs.append(float(rng.permutation(nc).mean()))
    perm_p = float(np.mean(np.array(perm_nc_fracs) >= nc_frac))

    # Ablation: random 2-state
    ablation_il = 0.5  # random binary = 50% interleaving
    ablation_deg = ablation_il - mean_il

    significant = (nc_frac >= pred['interleaving_threshold'] and
                   pers_in_range and perm_p < 0.01)

    return {
        'hmm_k_distribution': hmm_k_dist,
        'n_hmm_cycles': int(n_valid),
        'mean_interleaving': mean_il,
        'nc_fraction': nc_frac,
        'mean_persistence': mean_pers,
        'persistence_in_range': pers_in_range,
        'permutation_p': perm_p,
        'ablation_degradation': float(ablation_deg),
        'significant': significant,
    }


def score_h3(meta, bigrams, predictions, rng):
    """H3: Dual Feedback Channels."""
    pred = predictions['H3']
    # meta columns: length, overshoot, obs_pos, int_pos, passive_pos, active_pos
    passive_pos = meta[:, 4]
    active_pos = meta[:, 5]

    # Filter valid
    pv = passive_pos >= 0
    av = active_pos >= 0
    both = pv & av

    if both.sum() < 100:
        return {'error': 'insufficient observation data'}

    pp = float(passive_pos[pv].mean())
    ap = float(active_pos[av].mean())
    delta = ap - pp

    # Routing: after passive (HOLD_AT=4, HOLD_OFF=5) vs active (CHECK=6)
    # Aggregate bigram rows
    passive_next = bigrams[:, HA, :].mean(axis=0) + bigrams[:, HO, :].mean(axis=0)
    passive_next /= max(passive_next.sum(), 1e-10)
    active_next = bigrams[:, CK, :].mean(axis=0)
    active_next /= max(active_next.sum(), 1e-10)

    passive_to_ib = float(passive_next[IB])
    def entropy(p):
        p = p[p > 1e-10]
        return float(-np.sum(p * np.log2(p)))
    passive_entropy = entropy(passive_next)
    active_entropy = entropy(active_next)

    # Split vs merged
    all_obs = np.concatenate([passive_pos[pv], active_pos[av]])
    merged_pos = float(all_obs.mean())
    split_error = (pp - pred['passive_mean_position'])**2 + (ap - pred['active_mean_position'])**2
    pred_merged = (pred['passive_mean_position'] + pred['active_mean_position']) / 2
    merged_error = 2 * (merged_pos - pred_merged)**2
    split_adv = merged_error - split_error

    # Permutation
    n_p = pv.sum()
    all_p = np.concatenate([passive_pos[pv], active_pos[av]])
    perm_deltas = []
    for _ in range(N_PERM):
        perm = rng.permutation(len(all_p))
        pd = all_p[perm[n_p:]].mean() - all_p[perm[:n_p]].mean()
        perm_deltas.append(pd)
    perm_p = float(np.mean(np.array(perm_deltas) >= delta))

    # OOS
    n = len(meta)
    mid = n // 2
    tp = passive_pos[:mid]; ta = active_pos[:mid]
    ep = passive_pos[mid:]; ea = active_pos[mid:]
    train_d = float(ta[ta >= 0].mean() - tp[tp >= 0].mean()) if (ta >= 0).any() and (tp >= 0).any() else 0
    test_d = float(ea[ea >= 0].mean() - ep[ep >= 0].mean()) if (ea >= 0).any() and (ep >= 0).any() else 0

    significant = delta > pred['pass_criteria']['delta_min'] and perm_p < 0.01

    return {
        'passive_mean_pos': pp,
        'active_mean_pos': ap,
        'delta': float(delta),
        'delta_positive': delta > 0,
        'delta_sufficient': delta >= pred['pass_criteria']['delta_min'],
        'passive_to_increase_below': passive_to_ib,
        'passive_next_entropy': passive_entropy,
        'active_next_entropy': active_entropy,
        'active_higher_entropy': active_entropy > passive_entropy,
        'split_error': float(split_error),
        'merged_error': float(merged_error),
        'split_advantage': float(split_adv),
        'split_outperforms': split_adv > 0,
        'permutation_p': perm_p,
        'oos_train_delta': train_d,
        'oos_test_delta': test_d,
        'significant': significant,
    }


def score_h4(qa, counts, positions, params, predictions, rng):
    """H4: Preventive Stabilization Channel."""
    pred = predictions['H4']
    n = qa.shape[0]
    lengths = counts.sum(axis=1).astype(float)

    # Existence
    has_db = counts[:, DB] > 0
    existence_frac = float(has_db.mean())
    total_db = counts[:, DB].sum()
    total_acts = counts.sum()
    db_frac = float(total_db / max(total_acts, 1))

    # Mean position
    db_pos = positions[:, DB]
    valid = db_pos >= 0
    mean_db_pos = float(db_pos[valid].mean()) if valid.any() else -1
    early_biased = mean_db_pos < pred['mean_position_max'] if mean_db_pos >= 0 else False

    # Context independence
    da_rates = counts[:, DA] / np.maximum(lengths, 1)
    db_rates = counts[:, DB] / np.maximum(lengths, 1)
    plant_idx = params[:, 0]
    op_idx = params[:, 1]

    median_da = float(np.median(da_rates))
    high_corr_next_db = []
    low_corr_next_db = []
    for i in range(n - 1):
        if plant_idx[i] != plant_idx[i+1] or op_idx[i] != op_idx[i+1]:
            continue
        ndb = db_rates[i+1]
        if da_rates[i] > median_da:
            high_corr_next_db.append(ndb)
        else:
            low_corr_next_db.append(ndb)

    if high_corr_next_db and low_corr_next_db:
        context_diff = float(abs(np.mean(high_corr_next_db) - np.mean(low_corr_next_db)))
        context_independent = context_diff < pred['context_independence_max_diff']
    else:
        context_diff = -1.0
        context_independent = False

    # Correction-burden-reducing
    early_prev = (qa[:, 0, DB] + qa[:, 1, DB]) / 2
    late_corr = (qa[:, 3, DA] + qa[:, 4, DA]) / 2
    corr_rho, corr_p = stats.spearmanr(early_prev, late_corr)

    # Q4 avoidance
    agg = qa.mean(axis=0)  # (5, 7)
    db_q4 = agg[4, DB]
    db_mean = agg[:, DB].mean()
    q4_enrichment = float(db_q4 / max(db_mean, 1e-10))
    q4_depleted = q4_enrichment < pred['q4_depletion_max']

    # Permutation
    perm_positions = [float(rng.uniform(0, 1, size=valid.sum()).mean()) for _ in range(N_PERM)]
    perm_p = float(np.mean(np.array(perm_positions) <= mean_db_pos)) if mean_db_pos >= 0 else 1.0

    significant = (db_frac >= pred['existence_min_fraction'] and
                   early_biased and context_independent and q4_depleted)

    return {
        'existence_frac': existence_frac,
        'db_frac': db_frac,
        'mean_position': mean_db_pos,
        'early_biased': early_biased,
        'context_diff': context_diff,
        'context_independent': context_independent,
        'correction_rho': float(corr_rho),
        'correction_p': float(corr_p),
        'q4_enrichment': q4_enrichment,
        'q4_depleted': q4_depleted,
        'permutation_p': perm_p,
        'significant': significant,
    }


def _vectorized_corr(A, B):
    """Vectorized row-wise Pearson correlation between matching rows of A and B."""
    # A, B: (N, D)
    A = A - A.mean(axis=1, keepdims=True)
    B = B - B.mean(axis=1, keepdims=True)
    num = (A * B).sum(axis=1)
    den = np.sqrt((A**2).sum(axis=1) * (B**2).sum(axis=1))
    den = np.maximum(den, 1e-10)
    return num / den


def score_h5(qa, counts, params, predictions, rng):
    """H5: Instruction-Profile Locality."""
    pred = predictions['H5']
    n = qa.shape[0]
    plant_idx = params[:, 0]
    op_idx = params[:, 1]

    # Flatten quintile-actions for correlation
    profiles = qa.reshape(n, -1).astype(np.float64)  # (N, 35)

    # Same-parameterization consecutive mask
    same_param = ((plant_idx[:-1] == plant_idx[1:]) &
                  (op_idx[:-1] == op_idx[1:]))
    idx = np.where(same_param)[0]

    # Vectorized lag-1 correlation
    if len(idx) > 0:
        corrs = _vectorized_corr(profiles[idx], profiles[idx + 1])
        valid = ~np.isnan(corrs)
        raw_lag1 = float(corrs[valid].mean()) if valid.any() else 0
        n_pairs = int(valid.sum())
    else:
        raw_lag1 = 0
        n_pairs = 0

    # Parameterization-mediated shuffle (sample for speed)
    # Use a sample of 50K pairs max
    sample_idx = idx if len(idx) < 50000 else rng.choice(idx, 50000, replace=False)
    shuffled_corrs = []
    for _ in range(min(N_PERM, 100)):
        perm = rng.permutation(len(sample_idx))
        perm_corrs = _vectorized_corr(profiles[sample_idx], profiles[sample_idx[perm] + 1])
        valid = ~np.isnan(perm_corrs)
        if valid.any():
            shuffled_corrs.append(float(perm_corrs[valid].mean()))

    shuffle_mean = float(np.mean(shuffled_corrs)) if shuffled_corrs else 0
    shuffle_p = float(np.mean(np.array(shuffled_corrs) < raw_lag1)) if shuffled_corrs else 1.0

    # No compensatory pattern (vectorized)
    lengths = counts.sum(axis=1).astype(float)
    da_rates = counts[:, DA] / np.maximum(lengths, 1)
    db_rates = counts[:, DB] / np.maximum(lengths, 1)
    median_da = float(np.median(da_rates))

    # For consecutive same-param pairs
    if len(idx) > 0:
        high_mask = da_rates[idx] > median_da
        low_mask = ~high_mask
        next_db = db_rates[idx + 1]
        high_next_db = next_db[high_mask]
        low_next_db = next_db[low_mask]
        if len(high_next_db) > 0 and len(low_next_db) > 0:
            comp_ratio = float(high_next_db.mean() / max(low_next_db.mean(), 1e-10))
        else:
            comp_ratio = 1.0
    else:
        comp_ratio = 1.0
    no_compensatory = comp_ratio <= pred['compensatory_ratio_max']

    significant = (raw_lag1 > pred['raw_lag1_min'] and
                   shuffle_p > pred['shuffle_collapse_p_min'] and
                   no_compensatory)

    return {
        'raw_lag1': raw_lag1,
        'shuffle_mean_lag1': shuffle_mean,
        'shuffle_p': shuffle_p,
        'shuffle_collapses': shuffle_p > pred['shuffle_collapse_p_min'],
        'compensatory_ratio': comp_ratio,
        'no_compensatory': no_compensatory,
        'significant': significant,
        'n_lag1_pairs': n_pairs,
    }


def score_h6(qa, bigrams, qr_stability, qr_phase_activity, predictions, rng):
    """H6: Hazard Immunity of Energy Operations."""
    pred = predictions['H6']
    n = qa.shape[0]

    # Transition rates from averaged bigrams
    mean_bg = bigrams.mean(axis=0)  # (7, 7)

    # IB -> DA
    ib_row = mean_bg[IB]
    ib_to_da = float(ib_row[DA] / max(ib_row.sum(), 1e-10))

    # CHECK -> DA
    ck_row = mean_bg[CK]
    check_to_da = float(ck_row[DA] / max(ck_row.sum(), 1e-10))

    transition_immune = ib_to_da < pred['ib_to_da_max']
    da_ratio = float(check_to_da / max(ib_to_da, 1e-10))
    check_more_dangerous = da_ratio >= pred['check_to_da_ratio_min']

    # Stability context
    med_stab = float(np.median(qr_stability[qr_stability > 0])) if (qr_stability > 0).any() else 0
    med_pa = float(np.median(qr_phase_activity[qr_phase_activity > 0])) if (qr_phase_activity > 0).any() else 0

    # IB fraction in low vs high stability quintiles
    ib_fracs = qa[:, :, IB]  # (N, 5)
    low_stab_mask = qr_stability < med_stab
    high_stab_mask = qr_stability >= med_stab

    ib_low = float(ib_fracs[low_stab_mask].mean()) if low_stab_mask.any() else 0
    ib_high = float(ib_fracs[high_stab_mask].mean()) if high_stab_mask.any() else 0
    stab_enrich = float(ib_low / max(ib_high, 1e-10))
    stability_enriched = stab_enrich >= pred['ib_low_stability_enrichment_min']

    # Phase activity depletion
    low_pa_mask = qr_phase_activity <= med_pa
    high_pa_mask = qr_phase_activity > med_pa
    ib_low_pa = float(ib_fracs[low_pa_mask].mean()) if low_pa_mask.any() else 0
    ib_high_pa = float(ib_fracs[high_pa_mask].mean()) if high_pa_mask.any() else 0
    phase_depl = float(ib_high_pa / max(ib_low_pa, 1e-10))
    phase_depleted = phase_depl <= pred['ib_high_phase_depletion_max']

    # Permutation: shuffle action labels in bigrams
    perm_ib_da = []
    sample = min(n, 2000)
    bg_sample = bigrams[:sample]
    for _ in range(N_PERM):
        perm = rng.permutation(N_ACTIONS)
        pbg = bg_sample[:, perm, :][:, :, perm]
        pmean = pbg.mean(axis=0)
        row = pmean[IB]
        if row.sum() > 0:
            perm_ib_da.append(row[DA] / row.sum())
    perm_p = float(np.mean(np.array(perm_ib_da) <= ib_to_da)) if perm_ib_da else 1.0

    significant = (transition_immune and check_more_dangerous and
                   stability_enriched and phase_depleted)

    return {
        'mean_ib_to_da': ib_to_da,
        'mean_check_to_da': check_to_da,
        'da_ratio': da_ratio,
        'transition_immune': transition_immune,
        'check_more_dangerous': check_more_dangerous,
        'stab_enrichment': stab_enrich,
        'stability_enriched': stability_enriched,
        'phase_depletion': phase_depl,
        'phase_depleted': phase_depleted,
        'ib_low_stab': ib_low,
        'ib_high_stab': ib_high,
        'permutation_p': perm_p,
        'significant': significant,
    }


def score_per_apparatus(qa, params, summary, predictions, rng):
    """Re-score H1 per apparatus family."""
    families = summary.get('apparatus_families', {})
    if not families:
        return {}
    assignments = families.get('plant_assignments', [])
    names = families.get('names', [])
    plant_idx = params[:, 0]

    results = {}
    for fi, fname in enumerate(names):
        mask = np.array([assignments[int(pi)] == fi for pi in plant_idx])
        if mask.sum() < 100:
            results[fname] = {'n_cycles': int(mask.sum()), 'skipped': True}
            continue
        h1 = score_h1(qa[mask], rng, predictions)
        results[fname] = {
            'n_cycles': int(mask.sum()),
            'h1_voynich_jsd': h1['voynich_jsd'],
            'h1_position_jsd': h1['position_jsd'],
            'h1_beats_position': h1['voynich_beats_position'],
            'h1_q1_peak': h1['q1_peak'],
            'h1_closure_ratio': h1['closure_ratio'],
        }
    return results


def main():
    import sys
    print("Loading data...", flush=True)
    summary, npz, t2 = load_data()
    print("Data loaded.", flush=True)
    predictions = t2['predictions']

    qa = npz['quintile_actions']
    bg = npz['bigrams']
    pos = npz['mean_positions']
    counts = npz['action_counts']
    meta = npz['meta']
    params = npz['params']
    qr_stab = npz['qr_stability']
    qr_pa = npz['qr_phase_activity']
    hmm_il = npz['hmm_interleaving']
    hmm_pers = npz['hmm_persistence']
    hmm_nc = npz['hmm_non_contiguous']
    hmm_k = npz['hmm_k']

    n = qa.shape[0]
    print(f"  {n} cycles loaded")

    rng = np.random.default_rng(42)
    results = {}

    print("\nScoring H1: Three-Phase Operator Scheduling...")
    results['H1'] = score_h1(qa, rng, predictions)
    h1 = results['H1']
    print(f"  Voynich JSD: {h1['voynich_jsd']:.4f}")
    print(f"  Position JSD: {h1['position_jsd']:.4f}")
    print(f"  Beats position: {h1['voynich_beats_position']}")
    print(f"  Q1 peak: {h1['q1_peak']} (actual: Q{h1['q1_peak_quintile']})")
    print(f"  Closure ratio: {h1['closure_ratio']:.2f}")

    print("\nScoring H2: Supervisory Decomposition...")
    results['H2'] = score_h2(hmm_il, hmm_pers, hmm_nc, hmm_k, summary, predictions, rng)
    h2 = results['H2']
    print(f"  N HMM cycles: {h2.get('n_hmm_cycles', 0)}")
    print(f"  NC fraction: {h2.get('nc_fraction', 'N/A')}")
    print(f"  Persistence: {h2.get('mean_persistence', 'N/A')}")

    print("\nScoring H3: Dual Feedback Channels...")
    results['H3'] = score_h3(meta, bg, predictions, rng)
    h3 = results['H3']
    print(f"  Passive pos: {h3.get('passive_mean_pos', '?'):.4f}")
    print(f"  Active pos: {h3.get('active_mean_pos', '?'):.4f}")
    print(f"  Delta: {h3.get('delta', '?'):.4f}")
    print(f"  Split advantage: {h3.get('split_advantage', '?'):.4f}")

    print("\nScoring H4: Preventive Stabilization...")
    results['H4'] = score_h4(qa, counts, pos, params, predictions, rng)
    h4 = results['H4']
    print(f"  DB fraction: {h4['db_frac']:.4f}")
    print(f"  Mean position: {h4['mean_position']:.4f}")
    print(f"  Context independent: {h4['context_independent']}")
    print(f"  Q4 depleted: {h4['q4_depleted']}")

    print("\nScoring H5: Instruction-Profile Locality...")
    results['H5'] = score_h5(qa, counts, params, predictions, rng)
    h5 = results['H5']
    print(f"  Raw lag-1: {h5['raw_lag1']:.4f}")
    print(f"  Shuffle p: {h5['shuffle_p']:.4f}")
    print(f"  Compensatory ratio: {h5['compensatory_ratio']:.4f}")

    print("\nScoring H6: Hazard Immunity...")
    results['H6'] = score_h6(qa, bg, qr_stab, qr_pa, predictions, rng)
    h6 = results['H6']
    print(f"  IB->DA rate: {h6['mean_ib_to_da']:.4f}")
    print(f"  CHECK->DA rate: {h6['mean_check_to_da']:.4f}")
    print(f"  DA ratio: {h6['da_ratio']:.2f}")
    print(f"  Stability enriched: {h6['stability_enriched']}")

    print("\nScoring per apparatus family...")
    results['apparatus'] = score_per_apparatus(qa, params, summary, predictions, rng)
    for fname, fres in results['apparatus'].items():
        print(f"  {fname}: n={fres.get('n_cycles', 0)}, beats_pos={fres.get('h1_beats_position', 'N/A')}")

    # Summary
    print(f"\n{'='*60}")
    print("T3 SCORING SUMMARY")
    print(f"{'='*60}")
    for h in ['H1', 'H2', 'H3', 'H4', 'H5', 'H6']:
        r = results[h]
        sig = r.get('significant', r.get('voynich_beats_position', False))
        print(f"  {h}: {'PASS' if sig else 'FAIL'}")

    out_path = RESULTS_DIR / 't3_scoring_engine.json'
    print(f"\nWriting: {out_path}")
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Size: {out_path.stat().st_size / 1e3:.1f} KB")


if __name__ == '__main__':
    main()
