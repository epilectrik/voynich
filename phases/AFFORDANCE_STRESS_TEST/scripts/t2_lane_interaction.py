#!/usr/bin/env python3
"""T2: Lane-Interaction Stress Test per Affordance Bin.

Tests whether bins show distinct lane dynamics:
  - QO/CHSH split per bin
  - Run-length conditioning
  - Lane-switch inertia

Expert predictions:
  - PHASE_SENSITIVE produces longer CHSH runs
  - ENERGY_SPECIALIZED produces longer QO runs
"""

import sys, json, functools
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ── Load data ──────────────────────────────────────────────────────

with open(PROJECT / 'data' / 'middle_affordance_table.json') as f:
    aff = json.load(f)

middle_to_bin = {}
middle_to_qo = {}
bin_labels = {}
for mid, data in aff['middles'].items():
    middle_to_bin[mid] = data['affordance_bin']
    sig = data.get('behavioral_signature', {})
    middle_to_qo[mid] = sig.get('qo_affinity', 0.5)
for b, meta in aff['_metadata']['affordance_bins'].items():
    bin_labels[int(b)] = meta['label']

FUNCTIONAL_BINS = [0, 1, 2, 3, 5, 6, 7, 8, 9]

# Lane thresholds
QO_THRESH = 0.6
CHSH_THRESH = 0.4

def classify_lane(qo_aff):
    if qo_aff > QO_THRESH:
        return 'QO'
    elif qo_aff < CHSH_THRESH:
        return 'CHSH'
    else:
        return 'NEUTRAL'

# ── Build corpus lines ─────────────────────────────────────────────

tx = Transcript()
morph = Morphology()

lines_dict = defaultdict(list)
for token in tx.currier_b():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    mid = m.middle if m.middle else ''
    b = middle_to_bin.get(mid, -1)
    qo = middle_to_qo.get(mid, 0.5)
    lane = classify_lane(qo)
    lines_dict[(token.folio, token.line)].append({
        'word': word,
        'middle': mid,
        'bin': b,
        'qo_affinity': qo,
        'lane': lane,
    })

print("=" * 70)
print("T2: LANE-INTERACTION STRESS TEST PER AFFORDANCE BIN")
print("=" * 70)
print(f"\nCorpus: {len(lines_dict)} lines")

# ── ANALYSIS 1: Per-bin lane distribution ──────────────────────────

print(f"\n{'=' * 70}")
print("PER-BIN LANE DISTRIBUTION")
print("=" * 70)

bin_lane_counts = defaultdict(Counter)  # bin → {QO: n, CHSH: n, NEUTRAL: n}
bin_total = Counter()

for key, tokens in lines_dict.items():
    for tok in tokens:
        b = tok['bin']
        if b == 4 or b == -1:
            continue
        bin_total[b] += 1
        bin_lane_counts[b][tok['lane']] += 1

print(f"\n  {'Bin':>4} {'Label':>25} {'Total':>7} {'QO%':>7} {'CHSH%':>7} {'NEUT%':>7} {'Decisive':>9}")
print(f"  {'-' * 70}")
for b in FUNCTIONAL_BINS:
    label = bin_labels.get(b, '?')
    total = bin_total[b]
    qo_n = bin_lane_counts[b]['QO']
    ch_n = bin_lane_counts[b]['CHSH']
    ne_n = bin_lane_counts[b]['NEUTRAL']
    qo_pct = 100 * qo_n / total if total > 0 else 0
    ch_pct = 100 * ch_n / total if total > 0 else 0
    ne_pct = 100 * ne_n / total if total > 0 else 0
    decisive = max(qo_pct, ch_pct) / 100
    print(f"  {b:>4} {label:>25} {total:>7} {qo_pct:>6.1f}% {ch_pct:>6.1f}% {ne_pct:>6.1f}% {decisive:>9.3f}")

# ── ANALYSIS 2: Run-length analysis ───────────────────────────────

print(f"\n{'=' * 70}")
print("RUN-LENGTH ANALYSIS")
print("=" * 70)

# For each line, identify runs of same-lane tokens
# A "run" = consecutive tokens with the same lane (QO or CHSH)
# For each run, record which bins participate and the run length

bin_qo_runs = defaultdict(list)    # bin → [run_lengths when bin participates in QO run]
bin_chsh_runs = defaultdict(list)  # bin → [run_lengths when bin participates in CHSH run]

for key, tokens in lines_dict.items():
    # Build lane sequence (only QO and CHSH; skip NEUTRAL for run analysis)
    lane_seq = []
    for tok in tokens:
        if tok['bin'] == 4 or tok['bin'] == -1:
            lane_seq.append(('SKIP', tok))
        else:
            lane_seq.append((tok['lane'], tok))

    # Extract runs
    if not lane_seq:
        continue

    current_lane = None
    current_run = []

    def flush_run():
        if current_lane in ('QO', 'CHSH') and len(current_run) >= 1:
            run_len = len(current_run)
            for tok in current_run:
                b = tok['bin']
                if b == 4 or b == -1:
                    continue
                if current_lane == 'QO':
                    bin_qo_runs[b].append(run_len)
                else:
                    bin_chsh_runs[b].append(run_len)

    for lane, tok in lane_seq:
        if lane == 'SKIP' or lane == 'NEUTRAL':
            flush_run()
            current_lane = None
            current_run = []
        elif lane == current_lane:
            current_run.append(tok)
        else:
            flush_run()
            current_lane = lane
            current_run = [tok]
    flush_run()

print(f"\n  {'Bin':>4} {'Label':>25} {'QO_runs':>8} {'QO_mean':>8} {'QO_med':>7} {'CH_runs':>8} {'CH_mean':>8} {'CH_med':>7} {'Asym':>6}")
print(f"  {'-' * 84}")
for b in FUNCTIONAL_BINS:
    label = bin_labels.get(b, '?')
    qo_n = len(bin_qo_runs[b])
    ch_n = len(bin_chsh_runs[b])
    qo_mean = np.mean(bin_qo_runs[b]) if qo_n > 0 else 0
    ch_mean = np.mean(bin_chsh_runs[b]) if ch_n > 0 else 0
    qo_med = np.median(bin_qo_runs[b]) if qo_n > 0 else 0
    ch_med = np.median(bin_chsh_runs[b]) if ch_n > 0 else 0
    asym = qo_mean / ch_mean if ch_mean > 0 else float('inf')
    print(f"  {b:>4} {label:>25} {qo_n:>8} {qo_mean:>8.2f} {qo_med:>7.1f} {ch_n:>8} {ch_mean:>8.2f} {ch_med:>7.1f} {asym:>6.2f}")

# ── ANALYSIS 3: Lane-switch inertia ───────────────────────────────

print(f"\n{'=' * 70}")
print("LANE-SWITCH INERTIA")
print("=" * 70)

# For each token, check if the next token is in the same lane
bin_same = Counter()
bin_switch = Counter()
bin_transitions = Counter()  # total transitions

for key, tokens in lines_dict.items():
    for i in range(len(tokens) - 1):
        tok = tokens[i]
        nxt = tokens[i + 1]
        b = tok['bin']
        if b == 4 or b == -1:
            continue
        if tok['lane'] in ('QO', 'CHSH') and nxt['lane'] in ('QO', 'CHSH'):
            bin_transitions[b] += 1
            if tok['lane'] == nxt['lane']:
                bin_same[b] += 1
            else:
                bin_switch[b] += 1

print(f"\n  {'Bin':>4} {'Label':>25} {'Trans':>7} {'Same%':>7} {'Switch%':>8} {'Inertia':>8}")
print(f"  {'-' * 64}")
for b in FUNCTIONAL_BINS:
    label = bin_labels.get(b, '?')
    total = bin_transitions[b]
    same_pct = 100 * bin_same[b] / total if total > 0 else 0
    switch_pct = 100 * bin_switch[b] / total if total > 0 else 0
    # Inertia = same/(same+switch), higher = more lane-anchoring
    inertia = bin_same[b] / total if total > 0 else 0
    print(f"  {b:>4} {label:>25} {total:>7} {same_pct:>6.1f}% {switch_pct:>7.1f}% {inertia:>8.3f}")

# ── STATISTICAL TESTS ──────────────────────────────────────────────

print(f"\n{'=' * 70}")
print("STATISTICAL TESTS")
print("=" * 70)

stat_results = {}

# Chi-square on bin × lane (3-way: QO, CHSH, NEUTRAL)
contingency = np.array([
    [bin_lane_counts[b]['QO'], bin_lane_counts[b]['CHSH'], bin_lane_counts[b]['NEUTRAL']]
    for b in FUNCTIONAL_BINS
])
if contingency.sum() > 0:
    chi2, p, dof, exp = stats.chi2_contingency(contingency)
    print(f"\n  Chi-square on bin x lane (QO/CHSH/NEUTRAL):")
    print(f"    chi2 = {chi2:.3f}, df = {dof}, p = {p:.2e}")
    stat_results['chi2_bin_lane'] = {'chi2': float(chi2), 'df': int(dof), 'p': float(p)}

# KW on QO run lengths across bins
qo_groups = [bin_qo_runs[b] for b in FUNCTIONAL_BINS if len(bin_qo_runs[b]) >= 5]
qo_labels = [b for b in FUNCTIONAL_BINS if len(bin_qo_runs[b]) >= 5]
if len(qo_groups) >= 2:
    h, p = stats.kruskal(*qo_groups)
    print(f"\n  Kruskal-Wallis on QO run lengths across bins:")
    print(f"    H = {h:.3f}, p = {p:.2e}")
    stat_results['kruskal_qo_runs'] = {'H': float(h), 'p': float(p)}

# KW on CHSH run lengths across bins
ch_groups = [bin_chsh_runs[b] for b in FUNCTIONAL_BINS if len(bin_chsh_runs[b]) >= 5]
ch_labels = [b for b in FUNCTIONAL_BINS if len(bin_chsh_runs[b]) >= 5]
if len(ch_groups) >= 2:
    h, p = stats.kruskal(*ch_groups)
    print(f"\n  Kruskal-Wallis on CHSH run lengths across bins:")
    print(f"    H = {h:.3f}, p = {p:.2e}")
    stat_results['kruskal_chsh_runs'] = {'H': float(h), 'p': float(p)}

# Chi-square on bin × lane inertia (same vs switch)
inertia_obs = np.array([[bin_same[b], bin_switch[b]] for b in FUNCTIONAL_BINS if bin_transitions[b] >= 5])
inertia_labels = [b for b in FUNCTIONAL_BINS if bin_transitions[b] >= 5]
if inertia_obs.shape[0] >= 2 and inertia_obs.sum() > 0:
    chi2_i, p_i, dof_i, exp_i = stats.chi2_contingency(inertia_obs)
    print(f"\n  Chi-square on bin x lane inertia (same vs switch):")
    print(f"    chi2 = {chi2_i:.3f}, df = {dof_i}, p = {p_i:.2e}")
    stat_results['chi2_lane_inertia'] = {'chi2': float(chi2_i), 'df': int(dof_i), 'p': float(p_i)}

# ── EXPERT PREDICTION VERIFICATION ────────────────────────────────

print(f"\n{'=' * 70}")
print("EXPERT PREDICTION VERIFICATION")
print("=" * 70)

predictions = []

# P1: PHASE_SENSITIVE (9) produces longer CHSH runs
b9_ch = np.mean(bin_chsh_runs[9]) if bin_chsh_runs[9] else 0
all_ch = [np.mean(bin_chsh_runs[b]) for b in FUNCTIONAL_BINS if bin_chsh_runs[b]]
median_ch = np.median(all_ch) if all_ch else 0
p1 = b9_ch > median_ch
predictions.append(('PHASE_SENSITIVE longer CHSH runs', p1, f"mean_chsh_run={b9_ch:.2f} vs median={median_ch:.2f}"))

# P2: ENERGY_SPECIALIZED (7) produces longer QO runs
b7_qo = np.mean(bin_qo_runs[7]) if bin_qo_runs[7] else 0
all_qo = [np.mean(bin_qo_runs[b]) for b in FUNCTIONAL_BINS if bin_qo_runs[b]]
median_qo = np.median(all_qo) if all_qo else 0
p2 = b7_qo > median_qo
predictions.append(('ENERGY_SPECIALIZED longer QO runs', p2, f"mean_qo_run={b7_qo:.2f} vs median={median_qo:.2f}"))

# P3: ENERGY_SPECIALIZED (7) QO-leaning
b7_qo_frac = bin_lane_counts[7]['QO'] / bin_total[7] if bin_total[7] > 0 else 0
p3 = b7_qo_frac > 0.4  # should be QO-dominant
predictions.append(('ENERGY_SPECIALIZED QO-leaning', p3, f"qo_fraction={b7_qo_frac:.3f}"))

# P4: STABILITY_CRITICAL (8) CHSH-leaning
b8_ch_frac = bin_lane_counts[8]['CHSH'] / bin_total[8] if bin_total[8] > 0 else 0
p4 = b8_ch_frac > 0.4  # should be CHSH-dominant
predictions.append(('STABILITY_CRITICAL CHSH-leaning', p4, f"chsh_fraction={b8_ch_frac:.3f}"))

# P5: HUB_UNIVERSAL (6) neutral — neither QO nor CHSH dominant
b6_qo = bin_lane_counts[6]['QO'] / bin_total[6] if bin_total[6] > 0 else 0
b6_ch = bin_lane_counts[6]['CHSH'] / bin_total[6] if bin_total[6] > 0 else 0
p5 = abs(b6_qo - b6_ch) < 0.2  # balanced within 20pp
predictions.append(('HUB_UNIVERSAL lane-neutral', p5, f"qo={b6_qo:.3f}, chsh={b6_ch:.3f}, diff={abs(b6_qo-b6_ch):.3f}"))

for name, result, detail in predictions:
    status = "CONFIRMED" if result else "REJECTED"
    print(f"\n  [{status}] {name}")
    print(f"    {detail}")

confirmed = sum(1 for _, r, _ in predictions if r)
print(f"\n  SCORE: {confirmed}/{len(predictions)} predictions confirmed")

# ── Save results ───────────────────────────────────────────────────

results = {
    'metadata': {
        'phase': 'AFFORDANCE_STRESS_TEST',
        'test': 'T2_LANE_INTERACTION',
        'qo_threshold': QO_THRESH,
        'chsh_threshold': CHSH_THRESH,
    },
    'per_bin': {},
    'statistical_tests': stat_results,
    'predictions': {name: {'confirmed': bool(result), 'detail': detail} for name, result, detail in predictions},
}

for b in FUNCTIONAL_BINS:
    total = bin_total[b]
    results['per_bin'][str(b)] = {
        'label': bin_labels.get(b, '?'),
        'total_tokens': total,
        'qo_fraction': round(bin_lane_counts[b]['QO'] / total, 4) if total > 0 else 0,
        'chsh_fraction': round(bin_lane_counts[b]['CHSH'] / total, 4) if total > 0 else 0,
        'neutral_fraction': round(bin_lane_counts[b]['NEUTRAL'] / total, 4) if total > 0 else 0,
        'mean_qo_run': round(float(np.mean(bin_qo_runs[b])), 3) if bin_qo_runs[b] else None,
        'mean_chsh_run': round(float(np.mean(bin_chsh_runs[b])), 3) if bin_chsh_runs[b] else None,
        'lane_inertia': round(bin_same[b] / bin_transitions[b], 4) if bin_transitions[b] > 0 else None,
        'n_qo_runs': len(bin_qo_runs[b]),
        'n_chsh_runs': len(bin_chsh_runs[b]),
    }

out_path = PROJECT / 'phases' / 'AFFORDANCE_STRESS_TEST' / 'results' / 't2_lane_interaction.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {out_path}")
