#!/usr/bin/env python3
"""
Phase 530: Cross-Line Hazard Continuity

Research question: C1429 says lines are i.i.d. for category (MI=0.032 bits) and
suffix mode (MI=0.003 bits). C1451 says Mode B carries 100% of forbidden violations.
C1463 shows lines route hazard to line-final (CLOSURE zone). Does one line's closing
hazard predict the next line's opening safety? Is there sequential hazard structure
across lines invisible to category-level analysis?

Seven tests:
  1. Cross-line hazard MI (compare with C1429's 0.032 bits)
  2. Mode-stratified analysis (B->B, A->A, A->B, B->A pairs)
  3. Closure->opening bridge (line N Q4 hazard vs line N+1 Q0 hazard)
  4. HIGH frame carry-over (line N ends HIGH -> what opens line N+1)
  5. e->y recovery after hazard (above-median HIGH -> enriched e->y at next Q0)
  6. Within-paragraph vs cross-paragraph correlation
  7. Autocorrelation lag structure (lags 1-4)

Script: phases/CROSS_LINE_HAZARD/scripts/cross_line_hazard.py
Results: phases/CROSS_LINE_HAZARD/results/cross_line_hazard.json
"""

import sys
import os
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

# Force UTF-8 on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from scipy import stats as scipy_stats

from scripts.voynich import Transcript, Morphology, decompose_middle_hmt


# =============================================================================
# Data Loading
# =============================================================================

def load_frame_hazard_map():
    """Load frame -> hazard class map from decoder_maps.json."""
    map_path = PROJECT_ROOT / 'data' / 'decoder_maps.json'
    with open(map_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    entries = data['maps']['frame_hazard']['entries']
    return {k: v['value'] for k, v in entries.items()}


def load_suffix_mode_centroids():
    """Load suffix mode centroids from decoder_maps.json."""
    map_path = PROJECT_ROOT / 'data' / 'decoder_maps.json'
    with open(map_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    smc = data['maps']['suffix_mode_centroids']
    return smc


def classify_hazard(head, frame_str, frame_map):
    """Classify a token's hazard class based on HEAD and frame."""
    if head == 'k':
        return 'IMMUNE'
    elif frame_str and frame_str in frame_map:
        return frame_map[frame_str]
    elif frame_str:
        return 'LOW'
    else:
        return 'LOW'


def classify_suffix_mode(tokens_on_line, morph, centroids):
    """
    Classify a line's suffix mode from its tokens.
    Uses centroids from decoder_maps.json (C1231).
    Features: [terminal_frac, checkpoint_frac, iterative_frac, bare_frac]
    Returns 'A', 'B', or None if insufficient data.
    """
    TERMINAL_SUFFIXES = {'y', 'ey', 'edy', 'dy', 'eedy', 'eey', 'hy', 'ly', 'ry',
                         'eody', 'eoy', 'ody', 'oy'}
    CHECKPOINT_SUFFIXES = {'aiin', 'ain', 'oiin', 'iin', 'in'}
    ITERATIVE_SUFFIXES = {'ol', 'or', 'al', 'ar', 'am'}

    suffix_count = 0
    terminal_count = 0
    checkpoint_count = 0
    iterative_count = 0
    bare_count = 0

    for tok in tokens_on_line:
        m = morph.extract(tok)
        if not m or not m.middle:
            continue
        suffix_count += 1
        sfx = m.suffix
        if sfx is None or sfx == '':
            bare_count += 1
        elif sfx in TERMINAL_SUFFIXES:
            terminal_count += 1
        elif sfx in CHECKPOINT_SUFFIXES:
            checkpoint_count += 1
        elif sfx in ITERATIVE_SUFFIXES:
            iterative_count += 1
        else:
            bare_count += 1  # unknown suffix treated as bare

    if suffix_count < 3:
        return None

    total = terminal_count + checkpoint_count + iterative_count + bare_count
    if total == 0:
        return None

    # Feature order: terminal_frac, checkpoint_frac, iterative_frac, bare_frac
    vec = np.array([
        terminal_count / total,
        checkpoint_count / total,
        iterative_count / total,
        bare_count / total
    ])

    centroid_a = np.array(centroids['mode_a'])
    centroid_b = np.array(centroids['mode_b'])

    dist_a = np.linalg.norm(vec - centroid_a)
    dist_b = np.linalg.norm(vec - centroid_b)

    return 'A' if dist_a < dist_b else 'B'


def load_b_tokens():
    """
    Load all Currier B tokens with per-token hazard classification
    and per-line aggregation.

    Returns:
        line_data: dict keyed by (folio, line_num) -> {
            'tokens': list of token dicts,
            'folio': str,
            'line_num': int,
            'hazard_profile': Counter of hazard classes,
            'suffix_mode': 'A'|'B'|None,
            'para_idx': int (paragraph index within folio),
            'is_para_boundary': bool,
        }
        folio_line_order: dict keyed by folio -> sorted list of line_nums
    """
    tx = Transcript()
    morph = Morphology()
    frame_map = load_frame_hazard_map()
    centroids = load_suffix_mode_centroids()

    GALLOWS = {'k', 't', 'p', 'f'}

    # Collect B tokens grouped by (folio, line)
    lines_tokens = defaultdict(list)
    for token in tx.currier_b():
        if '*' in token.word or not token.word.strip():
            continue
        # Skip labels
        if hasattr(token, 'placement') and token.placement and token.placement.startswith('L'):
            continue

        m = morph.extract(token.word)
        if not m or not m.middle:
            continue

        head, mods, term, frame_str = decompose_middle_hmt(m.middle)
        hazard_class = classify_hazard(head, frame_str, frame_map)

        tok_dict = {
            'word': token.word,
            'folio': token.folio,
            'line': token.line,
            'middle': m.middle,
            'prefix': m.prefix,
            'suffix': m.suffix,
            'head': head,
            'term': term,
            'frame_str': frame_str,
            'hazard_class': hazard_class,
        }
        lines_tokens[(token.folio, token.line)].append(tok_dict)

    # Build folio -> sorted line_nums
    folio_lines = defaultdict(set)
    for (folio, line_num) in lines_tokens:
        folio_lines[folio].add(line_num)
    folio_line_order = {f: sorted(lns) for f, lns in folio_lines.items()}

    # Detect paragraph boundaries (gallows-initial)
    folio_para_boundaries = {}
    for folio, line_nums in folio_line_order.items():
        boundaries = []
        for ln in line_nums:
            toks = lines_tokens[(folio, ln)]
            if toks:
                first_mid = toks[0]['middle']
                if first_mid and first_mid[0] in GALLOWS:
                    boundaries.append(ln)
        if not boundaries or boundaries[0] != line_nums[0]:
            boundaries = [line_nums[0]] + boundaries
        folio_para_boundaries[folio] = boundaries

    # Build line_data with all annotations
    line_data = {}
    for (folio, line_num), toks in lines_tokens.items():
        # Hazard profile
        hazard_counts = Counter(t['hazard_class'] for t in toks)

        # Suffix mode
        words = [t['word'] for t in toks]
        smode = classify_suffix_mode(words, morph, centroids)

        # Paragraph index
        boundaries = folio_para_boundaries.get(folio, [])
        para_idx = 0
        for i, b in enumerate(boundaries):
            if line_num >= b:
                para_idx = i
        is_para_boundary = line_num in boundaries

        # Quintile positions for each token within line
        n_toks = len(toks)
        for i, t in enumerate(toks):
            frac_pos = i / max(1, n_toks - 1) if n_toks > 1 else 0.5
            t['frac_pos'] = frac_pos
            if frac_pos <= 0.2:
                t['quintile'] = 0
            elif frac_pos <= 0.4:
                t['quintile'] = 1
            elif frac_pos <= 0.6:
                t['quintile'] = 2
            elif frac_pos <= 0.8:
                t['quintile'] = 3
            else:
                t['quintile'] = 4

        line_data[(folio, line_num)] = {
            'tokens': toks,
            'folio': folio,
            'line_num': line_num,
            'hazard_profile': hazard_counts,
            'suffix_mode': smode,
            'para_idx': para_idx,
            'is_para_boundary': is_para_boundary,
        }

    return line_data, folio_line_order


# =============================================================================
# Utility Functions
# =============================================================================

def cramers_v(contingency_table):
    """Compute Cramer's V from a contingency table (2D numpy array)."""
    chi2 = 0
    row_sums = contingency_table.sum(axis=1)
    col_sums = contingency_table.sum(axis=0)
    total = contingency_table.sum()
    if total == 0:
        return 0.0
    for i in range(contingency_table.shape[0]):
        for j in range(contingency_table.shape[1]):
            expected = row_sums[i] * col_sums[j] / total
            if expected > 0:
                chi2 += (contingency_table[i, j] - expected) ** 2 / expected
    k = min(contingency_table.shape) - 1
    if k <= 0 or total <= 0:
        return 0.0
    return math.sqrt(chi2 / (total * k))


def mutual_information(joint_counts):
    """
    Compute mutual information in bits from a dict of (x, y) -> count.
    Returns MI in bits.
    """
    total = sum(joint_counts.values())
    if total == 0:
        return 0.0

    # Marginals
    x_counts = Counter()
    y_counts = Counter()
    for (x, y), c in joint_counts.items():
        x_counts[x] += c
        y_counts[y] += c

    mi = 0.0
    for (x, y), c in joint_counts.items():
        if c == 0:
            continue
        p_xy = c / total
        p_x = x_counts[x] / total
        p_y = y_counts[y] / total
        if p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi


def build_consecutive_pairs(folio_line_order, line_data):
    """Build list of consecutive line pairs within each folio."""
    pairs = []
    for folio, line_nums in sorted(folio_line_order.items()):
        for i in range(len(line_nums) - 1):
            ln_a = line_nums[i]
            ln_b = line_nums[i + 1]
            key_a = (folio, ln_a)
            key_b = (folio, ln_b)
            if key_a in line_data and key_b in line_data:
                pairs.append((key_a, key_b))
    return pairs


def get_dominant_hazard(line_info):
    """Get the dominant hazard class for a line (by token count)."""
    hp = line_info['hazard_profile']
    if not hp:
        return 'LOW'
    return hp.most_common(1)[0][0]


def get_hazard_fraction(line_info, hazard_class):
    """Get fraction of tokens in a specific hazard class."""
    hp = line_info['hazard_profile']
    total = sum(hp.values())
    if total == 0:
        return 0.0
    return hp.get(hazard_class, 0) / total


def get_q_tokens(line_info, quintile):
    """Get tokens in a specific quintile of the line."""
    return [t for t in line_info['tokens'] if t['quintile'] == quintile]


def get_q_hazard_frac(line_info, quintile, hazard_class):
    """Get fraction of tokens in quintile that are a given hazard class."""
    toks = get_q_tokens(line_info, quintile)
    if not toks:
        return 0.0
    return sum(1 for t in toks if t['hazard_class'] == hazard_class) / len(toks)


def permutation_test_mi(joint_counts, n_perm=1000, rng=None):
    """Permutation test for MI significance."""
    if rng is None:
        rng = np.random.default_rng(42)

    real_mi = mutual_information(joint_counts)

    # Expand to list of (x, y) pairs
    pairs_list = []
    for (x, y), c in joint_counts.items():
        pairs_list.extend([(x, y)] * c)

    if len(pairs_list) < 10:
        return real_mi, 1.0, 0

    xs = [p[0] for p in pairs_list]
    ys = [p[1] for p in pairs_list]

    count_ge = 0
    for _ in range(n_perm):
        shuffled_ys = list(ys)
        rng.shuffle(shuffled_ys)
        perm_counts = Counter(zip(xs, shuffled_ys))
        perm_mi = mutual_information(perm_counts)
        if perm_mi >= real_mi:
            count_ge += 1

    p_val = (count_ge + 1) / (n_perm + 1)
    return real_mi, p_val, n_perm


# =============================================================================
# Test 1: Cross-Line Hazard MI
# =============================================================================

def test1_cross_line_hazard_mi(pairs, line_data):
    """
    Mutual information between consecutive lines' dominant hazard classes.
    Compare with C1429's category MI=0.032 bits.
    """
    print("\n=== Test 1: Cross-Line Hazard MI ===")

    HAZARD_CLASSES = ['HIGH', 'LOW', 'ZERO', 'IMMUNE']

    # Joint distribution of dominant hazard class
    joint_dominant = Counter()
    for key_a, key_b in pairs:
        dom_a = get_dominant_hazard(line_data[key_a])
        dom_b = get_dominant_hazard(line_data[key_b])
        joint_dominant[(dom_a, dom_b)] += 1

    mi_dominant, p_dom, _ = permutation_test_mi(joint_dominant, n_perm=2000)

    # Joint distribution of per-class fractions (discretized into thirds)
    # For each hazard class, discretize each line's fraction into LOW/MED/HIGH
    class_mis = {}
    for hc in HAZARD_CLASSES:
        fracs_a = []
        fracs_b = []
        for key_a, key_b in pairs:
            fracs_a.append(get_hazard_fraction(line_data[key_a], hc))
            fracs_b.append(get_hazard_fraction(line_data[key_b], hc))

        if not fracs_a:
            continue

        # Discretize into terciles
        arr_a = np.array(fracs_a)
        arr_b = np.array(fracs_b)
        t33_a = np.percentile(arr_a, [33.3, 66.7])
        t33_b = np.percentile(arr_b, [33.3, 66.7])

        def tercile(v, thresholds):
            if v <= thresholds[0]:
                return 'lo'
            elif v <= thresholds[1]:
                return 'mid'
            return 'hi'

        joint_class = Counter()
        for fa, fb in zip(fracs_a, fracs_b):
            joint_class[(tercile(fa, t33_a), tercile(fb, t33_b))] += 1

        mi_val = mutual_information(joint_class)
        class_mis[hc] = mi_val

    # Spearman correlation of HIGH fraction between consecutive lines
    high_a = [get_hazard_fraction(line_data[ka], 'HIGH') for ka, kb in pairs]
    high_b = [get_hazard_fraction(line_data[kb], 'HIGH') for ka, kb in pairs]
    rho_high, p_rho = scipy_stats.spearmanr(high_a, high_b)

    n_pairs = len(pairs)
    print(f"  N consecutive pairs: {n_pairs}")
    print(f"  Dominant hazard MI: {mi_dominant:.4f} bits (p={p_dom:.4f})")
    print(f"  C1429 category MI:  0.032 bits")
    print(f"  Ratio: {mi_dominant / 0.032:.2f}x of category MI")
    print(f"  Per-class tercile MI: {class_mis}")
    print(f"  HIGH fraction Spearman rho: {rho_high:.4f} (p={p_rho:.4f})")

    return {
        'test': 'cross_line_hazard_mi',
        'n_pairs': n_pairs,
        'dominant_hazard_mi_bits': round(mi_dominant, 6),
        'dominant_hazard_mi_p': round(p_dom, 4),
        'c1429_category_mi_bits': 0.032,
        'mi_ratio_to_category': round(mi_dominant / 0.032, 3),
        'per_class_tercile_mi_bits': {k: round(v, 6) for k, v in class_mis.items()},
        'high_fraction_spearman_rho': round(rho_high, 4),
        'high_fraction_spearman_p': round(p_rho, 4),
        'joint_dominant_counts': {f"{k[0]}->{k[1]}": v for k, v in joint_dominant.most_common()},
    }


# =============================================================================
# Test 2: Mode-Stratified Analysis
# =============================================================================

def test2_mode_stratified(pairs, line_data):
    """
    Split consecutive line pairs by suffix mode transitions:
    B->B, A->A, A->B, B->A. C1451 says Mode B carries 100% forbidden violations.
    """
    print("\n=== Test 2: Mode-Stratified Analysis ===")

    mode_pairs = defaultdict(list)
    for key_a, key_b in pairs:
        ma = line_data[key_a]['suffix_mode']
        mb = line_data[key_b]['suffix_mode']
        if ma and mb:
            mode_pairs[f"{ma}->{mb}"].append((key_a, key_b))

    results = {}
    for mode_trans, mpairs in sorted(mode_pairs.items()):
        n = len(mpairs)
        if n < 20:
            results[mode_trans] = {'n': n, 'insufficient': True}
            print(f"  {mode_trans}: N={n} (insufficient)")
            continue

        # HIGH fraction correlation
        high_a = [get_hazard_fraction(line_data[ka], 'HIGH') for ka, kb in mpairs]
        high_b = [get_hazard_fraction(line_data[kb], 'HIGH') for ka, kb in mpairs]
        rho, p = scipy_stats.spearmanr(high_a, high_b)

        # ZERO fraction correlation (e->y safe)
        zero_a = [get_hazard_fraction(line_data[ka], 'ZERO') for ka, kb in mpairs]
        zero_b = [get_hazard_fraction(line_data[kb], 'ZERO') for ka, kb in mpairs]
        rho_z, p_z = scipy_stats.spearmanr(zero_a, zero_b)

        # Mean HIGH fraction for lines in this transition
        mean_high_a = np.mean(high_a)
        mean_high_b = np.mean(high_b)

        # MI of dominant hazard
        joint = Counter()
        for ka, kb in mpairs:
            joint[(get_dominant_hazard(line_data[ka]),
                   get_dominant_hazard(line_data[kb]))] += 1
        mi_val = mutual_information(joint)

        results[mode_trans] = {
            'n': n,
            'high_rho': round(rho, 4),
            'high_p': round(p, 4),
            'zero_rho': round(rho_z, 4),
            'zero_p': round(p_z, 4),
            'mean_high_line_a': round(mean_high_a, 4),
            'mean_high_line_b': round(mean_high_b, 4),
            'dominant_mi_bits': round(mi_val, 6),
        }
        print(f"  {mode_trans}: N={n}, HIGH rho={rho:.4f}(p={p:.4f}), "
              f"ZERO rho={rho_z:.4f}(p={p_z:.4f}), MI={mi_val:.4f} bits")

    # B->B vs A->A comparison if both have sufficient data
    bb = results.get('B->B', {})
    aa = results.get('A->A', {})
    comparison = None
    if bb.get('n', 0) >= 20 and aa.get('n', 0) >= 20:
        comparison = {
            'bb_high_rho': bb['high_rho'],
            'aa_high_rho': aa['high_rho'],
            'bb_mi': bb['dominant_mi_bits'],
            'aa_mi': aa['dominant_mi_bits'],
            'bb_mean_high': bb['mean_high_line_a'],
            'aa_mean_high': aa['mean_high_line_a'],
        }
        print(f"  B->B vs A->A: HIGH rho {bb['high_rho']:.4f} vs {aa['high_rho']:.4f}")

    return {
        'test': 'mode_stratified',
        'mode_transitions': results,
        'bb_vs_aa': comparison,
        'total_with_mode': sum(r.get('n', 0) for r in results.values()),
    }


# =============================================================================
# Test 3: Closure->Opening Bridge
# =============================================================================

def test3_closure_opening_bridge(pairs, line_data):
    """
    Line N Q4 (CLOSURE) hazard vs Line N+1 Q0 (SPECIFICATION) hazard.
    Tests whether high-hazard closures predict safe openings.
    """
    print("\n=== Test 3: Closure->Opening Bridge ===")

    HAZARD_CLASSES = ['HIGH', 'LOW', 'ZERO', 'IMMUNE']

    q4_high_fracs = []
    q0_high_fracs = []
    q4_zero_fracs = []
    q0_zero_fracs = []
    q4_immune_fracs = []
    q0_immune_fracs = []

    valid_pairs = 0
    for key_a, key_b in pairs:
        la = line_data[key_a]
        lb = line_data[key_b]

        q4_toks = get_q_tokens(la, 4)
        q0_toks = get_q_tokens(lb, 0)

        if len(q4_toks) < 1 or len(q0_toks) < 1:
            continue

        valid_pairs += 1
        q4_high_fracs.append(sum(1 for t in q4_toks if t['hazard_class'] == 'HIGH') / len(q4_toks))
        q0_high_fracs.append(sum(1 for t in q0_toks if t['hazard_class'] == 'HIGH') / len(q0_toks))
        q4_zero_fracs.append(sum(1 for t in q4_toks if t['hazard_class'] == 'ZERO') / len(q0_toks))
        q0_zero_fracs.append(sum(1 for t in q0_toks if t['hazard_class'] == 'ZERO') / len(q0_toks))
        q4_immune_fracs.append(sum(1 for t in q4_toks if t['hazard_class'] == 'IMMUNE') / len(q4_toks))
        q0_immune_fracs.append(sum(1 for t in q0_toks if t['hazard_class'] == 'IMMUNE') / len(q0_toks))

    # Correlations
    rho_high, p_high = scipy_stats.spearmanr(q4_high_fracs, q0_high_fracs) if valid_pairs >= 10 else (0, 1)
    rho_zero, p_zero = scipy_stats.spearmanr(q4_zero_fracs, q0_zero_fracs) if valid_pairs >= 10 else (0, 1)
    rho_cross_hz, p_cross_hz = scipy_stats.spearmanr(q4_high_fracs, q0_zero_fracs) if valid_pairs >= 10 else (0, 1)
    rho_cross_hi, p_cross_hi = scipy_stats.spearmanr(q4_high_fracs, q0_immune_fracs) if valid_pairs >= 10 else (0, 1)

    # Discretized contingency: Q4 HIGH tercile vs Q0 ZERO tercile
    arr_q4h = np.array(q4_high_fracs)
    arr_q0z = np.array(q0_zero_fracs)
    if valid_pairs >= 30:
        t_q4 = np.percentile(arr_q4h, [33.3, 66.7])
        t_q0 = np.percentile(arr_q0z, [33.3, 66.7])

        def terc(v, t):
            if v <= t[0]: return 0
            elif v <= t[1]: return 1
            return 2

        ct = np.zeros((3, 3), dtype=int)
        for q4h, q0z in zip(q4_high_fracs, q0_zero_fracs):
            ct[terc(q4h, t_q4), terc(q0z, t_q0)] += 1
        v_bridge = cramers_v(ct)
    else:
        v_bridge = 0.0

    print(f"  Valid pairs: {valid_pairs}")
    print(f"  Q4_HIGH -> Q0_HIGH rho: {rho_high:.4f} (p={p_high:.4f})")
    print(f"  Q4_HIGH -> Q0_ZERO rho: {rho_cross_hz:.4f} (p={p_cross_hz:.4f})")
    print(f"  Q4_HIGH -> Q0_IMMUNE rho: {rho_cross_hi:.4f} (p={p_cross_hi:.4f})")
    print(f"  Q4_ZERO -> Q0_ZERO rho: {rho_zero:.4f} (p={p_zero:.4f})")
    print(f"  Bridge V (Q4_HIGH tercile x Q0_ZERO tercile): {v_bridge:.4f}")

    return {
        'test': 'closure_opening_bridge',
        'valid_pairs': valid_pairs,
        'q4_high_to_q0_high_rho': round(rho_high, 4),
        'q4_high_to_q0_high_p': round(p_high, 4),
        'q4_high_to_q0_zero_rho': round(rho_cross_hz, 4),
        'q4_high_to_q0_zero_p': round(p_cross_hz, 4),
        'q4_high_to_q0_immune_rho': round(rho_cross_hi, 4),
        'q4_high_to_q0_immune_p': round(p_cross_hi, 4),
        'q4_zero_to_q0_zero_rho': round(rho_zero, 4),
        'q4_zero_to_q0_zero_p': round(p_zero, 4),
        'bridge_cramers_v': round(v_bridge, 4),
        'mean_q4_high': round(float(np.mean(q4_high_fracs)), 4) if q4_high_fracs else 0,
        'mean_q0_high': round(float(np.mean(q0_high_fracs)), 4) if q0_high_fracs else 0,
        'mean_q0_zero': round(float(np.mean(q0_zero_fracs)), 4) if q0_zero_fracs else 0,
        'mean_q0_immune': round(float(np.mean(q0_immune_fracs)), 4) if q0_immune_fracs else 0,
    }


# =============================================================================
# Test 4: HIGH Frame Carry-Over
# =============================================================================

def test4_high_frame_carryover(pairs, line_data):
    """
    When line N ends with a HIGH-hazard token in Q4, what hazard class
    opens line N+1 (Q0)?
    """
    print("\n=== Test 4: HIGH Frame Carry-Over ===")

    # Get pairs where line N's LAST token is HIGH
    high_end_pairs = []
    nonhigh_end_pairs = []

    for key_a, key_b in pairs:
        la = line_data[key_a]
        lb = line_data[key_b]

        if not la['tokens'] or not lb['tokens']:
            continue

        last_tok = la['tokens'][-1]
        if last_tok['hazard_class'] == 'HIGH':
            high_end_pairs.append((key_a, key_b))
        else:
            nonhigh_end_pairs.append((key_a, key_b))

    # For each set, profile the opening token(s) of the next line
    def profile_opening(pair_list, n_opening=2):
        """Profile the first n_opening tokens of the next line."""
        counts = Counter()
        total = 0
        for ka, kb in pair_list:
            lb = line_data[kb]
            for t in lb['tokens'][:n_opening]:
                counts[t['hazard_class']] += 1
                total += 1
        fracs = {k: round(v / max(1, total), 4) for k, v in counts.items()}
        return fracs, total

    high_end_profile, high_end_n = profile_opening(high_end_pairs)
    nonhigh_end_profile, nonhigh_end_n = profile_opening(nonhigh_end_pairs)

    # Enrichment: after HIGH end, is ZERO/IMMUNE enriched at next opening?
    zero_after_high = high_end_profile.get('ZERO', 0)
    zero_after_nonhigh = nonhigh_end_profile.get('ZERO', 0)
    immune_after_high = high_end_profile.get('IMMUNE', 0)
    immune_after_nonhigh = nonhigh_end_profile.get('IMMUNE', 0)

    zero_enrichment = zero_after_high / max(0.001, zero_after_nonhigh)
    immune_enrichment = immune_after_high / max(0.001, immune_after_nonhigh)

    # Chi-squared test on opening hazard class after HIGH vs non-HIGH ending
    all_classes = sorted(set(list(high_end_profile.keys()) + list(nonhigh_end_profile.keys())))
    if len(all_classes) >= 2 and high_end_n >= 10 and nonhigh_end_n >= 10:
        ct = np.zeros((2, len(all_classes)), dtype=int)
        for j, hc in enumerate(all_classes):
            ct[0, j] = int(high_end_profile.get(hc, 0) * high_end_n)
            ct[1, j] = int(nonhigh_end_profile.get(hc, 0) * nonhigh_end_n)
        # Recompute from raw counts for accuracy
        ct_raw = np.zeros((2, len(all_classes)), dtype=int)
        for ka, kb in high_end_pairs:
            for t in line_data[kb]['tokens'][:2]:
                j = all_classes.index(t['hazard_class'])
                ct_raw[0, j] += 1
        for ka, kb in nonhigh_end_pairs:
            for t in line_data[kb]['tokens'][:2]:
                j = all_classes.index(t['hazard_class'])
                ct_raw[1, j] += 1
        v_carryover = cramers_v(ct_raw)
        chi2_val = sum(ct_raw.flatten())  # approximate
    else:
        v_carryover = 0.0

    print(f"  HIGH-ending pairs: {len(high_end_pairs)}")
    print(f"  Non-HIGH-ending pairs: {len(nonhigh_end_pairs)}")
    print(f"  Opening profile after HIGH end:     {high_end_profile}")
    print(f"  Opening profile after non-HIGH end: {nonhigh_end_profile}")
    print(f"  ZERO enrichment after HIGH: {zero_enrichment:.3f}x")
    print(f"  IMMUNE enrichment after HIGH: {immune_enrichment:.3f}x")
    print(f"  Cramer's V: {v_carryover:.4f}")

    return {
        'test': 'high_frame_carryover',
        'high_ending_pairs': len(high_end_pairs),
        'nonhigh_ending_pairs': len(nonhigh_end_pairs),
        'opening_after_high': high_end_profile,
        'opening_after_nonhigh': nonhigh_end_profile,
        'zero_enrichment': round(zero_enrichment, 3),
        'immune_enrichment': round(immune_enrichment, 3),
        'cramers_v': round(v_carryover, 4),
    }


# =============================================================================
# Test 5: e->y Recovery After Hazard
# =============================================================================

def test5_ey_recovery(pairs, line_data):
    """
    Lines with above-median HIGH fraction -> is e->y enriched at the
    next line's Q0 (SPECIFICATION zone)?
    """
    print("\n=== Test 5: e->y Recovery After Hazard ===")

    # Compute HIGH fraction for all lines
    all_high_fracs = []
    for key_a, key_b in pairs:
        all_high_fracs.append(get_hazard_fraction(line_data[key_a], 'HIGH'))
    median_high = np.median(all_high_fracs)

    # Split pairs by line A's HIGH fraction
    above_pairs = []
    below_pairs = []
    for i, (key_a, key_b) in enumerate(pairs):
        if all_high_fracs[i] > median_high:
            above_pairs.append((key_a, key_b))
        else:
            below_pairs.append((key_a, key_b))

    # For each group, compute e->y (ZERO) rate at Q0 of next line
    def q0_ey_rate(pair_list):
        zero_count = 0
        total_count = 0
        for ka, kb in pair_list:
            q0 = get_q_tokens(line_data[kb], 0)
            for t in q0:
                total_count += 1
                if t['hazard_class'] == 'ZERO':
                    zero_count += 1
        return zero_count / max(1, total_count), total_count

    above_rate, above_n = q0_ey_rate(above_pairs)
    below_rate, below_n = q0_ey_rate(below_pairs)

    enrichment = above_rate / max(0.001, below_rate)

    # Also check IMMUNE rate
    def q0_immune_rate(pair_list):
        imm_count = 0
        total_count = 0
        for ka, kb in pair_list:
            q0 = get_q_tokens(line_data[kb], 0)
            for t in q0:
                total_count += 1
                if t['hazard_class'] == 'IMMUNE':
                    imm_count += 1
        return imm_count / max(1, total_count), total_count

    above_imm, _ = q0_immune_rate(above_pairs)
    below_imm, _ = q0_immune_rate(below_pairs)
    imm_enrichment = above_imm / max(0.001, below_imm)

    # Fisher exact test (2x2) for ZERO at Q0 after above vs below median HIGH
    a_zero = int(above_rate * above_n)
    a_nonzero = above_n - a_zero
    b_zero = int(below_rate * below_n)
    b_nonzero = below_n - b_zero
    _, fisher_p = scipy_stats.fisher_exact([[a_zero, a_nonzero], [b_zero, b_nonzero]])

    print(f"  Median HIGH fraction: {median_high:.4f}")
    print(f"  Above-median pairs: {len(above_pairs)}, Below: {len(below_pairs)}")
    print(f"  Q0 ZERO (e->y) rate after above-median HIGH: {above_rate:.4f}")
    print(f"  Q0 ZERO (e->y) rate after below-median HIGH: {below_rate:.4f}")
    print(f"  ZERO enrichment: {enrichment:.3f}x (Fisher p={fisher_p:.4f})")
    print(f"  Q0 IMMUNE rate after above-median HIGH: {above_imm:.4f}")
    print(f"  Q0 IMMUNE rate after below-median HIGH: {below_imm:.4f}")
    print(f"  IMMUNE enrichment: {imm_enrichment:.3f}x")

    return {
        'test': 'ey_recovery_after_hazard',
        'median_high_fraction': round(median_high, 4),
        'above_median_pairs': len(above_pairs),
        'below_median_pairs': len(below_pairs),
        'q0_zero_rate_after_above': round(above_rate, 4),
        'q0_zero_rate_after_below': round(below_rate, 4),
        'zero_enrichment': round(enrichment, 3),
        'fisher_p': round(fisher_p, 4),
        'q0_immune_rate_after_above': round(above_imm, 4),
        'q0_immune_rate_after_below': round(below_imm, 4),
        'immune_enrichment': round(imm_enrichment, 3),
    }


# =============================================================================
# Test 6: Within-Paragraph vs Cross-Paragraph
# =============================================================================

def test6_within_vs_cross_paragraph(pairs, line_data):
    """
    Does hazard correlation differ for within-paragraph vs
    cross-paragraph consecutive line pairs?
    """
    print("\n=== Test 6: Within-Paragraph vs Cross-Paragraph ===")

    within_pairs = []
    cross_pairs = []

    for key_a, key_b in pairs:
        la = line_data[key_a]
        lb = line_data[key_b]
        if la['folio'] == lb['folio'] and la['para_idx'] == lb['para_idx']:
            within_pairs.append((key_a, key_b))
        else:
            cross_pairs.append((key_a, key_b))

    def compute_metrics(pair_list, label):
        n = len(pair_list)
        if n < 20:
            print(f"  {label}: N={n} (insufficient)")
            return {'n': n, 'insufficient': True}

        high_a = [get_hazard_fraction(line_data[ka], 'HIGH') for ka, kb in pair_list]
        high_b = [get_hazard_fraction(line_data[kb], 'HIGH') for ka, kb in pair_list]
        rho_h, p_h = scipy_stats.spearmanr(high_a, high_b)

        zero_a = [get_hazard_fraction(line_data[ka], 'ZERO') for ka, kb in pair_list]
        zero_b = [get_hazard_fraction(line_data[kb], 'ZERO') for ka, kb in pair_list]
        rho_z, p_z = scipy_stats.spearmanr(zero_a, zero_b)

        # MI
        joint = Counter()
        for ka, kb in pair_list:
            joint[(get_dominant_hazard(line_data[ka]),
                   get_dominant_hazard(line_data[kb]))] += 1
        mi_val = mutual_information(joint)

        print(f"  {label}: N={n}, HIGH rho={rho_h:.4f}(p={p_h:.4f}), "
              f"ZERO rho={rho_z:.4f}(p={p_z:.4f}), MI={mi_val:.4f} bits")

        return {
            'n': n,
            'high_rho': round(rho_h, 4),
            'high_p': round(p_h, 4),
            'zero_rho': round(rho_z, 4),
            'zero_p': round(p_z, 4),
            'dominant_mi_bits': round(mi_val, 6),
        }

    within_result = compute_metrics(within_pairs, "Within-paragraph")
    cross_result = compute_metrics(cross_pairs, "Cross-paragraph")

    # Bootstrap comparison of HIGH rho
    comparison = None
    if within_result.get('n', 0) >= 20 and cross_result.get('n', 0) >= 20:
        rho_diff = within_result['high_rho'] - cross_result['high_rho']
        comparison = {
            'rho_difference': round(rho_diff, 4),
            'within_stronger': rho_diff > 0,
        }
        print(f"  Rho difference (within - cross): {rho_diff:.4f}")

    return {
        'test': 'within_vs_cross_paragraph',
        'within_paragraph': within_result,
        'cross_paragraph': cross_result,
        'comparison': comparison,
    }


# =============================================================================
# Test 7: Autocorrelation Lag Structure
# =============================================================================

def test7_autocorrelation(folio_line_order, line_data):
    """
    Autocorrelation of HIGH fraction at lags 1-4 within folios.
    """
    print("\n=== Test 7: Autocorrelation Lag Structure ===")

    # Build per-folio HIGH fraction time series
    folio_series = {}
    for folio, line_nums in folio_line_order.items():
        series = []
        for ln in line_nums:
            key = (folio, ln)
            if key in line_data:
                series.append(get_hazard_fraction(line_data[key], 'HIGH'))
        if len(series) >= 8:  # Need enough lines for lag-4
            folio_series[folio] = np.array(series)

    results = {}
    for lag in range(1, 5):
        all_x = []
        all_y = []
        for folio, series in folio_series.items():
            if len(series) > lag:
                all_x.extend(series[:-lag])
                all_y.extend(series[lag:])

        if len(all_x) < 30:
            results[f'lag_{lag}'] = {'n': len(all_x), 'insufficient': True}
            continue

        rho, p = scipy_stats.spearmanr(all_x, all_y)

        # Permutation test within folios
        rng = np.random.default_rng(42 + lag)
        n_perm = 1000
        count_ge = 0
        for _ in range(n_perm):
            perm_x = []
            perm_y = []
            for folio, series in folio_series.items():
                if len(series) > lag:
                    shuffled = rng.permutation(series)
                    perm_x.extend(shuffled[:-lag])
                    perm_y.extend(shuffled[lag:])
            perm_rho, _ = scipy_stats.spearmanr(perm_x, perm_y)
            if abs(perm_rho) >= abs(rho):
                count_ge += 1
        perm_p = (count_ge + 1) / (n_perm + 1)

        results[f'lag_{lag}'] = {
            'n_pairs': len(all_x),
            'spearman_rho': round(rho, 4),
            'parametric_p': round(p, 4),
            'permutation_p': round(perm_p, 4),
        }
        print(f"  Lag {lag}: N={len(all_x)}, rho={rho:.4f} "
              f"(param p={p:.4f}, perm p={perm_p:.4f})")

    # Also compute ZERO and IMMUNE autocorrelation at lag 1
    for hc in ['ZERO', 'IMMUNE']:
        all_x = []
        all_y = []
        for folio, line_nums in folio_line_order.items():
            series = []
            for ln in line_nums:
                key = (folio, ln)
                if key in line_data:
                    series.append(get_hazard_fraction(line_data[key], hc))
            if len(series) >= 4:
                all_x.extend(series[:-1])
                all_y.extend(series[1:])
        if len(all_x) >= 30:
            rho, p = scipy_stats.spearmanr(all_x, all_y)
            results[f'{hc}_lag_1'] = {
                'n_pairs': len(all_x),
                'spearman_rho': round(rho, 4),
                'parametric_p': round(p, 4),
            }
            print(f"  {hc} lag-1: N={len(all_x)}, rho={rho:.4f} (p={p:.4f})")

    return {
        'test': 'autocorrelation_lag_structure',
        'n_folios': len(folio_series),
        'lags': results,
    }


# =============================================================================
# Folio-Shuffled Control
# =============================================================================

def folio_shuffle_control(pairs, line_data, folio_line_order, n_shuffles=500):
    """
    Shuffle lines within each folio to test if any observed cross-line
    correlation is just folio-level shared environment.
    """
    print("\n=== Folio-Shuffle Control ===")

    # Real MI
    joint_real = Counter()
    for key_a, key_b in pairs:
        joint_real[(get_dominant_hazard(line_data[key_a]),
                    get_dominant_hazard(line_data[key_b]))] += 1
    real_mi = mutual_information(joint_real)

    # Real HIGH rho
    real_high_a = [get_hazard_fraction(line_data[ka], 'HIGH') for ka, kb in pairs]
    real_high_b = [get_hazard_fraction(line_data[kb], 'HIGH') for ka, kb in pairs]
    real_rho, _ = scipy_stats.spearmanr(real_high_a, real_high_b)

    rng = np.random.default_rng(42)
    shuffle_mis = []
    shuffle_rhos = []

    for _ in range(n_shuffles):
        # Shuffle line order within each folio
        shuffled_pairs = []
        for folio, line_nums in folio_line_order.items():
            shuffled_lns = list(line_nums)
            rng.shuffle(shuffled_lns)
            for i in range(len(shuffled_lns) - 1):
                ka = (folio, shuffled_lns[i])
                kb = (folio, shuffled_lns[i + 1])
                if ka in line_data and kb in line_data:
                    shuffled_pairs.append((ka, kb))

        # Shuffled MI
        joint_shuf = Counter()
        for ka, kb in shuffled_pairs:
            joint_shuf[(get_dominant_hazard(line_data[ka]),
                        get_dominant_hazard(line_data[kb]))] += 1
        shuffle_mis.append(mutual_information(joint_shuf))

        # Shuffled HIGH rho
        sh_a = [get_hazard_fraction(line_data[ka], 'HIGH') for ka, kb in shuffled_pairs]
        sh_b = [get_hazard_fraction(line_data[kb], 'HIGH') for ka, kb in shuffled_pairs]
        if len(sh_a) >= 10:
            sh_rho, _ = scipy_stats.spearmanr(sh_a, sh_b)
            shuffle_rhos.append(sh_rho)

    mi_p = (sum(1 for m in shuffle_mis if m >= real_mi) + 1) / (n_shuffles + 1)
    rho_p = (sum(1 for r in shuffle_rhos if abs(r) >= abs(real_rho)) + 1) / (n_shuffles + 1) if shuffle_rhos else 1.0

    mean_shuffle_mi = np.mean(shuffle_mis)
    mean_shuffle_rho = np.mean(shuffle_rhos) if shuffle_rhos else 0

    print(f"  Real MI: {real_mi:.4f}, Mean shuffle MI: {mean_shuffle_mi:.4f}, p={mi_p:.4f}")
    print(f"  Real HIGH rho: {real_rho:.4f}, Mean shuffle rho: {mean_shuffle_rho:.4f}, p={rho_p:.4f}")

    return {
        'test': 'folio_shuffle_control',
        'real_mi': round(real_mi, 6),
        'mean_shuffle_mi': round(mean_shuffle_mi, 6),
        'mi_p': round(mi_p, 4),
        'real_high_rho': round(real_rho, 4),
        'mean_shuffle_high_rho': round(mean_shuffle_rho, 4),
        'rho_p': round(rho_p, 4),
        'n_shuffles': n_shuffles,
    }


# =============================================================================
# Main
# =============================================================================

def main():
    print("Phase 530: Cross-Line Hazard Continuity")
    print("=" * 60)

    print("\nLoading data...")
    line_data, folio_line_order = load_b_tokens()
    n_lines = len(line_data)
    n_folios = len(folio_line_order)
    print(f"  Loaded {n_lines} lines across {n_folios} folios")

    # Build consecutive pairs
    pairs = build_consecutive_pairs(folio_line_order, line_data)
    print(f"  Consecutive line pairs: {len(pairs)}")

    # Summary stats
    mode_counts = Counter()
    for ld in line_data.values():
        if ld['suffix_mode']:
            mode_counts[ld['suffix_mode']] += 1
    print(f"  Suffix mode distribution: {dict(mode_counts)}")

    hazard_totals = Counter()
    for ld in line_data.values():
        for hc, cnt in ld['hazard_profile'].items():
            hazard_totals[hc] += cnt
    total_tokens = sum(hazard_totals.values())
    print(f"  Total tokens: {total_tokens}")
    for hc in ['HIGH', 'LOW', 'ZERO', 'IMMUNE']:
        print(f"    {hc}: {hazard_totals.get(hc, 0)} ({hazard_totals.get(hc, 0)/max(1,total_tokens)*100:.1f}%)")

    # Run all tests
    results = {'metadata': {
        'phase': 530,
        'n_lines': n_lines,
        'n_folios': n_folios,
        'n_consecutive_pairs': len(pairs),
        'suffix_mode_distribution': dict(mode_counts),
        'hazard_distribution': dict(hazard_totals),
        'total_tokens': total_tokens,
    }}

    results['test1'] = test1_cross_line_hazard_mi(pairs, line_data)
    results['test2'] = test2_mode_stratified(pairs, line_data)
    results['test3'] = test3_closure_opening_bridge(pairs, line_data)
    results['test4'] = test4_high_frame_carryover(pairs, line_data)
    results['test5'] = test5_ey_recovery(pairs, line_data)
    results['test6'] = test6_within_vs_cross_paragraph(pairs, line_data)
    results['test7'] = test7_autocorrelation(folio_line_order, line_data)
    results['shuffle_control'] = folio_shuffle_control(pairs, line_data, folio_line_order)

    # Summary verdict
    print("\n" + "=" * 60)
    print("SUMMARY VERDICT")
    print("=" * 60)

    t1 = results['test1']
    t3 = results['test3']
    t7 = results['test7']
    sc = results['shuffle_control']

    mi_ratio = t1['mi_ratio_to_category']
    high_rho = t1['high_fraction_spearman_rho']
    bridge_v = t3['bridge_cramers_v']
    lag1_rho = t7['lags'].get('lag_1', {}).get('spearman_rho', 0)
    shuffle_p = sc['mi_p']

    print(f"  Cross-line hazard MI: {t1['dominant_hazard_mi_bits']:.4f} bits "
          f"({mi_ratio:.2f}x of C1429 category MI)")
    print(f"  HIGH fraction rho: {high_rho:.4f}")
    print(f"  Closure->Opening bridge V: {bridge_v:.4f}")
    print(f"  Lag-1 autocorrelation: {lag1_rho:.4f}")
    print(f"  Folio-shuffle control p: {shuffle_p:.4f}")

    # Determine if cross-line hazard is i.i.d. or structured
    is_iid = True
    if t1['dominant_hazard_mi_p'] < 0.05:
        is_iid = False
    if abs(high_rho) > 0.05 and t1['high_fraction_spearman_p'] < 0.05:
        is_iid = False
    if shuffle_p < 0.05:
        is_iid = False

    if is_iid:
        verdict = "CROSS_LINE_HAZARD_IID"
        print(f"\n  VERDICT: {verdict}")
        print("  Cross-line hazard is consistent with i.i.d. (no sequential structure)")
        print("  This EXTENDS C1429 from category/mode to hazard-frame resolution")
    else:
        # Check if it's folio-mediated or genuine
        if shuffle_p >= 0.05:
            verdict = "CROSS_LINE_HAZARD_FOLIO_MEDIATED"
            print(f"\n  VERDICT: {verdict}")
            print("  Cross-line hazard shows correlation but it's folio-level shared environment")
            print("  Consistent with C1429 + C681 (folio-mediated, not sequential)")
        else:
            verdict = "CROSS_LINE_HAZARD_SEQUENTIAL"
            print(f"\n  VERDICT: {verdict}")
            print("  Cross-line hazard shows GENUINE sequential structure beyond folio effect")
            print("  This would EXTEND C1429 with hazard-specific cross-line coupling")

    results['verdict'] = verdict

    # Save results (convert numpy types for JSON)
    def json_safe(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, (np.bool_,)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f'Object of type {type(obj)} is not JSON serializable')

    out_path = PROJECT_ROOT / 'phases' / 'CROSS_LINE_HAZARD' / 'results' / 'cross_line_hazard.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=json_safe)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
