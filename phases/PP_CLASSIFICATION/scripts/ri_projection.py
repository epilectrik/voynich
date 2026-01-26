"""
RI PROJECTION FROM PP CLASSIFICATION

Project PP properties onto RI through containment.
If RI contains PP atoms with known material associations,
we can infer RI's material-class profile.

Per C516: 85% of RI contain multiple PP atoms.
RI = PP1 ^ PP2 ^ ... (compatibility intersection)
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("RI PROJECTION FROM PP CLASSIFICATION")
print("=" * 70)

# Load PP classification
with open('phases/PP_CLASSIFICATION/results/pp_classification.json', 'r') as f:
    pp_data = json.load(f)

pp_classification = pp_data['pp_classification']

# Get RI MIDDLEs
a_middles = set()
b_middles = set()

for token in tx.currier_a():
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            a_middles.add(m.middle)

for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            b_middles.add(m.middle)

pp_middles = a_middles & b_middles
ri_middles = a_middles - b_middles

print(f"\nRI MIDDLEs to classify: {len(ri_middles)}")
print(f"PP MIDDLEs with classification: {len(pp_classification)}")

# =============================================================================
# STEP 1: FIND PP ATOMS IN EACH RI
# =============================================================================
print("\n[1] Finding PP atoms in RI...")

# For each RI, find all PP substrings (min length 2)
ri_pp_atoms = {}

for ri in ri_middles:
    atoms = []
    for pp in pp_middles:
        if len(pp) >= 2 and pp in ri:
            atoms.append(pp)
    ri_pp_atoms[ri] = atoms

# Stats
atom_counts = [len(v) for v in ri_pp_atoms.values()]
print(f"  RI with PP atoms: {sum(1 for v in ri_pp_atoms.values() if v)} ({100*sum(1 for v in ri_pp_atoms.values() if v)/len(ri_middles):.1f}%)")
print(f"  Mean PP atoms per RI: {np.mean(atom_counts):.2f}")
print(f"  Max PP atoms per RI: {max(atom_counts)}")

# Distribution
atom_dist = Counter(atom_counts)
print(f"\n  Atom count distribution:")
for n in sorted(atom_dist.keys())[:10]:
    print(f"    {n} atoms: {atom_dist[n]} RI ({100*atom_dist[n]/len(ri_middles):.1f}%)")

# =============================================================================
# STEP 2: PROJECT PP MATERIAL CLASS ONTO RI
# =============================================================================
print("\n[2] Projecting PP material class onto RI...")

ri_classification = {}

for ri, atoms in ri_pp_atoms.items():
    if not atoms:
        ri_classification[ri] = {
            'pp_atoms': [],
            'animal_atoms': 0,
            'herb_atoms': 0,
            'mixed_atoms': 0,
            'neutral_atoms': 0,
            'projected_class': 'UNKNOWN',
            'confidence': 0.0,
        }
        continue

    # Count atom classes
    animal_atoms = []
    herb_atoms = []
    mixed_atoms = []
    neutral_atoms = []

    for pp in atoms:
        if pp in pp_classification:
            cls = pp_classification[pp]['material_class']
            if cls == 'ANIMAL':
                animal_atoms.append(pp)
            elif cls == 'HERB':
                herb_atoms.append(pp)
            elif cls == 'MIXED':
                mixed_atoms.append(pp)
            else:
                neutral_atoms.append(pp)

    # Project class based on atom composition
    n_animal = len(animal_atoms)
    n_herb = len(herb_atoms)
    n_mixed = len(mixed_atoms)
    n_neutral = len(neutral_atoms)
    n_total = n_animal + n_herb + n_mixed + n_neutral

    # Classification rules
    if n_animal > 0 and n_herb == 0:
        projected = 'ANIMAL'
        confidence = n_animal / n_total if n_total > 0 else 0
    elif n_herb > 0 and n_animal == 0:
        projected = 'HERB'
        confidence = n_herb / n_total if n_total > 0 else 0
    elif n_animal > 0 and n_herb > 0:
        if n_animal > n_herb * 2:
            projected = 'ANIMAL_MIXED'
            confidence = n_animal / (n_animal + n_herb)
        elif n_herb > n_animal * 2:
            projected = 'HERB_MIXED'
            confidence = n_herb / (n_animal + n_herb)
        else:
            projected = 'MIXED'
            confidence = 0.5
    elif n_mixed > 0:
        projected = 'MIXED'
        confidence = n_mixed / n_total if n_total > 0 else 0
    else:
        projected = 'NEUTRAL'
        confidence = n_neutral / n_total if n_total > 0 else 0

    ri_classification[ri] = {
        'pp_atoms': atoms,
        'animal_atoms': animal_atoms,
        'herb_atoms': herb_atoms,
        'mixed_atoms': mixed_atoms,
        'neutral_atoms': neutral_atoms,
        'n_animal': n_animal,
        'n_herb': n_herb,
        'n_mixed': n_mixed,
        'n_neutral': n_neutral,
        'projected_class': projected,
        'confidence': confidence,
    }

# Count projected classes
projected_counts = Counter(r['projected_class'] for r in ri_classification.values())
print(f"\n  Projected RI class distribution:")
for cls, count in sorted(projected_counts.items(), key=lambda x: -x[1]):
    pct = 100 * count / len(ri_classification)
    print(f"    {cls}: {count} ({pct:.1f}%)")

# =============================================================================
# STEP 3: VALIDATE PROJECTION AGAINST FOLIO LOCALIZATION
# =============================================================================
print("\n[3] Validating projection against folio patterns...")

# Build RI -> folio mapping
ri_folios = defaultdict(set)
for token in tx.currier_a():
    if token.word:
        m = morph.extract(token.word)
        if m.middle and m.middle in ri_middles:
            ri_folios[m.middle].add(token.folio)

# Check if projected class correlates with folio localization
# Animal-heavy folios vs herb-heavy folios
folio_animal_density = defaultdict(int)
folio_herb_density = defaultdict(int)

for ri, data in ri_classification.items():
    cls = data['projected_class']
    for folio in ri_folios.get(ri, []):
        if cls in ['ANIMAL', 'ANIMAL_MIXED']:
            folio_animal_density[folio] += 1
        elif cls in ['HERB', 'HERB_MIXED']:
            folio_herb_density[folio] += 1

# Compare folio profiles
folios_with_both = set(folio_animal_density.keys()) & set(folio_herb_density.keys())
print(f"\n  Folios with both animal and herb RI: {len(folios_with_both)}")

if folios_with_both:
    ratios = []
    for f in folios_with_both:
        a = folio_animal_density[f]
        h = folio_herb_density[f]
        if h > 0:
            ratios.append(a / h)
    if ratios:
        print(f"  Animal/Herb ratio range: {min(ratios):.2f} to {max(ratios):.2f}")
        print(f"  Mean ratio: {np.mean(ratios):.2f}")

# =============================================================================
# STEP 4: HIGH-CONFIDENCE RI EXAMPLES
# =============================================================================
print("\n" + "=" * 70)
print("HIGH-CONFIDENCE RI CLASSIFICATIONS")
print("=" * 70)

# Sort by confidence
high_confidence = [(ri, d) for ri, d in ri_classification.items()
                   if d['confidence'] >= 0.7 and d['projected_class'] not in ['UNKNOWN', 'NEUTRAL', 'MIXED']]

animal_ri = [(ri, d) for ri, d in high_confidence if 'ANIMAL' in d['projected_class']]
herb_ri = [(ri, d) for ri, d in high_confidence if 'HERB' in d['projected_class']]

print(f"\nHigh-confidence ANIMAL RI ({len(animal_ri)}):")
print(f"{'RI':<15} {'Confidence':<12} {'Animal Atoms':<30}")
print("-" * 60)
for ri, d in sorted(animal_ri, key=lambda x: -x[1]['confidence'])[:15]:
    atoms = ', '.join(d['animal_atoms'][:5])
    print(f"{ri:<15} {d['confidence']:.2f}         {atoms}")

print(f"\nHigh-confidence HERB RI ({len(herb_ri)}):")
print(f"{'RI':<15} {'Confidence':<12} {'Herb Atoms':<30}")
print("-" * 60)
for ri, d in sorted(herb_ri, key=lambda x: -x[1]['confidence'])[:15]:
    atoms = ', '.join(d['herb_atoms'][:5])
    print(f"{ri:<15} {d['confidence']:.2f}         {atoms}")

# =============================================================================
# STEP 5: SAVE RESULTS
# =============================================================================
print("\n" + "=" * 70)
print("SAVING RESULTS")
print("=" * 70)

# Prepare output
results = {
    'metadata': {
        'n_ri': len(ri_middles),
        'n_ri_with_atoms': sum(1 for v in ri_pp_atoms.values() if v),
        'mean_atoms_per_ri': np.mean(atom_counts),
    },
    'projected_distribution': dict(projected_counts),
    'high_confidence_count': {
        'animal': len(animal_ri),
        'herb': len(herb_ri),
    },
    'ri_classification': {
        ri: {
            'projected_class': d['projected_class'],
            'confidence': d['confidence'],
            'n_animal': d.get('n_animal', 0),
            'n_herb': d.get('n_herb', 0),
            'n_mixed': d.get('n_mixed', 0),
            'n_neutral': d.get('n_neutral', 0),
            'pp_atoms': d.get('pp_atoms', [])[:10],  # Limit size
        }
        for ri, d in ri_classification.items()
    },
}

output_path = 'phases/PP_CLASSIFICATION/results/ri_projection.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Results saved to: {output_path}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY: RI PROJECTION FROM PP CLASSIFICATION")
print("=" * 70)

print(f"""
PROJECTION METHODOLOGY:
1. Find PP substrings (atoms) within each RI
2. Look up material class for each PP atom
3. Project class based on atom composition

RESULTS:
- RI with PP atoms: {sum(1 for v in ri_pp_atoms.values() if v)}/{len(ri_middles)} ({100*sum(1 for v in ri_pp_atoms.values() if v)/len(ri_middles):.1f}%)
- Mean atoms per RI: {np.mean(atom_counts):.2f}

PROJECTED CLASS DISTRIBUTION:
""")
for cls, count in sorted(projected_counts.items(), key=lambda x: -x[1]):
    pct = 100 * count / len(ri_classification)
    print(f"  {cls:<15}: {count:>4} ({pct:>5.1f}%)")

print(f"""
HIGH-CONFIDENCE CLASSIFICATIONS (>70%):
- Animal RI: {len(animal_ri)}
- Herb RI: {len(herb_ri)}

TIER 4 INTERPRETATION:
RI MIDDLEs inherit material-class associations from their PP atoms.
An RI containing animal-associated PP atoms is likely an animal-specific
substance identifier. This provides a pathway from PP classification
to RI semantic properties through compositional analysis.
""")
