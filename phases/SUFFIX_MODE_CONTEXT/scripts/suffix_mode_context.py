"""
Phase 470: SUFFIX_MODE_CONTEXT

Decomposes the ~20% contextual residual in suffix mode prediction (C1341).
Phase 469 showed suffix mode is ~80% emergent from token identity. This phase
identifies what drives the remaining ~20%: PREFIX, line category environment,
position within line, and/or paragraph opener mode.

Tests:
  T1: PREFIX modulation of suffix choice for flexible MIDDLEs
  T2: Line category environment effect on flexible MIDDLEs
  T3: Position within line effect on flexible MIDDLEs
  T4: Paragraph opener mode propagation to flexible MIDDLEs
  T5: Variance decomposition across all factors

References: C1338, C1339, C1340, C1341, C1297, C1279, C1309, C1256, C1312
"""

import json
import sys
import math
import time
import random
import functools
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

# Phase 469: data building, suffix classification, MI, constants
sys.path.insert(0, str(ROOT / 'phases' / 'SUFFIX_MODE_ASSIGNMENT' / 'scripts'))
from suffix_mode_assignment import (
    build_b_lines, classify_suffix_mode, suffix_category,
    mutual_information, chi2_independence, entropy_from_counts,
    TERMINAL_SUFFIXES, CONNECTOR_SUFFIXES, ITERATE_SUFFIXES,
    MODE_A_CENTROID, MODE_B_CENTROID, SUFFIX_CATS, euclidean_dist,
)

# Phase 462: stats
sys.path.insert(0, str(ROOT / 'phases' / 'TEXT_BLOCK_PARALLEL_OPERATORS' / 'scripts'))
from text_block_parallel_operators import (
    jsd, normalize_profile, normal_cdf, chi2_sf, mann_whitney_u
)

# Phase 463: Spearman
sys.path.insert(0, str(ROOT / 'phases' / 'BLOCK_GALLOWS_ORDERING' / 'scripts'))
from block_gallows_ordering import spearman_rho

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "SUFFIX_MODE_CONTEXT" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 1000
SEED = 42

# Flexible MIDDLE threshold: selectivity < 0.80
FLEX_THRESHOLD = 0.80
MIN_FREQ = 20  # minimum total frequency for a MIDDLE to be included

ALL_CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
                  'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']


# ================================================================
# UTILITY FUNCTIONS
# ================================================================

def prefix_group(prefix):
    """Map raw prefix to analysis group."""
    if prefix is None or prefix == '':
        return 'BARE'
    if prefix == 'qo':
        return 'qo'
    if prefix == 'ch':
        return 'ch'
    if prefix == 'sh':
        return 'sh'
    if prefix == 'da':
        return 'da'
    if prefix in ('ok', 'ot', 'ol'):
        return 'ok_group'
    return 'OTHER'


def fisher_combine_pvalues(pvals):
    """Fisher's method for combining p-values: -2 * sum(ln(p)) ~ chi2(2k).

    Returns combined p-value. Handles p=0 by clamping to 1e-15.
    """
    if not pvals:
        return 1.0
    k = len(pvals)
    stat = 0.0
    for p in pvals:
        p_clamped = max(p, 1e-15)
        stat += -2.0 * math.log(p_clamped)
    # chi2 survival with 2k degrees of freedom
    return chi2_sf(stat, 2 * k)


def conditional_mi_within_middle(tokens, predictor_key, outcome_key='suffix_cat'):
    """Compute I(outcome; predictor | MIDDLE) as weighted average of within-MIDDLE MI.

    For each MIDDLE with tokens in 2+ predictor groups: compute MI(predictor; outcome)
    within that MIDDLE. Weight-average by token count.

    Returns: (weighted_mi, n_middles_used, per_middle_details)
    """
    # Group tokens by MIDDLE
    by_middle = defaultdict(list)
    for t in tokens:
        if t.get('middle'):
            by_middle[t['middle']].append(t)

    total_weight = 0
    weighted_sum = 0.0
    details = []

    for mid, toks in by_middle.items():
        pred_vals = [t[predictor_key] for t in toks]
        out_vals = [t[outcome_key] for t in toks]
        # Need 2+ distinct predictor values
        if len(set(pred_vals)) < 2:
            continue
        mi = mutual_information(pred_vals, out_vals)
        n = len(toks)
        weighted_sum += mi * n
        total_weight += n
        details.append({'middle': mid, 'mi': round(mi, 6), 'n': n})

    if total_weight == 0:
        return 0.0, 0, []

    weighted_mi = weighted_sum / total_weight
    details.sort(key=lambda x: x['mi'], reverse=True)
    return weighted_mi, len(details), details


def leave_one_out_thermal_frac(line_tokens, exclude_idx):
    """Compute THERMAL fraction of line tokens excluding token at exclude_idx."""
    n_thermal = 0
    n_total = 0
    for i, t in enumerate(line_tokens):
        if i == exclude_idx:
            continue
        cat = t.get('category')
        if cat:
            n_total += 1
            if cat == 'THERMAL':
                n_thermal += 1
    if n_total == 0:
        return None
    return n_thermal / n_total


def leave_one_out_dominant_cat(line_tokens, exclude_idx):
    """Compute dominant category of line tokens excluding token at exclude_idx."""
    counts = Counter()
    for i, t in enumerate(line_tokens):
        if i == exclude_idx:
            continue
        cat = t.get('category')
        if cat:
            counts[cat] += 1
    if not counts:
        return None
    return counts.most_common(1)[0][0]


def suffix_numeric_code(suffix_cat):
    """Encode suffix_cat as numeric for correlation: terminal=1, bare=0, others=0.5."""
    if suffix_cat == 'terminal':
        return 1.0
    elif suffix_cat == 'bare':
        return 0.0
    else:
        return 0.5


# ================================================================
# DATA PREPARATION
# ================================================================

def build_context_data(classified_lines, all_tokens):
    """Annotate tokens and lines with context features for T1-T5.

    Adds to each token:
        modal_suffix_cat, deviates, selectivity, is_flexible,
        line_position_frac, position_zone, prefix_group, para_opener_mode
    Adds to each line:
        para_opener_mode

    Returns: flexible_tokens (list of token dicts for flexible MIDDLEs with freq >= MIN_FREQ)
    """
    print("\n=== Building context data ===")

    # Step 1: Compute per-MIDDLE modal suffix and selectivity
    mid_tokens = defaultdict(list)
    for t in all_tokens:
        if t.get('middle'):
            mid_tokens[t['middle']].append(t)

    mid_modal_suffix = {}  # middle -> most common suffix_cat
    mid_selectivity = {}   # middle -> max fraction
    mid_freq = {}          # middle -> total count

    for mid, toks in mid_tokens.items():
        counts = Counter(t['suffix_cat'] for t in toks)
        total = sum(counts.values())
        mid_freq[mid] = total
        most_common_cat = counts.most_common(1)[0][0]
        mid_modal_suffix[mid] = most_common_cat
        mid_selectivity[mid] = counts[most_common_cat] / total

    # Step 2: Identify paragraph opener modes
    # Group lines by para_id, find first body line's mode
    para_lines = defaultdict(list)
    for line in classified_lines:
        para_lines[line['para_id']].append(line)

    para_opener_mode = {}
    for pid, lines in para_lines.items():
        # Lines are already body lines (headers excluded by build_b_lines)
        # Sort by line_num to find opener (first body line)
        sorted_lines = sorted(lines, key=lambda l: l['line_num'])
        para_opener_mode[pid] = sorted_lines[0]['mode']

    # Step 3: Annotate lines with opener mode
    for line in classified_lines:
        line['para_opener_mode'] = para_opener_mode.get(line['para_id'])

    # Step 4: Annotate each token
    # Need to iterate by line to get position info
    for line in classified_lines:
        n_tok = len(line['tokens'])
        opener_mode = line.get('para_opener_mode')
        for idx, tok in enumerate(line['tokens']):
            mid = tok.get('middle')
            if mid and mid in mid_modal_suffix:
                tok['modal_suffix_cat'] = mid_modal_suffix[mid]
                tok['selectivity'] = mid_selectivity[mid]
                tok['deviates'] = (tok['suffix_cat'] != mid_modal_suffix[mid])
                tok['is_flexible'] = (mid_selectivity[mid] < FLEX_THRESHOLD
                                       and mid_freq[mid] >= MIN_FREQ)
            else:
                tok['modal_suffix_cat'] = None
                tok['selectivity'] = None
                tok['deviates'] = None
                tok['is_flexible'] = False

            # Position
            if n_tok > 1:
                tok['line_position_frac'] = idx / (n_tok - 1)
            else:
                tok['line_position_frac'] = 0.5
            frac = tok['line_position_frac']
            if frac < 1.0 / 3.0:
                tok['position_zone'] = 'EARLY'
            elif frac < 2.0 / 3.0:
                tok['position_zone'] = 'MID'
            else:
                tok['position_zone'] = 'LATE'

            # PREFIX group
            tok['prefix_group'] = prefix_group(tok.get('prefix'))

            # Paragraph opener mode
            tok['para_opener_mode'] = opener_mode

            # Is this token on the opener line?
            sorted_para_lines = sorted(para_lines.get(line['para_id'], []),
                                        key=lambda l: l['line_num'])
            if sorted_para_lines:
                tok['is_opener_line'] = (line['line_num'] == sorted_para_lines[0]['line_num'])
            else:
                tok['is_opener_line'] = False

    # Step 5: Collect flexible tokens
    flexible_tokens = [t for t in all_tokens if t.get('is_flexible')]

    # Report
    n_flex_middles = len(set(t['middle'] for t in flexible_tokens))
    print(f"  Flexible MIDDLEs (sel<{FLEX_THRESHOLD}, freq>={MIN_FREQ}): {n_flex_middles}")
    print(f"  Flexible tokens: {len(flexible_tokens)}")
    print(f"  Deviation rate: {sum(1 for t in flexible_tokens if t['deviates'])/len(flexible_tokens)*100:.1f}%")

    # Summary of flexible MIDDLEs
    flex_mids = sorted(set(t['middle'] for t in flexible_tokens))
    for mid in flex_mids[:10]:
        sel = mid_selectivity[mid]
        freq = mid_freq[mid]
        modal = mid_modal_suffix[mid]
        print(f"    {mid}: sel={sel:.3f} freq={freq} modal={modal}")
    if len(flex_mids) > 10:
        print(f"    ... and {len(flex_mids) - 10} more")

    return flexible_tokens


# ================================================================
# TEST T1: PREFIX Modulation of Suffix Choice
# ================================================================

def test_t1(flexible_tokens, rng):
    """Does PREFIX modulate suffix choice for flexible MIDDLEs?"""
    print("\n=== T1: PREFIX Modulation of Suffix Choice ===")

    tokens = [t for t in flexible_tokens if t.get('middle')]
    print(f"  Tokens: {len(tokens)}")

    # --- Raw contingency: prefix_group x suffix_cat ---
    contingency = defaultdict(Counter)
    for t in tokens:
        contingency[t['prefix_group']][t['suffix_cat']] += 1

    pfx_groups = sorted(contingency.keys())
    chi2_val, chi2_p, chi2_n = chi2_independence(dict(contingency))
    n_total = chi2_n
    min_dim = min(len(pfx_groups), len(SUFFIX_CATS)) - 1
    v = math.sqrt(chi2_val / (n_total * min_dim)) if n_total * min_dim > 0 else 0.0

    print(f"  PREFIX groups: {pfx_groups}")
    print(f"  Chi2={chi2_val:.1f}, V={v:.4f}, p={chi2_p:.6f}")

    # --- Per-group suffix profile and deviation rate ---
    group_profiles = {}
    group_deviation_rates = {}
    for pg in pfx_groups:
        pg_tokens = [t for t in tokens if t['prefix_group'] == pg]
        cats = Counter(t['suffix_cat'] for t in pg_tokens)
        total = sum(cats.values())
        profile = {sc: cats.get(sc, 0) / total for sc in SUFFIX_CATS}
        group_profiles[pg] = profile
        n_dev = sum(1 for t in pg_tokens if t['deviates'])
        group_deviation_rates[pg] = {
            'deviation_rate': round(n_dev / total, 4) if total > 0 else 0.0,
            'n': total,
            'terminal_frac': round(profile.get('terminal', 0), 4),
            'bare_frac': round(profile.get('bare', 0), 4),
        }
        print(f"    {pg}: n={total} terminal={profile.get('terminal',0):.3f} "
              f"bare={profile.get('bare',0):.3f} dev_rate={n_dev/total:.3f}")

    # --- Conditional MI: I(suffix_cat; PREFIX | MIDDLE) ---
    cond_mi, n_mid_used, mi_details = conditional_mi_within_middle(
        tokens, 'prefix_group', 'suffix_cat'
    )
    print(f"  Conditional MI (suffix; PREFIX | MIDDLE): {cond_mi:.6f} bits")
    print(f"  MIDDLEs contributing: {n_mid_used}")

    # --- Permutation null for conditional MI ---
    null_mis = []
    for perm_i in range(N_PERM):
        # Shuffle PREFIX labels within each MIDDLE
        by_middle = defaultdict(list)
        for t in tokens:
            by_middle[t['middle']].append(t)

        for mid, toks in by_middle.items():
            pfx_labels = [t['prefix_group'] for t in toks]
            rng.shuffle(pfx_labels)
            for i, t in enumerate(toks):
                t['_perm_prefix_group'] = pfx_labels[i]

        # Compute conditional MI with shuffled labels
        perm_mi, _, _ = conditional_mi_within_middle(
            tokens, '_perm_prefix_group', 'suffix_cat'
        )
        null_mis.append(perm_mi)

    null_mean = sum(null_mis) / len(null_mis)
    n_ge = sum(1 for nm in null_mis if nm >= cond_mi)
    perm_p = (n_ge + 1) / (N_PERM + 1)
    print(f"  Null mean MI: {null_mean:.6f}, Perm p={perm_p:.4f}")

    # Clean up temp key
    for t in tokens:
        t.pop('_perm_prefix_group', None)

    # --- Verdict ---
    passes_mi = cond_mi > 0.010
    passes_perm = perm_p < 0.01
    passes_v = v > 0.10
    if passes_mi and passes_perm and passes_v:
        verdict = 'PASS'
    elif not passes_mi and not passes_v:
        verdict = 'FAIL'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict} (MI>{0.010}:{passes_mi}, perm<0.01:{passes_perm}, V>{0.10}:{passes_v})")

    return {
        'test': 'T1_prefix_modulation',
        'verdict': verdict,
        'n_tokens': len(tokens),
        'chi2': round(chi2_val, 2),
        'cramers_v': round(v, 4),
        'chi2_p': chi2_p,
        'conditional_mi_bits': round(cond_mi, 6),
        'null_mean_mi': round(null_mean, 6),
        'perm_p': round(perm_p, 4),
        'n_middles_used': n_mid_used,
        'group_profiles': {pg: {k: round(v, 4) for k, v in prof.items()}
                           for pg, prof in group_profiles.items()},
        'group_deviation_rates': group_deviation_rates,
        'top_mi_middles': mi_details[:10],
    }


# ================================================================
# TEST T2: Line Category Environment
# ================================================================

def test_t2(flexible_tokens, classified_lines, rng):
    """Does the category composition of OTHER tokens on the line predict suffix choice?"""
    print("\n=== T2: Line Category Environment ===")

    # Build line lookup: (folio, line_num) -> line dict
    line_lookup = {}
    for line in classified_lines:
        key = (line['folio'], line['line_num'])
        line_lookup[key] = line

    # For each flexible token, compute leave-one-out THERMAL fraction
    records = []
    for line in classified_lines:
        for idx, tok in enumerate(line['tokens']):
            if not tok.get('is_flexible'):
                continue
            thermal_frac = leave_one_out_thermal_frac(line['tokens'], idx)
            if thermal_frac is None:
                continue
            dom_cat = leave_one_out_dominant_cat(line['tokens'], idx)
            records.append({
                'suffix_cat': tok['suffix_cat'],
                'thermal_frac': thermal_frac,
                'dom_cat': dom_cat,
                'deviates': tok['deviates'],
                'middle': tok['middle'],
            })

    print(f"  Flexible tokens with LOO context: {len(records)}")

    # --- Mann-Whitney: thermal_frac for terminal vs bare tokens ---
    terminal_thermals = [r['thermal_frac'] for r in records if r['suffix_cat'] == 'terminal']
    bare_thermals = [r['thermal_frac'] for r in records if r['suffix_cat'] == 'bare']

    if terminal_thermals and bare_thermals:
        u_stat, u_z, u_p = mann_whitney_u(terminal_thermals, bare_thermals)
        mean_t = sum(terminal_thermals) / len(terminal_thermals)
        mean_b = sum(bare_thermals) / len(bare_thermals)
        print(f"  Terminal tokens: n={len(terminal_thermals)}, mean THERMAL_frac={mean_t:.4f}")
        print(f"  Bare tokens: n={len(bare_thermals)}, mean THERMAL_frac={mean_b:.4f}")
        print(f"  Mann-Whitney U: Z={u_z:.3f}, p={u_p:.6f}")
    else:
        u_z, u_p = 0.0, 1.0
        mean_t, mean_b = 0.0, 0.0
        print("  Insufficient terminal or bare tokens for Mann-Whitney")

    # --- Quintile analysis: bin by thermal_frac, compute terminal frac per quintile ---
    all_thermal_fracs = sorted(r['thermal_frac'] for r in records)
    n_rec = len(records)
    quintile_boundaries = []
    for q in range(1, 5):
        idx = int(n_rec * q / 5)
        quintile_boundaries.append(all_thermal_fracs[min(idx, n_rec - 1)])

    def assign_quintile(tf):
        for i, boundary in enumerate(quintile_boundaries):
            if tf <= boundary:
                return i
        return 4

    quintile_data = defaultdict(lambda: {'terminal': 0, 'total': 0, 'thermal_sum': 0.0})
    for r in records:
        q = assign_quintile(r['thermal_frac'])
        quintile_data[q]['total'] += 1
        quintile_data[q]['thermal_sum'] += r['thermal_frac']
        if r['suffix_cat'] == 'terminal':
            quintile_data[q]['terminal'] += 1

    quintile_results = []
    quintile_x = []
    quintile_y = []
    for q in range(5):
        d = quintile_data[q]
        if d['total'] > 0:
            tf = d['terminal'] / d['total']
            mean_th = d['thermal_sum'] / d['total']
        else:
            tf = 0.0
            mean_th = 0.0
        quintile_results.append({
            'quintile': q,
            'n': d['total'],
            'terminal_frac': round(tf, 4),
            'mean_thermal_frac': round(mean_th, 4),
        })
        quintile_x.append(mean_th)
        quintile_y.append(tf)
        print(f"    Q{q}: n={d['total']} mean_thermal={mean_th:.3f} terminal_frac={tf:.3f}")

    # Spearman on quintile medians
    if len(quintile_x) >= 3:
        sp_rho, sp_p = spearman_rho(quintile_x, quintile_y)
        print(f"  Quintile Spearman rho={sp_rho:.3f}, p={sp_p:.4f}")
    else:
        sp_rho, sp_p = 0.0, 1.0

    # --- Conditional MI: I(suffix_cat; dom_cat | MIDDLE) ---
    # Tag each token with its neighborhood dominant category
    for t in flexible_tokens:
        t['_loo_dom_cat'] = None  # will be set from records if available

    rec_idx = 0
    for line in classified_lines:
        for idx, tok in enumerate(line['tokens']):
            if not tok.get('is_flexible'):
                continue
            if rec_idx < len(records):
                tok['_loo_dom_cat'] = records[rec_idx]['dom_cat']
                rec_idx += 1

    # Use records directly for conditional MI
    loo_tokens_for_mi = [
        {'middle': r['middle'], '_loo_dom_cat': r['dom_cat'], 'suffix_cat': r['suffix_cat']}
        for r in records if r['dom_cat'] is not None
    ]
    cond_mi, n_mid_used, mi_details = conditional_mi_within_middle(
        loo_tokens_for_mi, '_loo_dom_cat', 'suffix_cat'
    )
    print(f"  Conditional MI (suffix; LOO_dom_cat | MIDDLE): {cond_mi:.6f} bits")
    print(f"  MIDDLEs contributing: {n_mid_used}")

    # --- Verdict ---
    passes_mw = u_p < 0.01
    passes_rho = abs(sp_rho) > 0.30
    passes_mi = cond_mi > 0.005
    if passes_mw and passes_rho and passes_mi:
        verdict = 'PASS'
    elif not passes_mw and not passes_mi:
        verdict = 'FAIL'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict} (MW_p<0.01:{passes_mw}, |rho|>0.30:{passes_rho}, MI>0.005:{passes_mi})")

    return {
        'test': 'T2_category_environment',
        'verdict': verdict,
        'n_tokens': len(records),
        'terminal_mean_thermal_frac': round(mean_t, 4),
        'bare_mean_thermal_frac': round(mean_b, 4),
        'mann_whitney_z': round(u_z, 3),
        'mann_whitney_p': round(u_p, 6),
        'quintile_spearman_rho': round(sp_rho, 3),
        'quintile_spearman_p': round(sp_p, 4),
        'quintile_data': quintile_results,
        'conditional_mi_bits': round(cond_mi, 6),
        'n_middles_used': n_mid_used,
        'top_mi_middles': mi_details[:10],
    }


# ================================================================
# TEST T3: Position Within Line
# ================================================================

def test_t3(flexible_tokens, rng):
    """Does position within the line affect suffix choice for flexible MIDDLEs?"""
    print("\n=== T3: Position Within Line ===")

    tokens = [t for t in flexible_tokens if t.get('middle')]
    print(f"  Tokens: {len(tokens)}")

    # --- Contingency: position_zone x suffix_cat ---
    contingency = defaultdict(Counter)
    for t in tokens:
        contingency[t['position_zone']][t['suffix_cat']] += 1

    zones = ['EARLY', 'MID', 'LATE']
    chi2_val, chi2_p, chi2_n = chi2_independence(dict(contingency))
    n_total = chi2_n
    min_dim = min(len(zones), len(SUFFIX_CATS)) - 1
    v = math.sqrt(chi2_val / (n_total * min_dim)) if n_total * min_dim > 0 else 0.0

    print(f"  Chi2={chi2_val:.1f}, V={v:.4f}, p={chi2_p:.6f}")

    # Per-zone profiles
    zone_profiles = {}
    for z in zones:
        z_tokens = [t for t in tokens if t['position_zone'] == z]
        cats = Counter(t['suffix_cat'] for t in z_tokens)
        total = sum(cats.values())
        if total > 0:
            profile = {sc: cats.get(sc, 0) / total for sc in SUFFIX_CATS}
        else:
            profile = {sc: 0.0 for sc in SUFFIX_CATS}
        zone_profiles[z] = profile
        print(f"    {z}: n={total} terminal={profile.get('terminal',0):.3f} "
              f"bare={profile.get('bare',0):.3f}")

    # --- Spearman: position (continuous) vs suffix_code ---
    positions = [t['line_position_frac'] for t in tokens]
    suffix_codes = [suffix_numeric_code(t['suffix_cat']) for t in tokens]

    if len(positions) >= 10:
        sp_rho, sp_p = spearman_rho(positions, suffix_codes)
        print(f"  Spearman rho={sp_rho:.4f}, p={sp_p:.6f}")
    else:
        sp_rho, sp_p = 0.0, 1.0

    # --- Conditional MI: I(suffix_cat; position_zone | MIDDLE) ---
    cond_mi, n_mid_used, mi_details = conditional_mi_within_middle(
        tokens, 'position_zone', 'suffix_cat'
    )
    print(f"  Conditional MI (suffix; position | MIDDLE): {cond_mi:.6f} bits")
    print(f"  MIDDLEs contributing: {n_mid_used}")

    # --- Per-MIDDLE position effect ---
    by_middle = defaultdict(list)
    for t in tokens:
        by_middle[t['middle']].append(t)

    per_mid_rhos = []
    for mid, toks in by_middle.items():
        if len(toks) < 10:
            continue
        pos = [t['line_position_frac'] for t in toks]
        codes = [suffix_numeric_code(t['suffix_cat']) for t in toks]
        if len(set(codes)) < 2:
            continue
        rho_m, p_m = spearman_rho(pos, codes)
        per_mid_rhos.append({'middle': mid, 'rho': round(rho_m, 4), 'p': round(p_m, 4),
                             'n': len(toks)})

    per_mid_rhos.sort(key=lambda x: abs(x['rho']), reverse=True)
    mean_abs_rho = (sum(abs(r['rho']) for r in per_mid_rhos) / len(per_mid_rhos)
                    if per_mid_rhos else 0.0)
    print(f"  Per-MIDDLE position rho: n={len(per_mid_rhos)}, mean |rho|={mean_abs_rho:.3f}")

    # --- Verdict ---
    passes_v = v > 0.05
    passes_chi2 = chi2_p < 0.01
    passes_mi = cond_mi > 0.003
    if passes_v and passes_chi2 and passes_mi:
        verdict = 'PASS'
    elif not passes_chi2 and not passes_mi:
        verdict = 'FAIL'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict} (V>0.05:{passes_v}, chi2_p<0.01:{passes_chi2}, MI>0.003:{passes_mi})")

    return {
        'test': 'T3_position',
        'verdict': verdict,
        'n_tokens': len(tokens),
        'chi2': round(chi2_val, 2),
        'cramers_v': round(v, 4),
        'chi2_p': chi2_p,
        'spearman_rho': round(sp_rho, 4),
        'spearman_p': round(sp_p, 6),
        'conditional_mi_bits': round(cond_mi, 6),
        'n_middles_used': n_mid_used,
        'zone_profiles': {z: {k: round(val, 4) for k, val in prof.items()}
                          for z, prof in zone_profiles.items()},
        'per_middle_position_rho': {
            'n_middles': len(per_mid_rhos),
            'mean_abs_rho': round(mean_abs_rho, 4),
            'top_5': per_mid_rhos[:5],
        },
        'top_mi_middles': mi_details[:10],
    }


# ================================================================
# TEST T4: Paragraph Opener Mode Propagation
# ================================================================

def test_t4(flexible_tokens, classified_lines, rng):
    """Does paragraph opener mode propagate to suffix choice for flexible MIDDLEs?"""
    print("\n=== T4: Paragraph Opener Mode Propagation ===")

    # Filter to non-opener body lines only (avoid circularity)
    tokens = [t for t in flexible_tokens
              if t.get('middle') and not t.get('is_opener_line')
              and t.get('para_opener_mode') is not None]
    print(f"  Non-opener flexible tokens: {len(tokens)}")

    # --- Contingency: opener_mode x suffix_cat ---
    contingency = defaultdict(Counter)
    for t in tokens:
        contingency[t['para_opener_mode']][t['suffix_cat']] += 1

    modes = ['A', 'B']
    chi2_val, chi2_p, chi2_n = chi2_independence(dict(contingency))
    n_total = chi2_n
    min_dim = min(len(modes), len(SUFFIX_CATS)) - 1
    v = math.sqrt(chi2_val / (n_total * min_dim)) if n_total * min_dim > 0 else 0.0

    print(f"  Chi2={chi2_val:.1f}, V={v:.4f}, p={chi2_p:.6f}")

    # Per-opener-mode profiles
    opener_profiles = {}
    for m in modes:
        m_tokens = [t for t in tokens if t['para_opener_mode'] == m]
        cats = Counter(t['suffix_cat'] for t in m_tokens)
        total = sum(cats.values())
        if total > 0:
            profile = {sc: cats.get(sc, 0) / total for sc in SUFFIX_CATS}
            dev_rate = sum(1 for t in m_tokens if t['deviates']) / total
        else:
            profile = {sc: 0.0 for sc in SUFFIX_CATS}
            dev_rate = 0.0
        opener_profiles[m] = {
            'profile': profile,
            'n': total,
            'deviation_rate': round(dev_rate, 4),
        }
        print(f"    Opener {m}: n={total} terminal={profile.get('terminal',0):.3f} "
              f"bare={profile.get('bare',0):.3f} dev_rate={dev_rate:.3f}")

    # --- Conditional MI: I(suffix_cat; opener_mode | MIDDLE) ---
    cond_mi, n_mid_used, mi_details = conditional_mi_within_middle(
        tokens, 'para_opener_mode', 'suffix_cat'
    )
    print(f"  Conditional MI (suffix; opener_mode | MIDDLE): {cond_mi:.6f} bits")
    print(f"  MIDDLEs contributing: {n_mid_used}")

    # --- Section stratification ---
    section_results = []
    section_pvals = []
    by_section = defaultdict(list)
    for t in tokens:
        by_section[t.get('section', '?')].append(t)

    for sec in sorted(by_section.keys()):
        sec_tokens = by_section[sec]
        if len(sec_tokens) < 30:
            continue
        sec_cont = defaultdict(Counter)
        for t in sec_tokens:
            sec_cont[t['para_opener_mode']][t['suffix_cat']] += 1
        sec_chi2_val, sec_chi2_p, sec_chi2_n = chi2_independence(dict(sec_cont))
        sec_v = math.sqrt(sec_chi2_val / (sec_chi2_n * min_dim)) if sec_chi2_n * min_dim > 0 else 0.0
        section_results.append({
            'section': sec,
            'n': sec_chi2_n,
            'chi2': round(sec_chi2_val, 2),
            'v': round(sec_v, 4),
            'p': sec_chi2_p,
        })
        if sec_chi2_p < 1.0:
            section_pvals.append(sec_chi2_p)
        print(f"    Section {sec}: n={sec_chi2_n} V={sec_v:.4f} p={sec_chi2_p:.4f}")

    # Fisher-combined p-value
    if section_pvals:
        fisher_p = fisher_combine_pvalues(section_pvals)
        print(f"  Fisher combined p={fisher_p:.6f}")
    else:
        fisher_p = 1.0

    # --- Verdict ---
    passes_v = v > 0.05
    passes_chi2 = chi2_p < 0.01
    passes_mi = cond_mi > 0.003
    passes_fisher = fisher_p < 0.01
    if passes_v and passes_chi2 and passes_mi and passes_fisher:
        verdict = 'PASS'
    elif not passes_chi2 and not passes_mi:
        verdict = 'FAIL'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict} (V>0.05:{passes_v}, chi2_p<0.01:{passes_chi2}, "
          f"MI>0.003:{passes_mi}, Fisher<0.01:{passes_fisher})")

    return {
        'test': 'T4_paragraph_opener',
        'verdict': verdict,
        'n_tokens': len(tokens),
        'chi2': round(chi2_val, 2),
        'cramers_v': round(v, 4),
        'chi2_p': chi2_p,
        'conditional_mi_bits': round(cond_mi, 6),
        'n_middles_used': n_mid_used,
        'opener_profiles': {m: {
            'n': d['n'],
            'deviation_rate': d['deviation_rate'],
            'profile': {k: round(val, 4) for k, val in d['profile'].items()},
        } for m, d in opener_profiles.items()},
        'section_stratification': section_results,
        'fisher_combined_p': round(fisher_p, 6),
        'top_mi_middles': mi_details[:10],
    }


# ================================================================
# TEST T5: Variance Decomposition
# ================================================================

def test_t5(flexible_tokens, classified_lines):
    """How much of the contextual residual does each factor explain?"""
    print("\n=== T5: Variance Decomposition ===")

    # Prepare records with all 4 predictors
    records = []
    for line in classified_lines:
        for idx, tok in enumerate(line['tokens']):
            if not tok.get('is_flexible'):
                continue
            if tok.get('deviates') is None:
                continue
            thermal_frac = leave_one_out_thermal_frac(line['tokens'], idx)
            if thermal_frac is None:
                thermal_frac = 0.0
            # Bin thermal frac into thirds for combinatorial analysis
            if thermal_frac < 0.15:
                thermal_bin = 'LOW'
            elif thermal_frac < 0.35:
                thermal_bin = 'MED'
            else:
                thermal_bin = 'HIGH'

            records.append({
                'middle': tok['middle'],
                'suffix_cat': tok['suffix_cat'],
                'deviates': tok['deviates'],
                'prefix_group': tok['prefix_group'],
                'position_zone': tok['position_zone'],
                'opener_mode': tok.get('para_opener_mode', '?'),
                'thermal_bin': thermal_bin,
                'thermal_frac': thermal_frac,
            })

    print(f"  Records: {len(records)}")

    overall_dev_rate = sum(1 for r in records if r['deviates']) / len(records)
    print(f"  Overall deviation rate: {overall_dev_rate:.4f}")

    # --- Single-factor deviation rate reduction ---
    # For each factor, compute how well grouping by that factor reduces deviation variance
    factors = ['prefix_group', 'position_zone', 'opener_mode', 'thermal_bin']
    factor_results = {}

    for factor in factors:
        groups = defaultdict(list)
        for r in records:
            groups[r[factor]].append(r)

        # Weighted sum of squared deviation from group mean
        # (analogous to within-group SS / total SS)
        total_ss = sum((1 if r['deviates'] else 0 - overall_dev_rate) ** 2 for r in records)
        within_ss = 0.0
        group_info = {}
        for g, grp_records in groups.items():
            grp_dev_rate = sum(1 for r in grp_records if r['deviates']) / len(grp_records)
            within_ss += sum((1 if r['deviates'] else 0 - grp_dev_rate) ** 2
                             for r in grp_records)
            group_info[g] = {
                'n': len(grp_records),
                'deviation_rate': round(grp_dev_rate, 4),
            }

        variance_explained = 1.0 - (within_ss / total_ss) if total_ss > 0 else 0.0

        # Also compute MI(deviates; factor)
        dev_vals = [1 if r['deviates'] else 0 for r in records]
        factor_vals = [r[factor] for r in records]
        mi = mutual_information(dev_vals, factor_vals)

        factor_results[factor] = {
            'variance_explained': round(variance_explained, 4),
            'mi_bits': round(mi, 6),
            'groups': group_info,
        }
        print(f"  {factor}: var_explained={variance_explained:.4f}, MI={mi:.6f} bits")
        for g in sorted(group_info.keys()):
            gi = group_info[g]
            print(f"    {g}: n={gi['n']} dev_rate={gi['deviation_rate']}")

    # --- Combined model: PREFIX x position x opener ---
    combo_key = lambda r: (r['prefix_group'], r['position_zone'], r['opener_mode'])
    combo_groups = defaultdict(list)
    for r in records:
        combo_groups[combo_key(r)].append(r)

    combo_within_ss = 0.0
    total_ss = sum(((1 if r['deviates'] else 0) - overall_dev_rate) ** 2 for r in records)
    for key, grp in combo_groups.items():
        grp_rate = sum(1 for r in grp if r['deviates']) / len(grp)
        combo_within_ss += sum(((1 if r['deviates'] else 0) - grp_rate) ** 2
                               for r in grp)

    combined_var_explained = 1.0 - (combo_within_ss / total_ss) if total_ss > 0 else 0.0
    print(f"  Combined (PREFIX x position x opener): var_explained={combined_var_explained:.4f}")

    # --- Redundancy check: MI(PREFIX; opener_mode) ---
    prefix_vals = [r['prefix_group'] for r in records]
    opener_vals = [r['opener_mode'] for r in records]
    redundancy_mi = mutual_information(prefix_vals, opener_vals)
    print(f"  Redundancy MI(PREFIX; opener_mode): {redundancy_mi:.6f} bits")

    # --- Redundancy check: MI(PREFIX; thermal_bin) ---
    thermal_vals = [r['thermal_bin'] for r in records]
    redundancy_mi_thermal = mutual_information(prefix_vals, thermal_vals)
    print(f"  Redundancy MI(PREFIX; thermal_bin): {redundancy_mi_thermal:.6f} bits")

    # --- Verdict ---
    max_single = max(fr['variance_explained'] for fr in factor_results.values())
    dominant_factor = max(factor_results.items(), key=lambda x: x[1]['variance_explained'])[0]

    if max_single > 0.50:
        verdict = 'DOMINANT'
        verdict_detail = f'{dominant_factor} explains {max_single:.1%}'
    elif combined_var_explained > 0.50:
        verdict = 'DISTRIBUTED'
        verdict_detail = f'combined={combined_var_explained:.1%}, no single >{50}%'
    elif combined_var_explained > 0.30:
        verdict = 'PARTIAL'
        verdict_detail = f'combined={combined_var_explained:.1%}'
    else:
        verdict = 'INCONCLUSIVE'
        verdict_detail = f'combined={combined_var_explained:.1%}'

    print(f"  Verdict: {verdict} ({verdict_detail})")

    return {
        'test': 'T5_variance_decomposition',
        'verdict': verdict,
        'verdict_detail': verdict_detail,
        'n_records': len(records),
        'overall_deviation_rate': round(overall_dev_rate, 4),
        'single_factors': factor_results,
        'combined_variance_explained': round(combined_var_explained, 4),
        'n_combo_groups': len(combo_groups),
        'dominant_factor': dominant_factor,
        'max_single_var_explained': round(max_single, 4),
        'redundancy_prefix_opener_mi': round(redundancy_mi, 6),
        'redundancy_prefix_thermal_mi': round(redundancy_mi_thermal, 6),
    }


# ================================================================
# MAIN
# ================================================================

def main():
    t0 = time.time()
    rng = random.Random(SEED)
    print("Phase 470: SUFFIX_MODE_CONTEXT")
    print("=" * 60)

    # Load data from Phase 469
    print("\nLoading data via Phase 469 build_b_lines()...")
    classified_lines, all_tokens = build_b_lines()

    # Build context annotations
    flexible_tokens = build_context_data(classified_lines, all_tokens)

    if not flexible_tokens:
        print("ERROR: No flexible tokens found!")
        return

    # Run tests
    results = {}
    results['T1'] = test_t1(flexible_tokens, rng)
    results['T2'] = test_t2(flexible_tokens, classified_lines, rng)
    results['T3'] = test_t3(flexible_tokens, rng)
    results['T4'] = test_t4(flexible_tokens, classified_lines, rng)
    results['T5'] = test_t5(flexible_tokens, classified_lines)

    # Summary
    dt = time.time() - t0
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    verdicts = {}
    for key in ['T1', 'T2', 'T3', 'T4', 'T5']:
        v = results[key]['verdict']
        verdicts[key] = v
        print(f"  {key}: {v}")

    results['meta'] = {
        'phase': 470,
        'name': 'SUFFIX_MODE_CONTEXT',
        'n_classified_lines': len(classified_lines),
        'n_all_tokens': len(all_tokens),
        'n_flexible_tokens': len(flexible_tokens),
        'flex_threshold': FLEX_THRESHOLD,
        'min_freq': MIN_FREQ,
        'n_perm': N_PERM,
        'seed': SEED,
        'runtime_s': round(dt, 1),
        'verdicts': verdicts,
    }

    # Save
    out_path = RESULTS_DIR / "suffix_mode_context.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")
    print(f"Runtime: {dt:.1f}s")


if __name__ == '__main__':
    main()
