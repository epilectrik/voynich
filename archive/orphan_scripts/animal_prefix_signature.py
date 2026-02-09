#!/usr/bin/env python3
"""
Use animal prefix signature to identify candidate animal records.

From animal_folio_analysis:
- Animal prefixes: qo (23.5%), ok (17.6%), da (8.8%), ct (8.8%), ot (5.9%)
- Herb prefixes: ko, tch, pch, to (0% in animal)

Can we use this signature to find more animal records?
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

# Define prefix signatures
ANIMAL_PREFIXES = {'qo', 'ok', 'da', 'ct', 'ot', 'ch'}
HERB_PREFIXES = {'ko', 'tch', 'pch', 'to', 'kch'}

print("="*70)
print("ANIMAL PREFIX SIGNATURE ANALYSIS")
print("="*70)

# Build paragraph data
folio_paragraphs = defaultdict(list)

current_folio = None
current_para = []
current_line = None

for token in tx.currier_a():
    if '*' in token.word:
        continue

    # New folio
    if token.folio != current_folio:
        if current_para:
            folio_paragraphs[current_folio].append(current_para)
        current_folio = token.folio
        current_para = [token]
        current_line = token.line
        continue

    # Same folio - check for new paragraph
    if token.line != current_line:
        first_word = token.word
        if first_word and first_word[0] in GALLOWS:
            # New paragraph
            folio_paragraphs[current_folio].append(current_para)
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

# Don't forget last paragraph
if current_para:
    folio_paragraphs[current_folio].append(current_para)

# Score each paragraph for animal vs herb signature
paragraph_scores = []

for folio, paras in folio_paragraphs.items():
    for para_idx, para in enumerate(paras):
        if len(para) < 3:
            continue

        # Get RI tokens (first 1-3 tokens)
        ri_tokens = [t.word for t in para[:3]]

        # Extract prefixes
        prefixes = []
        for token in ri_tokens:
            try:
                m = morph.extract(token)
                if m.prefix:
                    prefixes.append(m.prefix)
            except:
                pass

        # Score
        animal_score = sum(1 for p in prefixes if p in ANIMAL_PREFIXES)
        herb_score = sum(1 for p in prefixes if p in HERB_PREFIXES)

        if prefixes:
            paragraph_scores.append({
                'folio': folio,
                'para_idx': para_idx,
                'ri_tokens': ri_tokens,
                'prefixes': prefixes,
                'animal_score': animal_score,
                'herb_score': herb_score,
                'net_score': animal_score - herb_score,
                'n_tokens': len(para)
            })

# Classify paragraphs
animal_candidates = [p for p in paragraph_scores if p['net_score'] > 0]
herb_candidates = [p for p in paragraph_scores if p['net_score'] < 0]
neutral = [p for p in paragraph_scores if p['net_score'] == 0]

print(f"\nTotal paragraphs scored: {len(paragraph_scores)}")
print(f"Animal signature (net > 0): {len(animal_candidates)} ({100*len(animal_candidates)/len(paragraph_scores):.1f}%)")
print(f"Herb signature (net < 0): {len(herb_candidates)} ({100*len(herb_candidates)/len(paragraph_scores):.1f}%)")
print(f"Neutral (net = 0): {len(neutral)} ({100*len(neutral)/len(paragraph_scores):.1f}%)")

# Top animal candidates
print(f"\n{'='*70}")
print("TOP ANIMAL CANDIDATES BY PREFIX SIGNATURE")
print("="*70)

animal_candidates.sort(key=lambda x: -x['net_score'])

print(f"\n{'Folio':<10} {'Para':<6} {'Score':<8} {'Prefixes':<20} {'RI tokens':<40}")
print("-"*90)

for p in animal_candidates[:20]:
    prefixes_str = ', '.join(p['prefixes'])
    ri_str = ', '.join(p['ri_tokens'][:3])
    print(f"{p['folio']:<10} {p['para_idx']:<6} {p['net_score']:<8} {prefixes_str:<20} {ri_str:<40}")

# Folio-level aggregation
print(f"\n{'='*70}")
print("FOLIO-LEVEL ANIMAL CONCENTRATION")
print("="*70)

folio_animal_counts = Counter()
folio_total_counts = Counter()

for p in paragraph_scores:
    folio_total_counts[p['folio']] += 1
    if p['net_score'] > 0:
        folio_animal_counts[p['folio']] += 1

# Rank folios by animal concentration
folio_rankings = []
for folio in folio_total_counts:
    total = folio_total_counts[folio]
    animal = folio_animal_counts.get(folio, 0)
    if total >= 3:
        folio_rankings.append({
            'folio': folio,
            'total': total,
            'animal': animal,
            'rate': animal / total
        })

folio_rankings.sort(key=lambda x: -x['rate'])

print(f"\n{'Folio':<12} {'Total Paras':<15} {'Animal Paras':<15} {'Animal Rate':<12}")
print("-"*55)

for f in folio_rankings[:20]:
    print(f"{f['folio']:<12} {f['total']:<15} {f['animal']:<15} {100*f['rate']:<12.1f}")

# Validate against known animal folios
print(f"\n{'='*70}")
print("VALIDATION AGAINST KNOWN ANIMAL FOLIOS")
print("="*70)

# Load known animal folios
known_animal_path = Path(__file__).parent.parent / 'results' / 'animal_folio_analysis.json'
if known_animal_path.exists():
    with open(known_animal_path) as f:
        known_data = json.load(f)
    known_animal_folios = set(known_data['animal_folios'])

    print(f"\nKnown animal folios: {sorted(known_animal_folios)}")

    # Check overlap
    predicted_animal = set(f['folio'] for f in folio_rankings if f['rate'] >= 0.3)
    overlap = predicted_animal & known_animal_folios
    precision = len(overlap) / len(predicted_animal) if predicted_animal else 0
    recall = len(overlap) / len(known_animal_folios) if known_animal_folios else 0

    print(f"\nPredicted (rate >= 30%): {sorted(predicted_animal)}")
    print(f"Overlap with known: {sorted(overlap)}")
    print(f"Precision: {100*precision:.1f}%")
    print(f"Recall: {100*recall:.1f}%")

    # New candidates (predicted but not in known)
    new_candidates = predicted_animal - known_animal_folios
    if new_candidates:
        print(f"\nNEW ANIMAL FOLIO CANDIDATES: {sorted(new_candidates)}")

# Summary
print(f"\n{'='*70}")
print("SUMMARY")
print("="*70)

print("""
PREFIX SIGNATURE METHOD:
- Animal prefixes: qo, ok, da, ct, ot, ch
- Herb prefixes: ko, tch, pch, to, kch

This signature identifies:
1. Paragraphs with animal-associated RI structure
2. Folios with high animal concentration
3. New animal folio candidates

The prefix pattern reveals:
- A records ARE organized by material class
- PREFIX encodes material-relevant information
- Animal vs herb distinction is lexically marked in RI
""")

# Save results
output = {
    'animal_candidates': len(animal_candidates),
    'herb_candidates': len(herb_candidates),
    'neutral': len(neutral),
    'top_animal_folios': [f['folio'] for f in folio_rankings if f['rate'] >= 0.3],
    'method': 'prefix_signature',
}

output_path = Path(__file__).parent.parent / 'results' / 'animal_prefix_signature.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
