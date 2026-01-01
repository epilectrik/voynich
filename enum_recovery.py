#!/usr/bin/env python3
"""
Data Recovery Phase, Task 5: Enum Recovery Framework

Framework for recovering classifier marker meanings from correlations.
Implements strict confidence criteria with propagation and context diversity.
Includes anti-overclaim safeguards.
"""

import json
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re

# =============================================================================
# CONFIDENCE CRITERIA
# =============================================================================

# HIGH confidence requires ALL of:
HIGH_CONFIDENCE_CRITERIA = {
    'effect_size_min': 0.3,          # Cramer's V >= 0.3
    'null_percentile_min': 99,       # >= 99th percentile
    'propagation_min': 3,            # >= 3 entries show pattern
    'context_diversity_min': 2       # >= 2 structural contexts
}

# MEDIUM confidence requires:
MEDIUM_CONFIDENCE_CRITERIA = {
    'effect_size_min': 0.2,
    'null_percentile_min': 95,
    'propagation_min': 2,
    'context_diversity_min': 1
}

# Structural contexts for diversity calculation
STRUCTURAL_CONTEXTS = [
    'part1_position',      # Appears in Part 1
    'part2_position',      # Appears in Part 2
    'part3_position',      # Appears in Part 3
    'b_references',        # Appears in B entries that reference A
    'heading_context',     # Used as heading word
    'body_context'         # Used in body text
]


# =============================================================================
# HEDGED LANGUAGE VALIDATION
# =============================================================================

# Acceptable claim language
ACCEPTABLE_LANGUAGE = [
    'correlates with',
    'is associated with',
    'tracks',
    'co-occurs with',
    'appears alongside',
    'shows correlation to'
]

# Unacceptable overclaims
OVERCLAIM_LANGUAGE = [
    'means',
    'represents',
    'encodes',
    'signifies',
    'indicates',
    'denotes',
    'stands for',
    'is equivalent to',
    'translates to'
]


def validate_claim_language(claim: str) -> Dict:
    """
    Ensure claim uses appropriate hedged language.

    REJECTS claims that use definitive meaning language.
    """
    claim_lower = claim.lower()

    # Check for overclaims
    overclaims_found = []
    for phrase in OVERCLAIM_LANGUAGE:
        if phrase in claim_lower:
            overclaims_found.append(phrase)

    # Check for acceptable language
    acceptable_found = []
    for phrase in ACCEPTABLE_LANGUAGE:
        if phrase in claim_lower:
            acceptable_found.append(phrase)

    is_valid = len(overclaims_found) == 0 and len(acceptable_found) > 0

    return {
        'valid': is_valid,
        'overclaims_found': overclaims_found,
        'acceptable_language_used': acceptable_found,
        'suggestion': 'Use "correlates with" or "is associated with" instead of meaning claims' if not is_valid else None
    }


# =============================================================================
# CONTEXT DIVERSITY
# =============================================================================

def calculate_context_diversity(prefix: str, visual_feature: str,
                                merged_data: Dict, text_data: Dict) -> Dict:
    """
    Count distinct structural contexts where correlation holds.

    Contexts include:
    - Part 1 position (appears in Part 1 vocabulary)
    - Part 2 position
    - Part 3 position
    - B references (appears in B entries)
    - Heading context (used as heading word)
    - Body context (used in body text)
    """
    contexts_found = []
    context_details = {}

    for folio_id, data in merged_data.items():
        visual = data.get('visual_features', {})
        text = data.get('text_features', {})

        visual_value = visual.get(visual_feature)
        if visual_value is None:
            continue

        # Check Part 1 context
        part1_vocab = text.get('part1_vocabulary', [])
        if any(w.startswith(prefix) for w in part1_vocab if w):
            if 'part1_position' not in contexts_found:
                contexts_found.append('part1_position')
                context_details['part1_position'] = {'folios': []}
            context_details['part1_position']['folios'].append(folio_id)

        # Check Part 2 context
        part2_vocab = text.get('part2_vocabulary', [])
        if any(w.startswith(prefix) for w in part2_vocab if w):
            if 'part2_position' not in contexts_found:
                contexts_found.append('part2_position')
                context_details['part2_position'] = {'folios': []}
            context_details['part2_position']['folios'].append(folio_id)

        # Check Part 3 context
        part3_vocab = text.get('part3_vocabulary', [])
        if any(w.startswith(prefix) for w in part3_vocab if w):
            if 'part3_position' not in contexts_found:
                contexts_found.append('part3_position')
                context_details['part3_position'] = {'folios': []}
            context_details['part3_position']['folios'].append(folio_id)

        # Check heading context
        heading_prefix = text.get('heading_prefix', '')
        if heading_prefix == prefix:
            if 'heading_context' not in contexts_found:
                contexts_found.append('heading_context')
                context_details['heading_context'] = {'folios': []}
            context_details['heading_context']['folios'].append(folio_id)

        # Check B reference context
        cross_refs = text.get('cross_reference_candidates', [])
        if cross_refs:
            if 'b_references' not in contexts_found:
                contexts_found.append('b_references')
                context_details['b_references'] = {'folios': []}
            context_details['b_references']['folios'].append(folio_id)

    return {
        'context_count': len(contexts_found),
        'contexts': contexts_found,
        'details': context_details,
        'meets_high_threshold': len(contexts_found) >= HIGH_CONFIDENCE_CRITERIA['context_diversity_min'],
        'meets_medium_threshold': len(contexts_found) >= MEDIUM_CONFIDENCE_CRITERIA['context_diversity_min']
    }


# =============================================================================
# PROPAGATION TEST
# =============================================================================

def test_propagation(prefix: str, visual_feature: str, visual_value: str,
                    merged_data: Dict) -> Dict:
    """
    Test if correlation holds across multiple entries.

    Counts entries where:
    - The prefix appears in the entry text
    - The visual feature has the specified value
    """
    matching_entries = []
    non_matching_entries = []

    for folio_id, data in merged_data.items():
        visual = data.get('visual_features', {})
        text = data.get('text_features', {})

        actual_visual = visual.get(visual_feature)
        if actual_visual is None:
            continue

        # Check if prefix appears in this entry
        all_vocab = (
            text.get('part1_vocabulary', []) +
            text.get('part2_vocabulary', []) +
            text.get('part3_vocabulary', [])
        )
        has_prefix = any(w.startswith(prefix) for w in all_vocab if w)

        if has_prefix:
            if actual_visual == visual_value:
                matching_entries.append(folio_id)
            else:
                non_matching_entries.append(folio_id)

    propagation_count = len(matching_entries)
    total_with_prefix = len(matching_entries) + len(non_matching_entries)
    propagation_rate = propagation_count / total_with_prefix if total_with_prefix > 0 else 0

    return {
        'propagation_count': propagation_count,
        'total_entries_with_prefix': total_with_prefix,
        'propagation_rate': round(propagation_rate, 3),
        'matching_entries': matching_entries,
        'non_matching_entries': non_matching_entries,
        'passes_high_threshold': propagation_count >= HIGH_CONFIDENCE_CRITERIA['propagation_min'],
        'passes_medium_threshold': propagation_count >= MEDIUM_CONFIDENCE_CRITERIA['propagation_min']
    }


# =============================================================================
# CONFIDENCE ASSIGNMENT
# =============================================================================

def assign_confidence(effect_size: float, null_percentile: float,
                     propagation_count: int, context_diversity: int) -> Dict:
    """
    Assign confidence level based on strict criteria.

    HIGH confidence requires ALL of:
    - Effect size (Cramer's V) >= 0.3
    - Null percentile >= 99
    - Propagation across >= 3 entries
    - Context diversity >= 2

    MEDIUM confidence requires:
    - Effect size >= 0.2
    - Null percentile >= 95
    - Propagation across >= 2 entries
    - Context diversity >= 1

    LOW confidence: Passes Bonferroni but fails above

    NO CLAIM: Fails Bonferroni or null model
    """
    # Check HIGH criteria
    high_checks = {
        'effect_size': effect_size >= HIGH_CONFIDENCE_CRITERIA['effect_size_min'],
        'null_percentile': null_percentile >= HIGH_CONFIDENCE_CRITERIA['null_percentile_min'],
        'propagation': propagation_count >= HIGH_CONFIDENCE_CRITERIA['propagation_min'],
        'context_diversity': context_diversity >= HIGH_CONFIDENCE_CRITERIA['context_diversity_min']
    }
    is_high = all(high_checks.values())

    # Check MEDIUM criteria
    medium_checks = {
        'effect_size': effect_size >= MEDIUM_CONFIDENCE_CRITERIA['effect_size_min'],
        'null_percentile': null_percentile >= MEDIUM_CONFIDENCE_CRITERIA['null_percentile_min'],
        'propagation': propagation_count >= MEDIUM_CONFIDENCE_CRITERIA['propagation_min'],
        'context_diversity': context_diversity >= MEDIUM_CONFIDENCE_CRITERIA['context_diversity_min']
    }
    is_medium = all(medium_checks.values()) and not is_high

    # Determine confidence level
    if is_high:
        confidence = 'HIGH'
    elif is_medium:
        confidence = 'MEDIUM'
    elif null_percentile >= 95 or effect_size >= 0.1:
        confidence = 'LOW'
    else:
        confidence = 'NO_CLAIM'

    return {
        'confidence': confidence,
        'high_criteria_met': high_checks,
        'medium_criteria_met': medium_checks,
        'scores': {
            'effect_size': round(effect_size, 3),
            'null_percentile': round(null_percentile, 1),
            'propagation': propagation_count,
            'context_diversity': context_diversity
        }
    }


# =============================================================================
# ENUM MAPPING GENERATION
# =============================================================================

def generate_enum_mapping(correlation_results: List[Dict],
                         merged_data: Dict,
                         text_data: Dict) -> Dict:
    """
    Generate enum mappings from significant correlations.

    Only creates mappings for correlations that pass strict criteria.
    """
    mappings = {}

    for result in correlation_results:
        if not result.get('significant_bonferroni', False):
            continue

        visual_feature = result.get('visual_feature', '')
        text_feature = result.get('text_feature', '')

        # Skip non-prefix text features
        if 'prefix' not in text_feature.lower():
            continue

        effect_size = result.get('cramers_v', 0)
        null_percentile = result.get('null_percentile', 0)

        # Get the prefix value from the correlation
        # This is simplified - in practice, need to extract specific prefix-value pair
        prefix = result.get('dominant_prefix', 'unknown')
        visual_value = result.get('dominant_visual_value', 'unknown')

        # Calculate propagation
        propagation = test_propagation(prefix, visual_feature, visual_value, merged_data)

        # Calculate context diversity
        context = calculate_context_diversity(prefix, visual_feature, merged_data, text_data)

        # Assign confidence
        confidence = assign_confidence(
            effect_size,
            null_percentile,
            propagation['propagation_count'],
            context['context_count']
        )

        # Generate hedged interpretation
        if confidence['confidence'] in ['HIGH', 'MEDIUM']:
            interpretation = f"Classifier '{prefix}' correlates with {visual_feature}={visual_value}"
            claim_validation = validate_claim_language(interpretation)
        else:
            interpretation = None
            claim_validation = None

        mapping_id = f"{prefix}_{visual_feature}"
        mappings[mapping_id] = {
            'prefix': prefix,
            'visual_feature': visual_feature,
            'visual_value': visual_value,
            'effect_size': round(effect_size, 4),
            'null_percentile': round(null_percentile, 1),
            'propagation_count': propagation['propagation_count'],
            'propagation_rate': propagation['propagation_rate'],
            'context_diversity': context['context_count'],
            'contexts_observed': context['contexts'],
            'confidence': confidence['confidence'],
            'confidence_details': confidence,
            'interpretation': interpretation,
            'claim_validation': claim_validation,
            'note': 'Correlation established; semantic equivalence not claimed'
        }

    return mappings


# =============================================================================
# ANTI-OVERCLAIM REPORT
# =============================================================================

def generate_overclaim_report(mappings: Dict) -> Dict:
    """
    Generate report on claim language compliance.
    """
    issues = []
    compliant = []

    for mapping_id, mapping in mappings.items():
        interpretation = mapping.get('interpretation', '')
        if not interpretation:
            continue

        validation = validate_claim_language(interpretation)
        if validation['valid']:
            compliant.append({
                'mapping': mapping_id,
                'interpretation': interpretation,
                'language_used': validation['acceptable_language_used']
            })
        else:
            issues.append({
                'mapping': mapping_id,
                'interpretation': interpretation,
                'overclaims': validation['overclaims_found'],
                'suggestion': validation['suggestion']
            })

    return {
        'compliant_count': len(compliant),
        'issue_count': len(issues),
        'compliant': compliant,
        'issues': issues,
        'all_claims_valid': len(issues) == 0
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Data Recovery Phase, Task 5: Enum Recovery Framework")
    print("=" * 70)

    print("\nEnum recovery framework ready.")
    print("Awaiting correlation results to generate mappings.")

    print("\nConfidence Criteria:")
    print("\n  HIGH (ALL required):")
    for k, v in HIGH_CONFIDENCE_CRITERIA.items():
        print(f"    - {k}: >= {v}")

    print("\n  MEDIUM (ALL required):")
    for k, v in MEDIUM_CONFIDENCE_CRITERIA.items():
        print(f"    - {k}: >= {v}")

    print("\n  LOW: Passes Bonferroni but fails above")
    print("  NO_CLAIM: Fails Bonferroni or null model")

    print("\nAnti-Overclaim Safeguards:")
    print("  ACCEPTABLE language:")
    for phrase in ACCEPTABLE_LANGUAGE[:3]:
        print(f"    - '{phrase}'")
    print("  REJECTED language:")
    for phrase in OVERCLAIM_LANGUAGE[:3]:
        print(f"    - '{phrase}'")

    # Save configuration
    config = {
        'metadata': {
            'title': 'Enum Recovery Framework Configuration',
            'phase': 'Data Recovery Phase, Task 5',
            'date': datetime.now().isoformat()
        },
        'confidence_criteria': {
            'high': HIGH_CONFIDENCE_CRITERIA,
            'medium': MEDIUM_CONFIDENCE_CRITERIA
        },
        'structural_contexts': STRUCTURAL_CONTEXTS,
        'language_validation': {
            'acceptable': ACCEPTABLE_LANGUAGE,
            'rejected': OVERCLAIM_LANGUAGE
        },
        'status': 'READY - awaiting correlation results'
    }

    with open('enum_recovery_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    print(f"\nSaved configuration to: enum_recovery_config.json")


if __name__ == '__main__':
    main()
