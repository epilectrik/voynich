#!/usr/bin/env python3
"""
B_LEGALITY_GRADIENT - Legality Gradient Analysis

Tests whether the A-legal/A-illegal token ratio follows a predictable
trajectory within B folios, correlated with SETUP->WORK->CLOSE line syntax.

Hypothesis: B folios open with procedure-identity vocabulary (B-exclusive,
mostly illegal under A filtering) then transition to shared operational
vocabulary (mostly legal). This corresponds to the SETUP->WORK transition
documented in C556.

Tests:
  T1: Within-line position gradient (quintile -> accessibility)
  T2: Role-correlated legality (CC/EN/FL/FQ/AX -> accessibility)
  T3: Across-line gradient (line position -> per-line accessibility)
  T4: SETUP-WORK-CLOSE thirds comparison
  T5: Role position interaction (SETUP roles vs WORK roles legality)

Dependencies:
  - scripts/voynich.py (Transcript, Morphology, RecordAnalyzer)
  - phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json (RI/PP)
  - phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json (token->class)

Output: results/legality_gradient.json
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, RecordAnalyzer

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONSTANTS: Role taxonomy (from B_LINE_SEQUENTIAL_STRUCTURE)
# ============================================================
CLASS_TO_ROLE = {
    10: 'CC', 11: 'CC', 12: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 35: 'EN',
    36: 'EN', 37: 'EN', 39: 'EN', 41: 'EN', 42: 'EN', 43: 'EN',
    44: 'EN', 45: 'EN', 46: 'EN', 47: 'EN', 48: 'EN', 49: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 13: 'FQ', 14: 'FQ', 23: 'FQ',
}
for c in list(range(1, 7)) + list(range(15, 17)) + list(range(18, 23)) + list(range(24, 30)):
    if c not in CLASS_TO_ROLE:
        CLASS_TO_ROLE[c] = 'AX'

ROLES = ['CC', 'EN', 'FL', 'FQ', 'AX']

print("=" * 70)
print("B_LEGALITY_GRADIENT - Legality Gradient Analysis")
print("=" * 70)

# ============================================================
# SECTION 1: Load & Pre-compute
# ============================================================
print("\n--- Section 1: Load & Pre-compute ---")

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# Load class->token map
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm_raw = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in ctm_raw['token_to_class'].items()}
token_to_role = {}
for tok, cls in token_to_class.items():
    token_to_role[tok] = CLASS_TO_ROLE.get(cls, 'UN')

# ============================================================
# Pre-compute per-A-folio PP pools
# ============================================================
print("Building per-A-folio PP pools...")
a_folios = analyzer.get_folios()
morph_cache = {}

def get_morph(word):
    if word not in morph_cache:
        morph_cache[word] = morph.extract(word)
    return morph_cache[word]

a_folio_pp = {}  # folio -> (mids, prefs, sufs)
for fol in a_folios:
    records = analyzer.analyze_folio(fol)
    mids, prefs, sufs = set(), set(), set()
    for rec in records:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                mids.add(t.middle)
                m = get_morph(t.word)
                if m.prefix:
                    prefs.add(m.prefix)
                if m.suffix:
                    sufs.add(m.suffix)
    a_folio_pp[fol] = (mids, prefs, sufs)

print(f"  {len(a_folios)} A folios processed")

# ============================================================
# Build B token inventory (pre-compute morphology)
# ============================================================
print("Building B token inventory...")
b_tokens = {}  # word -> (prefix, middle, suffix)
for token in tx.currier_b():
    w = token.word
    if w in b_tokens:
        continue
    m = get_morph(w)
    if m.middle:
        b_tokens[w] = (m.prefix, m.middle, m.suffix)

b_middles_set = set(mid for _, mid, _ in b_tokens.values())
b_prefixes_set = set(pref for pref, _, _ in b_tokens.values() if pref)
b_suffixes_set = set(suf for _, _, suf in b_tokens.values() if suf)
print(f"  {len(b_tokens)} unique B token types with morphology")

# ============================================================
# Compute per-A-folio legal B token sets (C502.a filtering)
# ============================================================
print("Computing per-A-folio legal B token sets...")
a_folio_legal = {}  # A folio -> set of legal B tokens

for fol in a_folios:
    mids, prefs, sufs = a_folio_pp[fol]
    shared_mids = mids & b_middles_set
    shared_prefs = prefs & b_prefixes_set
    shared_sufs = sufs & b_suffixes_set
    legal = set()
    for tok, (pref, mid, suf) in b_tokens.items():
        if mid in shared_mids:
            if (pref is None or pref in shared_prefs):
                if (suf is None or suf in shared_sufs):
                    legal.add(tok)
    a_folio_legal[fol] = legal

# Compute per-B-token accessibility: fraction of A folios making it legal
n_a = len(a_folios)
b_token_access = {}  # B token -> fraction of A folios making it legal
b_token_legal_count = defaultdict(int)
for fol in a_folios:
    for tok in a_folio_legal[fol]:
        b_token_legal_count[tok] += 1

for tok in b_tokens:
    b_token_access[tok] = b_token_legal_count[tok] / n_a

# Report
access_vals = list(b_token_access.values())
print(f"  Mean accessibility: {np.mean(access_vals):.3f}")
print(f"  Median accessibility: {np.median(access_vals):.3f}")
print(f"  Zero-access tokens: {sum(1 for v in access_vals if v == 0)}")
print(f"  Full-access tokens: {sum(1 for v in access_vals if v == 1.0)}")

# ============================================================
# Build B folio line data with positions
# ============================================================
print("\nBuilding B folio line data...")
# Collect all B tokens grouped by (folio, line) preserving order
b_folio_line_tokens = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    b_folio_line_tokens[token.folio][token.line].append(token.word)

# Build ordered line keys per folio
def line_sort_key(line_str):
    digits = ''
    for ch in line_str:
        if ch.isdigit():
            digits += ch
        else:
            break
    rest = line_str[len(digits):]
    return (int(digits) if digits else 0, rest)

b_folio_lines = {}  # folio -> [line_key_1, line_key_2, ...]
for bfol in b_folio_line_tokens:
    b_folio_lines[bfol] = sorted(b_folio_line_tokens[bfol].keys(), key=line_sort_key)

n_b_folios = len(b_folio_lines)
total_b_lines = sum(len(lines) for lines in b_folio_lines.values())
print(f"  {n_b_folios} B folios, {total_b_lines} lines")

# ============================================================
# SECTION 2: T1 - Within-Line Position Gradient
# ============================================================
print("\n--- T1: Within-Line Position Gradient ---")

from scipy.stats import spearmanr, kruskal

# For every B token occurrence: (normalized position, accessibility)
quintile_access = defaultdict(list)  # quintile 0-4 -> [accessibility values]
all_positions = []
all_access = []

for bfol in b_folio_line_tokens:
    for line_key in b_folio_lines[bfol]:
        tokens = b_folio_line_tokens[bfol][line_key]
        n = len(tokens)
        if n < 2:
            continue
        for i, tok in enumerate(tokens):
            if tok not in b_token_access:
                continue
            norm_pos = i / (n - 1)  # 0.0 = first, 1.0 = last
            acc = b_token_access[tok]
            all_positions.append(norm_pos)
            all_access.append(acc)
            q = min(int(norm_pos * 5), 4)
            quintile_access[q].append(acc)

rho_pos, p_pos = spearmanr(all_positions, all_access)
quintile_means = {q: float(np.mean(vals)) for q, vals in sorted(quintile_access.items())}
quintile_counts = {q: len(vals) for q, vals in sorted(quintile_access.items())}

# KW test across quintiles
kw_stat, kw_p = kruskal(*[quintile_access[q] for q in range(5)])

print(f"  Spearman rho(position, accessibility): {rho_pos:.4f}, p={p_pos:.4e}")
print(f"  KW across quintiles: H={kw_stat:.1f}, p={kw_p:.4e}")
for q in range(5):
    lo = q * 0.2
    hi = (q + 1) * 0.2
    print(f"    Q{q} [{lo:.1f}-{hi:.1f}]: mean={quintile_means[q]:.4f} (n={quintile_counts[q]})")

T1_pass = abs(rho_pos) > 0.02 and p_pos < 0.001
T1_direction = "initial-higher" if rho_pos < 0 else "final-higher"
print(f"  T1 verdict: {'PASS' if T1_pass else 'FAIL'} (direction: {T1_direction})")

# ============================================================
# SECTION 3: T2 - Role-Correlated Legality
# ============================================================
print("\n--- T2: Role-Correlated Legality ---")

role_access = defaultdict(list)
role_counts = defaultdict(int)
unclassified_access = []

for tok, acc in b_token_access.items():
    role = token_to_role.get(tok, 'UN')
    if role == 'UN':
        unclassified_access.append(acc)
    else:
        role_access[role].append(acc)
    role_counts[role] += 1

print(f"  Role accessibility (per unique token type):")
role_means = {}
for role in ROLES + ['UN']:
    vals = role_access[role] if role != 'UN' else unclassified_access
    if vals:
        m = float(np.mean(vals))
        role_means[role] = m
        print(f"    {role:3s}: mean={m:.4f} (n={len(vals)})")

# KW test across roles
role_groups = [role_access[r] for r in ROLES if role_access[r]]
if len(role_groups) >= 2:
    kw_role_stat, kw_role_p = kruskal(*role_groups)
else:
    kw_role_stat, kw_role_p = 0.0, 1.0

print(f"  KW across classified roles: H={kw_role_stat:.1f}, p={kw_role_p:.4e}")

# Compare operational (EN+FL) vs structural (CC+AX)
operational = role_access['EN'] + role_access['FL']
structural = role_access['CC'] + role_access['AX']
if operational and structural:
    from scipy.stats import mannwhitneyu
    u_stat, u_p = mannwhitneyu(operational, structural, alternative='two-sided')
    op_mean = float(np.mean(operational))
    st_mean = float(np.mean(structural))
    print(f"  Operational (EN+FL) mean: {op_mean:.4f}")
    print(f"  Structural (CC+AX) mean: {st_mean:.4f}")
    print(f"  Mann-Whitney U: U={u_stat:.0f}, p={u_p:.4e}")
    T2_pass = kw_role_p < 0.001
else:
    u_p = 1.0
    op_mean = 0.0
    st_mean = 0.0
    T2_pass = False

print(f"  T2 verdict: {'PASS' if T2_pass else 'FAIL'}")

# ============================================================
# SECTION 4: T3 - Across-Line Gradient
# ============================================================
print("\n--- T3: Across-Line Gradient ---")

# Per-folio: compute mean accessibility per line, normalized line position
folio_line_rhos = []
all_line_positions = []
all_line_access_means = []

for bfol in b_folio_lines:
    lines = b_folio_lines[bfol]
    n_lines = len(lines)
    if n_lines < 4:
        continue
    line_means = []
    line_positions = []
    for li, lk in enumerate(lines):
        tokens = b_folio_line_tokens[bfol][lk]
        acc_vals = [b_token_access[t] for t in tokens if t in b_token_access]
        if not acc_vals:
            continue
        line_means.append(float(np.mean(acc_vals)))
        line_positions.append(li / (n_lines - 1))
    if len(line_means) >= 4:
        rho, p = spearmanr(line_positions, line_means)
        folio_line_rhos.append(rho)
        all_line_positions.extend(line_positions)
        all_line_access_means.extend(line_means)

mean_rho = float(np.mean(folio_line_rhos))
median_rho = float(np.median(folio_line_rhos))
pos_rho_count = sum(1 for r in folio_line_rhos if r > 0)
neg_rho_count = sum(1 for r in folio_line_rhos if r < 0)

# Global correlation
global_rho, global_p = spearmanr(all_line_positions, all_line_access_means)

print(f"  Per-folio Spearman(line_pos, mean_access):")
print(f"    Mean rho: {mean_rho:.4f}")
print(f"    Median rho: {median_rho:.4f}")
print(f"    Positive: {pos_rho_count}/{len(folio_line_rhos)}")
print(f"    Negative: {neg_rho_count}/{len(folio_line_rhos)}")
print(f"  Global correlation: rho={global_rho:.4f}, p={global_p:.4e}")

# Bin into thirds
third_access = defaultdict(list)
for pos, acc in zip(all_line_positions, all_line_access_means):
    if pos < 0.333:
        third_access['first'].append(acc)
    elif pos < 0.667:
        third_access['middle'].append(acc)
    else:
        third_access['last'].append(acc)

for t in ['first', 'middle', 'last']:
    vals = third_access[t]
    print(f"    {t:6s} third: mean={np.mean(vals):.4f} (n={len(vals)})")

T3_pass = abs(global_rho) > 0.02 and global_p < 0.01
T3_direction = "first-higher" if global_rho < 0 else "last-higher"
print(f"  T3 verdict: {'PASS' if T3_pass else 'FAIL'} (direction: {T3_direction})")

# ============================================================
# SECTION 5: T4 - SETUP / WORK / CLOSE Thirds (Within-Line)
# ============================================================
print("\n--- T4: SETUP / WORK / CLOSE Thirds (Within-Line) ---")

# For each token occurrence: categorize by within-line third
setup_access = []   # first third of line
work_access = []    # middle third
close_access = []   # last third

for bfol in b_folio_line_tokens:
    for line_key in b_folio_lines[bfol]:
        tokens = b_folio_line_tokens[bfol][line_key]
        n = len(tokens)
        if n < 3:
            continue
        for i, tok in enumerate(tokens):
            if tok not in b_token_access:
                continue
            frac = i / (n - 1) if n > 1 else 0.5
            acc = b_token_access[tok]
            if frac < 0.333:
                setup_access.append(acc)
            elif frac < 0.667:
                work_access.append(acc)
            else:
                close_access.append(acc)

setup_mean = float(np.mean(setup_access))
work_mean = float(np.mean(work_access))
close_mean = float(np.mean(close_access))

kw_swc_stat, kw_swc_p = kruskal(setup_access, work_access, close_access)

print(f"  SETUP  (first 1/3):  mean={setup_mean:.4f} (n={len(setup_access)})")
print(f"  WORK   (middle 1/3): mean={work_mean:.4f} (n={len(work_access)})")
print(f"  CLOSE  (last 1/3):   mean={close_mean:.4f} (n={len(close_access)})")
print(f"  KW test: H={kw_swc_stat:.1f}, p={kw_swc_p:.4e}")

# Effect size: SETUP vs WORK
if setup_access and work_access:
    u_sw, p_sw = mannwhitneyu(setup_access, work_access, alternative='two-sided')
    print(f"  SETUP vs WORK: U={u_sw:.0f}, p={p_sw:.4e}")

T4_pass = kw_swc_p < 0.001
print(f"  T4 verdict: {'PASS' if T4_pass else 'FAIL'}")

# ============================================================
# SECTION 6: T5 - Role x Position Interaction
# ============================================================
print("\n--- T5: Role x Position Interaction ---")

# For each B token occurrence: record (role, normalized position, accessibility)
role_position_access = defaultdict(lambda: defaultdict(list))

for bfol in b_folio_line_tokens:
    for line_key in b_folio_lines[bfol]:
        tokens = b_folio_line_tokens[bfol][line_key]
        n = len(tokens)
        if n < 2:
            continue
        for i, tok in enumerate(tokens):
            if tok not in b_token_access:
                continue
            role = token_to_role.get(tok, 'UN')
            frac = i / (n - 1)
            acc = b_token_access[tok]
            zone = 'SETUP' if frac < 0.333 else ('WORK' if frac < 0.667 else 'CLOSE')
            role_position_access[role][zone].append(acc)

print(f"  Role x Zone mean accessibility:")
print(f"  {'Role':>4s}  {'SETUP':>8s}  {'WORK':>8s}  {'CLOSE':>8s}  {'Gradient':>10s}")
role_gradients = {}
for role in ROLES + ['UN']:
    zones = role_position_access[role]
    s_mean = float(np.mean(zones['SETUP'])) if zones['SETUP'] else 0.0
    w_mean = float(np.mean(zones['WORK'])) if zones['WORK'] else 0.0
    c_mean = float(np.mean(zones['CLOSE'])) if zones['CLOSE'] else 0.0
    gradient = c_mean - s_mean
    role_gradients[role] = gradient
    print(f"  {role:>4s}  {s_mean:>8.4f}  {w_mean:>8.4f}  {c_mean:>8.4f}  {gradient:>+10.4f}")

# Test: do all roles show the same gradient direction?
gradient_directions = [1 if g > 0 else -1 for g in role_gradients.values() if abs(g) > 0.001]
unanimous = len(set(gradient_directions)) == 1 if gradient_directions else False
T5_pass = unanimous and T4_pass
print(f"  Gradient unanimous across roles: {unanimous}")
print(f"  T5 verdict: {'PASS' if T5_pass else 'FAIL'}")

# ============================================================
# SECTION 7: Special token analysis
# ============================================================
print("\n--- Special Token Analysis ---")

special_tokens = ['daiin', 'ol', 'ar', 'al', 'or', 'aiin', 'chedy', 'shedy',
                  'qokeedy', 'qokedy', 'qokaiin', 'lkeedy', 'lkedy']
print(f"  {'Token':>12s}  {'Access':>7s}  {'Class':>5s}  {'Role':>4s}")
for tok in special_tokens:
    acc = b_token_access.get(tok, -1)
    cls = token_to_class.get(tok, -1)
    role = token_to_role.get(tok, '??')
    if acc >= 0:
        print(f"  {tok:>12s}  {acc:>7.3f}  {str(cls):>5s}  {role:>4s}")

# daiin specifically
daiin_acc = b_token_access.get('daiin', -1)
if daiin_acc >= 0:
    # Compare to CC average
    cc_mean = float(np.mean(role_access['CC'])) if role_access['CC'] else 0
    print(f"\n  daiin accessibility: {daiin_acc:.3f}")
    print(f"  CC role average: {cc_mean:.3f}")
    print(f"  daiin vs CC: {'below' if daiin_acc < cc_mean else 'above'} average")

# ============================================================
# SECTION 8: Accessibility distribution by B-exclusivity
# ============================================================
print("\n--- Accessibility Distribution ---")

zero_count = sum(1 for v in b_token_access.values() if v == 0)
low_count = sum(1 for v in b_token_access.values() if 0 < v <= 0.1)
mid_count = sum(1 for v in b_token_access.values() if 0.1 < v <= 0.5)
high_count = sum(1 for v in b_token_access.values() if 0.5 < v < 1.0)
full_count = sum(1 for v in b_token_access.values() if v == 1.0)
total = len(b_token_access)

print(f"  Zero (B-exclusive):   {zero_count:4d} ({100*zero_count/total:.1f}%)")
print(f"  Low (0-10%):          {low_count:4d} ({100*low_count/total:.1f}%)")
print(f"  Medium (10-50%):      {mid_count:4d} ({100*mid_count/total:.1f}%)")
print(f"  High (50-99%):        {high_count:4d} ({100*high_count/total:.1f}%)")
print(f"  Full (100%):          {full_count:4d} ({100*full_count/total:.1f}%)")

# Role distribution of zero-access tokens
print(f"\n  Zero-access tokens by role:")
for role in ROLES + ['UN']:
    zero_role = sum(1 for tok, acc in b_token_access.items()
                    if acc == 0 and token_to_role.get(tok, 'UN') == role)
    total_role = role_counts.get(role, 0)
    if total_role > 0:
        print(f"    {role:3s}: {zero_role}/{total_role} ({100*zero_role/total_role:.1f}%)")

# ============================================================
# SECTION 9: Per-B-folio legality rate under best A folio
# ============================================================
print("\n--- Per-B-Folio Legality Under Best A Folio ---")

b_folio_best_legal = {}
for bfol in b_folio_line_tokens:
    all_b_toks = []
    for lk in b_folio_lines[bfol]:
        all_b_toks.extend(b_folio_line_tokens[bfol][lk])
    best_rate = 0.0
    best_a = None
    for afol in a_folios:
        legal = a_folio_legal[afol]
        rate = sum(1 for t in all_b_toks if t in legal) / len(all_b_toks) if all_b_toks else 0
        if rate > best_rate:
            best_rate = rate
            best_a = afol
    b_folio_best_legal[bfol] = (best_a, best_rate)

rates = [r for _, r in b_folio_best_legal.values()]
print(f"  Mean best-A legality: {np.mean(rates):.3f}")
print(f"  Median: {np.median(rates):.3f}")
print(f"  Range: [{min(rates):.3f}, {max(rates):.3f}]")

# ============================================================
# Save results
# ============================================================
print("\n--- Saving Results ---")

results = {
    "metadata": {
        "phase": "B_LEGALITY_GRADIENT",
        "script": "legality_gradient.py",
        "timestamp": str(datetime.now()),
        "n_a_folios": len(a_folios),
        "n_b_folios": n_b_folios,
        "n_b_token_types": len(b_tokens),
        "mean_accessibility": float(np.mean(access_vals)),
        "median_accessibility": float(np.median(access_vals)),
    },
    "T1_within_line_position": {
        "spearman_rho": float(rho_pos),
        "spearman_p": float(p_pos),
        "kruskal_H": float(kw_stat),
        "kruskal_p": float(kw_p),
        "quintile_means": {str(k): v for k, v in quintile_means.items()},
        "quintile_counts": {str(k): v for k, v in quintile_counts.items()},
        "direction": T1_direction,
        "pass": T1_pass,
    },
    "T2_role_legality": {
        "role_means": {str(k): v for k, v in role_means.items()},
        "role_counts": {str(k): v for k, v in role_counts.items()},
        "kruskal_H": float(kw_role_stat),
        "kruskal_p": float(kw_role_p),
        "operational_mean": float(op_mean),
        "structural_mean": float(st_mean),
        "mw_p": float(u_p),
        "pass": T2_pass,
    },
    "T3_across_line": {
        "global_rho": float(global_rho),
        "global_p": float(global_p),
        "mean_per_folio_rho": float(mean_rho),
        "median_per_folio_rho": float(median_rho),
        "positive_count": pos_rho_count,
        "negative_count": neg_rho_count,
        "third_means": {
            "first": float(np.mean(third_access['first'])),
            "middle": float(np.mean(third_access['middle'])),
            "last": float(np.mean(third_access['last'])),
        },
        "direction": T3_direction,
        "pass": T3_pass,
    },
    "T4_setup_work_close": {
        "setup_mean": setup_mean,
        "work_mean": work_mean,
        "close_mean": close_mean,
        "kruskal_H": float(kw_swc_stat),
        "kruskal_p": float(kw_swc_p),
        "pass": T4_pass,
    },
    "T5_role_position_interaction": {
        "role_gradients": {str(k): float(v) for k, v in role_gradients.items()},
        "unanimous_direction": unanimous,
        "pass": T5_pass,
    },
    "accessibility_distribution": {
        "zero_count": zero_count,
        "low_count": low_count,
        "mid_count": mid_count,
        "high_count": high_count,
        "full_count": full_count,
        "total": total,
    },
    "best_a_folio_legality": {
        "mean_rate": float(np.mean(rates)),
        "median_rate": float(np.median(rates)),
        "min_rate": float(min(rates)),
        "max_rate": float(max(rates)),
    },
    "summary": {
        "T1_pass": T1_pass,
        "T2_pass": T2_pass,
        "T3_pass": T3_pass,
        "T4_pass": T4_pass,
        "T5_pass": T5_pass,
        "pass_count": sum([T1_pass, T2_pass, T3_pass, T4_pass, T5_pass]),
        "total_tests": 5,
    },
}

out_path = RESULTS_DIR / 'legality_gradient.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)
print(f"  Saved to {out_path}")
print(f"\n  SUMMARY: {results['summary']['pass_count']}/5 tests pass")
