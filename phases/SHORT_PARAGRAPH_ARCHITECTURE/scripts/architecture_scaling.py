"""
Phase 625: SHORT_PARAGRAPH_ARCHITECTURE -- Script 2: Architecture Scaling

Tests whether short paragraphs are truncated beginnings of long paragraphs or
structurally distinct operational objects.

Five analyses:
  T1: Position-matched subsample null (THE KEY TEST)
  T2: Minimum viable paragraph (line-level arc scaling)
  T3: Kernel gradient in short paragraphs
  T4: m-terminal and terminal opacity by stratum
  T5: Header-body coupling by stratum

Output: results/architecture_scaling.json
"""

import sys
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from phases.SHORT_PARAGRAPH_ARCHITECTURE.scripts.shared_625 import (
    build_corpus, assign_stratum, get_all_tokens, extract_paragraph_features,
    position_matched_subsample, extract_header_features,
    STRATA, STRATUM_ORDER, FEATURE_NAMES, CATEGORIES, RESULTS_DIR, RNG, N_PERM,
    round_floats, ks_test, mann_whitney_u, spearman_rho, cohens_d, cosine_similarity,
    section_residualize_values, _OPACITY_NUMERIC, MODE_A_SUFFIXES, MODE_B_SUFFIXES,
)


# ============================================================
# Helper: compute per-line feature vector (12-dim) for T2
# ============================================================

T2_LINE_FEATURE_NAMES = [
    'MARKING_frac', 'STAGING_frac', 'THERMAL_frac', 'FLOW_frac',
    'TRANSITION_frac', 'CONTAINMENT_frac', 'artic_rate', 'm_terminal_rate',
    'mean_opacity', 'mode_a_frac', 'headless_rate', 'tokens_per_line',
]


def _line_feature_vector(line_dict):
    """
    Compute a 12-dim feature vector for a single body line.

    Returns list of 12 floats in T2_LINE_FEATURE_NAMES order.
    """
    tokens = line_dict.get('tokens', [])
    n = len(tokens)
    if n == 0:
        return [0.0] * 12

    # Category fractions (only among tokens with a recognized category)
    cat_counts = Counter()
    for t in tokens:
        cat = t.get('category', 'UNKNOWN')
        if cat in CATEGORIES:
            cat_counts[cat] += 1
    cat_total = sum(cat_counts.values())

    marking_frac = cat_counts.get('MARKING', 0) / cat_total if cat_total > 0 else 0.0
    staging_frac = cat_counts.get('STAGING', 0) / cat_total if cat_total > 0 else 0.0
    thermal_frac = cat_counts.get('THERMAL', 0) / cat_total if cat_total > 0 else 0.0
    flow_frac = cat_counts.get('FLOW', 0) / cat_total if cat_total > 0 else 0.0
    transition_frac = cat_counts.get('TRANSITION', 0) / cat_total if cat_total > 0 else 0.0
    containment_frac = cat_counts.get('CONTAINMENT', 0) / cat_total if cat_total > 0 else 0.0

    artic_rate = sum(1 for t in tokens if t.get('articulator', '')) / n
    m_terminal_rate = sum(1 for t in tokens if t.get('term') == 'm') / n

    opacity_sum = 0.0
    for t in tokens:
        tier = t.get('terminal_opacity', 'BARE')
        opacity_sum += _OPACITY_NUMERIC.get(tier, 0.0)
    mean_opacity = opacity_sum / n

    mode_a_frac = sum(1 for t in tokens if t.get('suffix_mode') == 'A') / n
    headless_rate = sum(1 for t in tokens if t.get('is_headless', False)) / n
    tokens_per_line = float(n)

    return [
        marking_frac, staging_frac, thermal_frac, flow_frac,
        transition_frac, containment_frac, artic_rate, m_terminal_rate,
        mean_opacity, mode_a_frac, headless_rate, tokens_per_line,
    ]


def _mean_vector(vectors):
    """Element-wise mean of a list of equal-length vectors."""
    if not vectors:
        return []
    d = len(vectors[0])
    n = len(vectors)
    return [sum(v[i] for v in vectors) / n for i in range(d)]


# ============================================================
# Helper: extract body-only features for T5
# ============================================================

def _extract_body_features(paragraph):
    """
    Compute the 11-feature profile from body lines only.

    Creates a temporary paragraph with empty header_lines and the
    original body_lines, then calls extract_paragraph_features.
    """
    temp = {
        'header_lines': [],
        'body_lines': paragraph.get('body_lines', []),
        'id': paragraph.get('id', '?'),
    }
    return extract_paragraph_features(temp)


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 625, Script 2: Architecture Scaling")
    print("=" * 60)

    # ---- Build corpus ----
    print("\n[CORPUS] Building paragraph corpus...")
    corpus = build_corpus()

    # Flatten all paragraphs with metadata
    all_paragraphs = []
    for folio, fdata in sorted(corpus.items()):
        section = fdata['section']
        for para in fdata['paragraphs']:
            stratum = assign_stratum(para)
            all_paragraphs.append({
                'paragraph': para,
                'folio': folio,
                'section': section,
                'stratum': stratum,
                'n_body': len(para.get('body_lines', [])),
            })

    # Stratum counts
    stratum_counts = Counter(p['stratum'] for p in all_paragraphs)
    for s in STRATUM_ORDER:
        print(f"  {s}: {stratum_counts.get(s, 0)}")
    print(f"  Total: {len(all_paragraphs)}")

    # Group by stratum
    by_stratum = defaultdict(list)
    for p in all_paragraphs:
        by_stratum[p['stratum']].append(p)

    n_long = stratum_counts.get('LONG', 0)
    n_short = stratum_counts.get('SHORT', 0)
    n_minimal = stratum_counts.get('MINIMAL', 0)

    # Pre-compute 11 features for all paragraphs
    print("\n[FEATURES] Computing 11-feature profiles...")
    for p in all_paragraphs:
        p['features'] = extract_paragraph_features(p['paragraph'])
        p['feature_vector'] = [p['features'][fn] for fn in FEATURE_NAMES]

    results = {
        'metadata': {
            'phase': 625,
            'script': 2,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'n_long': n_long,
            'n_short': n_short,
            'n_minimal': n_minimal,
            'n_header_only': stratum_counts.get('HEADER_ONLY', 0),
            'n_total': len(all_paragraphs),
        },
    }

    # ============================================================
    # T1: Position-matched subsample null (THE KEY TEST)
    # ============================================================
    print("\n" + "=" * 60)
    print("[T1] Position-Matched Subsample Null")
    print("=" * 60)

    long_paras = by_stratum['LONG']
    minimal_paras = by_stratum['MINIMAL']
    short_paras = by_stratum['SHORT']

    # ---- Section-matched comparisons ----
    # Group paragraphs by section
    long_by_section = defaultdict(list)
    for p in long_paras:
        long_by_section[p['section']].append(p)

    minimal_by_section = defaultdict(list)
    for p in minimal_paras:
        minimal_by_section[p['section']].append(p)

    short_by_section = defaultdict(list)
    for p in short_paras:
        short_by_section[p['section']].append(p)

    def _compute_features_for_truncated(paragraph, n_body):
        """Truncate a LONG paragraph to n_body lines and compute features."""
        truncated = position_matched_subsample(paragraph, n_body)
        return extract_paragraph_features(truncated)

    def _compute_features_for_random_subsample(paragraph, n_body, n_reps=200):
        """
        Randomly select n_body body lines from paragraph, n_reps times.
        Average the feature vectors.
        """
        body = paragraph.get('body_lines', [])
        if len(body) <= n_body:
            feats = extract_paragraph_features(paragraph)
            return [feats[fn] for fn in FEATURE_NAMES]

        all_vecs = []
        for _ in range(n_reps):
            sampled_lines = RNG.sample(body, n_body)
            temp = {
                'header_lines': paragraph.get('header_lines', []),
                'body_lines': sampled_lines,
                'id': paragraph.get('id', '?'),
            }
            feats = extract_paragraph_features(temp)
            all_vecs.append([feats[fn] for fn in FEATURE_NAMES])

        return _mean_vector(all_vecs)

    def _run_ks_comparison(real_features_list, synthetic_features_list):
        """
        Run per-feature KS test between real and synthetic feature vectors.

        Args:
            real_features_list: list of dicts (feature_name -> value) for real paragraphs
            synthetic_features_list: list of dicts (feature_name -> value) for synthetic paragraphs

        Returns:
            dict: feature_name -> {'D': .., 'p': ..}, n_pass count
        """
        per_feature = {}
        n_pass = 0
        for fn in FEATURE_NAMES:
            real_vals = [f[fn] for f in real_features_list]
            synth_vals = [f[fn] for f in synthetic_features_list]
            if len(real_vals) < 3 or len(synth_vals) < 3:
                per_feature[fn] = {'D': 0.0, 'p': 1.0, 'n_real': len(real_vals), 'n_synth': len(synth_vals)}
                n_pass += 1
                continue
            result = ks_test(real_vals, synth_vals)
            per_feature[fn] = {
                'D': result['D'],
                'p': result['p'],
                'n_real': len(real_vals),
                'n_synth': len(synth_vals),
            }
            if result['p'] > 0.05:
                n_pass += 1
        return per_feature, n_pass

    def _run_ks_comparison_vectors(real_vectors, synthetic_vectors):
        """
        Same as _run_ks_comparison but with pre-computed vectors (lists of floats).
        """
        per_feature = {}
        n_pass = 0
        for fi, fn in enumerate(FEATURE_NAMES):
            real_vals = [v[fi] for v in real_vectors]
            synth_vals = [v[fi] for v in synthetic_vectors]
            if len(real_vals) < 3 or len(synth_vals) < 3:
                per_feature[fn] = {'D': 0.0, 'p': 1.0, 'n_real': len(real_vals), 'n_synth': len(synth_vals)}
                n_pass += 1
                continue
            result = ks_test(real_vals, synth_vals)
            per_feature[fn] = {
                'D': result['D'],
                'p': result['p'],
                'n_real': len(real_vals),
                'n_synth': len(synth_vals),
            }
            if result['p'] > 0.05:
                n_pass += 1
        return per_feature, n_pass

    # ---- POOLED comparison ----
    print("\n  [T1a] Pooled comparisons...")

    # Position-matched: truncate LONG to 1-2 body lines -> compare with MINIMAL
    print("    Generating position-matched truncated LONG paragraphs...")
    posmatched_minimal_features = []
    for p in long_paras:
        para = p['paragraph']
        if len(para.get('body_lines', [])) >= 2:
            # Truncate to 1 body line and 2 body lines, average
            for nb in [1, 2]:
                feats = _compute_features_for_truncated(para, nb)
                posmatched_minimal_features.append(feats)

    real_minimal_features = [p['features'] for p in minimal_paras]
    pm_minimal_comp, pm_minimal_npass = _run_ks_comparison(real_minimal_features, posmatched_minimal_features)
    print(f"    Position-matched MINIMAL: {pm_minimal_npass}/11 features pass (p > 0.05)")

    # Position-matched: truncate LONG to 3-4 body lines -> compare with SHORT
    posmatched_short_features = []
    for p in long_paras:
        para = p['paragraph']
        if len(para.get('body_lines', [])) >= 4:
            for nb in [3, 4]:
                feats = _compute_features_for_truncated(para, nb)
                posmatched_short_features.append(feats)

    real_short_features = [p['features'] for p in short_paras]
    pm_short_comp, pm_short_npass = _run_ks_comparison(real_short_features, posmatched_short_features)
    print(f"    Position-matched SHORT: {pm_short_npass}/11 features pass (p > 0.05)")

    # Random subsample: LONG -> 1-2 body lines, compare with MINIMAL
    print("    Generating random-subsampled LONG paragraphs (200 reps)...")
    random_minimal_vectors = []
    for p in long_paras:
        para = p['paragraph']
        if len(para.get('body_lines', [])) >= 2:
            for nb in [1, 2]:
                vec = _compute_features_for_random_subsample(para, nb, n_reps=200)
                random_minimal_vectors.append(vec)

    real_minimal_vectors = [p['feature_vector'] for p in minimal_paras]
    rand_minimal_comp, rand_minimal_npass = _run_ks_comparison_vectors(real_minimal_vectors, random_minimal_vectors)
    print(f"    Random-subsample MINIMAL: {rand_minimal_npass}/11 features pass (p > 0.05)")

    # Random subsample: LONG -> 3-4 body lines, compare with SHORT
    random_short_vectors = []
    for p in long_paras:
        para = p['paragraph']
        if len(para.get('body_lines', [])) >= 4:
            for nb in [3, 4]:
                vec = _compute_features_for_random_subsample(para, nb, n_reps=200)
                random_short_vectors.append(vec)

    real_short_vectors = [p['feature_vector'] for p in short_paras]
    rand_short_comp, rand_short_npass = _run_ks_comparison_vectors(real_short_vectors, random_short_vectors)
    print(f"    Random-subsample SHORT: {rand_short_npass}/11 features pass (p > 0.05)")

    # ---- SECTION-MATCHED comparisons ----
    print("\n  [T1b] Section-matched comparisons...")
    shared_sections_minimal = sorted(
        set(long_by_section.keys()) & set(minimal_by_section.keys())
    )
    shared_sections_short = sorted(
        set(long_by_section.keys()) & set(short_by_section.keys())
    )

    section_matched = {}

    # Section-matched: MINIMAL comparison
    sec_pm_minimal_all = []
    sec_real_minimal_all = []
    sec_pm_minimal_detail = {}

    for sec in shared_sections_minimal:
        sec_long = long_by_section[sec]
        sec_min = minimal_by_section[sec]
        if len(sec_long) < 3 or len(sec_min) < 3:
            continue

        pm_feats = []
        for p in sec_long:
            para = p['paragraph']
            if len(para.get('body_lines', [])) >= 2:
                for nb in [1, 2]:
                    feats = _compute_features_for_truncated(para, nb)
                    pm_feats.append(feats)

        real_feats = [p['features'] for p in sec_min]

        if len(pm_feats) >= 3 and len(real_feats) >= 3:
            comp, npass = _run_ks_comparison(real_feats, pm_feats)
            sec_pm_minimal_detail[sec] = {
                'per_feature': comp,
                'n_pass': npass,
                'n_real': len(real_feats),
                'n_synthetic': len(pm_feats),
            }
            sec_pm_minimal_all.extend(pm_feats)
            sec_real_minimal_all.extend(real_feats)
            print(f"    Section {sec}: MINIMAL pos-matched {npass}/11 pass "
                  f"(n_real={len(real_feats)}, n_synth={len(pm_feats)})")

    # Pooled across sections for section-matched
    if sec_pm_minimal_all and sec_real_minimal_all:
        sm_pm_minimal_comp, sm_pm_minimal_npass = _run_ks_comparison(
            sec_real_minimal_all, sec_pm_minimal_all
        )
    else:
        sm_pm_minimal_comp, sm_pm_minimal_npass = {}, 0

    # Section-matched: SHORT comparison
    sec_pm_short_all = []
    sec_real_short_all = []
    sec_pm_short_detail = {}

    for sec in shared_sections_short:
        sec_long = long_by_section[sec]
        sec_sh = short_by_section[sec]
        if len(sec_long) < 3 or len(sec_sh) < 3:
            continue

        pm_feats = []
        for p in sec_long:
            para = p['paragraph']
            if len(para.get('body_lines', [])) >= 4:
                for nb in [3, 4]:
                    feats = _compute_features_for_truncated(para, nb)
                    pm_feats.append(feats)

        real_feats = [p['features'] for p in sec_sh]

        if len(pm_feats) >= 3 and len(real_feats) >= 3:
            comp, npass = _run_ks_comparison(real_feats, pm_feats)
            sec_pm_short_detail[sec] = {
                'per_feature': comp,
                'n_pass': npass,
                'n_real': len(real_feats),
                'n_synthetic': len(pm_feats),
            }
            sec_pm_short_all.extend(pm_feats)
            sec_real_short_all.extend(real_feats)
            print(f"    Section {sec}: SHORT pos-matched {npass}/11 pass "
                  f"(n_real={len(real_feats)}, n_synth={len(pm_feats)})")

    if sec_pm_short_all and sec_real_short_all:
        sm_pm_short_comp, sm_pm_short_npass = _run_ks_comparison(
            sec_real_short_all, sec_pm_short_all
        )
    else:
        sm_pm_short_comp, sm_pm_short_npass = {}, 0

    # Section-matched random subsample for MINIMAL
    sec_rand_minimal_all = []
    sec_real_minimal_rand_all = []

    for sec in shared_sections_minimal:
        sec_long = long_by_section[sec]
        sec_min = minimal_by_section[sec]
        if len(sec_long) < 3 or len(sec_min) < 3:
            continue

        rand_vecs = []
        for p in sec_long:
            para = p['paragraph']
            if len(para.get('body_lines', [])) >= 2:
                for nb in [1, 2]:
                    vec = _compute_features_for_random_subsample(para, nb, n_reps=200)
                    rand_vecs.append(vec)

        real_vecs = [p['feature_vector'] for p in sec_min]
        if len(rand_vecs) >= 3 and len(real_vecs) >= 3:
            sec_rand_minimal_all.extend(rand_vecs)
            sec_real_minimal_rand_all.extend(real_vecs)

    if sec_rand_minimal_all and sec_real_minimal_rand_all:
        sm_rand_minimal_comp, sm_rand_minimal_npass = _run_ks_comparison_vectors(
            sec_real_minimal_rand_all, sec_rand_minimal_all
        )
    else:
        sm_rand_minimal_comp, sm_rand_minimal_npass = {}, 0

    # Section-matched random subsample for SHORT
    sec_rand_short_all = []
    sec_real_short_rand_all = []

    for sec in shared_sections_short:
        sec_long = long_by_section[sec]
        sec_sh = short_by_section[sec]
        if len(sec_long) < 3 or len(sec_sh) < 3:
            continue

        rand_vecs = []
        for p in sec_long:
            para = p['paragraph']
            if len(para.get('body_lines', [])) >= 4:
                for nb in [3, 4]:
                    vec = _compute_features_for_random_subsample(para, nb, n_reps=200)
                    rand_vecs.append(vec)

        real_vecs = [p['feature_vector'] for p in sec_sh]
        if len(rand_vecs) >= 3 and len(real_vecs) >= 3:
            sec_rand_short_all.extend(rand_vecs)
            sec_real_short_rand_all.extend(real_vecs)

    if sec_rand_short_all and sec_real_short_rand_all:
        sm_rand_short_comp, sm_rand_short_npass = _run_ks_comparison_vectors(
            sec_real_short_rand_all, sec_rand_short_all
        )
    else:
        sm_rand_short_comp, sm_rand_short_npass = {}, 0

    # ---- Verdict logic ----
    # Use section-matched results as primary
    primary_pm_npass = sm_pm_minimal_npass
    primary_rand_npass = sm_rand_minimal_npass

    # If section-matched not available, fall back to pooled
    if not sm_pm_minimal_comp:
        primary_pm_npass = pm_minimal_npass
        primary_rand_npass = rand_minimal_npass
        verdict_source = 'pooled'
    else:
        verdict_source = 'section_matched'

    if primary_pm_npass >= 8 and primary_rand_npass < 8:
        # Position-matched passes, random fails -> truncated from start
        if primary_rand_npass <= 7:
            t1_verdict = 'TRUNCATED_FROM_START'
        else:
            t1_verdict = 'FULLY_TRUNCATED'
    elif primary_pm_npass >= 8:
        t1_verdict = 'FULLY_TRUNCATED'
    else:
        t1_verdict = 'DISTINCT'

    print(f"\n  T1 Verdict: {t1_verdict} (source: {verdict_source})")
    print(f"    Position-matched MINIMAL n_pass: {primary_pm_npass}/11")
    print(f"    Random-subsample MINIMAL n_pass: {primary_rand_npass}/11")

    results['T1_subsample_null'] = {
        'position_matched': {
            'minimal_comparison': pm_minimal_comp,
            'short_comparison': pm_short_comp,
            'n_pass_minimal': pm_minimal_npass,
            'n_pass_short': pm_short_npass,
        },
        'random': {
            'minimal_comparison': rand_minimal_comp,
            'short_comparison': rand_short_comp,
            'n_pass_minimal': rand_minimal_npass,
            'n_pass_short': rand_short_npass,
        },
        'section_matched': {
            'position_matched_minimal': {
                'per_section': sec_pm_minimal_detail,
                'pooled_across_sections': sm_pm_minimal_comp,
                'n_pass': sm_pm_minimal_npass,
            },
            'position_matched_short': {
                'per_section': sec_pm_short_detail,
                'pooled_across_sections': sm_pm_short_comp,
                'n_pass': sm_pm_short_npass,
            },
            'random_minimal': {
                'pooled_across_sections': sm_rand_minimal_comp,
                'n_pass': sm_rand_minimal_npass,
            },
            'random_short': {
                'pooled_across_sections': sm_rand_short_comp,
                'n_pass': sm_rand_short_npass,
            },
            'shared_sections_minimal': shared_sections_minimal,
            'shared_sections_short': shared_sections_short,
        },
        'verdict': t1_verdict,
        'verdict_source': verdict_source,
    }

    # ============================================================
    # T2: Minimum viable paragraph (LINE-LEVEL ARC SCALING)
    # ============================================================
    print("\n" + "=" * 60)
    print("[T2] Minimum Viable Paragraph (Line-Level Arc Scaling)")
    print("=" * 60)

    # For each stratum with >=2 body lines, compute first/last body line
    # feature vectors and their cosine similarity.

    per_stratum_cosine = {}
    per_stratum_first_last_mw = {}

    for stratum in STRATUM_ORDER:
        paras = by_stratum.get(stratum, [])
        # Filter to paragraphs with >=2 body lines
        eligible = [p for p in paras if p['n_body'] >= 2]
        if not eligible:
            print(f"  {stratum}: insufficient body lines (need >=2), skipping")
            continue

        first_vectors = []
        last_vectors = []

        for p in eligible:
            body = p['paragraph']['body_lines']
            first_vec = _line_feature_vector(body[0])
            last_vec = _line_feature_vector(body[-1])
            first_vectors.append(first_vec)
            last_vectors.append(last_vec)

        # Mean vectors
        mean_first = _mean_vector(first_vectors)
        mean_last = _mean_vector(last_vectors)

        if mean_first and mean_last:
            cos_sim = cosine_similarity(mean_first, mean_last)
        else:
            cos_sim = 0.0

        per_stratum_cosine[stratum] = {
            'cosine': cos_sim,
            'n_paragraphs': len(eligible),
            'mean_first': mean_first,
            'mean_last': mean_last,
        }

        # Per-feature first-vs-last Mann-Whitney
        feature_mw = {}
        for fi, fn in enumerate(T2_LINE_FEATURE_NAMES):
            first_vals = [v[fi] for v in first_vectors]
            last_vals = [v[fi] for v in last_vectors]
            if len(first_vals) >= 3 and len(last_vals) >= 3:
                mw = mann_whitney_u(first_vals, last_vals)
                d = cohens_d(first_vals, last_vals)
                feature_mw[fn] = {
                    'U': mw['U'], 'z': mw['z'], 'p': mw['p'],
                    'd': d,
                    'mean_first': sum(first_vals) / len(first_vals),
                    'mean_last': sum(last_vals) / len(last_vals),
                }
            else:
                feature_mw[fn] = {'U': 0, 'z': 0, 'p': 1.0, 'd': 0.0}

        per_stratum_first_last_mw[stratum] = feature_mw

        print(f"  {stratum} (n={len(eligible)}): cosine(first, last) = {cos_sim:.4f}")

    # Section-controlled: within Recipe only
    t2_section_controlled = {}
    recipe_paras = [p for p in all_paragraphs if p['section'] == 'Recipe']
    recipe_by_stratum = defaultdict(list)
    for p in recipe_paras:
        recipe_by_stratum[p['stratum']].append(p)

    for stratum in STRATUM_ORDER:
        paras = recipe_by_stratum.get(stratum, [])
        eligible = [p for p in paras if p['n_body'] >= 2]
        if len(eligible) < 5:
            continue

        first_vectors = []
        last_vectors = []
        for p in eligible:
            body = p['paragraph']['body_lines']
            first_vectors.append(_line_feature_vector(body[0]))
            last_vectors.append(_line_feature_vector(body[-1]))

        mean_first = _mean_vector(first_vectors)
        mean_last = _mean_vector(last_vectors)
        cos_sim = cosine_similarity(mean_first, mean_last) if mean_first and mean_last else 0.0

        t2_section_controlled[stratum] = {
            'cosine': cos_sim,
            'n_paragraphs': len(eligible),
        }
        print(f"  Recipe-only {stratum} (n={len(eligible)}): cosine = {cos_sim:.4f}")

    # Determine minimum viable body-line count
    # Arc operates if cosine < -0.3
    min_viable = None
    for stratum in ['MINIMAL', 'SHORT', 'LONG']:
        if stratum in per_stratum_cosine:
            cos = per_stratum_cosine[stratum]['cosine']
            n_body_range = STRATA[stratum]
            if cos < -0.3:
                min_viable = n_body_range[0]
                break

    if min_viable is None:
        # Check if LONG has it
        if 'LONG' in per_stratum_cosine and per_stratum_cosine['LONG']['cosine'] < -0.3:
            min_viable = 5
        else:
            min_viable = None  # Arc not detected at any scale

    print(f"\n  Minimum viable body-line count for arc: {min_viable}")

    results['T2_minimum_viable'] = {
        'per_stratum_cosine': {s: {'cosine': v['cosine'], 'n_paragraphs': v['n_paragraphs']}
                               for s, v in per_stratum_cosine.items()},
        'per_feature_first_vs_last': per_stratum_first_last_mw,
        'section_controlled': t2_section_controlled,
        'minimum_viable_body_lines': min_viable,
    }

    # ============================================================
    # T3: Kernel gradient in short paragraphs
    # ============================================================
    print("\n" + "=" * 60)
    print("[T3] Kernel Gradient in Short Paragraphs")
    print("=" * 60)

    t3_per_stratum = {}
    t3_section_controlled = {}

    for stratum in STRATUM_ORDER:
        paras = by_stratum.get(stratum, [])
        eligible = [p for p in paras if p['n_body'] >= 2]
        if not eligible:
            print(f"  {stratum}: no eligible paragraphs (need >=2 body lines)")
            continue

        # Per-paragraph Spearman rho of h_rate vs body line position
        per_para_rhos = []
        pooled_positions = []
        pooled_h_rates = []

        for p in eligible:
            body = p['paragraph']['body_lines']
            positions = []
            h_rates = []
            for pos, line in enumerate(body):
                tokens = line.get('tokens', [])
                if not tokens:
                    continue
                h_count = sum(1 for t in tokens for c in t.get('kernels', []) if c == 'h')
                h_rate = h_count / len(tokens)
                positions.append(float(pos))
                h_rates.append(h_rate)
                pooled_positions.append(float(pos))
                pooled_h_rates.append(h_rate)

            if len(positions) >= 3:
                rho_result = spearman_rho(positions, h_rates)
                per_para_rhos.append(rho_result['rho'])

        # Mean rho across paragraphs
        mean_rho = sum(per_para_rhos) / len(per_para_rhos) if per_para_rhos else 0.0

        # Pooled rho
        if len(pooled_positions) >= 5:
            pooled_result = spearman_rho(pooled_positions, pooled_h_rates)
        else:
            pooled_result = {'rho': 0.0, 'p': 1.0, 'n': len(pooled_positions)}

        t3_per_stratum[stratum] = {
            'mean_rho': mean_rho,
            'n_paragraphs_with_rho': len(per_para_rhos),
            'pooled_rho': pooled_result['rho'],
            'pooled_p': pooled_result['p'],
            'pooled_n': pooled_result['n'],
        }

        sig_marker = '*' if pooled_result['p'] < 0.05 else ''
        print(f"  {stratum} (n={len(eligible)}, n_rho={len(per_para_rhos)}): "
              f"mean_rho={mean_rho:.4f}, pooled_rho={pooled_result['rho']:.4f}, "
              f"pooled_p={pooled_result['p']:.4f}{sig_marker}")

    # Section-controlled: within Recipe
    print("\n  Section-controlled (Recipe only):")
    for stratum in STRATUM_ORDER:
        paras = recipe_by_stratum.get(stratum, [])
        eligible = [p for p in paras if p['n_body'] >= 2]
        if len(eligible) < 5:
            continue

        per_para_rhos = []
        pooled_positions = []
        pooled_h_rates = []

        for p in eligible:
            body = p['paragraph']['body_lines']
            positions = []
            h_rates = []
            for pos, line in enumerate(body):
                tokens = line.get('tokens', [])
                if not tokens:
                    continue
                h_count = sum(1 for t in tokens for c in t.get('kernels', []) if c == 'h')
                h_rate = h_count / len(tokens)
                positions.append(float(pos))
                h_rates.append(h_rate)
                pooled_positions.append(float(pos))
                pooled_h_rates.append(h_rate)

            if len(positions) >= 3:
                rho_result = spearman_rho(positions, h_rates)
                per_para_rhos.append(rho_result['rho'])

        mean_rho = sum(per_para_rhos) / len(per_para_rhos) if per_para_rhos else 0.0

        if len(pooled_positions) >= 5:
            pooled_result = spearman_rho(pooled_positions, pooled_h_rates)
        else:
            pooled_result = {'rho': 0.0, 'p': 1.0, 'n': len(pooled_positions)}

        t3_section_controlled[stratum] = {
            'mean_rho': mean_rho,
            'n_paragraphs_with_rho': len(per_para_rhos),
            'pooled_rho': pooled_result['rho'],
            'pooled_p': pooled_result['p'],
            'pooled_n': pooled_result['n'],
        }

        sig_marker = '*' if pooled_result['p'] < 0.05 else ''
        print(f"    Recipe {stratum} (n={len(eligible)}): "
              f"mean_rho={mean_rho:.4f}, pooled_rho={pooled_result['rho']:.4f}, "
              f"pooled_p={pooled_result['p']:.4f}{sig_marker}")

    results['T3_kernel_gradient'] = {
        'per_stratum': t3_per_stratum,
        'section_controlled': t3_section_controlled,
    }

    # ============================================================
    # T4: m-terminal and terminal opacity by stratum
    # ============================================================
    print("\n" + "=" * 60)
    print("[T4] m-terminal and Terminal Opacity by Stratum")
    print("=" * 60)

    t4_per_stratum = {}
    t4_kw_groups_m = []
    t4_kw_groups_opacity = []
    t4_strata_names = []

    for stratum in STRATUM_ORDER:
        paras = by_stratum.get(stratum, [])
        eligible = [p for p in paras if p['n_body'] >= 1]
        if not eligible:
            continue

        last_line_m_rates = []
        last_line_opacities = []

        for p in eligible:
            body = p['paragraph']['body_lines']
            last_line = body[-1]
            tokens = last_line.get('tokens', [])
            if not tokens:
                continue

            m_rate = sum(1 for t in tokens if t.get('term') == 'm') / len(tokens)
            last_line_m_rates.append(m_rate)

            opacity_sum = sum(_OPACITY_NUMERIC.get(t.get('terminal_opacity', 'BARE'), 0.0)
                              for t in tokens)
            mean_op = opacity_sum / len(tokens)
            last_line_opacities.append(mean_op)

        if last_line_m_rates:
            mean_m = sum(last_line_m_rates) / len(last_line_m_rates)
            mean_opacity = sum(last_line_opacities) / len(last_line_opacities)

            t4_per_stratum[stratum] = {
                'last_line_m_terminal_rate': mean_m,
                'last_line_mean_opacity': mean_opacity,
                'n': len(last_line_m_rates),
            }

            t4_kw_groups_m.append(last_line_m_rates)
            t4_kw_groups_opacity.append(last_line_opacities)
            t4_strata_names.append(stratum)

            print(f"  {stratum} (n={len(last_line_m_rates)}): "
                  f"m_terminal={mean_m:.4f}, opacity={mean_opacity:.4f}")

    # Kruskal-Wallis across strata
    from phases.SHORT_PARAGRAPH_ARCHITECTURE.scripts.shared_625 import kruskal_wallis

    kw_m = kruskal_wallis(t4_kw_groups_m)
    kw_opacity = kruskal_wallis(t4_kw_groups_opacity)
    print(f"\n  Kruskal-Wallis m-terminal: H={kw_m['H']:.3f}, p={kw_m['p']:.6f}")
    print(f"  Kruskal-Wallis opacity: H={kw_opacity['H']:.3f}, p={kw_opacity['p']:.6f}")

    # Pairwise: MINIMAL vs LONG
    t4_pairwise = {}
    if 'MINIMAL' in t4_per_stratum and 'LONG' in t4_per_stratum:
        # Get the actual value arrays for MINIMAL and LONG
        minimal_idx = t4_strata_names.index('MINIMAL') if 'MINIMAL' in t4_strata_names else None
        long_idx = t4_strata_names.index('LONG') if 'LONG' in t4_strata_names else None

        if minimal_idx is not None and long_idx is not None:
            mw_m = mann_whitney_u(t4_kw_groups_m[minimal_idx], t4_kw_groups_m[long_idx])
            mw_op = mann_whitney_u(t4_kw_groups_opacity[minimal_idx], t4_kw_groups_opacity[long_idx])
            d_m = cohens_d(t4_kw_groups_m[minimal_idx], t4_kw_groups_m[long_idx])
            d_op = cohens_d(t4_kw_groups_opacity[minimal_idx], t4_kw_groups_opacity[long_idx])

            t4_pairwise['MINIMAL_vs_LONG'] = {
                'm_terminal': {'U': mw_m['U'], 'z': mw_m['z'], 'p': mw_m['p'], 'd': d_m},
                'opacity': {'U': mw_op['U'], 'z': mw_op['z'], 'p': mw_op['p'], 'd': d_op},
            }
            print(f"\n  MINIMAL vs LONG m-terminal: z={mw_m['z']:.3f}, p={mw_m['p']:.6f}, d={d_m:.3f}")
            print(f"  MINIMAL vs LONG opacity: z={mw_op['z']:.3f}, p={mw_op['p']:.6f}, d={d_op:.3f}")

    # Section-controlled T4: within Recipe
    print("\n  Section-controlled (Recipe only):")
    t4_section_controlled = {}
    t4_recipe_kw_m = []
    t4_recipe_kw_op = []
    t4_recipe_strata = []

    for stratum in STRATUM_ORDER:
        paras = recipe_by_stratum.get(stratum, [])
        eligible = [p for p in paras if p['n_body'] >= 1]
        if len(eligible) < 5:
            continue

        last_line_m_rates = []
        last_line_opacities = []

        for p in eligible:
            body = p['paragraph']['body_lines']
            last_line = body[-1]
            tokens = last_line.get('tokens', [])
            if not tokens:
                continue
            m_rate = sum(1 for t in tokens if t.get('term') == 'm') / len(tokens)
            last_line_m_rates.append(m_rate)
            opacity_sum = sum(_OPACITY_NUMERIC.get(t.get('terminal_opacity', 'BARE'), 0.0)
                              for t in tokens)
            last_line_opacities.append(opacity_sum / len(tokens))

        if last_line_m_rates:
            mean_m = sum(last_line_m_rates) / len(last_line_m_rates)
            mean_op = sum(last_line_opacities) / len(last_line_opacities)

            t4_section_controlled[stratum] = {
                'last_line_m_terminal_rate': mean_m,
                'last_line_mean_opacity': mean_op,
                'n': len(last_line_m_rates),
            }
            t4_recipe_kw_m.append(last_line_m_rates)
            t4_recipe_kw_op.append(last_line_opacities)
            t4_recipe_strata.append(stratum)

            print(f"    Recipe {stratum} (n={len(last_line_m_rates)}): "
                  f"m_terminal={mean_m:.4f}, opacity={mean_op:.4f}")

    t4_recipe_kw = {}
    if len(t4_recipe_kw_m) >= 2:
        kw_m_r = kruskal_wallis(t4_recipe_kw_m)
        kw_op_r = kruskal_wallis(t4_recipe_kw_op)
        t4_recipe_kw = {
            'm_terminal': {'H': kw_m_r['H'], 'p': kw_m_r['p']},
            'opacity': {'H': kw_op_r['H'], 'p': kw_op_r['p']},
        }
        print(f"    Recipe KW m-terminal: H={kw_m_r['H']:.3f}, p={kw_m_r['p']:.6f}")
        print(f"    Recipe KW opacity: H={kw_op_r['H']:.3f}, p={kw_op_r['p']:.6f}")

    results['T4_m_terminal'] = {
        'per_stratum': t4_per_stratum,
        'kruskal_wallis': {
            'm_terminal': {'H': kw_m['H'], 'df': kw_m['df'], 'p': kw_m['p']},
            'opacity': {'H': kw_opacity['H'], 'df': kw_opacity['df'], 'p': kw_opacity['p']},
        },
        'pairwise': t4_pairwise,
        'section_controlled': {
            'per_stratum': t4_section_controlled,
            'kruskal_wallis': t4_recipe_kw,
        },
    }

    # ============================================================
    # T5: Header-body coupling by stratum
    # ============================================================
    print("\n" + "=" * 60)
    print("[T5] Header-Body Coupling by Stratum")
    print("=" * 60)

    HEADER_FEATURE_NAMES = ['k_frac', 'h_frac', 'e_frac', 'o_frac', 'a_frac', 'ht_rate', 'n_tokens']

    t5_per_stratum = {}
    t5_section_controlled = {}

    for stratum in STRATUM_ORDER:
        paras = by_stratum.get(stratum, [])
        # Need paragraphs with both header AND body
        eligible = [p for p in paras if p['n_body'] >= 1]
        if len(eligible) < 10:
            print(f"  {stratum}: insufficient paragraphs (n={len(eligible)}, need >=10)")
            continue

        header_vectors = []
        body_vectors = []

        for p in eligible:
            hdr_result = extract_header_features(p['paragraph'])
            if hdr_result[0] is None:
                continue

            hdr_vec = hdr_result[0]  # 7-dim

            # Body features (11-dim)
            body_feats = _extract_body_features(p['paragraph'])
            body_vec = [body_feats[fn] for fn in FEATURE_NAMES]

            header_vectors.append(hdr_vec)
            body_vectors.append(body_vec)

        if len(header_vectors) < 10:
            print(f"  {stratum}: insufficient valid header-body pairs (n={len(header_vectors)})")
            continue

        # Compute header x body Spearman correlations
        n_hdr = len(HEADER_FEATURE_NAMES)
        n_body = len(FEATURE_NAMES)
        correlation_matrix = {}
        abs_rhos = []

        for hi in range(n_hdr):
            hdr_name = HEADER_FEATURE_NAMES[hi]
            hdr_vals = [hv[hi] for hv in header_vectors]

            for bi in range(n_body):
                body_name = FEATURE_NAMES[bi]
                body_vals = [bv[bi] for bv in body_vectors]

                rho_result = spearman_rho(hdr_vals, body_vals)
                key = f"{hdr_name}_x_{body_name}"
                correlation_matrix[key] = {
                    'rho': rho_result['rho'],
                    'p': rho_result['p'],
                }
                abs_rhos.append(abs(rho_result['rho']))

        mean_abs_rho = sum(abs_rhos) / len(abs_rhos) if abs_rhos else 0.0

        # Count significant correlations (p < 0.05)
        n_sig = sum(1 for key, val in correlation_matrix.items() if val['p'] < 0.05)

        t5_per_stratum[stratum] = {
            'mean_abs_rho': mean_abs_rho,
            'n_significant_pairs': n_sig,
            'total_pairs': len(abs_rhos),
            'n_paragraphs': len(header_vectors),
            'correlation_matrix': correlation_matrix,
        }

        print(f"  {stratum} (n={len(header_vectors)}): "
              f"mean|rho|={mean_abs_rho:.4f}, sig_pairs={n_sig}/{len(abs_rhos)}")

    # Section-controlled: within Recipe
    print("\n  Section-controlled (Recipe only):")
    for stratum in STRATUM_ORDER:
        paras = recipe_by_stratum.get(stratum, [])
        eligible = [p for p in paras if p['n_body'] >= 1]
        if len(eligible) < 10:
            continue

        header_vectors = []
        body_vectors = []

        for p in eligible:
            hdr_result = extract_header_features(p['paragraph'])
            if hdr_result[0] is None:
                continue

            hdr_vec = hdr_result[0]
            body_feats = _extract_body_features(p['paragraph'])
            body_vec = [body_feats[fn] for fn in FEATURE_NAMES]

            header_vectors.append(hdr_vec)
            body_vectors.append(body_vec)

        if len(header_vectors) < 10:
            continue

        abs_rhos = []
        n_hdr = len(HEADER_FEATURE_NAMES)
        n_body_feat = len(FEATURE_NAMES)

        for hi in range(n_hdr):
            hdr_vals = [hv[hi] for hv in header_vectors]
            for bi in range(n_body_feat):
                body_vals = [bv[bi] for bv in body_vectors]
                rho_result = spearman_rho(hdr_vals, body_vals)
                abs_rhos.append(abs(rho_result['rho']))

        mean_abs_rho = sum(abs_rhos) / len(abs_rhos) if abs_rhos else 0.0
        t5_section_controlled[stratum] = {
            'mean_abs_rho': mean_abs_rho,
            'n_paragraphs': len(header_vectors),
        }

        print(f"    Recipe {stratum} (n={len(header_vectors)}): mean|rho|={mean_abs_rho:.4f}")

    # Test: does coupling increase for shorter paragraphs?
    coupling_values = [(s, t5_per_stratum[s]['mean_abs_rho'])
                       for s in STRATUM_ORDER if s in t5_per_stratum]
    coupling_increases = False
    if len(coupling_values) >= 2:
        # Check if shorter strata have higher mean|rho|
        short_strata = [v for s, v in coupling_values if s in ('MINIMAL', 'SHORT')]
        long_strata = [v for s, v in coupling_values if s == 'LONG']
        if short_strata and long_strata:
            mean_short_coupling = sum(short_strata) / len(short_strata)
            mean_long_coupling = sum(long_strata) / len(long_strata)
            coupling_increases = mean_short_coupling > mean_long_coupling
            print(f"\n  Coupling in short strata: {mean_short_coupling:.4f}")
            print(f"  Coupling in LONG: {mean_long_coupling:.4f}")
            print(f"  Coupling increases with shortness: {coupling_increases}")

    # Strip full correlation matrices for compactness (keep top-level summaries)
    t5_per_stratum_summary = {}
    for s, data in t5_per_stratum.items():
        t5_per_stratum_summary[s] = {
            'mean_abs_rho': data['mean_abs_rho'],
            'n_significant_pairs': data['n_significant_pairs'],
            'total_pairs': data['total_pairs'],
            'n_paragraphs': data['n_paragraphs'],
        }

    # Find top 5 most correlated pairs per stratum (for insight)
    t5_top_pairs = {}
    for s, data in t5_per_stratum.items():
        cmat = data['correlation_matrix']
        sorted_pairs = sorted(cmat.items(), key=lambda x: abs(x[1]['rho']), reverse=True)
        t5_top_pairs[s] = [
            {'pair': p, 'rho': v['rho'], 'p': v['p']}
            for p, v in sorted_pairs[:5]
        ]

    results['T5_header_body_coupling'] = {
        'per_stratum_mean_abs_rho': {s: d['mean_abs_rho'] for s, d in t5_per_stratum.items()},
        'per_stratum_detail': t5_per_stratum_summary,
        'top_correlated_pairs': t5_top_pairs,
        'coupling_increases_with_shortness': coupling_increases,
        'section_controlled': t5_section_controlled,
    }

    # ============================================================
    # SYNTHESIS
    # ============================================================
    print("\n" + "=" * 60)
    print("SYNTHESIS")
    print("=" * 60)

    print(f"\n  T1 (Subsample Null): {t1_verdict}")
    print(f"    Position-matched MINIMAL: {pm_minimal_npass}/11 pass (pooled)")
    print(f"    Position-matched SHORT: {pm_short_npass}/11 pass (pooled)")
    print(f"    Random-subsample MINIMAL: {rand_minimal_npass}/11 pass (pooled)")
    print(f"    Random-subsample SHORT: {rand_short_npass}/11 pass (pooled)")
    if sm_pm_minimal_comp:
        print(f"    Section-matched pos-matched MINIMAL: {sm_pm_minimal_npass}/11 pass")
    if sm_pm_short_comp:
        print(f"    Section-matched pos-matched SHORT: {sm_pm_short_npass}/11 pass")

    print(f"\n  T2 (Minimum Viable Paragraph):")
    for s, v in per_stratum_cosine.items():
        label = 'ARC PRESENT' if v['cosine'] < -0.3 else 'no arc'
        print(f"    {s}: cosine={v['cosine']:.4f} [{label}]")
    print(f"    Minimum viable body lines: {min_viable}")

    print(f"\n  T3 (Kernel Gradient):")
    for s, v in t3_per_stratum.items():
        sig = 'SIGNIFICANT' if v['pooled_p'] < 0.05 else 'not significant'
        print(f"    {s}: pooled_rho={v['pooled_rho']:.4f}, p={v['pooled_p']:.4f} [{sig}]")

    print(f"\n  T4 (m-terminal):")
    for s, v in t4_per_stratum.items():
        print(f"    {s}: m_terminal={v['last_line_m_terminal_rate']:.4f}, "
              f"opacity={v['last_line_mean_opacity']:.4f}")
    print(f"    KW m-terminal: p={kw_m['p']:.6f}")
    print(f"    KW opacity: p={kw_opacity['p']:.6f}")

    print(f"\n  T5 (Header-Body Coupling):")
    for s in STRATUM_ORDER:
        if s in t5_per_stratum:
            v = t5_per_stratum[s]
            print(f"    {s}: mean|rho|={v['mean_abs_rho']:.4f} "
                  f"(sig_pairs={v['n_significant_pairs']}/{v['total_pairs']})")
    print(f"    Coupling increases with shortness: {coupling_increases}")

    # Overall interpretation
    print(f"\n  OVERALL:")
    if t1_verdict == 'TRUNCATED_FROM_START':
        print("    Short paragraphs resemble the BEGINNINGS of long paragraphs.")
        print("    They are likely truncated programs that stop early.")
    elif t1_verdict == 'FULLY_TRUNCATED':
        print("    Short paragraphs resemble arbitrary subsets of long paragraphs.")
        print("    They use the same grammar but at reduced scale.")
    else:
        print("    Short paragraphs are STRUCTURALLY DISTINCT from long paragraphs.")
        print("    They are not truncated versions but different operational objects.")

    if min_viable is not None:
        print(f"    The line-level arc (spec-work-closure) becomes visible at {min_viable}+ body lines.")
    else:
        print("    The line-level arc was not detected even in LONG paragraphs (unexpected).")

    # ---- Write output ----
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'architecture_scaling.json'
    with open(out_path, 'w') as f:
        json.dump(round_floats(results), f, indent=2)
    print(f"\n  Output written to: {out_path}")
    print("  Done.")


if __name__ == '__main__':
    main()
