#!/usr/bin/env python3
"""
Phase 383: HT Interaction Architecture — 6-test battery

Tests 4 untested HTSC V9 cross-guarantee predictions + 1 open structural
question + 1 negative control.

T1: Boundary-position hazard distance (C217 x C803)
T2: Line-1 vs body section exclusivity (C167 x C747/C748 x C870)
T3: Tail MIDDLE x compound rate (C477 x C935)
T4: LINK-adjacent EARLY/LATE prefix ratio (C806 x C348)
T5: HT oscillation wavelength (open question)
T6: Paragraph ordinal neutrality (negative control, C861 x C1022)
"""

import sys
import csv
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats as sp_stats
from scipy.stats import mannwhitneyu, spearmanr, chi2_contingency

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

RESULTS = ROOT / "phases" / "HT_INTERACTION_ARCHITECTURE" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

# C109: 17 forbidden transitions
FORBIDDEN_TRANSITIONS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('dy', 'chey'), ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'), ('ar', 'dal'),
    ('c', 'ee'), ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o')
]

# Build bidirectional forbidden set
FORBIDDEN_SET = set()
for a, b in FORBIDDEN_TRANSITIONS:
    FORBIDDEN_SET.add((a, b))
    FORBIDDEN_SET.add((b, a))

# Forbidden participant words (either side)
FORBIDDEN_WORDS = set()
for a, b in FORBIDDEN_TRANSITIONS:
    FORBIDDEN_WORDS.add(a)
    FORBIDDEN_WORDS.add(b)

# C348: Phase synchrony prefixes
EARLY_PREFIXES = {'op', 'pc', 'do', 'qo', 'ok', 'ot'}
LATE_PREFIXES = {'ta', 'da', 'sa', 'so'}


def save_result(data, filename):
    """Save result JSON."""
    path = RESULTS / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else str(x))
    print(f"  Saved: {path.name}")


def cramers_v(table):
    """Cramér's V from contingency table."""
    chi2_val = chi2_contingency(table)[0]
    n = table.sum()
    r, c = table.shape
    return np.sqrt(chi2_val / (n * (min(r, c) - 1))) if n > 0 and min(r, c) > 1 else 0.0


def cohens_d(group1, group2):
    """Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    m1, m2 = np.mean(group1), np.mean(group2)
    s1, s2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
    pooled = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    return (m1 - m2) / pooled if pooled > 0 else 0.0


def load_data():
    """Load all shared data."""
    print("Loading data...")

    tx = Transcript()
    morph = Morphology()

    # Class map for HT identification
    ctm_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path) as f:
        ctm = json.load(f)
    token_to_class = ctm.get('token_to_class', ctm)

    # Paragraph inventory for T6
    par_path = ROOT / 'phases' / 'PARAGRAPH_INTERNAL_PROFILING' / 'results' / 'b_paragraph_inventory.json'
    with open(par_path) as f:
        par_inv = json.load(f)

    # MiddleAnalyzer for compound detection (T3)
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # Build line sequences from B tokens (for T1 hazard distance)
    b_tokens = list(tx.currier_b())
    print(f"  B tokens: {len(b_tokens)}")

    # Identify HT tokens
    ht_count = sum(1 for t in b_tokens if t.word not in token_to_class)
    print(f"  HT tokens in B: {ht_count}")

    # Build per-folio-line token sequences
    line_seqs = defaultdict(list)
    for t in b_tokens:
        line_seqs[(t.folio, t.line)].append(t)

    # Read quire info from transcript CSV (not in Token dataclass)
    folio_quire = {}
    with open(ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            fol = row.get('folio', '').strip().strip('"')
            quire = row.get('quire', '').strip().strip('"')
            if fol and quire:
                folio_quire[fol] = quire

    # PP MIDDLE identification (for T2 stratification)
    mc_path = ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json'
    pp_middles = set()
    if mc_path.exists():
        with open(mc_path) as f:
            mc = json.load(f)
        pp_middles = set(mc.get('a_shared_middles', []))

    return {
        'tx': tx,
        'morph': morph,
        'token_to_class': token_to_class,
        'par_inv': par_inv,
        'mid_analyzer': mid_analyzer,
        'b_tokens': b_tokens,
        'line_seqs': line_seqs,
        'folio_quire': folio_quire,
        'pp_middles': pp_middles,
    }


# ============================================================
# T1: Boundary-Position Hazard Distance
# ============================================================
def run_t1(data):
    """T1: Do boundary-position HT tokens show different hazard distances?"""
    print("\n" + "=" * 70)
    print("T1: Boundary-Position Hazard Distance")
    print("=" * 70)

    token_to_class = data['token_to_class']
    line_seqs = data['line_seqs']

    boundary_dists = []
    interior_dists = []

    for (folio, line), tokens in line_seqs.items():
        words = [t.word for t in tokens]
        n = len(words)
        if n < 2:
            continue

        for i, t in enumerate(tokens):
            if t.word in token_to_class:
                continue  # Not HT

            # Compute minimum distance to nearest forbidden partner
            min_dist = None
            for j, w2 in enumerate(words):
                if i == j:
                    continue
                if (t.word, w2) in FORBIDDEN_SET:
                    d = abs(i - j)
                    if min_dist is None or d < min_dist:
                        min_dist = d

            # If this word can't participate in any forbidden pair, distance = line length
            if min_dist is None:
                if t.word in FORBIDDEN_WORDS:
                    min_dist = n  # Can participate but no partner in this line
                else:
                    continue  # Word never participates in forbidden transitions, skip

            is_boundary = t.line_initial or t.line_final
            if is_boundary:
                boundary_dists.append(min_dist)
            else:
                interior_dists.append(min_dist)

    print(f"  Boundary HT tokens with forbidden potential: {len(boundary_dists)}")
    print(f"  Interior HT tokens with forbidden potential: {len(interior_dists)}")

    # Main test
    if len(boundary_dists) > 1 and len(interior_dists) > 1:
        U, p = mannwhitneyu(boundary_dists, interior_dists, alternative='two-sided')
        d = cohens_d(boundary_dists, interior_dists)
        verdict = "PASS" if p < 0.01 and abs(d) > 0.2 else ("PARTIAL" if p < 0.05 else "FAIL")
    else:
        U, p, d = 0, 1.0, 0.0
        verdict = "FAIL"

    print(f"  Boundary median: {np.median(boundary_dists):.1f}, Interior median: {np.median(interior_dists):.1f}")
    print(f"  Mann-Whitney p={p:.4f}, Cohen's d={d:.4f}")
    print(f"  Verdict: {verdict}")

    # Alternative approach: fraction of HT tokens adjacent to forbidden partner
    # (distance == 1) by position
    boundary_adj = sum(1 for d in boundary_dists if d == 1)
    interior_adj = sum(1 for d in interior_dists if d == 1)
    boundary_adj_rate = boundary_adj / len(boundary_dists) if boundary_dists else 0
    interior_adj_rate = interior_adj / len(interior_dists) if interior_dists else 0

    result = {
        'test': 'T1_boundary_hazard_distance',
        'verdict': verdict,
        'n_boundary_ht': len(boundary_dists),
        'n_interior_ht': len(interior_dists),
        'boundary_median': float(np.median(boundary_dists)) if boundary_dists else None,
        'interior_median': float(np.median(interior_dists)) if interior_dists else None,
        'boundary_mean': float(np.mean(boundary_dists)) if boundary_dists else None,
        'interior_mean': float(np.mean(interior_dists)) if interior_dists else None,
        'mann_whitney_U': float(U),
        'mann_whitney_p': float(p),
        'cohens_d': float(d),
        'boundary_adjacent_rate': float(boundary_adj_rate),
        'interior_adjacent_rate': float(interior_adj_rate),
        'notes': [
            "Distance = min token positions to nearest forbidden partner in same line",
            "Only HT tokens that participate in forbidden vocabulary are included",
            "Expert prediction: likely null — hazard avoidance is vocabulary-level (C622), not positional"
        ],
        'constraints_referenced': ['C217', 'C803', 'C166', 'C169', 'C622', 'C740']
    }
    save_result(result, 't1_boundary_hazard_distance.json')
    return result


# ============================================================
# T2: Line-1 vs Body Section Exclusivity
# ============================================================
def run_t2(data):
    """T2: Is section exclusivity different for line-1 vs body HT?"""
    print("\n" + "=" * 70)
    print("T2: Line-1 vs Body Section Exclusivity")
    print("=" * 70)

    token_to_class = data['token_to_class']
    morph = data['morph']
    b_tokens = data['b_tokens']
    pp_middles = data['pp_middles']

    # Collect HT MIDDLE types with their line and section info
    # Also track folio membership for singleton control
    middle_info = defaultdict(lambda: {
        'sections': set(),
        'folios': set(),
        'in_line1': False,
        'in_body': False,
        'is_pp': False,
        'count': 0,
    })

    for t in b_tokens:
        if t.word in token_to_class:
            continue  # Not HT

        m = morph.extract(t.word)
        if not m.middle:
            continue

        mid = m.middle
        info = middle_info[mid]
        info['sections'].add(t.section)
        info['folios'].add(t.folio)
        info['count'] += 1
        if t.line == '1':
            info['in_line1'] = True
        else:
            info['in_body'] = True
        if mid in pp_middles:
            info['is_pp'] = True

    # Classify MIDDLEs
    line1_only = []
    body_only = []
    both = []

    for mid, info in middle_info.items():
        is_exclusive = len(info['sections']) == 1
        is_singleton = len(info['folios']) == 1

        entry = {
            'middle': mid,
            'section_exclusive': is_exclusive,
            'folio_singleton': is_singleton,
            'n_sections': len(info['sections']),
            'n_folios': len(info['folios']),
            'is_pp': info['is_pp'],
        }

        if info['in_line1'] and not info['in_body']:
            line1_only.append(entry)
        elif info['in_body'] and not info['in_line1']:
            body_only.append(entry)
        else:
            both.append(entry)

    # Compute rates
    line1_excl = sum(1 for e in line1_only if e['section_exclusive'])
    body_excl = sum(1 for e in body_only if e['section_exclusive'])
    line1_rate = line1_excl / len(line1_only) if line1_only else 0
    body_rate = body_excl / len(body_only) if body_only else 0

    print(f"  Line-1-only MIDDLEs: {len(line1_only)}, section-exclusive: {line1_excl} ({line1_rate:.3f})")
    print(f"  Body-only MIDDLEs: {len(body_only)}, section-exclusive: {body_excl} ({body_rate:.3f})")
    print(f"  Both: {len(both)}")

    # Fisher exact test on 2x2 (line1/body × exclusive/non-exclusive)
    table = np.array([
        [line1_excl, len(line1_only) - line1_excl],
        [body_excl, len(body_only) - body_excl]
    ])
    if table.sum() > 0 and table.shape == (2, 2):
        odds_ratio, fisher_p = sp_stats.fisher_exact(table)
    else:
        odds_ratio, fisher_p = 1.0, 1.0

    print(f"  Fisher exact p={fisher_p:.4f}, OR={odds_ratio:.3f}")

    # SINGLETON CONTROL (expert trap)
    # Compare body folio-singletons vs line-1 folio-singletons
    line1_sing = [e for e in line1_only if e['folio_singleton']]
    body_sing = [e for e in body_only if e['folio_singleton']]
    line1_sing_excl = sum(1 for e in line1_sing if e['section_exclusive'])
    body_sing_excl = sum(1 for e in body_sing if e['section_exclusive'])
    line1_sing_rate = line1_sing_excl / len(line1_sing) if line1_sing else 0
    body_sing_rate = body_sing_excl / len(body_sing) if body_sing else 0

    print(f"\n  Singleton control:")
    print(f"    Line-1 singletons: {len(line1_sing)}, exclusive: {line1_sing_excl} ({line1_sing_rate:.3f})")
    print(f"    Body singletons: {len(body_sing)}, exclusive: {body_sing_excl} ({body_sing_rate:.3f})")

    # Fisher on singleton-controlled
    ctrl_table = np.array([
        [line1_sing_excl, len(line1_sing) - line1_sing_excl],
        [body_sing_excl, len(body_sing) - body_sing_excl]
    ])
    if ctrl_table.sum() > 0 and min(ctrl_table.shape) > 0 and all(ctrl_table.sum(axis=1) > 0):
        ctrl_or, ctrl_p = sp_stats.fisher_exact(ctrl_table)
    else:
        ctrl_or, ctrl_p = 1.0, 1.0

    print(f"    Controlled Fisher p={ctrl_p:.4f}, OR={ctrl_or:.3f}")

    # PP stratification within line-1
    line1_pp = [e for e in line1_only if e['is_pp']]
    line1_bexcl = [e for e in line1_only if not e['is_pp']]
    pp_excl_rate = sum(1 for e in line1_pp if e['section_exclusive']) / len(line1_pp) if line1_pp else 0
    bexcl_rate = sum(1 for e in line1_bexcl if e['section_exclusive']) / len(line1_bexcl) if line1_bexcl else 0

    print(f"\n  PP stratification (line-1 only):")
    print(f"    PP MIDDLEs: {len(line1_pp)}, exclusive rate: {pp_excl_rate:.3f}")
    print(f"    B-exclusive MIDDLEs: {len(line1_bexcl)}, exclusive rate: {bexcl_rate:.3f}")

    # Verdict
    if fisher_p < 0.01 and ctrl_p < 0.01:
        verdict = "PASS"
    elif fisher_p < 0.01 and ctrl_p >= 0.01:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"  Verdict: {verdict}")

    result = {
        'test': 'T2_line1_section_exclusivity',
        'verdict': verdict,
        'n_line1_only': len(line1_only),
        'n_body_only': len(body_only),
        'n_both': len(both),
        'line1_exclusivity_rate': float(line1_rate),
        'body_exclusivity_rate': float(body_rate),
        'fisher_p': float(fisher_p),
        'odds_ratio': float(odds_ratio),
        'singleton_control': {
            'n_line1_singletons': len(line1_sing),
            'n_body_singletons': len(body_sing),
            'line1_singleton_excl_rate': float(line1_sing_rate),
            'body_singleton_excl_rate': float(body_sing_rate),
            'controlled_fisher_p': float(ctrl_p),
            'controlled_odds_ratio': float(ctrl_or),
        },
        'pp_stratification': {
            'n_line1_pp': len(line1_pp),
            'n_line1_b_exclusive': len(line1_bexcl),
            'pp_exclusivity_rate': float(pp_excl_rate),
            'b_exclusive_rate': float(bexcl_rate),
        },
        'tautology_note': 'If controlled rate matches, effect is entirely explained by folio-specificity (C870)',
        'constraints_referenced': ['C167', 'C747', 'C748', 'C870', 'C794', 'C795']
    }
    save_result(result, 't2_line1_section_exclusivity.json')
    return result


# ============================================================
# T3: Tail MIDDLE x Compound Rate
# ============================================================
def run_t3(data):
    """T3: Do folios with more tail MIDDLEs have different HT compound rates?"""
    print("\n" + "=" * 70)
    print("T3: Tail MIDDLE x Compound Rate")
    print("=" * 70)

    token_to_class = data['token_to_class']
    morph = data['morph']
    b_tokens = data['b_tokens']
    mid_analyzer = data['mid_analyzer']

    # Step 1: Compute global MIDDLE frequency for tail detection
    middle_counts = Counter()
    for t in b_tokens:
        m = morph.extract(t.word)
        if m.middle:
            middle_counts[m.middle] += 1

    # Bottom 50% by frequency = tail
    sorted_mids = sorted(middle_counts.items(), key=lambda x: x[1])
    cutoff = len(sorted_mids) // 2
    tail_middles = set(m for m, _ in sorted_mids[:cutoff])
    print(f"  Total MIDDLE types: {len(middle_counts)}, tail (bottom 50%): {len(tail_middles)}")

    # Step 2: Per-folio metrics
    folio_data = defaultdict(lambda: {
        'total_middles': 0,
        'tail_middles': 0,
        'ht_tokens': 0,
        'ht_compound': 0,
    })

    for t in b_tokens:
        m = morph.extract(t.word)
        if not m.middle:
            continue

        fd = folio_data[t.folio]
        fd['total_middles'] += 1

        if m.middle in tail_middles:
            fd['tail_middles'] += 1

        if t.word not in token_to_class:  # HT token
            fd['ht_tokens'] += 1
            if mid_analyzer.is_compound(m.middle):
                fd['ht_compound'] += 1

    # Compute rates per folio (only folios with >= 3 HT tokens)
    folios = []
    tail_pressures = []
    compound_rates = []
    ht_counts = []

    for folio, fd in sorted(folio_data.items()):
        if fd['ht_tokens'] < 3:
            continue
        tp = fd['tail_middles'] / fd['total_middles'] if fd['total_middles'] > 0 else 0
        cr = fd['ht_compound'] / fd['ht_tokens']

        folios.append(folio)
        tail_pressures.append(tp)
        compound_rates.append(cr)
        ht_counts.append(fd['ht_tokens'])

    print(f"  Folios with >=3 HT tokens: {len(folios)}")
    print(f"  Mean tail pressure: {np.mean(tail_pressures):.3f}")
    print(f"  Mean HT compound rate: {np.mean(compound_rates):.3f}")

    # Step 3: Correlation
    rho, p = spearmanr(tail_pressures, compound_rates)
    print(f"  Spearman rho={rho:.4f}, p={p:.4f}")

    # Pre-registered direction check
    if rho < 0 and p < 0.05:
        direction = "INVERSE (two-axis model supported)"
    elif rho > 0 and p < 0.05:
        direction = "POSITIVE (specification model supported)"
    else:
        direction = "NULL (independent)"

    print(f"  Direction: {direction}")

    # Partial correlation controlling for HT count
    from scipy.stats import pearsonr
    # Rank-based partial correlation
    r_tp = np.argsort(np.argsort(tail_pressures))
    r_cr = np.argsort(np.argsort(compound_rates))
    r_hc = np.argsort(np.argsort(ht_counts))

    # Residualize tp and cr on ht_count
    slope1, intercept1 = np.polyfit(r_hc, r_tp, 1)
    res_tp = r_tp - (slope1 * r_hc + intercept1)
    slope2, intercept2 = np.polyfit(r_hc, r_cr, 1)
    res_cr = r_cr - (slope2 * r_hc + intercept2)

    partial_rho, partial_p = pearsonr(res_tp, res_cr)
    print(f"  Partial rho (ctrl HT count): {partial_rho:.4f}, p={partial_p:.4f}")

    # Verdict
    if abs(rho) > 0.3 and p < 0.01:
        verdict = "PASS"
    elif p < 0.05:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"  Verdict: {verdict}")

    result = {
        'test': 'T3_tail_compound_correlation',
        'verdict': verdict,
        'n_folios': len(folios),
        'n_tail_middles': len(tail_middles),
        'mean_tail_pressure': float(np.mean(tail_pressures)),
        'mean_compound_rate': float(np.mean(compound_rates)),
        'spearman_rho': float(rho),
        'spearman_p': float(p),
        'partial_rho': float(partial_rho),
        'partial_p': float(partial_p),
        'direction': direction,
        'pre_registered': {
            'inverse': 'two-axis model (high tail → simple HT)',
            'positive': 'specification model (compound = specification density)',
            'null': 'independent systems',
        },
        'constraints_referenced': ['C477', 'C935', 'C766', 'C610', 'C461']
    }
    save_result(result, 't3_tail_compound_correlation.json')
    return result


# ============================================================
# T4: LINK-Adjacent EARLY/LATE Prefix Ratio
# ============================================================
def run_t4(data):
    """T4: Do LINK-adjacent HT tokens show different EARLY/LATE prefix ratios?"""
    print("\n" + "=" * 70)
    print("T4: LINK-Adjacent EARLY/LATE Prefix Ratio")
    print("=" * 70)

    token_to_class = data['token_to_class']
    morph = data['morph']
    line_seqs = data['line_seqs']

    # Collect HT tokens with prefix phase classification
    # Track LINK adjacency and normalized line position
    link_adj_ht = []     # (prefix_phase, norm_pos)
    non_link_adj_ht = [] # (prefix_phase, norm_pos)

    for (folio, line), tokens in line_seqs.items():
        n = len(tokens)
        if n < 2:
            continue

        # Find LINK positions
        link_positions = set()
        for i, t in enumerate(tokens):
            if 'ol' in t.word:
                link_positions.add(i)

        for i, t in enumerate(tokens):
            if t.word in token_to_class:
                continue  # Not HT

            m = morph.extract(t.word)
            if not m.prefix:
                continue

            # Classify prefix phase
            if m.prefix in EARLY_PREFIXES:
                phase = 'EARLY'
            elif m.prefix in LATE_PREFIXES:
                phase = 'LATE'
            else:
                continue  # Only count EARLY/LATE

            norm_pos = i / (n - 1) if n > 1 else 0.5
            is_link_adj = any(abs(i - lp) == 1 for lp in link_positions)

            if is_link_adj:
                link_adj_ht.append((phase, norm_pos))
            else:
                non_link_adj_ht.append((phase, norm_pos))

    print(f"  LINK-adjacent HT with EARLY/LATE prefix: {len(link_adj_ht)}")
    print(f"  Non-adjacent HT with EARLY/LATE prefix: {len(non_link_adj_ht)}")

    # Uncontrolled comparison
    adj_early = sum(1 for p, _ in link_adj_ht if p == 'EARLY')
    adj_late = sum(1 for p, _ in link_adj_ht if p == 'LATE')
    non_early = sum(1 for p, _ in non_link_adj_ht if p == 'EARLY')
    non_late = sum(1 for p, _ in non_link_adj_ht if p == 'LATE')

    print(f"  Adjacent: EARLY={adj_early}, LATE={adj_late}")
    print(f"  Non-adjacent: EARLY={non_early}, LATE={non_late}")

    table_raw = np.array([[adj_early, adj_late], [non_early, non_late]])
    if table_raw.sum() > 0 and all(table_raw.sum(axis=1) > 0) and all(table_raw.sum(axis=0) > 0):
        chi2, p_raw, _, _ = chi2_contingency(table_raw, correction=True)
        v_raw = cramers_v(table_raw)
        or_raw, fisher_p_raw = sp_stats.fisher_exact(table_raw)
    else:
        chi2, p_raw, v_raw = 0, 1.0, 0.0
        or_raw, fisher_p_raw = 1.0, 1.0

    print(f"  Uncontrolled: chi2={chi2:.2f}, p={p_raw:.4f}, V={v_raw:.4f}, OR={or_raw:.3f}")

    # POSITIONAL CONTROL: match by decile
    # Bin all HT tokens by position decile, compare EARLY/LATE within same deciles
    adj_by_decile = defaultdict(lambda: {'EARLY': 0, 'LATE': 0})
    non_by_decile = defaultdict(lambda: {'EARLY': 0, 'LATE': 0})

    for phase, pos in link_adj_ht:
        decile = min(int(pos * 10), 9)
        adj_by_decile[decile][phase] += 1

    for phase, pos in non_link_adj_ht:
        decile = min(int(pos * 10), 9)
        non_by_decile[decile][phase] += 1

    # Position-matched comparison: for each decile, compute EARLY fraction
    ctrl_adj_early = 0
    ctrl_adj_total = 0
    ctrl_non_early = 0
    ctrl_non_total = 0

    for dec in range(10):
        a = adj_by_decile[dec]
        n = non_by_decile[dec]
        a_tot = a['EARLY'] + a['LATE']
        n_tot = n['EARLY'] + n['LATE']
        if a_tot > 0 and n_tot > 0:
            ctrl_adj_early += a['EARLY']
            ctrl_adj_total += a_tot
            ctrl_non_early += n['EARLY']
            ctrl_non_total += n_tot

    ctrl_table = np.array([
        [ctrl_adj_early, ctrl_adj_total - ctrl_adj_early],
        [ctrl_non_early, ctrl_non_total - ctrl_non_early]
    ])
    if ctrl_table.sum() > 0 and all(ctrl_table.sum(axis=1) > 0) and all(ctrl_table.sum(axis=0) > 0):
        chi2_ctrl, p_ctrl, _, _ = chi2_contingency(ctrl_table, correction=True)
        v_ctrl = cramers_v(ctrl_table)
        or_ctrl, fisher_p_ctrl = sp_stats.fisher_exact(ctrl_table)
    else:
        chi2_ctrl, p_ctrl, v_ctrl = 0, 1.0, 0.0
        or_ctrl, fisher_p_ctrl = 1.0, 1.0

    print(f"  Position-controlled: chi2={chi2_ctrl:.2f}, p={p_ctrl:.4f}, V={v_ctrl:.4f}, OR={or_ctrl:.3f}")

    # Verdict
    if p_ctrl < 0.01 and v_ctrl > 0.1:
        verdict = "PASS"
    elif p_raw < 0.01 and p_ctrl >= 0.01:
        verdict = "PARTIAL"
    elif p_raw < 0.05:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"  Verdict: {verdict}")

    result = {
        'test': 'T4_link_prefix_phase',
        'verdict': verdict,
        'n_link_adjacent_ht': len(link_adj_ht),
        'n_non_adjacent_ht': len(non_link_adj_ht),
        'uncontrolled': {
            'adj_early': int(adj_early),
            'adj_late': int(adj_late),
            'non_early': int(non_early),
            'non_late': int(non_late),
            'chi2': float(chi2),
            'p': float(p_raw),
            'cramers_v': float(v_raw),
            'odds_ratio': float(or_raw),
            'fisher_p': float(fisher_p_raw),
        },
        'position_controlled': {
            'chi2': float(chi2_ctrl),
            'p': float(p_ctrl),
            'cramers_v': float(v_ctrl),
            'odds_ratio': float(or_ctrl),
            'fisher_p': float(fisher_p_ctrl),
        },
        'notes': [
            "C804: LINK predecessor bias NS (p=0.41), successor bias weak (~1.1x)",
            "Position control matches by decile of normalized line position"
        ],
        'constraints_referenced': ['C806', 'C348', 'C804', 'C805', 'C609', 'C876']
    }
    save_result(result, 't4_link_prefix_phase.json')
    return result


# ============================================================
# T5: HT Oscillation Wavelength
# ============================================================
def run_t5(data):
    """T5: What drives ~10-folio HT oscillation?"""
    print("\n" + "=" * 70)
    print("T5: HT Oscillation Wavelength")
    print("=" * 70)

    token_to_class = data['token_to_class']
    b_tokens = data['b_tokens']
    folio_quire = data['folio_quire']

    # Per-folio HT density, preserving physical order
    folio_stats = defaultdict(lambda: {'total': 0, 'ht': 0, 'section': None, 'quire': None})
    folio_order = []
    seen_folios = set()

    for t in b_tokens:
        fd = folio_stats[t.folio]
        fd['total'] += 1
        if t.word not in token_to_class:
            fd['ht'] += 1
        if fd['section'] is None:
            fd['section'] = t.section
        if t.folio not in seen_folios:
            folio_order.append(t.folio)
            seen_folios.add(t.folio)
            fd['quire'] = folio_quire.get(t.folio, '?')

    # Compute density series
    densities = []
    sections = []
    quires = []
    folio_names = []

    for fol in folio_order:
        fd = folio_stats[fol]
        if fd['total'] > 0:
            densities.append(fd['ht'] / fd['total'])
            sections.append(fd['section'])
            quires.append(fd['quire'])
            folio_names.append(fol)

    n_folios = len(densities)
    print(f"  B folios: {n_folios}")
    print(f"  Mean HT density: {np.mean(densities):.4f}")
    print(f"  Std HT density: {np.std(densities):.4f}")

    # Autocorrelation function
    max_lag = min(20, n_folios // 3)
    density_arr = np.array(densities)
    density_centered = density_arr - density_arr.mean()
    var = np.var(density_arr)

    acf = []
    for lag in range(1, max_lag + 1):
        if var > 0:
            c = np.mean(density_centered[:-lag] * density_centered[lag:])
            acf.append(c / var)
        else:
            acf.append(0.0)

    # Significance threshold (approximate 95% CI for white noise)
    sig_threshold = 1.96 / np.sqrt(n_folios)
    significant_lags = [lag + 1 for lag, r in enumerate(acf) if abs(r) > sig_threshold]

    print(f"  ACF significance threshold: {sig_threshold:.4f}")
    print(f"  Significant lags: {significant_lags}")
    if acf:
        peak_lag = np.argmax(np.abs(acf)) + 1
        peak_acf = acf[peak_lag - 1]
        print(f"  Peak ACF: lag={peak_lag}, r={peak_acf:.4f}")

    # Section boundary analysis
    section_changes = []
    for i in range(1, len(sections)):
        if sections[i] != sections[i - 1]:
            section_changes.append(i)

    # Quire boundary analysis
    quire_changes = []
    for i in range(1, len(quires)):
        if quires[i] != quires[i - 1]:
            quire_changes.append(i)

    print(f"  Section boundaries: {len(section_changes)} at positions {section_changes}")
    print(f"  Quire boundaries: {len(quire_changes)} at positions {quire_changes}")

    # Section-residualized ACF: remove section means
    section_means = {}
    for sec in set(sections):
        sec_densities = [d for d, s in zip(densities, sections) if s == sec]
        section_means[sec] = np.mean(sec_densities) if sec_densities else 0

    residuals = np.array([d - section_means[s] for d, s in zip(densities, sections)])
    res_var = np.var(residuals)

    acf_residual = []
    for lag in range(1, max_lag + 1):
        if res_var > 0:
            c = np.mean(residuals[:-lag] * residuals[lag:])
            acf_residual.append(c / res_var)
        else:
            acf_residual.append(0.0)

    sig_lags_residual = [lag + 1 for lag, r in enumerate(acf_residual) if abs(r) > sig_threshold]
    print(f"\n  After section-residualization:")
    print(f"  Significant lags: {sig_lags_residual}")

    # Ljung-Box test on raw density series
    try:
        from statsmodels.stats.diagnostic import acorr_ljungbox
        lb_result = acorr_ljungbox(density_arr, lags=max_lag, return_df=True)
        lb_p_min = lb_result['lb_pvalue'].min()
        lb_lag_min = lb_result['lb_pvalue'].idxmin()
        print(f"  Ljung-Box: min p={lb_p_min:.4f} at lag {lb_lag_min}")
    except ImportError:
        lb_p_min = None
        lb_lag_min = None
        print("  Ljung-Box: statsmodels not available, skipping")

    # Verdict
    has_raw_signal = len(significant_lags) > 0
    has_residual_signal = len(sig_lags_residual) > 0
    has_target_range = any(8 <= lag <= 12 for lag in sig_lags_residual)

    if has_target_range:
        verdict = "PASS"
    elif has_residual_signal:
        verdict = "PARTIAL"
    elif has_raw_signal and not has_residual_signal:
        verdict = "PARTIAL"  # Section-explained
    else:
        verdict = "FAIL"

    print(f"  Verdict: {verdict}")

    result = {
        'test': 'T5_ht_oscillation_wavelength',
        'verdict': verdict,
        'n_folios': n_folios,
        'mean_density': float(np.mean(densities)),
        'std_density': float(np.std(densities)),
        'acf_raw': {f'lag_{i+1}': float(acf[i]) for i in range(len(acf))},
        'acf_residual': {f'lag_{i+1}': float(acf_residual[i]) for i in range(len(acf_residual))},
        'sig_threshold': float(sig_threshold),
        'significant_lags_raw': significant_lags,
        'significant_lags_residual': sig_lags_residual,
        'section_boundaries': section_changes,
        'quire_boundaries': quire_changes,
        'n_sections': len(set(sections)),
        'n_quires': len(set(quires)),
        'ljung_box_min_p': float(lb_p_min) if lb_p_min is not None else None,
        'ljung_box_min_lag': int(lb_lag_min) if lb_lag_min is not None else None,
        'notes': [
            "ACF computed on B folios in physical order",
            "Section-residualized ACF removes section-mean HT density",
            "Target range: lag 8-12 (the reported ~10-folio oscillation)",
        ],
        'constraints_referenced': ['C450', 'C459', 'C746', 'C156', 'C367', 'C451']
    }
    save_result(result, 't5_ht_oscillation_wavelength.json')
    return result


# ============================================================
# T6: Paragraph Ordinal Neutrality (Negative Control)
# ============================================================
def run_t6(data):
    """T6: Is HT density independent of paragraph ordinal?"""
    print("\n" + "=" * 70)
    print("T6: Paragraph Ordinal Neutrality (Negative Control)")
    print("=" * 70)

    token_to_class = data['token_to_class']
    b_tokens = data['b_tokens']
    par_inv = data['par_inv']

    # Build paragraph-to-tokens mapping
    # Use par_initial/par_final to detect paragraph boundaries
    par_list = par_inv['paragraphs']

    # Map (folio, line) to paragraph_ordinal
    line_to_par = {}
    for par in par_list:
        for ln in par['lines']:
            line_to_par[(par['folio'], ln)] = par['paragraph_ordinal']

    # Per-paragraph HT density
    par_data = defaultdict(lambda: {'total': 0, 'ht': 0, 'folio': None})

    for t in b_tokens:
        key = (t.folio, t.line)
        par_ord = line_to_par.get(key)
        if par_ord is None:
            continue

        par_key = (t.folio, par_ord)
        pd = par_data[par_key]
        pd['total'] += 1
        pd['folio'] = t.folio
        if t.word not in token_to_class:
            pd['ht'] += 1

    # Compute densities
    ordinals = []
    ht_densities = []
    folio_par_counts = Counter()

    for (folio, ordinal), pd in par_data.items():
        if pd['total'] < 5:
            continue
        ordinals.append(ordinal)
        ht_densities.append(pd['ht'] / pd['total'])
        folio_par_counts[folio] += 1

    print(f"  Paragraphs with >=5 tokens: {len(ordinals)}")
    print(f"  Mean HT density: {np.mean(ht_densities):.4f}")

    # Spearman correlation
    rho, p_rho = spearmanr(ordinals, ht_densities)
    print(f"  Spearman rho={rho:.4f}, p={p_rho:.4f}")

    # First vs last paragraph comparison
    first_densities = []
    last_densities = []

    # Group by folio
    folio_pars = defaultdict(list)
    for (folio, ordinal), pd in par_data.items():
        if pd['total'] >= 5:
            folio_pars[folio].append((ordinal, pd['ht'] / pd['total']))

    for folio, pars in folio_pars.items():
        if len(pars) < 2:
            continue
        pars.sort()
        first_densities.append(pars[0][1])
        last_densities.append(pars[-1][1])

    if first_densities and last_densities:
        U, p_mw = mannwhitneyu(first_densities, last_densities, alternative='two-sided')
        d_fl = cohens_d(first_densities, last_densities)
    else:
        U, p_mw, d_fl = 0, 1.0, 0.0

    print(f"  First vs last paragraph: MW p={p_mw:.4f}, Cohen's d={d_fl:.4f}")
    print(f"    First mean: {np.mean(first_densities):.4f}, Last mean: {np.mean(last_densities):.4f}")

    # Stratify by folio paragraph count
    strat = {}
    for n_pars in [2, 3]:
        target_folios = [f for f, c in folio_par_counts.items() if c == n_pars]
        sub_ords = []
        sub_dens = []
        for (folio, ordinal), pd in par_data.items():
            if folio in target_folios and pd['total'] >= 5:
                sub_ords.append(ordinal)
                sub_dens.append(pd['ht'] / pd['total'])
        if len(sub_ords) > 3:
            r, p = spearmanr(sub_ords, sub_dens)
            strat[f'{n_pars}_par_folios'] = {'n': len(sub_ords), 'rho': float(r), 'p': float(p)}
            print(f"  {n_pars}-paragraph folios: n={len(sub_ords)}, rho={r:.4f}, p={p:.4f}")

    # 4+ grouped
    target_folios = [f for f, c in folio_par_counts.items() if c >= 4]
    sub_ords = []
    sub_dens = []
    for (folio, ordinal), pd in par_data.items():
        if folio in target_folios and pd['total'] >= 5:
            sub_ords.append(ordinal)
            sub_dens.append(pd['ht'] / pd['total'])
    if len(sub_ords) > 3:
        r, p = spearmanr(sub_ords, sub_dens)
        strat['4plus_par_folios'] = {'n': len(sub_ords), 'rho': float(r), 'p': float(p)}
        print(f"  4+-paragraph folios: n={len(sub_ords)}, rho={r:.4f}, p={p:.4f}")

    # Verdict (negative control: PASS = null confirmed)
    if p_rho >= 0.05 and p_mw >= 0.05:
        verdict = "PASS"
    elif p_rho < 0.01 or p_mw < 0.01:
        verdict = "FAIL"
    else:
        verdict = "PARTIAL"

    print(f"  Verdict: {verdict} (negative control: PASS = no ordinal effect)")

    result = {
        'test': 'T6_paragraph_ordinal_neutrality',
        'verdict': verdict,
        'is_negative_control': True,
        'n_paragraphs': len(ordinals),
        'spearman_rho': float(rho),
        'spearman_p': float(p_rho),
        'first_vs_last': {
            'n_folios': len(first_densities),
            'first_mean': float(np.mean(first_densities)) if first_densities else None,
            'last_mean': float(np.mean(last_densities)) if last_densities else None,
            'mann_whitney_p': float(p_mw),
            'cohens_d': float(d_fl),
        },
        'stratified': strat,
        'expected': 'NULL — HT should be paragraph-ordinal neutral (PSC PARALLEL_PROGRAMS)',
        'constraints_referenced': ['C861', 'C1022', 'C855']
    }
    save_result(result, 't6_paragraph_ordinal_neutrality.json')
    return result


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 70)
    print("Phase 383: HT Interaction Architecture")
    print("6-test battery: 4 HTSC V9 predictions + 1 open question + 1 negative control")
    print("=" * 70)

    data = load_data()

    t1 = run_t1(data)
    t2 = run_t2(data)
    t3 = run_t3(data)
    t4 = run_t4(data)
    t5 = run_t5(data)
    t6 = run_t6(data)

    # Summary
    summary = {
        'phase': 383,
        'name': 'HT_INTERACTION_ARCHITECTURE',
        'description': '6-test battery: HTSC V9 cross-guarantee predictions, HT oscillation, paragraph ordinal neutrality',
        'tier': 2,
        'tests': [
            {'id': 'T1', 'name': 'Boundary Hazard Distance', 'verdict': t1['verdict']},
            {'id': 'T2', 'name': 'Line-1 Section Exclusivity', 'verdict': t2['verdict']},
            {'id': 'T3', 'name': 'Tail x Compound Correlation', 'verdict': t3['verdict']},
            {'id': 'T4', 'name': 'LINK Prefix Phase', 'verdict': t4['verdict']},
            {'id': 'T5', 'name': 'HT Oscillation Wavelength', 'verdict': t5['verdict']},
            {'id': 'T6', 'name': 'Paragraph Ordinal Neutrality', 'verdict': t6['verdict'],
             'note': 'negative control'},
        ],
        'constraints_referenced': sorted(set(
            t1.get('constraints_referenced', []) +
            t2.get('constraints_referenced', []) +
            t3.get('constraints_referenced', []) +
            t4.get('constraints_referenced', []) +
            t5.get('constraints_referenced', []) +
            t6.get('constraints_referenced', [])
        ))
    }
    save_result(summary, 'ht_interaction_summary.json')

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for t in summary['tests']:
        note = f" ({t['note']})" if 'note' in t else ""
        print(f"  {t['id']}: {t['name']} — {t['verdict']}{note}")


if __name__ == '__main__':
    main()
