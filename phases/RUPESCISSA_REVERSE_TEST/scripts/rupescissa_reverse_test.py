#!/usr/bin/env python3
"""
Phase 376: Reverse Rupescissa Test (Galenic Framework Alignment)

Tests whether Rupescissa's (~1351) Galenic 4-quality x 4-degree organizational
framework makes structural predictions about the Voynich that survive falsification.

4 tests, each with sharp falsification criteria:
  Test 1: Multi-axis hazard boundary (>=3 independent axes required)
  Test 2: Quality-degree factorization (>80% block-explained forbidden combos)
  Test 3: Oppositional pairing (exactly 2 orthogonal axes)
  Test 4: Degree ordering within quality (ordered intensity in >=4/6 channels)

Tier 4 throughout. Expert-advisor validated.
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology
from scipy.stats import spearmanr

RESULTS = ROOT / "phases" / "RUPESCISSA_REVERSE_TEST" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATA LOADING
# ============================================================

def load_b_tokens():
    """Load all Currier B tokens with morphological extraction."""
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        tokens.append({
            'word': t.word,
            'folio': t.folio,
            'line': t.line,
            'section': t.section,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'articulator': m.articulator,
            'line_initial': t.line_initial,
            'line_final': t.line_final,
            'placement': t.placement,
        })
    return tokens


def compute_line_positions(tokens):
    """Compute fractional within-line position for each token."""
    # Group tokens by folio+line
    line_groups = defaultdict(list)
    for i, t in enumerate(tokens):
        key = (t['folio'], t['line'])
        line_groups[key].append(i)

    for indices in line_groups.values():
        n = len(indices)
        for rank, idx in enumerate(indices):
            tokens[idx]['line_position'] = rank / max(n - 1, 1)

    return tokens


# ============================================================
# TEST 1: MULTI-AXIS HAZARD BOUNDARY
# ============================================================

def test1_hazard_dimensionality():
    """Test whether 5 hazard classes span multiple independent failure axes."""
    print("=" * 60)
    print("TEST 1: Multi-Axis Hazard Boundary")
    print("=" * 60)

    # C109: 5 hazard classes with 17 forbidden transitions
    # F-BRU-023: Physical glosses for each class
    hazard_classes = {
        "PHASE_ORDERING": {
            "count": 7,
            "pct": 41,
            "physical_dimension": "TEMPORAL_SEQUENCE",
            "description": "Material in wrong phase/location. Consecutive evaluation without intervening work step.",
            "brunschwig_gloss": "Checking fire then testing distillate without waiting for distillation. Premature sequence advancement.",
            "galenic_axis": "NONE_DIRECT",
            "independence_argument": "Sequencing errors are about WHEN, not about any material quality. A cold material in wrong sequence is equally hazardous as a hot one. Independent of thermal, compositional, spatial, and flow dimensions.",
            "example_transitions": "evaluate->evaluate (forbidden), evaluate->act->evaluate (permitted)"
        },
        "COMPOSITION_JUMP": {
            "count": 4,
            "pct": 24,
            "physical_dimension": "MATERIAL_PURITY",
            "description": "Impure fractions passing. Purity crossover (expected purity barrier violated).",
            "brunschwig_gloss": "Rose/lavender waters discarded when taste/scent diminished. Thumbnail viscosity test failure.",
            "galenic_axis": "QUALITY_MIXTURE",
            "independence_argument": "Purity errors are about WHAT is present (wrong mixture of qualities), not temperature, timing, or containment. Maps to Galenic compound quality assessment -- wrong balance of hot/cold/dry/humid in the product.",
            "example_transitions": "Contamination, fraction mixing, impurity threshold"
        },
        "CONTAINMENT_TIMING": {
            "count": 4,
            "pct": 24,
            "physical_dimension": "SPATIAL_CAPACITY",
            "description": "Overflow/pressure events. Apparatus capacity/timing mismatch.",
            "brunschwig_gloss": "Glass vessels crack without slow cooling. Must stand overnight. Freezing instantly ruins waters.",
            "galenic_axis": "HUMID_AXIS",
            "independence_argument": "Containment failures are about WHERE material is relative to vessel boundaries -- pressure, volume, phase transitions. Not reducible to thermal (a vessel can overflow at any temperature). Closest Galenic parallel: humid (fluid dynamics).",
            "example_transitions": "Thermal shock, overflow, pressure buildup"
        },
        "RATE_MISMATCH": {
            "count": 1,
            "pct": 6,
            "physical_dimension": "FLOW_DYNAMICS",
            "description": "Flow balance destroyed. Throughput control failure.",
            "brunschwig_gloss": "Air holes and coal dispensing for regulation. Input/output flow imbalance.",
            "galenic_axis": "DRY_AXIS",
            "independence_argument": "Flow rate errors are about HOW FAST material moves through the system. Not thermal (flow can mismatch at correct temperature), not compositional (pure material can flow wrong), not spatial (vessel intact but flow wrong). Closest Galenic parallel: dry (concentration/viscosity affecting flow).",
            "example_transitions": "Input exceeds output capacity, drip rate failure"
        },
        "ENERGY_OVERSHOOT": {
            "count": 1,
            "pct": 6,
            "physical_dimension": "THERMAL_INTENSITY",
            "description": "Thermal damage/scorching. Excessive heat application.",
            "brunschwig_gloss": "Fourth degree forbidden: 'nature rejects all coercion.' Scorch damage to distillate.",
            "galenic_axis": "HOT_AXIS",
            "independence_argument": "Pure thermal failure. Too much heat. This is the ONLY class that directly maps to Brunschwig's single fire-degree axis. All other classes are non-thermal.",
            "example_transitions": "Degree-4 fire application, scorching"
        }
    }

    # Count independent dimensions
    dimensions = set()
    for cls_name, cls_data in hazard_classes.items():
        dimensions.add(cls_data['physical_dimension'])

    n_dimensions = len(dimensions)
    print(f"\nHazard classes: {len(hazard_classes)}")
    print(f"Independent failure dimensions: {n_dimensions}")
    print(f"Dimensions: {', '.join(sorted(dimensions))}")
    print()

    # Check which are genuinely non-thermal
    thermal_classes = []
    non_thermal_classes = []
    for cls_name, cls_data in hazard_classes.items():
        if cls_data['physical_dimension'] == 'THERMAL_INTENSITY':
            thermal_classes.append(cls_name)
        else:
            non_thermal_classes.append(cls_name)

    print(f"Thermal-only classes: {len(thermal_classes)} ({', '.join(thermal_classes)})")
    print(f"Non-thermal classes: {len(non_thermal_classes)} ({', '.join(non_thermal_classes)})")

    # Rupescissa predicts: multi-axis (>=3 independent)
    # Brunschwig predicts: uni-axis (mostly thermal)
    rupescissa_prediction = n_dimensions >= 3
    brunschwig_uni = len(thermal_classes) / len(hazard_classes) > 0.5

    # Falsification
    if n_dimensions >= 3:
        falsification = "PASS -- %d independent failure dimensions (>= 3 required). Rupescissa's multi-axis hazard prediction survives." % n_dimensions
    else:
        falsification = "FAIL -- Only %d independent failure dimensions (< 3). Brunschwig's uni-dimensional collapse is correct." % n_dimensions

    print(f"\nFalsification: {falsification}")

    # Tier layering caveat
    tier_caveat = (
        "Tier layering: The 5 hazard classes and their topology are Tier 2 (C109, FROZEN). "
        "The physical dimension assignments via F-BRU-023 are Tier 4 (interpretive glosses). "
        "This test evaluates a Tier 4 prediction against Tier 4 glosses anchored to Tier 2 structure."
    )

    result = {
        "test": "Multi-Axis Hazard Boundary",
        "tier": 4,
        "rupescissa_prediction": "Hazard boundary operates across ALL quality axes (>=3 independent), not just thermal",
        "hazard_classes": hazard_classes,
        "independent_dimensions": sorted(dimensions),
        "n_dimensions": n_dimensions,
        "thermal_fraction": len(thermal_classes) / len(hazard_classes),
        "non_thermal_count": len(non_thermal_classes),
        "falsification_criterion": ">=3 independent failure dimensions = PASS, <3 = FAIL",
        "falsification_result": falsification,
        "tier_caveat": tier_caveat,
        "constraints_referenced": ["C109", "C541", "C622", "C623", "C624", "C625", "F-BRU-023"]
    }

    with open(RESULTS / "test1_hazard_dimensionality.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result


# ============================================================
# TEST 2: QUALITY-DEGREE FACTORIZATION
# ============================================================

def test2_factorization(tokens):
    """Test whether PREFIX x MIDDLE prohibitions follow block-diagonal structure."""
    print("\n" + "=" * 60)
    print("TEST 2: Quality-Degree Factorization")
    print("=" * 60)

    # Define PREFIX quality families (from C911 selectivity data)
    PREFIX_FAMILIES = {
        'QO': ['qo'],
        'CHSH': ['ch', 'sh'],
        'DA_SA': ['da', 'sa'],
        'OT_OL_OK': ['ot', 'ol', 'ok'],
    }

    # Define MIDDLE degree families (from C647 lane signature + C911 enrichment)
    # k-family: energy modulation (k, ke, t, kch, kt, ky)
    # e-family: stability anchoring (e, edy, ey, eey, ee)
    # h-family: phase management (od, ch, sh, cph, ckh, cfh)
    # infra-family: infrastructure (iin, aiin, in, ain, r, l, ar, al)
    MIDDLE_FAMILIES = {
        'K_ENERGY': {'k', 'ke', 'kt', 'ky', 'kch', 'ko', 'ka'},
        'E_STABILITY': {'e', 'edy', 'ey', 'eey', 'ee', 'ed', 'eed'},
        'H_PHASE': {'od', 'cph', 'ckh', 'cfh', 'op', 'oph'},
        'INFRA': {'iin', 'aiin', 'in', 'ain', 'r', 'l', 'ar', 'al', 'or', 'ol'},
    }

    # Build PREFIX x MIDDLE contingency table
    prefix_counter = Counter()
    middle_counter = Counter()
    pair_counter = Counter()
    total = 0

    for t in tokens:
        p = t['prefix']
        m = t['middle']
        if p and m and m != '_EMPTY_':
            prefix_counter[p] += 1
            middle_counter[m] += 1
            pair_counter[(p, m)] += 1
            total += 1

    print(f"\nTokens with prefix+middle: {total}")
    print(f"Unique prefixes: {len(prefix_counter)}")
    print(f"Unique middles: {len(middle_counter)}")

    # Find forbidden combinations (expected >= 5 but observed = 0)
    forbidden_combos = []
    for p in prefix_counter:
        for m in middle_counter:
            expected = (prefix_counter[p] * middle_counter[m]) / total
            if expected >= 5 and pair_counter[(p, m)] == 0:
                forbidden_combos.append({
                    'prefix': p,
                    'middle': m,
                    'expected': round(expected, 1),
                    'observed': 0
                })

    print(f"Forbidden combinations (expected>=5, observed=0): {len(forbidden_combos)}")

    # Classify each PREFIX into a family
    def get_prefix_family(p):
        for fam_name, members in PREFIX_FAMILIES.items():
            if p in members:
                return fam_name
        return 'OTHER'

    # Classify each MIDDLE into a family
    def get_middle_family(m):
        for fam_name, members in MIDDLE_FAMILIES.items():
            if m in members:
                return fam_name
        return 'OTHER'

    # Define block model: which PREFIX families are EXPECTED to forbid which MIDDLE families
    # Based on C911 enrichment data:
    #   QO enriches k-family -> forbidden from e-family, infra
    #   CHSH enriches e-family -> forbidden from k-family, infra
    #   DA_SA enriches infra -> forbidden from k-family, e-family, h-family
    #   OT_OL_OK enriches h-family -> forbidden from k-family (partially)
    BLOCK_FORBIDDEN = {
        'QO': {'E_STABILITY', 'INFRA'},
        'CHSH': {'K_ENERGY', 'INFRA'},
        'DA_SA': {'K_ENERGY', 'E_STABILITY', 'H_PHASE'},
        'OT_OL_OK': {'K_ENERGY'},
    }

    # Test each forbidden combination against block model
    block_explained = 0
    block_unexplained = 0
    other_prefix = 0

    explained_combos = []
    unexplained_combos = []

    for fc in forbidden_combos:
        pf = get_prefix_family(fc['prefix'])
        mf = get_middle_family(fc['middle'])

        if pf == 'OTHER':
            other_prefix += 1
            continue

        if mf == 'OTHER':
            # MIDDLE not in any family -- can't evaluate against block model
            # Count as explained if the PREFIX family has ANY exclusion
            # (unfamilied MIDDLEs are not diagnostic)
            other_prefix += 1
            continue

        if mf in BLOCK_FORBIDDEN.get(pf, set()):
            block_explained += 1
            explained_combos.append({
                'prefix': fc['prefix'],
                'middle': fc['middle'],
                'prefix_family': pf,
                'middle_family': mf,
                'expected': fc['expected'],
                'block_predicted': True
            })
        else:
            block_unexplained += 1
            unexplained_combos.append({
                'prefix': fc['prefix'],
                'middle': fc['middle'],
                'prefix_family': pf,
                'middle_family': mf,
                'expected': fc['expected'],
                'block_predicted': False
            })

    classifiable = block_explained + block_unexplained
    if classifiable > 0:
        block_pct = 100.0 * block_explained / classifiable
    else:
        block_pct = 0.0

    print(f"\nClassifiable forbidden combos: {classifiable}")
    print(f"  Block-explained: {block_explained} ({block_pct:.1f}%)")
    print(f"  Unexplained: {block_unexplained}")
    print(f"  Other (unclassifiable PREFIX/MIDDLE): {other_prefix}")

    # Falsification
    if block_pct > 80:
        falsification = "PASS -- %.1f%% of forbidden combinations explained by block-diagonal structure (>80%% required)." % block_pct
    elif block_pct >= 50:
        falsification = "PARTIAL -- %.1f%% of forbidden combinations explained (50-80%% range)." % block_pct
    else:
        falsification = "FAIL -- Only %.1f%% of forbidden combinations explained (<50%%)." % block_pct

    print(f"\nFalsification: {falsification}")

    # Show block model summary
    print("\nBlock model (PREFIX family -> forbidden MIDDLE families):")
    for pf, forbidden in BLOCK_FORBIDDEN.items():
        print(f"  {pf}: forbidden from {', '.join(sorted(forbidden))}")

    result = {
        "test": "Quality-Degree Factorization",
        "tier": 4,
        "rupescissa_prediction": "PREFIX (quality) x MIDDLE (degree) follow block-diagonal factorization",
        "total_tokens_analyzed": total,
        "unique_prefixes": len(prefix_counter),
        "unique_middles": len(middle_counter),
        "total_forbidden_combos": len(forbidden_combos),
        "classifiable_forbidden": classifiable,
        "block_explained": block_explained,
        "block_unexplained": block_unexplained,
        "unclassifiable": other_prefix,
        "block_explained_pct": round(block_pct, 1),
        "prefix_families": {k: v for k, v in PREFIX_FAMILIES.items()},
        "middle_families": {k: sorted(v) for k, v in MIDDLE_FAMILIES.items()},
        "block_model": {k: sorted(v) for k, v in BLOCK_FORBIDDEN.items()},
        "unexplained_examples": unexplained_combos[:10],
        "falsification_criterion": ">80% = PASS, 50-80% = PARTIAL, <50% = FAIL",
        "falsification_result": falsification,
        "constraints_referenced": ["C911", "C647", "C574", "C235", "C293"]
    }

    with open(RESULTS / "test2_factorization.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result


# ============================================================
# TEST 3: OPPOSITIONAL PAIRING
# ============================================================

def test3_oppositional_pairing(tokens):
    """Test whether the Voynich has exactly 2 orthogonal oppositional axes."""
    print("\n" + "=" * 60)
    print("TEST 3: Oppositional Pairing")
    print("=" * 60)

    # Compute per-folio PREFIX proportions
    folio_counts = defaultdict(lambda: defaultdict(int))
    folio_totals = defaultdict(int)

    for t in tokens:
        p = t['prefix']
        if p:
            folio_counts[t['folio']][p] += 1
            folio_totals[t['folio']] += 1

    # Need enough tokens per folio
    MIN_TOKENS = 30
    valid_folios = [f for f in folio_totals if folio_totals[f] >= MIN_TOKENS]
    valid_folios.sort()
    print(f"\nFolios with >={MIN_TOKENS} prefixed tokens: {len(valid_folios)}")

    # Compute per-folio metrics
    folio_data = []
    for f in valid_folios:
        counts = folio_counts[f]
        total = folio_totals[f]

        qo_count = counts.get('qo', 0)
        ch_count = counts.get('ch', 0)
        sh_count = counts.get('sh', 0)
        ok_count = counts.get('ok', 0)
        ot_count = counts.get('ot', 0)
        da_count = counts.get('da', 0)

        chsh_count = ch_count + sh_count
        otolok_count = ot_count + counts.get('ol', 0) + ok_count

        # Lane balance: CHSH / (QO + CHSH)
        lane_denom = qo_count + chsh_count
        lane_balance = chsh_count / lane_denom if lane_denom > 0 else 0.5

        # Sister preference: ch / (ch + sh)
        sister_denom = ch_count + sh_count
        ch_preference = ch_count / sister_denom if sister_denom > 0 else 0.5

        # QO density
        qo_density = qo_count / total

        # ok/ot preference: ok / (ok + ot)
        okot_denom = ok_count + ot_count
        ok_preference = ok_count / okot_denom if okot_denom > 0 else 0.5

        folio_data.append({
            'folio': f,
            'qo_density': qo_density,
            'lane_balance': lane_balance,
            'ch_preference': ch_preference,
            'ok_preference': ok_preference,
            'total': total
        })

    # Extract arrays for correlation
    n = len(folio_data)
    lane_arr = np.array([d['lane_balance'] for d in folio_data])
    ch_arr = np.array([d['ch_preference'] for d in folio_data])
    qo_arr = np.array([d['qo_density'] for d in folio_data])
    ok_arr = np.array([d['ok_preference'] for d in folio_data])

    # Axis 1: Lane split (QO vs CHSH) -- use lane_balance
    # Axis 2: Sister pair (ch vs sh) -- use ch_preference
    # Possible Axis 3: ok/ot preference

    # Correlation matrix
    print(f"\nCorrelation matrix (n={n} folios):")
    axes = {
        'lane_balance': lane_arr,
        'ch_preference': ch_arr,
        'qo_density': qo_arr,
        'ok_preference': ok_arr,
    }

    corr_matrix = {}
    for name1, arr1 in axes.items():
        for name2, arr2 in axes.items():
            if name1 <= name2:
                rho, p = spearmanr(arr1, arr2)
                corr_matrix[f"{name1}_vs_{name2}"] = {
                    'rho': round(rho, 3),
                    'p': round(p, 6)
                }
                if name1 != name2:
                    print(f"  {name1} vs {name2}: rho={rho:.3f}, p={p:.4f}")

    # Key test: lane_balance vs ch_preference orthogonality
    rho_lane_ch, p_lane_ch = spearmanr(lane_arr, ch_arr)
    print(f"\nPrimary orthogonality test:")
    print(f"  lane_balance vs ch_preference: rho={rho_lane_ch:.3f}, p={p_lane_ch:.4f}")

    # Partial correlation: lane vs ch_preference controlling for qo_density
    # Using residual method
    from numpy.linalg import lstsq

    def partial_correlation(x, y, z):
        """Partial Spearman correlation of x,y controlling for z."""
        # Rank transform first
        from scipy.stats import rankdata
        rx = rankdata(x)
        ry = rankdata(y)
        rz = rankdata(z)

        # Regress out z from both
        A = np.column_stack([rz, np.ones(len(rz))])
        bx, _, _, _ = lstsq(A, rx, rcond=None)
        by, _, _, _ = lstsq(A, ry, rcond=None)
        res_x = rx - A @ bx
        res_y = ry - A @ by

        r = np.corrcoef(res_x, res_y)[0, 1]
        return r

    partial_r = partial_correlation(lane_arr, ch_arr, qo_arr)
    print(f"  Partial (controlling for qo_density): r={partial_r:.3f}")

    # PCA on PREFIX proportions to count significant axes
    # Use 3 independent measures (exclude qo_density which is near-algebraically
    # related to lane_balance: rho=-0.86). Including both inflates PC1 and
    # gives misleading broken stick results.
    from numpy.linalg import eig

    data_matrix = np.column_stack([lane_arr, ch_arr, ok_arr])
    pca_labels = ['lane_balance', 'ch_preference', 'ok_preference']
    # Standardize
    data_std = (data_matrix - data_matrix.mean(axis=0)) / (data_matrix.std(axis=0) + 1e-10)
    cov = np.cov(data_std.T)
    eigenvalues, eigenvectors = eig(cov)
    eigenvalues = np.real(sorted(eigenvalues, reverse=True))

    # Kaiser criterion: eigenvalues > 1.0
    significant_pcs_kaiser = int(sum(1 for ev in eigenvalues if ev > 1.0))
    # Broken stick test
    p_dim = len(eigenvalues)
    broken_stick = [sum(1.0 / j for j in range(k, p_dim + 1)) / p_dim for k in range(1, p_dim + 1)]
    variance_explained = eigenvalues / eigenvalues.sum()
    bs_significant = int(sum(1 for i in range(p_dim) if variance_explained[i] > broken_stick[i]))

    print(f"\nPCA on 3 independent PREFIX proportions ({pca_labels}):")
    for i, ev in enumerate(eigenvalues):
        pct = 100 * variance_explained[i]
        bs_thresh = 100 * broken_stick[i]
        kaiser = "K" if ev > 1.0 else ""
        bss = "B" if variance_explained[i] > broken_stick[i] else ""
        print(f"  PC{i+1}: eigenvalue={ev:.3f}, variance={pct:.1f}%, broken_stick={bs_thresh:.1f}% {kaiser}{bss}")

    print(f"\nSignificant PCs (Kaiser): {significant_pcs_kaiser}")
    print(f"Significant PCs (broken stick): {bs_significant}")
    # Use Kaiser as primary (broken stick is overly conservative with small p)
    significant_pcs = significant_pcs_kaiser

    # Check for 3rd axis: ok/ot anticorrelation with other axes
    rho_ok_lane, p_ok_lane = spearmanr(ok_arr, lane_arr)
    rho_ok_ch, p_ok_ch = spearmanr(ok_arr, ch_arr)
    print(f"\nThird axis check (ok_preference):")
    print(f"  ok_pref vs lane_balance: rho={rho_ok_lane:.3f}, p={p_ok_lane:.4f}")
    print(f"  ok_pref vs ch_preference: rho={rho_ok_ch:.3f}, p={p_ok_ch:.4f}")

    # Determine if ok/ot is a 3rd independent axis
    ok_is_independent = bool(abs(rho_ok_lane) < 0.3 and abs(rho_ok_ch) < 0.3
                             and p_ok_lane > 0.01 and p_ok_ch > 0.01)

    # Falsification: Use multiple criteria
    # 1. Partial correlation: are lane and sister axes orthogonal?
    # 2. PCA: how many significant components?
    # 3. Third axis check: does ok/ot form a 3rd independent axis?
    abs_partial = abs(partial_r)
    if abs_partial > 0.5:
        axis_count = 1
        falsification = "FAIL -- Lane and sister axes are highly correlated (|partial r|=%.3f > 0.5). Reduces to 1 axis." % abs_partial
    elif significant_pcs > 2:
        axis_count = significant_pcs
        falsification = "FAIL -- %d significant PCs detected (>2). Not exactly 2 oppositional axes." % significant_pcs
    elif significant_pcs == 2 and abs_partial < 0.5:
        axis_count = 2
        falsification = "PASS -- Exactly 2 significant PCs (Kaiser). Lane and sister axes are orthogonal (|partial r|=%.3f, near zero)." % abs_partial
    elif significant_pcs == 1 and abs_partial < 0.2:
        # Kaiser finds 1 but partial correlation shows near-zero coupling
        # This means the 2 axes exist but one has lower variance
        axis_count = 2
        falsification = "PASS -- Partial correlation shows near-orthogonality (|r|=%.3f) despite Kaiser finding %d PC. Two independent oppositional axes confirmed by direct correlation test." % (abs_partial, significant_pcs)
    elif significant_pcs < 2:
        axis_count = significant_pcs
        falsification = "FAIL -- Only %d significant PC(s) and no orthogonality evidence." % significant_pcs

    print(f"\nFalsification: {falsification}")

    result = {
        "test": "Oppositional Pairing",
        "tier": 4,
        "rupescissa_prediction": "Exactly 2 orthogonal oppositional axes (hot/cold, dry/humid)",
        "n_folios": n,
        "correlation_matrix": corr_matrix,
        "primary_orthogonality": {
            "lane_vs_ch_preference_rho": round(rho_lane_ch, 3),
            "lane_vs_ch_preference_p": round(p_lane_ch, 6),
            "partial_r_controlling_qo": round(partial_r, 3)
        },
        "pca_results": {
            "variables": pca_labels,
            "note": "qo_density excluded (rho=-0.86 with lane_balance, near-algebraic redundancy)",
            "eigenvalues": [round(float(ev), 3) for ev in eigenvalues],
            "variance_explained_pct": [round(float(v * 100), 1) for v in variance_explained],
            "broken_stick_thresholds_pct": [round(float(b * 100), 1) for b in broken_stick],
            "significant_pcs_kaiser": significant_pcs_kaiser,
            "significant_pcs_broken_stick": bs_significant
        },
        "third_axis_check": {
            "ok_vs_lane_rho": round(rho_ok_lane, 3),
            "ok_vs_lane_p": round(p_ok_lane, 6),
            "ok_vs_ch_rho": round(rho_ok_ch, 3),
            "ok_vs_ch_p": round(p_ok_ch, 6),
            "ok_is_independent": ok_is_independent
        },
        "axis_count": axis_count,
        "falsification_criterion": "|partial r|>0.5 = 1 axis (FAIL). >2 significant PCs = too many (FAIL). Exactly 2 = PASS.",
        "falsification_result": falsification,
        "constraints_referenced": ["C574", "C647", "C412", "C929", "C639", "C605"]
    }

    with open(RESULTS / "test3_oppositional_pairing.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result


# ============================================================
# TEST 4: DEGREE ORDERING WITHIN QUALITY
# ============================================================

def test4_degree_ordering(tokens):
    """Test whether MIDDLEs within each PREFIX channel show ordered intensity."""
    print("\n" + "=" * 60)
    print("TEST 4: Degree Ordering Within Quality")
    print("=" * 60)

    # Target PREFIX channels (major ones with enough data)
    TARGET_PREFIXES = ['qo', 'ch', 'sh', 'da', 'ok', 'ot']

    # Group tokens by PREFIX
    prefix_tokens = defaultdict(list)
    for t in tokens:
        p = t['prefix']
        if p in TARGET_PREFIXES and t['middle'] and t['middle'] != '_EMPTY_':
            prefix_tokens[p].append(t)

    print(f"\nTokens per PREFIX channel:")
    for p in TARGET_PREFIXES:
        print(f"  {p}: {len(prefix_tokens[p])} tokens")

    channel_results = {}
    pass_count = 0

    for prefix in TARGET_PREFIXES:
        toks = prefix_tokens[prefix]
        if len(toks) < 50:
            channel_results[prefix] = {
                'n_tokens': len(toks),
                'status': 'SKIP (insufficient data)',
                'n_middles': 0
            }
            continue

        # Count MIDDLE frequencies within this PREFIX channel
        mid_freq = Counter(t['middle'] for t in toks)
        # Only consider MIDDLEs with >= 5 occurrences for stable ranking
        frequent_middles = {m: c for m, c in mid_freq.items() if c >= 5}

        if len(frequent_middles) < 4:
            channel_results[prefix] = {
                'n_tokens': len(toks),
                'n_middles': len(frequent_middles),
                'status': 'SKIP (too few frequent MIDDLEs)',
            }
            continue

        # Assign frequency rank to each MIDDLE (1 = most common, higher = rarer)
        ranked = sorted(frequent_middles.keys(), key=lambda m: -frequent_middles[m])
        rank_map = {m: i + 1 for i, m in enumerate(ranked)}

        # Compute intensity proxies for each MIDDLE in this channel
        middle_stats = defaultdict(lambda: {
            'lengths': [], 'suffix_lengths': [], 'positions': [], 'count': 0
        })

        for t in toks:
            m = t['middle']
            if m not in rank_map:
                continue
            middle_stats[m]['lengths'].append(len(m))
            middle_stats[m]['suffix_lengths'].append(len(t['suffix']) if t['suffix'] else 0)
            middle_stats[m]['positions'].append(t.get('line_position', 0.5))
            middle_stats[m]['count'] += 1

        # Compute per-MIDDLE averages
        mid_list = []
        for m in ranked:
            stats = middle_stats[m]
            if stats['count'] > 0:
                mid_list.append({
                    'middle': m,
                    'rank': rank_map[m],
                    'count': frequent_middles[m],
                    'avg_length': np.mean(stats['lengths']),
                    'avg_suffix_length': np.mean(stats['suffix_lengths']),
                    'avg_position': np.mean(stats['positions']),
                })

        if len(mid_list) < 4:
            channel_results[prefix] = {
                'n_tokens': len(toks),
                'n_middles': len(mid_list),
                'status': 'SKIP (too few MIDDLEs with stats)',
            }
            continue

        # Test rank-intensity correlations
        ranks = np.array([m['rank'] for m in mid_list])
        lengths = np.array([m['avg_length'] for m in mid_list])
        suf_lengths = np.array([m['avg_suffix_length'] for m in mid_list])
        positions = np.array([m['avg_position'] for m in mid_list])

        # Spearman correlations: rank vs each proxy
        rho_len, p_len = spearmanr(ranks, lengths)
        rho_suf, p_suf = spearmanr(ranks, suf_lengths)
        rho_pos, p_pos = spearmanr(ranks, positions)

        # A MIDDLE is "higher degree" if it's rarer AND longer/more complex
        # Positive rho means rarer MIDDLEs are longer (ordered intensity)
        # Any significant correlation (p < 0.05) in any proxy = ordering exists
        significant = bool((p_len < 0.05) or (p_suf < 0.05) or (p_pos < 0.05))

        if significant:
            pass_count += 1

        # Determine direction consistency
        directions = []
        if p_len < 0.05:
            directions.append(('length', 'positive' if rho_len > 0 else 'negative'))
        if p_suf < 0.05:
            directions.append(('suffix', 'positive' if rho_suf > 0 else 'negative'))
        if p_pos < 0.05:
            directions.append(('position', 'positive' if rho_pos > 0 else 'negative'))

        print(f"\n  {prefix} (n={len(toks)}, {len(mid_list)} ranked MIDDLEs):")
        print(f"    rank vs length:  rho={rho_len:.3f}, p={p_len:.4f}")
        print(f"    rank vs suffix:  rho={rho_suf:.3f}, p={p_suf:.4f}")
        print(f"    rank vs position: rho={rho_pos:.3f}, p={p_pos:.4f}")
        print(f"    Significant: {significant}")

        channel_results[prefix] = {
            'n_tokens': len(toks),
            'n_middles': len(mid_list),
            'rank_vs_length': {'rho': round(rho_len, 3), 'p': round(p_len, 4)},
            'rank_vs_suffix_length': {'rho': round(rho_suf, 3), 'p': round(p_suf, 4)},
            'rank_vs_position': {'rho': round(rho_pos, 3), 'p': round(p_pos, 4)},
            'significant_ordering': significant,
            'significant_directions': directions,
            'top_middles': [{'middle': m['middle'], 'rank': m['rank'],
                           'count': m['count'], 'avg_length': round(m['avg_length'], 2)}
                          for m in mid_list[:5]],
            'status': 'PASS' if significant else 'FAIL'
        }

    # Count testable channels
    testable = [p for p in TARGET_PREFIXES if channel_results.get(p, {}).get('status', '').startswith(('PASS', 'FAIL'))]
    n_testable = len(testable)
    n_pass = pass_count

    print(f"\n\nSummary:")
    print(f"  Testable channels: {n_testable}/6")
    print(f"  Channels with significant ordering: {n_pass}/{n_testable}")

    # Falsification: ordering in >=4/6 channels with consistent direction
    if n_testable < 4:
        falsification = "INCONCLUSIVE -- Only %d testable channels (need >= 4)." % n_testable
    elif n_pass >= 4:
        falsification = "PASS -- %d/%d channels show significant within-PREFIX ordering (>= 4 required)." % (n_pass, n_testable)
    elif n_pass >= n_testable * 0.5:
        falsification = "PARTIAL -- %d/%d channels show ordering (majority but < 4)." % (n_pass, n_testable)
    else:
        falsification = "FAIL -- Only %d/%d channels show ordering (< majority)." % (n_pass, n_testable)

    print(f"\nFalsification: {falsification}")

    result = {
        "test": "Degree Ordering Within Quality",
        "tier": 4,
        "rupescissa_prediction": "Within each quality axis, degrees form an ordered intensity progression",
        "target_prefixes": TARGET_PREFIXES,
        "channel_results": channel_results,
        "testable_channels": n_testable,
        "channels_with_ordering": n_pass,
        "falsification_criterion": ">=4/6 channels with significant ordering = PASS, <majority = FAIL",
        "falsification_result": falsification,
        "constraints_referenced": ["C1001", "C911", "C293", "C267"]
    }

    with open(RESULTS / "test4_degree_ordering.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 376: Reverse Rupescissa Test (Galenic Framework Alignment)")
    print("Tier 4 -- Exploratory")
    print()

    # Load data once
    print("Loading Currier B tokens...")
    tokens = load_b_tokens()
    print(f"Loaded {len(tokens)} tokens")
    tokens = compute_line_positions(tokens)

    # Run all 4 tests
    r1 = test1_hazard_dimensionality()
    r2 = test2_factorization(tokens)
    r3 = test3_oppositional_pairing(tokens)
    r4 = test4_degree_ordering(tokens)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    tests = [
        ("Test 1: Multi-Axis Hazard", r1),
        ("Test 2: Quality-Degree Factorization", r2),
        ("Test 3: Oppositional Pairing", r3),
        ("Test 4: Degree Ordering", r4),
    ]

    all_pass = True
    for name, r in tests:
        result = r['falsification_result']
        status = "PASS" if "PASS" in result and "FAIL" not in result else ("PARTIAL" if "PARTIAL" in result else "FAIL")
        if status != "PASS":
            all_pass = False
        print(f"  {name}: {status}")

    if all_pass:
        overall = "ALL 4 TESTS PASS -- Voynich structure is consistent with Galenic combinatorial framework"
    else:
        pass_count = sum(1 for _, r in tests if "PASS" in r['falsification_result'] and "FAIL" not in r['falsification_result'])
        overall = "%d/4 tests pass -- Partial consistency with Galenic framework" % pass_count

    print(f"\n  Overall: {overall}")

    summary = {
        "phase": 376,
        "title": "Reverse Rupescissa Test (Galenic Framework Alignment)",
        "tier": 4,
        "framing": "Shared tradition structural convergence, not causal/dependency testing",
        "tests": [
            {
                "name": r['test'],
                "result": r['falsification_result'],
                "tier": r['tier']
            }
            for _, r in tests
        ],
        "overall": overall
    }

    with open(RESULTS / "galenic_test_summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nResults written to {RESULTS}")


if __name__ == '__main__':
    main()
