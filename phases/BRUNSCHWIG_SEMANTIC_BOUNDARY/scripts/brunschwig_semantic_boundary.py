"""
Phase 363: Brunschwig-Voynich Semantic Boundary Probe (F-BRU-029)

Three-path probe of remaining Tier 4 semantic mapping possibilities:
  Path A: Hazard class thermodynamic signatures (buffer profiles per class)
  Path B: Process-side REGIME gradient (clamped envelope match)
  Path C: Operational manifold axis alignment (PCA structure comparison)
"""

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# ── Paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

BUFFER_SCAN = ROOT / 'phases' / 'BIN_HAZARD_NECESSITY' / 'results' / 'safety_buffer_scan.json'
FORBIDDEN_THERMO = ROOT / 'phases' / 'FORBIDDEN_TRANSITION_THERMODYNAMICS' / 'results' / 'forbidden_transition_thermodynamics.json'
AXM_RESULTS = ROOT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' / 'axm_residual_decomposition.json'
REGIME_ASSIGNMENTS = ROOT / 'phases' / 'OPS2_control_strategy_clustering' / 'ops2_folio_cluster_assignments.json'
MASTER_PATH = ROOT / 'data' / 'brunschwig_materials_master.json'
CURATED_V3_PATH = ROOT / 'data' / 'brunschwig_curated_v3.json'
VOYNICH_PCA = ROOT / 'phases' / 'BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS' / 'results' / 'multidimensional_pca.json'
RESULTS_DIR = ROOT / 'phases' / 'BRUNSCHWIG_SEMANTIC_BOUNDARY' / 'results'
RESULTS_PATH = RESULTS_DIR / 'brunschwig_semantic_boundary.json'


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


# ── Pair-to-class mapping (from F-BRU-023 / C109) ─────────────────────
# Source: forbidden_transition_thermodynamics.json T1 pairs
PAIR_TO_CLASS = {
    'shey -> aiin': 'PHASE_ORDERING',
    'shey -> al': 'PHASE_ORDERING',
    'shey -> c': 'PHASE_ORDERING',
    'dy -> aiin': 'PHASE_ORDERING',
    'dy -> chey': 'PHASE_ORDERING',
    'chey -> chedy': 'PHASE_ORDERING',
    'chey -> shedy': 'PHASE_ORDERING',
    'chol -> r': 'CONTAINMENT_TIMING',
    'l -> chol': 'CONTAINMENT_TIMING',
    'or -> dal': 'CONTAINMENT_TIMING',
    'he -> or': 'CONTAINMENT_TIMING',
    'chedy -> ee': 'COMPOSITION_JUMP',
    'c -> ee': 'COMPOSITION_JUMP',
    'shedy -> aiin': 'COMPOSITION_JUMP',
    'shedy -> o': 'COMPOSITION_JUMP',
    'ar -> dal': 'RATE_MISMATCH',
    'he -> t': 'ENERGY_OVERSHOOT',
}

# ── Action-to-phase mapping (from curated v3 action_taxonomy) ──────────
ACTION_TO_PHASE = {
    'GATHER': 'COLLECTION', 'SELECT': 'COLLECTION',
    'CHOP': 'PREPARATION', 'STRIP': 'PREPARATION', 'POUND': 'PREPARATION',
    'CRUSH': 'PREPARATION', 'BREAK': 'PREPARATION', 'PLUCK': 'PREPARATION',
    'BORE': 'PREPARATION', 'WASH': 'PREPARATION', 'KILL': 'PREPARATION',
    'CLEAN': 'PREPARATION', 'POWDER': 'PREPARATION', 'GRIND': 'PREPARATION',
    'MACERATE': 'PRETREATMENT', 'DRY': 'PRETREATMENT', 'FERMENT': 'PRETREATMENT',
    'DIGEST': 'PRETREATMENT', 'MIX': 'PRETREATMENT',
    'DISTILL': 'DISTILLATION', 'REDISTILL': 'DISTILLATION',
    'SEAL': 'MIDPROCESS', 'REGULATE': 'MIDPROCESS', 'MONITOR_DRIPS': 'MIDPROCESS',
    'MONITOR_TEMP': 'MIDPROCESS', 'REPLENISH': 'MIDPROCESS', 'COOL': 'MIDPROCESS',
    'STRAIN': 'POSTPROCESS', 'FILTER': 'POSTPROCESS', 'RECTIFY': 'POSTPROCESS',
    'SETTLE': 'POSTPROCESS', 'POUR': 'POSTPROCESS', 'COLLECT': 'POSTPROCESS',
    'MELT': 'POSTPROCESS',
    'SEAL_VESSEL': 'STORAGE', 'LABEL': 'STORAGE', 'STORE': 'STORAGE',
    'RENEW': 'STORAGE', 'STEEP': 'PRETREATMENT',
}

PHASE_ORDER = ['COLLECTION', 'PREPARATION', 'PRETREATMENT', 'DISTILLATION',
               'MIDPROCESS', 'POSTPROCESS', 'STORAGE']

# REGIME-to-degree mapping: Degree 1→REGIME_2, 2→REGIME_1, 3→REGIME_3, 4→REGIME_4
DEGREE_TO_REGIME = {1: 'REGIME_2', 2: 'REGIME_1', 3: 'REGIME_3', 4: 'REGIME_4'}
REGIME_TO_DEGREE = {v: k for k, v in DEGREE_TO_REGIME.items()}


# ═══════════════════════════════════════════════════════════════════════
# S1: Load all data
# ═══════════════════════════════════════════════════════════════════════
def load_all_data():
    with open(BUFFER_SCAN, encoding='utf-8') as f:
        buffers = json.load(f)
    with open(FORBIDDEN_THERMO, encoding='utf-8') as f:
        thermo = json.load(f)
    with open(AXM_RESULTS, encoding='utf-8') as f:
        axm = json.load(f)
    with open(REGIME_ASSIGNMENTS, encoding='utf-8') as f:
        regimes = json.load(f)['assignments']
    with open(MASTER_PATH, encoding='utf-8') as f:
        master = json.load(f)
    with open(CURATED_V3_PATH, encoding='utf-8') as f:
        curated = json.load(f)
    with open(VOYNICH_PCA, encoding='utf-8') as f:
        voy_pca = json.load(f)

    print("S1: All data loaded")
    print(f"    Buffers: {buffers['n_buffers']}")
    print(f"    Forbidden pairs prevented: {len(buffers['forbidden_pairs_prevented'])}")
    print(f"    Thermo glossed pairs: {thermo['tests']['T1']['classifiable']}")
    print(f"    Voynich folios: {len(axm['folio_data'])}")
    print(f"    Brunschwig materials: {master['summary']['total_materials']}")
    print(f"    Curated v3 recipes: {len(curated['recipes'])}")
    print(f"    Voynich PCA features: {voy_pca['n_features']}")

    return buffers, thermo, axm, regimes, master, curated, voy_pca


# ═══════════════════════════════════════════════════════════════════════
# S2: Path A — Buffer profile per hazard class
# ═══════════════════════════════════════════════════════════════════════
def path_a_buffer_profiles(buffers, thermo):
    """Group safety buffers by hazard class and compute PREFIX/MIDDLE profiles."""
    from scripts.voynich import Morphology
    morph = Morphology()

    print("\n" + "=" * 72)
    print("PATH A: Hazard Class Thermodynamic Signatures")
    print("=" * 72)

    safety_buffers = buffers['safety_buffers']
    print(f"\nTotal safety buffers: {len(safety_buffers)}")

    # Map each buffer to its hazard class via forbidden pair
    class_buffers = defaultdict(list)
    for buf in safety_buffers:
        pair = buf['forbidden_pair']
        hclass = PAIR_TO_CLASS.get(pair, 'UNKNOWN')
        m = morph.extract(buf['token'])
        prefix = 'none'
        if m:
            if m.articulator:
                prefix = m.articulator
            elif m.prefix:
                prefix = m.prefix
        class_buffers[hclass].append({
            'token': buf['token'],
            'middle': buf['middle'],
            'prefix': prefix,
            'pair': pair,
            'folio': buf['folio'],
        })

    # Report
    all_classes = ['PHASE_ORDERING', 'COMPOSITION_JUMP', 'CONTAINMENT_TIMING',
                   'RATE_MISMATCH', 'ENERGY_OVERSHOOT']

    print("\n  Buffers per hazard class:")
    prefix_by_class = {}
    for hclass in all_classes:
        bufs = class_buffers.get(hclass, [])
        prefix_counts = Counter(b['prefix'] for b in bufs)
        middle_counts = Counter(b['middle'] for b in bufs)
        prefix_by_class[hclass] = prefix_counts
        print(f"\n  {hclass}: {len(bufs)} buffers")
        if bufs:
            print(f"    PREFIX profile: {dict(prefix_counts)}")
            print(f"    MIDDLE profile: {dict(middle_counts)}")
            for b in bufs:
                print(f"      {b['token']} (prefix={b['prefix']}) prevents {b['pair']} in {b['folio']}")

    # A-1: PREFIX profiles differ across classes
    # Build contingency table: classes with buffers × prefix categories
    classes_with_buffers = [c for c in all_classes if len(class_buffers.get(c, [])) > 0]
    all_prefixes = sorted(set(
        b['prefix'] for c in classes_with_buffers for b in class_buffers[c]
    ))

    print(f"\n  A-1: PREFIX profile independence test")
    print(f"    Classes with buffers: {classes_with_buffers}")
    print(f"    PREFIX categories: {all_prefixes}")

    if len(classes_with_buffers) >= 2 and len(all_prefixes) >= 2:
        contingency = np.zeros((len(classes_with_buffers), len(all_prefixes)), dtype=int)
        for i, c in enumerate(classes_with_buffers):
            for b in class_buffers[c]:
                j = all_prefixes.index(b['prefix'])
                contingency[i, j] += 1

        print(f"    Contingency table:")
        header = f"    {'Class':<24}" + "".join(f"{p:>8}" for p in all_prefixes) + f"{'Total':>8}"
        print(header)
        for i, c in enumerate(classes_with_buffers):
            row = f"    {c:<24}" + "".join(f"{contingency[i,j]:>8}" for j in range(len(all_prefixes))) + f"{contingency[i].sum():>8}"
            print(row)

        # Fisher's exact or chi-squared (use Fisher for small expected counts)
        # Since expected counts are very small, use Fisher's exact for 2x2
        # or report chi-squared with caveat
        if contingency.shape[0] == 2 and contingency.shape[1] == 2:
            odds, fisher_p = stats.fisher_exact(contingency)
            a1_p = float(fisher_p)
            a1_test = 'fisher_exact'
        else:
            chi2, chi_p, dof, expected = stats.chi2_contingency(contingency)
            a1_p = float(chi_p)
            a1_test = 'chi2'
            min_expected = expected.min()
            print(f"    Chi2={chi2:.3f}, p={chi_p:.4f}, dof={dof}, min_expected={min_expected:.2f}")
            if min_expected < 5:
                print(f"    WARNING: min expected < 5, chi-squared unreliable")

        a1_pass = a1_p < 0.05
        print(f"    A-1 RESULT: p={a1_p:.4f}, {'PASS' if a1_pass else 'FAIL'}")
    else:
        a1_pass = False
        a1_p = 1.0
        a1_test = 'insufficient_data'
        print(f"    A-1: INSUFFICIENT DATA (need >= 2 classes with buffers)")

    # A-2: Most-buffered class has the most buffers
    class_counts = {c: len(class_buffers.get(c, [])) for c in all_classes}
    # PHASE_ORDERING has 7 of 17 pairs (41%) — expect most buffers
    most_pairs = max(all_classes, key=lambda c: sum(1 for p, cl in PAIR_TO_CLASS.items() if cl == c))
    most_buffers = max(all_classes, key=lambda c: class_counts[c])
    a2_pass = most_pairs == most_buffers
    print(f"\n  A-2: Most-buffered class alignment")
    print(f"    Class with most pairs: {most_pairs} ({sum(1 for p,cl in PAIR_TO_CLASS.items() if cl==most_pairs)} pairs)")
    print(f"    Class with most buffers: {most_buffers} ({class_counts[most_buffers]} buffers)")
    print(f"    A-2 RESULT: {'PASS' if a2_pass else 'FAIL'}")

    # A-3: QO-prefixed buffers enriched in PHASE_ORDERING
    total_qo = sum(1 for c in all_classes for b in class_buffers.get(c, []) if b['prefix'] in ('qo', 'QO'))
    po_qo = sum(1 for b in class_buffers.get('PHASE_ORDERING', []) if b['prefix'] in ('qo', 'QO'))
    po_total = len(class_buffers.get('PHASE_ORDERING', []))
    other_qo = total_qo - po_qo
    other_total = len(safety_buffers) - po_total

    print(f"\n  A-3: QO enrichment in PHASE_ORDERING")
    print(f"    PHASE_ORDERING: {po_qo}/{po_total} QO-prefixed")
    print(f"    Other classes: {other_qo}/{other_total} QO-prefixed")

    if po_total > 0 and other_total > 0:
        po_qo_frac = po_qo / po_total if po_total > 0 else 0
        other_qo_frac = other_qo / other_total if other_total > 0 else 0
        # Fisher's exact on 2x2: QO/non-QO × PO/non-PO
        table = np.array([[po_qo, po_total - po_qo],
                          [other_qo, other_total - other_qo]])
        _, a3_p = stats.fisher_exact(table)
        a3_enriched = po_qo_frac > other_qo_frac
        a3_pass = a3_enriched  # directional — is QO enriched in PO?
        print(f"    QO fraction in PO: {po_qo_frac:.3f}")
        print(f"    QO fraction elsewhere: {other_qo_frac:.3f}")
        print(f"    Fisher's exact p={a3_p:.4f}")
        print(f"    A-3 RESULT: {'PASS' if a3_pass else 'FAIL'} (enriched={a3_enriched})")
    else:
        a3_pass = False
        a3_p = 1.0
        print(f"    A-3: INSUFFICIENT DATA")

    path_a_pass = sum([a1_pass, a2_pass, a3_pass])
    print(f"\n  PATH A SUMMARY: {path_a_pass}/3 predictions pass")

    return {
        'class_buffer_counts': class_counts,
        'prefix_profiles': {c: dict(prefix_by_class.get(c, {})) for c in all_classes},
        'a1': {'test': a1_test, 'p': a1_p, 'pass': a1_pass},
        'a2': {'most_pairs_class': most_pairs, 'most_buffers_class': most_buffers, 'pass': a2_pass},
        'a3': {'po_qo': po_qo, 'po_total': po_total, 'other_qo': other_qo,
               'other_total': other_total, 'pass': a3_pass},
        'predictions_passing': path_a_pass,
    }


# ═══════════════════════════════════════════════════════════════════════
# S3: Path B — Process-side REGIME gradient
# ═══════════════════════════════════════════════════════════════════════
def path_b_process_gradient(axm, regimes, master):
    """Compare process-side constraint envelope widths across REGIMEs/degrees."""
    print("\n" + "=" * 72)
    print("PATH B: Process-Side REGIME Gradient (Clamped Envelope Match)")
    print("=" * 72)

    # ── Voynich: hazard density envelope per REGIME ──
    folio_data = axm['folio_data']
    regime_hazard = defaultdict(list)
    for fid, fd in folio_data.items():
        regime = fd.get('regime')
        if regime:
            regime_hazard[regime].append(fd['hazard_density'])

    print("\n  Voynich hazard density envelope per REGIME:")
    voy_envelopes = {}
    ordered_regimes = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
    for reg in ordered_regimes:
        vals = np.array(regime_hazard[reg])
        env = {
            'n': len(vals),
            'mean': float(vals.mean()),
            'std': float(vals.std()),
            'cv': float(vals.std() / vals.mean()) if vals.mean() > 0 else 0,
            'min': float(vals.min()),
            'max': float(vals.max()),
            'range': float(vals.max() - vals.min()),
            'iqr': float(np.percentile(vals, 75) - np.percentile(vals, 25)),
        }
        voy_envelopes[reg] = env
        degree = REGIME_TO_DEGREE.get(reg, '?')
        print(f"    {reg} (~Degree {degree}): N={env['n']}, "
              f"mean={env['mean']:.3f}, CV={env['cv']:.3f}, "
              f"range={env['range']:.3f}, IQR={env['iqr']:.3f}")

    # B-1: REGIME_4 has narrowest envelope
    narrowest = min(ordered_regimes, key=lambda r: voy_envelopes[r]['range'])
    b1_pass = narrowest == 'REGIME_4'
    print(f"\n  B-1: Narrowest hazard envelope is {narrowest} (range={voy_envelopes[narrowest]['range']:.3f})")
    print(f"    Expected: REGIME_4. {'PASS' if b1_pass else 'FAIL'}")

    # ── Brunschwig: constraint intensity per fire degree ──
    materials = master['materials']
    degree_metrics = defaultdict(lambda: {
        'precision_scores': [], 'monitoring': [], 'compliance': [], 'n': 0
    })

    precision_map = {'LOW': 0, 'MODERATE': 1, 'HIGH': 2, 'CRITICAL': 3}

    for mat in materials:
        deg = mat.get('fire_degree')
        if deg is None:
            continue
        ra = mat.get('regime_assignment', {})
        prec = precision_map.get(ra.get('precision_requirement', 'LOW'), 0)
        mon = ra.get('monitoring_intensity', 0)

        # Grammar compliance: 1 if compliant, 0 if violation
        gc = mat.get('grammar_compliance', {})
        compliant = 1 if gc.get('status') == 'COMPLIANT' else (0 if gc.get('status') == 'VIOLATION' else np.nan)

        degree_metrics[deg]['precision_scores'].append(prec)
        degree_metrics[deg]['monitoring'].append(mon)
        if not np.isnan(compliant):
            degree_metrics[deg]['compliance'].append(compliant)
        degree_metrics[deg]['n'] += 1

    print("\n  Brunschwig constraint intensity per fire degree:")
    bru_intensity = {}
    for deg in [1, 2, 3, 4]:
        dm = degree_metrics[deg]
        prec_vals = np.array(dm['precision_scores'])
        mon_vals = np.array(dm['monitoring'])
        comp_vals = np.array(dm['compliance']) if dm['compliance'] else np.array([0])

        intensity = {
            'n': dm['n'],
            'mean_precision': float(prec_vals.mean()) if len(prec_vals) > 0 else 0,
            'mean_monitoring': float(mon_vals.mean()) if len(mon_vals) > 0 else 0,
            'compliance_rate': float(comp_vals.mean()) if len(comp_vals) > 0 else 0,
            'composite': 0,  # computed below
        }
        # Composite constraint intensity: weighted sum
        intensity['composite'] = (intensity['mean_precision'] * 0.4 +
                                   intensity['mean_monitoring'] * 0.3 +
                                   (1 - intensity['compliance_rate']) * 0.3)  # violation rate
        bru_intensity[deg] = intensity

        regime = DEGREE_TO_REGIME[deg]
        print(f"    Degree {deg} (~ {regime}): N={intensity['n']}, "
              f"precision={intensity['mean_precision']:.3f}, "
              f"monitoring={intensity['mean_monitoring']:.3f}, "
              f"compliance={intensity['compliance_rate']:.3f}, "
              f"composite={intensity['composite']:.3f}")

    # B-2: Degree 4 has highest precision and monitoring
    highest_prec = max([1, 2, 3, 4], key=lambda d: bru_intensity[d]['mean_precision'])
    highest_mon = max([1, 2, 3, 4], key=lambda d: bru_intensity[d]['mean_monitoring'])
    b2_pass = highest_prec == 4 or highest_mon == 4
    print(f"\n  B-2: Highest precision degree: {highest_prec}, Highest monitoring degree: {highest_mon}")
    print(f"    Expected: Degree 4. {'PASS' if b2_pass else 'FAIL'}")

    # B-3: Process constraint gradient correlates positively
    # Use degree ordering mapped to REGIME ordering
    # Voynich: CV per REGIME (lower CV = more constrained = higher process intensity)
    # Brunschwig: composite constraint intensity per degree
    # Both should show: higher degree/REGIME → more constrained

    # Map: degree 1→R2, 2→R1, 3→R3, 4→R4
    # Order by degree: 1, 2, 3, 4
    voy_cv_by_degree = [voy_envelopes[DEGREE_TO_REGIME[d]]['cv'] for d in [1, 2, 3, 4]]
    bru_comp_by_degree = [bru_intensity[d]['composite'] for d in [1, 2, 3, 4]]

    # Higher composite = more constrained in Brunschwig
    # Lower CV = more constrained in Voynich → negate for same-direction comparison
    # Or: test if composite and (1-CV) correlate positively
    voy_constraint = [1.0 - cv for cv in voy_cv_by_degree]  # invert: higher = more constrained

    rho_composite, _ = stats.spearmanr(bru_comp_by_degree, voy_constraint)

    # Also test individual pairs
    voy_range_by_degree = [voy_envelopes[DEGREE_TO_REGIME[d]]['range'] for d in [1, 2, 3, 4]]
    bru_prec_by_degree = [bru_intensity[d]['mean_precision'] for d in [1, 2, 3, 4]]

    rho_prec_range, _ = stats.spearmanr(bru_prec_by_degree, [-r for r in voy_range_by_degree])

    b3_pass = rho_composite > 0
    print(f"\n  B-3: Process constraint gradient correlation")
    print(f"    Brunschwig composite by degree: {[f'{v:.3f}' for v in bru_comp_by_degree]}")
    print(f"    Voynich constraint (1-CV) by degree: {[f'{v:.3f}' for v in voy_constraint]}")
    print(f"    Spearman rho (composite vs 1-CV): {rho_composite:.3f}")
    print(f"    Brunschwig precision by degree: {[f'{v:.3f}' for v in bru_prec_by_degree]}")
    print(f"    Voynich -range by degree: {[f'{v:.3f}' for v in [-r for r in voy_range_by_degree]]}")
    print(f"    Spearman rho (precision vs -range): {rho_prec_range:.3f}")
    print(f"    B-3 RESULT: rho={rho_composite:.3f}, {'PASS' if b3_pass else 'FAIL'} (need rho > 0)")

    path_b_pass = sum([b1_pass, b2_pass, b3_pass])
    print(f"\n  PATH B SUMMARY: {path_b_pass}/3 predictions pass")

    return {
        'voynich_envelopes': voy_envelopes,
        'brunschwig_intensity': {str(k): v for k, v in bru_intensity.items()},
        'b1': {'narrowest_regime': narrowest, 'pass': b1_pass},
        'b2': {'highest_precision_degree': highest_prec, 'highest_monitoring_degree': highest_mon,
               'pass': b2_pass},
        'b3': {'rho_composite': float(rho_composite), 'rho_precision_range': float(rho_prec_range),
               'pass': b3_pass},
        'predictions_passing': path_b_pass,
    }


# ═══════════════════════════════════════════════════════════════════════
# S4: Path C — Operational manifold axis alignment
# ═══════════════════════════════════════════════════════════════════════
def path_c_operational_manifold(curated, voy_pca):
    """PCA on Brunschwig action-phase space, compare to Voynich operational PCA."""
    print("\n" + "=" * 72)
    print("PATH C: Operational Manifold Axis Alignment")
    print("=" * 72)

    # Build per-recipe phase profiles
    recipes_with_steps = []
    for recipe in curated['recipes']:
        steps = recipe.get('procedural_steps')
        if not steps:
            continue
        phase_counts = Counter()
        for step in steps:
            action = step.get('action')
            if action and action in ACTION_TO_PHASE:
                phase_counts[ACTION_TO_PHASE[action]] += 1

        total = sum(phase_counts.values())
        if total == 0:
            continue

        profile = {phase: phase_counts.get(phase, 0) / total for phase in PHASE_ORDER}
        profile['recipe_id'] = recipe['id']
        profile['fire_degree'] = recipe.get('fire_degree')
        profile['n_steps'] = total
        recipes_with_steps.append(profile)

    print(f"\n  Recipes with procedural steps: {len(recipes_with_steps)}")

    if len(recipes_with_steps) < 10:
        print("  INSUFFICIENT DATA for PCA")
        return {'status': 'INSUFFICIENT_DATA', 'predictions_passing': 0}

    # Build feature matrix
    X = np.array([[r[p] for p in PHASE_ORDER] for r in recipes_with_steps])
    print(f"  Feature matrix: {X.shape[0]} recipes × {X.shape[1]} phases")

    # Report phase means
    print("\n  Mean phase proportions across recipes:")
    for i, phase in enumerate(PHASE_ORDER):
        print(f"    {phase:<16}: {X[:, i].mean():.3f} (std={X[:, i].std():.3f})")

    # Standardize and PCA
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    pca = PCA()
    pca.fit(X_scaled)

    var_explained = pca.explained_variance_ratio_
    cum_var = np.cumsum(var_explained)

    print(f"\n  Brunschwig PCA variance explained:")
    for i, (v, c) in enumerate(zip(var_explained, cum_var)):
        print(f"    PC{i+1}: {v:.3f} (cumulative: {c:.3f})")

    n_for_80 = int(np.searchsorted(cum_var, 0.80) + 1)
    print(f"\n  Components for 80% variance: {n_for_80}")

    # C-1: Dimensionality <= 5 for 80%
    c1_pass = n_for_80 <= 5
    print(f"  C-1: Brunschwig needs {n_for_80} components for 80% (Voynich needs {voy_pca['n_components_80']})")
    print(f"    {'PASS' if c1_pass else 'FAIL'} (need <= 5)")

    # Loadings
    loadings = pca.components_  # shape: (n_components, n_features)
    print(f"\n  Brunschwig PCA loadings (PC1-PC3):")
    header = f"  {'Phase':<16}" + "".join(f"{'PC'+str(i+1):>10}" for i in range(min(3, len(var_explained))))
    print(header)
    for j, phase in enumerate(PHASE_ORDER):
        row = f"  {phase:<16}" + "".join(f"{loadings[i, j]:>10.3f}" for i in range(min(3, len(var_explained))))
        print(row)

    # Voynich PCA loadings
    voy_loadings = voy_pca['loadings']
    voy_features = voy_pca['features']
    print(f"\n  Voynich PCA loadings (PC1-PC3):")
    header = f"  {'Feature':<16}" + "".join(f"{'PC'+str(i+1):>10}" for i in range(3))
    print(header)
    for feat in voy_features:
        row = f"  {feat:<16}" + "".join(f"{voy_loadings[f'PC{i+1}'][feat]:>10.3f}" for i in range(3))
        print(row)

    # C-2: PC1 loads on energy/intensity
    # Brunschwig PC1: expect DISTILLATION + MIDPROCESS (= core energy application)
    bru_pc1 = {phase: loadings[0, i] for i, phase in enumerate(PHASE_ORDER)}
    bru_pc1_top = sorted(bru_pc1.items(), key=lambda x: abs(x[1]), reverse=True)[:3]

    # Voynich PC1: 'energy' loading = -0.406, 'fq' loading = 0.471
    voy_pc1_energy = voy_loadings['PC1']['energy']  # -0.406
    voy_pc1_fq = voy_loadings['PC1']['fq']  # 0.471

    energy_phases = {'DISTILLATION', 'MIDPROCESS'}
    bru_pc1_energy_loading = sum(abs(bru_pc1.get(p, 0)) for p in energy_phases)
    bru_pc1_total_loading = sum(abs(v) for v in bru_pc1.values())
    energy_fraction = bru_pc1_energy_loading / bru_pc1_total_loading if bru_pc1_total_loading > 0 else 0

    c2_pass = any(p in energy_phases for p, _ in bru_pc1_top[:2])
    print(f"\n  C-2: PC1 energy/intensity axis alignment")
    print(f"    Brunschwig PC1 top loadings: {[(p, f'{v:.3f}') for p, v in bru_pc1_top]}")
    print(f"    Energy phases (DISTILLATION+MIDPROCESS) fraction of PC1: {energy_fraction:.3f}")
    print(f"    Voynich PC1: energy={voy_pc1_energy:.3f}, fq={voy_pc1_fq:.3f}")
    print(f"    C-2 RESULT: {'PASS' if c2_pass else 'FAIL'} (energy phase in top-2 PC1 loadings)")

    # C-3: Monitoring/control dimension exists
    # Brunschwig: MIDPROCESS contains MONITOR_DRIPS, MONITOR_TEMP, REGULATE
    # Voynich PC2: link=0.508, kernel_k=0.503 (monitoring/kernel engagement)
    # Check if MIDPROCESS loads strongly on any PC
    midprocess_loadings = [abs(loadings[i, PHASE_ORDER.index('MIDPROCESS')])
                           for i in range(min(5, len(var_explained)))]
    max_mid_pc = np.argmax(midprocess_loadings) + 1
    max_mid_val = max(midprocess_loadings)

    voy_pc2_link = voy_loadings['PC2']['link']  # 0.508
    voy_pc2_kernel_k = voy_loadings['PC2']['kernel_k']  # 0.503

    c3_pass = max_mid_val > 0.3  # MIDPROCESS loads > 0.3 on some PC
    print(f"\n  C-3: Monitoring/control dimension")
    print(f"    Brunschwig MIDPROCESS loadings: {[f'{v:.3f}' for v in midprocess_loadings]}")
    print(f"    Strongest on PC{max_mid_pc}: {max_mid_val:.3f}")
    print(f"    Voynich PC2: link={voy_pc2_link:.3f}, kernel_k={voy_pc2_kernel_k:.3f}")
    print(f"    C-3 RESULT: {'PASS' if c3_pass else 'FAIL'} (MIDPROCESS > 0.3 on some PC)")

    path_c_pass = sum([c1_pass, c2_pass, c3_pass])
    print(f"\n  PATH C SUMMARY: {path_c_pass}/3 predictions pass")

    return {
        'n_recipes': len(recipes_with_steps),
        'brunschwig_var_explained': var_explained.tolist(),
        'brunschwig_n_for_80': n_for_80,
        'brunschwig_loadings': {f'PC{i+1}': {p: float(loadings[i, j])
                                              for j, p in enumerate(PHASE_ORDER)}
                                 for i in range(min(5, len(var_explained)))},
        'voynich_n_for_80': voy_pca['n_components_80'],
        'c1': {'bru_n_for_80': n_for_80, 'voy_n_for_80': voy_pca['n_components_80'], 'pass': c1_pass},
        'c2': {'bru_pc1_top': [(p, float(v)) for p, v in bru_pc1_top],
               'energy_fraction': float(energy_fraction), 'pass': c2_pass},
        'c3': {'midprocess_max_pc': int(max_mid_pc), 'midprocess_max_val': float(max_mid_val),
               'pass': c3_pass},
        'predictions_passing': path_c_pass,
    }


# ═══════════════════════════════════════════════════════════════════════
# S5: Summary + verdict
# ═══════════════════════════════════════════════════════════════════════
def main():
    print("=" * 72)
    print("Phase 363: Brunschwig-Voynich Semantic Boundary Probe (F-BRU-029)")
    print("=" * 72)

    # S1: Load data
    buffers, thermo, axm, regimes, master, curated, voy_pca = load_all_data()

    # S2: Path A
    path_a = path_a_buffer_profiles(buffers, thermo)

    # S3: Path B
    path_b = path_b_process_gradient(axm, regimes, master)

    # S4: Path C
    path_c = path_c_operational_manifold(curated, voy_pca)

    # S5: Final verdict
    total_pass = path_a['predictions_passing'] + path_b['predictions_passing'] + path_c['predictions_passing']
    total_tests = 9

    print("\n" + "=" * 72)
    print("FINAL VERDICT")
    print("=" * 72)
    print(f"  Path A (Hazard thermodynamic signatures): {path_a['predictions_passing']}/3")
    print(f"  Path B (Process-side gradient): {path_b['predictions_passing']}/3")
    print(f"  Path C (Operational manifold): {path_c['predictions_passing']}/3")
    print(f"  TOTAL: {total_pass}/{total_tests}")

    if total_pass >= 7:
        verdict = 'SEMANTIC_BOUNDARY_EXTENDED'
        print(f"\n  VERDICT: {verdict}")
        print("  Multiple paths extend structural homology beyond F-BRU-027 level.")
    elif total_pass >= 5:
        verdict = 'PARTIAL_EXTENSION'
        print(f"\n  VERDICT: {verdict}")
        print("  Some structural homology paths viable, others at ceiling.")
    elif total_pass >= 3:
        verdict = 'MIXED_SIGNAL'
        print(f"\n  VERDICT: {verdict}")
        print("  Weak or mixed evidence for deeper structural correspondence.")
    else:
        verdict = 'SEMANTIC_CEILING_CONFIRMED'
        print(f"\n  VERDICT: {verdict}")
        print("  The Brunschwig comparison has reached its semantic ceiling.")
        print("  Architectural alignment (F-BRU-027) is the deepest recoverable level.")

    # Write results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 363,
        'fit_id': 'F-BRU-029',
        'title': 'Brunschwig-Voynich Semantic Boundary Probe',
        'path_a': path_a,
        'path_b': path_b,
        'path_c': path_c,
        'total_passing': total_pass,
        'total_tests': total_tests,
        'verdict': verdict,
    }
    with open(RESULTS_PATH, 'w') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults written to {RESULTS_PATH}")


if __name__ == '__main__':
    main()
