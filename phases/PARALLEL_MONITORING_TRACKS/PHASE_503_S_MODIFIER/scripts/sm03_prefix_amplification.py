#!/usr/bin/env python3
"""
SM-3: PREFIX amplification test

Question: Does s-modifier PREFIX make the base's MIDDLE selection more specific?

For a-base PREFIXes: compare category purity of sa vs da, ka, ta
  (all share 'a' as base character per C1218-C1219)
For h-base PREFIXes: compare sh vs ch
  (both share 'h' as base character)

"Purity" = concentration of the dominant category (max category %).
Higher purity means the PREFIX selects a narrower range of MIDDLE categories.

Prediction: s-modifier PREFIXes have HIGHER dominant-category % than
other modifiers for the same base.

Pass: s-modifier purity >= purity of >= 2/3 other modifiers for same base
      (for BOTH a-base AND h-base tests).
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier


CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']


def compute_purity(cat_counts, total):
    """Return (max_category, max_pct, entropy_proxy) for a category distribution."""
    if total == 0:
        return None, 0.0, 0.0
    best_cat = max(cat_counts, key=cat_counts.get)
    best_pct = cat_counts[best_cat] / total * 100
    # Count how many categories have > 5% presence as a secondary measure
    active_cats = sum(1 for c in CATEGORIES if cat_counts.get(c, 0) / total > 0.05)
    return best_cat, best_pct, active_cats


def print_profile(cat_counts, total, indent="      "):
    """Print 8-category profile."""
    for cat in CATEGORIES:
        n = cat_counts.get(cat, 0)
        pct = n / total * 100 if total > 0 else 0.0
        if n > 0:
            print(f"{indent}{cat:<15} {n:>5} ({pct:>5.1f}%)")


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Group tokens by PREFIX, collect category profile of their MIDDLEs
    prefix_cats = defaultdict(lambda: defaultdict(int))
    prefix_totals = defaultdict(int)
    prefix_middles = defaultdict(lambda: defaultdict(int))

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or not m.prefix:
            continue

        cat = cc.classify(m.middle)
        if cat is None:
            continue

        prefix_cats[m.prefix][cat] += 1
        prefix_totals[m.prefix] += 1
        prefix_middles[m.prefix][m.middle] += 1

    print("=" * 75)
    print("SM-3: PREFIX amplification -- Does s-modifier increase MIDDLE specificity?")
    print("=" * 75)
    print()

    # ---- Define test groups ----
    # a-base PREFIXes: sa, da, ka, ta (all end in 'a')
    # h-base PREFIXes: sh, ch (all end in 'h')
    test_groups = [
        {
            'name': 'a-base',
            's_prefix': 'sa',
            'other_prefixes': ['da', 'ka', 'ta'],
            'base': 'a',
        },
        {
            'name': 'h-base',
            's_prefix': 'sh',
            'other_prefixes': ['ch'],
            'base': 'h',
        },
    ]

    group_pass_count = 0

    for group in test_groups:
        print("-" * 75)
        print(f"TEST GROUP: {group['name']} PREFIXes (base = '{group['base']}')")
        print("-" * 75)
        print()

        s_pfx = group['s_prefix']
        s_total = prefix_totals.get(s_pfx, 0)

        if s_total == 0:
            print(f"  {s_pfx}: NOT FOUND in corpus -- SKIP GROUP")
            print()
            continue

        s_primary, s_purity, s_active = compute_purity(prefix_cats[s_pfx], s_total)

        # Print s-modifier profile
        print(f"  s-modifier PREFIX: {s_pfx} (N={s_total})")
        print(f"    Dominant: {s_primary} ({s_purity:.1f}%)")
        print(f"    Active categories (>5%): {s_active}")
        print(f"    Full profile:")
        print_profile(prefix_cats[s_pfx], s_total)
        print(f"    Unique MIDDLEs: {len(prefix_middles[s_pfx])}")
        # Show top 5 MIDDLEs
        top_mids = sorted(prefix_middles[s_pfx].items(), key=lambda x: -x[1])[:5]
        for mid, cnt in top_mids:
            cat = cc.classify(mid)
            print(f"      {mid:<12} {cnt:>4}  ({cat})")
        print()

        # Print other modifier profiles
        beats_count = 0
        other_count = 0

        for other_pfx in group['other_prefixes']:
            o_total = prefix_totals.get(other_pfx, 0)
            if o_total == 0:
                print(f"  Other PREFIX: {other_pfx} -- NOT FOUND")
                continue

            other_count += 1
            o_primary, o_purity, o_active = compute_purity(prefix_cats[other_pfx], o_total)

            s_beats = s_purity >= o_purity
            if s_beats:
                beats_count += 1

            print(f"  Other PREFIX: {other_pfx} (N={o_total})")
            print(f"    Dominant: {o_primary} ({o_purity:.1f}%)")
            print(f"    Active categories (>5%): {o_active}")
            print(f"    Full profile:")
            print_profile(prefix_cats[other_pfx], o_total)
            print(f"    Unique MIDDLEs: {len(prefix_middles[other_pfx])}")
            top_mids = sorted(prefix_middles[other_pfx].items(), key=lambda x: -x[1])[:5]
            for mid, cnt in top_mids:
                cat = cc.classify(mid)
                print(f"      {mid:<12} {cnt:>4}  ({cat})")
            print(f"    s-modifier ({s_pfx}) purity {s_purity:.1f}% vs {other_pfx} purity {o_purity:.1f}%:"
                  f" {'s HIGHER' if s_beats else 'OTHER HIGHER'}")
            print()

        # Group verdict
        if other_count == 0:
            print(f"  GROUP {group['name']}: No other PREFIXes found -- SKIP")
        else:
            # For a-base: need >= 2/3; for h-base: need >= 1/1
            # General rule: s-modifier purity >= purity of >= 2/3 others (at least 2 of 3 for a-base)
            if group['name'] == 'a-base':
                needed = 2
            else:
                needed = 1  # h-base only has 1 other (ch)

            group_passes = beats_count >= needed
            if group_passes:
                group_pass_count += 1

            print(f"  GROUP {group['name']} RESULT: s-modifier beats {beats_count}/{other_count} others"
                  f" (needed >= {needed}): {'PASS' if group_passes else 'FAIL'}")
        print()

    # ---- Cross-group comparison table ----
    print("-" * 75)
    print("COMPARISON TABLE: All tested PREFIXes")
    print("-" * 75)
    print()

    all_prefixes = set()
    for g in test_groups:
        all_prefixes.add(g['s_prefix'])
        all_prefixes.update(g['other_prefixes'])

    header = f"{'PREFIX':<8} {'N':>6} {'Dominant':<15} {'Purity%':>8} {'Active':>7} {'Unique MIDs':>11}"
    print(header)
    print("-" * len(header))

    for pfx in sorted(all_prefixes, key=lambda p: -prefix_totals.get(p, 0)):
        total = prefix_totals.get(pfx, 0)
        if total == 0:
            print(f"  {pfx:<6} {0:>6} {'N/A':<15} {'N/A':>8} {'N/A':>7} {'N/A':>11}")
            continue
        primary, purity, active = compute_purity(prefix_cats[pfx], total)
        is_s = pfx.startswith('s')
        marker = " *s*" if is_s else ""
        print(f"  {pfx:<6} {total:>6} {primary:<15} {purity:>7.1f}% {active:>7} {len(prefix_middles[pfx]):>11}{marker}")

    # ---- VERDICT ----
    print()
    print("=" * 75)
    print("VERDICT")
    print("=" * 75)
    print()

    # Both groups must pass
    overall = group_pass_count >= 2
    print(f"  Groups passing: {group_pass_count}/2")
    print(f"  Requirement: BOTH a-base AND h-base must pass")
    print()
    print(f"  OVERALL: {'PASS' if overall else 'FAIL'}")
    if overall:
        print("  s-modifier PREFIXes produce more category-specific MIDDLE selection")
    else:
        print("  s-modifier PREFIXes do NOT consistently amplify category specificity")


if __name__ == '__main__':
    main()
