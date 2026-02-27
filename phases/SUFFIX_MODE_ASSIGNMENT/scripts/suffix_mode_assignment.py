"""
Phase 469: SUFFIX_MODE_ASSIGNMENT

Tests whether suffix mode assignment (Mode A vs Mode B) is determined by
token identity (MIDDLE determines suffix) or line-level context (mode is
imposed on tokens). Discriminates between Identity and Context models.

Tests:
  S1: MIDDLE suffix selectivity (MI comparison)
  S2: MIDDLE mode preference distribution
  S3: Same-MIDDLE suffix shift across modes
  S4: Mode as emergent vs imposed property

References: C1229, C1231, C1256, C1258, C1279, C1309
"""

import json
import sys
import math
import time
import random
import functools
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

# Phase 462 (pure Python stats)
sys.path.insert(0, str(ROOT / 'phases' / 'TEXT_BLOCK_PARALLEL_OPERATORS' / 'scripts'))
from text_block_parallel_operators import (
    jsd, normalize_profile, normal_cdf
)

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "SUFFIX_MODE_ASSIGNMENT" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 1000
SEED = 42

# ================================================================
# SUFFIX MODE CONSTANTS (from C1231)
# ================================================================
TERMINAL_SUFFIXES = {'edy', 'dy', 'eey', 'ey', 'y', 'hy', 'iry', 'oly',
                     'ry', 'ky', 'ty', 'py', 'fy', 'my', 'ly', 'sy'}
CONNECTOR_SUFFIXES = {'o', 'or', 'os', 'oe'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'aiiin', 'al', 'am', 'an'}

MODE_A_CENTROID = [0.430, 0.019, 0.086, 0.466]
MODE_B_CENTROID = [0.155, 0.031, 0.072, 0.741]

SUFFIX_CATS = ['terminal', 'connector', 'iterate', 'bare']


# ================================================================
# PURE PYTHON HELPERS
# ================================================================
def euclidean_dist(a, b):
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def suffix_category(suffix):
    """Classify a suffix string into one of 4 categories."""
    if not suffix:
        return 'bare'
    if suffix in TERMINAL_SUFFIXES:
        return 'terminal'
    if suffix in CONNECTOR_SUFFIXES:
        return 'connector'
    if suffix in ITERATE_SUFFIXES:
        return 'iterate'
    return 'bare'


def classify_suffix_mode(line_toks):
    """Classify a line's suffix mode (A or B) using C1231 centroids.

    Args:
        line_toks: list of dicts with 'suffix_cat' key

    Returns:
        'A', 'B', or None (< 3 tokens)
    """
    if len(line_toks) < 3:
        return None
    counts = Counter(t['suffix_cat'] for t in line_toks)
    n = len(line_toks)
    vec = [counts.get(c, 0) / n for c in SUFFIX_CATS]
    d_a = euclidean_dist(vec, MODE_A_CENTROID)
    d_b = euclidean_dist(vec, MODE_B_CENTROID)
    return 'A' if d_a < d_b else 'B'


def entropy_from_counts(counts):
    """Shannon entropy (bits) from a Counter."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def mutual_information(x_vals, y_vals):
    """Mutual information I(X;Y) in bits from paired value lists."""
    n = len(x_vals)
    if n == 0:
        return 0.0

    # Joint counts
    joint = Counter(zip(x_vals, y_vals))
    x_counts = Counter(x_vals)
    y_counts = Counter(y_vals)

    mi = 0.0
    for (x, y), count in joint.items():
        p_xy = count / n
        p_x = x_counts[x] / n
        p_y = y_counts[y] / n
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi


def chi2_independence(contingency):
    """Chi-squared test of independence from a contingency dict.

    Args:
        contingency: dict of {row: Counter({col: count})}

    Returns:
        (chi2, p, n)
    """
    rows = sorted(contingency.keys())
    cols = set()
    for row_counts in contingency.values():
        cols.update(row_counts.keys())
    cols = sorted(cols)

    n = sum(sum(contingency[r].get(c, 0) for c in cols) for r in rows)
    if n == 0:
        return 0.0, 1.0, 0

    row_totals = {r: sum(contingency[r].get(c, 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency[r].get(c, 0) for r in rows) for c in cols}

    chi2 = 0.0
    for r in rows:
        for c in cols:
            observed = contingency[r].get(c, 0)
            expected = row_totals[r] * col_totals[c] / n if n > 0 else 0
            if expected > 0:
                chi2 += (observed - expected) ** 2 / expected

    df = (len(rows) - 1) * (len(cols) - 1)
    if df <= 0:
        return chi2, 1.0, n

    # Wilson-Hilferty approximation for chi2 p-value
    if chi2 <= 0:
        return 0.0, 1.0, n
    z = ((chi2 / df) ** (1.0 / 3.0) - (1 - 2.0 / (9.0 * df))) / math.sqrt(2.0 / (9.0 * df))
    p = 1.0 - normal_cdf(z)
    return chi2, p, n


# ================================================================
# DATA LOADING
# ================================================================
def build_b_lines():
    """Load B tokens, group into paragraph body lines, classify suffix modes.

    Returns:
        lines: list of dicts, each representing a body line with:
            folio, section, para_id, line_num, tokens (list of token dicts),
            mode ('A', 'B', or None)
        all_tokens: flat list of all tokens in classified body lines
    """
    t0 = time.time()
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Collect all B tokens with morphology
    raw_tokens = []
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        suf = m.suffix if m.suffix else ''
        raw_tokens.append({
            'word': w,
            'folio': token.folio,
            'section': token.section,
            'line': token.line,
            'middle': m.middle,
            'prefix': m.prefix,
            'suffix': suf,
            'suffix_cat': suffix_category(suf),
            'category': cc.classify(m.middle) if m.middle else None,
            'par_initial': token.par_initial,
            'par_final': token.par_final,
        })

    print(f"  B tokens loaded: {len(raw_tokens)}")

    # Group into paragraphs, then lines
    paragraphs = []
    current_para = None
    para_id = 0

    for tok in raw_tokens:
        if tok['par_initial']:
            if current_para is not None:
                paragraphs.append(current_para)
            para_id += 1
            current_para = {
                'id': para_id,
                'folio': tok['folio'],
                'section': tok['section'],
                'lines': defaultdict(list),
            }
        if current_para is not None:
            current_para['lines'][tok['line']].append(tok)
        if tok['par_final'] and current_para is not None:
            paragraphs.append(current_para)
            current_para = None

    if current_para is not None:
        paragraphs.append(current_para)

    print(f"  Paragraphs: {len(paragraphs)}")

    # Extract body lines (skip header = first line of each paragraph)
    lines = []
    for para in paragraphs:
        sorted_line_nums = sorted(para['lines'].keys())
        if len(sorted_line_nums) < 2:
            continue  # Skip single-line paragraphs (no body)

        header_line = sorted_line_nums[0]
        for i, line_num in enumerate(sorted_line_nums):
            if line_num == header_line:
                continue  # Skip header
            line_toks = para['lines'][line_num]
            mode = classify_suffix_mode(line_toks)
            lines.append({
                'folio': para['folio'],
                'section': para['section'],
                'para_id': para['id'],
                'line_num': line_num,
                'tokens': line_toks,
                'mode': mode,
                'n_tokens': len(line_toks),
            })

    # Classify and collect tokens from classified lines
    classified_lines = [l for l in lines if l['mode'] is not None]
    all_tokens = []
    for line in classified_lines:
        for tok in line['tokens']:
            tok['line_mode'] = line['mode']
            all_tokens.append(tok)

    n_a = sum(1 for l in classified_lines if l['mode'] == 'A')
    n_b = sum(1 for l in classified_lines if l['mode'] == 'B')

    dt = time.time() - t0
    print(f"  Body lines: {len(lines)} ({len(classified_lines)} classified)")
    print(f"  Mode A lines: {n_a} ({n_a/len(classified_lines)*100:.1f}%)")
    print(f"  Mode B lines: {n_b} ({n_b/len(classified_lines)*100:.1f}%)")
    print(f"  Tokens in classified lines: {len(all_tokens)}")
    print(f"  Data built in {dt:.1f}s")

    return classified_lines, all_tokens


# ================================================================
# TEST S1: MIDDLE Suffix Selectivity
# ================================================================
def test_s1(all_tokens):
    """How much does MIDDLE identity determine suffix selection?"""
    print("\n=== S1: MIDDLE Suffix Selectivity ===")

    # Filter to tokens with MIDDLEs
    tokens = [t for t in all_tokens if t['middle']]

    # MIDDLE frequency
    mid_freq = Counter(t['middle'] for t in tokens)
    frequent = {m for m, c in mid_freq.items() if c >= 20}
    freq_tokens = [t for t in tokens if t['middle'] in frequent]

    print(f"  Tokens with MIDDLEs: {len(tokens)}")
    print(f"  Frequent MIDDLEs (20+): {len(frequent)}")
    print(f"  Tokens from frequent MIDDLEs: {len(freq_tokens)}")

    # Mutual information: I(suffix_cat; MIDDLE) vs I(suffix_cat; line_mode)
    middles = [t['middle'] for t in freq_tokens]
    suffix_cats = [t['suffix_cat'] for t in freq_tokens]
    line_modes = [t['line_mode'] for t in freq_tokens]

    mi_middle_suffix = mutual_information(middles, suffix_cats)
    mi_mode_suffix = mutual_information(line_modes, suffix_cats)

    print(f"  I(MIDDLE; suffix_cat) = {mi_middle_suffix:.4f} bits")
    print(f"  I(line_mode; suffix_cat) = {mi_mode_suffix:.4f} bits")
    print(f"  Ratio: {mi_middle_suffix / mi_mode_suffix:.2f}x"
          if mi_mode_suffix > 0 else "  Ratio: inf")

    # Per-MIDDLE selectivity: max suffix category fraction
    selectivities = {}
    mid_suffix_profiles = {}
    for mid in sorted(frequent):
        mid_toks = [t for t in freq_tokens if t['middle'] == mid]
        sc = Counter(t['suffix_cat'] for t in mid_toks)
        total = sum(sc.values())
        profile = {c: sc.get(c, 0) / total for c in SUFFIX_CATS}
        max_frac = max(profile.values())
        selectivities[mid] = max_frac
        mid_suffix_profiles[mid] = profile

    sel_values = sorted(selectivities.values())
    mean_sel = sum(sel_values) / len(sel_values)
    median_sel = sel_values[len(sel_values) // 2]

    # Distribution: count by selectivity bands
    band_counts = {'bare_locked': 0, 'terminal_locked': 0,
                   'high_sel': 0, 'moderate': 0, 'low': 0}
    for mid, sel in selectivities.items():
        prof = mid_suffix_profiles[mid]
        if sel >= 0.80:
            if prof['bare'] == sel:
                band_counts['bare_locked'] += 1
            elif prof['terminal'] == sel:
                band_counts['terminal_locked'] += 1
            else:
                band_counts['high_sel'] += 1
        elif sel >= 0.60:
            band_counts['moderate'] += 1
        else:
            band_counts['low'] += 1

    print(f"  Mean selectivity: {mean_sel:.4f}")
    print(f"  Median selectivity: {median_sel:.4f}")
    print(f"  Distribution:")
    for band, count in band_counts.items():
        print(f"    {band}: {count} ({count/len(frequent)*100:.1f}%)")

    # Top 10 most selective MIDDLEs
    top_selective = sorted(selectivities.items(), key=lambda x: -x[1])[:10]
    print(f"  Top 10 most selective MIDDLEs:")
    for mid, sel in top_selective:
        prof = mid_suffix_profiles[mid]
        dom = max(prof, key=prof.get)
        print(f"    {mid}: {sel:.3f} ({dom}, n={mid_freq[mid]})")

    verdict = 'PASS' if mi_middle_suffix > mi_mode_suffix else 'FAIL'
    print(f"  Verdict: {verdict} "
          f"(MIDDLE→suffix {mi_middle_suffix:.4f} "
          f"{'>' if mi_middle_suffix > mi_mode_suffix else '<='} "
          f"mode→suffix {mi_mode_suffix:.4f})")

    return {
        'verdict': verdict,
        'n_frequent_middles': len(frequent),
        'n_tokens': len(freq_tokens),
        'mi_middle_suffix': round(mi_middle_suffix, 4),
        'mi_mode_suffix': round(mi_mode_suffix, 4),
        'mi_ratio': round(mi_middle_suffix / mi_mode_suffix, 3)
            if mi_mode_suffix > 0 else None,
        'mean_selectivity': round(mean_sel, 4),
        'median_selectivity': round(median_sel, 4),
        'selectivity_bands': band_counts,
        'top10_selective': [
            {'middle': m, 'selectivity': round(s, 3),
             'dominant_suffix': max(mid_suffix_profiles[m],
                                    key=mid_suffix_profiles[m].get),
             'freq': mid_freq[m]}
            for m, s in top_selective
        ],
    }


# ================================================================
# TEST S2: MIDDLE Mode Preference Distribution
# ================================================================
def test_s2(all_tokens, cc):
    """Are MIDDLEs mode-locked or mode-flexible?"""
    print("\n=== S2: MIDDLE Mode Preference Distribution ===")

    tokens = [t for t in all_tokens if t['middle']]
    mid_freq = Counter(t['middle'] for t in tokens)
    frequent = {m for m, c in mid_freq.items() if c >= 10}
    freq_tokens = [t for t in tokens if t['middle'] in frequent]

    print(f"  Frequent MIDDLEs (10+): {len(frequent)}")

    # Mode preference per MIDDLE
    mid_mode_counts = defaultdict(Counter)
    for t in freq_tokens:
        mid_mode_counts[t['middle']][t['line_mode']] += 1

    preferences = {}
    for mid in sorted(frequent):
        mc = mid_mode_counts[mid]
        total = mc['A'] + mc['B']
        if total == 0:
            continue
        preferences[mid] = mc['A'] / total

    pref_values = sorted(preferences.values())

    # Distribution bands
    locked_a = [m for m, p in preferences.items() if p >= 0.80]
    locked_b = [m for m, p in preferences.items() if p <= 0.20]
    leaning_a = [m for m, p in preferences.items() if 0.60 <= p < 0.80]
    leaning_b = [m for m, p in preferences.items() if 0.20 < p <= 0.40]
    flexible = [m for m, p in preferences.items() if 0.40 < p < 0.60]

    total_mids = len(preferences)
    mode_locked_frac = (len(locked_a) + len(locked_b)) / total_mids if total_mids else 0

    print(f"  Mode-locked A (>80%): {len(locked_a)} ({len(locked_a)/total_mids*100:.1f}%)")
    print(f"  Mode-locked B (<20%): {len(locked_b)} ({len(locked_b)/total_mids*100:.1f}%)")
    print(f"  Leaning A (60-80%): {len(leaning_a)} ({len(leaning_a)/total_mids*100:.1f}%)")
    print(f"  Leaning B (20-40%): {len(leaning_b)} ({len(leaning_b)/total_mids*100:.1f}%)")
    print(f"  Flexible (40-60%): {len(flexible)} ({len(flexible)/total_mids*100:.1f}%)")
    print(f"  Total mode-locked: {len(locked_a)+len(locked_b)}/{total_mids} "
          f"({mode_locked_frac*100:.1f}%)")

    # Category × mode preference
    cat_prefs = defaultdict(list)
    for mid, pref in preferences.items():
        cat = cc.classify(mid)
        if cat:
            cat_prefs[cat].append(pref)

    cat_results = {}
    print(f"  Category mean mode_A_fraction:")
    for cat in sorted(cat_prefs.keys()):
        vals = cat_prefs[cat]
        mean_p = sum(vals) / len(vals)
        cat_results[cat] = {
            'mean_mode_a_frac': round(mean_p, 4),
            'n_middles': len(vals),
        }
        direction = "Mode A" if mean_p > 0.5 else "Mode B"
        print(f"    {cat}: {mean_p:.4f} (n={len(vals)}) -> {direction}")

    # Section stratification
    section_tokens = defaultdict(list)
    for t in freq_tokens:
        section_tokens[t['section']].append(t)

    section_results = {}
    for sec in sorted(section_tokens.keys()):
        sec_toks = section_tokens[sec]
        sec_mid_mode = defaultdict(Counter)
        for t in sec_toks:
            sec_mid_mode[t['middle']][t['line_mode']] += 1
        sec_prefs = {}
        for mid, mc in sec_mid_mode.items():
            total = mc['A'] + mc['B']
            if total >= 5:
                sec_prefs[mid] = mc['A'] / total
        if sec_prefs:
            sec_locked = sum(1 for p in sec_prefs.values()
                             if p >= 0.80 or p <= 0.20)
            section_results[sec] = {
                'n_middles': len(sec_prefs),
                'locked_frac': round(sec_locked / len(sec_prefs), 4),
                'mean_pref': round(sum(sec_prefs.values()) / len(sec_prefs), 4),
            }

    verdict = 'PASS' if mode_locked_frac > 0.30 else 'FAIL'
    print(f"  Verdict: {verdict} (mode-locked {mode_locked_frac*100:.1f}% "
          f"{'>' if mode_locked_frac > 0.30 else '<='} 30%)")

    return {
        'verdict': verdict,
        'n_middles': total_mids,
        'locked_a': len(locked_a),
        'locked_b': len(locked_b),
        'leaning_a': len(leaning_a),
        'leaning_b': len(leaning_b),
        'flexible': len(flexible),
        'mode_locked_fraction': round(mode_locked_frac, 4),
        'category_mode_preference': cat_results,
        'section_breakdown': section_results,
        'top_locked_a': [
            {'middle': m, 'mode_a_frac': round(preferences[m], 3),
             'freq': mid_freq[m]}
            for m in sorted(locked_a, key=lambda m: -preferences[m])[:5]
        ],
        'top_locked_b': [
            {'middle': m, 'mode_a_frac': round(preferences[m], 3),
             'freq': mid_freq[m]}
            for m in sorted(locked_b, key=lambda m: preferences[m])[:5]
        ],
    }


# ================================================================
# TEST S3: Same-MIDDLE Suffix Shift Across Modes
# ================================================================
def test_s3(all_tokens, rng):
    """Does the SAME MIDDLE carry different suffixes in different modes?"""
    print("\n=== S3: Same-MIDDLE Suffix Shift Across Modes ===")

    tokens = [t for t in all_tokens if t['middle']]

    # Find MIDDLEs with 5+ tokens in BOTH modes
    mid_mode_counts = defaultdict(lambda: Counter())
    for t in tokens:
        mid_mode_counts[t['middle']][t['line_mode']] += 1

    dual_mode = {m for m, mc in mid_mode_counts.items()
                 if mc['A'] >= 5 and mc['B'] >= 5}

    print(f"  MIDDLEs with 5+ in both modes: {len(dual_mode)}")

    if len(dual_mode) < 10:
        return {'verdict': 'SKIP', 'reason': 'too few dual-mode MIDDLEs'}

    # For each dual-mode MIDDLE: compare suffix distributions across modes
    mid_jsds = {}
    mid_chi2_p = {}
    for mid in sorted(dual_mode):
        mode_a_toks = [t for t in tokens if t['middle'] == mid and t['line_mode'] == 'A']
        mode_b_toks = [t for t in tokens if t['middle'] == mid and t['line_mode'] == 'B']

        a_counts = Counter(t['suffix_cat'] for t in mode_a_toks)
        b_counts = Counter(t['suffix_cat'] for t in mode_b_toks)

        a_vec = normalize_profile(a_counts, SUFFIX_CATS)
        b_vec = normalize_profile(b_counts, SUFFIX_CATS)

        mid_jsds[mid] = jsd(a_vec, b_vec)

        # Chi-squared
        contingency = {
            'A': Counter({c: a_counts.get(c, 0) for c in SUFFIX_CATS}),
            'B': Counter({c: b_counts.get(c, 0) for c in SUFFIX_CATS}),
        }
        chi2, p, n = chi2_independence(contingency)
        mid_chi2_p[mid] = p

    jsd_values = sorted(mid_jsds.values())
    mean_jsd = sum(jsd_values) / len(jsd_values)
    median_jsd = jsd_values[len(jsd_values) // 2]

    sig_shift = sum(1 for p in mid_chi2_p.values() if p < 0.01)
    sig_frac = sig_shift / len(dual_mode)

    print(f"  Mean cross-mode JSD: {mean_jsd:.4f}")
    print(f"  Median cross-mode JSD: {median_jsd:.4f}")
    print(f"  MIDDLEs with significant shift (p<0.01): {sig_shift}/{len(dual_mode)} "
          f"({sig_frac*100:.1f}%)")

    # Permutation null: shuffle mode labels across lines within paragraph
    # Build paragraph -> line mapping
    para_lines = defaultdict(list)
    for t in tokens:
        key = (t['folio'], t.get('line_mode', None))
        # We need to track which tokens are on which lines
        # Simpler: just shuffle the line_mode labels across tokens within each line group
    # Actually, for permutation: shuffle mode labels across lines within paragraphs
    # We need to collect line-level data
    line_data = defaultdict(list)  # (folio, line) -> list of tokens
    for t in tokens:
        if t['middle'] in dual_mode:
            line_data[(t['folio'], t.get('line', ''))].append(t)

    # Group lines by paragraph
    para_line_groups = defaultdict(list)
    for t in tokens:
        para_line_groups[(t['folio'], t.get('line', ''))].append(t)

    # Collect unique lines with their modes
    line_modes = {}
    for (f, ln), toks in para_line_groups.items():
        if toks and 'line_mode' in toks[0]:
            line_modes[(f, ln)] = toks[0]['line_mode']

    null_mean_jsds = []
    for _ in range(N_PERM):
        # Shuffle mode labels across all lines (simple global shuffle)
        keys = list(line_modes.keys())
        modes = [line_modes[k] for k in keys]
        rng.shuffle(modes)
        shuffled_modes = dict(zip(keys, modes))

        # Recompute per-MIDDLE JSD with shuffled modes
        mid_a_counts = defaultdict(Counter)
        mid_b_counts = defaultdict(Counter)
        for t in tokens:
            if t['middle'] not in dual_mode:
                continue
            key = (t['folio'], t.get('line', ''))
            sm = shuffled_modes.get(key, t.get('line_mode'))
            if sm == 'A':
                mid_a_counts[t['middle']][t['suffix_cat']] += 1
            else:
                mid_b_counts[t['middle']][t['suffix_cat']] += 1

        perm_jsds = []
        for mid in dual_mode:
            ac = mid_a_counts[mid]
            bc = mid_b_counts[mid]
            if sum(ac.values()) < 3 or sum(bc.values()) < 3:
                continue
            av = normalize_profile(ac, SUFFIX_CATS)
            bv = normalize_profile(bc, SUFFIX_CATS)
            perm_jsds.append(jsd(av, bv))

        if perm_jsds:
            null_mean_jsds.append(sum(perm_jsds) / len(perm_jsds))

    null_mean = sum(null_mean_jsds) / len(null_mean_jsds) if null_mean_jsds else 0.0
    perm_p = sum(1 for nm in null_mean_jsds if nm >= mean_jsd) / len(null_mean_jsds) \
        if null_mean_jsds else 1.0

    print(f"  Null mean JSD: {null_mean:.4f}")
    print(f"  Permutation p: {perm_p:.4f}")

    # Top shifters and non-shifters
    top_shifters = sorted(mid_jsds.items(), key=lambda x: -x[1])[:5]
    top_stable = sorted(mid_jsds.items(), key=lambda x: x[1])[:5]

    print(f"  Top 5 shifters (highest JSD):")
    for mid, j in top_shifters:
        print(f"    {mid}: JSD={j:.4f} (n_A={mid_mode_counts[mid]['A']}, "
              f"n_B={mid_mode_counts[mid]['B']})")
    print(f"  Top 5 stable (lowest JSD):")
    for mid, j in top_stable:
        print(f"    {mid}: JSD={j:.4f} (n_A={mid_mode_counts[mid]['A']}, "
              f"n_B={mid_mode_counts[mid]['B']})")

    # Verdict
    if mean_jsd > 0.10 and sig_frac > 0.40:
        verdict = 'PASS_CONTEXT'
    elif mean_jsd < 0.03 and sig_frac < 0.15:
        verdict = 'PASS_IDENTITY'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_dual_mode_middles': len(dual_mode),
        'mean_jsd': round(mean_jsd, 4),
        'median_jsd': round(median_jsd, 4),
        'significant_shift_count': sig_shift,
        'significant_shift_fraction': round(sig_frac, 4),
        'null_mean_jsd': round(null_mean, 4),
        'perm_p': round(perm_p, 4),
        'top_shifters': [
            {'middle': m, 'jsd': round(j, 4),
             'n_A': mid_mode_counts[m]['A'], 'n_B': mid_mode_counts[m]['B']}
            for m, j in top_shifters
        ],
        'top_stable': [
            {'middle': m, 'jsd': round(j, 4),
             'n_A': mid_mode_counts[m]['A'], 'n_B': mid_mode_counts[m]['B']}
            for m, j in top_stable
        ],
    }


# ================================================================
# TEST S4: Mode as Emergent vs Imposed Property
# ================================================================
def test_s4(classified_lines, all_tokens):
    """Can line mode be predicted purely from which MIDDLEs are on the line?"""
    print("\n=== S4: Mode as Emergent vs Imposed Property ===")

    tokens = [t for t in all_tokens if t['middle']]

    # Compute per-MIDDLE modal suffix (most common suffix category)
    mid_suffix_counts = defaultdict(Counter)
    for t in tokens:
        mid_suffix_counts[t['middle']][t['suffix_cat']] += 1

    mid_modal_suffix = {}
    for mid, counts in mid_suffix_counts.items():
        mid_modal_suffix[mid] = counts.most_common(1)[0][0]

    print(f"  MIDDLEs with modal suffix: {len(mid_modal_suffix)}")

    # For each line: predict mode from token identities
    predictions = []
    for line in classified_lines:
        toks = [t for t in line['tokens'] if t.get('middle') and
                t['middle'] in mid_modal_suffix]
        if len(toks) < 3:
            continue

        # Build predicted suffix profile from modal suffixes
        predicted_cats = Counter()
        for t in toks:
            predicted_cats[mid_modal_suffix[t['middle']]] += 1

        n = len(toks)
        pred_vec = [predicted_cats.get(c, 0) / n for c in SUFFIX_CATS]
        d_a = euclidean_dist(pred_vec, MODE_A_CENTROID)
        d_b = euclidean_dist(pred_vec, MODE_B_CENTROID)
        pred_mode = 'A' if d_a < d_b else 'B'

        predictions.append({
            'actual': line['mode'],
            'predicted': pred_mode,
        })

    if not predictions:
        return {'verdict': 'SKIP', 'reason': 'no predictable lines'}

    # Accuracy
    correct = sum(1 for p in predictions if p['actual'] == p['predicted'])
    accuracy = correct / len(predictions)

    # Per-mode metrics
    tp_a = sum(1 for p in predictions if p['actual'] == 'A' and p['predicted'] == 'A')
    fp_a = sum(1 for p in predictions if p['actual'] == 'B' and p['predicted'] == 'A')
    fn_a = sum(1 for p in predictions if p['actual'] == 'A' and p['predicted'] == 'B')
    tp_b = sum(1 for p in predictions if p['actual'] == 'B' and p['predicted'] == 'B')

    precision_a = tp_a / (tp_a + fp_a) if (tp_a + fp_a) > 0 else 0
    recall_a = tp_a / (tp_a + fn_a) if (tp_a + fn_a) > 0 else 0
    precision_b = tp_b / (tp_b + fn_a) if (tp_b + fn_a) > 0 else 0
    recall_b = tp_b / (tp_b + fp_a) if (tp_b + fp_a) > 0 else 0

    # Baseline: majority class prediction
    actual_counts = Counter(p['actual'] for p in predictions)
    majority = actual_counts.most_common(1)[0]
    baseline_accuracy = majority[1] / len(predictions)

    print(f"  Predictable lines: {len(predictions)}")
    print(f"  Accuracy: {accuracy:.4f} ({correct}/{len(predictions)})")
    print(f"  Baseline (majority {majority[0]}): {baseline_accuracy:.4f}")
    print(f"  Lift over baseline: {accuracy / baseline_accuracy:.3f}x")
    print(f"  Mode A: precision={precision_a:.3f}, recall={recall_a:.3f}")
    print(f"  Mode B: precision={precision_b:.3f}, recall={recall_b:.3f}")

    # Confusion matrix
    print(f"  Confusion matrix:")
    print(f"              Pred A  Pred B")
    print(f"    Actual A:  {tp_a:5d}  {fn_a:5d}")
    print(f"    Actual B:  {fp_a:5d}  {tp_b:5d}")

    if accuracy > 0.80:
        verdict = 'PASS_IDENTITY'
    elif accuracy < 0.60:
        verdict = 'PASS_CONTEXT'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict} (accuracy {accuracy:.4f})")

    return {
        'verdict': verdict,
        'n_lines': len(predictions),
        'accuracy': round(accuracy, 4),
        'baseline_accuracy': round(baseline_accuracy, 4),
        'lift': round(accuracy / baseline_accuracy, 3),
        'mode_a_precision': round(precision_a, 4),
        'mode_a_recall': round(recall_a, 4),
        'mode_b_precision': round(precision_b, 4),
        'mode_b_recall': round(recall_b, 4),
        'confusion': {
            'tp_a': tp_a, 'fn_a': fn_a,
            'fp_a': fp_a, 'tp_b': tp_b,
        },
    }


# ================================================================
# MAIN
# ================================================================
def main():
    rng = random.Random(SEED)
    t0 = time.time()

    print("Phase 469: SUFFIX_MODE_ASSIGNMENT")
    print("=" * 60)

    # Load data
    print("\nBuilding B body lines...")
    classified_lines, all_tokens = build_b_lines()

    cc = CategoryClassifier()

    # Run tests
    results = {}
    results['S1'] = test_s1(all_tokens)
    results['S2'] = test_s2(all_tokens, cc)
    results['S3'] = test_s3(all_tokens, rng)
    results['S4'] = test_s4(classified_lines, all_tokens)

    # Summary
    dt = time.time() - t0
    results['meta'] = {
        'phase': 'SUFFIX_MODE_ASSIGNMENT',
        'phase_number': 469,
        'n_classified_lines': len(classified_lines),
        'n_tokens': len(all_tokens),
        'n_perm': N_PERM,
        'seed': SEED,
        'runtime_s': round(dt, 1),
    }

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    for test_id in ['S1', 'S2', 'S3', 'S4']:
        v = results[test_id].get('verdict', 'N/A')
        print(f"  {test_id}: {v}")
    print(f"\nRuntime: {dt:.1f}s")

    # Save
    out_path = RESULTS_DIR / "suffix_mode_assignment.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
