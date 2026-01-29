#!/usr/bin/env python3
"""
B_LINE_SEQUENTIAL_STRUCTURE - Script 2: Line Token Trajectory

Measures what evolves at the token/morphological level while class
proportions stay flat (C664-C669).

Tests:
  6. MIDDLE Vocabulary Trajectory (JSD across quartiles, per-MIDDLE positional preference)
  7. PREFIX Combination Trajectory (PREFIX distribution shifts across position)
  8. Suffix Profile Trajectory (suffix pattern evolution within folios)
  9. Articulator Rate Trajectory (outermost morphological layer shifts)
  10. Line Complexity Trajectory (vocabulary diversity across position)

Constraint references:
  C506.b: 73% of within-class MIDDLE pairs JSD > 0.4
  C664-C669: Class-level proportions stationary within folios
  C668: QO lane fraction rho=-0.058

Dependencies:
  - phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json
  - phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json
  - scripts/voynich.py (Transcript, Morphology)

Output: results/line_token_trajectory.json
"""

import json
import sys
import warnings
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONSTANTS
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

MIN_LINES_PER_FOLIO = 8

# PREFIX families (from plan)
PREFIX_FAMILIES = ['ch', 'sh', 'qo', 'da', 'ol', 'ok', 'ot', 'ct']

# Suffix categories
SUFFIX_AIIN = {'aiin'}
SUFFIX_OL = {'ol'}
SUFFIX_Y = {'y'}
SUFFIX_E_FAMILY = {'ey', 'eey', 'edy', 'dy'}


def line_sort_key(line_str):
    digits = ''
    for ch in line_str:
        if ch.isdigit():
            digits += ch
        else:
            break
    rest = line_str[len(digits):]
    return (int(digits) if digits else 0, rest)


def safe_spearmanr(x, y):
    from scipy.stats import spearmanr
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        if len(set(y)) <= 1 or len(x) < 3:
            return 0.0, 1.0
        return spearmanr(x, y)


def safe_kruskal(*groups):
    from scipy.stats import kruskal
    filtered = [g for g in groups if len(g) > 0]
    if len(filtered) < 2:
        return 0.0, 1.0
    all_vals = []
    for g in filtered:
        all_vals.extend(g)
    if len(set(all_vals)) <= 1:
        return 0.0, 1.0
    try:
        return kruskal(*filtered)
    except ValueError:
        return 0.0, 1.0


def classify_suffix(suffix):
    if suffix is None:
        return 'bare'
    if suffix in SUFFIX_AIIN:
        return 'aiin'
    if suffix in SUFFIX_OL:
        return 'ol'
    if suffix in SUFFIX_Y:
        return 'y'
    if suffix in SUFFIX_E_FAMILY:
        return 'e_family'
    return 'other'


def classify_prefix(prefix):
    if prefix is None:
        return 'None'
    for family in PREFIX_FAMILIES:
        if prefix == family:
            return family
    return 'other'


def jsd(p, q):
    """Jensen-Shannon divergence between two probability distributions."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    p = p / p.sum() if p.sum() > 0 else p
    q = q / q.sum() if q.sum() > 0 else q
    m = 0.5 * (p + q)
    # Avoid log(0)
    def kl(a, b):
        mask = (a > 0) & (b > 0)
        return np.sum(a[mask] * np.log2(a[mask] / b[mask]))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


# ============================================================
# SECTION 1: LOAD & PREPARE
# ============================================================
print("=" * 70)
print("B_LINE_SEQUENTIAL_STRUCTURE - Script 2: Line Token Trajectory")
print("=" * 70)
print("\n--- Section 1: Load & Prepare ---")

# Load class token map
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm_raw = json.load(f)
if 'token_to_class' in ctm_raw:
    token_to_class = {tok: int(cls) for tok, cls in ctm_raw['token_to_class'].items()}
else:
    token_to_class = {tok: int(cls) for tok, cls in ctm_raw.items()}
print(f"  Loaded class_token_map: {len(token_to_class)} tokens mapped")

# Load regime mapping
regime_path = PROJECT_ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)
folio_to_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_to_regime[folio] = regime
print(f"  Loaded regime mapping: {len(folio_to_regime)} folios")

# Build morphology cache
morph = Morphology()
morph_cache = {}


def get_morph(word):
    if word not in morph_cache:
        morph_cache[word] = morph.extract(word)
    return morph_cache[word]


# Build per-line feature records
tx = Transcript()

line_records = []  # flat list of per-line feature dicts
folio_lines_raw = defaultdict(lambda: defaultdict(list))
total_b_tokens = 0

for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    total_b_tokens += 1
    folio_lines_raw[token.folio][token.line].append(token.word)

# Filter to folios with >= MIN_LINES
valid_folios = {f for f, lines in folio_lines_raw.items() if len(lines) >= MIN_LINES_PER_FOLIO}
print(f"  Total B tokens: {total_b_tokens}")
print(f"  Valid folios (>={MIN_LINES_PER_FOLIO} lines): {len(valid_folios)}")

# Pre-compute morphology for all B words
all_words = set()
for folio in valid_folios:
    for line_id, words in folio_lines_raw[folio].items():
        all_words.update(words)

for w in all_words:
    get_morph(w)
print(f"  Morphology cache: {len(morph_cache)} words")

# Build per-line feature records
for folio in sorted(valid_folios):
    sorted_lines = sorted(folio_lines_raw[folio].keys(), key=line_sort_key)
    n_lines = len(sorted_lines)

    for idx, line_id in enumerate(sorted_lines):
        words = folio_lines_raw[folio][line_id]
        n_tok = len(words)
        if n_tok == 0:
            continue

        norm_pos = idx / max(n_lines - 1, 1)
        quartile = min(int(norm_pos * 4) + 1, 4)

        # Extract morphological components
        middles = []
        prefixes = []
        suffixes = []
        articulators = []
        prefix_families = []
        suffix_cats = []

        for w in words:
            m = morph_cache.get(w)
            if m:
                middles.append(m.middle)
                prefixes.append(m.prefix)
                suffixes.append(m.suffix)
                articulators.append(m.articulator)
                prefix_families.append(classify_prefix(m.prefix))
                suffix_cats.append(classify_suffix(m.suffix))
            else:
                middles.append(None)
                prefixes.append(None)
                suffixes.append(None)
                articulators.append(None)
                prefix_families.append('None')
                suffix_cats.append('bare')

        # Classes
        classes = [token_to_class.get(w) for w in words]
        roles = [CLASS_TO_ROLE.get(c, 'UNC') if c is not None else 'UNC' for c in classes]

        # Unique counts
        unique_tokens = len(set(words))
        unique_middles = len(set(m for m in middles if m is not None))
        unique_classes = len(set(c for c in classes if c is not None))
        ttr = unique_tokens / n_tok if n_tok > 0 else 0
        mean_token_len = np.mean([len(w) for w in words])

        # Articulator rate
        art_present = sum(1 for a in articulators if a is not None)
        art_rate = art_present / n_tok

        # Prefix family distribution
        pf_counts = Counter(prefix_families)
        # Suffix category distribution
        sc_counts = Counter(suffix_cats)

        line_records.append({
            'folio': folio,
            'line': line_id,
            'n_tokens': n_tok,
            'norm_pos': norm_pos,
            'quartile': quartile,
            'regime': folio_to_regime.get(folio, 'UNKNOWN'),
            # Raw data
            'words': words,
            'middles': [m for m in middles if m is not None],
            'middle_set': set(m for m in middles if m is not None),
            # Computed features
            'unique_tokens': unique_tokens,
            'unique_middles': unique_middles,
            'unique_classes': unique_classes,
            'ttr': ttr,
            'mean_token_len': mean_token_len,
            'art_rate': art_rate,
            'prefix_family_counts': dict(pf_counts),
            'suffix_cat_counts': dict(sc_counts),
        })

n_lines_total = len(line_records)
print(f"  Line records: {n_lines_total}")

regimes = sorted(set(r['regime'] for r in line_records if r['regime'] != 'UNKNOWN'))


# ============================================================
# TEST 6: MIDDLE VOCABULARY TRAJECTORY
# ============================================================
print("\n" + "=" * 70)
print("TEST 6: MIDDLE Vocabulary Trajectory")
print("=" * 70)

# 6a: JSD of MIDDLE frequency distributions across quartiles
# Pool all MIDDLEs within each quartile
all_middles_ever = sorted(set(m for rec in line_records for m in rec['middles']))
mid_idx = {m: i for i, m in enumerate(all_middles_ever)}
n_mid = len(all_middles_ever)
print(f"\n  Total unique MIDDLEs in valid folios: {n_mid}")

q_middle_counts = {q: np.zeros(n_mid) for q in range(1, 5)}
for rec in line_records:
    q = rec['quartile']
    for m in rec['middles']:
        if m in mid_idx:
            q_middle_counts[q][mid_idx[m]] += 1

# Normalize to distributions
q_middle_dists = {}
for q in range(1, 5):
    total = q_middle_counts[q].sum()
    q_middle_dists[q] = q_middle_counts[q] / total if total > 0 else q_middle_counts[q]

# JSD between quartile pairs
jsd_results = {}
for qi in range(1, 5):
    for qj in range(qi + 1, 5):
        j = jsd(q_middle_dists[qi], q_middle_dists[qj])
        key = f"Q{qi}_Q{qj}"
        jsd_results[key] = round(j, 6)
        print(f"  JSD(Q{qi}, Q{qj}) = {j:.6f}")

# Is Q1-Q4 JSD > adjacent-quartile JSDs?
jsd_q1q4 = jsd_results['Q1_Q4']
adj_mean = np.mean([jsd_results['Q1_Q2'], jsd_results['Q2_Q3'], jsd_results['Q3_Q4']])
print(f"\n  JSD(Q1,Q4) = {jsd_q1q4:.6f}")
print(f"  Mean adjacent JSD = {adj_mean:.6f}")
print(f"  Progressive drift: {'YES' if jsd_q1q4 > adj_mean else 'NO'} (ratio={jsd_q1q4/adj_mean:.3f})" if adj_mean > 0 else "  adj_mean = 0")

# 6b: Per-MIDDLE positional preference
# For MIDDLEs with >= 10 occurrences, Spearman rho vs norm_pos
MIN_MIDDLE_OCC = 10
middle_positions = defaultdict(list)  # middle -> [norm_pos, ...]
for rec in line_records:
    for m in rec['middles']:
        middle_positions[m].append(rec['norm_pos'])

frequent_middles = {m: positions for m, positions in middle_positions.items()
                    if len(positions) >= MIN_MIDDLE_OCC}
print(f"\n  MIDDLEs with >={MIN_MIDDLE_OCC} occurrences: {len(frequent_middles)}")

mid_rho_results = {}
sig_middles = []
n_tests = len(frequent_middles)
bonferroni_alpha = 0.05 / n_tests if n_tests > 0 else 0.05

for mid_name, positions in sorted(frequent_middles.items()):
    rho, p = safe_spearmanr(list(range(len(positions))), positions)
    # Actually we want: rho of (occurrence index) vs (norm_pos) isn't right
    # We want: Spearman rho of this MIDDLE's frequency vs norm_pos across lines
    pass

# Better approach: for each frequent MIDDLE, compute its occurrence rate per quartile
# and test if rate varies with position
mid_positional = {}
for mid_name, positions in sorted(frequent_middles.items()):
    rho, p = safe_spearmanr(positions, [1.0] * len(positions))
    # Actually: test if norm_pos distribution of this MIDDLE differs from the overall
    # Simple: Spearman rho of norm_pos values of this MIDDLE's occurrences
    # If rho > 0, MIDDLE appears later; if rho < 0, appears earlier
    # Better: compare mean norm_pos of this MIDDLE to grand mean
    mean_pos = np.mean(positions)
    # One-sample test: is this MIDDLE's position distribution different from uniform?
    # Use KS test against uniform
    from scipy.stats import kstest
    ks_stat, ks_p = kstest(positions, 'uniform', args=(0, 1))
    mid_positional[mid_name] = {
        'n': len(positions),
        'mean_pos': round(mean_pos, 4),
        'ks_stat': round(ks_stat, 4),
        'ks_p': float(ks_p),
        'sig_bonferroni': ks_p < bonferroni_alpha,
    }
    if ks_p < bonferroni_alpha:
        sig_middles.append((mid_name, len(positions), mean_pos, ks_stat, ks_p))

print(f"  Bonferroni alpha: {bonferroni_alpha:.6f}")
print(f"  MIDDLEs with significant positional preference: {len(sig_middles)}/{n_tests}")
if sig_middles:
    sig_middles.sort(key=lambda x: x[4])
    print(f"\n  Top 10 positionally-biased MIDDLEs:")
    for mid_name, n, mean_pos, ks, p in sig_middles[:10]:
        bias = 'LATE' if mean_pos > 0.55 else ('EARLY' if mean_pos < 0.45 else 'NEUTRAL')
        print(f"    {mid_name:>12}: n={n:>4} mean_pos={mean_pos:.3f} [{bias}] KS={ks:.3f} p={p:.2e}")

# Early vs late MIDDLEs
early_middles = [m for m, n, mp, _, p in sig_middles if mp < 0.45]
late_middles = [m for m, n, mp, _, p in sig_middles if mp > 0.55]
print(f"\n  Early-biased MIDDLEs: {len(early_middles)}")
print(f"  Late-biased MIDDLEs: {len(late_middles)}")

test6_results = {
    'n_unique_middles': n_mid,
    'quartile_jsd': jsd_results,
    'jsd_q1_q4': jsd_q1q4,
    'mean_adjacent_jsd': round(adj_mean, 6),
    'progressive_drift': jsd_q1q4 > adj_mean,
    'frequent_middles_tested': n_tests,
    'sig_positional_middles': len(sig_middles),
    'bonferroni_alpha': round(bonferroni_alpha, 6),
    'early_biased_count': len(early_middles),
    'late_biased_count': len(late_middles),
    'top_sig_middles': [
        {'middle': m, 'n': n, 'mean_pos': round(mp, 4), 'ks_p': float(p)}
        for m, n, mp, ks, p in sig_middles[:20]
    ],
}


# ============================================================
# TEST 7: PREFIX COMBINATION TRAJECTORY
# ============================================================
print("\n" + "=" * 70)
print("TEST 7: PREFIX Combination Trajectory")
print("=" * 70)

from scipy.stats import chi2_contingency

# PREFIX distribution per quartile
prefix_cats = PREFIX_FAMILIES + ['other', 'None']
prefix_by_q = {q: Counter() for q in range(1, 5)}
prefix_positions = defaultdict(list)  # prefix_family -> [norm_pos, ...]

for rec in line_records:
    q = rec['quartile']
    for pf, count in rec['prefix_family_counts'].items():
        prefix_by_q[q][pf] += count
        for _ in range(count):
            prefix_positions[pf].append(rec['norm_pos'])

# Print distribution
print(f"\n  PREFIX distribution by quartile:")
print(f"    {'PREFIX':>8}", end='')
for q in range(1, 5):
    print(f"   Q{q}", end='')
print(f"   Total")

for pf in prefix_cats:
    print(f"    {pf:>8}", end='')
    total = sum(prefix_by_q[q][pf] for q in range(1, 5))
    for q in range(1, 5):
        q_total = sum(prefix_by_q[q].values())
        pct = 100 * prefix_by_q[q][pf] / q_total if q_total > 0 else 0
        print(f" {pct:>5.1f}%", end='')
    print(f"  {total:>5}")

# Chi-square across quartiles
contingency = np.zeros((len(prefix_cats), 4), dtype=int)
for i, pf in enumerate(prefix_cats):
    for q in range(1, 5):
        contingency[i, q - 1] = prefix_by_q[q][pf]

# Remove zero rows
nonzero = contingency.sum(axis=1) > 0
contingency_trim = contingency[nonzero]

try:
    chi2_pf, p_pf, dof_pf, _ = chi2_contingency(contingency_trim)
    print(f"\n  Chi-square (PREFIX x quartile): chi2={chi2_pf:.2f}, dof={dof_pf}, p={p_pf:.2e}")
    prefix_chi2 = {'chi2': round(chi2_pf, 2), 'dof': dof_pf, 'p': float(p_pf)}
except Exception as e:
    print(f"\n  Chi-square failed: {e}")
    prefix_chi2 = {'error': str(e)}

# Per-PREFIX Spearman rho vs norm_pos
print(f"\n  Per-PREFIX Spearman rho vs norm_pos:")
prefix_rho_results = {}
for pf in prefix_cats:
    positions = prefix_positions[pf]
    if len(positions) >= 10:
        rho, p = safe_spearmanr(list(range(len(positions))), positions)
        # Better: compute per-line fraction and correlate with norm_pos
        pass

# Per-line prefix fraction approach
for pf in prefix_cats:
    line_fracs = []
    line_pos = []
    for rec in line_records:
        n = rec['n_tokens']
        if n < 3:
            continue
        frac = rec['prefix_family_counts'].get(pf, 0) / n
        line_fracs.append(frac)
        line_pos.append(rec['norm_pos'])

    if len(line_fracs) >= 10:
        rho, p = safe_spearmanr(line_pos, line_fracs)
        sig = '*' if p < 0.05 else ''
        print(f"    {pf:>8}: rho={rho:+.4f} p={p:.2e} {sig}")
        prefix_rho_results[pf] = {'rho': round(rho, 4), 'p': float(p)}
    else:
        prefix_rho_results[pf] = {'rho': 0.0, 'p': 1.0, 'note': 'insufficient'}

test7_results = {
    'chi_square': prefix_chi2,
    'per_prefix_rho': prefix_rho_results,
    'quartile_distributions': {
        f'Q{q}': {pf: prefix_by_q[q][pf] for pf in prefix_cats}
        for q in range(1, 5)
    },
}


# ============================================================
# TEST 8: SUFFIX PROFILE TRAJECTORY
# ============================================================
print("\n" + "=" * 70)
print("TEST 8: Suffix Profile Trajectory")
print("=" * 70)

suffix_cats_list = ['aiin', 'ol', 'y', 'e_family', 'bare', 'other']
suffix_by_q = {q: Counter() for q in range(1, 5)}

for rec in line_records:
    q = rec['quartile']
    for sc, count in rec['suffix_cat_counts'].items():
        suffix_by_q[q][sc] += count

# Print distribution
print(f"\n  Suffix distribution by quartile:")
print(f"    {'Suffix':>10}", end='')
for q in range(1, 5):
    print(f"   Q{q}", end='')
print(f"   Total")

for sc in suffix_cats_list:
    print(f"    {sc:>10}", end='')
    total = sum(suffix_by_q[q][sc] for q in range(1, 5))
    for q in range(1, 5):
        q_total = sum(suffix_by_q[q].values())
        pct = 100 * suffix_by_q[q][sc] / q_total if q_total > 0 else 0
        print(f" {pct:>5.1f}%", end='')
    print(f"  {total:>5}")

# Chi-square
contingency_s = np.zeros((len(suffix_cats_list), 4), dtype=int)
for i, sc in enumerate(suffix_cats_list):
    for q in range(1, 5):
        contingency_s[i, q - 1] = suffix_by_q[q][sc]

nonzero_s = contingency_s.sum(axis=1) > 0
contingency_s_trim = contingency_s[nonzero_s]

try:
    chi2_s, p_s, dof_s, _ = chi2_contingency(contingency_s_trim)
    print(f"\n  Chi-square (suffix x quartile): chi2={chi2_s:.2f}, dof={dof_s}, p={p_s:.2e}")
    suffix_chi2 = {'chi2': round(chi2_s, 2), 'dof': dof_s, 'p': float(p_s)}
except Exception as e:
    print(f"\n  Chi-square failed: {e}")
    suffix_chi2 = {'error': str(e)}

# Per-suffix Spearman rho vs norm_pos (per-line fraction)
print(f"\n  Per-suffix Spearman rho vs norm_pos:")
suffix_rho_results = {}
for sc in suffix_cats_list:
    line_fracs = []
    line_pos = []
    for rec in line_records:
        n = rec['n_tokens']
        if n < 3:
            continue
        frac = rec['suffix_cat_counts'].get(sc, 0) / n
        line_fracs.append(frac)
        line_pos.append(rec['norm_pos'])

    if len(line_fracs) >= 10:
        rho, p = safe_spearmanr(line_pos, line_fracs)
        sig = '*' if p < 0.05 else ''
        print(f"    {sc:>10}: rho={rho:+.4f} p={p:.2e} {sig}")
        suffix_rho_results[sc] = {'rho': round(rho, 4), 'p': float(p)}
    else:
        suffix_rho_results[sc] = {'rho': 0.0, 'p': 1.0, 'note': 'insufficient'}

test8_results = {
    'chi_square': suffix_chi2,
    'per_suffix_rho': suffix_rho_results,
    'quartile_distributions': {
        f'Q{q}': {sc: suffix_by_q[q][sc] for sc in suffix_cats_list}
        for q in range(1, 5)
    },
}


# ============================================================
# TEST 9: ARTICULATOR RATE TRAJECTORY
# ============================================================
print("\n" + "=" * 70)
print("TEST 9: Articulator Rate Trajectory")
print("=" * 70)

# Overall articulator rate by quartile
art_by_q = {q: [] for q in range(1, 5)}
for rec in line_records:
    art_by_q[rec['quartile']].append(rec['art_rate'])

art_q_means = {q: float(np.mean(art_by_q[q])) if art_by_q[q] else 0 for q in range(1, 5)}
print(f"\n  Articulator rate by quartile:")
for q in range(1, 5):
    print(f"    Q{q}: {art_q_means[q]:.4f} (n={len(art_by_q[q])})")

# Spearman rho
art_pos = [rec['norm_pos'] for rec in line_records]
art_vals = [rec['art_rate'] for rec in line_records]
rho_art, p_art = safe_spearmanr(art_pos, art_vals)
kw_art_h, kw_art_p = safe_kruskal(*[art_by_q[q] for q in range(1, 5)])
sig = '*' if p_art < 0.05 else ''
print(f"\n  Spearman rho = {rho_art:.4f}, p = {p_art:.2e} {sig}")
print(f"  KW H = {kw_art_h:.2f}, p = {kw_art_p:.2e}")
print(f"  Slope (Q4-Q1): {art_q_means[4] - art_q_means[1]:+.4f}")

# Per-articulator type trajectory
# Count each articulator type per line
art_type_positions = defaultdict(list)  # art_type -> [(norm_pos, present_flag), ...]

for rec in line_records:
    words = rec['words']
    n = len(words)
    art_types_in_line = Counter()
    for w in words:
        m = morph_cache.get(w)
        if m and m.articulator:
            art_types_in_line[m.articulator] += 1
    for at, count in art_types_in_line.items():
        art_type_positions[at].append((rec['norm_pos'], count / n))

print(f"\n  Per-articulator type trajectory:")
art_type_rho = {}
for at in sorted(art_type_positions.keys()):
    positions_at = art_type_positions[at]
    if len(positions_at) >= 20:
        xp = [p[0] for p in positions_at]
        yp = [p[1] for p in positions_at]
        rho, p = safe_spearmanr(xp, yp)
        sig = '*' if p < 0.05 else ''
        print(f"    '{at}': n={len(positions_at)}, rho={rho:+.4f}, p={p:.2e} {sig}")
        art_type_rho[at] = {'n': len(positions_at), 'rho': round(rho, 4), 'p': float(p)}

# Regime stratification
print(f"\n  Regime stratification (overall art rate):")
regime_art = {}
for regime in regimes:
    r_recs = [rec for rec in line_records if rec['regime'] == regime]
    r_pos = [rec['norm_pos'] for rec in r_recs]
    r_vals = [rec['art_rate'] for rec in r_recs]
    rho, p = safe_spearmanr(r_pos, r_vals)
    rq = {q: [] for q in range(1, 5)}
    for rec in r_recs:
        rq[rec['quartile']].append(rec['art_rate'])
    rq_means = {q: float(np.mean(rq[q])) if rq[q] else 0 for q in range(1, 5)}
    slope = rq_means[4] - rq_means[1]
    regime_art[regime] = {
        'rho': round(rho, 4), 'p': float(p),
        'slope': round(slope, 4), 'n': len(r_recs),
    }
    print(f"    {regime} (n={len(r_recs)}): rho={rho:+.4f} slope={slope:+.4f}")

test9_results = {
    'overall': {
        'spearman': {'rho': round(rho_art, 4), 'p': float(p_art)},
        'kruskal_wallis': {'H': round(kw_art_h, 2), 'p': float(kw_art_p)},
        'quartile_means': {f'Q{q}': round(art_q_means[q], 4) for q in range(1, 5)},
        'slope': round(art_q_means[4] - art_q_means[1], 4),
    },
    'per_articulator_type': art_type_rho,
    'regime_stratified': regime_art,
}


# ============================================================
# TEST 10: LINE COMPLEXITY TRAJECTORY
# ============================================================
print("\n" + "=" * 70)
print("TEST 10: Line Complexity Trajectory")
print("=" * 70)

complexity_metrics = {
    'unique_tokens': [],
    'unique_middles': [],
    'unique_classes': [],
    'ttr': [],
    'mean_token_len': [],
}

complexity_by_q = {metric: {q: [] for q in range(1, 5)} for metric in complexity_metrics}

for rec in line_records:
    q = rec['quartile']
    for metric in complexity_metrics:
        val = rec[metric]
        complexity_metrics[metric].append((rec['norm_pos'], val))
        complexity_by_q[metric][q].append(val)

test10_results = {}
print(f"\n  Complexity metrics:")
for metric in complexity_metrics:
    positions = [p[0] for p in complexity_metrics[metric]]
    values = [p[1] for p in complexity_metrics[metric]]
    rho, p = safe_spearmanr(positions, values)
    kw_h, kw_p = safe_kruskal(*[complexity_by_q[metric][q] for q in range(1, 5)])
    q_means = {q: float(np.mean(complexity_by_q[metric][q])) if complexity_by_q[metric][q] else 0
               for q in range(1, 5)}
    sig = '*' if p < 0.05 else ''
    print(f"    {metric:>16}: rho={rho:+.4f} p={p:.2e} {sig}  Q1={q_means[1]:.3f} Q4={q_means[4]:.3f}")

    test10_results[metric] = {
        'spearman': {'rho': round(rho, 4), 'p': float(p)},
        'kruskal_wallis': {'H': round(kw_h, 2), 'p': float(kw_p)},
        'quartile_means': {f'Q{q}': round(q_means[q], 4) for q in range(1, 5)},
    }

# Regime stratification for TTR
print(f"\n  TTR regime stratification:")
for regime in regimes:
    r_recs = [rec for rec in line_records if rec['regime'] == regime]
    r_pos = [rec['norm_pos'] for rec in r_recs]
    r_vals = [rec['ttr'] for rec in r_recs]
    rho, p = safe_spearmanr(r_pos, r_vals)
    rq = {q: [] for q in range(1, 5)}
    for rec in r_recs:
        rq[rec['quartile']].append(rec['ttr'])
    rq_means = {q: float(np.mean(rq[q])) if rq[q] else 0 for q in range(1, 5)}
    print(f"    {regime} (n={len(r_recs)}): rho={rho:+.4f} Q1={rq_means[1]:.3f} Q4={rq_means[4]:.3f}")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"\n  T6 MIDDLE Vocabulary:")
print(f"    JSD(Q1,Q4) = {test6_results['jsd_q1_q4']:.6f}")
print(f"    Progressive drift: {test6_results['progressive_drift']}")
print(f"    Sig positional MIDDLEs: {test6_results['sig_positional_middles']}/{test6_results['frequent_middles_tested']}")

print(f"\n  T7 PREFIX Trajectory:")
if 'chi2' in test7_results['chi_square']:
    print(f"    Chi2 p = {test7_results['chi_square']['p']:.2e}")
sig_pf = sum(1 for v in test7_results['per_prefix_rho'].values()
             if isinstance(v, dict) and v.get('p', 1) < 0.05)
print(f"    Sig PREFIX families: {sig_pf}/{len(prefix_cats)}")

print(f"\n  T8 Suffix Trajectory:")
if 'chi2' in test8_results['chi_square']:
    print(f"    Chi2 p = {test8_results['chi_square']['p']:.2e}")
sig_sf = sum(1 for v in test8_results['per_suffix_rho'].values()
             if isinstance(v, dict) and v.get('p', 1) < 0.05)
print(f"    Sig suffix categories: {sig_sf}/{len(suffix_cats_list)}")

print(f"\n  T9 Articulator Rate:")
print(f"    Overall rho = {test9_results['overall']['spearman']['rho']:+.4f}, p = {test9_results['overall']['spearman']['p']:.2e}")

print(f"\n  T10 Complexity:")
sig_cx = sum(1 for v in test10_results.values()
             if v['spearman']['p'] < 0.05)
print(f"    Sig complexity metrics: {sig_cx}/{len(complexity_metrics)}")


# ============================================================
# SAVE
# ============================================================
results = {
    'metadata': {
        'phase': 'B_LINE_SEQUENTIAL_STRUCTURE',
        'script': 'line_token_trajectory',
        'timestamp': datetime.now().isoformat(),
        'total_lines': n_lines_total,
        'valid_folios': len(valid_folios),
    },
    'test6_middle_trajectory': test6_results,
    'test7_prefix_trajectory': test7_results,
    'test8_suffix_trajectory': test8_results,
    'test9_articulator_trajectory': test9_results,
    'test10_complexity_trajectory': test10_results,
}

output_path = RESULTS_DIR / 'line_token_trajectory.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to: {output_path}")
print("\nDone.")
