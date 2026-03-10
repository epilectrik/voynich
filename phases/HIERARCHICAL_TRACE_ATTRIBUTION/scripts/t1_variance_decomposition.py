"""
Phase 561 T1: Hierarchical Variance Partition

Nested dispersion attribution for 9 token-level features across 5 hierarchy levels:
    section > folio > paragraph > line > token (residual)

Method: ANOVA-style sequential SS decomposition (descriptive, not formal ICC).
Features include binary/ordinal/integer types. Results are "variance share" (VS),
the fraction of total variance explained at each nesting level.

4 null models (200 permutations each):
    1. Section-shuffle: permute section labels across folios
    2. Folio-shuffle-within-section: permute folio labels within sections
    3. Paragraph-shuffle-within-folio: permute paragraph labels within folios
    4. Line-shuffle-within-paragraph: permute line labels within paragraphs

Success criteria:
    T1-A: VS_section > 0.03 for >= 5/9 features
    T1-B: VS_folio|section > 0.01 for >= 4/9 features
    T1-C: VS_para|folio > 0.01 for >= 3/9 features
    T1-D: Feature-family hierarchy matches expectations
    T1-E: Line-shuffle null destroys VS_line for hazard/closure features (>50% drop)
"""

import json
import numpy as np
from collections import defaultdict
import os
import sys
import time

# Paths
CORPUS_PATH = os.path.join(os.path.dirname(__file__), '..', '..',
    'WITHIN_DOMAIN_COMPOSITIONAL_CONTROL', 'results', 't1_domain_decomposition.json')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'results', 't1_variance_decomposition.json')

N_PERMS = 200
RNG_SEED = 42


def load_corpus():
    with open(CORPUS_PATH) as f:
        data = json.load(f)
    return data['corpus_tokens']


def build_group_indices(tokens):
    """Build integer group index arrays for each hierarchy level.

    Returns:
        section_ids, folio_ids, para_ids, line_ids: int arrays
        section_labels, folio_labels, para_labels, line_labels: label lists
        folio_to_section: mapping from folio_id to section_id
        para_to_folio: mapping from para_id to folio_id
        line_to_para: mapping from line_id to para_id
    """
    section_map = {}
    folio_map = {}
    para_map = {}
    line_map = {}

    section_ids = np.zeros(len(tokens), dtype=np.int32)
    folio_ids = np.zeros(len(tokens), dtype=np.int32)
    para_ids = np.zeros(len(tokens), dtype=np.int32)
    line_ids = np.zeros(len(tokens), dtype=np.int32)

    for i, t in enumerate(tokens):
        sec = t['section']
        fol = t['folio']
        par = (fol, t['paragraph_idx'])
        lin = (fol, t['paragraph_idx'], t['line'])

        if sec not in section_map:
            section_map[sec] = len(section_map)
        if fol not in folio_map:
            folio_map[fol] = len(folio_map)
        if par not in para_map:
            para_map[par] = len(para_map)
        if lin not in line_map:
            line_map[lin] = len(line_map)

        section_ids[i] = section_map[sec]
        folio_ids[i] = folio_map[fol]
        para_ids[i] = para_map[par]
        line_ids[i] = line_map[lin]

    # Build nesting maps
    folio_to_section = np.zeros(len(folio_map), dtype=np.int32)
    for fol, fid in folio_map.items():
        # Find any token with this folio to get section
        for t in tokens:
            if t['folio'] == fol:
                folio_to_section[fid] = section_map[t['section']]
                break

    para_to_folio = np.zeros(len(para_map), dtype=np.int32)
    for (fol, pidx), pid in para_map.items():
        para_to_folio[pid] = folio_map[fol]

    line_to_para = np.zeros(len(line_map), dtype=np.int32)
    for (fol, pidx, ln), lid in line_map.items():
        line_to_para[lid] = para_map[(fol, pidx)]

    return (section_ids, folio_ids, para_ids, line_ids,
            list(section_map.keys()), list(folio_map.keys()),
            folio_to_section, para_to_folio, line_to_para)


def derive_features(tokens):
    """Derive 9 analysis features from corpus tokens.

    Returns dict of feature_name -> np.array (float64, NaN for missing).
    """
    n = len(tokens)

    # C1563 routing enrichment map
    ROUTING_MAP = {'r': 'ACTIVE', 'y': 'THERMAL', 'h': 'FLOW', 'm': 'ARRANGEMENT'}

    features = {}

    # Domain membership (binary)
    features['head_k'] = np.array([1.0 if t['domain'] == 'THERMAL' else 0.0 for t in tokens])
    features['head_e'] = np.array([1.0 if t['domain'] == 'STABILITY' else 0.0 for t in tokens])
    features['head_a'] = np.array([1.0 if t['domain'] == 'ACTIVE' else 0.0 for t in tokens])
    features['is_headless'] = np.array([1.0 if t['domain'] == 'HEADLESS' else 0.0 for t in tokens])

    # Hazard ordinal: ZERO=0, LOW=1, HIGH=2, IMMUNE=NaN (outside hazard framework)
    hazard_map = {'ZERO': 0.0, 'LOW': 1.0, 'HIGH': 2.0}
    features['hazard_ord'] = np.array([hazard_map.get(t.get('frame_hazard'), np.nan) for t in tokens])

    # Opacity ordinal: TRANSPARENT=0, SEMI_TRANSPARENT=1, OPAQUE=2, None=NaN
    opacity_map = {'TRANSPARENT': 0.0, 'SEMI_TRANSPARENT': 1.0, 'OPAQUE': 2.0}
    features['opacity_ord'] = np.array([opacity_map.get(t.get('terminal_opacity'), np.nan) for t in tokens])

    # Compound depth (integer)
    features['compound_depth'] = np.array([float(t.get('compound_depth', 0)) for t in tokens])

    # Safe pathway (binary)
    features['is_safe_pathway'] = np.array([1.0 if t.get('is_safe_pathway') else 0.0 for t in tokens])

    # Routing match (binary) - C1563 enrichments
    routing = np.zeros(n)
    for i, t in enumerate(tokens):
        prev_term = t.get('prev_term_same_line')
        if prev_term and prev_term in ROUTING_MAP:
            if t['domain'] == ROUTING_MAP[prev_term]:
                routing[i] = 1.0
    features['routing_match'] = routing

    return features


def compute_group_means_expanded(x, group_ids, max_id=None):
    """Return per-token group mean array."""
    if max_id is None:
        max_id = group_ids.max() + 1
    counts = np.bincount(group_ids, minlength=max_id)
    sums = np.bincount(group_ids, weights=x, minlength=max_id)
    means = np.divide(sums, counts, out=np.zeros_like(sums, dtype=float), where=counts > 0)
    return means[group_ids]


def hierarchical_variance_decomposition(x, s_ids, f_ids, p_ids, l_ids):
    """Compute nested variance partition for feature x.

    Returns dict with variance shares (VS) for each level.
    NaN values in x are excluded.
    """
    valid = ~np.isnan(x)
    if valid.sum() < 10:
        return {'section': 0, 'folio': 0, 'paragraph': 0, 'line': 0,
                'residual': 0, 'valid_n': int(valid.sum()), 'ss_total': 0}

    xv = x[valid]
    sv = s_ids[valid]
    fv = f_ids[valid]
    pv = p_ids[valid]
    lv = l_ids[valid]

    grand_mean = np.mean(xv)
    ss_total = np.sum((xv - grand_mean)**2)

    if ss_total < 1e-15:
        return {'section': 0, 'folio': 0, 'paragraph': 0, 'line': 0,
                'residual': 0, 'valid_n': int(valid.sum()), 'ss_total': 0}

    # Per-token group means at each level
    s_means = compute_group_means_expanded(xv, sv)
    f_means = compute_group_means_expanded(xv, fv)
    p_means = compute_group_means_expanded(xv, pv)
    l_means = compute_group_means_expanded(xv, lv)

    # Nested SS decomposition
    ss_section = np.sum((s_means - grand_mean)**2)
    ss_folio = np.sum((f_means - s_means)**2)
    ss_para = np.sum((p_means - f_means)**2)
    ss_line = np.sum((l_means - p_means)**2)
    ss_residual = np.sum((xv - l_means)**2)

    return {
        'section': float(ss_section / ss_total),
        'folio': float(ss_folio / ss_total),
        'paragraph': float(ss_para / ss_total),
        'line': float(ss_line / ss_total),
        'residual': float(ss_residual / ss_total),
        'valid_n': int(valid.sum()),
        'ss_total': float(ss_total)
    }


def run_null_section_shuffle(features, s_ids, f_ids, p_ids, l_ids,
                             folio_to_section, rng, n_perms):
    """Null model 1: permute section labels across folios."""
    n_folios = len(folio_to_section)
    results = {fname: [] for fname in features}

    for _ in range(n_perms):
        # Shuffle section assignments of folios
        shuffled_f2s = folio_to_section.copy()
        rng.shuffle(shuffled_f2s)
        # Expand to per-token section IDs
        s_ids_null = shuffled_f2s[f_ids]

        for fname, x in features.items():
            vs = hierarchical_variance_decomposition(x, s_ids_null, f_ids, p_ids, l_ids)
            results[fname].append(vs)

    return results


def run_null_folio_shuffle(features, s_ids, f_ids, p_ids, l_ids,
                           folio_to_section, para_to_folio, rng, n_perms):
    """Null model 2: shuffle paragraph->folio assignments within sections.

    Randomly reassigns paragraphs to different folios within the same section,
    preserving how many paragraphs go to each folio. This changes which paragraphs
    are grouped into which folio, testing whether folio-level grouping is meaningful.
    """
    # Group paragraphs by section, with their folio assignments
    n_paras = len(para_to_folio)
    section_paras = defaultdict(list)
    for pid in range(n_paras):
        fid = para_to_folio[pid]
        sid = folio_to_section[fid]
        section_paras[int(sid)].append(pid)

    # Pre-compute folio assignments per section
    section_folio_assigns = {}
    for sid, pids in section_paras.items():
        section_folio_assigns[sid] = np.array([para_to_folio[pid] for pid in pids])

    results = {fname: [] for fname in features}

    for _ in range(n_perms):
        # Shuffle paragraph->folio assignments within each section
        new_p2f = para_to_folio.copy()
        for sid, pids in section_paras.items():
            folio_assigns = section_folio_assigns[sid].copy()
            rng.shuffle(folio_assigns)
            for pid, new_fid in zip(pids, folio_assigns):
                new_p2f[pid] = new_fid

        # Update per-token folio IDs: token i's folio = new_p2f[p_ids[i]]
        f_ids_null = new_p2f[p_ids]

        for fname, x in features.items():
            vs = hierarchical_variance_decomposition(x, s_ids, f_ids_null, p_ids, l_ids)
            results[fname].append(vs)

    return results


def run_null_para_shuffle(features, s_ids, f_ids, p_ids, l_ids,
                          line_to_para, para_to_folio, rng, n_perms):
    """Null model 3: shuffle line->paragraph assignments within folios.

    Randomly reassigns lines to different paragraphs within the same folio,
    preserving how many lines go to each paragraph. This changes which lines
    are grouped into which paragraph, testing whether paragraph structure is meaningful.
    """
    # Group lines by folio
    n_lines = len(line_to_para)
    folio_lines = defaultdict(list)
    for lid in range(n_lines):
        fid = para_to_folio[line_to_para[lid]]
        folio_lines[int(fid)].append(lid)

    # Pre-compute paragraph assignments per folio
    folio_para_assigns = {}
    for fid, lids in folio_lines.items():
        folio_para_assigns[fid] = np.array([line_to_para[lid] for lid in lids])

    results = {fname: [] for fname in features}

    for _ in range(n_perms):
        # Shuffle line->paragraph assignments within each folio
        new_l2p = line_to_para.copy()
        for fid, lids in folio_lines.items():
            para_assigns = folio_para_assigns[fid].copy()
            rng.shuffle(para_assigns)
            for lid, new_pid in zip(lids, para_assigns):
                new_l2p[lid] = new_pid

        # Update per-token paragraph IDs: token i's paragraph = new_l2p[l_ids[i]]
        p_ids_null = new_l2p[l_ids]

        for fname, x in features.items():
            vs = hierarchical_variance_decomposition(x, s_ids, f_ids, p_ids_null, l_ids)
            results[fname].append(vs)

    return results


def run_null_line_shuffle(features, s_ids, f_ids, p_ids, l_ids,
                          line_to_para, para_to_folio, rng, n_perms):
    """Null model 4: permute line labels within paragraphs.

    Within each paragraph, randomly reassign tokens' line labels.
    Preserves paragraph/folio/section membership but destroys line packeting.
    """
    # Group token indices by paragraph
    para_token_groups = defaultdict(list)
    for i, pid in enumerate(p_ids):
        para_token_groups[int(pid)].append(i)

    results = {fname: [] for fname in features}

    for _ in range(n_perms):
        l_ids_null = l_ids.copy()
        for pid, token_indices in para_token_groups.items():
            idx = np.array(token_indices)
            line_vals = l_ids[idx].copy()
            rng.shuffle(line_vals)
            l_ids_null[idx] = line_vals

        for fname, x in features.items():
            vs = hierarchical_variance_decomposition(x, s_ids, f_ids, p_ids, l_ids_null)
            results[fname].append(vs)

    return results


def summarize_null(null_results):
    """Compute mean and std of each VS component across permutations."""
    summary = {}
    for fname, perm_results in null_results.items():
        levels = ['section', 'folio', 'paragraph', 'line', 'residual']
        summary[fname] = {}
        for level in levels:
            vals = [r[level] for r in perm_results]
            summary[fname][level] = {
                'mean': float(np.mean(vals)),
                'std': float(np.std(vals)),
                'p05': float(np.percentile(vals, 5)),
                'p95': float(np.percentile(vals, 95))
            }
    return summary


def evaluate_criteria(real_results, null_summaries, features):
    """Evaluate success criteria T1-A through T1-E."""
    feature_names = list(features.keys())

    # T1-A: VS_section > 0.03 for >= 5/9 features
    t1a_pass_count = sum(1 for f in feature_names if real_results[f]['section'] > 0.03)
    t1a = {'pass': t1a_pass_count >= 5, 'count': t1a_pass_count, 'threshold': 5,
           'details': {f: round(real_results[f]['section'], 4) for f in feature_names}}

    # T1-B: VS_folio|section > 0.01 for >= 4/9 features
    t1b_pass_count = sum(1 for f in feature_names if real_results[f]['folio'] > 0.01)
    t1b = {'pass': t1b_pass_count >= 4, 'count': t1b_pass_count, 'threshold': 4,
           'details': {f: round(real_results[f]['folio'], 4) for f in feature_names}}

    # T1-C: VS_para|folio > 0.01 for >= 3/9 features
    t1c_pass_count = sum(1 for f in feature_names if real_results[f]['paragraph'] > 0.01)
    t1c = {'pass': t1c_pass_count >= 3, 'count': t1c_pass_count, 'threshold': 3,
           'details': {f: round(real_results[f]['paragraph'], 4) for f in feature_names}}

    # T1-D: Feature-family hierarchy check
    domain_features = ['head_k', 'head_e', 'head_a', 'is_headless']
    hazard_features = ['hazard_ord', 'opacity_ord', 'is_safe_pathway']
    routing_features = ['routing_match']

    # Domain features: section+folio should be top contributors
    domain_check = []
    for f in domain_features:
        r = real_results[f]
        top_two = r['section'] + r['folio']
        domain_check.append(top_two > r['paragraph'] + r['line'])

    # Hazard features: line+paragraph should be major contributors (with possible section residue)
    hazard_check = []
    for f in hazard_features:
        r = real_results[f]
        line_para = r['line'] + r['paragraph']
        hazard_check.append(line_para > 0.01)  # meaningful contribution

    # Routing: line should be major contributor
    routing_check = []
    for f in routing_features:
        r = real_results[f]
        routing_check.append(r['line'] > r['section'] or r['line'] > r['folio'])

    # No level null across all features
    levels = ['section', 'folio', 'paragraph', 'line']
    level_null_check = {}
    for level in levels:
        max_vs = max(real_results[f][level] for f in feature_names)
        level_null_check[level] = max_vs > 0.005

    t1d = {
        'domain_family': {'pass': sum(domain_check) >= 3, 'details': dict(zip(domain_features, domain_check))},
        'hazard_family': {'pass': sum(hazard_check) >= 2, 'details': dict(zip(hazard_features, hazard_check))},
        'routing_family': {'pass': all(routing_check), 'details': dict(zip(routing_features, routing_check))},
        'no_null_level': {'pass': all(level_null_check.values()), 'details': level_null_check},
        'pass': (sum(domain_check) >= 3 and sum(hazard_check) >= 2 and
                 all(routing_check) and all(level_null_check.values()))
    }

    # T1-E: Line-shuffle null destroys VS_line for hazard/closure features
    line_null = null_summaries['line_shuffle']
    t1e_checks = {}
    for f in hazard_features + routing_features:
        real_vs_line = real_results[f]['line']
        null_vs_line = line_null[f]['line']['mean']
        if real_vs_line > 0.001:
            drop = 1.0 - (null_vs_line / real_vs_line)
            t1e_checks[f] = {'real': round(real_vs_line, 4),
                             'null_mean': round(null_vs_line, 4),
                             'drop_pct': round(drop * 100, 1),
                             'pass': drop > 0.5}
        else:
            t1e_checks[f] = {'real': round(real_vs_line, 4),
                             'null_mean': round(null_vs_line, 4),
                             'drop_pct': 0, 'pass': False}

    t1e_pass_count = sum(1 for v in t1e_checks.values() if v['pass'])
    t1e = {'pass': t1e_pass_count >= 2, 'count': t1e_pass_count,
           'threshold': 2, 'details': t1e_checks}

    return {'T1-A': t1a, 'T1-B': t1b, 'T1-C': t1c, 'T1-D': t1d, 'T1-E': t1e}


def main():
    t_start = time.time()
    print("Phase 561 T1: Hierarchical Variance Partition")
    print("=" * 60)

    # Load corpus
    print("Loading corpus...")
    tokens = load_corpus()
    print(f"  {len(tokens)} tokens loaded")

    # Build group indices
    print("Building group indices...")
    (s_ids, f_ids, p_ids, l_ids,
     section_labels, folio_labels,
     folio_to_section, para_to_folio, line_to_para) = build_group_indices(tokens)

    n_sections = len(section_labels)
    n_folios = len(folio_labels)
    n_paras = len(set(p_ids))
    n_lines = len(set(l_ids))
    print(f"  {n_sections} sections, {n_folios} folios, {n_paras} paragraphs, {n_lines} lines")

    # Derive features
    print("Deriving features...")
    features = derive_features(tokens)
    for fname, x in features.items():
        valid = ~np.isnan(x)
        print(f"  {fname}: {valid.sum()}/{len(x)} valid, mean={np.nanmean(x):.4f}")

    # Real variance decomposition
    print("\nComputing real variance decomposition...")
    real_results = {}
    for fname, x in features.items():
        vs = hierarchical_variance_decomposition(x, s_ids, f_ids, p_ids, l_ids)
        real_results[fname] = vs
        total = vs['section'] + vs['folio'] + vs['paragraph'] + vs['line'] + vs['residual']
        print(f"  {fname}: S={vs['section']:.4f} F={vs['folio']:.4f} "
              f"P={vs['paragraph']:.4f} L={vs['line']:.4f} R={vs['residual']:.4f} "
              f"(sum={total:.4f}, n={vs['valid_n']})")

    # Null models
    rng = np.random.default_rng(RNG_SEED)
    null_summaries = {}

    print(f"\nRunning null model 1: section-shuffle ({N_PERMS} permutations)...")
    null_section = run_null_section_shuffle(features, s_ids, f_ids, p_ids, l_ids,
                                            folio_to_section, rng, N_PERMS)
    null_summaries['section_shuffle'] = summarize_null(null_section)

    print(f"Running null model 2: folio-shuffle-within-section ({N_PERMS} permutations)...")
    null_folio = run_null_folio_shuffle(features, s_ids, f_ids, p_ids, l_ids,
                                        folio_to_section, para_to_folio, rng, N_PERMS)
    null_summaries['folio_shuffle'] = summarize_null(null_folio)

    print(f"Running null model 3: paragraph-shuffle-within-folio ({N_PERMS} permutations)...")
    null_para = run_null_para_shuffle(features, s_ids, f_ids, p_ids, l_ids,
                                      line_to_para, para_to_folio, rng, N_PERMS)
    null_summaries['para_shuffle'] = summarize_null(null_para)

    print(f"Running null model 4: line-shuffle-within-paragraph ({N_PERMS} permutations)...")
    null_line = run_null_line_shuffle(features, s_ids, f_ids, p_ids, l_ids,
                                      line_to_para, para_to_folio, rng, N_PERMS)
    null_summaries['line_shuffle'] = summarize_null(null_line)

    # Significance: compare real VS to null distribution
    print("\nSignificance (real vs null, z-scores):")
    significance = {}
    null_names = ['section_shuffle', 'folio_shuffle', 'para_shuffle', 'line_shuffle']
    target_levels = ['section', 'folio', 'paragraph', 'line']

    for fname in features:
        significance[fname] = {}
        for null_name, target_level in zip(null_names, target_levels):
            ns = null_summaries[null_name][fname][target_level]
            real_val = real_results[fname][target_level]
            if ns['std'] > 0:
                z = (real_val - ns['mean']) / ns['std']
            else:
                z = float('inf') if real_val > ns['mean'] else 0
            significance[fname][target_level] = {
                'real': round(real_val, 5),
                'null_mean': round(ns['mean'], 5),
                'null_std': round(ns['std'], 5),
                'z_score': round(z, 2),
                'significant': z > 2.0
            }
        print(f"  {fname}: " + ", ".join(
            f"{lev}={significance[fname][lev]['z_score']:.1f}z"
            for lev in target_levels))

    # Evaluate criteria
    print("\n" + "=" * 60)
    print("CRITERIA EVALUATION")
    print("=" * 60)
    criteria = evaluate_criteria(real_results, null_summaries, features)

    for crit_name, crit in criteria.items():
        if isinstance(crit.get('pass'), bool):
            status = "PASS" if crit['pass'] else "FAIL"
            print(f"  {crit_name}: {status}")
            if 'count' in crit:
                print(f"    {crit['count']}/{crit.get('threshold', '?')} features pass")
        elif crit_name == 'T1-D':
            status = "PASS" if crit['pass'] else "FAIL"
            print(f"  {crit_name}: {status}")
            for family, fdata in crit.items():
                if isinstance(fdata, dict) and 'pass' in fdata:
                    print(f"    {family}: {'PASS' if fdata['pass'] else 'FAIL'}")

    # Stacked variance chart data
    chart_data = {}
    for fname in features:
        r = real_results[fname]
        chart_data[fname] = {
            'section': round(r['section'], 4),
            'folio': round(r['folio'], 4),
            'paragraph': round(r['paragraph'], 4),
            'line': round(r['line'], 4),
            'residual': round(r['residual'], 4)
        }

    # Overall pass
    overall_pass = (criteria['T1-A']['pass'] and criteria['T1-B']['pass'] and
                    criteria['T1-C']['pass'] and criteria['T1-D']['pass'] and
                    criteria['T1-E']['pass'])

    elapsed = time.time() - t_start
    print(f"\nOverall T1: {'PASS' if overall_pass else 'FAIL'}")
    print(f"Elapsed: {elapsed:.1f}s")

    # Build output
    output = {
        'metadata': {
            'phase': 'HIERARCHICAL_TRACE_ATTRIBUTION',
            'task': 'T1',
            'name': 'Hierarchical Variance Partition',
            'method': 'ANOVA-style sequential SS decomposition (descriptive)',
            'n_tokens': len(tokens),
            'n_sections': n_sections,
            'n_folios': n_folios,
            'n_paragraphs': n_paras,
            'n_lines': n_lines,
            'n_permutations': N_PERMS,
            'rng_seed': RNG_SEED,
            'elapsed_seconds': round(elapsed, 1),
            'section_labels': section_labels,
        },
        'real_variance_shares': real_results,
        'chart_data': chart_data,
        'null_summaries': null_summaries,
        'significance': significance,
        'criteria': criteria,
        'overall_pass': overall_pass,
        'feature_families': {
            'domain_membership': ['head_k', 'head_e', 'head_a', 'is_headless'],
            'hazard_closure': ['hazard_ord', 'opacity_ord', 'is_safe_pathway'],
            'routing': ['routing_match'],
            'structural': ['compound_depth']
        }
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults written to {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
