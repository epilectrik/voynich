#!/usr/bin/env python3
"""
Test: Do A records with the same OUTPUT RI share similar materials?

Hypothesis: If RI encodes output category, records converging to the same
output should have similar input materials (herb vs animal).

Method:
1. Find RI tokens appearing in FINAL position in multiple records
2. Check if those records share material class (via prefix signature)
3. If same-output records cluster by material, supports category theory
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

# Material class signatures from previous analysis
ANIMAL_PREFIXES = {'qo', 'ok', 'da', 'ct', 'ot', 'ch'}
HERB_PREFIXES = {'ko', 'tch', 'pch', 'to', 'kch'}

print("="*70)
print("OUTPUT RI MATERIAL CONVERGENCE TEST")
print("="*70)

# Build paragraph data with positions
paragraphs = []
current_folio = None
current_para = []
current_line = None
para_idx = 0

for token in tx.currier_a():
    if '*' in token.word:
        continue

    if token.folio != current_folio:
        if current_para:
            paragraphs.append({
                'folio': current_folio,
                'para_idx': para_idx,
                'tokens': [t.word for t in current_para]
            })
            para_idx += 1
        current_folio = token.folio
        current_para = [token]
        current_line = token.line
        para_idx = 0
        continue

    if token.line != current_line:
        first_word = token.word
        if first_word and first_word[0] in GALLOWS:
            paragraphs.append({
                'folio': current_folio,
                'para_idx': para_idx,
                'tokens': [t.word for t in current_para]
            })
            para_idx += 1
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

if current_para:
    paragraphs.append({
        'folio': current_folio,
        'para_idx': para_idx,
        'tokens': [t.word for t in current_para]
    })

print(f"\nTotal paragraphs: {len(paragraphs)}")

# Identify INITIAL and FINAL RI for each paragraph
def get_ri_positions(para):
    """Get RI tokens in INITIAL (first 3) and FINAL (last 3) positions."""
    tokens = para['tokens']
    if len(tokens) < 4:
        return None, None

    initial_ri = tokens[:3]
    final_ri = tokens[-3:]

    return initial_ri, final_ri

def get_material_class(tokens):
    """Classify paragraph by material class using prefix signature."""
    animal_score = 0
    herb_score = 0

    for token in tokens[:5]:  # Look at first 5 tokens
        try:
            m = morph.extract(token)
            if m.prefix:
                if m.prefix in ANIMAL_PREFIXES:
                    animal_score += 1
                elif m.prefix in HERB_PREFIXES:
                    herb_score += 1
        except:
            pass

    if animal_score > herb_score:
        return 'ANIMAL'
    elif herb_score > animal_score:
        return 'HERB'
    else:
        return 'NEUTRAL'

# Build output RI index
output_ri_records = defaultdict(list)  # RI token -> list of records

for para in paragraphs:
    initial_ri, final_ri = get_ri_positions(para)
    if final_ri is None:
        continue

    material_class = get_material_class(para['tokens'])

    for ri in final_ri:
        output_ri_records[ri].append({
            'folio': para['folio'],
            'para_idx': para['para_idx'],
            'material_class': material_class,
            'initial_ri': initial_ri
        })

# Find RI tokens with multiple source records
shared_output_ri = {ri: recs for ri, recs in output_ri_records.items()
                    if len(recs) >= 2}

print(f"RI tokens appearing in FINAL position: {len(output_ri_records)}")
print(f"RI tokens with 2+ source records: {len(shared_output_ri)}")

# Analyze material class homogeneity for shared outputs
print(f"\n{'='*70}")
print("SHARED OUTPUT RI - MATERIAL CLASS ANALYSIS")
print("="*70)

homogeneous_count = 0
heterogeneous_count = 0
results = []

for ri, records in sorted(shared_output_ri.items(), key=lambda x: -len(x[1])):
    classes = [r['material_class'] for r in records]
    class_counts = Counter(classes)

    # Is it homogeneous?
    dominant_class = class_counts.most_common(1)[0]
    homogeneity = dominant_class[1] / len(classes)

    is_homogeneous = homogeneity >= 0.75  # 75% or more same class

    if is_homogeneous:
        homogeneous_count += 1
    else:
        heterogeneous_count += 1

    results.append({
        'ri': ri,
        'n_records': len(records),
        'classes': dict(class_counts),
        'homogeneity': homogeneity,
        'dominant': dominant_class[0],
        'folios': [r['folio'] for r in records]
    })

# Show top examples
print(f"\n{'RI Token':<15} {'Records':<8} {'Homog.':<8} {'Classes':<25} {'Folios':<30}")
print("-"*90)

for r in results[:25]:
    class_str = ', '.join(f"{c}:{n}" for c, n in r['classes'].items())
    folio_str = ', '.join(r['folios'][:4])
    if len(r['folios']) > 4:
        folio_str += '...'
    print(f"{r['ri']:<15} {r['n_records']:<8} {r['homogeneity']:<8.2f} {class_str:<25} {folio_str:<30}")

# Summary statistics
print(f"\n{'='*70}")
print("HOMOGENEITY SUMMARY")
print("="*70)

print(f"\nShared output RI tokens: {len(shared_output_ri)}")
print(f"Homogeneous (>=75% same class): {homogeneous_count} ({100*homogeneous_count/len(shared_output_ri):.1f}%)")
print(f"Heterogeneous (<75% same class): {heterogeneous_count} ({100*heterogeneous_count/len(shared_output_ri):.1f}%)")

# By dominant class
animal_dominant = sum(1 for r in results if r['dominant'] == 'ANIMAL')
herb_dominant = sum(1 for r in results if r['dominant'] == 'HERB')
neutral_dominant = sum(1 for r in results if r['dominant'] == 'NEUTRAL')

print(f"\nBy dominant material class:")
print(f"  ANIMAL-dominant: {animal_dominant}")
print(f"  HERB-dominant: {herb_dominant}")
print(f"  NEUTRAL-dominant: {neutral_dominant}")

# Statistical test: Are shared outputs more homogeneous than random?
print(f"\n{'='*70}")
print("STATISTICAL TEST: HOMOGENEITY VS RANDOM")
print("="*70)

# Calculate baseline: what's the overall material class distribution?
all_classes = [get_material_class(p['tokens']) for p in paragraphs]
baseline_dist = Counter(all_classes)
total = len(all_classes)

print(f"\nBaseline material class distribution:")
for cls, count in baseline_dist.items():
    print(f"  {cls}: {count} ({100*count/total:.1f}%)")

# Expected homogeneity if random
# If we pick n records randomly, expected homogeneity is sum of (p_i)^n
# For simplicity, use average homogeneity under random assignment
from scipy import stats as scipy_stats

# For each shared output, calculate expected homogeneity under random assignment
observed_homogeneities = [r['homogeneity'] for r in results]
mean_observed = np.mean(observed_homogeneities)

# Simulate random assignment
n_simulations = 1000
simulated_means = []

for _ in range(n_simulations):
    sim_homogeneities = []
    for r in results:
        n = r['n_records']
        # Randomly assign material classes according to baseline
        random_classes = np.random.choice(
            list(baseline_dist.keys()),
            size=n,
            p=[baseline_dist[c]/total for c in baseline_dist.keys()]
        )
        sim_counts = Counter(random_classes)
        sim_homog = sim_counts.most_common(1)[0][1] / n
        sim_homogeneities.append(sim_homog)
    simulated_means.append(np.mean(sim_homogeneities))

mean_random = np.mean(simulated_means)
std_random = np.std(simulated_means)

z_score = (mean_observed - mean_random) / std_random if std_random > 0 else 0
p_value = 1 - scipy_stats.norm.cdf(z_score)

print(f"\nObserved mean homogeneity: {mean_observed:.3f}")
print(f"Expected under random: {mean_random:.3f} (std: {std_random:.3f})")
print(f"Z-score: {z_score:.2f}")
print(f"P-value (one-tailed): {p_value:.4f}")

if p_value < 0.05:
    print("-> *SIGNIFICANT: Shared outputs ARE more material-homogeneous than random")
else:
    print("-> Not significant: No evidence of material clustering by output")

# Summary
print(f"\n{'='*70}")
print("INTERPRETATION")
print("="*70)

print(f"""
If OUTPUT RI encodes procedural category:
- Records producing same output should use similar materials
- Material homogeneity should be HIGHER than random

Results:
- Mean homogeneity: {mean_observed:.3f} vs {mean_random:.3f} random
- {'SUPPORTS' if p_value < 0.05 else 'DOES NOT SUPPORT'} the hypothesis

{'If significant: Same output RI = same material class processing' if p_value < 0.05 else 'Output category may be independent of material class'}
""")

# Save results
output = {
    'shared_output_ri_count': len(shared_output_ri),
    'homogeneous_count': homogeneous_count,
    'heterogeneous_count': heterogeneous_count,
    'mean_homogeneity': mean_observed,
    'random_homogeneity': mean_random,
    'z_score': z_score,
    'p_value': p_value,
    'top_shared_ri': [r['ri'] for r in results[:10]]
}

output_path = Path(__file__).parent.parent / 'results' / 'output_ri_convergence.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
