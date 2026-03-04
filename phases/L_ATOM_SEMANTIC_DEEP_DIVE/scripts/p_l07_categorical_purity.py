"""P-L7: Is l-terminal uniquely a categorical purifier?

Direct test: compare categorical concentration (HHI) of compounds
by terminal atom. If l = "dedicated" (specifier), l-terminal compounds
should have the HIGHEST categorical purity of any terminal atom.

HHI = sum of squared category fractions. Range: 0.125 (uniform across 8 cats) to 1.0 (all one cat).
"""

import json
import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

PROJECT = Path(__file__).resolve().parent

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

atoms_set = set('adehkonimycpfstrlq')
categories = ['STAGING', 'THERMAL', 'FLOW', 'OPERATION', 'TRANSITION',
              'CONTAINMENT', 'MARKING', 'MONITORING']

# ============================================================
# Collect: category distribution by terminal atom (for compound MIDDLEs only)
# ============================================================

# terminal_atom -> {category: count}
term_cat = defaultdict(Counter)
term_total = Counter()

# Also: (initial, terminal) -> {category: count} for per-pair analysis
pair_cat = defaultdict(Counter)
pair_total = Counter()

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid or len(mid) < 2:  # compound only (2+ chars)
        continue

    analysis = decoder.analyze_token(w)
    cat = analysis.operational_category
    if not cat:
        continue

    initial = mid[0]
    terminal = mid[-1]
    if initial not in atoms_set or terminal not in atoms_set:
        continue
    if initial == terminal:  # skip single-repeated (ee, kk, etc.)
        continue

    term_cat[terminal][cat] += 1
    term_total[terminal] += 1
    pair_cat[(initial, terminal)][cat] += 1
    pair_total[(initial, terminal)] += 1

# ============================================================
# Compute HHI per terminal atom
# ============================================================
print(f"{'='*70}")
print("CATEGORICAL PURITY BY TERMINAL ATOM (HHI)")
print(f"{'='*70}")
print("HHI = 1.0 means all tokens in one category (perfect purity)")
print("HHI = 0.125 means uniform across 8 categories (no purity)")
print(f"\nPrediction: l-terminal has HIGHEST HHI\n")

print(f"  {'Term':<5s} {'HHI':>8s} {'n':>8s} {'dominant cat':>16s} {'dom %':>8s} {'#cats>5%':>9s}")
print(f"  {'-'*5} {'-'*8} {'-'*8} {'-'*16} {'-'*8} {'-'*9}")

results = []
for term in sorted(term_cat.keys()):
    n = term_total[term]
    if n < 50:  # need enough data
        continue
    fracs = {cat: term_cat[term].get(cat, 0) / n for cat in categories}
    hhi = sum(f ** 2 for f in fracs.values())
    dominant = max(fracs, key=fracs.get)
    dom_pct = fracs[dominant] * 100
    cats_above_5 = sum(1 for f in fracs.values() if f > 0.05)
    results.append((term, hhi, n, dominant, dom_pct, cats_above_5))

results.sort(key=lambda x: -x[1])
for i, (term, hhi, n, dominant, dom_pct, cats5) in enumerate(results):
    rank = i + 1
    marker = ' <-- l' if term == 'l' else ''
    print(f"  {term:<5s} {hhi:>8.4f} {n:>8d} {dominant:>16s} {dom_pct:>7.1f}% {cats5:>9d}{marker}")

# ============================================================
# Per initial-atom: HHI with l-terminal vs best alternative terminal
# ============================================================
print(f"\n{'='*70}")
print("PER INITIAL ATOM: HHI OF l-TERMINAL vs BEST ALTERNATIVE TERMINAL")
print(f"{'='*70}")
print("(Does l produce higher purity than other terminals, per initial atom?)\n")

initials_to_test = ['o', 'e', 'a', 'k', 'i', 'd', 'r', 'y', 'n']

for init in initials_to_test:
    # Collect all terminal atoms for this initial
    term_hhis = []
    for term in sorted(atoms_set):
        if term == init:
            continue
        key = (init, term)
        n = pair_total[key]
        if n < 20:
            continue
        fracs = {cat: pair_cat[key].get(cat, 0) / n for cat in categories}
        hhi = sum(f ** 2 for f in fracs.values())
        dominant = max(fracs, key=fracs.get)
        dom_pct = fracs[dominant] * 100
        term_hhis.append((term, hhi, n, dominant, dom_pct))

    if not term_hhis:
        continue

    term_hhis.sort(key=lambda x: -x[1])
    l_entry = [t for t in term_hhis if t[0] == 'l']
    l_rank = next((i + 1 for i, t in enumerate(term_hhis) if t[0] == 'l'), None)

    print(f"  {init}-initial compounds (n terminals tested: {len(term_hhis)}):")
    # Show top 3 and l if not in top 3
    shown = set()
    for i, (term, hhi, n, dom, dom_pct) in enumerate(term_hhis[:3]):
        marker = ' <-- l' if term == 'l' else ''
        print(f"    #{i+1}: {init}+{term} HHI={hhi:.4f} n={n:>4d} dominant={dom}({dom_pct:.0f}%){marker}")
        shown.add(term)
    if l_entry and 'l' not in shown:
        term, hhi, n, dom, dom_pct = l_entry[0]
        print(f"    #{l_rank}: {init}+l HHI={hhi:.4f} n={n:>4d} dominant={dom}({dom_pct:.0f}%) <-- l")
    print()

# ============================================================
# Control: do other TERMINAL-class atoms (C1209: n, y, m, r, h) also purify?
# ============================================================
print(f"{'='*70}")
print("CONTROL: TERMINAL-CLASS ATOMS (C1209) — DO THEY ALL PURIFY?")
print(f"{'='*70}")
print("C1209 terminal atoms: l, n, y, m, r, h")
print("If l is special, it should have higher HHI than other terminal atoms\n")

terminal_class = ['l', 'n', 'y', 'm', 'r', 'h']
tc_results = [(term, hhi, n, dominant, dom_pct, cats5)
              for term, hhi, n, dominant, dom_pct, cats5 in
              [(t, h, nn, d, dp, c5) for t, h, nn, d, dp, c5 in
               [(term, sum((term_cat[term].get(cat, 0) / term_total[term]) ** 2 for cat in categories),
                 term_total[term],
                 max(categories, key=lambda c: term_cat[term].get(c, 0)),
                 term_cat[term].get(max(categories, key=lambda c: term_cat[term].get(c, 0)), 0) / term_total[term] * 100,
                 sum(1 for cat in categories if term_cat[term].get(cat, 0) / term_total[term] > 0.05))
                for term in terminal_class if term_total[term] >= 50]]
              ]

tc_results.sort(key=lambda x: -x[1])
print(f"  {'Atom':<5s} {'HHI':>8s} {'n':>8s} {'dominant':>16s} {'dom%':>8s} {'#cats>5%':>9s}")
print(f"  {'-'*5} {'-'*8} {'-'*8} {'-'*16} {'-'*8} {'-'*9}")
for term, hhi, n, dom, dom_pct, cats5 in tc_results:
    marker = ' <-- l' if term == 'l' else ''
    print(f"  {term:<5s} {hhi:>8.4f} {n:>8d} {dom:>16s} {dom_pct:>7.1f}% {cats5:>9d}{marker}")

# ============================================================
# The predictability test: can we predict WHICH category l purifies into?
# ============================================================
print(f"\n{'='*70}")
print("PREDICTABILITY: WHICH CATEGORY DOES l-TERMINAL PURIFY INTO?")
print(f"{'='*70}")
print("For each initial atom, compare: non-l dominant cat vs l-terminal dominant cat\n")

print(f"  {'Init':<5s} {'non-l dominant':>20s} {'non-l top%':>10s} {'l-term dominant':>20s} {'l-term top%':>10s} {'match?':>8s}")
print(f"  {'-'*5} {'-'*20} {'-'*10} {'-'*20} {'-'*10} {'-'*8}")

for init in sorted(atoms_set):
    # non-l terminal distribution for this initial
    nol_counts = Counter()
    nol_n = 0
    l_counts = Counter()
    l_n = 0

    for term in atoms_set:
        if term == init:
            continue
        key = (init, term)
        n = pair_total[key]
        if n == 0:
            continue
        if term == 'l':
            for cat in categories:
                l_counts[cat] += pair_cat[key].get(cat, 0)
            l_n += n
        else:
            for cat in categories:
                nol_counts[cat] += pair_cat[key].get(cat, 0)
            nol_n += n

    if nol_n < 20 or l_n < 10:
        continue

    nol_dom = max(categories, key=lambda c: nol_counts.get(c, 0))
    nol_pct = nol_counts[nol_dom] / nol_n * 100
    l_dom = max(categories, key=lambda c: l_counts.get(c, 0))
    l_pct = l_counts[l_dom] / l_n * 100
    match = 'YES' if nol_dom == l_dom else 'no'
    print(f"  {init:<5s} {nol_dom:>20s} {nol_pct:>9.1f}% {l_dom:>20s} {l_pct:>9.1f}% {match:>8s}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-L7 SUMMARY")
print(f"{'='*70}")

l_hhi = None
l_rank = None
for i, (term, hhi, n, dominant, dom_pct, cats5) in enumerate(results):
    if term == 'l':
        l_hhi = hhi
        l_rank = i + 1

print(f"\n  l-terminal HHI: {l_hhi:.4f} (rank {l_rank}/{len(results)})")
print(f"  Prediction: l has HIGHEST HHI (rank 1)")
if l_rank == 1:
    print(f"  RESULT: CONFIRMED — l-terminal is the strongest categorical purifier")
elif l_rank <= 3:
    print(f"  RESULT: PARTIAL — l is top-3 but not #1")
else:
    print(f"  RESULT: FAILED — l is not uniquely a purifier (rank {l_rank})")
