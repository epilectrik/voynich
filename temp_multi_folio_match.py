"""Test if different Currier A folios match AZC folios."""
from apps.azc_folio_animator.core.folio_loader import FolioLoader

loader = FolioLoader()
loader.load()

# Build token sets for all AZC folios
azc_ids = loader.get_azc_folio_ids()
azc_token_sets = {}
for azc_id in azc_ids:
    azc_folio = loader.get_folio(azc_id.lstrip('f'))
    if azc_folio:
        azc_token_sets[azc_id] = set(t.text for t in azc_folio.tokens)

print(f"AZC folios loaded: {len(azc_token_sets)}")
print(f"Total unique AZC tokens: {len(set.union(*azc_token_sets.values()))}")

# Test several Currier A folios
test_folios = ['1r', '1v', '2r', '3r', '4r', '5r', '10r', '15r', '20r']

for test_id in test_folios:
    folio = loader.get_folio(test_id)
    if not folio or not folio.lines:
        continue

    # Get all tokens from this folio
    all_tokens = [t.text for t in folio.tokens]
    unique_tokens = set(all_tokens)

    # Count how many match ANY AZC folio
    all_azc_tokens = set.union(*azc_token_sets.values())
    matching = unique_tokens & all_azc_tokens

    # Find best single AZC folio match
    best_match = 0
    best_folio = None
    for azc_id, azc_tokens in azc_token_sets.items():
        match_count = len(unique_tokens & azc_tokens)
        if match_count > best_match:
            best_match = match_count
            best_folio = azc_id

    print(f"\nf{test_id}: {len(unique_tokens)} unique tokens")
    print(f"  Match ANY AZC: {len(matching)}/{len(unique_tokens)} ({100*len(matching)/len(unique_tokens):.1f}%)")
    print(f"  Best single AZC: {best_folio} with {best_match} matches")
    print(f"  Sample matches: {list(matching)[:8]}")
