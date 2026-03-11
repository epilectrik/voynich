"""
T5: Integration + Report + Constraints
Phase 575 - SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE

Synthesizes T0-T4 results into C1647-C1650 constraint verdicts and generates
REPORT_575.md.
"""

import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
PHASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def main():
    t_start = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 70)
    print("T5: Integration + Constraints")
    print("Phase 575 - SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE")
    print("=" * 70)

    # ---- Load all prior results ----
    with open(os.path.join(RESULTS_DIR, 't0_acs_assembly.json')) as f:
        t0 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't1_authenticated_apparatus.json')) as f:
        t1 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't2_gated_simulation.json')) as f:
        t2 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't3_packet_authentication_anatomy.json')) as f:
        t3 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't4_landscape_remap.json')) as f:
        t4 = json.load(f)

    # ================================================================
    # C1647: ACS Configuration Verdict
    # ================================================================
    print("\n--- C1647: ACS Configuration ---")
    sig_coverage = t0['signature_coverage']['coverage_pct']
    cts_acs_rho = t0['cts_acs_correlation']['rho']
    acs_better = t0['discrimination_check']['acs_better']
    acs_gap = t0['discrimination_check']['acs_gap']
    cts_gap = t0['discrimination_check']['cts_gap']

    # Check criteria
    coverage_ok = sig_coverage > 60
    rho_ok = 0.3 <= cts_acs_rho <= 0.85
    rho_redundant = cts_acs_rho > 0.85

    # Check RESISTANT mean ACS > COUNTERFEITABLE mean ACS
    per_sig = t3.get('per_signature', {})
    resistant_acs_vals = [s['mean_acs'] for s in per_sig.values()
                         if s.get('class') == 'RESISTANT' and s['n_events'] > 0]
    counter_acs_vals = [s['mean_acs'] for s in per_sig.values()
                        if s.get('class') == 'A2_COUNTERFEITABLE' and s['n_events'] > 0]
    if resistant_acs_vals and counter_acs_vals:
        res_mean = sum(resistant_acs_vals) / len(resistant_acs_vals)
        cf_mean = sum(counter_acs_vals) / len(counter_acs_vals)
        acs_discriminates = res_mean > cf_mean
    else:
        res_mean = cf_mean = 0
        acs_discriminates = False

    # Empirical thresholds differ between profiles
    thresholds = t0['empirical_thresholds'].get('MODERATE', {})
    thresh_a1 = thresholds.get('A1', 0)
    thresh_a2 = thresholds.get('A2', 0)
    thresh_a3 = thresholds.get('A3', 0)
    thresholds_differ = (abs(thresh_a2 - thresh_a1) > 0.05 or
                         abs(thresh_a2 - thresh_a3) > 0.05)

    if rho_redundant:
        c1647_verdict = 'CONFIGURATION_ACS_REDUNDANT'
    elif coverage_ok and rho_ok and acs_discriminates and thresholds_differ:
        c1647_verdict = 'CONFIGURATION_ACS_VALIDATED'
    else:
        c1647_verdict = 'CONFIGURATION_ACS_PARTIAL'

    c1647_explanation = (
        f"Signature coverage={sig_coverage:.1f}% (>60%: {coverage_ok}). "
        f"CTS-ACS rho={cts_acs_rho:.4f} (in [0.3,0.85]: {rho_ok}). "
        f"RESISTANT mean ACS={res_mean:.4f} > COUNTERFEITABLE={cf_mean:.4f}: {acs_discriminates}. "
        f"Thresholds differ: A1={thresh_a1:.4f}, A2={thresh_a2:.4f}, A3={thresh_a3:.4f} ({thresholds_differ}). "
        f"ACS gap={acs_gap:.4f} vs CTS gap={cts_gap:.4f}, ACS better={acs_better}."
    )
    print(f"  {c1647_verdict}")
    print(f"  {c1647_explanation}")

    # ================================================================
    # C1648: Two-Layer Gate Verdict
    # ================================================================
    print("\n--- C1648: Two-Layer Gate ---")
    layer_d = t3['layer_decomposition']
    l1_delta = layer_d['layer1_only_mean_delta']
    l2_delta = layer_d['layer2_incremental_mean_delta']
    both_delta = layer_d['both_mean_delta']
    synergy = layer_d['synergy']
    l1_contributes = layer_d['layer1_contributes']
    l2_contributes = layer_d['layer2_contributes']

    # Check A2 FI reduction > 10%
    best_config = t3['best_config_by_SSI']
    ps = t2['profile_summary'].get(best_config, {})
    a2_summary = ps.get('A2_SEALED_RECIRCULATION', {})
    a2_fi_reduction = abs(a2_summary.get('ccs1_reduction_pct', 0))

    # Check non-A2 not degraded > 5%
    a1_summary = ps.get('A1_BATH_REFLUX', {})
    a3_summary = ps.get('A3_DISTILL_COLLECT', {})
    a1_delta = abs(a1_summary.get('mean_delta_advantage', 0))
    a3_delta = abs(a3_summary.get('mean_delta_advantage', 0))
    a1_baseline = abs(a1_summary.get('mean_baseline_advantage', 0.001))
    a3_baseline = abs(a3_summary.get('mean_baseline_advantage', 0.001))
    a1_pct_change = a1_delta / a1_baseline * 100 if a1_baseline > 0.001 else 0
    a3_pct_change = a3_delta / a3_baseline * 100 if a3_baseline > 0.001 else 0
    non_a2_degraded = a1_pct_change > 5 or a3_pct_change > 5

    if both_delta <= 0 or non_a2_degraded:
        c1648_verdict = 'TWO_LAYER_GATE_REJECTED'
    elif synergy and l1_contributes and l2_contributes:
        c1648_verdict = 'TWO_LAYER_GATE_SYNERGISTIC'
    else:
        c1648_verdict = 'TWO_LAYER_GATE_SINGLE_DOMINANT'

    c1648_explanation = (
        f"Layer1 delta={l1_delta:.6f}, Layer2 incremental={l2_delta:.6f}, "
        f"Both={both_delta:.6f}. Synergy={synergy}. "
        f"L1 contributes={l1_contributes}, L2 contributes={l2_contributes}. "
        f"A2 CCS1 reduction={a2_fi_reduction:.1f}%. "
        f"A1 change={a1_pct_change:.1f}%, A3 change={a3_pct_change:.1f}% "
        f"(non-A2 degraded >5%: {non_a2_degraded})."
    )
    print(f"  {c1648_verdict}")
    print(f"  {c1648_explanation}")

    # ================================================================
    # C1649: Event-Band Stratification Verdict
    # ================================================================
    print("\n--- C1649: Event-Band Stratification ---")
    ssi_data = t3['surgical_selectivity'].get(best_config, {})
    ssi = ssi_data.get('SSI', 0)
    fi_reduction = ssi_data.get('fi_reduction', 0)
    strong_loss = ssi_data.get('strong_loss', 0)

    if ssi >= 2.0:
        c1649_verdict = 'STRATIFIED_SELECTIVITY_VALIDATED'
    elif ssi >= 1.0:
        c1649_verdict = 'STRATIFIED_SELECTIVITY_PARTIAL'
    else:
        c1649_verdict = 'STRATIFIED_SELECTIVITY_REJECTED'

    c1649_explanation = (
        f"Best config: {best_config}. SSI={ssi:.4f}. "
        f"FI reduction={fi_reduction:.6f}, Strong-band loss={strong_loss:.6f}. "
    )
    print(f"  {c1649_verdict}")
    print(f"  {c1649_explanation}")

    # ================================================================
    # C1650: Landscape Shift Verdict
    # ================================================================
    print("\n--- C1650: Landscape Shift ---")
    a2_pole = t4['a2_pole_analysis']
    n_forg_ungated = a2_pole['n_forgiving_ungated']
    n_forg_gated = a2_pole['n_forgiving_gated']
    pole_reduction = a2_pole['pole_reduction_pct']
    new_a1a3 = a2_pole['a1a3_new_forgiving']

    cls_summary = t4['classification_summary']
    total_forg_gated = cls_summary['FORGIVING_RECIRCULATOR']['n_gated']
    total_forg_ungated = cls_summary['FORGIVING_RECIRCULATOR']['n_ungated']

    if new_a1a3 > 0 or total_forg_gated > total_forg_ungated:
        c1650_verdict = 'LANDSCAPE_POLE_AGGRAVATED'
    elif pole_reduction >= 30:
        c1650_verdict = 'LANDSCAPE_POLE_REDUCED'
    else:
        c1650_verdict = 'LANDSCAPE_POLE_STABLE'

    c1650_explanation = (
        f"A2 FORGIVING: ungated={n_forg_ungated}, gated={n_forg_gated}, "
        f"reduction={pole_reduction:.1f}%. "
        f"Total FORGIVING: ungated={total_forg_ungated}, gated={total_forg_gated}. "
        f"New A1/A3 FORGIVING: {new_a1a3}."
    )
    print(f"  {c1650_verdict}")
    print(f"  {c1650_explanation}")

    # ================================================================
    # Build constraints
    # ================================================================
    constraints = {
        'C1647': {
            'id': 'C1647',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'ACS', 'configuration', 'morphology'],
            'claim': f"ACS configuration verdict: {c1647_verdict}. {c1647_explanation}",
            'verdict': c1647_verdict,
            'evidence': {
                'source': 'Phase 575 T0 ACS assembly + T3 per-signature analysis',
                'signature_coverage_pct': round(sig_coverage, 1),
                'cts_acs_rho': round(cts_acs_rho, 4),
                'resistant_mean_acs': round(res_mean, 4),
                'counterfeitable_mean_acs': round(cf_mean, 4),
                'acs_gap': round(acs_gap, 4),
                'cts_gap': round(cts_gap, 4),
            },
            'phase': 575,
        },
        'C1648': {
            'id': 'C1648',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'gate', 'two_layer', 'Y_credit', 'cleanliness'],
            'claim': f"Two-layer gate verdict: {c1648_verdict}. {c1648_explanation}",
            'verdict': c1648_verdict,
            'evidence': {
                'source': 'Phase 575 T1 verification + T3 layer decomposition',
                'layer1_delta': round(l1_delta, 6),
                'layer2_delta': round(l2_delta, 6),
                'both_delta': round(both_delta, 6),
                'synergy': synergy,
                'a2_ccs1_reduction_pct': round(a2_fi_reduction, 1),
            },
            'phase': 575,
        },
        'C1649': {
            'id': 'C1649',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'stratification', 'event_band', 'SSI'],
            'claim': f"Event-band stratification verdict: {c1649_verdict}. {c1649_explanation}",
            'verdict': c1649_verdict,
            'evidence': {
                'source': 'Phase 575 T3 surgical selectivity analysis',
                'best_config': best_config,
                'SSI': round(ssi, 4),
                'fi_reduction': round(fi_reduction, 6),
                'strong_loss': round(strong_loss, 6),
            },
            'phase': 575,
        },
        'C1650': {
            'id': 'C1650',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'landscape', 'pole_reduction', 'folio_classification'],
            'claim': f"Landscape shift verdict: {c1650_verdict}. {c1650_explanation}",
            'verdict': c1650_verdict,
            'evidence': {
                'source': 'Phase 575 T4 landscape remapping',
                'n_forgiving_ungated': n_forg_ungated,
                'n_forgiving_gated': n_forg_gated,
                'pole_reduction_pct': round(pole_reduction, 1),
                'new_a1a3_forgiving': new_a1a3,
                'best_config_used': t4['metadata']['best_config_used'],
            },
            'phase': 575,
        },
    }

    # ================================================================
    # Summary verdicts
    # ================================================================
    verdicts = {
        'acs_configuration': {
            'verdict': c1647_verdict,
            'explanation': c1647_explanation,
        },
        'two_layer_gate': {
            'verdict': c1648_verdict,
            'explanation': c1648_explanation,
        },
        'event_band_stratification': {
            'verdict': c1649_verdict,
            'explanation': c1649_explanation,
        },
        'landscape_shift': {
            'verdict': c1650_verdict,
            'explanation': c1650_explanation,
        },
    }

    all_validated = (
        c1647_verdict == 'CONFIGURATION_ACS_VALIDATED' and
        c1648_verdict == 'TWO_LAYER_GATE_SYNERGISTIC' and
        c1649_verdict == 'STRATIFIED_SELECTIVITY_VALIDATED' and
        c1650_verdict == 'LANDSCAPE_POLE_REDUCED'
    )

    # ================================================================
    # Generate REPORT_575.md
    # ================================================================
    print("\n--- Generating REPORT_575.md ---")

    # Gather key numbers
    t1_verify = t1.get('verification', {})
    t2_meta = t2.get('metadata', {})

    report_lines = [
        "# Phase 575: SELECTIVE CLOSURE CREDIT + AUTHENTICATION GATE",
        "",
        "## Summary",
        "",
        f"Authentication gate internalizing Phase 574's counterfeit-closure threshold "
        f"as an online apparatus parameter. Four constraints (C1647-C1650) produced.",
        "",
        f"**Best gate configuration:** {best_config}",
        f"**SSI (Surgical Selectivity Index):** {ssi:.4f}",
        "",
        "## Constraint Verdicts",
        "",
        f"| ID | Verdict | Pass? |",
        f"|------|---------|-------|",
        f"| C1647 (ACS Configuration) | {c1647_verdict} | {'YES' if c1647_verdict == 'CONFIGURATION_ACS_VALIDATED' else 'PARTIAL/NO'} |",
        f"| C1648 (Two-Layer Gate) | {c1648_verdict} | {'YES' if c1648_verdict == 'TWO_LAYER_GATE_SYNERGISTIC' else 'PARTIAL/NO'} |",
        f"| C1649 (Event-Band Stratification) | {c1649_verdict} | {'YES' if c1649_verdict == 'STRATIFIED_SELECTIVITY_VALIDATED' else 'PARTIAL/NO'} |",
        f"| C1650 (Landscape Shift) | {c1650_verdict} | {'YES' if c1650_verdict == 'LANDSCAPE_POLE_REDUCED' else 'PARTIAL/NO'} |",
        "",
        "## T0: ACS Assembly",
        "",
        f"- Events: {t0['metadata']['n_events']}",
        f"- Signature table coverage: {sig_coverage:.1f}%",
        f"- CTS-ACS Spearman rho: {cts_acs_rho:.4f}",
        f"- ACS discrimination gap: {acs_gap:.4f} (vs CTS: {cts_gap:.4f})",
        f"- Empirical A2 thresholds: CONSERVATIVE={t0['empirical_thresholds'].get('CONSERVATIVE', {}).get('A2', '?')}, "
        f"MODERATE={thresh_a2}, AGGRESSIVE={t0['empirical_thresholds'].get('AGGRESSIVE', {}).get('A2', '?')}",
        "",
        "## T1: Authenticated Apparatus",
        "",
        f"- Identity check (threshold=0): {'PASS' if t1_verify.get('identity_check', {}).get('pass') else 'FAIL'}",
        f"- Zero-auth check (threshold=999): {'PASS' if t1_verify.get('zero_auth_check', {}).get('pass') else 'FAIL'}",
        f"- Both-layers synergy: {'PASS' if t1_verify.get('both_layers', {}).get('synergy') else 'FAIL'}",
        "",
        "## T2: Gated Simulation",
        "",
        f"- Configurations tested: {t2_meta.get('n_configs', 5)}",
        f"- Total runs: {t2_meta.get('total_runs', '?')}",
        f"- Elapsed: {t2_meta.get('elapsed_seconds', '?')}s",
        "",
        "### Profile Summary (best config: {})".format(best_config),
        "",
    ]

    for profile in ['A1_BATH_REFLUX', 'A2_SEALED_RECIRCULATION', 'A3_DISTILL_COLLECT']:
        ps_data = ps.get(profile, {})
        report_lines.append(
            f"- **{profile}**: delta_adv={ps_data.get('mean_delta_advantage', 0):.4f}, "
            f"CCS1_red={ps_data.get('ccs1_reduction_pct', 0):.1f}%, "
            f"improved/degraded={ps_data.get('n_improved', 0)}/{ps_data.get('n_degraded', 0)}"
        )
    report_lines.append("")

    report_lines.extend([
        "## T3: Surgical Selectivity",
        "",
        f"- Best config SSI: {ssi:.4f}",
        f"- FI reduction: {fi_reduction:.6f}",
        f"- Strong-band loss: {strong_loss:.6f}",
        f"- Layer 1 delta: {l1_delta:.6f}",
        f"- Layer 2 incremental: {l2_delta:.6f}",
        f"- Combined delta: {both_delta:.6f}",
        f"- Synergy: {synergy}",
        "",
        "### Confusion Matrix (MODERATE)",
        "",
    ])
    cm = t3['confusion_matrix'].get('MODERATE', {})
    report_lines.extend([
        f"- TP (counterfeitable correctly starved): {cm.get('TP', 0)}",
        f"- TN (resistant correctly spared): {cm.get('TN', 0)}",
        f"- FP (resistant incorrectly starved): {cm.get('FP', 0)}",
        f"- FN (counterfeitable incorrectly spared): {cm.get('FN', 0)}",
        "",
        "## T4: Landscape Remapping",
        "",
        f"- A2 FORGIVING: {n_forg_ungated} -> {n_forg_gated} "
        f"({pole_reduction:.1f}% reduction)",
        f"- Total FORGIVING: {total_forg_ungated} -> {total_forg_gated}",
        f"- New A1/A3 FORGIVING: {new_a1a3}",
        "",
        "### Transition Matrix",
        "",
        "| From \\ To | STABLE_AMPLIFIER | THRESHOLD_DEPENDENT | FORGIVING_RECIRCULATOR |",
        "|-----------|------------------|--------------------|-----------------------|",
    ])

    tm = t4['transition_matrix']
    for from_cls in ['STABLE_AMPLIFIER', 'THRESHOLD_DEPENDENT', 'FORGIVING_RECIRCULATOR']:
        row = tm.get(from_cls, {})
        report_lines.append(
            f"| {from_cls} | {row.get('STABLE_AMPLIFIER', 0)} | "
            f"{row.get('THRESHOLD_DEPENDENT', 0)} | "
            f"{row.get('FORGIVING_RECIRCULATOR', 0)} |"
        )

    report_lines.extend([
        "",
        "## Tier 3 Interpretation",
        "",
    ])

    if all_validated:
        report_lines.append(
            "> The authentication gate internalizes Phase 574's counterfeit-closure threshold "
            "as an online apparatus parameter. Closure packets earn Y-credit in proportion to "
            "their authentication score — a composite of CTS and configuration-specific "
            "morphological specificity. The two-layer design (credit gating + cleanliness gain "
            "modulation) addresses the coupled R1_C<->R4_C redemption circuit identified in C1643: "
            "fake closure is both starved of reward and denied the 'clean closure' amplification "
            "that legitimate packets earn. Strong closure packets are rewarded normally; weakly "
            "specified closure is discounted. The forgiving pole of the response landscape shrinks "
            "not because A2 parameters change, but because the gate discriminates what counts as "
            "genuine closure success."
        )
    else:
        failing = []
        if c1647_verdict != 'CONFIGURATION_ACS_VALIDATED':
            failing.append(f"C1647={c1647_verdict}")
        if c1648_verdict != 'TWO_LAYER_GATE_SYNERGISTIC':
            failing.append(f"C1648={c1648_verdict}")
        if c1649_verdict != 'STRATIFIED_SELECTIVITY_VALIDATED':
            failing.append(f"C1649={c1649_verdict}")
        if c1650_verdict != 'LANDSCAPE_POLE_REDUCED':
            failing.append(f"C1650={c1650_verdict}")
        report_lines.append(
            f"> Tier 3 interpretation NOT frozen. Non-validated constraints: {', '.join(failing)}. "
            f"The authentication gate shows {'partial' if any('PARTIAL' in v for v in [c1647_verdict, c1648_verdict, c1649_verdict, c1650_verdict]) else 'mixed'} "
            f"effectiveness. Further iteration may be needed."
        )

    report_lines.extend(["", f"*Generated: {datetime.now(timezone.utc).isoformat()}*", ""])

    report_path = os.path.join(PHASE_DIR, 'REPORT_575.md')
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))
    print(f"  Wrote {report_path}")

    # ================================================================
    # Output
    # ================================================================
    output = {
        'metadata': {
            'phase': '575',
            'script': 't5_synthesis.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        'verdicts': verdicts,
        'constraints': constraints,
        'all_validated': all_validated,
        'best_config': best_config,
    }

    out_path = os.path.join(RESULTS_DIR, 't5_synthesis.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")
    print(f"Total elapsed: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
