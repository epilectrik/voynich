from apps.azc_folio_animator.core.folio_loader import FolioLoader

loader = FolioLoader()
loader.load()

# Check f1r line 3 tokens
folio = loader.get_folio('1r')
line3 = folio.lines[2] if len(folio.lines) > 2 else []
print('Line 3 tokens:', [t.text for t in line3[:8]])

# Check what's in an AZC folio
azc_ids = loader.get_azc_folio_ids()
print('AZC folios:', azc_ids[:5])

azc_folio = loader.get_folio(azc_ids[0])
if azc_folio:
    sample = [t.text for t in azc_folio.tokens[:15]]
    print(f'Sample AZC tokens from {azc_ids[0]}:', sample)

# Build token sets for each AZC folio
azc_token_sets = {}
for azc_id in azc_ids:
    azc = loader.get_folio(azc_id)
    if azc:
        azc_token_sets[azc_id] = set(t.text for t in azc.tokens)

# Check if any line 3 token appears in any AZC folio
print('\n--- Checking matches (line 3) ---')
for token in line3[:8]:
    matches = []
    for azc_id, token_set in azc_token_sets.items():
        if token.text in token_set:
            matches.append(azc_id)
    print(f'{token.text}: {len(matches)} folios')

# Check line 1 too
line1 = folio.lines[0] if len(folio.lines) > 0 else []
print('\n--- Checking matches (line 1) ---')
for token in line1[:10]:
    matches = []
    for azc_id, token_set in azc_token_sets.items():
        if token.text in token_set:
            matches.append(azc_id)
    print(f'{token.text}: {len(matches)} folios')

# Check common tokens
print('\n--- Common tokens ---')
common = ['ar', 'ol', 'or', 'al', 'daiin', 'aiin', 'chol', 'shol', 'dar']
for t in common:
    matches = []
    for azc_id, token_set in azc_token_sets.items():
        if t in token_set:
            matches.append(azc_id)
    print(f'{t}: {len(matches)} folios')
