"""
Phase 598d: Follow-up Apparatus Profile + Within-Folio Gradient Tests

Two independent blocks testing the 1512 Brunschwig alignment from different angles:

Block 1: APPARATUS PROFILE TEST (within Herbal section)
  Do R1 vs R2+R3+R4 folios within Herbal show apparatus profile scores
  (C1248, MIDDLE-based) predicted by 1512 fire degree distributions?
  Prediction chain:
    1512 degree 1 = balneum mariae (sealed water bath, sustained gentle heat)
    1512 degree 2-3 = direct/open fire (active distillation, vapor management)
    R1 (gentle) should show: higher SEALED_VESSEL + SUSTAINED_HEAT,
                              lower DISTILLATION + DIRECT_FIRE

Block 2: WITHIN-FOLIO GRADIENT TEST
  Do paragraph-level grammar features shift within folios in ways
  consistent with the 1512 alignment?
  H1: No monotonic e->y gradient across paragraph ordinals (C1399/C1400)
  H2: THERMAL-enriched paragraphs have higher e->y rate within folio
  H3: ke-depth correlates with thermal fraction within folio
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, decompose_middle_hmt, CategoryClassifier

# --- Paths ---
REGIME_PATH = Path("data/regime_folio_mapping.json")
APPARATUS_PATH = Path("phases/APPARATUS_VOCABULARY_CLASSIFICATION/results/apparatus_profiles.json")
OUT_PATH = Path("phases/BRUNSCHWIG_1512_BLIND_PREDICTION/results/followup_results.json")


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


def load_apparatus_scores():
    """Load per-folio apparatus profile scores from C1248 results."""
    with open(APPARATUS_PATH) as f:
        data = json.load(f)
    return data['folio_scores']


def assemble_data():
    """Build per-token data with section, paragraph info."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()
    regime_map = load_regime_map()

    folio_data = defaultdict(lambda: {
        'tokens': [],
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
        cat = cc.classify(m.middle)

        # e-depth for ke-family
        e_depth = 0
        if head == 'e':
            for ch in m.middle:
                if ch == 'e':
                    e_depth += 1
                else:
                    break

        tok = {
            'word': w,
            'folio': folio,
            'line': token.line,
            'middle': m.middle,
            'head': head,
            'term': term,
            'category': cat,
            'e_depth': e_depth,
            'is_ey': (head == 'e' and term == 'y'),
            'par_initial': token.par_initial,
        }
        folio_data[folio]['tokens'].append(tok)

        if folio in regime_map:
            folio_data[folio]['regime'] = regime_map[folio]
        if folio_data[folio]['section'] is None and token.section:
            folio_data[folio]['section'] = token.section

    return dict(folio_data)


def mann_whitney_onetail(group1, group2, alternative='greater'):
    """Mann-Whitney U test (one-tailed)."""
    from scipy.stats import mannwhitneyu
    if len(group1) < 2 or len(group2) < 2:
        return {'U': None, 'p': 1.0, 'n1': len(group1), 'n2': len(group2),
                'mean1': float(np.mean(group1)) if group1 else 0,
                'mean2': float(np.mean(group2)) if group2 else 0}
    try:
        U, p = mannwhitneyu(group1, group2, alternative=alternative)
    except ValueError:
        return {'U': None, 'p': 1.0, 'n1': len(group1), 'n2': len(group2),
                'mean1': float(np.mean(group1)), 'mean2': float(np.mean(group2))}
    return {'U': float(U), 'p': float(p), 'n1': len(group1), 'n2': len(group2),
            'mean1': float(np.mean(group1)), 'mean2': float(np.mean(group2))}


# =========================================================
# BLOCK 1: APPARATUS PROFILE TEST (within Herbal)
# =========================================================

def run_block1(folio_data):
    """Apparatus profile test: R1 vs R2+R3+R4 within Herbal using C1248 scores."""
    print("=" * 60)
    print("BLOCK 1: Apparatus Profile Test (within Herbal, MIDDLE-based)")
    print("=" * 60)

    apparatus_scores = load_apparatus_scores()
    regime_map = load_regime_map()

    # Get section per folio
    folio_section = {f: fd['section'] for f, fd in folio_data.items()}

    # 1512 predictions for apparatus profile direction within Herbal:
    # R1 (gentle, balneum mariae, degree 1):
    #   SEALED_VESSEL: HIGHER (sealed water bath)
    #   SUSTAINED_HEAT: HIGHER (gentle sustained heat)
    #   DISTILLATION: LOWER (active vapor management needs higher temps)
    #   DIRECT_FIRE: LOWER (not using direct fire)
    predictions = {
        'SEALED_VESSEL': {'r1_higher': True, 'label': 'R1 > rest (balneum = sealed vessel)'},
        'SUSTAINED_HEAT': {'r1_higher': True, 'label': 'R1 > rest (gentle = sustained heat)'},
        'DISTILLATION': {'r1_higher': False, 'label': 'R1 < rest (distillation needs higher temps)'},
        'DIRECT_FIRE': {'r1_higher': False, 'label': 'R1 < rest (direct fire = degree 2-3)'},
    }

    # Filter to Herbal section folios with apparatus scores
    herbal_r1 = []
    herbal_rest = []
    herbal_r1_folios = []
    herbal_rest_folios = []

    for folio, scores in apparatus_scores.items():
        section = folio_section.get(folio)
        regime = regime_map.get(folio)
        if section != 'H' or regime is None:
            continue
        if regime == 'REGIME_1':
            herbal_r1.append(scores)
            herbal_r1_folios.append(folio)
        else:
            herbal_rest.append(scores)
            herbal_rest_folios.append(folio)

    print(f"\n  Herbal R1: n={len(herbal_r1)} folios: {herbal_r1_folios}")
    print(f"  Herbal R2+R3+R4: n={len(herbal_rest)} folios")

    # Regime breakdown within Herbal
    regime_breakdown = Counter(regime_map.get(f) for f in herbal_rest_folios)
    print(f"  Rest breakdown: {dict(regime_breakdown)}")

    results = {'tests': [], 'directions_correct': 0, 'significant_count': 0}

    for profile, pred in predictions.items():
        r1_vals = [s[profile] for s in herbal_r1]
        rest_vals = [s[profile] for s in herbal_rest]

        # One-tailed test in predicted direction
        if pred['r1_higher']:
            mw = mann_whitney_onetail(r1_vals, rest_vals, alternative='greater')
            direction_correct = np.mean(r1_vals) > np.mean(rest_vals)
        else:
            mw = mann_whitney_onetail(r1_vals, rest_vals, alternative='less')
            direction_correct = np.mean(r1_vals) < np.mean(rest_vals)

        significant = mw['p'] < 0.10  # relaxed for n=2

        # Percentile rank: where do R1 folios fall in the Herbal distribution?
        all_vals = rest_vals + r1_vals
        percentiles = []
        for v in r1_vals:
            pct = sum(1 for x in rest_vals if x <= v) / len(rest_vals) * 100
            percentiles.append(round(pct, 1))

        # Are both R1 folios in the predicted half?
        if pred['r1_higher']:
            both_in_predicted_half = all(p >= 50 for p in percentiles)
        else:
            both_in_predicted_half = all(p <= 50 for p in percentiles)

        test_result = {
            'profile': profile,
            'prediction': pred['label'],
            'r1_mean': round(np.mean(r1_vals), 4),
            'r1_values': [round(v, 4) for v in r1_vals],
            'rest_mean': round(np.mean(rest_vals), 4),
            'direction_correct': bool(direction_correct),
            'p_value_onetail': round(mw['p'], 6),
            'significant_p10': bool(significant),
            'r1_percentiles_in_herbal': percentiles,
            'both_in_predicted_half': bool(both_in_predicted_half),
        }
        results['tests'].append(test_result)
        results['directions_correct'] += int(direction_correct)
        results['significant_count'] += int(significant)

        status = 'OK' if direction_correct else 'WRONG'
        sig = '*' if significant else ''
        half = 'BOTH_PREDICTED' if both_in_predicted_half else 'mixed'
        print(f"    {profile}: R1={np.mean(r1_vals):.4f} vs rest={np.mean(rest_vals):.4f} "
              f"p={mw['p']:.4f} {status}{sig} -- percentiles={percentiles} {half}")

    # Pass criteria
    n_directions = results['directions_correct']
    n_significant = results['significant_count']
    n_both_half = sum(1 for t in results['tests'] if t['both_in_predicted_half'])

    results['primary_passed'] = (n_directions >= 3 and n_significant >= 1)
    results['secondary_passed'] = (n_both_half >= 3)

    if results['primary_passed'] and results['secondary_passed']:
        results['block1_verdict'] = 'APPARATUS_PROFILE_CONFIRMED'
    elif results['primary_passed']:
        results['block1_verdict'] = 'APPARATUS_PROFILE_DIRECTIONAL'
    elif n_directions >= 3:
        results['block1_verdict'] = 'APPARATUS_PROFILE_SUGGESTIVE'
    else:
        results['block1_verdict'] = 'APPARATUS_PROFILE_NOT_CONFIRMED'

    results['block1_passed'] = results['primary_passed']

    print(f"\n  Directions correct: {n_directions}/4")
    print(f"  Significant (p<0.10): {n_significant}/4")
    print(f"  Both R1 in predicted half: {n_both_half}/4")
    print(f"  BLOCK 1 VERDICT: {results['block1_verdict']}")

    return results


# =========================================================
# BLOCK 2: WITHIN-FOLIO GRADIENT TEST
# =========================================================

def build_paragraphs(folio_data):
    """Build paragraph-level features per folio."""
    folio_paragraphs = {}

    for folio, fdata in folio_data.items():
        if fdata['regime'] is None or len(fdata['tokens']) < 20:
            continue

        tokens = fdata['tokens']
        paragraphs = []
        current_para = []

        for t in tokens:
            if t['par_initial'] and current_para:
                paragraphs.append(current_para)
                current_para = [t]
            else:
                current_para.append(t)
        if current_para:
            paragraphs.append(current_para)

        if len(paragraphs) < 4:
            continue

        para_features = []
        for idx, para_tokens in enumerate(paragraphs):
            n = len(para_tokens)
            if n < 3:
                continue

            n_ey = sum(1 for t in para_tokens if t['is_ey'])
            ey_frac = n_ey / n

            e_depths = [t['e_depth'] for t in para_tokens if t['e_depth'] > 0]
            mean_e_depth = np.mean(e_depths) if e_depths else 0.0

            cats = [t['category'] for t in para_tokens if t['category']]
            n_cats = len(cats)
            thermal_frac = sum(1 for c in cats if c == 'THERMAL') / n_cats if n_cats > 0 else 0.0

            para_features.append({
                'ordinal': idx,
                'n_tokens': n,
                'ey_frac': ey_frac,
                'mean_e_depth': float(mean_e_depth),
                'thermal_frac': thermal_frac,
            })

        if len(para_features) >= 4:
            folio_paragraphs[folio] = {
                'section': fdata['section'],
                'regime': fdata['regime'],
                'paragraphs': para_features,
                'n_paragraphs': len(para_features),
            }

    return folio_paragraphs


def run_block2(folio_data):
    """Within-folio gradient tests."""
    from scipy.stats import spearmanr, ttest_1samp

    print("\n" + "=" * 60)
    print("BLOCK 2: Within-Folio Gradient Test")
    print("=" * 60)

    folio_paragraphs = build_paragraphs(folio_data)
    print(f"  {len(folio_paragraphs)} folios with 4+ paragraphs")

    results = {}

    # --- H1: No monotonic e->y gradient across paragraph ordinals ---
    folio_rhos = []
    for folio, fpdata in folio_paragraphs.items():
        paras = fpdata['paragraphs']
        ordinals = [p['ordinal'] for p in paras]
        ey_fracs = [p['ey_frac'] for p in paras]

        if len(set(ey_fracs)) < 2:
            continue

        rho, p = spearmanr(ordinals, ey_fracs)
        if not np.isnan(rho):
            folio_rhos.append(rho)

    mean_abs_rho = np.mean(np.abs(folio_rhos)) if folio_rhos else 0
    mean_rho = np.mean(folio_rhos) if folio_rhos else 0

    if len(folio_rhos) >= 5:
        t_stat, t_p = ttest_1samp(folio_rhos, 0)
    else:
        t_stat, t_p = 0, 1.0

    # H1 criterion: t-test only (is mean rho systematically nonzero?)
    # mean |rho| threshold inappropriate for small within-folio paragraph counts
    h1_passed = t_p > 0.05

    results['H1_ordinal_gradient'] = {
        'test': 'H1_no_monotonic_ey_gradient',
        'mean_abs_rho': round(float(mean_abs_rho), 4),
        'mean_rho': round(float(mean_rho), 4),
        'n_folios_tested': len(folio_rhos),
        't_statistic': round(float(t_stat), 4),
        't_p_value': round(float(t_p), 6),
        'passed': bool(h1_passed),
        'note': 'PASSES if no systematic gradient (confirms C1399/C1400 paragraph ordering null)',
    }

    status = 'PASS' if h1_passed else 'FAIL'
    print(f"\n  H1 (no ordinal gradient): {status}")
    print(f"    mean |rho| = {mean_abs_rho:.4f}, mean rho = {mean_rho:.4f}")
    print(f"    t-test: t={t_stat:.3f}, p={t_p:.4f} (n={len(folio_rhos)} folios)")

    # --- H2: THERMAL-enriched paragraphs have higher e->y ---
    ey_deviations = []
    thermal_deviations = []

    for folio, fpdata in folio_paragraphs.items():
        paras = fpdata['paragraphs']
        folio_mean_ey = np.mean([p['ey_frac'] for p in paras])
        folio_mean_th = np.mean([p['thermal_frac'] for p in paras])

        for p in paras:
            ey_deviations.append(p['ey_frac'] - folio_mean_ey)
            thermal_deviations.append(p['thermal_frac'] - folio_mean_th)

    if len(ey_deviations) >= 10:
        rho_h2, p_h2 = spearmanr(thermal_deviations, ey_deviations)
    else:
        rho_h2, p_h2 = 0, 1.0

    h2_passed = rho_h2 > 0 and p_h2 < 0.01

    results['H2_thermal_ey'] = {
        'test': 'H2_thermal_ey_within_folio',
        'spearman_rho': round(float(rho_h2), 4),
        'p_value': round(float(p_h2), 6),
        'n_paragraphs': len(ey_deviations),
        'n_folios': len(folio_paragraphs),
        'passed': bool(h2_passed),
        'note': 'Within-folio deviations: THERMAL-enriched paras should have higher e->y rate',
    }

    status = 'PASS' if h2_passed else 'FAIL'
    print(f"\n  H2 (THERMAL -> e->y within-folio): {status}")
    print(f"    rho = {rho_h2:.4f}, p = {p_h2:.6f} (n={len(ey_deviations)} paragraphs)")

    # --- H3: ke-depth correlates with thermal fraction within folio ---
    ke_deviations = []
    thermal_devs_h3 = []

    for folio, fpdata in folio_paragraphs.items():
        paras = fpdata['paragraphs']
        folio_mean_ke = np.mean([p['mean_e_depth'] for p in paras])
        folio_mean_th = np.mean([p['thermal_frac'] for p in paras])

        for p in paras:
            ke_deviations.append(p['mean_e_depth'] - folio_mean_ke)
            thermal_devs_h3.append(p['thermal_frac'] - folio_mean_th)

    if len(ke_deviations) >= 10:
        rho_h3, p_h3 = spearmanr(thermal_devs_h3, ke_deviations)
    else:
        rho_h3, p_h3 = 0, 1.0

    h3_passed = rho_h3 > 0 and p_h3 < 0.05

    results['H3_thermal_ke'] = {
        'test': 'H3_thermal_ke_within_folio',
        'spearman_rho': round(float(rho_h3), 4),
        'p_value': round(float(p_h3), 6),
        'n_paragraphs': len(ke_deviations),
        'n_folios': len(folio_paragraphs),
        'passed': bool(h3_passed),
        'note': 'Within-folio deviations: THERMAL-enriched paras should have deeper ke engagement',
    }

    status = 'PASS' if h3_passed else 'FAIL'
    print(f"\n  H3 (THERMAL -> ke-depth within-folio): {status}")
    print(f"    rho = {rho_h3:.4f}, p = {p_h3:.6f} (n={len(ke_deviations)} paragraphs)")

    # Block 2 verdict: H1 must pass, then at least one of H2/H3
    if not h1_passed:
        block2_verdict = 'STRUCTURAL_INCONSISTENCY'
        block2_passed = False
    elif h2_passed or h3_passed:
        block2_verdict = 'WITHIN_FOLIO_GRADIENT_CONFIRMED'
        block2_passed = True
    else:
        block2_verdict = 'WITHIN_FOLIO_GRADIENT_NOT_CONFIRMED'
        block2_passed = False

    results['block2_passed'] = block2_passed
    results['block2_verdict'] = block2_verdict

    print(f"\n  BLOCK 2 VERDICT: {block2_verdict}")
    return results


def main():
    import time
    t0 = time.time()

    print("Phase 598d: Follow-up Apparatus Profile + Gradient Tests")
    print("=" * 60)

    print("\nAssembling B token data...")
    folio_data = assemble_data()
    n_folios = len(folio_data)
    n_tokens = sum(len(f['tokens']) for f in folio_data.values())
    print(f"  {n_folios} folios, {n_tokens} tokens")

    # Block 1
    block1 = run_block1(folio_data)

    # Block 2
    block2 = run_block2(folio_data)

    elapsed = time.time() - t0

    # Combined verdict
    b1 = block1.get('block1_passed', False)
    b2 = block2.get('block2_passed', False)

    if b1 and b2:
        combined = 'DUAL_CONFIRMATION'
    elif b1 or b2:
        combined = 'PARTIAL_CONFIRMATION'
    else:
        combined = 'NO_CONFIRMATION'

    print("\n" + "=" * 60)
    print(f"COMBINED VERDICT: {combined}")
    print(f"  Block 1 (apparatus profile within Herbal): {block1.get('block1_verdict')}")
    print(f"  Block 2 (within-folio gradient): {block2.get('block2_verdict')}")
    print(f"  Runtime: {elapsed:.1f}s")

    output = {
        'metadata': {
            'phase': '598d',
            'prediction_hash': 'ddeee7f7252ff378b7a1ca0b964f6d38b433f7ec0f90ab17526a383b36ef058d',
            'n_b_tokens': n_tokens,
            'n_folios': n_folios,
            'runtime_seconds': round(elapsed, 1),
        },
        'block1_apparatus': block1,
        'block2_gradient': block2,
        'combined_verdict': combined,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nWrote results to {OUT_PATH}")


if __name__ == '__main__':
    main()
