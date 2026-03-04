"""P-L11: l-terminal MIDDLEs predict LOW within-line kernel contact.

If l = "idle/standby" (in main loop, not actively specifying), lines with
l-terminal tokens should have fewer kernel atoms (k, h, e in MIDDLE) than
matched non-l lines from the same folio and suffix mode.

Prediction: l-terminal lines have <=0.85x kernel contact fraction vs matched non-l lines.
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

kernel_atoms = {'k', 'h', 'e'}

# ============================================================
# Build per-line data
# ============================================================
print("Building per-line data...")

line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

# Get line-level suffix mode
b_folios = sorted(set(t.folio for t in tx.currier_b()))
line_mode_map = {}
for folio in b_folios:
    try:
        lines = decoder.analyze_folio_lines(folio)
        for la in lines:
            if la.suffix_mode:
                line_mode_map[(folio, la.line_id)] = la.suffix_mode
    except Exception:
        pass

print(f"  Total lines: {len(line_tokens)}")
print(f"  Lines with mode: {len(line_mode_map)}")

# ============================================================
# For each line: compute l-terminal fraction and kernel fraction
# ============================================================
line_data = []

for (folio, line_id), words in line_tokens.items():
    if len(words) < 4:
        continue
    sec = folio_section.get(folio)
    if not sec:
        continue
    mode = line_mode_map.get((folio, line_id))

    n_classified = 0
    n_l_terminal = 0
    n_kernel_contact = 0  # tokens with any kernel atom in MIDDLE
    n_kernel_k = 0
    n_kernel_h = 0
    n_kernel_e = 0

    for w in words:
        mid = morph.extract(w).middle
        if not mid:
            continue
        n_classified += 1

        # l-terminal
        if len(mid) >= 2 and mid[-1] == 'l':
            n_l_terminal += 1

        # kernel contact: any k, h, e in MIDDLE
        mid_set = set(mid)
        if mid_set & kernel_atoms:
            n_kernel_contact += 1
        if 'k' in mid_set:
            n_kernel_k += 1
        if 'h' in mid_set:
            n_kernel_h += 1
        if 'e' in mid_set:
            n_kernel_e += 1

    if n_classified < 4:
        continue

    has_l_term = n_l_terminal > 0
    l_frac = n_l_terminal / n_classified
    kernel_frac = n_kernel_contact / n_classified
    k_frac = n_kernel_k / n_classified
    h_frac = n_kernel_h / n_classified
    e_frac = n_kernel_e / n_classified

    line_data.append({
        'folio': folio, 'line': line_id, 'sec': sec, 'mode': mode,
        'n': n_classified, 'has_l_term': has_l_term, 'n_l_term': n_l_terminal,
        'l_frac': l_frac, 'kernel_frac': kernel_frac,
        'k_frac': k_frac, 'h_frac': h_frac, 'e_frac': e_frac
    })

print(f"  Lines with >=4 classified: {len(line_data)}")
l_lines = [d for d in line_data if d['has_l_term']]
nol_lines = [d for d in line_data if not d['has_l_term']]
print(f"  Lines with l-terminal: {len(l_lines)}")
print(f"  Lines without l-terminal: {len(nol_lines)}")

# ============================================================
# P-L11a: Direct comparison: l-terminal lines vs non-l-terminal lines
# ============================================================
print(f"\n{'='*70}")
print("P-L11: KERNEL CONTACT ON l-TERMINAL vs NON-l-TERMINAL LINES")
print(f"{'='*70}")
print("Prediction: l-terminal lines have <=0.85x kernel contact\n")

l_kernel = sum(d['kernel_frac'] for d in l_lines) / len(l_lines) if l_lines else 0
nol_kernel = sum(d['kernel_frac'] for d in nol_lines) / len(nol_lines) if nol_lines else 0
ratio = l_kernel / nol_kernel if nol_kernel > 0 else 0

print(f"  l-terminal lines: mean kernel fraction = {l_kernel:.4f} (n={len(l_lines)})")
print(f"  non-l lines:      mean kernel fraction = {nol_kernel:.4f} (n={len(nol_lines)})")
print(f"  Ratio: {ratio:.4f}x")

# Per kernel atom
for atom_name, field in [('k', 'k_frac'), ('h', 'h_frac'), ('e', 'e_frac')]:
    l_val = sum(d[field] for d in l_lines) / len(l_lines) if l_lines else 0
    nol_val = sum(d[field] for d in nol_lines) / len(nol_lines) if nol_lines else 0
    r = l_val / nol_val if nol_val > 0 else 0
    print(f"    {atom_name}: l-lines={l_val:.4f}, non-l={nol_val:.4f}, ratio={r:.4f}x")

# ============================================================
# P-L11b: Spearman: l-terminal fraction vs kernel fraction (continuous)
# ============================================================
print(f"\n{'='*70}")
print("CONTINUOUS: l-TERMINAL FRACTION vs KERNEL FRACTION (line level)")
print(f"{'='*70}")

l_fracs = [d['l_frac'] for d in line_data]
k_fracs_all = [d['kernel_frac'] for d in line_data]
rho, p = spearman_rho(l_fracs, k_fracs_all)
print(f"  Global: rho={rho:+.4f}, p={p:.6f}, n={len(line_data)}")

# Within-section
print(f"\n  Within-section:")
for sec in sorted(set(d['sec'] for d in line_data)):
    sec_d = [d for d in line_data if d['sec'] == sec]
    if len(sec_d) < 30:
        continue
    sl = [d['l_frac'] for d in sec_d]
    sk = [d['kernel_frac'] for d in sec_d]
    sr, sp = spearman_rho(sl, sk)
    print(f"    {sec} (n={len(sec_d):>4d}): rho={sr:+.4f} p={sp:.6f}")

# ============================================================
# P-L11c: Matched comparison — same folio, same mode
# ============================================================
print(f"\n{'='*70}")
print("MATCHED: SAME FOLIO + SAME MODE")
print(f"{'='*70}")

# Group by (folio, mode)
matched_groups = defaultdict(lambda: {'l': [], 'nol': []})
for d in line_data:
    if d['mode'] is None:
        continue
    key = (d['folio'], d['mode'])
    if d['has_l_term']:
        matched_groups[key]['l'].append(d['kernel_frac'])
    else:
        matched_groups[key]['nol'].append(d['kernel_frac'])

l_matched = []
nol_matched = []
for key, group in matched_groups.items():
    if group['l'] and group['nol']:
        l_matched.extend(group['l'])
        nol_matched.extend(group['nol'])

if l_matched and nol_matched:
    l_mean = sum(l_matched) / len(l_matched)
    nol_mean = sum(nol_matched) / len(nol_matched)
    matched_ratio = l_mean / nol_mean if nol_mean > 0 else 0
    print(f"  l-terminal lines (matched): mean kernel = {l_mean:.4f} (n={len(l_matched)})")
    print(f"  non-l lines (matched):      mean kernel = {nol_mean:.4f} (n={len(nol_matched)})")
    print(f"  Matched ratio: {matched_ratio:.4f}x")

# ============================================================
# P-L11d: Comprehensive — ALL terminal atoms vs kernel contact
# ============================================================
print(f"\n{'='*70}")
print("ALL TERMINAL ATOMS: KERNEL CONTACT CORRELATION")
print(f"{'='*70}")
print("(Which terminal atoms predict high/low kernel contact at line level?)\n")

# Per-line: terminal atom fractions
atoms = 'a d e h k o n i m y c p f s t r l q'.split()

line_term_data = []
for (folio, line_id), words in line_tokens.items():
    if len(words) < 4:
        continue
    sec = folio_section.get(folio)
    if not sec:
        continue

    n = 0
    term_counts = Counter()
    kernel_count = 0

    for w in words:
        mid = morph.extract(w).middle
        if not mid:
            continue
        n += 1
        if len(mid) >= 2:
            term_counts[mid[-1]] += 1
        if set(mid) & kernel_atoms:
            kernel_count += 1

    if n < 4:
        continue

    entry = {'kernel_frac': kernel_count / n}
    for atom in atoms:
        entry[atom] = term_counts.get(atom, 0) / n
    line_term_data.append(entry)

print(f"  {'Atom':<5s} {'rho':>8s} {'p':>10s} {'direction':>14s}")
print(f"  {'-'*5} {'-'*8} {'-'*10} {'-'*14}")

kf = [d['kernel_frac'] for d in line_term_data]
atom_results = []
for atom in atoms:
    af = [d[atom] for d in line_term_data]
    r, p_val = spearman_rho(af, kf)
    atom_results.append((atom, r, p_val))

atom_results.sort(key=lambda x: x[1])
for atom, r, p_val in atom_results:
    sig = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''
    direction = 'low-kernel' if r < -0.05 else 'high-kernel' if r > 0.05 else 'neutral'
    marker = ' <-- l' if atom == 'l' else ''
    print(f"  {atom:<5s} {r:>+8.4f} {p_val:>10.6f} {direction:>14s} {sig}{marker}")

# ============================================================
# P-L11e: Does l-terminal NEIGHBOR kernel tokens? (adjacent position)
# ============================================================
print(f"\n{'='*70}")
print("ADJACENCY: DO l-TERMINAL TOKENS NEIGHBOR KERNEL TOKENS?")
print(f"{'='*70}")
print("(Is l adjacent to k/h/e, or separated from them?)\n")

adj_kernel = 0
adj_nonkernel = 0
total_l_adj = 0

for (folio, line_id), words in line_tokens.items():
    if len(words) < 3:
        continue

    mids = []
    for w in words:
        mid = morph.extract(w).middle
        mids.append(mid if mid else '')

    for i, mid in enumerate(mids):
        if not mid or len(mid) < 2 or mid[-1] != 'l':
            continue

        # Check left neighbor
        if i > 0 and mids[i-1]:
            total_l_adj += 1
            if set(mids[i-1]) & kernel_atoms:
                adj_kernel += 1
            else:
                adj_nonkernel += 1

        # Check right neighbor
        if i < len(mids) - 1 and mids[i+1]:
            total_l_adj += 1
            if set(mids[i+1]) & kernel_atoms:
                adj_kernel += 1
            else:
                adj_nonkernel += 1

if total_l_adj > 0:
    kernel_adj_rate = adj_kernel / total_l_adj
    # Compare to baseline: what fraction of ALL token neighbors are kernel?
    base_kernel = 0
    base_total = 0
    for (folio, line_id), words in line_tokens.items():
        if len(words) < 3:
            continue
        mids = [morph.extract(w).middle or '' for w in words]
        for i in range(len(mids)):
            if not mids[i]:
                continue
            if i > 0 and mids[i-1]:
                base_total += 1
                if set(mids[i-1]) & kernel_atoms:
                    base_kernel += 1
            if i < len(mids) - 1 and mids[i+1]:
                base_total += 1
                if set(mids[i+1]) & kernel_atoms:
                    base_kernel += 1

    base_rate = base_kernel / base_total if base_total > 0 else 0
    adj_ratio = kernel_adj_rate / base_rate if base_rate > 0 else 0
    print(f"  l-terminal kernel adjacency: {kernel_adj_rate:.4f} ({adj_kernel}/{total_l_adj})")
    print(f"  Baseline kernel adjacency:   {base_rate:.4f} ({base_kernel}/{base_total})")
    print(f"  Ratio: {adj_ratio:.4f}x")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-L11 SUMMARY")
print(f"{'='*70}")

print(f"\n  l-terminal lines: kernel fraction = {l_kernel:.4f}")
print(f"  non-l lines:      kernel fraction = {nol_kernel:.4f}")
print(f"  Ratio: {ratio:.4f}x")
print(f"  Predicted: <=0.85x")

if ratio <= 0.85:
    print(f"  RESULT: CONFIRMED (ratio={ratio:.4f}x, l-terminal lines have LOW kernel contact)")
elif ratio <= 0.95:
    print(f"  RESULT: PARTIAL (ratio={ratio:.4f}x, some reduction but weaker than predicted)")
elif ratio >= 1.05:
    print(f"  RESULT: FAILED (ratio={ratio:.4f}x, l-terminal lines have MORE kernel contact)")
else:
    print(f"  RESULT: FAILED (ratio={ratio:.4f}x, no meaningful difference)")

print(f"\n  l-terminal vs kernel (Spearman): rho={rho:+.4f}")
if rho < -0.10 and p < 0.05:
    print(f"  Continuous association: SIGNIFICANT negative (l predicts low kernel)")
elif rho < 0:
    print(f"  Continuous association: weak/NS negative")
else:
    print(f"  Continuous association: absent or positive")
