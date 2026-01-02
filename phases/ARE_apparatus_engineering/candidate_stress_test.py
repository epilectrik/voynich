#!/usr/bin/env python3
"""
Candidate Elimination Stress Test
Head-to-head adversarial comparison of HIGH similarity candidates against
the locked Voynich control signature.

Interpretive Firewall: Active
Goal: Elimination, not confirmation
"""

import json
from pathlib import Path

# Voynich reference signature (LOCKED - DO NOT MODIFY)
VOYNICH = {
    "numerical": {
        "F01": 1.0, "F02": 0.0, "F03": 17, "F04": 5,
        "F05": 1.0, "F06": 1, "F07": 2.37, "F08": 1.0,
        "F09": 0.946, "F10": 0.977, "F11": 1.0, "F12": 0.68,
        "F13": 1.0, "F14": 1.0, "F15": 3, "F16": 2.64,
        "F17": 1.0, "F18": 0.35
    },
    "categorical": {
        "C01": "MONOSTATE", "C02": "CLOSED_LOOP", "C03": "EXPERT",
        "C04": "EXTERNAL", "C05": "NONE", "C06": "ABSENT",
        "C07": "ABSENT", "C08": "CONTINUOUS", "C09": "RECOVERY",
        "C10": "EXPLICIT", "C11": "HIGH", "C12": "PRESENT",
        "C13": "PRESENT", "C14": "STRICT_LOCAL", "C15": "TEACHING"
    }
}

# HIGH similarity candidates (>85%)
HIGH_CANDIDATES = {
    "P01": {
        "name": "Reflux Distillation",
        "domain": "Chemical Process",
        "similarity": 0.952,
        "numerical": {
            "F01": 0.95, "F02": 0.1, "F03": 15, "F04": 5,
            "F05": 0.95, "F06": 1, "F07": 2.5, "F08": 0.9,
            "F09": 0.9, "F10": 0.95, "F11": 0.85, "F12": 0.5,
            "F13": 0.9, "F14": 0.9, "F15": 3, "F16": 2.5,
            "F17": 0.9, "F18": 0.4
        },
        "categorical": {
            "C01": "MONOSTATE", "C02": "CLOSED_LOOP", "C03": "EXPERT",
            "C04": "EXTERNAL", "C05": "NONE", "C06": "ABSENT",
            "C07": "ABSENT", "C08": "CONTINUOUS", "C09": "RECOVERY",
            "C10": "EXPLICIT", "C11": "HIGH", "C12": "PRESENT",
            "C13": "PRESENT", "C14": "STRICT_LOCAL", "C15": "TEACHING"
        },
        "notes": "Continuous cyclic operation, operator checks purity externally, flooding/weeping hazards"
    },
    "P07": {
        "name": "Steam Boiler Pressure Control",
        "domain": "Industrial Systems",
        "similarity": 0.858,
        "numerical": {
            "F01": 0.95, "F02": 0.0, "F03": 20, "F04": 5,
            "F05": 0.98, "F06": 1, "F07": 2.0, "F08": 0.95,
            "F09": 0.85, "F10": 0.9, "F11": 0.85, "F12": 0.4,
            "F13": 0.8, "F14": 0.9, "F15": 3, "F16": 2.3,
            "F17": 0.9, "F18": 0.45
        },
        "categorical": {
            "C01": "MONOSTATE", "C02": "CLOSED_LOOP", "C03": "EXPERT",
            "C04": "CONTINUOUS", "C05": "FIXED", "C06": "ABSENT",
            "C07": "ABSENT", "C08": "CONTINUOUS", "C09": "RECOVERY",
            "C10": "EXPLICIT", "C11": "HIGH", "C12": "PRESENT",
            "C13": "PRESENT", "C14": "STRICT_LOCAL", "C15": "OPERATIONAL"
        },
        "notes": "Redundant safety, pressure limits, manual reset on high-limit"
    },
    "P11": {
        "name": "Biological Homeostasis",
        "domain": "Biological Systems",
        "similarity": 0.871,
        "numerical": {
            "F01": 1.0, "F02": 0.0, "F03": 20, "F04": 8,
            "F05": 1.0, "F06": 1, "F07": 3.0, "F08": 0.98,
            "F09": 0.95, "F10": 0.98, "F11": 0.95, "F12": 0.5,
            "F13": 0.95, "F14": 1.0, "F15": 5, "F16": 2.5,
            "F17": 0.9, "F18": 0.4
        },
        "categorical": {
            "C01": "MONOSTATE", "C02": "CLOSED_LOOP", "C03": "EXPERT",
            "C04": "CONTINUOUS", "C05": "NONE", "C06": "ABSENT",
            "C07": "ABSENT", "C08": "CONTINUOUS", "C09": "RECOVERY",
            "C10": "EXPLICIT", "C11": "HIGH", "C12": "PRESENT",
            "C13": "PRESENT", "C14": "LOCAL", "C15": "OPERATIONAL"
        },
        "notes": "Negative feedback dominant, setpoint maintenance, redundant systems"
    },
    "P21": {
        "name": "Blood Glucose Regulation",
        "domain": "Biological Systems",
        "similarity": 0.886,
        "numerical": {
            "F01": 1.0, "F02": 0.0, "F03": 10, "F04": 4,
            "F05": 1.0, "F06": 1, "F07": 2.0, "F08": 0.95,
            "F09": 1.0, "F10": 0.98, "F11": 0.9, "F12": 0.6,
            "F13": 0.95, "F14": 1.0, "F15": 3, "F16": 2.5,
            "F17": 0.85, "F18": 0.4
        },
        "categorical": {
            "C01": "MONOSTATE", "C02": "CLOSED_LOOP", "C03": "EXPERT",
            "C04": "CONTINUOUS", "C05": "NONE", "C06": "ABSENT",
            "C07": "ABSENT", "C08": "CONTINUOUS", "C09": "RECOVERY",
            "C10": "EXPLICIT", "C11": "HIGH", "C12": "PRESENT",
            "C13": "PRESENT", "C14": "LOCAL", "C15": "OPERATIONAL"
        },
        "notes": "Insulin/glucagon antagonism, tight setpoint, rapid response"
    },
    "P22": {
        "name": "Distillation Column (Industrial)",
        "domain": "Chemical Process",
        "similarity": 0.885,
        "numerical": {
            "F01": 0.95, "F02": 0.1, "F03": 18, "F04": 5,
            "F05": 0.92, "F06": 1, "F07": 2.5, "F08": 0.88,
            "F09": 0.9, "F10": 0.92, "F11": 0.8, "F12": 0.45,
            "F13": 0.85, "F14": 0.92, "F15": 4, "F16": 2.6,
            "F17": 0.88, "F18": 0.42
        },
        "categorical": {
            "C01": "MONOSTATE", "C02": "CLOSED_LOOP", "C03": "EXPERT",
            "C04": "EXTERNAL", "C05": "VARIABLE", "C06": "ABSENT",
            "C07": "ABSENT", "C08": "CONTINUOUS", "C09": "RECOVERY",
            "C10": "EXPLICIT", "C11": "HIGH", "C12": "PRESENT",
            "C13": "PRESENT", "C14": "STRICT_LOCAL", "C15": "OPERATIONAL"
        },
        "notes": "MPC control, feed composition disturbances, flooding/weeping hazards"
    },
    "P25": {
        "name": "Temperature Regulation (Mammalian)",
        "domain": "Biological Systems",
        "similarity": 0.878,
        "numerical": {
            "F01": 1.0, "F02": 0.0, "F03": 15, "F04": 5,
            "F05": 1.0, "F06": 1, "F07": 2.5, "F08": 0.95,
            "F09": 0.95, "F10": 0.97, "F11": 0.9, "F12": 0.5,
            "F13": 0.9, "F14": 1.0, "F15": 4, "F16": 2.3,
            "F17": 0.85, "F18": 0.35
        },
        "categorical": {
            "C01": "MONOSTATE", "C02": "CLOSED_LOOP", "C03": "EXPERT",
            "C04": "CONTINUOUS", "C05": "NONE", "C06": "ABSENT",
            "C07": "ABSENT", "C08": "CONTINUOUS", "C09": "RECOVERY",
            "C10": "EXPLICIT", "C11": "HIGH", "C12": "PRESENT",
            "C13": "PRESENT", "C14": "LOCAL", "C15": "OPERATIONAL"
        },
        "notes": "Hypothalamus setpoint, sweating/shivering, vasodilation/constriction"
    }
}

def test_1_perturbation_response(candidate_id, candidate):
    """
    TEST 1: Perturbation Response Shape
    - Voynich requires continuous micro-intervention
    - Voynich has perfect perturbation tolerance (F11=1.0)
    - Voynich tolerates redundancy (F13=1.0) and compression (F12=0.68)

    Elimination rule: Systems requiring discrete, episodic correction fail
    """
    v = VOYNICH
    c = candidate

    results = {
        "test_name": "Perturbation Response Shape",
        "voynich_profile": {
            "intervention_style": v["categorical"]["C08"],
            "perturbation_tolerance": v["numerical"]["F11"],
            "compression_tolerance": v["numerical"]["F12"],
            "redundancy_tolerance": v["numerical"]["F13"],
            "recovery_steps": v["numerical"]["F07"]
        },
        "candidate_profile": {
            "intervention_style": c["categorical"]["C08"],
            "perturbation_tolerance": c["numerical"]["F11"],
            "compression_tolerance": c["numerical"]["F12"],
            "redundancy_tolerance": c["numerical"]["F13"],
            "recovery_steps": c["numerical"]["F07"]
        },
        "checks": {}
    }

    # Check 1: Intervention style must be CONTINUOUS
    continuous_match = c["categorical"]["C08"] == "CONTINUOUS"
    results["checks"]["continuous_intervention"] = {
        "pass": continuous_match,
        "reason": f"Candidate has {c['categorical']['C08']} intervention" +
                  (" (matches Voynich)" if continuous_match else " (Voynich requires CONTINUOUS)")
    }

    # Check 2: Perturbation tolerance should be close to 1.0
    perturb_delta = abs(v["numerical"]["F11"] - c["numerical"]["F11"])
    perturb_threshold = 0.2  # Allow 0.2 deviation
    perturb_pass = perturb_delta <= perturb_threshold
    results["checks"]["perturbation_tolerance"] = {
        "pass": perturb_pass,
        "delta": perturb_delta,
        "reason": f"Delta {perturb_delta:.2f} {'≤' if perturb_pass else '>'} threshold {perturb_threshold}"
    }

    # Check 3: Recovery should be fast (similar to Voynich ~2.4 steps)
    recovery_delta = abs(v["numerical"]["F07"] - c["numerical"]["F07"])
    recovery_threshold = 1.0  # Allow 1.0 step difference
    recovery_pass = recovery_delta <= recovery_threshold
    results["checks"]["recovery_speed"] = {
        "pass": recovery_pass,
        "delta": recovery_delta,
        "reason": f"Recovery steps delta {recovery_delta:.2f} {'≤' if recovery_pass else '>'} threshold {recovery_threshold}"
    }

    # Check 4: Redundancy tolerance (Voynich F13=1.0)
    redundancy_delta = abs(v["numerical"]["F13"] - c["numerical"]["F13"])
    redundancy_threshold = 0.2
    redundancy_pass = redundancy_delta <= redundancy_threshold
    results["checks"]["redundancy_tolerance"] = {
        "pass": redundancy_pass,
        "delta": redundancy_delta,
        "reason": f"Redundancy delta {redundancy_delta:.2f} {'≤' if redundancy_pass else '>'} threshold {redundancy_threshold}"
    }

    # Overall verdict
    passed = sum(1 for c in results["checks"].values() if c["pass"])
    total = len(results["checks"])
    results["verdict"] = "PASS" if passed >= 3 else "MARGINAL" if passed >= 2 else "FAIL"
    results["score"] = passed / total

    return results


def test_2_hard_hazard_topology(candidate_id, candidate):
    """
    TEST 2: Hard Hazard Topology
    - Voynich has 17 EXPLICIT forbidden transitions
    - ALL are bidirectional (mutual exclusions, not one-way causal)
    - This indicates HARD hazards (catastrophic, not graded)

    Elimination rule: Systems without hard hazards fail alignment
    """
    v = VOYNICH
    c = candidate

    results = {
        "test_name": "Hard Hazard Topology",
        "voynich_profile": {
            "forbidden_count": v["numerical"]["F03"],
            "failure_classes": v["numerical"]["F04"],
            "hazard_encoding": v["categorical"]["C10"],
            "forbidden_bidirectionality": v["numerical"]["F17"]
        },
        "candidate_profile": {
            "forbidden_count": c["numerical"]["F03"],
            "failure_classes": c["numerical"]["F04"],
            "hazard_encoding": c["categorical"]["C10"],
            "forbidden_bidirectionality": c["numerical"]["F17"]
        },
        "checks": {}
    }

    # Check 1: Hazard encoding must be EXPLICIT
    explicit_match = c["categorical"]["C10"] == "EXPLICIT"
    results["checks"]["explicit_hazards"] = {
        "pass": explicit_match,
        "reason": f"Candidate has {c['categorical']['C10']} hazard encoding" +
                  (" (matches Voynich)" if explicit_match else " (Voynich requires EXPLICIT)")
    }

    # Check 2: Must have substantial forbidden transitions (Voynich has 17)
    forbidden_count = c["numerical"]["F03"]
    forbidden_threshold = 10  # At least 10 to be comparable
    forbidden_pass = forbidden_count >= forbidden_threshold
    results["checks"]["forbidden_count"] = {
        "pass": forbidden_pass,
        "count": forbidden_count,
        "reason": f"Forbidden count {forbidden_count} {'≥' if forbidden_pass else '<'} threshold {forbidden_threshold}"
    }

    # Check 3: Bidirectionality should be high (Voynich F17=1.0)
    # High bidirectionality = mutual exclusions = hard hazards
    bidir = c["numerical"]["F17"]
    bidir_threshold = 0.8
    bidir_pass = bidir >= bidir_threshold
    results["checks"]["bidirectionality"] = {
        "pass": bidir_pass,
        "value": bidir,
        "reason": f"Bidirectionality {bidir:.2f} {'≥' if bidir_pass else '<'} threshold {bidir_threshold}"
    }

    # Check 4: Hard hazard nature assessment
    # Biological systems typically have GRADED responses, not BINARY failures
    domain = candidate.get("domain", "Unknown")
    is_biological = "Biological" in domain
    hard_hazard_concern = is_biological

    results["checks"]["hazard_nature"] = {
        "pass": not hard_hazard_concern,
        "domain": domain,
        "reason": "Biological systems typically have graded degradation, not hard failures" if hard_hazard_concern
                  else "Industrial/chemical systems typically have hard failure modes"
    }

    # Overall verdict
    passed = sum(1 for c in results["checks"].values() if c["pass"])
    total = len(results["checks"])
    results["verdict"] = "PASS" if passed >= 3 else "MARGINAL" if passed >= 2 else "FAIL"
    results["score"] = passed / total

    return results


def test_3_non_intervention_role(candidate_id, candidate):
    """
    TEST 3: Non-Intervention Role (LINK analog)
    - Voynich has explicit LINK operator = intentional non-intervention
    - "Waiting" must be a meaningful control action, not just idling
    - Requires EXTERNAL termination (operator decides when done)

    Elimination rule: Systems where waiting is not a control dimension fail
    """
    v = VOYNICH
    c = candidate

    results = {
        "test_name": "Non-Intervention Role (LINK Analog)",
        "voynich_profile": {
            "termination": v["categorical"]["C04"],
            "operator_model": v["categorical"]["C03"],
            "intervention_style": v["categorical"]["C08"],
            "intent": v["categorical"]["C15"]
        },
        "candidate_profile": {
            "termination": c["categorical"]["C04"],
            "operator_model": c["categorical"]["C03"],
            "intervention_style": c["categorical"]["C08"],
            "intent": c["categorical"]["C15"]
        },
        "checks": {}
    }

    # Check 1: Termination must be EXTERNAL (operator decides)
    # CONTINUOUS = autonomous, no external operator decision
    termination_match = c["categorical"]["C04"] == "EXTERNAL"
    results["checks"]["external_termination"] = {
        "pass": termination_match,
        "reason": f"Candidate has {c['categorical']['C04']} termination" +
                  (" (matches Voynich EXTERNAL)" if termination_match else
                   " (Voynich requires EXTERNAL - operator decides completion)")
    }

    # Check 2: Operator presence check
    # Biological systems are AUTONOMOUS - no external operator
    domain = candidate.get("domain", "Unknown")
    is_biological = "Biological" in domain
    has_operator = not is_biological  # Biological = autonomous

    results["checks"]["operator_presence"] = {
        "pass": has_operator,
        "domain": domain,
        "reason": "System is autonomous (no external operator)" if not has_operator
                  else "System has external operator making control decisions"
    }

    # Check 3: Deliberate non-intervention possibility
    # In distillation: reflux = deliberate waiting
    # In biological: "waiting" is emergent, not deliberate
    deliberate_wait = has_operator and c["categorical"]["C08"] == "CONTINUOUS"
    results["checks"]["deliberate_non_intervention"] = {
        "pass": deliberate_wait,
        "reason": "Operator can deliberately choose non-intervention as control action" if deliberate_wait
                  else "Non-intervention is not a deliberate operator choice"
    }

    # Check 4: Teaching/instructional nature
    # Voynich is a TEACHING document - records operator decisions
    intent = c["categorical"]["C15"]
    teaching_match = intent == "TEACHING"
    results["checks"]["teaching_intent"] = {
        "pass": teaching_match,
        "reason": f"Intent is {intent}" +
                  (" (matches Voynich TEACHING)" if teaching_match else
                   " (Voynich is a TEACHING document recording operator decisions)")
    }

    # Overall verdict
    passed = sum(1 for c in results["checks"].values() if c["pass"])
    total = len(results["checks"])
    results["verdict"] = "PASS" if passed >= 3 else "MARGINAL" if passed >= 2 else "FAIL"
    results["score"] = passed / total

    return results


def test_4_mode_regime_multiplicity(candidate_id, candidate):
    """
    TEST 4: Mode/Regime Multiplicity
    - Voynich converges to SINGLE viable regime (STATE-C only)
    - No mode switching (C06=ABSENT)
    - No branching logic (C07=ABSENT)

    Elimination rule: Multi-regime systems without forced collapse fail
    """
    v = VOYNICH
    c = candidate

    results = {
        "test_name": "Mode/Regime Multiplicity",
        "voynich_profile": {
            "topology": v["categorical"]["C01"],
            "attractor_count": v["numerical"]["F06"],
            "mode_switching": v["categorical"]["C06"],
            "branching": v["categorical"]["C07"]
        },
        "candidate_profile": {
            "topology": c["categorical"]["C01"],
            "attractor_count": c["numerical"]["F06"],
            "mode_switching": c["categorical"]["C06"],
            "branching": c["categorical"]["C07"]
        },
        "checks": {}
    }

    # Check 1: Must be MONOSTATE
    monostate_match = c["categorical"]["C01"] == "MONOSTATE"
    results["checks"]["monostate_topology"] = {
        "pass": monostate_match,
        "reason": f"Candidate topology is {c['categorical']['C01']}" +
                  (" (matches Voynich MONOSTATE)" if monostate_match else
                   " (Voynich requires single viable regime)")
    }

    # Check 2: Single attractor
    attractor_count = c["numerical"]["F06"]
    single_attractor = attractor_count == 1
    results["checks"]["single_attractor"] = {
        "pass": single_attractor,
        "count": attractor_count,
        "reason": f"Attractor count {attractor_count}" +
                  (" (matches Voynich single regime)" if single_attractor else
                   " (Voynich has single attractor)")
    }

    # Check 3: No mode switching
    no_modes = c["categorical"]["C06"] == "ABSENT"
    results["checks"]["no_mode_switching"] = {
        "pass": no_modes,
        "reason": f"Mode switching is {c['categorical']['C06']}" +
                  (" (matches Voynich ABSENT)" if no_modes else
                   " (Voynich has no mode switching)")
    }

    # Check 4: No branching logic
    no_branching = c["categorical"]["C07"] == "ABSENT"
    results["checks"]["no_branching"] = {
        "pass": no_branching,
        "reason": f"Branching logic is {c['categorical']['C07']}" +
                  (" (matches Voynich ABSENT)" if no_branching else
                   " (Voynich has no conditional branching)")
    }

    # Overall verdict
    passed = sum(1 for c in results["checks"].values() if c["pass"])
    total = len(results["checks"])
    results["verdict"] = "PASS" if passed >= 3 else "MARGINAL" if passed >= 2 else "FAIL"
    results["score"] = passed / total

    return results


def test_5_operator_granularity(candidate_id, candidate):
    """
    TEST 5: Operator Granularity & Expertise
    - Voynich assumes EXPERT operator
    - No parameter tuning (C05=NONE)
    - No automated safeguards
    - TEACHING intent (document for transmission)

    Elimination rule: Systems designed for novice or automated control are downgraded
    """
    v = VOYNICH
    c = candidate

    results = {
        "test_name": "Operator Granularity & Expertise",
        "voynich_profile": {
            "operator_model": v["categorical"]["C03"],
            "parameters": v["categorical"]["C05"],
            "intent": v["categorical"]["C15"],
            "dependency": v["categorical"]["C14"]
        },
        "candidate_profile": {
            "operator_model": c["categorical"]["C03"],
            "parameters": c["categorical"]["C05"],
            "intent": c["categorical"]["C15"],
            "dependency": c["categorical"]["C14"]
        },
        "checks": {}
    }

    # Check 1: Expert operator model
    expert_match = c["categorical"]["C03"] == "EXPERT"
    results["checks"]["expert_operator"] = {
        "pass": expert_match,
        "reason": f"Operator model is {c['categorical']['C03']}" +
                  (" (matches Voynich EXPERT)" if expert_match else
                   " (Voynich requires expert-level competence)")
    }

    # Check 2: Parameter handling
    # Voynich has NONE - no parameter tuning
    param = c["categorical"]["C05"]
    param_match = param == "NONE"
    results["checks"]["no_parameters"] = {
        "pass": param_match,
        "reason": f"Parameter dependency is {param}" +
                  (" (matches Voynich NONE)" if param_match else
                   " (Voynich has no parameter tuning)")
    }

    # Check 3: Local dependency (strict = minimal safeguards)
    dep = c["categorical"]["C14"]
    strict_local = dep in ["STRICT_LOCAL", "LOCAL"]
    results["checks"]["local_dependency"] = {
        "pass": strict_local,
        "reason": f"Dependency is {dep}" +
                  (" (compatible with Voynich STRICT_LOCAL)" if strict_local else
                   " (Voynich has strict local dependency)")
    }

    # Check 4: Operator actually exists (biological systems are autonomous)
    domain = candidate.get("domain", "Unknown")
    is_biological = "Biological" in domain
    has_external_operator = not is_biological

    results["checks"]["external_operator_exists"] = {
        "pass": has_external_operator,
        "domain": domain,
        "reason": "System has external human operator" if has_external_operator
                  else "System is autonomous - 'expert' is the system itself, not a human operator"
    }

    # Overall verdict
    passed = sum(1 for c in results["checks"].values() if c["pass"])
    total = len(results["checks"])
    results["verdict"] = "PASS" if passed >= 3 else "MARGINAL" if passed >= 2 else "FAIL"
    results["score"] = passed / total

    return results


def test_6_representation_invariance(candidate_id, candidate):
    """
    TEST 6: Invariance Under Representation Perturbation
    - Voynich grammar remains legal under massive syntactic perturbation (F11=1.0)
    - System is robust to representation changes

    Elimination rule: Candidates fragile to representation change lose alignment
    """
    v = VOYNICH
    c = candidate

    results = {
        "test_name": "Representation Invariance",
        "voynich_profile": {
            "perturbation_tolerance": v["numerical"]["F11"],
            "compression_tolerance": v["numerical"]["F12"],
            "cycle_closure": v["numerical"]["F10"],
            "reversibility": v["numerical"]["F09"]
        },
        "candidate_profile": {
            "perturbation_tolerance": c["numerical"]["F11"],
            "compression_tolerance": c["numerical"]["F12"],
            "cycle_closure": c["numerical"]["F10"],
            "reversibility": c["numerical"]["F09"]
        },
        "checks": {}
    }

    # Check 1: Perturbation tolerance (Voynich = 1.0)
    perturb = c["numerical"]["F11"]
    perturb_threshold = 0.8  # Require high tolerance
    perturb_pass = perturb >= perturb_threshold
    results["checks"]["perturbation_tolerance"] = {
        "pass": perturb_pass,
        "value": perturb,
        "reason": f"Perturbation tolerance {perturb:.2f} {'≥' if perturb_pass else '<'} threshold {perturb_threshold}"
    }

    # Check 2: Cycle closure (ability to return to start state)
    cycle = c["numerical"]["F10"]
    cycle_threshold = 0.9
    cycle_pass = cycle >= cycle_threshold
    results["checks"]["cycle_closure"] = {
        "pass": cycle_pass,
        "value": cycle,
        "reason": f"Cycle closure {cycle:.2f} {'≥' if cycle_pass else '<'} threshold {cycle_threshold}"
    }

    # Check 3: Reversibility (operations can be undone)
    rev = c["numerical"]["F09"]
    rev_threshold = 0.85
    rev_pass = rev >= rev_threshold
    results["checks"]["reversibility"] = {
        "pass": rev_pass,
        "value": rev,
        "reason": f"Reversibility {rev:.2f} {'≥' if rev_pass else '<'} threshold {rev_threshold}"
    }

    # Check 4: Combined robustness score
    combined = (perturb + cycle + rev) / 3
    voynich_combined = (v["numerical"]["F11"] + v["numerical"]["F10"] + v["numerical"]["F09"]) / 3
    combined_delta = abs(voynich_combined - combined)
    combined_threshold = 0.1
    combined_pass = combined_delta <= combined_threshold
    results["checks"]["combined_robustness"] = {
        "pass": combined_pass,
        "candidate_score": combined,
        "voynich_score": voynich_combined,
        "delta": combined_delta,
        "reason": f"Combined robustness delta {combined_delta:.3f} {'≤' if combined_pass else '>'} threshold {combined_threshold}"
    }

    # Overall verdict
    passed = sum(1 for c in results["checks"].values() if c["pass"])
    total = len(results["checks"])
    results["verdict"] = "PASS" if passed >= 3 else "MARGINAL" if passed >= 2 else "FAIL"
    results["score"] = passed / total

    return results


def run_all_tests():
    """Run all 6 tests against all 6 HIGH similarity candidates."""

    all_results = {}
    failure_matrix = {}

    for cid, candidate in HIGH_CANDIDATES.items():
        all_results[cid] = {
            "name": candidate["name"],
            "domain": candidate["domain"],
            "initial_similarity": candidate["similarity"],
            "tests": {}
        }
        failure_matrix[cid] = {
            "name": candidate["name"],
            "failures": []
        }

        # Run all 6 tests
        test_functions = [
            ("TEST_1", test_1_perturbation_response),
            ("TEST_2", test_2_hard_hazard_topology),
            ("TEST_3", test_3_non_intervention_role),
            ("TEST_4", test_4_mode_regime_multiplicity),
            ("TEST_5", test_5_operator_granularity),
            ("TEST_6", test_6_representation_invariance)
        ]

        for test_id, test_func in test_functions:
            result = test_func(cid, candidate)
            all_results[cid]["tests"][test_id] = result

            if result["verdict"] == "FAIL":
                failure_matrix[cid]["failures"].append({
                    "test": test_id,
                    "reason": result["test_name"],
                    "checks_failed": [k for k, v in result["checks"].items() if not v["pass"]]
                })

        # Calculate overall score
        scores = [t["score"] for t in all_results[cid]["tests"].values()]
        all_results[cid]["overall_score"] = sum(scores) / len(scores)

        verdicts = [t["verdict"] for t in all_results[cid]["tests"].values()]
        fail_count = verdicts.count("FAIL")
        pass_count = verdicts.count("PASS")

        if fail_count >= 2:
            all_results[cid]["overall_verdict"] = "ELIMINATED"
        elif fail_count == 1:
            all_results[cid]["overall_verdict"] = "WEAKENED"
        elif pass_count >= 5:
            all_results[cid]["overall_verdict"] = "SURVIVES"
        else:
            all_results[cid]["overall_verdict"] = "MARGINAL"

    return all_results, failure_matrix


def generate_reports(all_results, failure_matrix):
    """Generate the output reports."""

    # 1. Main stress test report
    report_lines = [
        "# Candidate Elimination Stress Test Report",
        "",
        "*Generated: 2026-01-01*",
        "*Status: Adversarial Comparison (Interpretive Firewall Active)*",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "| Candidate | Domain | Initial Similarity | Overall Score | Verdict |",
        "|-----------|--------|-------------------|---------------|---------|"
    ]

    for cid in sorted(all_results.keys(), key=lambda x: all_results[x]["initial_similarity"], reverse=True):
        r = all_results[cid]
        report_lines.append(
            f"| {r['name']} | {r['domain']} | {r['initial_similarity']:.3f} | {r['overall_score']:.3f} | **{r['overall_verdict']}** |"
        )

    report_lines.extend([
        "",
        "---",
        "",
        "## Test Results by Candidate",
        ""
    ])

    for cid in sorted(all_results.keys(), key=lambda x: all_results[x]["initial_similarity"], reverse=True):
        r = all_results[cid]
        report_lines.extend([
            f"### {r['name']} ({r['domain']})",
            f"- Initial similarity: {r['initial_similarity']:.3f}",
            f"- Overall score: {r['overall_score']:.3f}",
            f"- Verdict: **{r['overall_verdict']}**",
            "",
            "| Test | Score | Verdict | Key Issues |",
            "|------|-------|---------|------------|"
        ])

        for test_id, test_result in r["tests"].items():
            issues = [k for k, v in test_result["checks"].items() if not v["pass"]]
            issues_str = ", ".join(issues) if issues else "None"
            report_lines.append(
                f"| {test_id} | {test_result['score']:.2f} | {test_result['verdict']} | {issues_str} |"
            )

        report_lines.append("")

    # Detailed failure analysis
    report_lines.extend([
        "---",
        "",
        "## Detailed Failure Analysis",
        ""
    ])

    # Group by test for systematic analysis
    test_failures = {}
    for test_id in ["TEST_1", "TEST_2", "TEST_3", "TEST_4", "TEST_5", "TEST_6"]:
        test_failures[test_id] = []
        for cid, r in all_results.items():
            if r["tests"][test_id]["verdict"] == "FAIL":
                test_failures[test_id].append({
                    "candidate": r["name"],
                    "domain": r["domain"],
                    "checks": r["tests"][test_id]["checks"]
                })

    test_names = {
        "TEST_1": "Perturbation Response Shape",
        "TEST_2": "Hard Hazard Topology",
        "TEST_3": "Non-Intervention Role (LINK Analog)",
        "TEST_4": "Mode/Regime Multiplicity",
        "TEST_5": "Operator Granularity & Expertise",
        "TEST_6": "Representation Invariance"
    }

    for test_id, failures in test_failures.items():
        report_lines.append(f"### {test_id}: {test_names[test_id]}")
        report_lines.append("")
        if not failures:
            report_lines.append("*No candidates failed this test.*")
        else:
            report_lines.append(f"**{len(failures)} candidate(s) failed:**")
            for f in failures:
                report_lines.append(f"- **{f['candidate']}** ({f['domain']})")
                for check_name, check_result in f["checks"].items():
                    if not check_result["pass"]:
                        report_lines.append(f"  - {check_name}: {check_result['reason']}")
        report_lines.append("")

    # Survivors section
    report_lines.extend([
        "---",
        "",
        "## Survivors Analysis",
        ""
    ])

    survivors = [cid for cid, r in all_results.items() if r["overall_verdict"] == "SURVIVES"]
    eliminated = [cid for cid, r in all_results.items() if r["overall_verdict"] == "ELIMINATED"]
    weakened = [cid for cid, r in all_results.items() if r["overall_verdict"] == "WEAKENED"]
    marginal = [cid for cid, r in all_results.items() if r["overall_verdict"] == "MARGINAL"]

    report_lines.append(f"**Survivors:** {len(survivors)}")
    for cid in survivors:
        report_lines.append(f"- {all_results[cid]['name']} ({all_results[cid]['overall_score']:.3f})")

    report_lines.append("")
    report_lines.append(f"**Weakened (1 test failed):** {len(weakened)}")
    for cid in weakened:
        report_lines.append(f"- {all_results[cid]['name']} ({all_results[cid]['overall_score']:.3f})")

    report_lines.append("")
    report_lines.append(f"**Marginal:** {len(marginal)}")
    for cid in marginal:
        report_lines.append(f"- {all_results[cid]['name']} ({all_results[cid]['overall_score']:.3f})")

    report_lines.append("")
    report_lines.append(f"**Eliminated (≥2 tests failed):** {len(eliminated)}")
    for cid in eliminated:
        r = all_results[cid]
        failed_tests = [tid for tid, t in r["tests"].items() if t["verdict"] == "FAIL"]
        report_lines.append(f"- {r['name']}: Failed {', '.join(failed_tests)}")

    # Interpretive firewall
    report_lines.extend([
        "",
        "---",
        "",
        "## Interpretive Firewall Statement",
        "",
        "### What These Results Say",
        "",
        "1. **Elimination is structural**: Candidates fail because they diverge from the Voynich control profile on specific, measurable dimensions.",
        "2. **Survival is not identification**: Surviving candidates share operational homology with the Voynich signature. This does NOT mean the manuscript \"is\" or \"represents\" any specific process.",
        "3. **Biological systems face structural barriers**: The lack of an external human operator making deliberate control decisions is a fundamental architectural difference.",
        "",
        "### Permitted Interpretations",
        "",
        "- \"Candidate X fails to reproduce Voynich control behavior on [dimension]\"",
        "- \"Candidate X shares operational homology with the Voynich signature on [dimension]\"",
        "- \"The Voynich control profile is structurally compatible with process class [Y]\"",
        "",
        "### Forbidden Interpretations",
        "",
        "- ~~\"This proves the Voynich Manuscript is about [X]\"~~",
        "- ~~\"The author was working with [X]\"~~",
        "- ~~\"[X] is eliminated as a possibility\"~~ (Only high-similarity candidates were tested)",
        "",
        "---",
        "",
        "*Document closes the adversarial stress test phase.*"
    ])

    # Write main report
    with open("candidate_stress_test_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    # 2. Failure matrix JSON
    failure_output = {
        "metadata": {
            "generated": "2026-01-01",
            "candidates_tested": len(all_results),
            "tests_per_candidate": 6
        },
        "summary": {
            "survivors": len(survivors),
            "weakened": len(weakened),
            "marginal": len(marginal),
            "eliminated": len(eliminated)
        },
        "failure_matrix": failure_matrix,
        "test_failure_counts": {
            test_id: len(failures) for test_id, failures in test_failures.items()
        }
    }

    with open("candidate_failure_matrix.json", "w", encoding="utf-8") as f:
        json.dump(failure_output, f, indent=2)

    # 3. Remaining candidate summary
    summary_lines = [
        "# Remaining Candidate Summary",
        "",
        "*Generated: 2026-01-01*",
        "*Status: Post-Adversarial Stress Test*",
        "",
        "---",
        "",
        "## Candidates Surviving Stress Test",
        ""
    ]

    if survivors:
        for cid in survivors:
            r = all_results[cid]
            summary_lines.extend([
                f"### {r['name']}",
                f"- Domain: {r['domain']}",
                f"- Initial similarity: {r['initial_similarity']:.3f}",
                f"- Stress test score: {r['overall_score']:.3f}",
                f"- All 6 tests: PASS or MARGINAL",
                ""
            ])
    else:
        summary_lines.append("*No candidates achieved SURVIVES status.*")
        summary_lines.append("")

    summary_lines.extend([
        "## Weakened Candidates (1 Test Failed)",
        ""
    ])

    if weakened:
        for cid in weakened:
            r = all_results[cid]
            failed = [tid for tid, t in r["tests"].items() if t["verdict"] == "FAIL"]
            summary_lines.extend([
                f"### {r['name']}",
                f"- Domain: {r['domain']}",
                f"- Initial similarity: {r['initial_similarity']:.3f}",
                f"- Failed test(s): {', '.join(failed)}",
                ""
            ])
    else:
        summary_lines.append("*No candidates in this category.*")
        summary_lines.append("")

    summary_lines.extend([
        "## Eliminated Candidates (≥2 Tests Failed)",
        ""
    ])

    if eliminated:
        for cid in eliminated:
            r = all_results[cid]
            failed = [tid for tid, t in r["tests"].items() if t["verdict"] == "FAIL"]
            summary_lines.extend([
                f"### {r['name']}",
                f"- Domain: {r['domain']}",
                f"- Initial similarity: {r['initial_similarity']:.3f}",
                f"- Failed tests: {', '.join(failed)}",
                f"- **Elimination rationale**: Structural mismatch on {len(failed)} control dimensions",
                ""
            ])
    else:
        summary_lines.append("*No candidates eliminated.*")
        summary_lines.append("")

    summary_lines.extend([
        "---",
        "",
        "## Uncertainty Statement",
        "",
        "The following sources of uncertainty remain:",
        "",
        "1. **Library incompleteness**: Only 6 HIGH-similarity candidates were stress-tested. Unlisted processes may also share operational homology.",
        "",
        "2. **Feature abstraction**: Control features are abstractions. Different physical processes can have identical control profiles.",
        "",
        "3. **Historical unknowns**: Surviving candidates are structurally compatible. Historical plausibility was NOT assessed.",
        "",
        "4. **Interpretation barrier**: Even surviving candidates cannot be identified AS the Voynich content. Operational homology ≠ identity.",
        "",
        "---",
        "",
        "## Final Statement",
        "",
        "This stress test **eliminates** candidates that structurally diverge from the Voynich control signature.",
        "",
        "It does **NOT**:",
        "- Identify what the manuscript is",
        "- Prove any historical claim",
        "- Translate any content",
        "",
        "**Ambiguity is itself a result.** If multiple candidates survive, that reflects the resolution limit of this methodology.",
        "",
        "---",
        "",
        "*Document closes the remaining candidate summary phase.*"
    ])

    with open("remaining_candidate_summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))

    return len(survivors), len(weakened), len(marginal), len(eliminated)


def main():
    print("=" * 60)
    print("CANDIDATE ELIMINATION STRESS TEST")
    print("Head-to-Head Adversarial Comparison")
    print("=" * 60)
    print()

    print("Running 6 tests against 6 HIGH-similarity candidates...")
    print()

    all_results, failure_matrix = run_all_tests()

    print("Test Results:")
    print("-" * 60)

    for cid in sorted(all_results.keys(), key=lambda x: all_results[x]["initial_similarity"], reverse=True):
        r = all_results[cid]
        print(f"\n{r['name']} ({r['domain']})")
        print(f"  Initial similarity: {r['initial_similarity']:.3f}")
        print(f"  Overall score: {r['overall_score']:.3f}")
        print(f"  Verdict: {r['overall_verdict']}")

        for test_id, test_result in r["tests"].items():
            status = "[PASS]" if test_result["verdict"] == "PASS" else "[MARG]" if test_result["verdict"] == "MARGINAL" else "[FAIL]"
            print(f"    {status} {test_id}: {test_result['verdict']} ({test_result['score']:.2f})")

    print()
    print("-" * 60)
    print("Generating reports...")

    survivors, weakened, marginal, eliminated = generate_reports(all_results, failure_matrix)

    print()
    print("SUMMARY:")
    print(f"  Survivors: {survivors}")
    print(f"  Weakened:  {weakened}")
    print(f"  Marginal:  {marginal}")
    print(f"  Eliminated: {eliminated}")
    print()
    print("Output files:")
    print("  - candidate_stress_test_report.md")
    print("  - candidate_failure_matrix.json")
    print("  - remaining_candidate_summary.md")
    print()
    print("=" * 60)
    print("STRESS TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
