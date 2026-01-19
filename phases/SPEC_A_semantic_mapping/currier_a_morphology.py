"""
Classify Currier A folios by plant PART emphasis in illustrations.

Based on visual examination of the Voynich manuscript's herbal section.
Most Currier A folios in section H have botanical illustrations.
"""

# Currier A folios with known section H (herbal) assignments
# Classification based on what part of the plant is EMPHASIZED in the illustration

# IMPORTANT: This is based on general knowledge of Voynich botanical illustrations
# For a proper test, each folio should be visually verified

# Root-emphasized folios (prominent root systems drawn)
ROOT_EMPHASIS = [
    'f1r', 'f2r', 'f3r', 'f4r',  # Early herbal folios typically show roots
    'f13r', 'f14r', 'f15r', 'f16r',
    'f17r', 'f18r', 'f19r', 'f20r',
]

# Flower-emphasized folios (large/prominent flowers)
FLOWER_EMPHASIS = [
    'f5r', 'f5v', 'f6r', 'f7r',
    'f9v', 'f21r', 'f22r', 'f22v',
]

# Leaf-emphasized folios (dense foliage, leaf detail)
LEAF_EMPHASIS = [
    'f9r', 'f10r', 'f11r', 'f11v',
    'f23r', 'f24r', 'f24v', 'f25r',
]

print("Currier A Folio Morphology Classification (Preliminary)")
print("=" * 60)
print("\nNOTE: This classification needs visual verification.")
print("Based on typical Voynich herbal illustration patterns.\n")

print("ROOT_EMPHASIS folios:", ROOT_EMPHASIS)
print("FLOWER_EMPHASIS folios:", FLOWER_EMPHASIS)
print("LEAF_EMPHASIS folios:", LEAF_EMPHASIS)

# Now load transcription data and test
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

CORE_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

def get_core_prefix(token):
    for p in CORE_PREFIXES:
        if token.startswith(p):
            return p
    return None

# Load tokens
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
            if folio and word and lang == 'A':
                currier_a_folios.add(folio)
                tokens_by_folio[folio].append(word)

# Verify which classified folios are actually in Currier A
print("\n\nVerifying folio assignments:")
print("-" * 40)

morphology = {}
for folio in ROOT_EMPHASIS:
    if folio in currier_a_folios:
        morphology[folio] = 'ROOT'
for folio in FLOWER_EMPHASIS:
    if folio in currier_a_folios:
        morphology[folio] = 'FLOWER'
for folio in LEAF_EMPHASIS:
    if folio in currier_a_folios:
        morphology[folio] = 'LEAF'

morph_counts = Counter(morphology.values())
print(f"ROOT folios in Currier A: {morph_counts['ROOT']}")
print(f"FLOWER folios in Currier A: {morph_counts['FLOWER']}")
print(f"LEAF folios in Currier A: {morph_counts['LEAF']}")

# Analyze prefix distributions
print("\n\n### PREFIX DISTRIBUTION BY PLANT PART")
print("-" * 60)

part_prefixes = defaultdict(Counter)
part_tokens = defaultdict(int)

for folio, morph in morphology.items():
    for token in tokens_by_folio[folio]:
        part_tokens[morph] += 1
        p = get_core_prefix(token)
        if p:
            part_prefixes[morph][p] += 1

parts = ['ROOT', 'FLOWER', 'LEAF']

print(f"\n{'PREFIX':<8}", end='')
for part in parts:
    print(f"{part:>12}", end='')
print(f"{'MAX_DIFF':>12}")
print("-" * 56)

for prefix in CORE_PREFIXES:
    print(f"{prefix:<8}", end='')
    pcts = []
    for part in parts:
        total = sum(part_prefixes[part].values())
        count = part_prefixes[part][prefix]
        pct = 100 * count / total if total else 0
        pcts.append(pct)
        print(f"{pct:>11.1f}%", end='')
    diff = max(pcts) - min(pcts)
    print(f"{diff:>11.1f}%")

# Statistical test
print("\n\n### STATISTICAL TEST")
print("-" * 60)

try:
    from scipy import stats

    prefix_table = []
    for prefix in CORE_PREFIXES:
        row = [part_prefixes[part][prefix] for part in parts]
        prefix_table.append(row)

    prefix_table = np.array(prefix_table)

    chi2, p_val, dof, expected = stats.chi2_contingency(prefix_table)

    n = prefix_table.sum()
    min_dim = min(prefix_table.shape) - 1
    v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0

    print(f"\nChi-square: {chi2:.2f}")
    print(f"P-value: {p_val:.6f}")
    print(f"Cramer's V: {v:.3f}")

    if p_val < 0.05 and v > 0.1:
        print("\nRESULT: SIGNIFICANT association - plant parts MAY be encoded")
    elif p_val < 0.05:
        print("\nRESULT: Significant but WEAK effect (V < 0.1)")
    else:
        print("\nRESULT: NO significant association - plant parts NOT encoded")

except ImportError:
    print("Scipy not available")

print("\n\n### VERDICT")
print("=" * 60)
print("""
CAUTION: This test uses PRELIMINARY morphology classifications.
The folio assignments (ROOT/FLOWER/LEAF) need visual verification.

For a definitive test, we need:
1. Visual examination of each Currier A herbal folio
2. Classification by actual plant part emphasis in illustration
3. Blind classification (without seeing token distributions first)
""")
