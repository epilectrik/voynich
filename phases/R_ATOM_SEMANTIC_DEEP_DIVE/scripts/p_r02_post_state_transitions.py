"""P-R2: r-terminal MIDDLEs enriched AFTER FL state advances.

If r = "return/reflux", then r-terminal tokens should appear preferentially
in positions following a macro-state transition (material state changed,
condensate returns). This extends C1386 but tests specifically whether
r's RESPONDER signal holds when measured via FL/macro-state advances
rather than just any state change.

Test: For each token at position i>0, check if the preceding token had
a different macro_state. Compute r-terminal enrichment at post-transition
positions. Also test: does r appear after SPECIFIC state transitions
(e.g., AXM->FL_SAFE = heating->cooling = when condensate would return)?
"""

import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder


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

# ============================================================
# Build per-line token sequences with macro-state
# ============================================================
print("Building per-line sequences...")

line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

print(f"  Total lines: {len(line_tokens)}")

# ============================================================
# Test 1: r-terminal enrichment after ANY macro-state transition
# ============================================================
print(f"\n{'='*70}")
print("TEST 1: r-TERMINAL ENRICHMENT AFTER MACRO-STATE TRANSITIONS")
print(f"{'='*70}")
print("Already know from C1386: r=72.6% post-change")
print("Now: is this r-SPECIFIC or do all iteration-axis atoms behave this way?\n")

# Per terminal atom: post-change rate
term_after = defaultdict(lambda: {'after_change': 0, 'after_same': 0})

for (folio, line_id), words in line_tokens.items():
    if len(words) < 4:
        continue
    seq = []
    for w in words:
        mid = morph.extract(w).middle
        if not mid:
            seq.append((None, None))
            continue
        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        terminal = mid[-1] if len(mid) >= 2 else None
        seq.append((terminal, ms))

    for i in range(1, len(seq)):
        curr_term, curr_ms = seq[i]
        prev_term, prev_ms = seq[i-1]
        if not curr_term or not curr_ms or not prev_ms:
            continue
        if prev_ms != curr_ms:
            term_after[curr_term]['after_change'] += 1
        else:
            term_after[curr_term]['after_same'] += 1

print(f"  {'Term':<5s} {'post-chg%':>10s} {'post-chg':>10s} {'total':>8s} {'cluster':>12s}")
print(f"  {'-'*5} {'-'*10} {'-'*10} {'-'*8} {'-'*12}")

iter_atoms = {'a', 'i', 'n', 'r'}
results = []
for term in sorted(term_after.keys()):
    d = term_after[term]
    total = d['after_change'] + d['after_same']
    if total < 100:
        continue
    rate = d['after_change'] / total * 100
    cluster = 'ITERATION' if term in iter_atoms else ''
    results.append((term, rate, d['after_change'], total, cluster))

results.sort(key=lambda x: -x[1])
for term, rate, ac, total, cluster in results:
    marker = ' <-- r' if term == 'r' else ''
    print(f"  {term:<5s} {rate:>9.1f}% {ac:>10d} {total:>8d} {cluster:>12s}{marker}")

# Compare iteration-axis atoms vs non-iteration
iter_rates = [r for t, r, _, _, c in results if c == 'ITERATION']
noniter_rates = [r for t, r, _, _, c in results if c != 'ITERATION' and t not in iter_atoms]
if iter_rates and noniter_rates:
    iter_mean = sum(iter_rates) / len(iter_rates)
    noniter_mean = sum(noniter_rates) / len(noniter_rates)
    print(f"\n  Iteration-axis mean: {iter_mean:.1f}%")
    print(f"  Non-iteration mean: {noniter_mean:.1f}%")

# ============================================================
# Test 2: r-terminal after SPECIFIC state transitions
# ============================================================
print(f"\n{'='*70}")
print("TEST 2: r-TERMINAL AFTER SPECIFIC STATE TRANSITIONS")
print(f"{'='*70}")
print("Which transitions does r preferentially follow?")
print("If r=return/reflux: enriched after AXM->FL_SAFE (heating->cooling)\n")

# For each transition type (prev->curr), compute r-terminal rate
transition_r = defaultdict(lambda: {'r_term': 0, 'non_r': 0})

for (folio, line_id), words in line_tokens.items():
    if len(words) < 4:
        continue
    seq = []
    for w in words:
        mid = morph.extract(w).middle
        if not mid:
            seq.append((None, None))
            continue
        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        terminal = mid[-1] if len(mid) >= 2 else None
        seq.append((terminal, ms))

    for i in range(1, len(seq)):
        curr_term, curr_ms = seq[i]
        prev_term, prev_ms = seq[i-1]
        if not curr_term or not curr_ms or not prev_ms:
            continue
        if prev_ms != curr_ms:
            trans_key = f"{prev_ms}->{curr_ms}"
            if curr_term == 'r':
                transition_r[trans_key]['r_term'] += 1
            else:
                transition_r[trans_key]['non_r'] += 1

# Report r-terminal rate by transition type
print(f"  {'Transition':<25s} {'r-term':>8s} {'non-r':>8s} {'total':>8s} {'r%':>8s}")
print(f"  {'-'*25} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

trans_results = []
for trans, d in transition_r.items():
    total = d['r_term'] + d['non_r']
    if total < 20:
        continue
    r_pct = d['r_term'] / total * 100
    trans_results.append((trans, d['r_term'], d['non_r'], total, r_pct))

# Global r-terminal rate for baseline
global_r = sum(d['r_term'] for d in transition_r.values())
global_total = sum(d['r_term'] + d['non_r'] for d in transition_r.values())
global_r_pct = global_r / global_total * 100 if global_total > 0 else 0

trans_results.sort(key=lambda x: -x[4])
for trans, rt, nrt, total, r_pct in trans_results:
    enrich = r_pct / global_r_pct if global_r_pct > 0 else 0
    marker = ' <-- predicted' if 'AXM' in trans and 'FL_SAFE' in trans else ''
    print(f"  {trans:<25s} {rt:>8d} {nrt:>8d} {total:>8d} {r_pct:>7.1f}% ({enrich:.2f}x){marker}")

print(f"\n  Global r-terminal rate at transitions: {global_r_pct:.1f}%")

# ============================================================
# Test 3: r-terminal after state change vs SAME state
# ============================================================
print(f"\n{'='*70}")
print("TEST 3: WHAT STATE IS r IN WHEN IT APPEARS POST-CHANGE?")
print(f"{'='*70}")
print("If r=return, it should preferentially appear in FL states (material returning)\n")

r_dest_state = Counter()
nonr_dest_state = Counter()

for (folio, line_id), words in line_tokens.items():
    if len(words) < 4:
        continue
    seq = []
    for w in words:
        mid = morph.extract(w).middle
        if not mid:
            seq.append((None, None))
            continue
        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        terminal = mid[-1] if len(mid) >= 2 else None
        seq.append((terminal, ms))

    for i in range(1, len(seq)):
        curr_term, curr_ms = seq[i]
        prev_term, prev_ms = seq[i-1]
        if not curr_term or not curr_ms or not prev_ms:
            continue
        if prev_ms != curr_ms:
            if curr_term == 'r':
                r_dest_state[curr_ms] += 1
            else:
                nonr_dest_state[curr_ms] += 1

r_total = sum(r_dest_state.values())
nr_total = sum(nonr_dest_state.values())

print(f"  {'Dest state':<12s} {'r%':>8s} {'non-r%':>8s} {'r/non-r':>10s}")
print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*10}")

for state in ['FL_SAFE', 'FL_HAZ', 'AXM', 'AXm', 'FQ', 'CC']:
    r_pct = r_dest_state.get(state, 0) / r_total * 100 if r_total > 0 else 0
    nr_pct = nonr_dest_state.get(state, 0) / nr_total * 100 if nr_total > 0 else 0
    ratio = (r_pct / nr_pct) if nr_pct > 0 else 0
    marker = ' <-- predicted' if state in ('FL_SAFE', 'FL_HAZ') else ''
    print(f"  {state:<12s} {r_pct:>7.1f}% {nr_pct:>7.1f}% {ratio:>9.2f}x{marker}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-R2 SUMMARY")
print(f"{'='*70}")

r_rate = next((r for t, r, _, _, _ in results if t == 'r'), None)
baseline = sum(r for _, r, _, _, _ in results) / len(results) if results else 0

print(f"\n  r-terminal post-change rate: {r_rate:.1f}%")
print(f"  Mean across all atoms: {baseline:.1f}%")
print(f"  r above baseline: {r_rate - baseline:+.1f}pp")

# Check if r is enriched after AXM->FL transitions specifically
axm_fl_trans = [t for t in trans_results if 'AXM' in t[0] and 'FL' in t[0]]
if axm_fl_trans:
    for trans, rt, nrt, total, r_pct in axm_fl_trans:
        print(f"\n  {trans}: r-terminal rate = {r_pct:.1f}% (vs {global_r_pct:.1f}% global)")
