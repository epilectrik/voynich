"""Test for a 'baseline' AZC folio that dodges constraint mechanisms."""
from apps.azc_folio_animator.core.folio_loader import FolioLoader
from collections import Counter

loader = FolioLoader()
loader.load()

# Get all AZC folios and their vocabularies
azc_ids = loader.get_azc_folio_ids()
azc_vocabs = {}
for azc_id in azc_ids:
    folio = loader.get_folio(azc_id.lstrip('f'))
    if folio:
        azc_vocabs[azc_id] = set(t.text for t in folio.tokens)

print(f"AZC folios: {len(azc_vocabs)}")

# Get Currier A test folios vocabulary
test_folios = ['1r', '1v', '2r', '3r', '4r', '5r', '10r', '15r', '20r', '25r', '30r']
currier_a_tokens = []
currier_a_types = set()

for fid in test_folios:
    folio = loader.get_folio(fid)
    if folio:
        for t in folio.tokens:
            currier_a_tokens.append(t.text)
            currier_a_types.add(t.text)

currier_a_freq = Counter(currier_a_tokens)
print(f"Currier A types: {len(currier_a_types)}")
print(f"Currier A tokens: {len(currier_a_tokens)}")

# For each AZC folio, measure:
# 1. How many Currier A types it contains
# 2. How many Currier A token occurrences it covers
# 3. Size of its own vocabulary (smaller = simpler?)

print("\n=== AZC Folio Compatibility with Currier A ===")
print(f"{'Folio':<10} {'Types':<8} {'Tokens':<8} {'Coverage%':<10} {'Own Size':<10}")
print("-" * 50)

results = []
for azc_id, vocab in azc_vocabs.items():
    # Types covered
    types_covered = len(currier_a_types & vocab)

    # Token occurrences covered
    tokens_covered = sum(currier_a_freq[t] for t in currier_a_types & vocab)

    # Coverage percentage (by occurrence)
    coverage_pct = 100 * tokens_covered / len(currier_a_tokens)

    results.append({
        'folio': azc_id,
        'types': types_covered,
        'tokens': tokens_covered,
        'coverage': coverage_pct,
        'own_size': len(vocab)
    })

# Sort by coverage (highest first)
results.sort(key=lambda x: -x['coverage'])

for r in results:
    print(f"{r['folio']:<10} {r['types']:<8} {r['tokens']:<8} {r['coverage']:<10.1f} {r['own_size']:<10}")

# Identify potential baseline
print("\n=== BASELINE CANDIDATE ===")
top = results[0]
print(f"Highest coverage: {top['folio']}")
print(f"  Covers {top['types']} types, {top['tokens']} token occurrences ({top['coverage']:.1f}%)")
print(f"  Own vocabulary size: {top['own_size']}")

# Check if there's a clear winner or a cluster
print("\n=== Top 5 vs Bottom 5 ===")
print("Top 5:")
for r in results[:5]:
    print(f"  {r['folio']}: {r['coverage']:.1f}% coverage")
print("Bottom 5:")
for r in results[-5:]:
    print(f"  {r['folio']}: {r['coverage']:.1f}% coverage")

# Gap between top and rest?
if len(results) > 1:
    gap = results[0]['coverage'] - results[1]['coverage']
    print(f"\nGap between #1 and #2: {gap:.1f}%")
