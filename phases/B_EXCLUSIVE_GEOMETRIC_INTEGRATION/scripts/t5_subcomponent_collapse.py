#!/usr/bin/env python3
"""
T5: Sub-Component Collapse
B_EXCLUSIVE_GEOMETRIC_INTEGRATION phase

Using atom decomposition: can B-exclusive MIDDLEs be decomposed to A PP atoms?
What percentage share atoms with A manifold?
If >=80-90% → superstring variants of same discrimination axes.
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def get_a_middles():
    tx = Transcript()
    morph = Morphology()
    a_set = set()
    a_counts = Counter()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            a_set.add(m.middle)
            a_counts[m.middle] += 1
    return a_set, a_counts


def get_b_middles():
    tx = Transcript()
    morph = Morphology()
    b_counts = Counter()
    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            b_counts[m.middle] += 1
    return b_counts


def decompose_middle(middle, atoms):
    """Find all A-space atoms contained in a MIDDLE.

    Returns maximal (non-redundant) atoms.
    """
    found = []
    for atom in atoms:
        if atom in middle and atom != middle and len(atom) >= 2:
            found.append(atom)

    if len(found) <= 1:
        return found

    # Keep maximal (remove substrings of longer matches)
    found.sort(key=len, reverse=True)
    maximal = []
    for atom in found:
        if not any(atom in longer for longer in maximal):
            maximal.append(atom)
    return maximal


def compute_coverage(middle, atoms):
    """Compute what fraction of the MIDDLE string is covered by A-space atoms."""
    if not atoms:
        return 0.0

    # Greedy coverage: mark positions covered by atoms
    covered = [False] * len(middle)
    for atom in sorted(atoms, key=len, reverse=True):
        start = 0
        while True:
            pos = middle.find(atom, start)
            if pos == -1:
                break
            for i in range(pos, pos + len(atom)):
                covered[i] = True
            start = pos + 1

    return sum(covered) / len(middle)


def main():
    print("=" * 60)
    print("T5: Sub-Component Collapse")
    print("=" * 60)

    # Setup
    print("\n[1] Loading inventories...")
    a_set, a_counts = get_a_middles()
    b_counts = get_b_middles()

    all_b = set(b_counts.keys())
    shared = all_b & a_set
    exclusive = all_b - a_set

    print(f"  A MIDDLEs: {len(a_set)}")
    print(f"  B MIDDLEs: {len(all_b)} (shared: {len(shared)}, exclusive: {len(exclusive)})")

    # Build atom sets at different thresholds
    a_all = {m for m in a_set if len(m) >= 2}
    a_core = {m for m in a_set if len(m) <= 3 and len(m) >= 2}  # Short core atoms
    a_frequent = {m for m in a_set if a_counts[m] >= 10 and len(m) >= 2}

    print(f"\n  Atom sets:")
    print(f"  All A (len>=2): {len(a_all)}")
    print(f"  Core A (len 2-3): {len(a_core)}")
    print(f"  Frequent A (count>=10): {len(a_frequent)}")

    # Step 2: Decompose all B-exclusive MIDDLEs
    print("\n[2] Decomposing B-exclusive MIDDLEs...")

    results_by_threshold = {}
    for label, atom_set in [('all_a', a_all), ('core_a', a_core), ('frequent_a', a_frequent)]:
        decomp_results = []
        for mid in sorted(exclusive):
            atoms = decompose_middle(mid, atom_set)
            coverage = compute_coverage(mid, atoms)
            decomp_results.append({
                'middle': mid,
                'atoms': atoms,
                'n_atoms': len(atoms),
                'coverage': coverage,
                'has_atoms': len(atoms) > 0,
            })

        n_with = sum(1 for d in decomp_results if d['has_atoms'])
        coverages = [d['coverage'] for d in decomp_results]
        mean_cov = np.mean(coverages)
        n_high_cov = sum(1 for c in coverages if c >= 0.8)

        results_by_threshold[label] = {
            'n_atoms_available': len(atom_set),
            'n_with_atoms': n_with,
            'pct_with_atoms': n_with / len(exclusive),
            'mean_coverage': mean_cov,
            'n_high_coverage': n_high_cov,
            'pct_high_coverage': n_high_cov / len(exclusive),
        }

        print(f"\n  [{label}] ({len(atom_set)} atoms):")
        print(f"    MIDDLEs with atoms: {n_with}/{len(exclusive)} "
              f"({n_with/len(exclusive):.1%})")
        print(f"    Mean string coverage: {mean_cov:.1%}")
        print(f"    High coverage (>=80%): {n_high_cov}/{len(exclusive)} "
              f"({n_high_cov/len(exclusive):.1%})")

    # Step 3: Detailed decomposition with all_a atoms
    print("\n[3] Detailed decomposition analysis (all A atoms)...")
    full_decomp = []
    for mid in sorted(exclusive):
        atoms = decompose_middle(mid, a_all)
        coverage = compute_coverage(mid, atoms)
        full_decomp.append({
            'middle': mid,
            'atoms': atoms,
            'n_atoms': len(atoms),
            'coverage': coverage,
            'b_count': b_counts[mid],
        })

    # Atom count distribution
    atom_count_dist = Counter(d['n_atoms'] for d in full_decomp)
    print(f"  Atom count distribution: {dict(sorted(atom_count_dist.items()))}")

    # Coverage distribution
    cov_bins = [(0, 0, 'none'), (0.01, 0.5, '1-50%'), (0.5, 0.8, '50-80%'),
                (0.8, 1.01, '80-100%')]
    print(f"\n  Coverage distribution:")
    for lo, hi, label in cov_bins:
        n = sum(1 for d in full_decomp if lo <= d['coverage'] < hi)
        print(f"    {label:>8s}: {n:>4d} ({n/len(full_decomp):.1%})")

    # Step 4: What atoms are most common in B-exclusive MIDDLEs?
    print("\n[4] Most common A-space atoms in B-exclusive MIDDLEs...")
    atom_usage = Counter()
    for d in full_decomp:
        for atom in d['atoms']:
            atom_usage[atom] += 1

    print(f"  Top 15 atoms:")
    for atom, count in atom_usage.most_common(15):
        print(f"    {atom:>6s}: {count:>4d} ({count/len(exclusive):.1%} of exclusives)")

    # Step 5: Residual after atom removal — what's left?
    print("\n[5] Residual characters after atom removal...")
    residual_chars = Counter()
    n_fully_covered = 0
    n_partial = 0
    n_none = 0

    for d in full_decomp:
        cov = d['coverage']
        if cov >= 0.99:
            n_fully_covered += 1
        elif cov > 0:
            n_partial += 1
        else:
            n_none += 1

        # Find uncovered characters
        mid = d['middle']
        covered = [False] * len(mid)
        for atom in sorted(d['atoms'], key=len, reverse=True):
            start = 0
            while True:
                pos = mid.find(atom, start)
                if pos == -1:
                    break
                for i in range(pos, pos + len(atom)):
                    covered[i] = True
                start = pos + 1

        for i, c in enumerate(mid):
            if not covered[i]:
                residual_chars[c] += 1

    print(f"  Fully covered (>=99%): {n_fully_covered}")
    print(f"  Partially covered: {n_partial}")
    print(f"  No coverage: {n_none}")

    print(f"\n  Residual (uncovered) characters:")
    for ch, count in residual_chars.most_common(15):
        print(f"    '{ch}': {count}")

    # Step 6: Examples
    print("\n[6] Example decompositions...")
    # Show 10 high-frequency exclusives
    by_freq = sorted(full_decomp, key=lambda d: d['b_count'], reverse=True)
    print(f"  Top 10 most frequent B-exclusive MIDDLEs:")
    for d in by_freq[:10]:
        atoms_str = '+'.join(d['atoms']) if d['atoms'] else '(none)'
        print(f"    {d['middle']:>12s} (count={d['b_count']:>3d}): "
              f"atoms=[{atoms_str}], coverage={d['coverage']:.0%}")

    # Show 5 with zero atoms
    no_atoms = [d for d in full_decomp if d['n_atoms'] == 0]
    if no_atoms:
        print(f"\n  B-exclusive with NO A-space atoms ({len(no_atoms)} total):")
        for d in sorted(no_atoms, key=lambda d: d['b_count'], reverse=True)[:10]:
            print(f"    {d['middle']:>12s} (count={d['b_count']:>3d}, len={len(d['middle'])})")

    # Verdict
    print("\n" + "=" * 60)

    best = results_by_threshold['all_a']
    atom_rate = best['pct_with_atoms']
    mean_coverage = best['mean_coverage']
    high_cov_rate = best['pct_high_coverage']

    if atom_rate >= 0.90 and mean_coverage >= 0.70:
        verdict = "FULL_COLLAPSE"
        explanation = (
            f"{atom_rate:.0%} of B-exclusive MIDDLEs contain A atoms, "
            f"mean coverage {mean_coverage:.0%}. "
            f"They are superstring variants of A discrimination axes."
        )
    elif atom_rate >= 0.80:
        verdict = "STRONG_COLLAPSE"
        explanation = (
            f"{atom_rate:.0%} contain A atoms (mean coverage {mean_coverage:.0%}). "
            f"Overwhelming majority are A-atom elaborations."
        )
    elif atom_rate >= 0.60:
        verdict = "PARTIAL_COLLAPSE"
        explanation = (
            f"{atom_rate:.0%} contain A atoms. "
            f"Majority collapse but {1-atom_rate:.0%} are genuinely novel."
        )
    else:
        verdict = "NO_COLLAPSE"
        explanation = (
            f"Only {atom_rate:.0%} contain A atoms. "
            f"B-exclusive vocabulary is substantially independent."
        )

    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    results = {
        'test': 'T5_subcomponent_collapse',
        'n_exclusive': len(exclusive),
        'n_shared': len(shared),
        'thresholds': {k: {kk: float(vv) if isinstance(vv, (float, np.floating)) else vv
                           for kk, vv in v.items()}
                       for k, v in results_by_threshold.items()},
        'atom_count_distribution': dict(sorted(atom_count_dist.items())),
        'top_atoms': dict(atom_usage.most_common(20)),
        'coverage_summary': {
            'fully_covered': n_fully_covered,
            'partial': n_partial,
            'none': n_none,
        },
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't5_subcomponent_collapse.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't5_subcomponent_collapse.json'}")


if __name__ == '__main__':
    main()
