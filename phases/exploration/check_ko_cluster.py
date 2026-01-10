#!/usr/bin/env python
"""Check if ko- clustering in early folios is significant."""
import json

with open('C:/git/voynich/phases/exploration/first_token_data.json', 'r') as f:
    data = json.load(f)

records = data['records']

print('=== ko- Distribution ===')
print()

# Show full folio sequence with ko- marked
print('Folio sequence (ko- marked with ***):')
for r in records:
    marker = '***' if r['prefix_2char'] == 'ko' else '   '
    print(f"  {r['folio_id']:6} {marker} {r['token']}")

print()
print('=== ko- positions ===')
ko_folios = [r['folio_id'] for r in records if r['prefix_2char'] == 'ko']
print(f'ko- folios: {ko_folios}')

# Extract folio numbers
ko_nums = []
for f in ko_folios:
    num = int(f[:-1])
    side = f[-1]
    ko_nums.append((num, side))

print(f'Folio numbers: {ko_nums}')

# Check if ko- concentrates in folio range 2-6
early = sum(1 for n, s in ko_nums if n <= 6)
late = sum(1 for n, s in ko_nums if n > 6)

print()
print(f'ko- in folios 1-6: {early}')
print(f'ko- in folios 7+: {late}')

# Expected if random (6/48 ko- tokens, 12/48 folios are 1-6)
# Expected early = 6 * (12/48) = 1.5
print()
print('If ko- were random across 48 folios:')
print(f'  Expected in f1-6 (12 folios): {6 * 12/48:.1f}')
print(f'  Observed in f1-6: {early}')
print(f'  Enrichment: {early / (6 * 12/48):.1f}x')
