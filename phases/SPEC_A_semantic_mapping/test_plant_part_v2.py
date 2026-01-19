"""
Test: Does Currier A structure encode plant parts?

Using plant classifications from PIAA phase that apply to Currier A folios.

Tier 2 TEST - structural correlation analysis
"""

from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

CORE_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SUFFIXES = ['daiin', 'aiin', 'ain', 'dy', 'edy', 'ody', 'or', 'eor', 'ar',
            'ol', 'eol', 'al', 'chy', 'hy', 'y', 'ey', 'am', 'om', 'in']

# First, identify which folios are Currier A
currier_a_folios = set()
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
            folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
            word = parts[0].strip('"').strip().lower()
            if folio and word:
                if lang == 'A':
                    currier_a_folios.add(folio)
                    tokens_by_folio[folio].append(word)

# Plant class assignments from PIAA phase (for Currier A folios only)
# Classes: AF (Aromatic Flower), ALH (Aromatic Leaf Herb), AS (Aromatic Shrub),
#          RT (Resinous Tree), MH (Medicinal Herb)
PLANT_CLASSES = {
    'f2r': 'ALH',   # Aromatic Leaf Herb
    'f5r': 'AF',    # Aromatic Flower
    'f5v': 'AF',    # Aromatic Flower
    'f9r': 'ALH',   # Aromatic Leaf Herb (umbellifer)
    'f9v': 'AF',    # Aromatic Flower
    'f11r': 'AS',   # Aromatic Shrub
    'f11v': 'AS',   # Aromatic Shrub/Tree
    'f17r': 'AF',   # Aromatic Flower
    'f18r': 'MH',   # Medicinal Herb
    'f19r': 'ALH',  # Aromatic Leaf Herb
    'f21r': 'AF',   # Aromatic Flower
    'f22r': 'AF',   # Aromatic Flower
    'f22v': 'AF',   # Aromatic Flower
    'f24v': 'ALH',  # Aromatic Leaf Herb
    'f25r': 'ALH',  # Aromatic Leaf Herb
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

print("=" * 80)
print("TEST: PLANT CLASS ENCODING IN CURRIER A")
print("=" * 80)

# Check which plant-classified folios are in Currier A
print("\n### 1. FOLIO VERIFICATION")
print("-" * 60)

valid_folios = {}
for folio, plant_class in PLANT_CLASSES.items():
    if folio in currier_a_folios:
        valid_folios[folio] = plant_class
        token_count = len(tokens_by_folio[folio])
        print(f"  {folio}: {plant_class} ({token_count} tokens) - IN CURRIER A")
    else:
        print(f"  {folio}: {plant_class} - NOT IN CURRIER A")

print(f"\nValid folios for analysis: {len(valid_folios)}")

if len(valid_folios) < 5:
    print("\nINSUFFICIENT DATA for statistical testing.")
    print("Need to classify more Currier A folios by plant morphology.")
    exit()

# Analyze prefix/suffix distributions by plant class
print("\n\n### 2. PREFIX DISTRIBUTION BY PLANT CLASS")
print("-" * 60)

class_prefixes = defaultdict(Counter)
class_tokens = defaultdict(int)

for folio, plant_class in valid_folios.items():
    for token in tokens_by_folio[folio]:
        class_tokens[plant_class] += 1
        p = get_core_prefix(token)
        if p:
            class_prefixes[plant_class][p] += 1

# Get classes with enough data
active_classes = [c for c in class_prefixes.keys() if sum(class_prefixes[c].values()) >= 20]
print(f"\nClasses with sufficient data: {active_classes}")

print(f"\n{'PREFIX':<8}", end='')
for cls in active_classes:
    print(f"{cls:>12}", end='')
print()
print("-" * (8 + 12 * len(active_classes)))

for prefix in CORE_PREFIXES:
    print(f"{prefix:<8}", end='')
    for cls in active_classes:
        total = sum(class_prefixes[cls].values())
        count = class_prefixes[cls][prefix]
        pct = 100 * count / total if total else 0
        print(f"{pct:>11.1f}%", end='')
    print()

# Look for differential patterns
print("\n\n### 3. DIFFERENTIAL ANALYSIS")
print("-" * 60)
print("\nLooking for prefixes that distinguish plant classes...")

# Compare each class pair
if len(active_classes) >= 2:
    from itertools import combinations
    for c1, c2 in combinations(active_classes, 2):
        print(f"\n{c1} vs {c2}:")
        t1 = sum(class_prefixes[c1].values())
        t2 = sum(class_prefixes[c2].values())

        diffs = []
        for p in CORE_PREFIXES:
            p1 = class_prefixes[c1][p] / t1 if t1 else 0
            p2 = class_prefixes[c2][p] / t2 if t2 else 0
            diff = abs(p1 - p2)
            diffs.append((p, p1, p2, diff))

        # Sort by difference
        diffs.sort(key=lambda x: -x[3])
        for p, pct1, pct2, diff in diffs[:3]:
            direction = ">" if pct1 > pct2 else "<"
            print(f"  {p}: {100*pct1:.1f}% {direction} {100*pct2:.1f}% (diff={100*diff:.1f}%)")

# Suffix analysis
print("\n\n### 4. SUFFIX DISTRIBUTION BY PLANT CLASS")
print("-" * 60)

class_suffixes = defaultdict(Counter)
for folio, plant_class in valid_folios.items():
    for token in tokens_by_folio[folio]:
        s = get_suffix(token)
        if s:
            class_suffixes[plant_class][s] += 1

# Top suffixes
all_suf = Counter()
for cls in active_classes:
    all_suf.update(class_suffixes[cls])
top_suf = [s for s, _ in all_suf.most_common(8)]

print(f"\n{'SUFFIX':<12}", end='')
for cls in active_classes:
    print(f"{cls:>12}", end='')
print()
print("-" * (12 + 12 * len(active_classes)))

for suffix in top_suf:
    print(f"-{suffix:<11}", end='')
    for cls in active_classes:
        total = sum(class_suffixes[cls].values())
        count = class_suffixes[cls][suffix]
        pct = 100 * count / total if total else 0
        print(f"{pct:>11.1f}%", end='')
    print()

# Statistical test if enough data
print("\n\n### 5. STATISTICAL SIGNIFICANCE")
print("-" * 60)

try:
    from scipy import stats

    # Build contingency table
    prefix_table = []
    for prefix in CORE_PREFIXES:
        row = [class_prefixes[cls][prefix] for cls in active_classes]
        prefix_table.append(row)

    prefix_table = np.array(prefix_table)

    # Remove rows/cols with all zeros
    prefix_table = prefix_table[prefix_table.sum(axis=1) > 0]
    prefix_table = prefix_table[:, prefix_table.sum(axis=0) > 0]

    if prefix_table.size > 0 and prefix_table.min() >= 0:
        chi2, p_val, dof, expected = stats.chi2_contingency(prefix_table)

        # Cramér's V
        n = prefix_table.sum()
        min_dim = min(prefix_table.shape) - 1
        if min_dim > 0 and n > 0:
            v = np.sqrt(chi2 / (n * min_dim))
        else:
            v = 0

        print(f"\nChi-square: {chi2:.2f}")
        print(f"P-value: {p_val:.4f}")
        print(f"Cramér's V: {v:.3f}")

        if p_val < 0.05 and v > 0.1:
            print("\nRESULT: SIGNIFICANT association between PREFIX and plant class")
        elif p_val < 0.05:
            print("\nRESULT: Statistically significant but WEAK effect (V < 0.1)")
        else:
            print("\nRESULT: NO significant association")
    else:
        print("\nInsufficient data for chi-square test")

except ImportError:
    print("\nScipy not available - skipping statistical test")

# Conclusion
print("\n\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

print(f"""
DATA AVAILABLE:
  - {len(valid_folios)} Currier A folios with plant classifications
  - {sum(class_tokens.values())} total tokens analyzed
  - {len(active_classes)} plant classes with sufficient data

OBSERVATION:
  The test is LIMITED by small sample size.
  We need morphology classifications for MORE Currier A folios
  to properly test plant-part encoding.

CURRENT EVIDENCE:
""")

# Check if any prefix shows >10% differential across classes
max_diff = 0
max_prefix = None
if len(active_classes) >= 2:
    for p in CORE_PREFIXES:
        pcts = []
        for cls in active_classes:
            total = sum(class_prefixes[cls].values())
            if total > 0:
                pcts.append(class_prefixes[cls][p] / total)
        if pcts:
            diff = max(pcts) - min(pcts)
            if diff > max_diff:
                max_diff = diff
                max_prefix = p

if max_diff > 0.10:
    print(f"  PREFIX '{max_prefix}' shows {100*max_diff:.1f}% differential across classes")
    print("  This SUGGESTS possible plant-class encoding, but sample size is small")
else:
    print("  No PREFIX shows >10% differential across plant classes")
    print("  PLANT CLASS encoding in PREFIX is NOT SUPPORTED by current data")
