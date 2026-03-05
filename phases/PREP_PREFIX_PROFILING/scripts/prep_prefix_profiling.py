#!/usr/bin/env python3
"""
Phase 508: PREP_PREFIX_PROFILING

Comprehensive profiling of prep PREFIXes (pch, tch, dch, lch, te) to determine
whether they are statistically differentiable despite C1221's finding that they
carry IDENTICAL MIDDLE content (cosine 0.963).

Tests:
  T1: Positional Differentiation (line position)
  T2: Sequential Context (predecessor/successor class)
  T3: Suffix Pattern Divergence
  T4: REGIME Distribution
  T5: Specific MIDDLE Vocabulary
  T6: Paragraph Position Profile
  T7: Section Distribution
  T8: Bare ch Comparison (divergence from base)

Uses canonical library: scripts/voynich.py
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

# ============================================================
# CONFIGURATION
# ============================================================
PREP_PREFIXES = ['pch', 'tch', 'dch', 'lch', 'te']
BARE_CH = 'ch'
ALL_TARGETS = PREP_PREFIXES + [BARE_CH]

OUTPUT_DIR = PROJECT_ROOT / 'phases' / 'PREP_PREFIX_PROFILING' / 'results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOAD DATA
# ============================================================
print("=" * 70)
print("Phase 508: PREP_PREFIX_PROFILING")
print("=" * 70)

tx = Transcript()
morph = Morphology()

# Load REGIME assignments
regime_path = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)
FOLIO_REGIME = {}
for folio, info in regime_data.get('regime_assignments', {}).items():
    FOLIO_REGIME[folio] = info['regime']

# Load token-to-class mapping (49 classes)
class_map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path, 'r', encoding='utf-8') as f:
    class_map_data = json.load(f)
TOKEN_TO_CLASS = {t: int(c) for t, c in class_map_data['token_to_class'].items()}

# ============================================================
# COLLECT CURRIER B TOKENS WITH LINE CONTEXT
# ============================================================
print("\nCollecting Currier B tokens...")

# Group tokens by (folio, line) to compute positions and context
line_tokens = defaultdict(list)  # (folio, line) -> [token_obj]
all_b_tokens = []

for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    all_b_tokens.append(t)

print(f"  Total B tokens: {len(all_b_tokens)}")
print(f"  Lines: {len(line_tokens)}")

# Build token index within line
token_line_pos = {}  # id(token) -> (index, line_length)
for key, tokens in line_tokens.items():
    for i, t in enumerate(tokens):
        token_line_pos[id(t)] = (i, len(tokens))

# Build paragraph structure: group lines by folio, split on par_initial
# Paragraph = sequence of lines from par_initial=True to next par_initial=True
folio_lines = defaultdict(list)  # folio -> [(line_number, [tokens])]
for (folio, line), tokens in sorted(line_tokens.items()):
    folio_lines[folio].append((line, tokens))

# Assign paragraph index to each line
line_to_para = {}  # (folio, line) -> (para_idx, line_in_para_idx, para_length)
for folio, lines in folio_lines.items():
    para_idx = -1
    para_lines = []
    paragraphs = []

    for line_num, tokens in lines:
        # Check if any token in this line starts a paragraph
        is_para_start = any(t.par_initial for t in tokens)
        if is_para_start:
            if para_lines:
                paragraphs.append(para_lines)
            para_lines = [(line_num, tokens)]
            para_idx += 1
        else:
            para_lines.append((line_num, tokens))
    if para_lines:
        paragraphs.append(para_lines)

    for pidx, plines in enumerate(paragraphs):
        plen = len(plines)
        for lidx, (lnum, _) in enumerate(plines):
            line_to_para[(folio, lnum)] = (pidx, lidx, plen)

# ============================================================
# EXTRACT PREP PREFIX TOKEN DATA
# ============================================================
print("\nExtracting prep prefix tokens...")

# For each target prefix, collect token data
prefix_data = {p: [] for p in ALL_TARGETS}

for t in all_b_tokens:
    m = morph.extract(t.word)
    pfx = m.prefix
    if pfx not in ALL_TARGETS:
        continue

    idx, line_len = token_line_pos.get(id(t), (0, 1))
    norm_pos = idx / (line_len - 1) if line_len > 1 else 0.5

    # Get instruction class
    token_class = TOKEN_TO_CLASS.get(t.word, None)

    # Get REGIME
    regime = FOLIO_REGIME.get(t.folio, None)

    # Get paragraph position
    para_info = line_to_para.get((t.folio, t.line), None)
    if para_info:
        _, line_in_para, para_len = para_info
        para_pos = line_in_para / (para_len - 1) if para_len > 1 else 0.5
    else:
        para_pos = None

    prefix_data[pfx].append({
        'word': t.word,
        'folio': t.folio,
        'line': t.line,
        'section': t.section,
        'middle': m.middle,
        'suffix': m.suffix,
        'norm_pos': norm_pos,
        'token_class': token_class,
        'regime': regime,
        'para_pos': para_pos,
        'line_initial': t.line_initial,
        'line_final': t.line_final,
        'par_initial': t.par_initial,
        'par_final': t.par_final,
    })

print("\nToken counts:")
for p in ALL_TARGETS:
    print(f"  {p}: {len(prefix_data[p])}")

# ============================================================
# BUILD PREDECESSOR/SUCCESSOR CONTEXT
# ============================================================
print("\nBuilding sequential context...")

# For each token in each line, record predecessor and successor class
token_context = defaultdict(list)  # prefix -> [(pred_class, succ_class)]

for (folio, line), tokens in line_tokens.items():
    for i, t in enumerate(tokens):
        m = morph.extract(t.word)
        pfx = m.prefix
        if pfx not in ALL_TARGETS:
            continue

        pred_class = None
        succ_class = None
        if i > 0:
            pred_class = TOKEN_TO_CLASS.get(tokens[i-1].word, None)
        if i < len(tokens) - 1:
            succ_class = TOKEN_TO_CLASS.get(tokens[i+1].word, None)

        token_context[pfx].append((pred_class, succ_class))

# ============================================================
# STATISTICAL HELPERS
# ============================================================

def ks_test_2sample(data1, data2):
    """Two-sample KS test. Returns (D, p_approx)."""
    if len(data1) < 2 or len(data2) < 2:
        return (float('nan'), float('nan'))

    s1 = sorted(data1)
    s2 = sorted(data2)
    n1, n2 = len(s1), len(s2)

    # Combine and sort all values
    all_vals = sorted(set(s1 + s2))

    # Compute ECDF at each point
    d_max = 0.0
    i1, i2 = 0, 0
    for v in all_vals:
        while i1 < n1 and s1[i1] <= v:
            i1 += 1
        while i2 < n2 and s2[i2] <= v:
            i2 += 1
        d = abs(i1 / n1 - i2 / n2)
        if d > d_max:
            d_max = d

    # Approximate p-value (Kolmogorov-Smirnov)
    en = math.sqrt(n1 * n2 / (n1 + n2))
    try:
        # Using the asymptotic approximation
        lam = (en + 0.12 + 0.11 / en) * d_max
        p = 2.0 * math.exp(-2.0 * lam * lam)
        p = max(0.0, min(1.0, p))
    except:
        p = float('nan')

    return (d_max, p)


def chi2_test(counts_dict):
    """
    Chi-squared test of independence.
    counts_dict: {group: Counter({category: count})}
    Returns (chi2, p, dof, V).
    """
    groups = list(counts_dict.keys())
    all_cats = set()
    for c in counts_dict.values():
        all_cats.update(c.keys())
    cats = sorted(all_cats)

    if len(groups) < 2 or len(cats) < 2:
        return (0.0, 1.0, 0, 0.0)

    # Build contingency table
    table = []
    for g in groups:
        row = [counts_dict[g].get(c, 0) for c in cats]
        table.append(row)

    n_rows = len(groups)
    n_cols = len(cats)
    N = sum(sum(row) for row in table)

    if N == 0:
        return (0.0, 1.0, 0, 0.0)

    row_totals = [sum(row) for row in table]
    col_totals = [sum(table[i][j] for i in range(n_rows)) for j in range(n_cols)]

    chi2 = 0.0
    for i in range(n_rows):
        for j in range(n_cols):
            expected = row_totals[i] * col_totals[j] / N
            if expected > 0:
                chi2 += (table[i][j] - expected) ** 2 / expected

    dof = (n_rows - 1) * (n_cols - 1)

    # Cramer's V
    k = min(n_rows, n_cols)
    V = math.sqrt(chi2 / (N * (k - 1))) if N > 0 and k > 1 else 0.0

    # Approximate p-value using chi2 CDF (Wilson-Hilferty approximation)
    if dof > 0:
        z = (chi2 / dof) ** (1/3) - (1 - 2 / (9 * dof))
        z /= math.sqrt(2 / (9 * dof))
        # Standard normal CDF approximation
        p = 0.5 * math.erfc(z / math.sqrt(2))
        p = max(0.0, min(1.0, p))
    else:
        p = 1.0

    return (chi2, p, dof, V)


def jaccard(set1, set2):
    """Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    inter = len(set1 & set2)
    union = len(set1 | set2)
    return inter / union if union > 0 else 0.0


# ============================================================
# T1: POSITIONAL DIFFERENTIATION
# ============================================================
print("\n" + "=" * 70)
print("T1: POSITIONAL DIFFERENTIATION")
print("=" * 70)

t1_results = {}
for p in ALL_TARGETS:
    positions = [d['norm_pos'] for d in prefix_data[p]]
    if positions:
        mean_p = sum(positions) / len(positions)
        var_p = sum((x - mean_p) ** 2 for x in positions) / len(positions)
        std_p = math.sqrt(var_p)
        t1_results[p] = {
            'mean': round(mean_p, 4),
            'std': round(std_p, 4),
            'n': len(positions),
            'line_initial_pct': round(100 * sum(1 for d in prefix_data[p] if d['line_initial']) / len(prefix_data[p]), 1),
            'line_final_pct': round(100 * sum(1 for d in prefix_data[p] if d['line_final']) / len(prefix_data[p]), 1),
        }
        print(f"  {p:5s}: mean={mean_p:.4f} std={std_p:.4f} n={len(positions):5d}  "
              f"initial={t1_results[p]['line_initial_pct']:5.1f}%  final={t1_results[p]['line_final_pct']:5.1f}%")

# Pairwise KS tests among prep prefixes
print("\n  Pairwise KS tests (prep vs prep):")
t1_ks_prep = {}
for p1, p2 in combinations(PREP_PREFIXES, 2):
    d1 = [d['norm_pos'] for d in prefix_data[p1]]
    d2 = [d['norm_pos'] for d in prefix_data[p2]]
    D, p_val = ks_test_2sample(d1, d2)
    key = f"{p1}_vs_{p2}"
    t1_ks_prep[key] = {'D': round(D, 4), 'p': round(p_val, 6)}
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
    print(f"    {p1:4s} vs {p2:4s}: D={D:.4f}  p={p_val:.6f} {sig}")

# Prep vs bare ch
print("\n  Prep vs bare ch:")
t1_ks_bare = {}
for p in PREP_PREFIXES:
    d1 = [d['norm_pos'] for d in prefix_data[p]]
    d2 = [d['norm_pos'] for d in prefix_data[BARE_CH]]
    D, p_val = ks_test_2sample(d1, d2)
    key = f"{p}_vs_{BARE_CH}"
    t1_ks_bare[key] = {'D': round(D, 4), 'p': round(p_val, 6)}
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
    print(f"    {p:4s} vs {BARE_CH}: D={D:.4f}  p={p_val:.6f} {sig}")

# Count significant results
n_prep_sig = sum(1 for v in t1_ks_prep.values() if v['p'] < 0.05)
n_bare_sig = sum(1 for v in t1_ks_bare.values() if v['p'] < 0.05)
t1_verdict = "DIFFERENTIATED" if n_prep_sig >= 3 else "PARTIAL" if n_prep_sig >= 1 else "NOT_DIFFERENTIATED"
print(f"\n  T1 Verdict: {t1_verdict} ({n_prep_sig}/{len(t1_ks_prep)} prep pairs sig, {n_bare_sig}/{len(t1_ks_bare)} vs bare ch)")

# ============================================================
# T2: SEQUENTIAL CONTEXT
# ============================================================
print("\n" + "=" * 70)
print("T2: SEQUENTIAL CONTEXT")
print("=" * 70)

# Predecessor class distributions
pred_counts = {}
succ_counts = {}
for p in ALL_TARGETS:
    pred_counts[p] = Counter()
    succ_counts[p] = Counter()
    for pred_c, succ_c in token_context[p]:
        if pred_c is not None:
            pred_counts[p][pred_c] += 1
        if succ_c is not None:
            succ_counts[p][succ_c] += 1

# Top 3 predecessors and successors for each
print("\n  Top 3 predecessor classes:")
t2_top_pred = {}
for p in ALL_TARGETS:
    top3 = pred_counts[p].most_common(3)
    t2_top_pred[p] = [(c, n) for c, n in top3]
    total = sum(pred_counts[p].values())
    top_str = "  ".join(f"C{c}:{n}({100*n/total:.0f}%)" for c, n in top3) if total > 0 else "none"
    print(f"    {p:5s}: {top_str}")

print("\n  Top 3 successor classes:")
t2_top_succ = {}
for p in ALL_TARGETS:
    top3 = succ_counts[p].most_common(3)
    t2_top_succ[p] = [(c, n) for c, n in top3]
    total = sum(succ_counts[p].values())
    top_str = "  ".join(f"C{c}:{n}({100*n/total:.0f}%)" for c, n in top3) if total > 0 else "none"
    print(f"    {p:5s}: {top_str}")

# Chi-squared: predecessor distribution across prep prefixes
prep_pred = {p: pred_counts[p] for p in PREP_PREFIXES}
chi2_pred, p_pred, dof_pred, V_pred = chi2_test(prep_pred)
print(f"\n  Predecessor chi2 (prep PREFIXes): chi2={chi2_pred:.1f} dof={dof_pred} p={p_pred:.6f} V={V_pred:.3f}")

prep_succ = {p: succ_counts[p] for p in PREP_PREFIXES}
chi2_succ, p_succ, dof_succ, V_succ = chi2_test(prep_succ)
print(f"  Successor chi2 (prep PREFIXes):   chi2={chi2_succ:.1f} dof={dof_succ} p={p_succ:.6f} V={V_succ:.3f}")

# Also test prep vs bare ch
all_pred = {p: pred_counts[p] for p in ALL_TARGETS}
chi2_pred_all, p_pred_all, dof_pred_all, V_pred_all = chi2_test(all_pred)
print(f"\n  Predecessor chi2 (all incl ch):   chi2={chi2_pred_all:.1f} dof={dof_pred_all} p={p_pred_all:.6f} V={V_pred_all:.3f}")

all_succ = {p: succ_counts[p] for p in ALL_TARGETS}
chi2_succ_all, p_succ_all, dof_succ_all, V_succ_all = chi2_test(all_succ)
print(f"  Successor chi2 (all incl ch):     chi2={chi2_succ_all:.1f} dof={dof_succ_all} p={p_succ_all:.6f} V={V_succ_all:.3f}")

t2_verdict = "DIFFERENTIATED" if p_pred < 0.01 or p_succ < 0.01 else "PARTIAL" if p_pred < 0.05 or p_succ < 0.05 else "NOT_DIFFERENTIATED"
print(f"\n  T2 Verdict: {t2_verdict}")

# ============================================================
# T3: SUFFIX PATTERN DIVERGENCE
# ============================================================
print("\n" + "=" * 70)
print("T3: SUFFIX PATTERN DIVERGENCE")
print("=" * 70)

suffix_counts = {}
for p in ALL_TARGETS:
    suffix_counts[p] = Counter()
    for d in prefix_data[p]:
        sfx = d['suffix'] if d['suffix'] else 'BARE'
        suffix_counts[p][sfx] += 1

print("\n  Top 5 suffixes per prefix:")
t3_top_suffix = {}
for p in ALL_TARGETS:
    total = sum(suffix_counts[p].values())
    top5 = suffix_counts[p].most_common(5)
    t3_top_suffix[p] = [(s, n) for s, n in top5]
    top_str = "  ".join(f"{s}:{100*n/total:.0f}%" for s, n in top5) if total > 0 else "none"
    print(f"    {p:5s}: {top_str}")

# Chi-squared test across prep prefixes
prep_sfx = {p: suffix_counts[p] for p in PREP_PREFIXES}
chi2_sfx, p_sfx, dof_sfx, V_sfx = chi2_test(prep_sfx)
print(f"\n  Suffix chi2 (prep PREFIXes): chi2={chi2_sfx:.1f} dof={dof_sfx} p={p_sfx:.6f} V={V_sfx:.3f}")

# Also test including bare ch
all_sfx = {p: suffix_counts[p] for p in ALL_TARGETS}
chi2_sfx_all, p_sfx_all, dof_sfx_all, V_sfx_all = chi2_test(all_sfx)
print(f"  Suffix chi2 (all incl ch):   chi2={chi2_sfx_all:.1f} dof={dof_sfx_all} p={p_sfx_all:.6f} V={V_sfx_all:.3f}")

# Bare rate comparison
print("\n  Bare (no suffix) rate:")
for p in ALL_TARGETS:
    total = sum(suffix_counts[p].values())
    bare_n = suffix_counts[p].get('BARE', 0)
    print(f"    {p:5s}: {100*bare_n/total:.1f}% ({bare_n}/{total})")

t3_verdict = "DIFFERENTIATED" if p_sfx < 0.01 else "PARTIAL" if p_sfx < 0.05 else "NOT_DIFFERENTIATED"
print(f"\n  T3 Verdict: {t3_verdict}")

# ============================================================
# T4: REGIME DISTRIBUTION
# ============================================================
print("\n" + "=" * 70)
print("T4: REGIME DISTRIBUTION")
print("=" * 70)

regime_counts = {}
for p in ALL_TARGETS:
    regime_counts[p] = Counter()
    for d in prefix_data[p]:
        r = d['regime']
        if r:
            regime_counts[p][r] += 1

print("\n  REGIME distribution (%):")
regimes_sorted = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
header = "  {:5s}".format("") + "".join(f"  {r:>10s}" for r in regimes_sorted)
print(header)
for p in ALL_TARGETS:
    total = sum(regime_counts[p].values())
    vals = []
    for r in regimes_sorted:
        n = regime_counts[p].get(r, 0)
        vals.append(f"  {100*n/total:>9.1f}%" if total > 0 else f"  {'n/a':>9s}")
    print(f"  {p:5s}" + "".join(vals))

prep_reg = {p: regime_counts[p] for p in PREP_PREFIXES}
chi2_reg, p_reg, dof_reg, V_reg = chi2_test(prep_reg)
print(f"\n  REGIME chi2 (prep PREFIXes): chi2={chi2_reg:.1f} dof={dof_reg} p={p_reg:.6f} V={V_reg:.3f}")

all_reg = {p: regime_counts[p] for p in ALL_TARGETS}
chi2_reg_all, p_reg_all, dof_reg_all, V_reg_all = chi2_test(all_reg)
print(f"  REGIME chi2 (all incl ch):   chi2={chi2_reg_all:.1f} dof={dof_reg_all} p={p_reg_all:.6f} V={V_reg_all:.3f}")

t4_verdict = "DIFFERENTIATED" if p_reg < 0.01 else "PARTIAL" if p_reg < 0.05 else "NOT_DIFFERENTIATED"
print(f"\n  T4 Verdict: {t4_verdict}")

# ============================================================
# T5: SPECIFIC MIDDLE VOCABULARY
# ============================================================
print("\n" + "=" * 70)
print("T5: SPECIFIC MIDDLE VOCABULARY")
print("=" * 70)

middle_counts = {}
for p in ALL_TARGETS:
    middle_counts[p] = Counter()
    for d in prefix_data[p]:
        if d['middle']:
            middle_counts[p][d['middle']] += 1

print("\n  Top 10 MIDDLEs per prefix:")
t5_top_middles = {}
for p in ALL_TARGETS:
    total = sum(middle_counts[p].values())
    top10 = middle_counts[p].most_common(10)
    t5_top_middles[p] = [(m, n) for m, n in top10]
    top_str = " ".join(f"{m}:{n}" for m, n in top10[:5])
    top_str2 = " ".join(f"{m}:{n}" for m, n in top10[5:10])
    print(f"    {p:5s}: {top_str}")
    if top_str2:
        print(f"    {'':5s}  {top_str2}")

# Pairwise Jaccard similarity on MIDDLE sets
print("\n  Pairwise Jaccard (MIDDLE type sets) among prep PREFIXes:")
t5_jaccard = {}
for p1, p2 in combinations(PREP_PREFIXES, 2):
    s1 = set(middle_counts[p1].keys())
    s2 = set(middle_counts[p2].keys())
    j = jaccard(s1, s2)
    key = f"{p1}_vs_{p2}"
    t5_jaccard[key] = round(j, 4)
    print(f"    {p1:4s} vs {p2:4s}: J={j:.4f}  |{p1}|={len(s1)} |{p2}|={len(s2)} |inter|={len(s1&s2)}")

# Prep vs bare ch Jaccard
print("\n  Prep vs bare ch Jaccard:")
t5_jaccard_bare = {}
for p in PREP_PREFIXES:
    s1 = set(middle_counts[p].keys())
    s2 = set(middle_counts[BARE_CH].keys())
    j = jaccard(s1, s2)
    t5_jaccard_bare[f"{p}_vs_ch"] = round(j, 4)
    print(f"    {p:4s} vs ch: J={j:.4f}  |{p}|={len(s1)} |ch|={len(s2)} |inter|={len(s1&s2)}")

# Unique MIDDLEs per prep prefix (not shared with any other prep prefix)
print("\n  Unique MIDDLEs (exclusive to one prep PREFIX):")
all_prep_middles = {p: set(middle_counts[p].keys()) for p in PREP_PREFIXES}
t5_unique = {}
for p in PREP_PREFIXES:
    others = set()
    for p2 in PREP_PREFIXES:
        if p2 != p:
            others |= all_prep_middles[p2]
    unique = all_prep_middles[p] - others
    t5_unique[p] = sorted(unique)
    print(f"    {p:5s}: {len(unique)} unique MIDDLEs  (examples: {', '.join(sorted(unique)[:5])})")

# Mean Jaccard
mean_j = sum(t5_jaccard.values()) / len(t5_jaccard) if t5_jaccard else 0
t5_verdict = "DIFFERENTIATED" if mean_j < 0.30 else "PARTIAL" if mean_j < 0.50 else "NOT_DIFFERENTIATED"
print(f"\n  Mean prep-prep Jaccard: {mean_j:.4f}")
print(f"  T5 Verdict: {t5_verdict}")

# ============================================================
# T6: PARAGRAPH POSITION PROFILE
# ============================================================
print("\n" + "=" * 70)
print("T6: PARAGRAPH POSITION PROFILE")
print("=" * 70)

t6_results = {}
for p in ALL_TARGETS:
    para_positions = [d['para_pos'] for d in prefix_data[p] if d['para_pos'] is not None]
    if para_positions:
        mean_pp = sum(para_positions) / len(para_positions)
        var_pp = sum((x - mean_pp) ** 2 for x in para_positions) / len(para_positions)
        std_pp = math.sqrt(var_pp)
        # Paragraph-initial rate
        par_init_pct = 100 * sum(1 for d in prefix_data[p] if d['par_initial']) / len(prefix_data[p])
        t6_results[p] = {
            'mean': round(mean_pp, 4),
            'std': round(std_pp, 4),
            'n': len(para_positions),
            'par_initial_pct': round(par_init_pct, 1),
        }
        print(f"  {p:5s}: mean={mean_pp:.4f} std={std_pp:.4f} n={len(para_positions):5d}  par_initial={par_init_pct:.1f}%")

# Pairwise KS tests among prep prefixes
print("\n  Pairwise KS tests (paragraph position):")
t6_ks_prep = {}
for p1, p2 in combinations(PREP_PREFIXES, 2):
    d1 = [d['para_pos'] for d in prefix_data[p1] if d['para_pos'] is not None]
    d2 = [d['para_pos'] for d in prefix_data[p2] if d['para_pos'] is not None]
    D, p_val = ks_test_2sample(d1, d2)
    key = f"{p1}_vs_{p2}"
    t6_ks_prep[key] = {'D': round(D, 4), 'p': round(p_val, 6)}
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
    print(f"    {p1:4s} vs {p2:4s}: D={D:.4f}  p={p_val:.6f} {sig}")

# Prep vs bare ch
print("\n  Prep vs bare ch (paragraph position):")
t6_ks_bare = {}
for p in PREP_PREFIXES:
    d1 = [d['para_pos'] for d in prefix_data[p] if d['para_pos'] is not None]
    d2 = [d['para_pos'] for d in prefix_data[BARE_CH] if d['para_pos'] is not None]
    D, p_val = ks_test_2sample(d1, d2)
    key = f"{p}_vs_{BARE_CH}"
    t6_ks_bare[key] = {'D': round(D, 4), 'p': round(p_val, 6)}
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
    print(f"    {p:4s} vs {BARE_CH}: D={D:.4f}  p={p_val:.6f} {sig}")

n_para_sig = sum(1 for v in t6_ks_prep.values() if v['p'] < 0.05)
t6_verdict = "DIFFERENTIATED" if n_para_sig >= 3 else "PARTIAL" if n_para_sig >= 1 else "NOT_DIFFERENTIATED"
print(f"\n  T6 Verdict: {t6_verdict} ({n_para_sig}/{len(t6_ks_prep)} prep pairs sig)")

# ============================================================
# T7: SECTION DISTRIBUTION
# ============================================================
print("\n" + "=" * 70)
print("T7: SECTION DISTRIBUTION")
print("=" * 70)

section_counts = {}
for p in ALL_TARGETS:
    section_counts[p] = Counter()
    for d in prefix_data[p]:
        section_counts[p][d['section']] += 1

sections_sorted = sorted(set(s for c in section_counts.values() for s in c.keys()))
print("\n  Section distribution (%):")
header = "  {:5s}".format("") + "".join(f"  {s:>6s}" for s in sections_sorted)
print(header)
for p in ALL_TARGETS:
    total = sum(section_counts[p].values())
    vals = []
    for s in sections_sorted:
        n = section_counts[p].get(s, 0)
        vals.append(f"  {100*n/total:>5.1f}%" if total > 0 else f"  {'n/a':>5s}")
    print(f"  {p:5s}" + "".join(vals))

prep_sec = {p: section_counts[p] for p in PREP_PREFIXES}
chi2_sec, p_sec, dof_sec, V_sec = chi2_test(prep_sec)
print(f"\n  Section chi2 (prep PREFIXes): chi2={chi2_sec:.1f} dof={dof_sec} p={p_sec:.6f} V={V_sec:.3f}")

all_sec = {p: section_counts[p] for p in ALL_TARGETS}
chi2_sec_all, p_sec_all, dof_sec_all, V_sec_all = chi2_test(all_sec)
print(f"  Section chi2 (all incl ch):   chi2={chi2_sec_all:.1f} dof={dof_sec_all} p={p_sec_all:.6f} V={V_sec_all:.3f}")

t7_verdict = "DIFFERENTIATED" if p_sec < 0.01 else "PARTIAL" if p_sec < 0.05 else "NOT_DIFFERENTIATED"
print(f"\n  T7 Verdict: {t7_verdict}")

# ============================================================
# T8: BARE CH COMPARISON (DIVERGENCE SCORES)
# ============================================================
print("\n" + "=" * 70)
print("T8: BARE CH COMPARISON")
print("=" * 70)

print("\n  Divergence from bare ch across all dimensions:")
t8_divergence = {}
for p in PREP_PREFIXES:
    scores = {}

    # Position KS
    d1 = [d['norm_pos'] for d in prefix_data[p]]
    d2 = [d['norm_pos'] for d in prefix_data[BARE_CH]]
    D, p_val = ks_test_2sample(d1, d2)
    scores['position_KS'] = {'D': round(D, 4), 'p': round(p_val, 6)}

    # Suffix chi2
    sfx_pair = {p: suffix_counts[p], BARE_CH: suffix_counts[BARE_CH]}
    chi2_s, p_s, dof_s, V_s = chi2_test(sfx_pair)
    scores['suffix_chi2'] = {'chi2': round(chi2_s, 1), 'p': round(p_s, 6), 'V': round(V_s, 3)}

    # REGIME chi2
    reg_pair = {p: regime_counts[p], BARE_CH: regime_counts[BARE_CH]}
    chi2_r, p_r, dof_r, V_r = chi2_test(reg_pair)
    scores['regime_chi2'] = {'chi2': round(chi2_r, 1), 'p': round(p_r, 6), 'V': round(V_r, 3)}

    # Section chi2
    sec_pair = {p: section_counts[p], BARE_CH: section_counts[BARE_CH]}
    chi2_sc, p_sc, dof_sc, V_sc = chi2_test(sec_pair)
    scores['section_chi2'] = {'chi2': round(chi2_sc, 1), 'p': round(p_sc, 6), 'V': round(V_sc, 3)}

    # Paragraph position KS
    d1 = [d['para_pos'] for d in prefix_data[p] if d['para_pos'] is not None]
    d2 = [d['para_pos'] for d in prefix_data[BARE_CH] if d['para_pos'] is not None]
    D_pp, p_pp = ks_test_2sample(d1, d2)
    scores['para_pos_KS'] = {'D': round(D_pp, 4), 'p': round(p_pp, 6)}

    # MIDDLE Jaccard
    s1 = set(middle_counts[p].keys())
    s2 = set(middle_counts[BARE_CH].keys())
    j = jaccard(s1, s2)
    scores['middle_jaccard'] = round(j, 4)

    # Predecessor chi2
    pred_pair = {p: pred_counts[p], BARE_CH: pred_counts[BARE_CH]}
    chi2_pr, p_pr, dof_pr, V_pr = chi2_test(pred_pair)
    scores['pred_chi2'] = {'chi2': round(chi2_pr, 1), 'p': round(p_pr, 6), 'V': round(V_pr, 3)}

    # Successor chi2
    succ_pair = {p: succ_counts[p], BARE_CH: succ_counts[BARE_CH]}
    chi2_su, p_su, dof_su, V_su = chi2_test(succ_pair)
    scores['succ_chi2'] = {'chi2': round(chi2_su, 1), 'p': round(p_su, 6), 'V': round(V_su, 3)}

    t8_divergence[p] = scores

    # Count significant dimensions
    sig_dims = 0
    sig_names = []
    for dim_name, dim_val in scores.items():
        if isinstance(dim_val, dict):
            pv = dim_val.get('p', 1.0)
            if pv < 0.05:
                sig_dims += 1
                sig_names.append(dim_name)

    print(f"\n  {p} vs ch:")
    print(f"    Position KS:    D={scores['position_KS']['D']:.4f}  p={scores['position_KS']['p']:.6f}")
    print(f"    Suffix chi2:    V={scores['suffix_chi2']['V']:.3f}  p={scores['suffix_chi2']['p']:.6f}")
    print(f"    REGIME chi2:    V={scores['regime_chi2']['V']:.3f}  p={scores['regime_chi2']['p']:.6f}")
    print(f"    Section chi2:   V={scores['section_chi2']['V']:.3f}  p={scores['section_chi2']['p']:.6f}")
    print(f"    Para pos KS:    D={scores['para_pos_KS']['D']:.4f}  p={scores['para_pos_KS']['p']:.6f}")
    print(f"    MIDDLE Jaccard: {scores['middle_jaccard']:.4f}")
    print(f"    Pred chi2:      V={scores['pred_chi2']['V']:.3f}  p={scores['pred_chi2']['p']:.6f}")
    print(f"    Succ chi2:      V={scores['succ_chi2']['V']:.3f}  p={scores['succ_chi2']['p']:.6f}")
    print(f"    Significant dimensions: {sig_dims}/7  ({', '.join(sig_names)})")

# Overall T8 verdict
total_sig = sum(
    sum(1 for dim_name, dim_val in scores.items()
        if isinstance(dim_val, dict) and dim_val.get('p', 1.0) < 0.05)
    for scores in t8_divergence.values()
)
max_possible = 7 * len(PREP_PREFIXES)  # 7 testable dims x 5 preps
t8_verdict = "DIFFERENTIATED" if total_sig > max_possible * 0.5 else "PARTIAL" if total_sig > max_possible * 0.2 else "NOT_DIFFERENTIATED"
print(f"\n  T8 Verdict: {t8_verdict} ({total_sig}/{max_possible} total significant)")

# ============================================================
# OVERALL SYNTHESIS
# ============================================================
print("\n" + "=" * 70)
print("OVERALL SYNTHESIS")
print("=" * 70)

verdicts = {
    'T1_position': t1_verdict,
    'T2_context': t2_verdict,
    'T3_suffix': t3_verdict,
    'T4_regime': t4_verdict,
    'T5_vocabulary': t5_verdict,
    'T6_paragraph': t6_verdict,
    'T7_section': t7_verdict,
    'T8_bare_ch': t8_verdict,
}

n_diff = sum(1 for v in verdicts.values() if v == "DIFFERENTIATED")
n_partial = sum(1 for v in verdicts.values() if v == "PARTIAL")
n_null = sum(1 for v in verdicts.values() if v == "NOT_DIFFERENTIATED")

print(f"\n  Results: {n_diff} DIFFERENTIATED, {n_partial} PARTIAL, {n_null} NOT_DIFFERENTIATED")
for test, verdict in verdicts.items():
    mark = "+++" if verdict == "DIFFERENTIATED" else "++-" if verdict == "PARTIAL" else "---"
    print(f"    {mark} {test}: {verdict}")

if n_diff >= 4:
    overall = "PREP_PREFIXES_DIFFERENTIATED"
    overall_text = ("Prep PREFIXes show genuine multi-dimensional differentiation despite "
                    "C1221's finding of identical MIDDLE category content. The modifier "
                    "characters (p, t, d, l) alter non-content dimensions: position, suffix, "
                    "REGIME, section, or sequential context.")
elif n_diff + n_partial >= 4:
    overall = "PREP_PREFIXES_PARTIALLY_DIFFERENTIATED"
    overall_text = ("Prep PREFIXes show partial differentiation on some dimensions but not "
                    "others. C1221's finding of identical MIDDLE content holds, but modifiers "
                    "still have measurable effects on non-content dimensions.")
else:
    overall = "PREP_PREFIXES_NOT_DIFFERENTIATED"
    overall_text = ("Prep PREFIXes are NOT differentiated on any non-content dimension. "
                    "C1221's finding of identical behavior generalizes beyond MIDDLE content. "
                    "The modifier characters (p, t, d, l) are truly interchangeable in the "
                    "h-base context.")

print(f"\n  OVERALL VERDICT: {overall}")
print(f"  {overall_text}")

# ============================================================
# SAVE RESULTS
# ============================================================
results = {
    '_metadata': {
        'phase': 'PREP_PREFIX_PROFILING',
        'phase_number': 508,
        'description': 'Comprehensive profiling of prep PREFIXes (pch, tch, dch, lch, te)',
        'background': 'C1221 showed identical MIDDLE content. C1394 provides atom-level modifier functions.',
        'token_counts': {p: len(prefix_data[p]) for p in ALL_TARGETS},
    },
    'T1_positional_differentiation': {
        'stats': {k: v for k, v in t1_results.items()},
        'ks_prep_pairs': t1_ks_prep,
        'ks_vs_bare_ch': t1_ks_bare,
        'verdict': t1_verdict,
        'interpretation': f'{n_prep_sig}/{len(t1_ks_prep)} prep pairs significant at p<0.05 for line position',
    },
    'T2_sequential_context': {
        'top3_predecessors': {p: [(int(c), n) for c, n in v] for p, v in t2_top_pred.items()},
        'top3_successors': {p: [(int(c), n) for c, n in v] for p, v in t2_top_succ.items()},
        'pred_chi2_prep': {'chi2': round(chi2_pred, 1), 'p': round(p_pred, 6), 'dof': dof_pred, 'V': round(V_pred, 3)},
        'succ_chi2_prep': {'chi2': round(chi2_succ, 1), 'p': round(p_succ, 6), 'dof': dof_succ, 'V': round(V_succ, 3)},
        'pred_chi2_all': {'chi2': round(chi2_pred_all, 1), 'p': round(p_pred_all, 6), 'dof': dof_pred_all, 'V': round(V_pred_all, 3)},
        'succ_chi2_all': {'chi2': round(chi2_succ_all, 1), 'p': round(p_succ_all, 6), 'dof': dof_succ_all, 'V': round(V_succ_all, 3)},
        'verdict': t2_verdict,
    },
    'T3_suffix_divergence': {
        'top5_suffixes': {p: v for p, v in t3_top_suffix.items()},
        'chi2_prep': {'chi2': round(chi2_sfx, 1), 'p': round(p_sfx, 6), 'dof': dof_sfx, 'V': round(V_sfx, 3)},
        'chi2_all': {'chi2': round(chi2_sfx_all, 1), 'p': round(p_sfx_all, 6), 'dof': dof_sfx_all, 'V': round(V_sfx_all, 3)},
        'bare_rates': {p: round(suffix_counts[p].get('BARE', 0) / max(sum(suffix_counts[p].values()), 1), 4) for p in ALL_TARGETS},
        'verdict': t3_verdict,
    },
    'T4_regime_distribution': {
        'distributions': {p: {r: regime_counts[p].get(r, 0) for r in regimes_sorted} for p in ALL_TARGETS},
        'chi2_prep': {'chi2': round(chi2_reg, 1), 'p': round(p_reg, 6), 'dof': dof_reg, 'V': round(V_reg, 3)},
        'chi2_all': {'chi2': round(chi2_reg_all, 1), 'p': round(p_reg_all, 6), 'dof': dof_reg_all, 'V': round(V_reg_all, 3)},
        'verdict': t4_verdict,
    },
    'T5_middle_vocabulary': {
        'top10_middles': {p: v for p, v in t5_top_middles.items()},
        'jaccard_prep_pairs': t5_jaccard,
        'jaccard_vs_bare_ch': t5_jaccard_bare,
        'unique_middles': t5_unique,
        'mean_prep_jaccard': round(mean_j, 4),
        'verdict': t5_verdict,
    },
    'T6_paragraph_position': {
        'stats': t6_results,
        'ks_prep_pairs': t6_ks_prep,
        'ks_vs_bare_ch': t6_ks_bare,
        'verdict': t6_verdict,
    },
    'T7_section_distribution': {
        'distributions': {p: {s: section_counts[p].get(s, 0) for s in sections_sorted} for p in ALL_TARGETS},
        'chi2_prep': {'chi2': round(chi2_sec, 1), 'p': round(p_sec, 6), 'dof': dof_sec, 'V': round(V_sec, 3)},
        'chi2_all': {'chi2': round(chi2_sec_all, 1), 'p': round(p_sec_all, 6), 'dof': dof_sec_all, 'V': round(V_sec_all, 3)},
        'verdict': t7_verdict,
    },
    'T8_bare_ch_comparison': {
        'per_prefix_divergence': t8_divergence,
        'total_significant': total_sig,
        'max_possible': max_possible,
        'verdict': t8_verdict,
    },
    'verdicts': verdicts,
    'overall_verdict': overall,
    'overall_interpretation': overall_text,
}

output_path = OUTPUT_DIR / 'prep_prefix_profiling.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to: {output_path}")
print("DONE.")
