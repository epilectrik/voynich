#!/usr/bin/env python3
"""
Phase 587: BSIDE_OPERATIONAL_SIGNATURES
A's Shadow in B — Characterize A records by their B-side operational signatures.

Tests:
  T0: Noise floor (random draws from B marginal)
  T1: Folio-level coherence (with PP overlap control)
  T2: Section prediction (random forest, LOO-CV)
  T3: RI extension directional predictions
  T4: C475-pair divergence (incompatible vs compatible record pairs)
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
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[3]
t0 = time.time()

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']
HEADS = ['k', 't', 'a', 'e', 'o', 'headless']
FEATURE_NAMES = CATEGORIES + [f'HEAD_{h}' for h in HEADS] + ['k_initial', 'hazard']

# ============================================================
# STAGE 0: Data Loading
# ============================================================

print("=" * 70)
print("Phase 587: BSIDE_OPERATIONAL_SIGNATURES")
print("A's Shadow in B")
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

# Pre-compute B token features (category, HEAD, k-initial)
b_token_category = {}
b_token_head = {}
b_token_k_initial = {}

for tok, (pref, mid, suf) in b_tokens.items():
    cat = cc.classify(mid)
    b_token_category[tok] = cat
    head, _, _, _ = decompose_middle_hmt(mid)
    b_token_head[tok] = head if head else 'headless'
    b_token_k_initial[tok] = mid.startswith('k')

# --- Build A record morphology ---
print("  Building A record morphology...")
a_records = []  # list of dicts with folio, line, prefixes, middles, suffixes, composition
folio_section_map = {}

for record in analyzer.iter_records():
    prefixes = set()
    middles = set()
    suffixes = set()
    ri_mids = []
    pp_mids = []
    for t in record.tokens:
        m = morph.extract(t.word)
        if m.prefix:
            prefixes.add(m.prefix)
        if m.middle:
            middles.add(m.middle)
            if m.middle in ri_middles:
                ri_mids.append(m.middle)
            elif m.middle in pp_middles:
                pp_mids.append(m.middle)
        if m.suffix:
            suffixes.add(m.suffix)

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
        'ri_middles': ri_mids,
        'composition': record.composition,
    })

print(f"  A records: {len(a_records)}")
print(f"  Folios: {len(set(r['folio'] for r in a_records))}")

# --- Build PP sorted list for extension extraction ---
pp_sorted = sorted(b_middles_set, key=len, reverse=True)

def get_extension(ri_middle):
    for pp in pp_sorted:
        if len(pp) >= 2:
            if ri_middle.startswith(pp) and len(ri_middle) > len(pp):
                return ri_middle[len(pp):], 'suffix'
            elif ri_middle.endswith(pp) and len(ri_middle) > len(pp):
                return ri_middle[:-len(pp)], 'prefix'
    return None, None

# ============================================================
# STAGE 1: C502.a Filtering + Signature Computation
# ============================================================

print("\n  Computing C502.a survivor sets and signatures...")

def compute_signature(legal_tokens):
    """Compute 16-dim B-side operational signature from a set of legal B tokens."""
    n = len(legal_tokens)
    if n == 0:
        return np.zeros(16)

    # Category composition (8 dims)
    cat_counts = Counter()
    for tok in legal_tokens:
        cat = b_token_category.get(tok)
        if cat:
            cat_counts[cat] += 1
    cat_total = sum(cat_counts.values())
    cat_vec = [cat_counts.get(c, 0) / cat_total if cat_total > 0 else 0
               for c in CATEGORIES]

    # HEAD distribution (6 dims)
    head_counts = Counter()
    for tok in legal_tokens:
        head_counts[b_token_head.get(tok, 'headless')] += 1
    head_vec = [head_counts.get(h, 0) / n for h in HEADS]

    # k-initial fraction (1 dim)
    k_init = sum(1 for tok in legal_tokens if b_token_k_initial.get(tok, False)) / n

    # Hazard exposure (1 dim)
    hazard = sum(1 for src, tgt in FORBIDDEN_PAIRS
                 if src in legal_tokens and tgt in legal_tokens)

    return np.array(cat_vec + head_vec + [k_init, hazard])


record_signatures = []
record_survivors = []

for rec in a_records:
    pp_mids = rec['middles'] & b_middles_set
    pp_prefs = rec['prefixes'] & b_prefixes_set
    pp_sufs = rec['suffixes'] & b_suffixes_set

    legal = set()
    for tok, (pref, mid, suf) in b_tokens.items():
        if mid in pp_mids:
            pref_ok = (pref is None or pref in pp_prefs)
            suf_ok = (suf is None or suf in pp_sufs)
            if pref_ok and suf_ok:
                legal.add(tok)

    sig = compute_signature(legal)
    record_signatures.append(sig)
    record_survivors.append(legal)

record_signatures = np.array(record_signatures)
survivor_sizes = [len(s) for s in record_survivors]
print(f"  Mean survivors: {np.mean(survivor_sizes):.1f}, "
      f"median: {np.median(survivor_sizes):.0f}, "
      f"range: [{min(survivor_sizes)}, {max(survivor_sizes)}]")
print(f"  Records with 0 survivors: {sum(1 for s in survivor_sizes if s == 0)}")

# --- Folio-level signatures (pooled) ---
print("  Computing folio-level pooled signatures...")
folio_records = defaultdict(list)
for i, rec in enumerate(a_records):
    folio_records[rec['folio']].append(i)

folio_signatures = {}
for folio, indices in folio_records.items():
    pooled = set()
    for idx in indices:
        pooled.update(record_survivors[idx])
    folio_signatures[folio] = compute_signature(pooled)

folio_list = sorted(folio_signatures.keys())
folio_sig_matrix = np.array([folio_signatures[f] for f in folio_list])
folio_sections = [folio_section_map[f] for f in folio_list]
print(f"  Folio-level signatures: {len(folio_list)}")

print(f"\n  Data loading complete ({time.time()-t0:.1f}s)")

# ============================================================
# TEST 0: Noise Floor
# ============================================================

print(f"\n{'='*70}")
print("  TEST 0: Noise Floor")
print(f"{'='*70}")

# Build B marginal distributions
all_b_cats = [b_token_category.get(t) for t in b_tokens if b_token_category.get(t)]
all_b_heads = [b_token_head.get(t, 'headless') for t in b_tokens]
b_tok_list = list(b_tokens.keys())
n_b = len(b_tok_list)

N_NOISE = 1000
median_surv = int(np.median(survivor_sizes))
noise_sigs = []

rng = np.random.RandomState(42)
for _ in range(N_NOISE):
    sample_idx = rng.choice(n_b, size=median_surv, replace=False)
    sample_toks = {b_tok_list[i] for i in sample_idx}
    noise_sigs.append(compute_signature(sample_toks))

noise_sigs = np.array(noise_sigs)

# Compute pairwise cosine similarities for noise
n_noise_pairs = min(5000, N_NOISE * (N_NOISE - 1) // 2)
noise_sims = []
pair_indices = rng.choice(N_NOISE, size=(n_noise_pairs, 2), replace=True)
for i, j in pair_indices:
    if i != j:
        a_vec, b_vec = noise_sigs[i], noise_sigs[j]
        if np.any(a_vec) and np.any(b_vec):
            noise_sims.append(1 - cosine_dist(a_vec, b_vec))

noise_mean = float(np.mean(noise_sims))
noise_p95 = float(np.percentile(noise_sims, 95))
noise_std = float(np.std(noise_sims))

print(f"  Random draws of {median_surv} B tokens:")
print(f"    Mean cosine similarity: {noise_mean:.4f}")
print(f"    95th percentile: {noise_p95:.4f}")
print(f"    Std: {noise_std:.4f}")

# ============================================================
# TEST 1: Folio-Level Coherence
# ============================================================

print(f"\n{'='*70}")
print("  TEST 1: Folio-Level Coherence")
print(f"{'='*70}")

# Within-folio cosine similarities
within_sims = []
within_pp_jaccards = []
for folio, indices in folio_records.items():
    if len(indices) < 2:
        continue
    for i in range(len(indices)):
        for j in range(i + 1, len(indices)):
            a_vec = record_signatures[indices[i]]
            b_vec = record_signatures[indices[j]]
            if np.any(a_vec) and np.any(b_vec):
                sim = 1 - cosine_dist(a_vec, b_vec)
                within_sims.append(sim)
                # PP overlap Jaccard
                pp_i = a_records[indices[i]]['pp_middles']
                pp_j = a_records[indices[j]]['pp_middles']
                if pp_i or pp_j:
                    jac = len(pp_i & pp_j) / len(pp_i | pp_j) if (pp_i | pp_j) else 0
                    within_pp_jaccards.append(jac)

observed_within = float(np.mean(within_sims))
observed_pp_jaccard = float(np.mean(within_pp_jaccards))

print(f"  Observed within-folio cosine similarity: {observed_within:.4f}")
print(f"  Noise floor mean: {noise_mean:.4f}")
print(f"  Within-folio PP Jaccard: {observed_pp_jaccard:.4f}")

# Permutation test
N_PERM = 1000
perm_means = []
all_folios = [rec['folio'] for rec in a_records]

for p in range(N_PERM):
    shuffled = rng.permutation(all_folios)
    shuffled_folio_records = defaultdict(list)
    for i, f in enumerate(shuffled):
        shuffled_folio_records[f].append(i)

    perm_sims = []
    for folio, indices in shuffled_folio_records.items():
        if len(indices) < 2:
            continue
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                a_vec = record_signatures[indices[i]]
                b_vec = record_signatures[indices[j]]
                if np.any(a_vec) and np.any(b_vec):
                    perm_sims.append(1 - cosine_dist(a_vec, b_vec))
    if perm_sims:
        perm_means.append(np.mean(perm_sims))

perm_mean = float(np.mean(perm_means))
perm_std = float(np.std(perm_means))
z_score = (observed_within - perm_mean) / perm_std if perm_std > 0 else 0
p_value = float(np.mean([m >= observed_within for m in perm_means]))

print(f"  Permutation mean: {perm_mean:.4f} +/- {perm_std:.4f}")
print(f"  z-score: {z_score:.2f}")
print(f"  p-value: {p_value:.4f}")

# PP overlap control: partial correlation
# Compute between-folio similarities for comparison
between_sims = []
between_pp_jaccards = []
sample_between = rng.choice(len(a_records), size=(5000, 2), replace=True)
for i, j in sample_between:
    if a_records[i]['folio'] != a_records[j]['folio']:
        a_vec = record_signatures[i]
        b_vec = record_signatures[j]
        if np.any(a_vec) and np.any(b_vec):
            between_sims.append(1 - cosine_dist(a_vec, b_vec))
            pp_i = a_records[i]['pp_middles']
            pp_j = a_records[j]['pp_middles']
            jac = len(pp_i & pp_j) / len(pp_i | pp_j) if (pp_i | pp_j) else 0
            between_pp_jaccards.append(jac)

between_mean = float(np.mean(between_sims))
between_pp_mean = float(np.mean(between_pp_jaccards))
print(f"  Between-folio cosine similarity: {between_mean:.4f}")
print(f"  Between-folio PP Jaccard: {between_pp_mean:.4f}")
print(f"  Within/between ratio: {observed_within/between_mean:.3f}")

# Section-level ANOVA on folio-level signatures
print("\n  Section-level ANOVA (folio-level signatures):")
section_groups = defaultdict(list)
for i, sec in enumerate(folio_sections):
    section_groups[sec].append(i)

anova_results = {}
for dim, name in enumerate(FEATURE_NAMES):
    groups = [folio_sig_matrix[indices, dim] for sec, indices in section_groups.items()
              if len(indices) >= 3]
    if len(groups) >= 2:
        F, p = stats.f_oneway(*groups)
        anova_results[name] = {'F': float(F), 'p': float(p)}
        if p < 0.05:
            print(f"    {name}: F={F:.2f}, p={p:.4f} *")

# ============================================================
# TEST 2: Section Prediction (Supervised)
# ============================================================

print(f"\n{'='*70}")
print("  TEST 2: Section Prediction (Random Forest, LOO-CV)")
print(f"{'='*70}")

# Record-level prediction
sections = [rec['section'] for rec in a_records]
unique_sections = sorted(set(sections))
n_sections = len(unique_sections)
chance = 1.0 / n_sections

# Filter out records with zero survivors
valid_mask = np.array([np.any(sig) for sig in record_signatures])
X_valid = record_signatures[valid_mask]
y_valid = np.array(sections)[valid_mask]
n_valid = len(X_valid)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_valid)

rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
loo = LeaveOneOut()
y_pred = cross_val_predict(rf, X_scaled, y_valid, cv=loo)
record_accuracy = float(np.mean(y_pred == y_valid))

print(f"  Record-level LOO-CV accuracy: {record_accuracy:.4f} (chance: {chance:.4f})")
print(f"  Accuracy / chance: {record_accuracy/chance:.2f}x")

# Feature importances (train on full data)
rf.fit(X_scaled, y_valid)
importances = rf.feature_importances_
top_features = sorted(zip(FEATURE_NAMES, importances), key=lambda x: -x[1])[:5]
print(f"  Top features:")
for name, imp in top_features:
    print(f"    {name}: {imp:.4f}")

# Folio-level prediction
if len(folio_list) >= 10:
    X_folio = scaler.fit_transform(folio_sig_matrix)
    y_folio = np.array(folio_sections)

    rf_folio = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    loo_folio = LeaveOneOut()
    y_folio_pred = cross_val_predict(rf_folio, X_folio, y_folio, cv=loo_folio)
    folio_accuracy = float(np.mean(y_folio_pred == y_folio))
    print(f"  Folio-level LOO-CV accuracy: {folio_accuracy:.4f} (chance: {chance:.4f})")
    print(f"  Folio accuracy / chance: {folio_accuracy/chance:.2f}x")
else:
    folio_accuracy = None
    print(f"  Folio-level: insufficient data")

# ============================================================
# TEST 3: RI Extension Directional Predictions
# ============================================================

print(f"\n{'='*70}")
print("  TEST 3: RI Extension Directional Predictions")
print(f"{'='*70}")

# Extract dominant extension per MIXED record
mixed_indices = [i for i, rec in enumerate(a_records) if rec['composition'] == 'MIXED']
print(f"  MIXED records: {len(mixed_indices)}")

ext_to_records = defaultdict(list)  # extension_char -> list of record indices
for idx in mixed_indices:
    rec = a_records[idx]
    ext_chars = []
    for ri_mid in rec['ri_middles']:
        ext, pos = get_extension(ri_mid)
        if ext and len(ext) == 1:
            ext_chars.append(ext)
    if ext_chars:
        dominant = Counter(ext_chars).most_common(1)[0][0]
        ext_to_records[dominant].append(idx)

print(f"  Extension groups (single-char):")
for ext in sorted(ext_to_records.keys()):
    print(f"    '{ext}': {len(ext_to_records[ext])} records")

# Define directional predictions
predictions = [
    ('k', 'HEAD_k', 'greater'),
    ('e', 'HEAD_e', 'greater'),
    ('h', 'MONITORING', 'greater'),
    ('d', 'TRANSITION', 'greater'),
    ('t', 'FLOW', 'greater'),
    ('r', 'hazard', 'greater'),
]

prediction_results = {}
n_passed = 0
n_testable = 0
MIN_GROUP = 10

for ext_char, feature_name, direction in predictions:
    feat_idx = FEATURE_NAMES.index(feature_name)
    group_indices = ext_to_records.get(ext_char, [])
    other_indices = [i for i in mixed_indices if i not in set(group_indices)]

    result = {
        'extension': ext_char,
        'feature': feature_name,
        'n_group': len(group_indices),
        'n_other': len(other_indices),
    }

    if len(group_indices) < MIN_GROUP:
        result['status'] = 'INSUFFICIENT_DATA'
        if group_indices:
            result['group_mean'] = float(np.mean([record_signatures[i][feat_idx]
                                                   for i in group_indices]))
            result['other_mean'] = float(np.mean([record_signatures[i][feat_idx]
                                                   for i in other_indices]))
        print(f"  {ext_char}-ext -> {feature_name}: n={len(group_indices)} (insufficient)")
    else:
        n_testable += 1
        group_vals = [record_signatures[i][feat_idx] for i in group_indices]
        other_vals = [record_signatures[i][feat_idx] for i in other_indices]
        result['group_mean'] = float(np.mean(group_vals))
        result['other_mean'] = float(np.mean(other_vals))
        result['effect_direction'] = 'correct' if result['group_mean'] > result['other_mean'] else 'wrong'

        U, p_two = stats.mannwhitneyu(group_vals, other_vals, alternative='greater')
        result['U'] = float(U)
        result['p_one_sided'] = float(p_two)
        # Cohen's d
        pooled_std = np.sqrt((np.var(group_vals) * (len(group_vals)-1) +
                              np.var(other_vals) * (len(other_vals)-1)) /
                             (len(group_vals) + len(other_vals) - 2))
        result['cohens_d'] = float((np.mean(group_vals) - np.mean(other_vals)) /
                                   pooled_std) if pooled_std > 0 else 0.0
        # Bonferroni correction
        bonferroni_threshold = 0.05 / len(predictions)
        result['passed'] = result['p_one_sided'] < bonferroni_threshold
        result['status'] = 'PASSED' if result['passed'] else 'FAILED'
        if result['passed']:
            n_passed += 1

        print(f"  {ext_char}-ext -> {feature_name}: "
              f"group={result['group_mean']:.4f}, other={result['other_mean']:.4f}, "
              f"d={result['cohens_d']:.3f}, p={result['p_one_sided']:.4f} "
              f"{'PASS' if result['passed'] else ''}")

    prediction_results[ext_char] = result

print(f"\n  Directional predictions: {n_passed}/{n_testable} passed "
      f"(of {len(predictions)} total, {len(predictions)-n_testable} insufficient data)")

# ============================================================
# TEST 4: C475-Pair Divergence
# ============================================================

print(f"\n{'='*70}")
print("  TEST 4: C475-Pair Divergence")
print(f"{'='*70}")

# For each pair of A records, check if they share any PP MIDDLEs
# C475-incompatible = share NO PP MIDDLEs in common
# C475-compatible = share at least one PP MIDDLE

# Sample pairs (full pairwise is O(n^2) = ~1.2M pairs, too many)
N_SAMPLE_PAIRS = 10000
compat_dists = []
incompat_dists = []

valid_records = [i for i in range(len(a_records))
                 if np.any(record_signatures[i]) and a_records[i]['pp_middles']]

for _ in range(N_SAMPLE_PAIRS):
    i, j = rng.choice(valid_records, size=2, replace=False)
    pp_i = a_records[i]['pp_middles']
    pp_j = a_records[j]['pp_middles']
    shared = pp_i & pp_j

    sig_i = record_signatures[i]
    sig_j = record_signatures[j]
    dist = cosine_dist(sig_i, sig_j)

    if shared:
        compat_dists.append(dist)
    else:
        incompat_dists.append(dist)

print(f"  Compatible pairs (shared PP): {len(compat_dists)}")
print(f"  Incompatible pairs (no shared PP): {len(incompat_dists)}")

compat_mean = float(np.mean(compat_dists))
incompat_mean = float(np.mean(incompat_dists))

print(f"  Compatible mean cosine distance: {compat_mean:.4f}")
print(f"  Incompatible mean cosine distance: {incompat_mean:.4f}")

if compat_dists and incompat_dists:
    U, p_c475 = stats.mannwhitneyu(incompat_dists, compat_dists, alternative='greater')
    # Effect size
    pooled_std = np.sqrt((np.var(compat_dists) * (len(compat_dists)-1) +
                          np.var(incompat_dists) * (len(incompat_dists)-1)) /
                         (len(compat_dists) + len(incompat_dists) - 2))
    d_c475 = float((incompat_mean - compat_mean) / pooled_std) if pooled_std > 0 else 0
    print(f"  Mann-Whitney U p-value: {p_c475:.6f}")
    print(f"  Cohen's d: {d_c475:.4f}")
    c475_significant = p_c475 < 0.01
else:
    p_c475 = 1.0
    d_c475 = 0.0
    c475_significant = False

# ============================================================
# SUMMARY
# ============================================================

print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")

print(f"\n  Noise floor: mean cosine sim = {noise_mean:.4f}")
print(f"  Within-folio cosine sim: {observed_within:.4f} "
      f"(vs noise {noise_mean:.4f}, vs between {between_mean:.4f})")
print(f"  Folio coherence: z={z_score:.2f}, p={p_value:.4f}")
print(f"  Section prediction (record): {record_accuracy:.4f} ({record_accuracy/chance:.2f}x chance)")
if folio_accuracy is not None:
    print(f"  Section prediction (folio): {folio_accuracy:.4f} ({folio_accuracy/chance:.2f}x chance)")
print(f"  RI directional predictions: {n_passed}/{n_testable} passed")
print(f"  C475 divergence: d={d_c475:.4f}, p={p_c475:.6f}")

# Verdicts
folio_coherent = p_value < 0.01
section_predictable = record_accuracy > 2 * chance
c475_divergent = c475_significant
extensions_pass = n_passed >= 4

if folio_coherent and section_predictable and c475_divergent:
    verdict = "OPERATIONAL_PARAMETRIC_SUPPORTED"
elif section_predictable:
    verdict = "SECTION_STRUCTURE_ONLY"
else:
    verdict = "NO_BSIDE_STRUCTURE"

print(f"\n  VERDICT: {verdict}")
print(f"  Total runtime: {time.time()-t0:.1f}s")

# ============================================================
# Save Results
# ============================================================

output = {
    'phase': 587,
    'test': 'BSIDE_OPERATIONAL_SIGNATURES',
    'metadata': {
        'n_records': len(a_records),
        'n_folios': len(folio_list),
        'n_b_token_types': len(b_tokens),
        'n_mixed_records': len(mixed_indices),
        'median_survivors': int(np.median(survivor_sizes)),
        'mean_survivors': float(np.mean(survivor_sizes)),
        'signature_dimensions': 16,
        'feature_names': FEATURE_NAMES,
    },
    'T0_noise_floor': {
        'draw_size': median_surv,
        'n_draws': N_NOISE,
        'mean_cosine_sim': noise_mean,
        'p95_cosine_sim': noise_p95,
        'std_cosine_sim': noise_std,
    },
    'T1_folio_coherence': {
        'within_folio_cosine_sim': observed_within,
        'between_folio_cosine_sim': between_mean,
        'within_pp_jaccard': observed_pp_jaccard,
        'between_pp_jaccard': between_pp_mean,
        'permutation_mean': perm_mean,
        'permutation_std': perm_std,
        'z_score': z_score,
        'p_value': p_value,
        'n_permutations': N_PERM,
        'anova_significant_features': {k: v for k, v in anova_results.items()
                                        if v['p'] < 0.05},
    },
    'T2_section_prediction': {
        'record_level': {
            'accuracy': record_accuracy,
            'chance': chance,
            'accuracy_over_chance': record_accuracy / chance,
            'n_records': n_valid,
            'n_sections': n_sections,
            'top_features': {name: float(imp) for name, imp in top_features},
        },
        'folio_level': {
            'accuracy': folio_accuracy,
            'chance': chance,
            'accuracy_over_chance': folio_accuracy / chance if folio_accuracy else None,
            'n_folios': len(folio_list),
        },
    },
    'T3_ri_extension_predictions': {
        'predictions': {k: {kk: (float(vv) if isinstance(vv, (np.floating, np.integer)) else
                            bool(vv) if isinstance(vv, (np.bool_, bool)) else vv)
                            for kk, vv in v.items()}
                        for k, v in prediction_results.items()},
        'n_passed': n_passed,
        'n_testable': n_testable,
        'n_total': len(predictions),
    },
    'T4_c475_divergence': {
        'n_compatible_pairs': len(compat_dists),
        'n_incompatible_pairs': len(incompat_dists),
        'compatible_mean_distance': compat_mean,
        'incompatible_mean_distance': incompat_mean,
        'p_value': float(p_c475),
        'cohens_d': d_c475,
        'significant': bool(c475_significant),
    },
    'verdict': verdict,
    'folio_coherent': bool(folio_coherent),
    'section_predictable': bool(section_predictable),
    'c475_divergent': bool(c475_divergent),
    'extensions_passed': int(n_passed),
    'runtime_seconds': float(time.time() - t0),
}

results_file = Path(__file__).parent.parent / 'results' / 'bside_operational_signatures.json'
json.dump(output, open(results_file, 'w'), indent=2)
print(f"\n  Saved to {results_file}")
