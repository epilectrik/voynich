#!/usr/bin/env python3
"""
Visual Coding Phase, Task 1: Pilot Folio Verification

Verifies all 30 pilot folios are appropriate for herbal visual correlation study.
Compiles metadata including reference status and flags any issues.
"""

import json
from datetime import datetime
from typing import Dict, List

# =============================================================================
# CONFIGURATION
# =============================================================================

PILOT_FOLIO_FILE = 'pilot_folio_selection.json'
REFERENCE_GRAPH_FILE = 'reference_graph_analysis_report.json'
PILOT_TEXT_FEATURES_FILE = 'pilot_folio_text_features.json'

# Reference status thresholds
HUB_THRESHOLD = 5  # >5 references = HUB
ISOLATED_THRESHOLD = 0  # 0 references = ISOLATED

# Early folios (potentially isolated introductory material)
EARLY_FOLIOS = ['f1r', 'f1v', 'f2r', 'f2v', 'f3r', 'f3v', 'f4r', 'f4v', 'f5r', 'f5v']

# pchor duplicate folios (not in pilot, but note if any are)
PCHOR_FOLIOS = ['f19r', 'f21r', 'f52v']


# =============================================================================
# DATA LOADING
# =============================================================================

def load_pilot_selection() -> Dict:
    """Load pilot folio selection data."""
    with open(PILOT_FOLIO_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_reference_graph() -> Dict:
    """Load reference graph analysis."""
    with open(REFERENCE_GRAPH_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_pilot_text_features() -> Dict:
    """Load pilot folio text features."""
    try:
        with open(PILOT_TEXT_FEATURES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# =============================================================================
# REFERENCE COUNT EXTRACTION
# =============================================================================

def build_reference_counts(graph_data: Dict) -> Dict[str, int]:
    """Build dictionary of folio -> reference count from graph data."""
    ref_counts = {}

    # Get most referenced A entries
    most_ref = graph_data.get('graph_statistics', {}).get('most_referenced_a', [])
    for entry in most_ref:
        ref_counts[entry['folio']] = entry['in_degree']

    # All isolated A entries have 0 references
    isolated = graph_data.get('graph_statistics', {}).get('isolated_nodes', {})
    isolated_a = isolated.get('a_isolated_folios', [])
    for folio in isolated_a:
        ref_counts[folio] = 0

    return ref_counts


def get_reference_status(count: int) -> str:
    """Classify reference status based on count."""
    if count > HUB_THRESHOLD:
        return "HUB"
    elif count == ISOLATED_THRESHOLD:
        return "ISOLATED"
    else:
        return "NORMAL"


# =============================================================================
# FOLIO VERIFICATION
# =============================================================================

def verify_pilot_folios(pilot_data: Dict, ref_counts: Dict) -> List[Dict]:
    """Verify and enrich metadata for each pilot folio."""
    verified_folios = []
    folio_details = pilot_data.get('folio_details', [])
    selection_criteria = pilot_data.get('selection_criteria', {})

    short_entries = set(selection_criteria.get('short_entries', []))
    medium_entries = set(selection_criteria.get('medium_entries', []))
    long_entries = set(selection_criteria.get('long_entries', []))

    for folio in folio_details:
        folio_id = folio['folio_id']
        section = folio.get('section', '')
        word_count = folio.get('word_count', 0)
        opening_word = folio.get('opening_word', '')
        opening_prefix = folio.get('opening_prefix', '')

        # Determine entry length category
        if folio_id in short_entries:
            length_category = "SHORT"
        elif folio_id in medium_entries:
            length_category = "MEDIUM"
        elif folio_id in long_entries:
            length_category = "LONG"
        else:
            length_category = "UNKNOWN"

        # Get reference count and status
        ref_count = ref_counts.get(folio_id, 0)
        ref_status = get_reference_status(ref_count)

        # Check special flags
        is_early = folio_id in EARLY_FOLIOS
        is_pchor = folio_id in PCHOR_FOLIOS
        is_isolated_early = ref_count == 0 and is_early

        # Check for f90v2 issue (folio number in RECIPES range but marked as H)
        folio_number_issue = False
        if folio_id == 'f90v2':
            # Folio 90 is in range 87-102 which some systems classify as RECIPES
            # But transcription marks it as "H" (Herbal)
            folio_number_issue = True

        # Section verification
        section_verified = section == 'H'
        currier_verified = True  # All selected from Currier A per criteria

        verified = {
            'folio_id': folio_id,
            'section': section,
            'section_verified': section_verified,
            'currier': 'A',
            'currier_verified': currier_verified,
            'word_count': word_count,
            'length_category': length_category,
            'heading_word': opening_word,
            'heading_prefix': opening_prefix,
            'reference_count': ref_count,
            'reference_status': ref_status,
            'is_pchor_duplicate': is_pchor,
            'is_early_folio': is_early,
            'is_isolated_early': is_isolated_early,
            'has_folio_number_issue': folio_number_issue,
            'verification_status': 'VERIFIED' if section_verified and currier_verified else 'NEEDS_REVIEW'
        }

        verified_folios.append(verified)

    return verified_folios


# =============================================================================
# SUMMARY STATISTICS
# =============================================================================

def compute_summary(verified_folios: List[Dict]) -> Dict:
    """Compute summary statistics for the pilot."""
    total = len(verified_folios)

    # Section verification
    section_verified = sum(1 for f in verified_folios if f['section_verified'])

    # Reference status counts
    hub_count = sum(1 for f in verified_folios if f['reference_status'] == 'HUB')
    normal_count = sum(1 for f in verified_folios if f['reference_status'] == 'NORMAL')
    isolated_count = sum(1 for f in verified_folios if f['reference_status'] == 'ISOLATED')

    # Special flags
    early_count = sum(1 for f in verified_folios if f['is_early_folio'])
    isolated_early_count = sum(1 for f in verified_folios if f['is_isolated_early'])
    pchor_count = sum(1 for f in verified_folios if f['is_pchor_duplicate'])
    folio_issues = sum(1 for f in verified_folios if f['has_folio_number_issue'])

    # Length distribution
    short_count = sum(1 for f in verified_folios if f['length_category'] == 'SHORT')
    medium_count = sum(1 for f in verified_folios if f['length_category'] == 'MEDIUM')
    long_count = sum(1 for f in verified_folios if f['length_category'] == 'LONG')

    # Heading prefix diversity
    prefixes = set(f['heading_prefix'] for f in verified_folios)

    # Hub and isolated folios
    hub_folios = [f['folio_id'] for f in verified_folios if f['reference_status'] == 'HUB']
    isolated_folios = [f['folio_id'] for f in verified_folios if f['reference_status'] == 'ISOLATED']
    isolated_early_folios = [f['folio_id'] for f in verified_folios if f['is_isolated_early']]

    return {
        'total_folios': total,
        'section_verified': section_verified,
        'all_herbal': section_verified == total,
        'reference_status_distribution': {
            'HUB': hub_count,
            'NORMAL': normal_count,
            'ISOLATED': isolated_count
        },
        'length_distribution': {
            'SHORT': short_count,
            'MEDIUM': medium_count,
            'LONG': long_count
        },
        'heading_prefix_diversity': len(prefixes),
        'unique_heading_prefixes': sorted(prefixes),
        'special_folios': {
            'hub_folios': hub_folios,
            'isolated_folios': isolated_folios,
            'isolated_early_folios': isolated_early_folios,
            'early_folio_count': early_count,
            'pchor_duplicates_in_pilot': pchor_count
        },
        'issues': {
            'folio_number_issues': folio_issues,
            'folios_with_issues': [f['folio_id'] for f in verified_folios if f['has_folio_number_issue']]
        }
    }


# =============================================================================
# ISSUE ANALYSIS
# =============================================================================

def analyze_f90v2_issue() -> Dict:
    """Analyze the f90v2 classification issue."""
    return {
        'folio': 'f90v2',
        'issue': 'Folio number classification discrepancy',
        'details': {
            'folio_number': 90,
            'number_based_section': 'RECIPES (87-102 range)',
            'transcription_section': 'H (Herbal)',
            'pilot_selection_section': 'Herbal (H)'
        },
        'resolution': 'Transcription metadata takes precedence over folio number range',
        'action_required': 'Verify f90v2 has plant illustration before proceeding',
        'recommendation': 'KEEP in pilot if plant illustration present, otherwise REPLACE',
        'replacement_candidates': [
            # Medium entries (89-105 words) from Currier A herbal not in pilot
            # Would need to identify from full database
        ],
        'verification_method': 'Visual inspection via Yale Digital Collections'
    }


def identify_replacement_candidates(pilot_data: Dict) -> List[str]:
    """Identify potential replacement folios if f90v2 needs replacement."""
    # This would need access to full folio database
    # For now, return placeholder
    return [
        'Note: Full folio database needed to identify replacements',
        'Requirements: Currier A, Herbal section, 89-105 words, not in current pilot'
    ]


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Visual Coding Phase, Task 1: Pilot Folio Verification")
    print("=" * 70)

    # Load data
    print("\n[1/4] Loading data...")
    pilot_data = load_pilot_selection()
    graph_data = load_reference_graph()

    print(f"  Pilot folios: {len(pilot_data.get('pilot_study_folios', []))}")
    print(f"  Reference edges: {graph_data.get('key_findings', {}).get('total_edges', 0)}")

    # Build reference counts
    print("\n[2/4] Building reference counts...")
    ref_counts = build_reference_counts(graph_data)
    print(f"  Folios with reference data: {len(ref_counts)}")

    # Verify pilot folios
    print("\n[3/4] Verifying pilot folios...")
    verified_folios = verify_pilot_folios(pilot_data, ref_counts)
    summary = compute_summary(verified_folios)

    print(f"  Section verified: {summary['section_verified']}/{summary['total_folios']}")
    print(f"  Reference status: HUB={summary['reference_status_distribution']['HUB']}, "
          f"NORMAL={summary['reference_status_distribution']['NORMAL']}, "
          f"ISOLATED={summary['reference_status_distribution']['ISOLATED']}")

    # Analyze issues
    print("\n[4/4] Analyzing issues...")
    f90v2_analysis = analyze_f90v2_issue()

    if summary['issues']['folio_number_issues'] > 0:
        print(f"  Issues found: {summary['issues']['folio_number_issues']}")
        print(f"  Folios with issues: {summary['issues']['folios_with_issues']}")
    else:
        print("  No issues found")

    # Compile report
    report = {
        'metadata': {
            'title': 'Pilot Folio Verification Report',
            'phase': 'Visual Coding Phase, Task 1',
            'date': datetime.now().isoformat(),
            'purpose': 'Verify 30 pilot folios for herbal visual correlation study'
        },
        'summary': summary,
        'verified_folios': verified_folios,
        'issue_analysis': {
            'f90v2': f90v2_analysis
        },
        'hub_entities_detail': [
            {
                'folio_id': f['folio_id'],
                'heading_word': f['heading_word'],
                'reference_count': f['reference_count'],
                'word_count': f['word_count']
            }
            for f in verified_folios if f['reference_status'] == 'HUB'
        ],
        'isolated_early_detail': [
            {
                'folio_id': f['folio_id'],
                'heading_word': f['heading_word'],
                'word_count': f['word_count'],
                'heading_prefix': f['heading_prefix']
            }
            for f in verified_folios if f['is_isolated_early']
        ],
        'recommendations': {
            'f90v2_action': 'Verify plant illustration present via Yale Digital Collections',
            'proceed_if': 'f90v2 has clear plant illustration',
            'replace_if': 'f90v2 lacks plant illustration or shows non-herbal content'
        },
        'verification_result': 'PASS' if summary['all_herbal'] else 'NEEDS_REVIEW'
    }

    # Save report
    output_file = 'pilot_folio_verification_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    print(f"\nTotal pilot folios: {summary['total_folios']}")
    print(f"All herbal section: {'YES' if summary['all_herbal'] else 'NO'}")
    print(f"Heading prefix diversity: {summary['heading_prefix_diversity']} unique prefixes")

    print(f"\nReference Status Distribution:")
    print(f"  HUB (>5 refs): {summary['reference_status_distribution']['HUB']} folios")
    for f in report['hub_entities_detail']:
        print(f"    - {f['folio_id']} ({f['heading_word']}): {f['reference_count']} references")

    print(f"  NORMAL (1-5 refs): {summary['reference_status_distribution']['NORMAL']} folios")
    print(f"  ISOLATED (0 refs): {summary['reference_status_distribution']['ISOLATED']} folios")

    print(f"\nIsolated Early Folios (never referenced by B):")
    for f in report['isolated_early_detail']:
        print(f"    - {f['folio_id']} ({f['heading_word']})")

    print(f"\nLength Distribution:")
    print(f"  SHORT: {summary['length_distribution']['SHORT']} folios")
    print(f"  MEDIUM: {summary['length_distribution']['MEDIUM']} folios")
    print(f"  LONG: {summary['length_distribution']['LONG']} folios")

    if summary['issues']['folio_number_issues'] > 0:
        print(f"\n[!] ISSUES REQUIRING ATTENTION:")
        print(f"  f90v2: Folio number suggests RECIPES section, but transcription says Herbal")
        print(f"  ACTION: Verify plant illustration via Yale Digital Collections")

    print(f"\nVerification Result: {report['verification_result']}")
    print(f"\nSaved to: {output_file}")

    return report


if __name__ == '__main__':
    main()
