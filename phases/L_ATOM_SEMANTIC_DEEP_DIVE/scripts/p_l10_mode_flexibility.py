"""P-L10: l-terminal MIDDLEs have higher suffix mode flexibility than non-l-terminal.

If l = NOMINALIZER (converts action to state), then l-terminal compounds should
be more mode-neutral (closer to 50/50 Mode A/B split) because state descriptions
are context-independent, while active operations have natural mode affinities.

Prediction: For each initial atom X with enough data, Xl compounds have
mode_A_fraction closer to 0.50 than X-non-l compounds. Overall: l-terminal
flexibility > non-l-terminal flexibility.
"""

import json
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

atoms_set = set('adehkonimycpfstrlq')

# ============================================================
# Step 1: Get line-level suffix mode for all Currier B folios
# ============================================================
print("Building line-level suffix mode map...")

# folio -> line_id -> suffix_mode
line_mode_map = {}  # (folio, line_id) -> 'A' or 'B'

# Get all B folios from transcript
b_folios = sorted(set(t.folio for t in tx.currier_b()))
print(f"  Currier B folios: {len(b_folios)}")

for folio in b_folios:
    try:
        lines = decoder.analyze_folio_lines(folio)
        for la in lines:
            if la.suffix_mode:
                line_mode_map[(folio, la.line_id)] = la.suffix_mode
    except Exception:
        pass

print(f"  Lines with mode classification: {len(line_mode_map)}")
mode_counts = Counter(line_mode_map.values())
print(f"  Mode A: {mode_counts.get('A', 0)}, Mode B: {mode_counts.get('B', 0)}")

# ============================================================
# Step 2: For each MIDDLE, count appearances on Mode A vs Mode B lines
# ============================================================
print("\nCounting MIDDLE mode appearances...")

# middle -> {'A': count, 'B': count}
middle_mode = defaultdict(Counter)
# terminal_atom -> {'A': count, 'B': count}  (aggregated)
term_mode = defaultdict(Counter)
# (initial_atom, is_l_terminal) -> {'A': count, 'B': count}
init_lterm_mode = defaultdict(Counter)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid or len(mid) < 2:
        continue

    mode = line_mode_map.get((token.folio, token.line))
    if not mode:
        continue

    initial = mid[0]
    terminal = mid[-1]
    if initial not in atoms_set or terminal not in atoms_set:
        continue
    if initial == terminal and len(mid) == 2:  # skip doubled atoms like ee, kk
        continue

    middle_mode[mid][mode] += 1
    term_mode[terminal][mode] += 1
    is_l_term = (terminal == 'l')
    init_lterm_mode[(initial, is_l_term)][mode] += 1

# ============================================================
# P-L10a: Terminal atom mode flexibility ranking
# ============================================================
print(f"\n{'='*70}")
print("TERMINAL ATOM MODE FLEXIBILITY RANKING")
print(f"{'='*70}")
print("Flexibility = 1 - 2*|mode_A_frac - 0.5| (1.0 = perfect 50/50, 0.0 = locked)")
print(f"\nPrediction: l-terminal has HIGHEST flexibility\n")

print(f"  {'Term':<5s} {'mode_A%':>8s} {'mode_B%':>8s} {'flex':>8s} {'n':>8s}")
print(f"  {'-'*5} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

term_results = []
for term in sorted(term_mode.keys()):
    n_a = term_mode[term].get('A', 0)
    n_b = term_mode[term].get('B', 0)
    total = n_a + n_b
    if total < 50:
        continue
    frac_a = n_a / total
    flex = 1.0 - 2.0 * abs(frac_a - 0.5)
    term_results.append((term, frac_a, 1 - frac_a, flex, total))

term_results.sort(key=lambda x: -x[3])
for i, (term, fa, fb, flex, n) in enumerate(term_results):
    marker = ' <-- l' if term == 'l' else ''
    print(f"  {term:<5s} {fa*100:>7.1f}% {fb*100:>7.1f}% {flex:>8.4f} {n:>8d}{marker}")

l_flex = next((flex for term, fa, fb, flex, n in term_results if term == 'l'), None)
l_rank = next((i + 1 for i, (term, *_) in enumerate(term_results) if term == 'l'), None)

# ============================================================
# P-L10b: Per-initial-atom comparison: l-terminal vs non-l-terminal flexibility
# ============================================================
print(f"\n{'='*70}")
print("PER INITIAL ATOM: l-TERMINAL vs NON-l-TERMINAL MODE FLEXIBILITY")
print(f"{'='*70}")
print("Prediction: l-terminal closer to 50/50 than non-l-terminal\n")

print(f"  {'Init':<5s} {'l-term A%':>10s} {'l-term flex':>12s} {'l-term n':>10s} "
      f"{'non-l A%':>10s} {'non-l flex':>12s} {'non-l n':>10s} {'l more flex?':>14s}")
print(f"  {'-'*5} {'-'*10} {'-'*12} {'-'*10} {'-'*10} {'-'*12} {'-'*10} {'-'*14}")

l_more_flex_count = 0
testable_count = 0

pair_results = []
for initial in sorted(atoms_set):
    l_data = init_lterm_mode.get((initial, True))
    nol_data = init_lterm_mode.get((initial, False))
    if not l_data or not nol_data:
        continue
    l_total = l_data.get('A', 0) + l_data.get('B', 0)
    nol_total = nol_data.get('A', 0) + nol_data.get('B', 0)
    if l_total < 20 or nol_total < 20:
        continue

    l_frac_a = l_data.get('A', 0) / l_total
    nol_frac_a = nol_data.get('A', 0) / nol_total
    l_flex = 1.0 - 2.0 * abs(l_frac_a - 0.5)
    nol_flex = 1.0 - 2.0 * abs(nol_frac_a - 0.5)
    testable_count += 1
    if l_flex > nol_flex:
        l_more_flex_count += 1
        verdict = 'YES'
    else:
        verdict = 'no'

    pair_results.append((initial, l_frac_a, l_flex, l_total, nol_frac_a, nol_flex, nol_total, verdict))
    print(f"  {initial:<5s} {l_frac_a*100:>9.1f}% {l_flex:>12.4f} {l_total:>10d} "
          f"{nol_frac_a*100:>9.1f}% {nol_flex:>12.4f} {nol_total:>10d} {verdict:>14s}")

# ============================================================
# P-L10c: Per-MIDDLE compound comparison
# ============================================================
print(f"\n{'='*70}")
print("PER-MIDDLE COMPOUND: l-TERMINAL vs SAME-INITIAL NON-l MIDDLES")
print(f"{'='*70}")
print("(Detailed: for each frequent l-terminal MIDDLE, compare to non-l peers)\n")

# Group MIDDLEs by initial atom
middles_by_init = defaultdict(list)
for mid, counts in middle_mode.items():
    if len(mid) < 2:
        continue
    total = counts.get('A', 0) + counts.get('B', 0)
    if total < 20:
        continue
    frac_a = counts.get('A', 0) / total
    flex = 1.0 - 2.0 * abs(frac_a - 0.5)
    middles_by_init[mid[0]].append((mid, frac_a, flex, total, mid[-1] == 'l'))

for initial in sorted(middles_by_init.keys()):
    entries = middles_by_init[initial]
    l_entries = [(m, fa, fl, n) for m, fa, fl, n, is_l in entries if is_l]
    nol_entries = [(m, fa, fl, n) for m, fa, fl, n, is_l in entries if not is_l]
    if not l_entries or not nol_entries:
        continue

    print(f"\n  {initial}-initial:")
    # Sort l-entries and non-l by flexibility
    all_sorted = sorted(entries, key=lambda x: -x[2])
    for mid, fa, fl, n, is_l in all_sorted:
        marker = ' *L*' if is_l else ''
        print(f"    {mid:<12s} A={fa*100:>5.1f}% flex={fl:.4f} n={n:>5d}{marker}")

# ============================================================
# P-L10d: Comprehensive: ALL terminal atoms, mean flexibility per initial
# ============================================================
print(f"\n{'='*70}")
print("COMPREHENSIVE: MEAN FLEXIBILITY BY TERMINAL ATOM (across initials)")
print(f"{'='*70}")

# (initial, terminal) -> {'A': count, 'B': count}
init_term_mode = defaultdict(Counter)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid or len(mid) < 2:
        continue
    mode = line_mode_map.get((token.folio, token.line))
    if not mode:
        continue
    initial = mid[0]
    terminal = mid[-1]
    if initial not in atoms_set or terminal not in atoms_set:
        continue
    init_term_mode[(initial, terminal)][mode] += 1

# Per terminal atom, compute mean flexibility across initials
term_flexes = defaultdict(list)
for (initial, terminal), counts in init_term_mode.items():
    total = counts.get('A', 0) + counts.get('B', 0)
    if total < 20:
        continue
    frac_a = counts.get('A', 0) / total
    flex = 1.0 - 2.0 * abs(frac_a - 0.5)
    term_flexes[terminal].append(flex)

print(f"\n  {'Term':<5s} {'mean flex':>10s} {'median flex':>12s} {'n_groups':>10s}")
print(f"  {'-'*5} {'-'*10} {'-'*12} {'-'*10}")

comp_results = []
for term in sorted(term_flexes.keys()):
    flexes = term_flexes[term]
    if len(flexes) < 3:
        continue
    mean_f = sum(flexes) / len(flexes)
    sorted_f = sorted(flexes)
    median_f = sorted_f[len(sorted_f) // 2]
    comp_results.append((term, mean_f, median_f, len(flexes)))

comp_results.sort(key=lambda x: -x[1])
for i, (term, mf, medf, ng) in enumerate(comp_results):
    marker = ' <-- l' if term == 'l' else ''
    print(f"  {term:<5s} {mf:>10.4f} {medf:>12.4f} {ng:>10d}{marker}")

# ============================================================
# P-L10e: Does l-terminal correlate with mode-SWITCHING?
# ============================================================
print(f"\n{'='*70}")
print("BONUS: l-TERMINAL FRACTION vs MODE SWITCHING AT PARAGRAPH LEVEL")
print(f"{'='*70}")
print("(If l is a nominalizer, l-rich paragraphs might show more mode switching)\n")

# Get paragraph-level data
para_data = []
for folio in b_folios:
    try:
        paragraphs = decoder.analyze_folio_paragraphs(folio)
        for p in paragraphs:
            if not p.suffix_mode_sequence or len(p.suffix_mode_sequence) < 3:
                continue
            # Count l-terminal tokens in this paragraph
            n_tokens = 0
            n_l_term = 0
            for la in p.lines:
                for t in la.tokens:
                    mid_str = morph.extract(t.word).middle if t.word else None
                    if mid_str and len(mid_str) >= 2:
                        n_tokens += 1
                        if mid_str[-1] == 'l':
                            n_l_term += 1

            if n_tokens < 10:
                continue

            l_frac = n_l_term / n_tokens
            seq = p.suffix_mode_sequence
            changes = sum(1 for i in range(1, len(seq)) if seq[i] != seq[i-1])
            interleave = changes / (len(seq) - 1) if len(seq) > 1 else 0

            para_data.append({
                'l_frac': l_frac,
                'interleave': interleave,
                'n_lines': len(seq),
                'n_tokens': n_tokens
            })
    except Exception:
        pass

if para_data:
    l_fracs = [d['l_frac'] for d in para_data]
    interleaves = [d['interleave'] for d in para_data]
    rho, p = spearman_rho(l_fracs, interleaves)
    print(f"  l-terminal fraction vs mode interleave: rho={rho:+.4f}, p={p:.6f}, n={len(para_data)}")
    print(f"  (Positive = more l -> more mode switching)")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-L10 SUMMARY")
print(f"{'='*70}")

l_rank_val = next((i + 1 for i, (term, *_) in enumerate(term_results) if term == 'l'), None)
l_flex_val = next((flex for term, fa, fb, flex, n in term_results if term == 'l'), None)

print(f"\n  l-terminal global flexibility: {l_flex_val:.4f} (rank {l_rank_val}/{len(term_results)})")
print(f"  Prediction: l has HIGHEST flexibility (rank 1)")

if l_rank_val == 1:
    print(f"  RESULT: CONFIRMED -- l-terminal is the most mode-flexible terminal atom")
elif l_rank_val and l_rank_val <= 3:
    print(f"  RESULT: PARTIAL -- l is top-3 but not #1")
else:
    print(f"  RESULT: FAILED -- l is rank {l_rank_val}")

print(f"\n  Per-initial comparison: l more flexible in {l_more_flex_count}/{testable_count} groups")
if testable_count > 0:
    pct = l_more_flex_count / testable_count * 100
    print(f"  ({pct:.0f}% of testable groups)")
    if pct >= 70:
        print(f"  RESULT: CONFIRMED (>=70% of groups)")
    elif pct >= 50:
        print(f"  RESULT: PARTIAL (50-70%)")
    else:
        print(f"  RESULT: FAILED (<50%)")

if para_data:
    print(f"\n  l-terminal vs mode interleave: rho={rho:+.4f}")
    if rho > 0.10 and p < 0.05:
        print(f"  Mode-switching association: SIGNIFICANT positive")
    elif rho > 0:
        print(f"  Mode-switching association: weak positive (NS)")
    else:
        print(f"  Mode-switching association: absent or negative")
