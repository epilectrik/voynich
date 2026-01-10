#!/usr/bin/env python
"""Check if there's a pattern to when position 1 passes vs fails."""
import json

with open('C:/git/voynich/phases/exploration/first_token_data.json', 'r') as f:
    data = json.load(f)

records = data['records']

print('=== Pass/Fail by Folio Number ===')
print()

# Group by folio number (ignoring r/v)
from collections import defaultdict
by_folio_num = defaultdict(list)
for r in records:
    num = int(r['folio_id'][:-1])
    by_folio_num[num].append(r)

print('Folio  Recto           Verso')
print('-' * 50)
for num in sorted(by_folio_num.keys()):
    recs = by_folio_num[num]
    recto = next((r for r in recs if r['folio_id'].endswith('r')), None)
    verso = next((r for r in recs if r['folio_id'].endswith('v')), None)

    r_status = 'PASS' if recto and recto['is_pass'] else 'fail' if recto else '----'
    v_status = 'PASS' if verso and verso['is_pass'] else 'fail' if verso else '----'

    r_token = recto['token'][:12] if recto else ''
    v_token = verso['token'][:12] if verso else ''

    print(f'{num:3}    {r_status} {r_token:<12}  {v_status} {v_token:<12}')

# Check patterns
print()
print('=== Pattern Analysis ===')

# Both sides same?
both_pass = 0
both_fail = 0
mixed = 0

for num in sorted(by_folio_num.keys()):
    recs = by_folio_num[num]
    if len(recs) == 2:
        r_pass = any(r['is_pass'] for r in recs if r['folio_id'].endswith('r'))
        v_pass = any(r['is_pass'] for r in recs if r['folio_id'].endswith('v'))

        if r_pass and v_pass:
            both_pass += 1
        elif not r_pass and not v_pass:
            both_fail += 1
        else:
            mixed += 1

print(f'Both sides PASS: {both_pass}')
print(f'Both sides FAIL: {both_fail}')
print(f'Mixed (one pass, one fail): {mixed}')

# Check recto vs verso overall
print()
print('=== Recto vs Verso ===')
recto_pass = sum(1 for r in records if r['folio_id'].endswith('r') and r['is_pass'])
recto_total = sum(1 for r in records if r['folio_id'].endswith('r'))
verso_pass = sum(1 for r in records if r['folio_id'].endswith('v') and r['is_pass'])
verso_total = sum(1 for r in records if r['folio_id'].endswith('v'))

print(f'Recto: {recto_pass}/{recto_total} pass ({100*recto_pass/recto_total:.1f}%)')
print(f'Verso: {verso_pass}/{verso_total} pass ({100*verso_pass/verso_total:.1f}%)')

# Check if passing folios cluster
print()
print('=== Clustering ===')
pass_folios = [int(r['folio_id'][:-1]) for r in records if r['is_pass']]
print(f'Passing folio numbers: {sorted(set(pass_folios))}')

# Check quire distribution
print()
print('=== By Quire ===')
quires = {
    'Q1 (1-8)': [r for r in records if 1 <= int(r['folio_id'][:-1]) <= 8],
    'Q2 (9-16)': [r for r in records if 9 <= int(r['folio_id'][:-1]) <= 16],
    'Q3 (17-24)': [r for r in records if 17 <= int(r['folio_id'][:-1]) <= 24],
    'Q4 (25+)': [r for r in records if int(r['folio_id'][:-1]) >= 25],
}

for q, recs in quires.items():
    if recs:
        passes = sum(1 for r in recs if r['is_pass'])
        print(f'{q}: {passes}/{len(recs)} pass ({100*passes/len(recs):.1f}%)')
