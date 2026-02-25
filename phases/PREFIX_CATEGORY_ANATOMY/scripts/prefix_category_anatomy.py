#!/usr/bin/env python3
"""Phase 458: PREFIX_CATEGORY_ANATOMY

8-test battery probing the PREFIX x 8-category relationship in Currier B.
Primary question: do ok and ot select different operational categories?

Tests:
  T1: Full PREFIX x Category Contingency Table (primary deliverable)
  T2: ok vs ot Category Divergence (primary question)
  T3: ch/sh Category Identity in B (control -- must match C1268)
  T4: qo Category Purity (extend C1277)
  T5: da vs sa Category Comparison (extend C1015)
  T6: Base-Group Category Tautology Decomposition (CRITICAL gate)
  T7: BARE PREFIX Category Profile
  T8: Base-Group Category Alignment (extend C1219)
"""

import json
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict
from math import log2

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

# ============================================================
# Constants
# ============================================================

N_PERM = 1000
SEED = 42
BONFERRONI_P = 0.05 / 8  # 0.00625

CATEGORIES = ['CONTAINMENT', 'FLOW', 'MARKING', 'MONITORING',
              'OPERATION', 'STAGING', 'THERMAL', 'TRANSITION']

# --- Category assignment (from Phase 452/454) ---
GLOSS_TO_CATEGORY = {
    'heat': 'THERMAL', 'fire': 'THERMAL', 'cool': 'THERMAL',
    'sustain': 'THERMAL', 'pulse': 'THERMAL', 'steady': 'THERMAL',
    'extended': 'THERMAL', 'deep': 'THERMAL', 'long': 'THERMAL',
    'overnight': 'THERMAL',
    'seal': 'CONTAINMENT', 'hold': 'CONTAINMENT', 'lock': 'CONTAINMENT',
    'bind': 'CONTAINMENT', 'bond': 'CONTAINMENT', 'rigid': 'CONTAINMENT',
    'firm': 'CONTAINMENT', 'dense': 'CONTAINMENT',
    'transfer': 'FLOW', 'gather': 'FLOW', 'discharge': 'FLOW',
    'release': 'FLOW', 'vent': 'FLOW', 'route': 'FLOW',
    'portion': 'FLOW', 'input': 'FLOW', 'intake': 'FLOW',
    'watch': 'MONITORING', 'check': 'MONITORING', 'verify': 'MONITORING',
    'confirm': 'MONITORING', 'scan': 'MONITORING', 'measure': 'MONITORING',
    'control': 'MONITORING', 'regulate': 'MONITORING',
    'work': 'OPERATION', 'operate': 'OPERATION', 'batch': 'OPERATION',
    'pound': 'OPERATION', 'strip': 'OPERATION', 'exact': 'OPERATION',
    'precise': 'OPERATION', 'hard': 'OPERATION', 'wide': 'OPERATION',
    'start': 'TRANSITION', 'open': 'TRANSITION', 'close': 'TRANSITION',
    'end': 'TRANSITION', 'finish': 'TRANSITION', 'complete': 'TRANSITION',
    'finalize': 'TRANSITION', 'yield': 'TRANSITION', 'final': 'TRANSITION',
    'stand': 'TRANSITION', 'settle': 'TRANSITION', 'set': 'TRANSITION',
    'halt': 'TRANSITION',
    'frame': 'STAGING', 'step': 'STAGING', 'iterate': 'STAGING',
    'sequence': 'STAGING', 'continue': 'STAGING', 'repeat': 'STAGING',
    'cycle': 'STAGING', 'loop': 'STAGING', 'path': 'STAGING',
    'mark': 'MARKING', 'flag': 'MARKING', 'note': 'MARKING',
    'pause': 'MARKING', 'diagram': 'MARKING', 'hazard': 'MARKING',
    'danger': 'MARKING', 'link': 'MARKING', 'adjust': 'MARKING',
}

ATOM_GLOSSES = {
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'halt', 'a': 'yield', 'm': 'final',
    'd': 'mark', 't': 'transfer', 'c': 'adjust', 'p': 'pause',
    'f': 'flag', 's': 'sequence', 'g': 'complete', 'o': 'work',
    'l': 'frame', 'r': 'input',
}
ATOM_TO_CATEGORY = {a: GLOSS_TO_CATEGORY[g] for a, g in ATOM_GLOSSES.items()}

# --- Base-group classification (C1219) ---
PREFIX_TO_BASE = {
    'da': 'a', 'ka': 'a', 'sa': 'a', 'ta': 'a',
    'qo': 'o', 'so': 'o', 'do': 'o', 'ko': 'o', 'po': 'o', 'to': 'o',
    'ch': 'h', 'sh': 'h', 'pch': 'h', 'tch': 'h', 'dch': 'h', 'lch': 'h',
    'lsh': 'h', 'kch': 'h', 'fch': 'h', 'rch': 'h', 'sch': 'h',
    'ke': 'e', 'te': 'e', 'se': 'e', 'de': 'e', 'pe': 'e',
    'ok': 'k', 'lk': 'k', 'yk': 'k',
    'ot': 't', 'ct': 't',
    'ar': 'r', 'or': 'r',
    'al': 'l', 'ol': 'l',
    'BARE': 'BARE',
}

# Expected category alignment from C1219 functional domains
BASE_EXPECTED_CATEGORIES = {
    'a': ['STAGING'],
    'o': ['THERMAL', 'FLOW'],
    'h': ['CONTAINMENT', 'TRANSITION'],
    'e': ['TRANSITION'],
    'k': ['STAGING', 'CONTAINMENT'],
    't': ['STAGING', 'CONTAINMENT'],
    'r': ['STAGING'],
    # l-base is Mixed per C1219, excluded from alignment
}

MIN_N = 30  # Minimum tokens per PREFIX for contingency table


# ============================================================
# Utilities
# ============================================================

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


def auto_assign_category(atoms_str):
    """Assign category via plurality vote over atoms."""
    if not atoms_str:
        return None
    votes = Counter()
    for atom in atoms_str:
        cat = ATOM_TO_CATEGORY.get(atom)
        if cat:
            votes[cat] += 1
    if not votes:
        return None
    max_count = max(votes.values())
    winners = [c for c, v in votes.items() if v == max_count]
    return sorted(winners)[0]


def build_category_map():
    """Build mid_to_category dict from middle_dictionary.json."""
    with open(ROOT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
        mid_dict = json.load(f)['middles']
    mid_to_cat = {}
    for mid, minfo in mid_dict.items():
        gloss = minfo.get('gloss')
        if gloss and gloss in GLOSS_TO_CATEGORY:
            mid_to_cat[mid] = GLOSS_TO_CATEGORY[gloss]
    for mid, minfo in mid_dict.items():
        if mid in mid_to_cat:
            continue
        atoms_str = minfo.get('autogloss_atoms', '')
        if atoms_str:
            cat = auto_assign_category(atoms_str)
            if cat:
                mid_to_cat[mid] = cat
    return mid_to_cat


def entropy_from_counts(counts):
    """Shannon entropy in bits from a list of counts."""
    total = sum(counts)
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            h -= p * log2(p)
    return h


def conditional_entropy(joint_counts):
    """H(Y|X) from a dict {x: Counter(y: count)}."""
    total = sum(sum(c.values()) for c in joint_counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for x, ycounts in joint_counts.items():
        nx = sum(ycounts.values())
        if nx == 0:
            continue
        px = nx / total
        hx = entropy_from_counts(list(ycounts.values()))
        h += px * hx
    return h


def cramers_v(table):
    """Cramer's V from a 2D numpy array contingency table."""
    n = table.sum()
    if n == 0:
        return 0.0
    chi2 = stats.chi2_contingency(table)[0]
    k = min(table.shape) - 1
    if k == 0:
        return 0.0
    return np.sqrt(chi2 / (n * k))


def jsd(p, q):
    """Jensen-Shannon divergence between two distributions (as arrays)."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    p = p / p.sum() if p.sum() > 0 else p
    q = q / q.sum() if q.sum() > 0 else q
    m = 0.5 * (p + q)
    d = 0.0
    for i in range(len(p)):
        if p[i] > 0 and m[i] > 0:
            d += 0.5 * p[i] * log2(p[i] / m[i])
        if q[i] > 0 and m[i] > 0:
            d += 0.5 * q[i] * log2(q[i] / m[i])
    return d


def build_contingency_2x8(cats_a, cats_b):
    """Build 2x8 contingency table from two lists of category labels."""
    table = np.zeros((2, 8), dtype=int)
    for c in cats_a:
        if c in CATEGORIES:
            table[0, CATEGORIES.index(c)] += 1
    for c in cats_b:
        if c in CATEGORIES:
            table[1, CATEGORIES.index(c)] += 1
    return table


def chi2_test_safe(table):
    """Chi-squared test with fallback for small expected counts."""
    # Remove all-zero rows/cols
    row_mask = table.sum(axis=1) > 0
    col_mask = table.sum(axis=0) > 0
    filtered = table[np.ix_(row_mask, col_mask)]
    if filtered.shape[0] < 2 or filtered.shape[1] < 2:
        return 0.0, 1.0, 0
    chi2, p, dof, _ = stats.chi2_contingency(filtered)
    return chi2, p, dof


# ============================================================
# Data Loading
# ============================================================

def load_data():
    """Load B tokens with prefix, middle, category, and base-group."""
    tx = Transcript()
    morph = Morphology()
    mid_to_cat = build_category_map()

    tokens = []
    for tok in tx.currier_b():
        w = tok.word
        if not w.strip() or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle or ''
        pfx = m.prefix or ''
        cat = mid_to_cat.get(mid)
        if not cat and mid:
            cat = auto_assign_category(mid)
        if not cat:
            continue  # Skip uncategorizable tokens
        pfx_label = pfx if pfx else 'BARE'
        base = PREFIX_TO_BASE.get(pfx_label)
        if base is None:
            # Unknown prefix -- assign to 'OTHER' base
            base = 'OTHER'
        tokens.append({
            'prefix': pfx_label,
            'middle': mid,
            'category': cat,
            'base': base,
            'folio': tok.folio,
        })
    return tokens


# ============================================================
# Test Functions
# ============================================================

def test_1_full_contingency(tokens):
    """T1: Full PREFIX x Category contingency table."""
    print("\n=== T1: Full PREFIX x Category Contingency Table ===")

    # Count tokens per prefix
    pfx_counts = Counter(t['prefix'] for t in tokens)
    qualifying = sorted([p for p, n in pfx_counts.items() if n >= MIN_N])
    excluded = sorted([p for p, n in pfx_counts.items() if n < MIN_N])

    print(f"  Qualifying PREFIXes (N>={MIN_N}): {len(qualifying)}")
    print(f"  Excluded (N<{MIN_N}): {len(excluded)} ({excluded})")

    # Build contingency table
    pfx_to_idx = {p: i for i, p in enumerate(qualifying)}
    table = np.zeros((len(qualifying), 8), dtype=int)
    for t in tokens:
        if t['prefix'] in pfx_to_idx:
            table[pfx_to_idx[t['prefix']], CATEGORIES.index(t['category'])] += 1

    # Chi-squared and Cramer's V
    chi2, p, dof = chi2_test_safe(table)
    v = cramers_v(table)
    n_tokens = int(table.sum())

    print(f"  N tokens: {n_tokens}")
    print(f"  chi2={chi2:.1f}, dof={dof}, p={p:.4e}, V={v:.3f}")

    # Per-PREFIX dominant category and purity
    pfx_profiles = {}
    for i, pfx in enumerate(qualifying):
        row = table[i]
        total = row.sum()
        if total == 0:
            continue
        props = row / total
        dominant = CATEGORIES[np.argmax(row)]
        purity = float(np.max(props))
        pfx_profiles[pfx] = {
            'n': int(total),
            'dominant': dominant,
            'purity': round(purity, 3),
            'profile': {CATEGORIES[j]: round(float(props[j]), 4) for j in range(8)},
        }

    # Print top profiles
    print("  Per-PREFIX profiles:")
    for pfx in qualifying:
        if pfx in pfx_profiles:
            p_info = pfx_profiles[pfx]
            print(f"    {pfx:6s} (n={p_info['n']:5d}): {p_info['dominant']:12s} "
                  f"purity={p_info['purity']:.3f}")

    v_pass = p < BONFERRONI_P and v >= 0.10
    vrd = 'PASS' if v_pass else ('WEAK' if p < 0.05 else 'FAIL')
    print(f"  Verdict: {vrd}")

    return {
        'test': 'T1_full_contingency',
        'n_qualifying': len(qualifying),
        'n_excluded': len(excluded),
        'n_tokens': n_tokens,
        'chi2': chi2, 'p': p, 'dof': dof, 'V': v,
        'prefix_profiles': pfx_profiles,
        'qualifying_prefixes': qualifying,
        'verdict': vrd,
    }


def test_2_ok_ot(tokens):
    """T2: ok vs ot category divergence."""
    print("\n=== T2: ok vs ot Category Divergence ===")

    ok_cats = [t['category'] for t in tokens if t['prefix'] == 'ok']
    ot_cats = [t['category'] for t in tokens if t['prefix'] == 'ot']

    print(f"  ok tokens: {len(ok_cats)}, ot tokens: {len(ot_cats)}")

    table = build_contingency_2x8(ok_cats, ot_cats)
    chi2, p, dof = chi2_test_safe(table)
    v = cramers_v(table)

    # JSD
    ok_dist = table[0] / table[0].sum() if table[0].sum() > 0 else table[0]
    ot_dist = table[1] / table[1].sum() if table[1].sum() > 0 else table[1]
    j = jsd(ok_dist, ot_dist)

    # Per-category enrichment
    enrichment = {}
    for i, cat in enumerate(CATEGORIES):
        ok_frac = ok_dist[i] if table[0].sum() > 0 else 0
        ot_frac = ot_dist[i] if table[1].sum() > 0 else 0
        enrichment[cat] = {
            'ok': round(float(ok_frac), 4),
            'ot': round(float(ot_frac), 4),
            'ratio': round(float(ok_frac / ot_frac), 2) if ot_frac > 0 else None,
        }

    print(f"  chi2={chi2:.1f}, dof={dof}, p={p:.4e}, V={v:.3f}, JSD={j:.4f}")
    print("  Per-category (ok vs ot):")
    for cat in CATEGORIES:
        e = enrichment[cat]
        r_str = f"{e['ratio']:.2f}x" if e['ratio'] is not None else "N/A"
        marker = '+' if e['ok'] > e['ot'] * 1.1 else ('-' if e['ot'] > e['ok'] * 1.1 else ' ')
        print(f"  {marker} {cat:14s}: ok={e['ok']:.3f}  ot={e['ot']:.3f}  ({r_str})")

    v_pass = p < BONFERRONI_P and v >= 0.05
    vrd = 'PASS' if v_pass else ('WEAK' if p < 0.05 else 'FAIL')
    print(f"  Verdict: {vrd}")

    return {
        'test': 'T2_ok_ot_divergence',
        'n_ok': len(ok_cats), 'n_ot': len(ot_cats),
        'chi2': chi2, 'p': p, 'dof': dof, 'V': v, 'JSD': j,
        'enrichment': enrichment,
        'verdict': vrd,
    }


def test_3_ch_sh_control(tokens):
    """T3: ch/sh category identity in B (control)."""
    print("\n=== T3: ch/sh Category Identity in B (Control) ===")

    ch_cats = [t['category'] for t in tokens if t['prefix'] == 'ch']
    sh_cats = [t['category'] for t in tokens if t['prefix'] == 'sh']

    print(f"  ch tokens: {len(ch_cats)}, sh tokens: {len(sh_cats)}")

    table = build_contingency_2x8(ch_cats, sh_cats)
    chi2, p, dof = chi2_test_safe(table)
    v = cramers_v(table)
    j = jsd(table[0] / table[0].sum(), table[1] / table[1].sum())

    # Control: V < 0.05 = CONFIRMED, V >= 0.05 + sig = VIOLATED
    if v < 0.05:
        vrd = 'CONTROL_CONFIRMED'
    elif p < BONFERRONI_P:
        vrd = 'CONTROL_VIOLATED'
    else:
        vrd = 'CONTROL_CONFIRMED'  # Not significant even if V is borderline

    # Per-category profiles
    ch_dist = table[0] / table[0].sum()
    sh_dist = table[1] / table[1].sum()
    profiles = {}
    for i, cat in enumerate(CATEGORIES):
        profiles[cat] = {
            'ch': round(float(ch_dist[i]), 4),
            'sh': round(float(sh_dist[i]), 4),
        }

    print(f"  chi2={chi2:.1f}, dof={dof}, p={p:.4e}, V={v:.3f}, JSD={j:.4f}")
    print(f"  C1268 reference: V=0.021, p=0.480 (Currier A)")
    print(f"  Verdict: {vrd}")

    return {
        'test': 'T3_ch_sh_control',
        'n_ch': len(ch_cats), 'n_sh': len(sh_cats),
        'chi2': chi2, 'p': p, 'dof': dof, 'V': v, 'JSD': j,
        'c1268_reference': {'V': 0.021, 'p': 0.480, 'scope': 'Currier A'},
        'profiles': profiles,
        'verdict': vrd,
    }


def test_4_qo_purity(tokens):
    """T4: qo category purity."""
    print("\n=== T4: qo Category Purity ===")

    qo_cats = Counter(t['category'] for t in tokens if t['prefix'] == 'qo')
    all_cats = Counter(t['category'] for t in tokens)

    qo_total = sum(qo_cats.values())
    all_total = sum(all_cats.values())

    print(f"  qo tokens: {qo_total}, total B tokens: {all_total}")

    # qo THERMAL rate vs corpus baseline
    qo_thermal = qo_cats.get('THERMAL', 0)
    corpus_thermal_rate = all_cats.get('THERMAL', 0) / all_total
    qo_thermal_rate = qo_thermal / qo_total if qo_total > 0 else 0

    # Binomial test
    binom_result = stats.binomtest(qo_thermal, qo_total, corpus_thermal_rate,
                                   alternative='greater')
    binom_p = binom_result.pvalue

    # Full profile
    qo_profile = {}
    for cat in CATEGORIES:
        frac = qo_cats.get(cat, 0) / qo_total if qo_total > 0 else 0
        qo_profile[cat] = round(frac, 4)

    # Rank among all prefixes
    pfx_thermal = {}
    for t in tokens:
        pfx = t['prefix']
        if pfx not in pfx_thermal:
            pfx_thermal[pfx] = [0, 0]  # [thermal, total]
        pfx_thermal[pfx][1] += 1
        if t['category'] == 'THERMAL':
            pfx_thermal[pfx][0] += 1

    # Only rank prefixes with N >= 30
    thermal_rates = {}
    for pfx, (th, tot) in pfx_thermal.items():
        if tot >= MIN_N:
            thermal_rates[pfx] = th / tot

    sorted_by_thermal = sorted(thermal_rates.items(), key=lambda x: -x[1])
    qo_rank = next(i + 1 for i, (p, _) in enumerate(sorted_by_thermal) if p == 'qo')
    n_ranked = len(sorted_by_thermal)

    ratio = qo_thermal_rate / corpus_thermal_rate if corpus_thermal_rate > 0 else 0

    print(f"  qo THERMAL rate: {qo_thermal_rate:.3f} ({qo_thermal}/{qo_total})")
    print(f"  Corpus THERMAL rate: {corpus_thermal_rate:.3f}")
    print(f"  Ratio: {ratio:.2f}x")
    print(f"  Binomial p: {binom_p:.4e}")
    print(f"  THERMAL rank: {qo_rank}/{n_ranked}")
    print(f"  qo profile: {qo_profile}")

    # Top 3 and bottom 3 by THERMAL rate
    print("  Top 5 THERMAL PREFIXes:")
    for pfx, rate in sorted_by_thermal[:5]:
        print(f"    {pfx:6s}: {rate:.3f}")

    v_pass = binom_p < BONFERRONI_P and ratio >= 2.0
    vrd = 'PASS' if v_pass else ('WEAK' if binom_p < 0.05 else 'FAIL')
    print(f"  Verdict: {vrd}")

    return {
        'test': 'T4_qo_purity',
        'n_qo': qo_total,
        'qo_thermal_rate': qo_thermal_rate,
        'corpus_thermal_rate': corpus_thermal_rate,
        'ratio': ratio,
        'binomial_p': binom_p,
        'qo_rank': qo_rank,
        'n_ranked': n_ranked,
        'qo_profile': qo_profile,
        'verdict': vrd,
    }


def test_5_da_sa(tokens):
    """T5: da vs sa category comparison."""
    print("\n=== T5: da vs sa Category Comparison ===")

    da_cats = [t['category'] for t in tokens if t['prefix'] == 'da']
    sa_cats = [t['category'] for t in tokens if t['prefix'] == 'sa']

    print(f"  da tokens: {len(da_cats)}, sa tokens: {len(sa_cats)}")

    if len(da_cats) < 5 or len(sa_cats) < 5:
        print("  Insufficient tokens for test")
        print("  Verdict: SKIP")
        return {
            'test': 'T5_da_sa',
            'n_da': len(da_cats), 'n_sa': len(sa_cats),
            'verdict': 'SKIP',
        }

    table = build_contingency_2x8(da_cats, sa_cats)
    chi2_obs, p_analytic, dof = chi2_test_safe(table)
    v = cramers_v(table)

    # If any expected count < 5, use permutation
    expected = np.outer(table.sum(axis=1), table.sum(axis=0)) / table.sum()
    use_perm = np.any(expected < 5)

    if use_perm:
        rng = np.random.RandomState(SEED)
        all_cats = da_cats + sa_cats
        n_da = len(da_cats)
        count_ge = 0
        for _ in range(N_PERM):
            perm = rng.permutation(len(all_cats))
            perm_da = [all_cats[i] for i in perm[:n_da]]
            perm_sa = [all_cats[i] for i in perm[n_da:]]
            perm_table = build_contingency_2x8(perm_da, perm_sa)
            perm_chi2, _, _ = chi2_test_safe(perm_table)
            if perm_chi2 >= chi2_obs:
                count_ge += 1
        p = (count_ge + 1) / (N_PERM + 1)
        print(f"  Using permutation test (small expected counts)")
    else:
        p = p_analytic

    # Per-category enrichment
    enrichment = {}
    da_dist = table[0] / table[0].sum() if table[0].sum() > 0 else table[0].astype(float)
    sa_dist = table[1] / table[1].sum() if table[1].sum() > 0 else table[1].astype(float)
    for i, cat in enumerate(CATEGORIES):
        enrichment[cat] = {
            'da': round(float(da_dist[i]), 4),
            'sa': round(float(sa_dist[i]), 4),
        }

    print(f"  chi2={chi2_obs:.1f}, dof={dof}, p={p:.4e}, V={v:.3f}")
    print(f"  Verdict criteria: any divergence is anti-circular (both a-base)")

    vrd = 'PASS' if p < BONFERRONI_P else ('WEAK' if p < 0.05 else 'FAIL')
    print(f"  Verdict: {vrd}")

    return {
        'test': 'T5_da_sa',
        'n_da': len(da_cats), 'n_sa': len(sa_cats),
        'chi2': chi2_obs, 'p': p, 'dof': dof, 'V': v,
        'permutation_used': use_perm,
        'enrichment': enrichment,
        'verdict': vrd,
    }


def test_6_tautology(tokens):
    """T6: Base-group category tautology decomposition (CRITICAL GATE)."""
    print("\n=== T6: Base-Group Category Tautology Decomposition (CRITICAL) ===")

    # Table A: BASE x CATEGORY
    bases = sorted(set(t['base'] for t in tokens))
    base_to_idx = {b: i for i, b in enumerate(bases)}
    table_a = np.zeros((len(bases), 8), dtype=int)
    for t in tokens:
        table_a[base_to_idx[t['base']], CATEGORIES.index(t['category'])] += 1

    chi2_base, p_base, dof_base = chi2_test_safe(table_a)
    v_base = cramers_v(table_a)

    # Table B: PREFIX x CATEGORY (qualifying only)
    pfx_counts = Counter(t['prefix'] for t in tokens)
    qualifying = sorted([p for p, n in pfx_counts.items() if n >= MIN_N])
    pfx_to_idx = {p: i for i, p in enumerate(qualifying)}
    table_b = np.zeros((len(qualifying), 8), dtype=int)
    for t in tokens:
        if t['prefix'] in pfx_to_idx:
            table_b[pfx_to_idx[t['prefix']], CATEGORIES.index(t['category'])] += 1

    chi2_pfx, p_pfx, dof_pfx = chi2_test_safe(table_b)
    v_pfx = cramers_v(table_b)

    print(f"  V_base={v_base:.3f} (chi2={chi2_base:.1f}, p={p_base:.4e})")
    print(f"  V_prefix={v_pfx:.3f} (chi2={chi2_pfx:.1f}, p={p_pfx:.4e})")
    print(f"  V_prefix - V_base = {v_pfx - v_base:+.3f}")

    # Within-base chi-squared tests
    within_base_results = {}
    within_base_pvals = []
    for base in bases:
        if base in ('BARE', 'OTHER'):
            continue
        # Get prefixes in this base with N >= MIN_N
        base_pfxs = [p for p in qualifying if PREFIX_TO_BASE.get(p) == base]
        if len(base_pfxs) < 2:
            continue
        # Build within-base contingency
        base_pfx_idx = {p: i for i, p in enumerate(base_pfxs)}
        base_table = np.zeros((len(base_pfxs), 8), dtype=int)
        for t in tokens:
            if t['prefix'] in base_pfx_idx:
                base_table[base_pfx_idx[t['prefix']],
                           CATEGORIES.index(t['category'])] += 1

        chi2_wb, p_wb, dof_wb = chi2_test_safe(base_table)
        v_wb = cramers_v(base_table)
        n_wb = int(base_table.sum())
        within_base_results[base] = {
            'prefixes': base_pfxs,
            'n': n_wb,
            'chi2': chi2_wb,
            'p': p_wb,
            'dof': dof_wb,
            'V': v_wb,
        }
        if p_wb > 0:
            within_base_pvals.append(p_wb)

        marker = '*' if p_wb < 0.05 else ' '
        print(f"  {marker} {base}-base ({', '.join(base_pfxs)}): "
              f"chi2={chi2_wb:.1f}, p={p_wb:.4e}, V={v_wb:.3f}, n={n_wb}")

    # Fisher-combine within-base p-values
    if len(within_base_pvals) >= 2:
        fisher_stat = -2 * sum(np.log(p) for p in within_base_pvals)
        fisher_dof = 2 * len(within_base_pvals)
        fisher_p = 1 - stats.chi2.cdf(fisher_stat, fisher_dof)
    else:
        fisher_stat = 0
        fisher_dof = 0
        fisher_p = 1.0

    print(f"  Fisher combined: stat={fisher_stat:.1f}, dof={fisher_dof}, p={fisher_p:.4e}")

    # Conditional mutual information: I(CAT; PREFIX | BASE)
    # = H(CAT|BASE) - H(CAT|PREFIX)
    # H(CAT|BASE)
    base_joint = defaultdict(Counter)
    for t in tokens:
        if t['prefix'] in pfx_to_idx:  # Only qualifying
            base_joint[t['base']][t['category']] += 1
    h_cat_given_base = conditional_entropy(base_joint)

    # H(CAT|PREFIX)
    pfx_joint = defaultdict(Counter)
    for t in tokens:
        if t['prefix'] in pfx_to_idx:
            pfx_joint[t['prefix']][t['category']] += 1
    h_cat_given_pfx = conditional_entropy(pfx_joint)

    # H(CAT)
    cat_counts = Counter(t['category'] for t in tokens if t['prefix'] in pfx_to_idx)
    h_cat = entropy_from_counts([cat_counts[c] for c in CATEGORIES])

    cmi = h_cat_given_base - h_cat_given_pfx
    mi_base = h_cat - h_cat_given_base
    mi_pfx = h_cat - h_cat_given_pfx

    print(f"  H(CAT)={h_cat:.3f} bits")
    print(f"  H(CAT|BASE)={h_cat_given_base:.3f} bits  ->  I(CAT;BASE)={mi_base:.3f} bits ({100*mi_base/h_cat:.1f}%)")
    print(f"  H(CAT|PREFIX)={h_cat_given_pfx:.3f} bits  ->  I(CAT;PREFIX)={mi_pfx:.3f} bits ({100*mi_pfx/h_cat:.1f}%)")
    print(f"  I(CAT; PREFIX | BASE) = {cmi:.3f} bits ({100*cmi/h_cat:.1f}%)")

    # PASS: Fisher p < 0.00625 AND CMI > 0.05 bits
    t6_pass = fisher_p < BONFERRONI_P and cmi > 0.05
    vrd = 'PASS' if t6_pass else 'FAIL'

    if vrd == 'FAIL':
        print("  *** TAUTOLOGY GATE FAILED: base fully explains PREFIX-category ***")
    print(f"  Verdict: {vrd}")

    return {
        'test': 'T6_tautology_decomposition',
        'v_base': v_base, 'chi2_base': chi2_base, 'p_base': p_base,
        'v_prefix': v_pfx, 'chi2_prefix': chi2_pfx, 'p_prefix': p_pfx,
        'within_base': within_base_results,
        'fisher_stat': fisher_stat, 'fisher_dof': fisher_dof, 'fisher_p': fisher_p,
        'h_cat': h_cat,
        'h_cat_given_base': h_cat_given_base,
        'h_cat_given_prefix': h_cat_given_pfx,
        'mi_base': mi_base, 'mi_prefix': mi_pfx,
        'conditional_mi': cmi,
        'cmi_pct': 100 * cmi / h_cat if h_cat > 0 else 0,
        'verdict': vrd,
    }


def test_7_bare(tokens):
    """T7: BARE prefix category profile."""
    print("\n=== T7: BARE PREFIX Category Profile ===")

    bare_cats = [t['category'] for t in tokens if t['prefix'] == 'BARE']
    prefixed_cats = [t['category'] for t in tokens if t['prefix'] != 'BARE']

    print(f"  BARE tokens: {len(bare_cats)}, prefixed tokens: {len(prefixed_cats)}")

    table = build_contingency_2x8(bare_cats, prefixed_cats)
    chi2, p, dof = chi2_test_safe(table)
    v = cramers_v(table)

    bare_dist = table[0] / table[0].sum() if table[0].sum() > 0 else table[0].astype(float)
    pfx_dist = table[1] / table[1].sum() if table[1].sum() > 0 else table[1].astype(float)

    print(f"  chi2={chi2:.1f}, dof={dof}, p={p:.4e}, V={v:.3f}")
    print("  Category profiles (BARE vs PREFIXED):")
    for i, cat in enumerate(CATEGORIES):
        diff = bare_dist[i] - pfx_dist[i]
        marker = '+' if diff > 0.02 else ('-' if diff < -0.02 else ' ')
        print(f"  {marker} {cat:14s}: BARE={bare_dist[i]:.3f}  PFX={pfx_dist[i]:.3f}  "
              f"diff={diff:+.3f}")

    vrd = 'PASS' if (p < BONFERRONI_P and v >= 0.05) else ('WEAK' if p < 0.05 else 'FAIL')
    print(f"  Verdict: {vrd}")

    return {
        'test': 'T7_bare_profile',
        'n_bare': len(bare_cats), 'n_prefixed': len(prefixed_cats),
        'chi2': chi2, 'p': p, 'dof': dof, 'V': v,
        'bare_profile': {CATEGORIES[i]: round(float(bare_dist[i]), 4) for i in range(8)},
        'prefixed_profile': {CATEGORIES[i]: round(float(pfx_dist[i]), 4) for i in range(8)},
        'verdict': vrd,
    }


def test_8_base_alignment(tokens):
    """T8: Base-group category alignment."""
    print("\n=== T8: Base-Group Category Alignment ===")

    # Build base x category counts
    base_cats = defaultdict(Counter)
    for t in tokens:
        base_cats[t['base']][t['category']] += 1

    # Compute alignment for each base with predictions
    alignment_scores = {}
    for base, expected_cats in BASE_EXPECTED_CATEGORIES.items():
        if base not in base_cats:
            continue
        total = sum(base_cats[base].values())
        if total < MIN_N:
            continue
        predicted_count = sum(base_cats[base].get(c, 0) for c in expected_cats)
        alignment = predicted_count / total
        alignment_scores[base] = {
            'n': total,
            'predicted_cats': expected_cats,
            'alignment': round(alignment, 3),
            'profile': {c: round(base_cats[base].get(c, 0) / total, 4)
                        for c in CATEGORIES},
        }
        print(f"  {base}-base (n={total}): alignment={alignment:.3f} "
              f"(expected: {', '.join(expected_cats)})")

    # Mean alignment across qualifying bases
    if alignment_scores:
        mean_alignment = np.mean([v['alignment'] for v in alignment_scores.values()])
    else:
        mean_alignment = 0.0

    print(f"  Mean alignment: {mean_alignment:.3f}")

    # Permutation test: shuffle base labels
    rng = np.random.RandomState(SEED)

    # Flatten tokens to (base, category) pairs for qualifying bases only
    qualifying_bases = set(alignment_scores.keys())
    qual_tokens = [(t['base'], t['category']) for t in tokens
                   if t['base'] in qualifying_bases]
    all_bases_arr = [b for b, c in qual_tokens]
    all_cats_arr = [c for b, c in qual_tokens]

    count_ge = 0
    for _ in range(N_PERM):
        perm_bases = rng.permutation(all_bases_arr)
        # Rebuild base-category counts
        perm_base_cats = defaultdict(Counter)
        for b, c in zip(perm_bases, all_cats_arr):
            perm_base_cats[b][c] += 1
        # Compute alignment
        perm_scores = []
        for base, expected_cats in BASE_EXPECTED_CATEGORIES.items():
            if base not in perm_base_cats or base not in qualifying_bases:
                continue
            total = sum(perm_base_cats[base].values())
            if total < MIN_N:
                continue
            pred = sum(perm_base_cats[base].get(c, 0) for c in expected_cats)
            perm_scores.append(pred / total)
        if perm_scores:
            perm_mean = np.mean(perm_scores)
            if perm_mean >= mean_alignment:
                count_ge += 1

    perm_p = (count_ge + 1) / (N_PERM + 1)

    # Diagnostic interpretation
    if mean_alignment > 0.70:
        diagnostic = "SEVERE tautology: base->category mapping very strong"
    elif mean_alignment > 0.40:
        diagnostic = "PARTIAL alignment: base predicts category but not completely"
    else:
        diagnostic = "WEAK alignment: base-category mapping surprisingly loose"

    vrd = 'PASS' if (perm_p < BONFERRONI_P and mean_alignment > 0.40) else \
          ('WEAK' if perm_p < 0.05 else 'FAIL')
    print(f"  Permutation p: {perm_p:.4e}")
    print(f"  Diagnostic: {diagnostic}")
    print(f"  Verdict: {vrd}")

    return {
        'test': 'T8_base_alignment',
        'alignment_scores': alignment_scores,
        'mean_alignment': mean_alignment,
        'perm_p': perm_p,
        'diagnostic': diagnostic,
        'verdict': vrd,
    }


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 60)
    print("Phase 458: PREFIX_CATEGORY_ANATOMY")
    print("=" * 60)

    t0 = time.time()
    print("Loading data...")
    tokens = load_data()
    print(f"  B tokens with category: {len(tokens)}")
    print(f"  Unique PREFIXes: {len(set(t['prefix'] for t in tokens))}")
    print(f"  Unique bases: {len(set(t['base'] for t in tokens))}")
    print(f"  Time: {time.time() - t0:.1f}s")

    # Run tests
    results = []
    r1 = test_1_full_contingency(tokens)
    results.append(r1)
    r2 = test_2_ok_ot(tokens)
    results.append(r2)
    r3 = test_3_ch_sh_control(tokens)
    results.append(r3)
    r4 = test_4_qo_purity(tokens)
    results.append(r4)
    r5 = test_5_da_sa(tokens)
    results.append(r5)
    r6 = test_6_tautology(tokens)
    results.append(r6)
    r7 = test_7_bare(tokens)
    results.append(r7)
    r8 = test_8_base_alignment(tokens)
    results.append(r8)

    # Compute overall verdict
    t6_pass = r6['verdict'] == 'PASS'

    # Count passes
    n_pass = 0
    n_weak = 0
    n_fail = 0
    n_skip = 0

    for r in results:
        v = r['verdict']
        if v == 'PASS' or v == 'CONTROL_CONFIRMED':
            n_pass += 1
        elif v == 'WEAK':
            n_weak += 1
        elif v == 'SKIP':
            n_skip += 1
        elif v == 'CONTROL_VIOLATED':
            n_fail += 1  # Unexpected, counts as fail in total but is a discovery
        else:
            n_fail += 1

    if not t6_pass:
        overall = 'TAUTOLOGICAL'
    elif n_pass >= 6:
        overall = 'CATEGORY_ANATOMY_CONFIRMED'
    elif n_pass >= 4:
        overall = 'PARTIAL_ANATOMY'
    else:
        overall = 'NULL_ANATOMY'

    # Summary
    elapsed = time.time() - t0
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in results:
        p_val = r.get('p', r.get('binomial_p', r.get('perm_p', r.get('fisher_p', None))))
        p_str = f"p={p_val:.2e}" if p_val is not None else ""
        print(f"  {r['test']:45s} {r['verdict']:20s} {p_str}")

    print(f"\n  PASS={n_pass} WEAK={n_weak} FAIL={n_fail} SKIP={n_skip}")
    if not t6_pass:
        print(f"  T6 GATE: FAILED -- tautology confirmed")
    print(f"  Overall: {overall}")
    print(f"  Elapsed: {elapsed:.1f}s")

    # Save results
    output = {
        'phase_name': 'PREFIX_CATEGORY_ANATOMY',
        'phase_number': 458,
        'n_tokens': len(tokens),
        'bonferroni_p': BONFERRONI_P,
        'tests': results,
        'summary': {
            'n_pass': n_pass,
            'n_weak': n_weak,
            'n_fail': n_fail,
            'n_skip': n_skip,
            't6_gate': t6_pass,
            'overall_verdict': overall,
        },
    }

    outpath = ROOT / 'phases' / 'PREFIX_CATEGORY_ANATOMY' / 'results' / 'prefix_category_anatomy.json'
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\n  Results saved to: {outpath}")


if __name__ == '__main__':
    main()
