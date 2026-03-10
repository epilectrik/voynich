"""
Phase 561 T4: Headless Token Ecology — Hierarchical Attribution

Determines whether headless token subtype distributions are section-specific,
folio-specific, or paragraph-specific.

Method:
    A. Extract 14 headless ecology features per qualifying paragraph (>=5 headless tokens).
    B. Hierarchical variance decomposition: section > folio|section > residual (paragraph).
       Null models (200 perms): section-shuffle, folio-shuffle-within-section.
    C. Paragraph-within-folio headless ecology dispersion (pairwise Euclidean, 300-seed null).
    D. Within-section headless folio discrimination (pairwise Euclidean, 300-seed null).

Success criteria:
    T4-A: VS_section > 0.05 for >= 5/14 features
    T4-B: VS_folio|section > VS_section for >= 3/14 features
    T4-C: >= 30% of qualifying folios show dispersion > null + 2sigma
    T4-D: >= 1/3 sections show distance > null + 2sigma
"""

import json
import numpy as np
from collections import defaultdict
from itertools import combinations
import os
import time

# Paths (relative from __file__)
CORPUS_PATH = os.path.join(os.path.dirname(__file__), '..', '..',
    'WITHIN_DOMAIN_COMPOSITIONAL_CONTROL', 'results', 't1_domain_decomposition.json')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'results', 't4_headless_ecology.json')

N_PERMS_VS = 200
N_PERMS_DISP = 300
RNG_SEED = 42
MIN_HL_PER_PARA = 5
TEST_SECTIONS = ['S', 'H', 'B']

FEATURE_NAMES = [
    'hl_rate', 'pseudo_d_frac', 'pseudo_i_frac', 'pseudo_l_frac',
    'pseudo_cpf_frac', 'sfx_bifurc', 'displaced_kt_rate', 'displaced_nonkt_rate',
    'hl_term_y_frac', 'hl_term_n_frac', 'hl_close_rate', 'hl_spec_rate',
    'hl_headed_adj_rate', 'hl_compound_rate'
]


def load_corpus():
    with open(CORPUS_PATH) as f:
        data = json.load(f)
    return data['corpus_tokens']


def compute_paragraph_features(tokens):
    """Compute 14 headless ecology features per qualifying paragraph.

    A paragraph qualifies if it has >= MIN_HL_PER_PARA headless tokens.

    Returns:
        paragraphs: list of dicts with keys:
            folio, paragraph_idx, section, n_tokens, n_headless, features (14-element list)
    """
    # Group tokens by paragraph
    para_tokens = defaultdict(list)
    for t in tokens:
        key = (t['folio'], t['paragraph_idx'])
        para_tokens[key].append(t)

    paragraphs = []

    for (folio, pidx), toks in para_tokens.items():
        hl_toks = [t for t in toks if t['domain'] == 'HEADLESS']
        n_hl = len(hl_toks)
        n_total = len(toks)

        if n_hl < MIN_HL_PER_PARA:
            continue

        section = toks[0]['section']

        # --- Feature computation ---
        # 1. hl_rate: headless fraction of total paragraph tokens
        hl_rate = n_hl / n_total

        # 2-5. Pseudo-head initial character fractions (from word[0])
        pseudo_d = sum(1 for t in hl_toks if t['word'] and t['word'][0] == 'd')
        pseudo_i = sum(1 for t in hl_toks if t['word'] and t['word'][0] == 'i')
        pseudo_l = sum(1 for t in hl_toks if t['word'] and t['word'][0] == 'l')
        pseudo_cpf = sum(1 for t in hl_toks if t['word'] and t['word'][0] in ('c', 'p', 'f'))

        pseudo_d_frac = pseudo_d / n_hl
        pseudo_i_frac = pseudo_i / n_hl
        pseudo_l_frac = pseudo_l / n_hl
        pseudo_cpf_frac = pseudo_cpf / n_hl

        # 6. sfx_bifurc: headless tokens with non-empty suffix
        sfx_count = sum(1 for t in hl_toks if t.get('suffix') is not None and t['suffix'] != '')
        sfx_bifurc = sfx_count / n_hl

        # 7-8. Displaced head terminal rates
        displaced_kt = sum(1 for t in hl_toks
                           if t.get('has_displaced_head_terminal')
                           and t.get('pseudo_head_atom') in ('k', 't'))
        displaced_nonkt = sum(1 for t in hl_toks
                              if t.get('has_displaced_head_terminal')
                              and t.get('pseudo_head_atom') is not None
                              and t.get('pseudo_head_atom') not in ('k', 't'))

        displaced_kt_rate = displaced_kt / n_hl
        displaced_nonkt_rate = displaced_nonkt / n_hl

        # 9-10. Terminal classification for headless tokens
        hl_term_y = sum(1 for t in hl_toks if t.get('suffix_head') == 'y')
        hl_term_n = sum(1 for t in hl_toks if t.get('suffix_head') == 'n')

        hl_term_y_frac = hl_term_y / n_hl
        hl_term_n_frac = hl_term_n / n_hl

        # 11-12. Zone classification for headless tokens
        hl_close = sum(1 for t in hl_toks if t.get('line_zone') == 'CLOSE')
        hl_spec = sum(1 for t in hl_toks if t.get('line_zone') == 'SPEC')

        hl_close_rate = hl_close / n_hl
        hl_spec_rate = hl_spec / n_hl

        # 13. Headed adjacency: headless tokens preceded by another token on same line
        hl_headed_adj = sum(1 for t in hl_toks if t.get('prev_term_same_line') is not None)
        hl_headed_adj_rate = hl_headed_adj / n_hl

        # 14. Compound rate: headless tokens with compound_depth > 0
        hl_compound = sum(1 for t in hl_toks if (t.get('compound_depth') or 0) > 0)
        hl_compound_rate = hl_compound / n_hl

        features = [
            hl_rate, pseudo_d_frac, pseudo_i_frac, pseudo_l_frac,
            pseudo_cpf_frac, sfx_bifurc, displaced_kt_rate, displaced_nonkt_rate,
            hl_term_y_frac, hl_term_n_frac, hl_close_rate, hl_spec_rate,
            hl_headed_adj_rate, hl_compound_rate
        ]

        paragraphs.append({
            'folio': folio,
            'paragraph_idx': pidx,
            'section': section,
            'n_tokens': n_total,
            'n_headless': n_hl,
            'features': features
        })

    return paragraphs


def compute_group_means_expanded(x, group_ids, max_id=None):
    """Return per-observation group mean array."""
    if max_id is None:
        max_id = group_ids.max() + 1
    counts = np.bincount(group_ids, minlength=max_id)
    sums = np.bincount(group_ids, weights=x, minlength=max_id)
    means = np.divide(sums, counts, out=np.zeros_like(sums, dtype=float), where=counts > 0)
    return means[group_ids]


def hierarchical_variance_decomposition_3level(x, s_ids, f_ids):
    """Compute nested variance partition for 3 levels: section, folio|section, residual.

    Observation unit is the paragraph.

    Returns dict with variance shares for each level.
    """
    n = len(x)
    if n < 3:
        return {'section': 0.0, 'folio': 0.0, 'residual': 0.0, 'valid_n': n, 'ss_total': 0.0}

    grand_mean = np.mean(x)
    ss_total = np.sum((x - grand_mean) ** 2)

    if ss_total < 1e-15:
        return {'section': 0.0, 'folio': 0.0, 'residual': 0.0, 'valid_n': n, 'ss_total': 0.0}

    s_means = compute_group_means_expanded(x, s_ids)
    f_means = compute_group_means_expanded(x, f_ids)

    ss_section = np.sum((s_means - grand_mean) ** 2)
    ss_folio = np.sum((f_means - s_means) ** 2)
    ss_residual = np.sum((x - f_means) ** 2)

    return {
        'section': float(ss_section / ss_total),
        'folio': float(ss_folio / ss_total),
        'residual': float(ss_residual / ss_total),
        'valid_n': n,
        'ss_total': float(ss_total)
    }


def build_group_indices(paragraphs):
    """Build integer group index arrays for section and folio levels.

    Returns:
        section_ids: int array (per paragraph)
        folio_ids: int array (per paragraph)
        section_map: str->int
        folio_map: str->int
        folio_to_section: int array (folio_id -> section_id)
    """
    section_map = {}
    folio_map = {}

    section_ids = np.zeros(len(paragraphs), dtype=np.int32)
    folio_ids = np.zeros(len(paragraphs), dtype=np.int32)

    for i, p in enumerate(paragraphs):
        sec = p['section']
        fol = p['folio']

        if sec not in section_map:
            section_map[sec] = len(section_map)
        if fol not in folio_map:
            folio_map[fol] = len(folio_map)

        section_ids[i] = section_map[sec]
        folio_ids[i] = folio_map[fol]

    # Build folio->section mapping
    folio_to_section = np.zeros(len(folio_map), dtype=np.int32)
    for p in paragraphs:
        fid = folio_map[p['folio']]
        sid = section_map[p['section']]
        folio_to_section[fid] = sid

    return section_ids, folio_ids, section_map, folio_map, folio_to_section


def run_null_section_shuffle(feature_arrays, s_ids, f_ids, folio_to_section, rng, n_perms):
    """Null model 1: permute section labels across folios."""
    results = {fname: [] for fname in FEATURE_NAMES}

    for perm_i in range(n_perms):
        shuffled_f2s = folio_to_section.copy()
        rng.shuffle(shuffled_f2s)
        s_ids_null = shuffled_f2s[f_ids]

        for fi, fname in enumerate(FEATURE_NAMES):
            vs = hierarchical_variance_decomposition_3level(feature_arrays[fi], s_ids_null, f_ids)
            results[fname].append(vs)

    return results


def run_null_folio_shuffle(feature_arrays, s_ids, f_ids, folio_to_section, paragraphs, rng, n_perms):
    """Null model 2: shuffle paragraph->folio assignments within sections.

    Reassign paragraphs to different folios within the same section, preserving
    how many paragraphs go to each folio.
    """
    n_paras = len(paragraphs)

    # Group paragraph indices by section
    section_paras = defaultdict(list)
    for i in range(n_paras):
        sid = int(s_ids[i])
        section_paras[sid].append(i)

    # Pre-compute folio assignments per section
    section_folio_assigns = {}
    for sid, pidxs in section_paras.items():
        section_folio_assigns[sid] = np.array([f_ids[i] for i in pidxs])

    results = {fname: [] for fname in FEATURE_NAMES}

    for perm_i in range(n_perms):
        f_ids_null = f_ids.copy()
        for sid, pidxs in section_paras.items():
            folio_assigns = section_folio_assigns[sid].copy()
            rng.shuffle(folio_assigns)
            for pi, new_fid in zip(pidxs, folio_assigns):
                f_ids_null[pi] = new_fid

        for fi, fname in enumerate(FEATURE_NAMES):
            vs = hierarchical_variance_decomposition_3level(feature_arrays[fi], s_ids, f_ids_null)
            results[fname].append(vs)

    return results


def summarize_null(null_results):
    """Compute mean/std of each VS component across permutations."""
    summary = {}
    levels = ['section', 'folio', 'residual']
    for fname, perm_results in null_results.items():
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


def step_b_hierarchical_attribution(paragraphs, feature_arrays, rng):
    """Step B: Hierarchical variance decomposition with null models."""
    print("\n--- Step B: Hierarchical Variance Attribution ---")

    s_ids, f_ids, section_map, folio_map, folio_to_section = build_group_indices(paragraphs)

    n_sections = len(section_map)
    n_folios = len(folio_map)
    print(f"  {len(paragraphs)} paragraphs, {n_sections} sections, {n_folios} folios")

    # Real decomposition
    print("  Computing real variance decomposition...")
    real_results = {}
    for fi, fname in enumerate(FEATURE_NAMES):
        vs = hierarchical_variance_decomposition_3level(feature_arrays[fi], s_ids, f_ids)
        real_results[fname] = vs
        print(f"    {fname}: S={vs['section']:.4f} F|S={vs['folio']:.4f} R={vs['residual']:.4f}")

    # Null model 1: section shuffle
    print(f"  Running section-shuffle null ({N_PERMS_VS} perms)...")
    null_section = run_null_section_shuffle(feature_arrays, s_ids, f_ids,
                                            folio_to_section, rng, N_PERMS_VS)
    null_section_summary = summarize_null(null_section)

    # Null model 2: folio shuffle within section
    print(f"  Running folio-shuffle-within-section null ({N_PERMS_VS} perms)...")
    null_folio = run_null_folio_shuffle(feature_arrays, s_ids, f_ids,
                                        folio_to_section, paragraphs, rng, N_PERMS_VS)
    null_folio_summary = summarize_null(null_folio)

    # Significance z-scores
    significance = {}
    for fname in FEATURE_NAMES:
        sig = {}
        # Section VS vs section-shuffle null
        ns = null_section_summary[fname]['section']
        real_val = real_results[fname]['section']
        z = (real_val - ns['mean']) / ns['std'] if ns['std'] > 0 else (float('inf') if real_val > ns['mean'] else 0)
        sig['section'] = {
            'real': round(real_val, 5), 'null_mean': round(ns['mean'], 5),
            'null_std': round(ns['std'], 5), 'z_score': round(z, 2), 'significant': z > 2.0
        }

        # Folio VS vs folio-shuffle null
        nf = null_folio_summary[fname]['folio']
        real_val_f = real_results[fname]['folio']
        z_f = (real_val_f - nf['mean']) / nf['std'] if nf['std'] > 0 else (float('inf') if real_val_f > nf['mean'] else 0)
        sig['folio'] = {
            'real': round(real_val_f, 5), 'null_mean': round(nf['mean'], 5),
            'null_std': round(nf['std'], 5), 'z_score': round(z_f, 2), 'significant': z_f > 2.0
        }

        significance[fname] = sig

    print("\n  Significance (z-scores):")
    for fname in FEATURE_NAMES:
        s_z = significance[fname]['section']['z_score']
        f_z = significance[fname]['folio']['z_score']
        print(f"    {fname}: section={s_z:.1f}z, folio={f_z:.1f}z")

    # Criteria T4-A and T4-B
    t4a_count = sum(1 for f in FEATURE_NAMES if real_results[f]['section'] > 0.05)
    t4a_pass = t4a_count >= 5
    t4a = {
        'pass': t4a_pass, 'count': t4a_count, 'threshold': 5,
        'details': {f: round(real_results[f]['section'], 5) for f in FEATURE_NAMES}
    }

    t4b_count = sum(1 for f in FEATURE_NAMES if real_results[f]['folio'] > real_results[f]['section'])
    t4b_pass = t4b_count >= 3
    t4b = {
        'pass': t4b_pass, 'count': t4b_count, 'threshold': 3,
        'details': {f: {
            'folio': round(real_results[f]['folio'], 5),
            'section': round(real_results[f]['section'], 5),
            'folio_gt_section': real_results[f]['folio'] > real_results[f]['section']
        } for f in FEATURE_NAMES}
    }

    print(f"\n  T4-A: VS_section > 0.05 for {t4a_count}/14 features -> {'PASS' if t4a_pass else 'FAIL'}")
    print(f"  T4-B: VS_folio|section > VS_section for {t4b_count}/14 features -> {'PASS' if t4b_pass else 'FAIL'}")

    return {
        'real_variance_shares': {f: {k: round(v, 5) for k, v in real_results[f].items()
                                      if k != 'valid_n' and k != 'ss_total'}
                                  for f in FEATURE_NAMES},
        'real_results_full': {f: {k: round(v, 5) if isinstance(v, float) else v
                                   for k, v in real_results[f].items()}
                               for f in FEATURE_NAMES},
        'null_summaries': {
            'section_shuffle': null_section_summary,
            'folio_shuffle': null_folio_summary
        },
        'significance': significance,
        'criteria': {'T4-A': t4a, 'T4-B': t4b},
        'n_sections': n_sections,
        'n_folios': n_folios
    }


def step_c_paragraph_dispersion(paragraphs, feature_arrays, rng):
    """Step C: Paragraph-within-folio headless ecology dispersion.

    For each folio with >= 3 qualifying paragraphs, compute mean pairwise
    Euclidean distance between paragraph feature vectors (14D).
    Compare to null: shuffle headless tokens across paragraphs within folio,
    recompute features, measure dispersion.

    Approach: since we cannot re-extract features from shuffled tokens directly
    (we have paragraph-level aggregates), we shuffle the feature vectors across
    paragraphs within the folio and recompute pairwise distances.
    This tests whether within-folio paragraph differentiation is real.
    """
    print("\n--- Step C: Paragraph-Within-Folio Dispersion ---")

    # Group paragraphs by folio
    folio_paras = defaultdict(list)
    for i, p in enumerate(paragraphs):
        folio_paras[p['folio']].append(i)

    # Qualify: folios with >= 3 paragraphs
    qualifying_folios = {f: idxs for f, idxs in folio_paras.items() if len(idxs) >= 3}
    print(f"  Qualifying folios (>=3 paras): {len(qualifying_folios)}")

    if len(qualifying_folios) == 0:
        return {'pass': False, 'reason': 'no qualifying folios', 'n_qualifying': 0}

    # Build full feature matrix (n_paragraphs x 14)
    feat_matrix = np.column_stack(feature_arrays)  # shape: (n_paras, 14)

    folio_results = {}

    for folio, pidxs in sorted(qualifying_folios.items()):
        vecs = feat_matrix[pidxs]  # shape: (n_paras_in_folio, 14)
        n = len(vecs)

        # Real mean pairwise Euclidean distance
        real_dists = []
        for i, j in combinations(range(n), 2):
            real_dists.append(np.linalg.norm(vecs[i] - vecs[j]))
        real_mean_dist = np.mean(real_dists) if real_dists else 0.0

        # Get the section for this folio (to find same-section paragraphs)
        folio_section = paragraphs[pidxs[0]]['section']

        # Null: shuffle paragraph feature vectors within the section,
        # preserving folio sizes. This tests whether THIS folio's paragraphs
        # are more diverse than random same-section paragraphs.
        sec_idxs = [i for i, p in enumerate(paragraphs) if p['section'] == folio_section]
        sec_vecs = feat_matrix[sec_idxs]

        null_means = []
        for seed_i in range(N_PERMS_DISP):
            perm = rng.permutation(len(sec_vecs))
            # Take first n vectors as the "folio" paragraphs
            null_vecs = sec_vecs[perm[:n]]
            null_dists = []
            for i, j in combinations(range(n), 2):
                null_dists.append(np.linalg.norm(null_vecs[i] - null_vecs[j]))
            null_means.append(np.mean(null_dists) if null_dists else 0.0)

        null_mean = np.mean(null_means)
        null_std = np.std(null_means)
        exceeds = real_mean_dist > null_mean + 2 * null_std

        folio_results[folio] = {
            'n_paras': n,
            'section': folio_section,
            'real_mean_dist': round(float(real_mean_dist), 6),
            'null_mean': round(float(null_mean), 6),
            'null_std': round(float(null_std), 6),
            'exceeds_2sigma': exceeds
        }

    n_exceed = sum(1 for v in folio_results.values() if v['exceeds_2sigma'])
    n_total = len(folio_results)
    frac_exceed = n_exceed / n_total if n_total > 0 else 0
    t4c_pass = frac_exceed >= 0.30

    print(f"  Folios exceeding null+2sigma: {n_exceed}/{n_total} ({frac_exceed:.1%})")
    print(f"  T4-C: {'PASS' if t4c_pass else 'FAIL'} (threshold: 30%)")

    return {
        'per_folio': folio_results,
        'n_qualifying': n_total,
        'n_exceeding': n_exceed,
        'fraction_exceeding': round(frac_exceed, 4),
        'threshold': 0.30,
        'pass': t4c_pass
    }


def step_d_section_discrimination(paragraphs, feature_arrays, rng):
    """Step D: Within-section headless folio discrimination.

    Average headless features to folio level. For each test section, compute
    pairwise Euclidean distance between folio vectors. Compare to null:
    shuffle paragraphs across folios within section (300 seeds).

    T4-D PASS: real mean distance > null + 2sigma for >= 1/3 sections.
    """
    print("\n--- Step D: Within-Section Folio Discrimination ---")

    feat_matrix = np.column_stack(feature_arrays)

    # Group paragraphs by section and folio
    sec_folio_paras = defaultdict(lambda: defaultdict(list))
    for i, p in enumerate(paragraphs):
        sec_folio_paras[p['section']][p['folio']].append(i)

    section_results = {}

    for section in TEST_SECTIONS:
        folio_paras = sec_folio_paras.get(section, {})

        # Average features to folio level
        folio_vecs = {}
        for folio, pidxs in folio_paras.items():
            vecs = feat_matrix[pidxs]
            folio_vecs[folio] = np.mean(vecs, axis=0)

        folio_list = sorted(folio_vecs.keys())
        n_folios = len(folio_list)

        if n_folios < 3:
            section_results[section] = {
                'status': 'SKIP', 'reason': f'too few folios ({n_folios})', 'pass': False
            }
            print(f"  {section}: SKIP (too few folios: {n_folios})")
            continue

        # Real mean pairwise Euclidean distance between folio vectors
        folio_matrix = np.array([folio_vecs[f] for f in folio_list])
        real_dists = []
        for i, j in combinations(range(n_folios), 2):
            real_dists.append(np.linalg.norm(folio_matrix[i] - folio_matrix[j]))
        real_mean = np.mean(real_dists)

        # Null: shuffle paragraphs across folios within section
        all_pidxs = []
        folio_sizes = []
        for f in folio_list:
            all_pidxs.extend(folio_paras[f])
            folio_sizes.append(len(folio_paras[f]))

        all_vecs = feat_matrix[all_pidxs]

        null_means = []
        for seed_i in range(N_PERMS_DISP):
            perm = rng.permutation(len(all_vecs))
            shuffled = all_vecs[perm]

            # Reconstruct folio groupings with shuffled paragraphs
            idx = 0
            null_folio_vecs = []
            for fi in range(n_folios):
                group = shuffled[idx:idx + folio_sizes[fi]]
                null_folio_vecs.append(np.mean(group, axis=0))
                idx += folio_sizes[fi]

            null_folio_matrix = np.array(null_folio_vecs)
            null_dists = []
            for i, j in combinations(range(n_folios), 2):
                null_dists.append(np.linalg.norm(null_folio_matrix[i] - null_folio_matrix[j]))
            null_means.append(np.mean(null_dists))

        null_mean = np.mean(null_means)
        null_std = np.std(null_means)
        exceeds = real_mean > null_mean + 2 * null_std
        z = (real_mean - null_mean) / null_std if null_std > 0 else 0

        section_results[section] = {
            'status': 'TESTED',
            'n_folios': n_folios,
            'n_paragraphs': len(all_pidxs),
            'real_mean_dist': round(float(real_mean), 6),
            'null_mean': round(float(null_mean), 6),
            'null_std': round(float(null_std), 6),
            'z_score': round(float(z), 2),
            'exceeds_2sigma': exceeds,
            'pass': exceeds
        }

        print(f"  {section}: real={real_mean:.6f}, null={null_mean:.6f}+/-{null_std:.6f}, "
              f"z={z:.2f} -> {'PASS' if exceeds else 'FAIL'} "
              f"({n_folios} folios, {len(all_pidxs)} paras)")

    pass_count = sum(1 for v in section_results.values() if v.get('pass', False))
    tested_count = sum(1 for v in section_results.values() if v.get('status') == 'TESTED')
    # >= 1/3 of tested sections
    threshold = max(1, tested_count // 3) if tested_count > 0 else 1
    t4d_pass = pass_count >= threshold

    print(f"  T4-D: {pass_count}/{tested_count} sections pass (threshold: {threshold}) -> "
          f"{'PASS' if t4d_pass else 'FAIL'}")

    return {
        'per_section': section_results,
        'pass_count': pass_count,
        'tested_count': tested_count,
        'threshold': threshold,
        'pass': t4d_pass
    }


def main():
    t_start = time.time()
    print("Phase 561 T4: Headless Token Ecology — Hierarchical Attribution")
    print("=" * 65)

    # Load corpus
    print("Loading T1 corpus...")
    tokens = load_corpus()
    n_hl = sum(1 for t in tokens if t['domain'] == 'HEADLESS')
    print(f"  {len(tokens)} tokens, {n_hl} headless")

    # Step A: Compute paragraph-level headless ecology features
    print("\n--- Step A: Headless Feature Extraction ---")
    paragraphs = compute_paragraph_features(tokens)
    print(f"  {len(paragraphs)} qualifying paragraphs (>={MIN_HL_PER_PARA} headless tokens)")

    # Per-section counts
    sec_counts = defaultdict(int)
    for p in paragraphs:
        sec_counts[p['section']] += 1
    for s in sorted(sec_counts.keys()):
        print(f"    {s}: {sec_counts[s]} paragraphs")

    # Build feature arrays (14 arrays, each length = n_paragraphs)
    feature_arrays = []
    for fi in range(len(FEATURE_NAMES)):
        arr = np.array([p['features'][fi] for p in paragraphs])
        feature_arrays.append(arr)

    # Feature summary
    print("\n  Feature summary:")
    for fi, fname in enumerate(FEATURE_NAMES):
        arr = feature_arrays[fi]
        print(f"    {fname}: mean={np.mean(arr):.4f}, std={np.std(arr):.4f}, "
              f"min={np.min(arr):.4f}, max={np.max(arr):.4f}")

    # Initialize RNG
    rng = np.random.default_rng(RNG_SEED)

    # Step B: Hierarchical variance decomposition
    step_b_results = step_b_hierarchical_attribution(paragraphs, feature_arrays, rng)

    # Step C: Paragraph-within-folio dispersion
    step_c_results = step_c_paragraph_dispersion(paragraphs, feature_arrays, rng)

    # Step D: Within-section folio discrimination
    step_d_results = step_d_section_discrimination(paragraphs, feature_arrays, rng)

    # Overall verdict
    t4a_pass = step_b_results['criteria']['T4-A']['pass']
    t4b_pass = step_b_results['criteria']['T4-B']['pass']
    t4c_pass = step_c_results['pass']
    t4d_pass = step_d_results['pass']

    overall_pass = t4a_pass and t4b_pass and t4c_pass and t4d_pass

    elapsed = time.time() - t_start

    print(f"\n{'=' * 65}")
    print("CRITERIA SUMMARY")
    print(f"{'=' * 65}")
    print(f"  T4-A (VS_section > 0.05 for >=5/14): "
          f"{'PASS' if t4a_pass else 'FAIL'} ({step_b_results['criteria']['T4-A']['count']}/14)")
    print(f"  T4-B (VS_folio|section > VS_section for >=3/14): "
          f"{'PASS' if t4b_pass else 'FAIL'} ({step_b_results['criteria']['T4-B']['count']}/14)")
    print(f"  T4-C (>=30% folios dispersion > null+2sigma): "
          f"{'PASS' if t4c_pass else 'FAIL'} ({step_c_results.get('fraction_exceeding', 0):.1%})")
    print(f"  T4-D (>=1/3 sections distance > null+2sigma): "
          f"{'PASS' if t4d_pass else 'FAIL'} ({step_d_results['pass_count']}/{step_d_results['tested_count']})")
    print(f"\n  Overall T4: {'PASS' if overall_pass else 'FAIL'}")
    print(f"  Elapsed: {elapsed:.1f}s")

    # Build paragraph detail records for output
    para_details = []
    for i, p in enumerate(paragraphs):
        detail = {
            'folio': p['folio'],
            'paragraph_idx': p['paragraph_idx'],
            'section': p['section'],
            'n_tokens': p['n_tokens'],
            'n_headless': p['n_headless'],
        }
        for fi, fname in enumerate(FEATURE_NAMES):
            detail[fname] = round(p['features'][fi], 5)
        para_details.append(detail)

    # Assemble output
    output = {
        'metadata': {
            'phase': 'HIERARCHICAL_TRACE_ATTRIBUTION',
            'task': 'T4',
            'name': 'Headless Token Ecology — Hierarchical Attribution',
            'n_tokens': len(tokens),
            'n_headless_tokens': n_hl,
            'n_qualifying_paragraphs': len(paragraphs),
            'min_headless_per_para': MIN_HL_PER_PARA,
            'n_perms_vs': N_PERMS_VS,
            'n_perms_disp': N_PERMS_DISP,
            'rng_seed': RNG_SEED,
            'feature_names': FEATURE_NAMES,
            'elapsed_seconds': round(elapsed, 1)
        },
        'step_A_paragraph_features': para_details,
        'step_B_hierarchical_attribution': step_b_results,
        'step_C_paragraph_dispersion': step_c_results,
        'step_D_section_discrimination': step_d_results,
        'criteria': {
            'T4-A': step_b_results['criteria']['T4-A'],
            'T4-B': step_b_results['criteria']['T4-B'],
            'T4-C': {
                'pass': t4c_pass,
                'n_qualifying_folios': step_c_results.get('n_qualifying', 0),
                'n_exceeding': step_c_results.get('n_exceeding', 0),
                'fraction_exceeding': step_c_results.get('fraction_exceeding', 0),
                'threshold': 0.30
            },
            'T4-D': {
                'pass': t4d_pass,
                'pass_count': step_d_results['pass_count'],
                'tested_count': step_d_results['tested_count'],
                'threshold': step_d_results['threshold']
            }
        },
        'overall_pass': overall_pass
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults written to {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
