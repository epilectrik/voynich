"""
Phase 598c: Blind Prediction Test -- 1512 Brunschwig de compositis

Tests 5 positive predictions and 1 negative control pre-registered
in PREDICTIONS.md (SHA-256: ddeee7f7252ff378b7a1ca0b964f6d38b433f7ec0f90ab17526a383b36ef058d).

All predictions derive from the 1512 recipe distribution (never used in any prior fit).
Approach A: class-level distributional predictions, no recipe-to-folio mapping.

v2 CORRECTIONS (post expert review):
  1. All tests use R1 vs R3+R4 consistently (R2 excluded as ambiguous)
  2. P2/P3 add section-stratified (Herbal-only) replication to control section confound
  3. P5 adds partial correlation controlling for log(n_tokens) to remove size confound
  4. N2 DROPPED -- trivially passes (Jaccard=1.000), C1499 guarantees atom universality
  5. N1 annotated: failure is informative (C1574: headless IS folio-parameterized)
  6. P2 annotated: direction is genuine prediction, p-value partially inflated by
     REGIME definition overlap with ke-features
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, decompose_middle_hmt

# --- Paths ---
REGIME_PATH = Path("data/regime_folio_mapping.json")
CLASS_MAP_PATH = Path("phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json")
OUT_PATH = Path("phases/BRUNSCHWIG_1512_BLIND_PREDICTION/results/blind_prediction_results.json")

# --- Thresholds from PREDICTIONS.md ---
P1_GENTLE_MIN = 0.60       # R1 fraction of (R1+R3+R4) must be > 60%
P2_P_THRESHOLD = 0.05      # Mann-Whitney p < 0.05
P3_P_THRESHOLD = 0.05
P4_P_THRESHOLD = 0.05
P5_RHO_MIN = 0.15          # Spearman rho > 0.15
P5_P_THRESHOLD = 0.05
N1_P_THRESHOLD = 0.10      # Must be p > 0.10 (non-significant)


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


def load_regime_map():
    with open(REGIME_PATH) as f:
        data = json.load(f)
    return {f: info['regime'] for f, info in data['regime_assignments'].items()}


def load_class_map():
    with open(CLASS_MAP_PATH) as f:
        data = json.load(f)
    return {t: int(c) for t, c in data['token_to_class'].items()}


def assemble_data():
    """Build per-folio and per-token data structures for all B tokens."""
    tx = Transcript()
    morph = Morphology()
    regime_map = load_regime_map()
    class_map = load_class_map()

    folio_data = defaultdict(lambda: {
        'tokens': [],
        'n_tokens': 0,
        'regime': None,
        'section': None,
    })

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        if token.placement.startswith('L'):
            continue

        folio = token.folio
        m = morph.extract(w)
        head, mods, term, frame = decompose_middle_hmt(m.middle)
        cls = class_map.get(w)

        tok = {
            'word': w,
            'folio': folio,
            'line': token.line,
            'middle': m.middle,
            'head': head,
            'term': term,
            'mods': mods,
            'frame': frame,
            'cls': cls,
            'is_ey': (head == 'e' and term == 'y'),
            'is_headless': head is None and len(m.middle) > 2,
        }
        folio_data[folio]['tokens'].append(tok)
        folio_data[folio]['n_tokens'] += 1

        if folio in regime_map:
            folio_data[folio]['regime'] = regime_map[folio]

        # Capture section from first token seen
        if folio_data[folio]['section'] is None and token.section:
            folio_data[folio]['section'] = token.section

    return dict(folio_data)


def compute_folio_features(folio_data):
    """Compute per-folio structural features for prediction tests."""
    features = {}

    for folio, fdata in folio_data.items():
        tokens = fdata['tokens']
        n = len(tokens)
        if n < 10:
            continue

        regime = fdata['regime']
        if regime is None:
            continue

        section = fdata['section']

        # k/(k+ke) ratio
        k_head = sum(1 for t in tokens if t['head'] == 'k')
        e_head = sum(1 for t in tokens if t['head'] == 'e')
        k_ke_ratio = k_head / (k_head + e_head) if (k_head + e_head) > 0 else 0.5

        # e-to-y rate
        n_ey = sum(1 for t in tokens if t['is_ey'])
        ey_rate = n_ey / n

        # Terminal r -> a routing
        r_total = 0
        r_to_a = 0
        line_tokens = defaultdict(list)
        for t in tokens:
            line_tokens[(folio, t['line'])].append(t)
        for key, ltoks in line_tokens.items():
            for i in range(len(ltoks) - 1):
                if ltoks[i]['term'] == 'r':
                    r_total += 1
                    if ltoks[i + 1]['head'] == 'a':
                        r_to_a += 1
        r_to_a_rate = r_to_a / r_total if r_total > 0 else 0.0

        # Headless compound rate
        n_headless = sum(1 for t in tokens if t['is_headless'])
        headless_rate = n_headless / n

        # Instruction class entropy
        cls_counts = Counter(t['cls'] for t in tokens if t['cls'] is not None)
        total_classed = sum(cls_counts.values())
        if total_classed > 0:
            probs = np.array(list(cls_counts.values()), dtype=float) / total_classed
            probs = probs[probs > 0]
            class_entropy = float(-np.sum(probs * np.log2(probs)))
        else:
            class_entropy = 0.0

        # ke-depth: mean e-depth among e-HEAD tokens
        e_depths = []
        for t in tokens:
            if t['head'] == 'e':
                mid = t['middle']
                depth = 0
                for ch in mid:
                    if ch == 'e':
                        depth += 1
                    else:
                        break
                e_depths.append(depth)
        mean_e_depth = np.mean(e_depths) if e_depths else 0.0

        features[folio] = {
            'regime': regime,
            'section': section,
            'n_tokens': n,
            'k_ke_ratio': k_ke_ratio,
            'ey_rate': ey_rate,
            'r_to_a_rate': r_to_a_rate,
            'headless_rate': headless_rate,
            'class_entropy': class_entropy,
            'mean_e_depth': mean_e_depth,
        }

    return features


def mann_whitney_test(group1, group2):
    """Mann-Whitney U test (two-sided)."""
    from scipy.stats import mannwhitneyu
    if len(group1) < 3 or len(group2) < 3:
        return {'U': None, 'p': 1.0, 'n1': len(group1), 'n2': len(group2)}
    U, p = mannwhitneyu(group1, group2, alternative='two-sided')
    return {'U': float(U), 'p': float(p), 'n1': len(group1), 'n2': len(group2),
            'mean1': float(np.mean(group1)), 'mean2': float(np.mean(group2))}


def spearman_test(x, y):
    """Spearman rank correlation."""
    from scipy.stats import spearmanr
    rho, p = spearmanr(x, y)
    return {'rho': float(rho), 'p': float(p), 'n': len(x)}


def partial_spearman(x, y, z):
    """Partial Spearman: rank-transform, regress out z, correlate residuals."""
    from scipy.stats import rankdata, pearsonr
    rx = rankdata(x)
    ry = rankdata(y)
    rz = rankdata(z)

    # Regress out confound
    slope_x, intercept_x = np.polyfit(rz, rx, 1)
    resid_x = rx - (slope_x * rz + intercept_x)

    slope_y, intercept_y = np.polyfit(rz, ry, 1)
    resid_y = ry - (slope_y * rz + intercept_y)

    r, p = pearsonr(resid_x, resid_y)
    return {'rho': float(r), 'p': float(p), 'n': len(x)}


# =========================================================
# GROUPING HELPERS -- v2: R1 vs R3+R4, R2 excluded
# =========================================================
GENTLE_REGIMES = ('REGIME_1',)
INTENSE_REGIMES = ('REGIME_3', 'REGIME_4')

def is_gentle(regime):
    return regime in GENTLE_REGIMES

def is_intense(regime):
    return regime in INTENSE_REGIMES

def split_groups(features, section_filter=None):
    """Split features into gentle (R1) and intense (R3+R4), optionally filtered by section."""
    gentle = {}
    intense = {}
    for folio, f in features.items():
        if section_filter and f['section'] != section_filter:
            continue
        if is_gentle(f['regime']):
            gentle[folio] = f
        elif is_intense(f['regime']):
            intense[folio] = f
    return gentle, intense


# =========================================================
# TESTS
# =========================================================

def run_p1(features):
    """P1: REGIME Distribution Matches Fire Degree Ratio.
    v2: R1 fraction of resolved (R1+R3+R4), excluding ambiguous R2.
    """
    regime_counts = Counter(f['regime'] for f in features.values())
    total = sum(regime_counts.values())

    r1 = regime_counts.get('REGIME_1', 0)
    r3_r4 = regime_counts.get('REGIME_3', 0) + regime_counts.get('REGIME_4', 0)
    resolved = r1 + r3_r4
    r1_frac = r1 / resolved if resolved > 0 else 0

    # Also report R1+R2 for reference (original grouping)
    r1_r2 = r1 + regime_counts.get('REGIME_2', 0)
    r1_r2_frac = r1_r2 / total if total > 0 else 0

    passed = r1_frac > P1_GENTLE_MIN

    return {
        'test': 'P1_regime_distribution',
        'regime_counts': dict(regime_counts),
        'total_folios': total,
        'r1_count': r1,
        'r3_r4_count': r3_r4,
        'resolved_count': resolved,
        'r1_fraction_of_resolved': round(r1_frac, 4),
        'r1_r2_fraction_of_total': round(r1_r2_frac, 4),
        'threshold': P1_GENTLE_MIN,
        'passed': passed,
        'note': (f'R1/(R1+R3+R4) = {r1}/{resolved} = {r1_frac:.1%}; '
                 f'R1+R2 = {r1_r2}/{total} = {r1_r2_frac:.1%}; '
                 f'predicted >60% from 1512 gentle:elevated ratio 4.9:1'),
        'v2_fix': 'R2 excluded from resolved count for consistency with P2-P4 grouping',
    }


def run_p2(features, section_filter=None):
    """P2: k/(k+ke) Ratio Discriminates REGIME Classes.
    v2: R1 vs R3+R4 consistently. Optional section filter for stratification.
    """
    gentle, intense = split_groups(features, section_filter)
    g_vals = [f['k_ke_ratio'] for f in gentle.values()]
    i_vals = [f['k_ke_ratio'] for f in intense.values()]

    mw = mann_whitney_test(g_vals, i_vals)
    direction_correct = mw.get('mean1', 0) > mw.get('mean2', 0)
    passed = mw['p'] < P2_P_THRESHOLD and direction_correct

    result = {
        'test': 'P2_k_ke_ratio_by_regime',
        'gentle_mean': round(mw.get('mean1', 0), 4),
        'intense_mean': round(mw.get('mean2', 0), 4),
        'mann_whitney_U': mw['U'],
        'p_value': round(mw['p'], 6),
        'direction_correct': direction_correct,
        'n_gentle': mw['n1'],
        'n_intense': mw['n2'],
        'passed': passed,
        'v2_note': ('Direction is genuine prediction from 1512 fire degrees. '
                    'P-value partially inflated: REGIME definition overlaps ke-features.'),
    }
    if section_filter:
        result['section_filter'] = section_filter
    return result


def run_p3(features, section_filter=None):
    """P3: e->y Safe Pathway Rate Discriminates REGIME Classes.
    v2: R1 vs R3+R4 consistently. Optional section filter.
    """
    gentle, intense = split_groups(features, section_filter)
    g_vals = [f['ey_rate'] for f in gentle.values()]
    i_vals = [f['ey_rate'] for f in intense.values()]

    mw = mann_whitney_test(g_vals, i_vals)
    direction_correct = mw.get('mean1', 0) > mw.get('mean2', 0)
    passed = mw['p'] < P3_P_THRESHOLD and direction_correct

    result = {
        'test': 'P3_ey_rate_by_regime',
        'gentle_mean': round(mw.get('mean1', 0), 4),
        'intense_mean': round(mw.get('mean2', 0), 4),
        'mann_whitney_U': mw['U'],
        'p_value': round(mw['p'], 6),
        'direction_correct': direction_correct,
        'n_gentle': mw['n1'],
        'n_intense': mw['n2'],
        'passed': passed,
    }
    if section_filter:
        result['section_filter'] = section_filter
    return result


def run_p4(features):
    """P4: Terminal r->a Routing Rate Discriminates REGIME Classes."""
    gentle, intense = split_groups(features)
    g_vals = [f['r_to_a_rate'] for f in gentle.values()]
    i_vals = [f['r_to_a_rate'] for f in intense.values()]

    mw = mann_whitney_test(g_vals, i_vals)
    # Prediction: intense > gentle
    direction_correct = mw.get('mean2', 0) > mw.get('mean1', 0)
    passed = mw['p'] < P4_P_THRESHOLD and direction_correct

    return {
        'test': 'P4_r_to_a_routing_by_regime',
        'gentle_mean': round(mw.get('mean1', 0), 4),
        'intense_mean': round(mw.get('mean2', 0), 4),
        'mann_whitney_U': mw['U'],
        'p_value': round(mw['p'], 6),
        'direction_correct': direction_correct,
        'n_gentle': mw['n1'],
        'n_intense': mw['n2'],
        'passed': passed,
        'v2_note': 'Failure accepted as genuine -- consistent with C1724 (routing is compositional)',
    }


def run_p5(features):
    """P5: Procedural Complexity Correlates with ke-Depth.
    v2: Adds partial correlation controlling for log(n_tokens) to remove size confound.
    """
    entropies = []
    e_depths = []
    log_sizes = []
    for f in features.values():
        if f['mean_e_depth'] > 0:
            entropies.append(f['class_entropy'])
            e_depths.append(f['mean_e_depth'])
            log_sizes.append(np.log(f['n_tokens']))

    # Raw correlation
    sp_raw = spearman_test(entropies, e_depths)

    # Partial correlation controlling for log(n_tokens)
    sp_partial = partial_spearman(entropies, e_depths, log_sizes)

    # Use partial correlation for pass/fail
    passed = sp_partial['rho'] > P5_RHO_MIN and sp_partial['p'] < P5_P_THRESHOLD

    return {
        'test': 'P5_complexity_ke_depth_correlation',
        'raw_spearman_rho': round(sp_raw['rho'], 4),
        'raw_p_value': round(sp_raw['p'], 6),
        'partial_spearman_rho': round(sp_partial['rho'], 4),
        'partial_p_value': round(sp_partial['p'], 6),
        'n_folios': sp_raw['n'],
        'rho_threshold': P5_RHO_MIN,
        'passed': passed,
        'v2_fix': 'Partial correlation controlling for log(n_tokens) removes size confound',
    }


def run_n1(features):
    """N1: Headless Compound Rate Independence.
    v2: Annotated -- failure is informative (C1574: headless IS folio-parameterized).
    """
    gentle, intense = split_groups(features)
    g_vals = [f['headless_rate'] for f in gentle.values()]
    i_vals = [f['headless_rate'] for f in intense.values()]

    mw = mann_whitney_test(g_vals, i_vals)
    # Negative control: should NOT be significant
    passed = mw['p'] > N1_P_THRESHOLD

    return {
        'test': 'N1_headless_rate_independence',
        'gentle_mean': round(mw.get('mean1', 0), 4),
        'intense_mean': round(mw.get('mean2', 0), 4),
        'mann_whitney_U': mw['U'],
        'p_value': round(mw['p'], 6),
        'threshold': N1_P_THRESHOLD,
        'passed': passed,
        'note': 'Negative control: PASSES if p > 0.10 (no significant difference)',
        'v2_note': ('Failure is informative, not damaging: C1574 confirms headless rate IS '
                    'folio-parameterized. This was a mis-premised control, not a structural failure.'),
    }


def compute_verdict(results):
    """Compute overall verdict from test results.
    v2: 5 positive tests, 1 negative control (N2 dropped).
    """
    positive = [r for r in results if r['test'].startswith('P')]
    negative = [r for r in results if r['test'].startswith('N')]

    n_positive_pass = sum(1 for r in positive if r['passed'])
    n_negative_pass = sum(1 for r in negative if r['passed'])

    if n_positive_pass >= 5:
        verdict = 'STRONG_ALIGNMENT'
    elif n_positive_pass >= 4:
        verdict = 'ALIGNMENT'
    elif n_positive_pass >= 3:
        verdict = 'WEAK_ALIGNMENT'
    else:
        verdict = 'NO_ALIGNMENT'

    # With only 1 negative control, 0/1 = controls failed
    if len(negative) > 0 and n_negative_pass < len(negative):
        verdict += '_CONTROLS_NOTED'

    return {
        'verdict': verdict,
        'positive_passed': n_positive_pass,
        'positive_total': len(positive),
        'negative_passed': n_negative_pass,
        'negative_total': len(negative),
    }


def main():
    import time
    t0 = time.time()

    print("Phase 598c v2: Corrected Blind Prediction Test")
    print("=" * 60)
    print("Corrections applied:")
    print("  1. R1 vs R3+R4 consistently (R2 excluded)")
    print("  2. Section-stratified replication for P2/P3")
    print("  3. Partial correlation for P5 (size control)")
    print("  4. N2 dropped (trivially passes)")
    print()

    print("Assembling B token data...")
    folio_data = assemble_data()
    n_folios = len(folio_data)
    n_tokens = sum(f['n_tokens'] for f in folio_data.values())
    print(f"  {n_folios} folios, {n_tokens} tokens")

    print("Computing per-folio features...")
    features = compute_folio_features(folio_data)
    print(f"  {len(features)} folios with features (>10 tokens + REGIME assigned)")

    # Regime distribution summary
    regime_dist = Counter(f['regime'] for f in features.values())
    print(f"  REGIME distribution: {dict(regime_dist)}")

    # Section-regime cross-tab
    section_regime = defaultdict(lambda: Counter())
    for f in features.values():
        section_regime[f['section']][f['regime']] += 1
    print("\n  Section-REGIME cross-tab:")
    for sec in sorted(section_regime.keys()):
        counts = section_regime[sec]
        r1 = counts.get('REGIME_1', 0)
        r2 = counts.get('REGIME_2', 0)
        r3 = counts.get('REGIME_3', 0)
        r4 = counts.get('REGIME_4', 0)
        print(f"    {sec}: R1={r1} R2={r2} R3={r3} R4={r4}")

    # Identify best section for stratification (needs both R1 and R3+R4)
    herbal_section = None
    for sec in sorted(section_regime.keys()):
        counts = section_regime[sec]
        has_gentle = counts.get('REGIME_1', 0) >= 3
        has_intense = (counts.get('REGIME_3', 0) + counts.get('REGIME_4', 0)) >= 3
        if has_gentle and has_intense:
            if herbal_section is None or sec == 'H':  # prefer Herbal
                herbal_section = sec
    print(f"\n  Section for stratified replication: {herbal_section}")

    print("\n=== Running Predictions (v2: R1 vs R3+R4) ===\n")

    results = []

    # P1: REGIME distribution
    p1 = run_p1(features)
    results.append(p1)
    status = 'PASS' if p1['passed'] else 'FAIL'
    print(f"P1 (REGIME distribution): {status} -- "
          f"R1/(R1+R3+R4) = {p1['r1_fraction_of_resolved']:.1%}, "
          f"R1+R2/total = {p1['r1_r2_fraction_of_total']:.1%}")

    # P2: k/(k+ke) by REGIME -- full sample
    p2 = run_p2(features)
    results.append(p2)
    status = 'PASS' if p2['passed'] else 'FAIL'
    print(f"P2 (k/(k+ke) ratio): {status} -- "
          f"gentle={p2['gentle_mean']:.4f}, intense={p2['intense_mean']:.4f}, "
          f"p={p2['p_value']:.6f}")

    # P2 stratified: Herbal only
    if herbal_section:
        p2_strat = run_p2(features, section_filter=herbal_section)
        results.append(p2_strat)
        p2_strat['test'] = 'P2_stratified_herbal'
        status = 'PASS' if p2_strat['passed'] else 'FAIL'
        print(f"  P2 stratified ({herbal_section} only): {status} -- "
              f"gentle={p2_strat['gentle_mean']:.4f}, intense={p2_strat['intense_mean']:.4f}, "
              f"p={p2_strat['p_value']:.6f}, n={p2_strat['n_gentle']}+{p2_strat['n_intense']}")

    # P3: e->y rate by REGIME -- full sample
    p3 = run_p3(features)
    results.append(p3)
    status = 'PASS' if p3['passed'] else 'FAIL'
    print(f"P3 (e->y rate): {status} -- "
          f"gentle={p3['gentle_mean']:.4f}, intense={p3['intense_mean']:.4f}, "
          f"p={p3['p_value']:.6f}")

    # P3 stratified: Herbal only
    if herbal_section:
        p3_strat = run_p3(features, section_filter=herbal_section)
        results.append(p3_strat)
        p3_strat['test'] = 'P3_stratified_herbal'
        status = 'PASS' if p3_strat['passed'] else 'FAIL'
        print(f"  P3 stratified ({herbal_section} only): {status} -- "
              f"gentle={p3_strat['gentle_mean']:.4f}, intense={p3_strat['intense_mean']:.4f}, "
              f"p={p3_strat['p_value']:.6f}, n={p3_strat['n_gentle']}+{p3_strat['n_intense']}")

    # P4: r->a routing by REGIME
    p4 = run_p4(features)
    results.append(p4)
    status = 'PASS' if p4['passed'] else 'FAIL'
    print(f"P4 (r->a routing): {status} -- "
          f"gentle={p4['gentle_mean']:.4f}, intense={p4['intense_mean']:.4f}, "
          f"p={p4['p_value']:.6f}")

    # P5: complexity-ke correlation (with size control)
    p5 = run_p5(features)
    results.append(p5)
    status = 'PASS' if p5['passed'] else 'FAIL'
    print(f"P5 (complexity~ke-depth): {status} -- "
          f"raw rho={p5['raw_spearman_rho']:.4f}, "
          f"partial rho={p5['partial_spearman_rho']:.4f} (size-controlled), "
          f"p={p5['partial_p_value']:.6f}")

    # N1: headless independence
    n1 = run_n1(features)
    results.append(n1)
    status = 'PASS' if n1['passed'] else 'FAIL'
    print(f"N1 (headless independence): {status} -- p={n1['p_value']:.6f}")
    if not n1['passed']:
        print(f"  (Expected: C1574 confirms headless IS folio-parameterized)")

    # N2: DROPPED
    print("N2 (atom overlap): DROPPED -- Jaccard=1.000 guaranteed by C1499")

    # Verdict (only count primary P and N tests, not stratified replications)
    primary_results = [r for r in results
                       if not r['test'].endswith('_herbal')]
    verdict = compute_verdict(primary_results)
    elapsed = time.time() - t0
    print(f"\n=== VERDICT: {verdict['verdict']} ===")
    print(f"Positive: {verdict['positive_passed']}/{verdict['positive_total']}")
    print(f"Negative: {verdict['negative_passed']}/{verdict['negative_total']}")
    print(f"Runtime: {elapsed:.1f}s")

    # Summary assessment
    print("\n=== HONEST ASSESSMENT ===")
    p2_survives = any(r['test'] == 'P2_stratified_herbal' and r['passed'] for r in results)
    p3_survives = any(r['test'] == 'P3_stratified_herbal' and r['passed'] for r in results)
    print(f"P2 survives Herbal stratification: {p2_survives}")
    print(f"P3 survives Herbal stratification: {p3_survives}")
    print(f"P5 survives size control: {p5['passed']}")

    # Output
    output = {
        'metadata': {
            'phase': '598c_v2',
            'prediction_hash': 'ddeee7f7252ff378b7a1ca0b964f6d38b433f7ec0f90ab17526a383b36ef058d',
            'n_b_tokens': n_tokens,
            'n_folios_with_features': len(features),
            'runtime_seconds': round(elapsed, 1),
            'v2_corrections': [
                'R1 vs R3+R4 consistently (R2 excluded)',
                'Section-stratified replication for P2/P3',
                'Partial correlation for P5 (log(n_tokens) control)',
                'N2 dropped (trivially passes)',
                'N1 failure annotated as informative (C1574)',
            ],
        },
        'section_regime_crosstab': {
            sec: dict(counts)
            for sec, counts in section_regime.items()
        },
        'results': results,
        'stratification_summary': {
            'section_used': herbal_section,
            'P2_survives_stratification': p2_survives,
            'P3_survives_stratification': p3_survives,
            'P5_survives_size_control': p5['passed'],
        },
        'verdict': verdict,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nWrote results to {OUT_PATH}")


if __name__ == '__main__':
    main()
