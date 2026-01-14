"""Quick script to find forgiving/brittle/mixed B folios."""
import json
import statistics

with open('results/unified_folio_profiles.json') as f:
    data = json.load(f)

# Find B folios and their metrics
b_folios = []
for folio_id, profile in data['profiles'].items():
    if profile.get('system') == 'B' and profile.get('b_metrics'):
        b_folios.append({
            'folio': folio_id,
            'hazard': profile['b_metrics'].get('hazard_density', 0),
            'escape': profile['b_metrics'].get('escape_density', 0),
            'link': profile['b_metrics'].get('link_density', 0),
            'cei': profile['b_metrics'].get('cei_total', 0)
        })

# Sort by hazard (high = brittle)
b_folios.sort(key=lambda x: x['hazard'], reverse=True)

print('Top 5 Brittle (high hazard):')
for f in b_folios[:5]:
    print(f"  {f['folio']}: hazard={f['hazard']:.3f}, link={f['link']:.3f}")

print()
b_folios.sort(key=lambda x: x['hazard'])
print('Top 5 Forgiving (low hazard):')
for f in b_folios[:5]:
    print(f"  {f['folio']}: hazard={f['hazard']:.3f}, link={f['link']:.3f}")

print()
# Find median
hazards = [f['hazard'] for f in b_folios]
median_hazard = statistics.median(hazards)
print(f'Median hazard: {median_hazard:.3f}')

# Mixed (near median)
b_folios.sort(key=lambda x: abs(x['hazard'] - median_hazard))
print('Top 5 Mixed (near median):')
for f in b_folios[:5]:
    print(f"  {f['folio']}: hazard={f['hazard']:.3f}, link={f['link']:.3f}")

print(f'\nTotal B folios with metrics: {len(b_folios)}')
