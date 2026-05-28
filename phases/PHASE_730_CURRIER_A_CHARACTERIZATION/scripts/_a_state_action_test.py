"""Currier A State-vs-Action Mapping Test (PRE-REGISTERED).

CASC C1395 T5 claims: A = state-describing terminals, B = action-performing terminals.
- l-terminal 1.84x A-enriched (state)
- dy-terminal 144x B-enriched (action-sealing)
- o-frames 2.5-2.8x A-enriched (arrangement)
- execution frames (edy, aiin, ar, am) B-only

The sharpest test: use PP MIDDLEs (the ~400 shared between A and B). The SAME
lexical item appears in both systems. If A catalogs states and B catalogs actions,
then the same MIDDLE should carry STATE terminals in A-context but ACTION terminals
in B-context.

PRE-REGISTERED HYPOTHESES (locked before running):

S1: dy-SUFFIX ASYMMETRY (the headline C1395 T5 claim)
    For PP MIDDLEs, dy-suffix rate in B-context >> A-context.
    PASS: aggregate dy-rate(B) > 5x dy-rate(A) AND per-MIDDLE majority show B>A

S2: l-TERMINAL ASYMMETRY (state-describing signature)
    For PP MIDDLEs, l-terminal (MIDDLE-internal TERM=l) rate in A > B.
    PASS: aggregate l-rate(A) > l-rate(B), per-MIDDLE majority A>B

S3: PER-MIDDLE CONSISTENCY
    The state/action split should hold WITHIN individual PP MIDDLEs, not just
    aggregate. For PP MIDDLEs appearing >=3x in both A and B:
    PASS: >60% of such MIDDLEs show dy(B) > dy(A)

S4: SUFFIX-MODE SEPARATION
    A-context tokens should be suffix-LIGHT (state = bare description),
    B-context suffix-HEAVY (action = sealed with suffix).
    PASS: mean suffix-presence rate B > A by >10pp

NEGATIVE CONTROL S5:
    Shuffle A/B context labels per MIDDLE, recompute dy-asymmetry.
    PASS: observed asymmetry > p95 of shuffle null

VERDICT:
- S1+S3 PASS = state/action split confirmed at the discriminating per-MIDDLE level
- S1 PASS, S3 FAIL = aggregate effect only (could be composition)
- S1 FAIL = C1395 T5 doesn't replicate
"""
import json
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, 'C:/git/voynich')
random.seed(42); np.random.seed(42)

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# ===== Collect per-MIDDLE suffix + terminal data, split by A/B context =====
# Structure: middle -> {'A': [token info], 'B': [token info]}
middle_data = defaultdict(lambda: {'A': [], 'B': []})


def token_features(w):
    """Return (middle, suffix, term_atom, has_suffix)."""
    try:
        m = morph.extract(w)
    except Exception:
        return None
    if not m.middle:
        return None
    suffix = m.suffix or ''
    # Get MIDDLE-internal terminal atom
    term_atom = None
    try:
        a = morph.atomize(w)
        if hasattr(a, 'atoms') and a.atoms:
            for char, role, _ in a.atoms:
                if role == 'TERM':
                    term_atom = char
    except Exception:
        pass
    return (m.middle, suffix, term_atom, bool(suffix))


for t in tx.currier_a(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    tf = token_features(w)
    if tf:
        middle_data[tf[0]]['A'].append(tf)

for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    tf = token_features(w)
    if tf:
        middle_data[tf[0]]['B'].append(tf)

# PP MIDDLEs = appear in both A and B
pp_middles = [m for m, d in middle_data.items() if d['A'] and d['B']]
print(f'PP MIDDLEs (in both A and B): {len(pp_middles)}')


def dy_rate(tokens):
    if not tokens: return 0
    return sum(1 for tf in tokens if tf[1] in ('dy', 'edy', 'eedy')) / len(tokens)

def l_term_rate(tokens):
    if not tokens: return 0
    return sum(1 for tf in tokens if tf[2] == 'l') / len(tokens)

def suffix_presence(tokens):
    if not tokens: return 0
    return sum(1 for tf in tokens if tf[3]) / len(tokens)


# ===== S1: dy-suffix asymmetry (aggregate) =====
print('\n=== S1: dy-SUFFIX ASYMMETRY ===')
all_a_tokens = [tf for m in pp_middles for tf in middle_data[m]['A']]
all_b_tokens = [tf for m in pp_middles for tf in middle_data[m]['B']]
a_dy = dy_rate(all_a_tokens)
b_dy = dy_rate(all_b_tokens)
print(f'  Aggregate dy-suffix rate: A={a_dy:.4f}, B={b_dy:.4f}')
ratio = b_dy / a_dy if a_dy > 0 else float('inf')
print(f'  B/A ratio: {ratio:.1f}x (CASC claims 144x)')

# Per-MIDDLE direction
per_middle_dy = []
for m in pp_middles:
    da = dy_rate(middle_data[m]['A'])
    db = dy_rate(middle_data[m]['B'])
    per_middle_dy.append((m, da, db))
n_b_higher = sum(1 for _, da, db in per_middle_dy if db > da)
n_a_higher = sum(1 for _, da, db in per_middle_dy if da > db)
n_equal = sum(1 for _, da, db in per_middle_dy if da == db)
print(f'  Per-MIDDLE: B>A for {n_b_higher}, A>B for {n_a_higher}, equal for {n_equal} (of {len(pp_middles)})')
s1_pass = ratio > 5 and n_b_higher > n_a_higher
print(f'  S1 VERDICT: {"PASS" if s1_pass else "FAIL"}')

# ===== S2: l-terminal asymmetry =====
print('\n=== S2: l-TERMINAL ASYMMETRY ===')
a_l = l_term_rate(all_a_tokens)
b_l = l_term_rate(all_b_tokens)
print(f'  Aggregate l-terminal rate: A={a_l:.4f}, B={b_l:.4f}')
l_ratio = a_l / b_l if b_l > 0 else float('inf')
print(f'  A/B ratio: {l_ratio:.2f}x (CASC claims 1.84x)')
per_middle_l = []
for m in pp_middles:
    la = l_term_rate(middle_data[m]['A'])
    lb = l_term_rate(middle_data[m]['B'])
    per_middle_l.append((m, la, lb))
n_a_higher_l = sum(1 for _, la, lb in per_middle_l if la > lb)
n_b_higher_l = sum(1 for _, la, lb in per_middle_l if lb > la)
print(f'  Per-MIDDLE: A>B for {n_a_higher_l}, B>A for {n_b_higher_l}')
s2_pass = a_l > b_l and n_a_higher_l > n_b_higher_l
print(f'  S2 VERDICT: {"PASS" if s2_pass else "FAIL"}')

# ===== S3: per-MIDDLE consistency (MIDDLEs with >=3 occurrences each side) =====
print('\n=== S3: PER-MIDDLE CONSISTENCY ===')
robust_middles = [m for m in pp_middles if len(middle_data[m]['A']) >= 3 and len(middle_data[m]['B']) >= 3]
print(f'  PP MIDDLEs with >=3 occurrences in both A and B: {len(robust_middles)}')
if robust_middles:
    n_consistent = sum(1 for m in robust_middles if dy_rate(middle_data[m]['B']) > dy_rate(middle_data[m]['A']))
    consistency_rate = n_consistent / len(robust_middles)
    print(f'  Show dy(B) > dy(A): {n_consistent}/{len(robust_middles)} = {100*consistency_rate:.1f}%')
    s3_pass = consistency_rate > 0.60
    print(f'  S3 VERDICT: {"PASS" if s3_pass else "FAIL"}')
else:
    s3_pass = False
    print('  Insufficient robust MIDDLEs')

# ===== S4: suffix-mode separation =====
print('\n=== S4: SUFFIX-PRESENCE SEPARATION ===')
a_suff = suffix_presence(all_a_tokens)
b_suff = suffix_presence(all_b_tokens)
print(f'  Suffix-presence rate: A={a_suff:.4f}, B={b_suff:.4f}')
print(f'  B-A gap: {100*(b_suff-a_suff):+.1f}pp')
s4_pass = (b_suff - a_suff) > 0.10
print(f'  S4 VERDICT: {"PASS" if s4_pass else "FAIL"}')

# ===== S5: negative control — shuffle A/B labels =====
print('\n=== S5: NEGATIVE CONTROL (shuffle A/B labels per MIDDLE) ===')
# For robust MIDDLEs, pool A+B tokens, randomly relabel preserving counts, recompute aggregate dy-asymmetry
observed_asymmetry = b_dy - a_dy
shuffle_asymmetries = []
for _ in range(1000):
    shuf_a = []
    shuf_b = []
    for m in pp_middles:
        pooled = middle_data[m]['A'] + middle_data[m]['B']
        n_a = len(middle_data[m]['A'])
        random.shuffle(pooled)
        shuf_a.extend(pooled[:n_a])
        shuf_b.extend(pooled[n_a:])
    shuffle_asymmetries.append(dy_rate(shuf_b) - dy_rate(shuf_a))
shuffle_arr = np.array(shuffle_asymmetries)
p_emp_s5 = (np.abs(shuffle_arr) >= abs(observed_asymmetry)).mean()
print(f'  Observed dy-asymmetry (B-A): {observed_asymmetry:+.4f}')
print(f'  Shuffle null: mean {shuffle_arr.mean():+.4f}, p95 |asym|={np.percentile(np.abs(shuffle_arr), 95):.4f}')
print(f'  p_emp: {p_emp_s5:.4f}')
s5_pass = p_emp_s5 < 0.05
print(f'  S5 VERDICT: {"PASS" if s5_pass else "FAIL"}')

# ===== FINAL =====
print('\n' + '=' * 60)
print('=== STATE-VS-ACTION VERDICT ===')
print('=' * 60)
verdicts = {'S1 dy-asymmetry': s1_pass, 'S2 l-terminal': s2_pass, 'S3 per-MIDDLE consistency': s3_pass, 'S4 suffix-mode': s4_pass, 'S5 negative control': s5_pass}
for k, v in verdicts.items():
    print(f'  {k}: {"PASS" if v else "FAIL"}')
n_pass = sum(verdicts.values())
print(f'\nTotal: {n_pass}/5')

if s1_pass and s3_pass:
    print('\nVERDICT: State/action split CONFIRMED at discriminating per-MIDDLE level.')
    print('Same lexical item treated as state in A, action in B. C1395 T5 validated and sharpened.')
elif s1_pass:
    print('\nVERDICT: Aggregate state/action split holds but per-MIDDLE consistency weak.')
else:
    print('\nVERDICT: State/action split does not replicate cleanly.')

# Show the strongest per-MIDDLE examples
print('\n=== Strongest per-MIDDLE state/action splits (robust MIDDLEs) ===')
examples = []
for m in robust_middles:
    da = dy_rate(middle_data[m]['A'])
    db = dy_rate(middle_data[m]['B'])
    examples.append((m, da, db, db - da, len(middle_data[m]['A']), len(middle_data[m]['B'])))
examples.sort(key=lambda x: -x[3])
print(f'{"MIDDLE":<12} {"dy(A)":>7} {"dy(B)":>7} {"gap":>7} {"nA":>4} {"nB":>5}')
for m, da, db, gap, na, nb in examples[:15]:
    print(f'{m:<12} {da:>7.3f} {db:>7.3f} {gap:>+7.3f} {na:>4} {nb:>5}')
