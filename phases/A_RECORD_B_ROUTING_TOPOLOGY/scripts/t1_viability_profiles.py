"""
T1: A-Record B-Viability Profiles

Build survivor sets: for each A-record, which B-folios could it produce?

An A-record R "permits" a B-folio F if R's PP vocabulary is a subset of F's PP vocabulary.
This is the core filtering mechanism from C502.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("T1: A-RECORD B-VIABILITY PROFILES")
print("=" * 70)

# Step 1: Build A-record PP inventories
print("\nStep 1: Building A-record PP inventories...")

a_record_pp = defaultdict(set)  # (folio, line) -> set of PP MIDDLEs
a_record_all = defaultdict(set)  # (folio, line) -> set of all MIDDLEs

for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    m = morph.extract(w)
    if not m.middle:
        continue

    key = (token.folio, token.line)
    a_record_all[key].add(m.middle)

    # PP = shared with B (we'll compute this properly)
    # For now, collect all MIDDLEs

# Step 2: Build B-folio PP inventories
print("Step 2: Building B-folio PP inventories...")

b_folio_middles = defaultdict(set)  # folio -> set of MIDDLEs
all_b_middles = set()

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    m = morph.extract(w)
    if not m.middle:
        continue

    b_folio_middles[token.folio].add(m.middle)
    all_b_middles.add(m.middle)

print(f"  B folios: {len(b_folio_middles)}")
print(f"  B MIDDLEs: {len(all_b_middles)}")

# Step 3: Compute PP set (MIDDLEs shared between A and B)
all_a_middles = set()
for middles in a_record_all.values():
    all_a_middles.update(middles)

pp_vocabulary = all_a_middles & all_b_middles
print(f"\nPP vocabulary (A & B): {len(pp_vocabulary)}")

# Step 4: Filter A-records to PP only
for key in a_record_all:
    a_record_pp[key] = a_record_all[key] & pp_vocabulary

# Step 5: Compute viability profiles
print("\nStep 5: Computing viability profiles...")

# For each A-record, find which B-folios it can produce
# A-record R permits B-folio F if R's PP ⊆ F's PP
viability_profiles = {}  # (folio, line) -> set of viable B-folios

b_folio_pp = {}
for folio, middles in b_folio_middles.items():
    b_folio_pp[folio] = middles & pp_vocabulary

b_folios = list(b_folio_pp.keys())

for a_key, a_pp in a_record_pp.items():
    if not a_pp:  # No PP MIDDLEs = universal viability
        viability_profiles[a_key] = set(b_folios)
        continue

    viable = set()
    for b_folio in b_folios:
        if a_pp.issubset(b_folio_pp[b_folio]):
            viable.add(b_folio)

    viability_profiles[a_key] = viable

# Step 6: Analyze viability profiles
print("\nStep 6: Analyzing viability profiles...")

viability_sizes = [len(v) for v in viability_profiles.values()]
n_records = len(viability_profiles)
n_b_folios = len(b_folios)

print(f"\n  A-records: {n_records}")
print(f"  B-folios: {n_b_folios}")
print(f"\n  Viability size distribution:")
print(f"    Mean: {np.mean(viability_sizes):.1f} folios")
print(f"    Median: {np.median(viability_sizes):.1f} folios")
print(f"    Std: {np.std(viability_sizes):.1f}")
print(f"    Min: {np.min(viability_sizes)}")
print(f"    Max: {np.max(viability_sizes)}")

# Filtering rate
mean_filter = 1 - (np.mean(viability_sizes) / n_b_folios)
print(f"\n  Mean filtering rate: {mean_filter*100:.1f}%")

# Universal records (can produce any B-folio)
universal = sum(1 for v in viability_sizes if v == n_b_folios)
print(f"  Universal records: {universal} ({universal/n_records*100:.1f}%)")

# Narrow records (< 10 viable folios)
narrow = sum(1 for v in viability_sizes if v < 10)
print(f"  Narrow records (<10 viable): {narrow} ({narrow/n_records*100:.1f}%)")

# Zero-viability records
zero = sum(1 for v in viability_sizes if v == 0)
print(f"  Zero-viability records: {zero} ({zero/n_records*100:.1f}%)")

# Step 7: Build profile vectors for clustering
print("\nStep 7: Building profile vectors...")

# Each A-record becomes a binary vector over B-folios
profile_vectors = {}
for a_key, viable in viability_profiles.items():
    vec = np.zeros(len(b_folios), dtype=np.int8)
    for i, f in enumerate(b_folios):
        if f in viable:
            vec[i] = 1
    profile_vectors[a_key] = vec

# Save results
results = {
    'n_a_records': n_records,
    'n_b_folios': n_b_folios,
    'pp_vocabulary_size': len(pp_vocabulary),
    'viability_stats': {
        'mean': float(np.mean(viability_sizes)),
        'median': float(np.median(viability_sizes)),
        'std': float(np.std(viability_sizes)),
        'min': int(np.min(viability_sizes)),
        'max': int(np.max(viability_sizes)),
    },
    'filtering_rate': float(mean_filter),
    'universal_records': universal,
    'narrow_records': narrow,
    'zero_viability_records': zero,
    'b_folios': b_folios,
}

# Save profile vectors for next script
profile_data = {
    'b_folios': b_folios,
    'profiles': {f"{k[0]}_{k[1]}": v.tolist() for k, v in profile_vectors.items()},
    'a_record_pp': {f"{k[0]}_{k[1]}": list(v) for k, v in a_record_pp.items()},
}

out_dir = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results'
with open(out_dir / 't1_viability_profiles.json', 'w') as f:
    json.dump(results, f, indent=2)

with open(out_dir / 't1_profile_vectors.json', 'w') as f:
    json.dump(profile_data, f, indent=2)

print(f"\nResults saved.")
