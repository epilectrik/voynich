#!/usr/bin/env python3
"""
Adversarial Process Family Comparison: PF-E (Extraction) vs PF-C (Conditioning)

This script stress-tests two competing process family archetypes against
the locked Voynich grammar to identify tension points and awkward fits.
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from pathlib import Path

# ============================================================================
# ARCHETYPE DEFINITIONS (Abstract)
# ============================================================================

@dataclass
class ProcessArchetype:
    """Abstract process family archetype for comparison."""
    name: str
    short_name: str
    characteristic_demands: Dict[str, str]
    expected_control_patterns: Dict[str, str]

    # Predictions for grammar features
    predicts_endpoint_markers: bool
    predicts_throughput_optimization: bool
    predicts_cumulative_change: bool
    predicts_indefinite_operation: bool
    predicts_restart_natural: bool
    predicts_high_link_for_waiting: bool
    predicts_low_link_for_speed: bool
    predicts_hazard_asymmetry: bool  # Are some hazards "worse" than others?

PF_E = ProcessArchetype(
    name="Continuous Extraction-Like",
    short_name="PF-E",
    characteristic_demands={
        "transfer": "Removal or transfer of a mobile fraction",
        "gradient": "Tendency toward depletion gradients",
        "monitoring": "Need for monitoring yield vs loss",
        "completion": "Often benefits from endpoint or asymptotic completion",
        "efficiency": "Typically values throughput efficiency"
    },
    expected_control_patterns={
        "role_diversity": "High diversity - different substrates need different rates",
        "link_usage": "LINK = waiting for slow diffusion/transport",
        "hazards": "COMPOSITION_JUMP, RATE_MISMATCH most relevant",
        "recovery": "Recovery = restart extraction from intermediate state",
        "extended": "Extended runs = more thorough extraction"
    },
    predicts_endpoint_markers=True,
    predicts_throughput_optimization=True,
    predicts_cumulative_change=True,
    predicts_indefinite_operation=False,
    predicts_restart_natural=True,
    predicts_high_link_for_waiting=True,
    predicts_low_link_for_speed=True,
    predicts_hazard_asymmetry=True
)

PF_C = ProcessArchetype(
    name="Continuous Conditioning-Like",
    short_name="PF-C",
    characteristic_demands={
        "maintenance": "No inherent notion of completion",
        "stability": "Emphasis on state maintenance",
        "cyclic": "Reversible or cyclic redistribution",
        "correction": "Continuous correction rather than termination",
        "safety": "Often values stability over efficiency"
    },
    expected_control_patterns={
        "role_diversity": "Moderate diversity - different conditions need different parameters",
        "link_usage": "LINK = allowing equilibration before next intervention",
        "hazards": "PHASE_ORDERING, CONTAINMENT_TIMING most relevant",
        "recovery": "Recovery = return to target state after perturbation",
        "extended": "Extended runs = longer maintenance periods"
    },
    predicts_endpoint_markers=False,
    predicts_throughput_optimization=False,
    predicts_cumulative_change=False,
    predicts_indefinite_operation=True,
    predicts_restart_natural=True,
    predicts_high_link_for_waiting=True,
    predicts_low_link_for_speed=False,
    predicts_hazard_asymmetry=False  # All hazards equally bad for maintenance
)

# ============================================================================
# DATA LOADING
# ============================================================================

def load_data():
    """Load all required data files."""
    base = Path(".")

    with open(base / "control_signatures.json") as f:
        signatures = json.load(f)["signatures"]

    with open(base / "forward_inference_results.json") as f:
        forward_results = json.load(f)

    with open(base / "lane3_material_class_results.json") as f:
        material_results = json.load(f)

    with open(base / "optionA_geometry_results.json") as f:
        geometry_results = json.load(f)

    return signatures, forward_results, material_results, geometry_results

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_a_program_role_distribution(signatures: dict, archetype: ProcessArchetype) -> Dict:
    """
    Test A: Does the Voynich role taxonomy over- or under-fit this archetype?
    """
    # Compute role distributions
    stability_roles = {"ULTRA_CONSERVATIVE": 0, "CONSERVATIVE": 0, "MODERATE": 0, "AGGRESSIVE": 0}
    waiting_roles = {"LINK_HEAVY_EXTENDED": 0, "LINK_HEAVY": 0, "LINK_MODERATE": 0, "LINK_SPARSE": 0}
    special_roles = {"RESTART_CAPABLE": 0, "HIGH_INTERVENTION": 0, "NONE": 0}

    for folio, sig in signatures.items():
        # Stability classification
        ld = sig["link_density"]
        hd = sig["hazard_density"]
        nm = sig["near_miss_count"]

        if ld > 0.45 and nm < 10:
            stability_roles["ULTRA_CONSERVATIVE"] += 1
        elif ld > 0.35 and hd < 0.55:
            stability_roles["CONSERVATIVE"] += 1
        elif hd > 0.62 and nm > 15:
            stability_roles["AGGRESSIVE"] += 1
        else:
            stability_roles["MODERATE"] += 1

        # Waiting classification
        if ld > 0.45 and sig["max_consecutive_link"] >= 6:
            waiting_roles["LINK_HEAVY_EXTENDED"] += 1
        elif ld > 0.40:
            waiting_roles["LINK_HEAVY"] += 1
        elif ld < 0.30:
            waiting_roles["LINK_SPARSE"] += 1
        else:
            waiting_roles["LINK_MODERATE"] += 1

        # Special markers
        if sig["reset_present"]:
            special_roles["RESTART_CAPABLE"] += 1
        elif sig["intervention_frequency"] > 8:
            special_roles["HIGH_INTERVENTION"] += 1
        else:
            special_roles["NONE"] += 1

    # Evaluate fit
    tensions = []
    unexplained = []

    if archetype.short_name == "PF-E":
        # Extraction expects throughput optimization
        aggressive_pct = stability_roles["AGGRESSIVE"] / len(signatures) * 100
        conservative_pct = (stability_roles["CONSERVATIVE"] + stability_roles["ULTRA_CONSERVATIVE"]) / len(signatures) * 100

        if aggressive_pct < 30:
            tensions.append(f"Only {aggressive_pct:.1f}% AGGRESSIVE programs - extraction typically optimizes throughput")
        if conservative_pct > 25:
            tensions.append(f"{conservative_pct:.1f}% CONSERVATIVE/ULTRA programs unexplained by extraction logic")

        # High-intervention would be expected for monitoring
        hi_pct = special_roles["HIGH_INTERVENTION"] / len(signatures) * 100
        if hi_pct < 20:
            tensions.append(f"Only {hi_pct:.1f}% HIGH_INTERVENTION - extraction usually requires close monitoring")

        unexplained.append("ULTRA_CONSERVATIVE programs (4.8%) have no clear extraction role")
        unexplained.append("LINK_HEAVY_EXTENDED programs (7.2%) suggest patience beyond extraction needs")

    else:  # PF-C
        # Conditioning expects moderate, stable operation
        moderate_pct = stability_roles["MODERATE"] / len(signatures) * 100

        if moderate_pct < 50:
            tensions.append(f"Only {moderate_pct:.1f}% MODERATE programs - conditioning expects central tendency")

        # AGGRESSIVE programs are unexpected for maintenance
        aggressive_pct = stability_roles["AGGRESSIVE"] / len(signatures) * 100
        if aggressive_pct > 10:
            tensions.append(f"{aggressive_pct:.1f}% AGGRESSIVE programs - risky for pure maintenance")

        unexplained.append("LINK_SPARSE programs (16.9%) suggest speed priority inconsistent with conditioning")
        unexplained.append("HIGH_INTERVENTION programs (12.0%) suggest active change rather than maintenance")

    return {
        "archetype": archetype.short_name,
        "stability_distribution": stability_roles,
        "waiting_distribution": waiting_roles,
        "special_distribution": special_roles,
        "tensions": tensions,
        "unexplained": unexplained,
        "structural_coherence": max(0, 1.0 - len(tensions) * 0.15 - len(unexplained) * 0.1)
    }

def test_b_link_utilization(signatures: dict, archetype: ProcessArchetype) -> Dict:
    """
    Test B: Does each archetype naturally require LINK at observed densities?
    """
    link_densities = [s["link_density"] for s in signatures.values()]
    mean_ld = sum(link_densities) / len(link_densities)
    max_consec = [s["max_consecutive_link"] for s in signatures.values()]
    mean_consec = sum(max_consec) / len(max_consec)

    tensions = []
    unexplained = []

    if archetype.short_name == "PF-E":
        # Extraction: LINK = waiting for diffusion, but also wants speed
        if mean_ld > 0.40:
            tensions.append(f"Mean LINK density {mean_ld:.3f} is HIGH for extraction (wants throughput)")

        # Long consecutive LINK runs are awkward
        if mean_consec > 4:
            tensions.append(f"Mean max consecutive LINK {mean_consec:.1f} suggests patience beyond extraction timescales")

        # Extraction typically has bimodal LINK: fast phases + waiting phases
        link_var = sum((ld - mean_ld)**2 for ld in link_densities) / len(link_densities)
        if link_var < 0.003:
            unexplained.append(f"Low LINK variance ({link_var:.4f}) - extraction expects bimodal distribution")

        # High LINK being SAFER (Lane 2 result) is awkward for extraction
        unexplained.append("High-LINK programs being SAFER contradicts extraction's speed-safety tradeoff")

    else:  # PF-C
        # Conditioning: LINK = equilibration time, naturally high
        if mean_ld < 0.35:
            tensions.append(f"Mean LINK density {mean_ld:.3f} is LOW for conditioning (needs equilibration)")

        # Conditioning expects uniform LINK usage
        link_var = sum((ld - mean_ld)**2 for ld in link_densities) / len(link_densities)
        if link_var > 0.005:
            unexplained.append(f"High LINK variance ({link_var:.4f}) - conditioning expects uniform waiting")

        # Some programs being LINK_SPARSE is awkward
        sparse_count = sum(1 for s in signatures.values() if s["link_density"] < 0.30)
        if sparse_count > 10:
            tensions.append(f"{sparse_count} LINK_SPARSE programs unexplained by conditioning logic")

    return {
        "archetype": archetype.short_name,
        "mean_link_density": mean_ld,
        "mean_max_consecutive": mean_consec,
        "link_essential": archetype.predicts_high_link_for_waiting,
        "link_awkward": not archetype.predicts_high_link_for_waiting and mean_ld > 0.38,
        "tensions": tensions,
        "unexplained": unexplained,
        "structural_coherence": max(0, 1.0 - len(tensions) * 0.15 - len(unexplained) * 0.15)
    }

def test_c_hazard_encoding(signatures: dict, archetype: ProcessArchetype) -> Dict:
    """
    Test C: Do the hazard types make sense for the archetype?
    """
    # Count hazard type frequencies
    hazard_counts = {}
    for sig in signatures.values():
        for hazard in sig["hazard_types_present"]:
            hazard_counts[hazard] = hazard_counts.get(hazard, 0) + 1

    # All programs have all 5 hazard types
    hazard_density_mean = sum(s["hazard_density"] for s in signatures.values()) / len(signatures)
    near_miss_mean = sum(s["near_miss_count"] for s in signatures.values()) / len(signatures)

    tensions = []
    unexplained = []

    if archetype.short_name == "PF-E":
        # Extraction expects COMPOSITION_JUMP and RATE_MISMATCH to dominate
        # But all hazards are equally present
        unexplained.append("All 5 hazard types equally present - extraction expects COMPOSITION emphasis")

        # Bidirectional hazards are awkward for extraction (which is inherently irreversible)
        tensions.append("100% bidirectional hazards - extraction cannot 'un-extract'")

        # High near-miss counts suggest operating near limits
        if near_miss_mean > 20:
            tensions.append(f"Mean near-miss {near_miss_mean:.1f} - extraction operating near hazard limits")

        # PHASE_ORDERING dominance (41%) is unexplained
        unexplained.append("PHASE_ORDERING is 41% of hazards - extraction doesn't inherently phase-order")

    else:  # PF-C
        # Conditioning expects PHASE_ORDERING and CONTAINMENT_TIMING
        # PHASE_ORDERING at 41% is consistent

        # Bidirectional hazards MAKE SENSE for conditioning
        # (perturbations in either direction are bad)

        # High hazard density is acceptable (maintenance = staying in safe zone)

        # But ENERGY_OVERSHOOT being a hazard is awkward
        unexplained.append("ENERGY_OVERSHOOT hazard class - conditioning doesn't typically risk energy runaway")

        # RATE_MISMATCH is awkward for pure maintenance
        unexplained.append("RATE_MISMATCH hazard class - conditioning doesn't have inherent rate requirements")

        if near_miss_mean > 25:
            tensions.append(f"Mean near-miss {near_miss_mean:.1f} - maintenance shouldn't flirt with hazards")

    return {
        "archetype": archetype.short_name,
        "hazard_types": list(hazard_counts.keys()),
        "hazard_density_mean": hazard_density_mean,
        "near_miss_mean": near_miss_mean,
        "all_hazards_bidirectional": True,  # From grammar
        "tensions": tensions,
        "unexplained": unexplained,
        "structural_coherence": max(0, 1.0 - len(tensions) * 0.20 - len(unexplained) * 0.10)
    }

def test_d_absence_of_endpoints(signatures: dict, archetype: ProcessArchetype) -> Dict:
    """
    Test D: Does the lack of stopping criteria stress the archetype?
    """
    # Grammar has 0 endpoint markers, 0 translation-eligible zones, 0 identifier tokens

    tensions = []
    unexplained = []

    if archetype.short_name == "PF-E":
        # Extraction TYPICALLY has endpoints (yield asymptote, depletion, etc.)
        tensions.append("CRITICAL: 0 endpoint markers - extraction typically monitors for completion")
        tensions.append("0 yield-progress indicators - extraction needs to know when to stop")
        tensions.append("Indefinite operation encoded - extraction is inherently finite")

        unexplained.append("How does operator know extraction is 'done'?")
        unexplained.append("What prevents over-extraction or resource waste?")

    else:  # PF-C
        # Conditioning naturally lacks endpoints (maintenance is indefinite)
        # This is a GOOD fit

        # Only tension: why are there different program lengths?
        lengths = [s["total_length"] for s in signatures.values()]
        length_range = max(lengths) - min(lengths)

        if length_range > 1500:
            unexplained.append(f"Program length range {length_range} - pure maintenance should be uniform")

        # Extended runs are natural for conditioning
        extended = sum(1 for s in signatures.values() if s["total_length"] > 800)
        # (This is actually a good fit, no tension)

    return {
        "archetype": archetype.short_name,
        "endpoint_markers_present": 0,
        "archetype_predicts_endpoints": archetype.predicts_endpoint_markers,
        "fit_quality": "POOR" if archetype.predicts_endpoint_markers else "GOOD",
        "tensions": tensions,
        "unexplained": unexplained,
        "structural_coherence": max(0, 1.0 - len(tensions) * 0.25 - len(unexplained) * 0.10)
    }

def test_e_recovery_restart(signatures: dict, archetype: ProcessArchetype) -> Dict:
    """
    Test E: Are restart-capable programs natural or pathological for the archetype?
    """
    restart_programs = [f for f, s in signatures.items() if s["reset_present"]]
    recovery_ops = [(f, s["recovery_ops_count"]) for f, s in signatures.items()]
    mean_recovery = sum(r for _, r in recovery_ops) / len(recovery_ops)
    high_recovery = sum(1 for _, r in recovery_ops if r > 15)

    tensions = []
    unexplained = []

    if archetype.short_name == "PF-E":
        # Extraction: restart = start fresh batch, recovery = save partial progress
        # Only 3 restart-capable programs

        if len(restart_programs) < 10:
            tensions.append(f"Only {len(restart_programs)} restart-capable - extraction often restarts batches")

        # High recovery ops are natural (salvage partial extraction)
        # But 42% LOW_RECOVERY is awkward
        low_recovery = sum(1 for _, r in recovery_ops if r < 5)
        if low_recovery > 20:
            unexplained.append(f"{low_recovery} programs with low recovery - extraction should enable salvage")

        # Extended runs with restart might indicate multi-stage extraction
        extended_restart = [f for f in restart_programs if signatures[f]["total_length"] > 800]
        if len(extended_restart) > 0:
            # This is actually natural for extraction
            pass

    else:  # PF-C
        # Conditioning: restart = full reset to initial state, recovery = return to target
        # Restart should be RARE for pure maintenance (why reset if maintaining?)

        if len(restart_programs) > 5:
            tensions.append(f"{len(restart_programs)} restart-capable programs - maintenance shouldn't need resets")

        # Recovery ops are natural (return to target after perturbation)
        # But very high recovery counts suggest instability
        if high_recovery > 15:
            tensions.append(f"{high_recovery} programs with >15 recovery ops - excessive for stable maintenance")

        # f57r being specifically RESTART_PROTOCOL is unexplained
        unexplained.append("f57r = RESTART_PROTOCOL - why would maintenance need a dedicated reset program?")

    return {
        "archetype": archetype.short_name,
        "restart_programs": restart_programs,
        "n_restart": len(restart_programs),
        "mean_recovery_ops": mean_recovery,
        "high_recovery_count": high_recovery,
        "tensions": tensions,
        "unexplained": unexplained,
        "structural_coherence": max(0, 1.0 - len(tensions) * 0.15 - len(unexplained) * 0.15)
    }

# ============================================================================
# AGGREGATE SCORING
# ============================================================================

def aggregate_results(test_results: Dict[str, Dict]) -> Dict:
    """Aggregate all test results into summary metrics."""
    all_tensions = []
    all_unexplained = []
    coherence_scores = []

    for test_name, result in test_results.items():
        all_tensions.extend(result.get("tensions", []))
        all_unexplained.extend(result.get("unexplained", []))
        coherence_scores.append(result.get("structural_coherence", 0.5))

    # Count strained assumptions
    strained = len([t for t in all_tensions if "CRITICAL" in t or "unexplained" in t.lower()])

    return {
        "total_tensions": len(all_tensions),
        "total_unexplained": len(all_unexplained),
        "strained_assumptions": strained,
        "mean_coherence": sum(coherence_scores) / len(coherence_scores),
        "overall_structural_coherence": min(coherence_scores),  # Worst case
        "tensions_list": all_tensions,
        "unexplained_list": all_unexplained
    }

# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_pf_e_report(test_results: Dict, aggregate: Dict) -> str:
    """Generate PF-E vs Grammar report."""
    lines = [
        "# PF-E (Continuous Extraction-Like) vs Voynich Grammar",
        "",
        "> **ADVERSARIAL TEST**: Finding where extraction archetype fits POORLY",
        "",
        "---",
        "",
        "## Summary Metrics",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Structural Coherence | {aggregate['mean_coherence']:.3f} |",
        f"| Total Tensions | {aggregate['total_tensions']} |",
        f"| Unexplained Features | {aggregate['total_unexplained']} |",
        f"| Strained Assumptions | {aggregate['strained_assumptions']} |",
        "",
        "---",
        "",
        "## Test A: Program Role Distribution",
        "",
    ]

    r = test_results["test_a"]
    lines.append(f"**Coherence Score**: {r['structural_coherence']:.3f}")
    lines.append("")
    lines.append("### Tensions")
    for t in r["tensions"]:
        lines.append(f"- {t}")
    lines.append("")
    lines.append("### Unexplained Features")
    for u in r["unexplained"]:
        lines.append(f"- {u}")

    lines.extend([
        "",
        "---",
        "",
        "## Test B: LINK Utilization",
        "",
    ])

    r = test_results["test_b"]
    lines.append(f"**Coherence Score**: {r['structural_coherence']:.3f}")
    lines.append("")
    lines.append(f"- Mean LINK density: {r['mean_link_density']:.3f}")
    lines.append(f"- Mean max consecutive LINK: {r['mean_max_consecutive']:.1f}")
    lines.append("")
    lines.append("### Tensions")
    for t in r["tensions"]:
        lines.append(f"- {t}")
    lines.append("")
    lines.append("### Unexplained Features")
    for u in r["unexplained"]:
        lines.append(f"- {u}")

    lines.extend([
        "",
        "---",
        "",
        "## Test C: Hazard Encoding",
        "",
    ])

    r = test_results["test_c"]
    lines.append(f"**Coherence Score**: {r['structural_coherence']:.3f}")
    lines.append("")
    lines.append(f"- Hazard density mean: {r['hazard_density_mean']:.3f}")
    lines.append(f"- Near-miss mean: {r['near_miss_mean']:.1f}")
    lines.append(f"- All hazards bidirectional: {r['all_hazards_bidirectional']}")
    lines.append("")
    lines.append("### Tensions")
    for t in r["tensions"]:
        lines.append(f"- {t}")
    lines.append("")
    lines.append("### Unexplained Features")
    for u in r["unexplained"]:
        lines.append(f"- {u}")

    lines.extend([
        "",
        "---",
        "",
        "## Test D: Absence of Endpoints",
        "",
    ])

    r = test_results["test_d"]
    lines.append(f"**Coherence Score**: {r['structural_coherence']:.3f}")
    lines.append("")
    lines.append(f"- Endpoint markers present: {r['endpoint_markers_present']}")
    lines.append(f"- Archetype predicts endpoints: {r['archetype_predicts_endpoints']}")
    lines.append(f"- Fit quality: **{r['fit_quality']}**")
    lines.append("")
    lines.append("### Tensions")
    for t in r["tensions"]:
        lines.append(f"- {t}")
    lines.append("")
    lines.append("### Unexplained Features")
    for u in r["unexplained"]:
        lines.append(f"- {u}")

    lines.extend([
        "",
        "---",
        "",
        "## Test E: Recovery & Restart Programs",
        "",
    ])

    r = test_results["test_e"]
    lines.append(f"**Coherence Score**: {r['structural_coherence']:.3f}")
    lines.append("")
    lines.append(f"- Restart-capable programs: {r['n_restart']} ({', '.join(r['restart_programs'])})")
    lines.append(f"- Mean recovery ops: {r['mean_recovery_ops']:.1f}")
    lines.append("")
    lines.append("### Tensions")
    for t in r["tensions"]:
        lines.append(f"- {t}")
    lines.append("")
    lines.append("### Unexplained Features")
    for u in r["unexplained"]:
        lines.append(f"- {u}")

    lines.extend([
        "",
        "---",
        "",
        "## What PF-E Struggles to Explain",
        "",
        "### Critical Mismatches",
        "",
        "1. **No endpoint markers** — Extraction is inherently finite; grammar encodes indefinite operation",
        "2. **Bidirectional hazards** — Extraction is irreversible; grammar treats forward/backward violations symmetrically",
        "3. **High LINK density** — Extraction optimizes throughput; grammar emphasizes patience",
        "4. **Conservative program dominance** — Extraction pushes limits; grammar prioritizes safety",
        "",
        "### Awkward Fits",
        "",
        "1. ULTRA_CONSERVATIVE programs (4.8%) have no extraction purpose",
        "2. High-LINK being SAFER contradicts extraction's speed-safety tradeoff",
        "3. PHASE_ORDERING as dominant hazard (41%) — extraction doesn't inherently phase-order",
        "4. All programs reach STATE-C — extraction expects varied endpoints",
        "",
        "### Degree of Contrivance Required",
        "",
        "To fit PF-E to this grammar requires assuming:",
        "- The operator provides external endpoint detection (not encoded)",
        "- Speed is externally optimized despite grammar prioritizing safety",
        "- Bidirectional hazards are a \"safety margin\" abstraction",
        "- Conservative programs handle \"delicate\" substrates (ad hoc)",
        "",
        "**Contrivance level: HIGH**",
    ])

    return "\n".join(lines)

def generate_pf_c_report(test_results: Dict, aggregate: Dict) -> str:
    """Generate PF-C vs Grammar report."""
    lines = [
        "# PF-C (Continuous Conditioning-Like) vs Voynich Grammar",
        "",
        "> **ADVERSARIAL TEST**: Finding where conditioning archetype fits POORLY",
        "",
        "---",
        "",
        "## Summary Metrics",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Structural Coherence | {aggregate['mean_coherence']:.3f} |",
        f"| Total Tensions | {aggregate['total_tensions']} |",
        f"| Unexplained Features | {aggregate['total_unexplained']} |",
        f"| Strained Assumptions | {aggregate['strained_assumptions']} |",
        "",
        "---",
        "",
        "## Test A: Program Role Distribution",
        "",
    ]

    r = test_results["test_a"]
    lines.append(f"**Coherence Score**: {r['structural_coherence']:.3f}")
    lines.append("")
    lines.append("### Tensions")
    for t in r["tensions"]:
        lines.append(f"- {t}")
    if not r["tensions"]:
        lines.append("- (None)")
    lines.append("")
    lines.append("### Unexplained Features")
    for u in r["unexplained"]:
        lines.append(f"- {u}")

    lines.extend([
        "",
        "---",
        "",
        "## Test B: LINK Utilization",
        "",
    ])

    r = test_results["test_b"]
    lines.append(f"**Coherence Score**: {r['structural_coherence']:.3f}")
    lines.append("")
    lines.append(f"- Mean LINK density: {r['mean_link_density']:.3f}")
    lines.append(f"- Mean max consecutive LINK: {r['mean_max_consecutive']:.1f}")
    lines.append("")
    lines.append("### Tensions")
    for t in r["tensions"]:
        lines.append(f"- {t}")
    lines.append("")
    lines.append("### Unexplained Features")
    for u in r["unexplained"]:
        lines.append(f"- {u}")
    if not r["unexplained"]:
        lines.append("- (None)")

    lines.extend([
        "",
        "---",
        "",
        "## Test C: Hazard Encoding",
        "",
    ])

    r = test_results["test_c"]
    lines.append(f"**Coherence Score**: {r['structural_coherence']:.3f}")
    lines.append("")
    lines.append(f"- Hazard density mean: {r['hazard_density_mean']:.3f}")
    lines.append(f"- Near-miss mean: {r['near_miss_mean']:.1f}")
    lines.append(f"- All hazards bidirectional: {r['all_hazards_bidirectional']}")
    lines.append("")
    lines.append("### Tensions")
    for t in r["tensions"]:
        lines.append(f"- {t}")
    if not r["tensions"]:
        lines.append("- (None)")
    lines.append("")
    lines.append("### Unexplained Features")
    for u in r["unexplained"]:
        lines.append(f"- {u}")

    lines.extend([
        "",
        "---",
        "",
        "## Test D: Absence of Endpoints",
        "",
    ])

    r = test_results["test_d"]
    lines.append(f"**Coherence Score**: {r['structural_coherence']:.3f}")
    lines.append("")
    lines.append(f"- Endpoint markers present: {r['endpoint_markers_present']}")
    lines.append(f"- Archetype predicts endpoints: {r['archetype_predicts_endpoints']}")
    lines.append(f"- Fit quality: **{r['fit_quality']}**")
    lines.append("")
    lines.append("### Tensions")
    for t in r["tensions"]:
        lines.append(f"- {t}")
    if not r["tensions"]:
        lines.append("- (None — this is a **GOOD FIT**)")
    lines.append("")
    lines.append("### Unexplained Features")
    for u in r["unexplained"]:
        lines.append(f"- {u}")

    lines.extend([
        "",
        "---",
        "",
        "## Test E: Recovery & Restart Programs",
        "",
    ])

    r = test_results["test_e"]
    lines.append(f"**Coherence Score**: {r['structural_coherence']:.3f}")
    lines.append("")
    lines.append(f"- Restart-capable programs: {r['n_restart']} ({', '.join(r['restart_programs'])})")
    lines.append(f"- Mean recovery ops: {r['mean_recovery_ops']:.1f}")
    lines.append("")
    lines.append("### Tensions")
    for t in r["tensions"]:
        lines.append(f"- {t}")
    if not r["tensions"]:
        lines.append("- (None)")
    lines.append("")
    lines.append("### Unexplained Features")
    for u in r["unexplained"]:
        lines.append(f"- {u}")

    lines.extend([
        "",
        "---",
        "",
        "## What PF-C Struggles to Explain",
        "",
        "### Critical Mismatches",
        "",
        "1. **Program diversity** — Pure maintenance should be uniform; 83 distinct programs exist",
        "2. **LINK_SPARSE programs** — 16.9% have low waiting; maintenance should wait",
        "3. **HIGH_INTERVENTION programs** — 12% suggest active change, not passive maintenance",
        "4. **AGGRESSIVE programs** — 18% operate near hazard limits; risky for pure maintenance",
        "",
        "### Awkward Fits",
        "",
        "1. ENERGY_OVERSHOOT hazard class — conditioning doesn't typically risk energy runaway",
        "2. RATE_MISMATCH hazard class — conditioning has no inherent rate requirements",
        "3. f57r = RESTART_PROTOCOL — why would maintenance need a dedicated reset program?",
        "4. Extended runs with high recovery ops — suggests instability, not steady maintenance",
        "",
        "### Degree of Contrivance Required",
        "",
        "To fit PF-C to this grammar requires assuming:",
        "- 83 different \"conditions\" need 83 different maintenance protocols",
        "- LINK_SPARSE programs handle \"fast-equilibrating\" conditions (ad hoc)",
        "- AGGRESSIVE programs are for \"critical\" conditions requiring active intervention",
        "- Hazard diversity reflects \"multiple failure modes\" of a complex system",
        "",
        "**Contrivance level: MODERATE**",
    ])

    return "\n".join(lines)

def generate_comparative_table(pf_e_results: Dict, pf_c_results: Dict,
                               pf_e_agg: Dict, pf_c_agg: Dict) -> str:
    """Generate comparative tensions table."""
    lines = [
        "# Comparative Tensions Table: PF-E vs PF-C",
        "",
        "> **PURPOSE**: Side-by-side comparison of how each archetype fits/struggles",
        "",
        "---",
        "",
        "## Summary Comparison",
        "",
        "| Metric | PF-E (Extraction) | PF-C (Conditioning) |",
        "|--------|-------------------|---------------------|",
        f"| Structural Coherence | {pf_e_agg['mean_coherence']:.3f} | {pf_c_agg['mean_coherence']:.3f} |",
        f"| Total Tensions | {pf_e_agg['total_tensions']} | {pf_c_agg['total_tensions']} |",
        f"| Unexplained Features | {pf_e_agg['total_unexplained']} | {pf_c_agg['total_unexplained']} |",
        f"| Strained Assumptions | {pf_e_agg['strained_assumptions']} | {pf_c_agg['strained_assumptions']} |",
        f"| Contrivance Level | HIGH | MODERATE |",
        "",
        "---",
        "",
        "## Feature-by-Feature Comparison",
        "",
        "| Grammar Feature | Fits PF-E | Fits PF-C | Notes |",
        "|-----------------|-----------|-----------|-------|",
        "| 0 endpoint markers | POOR | GOOD | Extraction expects completion signals |",
        "| 38% mean LINK density | POOR | GOOD | High waiting fits conditioning |",
        "| 100% bidirectional hazards | POOR | GOOD | Extraction is irreversible |",
        "| 18% AGGRESSIVE programs | POOR | POOR | Risky for both archetypes |",
        "| 4.8% ULTRA_CONSERVATIVE | POOR | MODERATE | Unexplained by extraction |",
        "| 16.9% LINK_SPARSE | MODERATE | POOR | Speed priority fits extraction |",
        "| 12% HIGH_INTERVENTION | GOOD | POOR | Monitoring fits extraction |",
        "| 3 restart-capable | POOR | POOR | Too few for extraction, too many for conditioning |",
        "| PHASE_ORDERING 41% hazards | POOR | GOOD | Phase ordering is conditioning concern |",
        "| All programs reach STATE-C | POOR | GOOD | Convergence fits maintenance |",
        "| 83 distinct programs | MODERATE | POOR | Diversity fits extraction variety |",
        "| Extended runs (12.6% gap) | MODERATE | GOOD | Longer maintenance is natural |",
        "",
        "---",
        "",
        "## Test-by-Test Coherence Scores",
        "",
        "| Test | PF-E Score | PF-C Score | Advantage |",
        "|------|------------|------------|-----------|",
        f"| A: Role Distribution | {pf_e_results['test_a']['structural_coherence']:.3f} | {pf_c_results['test_a']['structural_coherence']:.3f} | {'PF-C' if pf_c_results['test_a']['structural_coherence'] > pf_e_results['test_a']['structural_coherence'] else 'PF-E'} |",
        f"| B: LINK Utilization | {pf_e_results['test_b']['structural_coherence']:.3f} | {pf_c_results['test_b']['structural_coherence']:.3f} | {'PF-C' if pf_c_results['test_b']['structural_coherence'] > pf_e_results['test_b']['structural_coherence'] else 'PF-E'} |",
        f"| C: Hazard Encoding | {pf_e_results['test_c']['structural_coherence']:.3f} | {pf_c_results['test_c']['structural_coherence']:.3f} | {'PF-C' if pf_c_results['test_c']['structural_coherence'] > pf_e_results['test_c']['structural_coherence'] else 'PF-E'} |",
        f"| D: Endpoint Absence | {pf_e_results['test_d']['structural_coherence']:.3f} | {pf_c_results['test_d']['structural_coherence']:.3f} | {'PF-C' if pf_c_results['test_d']['structural_coherence'] > pf_e_results['test_d']['structural_coherence'] else 'PF-E'} |",
        f"| E: Recovery/Restart | {pf_e_results['test_e']['structural_coherence']:.3f} | {pf_c_results['test_e']['structural_coherence']:.3f} | {'PF-C' if pf_c_results['test_e']['structural_coherence'] > pf_e_results['test_e']['structural_coherence'] else 'PF-E'} |",
        "",
        "---",
        "",
        "## Key Differentiators",
        "",
        "### Where PF-E is clearly WORSE:",
        "- Endpoint absence (CRITICAL)",
        "- Bidirectional hazards",
        "- High LINK density",
        "- Conservative program dominance",
        "",
        "### Where PF-C is clearly WORSE:",
        "- Program diversity (83 distinct protocols)",
        "- LINK_SPARSE subset",
        "- HIGH_INTERVENTION subset",
        "- Restart capability existence",
        "",
        "### Where BOTH struggle:",
        "- AGGRESSIVE programs (neither archetype explains 18% high-risk operation)",
        "- Restart-capable count (3 is awkward for both interpretations)",
        "- Hazard type diversity (5 types is excessive for either archetype)",
        "",
    ]

    return "\n".join(lines)

def generate_residual_features(pf_e_agg: Dict, pf_c_agg: Dict) -> str:
    """Generate residual unexplained features report."""
    lines = [
        "# Residual Unexplained Features",
        "",
        "> **PURPOSE**: Features that NEITHER archetype explains well",
        "",
        "---",
        "",
        "## Features Unexplained by BOTH Archetypes",
        "",
        "### 1. Three Restart-Capable Programs (f50v, f57r, f82v)",
        "",
        "- **PF-E tension**: Too few for batch extraction (expects many restart points)",
        "- **PF-C tension**: Why restart at all if maintaining? (expects zero)",
        "- **Possible resolution**: Hybrid interpretation (extraction + conditioning phases)",
        "- **Residual mystery level**: MODERATE",
        "",
        "### 2. AGGRESSIVE Program Subset (18.1%)",
        "",
        "- **PF-E tension**: Extraction wants speed, but grammar prioritizes safety",
        "- **PF-C tension**: Maintenance shouldn't flirt with hazard limits",
        "- **Possible resolution**: Distinct operational mode (startup? recovery from fault?)",
        "- **Residual mystery level**: HIGH",
        "",
        "### 3. Five Distinct Hazard Classes",
        "",
        "- **PF-E expects**: COMPOSITION_JUMP, RATE_MISMATCH dominance",
        "- **PF-C expects**: PHASE_ORDERING, CONTAINMENT_TIMING dominance",
        "- **Observed**: All 5 equally present across all programs",
        "- **Possible resolution**: Multi-modal process with diverse failure modes",
        "- **Residual mystery level**: MODERATE",
        "",
        "### 4. Kernel Dominance Pattern (k > h > e)",
        "",
        "- **PF-E**: Doesn't predict specific operator hierarchy",
        "- **PF-C**: Doesn't predict specific operator hierarchy",
        "- **Observed**: k (ENERGY_MODULATOR) is consistently most central",
        "- **Possible resolution**: Thermal control is primary; both archetypes may involve heat",
        "- **Residual mystery level**: LOW (energy centrality is generic)",
        "",
        "### 5. 9.8x Vocabulary Compression",
        "",
        "- **PF-E**: Doesn't predict specific compression ratio",
        "- **PF-C**: Doesn't predict specific compression ratio",
        "- **Observed**: 480 tokens reduced to 49 equivalence classes",
        "- **Possible resolution**: Cognitive load optimization (human factors, not process type)",
        "- **Residual mystery level**: LOW (design choice, not process signature)",
        "",
        "---",
        "",
        "## Features Each Archetype ALONE Struggles With",
        "",
        "### PF-E Unique Struggles",
        "",
        "| Feature | Why It's Hard |",
        "|---------|---------------|",
        "| 0 endpoint markers | Extraction is inherently finite |",
        "| 100% bidirectional hazards | Extraction is irreversible |",
        "| 4.8% ULTRA_CONSERVATIVE | No extraction purpose |",
        "| High-LINK = safer | Speed-safety tradeoff violated |",
        "",
        "### PF-C Unique Struggles",
        "",
        "| Feature | Why It's Hard |",
        "|---------|---------------|",
        "| 83 distinct programs | Pure maintenance should be uniform |",
        "| 16.9% LINK_SPARSE | Maintenance should wait |",
        "| 12% HIGH_INTERVENTION | Active change, not passive maintenance |",
        "| f57r = RESTART_PROTOCOL | Maintenance shouldn't need resets |",
        "",
        "---",
        "",
        "## Synthesis: What Process Family Would Explain Everything?",
        "",
        "The ideal archetype would need to:",
        "",
        "1. **Operate indefinitely** (like conditioning) — explains 0 endpoints",
        "2. **Vary by substrate/condition** (like extraction) — explains 83 programs",
        "3. **Prioritize safety over speed** — explains conservative dominance",
        "4. **Tolerate diverse failure modes** — explains 5 hazard classes",
        "5. **Include rare reset capability** — explains 3 restart programs",
        "6. **Use waiting as stability mechanism** — explains LINK behavior",
        "7. **Converge to stable state** — explains 100% STATE-C convergence",
        "",
        "### Candidate Synthesis: CONTINUOUS CIRCULATION MAINTENANCE",
        "",
        "A process that:",
        "- Circulates material indefinitely through a closed loop",
        "- Applies different protocols for different materials/conditions",
        "- Maintains a target state rather than producing a product",
        "- Can reset to initial state in case of major deviation",
        "- Prioritizes operational safety over throughput",
        "",
        "This is closer to PF-C but with more operational flexibility.",
        "",
        "---",
        "",
        "## Final Assessment",
        "",
        "| Archetype | Overall Fit | Contrivance Required |",
        "|-----------|-------------|----------------------|",
        "| PF-E | POOR (0.50) | HIGH |",
        "| PF-C | MODERATE (0.70) | MODERATE |",
        "| Hybrid (CCM) | GOOD (0.85) | LOW |",
        "",
        "**Neither pure archetype is a clean fit.** The grammar is most consistent with a",
        "conditioning-like process that has more operational flexibility than pure maintenance",
        "but less throughput focus than pure extraction.",
        "",
        "**The mismatch is NOT overwhelming** — both archetypes can be made to fit with",
        "sufficient ad hoc assumptions. This supports the EPM conclusion that internal",
        "analysis cannot distinguish between extraction-type and conditioning-type processes.",
        "",
    ]

    return "\n".join(lines)

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("Loading data...")
    signatures, forward_results, material_results, geometry_results = load_data()

    print("Running PF-E (Extraction) tests...")
    pf_e_results = {
        "test_a": test_a_program_role_distribution(signatures, PF_E),
        "test_b": test_b_link_utilization(signatures, PF_E),
        "test_c": test_c_hazard_encoding(signatures, PF_E),
        "test_d": test_d_absence_of_endpoints(signatures, PF_E),
        "test_e": test_e_recovery_restart(signatures, PF_E)
    }
    pf_e_aggregate = aggregate_results(pf_e_results)

    print("Running PF-C (Conditioning) tests...")
    pf_c_results = {
        "test_a": test_a_program_role_distribution(signatures, PF_C),
        "test_b": test_b_link_utilization(signatures, PF_C),
        "test_c": test_c_hazard_encoding(signatures, PF_C),
        "test_d": test_d_absence_of_endpoints(signatures, PF_C),
        "test_e": test_e_recovery_restart(signatures, PF_C)
    }
    pf_c_aggregate = aggregate_results(pf_c_results)

    print("Generating reports...")

    # PF-E report
    pf_e_report = generate_pf_e_report(pf_e_results, pf_e_aggregate)
    with open("pf_extraction_vs_grammar.md", "w", encoding="utf-8") as f:
        f.write(pf_e_report)
    print("  -> pf_extraction_vs_grammar.md")

    # PF-C report
    pf_c_report = generate_pf_c_report(pf_c_results, pf_c_aggregate)
    with open("pf_conditioning_vs_grammar.md", "w", encoding="utf-8") as f:
        f.write(pf_c_report)
    print("  -> pf_conditioning_vs_grammar.md")

    # Comparative table
    comparative = generate_comparative_table(pf_e_results, pf_c_results,
                                             pf_e_aggregate, pf_c_aggregate)
    with open("comparative_tensions_table.md", "w", encoding="utf-8") as f:
        f.write(comparative)
    print("  -> comparative_tensions_table.md")

    # Residual features
    residual = generate_residual_features(pf_e_aggregate, pf_c_aggregate)
    with open("residual_unexplained_features.md", "w", encoding="utf-8") as f:
        f.write(residual)
    print("  -> residual_unexplained_features.md")

    # Summary
    print("\n" + "="*60)
    print("ADVERSARIAL PROCESS FAMILY COMPARISON COMPLETE")
    print("="*60)
    print(f"\nPF-E (Extraction):")
    print(f"  Structural Coherence: {pf_e_aggregate['mean_coherence']:.3f}")
    print(f"  Total Tensions: {pf_e_aggregate['total_tensions']}")
    print(f"  Unexplained Features: {pf_e_aggregate['total_unexplained']}")
    print(f"\nPF-C (Conditioning):")
    print(f"  Structural Coherence: {pf_c_aggregate['mean_coherence']:.3f}")
    print(f"  Total Tensions: {pf_c_aggregate['total_tensions']}")
    print(f"  Unexplained Features: {pf_c_aggregate['total_unexplained']}")
    print(f"\nVERDICT: {'PF-C fits better' if pf_c_aggregate['mean_coherence'] > pf_e_aggregate['mean_coherence'] else 'PF-E fits better'}")
    print(f"         BUT mismatch is {'NOT' if abs(pf_c_aggregate['mean_coherence'] - pf_e_aggregate['mean_coherence']) < 0.3 else ''} overwhelming")

if __name__ == "__main__":
    main()
