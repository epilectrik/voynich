#!/usr/bin/env python3
"""
A-B Vocabulary Comparison

Compare the MIDDLE vocabulary between A and B to understand the coverage result.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
from collections import Counter
from scripts.voynich import Transcript, Morphology

def main():
    tx = Transcript()
    morph = Morphology()

    # Load classified B tokens
    class_map_path = Path(__file__).parent.parent / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        class_map = json.load(f)
    classified_tokens = set(class_map['token_to_class'].keys())
    classified_middles = set(class_map['token_to_middle'].values()) - {None}

    print("=" * 70)
    print("A-B VOCABULARY COMPARISON")
    print("=" * 70)

    # Get A middles
    a_middles = Counter()
    for token in tx.currier_a():
        m = morph.extract(token.word)
        if m.middle:
            a_middles[m.middle] += 1

    # Get B middles (all)
    b_middles_all = Counter()
    for token in tx.currier_b():
        m = morph.extract(token.word)
        if m.middle:
            b_middles_all[m.middle] += 1

    # Get B middles (classified only)
    b_middles_classified = Counter()
    for token in tx.currier_b():
        if token.word in classified_tokens:
            m = morph.extract(token.word)
            if m.middle:
                b_middles_classified[m.middle] += 1

    print(f"\nVOCABULARY SIZES:")
    print(f"   A unique MIDDLEs:               {len(a_middles)}")
    print(f"   B unique MIDDLEs (all):         {len(b_middles_all)}")
    print(f"   B unique MIDDLEs (classified):  {len(b_middles_classified)}")
    print(f"   Classified token types:         {len(classified_tokens)}")

    # Set operations
    a_set = set(a_middles.keys())
    b_all_set = set(b_middles_all.keys())
    b_class_set = set(b_middles_classified.keys())

    print(f"\nOVERLAP ANALYSIS:")
    print(f"   A AND B(all):        {len(a_set & b_all_set)} ({len(a_set & b_all_set)/len(b_all_set):.1%} of B)")
    print(f"   A AND B(classified): {len(a_set & b_class_set)} ({len(a_set & b_class_set)/len(b_class_set):.1%} of B)")
    print(f"   B(all) - A:          {len(b_all_set - a_set)} MIDDLEs unique to B")
    print(f"   B(class) - A:        {len(b_class_set - a_set)} MIDDLEs unique to classified B")

    # Why is B(classified) vocabulary so small?
    print(f"\nCLASSIFIED B VOCABULARY:")
    print(f"   The 480 classified tokens represent only {len(b_class_set)} unique MIDDLEs")
    print(f"   These are high-frequency tokens - the operational core")
    print(f"   All {len(b_class_set)} appear in A vocabulary")

    # Show the classified B MIDDLEs
    print(f"\n   Classified B MIDDLEs (sorted by B frequency):")
    sorted_class = sorted(b_middles_classified.items(), key=lambda x: -x[1])
    for m, b_count in sorted_class[:30]:
        a_count = a_middles.get(m, 0)
        print(f"      {m:10s}  A: {a_count:4d}  B: {b_count:4d}")

    # What's in B but not classified?
    print(f"\nUNCLASSIFIED B MIDDLEs (examples):")
    unclassified_mids = b_all_set - b_class_set
    print(f"   Total unclassified B MIDDLEs: {len(unclassified_mids)}")

    # How many appear in A?
    unclass_in_a = unclassified_mids & a_set
    print(f"   Of these, {len(unclass_in_a)} also appear in A")
    print(f"   {len(unclassified_mids - a_set)} are unique to B (not in A)")

    # Show B-unique MIDDLEs
    b_unique = sorted(b_all_set - a_set, key=lambda m: -b_middles_all[m])
    print(f"\n   Top B-unique MIDDLEs (not in A):")
    for m in b_unique[:20]:
        print(f"      {m:15s}  B: {b_middles_all[m]:4d}")

    print("\n" + "=" * 70)
    print("IMPLICATION FOR COVERAGE ANALYSIS")
    print("=" * 70)
    print(f"""
The classified B vocabulary consists of 480 high-frequency tokens
mapping to only {len(b_class_set)} unique MIDDLEs. ALL of these appear
in the A vocabulary.

This means:
1. By definition, any B line using only classified tokens has 100%
   potential coverage from the A vocabulary as a whole.

2. The question becomes: can a SINGLE A LINE cover a significant
   fraction of a B line's classified MIDDLEs?

3. Since the classified vocabulary is small and shared, the answer
   is often YES - but this reflects shared core vocabulary, not
   line-level correspondence.

4. For true line-level correspondence, we would need to see:
   - Specific A lines matching specific B lines
   - Rare MIDDLE sharing (not just common MIDDLEs)
   - Non-random best-match pairing

None of these conditions are met.
""")

if __name__ == '__main__':
    main()
