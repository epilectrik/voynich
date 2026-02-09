#!/usr/bin/env python3
"""
Test 2: Brunschwig Tier Mapping by Prefix Family

Question: Do QO-exclusive and CHSH-exclusive MIDDLEs map to different
          Brunschwig operation tiers (PREP, THERMO, EXTENDED)?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict
import json

def main():
    tx = Transcript()
    morph = Morphology()

    # From C649: EN-exclusive MIDDLEs by lane
    QO_EXCLUSIVE_MIDDLES = {'ka', 'kai', 'kc', 'kch', 'ke', 'kec', 'keed', 'keeo', 'keo', 'pch', 'tc', 'tch', 'te'}
    CHSH_EXCLUSIVE_MIDDLES = {'ct', 'eck', 'ect', 'eek', 'ek', 'eod', 'et', 'ok', 'ot'}

    # F-BRU-011 tier mapping
    MIDDLE_TIERS = {
        # PREPARATION (early)
        'te': 'PREP',     # gather material
        'pch': 'PREP',    # chop
        'lch': 'PREP',    # strip/separate
        'tch': 'PREP',    # pound
        'ksh': 'PREP',    # special prep
        'sch': 'PREP',    # grind
        'cth': 'PREP',    # cut/divide
        'tc': 'PREP',     # likely prep

        # THERMODYNAMIC (mid)
        'k': 'THERMO',
        't': 'THERMO',
        'e': 'THERMO',
        'ch': 'THERMO',
        'sh': 'THERMO',
        'h': 'THERMO',
        'ok': 'THERMO',   # o-kernel
        'ot': 'THERMO',   # o-transfer
        'ek': 'THERMO',   # e-kernel
        'et': 'THERMO',   # e-transfer
        'ct': 'THERMO',   # c-transfer

        # EXTENDED (late, equilibration cycles)
        'ke': 'EXTENDED',
        'kch': 'EXTENDED',
        'kc': 'EXTENDED',
        'ka': 'EXTENDED',
        'kai': 'EXTENDED',
        'kec': 'EXTENDED',
        'keed': 'EXTENDED',
        'keeo': 'EXTENDED',
        'keo': 'EXTENDED',
        'eck': 'EXTENDED',
        'ect': 'EXTENDED',
        'eek': 'EXTENDED',
        'eod': 'EXTENDED',
    }

    # Classify QO-exclusive MIDDLEs
    qo_tiers = Counter()
    qo_mapping = {}
    for mid in QO_EXCLUSIVE_MIDDLES:
        tier = MIDDLE_TIERS.get(mid, 'UNKNOWN')
        qo_tiers[tier] += 1
        qo_mapping[mid] = tier

    # Classify CHSH-exclusive MIDDLEs
    chsh_tiers = Counter()
    chsh_mapping = {}
    for mid in CHSH_EXCLUSIVE_MIDDLES:
        tier = MIDDLE_TIERS.get(mid, 'UNKNOWN')
        chsh_tiers[tier] += 1
        chsh_mapping[mid] = tier

    # Now count actual token occurrences by tier
    qo_token_tiers = Counter()
    chsh_token_tiers = Counter()

    QO_PREFIXES = {'qo', 'ok', 'ot', 'o'}
    CHSH_PREFIXES = {'ch', 'sh'}

    for token in tx.currier_b():
        if '*' in token.word or not token.word.strip():
            continue

        m = morph.extract(token.word)
        if not m.prefix or not m.middle:
            continue

        tier = MIDDLE_TIERS.get(m.middle)
        if not tier:
            # Try to infer from initial characters
            if m.middle and len(m.middle) >= 2:
                prefix2 = m.middle[:2]
                if prefix2 in MIDDLE_TIERS:
                    tier = MIDDLE_TIERS[prefix2]

        if m.prefix in QO_PREFIXES and tier:
            qo_token_tiers[tier] += 1
        elif m.prefix in CHSH_PREFIXES and tier:
            chsh_token_tiers[tier] += 1

    results = {
        'qo_exclusive_middles': list(QO_EXCLUSIVE_MIDDLES),
        'chsh_exclusive_middles': list(CHSH_EXCLUSIVE_MIDDLES),
        'qo_tier_distribution_types': dict(qo_tiers),
        'chsh_tier_distribution_types': dict(chsh_tiers),
        'qo_mapping': qo_mapping,
        'chsh_mapping': chsh_mapping,
        'qo_token_tiers': dict(qo_token_tiers),
        'chsh_token_tiers': dict(chsh_token_tiers),
    }

    # Print results
    print("=" * 60)
    print("TEST 2: BRUNSCHWIG TIER MAPPING BY PREFIX FAMILY")
    print("=" * 60)
    print()
    print("QO-Exclusive MIDDLEs (from C649):")
    print("-" * 40)
    for mid in sorted(QO_EXCLUSIVE_MIDDLES):
        tier = qo_mapping[mid]
        print(f"  {mid:<8} -> {tier}")
    print()
    print(f"QO Tier Summary (types): {dict(qo_tiers)}")
    print()

    print("CHSH-Exclusive MIDDLEs (from C649):")
    print("-" * 40)
    for mid in sorted(CHSH_EXCLUSIVE_MIDDLES):
        tier = chsh_mapping[mid]
        print(f"  {mid:<8} -> {tier}")
    print()
    print(f"CHSH Tier Summary (types): {dict(chsh_tiers)}")
    print()

    print("Token-Level Tier Distribution:")
    print("-" * 40)
    print(f"{'Tier':<12} {'QO tokens':<15} {'CHSH tokens':<15}")
    print("-" * 40)
    all_tiers = set(qo_token_tiers.keys()) | set(chsh_token_tiers.keys())
    for tier in sorted(all_tiers):
        qo_count = qo_token_tiers.get(tier, 0)
        chsh_count = chsh_token_tiers.get(tier, 0)
        print(f"{tier:<12} {qo_count:<15} {chsh_count:<15}")

    print()
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print()

    # Key finding: What tier dominates each family?
    qo_prep = qo_tiers.get('PREP', 0)
    qo_thermo = qo_tiers.get('THERMO', 0)
    qo_ext = qo_tiers.get('EXTENDED', 0)

    chsh_prep = chsh_tiers.get('PREP', 0)
    chsh_thermo = chsh_tiers.get('THERMO', 0)
    chsh_ext = chsh_tiers.get('EXTENDED', 0)

    print(f"QO-exclusive MIDDLEs: {qo_prep} PREP, {qo_thermo} THERMO, {qo_ext} EXTENDED")
    print(f"CHSH-exclusive MIDDLEs: {chsh_prep} PREP, {chsh_thermo} THERMO, {chsh_ext} EXTENDED")
    print()

    if qo_ext > qo_thermo and qo_ext > qo_prep:
        print("QO MIDDLEs concentrate in EXTENDED tier (equilibration cycles)")
    if chsh_thermo > chsh_ext and chsh_thermo > chsh_prep:
        print("CHSH MIDDLEs concentrate in THERMO tier (monitoring)")

    # Save results
    import os
    os.makedirs('C:/git/voynich/phases/QO_CHSH_DIFFERENTIATION/results', exist_ok=True)
    with open('C:/git/voynich/phases/QO_CHSH_DIFFERENTIATION/results/02_brunschwig_tier.json', 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print("Results saved to results/02_brunschwig_tier.json")

if __name__ == '__main__':
    main()
