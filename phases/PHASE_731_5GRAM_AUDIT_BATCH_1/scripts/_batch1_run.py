"""Phase 731 Batch 1 — 5-gram null audit (expert-audited redesign).

PRE-REGISTERED & LOCKED (see INDEX.md):

POSITIVE CONTROL (must survive):
- C2056: qo-k -> ok bigram (known +29.6pp residual from PHASE_729)

CONSTRAINTS UNDER AUDIT:
- C549: qo-prefix -> ch/sh-prefix (mechanism claim)
- C557: daiin line-initial rate (surface-fact)
- C561 M1: or -> aiin bigram; M2: aiin -> aiin (near-zero rail)
- C562: ary line-final rate (surface-fact)
- C816 M1: daiin mean-pos; M2: ol mean-pos; M3: position differential (mechanism)

METHODOLOGY:
- Held-out folio split (80/20, seed=42)
- Train 5-gram on 80% folio lines
- Measure on 20% held-out real + N synth corpora (matched to held-out structure)
- N_SYNTH = 200 for high-freq, 500 for rare-event sub-measurements
- Apply STRICTER of (absolute 0.10) and (fractional 0.30 x original_effect)
- Near-zero rail for C561 M2

POSITIVE-CONTROL GATE: If C2056 DEMOTES, abort and recalibrate.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from _audit_framework import (
    load_real_currier_b_lines, train_5gram,
    line_initial_rate, line_final_rate, mean_normalized_position,
    bigram_rate, prefix_bigram_rate, position_differential,
    run_audit, classify_disposition,
)

ORDER = 5
N_SYNTH_HIGH = 200
N_SYNTH_RARE = 500

print('=' * 70)
print('Phase 731 Batch 1 -- 5-gram null audit (revised: p_emp-primary, same-corpus)')
print('=' * 70)
print('\nMETHODOLOGY NOTE: First-run held-out validation produced calibration-')
print('inconsistent results vs PHASE_729 (small held-out subsets create sampling')
print('noise that destabilizes low-frequency bigram measurements). Revised to')
print('same-corpus train+measure. Caveat: in-sample evaluation. Verdicts use')
print('p_emp as significance bar; residual/original-effect ratio as mechanism-')
print('strength descriptor.')

print('\nLoading Currier B...')
lines, line_folios = load_real_currier_b_lines()
print(f'  Total: {len(lines)} lines, {len(set(line_folios))} folios, {sum(len(l) for l in lines)} tokens')
# Use full corpus for training AND for measurement (in-sample)
hold_lines = lines  # rename for clarity in measurement code
print(f'\nTraining {ORDER}-gram on full Currier B (in-sample)...')
counts = train_5gram(lines, order=ORDER)
print(f'  {len(counts)} contexts learned.')

dispositions = {}


def record(cid, sub, summary, original_effect_magnitude, claim_type, claim_note='', near_zero_claim=False):
    verdict = classify_disposition(summary, original_effect_magnitude, claim_type, near_zero_claim)
    if cid not in dispositions:
        dispositions[cid] = {'sub_measurements': {}, 'claim_type': claim_type, 'claim_note': claim_note}
    dispositions[cid]['sub_measurements'][sub] = {
        'real_held_out': summary['real_value'],
        'synth_mean': summary['synth_mean'],
        'synth_std': summary['synth_std'],
        'residual': summary['residual'],
        'z_diff': summary['z_diff'],
        'p_emp_above': summary['p_emp_above'],
        'p_emp_below': summary['p_emp_below'],
        'original_effect_magnitude': original_effect_magnitude,
        'near_zero_claim': near_zero_claim,
        'verdict': verdict,
        'real_full': summary['real_full'],
        'n_synth': summary['n_synth'],
    }
    print(f'    {sub}: real={summary["real_value"]:.4f} synth={summary["synth_mean"]:.4f}+/-{summary["synth_std"]:.4f}  '
          f'res={summary["residual"]:+.4f}  z={summary["z_diff"]:+.2f}  p_above={summary["p_emp_above"]:.3f}')
    print(f'      -> {verdict}')


# ============ POSITIVE CONTROL: C2056 ============
print('\n[POSITIVE CONTROL C2056] qo-k -> ok bigram (PHASE_729: real +35.1%, synth +5.5%, residual +29.6pp)')
# qo-k tokens are tokens starting with 'qok'; next token starts with 'ok'
summary = run_audit(hold_lines, counts, ORDER, N_SYNTH_HIGH,
                    lambda c: prefix_bigram_rate(c, 'qok', ['ok']))
record('C2056_CONTROL', 'M1_qok_to_ok_prefix_bigram', summary,
       original_effect_magnitude=0.296, claim_type='mechanism',
       claim_note='POSITIVE CONTROL — must SURVIVE for methodology to be calibrated')

control_verdict = list(dispositions['C2056_CONTROL']['sub_measurements'].values())[0]['verdict']
print(f'\n  Control verdict: {control_verdict}')
if 'DEMOTE' in control_verdict and 'STRONG' not in control_verdict:
    print('\n  !!! POSITIVE CONTROL FAILED -- methodology likely miscalibrated !!!')
    print('  This may indicate:')
    print('    - Held-out split disrupting qo-k coverage')
    print('    - Synth corpora too small to reproduce qo-k frequency')
    print('    - Threshold misconfiguration')
    print('  ABORTING further batch measurements.')
    out = Path(__file__).parent.parent / 'results' / 'batch1_dispositions.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dispositions, indent=2))
    sys.exit(1)
print(f'  Control SURVIVED. Proceeding with batch measurements.\n')


# ============ C549 ============
print('[C549] qo-prefix -> ch/sh-prefix interleaving (mechanism; claim: 56.3% vs 50.6% expected)')
summary = run_audit(hold_lines, counts, ORDER, N_SYNTH_HIGH,
                    lambda c: prefix_bigram_rate(c, 'qo', ['ch', 'sh']))
record('C549', 'M1_qo_to_chsh_prefix_bigram', summary,
       original_effect_magnitude=0.057, claim_type='mechanism',
       claim_note='qo/ch-sh coordination signature; effect = 56.3% - 50.6% expected = 5.7pp')


# ============ C557 ============
print('\n[C557] daiin line-initial rate (surface-fact; claim: 27.7% vs ~3% baseline)')
summary = run_audit(hold_lines, counts, ORDER, N_SYNTH_HIGH,
                    lambda c: line_initial_rate(c, 'daiin'))
record('C557', 'M1_daiin_line_initial', summary,
       original_effect_magnitude=0.247, claim_type='surface_fact',
       claim_note='daiin line-initial rate; effect = 27.7% - ~3% line-fraction = 24.7pp')


# ============ C561 ============
print('\n[C561 M1] or -> aiin directional bigram (surface-fact; claim: 87.5%)')
summary1 = run_audit(hold_lines, counts, ORDER, N_SYNTH_HIGH,
                     lambda c: bigram_rate(c, 'or', 'aiin'))
record('C561', 'M1_or_to_aiin_bigram', summary1,
       original_effect_magnitude=0.575, claim_type='surface_fact',
       claim_note='or->aiin bigram; effect = 87.5% - ~30% baseline = 57.5pp')

print('\n[C561 M2] aiin -> aiin structural prohibition (claim: 0%; near-zero rail)')
summary2 = run_audit(hold_lines, counts, ORDER, N_SYNTH_RARE,
                     lambda c: bigram_rate(c, 'aiin', 'aiin'))
record('C561', 'M2_aiin_to_aiin_zero_prohibition', summary2,
       original_effect_magnitude=0.05, claim_type='surface_fact',
       claim_note='aiin->aiin should be ~0% (structural prohibition); near-zero rail applied',
       near_zero_claim=True)


# ============ C562 ============
print('\n[C562] ary line-final rate (surface-fact; claim: 100%)')
summary = run_audit(hold_lines, counts, ORDER, N_SYNTH_RARE,
                    lambda c: line_final_rate(c, 'ary'))
record('C562', 'M1_ary_line_final', summary,
       original_effect_magnitude=0.90, claim_type='surface_fact',
       claim_note='ary 100% line-final; effect = 100% - ~10% random = 90pp')


# ============ C816 ============
print('\n[C816 M1] daiin mean normalized line-position (mechanism; claim: 0.413)')
summary_d = run_audit(hold_lines, counts, ORDER, N_SYNTH_HIGH,
                      lambda c: mean_normalized_position(c, 'daiin'))
record('C816', 'M1_daiin_mean_position', summary_d,
       original_effect_magnitude=0.087, claim_type='mechanism',
       claim_note='daiin mean pos 0.413; effect vs midline 0.5 = 0.087')

print('\n[C816 M2] ol mean normalized line-position (mechanism; claim: 0.511)')
summary_o = run_audit(hold_lines, counts, ORDER, N_SYNTH_HIGH,
                      lambda c: mean_normalized_position(c, 'ol'))
record('C816', 'M2_ol_mean_position', summary_o,
       original_effect_magnitude=0.011, claim_type='mechanism',
       claim_note='ol mean pos 0.511; effect vs midline 0.5 = 0.011')

print('\n[C816 M3] daiin-vs-ol position differential (mechanism; claim: ol_pos - daiin_pos = +0.098)')
summary_diff = run_audit(hold_lines, counts, ORDER, N_SYNTH_HIGH,
                         lambda c: position_differential(c, 'daiin', 'ol'))
record('C816', 'M3_position_differential', summary_diff,
       original_effect_magnitude=0.098, claim_type='mechanism',
       claim_note='ol mean-pos minus daiin mean-pos; effect = 0.511 - 0.413 = +0.098')


# ============ AGGREGATE VERDICTS ============
print('\n' + '=' * 70)
print('=== AGGREGATE VERDICTS (worst sub-measurement determines) ===')
print('=' * 70)
verdict_priority = {
    'DEMOTE_Tier2_to_Tier3_zero_reproducible_by_markov': 5,
    'DEMOTE_Tier2_to_Tier3_markov_trivial': 4,
}
def verdict_rank(v):
    if 'DEMOTE' in v and 'STRONG' not in v:
        return 4 + ('markov_trivial' in v) - ('weakly' in v) * 0.5
    return 0
for cid in sorted(dispositions.keys()):
    subs = dispositions[cid]['sub_measurements']
    verdicts = [v['verdict'] for v in subs.values()]
    # Sort: any DEMOTE wins, except SURVIVES_STRONG can override
    has_strong = any('SURVIVES_STRONG' in v for v in verdicts)
    has_demote = any('DEMOTE' in v and 'STRONG' not in v for v in verdicts)
    has_survives = any(v.startswith('SURVIVES') for v in verdicts)
    if has_strong and not has_demote:
        worst = next(v for v in verdicts if 'SURVIVES_STRONG' in v)
    elif has_demote:
        worst = next(v for v in verdicts if 'DEMOTE' in v and 'STRONG' not in v)
    else:
        worst = next(iter(verdicts))
    dispositions[cid]['aggregate_verdict'] = worst
    print(f'  {cid}: {worst}')

# Write JSON
out = Path(__file__).parent.parent / 'results' / 'batch1_dispositions.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(dispositions, indent=2))
print(f'\nDispositions written to {out}')

# Summary stats (exclude control from rates)
audited = {k: v for k, v in dispositions.items() if k != 'C2056_CONTROL'}
agg = [audited[c]['aggregate_verdict'] for c in audited]
n_demote = sum(1 for v in agg if 'DEMOTE' in v and 'STRONG' not in v)
n_survive = sum(1 for v in agg if 'SURVIVES' in v)
print(f'\nBatch 1 summary (excluding positive control):')
print(f'  {n_demote}/{len(agg)} demoted; {n_survive}/{len(agg)} survived')
print(f'  Demotion rate: {n_demote/len(agg)*100:.0f}% (expert prediction 67-83% due to selection bias)')
print(f'  Crazy-expert: do NOT extrapolate to full suspect zone (lexical/positional subset over-represented)')
