#!/usr/bin/env python3
"""
Test: Does RI behave like PRODUCT TYPES or MATERIAL INPUTS?

If RI = product type:
  - Similar procedures (PP) should yield similar products (RI)
  - PP-similar folios should share RI

If RI = material input:
  - Same procedure can apply to different materials
  - PP-similar folios should have DIFFERENT RI
"""

import json
import csv
from collections import defaultdict
from pathlib import Path
from itertools import combinations

PROJECT_ROOT = Path('.')

# Load classifications
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])
pp_middles = set(data['a_shared_middles'])

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_middle(token):
    if not token:
        return None
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break
    return token if token else None

# Collect folio PP and RI profiles
folio_pp = defaultdict(set)
folio_ri = defaultdict(set)

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        if not word or '*' in word:
            continue
        middle = extract_middle(word)
        if middle:
            if middle in ri_middles:
                folio_ri[folio].add(middle)
            elif middle in pp_middles:
                folio_pp[folio].add(middle)

# Group folios by PP profile (similar procedures)
pp_similar_pairs = []
folios = list(folio_pp.keys())
for f1, f2 in combinations(folios, 2):
    pp1, pp2 = folio_pp[f1], folio_pp[f2]
    if not pp1 or not pp2:
        continue
    jaccard = len(pp1 & pp2) / len(pp1 | pp2) if pp1 | pp2 else 0
    if jaccard >= 0.5:  # High PP overlap
        ri1, ri2 = folio_ri.get(f1, set()), folio_ri.get(f2, set())
        ri_jaccard = len(ri1 & ri2) / len(ri1 | ri2) if ri1 | ri2 else 0
        pp_similar_pairs.append({
            'f1': f1, 'f2': f2,
            'pp_jaccard': jaccard,
            'ri_jaccard': ri_jaccard,
            'shared_ri': ri1 & ri2
        })

print('FOLIOS WITH SIMILAR PP PROFILES (Jaccard >= 0.5)')
print('='*60)
print(f'Total pairs with similar PP: {len(pp_similar_pairs)}')

if pp_similar_pairs:
    avg_ri_jaccard = sum(p['ri_jaccard'] for p in pp_similar_pairs) / len(pp_similar_pairs)
    pairs_with_shared_ri = sum(1 for p in pp_similar_pairs if p['ri_jaccard'] > 0)
    print(f'Average RI Jaccard among PP-similar pairs: {avg_ri_jaccard:.3f}')
    print(f'Pairs with ANY shared RI: {pairs_with_shared_ri} ({100*pairs_with_shared_ri/len(pp_similar_pairs):.1f}%)')

    print('\nIf RI = PRODUCT TYPE:')
    print('  Similar procedures (PP) should produce similar products (RI)')
    print('  Expected: HIGH RI overlap among PP-similar folios')
    print(f'  Observed: {avg_ri_jaccard:.3f} average RI Jaccard')

    print('\nIf RI = MATERIAL INPUT:')
    print('  Similar procedures can be applied to DIFFERENT materials')
    print('  Expected: LOW RI overlap (different inputs, same process)')
    print(f'  Observed: {avg_ri_jaccard:.3f} average RI Jaccard')

# Show some examples
print('\n' + '='*60)
print('EXAMPLE PAIRS (high PP similarity)')
print('='*60)
for p in sorted(pp_similar_pairs, key=lambda x: -x['pp_jaccard'])[:10]:
    print(f"  {p['f1']} + {p['f2']}: PP={p['pp_jaccard']:.2f}, RI={p['ri_jaccard']:.2f}, shared RI: {p['shared_ri'] or 'none'}")

# Also check: do same RI appear with different PP?
print('\n' + '='*60)
print('REVERSE TEST: DO SAME RI APPEAR WITH DIFFERENT PP?')
print('='*60)

ri_to_pp = defaultdict(list)
for folio in folio_ri:
    for ri in folio_ri[folio]:
        ri_to_pp[ri].append(folio_pp.get(folio, set()))

# For RI appearing on 2+ folios, how similar are their PP profiles?
multi_folio_ri = {ri: pps for ri, pps in ri_to_pp.items() if len(pps) >= 2}
print(f'\nRI appearing on 2+ folios: {len(multi_folio_ri)}')

if multi_folio_ri:
    pp_similarity_per_ri = []
    for ri, pp_sets in multi_folio_ri.items():
        # Average pairwise PP similarity
        if len(pp_sets) >= 2:
            sims = []
            for i, pp1 in enumerate(pp_sets):
                for pp2 in pp_sets[i+1:]:
                    if pp1 and pp2:
                        sims.append(len(pp1 & pp2) / len(pp1 | pp2))
            if sims:
                pp_similarity_per_ri.append(sum(sims)/len(sims))

    if pp_similarity_per_ri:
        avg_pp_sim = sum(pp_similarity_per_ri) / len(pp_similarity_per_ri)
        print(f'Average PP similarity among folios sharing same RI: {avg_pp_sim:.3f}')

        print('\nIf RI = PRODUCT TYPE:')
        print('  Same product should come from similar procedures')
        print('  Expected: HIGH PP similarity among folios with same RI')

        print('\nIf RI = MATERIAL INPUT:')
        print('  Same material can undergo different procedures')
        print('  Expected: VARIABLE PP similarity')
        print(f'  Observed: {avg_pp_sim:.3f}')

print('\n' + '='*60)
print('VERDICT')
print('='*60)
