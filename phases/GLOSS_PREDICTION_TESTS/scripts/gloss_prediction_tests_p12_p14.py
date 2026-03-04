"""Phase 495c: Crazy-expert gloss predictions P12, P13, P14.

P12: h-terminal MIDDLEs enriched in CHSH lane vs QO lane
P13: e-initial fraction anticorrelates with AXM self-transition at folio level
P14: y-terminal MIDDLEs enriched at paragraph-final lines
"""

import json
import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology

PROJECT = Path(__file__).resolve().parent

# ================================================================
# HELPERS
# ================================================================

def normal_cdf(z):
    if z < -8: return 0.0
    if z > 8: return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1 if z >= 0 else -1
    z_abs = abs(z)
    t = 1.0 / (1.0 + p * z_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z_abs * z_abs / 2.0)
    return 0.5 * (1.0 + sign * y)


def chi2_2x2(a, b, c, d):
    n = a + b + c + d
    if n == 0:
        return 0.0, 1.0
    exp = [[(a+b)*(a+c)/n, (a+b)*(b+d)/n], [(c+d)*(a+c)/n, (c+d)*(b+d)/n]]
    chi2 = 0.0
    for obs, exp_row in zip([[a,b],[c,d]], exp):
        for o, e in zip(obs, exp_row):
            if e > 0:
                chi2 += (o - e)**2 / e
    z = ((chi2 / 1.0)**(1.0/3.0) - (1 - 2.0/9.0)) / math.sqrt(2.0/9.0)
    p = 1.0 - normal_cdf(z)
    return chi2, p


def spearman_rho(x, y):
    """Spearman rank correlation."""
    n = len(x)
    if n < 3:
        return 0.0, 1.0
    def rankdata(vals):
        indexed = sorted(enumerate(vals), key=lambda t: t[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n and indexed[j][1] == indexed[i][1]:
                j += 1
            avg_rank = (i + j - 1) / 2.0 + 1
            for k in range(i, j):
                ranks[indexed[k][0]] = avg_rank
            i = j
        return ranks
    rx = rankdata(x)
    ry = rankdata(y)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = math.sqrt(sum((rx[i] - mean_rx)**2 for i in range(n)))
    den_y = math.sqrt(sum((ry[i] - mean_ry)**2 for i in range(n)))
    if den_x == 0 or den_y == 0:
        return 0.0, 1.0
    rho = num / (den_x * den_y)
    # t-test for significance
    if abs(rho) >= 1.0:
        return rho, 0.0
    t_stat = rho * math.sqrt((n - 2) / (1 - rho**2))
    # Approximate p-value from t-distribution using normal for large n
    p = 2 * (1 - normal_cdf(abs(t_stat)))
    return rho, p


# ================================================================
# LOAD DATA
# ================================================================
tx = Transcript()
morph = Morphology()

# Lane classification (from BTokenAnalysis._get_prefix_lane)
LANE_MAP = {
    'qo': 'QO', 'ok': 'QO', 'ot': 'QO', 'o': 'QO',
    'ko': 'QO', 'to': 'QO', 'po': 'QO',
    'ch': 'CHSH', 'sh': 'CHSH', 'lsh': 'CHSH',
}

# Build all B tokens with morphology
all_b_tokens = []
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    mid = m.middle if m.middle else ''
    suf = m.suffix if m.suffix else ''
    pfx = m.prefix if m.prefix else ''
    tok_data = {
        'word': w, 'folio': token.folio, 'line': token.line,
        'middle': mid, 'prefix': pfx, 'suffix': suf,
        'section': token.section,
        'par_initial': token.par_initial,
        'par_final': token.par_final,
        'line_initial': token.line_initial,
        'line_final': token.line_final,
    }
    all_b_tokens.append(tok_data)

print(f"Currier B tokens: {len(all_b_tokens)}")


# ================================================================
# P12: h-TERMINAL MIDDLEs IN CHSH vs QO LANE
# ================================================================
print(f"\n{'='*70}")
print("P12: h-TERMINAL MIDDLEs IN CHSH vs QO LANE")
print(f"{'='*70}")

chsh_h_count = 0
chsh_nonhcount = 0
qo_h_count = 0
qo_nonh_count = 0

# Per-section tracking
sec_lane = defaultdict(lambda: {'chsh_h': 0, 'chsh_nh': 0, 'qo_h': 0, 'qo_nh': 0})

for t in all_b_tokens:
    pfx = t['prefix']
    mid = t['middle']
    if not mid or not pfx:
        continue
    lane = LANE_MAP.get(pfx, None)
    if lane is None:
        continue
    is_h_terminal = mid.endswith('h')
    sec = t['section']
    if lane == 'CHSH':
        if is_h_terminal:
            chsh_h_count += 1
            sec_lane[sec]['chsh_h'] += 1
        else:
            chsh_nonhcount += 1
            sec_lane[sec]['chsh_nh'] += 1
    elif lane == 'QO':
        if is_h_terminal:
            qo_h_count += 1
            sec_lane[sec]['qo_h'] += 1
        else:
            qo_nonh_count += 1
            sec_lane[sec]['qo_nh'] += 1

chsh_total = chsh_h_count + chsh_nonhcount
qo_total = qo_h_count + qo_nonh_count
chsh_h_rate = chsh_h_count / chsh_total if chsh_total else 0
qo_h_rate = qo_h_count / qo_total if qo_total else 0

print(f"\nCHSH lane tokens: {chsh_total} ({chsh_h_count} h-terminal)")
print(f"QO lane tokens:   {qo_total} ({qo_h_count} h-terminal)")

print(f"\nh-terminal MIDDLE rate:")
print(f"  CHSH: {chsh_h_count}/{chsh_total} = {chsh_h_rate:.4f}")
print(f"  QO:   {qo_h_count}/{qo_total} = {qo_h_rate:.4f}")
ratio_12 = chsh_h_rate / qo_h_rate if qo_h_rate > 0 else float('inf')
print(f"  CHSH/QO ratio: {ratio_12:.3f}x")

chi2_12, p_12 = chi2_2x2(chsh_h_count, chsh_nonhcount, qo_h_count, qo_nonh_count)
print(f"  Chi2={chi2_12:.3f}, p={p_12:.6f}")

if ratio_12 > 1.0 and p_12 < 0.05:
    print(f"  RESULT: CONFIRMED - h-terminal MIDDLEs enriched in CHSH lane")
elif ratio_12 < 1.0 and p_12 < 0.05:
    print(f"  RESULT: INVERTED - h-terminal MIDDLEs depleted in CHSH lane")
else:
    print(f"  RESULT: NOT SIGNIFICANT")

# Section control
print(f"\nSection breakdown:")
for sec in sorted(sec_lane.keys()):
    d = sec_lane[sec]
    ct = d['chsh_h'] + d['chsh_nh']
    qt = d['qo_h'] + d['qo_nh']
    if ct > 0 and qt > 0:
        cr = d['chsh_h'] / ct
        qr = d['qo_h'] / qt
        rat = cr / qr if qr > 0 else float('inf')
        print(f"  {sec:5s}  CHSH={cr:.4f} QO={qr:.4f} ratio={rat:.3f}x (CHSH:{ct} QO:{qt})")

# Top h-terminal MIDDLEs by lane
print(f"\nTop h-terminal MIDDLEs in CHSH:")
chsh_h_middles = Counter()
qo_h_middles = Counter()
for t in all_b_tokens:
    pfx = t['prefix']
    mid = t['middle']
    if not mid or not pfx or not mid.endswith('h'):
        continue
    lane = LANE_MAP.get(pfx, None)
    if lane == 'CHSH':
        chsh_h_middles[mid] += 1
    elif lane == 'QO':
        qo_h_middles[mid] += 1

for mid, cnt in chsh_h_middles.most_common(10):
    qcnt = qo_h_middles.get(mid, 0)
    print(f"  {mid:<12s} CHSH={cnt:>5d} QO={qcnt:>5d}")


# ================================================================
# P13: e-INITIAL FRACTION vs AXM SELF-TRANSITION AT FOLIO LEVEL
# ================================================================
print(f"\n{'='*70}")
print("P13: e-INITIAL / k-INITIAL FRACTION vs AXM SELF-TRANSITION")
print(f"{'='*70}")

# Load AXM data
with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
          'axm_residual_decomposition.json', encoding='utf-8') as f:
    axm_data = json.load(f)
folio_axm = {f: d['axm_self'] for f, d in axm_data['folio_data'].items()}
folio_section = {f: d['section'] for f, d in axm_data['folio_data'].items()}

# Compute per-folio atom-initial fractions
folio_e_count = Counter()
folio_k_count = Counter()
folio_total = Counter()

for t in all_b_tokens:
    f = t['folio']
    mid = t['middle']
    if not mid:
        continue
    folio_total[f] += 1
    if mid.startswith('e'):
        folio_e_count[f] += 1
    if mid.startswith('k'):
        folio_k_count[f] += 1

# Build arrays for folios with AXM data
folios_with_axm = [f for f in folio_axm if folio_total[f] >= 50]
e_fracs = [folio_e_count[f] / folio_total[f] for f in folios_with_axm]
k_fracs = [folio_k_count[f] / folio_total[f] for f in folios_with_axm]
axm_vals = [folio_axm[f] for f in folios_with_axm]
sections = [folio_section.get(f, '?') for f in folios_with_axm]

print(f"\nFolios with AXM data: {len(folios_with_axm)}")

rho_e, p_e = spearman_rho(e_fracs, axm_vals)
rho_k, p_k = spearman_rho(k_fracs, axm_vals)

# e/k ratio
ek_ratios = [e_fracs[i] / k_fracs[i] if k_fracs[i] > 0 else 0
             for i in range(len(folios_with_axm))]
rho_ek, p_ek = spearman_rho(ek_ratios, axm_vals)

print(f"\nSpearman correlations with AXM self-transition:")
print(f"  e-initial fraction: rho={rho_e:.4f}, p={p_e:.6f}")
print(f"  k-initial fraction: rho={rho_k:.4f}, p={p_k:.6f}")
print(f"  e/k ratio:          rho={rho_ek:.4f}, p={p_ek:.6f}")

# Prediction check
if rho_e < 0 and p_e < 0.05:
    print(f"\n  e-initial CONFIRMED: negative correlation as predicted")
elif rho_e > 0 and p_e < 0.05:
    print(f"\n  e-initial INVERTED: positive correlation (opposite of prediction)")
else:
    print(f"\n  e-initial NOT SIGNIFICANT")

if rho_k > 0 and p_k < 0.05:
    print(f"  k-initial CONFIRMED: positive correlation as predicted")
elif rho_k < 0 and p_k < 0.05:
    print(f"  k-initial INVERTED: negative correlation (opposite of prediction)")
else:
    print(f"  k-initial NOT SIGNIFICANT")

# Section-controlled: within each section
print(f"\nWithin-section correlations:")
for sec in sorted(set(sections)):
    idx = [i for i, s in enumerate(sections) if s == sec]
    if len(idx) < 5:
        continue
    sec_e = [e_fracs[i] for i in idx]
    sec_k = [k_fracs[i] for i in idx]
    sec_axm = [axm_vals[i] for i in idx]
    r_e, pe = spearman_rho(sec_e, sec_axm)
    r_k, pk = spearman_rho(sec_k, sec_axm)
    print(f"  {sec:5s} (n={len(idx):>2d}): e rho={r_e:+.4f} p={pe:.4f} | k rho={r_k:+.4f} p={pk:.4f}")

# Compare other atoms for specificity
print(f"\nComparison: other atom-initial fractions vs AXM:")
for atom in ['a', 'o', 'd', 'h']:
    atom_fracs = [sum(1 for t in all_b_tokens if t['folio'] == f and t['middle'] and t['middle'].startswith(atom))
                  / folio_total[f] for f in folios_with_axm]
    r_a, p_a = spearman_rho(atom_fracs, axm_vals)
    print(f"  {atom}-initial: rho={r_a:+.4f}, p={p_a:.6f}")


# ================================================================
# P14: y-TERMINAL MIDDLEs AT PARAGRAPH-FINAL LINES
# ================================================================
print(f"\n{'='*70}")
print("P14: y-TERMINAL MIDDLEs AT PARAGRAPH-FINAL LINES")
print(f"{'='*70}")

# Group tokens by (folio, line) to identify paragraph structure
lines_by_key = defaultdict(list)
for t in all_b_tokens:
    key = (t['folio'], t['line'])
    lines_by_key[key].append(t)

# Classify lines as par-final, par-initial, or medial
# A line is par-final if ANY token on it has par_final=True
# A line is par-initial if ANY token on it has par_initial=True
par_final_y = 0
par_final_nony = 0
par_medial_y = 0
par_medial_nony = 0
par_initial_y = 0
par_initial_nony = 0

# Also track without -am suffix tokens
par_final_y_noam = 0
par_final_nony_noam = 0
par_medial_y_noam = 0
par_medial_nony_noam = 0

# Section tracking
sec_par = defaultdict(lambda: {'fy': 0, 'fny': 0, 'my': 0, 'mny': 0})

for key, toks in lines_by_key.items():
    is_par_final = any(t['par_final'] for t in toks)
    is_par_initial = any(t['par_initial'] for t in toks)

    # Skip if both (single-line paragraphs)
    if is_par_final and is_par_initial:
        continue

    sec = toks[0]['section'] if toks else ''

    for t in toks:
        mid = t['middle']
        suf = t['suffix']
        if not mid:
            continue
        is_y_terminal = mid.endswith('y')

        if is_par_final:
            if is_y_terminal:
                par_final_y += 1
                sec_par[sec]['fy'] += 1
            else:
                par_final_nony += 1
                sec_par[sec]['fny'] += 1
            # Without -am
            if suf != 'am':
                if is_y_terminal:
                    par_final_y_noam += 1
                else:
                    par_final_nony_noam += 1
        elif is_par_initial:
            if is_y_terminal:
                par_initial_y += 1
            else:
                par_initial_nony += 1
        else:
            # Medial
            if is_y_terminal:
                par_medial_y += 1
                sec_par[sec]['my'] += 1
            else:
                par_medial_nony += 1
                sec_par[sec]['mny'] += 1
            # Without -am
            if suf != 'am':
                if is_y_terminal:
                    par_medial_y_noam += 1
                else:
                    par_medial_nony_noam += 1

# Final vs medial
pf_total = par_final_y + par_final_nony
pm_total = par_medial_y + par_medial_nony
pi_total = par_initial_y + par_initial_nony
pf_rate = par_final_y / pf_total if pf_total else 0
pm_rate = par_medial_y / pm_total if pm_total else 0
pi_rate = par_initial_y / pi_total if pi_total else 0

print(f"\ny-terminal MIDDLE rate by paragraph position:")
print(f"  Par-initial: {par_initial_y}/{pi_total} = {pi_rate:.4f}")
print(f"  Par-medial:  {par_medial_y}/{pm_total} = {pm_rate:.4f}")
print(f"  Par-final:   {par_final_y}/{pf_total} = {pf_rate:.4f}")
ratio_14 = pf_rate / pm_rate if pm_rate > 0 else float('inf')
print(f"  Final/Medial ratio: {ratio_14:.3f}x")

chi2_14, p_14 = chi2_2x2(par_final_y, par_final_nony, par_medial_y, par_medial_nony)
print(f"  Chi2={chi2_14:.3f}, p={p_14:.6f}")

if ratio_14 > 1.0 and p_14 < 0.05:
    print(f"  RESULT: CONFIRMED - y-terminal MIDDLEs enriched at paragraph-final")
elif ratio_14 < 1.0 and p_14 < 0.05:
    print(f"  RESULT: INVERTED - y-terminal MIDDLEs depleted at paragraph-final")
else:
    print(f"  RESULT: NOT SIGNIFICANT")

# Without -am control
pf_noam_total = par_final_y_noam + par_final_nony_noam
pm_noam_total = par_medial_y_noam + par_medial_nony_noam
pf_noam_rate = par_final_y_noam / pf_noam_total if pf_noam_total else 0
pm_noam_rate = par_medial_y_noam / pm_noam_total if pm_noam_total else 0
ratio_14_noam = pf_noam_rate / pm_noam_rate if pm_noam_rate > 0 else float('inf')
chi2_14_noam, p_14_noam = chi2_2x2(par_final_y_noam, par_final_nony_noam,
                                     par_medial_y_noam, par_medial_nony_noam)

print(f"\nAfter excluding -am suffix tokens:")
print(f"  Par-medial:  {par_medial_y_noam}/{pm_noam_total} = {pm_noam_rate:.4f}")
print(f"  Par-final:   {par_final_y_noam}/{pf_noam_total} = {pf_noam_rate:.4f}")
print(f"  Final/Medial ratio: {ratio_14_noam:.3f}x")
print(f"  Chi2={chi2_14_noam:.3f}, p={p_14_noam:.6f}")

# Section control
print(f"\nSection breakdown (final vs medial, y-terminal rate):")
for sec in sorted(sec_par.keys()):
    d = sec_par[sec]
    ft = d['fy'] + d['fny']
    mt = d['my'] + d['mny']
    if ft > 10 and mt > 10:
        fr = d['fy'] / ft
        mr = d['my'] / mt
        rat = fr / mr if mr > 0 else float('inf')
        print(f"  {sec:5s}  final={fr:.4f} medial={mr:.4f} ratio={rat:.3f}x (F:{ft} M:{mt})")

# Also check n-terminal for comparison (should show opposite per C1383)
par_final_n = sum(1 for t in all_b_tokens
                  if t['middle'] and t['middle'].endswith('n')
                  and any(t2['par_final'] for t2 in lines_by_key[(t['folio'], t['line'])])
                  and not (any(t2['par_final'] for t2 in lines_by_key[(t['folio'], t['line'])])
                           and any(t2['par_initial'] for t2 in lines_by_key[(t['folio'], t['line'])])))
# Simplified: just count n-terminal at par-final vs par-medial
n_final = 0
n_final_total = 0
n_medial = 0
n_medial_total = 0
for key, toks in lines_by_key.items():
    is_pf = any(t['par_final'] for t in toks)
    is_pi = any(t['par_initial'] for t in toks)
    if is_pf and is_pi:
        continue
    for t in toks:
        mid = t['middle']
        if not mid:
            continue
        is_n_term = mid.endswith('n')
        if is_pf:
            n_final_total += 1
            if is_n_term:
                n_final += 1
        elif not is_pi:
            n_medial_total += 1
            if is_n_term:
                n_medial += 1

nf_rate = n_final / n_final_total if n_final_total else 0
nm_rate = n_medial / n_medial_total if n_medial_total else 0
print(f"\nComparison: n-terminal at paragraph positions (C1383 check):")
print(f"  Par-medial:  {n_medial}/{n_medial_total} = {nm_rate:.4f}")
print(f"  Par-final:   {n_final}/{n_final_total} = {nf_rate:.4f}")
print(f"  Final/Medial ratio: {nf_rate/nm_rate:.3f}x" if nm_rate > 0 else "  N/A")


# ================================================================
# SUMMARY
# ================================================================
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")

p12_label = "CONFIRMED" if (ratio_12 > 1.0 and p_12 < 0.05) else \
            "INVERTED" if (ratio_12 < 1.0 and p_12 < 0.05) else "NOT SIGNIFICANT"
print(f"\nP12 (h-term CHSH enrichment): {p12_label} (CHSH/QO={ratio_12:.3f}x, p={p_12:.6f})")

p13_e = "CONFIRMED" if (rho_e < 0 and p_e < 0.05) else \
        "INVERTED" if (rho_e > 0 and p_e < 0.05) else "NOT SIGNIFICANT"
p13_k = "CONFIRMED" if (rho_k > 0 and p_k < 0.05) else \
        "INVERTED" if (rho_k < 0 and p_k < 0.05) else "NOT SIGNIFICANT"
print(f"P13 (e vs AXM):              e: {p13_e} (rho={rho_e:+.4f}, p={p_e:.6f})")
print(f"     (k vs AXM):             k: {p13_k} (rho={rho_k:+.4f}, p={p_k:.6f})")

p14_label = "CONFIRMED" if (ratio_14 > 1.0 and p_14 < 0.05) else \
            "INVERTED" if (ratio_14 < 1.0 and p_14 < 0.05) else "NOT SIGNIFICANT"
print(f"P14 (y-term par-final):      {p14_label} (final/medial={ratio_14:.3f}x, p={p_14:.6f})")
