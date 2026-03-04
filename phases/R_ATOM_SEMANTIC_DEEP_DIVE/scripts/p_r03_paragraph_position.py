"""P-R3: r-terminal MIDDLEs depleted at paragraph-initial, enriched mid-paragraph.

If r = "return/reflux", return flow can't happen before the process starts.
r should be:
- DEPLETED at paragraph-initial positions (Q0)
- ENRICHED at mid-paragraph positions (Q2-Q3) where cycling is active
- Possibly declining at paragraph-final (Q4) as the process winds down

Compare to k-initial (C1384: k should front-load = heating starts first).
Also compare to all terminal atoms for ranking.
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

# ============================================================
# Build paragraph structure
# ============================================================
print("Building paragraph structure...")

# Collect tokens by folio+line
lines_by_folio = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    lines_by_folio[token.folio][token.line].append(w)

# Gallows that mark paragraph starts
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

# Build paragraphs
all_paragraphs = []
for folio in sorted(lines_by_folio.keys()):
    line_keys = sorted(lines_by_folio[folio].keys())
    current_para = []
    for lk in line_keys:
        words = lines_by_folio[folio][lk]
        if is_gallows_initial(words) and current_para:
            all_paragraphs.append((folio, current_para))
            current_para = list(words)
        else:
            current_para.extend(words)
    if current_para:
        all_paragraphs.append((folio, current_para))

paras = [(f, ws) for f, ws in all_paragraphs if len(ws) >= 10]
print(f"  Paragraphs with >=10 tokens: {len(paras)}")

# ============================================================
# P-R3a: r-terminal fraction by paragraph quintile
# ============================================================
print(f"\n{'='*70}")
print("P-R3a: r-TERMINAL FRACTION BY PARAGRAPH BODY QUINTILE")
print(f"{'='*70}")
print("Prediction: Q0 depleted, Q2-Q3 enriched, possibly Q4 declining\n")

# Per-terminal-atom quintile tracking
term_quintile = defaultdict(lambda: defaultdict(int))
quintile_total = defaultdict(int)

for folio, words in paras:
    body = words[1:] if len(words) > 1 else words
    n = len(body)
    if n < 5:
        continue

    for i, w in enumerate(body):
        q = min(int(i / n * 5), 4)
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2:
            continue

        terminal = mid[-1]
        term_quintile[terminal][q] += 1
        quintile_total[q] += 1

# Report r-terminal by quintile
global_r_frac = sum(term_quintile['r'].values()) / sum(quintile_total.values()) if sum(quintile_total.values()) > 0 else 0

print(f"  {'Quintile':<10s} {'r-term':>8s} {'total':>8s} {'fraction':>10s} {'enrichment':>12s}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*10} {'-'*12}")

for q in range(5):
    rc = term_quintile['r'][q]
    tc = quintile_total[q]
    frac = rc / tc if tc > 0 else 0
    enrich = frac / global_r_frac if global_r_frac > 0 else 0
    label = f"Q{q} ({'first' if q == 0 else 'last' if q == 4 else 'mid'})"
    print(f"  {label:<10s} {rc:>8d} {tc:>8d} {frac:>10.4f} {enrich:>11.3f}x")

# Chi-square Q0 vs Q2+Q3
r_q0 = term_quintile['r'][0]
t_q0 = quintile_total[0]
r_mid = term_quintile['r'][2] + term_quintile['r'][3]
t_mid = quintile_total[2] + quintile_total[3]

if t_q0 > 0 and t_mid > 0:
    q0_frac = r_q0 / t_q0
    mid_frac = r_mid / t_mid
    a_val = r_q0
    b_val = t_q0 - r_q0
    c_val = r_mid
    d_val = t_mid - r_mid
    n = a_val + b_val + c_val + d_val
    denom = (a_val + b_val) * (c_val + d_val) * (a_val + c_val) * (b_val + d_val)
    if denom > 0:
        chi2 = (n * (a_val * d_val - b_val * c_val) ** 2) / denom
        z_val = math.sqrt(chi2)
        p_val = 2 * (1 - normal_cdf(z_val))
        print(f"\n  Q0 vs Q2+Q3: {q0_frac:.4f} vs {mid_frac:.4f}")
        print(f"  Ratio: {mid_frac / q0_frac:.3f}x" if q0_frac > 0 else "")
        print(f"  Chi-square: {chi2:.2f}, p={p_val:.6f}")

# ============================================================
# P-R3b: ALL terminal atoms Q0/Q3 ratio (comprehensive ranking)
# ============================================================
print(f"\n{'='*70}")
print("ALL TERMINAL ATOMS: Q0/Q3 ENRICHMENT RANKING")
print(f"{'='*70}")
print("(Who front-loads vs back-loads in paragraphs?)\n")

print(f"  {'Term':<5s} {'Q0':>8s} {'Q3':>8s} {'Q0 frac':>10s} {'Q3 frac':>10s} {'Q3/Q0':>8s} {'shape':>10s}")
print(f"  {'-'*5} {'-'*8} {'-'*8} {'-'*10} {'-'*10} {'-'*8} {'-'*10}")

atom_results = []
for term in sorted(term_quintile.keys()):
    total_for_term = sum(term_quintile[term].values())
    if total_for_term < 100:
        continue
    q0_count = term_quintile[term][0]
    q3_count = term_quintile[term][3]
    q0_frac = q0_count / quintile_total[0] if quintile_total[0] > 0 else 0
    q3_frac = q3_count / quintile_total[3] if quintile_total[3] > 0 else 0
    ratio = q3_frac / q0_frac if q0_frac > 0 else 0

    # Determine shape: front-loaded, back-loaded, or U/inverted-U
    q_fracs = []
    for q in range(5):
        qf = term_quintile[term][q] / quintile_total[q] if quintile_total[q] > 0 else 0
        q_fracs.append(qf)
    mid_avg = sum(q_fracs[1:4]) / 3
    end_avg = (q_fracs[0] + q_fracs[4]) / 2
    if mid_avg > end_avg * 1.1:
        shape = 'INVERTED-U'
    elif end_avg > mid_avg * 1.1:
        shape = 'U-SHAPED'
    elif q_fracs[0] > q_fracs[4] * 1.1:
        shape = 'FRONT'
    elif q_fracs[4] > q_fracs[0] * 1.1:
        shape = 'BACK'
    else:
        shape = 'FLAT'

    atom_results.append((term, q0_count, q3_count, q0_frac, q3_frac, ratio, shape))

atom_results.sort(key=lambda x: -x[5])
for term, q0c, q3c, q0f, q3f, ratio, shape in atom_results:
    marker = ' <-- r' if term == 'r' else ' <-- k' if term == 'k' else ' <-- l' if term == 'l' else ''
    print(f"  {term:<5s} {q0c:>8d} {q3c:>8d} {q0f:>10.4f} {q3f:>10.4f} {ratio:>7.3f}x {shape:>10s}{marker}")

# ============================================================
# P-R3c: r vs k paragraph position gradient (Spearman)
# ============================================================
print(f"\n{'='*70}")
print("P-R3c: r-TERMINAL vs k-INITIAL FRACTION BY PARAGRAPH POSITION")
print(f"{'='*70}")
print("Prediction: k front-loads (heating first), r back-loads (return later)\n")

# Per-paragraph: compute r-terminal and k-atom fractions at each quintile
para_r_gradient = []
para_k_gradient = []

for folio, words in paras:
    body = words[1:] if len(words) > 1 else words
    n = len(body)
    if n < 10:
        continue

    r_by_q = defaultdict(int)
    k_by_q = defaultdict(int)
    total_by_q = defaultdict(int)

    for i, w in enumerate(body):
        q = min(int(i / n * 5), 4)
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2:
            continue
        total_by_q[q] += 1
        if mid[-1] == 'r':
            r_by_q[q] += 1
        if mid[0] == 'k':
            k_by_q[q] += 1

    # Compute normalized position of r vs k tokens
    r_positions = []
    k_positions = []
    for i, w in enumerate(body):
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2:
            continue
        norm = i / (n - 1) if n > 1 else 0.5
        if mid[-1] == 'r':
            r_positions.append(norm)
        if mid[0] == 'k':
            k_positions.append(norm)

    if r_positions:
        para_r_gradient.append(sum(r_positions) / len(r_positions))
    if k_positions:
        para_k_gradient.append(sum(k_positions) / len(k_positions))

if para_r_gradient:
    r_mean_pos = sum(para_r_gradient) / len(para_r_gradient)
    print(f"  r-terminal mean paragraph position: {r_mean_pos:.4f} (n={len(para_r_gradient)} paras)")
if para_k_gradient:
    k_mean_pos = sum(para_k_gradient) / len(para_k_gradient)
    print(f"  k-initial mean paragraph position:  {k_mean_pos:.4f} (n={len(para_k_gradient)} paras)")

if para_r_gradient and para_k_gradient:
    if r_mean_pos > k_mean_pos:
        print(f"  --> k comes first, r comes later (delta={r_mean_pos - k_mean_pos:+.4f})")
        print(f"  SUPPORTS: heating first, return later")
    else:
        print(f"  --> r comes first, k comes later (delta={r_mean_pos - k_mean_pos:+.4f})")
        print(f"  DOES NOT SUPPORT")

# ============================================================
# P-R3d: r-terminal fraction vs line position within paragraph
# ============================================================
print(f"\n{'='*70}")
print("P-R3d: r-TERMINAL FRACTION BY LINE INDEX WITHIN PARAGRAPH")
print(f"{'='*70}")

line_in_para_r = defaultdict(int)
line_in_para_total = defaultdict(int)

for folio in sorted(lines_by_folio.keys()):
    line_keys = sorted(lines_by_folio[folio].keys())
    para_line_idx = 0
    for lk in line_keys:
        words = lines_by_folio[folio][lk]
        if is_gallows_initial(words) and para_line_idx > 0:
            para_line_idx = 0

        for w in words:
            mid = morph.extract(w).middle
            if not mid or len(mid) < 2:
                continue
            line_bin = min(para_line_idx, 6)
            line_in_para_total[line_bin] += 1
            if mid[-1] == 'r':
                line_in_para_r[line_bin] += 1

        para_line_idx += 1

global_r_rate = sum(line_in_para_r.values()) / sum(line_in_para_total.values())
print(f"\n  {'Line':>6s} {'r-term':>8s} {'total':>8s} {'fraction':>10s} {'enrichment':>12s}")
print(f"  {'-'*6} {'-'*8} {'-'*8} {'-'*10} {'-'*12}")
for line in sorted(line_in_para_total.keys()):
    rc = line_in_para_r[line]
    tc = line_in_para_total[line]
    frac = rc / tc if tc > 0 else 0
    enrich = frac / global_r_rate if global_r_rate > 0 else 0
    label = f"L{line}{'+'if line == 6 else ''}"
    print(f"  {label:>6s} {rc:>8d} {tc:>8d} {frac:>10.4f} {enrich:>11.3f}x")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-R3 SUMMARY")
print(f"{'='*70}")

r_result = next((x for x in atom_results if x[0] == 'r'), None)
k_result = next((x for x in atom_results if x[0] == 'k'), None)

if r_result:
    print(f"\n  r-terminal paragraph shape: {r_result[6]}")
    print(f"  r Q3/Q0 ratio: {r_result[5]:.3f}x")
if k_result:
    print(f"  k Q3/Q0 ratio: {k_result[5]:.3f}x")

if r_result and r_result[6] in ('INVERTED-U', 'BACK'):
    print(f"\n  SUPPORTS: r-terminal enriched mid-paragraph (shape={r_result[6]})")
elif r_result and r_result[6] == 'FLAT':
    print(f"\n  NULL: r-terminal has no paragraph gradient")
else:
    print(f"\n  DOES NOT SUPPORT: r-terminal shape is {r_result[6] if r_result else 'unknown'}")

if para_r_gradient and para_k_gradient and r_mean_pos > k_mean_pos:
    print(f"  k-before-r: SUPPORTS (k={k_mean_pos:.4f}, r={r_mean_pos:.4f})")
else:
    print(f"  k-before-r: DOES NOT SUPPORT")
