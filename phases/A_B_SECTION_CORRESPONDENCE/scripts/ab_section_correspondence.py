#!/usr/bin/env python3
"""
Phase 367: A-to-B Section Correspondence via PP MIDDLE Composition

Tests whether A-side PP MIDDLE composition carries any trace of B's
section parameterization. B sections deeply parameterize grammar (C1029,
C1042-C1046) with 96% of MIDDLEs section-specific (C909). Does the
A->B shared vocabulary create section-dependent channels?

Prior null results:
  C752: No section-to-section routing (p=0.573)
  C753: No content-specific routing (partial r=-0.038)
  C946: No material-domain routing (reach cosine=0.997)
  C506: PP composition nearly uniform (cosine=0.995)

Hypotheses:
  H1: Shared MIDDLE section concentration (Herfindahl comparison)
  H2: Reach uniformity replication (C946 validation)
  H3: Section-conditioned class convergence (C708 extension)
  H4: PP composition -> section coverage residual
  H5: A folio ranking stability across sections

Output: results/ab_section_correspondence.json
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict
from itertools import combinations
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[3]

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, RecordAnalyzer

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

rng = np.random.RandomState(42)

print("=" * 70)
print("Phase 367: A-to-B Section Correspondence via PP MIDDLE Composition")
print("=" * 70)

# ============================================================
# S1: Load & Pre-compute
# ============================================================
print("\n--- S1: Load & Pre-compute ---")

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

morph_cache = {}
def get_morph(word):
    if word not in morph_cache:
        morph_cache[word] = morph.extract(word)
    return morph_cache[word]

# Load class map for H3 (class convergence)
class_map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_map_data = json.load(f)
token_to_class = class_map_data['token_to_class']  # word -> class number (string keys)
class_to_role = class_map_data['class_to_role']

# Build per-A-folio PP pools
print("Building per-A-folio PP pools...")
a_folio_pp = {}  # folio -> (mids, prefs, sufs)
a_folio_section = {}

for fol in sorted(analyzer.get_folios()):
    records = analyzer.analyze_folio(fol)
    mids, prefs, sufs = set(), set(), set()
    for rec in records:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                mids.add(t.middle)
                m = get_morph(t.word)
                if m.prefix:
                    prefs.add(m.prefix)
                if m.suffix:
                    sufs.add(m.suffix)
    a_folio_pp[fol] = (mids, prefs, sufs)

# Get A folio sections from transcript
for t in tx.currier_a():
    if t.folio not in a_folio_section:
        a_folio_section[t.folio] = t.section

# Filter to H+P A folios (exclude T, n=3)
a_folios = sorted([f for f in a_folio_pp if a_folio_section.get(f) in ('H', 'P')])
print(f"  {len(a_folios)} A folios (H+P)")

a_section_counts = defaultdict(int)
for f in a_folios:
    a_section_counts[a_folio_section[f]] += 1
for s, n in sorted(a_section_counts.items()):
    print(f"    A-{s}: {n}")

# Build B token inventory with morphology and section
print("Building B token inventory...")
b_tokens = {}  # word -> (prefix, middle, suffix)
b_folio_vocab = defaultdict(set)  # folio -> set of word types
b_folio_section = {}
b_folio_token_counts = defaultdict(int)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    if w not in b_tokens:
        m = get_morph(w)
        if m.middle:
            b_tokens[w] = (m.prefix, m.middle, m.suffix)
    if w in b_tokens:
        b_folio_vocab[token.folio].add(w)
        b_folio_token_counts[token.folio] += 1
    if token.folio not in b_folio_section:
        b_folio_section[token.folio] = token.section

# Filter to B+H+S sections (exclude C=5, T=2)
b_folios = sorted([f for f in b_folio_vocab if b_folio_section.get(f) in ('B', 'H', 'S')])
print(f"  {len(b_folios)} B folios (B+H+S)")

b_section_counts = defaultdict(int)
for f in b_folios:
    b_section_counts[b_folio_section[f]] += 1
SECTIONS = ['B', 'H', 'S']
for s in SECTIONS:
    print(f"    B-{s}: {b_section_counts[s]}")

# Build per-section B MIDDLE inventories
print("Building per-section B MIDDLE inventories...")
section_b_middles = defaultdict(set)  # section -> set of MIDDLEs
section_b_vocab = defaultdict(set)    # section -> set of word types

# Also count per-MIDDLE section occurrences for Herfindahl
middle_section_counts = defaultdict(lambda: defaultdict(int))  # middle -> {section -> count}

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    if token.section not in ('B', 'H', 'S'):
        continue
    m = get_morph(w)
    if m.middle:
        section_b_middles[token.section].add(m.middle)
        section_b_vocab[token.section].add(w)
        middle_section_counts[m.middle][token.section] += 1

for s in SECTIONS:
    print(f"    B-{s}: {len(section_b_middles[s])} MIDDLEs, {len(section_b_vocab[s])} token types")

# Identify shared MIDDLEs (PP in A, present in B)
all_pp_middles = set()
for fol in a_folios:
    mids, _, _ = a_folio_pp[fol]
    all_pp_middles.update(mids)

all_b_middles = set()
for s in SECTIONS:
    all_b_middles.update(section_b_middles[s])

shared_middles = all_pp_middles & all_b_middles
b_only_middles = all_b_middles - all_pp_middles
print(f"\n  PP MIDDLEs (union): {len(all_pp_middles)}")
print(f"  B MIDDLEs (B+H+S): {len(all_b_middles)}")
print(f"  Shared (PP in A AND in B): {len(shared_middles)}")
print(f"  B-only (in B but not PP): {len(b_only_middles)}")

# Apply C502.a filtering per A folio
print("\nApplying C502.a filtering per A folio...")
b_middles_set = set(mid for _, mid, _ in b_tokens.values())
b_prefixes_set = set(pref for pref, _, _ in b_tokens.values() if pref)
b_suffixes_set = set(suf for _, _, suf in b_tokens.values() if suf)

a_folio_legal = {}  # A folio -> set of legal B token words
for fol in a_folios:
    mids, prefs, sufs = a_folio_pp[fol]
    shared_mids = mids & b_middles_set
    shared_prefs = prefs & b_prefixes_set
    shared_sufs = sufs & b_suffixes_set
    legal = set()
    for tok, (pref, mid, suf) in b_tokens.items():
        if mid in shared_mids:
            if (pref is None or pref in shared_prefs):
                if (suf is None or suf in shared_sufs):
                    legal.add(tok)
    a_folio_legal[fol] = legal

legal_sizes = [len(a_folio_legal[f]) for f in a_folios]
print(f"  Legal set sizes: mean={np.mean(legal_sizes):.1f}, "
      f"min={np.min(legal_sizes)}, max={np.max(legal_sizes)}")

# Pre-compute per-section B folio vocabularies
section_folio_vocab = defaultdict(dict)  # section -> {folio -> set}
for f in b_folios:
    s = b_folio_section[f]
    section_folio_vocab[s][f] = b_folio_vocab[f]

# Pre-compute PP pool sizes for pool-size control
a_pool_sizes = {f: len(a_folio_pp[f][0]) for f in a_folios}
pool_arr = np.array([a_pool_sizes[f] for f in a_folios])
print(f"  A PP pool sizes: mean={np.mean(pool_arr):.1f}, "
      f"min={np.min(pool_arr)}, max={np.max(pool_arr)}")

# ============================================================
# S2: H1 — Shared MIDDLE Section Concentration
# ============================================================
print("\n--- S2: H1 — Shared MIDDLE Section Concentration ---")

def herfindahl(middle):
    """Compute Herfindahl index for a MIDDLE across B sections."""
    counts = middle_section_counts[middle]
    total = sum(counts.get(s, 0) for s in SECTIONS)
    if total == 0:
        return None
    fracs = [counts.get(s, 0) / total for s in SECTIONS]
    return sum(p**2 for p in fracs)

shared_herf = []
b_only_herf = []

for mid in shared_middles:
    h = herfindahl(mid)
    if h is not None:
        shared_herf.append(h)

for mid in b_only_middles:
    h = herfindahl(mid)
    if h is not None:
        b_only_herf.append(h)

shared_herf = np.array(shared_herf)
b_only_herf = np.array(b_only_herf)

print(f"  Shared MIDDLEs: n={len(shared_herf)}, "
      f"mean Herfindahl={np.mean(shared_herf):.4f}, "
      f"median={np.median(shared_herf):.4f}")
print(f"  B-only MIDDLEs: n={len(b_only_herf)}, "
      f"mean Herfindahl={np.mean(b_only_herf):.4f}, "
      f"median={np.median(b_only_herf):.4f}")

# Mann-Whitney test
from scipy.stats import mannwhitneyu, kruskal, spearmanr
u_stat, h1_p = mannwhitneyu(shared_herf, b_only_herf, alternative='less')
h1_pass = (h1_p < 0.01) and (np.mean(shared_herf) < np.mean(b_only_herf))

print(f"  Mann-Whitney U={u_stat:.0f}, p={h1_p:.6f}")
print(f"  Shared < B-only: {np.mean(shared_herf) < np.mean(b_only_herf)}")
print(f"  H1 PASS: {h1_pass}")

# Distribution details
uniform_threshold = 0.40  # close to 1/3 = 0.333
concentrated_threshold = 0.80

shared_uniform = np.sum(shared_herf < uniform_threshold) / len(shared_herf)
shared_concentrated = np.sum(shared_herf > concentrated_threshold) / len(shared_herf)
bonly_uniform = np.sum(b_only_herf < uniform_threshold) / len(b_only_herf)
bonly_concentrated = np.sum(b_only_herf > concentrated_threshold) / len(b_only_herf)

print(f"  Shared: {shared_uniform:.1%} uniform (<0.40), {shared_concentrated:.1%} concentrated (>0.80)")
print(f"  B-only: {bonly_uniform:.1%} uniform (<0.40), {bonly_concentrated:.1%} concentrated (>0.80)")

h1_results = {
    'shared_n': int(len(shared_herf)),
    'b_only_n': int(len(b_only_herf)),
    'shared_mean_herfindahl': float(np.mean(shared_herf)),
    'shared_median_herfindahl': float(np.median(shared_herf)),
    'b_only_mean_herfindahl': float(np.mean(b_only_herf)),
    'b_only_median_herfindahl': float(np.median(b_only_herf)),
    'mann_whitney_U': float(u_stat),
    'p_value': float(h1_p),
    'shared_pct_uniform': float(shared_uniform),
    'shared_pct_concentrated': float(shared_concentrated),
    'b_only_pct_uniform': float(bonly_uniform),
    'b_only_pct_concentrated': float(bonly_concentrated),
    'pass': h1_pass,
    'interpretation': 'shared_less_concentrated' if h1_pass else 'no_significant_difference'
}

# ============================================================
# S3: H2 — Reach Uniformity Replication
# ============================================================
print("\n--- S3: H2 — Reach Uniformity Replication ---")

# Compute per-section coverage for each A folio
# coverage_section[section] = array of shape (n_a,) — mean coverage of that section's B folios
coverage_section = {}
for s in SECTIONS:
    s_folios = sorted(section_folio_vocab[s].keys())
    cov = np.zeros(len(a_folios))
    for i, a_fol in enumerate(a_folios):
        legal = a_folio_legal[a_fol]
        coverages = []
        for b_fol in s_folios:
            vocab = b_folio_vocab[b_fol]
            if len(vocab) > 0:
                coverages.append(len(legal & vocab) / len(vocab))
        cov[i] = np.mean(coverages) if coverages else 0.0
    coverage_section[s] = cov

# Build reach vectors (n_a x 3)
reach = np.column_stack([coverage_section[s] for s in SECTIONS])
print(f"  Reach matrix shape: {reach.shape}")

for s_idx, s in enumerate(SECTIONS):
    print(f"  Section {s}: mean={np.mean(reach[:, s_idx]):.4f}, "
          f"std={np.std(reach[:, s_idx]):.4f}")

# Pairwise cosine similarity of reach vectors
def cosine_sim(a, b):
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

n_a = len(a_folios)
cosine_pairs = []
for i in range(n_a):
    for j in range(i + 1, n_a):
        cosine_pairs.append(cosine_sim(reach[i], reach[j]))

cosine_pairs = np.array(cosine_pairs)
print(f"  Raw reach cosine: mean={np.mean(cosine_pairs):.6f}, "
      f"min={np.min(cosine_pairs):.6f}, max={np.max(cosine_pairs):.6f}")

# Pool-size regression and residual reach
from scipy.stats import linregress

residual_reach = np.zeros_like(reach)
pool_size_r_values = []
for s_idx, s in enumerate(SECTIONS):
    slope, intercept, r, p, se = linregress(pool_arr, reach[:, s_idx])
    residual_reach[:, s_idx] = reach[:, s_idx] - (slope * pool_arr + intercept)
    pool_size_r_values.append(r)
    print(f"  Pool-size -> {s} coverage: r={r:.4f}, p={p:.2e}")

# Normalized reach proportions: for each A folio, what fraction of its total
# coverage goes to each section? If all A folios have the same proportions,
# PP composition doesn't create section-specific channels.
reach_totals = reach.sum(axis=1, keepdims=True)
reach_props = reach / np.where(reach_totals > 0, reach_totals, 1.0)  # (n_a, 3)

# Cosine similarity of proportion vectors
prop_cosine_pairs = []
for i in range(n_a):
    for j in range(i + 1, n_a):
        prop_cosine_pairs.append(cosine_sim(reach_props[i], reach_props[j]))
prop_cosine_pairs = np.array(prop_cosine_pairs)
prop_mean_cosine = float(np.mean(prop_cosine_pairs))
print(f"  Proportion-vector cosine: mean={prop_mean_cosine:.6f}, "
      f"min={np.min(prop_cosine_pairs):.6f}")

# Also test: does A section (H vs P) predict reach proportions?
# A-H vs A-P comparison of section proportions
a_h_mask = np.array([a_folio_section[f] == 'H' for f in a_folios])
a_p_mask = np.array([a_folio_section[f] == 'P' for f in a_folios])

section_prop_diffs = {}
for s_idx, s in enumerate(SECTIONS):
    h_props = reach_props[a_h_mask, s_idx]
    p_props = reach_props[a_p_mask, s_idx]
    u, p_val = mannwhitneyu(h_props, p_props, alternative='two-sided')
    section_prop_diffs[s] = {
        'a_h_mean': float(np.mean(h_props)),
        'a_p_mean': float(np.mean(p_props)),
        'diff': float(np.mean(p_props) - np.mean(h_props)),
        'mw_p': float(p_val)
    }
    print(f"  A-section -> {s} proportion: A-H={np.mean(h_props):.4f}, "
          f"A-P={np.mean(p_props):.4f}, p={p_val:.4f}")

# H2 PASS: proportion cosine < 0.999 (ANY systematic variation in reach shape)
# This is deliberately generous — C946 raw cosine was 0.997
h2_pass = prop_mean_cosine < 0.999
print(f"  H2 PASS (proportion cosine < 0.999): {h2_pass}")

h2_results = {
    'raw_cosine_mean': float(np.mean(cosine_pairs)),
    'raw_cosine_min': float(np.min(cosine_pairs)),
    'pool_size_r_by_section': {s: float(r) for s, r in zip(SECTIONS, pool_size_r_values)},
    'proportion_cosine_mean': prop_mean_cosine,
    'proportion_cosine_min': float(np.min(prop_cosine_pairs)),
    'c946_comparison': float(np.mean(cosine_pairs)),
    'section_proportion_by_a_section': section_prop_diffs,
    'pass': h2_pass
}

# ============================================================
# S4: H3 — Section-Conditioned Class Convergence
# ============================================================
print("\n--- S4: H3 — Section-Conditioned Class Convergence ---")

# For each A folio and section, compute enabled class set
a_folio_section_classes = {}  # (a_folio, section) -> set of class numbers

for a_fol in a_folios:
    legal = a_folio_legal[a_fol]
    for s in SECTIONS:
        s_vocab = section_b_vocab[s]
        enabled_tokens = legal & s_vocab
        classes = set()
        for tok in enabled_tokens:
            if tok in token_to_class:
                classes.add(int(token_to_class[tok]))
        a_folio_section_classes[(a_fol, s)] = classes

# Also compute global class set per A folio
a_folio_global_classes = {}
for a_fol in a_folios:
    legal = a_folio_legal[a_fol]
    classes = set()
    for tok in legal:
        if tok in token_to_class:
            classes.add(int(token_to_class[tok]))
    a_folio_global_classes[a_fol] = classes

# Compute pairwise class Jaccard within each section
def jaccard(s1, s2):
    if not s1 and not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)

# Sample pairs for efficiency (all pairs = 111*110/2 = 6105)
all_pairs = list(combinations(range(n_a), 2))

section_class_jaccards = {}
for s in SECTIONS:
    jaccards = []
    for i, j in all_pairs:
        a1, a2 = a_folios[i], a_folios[j]
        j_val = jaccard(a_folio_section_classes[(a1, s)],
                       a_folio_section_classes[(a2, s)])
        jaccards.append(j_val)
    section_class_jaccards[s] = np.array(jaccards)
    print(f"  Section {s}: class Jaccard mean={np.mean(jaccards):.4f}, "
          f"std={np.std(jaccards):.4f}, n_pairs={len(jaccards)}")

# Global class Jaccard (C708 replication)
global_jaccards = []
for i, j in all_pairs:
    a1, a2 = a_folios[i], a_folios[j]
    global_jaccards.append(jaccard(a_folio_global_classes[a1],
                                   a_folio_global_classes[a2]))
global_jaccards = np.array(global_jaccards)
print(f"  Global: class Jaccard mean={np.mean(global_jaccards):.4f}, "
      f"std={np.std(global_jaccards):.4f}")
print(f"  C708 reference: 0.830")

# Kruskal-Wallis test across sections
kw_stat, kw_p = kruskal(section_class_jaccards['B'],
                          section_class_jaccards['H'],
                          section_class_jaccards['S'])
print(f"  Kruskal-Wallis: H={kw_stat:.2f}, p={kw_p:.2e}")

# Check if any section differs from global by > 0.03
max_section_diff = max(abs(np.mean(section_class_jaccards[s]) - np.mean(global_jaccards))
                       for s in SECTIONS)
print(f"  Max section-global diff: {max_section_diff:.4f}")

h3_pass = (kw_p < 0.01) and (max_section_diff > 0.03)
print(f"  H3 PASS: {h3_pass}")

# Mean class set sizes per section (for context)
for s in SECTIONS:
    sizes = [len(a_folio_section_classes[(f, s)]) for f in a_folios]
    print(f"  Section {s}: mean enabled classes = {np.mean(sizes):.1f} / 49")

h3_results = {
    'global_class_jaccard_mean': float(np.mean(global_jaccards)),
    'global_class_jaccard_std': float(np.std(global_jaccards)),
    'c708_reference': 0.830,
    'section_class_jaccards': {},
    'kruskal_wallis_H': float(kw_stat),
    'kruskal_wallis_p': float(kw_p),
    'max_section_global_diff': float(max_section_diff),
    'pass': h3_pass
}
for s in SECTIONS:
    h3_results['section_class_jaccards'][s] = {
        'mean': float(np.mean(section_class_jaccards[s])),
        'std': float(np.std(section_class_jaccards[s])),
        'mean_enabled_classes': float(np.mean([len(a_folio_section_classes[(f, s)])
                                                for f in a_folios]))
    }

# ============================================================
# S5: H4 — PP Composition -> Section Coverage Residual
# ============================================================
print("\n--- S5: H4 — PP Composition -> Section Coverage Residual ---")

# Compute PP MIDDLE features per A folio
# core_fraction: fraction of PP MIDDLEs appearing in >= 3 B sections
# section_bias: mean Herfindahl of PP MIDDLEs in B

a_folio_features = {}
for a_fol in a_folios:
    pp_mids = a_folio_pp[a_fol][0]
    pp_in_b = pp_mids & all_b_middles

    if len(pp_in_b) == 0:
        a_folio_features[a_fol] = {
            'core_fraction': 0.0,
            'section_bias': 1.0,
            'pp_pool_size': len(pp_mids)
        }
        continue

    # core_fraction: fraction appearing in >= 3 sections
    n_core = 0
    herf_sum = 0.0
    for mid in pp_in_b:
        n_sections = sum(1 for s in SECTIONS if mid in section_b_middles[s])
        if n_sections >= 3:
            n_core += 1
        h = herfindahl(mid)
        if h is not None:
            herf_sum += h

    core_fraction = n_core / len(pp_in_b)
    section_bias = herf_sum / len(pp_in_b)

    a_folio_features[a_fol] = {
        'core_fraction': core_fraction,
        'section_bias': section_bias,
        'pp_pool_size': len(pp_mids)
    }

core_arr = np.array([a_folio_features[f]['core_fraction'] for f in a_folios])
bias_arr = np.array([a_folio_features[f]['section_bias'] for f in a_folios])

print(f"  core_fraction: mean={np.mean(core_arr):.4f}, std={np.std(core_arr):.4f}")
print(f"  section_bias: mean={np.mean(bias_arr):.4f}, std={np.std(bias_arr):.4f}")

# Pool-size-controlled section coverage residuals (from S3)
# residual_reach already computed above

# Partial correlations: core_fraction/section_bias -> section coverage residual
# controlling for pool_size
def partial_corr(x, y, z):
    """Partial correlation of x and y controlling for z."""
    # Residualize x on z
    sl_x, int_x, _, _, _ = linregress(z, x)
    res_x = x - (sl_x * z + int_x)
    # Residualize y on z
    sl_y, int_y, _, _, _ = linregress(z, y)
    res_y = y - (sl_y * z + int_y)
    # Correlate residuals
    r, p = spearmanr(res_x, res_y)
    return r, p

h4_results_detail = {}
h4_any_pass = False

for feature_name, feature_arr in [('core_fraction', core_arr), ('section_bias', bias_arr)]:
    for s_idx, s in enumerate(SECTIONS):
        r, p = partial_corr(feature_arr, reach[:, s_idx], pool_arr)
        this_pass = abs(r) > 0.15
        if this_pass:
            h4_any_pass = True
        key = f"{feature_name}_vs_{s}"
        h4_results_detail[key] = {
            'partial_r': float(r),
            'p_value': float(p),
            'pass': this_pass
        }
        print(f"  {feature_name} -> {s} coverage (pool controlled): "
              f"partial_r={r:.4f}, p={p:.4f}, pass={this_pass}")

print(f"  H4 PASS (any |partial r| > 0.15): {h4_any_pass}")

h4_results = {
    'features': {
        'core_fraction': {'mean': float(np.mean(core_arr)), 'std': float(np.std(core_arr))},
        'section_bias': {'mean': float(np.mean(bias_arr)), 'std': float(np.std(bias_arr))}
    },
    'partial_correlations': h4_results_detail,
    'pass': h4_any_pass
}

# ============================================================
# S6: H5 — A Folio Ranking Stability Across Sections
# ============================================================
print("\n--- S6: H5 — A Folio Ranking Stability Across Sections ---")

# Pool-size-residualized per-section coverage rankings
section_ranks = {}
for s_idx, s in enumerate(SECTIONS):
    # Residualize coverage on pool size
    residuals = residual_reach[:, s_idx]
    # Rank (higher residual = better coverage = lower rank number)
    ranks = np.argsort(np.argsort(-residuals)) + 1  # 1-based rank
    section_ranks[s] = ranks

# Pairwise Spearman rho
rank_pairs = list(combinations(SECTIONS, 2))
h5_any_below = False
h5_rho_results = {}

for s1, s2 in rank_pairs:
    rho, p = spearmanr(section_ranks[s1], section_ranks[s2])
    this_below = rho < 0.90
    if this_below:
        h5_any_below = True
    h5_rho_results[f"{s1}_vs_{s2}"] = {
        'spearman_rho': float(rho),
        'p_value': float(p),
        'below_090': this_below
    }
    print(f"  Rank stability {s1} vs {s2}: rho={rho:.4f}, p={p:.2e}, below 0.90: {this_below}")

# Also compute raw (not residualized) ranking stability for comparison
raw_section_ranks = {}
for s_idx, s in enumerate(SECTIONS):
    ranks = np.argsort(np.argsort(-reach[:, s_idx])) + 1
    raw_section_ranks[s] = ranks

for s1, s2 in rank_pairs:
    rho, _ = spearmanr(raw_section_ranks[s1], raw_section_ranks[s2])
    print(f"  (raw ranking {s1} vs {s2}: rho={rho:.4f})")

h5_pass = h5_any_below
print(f"  H5 PASS (any rho < 0.90): {h5_pass}")

h5_results = {
    'pairwise_rho': h5_rho_results,
    'pass': h5_pass
}

# ============================================================
# S7: Verdict Synthesis
# ============================================================
print("\n--- S7: Verdict Synthesis ---")

n_pass = sum([h1_pass, h2_pass, h3_pass, h4_any_pass, h5_pass])
print(f"\nResults: {n_pass}/5 hypotheses pass")
print(f"  H1 (shared MIDDLE deconcentration): {'PASS' if h1_pass else 'FAIL'}")
print(f"  H2 (reach uniformity breaks):       {'PASS' if h2_pass else 'FAIL'}")
print(f"  H3 (class convergence varies):      {'PASS' if h3_pass else 'FAIL'}")
print(f"  H4 (PP features predict section):   {'PASS' if h4_any_pass else 'FAIL'}")
print(f"  H5 (ranking instability):           {'PASS' if h5_pass else 'FAIL'}")

# Determine verdict
if h4_any_pass or h5_pass:
    verdict = 'PP_SECTION_SIGNAL'
    verdict_score = f"{n_pass}/5"
elif h1_pass and not h2_pass and not h3_pass and not h4_any_pass and not h5_pass:
    verdict = 'SECTION_UNIVERSAL_SUBSTRATE'
    verdict_score = f"{n_pass}/5"
else:
    verdict = 'FULLY_SECTION_AGNOSTIC'
    verdict_score = f"{n_pass}/5"

print(f"\nVerdict: {verdict} ({verdict_score})")

# Compile results
results = {
    'phase': 'A_B_SECTION_CORRESPONDENCE',
    'phase_number': 367,
    'timestamp': datetime.now().isoformat(),
    'analysis_set': {
        'a_folios': len(a_folios),
        'a_sections': dict(a_section_counts),
        'b_folios': len(b_folios),
        'b_sections': dict(b_section_counts),
        'shared_middles': len(shared_middles),
        'b_only_middles': len(b_only_middles)
    },
    'H1_shared_concentration': h1_results,
    'H2_reach_uniformity': h2_results,
    'H3_class_convergence': h3_results,
    'H4_pp_composition': h4_results,
    'H5_ranking_stability': h5_results,
    'verdict': verdict,
    'verdict_score': verdict_score,
    'prior_constraints': {
        'C752': 'no_section_routing (p=0.573)',
        'C753': 'no_content_routing (partial_r=-0.038)',
        'C946': 'no_material_routing (cosine=0.997)',
        'C506': 'pp_composition_uniform (cosine=0.995)',
        'C708': 'funnel_topology (middle_jaccard=0.274, class_jaccard=0.830)'
    }
}

out_path = RESULTS_DIR / 'ab_section_correspondence.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)
print(f"\nResults written to {out_path}")
print("\nDone.")
