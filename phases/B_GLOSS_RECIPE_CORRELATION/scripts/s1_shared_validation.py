"""
Phase 641, Script 1: Shared validation utilities.

Library module — not executed directly. Provides loaders, correlation fns,
leave-one-out, bootstrap, BH-FDR for the Phase 641 scripts.
"""
import sys, os, json, random, re
from collections import Counter, defaultdict
from statistics import mean

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, ROOT)

from scripts.voynich import Transcript, Morphology

# ============================================================
# MATCHED PAIRS — frozen set from prior phases
# ============================================================
MATCHED_PAIRS = [
    # (folio, part, chapter_num, tier, description)
    ('f75r',  'Mercuriorum', 19, 'CONFIRMED',       'Ch19M aqua vitae 9x reflux'),
    ('f76r',  'Practica',    18, 'CONFIRMED',       'Ch18P element separation'),
    ('f84r',  'Practica',    14, 'CONFIRMED',       'Ch14P gold dissolution balneum'),
    ('f79r',  'Mercuriorum', 12, 'STRONG',          'Ch12M mercury sublimation'),
    ('f82r',  'Mercuriorum', 22, 'STRONG',          'Ch22M lunaria maceration 3-day sealed'),
    ('f103r', 'Mercuriorum', 16, 'STRONG',          'Ch16M ferment multiplication'),
    ('f76v',  'Mercuriorum', 15, 'STRONG',          'Ch15M ferment conversion'),
    ('f77v',  'Mercuriorum', 27, 'SUPPORTED',       'Ch27M furnace specification'),
    ('f81v',  'Mercuriorum', 18, 'SUPPORTED',       'Ch18M potable gold'),
    ('f82v',  'Mercuriorum', 28, 'SUPPORTED',       'Ch28M vessel specification'),
    ('f112r', 'Mercuriorum', 11, 'SUPPORTED',       'Ch11M red mercury cohobation'),
    ('f112v', 'Mercuriorum',  1, 'SUPPORTED',       'Ch1M lunaria→quicksilver'),
    ('f116r', 'Mercuriorum',  4, 'SUPPORTED',       'Ch4M fixation / fusibility'),
    ('f107r', 'Mercuriorum', 44, 'SUPPORTED',       'Ch44M quicksilver coagulation'),
    # f80r matches multiple chapters 21-25; we'll handle by merging features
    ('f80r',  'Mercuriorum', (21, 23, 24, 25), 'SUPPORTED', 'Ch21-25M animal ash chain'),
    ('f83r',  'Practica',     9, 'SUPPORTED',       'Ch9P aqua vitae / alchemy fundamentals'),
]

# ============================================================
# LATIN FEATURE LOADER
# ============================================================
_feat_cache = None
def load_latin_features():
    global _feat_cache
    if _feat_cache: return _feat_cache
    path = os.path.join(os.path.dirname(__file__), '..', 'results', 'pl_channel_features_latin.json')
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Build (part, number) -> merged features dict. Duplicates get feature counts summed.
    lookup = defaultdict(lambda: {'line_count': 0, 'features': defaultdict(float), 'heat_subtypes': defaultdict(int)})
    for ch in data['chapters']:
        key = (ch['part'], ch['number'])
        lookup[key]['line_count'] += ch.get('line_count', 0)
        for k, v in ch['features'].items():
            if k == 'heat_subtypes':
                for sk, sv in v.items():
                    lookup[key]['heat_subtypes'][sk] += sv
            elif k.endswith('_count'):
                lookup[key]['features'][k] += v
            elif k.endswith('_rate'):
                pass  # we'll recompute
    # Compute final rates
    for key, entry in lookup.items():
        lc = max(1, entry['line_count'])
        for k in list(entry['features']):
            if k.endswith('_count'):
                entry['features'][k + '__rate'] = entry['features'][k] / lc
        entry['features'] = dict(entry['features'])
        entry['heat_subtypes'] = dict(entry['heat_subtypes'])
    _feat_cache = dict(lookup)
    return _feat_cache

def recipe_feature_profile(part, chapter_num):
    """For a matched pair, return feature profile. Handles multi-chapter (tuple).
    Returns dict of feature_name -> count (or rate)."""
    feats = load_latin_features()
    if isinstance(chapter_num, tuple):
        # Merge features across multi-chapter match (e.g., f80r -> 21,23,24,25)
        merged_counts = defaultdict(float)
        total_lines = 0
        for n in chapter_num:
            e = feats.get((part, n))
            if not e: continue
            for k, v in e['features'].items():
                if k.endswith('_count'):
                    merged_counts[k] += v
            total_lines += e['line_count']
        # Recompute rates
        for k in list(merged_counts):
            merged_counts[k + '__rate'] = merged_counts[k] / max(1, total_lines)
        return {'line_count': total_lines, 'features': dict(merged_counts)}
    e = feats.get((part, chapter_num))
    if not e: return None
    return e

# ============================================================
# FOLIO ATOM / PREFIX / SUFFIX PROFILES
# ============================================================
_tx = None
_morph = None
_folio_cache = {}

def _get_tx():
    global _tx, _morph
    if _tx is None:
        _tx = Transcript()
        _morph = Morphology()
    return _tx, _morph

def folio_profile(folio):
    """Return per-folio atom/prefix/suffix rates."""
    if folio in _folio_cache:
        return _folio_cache[folio]
    tx, morph = _get_tx()
    tokens = [t for t in tx.currier_b() if t.folio == folio and t.word.strip() and '*' not in t.word]

    atom_counts = Counter()
    head_atom_counts = Counter()
    term_atom_counts = Counter()
    prefix_counts = Counter()
    suffix_counts = Counter()
    suffix_head_counts = Counter()  # e.g., "dy" vs "ey" vs "hy" compound-terminal
    e_depth_counts = Counter()
    m_terminal_count = 0
    paragraph_final_m = 0

    # Track paragraph-final positions for -am
    para_final_tokens = []
    current_line_tokens = []
    prev_was_par_final = False

    for i, t in enumerate(tokens):
        a = morph.atomize(t.word)
        m = morph.extract(t.word)
        if a:
            if a.e_depth is not None:
                e_depth_counts[a.e_depth] += 1
            for ch, role, g in a.atoms:
                atom_counts[ch] += 1
            if a.atoms:
                head_atom_counts[a.atoms[0][0]] += 1
                term_atom_counts[a.atoms[-1][0]] += 1
                # m-terminal
                if a.atoms[-1][0] == 'm':
                    m_terminal_count += 1
        if m:
            prefix_counts[m.prefix or 'BARE'] += 1
            if m.suffix:
                suffix_counts[m.suffix] += 1
                # Compound terminal analysis: -dy, -ey, -hy, -am etc.
                # Look at last 2 chars of word (approximate compound terminal)
                if len(t.word) >= 2:
                    suffix_head_counts[t.word[-2:]] += 1

    n = max(1, len(tokens))
    profile = {
        'n_tokens': n,
        'folio': folio,
        'atom_rate': {k: v/n for k, v in atom_counts.items()},
        'head_atom_rate': {k: v/n for k, v in head_atom_counts.items()},
        'term_atom_rate': {k: v/n for k, v in term_atom_counts.items()},
        'prefix_rate': {k: v/n for k, v in prefix_counts.items()},
        'suffix_rate': {k: v/n for k, v in suffix_counts.items()},
        'compound_term_rate': {k: v/n for k, v in suffix_head_counts.items()},
        'e_depth_mean': sum(k*v for k, v in e_depth_counts.items())/n if e_depth_counts else 0,
        'm_terminal_rate': m_terminal_count / n,
    }
    _folio_cache[folio] = profile
    return profile

# ============================================================
# STATISTICAL UTILITIES
# ============================================================
def spearman_rho(x, y):
    """Spearman rank correlation."""
    n = len(x)
    if n < 3: return 0.0
    def rank(arr):
        order = sorted(range(n), key=lambda i: arr[i])
        r = [0] * n
        # Average-rank ties (robust to equal values)
        i = 0
        while i < n:
            j = i
            while j+1 < n and arr[order[j+1]] == arr[order[i]]:
                j += 1
            avg_rank = (i + j) / 2 + 1
            for k in range(i, j+1):
                r[order[k]] = avg_rank
            i = j + 1
        return r
    rx = rank(x); ry = rank(y)
    mx = mean(rx); my = mean(ry)
    num = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    dx = sum((rx[i]-mx)**2 for i in range(n))**0.5
    dy = sum((ry[i]-my)**2 for i in range(n))**0.5
    if dx*dy == 0: return 0.0
    return num / (dx*dy)

def perm_pvalue(x, y, n_perm=10000, seed=42, two_sided=True):
    """Exact permutation p-value for Spearman rho."""
    rng = random.Random(seed)
    obs = spearman_rho(x, y)
    count = 0
    y_copy = list(y)
    for _ in range(n_perm):
        rng.shuffle(y_copy)
        rho_perm = spearman_rho(x, y_copy)
        if two_sided:
            if abs(rho_perm) >= abs(obs): count += 1
        else:
            if rho_perm >= obs: count += 1
    return obs, count / n_perm

def bootstrap_rho_ci(x, y, n_boot=1000, seed=42, alpha=0.05):
    """Bootstrap 95% CI for Spearman rho."""
    rng = random.Random(seed)
    n = len(x)
    rhos = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        x_b = [x[i] for i in idx]
        y_b = [y[i] for i in idx]
        r = spearman_rho(x_b, y_b)
        rhos.append(r)
    rhos.sort()
    lo_idx = int(n_boot * alpha/2)
    hi_idx = int(n_boot * (1 - alpha/2))
    return rhos[lo_idx], rhos[hi_idx]

def leave_one_out(x, y, labels):
    """Return dict {dropped_label: rho_without_it} and stability flag."""
    results = {}
    obs_rho = spearman_rho(x, y)
    for i, lbl in enumerate(labels):
        x_loo = [v for j, v in enumerate(x) if j != i]
        y_loo = [v for j, v in enumerate(y) if j != i]
        results[lbl] = spearman_rho(x_loo, y_loo)
    # Stability: all LOO rhos same sign as original, min magnitude > 0.6 * original
    same_sign = all((r * obs_rho >= 0) for r in results.values())
    min_mag = min(abs(r) for r in results.values())
    stable = same_sign and (min_mag > 0.6 * abs(obs_rho))
    return {
        'observed': obs_rho,
        'loo_rhos': results,
        'same_sign': same_sign,
        'min_mag_fraction': min_mag / abs(obs_rho) if obs_rho != 0 else 0,
        'stable': stable,
    }

def bh_fdr(pvals, q=0.10):
    """Benjamini-Hochberg FDR. Returns list of bools (accept null hypothesis rejection)."""
    n = len(pvals)
    if n == 0: return []
    indexed = sorted(enumerate(pvals), key=lambda x: x[1])
    accept = [False]*n
    for rank, (orig_idx, p) in enumerate(indexed, 1):
        threshold = (rank / n) * q
        if p <= threshold:
            # Mark this and all prior as accepted
            for r2 in range(rank):
                accept[indexed[r2][0]] = True
    return accept

def directional_verdict(rho, p, predicted_sign, p_threshold=0.05):
    """
    SUPPORTED: predicted direction + p < threshold
    INCONCLUSIVE: predicted direction but p too high, or neutral
    FALSIFIED: direction reversed + p < threshold
    """
    if predicted_sign == '+':
        if rho > 0 and p < p_threshold:
            return 'SUPPORTED'
        if rho < 0 and p < p_threshold:
            return 'FALSIFIED'
    elif predicted_sign == '-':
        if rho < 0 and p < p_threshold:
            return 'SUPPORTED'
        if rho > 0 and p < p_threshold:
            return 'FALSIFIED'
    return 'INCONCLUSIVE'

# ============================================================
# CONVENIENCE: run one correlation with all apparatus
# ============================================================
def run_test(test_label, folio_values, feature_values, labels, predicted_sign, n_perm=10000, n_boot=1000):
    """Run single correlation test with full statistical apparatus."""
    rho, p = perm_pvalue(folio_values, feature_values, n_perm=n_perm)
    ci_lo, ci_hi = bootstrap_rho_ci(folio_values, feature_values, n_boot=n_boot)
    loo = leave_one_out(folio_values, feature_values, labels)
    verdict = directional_verdict(rho, p, predicted_sign)
    ci_excludes_zero = not (ci_lo <= 0 <= ci_hi)
    return {
        'label': test_label,
        'rho': rho,
        'p': p,
        'predicted_sign': predicted_sign,
        'verdict': verdict,
        'bootstrap_ci': [ci_lo, ci_hi],
        'ci_excludes_zero': ci_excludes_zero,
        'loo_stable': loo['stable'],
        'loo_min_mag_fraction': loo['min_mag_fraction'],
        'n_pairs': len(folio_values),
    }

if __name__ == '__main__':
    # Smoke test
    feats = load_latin_features()
    print(f"Loaded {len(feats)} (part, chapter) feature profiles")

    # Verify we can build profile for each matched pair
    print("\nMatched pair profile availability:")
    for folio, part, num, tier, desc in MATCHED_PAIRS:
        rp = recipe_feature_profile(part, num)
        fp = folio_profile(folio)
        if rp and fp:
            print(f"  OK  {folio:<6} -> {part} {num}  ({fp['n_tokens']} tokens / {rp['line_count']} recipe lines)")
        else:
            print(f"  MISSING  {folio} -> {part} {num}")
