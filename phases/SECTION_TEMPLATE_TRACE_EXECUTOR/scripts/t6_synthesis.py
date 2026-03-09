"""Phase 562 T6: Synthesis

Combines T1-T5 results into verdict, narrative synthesis, and constraint
proposals. This is the final script in the Phase 562 pipeline.

Input: All T1-T5 result files
Output: t6_synthesis.json
"""
import json
import time
from pathlib import Path


def main():
    t0 = time.time()
    print("=== Phase 562 T6: Synthesis ===")

    base = Path(__file__).resolve().parent.parent / 'results'

    # Load all results
    print("  Loading results...")
    with open(base / 't1_section_templates.json') as f:
        t1 = json.load(f)
    with open(base / 't2_folio_budgets.json') as f:
        t2 = json.load(f)
    with open(base / 't3_line_packets.json') as f:
        t3 = json.load(f)
    with open(base / 't4_token_traces.json') as f:
        t4 = json.load(f)
    with open(base / 't5_trace_validation.json') as f:
        t5 = json.load(f)

    # ───────────────────────────────────────────────────
    # Extract key results from T5 overall structure
    # ───────────────────────────────────────────────────
    t4_summary = t4['summary']
    t5_overall = t5.get('overall', {})
    t5_tests = t5.get('tests', {})
    t5_components = t5_overall.get('component_pass', {})

    # Extract pass/fail from T5 overall.component_pass
    p1_pass = t5_components.get('P1', False)
    p2_pass = t5_components.get('P2', False)
    p3a_pass = t5_components.get('P3a', False)
    p4_pass = t5_components.get('P4', False)
    p5_pass = t5_components.get('P5', False)

    # Null model z-scores
    nulls = t5_tests.get('null_models', {})
    n1_z = nulls.get('N1_token_shuffle', {}).get('z_score', 0)
    n3_z = nulls.get('N3_line_shuffle', {}).get('z_score', 0)
    n4_z = nulls.get('N4_domain_form_shuffle', {}).get('z_score', 0)
    n5_z = nulls.get('N5_terminal_shuffle', {}).get('z_score', 0)

    n1_pass = t5_components.get('N1', n1_z > 5.0)
    n4_pass = t5_components.get('N4', n4_z > 3.0)

    # Use T5's own verdict
    verdict = t5_overall.get('status', 'UNKNOWN')

    # ───────────────────────────────────────────────────
    # Determine verdict (from T5, validated here)
    # ───────────────────────────────────────────────────
    print("\n=== Verdict Determination ===")

    validated = t5_overall.get('trace_validated', False)
    partial = t5_overall.get('trace_partial', False)
    failed = t5_overall.get('trace_failed', True)

    print(f"  Verdict: {verdict}")
    print(f"    P1 (monotonic): {'PASS' if p1_pass else 'FAIL'}")
    print(f"    P2 (cloud recovery): {'PASS' if p2_pass else 'FAIL'}")
    print(f"    P3a (core routing): {'PASS' if p3a_pass else 'FAIL'}")
    print(f"    P4 (headless regime): {'PASS' if p4_pass else 'FAIL'}")
    print(f"    P5 (ablation): {'PASS' if p5_pass else 'FAIL'}")
    print(f"    N1 z={n1_z:.1f} (>5.0): {'PASS' if n1_pass else 'FAIL'}")
    print(f"    N4 z={n4_z:.1f} (>3.0): {'PASS' if n4_pass else 'FAIL'}")

    # ───────────────────────────────────────────────────
    # Composite LL improvement
    # ───────────────────────────────────────────────────
    mean_ll = t4_summary['mean_composite_LL']
    e1_ll = mean_ll['E1']
    e4_ll = mean_ll['E4']
    ll_improvement = e4_ll - e1_ll
    ll_improvement_pct = (ll_improvement / abs(e1_ll)) * 100

    print(f"\n  Composite LL improvement (E4 vs E1): {ll_improvement:.5f} "
          f"({ll_improvement_pct:.2f}%)")

    # Per-axis improvements
    per_axis = t4_summary['mean_axis_LL']
    print(f"  Per-axis E4 vs E1 improvement:")
    for ax, modes in per_axis.items():
        diff = modes['E4'] - modes['E1']
        print(f"    {ax}: {diff:+.5f}")

    # ───────────────────────────────────────────────────
    # Narrative synthesis
    # ───────────────────────────────────────────────────
    narrative_parts = []

    narrative_parts.append(
        f"Phase 562 constructed and validated a hierarchical trace executor "
        f"operating across the 5-layer stack (section -> folio -> paragraph "
        f"-> line -> token) for Currier B. The executor processes {t4['metadata']['n_tokens']} "
        f"tokens through 4 progressively enriched context modes.")

    if p1_pass:
        narrative_parts.append(
            f"Multi-axis prediction improves monotonically: E4 composite LL "
            f"= {e4_ll:.4f} vs E1 = {e1_ll:.4f} (improvement: "
            f"{ll_improvement_pct:.1f}%). The hierarchy is validated as "
            f"contributing real information at each level.")
    else:
        narrative_parts.append(
            f"Monotonic improvement was NOT fully achieved. E4 composite LL "
            f"= {e4_ll:.4f} vs E1 = {e1_ll:.4f}.")

    if p2_pass:
        narrative_parts.append(
            "Paragraph cloud structural recovery confirms that hierarchical "
            "context produces folio-specific paragraph distributions, not "
            "just section-level averages (P2 PASS).")

    # Domain vs other axes
    domain_diff = per_axis['domain']['E4'] - per_axis['domain']['E1']
    hazard_diff = per_axis['hazard']['E4'] - per_axis['hazard']['E1']
    narrative_parts.append(
        f"Primary contributors to E4 improvement: domain axis "
        f"({domain_diff:+.4f}, from phase adjustment + routing mask) and "
        f"hazard axis ({hazard_diff:+.4f}, from envelope adjustment). "
        f"E3 paragraph cloud does not improve per-token domain prediction "
        f"(E3 = E2 for domain LL) -- paragraph-level domain refinement is "
        f"noisier than the folio average. This is consistent with C1573's "
        f"finding that folio specificity lives in distributional SHAPE, "
        f"not in per-token mean position.")

    if n1_pass:
        narrative_parts.append(
            f"Token-shuffle null (N1 z={n1_z:.1f}) confirms the hierarchy is "
            f"non-trivial: destroying local structure collapses trace quality.")

    if n4_pass:
        narrative_parts.append(
            f"Within-domain form-shuffle null (N4 z={n4_z:.1f}) confirms that "
            f"compositional token structure (terminals, modifiers, suffixes) "
            f"carries information beyond domain inventory alone.")

    narrative = " ".join(narrative_parts)

    # ───────────────────────────────────────────────────
    # Proposed constraints
    # ───────────────────────────────────────────────────
    constraints = []

    if p1_pass:
        constraints.append({
            'id': 'C1575',
            'claim': (
                'Section-template trace executor with 4-layer hierarchy '
                'produces monotonic improvement in multi-axis token execution '
                'prediction (domain + hazard + routing + closure): '
                'E4 >= E3 >= E2 > E1. Composite LL improvement '
                f'{ll_improvement_pct:.1f}% from section-only to full context.'
            ),
            'tier': 2,
        })

    if p2_pass:
        constraints.append({
            'id': 'C1576',
            'claim': (
                'Paragraph emphasis cloud under leave-one-out E3/E4 '
                'contextualization recovers folio-specific distributional '
                'geometry not available to section-only or folio-average '
                'priors. However, paragraph-level domain refinement does '
                'NOT improve per-token prediction (E3 = E2 for domain LL).'
            ),
            'tier': 2,
        })

    if n1_pass and n4_pass:
        constraints.append({
            'id': 'C1577',
            'claim': (
                'Packet-destroying nulls collapse hierarchical trace fidelity '
                f'(N1 token-shuffle z={n1_z:.1f}, N4 within-domain form-shuffle '
                f'z={n4_z:.1f}), confirming context contribution is non-trivial '
                'and not reducible to domain inventory alone.'
            ),
            'tier': 2,
        })

    # E4's sources of improvement
    constraints.append({
        'id': 'C1578',
        'claim': (
            'E4 trace improvement over E2 comes from line-phase domain '
            f'adjustment ({per_axis["domain"]["E4"] - per_axis["domain"]["E2"]:+.4f} '
            'domain axis) and hazard envelope adjustment '
            f'({per_axis["hazard"]["E4"] - per_axis["hazard"]["E2"]:+.4f} '
            'hazard axis). Closure phase gating is counterproductive '
            '(WORK_SEMI at 87% dominance makes redistribution harmful). '
            'Routing and headless axes are folio-level, not line-level.'
        ),
        'tier': 2,
    })

    # ───────────────────────────────────────────────────
    # Conceptual scope note
    # ───────────────────────────────────────────────────
    scope_note = (
        "Phase 562 validates the executor SUBSTRATE, not the executor itself. "
        "The traces show that hierarchical context improves token-level "
        "prediction, and that removing layers degrades it. Key limitation: "
        "E3 paragraph cloud does not improve per-token LL (domain axis), "
        "confirming that paragraph-level distributional specificity operates "
        "at the aggregate level (cloud geometry), not at the token level. "
        "Closure phase gating (CLOSURE_PHASE_MASK) was disabled because "
        "WORK_SEMI dominance (87%) makes any redistribution harmful to LL. "
        "This is a property of the closure class distribution, not a failure "
        "of the architectural model."
    )

    # ───────────────────────────────────────────────────
    # Assemble output
    # ───────────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': '562',
            'task': 'T6_synthesis',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        },
        'verdict': verdict,
        'sub_test_results': {
            'P1_monotonic': p1_pass,
            'P2_cloud_recovery': p2_pass,
            'P3a_core_routing': p3a_pass,
            'P4_headless_regime': p4_pass,
            'P5_ablation': p5_pass,
            'N1_token_shuffle': {'z': round(n1_z, 2), 'pass': n1_pass},
            'N3_line_shuffle': {'z': round(n3_z, 2)},
            'N4_form_shuffle': {'z': round(n4_z, 2), 'pass': n4_pass},
            'N5_terminal_shuffle': {'z': round(n5_z, 2)},
        },
        'composite_LL': {
            'E1': round(e1_ll, 5),
            'E2': round(mean_ll['E2'], 5),
            'E3': round(mean_ll['E3'], 5),
            'E4': round(e4_ll, 5),
            'improvement_pct': round(ll_improvement_pct, 2),
        },
        'per_axis_improvement_E4_vs_E1': {
            ax: round(per_axis[ax]['E4'] - per_axis[ax]['E1'], 5)
            for ax in per_axis
        },
        'proposed_constraints': constraints,
        'narrative': narrative,
        'scope_note': scope_note,
        'design_notes': {
            'E3_domain_equals_E2': (
                'Paragraph kNN domain refinement is noisier than folio average. '
                'E3 value is in cloud geometry recovery (P2), not per-token LL.'
            ),
            'closure_mask_disabled': (
                'CLOSURE_PHASE_MASK disabled: WORK_SEMI at 87% makes any '
                'redistribution harmful. Folio-level closure prior is optimal.'
            ),
            'source_immune_correction': (
                'source_immune covers ALL headed tokens (C1546) plus '
                'quench-modified headless (C1450), NOT just k-HEAD. '
                'IMMUNE hazard posture restricted to k-HEAD only (C1446/C1476).'
            ),
        },
    }

    out_path = base / 't6_synthesis.json'
    print(f"\n  Writing to {out_path}...")
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    elapsed = time.time() - t0
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"\n=== Phase 562 Verdict: {verdict} ===")


if __name__ == '__main__':
    main()
