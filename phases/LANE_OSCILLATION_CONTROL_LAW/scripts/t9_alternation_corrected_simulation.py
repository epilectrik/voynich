#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T9: Alternation-Corrected Markov Simulation

Adds a 2-parameter alternation correction to the markov_haz model:
  - epsilon: after a SWITCH, increase P(switch) by epsilon
  - delta: after a STAY, adjust P(switch) by delta

Parameters estimated from T8 second-order transition data.

This is the minimal refinement suggested by expert review to close the
composite deviation gap from T7 (1.43 -> target < 1.2).

Critical constraint: per-line independence (C670-C673). State resets each line.
History resets each line (no cross-line 2nd-order memory).
"""

import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

N_SIM = 1000
rng = np.random.default_rng(42)

# ============================================================
# SECTION 1: Load Data & Model Parameters
# ============================================================
print("=" * 60)
print("T9: Alternation-Corrected Markov Simulation")
print("=" * 60)

# Load class token map
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)
token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
class_to_role[17] = 'CORE_CONTROL'

with open(PROJECT_ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_census = json.load(f)
qo_classes = set(en_census['prefix_families']['QO'])
chsh_classes = set(en_census['prefix_families']['CH_SH'])
all_en_classes = qo_classes | chsh_classes

CC_CLASSES = {10, 11, 12, 17}
HAZ_CLASSES = {7, 30}

# Load model parameters
with open(RESULTS_DIR / 't1_transition_matrices.json') as f:
    t1 = json.load(f)
with open(RESULTS_DIR / 't2_hazard_gate.json') as f:
    t2 = json.load(f)
with open(RESULTS_DIR / 't8_higher_order.json') as f:
    t8 = json.load(f)

# Morphology
tx = Transcript()
morph = Morphology()


# ============================================================
# SECTION 2: Estimate Alternation Correction Parameters
# ============================================================
print("\nEstimating alternation correction from T8 data...")

second = t8['second_order_transitions']
first = t8['first_order_baseline']

# epsilon: post-SWITCH correction to P(switch)
# After QO->CHSH (QC), next P(switch to QO) vs baseline P(QO|CHSH)
eps_qc = second['QC']['P_QO_given_context'] - first['CHSH_to_QO']
# After CHSH->QO (CQ), next P(switch to CHSH) vs baseline P(CHSH|QO)
eps_cq = second['CQ']['P_CHSH_given_context'] - first['QO_to_CHSH']
epsilon = (eps_qc + eps_cq) / 2.0

# delta: post-STAY correction to P(switch)
# After QO->QO (QQ), next P(switch to CHSH) vs baseline P(CHSH|QO)
del_qq = second['QQ']['P_CHSH_given_context'] - first['QO_to_CHSH']
# After CHSH->CHSH (CC), next P(switch to QO) vs baseline P(QO|CHSH)
del_cc = second['CC']['P_QO_given_context'] - first['CHSH_to_QO']
delta = (del_qq + del_cc) / 2.0

print(f"  epsilon (post-SWITCH boost to P(switch)): {epsilon:+.4f}")
print(f"    QC contribution: {eps_qc:+.4f}")
print(f"    CQ contribution: {eps_cq:+.4f}")
print(f"  delta (post-STAY shift to P(switch)): {delta:+.4f}")
print(f"    QQ contribution: {del_qq:+.4f}")
print(f"    CC contribution: {del_cc:+.4f}")


# ============================================================
# SECTION 3: Model Functions
# ============================================================

def get_section_matrix(section):
    """Get base transition matrix for section from T1."""
    sec_data = t1.get('section_matrices', {}).get(section)
    if sec_data:
        return {
            'QO': {'QO': 1.0 - sec_data['QO_to_CHSH'], 'CHSH': sec_data['QO_to_CHSH']},
            'CHSH': {'QO': sec_data['CHSH_to_QO'], 'CHSH': 1.0 - sec_data['CHSH_to_QO']},
        }
    fm = t1['filtered_matrix']
    return {
        'QO': {'QO': fm['QO_to_QO'], 'CHSH': fm['QO_to_CHSH']},
        'CHSH': {'QO': fm['CHSH_to_QO'], 'CHSH': fm['CHSH_to_CHSH']},
    }


def get_stationary(section):
    mat = get_section_matrix(section)
    p_qc = mat['QO']['CHSH']
    p_cq = mat['CHSH']['QO']
    denom = p_qc + p_cq
    if denom == 0:
        return {'QO': 0.5, 'CHSH': 0.5}
    return {'QO': p_cq / denom, 'CHSH': p_qc / denom}


def get_hazard_gate():
    """Get hazard gate P(CHSH) at offset +1."""
    offset_data = t2.get('per_offset', {}).get('1', t2.get('per_offset', {}).get(1, {}))
    chsh_frac = offset_data.get('chsh_fraction', 0.75)
    return max(min(chsh_frac, 0.99), 0.01)


HAZ_GATE_DIST = 2
haz_chsh_prob = get_hazard_gate()
print(f"\n  Hazard gate P(CHSH): {haz_chsh_prob:.4f}")


# ============================================================
# SECTION 4: Build Line Templates
# ============================================================
print("\nBuilding line templates...")

lines = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    cls = token_to_class.get(w)
    m = morph.extract(w)

    en_subfamily = None
    if cls is not None and cls in all_en_classes:
        if m.prefix == 'qo':
            en_subfamily = 'QO'
        elif m.prefix in ('ch', 'sh'):
            en_subfamily = 'CHSH'

    is_cc = cls in CC_CLASSES if cls is not None else False
    is_haz = cls in HAZ_CLASSES if cls is not None else False
    cc_type = None
    if is_cc:
        if w == 'daiin':
            cc_type = 'DAIIN'
        elif w == 'ol':
            cc_type = 'OL'
        elif cls == 17:
            cc_type = 'OL_DERIVED'
        else:
            cc_type = 'OTHER_CC'

    lines[(token.folio, token.line)].append({
        'en_subfamily': en_subfamily,
        'is_haz': is_haz,
        'is_cc': is_cc,
        'cc_type': cc_type,
        'section': token.section,
        'folio': token.folio,
    })

line_templates = []
for (folio, line_num), toks in lines.items():
    en_positions = []
    for i, t in enumerate(toks):
        if t['en_subfamily'] is None:
            continue
        near_haz = False
        near_cc_type = None
        for j in range(i - 1, max(-1, i - HAZ_GATE_DIST - 1), -1):
            if toks[j]['is_haz']:
                near_haz = True
                break
        for j in range(i - 1, max(-1, i - HAZ_GATE_DIST - 1), -1):
            if toks[j]['is_cc']:
                near_cc_type = toks[j]['cc_type']
                break

        en_positions.append({
            'observed_lane': t['en_subfamily'],
            'near_haz': near_haz,
            'near_cc_type': near_cc_type,
        })

    if len(en_positions) >= 2:
        line_templates.append({
            'folio': folio,
            'section': toks[0]['section'],
            'en_positions': en_positions,
        })

print(f"Line templates: {len(line_templates)}")
total_en = sum(len(lt['en_positions']) for lt in line_templates)
print(f"Total EN positions: {total_en}")


# ============================================================
# SECTION 5: Compute Observed Metrics
# ============================================================
print("\nComputing observed metrics...")


def compute_metrics(line_seqs):
    """Compute fidelity metrics from per-line lane sequences."""
    total_alt = 0
    total_pairs = 0
    for ls in line_seqs:
        lanes = ls['lanes']
        for i in range(len(lanes) - 1):
            total_pairs += 1
            if lanes[i] != lanes[i + 1]:
                total_alt += 1
    global_alt = total_alt / total_pairs if total_pairs > 0 else 0

    sec_alt = defaultdict(lambda: [0, 0])
    for ls in line_seqs:
        lanes = ls['lanes']
        sec = ls['section']
        for i in range(len(lanes) - 1):
            sec_alt[sec][1] += 1
            if lanes[i] != lanes[i + 1]:
                sec_alt[sec][0] += 1
    section_rates = {s: v[0] / v[1] if v[1] > 0 else 0 for s, v in sec_alt.items()}

    qo_runs = []
    chsh_runs = []
    for ls in line_seqs:
        lanes = ls['lanes']
        if not lanes:
            continue
        current = lanes[0]
        run_len = 1
        for i in range(1, len(lanes)):
            if lanes[i] == current:
                run_len += 1
            else:
                if current == 'QO':
                    qo_runs.append(run_len)
                else:
                    chsh_runs.append(run_len)
                current = lanes[i]
                run_len = 1
        if current == 'QO':
            qo_runs.append(run_len)
        else:
            chsh_runs.append(run_len)

    qo_run_mean = float(np.mean(qo_runs)) if qo_runs else 0.0
    chsh_run_mean = float(np.mean(chsh_runs)) if chsh_runs else 0.0

    # Post-hazard CHSH rate
    post_haz_chsh = 0
    post_haz_total = 0
    for ls in line_seqs:
        if 'contexts' not in ls:
            continue
        for i, ctx in enumerate(ls['contexts']):
            if ctx.get('near_haz'):
                post_haz_total += 1
                if ls['lanes'][i] == 'CHSH':
                    post_haz_chsh += 1
    post_haz_rate = post_haz_chsh / post_haz_total if post_haz_total > 0 else 0

    # Post-CC DAIIN CHSH rate
    post_cc_daiin_chsh = 0
    post_cc_daiin_total = 0
    for ls in line_seqs:
        if 'contexts' not in ls:
            continue
        for i, ctx in enumerate(ls['contexts']):
            if ctx.get('near_cc_type') == 'DAIIN':
                post_cc_daiin_total += 1
                if ls['lanes'][i] == 'CHSH':
                    post_cc_daiin_chsh += 1
    post_cc_daiin_rate = post_cc_daiin_chsh / post_cc_daiin_total if post_cc_daiin_total > 0 else 0

    # Folio QO mean
    folio_qo = defaultdict(lambda: [0, 0])
    for ls in line_seqs:
        for lane in ls['lanes']:
            folio_qo[ls['folio']][1] += 1
            if lane == 'QO':
                folio_qo[ls['folio']][0] += 1
    folio_qo_fracs = [v[0] / v[1] for v in folio_qo.values() if v[1] > 0]
    folio_qo_mean = float(np.mean(folio_qo_fracs)) if folio_qo_fracs else 0.0

    return {
        'global_alternation': float(global_alt),
        'section_rates': {k: float(v) for k, v in section_rates.items()},
        'qo_run_mean': qo_run_mean,
        'chsh_run_mean': chsh_run_mean,
        'post_haz_chsh_rate': float(post_haz_rate),
        'post_cc_daiin_chsh_rate': float(post_cc_daiin_rate),
        'folio_qo_mean': folio_qo_mean,
        'n_pairs': int(total_pairs),
        'n_qo_runs': len(qo_runs),
        'n_chsh_runs': len(chsh_runs),
        'n_post_haz': int(post_haz_total),
        'n_post_cc_daiin': int(post_cc_daiin_total),
    }


# Observed
observed_seqs = []
for lt in line_templates:
    observed_seqs.append({
        'folio': lt['folio'],
        'section': lt['section'],
        'lanes': [ep['observed_lane'] for ep in lt['en_positions']],
        'contexts': lt['en_positions'],
    })

observed = compute_metrics(observed_seqs)
print(f"Observed metrics:")
print(f"  Global alternation: {observed['global_alternation']:.4f}")
print(f"  QO run mean: {observed['qo_run_mean']:.3f}")
print(f"  CHSH run mean: {observed['chsh_run_mean']:.3f}")
print(f"  Post-hazard CHSH rate: {observed['post_haz_chsh_rate']:.4f}")
print(f"  Post-CC(DAIIN) CHSH rate: {observed['post_cc_daiin_chsh_rate']:.4f}")
print(f"  Folio QO mean: {observed['folio_qo_mean']:.4f}")


# ============================================================
# SECTION 6: Generate Alternation-Corrected Sequences
# ============================================================
print(f"\nGenerating {N_SIM} alternation-corrected replications...")
print(f"  Model: markov_haz + alternation correction (epsilon={epsilon:+.4f}, delta={delta:+.4f})")

sim_metrics = []
for sim_i in range(N_SIM):
    if (sim_i + 1) % 100 == 0:
        print(f"  Simulation {sim_i + 1}/{N_SIM}...")

    sim_seqs = []
    for lt in line_templates:
        section = lt['section']
        mat = get_section_matrix(section)
        stat = get_stationary(section)
        lanes = []
        prev_transition = None  # None, 'SWITCH', 'STAY'

        for j, ep in enumerate(lt['en_positions']):
            if j == 0:
                # First EN: use gate or stationary, no history
                if ep['near_haz']:
                    p_switch = haz_chsh_prob if rng.random() < 0.5 else (1.0 - haz_chsh_prob)
                    # For first token, hazard gate gives P(CHSH) directly
                    p_chsh = haz_chsh_prob
                else:
                    p_chsh = stat['CHSH']
                lane = 'CHSH' if rng.random() < p_chsh else 'QO'
                prev_transition = None  # No transition yet

            elif j == 1:
                # Second EN: base Markov + hazard, no alternation history yet
                prev = lanes[-1]
                if ep['near_haz']:
                    p_chsh = haz_chsh_prob
                else:
                    p_chsh = mat[prev]['CHSH']
                lane = 'CHSH' if rng.random() < p_chsh else 'QO'
                # Record transition type
                prev_transition = 'SWITCH' if lane != prev else 'STAY'

            else:
                # Third EN onward: apply alternation correction
                prev = lanes[-1]

                # Base transition probability
                if ep['near_haz']:
                    p_switch = 1.0 - mat[prev][prev]  # base switch rate
                    p_switch = haz_chsh_prob if prev == 'QO' else (1.0 - haz_chsh_prob)
                else:
                    p_switch = mat[prev]['QO'] if prev == 'CHSH' else mat[prev]['CHSH']

                # Apply alternation correction
                if prev_transition == 'SWITCH':
                    p_switch = p_switch + epsilon
                elif prev_transition == 'STAY':
                    p_switch = p_switch + delta

                # Clamp to valid probability
                p_switch = max(0.01, min(0.99, p_switch))

                # Generate lane
                if rng.random() < p_switch:
                    other = 'QO' if prev == 'CHSH' else 'CHSH'
                    lane = other
                else:
                    lane = prev

                prev_transition = 'SWITCH' if lane != prev else 'STAY'

            lanes.append(lane)

        sim_seqs.append({
            'folio': lt['folio'],
            'section': lt['section'],
            'lanes': lanes,
            'contexts': lt['en_positions'],
        })

    sim_metrics.append(compute_metrics(sim_seqs))


# ============================================================
# SECTION 7: Fidelity Assessment
# ============================================================
print("\n" + "=" * 60)
print("SECTION 7: Fidelity Assessment")
print("=" * 60)

metric_names = [
    'global_alternation',
    'qo_run_mean',
    'chsh_run_mean',
    'post_haz_chsh_rate',
    'post_cc_daiin_chsh_rate',
    'folio_qo_mean',
]
main_sections = ['B', 'H', 'S']
for sec in main_sections:
    metric_names.append(f'section_rate_{sec}')

fidelity_results = {}
n_within_ci = 0
total_deviation = 0.0
n_metrics = 0

for metric in metric_names:
    if metric.startswith('section_rate_'):
        sec = metric.split('_')[-1]
        obs_val = observed['section_rates'].get(sec, 0)
        sim_vals = np.array([sm['section_rates'].get(sec, 0) for sm in sim_metrics])
    else:
        obs_val = observed[metric]
        sim_vals = np.array([sm[metric] for sm in sim_metrics])

    sim_mean = float(np.mean(sim_vals))
    sim_sd = float(np.std(sim_vals))
    ci_lo = float(np.percentile(sim_vals, 2.5))
    ci_hi = float(np.percentile(sim_vals, 97.5))
    within_ci = ci_lo <= obs_val <= ci_hi

    if sim_sd > 0:
        deviation = abs(obs_val - sim_mean) / sim_sd
    else:
        deviation = 0.0 if abs(obs_val - sim_mean) < 1e-10 else float('inf')

    if within_ci:
        n_within_ci += 1
    total_deviation += deviation
    n_metrics += 1

    fidelity_results[metric] = {
        'observed': float(obs_val),
        'simulated_mean': sim_mean,
        'simulated_sd': sim_sd,
        'ci_95': [ci_lo, ci_hi],
        'within_ci': bool(within_ci),
        'deviation': float(deviation),
    }

    status = "PASS" if within_ci else "FAIL"
    print(f"  {metric:30s}: obs={obs_val:.4f}  sim={sim_mean:.4f}+/-{sim_sd:.4f}  [{ci_lo:.4f}, {ci_hi:.4f}]  dev={deviation:.2f}  [{status}]")

composite_deviation = total_deviation / n_metrics if n_metrics > 0 else float('inf')

print(f"\n  Metrics within 95% CI: {n_within_ci}/{n_metrics}")
print(f"  Composite deviation: {composite_deviation:.3f}")

# ============================================================
# SECTION 8: Comparison with T7 (uncorrected model)
# ============================================================
print("\n" + "=" * 60)
print("SECTION 8: Comparison with T7 (uncorrected)")
print("=" * 60)

with open(RESULTS_DIR / 't7_generative_simulation.json') as f:
    t7 = json.load(f)

t7_dev = t7['summary']['composite_deviation']
t7_ci = t7['summary']['n_within_ci']
t7_n = t7['summary']['n_metrics']

print(f"  T7 (first-order):     {t7_ci}/{t7_n} within CI, composite dev = {t7_dev:.3f}")
print(f"  T9 (alt-corrected):   {n_within_ci}/{n_metrics} within CI, composite dev = {composite_deviation:.3f}")
print(f"  Improvement:          dev {t7_dev:.3f} -> {composite_deviation:.3f} (delta = {t7_dev - composite_deviation:+.3f})")

# Per-metric comparison
print(f"\n  Per-metric deviation comparison:")
print(f"  {'Metric':30s}  {'T7 dev':>8s}  {'T9 dev':>8s}  {'Change':>8s}")
print(f"  {'-'*30}  {'-'*8}  {'-'*8}  {'-'*8}")
for metric in metric_names:
    t7_m = t7['fidelity'].get(metric, {})
    t9_m = fidelity_results[metric]
    t7_d = t7_m.get('deviation', float('nan'))
    t9_d = t9_m['deviation']
    change = t7_d - t9_d
    print(f"  {metric:30s}  {t7_d:8.2f}  {t9_d:8.2f}  {change:+8.2f}")

# ============================================================
# SECTION 9: Verdict
# ============================================================
print("\n" + "=" * 60)
print("SECTION 9: Verdict")
print("=" * 60)

qo_run_within = fidelity_results['qo_run_mean']['within_ci']
chsh_run_within = fidelity_results['chsh_run_mean']['within_ci']

checks = {
    'composite_below_1.2': composite_deviation < 1.2,
    'qo_run_fixed': qo_run_within,
    'chsh_run_preserved': chsh_run_within,
    'metrics_7_of_9': n_within_ci >= 7,
    'improvement_over_t7': composite_deviation < t7_dev,
}

for check, passed in checks.items():
    print(f"  {check}: {'PASS' if passed else 'FAIL'}")

n_pass = sum(1 for v in checks.values() if v)
if checks['composite_below_1.2'] and checks['qo_run_fixed'] and checks['improvement_over_t7']:
    verdict = 'STRUCTURAL_CLOSURE'
    verdict_text = ('EN oscillation subsystem is generable from first-order state '
                    'with hazard gate and weak alternation correction. '
                    'No hidden accumulator, no cross-line memory, no regime switching required.')
elif checks['improvement_over_t7']:
    verdict = 'IMPROVED'
    verdict_text = (f'Alternation correction improves model (dev {t7_dev:.3f} -> {composite_deviation:.3f}). '
                    f'Residual deviations remain.')
else:
    verdict = 'NO_IMPROVEMENT'
    verdict_text = 'Alternation correction does not improve generative fidelity.'

print(f"\n  T9 VERDICT: {verdict}")
print(f"  {verdict_text}")
print(f"\n  Model parameters (14 total):")
print(f"    Section matrices: 10 (5 sections x 2 transition probs)")
print(f"    Hazard gate: 2 (P(CHSH), gate distance)")
print(f"    Alternation correction: 2 (epsilon={epsilon:+.4f}, delta={delta:+.4f})")

# ============================================================
# SECTION 10: Save Results
# ============================================================
results = {
    'test': 'T9_alternation_corrected_simulation',
    'model': 'markov_haz_altcorr',
    'n_simulations': N_SIM,
    'n_line_templates': len(line_templates),
    'n_en_positions': int(total_en),
    'correction_parameters': {
        'epsilon': float(epsilon),
        'epsilon_qc': float(eps_qc),
        'epsilon_cq': float(eps_cq),
        'delta': float(delta),
        'delta_qq': float(del_qq),
        'delta_cc': float(del_cc),
        'description': 'epsilon: post-SWITCH boost to P(switch), delta: post-STAY shift to P(switch)',
    },
    'model_params': {
        'section_matrices': 10,
        'hazard_gate': 2,
        'alternation_correction': 2,
        'total': 14,
    },
    'observed_metrics': observed,
    'fidelity': fidelity_results,
    'summary': {
        'n_metrics': int(n_metrics),
        'n_within_ci': int(n_within_ci),
        'composite_deviation': float(composite_deviation),
    },
    'comparison_with_t7': {
        't7_composite_deviation': float(t7_dev),
        't7_within_ci': int(t7_ci),
        't9_composite_deviation': float(composite_deviation),
        't9_within_ci': int(n_within_ci),
        'improvement': float(t7_dev - composite_deviation),
    },
    'checks': {k: bool(v) for k, v in checks.items()},
    'verdict': verdict,
    'verdict_text': verdict_text,
}

out_path = RESULTS_DIR / 't9_alternation_corrected.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved: {out_path}")
