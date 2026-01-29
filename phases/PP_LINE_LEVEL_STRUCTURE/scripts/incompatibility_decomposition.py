"""
Quick analysis: decompose MIDDLE incompatibility into
folio-disjoint (trivial) vs genuine within-folio avoidance.
"""

import sys
import numpy as np
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import RecordAnalyzer


def main():
    analyzer = RecordAnalyzer()
    folios = analyzer.get_folios()

    folio_mid_sets = {}
    folio_line_mids = {}

    for fol in folios:
        records = analyzer.analyze_folio(fol)
        all_mids = set()
        line_sets = []
        for rec in records:
            line_mids = set()
            for t in rec.tokens:
                if t.is_pp and t.middle:
                    all_mids.add(t.middle)
                    line_mids.add(t.middle)
            line_sets.append(line_mids)
        folio_mid_sets[fol] = all_mids
        folio_line_mids[fol] = line_sets

    all_mids = set()
    for s in folio_mid_sets.values():
        all_mids.update(s)

    print(f"Total unique PP MIDDLEs: {len(all_mids)}")
    total_possible = len(all_mids) * (len(all_mids) - 1) // 2
    print(f"Total possible pairs: {total_possible}")

    # Per-MIDDLE folio membership
    mid_to_folios = defaultdict(set)
    for fol, mids in folio_mid_sets.items():
        for m in mids:
            mid_to_folios[m].add(fol)

    # Folio-coexisting pairs: share at least one folio
    cofolio_pairs = set()
    for fol, mids in folio_mid_sets.items():
        mids_sorted = sorted(mids)
        for i in range(len(mids_sorted)):
            for j in range(i + 1, len(mids_sorted)):
                cofolio_pairs.add((mids_sorted[i], mids_sorted[j]))

    folio_disjoint = total_possible - len(cofolio_pairs)
    print(f"Folio-disjoint pairs (never in same folio): {folio_disjoint} ({folio_disjoint / total_possible * 100:.1f}%)")
    print(f"Folio-coexisting pairs: {len(cofolio_pairs)} ({len(cofolio_pairs) / total_possible * 100:.1f}%)")

    # Line co-occurring pairs
    line_cooccur = set()
    for fol, line_sets in folio_line_mids.items():
        for ls in line_sets:
            if len(ls) < 2:
                continue
            ls_sorted = sorted(ls)
            for i in range(len(ls_sorted)):
                for j in range(i + 1, len(ls_sorted)):
                    line_cooccur.add((ls_sorted[i], ls_sorted[j]))

    within_folio_avoidance = len(cofolio_pairs) - len(line_cooccur)

    print(f"Line co-occurring pairs: {len(line_cooccur)} ({len(line_cooccur) / total_possible * 100:.1f}%)")
    print(f"Within-folio avoidance: {within_folio_avoidance} ({within_folio_avoidance / total_possible * 100:.1f}%)")

    print()
    print("=== DECOMPOSITION ===")
    print(f"Total pairs: {total_possible} (100%)")
    print(f"  Folio-disjoint (trivially incompatible): {folio_disjoint} ({folio_disjoint / total_possible * 100:.1f}%)")
    print(f"  Within-folio avoidance (genuine line-level): {within_folio_avoidance} ({within_folio_avoidance / total_possible * 100:.1f}%)")
    print(f"  Line co-occurring (legal): {len(line_cooccur)} ({len(line_cooccur) / total_possible * 100:.1f}%)")

    print()
    print("Among folio-coexisting pairs:")
    pct_cooccur = len(line_cooccur) / len(cofolio_pairs) * 100 if cofolio_pairs else 0
    pct_avoid = within_folio_avoidance / len(cofolio_pairs) * 100 if cofolio_pairs else 0
    print(f"  Co-occur on line: {len(line_cooccur)} ({pct_cooccur:.1f}%)")
    print(f"  Avoid within folio: {within_folio_avoidance} ({pct_avoid:.1f}%)")

    print()
    print("=== MIDDLE DISTRIBUTION ACROSS FOLIOS ===")
    fol_counts = np.array([len(mid_to_folios[m]) for m in all_mids])
    print(f"Median folio count per MIDDLE: {np.median(fol_counts):.0f}")
    print(f"Mean: {np.mean(fol_counts):.1f}, Min: {np.min(fol_counts)}, Max: {np.max(fol_counts)}")
    print(f"  1 folio only: {np.sum(fol_counts == 1)} ({np.sum(fol_counts == 1) / len(fol_counts) * 100:.1f}%)")
    print(f"  2-5 folios: {np.sum((fol_counts >= 2) & (fol_counts <= 5))} ({np.sum((fol_counts >= 2) & (fol_counts <= 5)) / len(fol_counts) * 100:.1f}%)")
    print(f"  6-20 folios: {np.sum((fol_counts >= 6) & (fol_counts <= 20))} ({np.sum((fol_counts >= 6) & (fol_counts <= 20)) / len(fol_counts) * 100:.1f}%)")
    print(f"  21+ folios: {np.sum(fol_counts >= 21)} ({np.sum(fol_counts >= 21) / len(fol_counts) * 100:.1f}%)")

    # How big are folio PP pools?
    pool_sizes = np.array([len(s) for s in folio_mid_sets.values()])
    print()
    print("=== FOLIO PP POOL SIZES ===")
    print(f"Median: {np.median(pool_sizes):.0f}")
    print(f"Mean: {np.mean(pool_sizes):.1f}, Min: {np.min(pool_sizes)}, Max: {np.max(pool_sizes)}")

    # If pools are small, what fraction of within-pool pairs co-occur on a line?
    within_pool_pairs_total = 0
    within_pool_cooccur = 0
    for fol in folios:
        mids = sorted(folio_mid_sets[fol])
        pool_pairs = set()
        for i in range(len(mids)):
            for j in range(i + 1, len(mids)):
                pool_pairs.add((mids[i], mids[j]))
        within_pool_pairs_total += len(pool_pairs)

        line_pairs_fol = set()
        for ls in folio_line_mids[fol]:
            if len(ls) < 2:
                continue
            ls_sorted = sorted(ls)
            for i in range(len(ls_sorted)):
                for j in range(i + 1, len(ls_sorted)):
                    line_pairs_fol.add((ls_sorted[i], ls_sorted[j]))

        within_pool_cooccur += len(pool_pairs & line_pairs_fol)

    # Note: within_pool_pairs_total counts same pair multiple times if in multiple folios
    print()
    print("=== WITHIN-FOLIO CO-OCCURRENCE RATE ===")
    print(f"Total within-pool pair-folio instances: {within_pool_pairs_total}")
    print(f"Of those, co-occur on a line: {within_pool_cooccur} ({within_pool_cooccur / within_pool_pairs_total * 100:.1f}%)")
    print(f"Avoid within own folio: {within_pool_pairs_total - within_pool_cooccur} ({(within_pool_pairs_total - within_pool_cooccur) / within_pool_pairs_total * 100:.1f}%)")


if __name__ == '__main__':
    main()
