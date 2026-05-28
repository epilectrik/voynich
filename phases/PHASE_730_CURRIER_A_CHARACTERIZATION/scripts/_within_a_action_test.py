"""Within-A action-form discriminating test (load-bearing for Finding 1).

PRE-REGISTERED (locked before running, see file docstring history):

H1: >=20% of dy-eligible MIDDLEs (>=10 B occurrences AND >=20% B dy-rate)
    appear in dy-form (>=1 instance) somewhere in A.
H2: Of dy-eligible MIDDLEs with >=5 dy-form occurrences in A: dy-rate varies
    significantly by line-position-within-paragraph (chi-square, alpha=0.05).

VERDICTS:
- Both pass    -> real operational deployment variable -> REGISTER Tier 2
- H1 < 5%      -> architecturally mandated -> F1 COLLAPSES into C234+C1395+C239
- H1 5-20%     -> AMBIGUOUS, hold
- H1 pass, H2 fail -> A has action-form but not positionally deployed; HOLD
"""
import sys
from collections import defaultdict, Counter

import numpy as np
from scipy.stats import chi2_contingency

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

tx = Transcript(); morph = Morphology()

# ===== Step 1: dy-eligible MIDDLEs from B =====
b_mid_total = Counter(); b_mid_dy = Counter()
for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    try: m = morph.extract(w)
    except Exception: continue
    if not m.middle: continue
    b_mid_total[m.middle] += 1
    if m.suffix == 'dy':
        b_mid_dy[m.middle] += 1

dy_eligible = []
for mid, tot in b_mid_total.items():
    if tot >= 10 and b_mid_dy[mid] / tot >= 0.20:
        dy_eligible.append(mid)

print(f'Dy-eligible MIDDLEs (>=10 B occ, >=20% B dy-rate): {len(dy_eligible)}')

# ===== Step 2: scan A tokens, compute line-index-within-paragraph =====
a_tokens = list(tx.currier_a(exclude_labels=True, exclude_uncertain=True))
print(f'A tokens (H-track, no labels/uncertain): {len(a_tokens)}')

# Compute line_in_par per token: reset to 1 at par_initial, increment at line_initial
records = []  # (mid, has_dy, line_in_par, folio)
line_in_par = 0
prev_line = None
prev_folio = None
prev_par_initial = False
cur_line_in_par = 1
for t in a_tokens:
    w = t.word.strip()
    if not w: continue
    # increment line_in_par when entering a new line
    if t.par_initial:
        cur_line_in_par = 1
    elif t.line_initial:
        cur_line_in_par += 1
    # (otherwise stays same — multiple tokens on a line)
    try: m = morph.extract(w)
    except Exception: continue
    if not m.middle: continue
    has_dy = (m.suffix == 'dy')
    records.append((m.middle, has_dy, cur_line_in_par, t.folio))

print(f'A records with extractable MIDDLE: {len(records)}')

# Sanity: how many dy-form tokens in A overall?
total_a_dy = sum(1 for r in records if r[1])
print(f'Total dy-form tokens in A: {total_a_dy} / {len(records)} ({total_a_dy/len(records):.2%})')

# ===== Step 3: H1 — % of dy-eligible MIDDLEs with >=1 dy-form in A =====
a_mid_dy_count = Counter()
a_mid_total = Counter()
for mid, has_dy, lip, folio in records:
    a_mid_total[mid] += 1
    if has_dy:
        a_mid_dy_count[mid] += 1

eligible_with_a_dy = [mid for mid in dy_eligible if a_mid_dy_count[mid] >= 1]
n_eligible = len(dy_eligible)
n_with_a_dy = len(eligible_with_a_dy)
pct_with_a_dy = n_with_a_dy / n_eligible * 100

# Also report: dy-eligible MIDDLEs that even appear in A (denominator question)
eligible_in_a = [mid for mid in dy_eligible if a_mid_total[mid] >= 1]
print(f'\n=== H1 ===')
print(f'Dy-eligible MIDDLEs: {n_eligible}')
print(f'Of those, appear at all in A (any form): {len(eligible_in_a)}')
print(f'Of those, appear in dy-form in A (>=1): {n_with_a_dy}')
print(f'H1 numerator: {n_with_a_dy} / {n_eligible} = {pct_with_a_dy:.1f}%')
if len(eligible_in_a) > 0:
    pct_conditional = n_with_a_dy / len(eligible_in_a) * 100
    print(f'Conditional (of those present in A): {n_with_a_dy} / {len(eligible_in_a)} = {pct_conditional:.1f}%')

if pct_with_a_dy >= 20:
    h1_verdict = 'PASS'
elif pct_with_a_dy < 5:
    h1_verdict = 'COLLAPSE'
else:
    h1_verdict = 'AMBIGUOUS'
print(f'H1 VERDICT: {h1_verdict}')

# Show details for MIDDLEs with A dy-form
print(f'\n  Dy-eligible MIDDLEs with A dy-form (sorted by A dy-count):')
details = [(mid, a_mid_dy_count[mid], a_mid_total[mid]) for mid in eligible_with_a_dy]
details.sort(key=lambda x: -x[1])
for mid, dy, tot in details[:20]:
    rate_a = dy / tot if tot else 0
    rate_b = b_mid_dy[mid] / b_mid_total[mid]
    print(f'    {mid:>8}  A_dy={dy:>3} / A_tot={tot:>4}  A_rate={rate_a:.2%}  B_rate={rate_b:.2%}')

# ===== Step 4: H2 — positional deployment (line-in-par chi-square) =====
print(f'\n=== H2 ===')
# Pool dy-eligible MIDDLEs with >=5 A dy-form occurrences (need stat power)
h2_candidates = [mid for mid in dy_eligible if a_mid_dy_count[mid] >= 5]
print(f'MIDDLEs with >=5 A dy-form occurrences for positional test: {len(h2_candidates)}')

if not h2_candidates:
    print('Insufficient dy-form occurrences in A for H2 chi-square')
    h2_verdict = 'INSUFFICIENT'
else:
    # Build 2x2 contingency: position (line_in_par == 1 vs > 1) x form (dy vs non-dy)
    # Pool across all H2 candidate MIDDLEs
    pos_dy = 0; pos_nondy = 0     # line 1
    bod_dy = 0; bod_nondy = 0     # line 2+
    for mid, has_dy, lip, folio in records:
        if mid not in h2_candidates: continue
        is_line_1 = (lip == 1)
        if is_line_1:
            if has_dy: pos_dy += 1
            else: pos_nondy += 1
        else:
            if has_dy: bod_dy += 1
            else: bod_nondy += 1
    contingency = [[pos_dy, pos_nondy], [bod_dy, bod_nondy]]
    chi2, p, dof, _ = chi2_contingency(contingency)
    print(f'  Line 1 of paragraph: dy={pos_dy}, non-dy={pos_nondy}  rate={pos_dy/(pos_dy+pos_nondy):.2%}' if pos_dy+pos_nondy else 'line1: 0')
    print(f'  Line 2+ of paragraph: dy={bod_dy}, non-dy={bod_nondy}  rate={bod_dy/(bod_dy+bod_nondy):.2%}' if bod_dy+bod_nondy else 'lineN: 0')
    print(f'  Chi-square: chi2={chi2:.2f}, p={p:.4f}, dof={dof}')
    h2_verdict = 'PASS' if p < 0.05 else 'FAIL'
print(f'H2 VERDICT: {h2_verdict}')

# Also: per-MIDDLE positional check for the strongest candidates
print(f'\n  Per-MIDDLE positional dy-rate (top 10 by A dy-count):')
print(f'  {"MIDDLE":>8} {"line1_dy":>9} {"line1_tot":>10} {"line1_rt":>9} {"lineN_dy":>9} {"lineN_tot":>10} {"lineN_rt":>9}')
top10 = sorted(h2_candidates, key=lambda m: -a_mid_dy_count[m])[:10]
for mid in top10:
    l1_dy = l1_tot = lN_dy = lN_tot = 0
    for r_mid, has_dy, lip, _ in records:
        if r_mid != mid: continue
        if lip == 1:
            l1_tot += 1
            if has_dy: l1_dy += 1
        else:
            lN_tot += 1
            if has_dy: lN_dy += 1
    l1_rt = l1_dy/l1_tot if l1_tot else 0
    lN_rt = lN_dy/lN_tot if lN_tot else 0
    print(f'  {mid:>8} {l1_dy:>9} {l1_tot:>10} {l1_rt:>9.2%} {lN_dy:>9} {lN_tot:>10} {lN_rt:>9.2%}')

# ===== Final verdict =====
print('\n' + '=' * 60)
print('=== FINAL VERDICT ===')
print('=' * 60)
print(f'H1 ({pct_with_a_dy:.1f}% dy-eligible with A dy-form): {h1_verdict}')
print(f'H2 (positional deployment): {h2_verdict}')

if h1_verdict == 'PASS' and h2_verdict == 'PASS':
    print('\n>>> Finding 1 SUPPORTED as real operational deployment variable. <<<')
    print('    A internally uses dy-form for the same MIDDLEs when grammar allows.')
    print('    State vs action is a deployment choice, not architectural exclusion.')
    print('    -> Register as Tier 2 constraint.')
elif h1_verdict == 'COLLAPSE':
    print('\n>>> Finding 1 COLLAPSES into existing constraints. <<<')
    print('    A grammar architecturally excludes dy-suffix; 95% state-form is tautological.')
    print('    -> Already covered by C234+C1395+C239.')
else:
    print('\n>>> Finding 1 AMBIGUOUS. <<<')
    print('    Hold from registration; need further investigation.')
