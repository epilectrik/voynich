#!/usr/bin/env python3
"""
Phase 475: GRADIENT_STEEPNESS
=================================
Tests whether the within-line stability→escape gradient (C1359) varies
by folio/program, and whether gradient steepness connects to REGIME
and section identity.

5-test battery (gated):
  T1 (GATE): Gradient variance exceeds noise
  T2 (GATE): Steepness adds info beyond C1168 boundary architecture
  T3: REGIME predicts gradient steepness
  T4: Section effect beyond REGIME
  T5: Gradient shape taxonomy (discrete vs continuous)

Pre-registered prediction: REGIME_1 gentler slopes than REGIME_3.

Extends: C1359 (smooth gradient), C1168 (dual boundary architecture)
Depends on: C121 (49 classes), C1358-C1362 (Phase 474)
"""

import json, sys, math, time, random, functools
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

sys.path.insert(0, str(ROOT / 'phases' / 'TEXT_BLOCK_PARALLEL_OPERATORS' / 'scripts'))
from text_block_parallel_operators import jsd, mann_whitney_u, normal_cdf, chi2_sf

sys.path.insert(0, str(ROOT / 'phases' / 'BLOCK_GALLOWS_ORDERING' / 'scripts'))
from block_gallows_ordering import spearman_rho

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "GRADIENT_STEEPNESS" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_CLASSES = 49
N_QUINTILES = 5
N_PERM = 1000
SEED = 42
MIN_FOLIO_TOKENS = 100
MIN_QUINTILE_TRANSITIONS = 10

# 6-state macro partition
MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}
STATE_ORDER = ['AXM', 'AXm', 'FQ', 'CC', 'FL_HAZ', 'FL_SAFE']
CLASS_TO_STATE = {}
for _state, _classes in MACRO_STATE_PARTITION.items():
    for _c in _classes:
        CLASS_TO_STATE[_c] = _state


def round_floats(obj, digits=6):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    return obj


def assign_quintile(idx, line_len):
    return min(N_QUINTILES - 1, int(idx / line_len * N_QUINTILES))


def linear_slope(ys):
    """Least-squares slope for y values at x=0,1,2,...,n-1."""
    n = len(ys)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2.0
    y_mean = sum(ys) / n
    num = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(ys))
    den = sum((i - x_mean) ** 2 for i in range(n))
    return num / den if den > 0 else 0.0


def ols_r_squared(y, X):
    """Simple OLS R-squared. y = list of floats, X = list of feature-lists."""
    n = len(y)
    if n < 3:
        return 0.0
    p = len(X[0])
    y_mean = sum(y) / n

    # Normal equations: beta = (X'X)^-1 X'y
    # For small p (2-3), compute directly
    XtX = [[0.0] * (p + 1) for _ in range(p + 1)]  # +1 for intercept
    Xty = [0.0] * (p + 1)

    for i in range(n):
        row = [1.0] + list(X[i])  # prepend intercept
        for j in range(p + 1):
            for k in range(p + 1):
                XtX[j][k] += row[j] * row[k]
            Xty[j] += row[j] * y[i]

    # Solve via Gaussian elimination
    aug = [XtX[j][:] + [Xty[j]] for j in range(p + 1)]
    for col in range(p + 1):
        # Find pivot
        max_row = col
        for row in range(col + 1, p + 1):
            if abs(aug[row][col]) > abs(aug[max_row][col]):
                max_row = row
        aug[col], aug[max_row] = aug[max_row], aug[col]

        if abs(aug[col][col]) < 1e-12:
            continue
        for row in range(col + 1, p + 1):
            factor = aug[row][col] / aug[col][col]
            for k in range(col, p + 2):
                aug[row][k] -= factor * aug[col][k]

    # Back substitution
    beta = [0.0] * (p + 1)
    for row in range(p, -1, -1):
        if abs(aug[row][row]) < 1e-12:
            continue
        beta[row] = aug[row][p + 1]
        for k in range(row + 1, p + 1):
            beta[row] -= aug[row][k] * beta[k]
        beta[row] /= aug[row][row]

    # Compute R-squared
    ss_res = 0.0
    ss_tot = 0.0
    for i in range(n):
        row = [1.0] + list(X[i])
        y_pred = sum(b * x for b, x in zip(beta, row))
        ss_res += (y[i] - y_pred) ** 2
        ss_tot += (y[i] - y_mean) ** 2

    return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0


def list_jsd(p, q):
    """JSD between two lists of probabilities."""
    return jsd(p, q)


def kruskal_wallis(groups):
    """Kruskal-Wallis H test. groups = list of lists of values."""
    all_vals = []
    for g_idx, g in enumerate(groups):
        for v in g:
            all_vals.append((v, g_idx))
    all_vals.sort(key=lambda x: x[0])
    n = len(all_vals)

    # Assign ranks
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n and all_vals[j][0] == all_vals[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0  # 1-indexed
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    # Group rank sums
    group_rank_sums = defaultdict(float)
    group_sizes = Counter()
    for idx, (val, g_idx) in enumerate(all_vals):
        group_rank_sums[g_idx] += ranks[idx]
        group_sizes[g_idx] += 1

    k = len(groups)
    H = 0.0
    for g_idx in range(k):
        ni = group_sizes[g_idx]
        if ni == 0:
            continue
        Ri = group_rank_sums[g_idx]
        H += (Ri ** 2) / ni
    H = (12.0 / (n * (n + 1))) * H - 3 * (n + 1)

    # Chi-squared approximation with k-1 df
    df = k - 1
    p_val = chi2_sf(H, df)

    return H, p_val, df


def kmeans(data, k, max_iter=100, seed=42):
    """Simple k-means on list of lists. Returns labels, centroids, inertia."""
    rng = random.Random(seed)
    n = len(data)
    dim = len(data[0])

    # Initialize centroids randomly
    indices = list(range(n))
    rng.shuffle(indices)
    centroids = [data[indices[i]][:] for i in range(k)]

    labels = [0] * n
    for _ in range(max_iter):
        # Assign
        changed = False
        for i in range(n):
            best_c = 0
            best_dist = float('inf')
            for c in range(k):
                d = sum((data[i][j] - centroids[c][j]) ** 2 for j in range(dim))
                if d < best_dist:
                    best_dist = d
                    best_c = c
            if labels[i] != best_c:
                changed = True
            labels[i] = best_c

        if not changed:
            break

        # Update centroids
        for c in range(k):
            members = [data[i] for i in range(n) if labels[i] == c]
            if members:
                centroids[c] = [sum(m[j] for m in members) / len(members) for j in range(dim)]

    # Inertia
    inertia = sum(
        sum((data[i][j] - centroids[labels[i]][j]) ** 2 for j in range(dim))
        for i in range(n)
    )
    return labels, centroids, inertia


def silhouette_score(data, labels):
    """Compute mean silhouette coefficient."""
    n = len(data)
    dim = len(data[0])
    k = max(labels) + 1
    if k < 2:
        return -1.0

    def dist(a, b):
        return math.sqrt(sum((a[j] - b[j]) ** 2 for j in range(dim)))

    silhouettes = []
    for i in range(n):
        ci = labels[i]
        # a(i) = mean distance to same-cluster points
        same = [j for j in range(n) if labels[j] == ci and j != i]
        if not same:
            silhouettes.append(0.0)
            continue
        a_i = sum(dist(data[i], data[j]) for j in same) / len(same)

        # b(i) = min mean distance to other clusters
        b_i = float('inf')
        for c in range(k):
            if c == ci:
                continue
            others = [j for j in range(n) if labels[j] == c]
            if not others:
                continue
            mean_d = sum(dist(data[i], data[j]) for j in others) / len(others)
            b_i = min(b_i, mean_d)

        if b_i == float('inf'):
            silhouettes.append(0.0)
        else:
            s_i = (b_i - a_i) / max(a_i, b_i) if max(a_i, b_i) > 0 else 0.0
            silhouettes.append(s_i)

    return sum(silhouettes) / len(silhouettes) if silhouettes else 0.0


# ── Data Loading ──────────────────────────────────────────────────

def load_data():
    """Load B tokens, regime assignments, AXM data per folio."""
    ctm_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    # Load REGIME assignments (authoritative)
    regime_path = ROOT / 'data' / 'regime_folio_mapping.json'
    with open(regime_path, 'r', encoding='utf-8') as f:
        regime_data = json.load(f)
    folio_to_regime = {f: d['regime'] for f, d in regime_data['regime_assignments'].items()}

    # Load AXM residual data for per-folio AXM self-rates and section
    axm_path = ROOT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' / 'axm_residual_decomposition.json'
    with open(axm_path, 'r', encoding='utf-8') as f:
        axm_data = json.load(f)
    folio_meta = axm_data['folio_data']

    # Build per-folio per-line token lists
    folio_lines = defaultdict(lambda: defaultdict(list))
    total = 0
    classified = 0

    for t in Transcript().currier_b():
        w = t.word.strip()
        if not w or '*' in w:
            continue
        if t.placement.startswith('L'):
            continue
        total += 1
        cls = token_to_class.get(w)
        if cls is not None:
            classified += 1
        folio_lines[t.folio][t.line].append({
            'word': w,
            'cls': cls,
            'folio': t.folio,
            'section': t.section,
        })

    # Organize into per-folio line lists
    folio_data = {}
    for folio in sorted(folio_lines.keys()):
        lines = []
        for line_key in sorted(folio_lines[folio].keys()):
            tokens = folio_lines[folio][line_key]
            classified_tokens = [t for t in tokens if t['cls'] is not None]
            if len(classified_tokens) >= 2:
                lines.append(tokens)

        n_classified = sum(1 for line in lines for t in line if t['cls'] is not None)
        if n_classified < MIN_FOLIO_TOKENS:
            continue

        section = lines[0][0]['section'] if lines else '?'
        regime = folio_to_regime.get(folio, None)
        axm_self = folio_meta.get(folio, {}).get('axm_self', None)

        folio_data[folio] = {
            'lines': lines,
            'section': section,
            'regime': regime,
            'axm_self': axm_self,
            'n_classified': n_classified,
        }

    print(f"  Total B tokens: {total}, classified: {classified}")
    print(f"  Folios with >={MIN_FOLIO_TOKENS} classified tokens: {len(folio_data)}")

    return folio_data, token_to_class


# ── Per-Folio Gradient Computation ────────────────────────────────

def compute_folio_gradient(lines):
    """Compute 5-quintile AXM self-transition profile and slope for a folio."""
    quintile_axm_src = Counter()
    quintile_axm_self = Counter()

    # Also compute entry/interior/exit zone 6-state profiles for C1168 comparison
    zone_state_trans = {z: Counter() for z in ['ENTRY', 'INTERIOR', 'EXIT']}

    for tokens in lines:
        classified = [(i, t) for i, t in enumerate(tokens) if t['cls'] is not None]
        line_len = len(tokens)

        for j in range(len(classified) - 1):
            idx1, tok1 = classified[j]
            idx2, tok2 = classified[j + 1]
            cls1, cls2 = tok1['cls'], tok2['cls']
            state1 = CLASS_TO_STATE[cls1]
            state2 = CLASS_TO_STATE[cls2]

            # Quintile of source
            q = assign_quintile(idx1, line_len)
            if state1 == 'AXM':
                quintile_axm_src[q] += 1
                if state2 == 'AXM':
                    quintile_axm_self[q] += 1

            # Zone classification (for entry/exit divergence)
            if j == 0:
                zone = 'ENTRY'
            elif j + 1 == len(classified) - 1:
                zone = 'EXIT'
            else:
                zone = 'INTERIOR'
            zone_state_trans[zone][(state1, state2)] += 1

    # Compute AXM self-rate per quintile
    profile = []
    valid_quintiles = 0
    for q in range(N_QUINTILES):
        src = quintile_axm_src[q]
        if src >= MIN_QUINTILE_TRANSITIONS:
            profile.append(quintile_axm_self[q] / src)
            valid_quintiles += 1
        else:
            profile.append(None)

    # Compute slope on valid quintiles only
    valid_points = [(i, v) for i, v in enumerate(profile) if v is not None]
    if len(valid_points) >= 3:
        xs = [p[0] for p in valid_points]
        ys = [p[1] for p in valid_points]
        x_mean = sum(xs) / len(xs)
        y_mean = sum(ys) / len(ys)
        num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
        den = sum((x - x_mean) ** 2 for x in xs)
        slope = num / den if den > 0 else 0.0
    else:
        slope = None

    # Compute entry and exit divergence (6-state profile JSD vs interior)
    def zone_profile(zone):
        counts = zone_state_trans[zone]
        total = sum(counts.values())
        if total == 0:
            return [1.0 / len(STATE_ORDER)] * len(STATE_ORDER)
        profile = []
        for s in STATE_ORDER:
            s_count = sum(c for (s1, s2), c in counts.items() if s1 == s)
            profile.append(s_count / total if total > 0 else 0.0)
        # Normalize
        total_p = sum(profile)
        if total_p > 0:
            profile = [p / total_p for p in profile]
        return profile

    interior_prof = zone_profile('INTERIOR')
    entry_prof = zone_profile('ENTRY')
    exit_prof = zone_profile('EXIT')

    entry_div = list_jsd(entry_prof, interior_prof) if sum(zone_state_trans['ENTRY'].values()) >= 10 else None
    exit_div = list_jsd(exit_prof, interior_prof) if sum(zone_state_trans['EXIT'].values()) >= 10 else None

    return {
        'profile': profile,
        'slope': slope,
        'valid_quintiles': valid_quintiles,
        'entry_div': entry_div,
        'exit_div': exit_div,
    }


# ── T1: Gradient Variance Exceeds Noise ───────────────────────────

def test_gradient_variance(folio_data, token_to_class):
    """Gate test: do folio-level slopes have real variance?"""
    print("\n=== T1 (GATE): GRADIENT VARIANCE EXCEEDS NOISE ===")

    # Compute gradient for each folio
    folio_gradients = {}
    for folio, fd in folio_data.items():
        grad = compute_folio_gradient(fd['lines'])
        if grad['slope'] is not None:
            folio_gradients[folio] = grad
            fd['gradient'] = grad  # attach for later tests

    slopes = [folio_gradients[f]['slope'] for f in folio_gradients]
    n_folios = len(slopes)
    obs_variance = sum((s - sum(slopes) / n_folios) ** 2 for s in slopes) / n_folios
    obs_mean = sum(slopes) / n_folios

    print(f"  Folios with valid gradient: {n_folios}")
    print(f"  Mean slope: {obs_mean:.6f}")
    print(f"  Slope variance: {obs_variance:.8f}")
    print(f"  Slope range: [{min(slopes):.4f}, {max(slopes):.4f}]")

    # Corpus-wide profile
    corpus_profile = [0.0] * N_QUINTILES
    counts = [0] * N_QUINTILES
    for f, g in folio_gradients.items():
        for q in range(N_QUINTILES):
            if g['profile'][q] is not None:
                corpus_profile[q] += g['profile'][q]
                counts[q] += 1
    corpus_profile = [corpus_profile[q] / counts[q] if counts[q] > 0 else 0 for q in range(N_QUINTILES)]
    print(f"  Corpus-wide AXM profile: {' '.join(f'Q{q}={v:.3f}' for q, v in enumerate(corpus_profile))}")

    # Permutation test: shuffle token positions within each folio's lines
    rng = random.Random(SEED)
    perm_variances = []

    for perm_i in range(N_PERM):
        perm_slopes = []
        for folio, fd in folio_data.items():
            if folio not in folio_gradients:
                continue
            # Shuffle class assignments within each line (preserving line structure)
            perm_q_axm_src = Counter()
            perm_q_axm_self = Counter()

            for tokens in fd['lines']:
                classified = [t for t in tokens if t['cls'] is not None]
                if len(classified) < 2:
                    continue
                line_len = len(tokens)

                # Shuffle the classified token positions within this line
                cls_list = [t['cls'] for t in classified]
                rng.shuffle(cls_list)

                # Recompute quintile assignments using original positions
                orig_positions = [i for i, t in enumerate(tokens) if t['cls'] is not None]
                for j in range(len(cls_list) - 1):
                    q = assign_quintile(orig_positions[j], line_len)
                    s1 = CLASS_TO_STATE[cls_list[j]]
                    s2 = CLASS_TO_STATE[cls_list[j + 1]]
                    if s1 == 'AXM':
                        perm_q_axm_src[q] += 1
                        if s2 == 'AXM':
                            perm_q_axm_self[q] += 1

            # Compute slope
            perm_profile = []
            for q in range(N_QUINTILES):
                src = perm_q_axm_src[q]
                if src >= MIN_QUINTILE_TRANSITIONS:
                    perm_profile.append(perm_q_axm_self[q] / src)
            if len(perm_profile) >= 3:
                perm_slopes.append(linear_slope(perm_profile))

        if perm_slopes:
            perm_mean = sum(perm_slopes) / len(perm_slopes)
            perm_var = sum((s - perm_mean) ** 2 for s in perm_slopes) / len(perm_slopes)
            perm_variances.append(perm_var)

    perm_p = sum(1 for v in perm_variances if v >= obs_variance) / len(perm_variances) if perm_variances else 1.0

    verdict = 'GATE_OPEN' if perm_p < 0.05 else 'GATE_CLOSED'

    print(f"  Permutation p (variance): {perm_p:.4f}")
    print(f"  Verdict: {verdict}")

    return {
        'test': 'T1_GRADIENT_VARIANCE',
        'verdict': verdict,
        'n_folios': n_folios,
        'mean_slope': obs_mean,
        'slope_variance': obs_variance,
        'slope_range': [min(slopes), max(slopes)],
        'corpus_profile': {f'Q{q}': v for q, v in enumerate(corpus_profile)},
        'perm_p': perm_p,
    }, folio_gradients


# ── T2: Steepness Adds Info Beyond C1168 ──────────────────────────

def test_incremental_info(folio_data, folio_gradients):
    """Gate test: does gradient slope add R-squared beyond entry+exit divergence?"""
    print("\n=== T2 (GATE): STEEPNESS VS C1168 BOUNDARY ARCHITECTURE ===")

    # Collect per-folio: axm_self, entry_div, exit_div, slope
    records = []
    for folio, grad in folio_gradients.items():
        fd = folio_data[folio]
        axm = fd.get('axm_self')
        entry = grad.get('entry_div')
        exit_d = grad.get('exit_div')
        slope = grad.get('slope')

        if all(v is not None for v in [axm, entry, exit_d, slope]):
            records.append({
                'folio': folio,
                'axm_self': axm,
                'entry_div': entry,
                'exit_div': exit_d,
                'slope': slope,
            })

    n = len(records)
    print(f"  Folios with all metrics: {n}")

    if n < 10:
        print("  Insufficient data for regression")
        return {
            'test': 'T2_INCREMENTAL_INFO',
            'verdict': 'INSUFFICIENT_DATA',
            'n': n,
        }

    y = [r['axm_self'] for r in records]

    # Baseline: entry_div + exit_div
    X_base = [[r['entry_div'], r['exit_div']] for r in records]
    r2_base = ols_r_squared(y, X_base)

    # Extended: entry_div + exit_div + slope
    X_ext = [[r['entry_div'], r['exit_div'], r['slope']] for r in records]
    r2_ext = ols_r_squared(y, X_ext)

    delta_r2 = r2_ext - r2_base

    # Also check slope alone
    X_slope = [[r['slope']] for r in records]
    r2_slope = ols_r_squared(y, X_slope)

    # Correlation of slope with entry/exit div
    slopes = [r['slope'] for r in records]
    entries = [r['entry_div'] for r in records]
    exits = [r['exit_div'] for r in records]

    rho_entry, p_entry = spearman_rho(slopes, entries)
    rho_exit, p_exit = spearman_rho(slopes, exits)

    verdict = 'GATE_OPEN' if delta_r2 > 0.02 else 'GATE_CLOSED'

    print(f"  R-squared (entry+exit): {r2_base:.4f}")
    print(f"  R-squared (entry+exit+slope): {r2_ext:.4f}")
    print(f"  Delta R-squared: {delta_r2:.4f}")
    print(f"  R-squared (slope alone): {r2_slope:.4f}")
    print(f"  Slope-entry corr: rho={rho_entry:.4f}, p={p_entry:.4f}")
    print(f"  Slope-exit corr: rho={rho_exit:.4f}, p={p_exit:.4f}")
    print(f"  Verdict: {verdict}")

    return {
        'test': 'T2_INCREMENTAL_INFO',
        'verdict': verdict,
        'n': n,
        'r2_baseline': r2_base,
        'r2_extended': r2_ext,
        'delta_r2': delta_r2,
        'r2_slope_alone': r2_slope,
        'slope_entry_rho': rho_entry,
        'slope_entry_p': p_entry,
        'slope_exit_rho': rho_exit,
        'slope_exit_p': p_exit,
    }


# ── T3: REGIME Predicts Gradient Steepness ────────────────────────

def test_regime_prediction(folio_data, folio_gradients):
    """Test whether REGIME predicts gradient steepness."""
    print("\n=== T3: REGIME PREDICTS GRADIENT STEEPNESS ===")

    regime_slopes = defaultdict(list)
    herbal_regime_slopes = defaultdict(list)

    for folio, grad in folio_gradients.items():
        fd = folio_data[folio]
        regime = fd.get('regime')
        slope = grad.get('slope')
        if regime is None or slope is None:
            continue
        regime_slopes[regime].append(slope)
        if fd['section'] == 'H':
            herbal_regime_slopes[regime].append(slope)

    # Print per-regime stats
    print(f"  Per-REGIME slope stats:")
    for r in sorted(regime_slopes.keys()):
        slopes = regime_slopes[r]
        mean = sum(slopes) / len(slopes)
        print(f"    {r}: n={len(slopes)}, mean={mean:.6f}")

    # Kruskal-Wallis across all regimes
    regime_order = sorted(regime_slopes.keys())
    groups = [regime_slopes[r] for r in regime_order]
    # Filter out groups with <3 members
    valid_groups = [(r, g) for r, g in zip(regime_order, groups) if len(g) >= 3]

    if len(valid_groups) < 2:
        print("  Insufficient REGIME groups for KW test")
        return {
            'test': 'T3_REGIME_PREDICTION',
            'verdict': 'INSUFFICIENT_DATA',
        }

    kw_H, kw_p, kw_df = kruskal_wallis([g for _, g in valid_groups])

    # Pre-registered directional test: R1 gentler than R3
    r1_slopes = regime_slopes.get('REGIME_1', [])
    r3_slopes = regime_slopes.get('REGIME_3', [])
    if r1_slopes and r3_slopes:
        r1_mean = sum(r1_slopes) / len(r1_slopes)
        r3_mean = sum(r3_slopes) / len(r3_slopes)
        # Gentler = closer to 0 (less negative)
        direction_correct = abs(r1_mean) < abs(r3_mean)
        # Mann-Whitney for R1 vs R3
        mw_U, mw_z, mw_p = mann_whitney_u(r1_slopes, r3_slopes)
    else:
        r1_mean = r3_mean = None
        direction_correct = None
        mw_z = mw_p = None

    # Within-Herbal control
    herbal_result = None
    if len([r for r in herbal_regime_slopes if len(herbal_regime_slopes[r]) >= 3]) >= 2:
        h_groups = [herbal_regime_slopes[r] for r in sorted(herbal_regime_slopes.keys())
                    if len(herbal_regime_slopes[r]) >= 3]
        if len(h_groups) >= 2:
            h_H, h_p, h_df = kruskal_wallis(h_groups)
            herbal_result = {'H': h_H, 'p': h_p, 'df': h_df}
            print(f"  Within-Herbal KW: H={h_H:.3f}, p={h_p:.4f}")
        for r in sorted(herbal_regime_slopes.keys()):
            if herbal_regime_slopes[r]:
                m = sum(herbal_regime_slopes[r]) / len(herbal_regime_slopes[r])
                print(f"    Herbal {r}: n={len(herbal_regime_slopes[r])}, mean={m:.6f}")

    # Verdict
    if kw_p < 0.05 and direction_correct:
        verdict = 'PASS'
    elif kw_p < 0.05:
        verdict = 'PARTIAL'
    else:
        verdict = 'FAIL'

    print(f"  KW: H={kw_H:.3f}, p={kw_p:.4f}, df={kw_df}")
    if direction_correct is not None:
        print(f"  R1 mean={r1_mean:.6f}, R3 mean={r3_mean:.6f}, "
              f"direction {'CORRECT' if direction_correct else 'WRONG'}")
        print(f"  R1 vs R3 MW: z={mw_z:.3f}, p={mw_p:.4f}")
    print(f"  Verdict: {verdict}")

    return {
        'test': 'T3_REGIME_PREDICTION',
        'verdict': verdict,
        'kw_H': kw_H,
        'kw_p': kw_p,
        'kw_df': kw_df,
        'regime_means': {r: sum(s) / len(s) for r, s in regime_slopes.items() if s},
        'regime_n': {r: len(s) for r, s in regime_slopes.items()},
        'r1_mean': r1_mean,
        'r3_mean': r3_mean,
        'direction_correct': direction_correct,
        'r1_r3_mw_z': mw_z,
        'r1_r3_mw_p': mw_p,
        'herbal_control': herbal_result,
    }


# ── T4: Section Effect Beyond REGIME ──────────────────────────────

def test_section_effect(folio_data, folio_gradients):
    """Test section predicts gradient steepness beyond REGIME."""
    print("\n=== T4: SECTION EFFECT BEYOND REGIME ===")

    # Per-section stats
    section_slopes = defaultdict(list)
    regime_section_slopes = defaultdict(lambda: defaultdict(list))

    for folio, grad in folio_gradients.items():
        fd = folio_data[folio]
        slope = grad.get('slope')
        section = fd['section']
        regime = fd.get('regime')
        if slope is None:
            continue
        section_slopes[section].append(slope)
        if regime:
            regime_section_slopes[regime][section].append(slope)

    print(f"  Per-section slope stats:")
    for s in sorted(section_slopes.keys()):
        slopes = section_slopes[s]
        mean = sum(slopes) / len(slopes)
        print(f"    Section {s}: n={len(slopes)}, mean={mean:.6f}")

    # KW across sections
    section_order = sorted(section_slopes.keys())
    section_groups = [section_slopes[s] for s in section_order if len(section_slopes[s]) >= 3]
    section_labels = [s for s in section_order if len(section_slopes[s]) >= 3]

    if len(section_groups) < 2:
        print("  Insufficient section groups")
        return {'test': 'T4_SECTION_EFFECT', 'verdict': 'INSUFFICIENT_DATA'}

    kw_H, kw_p, kw_df = kruskal_wallis(section_groups)

    # Within-REGIME section effect (for those REGIMEs spanning multiple sections)
    within_regime_results = {}
    for regime in sorted(regime_section_slopes.keys()):
        sections = regime_section_slopes[regime]
        valid_secs = {s: slopes for s, slopes in sections.items() if len(slopes) >= 3}
        if len(valid_secs) >= 2:
            groups = [valid_secs[s] for s in sorted(valid_secs.keys())]
            r_H, r_p, r_df = kruskal_wallis(groups)
            within_regime_results[regime] = {
                'H': r_H, 'p': r_p, 'df': r_df,
                'sections': {s: {'n': len(slopes), 'mean': sum(slopes) / len(slopes)}
                             for s, slopes in valid_secs.items()},
            }
            print(f"  Within-{regime}: KW H={r_H:.3f}, p={r_p:.4f}")
            for s in sorted(valid_secs.keys()):
                m = sum(valid_secs[s]) / len(valid_secs[s])
                print(f"    {s}: n={len(valid_secs[s])}, mean={m:.6f}")

    # Verdict: section significant AND at least one within-REGIME test significant
    any_within_sig = any(r['p'] < 0.05 for r in within_regime_results.values())
    verdict = 'PASS' if kw_p < 0.05 and any_within_sig else ('PARTIAL' if kw_p < 0.05 else 'FAIL')

    print(f"  Overall KW: H={kw_H:.3f}, p={kw_p:.4f}")
    print(f"  Verdict: {verdict}")

    return {
        'test': 'T4_SECTION_EFFECT',
        'verdict': verdict,
        'kw_H': kw_H,
        'kw_p': kw_p,
        'section_means': {s: sum(slopes) / len(slopes) for s, slopes in section_slopes.items() if slopes},
        'section_n': {s: len(slopes) for s, slopes in section_slopes.items()},
        'within_regime': within_regime_results,
    }


# ── T5: Gradient Shape Taxonomy ───────────────────────────────────

def test_shape_taxonomy(folio_data, folio_gradients):
    """Test whether discrete gradient shapes exist."""
    print("\n=== T5: GRADIENT SHAPE TAXONOMY ===")

    # Collect 5-quintile AXM profiles (only folios with all 5 quintiles valid)
    profiles = []
    folio_order = []
    for folio, grad in sorted(folio_gradients.items()):
        profile = grad['profile']
        if all(v is not None for v in profile):
            profiles.append(profile)
            folio_order.append(folio)

    n = len(profiles)
    print(f"  Folios with complete 5-quintile profiles: {n}")

    if n < 10:
        print("  Insufficient data for clustering")
        return {'test': 'T5_SHAPE_TAXONOMY', 'verdict': 'INSUFFICIENT_DATA', 'n': n}

    # Try k=2,3,4
    best_sil = -1.0
    best_k = 2
    results_by_k = {}

    for k in [2, 3, 4]:
        if k >= n:
            continue
        labels, centroids, inertia = kmeans(profiles, k, seed=SEED)
        sil = silhouette_score(profiles, labels)
        results_by_k[k] = {
            'silhouette': sil,
            'inertia': inertia,
            'centroids': centroids,
            'cluster_sizes': Counter(labels),
        }
        print(f"  k={k}: silhouette={sil:.4f}, inertia={inertia:.4f}, "
              f"sizes={dict(Counter(labels))}")
        if sil > best_sil:
            best_sil = sil
            best_k = k

    # Describe best clustering
    best = results_by_k[best_k]
    print(f"\n  Best: k={best_k}, silhouette={best_sil:.4f}")
    for c_idx, centroid in enumerate(best['centroids']):
        slope = linear_slope(centroid)
        print(f"    Cluster {c_idx} (n={best['cluster_sizes'][c_idx]}): "
              f"profile=[{', '.join(f'{v:.3f}' for v in centroid)}], slope={slope:.5f}")

    if best_sil > 0.20:
        verdict = 'TAXONOMIC'
    elif best_sil > 0.15:
        verdict = 'WEAK_STRUCTURE'
    else:
        verdict = 'CONTINUOUS'

    print(f"  Verdict: {verdict}")

    return {
        'test': 'T5_SHAPE_TAXONOMY',
        'verdict': verdict,
        'n': n,
        'best_k': best_k,
        'best_silhouette': best_sil,
        'results_by_k': {str(k): {
            'silhouette': r['silhouette'],
            'inertia': r['inertia'],
            'centroids': r['centroids'],
            'cluster_sizes': {str(c): n for c, n in r['cluster_sizes'].items()},
        } for k, r in results_by_k.items()},
    }


# ── Main ──────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("Phase 475: GRADIENT_STEEPNESS")
    print("=" * 60)

    folio_data, token_to_class = load_data()

    t1_result, folio_gradients = test_gradient_variance(folio_data, token_to_class)
    t2_result = test_incremental_info(folio_data, folio_gradients)
    t3_result = test_regime_prediction(folio_data, folio_gradients)
    t4_result = test_section_effect(folio_data, folio_gradients)
    t5_result = test_shape_taxonomy(folio_data, folio_gradients)

    verdicts = [t1_result['verdict'], t2_result['verdict'], t3_result['verdict'],
                t4_result['verdict'], t5_result['verdict']]

    print(f"\n{'=' * 60}")
    print(f"VERDICTS: T1={verdicts[0]}, T2={verdicts[1]}, T3={verdicts[2]}, "
          f"T4={verdicts[3]}, T5={verdicts[4]}")

    if verdicts[0] == 'GATE_CLOSED':
        print("  T1 GATE CLOSED: gradient steepness is noise. T2-T5 results are unreliable.")
    elif verdicts[1] == 'GATE_CLOSED':
        print("  T2 GATE CLOSED: gradient steepness is a reformulation of C1168 boundary architecture.")

    results = {
        'phase': 'GRADIENT_STEEPNESS',
        'phase_number': 475,
        'tests': [t1_result, t2_result, t3_result, t4_result, t5_result],
        'verdicts': {f'T{i+1}': v for i, v in enumerate(verdicts)},
        'elapsed_seconds': round(time.time() - t0, 1),
    }

    out_path = RESULTS_DIR / 'gradient_steepness.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)
    print(f"\nResults written to {out_path}")
    print(f"Elapsed: {results['elapsed_seconds']}s")


if __name__ == '__main__':
    main()
