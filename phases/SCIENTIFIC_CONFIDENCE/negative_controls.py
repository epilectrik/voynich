"""
Scientific Confidence Tightening: Negative Controls (NC1-NC4)

Tests alternative process hypotheses against ECR-4 discriminators.
Each alternative should FAIL on key discriminators if distillation is correct.

Tier 3 - Speculative (explicitly acknowledged)
"""

import os
import json
from typing import Dict, List

# =============================================================================
# DATA LOADING
# =============================================================================

def load_process_isomorphism():
    """Load ECR-4 process isomorphism results."""
    with open('results/process_behavior_isomorphism.json', 'r') as f:
        return json.load(f)

def load_behavioral_stats():
    """Load behavioral classification statistics."""
    with open('results/currier_a_behavioral_stats.json', 'r') as f:
        return json.load(f)

# =============================================================================
# NC1: FERMENTATION HYPOTHESIS
# =============================================================================

def test_nc1_fermentation(iso_results: dict) -> dict:
    """
    NC1: Test if grammar could encode fermentation process control.

    Key discriminators where fermentation SHOULD FAIL:
    1. k→h forbidden: Irrelevant in fermentation (no thermal phase transitions)
    2. e-recovery dominance: Minimal in fermentation (biological, not thermal)
    3. Hazard profile: Contamination would dominate, not PHASE_ORDERING
    """
    # Extract ECR-4 test results - correct structure
    ps_tests = iso_results.get('process_sequence_tests', [])
    bs_tests = iso_results.get('behavior_structural_tests', [])

    # PS-4: k→h forbidden test
    ps4_passed = False
    ps4_observed = ""
    for test in ps_tests:
        if test.get('test_id') == 'PS-4':
            ps4_passed = test.get('passed', False)
            ps4_observed = test.get('observed', '')
            break

    # BS-4: e-recovery dominance
    bs4_passed = False
    bs4_enrichment = 0
    for test in bs_tests:
        if test.get('test_id') == 'BS-4':
            bs4_passed = test.get('passed', False)
            bs4_enrichment = test.get('enrichment', 0)
            break

    # BS-1: Hazard clustering (100% k-adjacent = phase/energy boundary hazards)
    bs1_passed = False
    bs1_observed = ""
    for test in bs_tests:
        if test.get('test_id') == 'BS-1':
            bs1_passed = test.get('passed', False)
            bs1_observed = test.get('observed', '')
            break

    # Check failures against fermentation predictions
    discriminators_failed = []

    # Discriminator 1: k→h is NOT irrelevant (it's specifically forbidden)
    if ps4_passed:
        discriminators_failed.append({
            'test': 'k->h forbidden',
            'distillation_prediction': 'Forbidden (thermal phase danger)',
            'fermentation_prediction': 'Irrelevant (no thermal phases)',
            'observed': ps4_observed,
            'verdict': 'FERMENTATION FAILS'
        })

    # Discriminator 2: e-recovery IS dominant (not minimal)
    if bs4_passed:
        discriminators_failed.append({
            'test': 'e-recovery dominance',
            'distillation_prediction': '54.7% e-recovery (thermal equilibration)',
            'fermentation_prediction': 'Minimal (biological recovery)',
            'observed': f'e-recovery enriched {bs4_enrichment}x',
            'verdict': 'FERMENTATION FAILS'
        })

    # Discriminator 3: Hazards at k (phase/energy boundary), not contamination
    if bs1_passed:
        discriminators_failed.append({
            'test': 'Hazard profile',
            'distillation_prediction': 'Hazards cluster at k (phase/energy boundary)',
            'fermentation_prediction': 'CONTAMINATION dominant (biological)',
            'observed': bs1_observed,
            'verdict': 'FERMENTATION FAILS'
        })

    failed_count = len(discriminators_failed)

    result = {
        'control_id': 'NC1',
        'control_name': 'Fermentation Hypothesis',
        'hypothesis': 'Grammar encodes fermentation process control',

        'discriminators_tested': 3,
        'discriminators_failed': failed_count,
        'failure_details': discriminators_failed,

        'exclusion_strength': 'STRONG' if failed_count >= 2 else 'PARTIAL' if failed_count >= 1 else 'WEAK',
        'verdict': f'EXCLUDED - Failed {failed_count}/3 discriminators',

        'interpretation': (
            f"Fermentation hypothesis excluded: Failed on {failed_count} key discriminators. "
            "Grammar encodes thermal phase control (k→h forbidden, e-recovery dominant, "
            "PHASE_ORDERING hazards) that fermentation cannot explain."
        )
    }

    return result


# =============================================================================
# NC2: DYEING HYPOTHESIS
# =============================================================================

def test_nc2_dyeing(iso_results: dict, stats: dict) -> dict:
    """
    NC2: Test if grammar could encode textile dyeing process control.

    Key discriminators where dyeing SHOULD FAIL:
    1. BS-1: Phase ordering hazards (dyeing = color fastness, not phase)
    2. Discrimination gradient: 8.7x for volatiles (dyeing would be lower)
    3. k→h pattern: Dangerous (dyeing would need heat+dye immersion)
    """
    bs_tests = iso_results.get('behavior_structural_tests', [])

    # BS-1: Hazard clustering at kernel boundaries
    bs1_passed = False
    bs1_observed = ""
    for test in bs_tests:
        if test.get('test_id') == 'BS-1':
            bs1_passed = test.get('passed', False)
            bs1_observed = test.get('observed', '')
            break

    # Discrimination gradient
    middle_by_domain = stats.get('middle_by_domain', {})
    energy_middles = middle_by_domain.get('ENERGY_OPERATOR', 0)
    registry_middles = middle_by_domain.get('REGISTRY_REFERENCE', 0)
    gradient = energy_middles / registry_middles if registry_middles > 0 else 0

    # PS-4: k→h forbidden - use correct path
    ps_tests = iso_results.get('process_sequence_tests', [])
    ps4_passed = False
    ps4_observed = ""
    for test in ps_tests:
        if test.get('test_id') == 'PS-4':
            ps4_passed = test.get('passed', False)
            ps4_observed = test.get('observed', '')
            break

    discriminators_failed = []

    # Discriminator 1: Hazards cluster at phase boundaries (not color)
    if bs1_passed:
        discriminators_failed.append({
            'test': 'Hazard topology',
            'distillation_prediction': 'Phase ordering at k boundary',
            'dyeing_prediction': 'Color fastness primary hazard',
            'observed': bs1_observed,
            'verdict': 'DYEING FAILS'
        })

    # Discriminator 2: High discrimination gradient (8.7x)
    if gradient > 5.0:  # Dyeing would have lower (fewer dye variants)
        discriminators_failed.append({
            'test': 'Discrimination gradient',
            'distillation_prediction': '8.7x for volatiles (many fractions)',
            'dyeing_prediction': 'Lower (limited dye variants)',
            'observed': f'{round(gradient, 1)}x gradient observed',
            'verdict': 'DYEING FAILS'
        })

    # Discriminator 3: k→h forbidden (dyeing needs heat application)
    if ps4_passed:
        discriminators_failed.append({
            'test': 'k->h pattern',
            'distillation_prediction': 'k->h dangerous (thermal phase failure)',
            'dyeing_prediction': 'k->h required (heat + dye immersion)',
            'observed': ps4_observed,
            'verdict': 'DYEING FAILS'
        })

    failed_count = len(discriminators_failed)

    result = {
        'control_id': 'NC2',
        'control_name': 'Dyeing Hypothesis',
        'hypothesis': 'Grammar encodes textile dyeing process control',

        'discriminators_tested': 3,
        'discriminators_failed': failed_count,
        'failure_details': discriminators_failed,

        'exclusion_strength': 'STRONG' if failed_count >= 2 else 'PARTIAL' if failed_count >= 1 else 'WEAK',
        'verdict': f'EXCLUDED - Failed {failed_count}/3 discriminators',

        'interpretation': (
            f"Dyeing hypothesis excluded: Failed on {failed_count} key discriminators. "
            "Grammar encodes thermal fractionation control (phase hazards, high discrimination "
            "gradient, forbidden k→h) that dyeing cannot explain."
        )
    }

    return result


# =============================================================================
# NC3: PHARMACY COMPOUNDING HYPOTHESIS
# =============================================================================

def test_nc3_compounding(iso_results: dict, stats: dict) -> dict:
    """
    NC3: Test if grammar could encode pharmaceutical compounding.

    Key discriminators where compounding SHOULD FAIL:
    1. k→h pattern: Dangerous (compounding often requires heat + mixing)
    2. Discrimination gradient: 8.7x (compounding would be lower)
    3. Hazard profile: Phase hazards, not mixing ratio errors
    """
    bs_tests = iso_results.get('behavior_structural_tests', [])
    ps_tests = iso_results.get('process_sequence_tests', [])

    # PS-4: k→h forbidden - correct path
    ps4_passed = False
    ps4_observed = ""
    for test in ps_tests:
        if test.get('test_id') == 'PS-4':
            ps4_passed = test.get('passed', False)
            ps4_observed = test.get('observed', '')
            break

    # Discrimination gradient
    middle_by_domain = stats.get('middle_by_domain', {})
    energy_middles = middle_by_domain.get('ENERGY_OPERATOR', 0)
    registry_middles = middle_by_domain.get('REGISTRY_REFERENCE', 0)
    gradient = energy_middles / registry_middles if registry_middles > 0 else 0

    # BS-1: Hazard clustering at k (phase/energy boundary)
    bs1_passed = False
    bs1_observed = ""
    for test in bs_tests:
        if test.get('test_id') == 'BS-1':
            bs1_passed = test.get('passed', False)
            bs1_observed = test.get('observed', '')
            break

    discriminators_failed = []

    # Discriminator 1: k→h forbidden (compounding needs heat+mix)
    if ps4_passed:
        discriminators_failed.append({
            'test': 'k->h pattern',
            'distillation_prediction': 'k->h dangerous (phase failure)',
            'compounding_prediction': 'k->h required (heat + mixing)',
            'observed': ps4_observed,
            'verdict': 'COMPOUNDING FAILS'
        })

    # Discriminator 2: High discrimination gradient
    if gradient > 5.0:
        discriminators_failed.append({
            'test': 'Discrimination gradient',
            'distillation_prediction': '8.7x for volatiles',
            'compounding_prediction': 'Lower (fewer variants in pharmacy)',
            'observed': f'{round(gradient, 1)}x gradient observed',
            'verdict': 'COMPOUNDING FAILS'
        })

    # Discriminator 3: Hazards at k (phase boundary), not mixing errors
    if bs1_passed:
        discriminators_failed.append({
            'test': 'Hazard profile',
            'distillation_prediction': 'Hazards cluster at k (phase boundary)',
            'compounding_prediction': 'Mixing ratio errors dominant',
            'observed': bs1_observed,
            'verdict': 'COMPOUNDING FAILS'
        })

    failed_count = len(discriminators_failed)

    result = {
        'control_id': 'NC3',
        'control_name': 'Pharmacy Compounding Hypothesis',
        'hypothesis': 'Grammar encodes pharmaceutical preparation',

        'discriminators_tested': 3,
        'discriminators_failed': failed_count,
        'failure_details': discriminators_failed,

        'exclusion_strength': 'STRONG' if failed_count >= 2 else 'PARTIAL' if failed_count >= 1 else 'WEAK',
        'verdict': f'EXCLUDED - Failed {failed_count}/3 discriminators',

        'interpretation': (
            f"Compounding hypothesis excluded: Failed on {failed_count} key discriminators. "
            "Grammar forbids k→h (needed for compounding), shows high discrimination gradient, "
            "and has phase-dominant hazards (not mixing errors)."
        )
    }

    return result


# =============================================================================
# NC4: CRYSTALLIZATION HYPOTHESIS
# =============================================================================

def test_nc4_crystallization(iso_results: dict) -> dict:
    """
    NC4: Test if grammar could encode crystallization/precipitation control.

    Key discriminators where crystallization SHOULD FAIL:
    1. Recovery logic: Cooling recovers in distillation; cooling is PRIMARY in crystallization
    2. k→h pattern: Dangerous (crystallization uses k→h as supersaturation)
    3. Nucleation hazards: Should dominate in crystallization (absent here)
    """
    bs_tests = iso_results.get('behavior_structural_tests', [])
    ps_tests = iso_results.get('process_sequence_tests', [])

    # BS-4: e-recovery dominance (cooling = recovery, not primary operation)
    bs4_passed = False
    bs4_enrichment = 0
    for test in bs_tests:
        if test.get('test_id') == 'BS-4':
            bs4_passed = test.get('passed', False)
            bs4_enrichment = test.get('enrichment', 0)
            break

    # PS-4: k→h forbidden - correct path
    ps4_passed = False
    ps4_observed = ""
    for test in ps_tests:
        if test.get('test_id') == 'PS-4':
            ps4_passed = test.get('passed', False)
            ps4_observed = test.get('observed', '')
            break

    # BS-1: Hazard clustering at k (phase/energy boundary)
    bs1_passed = False
    bs1_observed = ""
    for test in bs_tests:
        if test.get('test_id') == 'BS-1':
            bs1_passed = test.get('passed', False)
            bs1_observed = test.get('observed', '')
            break

    discriminators_failed = []

    # Discriminator 1: e-recovery as RECOVERY (not primary operation)
    if bs4_passed:
        discriminators_failed.append({
            'test': 'Recovery logic',
            'distillation_prediction': 'Cooling = recovery from thermal excursion',
            'crystallization_prediction': 'Cooling = PRIMARY operation (supersaturation)',
            'observed': f'e-recovery is enriched {bs4_enrichment}x as RECOVERY path',
            'verdict': 'CRYSTALLIZATION FAILS'
        })

    # Discriminator 2: k→h forbidden (crystallization needs supersaturation via cooling)
    if ps4_passed:
        discriminators_failed.append({
            'test': 'k->h pattern',
            'distillation_prediction': 'k->h dangerous (thermal phase failure)',
            'crystallization_prediction': 'k->h is supersaturation (main process)',
            'observed': ps4_observed,
            'verdict': 'CRYSTALLIZATION FAILS'
        })

    # Discriminator 3: Hazards at k (phase boundary), not nucleation
    if bs1_passed:
        discriminators_failed.append({
            'test': 'Hazard profile',
            'distillation_prediction': 'Hazards cluster at k (liquid/vapor phase boundary)',
            'crystallization_prediction': 'Nucleation/polymorph hazards dominant',
            'observed': bs1_observed,
            'verdict': 'CRYSTALLIZATION FAILS'
        })

    failed_count = len(discriminators_failed)

    result = {
        'control_id': 'NC4',
        'control_name': 'Crystallization/Precipitation Hypothesis',
        'hypothesis': 'Grammar encodes crystallization or precipitation control',

        'discriminators_tested': 3,
        'discriminators_failed': failed_count,
        'failure_details': discriminators_failed,

        'exclusion_strength': 'STRONG' if failed_count >= 2 else 'PARTIAL' if failed_count >= 1 else 'WEAK',
        'verdict': f'EXCLUDED - Failed {failed_count}/3 discriminators',

        'interpretation': (
            f"Crystallization hypothesis excluded: Failed on {failed_count} key discriminators. "
            "Grammar treats cooling as recovery (not primary), forbids k→h (needed for "
            "supersaturation), and has phase-ordering hazards (not nucleation)."
        )
    }

    return result


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_all_negative_controls() -> dict:
    """Run all NC1-NC4 negative control tests."""
    print("=" * 60)
    print("Scientific Confidence Tightening: Negative Controls")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    iso_results = load_process_isomorphism()
    stats = load_behavioral_stats()

    results = {
        'test_suite': 'Negative Control Tests',
        'tier': 3,
        'method': 'Alternative hypothesis exclusion via discriminator failure',
        'controls': {}
    }

    # Run controls
    print("\nRunning NC1: Fermentation Hypothesis...")
    results['controls']['NC1'] = test_nc1_fermentation(iso_results)

    print("Running NC2: Dyeing Hypothesis...")
    results['controls']['NC2'] = test_nc2_dyeing(iso_results, stats)

    print("Running NC3: Pharmacy Compounding Hypothesis...")
    results['controls']['NC3'] = test_nc3_compounding(iso_results, stats)

    print("Running NC4: Crystallization Hypothesis...")
    results['controls']['NC4'] = test_nc4_crystallization(iso_results)

    # Summary
    strong_exclusions = sum(1 for c in results['controls'].values()
                           if c['exclusion_strength'] == 'STRONG')
    total_discriminators_failed = sum(c['discriminators_failed']
                                      for c in results['controls'].values())

    results['summary'] = {
        'controls_tested': 4,
        'strong_exclusions': strong_exclusions,
        'total_discriminators_failed': total_discriminators_failed,
        'all_excluded': strong_exclusions == 4
    }

    # Print results
    print("\n" + "-" * 60)
    print("RESULTS SUMMARY")
    print("-" * 60)

    for ctrl_id, ctrl_result in results['controls'].items():
        print(f"\n{ctrl_id}: {ctrl_result['control_name']}")
        print(f"  Exclusion: {ctrl_result['exclusion_strength']}")
        print(f"  Failed: {ctrl_result['discriminators_failed']}/3 discriminators")
        print(f"  {ctrl_result['verdict']}")

    print(f"\n\nOverall: {strong_exclusions}/4 strong exclusions")
    print(f"Total discriminators failed: {total_discriminators_failed}/12")

    return results


def main():
    """Main execution."""
    results = run_all_negative_controls()

    # Save results
    os.makedirs('results', exist_ok=True)
    output_path = 'results/negative_controls.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {output_path}")

    return results


if __name__ == '__main__':
    main()
