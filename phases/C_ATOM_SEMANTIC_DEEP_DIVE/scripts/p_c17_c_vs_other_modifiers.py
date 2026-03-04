"""
P-C17: c uniqueness as a compound modifier
============================================
Test whether c's compound-modifying behavior is UNIQUE among atoms.
c should be the ONLY atom combining high purity + high diversity + high MON+MARK fraction.

Predictions:
- c has >= 4 distinct categories across its compounds (diversity)
- c mean compound purity >= 90% (determinism)
- c MON+MARK fraction ranked top 3 among first atoms with >= 3 compounds
- c is the ONLY atom meeting all three criteria simultaneously

Pass: c is the only atom meeting all three criteria simultaneously (uniqueness test)
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']

# Single-character atoms used in compounds
ATOMS = set('acdefghiklmnopqrstxy')


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Collect all compound MIDDLEs from Currier B and their categories
    # compound = multi-character MIDDLE whose first char is an atom
    compound_data = defaultdict(lambda: defaultdict(list))
    # compound_data[first_atom][compound_middle] = [category, category, ...]

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle
        if not mid or len(mid) < 2:
            continue

        cat = cc.classify(mid)
        if cat == 'UNK':
            continue

        first_atom = mid[0]
        if first_atom not in ATOMS:
            continue

        compound_data[first_atom][mid].append(cat)

    print("=" * 72)
    print("P-C17: c uniqueness as a compound modifier")
    print("=" * 72)
    print()

    # For each first atom, compute metrics
    results = {}
    for atom in sorted(compound_data.keys()):
        compounds = compound_data[atom]
        n_compounds = len(compounds)
        if n_compounds < 1:
            continue

        # Category diversity: number of distinct majority categories across compounds
        majority_cats = set()
        purities = []
        total_mon_mark = 0
        total_tokens = 0

        for mid, cats in compounds.items():
            if len(cats) < 2:
                # For very rare compounds, still count them
                majority_cat = cats[0]
                purity = 1.0
            else:
                from collections import Counter
                cat_counts = Counter(cats)
                majority_cat = cat_counts.most_common(1)[0][0]
                purity = cat_counts[majority_cat] / len(cats)

            majority_cats.add(majority_cat)
            purities.append(purity)

            mon_mark = sum(1 for c in cats if c in ('MONITORING', 'MARKING'))
            total_mon_mark += mon_mark
            total_tokens += len(cats)

        diversity = len(majority_cats)
        mean_purity = sum(purities) / len(purities) if purities else 0
        mon_mark_frac = total_mon_mark / total_tokens if total_tokens > 0 else 0

        results[atom] = {
            'n_compounds': n_compounds,
            'diversity': diversity,
            'mean_purity': mean_purity,
            'mon_mark_frac': mon_mark_frac,
            'total_tokens': total_tokens,
            'majority_cats': sorted([c for c in majority_cats if c is not None]),
        }

    # Print full table
    print(f"{'Atom':<6} {'#Cpds':<7} {'#Tok':<7} {'Divers':<8} "
          f"{'MnPurity':<10} {'MON+MARK':<10} {'Categories'}")
    print("-" * 90)

    for atom in sorted(results.keys(), key=lambda a: -results[a]['mon_mark_frac']):
        r = results[atom]
        cats_str = ', '.join(r['majority_cats'])
        print(f"{atom:<6} {r['n_compounds']:<7} {r['total_tokens']:<7} "
              f"{r['diversity']:<8} {r['mean_purity']:<10.3f} "
              f"{r['mon_mark_frac']:<10.3f} {cats_str}")

    print()

    # Focus on atoms with >= 3 compounds (meaningful modifier analysis)
    eligible = {a: r for a, r in results.items() if r['n_compounds'] >= 3}
    print(f"Atoms with >= 3 compounds: {len(eligible)}")
    print()

    # Rank by MON+MARK fraction
    ranked_mm = sorted(eligible.keys(), key=lambda a: -eligible[a]['mon_mark_frac'])
    print("Ranked by MON+MARK fraction (atoms with >= 3 compounds):")
    for i, atom in enumerate(ranked_mm):
        r = eligible[atom]
        marker = " <-- c" if atom == 'c' else ""
        print(f"  {i+1}. {atom}: {r['mon_mark_frac']:.3f} "
              f"(diversity={r['diversity']}, purity={r['mean_purity']:.3f}){marker}")

    print()

    # Check predictions
    c_data = results.get('c', None)
    if c_data is None:
        print("FAIL: c not found in compound data")
        return

    print("=" * 72)
    print("PREDICTION CHECKS")
    print("=" * 72)
    print()

    # P1: c diversity >= 4
    p1 = c_data['diversity'] >= 4
    print(f"P1: c diversity >= 4")
    print(f"    c diversity = {c_data['diversity']}")
    print(f"    Categories: {', '.join(c_data['majority_cats'])}")
    print(f"    Verdict: {'PASS' if p1 else 'FAIL'}")
    print()

    # P2: c mean purity >= 90%
    p2 = c_data['mean_purity'] >= 0.90
    print(f"P2: c mean compound purity >= 90%")
    print(f"    c mean purity = {c_data['mean_purity']:.3f}")
    print(f"    Verdict: {'PASS' if p2 else 'FAIL'}")
    print()

    # P3: c MON+MARK ranked top 3 among eligible
    c_rank_mm = ranked_mm.index('c') + 1 if 'c' in ranked_mm else len(ranked_mm)
    p3 = c_rank_mm <= 3
    print(f"P3: c MON+MARK ranked top 3 among atoms with >= 3 compounds")
    print(f"    c rank = {c_rank_mm} (MON+MARK = {c_data['mon_mark_frac']:.3f})")
    print(f"    Verdict: {'PASS' if p3 else 'FAIL'}")
    print()

    # P4 (main test): c is the ONLY atom meeting ALL THREE criteria
    # diversity >= 4, purity >= 90%, MON+MARK >= 30%
    threshold_div = 4
    threshold_pur = 0.90
    threshold_mm = 0.30

    triple_qualifiers = []
    for atom, r in eligible.items():
        if (r['diversity'] >= threshold_div and
                r['mean_purity'] >= threshold_pur and
                r['mon_mark_frac'] >= threshold_mm):
            triple_qualifiers.append(atom)

    p4 = len(triple_qualifiers) == 1 and 'c' in triple_qualifiers

    print(f"P4 (UNIQUENESS): c is the ONLY atom with diversity >= {threshold_div}, "
          f"purity >= {threshold_pur:.0%}, MON+MARK >= {threshold_mm:.0%}")
    print(f"    Atoms meeting all three: {triple_qualifiers if triple_qualifiers else 'none'}")

    if not triple_qualifiers:
        # Relax thresholds slightly and report
        print(f"    NOTE: No atom meets all three thresholds.")
        print(f"    c values: diversity={c_data['diversity']}, "
              f"purity={c_data['mean_purity']:.3f}, "
              f"MON+MARK={c_data['mon_mark_frac']:.3f}")
        # Check which criteria c fails
        fails = []
        if c_data['diversity'] < threshold_div:
            fails.append(f"diversity {c_data['diversity']} < {threshold_div}")
        if c_data['mean_purity'] < threshold_pur:
            fails.append(f"purity {c_data['mean_purity']:.3f} < {threshold_pur}")
        if c_data['mon_mark_frac'] < threshold_mm:
            fails.append(f"MON+MARK {c_data['mon_mark_frac']:.3f} < {threshold_mm}")
        if fails:
            print(f"    c fails: {'; '.join(fails)}")

    print(f"    Verdict: {'PASS' if p4 else 'FAIL'}")
    print()

    # Detailed c-compound breakdown
    print("=" * 72)
    print("DETAILED c-COMPOUND BREAKDOWN")
    print("=" * 72)
    print()
    c_compounds = compound_data.get('c', {})
    print(f"{'Compound':<12} {'N':<6} {'Majority':<14} {'Purity':<10} {'MON+MARK':<10}")
    print("-" * 55)
    for mid in sorted(c_compounds.keys(), key=lambda m: -len(c_compounds[m])):
        cats = c_compounds[mid]
        from collections import Counter
        cat_counts = Counter(cats)
        majority = cat_counts.most_common(1)[0][0]
        purity = cat_counts[majority] / len(cats)
        mm = sum(1 for c in cats if c in ('MONITORING', 'MARKING')) / len(cats)
        print(f"{mid:<12} {len(cats):<6} {majority:<14} {purity:<10.3f} {mm:<10.3f}")

    print()

    # Overall verdict
    all_pass = p1 and p2 and p3 and p4
    n_pass = sum([p1, p2, p3, p4])
    print("=" * 72)
    print(f"OVERALL VERDICT: {'PASS' if all_pass else 'FAIL'} ({n_pass}/4 predictions confirmed)")
    print("=" * 72)

    if not all_pass:
        # Check if c is at least the BEST modifier even if not unique
        print()
        print("SUPPLEMENTARY: Is c at least the top-ranked modifier?")
        # Composite score: diversity * purity * mon_mark
        composites = {}
        for atom, r in eligible.items():
            composites[atom] = r['diversity'] * r['mean_purity'] * r['mon_mark_frac']
        ranked_composite = sorted(composites.keys(), key=lambda a: -composites[a])
        c_composite_rank = ranked_composite.index('c') + 1 if 'c' in ranked_composite else -1
        print(f"  Composite rank (diversity * purity * MON+MARK): "
              f"c is #{c_composite_rank} of {len(ranked_composite)}")
        for i, atom in enumerate(ranked_composite[:5]):
            r = eligible[atom]
            marker = " <--" if atom == 'c' else ""
            print(f"    {i+1}. {atom}: composite={composites[atom]:.4f} "
                  f"(div={r['diversity']}, pur={r['mean_purity']:.3f}, "
                  f"mm={r['mon_mark_frac']:.3f}){marker}")


if __name__ == '__main__':
    main()
