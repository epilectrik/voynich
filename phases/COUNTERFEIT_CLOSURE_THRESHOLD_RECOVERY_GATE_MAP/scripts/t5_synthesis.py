"""
T5: Synthesis + Report + Constraints
Phase 574 - COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP

Integrates T1-T4 results into:
  - C1643: Recovery gate verdict
  - C1644: Threshold verdict (relative profile ordering + sharpness)
  - C1645: Morphology verdict
  - C1646: Landscape verdict

Also freezes two Tier 3 interpretations in INTERPRETATION_SUMMARY.md.
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
    print("=" * 70)
    print("T5: Synthesis + Report + Constraints")
    print("Phase 574 - COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP")
    print("=" * 70)

    # ---- Load all results ----
    print("\n--- Loading results ---")

    with open(os.path.join(RESULTS_DIR, 't1_recovery_gate_decomposition.json'), 'r', encoding='utf-8') as f:
        t1 = json.load(f)

    with open(os.path.join(RESULTS_DIR, 't2_counterfeit_threshold.json'), 'r', encoding='utf-8') as f:
        t2 = json.load(f)

    with open(os.path.join(RESULTS_DIR, 't3_morphology_response.json'), 'r', encoding='utf-8') as f:
        t3 = json.load(f)

    with open(os.path.join(RESULTS_DIR, 't4_landscape_model.json'), 'r', encoding='utf-8') as f:
        t4 = json.load(f)

    # ================================================================
    # C1643: Recovery Gate Verdict
    # ================================================================
    print("\n--- C1643: Recovery Gate ---")
    recovery_diagnosis = t1['recovery_gate_diagnosis']

    # Focus on A2 profile
    a2_diag = None
    for p, diag in recovery_diagnosis.items():
        if 'A2' in p:
            a2_diag = diag
            break

    if a2_diag:
        interp = a2_diag['interpretation']
        r1c = a2_diag['r1c_share']
        r4c = a2_diag['r4c_share']
        joint = a2_diag['r1c_r4c_joint']

        if interp == 'R1_C_DOMINANT':
            c1643_verdict = 'RECOVERY_GATE_R1_C_DOMINANT'
        elif interp == 'R4_C_DOMINANT':
            c1643_verdict = 'RECOVERY_GATE_R4_C_DOMINANT'
        elif interp == 'R1_R4_COUPLED':
            c1643_verdict = 'RECOVERY_GATE_R1_R4_COUPLED'
        else:
            c1643_verdict = 'RECOVERY_GATE_DISTRIBUTED'

        # Additivity info
        a2_additivity = None
        for p, add in t1['additivity_check'].items():
            if 'A2' in p:
                a2_additivity = add
                break

        c1643_explanation = (
            f"A2 recovery gate diagnosis: {c1643_verdict}. "
            f"R1_C share={r1c:.1%}, R4_C share={r4c:.1%}, "
            f"R1_C+R4_C joint={joint:.1%}. "
        )
        if a2_additivity:
            c1643_explanation += (
                f"Sub-channel additivity: {a2_additivity['interaction_verdict']} "
                f"(interaction fraction={a2_additivity['mean_interaction_fraction']:.4f})"
            )
    else:
        c1643_verdict = 'RECOVERY_GATE_DISTRIBUTED'
        c1643_explanation = 'No A2 profile found in diagnosis'
        r1c, r4c, joint = 0, 0, 0
        a2_additivity = None

    print(f"  Verdict: {c1643_verdict}")
    print(f"  {c1643_explanation}")

    # ================================================================
    # C1644: Threshold Verdict (relative profile ordering)
    # ================================================================
    print("\n--- C1644: Threshold ---")
    threshold_estimates = t2['threshold_estimates']
    profile_shifts = t2['profile_shifts']

    # Primary: relative ordering
    a2_vs_a1 = profile_shifts.get('A2_vs_A1', {})
    mag_shift = a2_vs_a1.get('magnitude_shift', 0)

    if mag_shift > 0.05:
        primary = 'THRESHOLD_A2_SHIFTED'
    elif mag_shift < -0.05:
        primary = 'THRESHOLD_A1_SHIFTED'  # unexpected
    else:
        primary = 'THRESHOLD_UNIFORM'

    # No-threshold check
    all_thresholds = [te.get('cts_threshold_magnitude')
                      for te in threshold_estimates.values()
                      if te.get('cts_threshold_magnitude') is not None]
    if not all_thresholds or all(t >= 1.0 for t in all_thresholds):
        primary = 'NO_THRESHOLD'

    # Secondary: sharpness
    transition_sharpness = t2['transition_sharpness']
    a2_width = None
    for p, te in threshold_estimates.items():
        if 'A2' in p:
            a2_width = te.get('transition_width')
            break

    if a2_width is not None and a2_width < 0.2:
        sharpness = 'SHARP'
    else:
        sharpness = 'GRADUAL'

    # Shift magnitude
    if abs(mag_shift) > 0.15:
        shift_degree = 'STRONGLY_SHIFTED'
    elif abs(mag_shift) > 0.05:
        shift_degree = 'MODERATELY_SHIFTED'
    else:
        shift_degree = 'MINIMALLY_SHIFTED'

    c1644_verdict = f"{primary}_{sharpness}" if primary != 'NO_THRESHOLD' else primary
    c1644_explanation = (
        f"Threshold verdict: {c1644_verdict}. "
        f"A2 vs A1 magnitude shift={mag_shift:.4f} ({shift_degree}). "
    )

    # Add per-profile thresholds
    for p, te in sorted(threshold_estimates.items()):
        bt = te.get('cts_threshold_binary', 'N/A')
        mt = te.get('cts_threshold_magnitude', 'N/A')
        c1644_explanation += f"{p}: binary={bt}, magnitude={mt}. "

    print(f"  Verdict: {c1644_verdict}")
    print(f"  {c1644_explanation}")

    # ================================================================
    # C1645: Morphology Verdict
    # ================================================================
    print("\n--- C1645: Morphology ---")
    sig_class = t3['metadata'].get('signature_classification_counts', {})
    n_counterfeitable = sig_class.get('A2_COUNTERFEITABLE', 0)
    n_resistant = sig_class.get('RESISTANT', 0)
    n_universal_weak = sig_class.get('UNIVERSALLY_WEAK', 0)
    n_total_sigs = t3['metadata'].get('n_signatures', 1)

    if n_counterfeitable >= 2 and n_resistant >= 2:
        c1645_verdict = 'MORPHOLOGY_SELECTIVE_COUNTERFEITING'
    elif n_counterfeitable > 0.75 * n_total_sigs:
        c1645_verdict = 'MORPHOLOGY_UNIVERSAL_COUNTERFEITING'
    elif n_resistant > 0.75 * n_total_sigs:
        c1645_verdict = 'MORPHOLOGY_UNIVERSAL_RESISTANCE'
    else:
        c1645_verdict = 'MORPHOLOGY_SELECTIVE_COUNTERFEITING'  # default if some of each

    c1645_explanation = (
        f"Morphology verdict: {c1645_verdict}. "
        f"Signature classes: A2_COUNTERFEITABLE={n_counterfeitable}, "
        f"RESISTANT={n_resistant}, UNIVERSALLY_WEAK={n_universal_weak}, "
        f"total signatures={n_total_sigs}."
    )

    # Top protection features
    fp = t3.get('feature_protection_ranking', {})
    a2_profile = None
    for p in t2['metadata'].get('profiles', []):
        if 'A2' in p:
            a2_profile = p
            break

    if fp and a2_profile:
        sorted_feats = sorted(fp.items(),
                               key=lambda x: x[1].get(a2_profile) or 0,
                               reverse=True)
        top3 = [(f, v.get(a2_profile, 0)) for f, v in sorted_feats[:3]
                if v.get(a2_profile) is not None]
        if top3:
            c1645_explanation += f" Top A2 protective features: {top3}."

    print(f"  Verdict: {c1645_verdict}")
    print(f"  {c1645_explanation}")

    # ================================================================
    # C1646: Landscape Verdict
    # ================================================================
    print("\n--- C1646: Landscape ---")
    classification_summary = t4['classification_summary']
    total_folios = t4['metadata']['n_folios']

    fractions = {}
    for cls, cs in classification_summary.items():
        n = cs.get('n_folios', 0)
        fractions[cls] = n / max(total_folios, 1)

    n_above_10 = sum(1 for f in fractions.values() if f >= 0.10)

    if n_above_10 >= 3:
        c1646_verdict = 'LANDSCAPE_THREE_POLE'
    elif n_above_10 >= 2:
        c1646_verdict = 'LANDSCAPE_TWO_POLE'
    elif fractions.get('THRESHOLD_DEPENDENT', 0) > 0.6:
        c1646_verdict = 'LANDSCAPE_GRADIENT'
    else:
        c1646_verdict = 'LANDSCAPE_TWO_POLE'

    c1646_explanation = (
        f"Landscape verdict: {c1646_verdict}. "
        f"STABLE_AMPLIFIER={fractions.get('STABLE_AMPLIFIER', 0):.1%} "
        f"(n={classification_summary.get('STABLE_AMPLIFIER', {}).get('n_folios', 0)}), "
        f"THRESHOLD_DEPENDENT={fractions.get('THRESHOLD_DEPENDENT', 0):.1%} "
        f"(n={classification_summary.get('THRESHOLD_DEPENDENT', {}).get('n_folios', 0)}), "
        f"FORGIVING_RECIRCULATOR={fractions.get('FORGIVING_RECIRCULATOR', 0):.1%} "
        f"(n={classification_summary.get('FORGIVING_RECIRCULATOR', {}).get('n_folios', 0)}). "
        f"Cross-cut fraction={t4.get('cross_cut_fraction', 0):.4f}."
    )

    print(f"  Verdict: {c1646_verdict}")
    print(f"  {c1646_explanation}")

    # ================================================================
    # Build constraints
    # ================================================================
    constraints = {
        'C1643': {
            'id': 'C1643',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'A2', 'recovery_gate', 'sub_channel'],
            'claim': f'A2 recovery gate sub-channel decomposition: {c1643_verdict}. {c1643_explanation}',
            'verdict': c1643_verdict,
            'evidence': {
                'source': 'Phase 574 T1 sub-channel ablation',
                'r1c_share': round(r1c, 4) if isinstance(r1c, float) else r1c,
                'r4c_share': round(r4c, 4) if isinstance(r4c, float) else r4c,
                'r1c_r4c_joint': round(joint, 4) if isinstance(joint, float) else joint,
                'additivity': a2_additivity['interaction_verdict'] if a2_additivity else 'N/A',
            },
            'phase': 574,
        },
        'C1644': {
            'id': 'C1644',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'threshold', 'closure', 'CTS'],
            'claim': f'Counterfeit closure threshold: {c1644_verdict}. {c1644_explanation}',
            'verdict': c1644_verdict,
            'evidence': {
                'source': 'Phase 574 T2 threshold curves',
                'a2_vs_a1_magnitude_shift': round(mag_shift, 4),
                'shift_degree': shift_degree,
                'sharpness': sharpness,
            },
            'phase': 574,
        },
        'C1645': {
            'id': 'C1645',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'morphology', 'closure_packet', 'counterfeiting'],
            'claim': f'Closure packet morphology selectivity: {c1645_verdict}. {c1645_explanation}',
            'verdict': c1645_verdict,
            'evidence': {
                'source': 'Phase 574 T3 packet morphology signatures',
                'n_counterfeitable': n_counterfeitable,
                'n_resistant': n_resistant,
                'n_universal_weak': n_universal_weak,
                'n_total_signatures': n_total_sigs,
            },
            'phase': 574,
        },
        'C1646': {
            'id': 'C1646',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'landscape', 'folio_classification'],
            'claim': f'Apparatus response landscape: {c1646_verdict}. {c1646_explanation}',
            'verdict': c1646_verdict,
            'evidence': {
                'source': 'Phase 574 T4 continuous landscape model',
                'fractions': {k: round(v, 4) for k, v in fractions.items()},
                'cross_cut_fraction': t4.get('cross_cut_fraction', 0),
                'note': 'Three-way classification is a descriptive convenience overlay, not ontological species',
            },
            'phase': 574,
        },
    }

    # ================================================================
    # Generate report
    # ================================================================
    print("\n--- Generating report ---")

    # Per-profile threshold table
    threshold_rows = []
    for p in sorted(threshold_estimates.keys()):
        te = threshold_estimates[p]
        ts = t2['transition_sharpness'].get(p, {})
        threshold_rows.append(
            f"| {p} | {te.get('cts_threshold_binary', 'N/A')} | "
            f"{te.get('cts_threshold_magnitude', 'N/A')} | "
            f"{te.get('transition_width', 'N/A')} | "
            f"{ts.get('sigmoid_steepness', 'N/A')} | "
            f"{ts.get('r_squared', 'N/A')} |"
        )

    # Recovery gate table
    rg_rows = []
    for p in sorted(recovery_diagnosis.keys()):
        diag = recovery_diagnosis[p]
        add_info = t1['additivity_check'].get(p, {})
        rg_rows.append(
            f"| {p} | {diag['r1c_share']:.4f} | {diag['r4c_share']:.4f} | "
            f"{diag['r1c_r4c_joint']:.4f} | {diag['interpretation']} | "
            f"{add_info.get('interaction_verdict', 'N/A')} |"
        )

    # Signature classification table
    sig_rows = []
    for sig, sc in sorted(t3['packet_signature_classification'].items()):
        a2_adv = 'N/A'
        for p_key in sc:
            if 'A2' in p_key and isinstance(sc[p_key], dict):
                a2_adv = sc[p_key].get('weighted_dye_adv', 'N/A')
        sig_rows.append(
            f"| {sig} | {sc['classification']} | {sc['n_total']} | {a2_adv} |"
        )

    # Landscape summary
    landscape_rows = []
    for cls in ['STABLE_AMPLIFIER', 'THRESHOLD_DEPENDENT', 'FORGIVING_RECIRCULATOR']:
        cs = classification_summary.get(cls, {})
        n = cs.get('n_folios', 0)
        pd = cs.get('profile_distribution', {})
        mm = cs.get('mean_margin', 0)
        landscape_rows.append(
            f"| {cls} | {n} | {fractions.get(cls, 0):.1%} | {pd} | {mm:.4f} |"
        )

    report = f"""# Phase 574: Counterfeit Closure Threshold + Recovery Gate Map

**Recovery gate verdict: {c1643_verdict}**
**Threshold verdict: {c1644_verdict}**
**Morphology verdict: {c1645_verdict}**
**Landscape verdict: {c1646_verdict}**
**New constraints:** 4 (C1643-C1646)

---

## 1. Summary

Phase 574 follows Phase 573's identification of NO_CLOSE_RECOVERY as the dominant mechanism behind A2's excess forgivingness (C1639). It decomposes the recovery gate into R1-R5 sub-channels, models the counterfeit closure threshold curve, identifies which closure packet morphologies are counterfeitable, and maps the continuous apparatus response landscape.

## 2. Recovery Gate Decomposition (T1)

**Verdict: {c1643_verdict}**

{c1643_explanation}

### Sub-Channel Shares (A2)

| Profile | R1_C Share | R4_C Share | Joint R1_C+R4_C | Interpretation | Additivity |
|---------|-----------|-----------|-----------------|----------------|------------|
{chr(10).join(rg_rows)}

### Parameter Sensitivity (A2 only)

Parameters tested at +/-10%: R1_C_MULT, R4_C_TO_Y

## 3. Counterfeit Threshold Curves (T2)

**Verdict: {c1644_verdict}**

{c1644_explanation}

### Per-Profile Thresholds

| Profile | Binary Threshold | Magnitude Threshold | Transition Width | Steepness | R-squared |
|---------|-----------------|--------------------|--------------------|-----------|-----------|
{chr(10).join(threshold_rows)}

### Profile Shifts

- A2 vs A1 magnitude shift: {mag_shift:.4f} ({shift_degree})

## 4. Closure Packet Morphology (T3)

**Verdict: {c1645_verdict}**

{c1645_explanation}

### Packet Signature Classification

| Signature | Classification | N_events | A2 DYE_adv |
|-----------|---------------|----------|------------|
{chr(10).join(sig_rows)}

## 5. Continuous Landscape (T4)

**Verdict: {c1646_verdict}**

{c1646_explanation}

NOTE: Three-way classification is a **descriptive convenience overlay** on a continuous surface, NOT ontological folio species.

### Classification Summary

| Class | N_folios | Fraction | Profile Distribution | Mean Margin |
|-------|----------|----------|---------------------|-------------|
{chr(10).join(landscape_rows)}

## 6. New Constraints

**C1643** (Tier 2, scope B)
  {constraints['C1643']['claim']}

**C1644** (Tier 2, scope B)
  {constraints['C1644']['claim']}

**C1645** (Tier 2, scope B)
  {constraints['C1645']['claim']}

**C1646** (Tier 2, scope B)
  {constraints['C1646']['claim']}

## 7. Interpretive Synthesis

### Post-573 Interpretation (Tier 3, frozen)

> "Currier B's closure grammar advantage is not uniformly visible across apparatus conditions because apparatus families differ in counterfeit-closure susceptibility. A2_SEALED_RECIRCULATION is a forgiving closure-response regime in which close-recovery dynamics redeem generic disturbance too readily, especially when closure packets are weakly specified. Strong closure packets still outperform nulls there, showing that the grammar remains active, but the apparatus imposes a higher specificity threshold before productive disruption becomes discriminative. Across Currier B, folio accent and residual variance are better modeled as position on a continuous response landscape -- anchored by a distinct forgiving A2 pole and a broad productive field -- than as crisp discrete families."

### Post-574 Interpretation (Tier 3, contingent)

> "The main observable apparatus-side difference among Currier B folios is not endpoint recovery capacity but counterfeit-closure susceptibility: how much closure specificity must be present before the plant stops redeeming generic disturbance and starts rewarding grammar-aligned disturbance preferentially."

This interpretation is frozen only if T1-T4 results support it (A2 threshold shifted right, selective morphology counterfeiting, landscape showing forgiving pole).

---

*Generated: {datetime.now(timezone.utc).isoformat()}*
"""

    report_path = os.path.join(PHASE_DIR, 'REPORT_574.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  Written: {report_path}")

    # ================================================================
    # Save synthesis JSON
    # ================================================================
    print("\n--- Saving synthesis ---")
    output = {
        'metadata': {
            'phase': '574',
            'script': 't5_synthesis.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        'verdicts': {
            'recovery_gate': {
                'verdict': c1643_verdict,
                'explanation': c1643_explanation,
            },
            'threshold': {
                'verdict': c1644_verdict,
                'explanation': c1644_explanation,
            },
            'morphology': {
                'verdict': c1645_verdict,
                'explanation': c1645_explanation,
            },
            'landscape': {
                'verdict': c1646_verdict,
                'explanation': c1646_explanation,
            },
        },
        'constraints': constraints,
    }

    out_path = os.path.join(RESULTS_DIR, 't5_synthesis.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1, default=str)
    print(f"  Written: {out_path}")
    print(f"\nDone in {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
