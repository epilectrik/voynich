"""P-L13: l-terminal MIDDLEs predict HIGH successor MIDDLE diversity.

If l = "free/available" (uncommitted between operations), the next token
should be drawn from a WIDE pool. l-terminal successor entropy should be
in TOP 3 and HIGHER than all kernel atoms (e, k, h).
"""

import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology

PROJECT = Path(__file__).resolve().parent


def entropy(counts):
    """Shannon entropy from a Counter."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


tx = Transcript()
morph = Morphology()

# ============================================================
# Build token sequences per line
# ============================================================
print("Building per-line token sequences...")

line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

# Extract MIDDLE sequences per line
line_middles = {}
for (folio, line_id), words in line_tokens.items():
    mids = []
    for w in words:
        mid = morph.extract(w).middle
        if mid:
            mids.append(mid)
    if len(mids) >= 3:
        line_middles[(folio, line_id)] = mids

print(f"  Lines with >=3 MIDDLEs: {len(line_middles)}")

# ============================================================
# For each token, record what MIDDLE follows it
# ============================================================
print("Computing successor distributions...\n")

# terminal_atom -> Counter of successor MIDDLEs
term_successor = defaultdict(Counter)
# Also track: MIDDLE -> Counter of successor MIDDLEs (for specific compounds)
mid_successor = defaultdict(Counter)

atoms_set = set('adehkonimycpfstrlq')

for (folio, line_id), mids in line_middles.items():
    for i in range(len(mids) - 1):
        curr = mids[i]
        succ = mids[i + 1]

        if len(curr) >= 2:
            terminal = curr[-1]
            if terminal in atoms_set:
                term_successor[terminal][succ] += 1
        else:
            # Single-atom MIDDLE
            if curr in atoms_set:
                term_successor[curr][succ] += 1

        if len(curr) >= 2:
            mid_successor[curr][succ] += 1

# ============================================================
# P-L13a: Successor entropy by terminal atom
# ============================================================
print(f"{'='*70}")
print("SUCCESSOR MIDDLE ENTROPY BY TERMINAL ATOM")
print(f"{'='*70}")
print("Higher entropy = more diverse successor pool")
print(f"Prediction: l in TOP 3, above e, k, h\n")

print(f"  {'Term':<5s} {'entropy':>10s} {'unique':>8s} {'total':>8s} {'top succ':>14s} {'top %':>8s}")
print(f"  {'-'*5} {'-'*10} {'-'*8} {'-'*8} {'-'*14} {'-'*8}")

results = []
for term in sorted(term_successor.keys()):
    counts = term_successor[term]
    total = sum(counts.values())
    if total < 100:
        continue
    h = entropy(counts)
    n_unique = len(counts)
    top_succ = counts.most_common(1)[0] if counts else ('', 0)
    top_pct = top_succ[1] / total * 100 if total > 0 else 0
    results.append((term, h, n_unique, total, top_succ[0], top_pct))

results.sort(key=lambda x: -x[1])
for i, (term, h, nu, total, ts, tp) in enumerate(results):
    marker = ' <-- l' if term == 'l' else ' <-- kernel' if term in ('e', 'k', 'h') else ''
    print(f"  {term:<5s} {h:>10.4f} {nu:>8d} {total:>8d} {ts:>14s} {tp:>7.1f}%{marker}")

l_rank = next((i + 1 for i, (t, *_) in enumerate(results) if t == 'l'), None)
l_entropy = next((h for t, h, *_ in results if t == 'l'), None)
e_entropy = next((h for t, h, *_ in results if t == 'e'), None)
k_entropy = next((h for t, h, *_ in results if t == 'k'), None)
h_entropy = next((h for t, h, *_ in results if t == 'h'), None)

# ============================================================
# P-L13b: Normalized entropy (controlling for sample size)
# ============================================================
print(f"\n{'='*70}")
print("NORMALIZED SUCCESSOR ENTROPY (controlling for sample size)")
print(f"{'='*70}")
print("H_norm = H / log2(n_unique) -- fraction of maximum possible entropy\n")

print(f"  {'Term':<5s} {'H_norm':>10s} {'H':>8s} {'H_max':>8s} {'unique':>8s} {'total':>8s}")
print(f"  {'-'*5} {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

norm_results = []
for term, h, nu, total, ts, tp in results:
    h_max = math.log2(nu) if nu > 1 else 1.0
    h_norm = h / h_max if h_max > 0 else 0
    norm_results.append((term, h_norm, h, h_max, nu, total))

norm_results.sort(key=lambda x: -x[1])
for i, (term, hn, h, hm, nu, total) in enumerate(norm_results):
    marker = ' <-- l' if term == 'l' else ' <-- kernel' if term in ('e', 'k', 'h') else ''
    print(f"  {term:<5s} {hn:>10.4f} {h:>8.4f} {hm:>8.4f} {nu:>8d} {total:>8d}{marker}")

# ============================================================
# P-L13c: Successor concentration (Herfindahl)
# ============================================================
print(f"\n{'='*70}")
print("SUCCESSOR CONCENTRATION (HHI - lower = more diverse)")
print(f"{'='*70}")

print(f"\n  {'Term':<5s} {'HHI':>10s} {'total':>8s}")
print(f"  {'-'*5} {'-'*10} {'-'*8}")

hhi_results = []
for term in sorted(term_successor.keys()):
    counts = term_successor[term]
    total = sum(counts.values())
    if total < 100:
        continue
    hhi = sum((c / total) ** 2 for c in counts.values())
    hhi_results.append((term, hhi, total))

hhi_results.sort(key=lambda x: x[1])  # lower = more diverse
for i, (term, hhi, total) in enumerate(hhi_results):
    marker = ' <-- l' if term == 'l' else ' <-- kernel' if term in ('e', 'k', 'h') else ''
    print(f"  {term:<5s} {hhi:>10.6f} {total:>8d}{marker}")

# ============================================================
# P-L13d: Specific l-terminal MIDDLEs — successor diversity
# ============================================================
print(f"\n{'='*70}")
print("SPECIFIC l-TERMINAL MIDDLES: SUCCESSOR DIVERSITY")
print(f"{'='*70}")

print(f"\n  {'MIDDLE':<12s} {'entropy':>10s} {'unique':>8s} {'total':>8s} {'top succ':>14s} {'top %':>8s}")
print(f"  {'-'*12} {'-'*10} {'-'*8} {'-'*8} {'-'*14} {'-'*8}")

l_mid_results = []
for mid in sorted(mid_successor.keys()):
    if len(mid) < 2 or mid[-1] != 'l':
        continue
    counts = mid_successor[mid]
    total = sum(counts.values())
    if total < 30:
        continue
    h = entropy(counts)
    n_unique = len(counts)
    top_succ = counts.most_common(1)[0] if counts else ('', 0)
    top_pct = top_succ[1] / total * 100 if total > 0 else 0
    l_mid_results.append((mid, h, n_unique, total, top_succ[0], top_pct))

l_mid_results.sort(key=lambda x: -x[1])
for mid, h, nu, total, ts, tp in l_mid_results:
    print(f"  {mid:<12s} {h:>10.4f} {nu:>8d} {total:>8d} {ts:>14s} {tp:>7.1f}%")

# Compare to non-l peers from same initial
print(f"\n  Comparison: ol vs other o-terminal MIDDLEs:")
for mid in sorted(mid_successor.keys()):
    if len(mid) < 2 or mid[0] != 'o':
        continue
    counts = mid_successor[mid]
    total = sum(counts.values())
    if total < 30:
        continue
    h = entropy(counts)
    marker = ' *L*' if mid[-1] == 'l' else ''
    print(f"    {mid:<12s} H={h:.4f} n={total:>5d}{marker}")

print(f"\n  Comparison: eol/el vs other e-initial MIDDLEs:")
for mid in sorted(mid_successor.keys()):
    if len(mid) < 2 or mid[0] != 'e':
        continue
    counts = mid_successor[mid]
    total = sum(counts.values())
    if total < 30:
        continue
    h = entropy(counts)
    marker = ' *L*' if mid[-1] == 'l' else ''
    print(f"    {mid:<12s} H={h:.4f} n={total:>5d}{marker}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-L13 SUMMARY")
print(f"{'='*70}")

print(f"\n  l-terminal successor entropy: {l_entropy:.4f} (rank {l_rank}/{len(results)})")
print(f"  Prediction: l in TOP 3, above e({e_entropy:.4f}), k({k_entropy:.4f}), h({h_entropy:.4f})")

l_above_e = l_entropy > e_entropy if l_entropy and e_entropy else False
l_above_k = l_entropy > k_entropy if l_entropy and k_entropy else False
l_above_h = l_entropy > h_entropy if l_entropy and h_entropy else False

print(f"\n  l > e: {'YES' if l_above_e else 'NO'}")
print(f"  l > k: {'YES' if l_above_k else 'NO'}")
print(f"  l > h: {'YES' if l_above_h else 'NO'}")

if l_rank and l_rank <= 3 and l_above_e and l_above_k and l_above_h:
    print(f"\n  RESULT: CONFIRMED (l is rank {l_rank}, above all kernel atoms)")
elif l_above_e and l_above_k and l_above_h:
    print(f"\n  RESULT: PARTIAL (l above all kernels but rank {l_rank}, not top 3)")
elif l_rank and l_rank <= 5:
    print(f"\n  RESULT: PARTIAL (l is rank {l_rank})")
else:
    print(f"\n  RESULT: FAILED (l is rank {l_rank})")
