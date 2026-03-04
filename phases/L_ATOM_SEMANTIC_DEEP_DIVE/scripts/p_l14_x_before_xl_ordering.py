"""P-L14: X-atom precedes Xl-compound on shared lines.

If l = "product of X", then on lines containing both X-MIDDLEs and Xl-MIDDLEs,
X should appear BEFORE Xl at above-chance rates (>60%).

Test: For each base atom X, find lines containing both X-containing tokens and
Xl tokens. Compute the fraction where X precedes Xl.
"""

import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology

PROJECT = Path(__file__).resolve().parent

tx = Transcript()
morph = Morphology()

atoms_set = set('adehkonimycpfstrlq')

# ============================================================
# Build per-line MIDDLE sequences
# ============================================================
print("Building per-line MIDDLE sequences...")

line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

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
# P-L14a: For each base atom X, find co-occurrence with Xl
# ============================================================
print(f"\n{'='*70}")
print("P-L14: X-ATOM BEFORE Xl-COMPOUND ORDERING TEST")
print(f"{'='*70}")
print("Prediction: X precedes Xl at >60% on shared lines\n")

# For each base atom X:
# - Find lines that contain BOTH an X-initial (or X-containing) non-l MIDDLE
#   AND an Xl compound
# - Check ordering: does ANY X-non-l token precede the FIRST Xl token?

base_atoms = ['o', 'e', 'a', 'k', 'd', 'i', 'r', 'y', 'n']

print(f"  {'Base':<5s} {'X-before-Xl':>14s} {'Xl-before-X':>14s} {'total':>8s} {'X-first %':>10s}")
print(f"  {'-'*5} {'-'*14} {'-'*14} {'-'*8} {'-'*10}")

results = []

for base in base_atoms:
    x_before_xl = 0
    xl_before_x = 0

    for (folio, line_id), mids in line_middles.items():
        # Find positions of:
        # 1. Tokens with base atom X in MIDDLE but NOT l-terminal (X-operation tokens)
        # 2. Tokens with Xl compound (l-terminal with base atom X as initial)
        x_positions = []
        xl_positions = []

        for pos, mid in enumerate(mids):
            if len(mid) < 2:
                continue

            is_l_terminal = (mid[-1] == 'l')
            initial = mid[0]

            if is_l_terminal and initial == base:
                # This is an Xl compound
                xl_positions.append(pos)
            elif not is_l_terminal and base in mid:
                # This contains base atom X but is not l-terminal
                x_positions.append(pos)

        # Need at least one of each
        if not x_positions or not xl_positions:
            continue

        # Check: does ANY X come before the FIRST Xl?
        first_xl = min(xl_positions)
        first_x = min(x_positions)

        if first_x < first_xl:
            x_before_xl += 1
        else:
            xl_before_x += 1

    total = x_before_xl + xl_before_x
    if total < 10:
        continue

    pct = x_before_xl / total * 100
    results.append((base, x_before_xl, xl_before_x, total, pct))
    print(f"  {base:<5s} {x_before_xl:>14d} {xl_before_x:>14d} {total:>8d} {pct:>9.1f}%")

# ============================================================
# P-L14b: Stricter test — X-initial (not just containing) before Xl
# ============================================================
print(f"\n{'='*70}")
print("STRICTER: X-INITIAL (not containing) BEFORE Xl")
print(f"{'='*70}")
print("Only count tokens where X is the INITIAL atom of the MIDDLE\n")

print(f"  {'Base':<5s} {'X-before-Xl':>14s} {'Xl-before-X':>14s} {'total':>8s} {'X-first %':>10s}")
print(f"  {'-'*5} {'-'*14} {'-'*14} {'-'*8} {'-'*10}")

strict_results = []

for base in base_atoms:
    x_before_xl = 0
    xl_before_x = 0

    for (folio, line_id), mids in line_middles.items():
        x_positions = []
        xl_positions = []

        for pos, mid in enumerate(mids):
            if len(mid) < 2:
                continue

            initial = mid[0]
            terminal = mid[-1]

            if terminal == 'l' and initial == base:
                xl_positions.append(pos)
            elif initial == base and terminal != 'l':
                x_positions.append(pos)

        if not x_positions or not xl_positions:
            continue

        first_xl = min(xl_positions)
        first_x = min(x_positions)

        if first_x < first_xl:
            x_before_xl += 1
        else:
            xl_before_x += 1

    total = x_before_xl + xl_before_x
    if total < 10:
        continue

    pct = x_before_xl / total * 100
    strict_results.append((base, x_before_xl, xl_before_x, total, pct))
    print(f"  {base:<5s} {x_before_xl:>14d} {xl_before_x:>14d} {total:>8d} {pct:>9.1f}%")

# ============================================================
# P-L14c: Control — ALL terminal atoms (not just l)
# ============================================================
print(f"\n{'='*70}")
print("CONTROL: FOR EACH TERMINAL ATOM T, DOES X PRECEDE XT?")
print(f"{'='*70}")
print("(Is the ordering effect l-specific or universal for all terminals?)\n")

# For o-initial as example: compare ordering of o+y, o+d, o+l, o+r, etc.
for base in ['o', 'e']:
    print(f"\n  {base}-initial compounds:")
    print(f"    {'Term':<5s} {'X-before':>10s} {'XT-before':>10s} {'total':>8s} {'X-first %':>10s}")
    print(f"    {'-'*5} {'-'*10} {'-'*10} {'-'*8} {'-'*10}")

    term_order_results = []
    for terminal in sorted(atoms_set):
        if terminal == base:
            continue
        xb = 0
        xtb = 0

        for (folio, line_id), mids in line_middles.items():
            x_pos = []
            xt_pos = []

            for pos, mid in enumerate(mids):
                if len(mid) < 2:
                    continue
                if mid[0] == base and mid[-1] == terminal:
                    xt_pos.append(pos)
                elif mid[0] == base and mid[-1] != terminal:
                    x_pos.append(pos)

            if not x_pos or not xt_pos:
                continue

            if min(x_pos) < min(xt_pos):
                xb += 1
            else:
                xtb += 1

        total = xb + xtb
        if total < 10:
            continue
        pct = xb / total * 100
        term_order_results.append((terminal, xb, xtb, total, pct))

    term_order_results.sort(key=lambda x: -x[4])
    for terminal, xb, xtb, total, pct in term_order_results:
        marker = ' <-- l' if terminal == 'l' else ''
        print(f"    {terminal:<5s} {xb:>10d} {xtb:>10d} {total:>8d} {pct:>9.1f}%{marker}")

# ============================================================
# P-L14d: Median position of Xl vs X-non-l on shared lines
# ============================================================
print(f"\n{'='*70}")
print("MEDIAN POSITION: WHERE DOES Xl APPEAR vs X-non-l ON SHARED LINES?")
print(f"{'='*70}")

for base in base_atoms:
    x_norm_positions = []
    xl_norm_positions = []

    for (folio, line_id), mids in line_middles.items():
        n = len(mids)
        x_pos = []
        xl_pos = []

        for pos, mid in enumerate(mids):
            if len(mid) < 2:
                continue
            if mid[0] == base and mid[-1] == 'l':
                xl_pos.append(pos / (n - 1) if n > 1 else 0.5)
            elif mid[0] == base and mid[-1] != 'l':
                x_pos.append(pos / (n - 1) if n > 1 else 0.5)

        if x_pos and xl_pos:
            x_norm_positions.extend(x_pos)
            xl_norm_positions.extend(xl_pos)

    if len(x_norm_positions) < 20 or len(xl_norm_positions) < 20:
        continue

    x_mean = sum(x_norm_positions) / len(x_norm_positions)
    xl_mean = sum(xl_norm_positions) / len(xl_norm_positions)
    x_sorted = sorted(x_norm_positions)
    xl_sorted = sorted(xl_norm_positions)
    x_median = x_sorted[len(x_sorted) // 2]
    xl_median = xl_sorted[len(xl_sorted) // 2]

    order = 'X-first' if x_mean < xl_mean else 'Xl-first'
    print(f"  {base}: X-non-l mean pos={x_mean:.4f} (n={len(x_norm_positions)}), "
          f"Xl mean pos={xl_mean:.4f} (n={len(xl_norm_positions)}) -> {order}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-L14 SUMMARY")
print(f"{'='*70}")

confirmed = 0
total_tested = len(results)
for base, xb, xlb, total, pct in results:
    if pct > 60:
        confirmed += 1

print(f"\n  Base atoms where X-before-Xl > 60%: {confirmed}/{total_tested}")
print(f"  Prediction: >=3 base atoms show X-before-Xl > 60%")

if confirmed >= 3:
    print(f"  RESULT: CONFIRMED ({confirmed}/{total_tested} base atoms show X-before-Xl ordering)")
elif confirmed >= 1:
    print(f"  RESULT: PARTIAL ({confirmed}/{total_tested} base atoms)")
else:
    print(f"  RESULT: FAILED (no base atoms show consistent X-before-Xl ordering)")

# Strict test
strict_confirmed = 0
strict_tested = len(strict_results)
for base, xb, xlb, total, pct in strict_results:
    if pct > 60:
        strict_confirmed += 1

print(f"\n  Strict (X-initial only): {strict_confirmed}/{strict_tested} base atoms > 60%")
