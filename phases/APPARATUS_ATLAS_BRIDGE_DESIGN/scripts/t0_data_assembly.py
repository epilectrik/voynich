"""T0: Data Assembly for Phase 582.

Gather all apparatus-related data from prior phases into a consolidated dataset.
Pure data loading and merging -- no analysis.
"""
import json
import os

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')
PHASES_ROOT = os.path.dirname(PHASE_DIR)


def load_json(phase_name, filename):
    path = os.path.join(PHASES_ROOT, phase_name, 'results', filename)
    with open(path) as f:
        return json.load(f)


def main():
    # ---- 1. Phase 580: Apparatus manifold ----
    p580_t0 = load_json('APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS',
                         't0_feature_matrix_assembly.json')
    p580_t1 = load_json('APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS',
                         't1_manifold_embedding.json')
    p580_t2 = load_json('APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS',
                         't2_family_occupancy.json')

    folio_list = p580_t0['folios']  # 76 folios in order
    space_a_features = p580_t0['metadata']['space_A_features']
    space_b_features = p580_t0['metadata']['space_B_features']
    space_a_raw = p580_t0['space_A']['raw']  # 76 x 11
    space_b_raw = p580_t0['space_B']['raw']  # 76 x 4
    folio_metadata = p580_t0['folio_metadata']  # profile, family, section, landscape_class

    # PCA loadings and scores
    pca_loadings = p580_t1['space_A']['loadings']
    pca_eigenvalues = p580_t1['space_A']['eigenvalues']
    pca_variance = p580_t1['space_A']['variance_explained']
    pca_folio_scores = p580_t1['space_A']['folio_scores']
    effective_rank = p580_t1['space_A']['effective_rank']

    # Family geometry
    family_counts = p580_t2['metadata']['family_counts']

    # ---- 2. Phase 572: Productive disruption per-folio metrics ----
    p572_t1 = load_json('PRODUCTIVE_DISRUPTION_EXPANSION',
                         't1_full_scale_setup.json')
    p572_t4 = load_json('PRODUCTIVE_DISRUPTION_EXPANSION',
                         't4_expansion_metrics.json')

    folio_configs = p572_t1['folio_configs']  # per-folio F1-F5, profile, section
    per_folio_metrics = p572_t4['per_folio']  # DVA, DYE, YGA, etc.

    # ---- 3. Phase 573: Forgivingness mechanism ----
    p573_t0 = load_json('A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES',
                         't0_opportunity_normalization.json')
    p573_t1 = load_json('A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES',
                         't1_mechanism_ablation.json')
    p573_t5 = load_json('A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES',
                         't5_synthesis.json')

    # ---- 4. Phase 574: Landscape model ----
    p574_t4 = load_json('COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP',
                         't4_landscape_model.json')
    per_folio_landscape = p574_t4['per_folio_landscape']

    # ---- 5. Phase 563: Apparatus family profiles ----
    p563_t1 = load_json('VIRTUAL_APPARATUS_COUPLING',
                         't1_apparatus_family.json')
    family_profiles = p563_t1['profiles']  # A1/A2/A3 with sensitivity/decay/alpha

    # ---- 6. Phase 581: Atom deployment ----
    p581_t1 = load_json('LINE_INTERNAL_ATOM_GRADIENT_DECOMPOSITION',
                         't1_atom_positional_gradients.json')
    p581_t3 = load_json('LINE_INTERNAL_ATOM_GRADIENT_DECOMPOSITION',
                         't3_hazard_atom_position.json')

    # ---- 7. Phase 480: Folio accent ----
    accent_path = os.path.join(PHASES_ROOT, 'FOLIO_ACCENT_VECTOR', 'results',
                               'folio_accent_vector.json')
    with open(accent_path) as f:
        accent_data = json.load(f)
    accent_scores = accent_data['T1_pca']['folio_scores']

    # ---- 8. Decoder maps ----
    decoder_path = os.path.join(os.path.dirname(PHASES_ROOT), 'data',
                                'decoder_maps.json')
    with open(decoder_path) as f:
        decoder_maps = json.load(f)
    frame_hazard = decoder_maps.get('frame_hazard', {})

    # ---- Build consolidated per-folio records ----
    consolidated = {}
    for i, folio in enumerate(folio_list):
        meta = folio_metadata.get(folio, {})
        fc = folio_configs.get(folio, {})
        pm = per_folio_metrics.get(folio, {})
        landscape = per_folio_landscape.get(folio, {})
        accent = accent_scores.get(folio, {})

        # Space A features
        sa_vals = space_a_raw[i] if i < len(space_a_raw) else [None] * 11
        features_a = {space_a_features[j]: sa_vals[j]
                      for j in range(len(space_a_features)) if j < len(sa_vals)}

        # Space B features
        sb_vals = space_b_raw[i] if i < len(space_b_raw) else [None] * 4
        features_b = {space_b_features[j]: sb_vals[j]
                      for j in range(len(space_b_features)) if j < len(sb_vals)}

        # Manifold PC coordinates
        pc_coords = pca_folio_scores.get(folio, {})

        consolidated[folio] = {
            'family': meta.get('family', fc.get('profile', 'unknown')),
            'landscape_class': meta.get('landscape_class', landscape.get('classification', '')),
            'profile': meta.get('profile', fc.get('profile', '')),
            'section': meta.get('section', fc.get('section', '')),
            'features_A': features_a,
            'features_B': features_b,
            'pc_coordinates': pc_coords,
            'process_metrics': {
                'DVA': pm.get('DVA'),
                'DYE_M1': pm.get('DYE_M1'),
                'DYE_M4f': pm.get('DYE_M4f'),
                'DYE_advantage': pm.get('DYE_advantage'),
                'YGA': pm.get('YGA'),
                'DYC': pm.get('DYC'),
                'EPV': pm.get('EPV'),
                'CCS1': features_b.get('CCS1'),
                'z_DYE': pm.get('z_DYE'),
                'z_YGA': pm.get('z_YGA'),
                'M0_WCP': pm.get('M0_WCP'),
                'M1_WCP': pm.get('M1_WCP'),
            },
            'landscape': {
                'z_margin': landscape.get('z_margin'),
                'PEF': landscape.get('positive_event_fraction',
                                     features_b.get('PEF')),
                'mean_CTS': landscape.get('mean_CTS',
                                          features_a.get('mean_CTS')),
                'classification': landscape.get('classification', ''),
            },
            'accent': accent,
        }

    # ---- Family profile summaries ----
    family_summary = {}
    for fname, fprofile in family_profiles.items():
        family_folios = [f for f in folio_list
                         if folio_metadata.get(f, {}).get('family') == fname]
        family_summary[fname] = {
            'n_folios': len(family_folios),
            'folios': family_folios,
            'parameters': fprofile,
        }

    # ---- Ablation mechanism summary ----
    ablation_names = p573_t1.get('metadata', {}).get('ablation_names',
                                                       list(p573_t1.get('profile_results', {}).get(
                                                           list(p573_t1.get('profile_results', {}).keys())[0] if p573_t1.get('profile_results') else 'x', {}
                                                       ).get('ablation_effects', {}).keys()))
    ablation_summary = {}
    for prof_name, prof_data in p573_t1.get('profile_results', {}).items():
        effects = prof_data.get('ablation_effects', {})
        ablation_summary[prof_name] = {
            abl: effects.get(abl, {}) for abl in ablation_names
        }

    # ---- PCA loadings for manifold-to-knob mapping ----
    pca_summary = {
        'effective_rank': effective_rank,
        'eigenvalues': pca_eigenvalues,
        'variance_explained': pca_variance,
        'loadings': pca_loadings,
        'feature_names': space_a_features,
    }

    # ---- Atom deployment summary (from Phase 581) ----
    atom_deployment = {
        'head_profiles': p581_t1.get('head_profiles', {}),
        'terminal_profiles': p581_t1.get('terminal_profiles', {}),
        'predictions': p581_t1.get('predictions', {}),
        'carryover_cross_reference': p581_t1.get('carryover_cross_reference', {}),
    }

    hazard_atom_position = {
        'three_way_enrichment': p581_t3.get('three_way_enrichment', {}),
        'zone_specific_pairs': p581_t3.get('zone_specific_pairs', []),
        'thermal_cluster_comparison': p581_t3.get('thermal_cluster_comparison', {}),
    }

    # ---- Output ----
    output = {
        'metadata': {
            'phase': '582',
            'script': 't0_data_assembly.py',
            'n_folios': len(folio_list),
            'folio_list': folio_list,
            'space_A_features': space_a_features,
            'space_B_features': space_b_features,
            'sources': [
                'APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS (Phase 580)',
                'PRODUCTIVE_DISRUPTION_EXPANSION (Phase 572)',
                'A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES (Phase 573)',
                'COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP (Phase 574)',
                'VIRTUAL_APPARATUS_COUPLING (Phase 563)',
                'LINE_INTERNAL_ATOM_GRADIENT_DECOMPOSITION (Phase 581)',
                'FOLIO_ACCENT_VECTOR (Phase 480)',
                'data/decoder_maps.json',
            ],
        },
        'per_folio': consolidated,
        'family_profiles': family_summary,
        'ablation_summary': ablation_summary,
        'pca_summary': pca_summary,
        'atom_deployment': atom_deployment,
        'hazard_atom_position': hazard_atom_position,
        'family_counts': family_counts,
    }

    out_path = os.path.join(RESULTS_DIR, 't0_data_assembly.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    # ---- Validation ----
    n = len(folio_list)
    families_present = set(folio_metadata[f].get('family', '') for f in folio_list)
    profiles_present = set(folio_metadata[f].get('profile', '') for f in folio_list)
    n_with_dye = sum(1 for f in folio_list
                     if per_folio_metrics.get(f, {}).get('DYE_advantage') is not None)

    print("T0: Data assembly complete")
    print(f"  Folios: {n}")
    print(f"  Families: {sorted(families_present)}")
    print(f"  Profiles: {sorted(profiles_present)}")
    print(f"  Folios with DYE data: {n_with_dye}/{n}")
    print(f"  PCA effective rank: {effective_rank}")
    print(f"  Family counts: {family_counts}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
