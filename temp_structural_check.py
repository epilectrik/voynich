"""Check structural token AZC folio profiles."""
from apps.azc_folio_animator.core.folio_loader import FolioLoader
from apps.azc_folio_animator.core.azc_folio_model import AZCFolioRegistry

loader = FolioLoader()
loader.load()
registry = AZCFolioRegistry(loader)

# Check structural tokens
structural = ['ar', 'al', 'ol', 'or', 'daiin', 'aiin', 'dar', 'chol', 'shol', 'y']

print('=== Structural Token AZC Folio Profiles ===')
print()

folio_sets = {}
for token in structural:
    folios = {f.folio_id for f in registry.get_activated_folios(token)}
    folio_sets[token] = folios
    print(f'{token:8} -> {len(folios):2} folios: {sorted(folios)[:10]}')

print()
print('=== Pairwise Intersections ===')
pairs = [('ar', 'daiin'), ('ar', 'ol'), ('daiin', 'ol'), ('ar', 'al'), ('chol', 'shol')]
for t1, t2 in pairs:
    if t1 in folio_sets and t2 in folio_sets:
        inter = folio_sets[t1] & folio_sets[t2]
        print(f'{t1} AND {t2} = {len(inter)} folios: {sorted(inter)}')

print()
print('=== Cumulative Intersection ===')
cumulative = None
for token in ['ar', 'daiin', 'ol', 'al', 'or']:
    if token not in folio_sets:
        continue
    if cumulative is None:
        cumulative = folio_sets[token]
    else:
        cumulative = cumulative & folio_sets[token]
    print(f'After {token}: {len(cumulative)} folios remaining: {sorted(cumulative)}')

print()
print('=== Total AZC Folios ===')
print(f'Total AZC folios in registry: {len(registry.get_all_folio_ids())}')
print(f'All AZC folio IDs: {registry.get_all_folio_ids()}')
