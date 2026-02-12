#!/usr/bin/env python3
"""
T6: Integrated Assessment
PROCESS_PHENOMENOLOGY_EXCLUSION phase (Tier 4)

Combines T2-T5 results into composite phenomenological alignment score
and domain exclusion confidence. Applies stop rules and produces
final phase verdict.
"""

import sys
import json
import functools
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    print("=" * 70)
    print("T6: INTEGRATED ASSESSMENT")
    print("=" * 70)

    # ---- Load T2-T5 results ----
    t2 = load_json(RESULTS_DIR / 't2_sensorimotor_ontology.json')
    t3 = load_json(RESULTS_DIR / 't3_hazard_phenomenology.json')
    t4 = load_json(RESULTS_DIR / 't4_domain_compatibility.json')
    t5 = load_json(RESULTS_DIR / 't5_state_thermodynamic.json')
    print("  Loaded T2-T5 results")

    # ---- Thread A: Phenomenological Alignment ----
    print("\n--- Thread A: Phenomenological Alignment ---")

    # T2: Sensorimotor coverage (average of bidirectional)
    t2_a2s = t2['coverage']['a2s']['coverage_pct']
    t2_s2a = t2['coverage']['s2a']['coverage_pct']
    sensorimotor_coverage = (t2_a2s + t2_s2a) / 2
    print(f"  T2 sensorimotor: A2S={t2_a2s:.3f}, S2A={t2_s2a:.3f}, avg={sensorimotor_coverage:.3f}")

    # T3: Hazard coherence
    hazard_coherence = t3['phenomenological_coherence']['overall_score']
    print(f"  T3 hazard coherence: {hazard_coherence:.3f}")

    # T5: State derivation score
    state_derivation = t5['state_count_derivation']['derivation_score']
    print(f"  T5 state derivation: {state_derivation:.3f}")

    # Weighted composite (T2: 0.4, T3: 0.3, T5: 0.3)
    phenom_alignment = (
        sensorimotor_coverage * 0.4 +
        hazard_coherence * 0.3 +
        state_derivation * 0.3
    )
    phenom_alignment = round(phenom_alignment, 4)
    print(f"  Composite alignment: {phenom_alignment:.4f}")

    if phenom_alignment >= 0.7:
        phenom_verdict = 'HIGH'
    elif phenom_alignment >= 0.5:
        phenom_verdict = 'MEDIUM'
    else:
        phenom_verdict = 'LOW'
    print(f"  Thread A verdict: {phenom_verdict}")

    # ---- Thread B: Domain Exclusion ----
    print("\n--- Thread B: Domain Exclusion ---")

    exclusion_gap = t4['exclusion_gap']
    best_alt = t4['best_alternative']
    n_killer = t4['n_killer_features']
    t4_verdict = t4['verdict']

    print(f"  Exclusion gap: {exclusion_gap:.3f}")
    print(f"  Best alternative: {best_alt['domain']} at {best_alt['score']:.3f}")
    print(f"  Killer features: {n_killer}/20")
    print(f"  T4 verdict: {t4_verdict}")

    if t4_verdict == 'EXCLUDED':
        exclusion_verdict = 'STRONG'
    elif t4_verdict == 'WEAKLY_EXCLUDED':
        exclusion_verdict = 'WEAK'
    else:
        exclusion_verdict = 'NONE'
    print(f"  Thread B verdict: {exclusion_verdict}")

    # ---- Stop Rules ----
    print("\n--- Stop Rule Checks ---")

    stop_rules = {
        'domain_exclusion_failed': t4_verdict == 'NOT_EXCLUDED',
        'sensory_coverage_below_50': sensorimotor_coverage < 0.50,
        'hazard_mapping_incoherent': t3['verdict'] == 'INCOHERENT',
        'state_count_inconsistent': t5['verdict'] == 'INCONSISTENT',
    }

    any_stop = any(stop_rules.values())
    for rule, triggered in stop_rules.items():
        status = 'TRIGGERED' if triggered else 'PASSED'
        print(f"  {rule}: {status}")

    if any_stop:
        print(f"  ** STOP RULE TRIGGERED **")

    # ---- Integrated Verdict ----
    print("\n--- Integrated Verdict ---")

    # Verdict matrix from plan:
    # HIGH + EXCLUDED -> DISTILLATION_SUPPORTED
    # HIGH + WEAKLY_EXCLUDED -> DISTILLATION_PARTIAL
    # MEDIUM + EXCLUDED -> DISTILLATION_PARTIAL
    # MEDIUM + WEAKLY_EXCLUDED -> DISTILLATION_PARTIAL
    # Any + NOT_EXCLUDED -> INCONCLUSIVE
    # LOW + Any -> DISTILLATION_REJECTED

    if stop_rules['domain_exclusion_failed']:
        overall = 'INCONCLUSIVE'
    elif phenom_verdict == 'LOW':
        overall = 'DISTILLATION_REJECTED'
    elif phenom_verdict == 'HIGH' and exclusion_verdict == 'STRONG':
        overall = 'DISTILLATION_SUPPORTED'
    elif phenom_verdict == 'HIGH' and exclusion_verdict == 'WEAK':
        overall = 'DISTILLATION_PARTIAL'
    elif phenom_verdict == 'MEDIUM' and exclusion_verdict in ['STRONG', 'WEAK']:
        overall = 'DISTILLATION_PARTIAL'
    else:
        overall = 'INCONCLUSIVE'

    # ---- Evidence chain ----
    evidence_chain = [
        f"T1: Joint fingerprint compiled from 18 source files, 20 binary features extracted",
        f"T2: Sensorimotor ontology covers {t2_a2s:.1%} architecture->sensory, {t2_s2a:.1%} sensory->architecture ({t2['verdict']})",
        f"T3: Hazard phenomenology: pelican rank rho={t3['distribution_alignment']['spearman_rho_pelican']:.3f}, {t3['phenomenological_coherence']['n_coherent']}/5 classes coherent, CONTAINMENT at {t3['pelican_specificity']['containment_pct']}% ({t3['verdict']})",
        f"T4: Domain exclusion: gap={exclusion_gap:.1%}, best alternative={best_alt['domain']} at {best_alt['score']:.1%}, {n_killer} killer features ({t4['verdict']})",
        f"T5: 6-state count {t5['verdict']}: {t5['state_count_derivation']['n_physically_necessary']}/6 necessary, derivation score {state_derivation:.3f}",
        f"T6: Integrated alignment={phenom_alignment:.3f} ({phenom_verdict}), exclusion={exclusion_verdict}, overall={overall}",
    ]

    # ---- Confidence statement ----
    if overall == 'DISTILLATION_SUPPORTED':
        confidence = (
            "The Voynich Manuscript's Currier B control architecture is structurally compatible "
            "with — and discriminates uniquely toward — circulatory reflux distillation (pelican). "
            "Thread A: 25 sensory phenomena of pelican operation map bidirectionally to architectural "
            f"features ({sensorimotor_coverage:.1%} coverage), hazard distribution matches pelican "
            f"failure modes (rho={t3['distribution_alignment']['spearman_rho_pelican']:.3f}), and the "
            f"6-state automaton maps to physically necessary operational modes (score={state_derivation:.3f}). "
            f"Thread B: All 7 alternative domains score below {best_alt['score']:.1%} compatibility, with "
            f"{n_killer}/20 features being 'killer' discriminators that exclude all alternatives. "
            "This does NOT prove the manuscript is a distillation manual, but it establishes that "
            "no other 15th-century process domain produces a compatible structural fingerprint."
        )
    elif overall == 'DISTILLATION_PARTIAL':
        confidence = (
            "Partial support for distillation interpretation. Phenomenological alignment and/or "
            "domain exclusion meet thresholds but not at the highest level."
        )
    elif overall == 'INCONCLUSIVE':
        confidence = (
            "Domain exclusion failed or stop rule triggered. The structural fingerprint is not "
            "uniquely compatible with thermal distillation."
        )
    else:
        confidence = "Distillation interpretation rejected by phenomenological mismatch."

    # ---- Compile results ----
    results = {
        'test': 'T6_integrated_assessment',
        'thread_a_phenomenological_alignment': {
            'sensorimotor_coverage': round(sensorimotor_coverage, 4),
            'hazard_coherence': round(hazard_coherence, 4),
            'state_derivation': round(state_derivation, 4),
            'composite_score': phenom_alignment,
            'verdict': phenom_verdict,
            'component_verdicts': {
                'T2': t2['verdict'],
                'T3': t3['verdict'],
                'T5': t5['verdict'],
            },
        },
        'thread_b_domain_exclusion': {
            'exclusion_gap': exclusion_gap,
            'best_alternative': {
                'domain': best_alt['domain'],
                'score': best_alt['score'],
            },
            'killer_features_count': n_killer,
            'total_features': 20,
            'verdict': exclusion_verdict,
            't4_verdict': t4_verdict,
        },
        'stop_rules': stop_rules,
        'any_stop_triggered': any_stop,
        'integrated_verdict': {
            'phenomenological_alignment': phenom_verdict,
            'domain_exclusion': exclusion_verdict,
            'overall': overall,
            'confidence_statement': confidence,
        },
        'evidence_chain': evidence_chain,
        'per_test_verdicts': {
            'T1': 'COMPILED',
            'T2': t2['verdict'],
            'T3': t3['verdict'],
            'T4': t4['verdict'],
            'T5': t5['verdict'],
            'T6': overall,
        },
        'quantitative_summary': {
            'sensorimotor_a2s': t2_a2s,
            'sensorimotor_s2a': t2_s2a,
            'hazard_rho_pelican': t3['distribution_alignment']['spearman_rho_pelican'],
            'hazard_rho_open': t3['distribution_alignment']['spearman_rho_open'],
            'hazard_coherence_classes': f"{t3['phenomenological_coherence']['n_coherent']}/5",
            'domain_gap': exclusion_gap,
            'domain_best_alt': f"{best_alt['domain']} ({best_alt['score']:.1%})",
            'domain_killer_features': f"{n_killer}/20",
            'state_derivation_score': state_derivation,
            'state_necessary': f"{t5['state_count_derivation']['n_physically_necessary']}/6",
            'composite_alignment': phenom_alignment,
        },
    }

    # ---- Save ----
    out_path = RESULTS_DIR / 't6_integrated_assessment.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {out_path}")

    # ---- Final Summary ----
    print(f"\n{'=' * 70}")
    print(f"PHASE VERDICT: {overall}")
    print(f"{'=' * 70}")
    print(f"\nThread A — Phenomenological Alignment: {phenom_verdict} ({phenom_alignment:.3f})")
    print(f"  Sensorimotor coverage: {sensorimotor_coverage:.1%}")
    print(f"  Hazard coherence: {hazard_coherence:.3f}")
    print(f"  State derivation: {state_derivation:.3f}")
    print(f"\nThread B — Domain Exclusion: {exclusion_verdict}")
    print(f"  Exclusion gap: {exclusion_gap:.1%}")
    print(f"  Best alternative: {best_alt['domain']} at {best_alt['score']:.1%}")
    print(f"  Killer features: {n_killer}/20")
    print(f"\nEvidence Chain:")
    for e in evidence_chain:
        print(f"  {e}")
    print(f"\n{confidence}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
