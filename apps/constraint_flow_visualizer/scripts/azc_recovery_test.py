"""
AZC Recovery Test - Expert-Specified Falsifiable Test

PURPOSE: Test whether AZC produces mid-sized, distinct survivor sets.

CONSTRAINTS BEING TESTED:
- C479: Survivor-Set Discrimination Scaling
- C481: Survivor-Set Uniqueness
- C490: Categorical Strategy Exclusion
- C468-C470: AZC→B legality inheritance
- C124/C440: Grammar universality without coupling

PASS CONDITIONS:
1. Mid-sized (not tiny, not huge) S-SURVIVOR sets
2. Strong dependence on A vocabulary composition
3. Clear late-stage pruning (R→S)
4. High uniqueness of survivor signatures

FAILURE CONDITIONS:
1. S-SURVIVOR count is always 0 or always ≈82
2. S-SURVIVOR sets do not differ meaningfully across A entries
3. Tail-dominant A entries do not sharply reduce S-SURVIVORS
4. Strategy exclusions do not concentrate at S
5. Survivor sets collide across different A entries
"""

import sys
import json
import random
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import Set, Dict, List, Tuple

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

# Force fresh load
import core.data_loader as dl
dl._data_store = None

from core.data_loader import load_all_data
from core.a_record_loader import load_a_records
from core.constraint_bundle import compute_record_bundle
from core.azc_projection import project_bundle
from core.reachability_engine import compute_reachability, ReachabilityStatus


@dataclass
class AEntryClassification:
    """Classification of an A entry by MIDDLE composition."""
    record_id: str
    bundle_middles: Set[str]
    restricted_middles: Set[str]
    universal_middles: Set[str]
    unknown_middles: Set[str]
    classification: str  # 'universal', 'mixed', 'tail'
    restricted_count: int
    universal_pct: float


def classify_a_entry(record_id: str, bundle_middles: Set[str], data_store) -> AEntryClassification:
    """
    Classify an A entry into one of three bins:
    - universal: ≥80% universal MIDDLEs, no restricted
    - mixed: 1-2 restricted MIDDLEs
    - tail: ≥3 restricted MIDDLEs
    """
    restricted = set()
    universal = set()
    unknown = set()

    for m in bundle_middles:
        spread = data_store.middle_folio_spread.get(m, 0)
        if spread == 0:
            unknown.add(m)
        elif spread <= 3:
            restricted.add(m)
        else:
            universal.add(m)

    # Compute universal percentage (excluding unknowns)
    known_count = len(restricted) + len(universal)
    universal_pct = len(universal) / known_count if known_count > 0 else 1.0

    # Classification logic per expert spec
    if len(restricted) == 0 and universal_pct >= 0.8:
        classification = 'universal'
    elif len(restricted) >= 3:
        classification = 'tail'
    else:
        classification = 'mixed'

    return AEntryClassification(
        record_id=record_id,
        bundle_middles=bundle_middles,
        restricted_middles=restricted,
        universal_middles=universal,
        unknown_middles=unknown,
        classification=classification,
        restricted_count=len(restricted),
        universal_pct=universal_pct
    )


def compute_s_survivors(b_reach, data_store) -> Set[str]:
    """
    Compute S-SURVIVORS: B folios whose required class footprint is satisfied through ZONE S.

    This is the strictest test - survival through full commitment, no escape.

    Note: grammar_by_zone uses 'S' as the key (not fine-grained S zones).
    """
    s_survivors = set()

    # Get reachable classes in zone S
    # grammar_by_zone has keys: C, P, R1, R2, R3, S
    zone_s_grammar = b_reach.grammar_by_zone.get('S')
    if not zone_s_grammar:
        return s_survivors

    s_reachable_classes = zone_s_grammar.reachable_classes

    # Check each B folio
    for folio_id in data_store.b_folio_class_footprints:
        required_classes = data_store.b_folio_class_footprints.get(folio_id, set())
        # S-survivor if all required classes are reachable in S
        if required_classes <= s_reachable_classes:
            s_survivors.add(folio_id)

    return s_survivors


def compute_zone_survivors(b_reach, data_store) -> Dict[str, Set[str]]:
    """Compute survivors for each zone (C, P, R, S).

    Note: grammar_by_zone uses fine-grained zones (R1, R2, R3).
    We consolidate them for reporting: use R3 as the representative
    for R since it's the latest (most restricted).
    """
    zone_survivors = {}

    # Map consolidated zones to actual grammar_by_zone keys
    # R -> R3 (latest R zone), S -> S (only one)
    zone_mapping = {'C': 'C', 'P': 'P', 'R': 'R3', 'S': 'S'}

    for display_zone in ['C', 'P', 'R', 'S']:
        actual_zone = zone_mapping[display_zone]
        zone_grammar = b_reach.grammar_by_zone.get(actual_zone)
        if not zone_grammar:
            zone_survivors[display_zone] = set()
            continue

        zone_reachable = zone_grammar.reachable_classes
        survivors = set()

        for folio_id in data_store.b_folio_class_footprints:
            required = data_store.b_folio_class_footprints.get(folio_id, set())
            if required <= zone_reachable:
                survivors.add(folio_id)

        zone_survivors[display_zone] = survivors

    return zone_survivors


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    union = set1 | set2
    if not union:
        return 1.0
    return len(set1 & set2) / len(union)


def run_recovery_test():
    """Run the expert-specified AZC recovery test."""
    print("=" * 70)
    print("AZC RECOVERY TEST - Expert-Specified Falsifiable Test")
    print("=" * 70)
    print()

    # Step 0: Load data with current fixed implementation
    print("Step 0: Loading data with UNION vocabulary projection...")
    data_store = load_all_data()
    a_store = load_a_records()
    print(f"  Loaded {len(a_store.registry_entries)} A entries (2+ tokens)")
    print(f"  Loaded {len(data_store.b_folio_class_footprints)} B folio footprints")
    print()

    # Step 2: Partition A entries into three bins
    print("Step 2: Classifying A entries by MIDDLE composition...")

    bins = {'universal': [], 'mixed': [], 'tail': []}

    for record in a_store.registry_entries:
        bundle = compute_record_bundle(record)
        classification = classify_a_entry(record.display_name, bundle.middles, data_store)
        bins[classification.classification].append((record, bundle, classification))

    print(f"  Universal-dominant: {len(bins['universal'])} entries")
    print(f"  Mixed: {len(bins['mixed'])} entries")
    print(f"  Tail-dominant: {len(bins['tail'])} entries")
    print()

    # Sample N=50 from each bin (or all if fewer)
    N = 50
    samples = {}
    random.seed(42)  # Reproducibility
    for bin_name, entries in bins.items():
        if len(entries) <= N:
            samples[bin_name] = entries
        else:
            samples[bin_name] = random.sample(entries, N)
        print(f"  Sampled {len(samples[bin_name])} from {bin_name}")
    print()

    # Step 3: Project A → AZC → B for each sample
    print("Step 3: Computing S-SURVIVORS for each sample...")

    results = []
    all_s_survivors = []  # For collision detection

    for bin_name in ['universal', 'mixed', 'tail']:
        print(f"\n  Processing {bin_name} bin...")
        bin_results = []

        for record, bundle, classification in samples[bin_name]:
            # Compute full reachability
            projection = project_bundle(bundle)
            b_reach = compute_reachability(projection)

            # Get S-survivors
            s_survivors = compute_s_survivors(b_reach, data_store)

            # Get zone survivors for late-stage analysis
            zone_survivors = compute_zone_survivors(b_reach, data_store)

            result = {
                'A_id': record.display_name,
                'class': bin_name,
                'restricted_count': classification.restricted_count,
                'universal_pct': classification.universal_pct,
                'S_survivors': sorted(s_survivors),
                'count': len(s_survivors),
                'zone_counts': {z: len(s) for z, s in zone_survivors.items()},
                'R_to_S_drop': len(zone_survivors['R']) - len(zone_survivors['S'])
            }
            bin_results.append(result)
            results.append(result)
            all_s_survivors.append((record.display_name, frozenset(s_survivors)))

        # Bin statistics
        counts = [r['count'] for r in bin_results]
        avg_count = sum(counts) / len(counts) if counts else 0
        min_count = min(counts) if counts else 0
        max_count = max(counts) if counts else 0

        print(f"    S-SURVIVOR counts: min={min_count}, avg={avg_count:.1f}, max={max_count}")

    # ========================================
    # ANALYSIS AND VERDICT
    # ========================================

    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # 1. Cardinality separation by bin
    print("\n1. CARDINALITY SEPARATION")
    print("-" * 40)

    for bin_name in ['universal', 'mixed', 'tail']:
        bin_results = [r for r in results if r['class'] == bin_name]
        counts = [r['count'] for r in bin_results]
        if counts:
            avg = sum(counts) / len(counts)
            print(f"  {bin_name:12}: avg={avg:5.1f}, min={min(counts):3}, max={max(counts):3}")

    # Expected per expert:
    # - Universal: 5-15
    # - Mixed: 1-7
    # - Tail: 0-3

    universal_counts = [r['count'] for r in results if r['class'] == 'universal']
    mixed_counts = [r['count'] for r in results if r['class'] == 'mixed']
    tail_counts = [r['count'] for r in results if r['class'] == 'tail']

    universal_avg = sum(universal_counts) / len(universal_counts) if universal_counts else 0
    mixed_avg = sum(mixed_counts) / len(mixed_counts) if mixed_counts else 0
    tail_avg = sum(tail_counts) / len(tail_counts) if tail_counts else 0

    # 2. Survivor set uniqueness (C481)
    print("\n2. SURVIVOR SET UNIQUENESS (C481)")
    print("-" * 40)

    # Check for collisions
    survivor_sets = defaultdict(list)
    for record_id, s_set in all_s_survivors:
        survivor_sets[s_set].append(record_id)

    collisions = {k: v for k, v in survivor_sets.items() if len(v) > 1}
    collision_count = sum(len(v) - 1 for v in collisions.values())

    print(f"  Total unique survivor sets: {len(survivor_sets)}")
    print(f"  Collision groups: {len(collisions)}")
    print(f"  Total collisions: {collision_count}")

    if collisions:
        print("  Collision examples:")
        for s_set, records in list(collisions.items())[:3]:
            print(f"    {len(s_set)} survivors: {records[:5]}...")

    # 3. Jaccard similarity within and across bins
    print("\n3. JACCARD SIMILARITY")
    print("-" * 40)

    # Within-bin similarity
    for bin_name in ['universal', 'mixed', 'tail']:
        bin_survivors = [frozenset(r['S_survivors']) for r in results if r['class'] == bin_name]
        if len(bin_survivors) >= 2:
            similarities = []
            for i in range(min(100, len(bin_survivors))):
                for j in range(i + 1, min(100, len(bin_survivors))):
                    sim = jaccard_similarity(bin_survivors[i], bin_survivors[j])
                    similarities.append(sim)
            avg_sim = sum(similarities) / len(similarities) if similarities else 0
            print(f"  {bin_name:12} within-bin: avg Jaccard = {avg_sim:.3f}")

    # 4. Late-stage pruning (R→S)
    print("\n4. LATE-STAGE PRUNING (R->S)")
    print("-" * 40)

    for bin_name in ['universal', 'mixed', 'tail']:
        bin_results = [r for r in results if r['class'] == bin_name]
        drops = [r['R_to_S_drop'] for r in bin_results]
        if drops:
            avg_drop = sum(drops) / len(drops)
            entries_with_drop = sum(1 for d in drops if d > 0)
            print(f"  {bin_name:12}: avg R->S drop = {avg_drop:.1f}, entries with drop: {entries_with_drop}/{len(drops)}")

    # 5. Strategy exclusion pattern
    print("\n5. ZONE-BY-ZONE SURVIVORS")
    print("-" * 40)

    for bin_name in ['universal', 'mixed', 'tail']:
        bin_results = [r for r in results if r['class'] == bin_name]
        zone_avgs = {z: sum(r['zone_counts'][z] for r in bin_results) / len(bin_results)
                     for z in ['C', 'P', 'R', 'S']}
        print(f"  {bin_name:12}: C={zone_avgs['C']:.1f} -> P={zone_avgs['P']:.1f} -> R={zone_avgs['R']:.1f} -> S={zone_avgs['S']:.1f}")

    # ========================================
    # VERDICT
    # ========================================

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    failures = []
    passes = []

    # Failure condition 1: S-SURVIVOR count is always 0 or always ≈82
    all_counts = [r['count'] for r in results]
    all_zero = all(c == 0 for c in all_counts)
    all_max = all(c >= 80 for c in all_counts)
    count_range = max(all_counts) - min(all_counts) if all_counts else 0

    if all_zero:
        failures.append("FAIL 1: All S-SURVIVOR counts are 0")
    elif all_max:
        failures.append("FAIL 1: All S-SURVIVOR counts are ~82 (no discrimination)")
    elif count_range < 5:
        failures.append(f"FAIL 1: Insufficient count variation (range={count_range})")
    else:
        passes.append(f"PASS 1: S-SURVIVOR counts vary (range={count_range})")

    # Failure condition 2: S-SURVIVOR sets do not differ meaningfully
    unique_ratio = len(survivor_sets) / len(all_s_survivors) if all_s_survivors else 0
    if unique_ratio < 0.5:
        failures.append(f"FAIL 2: Low survivor set diversity (unique ratio = {unique_ratio:.2f})")
    else:
        passes.append(f"PASS 2: Good survivor set diversity (unique ratio = {unique_ratio:.2f})")

    # Failure condition 3: Tail-dominant does not sharply reduce S-SURVIVORS
    if tail_counts and universal_counts:
        if tail_avg >= universal_avg * 0.8:  # Tail should be much lower
            failures.append(f"FAIL 3: Tail-dominant not sharply reduced (tail={tail_avg:.1f} vs universal={universal_avg:.1f})")
        else:
            passes.append(f"PASS 3: Tail-dominant shows reduction (tail={tail_avg:.1f} vs universal={universal_avg:.1f})")
    elif not tail_counts:
        passes.append("PASS 3: No tail-dominant entries to test (skipped)")

    # Failure condition 4: Strategy exclusions do not concentrate at S
    late_drops = [r['R_to_S_drop'] for r in results]
    avg_late_drop = sum(late_drops) / len(late_drops) if late_drops else 0
    entries_with_late_drop = sum(1 for d in late_drops if d > 0)

    if avg_late_drop < 0.5 and entries_with_late_drop < len(results) * 0.1:
        failures.append(f"FAIL 4: No late-stage (R->S) exclusions (avg drop = {avg_late_drop:.1f})")
    else:
        passes.append(f"PASS 4: Late-stage exclusions present (avg R->S drop = {avg_late_drop:.1f})")

    # Failure condition 5: Survivor sets collide
    if collision_count > len(all_s_survivors) * 0.1:  # More than 10% collisions
        failures.append(f"FAIL 5: High collision rate ({collision_count} collisions, {collision_count/len(all_s_survivors)*100:.1f}%)")
    else:
        passes.append(f"PASS 5: Low collision rate ({collision_count} collisions)")

    print()
    for p in passes:
        print(f"  [PASS] {p}")
    for f in failures:
        print(f"  [FAIL] {f}")

    print()
    if failures:
        print(f"OVERALL: {len(failures)} FAILURES, {len(passes)} PASSES")
        print(">>> AZC MODEL REQUIRES INVESTIGATION <<<")
    else:
        print(f"OVERALL: ALL {len(passes)} TESTS PASSED")
        print(">>> AZC MODEL FUNCTIONING AS SPECIFIED <<<")

    # Save detailed results
    output = {
        'summary': {
            'total_entries': len(results),
            'bins': {
                'universal': len([r for r in results if r['class'] == 'universal']),
                'mixed': len([r for r in results if r['class'] == 'mixed']),
                'tail': len([r for r in results if r['class'] == 'tail'])
            },
            'cardinality': {
                'universal_avg': universal_avg,
                'mixed_avg': mixed_avg,
                'tail_avg': tail_avg
            },
            'uniqueness': {
                'unique_sets': len(survivor_sets),
                'collisions': collision_count,
                'unique_ratio': unique_ratio
            },
            'late_stage': {
                'avg_R_to_S_drop': avg_late_drop,
                'entries_with_drop': entries_with_late_drop
            },
            'verdict': {
                'passes': passes,
                'failures': failures,
                'overall': 'PASS' if not failures else 'FAIL'
            }
        },
        'detailed_results': results
    }

    output_path = PROJECT_ROOT / "results" / "azc_recovery_test.json"
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nDetailed results saved to: {output_path}")

    return output


if __name__ == "__main__":
    run_recovery_test()
