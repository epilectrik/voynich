"""Test if Currier A line tokens match C section folios."""
from apps.azc_folio_animator.core.folio_loader import FolioLoader

loader = FolioLoader()
loader.load()

# Get f1r line 3 tokens
folio = loader.get_folio('1r')
line3 = folio.lines[2] if len(folio.lines) > 2 else []
line3_tokens = [t.text for t in line3]
print('f1r line 3 tokens:', line3_tokens)

# C section folios
c_folios = ['f57v', 'f67v2', 'f68v3', 'f69r', 'f69v', 'f70r1', 'f70r2']

# A section folios (for comparison)
a_folios = ['f67r1', 'f67r2', 'f67v1', 'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2']

# Z section folios
z_folios = ['f70v1', 'f70v2', 'f71r', 'f71v', 'f72r1', 'f72r2']

print('\n=== C Section Matches ===')
for c_id in c_folios:
    c_folio = loader.get_folio(c_id.lstrip('f'))
    if c_folio:
        c_tokens = set(t.text for t in c_folio.tokens)
        matches = [t for t in line3_tokens if t in c_tokens]
        print(f'{c_id}: {len(matches)}/{len(line3_tokens)} match -> {matches}')

print('\n=== A Section Matches ===')
for a_id in a_folios[:4]:
    a_folio = loader.get_folio(a_id.lstrip('f'))
    if a_folio:
        a_tokens = set(t.text for t in a_folio.tokens)
        matches = [t for t in line3_tokens if t in a_tokens]
        print(f'{a_id}: {len(matches)}/{len(line3_tokens)} match -> {matches}')

print('\n=== Z Section Matches ===')
for z_id in z_folios[:4]:
    z_folio = loader.get_folio(z_id.lstrip('f'))
    if z_folio:
        z_tokens = set(t.text for t in z_folio.tokens)
        matches = [t for t in line3_tokens if t in z_tokens]
        print(f'{z_id}: {len(matches)}/{len(line3_tokens)} match -> {matches}')
