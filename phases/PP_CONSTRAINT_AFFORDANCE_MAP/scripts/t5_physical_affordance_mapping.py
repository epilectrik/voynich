#!/usr/bin/env python3
"""
T5: Physical Affordance Class Mapping
PP_CONSTRAINT_AFFORDANCE_MAP phase (Tier 4)

Attempt to label geometric regions with distillation process parameter
families. Explicitly speculative — hypothesis generation, not confirmation.

Uses T1-T4 results to build interpretive profiles, then maps them to
physical affordance classes anchored to distillation.
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from sklearn.mixture import GaussianMixture

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DISC_RESULTS = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'
K_RESIDUAL = 99

QO_INITIALS = set('ktp')
CHSH_INITIALS = set('eo')

# Physical affordance classes (distillation anchor)
AFFORDANCE_FAMILIES = {
    'THERMAL': {
        'HEAT_APPLICATION': 'Direct energy input (fire degree, heating rate)',
        'THERMAL_STABILITY': 'Temperature maintenance within narrow band',
        'COOLING_CONTROL': 'Rate and method of temperature decrease',
    },
    'PHASE': {
        'PHASE_TRANSITION': 'Liquid-vapor boundary operations',
        'CONDENSATION': 'Vapor-to-liquid return management',
        'BOILING_REGIME': 'Maintaining correct boiling behavior',
    },
    'FLOW': {
        'VAPOR_TRANSPORT': 'Movement of volatile fractions',
        'LIQUID_RETURN': 'Reflux and liquid circulation',
        'SEPARATION': 'Component separation efficiency',
    },
    'RECOVERY': {
        'OVERSHOOT_RECOVERY': 'Returning from excessive conditions',
        'CONTAMINATION_MANAGEMENT': 'Handling unwanted intrusions',
        'APPARATUS_BASELINE': 'System reset and preparation',
    },
    'MONITORING': {
        'QUALITY_ASSESSMENT': 'Purity and output quality checking',
        'RATE_TRACKING': 'Speed of process progression',
        'COMPLETION_DETECTION': 'Determining process endpoints',
    },
}


def reconstruct_middle_list():
    tx = Transcript()
    morph = Morphology()
    all_middles_set = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles_set.add(m.middle)
    return sorted(all_middles_set)


def build_residual_embedding(compat_matrix):
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    res_evals = eigenvalues[1:K_RESIDUAL + 1]
    res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
    scaling = np.sqrt(np.maximum(res_evals, 0))
    return res_evecs * scaling[np.newaxis, :], eigenvalues


def build_cluster_profiles(all_middles, mid_to_idx, labels, embedding, compat_matrix):
    """Build comprehensive profiles for each cluster."""
    tx = Transcript()
    morph = Morphology()

    # Gather frequency data
    a_counts = Counter()
    a_folio_sets = defaultdict(set)
    a_prefix_sets = defaultdict(set)
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            a_counts[m.middle] += 1
            a_folio_sets[m.middle].add(token.folio)
            if m.prefix:
                a_prefix_sets[m.middle].add(m.prefix)

    b_counts = Counter()
    b_section_counts = defaultdict(lambda: Counter())
    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            b_counts[m.middle] += 1
            b_section_counts[m.middle][token.section] += 1

    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('A')

    cluster_ids = sorted(set(labels))
    profiles = {}

    for c in cluster_ids:
        members = [i for i in range(len(all_middles)) if labels[i] == c]
        mids = [all_middles[i] for i in members]
        n = len(mids)

        # Morphological
        mean_len = np.mean([len(m) for m in mids])
        pct_qo = sum(1 for m in mids if m[0] in QO_INITIALS) / n
        pct_chsh = sum(1 for m in mids if m[0] in CHSH_INITIALS) / n
        pct_k = sum(1 for m in mids if 'k' in m) / n
        pct_e = sum(1 for m in mids if 'e' in m) / n
        pct_h = sum(1 for m in mids if 'h' in m) / n
        pct_compound = sum(1 for m in mids if mid_analyzer.is_compound(m)) / n

        # Frequency
        mean_freq = np.mean([a_counts.get(m, 0) for m in mids])
        median_freq = np.median([a_counts.get(m, 0) for m in mids])
        mean_folios = np.mean([len(a_folio_sets.get(m, set())) for m in mids])
        pct_in_b = sum(1 for m in mids if b_counts.get(m, 0) > 0) / n

        # Section
        section_totals = Counter()
        for m in mids:
            if m in b_section_counts:
                for sec, cnt in b_section_counts[m].items():
                    section_totals[sec] += cnt

        # Geometric
        mean_depth = np.mean([np.linalg.norm(embedding[i]) for i in members])

        # Internal compatibility (within-cluster)
        n_compat = 0
        n_pairs = 0
        for ii in range(len(members)):
            for jj in range(ii + 1, len(members)):
                n_pairs += 1
                if compat_matrix[members[ii], members[jj]] > 0:
                    n_compat += 1
        internal_compat = n_compat / n_pairs if n_pairs > 0 else 0

        # PREFIX diversity
        all_prefixes = set()
        for m in mids:
            all_prefixes.update(a_prefix_sets.get(m, set()))
        prefix_diversity = len(all_prefixes)

        # Top MIDDLEs (most frequent)
        top_mids = sorted(mids, key=lambda m: a_counts.get(m, 0), reverse=True)[:10]
        top_examples = [(m, a_counts.get(m, 0)) for m in top_mids]

        profiles[c] = {
            'n': n,
            'mean_length': float(mean_len),
            'pct_qo': float(pct_qo),
            'pct_chsh': float(pct_chsh),
            'pct_k': float(pct_k),
            'pct_e': float(pct_e),
            'pct_h': float(pct_h),
            'pct_compound': float(pct_compound),
            'mean_freq': float(mean_freq),
            'median_freq': float(median_freq),
            'mean_folios': float(mean_folios),
            'pct_in_b': float(pct_in_b),
            'section_totals': dict(section_totals.most_common()),
            'mean_depth': float(mean_depth),
            'internal_compat': float(internal_compat),
            'prefix_diversity': prefix_diversity,
            'top_examples': top_examples,
        }

    return profiles


def assign_affordance(profile, cluster_id):
    """Rule-based affordance mapping anchored to constraints."""
    assignments = []
    confidence_score = 0

    # Hub cluster (high freq, short, deep, universal compatibility)
    if profile['mean_freq'] > 100 and profile['mean_length'] < 2.5:
        assignments.append({
            'family': 'THERMAL',
            'class': 'APPARATUS_BASELINE',
            'reason': 'Universal connectors: high frequency, short, compatible with everything',
            'anchor': 'C476 (universal connector), C986 (hub = frequency)',
        })
        confidence_score += 3
        # Also monitoring — universal parameters are tracked everywhere
        assignments.append({
            'family': 'MONITORING',
            'class': 'RATE_TRACKING',
            'reason': 'Universal presence suggests monitoring/tracking function',
            'anchor': 'C475 (compatibility baseline)',
        })
        confidence_score += 1

    # Rare compound periphery (hapax, long, shallow)
    if profile['median_freq'] <= 1 and profile['pct_compound'] > 0.80:
        assignments.append({
            'family': 'RECOVERY',
            'class': 'APPARATUS_BASELINE',
            'reason': 'Hapax compounds: one-time specifications, setup/preparation',
            'anchor': 'C618 (unique MIDDLE identity), C935 (compound = specification)',
        })
        confidence_score += 2

    # k-enriched + QO-biased → heating/energy pathway
    if profile['pct_k'] > 0.25 and profile['pct_qo'] > 0.15:
        assignments.append({
            'family': 'THERMAL',
            'class': 'HEAT_APPLICATION',
            'reason': f"k-enriched ({profile['pct_k']:.0%}), QO-biased ({profile['pct_qo']:.0%})",
            'anchor': 'C647 (QO = k-rich), C911 (k = energy modulator)',
        })
        confidence_score += 2

    # e-enriched + CHSH-biased → stability/cooling
    if profile['pct_e'] > 0.35 and profile['pct_chsh'] > 0.40:
        assignments.append({
            'family': 'THERMAL',
            'class': 'THERMAL_STABILITY',
            'reason': f"e-enriched ({profile['pct_e']:.0%}), CHSH-biased ({profile['pct_chsh']:.0%})",
            'anchor': 'C647 (CHSH = e-rich), C992 (e = compatibility kernel)',
        })
        confidence_score += 2

    # h-enriched → monitoring/intervention
    if profile['pct_h'] > 0.35:
        assignments.append({
            'family': 'MONITORING',
            'class': 'QUALITY_ASSESSMENT',
            'reason': f"h-enriched ({profile['pct_h']:.0%})",
            'anchor': 'C908-C910 (h = monitoring)',
        })
        confidence_score += 1

    # Deep in manifold + moderate frequency → phase-critical operations
    if profile['mean_depth'] > 1.0 and profile['mean_freq'] > 5:
        assignments.append({
            'family': 'PHASE',
            'class': 'PHASE_TRANSITION',
            'reason': f"Deep (depth={profile['mean_depth']:.2f}), moderate freq ({profile['mean_freq']:.0f})",
            'anchor': 'C991 (depth = constraint tension)',
        })
        confidence_score += 2

    # Shallow + low internal compat → flow/transport (loose coupling)
    if profile['mean_depth'] < 0.6 and profile['internal_compat'] < 0.01:
        assignments.append({
            'family': 'FLOW',
            'class': 'VAPOR_TRANSPORT',
            'reason': f"Shallow (depth={profile['mean_depth']:.2f}), low internal compat ({profile['internal_compat']:.3f})",
            'anchor': 'C991 (shallow = low constraint), C987 (continuous manifold)',
        })
        confidence_score += 1

    # High B presence + section concentration → process-specific constraints
    if profile['pct_in_b'] > 0.90:
        dominant_sec = max(profile['section_totals'], key=profile['section_totals'].get) \
            if profile['section_totals'] else 'NONE'
        if dominant_sec == 'S':
            assignments.append({
                'family': 'PHASE',
                'class': 'BOILING_REGIME',
                'reason': f"S-section dominant, high B presence ({profile['pct_in_b']:.0%})",
                'anchor': 'C909 (section-MIDDLE alignment)',
            })
            confidence_score += 1
        elif dominant_sec == 'B':
            assignments.append({
                'family': 'FLOW',
                'class': 'LIQUID_RETURN',
                'reason': f"B-section dominant (biological/bathing), high B presence",
                'anchor': 'C909 (section-MIDDLE alignment)',
            })
            confidence_score += 1

    # Assign confidence level
    if confidence_score >= 4:
        confidence = 'HIGH'
    elif confidence_score >= 2:
        confidence = 'MEDIUM'
    elif confidence_score >= 1:
        confidence = 'LOW'
    else:
        confidence = 'SPECULATIVE'
        assignments.append({
            'family': 'UNKNOWN',
            'class': 'UNCLASSIFIED',
            'reason': 'No strong structural anchors match known affordance patterns',
            'anchor': 'None',
        })

    return assignments, confidence, confidence_score


def main():
    print("=" * 60)
    print("T5: Physical Affordance Class Mapping")
    print("=" * 60)

    # Load
    print("\n[1] Loading data...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    all_middles = reconstruct_middle_list()
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    embedding, eigenvalues = build_residual_embedding(compat_matrix)

    # Cluster
    print("\n[2] Clustering (GMM k=5)...")
    gmm = GaussianMixture(n_components=5, random_state=42, n_init=3,
                           covariance_type='diag', max_iter=300)
    labels = gmm.fit_predict(embedding)

    # Build profiles
    print("\n[3] Building cluster profiles...")
    profiles = build_cluster_profiles(all_middles, mid_to_idx, labels, embedding, compat_matrix)

    # Print affordance class catalog
    print("\n[4] Affordance class catalog (distillation anchor):")
    for family, classes in AFFORDANCE_FAMILIES.items():
        print(f"\n  {family}:")
        for cls, desc in classes.items():
            print(f"    {cls}: {desc}")

    # Assign affordances
    print("\n[5] Mapping clusters to affordance classes...")
    cluster_affordances = {}
    for c in sorted(profiles.keys()):
        p = profiles[c]
        assignments, confidence, score = assign_affordance(p, c)
        cluster_affordances[c] = {
            'assignments': assignments,
            'confidence': confidence,
            'score': score,
        }

        print(f"\n  Cluster {c} (n={p['n']}, depth={p['mean_depth']:.2f}, "
              f"freq={p['mean_freq']:.0f}):")
        print(f"    Top examples: {', '.join(m for m, _ in p['top_examples'][:5])}")
        print(f"    Confidence: {confidence} (score={score})")
        for a in assignments:
            print(f"    -> {a['family']}/{a['class']}")
            print(f"       Reason: {a['reason']}")
            print(f"       Anchor: {a['anchor']}")

    # Check exclusion coherence
    print("\n[6] Exclusion coherence check...")
    # Load T4 exclusion pairs
    t4_path = RESULTS_DIR / 't4_incompatibility_topology.json'
    if t4_path.exists():
        with open(t4_path) as f:
            t4 = json.load(f)
        exclusion_edges = t4.get('exclusion_edges', [])

        n_explained = 0
        n_total_excl = len(exclusion_edges)
        explanations = []

        for edge in exclusion_edges:
            pair = edge['pair']
            ci, cj = int(pair.split('-')[0]), int(pair.split('-')[1])
            aff_i = cluster_affordances.get(ci, {}).get('assignments', [])
            aff_j = cluster_affordances.get(cj, {}).get('assignments', [])

            families_i = set(a['family'] for a in aff_i)
            families_j = set(a['family'] for a in aff_j)
            classes_i = set(a['class'] for a in aff_i)
            classes_j = set(a['class'] for a in aff_j)

            # Check if exclusion makes physical sense
            explanation = None

            # Different families → natural exclusion
            if families_i and families_j and not families_i.intersection(families_j):
                explanation = f"Different families: {families_i} vs {families_j}"
                n_explained += 1
            # Same family but opposing classes
            elif ('HEAT_APPLICATION' in classes_i and 'COOLING_CONTROL' in classes_j) or \
                 ('COOLING_CONTROL' in classes_i and 'HEAT_APPLICATION' in classes_j):
                explanation = "Opposing thermal operations"
                n_explained += 1
            # Rare periphery vs working vocabulary
            elif ('APPARATUS_BASELINE' in classes_i and 'APPARATUS_BASELINE' not in classes_j) or \
                 ('APPARATUS_BASELINE' not in classes_i and 'APPARATUS_BASELINE' in classes_j):
                explanation = "Setup/specification vs active operation"
                n_explained += 1
            else:
                explanation = "No clear physical interpretation"

            explanations.append({
                'pair': pair,
                'explanation': explanation,
                'families_i': list(families_i),
                'families_j': list(families_j),
            })
            print(f"    C{ci}-C{cj}: {explanation}")

        explanation_rate = n_explained / n_total_excl if n_total_excl > 0 else 0
        print(f"\n  Exclusion explanation rate: {n_explained}/{n_total_excl} "
              f"({explanation_rate:.0%})")
    else:
        exclusion_edges = []
        explanation_rate = 0
        explanations = []
        print("  T4 results not found, skipping exclusion check")

    # Coverage analysis
    print("\n[7] Coverage analysis...")
    total_middles = len(all_middles)
    confidence_counts = Counter(v['confidence'] for v in cluster_affordances.values())
    coverage_by_confidence = {}
    for conf_level in ['HIGH', 'MEDIUM', 'LOW', 'SPECULATIVE']:
        clusters_at_level = [c for c, v in cluster_affordances.items()
                             if v['confidence'] == conf_level]
        n_mids = sum(profiles[c]['n'] for c in clusters_at_level)
        coverage_by_confidence[conf_level] = {
            'n_clusters': len(clusters_at_level),
            'n_middles': n_mids,
            'pct': float(n_mids / total_middles),
        }
        print(f"  {conf_level}: {len(clusters_at_level)} clusters, "
              f"{n_mids} MIDDLEs ({n_mids/total_middles:.0%})")

    med_plus_coverage = sum(v['n_middles'] for k, v in coverage_by_confidence.items()
                            if k in ('HIGH', 'MEDIUM'))
    med_plus_pct = med_plus_coverage / total_middles

    # Affordance family distribution
    print("\n[8] Affordance family distribution across MIDDLEs...")
    family_coverage = Counter()
    for c, aff_info in cluster_affordances.items():
        n_mids = profiles[c]['n']
        for a in aff_info['assignments']:
            family_coverage[a['family']] += n_mids

    for family, count in family_coverage.most_common():
        print(f"  {family}: {count} MIDDLEs ({count/total_middles:.0%})")

    # Verdict
    print("\n" + "=" * 60)

    if med_plus_pct >= 0.50 and explanation_rate >= 0.40:
        verdict = "COHERENT_MAPPING"
        explanation_text = (
            f"{med_plus_pct:.0%} coverage at MEDIUM+ confidence, "
            f"{explanation_rate:.0%} exclusion pairs explained. "
            f"The discrimination space admits a coherent distillation-anchored interpretation."
        )
    elif med_plus_pct >= 0.30:
        verdict = "PARTIAL_MAPPING"
        explanation_text = (
            f"{med_plus_pct:.0%} coverage at MEDIUM+ confidence. "
            f"Some regions map to physical affordance classes, others resist labeling."
        )
    else:
        verdict = "INCOHERENT"
        explanation_text = (
            f"Only {med_plus_pct:.0%} coverage at MEDIUM+ confidence. "
            f"The discrimination space does not decompose into recognizable physical families."
        )

    print(f"VERDICT: {verdict}")
    print(f"  {explanation_text}")

    results = {
        'test': 'T5_physical_affordance_mapping',
        'n_middles': total_middles,
        'n_clusters': 5,
        'cluster_affordances': {
            str(c): {
                'n': profiles[c]['n'],
                'confidence': v['confidence'],
                'score': v['score'],
                'assignments': v['assignments'],
                'top_examples': profiles[c]['top_examples'][:5],
            }
            for c, v in cluster_affordances.items()
        },
        'coverage': coverage_by_confidence,
        'med_plus_coverage_pct': float(med_plus_pct),
        'exclusion_explanations': explanations,
        'exclusion_explanation_rate': float(explanation_rate),
        'family_distribution': dict(family_coverage.most_common()),
        'verdict': verdict,
        'explanation': explanation_text,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't5_physical_affordance_mapping.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't5_physical_affordance_mapping.json'}")


if __name__ == '__main__':
    main()
