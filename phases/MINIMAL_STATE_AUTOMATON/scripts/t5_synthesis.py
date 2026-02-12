#!/usr/bin/env python3
"""
T5: Synthesis — Minimal State Automaton Assessment
MINIMAL_STATE_AUTOMATON phase
"""

import sys
import json
import functools
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def run():
    print("=" * 70)
    print("T5: Synthesis — Minimal State Automaton")
    print("MINIMAL_STATE_AUTOMATON phase")
    print("=" * 70)

    # Load all results
    with open(RESULTS_DIR / 't2_spectral.json') as f:
        t2 = json.load(f)
    with open(RESULTS_DIR / 't3_merged_automaton.json') as f:
        t3 = json.load(f)
    with open(RESULTS_DIR / 't4_synthetic.json') as f:
        t4 = json.load(f)

    # 1. Effective Dimensionality
    print("\n[1/5] Spectral Dimensionality")
    print(f"  Spectral gap suggests: {t2['spectral_gap']['suggested_states']} effective states")
    print(f"  Effective rank (>0.01): {t2['effective_rank']['0.01']}")
    print(f"  NMF elbow: k={t2['nmf_elbow']}")
    print(f"  Role-level rank: {t2['role_effective_rank']}")
    print(f"")
    print(f"  Interpretation: The transition matrix has HIGH information content")
    print(f"  ({t2['effective_rank']['0.01']} significant eigenvalues out of 49) but")
    print(f"  most of that information is 'texture' — variation within structurally")
    print(f"  equivalent groups, not between them.")

    # 2. Minimum State Count
    print(f"\n[2/5] Constraint-Preserving Compression")
    print(f"  Starting: {t3['n_classes']} classes")
    print(f"  Minimum: {t3['n_final_states']} states")
    print(f"  Compression: {t3['compression_ratio']}x")
    print(f"  Valid merges: {t3['n_merges']}")
    print(f"")
    print(f"  The 6 states are:")
    for sd in t3['state_descriptions']:
        cls_str = str(sd['classes']) if sd['n_classes'] <= 6 else f"({sd['n_classes']} classes)"
        print(f"    S{sd['state_id']}: {'/'.join(sd['roles']):>8} {cls_str:>30} "
              f"freq={sd['frequency_fraction']:.1%}")

    # 3. Binding Constraints
    print(f"\n[3/5] Binding Constraints (what prevents further compression)")
    for ctype, count in sorted(t3['binding_type_counts'].items(), key=lambda x: -x[1]):
        print(f"    {ctype}: {count} blocked merges")
    print(f"")
    print(f"  The 6 states cannot be reduced to 5 because:")
    print(f"  - ROLE integrity blocks: CC/FQ/FL cannot merge with EN/AX")
    print(f"  - DEPLETION asymmetry blocks: merging the two EN/AX groups")
    print(f"    would collapse depleted pairs into self-transitions")

    # 4. Generative Fidelity
    print(f"\n[4/5] Generative Fidelity")
    print(f"  Verdict: {t4['generation_verdict']}")
    print(f"  Fidelity: {t4['fidelity']:.0%} ({sum(1 for v in t4['comparison'].values() if v['match'])}/5 metrics)")
    print(f"")
    for metric, comp in t4['comparison'].items():
        status = "MATCH" if comp['match'] else "MISS"
        print(f"    {metric:>20}: real={comp['real']:>8.3f}  syn={comp['syn_mean']:>8.3f}  "
              f"z={comp['z_score']:>+5.1f}  [{status}]")

    # 5. Final Assessment
    print(f"\n[5/5] Final Assessment")
    print(f"{'='*70}")

    n_states = t3['n_final_states']
    if n_states <= 8:
        verdict = "COMPRESSIBLE"
    elif n_states <= 15:
        verdict = "MODERATELY_COMPLEX"
    else:
        verdict = "INCOMPRESSIBLE"

    print(f"\n  VERDICT: {verdict}")
    print(f"  The Voynich B grammar compresses to {n_states} latent states.")
    print(f"")
    print(f"  STRUCTURAL INTERPRETATION:")
    print(f"")
    print(f"  State 0 (FL_HAZ, 6%): Hazard flow markers — directional risk indexing")
    print(f"  State 1 (FQ, 18%):    Frequent operators — high-frequency scaffolding")
    print(f"  State 2 (CC, 5%):     Core control — daiin/ol/k execution primitives")
    print(f"  State 3 (AX/EN minor, 3%): Secondary execution — transitionally distinct")
    print(f"  State 4 (AX/EN major, 68%): Primary execution — the dominant operational mass")
    print(f"  State 5 (FL_SAFE, 1%): Safe flow markers — non-hazard progression")
    print(f"")
    print(f"  KEY FINDINGS:")
    print(f"")
    print(f"  1. EN and AX are TRANSITIONALLY INDISTINGUISHABLE at macro level.")
    print(f"     The role taxonomy's 5-way split over-differentiates; the grammar")
    print(f"     treats 'energy operators' and 'auxiliaries' as one operational mass.")
    print(f"")
    print(f"  2. FL splits into HAZ/SAFE (not merged) — confirming C586.")
    print(f"     FL's non-executive status (C949) doesn't mean it's uniform;")
    print(f"     the hazard/safe distinction is a genuine transition-level feature.")
    print(f"")
    print(f"  3. The 6-state automaton reproduces:")
    print(f"     - Zipf exponent (z=+0.8)")
    print(f"     - Cross-line MI (z=+1.3)")
    print(f"     - Asymmetry rate (z=-0.1)")
    print(f"     But NOT class-level depletion count (z=+7.6).")
    print(f"     Depletion is within-state texture, not macro-level structure.")
    print(f"")
    print(f"  4. 48 of 49 eigenvalues are significant (>0.01), meaning class-level")
    print(f"     transition profiles are nearly all unique. But constraint preservation")
    print(f"     only requires 6 states. The gap between 48 (information) and 6")
    print(f"     (constraint-necessary) is the 'free variation' envelope.")
    print(f"")
    print(f"  IMPLICATION:")
    print(f"  The grammar is a 6-state automaton dressed in 49 classes.")
    print(f"  The classes provide lexical diversity; the states provide structural law.")

    # Save
    results = {
        'test': 'T5_synthesis',
        'spectral_effective_rank': t2['effective_rank']['0.01'],
        'spectral_gap_states': t2['spectral_gap']['suggested_states'],
        'nmf_elbow': t2['nmf_elbow'],
        'minimum_states': t3['n_final_states'],
        'compression_ratio': t3['compression_ratio'],
        'binding_constraints': t3['binding_type_counts'],
        'generative_fidelity': t4['fidelity'],
        'generation_verdict': t4['generation_verdict'],
        'metric_matches': {k: v['match'] for k, v in t4['comparison'].items()},
        'verdict': verdict,
        'state_labels': [
            'FL_HAZ (hazard flow markers)',
            'FQ (frequent operators)',
            'CC (core control primitives)',
            'AX/EN minor (secondary execution)',
            'AX/EN major (primary execution mass)',
            'FL_SAFE (safe flow markers)',
        ],
        'key_finding': 'Grammar compresses to 6 states. EN/AX merge. FL splits HAZ/SAFE. 4/5 corpus metrics reproduced.',
    }

    with open(RESULTS_DIR / 't5_synthesis.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't5_synthesis.json'}")


if __name__ == '__main__':
    run()
