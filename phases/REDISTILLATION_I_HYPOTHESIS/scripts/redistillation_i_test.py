"""Phase 596: Redistillation-i Hypothesis Test.

Tests whether the i-extension system (single-i vs double-ii) encodes
redistillation familiarity vs first-pass iteration, or is fully explained
by the safety-routing mechanism (C1480-C1482).
"""
import json
import math
import os
import sys
import time
import numpy as np
from collections import defaultdict, Counter
from scipy import stats

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')
ROOT = os.path.dirname(os.path.dirname(PHASE_DIR))
sys.path.insert(0, ROOT)

from scripts.voynich import (Transcript, Morphology, CategoryClassifier,
                              decompose_middle_hmt)

REGIME_PATH = os.path.join(ROOT, 'data', 'regime_folio_mapping.json')
DECODER_PATH = os.path.join(ROOT, 'data', 'decoder_maps.json')

N_SHUFFLES = 1000
SEED = 42


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def max_consecutive_i(middle):
    """Count max run of consecutive 'i' in a MIDDLE string."""
    max_run = current = 0
    for ch in middle:
        if ch == 'i':
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0
    return max_run


def i_class(middle):
    """Classify MIDDLE by i-extension: 'no_i', 'single_i', 'double_ii'."""
    mc = max_consecutive_i(middle)
    if mc == 0:
        return 'no_i'
    elif mc == 1:
        return 'single_i'
    else:
        return 'double_ii'


def shannon_entropy(counts):
    """Shannon entropy in bits from a Counter or dict of counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def load_hazard_map():
    """Load frame hazard map from decoder_maps.json."""
    with open(DECODER_PATH) as f:
        dm = json.load(f)
    fh = dm['maps']['frame_hazard']['entries']
    return {k: v['value'] for k, v in fh.items()}


def token_hazard_class(head, term, frame_str, hazard_map):
    """Determine hazard class for a token."""
    if head == 'k':
        return 'IMMUNE'
    elif frame_str:
        return hazard_map.get(frame_str, 'LOW')
    else:
        return 'LOW'


def is_hazardous(hazard_class):
    """HIGH hazard = hazardous (matching C1280 FLOW/CONTAINMENT)."""
    return hazard_class == 'HIGH'


def load_regime_map():
    """Load folio -> REGIME mapping."""
    with open(REGIME_PATH) as f:
        data = json.load(f)
    return {f: v['regime'] for f, v in data.get('regime_assignments', {}).items()}


def stouffer_z(z_values):
    """Combine z-values via Stouffer's method."""
    z_arr = np.array(z_values)
    if len(z_arr) == 0:
        return 0.0, 1.0
    combined = np.sum(z_arr) / np.sqrt(len(z_arr))
    p = 2 * stats.norm.sf(abs(combined))
    return float(combined), float(p)


# ============================================================
# DATA ASSEMBLY
# ============================================================
def assemble_data():
    """Load and prepare all tokens with i-class, hazard, paragraph info."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()
    hazard_map = load_hazard_map()
    regime_map = load_regime_map()

    # Process Currier B tokens
    b_tokens = []
    for t in tx.currier_b():
        if t.placement.startswith('L'):
            continue
        if '*' in t.word:
            continue
        w = t.word.strip()
        if not w:
            continue
        m = morph.extract(w)
        if not m.middle:
            continue

        head, mods, term, frame_str = decompose_middle_hmt(m.middle)
        ic = i_class(m.middle)
        hc = token_hazard_class(head, term, frame_str, hazard_map)
        cat = cc.classify(m.middle)

        b_tokens.append({
            'word': w,
            'folio': t.folio,
            'line': t.line,
            'section': t.section,
            'middle': m.middle,
            'prefix': m.prefix,
            'suffix': m.suffix,
            'head': head,
            'term': term,
            'frame_str': frame_str,
            'i_class': ic,
            'hazard_class': hc,
            'hazardous': is_hazardous(hc),
            'category': cat,
            'par_initial': t.par_initial,
            'par_final': t.par_final,
            'regime': regime_map.get(t.folio, 'UNKNOWN'),
        })

    # Process Currier A tokens (for T8)
    a_tokens = []
    for t in tx.currier_a():
        if t.placement.startswith('L'):
            continue
        if '*' in t.word:
            continue
        w = t.word.strip()
        if not w:
            continue
        m = morph.extract(w)
        if not m.middle:
            continue
        ic = i_class(m.middle)
        a_tokens.append({
            'word': w,
            'folio': t.folio,
            'section': t.section,
            'middle': m.middle,
            'i_class': ic,
        })

    # Build paragraphs from B tokens
    paragraphs = []
    current_par = []
    current_folio = None
    par_idx = 0

    for tok in b_tokens:
        if tok['par_initial'] and current_par:
            paragraphs.append({
                'folio': current_folio,
                'par_idx': par_idx,
                'tokens': current_par,
                'section': current_par[0]['section'],
            })
            if tok['folio'] != current_folio:
                par_idx = 0
                current_folio = tok['folio']
            else:
                par_idx += 1
            current_par = [tok]
        else:
            if current_folio is None or tok['folio'] != current_folio:
                if current_par:
                    paragraphs.append({
                        'folio': current_folio,
                        'par_idx': par_idx,
                        'tokens': current_par,
                        'section': current_par[0]['section'],
                    })
                current_folio = tok['folio']
                par_idx = 0
                current_par = [tok]
            else:
                current_par.append(tok)
    if current_par:
        paragraphs.append({
            'folio': current_folio,
            'par_idx': par_idx,
            'tokens': current_par,
            'section': current_par[0]['section'],
        })

    # Separate header (first line) from body for each paragraph
    for par in paragraphs:
        lines = defaultdict(list)
        for tok in par['tokens']:
            lines[tok['line']].append(tok)
        sorted_lines = sorted(lines.keys())
        if len(sorted_lines) >= 2:
            par['header_tokens'] = lines[sorted_lines[0]]
            par['body_tokens'] = []
            par['body_lines'] = []
            for ln in sorted_lines[1:]:
                par['body_tokens'].extend(lines[ln])
                par['body_lines'].append(lines[ln])
            par['n_body_lines'] = len(sorted_lines) - 1
        else:
            par['header_tokens'] = par['tokens']
            par['body_tokens'] = []
            par['body_lines'] = []
            par['n_body_lines'] = 0

    # Build line-level index for B tokens
    line_index = defaultdict(list)
    for tok in b_tokens:
        line_index[(tok['folio'], tok['line'])].append(tok)

    return b_tokens, a_tokens, paragraphs, line_index


# ============================================================
# T1: Within-Paragraph Positional Distribution
# ============================================================
def run_t1(paragraphs, rng):
    """Test ii-token positional distribution within paragraph bodies."""
    qualifying = [p for p in paragraphs if p['n_body_lines'] >= 5]

    # Pool tokens by quintile
    quintile_counts = {q: Counter() for q in range(5)}  # i_class -> count
    for par in qualifying:
        n_lines = par['n_body_lines']
        for li, line_toks in enumerate(par['body_lines']):
            frac = li / (n_lines - 1) if n_lines > 1 else 0.5
            q = min(int(frac * 5), 4)
            for tok in line_toks:
                quintile_counts[q][tok['i_class']] += 1

    # Compute ii-fraction per quintile
    ii_fracs = {}
    for q in range(5):
        total_i = quintile_counts[q].get('single_i', 0) + quintile_counts[q].get('double_ii', 0)
        ii_fracs[q] = quintile_counts[q].get('double_ii', 0) / total_i if total_i > 0 else 0.0

    # Spearman rho
    qs = list(range(5))
    fracs = [ii_fracs[q] for q in qs]
    if len(set(fracs)) > 1:
        rho, rho_p = stats.spearmanr(qs, fracs)
    else:
        rho, rho_p = 0.0, 1.0

    # Permutation test: shuffle i-classes within each paragraph's body
    perm_rhos = []
    for _ in range(N_SHUFFLES):
        perm_qc = {q: Counter() for q in range(5)}
        for par in qualifying:
            n_lines = par['n_body_lines']
            # Collect all i-classes in body
            all_ic = [tok['i_class'] for tok in par['body_tokens']]
            rng.shuffle(all_ic)
            idx = 0
            for li, line_toks in enumerate(par['body_lines']):
                frac = li / (n_lines - 1) if n_lines > 1 else 0.5
                q = min(int(frac * 5), 4)
                for _ in line_toks:
                    perm_qc[q][all_ic[idx]] += 1
                    idx += 1
        perm_fracs = []
        for q in range(5):
            total_i = perm_qc[q].get('single_i', 0) + perm_qc[q].get('double_ii', 0)
            perm_fracs.append(perm_qc[q].get('double_ii', 0) / total_i if total_i > 0 else 0.0)
        if len(set(perm_fracs)) > 1:
            pr, _ = stats.spearmanr(qs, perm_fracs)
        else:
            pr = 0.0
        perm_rhos.append(pr)

    perm_p = np.mean(np.abs(perm_rhos) >= abs(rho))

    # HEAD-atom control: restrict to a-HEAD tokens only
    a_head_qc = {q: Counter() for q in range(5)}
    for par in qualifying:
        n_lines = par['n_body_lines']
        for li, line_toks in enumerate(par['body_lines']):
            frac = li / (n_lines - 1) if n_lines > 1 else 0.5
            q = min(int(frac * 5), 4)
            for tok in line_toks:
                if tok['head'] == 'a':
                    a_head_qc[q][tok['i_class']] += 1

    a_head_fracs = {}
    for q in range(5):
        total_i = a_head_qc[q].get('single_i', 0) + a_head_qc[q].get('double_ii', 0)
        a_head_fracs[q] = a_head_qc[q].get('double_ii', 0) / total_i if total_i > 0 else 0.0

    a_fracs_list = [a_head_fracs[q] for q in qs]
    if len(set(a_fracs_list)) > 1:
        a_rho, a_rho_p = stats.spearmanr(qs, a_fracs_list)
    else:
        a_rho, a_rho_p = 0.0, 1.0

    return {
        'n_qualifying_paragraphs': len(qualifying),
        'ii_fraction_by_quintile': {str(q): round(ii_fracs[q], 4) for q in range(5)},
        'quintile_i_counts': {str(q): dict(quintile_counts[q]) for q in range(5)},
        'rho': round(float(rho), 4),
        'rho_p': round(float(rho_p), 4),
        'perm_p': round(float(perm_p), 4),
        'significant': bool(perm_p < 0.01),
        'a_head_control': {
            'ii_fraction_by_quintile': {str(q): round(a_head_fracs[q], 4) for q in range(5)},
            'rho': round(float(a_rho), 4),
            'rho_p': round(float(a_rho_p), 4),
        },
    }


# ============================================================
# T2: Paragraph Type Discrimination
# ============================================================
def run_t2(paragraphs):
    """Test whether paragraphs separate into ii-enriched vs i-enriched types."""
    qualifying = [p for p in paragraphs if len(p['tokens']) >= 10]

    par_ii_fracs = []
    par_details = []
    for par in qualifying:
        i_tokens = [t for t in par['tokens'] if t['i_class'] != 'no_i']
        n_i = len(i_tokens)
        if n_i < 3:  # Need minimum i-tokens to compute meaningful fraction
            continue
        n_ii = sum(1 for t in i_tokens if t['i_class'] == 'double_ii')
        ii_frac = n_ii / n_i
        par_ii_fracs.append(ii_frac)
        par_details.append({
            'folio': par['folio'],
            'section': par['section'],
            'n_tokens': len(par['tokens']),
            'n_i_tokens': n_i,
            'n_ii': n_ii,
            'ii_fraction': round(ii_frac, 4),
        })

    if len(par_ii_fracs) < 10:
        return {'status': 'INSUFFICIENT_DATA', 'n_paragraphs': len(par_ii_fracs)}

    fracs = np.array(par_ii_fracs)
    obs_var = float(np.var(fracs))
    obs_mean = float(np.mean(fracs))

    # Expected variance under binomial null
    # For each paragraph, binomial variance = p*(1-p)/n_i
    # Expected total variance = mean of individual variances
    expected_vars = []
    for pd in par_details:
        p = obs_mean  # Use corpus-wide ii-fraction as p
        n = pd['n_i_tokens']
        expected_vars.append(p * (1 - p) / n)
    expected_var = float(np.mean(expected_vars))

    overdispersion_ratio = obs_var / expected_var if expected_var > 0 else float('inf')

    # Split at median and characterize groups
    median_frac = float(np.median(fracs))
    low_group = [pd for pd, f in zip(par_details, par_ii_fracs) if f <= median_frac]
    high_group = [pd for pd, f in zip(par_details, par_ii_fracs) if f > median_frac]

    # Category profiles for groups
    def group_category_profile(group_details, qualifying_pars):
        cats = Counter()
        for gd in group_details:
            # Find matching paragraph
            for par in qualifying_pars:
                if par['folio'] == gd['folio'] and len(par['tokens']) == gd['n_tokens']:
                    for tok in par['tokens']:
                        cats[tok['category']] += 1
                    break
        total = sum(cats.values())
        return {k: round(v / total, 4) for k, v in sorted(cats.items())} if total > 0 else {}

    # Hazard rates for groups
    def group_hazard_rate(group_details, qualifying_pars):
        n_haz = 0
        n_total = 0
        for gd in group_details:
            for par in qualifying_pars:
                if par['folio'] == gd['folio'] and len(par['tokens']) == gd['n_tokens']:
                    for tok in par['tokens']:
                        n_total += 1
                        if tok['hazardous']:
                            n_haz += 1
                    break
        return round(n_haz / n_total, 4) if n_total > 0 else 0.0

    return {
        'n_paragraphs': len(par_ii_fracs),
        'mean_ii_fraction': round(obs_mean, 4),
        'obs_variance': round(obs_var, 6),
        'binomial_expected_variance': round(expected_var, 6),
        'overdispersion_ratio': round(overdispersion_ratio, 2),
        'overdispersed': bool(overdispersion_ratio > 2.0),
        'median_ii_fraction': round(median_frac, 4),
        'low_group_n': len(low_group),
        'high_group_n': len(high_group),
        'low_group_mean_ii': round(float(np.mean([d['ii_fraction'] for d in low_group])), 4) if low_group else None,
        'high_group_mean_ii': round(float(np.mean([d['ii_fraction'] for d in high_group])), 4) if high_group else None,
        'low_group_hazard': group_hazard_rate(low_group, [p for p in paragraphs if len(p['tokens']) >= 10]),
        'high_group_hazard': group_hazard_rate(high_group, [p for p in paragraphs if len(p['tokens']) >= 10]),
        'low_group_sections': dict(Counter(d['section'] for d in low_group)),
        'high_group_sections': dict(Counter(d['section'] for d in high_group)),
    }


# ============================================================
# T3: Paragraph Ordinal Distribution (C1399 Negative Control)
# ============================================================
def run_t3(paragraphs, rng):
    """Test ii-fraction by paragraph ordinal within folios."""
    # Group paragraphs by folio
    folio_pars = defaultdict(list)
    for par in paragraphs:
        if len(par['tokens']) >= 5:  # Minimum tokens
            i_toks = [t for t in par['tokens'] if t['i_class'] != 'no_i']
            if len(i_toks) >= 2:
                n_ii = sum(1 for t in i_toks if t['i_class'] == 'double_ii')
                folio_pars[par['folio']].append({
                    'par_idx': par['par_idx'],
                    'ii_frac': n_ii / len(i_toks),
                    'section': par['section'],
                })

    # Filter folios with >= 3 paragraphs
    qualifying_folios = {f: ps for f, ps in folio_pars.items() if len(ps) >= 3}

    if len(qualifying_folios) < 5:
        return {'status': 'INSUFFICIENT_DATA', 'n_folios': len(qualifying_folios)}

    # Compute per-folio Spearman rho
    folio_rhos = []
    folio_zs = []
    for folio, pars in sorted(qualifying_folios.items()):
        pars_sorted = sorted(pars, key=lambda x: x['par_idx'])
        n = len(pars_sorted)
        ordinals = [i / (n - 1) if n > 1 else 0.5 for i in range(n)]
        ii_fracs = [p['ii_frac'] for p in pars_sorted]
        if len(set(ii_fracs)) > 1:
            r, p = stats.spearmanr(ordinals, ii_fracs)
            folio_rhos.append({'folio': folio, 'rho': round(float(r), 4),
                               'p': round(float(p), 4), 'n_pars': n})
            folio_zs.append(float(r) * math.sqrt(n - 1))  # Approximate z
        else:
            folio_rhos.append({'folio': folio, 'rho': 0.0, 'p': 1.0, 'n_pars': n})
            folio_zs.append(0.0)

    agg_z, agg_p = stouffer_z(folio_zs)

    # Shuffle control
    shuffle_zs = []
    for _ in range(N_SHUFFLES):
        shuf_folio_zs = []
        for folio, pars in sorted(qualifying_folios.items()):
            n = len(pars)
            ii_fracs = [p['ii_frac'] for p in pars]
            rng.shuffle(ii_fracs)
            ordinals = [i / (n - 1) if n > 1 else 0.5 for i in range(n)]
            if len(set(ii_fracs)) > 1:
                r, _ = stats.spearmanr(ordinals, ii_fracs)
                shuf_folio_zs.append(float(r) * math.sqrt(n - 1))
            else:
                shuf_folio_zs.append(0.0)
        sz, _ = stouffer_z(shuf_folio_zs)
        shuffle_zs.append(sz)

    perm_p = np.mean(np.abs(shuffle_zs) >= abs(agg_z))

    return {
        'n_folios': len(qualifying_folios),
        'stouffer_z': round(agg_z, 4),
        'stouffer_p': round(float(agg_p), 4),
        'perm_p': round(float(perm_p), 4),
        'significant': bool(perm_p < 0.01),
        'mean_rho': round(float(np.mean([fr['rho'] for fr in folio_rhos])), 4),
        'c1399_confirmed': bool(perm_p >= 0.01),
    }


# ============================================================
# T4: REGIME Enrichment
# ============================================================
def run_t4(b_tokens):
    """Test ii/i ratio by REGIME."""
    regime_counts = defaultdict(lambda: Counter())  # regime -> {single_i, double_ii}
    regime_hazard = defaultdict(lambda: {'haz': 0, 'total': 0})

    for tok in b_tokens:
        r = tok['regime']
        if r == 'UNKNOWN':
            continue
        if tok['i_class'] != 'no_i':
            regime_counts[r][tok['i_class']] += 1
        regime_hazard[r]['total'] += 1
        if tok['hazardous']:
            regime_hazard[r]['haz'] += 1

    # ii/(i+ii) ratio per REGIME
    regime_ratios = {}
    for r in sorted(regime_counts.keys()):
        si = regime_counts[r].get('single_i', 0)
        di = regime_counts[r].get('double_ii', 0)
        total = si + di
        regime_ratios[r] = {
            'single_i': si,
            'double_ii': di,
            'total_i': total,
            'ii_ratio': round(di / total, 4) if total > 0 else 0.0,
            'hazard_rate': round(regime_hazard[r]['haz'] / regime_hazard[r]['total'], 4) if regime_hazard[r]['total'] > 0 else 0.0,
        }

    # Chi-squared test: REGIME x i-extension
    regimes = sorted(regime_counts.keys())
    if len(regimes) >= 2:
        contingency = []
        for r in regimes:
            contingency.append([
                regime_counts[r].get('single_i', 0),
                regime_counts[r].get('double_ii', 0),
            ])
        contingency = np.array(contingency)
        if contingency.sum() > 0 and all(contingency.sum(axis=0) > 0):
            chi2, chi_p, dof, _ = stats.chi2_contingency(contingency)
            n_total = contingency.sum()
            cramers_v = math.sqrt(chi2 / (n_total * min(len(regimes) - 1, 1))) if n_total > 0 else 0.0
        else:
            chi2, chi_p, dof, cramers_v = 0.0, 1.0, 0, 0.0
    else:
        chi2, chi_p, dof, cramers_v = 0.0, 1.0, 0, 0.0

    # Hazard confound: correlation between ii_ratio and hazard_rate
    if len(regimes) >= 3:
        ii_rats = [regime_ratios[r]['ii_ratio'] for r in regimes]
        haz_rats = [regime_ratios[r]['hazard_rate'] for r in regimes]
        if len(set(ii_rats)) > 1 and len(set(haz_rats)) > 1:
            haz_corr, haz_corr_p = stats.spearmanr(ii_rats, haz_rats)
        else:
            haz_corr, haz_corr_p = 0.0, 1.0
    else:
        haz_corr, haz_corr_p = 0.0, 1.0

    # Check if REGIME_3 has highest ratio
    r3_ratio = regime_ratios.get('REGIME_3', {}).get('ii_ratio', 0.0)
    r3_highest = all(r3_ratio >= regime_ratios[r]['ii_ratio']
                     for r in regimes if r != 'REGIME_3')

    return {
        'regime_ratios': regime_ratios,
        'chi2': round(float(chi2), 2),
        'chi_p': round(float(chi_p), 6),
        'dof': int(dof),
        'cramers_v': round(float(cramers_v), 4),
        'significant': bool(chi_p < 0.01),
        'regime_3_highest': bool(r3_highest),
        'hazard_confound': {
            'ii_hazard_correlation': round(float(haz_corr), 4),
            'ii_hazard_p': round(float(haz_corr_p), 4),
            'confounded': bool(abs(haz_corr) > 0.8 and haz_corr_p < 0.1),
        },
    }


# ============================================================
# T5: Successor Entropy
# ============================================================
def run_t5(b_tokens, rng):
    """Test successor entropy by predecessor i-class."""
    # Build line-ordered token lists
    line_tokens = defaultdict(list)
    for tok in b_tokens:
        line_tokens[(tok['folio'], tok['line'])].append(tok)

    # Collect successor pairs
    succ_by_iclass = defaultdict(Counter)  # i_class -> Counter of successor MIDDLEs
    succ_by_iclass_term = defaultdict(lambda: defaultdict(Counter))  # i_class -> term -> Counter
    pair_iclasses = []  # List of (i_class, successor_middle) for shuffling

    for key, toks in line_tokens.items():
        for j in range(len(toks) - 1):
            pred = toks[j]
            succ = toks[j + 1]
            ic = pred['i_class']
            sm = succ['middle']
            succ_by_iclass[ic][sm] += 1
            term = pred['term'] if pred['term'] else 'bare'
            succ_by_iclass_term[ic][term][sm] += 1
            pair_iclasses.append((ic, sm))

    # Compute entropies
    entropies = {}
    for ic in ['no_i', 'single_i', 'double_ii']:
        entropies[ic] = {
            'entropy': round(shannon_entropy(succ_by_iclass[ic]), 4),
            'n_pairs': sum(succ_by_iclass[ic].values()),
            'n_unique_successors': len(succ_by_iclass[ic]),
        }

    # Permutation test: shuffle i-class labels
    real_diff = entropies['single_i']['entropy'] - entropies['double_ii']['entropy']
    perm_diffs = []
    all_ics = [ic for ic, _ in pair_iclasses]
    all_succs = [sm for _, sm in pair_iclasses]

    for _ in range(N_SHUFFLES):
        shuffled_ics = all_ics.copy()
        rng.shuffle(shuffled_ics)
        perm_succ = defaultdict(Counter)
        for ic, sm in zip(shuffled_ics, all_succs):
            perm_succ[ic][sm] += 1
        si_ent = shannon_entropy(perm_succ['single_i'])
        di_ent = shannon_entropy(perm_succ['double_ii'])
        perm_diffs.append(si_ent - di_ent)

    perm_p = np.mean(np.array(perm_diffs) >= real_diff)

    # Terminal-atom decomposition
    term_decomp = {}
    for term in ['l', 'r', 'h', 'y', 'm', 'n', 'bare']:
        term_ents = {}
        for ic in ['no_i', 'single_i', 'double_ii']:
            if term in succ_by_iclass_term[ic] and sum(succ_by_iclass_term[ic][term].values()) >= 10:
                term_ents[ic] = round(shannon_entropy(succ_by_iclass_term[ic][term]), 4)
            else:
                term_ents[ic] = None
        term_decomp[term] = term_ents

    return {
        'entropies': entropies,
        'single_i_minus_double_ii': round(real_diff, 4),
        'perm_p': round(float(perm_p), 4),
        'significant': bool(perm_p < 0.01),
        'terminal_decomposition': term_decomp,
    }


# ============================================================
# T6: Kernel Co-occurrence
# ============================================================
def run_t6(b_tokens):
    """Test kernel composition of ii-lines vs i-lines vs no-i lines."""
    line_data = defaultdict(lambda: {'tokens': [], 'ii_count': 0, 'i_count': 0, 'total': 0})

    for tok in b_tokens:
        key = (tok['folio'], tok['line'])
        ld = line_data[key]
        ld['tokens'].append(tok)
        ld['total'] += 1
        if tok['i_class'] == 'double_ii':
            ld['ii_count'] += 1
        elif tok['i_class'] == 'single_i':
            ld['i_count'] += 1
        ld['folio'] = tok['folio']
        ld['section'] = tok['section']

    # Kernel fractions per line
    line_records = []
    for key, ld in line_data.items():
        if ld['total'] < 3:
            continue
        n_k = sum(1 for t in ld['tokens'] if t['head'] == 'k')
        n_e = sum(1 for t in ld['tokens'] if t['head'] == 'e')
        n_a = sum(1 for t in ld['tokens'] if t['head'] == 'a')
        n_o = sum(1 for t in ld['tokens'] if t['head'] == 'o')
        n_t = sum(1 for t in ld['tokens'] if t['head'] == 't')

        ii_frac = ld['ii_count'] / ld['total']

        line_records.append({
            'folio': ld['folio'],
            'section': ld['section'],
            'ii_fraction': ii_frac,
            'has_ii': ld['ii_count'] > 0,
            'has_i_only': ld['i_count'] > 0 and ld['ii_count'] == 0,
            'k_frac': n_k / ld['total'],
            'e_frac': n_e / ld['total'],
            'a_frac': n_a / ld['total'],
        })

    # Spearman correlations (continuous ii_fraction)
    ii_fracs = np.array([r['ii_fraction'] for r in line_records])
    k_fracs = np.array([r['k_frac'] for r in line_records])
    e_fracs = np.array([r['e_frac'] for r in line_records])
    a_fracs = np.array([r['a_frac'] for r in line_records])

    if len(set(ii_fracs)) > 1:
        k_rho, k_p = stats.spearmanr(ii_fracs, k_fracs)
        e_rho, e_p = stats.spearmanr(ii_fracs, e_fracs)
        a_rho, a_p = stats.spearmanr(ii_fracs, a_fracs)
    else:
        k_rho = k_p = e_rho = e_p = a_rho = a_p = 0.0

    # Within-folio correlations (remove folio-level confound per C1205)
    folio_records = defaultdict(list)
    for r in line_records:
        folio_records[r['folio']].append(r)

    within_folio_rhos = {'k': [], 'e': [], 'a': []}
    for folio, recs in folio_records.items():
        if len(recs) < 5:
            continue
        ii_f = [r['ii_fraction'] for r in recs]
        if len(set(ii_f)) <= 1:
            continue
        k_f = [r['k_frac'] for r in recs]
        e_f = [r['e_frac'] for r in recs]
        a_f = [r['a_frac'] for r in recs]
        r_k, _ = stats.spearmanr(ii_f, k_f)
        r_e, _ = stats.spearmanr(ii_f, e_f)
        r_a, _ = stats.spearmanr(ii_f, a_f)
        within_folio_rhos['k'].append(float(r_k))
        within_folio_rhos['e'].append(float(r_e))
        within_folio_rhos['a'].append(float(r_a))

    return {
        'n_lines': len(line_records),
        'corpus_correlations': {
            'k_rho': round(float(k_rho), 4), 'k_p': round(float(k_p), 6),
            'e_rho': round(float(e_rho), 4), 'e_p': round(float(e_p), 6),
            'a_rho': round(float(a_rho), 4), 'a_p': round(float(a_p), 6),
        },
        'within_folio_mean_rhos': {
            'k': round(float(np.mean(within_folio_rhos['k'])), 4) if within_folio_rhos['k'] else None,
            'e': round(float(np.mean(within_folio_rhos['e'])), 4) if within_folio_rhos['e'] else None,
            'a': round(float(np.mean(within_folio_rhos['a'])), 4) if within_folio_rhos['a'] else None,
            'n_folios': len(within_folio_rhos['k']),
        },
    }


# ============================================================
# T7: Redistillation vs Safety Discrimination (CRITICAL)
# ============================================================
def run_t7(b_tokens, rng):
    """Critical test: do non-ii tokens on ii-lines have higher or lower hazard?"""
    # Group tokens by line
    line_tokens = defaultdict(list)
    for tok in b_tokens:
        line_tokens[(tok['folio'], tok['line'])].append(tok)

    # Classify lines
    ii_lines = []  # Lines with at least one double-ii token
    no_ii_lines = []  # Lines without any double-ii token

    for key, toks in line_tokens.items():
        has_ii = any(t['i_class'] == 'double_ii' for t in toks)
        if has_ii:
            ii_lines.append(toks)
        else:
            no_ii_lines.append(toks)

    # Hazard rate of NON-ii tokens on ii-lines
    non_ii_on_ii_lines = []
    for toks in ii_lines:
        for t in toks:
            if t['i_class'] != 'double_ii':
                non_ii_on_ii_lines.append(t)

    non_ii_on_no_ii_lines = []
    for toks in no_ii_lines:
        for t in toks:
            non_ii_on_no_ii_lines.append(t)

    haz_ii_context = sum(1 for t in non_ii_on_ii_lines if t['hazardous']) / len(non_ii_on_ii_lines) if non_ii_on_ii_lines else 0.0
    haz_no_ii_context = sum(1 for t in non_ii_on_no_ii_lines if t['hazardous']) / len(non_ii_on_no_ii_lines) if non_ii_on_no_ii_lines else 0.0

    haz_diff = haz_ii_context - haz_no_ii_context

    # Permutation test: shuffle ii-token assignments across lines
    all_lines = list(line_tokens.values())
    all_ii_flags = []
    for toks in all_lines:
        for t in toks:
            all_ii_flags.append(t['i_class'] == 'double_ii')

    perm_diffs = []
    for _ in range(N_SHUFFLES):
        shuffled_flags = all_ii_flags.copy()
        rng.shuffle(shuffled_flags)
        # Reassign flags to lines
        idx = 0
        perm_haz_ii = []
        perm_haz_no_ii = []
        for toks in all_lines:
            line_has_ii = False
            line_flags = []
            for _ in toks:
                flag = shuffled_flags[idx]
                line_flags.append(flag)
                if flag:
                    line_has_ii = True
                idx += 1
            for t, flag in zip(toks, line_flags):
                if line_has_ii and not flag:
                    perm_haz_ii.append(t['hazardous'])
                elif not line_has_ii:
                    perm_haz_no_ii.append(t['hazardous'])
        if perm_haz_ii and perm_haz_no_ii:
            pd = (sum(perm_haz_ii) / len(perm_haz_ii)) - (sum(perm_haz_no_ii) / len(perm_haz_no_ii))
        else:
            pd = 0.0
        perm_diffs.append(pd)

    perm_p = np.mean(np.abs(perm_diffs) >= abs(haz_diff))

    # Determine direction
    if haz_diff > 0:
        direction = 'SAFETY'
        interpretation = 'Non-ii tokens on ii-lines have HIGHER hazard -> ii deployed for protection'
    elif haz_diff < 0:
        direction = 'REDISTILLATION'
        interpretation = 'Non-ii tokens on ii-lines have LOWER hazard -> ii-lines are inherently safe contexts'
    else:
        direction = 'NEUTRAL'
        interpretation = 'No difference in hazard context'

    return {
        'n_ii_lines': len(ii_lines),
        'n_no_ii_lines': len(no_ii_lines),
        'n_non_ii_on_ii_lines': len(non_ii_on_ii_lines),
        'n_non_ii_on_no_ii_lines': len(non_ii_on_no_ii_lines),
        'hazard_rate_ii_context': round(haz_ii_context, 4),
        'hazard_rate_no_ii_context': round(haz_no_ii_context, 4),
        'hazard_difference': round(haz_diff, 4),
        'perm_p': round(float(perm_p), 4),
        'significant': bool(perm_p < 0.01),
        'direction': direction,
        'interpretation': interpretation,
    }


# ============================================================
# T8: Cross-System i-Extension
# ============================================================
def run_t8(b_tokens, a_tokens):
    """Compare i-extension distributions between Currier A and B."""
    b_dist = Counter(t['i_class'] for t in b_tokens)
    a_dist = Counter(t['i_class'] for t in a_tokens)

    # Chi-squared for system x i-extension
    classes = ['no_i', 'single_i', 'double_ii']
    contingency = np.array([
        [a_dist.get(c, 0) for c in classes],
        [b_dist.get(c, 0) for c in classes],
    ])
    if contingency.sum() > 0 and all(contingency.sum(axis=0) > 0):
        chi2, chi_p, dof, _ = stats.chi2_contingency(contingency)
    else:
        chi2, chi_p, dof = 0.0, 1.0, 0

    # Ratios
    a_total_i = a_dist.get('single_i', 0) + a_dist.get('double_ii', 0)
    b_total_i = b_dist.get('single_i', 0) + b_dist.get('double_ii', 0)
    a_ii_ratio = a_dist.get('double_ii', 0) / a_total_i if a_total_i > 0 else 0.0
    b_ii_ratio = b_dist.get('double_ii', 0) / b_total_i if b_total_i > 0 else 0.0

    # Section-level within B
    b_section_dist = defaultdict(Counter)
    for t in b_tokens:
        b_section_dist[t['section']][t['i_class']] += 1

    section_ratios = {}
    for sec in sorted(b_section_dist.keys()):
        si = b_section_dist[sec].get('single_i', 0)
        di = b_section_dist[sec].get('double_ii', 0)
        total = si + di
        section_ratios[sec] = {
            'single_i': si,
            'double_ii': di,
            'ii_ratio': round(di / total, 4) if total > 0 else 0.0,
        }

    return {
        'currier_a': {
            'no_i': a_dist.get('no_i', 0),
            'single_i': a_dist.get('single_i', 0),
            'double_ii': a_dist.get('double_ii', 0),
            'ii_ratio': round(a_ii_ratio, 4),
            'total': sum(a_dist.values()),
        },
        'currier_b': {
            'no_i': b_dist.get('no_i', 0),
            'single_i': b_dist.get('single_i', 0),
            'double_ii': b_dist.get('double_ii', 0),
            'ii_ratio': round(b_ii_ratio, 4),
            'total': sum(b_dist.values()),
        },
        'chi2': round(float(chi2), 2),
        'chi_p': round(float(chi_p), 6),
        'significant': bool(chi_p < 0.01),
        'b_depleted_ii': bool(b_ii_ratio < a_ii_ratio),
        'b_section_ratios': section_ratios,
    }


# ============================================================
# VERDICT
# ============================================================
def compute_verdict(t1, t2, t3, t4, t5, t6, t7, t8):
    """Determine overall verdict following decision logic."""
    # T7 is the decision gate
    if t7['direction'] == 'SAFETY' and t7['significant']:
        verdict = 'SAFETY_ONLY'
        note = 'T7 shows ii deployed in high-hazard contexts -> safety mechanism (C1480-C1482) sufficient'
    elif t7['direction'] == 'REDISTILLATION':
        # Count supporting tests
        passes = 0
        test_results = {}

        # T1
        t1_pass = t1.get('significant', False)
        test_results['T1'] = t1_pass
        if t1_pass:
            passes += 1

        # T2
        t2_pass = t2.get('overdispersed', False)
        test_results['T2'] = t2_pass
        if t2_pass:
            passes += 1

        # T4
        t4_pass = t4.get('significant', False) and t4.get('regime_3_highest', False) and not t4.get('hazard_confound', {}).get('confounded', False)
        test_results['T4'] = t4_pass
        if t4_pass:
            passes += 1

        # T5
        t5_pass = t5.get('significant', False)
        test_results['T5'] = t5_pass
        if t5_pass:
            passes += 1

        # T6 (check if within-folio correlations exist and are meaningful)
        wf = t6.get('within_folio_mean_rhos', {})
        t6_pass = wf.get('e') is not None and wf['e'] > 0.05
        test_results['T6'] = t6_pass
        if t6_pass:
            passes += 1

        # T8
        t8_pass = t8.get('significant', False)
        test_results['T8'] = t8_pass
        if t8_pass:
            passes += 1

        if passes >= 4:
            verdict = 'REDISTILLATION_SUPPORTED'
        elif passes >= 2:
            verdict = 'REDISTILLATION_SUGGESTIVE'
        else:
            verdict = 'TOKEN_LEVEL_ONLY'

        # Paragraph sub-verdict
        if t1_pass and not t2_pass:
            par_verdict = 'WITHIN_PARAGRAPH'
        elif t2_pass and not t1_pass:
            par_verdict = 'PARAGRAPH_TYPE'
        elif t1_pass and t2_pass:
            par_verdict = 'MIXED'
        else:
            par_verdict = 'NO_PARAGRAPH_SIGNAL'

        note = f'{passes}/6 supporting tests pass. Paragraph: {par_verdict}. Tests: {test_results}'
    else:
        # T7 neutral or not significant
        verdict = 'INCONCLUSIVE'
        note = f'T7 direction={t7["direction"]}, significant={t7["significant"]}. Cannot discriminate.'

    # T3 C1399 check
    c1399_note = 'C1399 CONFIRMED (null)' if t3.get('c1399_confirmed', True) else 'C1399 TENSION (significant ordinal trend)'

    return verdict, note, c1399_note


# ============================================================
# MAIN
# ============================================================
def main():
    start = time.time()
    rng = np.random.RandomState(SEED)

    print("Phase 596: Redistillation-i Hypothesis")
    print("=" * 60)

    print("\nAssembling data...")
    b_tokens, a_tokens, paragraphs, line_index = assemble_data()

    # Verification counts
    i_counts = Counter(t['i_class'] for t in b_tokens)
    i_containing = i_counts.get('single_i', 0) + i_counts.get('double_ii', 0)
    ii_ratio = i_counts.get('double_ii', 0) / i_containing if i_containing > 0 else 0.0
    print(f"  B tokens: {len(b_tokens)}")
    print(f"  A tokens: {len(a_tokens)}")
    print(f"  Paragraphs: {len(paragraphs)}")
    print(f"  i-class: no_i={i_counts.get('no_i', 0)}, single_i={i_counts.get('single_i', 0)}, double_ii={i_counts.get('double_ii', 0)}")
    print(f"  ii/(i+ii) ratio: {ii_ratio:.4f}")

    print("\nT1: Within-paragraph positional distribution...")
    t1 = run_t1(paragraphs, rng)
    print(f"  ii-fraction by quintile: {t1['ii_fraction_by_quintile']}")
    print(f"  Rho: {t1['rho']}, perm_p: {t1['perm_p']}, significant: {t1['significant']}")
    print(f"  a-HEAD control rho: {t1['a_head_control']['rho']}")

    print("\nT2: Paragraph type discrimination...")
    t2 = run_t2(paragraphs)
    if 'status' not in t2:
        print(f"  Overdispersion ratio: {t2['overdispersion_ratio']} (>2.0 = real types)")
        print(f"  Overdispersed: {t2['overdispersed']}")
        print(f"  Low-group hazard: {t2['low_group_hazard']}, High-group hazard: {t2['high_group_hazard']}")
    else:
        print(f"  {t2['status']}")

    print("\nT3: Paragraph ordinal (C1399 negative control)...")
    t3 = run_t3(paragraphs, rng)
    if 'status' not in t3:
        print(f"  Stouffer z: {t3['stouffer_z']}, perm_p: {t3['perm_p']}")
        print(f"  C1399 confirmed: {t3['c1399_confirmed']}")
    else:
        print(f"  {t3['status']}")

    print("\nT4: REGIME enrichment...")
    t4 = run_t4(b_tokens)
    for r, data in sorted(t4['regime_ratios'].items()):
        print(f"  {r}: ii_ratio={data['ii_ratio']}, hazard={data['hazard_rate']}, n={data['total_i']}")
    print(f"  Chi2={t4['chi2']}, p={t4['chi_p']}, significant: {t4['significant']}")
    print(f"  REGIME_3 highest: {t4['regime_3_highest']}")
    print(f"  Hazard confound: corr={t4['hazard_confound']['ii_hazard_correlation']}, confounded={t4['hazard_confound']['confounded']}")

    print("\nT5: Successor entropy...")
    t5 = run_t5(b_tokens, rng)
    for ic, data in t5['entropies'].items():
        print(f"  {ic}: entropy={data['entropy']} bits, n={data['n_pairs']}")
    print(f"  single_i - double_ii = {t5['single_i_minus_double_ii']} bits")
    print(f"  perm_p: {t5['perm_p']}, significant: {t5['significant']}")

    print("\nT6: Kernel co-occurrence...")
    t6 = run_t6(b_tokens)
    cc = t6['corpus_correlations']
    print(f"  Corpus: k_rho={cc['k_rho']} (p={cc['k_p']}), e_rho={cc['e_rho']} (p={cc['e_p']}), a_rho={cc['a_rho']} (p={cc['a_p']})")
    wf = t6['within_folio_mean_rhos']
    print(f"  Within-folio mean: k={wf['k']}, e={wf['e']}, a={wf['a']} (n={wf['n_folios']})")

    print("\nT7: Redistillation vs Safety discrimination (CRITICAL)...")
    t7 = run_t7(b_tokens, rng)
    print(f"  ii-lines: {t7['n_ii_lines']}, no-ii lines: {t7['n_no_ii_lines']}")
    print(f"  Hazard rate (non-ii on ii-lines): {t7['hazard_rate_ii_context']}")
    print(f"  Hazard rate (non-ii on no-ii lines): {t7['hazard_rate_no_ii_context']}")
    print(f"  Difference: {t7['hazard_difference']}")
    print(f"  Direction: {t7['direction']}, perm_p: {t7['perm_p']}")
    print(f"  {t7['interpretation']}")

    print("\nT8: Cross-system i-extension...")
    t8 = run_t8(b_tokens, a_tokens)
    print(f"  Currier A: ii_ratio={t8['currier_a']['ii_ratio']} (n={t8['currier_a']['total']})")
    print(f"  Currier B: ii_ratio={t8['currier_b']['ii_ratio']} (n={t8['currier_b']['total']})")
    print(f"  Chi2={t8['chi2']}, p={t8['chi_p']}, significant: {t8['significant']}")
    print(f"  B sections: {t8['b_section_ratios']}")

    # Verdict
    verdict, note, c1399_note = compute_verdict(t1, t2, t3, t4, t5, t6, t7, t8)

    elapsed = round(time.time() - start, 1)
    print(f"\n{'=' * 60}")
    print(f"VERDICT: {verdict}")
    print(f"  {note}")
    print(f"  {c1399_note}")
    print(f"{'=' * 60}")
    print(f"\nRuntime: {elapsed}s")

    # Save results
    results = {
        'metadata': {
            'phase': 596,
            'script': 'redistillation_i_test.py',
            'runtime_seconds': elapsed,
            'n_b_tokens': len(b_tokens),
            'n_a_tokens': len(a_tokens),
            'n_paragraphs': len(paragraphs),
            'seed': SEED,
            'i_class_counts': dict(i_counts),
            'ii_ratio_among_i': round(ii_ratio, 4),
        },
        'T1_within_paragraph': t1,
        'T2_paragraph_type': t2,
        'T3_ordinal_control': t3,
        'T4_regime': t4,
        'T5_successor_entropy': t5,
        'T6_kernel': t6,
        'T7_discrimination': t7,
        'T8_cross_system': t8,
        'verdict': verdict,
        'verdict_note': note,
        'c1399_note': c1399_note,
    }

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, 'redistillation_i_results.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)

    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
