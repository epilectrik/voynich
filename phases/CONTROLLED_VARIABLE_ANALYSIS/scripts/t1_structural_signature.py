#!/usr/bin/env python3
"""
T1: Structural Signature Extraction
CONTROLLED_VARIABLE_ANALYSIS phase (Tier 3/4)

Extract the quantitative properties from the 6-state automaton and
supporting constraints that any candidate controlled variable must explain.
These form the "structural signature" — the pattern that a physical
interpretation must fit.
"""

import sys
import json
import functools
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
MSA_RESULTS = Path(__file__).parent.parent.parent / 'MINIMAL_STATE_AUTOMATON' / 'results'


def run():
    print("=" * 70)
    print("T1: Structural Signature Extraction")
    print("CONTROLLED_VARIABLE_ANALYSIS phase (Tier 3/4)")
    print("=" * 70)

    # Load automaton data
    with open(MSA_RESULTS / 't6_state_topology.json') as f:
        t6 = json.load(f)
    with open(MSA_RESULTS / 't8_regime_conditioned.json') as f:
        t8 = json.load(f)
    with open(MSA_RESULTS / 't9_holdout_stability.json') as f:
        t9 = json.load(f)

    P = t6['transition_matrix']

    # =========================================================
    # Define the structural signature
    # =========================================================
    print("\n[1/3] Structural Signature Properties")
    print("  These are quantitative facts any controlled-variable")
    print("  interpretation must be consistent with.\n")

    signature = []

    # S1: Operational dominance
    s = {
        'id': 'SIG-01',
        'property': 'Operational mass dominance',
        'value': '68% of tokens in S4 (AX/EN major)',
        'numeric': 0.677,
        'implication': 'The system spends ~2/3 of its time in a single undifferentiated operational state. The controlled variable must have a dominant steady-state regime.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # S2: Hub-and-spoke
    s = {
        'id': 'SIG-02',
        'property': 'Universal attractor topology',
        'value': 'All states exit to S4 at >56%. S4 self-loop = 0.698',
        'numeric': 0.698,
        'implication': 'The controlled variable returns to baseline after every perturbation. Deviations are transient, not cumulative.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # S3: Fast mixing
    s = {
        'id': 'SIG-03',
        'property': 'Sub-2-token mixing time',
        'value': f"Spectral gap = {t6['spectral_gap']}, mixing time = {t6['mixing_time']} tokens",
        'numeric': t6['mixing_time'],
        'implication': 'The controlled variable has no long-range memory. Current state conveys all information about future evolution. The variable resets rapidly.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # S4: Hazard asymmetry
    s = {
        'id': 'SIG-04',
        'property': 'Hazard/safe asymmetry',
        'value': f"FL_HAZ entry 6.5x more likely than FL_SAFE from operational mass",
        'numeric': t6['hazard_safe_ratio'],
        'implication': 'Risk events are much more common than safe-completion events. The controlled variable operates near hazard boundaries most of the time.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # S5: 1-token hazard gate
    s = {
        'id': 'SIG-05',
        'property': 'Single-token hazard gate duration',
        'value': 'Hazard perturbation decays in exactly 1 token (C967)',
        'numeric': 1,
        'implication': 'Hazard events are sharp pulses, not sustained crises. The controlled variable can be destabilized briefly but recovers in one step.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # S6: Two-lane oscillation
    s = {
        'id': 'SIG-06',
        'property': 'Binary lane oscillation within operational mass',
        'value': 'QO/CHSH alternation with section-specific Markov + hazard gate (C966-C970)',
        'numeric': 2,
        'implication': 'The controlled variable has two complementary modes or phases that alternate. Not continuous variation — binary switching.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # S7: REGIME modulates weights not topology
    s = {
        'id': 'SIG-07',
        'property': 'REGIME modulates transition weights, topology fixed',
        'value': f"Global chi2={t8['global_chi2']}, p={t8['global_p']:.2e}. FL markers regime-independent.",
        'numeric': t8['global_chi2'],
        'implication': 'There is an external parameter (REGIME) that changes HOW INTENSELY the system operates without changing WHAT it does. The controlled variable responds to intensity scaling.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # S8: FL regime-invariance
    s = {
        'id': 'SIG-08',
        'property': 'Boundary markers regime-independent',
        'value': 'FL_HAZ p=0.127, FL_SAFE p=0.107 (not regime-dependent)',
        'numeric': 0.127,
        'implication': 'The MEANING of hazard and safe conditions does not change with operating intensity. Only the frequency of operational transitions changes.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # S9: Recovery architecture
    s = {
        'id': 'SIG-09',
        'property': 'e-dominated recovery with 2-retry limit',
        'value': '54.7% of recovery paths go through e (stability anchor). Max 2 recovery cycles (89% reversibility).',
        'numeric': 0.547,
        'implication': 'The controlled variable can be stabilized by a specific operation (e). Recovery is not symmetric with destabilization — it requires a dedicated mechanism. And it has a hard limit.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # S10: Closed-loop circulation
    s = {
        'id': 'SIG-10',
        'property': 'Closed-loop with no external reference',
        'value': 'C171: no external reference points. C384: no A-B entry coupling.',
        'numeric': 0,
        'implication': 'The controlled variable is internal to the system. It does not reference external standards or measurements. All control is relative to internal state.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # S11: Categorical control
    s = {
        'id': 'SIG-11',
        'property': 'Categorical (not quantitative) control',
        'value': 'C469: no parametric encoding. C287-C290: no magnitudes.',
        'numeric': 0,
        'implication': 'The controlled variable is assessed by categorical tests (pass/fail, present/absent), not by measurement. No numbers, no arithmetic.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # S12: AXm transient feeder
    s = {
        'id': 'SIG-12',
        'property': 'Minor execution group as transient feeder',
        'value': 'AXm->AXM 24.4x stronger than reverse. AXm = 3% of tokens.',
        'numeric': 24.4,
        'implication': 'There is a brief preparatory or transitional phase that feeds into the main operational regime. Not a separate mode — a ramp-up.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # S13: FQ scaffold
    s = {
        'id': 'SIG-13',
        'property': 'FQ as recurrence modulator (18%)',
        'value': 'FQ self-loop 0.251. All states flow to FQ at 9.5-25.1%.',
        'numeric': 0.18,
        'implication': 'There is a periodic monitoring/checking function that interrupts operational flow. In REGIME_4 (precision), this interruption rate increases.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # S14: Late-positioned FL_SAFE
    s = {
        'id': 'SIG-14',
        'property': 'FL_SAFE heavily line-final',
        'value': 'Mean position = 0.816, 73% in final third of line.',
        'numeric': 0.816,
        'implication': 'Safe/completion marking occurs at the end of control blocks (lines), not during them. It is a closure signal, not an ongoing status.',
    }
    signature.append(s)
    print(f"  {s['id']}: {s['property']}")
    print(f"    {s['value']}")
    print(f"    => {s['implication']}\n")

    # =========================================================
    # Summary
    # =========================================================
    print(f"\n{'='*70}")
    print(f"STRUCTURAL SIGNATURE SUMMARY")
    print(f"{'='*70}")
    print(f"\n  {len(signature)} signature properties extracted.")
    print(f"  Any candidate controlled variable must be consistent with ALL of these.")
    print(f"\n  The signature describes a system that:")
    print(f"  - Spends most time in a dominant steady-state (SIG-01, SIG-02)")
    print(f"  - Has no long-range memory (SIG-03)")
    print(f"  - Operates near hazard boundaries (SIG-04)")
    print(f"  - Experiences sharp transient risks, not sustained crises (SIG-05)")
    print(f"  - Alternates between two complementary modes (SIG-06)")
    print(f"  - Responds to intensity scaling without structural change (SIG-07, SIG-08)")
    print(f"  - Has dedicated recovery via a specific stabilizing operation (SIG-09)")
    print(f"  - Uses internal categorical assessment, not measurement (SIG-10, SIG-11)")
    print(f"  - Has a brief preparatory ramp before main operation (SIG-12)")
    print(f"  - Includes periodic monitoring interruptions (SIG-13)")
    print(f"  - Marks completion at block boundaries (SIG-14)")

    # Save
    results = {
        'test': 'T1_structural_signature',
        'n_properties': len(signature),
        'signature': signature,
    }
    with open(RESULTS_DIR / 't1_structural_signature.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't1_structural_signature.json'}")


if __name__ == '__main__':
    run()
