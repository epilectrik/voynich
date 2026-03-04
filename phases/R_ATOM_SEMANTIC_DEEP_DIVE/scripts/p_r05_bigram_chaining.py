"""P-R5: r-terminal MIDDLEs preferentially follow k-initial over e-initial in bigrams.

If r = "flow/run" (rinnen), then heating (k) triggers liquid motion (flow starts
when heat is applied). Cooling (e) should produce STATIC fluid (equilibrium).
Therefore: k->r bigrams should be enriched over e->r bigrams.

If r = "return/reflux" (Rücklauf), then COOLING triggers condensation and return.
Therefore: e->r should be enriched over k->r. The predictions are OPPOSITE.

Uses C1212 cross-token chaining: TERMINAL(N) -> INITIAL(N+1) within lines.
"""

import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology


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

# ============================================================
# Build per-line token sequences with morphological analysis
# ============================================================
print("Building per-line token sequences...")

line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

print(f"  Total lines: {len(line_tokens)}")

# ============================================================
# P-R5a: INITIAL(N) -> TERMINAL(N+1) bigram analysis
# ============================================================
print(f"\n{'='*70}")
print("P-R5a: CROSS-TOKEN CHAINING -- WHAT INITIAL PRECEDES r-TERMINAL?")
print(f"{'='*70}")
print("C1212: TERMINAL(N) chains to INITIAL(N+1)")
print("Testing: does k-initial -> r-terminal or e-initial -> r-terminal dominate?\n")

# Track bigrams: (initial_of_N, terminal_of_N+1)
init_to_rterm = Counter()  # initial atom of token N, when N+1 is r-terminal
init_to_any_term = Counter()  # initial atom of token N, for any N+1

# Also track: (terminal_of_N, initial_of_N+1)
term_to_rinit = Counter()  # What terminal precedes r (for completeness, r rarely initial)
term_to_any_init = Counter()

# Forward chaining: token N -> token N+1
# Question: what is INITIAL of token N when TERMINAL of N+1 is r?
for line_key, words in line_tokens.items():
    if len(words) < 2:
        continue

    mids = []
    for w in words:
        m = morph.extract(w).middle
        if m and len(m) >= 2:
            mids.append((m[0], m[-1]))  # (initial, terminal)
        else:
            mids.append((None, None))

    for i in range(len(mids) - 1):
        init_n, term_n = mids[i]
        init_n1, term_n1 = mids[i + 1]

        if init_n is None or term_n1 is None:
            continue

        # What initial atom at position N precedes a terminal r at position N+1?
        if term_n1 == 'r':
            init_to_rterm[init_n] += 1
        init_to_any_term[init_n] += 1

        # What terminal at N precedes initial at N+1?
        if term_n is not None and init_n1 is not None:
            if init_n1 == 'r':
                term_to_rinit[term_n] += 1
            term_to_any_init[term_n] += 1

# But actually, the more relevant question is:
# What is TERMINAL of token N when TERMINAL of N+1 is r?
# (Because C1212 chains TERMINAL -> INITIAL, not INITIAL -> TERMINAL)
# Let me also test: what is terminal(N) before r-terminal(N+1)?

term_before_rterm = Counter()
term_before_any = Counter()
init_before_rterm = Counter()
init_before_any = Counter()

for line_key, words in line_tokens.items():
    if len(words) < 2:
        continue

    mids = []
    for w in words:
        m = morph.extract(w).middle
        if m and len(m) >= 2:
            mids.append((m[0], m[-1]))
        else:
            mids.append((None, None))

    for i in range(len(mids) - 1):
        init_n, term_n = mids[i]
        init_n1, term_n1 = mids[i + 1]

        if term_n is not None and term_n1 is not None:
            if term_n1 == 'r':
                term_before_rterm[term_n] += 1
            term_before_any[term_n] += 1

        if init_n is not None and term_n1 is not None:
            if term_n1 == 'r':
                init_before_rterm[init_n] += 1
            init_before_any[init_n] += 1

# Report: TERMINAL(N) before r-terminal(N+1) -- enrichment
r_term_total = sum(term_before_rterm.values())
global_r_rate = r_term_total / sum(term_before_any.values()) if sum(term_before_any.values()) > 0 else 0

print(f"  Global r-terminal N+1 rate: {global_r_rate*100:.2f}%\n")
print(f"  {'Term(N)':<8s} {'before-r':>10s} {'total':>8s} {'r-rate':>10s} {'enrichment':>12s}")
print(f"  {'-'*8} {'-'*10} {'-'*8} {'-'*10} {'-'*12}")

term_results = []
for term in sorted(term_before_any.keys()):
    rc = term_before_rterm.get(term, 0)
    tc = term_before_any[term]
    if tc < 50:
        continue
    rate = rc / tc if tc > 0 else 0
    enrich = rate / global_r_rate if global_r_rate > 0 else 0
    term_results.append((term, rc, tc, rate, enrich))

term_results.sort(key=lambda x: -x[4])
for term, rc, tc, rate, enrich in term_results:
    marker = ''
    if term == 'k':
        marker = ' <-- HEAT'
    elif term == 'e':
        marker = ' <-- COOL'
    elif term == 'h':
        marker = ' <-- WATCH'
    print(f"  {term:<8s} {rc:>10d} {tc:>8d} {rate*100:>9.2f}% {enrich:>11.3f}x{marker}")

# Key comparison: k vs e
k_rate = term_before_rterm.get('k', 0) / term_before_any.get('k', 1)
e_rate = term_before_rterm.get('e', 0) / term_before_any.get('e', 1)
print(f"\n  k-terminal -> r-terminal rate: {k_rate*100:.2f}%")
print(f"  e-terminal -> r-terminal rate: {e_rate*100:.2f}%")
if k_rate > e_rate:
    print(f"  k->r > e->r by {(k_rate - e_rate)*100:.2f}pp -- SUPPORTS 'flow' (heat triggers flow)")
else:
    print(f"  e->r > k->r by {(e_rate - k_rate)*100:.2f}pp -- SUPPORTS 'return' (cooling triggers return)")

# ============================================================
# P-R5b: INITIAL(N) before r-terminal(N+1) -- enrichment
# ============================================================
print(f"\n{'='*70}")
print("P-R5b: INITIAL(N) ATOM BEFORE r-TERMINAL(N+1)")
print(f"{'='*70}")
print("What initial atom in the PRECEDING token precedes r-terminal?\n")

r_init_total = sum(init_before_rterm.values())
global_r_init_rate = r_init_total / sum(init_before_any.values()) if sum(init_before_any.values()) > 0 else 0

print(f"  {'Init(N)':<8s} {'before-r':>10s} {'total':>8s} {'r-rate':>10s} {'enrichment':>12s}")
print(f"  {'-'*8} {'-'*10} {'-'*8} {'-'*10} {'-'*12}")

init_results = []
for init in sorted(init_before_any.keys()):
    rc = init_before_rterm.get(init, 0)
    tc = init_before_any[init]
    if tc < 50:
        continue
    rate = rc / tc if tc > 0 else 0
    enrich = rate / global_r_init_rate if global_r_init_rate > 0 else 0
    init_results.append((init, rc, tc, rate, enrich))

init_results.sort(key=lambda x: -x[4])
for init, rc, tc, rate, enrich in init_results:
    marker = ''
    if init == 'k':
        marker = ' <-- HEAT'
    elif init == 'e':
        marker = ' <-- COOL'
    print(f"  {init:<8s} {rc:>10d} {tc:>8d} {rate*100:>9.2f}% {enrich:>11.3f}x{marker}")

# ============================================================
# P-R5c: COMPREHENSIVE ATOM PAIR ANALYSIS
# ============================================================
print(f"\n{'='*70}")
print("P-R5c: TERMINAL(N) -> TERMINAL(N+1) FULL MATRIX -- r COLUMN")
print(f"{'='*70}")
print("For EACH terminal atom at N, what fraction of N+1 terminals are r?\n")

# Also: for each terminal atom at N+1, what fraction of N terminals preceded it?
# This gives us the FULL chaining landscape for r

# Forward: after terminal X, what fraction are r-terminal?
# Already computed above. Just need to also do:
# Backward: before r-terminal, what is the distribution of preceding terminals?

if r_term_total > 0:
    print(f"  Distribution of TERMINAL(N) before r-terminal(N+1) (n={r_term_total}):\n")
    print(f"  {'Term(N)':<8s} {'count':>8s} {'%':>8s}")
    print(f"  {'-'*8} {'-'*8} {'-'*8}")

    dist_results = []
    for term in sorted(term_before_rterm.keys()):
        cnt = term_before_rterm[term]
        pct = cnt / r_term_total * 100
        dist_results.append((term, cnt, pct))

    dist_results.sort(key=lambda x: -x[1])
    for term, cnt, pct in dist_results:
        marker = ' <-- HEAT' if term == 'k' else ' <-- COOL' if term == 'e' else ''
        print(f"  {term:<8s} {cnt:>8d} {pct:>7.1f}%{marker}")

# ============================================================
# P-R5d: r-TERMINAL -> WHAT FOLLOWS? (INITIAL of N+1 after r-terminal N)
# ============================================================
print(f"\n{'='*70}")
print("P-R5d: AFTER r-TERMINAL(N), WHAT IS INITIAL(N+1)?")
print(f"{'='*70}")

init_after_r = Counter()
init_after_any = Counter()

for line_key, words in line_tokens.items():
    if len(words) < 2:
        continue

    mids = []
    for w in words:
        m = morph.extract(w).middle
        if m and len(m) >= 2:
            mids.append((m[0], m[-1]))
        else:
            mids.append((None, None))

    for i in range(len(mids) - 1):
        init_n, term_n = mids[i]
        init_n1, term_n1 = mids[i + 1]

        if term_n is not None and init_n1 is not None:
            if term_n == 'r':
                init_after_r[init_n1] += 1
            init_after_any[init_n1] += 1

r_fwd_total = sum(init_after_r.values())
global_fwd_rate = r_fwd_total / sum(init_after_any.values()) if sum(init_after_any.values()) > 0 else 0

print(f"\n  {'Init(N+1)':<10s} {'after-r':>10s} {'total':>8s} {'r-rate':>10s} {'enrichment':>12s}")
print(f"  {'-'*10} {'-'*10} {'-'*8} {'-'*10} {'-'*12}")

fwd_results = []
for init in sorted(init_after_any.keys()):
    rc = init_after_r.get(init, 0)
    tc = init_after_any[init]
    if tc < 50:
        continue
    rate = rc / tc if tc > 0 else 0
    enrich = rate / global_fwd_rate if global_fwd_rate > 0 else 0
    fwd_results.append((init, rc, tc, rate, enrich))

fwd_results.sort(key=lambda x: -x[4])
for init, rc, tc, rate, enrich in fwd_results:
    marker = ''
    if init == 'k':
        marker = ' <-- HEAT follows flow?'
    elif init == 'e':
        marker = ' <-- COOL follows flow?'
    elif init == 'n':
        marker = ' <-- SEAL follows flow?'
    elif init == 'a':
        marker = ' <-- COLLECT follows flow?'
    print(f"  {init:<10s} {rc:>10d} {tc:>8d} {rate*100:>9.2f}% {enrich:>11.3f}x{marker}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-R5 SUMMARY")
print(f"{'='*70}")
print("\nKey question: k->r or e->r?")
print("If k->r enriched: SUPPORTS 'flow' (heat triggers liquid motion)")
print("If e->r enriched: SUPPORTS 'return' (cooling triggers condensate return)")
print(f"\n  k-term before r-term: {k_rate*100:.2f}%")
print(f"  e-term before r-term: {e_rate*100:.2f}%")
print(f"  Ratio k/e: {k_rate/e_rate:.3f}x" if e_rate > 0 else "  e-rate is zero")
