"""
TEST 1: P-Text Reclassification (CRITICAL)

Goal: Determine whether A-like paragraph text behaves as Currier A or as AZC

Protocol:
1. Identify all P-placement tokens on AZC folios
2. Remove P-text tokens from AZC vocabulary
3. Recompute:
   - AZC compatibility breadth
   - Survivor-set uniqueness
   - MIDDLE exclusivity profiles
4. Compare P-text to Currier A structural behavior

Outcomes:
| Result | Interpretation | Action |
|--------|---------------|--------|
| P-text behaves like A | Reclassify as "A-on-AZC-folio" | Update C300/C301 annotations |
| P-text behaves like AZC | Treat as AZC subtype | No structural change |
| Mixed | Introduce AZC-LAYER distinction | New constraint needed |
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

# Load transcript
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Parse all H-track tokens
all_h_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        if row.get('transcriber', '').strip() == 'H':
            all_h_tokens.append(row)

# Separate by system
# 'language' field contains 'A' or 'B' for Currier classification
currier_a = [t for t in all_h_tokens if t.get('language', '').strip() == 'A']
currier_b = [t for t in all_h_tokens if t.get('language', '').strip() == 'B']
azc_all = [t for t in all_h_tokens if t.get('folio', '') in AZC_FOLIOS]

# Split AZC into P-text and diagram text
azc_p_text = [t for t in azc_all if t.get('placement', '').strip() == 'P']
azc_diagram = [t for t in azc_all if t.get('placement', '').strip() != 'P']

print("=" * 70)
print("TEST 1: P-TEXT RECLASSIFICATION")
print("=" * 70)

print(f"\n1. CORPUS BREAKDOWN")
print("-" * 40)
print(f"  Currier A tokens: {len(currier_a):,}")
print(f"  Currier B tokens: {len(currier_b):,}")
print(f"  AZC total tokens: {len(azc_all):,}")
print(f"    - P-text: {len(azc_p_text):,} ({100*len(azc_p_text)/len(azc_all):.1f}%)")
print(f"    - Diagram: {len(azc_diagram):,} ({100*len(azc_diagram)/len(azc_all):.1f}%)")

# Extract vocabulary for each corpus
def get_vocab(tokens):
    return Counter(t.get('word', '') for t in tokens if t.get('word', '').strip())

vocab_a = get_vocab(currier_a)
vocab_b = get_vocab(currier_b)
vocab_p = get_vocab(azc_p_text)
vocab_azc_d = get_vocab(azc_diagram)
vocab_azc_all = get_vocab(azc_all)

print(f"\n2. VOCABULARY SIZES")
print("-" * 40)
print(f"  Currier A: {len(vocab_a):,} types")
print(f"  Currier B: {len(vocab_b):,} types")
print(f"  AZC total: {len(vocab_azc_all):,} types")
print(f"    - P-text: {len(vocab_p):,} types")
print(f"    - Diagram: {len(vocab_azc_d):,} types")

# Calculate overlap
def vocab_overlap(v1, v2):
    shared = set(v1.keys()) & set(v2.keys())
    return len(shared), len(shared) / min(len(v1), len(v2)) if min(len(v1), len(v2)) > 0 else 0

overlap_p_a, pct_p_a = vocab_overlap(vocab_p, vocab_a)
overlap_p_d, pct_p_d = vocab_overlap(vocab_p, vocab_azc_d)
overlap_p_b, pct_p_b = vocab_overlap(vocab_p, vocab_b)

print(f"\n3. P-TEXT VOCABULARY OVERLAP")
print("-" * 40)
print(f"  P-text & Currier A: {overlap_p_a:,} types ({pct_p_a:.1%})")
print(f"  P-text & AZC diagram: {overlap_p_d:,} types ({pct_p_d:.1%})")
print(f"  P-text & Currier B: {overlap_p_b:,} types ({pct_p_b:.1%})")

# Jaccard similarity
def jaccard(v1, v2):
    s1, s2 = set(v1.keys()), set(v2.keys())
    if len(s1 | s2) == 0:
        return 0
    return len(s1 & s2) / len(s1 | s2)

print(f"\n4. JACCARD SIMILARITY")
print("-" * 40)
print(f"  P-text vs Currier A: {jaccard(vocab_p, vocab_a):.4f}")
print(f"  P-text vs AZC diagram: {jaccard(vocab_p, vocab_azc_d):.4f}")
print(f"  P-text vs Currier B: {jaccard(vocab_p, vocab_b):.4f}")
print(f"  AZC diagram vs Currier A: {jaccard(vocab_azc_d, vocab_a):.4f}")
print(f"  AZC diagram vs Currier B: {jaccard(vocab_azc_d, vocab_b):.4f}")

# MIDDLE morphology analysis (structural behavior)
# MIDDLEs are: ar, or, ol, al, etc. (core structural elements)
MIDDLES = {'ar', 'or', 'ol', 'al', 'air', 'aiin', 'oiin', 'ain', 'oin',
           'an', 'in', 'on', 'am', 'om', 'im'}

def extract_middle(token):
    """Extract middle component from a token (simplified)"""
    token = token.strip()
    if len(token) < 2:
        return None
    # Remove common prefixes
    for pfx in ['qo', 'cho', 'ch', 'sh', 'd', 'o', 's', 'y', 'ok', 'ot']:
        if token.startswith(pfx) and len(token) > len(pfx):
            token = token[len(pfx):]
            break
    # Remove common suffixes
    for sfx in ['y', 'dy', 'ey', 'edy', 'eey', 'hy']:
        if token.endswith(sfx) and len(token) > len(sfx):
            token = token[:-len(sfx)]
            break
    return token if token in MIDDLES else None

def get_middle_profile(tokens):
    """Get MIDDLE distribution for a token set"""
    middles = Counter()
    for t in tokens:
        tok = t.get('word', '')
        m = extract_middle(tok)
        if m:
            middles[m] += 1
    return middles

middle_a = get_middle_profile(currier_a)
middle_b = get_middle_profile(currier_b)
middle_p = get_middle_profile(azc_p_text)
middle_azc_d = get_middle_profile(azc_diagram)

print(f"\n5. MIDDLE MORPHOLOGY PROFILES")
print("-" * 40)
print(f"  Total MIDDLE tokens found:")
print(f"    Currier A: {sum(middle_a.values()):,}")
print(f"    Currier B: {sum(middle_b.values()):,}")
print(f"    P-text: {sum(middle_p.values()):,}")
print(f"    AZC diagram: {sum(middle_azc_d.values()):,}")

def cosine_sim(c1, c2):
    """Cosine similarity between two Counters"""
    all_keys = set(c1.keys()) | set(c2.keys())
    if not all_keys:
        return 0
    v1 = np.array([c1.get(k, 0) for k in all_keys])
    v2 = np.array([c2.get(k, 0) for k in all_keys])
    norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return np.dot(v1, v2) / (norm1 * norm2)

print(f"\n  MIDDLE distribution cosine similarity:")
print(f"    P-text vs Currier A: {cosine_sim(middle_p, middle_a):.4f}")
print(f"    P-text vs AZC diagram: {cosine_sim(middle_p, middle_azc_d):.4f}")
print(f"    P-text vs Currier B: {cosine_sim(middle_p, middle_b):.4f}")
print(f"    AZC diagram vs Currier A: {cosine_sim(middle_azc_d, middle_a):.4f}")
print(f"    AZC diagram vs Currier B: {cosine_sim(middle_azc_d, middle_b):.4f}")

# Line-initial token analysis (structural behavior)
def get_line_initial_profile(tokens):
    """Get distribution of tokens at line position 1"""
    by_line = defaultdict(list)
    for t in tokens:
        key = (t.get('folio', ''), t.get('line', ''))
        by_line[key].append(t)

    initial_tokens = Counter()
    for key, toks in by_line.items():
        if toks:
            # Sort by position within line if available
            sorted_toks = sorted(toks, key=lambda x: int(x.get('position', 0) or 0))
            if sorted_toks:
                initial_tokens[sorted_toks[0].get('token', '')] += 1
    return initial_tokens

initial_a = get_line_initial_profile(currier_a)
initial_b = get_line_initial_profile(currier_b)
initial_p = get_line_initial_profile(azc_p_text)
initial_azc_d = get_line_initial_profile(azc_diagram)

print(f"\n6. LINE-INITIAL TOKEN ANALYSIS")
print("-" * 40)
print(f"  Unique line-initial types:")
print(f"    Currier A: {len(initial_a):,}")
print(f"    Currier B: {len(initial_b):,}")
print(f"    P-text: {len(initial_p):,}")
print(f"    AZC diagram: {len(initial_azc_d):,}")

print(f"\n  Line-initial cosine similarity:")
print(f"    P-text vs Currier A: {cosine_sim(initial_p, initial_a):.4f}")
print(f"    P-text vs AZC diagram: {cosine_sim(initial_p, initial_azc_d):.4f}")
print(f"    P-text vs Currier B: {cosine_sim(initial_p, initial_b):.4f}")

# Compatibility breadth (how many B types can follow each A/AZC type)
# This is a key discriminator - A has narrow compatibility, AZC has broad
def get_prefix_dist(tokens):
    """Extract prefix distribution"""
    prefixes = Counter()
    for t in tokens:
        tok = t.get('word', '').strip()
        if len(tok) >= 2:
            for pfx in ['qo', 'cho', 'ch', 'sh', 'ok', 'ot', 'd', 's', 'y', 'o']:
                if tok.startswith(pfx):
                    prefixes[pfx] += 1
                    break
    return prefixes

prefix_a = get_prefix_dist(currier_a)
prefix_b = get_prefix_dist(currier_b)
prefix_p = get_prefix_dist(azc_p_text)
prefix_azc_d = get_prefix_dist(azc_diagram)

print(f"\n7. PREFIX DISTRIBUTION ANALYSIS")
print("-" * 40)
print(f"  Top prefixes by corpus:")

for name, dist in [("Currier A", prefix_a), ("Currier B", prefix_b),
                   ("P-text", prefix_p), ("AZC diagram", prefix_azc_d)]:
    total = sum(dist.values())
    if total > 0:
        top3 = dist.most_common(3)
        top_str = ", ".join(f"{p}:{c/total:.1%}" for p, c in top3)
        print(f"    {name}: {top_str}")

print(f"\n  PREFIX distribution cosine similarity:")
print(f"    P-text vs Currier A: {cosine_sim(prefix_p, prefix_a):.4f}")
print(f"    P-text vs AZC diagram: {cosine_sim(prefix_p, prefix_azc_d):.4f}")
print(f"    P-text vs Currier B: {cosine_sim(prefix_p, prefix_b):.4f}")

# Exclusive vocabulary test
p_only = set(vocab_p.keys()) - set(vocab_a.keys()) - set(vocab_azc_d.keys())
p_shared_a_only = (set(vocab_p.keys()) & set(vocab_a.keys())) - set(vocab_azc_d.keys())
p_shared_d_only = (set(vocab_p.keys()) & set(vocab_azc_d.keys())) - set(vocab_a.keys())

print(f"\n8. EXCLUSIVE VOCABULARY")
print("-" * 40)
print(f"  P-text types exclusive (not in A or diagram): {len(p_only)}")
print(f"  P-text types shared with A only (not diagram): {len(p_shared_a_only)}")
print(f"  P-text types shared with diagram only (not A): {len(p_shared_d_only)}")

if p_shared_a_only:
    print(f"\n  Types shared with A only (sample):")
    for tok in sorted(p_shared_a_only)[:10]:
        print(f"    {tok}: P={vocab_p[tok]}, A={vocab_a[tok]}")

# DECISION MATRIX
print(f"\n" + "=" * 70)
print("DECISION MATRIX")
print("=" * 70)

# Calculate decision scores (weighted by reliability)
score_like_a = 0
score_like_azc = 0
decisions = []

# 1. Jaccard - if closer to A than to diagram (weight: 1)
j_p_a = jaccard(vocab_p, vocab_a)
j_p_d = jaccard(vocab_p, vocab_azc_d)
if j_p_a > j_p_d:
    score_like_a += 1
    decisions.append(("Jaccard vocab", "A-like", f"{j_p_a:.3f} > {j_p_d:.3f}", 1))
else:
    score_like_azc += 1
    decisions.append(("Jaccard vocab", "AZC-like", f"{j_p_d:.3f} >= {j_p_a:.3f}", 1))

# 2. MIDDLE cosine - if closer to A than to diagram (weight: 1)
m_p_a = cosine_sim(middle_p, middle_a)
m_p_d = cosine_sim(middle_p, middle_azc_d)
if m_p_a > m_p_d:
    score_like_a += 1
    decisions.append(("MIDDLE profile", "A-like", f"{m_p_a:.3f} > {m_p_d:.3f}", 1))
else:
    score_like_azc += 1
    decisions.append(("MIDDLE profile", "AZC-like", f"{m_p_d:.3f} >= {m_p_a:.3f}", 1))

# 3. PREFIX cosine - if closer to A than to diagram (weight: 2 - most reliable)
pf_p_a = cosine_sim(prefix_p, prefix_a)
pf_p_d = cosine_sim(prefix_p, prefix_azc_d)
if pf_p_a > pf_p_d:
    score_like_a += 2  # Double weight for PREFIX
    decisions.append(("PREFIX profile", "A-like", f"{pf_p_a:.3f} > {pf_p_d:.3f}", 2))
else:
    score_like_azc += 2
    decisions.append(("PREFIX profile", "AZC-like", f"{pf_p_d:.3f} >= {pf_p_a:.3f}", 2))

# 4. Exclusive vocabulary ratio (weight: 2 - decisive)
excl_a_ratio = len(p_shared_a_only) / max(len(p_shared_d_only), 1)
if excl_a_ratio > 2.0:  # P-text shares >2x more exclusive types with A than diagram
    score_like_a += 2
    decisions.append(("Exclusive vocab", "A-like", f"{len(p_shared_a_only)} vs {len(p_shared_d_only)} ({excl_a_ratio:.1f}x)", 2))
elif excl_a_ratio < 0.5:
    score_like_azc += 2
    decisions.append(("Exclusive vocab", "AZC-like", f"{len(p_shared_d_only)} vs {len(p_shared_a_only)}", 2))
else:
    decisions.append(("Exclusive vocab", "MIXED", f"{len(p_shared_a_only)} vs {len(p_shared_d_only)}", 0))

print(f"\n  Metric-by-metric classification:")
for item in decisions:
    metric, verdict, evidence = item[0], item[1], item[2]
    weight = item[3] if len(item) > 3 else 1
    print(f"    {metric:20s}: {verdict:10s} ({evidence}) [weight:{weight}]")

print(f"\n  SUMMARY SCORES:")
print(f"    A-like indicators: {score_like_a}")
print(f"    AZC-like indicators: {score_like_azc}")

if score_like_a > score_like_azc:
    classification = "A-ON-AZC-FOLIO"
    action = "Reclassify P-text as Currier A; update C300/C301 counts"
elif score_like_azc > score_like_a:
    classification = "AZC-SUBTYPE"
    action = "Treat P-text as AZC variant; no structural change"
else:
    classification = "MIXED"
    action = "Introduce AZC-LAYER distinction; new constraint needed"

print(f"\n  CLASSIFICATION: {classification}")
print(f"  RECOMMENDED ACTION: {action}")

# Save results
results = {
    "test": "TEST 1: P-Text Reclassification",
    "status": "COMPLETE",
    "tokens": {
        "currier_a": len(currier_a),
        "currier_b": len(currier_b),
        "azc_total": len(azc_all),
        "azc_p_text": len(azc_p_text),
        "azc_diagram": len(azc_diagram)
    },
    "vocabulary": {
        "currier_a": len(vocab_a),
        "currier_b": len(vocab_b),
        "p_text": len(vocab_p),
        "azc_diagram": len(vocab_azc_d)
    },
    "similarities": {
        "jaccard_p_vs_a": j_p_a,
        "jaccard_p_vs_diagram": j_p_d,
        "middle_cosine_p_vs_a": m_p_a,
        "middle_cosine_p_vs_diagram": m_p_d,
        "prefix_cosine_p_vs_a": pf_p_a,
        "prefix_cosine_p_vs_diagram": pf_p_d
    },
    "exclusive_vocabulary": {
        "shared_with_a_only": len(p_shared_a_only),
        "shared_with_diagram_only": len(p_shared_d_only),
        "ratio_a_to_diagram": excl_a_ratio
    },
    "scores": {
        "a_like": score_like_a,
        "azc_like": score_like_azc
    },
    "classification": classification,
    "action": action
}

with open('results/test1_ptext_reclassification.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n" + "=" * 70)
print("TEST 1 COMPLETE")
print("=" * 70)
print(f"\nResults saved to: results/test1_ptext_reclassification.json")
