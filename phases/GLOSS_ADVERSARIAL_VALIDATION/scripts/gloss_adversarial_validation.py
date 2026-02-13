#!/usr/bin/env python3
"""Phase 337: Gloss Adversarial Validation (Final Glossing Phase).

Two orthogonal tests of gloss structural grounding:
T1: PREFIX-domain assignment uniqueness (exhaustive 6-permutation scoring)
T2: Mantel test (behavioral signature distance vs gloss category distance)
T3: Non-circular Mantel (ablated features)
T4: Per-category Mantel decomposition (diagnostic)

Non-circularity: C911 selectivity (2026-01-20), C601 hazard (2026-01-17),
C997 buffers (2026-02-08), C995 affordance (2026-02-03), glosses from
Brunschwig (Phase 330, 2026-02-06). Five independent derivations.
"""

import json
import sys
import functools
import itertools
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Pre-registered gloss categories (identical to Phase 336) ─────

GLOSS_CATEGORIES = {
    'THERMAL': [
        'cool', 'heat', 'fire', 'warm', 'deep', 'extended', 'overnight',
        'settle', 'steady',
    ],
    'CONTAINMENT': [
        'seal', 'close', 'lock', 'frame', 'hold', 'bind', 'rigid', 'firm',
        'hard',
    ],
    'FLOW': [
        'intake', 'open', 'transfer', 'collect', 'gather', 'route',
        'discharge', 'vent', 'release', 'pour',
    ],
    'MONITORING': [
        'check', 'watch', 'verify', 'scan', 'observe', 'control', 'exact',
        'precise', 'measure', 'danger', 'hazard',
    ],
    'OPERATION': [
        'set', 'portion', 'work', 'operate', 'step', 'pound', 'strip',
        'adjust', 'regulate', 'pulse', 'sustain',
    ],
    'TRANSITION': [
        'end', 'break', 'halt', 'finish', 'finalize', 'yield', 'pause',
        'complete',
    ],
    'STAGING': [
        'start', 'early', 'mid', 'late', 'final', 'batch', 'cycle',
        'iterate', 'repeat', 'continue', 'loop',
    ],
    'STRUCTURAL': [
        'stand', 'flag', 'mark', 'path', 'link', 'diagram', 'bond',
        'dense', 'wide', 'long',
    ],
}


def categorize_gloss(gloss):
    """Assign a gloss string to a pre-registered category."""
    if not gloss:
        return 'UNGLOSSED'
    gloss_lower = gloss.lower()
    for cat, keywords in GLOSS_CATEGORIES.items():
        for kw in keywords:
            if kw in gloss_lower:
                return cat
    return 'OTHER'


# ── PREFIX domain constants ──────────────────────────────────────

PREFIX_FAMILIES = {
    'qo': ['qo'],
    'ok': ['ok'],
    'chsh': ['ch', 'sh'],
}
DOMAIN_LABELS = ['ENERGY', 'VESSEL', 'PROCESS']

# Features for behavioral signature
FULL_FEATURES = [
    'radial_depth', 'compat_degree', 'token_frequency',
    'length', 'k_ratio', 'e_ratio', 'h_ratio', 'is_compound', 'qo_affinity',
    'regime_1_enrichment', 'regime_2_enrichment', 'regime_3_enrichment',
    'regime_4_enrichment', 'regime_entropy', 'initial_rate', 'final_rate',
    'folio_spread',
]

ABLATED_FEATURES = ['k_ratio', 'e_ratio', 'h_ratio', 'qo_affinity']

REDUCED_FEATURES = [f for f in FULL_FEATURES if f not in ABLATED_FEATURES]


# ── Load data ────────────────────────────────────────────────────

def load_data():
    print("Loading data...")

    morph = Morphology()
    tx = Transcript()

    # 1. MIDDLE dictionary (glosses)
    with open(PROJECT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
        mid_dict = json.load(f)

    glossed_middles = {}
    for mid, info in mid_dict['middles'].items():
        if info.get('gloss'):
            glossed_middles[mid] = info['gloss']

    middle_to_cat = {mid: categorize_gloss(g) for mid, g in glossed_middles.items()}
    print(f"  {len(glossed_middles)} glossed MIDDLEs")

    # 2. C911 PREFIX-MIDDLE interaction
    with open(PROJECT / 'phases' / 'MIDDLE_SEMANTIC_DEEPENING' / 'results' /
              'prefix_middle_interaction.json', encoding='utf-8') as f:
        c911 = json.load(f)

    enrichment_lookup = {}
    for ep in c911['enriched_pairs']:
        key = (ep['prefix'], ep['middle'])
        enrichment_lookup[key] = ep['ratio']

    forbidden_pm_lookup = set()
    for fp in c911['forbidden_pairs']:
        forbidden_pm_lookup.add((fp['prefix'], fp['middle']))

    print(f"  C911: {len(enrichment_lookup)} enriched, {len(forbidden_pm_lookup)} forbidden PREFIX-MIDDLE pairs")

    # 3. C997 safety buffers
    with open(PROJECT / 'phases' / 'BIN_HAZARD_NECESSITY' / 'results' /
              'safety_buffer_scan.json', encoding='utf-8') as f:
        buffers = json.load(f)

    # Extract PREFIX of each buffer token
    buffer_prefix_counts = Counter()
    buffer_prefix_detail = {}
    for token_str, count in buffers['buffer_tokens'].items():
        m = morph.extract(token_str)
        pfx = m.prefix if m and m.prefix else '(none)'
        buffer_prefix_counts[pfx] += count
        buffer_prefix_detail[token_str] = pfx

    print(f"  C997: {buffers['n_buffers']} buffers, PREFIX dist: {dict(buffer_prefix_counts)}")

    # 4. Forbidden transition inventory (Phase 18)
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' /
              'phase18a_forbidden_inventory.json', encoding='utf-8') as f:
        inventory = json.load(f)

    # Resolve forbidden pair entities to MIDDLEs
    forbidden_middle_pairs = []
    for t in inventory['transitions']:
        s_m = morph.extract(t['source'])
        t_m = morph.extract(t['target'])
        s_mid = s_m.middle if s_m and s_m.middle else t['source']
        t_mid = t_m.middle if t_m and t_m.middle else t['target']
        forbidden_middle_pairs.append((t['source'], t['target'], s_mid, t_mid))

    print(f"  {len(forbidden_middle_pairs)} forbidden transitions")

    # 5. Affordance table
    with open(PROJECT / 'data' / 'middle_affordance_table.json', encoding='utf-8') as f:
        affordance = json.load(f)

    # MIDDLEs are nested under 'middles' key
    affordance_middles = affordance.get('middles', {})
    print(f"  {len(affordance_middles)} MIDDLEs in affordance table")

    # 6. Build top-49 MIDDLEs from B corpus
    mid_freq = Counter()
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m and m.middle:
            mid_freq[m.middle] += 1

    top49 = [mid for mid, _ in mid_freq.most_common(49)]
    print(f"  Top-49 B MIDDLEs: {top49[:10]}...")

    # 7. Build B corpus line data for S3/S5 (pre-compute)
    # Group tokens by folio+line, extract (PREFIX, MIDDLE, entity) per position
    line_tokens = defaultdict(list)
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m and m.middle:
            pfx = m.prefix if m.prefix else '(none)'
            line_tokens[(token.folio, token.line)].append({
                'prefix': pfx,
                'middle': m.middle,
                'entity': w,
            })

    print(f"  {len(line_tokens)} B lines with tokens")

    return {
        'morph': morph,
        'glossed_middles': glossed_middles,
        'middle_to_cat': middle_to_cat,
        'enrichment_lookup': enrichment_lookup,
        'forbidden_pm_lookup': forbidden_pm_lookup,
        'buffer_prefix_counts': buffer_prefix_counts,
        'buffer_prefix_detail': buffer_prefix_detail,
        'buffer_total': buffers['n_buffers'],
        'forbidden_middle_pairs': forbidden_middle_pairs,
        'affordance_middles': affordance_middles,
        'top49': top49,
        'mid_freq': mid_freq,
        'line_tokens': dict(line_tokens),
    }


# ── T1: PREFIX-Domain Assignment Uniqueness ──────────────────────

def get_enrichment(enrichment_lookup, forbidden_pm_lookup, prefix_family, middle):
    """Get enrichment ratio for a PREFIX family with a given MIDDLE.

    Returns: mean ratio across family members.
    - If pair is in enriched_pairs, use ratio.
    - If pair is in forbidden_pairs, score = 0.0 (actively suppressed).
    - If pair is in neither, score = 1.0 (neutral/baseline).
    """
    ratios = []
    for pfx in prefix_family:
        key = (pfx, middle)
        if key in enrichment_lookup:
            ratios.append(enrichment_lookup[key])
        elif key in forbidden_pm_lookup:
            ratios.append(0.0)
        else:
            ratios.append(1.0)
    return np.mean(ratios) if ratios else 1.0


def compute_s1(enrichment_lookup, forbidden_pm_lookup, assignment):
    """S1: k-family enrichment of ENERGY-domain PREFIX."""
    energy_family_key = [k for k, v in assignment.items() if v == 'ENERGY'][0]
    energy_prefixes = PREFIX_FAMILIES[energy_family_key]
    return get_enrichment(enrichment_lookup, forbidden_pm_lookup, energy_prefixes, 'k')


def compute_s2(enrichment_lookup, forbidden_pm_lookup, assignment):
    """S2: e-family enrichment of VESSEL-domain PREFIX.

    Uses multiple ok-enriched MIDDLEs: e, aiin, ar, al, eey.
    """
    vessel_family_key = [k for k, v in assignment.items() if v == 'VESSEL'][0]
    vessel_prefixes = PREFIX_FAMILIES[vessel_family_key]
    target_middles = ['e', 'aiin', 'ar', 'al', 'eey']
    ratios = []
    for mid in target_middles:
        r = get_enrichment(enrichment_lookup, forbidden_pm_lookup, vessel_prefixes, mid)
        ratios.append(r)
    return np.mean(ratios)


def compute_s3(source_prefixes, assignment):
    """S3: Forbidden pair source PREFIX fraction for ENERGY domain.

    Among the 17 forbidden pair source entities, what fraction has the
    assigned-ENERGY PREFIX family? Lower is better (ENERGY avoids hazards).
    """
    energy_family_key = [k for k, v in assignment.items() if v == 'ENERGY'][0]
    energy_prefixes = set(PREFIX_FAMILIES[energy_family_key])

    total = len(source_prefixes)
    energy_count = sum(1 for pfx in source_prefixes if pfx in energy_prefixes)
    return energy_count / max(total, 1)


def compute_s4(buffer_prefix_counts, assignment):
    """S4: Safety buffer PREFIX fraction for ENERGY domain.

    Higher is better.
    """
    energy_family_key = [k for k, v in assignment.items() if v == 'ENERGY'][0]
    energy_prefixes = set(PREFIX_FAMILIES[energy_family_key])

    total = sum(buffer_prefix_counts.values())
    energy_count = sum(buffer_prefix_counts.get(pfx, 0) for pfx in energy_prefixes)
    return energy_count / max(total, 1)


def compute_s5(source_prefixes, assignment):
    """S5: Binary — does ENERGY PREFIX have ZERO forbidden pair source events?

    Check entity-level: among the 17 forbidden pairs, does ANY source entity
    have a PREFIX in the assigned-ENERGY family?
    """
    energy_family_key = [k for k, v in assignment.items() if v == 'ENERGY'][0]
    energy_prefixes = set(PREFIX_FAMILIES[energy_family_key])

    for pfx in source_prefixes:
        if pfx in energy_prefixes:
            return False  # Found a source event with ENERGY PREFIX

    return True  # Zero source events


def rank_scores(scores, higher_is_better=True):
    """Assign ranks 1-N to scores. Rank 1 = best."""
    indexed = sorted(enumerate(scores), key=lambda x: x[1],
                     reverse=higher_is_better)
    ranks = [0] * len(scores)
    for rank_pos, (idx, _) in enumerate(indexed):
        ranks[idx] = rank_pos + 1
    return ranks


def run_t1(data):
    print("\n" + "=" * 60)
    print("T1: PREFIX-Domain Assignment Uniqueness")
    print("=" * 60)

    family_keys = list(PREFIX_FAMILIES.keys())  # ['qo', 'ok', 'chsh']

    # Pre-compute: extract PREFIX of each forbidden pair SOURCE entity
    morph = data['morph']
    source_prefixes = []
    for src_entity, _, _, _ in data['forbidden_middle_pairs']:
        m = morph.extract(src_entity)
        pfx = m.prefix if m and m.prefix else '(none)'
        source_prefixes.append(pfx)

    print(f"  Forbidden pair source PREFIXes: {Counter(source_prefixes)}")

    results = []
    for perm in itertools.permutations(DOMAIN_LABELS):
        assignment = dict(zip(family_keys, perm))

        s1 = compute_s1(data['enrichment_lookup'], data['forbidden_pm_lookup'], assignment)
        s2 = compute_s2(data['enrichment_lookup'], data['forbidden_pm_lookup'], assignment)
        s3 = compute_s3(source_prefixes, assignment)
        s4 = compute_s4(data['buffer_prefix_counts'], assignment)
        s5 = compute_s5(source_prefixes, assignment)

        results.append({
            'assignment': dict(assignment),
            'S1': s1, 'S2': s2, 'S3': s3, 'S4': s4, 'S5': s5,
        })

    # Rank each score across the 6 assignments
    s1_scores = [r['S1'] for r in results]
    s2_scores = [r['S2'] for r in results]
    s3_scores = [r['S3'] for r in results]
    s4_scores = [r['S4'] for r in results]
    s5_scores = [1.0 if r['S5'] else 0.0 for r in results]

    s1_ranks = rank_scores(s1_scores, higher_is_better=True)
    s2_ranks = rank_scores(s2_scores, higher_is_better=True)
    s3_ranks = rank_scores(s3_scores, higher_is_better=False)  # Lower = better
    s4_ranks = rank_scores(s4_scores, higher_is_better=True)
    s5_ranks = rank_scores(s5_scores, higher_is_better=True)

    for i, r in enumerate(results):
        r['S1_rank'] = s1_ranks[i]
        r['S2_rank'] = s2_ranks[i]
        r['S3_rank'] = s3_ranks[i]
        r['S4_rank'] = s4_ranks[i]
        r['S5_rank'] = s5_ranks[i]
        r['composite'] = s1_ranks[i] + s2_ranks[i] + s3_ranks[i] + s4_ranks[i] + s5_ranks[i]

    # Sort by composite (lower = better)
    results.sort(key=lambda x: x['composite'])

    # Report
    print("\nAssignment rankings (lower composite = better):")
    for i, r in enumerate(results):
        a = r['assignment']
        print(f"  #{i+1}: qo={a['qo']:<8} ok={a['ok']:<8} chsh={a['chsh']:<8} | "
              f"S1={r['S1']:.3f}(r{r['S1_rank']}) S2={r['S2']:.3f}(r{r['S2_rank']}) "
              f"S3={r['S3']:.4f}(r{r['S3_rank']}) S4={r['S4']:.3f}(r{r['S4_rank']}) "
              f"S5={r['S5']}(r{r['S5_rank']}) | composite={r['composite']}")

    best = results[0]
    second = results[1]
    gap = second['composite'] - best['composite']
    is_unique = gap > 0

    # Check if current assignment is the winner
    current_is_winner = (
        best['assignment']['qo'] == 'ENERGY' and
        best['assignment']['ok'] == 'VESSEL' and
        best['assignment']['chsh'] == 'PROCESS'
    )

    # S5 check: current assignment must have S5=True
    s5_true_count = sum(1 for r in results if r['S5'])
    current_has_s5 = best['S5'] if current_is_winner else False

    # Pass: unique winner, gap >= 2, current has zero hazard sources, current is winner
    passed = is_unique and gap >= 2 and current_has_s5 and current_is_winner

    print(f"\nCurrent assignment (qo=ENERGY, ok=VESSEL, chsh=PROCESS) is winner: {current_is_winner}")
    print(f"Unique maximum: {is_unique} (gap={gap})")
    print(f"S5 current has zero hazard: {current_has_s5} ({s5_true_count} total with zero)")
    print(f"T1 PASS: {passed}")

    # Format for JSON output
    assignments_out = []
    for r in results:
        assignments_out.append({
            'qo': r['assignment']['qo'],
            'ok': r['assignment']['ok'],
            'chsh': r['assignment']['chsh'],
            'S1_value': round(r['S1'], 4),
            'S1_rank': r['S1_rank'],
            'S2_value': round(r['S2'], 4),
            'S2_rank': r['S2_rank'],
            'S3_value': round(r['S3'], 6),
            'S3_rank': r['S3_rank'],
            'S4_value': round(r['S4'], 4),
            'S4_rank': r['S4_rank'],
            'S5_value': r['S5'],
            'S5_rank': r['S5_rank'],
            'composite': r['composite'],
        })

    return {
        'pass': passed,
        'assignments': assignments_out,
        'current_assignment_is_winner': current_is_winner,
        'gap_to_next': gap,
        's5_current_zero_hazard': current_has_s5,
        's5_true_count': s5_true_count,
        'source_prefix_distribution': dict(Counter(source_prefixes)),
        'threshold': 'unique maximum, gap >= 2, current has S5, current assignment wins',
    }


# ── T2/T3: Mantel Test ──────────────────────────────────────────

def build_feature_matrix(data, feature_list):
    """Build feature matrix for eligible MIDDLEs.

    Eligible = in top-49 AND glossed AND in affordance table.
    Returns: (matrix, middle_names, categories)
    """
    eligible = []
    for mid in data['top49']:
        if mid not in data['glossed_middles']:
            continue
        if mid not in data['affordance_middles']:
            continue
        cat = data['middle_to_cat'].get(mid, 'OTHER')
        if cat == 'UNGLOSSED':
            continue

        entry = data['affordance_middles'][mid]
        sig = entry.get('behavioral_signature', {})

        # Build feature vector
        vec = []
        for feat in feature_list:
            if feat in ('radial_depth', 'compat_degree', 'token_frequency'):
                val = entry.get(feat, 0.0)
            else:
                val = sig.get(feat, 0.0)
            vec.append(float(val))

        eligible.append({
            'middle': mid,
            'category': cat,
            'features': vec,
        })

    if not eligible:
        return None, [], []

    matrix = np.array([e['features'] for e in eligible])
    names = [e['middle'] for e in eligible]
    cats = [e['category'] for e in eligible]

    return matrix, names, cats


def zscore_normalize(matrix):
    """Z-score normalize each column. If std=0, set to 0."""
    means = matrix.mean(axis=0)
    stds = matrix.std(axis=0)
    stds[stds == 0] = 1.0  # Avoid division by zero
    return (matrix - means) / stds


def mantel_test(features, categories, n_perm=10000):
    """Run Mantel test: correlation between behavioral and gloss distances.

    Returns: (r, p_value, n_eligible)
    """
    N = features.shape[0]
    if N < 5:
        return 0.0, 1.0, N

    # Z-score normalize
    features_z = zscore_normalize(features)

    # Behavioral distance (condensed form)
    d_behav = pdist(features_z, 'euclidean')

    # Gloss distance (condensed form): 0=same category, 1=different
    d_gloss = np.zeros(N * (N - 1) // 2)
    idx = 0
    for i in range(N):
        for j in range(i + 1, N):
            d_gloss[idx] = 0.0 if categories[i] == categories[j] else 1.0
            idx += 1

    # Observed Mantel r
    r_obs, _ = pearsonr(d_behav, d_gloss)

    # Permutation test
    n_geq = 0
    indices = np.arange(N)
    for _ in range(n_perm):
        perm = np.random.permutation(N)
        perm_cats = [categories[p] for p in perm]

        d_gloss_perm = np.zeros(N * (N - 1) // 2)
        idx = 0
        for i in range(N):
            for j in range(i + 1, N):
                d_gloss_perm[idx] = 0.0 if perm_cats[i] == perm_cats[j] else 1.0
                idx += 1

        r_perm, _ = pearsonr(d_behav, d_gloss_perm)
        if r_perm >= r_obs:
            n_geq += 1

    p_value = n_geq / n_perm
    return float(r_obs), float(p_value), N


def run_t2(data):
    print("\n" + "=" * 60)
    print("T2: Mantel Test (Full 17-Feature Set)")
    print("=" * 60)

    matrix, names, cats = build_feature_matrix(data, FULL_FEATURES)
    if matrix is None or len(names) < 5:
        print("  INSUFFICIENT DATA")
        return {'pass': False, 'mantel_r': 0.0, 'p_value': 1.0,
                'n_eligible': 0, 'n_features': 17, 'n_permutations': 10000,
                'threshold': 'r > 0, p < 0.05'}

    print(f"  Eligible MIDDLEs: {len(names)}")
    print(f"  Categories: {Counter(cats)}")
    print(f"  MIDDLEs: {names}")

    r, p, n = mantel_test(matrix, cats, n_perm=10000)

    passed = r > 0 and p < 0.05
    print(f"  Mantel r = {r:.4f}, p = {p:.4f}")
    print(f"  T2 PASS: {passed}")

    return {
        'pass': passed,
        'mantel_r': round(r, 6),
        'p_value': round(p, 4),
        'n_eligible': n,
        'n_features': 17,
        'n_permutations': 10000,
        'eligible_middles': names,
        'category_distribution': dict(Counter(cats)),
        'threshold': 'r > 0, p < 0.05',
    }


def run_t3(data):
    print("\n" + "=" * 60)
    print("T3: Non-Circular Mantel (13-Feature Ablated Set)")
    print("=" * 60)

    matrix, names, cats = build_feature_matrix(data, REDUCED_FEATURES)
    if matrix is None or len(names) < 5:
        print("  INSUFFICIENT DATA")
        return {'pass': False, 'mantel_r': 0.0, 'p_value': 1.0,
                'n_eligible': 0, 'n_features': 13, 'n_permutations': 10000,
                'ablated_features': ABLATED_FEATURES,
                'threshold': 'r > 0, p < 0.05'}

    print(f"  Eligible MIDDLEs: {len(names)}")
    print(f"  Ablated features: {ABLATED_FEATURES}")

    r, p, n = mantel_test(matrix, cats, n_perm=10000)

    passed = r > 0 and p < 0.05
    print(f"  Mantel r = {r:.4f}, p = {p:.4f}")
    print(f"  T3 PASS: {passed}")

    return {
        'pass': passed,
        'mantel_r': round(r, 6),
        'p_value': round(p, 4),
        'n_eligible': n,
        'n_features': 13,
        'n_permutations': 10000,
        'ablated_features': ABLATED_FEATURES,
        'threshold': 'r > 0, p < 0.05',
    }


# ── T4: Per-Category Mantel Decomposition ────────────────────────

def run_t4(data):
    print("\n" + "=" * 60)
    print("T4: Per-Category Discriminability Decomposition")
    print("=" * 60)

    matrix, names, cats = build_feature_matrix(data, FULL_FEATURES)
    if matrix is None or len(names) < 5:
        print("  INSUFFICIENT DATA")
        return {'per_category': {}, 'n_permutations': 1000}

    features_z = zscore_normalize(matrix)
    D = squareform(pdist(features_z, 'euclidean'))
    N = len(names)

    cat_counts = Counter(cats)
    testable_cats = [c for c, n in cat_counts.items() if n >= 3 and c != 'OTHER']

    print(f"  Testable categories (>= 3 members): {testable_cats}")

    per_category = {}
    n_perm = 1000

    for cat in testable_cats:
        members = [i for i, c in enumerate(cats) if c == cat]
        non_members = [i for i, c in enumerate(cats) if c != cat]

        # Within-category mean distance
        within_dists = []
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                within_dists.append(D[members[i], members[j]])
        mean_within = np.mean(within_dists) if within_dists else 0.0

        # Between-category mean distance
        between_dists = []
        for m in members:
            for nm in non_members:
                between_dists.append(D[m, nm])
        mean_between = np.mean(between_dists) if between_dists else 0.0

        # Discriminability
        if mean_between > 0:
            disc = (mean_between - mean_within) / mean_between
        else:
            disc = 0.0

        # Permutation test
        n_geq = 0
        n_members = len(members)
        all_indices = list(range(N))
        for _ in range(n_perm):
            perm_members = list(np.random.choice(all_indices, size=n_members, replace=False))
            perm_non = [i for i in all_indices if i not in set(perm_members)]

            perm_within = []
            for i in range(len(perm_members)):
                for j in range(i + 1, len(perm_members)):
                    perm_within.append(D[perm_members[i], perm_members[j]])
            perm_mean_within = np.mean(perm_within) if perm_within else 0.0

            perm_between = []
            for m in perm_members:
                for nm in perm_non:
                    perm_between.append(D[m, nm])
            perm_mean_between = np.mean(perm_between) if perm_between else 0.0

            if perm_mean_between > 0:
                perm_disc = (perm_mean_between - perm_mean_within) / perm_mean_between
            else:
                perm_disc = 0.0

            if perm_disc >= disc:
                n_geq += 1

        p_value = n_geq / n_perm

        print(f"  {cat}: n={len(members)}, disc={disc:.4f}, p={p_value:.4f}")

        per_category[cat] = {
            'n_members': len(members),
            'mean_within_dist': round(float(mean_within), 4),
            'mean_between_dist': round(float(mean_between), 4),
            'discriminability': round(float(disc), 4),
            'p_value': round(float(p_value), 4),
        }

    return {
        'per_category': per_category,
        'n_permutations': n_perm,
    }


# ── Verdict ──────────────────────────────────────────────────────

def synthesize_verdict(t1, t2, t3):
    t1_pass = t1['pass']
    t2_pass = t2['pass']
    t3_pass = t3['pass']

    if t1_pass and t2_pass and t3_pass:
        verdict = 'GLOSS_ADVERSARIAL_VALIDATED'
    elif t1_pass and t2_pass and not t3_pass:
        verdict = 'DOMAIN_VALIDATED_MANTEL_CIRCULAR'
    elif t1_pass and not t2_pass:
        verdict = 'DOMAIN_ONLY'
    elif not t1_pass and t2_pass and t3_pass:
        verdict = 'MANTEL_ONLY'
    else:
        verdict = 'GLOSS_EXHAUSTED'

    return {
        'verdict': verdict,
        't1_pass': t1_pass,
        't2_pass': t2_pass,
        't3_pass': t3_pass,
    }


# ── Main ─────────────────────────────────────────────────────────

def main():
    data = load_data()

    t1 = run_t1(data)
    t2 = run_t2(data)
    t3 = run_t3(data)
    t4 = run_t4(data)

    synthesis = synthesize_verdict(t1, t2, t3)

    print("\n" + "=" * 60)
    print(f"VERDICT: {synthesis['verdict']}")
    print(f"  T1 (PREFIX-domain uniqueness): {'PASS' if t1['pass'] else 'FAIL'}")
    print(f"  T2 (Mantel full): {'PASS' if t2['pass'] else 'FAIL'}")
    print(f"  T3 (Mantel ablated): {'PASS' if t3['pass'] else 'FAIL'}")
    print("=" * 60)

    results = {
        'phase': 337,
        'title': 'GLOSS_ADVERSARIAL_VALIDATION',
        'tests': {
            't1_prefix_domain_uniqueness': t1,
            't2_mantel_full': t2,
            't3_mantel_ablated': t3,
            't4_category_decomposition': t4,
        },
        'synthesis': synthesis,
        'metadata': {
            'n_glossed_middles': len(data['glossed_middles']),
            'n_top49': len(data['top49']),
            'n_top49_eligible_full': t2.get('n_eligible', 0),
            'n_top49_eligible_ablated': t3.get('n_eligible', 0),
            'prefix_families': {k: v for k, v in PREFIX_FAMILIES.items()},
            'n_buffer_tokens': data['buffer_total'],
            'buffer_prefix_distribution': dict(data['buffer_prefix_counts']),
            'n_forbidden_pairs': len(data['forbidden_middle_pairs']),
            'feature_list_full': FULL_FEATURES,
            'feature_list_ablated': REDUCED_FEATURES,
        },
    }

    out_path = PROJECT / 'phases' / 'GLOSS_ADVERSARIAL_VALIDATION' / 'results' / 'gloss_adversarial_validation.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
