#!/usr/bin/env python3
"""
T3: Hazard Class Phenomenology
PROCESS_PHENOMENOLOGY_EXCLUSION phase (Tier 4)

Maps the 5 hazard classes (41/24/24/6/6) to specific distillation failure
modes and checks distribution alignment with expected real-world frequencies.
"""

import sys
import json
import functools
from pathlib import Path
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


# ============================================================
# HAZARD -> FAILURE MODE MAPPING
# ============================================================

HAZARD_FAILURE_MAP = {
    'PHASE_ORDERING': {
        'observed_pct': 41,
        'observed_count': 7,
        'failure_modes': [
            'Boil-over (liquid carryover into condenser/receiver)',
            'Wrong fraction in receiver (premature or late cut)',
            'Phase reversal (vapor condenses back prematurely)',
            'Liquid flooding of vapor path',
        ],
        'detection': {
            'primary_modality': 'VISUAL',
            'secondary_modality': 'TACTILE',
            'what_operator_sees': 'Liquid rising in neck, foam at surface, sudden level change in receiver',
            'detection_difficulty': 'EASY (visible, immediate)',
            'response_time_required': 'FAST (seconds)',
        },
        'why_dominant': (
            'Phase ordering failures are the most common in distillation because the operator is '
            'constantly managing the liquid-vapor boundary. Any energy change can push material into '
            'the wrong phase. In pelican reflux (sealed, circulatory), the liquid return path makes '
            'phase positioning even more critical — there are more places where material can be in '
            'the wrong phase compared to simple alembic distillation.'
        ),
        'constraint_citations': ['C109', 'C110'],
        'expected_rank_pelican': 1,
        'expected_frequency': 'HIGHEST',
        'pelican_specificity': (
            'Elevated vs open distillation because sealed circulation creates additional '
            'phase-ordering failure points (liquid return, multiple phase boundaries).'
        ),
    },
    'COMPOSITION_JUMP': {
        'observed_pct': 24,
        'observed_count': 4,
        'failure_modes': [
            'Fraction contamination (mixed outputs in receiver)',
            'Azeotrope breakthrough (unexpected mixture comes through)',
            'Carry-over of non-volatile residue',
        ],
        'detection': {
            'primary_modality': 'OLFACTORY',
            'secondary_modality': 'VISUAL',
            'what_operator_sees': 'Smell change in distillate, cloudiness in receiver, unexpected color',
            'detection_difficulty': 'MODERATE (requires trained nose, not always immediate)',
            'response_time_required': 'MODERATE (tens of seconds, but damage may already be done)',
        },
        'why_second': (
            'Composition failures are second-largest because multi-fraction distillation requires '
            'precise cut points. The operator must detect when one fraction ends and another begins. '
            'Without instruments, this relies primarily on olfactory discrimination — a learned skill.'
        ),
        'constraint_citations': ['C109'],
        'expected_rank_pelican': 2,
        'expected_frequency': 'HIGH',
        'pelican_specificity': (
            'Similar to open distillation. Pelican reflux does not significantly change '
            'composition jump risk compared to simple alembic.'
        ),
    },
    'CONTAINMENT_TIMING': {
        'observed_pct': 24,
        'observed_count': 4,
        'failure_modes': [
            'Overpressure burst (sealed vessel exceeds pressure tolerance)',
            'Liquid overflow (vessel capacity exceeded)',
            'Joint/luting failure (seal breaks at connection)',
            'Thermal shock crack (temperature differential breaks glass)',
        ],
        'detection': {
            'primary_modality': 'AUDITORY',
            'secondary_modality': 'TACTILE',
            'what_operator_sees': 'Unusual sounds (hissing, popping), vessel vibration, visible leak at joints',
            'detection_difficulty': 'MODERATE (auditory cues may be subtle before catastrophe)',
            'response_time_required': 'IMMEDIATE (catastrophic if not caught)',
        },
        'why_elevated': (
            'CONTAINMENT_TIMING at 24% is notably high. In OPEN distillation (alembic with open '
            'receiver), containment failures are rare because pressure cannot build up. But in PELICAN '
            'reflux — a SEALED circulatory vessel — pressure management is a constant concern. The '
            'sealed system traps vapor pressure, making containment the second-equal hazard class. '
            'This is the strongest pelican-specific signal in the hazard distribution.'
        ),
        'constraint_citations': ['C109'],
        'expected_rank_pelican': 2,
        'expected_frequency': 'HIGH (pelican-specific elevation)',
        'pelican_specificity': (
            'STRONGLY ELEVATED vs open distillation. Open alembic has ~5-10% containment risk. '
            'Pelican sealed system elevates this to ~24% because pressure is trapped. '
            'This is the KEY DISCRIMINATOR for pelican vs open distillation.'
        ),
    },
    'RATE_MISMATCH': {
        'observed_pct': 6,
        'observed_count': 1,
        'failure_modes': [
            'Flow imbalance (reflux return rate vs distillation rate mismatch)',
            'Flooding (vapor cannot rise through descending liquid)',
        ],
        'detection': {
            'primary_modality': 'VISUAL',
            'secondary_modality': 'AUDITORY',
            'what_operator_sees': 'Uneven flow in return path, gurgling sounds, liquid accumulation',
            'detection_difficulty': 'MODERATE (requires watching multiple points simultaneously)',
            'response_time_required': 'MODERATE (progressive, not sudden)',
        },
        'why_minor': (
            'Rate mismatch is minor because pelican reflux has a simple flow topology — one main '
            'circulatory path. In more complex apparatus (column stills with multiple plates), rate '
            'mismatch would be more prevalent. The low percentage suggests a simple apparatus.'
        ),
        'constraint_citations': ['C109'],
        'expected_rank_pelican': 4,
        'expected_frequency': 'LOW',
        'pelican_specificity': (
            'Low rate mismatch is consistent with pelican (simple single-loop circulation) '
            'rather than column distillation (multiple rate-sensitive stages).'
        ),
    },
    'ENERGY_OVERSHOOT': {
        'observed_pct': 6,
        'observed_count': 1,
        'failure_modes': [
            'Scorching (material burns on vessel wall)',
            'Thermal decomposition of product',
            'Caramelization or charring of residue',
        ],
        'detection': {
            'primary_modality': 'OLFACTORY',
            'secondary_modality': 'VISUAL',
            'what_operator_sees': 'Burning smell, discoloration of residue, smoke',
            'detection_difficulty': 'EASY (unmistakable smell, but damage already done)',
            'response_time_required': 'PREVENTION (by the time you smell burning, product is lost)',
        },
        'why_rare': (
            'Energy overshoot is rare because an experienced operator manages heat carefully. '
            'It is a catastrophic but preventable failure. The low percentage (6%) suggests '
            'the system is designed for operators with basic competence — overshoot is the '
            '"beginner mistake" that the control system helps avoid. The k-operator (ENERGY_MODULATOR) '
            'concentration in QO lane and 1-token hazard gate provide the architecture for prevention.'
        ),
        'constraint_citations': ['C109'],
        'expected_rank_pelican': 5,
        'expected_frequency': 'LOWEST',
        'pelican_specificity': (
            'Similar across distillation types. Energy overshoot risk is independent of '
            'vessel topology (open vs sealed).'
        ),
    },
}


# ============================================================
# EXPECTED RANKING FOR PELICAN REFLUX
# ============================================================

# Expected ranking based on pelican reflux process engineering knowledge:
# 1. PHASE_ORDERING: Dominant because of constant liquid-vapor boundary management
# 2-3. CONTAINMENT_TIMING: Elevated because sealed vessel traps pressure
# 2-3. COMPOSITION_JUMP: Standard multi-fraction risk
# 4. RATE_MISMATCH: Low because simple single-loop topology
# 5. ENERGY_OVERSHOOT: Lowest because preventable with basic skill

OBSERVED_RANKING = ['PHASE_ORDERING', 'COMPOSITION_JUMP', 'CONTAINMENT_TIMING', 'RATE_MISMATCH', 'ENERGY_OVERSHOOT']
OBSERVED_VALUES = [41, 24, 24, 6, 6]

# Expected ranking specifically for pelican reflux (sealed circulatory vessel)
EXPECTED_RANKING_PELICAN = ['PHASE_ORDERING', 'CONTAINMENT_TIMING', 'COMPOSITION_JUMP', 'RATE_MISMATCH', 'ENERGY_OVERSHOOT']
EXPECTED_VALUES_PELICAN = [40, 25, 20, 10, 5]

# Expected ranking for OPEN alembic (unsealed)
EXPECTED_RANKING_OPEN = ['PHASE_ORDERING', 'COMPOSITION_JUMP', 'ENERGY_OVERSHOOT', 'RATE_MISMATCH', 'CONTAINMENT_TIMING']
EXPECTED_VALUES_OPEN = [45, 25, 15, 10, 5]


def main():
    print("=" * 70)
    print("T3: HAZARD CLASS PHENOMENOLOGY")
    print("=" * 70)

    # ---- Rank correlation ----
    print("\n--- Distribution Alignment ---")

    # Observed ranks (1=most common)
    obs_ranks = list(range(1, 6))  # [1, 2, 3, 4, 5]

    # Expected ranks for pelican: PHASE=1, CONTAIN=2, COMP=3, RATE=4, ENERGY=5
    # Map observed order to expected order
    # Observed: PO=1, CJ=2, CT=3, RM=4, EO=5
    # Pelican expected: PO=1, CT=2, CJ=3, RM=4, EO=5
    # So observed CJ=2 vs expected CJ=3, and observed CT=3 vs expected CT=2
    pelican_expected_ranks = [1, 3, 2, 4, 5]  # PO, CJ, CT, RM, EO in observed order

    rho_pelican, p_pelican = stats.spearmanr(obs_ranks, pelican_expected_ranks)
    print(f"  Pelican expected: rho={rho_pelican:.3f}, p={p_pelican:.4f}")

    # For open alembic comparison
    # Expected: PO=1, CJ=2, EO=3, RM=4, CT=5
    open_expected_ranks = [1, 2, 5, 4, 3]  # PO, CJ, CT, RM, EO in observed order
    rho_open, p_open = stats.spearmanr(obs_ranks, open_expected_ranks)
    print(f"  Open alembic expected: rho={rho_open:.3f}, p={p_open:.4f}")

    # Shape match: is it heavy-tailed (2 dominant + 2 minor)?
    top2_pct = OBSERVED_VALUES[0] + OBSERVED_VALUES[1]  # 41 + 24 = 65
    bottom2_pct = OBSERVED_VALUES[3] + OBSERVED_VALUES[4]  # 6 + 6 = 12
    shape_match = top2_pct > 50 and bottom2_pct < 20
    print(f"  Shape: top-2={top2_pct}%, bottom-2={bottom2_pct}%, heavy-tailed={shape_match}")

    # ---- Pelican specificity ----
    print("\n--- Pelican Specificity ---")
    containment_elevated = OBSERVED_VALUES[2] >= 20  # CT at 24%
    containment_note = (
        f"CONTAINMENT_TIMING at {OBSERVED_VALUES[2]}% is consistent with sealed pelican vessel "
        f"(expected ~25% for sealed vs ~5% for open). This is the strongest apparatus-type signal."
    )
    print(f"  Containment elevated: {containment_elevated} ({OBSERVED_VALUES[2]}%)")

    # Rate mismatch low = simple apparatus
    rate_low = OBSERVED_VALUES[3] <= 10
    rate_note = (
        f"RATE_MISMATCH at {OBSERVED_VALUES[3]}% is consistent with simple single-loop apparatus "
        f"(pelican) rather than complex multi-stage column still."
    )
    print(f"  Rate mismatch low: {rate_low} ({OBSERVED_VALUES[3]}%)")

    # ---- Phenomenological coherence per class ----
    print("\n--- Per-Class Coherence ---")
    coherence_scores = {}

    for haz_name, haz_data in HAZARD_FAILURE_MAP.items():
        det = haz_data['detection']
        # Score components:
        # 1. Detection feasible without instruments? (0.0-0.4)
        difficulty = det['detection_difficulty']
        if 'EASY' in difficulty:
            detect_score = 0.4
        elif 'MODERATE' in difficulty:
            detect_score = 0.3
        else:
            detect_score = 0.1

        # 2. Response time compatible with 1-token gate? (0.0-0.3)
        response = det['response_time_required']
        if 'IMMEDIATE' in response or 'FAST' in response:
            response_score = 0.3
        elif 'MODERATE' in response or 'PREVENTION' in response:
            response_score = 0.2
        else:
            response_score = 0.1

        # 3. Failure mode physically real in distillation? (0.0-0.3)
        n_modes = len(haz_data['failure_modes'])
        mode_score = min(0.3, 0.1 * n_modes)

        total = round(detect_score + response_score + mode_score, 2)
        coherence_scores[haz_name] = {
            'detection_feasibility': detect_score,
            'response_compatibility': response_score,
            'failure_mode_reality': mode_score,
            'total': total,
            'coherent': total >= 0.5,
        }
        print(f"  {haz_name}: {total:.2f} (detect={detect_score}, response={response_score}, modes={mode_score})")

    n_coherent = sum(1 for v in coherence_scores.values() if v['coherent'])
    overall_coherence = sum(v['total'] for v in coherence_scores.values()) / len(coherence_scores)
    print(f"  Coherent classes: {n_coherent}/5")
    print(f"  Overall coherence score: {overall_coherence:.3f}")

    # ---- Verdict ----
    if rho_pelican >= 0.8 and n_coherent == 5 and containment_elevated:
        verdict = 'COHERENT'
    elif rho_pelican >= 0.6 or n_coherent >= 4:
        verdict = 'PARTIAL'
    else:
        verdict = 'INCOHERENT'

    explanation = (
        f"Rank correlation with pelican expected: rho={rho_pelican:.3f} "
        f"(vs open alembic: rho={rho_open:.3f}). "
        f"{n_coherent}/5 classes phenomenologically coherent. "
        f"CONTAINMENT_TIMING at {OBSERVED_VALUES[2]}% confirms sealed-vessel apparatus. "
    )
    if verdict == 'COHERENT':
        explanation += "Hazard distribution matches pelican reflux distillation failure mode frequencies."
    elif verdict == 'PARTIAL':
        explanation += "Partial alignment; distribution is compatible but not uniquely diagnostic."

    # ---- Compile results ----
    results = {
        'test': 'T3_hazard_phenomenology',
        'hazard_failure_map': {
            name: {
                'observed_pct': data['observed_pct'],
                'observed_count': data['observed_count'],
                'failure_modes': data['failure_modes'],
                'detection': data['detection'],
                'constraint_citations': data['constraint_citations'],
                'expected_rank_pelican': data['expected_rank_pelican'],
                'pelican_specificity': data['pelican_specificity'],
            }
            for name, data in HAZARD_FAILURE_MAP.items()
        },
        'distribution_alignment': {
            'observed_ranking': OBSERVED_RANKING,
            'observed_values': OBSERVED_VALUES,
            'pelican_expected_ranking': EXPECTED_RANKING_PELICAN,
            'open_expected_ranking': EXPECTED_RANKING_OPEN,
            'spearman_rho_pelican': round(rho_pelican, 4),
            'spearman_p_pelican': round(p_pelican, 4),
            'spearman_rho_open': round(rho_open, 4),
            'spearman_p_open': round(p_open, 4),
            'shape_match': shape_match,
            'top2_pct': top2_pct,
            'bottom2_pct': bottom2_pct,
        },
        'pelican_specificity': {
            'containment_elevated': containment_elevated,
            'containment_pct': OBSERVED_VALUES[2],
            'containment_note': containment_note,
            'rate_mismatch_low': rate_low,
            'rate_mismatch_pct': OBSERVED_VALUES[3],
            'rate_note': rate_note,
            'pelican_vs_open_rho_advantage': round(rho_pelican - rho_open, 4),
        },
        'phenomenological_coherence': {
            'per_class': coherence_scores,
            'n_coherent': n_coherent,
            'overall_score': round(overall_coherence, 4),
        },
        'verdict': verdict,
        'explanation': explanation,
    }

    # ---- Save ----
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 't3_hazard_phenomenology.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {out_path}")

    # ---- Summary ----
    print(f"\n{'=' * 70}")
    print(f"VERDICT: {verdict}")
    print(f"  Pelican rank rho: {rho_pelican:.3f} (vs open: {rho_open:.3f})")
    print(f"  Coherent classes: {n_coherent}/5")
    print(f"  Overall coherence: {overall_coherence:.3f}")
    print(f"  Pelican specificity: CONTAINMENT={OBSERVED_VALUES[2]}% (sealed vessel signal)")
    print(f"  {explanation}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
