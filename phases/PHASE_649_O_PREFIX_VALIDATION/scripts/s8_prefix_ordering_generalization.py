"""
Phase 649 Step 8: Prefix-pair ordering generalization (Test A).

Crazy-expert's killer test: is qo->ok at 72.9% specific, or is qo a
generic operational opener that precedes ANY o-prefix at ~70-78%?

For each paragraph, identify first-mention position of each prefix.
For each pair (A, B), count paragraphs where both appear; compute
fraction where A comes first.

Predictions (per crazy-expert):
- qo -> {ok, ot, ol, or} all 70-78% (grammatical precedence)
- ok <-> ot near 50/50 (sister pair, no ordering)
- ch <-> sh near 50/50 (sister pair)
- da -> {qo, ok, ot, ol, or} 80%+ (DA = INFRASTRUCTURE, declares context)
- BARE -> qo low (BARE is post-spec execution)

If the prediction holds: C1963 should be reframed as "qo as paragraph
operational opener," linking to C1300/C1316/C1394, not as "qo->ok specific."

If qo->ok stands out vs other qo->o rates: register as specific.
"""
import sys
import json
import math
from collections import defaultdict
sys.path.insert(0, '.')
from scripts.voynich import Transcript

tx = Transcript()

def prefix_of(w):
    if w.startswith('ch'): return 'ch'
    if w.startswith('sh'): return 'sh'
    if w.startswith('qo'): return 'qo'
    if w.startswith('da'): return 'da'
    if len(w) >= 2 and w[0] == 'o' and w[1] in ('k','t','l','r'):
        return 'o' + w[1]
    return None

# Group tokens by paragraph
paragraphs = defaultdict(list)
current_par = {}
for t in tx.currier_b():
    f = t.folio
    if t.par_initial:
        current_par[f] = current_par.get(f, -1) + 1
    par_idx = current_par.get(f, 0)
    paragraphs[(f, par_idx)].append(t)

# For each paragraph, find first-position of each prefix
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'or']
par_firsts = {}
for key, toks in paragraphs.items():
    if len(toks) < 6: continue
    firsts = {}
    for i, t in enumerate(toks):
        p = prefix_of(t.word)
        if p and p not in firsts:
            firsts[p] = i
    par_firsts[key] = firsts

# Pairwise ordering
pairs_to_test = [
    # qo -> all o-prefixes (test crazy-expert's prediction)
    ('qo','ok'), ('qo','ot'), ('qo','ol'), ('qo','or'),
    # Sister pairs (predicted 50/50)
    ('ok','ot'), ('ot','ok'),
    ('ch','sh'), ('sh','ch'),
    # da -> all (predicted 80%+)
    ('da','qo'), ('da','ok'), ('da','ot'), ('da','ol'), ('da','or'),
    # Cross (for completeness)
    ('ch','qo'), ('sh','qo'),
    ('ch','ok'), ('sh','ok'),
    ('ol','ot'), ('ot','ol'),
    ('ol','or'), ('or','ol'),
]

print("="*72)
print("PREFIX-PAIR FIRST-MENTION ORDERING (paragraphs with both prefixes)")
print("="*72)
print(f"\n{'Pair':<12s}  {'n':>4s}  {'A first %':>10s}  {'Verdict'}")
print("-"*60)

results = {}
for a, b in pairs_to_test:
    a_first = 0
    b_first = 0
    for key, firsts in par_firsts.items():
        if a in firsts and b in firsts:
            if firsts[a] < firsts[b]:
                a_first += 1
            elif firsts[b] < firsts[a]:
                b_first += 1
    total = a_first + b_first
    if total < 5:
        print(f"{a}->{b:<8s}  {total:>4d}  --  insufficient")
        continue
    pct = a_first / total
    # Verdict
    if pct >= 0.70:
        verdict = 'STRONG ordering (>=70%)'
    elif pct >= 0.60:
        verdict = 'moderate ordering'
    elif pct >= 0.40:
        verdict = 'no ordering (~50/50)'
    elif pct >= 0.30:
        verdict = 'moderate REVERSE'
    else:
        verdict = 'STRONG REVERSE (<=30%)'
    print(f"{a}->{b:<8s}  {total:>4d}  {pct*100:>9.1f}%  {verdict}")
    results[f'{a}->{b}'] = {'n': total, 'a_first_pct': pct, 'a_first': a_first, 'b_first': b_first}

# Crazy-expert's specific test: are qo->{ok,ot,ol,or} all in same range?
print()
print("="*72)
print("CRAZY-EXPERT'S DISCRIMINATOR")
print("="*72)
print()
print("Question: are qo -> {ok, ot, ol, or} all at 70-78%, or does qo->ok stand out?")
print()
qo_rates = []
for target in ('ok', 'ot', 'ol', 'or'):
    key = f'qo->{target}'
    if key in results:
        r = results[key]
        qo_rates.append((target, r['a_first_pct'], r['n']))
        print(f"  qo -> {target}: {r['a_first_pct']*100:5.1f}%  (n={r['n']})")

if qo_rates:
    rates = [r[1] for r in qo_rates]
    mean_rate = sum(rates) / len(rates)
    spread = max(rates) - min(rates)
    print()
    print(f"Mean qo->o-prefix ordering rate: {mean_rate*100:.1f}%")
    print(f"Spread (max - min): {spread*100:.1f}pp")
    print()
    if spread < 0.10 and mean_rate >= 0.65:
        print("VERDICT: qo->o-prefix ordering is GENERIC (all in same range).")
        print("        qo serves as paragraph opener for o-prefix sequence.")
        print("        C1963 should reframe as grammatical-precedence finding,")
        print("        not qo->ok-specific.")
    elif spread > 0.20:
        print("VERDICT: qo->o-prefix ordering is HIGHLY VARIABLE.")
        print("        Specific pairs may carry distinct meaning.")
    else:
        print("VERDICT: qo->o-prefix ordering is moderately consistent.")
        print(f"        qo->ok (specific): {[r for r in qo_rates if r[0]=='ok'][0][1]*100:.1f}%")
        print(f"        Mean of others: {sum(r[1] for r in qo_rates if r[0] != 'ok')/3*100:.1f}%")

# Save
with open('phases/PHASE_649_O_PREFIX_VALIDATION/results/prefix_ordering_generalization.json', 'w') as f:
    json.dump(results, f, indent=2)
print()
print("Saved: phases/PHASE_649_O_PREFIX_VALIDATION/results/prefix_ordering_generalization.json")
