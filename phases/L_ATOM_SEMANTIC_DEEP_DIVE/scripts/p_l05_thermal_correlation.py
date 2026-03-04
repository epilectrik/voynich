"""P-L5: l-atom fraction correlates with THERMAL line fraction at paragraph level.

If l = "level" (maintained thermal state), lines with more THERMAL content
should use more l-atoms. Test at LINE level within paragraphs.
Prediction: Spearman rho > +0.30.
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

# Load section data
with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
          'axm_residual_decomposition.json', encoding='utf-8') as f:
    axm_data = json.load(f)
folio_section = {f: d['section'] for f, d in axm_data['folio_data'].items()}

# ============================================================
# Build per-line data: l-atom fraction and THERMAL fraction
# ============================================================

# Collect tokens by folio+line
lines = defaultdict(list)  # (folio, line) -> [word, ...]
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    lines[(token.folio, token.line)].append(w)

print(f"Total lines: {len(lines)}")

# For each line, compute l-fraction and THERMAL-fraction
line_data = []  # (folio, line, l_frac, thermal_frac, n_tokens, section)

for (folio, line_id), words in lines.items():
    if len(words) < 3:  # skip very short lines
        continue
    sec = folio_section.get(folio)
    if not sec:
        continue

    n = 0
    l_count = 0
    thermal_count = 0

    for w in words:
        mid = morph.extract(w).middle
        if not mid:
            continue
        n += 1

        # l-atom presence
        if 'l' in mid:
            l_count += 1

        # THERMAL category
        analysis = decoder.analyze_token(w)
        if analysis.operational_category == 'THERMAL':
            thermal_count += 1

    if n >= 3:
        line_data.append((folio, line_id, l_count / n, thermal_count / n, n, sec))

print(f"Lines with >=3 classified tokens: {len(line_data)}")

# ============================================================
# P-L5: Line-level correlation between l-fraction and THERMAL-fraction
# ============================================================
print(f"\n{'='*70}")
print("P-L5: l-ATOM FRACTION vs THERMAL FRACTION (line level)")
print(f"{'='*70}")
print("Prediction: Spearman rho > +0.30\n")

l_fracs = [d[2] for d in line_data]
th_fracs = [d[3] for d in line_data]

rho, p = spearman_rho(l_fracs, th_fracs)
print(f"  Global: rho={rho:+.4f}, p={p:.6f}, n={len(line_data)}")

# Within-section
print(f"\n  Within-section:")
for sec in sorted(set(d[5] for d in line_data)):
    sec_data = [d for d in line_data if d[5] == sec]
    if len(sec_data) < 20:
        continue
    sl = [d[2] for d in sec_data]
    st = [d[3] for d in sec_data]
    sr, sp = spearman_rho(sl, st)
    print(f"    {sec} (n={len(sec_data):>4d}): rho={sr:+.4f} p={sp:.6f}")

# ============================================================
# Also test: l-fraction vs ALL categories (comprehensive)
# ============================================================
print(f"\n{'='*70}")
print("COMPREHENSIVE: l-ATOM FRACTION vs EACH CATEGORY FRACTION (line level)")
print(f"{'='*70}")

# Recompute with all categories per line
line_cat_data = defaultdict(list)  # category -> list of fractions per line, aligned with l_fracs

all_categories = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                  'TRANSITION', 'MARKING', 'MONITORING']

# Rebuild with all categories
line_data2 = []
for (folio, line_id), words in lines.items():
    if len(words) < 3:
        continue
    sec = folio_section.get(folio)
    if not sec:
        continue

    n = 0
    l_count = 0
    cat_counts = Counter()

    for w in words:
        mid = morph.extract(w).middle
        if not mid:
            continue
        n += 1
        if 'l' in mid:
            l_count += 1
        analysis = decoder.analyze_token(w)
        if analysis.operational_category:
            cat_counts[analysis.operational_category] += 1

    if n >= 3:
        line_data2.append({
            'folio': folio, 'line': line_id, 'sec': sec, 'n': n,
            'l_frac': l_count / n,
            **{cat: cat_counts.get(cat, 0) / n for cat in all_categories}
        })

l_fracs2 = [d['l_frac'] for d in line_data2]

print(f"\n  {'Category':<16s} {'rho':>8s} {'p':>10s} {'direction':>12s}")
print(f"  {'-'*16} {'-'*8} {'-'*10} {'-'*12}")

results = []
for cat in all_categories:
    cat_fracs = [d[cat] for d in line_data2]
    r, p = spearman_rho(l_fracs2, cat_fracs)
    results.append((cat, r, p))

results.sort(key=lambda x: -x[1])
for cat, r, p in results:
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    direction = 'positive' if r > 0.05 else 'negative' if r < -0.05 else 'neutral'
    marker = ' <-- predicted' if cat == 'THERMAL' else ''
    print(f"  {cat:<16s} {r:>+8.4f} {p:>10.6f} {direction:>12s} {sig}{marker}")

# ============================================================
# Also: l-fraction vs k-atom fraction at LINE level
# ============================================================
print(f"\n{'='*70}")
print("l-ATOM vs k-ATOM FRACTION (line level)")
print(f"{'='*70}")
print("(Testing whether the folio-level {k,l} cluster holds at line level)\n")

# Recompute with k-atom
line_k_data = []
for (folio, line_id), words in lines.items():
    if len(words) < 3:
        continue
    sec = folio_section.get(folio)
    if not sec:
        continue

    n = 0
    l_count = 0
    k_count = 0

    for w in words:
        mid = morph.extract(w).middle
        if not mid:
            continue
        n += 1
        if 'l' in mid:
            l_count += 1
        if 'k' in mid:
            k_count += 1

    if n >= 3:
        line_k_data.append((l_count / n, k_count / n, sec))

l_line = [d[0] for d in line_k_data]
k_line = [d[1] for d in line_k_data]
rho_lk, p_lk = spearman_rho(l_line, k_line)
print(f"  Global l vs k: rho={rho_lk:+.4f}, p={p_lk:.6f}, n={len(line_k_data)}")

# Within-section
print(f"\n  Within-section:")
for sec in sorted(set(d[2] for d in line_k_data)):
    sec_d = [d for d in line_k_data if d[2] == sec]
    if len(sec_d) < 20:
        continue
    sl = [d[0] for d in sec_d]
    sk = [d[1] for d in sec_d]
    sr, sp = spearman_rho(sl, sk)
    print(f"    {sec} (n={len(sec_d):>4d}): rho={sr:+.4f} p={sp:.6f}")

# ============================================================
# ALSO: l-fraction vs ALL atoms at line level (comprehensive ranking)
# ============================================================
print(f"\n{'='*70}")
print("l-ATOM vs ALL OTHER ATOMS (line-level correlation ranking)")
print(f"{'='*70}")

atoms = 'a d e h k o n i m y c p f s t r q'.split()

atom_line_data = defaultdict(list)
for (folio, line_id), words in lines.items():
    if len(words) < 3:
        continue
    n = 0
    l_count = 0
    atom_counts = Counter()
    for w in words:
        mid = morph.extract(w).middle
        if not mid:
            continue
        n += 1
        if 'l' in mid:
            l_count += 1
        for ch in set(mid):
            if ch in 'adehkonimycpfstrlq':
                atom_counts[ch] += 1
    if n >= 3:
        for atom in atoms:
            atom_line_data[atom].append((l_count / n, atom_counts.get(atom, 0) / n))

print(f"\n  {'Atom':<5s} {'rho vs l':>10s} {'p':>10s} {'direction':>12s}")
print(f"  {'-'*5} {'-'*10} {'-'*10} {'-'*12}")

atom_results = []
for atom in atoms:
    data = atom_line_data[atom]
    la = [d[0] for d in data]
    aa = [d[1] for d in data]
    r, p = spearman_rho(la, aa)
    atom_results.append((atom, r, p))

atom_results.sort(key=lambda x: -x[1])
for atom, r, p in atom_results:
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    direction = 'positive' if r > 0.05 else 'negative' if r < -0.05 else 'neutral'
    marker = ' <-- k' if atom == 'k' else ''
    print(f"  {atom:<5s} {r:>+10.4f} {p:>10.6f} {direction:>12s} {sig}{marker}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-L5 SUMMARY")
print(f"{'='*70}")
print(f"\n  l vs THERMAL (line-level): rho={rho:+.4f}, p={p:.6f}")
print(f"  Predicted: rho > +0.30")
if rho > 0.30 and p < 0.05:
    print(f"  RESULT: CONFIRMED")
elif rho > 0.15 and p < 0.05:
    print(f"  RESULT: SIGNIFICANT but below 0.30 threshold (rho={rho:+.4f})")
elif rho > 0:
    print(f"  RESULT: DIRECTIONALLY CORRECT but {'not significant' if p >= 0.05 else 'weak'}")
else:
    print(f"  RESULT: FAILED (rho={rho:+.4f})")

print(f"\n  l vs k (line-level): rho={rho_lk:+.4f}")
print(f"  (Folio-level {'{k,l}'} cluster was r=+0.54)")
if rho_lk > 0.10 and p_lk < 0.05:
    print(f"  Line-level {'{k,l}'} cluster: CONFIRMED (rho={rho_lk:+.4f})")
else:
    print(f"  Line-level {'{k,l}'} cluster: {'WEAK' if rho_lk > 0 else 'ABSENT'}")
