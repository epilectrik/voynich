"""
LATE PREFIX PROVENANCE CHECK

Are LATE tokens (al, ar, or) inherent to B or enabled via PP/AZC?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import Counter

tx = Transcript()
morph = Morphology()

LATE_PREFIXES = {'al', 'ar', 'or'}

# Collect LATE tokens from A and B
a_late_words = set()
b_late_words = set()
a_late_middles = set()
b_late_middles = set()

for token in tx.currier_a():
    if token.word:
        m = morph.extract(token.word)
        if m.prefix in LATE_PREFIXES:
            a_late_words.add(token.word)
            if m.middle:
                a_late_middles.add(m.middle)

for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        if m.prefix in LATE_PREFIXES:
            b_late_words.add(token.word)
            if m.middle:
                b_late_middles.add(m.middle)

print('=' * 60)
print('LATE PREFIX PROVENANCE CHECK')
print('=' * 60)

print(f'\n=== TOKEN-LEVEL ANALYSIS ===')
print(f'LATE tokens in A: {len(a_late_words)} unique words')
print(f'LATE tokens in B: {len(b_late_words)} unique words')
print(f'')
print(f'Shared (A and B): {len(a_late_words & b_late_words)}')
print(f'A-exclusive: {len(a_late_words - b_late_words)}')
print(f'B-exclusive: {len(b_late_words - a_late_words)}')
print(f'')
print(f'B-exclusive rate: {len(b_late_words - a_late_words) / len(b_late_words) * 100:.1f}%')

print(f'\n=== MIDDLE-LEVEL ANALYSIS ===')
print(f'LATE MIDDLEs in A: {len(a_late_middles)}')
print(f'LATE MIDDLEs in B: {len(b_late_middles)}')
print(f'Shared MIDDLEs: {len(a_late_middles & b_late_middles)}')
print(f'B-exclusive MIDDLEs: {len(b_late_middles - a_late_middles)}')
print(f'A-exclusive MIDDLEs: {len(a_late_middles - b_late_middles)}')
print(f'')
print(f'B-exclusive MIDDLE rate: {len(b_late_middles - a_late_middles) / len(b_late_middles) * 100:.1f}%')

print(f'\n=== SAMPLE B-EXCLUSIVE LATE TOKENS ===')
b_only = sorted(b_late_words - a_late_words)[:15]
for w in b_only:
    m = morph.extract(w)
    print(f'  {w} (MIDDLE: {m.middle})')

print(f'\n=== SAMPLE SHARED LATE TOKENS ===')
shared = sorted(a_late_words & b_late_words)[:15]
for w in shared:
    m = morph.extract(w)
    print(f'  {w} (MIDDLE: {m.middle})')

# Check if shared MIDDLEs are PP (pipeline-participating)
print(f'\n=== PP vs RI CLASSIFICATION ===')

# Get all A MIDDLEs and B MIDDLEs to determine PP status
all_a_middles = set()
all_b_middles = set()

for token in tx.currier_a():
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            all_a_middles.add(m.middle)

for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            all_b_middles.add(m.middle)

pp_middles = all_a_middles & all_b_middles  # Pipeline-participating
ri_middles = all_a_middles - all_b_middles  # Registry-internal

# Check LATE MIDDLEs against PP/RI
late_pp = b_late_middles & pp_middles
late_b_exclusive = b_late_middles - all_a_middles

print(f'Total PP MIDDLEs (A+B shared): {len(pp_middles)}')
print(f'Total RI MIDDLEs (A-exclusive): {len(ri_middles)}')
print(f'')
print(f'LATE MIDDLEs that are PP: {len(late_pp)} ({len(late_pp)/len(b_late_middles)*100:.1f}%)')
print(f'LATE MIDDLEs that are B-exclusive: {len(late_b_exclusive)} ({len(late_b_exclusive)/len(b_late_middles)*100:.1f}%)')

print(f'\n=== INTERPRETATION ===')
if len(b_late_words - a_late_words) / len(b_late_words) > 0.5:
    print('LATE tokens are PREDOMINANTLY B-EXCLUSIVE (>50%)')
    print('-> LATE prefix class is B-internal grammar, not AZC-enabled')
else:
    print('LATE tokens are PREDOMINANTLY SHARED with A')
    print('-> LATE prefix class is pipeline-participating')

if len(late_pp) / len(b_late_middles) > 0.5:
    print(f'\nBut LATE MIDDLEs are {len(late_pp)/len(b_late_middles)*100:.1f}% PP')
    print('-> The MIDDLEs under LATE prefixes come through the pipeline')
    print('-> B applies LATE prefix to PP vocabulary at line-end positions')
