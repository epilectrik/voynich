#!/usr/bin/env python
"""Check bifolio pattern - which side passes when mixed?"""
import json
from scipy import stats

with open('C:/git/voynich/phases/exploration/first_token_data.json', 'r') as f:
    data = json.load(f)

records = data['records']

# Group by folio number
from collections import defaultdict
by_folio_num = defaultdict(dict)
for r in records:
    num = int(r['folio_id'][:-1])
    side = r['folio_id'][-1]
    by_folio_num[num][side] = r

print('=== Mixed Folios: Which Side Passes? ===')
print()

recto_passes = 0
verso_passes = 0

for num in sorted(by_folio_num.keys()):
    sides = by_folio_num[num]
    if 'r' in sides and 'v' in sides:
        r_pass = sides['r']['is_pass']
        v_pass = sides['v']['is_pass']

        if r_pass != v_pass:  # Mixed
            if r_pass:
                recto_passes += 1
                winner = 'RECTO'
            else:
                verso_passes += 1
                winner = 'VERSO'

            print(f"f{num}: {winner} passes")
            print(f"  Recto: {sides['r']['token']} ({'PASS' if r_pass else 'fail'})")
            print(f"  Verso: {sides['v']['token']} ({'PASS' if v_pass else 'fail'})")
            print()

print(f'=== Summary ===')
print(f'When mixed, RECTO passes: {recto_passes}')
print(f'When mixed, VERSO passes: {verso_passes}')

# Binomial test - is this 50/50?
if recto_passes + verso_passes > 0:
    result = stats.binomtest(recto_passes, recto_passes + verso_passes, 0.5)
    p = result.pvalue
    print(f'Binomial test (50/50): p = {p:.4f}')

# Check if there's alternation
print()
print('=== Alternation Pattern ===')
mixed_folios = []
for num in sorted(by_folio_num.keys()):
    sides = by_folio_num[num]
    if 'r' in sides and 'v' in sides:
        r_pass = sides['r']['is_pass']
        v_pass = sides['v']['is_pass']
        if r_pass != v_pass:
            mixed_folios.append((num, 'r' if r_pass else 'v'))

print('Mixed folios (which side passes):')
for num, side in mixed_folios:
    print(f'  f{num}: {side}')

# Check if passing side alternates
sides_seq = [s for _, s in mixed_folios]
print()
print(f'Sequence: {sides_seq}')

# Count transitions
rr = sum(1 for i in range(len(sides_seq)-1) if sides_seq[i] == 'r' and sides_seq[i+1] == 'r')
rv = sum(1 for i in range(len(sides_seq)-1) if sides_seq[i] == 'r' and sides_seq[i+1] == 'v')
vr = sum(1 for i in range(len(sides_seq)-1) if sides_seq[i] == 'v' and sides_seq[i+1] == 'r')
vv = sum(1 for i in range(len(sides_seq)-1) if sides_seq[i] == 'v' and sides_seq[i+1] == 'v')

print(f'Transitions: r->r={rr}, r->v={rv}, v->r={vr}, v->v={vv}')
alternations = rv + vr
same = rr + vv
print(f'Alternations: {alternations}, Same: {same}')
