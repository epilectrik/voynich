"""
Phase 439: EXTRACTION_CYCLING_VALIDATION
Test whether the two alternating suffix modes (C1229) correspond to
functionally distinct operational phases: energy-specification (Mode A)
vs extraction-execution (Mode B), reflected in PREFIX and MIDDLE composition.

Tests:
  T1: PREFIX domain by suffix mode (DECISIVE)
  T2: Lane alignment check (CALIBRATION)
  T3: MIDDLE content by suffix mode
  T4: PREFIX migration through paragraph
  T5: FL reset x mode transition alignment
  T6: Mode universality (FALSIFICATION)
  T7: Paragraph tail signatures
  T8: Section generalization
"""

import json, sys, math
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as sp_stats

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

# -- Constants --------------------------------------------------------

ALPHA_BONFERRONI = 0.05 / 8  # 0.00625
MIN_BODY_CLUSTER = 7   # 8+ body lines for mode assignment
MIN_BODY_MIGRATION = 5  # 6+ body lines for PREFIX migration

TERMINAL_SUFFIXES = {'y', 'dy', 'am', 'edy', 'ey', 'ly', 'ry', 'hy', 'eey', 'om', 'im'}
CONNECTOR_SUFFIXES = {'in', 'r', 'l', 's', 'an', 'en', 'on'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'iin', 'oiin'}

FL_STATES = {
    'EARLY': {'i', 'ii', 'in'},
    'MEDIAL': {'r', 'ar', 'al', 'l', 'ol'},
    'LATE': {'o', 'ly', 'am', 'm', 'dy', 'ry', 'y'},
}
STATE_ORDER = {'EARLY': 0, 'MEDIAL': 1, 'LATE': 2}

# PREFIX domain families (from F-BRU-026 and structural contracts)
ENERGY_PREFIX = {'qo'}
VESSEL_PREFIX = {'ok', 'ot', 'ol'}
PROCESS_PREFIX = {'ch', 'sh', 'sch'}

# MIDDLE families
K_FAMILY_MIDDLES = {'k', 'ke', 'kch', 'ksh', 'ek'}
E_FAMILY_MIDDLES = {'e', 'ey', 'edy', 'eey', 'eok'}
PREP_FAMILY_MIDDLES = {'tch', 'pch', 'lch', 'dch', 'te', 'ksh'}


# -- Statistics -------------------------------------------------------

def rd(x, d=4):
    if isinstance(x, float):
        return round(x, d)
    if isinstance(x, dict):
        return {k: rd(v, d) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rd(v, d) for v in x]
    if isinstance(x, np.floating):
        return round(float(x), d)
    if isinstance(x, np.integer):
        return int(x)
    return x


def compute_jsd(p, q, epsilon=1e-10):
    p = np.array(p, dtype=float) + epsilon
    q = np.array(q, dtype=float) + epsilon
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log2(p / m)) + 0.5 * np.sum(q * np.log2(q / m)))


def get_fl_stage(middle):
    for stage, middles in FL_STATES.items():
        if middle in middles:
            return stage
    return None


# -- Suffix / PREFIX / MIDDLE helpers ---------------------------------

def classify_suffix(suffix):
    if not suffix:
        return 'BARE'
    if suffix in TERMINAL_SUFFIXES:
        return 'TERMINAL'
    if suffix in CONNECTOR_SUFFIXES:
        return 'CONNECTOR'
    if suffix in ITERATE_SUFFIXES:
        return 'ITERATE'
    return 'BARE'


def suffix_profile(suffixes):
    if not suffixes:
        return {'terminal': 0, 'connector': 0, 'iterate': 0, 'bare': 1.0}
    cats = [classify_suffix(s) for s in suffixes]
    n = len(cats)
    return {
        'terminal': sum(1 for c in cats if c == 'TERMINAL') / n,
        'connector': sum(1 for c in cats if c == 'CONNECTOR') / n,
        'iterate': sum(1 for c in cats if c == 'ITERATE') / n,
        'bare': sum(1 for c in cats if c == 'BARE') / n,
    }


def suffix_vec(profile):
    return [profile['terminal'], profile['connector'], profile['iterate'], profile['bare']]


def prefix_domain(prefix):
    """Classify a prefix into domain family."""
    if not prefix:
        return 'NONE'
    if prefix in ENERGY_PREFIX:
        return 'ENERGY'
    if prefix in VESSEL_PREFIX:
        return 'VESSEL'
    if prefix in PROCESS_PREFIX:
        return 'PROCESS'
    return 'OTHER'


def prefix_profile(prefixes):
    """Compute PREFIX domain fractions from a list of prefixes."""
    if not prefixes:
        return {'energy': 0, 'vessel': 0, 'process': 0, 'other': 0, 'none': 0}
    domains = [prefix_domain(p) for p in prefixes]
    n = len(domains)
    return {
        'energy': sum(1 for d in domains if d == 'ENERGY') / n,
        'vessel': sum(1 for d in domains if d == 'VESSEL') / n,
        'process': sum(1 for d in domains if d == 'PROCESS') / n,
        'other': sum(1 for d in domains if d == 'OTHER') / n,
        'none': sum(1 for d in domains if d == 'NONE') / n,
    }


def middle_families(middles):
    """Compute MIDDLE family fractions from a list of middles."""
    if not middles:
        return {'k_family': 0, 'e_family': 0, 'prep_family': 0, 'other': 0}
    n = len(middles)
    return {
        'k_family': sum(1 for m in middles if m in K_FAMILY_MIDDLES) / n,
        'e_family': sum(1 for m in middles if m in E_FAMILY_MIDDLES) / n,
        'prep_family': sum(1 for m in middles if m in PREP_FAMILY_MIDDLES) / n,
        'other': sum(1 for m in middles
                     if m not in K_FAMILY_MIDDLES
                     and m not in E_FAMILY_MIDDLES
                     and m not in PREP_FAMILY_MIDDLES) / n,
    }


# -- Data Loading -----------------------------------------------------

def load_paragraphs():
    """Build paragraph inventory with per-line features."""
    tx = Transcript()
    morph = Morphology()

    line_tokens = defaultdict(list)
    folio_lines = defaultdict(list)
    line_meta = {}

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        if token.placement.startswith('L'):
            continue

        key = (token.folio, token.line)
        m = morph.extract(w)
        fl_stage = get_fl_stage(m.middle) if m.middle else None

        line_tokens[key].append({
            'word': w,
            'middle': m.middle or '',
            'prefix': m.prefix or '',
            'suffix': m.suffix or '',
            'articulator': m.articulator or '',
            'fl_stage': fl_stage,
        })

        if key not in line_meta:
            line_meta[key] = {
                'folio': token.folio,
                'line': token.line,
                'section': token.section,
                'par_initial': False,
                'par_final': False,
            }
            folio_lines[token.folio].append(key)

        if token.par_initial:
            line_meta[key]['par_initial'] = True
        if token.par_final:
            line_meta[key]['par_final'] = True

    # Build paragraphs
    paragraphs = []
    for folio, keys in folio_lines.items():
        current = []
        for key in keys:
            meta = line_meta[key]
            if meta['par_initial'] and current:
                paragraphs.append(current)
                current = []
            current.append(key)
            if meta['par_final']:
                paragraphs.append(current)
                current = []
        if current:
            paragraphs.append(current)

    # Build per-line features
    result = []
    for par_idx, line_keys in enumerate(paragraphs):
        if len(line_keys) < 2:
            continue

        folio = line_meta[line_keys[0]]['folio']
        section = line_meta[line_keys[0]]['section']

        line_records = []
        for lk in line_keys:
            tokens = line_tokens[lk]
            if not tokens:
                continue

            suffixes = [t['suffix'] for t in tokens]
            prefixes = [t['prefix'] for t in tokens]
            middles = [t['middle'] for t in tokens]
            profile = suffix_profile(suffixes)
            prf_profile = prefix_profile(prefixes)
            mid_profile = middle_families(middles)

            fl_stages = [t['fl_stage'] for t in tokens if t['fl_stage'] is not None]
            first_fl = fl_stages[0] if fl_stages else None
            last_fl = fl_stages[-1] if fl_stages else None

            qo_count = sum(1 for t in tokens if t['prefix'] in ENERGY_PREFIX)

            line_records.append({
                'key': lk,
                'n_tokens': len(tokens),
                'suffixes': suffixes,
                'prefixes': prefixes,
                'middles': middles,
                'suffix_profile': profile,
                'prefix_profile': prf_profile,
                'middle_profile': mid_profile,
                'first_fl': first_fl,
                'last_fl': last_fl,
                'qo_frac': qo_count / len(tokens) if tokens else 0,
            })

        if len(line_records) < 2:
            continue

        body = line_records[1:]
        result.append({
            'par_id': f'{folio}_p{par_idx}',
            'folio': folio,
            'section': section,
            'header': line_records[0],
            'body': body,
            'n_body': len(body),
        })

    return result


def assign_modes(paragraphs, min_body=MIN_BODY_CLUSTER):
    """Assign each body line to Mode A or B using k=2 clustering on suffix profiles.
    Mode A = the cluster with higher terminal fraction (specification mode).
    Mode B = the cluster with higher bare fraction (execution mode).
    Returns paragraphs augmented with mode labels."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    for p in paragraphs:
        p['mode_assigned'] = False
        if p['n_body'] < min_body:
            continue

        body = p['body']
        profiles = np.array([suffix_vec(ln['suffix_profile']) for ln in body])

        if len(profiles) < 4:
            continue

        km = KMeans(n_clusters=2, n_init=10, random_state=42).fit(profiles)
        labels = km.labels_
        sil = silhouette_score(profiles, labels) if len(set(labels)) > 1 else -1

        if sil < 0.3:
            continue

        # Identify which cluster is Mode A (higher terminal)
        c0_term = np.mean([profiles[i][0] for i in range(len(labels)) if labels[i] == 0])
        c1_term = np.mean([profiles[i][0] for i in range(len(labels)) if labels[i] == 1])

        if c0_term >= c1_term:
            mode_map = {0: 'A', 1: 'B'}
        else:
            mode_map = {0: 'B', 1: 'A'}

        for i, ln in enumerate(body):
            ln['mode'] = mode_map[labels[i]]

        p['mode_assigned'] = True
        p['silhouette'] = sil
        p['centroids'] = {
            'A': km.cluster_centers_[0 if c0_term >= c1_term else 1].tolist(),
            'B': km.cluster_centers_[1 if c0_term >= c1_term else 0].tolist(),
        }

    return paragraphs


# -- T1: PREFIX Domain by Suffix Mode (DECISIVE) ---------------------

def test_1_prefix_by_mode(paragraphs):
    """Compare PREFIX domain composition between Mode A and Mode B lines."""
    assigned = [p for p in paragraphs if p.get('mode_assigned')]
    print(f"  T1: {len(assigned)} paragraphs with mode assignments")

    mode_a_prefixes = {'energy': [], 'vessel': [], 'process': [], 'other': [], 'none': []}
    mode_b_prefixes = {'energy': [], 'vessel': [], 'process': [], 'other': [], 'none': []}

    for p in assigned:
        for ln in p['body']:
            mode = ln.get('mode')
            if not mode:
                continue
            pp = ln['prefix_profile']
            target = mode_a_prefixes if mode == 'A' else mode_b_prefixes
            for domain in target:
                target[domain].append(pp[domain])

    n_a = len(mode_a_prefixes['energy'])
    n_b = len(mode_b_prefixes['energy'])
    print(f"    Mode A lines: {n_a}, Mode B lines: {n_b}")

    results = {}
    for domain in ['energy', 'vessel', 'process', 'other', 'none']:
        a_vals = mode_a_prefixes[domain]
        b_vals = mode_b_prefixes[domain]
        a_mean = float(np.mean(a_vals)) if a_vals else 0
        b_mean = float(np.mean(b_vals)) if b_vals else 0
        ratio = a_mean / b_mean if b_mean > 0 else float('inf')

        if len(a_vals) > 5 and len(b_vals) > 5:
            stat, p_val = sp_stats.mannwhitneyu(a_vals, b_vals, alternative='two-sided')
        else:
            stat, p_val = 0, 1.0

        results[domain] = {
            'mode_a_mean': a_mean,
            'mode_b_mean': b_mean,
            'a_over_b_ratio': ratio,
            'mann_whitney_p': float(p_val),
        }
        print(f"    {domain:8s}: A={a_mean:.4f} B={b_mean:.4f} ratio={ratio:.3f} p={p_val:.6f}")

    # Check pre-registered predictions
    energy_ratio = results['energy']['a_over_b_ratio']
    vessel_process_a = results['vessel']['mode_a_mean'] + results['process']['mode_a_mean']
    vessel_process_b = results['vessel']['mode_b_mean'] + results['process']['mode_b_mean']
    vp_ratio = vessel_process_b / vessel_process_a if vessel_process_a > 0 else float('inf')

    energy_pass = (energy_ratio > 1.5 and results['energy']['mann_whitney_p'] < 0.005)
    vp_pass = (vp_ratio > 1.3 and
               (results['vessel']['mann_whitney_p'] < 0.005 or
                results['process']['mann_whitney_p'] < 0.005))

    if energy_pass and vp_pass:
        verdict = 'PREFIX_MODE_DIFFERENTIATION_CONFIRMED'
    elif energy_pass or vp_pass:
        verdict = 'PREFIX_MODE_PARTIAL'
    else:
        verdict = 'PREFIX_MODE_INDEPENDENT'

    print(f"    Energy A/B ratio: {energy_ratio:.3f} (pred >1.5)")
    print(f"    Vessel+Process B/A ratio: {vp_ratio:.3f} (pred >1.3)")
    print(f"    Verdict: {verdict}")

    return rd({
        'n_mode_a': n_a,
        'n_mode_b': n_b,
        'per_domain': results,
        'energy_a_over_b': energy_ratio,
        'vessel_process_b_over_a': vp_ratio,
        'energy_pass': energy_pass,
        'vp_pass': vp_pass,
        'verdict': verdict,
    })


# -- T2: Lane Alignment Check (CALIBRATION) --------------------------

def test_2_lane_alignment(paragraphs):
    """Check if suffix modes are rediscovering QO/CHSH lane oscillation."""
    assigned = [p for p in paragraphs if p.get('mode_assigned')]
    print(f"  T2: {len(assigned)} paragraphs with mode assignments")

    # Collect per-line QO fraction and mode
    qo_fracs = []
    modes = []  # 1 for A, 0 for B
    within_corrs = []

    for p in assigned:
        p_qo = []
        p_mode = []
        for ln in p['body']:
            if 'mode' not in ln:
                continue
            qo_fracs.append(ln['qo_frac'])
            modes.append(1 if ln['mode'] == 'A' else 0)
            p_qo.append(ln['qo_frac'])
            p_mode.append(1 if ln['mode'] == 'A' else 0)

        if len(p_qo) >= 4 and len(set(p_mode)) > 1:
            r, _ = sp_stats.pointbiserialr(p_mode, p_qo)
            within_corrs.append(r)

    # Global point-biserial
    if len(qo_fracs) > 10 and len(set(modes)) > 1:
        r_global, p_global = sp_stats.pointbiserialr(modes, qo_fracs)
    else:
        r_global, p_global = 0, 1.0

    mean_within = float(np.mean(within_corrs)) if within_corrs else 0

    if abs(r_global) > 0.5:
        interpretation = 'LANE_EXPRESSED'
    elif abs(r_global) > 0.2:
        interpretation = 'PARTIALLY_LANE_EXPRESSED'
    else:
        interpretation = 'INDEPENDENT_OF_LANE'

    print(f"    Global r: {r_global:.4f}, p: {p_global:.6f}")
    print(f"    Mean within-paragraph r: {mean_within:.4f} (n={len(within_corrs)})")
    print(f"    Interpretation: {interpretation}")

    return rd({
        'n_lines': len(qo_fracs),
        'global_r': float(r_global),
        'global_p': float(p_global),
        'mean_within_r': mean_within,
        'n_within_paragraphs': len(within_corrs),
        'interpretation': interpretation,
    })


# -- T3: MIDDLE Content by Suffix Mode --------------------------------

def test_3_middle_by_mode(paragraphs):
    """Compare MIDDLE family composition between Mode A and Mode B lines."""
    assigned = [p for p in paragraphs if p.get('mode_assigned')]
    print(f"  T3: {len(assigned)} paragraphs with mode assignments")

    mode_a_middles = {'k_family': [], 'e_family': [], 'prep_family': [], 'other': []}
    mode_b_middles = {'k_family': [], 'e_family': [], 'prep_family': [], 'other': []}

    for p in assigned:
        for ln in p['body']:
            if 'mode' not in ln:
                continue
            mp = ln['middle_profile']
            target = mode_a_middles if ln['mode'] == 'A' else mode_b_middles
            for fam in target:
                target[fam].append(mp[fam])

    n_a = len(mode_a_middles['k_family'])
    n_b = len(mode_b_middles['k_family'])
    print(f"    Mode A lines: {n_a}, Mode B lines: {n_b}")

    results = {}
    for fam in ['k_family', 'e_family', 'prep_family', 'other']:
        a_vals = mode_a_middles[fam]
        b_vals = mode_b_middles[fam]
        a_mean = float(np.mean(a_vals)) if a_vals else 0
        b_mean = float(np.mean(b_vals)) if b_vals else 0
        ratio = a_mean / b_mean if b_mean > 0 else float('inf')

        if len(a_vals) > 5 and len(b_vals) > 5:
            stat, p_val = sp_stats.mannwhitneyu(a_vals, b_vals, alternative='two-sided')
        else:
            stat, p_val = 0, 1.0

        results[fam] = {
            'mode_a_mean': a_mean,
            'mode_b_mean': b_mean,
            'a_over_b_ratio': ratio,
            'mann_whitney_p': float(p_val),
        }
        print(f"    {fam:12s}: A={a_mean:.4f} B={b_mean:.4f} ratio={ratio:.3f} p={p_val:.6f}")

    k_enriched_a = (results['k_family']['a_over_b_ratio'] > 1.0 and
                    results['k_family']['mann_whitney_p'] < 0.005)
    e_enriched_b = (results['e_family']['a_over_b_ratio'] < 1.0 and
                    results['e_family']['mann_whitney_p'] < 0.005)

    if k_enriched_a and e_enriched_b:
        verdict = 'MIDDLE_MODE_DIFFERENTIATION_CONFIRMED'
    elif k_enriched_a or e_enriched_b:
        verdict = 'MIDDLE_MODE_PARTIAL'
    else:
        verdict = 'MIDDLE_MODE_INDEPENDENT'

    print(f"    Verdict: {verdict}")

    return rd({
        'n_mode_a': n_a,
        'n_mode_b': n_b,
        'per_family': results,
        'k_enriched_in_a': k_enriched_a,
        'e_enriched_in_b': e_enriched_b,
        'verdict': verdict,
    })


# -- T4: PREFIX Migration Through Paragraph ---------------------------

def test_4_prefix_migration(paragraphs):
    """Test directional PREFIX shift through body positions."""
    qualifying = [p for p in paragraphs if p['n_body'] >= MIN_BODY_MIGRATION]
    print(f"  T4: {len(qualifying)} paragraphs with {MIN_BODY_MIGRATION}+ body lines")

    domains = ['energy', 'vessel', 'process']
    all_rhos = {d: [] for d in domains}

    for p in qualifying:
        body = p['body']
        n = len(body)
        positions = np.arange(n, dtype=float) / (n - 1) if n > 1 else np.array([0.5])

        for domain in domains:
            values = [ln['prefix_profile'][domain] for ln in body]
            if len(set(values)) < 2:
                continue
            rho, _ = sp_stats.spearmanr(positions, values)
            if not np.isnan(rho):
                all_rhos[domain].append(rho)

    results = {}
    for domain in domains:
        rhos = all_rhos[domain]
        if len(rhos) < 10:
            results[domain] = {'n': len(rhos), 'verdict': 'INSUFFICIENT_DATA'}
            continue

        mean_rho = float(np.mean(rhos))
        # One-sample t-test: is mean rho significantly different from 0?
        t_stat, t_p = sp_stats.ttest_1samp(rhos, 0)
        # Also: what fraction have the predicted sign?
        if domain == 'energy':
            predicted_sign = -1  # decreasing
            frac_correct = sum(1 for r in rhos if r < 0) / len(rhos)
        else:
            predicted_sign = 1   # increasing
            frac_correct = sum(1 for r in rhos if r > 0) / len(rhos)

        results[domain] = {
            'n': len(rhos),
            'mean_rho': mean_rho,
            't_stat': float(t_stat),
            't_p': float(t_p),
            'frac_predicted_sign': frac_correct,
        }
        print(f"    {domain:8s}: mean rho={mean_rho:.4f}, t_p={t_p:.6f}, {frac_correct:.1%} predicted sign")

    # Check pre-registered prediction: energy negative AND vessel/process positive
    e_pass = (results.get('energy', {}).get('mean_rho', 0) < 0 and
              results.get('energy', {}).get('t_p', 1) < 0.005)
    v_pass = (results.get('vessel', {}).get('mean_rho', 0) > 0 and
              results.get('vessel', {}).get('t_p', 1) < 0.005)
    p_pass = (results.get('process', {}).get('mean_rho', 0) > 0 and
              results.get('process', {}).get('t_p', 1) < 0.005)

    if e_pass and (v_pass or p_pass):
        verdict = 'PREFIX_MIGRATION_CONFIRMED'
    elif e_pass or v_pass or p_pass:
        verdict = 'PREFIX_MIGRATION_PARTIAL'
    else:
        verdict = 'PREFIX_MIGRATION_NULL'

    print(f"    Verdict: {verdict}")

    return rd({
        'n_qualifying': len(qualifying),
        'per_domain': results,
        'energy_declining': e_pass,
        'vessel_rising': v_pass,
        'process_rising': p_pass,
        'verdict': verdict,
    })


# -- T5: FL Reset x Mode Transition Alignment -------------------------

def test_5_fl_mode_alignment(paragraphs):
    """Test whether FL regressions coincide with suffix mode switches."""
    assigned = [p for p in paragraphs if p.get('mode_assigned')]
    print(f"  T5: {len(assigned)} paragraphs with mode assignments")

    # 2x2: {regression, no_regression} x {mode_switch, same_mode}
    regression_switch = 0
    regression_same = 0
    no_regr_switch = 0
    no_regr_same = 0
    no_fl_pairs = 0

    for p in assigned:
        body = p['body']
        for i in range(len(body) - 1):
            ln1 = body[i]
            ln2 = body[i + 1]
            if 'mode' not in ln1 or 'mode' not in ln2:
                continue

            mode_switch = (ln1['mode'] != ln2['mode'])

            # FL regression: last FL of ln1 vs first FL of ln2
            fl1 = ln1['last_fl']
            fl2 = ln2['first_fl']

            if fl1 is None or fl2 is None:
                no_fl_pairs += 1
                continue

            regression = (STATE_ORDER.get(fl2, 0) < STATE_ORDER.get(fl1, 0))

            if regression and mode_switch:
                regression_switch += 1
            elif regression and not mode_switch:
                regression_same += 1
            elif not regression and mode_switch:
                no_regr_switch += 1
            else:
                no_regr_same += 1

    total = regression_switch + regression_same + no_regr_switch + no_regr_same
    print(f"    Total pairs: {total}, no-FL pairs: {no_fl_pairs}")
    print(f"    2x2: regr+switch={regression_switch}, regr+same={regression_same}, "
          f"no_regr+switch={no_regr_switch}, no_regr+same={no_regr_same}")

    if total < 20:
        return rd({'total_pairs': total, 'verdict': 'INSUFFICIENT_DATA'})

    # Fisher's exact test
    table = [[regression_switch, regression_same],
             [no_regr_switch, no_regr_same]]
    odds_ratio, p_val = sp_stats.fisher_exact(table)

    # Proportions
    regr_total = regression_switch + regression_same
    regr_switch_rate = regression_switch / regr_total if regr_total > 0 else 0
    no_regr_total = no_regr_switch + no_regr_same
    no_regr_switch_rate = no_regr_switch / no_regr_total if no_regr_total > 0 else 0

    if odds_ratio > 1.5 and p_val < 0.01:
        verdict = 'FL_MODE_ALIGNED'
    elif odds_ratio > 1.0 and p_val < 0.05:
        verdict = 'FL_MODE_WEAK_ALIGNMENT'
    else:
        verdict = 'FL_MODE_INDEPENDENT'

    print(f"    Regression switch rate: {regr_switch_rate:.3f}")
    print(f"    Non-regression switch rate: {no_regr_switch_rate:.3f}")
    print(f"    OR={odds_ratio:.3f}, p={p_val:.6f}")
    print(f"    Verdict: {verdict}")

    return rd({
        'total_pairs': total,
        'no_fl_pairs': no_fl_pairs,
        'contingency': {
            'regression_switch': regression_switch,
            'regression_same': regression_same,
            'no_regression_switch': no_regr_switch,
            'no_regression_same': no_regr_same,
        },
        'regression_switch_rate': regr_switch_rate,
        'no_regression_switch_rate': no_regr_switch_rate,
        'odds_ratio': float(odds_ratio),
        'fisher_p': float(p_val),
        'verdict': verdict,
    })


# -- T6: Mode Universality (FALSIFICATION) ----------------------------

def test_6_mode_universality(paragraphs):
    """Test whether suffix modes converge on universal centroids across paragraphs."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    assigned = [p for p in paragraphs if p.get('mode_assigned')]
    print(f"  T6: {len(assigned)} paragraphs with mode assignments")

    # Collect all Mode A and Mode B centroids per paragraph
    a_centroids = []
    b_centroids = []
    for p in assigned:
        if 'centroids' in p:
            a_centroids.append(p['centroids']['A'])
            b_centroids.append(p['centroids']['B'])

    print(f"    Mode A centroids: {len(a_centroids)}, Mode B centroids: {len(b_centroids)}")

    if len(a_centroids) < 10:
        return rd({'n_paragraphs': len(a_centroids), 'verdict': 'INSUFFICIENT_DATA'})

    # Within-mode variance vs between-mode variance
    a_arr = np.array(a_centroids)
    b_arr = np.array(b_centroids)

    within_a = float(np.mean(np.var(a_arr, axis=0)))
    within_b = float(np.mean(np.var(b_arr, axis=0)))
    within_mean = (within_a + within_b) / 2

    # Between-mode: variance of the distance between A and B centroids
    all_centroids = np.vstack([a_arr, b_arr])
    labels = np.array([0] * len(a_arr) + [1] * len(b_arr))

    # Global centroid means
    global_a_centroid = np.mean(a_arr, axis=0)
    global_b_centroid = np.mean(b_arr, axis=0)
    between_var = float(np.mean((global_a_centroid - global_b_centroid) ** 2))

    f_stat = between_var / within_mean if within_mean > 0 else 0

    # Global silhouette: cluster ALL body lines (not centroids) into k=2
    all_lines = []
    all_labels = []
    for p in assigned:
        for ln in p['body']:
            if 'mode' not in ln:
                continue
            all_lines.append(suffix_vec(ln['suffix_profile']))
            all_labels.append(0 if ln['mode'] == 'A' else 1)

    all_lines = np.array(all_lines)
    all_labels = np.array(all_labels)

    if len(set(all_labels)) > 1 and len(all_lines) > 10:
        global_sil = silhouette_score(all_lines, all_labels)
    else:
        global_sil = -1

    # Also: re-cluster ALL lines globally (ignoring paragraph boundaries)
    km_global = KMeans(n_clusters=2, n_init=10, random_state=42).fit(all_lines)
    refit_sil = silhouette_score(all_lines, km_global.labels_) if len(set(km_global.labels_)) > 1 else -1

    if global_sil > 0.2 and f_stat > 2:
        verdict = 'MODES_UNIVERSAL'
    elif global_sil > 0.1:
        verdict = 'MODES_WEAKLY_UNIVERSAL'
    else:
        verdict = 'MODES_PARAGRAPH_SPECIFIC'

    print(f"    Within-mode variance: {within_mean:.6f}")
    print(f"    Between-mode variance: {between_var:.6f}")
    print(f"    F-statistic: {f_stat:.3f}")
    print(f"    Global silhouette (paragraph labels): {global_sil:.4f}")
    print(f"    Global silhouette (refit k=2): {refit_sil:.4f}")
    print(f"    Global A centroid: [{', '.join(f'{v:.3f}' for v in global_a_centroid)}]")
    print(f"    Global B centroid: [{', '.join(f'{v:.3f}' for v in global_b_centroid)}]")
    print(f"    Verdict: {verdict}")

    return rd({
        'n_paragraphs': len(a_centroids),
        'within_mode_variance': within_mean,
        'between_mode_variance': between_var,
        'f_statistic': f_stat,
        'global_silhouette_paragraph_labels': float(global_sil),
        'global_silhouette_refit': float(refit_sil),
        'global_a_centroid': [float(v) for v in global_a_centroid],
        'global_b_centroid': [float(v) for v in global_b_centroid],
        'n_total_lines': len(all_lines),
        'verdict': verdict,
    })


# -- T7: Paragraph Tail Signatures ------------------------------------

def test_7_tail_signatures(paragraphs):
    """Test whether final body lines cluster into distinct product types."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    qualifying = [p for p in paragraphs if p['n_body'] >= 3]
    print(f"  T7: {len(qualifying)} paragraphs with 3+ body lines")

    # Extract last 2 body lines per paragraph
    tail_features = []
    tail_sections = []
    for p in qualifying:
        body = p['body']
        tail = body[-2:]  # Last 2 lines
        # Combine PREFIX and MIDDLE profiles
        all_prefixes = []
        all_middles = []
        for ln in tail:
            all_prefixes.extend(ln['prefixes'])
            all_middles.extend(ln['middles'])

        pp = prefix_profile(all_prefixes)
        mp = middle_families(all_middles)

        # Feature vector: [energy, vessel, process, k_fam, e_fam, prep_fam]
        feat = [pp['energy'], pp['vessel'], pp['process'],
                mp['k_family'], mp['e_family'], mp['prep_family']]
        tail_features.append(feat)
        tail_sections.append(p['section'])

    tail_arr = np.array(tail_features)
    print(f"    Feature matrix: {tail_arr.shape}")

    if len(tail_arr) < 20:
        return rd({'n': len(tail_arr), 'verdict': 'INSUFFICIENT_DATA'})

    results = {}
    best_k = 1
    best_sil = -1

    for k in [2, 3, 4]:
        if len(tail_arr) < k * 3:
            continue
        km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(tail_arr)
        sil = silhouette_score(tail_arr, km.labels_) if len(set(km.labels_)) > 1 else -1
        results[f'k{k}'] = {
            'silhouette': float(sil),
            'cluster_sizes': [int(np.sum(km.labels_ == i)) for i in range(k)],
        }
        if sil > best_sil:
            best_sil = sil
            best_k = k
        print(f"    k={k}: silhouette={sil:.4f}, sizes={results[f'k{k}']['cluster_sizes']}")

    # For best k, check section correlation
    if best_k > 1 and best_sil > 0:
        km_best = KMeans(n_clusters=best_k, n_init=10, random_state=42).fit(tail_arr)
        # Section x cluster contingency
        sections = sorted(set(tail_sections))
        contingency = np.zeros((len(sections), best_k), dtype=int)
        sec_idx = {s: i for i, s in enumerate(sections)}
        for i, s in enumerate(tail_sections):
            contingency[sec_idx[s], km_best.labels_[i]] += 1

        if contingency.shape[0] >= 2 and contingency.shape[1] >= 2:
            chi2, chi_p, _, _ = sp_stats.chi2_contingency(contingency)
        else:
            chi2, chi_p = 0, 1.0

        # Cluster centroids
        centroids = {}
        for ci in range(best_k):
            mask = km_best.labels_ == ci
            centroid = np.mean(tail_arr[mask], axis=0)
            centroids[f'cluster_{ci}'] = {
                'energy': float(centroid[0]),
                'vessel': float(centroid[1]),
                'process': float(centroid[2]),
                'k_family': float(centroid[3]),
                'e_family': float(centroid[4]),
                'prep_family': float(centroid[5]),
            }

        results['best_k'] = best_k
        results['section_chi2'] = float(chi2)
        results['section_chi_p'] = float(chi_p)
        results['centroids'] = centroids
        print(f"    Section x cluster chi2={chi2:.3f}, p={chi_p:.6f}")

    if best_sil > 0.2:
        verdict = 'TAIL_CLUSTERS_DETECTED'
    elif best_sil > 0.1:
        verdict = 'TAIL_CLUSTERS_WEAK'
    else:
        verdict = 'TAIL_CLUSTERS_NULL'

    results['verdict'] = verdict
    print(f"    Best: k={best_k}, silhouette={best_sil:.4f}")
    print(f"    Verdict: {verdict}")

    return rd(results)


# -- T8: Section Generalization ----------------------------------------

def test_8_section_generalization(paragraphs):
    """Run T1 (PREFIX by mode) separately for each section."""
    sections = ['B', 'H', 'S']  # BIO first, HERBAL last per expert
    section_names = {'B': 'BIO', 'H': 'HERBAL', 'S': 'STARS'}

    results = {}
    all_pass = True

    for sec in sections:
        sec_paras = [p for p in paragraphs if p.get('mode_assigned') and p['section'] == sec]
        n = len(sec_paras)
        print(f"    {section_names[sec]} ({sec}): {n} paragraphs with modes")

        if n < 5:
            results[sec] = {'n': n, 'verdict': 'INSUFFICIENT_DATA'}
            all_pass = False
            continue

        a_energy = []
        b_energy = []
        a_vp = []
        b_vp = []

        for p in sec_paras:
            for ln in p['body']:
                if 'mode' not in ln:
                    continue
                pp = ln['prefix_profile']
                e_val = pp['energy']
                vp_val = pp['vessel'] + pp['process']
                if ln['mode'] == 'A':
                    a_energy.append(e_val)
                    a_vp.append(vp_val)
                else:
                    b_energy.append(e_val)
                    b_vp.append(vp_val)

        if len(a_energy) < 5 or len(b_energy) < 5:
            results[sec] = {'n': n, 'verdict': 'INSUFFICIENT_LINES'}
            all_pass = False
            continue

        a_e_mean = float(np.mean(a_energy))
        b_e_mean = float(np.mean(b_energy))
        e_ratio = a_e_mean / b_e_mean if b_e_mean > 0 else float('inf')
        _, e_p = sp_stats.mannwhitneyu(a_energy, b_energy, alternative='two-sided')

        a_vp_mean = float(np.mean(a_vp))
        b_vp_mean = float(np.mean(b_vp))
        vp_ratio = b_vp_mean / a_vp_mean if a_vp_mean > 0 else float('inf')
        _, vp_p = sp_stats.mannwhitneyu(a_vp, b_vp, alternative='two-sided')

        same_direction = (e_ratio > 1.0 and vp_ratio > 1.0)
        if not same_direction:
            all_pass = False

        results[sec] = {
            'n_paragraphs': n,
            'n_mode_a_lines': len(a_energy),
            'n_mode_b_lines': len(b_energy),
            'energy_a_mean': a_e_mean,
            'energy_b_mean': b_e_mean,
            'energy_ratio': e_ratio,
            'energy_p': float(e_p),
            'vp_a_mean': a_vp_mean,
            'vp_b_mean': b_vp_mean,
            'vp_ratio': vp_ratio,
            'vp_p': float(vp_p),
            'same_direction': same_direction,
        }
        print(f"      Energy A/B={e_ratio:.3f} (p={e_p:.6f}), V+P B/A={vp_ratio:.3f} (p={vp_p:.6f}), same_dir={same_direction}")

    verdict = 'SECTION_INVARIANT' if all_pass else 'SECTION_VARIABLE'
    results['verdict'] = verdict
    print(f"    Verdict: {verdict}")

    return rd(results)


# -- Main --------------------------------------------------------------

def main():
    print("Phase 439: EXTRACTION_CYCLING_VALIDATION")
    print("=" * 60)

    print("\nLoading paragraphs...")
    paragraphs = load_paragraphs()
    total_b = len(paragraphs)
    print(f"  Total B paragraphs: {total_b}")

    # Suffix distribution check
    all_suffixes = []
    for p in paragraphs:
        for ln in p['body']:
            all_suffixes.extend(ln['suffixes'])
    cats = Counter(classify_suffix(s) for s in all_suffixes)
    n_suf = sum(cats.values())
    print(f"  Suffix distribution: " + ", ".join(f"{k}={v/n_suf:.3f}" for k, v in sorted(cats.items())))

    print("\nAssigning modes (k=2 clustering on suffix profiles)...")
    paragraphs = assign_modes(paragraphs)
    n_assigned = sum(1 for p in paragraphs if p.get('mode_assigned'))
    print(f"  Paragraphs with mode assignments (8+ body lines, sil>0.3): {n_assigned}")

    results = {
        'phase': 'EXTRACTION_CYCLING_VALIDATION',
        'total_paragraphs': total_b,
        'n_mode_assigned': n_assigned,
    }

    # T1: PREFIX by suffix mode (DECISIVE)
    print("\n--- T1: PREFIX Domain by Suffix Mode (DECISIVE) ---")
    results['t1_prefix_by_mode'] = test_1_prefix_by_mode(paragraphs)

    # T2: Lane alignment (CALIBRATION)
    print("\n--- T2: Lane Alignment Check (CALIBRATION) ---")
    results['t2_lane_alignment'] = test_2_lane_alignment(paragraphs)

    # T3: MIDDLE content by mode
    print("\n--- T3: MIDDLE Content by Suffix Mode ---")
    results['t3_middle_by_mode'] = test_3_middle_by_mode(paragraphs)

    # T4: PREFIX migration
    print("\n--- T4: PREFIX Migration Through Paragraph ---")
    results['t4_prefix_migration'] = test_4_prefix_migration(paragraphs)

    # T5: FL reset x mode transition
    print("\n--- T5: FL Reset x Mode Transition Alignment ---")
    results['t5_fl_mode_alignment'] = test_5_fl_mode_alignment(paragraphs)

    # T6: Mode universality (FALSIFICATION)
    print("\n--- T6: Mode Universality (FALSIFICATION) ---")
    results['t6_mode_universality'] = test_6_mode_universality(paragraphs)

    # T7: Paragraph tail signatures
    print("\n--- T7: Paragraph Tail Signatures ---")
    results['t7_tail_signatures'] = test_7_tail_signatures(paragraphs)

    # T8: Section generalization
    print("\n--- T8: Section Generalization ---")
    results['t8_section_generalization'] = test_8_section_generalization(paragraphs)

    # Synthesis
    verdicts = {
        't1': results['t1_prefix_by_mode']['verdict'],
        't2': results['t2_lane_alignment']['interpretation'],
        't3': results['t3_middle_by_mode']['verdict'],
        't4': results['t4_prefix_migration']['verdict'],
        't5': results['t5_fl_mode_alignment']['verdict'],
        't6': results['t6_mode_universality']['verdict'],
        't7': results['t7_tail_signatures']['verdict'],
        't8': results['t8_section_generalization']['verdict'],
    }

    t1_pass = 'CONFIRMED' in verdicts['t1']
    t6_pass = 'UNIVERSAL' in verdicts['t6']
    t8_pass = verdicts['t8'] == 'SECTION_INVARIANT'

    if t1_pass and t6_pass:
        overall = 'EXTRACTION_CYCLING_CONFIRMED'
    elif t1_pass and not t6_pass:
        overall = 'PARAGRAPH_SPECIFIC_CYCLING'
    elif not t1_pass:
        overall = 'SUFFIX_MODES_NOT_FUNCTIONAL'
    else:
        overall = 'INCONCLUSIVE'

    if t8_pass:
        overall += '_SECTION_INVARIANT'
    elif verdicts['t8'] != 'SECTION_VARIABLE':
        overall += '_SECTION_UNKNOWN'

    results['synthesis'] = {
        'test_verdicts': verdicts,
        'overall_verdict': overall,
    }

    print(f"\n{'=' * 60}")
    print(f"OVERALL VERDICT: {overall}")
    for k, v in verdicts.items():
        print(f"  {k}: {v}")

    # Save results
    out_dir = Path(__file__).resolve().parent.parent / 'results'
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / 'extraction_cycling_results.json'
    with open(out_path, 'w') as f:
        json.dump(rd(results), f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
