#!/usr/bin/env python3
"""
Visual Coding Phase, Task 7: Coding Checklist Generator

Generates printable coding checklist and recommended coding order for
systematic visual feature coding of 30 pilot folios.
"""

import json
from datetime import datetime
from typing import Dict, List

# =============================================================================
# CONFIGURATION
# =============================================================================

PILOT_SELECTION_FILE = 'pilot_folio_selection.json'
TEXT_FEATURES_FILE = 'pilot_folio_text_features.json'
VERIFICATION_FILE = 'pilot_folio_verification_report.json'
VISUAL_SCHEMA_FILE = 'visual_feature_schema.json'

# Coding order priorities
CALIBRATION_FOLIOS = ['f38r', 'f9v', 'f56r', 'f3v', 'f42r']
HUB_FOLIOS = ['f42r', 'f10v']
ISOLATED_EARLY_FOLIOS = ['f2r', 'f3v', 'f4v', 'f5r', 'f5v']

# Hypothesis-relevant folios
PO_PREFIX_FOLIOS = ['f11v', 'f51v', 'f23v']  # H1: po -> root
KO_PREFIX_FOLIOS = ['f5v', 'f45v', 'f3v', 'f29v']  # H4: ko -> leaf


# =============================================================================
# DATA LOADING
# =============================================================================

def load_json_file(filepath: str) -> Dict:
    """Load JSON file with error handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_all_data() -> Dict:
    """Load all required data files."""
    return {
        'selection': load_json_file(PILOT_SELECTION_FILE),
        'text_features': load_json_file(TEXT_FEATURES_FILE).get('pilot_folios', {}),
        'verification': load_json_file(VERIFICATION_FILE),
        'visual_schema': load_json_file(VISUAL_SCHEMA_FILE)
    }


# =============================================================================
# CODING ORDER GENERATION
# =============================================================================

def generate_coding_order(data: Dict) -> List[Dict]:
    """Generate recommended coding order with rationale."""
    text_features = data['text_features']
    verification = data.get('verification', {})
    folio_info = verification.get('folio_verification', {})

    all_folios = list(text_features.keys())
    ordered = []
    seen = set()

    def add_folio(folio_id: str, reason: str, priority: str):
        if folio_id not in seen and folio_id in all_folios:
            seen.add(folio_id)
            tf = text_features.get(folio_id, {})
            fi = folio_info.get(folio_id, {})
            ordered.append({
                'order': len(ordered) + 1,
                'folio_id': folio_id,
                'reason': reason,
                'priority': priority,
                'word_count': tf.get('word_count', 0),
                'heading': tf.get('heading_word', ''),
                'heading_prefix': tf.get('heading_prefix', ''),
                'reference_status': fi.get('reference_status', 'UNKNOWN')
            })

    # Phase 1: Calibration set (for inter-coder reliability)
    for folio_id in CALIBRATION_FOLIOS:
        add_folio(folio_id, 'CALIBRATION: Inter-coder reliability set', 'HIGH')

    # Phase 2: Hub entities (most referenced)
    for folio_id in HUB_FOLIOS:
        add_folio(folio_id, 'HUB: Most-referenced A entries', 'HIGH')

    # Phase 3: Hypothesis-critical folios
    for folio_id in PO_PREFIX_FOLIOS:
        add_folio(folio_id, 'HYPOTHESIS H1: po prefix (root features)', 'HIGH')

    for folio_id in KO_PREFIX_FOLIOS:
        add_folio(folio_id, 'HYPOTHESIS H4: ko prefix (leaf features)', 'HIGH')

    # Phase 4: Isolated early folios (structural comparison)
    for folio_id in ISOLATED_EARLY_FOLIOS:
        add_folio(folio_id, 'STRUCTURAL S2: Isolated early folio', 'MEDIUM')

    # Phase 5: Short entries (simpler illustrations, build consistency)
    selection = data['selection']
    short_entries = selection.get('selection_criteria', {}).get('short_entries', [])
    for folio_id in short_entries:
        add_folio(folio_id, 'SHORT: Simple illustration baseline', 'MEDIUM')

    # Phase 6: Medium entries
    medium_entries = selection.get('selection_criteria', {}).get('medium_entries', [])
    for folio_id in medium_entries:
        add_folio(folio_id, 'MEDIUM: Moderate complexity', 'MEDIUM')

    # Phase 7: Long entries (most complex, code last)
    long_entries = selection.get('selection_criteria', {}).get('long_entries', [])
    for folio_id in long_entries:
        add_folio(folio_id, 'LONG: Complex illustration', 'LOW')

    # Any remaining folios
    for folio_id in all_folios:
        add_folio(folio_id, 'REMAINING: Standard entry', 'LOW')

    return ordered


# =============================================================================
# MARKDOWN CHECKLIST GENERATION
# =============================================================================

def generate_markdown_checklist(coding_order: List[Dict], data: Dict) -> str:
    """Generate printable markdown checklist."""
    lines = []

    # Header
    lines.append("# Visual Coding Checklist")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Total Folios:** {len(coding_order)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Instructions
    lines.append("## Instructions")
    lines.append("")
    lines.append("1. Code folios in the order listed below")
    lines.append("2. For each folio, record all visual features")
    lines.append("3. Use UNDETERMINED only when damage/abstraction prevents coding")
    lines.append("4. Mark checkbox when complete")
    lines.append("5. Note any special observations in the Notes field")
    lines.append("")
    lines.append("**Quality Control:**")
    lines.append("- Code CALIBRATION folios (f38r, f9v, f56r, f3v, f42r) for reliability check")
    lines.append("- At session end, re-code f38r and f42r without looking at original")
    lines.append("- Target: >80% agreement on re-coded folios")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Feature quick reference
    lines.append("## Feature Quick Reference")
    lines.append("")
    lines.append("**Root Types:** NONE | SINGLE | BRANCHING | BULBOUS | TUBEROUS | FIBROUS")
    lines.append("")
    lines.append("**Leaf Shapes:** OVATE | LANCEOLATE | COMPOUND | LOBED | SERRATED | PALMATE | PINNATE | ROUND | LINEAR")
    lines.append("")
    lines.append("**Flower Shapes:** SIMPLE | RADIAL | BILATERAL | COMPOSITE | TUBULAR | BELL")
    lines.append("")
    lines.append("**Complexity:** SIMPLE (<5 elements) | MODERATE (5-15) | COMPLEX (>15)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Group folios by phase
    phases = {
        'HIGH': {'title': 'Phase 1: HIGH PRIORITY (Code First)', 'folios': []},
        'MEDIUM': {'title': 'Phase 2: MEDIUM PRIORITY', 'folios': []},
        'LOW': {'title': 'Phase 3: REMAINING', 'folios': []}
    }

    for item in coding_order:
        phases[item['priority']]['folios'].append(item)

    # Generate each phase
    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        phase = phases[priority]
        if not phase['folios']:
            continue

        lines.append(f"## {phase['title']}")
        lines.append("")

        for item in phase['folios']:
            folio_id = item['folio_id']
            heading = item['heading'] or '(no heading)'
            prefix = item['heading_prefix'] or '??'
            wc = item['word_count']
            reason = item['reason']
            ref_status = item['reference_status']

            # Checklist item
            lines.append(f"### [ ] {folio_id}")
            lines.append("")
            lines.append(f"**{reason}**")
            lines.append("")
            lines.append(f"- Heading: `{heading}` (prefix: {prefix})")
            lines.append(f"- Words: {wc} | Status: {ref_status}")
            lines.append("")

            # Feature coding fields
            lines.append("| Feature | Value | Notes |")
            lines.append("|---------|-------|-------|")
            lines.append("| **ROOT** | | |")
            lines.append("| root_present | [ ] YES [ ] NO | |")
            lines.append("| root_type | ______________ | |")
            lines.append("| root_prominence | [ ] SMALL [ ] MEDIUM [ ] LARGE | |")
            lines.append("| **STEM** | | |")
            lines.append("| stem_visible | [ ] YES [ ] NO | |")
            lines.append("| stem_type | [ ] SINGLE [ ] BRANCHED [ ] MULTIPLE | |")
            lines.append("| **LEAF** | | |")
            lines.append("| leaf_present | [ ] YES [ ] NO | |")
            lines.append("| leaf_shape | ______________ | |")
            lines.append("| leaf_arrangement | [ ] ALT [ ] OPP [ ] WHORL [ ] BASAL | |")
            lines.append("| leaf_count | [ ] FEW [ ] MODERATE [ ] MANY | |")
            lines.append("| **FLOWER** | | |")
            lines.append("| flower_present | [ ] YES [ ] NO | |")
            lines.append("| flower_shape | ______________ | |")
            lines.append("| flower_position | [ ] TERMINAL [ ] AXILLARY [ ] BOTH | |")
            lines.append("| **OVERALL** | | |")
            lines.append("| complexity | [ ] SIMPLE [ ] MODERATE [ ] COMPLEX | |")
            lines.append("| symmetry | [ ] SYM [ ] ASYM [ ] PARTIAL | |")
            lines.append("")
            lines.append("**Observations:** _______________________________________")
            lines.append("")
            lines.append("---")
            lines.append("")

    # Quality control section
    lines.append("## Quality Control Verification")
    lines.append("")
    lines.append("### Intra-Coder Reliability Check")
    lines.append("")
    lines.append("Re-code these folios at end of session (without looking at originals):")
    lines.append("")
    lines.append("| Folio | Original | Re-code | Agreement |")
    lines.append("|-------|----------|---------|-----------|")
    lines.append("| f38r (simplest) | ______ | ______ | ____% |")
    lines.append("| f42r (hub) | ______ | ______ | ____% |")
    lines.append("")
    lines.append("**Target:** >80% agreement")
    lines.append("")
    lines.append("### Session Notes")
    lines.append("")
    lines.append("Date: ______________")
    lines.append("")
    lines.append("Coder: ______________")
    lines.append("")
    lines.append("Folios completed: ____ / 30")
    lines.append("")
    lines.append("Issues encountered: _______________________________________")
    lines.append("")

    return '\n'.join(lines)


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Visual Coding Phase, Task 7: Coding Checklist Generator")
    print("=" * 70)

    # Load data
    print("\n[1/3] Loading data...")
    data = load_all_data()

    if not data['text_features']:
        print("  ERROR: Could not load text features")
        return None

    print(f"  Loaded {len(data['text_features'])} folio text features")

    # Generate coding order
    print("\n[2/3] Generating coding order...")
    coding_order = generate_coding_order(data)
    print(f"  Generated order for {len(coding_order)} folios")

    # Count by priority
    priority_counts = {}
    for item in coding_order:
        p = item['priority']
        priority_counts[p] = priority_counts.get(p, 0) + 1

    for p, c in sorted(priority_counts.items()):
        print(f"    {p}: {c} folios")

    # Generate markdown checklist
    print("\n[3/3] Generating checklist files...")

    checklist_md = generate_markdown_checklist(coding_order, data)

    # Save files
    with open('coding_checklist.md', 'w', encoding='utf-8') as f:
        f.write(checklist_md)
    print("  Saved: coding_checklist.md")

    coding_order_json = {
        'metadata': {
            'title': 'Visual Coding Order',
            'date': datetime.now().isoformat(),
            'total_folios': len(coding_order),
            'priority_counts': priority_counts
        },
        'phases': {
            'calibration': CALIBRATION_FOLIOS,
            'hubs': HUB_FOLIOS,
            'hypothesis_po': PO_PREFIX_FOLIOS,
            'hypothesis_ko': KO_PREFIX_FOLIOS,
            'isolated_early': ISOLATED_EARLY_FOLIOS
        },
        'coding_order': coding_order,
        'quality_control': {
            'retest_folios': ['f38r', 'f42r'],
            'target_agreement': 0.80,
            'inter_coder_set': CALIBRATION_FOLIOS
        }
    }

    with open('coding_order.json', 'w', encoding='utf-8') as f:
        json.dump(coding_order_json, f, indent=2, ensure_ascii=False)
    print("  Saved: coding_order.json")

    # Summary
    print("\n" + "=" * 70)
    print("CODING ORDER SUMMARY")
    print("=" * 70)
    print(f"\nTotal folios to code: {len(coding_order)}")
    print(f"\nRecommended order:")
    print("  1. CALIBRATION (5 folios): f38r, f9v, f56r, f3v, f42r")
    print("  2. HUB entities (2 folios): f42r, f10v")
    print("  3. H1 hypothesis folios (3): f11v, f51v, f23v (po prefix)")
    print("  4. H4 hypothesis folios (4): f5v, f45v, f3v, f29v (ko prefix)")
    print("  5. Remaining by length category")
    print("\nQuality control:")
    print("  - Re-code f38r and f42r at session end")
    print("  - Target >80% agreement on re-coded folios")

    return {
        'coding_order': coding_order,
        'priority_counts': priority_counts
    }


if __name__ == '__main__':
    main()
