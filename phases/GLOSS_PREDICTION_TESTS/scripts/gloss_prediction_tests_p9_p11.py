"""Phase 495b: Crazy-expert gloss predictions P9, P10, P11.

P9: n-terminal MIDDLEs enriched at line-final positions in Currier B
P10: k-initial MIDDLEs depleted in Mode B lines vs Mode A lines
P11: Bridge MIDDLEs simpler than dark-pipeline MIDDLEs (frequency-controlled)
"""

import json
import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

PROJECT = Path(__file__).resolve().parent

# ================================================================
# HELPERS
# ================================================================

def normal_cdf(z):
    """Standard normal CDF (Abramowitz & Stegun)."""
    if z < -8:
        return 0.0
    if z > 8:
        return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1 if z >= 0 else -1
    z_abs = abs(z)
    t = 1.0 / (1.0 + p * z_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z_abs * z_abs / 2.0)
    return 0.5 * (1.0 + sign * y)


def chi2_2x2(a, b, c, d):
    """Chi-squared for 2x2 table [[a,b],[c,d]]."""
    n = a + b + c + d
    if n == 0:
        return 0.0, 1.0
    expected = [
        [(a+b)*(a+c)/n, (a+b)*(b+d)/n],
        [(c+d)*(a+c)/n, (c+d)*(b+d)/n]
    ]
    chi2 = 0.0
    for obs, exp_row in zip([[a,b],[c,d]], expected):
        for o, e in zip(obs, exp_row):
            if e > 0:
                chi2 += (o - e)**2 / e
    z = ((chi2 / 1.0)**(1.0/3.0) - (1 - 2.0/9.0)) / math.sqrt(2.0/9.0)
    p = 1.0 - normal_cdf(z)
    return chi2, p


def mann_whitney_u(x, y):
    """Simple Mann-Whitney U test (normal approximation for large samples)."""
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return 0, 1.0
    # Combine and rank
    combined = [(v, 'x') for v in x] + [(v, 'y') for v in y]
    combined.sort(key=lambda t: t[0])
    # Assign ranks (handle ties with average rank)
    ranks = {}
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2  # 1-based average
        for k in range(i, j):
            if k not in ranks:
                ranks[k] = []
            ranks[k] = avg_rank
        i = j
    # Sum ranks for group x
    r_x = sum(ranks[i] for i in range(len(combined)) if combined[i][1] == 'x')
    u_x = r_x - nx * (nx + 1) / 2
    mu = nx * ny / 2
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12)
    if sigma == 0:
        return u_x, 1.0
    z = (u_x - mu) / sigma
    p = 2 * (1 - normal_cdf(abs(z)))
    return u_x, p


# ================================================================
# LOAD DATA
# ================================================================
tx = Transcript()
morph = Morphology()

# Build all B tokens with line info
tokens_by_line = defaultdict(list)  # (folio, line_num) -> [tokens]
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
        'placement': token.placement,
        'line_initial': token.line_initial,
        'line_final': token.line_final,
    }
    key = (token.folio, token.line)
    tokens_by_line[key].append(tok_data)
    all_b_tokens.append(tok_data)

print(f"Currier B tokens: {len(all_b_tokens)}")
print(f"Lines: {len(tokens_by_line)}")

# ================================================================
# P9: n-TERMINAL MIDDLEs AT LINE-FINAL POSITIONS
# ================================================================
print(f"\n{'='*70}")
print("P9: n-TERMINAL MIDDLEs AT LINE-FINAL POSITIONS")
print(f"{'='*70}")

# For each token, compute normalized line position
# Group by (folio, line), assign position index
n_term_positions = []
other_positions = []
n_term_final_count = 0
n_term_nonfinal_count = 0
other_final_count = 0
other_nonfinal_count = 0

for key, toks in tokens_by_line.items():
    n_toks = len(toks)
    if n_toks < 3:
        continue
    for i, t in enumerate(toks):
        mid = t['middle']
        if not mid:
            continue
        norm_pos = i / (n_toks - 1) if n_toks > 1 else 0.5
        is_n_terminal = mid.endswith('n')
        is_final = (i == n_toks - 1)
        if is_n_terminal:
            n_term_positions.append(norm_pos)
            if is_final:
                n_term_final_count += 1
            else:
                n_term_nonfinal_count += 1
        else:
            other_positions.append(norm_pos)
            if is_final:
                other_final_count += 1
            else:
                other_nonfinal_count += 1

# Mean positions
mean_n = sum(n_term_positions) / len(n_term_positions) if n_term_positions else 0
mean_o = sum(other_positions) / len(other_positions) if other_positions else 0

print(f"\nn-terminal MIDDLEs: {len(n_term_positions)}")
print(f"Other MIDDLEs: {len(other_positions)}")
print(f"\nMean normalized position:")
print(f"  n-terminal: {mean_n:.4f}")
print(f"  Other:      {mean_o:.4f}")
print(f"  Ratio:      {mean_n/mean_o:.3f}x")

# Mann-Whitney test
u, p_mw = mann_whitney_u(n_term_positions, other_positions)
print(f"  Mann-Whitney p={p_mw:.6f}")

# Top quintile enrichment
top_quintile_n = sum(1 for p in n_term_positions if p >= 0.8)
top_quintile_o = sum(1 for p in other_positions if p >= 0.8)
n_rate = top_quintile_n / len(n_term_positions) if n_term_positions else 0
o_rate = top_quintile_o / len(other_positions) if other_positions else 0
print(f"\nTop quintile (pos >= 0.8) enrichment:")
print(f"  n-terminal: {top_quintile_n}/{len(n_term_positions)} = {n_rate:.4f}")
print(f"  Other:      {top_quintile_o}/{len(other_positions)} = {o_rate:.4f}")
print(f"  Ratio:      {n_rate/o_rate:.3f}x" if o_rate > 0 else "  Ratio: inf")

# Line-final enrichment (binary)
total_n = n_term_final_count + n_term_nonfinal_count
total_o = other_final_count + other_nonfinal_count
n_final_rate = n_term_final_count / total_n if total_n else 0
o_final_rate = other_final_count / total_o if total_o else 0
chi2_lf, p_lf = chi2_2x2(n_term_final_count, n_term_nonfinal_count,
                          other_final_count, other_nonfinal_count)
print(f"\nLine-final rate:")
print(f"  n-terminal: {n_term_final_count}/{total_n} = {n_final_rate:.4f}")
print(f"  Other:      {other_final_count}/{total_o} = {o_final_rate:.4f}")
print(f"  Ratio:      {n_final_rate/o_final_rate:.3f}x" if o_final_rate > 0 else "  Ratio: inf")
print(f"  Chi2={chi2_lf:.3f}, p={p_lf:.6f}")

if n_final_rate > o_final_rate and p_lf < 0.05:
    print(f"  RESULT: CONFIRMED - n-terminal MIDDLEs enriched at line-final")
elif n_final_rate < o_final_rate and p_lf < 0.05:
    print(f"  RESULT: INVERTED - n-terminal MIDDLEs depleted at line-final")
else:
    print(f"  RESULT: NOT SIGNIFICANT")

# Section control
print(f"\nSection breakdown (line-final rate):")
for sec in sorted(set(t['section'] for t in all_b_tokens if t['section'])):
    sec_n_final = 0
    sec_n_total = 0
    sec_o_final = 0
    sec_o_total = 0
    for key, toks in tokens_by_line.items():
        if len(toks) < 3:
            continue
        if toks[0]['section'] != sec:
            continue
        for i, t in enumerate(toks):
            mid = t['middle']
            if not mid:
                continue
            is_final = (i == len(toks) - 1)
            if mid.endswith('n'):
                sec_n_total += 1
                if is_final:
                    sec_n_final += 1
            else:
                sec_o_total += 1
                if is_final:
                    sec_o_final += 1
    if sec_n_total > 0 and sec_o_total > 0:
        sn_rate = sec_n_final / sec_n_total
        so_rate = sec_o_final / sec_o_total
        ratio = sn_rate / so_rate if so_rate > 0 else float('inf')
        print(f"  {sec:5s}  n-term={sn_rate:.4f} other={so_rate:.4f} ratio={ratio:.3f}x")


# ================================================================
# P10: k-INITIAL MIDDLEs IN MODE A vs MODE B LINES
# ================================================================
print(f"\n{'='*70}")
print("P10: k-INITIAL MIDDLEs IN MODE A vs MODE B LINES")
print(f"{'='*70}")

# Suffix mode infrastructure
TERMINAL_SUFFIXES = {'y', 'dy', 'edy', 'ody', 'ey', 'ary', 'ory',
                     'ry', 'ky', 'ty', 'py', 'fy', 'my', 'ly', 'sy'}
CONNECTOR_SUFFIXES = {'o', 'or', 'os', 'oe'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'aiiin', 'al', 'am', 'an'}
MODE_A_CENTROID = [0.430, 0.019, 0.086, 0.466]
MODE_B_CENTROID = [0.155, 0.031, 0.072, 0.741]
SUFFIX_CATS = ['terminal', 'connector', 'iterate', 'bare']


def suffix_category(suffix):
    if not suffix:
        return 'bare'
    if suffix in TERMINAL_SUFFIXES:
        return 'terminal'
    if suffix in CONNECTOR_SUFFIXES:
        return 'connector'
    if suffix in ITERATE_SUFFIXES:
        return 'iterate'
    return 'bare'


def euclidean_dist(a, b):
    return math.sqrt(sum((ai - bi)**2 for ai, bi in zip(a, b)))


def classify_suffix_mode(line_toks):
    if len(line_toks) < 3:
        return None
    counts = Counter(suffix_category(t['suffix']) for t in line_toks)
    n = len(line_toks)
    vec = [counts.get(c, 0) / n for c in SUFFIX_CATS]
    d_a = euclidean_dist(vec, MODE_A_CENTROID)
    d_b = euclidean_dist(vec, MODE_B_CENTROID)
    return 'A' if d_a < d_b else 'B'


# Classify all lines by suffix mode
mode_a_k_count = 0
mode_a_nonk_count = 0
mode_b_k_count = 0
mode_b_nonk_count = 0

# Per-section tracking
sec_mode_k = defaultdict(lambda: {'A_k': 0, 'A_nk': 0, 'B_k': 0, 'B_nk': 0})

for key, toks in tokens_by_line.items():
    mode = classify_suffix_mode(toks)
    if mode is None:
        continue
    sec = toks[0]['section'] if toks else ''
    for t in toks:
        mid = t['middle']
        if not mid:
            continue
        is_k_initial = mid.startswith('k')
        if mode == 'A':
            if is_k_initial:
                mode_a_k_count += 1
                sec_mode_k[sec]['A_k'] += 1
            else:
                mode_a_nonk_count += 1
                sec_mode_k[sec]['A_nk'] += 1
        else:
            if is_k_initial:
                mode_b_k_count += 1
                sec_mode_k[sec]['B_k'] += 1
            else:
                mode_b_nonk_count += 1
                sec_mode_k[sec]['B_nk'] += 1

mode_a_total = mode_a_k_count + mode_a_nonk_count
mode_b_total = mode_b_k_count + mode_b_nonk_count
k_rate_a = mode_a_k_count / mode_a_total if mode_a_total else 0
k_rate_b = mode_b_k_count / mode_b_total if mode_b_total else 0

print(f"\nMode A lines: {mode_a_total} tokens ({mode_a_k_count} k-initial)")
print(f"Mode B lines: {mode_b_total} tokens ({mode_b_k_count} k-initial)")

print(f"\nk-initial MIDDLE rate:")
print(f"  Mode A: {mode_a_k_count}/{mode_a_total} = {k_rate_a:.4f}")
print(f"  Mode B: {mode_b_k_count}/{mode_b_total} = {k_rate_b:.4f}")
ratio_k = k_rate_b / k_rate_a if k_rate_a > 0 else float('inf')
print(f"  Mode B/A ratio: {ratio_k:.3f}x")

chi2_k, p_k = chi2_2x2(mode_a_k_count, mode_a_nonk_count,
                        mode_b_k_count, mode_b_nonk_count)
print(f"  Chi2={chi2_k:.3f}, p={p_k:.6f}")

if ratio_k < 1.0 and p_k < 0.05:
    print(f"  RESULT: CONFIRMED - k-initial MIDDLEs depleted in Mode B (ratio={ratio_k:.3f}x)")
elif ratio_k > 1.0 and p_k < 0.05:
    print(f"  RESULT: INVERTED - k-initial MIDDLEs enriched in Mode B")
else:
    print(f"  RESULT: NOT SIGNIFICANT")

# Section control
print(f"\nSection breakdown (k-initial rate by mode):")
for sec in sorted(sec_mode_k.keys()):
    d = sec_mode_k[sec]
    a_tot = d['A_k'] + d['A_nk']
    b_tot = d['B_k'] + d['B_nk']
    if a_tot > 0 and b_tot > 0:
        ra = d['A_k'] / a_tot
        rb = d['B_k'] / b_tot
        rat = rb / ra if ra > 0 else float('inf')
        print(f"  {sec:5s}  modeA={ra:.4f} modeB={rb:.4f} B/A={rat:.3f}x (A:{a_tot} B:{b_tot})")

# Also check other initial atoms for comparison
print(f"\nComparison: other initial atoms by mode:")
for atom in ['e', 'h', 'o', 'a', 'd']:
    a_count = 0
    b_count = 0
    a_total_cmp = 0
    b_total_cmp = 0
    for key, toks in tokens_by_line.items():
        mode = classify_suffix_mode(toks)
        if mode is None:
            continue
        for t in toks:
            mid = t['middle']
            if not mid:
                continue
            if mode == 'A':
                a_total_cmp += 1
                if mid.startswith(atom):
                    a_count += 1
            else:
                b_total_cmp += 1
                if mid.startswith(atom):
                    b_count += 1
    ra = a_count / a_total_cmp if a_total_cmp else 0
    rb = b_count / b_total_cmp if b_total_cmp else 0
    rat = rb / ra if ra > 0 else float('inf')
    print(f"  {atom}-initial: modeA={ra:.4f} modeB={rb:.4f} B/A={rat:.3f}x")


# ================================================================
# P11: BRIDGE vs DARK PIPELINE COMPOUND DEPTH
# ================================================================
print(f"\n{'='*70}")
print("P11: BRIDGE vs DARK PIPELINE COMPOUND DEPTH")
print(f"{'='*70}")

# Load bridge and dark pipeline sets
with open(PROJECT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' /
          'bridge_selection.json', encoding='utf-8') as f:
    bridge_data = json.load(f)
bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])

with open(PROJECT / 'phases' / 'A_TO_B_ROLE_PROJECTION' / 'results' /
          'pp_role_foundation.json', encoding='utf-8') as f:
    pp_role_data = json.load(f)
with open(PROJECT / 'phases' / 'CROSS_SYSTEM_VOCABULARY_FLOW' / 'results' /
          'ab_vocabulary_flow.json', encoding='utf-8') as f:
    vocab_flow = json.load(f)
unmatched_pp = set(pp_role_data['unmatched_pp'])
b_absent = set(vocab_flow['b1']['b_absent_middles'])
dark_set = unmatched_pp - b_absent

print(f"\nBridge MIDDLEs: {len(bridge_set)}")
print(f"Dark pipeline MIDDLEs: {len(dark_set)}")

# Build MiddleAnalyzer for compound detection
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')

# Compute compound depth for each MIDDLE
# Depth = number of maximal atoms (0 if not compound, i.e. it IS a core atom)
def get_depth(middle):
    """Get compound depth: number of maximal contained atoms, or 1 if atomic."""
    atoms = mid_analyzer.get_maximal_atoms(middle)
    if not atoms:
        return 1  # atomic (no contained sub-atoms)
    return len(atoms)


# Also compute character length and token frequency
# Pre-compute frequencies
middle_freq = Counter()
for t in all_b_tokens:
    if t['middle']:
        middle_freq[t['middle']] += 1

# Bridge stats
bridge_depths = []
bridge_lengths = []
bridge_freqs = []
for m in bridge_set:
    bridge_depths.append(get_depth(m))
    bridge_lengths.append(len(m))
    bridge_freqs.append(middle_freq.get(m, 0))

# Dark stats
dark_depths = []
dark_lengths = []
dark_freqs = []
for m in dark_set:
    dark_depths.append(get_depth(m))
    dark_lengths.append(len(m))
    dark_freqs.append(middle_freq.get(m, 0))

mean_bd = sum(bridge_depths) / len(bridge_depths) if bridge_depths else 0
mean_dd = sum(dark_depths) / len(dark_depths) if dark_depths else 0
mean_bl = sum(bridge_lengths) / len(bridge_lengths) if bridge_lengths else 0
mean_dl = sum(dark_lengths) / len(dark_lengths) if dark_lengths else 0
mean_bf = sum(bridge_freqs) / len(bridge_freqs) if bridge_freqs else 0
mean_df = sum(dark_freqs) / len(dark_freqs) if dark_freqs else 0

print(f"\nRaw comparison:")
print(f"  {'Metric':<20s} {'Bridge':>10s} {'Dark':>10s} {'Ratio':>10s}")
print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*10}")
print(f"  {'Mean depth':<20s} {mean_bd:>10.3f} {mean_dd:>10.3f} {mean_bd/mean_dd:.3f}x" if mean_dd > 0 else "")
print(f"  {'Mean char length':<20s} {mean_bl:>10.2f} {mean_dl:>10.2f} {mean_bl/mean_dl:.3f}x" if mean_dl > 0 else "")
print(f"  {'Mean frequency':<20s} {mean_bf:>10.1f} {mean_df:>10.1f} {mean_bf/mean_df:.1f}x" if mean_df > 0 else "")

# Mann-Whitney on depth
u_depth, p_depth = mann_whitney_u(bridge_depths, dark_depths)
print(f"\n  Depth Mann-Whitney: U={u_depth:.0f}, p={p_depth:.6f}")

# Mann-Whitney on length
u_len, p_len = mann_whitney_u(bridge_lengths, dark_lengths)
print(f"  Length Mann-Whitney: U={u_len:.0f}, p={p_len:.6f}")

# Compound rate comparison
bridge_compound = sum(1 for d in bridge_depths if d > 1)
dark_compound = sum(1 for d in dark_depths if d > 1)
bc_rate = bridge_compound / len(bridge_depths) if bridge_depths else 0
dc_rate = dark_compound / len(dark_depths) if dark_depths else 0
print(f"\n  Compound rate (depth > 1):")
print(f"    Bridge: {bridge_compound}/{len(bridge_depths)} = {bc_rate:.4f}")
print(f"    Dark:   {dark_compound}/{len(dark_depths)} = {dc_rate:.4f}")
print(f"    Ratio:  {bc_rate/dc_rate:.3f}x" if dc_rate > 0 else "    Ratio: 0/0")

# Frequency-controlled comparison
# Bin by log-frequency quintiles
print(f"\nFrequency-controlled comparison:")
all_freqs = [(m, middle_freq.get(m, 0), 'bridge') for m in bridge_set] + \
            [(m, middle_freq.get(m, 0), 'dark') for m in dark_set]
all_freqs.sort(key=lambda x: x[1])

# Create frequency bands
n_total = len(all_freqs)
band_size = max(1, n_total // 5)

print(f"  {'Band':<10s} {'Freq range':<15s} {'B_depth':>8s} {'D_depth':>8s} {'Ratio':>8s} {'B_n':>5s} {'D_n':>5s}")
print(f"  {'-'*10} {'-'*15} {'-'*8} {'-'*8} {'-'*8} {'-'*5} {'-'*5}")

bridge_wins = 0
for band_i in range(5):
    start = band_i * band_size
    end = min(start + band_size, n_total) if band_i < 4 else n_total
    band = all_freqs[start:end]

    b_depths_band = [get_depth(m) for m, f, g in band if g == 'bridge']
    d_depths_band = [get_depth(m) for m, f, g in band if g == 'dark']

    freq_min = band[0][1] if band else 0
    freq_max = band[-1][1] if band else 0

    b_mean = sum(b_depths_band) / len(b_depths_band) if b_depths_band else 0
    d_mean = sum(d_depths_band) / len(d_depths_band) if d_depths_band else 0
    ratio = b_mean / d_mean if d_mean > 0 else float('inf')

    if b_mean < d_mean:
        bridge_wins += 1

    print(f"  Q{band_i+1:<9d} {freq_min:>5d}-{freq_max:<8d} {b_mean:>8.3f} {d_mean:>8.3f} {ratio:>8.3f} {len(b_depths_band):>5d} {len(d_depths_band):>5d}")

print(f"\n  Bridge simpler in {bridge_wins}/5 frequency bands")

# Simple regression-like control: compare within frequency-matched pairs
# Match each bridge MIDDLE to the closest-frequency dark MIDDLE
dark_by_freq = sorted([(middle_freq.get(m, 0), m) for m in dark_set])
matched_bridge_depths = []
matched_dark_depths = []

for m_b in bridge_set:
    freq_b = middle_freq.get(m_b, 0)
    # Binary search for closest frequency in dark
    best_dist = float('inf')
    best_m = None
    for freq_d, m_d in dark_by_freq:
        dist = abs(freq_d - freq_b)
        if dist < best_dist:
            best_dist = dist
            best_m = m_d
        elif freq_d > freq_b + best_dist:
            break
    if best_m:
        matched_bridge_depths.append(get_depth(m_b))
        matched_dark_depths.append(get_depth(best_m))

if matched_bridge_depths:
    mb_mean = sum(matched_bridge_depths) / len(matched_bridge_depths)
    md_mean = sum(matched_dark_depths) / len(matched_dark_depths)
    u_matched, p_matched = mann_whitney_u(matched_bridge_depths, matched_dark_depths)
    print(f"\nFrequency-matched pairs ({len(matched_bridge_depths)} pairs):")
    print(f"  Bridge mean depth: {mb_mean:.3f}")
    print(f"  Dark mean depth:   {md_mean:.3f}")
    print(f"  Ratio: {mb_mean/md_mean:.3f}x" if md_mean > 0 else "  Ratio: inf")
    print(f"  Mann-Whitney: U={u_matched:.0f}, p={p_matched:.6f}")

# Final verdict
print(f"\n  RAW depth ratio: {mean_bd/mean_dd:.3f}x" if mean_dd > 0 else "")
if mean_bd < mean_dd and p_depth < 0.05:
    print(f"  RESULT: CONFIRMED - bridges simpler than dark pipeline (p={p_depth:.6f})")
elif mean_bd >= mean_dd:
    print(f"  RESULT: FAILED - bridges not simpler")
else:
    print(f"  RESULT: NOT SIGNIFICANT (p={p_depth:.6f})")


# ================================================================
# SUMMARY
# ================================================================
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")

# P9
p9_label = "CONFIRMED" if (n_final_rate > o_final_rate and p_lf < 0.05) else \
           "INVERTED" if (n_final_rate < o_final_rate and p_lf < 0.05) else "NOT SIGNIFICANT"
print(f"\nP9  (n at line-final):       {p9_label} (ratio={n_final_rate/o_final_rate:.3f}x, p={p_lf:.6f})" if o_final_rate > 0 else "P9: N/A")

# P10
p10_label = "CONFIRMED" if (ratio_k < 1.0 and p_k < 0.05) else \
            "INVERTED" if (ratio_k > 1.0 and p_k < 0.05) else "NOT SIGNIFICANT"
print(f"P10 (k depleted in Mode B):  {p10_label} (B/A ratio={ratio_k:.3f}x, p={p_k:.6f})")

# P11
p11_label = "CONFIRMED" if (mean_bd < mean_dd and p_depth < 0.05) else \
            "FAILED" if (mean_bd >= mean_dd) else "NOT SIGNIFICANT"
print(f"P11 (bridge simpler):        {p11_label} (depth ratio={mean_bd/mean_dd:.3f}x, p={p_depth:.6f})" if mean_dd > 0 else "P11: N/A")
