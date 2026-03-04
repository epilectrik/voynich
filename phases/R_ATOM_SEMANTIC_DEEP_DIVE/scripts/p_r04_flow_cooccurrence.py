"""P-R4: r-terminal MIDDLEs co-occur with FLOW-category tokens on the same line.

If r = "flow/run" (rinnen), then r-terminal tokens should appear on lines
that also contain other FLOW-category tokens (e.g., t-containing MIDDLEs),
because both describe the same physical phenomenon (fluid movement).

Compare FLOW co-occurrence lift to THERMAL and CONTAINMENT lifts.
If r = "flow", FLOW lift > 1.3x and THERMAL lift < 1.0x.
If r = "return/reflux", CONTAINMENT lift should dominate over FLOW.
"""

import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology, CategoryClassifier


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
cc = CategoryClassifier()

# ============================================================
# Build per-line data
# ============================================================
print("Building per-line token data...")

line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

print(f"  Total lines: {len(line_tokens)}")

# ============================================================
# P-R4a: r-terminal co-occurrence with FLOW-category tokens
# ============================================================
print(f"\n{'='*70}")
print("P-R4a: r-TERMINAL CO-OCCURRENCE WITH FLOW CATEGORY TOKENS")
print(f"{'='*70}")
print("Prediction: FLOW lift > 1.3x, THERMAL lift < 1.0x\n")

# For each line: classify each token's MIDDLE category, track r-terminal presence
line_has_r = {}  # line_key -> bool
line_categories = {}  # line_key -> set of categories (excluding r's own contribution)

for line_key, words in line_tokens.items():
    has_r_terminal = False
    cats_on_line = defaultdict(int)

    for w in words:
        m = morph.extract(w)
        mid = m.middle
        if not mid or len(mid) < 2:
            continue

        terminal = mid[-1]
        cat = cc.classify(mid)

        if terminal == 'r':
            has_r_terminal = True
            # Don't count this token's category for co-occurrence
            # (would be tautological since r IS FLOW)
        else:
            if cat:
                cats_on_line[cat] += 1

    line_has_r[line_key] = has_r_terminal
    line_categories[line_key] = dict(cats_on_line)

# Compute lifts
all_categories = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                   'TRANSITION', 'MARKING', 'MONITORING']

total_lines = len(line_tokens)
r_lines = sum(1 for v in line_has_r.values() if v)
non_r_lines = total_lines - r_lines

print(f"  Lines with r-terminal: {r_lines} / {total_lines} ({r_lines/total_lines*100:.1f}%)\n")
print(f"  {'Category':<14s} {'P(cat)':>8s} {'P(cat|r)':>10s} {'P(cat|~r)':>10s} {'lift':>8s}")
print(f"  {'-'*14} {'-'*8} {'-'*10} {'-'*10} {'-'*8}")

for cat in all_categories:
    # P(category present on line)
    lines_with_cat = sum(1 for lk in line_tokens if cat in line_categories.get(lk, {}))
    p_cat = lines_with_cat / total_lines if total_lines > 0 else 0

    # P(category present | r-terminal present)
    r_with_cat = sum(1 for lk in line_tokens if line_has_r.get(lk) and cat in line_categories.get(lk, {}))
    p_cat_given_r = r_with_cat / r_lines if r_lines > 0 else 0

    # P(category present | no r-terminal)
    nonr_with_cat = sum(1 for lk in line_tokens if not line_has_r.get(lk) and cat in line_categories.get(lk, {}))
    p_cat_given_nonr = nonr_with_cat / non_r_lines if non_r_lines > 0 else 0

    lift = p_cat_given_r / p_cat if p_cat > 0 else 0
    marker = ' <-- target' if cat in ('FLOW', 'THERMAL', 'CONTAINMENT') else ''
    print(f"  {cat:<14s} {p_cat:>7.3f} {p_cat_given_r:>10.3f} {p_cat_given_nonr:>10.3f} {lift:>7.3f}x{marker}")

# ============================================================
# P-R4b: r-terminal co-occurrence by INDIVIDUAL non-r atoms
# ============================================================
print(f"\n{'='*70}")
print("P-R4b: r-TERMINAL CO-OCCURRENCE BY INDIVIDUAL ATOM (LINE LEVEL)")
print(f"{'='*70}")
print("Which atoms does r prefer to share a line with?\n")

# For each line: track which non-r terminal atoms appear
atom_on_line = defaultdict(lambda: {'with_r': 0, 'without_r': 0})

for line_key, words in line_tokens.items():
    has_r = line_has_r.get(line_key, False)
    atoms_seen = set()

    for w in words:
        m = morph.extract(w)
        mid = m.middle
        if not mid or len(mid) < 2:
            continue
        # Track all atoms in the middle
        for atom in mid:
            if atom != 'r':
                atoms_seen.add(atom)

    for atom in atoms_seen:
        if has_r:
            atom_on_line[atom]['with_r'] += 1
        else:
            atom_on_line[atom]['without_r'] += 1

print(f"  {'Atom':<5s} {'with-r':>8s} {'no-r':>8s} {'%with-r':>10s} {'%no-r':>10s} {'lift':>8s} {'cat':>12s}")
print(f"  {'-'*5} {'-'*8} {'-'*8} {'-'*10} {'-'*10} {'-'*8} {'-'*12}")

atom_results = []
for atom in sorted(atom_on_line.keys()):
    d = atom_on_line[atom]
    wr = d['with_r']
    nr = d['without_r']
    pct_wr = wr / r_lines * 100 if r_lines > 0 else 0
    pct_nr = nr / non_r_lines * 100 if non_r_lines > 0 else 0
    lift = pct_wr / pct_nr if pct_nr > 0 else 0
    atom_cat = cc.ATOM_TO_CATEGORY.get(atom, '?')
    atom_results.append((atom, wr, nr, pct_wr, pct_nr, lift, atom_cat))

atom_results.sort(key=lambda x: -x[5])
for atom, wr, nr, pct_wr, pct_nr, lift, atom_cat in atom_results:
    marker = ''
    if atom == 't':
        marker = ' <-- FLOW'
    elif atom in ('k', 'e'):
        marker = ' <-- THERMAL'
    elif atom in ('n', 'd'):
        marker = ' <-- SEAL/MARK'
    print(f"  {atom:<5s} {wr:>8d} {nr:>8d} {pct_wr:>9.1f}% {pct_nr:>9.1f}% {lift:>7.3f}x {atom_cat:>12s}{marker}")

# ============================================================
# P-R4c: r-terminal × non-r-terminal category profile (TOKEN LEVEL)
# ============================================================
print(f"\n{'='*70}")
print("P-R4c: ON LINES WITH r-TERMINAL, WHAT IS THE CATEGORY MIX OF OTHER TOKENS?")
print(f"{'='*70}")

r_line_cat_counts = Counter()
nonr_line_cat_counts = Counter()

for line_key, words in line_tokens.items():
    has_r = line_has_r.get(line_key, False)
    for w in words:
        m = morph.extract(w)
        mid = m.middle
        if not mid or len(mid) < 2:
            continue
        if mid[-1] == 'r':
            continue  # skip r-terminal tokens themselves
        cat = cc.classify(mid)
        if cat:
            if has_r:
                r_line_cat_counts[cat] += 1
            else:
                nonr_line_cat_counts[cat] += 1

r_total = sum(r_line_cat_counts.values())
nr_total = sum(nonr_line_cat_counts.values())

print(f"\n  {'Category':<14s} {'r-line %':>10s} {'non-r %':>10s} {'lift':>8s}")
print(f"  {'-'*14} {'-'*10} {'-'*10} {'-'*8}")

for cat in all_categories:
    r_pct = r_line_cat_counts[cat] / r_total * 100 if r_total > 0 else 0
    nr_pct = nonr_line_cat_counts[cat] / nr_total * 100 if nr_total > 0 else 0
    lift = r_pct / nr_pct if nr_pct > 0 else 0
    marker = ' <-- target' if cat in ('FLOW', 'THERMAL', 'CONTAINMENT') else ''
    print(f"  {cat:<14s} {r_pct:>9.1f}% {nr_pct:>9.1f}% {lift:>7.3f}x{marker}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-R4 SUMMARY")
print(f"{'='*70}")
print("\nPrediction: FLOW lift > 1.3x, THERMAL lift < 1.0x")
print("If CONTAINMENT lift > FLOW lift -> supports 'return' over 'flow'")
print("If FLOW lift > CONTAINMENT lift -> supports 'flow' over 'return'")
