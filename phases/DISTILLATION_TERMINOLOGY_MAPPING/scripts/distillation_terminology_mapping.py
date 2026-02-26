"""Phase 461: DISTILLATION_TERMINOLOGY_MAPPING

Test whether distillation physics maps directly to the Voynich B manuscript.
Produces the authoritative Tier 3-4 mapping table (extending GLOSSING.md).

10 tests with negative controls:
  T1  Two-Channel Thermal Model (qo=heat source, ok=vessel temp)
  T2  Overshoot-Correct Cycling (qo-k -> ok-e transitions)
  T3  MIDPROCESS Action Mapping (13 modern actions -> token patterns)
  T4  REGIME Token Profile Variation (4 REGIMEs differ structurally)
  T5  Luting Discrimination (CONTAINMENT enriched in luting REGIMEs)
  T6  Cooling Mode Differentiation (e-compounds by REGIME)
  T7  Monitoring PREFIX x REGIME (ch/sh ratio varies by fire degree)
  T8  O-PREFIX Differentiation (ok/ot/ol/or are distinct)
  T9  Thermal Shock Prevention (monitoring enriched near thermal transitions)
  T10 Bang-Bang Rate by REGIME (alternation varies by fire degree)
"""

import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

# ============================================================
# CONSTANTS
# ============================================================
SEED = 42
N_PERM = 10_000
RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']


# ============================================================
# STATISTICAL UTILITIES (pure Python, no scipy dependency)
# ============================================================

def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def std(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def normal_cdf(x):
    """Standard normal CDF (Abramowitz & Stegun)."""
    if x < -8:
        return 0.0
    if x > 8:
        return 1.0
    t = 1 / (1 + 0.2316419 * abs(x))
    d = 0.3989422804014327
    p = d * math.exp(-x * x / 2) * t * (0.319381530 + t * (-0.356563782 +
        t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
    return p if x < 0 else 1 - p


def _rank(combined):
    """Assign average ranks to sorted (value, group) tuples."""
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2
        for idx in range(i, j):
            ranks[idx] = avg_rank
        i = j
    return ranks


def mann_whitney_u(xs, ys):
    """Mann-Whitney U with normal approximation. Returns U, z, p (two-sided)."""
    n1, n2 = len(xs), len(ys)
    if n1 == 0 or n2 == 0:
        return 0, 0, 1.0
    combined = [(v, 0) for v in xs] + [(v, 1) for v in ys]
    combined.sort(key=lambda x: x[0])
    ranks = _rank(combined)
    R1 = sum(ranks[i] for i in range(len(combined)) if combined[i][1] == 0)
    U1 = R1 - n1 * (n1 + 1) / 2
    U = min(U1, n1 * n2 - U1)
    mu = n1 * n2 / 2
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    if sigma == 0:
        return U, 0, 1.0
    z = (U - mu) / sigma
    p = 2 * normal_cdf(-abs(z))
    return U, z, p


def kruskal_wallis(groups):
    """Kruskal-Wallis H test. Returns H, p."""
    all_vals = []
    for i, g in enumerate(groups):
        for v in g:
            all_vals.append((v, i))
    N = len(all_vals)
    if N == 0:
        return 0, 1.0
    all_vals.sort(key=lambda x: x[0])
    ranks = _rank(all_vals)
    rsums = defaultdict(float)
    gsizes = defaultdict(int)
    for idx, (_, gid) in enumerate(all_vals):
        rsums[gid] += ranks[idx]
        gsizes[gid] += 1
    H = sum(R ** 2 / gsizes[gid] for gid, R in rsums.items())
    H = (12 / (N * (N + 1))) * H - 3 * (N + 1)
    df = len(groups) - 1
    p = chi2_sf(H, df) if df > 0 else 1.0
    return H, p


def chi2_sf(x, df):
    """Chi-square survival function (p-value) via Wilson-Hilferty approximation."""
    if x <= 0 or df <= 0:
        return 1.0
    if df == 1:
        return 2 * normal_cdf(-math.sqrt(x))
    if df == 2:
        return math.exp(-x / 2)
    # Wilson-Hilferty normal approximation (accurate for df >= 3)
    z = ((x / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    return 1.0 - normal_cdf(z)


def chi_square_test(observed):
    """Chi-square for NxM contingency table. Returns chi2, p, df."""
    nrows = len(observed)
    ncols = len(observed[0]) if nrows > 0 else 0
    if nrows < 2 or ncols < 2:
        return 0, 1.0, 0
    row_sums = [sum(row) for row in observed]
    col_sums = [sum(observed[r][c] for r in range(nrows)) for c in range(ncols)]
    total = sum(row_sums)
    if total == 0:
        return 0, 1.0, 0
    chi2 = 0.0
    for r in range(nrows):
        for c in range(ncols):
            expected = row_sums[r] * col_sums[c] / total
            if expected > 0:
                chi2 += (observed[r][c] - expected) ** 2 / expected
    df = (nrows - 1) * (ncols - 1)
    p = chi2_sf(chi2, df)
    return chi2, p, df


def cohens_d(xs, ys):
    """Cohen's d effect size."""
    n1, n2 = len(xs), len(ys)
    if n1 < 2 or n2 < 2:
        return 0.0
    m1, m2 = mean(xs), mean(ys)
    s1, s2 = std(xs), std(ys)
    pooled = math.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))
    return (m1 - m2) / pooled if pooled > 0 else 0.0


def cosine_distance(v1, v2):
    """Cosine distance between two dicts treated as sparse vectors."""
    keys = set(v1) | set(v2)
    dot = sum(v1.get(k, 0) * v2.get(k, 0) for k in keys)
    n1 = math.sqrt(sum(v1.get(k, 0) ** 2 for k in keys))
    n2 = math.sqrt(sum(v2.get(k, 0) ** 2 for k in keys))
    if n1 == 0 or n2 == 0:
        return 1.0
    return 1.0 - dot / (n1 * n2)


def permutation_p(observed_stat, null_stats):
    """Fraction of null stats >= observed (one-tailed)."""
    return sum(1 for ns in null_stats if ns >= observed_stat) / len(null_stats)


# ============================================================
# PRE-COMPUTATION
# ============================================================

def load_data():
    """Load transcript, morphology, categories, regime assignments."""
    print("Loading data...")
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    with open(PROJECT_ROOT / 'data' / 'regime_folio_mapping.json', 'r', encoding='utf-8') as f:
        regime_data = json.load(f)
    folio_to_regime = {f: info['regime']
                       for f, info in regime_data.get('regime_assignments', {}).items()}

    # Process B tokens
    b_tokens = []
    line_groups = defaultdict(list)
    folio_groups = defaultdict(list)
    prefix_groups = defaultdict(list)
    regime_folio_groups = defaultdict(lambda: defaultdict(list))

    for t in tx.currier_b():
        m = morph.extract(t.word)
        cat = cc.classify(m.middle) if m.middle else None
        regime = folio_to_regime.get(t.folio)
        mid = m.middle or ''
        n = len(mid)
        ti = {
            'word': t.word, 'folio': t.folio, 'line': t.line,
            'section': t.section, 'prefix': m.prefix,
            'middle': mid, 'suffix': m.suffix,
            'category': cat, 'regime': regime,
            'k_frac': mid.count('k') / n if n else 0.0,
            'e_frac': mid.count('e') / n if n else 0.0,
            'h_frac': mid.count('h') / n if n else 0.0,
            'i_frac': mid.count('i') / n if n else 0.0,
            'line_initial': t.line_initial, 'line_final': t.line_final,
        }
        b_tokens.append(ti)
        line_groups[(t.folio, t.line)].append(ti)
        folio_groups[t.folio].append(ti)
        if m.prefix:
            prefix_groups[m.prefix].append(ti)
        if regime:
            regime_folio_groups[regime][t.folio].append(ti)

    # Compute normalized line positions
    for tokens in line_groups.values():
        n = len(tokens)
        for i, ti in enumerate(tokens):
            ti['line_pos'] = i / (n - 1) if n > 1 else 0.5

    # Process A tokens for negative controls
    a_tokens = []
    a_folio_groups = defaultdict(list)
    for t in tx.currier_a():
        m = morph.extract(t.word)
        cat = cc.classify(m.middle) if m.middle else None
        regime = folio_to_regime.get(t.folio)
        mid = m.middle or ''
        n = len(mid)
        ti = {
            'word': t.word, 'folio': t.folio, 'prefix': m.prefix,
            'middle': mid, 'suffix': m.suffix, 'category': cat,
            'regime': regime,
            'k_frac': mid.count('k') / n if n else 0.0,
            'e_frac': mid.count('e') / n if n else 0.0,
            'h_frac': mid.count('h') / n if n else 0.0,
        }
        a_tokens.append(ti)
        a_folio_groups[t.folio].append(ti)

    print(f"  B tokens: {len(b_tokens)}")
    print(f"  A tokens: {len(a_tokens)}")
    print(f"  B folios: {len(folio_groups)}")
    print(f"  Prefixes: {sorted(prefix_groups.keys())[:10]}...")
    print(f"  REGIMEs:  { {r: len(fs) for r, fs in regime_folio_groups.items()} }")

    return {
        'b_tokens': b_tokens, 'a_tokens': a_tokens,
        'line_groups': dict(line_groups),
        'folio_groups': dict(folio_groups),
        'a_folio_groups': dict(a_folio_groups),
        'prefix_groups': dict(prefix_groups),
        'regime_folio_groups': {r: dict(v) for r, v in regime_folio_groups.items()},
        'folio_to_regime': folio_to_regime,
        'cc': cc,
    }


# ============================================================
# T1: Two-Channel Thermal Model
# ============================================================

def test_t1(data):
    """qo is k-enriched (heat source), ok is e-enriched (vessel temp).
    Negative control: sa shows no thermal bias."""
    print("\n=== T1: Two-Channel Thermal Model ===")
    pg = data['prefix_groups']
    qo = pg.get('qo', [])
    ok = pg.get('ok', [])
    sa = pg.get('sa', [])

    qo_k = [t['k_frac'] for t in qo]
    ok_k = [t['k_frac'] for t in ok]
    qo_e = [t['e_frac'] for t in qo]
    ok_e = [t['e_frac'] for t in ok]
    sa_k = [t['k_frac'] for t in sa]
    sa_e = [t['e_frac'] for t in sa]

    # Mann-Whitney: qo k-frac > ok k-frac
    U_k, z_k, p_k = mann_whitney_u(qo_k, ok_k)
    # Mann-Whitney: ok e-frac > qo e-frac
    U_e, z_e, p_e = mann_whitney_u(ok_e, qo_e)
    # Negative control: sa should NOT show k-vs-e differentiation like qo/ok do
    # Compare sa's own k-frac vs e-frac (should be indistinguishable)
    U_sa, _, p_sa = mann_whitney_u(sa_k, sa_e)

    # Permutation test: shuffle qo/ok labels
    rng = random.Random(SEED)
    combined_k = qo_k + ok_k
    n_qo = len(qo_k)
    obs_diff_k = mean(qo_k) - mean(ok_k)
    obs_diff_e = mean(ok_e) - mean(qo_e)
    perm_diffs_k = []
    perm_diffs_e = []
    combined_e = qo_e + ok_e
    for _ in range(N_PERM):
        idx = list(range(len(combined_k)))
        rng.shuffle(idx)
        g1_k = [combined_k[i] for i in idx[:n_qo]]
        g2_k = [combined_k[i] for i in idx[n_qo:]]
        g1_e = [combined_e[i] for i in idx[:n_qo]]
        g2_e = [combined_e[i] for i in idx[n_qo:]]
        perm_diffs_k.append(mean(g1_k) - mean(g2_k))
        perm_diffs_e.append(mean(g2_e) - mean(g1_e))
    perm_p_k = permutation_p(obs_diff_k, perm_diffs_k)
    perm_p_e = permutation_p(obs_diff_e, perm_diffs_e)

    # Cross-validate against F-B-006
    qo_k_mean = mean(qo_k)
    ok_e_mean = mean(ok_e)

    passed = p_k < 0.001 and p_e < 0.001 and perm_p_k < 0.01 and perm_p_e < 0.01
    sa_neutral = p_sa > 0.05  # sa k-frac vs sa e-frac should be indistinguishable

    result = {
        'test': 'T1: Two-Channel Thermal Model',
        'tier': 'Structural=T2, Interpretation=T3-4',
        'passed': passed,
        'qo_count': len(qo), 'ok_count': len(ok), 'sa_count': len(sa),
        'qo_k_mean': round(qo_k_mean, 4), 'ok_k_mean': round(mean(ok_k), 4),
        'qo_e_mean': round(mean(qo_e), 4), 'ok_e_mean': round(ok_e_mean, 4),
        'sa_k_mean': round(mean(sa_k), 4), 'sa_e_mean': round(mean(sa_e), 4),
        'mw_k_p': round(p_k, 6), 'mw_e_p': round(p_e, 6),
        'perm_k_p': round(perm_p_k, 6), 'perm_e_p': round(perm_p_e, 6),
        'neg_ctrl_sa_kve_p': round(p_sa, 6), 'neg_ctrl_sa_neutral': sa_neutral,
        'f_b_006_crossval': f"qo k={qo_k_mean:.3f} (expect ~0.707), ok e={ok_e_mean:.3f} (expect ~0.687)",
    }
    print(f"  qo k-frac: {qo_k_mean:.3f}  ok k-frac: {mean(ok_k):.3f}  MW p={p_k:.2e}")
    print(f"  ok e-frac: {ok_e_mean:.3f}  qo e-frac: {mean(qo_e):.3f}  MW p={p_e:.2e}")
    print(f"  Permutation: k p={perm_p_k:.4f}, e p={perm_p_e:.4f}")
    print(f"  sa neg ctrl (k vs e): p={p_sa:.4f} neutral={sa_neutral}")
    print(f"  PASS: {passed}")
    return result


# ============================================================
# T2: Overshoot-Correct Cycling
# ============================================================

def test_t2(data):
    """Within lines, qo-k -> ok-e transitions exceed chance."""
    print("\n=== T2: Overshoot-Correct Cycling ===")
    line_groups = data['line_groups']

    def is_qo_k(ti):
        return ti['prefix'] == 'qo' and ti['k_frac'] > 0

    def is_ok_e(ti):
        return ti['prefix'] == 'ok' and ti['e_frac'] > 0

    # Count real transitions
    qo_k_to_ok_e = 0
    ok_e_to_qo_k = 0
    total_bigrams = 0
    for tokens in line_groups.values():
        for i in range(len(tokens) - 1):
            total_bigrams += 1
            if is_qo_k(tokens[i]) and is_ok_e(tokens[i + 1]):
                qo_k_to_ok_e += 1
            if is_ok_e(tokens[i]) and is_qo_k(tokens[i + 1]):
                ok_e_to_qo_k += 1

    # Permutation null: shuffle within each line
    rng = random.Random(SEED)
    null_fwd = []
    null_rev = []
    for _ in range(N_PERM):
        fwd, rev = 0, 0
        for tokens in line_groups.values():
            shuffled = list(tokens)
            rng.shuffle(shuffled)
            for i in range(len(shuffled) - 1):
                if is_qo_k(shuffled[i]) and is_ok_e(shuffled[i + 1]):
                    fwd += 1
                if is_ok_e(shuffled[i]) and is_qo_k(shuffled[i + 1]):
                    rev += 1
        null_fwd.append(fwd)
        null_rev.append(rev)

    p_fwd = permutation_p(qo_k_to_ok_e, null_fwd)
    p_rev = permutation_p(ok_e_to_qo_k, null_rev)

    # Negative control: da -> sa transitions (should be at chance)
    def is_da(ti):
        return ti['prefix'] == 'da'
    def is_sa(ti):
        return ti['prefix'] == 'sa'

    da_to_sa = 0
    for tokens in line_groups.values():
        for i in range(len(tokens) - 1):
            if is_da(tokens[i]) and is_sa(tokens[i + 1]):
                da_to_sa += 1
    null_ctrl = []
    rng2 = random.Random(SEED + 1)
    for _ in range(N_PERM):
        ct = 0
        for tokens in line_groups.values():
            shuffled = list(tokens)
            rng2.shuffle(shuffled)
            for i in range(len(shuffled) - 1):
                if is_da(shuffled[i]) and is_sa(shuffled[i + 1]):
                    ct += 1
        null_ctrl.append(ct)
    p_ctrl = permutation_p(da_to_sa, null_ctrl)

    passed = p_fwd < 0.01 and p_rev < 0.01
    null_mean_fwd = mean(null_fwd) if null_fwd else 0
    null_mean_rev = mean(null_rev) if null_rev else 0

    result = {
        'test': 'T2: Overshoot-Correct Cycling',
        'tier': 'Structural=T2, Interpretation=T3-4',
        'passed': passed,
        'qo_k_to_ok_e': qo_k_to_ok_e, 'null_mean_fwd': round(null_mean_fwd, 1),
        'ok_e_to_qo_k': ok_e_to_qo_k, 'null_mean_rev': round(null_mean_rev, 1),
        'total_bigrams': total_bigrams,
        'p_forward': round(p_fwd, 6), 'p_reverse': round(p_rev, 6),
        'neg_ctrl_da_sa': da_to_sa, 'neg_ctrl_p': round(p_ctrl, 4),
    }
    print(f"  qo-k -> ok-e: {qo_k_to_ok_e} (null mean: {null_mean_fwd:.1f}, p={p_fwd:.4f})")
    print(f"  ok-e -> qo-k: {ok_e_to_qo_k} (null mean: {null_mean_rev:.1f}, p={p_rev:.4f})")
    print(f"  Neg ctrl da->sa: {da_to_sa} (p={p_ctrl:.4f})")
    print(f"  PASS: {passed}")
    return result


# ============================================================
# T3: MIDPROCESS Action Mapping
# ============================================================

def test_t3(data):
    """13 MIDPROCESS actions map to specific PREFIX+category patterns."""
    print("\n=== T3: MIDPROCESS Action Mapping ===")
    b_tokens = data['b_tokens']

    # Define 13 action -> token filter
    def make_filter(prefix_set=None, cat_set=None, middle_contains=None,
                    suffix_set=None, line_final=None, cat_exclude=None):
        def f(ti):
            if prefix_set and ti['prefix'] not in prefix_set:
                return False
            if cat_set and ti['category'] not in cat_set:
                return False
            if cat_exclude and ti['category'] in cat_exclude:
                return False
            if middle_contains and middle_contains not in ti['middle']:
                return False
            if suffix_set and ti['suffix'] not in suffix_set:
                return False
            if line_final is not None and ti.get('line_final') != line_final:
                return False
            return True
        return f

    actions = {
        'MONITOR_TEMP': make_filter(prefix_set={'ch', 'sh'}, cat_set={'THERMAL'}),
        'MONITOR_RATE': make_filter(prefix_set={'ch', 'sh'}, suffix_set={'aiin', 'ain'}),
        'MONITOR_VISUAL': make_filter(prefix_set={'sh'}, cat_exclude={'THERMAL'}),
        'ADJUST_HEAT': make_filter(prefix_set={'qo'}, middle_contains='k'),
        'COOL_CONDENSER': make_filter(prefix_set={'ok'}, middle_contains='e'),
        'REPLENISH_WATER': make_filter(prefix_set={'da'}, cat_set={'FLOW'}),
        'DETECT_ENDPOINT': make_filter(suffix_set={'am', 'y'}, line_final=True),
        'COLLECT_FRACTION': make_filter(prefix_set={'ol'}, cat_set={'FLOW'}),
        'COHOBATE': make_filter(prefix_set={'da'}, middle_contains='i'),
        'MANAGE_PRESSURE': make_filter(cat_set={'CONTAINMENT'}),
        'AGITATE': make_filter(prefix_set={'ch'}, cat_set={'OPERATION'}),
        'SEAL_JOINTS': make_filter(prefix_set={'ok'}, middle_contains='d'),
        'DETECT_CHANNELING': make_filter(prefix_set={'ct'}),
    }

    # Compute matches and category profiles for each action
    action_profiles = {}
    action_counts = {}
    for name, filt in actions.items():
        matches = [t for t in b_tokens if filt(t)]
        action_counts[name] = len(matches)
        profile = Counter(t['category'] for t in matches if t['category'])
        total = sum(profile.values())
        action_profiles[name] = {c: profile.get(c, 0) / total if total > 0 else 0
                                  for c in CATEGORIES}

    # Pairwise cosine distances
    action_names = list(actions.keys())
    distances = []
    for i in range(len(action_names)):
        for j in range(i + 1, len(action_names)):
            d = cosine_distance(action_profiles[action_names[i]],
                                action_profiles[action_names[j]])
            distances.append(d)
    mean_distance = mean(distances) if distances else 0

    # Enrichment chi-square per action
    total_b = len(b_tokens)
    enrichment_results = {}
    significant_count = 0
    bonferroni = 0.005  # 0.05/13 ~ 0.004, using 0.005
    for name, filt in actions.items():
        matches = [t for t in b_tokens if filt(t)]
        non_matches = [t for t in b_tokens if not filt(t)]
        if not matches:
            enrichment_results[name] = {'count': 0, 'chi2': 0, 'p': 1.0, 'significant': False}
            continue
        # Category distribution: matches vs non-matches
        m_cats = Counter(t['category'] for t in matches if t['category'])
        nm_cats = Counter(t['category'] for t in non_matches if t['category'])
        table = [[m_cats.get(c, 0) for c in CATEGORIES],
                 [nm_cats.get(c, 0) for c in CATEGORIES]]
        chi2, p, df = chi_square_test(table)
        sig = p < bonferroni
        if sig:
            significant_count += 1
        enrichment_results[name] = {
            'count': len(matches), 'chi2': round(chi2, 2),
            'p': round(p, 6), 'significant': sig,
        }

    # Negative control: random groups
    rng = random.Random(SEED)
    null_distances = []
    for _ in range(1000):
        rng.shuffle(b_tokens)
        chunk_size = len(b_tokens) // 13
        rand_profiles = {}
        for k in range(13):
            chunk = b_tokens[k * chunk_size:(k + 1) * chunk_size]
            cat_counts = Counter(t['category'] for t in chunk if t['category'])
            total = sum(cat_counts.values())
            rand_profiles[k] = {c: cat_counts.get(c, 0) / total if total > 0 else 0
                                 for c in CATEGORIES}
        dists = []
        for i in range(13):
            for j in range(i + 1, 13):
                dists.append(cosine_distance(rand_profiles[i], rand_profiles[j]))
        null_distances.append(mean(dists))
    p_discrim = permutation_p(mean_distance, null_distances)

    passed = significant_count >= 10 and mean_distance > 0.3 and p_discrim < 0.001

    result = {
        'test': 'T3: MIDPROCESS Action Mapping',
        'tier': 'Tier 3-4 (intentionally interpretive)',
        'passed': passed,
        'significant_actions': significant_count,
        'total_actions': 13,
        'mean_cosine_distance': round(mean_distance, 4),
        'random_mean_distance': round(mean(null_distances), 4),
        'p_discriminability': round(p_discrim, 6),
        'action_counts': action_counts,
        'enrichment': enrichment_results,
        'action_profiles': {k: {c: round(v, 3) for c, v in p.items()}
                            for k, p in action_profiles.items()},
    }
    print(f"  Significant actions: {significant_count}/13 (Bonferroni p<{bonferroni})")
    print(f"  Mean cosine distance: {mean_distance:.4f} (random: {mean(null_distances):.4f})")
    print(f"  Discriminability p: {p_discrim:.6f}")
    print(f"  Action counts: {action_counts}")
    print(f"  PASS: {passed}")
    return result


# ============================================================
# T4: REGIME Token Profile Variation
# ============================================================

def test_t4(data):
    """4 REGIMEs produce different token profiles."""
    print("\n=== T4: REGIME Token Profile Variation ===")
    rfg = data['regime_folio_groups']
    regimes = sorted(rfg.keys())

    def folio_metric(tokens, metric):
        """Compute a metric across a folio's tokens."""
        if metric == 'k_frac':
            return mean([t['k_frac'] for t in tokens])
        elif metric == 'e_frac':
            return mean([t['e_frac'] for t in tokens])
        elif metric == 'h_frac':
            return mean([t['h_frac'] for t in tokens])
        elif metric == 'THERMAL_rate':
            n = sum(1 for t in tokens if t['category'] == 'THERMAL')
            return n / len(tokens) if tokens else 0
        elif metric == 'MONITORING_rate':
            n = sum(1 for t in tokens if t['category'] == 'MONITORING')
            return n / len(tokens) if tokens else 0
        elif metric == 'CONTAINMENT_rate':
            n = sum(1 for t in tokens if t['category'] == 'CONTAINMENT')
            return n / len(tokens) if tokens else 0
        elif metric == 'mean_line_length':
            lines = defaultdict(int)
            for t in tokens:
                lines[t['line']] += 1
            return mean(list(lines.values())) if lines else 0

    metrics = ['k_frac', 'e_frac', 'h_frac', 'THERMAL_rate',
               'MONITORING_rate', 'CONTAINMENT_rate', 'mean_line_length']

    kw_results = {}
    significant_count = 0
    for metric in metrics:
        groups = []
        for r in regimes:
            folio_vals = []
            for fol, tokens in rfg[r].items():
                if len(tokens) >= 5:
                    folio_vals.append(folio_metric(tokens, metric))
            groups.append(folio_vals)
        H, p = kruskal_wallis(groups)
        sig = p < 0.01
        if sig:
            significant_count += 1
        regime_means = {r: round(mean(g), 4) for r, g in zip(regimes, groups) if g}
        kw_results[metric] = {
            'H': round(H, 2), 'p': round(p, 6), 'significant': sig,
            'regime_means': regime_means,
        }

    # Negative control: same metrics on A tokens
    afg = data['a_folio_groups']
    ft = data['folio_to_regime']
    a_regime_folio = defaultdict(lambda: defaultdict(list))
    for fol, tokens in afg.items():
        r = ft.get(fol)
        if r:
            a_regime_folio[r][fol] = tokens

    a_sig_count = 0
    a_kw_results = {}
    for metric in metrics:
        groups = []
        for r in regimes:
            folio_vals = []
            for fol, tokens in a_regime_folio.get(r, {}).items():
                if len(tokens) >= 5:
                    folio_vals.append(folio_metric(tokens, metric))
            groups.append(folio_vals)
        H, p = kruskal_wallis(groups)
        if p < 0.01:
            a_sig_count += 1
        a_kw_results[metric] = {'H': round(H, 2), 'p': round(p, 6)}

    passed = significant_count >= 4
    stronger_than_a = significant_count > a_sig_count

    result = {
        'test': 'T4: REGIME Token Profile Variation',
        'tier': 'Structural=T2, Brunschwig alignment=T3-4',
        'passed': passed,
        'significant_metrics_b': significant_count,
        'significant_metrics_a': a_sig_count,
        'stronger_than_a': stronger_than_a,
        'b_results': kw_results,
        'a_neg_ctrl': a_kw_results,
    }
    print(f"  B significant: {significant_count}/7 metrics (need 4+)")
    print(f"  A neg ctrl significant: {a_sig_count}/7")
    for metric, r in kw_results.items():
        s = "*" if r['significant'] else " "
        print(f"    {s} {metric}: H={r['H']:.1f} p={r['p']:.4f} {r['regime_means']}")
    print(f"  PASS: {passed}")
    return result


# ============================================================
# T5: Luting Discrimination
# ============================================================

def test_t5(data):
    """CONTAINMENT enriched in REGIMEs requiring luting (R3) vs balneum (R1)."""
    print("\n=== T5: Luting Discrimination ===")
    rfg = data['regime_folio_groups']

    def folio_cat_rate(tokens, cat):
        cats = [t['category'] for t in tokens if t['category']]
        return sum(1 for c in cats if c == cat) / len(cats) if cats else 0

    r1_rates = [folio_cat_rate(toks, 'CONTAINMENT')
                for fol, toks in rfg.get('REGIME_1', {}).items() if len(toks) >= 5]
    r3_rates = [folio_cat_rate(toks, 'CONTAINMENT')
                for fol, toks in rfg.get('REGIME_3', {}).items() if len(toks) >= 5]

    U, z, p_cat = mann_whitney_u(r3_rates, r1_rates)
    d_cat = cohens_d(r3_rates, r1_rates)

    # Also test specific MIDDLE: dy (seal/close) — more targeted than full category
    def folio_dy_rate(tokens):
        mids = [t['middle'] for t in tokens if t['middle']]
        return sum(1 for m in mids if 'dy' in m) / len(mids) if mids else 0

    r1_dy = [folio_dy_rate(toks)
             for fol, toks in rfg.get('REGIME_1', {}).items() if len(toks) >= 5]
    r3_dy = [folio_dy_rate(toks)
             for fol, toks in rfg.get('REGIME_3', {}).items() if len(toks) >= 5]
    _, _, p_dy = mann_whitney_u(r3_dy, r1_dy)
    d_dy = cohens_d(r3_dy, r1_dy)

    # Negative control: OPERATION rate should NOT discriminate by REGIME
    r1_op = [folio_cat_rate(toks, 'OPERATION')
             for fol, toks in rfg.get('REGIME_1', {}).items() if len(toks) >= 5]
    r3_op = [folio_cat_rate(toks, 'OPERATION')
             for fol, toks in rfg.get('REGIME_3', {}).items() if len(toks) >= 5]
    _, _, p_op = mann_whitney_u(r3_op, r1_op)

    # Pass if either CONTAINMENT category or dy MIDDLE discriminates
    passed = (p_cat < 0.05 and abs(d_cat) > 0.3) or (p_dy < 0.05 and abs(d_dy) > 0.3)

    result = {
        'test': 'T5: Luting Discrimination',
        'tier': 'Structural=T2, Brunschwig=T3-4',
        'passed': passed,
        'R1_containment_mean': round(mean(r1_rates), 4),
        'R3_containment_mean': round(mean(r3_rates), 4),
        'containment_mw_p': round(p_cat, 6), 'containment_d': round(d_cat, 3),
        'R1_dy_mean': round(mean(r1_dy), 4), 'R3_dy_mean': round(mean(r3_dy), 4),
        'dy_mw_p': round(p_dy, 6), 'dy_d': round(d_dy, 3),
        'R1_n_folios': len(r1_rates), 'R3_n_folios': len(r3_rates),
        'neg_ctrl_operation_p': round(p_op, 6),
    }
    print(f"  R1 CONTAINMENT: {mean(r1_rates):.4f}, R3: {mean(r3_rates):.4f} (p={p_cat:.4f} d={d_cat:.3f})")
    print(f"  R1 dy-rate: {mean(r1_dy):.4f}, R3: {mean(r3_dy):.4f} (p={p_dy:.4f} d={d_dy:.3f})")
    print(f"  Neg ctrl OPERATION p={p_op:.4f}")
    print(f"  PASS: {passed}")
    return result


# ============================================================
# T6: Cooling Mode Differentiation
# ============================================================

def test_t6(data):
    """Different e-compound MIDDLEs vary by REGIME (cooling modes)."""
    print("\n=== T6: Cooling Mode Differentiation ===")
    rfg = data['regime_folio_groups']
    regimes = sorted(rfg.keys())

    # e-compound categories
    e_compounds = {
        'e_basic': lambda m: m == 'e',
        'eo_active': lambda m: m in ('eo', 'eol'),
        'ee_extended': lambda m: m in ('eey', 'eeol', 'ee', 'eeo'),
    }

    # Count per regime
    regime_e_counts = {r: {ec: 0 for ec in e_compounds} for r in regimes}
    for r in regimes:
        for fol, tokens in rfg[r].items():
            for t in tokens:
                mid = t['middle']
                for ec_name, ec_fn in e_compounds.items():
                    if ec_fn(mid):
                        regime_e_counts[r][ec_name] += 1

    # Build contingency table: regimes x e-compounds
    table = []
    for r in regimes:
        row = [regime_e_counts[r][ec] for ec in e_compounds]
        table.append(row)
    chi2, p, df = chi_square_test(table)

    # Specific prediction: eeol enriched in R1
    r1_eeol = sum(1 for t in data['b_tokens']
                  if t['regime'] == 'REGIME_1' and t['middle'] in ('eeol',))
    total_eeol = sum(1 for t in data['b_tokens'] if t['middle'] in ('eeol',))
    r1_total = sum(1 for t in data['b_tokens'] if t['regime'] == 'REGIME_1')
    total_b = len(data['b_tokens'])
    eeol_r1_rate = r1_eeol / r1_total if r1_total > 0 else 0
    eeol_overall_rate = total_eeol / total_b if total_b > 0 else 0
    eeol_enrichment = eeol_r1_rate / eeol_overall_rate if eeol_overall_rate > 0 else 0

    # Count specific predictions confirmed
    predictions_confirmed = 0
    # Prediction 1: ee_extended enriched in R1
    r1_ext = regime_e_counts.get('REGIME_1', {}).get('ee_extended', 0)
    r3_ext = regime_e_counts.get('REGIME_3', {}).get('ee_extended', 0)
    if r1_ext > r3_ext:
        predictions_confirmed += 1
    # Prediction 2: eo_active enriched in R3 (active cooling needed for direct fire)
    r1_act = regime_e_counts.get('REGIME_1', {}).get('eo_active', 0)
    r3_act = regime_e_counts.get('REGIME_3', {}).get('eo_active', 0)
    if r3_act > r1_act:
        predictions_confirmed += 1
    # Prediction 3: e_basic enriched in R3 (quick cool-down for direct fire)
    r1_bas = regime_e_counts.get('REGIME_1', {}).get('e_basic', 0)
    r3_bas = regime_e_counts.get('REGIME_3', {}).get('e_basic', 0)
    if r3_bas > r1_bas:
        predictions_confirmed += 1

    passed = p < 0.01 and predictions_confirmed >= 2

    result = {
        'test': 'T6: Cooling Mode Differentiation',
        'tier': 'Tier 3-4',
        'passed': passed,
        'chi2': round(chi2, 2), 'p': round(p, 6), 'df': df,
        'regime_e_counts': regime_e_counts,
        'predictions_confirmed': predictions_confirmed,
        'eeol_R1_enrichment': round(eeol_enrichment, 2),
    }
    print(f"  Chi-square: {chi2:.2f}, p={p:.4f}, df={df}")
    print(f"  Regime x e-compound counts: {regime_e_counts}")
    print(f"  Predictions confirmed: {predictions_confirmed}/3")
    print(f"  eeol R1 enrichment: {eeol_enrichment:.2f}x")
    print(f"  PASS: {passed}")
    return result


# ============================================================
# T7: Monitoring PREFIX x REGIME Interaction
# ============================================================

def test_t7(data):
    """ch/sh ratio varies by REGIME (different monitoring for different fire degrees)."""
    print("\n=== T7: Monitoring PREFIX x REGIME ===")
    rfg = data['regime_folio_groups']
    regimes = sorted(rfg.keys())

    def folio_ch_sh_ratio(tokens):
        ch = sum(1 for t in tokens if t['prefix'] == 'ch')
        sh = sum(1 for t in tokens if t['prefix'] == 'sh')
        total = ch + sh
        return ch / total if total > 0 else None

    ratio_groups = []
    for r in regimes:
        vals = []
        for fol, tokens in rfg[r].items():
            ratio = folio_ch_sh_ratio(tokens)
            if ratio is not None:
                vals.append(ratio)
        ratio_groups.append(vals)

    H, p = kruskal_wallis(ratio_groups)

    # 4 directional predictions (need 2/4 per plan)
    r_means = {r: round(mean(g), 4) for r, g in zip(regimes, ratio_groups) if g}
    predictions_confirmed = 0
    r1_mean = mean(ratio_groups[regimes.index('REGIME_1')]) if 'REGIME_1' in regimes else 0.5
    r2_mean = mean(ratio_groups[regimes.index('REGIME_2')]) if 'REGIME_2' in regimes else 0.5
    r3_mean = mean(ratio_groups[regimes.index('REGIME_3')]) if 'REGIME_3' in regimes else 0.5
    r4_mean = mean(ratio_groups[regimes.index('REGIME_4')]) if 'REGIME_4' in regimes else 0.5
    # P1: R3 highest ch/sh (most active testing for direct fire)
    if r3_mean >= max(r1_mean, r2_mean, r4_mean):
        predictions_confirmed += 1
    # P2: R1 lowest ch/sh (least active testing for gentle heat)
    if r1_mean <= min(r2_mean, r3_mean, r4_mean):
        predictions_confirmed += 1
    # P3: R3 > R1
    if r3_mean > r1_mean:
        predictions_confirmed += 1
    # P4: R4 > R2 (precision needs more testing than sustained)
    if r4_mean > r2_mean:
        predictions_confirmed += 1

    # Negative control: da/sa ratio should NOT vary by REGIME
    def folio_da_sa_ratio(tokens):
        da = sum(1 for t in tokens if t['prefix'] == 'da')
        sa = sum(1 for t in tokens if t['prefix'] == 'sa')
        total = da + sa
        return da / total if total > 0 else None

    ctrl_groups = []
    for r in regimes:
        vals = []
        for fol, tokens in rfg[r].items():
            ratio = folio_da_sa_ratio(tokens)
            if ratio is not None:
                vals.append(ratio)
        ctrl_groups.append(vals)
    H_ctrl, p_ctrl = kruskal_wallis(ctrl_groups)

    passed = p < 0.05 and predictions_confirmed >= 2

    result = {
        'test': 'T7: Monitoring PREFIX x REGIME',
        'tier': 'Structural=T2, Interpretation=T3-4',
        'passed': passed,
        'kw_H': round(H, 2), 'kw_p': round(p, 6),
        'regime_ch_sh_means': r_means,
        'predictions_confirmed': predictions_confirmed,
        'neg_ctrl_da_sa_H': round(H_ctrl, 2), 'neg_ctrl_da_sa_p': round(p_ctrl, 4),
    }
    print(f"  KW H={H:.2f}, p={p:.4f}")
    print(f"  ch/sh ratio by REGIME: {r_means}")
    print(f"  Predictions confirmed: {predictions_confirmed}/4")
    print(f"  Neg ctrl da/sa: H={H_ctrl:.2f} p={p_ctrl:.4f}")
    print(f"  PASS: {passed}")
    return result


# ============================================================
# T8: O-PREFIX Differentiation
# ============================================================

def test_t8(data):
    """ok, ot, ol, or have distinct category and suffix profiles."""
    print("\n=== T8: O-PREFIX Differentiation ===")
    pg = data['prefix_groups']
    o_prefixes = ['ok', 'ot', 'ol', 'or']

    # Category contingency table (4 prefixes x 8 categories)
    table = []
    for pf in o_prefixes:
        tokens = pg.get(pf, [])
        row = [sum(1 for t in tokens if t['category'] == c) for c in CATEGORIES]
        table.append(row)
    chi2, p, df = chi_square_test(table)

    # Dominant category per prefix
    dominants = {}
    for pf in o_prefixes:
        tokens = pg.get(pf, [])
        cats = Counter(t['category'] for t in tokens if t['category'])
        if cats:
            dominants[pf] = cats.most_common(1)[0]
        else:
            dominants[pf] = (None, 0)

    # Suffix distribution
    suffix_profiles = {}
    for pf in o_prefixes:
        tokens = pg.get(pf, [])
        suffixes = Counter(t['suffix'] for t in tokens if t['suffix'])
        total = sum(suffixes.values())
        suffix_profiles[pf] = {s: round(c / total, 3) for s, c in suffixes.most_common(5)} if total else {}

    # Positional profile
    positions = {}
    for pf in o_prefixes:
        tokens = pg.get(pf, [])
        pos_vals = [t.get('line_pos', 0.5) for t in tokens]
        positions[pf] = round(mean(pos_vals), 3) if pos_vals else 0.5

    # Count how many prefixes have distinct dominant category
    unique_doms = len(set(d[0] for d in dominants.values() if d[0]))

    passed = p < 0.001 and unique_doms >= 3

    result = {
        'test': 'T8: O-PREFIX Differentiation',
        'tier': 'Structural=T2, Interpretation=T3-4',
        'passed': passed,
        'chi2': round(chi2, 2), 'p': round(p, 6), 'df': df,
        'counts': {pf: len(pg.get(pf, [])) for pf in o_prefixes},
        'dominant_category': {pf: {'cat': d[0], 'count': d[1]} for pf, d in dominants.items()},
        'unique_dominant_categories': unique_doms,
        'suffix_profiles': suffix_profiles,
        'mean_line_positions': positions,
        'tier34_interpretation': {
            'ok': 'vessel management (e-enriched per T1)',
            'ot': 'adjustment/correction (C911 h-family)',
            'ol': 'continuation/collection (k-dominant)',
            'or': 'output/portioning (FLOW)',
        },
    }
    print(f"  Chi-square: {chi2:.2f}, p={p:.2e}, df={df}")
    print(f"  Counts: { {pf: len(pg.get(pf, [])) for pf in o_prefixes} }")
    print(f"  Dominants: { {pf: d[0] for pf, d in dominants.items()} }")
    print(f"  Unique dominant categories: {unique_doms}")
    print(f"  Positions: {positions}")
    print(f"  PASS: {passed}")
    return result


# ============================================================
# T9: Thermal Shock Prevention
# ============================================================

def test_t9(data):
    """Tokens adjacent to thermal transitions show MONITORING enrichment."""
    print("\n=== T9: Thermal Shock Prevention ===")
    line_groups = data['line_groups']

    # Define thermal transitions: k-rich -> e-rich or e-rich -> k-rich
    K_THRESH = 0.5
    E_THRESH = 0.5

    adjacent_tokens = []  # tokens before or after a thermal transition
    non_adjacent = []

    for tokens in line_groups.values():
        is_adj = [False] * len(tokens)
        for i in range(len(tokens) - 1):
            t1, t2 = tokens[i], tokens[i + 1]
            k_to_e = t1['k_frac'] >= K_THRESH and t2['e_frac'] >= E_THRESH
            e_to_k = t1['e_frac'] >= E_THRESH and t2['k_frac'] >= K_THRESH
            if k_to_e or e_to_k:
                # Mark neighbors
                if i > 0:
                    is_adj[i - 1] = True
                is_adj[i] = True
                is_adj[i + 1] = True
                if i + 2 < len(tokens):
                    is_adj[i + 2] = True
        for i, ti in enumerate(tokens):
            if is_adj[i]:
                adjacent_tokens.append(ti)
            else:
                non_adjacent.append(ti)

    # Category profiles
    adj_cats = Counter(t['category'] for t in adjacent_tokens if t['category'])
    non_cats = Counter(t['category'] for t in non_adjacent if t['category'])
    adj_total = sum(adj_cats.values())
    non_total = sum(non_cats.values())

    # Chi-square: adjacent vs non-adjacent category profiles
    table = [[adj_cats.get(c, 0) for c in CATEGORIES],
             [non_cats.get(c, 0) for c in CATEGORIES]]
    chi2, p, df = chi_square_test(table)

    # Specific predictions
    adj_thermal = adj_cats.get('THERMAL', 0) / adj_total if adj_total else 0
    non_thermal = non_cats.get('THERMAL', 0) / non_total if non_total else 0
    adj_monitor = adj_cats.get('MONITORING', 0) / adj_total if adj_total else 0
    non_monitor = non_cats.get('MONITORING', 0) / non_total if non_total else 0

    # ch/sh prefix enrichment near hazard
    adj_chsh = sum(1 for t in adjacent_tokens if t['prefix'] in ('ch', 'sh'))
    non_chsh = sum(1 for t in non_adjacent if t['prefix'] in ('ch', 'sh'))
    adj_chsh_rate = adj_chsh / len(adjacent_tokens) if adjacent_tokens else 0
    non_chsh_rate = non_chsh / len(non_adjacent) if non_adjacent else 0

    # QO depletion near hazard (energy near hazard is dangerous)
    adj_qo = sum(1 for t in adjacent_tokens if t['prefix'] == 'qo')
    non_qo = sum(1 for t in non_adjacent if t['prefix'] == 'qo')
    adj_qo_rate = adj_qo / len(adjacent_tokens) if adjacent_tokens else 0
    non_qo_rate = non_qo / len(non_adjacent) if non_adjacent else 0

    # Negative control: random positions
    rng = random.Random(SEED)
    null_chi2s = []
    all_tokens = data['b_tokens']
    n_adj = len(adjacent_tokens)
    for _ in range(1000):
        sample = rng.sample(range(len(all_tokens)), min(n_adj, len(all_tokens)))
        s_cats = Counter(all_tokens[i]['category'] for i in sample if all_tokens[i]['category'])
        rest_idx = set(range(len(all_tokens))) - set(sample)
        r_cats = Counter(all_tokens[i]['category'] for i in rest_idx if all_tokens[i]['category'])
        t = [[s_cats.get(c, 0) for c in CATEGORIES],
             [r_cats.get(c, 0) for c in CATEGORIES]]
        c2, _, _ = chi_square_test(t)
        null_chi2s.append(c2)
    p_ctrl = permutation_p(chi2, null_chi2s)

    passed = p < 0.01 and adj_chsh_rate > non_chsh_rate

    result = {
        'test': 'T9: Thermal Shock Prevention',
        'tier': 'Structural=T2, Interpretation=T3-4',
        'passed': passed,
        'n_adjacent': len(adjacent_tokens), 'n_non_adjacent': len(non_adjacent),
        'chi2': round(chi2, 2), 'p': round(p, 6),
        'adj_thermal': round(adj_thermal, 4), 'non_thermal': round(non_thermal, 4),
        'adj_monitoring': round(adj_monitor, 4), 'non_monitoring': round(non_monitor, 4),
        'adj_chsh_rate': round(adj_chsh_rate, 4), 'non_chsh_rate': round(non_chsh_rate, 4),
        'adj_qo_rate': round(adj_qo_rate, 4), 'non_qo_rate': round(non_qo_rate, 4),
        'neg_ctrl_p': round(p_ctrl, 4),
    }
    print(f"  Adjacent: {len(adjacent_tokens)}, Non-adjacent: {len(non_adjacent)}")
    print(f"  Chi-square: {chi2:.2f}, p={p:.4f}")
    print(f"  THERMAL: adj={adj_thermal:.3f} vs non={non_thermal:.3f}")
    print(f"  MONITORING: adj={adj_monitor:.3f} vs non={non_monitor:.3f}")
    print(f"  ch/sh: adj={adj_chsh_rate:.3f} vs non={non_chsh_rate:.3f}")
    print(f"  qo: adj={adj_qo_rate:.3f} vs non={non_qo_rate:.3f}")
    print(f"  Neg ctrl p={p_ctrl:.4f}")
    print(f"  PASS: {passed}")
    return result


# ============================================================
# T10: Bang-Bang Rate by REGIME
# ============================================================

def test_t10(data):
    """QO/CHSH alternation rate varies by REGIME."""
    print("\n=== T10: Bang-Bang Rate by REGIME ===")
    line_groups = data['line_groups']
    ft = data['folio_to_regime']

    def get_lane(ti):
        """Assign token to QO or CHSH lane."""
        pf = ti['prefix']
        if pf == 'qo':
            return 'QO'
        elif pf in ('ch', 'sh'):
            return 'CHSH'
        return None

    # Per-folio alternation rate
    folio_alt_rates = defaultdict(list)
    folio_regime_map = {}
    for (fol, line), tokens in line_groups.items():
        regime = ft.get(fol)
        if not regime:
            continue
        folio_regime_map[fol] = regime
        lanes = [get_lane(t) for t in tokens]
        lanes = [l for l in lanes if l is not None]
        if len(lanes) < 2:
            continue
        alternations = sum(1 for i in range(len(lanes) - 1) if lanes[i] != lanes[i + 1])
        rate = alternations / (len(lanes) - 1)
        folio_alt_rates[fol].append(rate)

    # Aggregate per folio
    folio_means = {f: mean(rates) for f, rates in folio_alt_rates.items()}

    # Group by REGIME
    regimes = sorted(set(ft.values()))
    regime_groups = {r: [] for r in regimes}
    for f, m in folio_means.items():
        r = folio_regime_map.get(f)
        if r:
            regime_groups[r].append(m)

    groups = [regime_groups.get(r, []) for r in regimes]
    H, p = kruskal_wallis(groups)
    regime_means = {r: round(mean(g), 4) for r, g in zip(regimes, groups) if g}

    # Overall weighted average (cross-validate with F-B-004 = 0.563)
    all_rates = [r for rates in folio_alt_rates.values() for r in rates]
    overall = mean(all_rates) if all_rates else 0

    # Predictions: R3 highest, R2 lowest
    predictions_confirmed = 0
    r3_mean = mean(regime_groups.get('REGIME_3', [0]))
    r2_mean = mean(regime_groups.get('REGIME_2', [0]))
    r1_mean = mean(regime_groups.get('REGIME_1', [0]))
    r4_mean = mean(regime_groups.get('REGIME_4', [0]))
    if r3_mean > r2_mean:
        predictions_confirmed += 1
    if r3_mean > r1_mean:
        predictions_confirmed += 1
    # R2 lowest
    if r2_mean <= min(r1_mean, r3_mean, r4_mean):
        predictions_confirmed += 1
    # R4 moderate
    if r4_mean > r2_mean:
        predictions_confirmed += 1

    # Negative control: A tokens
    a_line_groups = defaultdict(list)
    for t in data['a_tokens']:
        a_line_groups[(t['folio'], '1')].append(t)  # A doesn't have line structure the same way
    a_folio_rates = defaultdict(list)
    for (fol, _), tokens in a_line_groups.items():
        lanes = []
        for t in tokens:
            pf = t['prefix']
            if pf == 'qo':
                lanes.append('QO')
            elif pf in ('ch', 'sh'):
                lanes.append('CHSH')
        if len(lanes) < 2:
            continue
        alt = sum(1 for i in range(len(lanes) - 1) if lanes[i] != lanes[i + 1])
        a_folio_rates[fol].append(alt / (len(lanes) - 1))
    a_regime_groups = defaultdict(list)
    for f, rates in a_folio_rates.items():
        r = ft.get(f)
        if r:
            a_regime_groups[r].append(mean(rates))
    a_groups = [a_regime_groups.get(r, []) for r in regimes]
    H_a, p_a = kruskal_wallis(a_groups)

    passed = p < 0.05 and predictions_confirmed >= 2

    result = {
        'test': 'T10: Bang-Bang Rate by REGIME',
        'tier': 'Structural=T2, Brunschwig=T3-4',
        'passed': passed,
        'kw_H': round(H, 2), 'kw_p': round(p, 6),
        'regime_means': regime_means,
        'overall_rate': round(overall, 4),
        'f_b_004_crossval': f"overall={overall:.3f} (expect ~0.563)",
        'predictions_confirmed': predictions_confirmed,
        'neg_ctrl_a_H': round(H_a, 2), 'neg_ctrl_a_p': round(p_a, 4),
    }
    print(f"  KW H={H:.2f}, p={p:.4f}")
    print(f"  Regime means: {regime_means}")
    print(f"  Overall: {overall:.3f} (F-B-004: 0.563)")
    print(f"  Predictions confirmed: {predictions_confirmed}/4")
    print(f"  Neg ctrl A: H={H_a:.2f} p={p_a:.4f}")
    print(f"  PASS: {passed}")
    return result


# ============================================================
# MAPPING TABLE BUILDER
# ============================================================

def build_mapping_table(results):
    """Build the Tier 3-4 distillation mapping table from test results."""

    prefix_map = [
        {'prefix': 'qo', 'domain': 'Heat source', 'physical': 'Fire/furnace management',
         'tests': ['T1', 'T2', 'T10'], 'tier': 3},
        {'prefix': 'ok', 'domain': 'Vessel temperature', 'physical': 'Still/apparatus thermal state',
         'tests': ['T1', 'T2', 'T8'], 'tier': 3},
        {'prefix': 'ch', 'domain': 'Active testing', 'physical': 'Discrete tests (finger, taste, thumbnail)',
         'tests': ['T7', 'T9'], 'tier': 3},
        {'prefix': 'sh', 'domain': 'Passive monitoring', 'physical': 'Continuous observation (drip, fire)',
         'tests': ['T7'], 'tier': 3},
        {'prefix': 'ot', 'domain': 'Adjustment', 'physical': 'Corrective action on apparatus',
         'tests': ['T8'], 'tier': 4},
        {'prefix': 'ol', 'domain': 'Continuation', 'physical': 'Maintaining during active process',
         'tests': ['T8'], 'tier': 4},
        {'prefix': 'da', 'domain': 'Setup/infrastructure', 'physical': 'Apparatus prep, material loading',
         'tests': ['T4'], 'tier': 4},
        {'prefix': 'sa', 'domain': 'Scaffold', 'physical': 'Supporting infrastructure',
         'tests': ['T1 neg'], 'tier': 4},
    ]

    middle_map = [
        {'middle': 'k', 'operation': 'Heat application', 'physical': 'Add fire, open air holes',
         'tests': ['T1', 'T2'], 'tier': 3},
        {'middle': 'e', 'operation': 'Cooling', 'physical': 'Close air holes, water cooling',
         'tests': ['T1', 'T2'], 'tier': 3},
        {'middle': 'ke', 'operation': 'Sustained heat', 'physical': 'Maintain fire at level',
         'tests': ['T6'], 'tier': 3},
        {'middle': 'eey/eeol', 'operation': 'Extended cooling', 'physical': 'Overnight standing',
         'tests': ['T6'], 'tier': 3},
        {'middle': 'dy', 'operation': 'Seal/close', 'physical': 'Lute joints, close vessel',
         'tests': ['T5'], 'tier': 3},
        {'middle': 'edy', 'operation': 'Batch', 'physical': 'Standard operational batch',
         'tests': [], 'tier': 4},
        {'middle': 'od', 'operation': 'Collect', 'physical': 'Gather distillate',
         'tests': ['T8'], 'tier': 4},
        {'middle': 'iin', 'operation': 'Iterate', 'physical': 'Repeated cycling (cohobation)',
         'tests': ['T3'], 'tier': 4},
        {'middle': 'aiin/ain', 'operation': 'Settle/intake', 'physical': 'Wind-down cycling',
         'tests': ['T8'], 'tier': 4},
    ]

    category_map = [
        {'category': 'THERMAL', 'domain': 'Temperature management',
         'tests': ['T1', 'T4', 'T9'], 'tier': 3},
        {'category': 'MONITORING', 'domain': 'Sensory feedback',
         'tests': ['T7', 'T9'], 'tier': 3},
        {'category': 'CONTAINMENT', 'domain': 'Vessel integrity (luting, sealing)',
         'tests': ['T5'], 'tier': 3},
        {'category': 'FLOW', 'domain': 'Material movement (transfer, collection)',
         'tests': ['T8'], 'tier': 3},
        {'category': 'OPERATION', 'domain': 'Physical work (stirring, pounding)',
         'tests': ['T3'], 'tier': 4},
        {'category': 'STAGING', 'domain': 'Process sequencing',
         'tests': ['T8'], 'tier': 4},
        {'category': 'TRANSITION', 'domain': 'Phase boundaries (start, end)',
         'tests': ['T3'], 'tier': 4},
        {'category': 'MARKING', 'domain': 'Annotations, hazard flags',
         'tests': ['T9'], 'tier': 4},
    ]

    regime_map = [
        {'regime': 'REGIME_1', 'brunschwig': 'Balneum marie (water bath)',
         'character': 'Gentle, e-rich, overnight cooling, no luting',
         'tests': ['T4', 'T5', 'T6'], 'tier': 3},
        {'regime': 'REGIME_2', 'brunschwig': 'Sustained operation',
         'character': 'High k-purity, iteration-heavy',
         'tests': ['T4', 'T10'], 'tier': 3},
        {'regime': 'REGIME_3', 'brunschwig': 'Ash/sand (per ignem)',
         'character': 'Direct fire, rapid gathering, luting required',
         'tests': ['T4', 'T5', 'T7'], 'tier': 3},
        {'regime': 'REGIME_4', 'brunschwig': 'Precision operation',
         'character': 'h-rich monitoring, tight tolerance',
         'tests': ['T4', 'T7'], 'tier': 3},
    ]

    midprocess_map = results.get('T3', {}).get('action_profiles', {})

    return {
        'description': 'Tier 3-4 interpretive reference mapping (extends GLOSSING.md)',
        'precedent': 'GLOSSING.md (Tier 3-4, context/GLOSSING.md)',
        'prefix_to_domain': prefix_map,
        'middle_to_operation': middle_map,
        'category_to_domain': category_map,
        'regime_to_brunschwig': regime_map,
        'midprocess_action_profiles': midprocess_map,
    }


# ============================================================
# COVERAGE CHECK
# ============================================================

def compute_coverage(data):
    """What fraction of B tokens get a distillation mapping?"""
    mapped = 0
    total = len(data['b_tokens'])
    mapped_prefixes = {'qo', 'ok', 'ch', 'sh', 'ot', 'ol', 'da', 'sa', 'ct',
                       'or', 'ar', 'al'}  # all known prefixes
    for t in data['b_tokens']:
        if t['prefix'] in mapped_prefixes or t['category']:
            mapped += 1
    return {'mapped': mapped, 'total': total,
            'coverage': round(mapped / total * 100, 1) if total else 0}


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("Phase 461: DISTILLATION_TERMINOLOGY_MAPPING")
    print("=" * 60)

    data = load_data()

    # Canonical count verification
    n_b = len(data['b_tokens'])
    n_a = len(data['a_tokens'])
    print(f"\nCanonical counts: B={n_b} (expect ~23096), A={n_a} (expect ~11174)")
    assert 23000 < n_b < 23300, f"B count out of range: {n_b}"
    assert 11000 < n_a < 11500, f"A count out of range: {n_a}"

    # Run all 10 tests
    tests = [
        ('T1', test_t1),
        ('T2', test_t2),
        ('T3', test_t3),
        ('T4', test_t4),
        ('T5', test_t5),
        ('T6', test_t6),
        ('T7', test_t7),
        ('T8', test_t8),
        ('T9', test_t9),
        ('T10', test_t10),
    ]

    results = {}
    for name, fn in tests:
        results[name] = fn(data)

    # Build mapping table
    mapping = build_mapping_table(results)

    # Coverage
    coverage = compute_coverage(data)

    # Summary
    passed = sum(1 for r in results.values() if r.get('passed'))
    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed}/10 tests passed")
    print("=" * 60)
    for name, r in results.items():
        status = "PASS" if r.get('passed') else "FAIL"
        print(f"  {name}: {status}")
    print(f"\nCoverage: {coverage['coverage']}% ({coverage['mapped']}/{coverage['total']})")

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 'DISTILLATION_TERMINOLOGY_MAPPING',
        'phase_number': 461,
        'tier': '3-4 (intentionally interpretive, extending GLOSSING.md)',
        'seed': SEED,
        'n_permutations': N_PERM,
        'canonical_counts': {'B': n_b, 'A': n_a},
        'tests': results,
        'mapping_table': mapping,
        'coverage': coverage,
        'summary': {
            'tests_passed': passed,
            'tests_total': 10,
        },
        'fits_to_register': {
            'F-B-008': {'name': 'Two-Channel Thermal Architecture',
                        'source': 'T1', 'tier': 'F3',
                        'register': results['T1'].get('passed', False)},
            'F-B-009': {'name': 'Overshoot-Correct Cycling',
                        'source': 'T2', 'tier': 'F3',
                        'register': results['T2'].get('passed', False)},
            'F-B-010': {'name': 'REGIME Token Profile Discrimination',
                        'source': 'T4', 'tier': 'F3',
                        'register': results['T4'].get('passed', False)},
            'F-B-011': {'name': 'Luting-CONTAINMENT REGIME Association',
                        'source': 'T5', 'tier': 'F3',
                        'register': results['T5'].get('passed', False)},
            'F-B-012': {'name': 'E-Compound Cooling Taxonomy',
                        'source': 'T6', 'tier': 'F4',
                        'register': results['T6'].get('passed', False)},
        },
    }

    output_path = RESULTS_DIR / 'distillation_terminology_mapping.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
