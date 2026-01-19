"""
AZC Parsing Diagnostic - Expert-Prescribed Test

PURPOSE: Determine if Currier A record parsing is feeding AZC too much material,
collapsing discrimination and destroying C481 downstream.

HYPOTHESIS: The parser may be extracting tokens/components that should NOT
activate AZC constraints:
- Infrastructure tokens (DA, ol, ar in certain roles)
- Closure/articulation scaffolding
- Universal MIDDLEs that don't discriminate

RELEVANT CONSTRAINTS:
- C292: Articulators = ZERO identity distinction
- C254: Multiplicity does NOT interact with B
- C233: LINE_ATOMIC (no aggregation semantics)
- C256: Markers at block END are tagging, not content
- C422: DA tokens are punctuation, not discriminators
- C470: Only restricted MIDDLEs participate in AZC incompatibility
- C441: Activation is sparse and exception-based, not cumulative

TEST:
1. For each A record, compute:
   - all_middles: everything currently extracted
   - restricted_middles: those with AZC spread 1-3
   - azc_active_middles: restricted AND not infrastructure

2. Check distribution - if azc_active is collapsed, parsing is the bug
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Set, Dict, List

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

# Force fresh load
import core.data_loader as dl
dl._data_store = None

from core.data_loader import load_all_data
from core.a_record_loader import load_a_records
from core.constraint_bundle import compute_record_bundle
from core.morphology import decompose_token

# ============================================================================
# INFRASTRUCTURE IDENTIFICATION
# ============================================================================

# Per C292, C422, C256: These are infrastructure/articulator tokens
# that should NOT participate in AZC discrimination
INFRASTRUCTURE_TOKENS = {
    # Pure articulators (C292)
    'ol', 'or', 'ar', 'al',
    # DA family (C422 - punctuation)
    'daiin', 'dain', 'dar', 'dal',
    # Closure markers
    'dy', 'ky',
}

# MIDDLEs that are infrastructure/carrier, not discriminators
# These appear in MIDDLE position but carry no AZC signal
INFRASTRUCTURE_MIDDLES = {
    # Empty/null
    '',
    # Single-char carriers (too common to discriminate)
    # Per C475: Hub MIDDLEs like 'a', 'o', 'e' are universal connectors
}

# Universal hub MIDDLEs (per C475, C470)
# These appear in 4+ folios and cannot forbid compatibility
# They're "everywhere" so they carry no discrimination signal
HUB_MIDDLES = {'a', 'o', 'e', 'ee', 'eo'}  # From C475


def is_infrastructure_token(token: str) -> bool:
    """Check if a token is pure infrastructure (should be ignored by AZC)."""
    # Check full token match
    if token in INFRASTRUCTURE_TOKENS:
        return True
    # Check if it's a minimal form (very short, no MIDDLE content)
    if len(token) <= 2:
        return True
    return False


def is_infrastructure_middle(middle: str) -> bool:
    """Check if a MIDDLE is infrastructure (should not activate AZC)."""
    if not middle or middle in INFRASTRUCTURE_MIDDLES:
        return True
    # Single-char MIDDLEs are often too universal
    if len(middle) == 1 and middle in HUB_MIDDLES:
        return True
    return False


def run_parsing_diagnostic():
    """Run the parsing diagnostic to check MIDDLE extraction."""
    print("=" * 70)
    print("AZC PARSING DIAGNOSTIC")
    print("=" * 70)
    print()
    print("Checking if parsing feeds too much material to AZC...")
    print()

    # Load data
    print("Loading data...")
    data_store = load_all_data()
    a_store = load_a_records()
    print(f"  Loaded {len(a_store.registry_entries)} A entries")
    print()

    # Analyze each record
    results = []
    middle_usage = Counter()  # Track which MIDDLEs appear most
    token_type_counts = Counter()  # Track token types

    for record in a_store.registry_entries:
        bundle = compute_record_bundle(record)

        # Get all extracted MIDDLEs
        all_middles = bundle.middles

        # Classify MIDDLEs
        restricted_middles = set()
        universal_middles = set()
        unknown_middles = set()
        infrastructure_middles = set()

        for m in all_middles:
            if is_infrastructure_middle(m):
                infrastructure_middles.add(m)
                continue

            spread = data_store.middle_folio_spread.get(m, 0)
            if spread == 0:
                unknown_middles.add(m)
            elif spread <= 3:
                restricted_middles.add(m)
            else:
                universal_middles.add(m)

        # AZC-active = restricted AND not infrastructure
        azc_active = restricted_middles - infrastructure_middles

        # Track usage
        for m in all_middles:
            middle_usage[m] += 1

        # Classify tokens
        for token in record.tokens:
            if is_infrastructure_token(token):
                token_type_counts['infrastructure'] += 1
            else:
                token_type_counts['content'] += 1

        results.append({
            'record_id': record.display_name,
            'n_tokens': len(record.tokens),
            'all_middles': sorted(all_middles),
            'restricted': sorted(restricted_middles),
            'universal': sorted(universal_middles),
            'unknown': sorted(unknown_middles),
            'infrastructure': sorted(infrastructure_middles),
            'azc_active': sorted(azc_active),
            'counts': {
                'total': len(all_middles),
                'restricted': len(restricted_middles),
                'universal': len(universal_middles),
                'unknown': len(unknown_middles),
                'infrastructure': len(infrastructure_middles),
                'azc_active': len(azc_active)
            }
        })

    # ========================================
    # ANALYSIS
    # ========================================

    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # 1. Overall token type breakdown
    print("\n1. TOKEN TYPE BREAKDOWN")
    print("-" * 40)
    total_tokens = sum(token_type_counts.values())
    for ttype, count in token_type_counts.most_common():
        print(f"  {ttype:15}: {count:5} ({100*count/total_tokens:.1f}%)")

    # 2. MIDDLE extraction summary
    print("\n2. MIDDLE EXTRACTION SUMMARY")
    print("-" * 40)

    total_counts = Counter()
    for r in results:
        for key, val in r['counts'].items():
            total_counts[key] += val

    avg_counts = {k: v / len(results) for k, v in total_counts.items()}

    print(f"  Avg per record:")
    for key in ['total', 'restricted', 'universal', 'unknown', 'infrastructure', 'azc_active']:
        print(f"    {key:15}: {avg_counts[key]:.2f}")

    # 3. Distribution of azc_active counts
    print("\n3. AZC-ACTIVE MIDDLE DISTRIBUTION")
    print("-" * 40)

    azc_active_dist = Counter(r['counts']['azc_active'] for r in results)
    print("  AZC-active count | Records")
    for count in sorted(azc_active_dist.keys()):
        n_records = azc_active_dist[count]
        bar = '#' * min(50, n_records // 10)
        print(f"  {count:3} azc_active: {n_records:5} records {bar}")

    # 4. Most common MIDDLEs overall
    print("\n4. MOST COMMON MIDDLEs (TOP 20)")
    print("-" * 40)
    for middle, count in middle_usage.most_common(20):
        spread = data_store.middle_folio_spread.get(middle, 0)
        if spread == 0:
            status = "UNKNOWN"
        elif spread <= 3:
            status = f"RESTRICTED({spread})"
        else:
            status = f"UNIVERSAL({spread})"
        infra = " [INFRA]" if is_infrastructure_middle(middle) else ""
        print(f"  '{middle:10}': {count:5} occurrences, {status:15}{infra}")

    # 5. Records with 0 azc_active (potential problem)
    print("\n5. RECORDS WITH 0 AZC-ACTIVE MIDDLEs")
    print("-" * 40)
    zero_azc = [r for r in results if r['counts']['azc_active'] == 0]
    print(f"  Count: {len(zero_azc)} / {len(results)} ({100*len(zero_azc)/len(results):.1f}%)")

    if zero_azc:
        print("\n  Examples (first 5):")
        for r in zero_azc[:5]:
            print(f"    {r['record_id']}: {r['n_tokens']} tokens")
            print(f"      all_middles: {r['all_middles']}")
            print(f"      restricted: {r['restricted']}")
            print(f"      unknown: {r['unknown']}")

    # 6. Records with identical azc_active sets
    print("\n6. AZC-ACTIVE SET COLLISIONS")
    print("-" * 40)

    azc_sets = defaultdict(list)
    for r in results:
        key = tuple(sorted(r['azc_active']))
        azc_sets[key].append(r['record_id'])

    collision_groups = {k: v for k, v in azc_sets.items() if len(v) > 1}
    collision_count = sum(len(v) - 1 for v in collision_groups.values())

    print(f"  Unique azc_active sets: {len(azc_sets)}")
    print(f"  Collision groups: {len(collision_groups)}")
    print(f"  Total collisions: {collision_count}")

    print("\n  Largest collision groups:")
    sorted_groups = sorted(collision_groups.items(), key=lambda x: -len(x[1]))
    for azc_set, records in sorted_groups[:5]:
        print(f"    {azc_set}: {len(records)} records")
        print(f"      Examples: {records[:5]}...")

    # 7. Compare to original signature test
    print("\n7. UNIQUENESS COMPARISON")
    print("-" * 40)

    original_unique = len(azc_sets)
    original_ratio = original_unique / len(results)
    print(f"  Original all_middles approach: ~29 unique signatures (1.9%)")
    print(f"  With azc_active filtering: {original_unique} unique sets ({100*original_ratio:.1f}%)")

    if original_ratio > 0.05:
        improvement = original_ratio / 0.019
        print(f"  >>> {improvement:.1f}x improvement in uniqueness <<<")
    else:
        print(f"  >>> Still low uniqueness - parsing may not be the only issue <<<")

    # ========================================
    # DETAILED INSPECTION
    # ========================================

    print("\n" + "=" * 70)
    print("DETAILED INSPECTION: SAMPLE RECORDS")
    print("=" * 70)

    # Show some records from each category
    categories = {
        'zero_azc': [r for r in results if r['counts']['azc_active'] == 0][:3],
        'low_azc': [r for r in results if r['counts']['azc_active'] == 1][:3],
        'mid_azc': [r for r in results if r['counts']['azc_active'] == 2][:3],
        'high_azc': [r for r in results if r['counts']['azc_active'] >= 3][:3],
    }

    for cat_name, cat_records in categories.items():
        print(f"\n{cat_name.upper()} ({len(cat_records)} shown):")
        for r in cat_records:
            print(f"  {r['record_id']}: {r['n_tokens']} tokens")
            print(f"    all_middles ({r['counts']['total']}): {r['all_middles']}")
            print(f"    restricted ({r['counts']['restricted']}): {r['restricted']}")
            print(f"    azc_active ({r['counts']['azc_active']}): {r['azc_active']}")
            print()

    # ========================================
    # VERDICT
    # ========================================

    print("=" * 70)
    print("DIAGNOSTIC VERDICT")
    print("=" * 70)

    issues = []
    findings = []

    # Check for parsing issues
    if len(zero_azc) > len(results) * 0.5:
        issues.append(f"ISSUE: {len(zero_azc)/len(results)*100:.0f}% of records have 0 azc_active MIDDLEs")

    if original_ratio < 0.1:
        issues.append(f"ISSUE: Only {original_ratio*100:.1f}% unique azc_active sets (still collapsed)")

    if avg_counts['unknown'] > avg_counts['restricted']:
        issues.append(f"ISSUE: More UNKNOWN MIDDLEs ({avg_counts['unknown']:.1f}) than RESTRICTED ({avg_counts['restricted']:.1f})")

    # Positive findings
    if original_ratio > 0.019:
        findings.append(f"FINDING: azc_active filtering improved uniqueness from 1.9% to {original_ratio*100:.1f}%")

    if avg_counts['azc_active'] < avg_counts['total'] * 0.5:
        findings.append(f"FINDING: azc_active is a proper subset ({avg_counts['azc_active']:.1f} vs {avg_counts['total']:.1f} total)")

    print()
    for f in findings:
        print(f"  [+] {f}")
    for i in issues:
        print(f"  [-] {i}")

    print()
    if issues:
        print("CONCLUSION: Parsing issues likely contributing to C481 failure")
        print("RECOMMENDATION: Review MIDDLE extraction logic and infrastructure filtering")
    else:
        print("CONCLUSION: Parsing may be correct; issue may be elsewhere")

    # Save results
    output = {
        'summary': {
            'total_records': len(results),
            'avg_counts': avg_counts,
            'zero_azc_records': len(zero_azc),
            'unique_azc_sets': len(azc_sets),
            'unique_ratio': original_ratio,
            'token_types': dict(token_type_counts)
        },
        'middle_usage': dict(middle_usage.most_common(50)),
        'azc_active_distribution': dict(azc_active_dist),
        'largest_collisions': [
            {'azc_set': list(k), 'count': len(v), 'examples': v[:10]}
            for k, v in sorted_groups[:10]
        ],
        'sample_records': {
            cat: [r for r in records]
            for cat, records in categories.items()
        }
    }

    output_path = PROJECT_ROOT / "results" / "parsing_diagnostic.json"
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == "__main__":
    run_parsing_diagnostic()
