#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T7: Generative Simulation (KEY TEST)

Generates 1,000 synthetic lane sequences per line using the fitted PHMC-CG model
(with actual CC/hazard positions from the data), and compares 8 observed metrics
against the simulated distribution.

Scoring: weighted composite fidelity score (effect-size normalized deviation).

Target: composite deviation < 1.0 and >= 7/8 metrics within 95% CI.

Critical constraint: per-line independence (C670-C673). State resets each line.
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

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
print("T7: Generative Simulation (KEY TEST)")
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
with open(RESULTS_DIR / 't3_cc_routing_gate.json') as f:
    t3 = json.load(f)

# Load regime mapping
with open(PROJECT_ROOT / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json') as f:
    regime_data = json.load(f)
folio_to_regime = {}
for regime, folios in regime_data.items():
    for f_id in folios:
        folio_to_regime[f_id] = regime

# Morphology
tx = Transcript()
morph = Morphology()

# ============================================================
# Model parameter extraction
# ============================================================


def get_section_matrix(section):
    """Get base transition matrix for section."""
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
    """Get hazard gate P(lane) at offset +1."""
    offset_data = t2.get('per_offset', {}).get('1', t2.get('per_offset', {}).get(1, {}))
    chsh_frac = offset_data.get('chsh_fraction', 0.75)
    return max(min(chsh_frac, 0.99), 0.01)  # CHSH probability, clamped


def get_cc_gate(cc_type):
    """Get CC routing gate P(CHSH) at offset +1."""
    cc_data = t3.get('per_cc_type', {}).get(cc_type, {})
    offset1 = cc_data.get('offset_1', {})
    chsh_frac = offset1.get('chsh_fraction', 0.55)
    return max(min(chsh_frac, 0.99), 0.01)


HAZ_GATE_DIST = 2
CC_GATE_DIST = 2
haz_chsh_prob = get_hazard_gate()

# ============================================================
# SECTION 2: Build Line Templates
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

# Build line templates: for each line, record the EN positions and their context
line_templates = []
for (folio, line_num), toks in lines.items():
    en_positions = []
    for i, t in enumerate(toks):
        if t['en_subfamily'] is None:
            continue
        # Nearest preceding hazard
        near_haz = False
        near_cc_type = None
        for j in range(i - 1, max(-1, i - HAZ_GATE_DIST - 1), -1):
            if toks[j]['is_haz']:
                near_haz = True
                break
        for j in range(i - 1, max(-1, i - CC_GATE_DIST - 1), -1):
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
# SECTION 3: Compute Observed Metrics
# ============================================================
print("\nComputing observed metrics...")


def compute_metrics(line_seqs):
    """Compute all 8 metrics from a set of per-line lane sequences.

    line_seqs: list of dicts with 'section', 'folio', 'lanes' (list of 'QO'/'CHSH')
    """
    # 1. Global alternation rate
    total_alt = 0
    total_pairs = 0
    for ls in line_seqs:
        lanes = ls['lanes']
        for i in range(len(lanes) - 1):
            total_pairs += 1
            if lanes[i] != lanes[i + 1]:
                total_alt += 1
    global_alt = total_alt / total_pairs if total_pairs > 0 else 0

    # 2. Per-section alternation rates
    sec_alt = defaultdict(lambda: [0, 0])  # [alternations, pairs]
    for ls in line_seqs:
        lanes = ls['lanes']
        sec = ls['section']
        for i in range(len(lanes) - 1):
            sec_alt[sec][1] += 1
            if lanes[i] != lanes[i + 1]:
                sec_alt[sec][0] += 1
    section_rates = {s: v[0] / v[1] if v[1] > 0 else 0 for s, v in sec_alt.items()}

    # 3. QO run-length mean
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
        # Final run
        if current == 'QO':
            qo_runs.append(run_len)
        else:
            chsh_runs.append(run_len)

    qo_run_mean = np.mean(qo_runs) if qo_runs else 0
    chsh_run_mean = np.mean(chsh_runs) if chsh_runs else 0

    # 4. Post-hazard CHSH rate (from template context)
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

    # 5. Post-CC routing (DAIIN -> CHSH fraction)
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

    # 6. Folio QO fraction distribution
    folio_qo = defaultdict(lambda: [0, 0])
    for ls in line_seqs:
        for lane in ls['lanes']:
            folio_qo[ls['folio']][1] += 1
            if lane == 'QO':
                folio_qo[ls['folio']][0] += 1
    folio_qo_fracs = [v[0] / v[1] for v in folio_qo.values() if v[1] > 0]
    folio_qo_mean = np.mean(folio_qo_fracs) if folio_qo_fracs else 0

    # 7. Within-folio drift (Q1 vs Q4 QO fraction) - simplified
    # Not computed for simulated data (would need quartile info)

    return {
        'global_alternation': float(global_alt),
        'section_rates': {k: float(v) for k, v in section_rates.items()},
        'qo_run_mean': float(qo_run_mean),
        'chsh_run_mean': float(chsh_run_mean),
        'post_haz_chsh_rate': float(post_haz_rate),
        'post_cc_daiin_chsh_rate': float(post_cc_daiin_rate),
        'folio_qo_mean': float(folio_qo_mean),
        'n_pairs': int(total_pairs),
        'n_qo_runs': len(qo_runs),
        'n_chsh_runs': len(chsh_runs),
        'n_post_haz': int(post_haz_total),
        'n_post_cc_daiin': int(post_cc_daiin_total),
    }


# Observed: use actual lane assignments
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
# SECTION 4: Generate Synthetic Sequences
# ============================================================
print(f"\nGenerating {N_SIM} synthetic replications...")

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

        for j, ep in enumerate(lt['en_positions']):
            if j == 0:
                # First EN: use gate or stationary
                if ep['near_haz']:
                    p_chsh = haz_chsh_prob
                elif ep['near_cc_type']:
                    p_chsh = get_cc_gate(ep['near_cc_type'])
                else:
                    p_chsh = stat['CHSH']
                lane = 'CHSH' if rng.random() < p_chsh else 'QO'
            else:
                prev = lanes[-1]
                if ep['near_haz']:
                    p_chsh = haz_chsh_prob
                elif ep['near_cc_type']:
                    p_chsh = get_cc_gate(ep['near_cc_type'])
                else:
                    p_chsh = mat[prev]['CHSH']
                lane = 'CHSH' if rng.random() < p_chsh else 'QO'
            lanes.append(lane)

        sim_seqs.append({
            'folio': lt['folio'],
            'section': lt['section'],
            'lanes': lanes,
            'contexts': lt['en_positions'],
        })

    sim_metrics.append(compute_metrics(sim_seqs))


# ============================================================
# SECTION 5: Compare Observed vs Simulated
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: Fidelity Assessment")
print("=" * 60)

# Extract metric arrays from simulations
metric_names = [
    'global_alternation',
    'qo_run_mean',
    'chsh_run_mean',
    'post_haz_chsh_rate',
    'post_cc_daiin_chsh_rate',
    'folio_qo_mean',
]

# Add section-specific alternation rates for sections with enough data
main_sections = ['B', 'H', 'S']  # BIO, HERBAL, STARS — enough data
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

    # Effect-size normalized deviation
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
    print(f"  {metric:30s}: obs={obs_val:.4f}  sim={sim_mean:.4f}±{sim_sd:.4f}  [{ci_lo:.4f}, {ci_hi:.4f}]  dev={deviation:.2f}  [{status}]")

composite_deviation = total_deviation / n_metrics if n_metrics > 0 else float('inf')

print(f"\n  Metrics within 95% CI: {n_within_ci}/{n_metrics}")
print(f"  Composite deviation: {composite_deviation:.3f}")

# ============================================================
# SECTION 6: Verdict
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: Verdict")
print("=" * 60)

if composite_deviation < 1.0 and n_within_ci >= 7:
    verdict = 'FULL_SUCCESS'
    verdict_text = 'EN oscillation subsystem is generable from first-order state with local contextual overrides'
elif composite_deviation < 2.0 or n_within_ci >= 5:
    verdict = 'PARTIAL_SUCCESS'
    failed_metrics = [m for m, r in fidelity_results.items() if not r['within_ci']]
    verdict_text = f'Major patterns captured. Failed metrics: {failed_metrics}'
else:
    verdict = 'INSUFFICIENT'
    verdict_text = 'Model structurally insufficient — consider HMM or switching-state upgrade'

print(f"  Verdict: {verdict}")
print(f"  {verdict_text}")

# ============================================================
# SECTION 7: Save Results
# ============================================================
results = {
    'test': 'T7_generative_simulation',
    'n_simulations': N_SIM,
    'n_line_templates': len(line_templates),
    'n_en_positions': int(total_en),
    'observed_metrics': observed,
    'fidelity': fidelity_results,
    'summary': {
        'n_metrics': int(n_metrics),
        'n_within_ci': int(n_within_ci),
        'composite_deviation': float(composite_deviation),
    },
    'verdict': verdict,
    'verdict_text': verdict_text,
}

out_path = RESULTS_DIR / 't7_generative_simulation.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved: {out_path}")
