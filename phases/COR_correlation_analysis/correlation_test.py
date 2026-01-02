"""
Program-Plant Correlation Analysis
Phase 3: Statistical correlation between program behavior and plant morphology
"""

import json
import numpy as np
from collections import Counter
from scipy import stats

# BLIND MORPHOLOGY DATA (classified without seeing program metrics)
morphology = {
    'f26r': {'primary': 'ROOT_HEAVY', 'secondary': ['LEAFY_HERB']},
    'f26v': {'primary': 'ROOT_HEAVY', 'secondary': ['LEAFY_HERB']},
    'f31r': {'primary': 'ROOT_HEAVY', 'secondary': ['FLOWER_DOMINANT', 'LEAFY_HERB']},
    'f31v': {'primary': 'COMPOSITE', 'secondary': ['ROOT_HEAVY', 'LEAFY_HERB']},
    'f33r': {'primary': 'FLOWER_DOMINANT', 'secondary': ['ROOT_HEAVY', 'LEAFY_HERB']},
    'f33v': {'primary': 'LEAFY_HERB', 'secondary': ['AMBIGUOUS']},
    'f34r': {'primary': 'ROOT_HEAVY', 'secondary': ['LEAFY_HERB', 'FLOWER_DOMINANT']},
    'f34v': {'primary': 'WOODY_SHRUB', 'secondary': ['ROOT_HEAVY']},
    'f39r': {'primary': 'ROOT_HEAVY', 'secondary': ['LEAFY_HERB']},
    'f39v': {'primary': 'FLOWER_DOMINANT', 'secondary': ['ROOT_HEAVY', 'LEAFY_HERB']},
    'f40r': {'primary': 'FLOWER_DOMINANT', 'secondary': ['ROOT_HEAVY', 'LEAFY_HERB']},
    'f40v': {'primary': 'FLOWER_DOMINANT', 'secondary': ['ROOT_HEAVY']},
    'f41r': {'primary': 'LEAFY_HERB', 'secondary': ['ROOT_HEAVY']},
    'f41v': {'primary': 'ROOT_HEAVY', 'secondary': ['LEAFY_HERB', 'FLOWER_DOMINANT']},
    'f43r': {'primary': 'ROOT_HEAVY', 'secondary': ['LEAFY_HERB', 'FLOWER_DOMINANT']},
    'f43v': {'primary': 'COMPOSITE', 'secondary': ['LEAFY_HERB', 'ROOT_HEAVY']},
    'f46r': {'primary': 'LEAFY_HERB', 'secondary': ['ROOT_HEAVY']},
    'f46v': {'primary': 'FLOWER_DOMINANT', 'secondary': ['LEAFY_HERB', 'ROOT_HEAVY']},
    'f48r': {'primary': 'LEAFY_HERB', 'secondary': ['ROOT_HEAVY', 'AMBIGUOUS']},
    'f48v': {'primary': 'LEAFY_HERB', 'secondary': ['FLOWER_DOMINANT', 'ROOT_HEAVY']},
    'f50r': {'primary': 'FLOWER_DOMINANT', 'secondary': ['LEAFY_HERB', 'ROOT_HEAVY']},
    'f50v': {'primary': 'FLOWER_DOMINANT', 'secondary': ['ROOT_HEAVY', 'LEAFY_HERB']},
    'f55r': {'primary': 'LEAFY_HERB', 'secondary': ['FLOWER_DOMINANT', 'ROOT_HEAVY']},
    'f55v': {'primary': 'ROOT_HEAVY', 'secondary': ['LEAFY_HERB', 'FLOWER_DOMINANT']}
}

# PROGRAM METRICS (from control_signatures.json)
program_metrics = {
    'f26r': {'aggressiveness': 'MODERATE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'REGULAR', 'recovery': 'MODERATE'},
    'f26v': {'aggressiveness': 'CONSERVATIVE', 'link_class': 'HEAVY', 'hazard': 'LOW', 'duration': 'REGULAR', 'recovery': 'LOW'},
    'f31r': {'aggressiveness': 'AGGRESSIVE', 'link_class': 'SPARSE', 'hazard': 'HIGH', 'duration': 'REGULAR', 'recovery': 'MODERATE'},
    'f31v': {'aggressiveness': 'CONSERVATIVE', 'link_class': 'HEAVY', 'hazard': 'MEDIUM', 'duration': 'REGULAR', 'recovery': 'LOW'},
    'f33r': {'aggressiveness': 'AGGRESSIVE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'REGULAR', 'recovery': 'MODERATE'},
    'f33v': {'aggressiveness': 'AGGRESSIVE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'REGULAR', 'recovery': 'MODERATE'},
    'f34r': {'aggressiveness': 'MODERATE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'REGULAR', 'recovery': 'HIGH'},
    'f34v': {'aggressiveness': 'MODERATE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'REGULAR', 'recovery': 'MODERATE'},
    'f39r': {'aggressiveness': 'AGGRESSIVE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'EXTENDED', 'recovery': 'HIGH'},
    'f39v': {'aggressiveness': 'MODERATE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'EXTENDED', 'recovery': 'MODERATE'},
    'f40r': {'aggressiveness': 'MODERATE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'REGULAR', 'recovery': 'MODERATE'},
    'f40v': {'aggressiveness': 'CONSERVATIVE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'REGULAR', 'recovery': 'MODERATE'},
    'f41r': {'aggressiveness': 'MODERATE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'REGULAR', 'recovery': 'MODERATE'},
    'f41v': {'aggressiveness': 'CONSERVATIVE', 'link_class': 'HEAVY', 'hazard': 'LOW', 'duration': 'REGULAR', 'recovery': 'MODERATE'},
    'f43r': {'aggressiveness': 'MODERATE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'EXTENDED', 'recovery': 'MODERATE'},
    'f43v': {'aggressiveness': 'CONSERVATIVE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'EXTENDED', 'recovery': 'LOW'},
    'f46r': {'aggressiveness': 'AGGRESSIVE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'EXTENDED', 'recovery': 'HIGH'},
    'f46v': {'aggressiveness': 'MODERATE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'EXTENDED', 'recovery': 'MODERATE'},
    'f48r': {'aggressiveness': 'CONSERVATIVE', 'link_class': 'HEAVY', 'hazard': 'LOW', 'duration': 'REGULAR', 'recovery': 'LOW'},
    'f48v': {'aggressiveness': 'CONSERVATIVE', 'link_class': 'HEAVY', 'hazard': 'LOW', 'duration': 'REGULAR', 'recovery': 'LOW'},
    'f50r': {'aggressiveness': 'CONSERVATIVE', 'link_class': 'HEAVY', 'hazard': 'MEDIUM', 'duration': 'REGULAR', 'recovery': 'MODERATE'},
    'f50v': {'aggressiveness': 'CONSERVATIVE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'REGULAR', 'recovery': 'MODERATE'},
    'f55r': {'aggressiveness': 'AGGRESSIVE', 'link_class': 'MODERATE', 'hazard': 'MEDIUM', 'duration': 'REGULAR', 'recovery': 'MODERATE'},
    'f55v': {'aggressiveness': 'MODERATE', 'link_class': 'MODERATE', 'hazard': 'LOW', 'duration': 'REGULAR', 'recovery': 'HIGH'}
}

def cramers_v(confusion_matrix):
    """Calculate Cramer's V for effect size"""
    chi2 = stats.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum()
    min_dim = min(confusion_matrix.shape[0], confusion_matrix.shape[1]) - 1
    if min_dim == 0 or n == 0:
        return 0.0
    return np.sqrt(chi2 / (n * min_dim))

def permutation_test(observed_stat, data1, data2, n_permutations=10000):
    """Permutation test for association"""
    combined = list(zip(data1, data2))
    count_extreme = 0

    for _ in range(n_permutations):
        # Shuffle morphology labels
        shuffled_morph = np.random.permutation(data1)
        # Compute test statistic (e.g., count of specific pairings)
        shuffled_stat = sum(1 for m, p in zip(shuffled_morph, data2) if m == 'ROOT_HEAVY' and p == 'AGGRESSIVE')
        if shuffled_stat >= observed_stat:
            count_extreme += 1

    return count_extreme / n_permutations

print("="*80)
print("PROGRAM-PLANT CORRELATION ANALYSIS")
print("="*80)

folios = sorted(morphology.keys())

# Extract lists for analysis
primary_morph = [morphology[f]['primary'] for f in folios]
aggressiveness = [program_metrics[f]['aggressiveness'] for f in folios]
link_class = [program_metrics[f]['link_class'] for f in folios]
hazard = [program_metrics[f]['hazard'] for f in folios]
duration = [program_metrics[f]['duration'] for f in folios]
recovery = [program_metrics[f]['recovery'] for f in folios]

# Check if folio has ROOT_HEAVY anywhere (primary or secondary)
has_root_heavy = []
for f in folios:
    if morphology[f]['primary'] == 'ROOT_HEAVY' or 'ROOT_HEAVY' in morphology[f]['secondary']:
        has_root_heavy.append('YES')
    else:
        has_root_heavy.append('NO')

# Check if folio has FLOWER_DOMINANT anywhere
has_flower_dom = []
for f in folios:
    if morphology[f]['primary'] == 'FLOWER_DOMINANT' or 'FLOWER_DOMINANT' in morphology[f]['secondary']:
        has_flower_dom.append('YES')
    else:
        has_flower_dom.append('NO')

print("\n" + "-"*80)
print("TEST 1: AGGRESSIVENESS vs PRIMARY MORPHOLOGY")
print("-"*80)

# Create contingency table
morph_cats = ['ROOT_HEAVY', 'FLOWER_DOMINANT', 'LEAFY_HERB', 'OTHER']
agg_cats = ['AGGRESSIVE', 'MODERATE', 'CONSERVATIVE']

def simplify_morph(m):
    if m in ['ROOT_HEAVY', 'FLOWER_DOMINANT', 'LEAFY_HERB']:
        return m
    return 'OTHER'

simple_morph = [simplify_morph(m) for m in primary_morph]

# Build contingency table
contingency = np.zeros((len(morph_cats), len(agg_cats)), dtype=int)
for m, a in zip(simple_morph, aggressiveness):
    i = morph_cats.index(m)
    j = agg_cats.index(a)
    contingency[i, j] += 1

print("\nContingency Table:")
print(f"{'Morphology':<20} {'AGGRESSIVE':<12} {'MODERATE':<12} {'CONSERVATIVE':<12}")
print("-"*60)
for i, morph in enumerate(morph_cats):
    print(f"{morph:<20} {contingency[i,0]:<12} {contingency[i,1]:<12} {contingency[i,2]:<12}")

# Chi-square test (if cells are sufficient)
try:
    # Use Fisher's exact test approximation for small samples
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    v = cramers_v(contingency)
    print(f"\nChi-square: {chi2:.3f}")
    print(f"p-value: {p_value:.4f}")
    print(f"Cramer's V: {v:.3f}")

    # Interpretation
    if p_value < 0.05:
        print("RESULT: SIGNIFICANT correlation detected")
    else:
        print("RESULT: NO significant correlation")
except:
    print("Chi-square test not applicable (insufficient data)")

print("\n" + "-"*80)
print("TEST 2: LINK CLASS vs PRIMARY MORPHOLOGY")
print("-"*80)

link_cats = ['SPARSE', 'MODERATE', 'HEAVY']
contingency2 = np.zeros((len(morph_cats), len(link_cats)), dtype=int)
for m, l in zip(simple_morph, link_class):
    i = morph_cats.index(m)
    j = link_cats.index(l)
    contingency2[i, j] += 1

print("\nContingency Table:")
print(f"{'Morphology':<20} {'SPARSE':<12} {'MODERATE':<12} {'HEAVY':<12}")
print("-"*60)
for i, morph in enumerate(morph_cats):
    print(f"{morph:<20} {contingency2[i,0]:<12} {contingency2[i,1]:<12} {contingency2[i,2]:<12}")

try:
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency2)
    v = cramers_v(contingency2)
    print(f"\nChi-square: {chi2:.3f}")
    print(f"p-value: {p_value:.4f}")
    print(f"Cramer's V: {v:.3f}")

    if p_value < 0.05:
        print("RESULT: SIGNIFICANT correlation detected")
    else:
        print("RESULT: NO significant correlation")
except:
    print("Chi-square test not applicable")

print("\n" + "-"*80)
print("TEST 3: AGGRESSIVE PROGRAMS + ROOT_HEAVY MORPHOLOGY")
print("-"*80)

# Specific hypothesis: Are aggressive programs more likely with root-heavy plants?
aggressive_count = sum(1 for a in aggressiveness if a == 'AGGRESSIVE')
root_heavy_count = sum(1 for m in primary_morph if m == 'ROOT_HEAVY')
both_count = sum(1 for m, a in zip(primary_morph, aggressiveness) if m == 'ROOT_HEAVY' and a == 'AGGRESSIVE')

# Expected by chance
expected_both = (aggressive_count / len(folios)) * root_heavy_count

print(f"AGGRESSIVE programs: {aggressive_count}/24")
print(f"ROOT_HEAVY primary: {root_heavy_count}/24")
print(f"Both AGGRESSIVE + ROOT_HEAVY: {both_count}")
print(f"Expected by chance: {expected_both:.2f}")
print(f"Ratio observed/expected: {both_count/expected_both:.2f}" if expected_both > 0 else "N/A")

# Fisher's exact test for 2x2
is_root = [1 if m == 'ROOT_HEAVY' else 0 for m in primary_morph]
is_aggressive = [1 if a == 'AGGRESSIVE' else 0 for a in aggressiveness]

# 2x2 table: [[both, root_not_agg], [agg_not_root, neither]]
table_2x2 = [[sum(1 for r, a in zip(is_root, is_aggressive) if r==1 and a==1),
              sum(1 for r, a in zip(is_root, is_aggressive) if r==1 and a==0)],
             [sum(1 for r, a in zip(is_root, is_aggressive) if r==0 and a==1),
              sum(1 for r, a in zip(is_root, is_aggressive) if r==0 and a==0)]]

odds_ratio, p_fisher = stats.fisher_exact(table_2x2)
print(f"\nFisher's exact test:")
print(f"  2x2 table: {table_2x2}")
print(f"  Odds ratio: {odds_ratio:.3f}")
print(f"  p-value: {p_fisher:.4f}")

if p_fisher < 0.05:
    print("RESULT: SIGNIFICANT association")
else:
    print("RESULT: NO significant association")

print("\n" + "-"*80)
print("TEST 4: CONSERVATIVE/LINK_HEAVY + FLOWER_DOMINANT")
print("-"*80)

# Hypothesis: Are conservative, link-heavy programs associated with flower morphology?
conservative_heavy = sum(1 for a, l in zip(aggressiveness, link_class) if a == 'CONSERVATIVE' and l == 'HEAVY')
flower_count = sum(1 for m in primary_morph if m == 'FLOWER_DOMINANT')

# Count overlap
overlap = sum(1 for m, a, l in zip(primary_morph, aggressiveness, link_class)
              if m == 'FLOWER_DOMINANT' and a == 'CONSERVATIVE' and l == 'HEAVY')

print(f"CONSERVATIVE + HEAVY programs: {conservative_heavy}/24")
print(f"FLOWER_DOMINANT primary: {flower_count}/24")
print(f"Both: {overlap}")

# Fisher's exact for flower vs conservative
is_flower = [1 if m == 'FLOWER_DOMINANT' else 0 for m in primary_morph]
is_conservative = [1 if a == 'CONSERVATIVE' else 0 for a in aggressiveness]

table_2x2_b = [[sum(1 for f, c in zip(is_flower, is_conservative) if f==1 and c==1),
                sum(1 for f, c in zip(is_flower, is_conservative) if f==1 and c==0)],
               [sum(1 for f, c in zip(is_flower, is_conservative) if f==0 and c==1),
                sum(1 for f, c in zip(is_flower, is_conservative) if f==0 and c==0)]]

odds_ratio_b, p_fisher_b = stats.fisher_exact(table_2x2_b)
print(f"\nFisher's exact (FLOWER vs CONSERVATIVE):")
print(f"  2x2 table: {table_2x2_b}")
print(f"  Odds ratio: {odds_ratio_b:.3f}")
print(f"  p-value: {p_fisher_b:.4f}")

if p_fisher_b < 0.05:
    print("RESULT: SIGNIFICANT association")
else:
    print("RESULT: NO significant association")

print("\n" + "-"*80)
print("TEST 5: PERMUTATION TEST (AGGRESSIVE + ROOT_HEAVY)")
print("-"*80)

# Observed count
observed = both_count
n_perm = 10000
count_extreme = 0

np.random.seed(42)
for _ in range(n_perm):
    shuffled_agg = np.random.permutation(aggressiveness)
    shuffled_count = sum(1 for m, a in zip(primary_morph, shuffled_agg) if m == 'ROOT_HEAVY' and a == 'AGGRESSIVE')
    if shuffled_count >= observed:
        count_extreme += 1

p_perm = count_extreme / n_perm
print(f"Observed AGGRESSIVE + ROOT_HEAVY: {observed}")
print(f"Permutation p-value ({n_perm} permutations): {p_perm:.4f}")

if p_perm < 0.05:
    print("RESULT: SIGNIFICANT (non-random association)")
else:
    print("RESULT: NOT SIGNIFICANT (consistent with chance)")

print("\n" + "-"*80)
print("TEST 6: EXTENDED DURATION vs MORPHOLOGY")
print("-"*80)

# Are extended programs associated with specific morphologies?
extended_folios = [f for f in folios if program_metrics[f]['duration'] == 'EXTENDED']
extended_morph = Counter([morphology[f]['primary'] for f in extended_folios])

print(f"EXTENDED duration programs: {len(extended_folios)}")
print(f"Morphology distribution:")
for m, c in extended_morph.most_common():
    print(f"  {m}: {c}")

# Compare to overall distribution
overall_morph = Counter(primary_morph)
print(f"\nOverall morphology distribution:")
for m, c in overall_morph.most_common():
    print(f"  {m}: {c}")

print("\n" + "="*80)
print("SUMMARY TABLE: OBSERVED vs EXPECTED")
print("="*80)

print(f"\n{'Combination':<40} {'Observed':<10} {'Expected':<10} {'Ratio':<10}")
print("-"*70)

# Various combinations
combinations = [
    ('AGGRESSIVE + ROOT_HEAVY',
     sum(1 for m, a in zip(primary_morph, aggressiveness) if m == 'ROOT_HEAVY' and a == 'AGGRESSIVE'),
     (sum(1 for m in primary_morph if m == 'ROOT_HEAVY') * sum(1 for a in aggressiveness if a == 'AGGRESSIVE')) / len(folios)),

    ('AGGRESSIVE + FLOWER_DOMINANT',
     sum(1 for m, a in zip(primary_morph, aggressiveness) if m == 'FLOWER_DOMINANT' and a == 'AGGRESSIVE'),
     (sum(1 for m in primary_morph if m == 'FLOWER_DOMINANT') * sum(1 for a in aggressiveness if a == 'AGGRESSIVE')) / len(folios)),

    ('CONSERVATIVE + FLOWER_DOMINANT',
     sum(1 for m, a in zip(primary_morph, aggressiveness) if m == 'FLOWER_DOMINANT' and a == 'CONSERVATIVE'),
     (sum(1 for m in primary_morph if m == 'FLOWER_DOMINANT') * sum(1 for a in aggressiveness if a == 'CONSERVATIVE')) / len(folios)),

    ('LINK_HEAVY + FLOWER_DOMINANT',
     sum(1 for m, l in zip(primary_morph, link_class) if m == 'FLOWER_DOMINANT' and l == 'HEAVY'),
     (sum(1 for m in primary_morph if m == 'FLOWER_DOMINANT') * sum(1 for l in link_class if l == 'HEAVY')) / len(folios)),

    ('LINK_HEAVY + ROOT_HEAVY',
     sum(1 for m, l in zip(primary_morph, link_class) if m == 'ROOT_HEAVY' and l == 'HEAVY'),
     (sum(1 for m in primary_morph if m == 'ROOT_HEAVY') * sum(1 for l in link_class if l == 'HEAVY')) / len(folios)),
]

for name, obs, exp in combinations:
    ratio = obs / exp if exp > 0 else 'N/A'
    if isinstance(ratio, float):
        print(f"{name:<40} {obs:<10} {exp:<10.2f} {ratio:<10.2f}")
    else:
        print(f"{name:<40} {obs:<10} {exp:<10.2f} {ratio:<10}")

# Save results
results = {
    'test1_aggressiveness_morphology': {
        'chi2': chi2 if 'chi2' in dir() else None,
        'p_value': p_value if 'p_value' in dir() else None,
        'cramers_v': v if 'v' in dir() else None
    },
    'test3_aggressive_root_heavy': {
        'observed': both_count,
        'expected': expected_both,
        'fisher_odds': odds_ratio,
        'fisher_p': p_fisher
    },
    'test4_conservative_flower': {
        'fisher_odds': odds_ratio_b,
        'fisher_p': p_fisher_b
    },
    'test5_permutation': {
        'observed': observed,
        'p_value': p_perm
    },
    'combinations': [{'name': n, 'observed': o, 'expected': e, 'ratio': o/e if e > 0 else None} for n, o, e in combinations]
}

with open('correlation_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n\nResults saved to correlation_results.json")
