"""
TEST 3: Center Token Audit (HIGH)

Goal: Determine if systematically missing center tokens participate in legality

Protocol:
1. Identify center tokens from transcript (C placement, innermost rings)
2. Analyze their vocabulary profile
3. Compare to ring text and P-text
4. Determine if they function as labels/anchors or legality-participating tokens

Expert prior: "They are labels or anchors, not legality-participating tokens"
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

# Define center and near-center placement codes
CENTER_CODES = {'C', 'C1', 'C2', 'C3', 'W', 'L', 'I'}  # Center, labels, innermost
RING_CODES = {'R', 'R1', 'R2', 'R3', 'R4', 'O'}  # Ring positions
NYMPH_CODES = {'S', 'S1', 'S2', 'S3'}  # Nymph-interrupted rings

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

# Exclude P-text (per TEST 1 result - it's A-like)
azc_tokens = [t for t in azc_tokens if t.get('placement', '').strip() != 'P']

print("=" * 70)
print("TEST 3: CENTER TOKEN AUDIT")
print("=" * 70)

# Categorize tokens by placement type
center_tokens = [t for t in azc_tokens if t.get('placement', '').strip() in CENTER_CODES]
ring_tokens = [t for t in azc_tokens if t.get('placement', '').strip() in RING_CODES]
nymph_tokens = [t for t in azc_tokens if t.get('placement', '').strip() in NYMPH_CODES]
other_tokens = [t for t in azc_tokens if t.get('placement', '').strip() not in CENTER_CODES | RING_CODES | NYMPH_CODES]

print(f"\n1. TOKEN DISTRIBUTION BY PLACEMENT CATEGORY")
print("-" * 40)
print(f"  Center/Label tokens: {len(center_tokens):,}")
print(f"  Ring tokens: {len(ring_tokens):,}")
print(f"  Nymph-interrupted: {len(nymph_tokens):,}")
print(f"  Other: {len(other_tokens):,}")

# Detailed center placement breakdown
print(f"\n2. CENTER PLACEMENT BREAKDOWN")
print("-" * 40)
center_placements = Counter(t.get('placement', '') for t in center_tokens)
for p, count in sorted(center_placements.items(), key=lambda x: -x[1]):
    print(f"  {p:5s}: {count:4d}")

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

# Vocabulary analysis
vocab_center = get_vocab(center_tokens)
vocab_ring = get_vocab(ring_tokens)
vocab_nymph = get_vocab(nymph_tokens)

print(f"\n3. VOCABULARY SIZES")
print("-" * 40)
print(f"  Center tokens: {len(vocab_center):,} types ({len(center_tokens):,} tokens)")
print(f"  Ring tokens: {len(vocab_ring):,} types ({len(ring_tokens):,} tokens)")
print(f"  Nymph tokens: {len(vocab_nymph):,} types ({len(nymph_tokens):,} tokens)")

# Most common center tokens
print(f"\n4. MOST COMMON CENTER TOKENS")
print("-" * 40)
for tok, count in vocab_center.most_common(20):
    print(f"  {tok:15s}: {count:3d}")

# Token length analysis (labels tend to be short)
print(f"\n5. TOKEN LENGTH ANALYSIS")
print("-" * 40)
def avg_length(tokens):
    lengths = [len(t.get('word', '')) for t in tokens if t.get('word', '').strip()]
    return np.mean(lengths) if lengths else 0

print(f"  Center avg length: {avg_length(center_tokens):.2f}")
print(f"  Ring avg length: {avg_length(ring_tokens):.2f}")
print(f"  Nymph avg length: {avg_length(nymph_tokens):.2f}")

# Single-character tokens (strong label indicator)
center_single = [t for t in center_tokens if len(t.get('word', '').strip()) == 1]
ring_single = [t for t in ring_tokens if len(t.get('word', '').strip()) == 1]
print(f"\n  Single-character tokens:")
print(f"    Center: {len(center_single):3d} ({100*len(center_single)/max(len(center_tokens),1):.1f}%)")
print(f"    Ring: {len(ring_single):3d} ({100*len(ring_single)/max(len(ring_tokens),1):.1f}%)")

# PREFIX distribution comparison
print(f"\n6. PREFIX DISTRIBUTION")
print("-" * 40)
prefix_center = get_prefix_dist(center_tokens)
prefix_ring = get_prefix_dist(ring_tokens)
prefix_nymph = get_prefix_dist(nymph_tokens)

for name, dist in [("Center", prefix_center), ("Ring", prefix_ring), ("Nymph", prefix_nymph)]:
    total = sum(dist.values())
    if total > 0:
        top3 = dist.most_common(3)
        top_str = ", ".join(f"{p}:{c/total:.1%}" for p, c in top3)
        print(f"  {name:10s}: {top_str}")

# PREFIX cosine similarity
print(f"\n7. PREFIX SIMILARITY")
print("-" * 40)
print(f"  Center vs Ring: {cosine_sim(prefix_center, prefix_ring):.4f}")
print(f"  Center vs Nymph: {cosine_sim(prefix_center, prefix_nymph):.4f}")
print(f"  Ring vs Nymph: {cosine_sim(prefix_ring, prefix_nymph):.4f}")

# Exclusive vocabulary test
center_only = set(vocab_center.keys()) - set(vocab_ring.keys()) - set(vocab_nymph.keys())
center_ring_shared = set(vocab_center.keys()) & set(vocab_ring.keys())

print(f"\n8. VOCABULARY EXCLUSIVITY")
print("-" * 40)
print(f"  Center-only types: {len(center_only)}")
print(f"  Center-Ring shared: {len(center_ring_shared)}")
print(f"  Overlap ratio: {len(center_ring_shared)/max(len(vocab_center),1):.1%}")

if center_only:
    print(f"\n  Sample center-only tokens:")
    for tok in sorted(center_only)[:10]:
        print(f"    {tok}")

# Folio distribution - are center tokens concentrated or distributed?
print(f"\n9. FOLIO DISTRIBUTION")
print("-" * 40)
folios_with_center = sorted(set(t.get('folio', '') for t in center_tokens))
print(f"  Folios with center tokens: {len(folios_with_center)}")
print(f"  {', '.join(folios_with_center)}")

# Decision
print(f"\n" + "=" * 70)
print("CENTER TOKEN CLASSIFICATION")
print("=" * 70)

# Criteria for "label" classification:
# 1. High % single-character tokens (>5%)
# 2. Lower PREFIX similarity to ring text (<0.85)
# 3. Low overlap ratio with ring vocab (<30%)

single_pct = 100*len(center_single)/max(len(center_tokens),1)
prefix_sim_to_ring = cosine_sim(prefix_center, prefix_ring)
overlap_ratio = len(center_ring_shared)/max(len(vocab_center),1)

print(f"\n  Classification Criteria:")
print(f"    Single-char tokens: {single_pct:.1f}% (>5% = label-like)")
print(f"    PREFIX sim to ring: {prefix_sim_to_ring:.4f} (<0.85 = distinct)")
print(f"    Vocab overlap: {overlap_ratio:.1%} (<30% = label-like)")

label_score = 0
if single_pct > 5:
    label_score += 1
if prefix_sim_to_ring < 0.85:
    label_score += 1
if overlap_ratio < 0.30:
    label_score += 1

if label_score >= 2:
    classification = "LABEL/ANCHOR"
    interpretation = "Center tokens are non-participating labels/anchors"
    action = "Exclude from legality calculations; tag as CENTER_META"
else:
    classification = "LEGALITY-PARTICIPATING"
    interpretation = "Center tokens participate in legality like ring tokens"
    action = "Include in standard legality calculations"

print(f"\n  Score: {label_score}/3 label-like indicators")
print(f"\n  CLASSIFICATION: {classification}")
print(f"  INTERPRETATION: {interpretation}")
print(f"  ACTION: {action}")

# Save results
results = {
    "test": "TEST 3: Center Token Audit",
    "status": "COMPLETE",
    "token_counts": {
        "center": len(center_tokens),
        "ring": len(ring_tokens),
        "nymph": len(nymph_tokens)
    },
    "center_placement_breakdown": dict(center_placements),
    "vocabulary": {
        "center_types": len(vocab_center),
        "ring_types": len(vocab_ring),
        "center_only_types": len(center_only),
        "overlap_ratio": overlap_ratio
    },
    "indicators": {
        "single_char_pct": single_pct,
        "prefix_sim_to_ring": prefix_sim_to_ring,
        "label_score": label_score
    },
    "classification": classification,
    "interpretation": interpretation,
    "action": action
}

with open('results/test3_center_token_audit.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n" + "=" * 70)
print("TEST 3 COMPLETE")
print("=" * 70)
print(f"\nResults saved to: results/test3_center_token_audit.json")
