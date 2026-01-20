"""
TEST 2: Diagram-Type Stratification (HIGH)

Goal: Check whether scatter/ring/segmented/nymph diagrams differ functionally

Protocol:
1. Group AZC folios by diagram type
2. Compare across groups:
   - Vocabulary profile (PREFIX, MIDDLE)
   - Token count per folio
   - Placement code distribution
3. Expected: Same functional signatures across diagram styles

Diagram types from visual audit:
- STANDARD_RING: Standard ring diagrams (most folios)
- SCATTER: Scatter diagrams without ring structure (f68r1, f68r2)
- SEGMENTED: Segmented rings (f67r1, f67r2, f68v3)
- NYMPH: Nymph-interrupted rings (f70v2-f73v)
"""

import os
import json
from collections import defaultdict, Counter
import numpy as np

os.chdir('C:/git/voynich')

# Load official AZC folio structure
with open('phases/AZC_astronomical_zodiac_cosmological/azc_folio_structure.json', 'r', encoding='utf-8') as f:
    azc_structure = json.load(f)

AZC_FOLIOS = set(azc_structure['per_folio'].keys())

# Define diagram type groupings from visual audit
DIAGRAM_TYPES = {
    'SCATTER': {'f68r1', 'f68r2'},  # Scatter diagrams, no ring structure
    'SEGMENTED': {'f67r1', 'f67r2', 'f68v3'},  # Segmented/divided rings
    'NYMPH': {'f70v1', 'f70v2', 'f71r', 'f71v', 'f72r1', 'f72r2', 'f72r3',
              'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v'},  # Nymph-interrupted
    # All remaining are STANDARD_RING
}

# Compute STANDARD_RING as complement
all_special = set()
for dt in DIAGRAM_TYPES.values():
    all_special.update(dt)
DIAGRAM_TYPES['STANDARD_RING'] = AZC_FOLIOS - all_special

# Load transcript
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Parse all H-track AZC tokens
azc_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        if row.get('transcriber', '').strip() == 'H':
            if row.get('folio', '') in AZC_FOLIOS:
                azc_tokens.append(row)

print("=" * 70)
print("TEST 2: DIAGRAM-TYPE STRATIFICATION")
print("=" * 70)

# Group tokens by diagram type
tokens_by_type = defaultdict(list)
for t in azc_tokens:
    folio = t.get('folio', '')
    for dtype, folios in DIAGRAM_TYPES.items():
        if folio in folios:
            tokens_by_type[dtype].append(t)
            break

print(f"\n1. DIAGRAM TYPE DISTRIBUTION")
print("-" * 40)
for dtype in ['STANDARD_RING', 'SCATTER', 'SEGMENTED', 'NYMPH']:
    folios = DIAGRAM_TYPES[dtype]
    tokens = tokens_by_type[dtype]
    print(f"  {dtype:15s}: {len(folios):2d} folios, {len(tokens):5,} tokens")

# Exclude P-text for diagram analysis (per TEST 1 result)
tokens_by_type_noP = defaultdict(list)
for dtype, tokens in tokens_by_type.items():
    tokens_by_type_noP[dtype] = [t for t in tokens if t.get('placement', '').strip() != 'P']

print(f"\n2. AFTER P-TEXT EXCLUSION")
print("-" * 40)
for dtype in ['STANDARD_RING', 'SCATTER', 'SEGMENTED', 'NYMPH']:
    tokens = tokens_by_type_noP[dtype]
    print(f"  {dtype:15s}: {len(tokens):5,} tokens")

# Helper functions
def get_vocab(tokens):
    return Counter(t.get('word', '') for t in tokens if t.get('word', '').strip())

def get_prefix_dist(tokens):
    prefixes = Counter()
    for t in tokens:
        tok = t.get('word', '').strip()
        if len(tok) >= 2:
            for pfx in ['qo', 'cho', 'ch', 'sh', 'ok', 'ot', 'd', 's', 'y', 'o']:
                if tok.startswith(pfx):
                    prefixes[pfx] += 1
                    break
    return prefixes

def cosine_sim(c1, c2):
    all_keys = set(c1.keys()) | set(c2.keys())
    if not all_keys:
        return 0
    v1 = np.array([c1.get(k, 0) for k in all_keys])
    v2 = np.array([c2.get(k, 0) for k in all_keys])
    norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return np.dot(v1, v2) / (norm1 * norm2)

# PREFIX distribution by diagram type
print(f"\n3. PREFIX DISTRIBUTION BY DIAGRAM TYPE")
print("-" * 40)
prefix_by_type = {}
for dtype in ['STANDARD_RING', 'SCATTER', 'SEGMENTED', 'NYMPH']:
    tokens = tokens_by_type_noP[dtype]
    prefix_by_type[dtype] = get_prefix_dist(tokens)
    total = sum(prefix_by_type[dtype].values())
    if total > 0:
        top3 = prefix_by_type[dtype].most_common(3)
        top_str = ", ".join(f"{p}:{c/total:.1%}" for p, c in top3)
        print(f"  {dtype:15s}: {top_str}")

# PREFIX cosine similarity matrix
print(f"\n4. PREFIX COSINE SIMILARITY MATRIX")
print("-" * 40)
types = ['STANDARD_RING', 'SCATTER', 'SEGMENTED', 'NYMPH']
print(f"  {'':15s}", end="")
for t in types:
    print(f"{t[:8]:>10s}", end="")
print()
for t1 in types:
    print(f"  {t1:15s}", end="")
    for t2 in types:
        sim = cosine_sim(prefix_by_type[t1], prefix_by_type[t2])
        print(f"{sim:10.4f}", end="")
    print()

# Vocabulary overlap
print(f"\n5. VOCABULARY OVERLAP (Jaccard)")
print("-" * 40)
vocab_by_type = {dtype: get_vocab(tokens_by_type_noP[dtype]) for dtype in types}
print(f"  {'':15s}", end="")
for t in types:
    print(f"{t[:8]:>10s}", end="")
print()
for t1 in types:
    print(f"  {t1:15s}", end="")
    for t2 in types:
        s1, s2 = set(vocab_by_type[t1].keys()), set(vocab_by_type[t2].keys())
        jaccard = len(s1 & s2) / len(s1 | s2) if len(s1 | s2) > 0 else 0
        print(f"{jaccard:10.4f}", end="")
    print()

# Placement code distribution
print(f"\n6. PLACEMENT CODE DISTRIBUTION BY TYPE")
print("-" * 40)
for dtype in types:
    tokens = tokens_by_type_noP[dtype]
    placements = Counter(t.get('placement', '') for t in tokens)
    total = sum(placements.values())
    if total > 0:
        top5 = placements.most_common(5)
        top_str = ", ".join(f"{p}:{c/total:.1%}" for p, c in top5)
        print(f"  {dtype:15s}: {top_str}")

# Uniformity test: Do all types show similar PREFIX profile?
print(f"\n" + "=" * 70)
print("UNIFORMITY ASSESSMENT")
print("=" * 70)

# Compare each type to the pooled AZC diagram profile
pooled_prefix = Counter()
for dtype in types:
    pooled_prefix.update(prefix_by_type[dtype])

print(f"\n  Cosine to pooled AZC diagram profile:")
uniformity_scores = {}
for dtype in types:
    sim = cosine_sim(prefix_by_type[dtype], pooled_prefix)
    uniformity_scores[dtype] = sim
    status = "UNIFORM" if sim > 0.90 else "DISTINCT" if sim < 0.80 else "MARGINAL"
    print(f"    {dtype:15s}: {sim:.4f} ({status})")

# Summary
avg_uniformity = np.mean(list(uniformity_scores.values()))
min_uniformity = min(uniformity_scores.values())

print(f"\n  SUMMARY:")
print(f"    Average uniformity: {avg_uniformity:.4f}")
print(f"    Minimum uniformity: {min_uniformity:.4f}")

if min_uniformity > 0.85:
    verdict = "UNIFORM"
    interpretation = "Visual diagram variation is INTERFACE only - same functional signature"
elif min_uniformity > 0.70:
    verdict = "MOSTLY UNIFORM"
    interpretation = "Minor functional differences - investigate outliers"
else:
    verdict = "HETEROGENEOUS"
    interpretation = "Diagram types encode DIFFERENT linguistic functions"

print(f"\n  VERDICT: {verdict}")
print(f"  INTERPRETATION: {interpretation}")

# Save results
results = {
    "test": "TEST 2: Diagram-Type Stratification",
    "status": "COMPLETE",
    "diagram_types": {
        dtype: {
            "folios": sorted(list(DIAGRAM_TYPES[dtype])),
            "token_count": len(tokens_by_type_noP[dtype]),
            "uniformity_to_pooled": uniformity_scores[dtype]
        }
        for dtype in types
    },
    "prefix_similarity_matrix": {
        t1: {t2: cosine_sim(prefix_by_type[t1], prefix_by_type[t2]) for t2 in types}
        for t1 in types
    },
    "summary": {
        "avg_uniformity": avg_uniformity,
        "min_uniformity": min_uniformity,
        "verdict": verdict,
        "interpretation": interpretation
    }
}

with open('results/test2_diagram_stratification.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n" + "=" * 70)
print("TEST 2 COMPLETE")
print("=" * 70)
print(f"\nResults saved to: results/test2_diagram_stratification.json")
