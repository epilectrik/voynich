#!/usr/bin/env python3
"""
T2: Candidate Controlled Variable Scoring
CONTROLLED_VARIABLE_ANALYSIS phase (Tier 3/4)

For each candidate controlled variable, derive specific predictions about
what the 6-state automaton represents physically, then score against the
structural signature. All scoring is interpretive (Tier 3/4).

Candidates (in distillation context):
1. Temperature/thermal state
2. Vapor composition (fraction purity)
3. Liquid concentration (solvent/solute ratio)
4. Phase boundary position (liquid/gas interface)
5. Product quality (sensory: aroma, taste, clarity)
"""

import sys
import json
import functools
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


# ============================================================
# CANDIDATE DEFINITIONS
# ============================================================

CANDIDATES = [
    {
        'id': 'CV-1',
        'name': 'Temperature / Thermal State',
        'description': 'The system regulates heat distribution across the apparatus. The controlled variable is the thermal profile — how hot each part of the system is.',
        'mappings': {
            'S4_AXM': 'Steady heating at target fire degree. Maintained thermal equilibrium.',
            'S1_FQ': 'Temperature monitoring (finger test, visual check of bath/condensation).',
            'S0_FL_HAZ': 'Thermal excursion detected — temperature approaching dangerous level.',
            'S5_FL_SAFE': 'Temperature confirmed stable at safe operating point.',
            'S2_CC': 'Active thermal adjustment (regulate fire, adjust vent, replenish bath).',
            'S3_AXm': 'Initial heating ramp — bringing apparatus to operating temperature.',
            'two_lanes': 'Heating cycle vs cooling cycle (or fire-tending vs bath-monitoring).',
            'hazard': 'Overheating (4th degree fire) or thermal shock from rapid cooling.',
            'recovery_e': 'Cooling — overnight mandatory cooling period (Brunschwig explicit).',
            'regime': 'Fire degree (1st through 4th) — directly mapped to REGIME by Brunschwig.',
        },
    },
    {
        'id': 'CV-2',
        'name': 'Vapor Composition / Fraction Purity',
        'description': 'The system regulates what compounds are present in the vapor/distillate. The controlled variable is the purity or composition of the collected fraction.',
        'mappings': {
            'S4_AXM': 'Active distillation — vapor rising, condensing, fractions collecting.',
            'S1_FQ': 'Fraction testing (thumbnail test, scent check, drip rate monitoring).',
            'S0_FL_HAZ': 'Wrong fraction detected — off-notes, contamination, mixed fractions.',
            'S5_FL_SAFE': 'Pure fraction confirmed — quality test passed.',
            'S2_CC': 'Fraction change commands (switch receivers, adjust heat for new fraction).',
            'S3_AXm': 'Pre-distillation preparation (maceration, mixing, loading).',
            'two_lanes': 'Light fraction (foreshots/heads) vs heavy fraction (hearts/tails) management.',
            'hazard': 'Fraction contamination — wrong compounds in product.',
            'recovery_e': 'Redistillation — purify by re-running through apparatus.',
            'regime': 'Target compound volatility — different fractions need different heat profiles.',
        },
    },
    {
        'id': 'CV-3',
        'name': 'Liquid Concentration / Solvent Ratio',
        'description': 'The system regulates the ratio of solvent to solute in the liquid phase. The controlled variable is concentration — how much active material is dissolved.',
        'mappings': {
            'S4_AXM': 'Extraction cycling — solvent dissolving target compounds.',
            'S1_FQ': 'Concentration monitoring (visual turbidity, color change, taste).',
            'S0_FL_HAZ': 'Solvent breakthrough — too dilute or solvent overpowering product.',
            'S5_FL_SAFE': 'Target concentration achieved.',
            'S2_CC': 'Dilution/concentration adjustment (add solvent, evaporate).',
            'S3_AXm': 'Initial dissolution — loading material into solvent.',
            'two_lanes': 'Dissolution phase vs evaporation phase.',
            'hazard': 'Over-dilution or precipitation — material falls out of solution.',
            'recovery_e': 'Re-dissolution — add fresh solvent and re-extract.',
            'regime': 'Solvent type or ratio — different materials need different solvents.',
        },
    },
    {
        'id': 'CV-4',
        'name': 'Phase Boundary Position',
        'description': 'The system regulates where the liquid/gas boundary sits in the apparatus. The controlled variable is the phase equilibrium — how much material is in each phase.',
        'mappings': {
            'S4_AXM': 'Phase equilibrium maintenance — liquid and vapor coexisting stably.',
            'S1_FQ': 'Phase boundary monitoring (liquid level, condensation rate, foam).',
            'S0_FL_HAZ': 'Phase instability — flooding, foaming, bumping, dry-out.',
            'S5_FL_SAFE': 'Phase boundary stabilized at correct position.',
            'S2_CC': 'Phase adjustment (modify heat input to shift equilibrium).',
            'S3_AXm': 'Phase establishment — bringing system to first boil.',
            'two_lanes': 'Vaporization (upward flux) vs condensation (downward flux).',
            'hazard': 'Flooding (liquid carried into vapor) or dry-out (no liquid remaining).',
            'recovery_e': 'Reflux return — condensed liquid falling back to restore phase boundary.',
            'regime': 'Operating pressure/temperature determining phase boundary position.',
        },
    },
    {
        'id': 'CV-5',
        'name': 'Product Quality / Sensory State',
        'description': 'The system regulates the sensory quality of the output — taste, smell, clarity, viscosity. The controlled variable is product quality as assessed by categorical sensory tests.',
        'mappings': {
            'S4_AXM': 'Active processing — material undergoing transformation.',
            'S1_FQ': 'Sensory testing (smell, taste, visual clarity, thumbnail viscosity).',
            'S0_FL_HAZ': 'Quality deviation detected — off-taste, cloudiness, wrong viscosity.',
            'S5_FL_SAFE': 'Quality confirmed acceptable.',
            'S2_CC': 'Corrective action (adjust process to restore quality).',
            'S3_AXm': 'Initial quality assessment — baseline evaluation before processing.',
            'two_lanes': 'Primary quality axis vs secondary quality axis (e.g., potency vs purity).',
            'hazard': 'Quality failure — product is ruined or contaminated.',
            'recovery_e': 'Reprocessing — re-distill, re-filter, re-settle to restore quality.',
            'regime': 'Quality standard — different products have different acceptance thresholds.',
        },
    },
]


# ============================================================
# SCORING CRITERIA
# ============================================================

CRITERIA = [
    {
        'id': 'SC-01',
        'sig_ref': 'SIG-01',
        'criterion': 'Dominant steady-state (68% in S4)',
        'question': 'Does the controlled variable have a natural steady-state that the system inhabits most of the time?',
    },
    {
        'id': 'SC-02',
        'sig_ref': 'SIG-03',
        'criterion': 'Memoryless (mixing time ~1 token)',
        'question': 'Does the controlled variable reset quickly after perturbation, with no accumulating history?',
    },
    {
        'id': 'SC-03',
        'sig_ref': 'SIG-04',
        'criterion': 'Hazard-near operation (6.5x hazard/safe ratio)',
        'question': 'Does the controlled variable naturally operate close to dangerous boundaries, with risk much more frequent than safe completion?',
    },
    {
        'id': 'SC-04',
        'sig_ref': 'SIG-05',
        'criterion': 'Sharp hazard pulses (1-token gate)',
        'question': 'Are hazard events brief transients (not sustained crises) that resolve in a single control action?',
    },
    {
        'id': 'SC-05',
        'sig_ref': 'SIG-06',
        'criterion': 'Binary mode oscillation (two lanes)',
        'question': 'Does the controlled variable have exactly two complementary modes that alternate?',
    },
    {
        'id': 'SC-06',
        'sig_ref': 'SIG-07/08',
        'criterion': 'Intensity-scalable with fixed boundaries',
        'question': 'Can the control intensity be varied (REGIME) without changing the meaning of hazard/safe?',
    },
    {
        'id': 'SC-07',
        'sig_ref': 'SIG-09',
        'criterion': 'Dedicated recovery mechanism with hard limit',
        'question': 'Is there a specific stabilizing operation (not just "do less") with a maximum retry count?',
    },
    {
        'id': 'SC-08',
        'sig_ref': 'SIG-11',
        'criterion': 'Categorical assessment (pass/fail, not measured)',
        'question': 'Is the controlled variable assessed by sensory/categorical tests rather than instruments or numbers?',
    },
    {
        'id': 'SC-09',
        'sig_ref': 'SIG-12',
        'criterion': 'Brief preparatory ramp (AXm, 3%)',
        'question': 'Is there a short ramp-up or initialization phase before the main steady-state operation begins?',
    },
    {
        'id': 'SC-10',
        'sig_ref': 'SIG-13',
        'criterion': 'Periodic monitoring interruptions (FQ, 18%)',
        'question': 'Does the process require periodic checking/testing that interrupts the main operation?',
    },
    {
        'id': 'SC-11',
        'sig_ref': 'SIG-14',
        'criterion': 'End-of-block completion marking',
        'question': 'Does safe completion naturally occur at the end of a processing batch/cycle, not mid-process?',
    },
    {
        'id': 'SC-12',
        'sig_ref': 'SIG-06/Brunschwig',
        'criterion': 'Historical attestation in Brunschwig',
        'question': 'Is this controlled variable explicitly discussed in Brunschwig\'s distillation manual?',
    },
]


def score_candidate(candidate_id):
    """
    Score each candidate against criteria.
    Returns dict of criterion_id -> (score, rationale)

    Scoring:
      2 = Strong fit (naturally predicted by the interpretation)
      1 = Partial fit (compatible but not specifically predicted)
      0 = Neutral (no prediction either way)
     -1 = Weak tension (somewhat awkward fit)
     -2 = Strong conflict (contradicts structural signature)
    """

    # These scores encode domain expertise about distillation physics.
    # They are INTERPRETIVE (Tier 3/4), not structural proof.

    scores = {}

    if candidate_id == 'CV-1':  # Temperature
        scores = {
            'SC-01': (2, 'Temperature has a natural steady-state (target fire degree). System maintains it.'),
            'SC-02': (2, 'Temperature responds quickly to fire adjustment. Thermal mass of small apparatus is low.'),
            'SC-03': (2, 'Brunschwig: 4th degree is always dangerous. System operates between 2nd and 3rd — near hazard.'),
            'SC-04': (2, 'Brief temperature spike (fuel flare, draft change) resolves in seconds.'),
            'SC-05': (2, 'Heating vs cooling cycles alternate naturally in reflux. Fire-tending vs bath-checking.'),
            'SC-06': (2, 'Fire degree IS the REGIME. Brunschwig defines 4 levels. Hazard meaning unchanged across levels.'),
            'SC-07': (2, 'Cooling is the explicit recovery. Brunschwig: mandatory overnight cooling. Hard 2-retry limit matches.'),
            'SC-08': (2, 'Brunschwig finger test: can you bear a finger indefinitely? Binary pass/fail.'),
            'SC-09': (2, 'Initial heating ramp to bring apparatus to operating temperature.'),
            'SC-10': (2, 'Periodic fire/bath monitoring. Brunschwig: check bath temperature regularly.'),
            'SC-11': (1, 'Temperature stabilization at end of batch is expected but not uniquely temperature-specific.'),
            'SC-12': (2, 'Central topic of Brunschwig. Fire degree system, finger test, cooling protocol all explicit.'),
        }
    elif candidate_id == 'CV-2':  # Vapor composition
        scores = {
            'SC-01': (1, 'Steady-state distillation produces consistent vapor, but composition drifts over time as material depletes.'),
            'SC-02': (0, 'Vapor composition has some memory — current fraction depends on what has already been extracted.'),
            'SC-03': (1, 'Fraction contamination risk exists but is not the primary concern in reflux distillation.'),
            'SC-04': (0, 'Composition changes are gradual, not sharp pulses. Fraction transitions are smooth.'),
            'SC-05': (1, 'Light/heavy fraction distinction exists but is not a binary oscillation — it is sequential.'),
            'SC-06': (1, 'Different heat levels extract different compounds, but the fraction boundaries also shift.'),
            'SC-07': (1, 'Redistillation is possible but the "e as cooling" mapping is weaker here.'),
            'SC-08': (2, 'Scent test, taste test, thumbnail viscosity — all categorical. Strong match.'),
            'SC-09': (1, 'Pre-distillation preparation exists but is more than a brief ramp.'),
            'SC-10': (2, 'Fraction testing is a natural monitoring interruption. Strong match.'),
            'SC-11': (1, 'Final fraction collection happens at end, but fractions are sequential within a batch.'),
            'SC-12': (1, 'Brunschwig discusses fractions but temperature control is more prominent.'),
        }
    elif candidate_id == 'CV-3':  # Liquid concentration
        scores = {
            'SC-01': (0, 'Concentration does not have a natural steady-state — it changes monotonically during extraction.'),
            'SC-02': (-1, 'Concentration has strong memory — it is cumulative. Current state depends on all prior extraction.'),
            'SC-03': (0, 'Over-dilution is a risk but is not the dominant operational concern.'),
            'SC-04': (-1, 'Concentration changes are gradual, not sharp transients.'),
            'SC-05': (-1, 'Dissolution/evaporation could alternate, but this is not a natural binary oscillation.'),
            'SC-06': (0, 'Solvent ratio could vary by material, but this is material-specific, not intensity-specific.'),
            'SC-07': (0, 'Re-dissolution is possible but does not match e-as-cooling mapping.'),
            'SC-08': (1, 'Color/turbidity tests are categorical. Partial match.'),
            'SC-09': (1, 'Initial dissolution is real but gradual, not brief.'),
            'SC-10': (0, 'Monitoring is needed but not as periodic interruptions — more as continuous observation.'),
            'SC-11': (0, 'No natural end-of-block structure for concentration.'),
            'SC-12': (-1, 'Brunschwig does not focus on concentration as controlled variable. Extraction is a preparation step.'),
        }
    elif candidate_id == 'CV-4':  # Phase boundary
        scores = {
            'SC-01': (2, 'Phase equilibrium IS a natural steady-state in reflux. System maintains liquid/vapor balance.'),
            'SC-02': (1, 'Phase boundary responds quickly to heat changes in small apparatus. Moderate match.'),
            'SC-03': (2, 'Flooding and dry-out are primary risks in reflux columns. System operates between them.'),
            'SC-04': (2, 'Bumping (sudden boiling surge) is a sharp transient that resolves in one event.'),
            'SC-05': (2, 'Vaporization (upward flux) vs condensation (downward flux) is a natural binary in reflux.'),
            'SC-06': (1, 'Higher fire degree shifts equilibrium but the hazard meaning (flooding/dry-out) remains.'),
            'SC-07': (2, 'Reflux return (condensed liquid falling back) is the recovery mechanism in pelican design.'),
            'SC-08': (1, 'Phase boundary position is partly visual (liquid level, foam) but partly physical feel.'),
            'SC-09': (2, 'First boil is the establishment of the phase boundary. Brief, critical ramp.'),
            'SC-10': (1, 'Monitoring is more continuous (watching condensation) than periodic.'),
            'SC-11': (1, 'Phase boundary stabilization occurs when heat is removed at end of batch.'),
            'SC-12': (1, 'Brunschwig discusses boiling/condensation but not explicitly as a controlled boundary.'),
        }
    elif candidate_id == 'CV-5':  # Product quality
        scores = {
            'SC-01': (0, 'Quality does not have a steady-state — it is an outcome, not a process variable.'),
            'SC-02': (-1, 'Quality is cumulative — damage is not forgotten. Burned product stays burned.'),
            'SC-03': (0, 'Quality risk exists but quality is a measurement of outcome, not an operating condition.'),
            'SC-04': (-1, 'Quality degradation is often irreversible and gradual, not a sharp pulse.'),
            'SC-05': (-1, 'Quality does not have two complementary modes. It is a single axis (good/bad).'),
            'SC-06': (0, 'Quality standards may vary, but this conflates the variable with the criterion.'),
            'SC-07': (0, 'Reprocessing exists but the hard 2-retry limit is harder to justify for quality.'),
            'SC-08': (2, 'Brunschwig sensory tests (smell, taste, thumbnail) are exactly quality assessment. Perfect match.'),
            'SC-09': (0, 'No natural preparatory ramp for quality.'),
            'SC-10': (2, 'Periodic quality testing is the primary monitoring activity. Strong match.'),
            'SC-11': (1, 'Final quality check at end of batch is natural.'),
            'SC-12': (1, 'Brunschwig discusses quality tests but as EFFECTS of temperature control, not as the controlled variable itself.'),
        }

    return scores


def run():
    print("=" * 70)
    print("T2: Candidate Controlled Variable Scoring")
    print("CONTROLLED_VARIABLE_ANALYSIS phase (Tier 3/4)")
    print("=" * 70)
    print("\n  NOTE: All scores are INTERPRETIVE (Tier 3/4).")
    print("  They encode domain knowledge about distillation physics,")
    print("  not structural proof.\n")

    # Load signature
    with open(RESULTS_DIR / 't1_structural_signature.json') as f:
        t1 = json.load(f)

    # Score each candidate
    all_scores = {}
    all_totals = {}

    for cand in CANDIDATES:
        print(f"\n{'='*70}")
        print(f"  {cand['id']}: {cand['name']}")
        print(f"{'='*70}")
        print(f"  {cand['description']}\n")

        print(f"  State Mappings:")
        for key, mapping in cand['mappings'].items():
            print(f"    {key:>12}: {mapping}")

        scores = score_candidate(cand['id'])

        print(f"\n  Scoring Against Structural Signature:")
        print(f"  {'Criterion':>8} {'Score':>6} Rationale")
        total = 0
        for crit in CRITERIA:
            score, rationale = scores.get(crit['id'], (0, 'Not scored'))
            symbol = {2: '++', 1: '+ ', 0: '  ', -1: '- ', -2: '--'}[score]
            print(f"  {crit['id']:>8}   [{symbol}]  {rationale}")
            total += score

        max_possible = len(CRITERIA) * 2
        pct = total / max_possible * 100

        print(f"\n  TOTAL: {total}/{max_possible} ({pct:.0f}%)")
        all_scores[cand['id']] = scores
        all_totals[cand['id']] = {'total': total, 'max': max_possible, 'pct': round(pct, 1)}

    # =========================================================
    # Ranking
    # =========================================================
    print(f"\n\n{'='*70}")
    print(f"CANDIDATE RANKING")
    print(f"{'='*70}\n")

    ranked = sorted(all_totals.items(), key=lambda x: -x[1]['total'])
    for rank, (cid, totals) in enumerate(ranked, 1):
        name = next(c['name'] for c in CANDIDATES if c['id'] == cid)
        bar = '#' * int(totals['pct'] / 4)
        print(f"  {rank}. {name:>40}: {totals['total']:>3}/{totals['max']} ({totals['pct']:>5.1f}%) {bar}")

    winner = ranked[0]
    runner = ranked[1]

    print(f"\n  TOP CANDIDATE: {next(c['name'] for c in CANDIDATES if c['id'] == winner[0])}")
    print(f"  RUNNER-UP:     {next(c['name'] for c in CANDIDATES if c['id'] == runner[0])}")

    # Discriminant analysis
    print(f"\n\n{'='*70}")
    print(f"DISCRIMINANT ANALYSIS: What separates the top candidates?")
    print(f"{'='*70}\n")

    w_scores = all_scores[winner[0]]
    r_scores = all_scores[runner[0]]

    print(f"  Criteria where top candidate clearly beats runner-up:")
    for crit in CRITERIA:
        w_s = w_scores.get(crit['id'], (0, ''))[0]
        r_s = r_scores.get(crit['id'], (0, ''))[0]
        if w_s - r_s >= 1:
            print(f"    {crit['id']} ({crit['criterion']}): "
                  f"winner={w_s:+d} vs runner={r_s:+d}")

    print(f"\n  Criteria where runner-up matches or beats top candidate:")
    for crit in CRITERIA:
        w_s = w_scores.get(crit['id'], (0, ''))[0]
        r_s = r_scores.get(crit['id'], (0, ''))[0]
        if r_s >= w_s and r_s > 0:
            print(f"    {crit['id']} ({crit['criterion']}): "
                  f"runner={r_s:+d} vs winner={w_s:+d}")

    # =========================================================
    # Synthesis
    # =========================================================
    print(f"\n\n{'='*70}")
    print(f"SYNTHESIS (Tier 3/4)")
    print(f"{'='*70}")

    print(f"""
  FINDING: Temperature/thermal state is the strongest candidate
  controlled variable for the 6-state automaton.

  WHY IT WINS:
  1. Brunschwig's fire-degree system maps directly to REGIME (SC-12)
  2. Temperature has a natural steady-state matching S4 dominance (SC-01)
  3. Temperature resets quickly (no memory), matching mixing time (SC-02)
  4. Overheating is the primary hazard, sharp and recoverable (SC-03, SC-04)
  5. Heating/cooling cycles provide the binary oscillation (SC-05)
  6. Fire degree scales intensity without changing hazard meaning (SC-06)
  7. Cooling IS the recovery mechanism (e = mandatory overnight cool) (SC-07)
  8. Finger test IS categorical assessment (SC-08)

  WHY PHASE BOUNDARY IS THE STRONG RUNNER-UP:
  1. Flooding/dry-out are the primary reflux hazards (SC-03)
  2. Vaporization/condensation IS a natural binary oscillation (SC-05)
  3. Reflux return IS the dedicated recovery mechanism (SC-07)
  4. First boil IS the brief preparatory ramp (SC-09)
  But: phase boundary is less directly attested in Brunschwig
  and has more memory (phase history matters).

  RESOLUTION:
  Temperature and phase boundary are NOT independent.
  In a reflux apparatus, temperature IS the variable that
  controls the phase boundary position.

  The most coherent interpretation is:

  > The controlled variable is THERMAL STATE, which determines
  > phase boundary behavior as its primary effect.

  Temperature is the input (what the operator controls).
  Phase boundary is the output (what the apparatus responds with).
  The grammar tracks the input side: fire degree, heating/cooling,
  categorical monitoring, mandatory recovery by cooling.

  TIER: 3 (speculative but structurally coherent)
  CONFIDENCE: HIGH within distillation framework
""")

    # Save
    results = {
        'test': 'T2_candidate_scoring',
        'tier': '3/4',
        'n_candidates': len(CANDIDATES),
        'n_criteria': len(CRITERIA),
        'candidates': {c['id']: c['name'] for c in CANDIDATES},
        'ranking': [
            {'rank': rank+1, 'id': cid, 'name': next(c['name'] for c in CANDIDATES if c['id'] == cid),
             'total': t['total'], 'max': t['max'], 'pct': t['pct']}
            for rank, (cid, t) in enumerate(ranked)
        ],
        'top_candidate': {
            'id': winner[0],
            'name': next(c['name'] for c in CANDIDATES if c['id'] == winner[0]),
            'score': winner[1]['total'],
            'pct': winner[1]['pct'],
        },
        'runner_up': {
            'id': runner[0],
            'name': next(c['name'] for c in CANDIDATES if c['id'] == runner[0]),
            'score': runner[1]['total'],
            'pct': runner[1]['pct'],
        },
        'synthesis': 'Thermal state is the controlled variable; phase boundary is its primary effect. Temperature (input) controls phase boundary (output). Grammar tracks the input side.',
        'verdict': 'THERMAL_STATE',
        'confidence': 'HIGH within distillation framework',
    }

    with open(RESULTS_DIR / 't2_candidate_scoring.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {RESULTS_DIR / 't2_candidate_scoring.json'}")


if __name__ == '__main__':
    run()
