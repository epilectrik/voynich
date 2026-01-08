"""
Phase EXT-MAT-01: Material Domain Discrimination

Stress test to determine whether structural evidence better supports:
- ALCHEMICAL-MINERAL (mercury, antimony, gold preparations)
- AROMATIC-BOTANICAL (rose water, essential oils, resins)

This phase uses ONLY structural evidence already gathered.
It does NOT assign semantics or identify specific products.
"""

import json
import os
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# TEST DEFINITIONS
# =============================================================================

def test_1_illustration_alignment():
    """
    Test 1: Illustration Content Alignment

    PIAA found 86.7% of botanical illustrations are perfumery-aligned.
    If manuscript encodes alchemical-mineral work, why aromatic plant illustrations?

    Alchemical prediction: Illustrations should show apparatus, symbols, or be abstract
    Botanical prediction: Illustrations should show aromatic plants
    """
    # From PIAA findings
    perfumery_aligned = 0.867  # 86.7%
    root_emphasis = 0.73       # 73%
    blue_purple_flowers = 0.47 # 47%
    food_plants = 0.033        # 3.3%
    dye_plants = 0.0           # 0%

    # Alchemical texts typically show:
    # - Apparatus diagrams
    # - Symbolic imagery (dragons, lions, kings/queens)
    # - Abstract geometric forms
    # - NO botanical content unless discussing plant-derived materials

    # Score: How well does illustration content match each domain?
    botanical_score = perfumery_aligned  # Direct match

    # Alchemical score: aromatic plant illustrations are UNEXPECTED
    # Some alchemical texts do use botanical imagery symbolically, but 86.7% aromatic is very high
    alchemical_score = 1.0 - perfumery_aligned  # Inverse - aromatic plants unexpected

    # Adjustment: Root emphasis is notable for extraction (orris root, angelica root)
    # This slightly favors botanical (extraction source awareness)
    botanical_score += root_emphasis * 0.1

    return {
        'test': 1,
        'name': 'Illustration Content Alignment',
        'metrics': {
            'perfumery_aligned_rate': perfumery_aligned,
            'root_emphasis': root_emphasis,
            'blue_purple_flowers': blue_purple_flowers,
            'food_plants': food_plants,
            'dye_plants': dye_plants,
        },
        'alchemical_prediction': 'Apparatus, symbols, abstract forms expected; aromatic plants unexpected',
        'botanical_prediction': 'Aromatic plant illustrations expected',
        'observed': f'{perfumery_aligned:.1%} perfumery-aligned, {root_emphasis:.0%} root emphasis',
        'alchemical_score': round(alchemical_score, 3),
        'botanical_score': round(min(1.0, botanical_score), 3),
        'verdict': 'BOTANICAL' if botanical_score > alchemical_score else 'ALCHEMICAL',
        'confidence': 'HIGH' if abs(botanical_score - alchemical_score) > 0.5 else 'MODERATE'
    }


def test_2_danger_profile():
    """
    Test 2: Danger/Toxicity Profile

    EXT-ECO-01 found hazards encode opportunity-loss, not physical catastrophe.

    Alchemical prediction: Mercury/antimony work is LETHAL. Hazards should encode mortal danger.
    Botanical prediction: Aromatic work is SAFE. Hazards encode economic loss only.
    """
    # From EXT-ECO-01
    premature_hazards = 0.647      # 64.7% premature action
    late_hazards = 0.0             # 0% late action
    opportunity_loss_fit = 'STRONG'
    physical_instability_fit = 'WEAK'

    # Alchemical hazards would include:
    # - Mercury volatilization → poisoning
    # - Antimony toxicity → death
    # - Corrosive acid burns
    # - These are PHYSICAL CATASTROPHES, not just economic losses

    # Botanical hazards would include:
    # - Ruined batch (economic loss)
    # - Lost material (economic loss)
    # - Wasted time (opportunity loss)
    # - NO mortal danger from rose water

    # The EXT-ECO-01 finding of "opportunity loss not physical catastrophe"
    # STRONGLY favors botanical interpretation

    alchemical_score = 0.2  # Opportunity-loss doesn't match lethal materials
    botanical_score = 0.9   # Opportunity-loss perfectly matches aromatic work

    return {
        'test': 2,
        'name': 'Danger/Toxicity Profile',
        'metrics': {
            'premature_hazards': premature_hazards,
            'late_hazards': late_hazards,
            'opportunity_loss_fit': opportunity_loss_fit,
            'physical_instability_fit': physical_instability_fit,
        },
        'alchemical_prediction': 'Mercury/antimony hazards should encode mortal danger',
        'botanical_prediction': 'Aromatic hazards encode economic loss only',
        'observed': f'Opportunity-loss DOMINANT, physical-instability WEAK',
        'alchemical_score': alchemical_score,
        'botanical_score': botanical_score,
        'verdict': 'BOTANICAL',
        'confidence': 'HIGH'
    }


def test_3_product_diversity():
    """
    Test 3: Product/Program Diversity

    83 distinct programs in 8 families.

    Alchemical prediction: Few products (philosopher's stone, elixir, aurum potabile)
                          Many programs = variations on few products
    Botanical prediction: Many products (rose, lavender, orange, dozens of herbs)
                         Many programs = different source materials
    """
    total_programs = 83
    total_families = 8
    programs_per_family = total_programs / total_families  # ~10.4

    # Alchemical product space is SMALL:
    # - Philosopher's stone (1 product, many attempts)
    # - Elixir of life (1 product)
    # - Aurum potabile (1 product)
    # - Philosophical mercury (1 product)
    # Total: ~4-6 distinct products

    # Aromatic product space is LARGE:
    # - Rose water, lavender water, orange flower water
    # - Fennel oil, rosemary oil, mint oil
    # - Frankincense, myrrh, benzoin extracts
    # - Potentially dozens of distinct products

    # 83 programs makes more sense for a diverse product space
    # Alchemical work would need ~10-20 programs max

    # Scoring based on product space match
    if total_programs > 50:
        botanical_score = 0.8
        alchemical_score = 0.3
    elif total_programs > 20:
        botanical_score = 0.6
        alchemical_score = 0.5
    else:
        botanical_score = 0.4
        alchemical_score = 0.7

    return {
        'test': 3,
        'name': 'Product/Program Diversity',
        'metrics': {
            'total_programs': total_programs,
            'total_families': total_families,
            'programs_per_family': round(programs_per_family, 1),
        },
        'alchemical_prediction': 'Few products (4-6), many variations → expect 10-20 programs',
        'botanical_prediction': 'Many products (dozens), similar process → expect 50-100 programs',
        'observed': f'{total_programs} programs in {total_families} families',
        'alchemical_score': alchemical_score,
        'botanical_score': botanical_score,
        'verdict': 'BOTANICAL' if botanical_score > alchemical_score else 'ALCHEMICAL',
        'confidence': 'MODERATE'
    }


def test_4_duration_semantics():
    """
    Test 4: Duration Semantics (Post SID-05 Revision)

    SID-05 found attentional pacing = hours of active monitoring.

    Alchemical prediction: Weeks to months (digestion, circulation)
    Botanical prediction: Hours to days (distillation runs)
    """
    # SID-05 findings
    attention_model_wins = True
    position_independent = True  # r=0.017
    boundary_reset = True        # 17.6% within vs 0% cross

    # These indicate SHORT duration (hours) not LONG duration (weeks)
    # Operator is PRESENT and FOCUSED, not checking in periodically

    # Alchemical duration expectations:
    # - Philosophical mercury: weeks of sublimation/digestion
    # - Aurum potabile: months of circulation
    # - Mercurial elixirs: 40+ days minimum

    # Botanical duration expectations:
    # - Rose water: 4-6 hours
    # - Essential oils: hours to days
    # - Cohobation: hours per cycle

    alchemical_score = 0.2  # SID-05 contradicts weeks/months
    botanical_score = 0.9   # SID-05 supports hours of attention

    return {
        'test': 4,
        'name': 'Duration Semantics',
        'metrics': {
            'attention_model_wins': attention_model_wins,
            'position_independent': position_independent,
            'boundary_reset': boundary_reset,
        },
        'alchemical_prediction': 'Weeks to months duration',
        'botanical_prediction': 'Hours to days duration',
        'observed': 'SID-05: Attentional pacing = active monitoring (hours)',
        'alchemical_score': alchemical_score,
        'botanical_score': botanical_score,
        'verdict': 'BOTANICAL',
        'confidence': 'HIGH'
    }


def test_5_restart_semantics():
    """
    Test 5: Restart Cost Semantics

    Only 3.6% restart-capable. Failure = binary loss.

    Alchemical prediction: Restart loses EXPENSIVE MATERIALS (gold, mercury)
    Botanical prediction: Restart loses PERISHABLE MATERIAL (today's harvest)
    """
    restart_rate = 0.036  # 3.6%
    binary_penalty = True

    # Both domains have "catastrophic restart" but for different reasons:

    # Alchemical:
    # - Gold is expensive (material cost)
    # - Mercury is expensive (material cost)
    # - Weeks of accumulated work lost (time cost)
    # - Restart requires PURCHASING new materials

    # Botanical:
    # - Rose petals must be distilled same day (perishability)
    # - Tomorrow's petals require waiting for next harvest
    # - Restart requires WAITING, not purchasing
    # - Fresh material is abundant during season

    # The key distinction: material cost vs time cost
    # EXT-ECO-01's "opportunity loss" language suggests TIME not MONEY

    # Score based on opportunity-loss framing
    alchemical_score = 0.5  # Material cost is also "loss"
    botanical_score = 0.7   # Time/opportunity cost fits better

    return {
        'test': 5,
        'name': 'Restart Cost Semantics',
        'metrics': {
            'restart_rate': restart_rate,
            'binary_penalty': binary_penalty,
        },
        'alchemical_prediction': 'Restart loses expensive purchased materials',
        'botanical_prediction': 'Restart loses perishable time-bound opportunity',
        'observed': f'{restart_rate:.1%} restart-capable, binary penalty',
        'alchemical_score': alchemical_score,
        'botanical_score': botanical_score,
        'verdict': 'BOTANICAL' if botanical_score > alchemical_score else 'ALCHEMICAL',
        'confidence': 'LOW'  # Both interpretations work here
    }


def test_6_historical_documentation():
    """
    Test 6: Historical Documentation Pattern

    The manuscript has NO theoretical content, NO material specifications,
    pure operational instructions.

    Alchemical prediction: Alchemical texts are famously obscure, symbolic, encoded
    Botanical prediction: Practical manuals are operational and direct
    """
    # From EXT-7 structural parallel search
    theoretical_content = 0.0       # 0% theory
    material_specifications = 0.0   # 0% material encoding
    pure_operational = 1.0          # 100% operational

    # Alchemical documentation patterns:
    # - Heavy symbolic language (green lion, philosophical mercury)
    # - Deliberate obscurity (veil of secrecy)
    # - Theoretical frameworks (four elements, three principles)
    # - BUT: some operational texts exist (pseudo-Geber)

    # Botanical/perfumery documentation patterns:
    # - Practical instruction (Brunschwig 1500)
    # - Material lists common but not always
    # - Process focus
    # - Guild secrecy but less symbolic

    # The Voynich is EXTREMELY operational with 0 theory
    # This is unusual for alchemical texts but fits craft manuals

    # However, EXT-7 found Voynich is "structurally exceptional" for BOTH domains
    # Neither domain has a perfect parallel

    alchemical_score = 0.4  # Some operational alchemical texts exist
    botanical_score = 0.6   # Craft manuals are more purely operational

    return {
        'test': 6,
        'name': 'Historical Documentation Pattern',
        'metrics': {
            'theoretical_content': theoretical_content,
            'material_specifications': material_specifications,
            'pure_operational': pure_operational,
        },
        'alchemical_prediction': 'Symbolic, encoded, theoretical elements expected',
        'botanical_prediction': 'Practical, operational, direct instruction expected',
        'observed': '0% theory, 100% operational, structurally exceptional',
        'alchemical_score': alchemical_score,
        'botanical_score': botanical_score,
        'verdict': 'BOTANICAL' if botanical_score > alchemical_score else 'ALCHEMICAL',
        'confidence': 'LOW'  # Both domains have operational texts
    }


def test_7_section_semantics():
    """
    Test 7: Section Structure Interpretation

    8 sections (families) with distinct vocabularies.

    Alchemical prediction: Sections = stages of Great Work (nigredo, albedo, rubedo)
                          or different alchemical operations
    Botanical prediction: Sections = different source materials or product types
    """
    total_sections = 8
    vocabulary_exclusivity = 0.807  # 80.7% section-exclusive tokens

    # Alchemical section structure:
    # - 3-4 stages of transmutation would be expected
    # - 7 planetary metals possible
    # - 8 sections is unusual for alchemical framework

    # Botanical section structure:
    # - Different plant families or types
    # - Different product categories (waters, oils, resins)
    # - 8 sections is reasonable for diverse botanical work

    # 80.7% vocabulary exclusivity suggests DIFFERENT MATERIALS per section
    # This fits botanical better (different plants = different vocabulary)
    # Alchemical would use more shared vocabulary (same operations on different metals)

    alchemical_score = 0.4  # 8 sections unusual, high exclusivity unexpected
    botanical_score = 0.7   # Different materials = different vocabulary

    return {
        'test': 7,
        'name': 'Section Structure Interpretation',
        'metrics': {
            'total_sections': total_sections,
            'vocabulary_exclusivity': vocabulary_exclusivity,
        },
        'alchemical_prediction': '3-4 stages or 7 metals; shared operational vocabulary',
        'botanical_prediction': 'Multiple material types; distinct vocabularies per material',
        'observed': f'{total_sections} sections, {vocabulary_exclusivity:.1%} vocabulary exclusivity',
        'alchemical_score': alchemical_score,
        'botanical_score': botanical_score,
        'verdict': 'BOTANICAL',
        'confidence': 'MODERATE'
    }


def test_8_apparatus_fit():
    """
    Test 8: Apparatus Compatibility (Pelican Alembic)

    Prior analysis identified pelican alembic as best apparatus match.

    Both domains used pelican alembics, but for different purposes:
    Alchemical: Circulation for months (philosophical work)
    Botanical: Cohobation for hours (concentration, extraction)
    """
    # Pelican alembic characteristics that matter:
    link_density = 0.376          # 37.6% waiting
    premature_hazards = 0.647     # Patience required
    no_endpoint_markers = True    # Operator judges completion

    # Alchemical pelican use:
    # - Months of circulation
    # - Checking periodically
    # - Slow transformation

    # Botanical pelican use:
    # - Hours of cohobation
    # - Active monitoring
    # - Concentration through repeated distillation

    # Given SID-05 (hours not weeks), botanical use fits better
    # But pelican itself is compatible with both

    alchemical_score = 0.5  # Pelican used for philosophical work
    botanical_score = 0.7   # Pelican + short duration = cohobation

    return {
        'test': 8,
        'name': 'Apparatus Usage Pattern',
        'metrics': {
            'link_density': link_density,
            'premature_hazards': premature_hazards,
            'no_endpoint_markers': no_endpoint_markers,
        },
        'alchemical_prediction': 'Pelican for months-long philosophical circulation',
        'botanical_prediction': 'Pelican for hours-long cohobation/concentration',
        'observed': 'Pelican compatible, but SID-05 duration favors short cycles',
        'alchemical_score': alchemical_score,
        'botanical_score': botanical_score,
        'verdict': 'BOTANICAL' if botanical_score > alchemical_score else 'ALCHEMICAL',
        'confidence': 'LOW'  # Apparatus fits both
    }


def generate_summary(results):
    """Generate summary statistics and overall verdict."""
    alchemical_total = sum(r['alchemical_score'] for r in results)
    botanical_total = sum(r['botanical_score'] for r in results)

    verdicts = [r['verdict'] for r in results]
    botanical_wins = verdicts.count('BOTANICAL')
    alchemical_wins = verdicts.count('ALCHEMICAL')

    high_confidence = [r for r in results if r['confidence'] == 'HIGH']
    high_conf_botanical = sum(1 for r in high_confidence if r['verdict'] == 'BOTANICAL')
    high_conf_alchemical = sum(1 for r in high_confidence if r['verdict'] == 'ALCHEMICAL')

    # Overall verdict
    if botanical_total > alchemical_total * 1.3:
        overall = 'BOTANICAL_FAVORED'
        confidence = 'MODERATE' if botanical_total > alchemical_total * 1.5 else 'LOW'
    elif alchemical_total > botanical_total * 1.3:
        overall = 'ALCHEMICAL_FAVORED'
        confidence = 'MODERATE' if alchemical_total > botanical_total * 1.5 else 'LOW'
    else:
        overall = 'INDETERMINATE'
        confidence = 'LOW'

    # Strengthen confidence if high-confidence tests align
    if len(high_confidence) >= 2:
        if high_conf_botanical >= 2 and high_conf_alchemical == 0:
            confidence = 'HIGH' if overall == 'BOTANICAL_FAVORED' else confidence
        elif high_conf_alchemical >= 2 and high_conf_botanical == 0:
            confidence = 'HIGH' if overall == 'ALCHEMICAL_FAVORED' else confidence

    return {
        'alchemical_total_score': round(alchemical_total, 2),
        'botanical_total_score': round(botanical_total, 2),
        'score_ratio': round(botanical_total / alchemical_total, 2) if alchemical_total > 0 else float('inf'),
        'botanical_wins': botanical_wins,
        'alchemical_wins': alchemical_wins,
        'high_confidence_tests': len(high_confidence),
        'high_conf_botanical': high_conf_botanical,
        'high_conf_alchemical': high_conf_alchemical,
        'overall_verdict': overall,
        'confidence': confidence,
    }


def generate_report(results, summary, output_path):
    """Generate markdown report."""
    report = f"""# Phase EXT-MAT-01: Material Domain Discrimination

**Status:** COMPLETE
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Tier:** 3 (External Alignment Only)

---

## Purpose

Stress test to determine whether structural evidence better supports:
- **ALCHEMICAL-MINERAL** (mercury, antimony, gold preparations)
- **AROMATIC-BOTANICAL** (rose water, essential oils, resins)

---

## Test Results

"""
    for r in results:
        report += f"""### Test {r['test']}: {r['name']}

| Metric | Value |
|--------|-------|
"""
        for k, v in r['metrics'].items():
            report += f"| {k} | {v} |\n"

        report += f"""
**Alchemical Prediction:** {r['alchemical_prediction']}
**Botanical Prediction:** {r['botanical_prediction']}

**Observed:** {r['observed']}

| Domain | Score |
|--------|-------|
| Alchemical | {r['alchemical_score']} |
| Botanical | {r['botanical_score']} |

**Verdict:** {r['verdict']} (Confidence: {r['confidence']})

---

"""

    report += f"""## Summary

### Score Totals

| Domain | Total Score | Test Wins |
|--------|-------------|-----------|
| Alchemical | {summary['alchemical_total_score']} | {summary['alchemical_wins']} |
| Botanical | {summary['botanical_total_score']} | {summary['botanical_wins']} |

**Score Ratio (Botanical/Alchemical):** {summary['score_ratio']}

### High-Confidence Tests

| Metric | Value |
|--------|-------|
| High-confidence tests | {summary['high_confidence_tests']} |
| Botanical wins (high conf) | {summary['high_conf_botanical']} |
| Alchemical wins (high conf) | {summary['high_conf_alchemical']} |

---

## Overall Verdict

**{summary['overall_verdict']}** (Confidence: **{summary['confidence']}**)

"""

    if summary['overall_verdict'] == 'BOTANICAL_FAVORED':
        report += """### Why Botanical Wins

The structural evidence favors aromatic-botanical interpretation because:

1. **Illustrations are 86.7% perfumery-aligned** — If this were alchemical, why aromatic plant drawings?
2. **Hazards encode opportunity-loss, not physical danger** — Mercury kills; rose water doesn't
3. **83 programs suggests diverse product space** — Alchemical work has few products
4. **Duration is hours, not weeks** — SID-05 contradicts alchemical timescales
5. **Section vocabulary is highly exclusive** — Different materials = different vocabulary

### Caveats

- Pelican apparatus fits both domains
- Expert-only context fits both domains
- Some alchemical texts are purely operational
- Historical documentation patterns overlap

"""
    elif summary['overall_verdict'] == 'ALCHEMICAL_FAVORED':
        report += """### Why Alchemical Wins

The structural evidence favors alchemical-mineral interpretation because:

[Specific reasons would be listed here if alchemical won]

"""
    else:
        report += """### Why Indeterminate

The structural evidence does not decisively favor either interpretation:

- Both domains use pelican alembics
- Both require expert knowledge
- Both involve closed-loop circulation
- Historical documentation patterns overlap

**Internal analysis cannot distinguish between these interpretations.**

"""

    report += """---

## Interpretive Boundary

This analysis evaluates structural fit only. It does NOT:
- Identify specific products
- Assign semantics to tokens
- Prove historical identity
- Exclude either interpretation definitively

---

*EXT-MAT-01 COMPLETE.*
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)


def main():
    """Main analysis pipeline."""
    print("Phase EXT-MAT-01: Material Domain Discrimination")
    print("=" * 60)

    # Run all tests
    print("\nRunning discrimination tests...")
    results = []

    print("  Test 1: Illustration Content Alignment")
    results.append(test_1_illustration_alignment())

    print("  Test 2: Danger/Toxicity Profile")
    results.append(test_2_danger_profile())

    print("  Test 3: Product/Program Diversity")
    results.append(test_3_product_diversity())

    print("  Test 4: Duration Semantics")
    results.append(test_4_duration_semantics())

    print("  Test 5: Restart Cost Semantics")
    results.append(test_5_restart_semantics())

    print("  Test 6: Historical Documentation Pattern")
    results.append(test_6_historical_documentation())

    print("  Test 7: Section Structure Interpretation")
    results.append(test_7_section_semantics())

    print("  Test 8: Apparatus Usage Pattern")
    results.append(test_8_apparatus_fit())

    # Generate summary
    print("\nGenerating summary...")
    summary = generate_summary(results)

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    for r in results:
        print(f"\n  Test {r['test']}: {r['name']}")
        print(f"    Alchemical: {r['alchemical_score']}")
        print(f"    Botanical:  {r['botanical_score']}")
        print(f"    Verdict:    {r['verdict']} ({r['confidence']})")

    print(f"\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Alchemical Total: {summary['alchemical_total_score']}")
    print(f"  Botanical Total:  {summary['botanical_total_score']}")
    print(f"  Ratio (B/A):      {summary['score_ratio']}")
    print(f"  Botanical Wins:   {summary['botanical_wins']}/8")
    print(f"  Alchemical Wins:  {summary['alchemical_wins']}/8")
    print(f"\n  OVERALL: {summary['overall_verdict']} ({summary['confidence']})")

    # Save outputs
    print("\nSaving outputs...")

    json_path = os.path.join(OUTPUT_DIR, 'ext_mat_01_results.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'phase': 'EXT-MAT-01',
                'title': 'Material Domain Discrimination',
                'timestamp': datetime.now().isoformat(),
            },
            'test_results': results,
            'summary': summary,
        }, f, indent=2)
    print(f"  Written: {json_path}")

    report_path = os.path.join(OUTPUT_DIR, 'EXT_MAT_01_REPORT.md')
    generate_report(results, summary, report_path)
    print(f"  Written: {report_path}")

    print("\n" + "=" * 60)
    print("EXT-MAT-01 COMPLETE")
    print("=" * 60)

    return results, summary


if __name__ == '__main__':
    main()
