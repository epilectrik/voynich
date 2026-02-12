"""
T5: Integrated Verdict
=======================
Phase: PP_INFORMATION_DECOMPOSITION

Loads T1-T4 results and synthesizes into a verdict on PP information
architecture.

Verdict categories:
  PREFIX_POSITIONAL_OPERATOR  - PREFIX is primarily a positional grammar marker
  DUAL_ENCODING              - PREFIX encodes both position and content
  MIDDLE_DOMINANT             - MIDDLE carries primary information, PREFIX secondary
  INDEPENDENT_CHANNELS        - PREFIX and MIDDLE encode orthogonal dimensions

Output: t5_integrated_verdict.json
"""

import json
import functools
from pathlib import Path

print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def main():
    # ── Load all results ─────────────────────────────────
    with open(RESULTS_DIR / 't1_conditional_mi_decomposition.json') as f:
        t1 = json.load(f)
    with open(RESULTS_DIR / 't2_prefix_positional_grammar.json') as f:
        t2 = json.load(f)
    with open(RESULTS_DIR / 't3_prefix_sequential_grammar.json') as f:
        t3 = json.load(f)
    with open(RESULTS_DIR / 't4_prefix_regime_positional_stability.json') as f:
        t4 = json.load(f)

    # ── Score each dimension ─────────────────────────────
    scores = {}

    # D1: Information decomposition (T1)
    t1_targets = t1['targets']
    sig_targets = t1['significant_targets']
    avg_dom = t1['avg_prefix_dominance']
    pos_result = t1_targets.get('POSITION', {})
    pos_dom = pos_result.get('prefix_dominance', 0.5)

    d1_score = 0.0
    if sig_targets >= 3:
        d1_score += 0.5
    if pos_dom > 0.45:  # PREFIX dominant or co-equal for position
        d1_score += 0.5
    scores['information_decomposition'] = {
        'score': d1_score,
        'evidence': (f"{sig_targets}/4 targets significant, "
                     f"avg PREFIX dominance={avg_dom:.1%}, "
                     f"POSITION dominance={pos_dom:.1%}"),
        'verdict': t1['verdict'],
    }

    # D2: Positional grammar (T2)
    t2_verdict = t2['verdict']
    r2_pre = t2['variance_decomposition']['r2_prefix']
    r2_mid = t2['variance_decomposition']['r2_middle']
    r2_pp = t2['variance_decomposition']['r2_pp']
    r2_interaction = t2['variance_decomposition']['r2_interaction']
    eta_sq = t2['kruskal_wallis']['eta_sq']

    d2_score = 0.0
    if eta_sq > 0.02:
        d2_score += 0.33
    if r2_pre > 0.01:
        d2_score += 0.33
    if r2_interaction > 0.01:
        d2_score += 0.34

    scores['positional_grammar'] = {
        'score': d2_score,
        'evidence': (f"KW eta²={eta_sq:.4f}, R²(PREFIX)={r2_pre:.4f}, "
                     f"R²(MIDDLE)={r2_mid:.4f}, R²(PP)={r2_pp:.4f}, "
                     f"Interaction={r2_interaction:.4f}"),
        'verdict': t2_verdict,
    }

    # D3: Sequential grammar (T3)
    t3_verdict = t3['verdict']
    t3_v = t3['transition_matrix']['cramers_v']
    t3_forbidden = len(t3['forbidden_transitions'])
    t3_enriched = len(t3['enriched_transitions'])
    t3_mi = t3['sequential_mi']['prefix_to_prefix']
    t3_mid_mi = t3['sequential_mi']['middle_to_middle']
    t3_ratio = t3['sequential_mi']['seq_ratio']

    d3_score = 0.0
    if t3_v > 0.1:
        d3_score += 0.33
    if t3_forbidden >= 3:
        d3_score += 0.33
    if t3_ratio > 0.3:
        d3_score += 0.34

    scores['sequential_grammar'] = {
        'score': d3_score,
        'evidence': (f"Cramér's V={t3_v:.4f}, "
                     f"forbidden={t3_forbidden}, enriched={t3_enriched}, "
                     f"PREFIX MI={t3_mi:.4f}, MIDDLE MI={t3_mid_mi:.4f}, "
                     f"ratio={t3_ratio:.3f}"),
        'verdict': t3_verdict,
    }

    # D4: Stability (T4)
    t4_verdict = t4['verdict']
    n_stable = t4['n_stable']
    n_tested = t4['n_tested']
    n_consistent = t4['n_consistent']
    n_tested_fc = t4['n_tested_folio']
    stability_pct = n_stable / n_tested if n_tested > 0 else 0

    d4_score = 0.0
    if stability_pct >= 0.6:
        d4_score += 0.5
    elif stability_pct >= 0.3:
        d4_score += 0.25
    if n_tested_fc > 0 and n_consistent / n_tested_fc >= 0.5:
        d4_score += 0.5
    elif n_tested_fc > 0 and n_consistent / n_tested_fc >= 0.3:
        d4_score += 0.25

    scores['positional_stability'] = {
        'score': d4_score,
        'evidence': (f"Regime-stable: {n_stable}/{n_tested} "
                     f"({stability_pct:.1%}), "
                     f"Folio-consistent: {n_consistent}/{n_tested_fc}"),
        'verdict': t4_verdict,
    }

    # ── Overall verdict ──────────────────────────────────
    total_score = sum(s['score'] for s in scores.values())
    high_dims = sum(1 for s in scores.values() if s['score'] >= 0.5)

    # Determine architecture type
    pos_is_strong = (scores['positional_grammar']['score'] >= 0.5 and
                     scores['positional_stability']['score'] >= 0.5)
    seq_is_strong = scores['sequential_grammar']['score'] >= 0.5
    info_is_significant = scores['information_decomposition']['score'] >= 0.5

    if pos_is_strong and seq_is_strong and info_is_significant:
        verdict = 'PREFIX_POSITIONAL_OPERATOR'
        detail = (f'PREFIX functions as a positional grammar operator: '
                  f'it encodes line position (T2), follows sequential rules (T3), '
                  f'is regime-stable (T4), and adds significant unique '
                  f'information (T1). Score: {total_score:.2f}/4.0.')
    elif pos_is_strong and info_is_significant:
        verdict = 'DUAL_ENCODING'
        detail = (f'PREFIX encodes both positional grammar and content: '
                  f'strong positional profiles (T2), stable across regimes (T4), '
                  f'with unique information on multiple targets (T1). '
                  f'Score: {total_score:.2f}/4.0.')
    elif total_score < 1.0:
        verdict = 'MIDDLE_DOMINANT'
        detail = (f'MIDDLE carries the primary information. PREFIX shows '
                  f'little independent structure. Score: {total_score:.2f}/4.0.')
    else:
        verdict = 'INDEPENDENT_CHANNELS'
        detail = (f'PREFIX and MIDDLE encode partially independent dimensions. '
                  f'{high_dims}/4 dimensions show significant structure. '
                  f'Score: {total_score:.2f}/4.0.')

    # ── Print ────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"T5 PP INFORMATION DECOMPOSITION VERDICT")
    print(f"{'='*70}")
    print(f"\nVERDICT: {verdict}")
    print(f"  {detail}")
    print(f"\nDIMENSION SCORES:")
    for dim, data in scores.items():
        bar = '#' * int(data['score'] * 10) + '.' * (10 - int(data['score'] * 10))
        print(f"  {dim:<28s}: [{bar}] {data['score']:.2f}")
        print(f"    {data['evidence']}")

    # Key architectural findings
    print(f"\nARCHITECTURAL SUMMARY:")
    print(f"  Total score: {total_score:.2f}/4.0")
    print(f"  High dimensions: {high_dims}/4")

    # Print T1 key numbers
    print(f"\n  T1 (Information):")
    for target, r in t1['targets'].items():
        print(f"    {target}: PREFIX dom={r['prefix_dominance']:.1%}, "
              f"sig={r['significant']}")

    # Print T2 key numbers
    print(f"\n  T2 (Positional):")
    print(f"    R²: PREFIX={r2_pre:.4f}, MIDDLE={r2_mid:.4f}, "
          f"PP={r2_pp:.4f}, Interaction={r2_interaction:.4f}")

    # Print T3 key numbers
    print(f"\n  T3 (Sequential):")
    print(f"    PREFIX MI={t3_mi:.4f}, MIDDLE MI={t3_mid_mi:.4f}, "
          f"ratio={t3_ratio:.3f}")
    print(f"    Forbidden={t3_forbidden}, Enriched={t3_enriched}")

    # Print T4 key numbers
    print(f"\n  T4 (Stability):")
    print(f"    Regime-stable: {n_stable}/{n_tested}")
    print(f"    Folio-consistent: {n_consistent}/{n_tested_fc}")

    # ── Output ───────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'PP_INFORMATION_DECOMPOSITION',
            'test': 'T5_INTEGRATED_VERDICT',
        },
        'dimension_scores': scores,
        'total_score': total_score,
        'high_dimensions': high_dims,
        'verdict': verdict,
        'verdict_detail': detail,
    }

    out_path = RESULTS_DIR / 't5_integrated_verdict.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
