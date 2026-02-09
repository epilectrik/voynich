#!/usr/bin/env python3
"""
RI B-Survival Test - Controlling for PP Overlap

The question: Is the FINAL > INITIAL B survival finding real,
or just measuring that FINAL MIDDLEs happen to also be in PP?
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

# Build paragraph data
paragraphs = []
current_folio = None
current_para = []
current_line = None

for token in tx.currier_a():
    if '*' in token.word:
        continue
    if token.folio != current_folio:
        if current_para:
            paragraphs.append({'tokens': [t.word for t in current_para]})
        current_folio = token.folio
        current_para = [token]
        current_line = token.line
        continue
    if token.line != current_line:
        if token.word and token.word[0] in GALLOWS:
            paragraphs.append({'tokens': [t.word for t in current_para]})
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)
if current_para:
    paragraphs.append({'tokens': [t.word for t in current_para]})

print(f'Total A paragraphs: {len(paragraphs)}')

# Collect MIDDLEs by zone: INITIAL RI, FINAL RI, PP (middle zone)
initial_ri_middles = set()
final_ri_middles = set()
pp_middles = set()

for para in paragraphs:
    tokens = para['tokens']
    if len(tokens) < 4:
        continue

    # INITIAL RI = first 3
    for token in tokens[:3]:
        try:
            m = morph.extract(token)
            if m.middle:
                initial_ri_middles.add(m.middle)
        except:
            pass

    # FINAL RI = last 3
    for token in tokens[-3:]:
        try:
            m = morph.extract(token)
            if m.middle:
                final_ri_middles.add(m.middle)
        except:
            pass

    # PP = middle zone (positions 3 to -3)
    if len(tokens) > 6:
        for token in tokens[3:-3]:
            try:
                m = morph.extract(token)
                if m.middle:
                    pp_middles.add(m.middle)
            except:
                pass

print(f'\nMIDDLE counts by zone:')
print(f'  INITIAL RI: {len(initial_ri_middles)}')
print(f'  FINAL RI: {len(final_ri_middles)}')
print(f'  PP (middle): {len(pp_middles)}')

# Position-exclusive MIDDLEs
initial_only = initial_ri_middles - final_ri_middles
final_only = final_ri_middles - initial_ri_middles

print(f'\nPosition-exclusive:')
print(f'  INITIAL-only: {len(initial_only)}')
print(f'  FINAL-only: {len(final_only)}')

# KEY CHECK: How many of these also appear in PP?
initial_only_in_pp = initial_only & pp_middles
final_only_in_pp = final_only & pp_middles

initial_only_not_in_pp = initial_only - pp_middles
final_only_not_in_pp = final_only - pp_middles

print(f'\nPP OVERLAP CHECK:')
print(f'  INITIAL-only that ARE in PP: {len(initial_only_in_pp)} ({100*len(initial_only_in_pp)/len(initial_only):.1f}%)')
print(f'  INITIAL-only NOT in PP: {len(initial_only_not_in_pp)} ({100*len(initial_only_not_in_pp)/len(initial_only):.1f}%)')
print(f'  FINAL-only that ARE in PP: {len(final_only_in_pp)} ({100*len(final_only_in_pp)/len(final_only):.1f}%)')
print(f'  FINAL-only NOT in PP: {len(final_only_not_in_pp)} ({100*len(final_only_not_in_pp)/len(final_only):.1f}%)')

# B vocabulary
b_folio_middles = defaultdict(set)
for token in tx.currier_b():
    if '*' in token.word:
        continue
    try:
        m = morph.extract(token.word)
        if m.middle:
            b_folio_middles[token.folio].add(m.middle)
    except:
        pass

def b_survival_rate(middle):
    count = sum(1 for fv in b_folio_middles.values() if middle in fv)
    return count / len(b_folio_middles) if b_folio_middles else 0

# Re-run B survival test CONTROLLING for PP presence
print(f'\n' + '='*60)
print('B SURVIVAL - CONTROLLING FOR PP PRESENCE')
print('='*60)

# Only test MIDDLEs that are NOT in PP (pure RI vocabulary)
print(f'\nMIDDLEs NOT in PP (pure RI vocabulary):')
initial_pure_survival = [b_survival_rate(m) for m in initial_only_not_in_pp]
final_pure_survival = [b_survival_rate(m) for m in final_only_not_in_pp]

print(f'  INITIAL-only (not in PP): {len(initial_only_not_in_pp)} MIDDLEs')
print(f'    B survival = {np.mean(initial_pure_survival)*100:.1f}%')
print(f'  FINAL-only (not in PP): {len(final_only_not_in_pp)} MIDDLEs')
print(f'    B survival = {np.mean(final_pure_survival)*100:.1f}%')

if len(initial_pure_survival) >= 5 and len(final_pure_survival) >= 5:
    t_stat, p_value = stats.ttest_ind(initial_pure_survival, final_pure_survival)
    print(f'  T-test: t={t_stat:.3f}, p={p_value:.4f}')
    if p_value < 0.05:
        print(f'  ** SIGNIFICANT even without PP **')
    else:
        print(f'  Not significant')
else:
    print(f'  (Insufficient sample for t-test)')

# Test MIDDLEs that ARE in PP (shared vocabulary)
print(f'\nMIDDLEs that ARE in PP (shared vocabulary):')
initial_shared_survival = [b_survival_rate(m) for m in initial_only_in_pp]
final_shared_survival = [b_survival_rate(m) for m in final_only_in_pp]

print(f'  INITIAL-only (in PP): {len(initial_only_in_pp)} MIDDLEs')
print(f'    B survival = {np.mean(initial_shared_survival)*100:.1f}%')
print(f'  FINAL-only (in PP): {len(final_only_in_pp)} MIDDLEs')
print(f'    B survival = {np.mean(final_shared_survival)*100:.1f}%')

if len(initial_shared_survival) >= 5 and len(final_shared_survival) >= 5:
    t_stat, p_value = stats.ttest_ind(initial_shared_survival, final_shared_survival)
    print(f'  T-test: t={t_stat:.3f}, p={p_value:.4f}')
else:
    print(f'  (Insufficient sample for t-test)')

print(f'\n' + '='*60)
print('INTERPRETATION')
print('='*60)

# The key comparison
if len(initial_only_in_pp) > 0 and len(final_only_in_pp) > 0:
    in_pp_rate = len(final_only_in_pp) / len(final_only)
    initial_in_pp_rate = len(initial_only_in_pp) / len(initial_only)

    print(f'\nFINAL-only MIDDLEs in PP: {100*in_pp_rate:.1f}%')
    print(f'INITIAL-only MIDDLEs in PP: {100*initial_in_pp_rate:.1f}%')

    if in_pp_rate > initial_in_pp_rate:
        print(f'\n** FINAL-only MIDDLEs are MORE likely to be in PP **')
        print(f'   This explains the B survival difference!')
        print(f'   The effect is PP overlap, not a special RI positional function.')
    else:
        print(f'\n   FINAL-only MIDDLEs are NOT more likely to be in PP.')
        print(f'   If B survival still differs, it may be a real positional effect.')
