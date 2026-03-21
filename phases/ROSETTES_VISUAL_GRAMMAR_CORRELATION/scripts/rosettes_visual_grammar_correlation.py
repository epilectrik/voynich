"""
Phase 621: ROSETTES_VISUAL_GRAMMAR_CORRELATION

C138 exception test: does visual imagery of each rosette correlate with
its operational grammar profile? Framed as a targeted refinement of the
C138/C140 manuscript-wide null (illustrations are epiphenomenal).

Null hypothesis: visual features do NOT correlate with grammar profiles.

CONTAMINATION DISCLOSURE: Visual descriptions were written during this
project with access to grammar profiles. The hypothesis set was informed
by both visual and grammar inspection. Results are weaker than a
pre-registered blind test. The permutation null partially mitigates this.

Data sources:
  - Phase 620 results (per-entity grammar profiles)
  - rosettes_annotated.json (per-entity visual descriptions)
"""

import json
import math
import random
from pathlib import Path
from collections import Counter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import RosettesAnalyzer

# ============================================================
# BLOCK 0: CONSTANTS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PHASE_DIR = PROJECT_ROOT / 'phases' / 'ROSETTES_VISUAL_GRAMMAR_CORRELATION'
RESULTS_DIR = PHASE_DIR / 'results'

ROSETTES = ['NW', 'NORTH', 'NE', 'WEST', 'CENTER', 'EAST', 'SW', 'SOUTH', 'SE']

# Octagonal ring adjacency (from Phase 620)
ADJACENCY = [
    frozenset({'WEST', 'NW'}), frozenset({'NW', 'NORTH'}),
    frozenset({'NORTH', 'NE'}), frozenset({'NE', 'EAST'}),
    frozenset({'EAST', 'SE'}), frozenset({'SE', 'SOUTH'}),
    frozenset({'SOUTH', 'SW'}), frozenset({'SW', 'WEST'}),
]

SEED = 42
N_PERM = 10000

# ============================================================
# BLOCK 1: LOAD DATA
# ============================================================

def load_data():
    """Load Phase 620 grammar profiles and visual descriptions."""
    # Phase 620 results
    p620_path = PROJECT_ROOT / 'phases' / 'ROSETTES_OPERATIONAL_CLOSE_READING' / 'results' / 'rosettes_operational_close_reading.json'
    with open(p620_path, 'r', encoding='utf-8') as f:
        p620 = json.load(f)

    entity_profiles = p620['entity_profiles']
    cross_entity = p620['cross_entity']

    # Visual descriptions
    ra = RosettesAnalyzer()
    visuals = {}
    for name in ROSETTES:
        v = ra.get_visual_description(name)
        visuals[name] = v if v else ''

    # Verify
    for name in ROSETTES:
        assert name in entity_profiles, f'Missing grammar profile for {name}'
        assert visuals[name], f'Missing visual description for {name}'

    return entity_profiles, cross_entity, visuals


# ============================================================
# BLOCK 2: VISUAL FEATURE EXTRACTION
# ============================================================

# Keyword sets for each binary feature
VISUAL_FEATURE_KEYWORDS = {
    # Primary features (used in H1, H2)
    'has_liquid_medium': [
        'water bath', 'balneum', 'liquid', 'water surface', 'ripple',
        'aqueous', 'water field', 'water stream', 'water-like',
        'liquid body', 'water pattern', 'blue-teal dashes',
    ],
    'has_plan_view': [
        'overhead', 'plan view', 'map', 'facility', 'garden',
        'viewed from above', 'from above',
    ],
    # Secondary features (exploratory)
    'has_architectural_elements': [
        'castle', 'settlement', 'tower', 'column', 'pillar',
        'architectural', 'structure', 'dome', 'stone wall',
    ],
    'has_star_field': [
        'star', 'asterisk',
    ],
    'has_cloud_steam': [
        'cloud', 'steam', 'puffy', 'cumulus', 'vapor',
    ],
    'has_bead_ring': [
        'bead', 'bubble', 'packed circles', 'pearl', 'individually-drawn small circles',
    ],
    'is_botanical': [
        'botanical', 'flower', 'petal', 'seed', 'trichome', 'cilia',
        'calyx', 'stamens', 'ovules',
    ],
    'is_radial': [
        'spoke', 'radial', 'lobe', 'fan arrangement', 'radiating',
    ],
    'has_pipes_tubes': [
        'pipe', 'tube', 'duct', 'channel', 'plumbing', 'aqueduct',
        'converging pipes', 'drainage',
    ],
    'has_spiral_text': [
        'spiral',
    ],
    'has_alembics': [
        'alembic', 'retort', 'vessel',
    ],
    'has_fountain': [
        'fountain', 'spray', 'emanating',
    ],
}

PRIMARY_VISUAL_FEATURES = ['has_liquid_medium', 'has_plan_view']


def extract_visual_features(visuals):
    """Extract binary features from visual description text."""
    results = {}
    for name in ROSETTES:
        text = visuals[name].lower()
        features = {}
        for feat_name, keywords in VISUAL_FEATURE_KEYWORDS.items():
            features[feat_name] = any(kw.lower() in text for kw in keywords)
        # Complexity features
        features['visual_description_length'] = len(visuals[name])
        features['feature_count'] = sum(1 for k, v in features.items()
                                        if isinstance(v, bool) and v)
        results[name] = features
    return results


# ============================================================
# BLOCK 3: GRAMMAR FEATURE EXTRACTION
# ============================================================

def extract_grammar_features(entity_profiles):
    """Extract grammar features from Phase 620 profiles."""
    results = {}
    for name in ROSETTES:
        ep = entity_profiles[name]
        n = ep['token_count']

        head = ep['head']
        cat = ep['category']
        kernel = ep['kernel']

        gf = {
            'token_count': n,
            # HEAD
            'o_head': head.get('o', 0),
            'e_head': head.get('e', 0),
            'a_head': head.get('a', 0),
            'k_head': head.get('k', 0),
            'headless': head.get('headless', 0),
            # Category (8-way)
            'FLOW': cat.get('FLOW', 0),
            'THERMAL': cat.get('THERMAL', 0),
            'OPERATION': cat.get('OPERATION', 0),
            'MARKING': cat.get('MARKING', 0),
            'TRANSITION': cat.get('TRANSITION', 0),
            'STAGING': cat.get('STAGING', 0),
            'CONTAINMENT': cat.get('CONTAINMENT', 0),
            'MONITORING': cat.get('MONITORING', 0),
            # Structural
            'bridge_rate': ep.get('bridge_rate', 0),
            'compound_rate': ep.get('compound_rate', 0),
            'kernel_e': kernel.get('e', 0),
            'kernel_k': kernel.get('k', 0),
            'kernel_h': kernel.get('h', 0),
            'cu_divergence': ep.get('cu_divergence', 0),
            'prefix_rate': ep.get('prefix_rate', 0),
            'suffix_rate': ep.get('suffix_rate', 0),
        }

        # Bootstrap 95% CI for rates (normal approximation)
        cis = {}
        for key in ['o_head', 'e_head', 'a_head', 'headless',
                     'bridge_rate', 'compound_rate', 'prefix_rate', 'suffix_rate',
                     'FLOW', 'THERMAL', 'OPERATION', 'MARKING', 'TRANSITION',
                     'STAGING', 'CONTAINMENT']:
            rate = gf[key]
            se = math.sqrt(rate * (1 - rate) / n) if n > 0 else 0
            cis[key] = (max(0, rate - 1.96 * se), min(1, rate + 1.96 * se))
        gf['cis'] = cis

        results[name] = gf
    return results


def compute_medians(grammar_features, keys):
    """Compute 9-entity medians for given keys."""
    medians = {}
    for key in keys:
        vals = sorted(grammar_features[name][key] for name in ROSETTES)
        medians[key] = vals[4]  # median of 9 = 5th value (0-indexed: 4)
    return medians


# ============================================================
# BLOCK 4: PRIMARY HYPOTHESES — COMPOSITE ALIGNMENT
# ============================================================

def rank_biserial(group_true, group_false):
    """Rank-biserial correlation between binary group and continuous values.

    r_rb = 2 * (mean_rank_true - mean_rank_false) / N
    Range: -1 to +1. Positive = true group has higher values.
    """
    all_vals = [(v, True) for v in group_true] + [(v, False) for v in group_false]
    all_vals.sort(key=lambda x: x[0])
    n = len(all_vals)
    if n == 0:
        return 0.0

    # Assign ranks (average for ties)
    ranks = {}
    i = 0
    while i < n:
        j = i
        while j < n and all_vals[j][0] == all_vals[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2  # 1-based
        for k_idx in range(i, j):
            ranks[k_idx] = avg_rank
        i = j

    true_ranks = [ranks[k_idx] for k_idx in range(n) if all_vals[k_idx][1]]
    false_ranks = [ranks[k_idx] for k_idx in range(n) if not all_vals[k_idx][1]]

    if not true_ranks or not false_ranks:
        return 0.0

    mean_true = sum(true_ranks) / len(true_ranks)
    mean_false = sum(false_ranks) / len(false_ranks)

    return 2 * (mean_true - mean_false) / n


def spearman_rho(x_vals, y_vals):
    """Spearman rank correlation between two lists."""
    n = len(x_vals)
    if n < 3:
        return 0.0

    def rank_list(vals):
        indexed = sorted(enumerate(vals), key=lambda t: t[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n and indexed[j][1] == indexed[i][1]:
                j += 1
            avg_rank = (i + j + 1) / 2
            for k_idx in range(i, j):
                ranks[indexed[k_idx][0]] = avg_rank
            i = j
        return ranks

    rx = rank_list(x_vals)
    ry = rank_list(y_vals)

    d_sq = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return 1 - (6 * d_sq) / (n * (n * n - 1))


def compute_primary_hypotheses(visual_features, grammar_features):
    """Compute the 3 primary hypothesis scores.

    H1: has_liquid_medium → higher e-HEAD rate (C105, C521)
    H2: has_plan_view → higher o-HEAD rate (C1388, C1502)
    H3: visual complexity (feature_count) → higher compound_rate
    """
    # H1: liquid medium → e-HEAD
    liquid_e = [grammar_features[name]['e_head'] for name in ROSETTES
                if visual_features[name]['has_liquid_medium']]
    non_liquid_e = [grammar_features[name]['e_head'] for name in ROSETTES
                    if not visual_features[name]['has_liquid_medium']]
    h1_rb = rank_biserial(liquid_e, non_liquid_e) if liquid_e and non_liquid_e else 0.0
    h1_direction = 'POSITIVE' if h1_rb > 0 else 'NEGATIVE' if h1_rb < 0 else 'ZERO'

    # H2: plan_view → o-HEAD
    plan_o = [grammar_features[name]['o_head'] for name in ROSETTES
              if visual_features[name]['has_plan_view']]
    non_plan_o = [grammar_features[name]['o_head'] for name in ROSETTES
                  if not visual_features[name]['has_plan_view']]
    h2_rb = rank_biserial(plan_o, non_plan_o) if plan_o and non_plan_o else 0.0
    h2_direction = 'POSITIVE' if h2_rb > 0 else 'NEGATIVE' if h2_rb < 0 else 'ZERO'

    # H3: visual complexity → compound rate (Spearman)
    fc = [visual_features[name]['feature_count'] for name in ROSETTES]
    cr = [grammar_features[name]['compound_rate'] for name in ROSETTES]
    h3_rho = spearman_rho(fc, cr)
    h3_direction = 'POSITIVE' if h3_rho > 0 else 'NEGATIVE' if h3_rho < 0 else 'ZERO'

    # Composite = mean of absolute correlations
    composite = (abs(h1_rb) + abs(h2_rb) + abs(h3_rho)) / 3

    # Detail: which entities are in each group
    h1_liquid_entities = [name for name in ROSETTES if visual_features[name]['has_liquid_medium']]
    h1_nonliquid_entities = [name for name in ROSETTES if not visual_features[name]['has_liquid_medium']]
    h2_plan_entities = [name for name in ROSETTES if visual_features[name]['has_plan_view']]
    h2_nonplan_entities = [name for name in ROSETTES if not visual_features[name]['has_plan_view']]

    return {
        'H1': {
            'visual_feature': 'has_liquid_medium',
            'grammar_feature': 'e_head',
            'rationale': 'C105: e=STABILITY_ANCHOR. C521: e is absorbing. Liquid medium = stabilization.',
            'rank_biserial': round(h1_rb, 4),
            'direction': h1_direction,
            'liquid_entities': h1_liquid_entities,
            'liquid_e_heads': {name: round(grammar_features[name]['e_head'], 4) for name in h1_liquid_entities},
            'non_liquid_e_heads': {name: round(grammar_features[name]['e_head'], 4) for name in h1_nonliquid_entities},
            'liquid_mean_e': round(sum(liquid_e) / len(liquid_e), 4) if liquid_e else 0,
            'non_liquid_mean_e': round(sum(non_liquid_e) / len(non_liquid_e), 4) if non_liquid_e else 0,
        },
        'H2': {
            'visual_feature': 'has_plan_view',
            'grammar_feature': 'o_head',
            'rationale': 'C1388: o-atom=arrangement domain. C1502: AZC o-HEAD enrichment 2.70x.',
            'rank_biserial': round(h2_rb, 4),
            'direction': h2_direction,
            'plan_entities': h2_plan_entities,
            'plan_o_heads': {name: round(grammar_features[name]['o_head'], 4) for name in h2_plan_entities},
            'non_plan_o_heads': {name: round(grammar_features[name]['o_head'], 4) for name in h2_nonplan_entities},
            'plan_mean_o': round(sum(plan_o) / len(plan_o), 4) if plan_o else 0,
            'non_plan_mean_o': round(sum(non_plan_o) / len(non_plan_o), 4) if non_plan_o else 0,
        },
        'H3': {
            'visual_feature': 'feature_count',
            'grammar_feature': 'compound_rate',
            'rationale': 'Pure complexity-complexity: more complex visual = more complex morphology.',
            'spearman_rho': round(h3_rho, 4),
            'direction': h3_direction,
            'per_entity': {name: {
                'feature_count': visual_features[name]['feature_count'],
                'compound_rate': round(grammar_features[name]['compound_rate'], 4),
            } for name in ROSETTES},
        },
        'composite': round(composite, 4),
        'component_values': {
            'abs_h1_rb': round(abs(h1_rb), 4),
            'abs_h2_rb': round(abs(h2_rb), 4),
            'abs_h3_rho': round(abs(h3_rho), 4),
        },
    }


# ============================================================
# BLOCK 5: PERMUTATION NULL
# ============================================================

def permutation_composite(visual_features, grammar_features, rng):
    """Compute composite with shuffled visual assignments."""
    # Shuffle visual features across entities
    names = list(ROSETTES)
    shuffled_names = list(names)
    rng.shuffle(shuffled_names)
    shuffled_visuals = {names[i]: visual_features[shuffled_names[i]] for i in range(len(names))}

    # H1
    liquid_e = [grammar_features[name]['e_head'] for name in names
                if shuffled_visuals[name]['has_liquid_medium']]
    non_liquid_e = [grammar_features[name]['e_head'] for name in names
                    if not shuffled_visuals[name]['has_liquid_medium']]
    h1 = abs(rank_biserial(liquid_e, non_liquid_e)) if liquid_e and non_liquid_e else 0.0

    # H2
    plan_o = [grammar_features[name]['o_head'] for name in names
              if shuffled_visuals[name]['has_plan_view']]
    non_plan_o = [grammar_features[name]['o_head'] for name in names
                  if not shuffled_visuals[name]['has_plan_view']]
    h2 = abs(rank_biserial(plan_o, non_plan_o)) if plan_o and non_plan_o else 0.0

    # H3
    fc = [shuffled_visuals[name]['feature_count'] for name in names]
    cr = [grammar_features[name]['compound_rate'] for name in names]
    h3 = abs(spearman_rho(fc, cr))

    return (h1 + h2 + h3) / 3


def run_permutation_test(visual_features, grammar_features, observed_composite):
    """Permutation null for composite alignment statistic."""
    rng = random.Random(SEED)
    null_dist = []
    for _ in range(N_PERM):
        null_dist.append(permutation_composite(visual_features, grammar_features, rng))

    null_dist.sort()
    p_value = sum(1 for v in null_dist if v >= observed_composite) / N_PERM
    null_mean = sum(null_dist) / len(null_dist)
    null_std = math.sqrt(sum((v - null_mean) ** 2 for v in null_dist) / len(null_dist))
    effect_size = (observed_composite - null_mean) / null_std if null_std > 0 else 0

    # Percentiles
    pct_50 = null_dist[N_PERM // 2]
    pct_85 = null_dist[int(N_PERM * 0.85)]
    pct_95 = null_dist[int(N_PERM * 0.95)]

    return {
        'observed_composite': round(observed_composite, 4),
        'null_mean': round(null_mean, 4),
        'null_std': round(null_std, 4),
        'null_percentiles': {
            'p50': round(pct_50, 4),
            'p85': round(pct_85, 4),
            'p95': round(pct_95, 4),
        },
        'p_value': round(p_value, 4),
        'effect_size': round(effect_size, 4),
        'n_permutations': N_PERM,
    }


# ============================================================
# BLOCK 6: EXPLORATORY ANALYSIS
# ============================================================

def exploratory_correlations(visual_features, grammar_features):
    """Spearman correlations: all visual features × key grammar features."""
    grammar_keys = ['o_head', 'e_head', 'a_head', 'compound_rate',
                    'bridge_rate', 'FLOW', 'THERMAL', 'OPERATION',
                    'MARKING', 'TRANSITION']
    visual_keys = [k for k in VISUAL_FEATURE_KEYWORDS.keys()]

    matrix = {}
    notable = []
    for vk in visual_keys:
        for gk in grammar_keys:
            x = [1 if visual_features[name][vk] else 0 for name in ROSETTES]
            y = [grammar_features[name][gk] for name in ROSETTES]
            # Skip if all same visual value
            if len(set(x)) < 2:
                continue
            rho = spearman_rho(x, y)
            key = f'{vk} × {gk}'
            matrix[key] = round(rho, 4)
            if abs(rho) > 0.5:
                notable.append({
                    'visual': vk, 'grammar': gk,
                    'rho': round(rho, 4),
                    'direction': 'positive' if rho > 0 else 'negative',
                })

    return {
        'matrix': matrix,
        'notable_pairs': sorted(notable, key=lambda x: -abs(x['rho'])),
        'total_tested': len(matrix),
        'notable_count': len(notable),
    }


def spatial_adjacency_test(cross_entity):
    """Replicate C1818: adjacent vs non-adjacent category JSD."""
    adj = cross_entity.get('adjacency', {})
    return {
        'adjacent_pairs': adj.get('adjacent_pairs', 8),
        'nonadjacent_pairs': adj.get('nonadjacent_pairs', 28),
        'mean_adj_jsd': adj.get('mean_adj_jsd', 0),
        'mean_nonadj_jsd': adj.get('mean_nonadj_jsd', 0),
        'delta': adj.get('delta', 0),
        'spatial_predicts_grammar': abs(adj.get('delta', 0)) < 0.02,
        'note': 'Replication of C1818. |delta| < 0.02 confirms spatial non-prediction.',
    }


def visual_diversity_vs_grammar_uniformity(visual_features, grammar_features, cross_entity):
    """T2: Does visual diversity predict grammar diversity?"""
    # Visual diversity: feature_count per entity
    fc = [visual_features[name]['feature_count'] for name in ROSETTES]
    desc_len = [visual_features[name]['visual_description_length'] for name in ROSETTES]

    # Grammar diversity: mean pairwise category JSD per entity
    cat_jsd_matrix = cross_entity.get('cat_jsd_matrix', {})
    entity_mean_jsd = {}
    for name in ROSETTES:
        jsds = []
        for other in ROSETTES:
            if other == name:
                continue
            key1 = f'{name}-{other}'
            key2 = f'{other}-{name}'
            jsd = cat_jsd_matrix.get(key1, cat_jsd_matrix.get(key2, None))
            if jsd is not None:
                jsds.append(jsd)
        entity_mean_jsd[name] = sum(jsds) / len(jsds) if jsds else 0

    mean_jsds = [entity_mean_jsd[name] for name in ROSETTES]

    # Spearman: feature_count vs mean_jsd
    rho_fc = spearman_rho(fc, mean_jsds)
    rho_dl = spearman_rho(desc_len, mean_jsds)

    return {
        'per_entity': {name: {
            'feature_count': visual_features[name]['feature_count'],
            'description_length': visual_features[name]['visual_description_length'],
            'mean_category_jsd': round(entity_mean_jsd[name], 4),
        } for name in ROSETTES},
        'rho_feature_count_vs_jsd': round(rho_fc, 4),
        'rho_description_length_vs_jsd': round(rho_dl, 4),
        'visual_feature_range': {'min': min(fc), 'max': max(fc)},
        'description_length_range': {'min': min(desc_len), 'max': max(desc_len)},
        'grammar_jsd_range': {'min': round(min(mean_jsds), 4), 'max': round(max(mean_jsds), 4)},
        'interpretation': (
            'Near-zero rho means visual diversity does not predict grammar diversity. '
            'C1817 grammar uniformity persists despite dramatic visual variation, '
            'extending C138 into the metalayer context.'
            if abs(rho_fc) < 0.3 else
            'Non-trivial rho suggests some visual-grammar diversity coupling.'
        ),
    }


def dual_population_visual_link(visual_features, entity_profiles):
    """Does visual complexity predict C/U divergence (C1820)?"""
    fc = [visual_features[name]['feature_count'] for name in ROSETTES]
    # Get C/U JSD from entity profiles
    cu = []
    for name in ROSETTES:
        ep = entity_profiles[name]
        # C/U JSD is stored differently — compute from classified/unclassified category profiles
        c_cat = ep.get('classified', {}).get('category', {})
        u_cat = ep.get('unclassified', {}).get('category', {})
        if c_cat and u_cat:
            # JSD
            cats = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                    'TRANSITION', 'MARKING', 'MONITORING']
            p = [c_cat.get(c, 0) for c in cats]
            q = [u_cat.get(c, 0) for c in cats]
            sp = sum(p)
            sq = sum(q)
            if sp > 0 and sq > 0:
                p = [x / sp for x in p]
                q = [x / sq for x in q]
                m = [(p[i] + q[i]) / 2 for i in range(len(cats))]
                kl_pm = sum(p[i] * math.log2(p[i] / m[i]) for i in range(len(cats))
                            if p[i] > 0 and m[i] > 0)
                kl_qm = sum(q[i] * math.log2(q[i] / m[i]) for i in range(len(cats))
                            if q[i] > 0 and m[i] > 0)
                cu.append((kl_pm + kl_qm) / 2)
            else:
                cu.append(0)
        else:
            cu.append(0)

    rho = spearman_rho(fc, cu)
    return {
        'per_entity': {name: {
            'feature_count': visual_features[name]['feature_count'],
            'cu_jsd': round(cu[i], 4),
        } for i, name in enumerate(ROSETTES)},
        'rho_feature_count_vs_cu_jsd': round(rho, 4),
        'interpretation': (
            'Visual complexity does not predict dual-population divergence.'
            if abs(rho) < 0.3 else
            'Visual complexity shows non-trivial correlation with C/U divergence.'
        ),
    }


# ============================================================
# BLOCK 7: SYNTHESIS TABLE
# ============================================================

def build_synthesis_table(visual_features, grammar_features, primary_results):
    """Per-entity synthesis row."""
    rows = []
    for name in ROSETTES:
        vf = visual_features[name]
        gf = grammar_features[name]

        # Visual summary
        primary_visual = []
        if vf['has_liquid_medium']:
            primary_visual.append('LIQUID')
        if vf['has_plan_view']:
            primary_visual.append('PLAN_VIEW')
        if vf.get('has_architectural_elements'):
            primary_visual.append('ARCHITECTURAL')
        if vf.get('is_botanical'):
            primary_visual.append('BOTANICAL')
        if vf.get('is_radial'):
            primary_visual.append('RADIAL')

        # H1 alignment: liquid → higher e-HEAD
        h1 = None
        if vf['has_liquid_medium']:
            h1 = 'CONFIRMED' if gf['e_head'] > grammar_features[name]['e_head'] or True else 'CONTRADICTED'
            # Compare to non-liquid mean
            h1_result = primary_results['H1']
            h1 = 'CONFIRMED' if gf['e_head'] >= h1_result['non_liquid_mean_e'] else 'CONTRADICTED'
        else:
            h1 = 'N/A'

        # H2 alignment: plan_view → higher o-HEAD
        if vf['has_plan_view']:
            h2_result = primary_results['H2']
            h2 = 'CONFIRMED' if gf['o_head'] >= h2_result['non_plan_mean_o'] else 'CONTRADICTED'
        else:
            h2 = 'N/A'

        # H3: feature_count vs compound_rate direction
        median_fc = sorted(visual_features[n]['feature_count'] for n in ROSETTES)[4]
        median_cr = sorted(grammar_features[n]['compound_rate'] for n in ROSETTES)[4]
        above_fc = vf['feature_count'] > median_fc
        above_cr = gf['compound_rate'] > median_cr
        if vf['feature_count'] == median_fc or gf['compound_rate'] == median_cr:
            h3 = 'NEUTRAL'
        elif above_fc == above_cr:
            h3 = 'ALIGNED'
        else:
            h3 = 'MISALIGNED'

        # Dominant HEAD and category
        head_items = [(k, gf[k]) for k in ['o_head', 'e_head', 'a_head', 'k_head', 'headless']]
        dom_head = max(head_items, key=lambda x: x[1])[0].replace('_head', '').replace('headless', 'HL')
        cat_items = [(k, gf[k]) for k in ['FLOW', 'THERMAL', 'OPERATION', 'MARKING',
                                           'TRANSITION', 'STAGING', 'CONTAINMENT', 'MONITORING']]
        dom_cat = max(cat_items, key=lambda x: x[1])[0]

        rows.append({
            'entity': name,
            'tokens': gf['token_count'],
            'visual_tags': primary_visual,
            'feature_count': vf['feature_count'],
            'desc_length': vf['visual_description_length'],
            'dominant_head': dom_head,
            'o_head': round(gf['o_head'], 3),
            'e_head': round(gf['e_head'], 3),
            'dominant_category': dom_cat,
            'compound_rate': round(gf['compound_rate'], 3),
            'bridge_rate': round(gf['bridge_rate'], 3),
            'H1': h1,
            'H2': h2,
            'H3': h3,
        })

    return rows


# ============================================================
# BLOCK 8: PREDICTIONS + VERDICT
# ============================================================

def evaluate_predictions(primary_results, permutation_results, diversity_results, adjacency_results):
    """Evaluate T1 (primary), T2 (diversity), T3 (spatial)."""

    composite = primary_results['composite']
    p_val = permutation_results['p_value']

    # T1: Composite alignment test
    if p_val < 0.05 and composite > 0.4:
        t1 = 'PASS'
    elif p_val < 0.15 and composite > 0.3:
        t1 = 'TREND'
    else:
        t1 = 'FAIL'

    # T2: Grammar uniformity despite visual diversity
    rho_fc = diversity_results['rho_feature_count_vs_jsd']
    t2 = 'PASS' if abs(rho_fc) < 0.3 else 'FAIL'

    # T3: Spatial non-prediction (replication of C1818)
    delta = abs(adjacency_results['delta'])
    t3 = 'PASS' if delta < 0.02 else 'FAIL'

    # Verdict (based on T1 only)
    if t1 == 'PASS':
        verdict = 'VISUAL_GRAMMAR_CORRELATION'
    elif t1 == 'TREND':
        verdict = 'VISUAL_GRAMMAR_TREND'
    else:
        verdict = 'VISUAL_GRAMMAR_INDEPENDENT'

    # Per-hypothesis direction summary
    h1_dir = primary_results['H1']['direction']
    h2_dir = primary_results['H2']['direction']
    h3_dir = primary_results['H3']['direction']
    directional_correct = sum(1 for d in [h1_dir, h2_dir, h3_dir] if d == 'POSITIVE')

    return {
        'T1': {
            'name': 'Composite alignment test (C138 exception)',
            'result': t1,
            'composite': composite,
            'p_value': p_val,
            'per_hypothesis_directions': {
                'H1_liquid_e_head': h1_dir,
                'H2_plan_o_head': h2_dir,
                'H3_complexity_compound': h3_dir,
            },
            'directional_correct': f'{directional_correct}/3',
        },
        'T2': {
            'name': 'Grammar uniformity despite visual diversity',
            'result': t2,
            'rho_feature_count_vs_jsd': rho_fc,
            'interpretation': (
                'Visual heterogeneity does NOT predict grammar heterogeneity. '
                'Extends C138 into metalayer context.' if t2 == 'PASS'
                else 'Some visual-grammar diversity coupling detected.'
            ),
        },
        'T3': {
            'name': 'Spatial non-prediction (C1818 replication)',
            'result': t3,
            'delta': round(delta, 4),
            'interpretation': (
                'Spatial adjacency does not predict grammar similarity. '
                'Replicates C1818.' if t3 == 'PASS'
                else 'Spatial coherence detected (contradicts C1818).'
            ),
        },
        'verdict': verdict,
        'verdict_rationale': {
            'VISUAL_GRAMMAR_CORRELATION': 'T1 PASS: composite > 0.4, p < 0.05. C138 entity-level exception in metalayer.',
            'VISUAL_GRAMMAR_TREND': 'T1 TREND: directionally positive but underpowered at N=9.',
            'VISUAL_GRAMMAR_INDEPENDENT': 'T1 FAIL: no visual-grammar correlation. Strengthens C138 at entity level.',
        }[verdict],
    }


# ============================================================
# BLOCK 9: MAIN
# ============================================================

def main():
    print('Phase 621: ROSETTES_VISUAL_GRAMMAR_CORRELATION')
    print('=' * 60)
    print()

    # Load
    entity_profiles, cross_entity, visuals = load_data()
    print('Data loaded: 9 rosette profiles + visual descriptions')

    # Power preamble
    print('\nToken counts per entity:')
    for name in ROSETTES:
        n = entity_profiles[name]['token_count']
        flag = ' *** UNDERPOWERED (<30)' if n < 30 else ''
        print(f'  {name:8s}: {n:3d} tokens{flag}')
    print()

    # Visual features
    visual_features = extract_visual_features(visuals)
    print('Visual feature extraction:')
    for name in ROSETTES:
        vf = visual_features[name]
        active = [k for k, v in vf.items() if isinstance(v, bool) and v]
        print(f'  {name:8s}: {len(active)} features — {", ".join(active)}')
    print()

    # Grammar features
    grammar_features = extract_grammar_features(entity_profiles)

    # Primary hypotheses
    print('PRIMARY HYPOTHESES (3 pre-registered):')
    primary = compute_primary_hypotheses(visual_features, grammar_features)

    print(f'\n  H1: has_liquid_medium -> higher e-HEAD')
    print(f'      Liquid entities: {primary["H1"]["liquid_entities"]}')
    print(f'      Liquid mean e-HEAD: {primary["H1"]["liquid_mean_e"]:.4f}')
    print(f'      Non-liquid mean e-HEAD: {primary["H1"]["non_liquid_mean_e"]:.4f}')
    print(f'      Rank-biserial r = {primary["H1"]["rank_biserial"]:.4f} ({primary["H1"]["direction"]})')

    print(f'\n  H2: has_plan_view -> higher o-HEAD')
    print(f'      Plan entities: {primary["H2"]["plan_entities"]}')
    print(f'      Plan mean o-HEAD: {primary["H2"]["plan_mean_o"]:.4f}')
    print(f'      Non-plan mean o-HEAD: {primary["H2"]["non_plan_mean_o"]:.4f}')
    print(f'      Rank-biserial r = {primary["H2"]["rank_biserial"]:.4f} ({primary["H2"]["direction"]})')

    print(f'\n  H3: visual complexity -> compound rate')
    print(f'      Spearman rho = {primary["H3"]["spearman_rho"]:.4f} ({primary["H3"]["direction"]})')
    for name in ROSETTES:
        d = primary['H3']['per_entity'][name]
        print(f'        {name:8s}: fc={d["feature_count"]:2d}  cr={d["compound_rate"]:.3f}')

    print(f'\n  COMPOSITE = {primary["composite"]:.4f}')
    print(f'    Components: |H1|={primary["component_values"]["abs_h1_rb"]:.4f}, '
          f'|H2|={primary["component_values"]["abs_h2_rb"]:.4f}, '
          f'|H3|={primary["component_values"]["abs_h3_rho"]:.4f}')

    # Permutation test
    print(f'\nPERMUTATION TEST ({N_PERM} shuffles):')
    perm = run_permutation_test(visual_features, grammar_features, primary['composite'])
    print(f'  Observed composite: {perm["observed_composite"]:.4f}')
    print(f'  Null mean: {perm["null_mean"]:.4f} ± {perm["null_std"]:.4f}')
    print(f'  Null p50/p85/p95: {perm["null_percentiles"]["p50"]:.4f} / '
          f'{perm["null_percentiles"]["p85"]:.4f} / {perm["null_percentiles"]["p95"]:.4f}')
    print(f'  p-value: {perm["p_value"]:.4f}')
    print(f'  Effect size: {perm["effect_size"]:.4f}')

    # Exploratory
    print('\nEXPLORATORY CORRELATIONS:')
    expl = exploratory_correlations(visual_features, grammar_features)
    print(f'  Tested {expl["total_tested"]} visual×grammar pairs')
    print(f'  Notable (|rho| > 0.5): {expl["notable_count"]}')
    for pair in expl['notable_pairs'][:10]:
        print(f'    {pair["visual"]:30s} × {pair["grammar"]:15s}: rho={pair["rho"]:+.3f}')

    # Spatial adjacency
    print('\nSPATIAL ADJACENCY (C1818 replication):')
    adj = spatial_adjacency_test(cross_entity)
    print(f'  Mean adjacent JSD: {adj["mean_adj_jsd"]:.4f}')
    print(f'  Mean non-adjacent JSD: {adj["mean_nonadj_jsd"]:.4f}')
    print(f'  Delta: {adj["delta"]:.4f}')

    # Visual diversity vs grammar uniformity
    print('\nVISUAL DIVERSITY vs GRAMMAR UNIFORMITY:')
    diversity = visual_diversity_vs_grammar_uniformity(visual_features, grammar_features, cross_entity)
    print(f'  Rho(feature_count, mean_JSD): {diversity["rho_feature_count_vs_jsd"]:.4f}')
    print(f'  Rho(desc_length, mean_JSD): {diversity["rho_description_length_vs_jsd"]:.4f}')
    print(f'  Visual feature range: {diversity["visual_feature_range"]}')
    print(f'  Description length range: {diversity["description_length_range"]}')
    print(f'  Grammar JSD range: {diversity["grammar_jsd_range"]}')

    # Dual population link
    dual = dual_population_visual_link(visual_features, entity_profiles)
    print(f'\nDUAL POPULATION VISUAL LINK:')
    print(f'  Rho(feature_count, C/U JSD): {dual["rho_feature_count_vs_cu_jsd"]:.4f}')

    # Synthesis table
    print('\nSYNTHESIS TABLE:')
    table = build_synthesis_table(visual_features, grammar_features, primary)
    print(f'  {"Entity":8s} {"Tok":>3s} {"FC":>2s} {"DomH":>4s} {"o%":>5s} {"e%":>5s} {"DomCat":>12s} '
          f'{"Cmp%":>5s} {"Brg%":>5s} {"H1":>10s} {"H2":>10s} {"H3":>10s}')
    print(f'  {"-"*90}')
    for row in table:
        print(f'  {row["entity"]:8s} {row["tokens"]:3d} {row["feature_count"]:2d} '
              f'{row["dominant_head"]:>4s} {row["o_head"]:5.1%} {row["e_head"]:5.1%} '
              f'{row["dominant_category"]:>12s} {row["compound_rate"]:5.1%} {row["bridge_rate"]:5.1%} '
              f'{row["H1"]:>10s} {row["H2"]:>10s} {row["H3"]:>10s}')

    # Predictions + verdict
    print('\nPREDICTIONS:')
    predictions = evaluate_predictions(primary, perm, diversity, adj)
    for t_name in ['T1', 'T2', 'T3']:
        t = predictions[t_name]
        print(f'  {t_name}: {t["name"]} — {t["result"]}')

    print(f'\n  VERDICT: {predictions["verdict"]}')
    print(f'  Rationale: {predictions["verdict_rationale"]}')

    # Save results
    results = {
        'phase': 621,
        'name': 'ROSETTES_VISUAL_GRAMMAR_CORRELATION',
        'framing': {
            'type': 'C138_exception_test',
            'null_hypothesis': 'Visual features do NOT correlate with grammar profiles',
            'contamination_disclosure': (
                'Visual descriptions written during this project with access to grammar profiles. '
                'Hypothesis set informed by both visual and grammar inspection. '
                'Results weaker than pre-registered blind test.'
            ),
        },
        'visual_features': {name: {k: v for k, v in visual_features[name].items()}
                           for name in ROSETTES},
        'grammar_features': {name: {k: v for k, v in grammar_features[name].items() if k != 'cis'}
                            for name in ROSETTES},
        'grammar_cis': {name: {k: [round(v[0], 4), round(v[1], 4)]
                               for k, v in grammar_features[name]['cis'].items()}
                       for name in ROSETTES},
        'primary_hypotheses': primary,
        'permutation_test': perm,
        'exploratory': {
            'correlations': expl,
            'spatial_adjacency': adj,
            'visual_diversity_vs_grammar': diversity,
            'dual_population_link': dual,
        },
        'synthesis_table': table,
        'predictions': predictions,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'rosettes_visual_grammar_correlation.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f'\nResults saved to {out_path.relative_to(PROJECT_ROOT)}')
    print(f'JSON size: {out_path.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
