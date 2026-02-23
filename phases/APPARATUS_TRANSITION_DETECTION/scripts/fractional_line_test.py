"""
Phase 438 Extension: FRACTIONAL_LINE_TEST
Test whether lines within paragraphs represent fractional distillation passes
that produce distinct output products.

Tests:
  T1: Suffix profile piecewise vs smooth (BIC)
  T2: FL reset x suffix change co-occurrence
  T3: Paragraph length x output diversity
  T4: Within-paragraph suffix clustering
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

ALPHA_BONFERRONI = 0.05 / 4  # 0.0125
BIC_THRESHOLD = 6
MIN_BODY_PIECEWISE = 5   # 6+ total lines
MIN_BODY_CLUSTER = 7     # 8+ total lines

TERMINAL_SUFFIXES = {'y', 'dy', 'am', 'edy', 'ey', 'ly', 'ry', 'hy', 'eey', 'om', 'im'}
CONNECTOR_SUFFIXES = {'in', 'r', 'l', 's', 'an', 'en', 'on'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'iin', 'oiin'}
# BARE = no suffix or not in any category above

FL_STATES = {
    'EARLY': {'i', 'ii', 'in'},
    'MEDIAL': {'r', 'ar', 'al', 'l', 'ol'},
    'LATE': {'o', 'ly', 'am', 'm', 'dy', 'ry', 'y'},
}
STATE_ORDER = {'EARLY': 0, 'MEDIAL': 1, 'LATE': 2}


# ── Statistics ───────────────────────────────────────────────

def rd(x, d=4):
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
    if rss <= 0 or n <= k:
        return float('inf')
    return n * math.log(rss / n) + k * math.log(n)


def linear_fit(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    if n < 2:
        return 0.0, 0.0, float('inf')
    A = np.column_stack([np.ones(n), x])
    coef, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    rss = float(np.sum((y - pred) ** 2))
    return float(coef[0]), float(coef[1]), rss


def piecewise_fit(x, y, bp_idx):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    if bp_idx < 1 or bp_idx >= n - 1:
        return float('inf'), {}
    x1, y1 = x[:bp_idx + 1], y[:bp_idx + 1]
    x2, y2 = x[bp_idx:], y[bp_idx:]
    _, _, rss1 = linear_fit(x1, y1)
    _, _, rss2 = linear_fit(x2, y2)
    return rss1 + rss2, {'bp': int(bp_idx)}


def best_breakpoint(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    _, _, rss_lin = linear_fit(x, y)
    bic_lin = bic(n, 2, rss_lin)

    lo = max(2, n // 3)
    hi = min(n - 2, 2 * n // 3)

    best_bic_pw = float('inf')
    best_bp = None
    for bp in range(lo, hi + 1):
        rss_pw, _ = piecewise_fit(x, y, bp)
        bic_pw = bic(n, 5, rss_pw)
        if bic_pw < best_bic_pw:
            best_bic_pw = bic_pw
            best_bp = bp

    if best_bp is None:
        return 0.0, None, None

    delta = bic_lin - best_bic_pw
    bp_norm = best_bp / (n - 1) if n > 1 else 0.5
    return delta, best_bp, bp_norm


def compute_jsd(p, q, epsilon=1e-10):
    p = np.array(p, dtype=float) + epsilon
    q = np.array(q, dtype=float) + epsilon
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log2(p / m)) + 0.5 * np.sum(q * np.log2(q / m)))


def get_fl_stage(middle):
    for stage, middles in FL_STATES.items():
        if middle in middles:
            return stage
    return None


# ── Suffix Profile ───────────────────────────────────────────

def classify_suffix(suffix):
    """Classify a suffix into TERMINAL, CONNECTOR, ITERATE, or BARE."""
    if not suffix:
        return 'BARE'
    if suffix in TERMINAL_SUFFIXES:
        return 'TERMINAL'
    if suffix in CONNECTOR_SUFFIXES:
        return 'CONNECTOR'
    if suffix in ITERATE_SUFFIXES:
        return 'ITERATE'
    return 'BARE'


def suffix_profile(suffixes):
    """Compute suffix category fractions from a list of suffixes."""
    if not suffixes:
        return {'terminal': 0, 'connector': 0, 'iterate': 0, 'bare': 1.0}
    cats = [classify_suffix(s) for s in suffixes]
    n = len(cats)
    return {
        'terminal': sum(1 for c in cats if c == 'TERMINAL') / n,
        'connector': sum(1 for c in cats if c == 'CONNECTOR') / n,
        'iterate': sum(1 for c in cats if c == 'ITERATE') / n,
        'bare': sum(1 for c in cats if c == 'BARE') / n,
    }


def suffix_vec(profile):
    """Convert suffix profile dict to vector [terminal, connector, iterate, bare]."""
    return [profile['terminal'], profile['connector'], profile['iterate'], profile['bare']]


# ── Data Loading ─────────────────────────────────────────────

def load_paragraphs():
    """Build paragraph inventory with per-line suffix and FL features."""
    tx = Transcript()
    morph = Morphology()

    line_tokens = defaultdict(list)
    folio_lines = defaultdict(list)
    line_meta = {}

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue

        key = (token.folio, token.line)
        m = morph.extract(w)
        fl_stage = get_fl_stage(m.middle) if m.middle else None

        line_tokens[key].append({
            'word': w,
            'middle': m.middle or '',
            'prefix': m.prefix or '',
            'suffix': m.suffix or '',
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

    # Build paragraphs
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

    # Build per-line features
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

            suffixes = [t['suffix'] for t in tokens]
            profile = suffix_profile(suffixes)

            fl_stages = [t['fl_stage'] for t in tokens if t['fl_stage'] is not None]
            first_fl = fl_stages[0] if fl_stages else None
            last_fl = fl_stages[-1] if fl_stages else None

            line_records.append({
                'key': lk,
                'n_tokens': len(tokens),
                'suffixes': suffixes,
                'suffix_profile': profile,
                'first_fl': first_fl,
                'last_fl': last_fl,
            })

        if len(line_records) < 2:
            continue

        body = line_records[1:]
        result.append({
            'par_id': f'{folio}_p{par_idx}',
            'folio': folio,
            'section': section,
            'header': line_records[0],
            'body': body,
            'n_body': len(body),
        })

    return result


# ── T1: Suffix Profile Piecewise vs Smooth ───────────────────

def test_1_suffix_piecewise(paragraphs):
    """Fit piecewise vs linear on suffix category fractions."""
    qualifying = [p for p in paragraphs if p['n_body'] >= MIN_BODY_PIECEWISE]
    print(f"  T1: {len(qualifying)} paragraphs with {MIN_BODY_PIECEWISE}+ body lines")

    categories = ['terminal', 'connector', 'iterate', 'bare']
    cat_results = {}

    for cat in categories:
        bp_count = 0
        bp_positions = []
        delta_bics = []

        for p in qualifying:
            body = p['body']
            # Require at least 3 tokens per line for stable suffix fractions
            valid = [(i, ln) for i, ln in enumerate(body) if ln['n_tokens'] >= 3]
            if len(valid) < MIN_BODY_PIECEWISE:
                continue

            x = np.array([v[0] for v in valid], dtype=float)
            y = np.array([v[1]['suffix_profile'][cat] for v in valid], dtype=float)

            delta, bp_idx, bp_norm = best_breakpoint(x, y)
            delta_bics.append(delta)

            if delta > BIC_THRESHOLD:
                bp_count += 1
                if bp_norm is not None:
                    bp_positions.append(bp_norm)

        n_tested = len(delta_bics)
        rate = bp_count / n_tested if n_tested > 0 else 0

        # KS test on breakpoint positions
        if len(bp_positions) >= 5:
            ks_stat, ks_p = sp_stats.kstest(bp_positions, 'uniform')
        else:
            ks_stat, ks_p = 0.0, 1.0

        cat_results[cat] = {
            'n_tested': n_tested,
            'bp_count': bp_count,
            'bp_rate': rd(rate),
            'mean_delta_bic': rd(float(np.mean(delta_bics))) if delta_bics else 0,
            'ks_stat': rd(float(ks_stat)),
            'ks_p': rd(float(ks_p)),
        }

        print(f"    {cat}: {bp_count}/{n_tested} ({rate:.1%}) breakpoints")

    # Any category >30% -> discrete
    max_rate = max(cat_results[c]['bp_rate'] for c in categories)
    if max_rate > 0.30:
        verdict = 'DISCRETE_FRACTIONS_DETECTED'
    elif max_rate > 0.10:
        verdict = 'SUFFIX_BREAKPOINT_MARGINAL'
    else:
        verdict = 'SMOOTH_GRADIENT'

    print(f"    Verdict: {verdict}")

    return rd({
        'n_qualifying': len(qualifying),
        'by_category': cat_results,
        'max_breakpoint_rate': max_rate,
        'verdict': verdict,
    })


# ── T2: FL Reset × Suffix Change ────────────────────────────

def test_2_fl_reset_suffix(paragraphs):
    """Compare suffix JSD at FL regression vs non-regression line boundaries."""
    qualifying = [p for p in paragraphs if p['n_body'] >= 3]

    regression_jsds = []
    non_regression_jsds = []
    no_fl_jsds = []

    for p in qualifying:
        body = p['body']
        for i in range(len(body) - 1):
            # Suffix JSD between consecutive lines
            v1 = suffix_vec(body[i]['suffix_profile'])
            v2 = suffix_vec(body[i + 1]['suffix_profile'])
            jsd = compute_jsd(v1, v2)

            # FL regression check
            last_fl = body[i]['last_fl']
            first_fl = body[i + 1]['first_fl']

            if last_fl is None or first_fl is None:
                no_fl_jsds.append(jsd)
                continue

            if last_fl not in STATE_ORDER or first_fl not in STATE_ORDER:
                no_fl_jsds.append(jsd)
                continue

            regression = STATE_ORDER[last_fl] - STATE_ORDER[first_fl]

            if regression >= 1:  # FL regresses (LATE->MEDIAL or LATE->EARLY)
                regression_jsds.append(jsd)
            else:
                non_regression_jsds.append(jsd)

    print(f"  T2: {len(regression_jsds)} regression pairs, {len(non_regression_jsds)} non-regression, {len(no_fl_jsds)} no-FL")

    if len(regression_jsds) < 10 or len(non_regression_jsds) < 10:
        print(f"    INSUFFICIENT DATA")
        return rd({
            'n_regression': len(regression_jsds),
            'n_non_regression': len(non_regression_jsds),
            'verdict': 'INSUFFICIENT_FL_DATA',
        })

    regr_mean = float(np.mean(regression_jsds))
    non_regr_mean = float(np.mean(non_regression_jsds))

    stat, p_val = sp_stats.mannwhitneyu(regression_jsds, non_regression_jsds, alternative='greater')

    # Effect size (rank-biserial)
    n1, n2 = len(regression_jsds), len(non_regression_jsds)
    r_effect = 1 - (2 * stat) / (n1 * n2)

    verdict = 'FL_RESET_SUFFIX_CHANGE' if p_val < ALPHA_BONFERRONI else 'FL_RESET_NO_SUFFIX_EFFECT'

    print(f"    Regression JSD mean: {regr_mean:.4f}")
    print(f"    Non-regression JSD mean: {non_regr_mean:.4f}")
    print(f"    Mann-Whitney p: {p_val:.6f}, effect r: {r_effect:.4f}")
    print(f"    Verdict: {verdict}")

    return rd({
        'n_regression': len(regression_jsds),
        'n_non_regression': len(non_regression_jsds),
        'n_no_fl': len(no_fl_jsds),
        'regression_jsd_mean': regr_mean,
        'non_regression_jsd_mean': non_regr_mean,
        'mann_whitney_stat': float(stat),
        'mann_whitney_p': float(p_val),
        'effect_size_r': r_effect,
        'verdict': verdict,
    })


# ── T3: Paragraph Length × Output Diversity ──────────────────

def test_3_length_diversity(paragraphs):
    """Correlate paragraph length with within-paragraph suffix diversity."""
    qualifying = [p for p in paragraphs if p['n_body'] >= 3]
    print(f"  T3: {len(qualifying)} paragraphs with 3+ body lines")

    lengths = []
    diversities = []

    for p in qualifying:
        body = p['body']
        n = len(body)

        # Mean pairwise suffix JSD across all body line pairs
        jsds = []
        for i in range(n):
            for j in range(i + 1, n):
                v1 = suffix_vec(body[i]['suffix_profile'])
                v2 = suffix_vec(body[j]['suffix_profile'])
                jsds.append(compute_jsd(v1, v2))

        if jsds:
            mean_jsd = float(np.mean(jsds))
            lengths.append(n)
            diversities.append(mean_jsd)

    if len(lengths) < 20:
        print(f"    INSUFFICIENT DATA")
        return rd({'n': len(lengths), 'verdict': 'INSUFFICIENT_DATA'})

    rho, p_val = sp_stats.spearmanr(lengths, diversities)

    # Permutation control: shuffle suffix profiles within paragraphs
    rng = np.random.default_rng(42)
    perm_rhos = []
    for _ in range(1000):
        perm_divs = []
        for p in qualifying:
            body = p['body']
            n = len(body)
            profiles = [suffix_vec(ln['suffix_profile']) for ln in body]
            rng.shuffle(profiles)
            jsds = []
            for i in range(n):
                for j in range(i + 1, n):
                    jsds.append(compute_jsd(profiles[i], profiles[j]))
            if jsds:
                perm_divs.append(float(np.mean(jsds)))
        if len(perm_divs) == len(lengths):
            pr, _ = sp_stats.spearmanr(lengths, perm_divs)
            perm_rhos.append(pr)

    perm_p = (sum(1 for pr in perm_rhos if pr >= rho) + 1) / (len(perm_rhos) + 1) if perm_rhos else 1.0

    verdict = 'LENGTH_DIVERSITY_CORRELATED' if p_val < ALPHA_BONFERRONI and rho > 0 else 'LENGTH_DIVERSITY_NULL'

    print(f"    Spearman rho: {rho:.4f}, p: {p_val:.6f}")
    print(f"    Permutation p: {perm_p:.4f}")
    print(f"    Mean diversity (3-line): {np.mean([d for l, d in zip(lengths, diversities) if l <= 4]):.4f}")
    short_divs = [d for l, d in zip(lengths, diversities) if l <= 4]
    long_divs = [d for l, d in zip(lengths, diversities) if l >= 8]
    if short_divs:
        print(f"    Mean diversity (short <=4): {np.mean(short_divs):.4f}")
    if long_divs:
        print(f"    Mean diversity (long >=8): {np.mean(long_divs):.4f}")
    print(f"    Verdict: {verdict}")

    return rd({
        'n_paragraphs': len(lengths),
        'spearman_rho': float(rho),
        'spearman_p': float(p_val),
        'permutation_p': perm_p,
        'mean_diversity_short': float(np.mean(short_divs)) if short_divs else None,
        'mean_diversity_long': float(np.mean(long_divs)) if long_divs else None,
        'verdict': verdict,
    })


# ── T4: Within-Paragraph Suffix Clustering ───────────────────

def test_4_suffix_clustering(paragraphs):
    """Test whether body lines cluster into discrete suffix groups."""
    qualifying = [p for p in paragraphs if p['n_body'] >= MIN_BODY_CLUSTER]
    print(f"  T4: {len(qualifying)} paragraphs with {MIN_BODY_CLUSTER}+ body lines")

    if len(qualifying) < 10:
        print(f"    INSUFFICIENT DATA")
        return rd({'n': len(qualifying), 'verdict': 'INSUFFICIENT_DATA'})

    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    k1_wins = 0
    k2_wins = 0
    k3_wins = 0
    contiguous_count = 0
    n_tested = 0

    silhouette_k2s = []
    silhouette_k3s = []

    for p in qualifying:
        body = p['body']
        profiles = np.array([suffix_vec(ln['suffix_profile']) for ln in body])

        if len(profiles) < 4:
            continue

        n_tested += 1

        # k=2
        km2 = KMeans(n_clusters=2, n_init=10, random_state=42).fit(profiles)
        sil2 = silhouette_score(profiles, km2.labels_) if len(set(km2.labels_)) > 1 else -1
        silhouette_k2s.append(sil2)

        # k=3
        if len(profiles) >= 6:
            km3 = KMeans(n_clusters=3, n_init=10, random_state=42).fit(profiles)
            sil3 = silhouette_score(profiles, km3.labels_) if len(set(km3.labels_)) > 1 else -1
            silhouette_k3s.append(sil3)
        else:
            sil3 = -1

        # "k=1" baseline: silhouette is 0 by definition
        if sil2 > 0.3:
            k2_wins += 1
        elif sil3 > 0.3:
            k3_wins += 1
        else:
            k1_wins += 1

        # Contiguity test for best k=2: are clusters contiguous blocks?
        if sil2 > 0.3:
            labels = km2.labels_
            runs = 1
            for i in range(1, len(labels)):
                if labels[i] != labels[i - 1]:
                    runs += 1
            # Perfectly contiguous = 2 runs for k=2
            if runs <= 3:
                contiguous_count += 1

    k2_rate = k2_wins / n_tested if n_tested > 0 else 0
    k3_rate = k3_wins / n_tested if n_tested > 0 else 0
    cluster_rate = (k2_wins + k3_wins) / n_tested if n_tested > 0 else 0
    contiguous_rate = contiguous_count / k2_wins if k2_wins > 0 else 0

    mean_sil_k2 = float(np.mean(silhouette_k2s)) if silhouette_k2s else 0
    mean_sil_k3 = float(np.mean(silhouette_k3s)) if silhouette_k3s else 0

    if cluster_rate > 0.30:
        verdict = 'DISCRETE_CLUSTERS_DETECTED'
    elif cluster_rate > 0.10:
        verdict = 'CLUSTER_MARGINAL'
    else:
        verdict = 'CONTINUOUS_GRADIENT'

    print(f"    k=1 wins: {k1_wins}, k=2 wins: {k2_wins}, k=3 wins: {k3_wins}")
    print(f"    Cluster rate (sil>0.3): {cluster_rate:.1%}")
    print(f"    Contiguous clusters: {contiguous_count}/{k2_wins} ({contiguous_rate:.1%})")
    print(f"    Mean silhouette k=2: {mean_sil_k2:.4f}, k=3: {mean_sil_k3:.4f}")
    print(f"    Verdict: {verdict}")

    return rd({
        'n_tested': n_tested,
        'k1_wins': k1_wins,
        'k2_wins': k2_wins,
        'k3_wins': k3_wins,
        'cluster_rate': cluster_rate,
        'contiguous_clusters': contiguous_count,
        'contiguous_rate': contiguous_rate,
        'mean_silhouette_k2': mean_sil_k2,
        'mean_silhouette_k3': mean_sil_k3,
        'verdict': verdict,
    })


# ── Synthesis ────────────────────────────────────────────────

def synthesize(results):
    t1 = results['t1_suffix_piecewise']['verdict']
    t2 = results['t2_fl_reset_suffix']['verdict']
    t3 = results['t3_length_diversity']['verdict']
    t4 = results['t4_suffix_clustering']['verdict']

    t1_pos = t1 == 'DISCRETE_FRACTIONS_DETECTED'
    t2_pos = t2 == 'FL_RESET_SUFFIX_CHANGE'
    t3_pos = t3 == 'LENGTH_DIVERSITY_CORRELATED'
    t4_pos = t4 == 'DISCRETE_CLUSTERS_DETECTED'

    n_positive = sum([t1_pos, t2_pos, t3_pos, t4_pos])

    if t1_pos and t2_pos:
        overall = 'FRACTIONAL_DISTILLATION_SUPPORTED'
        interp = ('Suffix profiles show discrete breakpoints AND FL resets '
                  'co-occur with suffix changes - consistent with fractional '
                  'extraction producing distinct output products per line.')
    elif t2_pos and t3_pos:
        overall = 'FRACTION_BOUNDARIES_STRUCTURED'
        interp = ('FL resets mark output changes AND longer paragraphs have more '
                  'diverse outputs - fraction boundaries exist even without discrete '
                  'suffix breakpoints.')
    elif n_positive >= 2:
        overall = 'FRACTIONAL_EXTRACTION_SUGGESTIVE'
        interp = (f'{n_positive} of 4 tests positive - some evidence for fractional '
                  'extraction but not fully consistent.')
    elif t1 == 'SMOOTH_GRADIENT' and not t2_pos and not t4_pos:
        overall = 'OUTPUT_SPECIFICATION_GRADIENT_ONLY'
        interp = ('Suffix profiles follow smooth gradients without discrete steps. '
                  'C932 spec->exec interpretation holds. No evidence for fractional '
                  'extraction beyond existing constraints.')
    else:
        overall = 'CONTINUOUS_PROCESS_WITH_OUTPUT_SHIFT'
        interp = ('Suffix gradients are continuous, but some structure suggests '
                  'output specifications shift through the paragraph body - '
                  'more than pure spec->exec, less than discrete fractions.')

    return {
        'test_verdicts': {'t1': t1, 't2': t2, 't3': t3, 't4': t4},
        'n_positive': n_positive,
        'overall_verdict': overall,
        'interpretation': interp,
    }


# ── Main ─────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Phase 438 Extension: FRACTIONAL_LINE_TEST")
    print("=" * 70)

    print("\nLoading paragraphs...")
    paragraphs = load_paragraphs()
    print(f"  Total: {len(paragraphs)} paragraphs")
    print(f"  With 6+ body: {sum(1 for p in paragraphs if p['n_body'] >= MIN_BODY_PIECEWISE)}")
    print(f"  With 8+ body: {sum(1 for p in paragraphs if p['n_body'] >= MIN_BODY_CLUSTER)}")

    # Verify suffix classification
    all_suffixes = []
    for p in paragraphs:
        for ln in p['body']:
            all_suffixes.extend(ln['suffixes'])
    cats = Counter(classify_suffix(s) for s in all_suffixes)
    total = len(all_suffixes)
    print(f"\n  Suffix distribution: {dict(cats)}")
    print(f"  Terminal: {cats['TERMINAL']/total:.1%}, Connector: {cats['CONNECTOR']/total:.1%}, "
          f"Iterate: {cats['ITERATE']/total:.1%}, Bare: {cats['BARE']/total:.1%}")

    results = {
        'phase': 'FRACTIONAL_LINE_TEST',
        'total_paragraphs': len(paragraphs),
        'suffix_distribution': {k: rd(v / total) for k, v in cats.items()},
    }

    print("\n--- T1: Suffix Profile Piecewise vs Smooth ---")
    results['t1_suffix_piecewise'] = test_1_suffix_piecewise(paragraphs)

    print("\n--- T2: FL Reset × Suffix Change ---")
    results['t2_fl_reset_suffix'] = test_2_fl_reset_suffix(paragraphs)

    print("\n--- T3: Paragraph Length × Output Diversity ---")
    results['t3_length_diversity'] = test_3_length_diversity(paragraphs)

    print("\n--- T4: Within-Paragraph Suffix Clustering ---")
    results['t4_suffix_clustering'] = test_4_suffix_clustering(paragraphs)

    print("\n--- Synthesis ---")
    results['synthesis'] = synthesize(results)
    print(f"  Overall: {results['synthesis']['overall_verdict']}")
    print(f"  {results['synthesis']['interpretation']}")

    out_path = PROJECT / 'phases' / 'APPARATUS_TRANSITION_DETECTION' / 'results' / 'fractional_line_results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=lambda x: rd(x) if isinstance(x, float) else x)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
