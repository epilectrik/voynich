"""
Phase 667 s1 — C1964 retest: within-line interleaving

Original claim: 85.3% of prefix transitions occur within-line.
Problem: all-token same-line rate is ~91%, so 85% is BELOW baseline.

Fix: compute random-pair same-line rate as null, compare with prefix
transition same-line rate. If prefix < random, transitions actually
CROSS lines more often than chance — reversing the original claim.
"""
import sys
import io
import json
import math
import random
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from scripts.voynich import Transcript

tx = Transcript()

FIRE = {'ch', 'sh', 'qo'}
VESSEL = {'ok', 'ot', 'ol', 'or'}

def prefix_of(w):
    if w.startswith('ch'): return 'ch'
    if w.startswith('sh'): return 'sh'
    if w.startswith('qo'): return 'qo'
    if len(w) >= 2 and w[0] == 'o' and w[1] in ('k', 't', 'l', 'r'):
        return 'o' + w[1]
    return None

paragraphs = defaultdict(list)
current_par = {}
for t in tx.currier_b():
    f = t.folio
    if t.par_initial:
        current_par[f] = current_par.get(f, -1) + 1
    par_idx = current_par.get(f, 0)
    paragraphs[(f, par_idx)].append(t)

prefix_trans_same = 0
prefix_trans_diff = 0
all_consec_same = 0
all_consec_diff = 0
prefixed_consec_same = 0
prefixed_consec_diff = 0

for (f, par_idx), toks in paragraphs.items():
    if len(toks) < 6:
        continue

    # All consecutive token pairs (for baseline)
    for i in range(1, len(toks)):
        if toks[i].line == toks[i-1].line:
            all_consec_same += 1
        else:
            all_consec_diff += 1

    # Filter to prefixed tokens only
    prefixed = [(prefix_of(t.word), t.line) for t in toks]
    prefixed = [(p, l) for p, l in prefixed if p is not None]

    # Consecutive prefixed token pairs (baseline for prefixed subset)
    for i in range(1, len(prefixed)):
        if prefixed[i][1] == prefixed[i-1][1]:
            prefixed_consec_same += 1
        else:
            prefixed_consec_diff += 1

    # Prefix TRANSITIONS only (where prefix changes)
    for i in range(1, len(prefixed)):
        if prefixed[i][0] != prefixed[i-1][0]:
            if prefixed[i][1] == prefixed[i-1][1]:
                prefix_trans_same += 1
            else:
                prefix_trans_diff += 1

all_total = all_consec_same + all_consec_diff
all_same_rate = all_consec_same / all_total if all_total else 0

prefixed_total = prefixed_consec_same + prefixed_consec_diff
prefixed_same_rate = prefixed_consec_same / prefixed_total if prefixed_total else 0

trans_total = prefix_trans_same + prefix_trans_diff
trans_same_rate = prefix_trans_same / trans_total if trans_total else 0

print('=== C1964 Retest: Within-Line Interleaving ===')
print()
print(f'All consecutive token pairs:')
print(f'  Same line: {all_consec_same:,} / {all_total:,} = {all_same_rate:.3f}')
print()
print(f'Consecutive prefixed-token pairs (all, not just transitions):')
print(f'  Same line: {prefixed_consec_same:,} / {prefixed_total:,} = {prefixed_same_rate:.3f}')
print()
print(f'Prefix TRANSITION pairs (where prefix changes):')
print(f'  Same line: {prefix_trans_same:,} / {trans_total:,} = {trans_same_rate:.3f}')
print()
print(f'Comparison:')
print(f'  All-token baseline same-line rate:     {all_same_rate:.3f}')
print(f'  Prefixed-token baseline same-line rate: {prefixed_same_rate:.3f}')
print(f'  Prefix-transition same-line rate:       {trans_same_rate:.3f}')
print(f'  Transition vs all-token delta:          {trans_same_rate - all_same_rate:+.3f}')
print(f'  Transition vs prefixed-token delta:     {trans_same_rate - prefixed_same_rate:+.3f}')

# Binomial test: is prefix-transition same-line rate significantly different from baseline?
# Use prefixed-token same-line rate as the proper null (same population of tokens)
n = trans_total
k = prefix_trans_same
p0 = prefixed_same_rate

# Normal approximation to binomial
if n > 0 and 0 < p0 < 1:
    z = (k/n - p0) / math.sqrt(p0 * (1 - p0) / n)
    print(f'\n  Binomial z-test vs prefixed baseline: z = {z:+.3f}')
    if z < -1.96:
        print(f'  SIGNIFICANT: transitions cross lines MORE often than random prefixed pairs')
    elif z > 1.96:
        print(f'  SIGNIFICANT: transitions stay within lines MORE often than random')
    else:
        print(f'  NOT SIGNIFICANT: no evidence transitions differ from random')

# Verdict
print('\n=== VERDICT ===')
if trans_same_rate < prefixed_same_rate:
    print(f'Prefix transitions cross lines MORE often than random prefixed pairs.')
    print(f'Original C1964 claim ("85% within-line = interleaving dominance") is REVERSED.')
    print(f'The correct reading: prefix changes are weakly ATTRACTED to line boundaries.')
    verdict = 'REVERSED'
elif trans_same_rate > prefixed_same_rate and n > 0 and z > 1.96:
    print(f'Prefix transitions stay within lines more than baseline.')
    print(f'Original claim direction CONFIRMED with proper null comparison.')
    verdict = 'CONFIRMED'
else:
    print(f'No significant difference from baseline.')
    verdict = 'NULL'

print(f'Verdict: {verdict}')

out = {
    'all_token_same_line_rate': all_same_rate,
    'prefixed_token_same_line_rate': prefixed_same_rate,
    'prefix_transition_same_line_rate': trans_same_rate,
    'delta_vs_all': trans_same_rate - all_same_rate,
    'delta_vs_prefixed': trans_same_rate - prefixed_same_rate,
    'n_transitions': trans_total,
    'z_score': z if n > 0 and 0 < p0 < 1 else None,
    'verdict': verdict,
}

out_dir = REPO_ROOT / 'phases' / 'PHASE_667_RETRACTION_RETESTS' / 'results'
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / 'C1964_RETEST.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print(f'\nWrote results.')
