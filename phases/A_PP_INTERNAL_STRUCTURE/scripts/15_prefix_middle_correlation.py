#!/usr/bin/env python3
"""
Test: Are PREFIX and MIDDLE correlated?

If certain MIDDLEs preferentially appear with certain PREFIXes,
then knowing the MIDDLE tells you something about the PREFIX distribution.
This would explain how AZC position (determined by MIDDLE) predicts "escape rate" (PREFIX frequency).
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict
import json

def main():
    tx = Transcript()
    morph = Morphology()

    # Collect PREFIX-MIDDLE co-occurrences across all B tokens
    middle_prefix_counts = defaultdict(lambda: defaultdict(int))
    prefix_totals = defaultdict(int)
    middle_totals = defaultdict(int)

    for token in tx.currier_b():
        if not token.word.strip():
            continue
        m = morph.extract(token.word)
        if m.middle:
            prefix = m.prefix if m.prefix else 'NONE'
            middle = m.middle
            middle_prefix_counts[middle][prefix] += 1
            prefix_totals[prefix] += 1
            middle_totals[middle] += 1

    print("=" * 60)
    print("TEST: PREFIX-MIDDLE CORRELATION")
    print("=" * 60)
    print()

    # Find MIDDLEs that strongly prefer specific PREFIXes
    print("=== MIDDLEs with strong PREFIX preference ===")
    print("(MIDDLEs appearing 50+ times, showing dominant PREFIX)")
    print()

    strong_associations = []
    total_middles_50plus = 0

    for middle, prefixes in middle_prefix_counts.items():
        total = sum(prefixes.values())
        if total < 50:
            continue
        total_middles_50plus += 1

        # Find dominant prefix
        dominant_prefix, dominant_count = max(prefixes.items(), key=lambda x: x[1])
        dominance = dominant_count / total
        if dominance > 0.7:  # 70%+ with one prefix
            strong_associations.append((middle, dominant_prefix, dominance, total))

    print(f"MIDDLEs with >70% single-prefix dominance:")
    for middle, prefix, dom, total in sorted(strong_associations, key=lambda x: -x[2])[:25]:
        print(f"  {middle:15} -> {prefix:8} {dom*100:5.1f}% (n={total})")

    print()
    print(f"Total MIDDLEs with >70% dominance: {len(strong_associations)}")
    print(f"Total MIDDLEs with 50+ occurrences: {total_middles_50plus}")
    print(f"Percentage with strong PREFIX preference: {len(strong_associations)/total_middles_50plus*100:.1f}%")

    # Now check: are qo-preferring MIDDLEs different from ch/sh-preferring MIDDLEs?
    print()
    print("=" * 60)
    print("=== PREFIX family MIDDLE overlap ===")
    print("=" * 60)

    qo_middles = set()
    chsh_middles = set()
    ok_middles = set()
    ot_middles = set()

    for middle, prefixes in middle_prefix_counts.items():
        total = sum(prefixes.values())
        if total < 20:
            continue
        qo_frac = prefixes.get('qo', 0) / total
        ch_frac = prefixes.get('ch', 0) / total
        sh_frac = prefixes.get('sh', 0) / total
        ok_frac = prefixes.get('ok', 0) / total
        ot_frac = prefixes.get('ot', 0) / total
        chsh_frac = ch_frac + sh_frac

        if qo_frac > 0.5:
            qo_middles.add(middle)
        if chsh_frac > 0.5:
            chsh_middles.add(middle)
        if ok_frac > 0.3:
            ok_middles.add(middle)
        if ot_frac > 0.3:
            ot_middles.add(middle)

    overlap = qo_middles & chsh_middles
    print(f"MIDDLEs >50% qo-prefixed: {len(qo_middles)}")
    print(f"MIDDLEs >50% ch/sh-prefixed: {len(chsh_middles)}")
    print(f"Overlap: {len(overlap)}")

    if qo_middles | chsh_middles:
        jaccard = len(overlap) / len(qo_middles | chsh_middles)
        print(f"Jaccard similarity: {jaccard:.3f}")

    print()
    print("qo-dominant MIDDLEs:", sorted(qo_middles))
    print()
    print("chsh-dominant MIDDLEs:", sorted(chsh_middles))

    # Test: If I know the MIDDLE, how well can I predict qo vs chsh?
    print()
    print("=" * 60)
    print("=== MIDDLE -> PREFIX predictability ===")
    print("=" * 60)

    # For each MIDDLE, compute entropy of PREFIX distribution
    import math

    predictable_count = 0
    unpredictable_count = 0

    for middle, prefixes in middle_prefix_counts.items():
        total = sum(prefixes.values())
        if total < 30:
            continue

        # Compute entropy
        entropy = 0
        for count in prefixes.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        # Max entropy for this distribution
        max_entropy = math.log2(len(prefixes))

        if max_entropy > 0:
            normalized_entropy = entropy / max_entropy
        else:
            normalized_entropy = 0

        if normalized_entropy < 0.5:  # Low entropy = predictable
            predictable_count += 1
        else:
            unpredictable_count += 1

    print(f"MIDDLEs with predictable PREFIX (entropy < 0.5): {predictable_count}")
    print(f"MIDDLEs with unpredictable PREFIX (entropy >= 0.5): {unpredictable_count}")
    print(f"Predictability rate: {predictable_count/(predictable_count+unpredictable_count)*100:.1f}%")

    # Final test: Contingency table
    print()
    print("=" * 60)
    print("=== Chi-squared test: MIDDLE x PREFIX independence ===")
    print("=" * 60)

    # Build contingency table for top 20 MIDDLEs x top 5 PREFIXes
    top_middles = sorted(middle_totals.items(), key=lambda x: -x[1])[:20]
    top_prefixes = sorted(prefix_totals.items(), key=lambda x: -x[1])[:5]

    print(f"Testing top {len(top_middles)} MIDDLEs x top {len(top_prefixes)} PREFIXes")

    # Build observed matrix
    observed = []
    for middle, _ in top_middles:
        row = [middle_prefix_counts[middle].get(p, 0) for p, _ in top_prefixes]
        observed.append(row)

    # Chi-squared
    from scipy import stats
    import numpy as np

    observed = np.array(observed)
    chi2, p, dof, expected = stats.chi2_contingency(observed)

    print(f"Chi-squared: {chi2:.1f}")
    print(f"p-value: {p:.2e}")
    print(f"Degrees of freedom: {dof}")

    if p < 0.0001:
        print()
        print("VERDICT: PREFIX and MIDDLE are STRONGLY DEPENDENT")
        print("Knowing the MIDDLE significantly predicts the PREFIX distribution.")
    else:
        print()
        print("VERDICT: PREFIX and MIDDLE appear independent")

if __name__ == "__main__":
    main()
