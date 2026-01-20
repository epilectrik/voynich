"""
TEST 4: Nymph-Interrupted vs Continuous Rings (MEDIUM)

Goal: Test whether visual interruption (nymph occlusion) has functional consequences

Protocol:
1. Compare S-interrupted rings (nymph pages f70v2-f73v) vs continuous rings
2. Measure linguistic profile differences
3. Determine if nymph interruption is decorative or functional

Outcomes:
| Result | Interpretation |
|--------|---------------|
| Same profile | Nymphs are decorative occlusions (consistent with C137) |
| Different profile | Interruption encodes attention pacing (new constraint) |
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

# Define nymph vs non-nymph folios
NYMPH_FOLIOS = {'f70v1', 'f70v2', 'f71r', 'f71v', 'f72r1', 'f72r2', 'f72r3',
                'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v'}
NON_NYMPH_FOLIOS = AZC_FOLIOS - NYMPH_FOLIOS

# Define ring placement codes
CONTINUOUS_RING_CODES = {'R', 'R1', 'R2', 'R3', 'R4', 'O', 'C'}  # Continuous
INTERRUPTED_RING_CODES = {'S', 'S0', 'S1', 'S2', 'S3'}  # Nymph-interrupted

# Load transcript
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Parse all H-track AZC tokens (excluding P-text per TEST 1)
azc_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        if row.get('transcriber', '').strip() == 'H':
            if row.get('folio', '') in AZC_FOLIOS:
                if row.get('placement', '').strip() != 'P':
                    azc_tokens.append(row)

print("=" * 70)
print("TEST 4: NYMPH-INTERRUPTED vs CONTINUOUS RINGS")
print("=" * 70)

# Separate by folio type
nymph_tokens = [t for t in azc_tokens if t.get('folio', '') in NYMPH_FOLIOS]
non_nymph_tokens = [t for t in azc_tokens if t.get('folio', '') in NON_NYMPH_FOLIOS]

print(f"\n1. FOLIO TYPE DISTRIBUTION")
print("-" * 40)
print(f"  Nymph folios: {len(NYMPH_FOLIOS):2d}, {len(nymph_tokens):,} tokens")
print(f"  Non-nymph folios: {len(NON_NYMPH_FOLIOS):2d}, {len(non_nymph_tokens):,} tokens")

# Within nymph folios: S (interrupted) vs R (continuous)
nymph_interrupted = [t for t in nymph_tokens
                     if t.get('placement', '').strip() in INTERRUPTED_RING_CODES]
nymph_continuous = [t for t in nymph_tokens
                    if t.get('placement', '').strip() in CONTINUOUS_RING_CODES]
nymph_other = [t for t in nymph_tokens
               if t.get('placement', '').strip() not in INTERRUPTED_RING_CODES | CONTINUOUS_RING_CODES]

print(f"\n2. NYMPH FOLIO BREAKDOWN")
print("-" * 40)
print(f"  S-interrupted rings: {len(nymph_interrupted):,} tokens")
print(f"  R-continuous rings: {len(nymph_continuous):,} tokens")
print(f"  Other (center, etc.): {len(nymph_other):,} tokens")

# Non-nymph breakdown
non_nymph_continuous = [t for t in non_nymph_tokens
                        if t.get('placement', '').strip() in CONTINUOUS_RING_CODES]
non_nymph_other = [t for t in non_nymph_tokens
                   if t.get('placement', '').strip() not in CONTINUOUS_RING_CODES]

print(f"\n3. NON-NYMPH FOLIO BREAKDOWN")
print("-" * 40)
print(f"  Continuous rings: {len(non_nymph_continuous):,} tokens")
print(f"  Other: {len(non_nymph_other):,} tokens")

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

# PREFIX distribution comparison
print(f"\n4. PREFIX DISTRIBUTION")
print("-" * 40)
prefix_interrupted = get_prefix_dist(nymph_interrupted)
prefix_nymph_cont = get_prefix_dist(nymph_continuous)
prefix_non_nymph_cont = get_prefix_dist(non_nymph_continuous)

for name, dist in [("S-interrupted", prefix_interrupted),
                   ("Nymph R-cont", prefix_nymph_cont),
                   ("Non-nymph cont", prefix_non_nymph_cont)]:
    total = sum(dist.values())
    if total > 0:
        top3 = dist.most_common(3)
        top_str = ", ".join(f"{p}:{c/total:.1%}" for p, c in top3)
        print(f"  {name:15s}: {top_str}")

# PREFIX cosine similarity matrix
print(f"\n5. PREFIX COSINE SIMILARITY")
print("-" * 40)
print(f"  S-interrupted vs Nymph R-cont: {cosine_sim(prefix_interrupted, prefix_nymph_cont):.4f}")
print(f"  S-interrupted vs Non-nymph cont: {cosine_sim(prefix_interrupted, prefix_non_nymph_cont):.4f}")
print(f"  Nymph R-cont vs Non-nymph cont: {cosine_sim(prefix_nymph_cont, prefix_non_nymph_cont):.4f}")

# Token length analysis
print(f"\n6. TOKEN LENGTH ANALYSIS")
print("-" * 40)
def avg_length(tokens):
    lengths = [len(t.get('word', '')) for t in tokens if t.get('word', '').strip()]
    return np.mean(lengths) if lengths else 0

print(f"  S-interrupted avg length: {avg_length(nymph_interrupted):.2f}")
print(f"  Nymph R-cont avg length: {avg_length(nymph_continuous):.2f}")
print(f"  Non-nymph cont avg length: {avg_length(non_nymph_continuous):.2f}")

# Vocabulary overlap
vocab_interrupted = get_vocab(nymph_interrupted)
vocab_nymph_cont = get_vocab(nymph_continuous)
vocab_non_nymph_cont = get_vocab(non_nymph_continuous)

print(f"\n7. VOCABULARY SIZES")
print("-" * 40)
print(f"  S-interrupted: {len(vocab_interrupted):,} types")
print(f"  Nymph R-cont: {len(vocab_nymph_cont):,} types")
print(f"  Non-nymph cont: {len(vocab_non_nymph_cont):,} types")

# Jaccard similarity
def jaccard(v1, v2):
    s1, s2 = set(v1.keys()), set(v2.keys())
    if len(s1 | s2) == 0:
        return 0
    return len(s1 & s2) / len(s1 | s2)

print(f"\n8. VOCABULARY JACCARD SIMILARITY")
print("-" * 40)
print(f"  S-interrupted vs Nymph R-cont: {jaccard(vocab_interrupted, vocab_nymph_cont):.4f}")
print(f"  S-interrupted vs Non-nymph cont: {jaccard(vocab_interrupted, vocab_non_nymph_cont):.4f}")
print(f"  Nymph R-cont vs Non-nymph cont: {jaccard(vocab_nymph_cont, vocab_non_nymph_cont):.4f}")

# Decision
print(f"\n" + "=" * 70)
print("NYMPH INTERRUPTION ASSESSMENT")
print("=" * 70)

# Key comparison: S-interrupted vs R-continuous on SAME nymph folios
same_folio_sim = cosine_sim(prefix_interrupted, prefix_nymph_cont)
# Also: S-interrupted vs all continuous rings
all_cont_prefix = Counter()
all_cont_prefix.update(prefix_nymph_cont)
all_cont_prefix.update(prefix_non_nymph_cont)
cross_sim = cosine_sim(prefix_interrupted, all_cont_prefix)

print(f"\n  Same-folio comparison (S vs R on nymph pages):")
print(f"    PREFIX cosine: {same_folio_sim:.4f}")

print(f"\n  Cross-folio comparison (S vs all continuous):")
print(f"    PREFIX cosine: {cross_sim:.4f}")

if same_folio_sim > 0.85 and cross_sim > 0.85:
    verdict = "DECORATIVE"
    interpretation = "Nymph interruption is purely decorative - same linguistic content"
    constraint_status = "C137 (illustration independence) CONFIRMED"
elif same_folio_sim > 0.85:
    verdict = "FOLIO-SPECIFIC"
    interpretation = "Interruption is decorative but nymph folios are linguistically distinct"
    constraint_status = "May need nymph-specific constraint"
else:
    verdict = "FUNCTIONAL"
    interpretation = "Interruption encodes structural difference - attention pacing?"
    constraint_status = "NEW CONSTRAINT NEEDED"

print(f"\n  VERDICT: {verdict}")
print(f"  INTERPRETATION: {interpretation}")
print(f"  CONSTRAINT STATUS: {constraint_status}")

# Save results
results = {
    "test": "TEST 4: Nymph-Interrupted vs Continuous Rings",
    "status": "COMPLETE",
    "token_counts": {
        "nymph_interrupted": len(nymph_interrupted),
        "nymph_continuous": len(nymph_continuous),
        "non_nymph_continuous": len(non_nymph_continuous)
    },
    "similarities": {
        "s_vs_nymph_r_prefix": same_folio_sim,
        "s_vs_all_continuous_prefix": cross_sim,
        "nymph_r_vs_non_nymph_prefix": cosine_sim(prefix_nymph_cont, prefix_non_nymph_cont)
    },
    "verdict": verdict,
    "interpretation": interpretation,
    "constraint_status": constraint_status
}

with open('results/test4_nymph_interruption.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n" + "=" * 70)
print("TEST 4 COMPLETE")
print("=" * 70)
print(f"\nResults saved to: results/test4_nymph_interruption.json")
