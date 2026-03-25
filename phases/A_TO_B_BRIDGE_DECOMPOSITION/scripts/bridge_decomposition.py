#!/usr/bin/env python3
"""
Phase 626 Script 2: Bridge MIDDLE Operational Decomposition

For each of 85 bridge MIDDLEs, computes:
  - A-side context: folio spread, section bias, atom neighborhood, PP co-occurrence, RI co-occurrence
  - B-side consequence: category, HEAD redistribution, suffix mode, hazard frame, line/para position, opacity, lane

Tests:
  T1: A-side context vector per bridge MIDDLE
  T2: B-side consequence vector per bridge MIDDLE
  T3: A-context-to-B-consequence Mantel prediction
  T4: HEAD redistribution analysis (C1507 extension)
  T5: Bridge MIDDLE functional grouping
"""

import sys, json, functools, warnings, time, math, random
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
warnings.filterwarnings('ignore')

from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform, pdist
from scipy import stats

from scripts.voynich import (
    Transcript, Morphology, CategoryClassifier,
    load_middle_classes, decompose_middle_hmt,
)
from phases.A_TO_B_BRIDGE_DECOMPOSITION.scripts.shared_626 import (
    PROJECT_ROOT, RESULTS_DIR, N_PERM, RNG,
    CATEGORIES,
    load_a_record_profiles, load_bridge_dark_sets,
    group_records_by_folio, get_a_folio_section,
    cosine_sim, mantel_test, round_floats,
)

t0 = time.time()

print("=" * 70)
print("Phase 626 Script 2: Bridge MIDDLE Operational Decomposition")
print("=" * 70)
# ============================================================
# STAGE 0: Data Loading
# ============================================================

tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()
ri_middles, pp_middles = load_middle_classes()
bridge_set, dark_set = load_bridge_dark_sets()
records = load_a_record_profiles()
folio_records = group_records_by_folio(records)

# Load hazard pairs
hazard_path = (PROJECT_ROOT / 'phases' / '15-20_kernel_grammar' /
               'phase18a_forbidden_inventory.json')
with open(hazard_path) as f:
    hazard_data = json.load(f)
FORBIDDEN_PAIRS = [(t['source'], t['target']) for t in hazard_data['transitions']]
hazard_heads = set()
for s, t in FORBIDDEN_PAIRS:
    hazard_heads.add(s)
    hazard_heads.add(t)

# Mode A and Mode B suffix sets
MODE_A_SUFFIXES = {'y', 'dy', 'ey', 'ly', 'ry', 'shy', 'sy', 'ty'}
MODE_B_SUFFIXES = {'l', 'd', 'r', 's', 'm', 'n', 'g', 'in', 'iin', 'ain'}

print(f"  Bridge MIDDLEs: {len(bridge_set)}")
print(f"  Dark MIDDLEs: {len(dark_set)}")

# ============================================================
# STAGE 1: Build A-side context for each bridge MIDDLE
# ============================================================

print("\n[T1] Computing A-side context vectors...")

# Build A-side data: which folios/records contain each bridge MIDDLE as PP
bridge_a_folios = defaultdict(set)       # bridge MIDDLE -> set of A folios
bridge_a_records = defaultdict(list)     # bridge MIDDLE -> list of record dicts
bridge_a_pp_cooccur = defaultdict(Counter)   # bridge MIDDLE -> co-occurring PP MIDDLEs
bridge_a_ri_cooccur = defaultdict(Counter)   # bridge MIDDLE -> co-occurring RI MIDDLEs
bridge_a_head_counts = defaultdict(Counter)  # bridge MIDDLE -> HEAD distribution in A

for folio, recs in folio_records.items():
    for rec in recs:
        # Extract all PP MIDDLEs and RI MIDDLEs in this record
        rec_pp_middles = set()
        rec_ri_middles = set()
        rec_heads = []
        
        for tok in rec.get('pp_tokens', []):
            m = morph.extract(tok)
            if m.middle:
                rec_pp_middles.add(m.middle)
        
        for tok in rec.get('ri_tokens', []):
            m = morph.extract(tok)
            if m.middle:
                rec_ri_middles.add(m.middle)
        
        # Also extract HEAD info from all tokens
        for tok in rec.get('all_tokens', []):
            m = morph.extract(tok)
            if m.middle:
                hmt = decompose_middle_hmt(m.middle)
                if hmt:
                    rec_heads.append(hmt[0])  # HEAD
        
        # For each bridge MIDDLE in this record's PP tokens:
        for bm in rec_pp_middles & bridge_set:
            bridge_a_folios[bm].add(folio)
            bridge_a_records[bm].append(rec)
            
            # Co-occurrence with other PP MIDDLEs
            for other in rec_pp_middles:
                if other != bm:
                    bridge_a_pp_cooccur[bm][other] += 1
            
            # Co-occurrence with RI MIDDLEs
            for ri in rec_ri_middles:
                bridge_a_ri_cooccur[bm][ri] += 1
            
            # HEAD neighborhood
            for h in rec_heads:
                bridge_a_head_counts[bm][h] += 1

# Build A-side context vector for each bridge MIDDLE
a_context = {}
all_a_folios = sorted(folio_records.keys())
n_a_folios = len(all_a_folios)

HEAD_NAMES = ['k', 't', 'a', 'e', 'o', 'h', 'headless']

for bm in sorted(bridge_set):
    b_folios = bridge_a_folios.get(bm, set())
    spread = len(b_folios) / n_a_folios if n_a_folios > 0 else 0.0
    
    # Section bias
    h_count = sum(1 for f in b_folios if get_a_folio_section(f) == 'H')
    p_count = sum(1 for f in b_folios if get_a_folio_section(f) == 'P')
    section_bias = h_count / (h_count + p_count) if (h_count + p_count) > 0 else 0.5
    
    # HEAD neighborhood distribution
    head_total = sum(bridge_a_head_counts[bm].values())
    head_dist = {}
    for h in HEAD_NAMES:
        head_dist[h] = bridge_a_head_counts[bm].get(h, 0) / head_total if head_total > 0 else 0.0
    
    # Number of co-occurring PP MIDDLEs
    n_pp_cooccur = len(bridge_a_pp_cooccur[bm])
    
    # Number of co-occurring RI MIDDLEs
    n_ri_cooccur = len(bridge_a_ri_cooccur[bm])
    
    # Top co-occurring PP and RI
    top_pp = bridge_a_pp_cooccur[bm].most_common(5)
    top_ri = bridge_a_ri_cooccur[bm].most_common(5)
    
    a_context[bm] = {
        'folio_spread': spread,
        'n_folios': len(b_folios),
        'section_bias_h': section_bias,
        'head_neighborhood': head_dist,
        'n_pp_cooccur': n_pp_cooccur,
        'n_ri_cooccur': n_ri_cooccur,
        'top_pp_cooccur': [(m, c) for m, c in top_pp],
        'top_ri_cooccur': [(m, c) for m, c in top_ri],
    }

found_in_a = sum(1 for bm in bridge_set if bm in a_context and a_context[bm]['n_folios'] > 0)
print(f"  Bridge MIDDLEs found in A records: {found_in_a}/{len(bridge_set)}")
# ============================================================
# T2: Build B-side consequence for each bridge MIDDLE
# ============================================================

print("\n[T2] Computing B-side consequence vectors...")

# Scan all B tokens
bridge_b_occurrences = defaultdict(list)  # bridge MIDDLE -> list of occurrence dicts

b_tokens_by_folio_line = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if not m.middle:
        continue
    
    b_tokens_by_folio_line[(token.folio, token.line)].append({
        'word': w,
        'middle': m.middle,
        'prefix': m.prefix,
        'suffix': m.suffix,
        'articulator': m.articulator,
        'folio': token.folio,
        'line': token.line,
    })

# Build line-level info
b_line_tokens = defaultdict(list)  # (folio, line) -> list of middles in order
b_line_lengths = {}
b_folio_lines = defaultdict(list)  # folio -> sorted list of line numbers

for (folio, line), tokens in b_tokens_by_folio_line.items():
    middles = [t['middle'] for t in tokens]
    b_line_tokens[(folio, line)] = middles
    b_line_lengths[(folio, line)] = len(tokens)
    b_folio_lines[folio].append(line)

for folio in b_folio_lines:
    b_folio_lines[folio] = sorted(set(b_folio_lines[folio]))

# Now scan for bridge MIDDLE occurrences in B
for (folio, line), tokens in b_tokens_by_folio_line.items():
    lines_in_folio = b_folio_lines.get(folio, [])
    n_lines = len(lines_in_folio)
    if n_lines > 0:
        line_idx = lines_in_folio.index(line) if line in lines_in_folio else 0
        line_quartile = line_idx / n_lines  # 0.0 = first line, 1.0 = last
    else:
        line_quartile = 0.5
    
    middles_in_line = [t['middle'] for t in tokens]
    n_tokens_in_line = len(tokens)
    
    for pos, t in enumerate(tokens):
        mid = t['middle']
        if mid not in bridge_set:
            continue
        
        # Position within line
        token_quartile = pos / n_tokens_in_line if n_tokens_in_line > 0 else 0.5
        
        # HEAD via HMT decomposition
        hmt = decompose_middle_hmt(mid)
        b_head = hmt[0] if hmt else 'unknown'
        
        # Category
        cat = cc.classify(mid)
        
        # Suffix mode
        suffix = t.get('suffix', '')
        if suffix in MODE_A_SUFFIXES:
            suf_mode = 'A'
        elif suffix in MODE_B_SUFFIXES:
            suf_mode = 'B'
        else:
            suf_mode = 'BARE'
        
        # Terminal opacity
        if suffix in {'y', 'dy', 'ey', 'ly', 'ry'}:
            opacity = 'DIFFUSE'
        elif suffix in {'l', 'd', 'r', 's', 'm', 'n'}:
            opacity = 'LOCKED'
        elif suffix in {'in', 'iin', 'ain'}:
            opacity = 'CHANNELED'
        else:
            opacity = 'BARE'
        
        # Hazard proximity: is any token within 2 positions a hazard HEAD?
        near_hazard = False
        for delta in range(-2, 3):
            neighbor_pos = pos + delta
            if 0 <= neighbor_pos < n_tokens_in_line and neighbor_pos != pos:
                n_mid = middles_in_line[neighbor_pos]
                n_hmt = decompose_middle_hmt(n_mid)
                if n_hmt and n_hmt[0] in hazard_heads:
                    near_hazard = True
                    break
        
        # Lane assignment (approximate: k/t-initial = QO tendency, e/o-initial = CHSH tendency)
        if b_head in ('k', 't', 'p', 'f'):
            lane = 'QO'
        elif b_head in ('e', 'o'):
            lane = 'CHSH'
        else:
            lane = 'NEUTRAL'
        
        bridge_b_occurrences[mid].append({
            'folio': folio,
            'line': line,
            'category': cat,
            'b_head': b_head,
            'suffix_mode': suf_mode,
            'opacity': opacity,
            'near_hazard': near_hazard,
            'line_quartile': line_quartile,
            'token_quartile': token_quartile,
            'lane': lane,
        })
# Aggregate B-side consequence vector per bridge MIDDLE
b_consequence = {}
for bm in sorted(bridge_set):
    occs = bridge_b_occurrences.get(bm, [])
    n_occ = len(occs)
    
    if n_occ == 0:
        b_consequence[bm] = {
            'n_b_occurrences': 0,
            'category': 'UNKNOWN',
            'head_dist': {h: 0.0 for h in HEAD_NAMES},
            'suffix_mode_dist': {'A': 0.0, 'B': 0.0, 'BARE': 0.0},
            'hazard_fraction': 0.0,
            'mean_line_quartile': 0.5,
            'mean_token_quartile': 0.5,
            'opacity_dist': {'LOCKED': 0.0, 'CHANNELED': 0.0, 'DIFFUSE': 0.0, 'BARE': 0.0},
            'lane_dist': {'QO': 0.0, 'CHSH': 0.0, 'NEUTRAL': 0.0},
        }
        continue
    
    # Category (majority vote)
    cat_counts = Counter(o['category'] for o in occs)
    primary_cat = cat_counts.most_common(1)[0][0]
    
    # HEAD distribution in B
    head_counts = Counter(o['b_head'] for o in occs)
    head_dist = {h: head_counts.get(h, 0) / n_occ for h in HEAD_NAMES}
    
    # Suffix mode distribution
    suf_counts = Counter(o['suffix_mode'] for o in occs)
    suf_dist = {m: suf_counts.get(m, 0) / n_occ for m in ['A', 'B', 'BARE']}
    
    # Hazard fraction
    hazard_frac = sum(1 for o in occs if o['near_hazard']) / n_occ
    
    # Position means
    mean_line_q = float(np.mean([o['line_quartile'] for o in occs]))
    mean_token_q = float(np.mean([o['token_quartile'] for o in occs]))
    
    # Opacity distribution
    op_counts = Counter(o['opacity'] for o in occs)
    op_dist = {op: op_counts.get(op, 0) / n_occ for op in ['LOCKED', 'CHANNELED', 'DIFFUSE', 'BARE']}
    
    # Lane distribution
    lane_counts = Counter(o['lane'] for o in occs)
    lane_dist = {l: lane_counts.get(l, 0) / n_occ for l in ['QO', 'CHSH', 'NEUTRAL']}
    
    b_consequence[bm] = {
        'n_b_occurrences': n_occ,
        'category': primary_cat,
        'head_dist': head_dist,
        'suffix_mode_dist': suf_dist,
        'hazard_fraction': hazard_frac,
        'mean_line_quartile': mean_line_q,
        'mean_token_quartile': mean_token_q,
        'opacity_dist': op_dist,
        'lane_dist': lane_dist,
    }

found_in_b = sum(1 for bm in bridge_set if b_consequence.get(bm, {}).get('n_b_occurrences', 0) > 0)
print(f"  Bridge MIDDLEs found in B: {found_in_b}/{len(bridge_set)}")
# ============================================================
# T3: A-context-to-B-consequence Mantel prediction
# ============================================================

print("\n[T3] A-context to B-consequence prediction (Mantel)...")

# Build vectors for bridge MIDDLEs that appear in both A and B
both_middles = [bm for bm in sorted(bridge_set)
                if a_context.get(bm, {}).get('n_folios', 0) > 0
                and b_consequence.get(bm, {}).get('n_b_occurrences', 0) > 0]
n_both = len(both_middles)
print(f"  Bridge MIDDLEs in both A and B: {n_both}")

# Build A-context feature vectors
# Features: folio_spread, section_bias_h, head_neighborhood (7 dims), n_pp_cooccur, n_ri_cooccur
# Total: 11 dims
def a_context_vector(bm):
    ctx = a_context[bm]
    vec = [ctx['folio_spread'], ctx['section_bias_h']]
    for h in HEAD_NAMES:
        vec.append(ctx['head_neighborhood'].get(h, 0.0))
    vec.append(ctx['n_pp_cooccur'] / 100.0)  # normalize
    vec.append(ctx['n_ri_cooccur'] / 100.0)
    return vec

# Build B-consequence feature vectors
# Features: head_dist (7), suffix_mode (3), hazard_frac, line_q, token_q, opacity (4), lane (3)
# Total: 21 dims
def b_consequence_vector(bm):
    con = b_consequence[bm]
    vec = []
    for h in HEAD_NAMES:
        vec.append(con['head_dist'].get(h, 0.0))
    for m in ['A', 'B', 'BARE']:
        vec.append(con['suffix_mode_dist'].get(m, 0.0))
    vec.append(con['hazard_fraction'])
    vec.append(con['mean_line_quartile'])
    vec.append(con['mean_token_quartile'])
    for op in ['LOCKED', 'CHANNELED', 'DIFFUSE', 'BARE']:
        vec.append(con['opacity_dist'].get(op, 0.0))
    for l in ['QO', 'CHSH', 'NEUTRAL']:
        vec.append(con['lane_dist'].get(l, 0.0))
    return vec

if n_both >= 5:
    a_vecs = np.array([a_context_vector(bm) for bm in both_middles])
    b_vecs = np.array([b_consequence_vector(bm) for bm in both_middles])
    
    # Compute pairwise distance matrices (cosine distance)
    a_dist_flat = pdist(a_vecs, metric='cosine')
    b_dist_flat = pdist(b_vecs, metric='cosine')
    
    # Replace NaN with max distance
    a_dist_flat = np.nan_to_num(a_dist_flat, nan=1.0)
    b_dist_flat = np.nan_to_num(b_dist_flat, nan=1.0)
    
    # Mantel test
    mantel_r, mantel_p = mantel_test(list(a_dist_flat), list(b_dist_flat), n_perm=N_PERM)
    print(f"  Mantel r = {mantel_r:.4f}, p = {mantel_p:.4f}")
    
    # Per-feature partial correlations (A feature i vs B feature j)
    n_a_feats = a_vecs.shape[1]
    n_b_feats = b_vecs.shape[1]
    
    a_feat_names = ['folio_spread', 'section_bias'] + [f'head_{h}' for h in HEAD_NAMES] + ['n_pp_co', 'n_ri_co']
    b_feat_names = ([f'b_head_{h}' for h in HEAD_NAMES] + 
                    ['suf_A', 'suf_B', 'suf_BARE'] +
                    ['hazard', 'line_q', 'token_q'] +
                    ['op_LOCKED', 'op_CHAN', 'op_DIFF', 'op_BARE'] +
                    ['lane_QO', 'lane_CHSH', 'lane_NEUT'])
    
    sig_pairs = []
    for i in range(n_a_feats):
        for j in range(n_b_feats):
            a_col = a_vecs[:, i]
            b_col = b_vecs[:, j]
            if np.std(a_col) < 1e-10 or np.std(b_col) < 1e-10:
                continue
            r, p = stats.spearmanr(a_col, b_col)
            if not np.isnan(r) and abs(r) > 0.25 and p < 0.005:
                sig_pairs.append({
                    'a_feature': a_feat_names[i],
                    'b_feature': b_feat_names[j],
                    'rho': float(r),
                    'p': float(p),
                })
    
    sig_pairs.sort(key=lambda x: -abs(x['rho']))
    print(f"  Significant A-B feature pairs (|rho|>0.25, p<0.005): {len(sig_pairs)}")
    for sp in sig_pairs[:5]:
        print(f"    {sp['a_feature']} -> {sp['b_feature']}: rho={sp['rho']:.3f} p={sp['p']:.4f}")
else:
    mantel_r = 0.0
    mantel_p = 1.0
    sig_pairs = []
    a_feat_names = []
    b_feat_names = []
    print("  Too few bridge MIDDLEs in both A and B for Mantel test")
# ============================================================
# T4: HEAD redistribution analysis
# ============================================================

print("\n[T4] HEAD redistribution analysis...")

# For each bridge MIDDLE: compare HEAD in A vs HEAD in B
head_a_to_b = defaultdict(lambda: defaultdict(int))
for bm in both_middles:
    # A-side dominant HEAD
    a_heads = a_context[bm]['head_neighborhood']
    a_dominant = max(a_heads, key=a_heads.get) if a_heads else 'unknown'
    
    # B-side dominant HEAD
    b_heads = b_consequence[bm]['head_dist']
    b_dominant = max(b_heads, key=b_heads.get) if b_heads else 'unknown'
    
    head_a_to_b[a_dominant][b_dominant] += 1

# Build contingency table for chi-squared
used_heads = sorted(set(list(head_a_to_b.keys()) + 
                        [h for row in head_a_to_b.values() for h in row.keys()]))
contingency_head = np.zeros((len(used_heads), len(used_heads)), dtype=int)
for i, ah in enumerate(used_heads):
    for j, bh in enumerate(used_heads):
        contingency_head[i, j] = head_a_to_b[ah][bh]

# Remove zero rows/cols
row_sums = contingency_head.sum(axis=1)
col_sums = contingency_head.sum(axis=0)
keep_rows = row_sums > 0
keep_cols = col_sums > 0
contingency_trimmed = contingency_head[np.ix_(keep_rows, keep_cols)]

if contingency_trimmed.shape[0] >= 2 and contingency_trimmed.shape[1] >= 2:
    chi2_head, p_head, dof_head, _ = stats.chi2_contingency(contingency_trimmed)
    n_head = contingency_trimmed.sum()
    v_head = float(np.sqrt(chi2_head / (n_head * (min(contingency_trimmed.shape) - 1)))) if n_head > 0 else 0.0
else:
    chi2_head, p_head, v_head = 0.0, 1.0, 0.0

# Self-transition rate (HEAD same in A and B)
self_count = sum(head_a_to_b[h][h] for h in used_heads)
total_transitions = sum(sum(row.values()) for row in head_a_to_b.values())
self_rate = self_count / total_transitions if total_transitions > 0 else 0.0

print(f"  HEAD A->B chi2={chi2_head:.2f}, p={p_head:.6f}, V={v_head:.4f}")
print(f"  Self-transition rate: {self_rate:.4f} ({self_count}/{total_transitions})")
print(f"  Transition table:")
for ah in used_heads:
    if sum(head_a_to_b[ah].values()) > 0:
        transitions = ", ".join(f"{bh}:{head_a_to_b[ah][bh]}" 
                               for bh in used_heads if head_a_to_b[ah][bh] > 0)
        print(f"    A-{ah} -> {transitions}")
# ============================================================
# T5: Bridge MIDDLE functional grouping
# ============================================================

print("\n[T5] Bridge MIDDLE functional grouping...")

if n_both >= 5:
    from sklearn.metrics import silhouette_score
    
    # Cluster bridge MIDDLEs by B-consequence vectors
    b_dist_matrix = squareform(b_dist_flat)
    
    func_sil = {}
    for k in range(2, min(8, n_both)):
        Z_func = linkage(b_dist_flat, method='ward')
        labels = fcluster(Z_func, k, criterion='maxclust')
        sil = silhouette_score(b_dist_matrix, labels, metric='precomputed')
        func_sil[k] = float(sil)
    
    func_best_k = max(func_sil, key=func_sil.get) if func_sil else 2
    func_best_sil = func_sil.get(func_best_k, 0.0)
    
    Z_final = linkage(b_dist_flat, method='ward')
    func_labels = fcluster(Z_final, func_best_k, criterion='maxclust')
    bridge_func_group = {both_middles[i]: int(func_labels[i]) for i in range(n_both)}
    
    # Characterize functional groups
    func_profiles = {}
    for g in sorted(set(func_labels)):
        g_middles = [bm for bm, gl in bridge_func_group.items() if gl == g]
        
        # Mean B-consequence
        g_vecs = np.array([b_consequence_vector(bm) for bm in g_middles])
        mean_vec = g_vecs.mean(axis=0)
        
        # Category distribution
        cat_counts = Counter(b_consequence[bm]['category'] for bm in g_middles)
        
        # Atom structure via HMT decomposition
        hmt_heads = Counter()
        for bm in g_middles:
            hmt = decompose_middle_hmt(bm)
            if hmt:
                hmt_heads[hmt[0]] += 1
        
        func_profiles[int(g)] = {
            'n_middles': len(g_middles),
            'middles': g_middles[:10],  # truncate for readability
            'top_categories': dict(cat_counts.most_common(3)),
            'hmt_heads': dict(hmt_heads.most_common(5)),
            'mean_hazard_frac': float(np.mean([b_consequence[bm]['hazard_fraction'] for bm in g_middles])),
            'mean_line_q': float(np.mean([b_consequence[bm]['mean_line_quartile'] for bm in g_middles])),
        }
    
    print(f"  Best functional k={func_best_k}, silhouette={func_best_sil:.4f}")
    for g, prof in func_profiles.items():
        print(f"  Group {g} (n={prof['n_middles']}): cats={prof['top_categories']}, "
              f"hazard={prof['mean_hazard_frac']:.3f}, line_q={prof['mean_line_q']:.3f}")
else:
    func_best_k = 0
    func_best_sil = 0.0
    func_sil = {}
    bridge_func_group = {}
    func_profiles = {}
# ============================================================
# OUTPUT
# ============================================================

elapsed = time.time() - t0
print(f"\n  Total time: {elapsed:.1f}s")

output = {
    'metadata': {
        'phase': 626,
        'script': 2,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'n_bridge_middles': len(bridge_set),
        'n_in_a': found_in_a,
        'n_in_b': found_in_b,
        'n_in_both': n_both,
        'elapsed_s': round(elapsed, 1),
    },
    'T1_a_context': {bm: round_floats(ctx) for bm, ctx in a_context.items()},
    'T2_b_consequence': {bm: round_floats(con) for bm, con in b_consequence.items()},
    'T3_mantel': {
        'r': round(mantel_r, 6),
        'p': round(mantel_p, 6),
        'n_middles': n_both,
        'significant_pairs': round_floats(sig_pairs[:20]),
        'n_significant': len(sig_pairs),
    },
    'T4_head_redistribution': {
        'chi2': round(chi2_head, 4),
        'p': round(p_head, 6),
        'cramers_v': round(v_head, 4),
        'self_transition_rate': round(self_rate, 4),
        'transition_table': {ah: dict(bh_counts) for ah, bh_counts in head_a_to_b.items()},
    },
    'T5_functional_groups': {
        'silhouette_by_k': {str(k): round(v, 6) for k, v in func_sil.items()},
        'best_k': func_best_k,
        'best_silhouette': round(func_best_sil, 6),
        'group_profiles': round_floats(func_profiles),
        'bridge_group_assignment': bridge_func_group,
    },
}

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
with open(RESULTS_DIR / 'bridge_decomposition.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n  Output: {RESULTS_DIR / 'bridge_decomposition.json'}")
print("  DONE")