#!/usr/bin/env python3
"""
Phase 350: HAZARD_VIOLATION_ARCHAEOLOGY
=========================================
The 17 forbidden MIDDLE-pair transitions expand to ~84 CLASS-level forbidden
pairs. At class level, compliance is ~65% (C789) — meaning ~35% of eligible
transitions are violations. This phase asks: are violations SYSTEMATIC or RANDOM?

Tests at CLASS level (the operative grammar layer per C121, C1025, C1026):

  (1) FOLIO CLUSTERING:      Do violations concentrate in specific folios?
  (2) LINE POSITION:         Do violations cluster at specific line positions?
  (3) PARAGRAPH POSITION:    Do violations differ at paragraph boundaries vs body?
  (4) REGIME SPECIFICITY:    Do REGIMEs differ in violation rate?
  (5) PREFIX CONTEXT:        Do specific source PREFIX contexts license violations?
  (6) SPECIFIC PAIR VARIATION: Do all forbidden pairs violate at the same rate?
  (7) VIOLATION NEIGHBORHOOD: Do violation-heavy lines differ from clean lines?
  (8) SEQUENTIAL CONTEXT:    What follows a violation vs a compliant transition?
  (9) SECTION SPECIFICITY:   Do manuscript sections differ in violation rate?
  (10) PERMUTATION TEST:     Overall randomness assessment.

Also reports MIDDLE-level forbidden pair occurrences for comparison.

Depends on: C109 (17 forbidden transitions), C789 (65% compliance),
            C554 (hazard class clustering), C624 (hazard boundary),
            C667 (hazard density flat within-folio), C1026 (class ordering
            load-bearing)
"""

import json
import sys
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as sp_stats
from scipy.stats import entropy as sp_entropy

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(350)


# ── Constants ────────────────────────────────────────────────────────

MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}
CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state

ROLE_CLASSES = {
    'CC':  {10, 11, 12, 17},
    'EN':  {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49},
    'FL':  {7, 30, 38, 40},
    'FQ':  {9, 13, 14, 23},
    'AX':  {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29},
}
CLASS_TO_ROLE = {}
for role, classes in ROLE_CLASSES.items():
    for c in classes:
        CLASS_TO_ROLE[c] = role


def folio_to_section(folio):
    num = int(''.join(c for c in folio if c.isdigit())[:3])
    if num <= 25:    return 'HERBAL_A'
    elif num <= 56:  return 'HERBAL_B'
    elif num <= 67:  return 'PHARMA'
    elif num <= 73:  return 'ASTRO'
    elif num <= 84:  return 'BIO'
    elif num <= 86:  return 'COSMO'
    elif num <= 102: return 'RECIPE_A'
    else:            return 'RECIPE_B'


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load B corpus with full metadata for archaeology."""
    print("Loading data...")

    # Token -> class map
    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}

    # Forbidden MIDDLE pairs
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
              encoding='utf-8') as f:
        forbidden_inv = json.load(f)
    forbidden_middle_pairs = set()
    for t in forbidden_inv['transitions']:
        forbidden_middle_pairs.add((t['source'], t['target']))

    # Regime mapping
    with open(PROJECT / 'data' / 'regime_folio_mapping.json', encoding='utf-8') as f:
        regime_data = json.load(f)
    folio_to_regime = {}
    for fol, info in regime_data['regime_assignments'].items():
        folio_to_regime[fol] = info['regime']

    morph = Morphology()

    # Build token stream with full metadata
    lines = []
    line_meta = []
    current_line = []
    prev_key = None
    current_folio = None
    current_line_id = None
    para_idx = -1
    line_in_para = -1
    is_para_initial_line = False
    saw_par_initial_this_line = False

    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue
        cls = token_to_class.get(token.word)
        if cls is None:
            continue

        key = (token.folio, token.line)
        if key != prev_key:
            # Save previous line
            if current_line:
                lines.append(current_line)
                line_meta.append({
                    'folio': current_folio,
                    'line': current_line_id,
                    'regime': folio_to_regime.get(current_folio, 'UNKNOWN'),
                    'section': folio_to_section(current_folio),
                    'para_idx': para_idx,
                    'line_in_para': line_in_para,
                    'is_para_initial_line': is_para_initial_line,
                })
                current_line = []

            # New folio? Reset paragraph tracking
            if token.folio != current_folio:
                current_folio = token.folio
                para_idx = -1
                line_in_para = -1

            current_line_id = token.line
            prev_key = key
            is_para_initial_line = False
            saw_par_initial_this_line = False

        # Track paragraph boundaries via par_initial flag
        if token.par_initial and not saw_par_initial_this_line:
            para_idx += 1
            line_in_para = 0
            is_para_initial_line = True
            saw_par_initial_this_line = True
        elif key != prev_key or (not saw_par_initial_this_line and token == current_line[0] if current_line else False):
            pass  # already handled above

        m = morph.extract(token.word)
        current_line.append({
            'word': token.word,
            'cls': cls,
            'state': CLASS_TO_STATE.get(cls, 'UNK'),
            'role': CLASS_TO_ROLE.get(cls, 'UNK'),
            'prefix': m.prefix if m else None,
            'middle': m.middle if m else token.word,
            'suffix': m.suffix if m else None,
            'folio': token.folio,
            'line': token.line,
            'line_initial': token.line_initial,
            'line_final': token.line_final,
            'par_initial': token.par_initial,
        })

    if current_line:
        lines.append(current_line)
        line_meta.append({
            'folio': current_folio,
            'line': current_line_id,
            'regime': folio_to_regime.get(current_folio, 'UNKNOWN'),
            'section': folio_to_section(current_folio),
            'para_idx': para_idx,
            'line_in_para': line_in_para,
            'is_para_initial_line': is_para_initial_line,
        })

    # Increment line_in_para for non-initial lines in the same paragraph
    # (fix: walk through line_meta and fix line_in_para tracking)
    prev_folio = None
    prev_para = -1
    lip_counter = 0
    for lm in line_meta:
        if lm['folio'] != prev_folio:
            prev_folio = lm['folio']
            prev_para = lm['para_idx']
            lip_counter = 0
        elif lm['para_idx'] != prev_para:
            prev_para = lm['para_idx']
            lip_counter = 0
        else:
            lip_counter += 1
        lm['line_in_para'] = lip_counter

    all_tokens = [t for line in lines for t in line]

    # Build class-level forbidden pairs (expand from MIDDLE pairs)
    middle_to_classes = defaultdict(set)
    for t in all_tokens:
        mid = t['middle'] if t['middle'] else ''
        middle_to_classes[mid].add(t['cls'])

    forbidden_class_pairs = set()
    for src_mid, tgt_mid in forbidden_middle_pairs:
        for sc in middle_to_classes.get(src_mid, set()):
            for tc in middle_to_classes.get(tgt_mid, set()):
                forbidden_class_pairs.add((sc, tc))

    # Source classes that participate in forbidden pairs
    forbidden_source_classes = set(s for s, _ in forbidden_class_pairs)
    forbidden_targets_by_source = defaultdict(set)
    for s, t in forbidden_class_pairs:
        forbidden_targets_by_source[s].add(t)

    print(f"  {len(all_tokens)} tokens in {len(lines)} lines")
    print(f"  {len(forbidden_middle_pairs)} forbidden MIDDLE pairs -> {len(forbidden_class_pairs)} forbidden class pairs")
    print(f"  {len(forbidden_source_classes)} source classes participate in forbidden pairs")

    return (lines, line_meta, forbidden_middle_pairs, forbidden_class_pairs,
            forbidden_source_classes, forbidden_targets_by_source, folio_to_regime)


# ── Identify all class-level forbidden-eligible transitions and violations

def find_violations(lines, line_meta, forbidden_class_pairs,
                    forbidden_source_classes, forbidden_targets_by_source,
                    forbidden_middle_pairs):
    """Find every class bigram that matches a forbidden class pair."""
    all_transitions = []
    eligible = []
    violations = []
    middle_violations = []

    # Also track MIDDLE-level for comparison
    forbidden_mid_sources = {s for s, _ in forbidden_middle_pairs}
    forbidden_mid_targets = defaultdict(set)
    for s, t in forbidden_middle_pairs:
        forbidden_mid_targets[s].add(t)

    for line_idx, (line, meta) in enumerate(zip(lines, line_meta)):
        for i in range(len(line) - 1):
            src = line[i]
            tgt = line[i + 1]

            trans = {
                'src_cls': src['cls'],
                'tgt_cls': tgt['cls'],
                'src_mid': src['middle'],
                'tgt_mid': tgt['middle'],
                'src_prefix': src['prefix'],
                'tgt_prefix': tgt['prefix'],
                'src_role': src['role'],
                'tgt_role': tgt['role'],
                'src_state': src['state'],
                'tgt_state': tgt['state'],
                'folio': meta['folio'],
                'regime': meta['regime'],
                'section': meta['section'],
                'line_idx': line_idx,
                'token_idx': i,
                'frac_pos': i / max(1, len(line) - 1),
                'line_len': len(line),
                'para_idx': meta['para_idx'],
                'line_in_para': meta['line_in_para'],
                'is_para_initial_line': meta['is_para_initial_line'],
                'is_violation': False,
                'is_middle_violation': False,
            }
            all_transitions.append(trans)

            # CLASS-level eligibility
            if src['cls'] in forbidden_source_classes:
                eligible.append(trans)
                if tgt['cls'] in forbidden_targets_by_source[src['cls']]:
                    trans['is_violation'] = True
                    violations.append(trans)

            # MIDDLE-level (for comparison)
            if src['middle'] and tgt['middle']:
                if src['middle'] in forbidden_mid_sources:
                    if tgt['middle'] in forbidden_mid_targets[src['middle']]:
                        trans['is_middle_violation'] = True
                        middle_violations.append(trans)

    return all_transitions, eligible, violations, middle_violations


# ── Test 1: Folio Clustering ─────────────────────────────────────────

def test_folio_clustering(eligible, violations):
    """Test if violations cluster in specific folios beyond chance."""
    print("\n=== TEST 1: FOLIO CLUSTERING ===")

    folio_elig = Counter(t['folio'] for t in eligible)
    folio_viol = Counter(t['folio'] for t in violations)

    folios = sorted(folio_elig.keys())
    global_rate = len(violations) / max(1, len(eligible))

    rates = []
    folio_detail = {}
    for f in folios:
        n_e = folio_elig[f]
        n_v = folio_viol.get(f, 0)
        rate = n_v / max(1, n_e)
        rates.append(rate)
        folio_detail[f] = {'eligible': n_e, 'violations': n_v, 'rate': round(rate, 4)}

    rates_arr = np.array(rates)
    dispersion_index = rates_arr.var() / max(rates_arr.mean(), 1e-10)

    # Chi-squared: only folios with expected >= 1
    obs_list = []
    exp_list = []
    for f in folios:
        exp_val = folio_elig[f] * global_rate
        if exp_val >= 1:
            obs_list.append(folio_viol.get(f, 0))
            exp_list.append(exp_val)
    if len(obs_list) > 1:
        # Scale expected to match observed sum
        obs_arr = np.array(obs_list, dtype=float)
        exp_arr = np.array(exp_list, dtype=float)
        exp_arr = exp_arr * (obs_arr.sum() / exp_arr.sum())
        chi2, p_chi2 = sp_stats.chisquare(obs_arr, exp_arr)
        df = len(obs_list) - 1
    else:
        chi2, p_chi2, df = 0.0, 1.0, 0

    sorted_by_rate = sorted(folio_detail.items(), key=lambda x: x[1]['rate'], reverse=True)
    top5 = sorted_by_rate[:5]
    bottom5 = [x for x in sorted_by_rate if x[1]['eligible'] >= 5][-5:]

    print(f"  Global violation rate: {global_rate:.4f} ({len(violations)}/{len(eligible)})")
    print(f"  Dispersion index: {dispersion_index:.4f} (1.0 = Poisson)")
    print(f"  Chi-squared: {chi2:.2f}, p={p_chi2:.6f} (df={df})")
    print(f"  Top 5 violation folios:")
    for f, d in top5:
        print(f"    {f}: {d['rate']:.3f} ({d['violations']}/{d['eligible']})")
    print(f"  Bottom 5 (n>=5):")
    for f, d in bottom5:
        print(f"    {f}: {d['rate']:.3f} ({d['violations']}/{d['eligible']})")

    return {
        'global_rate': round(global_rate, 6),
        'n_violations': len(violations),
        'n_eligible': len(eligible),
        'n_folios': len(folios),
        'dispersion_index': round(dispersion_index, 6),
        'chi2': round(chi2, 4),
        'p_chi2': round(p_chi2, 6),
        'df': df,
        'top5': {f: d for f, d in top5},
        'bottom5': {f: d for f, d in bottom5},
        'rate_min': round(float(rates_arr.min()), 4),
        'rate_max': round(float(rates_arr.max()), 4),
        'rate_std': round(float(rates_arr.std()), 4),
    }


# ── Test 2: Line Position ────────────────────────────────────────────

def test_line_position(eligible, violations):
    """Test if violations cluster at specific positions within lines."""
    print("\n=== TEST 2: LINE POSITION ===")

    viol_pos = np.array([t['frac_pos'] for t in violations])
    nonviol_pos = np.array([t['frac_pos'] for t in eligible if not t['is_violation']])
    elig_pos = np.array([t['frac_pos'] for t in eligible])

    ks_stat, ks_p = sp_stats.ks_2samp(viol_pos, nonviol_pos)
    mean_viol = viol_pos.mean()
    mean_nonviol = nonviol_pos.mean()

    # Quintile analysis
    bins = [0, 0.2, 0.4, 0.6, 0.8, 1.01]
    viol_hist, _ = np.histogram(viol_pos, bins=bins)
    elig_hist, _ = np.histogram(elig_pos, bins=bins)
    rates_by_bin = [v / max(1, e) for v, e in zip(viol_hist, elig_hist)]

    print(f"  Mean position (violations): {mean_viol:.4f}")
    print(f"  Mean position (compliant):  {mean_nonviol:.4f}")
    print(f"  KS test: D={ks_stat:.4f}, p={ks_p:.6f}")
    print(f"  Violation rate by quintile: {['%.3f' % r for r in rates_by_bin]}")

    return {
        'mean_viol_pos': round(float(mean_viol), 6),
        'mean_nonviol_pos': round(float(mean_nonviol), 6),
        'ks_stat': round(float(ks_stat), 6),
        'ks_p': round(float(ks_p), 6),
        'quintile_rates': [round(r, 6) for r in rates_by_bin],
        'quintile_viol_counts': viol_hist.tolist(),
        'quintile_elig_counts': elig_hist.tolist(),
    }


# ── Test 3: Paragraph Position ───────────────────────────────────────

def test_paragraph_position(eligible, violations):
    """Test if violations differ between paragraph-initial lines and body."""
    print("\n=== TEST 3: PARAGRAPH POSITION ===")

    para_init_elig = sum(1 for t in eligible if t['is_para_initial_line'])
    para_init_viol = sum(1 for t in violations if t['is_para_initial_line'])
    body_elig = len(eligible) - para_init_elig
    body_viol = len(violations) - para_init_viol

    rate_init = para_init_viol / max(1, para_init_elig)
    rate_body = body_viol / max(1, body_elig)

    table = np.array([[para_init_viol, para_init_elig - para_init_viol],
                      [body_viol, body_elig - body_viol]])
    if table.min() >= 0 and table.sum() > 0 and para_init_elig > 0 and body_elig > 0:
        chi2, p_val, dof, _ = sp_stats.chi2_contingency(table)
    else:
        chi2, p_val, dof = 0.0, 1.0, 1

    # By line-in-paragraph ordinal (0=first, 1=second, ..., 4+=deep body)
    line_ord_elig = Counter()
    line_ord_viol = Counter()
    for t in eligible:
        lip = min(t['line_in_para'], 5)
        line_ord_elig[lip] += 1
    for t in violations:
        lip = min(t['line_in_para'], 5)
        line_ord_viol[lip] += 1

    ord_rates = {}
    for lip in sorted(line_ord_elig.keys()):
        n_e = line_ord_elig[lip]
        n_v = line_ord_viol.get(lip, 0)
        ord_rates[str(lip)] = {'eligible': n_e, 'violations': n_v, 'rate': round(n_v / max(1, n_e), 4)}

    print(f"  Para-initial violation rate: {rate_init:.4f} ({para_init_viol}/{para_init_elig})")
    print(f"  Body violation rate:         {rate_body:.4f} ({body_viol}/{body_elig})")
    print(f"  Chi-squared: {chi2:.4f}, p={p_val:.6f}")
    print(f"  By line-in-paragraph ordinal:")
    for lip, d in sorted(ord_rates.items()):
        print(f"    Line {lip}: {d['rate']:.3f} ({d['violations']}/{d['eligible']})")

    return {
        'para_initial_rate': round(rate_init, 6),
        'body_rate': round(rate_body, 6),
        'chi2': round(chi2, 4),
        'p_val': round(p_val, 6),
        'para_initial_n': para_init_elig,
        'body_n': body_elig,
        'by_line_ordinal': ord_rates,
    }


# ── Test 4: REGIME Specificity ───────────────────────────────────────

def test_regime_specificity(eligible, violations):
    """Test if REGIMEs differ in violation rate."""
    print("\n=== TEST 4: REGIME SPECIFICITY ===")

    regime_elig = Counter(t['regime'] for t in eligible)
    regime_viol = Counter(t['regime'] for t in violations)
    global_rate = len(violations) / max(1, len(eligible))

    regimes = sorted(r for r in regime_elig.keys() if r != 'UNKNOWN')
    regime_detail = {}
    for r in regimes:
        n_e = regime_elig[r]
        n_v = regime_viol.get(r, 0)
        regime_detail[r] = {'eligible': n_e, 'violations': n_v, 'rate': round(n_v / max(1, n_e), 4)}

    # Chi-squared with proper scaling
    obs = np.array([regime_viol.get(r, 0) for r in regimes], dtype=float)
    exp = np.array([regime_elig[r] * global_rate for r in regimes], dtype=float)
    if exp.sum() > 0:
        exp = exp * (obs.sum() / exp.sum())
    valid_mask = exp >= 1
    if valid_mask.sum() > 1:
        chi2, p_val = sp_stats.chisquare(obs[valid_mask], exp[valid_mask])
    else:
        chi2, p_val = 0.0, 1.0

    print(f"  Per-REGIME violation rates:")
    for r in regimes:
        d = regime_detail[r]
        print(f"    {r}: {d['rate']:.4f} ({d['violations']}/{d['eligible']})")
    print(f"  Chi-squared: {chi2:.4f}, p={p_val:.6f}")

    return {
        'regime_detail': regime_detail,
        'chi2': round(chi2, 4),
        'p_val': round(p_val, 6),
    }


# ── Test 5: PREFIX Context ───────────────────────────────────────────

def test_prefix_context(eligible, violations):
    """Test if specific source PREFIX contexts license violations."""
    print("\n=== TEST 5: PREFIX CONTEXT (source token) ===")

    prefix_elig = Counter(t['src_prefix'] or 'BARE' for t in eligible)
    prefix_viol = Counter(t['src_prefix'] or 'BARE' for t in violations)
    global_rate = len(violations) / max(1, len(eligible))

    prefix_detail = {}
    for pfx in sorted(prefix_elig.keys(), key=lambda x: prefix_elig[x], reverse=True):
        n_e = prefix_elig[pfx]
        n_v = prefix_viol.get(pfx, 0)
        rate = n_v / max(1, n_e)
        enrichment = rate / max(global_rate, 1e-10)
        prefix_detail[pfx] = {
            'eligible': n_e, 'violations': n_v,
            'rate': round(rate, 4), 'enrichment': round(enrichment, 3),
        }

    # Chi-squared for prefixes with >= 10 eligible
    big_prefixes = [p for p in prefix_elig if prefix_elig[p] >= 10]
    if len(big_prefixes) > 1:
        obs = np.array([prefix_viol.get(p, 0) for p in big_prefixes], dtype=float)
        exp = np.array([prefix_elig[p] * global_rate for p in big_prefixes], dtype=float)
        if exp.sum() > 0:
            exp = exp * (obs.sum() / exp.sum())
        valid_mask = exp >= 1
        if valid_mask.sum() > 1:
            chi2, p_val = sp_stats.chisquare(obs[valid_mask], exp[valid_mask])
        else:
            chi2, p_val = 0.0, 1.0
    else:
        chi2, p_val = 0.0, 1.0

    sortable = [(k, v) for k, v in prefix_detail.items() if v['eligible'] >= 10]
    top_enriched = sorted(sortable, key=lambda x: x[1]['enrichment'], reverse=True)[:5]
    top_depleted = sorted(sortable, key=lambda x: x[1]['enrichment'])[:5]

    print(f"  {len(prefix_detail)} unique source PREFIXes")
    print(f"  Chi-squared ({len(big_prefixes)} PREFIXes, n>=10): {chi2:.2f}, p={p_val:.6f}")
    print(f"  Top enriched:")
    for pfx, d in top_enriched:
        print(f"    {pfx}: {d['rate']:.3f} ({d['enrichment']:.2f}x) [{d['violations']}/{d['eligible']}]")
    print(f"  Top depleted:")
    for pfx, d in top_depleted:
        print(f"    {pfx}: {d['rate']:.3f} ({d['enrichment']:.2f}x) [{d['violations']}/{d['eligible']}]")

    return {
        'n_prefixes': len(prefix_detail),
        'chi2': round(chi2, 4),
        'p_val': round(p_val, 6),
        'n_tested': len(big_prefixes),
        'prefix_detail': prefix_detail,
        'top_enriched': {k: v for k, v in top_enriched},
        'top_depleted': {k: v for k, v in top_depleted},
    }


# ── Test 6: Specific Pair Variation ──────────────────────────────────

def test_pair_variation(eligible, violations, forbidden_class_pairs):
    """Test if all forbidden class pairs violate at the same rate."""
    print("\n=== TEST 6: SPECIFIC PAIR VARIATION ===")

    # For each forbidden class pair: count approaches and actual violations
    pair_approach = Counter()
    pair_viol = Counter()

    for t in eligible:
        src_cls = t['src_cls']
        # Count approaches: this source class is followed by SOME class
        for tgt_cls in set(fc[1] for fc in forbidden_class_pairs if fc[0] == src_cls):
            pair_approach[(src_cls, tgt_cls)] += 1

    for t in violations:
        pair_viol[(t['src_cls'], t['tgt_cls'])] += 1

    pair_detail = {}
    rates = []
    for sc, tc in sorted(forbidden_class_pairs):
        key = f"C{sc}->C{tc}"
        n_a = pair_approach.get((sc, tc), 0)
        n_v = pair_viol.get((sc, tc), 0)
        rate = n_v / max(1, n_a)
        pair_detail[key] = {'approaches': n_a, 'violations': n_v, 'rate': round(rate, 4),
                            'src_role': CLASS_TO_ROLE.get(sc, '?'), 'tgt_role': CLASS_TO_ROLE.get(tc, '?')}
        if n_a > 0:
            rates.append(rate)

    rates_arr = np.array(sorted(rates))
    if len(rates_arr) > 1 and rates_arr.sum() > 0:
        n = len(rates_arr)
        gini = (2 * np.sum((np.arange(1, n+1)) * rates_arr) - (n+1) * np.sum(rates_arr)) / (n * np.sum(rates_arr))
    else:
        gini = 0.0

    rate_range = (max(rates) - min(rates)) if rates else 0.0
    rate_cv = (np.std(rates) / max(np.mean(rates), 1e-10)) if rates else 0.0

    # Group by category
    categories = Counter()
    for (sc, tc), d in zip(sorted(forbidden_class_pairs),
                            [pair_detail[f"C{sc}->C{tc}"] for sc, tc in sorted(forbidden_class_pairs)]):
        cat = f"{d['src_role']}->{d['tgt_role']}"
        categories[cat] += d['violations']

    print(f"  Per-pair violation rates (sorted by rate):")
    for key, d in sorted(pair_detail.items(), key=lambda x: x[1]['rate'], reverse=True)[:10]:
        print(f"    {key} ({d['src_role']}->{d['tgt_role']}): {d['rate']:.4f} ({d['violations']}/{d['approaches']})")
    print(f"  Rate range: {rate_range:.4f}, CV: {rate_cv:.4f}, Gini: {gini:.4f}")
    print(f"  Violations by role-category: {dict(categories.most_common())}")

    return {
        'pair_detail': pair_detail,
        'rate_range': round(rate_range, 6),
        'rate_cv': round(rate_cv, 6),
        'gini': round(float(gini), 6),
        'n_pairs_with_data': len(rates),
        'category_violations': dict(categories),
    }


# ── Test 7: Violation Neighborhood ───────────────────────────────────

def test_violation_neighborhood(lines, line_meta, violations):
    """Compare properties of violation-containing lines vs clean lines."""
    print("\n=== TEST 7: VIOLATION NEIGHBORHOOD ===")

    violation_lines = set(t['line_idx'] for t in violations)

    def line_properties(line):
        classes = [t['cls'] for t in line]
        roles = [t['role'] for t in line]
        states = [t['state'] for t in line]
        middles = [t['middle'] for t in line]
        return {
            'length': len(line),
            'class_diversity': len(set(classes)) / max(1, len(classes)),
            'kernel_density': sum(1 for m in middles if m in {'k', 'h', 'e', 'ke', 'kch', 'he'}) / max(1, len(line)),
            'fl_density': sum(1 for s in states if s.startswith('FL')) / max(1, len(line)),
            'cc_density': sum(1 for r in roles if r == 'CC') / max(1, len(line)),
            'en_density': sum(1 for r in roles if r == 'EN') / max(1, len(line)),
            'unique_middle_rate': len(set(middles)) / max(1, len(middles)),
        }

    viol_props = defaultdict(list)
    clean_props = defaultdict(list)

    for idx, (line, meta) in enumerate(zip(lines, line_meta)):
        if len(line) < 2:
            continue
        props = line_properties(line)
        target = viol_props if idx in violation_lines else clean_props
        for k, v in props.items():
            target[k].append(v)

    results = {'n_violation_lines': len(violation_lines), 'n_clean_lines': len(lines) - len(violation_lines)}
    comparison = {}

    for prop in ['length', 'class_diversity', 'kernel_density', 'fl_density', 'cc_density', 'en_density', 'unique_middle_rate']:
        v_arr = np.array(viol_props[prop])
        c_arr = np.array(clean_props[prop])
        if len(v_arr) > 1 and len(c_arr) > 1:
            t_stat, t_p = sp_stats.ttest_ind(v_arr, c_arr)
            mw_stat, mw_p = sp_stats.mannwhitneyu(v_arr, c_arr, alternative='two-sided')
        else:
            t_stat, t_p, mw_stat, mw_p = 0.0, 1.0, 0.0, 1.0

        comparison[prop] = {
            'viol_mean': round(float(v_arr.mean()), 6),
            'clean_mean': round(float(c_arr.mean()), 6),
            'diff': round(float(v_arr.mean() - c_arr.mean()), 6),
            't_stat': round(float(t_stat), 4),
            't_p': round(float(t_p), 6),
            'mw_p': round(float(mw_p), 6),
        }
        sig = "**" if t_p < 0.001 else "*" if t_p < 0.01 else ""
        print(f"  {prop:25s}: viol={v_arr.mean():.4f}, clean={c_arr.mean():.4f}, diff={v_arr.mean()-c_arr.mean():+.4f}, p={t_p:.4f} {sig}")

    results['comparison'] = comparison
    return results


# ── Test 8: Sequential Context ───────────────────────────────────────

def test_sequential_context(lines, eligible, violations):
    """Compare what follows a violation vs what follows a compliant transition."""
    print("\n=== TEST 8: SEQUENTIAL CONTEXT ===")

    viol_set = set((t['line_idx'], t['token_idx']) for t in violations)

    # What class follows the target token (position i+2)?
    post_viol = []
    post_comp = []
    for t in eligible:
        line_idx = t['line_idx']
        tok_idx = t['token_idx']
        line = lines[line_idx]
        if tok_idx + 2 >= len(line):
            continue
        next_next_cls = line[tok_idx + 2]['cls']
        if (line_idx, tok_idx) in viol_set:
            post_viol.append(next_next_cls)
        else:
            post_comp.append(next_next_cls)

    # JSD of the target class distribution (position i+1)
    viol_targets = [t['tgt_cls'] for t in violations]
    comp_targets = [t['tgt_cls'] for t in eligible if not t['is_violation']]

    all_cls = set(viol_targets + comp_targets)
    def to_dist(lst, universe):
        c = Counter(lst)
        total = sum(c.values())
        return np.array([c.get(cl, 0) / max(1, total) for cl in sorted(universe)])

    if viol_targets and comp_targets:
        p = to_dist(viol_targets, all_cls)
        q = to_dist(comp_targets, all_cls)
        m = 0.5 * (p + q)
        jsd_target = float(0.5 * sp_entropy(p, m, base=2) + 0.5 * sp_entropy(q, m, base=2))
    else:
        jsd_target = 0.0

    # JSD of post-target class (i+2)
    if post_viol and post_comp:
        all_cls2 = set(post_viol + post_comp)
        p2 = to_dist(post_viol, all_cls2)
        q2 = to_dist(post_comp, all_cls2)
        m2 = 0.5 * (p2 + q2)
        jsd_post = float(0.5 * sp_entropy(p2, m2, base=2) + 0.5 * sp_entropy(q2, m2, base=2))
    else:
        jsd_post = 0.0

    # Target state distribution
    viol_target_states = Counter(t['tgt_state'] for t in violations)
    comp_target_states = Counter(t['tgt_state'] for t in eligible if not t['is_violation'])

    print(f"  JSD of target class (violations vs compliant): {jsd_target:.6f}")
    print(f"  JSD of post-target class (i+2): {jsd_post:.6f}")
    print(f"  N violations: {len(violations)}, N compliant: {len(eligible)-len(violations)}")
    print(f"  Violation target states: {dict(viol_target_states.most_common())}")
    print(f"  Compliant target states: {dict(comp_target_states.most_common(6))}")

    return {
        'jsd_target_class': round(jsd_target, 6),
        'jsd_post_target': round(jsd_post, 6),
        'n_viol': len(violations),
        'n_comp': len(eligible) - len(violations),
        'n_post_viol': len(post_viol),
        'n_post_comp': len(post_comp),
        'viol_target_states': dict(viol_target_states),
        'comp_target_states': dict(comp_target_states.most_common(6)),
    }


# ── Test 9: Section Specificity ──────────────────────────────────────

def test_section_specificity(eligible, violations):
    """Test if manuscript sections differ in violation rate."""
    print("\n=== TEST 9: SECTION SPECIFICITY ===")

    section_elig = Counter(t['section'] for t in eligible)
    section_viol = Counter(t['section'] for t in violations)
    global_rate = len(violations) / max(1, len(eligible))

    sections = sorted(section_elig.keys())
    section_detail = {}
    for s in sections:
        n_e = section_elig[s]
        n_v = section_viol.get(s, 0)
        rate = n_v / max(1, n_e)
        section_detail[s] = {
            'eligible': n_e, 'violations': n_v,
            'rate': round(rate, 4), 'enrichment': round(rate / max(global_rate, 1e-10), 3),
        }

    obs = np.array([section_viol.get(s, 0) for s in sections], dtype=float)
    exp = np.array([section_elig[s] * global_rate for s in sections], dtype=float)
    if exp.sum() > 0:
        exp = exp * (obs.sum() / exp.sum())
    valid_mask = exp >= 1
    if valid_mask.sum() > 1:
        chi2, p_val = sp_stats.chisquare(obs[valid_mask], exp[valid_mask])
    else:
        chi2, p_val = 0.0, 1.0

    print(f"  Per-section violation rates:")
    for s in sections:
        d = section_detail[s]
        print(f"    {s}: {d['rate']:.4f} ({d['enrichment']:.2f}x) [{d['violations']}/{d['eligible']}]")
    print(f"  Chi-squared: {chi2:.4f}, p={p_val:.6f}")

    return {
        'section_detail': section_detail,
        'chi2': round(chi2, 4),
        'p_val': round(p_val, 6),
    }


# ── Permutation Test ─────────────────────────────────────────────────

def permutation_test(eligible, violations, n_perm=2000):
    """Permutation test: if violations were randomly placed among eligible
    transitions, would we see as much folio-rate variance as observed?"""
    print("\n=== PERMUTATION TEST ===")

    n_viol = len(violations)
    n_elig = len(eligible)

    folio_elig = Counter(t['folio'] for t in eligible)
    folio_viol = Counter(t['folio'] for t in violations)
    folios = sorted(folio_elig.keys())

    obs_rates = np.array([folio_viol.get(f, 0) / max(1, folio_elig[f]) for f in folios])
    obs_var = obs_rates.var()

    # Also: observed range and observed regime chi2
    regime_elig = Counter(t['regime'] for t in eligible)
    regime_viol = Counter(t['regime'] for t in violations)
    regimes = sorted(r for r in regime_elig if r != 'UNKNOWN')
    obs_regime_rates = np.array([regime_viol.get(r, 0) / max(1, regime_elig[r]) for r in regimes])
    obs_regime_var = obs_regime_rates.var()

    perm_folio_vars = []
    perm_regime_vars = []

    elig_folios = [t['folio'] for t in eligible]
    elig_regimes = [t['regime'] for t in eligible]

    for _ in range(n_perm):
        perm_idx = np.random.choice(n_elig, size=n_viol, replace=False)

        perm_folio_viol = Counter()
        perm_regime_viol = Counter()
        for idx in perm_idx:
            perm_folio_viol[elig_folios[idx]] += 1
            perm_regime_viol[elig_regimes[idx]] += 1

        perm_f_rates = np.array([perm_folio_viol.get(f, 0) / max(1, folio_elig[f]) for f in folios])
        perm_folio_vars.append(perm_f_rates.var())

        perm_r_rates = np.array([perm_regime_viol.get(r, 0) / max(1, regime_elig[r]) for r in regimes])
        perm_regime_vars.append(perm_r_rates.var())

    perm_folio_vars = np.array(perm_folio_vars)
    perm_regime_vars = np.array(perm_regime_vars)

    p_folio = (perm_folio_vars >= obs_var).mean()
    p_regime = (perm_regime_vars >= obs_regime_var).mean()

    print(f"  Folio-rate variance: obs={obs_var:.8f}, perm_mean={perm_folio_vars.mean():.8f}, p={p_folio:.4f}")
    print(f"  Regime-rate variance: obs={obs_regime_var:.8f}, perm_mean={perm_regime_vars.mean():.8f}, p={p_regime:.4f}")

    return {
        'folio_obs_variance': round(float(obs_var), 8),
        'folio_perm_mean_variance': round(float(perm_folio_vars.mean()), 8),
        'folio_perm_p': round(float(p_folio), 6),
        'regime_obs_variance': round(float(obs_regime_var), 8),
        'regime_perm_mean_variance': round(float(perm_regime_vars.mean()), 8),
        'regime_perm_p': round(float(p_regime), 6),
        'n_permutations': n_perm,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("Phase 350: HAZARD_VIOLATION_ARCHAEOLOGY")
    print("=" * 60)

    (lines, line_meta, forbidden_middle_pairs, forbidden_class_pairs,
     forbidden_source_classes, forbidden_targets_by_source, folio_to_regime) = load_data()

    all_transitions, eligible, violations, middle_violations = find_violations(
        lines, line_meta, forbidden_class_pairs,
        forbidden_source_classes, forbidden_targets_by_source,
        forbidden_middle_pairs)

    print(f"\n  Total consecutive transitions: {len(all_transitions)}")
    print(f"  CLASS-level forbidden-eligible: {len(eligible)}")
    print(f"  CLASS-level violations: {len(violations)}")
    print(f"  CLASS-level violation rate: {len(violations)/max(1,len(eligible)):.4f}")
    print(f"  MIDDLE-level violations (for reference): {len(middle_violations)}")

    results = {
        'metadata': {
            'phase': 350,
            'name': 'HAZARD_VIOLATION_ARCHAEOLOGY',
            'total_transitions': len(all_transitions),
            'n_forbidden_middle_pairs': len(forbidden_middle_pairs),
            'n_forbidden_class_pairs': len(forbidden_class_pairs),
            'class_level_eligible': len(eligible),
            'class_level_violations': len(violations),
            'class_level_violation_rate': round(len(violations) / max(1, len(eligible)), 6),
            'middle_level_violations': len(middle_violations),
        }
    }

    results['test1_folio_clustering'] = test_folio_clustering(eligible, violations)
    results['test2_line_position'] = test_line_position(eligible, violations)
    results['test3_paragraph_position'] = test_paragraph_position(eligible, violations)
    results['test4_regime_specificity'] = test_regime_specificity(eligible, violations)
    results['test5_prefix_context'] = test_prefix_context(eligible, violations)
    results['test6_pair_variation'] = test_pair_variation(eligible, violations, forbidden_class_pairs)
    results['test7_violation_neighborhood'] = test_violation_neighborhood(lines, line_meta, violations)
    results['test8_sequential_context'] = test_sequential_context(lines, eligible, violations)
    results['test9_section_specificity'] = test_section_specificity(eligible, violations)
    results['permutation_test'] = permutation_test(eligible, violations)

    # ── Summary Verdict ──────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    systematic_signals = []

    t1 = results['test1_folio_clustering']
    if t1['p_chi2'] < 0.01:
        systematic_signals.append(f"FOLIO_CLUSTERED (chi2 p={t1['p_chi2']:.6f}, DI={t1['dispersion_index']:.3f})")

    t2 = results['test2_line_position']
    if t2['ks_p'] < 0.01:
        systematic_signals.append(f"LINE_POSITION_BIASED (KS p={t2['ks_p']:.6f})")

    t3 = results['test3_paragraph_position']
    if t3['p_val'] < 0.01:
        systematic_signals.append(f"PARAGRAPH_BIASED (chi2 p={t3['p_val']:.6f})")

    t4 = results['test4_regime_specificity']
    if t4['p_val'] < 0.01:
        systematic_signals.append(f"REGIME_SPECIFIC (chi2 p={t4['p_val']:.6f})")

    t5 = results['test5_prefix_context']
    if t5['p_val'] < 0.01:
        systematic_signals.append(f"PREFIX_CONTEXTUAL (chi2 p={t5['p_val']:.6f})")

    t9 = results['test9_section_specificity']
    if t9['p_val'] < 0.01:
        systematic_signals.append(f"SECTION_SPECIFIC (chi2 p={t9['p_val']:.6f})")

    perm = results['permutation_test']
    if perm['folio_perm_p'] < 0.05:
        systematic_signals.append(f"FOLIO_PERMUTATION_SIG (p={perm['folio_perm_p']:.4f})")
    if perm['regime_perm_p'] < 0.05:
        systematic_signals.append(f"REGIME_PERMUTATION_SIG (p={perm['regime_perm_p']:.4f})")

    if len(systematic_signals) >= 3:
        verdict = "SYSTEMATIC"
    elif len(systematic_signals) >= 1:
        verdict = "PARTIALLY_SYSTEMATIC"
    else:
        verdict = "RANDOM"

    results['summary'] = {
        'verdict': verdict,
        'n_systematic_signals': len(systematic_signals),
        'signals': systematic_signals,
    }

    for sig in systematic_signals:
        print(f"  SIGNAL: {sig}")
    print(f"\n  VERDICT: {verdict} ({len(systematic_signals)}/8 possible signals)")

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'hazard_violation_archaeology.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
