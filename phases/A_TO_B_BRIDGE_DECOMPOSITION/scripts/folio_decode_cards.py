#!/usr/bin/env python3
"""
Phase 626 Script 3: Folio Decode Cards

Selects 5 pilot folios spanning the PP Jaccard distance space,
constructs comprehensive A-side -> bridge -> B-side decode cards,
and validates the cross-folio chain.

Tests:
  T1: Select 5 pilot folios
  T2: Per-folio decode card construction
  T3: Cross-folio distance validation
  T4: Paragraph shape prediction (C1796-C1800)
  T5: Operational distinctiveness scoring
"""

import sys, json, functools, warnings, time, math, random
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
warnings.filterwarnings('ignore')

from scipy import stats
from scipy.spatial.distance import squareform

from scripts.voynich import (
    Transcript, Morphology, CategoryClassifier,
    load_middle_classes, decompose_middle_hmt,
)
from phases.A_TO_B_BRIDGE_DECOMPOSITION.scripts.shared_626 import (
    PROJECT_ROOT, RESULTS_DIR, CATEGORIES,
    load_pp_classification, load_a_record_profiles,
    load_b_operational_profiles, load_b_deployment_features,
    load_manifold_scores, load_bridge_dark_sets, load_regime_mapping,
    group_records_by_folio, compute_folio_pp_set_from_profiles,
    compute_folio_ri_set, compute_folio_bridge_inventory,
    get_a_folio_section,
    jaccard_similarity, jsd, cosine_sim, round_floats,
)

t0 = time.time()

print("=" * 70)
print("Phase 626 Script 3: Folio Decode Cards")
print("=" * 70)


# ============================================================
# STAGE 0: Load data + Script 1 & 2 results
# ============================================================

tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()
ri_middles, pp_middles = load_middle_classes()
pp_class = load_pp_classification()
records = load_a_record_profiles()
folio_records = group_records_by_folio(records)
b_ops = load_b_operational_profiles()
b_deploy, deploy_names = load_b_deployment_features()
manifold = load_manifold_scores()
bridge_set, dark_set = load_bridge_dark_sets()
regime_map = load_regime_mapping()

# Load Script 1 results
with open(RESULTS_DIR / 'pp_clustering.json') as f:
    s1 = json.load(f)
folio_cluster = s1['T1_pp_clustering']['folio_cluster']

# Load Script 2 results
with open(RESULTS_DIR / 'bridge_decomposition.json') as f:
    s2 = json.load(f)
a_context = s2['T1_a_context']
b_consequence = s2['T2_b_consequence']
bridge_func_group = s2['T5_functional_groups'].get('bridge_group_assignment', {})

a_folios = sorted(folio_records.keys())
n_folios = len(a_folios)
print(f"  A folios: {n_folios}")
print(f"  B folios with ops: {len(b_ops)}")

# ============================================================
# T1: Select 5 pilot folios
# ============================================================

print("\n[T1] Selecting 5 pilot folios...")

# Criteria:
# 1. Must have A records AND connected B folios with operational profiles
# 2. Span different clusters
# 3. Prefer folios with high bridge MIDDLE count

# Score each A folio
folio_scores = {}
for folio in a_folios:
    recs = folio_records[folio]
    
    # Bridge MIDDLE count
    bridge_inv = compute_folio_bridge_inventory(recs, bridge_set)
    n_bridge = sum(bridge_inv.values())
    
    # Connected B folios
    b_connections = Counter()
    for rec in recs:
        for bf, count in rec.get('b_convergence', {}).items():
            if bf in b_ops:
                b_connections[bf] += count
    n_b_connected = len(b_connections)
    
    # Cluster membership
    cluster = folio_cluster.get(folio, 0)
    
    folio_scores[folio] = {
        'n_bridge': n_bridge,
        'n_b_connected': n_b_connected,
        'cluster': cluster,
        'bridge_middles': sorted(bridge_inv.keys()),
        'top_b_folios': b_connections.most_common(5),
    }

# Select: one from each cluster (pick highest bridge count), span clusters
clusters_available = sorted(set(folio_cluster.values()))
pilot_folios = []
used_clusters = set()

# First pass: one per cluster
for c in clusters_available:
    candidates = [(f, folio_scores[f]) for f in a_folios 
                  if folio_cluster.get(f) == c and folio_scores[f]['n_b_connected'] > 0]
    if candidates:
        # Pick the one with most bridge MIDDLEs
        best = max(candidates, key=lambda x: x[1]['n_bridge'])
        pilot_folios.append(best[0])
        used_clusters.add(c)
    if len(pilot_folios) >= 5:
        break

# If fewer than 5 clusters, fill remaining from highest-bridge folios
if len(pilot_folios) < 5:
    remaining = [(f, folio_scores[f]) for f in a_folios 
                 if f not in pilot_folios and folio_scores[f]['n_b_connected'] > 0]
    remaining.sort(key=lambda x: -x[1]['n_bridge'])
    for f, _ in remaining:
        if len(pilot_folios) >= 5:
            break
        pilot_folios.append(f)

print(f"  Selected pilot folios: {pilot_folios}")
for pf in pilot_folios:
    sc = folio_scores[pf]
    print(f"    {pf}: cluster={sc['cluster']}, bridge_middles={sc['n_bridge']}, "
          f"b_connected={sc['n_b_connected']}")


# ============================================================
# T2: Decode card construction
# ============================================================

print("\n[T2] Building decode cards...")

MATERIAL_CLASSES = ['ANIMAL', 'HERB', 'NEUTRAL', 'MIXED']

decode_cards = {}
for pf in pilot_folios:
    recs = folio_records[pf]
    
    # === A-side (specification) ===
    
    # PP MIDDLE inventory with categories
    pp_inventory = Counter()
    pp_categories = {}
    for rec in recs:
        for tok in rec.get('pp_tokens', []):
            m = morph.extract(tok)
            if m.middle:
                pp_inventory[m.middle] += 1
                if m.middle not in pp_categories:
                    pp_categories[m.middle] = cc.classify(m.middle)
    
    top_pp = pp_inventory.most_common(10)
    top_pp_with_cat = [(mid, count, pp_categories.get(mid, 'UNKNOWN')) for mid, count in top_pp]
    
    # Bridge MIDDLEs
    bridge_inv = compute_folio_bridge_inventory(recs, bridge_set)
    bridge_list = sorted(bridge_inv.keys(), key=lambda x: -bridge_inv[x])
    
    # RI MIDDLEs
    ri_set = compute_folio_ri_set(recs)
    
    # PREFIX profile
    prefix_sums = Counter()
    prefix_n = 0
    for rec in recs:
        npp = rec.get('normalized_prefix_profile', {})
        if npp:
            for k, v in npp.items():
                prefix_sums[k] += v
            prefix_n += 1
    prefix_profile = {k: v / prefix_n for k, v in prefix_sums.items()} if prefix_n > 0 else {}
    
    # Cluster
    cluster = folio_cluster.get(pf, 0)
    
    # Material overlay (Tier 3)
    mat_counts = Counter()
    mat_total = 0
    for mid, count in pp_inventory.items():
        if mid in pp_class:
            mat_counts[pp_class[mid]['material_class']] += count
            mat_total += count
    material_overlay = {mc: mat_counts[mc] / mat_total if mat_total > 0 else 0.0 
                        for mc in MATERIAL_CLASSES}
    
    # Category profile
    cat_counts = Counter()
    cat_total = 0
    for mid, count in pp_inventory.items():
        cat = cc.classify(mid)
        if cat in CATEGORIES:
            cat_counts[cat] += count
            cat_total += count
    cat_profile = {cat: cat_counts[cat] / cat_total if cat_total > 0 else 0.0 
                   for cat in CATEGORIES}
    
    # === Bridge (translation) ===
    
    bridge_details = []
    for bm in bridge_list[:10]:
        a_ctx = a_context.get(bm, {})
        b_con = b_consequence.get(bm, {})
        func_group = bridge_func_group.get(bm, 0)
        
        # A-side HEAD (dominant in neighborhood)
        a_heads = a_ctx.get('head_neighborhood', {})
        a_dom = max(a_heads, key=a_heads.get) if a_heads else 'unknown'
        
        # B-side HEAD (dominant)
        b_heads = b_con.get('head_dist', {})
        b_dom = max(b_heads, key=b_heads.get) if b_heads else 'unknown'
        
        # RI co-occurrence
        ri_cooccur = a_ctx.get('top_ri_cooccur', [])
        
        bridge_details.append({
            'middle': bm,
            'count_in_folio': bridge_inv[bm],
            'a_head_dominant': a_dom,
            'b_head_dominant': b_dom,
            'b_category': b_con.get('category', 'UNKNOWN'),
            'functional_group': func_group,
            'ri_cooccur': ri_cooccur[:3],
            'b_hazard_frac': b_con.get('hazard_fraction', 0.0),
            'b_lane': b_con.get('lane_dist', {}),
        })
    
    # === B-side (execution) ===
    
    b_connections = Counter()
    for rec in recs:
        for bf, count in rec.get('b_convergence', {}).items():
            if bf in b_ops:
                b_connections[bf] += count
    
    top_b = b_connections.most_common(5)
    b_side_profiles = []
    for bf, count in top_b:
        ops = b_ops.get(bf, {})
        regime = regime_map.get(bf, 'UNKNOWN')
        man_scores = manifold.get(bf, {})
        
        b_side_profiles.append({
            'folio': bf,
            'convergence_count': count,
            'regime': regime,
            'k_ratio': ops.get('k_ratio', 0.0),
            'h_ratio': ops.get('h_ratio', 0.0),
            'e_ratio': ops.get('e_ratio', 0.0),
            'kernel_balance': ops.get('kernel_balance', 'UNKNOWN'),
            'material_category': ops.get('material_category', 'UNKNOWN'),
            'manifold_PC1': man_scores.get('PC1', 0.0),
            'manifold_PC2': man_scores.get('PC2', 0.0),
        })

    
    # === Synthesis ===
    
    # Top operational emphasis
    top_cats = sorted(cat_profile.items(), key=lambda x: -x[1])[:3]
    top_bridge_cats = Counter()
    for bd in bridge_details:
        top_bridge_cats[bd['b_category']] += 1
    
    # Dominant material (Tier 3)
    dom_material = max(material_overlay, key=material_overlay.get) if material_overlay else 'UNKNOWN'
    
    # Dominant REGIME of connected B folios
    regime_counts = Counter()
    for bp in b_side_profiles:
        regime_counts[bp['regime']] += bp['convergence_count']
    dom_regime = regime_counts.most_common(1)[0][0] if regime_counts else 'UNKNOWN'
    
    # Build narrative
    cat_str = ", ".join(f"{cat} ({frac:.0%})" for cat, frac in top_cats)
    bridge_cat_str = ", ".join(f"{cat}:{n}" for cat, n in top_bridge_cats.most_common(3))
    
    decode_cards[pf] = {
        'a_side': {
            'n_pp_tokens': sum(pp_inventory.values()),
            'n_unique_pp': len(pp_inventory),
            'top_pp_with_category': top_pp_with_cat,
            'n_bridge_middles': len(bridge_inv),
            'n_ri_middles': len(ri_set),
            'prefix_profile': prefix_profile,
            'cluster': cluster,
            'section': get_a_folio_section(pf),
            'material_overlay': material_overlay,
            'category_profile': cat_profile,
        },
        'bridge': {
            'n_bridge_types': len(bridge_inv),
            'n_bridge_tokens': sum(bridge_inv.values()),
            'details': bridge_details,
        },
        'b_side': {
            'n_connected': len(b_connections),
            'top_connections': b_side_profiles,
            'dominant_regime': dom_regime,
        },
        'synthesis': {
            'operational_emphasis': cat_str,
            'bridge_categories': bridge_cat_str,
            'material_overlay_dominant': dom_material,
            'dominant_regime': dom_regime,
            'narrative': (f"Folio {pf} specifies operations with emphasis on {cat_str}. "
                         f"Its {len(bridge_inv)} bridge MIDDLEs produce B-side categories "
                         f"{bridge_cat_str}. Material overlay (Tier 3): {dom_material}-dominant. "
                         f"Connected B folios predominantly run {dom_regime}."),
        },
    }
    
    print(f"\n  === {pf} ===")
    print(f"    A-side: {sum(pp_inventory.values())} PP tokens, {len(bridge_inv)} bridge, {len(ri_set)} RI")
    print(f"    Category: {cat_str}")
    print(f"    Bridge -> B categories: {bridge_cat_str}")
    print(f"    Connected to {len(b_connections)} B folios, dominant REGIME: {dom_regime}")


# ============================================================
# T3: Cross-folio distance validation
# ============================================================

print("\n\n[T3] Cross-folio distance validation...")

n_pilot = len(pilot_folios)
if n_pilot >= 3:
    # A-side distances
    a_pp_dists = []
    a_ri_dists = []
    b_op_dists = []
    b_manifold_dists = []
    
    pilot_pp_sets = {f: compute_folio_pp_set_from_profiles(folio_records[f]) for f in pilot_folios}
    pilot_ri_sets = {f: compute_folio_ri_set(folio_records[f]) for f in pilot_folios}
    
    # Aggregate B-side profiles for each pilot folio
    pilot_b_profiles = {}
    for pf in pilot_folios:
        recs = folio_records[pf]
        b_connections = Counter()
        for rec in recs:
            for bf, count in rec.get('b_convergence', {}).items():
                if bf in b_ops:
                    b_connections[bf] += count
        
        # Weighted mean operational profile
        if b_connections:
            total_weight = sum(b_connections.values())
            op_dims = list(list(b_ops.values())[0].keys())
            op_dims = [d for d in op_dims if isinstance(b_ops[list(b_ops.keys())[0]].get(d), (int, float))]
            
            mean_profile = {}
            for dim in op_dims:
                weighted_sum = sum(b_ops[bf].get(dim, 0.0) * w for bf, w in b_connections.items()
                                  if isinstance(b_ops[bf].get(dim), (int, float)))
                mean_profile[dim] = weighted_sum / total_weight
            pilot_b_profiles[pf] = mean_profile
            
            # Weighted mean manifold position
            man_dims = ['PC1', 'PC2', 'PC3', 'PC4', 'PC5']
            man_profile = {}
            for d in man_dims:
                weighted_sum = sum(manifold.get(bf, {}).get(d, 0.0) * w 
                                  for bf, w in b_connections.items())
                man_profile[d] = weighted_sum / total_weight
            pilot_b_profiles[pf]['manifold'] = man_profile
    
    # Compute pairwise distances
    pair_data = []
    for i in range(n_pilot):
        for j in range(i + 1, n_pilot):
            fi, fj = pilot_folios[i], pilot_folios[j]
            
            pp_jacc = 1.0 - jaccard_similarity(pilot_pp_sets[fi], pilot_pp_sets[fj])
            ri_jacc = 1.0 - jaccard_similarity(pilot_ri_sets[fi], pilot_ri_sets[fj])
            
            # B-side operational cosine distance
            if fi in pilot_b_profiles and fj in pilot_b_profiles:
                op_dims = [d for d in pilot_b_profiles[fi] if d != 'manifold' 
                          and isinstance(pilot_b_profiles[fi].get(d), (int, float))]
                vec_i = [pilot_b_profiles[fi].get(d, 0.0) for d in op_dims]
                vec_j = [pilot_b_profiles[fj].get(d, 0.0) for d in op_dims]
                op_cos = 1.0 - cosine_sim(vec_i, vec_j)
                
                # Manifold Euclidean
                man_i = pilot_b_profiles[fi].get('manifold', {})
                man_j = pilot_b_profiles[fj].get('manifold', {})
                man_dist = math.sqrt(sum((man_i.get(d, 0) - man_j.get(d, 0))**2 
                                        for d in ['PC1', 'PC2', 'PC3', 'PC4', 'PC5']))
            else:
                op_cos = 0.5
                man_dist = 0.0
            
            a_pp_dists.append(pp_jacc)
            a_ri_dists.append(ri_jacc)
            b_op_dists.append(op_cos)
            b_manifold_dists.append(man_dist)
            
            pair_data.append({
                'folio_i': fi,
                'folio_j': fj,
                'pp_jacc_dist': pp_jacc,
                'ri_jacc_dist': ri_jacc,
                'b_op_cos_dist': op_cos,
                'b_manifold_dist': man_dist,
            })
    
    # Correlations
    n_pairs = len(a_pp_dists)
    
    if n_pairs >= 3:
        rho_pp_op, p_pp_op = stats.spearmanr(a_pp_dists, b_op_dists)
        rho_pp_man, p_pp_man = stats.spearmanr(a_pp_dists, b_manifold_dists)
        rho_ri_op, p_ri_op = stats.spearmanr(a_ri_dists, b_op_dists)
    else:
        rho_pp_op = rho_pp_man = rho_ri_op = 0.0
        p_pp_op = p_pp_man = p_ri_op = 1.0
    
    print(f"  PP_dist vs B_op_dist: rho={rho_pp_op:.4f}, p={p_pp_op:.4f}")
    print(f"  PP_dist vs B_manifold_dist: rho={rho_pp_man:.4f}, p={p_pp_man:.4f}")
    print(f"  RI_dist vs B_op_dist: rho={rho_ri_op:.4f}, p={p_ri_op:.4f}")
else:
    pair_data = []
    rho_pp_op = rho_pp_man = rho_ri_op = 0.0
    p_pp_op = p_pp_man = p_ri_op = 1.0


# ============================================================
# T4: Paragraph shape (simplified -- compare B-paragraph line counts)
# ============================================================

print("\n[T4] Paragraph shape comparison...")

# For each pilot folio's connected B folios, compute paragraph length distribution
pilot_para_shapes = {}

b_para_info = defaultdict(list)  # folio -> list of paragraph line counts
current_folio = None
current_para_lines = 0

for token in tx.currier_b():
    if token.folio != current_folio:
        if current_folio and current_para_lines > 0:
            b_para_info[current_folio].append(current_para_lines)
        current_folio = token.folio
        current_para_lines = 1
        current_line = token.line
    elif token.line != current_line:
        # Check if new paragraph (gallows-initial)
        w = token.word.strip()
        if w and not ('*' in w):
            m = morph.extract(w)
            if m.middle:
                hmt = decompose_middle_hmt(m.middle)
                if hmt and hmt[0] in ('k', 't', 'p', 'f'):
                    b_para_info[current_folio].append(current_para_lines)
                    current_para_lines = 0
        current_line = token.line
        current_para_lines += 1

if current_folio and current_para_lines > 0:
    b_para_info[current_folio].append(current_para_lines)

# For each pilot folio: aggregate paragraph shapes of connected B folios
for pf in pilot_folios:
    recs = folio_records[pf]
    b_connections = Counter()
    for rec in recs:
        for bf, count in rec.get('b_convergence', {}).items():
            b_connections[bf] += count
    
    all_shapes = []
    for bf in b_connections:
        all_shapes.extend(b_para_info.get(bf, []))
    
    if all_shapes:
        pilot_para_shapes[pf] = {
            'mean_lines': float(np.mean(all_shapes)),
            'median_lines': float(np.median(all_shapes)),
            'std_lines': float(np.std(all_shapes)),
            'n_paragraphs': len(all_shapes),
        }
    else:
        pilot_para_shapes[pf] = {
            'mean_lines': 0.0, 'median_lines': 0.0, 
            'std_lines': 0.0, 'n_paragraphs': 0,
        }

for pf in pilot_folios:
    ps = pilot_para_shapes[pf]
    print(f"  {pf}: mean={ps['mean_lines']:.1f} lines, median={ps['median_lines']:.0f}, "
          f"n_para={ps['n_paragraphs']}")


# ============================================================
# T5: Operational distinctiveness scoring
# ============================================================

print("\n[T5] Operational distinctiveness scoring...")

# Z-score each pilot folio's B-side profile against all B folios
all_b_folios = sorted(b_ops.keys())
op_dims = ['k_ratio', 'h_ratio', 'e_ratio', 'thermo_ke', 'thermo_kch',
           'prep_te', 'prep_pch', 'iteration_rate', 'checkpoint_rate', 'terminal_rate']

dim_means = {}
dim_stds = {}
for dim in op_dims:
    vals = [b_ops[f].get(dim, 0.0) for f in all_b_folios if isinstance(b_ops[f].get(dim), (int, float))]
    dim_means[dim] = float(np.mean(vals)) if vals else 0.0
    dim_stds[dim] = float(np.std(vals)) if vals else 1.0

distinctiveness = {}
for pf in pilot_folios:
    if pf not in pilot_b_profiles:
        distinctiveness[pf] = {'z_scores': {}, 'top_3': []}
        continue
    
    z_scores = {}
    for dim in op_dims:
        val = pilot_b_profiles[pf].get(dim, 0.0)
        if dim_stds[dim] > 1e-10:
            z = (val - dim_means[dim]) / dim_stds[dim]
        else:
            z = 0.0
        z_scores[dim] = float(z)
    
    top_3 = sorted(z_scores.items(), key=lambda x: -abs(x[1]))[:3]
    distinctiveness[pf] = {
        'z_scores': z_scores,
        'top_3': [(dim, round(z, 3)) for dim, z in top_3],
    }
    
    top_str = ", ".join(f"{dim}={z:+.2f}" for dim, z in top_3)
    print(f"  {pf}: {top_str}")


# ============================================================
# OUTPUT
# ============================================================

elapsed = time.time() - t0
print(f"\n  Total time: {elapsed:.1f}s")

output = {
    'metadata': {
        'phase': 626,
        'script': 3,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'n_pilot_folios': len(pilot_folios),
        'elapsed_s': round(elapsed, 1),
    },
    'T1_pilot_selection': {
        'folios': pilot_folios,
        'scores': {f: round_floats(folio_scores[f]) for f in pilot_folios},
    },
    'T2_decode_cards': round_floats(decode_cards),
    'T3_cross_folio': {
        'pair_data': round_floats(pair_data),
        'rho_pp_op': round(rho_pp_op, 4) if not np.isnan(rho_pp_op) else 0.0,
        'p_pp_op': round(p_pp_op, 4) if not np.isnan(p_pp_op) else 1.0,
        'rho_pp_manifold': round(rho_pp_man, 4) if not np.isnan(rho_pp_man) else 0.0,
        'p_pp_manifold': round(p_pp_man, 4) if not np.isnan(p_pp_man) else 1.0,
        'rho_ri_op': round(rho_ri_op, 4) if not np.isnan(rho_ri_op) else 0.0,
        'p_ri_op': round(p_ri_op, 4) if not np.isnan(p_ri_op) else 1.0,
    },
    'T4_paragraph_shape': round_floats(pilot_para_shapes),
    'T5_distinctiveness': round_floats(distinctiveness),
}

with open(RESULTS_DIR / 'folio_decode_cards.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n  Output: {RESULTS_DIR / 'folio_decode_cards.json'}")
print("  DONE")
