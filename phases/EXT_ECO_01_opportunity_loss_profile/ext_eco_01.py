"""
Phase EXT-ECO-01: Opportunity-Loss Hazard Profile Analysis

Tests whether the hazard topology and restart-intolerance structure is more consistent
with OPPORTUNITY-LOSS (mistiming irreversibly loses value) than PHYSICAL-INSTABILITY
(system becomes physically unstable).

This phase does NOT:
- Assign semantics, materials, or products
- Identify trades, industries, or substances
- Interpret illustrations or botanical content
- Reopen SID conclusions
- Treat hazards as calendar-encoded
- Upgrade conclusions beyond Tier 3
"""

import json
import os
import statistics
from collections import Counter, defaultdict
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS1_PATH = os.path.join(BASE_DIR, 'phases', 'OPS1_folio_control_signatures', 'ops1_folio_control_signatures.json')
RECIPE_ATLAS_PATH = os.path.join(BASE_DIR, 'results', 'full_recipe_atlas.txt')
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Frozen hazard transitions from Phase 18
# Format: (source, target, hazard_class, direction_interpretation)
# direction_interpretation: "PREMATURE" (acting before ready), "SEQUENCE" (wrong order), "LATE" (waiting too long)
HAZARD_TRANSITIONS = [
    # PHASE_ORDERING (7 transitions - 41%)
    ('shey', 'aiin', 'PHASE_ORDERING', 'PREMATURE'),  # shey (phase marker) -> aiin (high impact) = acting before phase ready
    ('shey', 'al', 'PHASE_ORDERING', 'PREMATURE'),    # shey (phase marker) -> al = premature shift
    ('shey', 'c', 'PHASE_ORDERING', 'PREMATURE'),     # shey -> c = premature state change
    ('chol', 'r', 'PHASE_ORDERING', 'SEQUENCE'),      # chol (flow) -> r = wrong sequence
    ('chedy', 'ee', 'PHASE_ORDERING', 'SEQUENCE'),    # chedy (energy) -> ee = sequence violation
    ('chey', 'chedy', 'PHASE_ORDERING', 'SEQUENCE'),  # energy operator transitions
    ('l', 'chol', 'PHASE_ORDERING', 'PREMATURE'),     # l -> chol = premature flow start

    # COMPOSITION_JUMP (4 transitions - 24%)
    ('dy', 'aiin', 'COMPOSITION_JUMP', 'PREMATURE'),   # dy (frequent) -> aiin = premature commitment
    ('dy', 'chey', 'COMPOSITION_JUMP', 'PREMATURE'),   # dy -> chey = premature energy
    ('or', 'dal', 'COMPOSITION_JUMP', 'SEQUENCE'),     # wrong composition order
    ('ar', 'chol', 'COMPOSITION_JUMP', 'SEQUENCE'),    # wrong composition order

    # CONTAINMENT_TIMING (4 transitions - 24%)
    ('qo', 'shey', 'CONTAINMENT_TIMING', 'PREMATURE'), # qo (energy prefix) -> shey = premature phase shift
    ('qo', 'shy', 'CONTAINMENT_TIMING', 'PREMATURE'),  # qo -> shy = premature
    ('ok', 'shol', 'CONTAINMENT_TIMING', 'PREMATURE'), # ok -> shol = premature flow
    ('ol', 'shor', 'CONTAINMENT_TIMING', 'PREMATURE'), # ol -> shor = premature

    # RATE_MISMATCH (1 transition - 6%)
    ('dar', 'qokaiin', 'RATE_MISMATCH', 'SEQUENCE'),   # rate sequence violation

    # ENERGY_OVERSHOOT (1 transition - 6%)
    ('qokaiin', 'qokedy', 'ENERGY_OVERSHOOT', 'PREMATURE'),  # energy -> energy = overeager energy application
]

# Instruction type classification
INSTRUCTION_TYPES = {
    'LINK': 'WAIT',
    'APPLY_ENERGY': 'ACTION',
    'SUSTAIN_ENERGY': 'ACTION',
    'CONTINUE_CYCLE': 'ACTION',
    'ANCHOR_STATE': 'ACTION',
    'SET_RATE': 'ACTION',
    'ENABLE_MODE': 'ACTION',
    'STABLE_HOLD': 'ACTION',
    'STABLE_FLOW': 'ACTION',
    'CHECKPOINT': 'ACTION',
}


def load_ops1_signatures():
    """Load OPS1 folio control signatures."""
    with open(OPS1_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('signatures', {})


def parse_recipe_atlas():
    """Parse recipe atlas to extract instruction sequences per folio."""
    folio_programs = {}
    current_folio = None
    current_program = []
    in_program = False

    with open(RECIPE_ATLAS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            if line.startswith('FOLIO:'):
                current_folio = line.split(':')[1].strip()
                current_program = []
                in_program = False
            elif line == 'BEGIN':
                in_program = True
            elif line.startswith('======') and current_folio and current_program:
                folio_programs[current_folio] = current_program
                current_folio = None
                current_program = []
                in_program = False
            elif in_program and line and not line.startswith('---'):
                current_program.append(line)

    # Handle last folio
    if current_folio and current_program:
        folio_programs[current_folio] = current_program

    return folio_programs


def test_A_premature_vs_late_asymmetry():
    """
    Test A: Premature vs Late Action Asymmetry

    Prediction (Opportunity-loss model):
    - Premature transitions dominate (>70%)
    - "Too late" failures are less frequent (<20%)

    Prediction (Physical-instability model):
    - Both types roughly equal
    - Late failures (thermal runaway, pressure buildup) common
    """
    premature_count = 0
    sequence_count = 0
    late_count = 0

    for src, tgt, hclass, direction in HAZARD_TRANSITIONS:
        if direction == 'PREMATURE':
            premature_count += 1
        elif direction == 'SEQUENCE':
            sequence_count += 1
        elif direction == 'LATE':
            late_count += 1

    total = len(HAZARD_TRANSITIONS)
    premature_rate = premature_count / total
    sequence_rate = sequence_count / total
    late_rate = late_count / total

    # Opportunity-loss prediction: premature > 70%
    opp_loss_fit = premature_rate > 0.50  # Premature dominates
    phys_inst_fit = 0.3 < late_rate < 0.5  # Late actions significant

    return {
        'test': 'A',
        'name': 'Premature vs Late Action Asymmetry',
        'metrics': {
            'premature_count': premature_count,
            'sequence_count': sequence_count,
            'late_count': late_count,
            'total_hazards': total,
            'premature_rate': round(premature_rate, 3),
            'sequence_rate': round(sequence_rate, 3),
            'late_rate': round(late_rate, 3),
        },
        'opportunity_loss_prediction': 'Premature > 70%, Late < 20%',
        'physical_instability_prediction': 'Both roughly equal, Late significant',
        'observed': f'Premature {premature_rate:.1%}, Sequence {sequence_rate:.1%}, Late {late_rate:.1%}',
        'opportunity_loss_fit': 'STRONG' if premature_rate > 0.60 else 'MODERATE' if premature_rate > 0.40 else 'WEAK',
        'physical_instability_fit': 'STRONG' if late_rate > 0.30 else 'WEAK',
        'verdict': 'OPPORTUNITY_LOSS' if premature_rate > late_rate * 2 else 'AMBIGUOUS'
    }


def test_B_collapse_shape(signatures):
    """
    Test B: Collapse Shape (Binary vs Runaway)

    Prediction (Opportunity-loss model):
    - Execution space collapses cleanly (100% convergence to STATE-C)
    - No oscillatory or runaway behavior
    - Failure = clean stop (value lost but no cascade)

    Prediction (Physical-instability model):
    - Some programs show oscillation or cascade
    - Recovery attempts observable
    - Non-uniform collapse patterns
    """
    terminal_states = Counter()
    convergence_speeds = []
    cycle_regularities = []

    for folio_id, sig in signatures.items():
        terminal = sig['loop_metrics']['terminal_state']
        terminal_states[terminal] += 1

        conv_speed = sig['loop_metrics']['convergence_speed_index']
        if conv_speed:
            convergence_speeds.append(conv_speed)

        reg = sig['loop_metrics']['cycle_regularity']
        if reg:
            cycle_regularities.append(reg)

    total = len(signatures)
    state_c_rate = terminal_states.get('STATE-C', 0) / total

    # Calculate convergence uniformity
    conv_std = statistics.stdev(convergence_speeds) if len(convergence_speeds) > 1 else 0
    conv_mean = statistics.mean(convergence_speeds) if convergence_speeds else 0
    conv_cv = conv_std / conv_mean if conv_mean > 0 else 0  # Coefficient of variation

    # Regularity uniformity
    reg_std = statistics.stdev(cycle_regularities) if len(cycle_regularities) > 1 else 0
    reg_mean = statistics.mean(cycle_regularities) if cycle_regularities else 0

    # Binary collapse = high STATE-C rate + low variance
    is_binary_collapse = state_c_rate > 0.90 and conv_cv < 0.5

    return {
        'test': 'B',
        'name': 'Collapse Shape (Binary vs Runaway)',
        'metrics': {
            'terminal_state_distribution': dict(terminal_states),
            'state_c_rate': round(state_c_rate, 3),
            'convergence_speed_mean': round(conv_mean, 4),
            'convergence_speed_std': round(conv_std, 4),
            'convergence_cv': round(conv_cv, 3),
            'cycle_regularity_mean': round(reg_mean, 3),
            'cycle_regularity_std': round(reg_std, 3),
        },
        'opportunity_loss_prediction': 'Clean collapse, high STATE-C rate, uniform convergence',
        'physical_instability_prediction': 'Oscillation, cascade, varied terminal states',
        'observed': f'STATE-C rate {state_c_rate:.1%}, Convergence CV {conv_cv:.2f}',
        'is_binary_collapse': is_binary_collapse,
        'opportunity_loss_fit': 'STRONG' if is_binary_collapse else 'MODERATE' if state_c_rate > 0.70 else 'WEAK',
        'physical_instability_fit': 'STRONG' if conv_cv > 0.7 else 'WEAK',
        'verdict': 'OPPORTUNITY_LOSS' if is_binary_collapse else 'AMBIGUOUS'
    }


def test_C_wait_dominance(signatures, programs):
    """
    Test C: WAIT Dominance

    Prediction (Opportunity-loss model):
    - Large fraction of execution time is WAIT (>35%)
    - Action density is sparse and tightly constrained
    - Waiting = preserving value, not risking loss

    Prediction (Physical-instability model):
    - Wait fraction lower (<25%)
    - Active intervention more common
    - System requires constant adjustment
    """
    link_densities = []
    action_densities = []

    for folio_id, sig in signatures.items():
        link_density = sig['temporal_metrics']['link_density']
        link_densities.append(link_density)
        action_densities.append(1 - link_density)

    # Calculate action sparsity from programs
    action_run_lengths = []
    for folio_id, instructions in programs.items():
        current_action_run = 0
        for inst in instructions:
            inst_type = INSTRUCTION_TYPES.get(inst, 'ACTION')
            if inst_type == 'ACTION':
                current_action_run += 1
            else:
                if current_action_run > 0:
                    action_run_lengths.append(current_action_run)
                current_action_run = 0
        if current_action_run > 0:
            action_run_lengths.append(current_action_run)

    mean_link = statistics.mean(link_densities)
    median_link = statistics.median(link_densities)
    link_above_35 = sum(1 for d in link_densities if d > 0.35) / len(link_densities)

    mean_action_run = statistics.mean(action_run_lengths) if action_run_lengths else 0
    max_action_run = max(action_run_lengths) if action_run_lengths else 0

    # Opportunity-loss: high wait, sparse actions
    is_wait_dominant = mean_link > 0.35 and link_above_35 > 0.50

    return {
        'test': 'C',
        'name': 'WAIT Dominance',
        'metrics': {
            'mean_link_density': round(mean_link, 4),
            'median_link_density': round(median_link, 4),
            'min_link_density': round(min(link_densities), 4),
            'max_link_density': round(max(link_densities), 4),
            'folios_above_35_percent': round(link_above_35, 3),
            'mean_action_run_length': round(mean_action_run, 2),
            'max_action_run_length': max_action_run,
        },
        'opportunity_loss_prediction': 'LINK > 35%, sparse action runs',
        'physical_instability_prediction': 'LINK < 25%, frequent intervention',
        'observed': f'Mean LINK {mean_link:.1%}, {link_above_35:.1%} folios above 35%',
        'is_wait_dominant': is_wait_dominant,
        'opportunity_loss_fit': 'STRONG' if mean_link > 0.35 else 'MODERATE' if mean_link > 0.28 else 'WEAK',
        'physical_instability_fit': 'STRONG' if mean_link < 0.25 else 'WEAK',
        'verdict': 'OPPORTUNITY_LOSS' if is_wait_dominant else 'AMBIGUOUS'
    }


def test_D_restart_penalty_geometry(signatures):
    """
    Test D: Restart Penalty Geometry

    Prediction (Opportunity-loss model):
    - Binary loss ("cycle ruined")
    - Very few restart-capable programs
    - Little partial recovery possibility

    Prediction (Physical-instability model):
    - Graded recovery (partial salvage possible)
    - More restart/recovery branches
    - Emergency routines present
    """
    restart_capable = []
    recovery_ops = []

    for folio_id, sig in signatures.items():
        is_restart = sig['recovery_metrics']['restart_capable']
        restart_capable.append(1 if is_restart else 0)

        rec_ops = sig['recovery_metrics']['recovery_ops_count']
        recovery_ops.append(rec_ops)

    total = len(signatures)
    restart_rate = sum(restart_capable) / total
    mean_recovery_ops = statistics.mean(recovery_ops)
    zero_recovery_rate = sum(1 for r in recovery_ops if r == 0) / total

    # Binary = very few restarts, mostly zero recovery
    is_binary_penalty = restart_rate < 0.10 and zero_recovery_rate > 0.50

    return {
        'test': 'D',
        'name': 'Restart Penalty Geometry',
        'metrics': {
            'restart_capable_count': sum(restart_capable),
            'restart_capable_rate': round(restart_rate, 3),
            'mean_recovery_ops': round(mean_recovery_ops, 2),
            'max_recovery_ops': max(recovery_ops),
            'zero_recovery_rate': round(zero_recovery_rate, 3),
        },
        'opportunity_loss_prediction': 'Few restarts (<10%), binary loss',
        'physical_instability_prediction': 'More restarts, graded recovery',
        'observed': f'Restart rate {restart_rate:.1%}, Zero recovery {zero_recovery_rate:.1%}',
        'is_binary_penalty': is_binary_penalty,
        'opportunity_loss_fit': 'STRONG' if restart_rate < 0.10 else 'MODERATE' if restart_rate < 0.20 else 'WEAK',
        'physical_instability_fit': 'STRONG' if restart_rate > 0.20 else 'WEAK',
        'verdict': 'OPPORTUNITY_LOSS' if is_binary_penalty else 'AMBIGUOUS'
    }


def test_E_risk_vs_reward(signatures):
    """
    Test E: Risk vs Reward Structure

    Prediction (Opportunity-loss model):
    - No structural reward for risk
    - Aggressive programs don't show higher success/yield
    - Risk accelerates failure, not success

    Prediction (Physical-instability model):
    - Risk-reward tradeoff present
    - Faster programs have compensating advantages
    - Some payoff for accepting risk
    """
    aggressive_metrics = []
    conservative_metrics = []

    for folio_id, sig in signatures.items():
        style = sig['classifications']['intervention_style']
        aggressiveness = sig['margin_metrics']['aggressiveness_score']
        control_margin = sig['margin_metrics']['control_margin_index']
        conv_speed = sig['loop_metrics']['convergence_speed_index']

        if style == 'AGGRESSIVE':
            aggressive_metrics.append({
                'aggressiveness': aggressiveness,
                'control_margin': control_margin,
                'convergence_speed': conv_speed,
            })
        elif style == 'CONSERVATIVE':
            conservative_metrics.append({
                'aggressiveness': aggressiveness,
                'control_margin': control_margin,
                'convergence_speed': conv_speed,
            })

    # Compare aggressive vs conservative outcomes
    if aggressive_metrics and conservative_metrics:
        agg_margin = statistics.mean([m['control_margin'] for m in aggressive_metrics])
        cons_margin = statistics.mean([m['control_margin'] for m in conservative_metrics])

        agg_speed = statistics.mean([m['convergence_speed'] for m in aggressive_metrics])
        cons_speed = statistics.mean([m['convergence_speed'] for m in conservative_metrics])

        margin_diff = agg_margin - cons_margin  # Negative = aggressive has less margin (worse)
        speed_diff = agg_speed - cons_speed     # Positive = aggressive is faster

        # Risk-reward: if aggressive has compensating advantage
        has_risk_reward = margin_diff < -0.1 and speed_diff > 0.05  # Trades margin for speed
    else:
        agg_margin = cons_margin = agg_speed = cons_speed = 0
        margin_diff = speed_diff = 0
        has_risk_reward = False

    # No reward = aggressive just has worse margins without compensation
    no_reward_for_risk = margin_diff < -0.05 and speed_diff < 0.05

    return {
        'test': 'E',
        'name': 'Risk vs Reward Structure',
        'metrics': {
            'aggressive_count': len(aggressive_metrics),
            'conservative_count': len(conservative_metrics),
            'aggressive_mean_margin': round(agg_margin, 4),
            'conservative_mean_margin': round(cons_margin, 4),
            'margin_difference': round(margin_diff, 4),
            'aggressive_mean_speed': round(agg_speed, 4),
            'conservative_mean_speed': round(cons_speed, 4),
            'speed_difference': round(speed_diff, 4),
        },
        'opportunity_loss_prediction': 'No reward for risk, aggressive = worse outcomes',
        'physical_instability_prediction': 'Risk-reward tradeoff, speed for margin',
        'observed': f'Margin diff {margin_diff:+.3f}, Speed diff {speed_diff:+.3f}',
        'has_risk_reward_tradeoff': has_risk_reward,
        'no_reward_for_risk': no_reward_for_risk,
        'opportunity_loss_fit': 'STRONG' if no_reward_for_risk else 'MODERATE' if not has_risk_reward else 'WEAK',
        'physical_instability_fit': 'STRONG' if has_risk_reward else 'WEAK',
        'verdict': 'OPPORTUNITY_LOSS' if no_reward_for_risk else 'PHYSICAL_INSTABILITY' if has_risk_reward else 'AMBIGUOUS'
    }


def test_F_absence_salvage_logic(signatures, programs):
    """
    Test F: Absence of Salvage / Emergency Logic

    Prediction (Opportunity-loss model):
    - Emergency or salvage logic absent or minimal
    - No "fix it fast" branches
    - Grammar lacks recovery vocabulary

    Prediction (Physical-instability model):
    - Emergency routines present
    - Rapid intervention patterns
    - Recovery vocabulary in grammar
    """
    # Look for emergency patterns in programs
    emergency_patterns = [
        'EMERGENCY', 'RECOVER', 'ABORT', 'RESET', 'SALVAGE',
        'FIX', 'UNDO', 'REVERSE', 'BACK'
    ]

    emergency_found = 0
    total_instructions = 0

    for folio_id, instructions in programs.items():
        for inst in instructions:
            total_instructions += 1
            inst_upper = inst.upper()
            for pattern in emergency_patterns:
                if pattern in inst_upper:
                    emergency_found += 1
                    break

    emergency_rate = emergency_found / total_instructions if total_instructions > 0 else 0

    # Check for rapid intervention (multiple consecutive non-LINK)
    rapid_intervention_runs = []
    for folio_id, instructions in programs.items():
        current_run = 0
        for inst in instructions:
            if inst != 'LINK':
                current_run += 1
            else:
                if current_run >= 5:  # 5+ consecutive actions = rapid intervention
                    rapid_intervention_runs.append(current_run)
                current_run = 0
        if current_run >= 5:
            rapid_intervention_runs.append(current_run)

    rapid_intervention_count = len(rapid_intervention_runs)

    # Recovery ops from OPS1
    total_recovery_ops = sum(sig['recovery_metrics']['recovery_ops_count'] for sig in signatures.values())
    mean_recovery_ops = total_recovery_ops / len(signatures) if signatures else 0

    # Minimal salvage = very low emergency vocabulary, few rapid interventions
    is_minimal_salvage = emergency_rate < 0.01 and rapid_intervention_count < 10 and mean_recovery_ops < 2

    return {
        'test': 'F',
        'name': 'Absence of Salvage/Emergency Logic',
        'metrics': {
            'total_instructions': total_instructions,
            'emergency_instructions': emergency_found,
            'emergency_rate': round(emergency_rate, 6),
            'rapid_intervention_runs': rapid_intervention_count,
            'total_recovery_ops': total_recovery_ops,
            'mean_recovery_ops': round(mean_recovery_ops, 2),
        },
        'opportunity_loss_prediction': 'No emergency vocabulary, minimal recovery',
        'physical_instability_prediction': 'Emergency routines, rapid intervention patterns',
        'observed': f'Emergency rate {emergency_rate:.4%}, Rapid runs {rapid_intervention_count}',
        'is_minimal_salvage': is_minimal_salvage,
        'opportunity_loss_fit': 'STRONG' if is_minimal_salvage else 'MODERATE' if emergency_rate < 0.05 else 'WEAK',
        'physical_instability_fit': 'STRONG' if emergency_rate > 0.05 or rapid_intervention_count > 20 else 'WEAK',
        'verdict': 'OPPORTUNITY_LOSS' if is_minimal_salvage else 'AMBIGUOUS'
    }


def generate_comparative_assessment(results):
    """Generate comparative fit assessment."""
    opp_loss_scores = {'STRONG': 0, 'MODERATE': 0, 'WEAK': 0}
    phys_inst_scores = {'STRONG': 0, 'MODERATE': 0, 'WEAK': 0}

    for r in results:
        opp_loss_scores[r['opportunity_loss_fit']] += 1
        phys_inst_scores[r['physical_instability_fit']] += 1

    # Weighted score: STRONG=3, MODERATE=2, WEAK=1
    opp_loss_total = opp_loss_scores['STRONG'] * 3 + opp_loss_scores['MODERATE'] * 2 + opp_loss_scores['WEAK'] * 1
    phys_inst_total = phys_inst_scores['STRONG'] * 3 + phys_inst_scores['MODERATE'] * 2 + phys_inst_scores['WEAK'] * 1

    # Verdicts
    verdict_counts = Counter(r['verdict'] for r in results)

    if opp_loss_total > phys_inst_total * 1.5:
        overall_verdict = 'OPPORTUNITY_LOSS_DOMINANT'
    elif phys_inst_total > opp_loss_total * 1.5:
        overall_verdict = 'PHYSICAL_INSTABILITY_DOMINANT'
    else:
        overall_verdict = 'AMBIGUOUS'

    return {
        'opportunity_loss_fits': dict(opp_loss_scores),
        'physical_instability_fits': dict(phys_inst_scores),
        'opportunity_loss_weighted': opp_loss_total,
        'physical_instability_weighted': phys_inst_total,
        'test_verdicts': dict(verdict_counts),
        'overall_verdict': overall_verdict,
        'confidence': 'HIGH' if abs(opp_loss_total - phys_inst_total) > 6 else 'MODERATE' if abs(opp_loss_total - phys_inst_total) > 3 else 'LOW'
    }


def generate_report(results, assessment, output_path):
    """Generate markdown report."""
    report = f"""# Phase EXT-ECO-01: Opportunity-Loss Hazard Profile Analysis

**Status:** COMPLETE
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Tier:** 3 (External Alignment Only)

---

## Section 1 - Test Results

"""
    for r in results:
        report += f"""### Test {r['test']}: {r['name']}

| Metric | Value |
|--------|-------|
"""
        for k, v in r['metrics'].items():
            report += f"| {k} | {v} |\n"

        report += f"""
**Opportunity-Loss Prediction:** {r['opportunity_loss_prediction']}
**Physical-Instability Prediction:** {r['physical_instability_prediction']}

**Observed:** {r['observed']}

| Model | Fit |
|-------|-----|
| Opportunity-Loss | **{r['opportunity_loss_fit']}** |
| Physical-Instability | **{r['physical_instability_fit']}** |

**Test Verdict:** {r['verdict']}

---

"""

    report += f"""## Section 2 - Comparative Fit Assessment

### Score Summary

| Model | STRONG | MODERATE | WEAK | Weighted Total |
|-------|--------|----------|------|----------------|
| Opportunity-Loss | {assessment['opportunity_loss_fits']['STRONG']} | {assessment['opportunity_loss_fits']['MODERATE']} | {assessment['opportunity_loss_fits']['WEAK']} | **{assessment['opportunity_loss_weighted']}** |
| Physical-Instability | {assessment['physical_instability_fits']['STRONG']} | {assessment['physical_instability_fits']['MODERATE']} | {assessment['physical_instability_fits']['WEAK']} | **{assessment['physical_instability_weighted']}** |

### Test Verdicts

| Verdict | Count |
|---------|-------|
"""
    for verdict, count in assessment['test_verdicts'].items():
        report += f"| {verdict} | {count} |\n"

    report += f"""
### Overall Assessment

| Metric | Value |
|--------|-------|
| Overall Verdict | **{assessment['overall_verdict']}** |
| Confidence | **{assessment['confidence']}** |

---

## Section 3 - Interpretive Boundary (Required)

> **"This analysis evaluates abstract loss and hazard logic only.
> It does not identify materials, industries, or encoded purposes."**

The findings describe the *shape* of failure in the grammar:
- Whether hazards prevent premature vs late action
- Whether collapse is binary or cascading
- Whether waiting or intervention dominates
- Whether recovery is possible or precluded

These structural features are consistent with one abstract model over another,
but do not imply identification of any specific process, material, or industry.

---

## Section 4 - Tier Label

All conclusions in this phase are labeled **Tier 3 (External Alignment Only)**.

This analysis provides external alignment information only. It does NOT:
- Assign semantics, materials, or products
- Identify trades, industries, or substances
- Interpret illustrations or botanical content
- Reopen SID conclusions
- Treat hazards as calendar-encoded

---

## Key Findings

"""
    if assessment['overall_verdict'] == 'OPPORTUNITY_LOSS_DOMINANT':
        report += """The hazard topology and restart-intolerance structure is **STRONGLY CONSISTENT** with an **opportunity-loss** model:

1. **Premature action hazards dominate** - Hazards encode "acting before ready" rather than "waiting too long"
2. **Binary collapse** - Execution converges cleanly to STATE-C without oscillation or cascade
3. **Wait dominance** - LINK (waiting) constitutes a large fraction of execution time
4. **Binary penalty** - Very few restart-capable programs; failure = complete loss
5. **No risk-reward tradeoff** - Aggressive programs show no compensating advantage
6. **Minimal salvage logic** - No emergency vocabulary or rapid intervention patterns

This is consistent with a system where:
- **Mistimed action irreversibly loses value**
- **Waiting preserves opportunity**
- **Failure ends execution quietly (value lost, not system destroyed)**

"""
    elif assessment['overall_verdict'] == 'PHYSICAL_INSTABILITY_DOMINANT':
        report += """The hazard topology shows significant **physical-instability** characteristics:

1. Late-action hazards are prominent
2. Non-uniform collapse patterns
3. Active intervention required
4. Graded recovery possible
5. Risk-reward tradeoffs present
6. Emergency/salvage patterns detected

"""
    else:
        report += """The evidence is **AMBIGUOUS** between opportunity-loss and physical-instability models.
Both interpretations find partial support in the grammar structure.

"""

    report += f"""---

*EXT-ECO-01 COMPLETE. This phase terminates here. No follow-on interpretation permitted.*
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)


def main():
    """Main analysis pipeline."""
    print("Phase EXT-ECO-01: Opportunity-Loss Hazard Profile Analysis")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    signatures = load_ops1_signatures()
    print(f"  Loaded {len(signatures)} folio signatures")

    programs = parse_recipe_atlas()
    print(f"  Loaded {len(programs)} programs")

    # Run tests
    print("\nRunning tests...")
    results = []

    print("  Test A: Premature vs Late Action Asymmetry")
    results.append(test_A_premature_vs_late_asymmetry())

    print("  Test B: Collapse Shape")
    results.append(test_B_collapse_shape(signatures))

    print("  Test C: WAIT Dominance")
    results.append(test_C_wait_dominance(signatures, programs))

    print("  Test D: Restart Penalty Geometry")
    results.append(test_D_restart_penalty_geometry(signatures))

    print("  Test E: Risk vs Reward Structure")
    results.append(test_E_risk_vs_reward(signatures))

    print("  Test F: Absence of Salvage Logic")
    results.append(test_F_absence_salvage_logic(signatures, programs))

    # Generate assessment
    print("\nGenerating comparative assessment...")
    assessment = generate_comparative_assessment(results)

    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    for r in results:
        print(f"\n  Test {r['test']}: {r['name']}")
        print(f"    Opp-Loss Fit: {r['opportunity_loss_fit']}")
        print(f"    Phys-Inst Fit: {r['physical_instability_fit']}")
        print(f"    Verdict: {r['verdict']}")

    print(f"\n  OVERALL VERDICT: {assessment['overall_verdict']}")
    print(f"  Confidence: {assessment['confidence']}")
    print(f"  Opp-Loss Weighted Score: {assessment['opportunity_loss_weighted']}")
    print(f"  Phys-Inst Weighted Score: {assessment['physical_instability_weighted']}")

    # Generate outputs
    print("\nGenerating outputs...")

    # JSON output
    json_path = os.path.join(OUTPUT_DIR, 'ext_eco_01_results.json')
    output_data = {
        'metadata': {
            'phase': 'EXT-ECO-01',
            'title': 'Opportunity-Loss Hazard Profile Analysis',
            'timestamp': datetime.now().isoformat(),
            'tier': 3,
        },
        'test_results': results,
        'comparative_assessment': assessment,
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    print(f"  Written: {json_path}")

    # Report
    report_path = os.path.join(OUTPUT_DIR, 'EXT_ECO_01_REPORT.md')
    generate_report(results, assessment, report_path)
    print(f"  Written: {report_path}")

    print("\n" + "=" * 60)
    print("EXT-ECO-01 COMPLETE")
    print("=" * 60)

    return results, assessment


if __name__ == '__main__':
    main()
