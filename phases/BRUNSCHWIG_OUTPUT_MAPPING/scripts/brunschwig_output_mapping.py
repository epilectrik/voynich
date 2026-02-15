"""
Phase 362: Brunschwig-Voynich Output Parameter Mapping (F-BRU-028)

Tests whether output-side parameters correlate across Brunschwig recipes and
Voynich B folios within matched REGIMEs. Three-tier analysis:
  Tier 1: Cross-REGIME gradient correlation (Spearman rho on 4 REGIME medians)
  Tier 2: Within-REGIME_1 distributional shape (KS two-sample test)
  Tier 3: Correlation structure comparison (Mantel test on 5x5 matrices)

Distinct from F-BRU-022 (individual recipe triangulation, NEGATIVE):
  F-BRU-022 tested 1:1 recipe->folio mapping.
  This tests aggregate distributional shapes/gradients at REGIME level.
"""

import json
import math
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

# ── Paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

AXM_RESULTS = ROOT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' / 'axm_residual_decomposition.json'
REGIME_ASSIGNMENTS = ROOT / 'phases' / 'OPS2_control_strategy_clustering' / 'ops2_folio_cluster_assignments.json'
CLASS_TOKEN_MAP = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
MASTER_PATH = ROOT / 'data' / 'brunschwig_materials_master.json'
CURATED_V3_PATH = ROOT / 'data' / 'brunschwig_curated_v3.json'
RESULTS_DIR = ROOT / 'phases' / 'BRUNSCHWIG_OUTPUT_MAPPING' / 'results'
RESULTS_PATH = RESULTS_DIR / 'brunschwig_output_mapping.json'


# ── JSON encoder for numpy types ───────────────────────────────────────
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


# ═══════════════════════════════════════════════════════════════════════
# S1: Load Voynich per-folio data
# ═══════════════════════════════════════════════════════════════════════
def load_voynich_data():
    """Load per-folio output parameters + REGIME assignments."""
    # Load AXM residual decomposition (has most per-folio metrics)
    with open(AXM_RESULTS) as f:
        axm = json.load(f)

    # Load REGIME assignments (83 folios, all Currier B)
    with open(REGIME_ASSIGNMENTS) as f:
        regimes = json.load(f)['assignments']

    # Load class token map for instruction class diversity
    with open(CLASS_TOKEN_MAP) as f:
        class_map = json.load(f)['token_to_class']

    # Build per-folio class count from class_token_map
    # Need transcript to map tokens to folios
    from scripts.voynich import Transcript, Morphology
    tx = Transcript()
    morph = Morphology()

    # Count unique MIDDLEs and unique instruction classes per folio
    folio_middles = {}
    folio_classes = {}
    for token in tx.currier_b():
        folio = token.folio
        if folio not in folio_middles:
            folio_middles[folio] = set()
            folio_classes[folio] = set()
        # MIDDLE diversity
        m = morph.extract(token.word)
        if m and m.middle:
            folio_middles[folio].add(m.middle)
        # Instruction class diversity
        if token.word in class_map:
            folio_classes[folio].add(class_map[token.word])

    # Build unified folio table
    folio_data = axm['folio_data']
    voynich_rows = []
    for folio_id, fd in folio_data.items():
        regime = fd.get('regime') or regimes.get(folio_id, {}).get('cluster_id')
        if not regime:
            continue
        voynich_rows.append({
            'folio': folio_id,
            'regime': regime,
            'axm_self': fd['axm_self'],
            'prefix_entropy': fd['prefix_entropy'],
            'n_tokens': fd['n_tokens'],
            'line_count': fd['line_count'],
            'hazard_density': fd['hazard_density'],
            'middle_diversity': len(folio_middles.get(folio_id, set())),
            'instruction_class_count': len(folio_classes.get(folio_id, set())),
        })

    print(f"S1: Loaded {len(voynich_rows)} Voynich folios with 7 output parameters + REGIME")
    regime_counts = Counter(r['regime'] for r in voynich_rows)
    for reg in sorted(regime_counts):
        print(f"    {reg}: N={regime_counts[reg]}")
    return voynich_rows


# ═══════════════════════════════════════════════════════════════════════
# S2: Load Brunschwig per-recipe data
# ═══════════════════════════════════════════════════════════════════════
def load_brunschwig_data():
    """Load per-recipe output parameters from master + curated v3."""
    with open(MASTER_PATH, encoding='utf-8') as f:
        master = json.load(f)
    with open(CURATED_V3_PATH, encoding='utf-8') as f:
        curated = json.load(f)

    # Build v3 lookup by source line start for matching
    v3_by_line = {}
    for recipe in curated['recipes']:
        sl = recipe.get('source_lines', {})
        start = sl.get('start')
        if start is not None:
            v3_by_line[start] = recipe

    # Extract application diversity from v3 uses_summary
    APPLICATION_KEYWORDS = {
        'oral': ['getrunck', 'trinck', 'mund', 'drink', 'oral', 'swallow', 'eaten',
                 'gargle', 'gurgeln'],
        'topical': ['gestrichen', 'salb', 'wash', 'bath', 'bad', 'anoint',
                    'applied', 'skin', 'wound', 'sore', 'burn', 'rub',
                    'blemish', 'itch', 'scab', 'ulcer'],
        'compress': ['tuch', 'compress', 'cloth', 'umschlag', 'poultice', 'plaster'],
        'ear': ['ear', 'ohr', 'ohren'],
        'eye': ['eye', 'aug', 'augen', 'sight', 'clarity'],
        'nasal': ['nose', 'nas', 'nasen', 'smell', 'sniff'],
        'internal_organ': ['liver', 'kidney', 'spleen', 'bladder', 'stomach',
                          'lung', 'breast', 'heart', 'womb', 'uterus'],
    }

    def compute_app_diversity(uses_summary):
        """Count number of distinct application categories in uses_summary."""
        if not uses_summary:
            return 0
        text = uses_summary.lower()
        count = 0
        for cat, keywords in APPLICATION_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                count += 1
        return count

    # Build rows
    brunschwig_rows = []
    matched_v3 = 0
    for mat in master['materials']:
        regime = mat.get('predicted_regime')
        if not regime:
            continue

        # Base fields from master
        row = {
            'recipe_id': mat['recipe_id'],
            'name': mat.get('name_normalized', mat.get('name_german', '')),
            'regime': regime,
            'use_count': mat.get('uses_count', 0),
            'step_count': len(mat.get('procedural_steps', [])),
            'text_length': mat.get('entry_text_length', 0),
        }

        # Try to match v3 recipe by source line
        master_line = mat.get('source_reference', {}).get('line_start')
        v3_match = None
        if master_line:
            # Try exact match first, then ±5
            for offset in range(0, 6):
                for sign in [0, 1, -1]:
                    check = master_line + sign * offset
                    if check in v3_by_line:
                        v3_match = v3_by_line[check]
                        break
                if v3_match:
                    break

        if v3_match:
            matched_v3 += 1
            # Action diversity from procedural steps
            steps = v3_match.get('procedural_steps') or []
            actions = set()
            for s in steps:
                a = s.get('action')
                if a:
                    actions.add(a)
            row['action_diversity'] = len(actions)
            # Application diversity from uses_summary
            row['app_diversity'] = compute_app_diversity(v3_match.get('uses_summary'))
        else:
            row['action_diversity'] = np.nan
            row['app_diversity'] = np.nan

        brunschwig_rows.append(row)

    print(f"S2: Loaded {len(brunschwig_rows)} Brunschwig recipes with output parameters")
    print(f"    Matched to v3: {matched_v3}/{len(brunschwig_rows)}")
    regime_counts = Counter(r['regime'] for r in brunschwig_rows)
    for reg in sorted(regime_counts):
        print(f"    {reg}: N={regime_counts[reg]}")

    # Report parameter stats
    for param in ['use_count', 'step_count', 'text_length', 'action_diversity', 'app_diversity']:
        vals = [r[param] for r in brunschwig_rows if not (isinstance(r[param], float) and np.isnan(r[param]))]
        if vals:
            print(f"    {param}: min={min(vals)}, max={max(vals)}, median={np.median(vals):.1f}, N_valid={len(vals)}")

    return brunschwig_rows


# ═══════════════════════════════════════════════════════════════════════
# S3: Compute REGIME-level medians
# ═══════════════════════════════════════════════════════════════════════
def compute_regime_medians(voynich_rows, brunschwig_rows):
    """Compute median of each parameter per REGIME on both sides."""
    regimes = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']

    # Voynich parameters (output-side free parameters)
    voynich_params = ['axm_self', 'prefix_entropy', 'n_tokens', 'line_count',
                      'hazard_density', 'middle_diversity', 'instruction_class_count']

    # Brunschwig parameters (output-side)
    brunschwig_params = ['use_count', 'app_diversity', 'text_length',
                         'step_count', 'action_diversity']

    voynich_medians = {}
    brunschwig_medians = {}
    voynich_ns = {}
    brunschwig_ns = {}

    for reg in regimes:
        v_rows = [r for r in voynich_rows if r['regime'] == reg]
        b_rows = [r for r in brunschwig_rows if r['regime'] == reg]

        voynich_ns[reg] = len(v_rows)
        brunschwig_ns[reg] = len(b_rows)

        # Voynich medians
        voynich_medians[reg] = {}
        for param in voynich_params:
            vals = [r[param] for r in v_rows]
            voynich_medians[reg][param] = float(np.median(vals)) if vals else np.nan

        # Brunschwig medians
        brunschwig_medians[reg] = {}
        for param in brunschwig_params:
            vals = [r[param] for r in b_rows
                    if not (isinstance(r[param], float) and np.isnan(r[param]))]
            brunschwig_medians[reg][param] = float(np.median(vals)) if vals else np.nan

    print("\nS3: REGIME-level medians")
    print(f"{'REGIME':<12} {'Voynich N':>10} {'Brunschwig N':>13}")
    for reg in regimes:
        print(f"{reg:<12} {voynich_ns[reg]:>10} {brunschwig_ns[reg]:>13}")

    print("\n  Voynich REGIME medians:")
    header = f"  {'Param':<28}" + "".join(f"{reg:>12}" for reg in regimes)
    print(header)
    for param in voynich_params:
        vals = [f"{voynich_medians[reg][param]:>12.3f}" for reg in regimes]
        print(f"  {param:<28}" + "".join(vals))

    print("\n  Brunschwig REGIME medians:")
    header = f"  {'Param':<28}" + "".join(f"{reg:>12}" for reg in regimes)
    print(header)
    for param in brunschwig_params:
        vals = []
        for reg in regimes:
            v = brunschwig_medians[reg][param]
            if np.isnan(v):
                vals.append(f"{'NaN':>12}")
            else:
                vals.append(f"{v:>12.1f}")
        print(f"  {param:<28}" + "".join(vals))

    return voynich_medians, brunschwig_medians, voynich_ns, brunschwig_ns


# ═══════════════════════════════════════════════════════════════════════
# S4: Cross-REGIME gradient test (Tier 1)
# ═══════════════════════════════════════════════════════════════════════
def cross_regime_gradient_test(voynich_medians, brunschwig_medians):
    """
    For each pre-registered parameter pairing, compute Spearman rho
    across 4 REGIME medians. Also count directional rank matches.
    """
    regimes = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']

    # Pre-registered pairings: (ID, bru_param, voy_param, expected_positive)
    pairings = [
        ('OUT-1', 'use_count', 'axm_self', True),
        ('OUT-2', 'app_diversity', 'prefix_entropy', True),
        ('OUT-3', 'text_length', 'n_tokens', True),
        ('OUT-4', 'step_count', 'line_count', True),
        ('OUT-5', 'action_diversity', 'instruction_class_count', True),
        ('NULL-1', 'use_count', 'hazard_density', False),
    ]

    results = []
    print("\nS4: Cross-REGIME gradient test (Tier 1)")
    print(f"{'ID':<8} {'Bru param':<22} {'Voy param':<28} {'rho':>6} {'direction':>10} {'rank_match':>11} {'pass':>6}")

    for pair_id, bru_param, voy_param, expect_positive in pairings:
        bru_vals = [brunschwig_medians[reg][bru_param] for reg in regimes]
        voy_vals = [voynich_medians[reg][voy_param] for reg in regimes]

        # Skip if any NaN
        valid = [(b, v) for b, v in zip(bru_vals, voy_vals)
                 if not (np.isnan(b) or np.isnan(v))]

        if len(valid) < 3:
            results.append({
                'id': pair_id, 'bru_param': bru_param, 'voy_param': voy_param,
                'rho': np.nan, 'p_value': np.nan, 'direction': 'INSUFFICIENT',
                'rank_match': 0, 'n_valid': len(valid), 'pass': False,
                'expect_positive': expect_positive,
            })
            print(f"{pair_id:<8} {bru_param:<22} {voy_param:<28} {'N/A':>6} {'INSUF':>10} {'N/A':>11} {'SKIP':>6}")
            continue

        bru_v, voy_v = zip(*valid)
        rho, p = stats.spearmanr(bru_v, voy_v)

        # Rank match: count how many adjacent pairs have same direction
        bru_ranks = stats.rankdata(bru_v)
        voy_ranks = stats.rankdata(voy_v)
        rank_matches = sum(1 for i in range(len(bru_ranks) - 1)
                          if (bru_ranks[i+1] - bru_ranks[i]) * (voy_ranks[i+1] - voy_ranks[i]) > 0)
        total_pairs = len(bru_ranks) - 1

        direction = 'POSITIVE' if rho > 0 else 'NEGATIVE' if rho < 0 else 'ZERO'

        if expect_positive:
            passed = rho > 0
        else:
            passed = abs(rho) < 0.5

        results.append({
            'id': pair_id, 'bru_param': bru_param, 'voy_param': voy_param,
            'rho': float(rho), 'p_value': float(p),
            'direction': direction,
            'rank_match': f"{rank_matches}/{total_pairs}",
            'n_valid': len(valid), 'pass': passed,
            'expect_positive': expect_positive,
            'bru_medians': list(bru_v),
            'voy_medians': list(voy_v),
        })

        pass_str = 'PASS' if passed else 'FAIL'
        print(f"{pair_id:<8} {bru_param:<22} {voy_param:<28} {rho:>6.3f} {direction:>10} {rank_matches}/{total_pairs:>9} {pass_str:>6}")

    # Global verdict
    positive_pass = sum(1 for r in results if r['expect_positive'] and r['pass'])
    null_pass = all(r['pass'] for r in results if not r['expect_positive'])
    global_pass = positive_pass >= 3 and null_pass

    print(f"\n  Positive pairs passing: {positive_pass}/5 (need >= 3)")
    print(f"  Null pair passing: {null_pass}")
    print(f"  TIER 1 GLOBAL: {'PASS' if global_pass else 'FAIL'}")

    return results, global_pass


# ═══════════════════════════════════════════════════════════════════════
# S5: Within-REGIME_1 shape test (Tier 2)
# ═══════════════════════════════════════════════════════════════════════
def within_regime1_shape_test(voynich_rows, brunschwig_rows):
    """
    KS two-sample test on normalized CDFs within REGIME_1.
    Both parameters scaled to [0,1] before comparison (tests shape, not scale).
    """
    v_r1 = [r for r in voynich_rows if r['regime'] == 'REGIME_1']
    b_r1 = [r for r in brunschwig_rows if r['regime'] == 'REGIME_1']

    ks_tests = [
        ('KS-1', 'use_count', 'axm_self'),
        ('KS-2', 'text_length', 'n_tokens'),
    ]

    results = []
    print(f"\nS5: Within-REGIME_1 shape test (Tier 2)")
    print(f"    Voynich REGIME_1 N={len(v_r1)}, Brunschwig REGIME_1 N={len(b_r1)}")

    for ks_id, bru_param, voy_param in ks_tests:
        bru_vals = np.array([r[bru_param] for r in b_r1
                             if not (isinstance(r[bru_param], float) and np.isnan(r[bru_param]))])
        voy_vals = np.array([r[voy_param] for r in v_r1])

        # Normalize to [0,1]
        def normalize(arr):
            mn, mx = arr.min(), arr.max()
            if mx == mn:
                return np.zeros_like(arr)
            return (arr - mn) / (mx - mn)

        bru_norm = normalize(bru_vals.astype(float))
        voy_norm = normalize(voy_vals.astype(float))

        ks_stat, ks_p = stats.ks_2samp(bru_norm, voy_norm)
        passed = ks_p > 0.05

        results.append({
            'id': ks_id, 'bru_param': bru_param, 'voy_param': voy_param,
            'ks_statistic': float(ks_stat), 'ks_p': float(ks_p),
            'bru_n': len(bru_vals), 'voy_n': len(voy_vals),
            'pass': passed,
            'bru_stats': {'mean': float(bru_norm.mean()), 'std': float(bru_norm.std()),
                          'median': float(np.median(bru_norm))},
            'voy_stats': {'mean': float(voy_norm.mean()), 'std': float(voy_norm.std()),
                          'median': float(np.median(voy_norm))},
        })

        pass_str = 'PASS' if passed else 'FAIL'
        print(f"    {ks_id}: {bru_param} vs {voy_param}")
        print(f"      KS stat={ks_stat:.4f}, p={ks_p:.4f} -> {pass_str}")
        print(f"      Bru [0,1]: mean={bru_norm.mean():.3f}, std={bru_norm.std():.3f}")
        print(f"      Voy [0,1]: mean={voy_norm.mean():.3f}, std={voy_norm.std():.3f}")

    tier2_pass = all(r['pass'] for r in results)
    print(f"  TIER 2: {'PASS' if tier2_pass else 'FAIL'}")
    return results, tier2_pass


# ═══════════════════════════════════════════════════════════════════════
# S6: Correlation structure test (Tier 3)
# ═══════════════════════════════════════════════════════════════════════
def correlation_structure_test(voynich_rows, brunschwig_rows):
    """
    Compute 5x5 Spearman correlation matrix on each side.
    Compare via Mantel test (correlate vectorized upper triangles).
    """
    # Voynich output parameters (5 selected)
    voy_params = ['axm_self', 'prefix_entropy', 'n_tokens', 'line_count',
                  'instruction_class_count']
    # Brunschwig output parameters (5 matched)
    bru_params = ['use_count', 'app_diversity', 'text_length',
                  'step_count', 'action_diversity']

    # Build matrices — only use rows with complete data
    # Voynich: all rows have complete data
    voy_matrix = np.array([[r[p] for p in voy_params] for r in voynich_rows])

    # Brunschwig: filter to rows with non-NaN app_diversity and action_diversity
    bru_complete = [r for r in brunschwig_rows
                    if not (isinstance(r['app_diversity'], float) and np.isnan(r['app_diversity']))
                    and not (isinstance(r['action_diversity'], float) and np.isnan(r['action_diversity']))]
    bru_matrix = np.array([[r[p] for p in bru_params] for r in bru_complete])

    print(f"\nS6: Correlation structure test (Tier 3)")
    print(f"    Voynich: {voy_matrix.shape[0]} folios x {len(voy_params)} params")
    print(f"    Brunschwig: {bru_matrix.shape[0]} recipes x {len(bru_params)} params (complete data only)")

    # Compute Spearman correlation matrices
    voy_corr = np.zeros((len(voy_params), len(voy_params)))
    for i in range(len(voy_params)):
        for j in range(len(voy_params)):
            rho, _ = stats.spearmanr(voy_matrix[:, i], voy_matrix[:, j])
            voy_corr[i, j] = rho

    bru_corr = np.zeros((len(bru_params), len(bru_params)))
    for i in range(len(bru_params)):
        for j in range(len(bru_params)):
            rho, _ = stats.spearmanr(bru_matrix[:, i], bru_matrix[:, j])
            bru_corr[i, j] = rho

    # Print correlation matrices
    print("\n  Voynich correlation matrix:")
    header = "  " + f"{'':>28}" + "".join(f"{p:>14}" for p in voy_params)
    print(header)
    for i, p in enumerate(voy_params):
        row_str = "  " + f"{p:>28}" + "".join(f"{voy_corr[i,j]:>14.3f}" for j in range(len(voy_params)))
        print(row_str)

    print("\n  Brunschwig correlation matrix:")
    header = "  " + f"{'':>28}" + "".join(f"{p:>14}" for p in bru_params)
    print(header)
    for i, p in enumerate(bru_params):
        row_str = "  " + f"{p:>28}" + "".join(f"{bru_corr[i,j]:>14.3f}" for j in range(len(bru_params)))
        print(row_str)

    # Extract upper triangles (10 values each for 5x5)
    upper_idx = np.triu_indices(len(voy_params), k=1)
    voy_upper = voy_corr[upper_idx]
    bru_upper = bru_corr[upper_idx]

    # Mantel test: Spearman correlation of upper triangle vectors
    observed_r, _ = stats.spearmanr(voy_upper, bru_upper)

    # Permutation null: shuffle one triangle, recompute 1000 times
    np.random.seed(42)
    n_perms = 1000
    perm_rs = []
    for _ in range(n_perms):
        shuffled = np.random.permutation(bru_upper)
        r_perm, _ = stats.spearmanr(voy_upper, shuffled)
        perm_rs.append(r_perm)

    perm_rs = np.array(perm_rs)
    mantel_p = float(np.mean(perm_rs >= observed_r))

    passed = observed_r > 0 and mantel_p < 0.05

    print(f"\n  Mantel test:")
    print(f"    Upper triangle (Voynich): {voy_upper}")
    print(f"    Upper triangle (Bru):     {bru_upper}")
    print(f"    Observed Spearman r = {observed_r:.4f}")
    print(f"    Permutation p = {mantel_p:.4f} (N={n_perms})")
    print(f"  TIER 3: {'PASS' if passed else 'FAIL'}")

    return {
        'voynich_corr_matrix': voy_corr.tolist(),
        'brunschwig_corr_matrix': bru_corr.tolist(),
        'voynich_params': voy_params,
        'brunschwig_params': bru_params,
        'voynich_upper_triangle': voy_upper.tolist(),
        'brunschwig_upper_triangle': bru_upper.tolist(),
        'observed_mantel_r': float(observed_r),
        'mantel_p': mantel_p,
        'n_permutations': n_perms,
        'pass': passed,
        'voynich_n': int(voy_matrix.shape[0]),
        'brunschwig_n': int(bru_matrix.shape[0]),
    }, passed


# ═══════════════════════════════════════════════════════════════════════
# S7: Pooled analysis (REGIME_1+2 vs REGIME_3+4)
# ═══════════════════════════════════════════════════════════════════════
def pooled_analysis(voynich_rows, brunschwig_rows):
    """Pool REGIME_3+4 as 'specialized' vs REGIME_1+2 as 'standard'.
    Two-group comparison with better statistical power."""
    def pool_regime(regime):
        if regime in ('REGIME_1', 'REGIME_2'):
            return 'STANDARD'
        return 'SPECIALIZED'

    # Voynich pooled medians
    voy_params = ['axm_self', 'prefix_entropy', 'n_tokens', 'line_count',
                  'instruction_class_count']
    bru_params = ['use_count', 'app_diversity', 'text_length',
                  'step_count', 'action_diversity']

    pairings = [
        ('OUT-1', 'use_count', 'axm_self'),
        ('OUT-2', 'app_diversity', 'prefix_entropy'),
        ('OUT-3', 'text_length', 'n_tokens'),
        ('OUT-4', 'step_count', 'line_count'),
        ('OUT-5', 'action_diversity', 'instruction_class_count'),
    ]

    results = []
    print(f"\nS7: Pooled analysis (STANDARD=R1+R2 vs SPECIALIZED=R3+R4)")

    for pair_id, bru_param, voy_param in pairings:
        # Compute pooled medians
        bru_std = [r[bru_param] for r in brunschwig_rows
                   if pool_regime(r['regime']) == 'STANDARD'
                   and not (isinstance(r[bru_param], float) and np.isnan(r[bru_param]))]
        bru_spec = [r[bru_param] for r in brunschwig_rows
                    if pool_regime(r['regime']) == 'SPECIALIZED'
                    and not (isinstance(r[bru_param], float) and np.isnan(r[bru_param]))]
        voy_std = [r[voy_param] for r in voynich_rows
                   if pool_regime(r['regime']) == 'STANDARD']
        voy_spec = [r[voy_param] for r in voynich_rows
                    if pool_regime(r['regime']) == 'SPECIALIZED']

        if not bru_std or not bru_spec or not voy_std or not voy_spec:
            results.append({
                'id': pair_id, 'bru_param': bru_param, 'voy_param': voy_param,
                'status': 'INSUFFICIENT',
            })
            continue

        bru_diff = np.median(bru_spec) - np.median(bru_std)
        voy_diff = np.median(voy_spec) - np.median(voy_std)
        same_direction = (bru_diff > 0) == (voy_diff > 0)

        # Mann-Whitney U test for each side
        bru_u, bru_p = stats.mannwhitneyu(bru_std, bru_spec, alternative='two-sided')
        voy_u, voy_p = stats.mannwhitneyu(voy_std, voy_spec, alternative='two-sided')

        results.append({
            'id': pair_id, 'bru_param': bru_param, 'voy_param': voy_param,
            'bru_std_median': float(np.median(bru_std)),
            'bru_spec_median': float(np.median(bru_spec)),
            'bru_diff': float(bru_diff),
            'bru_mw_p': float(bru_p),
            'voy_std_median': float(np.median(voy_std)),
            'voy_spec_median': float(np.median(voy_spec)),
            'voy_diff': float(voy_diff),
            'voy_mw_p': float(voy_p),
            'same_direction': bool(same_direction),
            'bru_n': (len(bru_std), len(bru_spec)),
            'voy_n': (len(voy_std), len(voy_spec)),
        })

        dir_str = 'SAME' if same_direction else 'OPPOSITE'
        print(f"  {pair_id}: {bru_param} vs {voy_param}")
        print(f"    Bru: STD median={np.median(bru_std):.2f}, SPEC median={np.median(bru_spec):.2f}, diff={bru_diff:+.2f}, MW p={bru_p:.4f}")
        print(f"    Voy: STD median={np.median(voy_std):.3f}, SPEC median={np.median(voy_spec):.3f}, diff={voy_diff:+.3f}, MW p={voy_p:.4f}")
        print(f"    Direction: {dir_str}")

    same_count = sum(1 for r in results if r.get('same_direction', False))
    print(f"\n  Pooled: {same_count}/5 same direction")

    return results


# ═══════════════════════════════════════════════════════════════════════
# S8: Summary + verdict
# ═══════════════════════════════════════════════════════════════════════
def main():
    print("=" * 72)
    print("Phase 362: Brunschwig-Voynich Output Parameter Mapping (F-BRU-028)")
    print("=" * 72)

    # S1: Load Voynich data
    voynich_rows = load_voynich_data()

    # S2: Load Brunschwig data
    brunschwig_rows = load_brunschwig_data()

    # S3: Compute REGIME-level medians
    voy_medians, bru_medians, voy_ns, bru_ns = compute_regime_medians(
        voynich_rows, brunschwig_rows)

    # S4: Cross-REGIME gradient test (Tier 1)
    tier1_results, tier1_pass = cross_regime_gradient_test(voy_medians, bru_medians)

    # S5: Within-REGIME_1 shape test (Tier 2)
    tier2_results, tier2_pass = within_regime1_shape_test(voynich_rows, brunschwig_rows)

    # S6: Correlation structure test (Tier 3)
    tier3_results, tier3_pass = correlation_structure_test(voynich_rows, brunschwig_rows)

    # S7: Pooled analysis
    pooled_results = pooled_analysis(voynich_rows, brunschwig_rows)

    # ── Final verdict ──
    print("\n" + "=" * 72)
    print("FINAL VERDICT")
    print("=" * 72)

    positive_pass = sum(1 for r in tier1_results if r['expect_positive'] and r['pass'])
    null_pass = all(r['pass'] for r in tier1_results if not r['expect_positive'])

    print(f"  Tier 1 (Cross-REGIME gradient): {'PASS' if tier1_pass else 'FAIL'}")
    print(f"    Positive pairs: {positive_pass}/5 (need >= 3)")
    print(f"    Null pair: {'PASS' if null_pass else 'FAIL'}")
    print(f"  Tier 2 (REGIME_1 shape): {'PASS' if tier2_pass else 'FAIL'}")
    print(f"  Tier 3 (Correlation structure): {'PASS' if tier3_pass else 'FAIL'}")

    # Overall: Tier 1 is primary, Tier 2-3 are supplementary
    if tier1_pass:
        if tier3_pass:
            verdict = 'OUTPUT_GRADIENT_CONFIRMED'
            print(f"\n  VERDICT: {verdict}")
            print("  Output parameters follow the same REGIME gradient in both systems.")
            print("  Correlation structure also matches (Mantel test positive).")
        else:
            verdict = 'OUTPUT_GRADIENT_SUPPORTED'
            print(f"\n  VERDICT: {verdict}")
            print("  Output parameters follow the same REGIME gradient in both systems.")
            print("  Correlation structure does not independently confirm.")
    else:
        if positive_pass >= 2:
            verdict = 'OUTPUT_GRADIENT_WEAK'
            print(f"\n  VERDICT: {verdict}")
            print("  Some gradient alignment exists but below pre-registered threshold.")
        else:
            verdict = 'OUTPUT_GRADIENT_NEGATIVE'
            print(f"\n  VERDICT: {verdict}")
            print("  No systematic gradient alignment detected between systems.")

    # ── Write results ──
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 362,
        'fit_id': 'F-BRU-028',
        'title': 'Brunschwig-Voynich Output Parameter Mapping',
        'voynich_n_folios': len(voynich_rows),
        'brunschwig_n_recipes': len(brunschwig_rows),
        'regime_counts': {
            'voynich': dict(voy_ns),
            'brunschwig': dict(bru_ns),
        },
        'regime_medians': {
            'voynich': voy_medians,
            'brunschwig': bru_medians,
        },
        'tier1_gradient': {
            'results': tier1_results,
            'global_pass': tier1_pass,
            'positive_passing': positive_pass,
            'null_passing': null_pass,
        },
        'tier2_shape': {
            'results': tier2_results,
            'global_pass': tier2_pass,
        },
        'tier3_mantel': tier3_results,
        'pooled_analysis': pooled_results,
        'verdict': verdict,
    }

    with open(RESULTS_PATH, 'w') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults written to {RESULTS_PATH}")


if __name__ == '__main__':
    main()
