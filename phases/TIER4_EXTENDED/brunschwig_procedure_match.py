"""
Phase: Brunschwig Procedure Match Test
Tier 4 SPECULATIVE

Direct test: Can we match a specific Brunschwig procedure to a specific Voynich folio
at the structural/behavioral level?

Test Case:
- Brunschwig: Balneum Marie (Sixth Mode) - water bath distillation for flowers
- Voynich: f104r - REGIME_1, matched to Puff Ch.1 "Rosen" (Rose)
"""

import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

# =============================================================================
# BRUNSCHWIG PROCEDURE EXTRACTION
# =============================================================================

BRUNSCHWIG_BALNEUM_MARIE = {
    "name": "Sixth Mode - Balneum Marie (Water Bath)",
    "source": "Liber de arte distillandi, 1500, Chapter 6",
    "target_material": "Flowers, herbs, delicate aromatics",

    # Structural characteristics extracted from text
    "characteristics": {
        # Energy profile
        "fire_degree": 1,  # First degree (gentlest)
        "heat_instruction": "Water never boils, not hotter than finger can bear",
        "energy_profile": "LOW_SUSTAINED",

        # Recovery/forgiveness
        "recovery_instruction": "Let glass stand overnight to cool",
        "retry_allowed": True,  # Can re-distill after putrefaction
        "forgiveness": "HIGH",

        # Hazard profile
        "documented_hazards": [
            "THERMAL_SHOCK_COLD",   # Cold water drop shatters glass
            "THERMAL_SHOCK_EXIT",   # Remove hot shatters glass
            "CONTAINMENT_TIMING"    # Pressure/overflow
        ],
        "forbidden": "Boiling water (second+ degree)",

        # Monitoring requirements
        "monitoring": "CONTINUOUS",  # Finger test, refill water
        "completion_signal": "When it no longer drips",

        # Complexity
        "phases": 1,  # Single-pass distillation
        "optional_enhancement": "5-6 week putrefaction then re-distill"
    },

    # Predicted Voynich metrics for this procedure
    "predictions": {
        "regime": "REGIME_1",  # Forgiving, volatile handling
        "cei_range": (0.3, 0.6),  # Low-moderate (first degree)
        "escape_density_min": 0.15,  # HIGH forgiveness
        "hazard_density_range": (0.4, 0.7),  # Moderate (gentle but still risky)
        "intervention_freq_range": (3.0, 8.0),  # Moderate monitoring
        "recovery_ops_min": 10,  # Recovery available
    }
}


def load_folio_profile(folio_name):
    """Load a specific folio's profile."""
    with open(RESULTS_DIR / "unified_folio_profiles.json") as f:
        data = json.load(f)
    return data.get('profiles', {}).get(folio_name)


def test_procedure_match(brunschwig_proc, folio_profile):
    """Test if folio matches Brunschwig procedure predictions."""

    predictions = brunschwig_proc['predictions']
    b_metrics = folio_profile.get('b_metrics', {})

    results = []

    # Test 1: Regime Match
    predicted_regime = predictions['regime']
    actual_regime = b_metrics.get('regime')
    match = (actual_regime == predicted_regime)
    results.append({
        'test': 'REGIME',
        'predicted': predicted_regime,
        'actual': actual_regime,
        'match': match,
        'weight': 2  # High importance
    })

    # Test 2: CEI Range
    cei = b_metrics.get('cei_total', 0)
    cei_min, cei_max = predictions['cei_range']
    match = cei_min <= cei <= cei_max
    results.append({
        'test': 'CEI_RANGE',
        'predicted': f"{cei_min}-{cei_max}",
        'actual': f"{cei:.3f}",
        'match': match,
        'weight': 1.5
    })

    # Test 3: Escape Density (forgiveness)
    escape = b_metrics.get('escape_density', 0)
    escape_min = predictions['escape_density_min']
    match = escape >= escape_min
    results.append({
        'test': 'ESCAPE_DENSITY',
        'predicted': f">= {escape_min}",
        'actual': f"{escape:.3f}",
        'match': match,
        'weight': 2  # High importance for "forgiving" match
    })

    # Test 4: Hazard Density Range
    hazard = b_metrics.get('hazard_density', 0)
    haz_min, haz_max = predictions['hazard_density_range']
    match = haz_min <= hazard <= haz_max
    results.append({
        'test': 'HAZARD_RANGE',
        'predicted': f"{haz_min}-{haz_max}",
        'actual': f"{hazard:.3f}",
        'match': match,
        'weight': 1
    })

    # Test 5: Intervention Frequency
    intervention = b_metrics.get('intervention_frequency', 0)
    int_min, int_max = predictions['intervention_freq_range']
    match = int_min <= intervention <= int_max
    results.append({
        'test': 'INTERVENTION_FREQ',
        'predicted': f"{int_min}-{int_max}",
        'actual': f"{intervention:.2f}",
        'match': match,
        'weight': 1
    })

    # Test 6: Recovery Operations Available
    recovery = b_metrics.get('recovery_ops_count', 0)
    recovery_min = predictions['recovery_ops_min']
    match = recovery >= recovery_min
    results.append({
        'test': 'RECOVERY_OPS',
        'predicted': f">= {recovery_min}",
        'actual': str(recovery),
        'match': match,
        'weight': 1.5
    })

    return results


def score_results(results):
    """Calculate weighted match score."""
    total_weight = sum(r['weight'] for r in results)
    matched_weight = sum(r['weight'] for r in results if r['match'])
    return matched_weight / total_weight if total_weight > 0 else 0


def find_best_match(brunschwig_proc):
    """Find which REGIME_1 folio best matches the procedure."""
    with open(RESULTS_DIR / "unified_folio_profiles.json") as f:
        data = json.load(f)

    candidates = []
    for folio_name, profile in data.get('profiles', {}).items():
        if profile.get('system') != 'B':
            continue
        b_metrics = profile.get('b_metrics', {})
        if b_metrics.get('regime') == 'REGIME_1':
            results = test_procedure_match(brunschwig_proc, profile)
            score = score_results(results)
            candidates.append({
                'folio': folio_name,
                'score': score,
                'results': results
            })

    candidates.sort(key=lambda x: -x['score'])
    return candidates


def main():
    print("=" * 70)
    print("BRUNSCHWIG PROCEDURE MATCH TEST")
    print("=" * 70)

    print("\n--- Brunschwig Procedure ---")
    print(f"Name: {BRUNSCHWIG_BALNEUM_MARIE['name']}")
    print(f"Source: {BRUNSCHWIG_BALNEUM_MARIE['source']}")
    print(f"Target Material: {BRUNSCHWIG_BALNEUM_MARIE['target_material']}")

    chars = BRUNSCHWIG_BALNEUM_MARIE['characteristics']
    print(f"\nFire Degree: {chars['fire_degree']} (gentlest)")
    print(f"Heat Instruction: {chars['heat_instruction']}")
    print(f"Recovery: {chars['recovery_instruction']}")
    print(f"Forgiveness: {chars['forgiveness']}")
    print(f"Documented Hazards: {', '.join(chars['documented_hazards'])}")

    # Test primary candidate: f104r
    print("\n" + "=" * 70)
    print("PRIMARY TEST: f104r (Puff Ch.1 'Rosen' match)")
    print("=" * 70)

    f104r = load_folio_profile('f104r')
    if not f104r:
        print("ERROR: Could not load f104r profile")
        return

    results = test_procedure_match(BRUNSCHWIG_BALNEUM_MARIE, f104r)

    print("\n--- Test Results ---")
    print(f"{'Test':<20} {'Predicted':<15} {'Actual':<15} {'Match':<8} {'Weight':<8}")
    print("-" * 70)

    for r in results:
        match_str = "YES" if r['match'] else "NO"
        print(f"{r['test']:<20} {r['predicted']:<15} {r['actual']:<15} {match_str:<8} {r['weight']:<8}")

    score = score_results(results)
    matches = sum(1 for r in results if r['match'])

    print("-" * 70)
    print(f"Score: {score:.1%} ({matches}/{len(results)} tests)")

    # Verdict
    if score >= 0.9:
        verdict = "STRONG_MATCH"
    elif score >= 0.75:
        verdict = "GOOD_MATCH"
    elif score >= 0.5:
        verdict = "PARTIAL_MATCH"
    else:
        verdict = "WEAK_MATCH"

    print(f"\nVERDICT: {verdict}")

    # Find best match among all REGIME_1 folios
    print("\n" + "=" * 70)
    print("COMPARATIVE ANALYSIS: All REGIME_1 Folios")
    print("=" * 70)

    candidates = find_best_match(BRUNSCHWIG_BALNEUM_MARIE)

    print(f"\n{'Rank':<6} {'Folio':<10} {'Score':<10} {'Tests Passed':<15}")
    print("-" * 45)

    for i, c in enumerate(candidates[:10], 1):
        passed = sum(1 for r in c['results'] if r['match'])
        print(f"{i:<6} {c['folio']:<10} {c['score']:.1%}{'':>5} {passed}/{len(c['results'])}")

    # Check if f104r is top match
    f104r_rank = next((i for i, c in enumerate(candidates, 1) if c['folio'] == 'f104r'), None)

    print(f"\nf104r rank among {len(candidates)} REGIME_1 folios: #{f104r_rank}")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if f104r_rank == 1 and score >= 0.75:
        conclusion = "STRONG_PROCEDURAL_MATCH"
        interpretation = """
f104r is the BEST match for Brunschwig's Balneum Marie procedure among all
REGIME_1 folios. This supports the hypothesis that:

1. f104r encodes a water-bath flower distillation procedure
2. The Puff-Voynich matching (Ch.1 Rosen -> f104r) is structurally valid
3. Voynich regimes map to Brunschwig's fire degrees

This is STRUCTURAL correspondence at the PROCEDURE level, not just axis-level.
"""
    elif f104r_rank and f104r_rank <= 5 and score >= 0.5:
        conclusion = "PARTIAL_PROCEDURAL_MATCH"
        interpretation = """
f104r shows partial correspondence to Brunschwig's Balneum Marie procedure.
The match is not perfect but the folio is among the top candidates.

This suggests structural alignment without definitive 1:1 correspondence.
"""
    else:
        conclusion = "WEAK_PROCEDURAL_MATCH"
        interpretation = """
f104r does not strongly match Brunschwig's Balneum Marie predictions.
The structural correspondence is weaker than expected.
"""

    print(f"\nCONCLUSION: {conclusion}")
    print(interpretation)

    # Save results
    output = {
        "test": "BRUNSCHWIG_PROCEDURE_MATCH",
        "tier": 4,
        "status": "SPECULATIVE",
        "date": "2026-01-14",
        "brunschwig_procedure": BRUNSCHWIG_BALNEUM_MARIE['name'],
        "primary_candidate": {
            "folio": "f104r",
            "puff_match": "Chapter 1 - Rosen (Rose)",
            "score": score,
            "tests_passed": matches,
            "tests_total": len(results),
            "results": results
        },
        "all_regime1_candidates": [
            {"folio": c['folio'], "score": c['score']}
            for c in candidates[:10]
        ],
        "f104r_rank": f104r_rank,
        "verdict": conclusion
    }

    with open(RESULTS_DIR / "brunschwig_procedure_match.json", 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to results/brunschwig_procedure_match.json")


if __name__ == "__main__":
    main()
