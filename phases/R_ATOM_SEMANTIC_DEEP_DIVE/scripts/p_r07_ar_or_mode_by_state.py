"""P-R7: ar suffix mode should be Mode A (specification), or should be Mode B.

If r = "reifen" (ripen/mature):
- ar = "material ripe for collection" -> emergency specification -> Mode A
- or = "vessel cycle complete" -> routine continuation -> Mode B

NOTE: P-R1 already showed ar=27.4% Mode A, or=26.6% Mode A (nearly identical).
This test re-examines with additional granularity: per-state mode profiles.
"""

import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder


tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# ============================================================
# Build per-line data with suffix mode
# ============================================================
print("Building per-line data...")

b_folios = sorted(set(t.folio for t in tx.currier_b()))

line_mode = {}
for folio in b_folios:
    try:
        lines = decoder.analyze_folio_lines(folio)
        for la in lines:
            if la.suffix_mode in ('A', 'B'):
                line_mode[(folio, la.line_id)] = la.suffix_mode
    except Exception:
        pass

line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

print(f"  Lines with mode: {len(line_mode)}")

# ============================================================
# P-R7a: ar vs or suffix mode (re-examining P-R1)
# ============================================================
print(f"\n{'='*70}")
print("P-R7a: ar vs or SUFFIX MODE PROFILES")
print(f"{'='*70}")
print("Prediction: ar Mode A > 55%, or Mode B > 60%")
print("P-R1 showed: ar=27.4% Mode A, or=26.6% -- nearly identical\n")

mid_mode = defaultdict(lambda: {'A': 0, 'B': 0})

for (folio, line_id), words in line_tokens.items():
    mode = line_mode.get((folio, line_id))
    if not mode:
        continue
    for w in words:
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2 or mid[-1] != 'r':
            continue
        mid_mode[mid][mode] += 1

print(f"  {'MIDDLE':<8s} {'Mode A':>8s} {'Mode B':>8s} {'total':>8s} {'%A':>8s}")
print(f"  {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

for mid in sorted(mid_mode.keys()):
    d = mid_mode[mid]
    total = d['A'] + d['B']
    if total < 10:
        continue
    pct = d['A'] / total * 100
    print(f"  {mid:<8s} {d['A']:>8d} {d['B']:>8d} {total:>8d} {pct:>7.1f}%")

# ============================================================
# P-R7b: ar vs or mode BY MACRO-STATE
# ============================================================
print(f"\n{'='*70}")
print("P-R7b: ar vs or SUFFIX MODE BY MACRO-STATE")
print(f"{'='*70}")

mid_state_mode = defaultdict(lambda: defaultdict(lambda: {'A': 0, 'B': 0}))

for (folio, line_id), words in line_tokens.items():
    mode = line_mode.get((folio, line_id))
    if not mode:
        continue
    for w in words:
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2 or mid[-1] != 'r':
            continue
        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        if ms:
            mid_state_mode[mid][ms][mode] += 1

for mid in ['ar', 'or']:
    print(f"\n  {mid}:")
    print(f"    {'State':<12s} {'A':>6s} {'B':>6s} {'total':>6s} {'%A':>8s}")
    print(f"    {'-'*12} {'-'*6} {'-'*6} {'-'*6} {'-'*8}")
    for state in ['FL_HAZ', 'FL_SAFE', 'AXM', 'AXm', 'FQ', 'CC']:
        d = mid_state_mode[mid][state]
        total = d['A'] + d['B']
        if total == 0:
            continue
        pct = d['A'] / total * 100
        print(f"    {state:<12s} {d['A']:>6d} {d['B']:>6d} {total:>6d} {pct:>7.1f}%")

# ============================================================
# P-R7c: ar vs or -- are they functionally different tokens?
# ============================================================
print(f"\n{'='*70}")
print("P-R7c: FULL ar vs or COMPARISON")
print(f"{'='*70}")

ar_states = Counter()
or_states = Counter()

for (folio, line_id), words in line_tokens.items():
    for w in words:
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2 or mid[-1] != 'r':
            continue
        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        if ms:
            if mid == 'ar':
                ar_states[ms] += 1
            elif mid == 'or':
                or_states[ms] += 1

ar_total = sum(ar_states.values())
or_total = sum(or_states.values())

print(f"\n  ar tokens: {ar_total}, or tokens: {or_total}")
print(f"\n  {'State':<12s} {'ar%':>8s} {'or%':>8s} {'delta':>8s}")
print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8}")

for state in ['FL_HAZ', 'FL_SAFE', 'AXM', 'AXm', 'FQ', 'CC']:
    ar_pct = ar_states.get(state, 0) / ar_total * 100 if ar_total > 0 else 0
    or_pct = or_states.get(state, 0) / or_total * 100 if or_total > 0 else 0
    delta = ar_pct - or_pct
    print(f"  {state:<12s} {ar_pct:>7.1f}% {or_pct:>7.1f}% {delta:>+7.1f}pp")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-R7 SUMMARY")
print(f"{'='*70}")

ar_d = mid_mode.get('ar', {'A': 0, 'B': 0})
or_d = mid_mode.get('or', {'A': 0, 'B': 0})
ar_t = ar_d['A'] + ar_d['B']
or_t = or_d['A'] + or_d['B']

if ar_t > 0 and or_t > 0:
    ar_pct_a = ar_d['A'] / ar_t * 100
    or_pct_a = or_d['A'] / or_t * 100
    print(f"\n  ar Mode A: {ar_pct_a:.1f}% (n={ar_t})")
    print(f"  or Mode A: {or_pct_a:.1f}% (n={or_t})")
    print(f"  Delta: {ar_pct_a - or_pct_a:+.1f}pp")

    if ar_pct_a > 55:
        print(f"\n  SUPPORTS: ar Mode A > 55%")
    elif ar_pct_a > or_pct_a + 5:
        print(f"\n  PARTIAL: ar leans more Mode A than or")
    else:
        print(f"\n  DOES NOT SUPPORT: ar and or similar mode profiles")

    # But the state distribution IS different:
    if ar_states.get('FL_HAZ', 0) > 0 and or_states.get('FL_HAZ', 0) == 0:
        print(f"  BUT: ar and or have COMPLETELY DIFFERENT state profiles")
        print(f"  ar at FL_HAZ: {ar_states.get('FL_HAZ', 0)} ({ar_states.get('FL_HAZ', 0)/ar_total*100:.1f}%)")
        print(f"  or at FL_HAZ: {or_states.get('FL_HAZ', 0)}")
