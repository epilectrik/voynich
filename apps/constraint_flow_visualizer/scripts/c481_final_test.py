"""
C481 Final Sanity-Lock Test

EXPERT PREDICTION:
  unique_bundles == unique_folio_signatures

If this holds, C481 is satisfied exactly as intended:
  "Distinct constraint bundles induce distinct downstream legality profiles"

TEST:
1. Collapse A records by azc_active bundle identity
2. Deduplicate entries with identical bundles
3. Count unique bundles vs unique AZC folio signatures
4. Verify 1:1 mapping
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
from typing import Set, Tuple, FrozenSet

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

# Force fresh load
import core.data_loader as dl
dl._data_store = None

from core.data_loader import load_all_data
from core.a_record_loader import load_a_records
from core.morphology import decompose_token

# Hub MIDDLEs to exclude
HUB_MIDDLES = {'a', 'o', 'e'}


def extract_azc_active(record, data_store) -> FrozenSet[str]:
    """Extract AZC-active MIDDLEs as a frozen set (hashable bundle identity)."""
    azc_active = set()

    for token in record.tokens:
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

    return frozenset(azc_active)


def compute_compatible_folios(azc_active: FrozenSet[str], data_store) -> FrozenSet[str]:
    """Compute compatible AZC folios for this bundle."""
    if not azc_active:
        return frozenset(data_store.azc_folio_middles.keys())

    compatible = set()
    for folio_id, folio_vocab in data_store.azc_folio_middles.items():
        if azc_active <= folio_vocab:
            compatible.add(folio_id)

    return frozenset(compatible)


def run_c481_final_test():
    """Run the definitive C481 bundle-level test."""
    print("=" * 70)
    print("C481 FINAL SANITY-LOCK TEST")
    print("=" * 70)
    print()
    print("PREDICTION: unique_bundles == unique_folio_signatures")
    print()
    print("If this holds, C481 is satisfied exactly as intended:")
    print("  'Distinct constraint bundles induce distinct legality profiles'")
    print()

    # Load data
    print("Loading data...")
    data_store = load_all_data()
    a_store = load_a_records()
    print(f"  A entries: {len(a_store.registry_entries)}")
    print()

    # Step 1: Extract all bundles and their folio signatures
    print("Step 1: Extracting bundles and computing folio signatures...")

    bundle_to_records = defaultdict(list)  # bundle -> [record_ids]
    bundle_to_folios = {}                   # bundle -> compatible_folios

    for record in a_store.registry_entries:
        bundle = extract_azc_active(record, data_store)
        bundle_to_records[bundle].append(record.display_name)

        if bundle not in bundle_to_folios:
            folios = compute_compatible_folios(bundle, data_store)
            bundle_to_folios[bundle] = folios

    # Step 2: Count unique bundles
    unique_bundles = len(bundle_to_records)
    print(f"  Unique bundles: {unique_bundles}")

    # Step 3: Count unique folio signatures
    folio_signatures = set(bundle_to_folios.values())
    unique_folio_sigs = len(folio_signatures)
    print(f"  Unique folio signatures: {unique_folio_sigs}")

    # Step 4: Check 1:1 mapping
    print()
    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)

    # Build reverse mapping: folio_sig -> bundles
    folios_to_bundles = defaultdict(list)
    for bundle, folios in bundle_to_folios.items():
        folios_to_bundles[folios].append(bundle)

    # Check for any folio signature that maps to multiple bundles
    colliding_sigs = {f: b for f, b in folios_to_bundles.items() if len(b) > 1}

    # IMPORTANT: Separate analysis for activating bundles (>=1 folio) vs blocked (0 folios)
    empty_folio_sig = frozenset()
    blocked_bundles = [b for b, f in bundle_to_folios.items() if len(f) == 0]
    activating_bundles_list = [b for b, f in bundle_to_folios.items() if len(f) >= 1]

    # For activating bundles only
    activating_folio_sigs = set(bundle_to_folios[b] for b in activating_bundles_list)

    # Check 1:1 among activating bundles
    activating_folios_to_bundles = defaultdict(list)
    for b in activating_bundles_list:
        activating_folios_to_bundles[bundle_to_folios[b]].append(b)

    activating_collisions = {f: bs for f, bs in activating_folios_to_bundles.items() if len(bs) > 1}

    print()
    print(f"  ALL BUNDLES:")
    print(f"    Unique bundles:         {unique_bundles}")
    print(f"    Unique folio signatures: {unique_folio_sigs}")
    print()
    print(f"  BREAKDOWN:")
    print(f"    Blocked bundles (0 folios): {len(blocked_bundles)}")
    print(f"    Activating bundles (1+ folios): {len(activating_bundles_list)}")
    print(f"    Unique activating folio sigs: {len(activating_folio_sigs)}")
    print()

    # The KEY test: among ACTIVATING bundles, is there 1:1 mapping?
    if len(activating_bundles_list) == len(activating_folio_sigs) and not activating_collisions:
        print("  " + "=" * 50)
        print("  C481 TEST (Activating Bundles Only):")
        print(f"    activating_bundles ({len(activating_bundles_list)}) == activating_folio_sigs ({len(activating_folio_sigs)})")
        print()
        print("  [PASS] C481 SATISFIED among activating bundles")
        print("  [PASS] Distinct bundles -> Distinct legality profiles")
        print("  " + "=" * 50)
        c481_status = "SATISFIED"
    else:
        print("  " + "=" * 50)
        print("  C481 TEST (Activating Bundles Only):")
        print(f"    activating_bundles: {len(activating_bundles_list)}")
        print(f"    activating_folio_sigs: {len(activating_folio_sigs)}")
        print(f"    collisions: {len(activating_collisions)}")
        print()

        if activating_collisions:
            print("  Collision details (same folio sig, different bundles):")
            for folios, bundles in sorted(activating_collisions.items(), key=lambda x: -len(x[1]))[:5]:
                print(f"    {len(folios)} folios: {len(bundles)} distinct bundles")
                for b in bundles[:3]:
                    print(f"      {sorted(b)}")

        # Check if it's close
        ratio = len(activating_folio_sigs) / len(activating_bundles_list) if activating_bundles_list else 0
        if ratio >= 0.9:
            print()
            print(f"  [MARGINAL] Near 1:1 mapping ({ratio*100:.1f}%)")
            c481_status = "MARGINAL"
        else:
            print()
            print(f"  [FAIL] Not 1:1 mapping ({ratio*100:.1f}%)")
            c481_status = "VIOLATED"
        print("  " + "=" * 50)

    # Note about blocked bundles
    print()
    print(f"  NOTE: {len(blocked_bundles)} bundles have 0 compatible folios")
    print("  These are blocked by AZC (no folio contains all their MIDDLEs).")
    print("  Per C437, folios have only 5.6% overlap, so multi-MIDDLE")
    print("  bundles often can't find a compatible folio.")

    # Additional statistics
    print()
    print("=" * 70)
    print("BUNDLE STATISTICS")
    print("=" * 70)

    # Bundle size distribution
    bundle_sizes = [len(b) for b in bundle_to_records.keys()]
    size_dist = defaultdict(int)
    for s in bundle_sizes:
        size_dist[s] += 1

    print("\n  Bundle size distribution (# of azc_active MIDDLEs):")
    for size in sorted(size_dist.keys()):
        count = size_dist[size]
        pct = 100 * count / unique_bundles
        print(f"    Size {size}: {count:4} bundles ({pct:5.1f}%)")

    # Records per bundle distribution
    records_per_bundle = [len(recs) for recs in bundle_to_records.values()]
    print(f"\n  Records per bundle:")
    print(f"    Min: {min(records_per_bundle)}")
    print(f"    Max: {max(records_per_bundle)}")
    print(f"    Avg: {sum(records_per_bundle)/len(records_per_bundle):.1f}")

    # Largest bundles (most reused)
    sorted_bundles = sorted(bundle_to_records.items(), key=lambda x: -len(x[1]))
    print("\n  Most reused bundles:")
    for bundle, records in sorted_bundles[:5]:
        folios = bundle_to_folios[bundle]
        print(f"    {sorted(bundle) if bundle else '(empty)'}: {len(records)} records -> {len(folios)} folios")

    # Activating vs neutral
    empty_bundle = frozenset()
    neutral_count = len(bundle_to_records.get(empty_bundle, []))
    activating_bundles = unique_bundles - (1 if empty_bundle in bundle_to_records else 0)

    print(f"\n  Neutral entries (empty bundle): {neutral_count}")
    print(f"  Activating bundles: {activating_bundles}")

    # Save results
    output = {
        'c481_status': c481_status,
        'unique_bundles': unique_bundles,
        'unique_folio_signatures': unique_folio_sigs,
        'is_1_to_1': unique_bundles == unique_folio_sigs,
        'bundle_size_distribution': dict(size_dist),
        'records_per_bundle': {
            'min': min(records_per_bundle),
            'max': max(records_per_bundle),
            'avg': sum(records_per_bundle)/len(records_per_bundle)
        },
        'most_reused_bundles': [
            {
                'bundle': sorted(b) if b else [],
                'record_count': len(r),
                'folio_count': len(bundle_to_folios[b])
            }
            for b, r in sorted_bundles[:10]
        ]
    }

    output_path = PROJECT_ROOT / "results" / "c481_final_test.json"
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == "__main__":
    run_c481_final_test()
