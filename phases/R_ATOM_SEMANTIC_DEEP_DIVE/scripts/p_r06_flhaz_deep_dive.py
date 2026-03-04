"""P-R6: r-terminal enrichment at FL_HAZ macro-state tokens (deep dive).

If r = "flow/run" (rinnen), then:
- r-terminal should be enriched at FL_HAZ tokens (liquid in hazardous motion)
- r-terminal should be depleted at AXM tokens (thermal, not flow)
- r-terminal should be depleted at CC tokens (control logic, not physical)
- Among FL_HAZ tokens, r+FLOW category should dominate over r+THERMAL

Also: which MIDDLE compounds are r-terminal and appear at FL_HAZ vs AXM?
This reveals the specific vocabulary of hazardous flow.
"""

import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder, CategoryClassifier


def normal_cdf(z):
    if z < -8: return 0.0
    if z > 8: return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1 if z >= 0 else -1
    t = 1.0 / (1.0 + p * abs(z))
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z * z / 2.0)
    return 0.5 * (1.0 + sign * y)


tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()
cc = CategoryClassifier()

# ============================================================
# Build token-level data with macro-state
# ============================================================
print("Building token-level data with macro-state...")

line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

print(f"  Total lines: {len(line_tokens)}")

# ============================================================
# P-R6a: r-terminal fraction BY MACRO-STATE
# ============================================================
print(f"\n{'='*70}")
print("P-R6a: r-TERMINAL FRACTION BY MACRO-STATE")
print(f"{'='*70}")
print("Prediction: FL_HAZ enriched, AXM depleted, CC depleted\n")

state_r = defaultdict(int)
state_total = defaultdict(int)
state_term = defaultdict(lambda: defaultdict(int))

for (folio, line_id), words in line_tokens.items():
    for w in words:
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2:
            continue

        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        if not ms:
            continue

        terminal = mid[-1]
        state_total[ms] += 1
        state_term[ms][terminal] += 1
        if terminal == 'r':
            state_r[ms] += 1

global_r_frac = sum(state_r.values()) / sum(state_total.values()) if sum(state_total.values()) > 0 else 0

print(f"  Global r-terminal rate: {global_r_frac*100:.2f}% (n={sum(state_total.values())})\n")
print(f"  {'State':<12s} {'r-term':>8s} {'total':>8s} {'r%':>8s} {'enrichment':>12s}")
print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8} {'-'*12}")

for state in ['FL_HAZ', 'FL_SAFE', 'AXM', 'AXm', 'FQ', 'CC']:
    rc = state_r.get(state, 0)
    tc = state_total.get(state, 0)
    rate = rc / tc * 100 if tc > 0 else 0
    enrich = (rate / 100) / global_r_frac if global_r_frac > 0 else 0
    marker = ' <-- predicted enriched' if state == 'FL_HAZ' else ''
    print(f"  {state:<12s} {rc:>8d} {tc:>8d} {rate:>7.2f}% {enrich:>11.3f}x{marker}")

# Chi-square: FL_HAZ vs AXM for r-terminal
r_flh = state_r.get('FL_HAZ', 0)
t_flh = state_total.get('FL_HAZ', 0)
r_axm = state_r.get('AXM', 0)
t_axm = state_total.get('AXM', 0)

if t_flh > 0 and t_axm > 0:
    a_val = r_flh
    b_val = t_flh - r_flh
    c_val = r_axm
    d_val = t_axm - r_axm
    n = a_val + b_val + c_val + d_val
    denom = (a_val + b_val) * (c_val + d_val) * (a_val + c_val) * (b_val + d_val)
    if denom > 0:
        chi2 = (n * (a_val * d_val - b_val * c_val) ** 2) / denom
        z_val = math.sqrt(chi2)
        p_val = 2 * (1 - normal_cdf(z_val))
        print(f"\n  FL_HAZ vs AXM: {r_flh/t_flh*100:.2f}% vs {r_axm/t_axm*100:.2f}%")
        print(f"  Chi-square: {chi2:.2f}, p={p_val:.8f}")

# ============================================================
# P-R6b: ALL terminal atoms by macro-state (comprehensive)
# ============================================================
print(f"\n{'='*70}")
print("P-R6b: ALL TERMINAL ATOMS — FL_HAZ/AXM ENRICHMENT RATIO")
print(f"{'='*70}")
print("Which terminals prefer FL_HAZ (hazardous flow) vs AXM (heating)?\n")

print(f"  {'Term':<5s} {'FL_HAZ%':>10s} {'AXM%':>10s} {'ratio':>8s} {'class':>12s}")
print(f"  {'-'*5} {'-'*10} {'-'*10} {'-'*8} {'-'*12}")

term_state_results = []
for term in sorted(set(a for s in state_term for a in state_term[s])):
    flh_total = state_total.get('FL_HAZ', 0)
    axm_total = state_total.get('AXM', 0)
    if flh_total < 10 or axm_total < 10:
        continue

    flh_count = state_term.get('FL_HAZ', {}).get(term, 0)
    axm_count = state_term.get('AXM', {}).get(term, 0)
    total_for_term = sum(state_term[s].get(term, 0) for s in state_term)
    if total_for_term < 50:
        continue

    flh_frac = flh_count / flh_total * 100
    axm_frac = axm_count / axm_total * 100
    ratio = flh_frac / axm_frac if axm_frac > 0 else 999

    # C1386 class
    if term in ('e', 'h', 'k', 't'):
        cls = 'ACTOR'
    elif term in ('d', 'y', 'o', 'i'):
        cls = 'NEUTRAL'
    elif term in ('n', 'l', 'r', 'm'):
        cls = 'RESPONDER'
    else:
        cls = '?'

    term_state_results.append((term, flh_frac, axm_frac, ratio, cls))

term_state_results.sort(key=lambda x: -x[3])
for term, flh_f, axm_f, ratio, cls in term_state_results:
    marker = ' <-- r' if term == 'r' else ' <-- l' if term == 'l' else ''
    print(f"  {term:<5s} {flh_f:>9.2f}% {axm_f:>9.2f}% {ratio:>7.3f}x {cls:>12s}{marker}")

# ============================================================
# P-R6c: r-terminal MIDDLE compounds at FL_HAZ — the hazardous flow vocabulary
# ============================================================
print(f"\n{'='*70}")
print("P-R6c: r-TERMINAL MIDDLE COMPOUNDS AT FL_HAZ")
print(f"{'='*70}")
print("What specific MIDDLEs with r-terminal appear at FL_HAZ?\n")

flh_r_middles = Counter()
nonflh_r_middles = Counter()

for (folio, line_id), words in line_tokens.items():
    for w in words:
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2:
            continue
        if mid[-1] != 'r':
            continue

        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        if ms == 'FL_HAZ':
            flh_r_middles[mid] += 1
        elif ms:
            nonflh_r_middles[mid] += 1

print(f"  r-terminal at FL_HAZ: {sum(flh_r_middles.values())} tokens, {len(flh_r_middles)} types")
print(f"  r-terminal elsewhere: {sum(nonflh_r_middles.values())} tokens\n")

total_flh_r = sum(flh_r_middles.values())
total_other_r = sum(nonflh_r_middles.values())

print(f"  {'MIDDLE':<12s} {'FL_HAZ':>8s} {'other':>8s} {'FL_HAZ%':>10s} {'other%':>10s} {'ratio':>8s}")
print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*10} {'-'*10} {'-'*8}")

mid_results = []
all_r_mids = set(list(flh_r_middles.keys()) + list(nonflh_r_middles.keys()))
for mid in sorted(all_r_mids):
    fc = flh_r_middles.get(mid, 0)
    oc = nonflh_r_middles.get(mid, 0)
    total = fc + oc
    if total < 5:
        continue
    fp = fc / total_flh_r * 100 if total_flh_r > 0 else 0
    op = oc / total_other_r * 100 if total_other_r > 0 else 0
    ratio = fp / op if op > 0 else 999
    mid_results.append((mid, fc, oc, fp, op, ratio))

mid_results.sort(key=lambda x: -x[5])
for mid, fc, oc, fp, op, ratio in mid_results[:20]:
    cat = cc.classify(mid) or '?'
    print(f"  {mid:<12s} {fc:>8d} {oc:>8d} {fp:>9.1f}% {op:>9.1f}% {ratio:>7.2f}x  [{cat}]")

# ============================================================
# P-R6d: r-terminal category profile at FL_HAZ vs AXM
# ============================================================
print(f"\n{'='*70}")
print("P-R6d: CATEGORY PROFILE OF r-TERMINAL TOKENS AT FL_HAZ vs AXM")
print(f"{'='*70}")

r_flh_cats = Counter()
r_axm_cats = Counter()

for (folio, line_id), words in line_tokens.items():
    for w in words:
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2:
            continue
        if mid[-1] != 'r':
            continue

        cat = cc.classify(mid)
        if not cat:
            continue

        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        if ms == 'FL_HAZ':
            r_flh_cats[cat] += 1
        elif ms == 'AXM':
            r_axm_cats[cat] += 1

r_flh_total = sum(r_flh_cats.values())
r_axm_total = sum(r_axm_cats.values())

print(f"\n  r-terminal at FL_HAZ: {r_flh_total} classified tokens")
print(f"  r-terminal at AXM: {r_axm_total} classified tokens\n")

all_cats = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
            'TRANSITION', 'MARKING', 'MONITORING']

print(f"  {'Category':<14s} {'FL_HAZ%':>10s} {'AXM%':>10s} {'ratio':>8s}")
print(f"  {'-'*14} {'-'*10} {'-'*10} {'-'*8}")

for cat in all_cats:
    fp = r_flh_cats[cat] / r_flh_total * 100 if r_flh_total > 0 else 0
    ap = r_axm_cats[cat] / r_axm_total * 100 if r_axm_total > 0 else 0
    ratio = fp / ap if ap > 0 else (999 if fp > 0 else 0)
    marker = ' <-- predicted' if cat == 'FLOW' else ''
    print(f"  {cat:<14s} {fp:>9.1f}% {ap:>9.1f}% {ratio:>7.2f}x{marker}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-R6 SUMMARY")
print(f"{'='*70}")

flh_enrich = (state_r.get('FL_HAZ', 0) / state_total.get('FL_HAZ', 1)) / global_r_frac if global_r_frac > 0 else 0
axm_enrich = (state_r.get('AXM', 0) / state_total.get('AXM', 1)) / global_r_frac if global_r_frac > 0 else 0

print(f"\n  r-terminal FL_HAZ enrichment: {flh_enrich:.3f}x")
print(f"  r-terminal AXM enrichment: {axm_enrich:.3f}x")
print(f"  FL_HAZ/AXM ratio: {flh_enrich/axm_enrich:.3f}x" if axm_enrich > 0 else "  AXM enrichment is zero")

if flh_enrich > 1.5:
    print(f"\n  SUPPORTS: r is enriched at FL_HAZ (hazardous flow)")
elif flh_enrich > 1.0:
    print(f"\n  WEAK SUPPORT: r slightly enriched at FL_HAZ")
else:
    print(f"\n  DOES NOT SUPPORT: r not enriched at FL_HAZ")
