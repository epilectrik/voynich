"""P-L15: l-terminal compounds appear in CHECK positions, not DRIVE positions.

If l = "state/condition marker" (converts operation to status reading), then:

1. l-terminal tokens should disproportionately appear in NON-OPENER positions
   (C959: line opener determines line character = drives the line).
   Status readings don't drive — they inform.

2. l-terminal tokens should cluster in the WORK zone interior (C961: unordered
   bag of operations) rather than SETUP or CLOSE positions.
   Status checks are in the middle of work, not at boundaries.

3. l-terminal tokens should appear AFTER a state change more often than before.
   You CHECK status in response to something happening, not proactively.

4. On lines with BOTH l-terminal and kernel tokens, l should appear in
   non-first, non-last position more than kernel tokens do.
"""

import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

PROJECT = Path(__file__).resolve().parent


def normal_cdf(z):
    if z < -8: return 0.0
    if z > 8: return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1 if z >= 0 else -1
    t = 1.0 / (1.0 + p * abs(z))
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z * z / 2.0)
    return 0.5 * (1.0 + sign * y)


def spearman_rho(x, y):
    n = len(x)
    if n < 3: return 0.0, 1.0
    def rankdata(vals):
        indexed = sorted(enumerate(vals), key=lambda t: t[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n and indexed[j][1] == indexed[i][1]:
                j += 1
            avg = (i + j - 1) / 2.0 + 1
            for kk in range(i, j):
                ranks[indexed[kk][0]] = avg
            i = j
        return ranks
    rx, ry = rankdata(x), rankdata(y)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    dy = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    if dx == 0 or dy == 0: return 0.0, 1.0
    rho = num / (dx * dy)
    if abs(rho) >= 1.0: return rho, 0.0
    t_stat = rho * math.sqrt((n - 2) / (1 - rho ** 2))
    p = 2 * (1 - normal_cdf(abs(t_stat)))
    return rho, p


tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

kernel_atoms = {'k', 'h', 'e'}

# ============================================================
# Build per-line data with position info
# ============================================================
print("Building per-line position data...")

b_folios = sorted(set(t.folio for t in tx.currier_b()))

# Collect line analyses for opener/position info
line_analyses = {}
for folio in b_folios:
    try:
        lines = decoder.analyze_folio_lines(folio)
        for la in lines:
            line_analyses[(folio, la.line_id)] = la
    except Exception:
        pass

print(f"  Line analyses: {len(line_analyses)}")

# Build token sequences
line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

# ============================================================
# Test 1: Opener position — is l-terminal ever the line opener?
# ============================================================
print(f"\n{'='*70}")
print("TEST 1: l-TERMINAL AS LINE OPENER vs OTHER TERMINALS")
print(f"{'='*70}")
print("C959: Line opener determines line character.")
print("Prediction: l-terminal is RARELY the opener (status doesn't drive)\n")

# Per terminal atom: what fraction appear as position 0 (opener)?
term_opener = defaultdict(lambda: {'opener': 0, 'non_opener': 0, 'total': 0})

for (folio, line_id), words in line_tokens.items():
    if len(words) < 3:
        continue
    mids = []
    for w in words:
        mid = morph.extract(w).middle
        mids.append(mid if mid else None)

    for pos, mid in enumerate(mids):
        if not mid or len(mid) < 2:
            continue
        terminal = mid[-1]
        term_opener[terminal]['total'] += 1
        if pos == 0:
            term_opener[terminal]['opener'] += 1
        else:
            term_opener[terminal]['non_opener'] += 1

print(f"  {'Term':<5s} {'opener%':>10s} {'opener':>8s} {'total':>8s}")
print(f"  {'-'*5} {'-'*10} {'-'*8} {'-'*8}")

opener_results = []
for term in sorted(term_opener.keys()):
    d = term_opener[term]
    if d['total'] < 100:
        continue
    rate = d['opener'] / d['total'] * 100
    opener_results.append((term, rate, d['opener'], d['total']))

opener_results.sort(key=lambda x: -x[1])
for term, rate, opener, total in opener_results:
    marker = ' <-- l' if term == 'l' else ' <-- kernel' if term in kernel_atoms else ''
    print(f"  {term:<5s} {rate:>9.2f}% {opener:>8d} {total:>8d}{marker}")

# ============================================================
# Test 2: Position zone — SETUP / WORK / CLOSE
# ============================================================
print(f"\n{'='*70}")
print("TEST 2: l-TERMINAL POSITION WITHIN LINE (normalized)")
print(f"{'='*70}")
print("Prediction: l clusters in INTERIOR (work zone), avoids boundaries\n")

# For each terminal atom, collect normalized positions [0,1]
term_positions = defaultdict(list)

for (folio, line_id), words in line_tokens.items():
    n = len(words)
    if n < 5:
        continue
    mids = []
    for w in words:
        mid = morph.extract(w).middle
        mids.append(mid if mid else None)

    for pos, mid in enumerate(mids):
        if not mid or len(mid) < 2:
            continue
        norm_pos = pos / (n - 1) if n > 1 else 0.5
        terminal = mid[-1]
        term_positions[terminal].append(norm_pos)

print(f"  {'Term':<5s} {'mean pos':>10s} {'first 20%':>10s} {'last 20%':>10s} {'interior':>10s} {'n':>8s}")
print(f"  {'-'*5} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*8}")

for term in sorted(term_positions.keys()):
    positions = term_positions[term]
    if len(positions) < 100:
        continue
    mean_p = sum(positions) / len(positions)
    first_20 = sum(1 for p in positions if p < 0.2) / len(positions) * 100
    last_20 = sum(1 for p in positions if p > 0.8) / len(positions) * 100
    interior = sum(1 for p in positions if 0.2 <= p <= 0.8) / len(positions) * 100
    marker = ' <-- l' if term == 'l' else ' <-- kernel' if term in kernel_atoms else ''
    print(f"  {term:<5s} {mean_p:>10.4f} {first_20:>9.1f}% {last_20:>9.1f}% {interior:>9.1f}% {len(positions):>8d}{marker}")

# ============================================================
# Test 3: After state change — does l appear AFTER macro-state change?
# ============================================================
print(f"\n{'='*70}")
print("TEST 3: l-TERMINAL AFTER MACRO-STATE CHANGE")
print(f"{'='*70}")
print("For each token, is the PRECEDING token a different macro-state?")
print("Prediction: l appears after state changes more than average\n")

# Build macro-state sequences
term_after_change = defaultdict(lambda: {'after_change': 0, 'after_same': 0})

for (folio, line_id), words in line_tokens.items():
    if len(words) < 4:
        continue

    seq = []
    for w in words:
        mid = morph.extract(w).middle
        if not mid:
            seq.append((None, None, None))
            continue
        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        terminal = mid[-1] if len(mid) >= 2 else None
        seq.append((mid, terminal, ms))

    for i in range(1, len(seq)):
        curr_mid, curr_term, curr_ms = seq[i]
        prev_mid, prev_term, prev_ms = seq[i-1]
        if not curr_term or not curr_ms or not prev_ms:
            continue

        if prev_ms != curr_ms:
            term_after_change[curr_term]['after_change'] += 1
        else:
            term_after_change[curr_term]['after_same'] += 1

print(f"  {'Term':<5s} {'after-change%':>14s} {'after-change':>14s} {'total':>8s}")
print(f"  {'-'*5} {'-'*14} {'-'*14} {'-'*8}")

ac_results = []
for term in sorted(term_after_change.keys()):
    d = term_after_change[term]
    total = d['after_change'] + d['after_same']
    if total < 100:
        continue
    rate = d['after_change'] / total * 100
    ac_results.append((term, rate, d['after_change'], total))

ac_results.sort(key=lambda x: -x[1])
for term, rate, ac, total in ac_results:
    marker = ' <-- l' if term == 'l' else ' <-- kernel' if term in kernel_atoms else ''
    print(f"  {term:<5s} {rate:>13.2f}% {ac:>14d} {total:>8d}{marker}")

# ============================================================
# Test 4: On mixed lines (both l-terminal and kernel), where is l?
# ============================================================
print(f"\n{'='*70}")
print("TEST 4: ON MIXED LINES, l-TERMINAL vs KERNEL RELATIVE POSITION")
print(f"{'='*70}")
print("On lines with BOTH l-terminal and kernel tokens:")
print("Prediction: l appears AFTER kernel (check AFTER operate)\n")

l_before_kernel = 0
kernel_before_l = 0

for (folio, line_id), words in line_tokens.items():
    if len(words) < 4:
        continue

    l_positions = []
    kernel_positions = []

    for pos, w in enumerate(words):
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2:
            continue
        terminal = mid[-1]
        if terminal == 'l':
            l_positions.append(pos)
        if set(mid) & kernel_atoms:
            kernel_positions.append(pos)

    if l_positions and kernel_positions:
        first_l = min(l_positions)
        first_k = min(kernel_positions)
        if first_l < first_k:
            l_before_kernel += 1
        elif first_k < first_l:
            kernel_before_l += 1

total_mixed = l_before_kernel + kernel_before_l
if total_mixed > 0:
    kernel_first_pct = kernel_before_l / total_mixed * 100
    print(f"  Kernel-before-l: {kernel_before_l} ({kernel_first_pct:.1f}%)")
    print(f"  l-before-kernel: {l_before_kernel} ({100-kernel_first_pct:.1f}%)")
    print(f"  Total mixed lines: {total_mixed}")

    # Also: mean position of l vs kernel on mixed lines
    l_mean_pos = []
    k_mean_pos = []
    for (folio, line_id), words in line_tokens.items():
        n = len(words)
        if n < 4:
            continue
        l_pos = []
        k_pos = []
        for pos, w in enumerate(words):
            mid = morph.extract(w).middle
            if not mid or len(mid) < 2:
                continue
            norm = pos / (n - 1) if n > 1 else 0.5
            if mid[-1] == 'l':
                l_pos.append(norm)
            if set(mid) & kernel_atoms:
                k_pos.append(norm)
        if l_pos and k_pos:
            l_mean_pos.append(sum(l_pos) / len(l_pos))
            k_mean_pos.append(sum(k_pos) / len(k_pos))

    if l_mean_pos:
        l_mean = sum(l_mean_pos) / len(l_mean_pos)
        k_mean = sum(k_mean_pos) / len(k_mean_pos)
        print(f"\n  On mixed lines:")
        print(f"    l-terminal mean position: {l_mean:.4f}")
        print(f"    kernel mean position:     {k_mean:.4f}")
        order = 'kernel-first' if k_mean < l_mean else 'l-first'
        print(f"    --> {order}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-L15 SUMMARY")
print(f"{'='*70}")

l_opener_rate = next((r for t, r, _, _ in opener_results if t == 'l'), None)
l_ac_rate = next((r for t, r, _, _ in ac_results if t == 'l'), None)
baseline_ac = sum(r for _, r, _, _ in ac_results) / len(ac_results) if ac_results else 0

print(f"\n  Test 1 - l as opener: {l_opener_rate:.2f}%")
# Get mean across all atoms
mean_opener = sum(r for _, r, _, _ in opener_results) / len(opener_results) if opener_results else 0
print(f"    (mean across atoms: {mean_opener:.2f}%)")
if l_opener_rate and l_opener_rate < mean_opener * 0.8:
    print(f"    SUPPORTS: l AVOIDS opener position")
elif l_opener_rate and l_opener_rate < mean_opener:
    print(f"    WEAKLY supports: l slightly below average")
else:
    print(f"    DOES NOT support")

print(f"\n  Test 3 - l after state change: {l_ac_rate:.2f}%")
print(f"    (mean across atoms: {baseline_ac:.2f}%)")
if l_ac_rate and l_ac_rate > baseline_ac * 1.15:
    print(f"    SUPPORTS: l appears after state changes")
elif l_ac_rate and l_ac_rate > baseline_ac:
    print(f"    WEAKLY supports")
else:
    print(f"    DOES NOT support")

if total_mixed > 0:
    print(f"\n  Test 4 - kernel-before-l: {kernel_first_pct:.1f}%")
    if kernel_first_pct > 55:
        print(f"    SUPPORTS: kernel operates, then l checks status")
    elif kernel_first_pct > 50:
        print(f"    WEAKLY supports")
    else:
        print(f"    DOES NOT support")
