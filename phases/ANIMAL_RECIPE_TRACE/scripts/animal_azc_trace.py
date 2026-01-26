"""
ANIMAL AZC TRACE (Phase 2)

Goal: For high-confidence animal A records, trace which B vocabulary is legal.
Uses C502.a full morphological filtering: PREFIX+MIDDLE+SUFFIX must all match.

Input: animal_signatures.json from Phase 1
Output: animal_compatible_vocabulary.json
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("PHASE 2: ANIMAL AZC TRACE")
print("=" * 70)

# Load Phase 1 results
with open('phases/ANIMAL_RECIPE_TRACE/results/animal_signatures.json', 'r') as f:
    phase1 = json.load(f)

animal_records = phase1['high_confidence_records']
print(f"\nLoaded {len(animal_records)} high-confidence animal records from Phase 1")

# Build A record morphological profiles
print("\nBuilding A record morphological profiles...")

a_record_profiles = {}
for token in tx.currier_a():
    record_id = f"{token.folio}:{token.line}"
    if record_id not in a_record_profiles:
        a_record_profiles[record_id] = {
            'middles': set(),
            'prefixes': set(),
            'suffixes': set(),
        }

    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            a_record_profiles[record_id]['middles'].add(m.middle)
        if m.prefix:
            a_record_profiles[record_id]['prefixes'].add(m.prefix)
        if m.suffix:
            a_record_profiles[record_id]['suffixes'].add(m.suffix)

# Add empty string for "no prefix" and "no suffix" cases
for profile in a_record_profiles.values():
    profile['prefixes'].add('')  # Allows BARE tokens
    profile['suffixes'].add('')  # Allows unsuffixed tokens

# Build B token morphological data
print("Building B token morphological data...")

b_tokens = []
b_token_set = set()
for token in tx.currier_b():
    if token.word and token.word not in b_token_set:
        m = morph.extract(token.word)
        b_tokens.append({
            'word': token.word,
            'middle': m.middle or '',
            'prefix': m.prefix or '',
            'suffix': m.suffix or '',
            'folio': token.folio,
        })
        b_token_set.add(token.word)

print(f"Total unique B tokens: {len(b_tokens)}")

# For each animal A record, find compatible B tokens
print("\nTracing animal records through AZC filtering...")

def get_compatible_b_tokens(a_profile, b_tokens):
    """
    Apply C502.a filtering: B token legal iff
    MIDDLE in A-record AND PREFIX in A-record AND SUFFIX in A-record
    """
    compatible = []
    for bt in b_tokens:
        middle_ok = bt['middle'] in a_profile['middles']
        prefix_ok = bt['prefix'] in a_profile['prefixes']
        suffix_ok = bt['suffix'] in a_profile['suffixes']

        if middle_ok and prefix_ok and suffix_ok:
            compatible.append(bt)

    return compatible

# Trace each animal record
animal_compatible = {}
all_animal_compatible_middles = Counter()
all_animal_compatible_tokens = Counter()

for rec in animal_records:
    record_id = rec['record_id']
    if record_id not in a_record_profiles:
        continue

    profile = a_record_profiles[record_id]
    compatible = get_compatible_b_tokens(profile, b_tokens)

    animal_compatible[record_id] = {
        'score': rec['total_score'],
        'n_compatible_tokens': len(compatible),
        'compatible_middles': list(set(t['middle'] for t in compatible if t['middle'])),
        'compatible_tokens': [t['word'] for t in compatible],
    }

    for t in compatible:
        if t['middle']:
            all_animal_compatible_middles[t['middle']] += 1
        all_animal_compatible_tokens[t['word']] += 1

# Statistics
compatible_counts = [v['n_compatible_tokens'] for v in animal_compatible.values()]

print(f"\nCompatibility results:")
print(f"  Animal records traced: {len(animal_compatible)}")
print(f"  Mean compatible B tokens per record: {np.mean(compatible_counts):.1f}")
print(f"  Min: {min(compatible_counts)}")
print(f"  Max: {max(compatible_counts)}")

print(f"\nUnique B MIDDLEs compatible with animal records: {len(all_animal_compatible_middles)}")
print(f"Unique B tokens compatible with animal records: {len(all_animal_compatible_tokens)}")

# Compare to baseline (random A records)
print("\n" + "=" * 70)
print("BASELINE COMPARISON")
print("=" * 70)

import random
random.seed(42)

# Sample same number of random A records
all_record_ids = list(a_record_profiles.keys())
random_records = random.sample(all_record_ids, min(len(animal_records), len(all_record_ids)))

random_compatible_middles = Counter()
random_compatible_counts = []

for record_id in random_records:
    profile = a_record_profiles[record_id]
    compatible = get_compatible_b_tokens(profile, b_tokens)
    random_compatible_counts.append(len(compatible))
    for t in compatible:
        if t['middle']:
            random_compatible_middles[t['middle']] += 1

print(f"\nRandom baseline ({len(random_records)} records):")
print(f"  Mean compatible B tokens: {np.mean(random_compatible_counts):.1f}")
print(f"  Unique MIDDLEs reached: {len(random_compatible_middles)}")

print(f"\nAnimal vs Random:")
print(f"  Animal mean tokens: {np.mean(compatible_counts):.1f}")
print(f"  Random mean tokens: {np.mean(random_compatible_counts):.1f}")
print(f"  Ratio: {np.mean(compatible_counts)/np.mean(random_compatible_counts):.2f}x")

# Find MIDDLEs that are ENRICHED in animal-compatible set
print("\n" + "=" * 70)
print("ANIMAL-ENRICHED B MIDDLES")
print("=" * 70)

# Normalize by number of records
animal_norm = {m: c/len(animal_compatible) for m, c in all_animal_compatible_middles.items()}
random_norm = {m: c/len(random_records) for m, c in random_compatible_middles.items()}

# Find enrichment
enriched_middles = []
for middle in all_animal_compatible_middles:
    animal_rate = animal_norm.get(middle, 0)
    random_rate = random_norm.get(middle, 0.001)  # Avoid division by zero
    enrichment = animal_rate / random_rate
    if enrichment > 1.5 and all_animal_compatible_middles[middle] >= 5:
        enriched_middles.append((middle, enrichment, all_animal_compatible_middles[middle]))

enriched_middles.sort(key=lambda x: -x[1])

print(f"\nMIDDLEs enriched >1.5× in animal records (min 5 occurrences):")
print(f"{'MIDDLE':<15} {'Enrichment':<12} {'Count':<8}")
print("-" * 35)
for middle, enrich, count in enriched_middles[:20]:
    print(f"{middle:<15} {enrich:.2f}×         {count}")

# Find which B FOLIOS receive the most animal-compatible vocabulary
print("\n" + "=" * 70)
print("B FOLIO ANIMAL RECEPTION (Preview for Phase 3)")
print("=" * 70)

# Build folio -> middle mapping
b_folio_middles = defaultdict(set)
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            b_folio_middles[token.folio].add(m.middle)

# For each folio, count animal-compatible MIDDLEs
folio_animal_reception = {}
animal_middles_set = set(all_animal_compatible_middles.keys())

for folio, middles in b_folio_middles.items():
    animal_compatible_in_folio = middles & animal_middles_set
    reception = len(animal_compatible_in_folio) / len(middles) if middles else 0
    folio_animal_reception[folio] = {
        'total_middles': len(middles),
        'animal_compatible': len(animal_compatible_in_folio),
        'reception_rate': reception,
    }

# Sort by reception rate
sorted_folios = sorted(folio_animal_reception.items(), key=lambda x: -x[1]['reception_rate'])

print(f"\nTop 15 B folios by animal reception rate:")
print(f"{'Folio':<12} {'Reception':<12} {'Animal/Total':<15}")
print("-" * 40)
for folio, data in sorted_folios[:15]:
    print(f"{folio:<12} {data['reception_rate']:.3f}        {data['animal_compatible']}/{data['total_middles']}")

# Save results
results = {
    'metadata': {
        'phase': 2,
        'description': 'Animal AZC trace',
        'animal_records_traced': len(animal_compatible),
        'unique_compatible_middles': len(all_animal_compatible_middles),
        'unique_compatible_tokens': len(all_animal_compatible_tokens),
    },
    'statistics': {
        'mean_compatible_tokens': float(np.mean(compatible_counts)),
        'min_compatible_tokens': int(min(compatible_counts)),
        'max_compatible_tokens': int(max(compatible_counts)),
        'baseline_mean_tokens': float(np.mean(random_compatible_counts)),
        'animal_vs_baseline_ratio': float(np.mean(compatible_counts)/np.mean(random_compatible_counts)),
    },
    'animal_compatible_middles': dict(all_animal_compatible_middles.most_common()),
    'enriched_middles': [
        {'middle': m, 'enrichment': e, 'count': c}
        for m, e, c in enriched_middles
    ],
    'folio_reception_preview': {
        folio: data for folio, data in sorted_folios[:30]
    },
}

output_path = 'phases/ANIMAL_RECIPE_TRACE/results/animal_compatible_vocabulary.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")

# Summary
print("\n" + "=" * 70)
print("PHASE 2 COMPLETE - SUMMARY FOR CHECKPOINT")
print("=" * 70)

print(f"""
Key Results:
- Animal records traced: {len(animal_compatible)}
- Unique compatible B MIDDLEs: {len(all_animal_compatible_middles)}
- Mean compatible tokens: {np.mean(compatible_counts):.1f} (baseline: {np.mean(random_compatible_counts):.1f})
- Animal/baseline ratio: {np.mean(compatible_counts)/np.mean(random_compatible_counts):.2f}×
- Enriched MIDDLEs (>1.5×): {len(enriched_middles)}
- Top enriched: '{enriched_middles[0][0]}' ({enriched_middles[0][1]:.2f}×) if enriched_middles else 'None'

Next Step: Phase 3 - Full folio reception analysis using these compatible MIDDLEs.
""")
