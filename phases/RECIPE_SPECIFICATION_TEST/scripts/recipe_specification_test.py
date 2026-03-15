#!/usr/bin/env python3
"""
Phase 588: RECIPE_SPECIFICATION_TEST
Are A folios preparation specifications (recipes)?

Tests:
  T1: PP content predicts B-side similarity (size-controlled)
  T2: Folio-restricted PP MIDDLEs as recipe signatures
  T3: Specialization vs generalization (category diversity)
"""

import sys, json, functools, warnings, re, time
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
warnings.filterwarnings('ignore')

from scripts.voynich import (Transcript, Morphology, RecordAnalyzer,
                              CategoryClassifier, decompose_middle_hmt,
                              load_middle_classes)
from scipy import stats
from scipy.spatial.distance import cosine as cosine_dist

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
t0 = time.time()

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']
HEADS = ['k', 't', 'a', 'e', 'o', 'headless']
FEATURE_NAMES = CATEGORIES + [f'HEAD_{h}' for h in HEADS] + ['k_initial', 'hazard']

# ============================================================
# STAGE 0: Data Loading & Pre-computation
# ============================================================

print("=" * 70)
print("Phase 588: RECIPE_SPECIFICATION_TEST")
print("Are A Folios Preparation Specifications?")
print("=" * 70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()
cc = CategoryClassifier()
ri_middles, pp_middles = load_middle_classes()

# Load forbidden transitions
with open(PROJECT_ROOT / 'phases' / '15-20_kernel_grammar' /
          'phase18a_forbidden_inventory.json') as f:
    forbidden_data = json.load(f)
FORBIDDEN_PAIRS = [(t['source'], t['target']) for t in forbidden_data['transitions']]
print(f"  Loaded {len(FORBIDDEN_PAIRS)} forbidden transitions")

# --- Build C475 adjacency graph ---
print("\n  Building C475 compatibility graph...")
line_middles = defaultdict(set)
all_middles_set = set()

for token in tx.currier_a():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    if m.middle:
        key = (token.folio, token.line)
        line_middles[key].add(m.middle)
        all_middles_set.add(m.middle)

# Build adjacency as dict-of-sets
compat_adj = defaultdict(set)
for key, middles in line_middles.items():
    mid_list = list(middles)
    for i in range(len(mid_list)):
        for j in range(i + 1, len(mid_list)):
            compat_adj[mid_list[i]].add(mid_list[j])
            compat_adj[mid_list[j]].add(mid_list[i])

n_all_middles = len(all_middles_set)
n_all_edges = sum(len(v) for v in compat_adj.values()) // 2
print(f"  Total MIDDLEs: {n_all_middles}")
print(f"  Total C475 edges: {n_all_edges}")

# PP-PP restricted density
pp_in_graph = pp_middles & all_middles_set
n_pp = len(pp_in_graph)
n_pp_edges = 0
for m in pp_in_graph:
    n_pp_edges += len(compat_adj.get(m, set()) & pp_in_graph)
n_pp_edges //= 2
pp_pp_density = n_pp_edges / (n_pp * (n_pp - 1) // 2) if n_pp > 1 else 0
print(f"  PP MIDDLEs in graph: {n_pp}")
print(f"  PP-PP edges: {n_pp_edges}")
print(f"  PP-PP density: {pp_pp_density:.4f}")

# --- Build B token inventory with morphology ---
print("\n  Building B token inventory...")
b_tokens = {}
for token in tx.currier_b():
    w = token.word
    if w in b_tokens:
        continue
    m = morph.extract(w)
    if m.middle:
        b_tokens[w] = (m.prefix, m.middle, m.suffix)

b_middles_set = set(mid for _, mid, _ in b_tokens.values())
b_prefixes_set = set(pref for pref, _, _ in b_tokens.values() if pref)
b_suffixes_set = set(suf for _, _, suf in b_tokens.values() if suf)
print(f"  B token types: {len(b_tokens)}")

# Pre-compute B token features
b_token_category = {}
b_token_head = {}
b_token_k_initial = {}

for tok, (pref, mid, suf) in b_tokens.items():
    cat = cc.classify(mid)
    b_token_category[tok] = cat
    head, _, _, _ = decompose_middle_hmt(mid)
    b_token_head[tok] = head if head else 'headless'
    b_token_k_initial[tok] = mid.startswith('k')

# --- Build A record morphology and per-folio PP sets ---
print("  Building A record morphology...")

def get_section(folio):
    match = re.search(r'\d+', folio)
    if not match:
        return 'OTHER'
    num = int(match.group())
    if num <= 11: return 'HERBAL_1'
    elif num <= 25: return 'HERBAL_2'
    elif num <= 38: return 'HERBAL_3'
    elif num <= 66: return 'HERBAL_4'
    else: return 'PHARMA'

a_records = []
folio_section_map = {}
folio_pp_sets = defaultdict(set)
folio_prefix_sets = defaultdict(set)
folio_suffix_sets = defaultdict(set)

for record in analyzer.iter_records():
    prefixes = set()
    middles = set()
    suffixes = set()
    pp_mids = []
    for t in record.tokens:
        m = morph.extract(t.word)
        if m.prefix:
            prefixes.add(m.prefix)
        if m.middle:
            middles.add(m.middle)
            if m.middle in pp_middles:
                pp_mids.append(m.middle)
        if m.suffix:
            suffixes.add(m.suffix)

    section = get_section(record.folio)
    folio_section_map[record.folio] = section

    a_records.append({
        'folio': record.folio,
        'line': record.line,
        'section': section,
        'prefixes': prefixes,
        'middles': middles,
        'suffixes': suffixes,
        'pp_middles': set(pp_mids),
    })

    folio_pp_sets[record.folio].update(pp_mids)
    folio_prefix_sets[record.folio].update(prefixes)
    folio_suffix_sets[record.folio].update(suffixes)

all_folios = sorted(folio_pp_sets.keys())
n_folios = len(all_folios)
pp_sizes = [len(folio_pp_sets[f]) for f in all_folios]
print(f"  A records: {len(a_records)}")
print(f"  Folios: {n_folios}")
print(f"  PP pool sizes: mean={np.mean(pp_sizes):.1f}, "
      f"median={np.median(pp_sizes):.0f}, range=[{min(pp_sizes)}, {max(pp_sizes)}]")

# --- Classify PP MIDDLEs by folio spread ---
pp_folio_spread = Counter()
for folio, pp_set in folio_pp_sets.items():
    for mid in pp_set:
        pp_folio_spread[mid] += 1

# Define hub MIDDLEs: top 20% by folio spread
spread_values = sorted(pp_folio_spread.values(), reverse=True)
hub_threshold = spread_values[len(spread_values) // 5] if spread_values else 1
hub_middles = {m for m, s in pp_folio_spread.items() if s >= hub_threshold}
print(f"  Hub threshold: {hub_threshold} folios (top 20%)")
print(f"  Hub PP MIDDLEs: {len(hub_middles)}")

restricted_middles = {m for m, s in pp_folio_spread.items() if s <= 2}
multi_middles = {m for m, s in pp_folio_spread.items() if s >= 10}
print(f"  Folio-restricted PPs (<=2 folios): {len(restricted_middles)}")
print(f"  Multi-folio PPs (>=10 folios): {len(multi_middles)}")

# --- Compute per-PP-MIDDLE category profile ---
print("  Computing per-PP-MIDDLE category profiles...")
pp_middle_category = {}
for mid in pp_in_graph:
    cat = cc.classify(mid)
    pp_middle_category[mid] = cat

# --- Compute B-side signature function ---
def compute_signature(legal_tokens):
    """Compute 16-dim B-side operational signature from a set of legal B tokens."""
    n = len(legal_tokens)
    if n == 0:
        return np.zeros(16)

    cat_counts = Counter()
    for tok in legal_tokens:
        cat = b_token_category.get(tok)
        if cat:
            cat_counts[cat] += 1
    cat_total = sum(cat_counts.values())
    cat_vec = [cat_counts.get(c, 0) / cat_total if cat_total > 0 else 0
               for c in CATEGORIES]

    head_counts = Counter()
    for tok in legal_tokens:
        head_counts[b_token_head.get(tok, 'headless')] += 1
    head_vec = [head_counts.get(h, 0) / n for h in HEADS]

    k_init = sum(1 for tok in legal_tokens if b_token_k_initial.get(tok, False)) / n
    hazard = sum(1 for src, tgt in FORBIDDEN_PAIRS
                 if src in legal_tokens and tgt in legal_tokens)

    return np.array(cat_vec + head_vec + [k_init, hazard])


def compute_c502a_survivors(pp_mid_set, prefix_set, suffix_set):
    """C502.a three-axis filter: return set of legal B tokens."""
    pp_mids_in_b = pp_mid_set & b_middles_set
    pp_prefs = prefix_set & b_prefixes_set
    pp_sufs = suffix_set & b_suffixes_set

    legal = set()
    for tok, (pref, mid, suf) in b_tokens.items():
        if mid in pp_mids_in_b:
            pref_ok = (pref is None or pref in pp_prefs)
            suf_ok = (suf is None or suf in pp_sufs)
            if pref_ok and suf_ok:
                legal.add(tok)
    return legal


# --- Compute folio-level B-side signatures ---
print("\n  Computing folio-level B-side signatures...")
folio_signatures = {}
folio_survivors = {}

for folio in all_folios:
    legal = compute_c502a_survivors(
        folio_pp_sets[folio], folio_prefix_sets[folio], folio_suffix_sets[folio])
    folio_signatures[folio] = compute_signature(legal)
    folio_survivors[folio] = legal

survivor_sizes = [len(folio_survivors[f]) for f in all_folios]
print(f"  Folio survivor sizes: mean={np.mean(survivor_sizes):.1f}, "
      f"median={np.median(survivor_sizes):.0f}, range=[{min(survivor_sizes)}, {max(survivor_sizes)}]")

folio_sig_matrix = np.array([folio_signatures[f] for f in all_folios])
folio_sections = [folio_section_map[f] for f in all_folios]

print(f"\n  Stage 0 complete ({time.time()-t0:.1f}s)")

# ============================================================
# TEST 1: PP Content Predicts B-Side Similarity (Size-Controlled)
# ============================================================

print(f"\n{'='*70}")
print("  TEST 1: PP Content Predicts B-Side Similarity")
print(f"{'='*70}")

# Compute all folio pairs
pp_jaccards = []
bside_cosines = []
mean_pool_sizes = []
hub_fractions = []
same_sections = []

for i in range(n_folios):
    for j in range(i + 1, n_folios):
        fi, fj = all_folios[i], all_folios[j]
        pp_i, pp_j = folio_pp_sets[fi], folio_pp_sets[fj]

        # PP Jaccard
        intersection = pp_i & pp_j
        union = pp_i | pp_j
        jaccard = len(intersection) / len(union) if union else 0
        pp_jaccards.append(jaccard)

        # B-side cosine similarity
        sig_i, sig_j = folio_sig_matrix[i], folio_sig_matrix[j]
        if np.any(sig_i) and np.any(sig_j):
            cos_sim = 1.0 - cosine_dist(sig_i, sig_j)
        else:
            cos_sim = 0.0
        bside_cosines.append(cos_sim)

        # Controls
        mean_size = (len(pp_i) + len(pp_j)) / 2.0
        mean_pool_sizes.append(mean_size)

        hub_frac = len(intersection & hub_middles) / len(intersection) if intersection else 0
        hub_fractions.append(hub_frac)

        same_sec = 1.0 if folio_section_map[fi] == folio_section_map[fj] else 0.0
        same_sections.append(same_sec)

pp_jaccards = np.array(pp_jaccards)
bside_cosines = np.array(bside_cosines)
mean_pool_sizes = np.array(mean_pool_sizes)
hub_fractions = np.array(hub_fractions)
same_sections = np.array(same_sections)

n_pairs = len(pp_jaccards)
print(f"  Folio pairs: {n_pairs}")
print(f"  PP Jaccard: mean={pp_jaccards.mean():.4f}, "
      f"std={pp_jaccards.std():.4f}, range=[{pp_jaccards.min():.4f}, {pp_jaccards.max():.4f}]")
print(f"  B-side cosine sim: mean={bside_cosines.mean():.4f}, "
      f"std={bside_cosines.std():.4f}")

# Raw Spearman
raw_rho, raw_p = stats.spearmanr(pp_jaccards, bside_cosines)
print(f"\n  Raw Spearman: rho={raw_rho:.4f}, p={raw_p:.2e}")

# Partial correlation controlling for size, hub fraction, section
# Use rank-based partial correlation:
# Residualize both X and Y against controls, then correlate residuals
from numpy.linalg import lstsq

controls = np.column_stack([mean_pool_sizes, hub_fractions, same_sections])

# Rank-transform for Spearman
rank_jaccard = stats.rankdata(pp_jaccards)
rank_cosine = stats.rankdata(bside_cosines)

# Residualize jaccard ranks against controls
A_mat = np.column_stack([controls, np.ones(n_pairs)])
res_jaccard = rank_jaccard - A_mat @ lstsq(A_mat, rank_jaccard, rcond=None)[0]
res_cosine = rank_cosine - A_mat @ lstsq(A_mat, rank_cosine, rcond=None)[0]

# Partial Spearman = Pearson of residualized ranks
partial_rho, partial_p = stats.pearsonr(res_jaccard, res_cosine)
print(f"  Partial Spearman (controlling size, hub, section): rho={partial_rho:.4f}, p={partial_p:.2e}")

# Also report within-section and between-section separately
within_mask = same_sections == 1
between_mask = same_sections == 0

if within_mask.sum() > 10:
    within_rho, within_p = stats.spearmanr(pp_jaccards[within_mask], bside_cosines[within_mask])
    print(f"  Within-section Spearman: rho={within_rho:.4f}, p={within_p:.2e} (n={int(within_mask.sum())})")
else:
    within_rho, within_p = float('nan'), float('nan')

if between_mask.sum() > 10:
    between_rho, between_p = stats.spearmanr(pp_jaccards[between_mask], bside_cosines[between_mask])
    print(f"  Between-section Spearman: rho={between_rho:.4f}, p={between_p:.2e} (n={int(between_mask.sum())})")
else:
    between_rho, between_p = float('nan'), float('nan')

t1_pass = bool(partial_rho > 0.2 and partial_p < 0.001)
print(f"\n  T1 verdict: {'PASS' if t1_pass else 'FAIL'} "
      f"(partial rho={partial_rho:.4f}, threshold=0.2)")

# ============================================================
# TEST 2: Folio-Restricted PP MIDDLEs as Recipe Signatures
# ============================================================

print(f"\n{'='*70}")
print("  TEST 2: Folio-Restricted PP MIDDLEs as Recipe Signatures")
print(f"{'='*70}")

# Per-folio counts of restricted and multi-folio PPs
qualifying_folios = []
for folio in all_folios:
    pp_set = folio_pp_sets[folio]
    n_restricted = len(pp_set & restricted_middles)
    n_multi = len(pp_set & multi_middles)
    if n_restricted >= 8 and n_multi >= 8:
        qualifying_folios.append(folio)

print(f"  Qualifying folios (>=8 restricted AND >=8 multi): {len(qualifying_folios)}/{n_folios}")

if len(qualifying_folios) < 10:
    print("  WARNING: Too few qualifying folios for reliable test")
    # Relax threshold to >=4
    qualifying_folios = []
    for folio in all_folios:
        pp_set = folio_pp_sets[folio]
        n_restricted = len(pp_set & restricted_middles)
        n_multi = len(pp_set & multi_middles)
        if n_restricted >= 4 and n_multi >= 4:
            qualifying_folios.append(folio)
    print(f"  Relaxed threshold (>=4): {len(qualifying_folios)} qualifying folios")

# Report per-folio restricted/multi counts
for_report = []
for folio in all_folios:
    pp_set = folio_pp_sets[folio]
    n_r = len(pp_set & restricted_middles)
    n_m = len(pp_set & multi_middles)
    for_report.append((folio, len(pp_set), n_r, n_m))
n_r_all = [x[2] for x in for_report]
n_m_all = [x[3] for x in for_report]
print(f"  Restricted PPs per folio: mean={np.mean(n_r_all):.1f}, "
      f"median={np.median(n_r_all):.0f}, range=[{min(n_r_all)}, {max(n_r_all)}]")
print(f"  Multi-folio PPs per folio: mean={np.mean(n_m_all):.1f}, "
      f"median={np.median(n_m_all):.0f}, range=[{min(n_m_all)}, {max(n_m_all)}]")

t2_result = {}

if len(qualifying_folios) >= 10:
    # Compute restricted-only and multi-only B-side signatures
    print("  Computing restricted-only and multi-only signatures...")
    restricted_sigs = {}
    multi_sigs = {}

    for folio in qualifying_folios:
        pp_set = folio_pp_sets[folio]
        pref_set = folio_prefix_sets[folio]
        suf_set = folio_suffix_sets[folio]

        r_pp = pp_set & restricted_middles
        m_pp = pp_set & multi_middles

        r_legal = compute_c502a_survivors(r_pp, pref_set, suf_set)
        m_legal = compute_c502a_survivors(m_pp, pref_set, suf_set)

        restricted_sigs[folio] = compute_signature(r_legal)
        multi_sigs[folio] = compute_signature(m_legal)

    # Between-folio distances
    restricted_dists = []
    multi_dists = []

    for i in range(len(qualifying_folios)):
        for j in range(i + 1, len(qualifying_folios)):
            fi, fj = qualifying_folios[i], qualifying_folios[j]

            r_si, r_sj = restricted_sigs[fi], restricted_sigs[fj]
            m_si, m_sj = multi_sigs[fi], multi_sigs[fj]

            if np.any(r_si) and np.any(r_sj):
                restricted_dists.append(cosine_dist(r_si, r_sj))
            if np.any(m_si) and np.any(m_sj):
                multi_dists.append(cosine_dist(m_si, m_sj))

    restricted_dists = np.array(restricted_dists)
    multi_dists = np.array(multi_dists)

    print(f"  Restricted-PP distances: mean={restricted_dists.mean():.4f}, n={len(restricted_dists)}")
    print(f"  Multi-folio-PP distances: mean={multi_dists.mean():.4f}, n={len(multi_dists)}")

    # Mann-Whitney U: restricted > multi?
    u_stat, u_p_two = stats.mannwhitneyu(restricted_dists, multi_dists, alternative='greater')
    cohens_d = (restricted_dists.mean() - multi_dists.mean()) / np.sqrt(
        (restricted_dists.std()**2 + multi_dists.std()**2) / 2)

    print(f"  Mann-Whitney U: U={u_stat:.0f}, p(one-sided)={u_p_two:.2e}")
    print(f"  Cohen's d: {cohens_d:.4f}")

    t2_pass = bool(u_p_two < 0.05 and cohens_d > 0)
    print(f"\n  T2 verdict: {'PASS' if t2_pass else 'FAIL'} "
          f"(restricted > multi, p={u_p_two:.2e})")

    # Correlation: n_restricted per folio vs B-side distinctiveness
    folio_distinctiveness = {}
    for i, fi in enumerate(all_folios):
        dists = []
        for j, fj in enumerate(all_folios):
            if i != j:
                si, sj = folio_sig_matrix[i], folio_sig_matrix[j]
                if np.any(si) and np.any(sj):
                    dists.append(cosine_dist(si, sj))
        folio_distinctiveness[fi] = np.mean(dists) if dists else 0

    n_restricted_per_folio = [len(folio_pp_sets[f] & restricted_middles) for f in all_folios]
    distinctiveness_values = [folio_distinctiveness[f] for f in all_folios]
    distinct_rho, distinct_p = stats.spearmanr(n_restricted_per_folio, distinctiveness_values)
    print(f"  N_restricted vs distinctiveness: rho={distinct_rho:.4f}, p={distinct_p:.2e}")

    t2_result = {
        'n_qualifying': len(qualifying_folios),
        'restricted_mean_dist': float(restricted_dists.mean()),
        'multi_mean_dist': float(multi_dists.mean()),
        'U': float(u_stat),
        'p_one_sided': float(u_p_two),
        'cohens_d': float(cohens_d),
        'passed': t2_pass,
        'distinctiveness_rho': float(distinct_rho),
        'distinctiveness_p': float(distinct_p),
    }
else:
    print("  SKIPPED: insufficient qualifying folios")
    t2_pass = False
    t2_result = {'skipped': True, 'n_qualifying': len(qualifying_folios)}

# ============================================================
# TEST 3: Specialization vs Generalization (Category Diversity)
# ============================================================

print(f"\n{'='*70}")
print("  TEST 3: Specialization vs Generalization")
print(f"{'='*70}")

rng = np.random.default_rng(42)

def compute_category_entropy(pp_set):
    """Shannon entropy of category distribution for a set of PP MIDDLEs."""
    cat_counts = Counter()
    for mid in pp_set:
        cat = pp_middle_category.get(mid)
        if cat:
            cat_counts[cat] += 1
    total = sum(cat_counts.values())
    if total == 0:
        return 0.0
    probs = np.array([cat_counts.get(c, 0) / total for c in CATEGORIES])
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log2(probs)))

# Build PP MIDDLE list with folio-spread weights for coverage-matched null
pp_list = sorted(pp_in_graph)
pp_weights = np.array([pp_folio_spread.get(m, 1) for m in pp_list], dtype=float)
pp_weights /= pp_weights.sum()

# Compute real folio entropies
print("  Computing folio category entropies...")
folio_entropies = {}
folio_n_categories = {}
for folio in all_folios:
    pp_set = folio_pp_sets[folio] & pp_in_graph
    h = compute_category_entropy(pp_set)
    folio_entropies[folio] = h

    cat_counts = Counter()
    for mid in pp_set:
        cat = pp_middle_category.get(mid)
        if cat:
            cat_counts[cat] += 1
    folio_n_categories[folio] = len(cat_counts)

real_entropies = np.array([folio_entropies[f] for f in all_folios])
real_n_cats = np.array([folio_n_categories[f] for f in all_folios])
print(f"  Real entropy: mean={real_entropies.mean():.4f}, std={real_entropies.std():.4f}")
print(f"  Real categories covered: mean={real_n_cats.mean():.1f}")

# Coverage-matched null: for each folio, draw 1000 random PP subsets
# weighted by folio spread (matching coverage optimization)
print("  Computing coverage-matched null (1000 draws per folio)...")
N_NULL = 1000
z_scores = []
null_entropies_all = []

for folio in all_folios:
    pp_set = folio_pp_sets[folio] & pp_in_graph
    n_draw = len(pp_set)
    if n_draw < 2:
        z_scores.append(0.0)
        continue

    null_entropies = []
    for _ in range(N_NULL):
        # Draw n_draw PP MIDDLEs weighted by folio spread
        drawn_indices = rng.choice(len(pp_list), size=n_draw, replace=False, p=pp_weights)
        drawn_set = {pp_list[idx] for idx in drawn_indices}
        null_entropies.append(compute_category_entropy(drawn_set))

    null_mean = np.mean(null_entropies)
    null_std = np.std(null_entropies)
    null_entropies_all.extend(null_entropies)

    if null_std > 0:
        z = (folio_entropies[folio] - null_mean) / null_std
    else:
        z = 0.0
    z_scores.append(z)

z_scores = np.array(z_scores)
print(f"  z-scores: mean={z_scores.mean():.4f}, std={z_scores.std():.4f}")
print(f"  z < -2: {(z_scores < -2).sum()}/{n_folios} folios")
print(f"  |z| < 1: {(np.abs(z_scores) < 1).sum()}/{n_folios} folios")
print(f"  z > 2: {(z_scores > 2).sum()}/{n_folios} folios")

null_entropy_mean = np.mean(null_entropies_all)
print(f"  Null entropy mean: {null_entropy_mean:.4f}")
print(f"  Real entropy mean: {real_entropies.mean():.4f}")
print(f"  Difference: {real_entropies.mean() - null_entropy_mean:.4f}")

# Verdict
mean_z = float(z_scores.mean())
if mean_z < -2.0:
    t3_verdict = "SPECIALIZED"
    t3_pass = True
elif abs(mean_z) < 1.0:
    t3_verdict = "COVERAGE_MATCHED"
    t3_pass = False  # not specialized
else:
    t3_verdict = "AMBIGUOUS"
    t3_pass = False

print(f"\n  T3 verdict: {t3_verdict} (mean z={mean_z:.4f})")

# Also compute Gini coefficient
def gini_coefficient(values):
    """Gini coefficient of a distribution."""
    values = np.sort(values)
    n = len(values)
    if n == 0 or values.sum() == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return float(2.0 * np.sum(index * values) / (n * values.sum()) - (n + 1) / n)

folio_ginis = []
null_ginis = []
for folio in all_folios:
    pp_set = folio_pp_sets[folio] & pp_in_graph
    cat_counts = Counter()
    for mid in pp_set:
        cat = pp_middle_category.get(mid)
        if cat:
            cat_counts[cat] += 1
    dist = np.array([cat_counts.get(c, 0) for c in CATEGORIES], dtype=float)
    folio_ginis.append(gini_coefficient(dist))

# Null Ginis
for _ in range(1000):
    n_draw = int(np.median(pp_sizes))
    drawn_indices = rng.choice(len(pp_list), size=min(n_draw, len(pp_list)),
                               replace=False, p=pp_weights)
    drawn_set = {pp_list[idx] for idx in drawn_indices}
    cat_counts = Counter()
    for mid in drawn_set:
        cat = pp_middle_category.get(mid)
        if cat:
            cat_counts[cat] += 1
    dist = np.array([cat_counts.get(c, 0) for c in CATEGORIES], dtype=float)
    null_ginis.append(gini_coefficient(dist))

print(f"  Real Gini: mean={np.mean(folio_ginis):.4f}")
print(f"  Null Gini: mean={np.mean(null_ginis):.4f}")

# ============================================================
# SUMMARY & VERDICT
# ============================================================

print(f"\n{'='*70}")
print("  SUMMARY")
print(f"{'='*70}")

# Overall verdict
if t1_pass and t3_verdict == "SPECIALIZED":
    verdict = "RECIPE_SPECIFICATION_SUPPORTED"
elif t1_pass and t3_verdict == "COVERAGE_MATCHED":
    verdict = "CONTENT_RELEVANT_NOT_SPECIALIZED"
elif not t1_pass and t3_verdict == "SPECIALIZED":
    verdict = "SPECIALIZED_BUT_NOT_OPERATIONAL"
else:
    verdict = "COVERAGE_OPTIMIZED_POOL"

print(f"  T1 (content→B-side): partial rho={partial_rho:.4f} → {'PASS' if t1_pass else 'FAIL'}")
print(f"  T2 (restricted PPs): {'PASS' if t2_pass else 'FAIL'}")
print(f"  T3 (specialization): {t3_verdict} (mean z={mean_z:.4f})")
print(f"\n  VERDICT: {verdict}")
print(f"\n  Total runtime: {time.time()-t0:.1f}s")

# ============================================================
# Save results
# ============================================================

results = {
    'phase': 588,
    'test': 'RECIPE_SPECIFICATION_TEST',
    'metadata': {
        'n_folios': n_folios,
        'n_pp_middles': n_pp,
        'pp_pp_density': float(pp_pp_density),
        'pp_pp_edges': n_pp_edges,
        'mean_pp_pool_size': float(np.mean(pp_sizes)),
        'hub_threshold': int(hub_threshold),
        'n_hub_middles': len(hub_middles),
        'n_restricted_middles': len(restricted_middles),
        'n_multi_middles': len(multi_middles),
    },
    'T1_content_bside': {
        'n_pairs': n_pairs,
        'pp_jaccard_mean': float(pp_jaccards.mean()),
        'pp_jaccard_std': float(pp_jaccards.std()),
        'bside_cosine_mean': float(bside_cosines.mean()),
        'bside_cosine_std': float(bside_cosines.std()),
        'raw_spearman_rho': float(raw_rho),
        'raw_spearman_p': float(raw_p),
        'partial_spearman_rho': float(partial_rho),
        'partial_spearman_p': float(partial_p),
        'within_section_rho': float(within_rho) if not np.isnan(within_rho) else None,
        'within_section_p': float(within_p) if not np.isnan(within_p) else None,
        'between_section_rho': float(between_rho) if not np.isnan(between_rho) else None,
        'between_section_p': float(between_p) if not np.isnan(between_p) else None,
        'passed': t1_pass,
    },
    'T2_restricted_pp': t2_result,
    'T3_specialization': {
        'real_entropy_mean': float(real_entropies.mean()),
        'real_entropy_std': float(real_entropies.std()),
        'null_entropy_mean': float(null_entropy_mean),
        'mean_z': float(mean_z),
        'z_std': float(z_scores.std()),
        'n_specialized': int((z_scores < -2).sum()),
        'n_neutral': int((np.abs(z_scores) < 1).sum()),
        'n_generalized': int((z_scores > 2).sum()),
        'real_gini_mean': float(np.mean(folio_ginis)),
        'null_gini_mean': float(np.mean(null_ginis)),
        'verdict': t3_verdict,
    },
    'verdict': verdict,
    't1_pass': t1_pass,
    't2_pass': t2_pass,
    't3_verdict': t3_verdict,
    'runtime_seconds': float(time.time() - t0),
}

with open(RESULTS_DIR / 'recipe_specification_test.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n  Results saved to {RESULTS_DIR / 'recipe_specification_test.json'}")
