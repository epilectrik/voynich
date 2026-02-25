#!/usr/bin/env python3
"""
Phase 459: SISTER_CATEGORY_MECHANISM
=============================================

Tests whether sister pair PREFIX divergence (ch/sh and ok/ot) is driven by
category selection vs positional routing.

Core question: Do sister pairs have different category profiles even at the
same line position? If yes, sister encodes operational mode. If no, sister
is a pure positional router.

Tests:
  T1: Raw category divergence baseline (reproduce C1299 for ch/sh, C1298 for ok/ot)
  T2: Position-controlled ch/sh divergence (within position-thirds)
  T3: MIDDLE category shift by sister (same MIDDLE, different PREFIX -> different category?)
  T4: Cross-lane category cargo (ch->QO vs sh->QO category profiles)
  T5: Position-controlled ok/ot divergence (parallel to T2)
  T6: Three-way interaction: sister x category x position

Bonferroni: p < 0.00833 (6 tests)
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

# ============================================================
# Category assignment pipeline (from Phase 458)
# ============================================================

CATEGORIES = ['CONTAINMENT', 'FLOW', 'MARKING', 'MONITORING',
              'OPERATION', 'STAGING', 'THERMAL', 'TRANSITION']

GLOSS_TO_CATEGORY = {
    'seal': 'CONTAINMENT', 'hold': 'CONTAINMENT', 'lock': 'CONTAINMENT',
    'bind': 'CONTAINMENT', 'bond': 'CONTAINMENT', 'rigid': 'CONTAINMENT',
    'firm': 'CONTAINMENT', 'dense': 'CONTAINMENT',
    'transfer': 'FLOW', 'pour': 'FLOW', 'drain': 'FLOW', 'input': 'FLOW',
    'flow': 'FLOW', 'draw': 'FLOW', 'feed': 'FLOW', 'vent': 'FLOW',
    'move': 'FLOW', 'pipe': 'FLOW', 'route': 'FLOW',
    'mark': 'MARKING', 'flag': 'MARKING', 'note': 'MARKING',
    'pause': 'MARKING', 'diagram': 'MARKING', 'hazard': 'MARKING',
    'danger': 'MARKING', 'link': 'MARKING', 'adjust': 'MARKING',
    'watch': 'MONITORING', 'observe': 'MONITORING', 'check': 'MONITORING',
    'measure': 'MONITORING', 'test': 'MONITORING', 'gauge': 'MONITORING',
    'work': 'OPERATION', 'act': 'OPERATION', 'run': 'OPERATION',
    'execute': 'OPERATION', 'do': 'OPERATION', 'process': 'OPERATION',
    'operate': 'OPERATION',
    'prepare': 'STAGING', 'setup': 'STAGING', 'stage': 'STAGING',
    'ready': 'STAGING', 'prime': 'STAGING', 'load': 'STAGING',
    'charge': 'STAGING', 'frame': 'STAGING', 'yield': 'STAGING',
    'iterate': 'STAGING', 'repeat': 'STAGING', 'cycle': 'STAGING',
    'sequence': 'STAGING',
    'heat': 'THERMAL', 'cool': 'THERMAL', 'fire': 'THERMAL',
    'sustain': 'THERMAL', 'pulse': 'THERMAL', 'steady': 'THERMAL',
    'extended': 'THERMAL', 'deep': 'THERMAL', 'long': 'THERMAL',
    'overnight': 'THERMAL',
    'end': 'TRANSITION', 'halt': 'TRANSITION', 'stop': 'TRANSITION',
    'finish': 'TRANSITION', 'complete': 'TRANSITION', 'final': 'TRANSITION',
    'close': 'TRANSITION', 'done': 'TRANSITION', 'shift': 'TRANSITION',
    'change': 'TRANSITION', 'switch': 'TRANSITION', 'transition': 'TRANSITION',
}

ATOM_GLOSSES = {
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'halt', 'a': 'yield', 'm': 'final',
    'd': 'mark', 't': 'transfer', 'c': 'adjust', 'p': 'pause',
    'f': 'flag', 's': 'sequence', 'g': 'complete', 'o': 'work',
    'l': 'frame', 'r': 'input',
}
ATOM_TO_CATEGORY = {a: GLOSS_TO_CATEGORY[g] for a, g in ATOM_GLOSSES.items()}


def auto_assign_category(atoms_str):
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


# ============================================================
# Data loading
# ============================================================

def load_data():
    """Load Currier B tokens with category, position, and PREFIX info."""
    tx = Transcript()
    morph = Morphology()
    mid_to_cat = build_category_map()

    # Group tokens by (folio, line) for position computation
    folio_line_tokens = defaultdict(list)
    for token in tx.currier_b():
        w = token.word
        if not w.strip() or '*' in w:
            continue
        if token.placement.startswith('L'):
            continue
        folio_line_tokens[(token.folio, token.line)].append(token)

    records = []
    for (folio, line), tokens in folio_line_tokens.items():
        n_tok = len(tokens)
        for idx, token in enumerate(tokens):
            w = token.word
            m = morph.extract(w)
            prefix = m.prefix or ''
            middle = m.middle or ''
            suffix = m.suffix or ''

            # Category assignment
            cat = mid_to_cat.get(middle)
            if not cat and middle:
                cat = auto_assign_category(middle)
            if not cat:
                continue

            # Fractional position
            pos_norm = idx / max(n_tok - 1, 1)

            # Position zone (thirds)
            if n_tok <= 3:
                pos_zone = 'MID'
            elif pos_norm < 0.333:
                pos_zone = 'EARLY'
            elif pos_norm > 0.667:
                pos_zone = 'LATE'
            else:
                pos_zone = 'MID'

            records.append({
                'folio': folio,
                'line': line,
                'word': w,
                'prefix': prefix if prefix else 'BARE',
                'middle': middle,
                'suffix': suffix,
                'category': cat,
                'pos_norm': pos_norm,
                'pos_zone': pos_zone,
                'idx': idx,
                'n_tok': n_tok,
            })

    return records


# ============================================================
# Statistical helpers
# ============================================================

def cramers_v(ct):
    """Cramer's V from a contingency table (2D numpy array)."""
    chi2 = stats.chi2_contingency(ct)[0]
    n = ct.sum()
    r, c = ct.shape
    return np.sqrt(chi2 / (n * (min(r, c) - 1))) if n > 0 and min(r, c) > 1 else 0.0


def contingency_test(group_a, group_b, categories):
    """Chi-squared test on 2 x len(categories) contingency table."""
    ct = np.zeros((2, len(categories)), dtype=int)
    for cat in group_a:
        if cat in categories:
            ct[0, categories.index(cat)] += 1
    for cat in group_b:
        if cat in categories:
            ct[1, categories.index(cat)] += 1

    # Remove zero columns
    nonzero = ct.sum(axis=0) > 0
    ct_clean = ct[:, nonzero]
    if ct_clean.shape[1] < 2:
        return {'chi2': 0, 'p': 1.0, 'dof': 0, 'V': 0, 'n': int(ct.sum())}

    chi2, p, dof, _ = stats.chi2_contingency(ct_clean)
    n = ct_clean.sum()
    r, c = ct_clean.shape
    V = np.sqrt(chi2 / (n * (min(r, c) - 1))) if n > 0 and min(r, c) > 1 else 0.0

    # Profiles
    totals = ct.sum(axis=1, keepdims=True)
    profiles = ct / np.where(totals > 0, totals, 1)

    return {'chi2': float(chi2), 'p': float(p), 'dof': int(dof), 'V': float(V),
            'n': int(n), 'profiles': {categories[i]: [float(profiles[0, i]), float(profiles[1, i])]
                                       for i in range(len(categories))}}


def jsd(p, q):
    """Jensen-Shannon divergence."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    p = p / p.sum() if p.sum() > 0 else p
    q = q / q.sum() if q.sum() > 0 else q
    m = 0.5 * (p + q)
    kl_pm = np.sum(p * np.log2(p / m + 1e-15) * (p > 0))
    kl_qm = np.sum(q * np.log2(q / m + 1e-15) * (q > 0))
    return 0.5 * (kl_pm + kl_qm)


# ============================================================
# Tests
# ============================================================

BONFERRONI_P = 0.05 / 6  # 0.00833


def t1_raw_divergence(records):
    """T1: Raw category divergence baseline for ch/sh and ok/ot."""
    ch_cats = [r['category'] for r in records if r['prefix'] == 'ch']
    sh_cats = [r['category'] for r in records if r['prefix'] == 'sh']
    ok_cats = [r['category'] for r in records if r['prefix'] == 'ok']
    ot_cats = [r['category'] for r in records if r['prefix'] == 'ot']

    chsh = contingency_test(ch_cats, sh_cats, CATEGORIES)
    okot = contingency_test(ok_cats, ot_cats, CATEGORIES)

    return {
        'test': 'T1_raw_divergence',
        'ch_sh': {
            'n_ch': len(ch_cats), 'n_sh': len(sh_cats),
            **chsh,
            'verdict': 'PASS' if chsh['p'] < BONFERRONI_P else 'FAIL',
        },
        'ok_ot': {
            'n_ok': len(ok_cats), 'n_ot': len(ot_cats),
            **okot,
            'verdict': 'PASS' if okot['p'] < BONFERRONI_P else 'FAIL',
        },
        'verdict': 'PASS',  # Baseline reproduction
    }


def t2_position_controlled_chsh(records):
    """T2: ch/sh category divergence within each position zone."""
    zones = ['EARLY', 'MID', 'LATE']
    zone_results = {}
    fisher_stats = []

    for zone in zones:
        ch_cats = [r['category'] for r in records if r['prefix'] == 'ch' and r['pos_zone'] == zone]
        sh_cats = [r['category'] for r in records if r['prefix'] == 'sh' and r['pos_zone'] == zone]

        if len(ch_cats) < 30 or len(sh_cats) < 30:
            zone_results[zone] = {'n_ch': len(ch_cats), 'n_sh': len(sh_cats),
                                  'verdict': 'SKIP_LOW_N'}
            continue

        result = contingency_test(ch_cats, sh_cats, CATEGORIES)
        zone_results[zone] = {
            'n_ch': len(ch_cats), 'n_sh': len(sh_cats),
            **result,
        }
        if result['p'] > 0:
            fisher_stats.append(-2 * np.log(result['p']))
        else:
            fisher_stats.append(100.0)  # cap for p~0

    # Fisher-combined p across zones
    if fisher_stats:
        fisher_stat = sum(fisher_stats)
        fisher_dof = 2 * len(fisher_stats)
        fisher_p = float(stats.chi2.sf(fisher_stat, fisher_dof))
    else:
        fisher_stat, fisher_dof, fisher_p = 0, 0, 1.0

    # Key question: does V remain significant within zones?
    within_Vs = [zone_results[z]['V'] for z in zones if 'V' in zone_results.get(z, {})]
    mean_within_V = float(np.mean(within_Vs)) if within_Vs else 0.0

    # Compare to raw V
    raw_V = contingency_test(
        [r['category'] for r in records if r['prefix'] == 'ch'],
        [r['category'] for r in records if r['prefix'] == 'sh'],
        CATEGORIES
    )['V']

    v_retention = mean_within_V / raw_V if raw_V > 0 else 0.0

    verdict = 'PASS' if fisher_p < BONFERRONI_P else 'FAIL'
    interpretation = ('CATEGORY_GENUINE' if v_retention > 0.5 else
                      'POSITION_DOMINANT' if v_retention < 0.25 else
                      'MIXED')

    return {
        'test': 'T2_position_controlled_ch_sh',
        'zones': zone_results,
        'fisher_stat': float(fisher_stat),
        'fisher_dof': fisher_dof,
        'fisher_p': fisher_p,
        'raw_V': float(raw_V),
        'mean_within_V': mean_within_V,
        'V_retention': float(v_retention),
        'interpretation': interpretation,
        'verdict': verdict,
    }


def t3_middle_category_shift(records):
    """T3: Does the same MIDDLE change category distribution by sister?"""
    # For MIDDLEs that appear with both ch and sh
    ch_mid_cats = defaultdict(list)
    sh_mid_cats = defaultdict(list)

    for r in records:
        if r['prefix'] == 'ch':
            ch_mid_cats[r['middle']].append(r['category'])
        elif r['prefix'] == 'sh':
            sh_mid_cats[r['middle']].append(r['category'])

    shared_middles = set(ch_mid_cats.keys()) & set(sh_mid_cats.keys())
    # Require at least 10 tokens each
    qualifying = [mid for mid in shared_middles
                  if len(ch_mid_cats[mid]) >= 10 and len(sh_mid_cats[mid]) >= 10]

    mid_results = {}
    n_shifted = 0
    n_tested = 0
    shift_magnitudes = []

    for mid in sorted(qualifying):
        ch_cats = ch_mid_cats[mid]
        sh_cats = sh_mid_cats[mid]

        # Category distribution for this MIDDLE under ch vs sh
        ch_profile = np.zeros(len(CATEGORIES))
        sh_profile = np.zeros(len(CATEGORIES))
        for c in ch_cats:
            ch_profile[CATEGORIES.index(c)] += 1
        for c in sh_cats:
            sh_profile[CATEGORIES.index(c)] += 1

        ch_frac = ch_profile / ch_profile.sum() if ch_profile.sum() > 0 else ch_profile
        sh_frac = sh_profile / sh_profile.sum() if sh_profile.sum() > 0 else sh_profile

        j = float(jsd(ch_frac, sh_frac))
        shift_magnitudes.append(j)

        # Fisher exact or chi2 depending on N
        ct = np.array([ch_profile, sh_profile], dtype=int)
        nonzero = ct.sum(axis=0) > 0
        ct_clean = ct[:, nonzero]

        if ct_clean.shape[1] >= 2 and ct_clean.sum() >= 20:
            try:
                chi2, p, dof, _ = stats.chi2_contingency(ct_clean)
                sig = p < 0.05  # per-MIDDLE threshold (not Bonferroni)
            except ValueError:
                sig = False
                p = 1.0
        else:
            sig = False
            p = 1.0

        if sig:
            n_shifted += 1
        n_tested += 1

        ch_dom = CATEGORIES[int(np.argmax(ch_frac))]
        sh_dom = CATEGORIES[int(np.argmax(sh_frac))]

        mid_results[mid] = {
            'n_ch': len(ch_cats), 'n_sh': len(sh_cats),
            'ch_dominant': ch_dom, 'sh_dominant': sh_dom,
            'same_dominant': ch_dom == sh_dom,
            'JSD': j,
            'p': float(p),
            'shifted': sig,
        }

    # Summary: how many MIDDLEs show category shift?
    shift_rate = n_shifted / n_tested if n_tested > 0 else 0.0
    mean_jsd = float(np.mean(shift_magnitudes)) if shift_magnitudes else 0.0

    # Null: if category is purely MIDDLE-determined (no sister effect),
    # shift_rate should be near alpha (0.05)
    binom_p = float(stats.binomtest(n_shifted, n_tested, 0.05, alternative='greater').pvalue) if n_tested > 0 else 1.0

    # How many change DOMINANT category?
    n_dom_change = sum(1 for v in mid_results.values() if not v['same_dominant'])

    verdict = 'PASS' if binom_p < BONFERRONI_P else 'FAIL'
    interpretation = ('SISTER_MODULATES_CATEGORY' if shift_rate > 0.20 else
                      'MIDDLE_DETERMINES_CATEGORY' if shift_rate < 0.10 else
                      'WEAK_MODULATION')

    return {
        'test': 'T3_middle_category_shift',
        'n_shared_middles': len(shared_middles),
        'n_qualifying': len(qualifying),
        'n_tested': n_tested,
        'n_shifted': n_shifted,
        'shift_rate': float(shift_rate),
        'binom_p': float(binom_p),
        'n_dominant_changed': n_dom_change,
        'mean_JSD': mean_jsd,
        'top_shifted': {k: v for k, v in sorted(mid_results.items(),
                        key=lambda x: -x[1]['JSD'])[:10]},
        'interpretation': interpretation,
        'verdict': verdict,
    }


def t4_cross_lane_cargo(records):
    """T4: Do ch->QO and sh->QO transitions carry different category cargo?"""
    # Find consecutive token pairs where first is ch/sh and second is qo-lane
    QO_PREFIXES = {'qo', 'ok', 'ot', 'ko', 'to', 'po', 'so', 'do'}

    # Group records by (folio, line) preserving order
    line_tokens = defaultdict(list)
    for r in records:
        line_tokens[(r['folio'], r['line'])].append(r)

    ch_to_qo_cats = []  # category of the QO token after ch
    sh_to_qo_cats = []  # category of the QO token after sh

    for (folio, line), tokens in line_tokens.items():
        for i in range(len(tokens) - 1):
            curr = tokens[i]
            nxt = tokens[i + 1]
            if nxt['prefix'] in QO_PREFIXES:
                if curr['prefix'] == 'ch':
                    ch_to_qo_cats.append(nxt['category'])
                elif curr['prefix'] == 'sh':
                    sh_to_qo_cats.append(nxt['category'])

    if len(ch_to_qo_cats) < 30 or len(sh_to_qo_cats) < 30:
        return {
            'test': 'T4_cross_lane_cargo',
            'n_ch_to_qo': len(ch_to_qo_cats),
            'n_sh_to_qo': len(sh_to_qo_cats),
            'verdict': 'SKIP_LOW_N',
        }

    result = contingency_test(ch_to_qo_cats, sh_to_qo_cats, CATEGORIES)

    # Also test: category of ch/sh token ITSELF when followed by QO
    ch_self_cats = []
    sh_self_cats = []
    for (folio, line), tokens in line_tokens.items():
        for i in range(len(tokens) - 1):
            curr = tokens[i]
            nxt = tokens[i + 1]
            if nxt['prefix'] in QO_PREFIXES:
                if curr['prefix'] == 'ch':
                    ch_self_cats.append(curr['category'])
                elif curr['prefix'] == 'sh':
                    sh_self_cats.append(curr['category'])

    self_result = contingency_test(ch_self_cats, sh_self_cats, CATEGORIES)

    return {
        'test': 'T4_cross_lane_cargo',
        'n_ch_to_qo': len(ch_to_qo_cats),
        'n_sh_to_qo': len(sh_to_qo_cats),
        'qo_cargo': result,
        'self_category_at_transition': {
            'n_ch': len(ch_self_cats), 'n_sh': len(sh_self_cats),
            **self_result,
        },
        'verdict': 'PASS' if result['p'] < BONFERRONI_P else 'FAIL',
    }


def t5_position_controlled_okot(records):
    """T5: ok/ot category divergence within each position zone."""
    zones = ['EARLY', 'MID', 'LATE']
    zone_results = {}
    fisher_stats = []

    for zone in zones:
        ok_cats = [r['category'] for r in records if r['prefix'] == 'ok' and r['pos_zone'] == zone]
        ot_cats = [r['category'] for r in records if r['prefix'] == 'ot' and r['pos_zone'] == zone]

        if len(ok_cats) < 30 or len(ot_cats) < 30:
            zone_results[zone] = {'n_ok': len(ok_cats), 'n_ot': len(ot_cats),
                                  'verdict': 'SKIP_LOW_N'}
            continue

        result = contingency_test(ok_cats, ot_cats, CATEGORIES)
        zone_results[zone] = {
            'n_ok': len(ok_cats), 'n_ot': len(ot_cats),
            **result,
        }
        if result['p'] > 0:
            fisher_stats.append(-2 * np.log(result['p']))
        else:
            fisher_stats.append(100.0)

    if fisher_stats:
        fisher_stat = sum(fisher_stats)
        fisher_dof = 2 * len(fisher_stats)
        fisher_p = float(stats.chi2.sf(fisher_stat, fisher_dof))
    else:
        fisher_stat, fisher_dof, fisher_p = 0, 0, 1.0

    within_Vs = [zone_results[z]['V'] for z in zones if 'V' in zone_results.get(z, {})]
    mean_within_V = float(np.mean(within_Vs)) if within_Vs else 0.0

    raw_V = contingency_test(
        [r['category'] for r in records if r['prefix'] == 'ok'],
        [r['category'] for r in records if r['prefix'] == 'ot'],
        CATEGORIES
    )['V']

    v_retention = mean_within_V / raw_V if raw_V > 0 else 0.0

    verdict = 'PASS' if fisher_p < BONFERRONI_P else 'FAIL'
    interpretation = ('CATEGORY_GENUINE' if v_retention > 0.5 else
                      'POSITION_DOMINANT' if v_retention < 0.25 else
                      'MIXED')

    return {
        'test': 'T5_position_controlled_ok_ot',
        'zones': zone_results,
        'fisher_stat': float(fisher_stat),
        'fisher_dof': fisher_dof,
        'fisher_p': fisher_p,
        'raw_V': float(raw_V),
        'mean_within_V': mean_within_V,
        'V_retention': float(v_retention),
        'interpretation': interpretation,
        'verdict': verdict,
    }


def t6_three_way_interaction(records):
    """T6: sister x category x position three-way interaction test.

    Tests whether the sister-category association DIFFERS by position zone.
    If so, sister choice depends on both what category you need AND where in
    the line you are.
    """
    # For ch/sh: compute V(sister, category) within each zone
    zones = ['EARLY', 'MID', 'LATE']
    chsh_v_by_zone = {}

    for zone in zones:
        ch_cats = [r['category'] for r in records if r['prefix'] == 'ch' and r['pos_zone'] == zone]
        sh_cats = [r['category'] for r in records if r['prefix'] == 'sh' and r['pos_zone'] == zone]
        if len(ch_cats) >= 30 and len(sh_cats) >= 30:
            result = contingency_test(ch_cats, sh_cats, CATEGORIES)
            chsh_v_by_zone[zone] = result['V']
        else:
            chsh_v_by_zone[zone] = None

    # For ok/ot: same
    okot_v_by_zone = {}
    for zone in zones:
        ok_cats = [r['category'] for r in records if r['prefix'] == 'ok' and r['pos_zone'] == zone]
        ot_cats = [r['category'] for r in records if r['prefix'] == 'ot' and r['pos_zone'] == zone]
        if len(ok_cats) >= 30 and len(ot_cats) >= 30:
            result = contingency_test(ok_cats, ot_cats, CATEGORIES)
            okot_v_by_zone[zone] = result['V']
        else:
            okot_v_by_zone[zone] = None

    # Test whether V varies across zones (bootstrap)
    # If V is constant across zones -> no interaction
    # If V differs -> interaction exists
    chsh_Vs = [v for v in chsh_v_by_zone.values() if v is not None]
    okot_Vs = [v for v in okot_v_by_zone.values() if v is not None]

    chsh_v_range = max(chsh_Vs) - min(chsh_Vs) if len(chsh_Vs) >= 2 else 0.0
    okot_v_range = max(okot_Vs) - min(okot_Vs) if len(okot_Vs) >= 2 else 0.0

    # Permutation test: is the V-range larger than expected by chance?
    # Shuffle sister labels within each zone, recompute V per zone, measure range
    n_perm = 1000
    rng = np.random.RandomState(42)

    # ch/sh permutation
    chsh_by_zone = {}
    for zone in zones:
        chsh_zone = [(r['prefix'], r['category']) for r in records
                     if r['prefix'] in ('ch', 'sh') and r['pos_zone'] == zone]
        if len(chsh_zone) >= 60:
            chsh_by_zone[zone] = chsh_zone

    perm_ranges_chsh = []
    for _ in range(n_perm):
        perm_Vs = []
        for zone, pairs in chsh_by_zone.items():
            sisters = [p[0] for p in pairs]
            cats = [p[1] for p in pairs]
            rng.shuffle(sisters)
            ch_c = [c for s, c in zip(sisters, cats) if s == 'ch']
            sh_c = [c for s, c in zip(sisters, cats) if s == 'sh']
            if len(ch_c) >= 10 and len(sh_c) >= 10:
                r = contingency_test(ch_c, sh_c, CATEGORIES)
                perm_Vs.append(r['V'])
        if len(perm_Vs) >= 2:
            perm_ranges_chsh.append(max(perm_Vs) - min(perm_Vs))

    chsh_interaction_p = float(np.mean([1 for r in perm_ranges_chsh if r >= chsh_v_range])) if perm_ranges_chsh else 1.0

    # ok/ot permutation
    okot_by_zone = {}
    for zone in zones:
        okot_zone = [(r['prefix'], r['category']) for r in records
                     if r['prefix'] in ('ok', 'ot') and r['pos_zone'] == zone]
        if len(okot_zone) >= 60:
            okot_by_zone[zone] = okot_zone

    perm_ranges_okot = []
    for _ in range(n_perm):
        perm_Vs = []
        for zone, pairs in okot_by_zone.items():
            sisters = [p[0] for p in pairs]
            cats = [p[1] for p in pairs]
            rng.shuffle(sisters)
            ok_c = [c for s, c in zip(sisters, cats) if s == 'ok']
            ot_c = [c for s, c in zip(sisters, cats) if s == 'ot']
            if len(ok_c) >= 10 and len(ot_c) >= 10:
                r = contingency_test(ok_c, ot_c, CATEGORIES)
                perm_Vs.append(r['V'])
        if len(perm_Vs) >= 2:
            perm_ranges_okot.append(max(perm_Vs) - min(perm_Vs))

    okot_interaction_p = float(np.mean([1 for r in perm_ranges_okot if r >= okot_v_range])) if perm_ranges_okot else 1.0

    # Any interaction?
    any_interaction = chsh_interaction_p < BONFERRONI_P or okot_interaction_p < BONFERRONI_P

    return {
        'test': 'T6_three_way_interaction',
        'ch_sh': {
            'V_by_zone': chsh_v_by_zone,
            'V_range': float(chsh_v_range),
            'perm_p': chsh_interaction_p,
        },
        'ok_ot': {
            'V_by_zone': okot_v_by_zone,
            'V_range': float(okot_v_range),
            'perm_p': okot_interaction_p,
        },
        'any_interaction': any_interaction,
        'verdict': 'PASS' if any_interaction else 'FAIL',
    }


# ============================================================
# Main
# ============================================================

def main():
    print("Loading data...")
    records = load_data()
    print(f"  {len(records)} tokens loaded")

    # Counts
    for pfx in ['ch', 'sh', 'ok', 'ot']:
        n = sum(1 for r in records if r['prefix'] == pfx)
        print(f"  {pfx}: {n}")

    results = {
        'phase_name': 'SISTER_CATEGORY_MECHANISM',
        'phase_number': 459,
        'n_tokens': len(records),
        'bonferroni_p': BONFERRONI_P,
    }

    print("\nT1: Raw category divergence baseline...")
    t1 = t1_raw_divergence(records)
    print(f"  ch/sh V={t1['ch_sh']['V']:.3f}, p={t1['ch_sh']['p']:.2e}")
    print(f"  ok/ot V={t1['ok_ot']['V']:.3f}, p={t1['ok_ot']['p']:.2e}")

    print("\nT2: Position-controlled ch/sh divergence...")
    t2 = t2_position_controlled_chsh(records)
    print(f"  Raw V={t2['raw_V']:.3f}, Mean within-zone V={t2['mean_within_V']:.3f}")
    print(f"  V retention={t2['V_retention']:.1%}, Fisher p={t2['fisher_p']:.2e}")
    print(f"  Interpretation: {t2['interpretation']}")

    print("\nT3: MIDDLE category shift by sister...")
    t3 = t3_middle_category_shift(records)
    print(f"  {t3['n_qualifying']} qualifying MIDDLEs, {t3['n_shifted']}/{t3['n_tested']} shifted ({t3['shift_rate']:.1%})")
    print(f"  {t3['n_dominant_changed']} changed dominant category")
    print(f"  Binom p={t3['binom_p']:.2e}, mean JSD={t3['mean_JSD']:.4f}")
    print(f"  Interpretation: {t3['interpretation']}")

    print("\nT4: Cross-lane category cargo...")
    t4 = t4_cross_lane_cargo(records)
    if 'qo_cargo' in t4:
        print(f"  ch->QO: {t4['n_ch_to_qo']}, sh->QO: {t4['n_sh_to_qo']}")
        print(f"  Cargo V={t4['qo_cargo']['V']:.3f}, p={t4['qo_cargo']['p']:.2e}")
        print(f"  Self-category V={t4['self_category_at_transition']['V']:.3f}")
    else:
        print(f"  SKIP: low N ({t4.get('n_ch_to_qo', 0)}, {t4.get('n_sh_to_qo', 0)})")

    print("\nT5: Position-controlled ok/ot divergence...")
    t5 = t5_position_controlled_okot(records)
    print(f"  Raw V={t5['raw_V']:.3f}, Mean within-zone V={t5['mean_within_V']:.3f}")
    print(f"  V retention={t5['V_retention']:.1%}, Fisher p={t5['fisher_p']:.2e}")
    print(f"  Interpretation: {t5['interpretation']}")

    print("\nT6: Three-way interaction...")
    t6 = t6_three_way_interaction(records)
    print(f"  ch/sh V range={t6['ch_sh']['V_range']:.3f}, perm p={t6['ch_sh']['perm_p']:.3f}")
    print(f"  ok/ot V range={t6['ok_ot']['V_range']:.3f}, perm p={t6['ok_ot']['perm_p']:.3f}")

    tests = [t1, t2, t3, t4, t5, t6]
    results['tests'] = tests

    # Overall verdict
    n_pass = sum(1 for t in tests if t['verdict'] == 'PASS')
    n_fail = sum(1 for t in tests if t['verdict'] == 'FAIL')
    n_skip = sum(1 for t in tests if t['verdict'].startswith('SKIP'))

    # Key question: does position explain away the divergence?
    chsh_retained = t2['interpretation'] == 'CATEGORY_GENUINE'
    okot_retained = t5['interpretation'] == 'CATEGORY_GENUINE'
    middle_shifts = t3['interpretation'] != 'MIDDLE_DETERMINES_CATEGORY'

    if chsh_retained and okot_retained and middle_shifts:
        overall = 'SISTER_IS_MODE_SELECTOR'
    elif chsh_retained or okot_retained:
        overall = 'PARTIAL_MODE_SELECTION'
    elif middle_shifts:
        overall = 'WEAK_MODULATION'
    else:
        overall = 'SISTER_IS_POSITIONAL_ROUTER'

    results['summary'] = {
        'n_pass': n_pass,
        'n_fail': n_fail,
        'n_skip': n_skip,
        'chsh_position_controlled': t2['interpretation'],
        'okot_position_controlled': t5['interpretation'],
        'middle_shift': t3['interpretation'],
        'overall_verdict': overall,
    }

    print(f"\n{'='*60}")
    print(f"OVERALL: {overall} ({n_pass} PASS, {n_fail} FAIL, {n_skip} SKIP)")
    print(f"  ch/sh after position control: {t2['interpretation']}")
    print(f"  ok/ot after position control: {t5['interpretation']}")
    print(f"  MIDDLE category shift: {t3['interpretation']}")
    print(f"{'='*60}")

    out_path = ROOT / 'phases' / 'SISTER_CATEGORY_MECHANISM' / 'results' / 'sister_category_mechanism.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
