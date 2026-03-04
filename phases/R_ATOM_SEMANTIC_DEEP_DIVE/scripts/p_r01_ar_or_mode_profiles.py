"""P-R1: ar-initial and or-initial tokens have different suffix mode profiles.

If r = "return/reflux", then:
- ar = "collected product" (yield + return) -> Mode A leaning (specification)
- or = "vessel reflux" (vessel + return) -> Mode B leaning (continuation)

Test: Compute Mode A fraction for tokens with ar- vs or- initial MIDDLEs.
Also compare all Xr-initial compounds for systematic mode differences.
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
# Build per-line suffix mode data
# ============================================================
print("Building per-line suffix mode data...")

b_folios = sorted(set(t.folio for t in tx.currier_b()))

# Get line-level suffix mode from BFolioDecoder
line_mode = {}  # (folio, line_id) -> 'A' or 'B'
for folio in b_folios:
    try:
        lines = decoder.analyze_folio_lines(folio)
        for la in lines:
            if la.suffix_mode in ('A', 'B'):
                line_mode[(folio, la.line_id)] = la.suffix_mode
    except Exception:
        pass

print(f"  Lines with mode classification: {len(line_mode)}")

# Build token -> line mapping
line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

# ============================================================
# P-R1a: ar-initial vs or-initial suffix mode profiles
# ============================================================
print(f"\n{'='*70}")
print("P-R1a: ar-INITIAL vs or-INITIAL SUFFIX MODE PROFILES")
print(f"{'='*70}")
print("Prediction: ar leans Mode A (specification), or leans Mode B (continuation)\n")

# For each compound starting with ar or or, track which mode lines they appear on
xr_mode_counts = defaultdict(lambda: {'A': 0, 'B': 0, 'total': 0})

for (folio, line_id), words in line_tokens.items():
    mode = line_mode.get((folio, line_id))
    if not mode:
        continue
    for w in words:
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2:
            continue
        # Check first two characters of MIDDLE
        bigram = mid[:2]
        if mid[-1] == 'r' or bigram[1] == 'r':
            # Track by initial bigram if r is involved
            pass
        # Track all Xr-initial compounds (where X is an atom and r follows)
        if len(mid) >= 2 and mid[1] == 'r':
            prefix_pair = mid[:2]
            xr_mode_counts[prefix_pair][mode] += 1
            xr_mode_counts[prefix_pair]['total'] += 1
        # Also track r-terminal compounds by initial
        if len(mid) >= 2 and mid[-1] == 'r':
            init_r = f"{mid[0]}...r"
            xr_mode_counts[init_r][mode] += 1
            xr_mode_counts[init_r]['total'] += 1

# Report ar vs or specifically
print(f"  {'Compound':<12s} {'Mode A':>8s} {'Mode B':>8s} {'total':>8s} {'%A':>8s}")
print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

for key in sorted(xr_mode_counts.keys()):
    d = xr_mode_counts[key]
    if d['total'] < 20:
        continue
    pct_a = d['A'] / d['total'] * 100
    marker = ''
    if key in ('ar', 'or', 'a...r', 'o...r'):
        marker = ' <-- target'
    print(f"  {key:<12s} {d['A']:>8d} {d['B']:>8d} {d['total']:>8d} {pct_a:>7.1f}%{marker}")

# ============================================================
# P-R1b: Comprehensive r-terminal mode profile by initial atom
# ============================================================
print(f"\n{'='*70}")
print("P-R1b: r-TERMINAL COMPOUNDS BY INITIAL ATOM — MODE PROFILE")
print(f"{'='*70}")
print("For each initial atom X, compare Xr-terminal mode profile to X-non-r\n")

# Collect: for each initial atom, r-terminal vs non-r-terminal mode counts
init_r_mode = defaultdict(lambda: {'A': 0, 'B': 0})
init_nonr_mode = defaultdict(lambda: {'A': 0, 'B': 0})

for (folio, line_id), words in line_tokens.items():
    mode = line_mode.get((folio, line_id))
    if not mode:
        continue
    for w in words:
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2:
            continue
        initial = mid[0]
        terminal = mid[-1]
        if terminal == 'r':
            init_r_mode[initial][mode] += 1
        else:
            init_nonr_mode[initial][mode] += 1

print(f"  {'Init':<5s} {'r-term %A':>10s} {'r-term n':>10s} {'non-r %A':>10s} {'non-r n':>10s} {'delta':>8s}")
print(f"  {'-'*5} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*8}")

deltas = []
for init in sorted(set(list(init_r_mode.keys()) + list(init_nonr_mode.keys()))):
    r_total = init_r_mode[init]['A'] + init_r_mode[init]['B']
    nr_total = init_nonr_mode[init]['A'] + init_nonr_mode[init]['B']
    if r_total < 30 or nr_total < 30:
        continue
    r_pct_a = init_r_mode[init]['A'] / r_total * 100
    nr_pct_a = init_nonr_mode[init]['A'] / nr_total * 100
    delta = r_pct_a - nr_pct_a
    deltas.append((init, r_pct_a, r_total, nr_pct_a, nr_total, delta))
    print(f"  {init:<5s} {r_pct_a:>9.1f}% {r_total:>10d} {nr_pct_a:>9.1f}% {nr_total:>10d} {delta:>+7.1f}pp")

# Overall r-terminal mode
all_r_a = sum(init_r_mode[i]['A'] for i in init_r_mode)
all_r_b = sum(init_r_mode[i]['B'] for i in init_r_mode)
all_r_total = all_r_a + all_r_b
all_nr_a = sum(init_nonr_mode[i]['A'] for i in init_nonr_mode)
all_nr_b = sum(init_nonr_mode[i]['B'] for i in init_nonr_mode)
all_nr_total = all_nr_a + all_nr_b

if all_r_total > 0 and all_nr_total > 0:
    r_pct = all_r_a / all_r_total * 100
    nr_pct = all_nr_a / all_nr_total * 100
    print(f"\n  Overall r-terminal: {r_pct:.1f}% Mode A (n={all_r_total})")
    print(f"  Overall non-r:     {nr_pct:.1f}% Mode A (n={all_nr_total})")
    print(f"  Delta: {r_pct - nr_pct:+.1f}pp")

# ============================================================
# P-R1c: Compare ALL terminal atoms' mode profiles (ranking)
# ============================================================
print(f"\n{'='*70}")
print("ALL TERMINAL ATOMS: MODE A FRACTION (comprehensive ranking)")
print(f"{'='*70}")

term_mode = defaultdict(lambda: {'A': 0, 'B': 0})

for (folio, line_id), words in line_tokens.items():
    mode = line_mode.get((folio, line_id))
    if not mode:
        continue
    for w in words:
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2:
            continue
        terminal = mid[-1]
        term_mode[terminal][mode] += 1

print(f"\n  {'Term':<5s} {'%A':>8s} {'n':>8s}")
print(f"  {'-'*5} {'-'*8} {'-'*8}")

term_results = []
for term in sorted(term_mode.keys()):
    total = term_mode[term]['A'] + term_mode[term]['B']
    if total < 100:
        continue
    pct_a = term_mode[term]['A'] / total * 100
    term_results.append((term, pct_a, total))

term_results.sort(key=lambda x: -x[1])
for term, pct_a, total in term_results:
    marker = ' <-- r' if term == 'r' else ' <-- l' if term == 'l' else ' <-- kernel' if term in ('e', 'k', 'h') else ''
    print(f"  {term:<5s} {pct_a:>7.1f}% {total:>8d}{marker}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-R1 SUMMARY")
print(f"{'='*70}")

r_rank = next((i + 1 for i, (t, *_) in enumerate(term_results) if t == 'r'), None)
r_pct_a_val = next((p for t, p, _ in term_results if t == 'r'), None)
l_pct_a_val = next((p for t, p, _ in term_results if t == 'l'), None)

print(f"\n  r-terminal Mode A: {r_pct_a_val:.1f}% (rank {r_rank}/{len(term_results)})")
if l_pct_a_val:
    print(f"  l-terminal Mode A: {l_pct_a_val:.1f}% (for comparison)")

mean_delta = sum(d[-1] for d in deltas) / len(deltas) if deltas else 0
print(f"\n  Mean delta (r-terminal - non-r, per initial): {mean_delta:+.1f}pp")
print(f"  Prediction: ar leans Mode A, or leans Mode B")

# Check ar vs or specifically
ar_data = xr_mode_counts.get('a...r', {'A': 0, 'B': 0, 'total': 0})
or_data = xr_mode_counts.get('o...r', {'A': 0, 'B': 0, 'total': 0})
if ar_data['total'] >= 10 and or_data['total'] >= 10:
    ar_pct = ar_data['A'] / ar_data['total'] * 100
    or_pct = or_data['A'] / or_data['total'] * 100
    print(f"\n  ar-terminal %A: {ar_pct:.1f}% (n={ar_data['total']})")
    print(f"  or-terminal %A: {or_pct:.1f}% (n={or_data['total']})")
    if ar_pct > or_pct + 5:
        print(f"  SUPPORTS: ar leans Mode A more than or ({ar_pct - or_pct:+.1f}pp)")
    elif abs(ar_pct - or_pct) <= 5:
        print(f"  NULL: ar and or similar ({ar_pct - or_pct:+.1f}pp)")
    else:
        print(f"  INVERTED: or leans Mode A more than ar ({or_pct - ar_pct:+.1f}pp)")
