#!/usr/bin/env python3
"""
Identify A folios with animal content and analyze their record structure.

Goal: Use animal folios to understand A record patterns better.
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript, Morphology

# Load validated mappings
mappings_path = Path(__file__).parent.parent / 'phases' / 'MATERIAL_MAPPING_V2' / 'results' / 'validated_mappings.json'
with open(mappings_path) as f:
    mapping_data = json.load(f)

# Extract animal records by folio
animal_records_by_folio = defaultdict(list)
for mapping in mapping_data.get('validated_mappings', []):
    record_id = mapping['record_id']
    folio = record_id.split(':')[0]
    animal_records_by_folio[folio].append({
        'record_id': record_id,
        'recipe': mapping['recipe'],
        'ri_tokens': mapping['ri_tokens'],
        'confidence': mapping['confidence'],
        'score': mapping['score']
    })

print("="*70)
print("ANIMAL-RELATED A FOLIOS")
print("="*70)

# Sort folios by animal record count
folio_counts = [(f, len(recs)) for f, recs in animal_records_by_folio.items()]
folio_counts.sort(key=lambda x: -x[1])

print(f"\n{'Folio':<12} {'Animal Records':<15} {'Recipes':<30}")
print("-"*60)

for folio, count in folio_counts:
    recipes = set(r['recipe'] for r in animal_records_by_folio[folio])
    recipe_str = ', '.join(recipes)[:28]
    print(f"{folio:<12} {count:<15} {recipe_str:<30}")

# Identify high-concentration animal folios
high_animal_folios = [f for f, c in folio_counts if c >= 3]
print(f"\nHigh-concentration animal folios (3+ records): {high_animal_folios}")

# Now analyze A records on these folios
print(f"\n{'='*70}")
print("A RECORD ANALYSIS ON ANIMAL FOLIOS")
print("="*70)

tx = Transcript()
morph = Morphology()

# Build A folio data
a_folio_data = defaultdict(lambda: {'records': [], 'tokens': []})

for token in tx.currier_a():
    if '*' in token.word:
        continue
    a_folio_data[token.folio]['tokens'].append(token)

# Get paragraph structure for each folio
GALLOWS = {'k', 't', 'p', 'f'}

def get_paragraphs(tokens):
    """Group tokens into paragraphs based on gallows-initial lines."""
    if not tokens:
        return []

    # Group by line first
    lines = defaultdict(list)
    for t in tokens:
        lines[t.line].append(t)

    paragraphs = []
    current_para = []

    for line_num in sorted(lines.keys()):
        line_tokens = lines[line_num]
        if not line_tokens:
            continue
        first_word = line_tokens[0].word
        if first_word and first_word[0] in GALLOWS:
            if current_para:
                paragraphs.append(current_para)
            current_para = line_tokens
        else:
            current_para.extend(line_tokens)

    if current_para:
        paragraphs.append(current_para)

    return paragraphs

# Analyze animal folios vs non-animal folios
animal_folios = set(animal_records_by_folio.keys())
all_a_folios = set(a_folio_data.keys())

print(f"\nTotal A folios: {len(all_a_folios)}")
print(f"Folios with animal records: {len(animal_folios)}")

# Compare paragraph structure
animal_para_stats = []
non_animal_para_stats = []

for folio in all_a_folios:
    tokens = a_folio_data[folio]['tokens']
    paras = get_paragraphs(tokens)

    para_lengths = [len(p) for p in paras]

    stats = {
        'folio': folio,
        'n_paras': len(paras),
        'n_tokens': len(tokens),
        'mean_para_len': sum(para_lengths) / len(para_lengths) if para_lengths else 0,
    }

    if folio in animal_folios:
        animal_para_stats.append(stats)
    else:
        non_animal_para_stats.append(stats)

print(f"\n{'Metric':<25} {'Animal Folios':<20} {'Non-Animal Folios':<20}")
print("-"*65)

import numpy as np

if animal_para_stats and non_animal_para_stats:
    animal_n_paras = [s['n_paras'] for s in animal_para_stats]
    non_animal_n_paras = [s['n_paras'] for s in non_animal_para_stats]

    animal_n_tokens = [s['n_tokens'] for s in animal_para_stats]
    non_animal_n_tokens = [s['n_tokens'] for s in non_animal_para_stats]

    animal_para_len = [s['mean_para_len'] for s in animal_para_stats]
    non_animal_para_len = [s['mean_para_len'] for s in non_animal_para_stats]

    print(f"{'Mean paragraphs/folio':<25} {np.mean(animal_n_paras):<20.1f} {np.mean(non_animal_n_paras):<20.1f}")
    print(f"{'Mean tokens/folio':<25} {np.mean(animal_n_tokens):<20.1f} {np.mean(non_animal_n_tokens):<20.1f}")
    print(f"{'Mean para length':<25} {np.mean(animal_para_len):<20.1f} {np.mean(non_animal_para_len):<20.1f}")

# Analyze RI tokens on animal folios
print(f"\n{'='*70}")
print("RI TOKEN ANALYSIS ON ANIMAL FOLIOS")
print("="*70)

# Get all RI tokens from animal records
animal_ri_tokens = []
for folio, records in animal_records_by_folio.items():
    for rec in records:
        animal_ri_tokens.extend(rec['ri_tokens'])

print(f"\nTotal animal RI tokens: {len(animal_ri_tokens)}")
print(f"Unique: {len(set(animal_ri_tokens))}")

# Morphological analysis of animal RI
print(f"\n{'Token':<15} {'Prefix':<10} {'Middle':<12} {'Suffix':<8}")
print("-"*50)

for token in sorted(set(animal_ri_tokens))[:20]:
    try:
        m = morph.extract(token)
        prefix = m.prefix or '-'
        middle = m.middle or '-'
        suffix = m.suffix or '-'
        print(f"{token:<15} {prefix:<10} {middle:<12} {suffix:<8}")
    except:
        print(f"{token:<15} [parse error]")

# Prefix distribution
print(f"\n{'='*70}")
print("PREFIX DISTRIBUTION IN ANIMAL RI")
print("="*70)

prefix_counts = Counter()
for token in animal_ri_tokens:
    try:
        m = morph.extract(token)
        if m.prefix:
            prefix_counts[m.prefix] += 1
    except:
        pass

print(f"\n{'Prefix':<12} {'Count':<8} {'%':<8}")
print("-"*30)
total = sum(prefix_counts.values())
for prefix, count in prefix_counts.most_common(15):
    pct = 100 * count / total if total > 0 else 0
    print(f"{prefix:<12} {count:<8} {pct:<8.1f}")

# Compare to non-animal folios
print(f"\n{'='*70}")
print("COMPARISON: ANIMAL vs NON-ANIMAL RI PREFIXES")
print("="*70)

# Get RI from non-animal A folios (first token of each paragraph)
non_animal_ri = []
for folio in all_a_folios:
    if folio in animal_folios:
        continue
    tokens = a_folio_data[folio]['tokens']
    paras = get_paragraphs(tokens)
    for para in paras:
        if para:
            non_animal_ri.append(para[0].word)

non_animal_prefix_counts = Counter()
for token in non_animal_ri:
    try:
        m = morph.extract(token)
        if m.prefix:
            non_animal_prefix_counts[m.prefix] += 1
    except:
        pass

# Compare distributions
all_prefixes = set(prefix_counts.keys()) | set(non_animal_prefix_counts.keys())

print(f"\n{'Prefix':<12} {'Animal %':<12} {'Non-Animal %':<12} {'Ratio':<10}")
print("-"*50)

animal_total = sum(prefix_counts.values())
non_animal_total = sum(non_animal_prefix_counts.values())

for prefix in sorted(all_prefixes, key=lambda p: -prefix_counts.get(p, 0)):
    animal_pct = 100 * prefix_counts.get(prefix, 0) / animal_total if animal_total > 0 else 0
    non_animal_pct = 100 * non_animal_prefix_counts.get(prefix, 0) / non_animal_total if non_animal_total > 0 else 0

    if animal_pct > 0 and non_animal_pct > 0:
        ratio = animal_pct / non_animal_pct
    elif animal_pct > 0:
        ratio = float('inf')
    else:
        ratio = 0

    if animal_pct >= 3 or non_animal_pct >= 3:  # Only show significant prefixes
        ratio_str = f"{ratio:.2f}" if ratio != float('inf') else "INF"
        print(f"{prefix:<12} {animal_pct:<12.1f} {non_animal_pct:<12.1f} {ratio_str:<10}")

# Summary
print(f"\n{'='*70}")
print("SUMMARY")
print("="*70)

print(f"""
Animal-related A folios identified: {len(animal_folios)}
High-concentration (3+ records): {high_animal_folios}

Key patterns to investigate:
1. Do animal folios have different paragraph structure?
2. Do animal RI tokens have distinctive prefixes?
3. Do animal folios cluster in specific sections?
4. Can we use these patterns to identify more animal content?
""")

# Save results
output = {
    'animal_folios': list(animal_folios),
    'high_concentration_folios': high_animal_folios,
    'animal_record_count': sum(len(r) for r in animal_records_by_folio.values()),
    'prefix_distribution': dict(prefix_counts),
}

output_path = Path(__file__).parent.parent / 'results' / 'animal_folio_analysis.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
