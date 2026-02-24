"""
Phase 444: EN_CROSS_LANE_PAIRING
==================================
Decomposes the C1242 cross-lane MI signal (1.0632 bits, z=13.42) into
specific QO-CHSH MIDDLE pairings.

Tests:
  T1:  Pair enrichment/depletion matrix (Fisher exact, Bonferroni)
  T2:  Pair selectivity gradient (Shannon entropy ranking)
  T3:  E-depth correlation across lanes (Spearman)
  T4:  I-atom independence control (Spearman, expected NULL per C1205)
  T5:  Section/REGIME conditioning of top pairs
  T6:  Mode A vs Mode B pair profiles

Constraints:
  C1242 (cross-lane MI), C1243 (sh/ch routing), C1244 (aiin/ain wind-down)
  C911 (PREFIX selectivity), C660 (selectivity spectrum)
  C1225 (e-depth parametricity), C1226 (ke/ek ordering)
  C1205 (i orthogonal to k/e), C1204 (i-extension gradient)
  C1229-C1231 (suffix modes), C821 (line syntax REGIME-invariant)
  F-B-007 (extensible atom scaling)
"""
import json
import math
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = ROOT / "phases" / "EN_CROSS_LANE_PAIRING" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
REGIME_PATH = ROOT / "data" / "regime_folio_mapping.json"

N_SHUFFLES = 1000

# Lane classification (canonical, same as Phase 443)
QO_PREFIXES = {'qo', 'ok', 'ot', 'o', 'ko', 'to', 'po'}
CHSH_PREFIXES = {'ch', 'sh', 'lsh'}

# Suffix mode classification (from Phase 439 / C1229)
TERMINAL_SUFFIXES = {'y', 'dy', 'am', 'edy', 'ey', 'ly', 'ry', 'hy', 'eey', 'om', 'im'}
CONNECTOR_SUFFIXES = {'in', 'r', 'l', 's', 'an', 'en', 'on'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'iin', 'oiin'}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def classify_lane(prefix):
    """Classify prefix into QO, CHSH, or OTHER."""
    if prefix in QO_PREFIXES:
        return 'QO'
    elif prefix in CHSH_PREFIXES:
        return 'CHSH'
    return 'OTHER'


def e_depth(middle):
    """Count e-atoms in a MIDDLE (C1225 methodology)."""
    if not middle:
        return 0
    return sum(1 for ch in middle if ch == 'e')


def k_count(middle):
    """Count k-atoms in a MIDDLE."""
    if not middle:
        return 0
    return sum(1 for ch in middle if ch == 'k')


def i_count(middle):
    """Count i-atoms in a MIDDLE (C1205: expected orthogonal to k/e)."""
    if not middle:
        return 0
    return sum(1 for ch in middle if ch == 'i')


def classify_suffix(suffix):
    """Classify suffix into TERMINAL/CONNECTOR/ITERATE/BARE (C1229)."""
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
    """Compute suffix category fractions from list of suffixes."""
    if not suffixes:
        return [0.0, 0.0, 0.0, 1.0]  # [terminal, connector, iterate, bare]
    cats = [classify_suffix(s) for s in suffixes]
    n = len(cats)
    return [
        sum(1 for c in cats if c == 'TERMINAL') / n,
        sum(1 for c in cats if c == 'CONNECTOR') / n,
        sum(1 for c in cats if c == 'ITERATE') / n,
        sum(1 for c in cats if c == 'BARE') / n,
    ]


# ============================================================
# STATISTICAL FUNCTIONS
# ============================================================

def mutual_info(contingency):
    """Compute MI in bits from Counter with (row, col) keys."""
    n = sum(contingency.values())
    if n == 0:
        return 0.0
    rows = set(r for r, c in contingency)
    cols = set(c for r, c in contingency)
    row_totals = {r: sum(contingency.get((r, c), 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency.get((r, c), 0) for r in rows) for c in cols}
    mi = 0.0
    for r in rows:
        for c in cols:
            obs = contingency.get((r, c), 0)
            if obs == 0:
                continue
            p_rc = obs / n
            p_r = row_totals[r] / n
            p_c = col_totals[c] / n
            if p_r > 0 and p_c > 0:
                mi += p_rc * math.log2(p_rc / (p_r * p_c))
    return mi


def shannon_entropy(counts):
    """Shannon entropy in bits from a Counter or dict of counts."""
    n = sum(counts.values())
    if n == 0:
        return 0.0
    h = 0.0
    for v in counts.values():
        if v > 0:
            p = v / n
            h -= p * math.log2(p)
    return h


def enrichment_table(contingency, min_expected=5):
    """Compute obs/expected ratios and Fisher exact test per cell.

    Returns list of dicts sorted by ratio descending.
    """
    rows = sorted(set(r for r, c in contingency))
    cols = sorted(set(c for r, c in contingency))
    n = sum(contingency.values())
    if n == 0:
        return []
    row_totals = {r: sum(contingency.get((r, c), 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency.get((r, c), 0) for r in rows) for c in cols}

    cells = []
    for r in rows:
        for c in cols:
            obs = contingency.get((r, c), 0)
            exp = row_totals[r] * col_totals[c] / n
            if exp < min_expected:
                continue
            # Fisher exact on 2x2 table
            a = obs
            b = row_totals[r] - obs
            c_val = col_totals[c] - obs
            d = n - row_totals[r] - col_totals[c] + obs
            try:
                odds_ratio, p_val = sp_stats.fisher_exact([[a, b], [c_val, d]])
            except ValueError:
                odds_ratio, p_val = 1.0, 1.0
            cells.append({
                'qo_middle': r,
                'chsh_middle': c,
                'obs': obs,
                'exp': round(exp, 1),
                'ratio': round(obs / exp, 3) if exp > 0 else 0,
                'odds_ratio': round(odds_ratio, 3),
                'p_raw': p_val,
            })
    return cells


# ============================================================
# DATA LOADING
# ============================================================

def load_regime_map():
    """Load folio -> regime mapping."""
    with open(REGIME_PATH, encoding='utf-8') as f:
        raw = json.load(f)
    assignments = raw.get('regime_assignments', raw)
    return {k: v.get('regime', 'UNK') if isinstance(v, dict) else v
            for k, v in assignments.items()}


def load_cross_lane_data():
    """Load EN-lane tokens grouped by line, extract cross-lane pairs.

    Returns:
        pairs: list of pair dicts with atom counts pre-computed
        sequences: list of line token lists (for mode classification)
        metadata: counts dict
    """
    tx = Transcript()
    morph = Morphology()
    regime_map = load_regime_map()

    line_groups = defaultdict(list)
    n_total = 0
    n_en = 0

    for t in tx.currier_b():
        w = t.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if not m.middle or m.middle == '_EMPTY_':
            continue
        n_total += 1
        pfx = m.prefix or ''
        lane = classify_lane(pfx)

        if lane in ('QO', 'CHSH'):
            n_en += 1
            line_groups[(t.folio, t.line)].append({
                'word': w,
                'middle': m.middle,
                'suffix': m.suffix or '',
                'prefix': pfx,
                'lane': lane,
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
            })

    # Build sequences (lines with >= 2 EN tokens)
    sequences = []
    for k in sorted(line_groups.keys()):
        if len(line_groups[k]) >= 2:
            sequences.append(line_groups[k])

    # Extract cross-lane pairs (normalized to QO, CHSH order)
    pairs = []
    for seq in sequences:
        for i in range(len(seq) - 1):
            t1, t2 = seq[i], seq[i + 1]
            if t1['lane'] == t2['lane']:
                continue  # same lane, skip
            if t1['lane'] == 'QO':
                qo_tok, chsh_tok = t1, t2
            else:
                qo_tok, chsh_tok = t2, t1
            pairs.append({
                'qo_middle': qo_tok['middle'],
                'chsh_middle': chsh_tok['middle'],
                'qo_suffix': qo_tok['suffix'],
                'chsh_suffix': chsh_tok['suffix'],
                'qo_prefix': qo_tok['prefix'],
                'chsh_prefix': chsh_tok['prefix'],
                'qo_e': e_depth(qo_tok['middle']),
                'chsh_e': e_depth(chsh_tok['middle']),
                'qo_k': k_count(qo_tok['middle']),
                'chsh_k': k_count(chsh_tok['middle']),
                'qo_i': i_count(qo_tok['middle']),
                'chsh_i': i_count(chsh_tok['middle']),
                'folio': qo_tok['folio'],
                'line': qo_tok['line'],
                'section': qo_tok['section'],
                'regime': regime_map.get(qo_tok['folio'], 'UNK'),
            })

    # Also collect ALL tokens per line for mode classification
    all_line_tokens = defaultdict(list)
    for t in tx.currier_b():
        w = t.word.strip()
        if not w or '*' in w:
            continue
        if t.placement and t.placement.startswith('L'):
            continue
        m = morph.extract(w)
        if not m.middle or m.middle == '_EMPTY_':
            continue
        all_line_tokens[(t.folio, t.line)].append({
            'suffix': m.suffix or '',
            'folio': t.folio,
            'line': t.line,
            'par_initial': getattr(t, 'par_initial', False),
        })

    metadata = {
        'n_total_tokens': n_total,
        'n_en_tokens': n_en,
        'n_cross_lane_pairs': len(pairs),
        'n_lines_with_2plus_en': len(sequences),
    }
    return pairs, sequences, all_line_tokens, metadata


# ============================================================
# T1: PAIR ENRICHMENT / DEPLETION MATRIX
# ============================================================

def run_t1(pairs):
    """Fisher exact per cell, Bonferroni correction."""
    print("=" * 70)
    print("T1: Pair Enrichment/Depletion Matrix")
    print("=" * 70)

    cont = Counter((p['qo_middle'], p['chsh_middle']) for p in pairs)
    cells = enrichment_table(cont, min_expected=5)
    n_cells = len(cells)
    bonf_alpha = 0.05 / n_cells if n_cells > 0 else 0.05

    for c in cells:
        c['p_corrected'] = min(c['p_raw'] * n_cells, 1.0)
        c['significant'] = c['p_corrected'] < 0.05

    enriched = sorted([c for c in cells if c['ratio'] > 1 and c['significant']],
                       key=lambda x: -x['ratio'])
    depleted = sorted([c for c in cells if c['ratio'] < 1 and c['significant']],
                       key=lambda x: x['ratio'])

    print(f"  Cells with expected >= 5:  {n_cells}")
    print(f"  Bonferroni alpha:          {bonf_alpha:.6f}")
    print(f"\n  ENRICHED SIGNIFICANT ({len(enriched)}):")
    print(f"  {'QO_MID':<12} {'CHSH_MID':<12} {'obs':>5} {'exp':>7} {'ratio':>7} {'p_corr':>10}")
    for c in enriched[:20]:
        print(f"  {c['qo_middle']:<12} {c['chsh_middle']:<12} {c['obs']:>5} {c['exp']:>7} {c['ratio']:>7.2f} {c['p_corrected']:>10.4f}")

    print(f"\n  DEPLETED SIGNIFICANT ({len(depleted)}):")
    for c in depleted[:20]:
        print(f"  {c['qo_middle']:<12} {c['chsh_middle']:<12} {c['obs']:>5} {c['exp']:>7} {c['ratio']:>7.2f} {c['p_corrected']:>10.4f}")

    verdict = 'SELECTIVE_PAIRING' if len(enriched) >= 5 else (
        'WEAK_PAIRING' if len(enriched) >= 1 else 'NULL')
    print(f"\n  -> {len(enriched)} enriched, {len(depleted)} depleted -> Verdict: {verdict}")

    return {
        'test': 'T1_pair_enrichment',
        'n_pairs': len(pairs),
        'n_cells_tested': n_cells,
        'bonferroni_alpha': bonf_alpha,
        'n_enriched_sig': len(enriched),
        'n_depleted_sig': len(depleted),
        'enriched': enriched[:20],
        'depleted': depleted[:20],
        'verdict': verdict,
    }


# ============================================================
# T2: PAIR SELECTIVITY GRADIENT
# ============================================================

def run_t2(pairs):
    """Shannon entropy of CHSH partner distribution per QO MIDDLE."""
    print("\n" + "=" * 70)
    print("T2: Pair Selectivity Gradient")
    print("=" * 70)

    # Marginal CHSH entropy
    chsh_marginal = Counter(p['chsh_middle'] for p in pairs)
    h_marginal = shannon_entropy(chsh_marginal)

    # Per-QO-MIDDLE partner entropy
    qo_partners = defaultdict(Counter)
    for p in pairs:
        qo_partners[p['qo_middle']][p['chsh_middle']] += 1

    selectivities = []
    for qm, partner_counts in qo_partners.items():
        n = sum(partner_counts.values())
        if n < 20:
            continue
        h = shannon_entropy(partner_counts)
        top3 = partner_counts.most_common(3)
        selectivities.append({
            'qo_middle': qm,
            'n_pairs': n,
            'n_partners': len(partner_counts),
            'entropy': round(h, 3),
            'selectivity_ratio': round(h_marginal / h, 3) if h > 0 else float('inf'),
            'top_3': [{'chsh_middle': m, 'count': c, 'frac': round(c / n, 3)}
                      for m, c in top3],
        })

    selectivities.sort(key=lambda x: x['entropy'])
    entropies = [s['entropy'] for s in selectivities]

    # Selectivity vs frequency correlation
    if len(selectivities) >= 3:
        freqs = [s['n_pairs'] for s in selectivities]
        rho, p_val = sp_stats.spearmanr(freqs, entropies)
    else:
        rho, p_val = 0.0, 1.0

    print(f"  Marginal CHSH entropy:     {h_marginal:.3f} bits")
    print(f"  QO MIDDLEs with >= 20:     {len(selectivities)}")
    print(f"\n  {'QO_MID':<12} {'N':>5} {'Partners':>9} {'Entropy':>8} {'Select':>7}  Top partners")
    for s in selectivities:
        tops = ', '.join(f"{t['chsh_middle']}({t['count']})" for t in s['top_3'])
        print(f"  {s['qo_middle']:<12} {s['n_pairs']:>5} {s['n_partners']:>9} {s['entropy']:>8.3f} {s['selectivity_ratio']:>7.2f}  {tops}")

    e_range = max(entropies) - min(entropies) if entropies else 0
    print(f"\n  Entropy range: {e_range:.3f} bits ({min(entropies, default=0):.3f} to {max(entropies, default=0):.3f})")
    print(f"  Selectivity vs frequency: rho={rho:.3f}, p={p_val:.4f}")

    verdict = 'SELECTIVITY_GRADIENT' if e_range > 1.0 else 'FLAT'
    print(f"  -> Verdict: {verdict}")

    return {
        'test': 'T2_selectivity_gradient',
        'n_qo_middles_tested': len(selectivities),
        'marginal_chsh_entropy': round(h_marginal, 3),
        'qo_selectivities': selectivities,
        'entropy_range': round(e_range, 3),
        'selectivity_vs_frequency': {'rho': round(rho, 3), 'p': round(p_val, 4)},
        'verdict': verdict,
    }


# ============================================================
# T3: E-DEPTH CORRELATION ACROSS LANES
# ============================================================

def run_t3(pairs):
    """Spearman correlation on e-depth and k-count across lanes."""
    print("\n" + "=" * 70)
    print("T3: E-depth Correlation Across Lanes")
    print("=" * 70)

    qo_e = np.array([p['qo_e'] for p in pairs])
    chsh_e = np.array([p['chsh_e'] for p in pairs])
    qo_k = np.array([p['qo_k'] for p in pairs])
    chsh_k = np.array([p['chsh_k'] for p in pairs])

    rho_ee, p_ee = sp_stats.spearmanr(qo_e, chsh_e)
    rho_ke, p_ke = sp_stats.spearmanr(qo_k, chsh_e)
    rho_ek, p_ek = sp_stats.spearmanr(qo_e, chsh_k)

    print(f"  All pairs (N={len(pairs)}):")
    print(f"    e(QO) vs e(CHSH):  rho={rho_ee:.4f}, p={p_ee:.2e}")
    print(f"    k(QO) vs e(CHSH):  rho={rho_ke:.4f}, p={p_ke:.2e}")
    print(f"    e(QO) vs k(CHSH):  rho={rho_ek:.4f}, p={p_ek:.2e}")

    # Stratified: only pairs where at least one side has e > 0
    mask_e = (qo_e > 0) | (chsh_e > 0)
    n_with_e = int(mask_e.sum())
    if n_with_e >= 10:
        rho_ee_s, p_ee_s = sp_stats.spearmanr(qo_e[mask_e], chsh_e[mask_e])
        print(f"\n  Stratified (at least one e>0, N={n_with_e}):")
        print(f"    e(QO) vs e(CHSH):  rho={rho_ee_s:.4f}, p={p_ee_s:.2e}")
    else:
        rho_ee_s, p_ee_s = 0.0, 1.0

    # 2x2 single-e vs multi-e
    qo_multi = qo_e >= 2
    chsh_multi = chsh_e >= 2
    tab = np.array([
        [int(((~qo_multi) & (~chsh_multi)).sum()), int(((~qo_multi) & chsh_multi).sum())],
        [int((qo_multi & (~chsh_multi)).sum()), int((qo_multi & chsh_multi).sum())],
    ])
    if tab.min() >= 0:
        try:
            or_val, p_fisher = sp_stats.fisher_exact(tab)
        except ValueError:
            or_val, p_fisher = 1.0, 1.0
    else:
        or_val, p_fisher = 1.0, 1.0

    print(f"\n  E-depth 2x2 (single vs multi-e):")
    print(f"              CHSH_single  CHSH_multi")
    print(f"  QO_single   {tab[0,0]:>10}  {tab[0,1]:>10}")
    print(f"  QO_multi    {tab[1,0]:>10}  {tab[1,1]:>10}")
    print(f"  Fisher p={p_fisher:.4f}, OR={or_val:.3f}")

    if p_ee < 0.01:
        fb007 = 'MATCHED_INTENSITY' if rho_ee > 0 else 'COMPLEMENTARY_INTENSITY'
    else:
        fb007 = 'NULL'
    print(f"\n  F-B-007 prediction: {fb007}")

    return {
        'test': 'T3_edepth_correlation',
        'n_pairs': len(pairs),
        'spearman_ee': {'rho': round(rho_ee, 4), 'p': float(f'{p_ee:.2e}')},
        'spearman_ke': {'rho': round(rho_ke, 4), 'p': float(f'{p_ke:.2e}')},
        'spearman_ek': {'rho': round(rho_ek, 4), 'p': float(f'{p_ek:.2e}')},
        'stratified_ee': {'rho': round(rho_ee_s, 4), 'p': float(f'{p_ee_s:.2e}'),
                          'n': n_with_e},
        'cross_tab': {
            'both_single': int(tab[0, 0]), 'qo_single_chsh_multi': int(tab[0, 1]),
            'qo_multi_chsh_single': int(tab[1, 0]), 'both_multi': int(tab[1, 1]),
            'fisher_p': round(p_fisher, 4), 'odds_ratio': round(or_val, 3),
        },
        'fb007_prediction': fb007,
    }


# ============================================================
# T4: I-ATOM INDEPENDENCE CONTROL (C1205)
# ============================================================

def run_t4(pairs):
    """Control: i-count should NOT correlate across lanes."""
    print("\n" + "=" * 70)
    print("T4: I-atom Independence Control (C1205)")
    print("=" * 70)

    qo_i = np.array([p['qo_i'] for p in pairs])
    chsh_i = np.array([p['chsh_i'] for p in pairs])
    chsh_e = np.array([p['chsh_e'] for p in pairs])

    rho_ii, p_ii = sp_stats.spearmanr(qo_i, chsh_i)
    rho_ie, p_ie = sp_stats.spearmanr(qo_i, chsh_e)

    n_with_i = int(((qo_i > 0) | (chsh_i > 0)).sum())

    print(f"  i(QO) vs i(CHSH):  rho={rho_ii:.4f}, p={p_ii:.2e}  {'NULL' if p_ii > 0.05 else 'SIG!'}")
    print(f"  i(QO) vs e(CHSH):  rho={rho_ie:.4f}, p={p_ie:.2e}  {'NULL' if p_ie > 0.05 else 'SIG!'}")
    print(f"  Pairs with any i:  {n_with_i}")

    is_null = p_ii > 0.05 and p_ie > 0.05
    verdict = 'CONTROL_PASSED' if is_null else 'CONTROL_FAILED'
    print(f"\n  -> Verdict: {verdict}")

    return {
        'test': 'T4_i_atom_control',
        'spearman_ii': {'rho': round(rho_ii, 4), 'p': float(f'{p_ii:.2e}')},
        'spearman_ie': {'rho': round(rho_ie, 4), 'p': float(f'{p_ie:.2e}')},
        'n_pairs_with_i': n_with_i,
        'is_null': is_null,
        'verdict': verdict,
    }


# ============================================================
# T5: SECTION / REGIME CONDITIONING
# ============================================================

def run_t5(pairs, top_pairs):
    """Test whether top enriched pairs vary by section or REGIME."""
    print("\n" + "=" * 70)
    print("T5: Section/REGIME Conditioning")
    print("=" * 70)

    if not top_pairs:
        print("  No significant pairs from T1 to analyze.")
        return {'test': 'T5_conditioning', 'verdict': 'SKIPPED'}

    # Overall section/regime distribution (baseline)
    section_total = Counter(p['section'] for p in pairs)
    regime_total = Counter(p['regime'] for p in pairs)
    n_total = len(pairs)

    n_pairs_tested = min(len(top_pairs), 15)
    bonf_alpha_s = 0.05 / n_pairs_tested
    bonf_alpha_r = 0.05 / n_pairs_tested

    section_results = {}
    regime_results = {}

    print(f"  Top pairs analyzed: {n_pairs_tested}")
    print(f"\n  SECTION conditioning (Bonferroni alpha = {bonf_alpha_s:.4f}):")
    print(f"  {'Pair':<20} {'B':>5} {'H':>5} {'S':>5} {'p':>10} {'sig':>4}")

    for cp in top_pairs[:n_pairs_tested]:
        pair_key = (cp['qo_middle'], cp['chsh_middle'])
        label = f"{cp['qo_middle']}-{cp['chsh_middle']}"

        # Count this pair by section
        pair_section = Counter()
        other_section = Counter()
        for p in pairs:
            if (p['qo_middle'], p['chsh_middle']) == pair_key:
                pair_section[p['section']] += 1
            else:
                other_section[p['section']] += 1

        # Build contingency for chi2: sections that exist in data
        sections = sorted(set(pair_section.keys()) | set(other_section.keys()))
        if len(sections) >= 2:
            table = np.array([
                [pair_section.get(s, 0) for s in sections],
                [other_section.get(s, 0) for s in sections],
            ])
            # Remove columns with all zeros
            nonzero_cols = table.sum(axis=0) > 0
            table = table[:, nonzero_cols]
            sections_used = [s for s, nz in zip(sections, nonzero_cols) if nz]

            if table.shape[1] >= 2 and table.sum() > 0:
                try:
                    chi2, p_val, dof, _ = sp_stats.chi2_contingency(table)
                except ValueError:
                    chi2, p_val, dof = 0, 1.0, 0
            else:
                chi2, p_val, dof = 0, 1.0, 0
        else:
            chi2, p_val, dof = 0, 1.0, 0
            sections_used = sections

        sig = p_val < bonf_alpha_s
        section_results[label] = {
            'counts': {s: pair_section.get(s, 0) for s in ['B', 'H', 'S']},
            'chi2': round(chi2, 2), 'p': round(p_val, 4), 'sig': sig,
        }
        print(f"  {label:<20} {pair_section.get('B', 0):>5} {pair_section.get('H', 0):>5} "
              f"{pair_section.get('S', 0):>5} {p_val:>10.4f} {'*' if sig else ''}")

        # REGIME
        pair_regime = Counter()
        other_regime = Counter()
        for p in pairs:
            if (p['qo_middle'], p['chsh_middle']) == pair_key:
                pair_regime[p['regime']] += 1
            else:
                other_regime[p['regime']] += 1

        regimes = sorted(set(pair_regime.keys()) | set(other_regime.keys()))
        if len(regimes) >= 2:
            table_r = np.array([
                [pair_regime.get(r, 0) for r in regimes],
                [other_regime.get(r, 0) for r in regimes],
            ])
            nonzero_cols_r = table_r.sum(axis=0) > 0
            table_r = table_r[:, nonzero_cols_r]

            if table_r.shape[1] >= 2 and table_r.sum() > 0:
                try:
                    chi2_r, p_r, dof_r, _ = sp_stats.chi2_contingency(table_r)
                except ValueError:
                    chi2_r, p_r, dof_r = 0, 1.0, 0
            else:
                chi2_r, p_r, dof_r = 0, 1.0, 0
        else:
            chi2_r, p_r, dof_r = 0, 1.0, 0

        sig_r = p_r < bonf_alpha_r
        regime_results[label] = {
            'counts': {r: pair_regime.get(r, 0) for r in
                       ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']},
            'chi2': round(chi2_r, 2), 'p': round(p_r, 4), 'sig': sig_r,
        }

    n_sec_sig = sum(1 for v in section_results.values() if v['sig'])
    n_reg_sig = sum(1 for v in regime_results.values() if v['sig'])

    print(f"\n  REGIME conditioning (Bonferroni alpha = {bonf_alpha_r:.4f}):")
    print(f"  {'Pair':<20} {'R1':>5} {'R2':>5} {'R3':>5} {'R4':>5} {'p':>10} {'sig':>4}")
    for label, rv in regime_results.items():
        rc = rv['counts']
        print(f"  {label:<20} {rc.get('REGIME_1', 0):>5} {rc.get('REGIME_2', 0):>5} "
              f"{rc.get('REGIME_3', 0):>5} {rc.get('REGIME_4', 0):>5} {rv['p']:>10.4f} "
              f"{'*' if rv['sig'] else ''}")

    print(f"\n  Section-significant: {n_sec_sig}/{n_pairs_tested}")
    print(f"  Regime-significant:  {n_reg_sig}/{n_pairs_tested}")

    c821 = n_reg_sig / n_pairs_tested < 0.2 if n_pairs_tested > 0 else True
    verdict = 'SYNTAX_INVARIANT' if c821 and n_sec_sig / max(n_pairs_tested, 1) < 0.2 else (
        'DOMAIN_SPECIFIC' if n_sec_sig / max(n_pairs_tested, 1) > 0.5 else 'MIXED')
    print(f"  -> C821 consistent: {c821}")
    print(f"  -> Verdict: {verdict}")

    return {
        'test': 'T5_conditioning',
        'n_pairs_tested': n_pairs_tested,
        'section_results': section_results,
        'regime_results': regime_results,
        'n_section_significant': n_sec_sig,
        'n_regime_significant': n_reg_sig,
        'c821_consistent': c821,
        'verdict': verdict,
    }


# ============================================================
# T6: MODE A vs MODE B PAIR PROFILES
# ============================================================

def assign_line_modes(all_line_tokens):
    """Assign Mode A/B to lines using paragraph-level k-means (C1229).

    Returns dict of (folio, line) -> 'A' or 'B'.
    """
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    MIN_BODY = 8
    MIN_SIL = 0.3

    # Build paragraphs: group lines by folio, split on par_initial
    folio_lines = defaultdict(list)
    for key in sorted(all_line_tokens.keys()):
        folio, line = key
        folio_lines[folio].append((line, all_line_tokens[key]))

    mode_map = {}
    n_paras = 0
    n_assigned = 0

    for folio, lines_data in folio_lines.items():
        # Detect paragraph boundaries (par_initial tokens)
        para_starts = []
        for line_num, tokens in lines_data:
            if any(t.get('par_initial', False) for t in tokens):
                para_starts.append(line_num)

        if not para_starts:
            continue

        # Build paragraphs — line numbers may be strings
        def to_int(x):
            try:
                return int(x)
            except (ValueError, TypeError):
                return -1

        para_starts_s = sorted(set(para_starts), key=to_int)

        for pi in range(len(para_starts_s)):
            start_line = to_int(para_starts_s[pi])
            end_line = to_int(para_starts_s[pi + 1]) if pi + 1 < len(para_starts_s) else 99999

            body_lines = []
            for line_num, tokens in lines_data:
                ln = to_int(line_num)
                if ln > start_line and ln < end_line:
                    suffixes = [t['suffix'] for t in tokens]
                    body_lines.append((line_num, suffixes))

            if len(body_lines) < MIN_BODY:
                continue
            n_paras += 1

            # Compute suffix profiles
            profiles = np.array([suffix_profile(suf) for _, suf in body_lines])
            if profiles.shape[0] < MIN_BODY:
                continue

            km = KMeans(n_clusters=2, n_init=10, random_state=42).fit(profiles)
            labels = km.labels_
            try:
                sil = silhouette_score(profiles, labels)
            except ValueError:
                continue

            if sil < MIN_SIL:
                continue

            # Mode A = higher terminal fraction
            c0_term = np.mean(profiles[labels == 0, 0])
            c1_term = np.mean(profiles[labels == 1, 0])
            if c0_term >= c1_term:
                label_map = {0: 'A', 1: 'B'}
            else:
                label_map = {0: 'B', 1: 'A'}

            for i, (line_num, _) in enumerate(body_lines):
                mode_map[(folio, line_num)] = label_map[labels[i]]
                n_assigned += 1

    return mode_map, n_paras, n_assigned


def run_t6(pairs, all_line_tokens):
    """Compare pair distributions between Mode A and Mode B lines."""
    print("\n" + "=" * 70)
    print("T6: Mode A vs Mode B Pair Profiles")
    print("=" * 70)

    mode_map, n_paras, n_assigned = assign_line_modes(all_line_tokens)
    print(f"  Paragraphs assessed:  {n_paras}")
    print(f"  Lines with modes:     {n_assigned}")

    # Split pairs by mode
    mode_a_pairs = []
    mode_b_pairs = []
    for p in pairs:
        mode = mode_map.get((p['folio'], p['line']))
        if mode == 'A':
            mode_a_pairs.append(p)
        elif mode == 'B':
            mode_b_pairs.append(p)

    print(f"  Mode A pairs:         {len(mode_a_pairs)}")
    print(f"  Mode B pairs:         {len(mode_b_pairs)}")

    if len(mode_a_pairs) < 20 or len(mode_b_pairs) < 20:
        print("  Insufficient pairs for mode comparison.")
        return {'test': 'T6_mode_pairing', 'verdict': 'INSUFFICIENT_DATA'}

    # Pair distributions
    cont_a = Counter((p['qo_middle'], p['chsh_middle']) for p in mode_a_pairs)
    cont_b = Counter((p['qo_middle'], p['chsh_middle']) for p in mode_b_pairs)
    mi_a = mutual_info(cont_a)
    mi_b = mutual_info(cont_b)

    # JSD between mode distributions
    all_keys = set(cont_a.keys()) | set(cont_b.keys())
    n_a = sum(cont_a.values())
    n_b = sum(cont_b.values())
    p_a = np.array([cont_a.get(k, 0) / n_a for k in all_keys])
    p_b = np.array([cont_b.get(k, 0) / n_b for k in all_keys])
    # Add small epsilon to avoid log(0)
    eps = 1e-10
    p_a = p_a + eps
    p_b = p_b + eps
    p_a = p_a / p_a.sum()
    p_b = p_b / p_b.sum()
    m = (p_a + p_b) / 2
    jsd = 0.5 * np.sum(p_a * np.log2(p_a / m)) + 0.5 * np.sum(p_b * np.log2(p_b / m))

    # Permutation test: shuffle mode labels
    random.seed(42)
    labeled_pairs = [(p, mode_map.get((p['folio'], p['line'])))
                     for p in pairs if mode_map.get((p['folio'], p['line'])) in ('A', 'B')]
    obs_labels = [lbl for _, lbl in labeled_pairs]
    obs_pair_keys = [(p['qo_middle'], p['chsh_middle']) for p, _ in labeled_pairs]

    shuffle_jsds = []
    for _ in range(N_SHUFFLES):
        shuf_labels = obs_labels.copy()
        random.shuffle(shuf_labels)
        shuf_a = Counter()
        shuf_b = Counter()
        for pk, lbl in zip(obs_pair_keys, shuf_labels):
            if lbl == 'A':
                shuf_a[pk] += 1
            else:
                shuf_b[pk] += 1

        s_n_a = sum(shuf_a.values()) or 1
        s_n_b = sum(shuf_b.values()) or 1
        s_keys = set(shuf_a.keys()) | set(shuf_b.keys())
        s_pa = np.array([shuf_a.get(k, 0) / s_n_a for k in s_keys]) + eps
        s_pb = np.array([shuf_b.get(k, 0) / s_n_b for k in s_keys]) + eps
        s_pa = s_pa / s_pa.sum()
        s_pb = s_pb / s_pb.sum()
        s_m = (s_pa + s_pb) / 2
        s_jsd = 0.5 * np.sum(s_pa * np.log2(s_pa / s_m)) + 0.5 * np.sum(s_pb * np.log2(s_pb / s_m))
        shuffle_jsds.append(s_jsd)

    jsd_mean = np.mean(shuffle_jsds)
    jsd_std = np.std(shuffle_jsds)
    jsd_z = (jsd - jsd_mean) / jsd_std if jsd_std > 0 else 0

    print(f"\n  MI(Mode A): {mi_a:.4f} bits")
    print(f"  MI(Mode B): {mi_b:.4f} bits")
    print(f"  JSD(A, B):  {jsd:.6f}")
    print(f"  Permutation z: {jsd_z:.2f} (mean={jsd_mean:.6f}, std={jsd_std:.6f})")

    # Top enriched in each mode
    a_frac = {k: v / n_a for k, v in cont_a.items()}
    b_frac = {k: v / n_b for k, v in cont_b.items()}

    mode_a_enrich = []
    mode_b_enrich = []
    for k in all_keys:
        af = a_frac.get(k, 0)
        bf = b_frac.get(k, 0)
        if af > 0 and bf > 0:
            ratio = af / bf
            if ratio > 1.3 and cont_a.get(k, 0) >= 5:
                mode_a_enrich.append({
                    'qo_middle': k[0], 'chsh_middle': k[1],
                    'a_frac': round(af, 4), 'b_frac': round(bf, 4),
                    'ratio': round(ratio, 2)
                })
            if ratio < 0.7 and cont_b.get(k, 0) >= 5:
                mode_b_enrich.append({
                    'qo_middle': k[0], 'chsh_middle': k[1],
                    'a_frac': round(af, 4), 'b_frac': round(bf, 4),
                    'ratio': round(1 / ratio, 2)
                })

    mode_a_enrich.sort(key=lambda x: -x['ratio'])
    mode_b_enrich.sort(key=lambda x: -x['ratio'])

    if mode_a_enrich:
        print(f"\n  Mode A enriched pairs:")
        for e in mode_a_enrich[:10]:
            print(f"    {e['qo_middle']}-{e['chsh_middle']}: A={e['a_frac']:.3f}, B={e['b_frac']:.3f}, ratio={e['ratio']:.2f}")
    if mode_b_enrich:
        print(f"\n  Mode B enriched pairs:")
        for e in mode_b_enrich[:10]:
            print(f"    {e['qo_middle']}-{e['chsh_middle']}: B={e['b_frac']:.3f}, A={e['a_frac']:.3f}, ratio={e['ratio']:.2f}")

    verdict = 'MODE_DIFFERENTIATED' if jsd_z > 3 else 'MODE_INVARIANT'
    print(f"\n  -> Verdict: {verdict}")

    return {
        'test': 'T6_mode_pairing',
        'n_paragraphs': n_paras,
        'n_lines_with_modes': n_assigned,
        'n_mode_a_pairs': len(mode_a_pairs),
        'n_mode_b_pairs': len(mode_b_pairs),
        'mi_mode_a': round(mi_a, 4),
        'mi_mode_b': round(mi_b, 4),
        'jsd': round(jsd, 6),
        'jsd_z': round(jsd_z, 2),
        'mode_a_enriched': mode_a_enrich[:10],
        'mode_b_enriched': mode_b_enrich[:10],
        'verdict': verdict,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("Phase 444: EN_CROSS_LANE_PAIRING")
    print("=" * 70)

    print("\nLoading data...")
    pairs, sequences, all_line_tokens, meta = load_cross_lane_data()
    print(f"  Total B tokens (filtered):  {meta['n_total_tokens']}")
    print(f"  EN-lane tokens (QO+CHSH):   {meta['n_en_tokens']}")
    print(f"  Cross-lane pairs:           {meta['n_cross_lane_pairs']}")
    print(f"  Lines with 2+ EN:           {meta['n_lines_with_2plus_en']}")

    # T1
    t1 = run_t1(pairs)

    # T2
    t2 = run_t2(pairs)

    # T3
    t3 = run_t3(pairs)

    # T4
    t4 = run_t4(pairs)

    # T5 (uses T1 top pairs)
    top_pairs = t1.get('enriched', []) + t1.get('depleted', [])
    t5 = run_t5(pairs, top_pairs)

    # T6
    t6 = run_t6(pairs, all_line_tokens)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  T1 Pair enrichment:      {t1['n_enriched_sig']} enriched, {t1['n_depleted_sig']} depleted ({t1['verdict']})")
    print(f"  T2 Selectivity gradient: range={t2.get('entropy_range', 'N/A')} bits ({t2['verdict']})")
    print(f"  T3 E-depth correlation:  rho={t3['spearman_ee']['rho']} ({t3['fb007_prediction']})")
    print(f"  T4 I-atom control:       {t4['verdict']}")
    print(f"  T5 Section/REGIME:       {t5.get('n_section_significant', '?')}/{t5.get('n_pairs_tested', '?')} sec, "
          f"{t5.get('n_regime_significant', '?')}/{t5.get('n_pairs_tested', '?')} reg ({t5['verdict']})")
    print(f"  T6 Mode pairing:         JSD z={t6.get('jsd_z', 'N/A')} ({t6['verdict']})")

    # Save results
    results = {
        'phase': 'EN_CROSS_LANE_PAIRING',
        'phase_number': 444,
        'metadata': meta,
        'T1_pair_enrichment': t1,
        'T2_selectivity_gradient': t2,
        'T3_edepth_correlation': t3,
        'T4_i_atom_control': t4,
        'T5_conditioning': t5,
        'T6_mode_pairing': t6,
    }
    out_path = RESULTS_DIR / 'cross_lane_pairing.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
