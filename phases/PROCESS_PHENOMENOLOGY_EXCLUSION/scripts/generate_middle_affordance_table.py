#!/usr/bin/env python3
"""
Generate MIDDLE affordance lookup table.

Produces data/middle_affordance_table.json with per-MIDDLE:
  - GMM cluster assignment
  - Primary affordance family
  - Confidence tier
  - Radial depth (residual norm)
  - Compatibility degree

Based on PP_CONSTRAINT_AFFORDANCE_MAP T2 (clusters) and T5 (affordance labels).
Tier 4 speculative annotations — not resolved semantic assignments.
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

DISC_RESULTS = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'
PP_RESULTS = Path(__file__).resolve().parents[2] / 'PP_CONSTRAINT_AFFORDANCE_MAP' / 'results'
OUTPUT_DIR = Path(__file__).resolve().parents[3] / 'data'
K_RESIDUAL = 99


def reconstruct_middle_list():
    tx = Transcript()
    morph = Morphology()
    all_middles = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles.add(m.middle)
    return sorted(all_middles)


def build_residual_embedding(compat_matrix):
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    res_evals = eigenvalues[1:K_RESIDUAL + 1]
    res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
    scaling = np.sqrt(np.maximum(res_evals, 0))
    return res_evecs * scaling[np.newaxis, :], eigenvalues


def main():
    print("=" * 70)
    print("GENERATING MIDDLE AFFORDANCE TABLE")
    print("=" * 70)

    # ---- Reconstruct MIDDLE list (must match T1 ordering) ----
    middles = reconstruct_middle_list()
    n = len(middles)
    mid_to_idx = {m: i for i, m in enumerate(middles)}
    print(f"MIDDLEs: {n}")

    # ---- Load compatibility matrix and build embedding ----
    compat_path = DISC_RESULTS / 't1_compat_matrix.npy'
    compat = np.load(compat_path)
    print(f"Compatibility matrix: {compat.shape}")

    embedding, eigenvalues = build_residual_embedding(compat)
    print(f"Residual embedding: {embedding.shape}")

    # ---- Compute per-MIDDLE properties ----
    residual_norms = np.linalg.norm(embedding, axis=1)
    compat_degrees = compat.sum(axis=1)  # number of compatible partners

    # ---- GMM clustering (reproduce T2's k=5) ----
    from sklearn.mixture import GaussianMixture

    # Must match T2 parameters exactly for reproducible clusters
    gmm = GaussianMixture(n_components=5, covariance_type='diag',
                          n_init=3, max_iter=300, random_state=42)
    labels = gmm.fit_predict(embedding)
    print(f"GMM clusters: {np.bincount(labels)}")

    # ---- Map clusters to affordance families ----
    # From PP_CONSTRAINT_AFFORDANCE_MAP T5 results
    # We need to identify clusters by their properties (size + characteristics)
    # since GMM label ordering may differ between runs

    cluster_profiles = {}
    for c in range(5):
        mask = labels == c
        cluster_profiles[c] = {
            'size': int(mask.sum()),
            'mean_depth': float(residual_norms[mask].mean()),
            'mean_degree': float(compat_degrees[mask].mean()),
            'mean_freq': 0,  # will compute below
        }

    # Get token frequencies per MIDDLE
    tx = Transcript()
    morph = Morphology()
    mid_freq = {}
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            mid_freq[m.middle] = mid_freq.get(m.middle, 0) + 1

    for c in range(5):
        mask = labels == c
        freqs = [mid_freq.get(middles[i], 0) for i in range(n) if mask[i]]
        cluster_profiles[c]['mean_freq'] = float(np.mean(freqs)) if freqs else 0

    # Identify clusters by signature:
    # - Hub stars: smallest cluster with highest mean_freq and mean_degree
    # - Rare compounds: second-smallest with lowest mean_freq
    # - The rest: bulk clusters ordered by mean_depth

    sorted_by_size = sorted(cluster_profiles.items(), key=lambda x: x[1]['size'])

    # Smallest = hub stars (cluster 0 equivalent)
    hub_cluster = sorted_by_size[0][0]

    # Second smallest = rare compounds (cluster 1 equivalent)
    rare_cluster = sorted_by_size[1][0]

    # Remaining 3 clusters sorted by mean_depth
    remaining = [c for c, _ in sorted_by_size[2:]]
    remaining.sort(key=lambda c: cluster_profiles[c]['mean_depth'])

    # Shallowest depth = flow/transport (cluster 3 equivalent)
    # Middle depth = phase operations (cluster 2 equivalent)
    # Deepest = stability/monitoring (cluster 4 equivalent)
    shallow_cluster = remaining[0]
    mid_cluster = remaining[1]
    deep_cluster = remaining[2]

    # Affordance assignments (from PP_CONSTRAINT_AFFORDANCE_MAP T5)
    CLUSTER_AFFORDANCES = {
        hub_cluster: {
            'label': 'HUB_CONNECTORS',
            'primary_family': 'THERMAL',
            'secondary_families': ['MONITORING', 'PHASE'],
            'confidence': 'HIGH',
            'description': 'Universal connectors: high frequency, short, compatible with everything',
            'anchors': ['C476', 'C986'],
        },
        rare_cluster: {
            'label': 'SPECIFICATION_LAYER',
            'primary_family': 'RECOVERY',
            'secondary_families': ['THERMAL', 'MONITORING', 'FLOW'],
            'confidence': 'HIGH',
            'description': 'Hapax compounds: one-time specifications, setup/preparation',
            'anchors': ['C618', 'C935'],
        },
        mid_cluster: {
            'label': 'PHASE_OPERATIONS',
            'primary_family': 'PHASE',
            'secondary_families': [],
            'confidence': 'MEDIUM',
            'description': 'Phase transition and boiling regime management',
            'anchors': ['C991', 'C909'],
        },
        shallow_cluster: {
            'label': 'FLOW_TRANSPORT',
            'primary_family': 'FLOW',
            'secondary_families': [],
            'confidence': 'LOW',
            'description': 'Shallow depth, low internal compatibility — vapor/liquid transport',
            'anchors': ['C991', 'C987'],
        },
        deep_cluster: {
            'label': 'STABILITY_MONITORING',
            'primary_family': 'THERMAL',
            'secondary_families': ['MONITORING'],
            'confidence': 'MEDIUM',
            'description': 'e-enriched, CHSH-biased — thermal stability and quality assessment',
            'anchors': ['C647', 'C992', 'C908'],
        },
    }

    # ---- Build per-MIDDLE table ----
    print("\nBuilding per-MIDDLE table...")
    table = {}
    for i, middle in enumerate(middles):
        c = int(labels[i])
        aff = CLUSTER_AFFORDANCES[c]
        table[middle] = {
            'cluster': c,
            'cluster_label': aff['label'],
            'primary_family': aff['primary_family'],
            'secondary_families': aff['secondary_families'],
            'confidence': aff['confidence'],
            'radial_depth': round(float(residual_norms[i]), 4),
            'compat_degree': int(compat_degrees[i]),
            'token_frequency': mid_freq.get(middle, 0),
        }

    # ---- Summary stats ----
    conf_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    family_counts = {}
    for entry in table.values():
        conf_counts[entry['confidence']] += 1
        fam = entry['primary_family']
        family_counts[fam] = family_counts.get(fam, 0) + 1

    print(f"\nConfidence distribution:")
    for c, n_c in sorted(conf_counts.items()):
        print(f"  {c}: {n_c} ({n_c/n:.1%})")

    print(f"\nFamily distribution:")
    for f, n_f in sorted(family_counts.items(), key=lambda x: -x[1]):
        print(f"  {f}: {n_f}")

    # ---- Cluster summary ----
    print(f"\nCluster summary:")
    for c_id, aff in sorted(CLUSTER_AFFORDANCES.items()):
        mask = labels == c_id
        n_c = mask.sum()
        print(f"  Cluster {c_id} ({aff['label']}): n={n_c}, family={aff['primary_family']}, confidence={aff['confidence']}")
        # Top 5 examples by frequency
        examples = [(middles[i], mid_freq.get(middles[i], 0)) for i in range(n) if mask[i]]
        examples.sort(key=lambda x: -x[1])
        top5 = examples[:5]
        print(f"    Top examples: {top5}")

    # ---- Save ----
    output = {
        '_metadata': {
            'description': 'Per-MIDDLE affordance annotations (Tier 4 speculative)',
            'source_phase': 'PP_CONSTRAINT_AFFORDANCE_MAP + PROCESS_PHENOMENOLOGY_EXCLUSION',
            'n_middles': n,
            'n_clusters': 5,
            'overall_verdict': 'DISTILLATION_SUPPORTED',
            'confidence_distribution': conf_counts,
            'family_distribution': family_counts,
            'cluster_summary': {
                str(c_id): {
                    'label': aff['label'],
                    'size': int((labels == c_id).sum()),
                    'primary_family': aff['primary_family'],
                    'confidence': aff['confidence'],
                    'description': aff['description'],
                }
                for c_id, aff in CLUSTER_AFFORDANCES.items()
            },
            'warning': 'These are Tier 4 speculative annotations, NOT resolved semantic assignments. '
                       'Only 13% HIGH confidence. Use confidence field to filter.',
        },
        'middles': table,
    }

    out_path = OUTPUT_DIR / 'middle_affordance_table.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {out_path}")

    print(f"\n{'=' * 70}")
    print(f"MIDDLE AFFORDANCE TABLE GENERATED")
    print(f"  {n} MIDDLEs with cluster + family + confidence + depth")
    print(f"  HIGH: {conf_counts['HIGH']} | MEDIUM: {conf_counts['MEDIUM']} | LOW: {conf_counts['LOW']}")
    print(f"  Saved to: {out_path}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
