"""
AZC Folio-Level Signature Test

INSIGHT: Previous test showed 39.3% input uniqueness but only 5.2% output uniqueness.
This means different azc_active inputs produce the same class reachability.

HYPOTHESIS: The constraint signature should include WHICH AZC FOLIOS are activated,
not just the grammar outcome. Per C481, the survivor-set should capture the
folio activation pattern, not just reachable classes.

This test computes signatures that include:
1. Which AZC folios are compatible
2. The effective vocabulary (union of compatible folio vocabs)
3. The grammar state (reachable classes)
"""

import sys
import json
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
from typing import Set, Dict, List, Tuple, FrozenSet

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

# Hub MIDDLEs - exclude from azc_active
HUB_MIDDLES = {'a', 'o', 'e'}


def extract_azc_active(record, data_store) -> Set[str]:
    """Extract AZC-active MIDDLEs (restricted, not infrastructure)."""
    azc_active = set()

    for token in record.tokens:
        # Skip very short tokens (infrastructure)
        if len(token) <= 2:
            continue

        morph = decompose_token(token)
        middle = morph.middle if morph.middle else ""

        if not middle or middle in HUB_MIDDLES:
            continue

        if '*' in middle or len(middle) > 6:
            continue

        spread = data_store.middle_folio_spread.get(middle, 0)
        if 1 <= spread <= 3:
            azc_active.add(middle)

    return azc_active


def compute_compatible_folios(azc_active: Set[str], data_store) -> Set[str]:
    """
    Compute which AZC folios are compatible with this azc_active set.

    Per C442, C470: A folio is compatible if all restricted MIDDLEs are in its vocab.
    """
    if not azc_active:
        # No restricted MIDDLEs = all folios compatible
        return set(data_store.azc_folio_middles.keys())

    compatible = set()
    for folio_id, folio_vocab in data_store.azc_folio_middles.items():
        # Check if all azc_active MIDDLEs are in this folio's vocabulary
        if azc_active <= folio_vocab:
            compatible.add(folio_id)

    return compatible


def compute_folio_signature(
    azc_active: Set[str],
    compatible_folios: Set[str],
    data_store
) -> str:
    """
    Compute a signature that captures folio-level activation.

    This is the TRUE survivor-set signature per C481.
    """
    # Sort for deterministic hashing
    active_tuple = tuple(sorted(azc_active))
    folio_tuple = tuple(sorted(compatible_folios))

    # The signature is the combination of:
    # 1. Which restricted MIDDLEs are active
    # 2. Which AZC folios are compatible
    key = (active_tuple, folio_tuple)
    return hashlib.md5(str(key).encode()).hexdigest()[:12]


def run_folio_signature_test():
    """Test C481 using folio-level signatures."""
    print("=" * 70)
    print("AZC FOLIO-LEVEL SIGNATURE TEST")
    print("=" * 70)
    print()
    print("Testing C481 with folio activation included in signature.")
    print("Signature = (azc_active_middles, compatible_folios)")
    print()

    # Load data
    print("Loading data...")
    data_store = load_all_data()
    a_store = load_a_records()
    print(f"  A entries: {len(a_store.registry_entries)}")
    print(f"  AZC folios: {len(data_store.azc_folio_middles)}")
    print()

    # Process entries
    print("Computing folio-level signatures...")

    results = []
    activating = []
    neutral = []

    for record in a_store.registry_entries:
        azc_active = extract_azc_active(record, data_store)
        compatible = compute_compatible_folios(azc_active, data_store)
        signature = compute_folio_signature(azc_active, compatible, data_store)

        result = {
            'record_id': record.display_name,
            'azc_active': sorted(azc_active),
            'n_azc_active': len(azc_active),
            'compatible_folios': sorted(compatible),
            'n_compatible': len(compatible),
            'signature': signature
        }
        results.append(result)

        if len(azc_active) >= 1:
            activating.append(result)
        else:
            neutral.append(result)

    print(f"  Activating: {len(activating)} ({100*len(activating)/len(results):.1f}%)")
    print(f"  Neutral: {len(neutral)} ({100*len(neutral)/len(results):.1f}%)")
    print()

    # ========================================
    # ANALYSIS
    # ========================================

    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # 1. Folio compatibility distribution
    print("\n1. FOLIO COMPATIBILITY DISTRIBUTION")
    print("-" * 40)

    compat_dist = Counter(r['n_compatible'] for r in activating)
    print("  Among activating entries:")
    for n in sorted(compat_dist.keys()):
        count = compat_dist[n]
        pct = 100 * count / len(activating)
        bar = '#' * min(40, int(pct))
        print(f"    {n:2} compatible folios: {count:4} ({pct:5.1f}%) {bar}")

    # 2. Signature uniqueness (activating only)
    print("\n2. SIGNATURE UNIQUENESS (Activating Entries)")
    print("-" * 40)

    sig_to_entries = defaultdict(list)
    for r in activating:
        sig_to_entries[r['signature']].append(r['record_id'])

    unique_sigs = len(sig_to_entries)
    unique_ratio = unique_sigs / len(activating) if activating else 0

    collisions = {s: e for s, e in sig_to_entries.items() if len(e) > 1}
    collision_count = sum(len(e) - 1 for e in collisions.values())

    print(f"  Activating entries: {len(activating)}")
    print(f"  Unique signatures: {unique_sigs}")
    print(f"  Uniqueness ratio: {unique_ratio*100:.1f}%")
    print(f"  Collision groups: {len(collisions)}")
    print(f"  Total collisions: {collision_count}")

    # 3. Compare to previous tests
    print("\n3. COMPARISON TO PREVIOUS TESTS")
    print("-" * 40)
    print(f"  Original (class-only): 1.9% uniqueness")
    print(f"  Parsing fix (azc_active): 15.7% uniqueness")
    print(f"  Conditional (activating): 5.2% uniqueness")
    print(f"  Folio-level: {unique_ratio*100:.1f}% uniqueness")

    if unique_ratio > 0.052:
        improvement = unique_ratio / 0.052
        print(f"  >>> {improvement:.1f}x improvement over conditional test <<<")

    # 4. Collision analysis
    print("\n4. LARGEST COLLISION GROUPS")
    print("-" * 40)

    sorted_collisions = sorted(collisions.items(), key=lambda x: -len(x[1]))
    for sig, entries in sorted_collisions[:5]:
        example = next(r for r in activating if r['signature'] == sig)
        print(f"  {sig}: {len(entries)} entries")
        print(f"    azc_active: {example['azc_active']}")
        print(f"    compatible folios: {example['n_compatible']}")

    # 5. Entries with exactly 1 compatible folio
    print("\n5. ENTRIES WITH 1 COMPATIBLE FOLIO (Expected High Uniqueness)")
    print("-" * 40)

    one_folio = [r for r in activating if r['n_compatible'] == 1]
    if one_folio:
        one_sigs = defaultdict(list)
        for r in one_folio:
            one_sigs[r['signature']].append(r['record_id'])

        one_unique = len(one_sigs)
        one_ratio = one_unique / len(one_folio)

        print(f"  Entries with 1 folio: {len(one_folio)}")
        print(f"  Unique signatures: {one_unique}")
        print(f"  Uniqueness ratio: {one_ratio*100:.1f}%")
    else:
        print("  No entries with exactly 1 compatible folio")

    # ========================================
    # VERDICT
    # ========================================

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    passes = []
    failures = []

    if unique_ratio >= 0.5:
        passes.append(f"PASS: High folio-level uniqueness ({unique_ratio*100:.1f}%)")
    elif unique_ratio >= 0.2:
        passes.append(f"MARGINAL: Moderate folio-level uniqueness ({unique_ratio*100:.1f}%)")
    else:
        failures.append(f"FAIL: Low folio-level uniqueness ({unique_ratio*100:.1f}%)")

    # Check if entries with 1 folio have high uniqueness
    if one_folio:
        if one_ratio >= 0.8:
            passes.append(f"PASS: Single-folio entries highly unique ({one_ratio*100:.1f}%)")
        elif one_ratio >= 0.5:
            passes.append(f"MARGINAL: Single-folio entries moderately unique ({one_ratio*100:.1f}%)")
        else:
            failures.append(f"NOTE: Single-folio entries not fully unique ({one_ratio*100:.1f}%)")

    print()
    for p in passes:
        print(f"  [+] {p}")
    for f in failures:
        print(f"  [-] {f}")

    # Save results
    output = {
        'summary': {
            'total': len(results),
            'activating': len(activating),
            'neutral': len(neutral),
            'unique_signatures': unique_sigs,
            'uniqueness_ratio': unique_ratio,
            'compatibility_distribution': dict(compat_dist)
        },
        'collision_groups': [
            {'signature': s, 'count': len(e), 'entries': e[:10]}
            for s, e in sorted_collisions[:10]
        ],
        'sample_results': activating[:30]
    }

    output_path = PROJECT_ROOT / "results" / "azc_folio_signature_test.json"
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == "__main__":
    run_folio_signature_test()
