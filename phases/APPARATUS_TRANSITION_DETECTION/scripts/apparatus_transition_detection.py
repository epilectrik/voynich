"""
Phase 438: APPARATUS_TRANSITION_DETECTION
Detect whether paragraphs contain structural phase transitions
consistent with multi-apparatus processing stages.

Tests:
  A: Kernel inflection point detection (DECISIVE)
  B: MIDDLE vocabulary discontinuity
  C: PREFIX channel switching
  D: Opener token clustering
  E: ke/ek ratio discontinuity
  F: FL state index reset (DECISIVE)
  Cross: Breakpoint correlation (A × F)
"""

import json, sys, math
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as sp_stats

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

# ── Constants ────────────────────────────────────────────────

ALPHA_BONFERRONI = 0.05 / 6  # 0.00833
BIC_THRESHOLD = 6
MIN_BODY_BREAKPOINT = 5   # 6+ total lines (header + 5 body)
MIN_BODY_JACCARD = 3
MIN_BODY_PREFIX = 2
MIN_BODY_OPENER = 3
MIN_BODY_KE_EK = 5        # 6+ body AND 3+ lines with ke/ek
MIN_KE_EK_LINES = 3
N_PERM = 1000

FL_STATES = {
    'EARLY': {'i', 'ii', 'in'},
    'MEDIAL': {'r', 'ar', 'al', 'l', 'ol'},
    'LATE': {'o', 'ly', 'am', 'm', 'dy', 'ry', 'y'},
}
STATE_ORDER = {'EARLY': 0, 'MEDIAL': 1, 'LATE': 2}

ROLE_MAP = {}
for cls in [10, 11, 12, 17]:
    ROLE_MAP[cls] = 'CC'
for cls in [8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49]:
    ROLE_MAP[cls] = 'EN'
for cls in [7, 30, 38, 40]:
    ROLE_MAP[cls] = 'FL'
for cls in [9, 13, 14, 23]:
    ROLE_MAP[cls] = 'FQ'
for cls in [1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29]:
    ROLE_MAP[cls] = 'AX'

# ── Pure-Python Statistics ───────────────────────────────────

def rd(x, d=4):
    """Round float or recurse into dict/list."""
    if isinstance(x, float):
        return round(x, d)
    if isinstance(x, dict):
        return {k: rd(v, d) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rd(v, d) for v in x]
    if isinstance(x, np.floating):
        return round(float(x), d)
    if isinstance(x, np.integer):
        return int(x)
    return x


def bic(n, k, rss):
    """Bayesian Information Criterion."""
    if rss <= 0 or n <= k:
        return float('inf')
    return n * math.log(rss / n) + k * math.log(n)


def linear_fit(x, y):
    """Ordinary least squares y = a + b*x. Returns (a, b, rss)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    if n < 2:
        return 0.0, 0.0, float('inf')
    A = np.column_stack([np.ones(n), x])
    coef, residuals, _, _ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    rss = float(np.sum((y - pred) ** 2))
    return float(coef[0]), float(coef[1]), rss


def piecewise_fit(x, y, bp_idx):
    """Two-segment piecewise linear fit at breakpoint index bp_idx.
    Segment 1: indices 0..bp_idx (inclusive)
    Segment 2: indices bp_idx..n-1 (inclusive, shared point)
    Returns (rss_total, params)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    if bp_idx < 1 or bp_idx >= n - 1:
        return float('inf'), {}

    x1, y1 = x[:bp_idx + 1], y[:bp_idx + 1]
    x2, y2 = x[bp_idx:], y[bp_idx:]

    a1, b1, rss1 = linear_fit(x1, y1)
    a2, b2, rss2 = linear_fit(x2, y2)

    return rss1 + rss2, {'a1': a1, 'b1': b1, 'a2': a2, 'b2': b2, 'bp': int(bp_idx)}


def best_breakpoint(x, y):
    """Find best piecewise breakpoint by BIC. Returns (delta_bic, bp_idx, bp_normalized)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)

    _, _, rss_lin = linear_fit(x, y)
    bic_lin = bic(n, 2, rss_lin)

    # Scan interior third only (avoid edge overfitting)
    lo = max(2, n // 3)
    hi = min(n - 2, 2 * n // 3)

    best_bic_pw = float('inf')
    best_bp = None

    for bp in range(lo, hi + 1):
        rss_pw, _ = piecewise_fit(x, y, bp)
        bic_pw = bic(n, 5, rss_pw)  # 2 slopes + 2 intercepts + breakpoint
        if bic_pw < best_bic_pw:
            best_bic_pw = bic_pw
            best_bp = bp

    if best_bp is None:
        return 0.0, None, None

    delta = bic_lin - best_bic_pw
    bp_norm = best_bp / (n - 1) if n > 1 else 0.5
    return delta, best_bp, bp_norm


def compute_jsd(p, q, epsilon=1e-10):
    """Jensen-Shannon divergence between two distributions."""
    p = np.array(p, dtype=float) + epsilon
    q = np.array(q, dtype=float) + epsilon
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log2(p / m)) + 0.5 * np.sum(q * np.log2(q / m)))


def runs_test_categorical(sequence):
    """Wald-Wolfowitz runs test on categorical sequence.
    Binarize by most-common vs rest."""
    if len(sequence) < 4:
        return {'z': 0.0, 'p': 1.0, 'runs': 0, 'n': len(sequence)}

    counts = Counter(sequence)
    most_common = counts.most_common(1)[0][0]
    binary = [1 if s == most_common else 0 for s in sequence]

    n1 = sum(binary)
    n0 = len(binary) - n1
    if n0 == 0 or n1 == 0:
        return {'z': 0.0, 'p': 1.0, 'runs': 0, 'n': len(sequence)}

    runs = 1
    for i in range(1, len(binary)):
        if binary[i] != binary[i - 1]:
            runs += 1

    expected = (2 * n0 * n1) / (n0 + n1) + 1
    denom = (n0 + n1) ** 2 * (n0 + n1 - 1)
    if denom == 0:
        return {'z': 0.0, 'p': 1.0, 'runs': runs, 'n': len(sequence)}
    variance = (2 * n0 * n1 * (2 * n0 * n1 - n0 - n1)) / denom

    if variance <= 0:
        return {'z': 0.0, 'p': 1.0, 'runs': runs, 'n': len(sequence)}

    z = (runs - expected) / math.sqrt(variance)
    p = 2 * sp_stats.norm.cdf(-abs(z))
    return {'z': round(z, 4), 'p': round(p, 6), 'runs': runs, 'n': len(sequence)}


def get_fl_stage(middle):
    """Map MIDDLE to FL state stage."""
    for stage, middles in FL_STATES.items():
        if middle in middles:
            return stage
    return None


# ── Data Loading ─────────────────────────────────────────────

def load_paragraphs():
    """Build paragraph inventory with per-line features."""
    tx = Transcript()
    morph = Morphology()

    # Load class-token map
    ctm_path = PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm = json.load(f)
    token_to_class = ctm['token_to_class']

    # Group tokens by (folio, line) preserving order
    line_tokens = defaultdict(list)
    folio_lines = defaultdict(list)  # folio -> ordered list of line keys
    line_meta = {}

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue

        key = (token.folio, token.line)
        m = morph.extract(w)

        cls = int(token_to_class[w]) if w in token_to_class else None
        role = ROLE_MAP.get(cls, 'UNK') if cls else 'UNK'
        fl_stage = get_fl_stage(m.middle) if m.middle else None

        line_tokens[key].append({
            'word': w,
            'middle': m.middle or '',
            'prefix': m.prefix or '',
            'suffix': m.suffix or '',
            'cls': cls,
            'role': role,
            'fl_stage': fl_stage,
        })

        if key not in line_meta:
            line_meta[key] = {
                'folio': token.folio,
                'line': token.line,
                'section': token.section,
                'par_initial': False,
                'par_final': False,
            }
            folio_lines[token.folio].append(key)

        if token.par_initial:
            line_meta[key]['par_initial'] = True
        if token.par_final:
            line_meta[key]['par_final'] = True

    # Build paragraphs from par_initial/par_final markers
    paragraphs = []
    for folio, keys in folio_lines.items():
        current = []
        for key in keys:
            meta = line_meta[key]
            if meta['par_initial'] and current:
                paragraphs.append(current)
                current = []
            current.append(key)
            if meta['par_final']:
                paragraphs.append(current)
                current = []
        if current:
            paragraphs.append(current)

    # Build per-line feature records
    result = []
    for par_idx, line_keys in enumerate(paragraphs):
        if len(line_keys) < 2:
            continue

        folio = line_meta[line_keys[0]]['folio']
        section = line_meta[line_keys[0]]['section']

        line_records = []
        for lk in line_keys:
            tokens = line_tokens[lk]
            if not tokens:
                continue

            # Kernel fractions
            total_k = sum(t['middle'].count('k') for t in tokens)
            total_e = sum(t['middle'].count('e') for t in tokens)
            total_h = sum(t['middle'].count('h') for t in tokens)
            total_chars = sum(len(t['middle']) for t in tokens)

            k_frac = total_k / total_chars if total_chars > 0 else 0
            e_frac = total_e / total_chars if total_chars > 0 else 0
            h_frac = total_h / total_chars if total_chars > 0 else 0

            # MIDDLE set
            middles = set(t['middle'] for t in tokens if t['middle'])

            # PREFIX distribution
            prefix_dist = Counter(t['prefix'] for t in tokens if t['prefix'])

            # Opener
            opener_word = tokens[0]['word']
            opener_cls = tokens[0]['cls']
            opener_role = tokens[0]['role']

            # ke/ek counts
            ke_count = sum(1 for t in tokens if 'ke' in t['middle'])
            ek_count = sum(1 for t in tokens if 'ek' in t['middle'])

            # FL state: first and last FL tokens on this line
            fl_stages = [t['fl_stage'] for t in tokens if t['fl_stage'] is not None]
            first_fl = fl_stages[0] if fl_stages else None
            last_fl = fl_stages[-1] if fl_stages else None

            line_records.append({
                'key': lk,
                'n_tokens': len(tokens),
                'k_frac': k_frac,
                'e_frac': e_frac,
                'h_frac': h_frac,
                'total_kernel_chars': total_chars,
                'middles': middles,
                'prefix_dist': prefix_dist,
                'opener_word': opener_word,
                'opener_cls': opener_cls,
                'opener_role': opener_role,
                'ke_count': ke_count,
                'ek_count': ek_count,
                'first_fl': first_fl,
                'last_fl': last_fl,
            })

        if len(line_records) < 2:
            continue

        # Body = everything after header (line_records[0])
        body = line_records[1:]

        result.append({
            'par_id': f'{folio}_p{par_idx}',
            'folio': folio,
            'section': section,
            'header': line_records[0],
            'body': body,
            'all_lines': line_records,
            'n_body': len(body),
        })

    return result


# ── Test A: Kernel Inflection Point Detection ────────────────

def test_a_kernel_inflection(paragraphs):
    """Fit piecewise vs linear on h-kernel fraction through body lines."""
    qualifying = [p for p in paragraphs if p['n_body'] >= MIN_BODY_BREAKPOINT]
    print(f"  Test A: {len(qualifying)} paragraphs with {MIN_BODY_BREAKPOINT}+ body lines")

    breakpoint_results = []
    for p in qualifying:
        body = p['body']
        # Filter lines with enough kernel chars (at least 3)
        valid = [(i, ln) for i, ln in enumerate(body) if ln['total_kernel_chars'] >= 3]
        if len(valid) < MIN_BODY_BREAKPOINT:
            continue

        x = np.array([v[0] for v in valid], dtype=float)
        y = np.array([v[1]['h_frac'] for v in valid], dtype=float)

        delta_bic, bp_idx, bp_norm = best_breakpoint(x, y)

        breakpoint_results.append({
            'par_id': p['par_id'],
            'section': p['section'],
            'n_body': p['n_body'],
            'delta_bic': delta_bic,
            'bp_idx': bp_idx,
            'bp_norm': bp_norm,
            'has_breakpoint': delta_bic > BIC_THRESHOLD,
        })

    n_total = len(breakpoint_results)
    n_bp = sum(1 for r in breakpoint_results if r['has_breakpoint'])
    rate = n_bp / n_total if n_total > 0 else 0

    # Breakpoint position clustering
    bp_positions = [r['bp_norm'] for r in breakpoint_results if r['has_breakpoint'] and r['bp_norm'] is not None]
    if len(bp_positions) >= 5:
        ks_stat, ks_p = sp_stats.kstest(bp_positions, 'uniform')
    else:
        ks_stat, ks_p = 0.0, 1.0

    # Section stratification
    by_section = defaultdict(lambda: {'n': 0, 'bp': 0})
    for r in breakpoint_results:
        by_section[r['section']]['n'] += 1
        if r['has_breakpoint']:
            by_section[r['section']]['bp'] += 1
    section_rates = {s: rd(d['bp'] / d['n']) if d['n'] > 0 else 0 for s, d in by_section.items()}

    # Verdict
    if rate > 0.30:
        verdict = 'MULTI_APPARATUS_SUPPORTED'
    elif rate > 0.10:
        verdict = 'BREAKPOINT_MARGINAL'
    else:
        verdict = 'SINGLE_PROCESS_PARSIMONIOUS'

    delta_bics = [r['delta_bic'] for r in breakpoint_results]

    print(f"    Breakpoints: {n_bp}/{n_total} ({rate:.1%})")
    print(f"    KS vs uniform: stat={ks_stat:.4f}, p={ks_p:.4f}")
    print(f"    Verdict: {verdict}")

    return rd({
        'n_paragraphs': n_total,
        'breakpoint_count': n_bp,
        'breakpoint_rate': rate,
        'mean_delta_bic': float(np.mean(delta_bics)) if delta_bics else 0,
        'median_delta_bic': float(np.median(delta_bics)) if delta_bics else 0,
        'bp_position_ks_stat': float(ks_stat),
        'bp_position_ks_p': float(ks_p),
        'bp_positions': bp_positions,
        'by_section': section_rates,
        'verdict': verdict,
    })


# ── Test B: MIDDLE Vocabulary Discontinuity ──────────────────

def test_b_middle_discontinuity(paragraphs):
    """Find minimum Jaccard position within paragraphs; test clustering."""
    qualifying = [p for p in paragraphs if p['n_body'] >= MIN_BODY_JACCARD + 1]
    print(f"  Test B: {len(qualifying)} paragraphs with {MIN_BODY_JACCARD + 1}+ body lines")

    min_positions = []
    all_jaccards = []

    for p in qualifying:
        body = p['body']
        jaccards = []
        for i in range(len(body) - 1):
            m1 = body[i]['middles']
            m2 = body[i + 1]['middles']
            if not m1 and not m2:
                j = 0.0
            elif not m1 or not m2:
                j = 0.0
            else:
                j = len(m1 & m2) / len(m1 | m2)
            jaccards.append(j)

        if not jaccards:
            continue

        min_idx = int(np.argmin(jaccards))
        min_pos = min_idx / (len(jaccards) - 1) if len(jaccards) > 1 else 0.5
        min_positions.append(min_pos)
        all_jaccards.append({
            'par_id': p['par_id'],
            'section': p['section'],
            'min_jaccard': jaccards[min_idx],
            'min_pos': min_pos,
            'mean_jaccard': float(np.mean(jaccards)),
        })

    # KS test against uniform
    if len(min_positions) >= 10:
        ks_stat, ks_p = sp_stats.kstest(min_positions, 'uniform')
    else:
        ks_stat, ks_p = 0.0, 1.0

    # Section stratification
    by_section = defaultdict(list)
    for r in all_jaccards:
        by_section[r['section']].append(r['min_pos'])
    section_ks = {}
    for s, positions in by_section.items():
        if len(positions) >= 5:
            st, pv = sp_stats.kstest(positions, 'uniform')
            section_ks[s] = rd({'n': len(positions), 'ks_stat': float(st), 'ks_p': float(pv)})
        else:
            section_ks[s] = {'n': len(positions), 'ks_stat': 0.0, 'ks_p': 1.0}

    verdict = 'VOCABULARY_DISCONTINUITY_STRUCTURED' if ks_p < ALPHA_BONFERRONI else 'VOCABULARY_DISCONTINUITY_UNIFORM'

    mean_jaccard = float(np.mean([r['mean_jaccard'] for r in all_jaccards])) if all_jaccards else 0
    mean_min_jaccard = float(np.mean([r['min_jaccard'] for r in all_jaccards])) if all_jaccards else 0

    print(f"    Mean Jaccard: {mean_jaccard:.4f}, Mean min-Jaccard: {mean_min_jaccard:.4f}")
    print(f"    KS vs uniform: stat={ks_stat:.4f}, p={ks_p:.4f}")
    print(f"    Verdict: {verdict}")

    return rd({
        'n_paragraphs': len(all_jaccards),
        'mean_jaccard': mean_jaccard,
        'mean_min_jaccard': mean_min_jaccard,
        'min_position_ks_stat': float(ks_stat),
        'min_position_ks_p': float(ks_p),
        'by_section': section_ks,
        'verdict': verdict,
    })


# ── Test C: PREFIX Channel Switching ─────────────────────────

def test_c_prefix_switching(paragraphs):
    """Compute JSD between consecutive lines; test for channel resets."""
    qualifying = [p for p in paragraphs if p['n_body'] >= MIN_BODY_PREFIX + 1]
    print(f"  Test C: {len(qualifying)} paragraphs with {MIN_BODY_PREFIX + 1}+ body lines")

    switch_results = []

    for p in qualifying:
        all_lines = p['all_lines']  # Including header
        if len(all_lines) < 3:
            continue

        # Compute JSD between consecutive lines
        # Build shared prefix vocabulary
        all_prefixes = set()
        for ln in all_lines:
            all_prefixes.update(ln['prefix_dist'].keys())
        if not all_prefixes:
            continue
        prefix_list = sorted(all_prefixes)

        def to_vec(dist):
            return [dist.get(p, 0) for p in prefix_list]

        jsds = []
        for i in range(len(all_lines) - 1):
            v1 = to_vec(all_lines[i]['prefix_dist'])
            v2 = to_vec(all_lines[i + 1]['prefix_dist'])
            if sum(v1) == 0 or sum(v2) == 0:
                jsds.append(0.0)
            else:
                jsds.append(compute_jsd(v1, v2))

        if len(jsds) < 2:
            continue

        opening_jsd = jsds[0]  # header → first body line
        interior_jsds = jsds[1:]  # body line pairs
        max_interior_jsd = max(interior_jsds) if interior_jsds else 0

        has_switch = max_interior_jsd >= opening_jsd and opening_jsd > 0

        switch_results.append({
            'par_id': p['par_id'],
            'section': p['section'],
            'opening_jsd': opening_jsd,
            'max_interior_jsd': max_interior_jsd,
            'mean_interior_jsd': float(np.mean(interior_jsds)) if interior_jsds else 0,
            'has_switch': has_switch,
        })

    n_total = len(switch_results)
    n_switch = sum(1 for r in switch_results if r['has_switch'])
    rate = n_switch / n_total if n_total > 0 else 0

    # Section stratification
    by_section = defaultdict(lambda: {'n': 0, 'switch': 0})
    for r in switch_results:
        by_section[r['section']]['n'] += 1
        if r['has_switch']:
            by_section[r['section']]['switch'] += 1
    section_rates = {s: rd({'n': d['n'], 'rate': d['switch'] / d['n'] if d['n'] > 0 else 0})
                     for s, d in by_section.items()}

    opening_mean = float(np.mean([r['opening_jsd'] for r in switch_results])) if switch_results else 0
    interior_mean = float(np.mean([r['mean_interior_jsd'] for r in switch_results])) if switch_results else 0

    verdict = 'PREFIX_SWITCHING_DETECTED' if rate > 0.20 else 'PREFIX_GRADIENT_ONLY'

    print(f"    Opening JSD mean: {opening_mean:.4f}, Interior JSD mean: {interior_mean:.4f}")
    print(f"    Switch rate: {n_switch}/{n_total} ({rate:.1%})")
    print(f"    Verdict: {verdict}")

    return rd({
        'n_paragraphs': n_total,
        'n_switches': n_switch,
        'switch_rate': rate,
        'opening_jsd_mean': opening_mean,
        'interior_jsd_mean': interior_mean,
        'by_section': section_rates,
        'verdict': verdict,
    })


# ── Test D: Opener Token Clustering ──────────────────────────

def test_d_opener_clustering(paragraphs):
    """Runs test on opener role sequences within paragraphs."""
    qualifying = [p for p in paragraphs if p['n_body'] >= MIN_BODY_OPENER + 1]
    print(f"  Test D: {len(qualifying)} paragraphs with {MIN_BODY_OPENER + 1}+ body lines")

    runs_results = []

    for p in qualifying:
        body = p['body']
        roles = [ln['opener_role'] for ln in body]
        # Filter out UNK
        roles = [r for r in roles if r != 'UNK']
        if len(roles) < 4:
            continue

        result = runs_test_categorical(roles)
        result['par_id'] = p['par_id']
        result['section'] = p['section']
        result['sequence'] = roles
        runs_results.append(result)

    z_values = [r['z'] for r in runs_results]
    mean_z = float(np.mean(z_values)) if z_values else 0
    median_z = float(np.median(z_values)) if z_values else 0

    # Section stratification
    by_section = defaultdict(list)
    for r in runs_results:
        by_section[r['section']].append(r['z'])
    section_stats = {s: rd({'n': len(zs), 'mean_z': float(np.mean(zs)), 'median_z': float(np.median(zs))})
                     for s, zs in by_section.items()}

    n_clustering = sum(1 for r in runs_results if r['z'] < -2.0)
    clustering_rate = n_clustering / len(runs_results) if runs_results else 0

    verdict = 'OPENER_CLUSTERING_DETECTED' if median_z < -2.0 else 'OPENER_ORDERING_RANDOM'

    print(f"    Mean z: {mean_z:.4f}, Median z: {median_z:.4f}")
    print(f"    Clustering rate (z<-2): {n_clustering}/{len(runs_results)} ({clustering_rate:.1%})")
    print(f"    Verdict: {verdict}")

    return rd({
        'n_paragraphs': len(runs_results),
        'mean_z': mean_z,
        'median_z': median_z,
        'n_clustering': n_clustering,
        'clustering_rate': clustering_rate,
        'by_section': section_stats,
        'verdict': verdict,
    })


# ── Test E: ke/ek Ratio Discontinuity ────────────────────────

def test_e_ke_ek_changepoint(paragraphs):
    """Detect changepoints in per-line ke/ek balance."""
    qualifying = []
    n_excluded = 0
    for p in paragraphs:
        if p['n_body'] < MIN_BODY_KE_EK:
            continue
        body = p['body']
        ke_ek_lines = [(i, ln) for i, ln in enumerate(body)
                       if ln['ke_count'] + ln['ek_count'] > 0]
        if len(ke_ek_lines) >= MIN_KE_EK_LINES:
            qualifying.append((p, ke_ek_lines))
        else:
            n_excluded += 1

    print(f"  Test E: {len(qualifying)} qualifying paragraphs ({n_excluded} excluded for sparsity)")

    if len(qualifying) < 10:
        print(f"    INSUFFICIENT DATA ({len(qualifying)} < 10)")
        return rd({
            'n_paragraphs': len(qualifying),
            'n_excluded_sparse': n_excluded,
            'verdict': 'INSUFFICIENT_KE_EK_DATA',
        })

    # For each qualifying paragraph, test for changepoint
    n_changepoints_obs = 0
    para_bics = []
    for p, ke_ek_lines in qualifying:
        indices = [kl[0] for kl in ke_ek_lines]
        ratios = [kl[1]['ke_count'] / (kl[1]['ke_count'] + kl[1]['ek_count'])
                  for kl in ke_ek_lines]
        x = np.array(indices, dtype=float)
        y = np.array(ratios, dtype=float)

        delta, _, _ = best_breakpoint(x, y)
        if delta > BIC_THRESHOLD:
            n_changepoints_obs += 1
        para_bics.append(delta)

    obs_rate = n_changepoints_obs / len(qualifying)

    # Permutation test
    rng = np.random.default_rng(42)
    perm_counts = []
    for _ in range(N_PERM):
        count = 0
        for p, ke_ek_lines in qualifying:
            body = p['body']
            # Shuffle line order within paragraph
            shuffled = list(range(len(body)))
            rng.shuffle(shuffled)
            # Re-extract ke/ek from shuffled lines
            ke_ek_shuf = [(i, body[shuffled[i]]) for i in range(len(body))
                          if body[shuffled[i]]['ke_count'] + body[shuffled[i]]['ek_count'] > 0]
            if len(ke_ek_shuf) < MIN_KE_EK_LINES:
                continue
            indices = [kl[0] for kl in ke_ek_shuf]
            ratios = [kl[1]['ke_count'] / (kl[1]['ke_count'] + kl[1]['ek_count'])
                      for kl in ke_ek_shuf]
            x = np.array(indices, dtype=float)
            y = np.array(ratios, dtype=float)
            delta, _, _ = best_breakpoint(x, y)
            if delta > BIC_THRESHOLD:
                count += 1
        perm_counts.append(count)

    perm_p = (sum(1 for c in perm_counts if c >= n_changepoints_obs) + 1) / (N_PERM + 1)

    verdict = 'KE_EK_CHANGEPOINT_DETECTED' if perm_p < ALPHA_BONFERRONI else 'KE_EK_GRADIENT_ONLY'

    print(f"    Observed changepoints: {n_changepoints_obs}/{len(qualifying)} ({obs_rate:.1%})")
    print(f"    Permutation p: {perm_p:.4f}")
    print(f"    Verdict: {verdict}")

    return rd({
        'n_paragraphs': len(qualifying),
        'n_excluded_sparse': n_excluded,
        'n_changepoints': n_changepoints_obs,
        'changepoint_rate': obs_rate,
        'permutation_p': perm_p,
        'null_mean': float(np.mean(perm_counts)),
        'null_std': float(np.std(perm_counts)),
        'verdict': verdict,
    })


# ── Test F: FL State Index Reset ─────────────────────────────

def test_f_fl_reset(paragraphs):
    """Detect cross-line FL state regressions and test for clustering."""
    qualifying = [p for p in paragraphs if p['n_body'] >= MIN_BODY_BREAKPOINT]

    # Collect cross-line FL pairs
    all_pairs = []
    for p in qualifying:
        body = p['body']
        for i in range(len(body) - 1):
            last_fl = body[i]['last_fl']
            first_fl = body[i + 1]['first_fl']
            if last_fl is None or first_fl is None:
                continue
            if last_fl not in STATE_ORDER or first_fl not in STATE_ORDER:
                continue

            regression = STATE_ORDER[last_fl] - STATE_ORDER[first_fl]
            norm_pos = i / (len(body) - 1) if len(body) > 1 else 0.5

            all_pairs.append({
                'par_id': p['par_id'],
                'section': p['section'],
                'line_pair_idx': i,
                'n_body': p['n_body'],
                'from_stage': last_fl,
                'to_stage': first_fl,
                'regression': regression,
                'norm_pos': norm_pos,
            })

    print(f"  Test F: {len(all_pairs)} cross-line FL pairs from {len(qualifying)} paragraphs")

    if len(all_pairs) < 30:
        print(f"    INSUFFICIENT FL DATA ({len(all_pairs)} < 30)")
        return rd({
            'n_pairs': len(all_pairs),
            'verdict': 'INSUFFICIENT_FL_DATA',
        })

    # Major regression events (regression >= 2: LATE→EARLY or stronger)
    # Actually any regression >= 1 is interesting (going backwards at all)
    major = [p for p in all_pairs if p['regression'] >= 1]
    any_regression = [p for p in all_pairs if p['regression'] > 0]

    # Regression distribution
    regression_counts = Counter(p['regression'] for p in all_pairs)

    # Test if major regression positions cluster
    if len(major) >= 5:
        major_positions = [p['norm_pos'] for p in major]
        ks_stat, ks_p = sp_stats.kstest(major_positions, 'uniform')
    else:
        ks_stat, ks_p = 0.0, 1.0

    # Also test all regressions (>0)
    if len(any_regression) >= 5:
        regr_positions = [p['norm_pos'] for p in any_regression]
        ks_regr_stat, ks_regr_p = sp_stats.kstest(regr_positions, 'uniform')
    else:
        ks_regr_stat, ks_regr_p = 0.0, 1.0

    # Section stratification
    by_section = defaultdict(lambda: {'total': 0, 'major': 0, 'regress': 0})
    for p in all_pairs:
        by_section[p['section']]['total'] += 1
        if p['regression'] >= 1:
            by_section[p['section']]['major'] += 1
        if p['regression'] > 0:
            by_section[p['section']]['regress'] += 1

    section_stats = {s: rd({
        'n_pairs': d['total'],
        'major_rate': d['major'] / d['total'] if d['total'] > 0 else 0,
        'regress_rate': d['regress'] / d['total'] if d['total'] > 0 else 0,
    }) for s, d in by_section.items()}

    # Transition matrix
    trans_matrix = Counter((p['from_stage'], p['to_stage']) for p in all_pairs)
    trans_dict = {f"{k[0]}_{k[1]}": v for k, v in trans_matrix.most_common(20)}

    verdict = 'FL_RESET_STRUCTURED' if ks_p < ALPHA_BONFERRONI else 'FL_RESET_UNIFORM'
    if len(major) < 5:
        verdict = 'FL_MAJOR_REGRESSION_RARE'

    major_rate = len(major) / len(all_pairs) if all_pairs else 0
    regress_rate = len(any_regression) / len(all_pairs) if all_pairs else 0

    print(f"    Total pairs: {len(all_pairs)}")
    print(f"    Major regressions (>=1 stage): {len(major)} ({major_rate:.1%})")
    print(f"    Any regression (>0): {len(any_regression)} ({regress_rate:.1%})")
    print(f"    KS major vs uniform: stat={ks_stat:.4f}, p={ks_p:.4f}")
    print(f"    Regression counts: {dict(regression_counts.most_common())}")
    print(f"    Verdict: {verdict}")

    return rd({
        'n_pairs': len(all_pairs),
        'n_major_regression': len(major),
        'major_regression_rate': major_rate,
        'n_any_regression': len(any_regression),
        'any_regression_rate': regress_rate,
        'regression_counts': dict(regression_counts),
        'major_ks_stat': float(ks_stat),
        'major_ks_p': float(ks_p),
        'any_regression_ks_stat': float(ks_regr_stat),
        'any_regression_ks_p': float(ks_regr_p),
        'transition_matrix': trans_dict,
        'by_section': section_stats,
        'verdict': verdict,
    })


# ── Cross-Test: Breakpoint Correlation ───────────────────────

def cross_test_correlation(test_a_result, test_f_result, paragraphs):
    """Correlate Test A breakpoint positions with Test F regression positions."""
    # Check if both tests had structured results
    a_structured = test_a_result['verdict'] == 'MULTI_APPARATUS_SUPPORTED'
    f_structured = test_f_result['verdict'] == 'FL_RESET_STRUCTURED'

    if not (a_structured or test_a_result['verdict'] == 'BREAKPOINT_MARGINAL'):
        return rd({
            'n_overlapping': 0,
            'verdict': 'SKIPPED_NO_BREAKPOINTS',
            'note': f"Test A verdict: {test_a_result['verdict']}",
        })

    if test_f_result.get('verdict', '').startswith('INSUFFICIENT') or test_f_result.get('verdict') == 'FL_MAJOR_REGRESSION_RARE':
        return rd({
            'n_overlapping': 0,
            'verdict': 'SKIPPED_NO_FL_DATA',
            'note': f"Test F verdict: {test_f_result['verdict']}",
        })

    # Get paragraphs with breakpoints from Test A
    bp_positions = {}
    if 'bp_positions' in test_a_result:
        # We need to reconstruct which paragraphs had breakpoints
        # Run a quick re-scan using the same logic
        qualifying_a = [p for p in paragraphs if p['n_body'] >= MIN_BODY_BREAKPOINT]
        for p in qualifying_a:
            body = p['body']
            valid = [(i, ln) for i, ln in enumerate(body) if ln['total_kernel_chars'] >= 3]
            if len(valid) < MIN_BODY_BREAKPOINT:
                continue
            x = np.array([v[0] for v in valid], dtype=float)
            y = np.array([v[1]['h_frac'] for v in valid], dtype=float)
            delta, _, bp_norm = best_breakpoint(x, y)
            if delta > BIC_THRESHOLD and bp_norm is not None:
                bp_positions[p['par_id']] = bp_norm

    # Get FL regression positions per paragraph from Test F data
    # Re-compute to get per-paragraph regression positions
    qualifying_f = [p for p in paragraphs if p['n_body'] >= MIN_BODY_BREAKPOINT]
    fl_regression_positions = defaultdict(list)
    for p in qualifying_f:
        body = p['body']
        for i in range(len(body) - 1):
            last_fl = body[i]['last_fl']
            first_fl = body[i + 1]['first_fl']
            if last_fl is None or first_fl is None:
                continue
            if last_fl not in STATE_ORDER or first_fl not in STATE_ORDER:
                continue
            regression = STATE_ORDER[last_fl] - STATE_ORDER[first_fl]
            if regression >= 1:
                norm_pos = i / (len(body) - 1) if len(body) > 1 else 0.5
                fl_regression_positions[p['par_id']].append(norm_pos)

    # Find overlapping paragraphs
    overlap_pars = set(bp_positions.keys()) & set(fl_regression_positions.keys())

    if len(overlap_pars) < 5:
        return rd({
            'n_overlapping': len(overlap_pars),
            'verdict': 'INSUFFICIENT_OVERLAP',
        })

    # For each overlapping paragraph, correlate breakpoint position with nearest FL regression
    bp_vals = []
    fl_vals = []
    for par_id in sorted(overlap_pars):
        bp = bp_positions[par_id]
        fl_positions = fl_regression_positions[par_id]
        nearest_fl = min(fl_positions, key=lambda x: abs(x - bp))
        bp_vals.append(bp)
        fl_vals.append(nearest_fl)

    rho, p_val = sp_stats.spearmanr(bp_vals, fl_vals)

    if rho > 0.3 and p_val < 0.05:
        verdict = 'BREAKPOINTS_CO_OCCUR'
    elif rho > 0.3:
        verdict = 'BREAKPOINTS_CO_OCCUR_WEAK'
    else:
        verdict = 'BREAKPOINTS_INDEPENDENT'

    print(f"  Cross-Test: {len(overlap_pars)} overlapping paragraphs")
    print(f"    Spearman rho: {rho:.4f}, p: {p_val:.4f}")
    print(f"    Verdict: {verdict}")

    return rd({
        'n_overlapping': len(overlap_pars),
        'spearman_rho': float(rho),
        'spearman_p': float(p_val),
        'verdict': verdict,
    })


# ── Synthesis ────────────────────────────────────────────────

def synthesize(results):
    """Combine all test verdicts into overall assessment."""
    a = results['test_a_kernel_inflection']['verdict']
    b = results['test_b_middle_discontinuity']['verdict']
    c = results['test_c_prefix_switching']['verdict']
    d = results['test_d_opener_clustering']['verdict']
    e = results['test_e_ke_ek_changepoint']['verdict']
    f = results['test_f_fl_reset']['verdict']
    x = results['cross_test_correlation']['verdict']

    a_positive = a == 'MULTI_APPARATUS_SUPPORTED'
    f_positive = f == 'FL_RESET_STRUCTURED'
    x_positive = x == 'BREAKPOINTS_CO_OCCUR'

    supporting = sum([
        b == 'VOCABULARY_DISCONTINUITY_STRUCTURED',
        c == 'PREFIX_SWITCHING_DETECTED',
        d == 'OPENER_CLUSTERING_DETECTED',
        e == 'KE_EK_CHANGEPOINT_DETECTED',
    ])

    if a_positive and f_positive and x_positive:
        overall = 'APPARATUS_TRANSITIONS_CONFIRMED'
        interp = ('Paragraphs show structured phase transitions at co-located '
                  'kernel breakpoints and FL state resets, consistent with '
                  'multi-apparatus processing stages.')
    elif a_positive and f_positive:
        overall = 'APPARATUS_TRANSITIONS_SUPPORTED'
        interp = ('Both decisive tests positive but breakpoints do not co-locate — '
                  'transitions exist but may not be apparatus-driven.')
    elif (a_positive or f_positive) and supporting >= 2:
        overall = 'APPARATUS_TRANSITIONS_SUGGESTIVE'
        interp = ('One decisive test positive with supporting evidence — '
                  'warrants further investigation.')
    elif supporting >= 3:
        overall = 'INTERNAL_STRUCTURE_WITHOUT_TRANSITIONS'
        interp = ('Supporting tests show internal paragraph structure '
                  'but no macro-level breakpoints.')
    elif a == 'BREAKPOINT_MARGINAL' and supporting >= 1:
        overall = 'WEAK_INTERNAL_STRUCTURE'
        interp = ('Marginal breakpoint evidence with some supporting structure — '
                  'paragraphs may have soft phases rather than hard transitions.')
    else:
        overall = 'SINGLE_PROCESS_PARSIMONIOUS'
        interp = ('Paragraphs show smooth gradients without phase transitions — '
                  'single-process model sufficient.')

    return {
        'decisive_tests': {'test_a': a, 'test_f': f},
        'supporting_tests': {'test_b': b, 'test_c': c, 'test_d': d, 'test_e': e},
        'cross_test': x,
        'n_supporting_positive': supporting,
        'overall_verdict': overall,
        'interpretation': interp,
    }


# ── Main ─────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Phase 438: APPARATUS_TRANSITION_DETECTION")
    print("=" * 70)

    print("\nLoading paragraphs...")
    paragraphs = load_paragraphs()
    print(f"  Total paragraphs: {len(paragraphs)}")
    print(f"  With 6+ body lines: {sum(1 for p in paragraphs if p['n_body'] >= 5)}")
    print(f"  With 4+ body lines: {sum(1 for p in paragraphs if p['n_body'] >= 3)}")

    # Section distribution
    section_counts = Counter(p['section'] for p in paragraphs)
    print(f"  Sections: {dict(section_counts.most_common())}")

    results = {
        'phase': 'APPARATUS_TRANSITION_DETECTION',
        'phase_number': 438,
        'total_paragraphs': len(paragraphs),
        'parameters': {
            'bic_threshold': BIC_THRESHOLD,
            'alpha_bonferroni': rd(ALPHA_BONFERRONI),
            'n_permutations': N_PERM,
        },
    }

    print("\n--- Test A: Kernel Inflection Point Detection (DECISIVE) ---")
    results['test_a_kernel_inflection'] = test_a_kernel_inflection(paragraphs)

    print("\n--- Test B: MIDDLE Vocabulary Discontinuity ---")
    results['test_b_middle_discontinuity'] = test_b_middle_discontinuity(paragraphs)

    print("\n--- Test C: PREFIX Channel Switching ---")
    results['test_c_prefix_switching'] = test_c_prefix_switching(paragraphs)

    print("\n--- Test D: Opener Token Clustering ---")
    results['test_d_opener_clustering'] = test_d_opener_clustering(paragraphs)

    print("\n--- Test E: ke/ek Ratio Discontinuity ---")
    results['test_e_ke_ek_changepoint'] = test_e_ke_ek_changepoint(paragraphs)

    print("\n--- Test F: FL State Index Reset (DECISIVE) ---")
    results['test_f_fl_reset'] = test_f_fl_reset(paragraphs)

    print("\n--- Cross-Test: Breakpoint Correlation (A × F) ---")
    results['cross_test_correlation'] = cross_test_correlation(
        results['test_a_kernel_inflection'],
        results['test_f_fl_reset'],
        paragraphs
    )

    print("\n--- Synthesis ---")
    results['synthesis'] = synthesize(results)
    print(f"  Overall: {results['synthesis']['overall_verdict']}")
    print(f"  {results['synthesis']['interpretation']}")

    # Remove raw position lists from output (too verbose)
    if 'bp_positions' in results['test_a_kernel_inflection']:
        n_bp = len(results['test_a_kernel_inflection']['bp_positions'])
        del results['test_a_kernel_inflection']['bp_positions']
        results['test_a_kernel_inflection']['n_bp_positions_recorded'] = n_bp

    # Save
    out_path = PROJECT / 'phases' / 'APPARATUS_TRANSITION_DETECTION' / 'results' / 'apparatus_transition_results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=lambda x: rd(x) if isinstance(x, float) else x)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
