import json
from collections import Counter

# Check Puff aromatic distribution
with open('results/puff_83_chapters.json') as f:
    puff = json.load(f)

aromatic_herbs = [ch for ch in puff['chapters'] if ch.get('aromatic') and ch.get('category') == 'HERB']
print(f'Aromatic HERBs: {len(aromatic_herbs)}')
for ch in aromatic_herbs:
    print(f'  Ch.{ch["chapter"]}: {ch["german"]}')

# Check dangerous distribution
dangerous = [ch for ch in puff['chapters'] if ch.get('dangerous')]
print(f'\nDangerous chapters: {len(dangerous)}')
for ch in dangerous:
    print(f'  Ch.{ch["chapter"]}: {ch["german"]} - {ch["category"]}')

# Category breakdown
cats = Counter(ch['category'] for ch in puff['chapters'])
print(f'\nFull category breakdown:')
for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
    print(f'  {cat}: {count}')

# What if we reclassify aromatic herbs as degree 1?
aromatics_in_herbs = len(aromatic_herbs)
print(f'\n--- RECLASSIFICATION TEST ---')
print(f'If aromatic HERBs treated as degree 1 (like flowers):')
print(f'  Degree 1: 22 flowers + {aromatics_in_herbs} aromatic herbs = {22 + aromatics_in_herbs}')
print(f'  Degree 2: 45 herbs - {aromatics_in_herbs} aromatics = {45 - aromatics_in_herbs}')

# Check regime distribution again
with open('results/unified_folio_profiles.json') as f:
    profiles = json.load(f)

regime_counts = Counter()
for folio_name, folio_data in profiles.get('profiles', {}).items():
    if isinstance(folio_data, dict) and folio_data.get('system') == 'B':
        b_metrics = folio_data.get('b_metrics', {})
        if b_metrics:
            regime_counts[b_metrics.get('regime')] += 1

print(f'\nVoynich regime distribution:')
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    print(f'  {regime}: {regime_counts[regime]}')
