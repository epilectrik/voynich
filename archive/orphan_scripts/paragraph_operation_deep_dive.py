#!/usr/bin/env python3
"""
Deep dive into the counterintuitive finding:
- HIGH_K paragraphs have MORE FREQUENT_OPERATOR (escape), LESS ENERGY_OPERATOR
- HIGH_H paragraphs have MORE ENERGY_OPERATOR

What does this mean?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = {t: int(c) for t, c in class_data['token_to_class'].items()}
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

folio_line_tokens = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_line_tokens[token.folio][token.line].append(token)

def get_paragraphs(folio):
    lines = folio_line_tokens[folio]
    paragraphs = []
    current_para = []
    for line_num in sorted(lines.keys()):
        tokens = lines[line_num]
        if not tokens:
            continue
        first_word = tokens[0].word
        if first_word and first_word[0] in GALLOWS:
            if current_para:
                paragraphs.append(current_para)
            current_para = [(line_num, tokens)]
        else:
            current_para.append((line_num, tokens))
    if current_para:
        paragraphs.append(current_para)
    return paragraphs

# Collect paragraph data
all_paragraphs = []
for folio in folio_line_tokens:
    paras = get_paragraphs(folio)
    for i, p in enumerate(paras):
        words = []
        for line_num, tokens in p:
            words.extend([t.word for t in tokens])

        if len(words) < 5:
            continue

        k = sum(w.count('k') for w in words)
        h = sum(w.count('h') for w in words)
        e = sum(w.count('e') for w in words)
        total = k + h + e
        if total < 10:
            continue

        k_pct = 100 * k / total
        h_pct = 100 * h / total

        if k_pct > 35:
            kernel_type = 'HIGH_K'
        elif h_pct > 35:
            kernel_type = 'HIGH_H'
        else:
            kernel_type = 'OTHER'

        all_paragraphs.append({
            'kernel_type': kernel_type,
            'words': words,
            'k_pct': k_pct,
            'h_pct': h_pct
        })

# ============================================================
# ANALYZE ENERGY vs FREQUENT tokens by kernel type
# ============================================================
print("="*70)
print("ENERGY vs FREQUENT TOKENS BY PARAGRAPH TYPE")
print("="*70)

# Get EN and FQ tokens
EN_tokens = [t for t, role in token_to_role.items() if role == 'ENERGY_OPERATOR']
FQ_tokens = [t for t, role in token_to_role.items() if role == 'FREQUENT_OPERATOR']

print(f"\nTotal ENERGY_OPERATOR tokens in vocabulary: {len(EN_tokens)}")
print(f"Total FREQUENT_OPERATOR tokens in vocabulary: {len(FQ_tokens)}")

# Sample tokens
print(f"\nSample EN tokens: {EN_tokens[:10]}")
print(f"Sample FQ tokens: {FQ_tokens[:10]}")

# Analyze kernel content of EN vs FQ tokens
print(f"\n{'='*70}")
print("KERNEL CONTENT OF EN vs FQ TOKENS (VOCABULARY LEVEL)")
print("="*70)

def analyze_kernel_content(token_list):
    k_total = sum(t.count('k') for t in token_list)
    h_total = sum(t.count('h') for t in token_list)
    e_total = sum(t.count('e') for t in token_list)
    total = k_total + h_total + e_total
    return {
        'k_pct': 100 * k_total / total if total > 0 else 0,
        'h_pct': 100 * h_total / total if total > 0 else 0,
        'e_pct': 100 * e_total / total if total > 0 else 0
    }

en_kernel = analyze_kernel_content(EN_tokens)
fq_kernel = analyze_kernel_content(FQ_tokens)

print(f"\nENERGY_OPERATOR vocabulary kernel content:")
print(f"  k: {en_kernel['k_pct']:.1f}%  h: {en_kernel['h_pct']:.1f}%  e: {en_kernel['e_pct']:.1f}%")

print(f"\nFREQUENT_OPERATOR vocabulary kernel content:")
print(f"  k: {fq_kernel['k_pct']:.1f}%  h: {fq_kernel['h_pct']:.1f}%  e: {fq_kernel['e_pct']:.1f}%")

# ============================================================
# LOOK AT SPECIFIC TOKENS IN HIGH_K vs HIGH_H PARAGRAPHS
# ============================================================
print(f"\n{'='*70}")
print("EN TOKENS USED IN HIGH_K vs HIGH_H PARAGRAPHS")
print("="*70)

high_k_en = Counter()
high_h_en = Counter()
high_k_fq = Counter()
high_h_fq = Counter()

for p in all_paragraphs:
    for w in p['words']:
        role = token_to_role.get(w)
        if p['kernel_type'] == 'HIGH_K':
            if role == 'ENERGY_OPERATOR':
                high_k_en[w] += 1
            elif role == 'FREQUENT_OPERATOR':
                high_k_fq[w] += 1
        elif p['kernel_type'] == 'HIGH_H':
            if role == 'ENERGY_OPERATOR':
                high_h_en[w] += 1
            elif role == 'FREQUENT_OPERATOR':
                high_h_fq[w] += 1

print(f"\nTop EN tokens in HIGH_K paragraphs:")
for w, c in high_k_en.most_common(10):
    k_content = 100 * w.count('k') / (w.count('k') + w.count('h') + w.count('e')) if (w.count('k') + w.count('h') + w.count('e')) > 0 else 0
    print(f"  {w:<15} {c:>5}  (k-content: {k_content:.0f}%)")

print(f"\nTop EN tokens in HIGH_H paragraphs:")
for w, c in high_h_en.most_common(10):
    h_content = 100 * w.count('h') / (w.count('k') + w.count('h') + w.count('e')) if (w.count('k') + w.count('h') + w.count('e')) > 0 else 0
    print(f"  {w:<15} {c:>5}  (h-content: {h_content:.0f}%)")

print(f"\nTop FQ tokens in HIGH_K paragraphs:")
for w, c in high_k_fq.most_common(10):
    k_content = 100 * w.count('k') / (w.count('k') + w.count('h') + w.count('e')) if (w.count('k') + w.count('h') + w.count('e')) > 0 else 0
    print(f"  {w:<15} {c:>5}  (k-content: {k_content:.0f}%)")

print(f"\nTop FQ tokens in HIGH_H paragraphs:")
for w, c in high_h_fq.most_common(10):
    h_content = 100 * w.count('h') / (w.count('k') + w.count('h') + w.count('e')) if (w.count('k') + w.count('h') + w.count('e')) > 0 else 0
    print(f"  {w:<15} {c:>5}  (h-content: {h_content:.0f}%)")

# ============================================================
# INTERPRETATION
# ============================================================
print(f"\n{'='*70}")
print("INTERPRETATION")
print("="*70)

print("""
KEY INSIGHT: Kernel type (k/h/e) and Role (EN/FQ) are ORTHOGONAL dimensions!

The kernel character distribution reflects the MORPHOLOGICAL choices within
a role, not the role itself.

HIGH_K paragraphs:
- Use k-rich vocabulary ACROSS ALL ROLES
- Higher FQ rate = more escape/recovery operations
- The "k" kernel appears in EN tokens, FQ tokens, etc.
- INTERPRETATION: "Emergency/intervention mode" - doing recovery with k-operations

HIGH_H paragraphs:
- Use h-rich vocabulary ACROSS ALL ROLES
- Higher EN rate = more energy operations
- The "h" kernel appears in EN tokens, FQ tokens, etc.
- INTERPRETATION: "Careful processing mode" - doing energy ops with h-monitoring

This means:
- Kernel (k/h/e) = HOW you do the operation (intervention type)
- Role (EN/FQ/FL) = WHAT operation you're doing (energy, escape, hazard)

A HIGH_K paragraph is not "more energy" - it's "using k-type interventions
for whatever operations it's doing (which happen to be more escape-focused)."

A HIGH_H paragraph is not "more monitoring" - it's "using h-type interventions
for whatever operations it's doing (which happen to be more energy-focused)."
""")

# ============================================================
# BRUNSCHWIG MAPPING REVISED
# ============================================================
print(f"\n{'='*70}")
print("REVISED BRUNSCHWIG MAPPING")
print("="*70)

print("""
BRUNSCHWIG OPERATION TYPES vs VOYNICH PARAGRAPH TYPES:

1. HIGH_K + HIGH_FQ ("Recovery-intensive with k-interventions"):
   BRUNSCHWIG: "If it overheats, remove from fire immediately..."
   - Crisis handling procedures
   - Recovery from problems
   - k = specific intervention type (perhaps "remove/reduce")

2. HIGH_H + HIGH_EN ("Energy operations with h-monitoring"):
   BRUNSCHWIG: "Distill slowly, watching the color..."
   - Careful heating with continuous monitoring
   - h = monitoring/checking intervention type

3. BALANCED ("Standard operations"):
   BRUNSCHWIG: "Distill per alembicum..."
   - General-purpose procedures
   - Mixed intervention types

This aligns with the closed-loop model:
- Different paragraphs handle different SITUATIONS
- The kernel indicates INTERVENTION TYPE, not operation category
- Role indicates OPERATION CATEGORY
- Paragraphs specialize in situation-intervention combinations
""")
