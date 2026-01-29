"""
Test: Do B compound MIDDLEs contain PP atoms that are specific to THAT folio?

If B compounds are "headers" for folio-specific vocabulary, then:
  - The PP atoms inside a B compound MIDDLE should be enriched for PP that
    appears in the same folio
  - Compound MIDDLEs might compress/index the folio's vocabulary
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("B COMPOUND FOLIO SPECIFICITY TEST")
print("="*70)

# ============================================================
# COLLECT PP MIDDLEs AND B MIDDLEs BY FOLIO
# ============================================================

# Get all A MIDDLEs (to identify PP)
all_a_middles = set()
for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        all_a_middles.add(m.middle)

# Get all B MIDDLEs by folio
b_middles_by_folio = defaultdict(set)
b_token_middles_by_folio = defaultdict(list)  # Keep all occurrences

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_middles_by_folio[token.folio].add(m.middle)
        b_token_middles_by_folio[token.folio].append(m.middle)

all_b_middles = set()
for mids in b_middles_by_folio.values():
    all_b_middles.update(mids)

# PP = shared between A and B
pp_middles = all_a_middles & all_b_middles

# B-exclusive = in B but not A
b_exclusive = all_b_middles - all_a_middles

print(f"\nInventory:")
print(f"  B folios: {len(b_middles_by_folio)}")
print(f"  PP (shared): {len(pp_middles)}")
print(f"  B-exclusive: {len(b_exclusive)}")

# ============================================================
# FOR EACH B FOLIO: WHICH PP MIDDLEs APPEAR?
# ============================================================
print("\n" + "="*70)
print("PP VOCABULARY BY B FOLIO")
print("="*70)

folio_pp = {}
for folio, middles in b_middles_by_folio.items():
    folio_pp[folio] = middles & pp_middles

# Which PP are folio-specific vs shared?
pp_folio_count = Counter()
for folio, pps in folio_pp.items():
    for pp in pps:
        pp_folio_count[pp] += 1

# PP that appear in only 1-3 folios
rare_pp = {pp for pp, count in pp_folio_count.items() if count <= 3}
common_pp = {pp for pp, count in pp_folio_count.items() if count >= 50}

print(f"\nPP distribution across folios:")
print(f"  Rare (1-3 folios): {len(rare_pp)} ({100*len(rare_pp)/len(pp_middles):.1f}%)")
print(f"  Common (50+ folios): {len(common_pp)} ({100*len(common_pp)/len(pp_middles):.1f}%)")
print(f"  Mean folios per PP: {np.mean(list(pp_folio_count.values())):.1f}")

# ============================================================
# FOR EACH B FOLIO: IDENTIFY COMPOUND MIDDLEs
# ============================================================
print("\n" + "="*70)
print("B-EXCLUSIVE COMPOUND STRUCTURE BY FOLIO")
print("="*70)

# For each folio, find B-exclusive MIDDLEs that appear in that folio
# and extract the PP atoms they contain
folio_exclusive_compounds = {}

for folio, middles in b_middles_by_folio.items():
    # B-exclusive MIDDLEs in this folio
    folio_b_excl = middles & b_exclusive

    # For each compound, extract PP atoms
    compound_data = []
    for comp in folio_b_excl:
        pp_atoms = {pp for pp in pp_middles if pp in comp and pp != comp}
        if pp_atoms:
            compound_data.append({
                'compound': comp,
                'pp_atoms': pp_atoms,
                'n_atoms': len(pp_atoms)
            })

    folio_exclusive_compounds[folio] = compound_data

# Sample output
sample_folios = list(b_middles_by_folio.keys())[:3]
for folio in sample_folios:
    compounds = folio_exclusive_compounds[folio]
    print(f"\n{folio}: {len(compounds)} B-exclusive compounds")
    for c in compounds[:3]:
        print(f"  '{c['compound']}' contains: {list(c['pp_atoms'])[:5]}")

# ============================================================
# KEY TEST: Do compound PP atoms match SAME-FOLIO PP?
# ============================================================
print("\n" + "="*70)
print("SAME-FOLIO PP ENRICHMENT TEST")
print("="*70)

# For each folio's compounds, check what fraction of their PP atoms
# appear in that same folio (vs other folios)

folio_enrichment = []

for folio, compounds in folio_exclusive_compounds.items():
    if not compounds:
        continue

    folio_pp_set = folio_pp[folio]
    all_compound_pp = set()
    for c in compounds:
        all_compound_pp.update(c['pp_atoms'])

    if not all_compound_pp:
        continue

    # What fraction of compound PP atoms appear in same folio?
    same_folio_match = all_compound_pp & folio_pp_set
    same_folio_rate = len(same_folio_match) / len(all_compound_pp)

    # What fraction appear in OTHER folios (random baseline)?
    # Average across other folios
    other_rates = []
    for other_folio, other_pp in folio_pp.items():
        if other_folio != folio:
            other_match = all_compound_pp & other_pp
            other_rates.append(len(other_match) / len(all_compound_pp))

    mean_other_rate = np.mean(other_rates) if other_rates else 0
    lift = same_folio_rate / mean_other_rate if mean_other_rate > 0 else float('inf')

    folio_enrichment.append({
        'folio': folio,
        'n_compounds': len(compounds),
        'n_pp_atoms': len(all_compound_pp),
        'same_folio_rate': same_folio_rate,
        'other_folio_rate': mean_other_rate,
        'lift': lift
    })

if folio_enrichment:
    same_rates = [d['same_folio_rate'] for d in folio_enrichment]
    other_rates = [d['other_folio_rate'] for d in folio_enrichment]
    lifts = [d['lift'] for d in folio_enrichment if d['lift'] != float('inf')]

    print(f"\nSame-folio PP match rate:")
    print(f"  Mean: {np.mean(same_rates):.3f}")
    print(f"  Median: {np.median(same_rates):.3f}")

    print(f"\nOther-folio PP match rate (baseline):")
    print(f"  Mean: {np.mean(other_rates):.3f}")

    print(f"\nLift (same vs other):")
    print(f"  Mean: {np.mean(lifts):.2f}x")
    print(f"  Median: {np.median(lifts):.2f}x")

# ============================================================
# TEST: RARE PP ENRICHMENT
# ============================================================
print("\n" + "="*70)
print("RARE PP ENRICHMENT IN COMPOUNDS")
print("="*70)

# Do compounds preferentially contain RARE (folio-specific) PP atoms?
rare_enrichment = []

for folio, compounds in folio_exclusive_compounds.items():
    if not compounds:
        continue

    all_compound_pp = set()
    for c in compounds:
        all_compound_pp.update(c['pp_atoms'])

    if not all_compound_pp:
        continue

    # What fraction are rare PP?
    rare_in_compound = all_compound_pp & rare_pp
    rare_rate = len(rare_in_compound) / len(all_compound_pp)

    # Baseline: fraction of all PP that are rare
    baseline_rare = len(rare_pp) / len(pp_middles)

    rare_enrichment.append({
        'folio': folio,
        'rare_rate': rare_rate,
        'baseline': baseline_rare,
        'lift': rare_rate / baseline_rare if baseline_rare > 0 else 0
    })

if rare_enrichment:
    rates = [d['rare_rate'] for d in rare_enrichment]
    lifts = [d['lift'] for d in rare_enrichment]

    print(f"\nRare PP (1-3 folios) in compounds:")
    print(f"  Mean rate: {np.mean(rates):.3f}")
    print(f"  Baseline: {len(rare_pp)/len(pp_middles):.3f}")
    print(f"  Lift: {np.mean(lifts):.2f}x")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

if folio_enrichment:
    mean_lift = np.mean([d['lift'] for d in folio_enrichment if d['lift'] != float('inf')])
    if mean_lift > 1.2:
        findings.append(f"SAME_FOLIO_ENRICHED: Compound PP atoms {mean_lift:.2f}x more likely in same folio")
    else:
        findings.append(f"NO_SAME_FOLIO_ENRICHMENT: Compound PP atoms only {mean_lift:.2f}x in same folio")

if rare_enrichment:
    rare_lift = np.mean([d['lift'] for d in rare_enrichment])
    if rare_lift > 1.5:
        findings.append(f"RARE_PP_ENRICHED: Compounds contain {rare_lift:.2f}x more rare (folio-specific) PP")
    else:
        findings.append(f"NO_RARE_ENRICHMENT: Compounds contain {rare_lift:.2f}x rare PP (near baseline)")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

print(f"""

B COMPOUND HEADER HYPOTHESIS:

If B compounds are "headers" that compress folio vocabulary:
1. PP atoms in compounds should be enriched for SAME-folio PP
2. PP atoms in compounds should preferentially be RARE (folio-specific)

Results:
  - Same-folio PP rate: {np.mean(same_rates):.1%} (vs {np.mean(other_rates):.1%} baseline)
  - Same-folio lift: {np.mean(lifts):.2f}x
  - Rare PP lift: {np.mean([d['lift'] for d in rare_enrichment]):.2f}x

{'SUPPORTS HEADER HYPOTHESIS' if mean_lift > 1.3 and rare_lift > 1.5 else
 'PARTIAL SUPPORT' if mean_lift > 1.1 or rare_lift > 1.2 else
 'DOES NOT SUPPORT HEADER HYPOTHESIS'}
""")
