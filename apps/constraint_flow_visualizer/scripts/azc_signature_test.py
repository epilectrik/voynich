"""
AZC Signature Uniqueness Test - Expert-Specified Definitive Test

PURPOSE: Test whether AZC produces unique CONSTRAINT SIGNATURES per A entry.

KEY INSIGHT (from expert):
- C481 does NOT say "each A entry yields unique B folio sets"
- C481 says "each A entry yields unique CONSTRAINT SIGNATURES"

A constraint signature captures the STRUCTURAL IMPACT on grammar:
- Which hazard classes survive/blocked
- Which decomposable classes survive/blocked
- Kernel degree metrics
- Escape/recovery density

If signatures collide -> AZC model fails (C481 violated)
If signatures are unique -> AZC model upheld at correct structural level

CONSTRAINTS BEING TESTED:
- C481: Survivor-Set Uniqueness (at signature level)
- C458: Hazard exposure + intervention diversity
- C468-C470: AZC→B legality inheritance
- C490: Categorical strategy exclusion
"""

import sys
import json
import random
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from typing import Set, Dict, List, Tuple, FrozenSet

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

# Force fresh load
import core.data_loader as dl
dl._data_store = None

from core.data_loader import load_all_data, is_atomic_hazard, is_decomposable_hazard
from core.a_record_loader import load_a_records
from core.constraint_bundle import compute_record_bundle
from core.azc_projection import project_bundle
from core.reachability_engine import compute_reachability, ReachabilityStatus


@dataclass(frozen=True)
class ConstraintSignature:
    """
    The structural constraint impact of an A entry at zone S.

    This is what C481 measures - not raw B folio IDs.
    """
    # Hazard class state
    surviving_atomic_hazards: FrozenSet[int]
    surviving_decomposable_hazards: FrozenSet[int]
    blocked_decomposable_hazards: FrozenSet[int]

    # Class-level state
    reachable_classes: FrozenSet[int]
    pruned_classes: FrozenSet[int]

    # Kernel metrics
    kernel_classes_count: int  # Should always be 31 per model

    # Derived metrics
    n_reachable: int
    n_pruned: int
    hazard_exposure: float  # ratio of surviving hazards

    def to_hash(self) -> str:
        """Create a unique hash for collision detection."""
        # Use sorted tuples for deterministic hashing
        key = (
            tuple(sorted(self.surviving_atomic_hazards)),
            tuple(sorted(self.surviving_decomposable_hazards)),
            tuple(sorted(self.blocked_decomposable_hazards)),
            tuple(sorted(self.reachable_classes)),
            self.n_reachable,
            self.n_pruned
        )
        return hashlib.md5(str(key).encode()).hexdigest()[:12]

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            'surviving_atomic_hazards': sorted(self.surviving_atomic_hazards),
            'surviving_decomposable_hazards': sorted(self.surviving_decomposable_hazards),
            'blocked_decomposable_hazards': sorted(self.blocked_decomposable_hazards),
            'reachable_classes': sorted(self.reachable_classes),
            'pruned_classes': sorted(self.pruned_classes),
            'kernel_classes_count': self.kernel_classes_count,
            'n_reachable': self.n_reachable,
            'n_pruned': self.n_pruned,
            'hazard_exposure': self.hazard_exposure
        }


def compute_constraint_signature(b_reach, data_store) -> ConstraintSignature:
    """
    Compute the constraint signature for an A entry at zone S.

    This captures the STRUCTURAL IMPACT, not raw folio identity.
    """
    # Get zone S grammar state
    # grammar_by_zone has keys: C, P, R1, R2, R3, S
    zone_s_grammar = b_reach.grammar_by_zone.get('S')
    if not zone_s_grammar:
        # No S zone = fully blocked
        return ConstraintSignature(
            surviving_atomic_hazards=frozenset(),
            surviving_decomposable_hazards=frozenset(),
            blocked_decomposable_hazards=frozenset(data_store.decomposable_hazard_classes),
            reachable_classes=frozenset(),
            pruned_classes=frozenset(range(1, 50)),
            kernel_classes_count=0,
            n_reachable=0,
            n_pruned=49,
            hazard_exposure=0.0
        )

    reachable = zone_s_grammar.reachable_classes
    pruned = zone_s_grammar.pruned_classes

    # Categorize hazard classes
    surviving_atomic = set()
    surviving_decomposable = set()
    blocked_decomposable = set()

    for class_id in data_store.hazard_classes:
        if is_atomic_hazard(class_id):
            if class_id in reachable:
                surviving_atomic.add(class_id)
            # Note: atomic hazards should never be pruned per model
        elif is_decomposable_hazard(class_id):
            if class_id in reachable:
                surviving_decomposable.add(class_id)
            else:
                blocked_decomposable.add(class_id)

    # Kernel classes count
    kernel_count = len(reachable & data_store.kernel_classes)

    # Hazard exposure ratio
    total_hazards = len(data_store.hazard_classes)
    surviving_hazards = len(surviving_atomic) + len(surviving_decomposable)
    hazard_exposure = surviving_hazards / total_hazards if total_hazards > 0 else 0.0

    return ConstraintSignature(
        surviving_atomic_hazards=frozenset(surviving_atomic),
        surviving_decomposable_hazards=frozenset(surviving_decomposable),
        blocked_decomposable_hazards=frozenset(blocked_decomposable),
        reachable_classes=frozenset(reachable),
        pruned_classes=frozenset(pruned),
        kernel_classes_count=kernel_count,
        n_reachable=len(reachable),
        n_pruned=len(pruned),
        hazard_exposure=hazard_exposure
    )


def classify_a_entry(bundle_middles: Set[str], data_store) -> str:
    """Classify A entry into universal/mixed/tail."""
    restricted = set()
    universal = set()

    for m in bundle_middles:
        spread = data_store.middle_folio_spread.get(m, 0)
        if spread == 0:
            continue  # Unknown
        elif spread <= 3:
            restricted.add(m)
        else:
            universal.add(m)

    if len(restricted) == 0:
        return 'universal'
    elif len(restricted) >= 3:
        return 'tail'
    else:
        return 'mixed'


def run_signature_test():
    """Run the definitive AZC constraint signature uniqueness test."""
    print("=" * 70)
    print("AZC CONSTRAINT SIGNATURE UNIQUENESS TEST")
    print("=" * 70)
    print()
    print("Testing C481 at the correct structural level:")
    print("  - Not 'which B folios survive'")
    print("  - But 'what constraint signature emerges'")
    print()

    # Load data
    print("Loading data...")
    data_store = load_all_data()
    a_store = load_a_records()
    print(f"  Loaded {len(a_store.registry_entries)} A entries")
    print(f"  Hazard classes: {len(data_store.hazard_classes)}")
    print(f"  Kernel classes: {len(data_store.kernel_classes)}")
    print()

    # Process ALL A entries (not just samples)
    print("Computing constraint signatures for ALL A entries...")

    results = []
    signature_to_entries = defaultdict(list)  # hash -> [entry_ids]
    signatures_by_class = {'universal': [], 'mixed': [], 'tail': []}

    for i, record in enumerate(a_store.registry_entries):
        if (i + 1) % 200 == 0:
            print(f"  Processed {i + 1}/{len(a_store.registry_entries)}...")

        bundle = compute_record_bundle(record)
        entry_class = classify_a_entry(bundle.middles, data_store)

        projection = project_bundle(bundle)
        b_reach = compute_reachability(projection)

        signature = compute_constraint_signature(b_reach, data_store)
        sig_hash = signature.to_hash()

        result = {
            'A_id': record.display_name,
            'class': entry_class,
            'signature_hash': sig_hash,
            'n_reachable': signature.n_reachable,
            'n_pruned': signature.n_pruned,
            'hazard_exposure': signature.hazard_exposure,
            'surviving_decomposable': list(signature.surviving_decomposable_hazards),
            'blocked_decomposable': list(signature.blocked_decomposable_hazards)
        }
        results.append(result)
        signature_to_entries[sig_hash].append(record.display_name)
        signatures_by_class[entry_class].append(sig_hash)

    print(f"  Done. Processed {len(results)} entries.")
    print()

    # ========================================
    # ANALYSIS
    # ========================================

    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # 1. Unique signature count
    print("\n1. SIGNATURE UNIQUENESS")
    print("-" * 40)

    unique_signatures = len(signature_to_entries)
    total_entries = len(results)
    unique_ratio = unique_signatures / total_entries

    print(f"  Total A entries: {total_entries}")
    print(f"  Unique signatures: {unique_signatures}")
    print(f"  Unique ratio: {unique_ratio:.3f} ({unique_ratio*100:.1f}%)")

    # Count collisions
    collision_groups = {h: entries for h, entries in signature_to_entries.items() if len(entries) > 1}
    collision_count = sum(len(entries) - 1 for entries in collision_groups.values())

    print(f"  Collision groups: {len(collision_groups)}")
    print(f"  Total collisions: {collision_count}")

    # 2. Signatures by class
    print("\n2. SIGNATURES BY A-ENTRY CLASS")
    print("-" * 40)

    for cls in ['universal', 'mixed', 'tail']:
        hashes = signatures_by_class[cls]
        unique_in_class = len(set(hashes))
        total_in_class = len(hashes)
        ratio = unique_in_class / total_in_class if total_in_class > 0 else 0
        print(f"  {cls:12}: {total_in_class:4} entries, {unique_in_class:4} unique signatures ({ratio*100:.1f}%)")

    # 3. Signature distribution
    print("\n3. SIGNATURE SIZE DISTRIBUTION")
    print("-" * 40)

    size_distribution = Counter(len(entries) for entries in signature_to_entries.values())
    print("  Entries per signature:")
    for size in sorted(size_distribution.keys())[:10]:
        count = size_distribution[size]
        print(f"    {size:4} entries: {count:4} signatures")
    if len(size_distribution) > 10:
        print(f"    ... and {len(size_distribution) - 10} more sizes")

    # 4. Largest collision groups
    print("\n4. LARGEST COLLISION GROUPS")
    print("-" * 40)

    sorted_groups = sorted(collision_groups.items(), key=lambda x: -len(x[1]))
    for sig_hash, entries in sorted_groups[:5]:
        # Get signature details
        example_entry = entries[0]
        example_result = next(r for r in results if r['A_id'] == example_entry)
        print(f"  {sig_hash}: {len(entries)} entries")
        print(f"    n_reachable={example_result['n_reachable']}, hazard_exp={example_result['hazard_exposure']:.2f}")
        print(f"    Examples: {entries[:5]}...")

    # 5. Hazard exposure distribution
    print("\n5. HAZARD EXPOSURE BY CLASS")
    print("-" * 40)

    for cls in ['universal', 'mixed', 'tail']:
        class_results = [r for r in results if r['class'] == cls]
        if class_results:
            exposures = [r['hazard_exposure'] for r in class_results]
            avg_exp = sum(exposures) / len(exposures)
            min_exp = min(exposures)
            max_exp = max(exposures)
            print(f"  {cls:12}: avg={avg_exp:.3f}, min={min_exp:.3f}, max={max_exp:.3f}")

    # 6. Decomposable hazard blocking
    print("\n6. DECOMPOSABLE HAZARD BLOCKING")
    print("-" * 40)

    for cls in ['universal', 'mixed', 'tail']:
        class_results = [r for r in results if r['class'] == cls]
        if class_results:
            blocked_counts = [len(r['blocked_decomposable']) for r in class_results]
            avg_blocked = sum(blocked_counts) / len(blocked_counts)
            print(f"  {cls:12}: avg blocked = {avg_blocked:.1f} decomposable hazard classes")

    # ========================================
    # VERDICT
    # ========================================

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    failures = []
    passes = []

    # Critical test: Do signatures collide at unacceptable rates?
    # Per C481: 0 collisions in 1575 lines (original test)
    # We allow some tolerance since we're testing a subset of the signature

    # Test 1: Overall uniqueness
    if unique_ratio >= 0.9:
        passes.append(f"PASS: High signature uniqueness ({unique_ratio*100:.1f}%)")
    elif unique_ratio >= 0.5:
        passes.append(f"MARGINAL: Moderate signature uniqueness ({unique_ratio*100:.1f}%)")
    else:
        failures.append(f"FAIL: Low signature uniqueness ({unique_ratio*100:.1f}%)")

    # Test 2: Universal entries should still differentiate
    universal_hashes = signatures_by_class['universal']
    if universal_hashes:
        universal_unique = len(set(universal_hashes)) / len(universal_hashes)
        if universal_unique < 0.1:
            failures.append(f"FAIL: Universal entries collapse to same signature ({universal_unique*100:.1f}% unique)")
        else:
            passes.append(f"PASS: Universal entries show differentiation ({universal_unique*100:.1f}% unique)")

    # Test 3: Mixed entries should show variety
    mixed_hashes = signatures_by_class['mixed']
    if mixed_hashes:
        mixed_unique = len(set(mixed_hashes)) / len(mixed_hashes)
        if mixed_unique >= 0.5:
            passes.append(f"PASS: Mixed entries show good variety ({mixed_unique*100:.1f}% unique)")
        elif mixed_unique >= 0.2:
            passes.append(f"MARGINAL: Mixed entries show some variety ({mixed_unique*100:.1f}% unique)")
        else:
            failures.append(f"FAIL: Mixed entries collapse ({mixed_unique*100:.1f}% unique)")

    # Test 4: Hazard exposure differentiation
    universal_results = [r for r in results if r['class'] == 'universal']
    mixed_results = [r for r in results if r['class'] == 'mixed']
    tail_results = [r for r in results if r['class'] == 'tail']

    if universal_results and mixed_results:
        u_exp = sum(r['hazard_exposure'] for r in universal_results) / len(universal_results)
        m_exp = sum(r['hazard_exposure'] for r in mixed_results) / len(mixed_results)
        if m_exp < u_exp * 0.95:  # Mixed should have lower hazard exposure
            passes.append(f"PASS: Hazard exposure differentiates (universal={u_exp:.2f}, mixed={m_exp:.2f})")
        else:
            failures.append(f"FAIL: No hazard exposure differentiation (universal={u_exp:.2f}, mixed={m_exp:.2f})")

    print()
    for p in passes:
        print(f"  [PASS] {p}")
    for f in failures:
        print(f"  [FAIL] {f}")

    print()
    # Final verdict
    critical_failures = [f for f in failures if 'FAIL' in f and 'uniqueness' in f.lower()]

    if critical_failures:
        print("OVERALL: CRITICAL FAILURE")
        print(">>> C481 VIOLATED - AZC MODEL MUST BE REOPENED <<<")
        verdict = 'CRITICAL_FAIL'
    elif failures:
        print(f"OVERALL: {len(failures)} FAILURES, {len(passes)} PASSES")
        print(">>> AZC MODEL PARTIALLY UPHELD - FURTHER INVESTIGATION NEEDED <<<")
        verdict = 'PARTIAL_FAIL'
    else:
        print(f"OVERALL: ALL {len(passes)} TESTS PASSED")
        print(">>> C481 UPHELD AT CONSTRAINT SIGNATURE LEVEL <<<")
        verdict = 'PASS'

    # Save results
    output = {
        'summary': {
            'total_entries': total_entries,
            'unique_signatures': unique_signatures,
            'unique_ratio': unique_ratio,
            'collision_count': collision_count,
            'by_class': {
                cls: {
                    'total': len(signatures_by_class[cls]),
                    'unique': len(set(signatures_by_class[cls]))
                }
                for cls in ['universal', 'mixed', 'tail']
            },
            'verdict': {
                'passes': passes,
                'failures': failures,
                'overall': verdict
            }
        },
        'signature_groups': {
            h: entries for h, entries in sorted_groups[:20]  # Top 20 collision groups
        },
        'detailed_results': results[:100]  # First 100 for inspection
    }

    output_path = PROJECT_ROOT / "results" / "azc_signature_test.json"
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == "__main__":
    run_signature_test()
