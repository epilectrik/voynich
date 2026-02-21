"""
Phase 410: Folio Balance Characterization

Tests whether the bridge/dark-pipeline balance (C1146, r=-0.865) is a
structurally informative axis beyond section membership.

5-test battery:
  1. Balance vs Section (chi-square)
  2. Balance vs Dynamical Archetype (ARI + chi-square)
  3. Balance vs AXM Self-Transition (Kruskal-Wallis + within-section)
  4. Balance vs Kernel Profile (k/h/e Kruskal-Wallis)
  5. Balance vs Paragraph Count (Kruskal-Wallis + within-section)
"""
import json
import sys
import math
import os
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology


# ── Utility ──────────────────────────────────────────────────────────

def round_floats(obj, digits=4):
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [round_floats(x, digits) for x in obj]
    return obj


# ── Pure-Python Statistics ───────────────────────────────────────────

def chi_square_rxc(observed):
    """Chi-square test for RxC contingency table (list of lists).
    Returns chi2, p, df."""
    R = len(observed)
    C = len(observed[0])
    row_sums = [sum(row) for row in observed]
    col_sums = [sum(observed[r][c] for r in range(R)) for c in range(C)]
    total = sum(row_sums)
    if total == 0:
        return 0.0, 1.0, 0

    chi2 = 0.0
    for r in range(R):
        for c in range(C):
            exp = row_sums[r] * col_sums[c] / total
            if exp > 0:
                chi2 += (observed[r][c] - exp) ** 2 / exp

    df = (R - 1) * (C - 1)
    if df == 0:
        return chi2, 1.0, 0
    p = _chi2_sf(chi2, df)
    return chi2, p, df


def _chi2_sf(x, k):
    """Survival function for chi-square distribution (upper-tail p-value)."""
    if x <= 0:
        return 1.0
    return 1.0 - _regularized_gamma_p(k / 2.0, x / 2.0)


def _regularized_gamma_p(a, x):
    """Lower regularized incomplete gamma function P(a,x) via series."""
    if x < 0:
        return 0.0
    if x == 0:
        return 0.0
    if x < a + 1:
        return _gamma_series(a, x)
    else:
        return 1.0 - _gamma_cf(a, x)


def _gamma_series(a, x, max_iter=200):
    """Series expansion for P(a,x)."""
    ap = a
    s = 1.0 / a
    ds = s
    for _ in range(max_iter):
        ap += 1
        ds *= x / ap
        s += ds
        if abs(ds) < abs(s) * 1e-12:
            break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gamma_cf(a, x, max_iter=200):
    """Continued fraction for Q(a,x) = 1-P(a,x)."""
    b = x + 1 - a
    c = 1e30
    d = 1.0 / b
    h = d
    for i in range(1, max_iter + 1):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < 1e-30:
            d = 1e-30
        c = b + an / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        dl = d * c
        h *= dl
        if abs(dl - 1.0) < 1e-12:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def kruskal_wallis(groups):
    """Kruskal-Wallis H test. groups = list of lists of values.
    Returns H, p, df."""
    all_vals = []
    for i, g in enumerate(groups):
        for v in g:
            all_vals.append((v, i))
    all_vals.sort(key=lambda x: x[0])

    # Assign ranks (average ties)
    n = len(all_vals)
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n and all_vals[j][0] == all_vals[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    # Sum ranks per group
    group_rank_sums = defaultdict(float)
    group_ns = defaultdict(int)
    for idx, (val, gid) in enumerate(all_vals):
        group_rank_sums[gid] += ranks[idx]
        group_ns[gid] += 1

    K = len(groups)
    H = 0.0
    for gid in range(K):
        ni = group_ns[gid]
        if ni > 0:
            Ri = group_rank_sums[gid]
            H += (Ri ** 2) / ni
    H = (12.0 / (n * (n + 1))) * H - 3 * (n + 1)

    df = K - 1
    p = _chi2_sf(H, df) if df > 0 else 1.0
    return H, p, df


def adjusted_rand_index(labels_a, labels_b):
    """Compute ARI between two label vectors (same length)."""
    n = len(labels_a)
    if n == 0:
        return 0.0

    # Build contingency table
    contingency = defaultdict(int)
    a_counts = Counter(labels_a)
    b_counts = Counter(labels_b)
    for la, lb in zip(labels_a, labels_b):
        contingency[(la, lb)] += 1

    # Compute index components
    sum_comb_nij = sum(v * (v - 1) // 2 for v in contingency.values())
    sum_comb_ai = sum(v * (v - 1) // 2 for v in a_counts.values())
    sum_comb_bi = sum(v * (v - 1) // 2 for v in b_counts.values())
    comb_n = n * (n - 1) // 2

    expected = sum_comb_ai * sum_comb_bi / comb_n if comb_n > 0 else 0
    max_index = (sum_comb_ai + sum_comb_bi) / 2.0
    denom = max_index - expected
    if denom == 0:
        return 0.0 if sum_comb_nij == expected else 1.0
    return (sum_comb_nij - expected) / denom


def spearman_r(x, y):
    """Spearman rank correlation."""
    n = len(x)
    if n < 3:
        return 0.0, 1.0

    def rank_data(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n and vals[indexed[j]] == vals[indexed[i]]:
                j += 1
            avg = (i + j + 1) / 2.0
            for k in range(i, j):
                ranks[indexed[k]] = avg
            i = j
        return ranks

    rx = rank_data(x)
    ry = rank_data(y)

    mx = sum(rx) / n
    my = sum(ry) / n
    cov = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    sx = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    sy = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    if sx == 0 or sy == 0:
        return 0.0, 1.0

    rho = cov / (sx * sy)
    # t-test for significance
    t = rho * math.sqrt((n - 2) / (1 - rho ** 2)) if abs(rho) < 1 else float('inf')
    # Approximate p from t-distribution using normal for n>20
    p = 2 * (1 - _normal_cdf(abs(t))) if n > 20 else 1.0
    return rho, p


def _normal_cdf(x):
    """Standard normal CDF approximation (Abramowitz & Stegun)."""
    if x < -8:
        return 0.0
    if x > 8:
        return 1.0
    t = 1.0 / (1.0 + 0.2316419 * abs(x))
    d = 0.3989422804014327
    p = d * math.exp(-x * x / 2.0) * t * (
        0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
    return 1.0 - p if x > 0 else p


def eta_squared(groups):
    """Eta-squared: fraction of variance explained by group membership."""
    all_vals = [v for g in groups for v in g]
    n = len(all_vals)
    if n == 0:
        return 0.0
    grand_mean = sum(all_vals) / n
    ss_total = sum((v - grand_mean) ** 2 for v in all_vals)
    if ss_total == 0:
        return 0.0
    ss_between = sum(len(g) * (sum(g) / len(g) - grand_mean) ** 2
                     for g in groups if len(g) > 0)
    return ss_between / ss_total


# ── Section assignment ───────────────────────────────────────────────

def get_section(folio):
    """Map folio to Currier B section."""
    num = int(''.join(c for c in folio if c.isdigit()))
    if 74 <= num <= 84:
        return 'BIO'
    elif 26 <= num <= 56:
        return 'HERBAL_B'
    elif 57 <= num <= 67:
        return 'PHARMA'
    elif num >= 85:
        return 'RECIPE_B'
    else:
        return 'OTHER'


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load all data sources and compute per-folio balance metrics."""
    tx = Transcript()
    morph = Morphology()

    # Load dark pipeline + bridge sets
    with open(ROOT / 'data' / 'dark_pipeline_middles.json') as f:
        dp_data = json.load(f)
    dark_set = set(dp_data['middles'])

    with open(ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json') as f:
        bridge_data = json.load(f)
    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])

    # Load archetype labels (72 folios)
    with open(ROOT / 'phases' / 'FOLIO_MACRO_AUTOMATON_DECOMPOSITION' / 'results' / 'folio_macro_decomposition.json') as f:
        macro_data = json.load(f)
    archetype_labels = macro_data['t2_archetype_discovery']['folio_labels']

    # Load AXM per-folio data (72 folios)
    with open(ROOT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' / 'axm_residual_decomposition.json') as f:
        axm_data = json.load(f)
    folio_metrics = axm_data['folio_data']

    # Load paragraph census
    with open(ROOT / 'phases' / 'FOLIO_PARAGRAPH_ARCHITECTURE' / 'results' / 'folio_paragraph_census.json') as f:
        census = json.load(f)
    para_counts = {e['folio']: e['paragraph_count'] for e in census['folios']}

    # Single B-pass: compute per-folio bridge/dark/kernel counts
    folio_bridge = Counter()
    folio_dark = Counter()
    folio_total = Counter()
    folio_kernels = defaultdict(lambda: Counter())  # folio -> {k:n, h:n, e:n}

    KERNEL_CHARS = {'k', 'h', 'e'}

    for t in tx.currier_b():
        w = t.word.strip()
        if not w or '*' in w:
            continue
        folio_total[t.folio] += 1
        m = morph.extract(w)
        if m.middle:
            if m.middle in bridge_set:
                folio_bridge[t.folio] += 1
            if m.middle in dark_set:
                folio_dark[t.folio] += 1
            # Kernel extraction
            for ch in m.middle:
                if ch in KERNEL_CHARS:
                    folio_kernels[t.folio][ch] += 1

    # Build unified per-folio records
    folios = sorted(folio_total.keys())
    records = {}
    for f in folios:
        total = folio_total[f]
        br = folio_bridge[f] / total if total else 0
        dr = folio_dark[f] / total if total else 0
        ratio = dr / br if br > 0 else 0

        if ratio < 0.063:
            balance = 'BRIDGE_DOMINANT'
        elif ratio > 0.110:
            balance = 'DARK_DOMINANT'
        else:
            balance = 'BALANCED'

        records[f] = {
            'section': get_section(f),
            'bridge_count': folio_bridge[f],
            'dark_count': folio_dark[f],
            'total': total,
            'bridge_rate': br,
            'dark_rate': dr,
            'ratio': ratio,
            'balance': balance,
            'archetype': archetype_labels.get(f),
            'axm_self': folio_metrics[f]['axm_self'] if f in folio_metrics else None,
            'c1017_residual': folio_metrics[f].get('c1017_residual') if f in folio_metrics else None,
            'paragraph_count': para_counts.get(f),
            'kernel_k': folio_kernels[f].get('k', 0),
            'kernel_h': folio_kernels[f].get('h', 0),
            'kernel_e': folio_kernels[f].get('e', 0),
        }

    return {
        'records': records,
        'folios': folios,
        'n_dark_middles': len(dark_set),
        'n_bridge_middles': len(bridge_set),
        'n_folios': len(folios),
    }


# ── Test 1: Balance vs Section ───────────────────────────────────────

def test1_balance_vs_section(data):
    """Chi-square test of balance × section independence."""
    records = data['records']
    balance_order = ['BRIDGE_DOMINANT', 'BALANCED', 'DARK_DOMINANT']
    sections = ['HERBAL_B', 'BIO', 'PHARMA', 'RECIPE_B']

    # Cross-tabulate
    table = {b: {s: 0 for s in sections} for b in balance_order}
    for f, rec in records.items():
        if rec['section'] in sections:
            table[rec['balance']][rec['section']] += 1

    # Build observed matrix for chi-square
    observed = [[table[b][s] for s in sections] for b in balance_order]
    chi2, p, df = chi_square_rxc(observed)

    # Per-section balance distribution
    section_profiles = {}
    for s in sections:
        col_total = sum(table[b][s] for b in balance_order)
        if col_total > 0:
            section_profiles[s] = {
                b: {'count': table[b][s], 'pct': table[b][s] / col_total}
                for b in balance_order
            }
            section_profiles[s]['n'] = col_total

    verdict = 'SECTION_STRUCTURED' if p < 0.05 else 'SECTION_INDEPENDENT'

    print(f"\n  Test 1: Balance vs Section")
    print(f"    Chi-square = {chi2:.3f}, df = {df}, p = {p:.4f}")
    print(f"    Verdict: {verdict}")
    for s in sections:
        prof = section_profiles.get(s, {})
        n = prof.get('n', 0)
        bd = prof.get('BRIDGE_DOMINANT', {}).get('count', 0)
        ba = prof.get('BALANCED', {}).get('count', 0)
        dd = prof.get('DARK_DOMINANT', {}).get('count', 0)
        print(f"    {s:10}: BD={bd} BAL={ba} DD={dd} (n={n})")

    return {
        'contingency': table,
        'chi2': chi2,
        'p': p,
        'df': df,
        'section_profiles': section_profiles,
        'verdict': verdict,
    }


# ── Test 2: Balance vs Dynamical Archetype ───────────────────────────

def test2_balance_vs_archetype(data):
    """ARI and chi-square: balance labels vs archetype labels."""
    records = data['records']

    # Only folios with archetype assignments
    balance_labels = []
    arch_labels = []
    for f, rec in records.items():
        if rec['archetype'] is not None:
            balance_labels.append(rec['balance'])
            arch_labels.append(rec['archetype'])

    n = len(balance_labels)
    ari = adjusted_rand_index(balance_labels, arch_labels)

    # Chi-square on balance × archetype
    balance_order = ['BRIDGE_DOMINANT', 'BALANCED', 'DARK_DOMINANT']
    arch_ids = sorted(set(arch_labels))
    table = {b: {a: 0 for a in arch_ids} for b in balance_order}
    for bl, al in zip(balance_labels, arch_labels):
        table[bl][al] += 1

    observed = [[table[b][a] for a in arch_ids] for b in balance_order]
    chi2, p, df = chi_square_rxc(observed)

    # Per-archetype balance distribution
    arch_profiles = {}
    for a in arch_ids:
        col_total = sum(table[b][a] for b in balance_order)
        if col_total > 0:
            arch_profiles[a] = {
                b: table[b][a] for b in balance_order
            }
            arch_profiles[a]['n'] = col_total

    if ari > 0.10 and p < 0.05:
        verdict = 'ARCHETYPE_ALIGNED'
    elif ari > 0.03:
        verdict = 'ARCHETYPE_WEAK'
    else:
        verdict = 'ARCHETYPE_ORTHOGONAL'

    print(f"\n  Test 2: Balance vs Archetype")
    print(f"    n = {n} folios with archetype assignments")
    print(f"    ARI = {ari:.4f}")
    print(f"    Chi-square = {chi2:.3f}, df = {df}, p = {p:.4f}")
    print(f"    Verdict: {verdict}")
    for a in arch_ids:
        prof = arch_profiles.get(a, {})
        nn = prof.get('n', 0)
        print(f"    Arch {a}: BD={prof.get('BRIDGE_DOMINANT', 0)} "
              f"BAL={prof.get('BALANCED', 0)} DD={prof.get('DARK_DOMINANT', 0)} (n={nn})")

    return {
        'n': n,
        'ari': ari,
        'chi2': chi2,
        'p': p,
        'df': df,
        'arch_profiles': arch_profiles,
        'verdict': verdict,
    }


# ── Test 3: Balance vs AXM Self-Transition ───────────────────────────

def test3_balance_vs_axm(data):
    """Kruskal-Wallis: AXM self-transition across balance groups + within-section."""
    records = data['records']
    balance_order = ['BRIDGE_DOMINANT', 'BALANCED', 'DARK_DOMINANT']

    # Global comparison
    groups = {b: [] for b in balance_order}
    for f, rec in records.items():
        if rec['axm_self'] is not None:
            groups[rec['balance']].append(rec['axm_self'])

    group_lists = [groups[b] for b in balance_order]
    H, p, df = kruskal_wallis(group_lists)

    # Group means
    group_stats = {}
    for b in balance_order:
        vals = groups[b]
        if vals:
            group_stats[b] = {
                'n': len(vals),
                'mean': sum(vals) / len(vals),
                'median': sorted(vals)[len(vals) // 2],
            }

    eta2 = eta_squared(group_lists)

    # Within-section analysis (C1103 confound control)
    sections = ['HERBAL_B', 'BIO', 'RECIPE_B']  # PHARMA too small
    within_section = {}
    for s in sections:
        s_groups = {b: [] for b in balance_order}
        for f, rec in records.items():
            if rec['axm_self'] is not None and rec['section'] == s:
                s_groups[rec['balance']].append(rec['axm_self'])

        # Only test if ≥2 non-empty groups with ≥2 values
        non_empty = [s_groups[b] for b in balance_order if len(s_groups[b]) >= 2]
        if len(non_empty) >= 2:
            sH, sp, sdf = kruskal_wallis(non_empty)
            within_section[s] = {
                'H': sH, 'p': sp,
                'group_ns': {b: len(s_groups[b]) for b in balance_order},
            }

    # Spearman: ratio vs AXM (continuous)
    ratios = []
    axm_vals = []
    for f, rec in records.items():
        if rec['axm_self'] is not None:
            ratios.append(rec['ratio'])
            axm_vals.append(rec['axm_self'])
    rho, rho_p = spearman_r(ratios, axm_vals)

    verdict = 'AXM_DIFFERENTIATED' if p < 0.05 else 'AXM_UNIFORM'

    print(f"\n  Test 3: Balance vs AXM Self-Transition")
    print(f"    Kruskal-Wallis H = {H:.3f}, p = {p:.4f}, eta² = {eta2:.4f}")
    print(f"    Spearman(ratio, AXM) rho = {rho:.4f}, p = {rho_p:.4f}")
    for b in balance_order:
        s = group_stats.get(b, {})
        print(f"    {b:18}: n={s.get('n', 0)}, mean={s.get('mean', 0):.4f}")
    print(f"    Within-section controls:")
    for s, ws in within_section.items():
        print(f"      {s}: H={ws['H']:.3f}, p={ws['p']:.4f}, ns={ws['group_ns']}")
    print(f"    Verdict: {verdict}")

    return {
        'H': H,
        'p': p,
        'df': df,
        'eta2': eta2,
        'group_stats': group_stats,
        'within_section': within_section,
        'spearman_rho': rho,
        'spearman_p': rho_p,
        'verdict': verdict,
    }


# ── Test 4: Balance vs Kernel Profile ────────────────────────────────

def test4_balance_vs_kernel(data):
    """Kruskal-Wallis per kernel (k, h, e fractions) across balance groups."""
    records = data['records']
    balance_order = ['BRIDGE_DOMINANT', 'BALANCED', 'DARK_DOMINANT']

    # Compute kernel fractions per folio
    kernel_fracs = {}
    for f, rec in records.items():
        ktotal = rec['kernel_k'] + rec['kernel_h'] + rec['kernel_e']
        if ktotal > 0:
            kernel_fracs[f] = {
                'k_frac': rec['kernel_k'] / ktotal,
                'h_frac': rec['kernel_h'] / ktotal,
                'e_frac': rec['kernel_e'] / ktotal,
            }

    results = {}
    for kern in ['k_frac', 'h_frac', 'e_frac']:
        groups = {b: [] for b in balance_order}
        for f, rec in records.items():
            if f in kernel_fracs:
                groups[rec['balance']].append(kernel_fracs[f][kern])

        group_lists = [groups[b] for b in balance_order]
        H, p, df = kruskal_wallis(group_lists)
        eta2 = eta_squared(group_lists)

        group_means = {}
        for b in balance_order:
            vals = groups[b]
            if vals:
                group_means[b] = {'n': len(vals), 'mean': sum(vals) / len(vals)}

        results[kern] = {
            'H': H, 'p': p, 'eta2': eta2,
            'group_means': group_means,
        }

    # Within-section control for the strongest kernel signal
    strongest = min(results.keys(), key=lambda k: results[k]['p'])
    sections = ['HERBAL_B', 'BIO', 'RECIPE_B']
    within_section = {}
    for s in sections:
        s_groups = {b: [] for b in balance_order}
        for f, rec in records.items():
            if f in kernel_fracs and rec['section'] == s:
                s_groups[rec['balance']].append(kernel_fracs[f][strongest])
        non_empty = [s_groups[b] for b in balance_order if len(s_groups[b]) >= 2]
        if len(non_empty) >= 2:
            sH, sp, sdf = kruskal_wallis(non_empty)
            within_section[s] = {'H': sH, 'p': sp}

    any_sig = any(results[k]['p'] < 0.05 for k in results)
    verdict = 'KERNEL_DIFFERENTIATED' if any_sig else 'KERNEL_UNIFORM'

    print(f"\n  Test 4: Balance vs Kernel Profile")
    for kern in ['k_frac', 'h_frac', 'e_frac']:
        r = results[kern]
        print(f"    {kern}: H={r['H']:.3f}, p={r['p']:.4f}, eta²={r['eta2']:.4f}")
        for b in balance_order:
            gm = r['group_means'].get(b, {})
            print(f"      {b:18}: n={gm.get('n', 0)}, mean={gm.get('mean', 0):.4f}")
    print(f"    Within-section ({strongest}):")
    for s, ws in within_section.items():
        print(f"      {s}: H={ws['H']:.3f}, p={ws['p']:.4f}")
    print(f"    Verdict: {verdict}")

    return {
        'per_kernel': results,
        'within_section_strongest': {
            'kernel': strongest,
            'sections': within_section,
        },
        'verdict': verdict,
    }


# ── Test 5: Balance vs Paragraph Count ───────────────────────────────

def test5_balance_vs_paragraphs(data):
    """Kruskal-Wallis: paragraph count across balance groups + within-section."""
    records = data['records']
    balance_order = ['BRIDGE_DOMINANT', 'BALANCED', 'DARK_DOMINANT']

    groups = {b: [] for b in balance_order}
    for f, rec in records.items():
        if rec['paragraph_count'] is not None:
            groups[rec['balance']].append(rec['paragraph_count'])

    group_lists = [groups[b] for b in balance_order]
    H, p, df = kruskal_wallis(group_lists)
    eta2 = eta_squared(group_lists)

    group_stats = {}
    for b in balance_order:
        vals = groups[b]
        if vals:
            group_stats[b] = {
                'n': len(vals),
                'mean': sum(vals) / len(vals),
                'median': sorted(vals)[len(vals) // 2],
            }

    # Within-section
    sections = ['HERBAL_B', 'BIO', 'RECIPE_B']
    within_section = {}
    for s in sections:
        s_groups = {b: [] for b in balance_order}
        for f, rec in records.items():
            if rec['paragraph_count'] is not None and rec['section'] == s:
                s_groups[rec['balance']].append(rec['paragraph_count'])
        non_empty = [s_groups[b] for b in balance_order if len(s_groups[b]) >= 2]
        if len(non_empty) >= 2:
            sH, sp, sdf = kruskal_wallis(non_empty)
            within_section[s] = {
                'H': sH, 'p': sp,
                'group_ns': {b: len(s_groups[b]) for b in balance_order},
            }

    # Spearman: ratio vs paragraph count
    ratios = []
    para_vals = []
    for f, rec in records.items():
        if rec['paragraph_count'] is not None:
            ratios.append(rec['ratio'])
            para_vals.append(rec['paragraph_count'])
    rho, rho_p = spearman_r(ratios, para_vals)

    verdict = 'PARAGRAPH_DIFFERENTIATED' if p < 0.05 else 'PARAGRAPH_UNIFORM'

    print(f"\n  Test 5: Balance vs Paragraph Count")
    print(f"    Kruskal-Wallis H = {H:.3f}, p = {p:.4f}, eta² = {eta2:.4f}")
    print(f"    Spearman(ratio, para_count) rho = {rho:.4f}, p = {rho_p:.4f}")
    for b in balance_order:
        s = group_stats.get(b, {})
        print(f"    {b:18}: n={s.get('n', 0)}, mean={s.get('mean', 0):.1f}, "
              f"median={s.get('median', 0)}")
    print(f"    Within-section controls:")
    for s, ws in within_section.items():
        print(f"      {s}: H={ws['H']:.3f}, p={ws['p']:.4f}, ns={ws['group_ns']}")
    print(f"    Verdict: {verdict}")

    return {
        'H': H,
        'p': p,
        'df': df,
        'eta2': eta2,
        'group_stats': group_stats,
        'within_section': within_section,
        'spearman_rho': rho,
        'spearman_p': rho_p,
        'verdict': verdict,
    }


# ── Synthesis ────────────────────────────────────────────────────────

def synthesize(results):
    """Combine test verdicts into overall assessment."""
    verdicts = {f'test{i}': results[f'test{i}']['verdict'] for i in range(1, 6)}

    differentiated_count = sum(1 for v in verdicts.values()
                               if v not in ('SECTION_INDEPENDENT', 'ARCHETYPE_ORTHOGONAL',
                                            'AXM_UNIFORM', 'KERNEL_UNIFORM',
                                            'PARAGRAPH_UNIFORM'))

    if differentiated_count >= 3:
        overall = 'BALANCE_IS_STRUCTURAL_AXIS'
    elif differentiated_count >= 1:
        overall = 'BALANCE_PARTIALLY_INFORMATIVE'
    else:
        overall = 'BALANCE_IS_EPIPHENOMENAL'

    # Special flag: archetype alignment
    arch_flag = ''
    if verdicts['test2'] == 'ARCHETYPE_ALIGNED':
        arch_flag = ' (ARCHETYPE_PENETRATION)'
    elif verdicts['test2'] == 'ARCHETYPE_WEAK':
        arch_flag = ' (ARCHETYPE_TRACE)'

    findings = []
    if verdicts['test1'] == 'SECTION_STRUCTURED':
        findings.append('Balance distribution varies by section')
    if verdicts['test2'] in ('ARCHETYPE_ALIGNED', 'ARCHETYPE_WEAK'):
        ari = results['test2']['ari']
        findings.append(f'Balance partially predicts dynamical archetype (ARI={ari:.4f})')
    if verdicts['test3'] == 'AXM_DIFFERENTIATED':
        rho = results['test3']['spearman_rho']
        findings.append(f'Dark/bridge ratio correlates with AXM forgiveness (rho={rho:.4f})')
    if verdicts['test4'] == 'KERNEL_DIFFERENTIATED':
        findings.append('Balance groups have different kernel profiles')
    if verdicts['test5'] == 'PARAGRAPH_DIFFERENTIATED':
        rho = results['test5']['spearman_rho']
        findings.append(f'Dark/bridge ratio correlates with paragraph count (rho={rho:.4f})')

    summary = (f"{differentiated_count}/5 tests show balance-dependent variation. "
               f"Overall: {overall}{arch_flag}. "
               f"Section confound: {'present' if verdicts['test1'] == 'SECTION_STRUCTURED' else 'absent'}.")

    verdicts['overall'] = overall + arch_flag
    verdicts['summary'] = summary
    verdicts['findings'] = findings
    verdicts['differentiated_count'] = differentiated_count

    print(f"\n{'='*60}")
    print(f"  SYNTHESIS")
    print(f"{'='*60}")
    print(f"  {summary}")
    for finding in findings:
        print(f"    - {finding}")

    return verdicts


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 410: Folio Balance Characterization")
    print("=" * 60)

    data = load_data()

    # Validation
    balance_counts = Counter(r['balance'] for r in data['records'].values())
    print(f"\n  Folios: {data['n_folios']}")
    print(f"  Dark pipeline MIDDLEs: {data['n_dark_middles']}")
    print(f"  Bridge MIDDLEs: {data['n_bridge_middles']}")
    print(f"  Balance split: BD={balance_counts.get('BRIDGE_DOMINANT', 0)} "
          f"BAL={balance_counts.get('BALANCED', 0)} "
          f"DD={balance_counts.get('DARK_DOMINANT', 0)}")

    results = {}
    results['test1'] = test1_balance_vs_section(data)
    results['test2'] = test2_balance_vs_archetype(data)
    results['test3'] = test3_balance_vs_axm(data)
    results['test4'] = test4_balance_vs_kernel(data)
    results['test5'] = test5_balance_vs_paragraphs(data)

    verdicts = synthesize(results)

    # Output
    output = round_floats({
        'test1': results['test1'],
        'test2': results['test2'],
        'test3': results['test3'],
        'test4': results['test4'],
        'test5': results['test5'],
        'verdicts': verdicts,
        'metadata': {
            'phase': 'FOLIO_BALANCE_CHARACTERIZATION',
            'phase_number': 410,
            'script': 'folio_balance_characterization.py',
            'n_folios': data['n_folios'],
            'n_dark_middles': data['n_dark_middles'],
            'n_bridge_middles': data['n_bridge_middles'],
            'balance_split': dict(balance_counts),
        },
    })

    out_path = ROOT / 'phases' / 'FOLIO_BALANCE_CHARACTERIZATION' / 'results' / 'folio_balance_characterization.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    size = os.path.getsize(out_path)
    print(f"\n  Output: {out_path}")
    print(f"  Size: {size:,} bytes")


if __name__ == '__main__':
    main()
