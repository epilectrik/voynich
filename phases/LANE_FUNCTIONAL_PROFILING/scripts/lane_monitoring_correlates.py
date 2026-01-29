#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANE_FUNCTIONAL_PROFILING - Script 1: Lane Monitoring Correlates

Four tests of monitoring/vigilance correlates for QO vs CHSH execution lanes:
1. LINK rate by lane context (controlling AX sub-position)
2. HT at switch vs continuation points
3. HT by lane balance (folio-level, partial correlation)
4. EN-exclusive MIDDLEs by lane (bonus)

Data dependencies:
  - class_token_map.json (CLASS_COSURVIVAL_TEST)
  - en_census.json (EN_ANATOMY)
  - regime_folio_mapping.json (REGIME_SEMANTIC_INTERPRETATION)
"""

import json
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
from math import log2, sqrt

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================
# SECTION 1: Load & Prepare
# ============================================================
print("=" * 60)
print("SECTION 1: Load & Prepare")
print("=" * 60)

# Load class token map
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)

token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
class_to_role[17] = 'CORE_CONTROL'  # C560/C581 correction
token_to_role = {}
for t, c in token_to_class.items():
    token_to_role[t] = class_to_role.get(c, 'UNKNOWN')

# Load EN census
with open(PROJECT_ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_census = json.load(f)
qo_classes = set(en_census['prefix_families']['QO'])
chsh_classes = set(en_census['prefix_families']['CH_SH'])
all_en_classes = qo_classes | chsh_classes
en_exclusive_middles = set(en_census['middle_inventory']['en_exclusive_middles'])

# Load REGIME mapping
with open(PROJECT_ROOT / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json') as f:
    regime_data = json.load(f)
folio_to_regime = {}
for regime, folios in regime_data.items():
    for f in folios:
        folio_to_regime[f] = regime

# Role constants
CC_CLASSES = {10, 11, 12, 17}
HAZ_CLASSES = {7, 30}

# AX sub-position definitions (C563, SUB_ROLE_INTERACTION)
AX_INIT = {4, 5, 6, 24, 26}
AX_MED = {1, 2, 3, 16, 18, 27, 28, 29}
AX_FINAL = {15, 19, 20, 21, 22, 25}
AX_ALL = AX_INIT | AX_MED | AX_FINAL

# Load transcript and morphology
tx = Transcript()
morph = Morphology()

# Build line-organized B token data
print("Building line-organized B token data...")
lines = defaultdict(list)

for token in tx.currier_b():
    cls = token_to_class.get(token.word)
    role = token_to_role.get(token.word, 'UNKNOWN')
    m = morph.extract(token.word)

    en_subfamily = None
    if cls is not None and cls in all_en_classes:
        if m.prefix == 'qo':
            en_subfamily = 'QO'
        elif m.prefix in ('ch', 'sh'):
            en_subfamily = 'CHSH'

    is_en = cls in all_en_classes if cls is not None else False
    is_cc = cls in CC_CLASSES if cls is not None else False
    is_haz = cls in HAZ_CLASSES if cls is not None else False
    is_link = 'ol' in token.word if token.word else False  # C609/C617 canonical
    is_ht = token.word not in token_to_class if token.word else False  # outside grammar

    ax_subpos = None
    if cls is not None:
        if cls in AX_INIT:
            ax_subpos = 'INIT'
        elif cls in AX_MED:
            ax_subpos = 'MED'
        elif cls in AX_FINAL:
            ax_subpos = 'FINAL'

    lines[(token.folio, token.line)].append({
        'word': token.word,
        'class': cls,
        'role': role,
        'prefix': m.prefix,
        'middle': m.middle,
        'en_subfamily': en_subfamily,
        'is_en': is_en,
        'is_cc': is_cc,
        'is_haz': is_haz,
        'is_link': is_link,
        'is_ht': is_ht,
        'ax_subpos': ax_subpos,
        'section': token.section,
        'folio': token.folio,
    })

print(f"B lines: {len(lines)}")

# Build EN sequences per line (MIN_EN = 4)
MIN_EN = 4
en_line_data = []

for (folio, line_num), toks in lines.items():
    en_positions = []
    for i, t in enumerate(toks):
        if t['en_subfamily'] is not None:
            en_positions.append({
                'pos': i,
                'subfamily': t['en_subfamily'],
                'middle': t['middle'],
                'class': t['class'],
            })

    if len(en_positions) >= MIN_EN:
        en_line_data.append({
            'folio': folio,
            'line': line_num,
            'section': toks[0]['section'],
            'all_tokens': toks,
            'en_positions': en_positions,
            'en_seq': [e['subfamily'] for e in en_positions],
        })

print(f"Lines with >= {MIN_EN} EN tokens: {len(en_line_data)}")
total_en_pairs = sum(len(d['en_seq']) - 1 for d in en_line_data)
print(f"Total EN-to-EN transitions: {total_en_pairs}")


def cramers_v(table):
    """Cramer's V from a contingency table."""
    chi2_val = stats.chi2_contingency(table, correction=False)[0]
    n = np.array(table).sum()
    r, c = np.array(table).shape
    return sqrt(chi2_val / (n * (min(r, c) - 1))) if n > 0 else 0.0


def safe_chi2(table):
    """Chi-squared with Fisher's exact fallback for small expected cells."""
    table = np.array(table)
    if table.min() == 0 and (table.sum(axis=0).min() == 0 or table.sum(axis=1).min() == 0):
        return {'chi2': None, 'p': None, 'method': 'degenerate', 'note': 'zero marginal'}
    expected = stats.chi2_contingency(table, correction=True)[3]
    if expected.min() < 5:
        # Fisher's exact (2x2 only)
        if table.shape == (2, 2):
            odds, p = stats.fisher_exact(table)
            return {'chi2': None, 'p': float(p), 'method': 'fisher_exact', 'odds_ratio': float(odds)}
        else:
            chi2_val, p, dof, _ = stats.chi2_contingency(table, correction=True)
            return {'chi2': float(chi2_val), 'p': float(p), 'method': 'chi2_small_expected',
                    'dof': int(dof), 'min_expected': float(expected.min())}
    chi2_val, p, dof, _ = stats.chi2_contingency(table, correction=True)
    return {'chi2': float(chi2_val), 'p': float(p), 'method': 'chi2', 'dof': int(dof)}


# ============================================================
# SECTION 2: Test 1 -- LINK Rate by QO vs CHSH
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: Test 1 -- LINK Rate by Lane Context")
print("=" * 60)

# For each EN token, find nearest AX in same line
link_by_lane = {'QO': {'link': 0, 'non_link': 0},
                'CHSH': {'link': 0, 'non_link': 0}}
link_by_lane_subpos = {sp: {'QO': {'link': 0, 'non_link': 0},
                             'CHSH': {'link': 0, 'non_link': 0}}
                       for sp in ['INIT', 'MED', 'FINAL']}
# Also track excluding AX_FINAL
link_by_lane_excl_final = {'QO': {'link': 0, 'non_link': 0},
                           'CHSH': {'link': 0, 'non_link': 0}}

for (folio, line_num), toks in lines.items():
    # Find all AX positions
    ax_positions = [(i, t) for i, t in enumerate(toks) if t['ax_subpos'] is not None]
    if not ax_positions:
        continue

    for i, t in enumerate(toks):
        if t['en_subfamily'] is None:
            continue
        # Find nearest AX
        nearest_ax = min(ax_positions, key=lambda x: abs(x[0] - i))
        ax_tok = nearest_ax[1]
        lane = t['en_subfamily']
        is_link_ax = ax_tok['is_link']
        subpos = ax_tok['ax_subpos']

        key = 'link' if is_link_ax else 'non_link'
        link_by_lane[lane][key] += 1
        link_by_lane_subpos[subpos][lane][key] += 1
        if subpos != 'FINAL':
            link_by_lane_excl_final[lane][key] += 1

# Overall test
qo_link = link_by_lane['QO']['link']
qo_nonlink = link_by_lane['QO']['non_link']
chsh_link = link_by_lane['CHSH']['link']
chsh_nonlink = link_by_lane['CHSH']['non_link']
qo_total = qo_link + qo_nonlink
chsh_total = chsh_link + chsh_nonlink

print(f"\nOverall:")
print(f"  QO:   {qo_link}/{qo_total} LINK ({100*qo_link/qo_total:.1f}%)" if qo_total > 0 else "  QO: no data")
print(f"  CHSH: {chsh_link}/{chsh_total} LINK ({100*chsh_link/chsh_total:.1f}%)" if chsh_total > 0 else "  CHSH: no data")

overall_table = [[qo_link, qo_nonlink], [chsh_link, chsh_nonlink]]
overall_test = safe_chi2(overall_table)
overall_v = cramers_v(overall_table) if overall_test.get('chi2') is not None else None
print(f"  Test: {overall_test}")
if overall_v is not None:
    print(f"  Cramer's V: {overall_v:.4f}")

test1_result = {
    'overall': {
        'table': overall_table,
        'qo_link_rate': qo_link / qo_total if qo_total > 0 else None,
        'chsh_link_rate': chsh_link / chsh_total if chsh_total > 0 else None,
        'n_qo': qo_total,
        'n_chsh': chsh_total,
        'cramers_v': overall_v,
        **overall_test,
    },
    'by_subposition': {},
    'excluding_final': {},
}

# Per sub-position
for sp in ['INIT', 'MED', 'FINAL']:
    d = link_by_lane_subpos[sp]
    ql = d['QO']['link']
    qn = d['QO']['non_link']
    cl = d['CHSH']['link']
    cn = d['CHSH']['non_link']
    qt = ql + qn
    ct = cl + cn
    total = qt + ct

    print(f"\n  {sp}: QO {ql}/{qt}, CHSH {cl}/{ct} (total {total})")

    if total < 20:
        test1_result['by_subposition'][sp] = {'insufficient_data': True, 'n': total}
        print(f"    Skipped (n < 20)")
        continue

    table = [[ql, qn], [cl, cn]]
    test_res = safe_chi2(table)
    v = cramers_v(table) if test_res.get('chi2') is not None else None

    qo_rate = ql / qt if qt > 0 else None
    chsh_rate = cl / ct if ct > 0 else None
    print(f"    QO LINK rate: {qo_rate:.3f}" if qo_rate else "    QO: no data")
    print(f"    CHSH LINK rate: {chsh_rate:.3f}" if chsh_rate else "    CHSH: no data")
    print(f"    Test: {test_res}")

    test1_result['by_subposition'][sp] = {
        'table': table,
        'qo_link_rate': qo_rate,
        'chsh_link_rate': chsh_rate,
        'n_qo': qt, 'n_chsh': ct,
        'cramers_v': v,
        **test_res,
    }

# Excluding AX_FINAL
d = link_by_lane_excl_final
ql = d['QO']['link']
qn = d['QO']['non_link']
cl = d['CHSH']['link']
cn = d['CHSH']['non_link']
qt = ql + qn
ct = cl + cn

print(f"\nExcluding AX_FINAL:")
print(f"  QO:   {ql}/{qt} LINK ({100*ql/qt:.1f}%)" if qt > 0 else "  QO: no data")
print(f"  CHSH: {cl}/{ct} LINK ({100*cl/ct:.1f}%)" if ct > 0 else "  CHSH: no data")

excl_table = [[ql, qn], [cl, cn]]
excl_test = safe_chi2(excl_table)
excl_v = cramers_v(excl_table) if excl_test.get('chi2') is not None else None

test1_result['excluding_final'] = {
    'table': excl_table,
    'qo_link_rate': ql / qt if qt > 0 else None,
    'chsh_link_rate': cl / ct if ct > 0 else None,
    'n_qo': qt, 'n_chsh': ct,
    'cramers_v': excl_v,
    **excl_test,
}

# Interpretation
overall_p = overall_test.get('p')
excl_p = excl_test.get('p')
if overall_p is not None and overall_p < 0.05:
    if excl_p is not None and excl_p < 0.05:
        test1_result['interpretation'] = 'LINK_LANE_ASSOCIATION'
    else:
        test1_result['interpretation'] = 'CONFOUNDED_BY_SUBPOSITION'
else:
    test1_result['interpretation'] = 'LINK_LANE_INDEPENDENT'

print(f"\nInterpretation: {test1_result['interpretation']}")

# ============================================================
# SECTION 3: Test 2 -- HT at Switch vs Continuation Points
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: Test 2 -- HT at Switch vs Continuation Points")
print("=" * 60)

# For each consecutive EN pair, check for HT in gap
switch_counts = {'has_ht': 0, 'no_ht': 0}
continue_counts = {'has_ht': 0, 'no_ht': 0}
# Non-zero gaps only
switch_nz = {'has_ht': 0, 'no_ht': 0}
continue_nz = {'has_ht': 0, 'no_ht': 0}
# By line position
switch_by_pos = {p: {'has_ht': 0, 'no_ht': 0} for p in ['early', 'mid', 'late']}
continue_by_pos = {p: {'has_ht': 0, 'no_ht': 0} for p in ['early', 'mid', 'late']}
# Window-based (2-token window around switch point)
switch_window = {'has_ht': 0, 'no_ht': 0}
continue_window = {'has_ht': 0, 'no_ht': 0}

n_zero_gaps = 0
n_total_gaps = 0

for d in en_line_data:
    toks = d['all_tokens']
    en_pos = d['en_positions']
    n_toks = len(toks)

    for idx in range(1, len(en_pos)):
        prev_en = en_pos[idx - 1]
        curr_en = en_pos[idx]
        is_switch = prev_en['subfamily'] != curr_en['subfamily']

        gap_start = prev_en['pos'] + 1
        gap_end = curr_en['pos']
        gap_len = gap_end - gap_start
        gap_tokens = toks[gap_start:gap_end]
        has_ht_gap = any(t['is_ht'] for t in gap_tokens)

        n_total_gaps += 1
        if gap_len == 0:
            n_zero_gaps += 1

        # Relative position of second EN
        rel_pos = curr_en['pos'] / n_toks if n_toks > 0 else 0.5
        pos_bin = 'early' if rel_pos < 0.33 else ('mid' if rel_pos < 0.67 else 'late')

        # Gap-based
        target = switch_counts if is_switch else continue_counts
        target_pos = switch_by_pos[pos_bin] if is_switch else continue_by_pos[pos_bin]
        key = 'has_ht' if has_ht_gap else 'no_ht'
        target[key] += 1
        target_pos[key] += 1

        # Non-zero gaps only
        if gap_len > 0:
            target_nz = switch_nz if is_switch else continue_nz
            target_nz[key] += 1

        # Window-based: 1 token before curr_en + gap
        window_start = max(0, curr_en['pos'] - 1)
        window_end = curr_en['pos']
        # Include gap tokens + 1 token before switch point
        window_tokens = toks[min(gap_start, window_start):window_end]
        has_ht_window = any(t['is_ht'] for t in window_tokens)
        target_w = switch_window if is_switch else continue_window
        target_w['has_ht' if has_ht_window else 'no_ht'] += 1

# Print results
sw_total = switch_counts['has_ht'] + switch_counts['no_ht']
co_total = continue_counts['has_ht'] + continue_counts['no_ht']
print(f"\nGap statistics:")
print(f"  Total gaps: {n_total_gaps}")
print(f"  Zero-length gaps: {n_zero_gaps} ({100*n_zero_gaps/n_total_gaps:.1f}%)")
print(f"  Non-zero gaps: {n_total_gaps - n_zero_gaps}")

sw_ht_rate = switch_counts['has_ht'] / sw_total if sw_total > 0 else 0
co_ht_rate = continue_counts['has_ht'] / co_total if co_total > 0 else 0
print(f"\nAll gaps:")
print(f"  Switch:       {switch_counts['has_ht']}/{sw_total} HT ({100*sw_ht_rate:.1f}%)")
print(f"  Continuation: {continue_counts['has_ht']}/{co_total} HT ({100*co_ht_rate:.1f}%)")

# Overall test
table2 = [[switch_counts['has_ht'], switch_counts['no_ht']],
           [continue_counts['has_ht'], continue_counts['no_ht']]]
test2_overall = safe_chi2(table2)
v2 = cramers_v(table2) if test2_overall.get('chi2') is not None else None
print(f"  Test: {test2_overall}")

# Non-zero gaps
sw_nz_total = switch_nz['has_ht'] + switch_nz['no_ht']
co_nz_total = continue_nz['has_ht'] + continue_nz['no_ht']
sw_nz_rate = switch_nz['has_ht'] / sw_nz_total if sw_nz_total > 0 else 0
co_nz_rate = continue_nz['has_ht'] / co_nz_total if co_nz_total > 0 else 0
print(f"\nNon-zero gaps only:")
print(f"  Switch:       {switch_nz['has_ht']}/{sw_nz_total} HT ({100*sw_nz_rate:.1f}%)")
print(f"  Continuation: {continue_nz['has_ht']}/{co_nz_total} HT ({100*co_nz_rate:.1f}%)")

nz_table = [[switch_nz['has_ht'], switch_nz['no_ht']],
             [continue_nz['has_ht'], continue_nz['no_ht']]]
nz_test = safe_chi2(nz_table)
nz_v = cramers_v(nz_table) if nz_test.get('chi2') is not None else None

# Window-based
sw_w_total = switch_window['has_ht'] + switch_window['no_ht']
co_w_total = continue_window['has_ht'] + continue_window['no_ht']
sw_w_rate = switch_window['has_ht'] / sw_w_total if sw_w_total > 0 else 0
co_w_rate = continue_window['has_ht'] / co_w_total if co_w_total > 0 else 0
print(f"\nWindow-based (1 token before switch point):")
print(f"  Switch:       {switch_window['has_ht']}/{sw_w_total} HT ({100*sw_w_rate:.1f}%)")
print(f"  Continuation: {continue_window['has_ht']}/{co_w_total} HT ({100*co_w_rate:.1f}%)")

w_table = [[switch_window['has_ht'], switch_window['no_ht']],
            [continue_window['has_ht'], continue_window['no_ht']]]
w_test = safe_chi2(w_table)

test2_result = {
    'overall': {
        'table': table2,
        'switch_ht_rate': sw_ht_rate,
        'continuation_ht_rate': co_ht_rate,
        'rate_ratio': sw_ht_rate / co_ht_rate if co_ht_rate > 0 else None,
        'n_switches': sw_total,
        'n_continuations': co_total,
        'cramers_v': v2,
        **test2_overall,
    },
    'gap_statistics': {
        'total_gaps': n_total_gaps,
        'zero_length_gaps': n_zero_gaps,
        'zero_length_pct': 100 * n_zero_gaps / n_total_gaps if n_total_gaps > 0 else 0,
    },
    'nonzero_gaps_only': {
        'table': nz_table,
        'switch_ht_rate': sw_nz_rate,
        'continuation_ht_rate': co_nz_rate,
        'rate_ratio': sw_nz_rate / co_nz_rate if co_nz_rate > 0 else None,
        'n_switches': sw_nz_total,
        'n_continuations': co_nz_total,
        'cramers_v': nz_v,
        **nz_test,
    },
    'window_based': {
        'table': w_table,
        'switch_ht_rate': sw_w_rate,
        'continuation_ht_rate': co_w_rate,
        'n_switches': sw_w_total,
        'n_continuations': co_w_total,
        **w_test,
    },
    'by_position': {},
}

# By line position
for pos in ['early', 'mid', 'late']:
    sw_d = switch_by_pos[pos]
    co_d = continue_by_pos[pos]
    sw_t = sw_d['has_ht'] + sw_d['no_ht']
    co_t = co_d['has_ht'] + co_d['no_ht']
    total_pos = sw_t + co_t

    print(f"\n  Position {pos}: switch={sw_t}, continue={co_t}")

    if total_pos < 20:
        test2_result['by_position'][pos] = {'insufficient_data': True, 'n': total_pos}
        continue

    pos_table = [[sw_d['has_ht'], sw_d['no_ht']], [co_d['has_ht'], co_d['no_ht']]]
    pos_test = safe_chi2(pos_table)
    pos_v = cramers_v(pos_table) if pos_test.get('chi2') is not None else None
    sw_rate = sw_d['has_ht'] / sw_t if sw_t > 0 else 0
    co_rate = co_d['has_ht'] / co_t if co_t > 0 else 0
    print(f"    Switch HT: {100*sw_rate:.1f}%, Continue HT: {100*co_rate:.1f}%")

    test2_result['by_position'][pos] = {
        'table': pos_table,
        'switch_ht_rate': sw_rate,
        'continuation_ht_rate': co_rate,
        'cramers_v': pos_v,
        **pos_test,
    }

# Low power warning
ht_rate_overall = (switch_counts['has_ht'] + continue_counts['has_ht']) / n_total_gaps if n_total_gaps > 0 else 0
test2_result['ht_rate_in_gaps'] = ht_rate_overall
if ht_rate_overall < 0.05:
    test2_result['low_power_warning'] = True
    print(f"\n  WARNING: HT rate in gaps is {100*ht_rate_overall:.1f}% (< 5%) -- low power")

# Interpretation
p_overall = test2_overall.get('p')
if p_overall is not None and p_overall < 0.05:
    if sw_ht_rate > co_ht_rate:
        test2_result['interpretation'] = 'HT_ELEVATED_AT_SWITCHES'
    else:
        test2_result['interpretation'] = 'HT_ELEVATED_AT_CONTINUATIONS'
else:
    test2_result['interpretation'] = 'HT_NOT_ELEVATED'

print(f"\nInterpretation: {test2_result['interpretation']}")


# ============================================================
# SECTION 4: Test 3 -- HT by Lane Balance (Folio-Level)
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: Test 3 -- HT by Lane Balance (Folio-Level)")
print("=" * 60)

# Compute per-folio statistics
folio_stats = defaultdict(lambda: {
    'n_qo': 0, 'n_chsh': 0, 'n_ht': 0, 'n_total': 0,
    'sections': Counter(), 'middles': Counter()
})

for (folio, line_num), toks in lines.items():
    fs = folio_stats[folio]
    for t in toks:
        fs['n_total'] += 1
        if t['en_subfamily'] == 'QO':
            fs['n_qo'] += 1
        elif t['en_subfamily'] == 'CHSH':
            fs['n_chsh'] += 1
        if t['is_ht']:
            fs['n_ht'] += 1
        if t['middle']:
            fs['middles'][t['middle']] += 1
        fs['sections'][t['section']] += 1

# Compute B-side tail_pressure (bottom 50% of MIDDLE frequency)
all_b_middles = Counter()
for fs in folio_stats.values():
    all_b_middles += fs['middles']
sorted_middles = sorted(all_b_middles.items(), key=lambda x: x[1])
cutoff = len(sorted_middles) // 2
tail_middles = set(m for m, c in sorted_middles[:cutoff])

# Build folio records
folio_records = []
for folio, fs in folio_stats.items():
    n_en = fs['n_qo'] + fs['n_chsh']
    if n_en < 10:  # Guard: min EN for stable balance
        continue
    lane_balance = fs['n_qo'] / n_en
    ht_density = fs['n_ht'] / fs['n_total'] if fs['n_total'] > 0 else 0
    section = fs['sections'].most_common(1)[0][0] if fs['sections'] else 'UNKNOWN'
    regime = folio_to_regime.get(folio, 'UNKNOWN')
    tail_p = (sum(fs['middles'][m] for m in tail_middles if m in fs['middles'])
              / sum(fs['middles'].values())) if fs['middles'] else 0

    folio_records.append({
        'folio': folio,
        'lane_balance': lane_balance,
        'ht_density': ht_density,
        'section': section,
        'regime': regime,
        'tail_pressure': tail_p,
        'n_en': n_en,
    })

print(f"Folios with >= 10 EN tokens: {len(folio_records)}")

# Bivariate correlation
balances = np.array([r['lane_balance'] for r in folio_records])
ht_densities = np.array([r['ht_density'] for r in folio_records])

rho, p_biv = stats.spearmanr(balances, ht_densities)
print(f"\nBivariate Spearman: rho={rho:.4f}, p={p_biv:.4f}, n={len(folio_records)}")


def partial_correlation(x, y, covariates):
    """Pearson partial correlation controlling for covariates."""
    if len(covariates) == 0:
        return stats.pearsonr(x, y)
    X_cov = np.column_stack(covariates)
    X_cov = np.column_stack([np.ones(len(x)), X_cov])
    beta_x = np.linalg.lstsq(X_cov, x, rcond=None)[0]
    resid_x = x - X_cov @ beta_x
    beta_y = np.linalg.lstsq(X_cov, y, rcond=None)[0]
    resid_y = y - X_cov @ beta_y
    r, p = stats.pearsonr(resid_x, resid_y)
    return r, p


# Build covariates for partial correlation
sections_unique = sorted(set(r['section'] for r in folio_records))
regimes_unique = sorted(set(r['regime'] for r in folio_records if r['regime'] != 'UNKNOWN'))

covariates = []
# Section dummies (k-1)
for s in sections_unique[1:]:
    covariates.append(np.array([1 if r['section'] == s else 0 for r in folio_records], dtype=float))
# Regime dummies (k-1), excluding UNKNOWN
for reg in regimes_unique[1:]:
    covariates.append(np.array([1 if r['regime'] == reg else 0 for r in folio_records], dtype=float))
# Tail pressure
covariates.append(np.array([r['tail_pressure'] for r in folio_records]))

partial_r, partial_p = partial_correlation(balances, ht_densities, covariates)
print(f"Partial correlation: r={partial_r:.4f}, p={partial_p:.4f}")
print(f"  Controlling: section ({len(sections_unique)} levels), regime ({len(regimes_unique)} levels), tail_pressure")

# By-section bivariate
section_results = {}
for sec in sections_unique:
    sec_records = [r for r in folio_records if r['section'] == sec]
    if len(sec_records) < 10:
        section_results[sec] = {'insufficient_data': True, 'n': len(sec_records)}
        continue
    sec_bal = np.array([r['lane_balance'] for r in sec_records])
    sec_ht = np.array([r['ht_density'] for r in sec_records])
    r_sec, p_sec = stats.spearmanr(sec_bal, sec_ht)
    section_results[sec] = {'rho': float(r_sec), 'p': float(p_sec), 'n': len(sec_records)}
    print(f"  Section {sec}: rho={r_sec:.4f}, p={p_sec:.4f}, n={len(sec_records)}")

test3_result = {
    'n_folios': len(folio_records),
    'bivariate': {
        'spearman_rho': float(rho),
        'p': float(p_biv),
    },
    'partial': {
        'controlling': ['section', 'regime', 'tail_pressure'],
        'partial_r': float(partial_r),
        'p': float(partial_p),
    },
    'by_section': section_results,
    'folio_data': [
        {'folio': r['folio'], 'lane_balance': round(r['lane_balance'], 4),
         'ht_density': round(r['ht_density'], 4), 'section': r['section'],
         'regime': r['regime']}
        for r in folio_records
    ],
}

# Interpretation
if p_biv < 0.05:
    if partial_p < 0.05:
        test3_result['interpretation'] = 'LANE_BALANCE_PREDICTS_HT'
    else:
        test3_result['interpretation'] = 'CONFOUND_DRIVEN'
else:
    test3_result['interpretation'] = 'NO_ASSOCIATION'

print(f"\nInterpretation: {test3_result['interpretation']}")


# ============================================================
# SECTION 5: Bonus -- EN-Exclusive MIDDLEs by Lane
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: Bonus -- EN-Exclusive MIDDLEs by Lane")
print("=" * 60)

# Count QO vs CHSH for each exclusive MIDDLE
middle_lane_counts = {m: {'QO': 0, 'CHSH': 0} for m in en_exclusive_middles}

for (folio, line_num), toks in lines.items():
    for t in toks:
        if t['en_subfamily'] is not None and t['middle'] in en_exclusive_middles:
            middle_lane_counts[t['middle']][t['en_subfamily']] += 1

# Compute base QO rate from all EN tokens
total_qo = sum(1 for (f, l), toks in lines.items() for t in toks if t['en_subfamily'] == 'QO')
total_chsh = sum(1 for (f, l), toks in lines.items() for t in toks if t['en_subfamily'] == 'CHSH')
total_en_all = total_qo + total_chsh
base_qo_rate = total_qo / total_en_all if total_en_all > 0 else 0.5
print(f"Base QO rate: {base_qo_rate:.4f} ({total_qo}/{total_en_all})")

# Per-MIDDLE binomial tests
per_middle = []
p_values = []
testable_middles = []

for m in sorted(en_exclusive_middles):
    qo_n = middle_lane_counts[m]['QO']
    chsh_n = middle_lane_counts[m]['CHSH']
    total = qo_n + chsh_n

    entry = {
        'middle': m,
        'qo': qo_n,
        'chsh': chsh_n,
        'total': total,
        'qo_rate': qo_n / total if total > 0 else None,
    }

    if total >= 10:
        p_val = stats.binomtest(qo_n, total, base_qo_rate).pvalue
        entry['binom_p'] = float(p_val)
        p_values.append(p_val)
        testable_middles.append(m)
    else:
        entry['binom_p'] = None
        entry['note'] = 'insufficient (n < 10)'

    per_middle.append(entry)

# FDR correction (Benjamini-Hochberg)
if p_values:
    n_tests = len(p_values)
    sorted_pvals = sorted(enumerate(p_values), key=lambda x: x[1])
    fdr_significant = [False] * n_tests
    for rank, (orig_idx, pval) in enumerate(sorted_pvals, 1):
        threshold = 0.05 * rank / n_tests
        if pval <= threshold:
            fdr_significant[orig_idx] = True
        else:
            break  # All subsequent are also NS

    # Apply FDR results back
    testable_idx = 0
    for entry in per_middle:
        if entry['binom_p'] is not None:
            entry['fdr_significant'] = fdr_significant[testable_idx]
            testable_idx += 1

# Aggregate test
agg_qo = sum(middle_lane_counts[m]['QO'] for m in en_exclusive_middles)
agg_chsh = sum(middle_lane_counts[m]['CHSH'] for m in en_exclusive_middles)
agg_total = agg_qo + agg_chsh
agg_p = stats.binomtest(agg_qo, agg_total, base_qo_rate).pvalue if agg_total > 0 else None

n_qo_enriched = sum(1 for e in per_middle if e.get('fdr_significant') and e['qo_rate'] is not None and e['qo_rate'] > base_qo_rate)
n_chsh_enriched = sum(1 for e in per_middle if e.get('fdr_significant') and e['qo_rate'] is not None and e['qo_rate'] < base_qo_rate)

print(f"\nAggregate: {agg_qo} QO, {agg_chsh} CHSH (rate={agg_qo/agg_total:.4f} vs base {base_qo_rate:.4f})")
print(f"  Binomial p={agg_p:.6f}" if agg_p else "  No data")
print(f"\nFDR-significant MIDDLEs: {n_qo_enriched} QO-enriched, {n_chsh_enriched} CHSH-enriched")

for e in per_middle:
    if e.get('fdr_significant'):
        direction = 'QO' if e['qo_rate'] > base_qo_rate else 'CHSH'
        print(f"  {e['middle']}: {e['qo']}/{e['total']} QO ({e['qo_rate']:.3f}), p={e['binom_p']:.6f} -> {direction}")

bonus_result = {
    'base_qo_rate': base_qo_rate,
    'n_exclusive_middles': len(en_exclusive_middles),
    'n_testable': len(testable_middles),
    'aggregate': {
        'total_qo': agg_qo,
        'total_chsh': agg_chsh,
        'observed_qo_rate': agg_qo / agg_total if agg_total > 0 else None,
        'binom_p': float(agg_p) if agg_p is not None else None,
    },
    'per_middle': per_middle,
    'n_qo_enriched': n_qo_enriched,
    'n_chsh_enriched': n_chsh_enriched,
}

if n_qo_enriched + n_chsh_enriched > 0:
    if n_qo_enriched > n_chsh_enriched * 2 or n_chsh_enriched > n_qo_enriched * 2:
        bonus_result['interpretation'] = 'LANE_CONCENTRATED'
    else:
        bonus_result['interpretation'] = 'LANE_DISTRIBUTED'
else:
    bonus_result['interpretation'] = 'EVENLY_DISTRIBUTED'

print(f"\nInterpretation: {bonus_result['interpretation']}")


# ============================================================
# SECTION 6: Summary
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: Summary")
print("=" * 60)

results = {
    'test1_link_by_lane': test1_result,
    'test2_ht_at_switches': test2_result,
    'test3_ht_lane_balance': test3_result,
    'bonus_exclusive_middles': bonus_result,
    'summary': {
        'test1': test1_result['interpretation'],
        'test2': test2_result['interpretation'],
        'test3': test3_result['interpretation'],
        'bonus': bonus_result['interpretation'],
    }
}

print(f"\nTest 1 (LINK by lane):      {test1_result['interpretation']}")
print(f"Test 2 (HT at switches):    {test2_result['interpretation']}")
print(f"Test 3 (HT lane balance):   {test3_result['interpretation']}")
print(f"Bonus (exclusive MIDDLEs):  {bonus_result['interpretation']}")

# Save results
output_path = RESULTS_DIR / 'lane_monitoring_correlates.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to {output_path}")
