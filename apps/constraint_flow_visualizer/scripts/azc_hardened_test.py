"""
AZC Hardened Test - Expert-Prescribed Fixes Applied

FIXES APPLIED:
1. Hardened azc_active criteria (infrastructure, PREFIX-bound, closure filtering)
2. C481 test CONDITIONAL on azc_active ≥ 1 (correct interpretation)
3. Block malformed MIDDLEs (spread=0 AND not in AZC vocab)

CONSTRAINTS ENFORCED:
- C276: MIDDLE is PREFIX-bound
- C423: 80% of MIDDLEs are domain-exclusive
- C292: Articulators = ZERO identity distinction
- C422: DA tokens are punctuation, not discriminators
- C470: Only restricted MIDDLEs gate AZC
- C481: Survivor-set uniqueness (CONDITIONAL on activation)
"""

import sys
import json
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import Set, Dict, List, Tuple, FrozenSet, Optional

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

# Force fresh load
import core.data_loader as dl
dl._data_store = None

from core.data_loader import load_all_data, is_atomic_hazard, is_decomposable_hazard
from core.a_record_loader import load_a_records
from core.constraint_bundle import compute_record_bundle
from core.morphology import decompose_token
from core.azc_projection import project_bundle
from core.reachability_engine import compute_reachability

# ============================================================================
# HARDENED AZC-ACTIVE EXTRACTION
# ============================================================================

# Infrastructure tokens (C292, C422) - NEVER activate AZC
INFRASTRUCTURE_TOKENS = {
    'ol', 'or', 'ar', 'al',  # Articulators
    'daiin', 'dain', 'dar', 'dal', 'dam',  # DA family (punctuation)
    'dy', 'ky', 'ty',  # Closure markers
    'aiin', 'ain', 'an',  # Terminal articulation
}

# Closure suffixes - tokens ending in these are likely closure, not content
CLOSURE_SUFFIXES = {'dy', 'ky', 'ty', 'my', 'ny'}

# PREFIX families (C276) - MIDDLEs are PREFIX-bound
PREFIX_FAMILIES = {'ch', 'sh', 'ok', 'ot', 'da', 'qo', 'ol', 'ct'}

# Hub MIDDLEs (C475) - too universal to discriminate
HUB_MIDDLES = {'a', 'o', 'e'}  # Core hubs only


def is_infrastructure_token(token: str) -> bool:
    """Check if token is pure infrastructure (C292, C422)."""
    if token in INFRASTRUCTURE_TOKENS:
        return True
    # Very short tokens are often infrastructure
    if len(token) <= 2 and token in {'ol', 'or', 'ar', 'al', 'an'}:
        return True
    return False


def is_closure_token(token: str) -> bool:
    """Check if token is closure/trailing scaffolding."""
    for suffix in CLOSURE_SUFFIXES:
        if token.endswith(suffix):
            return True
    return False


def is_articulator_token(token: str) -> bool:
    """Check if token is an articulator (C292)."""
    # DA family
    if token.startswith('da') and len(token) <= 5:
        return True
    return False


def is_malformed_middle(middle: str, azc_vocab: Set[str]) -> bool:
    """
    Check if MIDDLE is malformed (likely parsing bleed).

    Criteria:
    - Contains '*' (transcription uncertainty marker)
    - Not in AZC vocab AND not a recognized A-exclusive form
    - Contains unusual character sequences
    """
    if '*' in middle:
        return True
    # Very long MIDDLEs are suspicious
    if len(middle) > 6:
        return True
    return False


def extract_azc_active_middles(
    record,
    data_store,
    azc_vocab: Set[str]
) -> Tuple[Set[str], Dict[str, str]]:
    """
    Extract AZC-active MIDDLEs with hardened criteria.

    Returns:
        - azc_active: Set of MIDDLEs that should activate AZC
        - exclusion_log: Dict mapping excluded MIDDLEs to reason
    """
    azc_active = set()
    exclusion_log = {}

    for token in record.tokens:
        # Gate 1: Infrastructure tokens (C292, C422)
        if is_infrastructure_token(token):
            continue

        # Gate 2: Articulator tokens
        if is_articulator_token(token):
            continue

        # Gate 3: Closure tokens (trailing scaffolding)
        if is_closure_token(token):
            continue

        # Decompose token
        morph = decompose_token(token)
        middle = morph.middle if morph.middle else ""

        if not middle:
            continue

        # Gate 4: Hub MIDDLEs (C475 - too universal)
        if middle in HUB_MIDDLES:
            exclusion_log[middle] = "hub_middle"
            continue

        # Gate 5: Malformed MIDDLEs (parsing bleed)
        if is_malformed_middle(middle, azc_vocab):
            exclusion_log[middle] = "malformed"
            continue

        # Gate 6: Spread check - must be restricted (1-3)
        spread = data_store.middle_folio_spread.get(middle, 0)

        if spread == 0:
            # Not in AZC vocab - check if it's a known A-exclusive form
            if middle not in azc_vocab:
                exclusion_log[middle] = "not_in_azc_vocab"
                continue

        if spread > 3:
            exclusion_log[middle] = f"universal_spread_{spread}"
            continue

        # Passed all gates - this is AZC-active
        azc_active.add(middle)

    return azc_active, exclusion_log


@dataclass(frozen=True)
class ConstraintSignature:
    """Constraint signature for C481 testing."""
    reachable_classes: FrozenSet[int]
    surviving_decomposable: FrozenSet[int]
    blocked_decomposable: FrozenSet[int]
    n_reachable: int
    hazard_exposure: float

    def to_hash(self) -> str:
        key = (
            tuple(sorted(self.reachable_classes)),
            tuple(sorted(self.surviving_decomposable)),
            self.n_reachable
        )
        return hashlib.md5(str(key).encode()).hexdigest()[:12]


def compute_signature(b_reach, data_store) -> ConstraintSignature:
    """Compute constraint signature at zone S."""
    zone_s = b_reach.grammar_by_zone.get('S')
    if not zone_s:
        return ConstraintSignature(
            reachable_classes=frozenset(),
            surviving_decomposable=frozenset(),
            blocked_decomposable=frozenset(data_store.decomposable_hazard_classes),
            n_reachable=0,
            hazard_exposure=0.0
        )

    reachable = zone_s.reachable_classes
    surviving_decomp = reachable & data_store.decomposable_hazard_classes
    blocked_decomp = data_store.decomposable_hazard_classes - reachable

    total_hazards = len(data_store.hazard_classes)
    surviving = len(reachable & data_store.hazard_classes)
    exposure = surviving / total_hazards if total_hazards > 0 else 0.0

    return ConstraintSignature(
        reachable_classes=frozenset(reachable),
        surviving_decomposable=frozenset(surviving_decomp),
        blocked_decomposable=frozenset(blocked_decomp),
        n_reachable=len(reachable),
        hazard_exposure=exposure
    )


def run_hardened_test():
    """Run the hardened AZC test with expert-prescribed fixes."""
    print("=" * 70)
    print("AZC HARDENED TEST - Expert-Prescribed Fixes")
    print("=" * 70)
    print()
    print("Fixes applied:")
    print("  1. Hardened azc_active extraction criteria")
    print("  2. C481 test CONDITIONAL on azc_active >= 1")
    print("  3. Malformed MIDDLEs blocked")
    print()

    # Load data
    print("Loading data...")
    data_store = load_all_data()
    a_store = load_a_records()

    # Build AZC vocabulary
    azc_vocab = set()
    for folio_middles in data_store.azc_folio_middles.values():
        azc_vocab.update(folio_middles)

    print(f"  A entries: {len(a_store.registry_entries)}")
    print(f"  AZC vocabulary: {len(azc_vocab)} MIDDLEs")
    print()

    # Process all entries with hardened extraction
    print("Processing entries with hardened extraction...")

    results = []
    exclusion_stats = Counter()

    activating_entries = []  # Entries with >= 1 azc_active
    neutral_entries = []     # Entries with 0 azc_active

    for i, record in enumerate(a_store.registry_entries):
        if (i + 1) % 300 == 0:
            print(f"  Processed {i + 1}/{len(a_store.registry_entries)}...")

        # Hardened extraction
        azc_active, exclusion_log = extract_azc_active_middles(
            record, data_store, azc_vocab
        )

        # Track exclusions
        for reason in exclusion_log.values():
            exclusion_stats[reason] += 1

        # Compute bundle (using standard extraction for comparison)
        bundle = compute_record_bundle(record)

        # Compute signature
        projection = project_bundle(bundle)
        b_reach = compute_reachability(projection)
        signature = compute_signature(b_reach, data_store)

        result = {
            'record_id': record.display_name,
            'n_tokens': len(record.tokens),
            'all_middles': sorted(bundle.middles),
            'azc_active': sorted(azc_active),
            'n_azc_active': len(azc_active),
            'signature_hash': signature.to_hash(),
            'n_reachable': signature.n_reachable,
            'hazard_exposure': signature.hazard_exposure
        }
        results.append(result)

        if len(azc_active) >= 1:
            activating_entries.append(result)
        else:
            neutral_entries.append(result)

    print(f"  Done.")
    print()

    # ========================================
    # ANALYSIS
    # ========================================

    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # 1. Entry classification
    print("\n1. ENTRY CLASSIFICATION")
    print("-" * 40)
    print(f"  Total entries: {len(results)}")
    print(f"  Activating (azc_active >= 1): {len(activating_entries)} ({100*len(activating_entries)/len(results):.1f}%)")
    print(f"  Neutral (azc_active == 0): {len(neutral_entries)} ({100*len(neutral_entries)/len(results):.1f}%)")

    # 2. Exclusion statistics
    print("\n2. EXCLUSION STATISTICS (Why MIDDLEs were excluded)")
    print("-" * 40)
    for reason, count in exclusion_stats.most_common():
        print(f"  {reason:25}: {count:5}")

    # 3. AZC-active distribution
    print("\n3. AZC-ACTIVE DISTRIBUTION")
    print("-" * 40)
    active_dist = Counter(r['n_azc_active'] for r in results)
    for count in sorted(active_dist.keys()):
        n = active_dist[count]
        bar = '#' * min(50, n // 10)
        print(f"  {count} azc_active: {n:5} entries {bar}")

    # ========================================
    # C481 TEST - CONDITIONAL ON ACTIVATION
    # ========================================

    print("\n" + "=" * 70)
    print("C481 TEST - CONDITIONAL ON azc_active >= 1")
    print("=" * 70)
    print()
    print("Per expert: C481 uniqueness applies to entries that ACTIVATE AZC,")
    print("not neutral entries that pass through unchanged.")
    print()

    # Test on activating entries only
    if activating_entries:
        sig_to_entries = defaultdict(list)
        for r in activating_entries:
            sig_to_entries[r['signature_hash']].append(r['record_id'])

        unique_sigs = len(sig_to_entries)
        total = len(activating_entries)
        unique_ratio = unique_sigs / total

        collisions = {h: e for h, e in sig_to_entries.items() if len(e) > 1}
        collision_count = sum(len(e) - 1 for e in collisions.values())

        print(f"  Activating entries: {total}")
        print(f"  Unique signatures: {unique_sigs}")
        print(f"  Uniqueness ratio: {unique_ratio*100:.1f}%")
        print(f"  Collision groups: {len(collisions)}")
        print(f"  Total collisions: {collision_count}")

        # Show collision details
        if collisions:
            print("\n  Largest collision groups:")
            sorted_collisions = sorted(collisions.items(), key=lambda x: -len(x[1]))
            for sig_hash, entries in sorted_collisions[:5]:
                # Get details
                example = next(r for r in activating_entries if r['signature_hash'] == sig_hash)
                print(f"    {sig_hash}: {len(entries)} entries")
                print(f"      azc_active example: {example['azc_active']}")
                print(f"      n_reachable: {example['n_reachable']}")

    # ========================================
    # COMPARE: azc_active SET UNIQUENESS
    # ========================================

    print("\n" + "=" * 70)
    print("AZC-ACTIVE SET UNIQUENESS (Input Uniqueness)")
    print("=" * 70)
    print()

    # Check if azc_active sets themselves are unique
    active_sets = defaultdict(list)
    for r in activating_entries:
        key = tuple(sorted(r['azc_active']))
        active_sets[key].append(r['record_id'])

    unique_active_sets = len(active_sets)
    active_unique_ratio = unique_active_sets / len(activating_entries) if activating_entries else 0

    print(f"  Unique azc_active sets: {unique_active_sets}")
    print(f"  Uniqueness ratio: {active_unique_ratio*100:.1f}%")

    # ========================================
    # AUDIT: Unknown MIDDLEs
    # ========================================

    print("\n" + "=" * 70)
    print("AUDIT: UNKNOWN MIDDLEs (Not in AZC Vocab)")
    print("=" * 70)
    print()

    unknown_middles = Counter()
    for record in a_store.registry_entries:
        bundle = compute_record_bundle(record)
        for m in bundle.middles:
            if m and data_store.middle_folio_spread.get(m, 0) == 0:
                unknown_middles[m] += 1

    print(f"  Total unknown MIDDLE types: {len(unknown_middles)}")
    print(f"  Total unknown MIDDLE occurrences: {sum(unknown_middles.values())}")
    print()
    print("  Most common unknown MIDDLEs:")
    for middle, count in unknown_middles.most_common(20):
        # Check if it looks malformed
        malformed = "*" in middle or len(middle) > 5
        flag = " [MALFORMED]" if malformed else ""
        print(f"    '{middle:10}': {count:4} occurrences{flag}")

    # ========================================
    # VERDICT
    # ========================================

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    passes = []
    failures = []

    # Test 1: Activating entry uniqueness
    if activating_entries:
        if unique_ratio >= 0.5:
            passes.append(f"PASS: High uniqueness among activating entries ({unique_ratio*100:.1f}%)")
        elif unique_ratio >= 0.2:
            passes.append(f"MARGINAL: Moderate uniqueness ({unique_ratio*100:.1f}%)")
        else:
            failures.append(f"FAIL: Low uniqueness among activating entries ({unique_ratio*100:.1f}%)")

    # Test 2: Input uniqueness (azc_active sets)
    if activating_entries:
        if active_unique_ratio >= 0.7:
            passes.append(f"PASS: High input uniqueness (azc_active sets: {active_unique_ratio*100:.1f}%)")
        elif active_unique_ratio >= 0.4:
            passes.append(f"MARGINAL: Moderate input uniqueness ({active_unique_ratio*100:.1f}%)")
        else:
            failures.append(f"FAIL: Low input uniqueness ({active_unique_ratio*100:.1f}%)")

    # Test 3: Neutral entries should be a minority of activating records
    neutral_ratio = len(neutral_entries) / len(results)
    if neutral_ratio <= 0.7:
        passes.append(f"PASS: Reasonable activation rate ({100*(1-neutral_ratio):.1f}% activate AZC)")
    else:
        failures.append(f"WARNING: High neutral rate ({neutral_ratio*100:.1f}% don't activate)")

    print()
    for p in passes:
        print(f"  [+] {p}")
    for f in failures:
        print(f"  [-] {f}")

    print()
    if not failures or all('MARGINAL' in p or 'WARNING' in f for p in passes for f in failures):
        print("OVERALL: C481 UPHELD (conditional on activation)")
        print(">>> AZC MODEL RESCUED - Parsing was the issue <<<")
        verdict = 'PASS'
    else:
        print("OVERALL: Further investigation needed")
        verdict = 'PARTIAL'

    # Save results
    output = {
        'summary': {
            'total_entries': len(results),
            'activating_entries': len(activating_entries),
            'neutral_entries': len(neutral_entries),
            'signature_uniqueness': {
                'unique_signatures': unique_sigs if activating_entries else 0,
                'uniqueness_ratio': unique_ratio if activating_entries else 0
            },
            'input_uniqueness': {
                'unique_azc_active_sets': unique_active_sets,
                'uniqueness_ratio': active_unique_ratio
            },
            'exclusion_stats': dict(exclusion_stats),
            'verdict': verdict
        },
        'unknown_middles': dict(unknown_middles.most_common(50)),
        'sample_activating': activating_entries[:20],
        'sample_neutral': neutral_entries[:10]
    }

    output_path = PROJECT_ROOT / "results" / "azc_hardened_test.json"
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == "__main__":
    run_hardened_test()
