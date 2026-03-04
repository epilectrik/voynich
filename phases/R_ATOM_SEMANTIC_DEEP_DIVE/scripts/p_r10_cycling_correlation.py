"""P-R10: r-density predicts suffix-mode cycling rate within paragraphs.

If r = "repeat/iterate", then paragraphs with higher r-terminal density
(ar+or tokens / total body tokens) should exhibit MORE suffix-mode
alternation events per unit length.

Pass criterion: Spearman rho > +0.15, p < 0.01.
Also control for or->aiin confound and test per-section.
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


def spearman_rho(x, y):
    n = len(x)
    if n < 5: return 0.0, 1.0
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

# ============================================================
# Build paragraph structure with line-level suffix modes
# ============================================================
print("Building paragraph structure...")

# Get all B folios
b_folios = sorted(set(t.folio for t in tx.currier_b()))

# Build line data: tokens and suffix mode
lines_by_folio = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    lines_by_folio[token.folio][token.line].append(w)

# Get suffix mode per line
line_mode = {}
for folio in b_folios:
    try:
        lines = decoder.analyze_folio_lines(folio)
        for la in lines:
            if la.suffix_mode in ('A', 'B'):
                line_mode[(folio, la.line_id)] = la.suffix_mode
    except Exception:
        pass

# Gallows for paragraph breaks
GALLOWS = {'t', 'k', 'p', 'f'}

def is_gallows_initial(words):
    if not words:
        return False
    first = words[0]
    if first and first[0] in GALLOWS:
        return True
    m = morph.extract(first)
    if m.prefix and m.prefix[0] in GALLOWS:
        return True
    if not m.prefix and m.middle and m.middle[0] in GALLOWS:
        return True
    return False

# Build paragraphs with per-line data
all_paragraphs = []
for folio in sorted(lines_by_folio.keys()):
    line_keys = sorted(lines_by_folio[folio].keys())
    current_lines = []
    for lk in line_keys:
        words = lines_by_folio[folio][lk]
        if is_gallows_initial(words) and current_lines:
            all_paragraphs.append((folio, current_lines))
            current_lines = [(lk, words)]
        else:
            current_lines.append((lk, words))
    if current_lines:
        all_paragraphs.append((folio, current_lines))

print(f"  Total paragraphs: {len(all_paragraphs)}")

# ============================================================
# P-R10a: r-density vs suffix-mode cycling rate
# ============================================================
print(f"\n{'='*70}")
print("P-R10a: r-DENSITY vs SUFFIX-MODE CYCLING RATE")
print(f"{'='*70}")
print("Prediction: rho > +0.15, p < 0.01\n")

para_data = []

for folio, para_lines in all_paragraphs:
    if len(para_lines) < 8:
        continue

    # Skip first line (header), use body lines
    body_lines = para_lines[1:]
    n_body_lines = len(body_lines)

    # Count r-terminal tokens and total tokens in body
    r_count = 0
    total_count = 0
    for lk, words in body_lines:
        for w in words:
            mid = morph.extract(w).middle
            if not mid or len(mid) < 2:
                continue
            total_count += 1
            if mid[-1] == 'r':
                r_count += 1

    if total_count < 10:
        continue

    r_density = r_count / total_count

    # Count suffix-mode switches in body
    modes = []
    for lk, words in body_lines:
        m = line_mode.get((folio, lk))
        if m:
            modes.append(m)

    if len(modes) < 3:
        continue

    switches = sum(1 for i in range(1, len(modes)) if modes[i] != modes[i-1])
    cycling_rate = switches / (len(modes) - 1)

    # Get section for control
    try:
        folio_analysis = decoder.analyze_folio(folio)
        section = folio_analysis.section if folio_analysis else '?'
    except Exception:
        section = '?'

    para_data.append({
        'folio': folio,
        'section': section,
        'n_lines': n_body_lines,
        'r_count': r_count,
        'total': total_count,
        'r_density': r_density,
        'n_modes': len(modes),
        'switches': switches,
        'cycling_rate': cycling_rate,
    })

print(f"  Paragraphs with >=8 lines and >=3 mode readings: {len(para_data)}")

if para_data:
    r_dens = [p['r_density'] for p in para_data]
    cyc_rates = [p['cycling_rate'] for p in para_data]

    rho, p_val = spearman_rho(r_dens, cyc_rates)
    print(f"\n  Spearman rho: {rho:+.4f}")
    print(f"  p-value: {p_val:.6f}")
    print(f"  n: {len(para_data)}")

    if rho > 0.15 and p_val < 0.01:
        print(f"  CONFIRMED: r-density positively correlates with cycling rate")
    elif rho > 0.10 and p_val < 0.05:
        print(f"  PARTIAL: weak positive correlation")
    elif abs(rho) < 0.10:
        print(f"  NULL: no meaningful correlation")
    elif rho < -0.10:
        print(f"  INVERTED: r-density negatively correlates with cycling (opposite of prediction)")

# ============================================================
# P-R10b: Binned analysis for visualization
# ============================================================
print(f"\n{'='*70}")
print("P-R10b: r-DENSITY BINS vs CYCLING RATE")
print(f"{'='*70}")

if para_data:
    # Sort by r-density and bin into quartiles
    sorted_data = sorted(para_data, key=lambda x: x['r_density'])
    n = len(sorted_data)
    bins = [
        ('Q1 (low r)', sorted_data[:n//4]),
        ('Q2', sorted_data[n//4:n//2]),
        ('Q3', sorted_data[n//2:3*n//4]),
        ('Q4 (high r)', sorted_data[3*n//4:]),
    ]

    print(f"\n  {'Bin':<15s} {'n':>6s} {'mean r%':>10s} {'mean cyc':>10s} {'mean switches':>14s}")
    print(f"  {'-'*15} {'-'*6} {'-'*10} {'-'*10} {'-'*14}")

    for label, group in bins:
        n_g = len(group)
        mean_r = sum(p['r_density'] for p in group) / n_g * 100
        mean_cyc = sum(p['cycling_rate'] for p in group) / n_g
        mean_sw = sum(p['switches'] for p in group) / n_g
        print(f"  {label:<15s} {n_g:>6d} {mean_r:>9.2f}% {mean_cyc:>10.4f} {mean_sw:>14.2f}")

# ============================================================
# P-R10c: Control for section effects
# ============================================================
print(f"\n{'='*70}")
print("P-R10c: SECTION-CONTROLLED CORRELATION")
print(f"{'='*70}")

if para_data:
    sections = defaultdict(list)
    for p in para_data:
        sections[p['section']].append(p)

    print(f"\n  {'Section':<10s} {'n':>6s} {'rho':>8s} {'p':>10s}")
    print(f"  {'-'*10} {'-'*6} {'-'*8} {'-'*10}")

    for sec in sorted(sections.keys()):
        group = sections[sec]
        if len(group) < 10:
            continue
        r_d = [p['r_density'] for p in group]
        c_r = [p['cycling_rate'] for p in group]
        rho_s, p_s = spearman_rho(r_d, c_r)
        print(f"  {sec:<10s} {len(group):>6d} {rho_s:>+7.4f} {p_s:>10.6f}")

# ============================================================
# P-R10d: ar-density vs or-density separate effects
# ============================================================
print(f"\n{'='*70}")
print("P-R10d: ar-DENSITY vs or-DENSITY SEPARATE EFFECTS")
print(f"{'='*70}")

para_data_split = []

for folio, para_lines in all_paragraphs:
    if len(para_lines) < 8:
        continue

    body_lines = para_lines[1:]

    ar_count = 0
    or_count = 0
    total_count = 0
    for lk, words in body_lines:
        for w in words:
            mid = morph.extract(w).middle
            if not mid or len(mid) < 2:
                continue
            total_count += 1
            if mid == 'ar':
                ar_count += 1
            elif mid == 'or':
                or_count += 1

    if total_count < 10:
        continue

    modes = []
    for lk, words in body_lines:
        m = line_mode.get((folio, lk))
        if m:
            modes.append(m)

    if len(modes) < 3:
        continue

    switches = sum(1 for i in range(1, len(modes)) if modes[i] != modes[i-1])
    cycling_rate = switches / (len(modes) - 1)

    para_data_split.append({
        'ar_density': ar_count / total_count,
        'or_density': or_count / total_count,
        'r_density': (ar_count + or_count) / total_count,
        'cycling_rate': cycling_rate,
    })

if para_data_split:
    ar_d = [p['ar_density'] for p in para_data_split]
    or_d = [p['or_density'] for p in para_data_split]
    cyc = [p['cycling_rate'] for p in para_data_split]

    rho_ar, p_ar = spearman_rho(ar_d, cyc)
    rho_or, p_or = spearman_rho(or_d, cyc)

    print(f"\n  ar-density vs cycling: rho={rho_ar:+.4f}, p={p_ar:.6f}")
    print(f"  or-density vs cycling: rho={rho_or:+.4f}, p={p_or:.6f}")

    if rho_ar > rho_or + 0.05:
        print(f"\n  ar drives cycling more than or")
    elif rho_or > rho_ar + 0.05:
        print(f"\n  or drives cycling more than ar")
    else:
        print(f"\n  ar and or contribute similarly")

# ============================================================
# P-R10e: Compare r-density to OTHER atom densities
# ============================================================
print(f"\n{'='*70}")
print("P-R10e: ALL TERMINAL ATOMS -- DENSITY vs CYCLING RATE")
print(f"{'='*70}")
print("Does r predict cycling better than other atoms?\n")

# Compute density for each terminal atom
atom_densities = defaultdict(list)

for folio, para_lines in all_paragraphs:
    if len(para_lines) < 8:
        continue

    body_lines = para_lines[1:]

    atom_counts = defaultdict(int)
    total = 0
    for lk, words in body_lines:
        for w in words:
            mid = morph.extract(w).middle
            if not mid or len(mid) < 2:
                continue
            total += 1
            terminal = mid[-1]
            atom_counts[terminal] += 1

    if total < 10:
        continue

    modes = []
    for lk, words in body_lines:
        m = line_mode.get((folio, lk))
        if m:
            modes.append(m)

    if len(modes) < 3:
        continue

    switches = sum(1 for i in range(1, len(modes)) if modes[i] != modes[i-1])
    cycling_rate = switches / (len(modes) - 1)

    for atom in atom_counts:
        atom_densities[atom].append((atom_counts[atom] / total, cycling_rate))

print(f"  {'Atom':<5s} {'n':>6s} {'rho':>8s} {'p':>10s} {'signal':>10s}")
print(f"  {'-'*5} {'-'*6} {'-'*8} {'-'*10} {'-'*10}")

atom_corrs = []
for atom in sorted(atom_densities.keys()):
    data = atom_densities[atom]
    if len(data) < 20:
        continue
    dens = [d[0] for d in data]
    cycs = [d[1] for d in data]
    rho_a, p_a = spearman_rho(dens, cycs)
    atom_corrs.append((atom, len(data), rho_a, p_a))

atom_corrs.sort(key=lambda x: -x[2])
for atom, n_a, rho_a, p_a in atom_corrs:
    sig = 'YES' if p_a < 0.01 else 'weak' if p_a < 0.05 else ''
    marker = ' <-- r' if atom == 'r' else ' <-- l' if atom == 'l' else ' <-- k' if atom == 'k' else ''
    print(f"  {atom:<5s} {n_a:>6d} {rho_a:>+7.4f} {p_a:>10.6f} {sig:>10s}{marker}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-R10 SUMMARY")
print(f"{'='*70}")

if para_data:
    rho_final, p_final = spearman_rho(
        [p['r_density'] for p in para_data],
        [p['cycling_rate'] for p in para_data]
    )
    print(f"\n  r-density vs cycling rate: rho={rho_final:+.4f}, p={p_final:.6f}")

    if rho_final > 0.15 and p_final < 0.01:
        print(f"  CONFIRMED: r predicts paragraph cycling -> upgrade to SOLID candidate")
    elif rho_final > 0.10 and p_final < 0.05:
        print(f"  PARTIAL: weak positive signal -> PLAUSIBLE confirmed")
    elif abs(rho_final) < 0.10:
        print(f"  NULL: r does not predict cycling -> PLAUSIBLE ceiling")
    else:
        print(f"  INVERTED: opposite to prediction")

    # r's rank among all atoms
    r_rank = next((i+1 for i, (a, n, r, p) in enumerate(atom_corrs) if a == 'r'), None)
    if r_rank:
        print(f"  r rank among all atoms for cycling prediction: {r_rank}/{len(atom_corrs)}")
