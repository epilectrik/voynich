"""
Test: Does Currier A structure encode plant parts?

If plant parts ARE encoded, we expect:
- ROOT_DOMINATED folios to have different PREFIX/SUFFIX distributions
- FLOWER_DOMINATED folios to have different PREFIX/SUFFIX distributions
- Statistically significant association between morphology and structure

Tier 2 TEST - structural correlation analysis
"""

from collections import defaultdict, Counter
from pathlib import Path
from scipy import stats
import numpy as np

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

CORE_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SUFFIXES = ['daiin', 'aiin', 'ain', 'dy', 'edy', 'ody', 'or', 'eor', 'ar',
            'ol', 'eol', 'al', 'chy', 'hy', 'y', 'ey', 'am', 'om', 'in']

# Morphology classifications from PPC phase
MORPHOLOGY = {
    # ROOT_DOMINATED
    'f26r': 'ROOT', 'f26v': 'ROOT', 'f31r': 'ROOT', 'f34r': 'ROOT',
    'f39r': 'ROOT', 'f41v': 'ROOT', 'f43r': 'ROOT', 'f55v': 'ROOT',
    # FLOWER_DOMINATED
    'f33r': 'FLOWER', 'f39v': 'FLOWER', 'f40r': 'FLOWER', 'f40v': 'FLOWER',
    'f46v': 'FLOWER', 'f50r': 'FLOWER', 'f50v': 'FLOWER',
    # LEAF_DOMINATED
    'f33v': 'LEAF', 'f41r': 'LEAF', 'f46r': 'LEAF',
    'f48r': 'LEAF', 'f48v': 'LEAF', 'f55r': 'LEAF',
    # WOODY_STRUCTURE
    'f34v': 'WOODY',
    # COMPOSITE/AMBIGUOUS
    'f31v': 'COMPOSITE', 'f43v': 'COMPOSITE',
}

def get_core_prefix(token):
    for p in CORE_PREFIXES:
        if token.startswith(p):
            return p
    return None

def get_suffix(token):
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if token.endswith(s):
            return s
    return None

# Load tokens by folio
tokens_by_folio = defaultdict(list)
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue
            lang = parts[6].strip('"').strip()
            if lang == 'A':
                word = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                if word and folio:
                    tokens_by_folio[folio].append(word)

print("=" * 80)
print("TEST: PLANT PART ENCODING IN CURRIER A")
print("=" * 80)
print("\nH0: PREFIX/SUFFIX distributions are INDEPENDENT of plant morphology")
print("H1: Plant parts ARE encoded in the compositional structure\n")

# Get prefix/suffix distributions by morphology class
morph_prefixes = defaultdict(Counter)
morph_suffixes = defaultdict(Counter)
morph_tokens = defaultdict(int)

for folio, morph in MORPHOLOGY.items():
    if folio in tokens_by_folio:
        for token in tokens_by_folio[folio]:
            morph_tokens[morph] += 1
            p = get_core_prefix(token)
            s = get_suffix(token)
            if p:
                morph_prefixes[morph][p] += 1
            if s:
                morph_suffixes[morph][s] += 1

print("### 1. TOKEN COUNTS BY MORPHOLOGY CLASS")
print("-" * 60)
for morph in ['ROOT', 'FLOWER', 'LEAF', 'WOODY', 'COMPOSITE']:
    print(f"  {morph}: {morph_tokens[morph]} tokens")

# Focus on ROOT vs FLOWER vs LEAF (enough data)
main_classes = ['ROOT', 'FLOWER', 'LEAF']

print("\n\n### 2. PREFIX DISTRIBUTION BY MORPHOLOGY")
print("-" * 60)

print(f"\n{'PREFIX':<8}", end='')
for morph in main_classes:
    print(f"{morph:>12}", end='')
print()
print("-" * 45)

for prefix in CORE_PREFIXES:
    print(f"{prefix:<8}", end='')
    for morph in main_classes:
        total = sum(morph_prefixes[morph].values())
        count = morph_prefixes[morph][prefix]
        pct = 100 * count / total if total else 0
        print(f"{pct:>11.1f}%", end='')
    print()

# Chi-square test for prefix independence
print("\n\n### 3. CHI-SQUARE TEST: PREFIX x MORPHOLOGY")
print("-" * 60)

# Build contingency table for main classes
prefix_table = []
for prefix in CORE_PREFIXES:
    row = [morph_prefixes[morph][prefix] for morph in main_classes]
    prefix_table.append(row)

prefix_table = np.array(prefix_table)
chi2, p_prefix, dof, expected = stats.chi2_contingency(prefix_table)

print(f"\nChi-square statistic: {chi2:.2f}")
print(f"Degrees of freedom: {dof}")
print(f"P-value: {p_prefix:.6f}")

if p_prefix < 0.05:
    print("\nRESULT: SIGNIFICANT (p < 0.05)")
    print("PREFIX distributions DIFFER by morphology class")
else:
    print("\nRESULT: NOT SIGNIFICANT (p >= 0.05)")
    print("PREFIX distributions are INDEPENDENT of morphology")

# Suffix analysis
print("\n\n### 4. SUFFIX DISTRIBUTION BY MORPHOLOGY")
print("-" * 60)

# Get top suffixes
all_suffixes = Counter()
for morph in main_classes:
    all_suffixes.update(morph_suffixes[morph])
top_suffixes = [s for s, _ in all_suffixes.most_common(10)]

print(f"\n{'SUFFIX':<12}", end='')
for morph in main_classes:
    print(f"{morph:>12}", end='')
print()
print("-" * 50)

for suffix in top_suffixes:
    print(f"-{suffix:<11}", end='')
    for morph in main_classes:
        total = sum(morph_suffixes[morph].values())
        count = morph_suffixes[morph][suffix]
        pct = 100 * count / total if total else 0
        print(f"{pct:>11.1f}%", end='')
    print()

# Chi-square for suffix
print("\n\n### 5. CHI-SQUARE TEST: SUFFIX x MORPHOLOGY")
print("-" * 60)

suffix_table = []
for suffix in top_suffixes:
    row = [morph_suffixes[morph][suffix] for morph in main_classes]
    suffix_table.append(row)

suffix_table = np.array(suffix_table)
chi2_s, p_suffix, dof_s, expected_s = stats.chi2_contingency(suffix_table)

print(f"\nChi-square statistic: {chi2_s:.2f}")
print(f"Degrees of freedom: {dof_s}")
print(f"P-value: {p_suffix:.6f}")

if p_suffix < 0.05:
    print("\nRESULT: SIGNIFICANT (p < 0.05)")
    print("SUFFIX distributions DIFFER by morphology class")
else:
    print("\nRESULT: NOT SIGNIFICANT (p >= 0.05)")
    print("SUFFIX distributions are INDEPENDENT of morphology")

# Effect size analysis
print("\n\n### 6. EFFECT SIZE: CRAMÉR'S V")
print("-" * 60)

def cramers_v(contingency_table):
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum()
    min_dim = min(contingency_table.shape) - 1
    return np.sqrt(chi2 / (n * min_dim))

v_prefix = cramers_v(prefix_table)
v_suffix = cramers_v(suffix_table)

print(f"\nPREFIX x MORPHOLOGY: Cramér's V = {v_prefix:.3f}")
print(f"SUFFIX x MORPHOLOGY: Cramér's V = {v_suffix:.3f}")

print("\nInterpretation (Cramér's V):")
print("  < 0.1 = negligible")
print("  0.1-0.3 = small")
print("  0.3-0.5 = medium")
print("  > 0.5 = large")

# Look for specific associations
print("\n\n### 7. SPECIFIC ASSOCIATIONS (Residual Analysis)")
print("-" * 60)
print("\nLooking for PREFIX-MORPHOLOGY pairs with strong residuals...")

chi2, p, dof, expected = stats.chi2_contingency(prefix_table)
residuals = (prefix_table - expected) / np.sqrt(expected)

print(f"\n{'PREFIX':<8}", end='')
for morph in main_classes:
    print(f"{morph:>12}", end='')
print()
print("-" * 45)

for i, prefix in enumerate(CORE_PREFIXES):
    print(f"{prefix:<8}", end='')
    for j, morph in enumerate(main_classes):
        r = residuals[i, j]
        if r > 2:
            marker = "++"
        elif r > 1:
            marker = "+"
        elif r < -2:
            marker = "--"
        elif r < -1:
            marker = "-"
        else:
            marker = "~"
        print(f"{marker:>12}", end='')
    print()

print("\nLegend: ++ strong positive, + positive, ~ neutral, - negative, -- strong negative")

# Conclusion
print("\n\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

if p_prefix < 0.05 and v_prefix > 0.1:
    print("""
FINDING: There IS a statistically significant association between
PREFIX distributions and plant morphology (p < 0.05, V > 0.1).

However, this could reflect:
  1. Plant parts ARE encoded in prefixes
  2. Folios with similar morphology are adjacent (spatial clustering)
  3. Section effects (all are section H)
  4. Coincidental variation in small sample

FURTHER TESTING REQUIRED to distinguish these hypotheses.
""")
elif p_prefix < 0.05:
    print("""
FINDING: Statistically significant but WEAK effect.

The association exists but effect size is negligible (V < 0.1).
This is likely noise or sampling artifact, not meaningful encoding.
""")
else:
    print("""
FINDING: NO significant association between PREFIX and plant morphology.

PREFIX distributions are INDEPENDENT of whether the illustration
emphasizes roots, flowers, or leaves.

PLANT PARTS ARE NOT ENCODED in the PREFIX component.
""")

if p_suffix < 0.05 and v_suffix > 0.1:
    print("""
SUFFIX FINDING: Significant association detected.
Suffixes may carry morphology-related information.
""")
else:
    print("""
SUFFIX FINDING: No significant association.
PLANT PARTS ARE NOT ENCODED in the SUFFIX component.
""")

print("""
OVERALL VERDICT:
""")
if p_prefix >= 0.05 and p_suffix >= 0.05:
    print("PLANT PARTS ARE NOT ENCODED in Currier A structure.")
    print("The compositional system (PREFIX+MIDDLE+SUFFIX) is INDEPENDENT")
    print("of the botanical morphology shown in illustrations.")
elif (p_prefix < 0.05 and v_prefix > 0.1) or (p_suffix < 0.05 and v_suffix > 0.1):
    print("WEAK EVIDENCE for plant-part encoding detected.")
    print("Further testing with larger sample recommended.")
else:
    print("Statistical significance without practical effect size.")
    print("Plant-part encoding hypothesis NOT SUPPORTED.")
