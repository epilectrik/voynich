#!/usr/bin/env python3
"""
UN COMPOSITIONAL MECHANICS - Script 3: Population Structure

Tests whether UN is a uniform cloud or contains distinct sub-populations.

Sections:
1. Distributional Clustering (k-means, silhouette)
2. Hapax vs Repeater Analysis
3. AX-UN Boundary Test
4. Folio-Level UN Predictors
"""

import os
import sys
import json
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import spearmanr, mannwhitneyu, chi2_contingency

os.chdir('C:/git/voynich')
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

# ==============================================================================
# LOAD DATA
# ==============================================================================

print("=" * 70)
print("UN COMPOSITIONAL MECHANICS - Script 3: Population Structure")
print("=" * 70)

tx = Transcript()
morph = Morphology()

b_tokens = list(tx.currier_b())
print(f"Total Currier B tokens: {len(b_tokens)}")

with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
class_to_role = class_map['class_to_role']

ROLE_ABBREV = {
    'CORE_CONTROL': 'CC',
    'ENERGY_OPERATOR': 'EN',
    'FLOW_OPERATOR': 'FL',
    'FREQUENT_OPERATOR': 'FQ',
    'AUXILIARY': 'AX',
}

# Load regime mapping
with open('phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json', 'r') as f:
    regime_map_raw = json.load(f)
folio_to_regime = {}
for regime, folios in regime_map_raw.items():
    for f in folios:
        folio_to_regime[f] = regime

# Build token lists with morphology
classified = []
un_list = []
for t in b_tokens:
    m = morph.extract(t.word)
    if t.word in token_to_class:
        cls = str(token_to_class[t.word])
        role = ROLE_ABBREV.get(class_to_role.get(cls, ''), '?')
        classified.append((t, role, m))
    else:
        un_list.append((t, m))

print(f"Classified: {len(classified)}, UN: {len(un_list)}")

# UN type counts
un_type_counts = Counter(t.word for t, _ in un_list)

# Build prefix->role mapping from classified data for prediction
prefix_role_dist = defaultdict(Counter)
for t, role, m in classified:
    p = m.prefix if m.prefix else '_NONE_'
    prefix_role_dist[p][role] += 1

def predict_role(m):
    """Predict role from morphology using PREFIX."""
    p = m.prefix if m.prefix else '_NONE_'
    dist = prefix_role_dist.get(p)
    if not dist:
        return None
    return dist.most_common(1)[0][0]

# ==============================================================================
# SECTION 1: DISTRIBUTIONAL CLUSTERING
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 1: DISTRIBUTIONAL CLUSTERING")
print("=" * 70)

# Build feature vectors for UN tokens (type-level to avoid duplicates)
# Features: PREFIX category (one-hot), suffix presence, word length, section
print("\nBuilding feature vectors (type-level)...")

# Get unique types and their first occurrence for section info
un_type_first = {}
un_type_sections = defaultdict(Counter)
for t, m in un_list:
    word = t.word
    if word not in un_type_first:
        un_type_first[word] = (t, m)
    un_type_sections[word][t.section] += 1

# Get top prefixes for one-hot encoding
top_prefixes = ['ch', 'qo', 'sh', 'ol', 'ot', 'ok', 'da', 'lk', 'pch', 'al']

feature_names = top_prefixes + ['other_prefix', 'no_prefix', 'has_suffix', 'has_articulator', 'word_len']

types_list = sorted(un_type_first.keys())
X = np.zeros((len(types_list), len(feature_names)))

for i, word in enumerate(types_list):
    t, m = un_type_first[word]
    # Prefix one-hot
    if m.prefix in top_prefixes:
        idx = top_prefixes.index(m.prefix)
        X[i, idx] = 1
    elif m.prefix:
        X[i, len(top_prefixes)] = 1  # other_prefix
    else:
        X[i, len(top_prefixes) + 1] = 1  # no_prefix

    # Suffix, articulator, length
    X[i, -3] = 1 if m.suffix else 0
    X[i, -2] = 1 if m.has_articulator else 0
    X[i, -1] = len(word)

# Normalize word_len column
if X[:, -1].std() > 0:
    X[:, -1] = (X[:, -1] - X[:, -1].mean()) / X[:, -1].std()

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score

print(f"Feature matrix: {X.shape[0]} types x {X.shape[1]} features")
print(f"\nClustering results:")
print(f"  {'k':>3} {'Silhouette':>12} {'Calinski':>12} {'Sizes':>30}")
print(f"  {'-'*60}")

best_k = 2
best_sil = -1
cluster_results = {}

for k in [2, 3, 4, 5]:
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = km.fit_predict(X)
    sil = silhouette_score(X, labels)
    cal = calinski_harabasz_score(X, labels)
    sizes = Counter(labels)
    size_str = ', '.join(f"{sizes[j]}" for j in range(k))
    print(f"  {k:>3} {sil:>12.3f} {cal:>12.1f} {size_str:>30}")
    cluster_results[k] = {'silhouette': round(sil, 3), 'calinski': round(cal, 1)}
    if sil > best_sil:
        best_sil = sil
        best_k = k

print(f"\n  Best k by silhouette: {best_k} (silhouette={best_sil:.3f})")
print(f"  Compare: EN anatomy k=2 silhouette=0.180 (C574)")

# At best k, characterize clusters
km_best = KMeans(n_clusters=best_k, n_init=10, random_state=42)
best_labels = km_best.fit_predict(X)

print(f"\n  Cluster characterization (k={best_k}):")
for cluster_id in range(best_k):
    mask = best_labels == cluster_id
    cluster_types = [types_list[i] for i in range(len(types_list)) if mask[i]]
    cluster_X = X[mask]

    # Dominant prefix
    prefix_sums = cluster_X[:, :len(top_prefixes)].sum(axis=0)
    dom_prefix_idx = np.argmax(prefix_sums)
    dom_prefix = top_prefixes[dom_prefix_idx] if prefix_sums[dom_prefix_idx] > 0 else '(none)'

    # Suffix rate
    suffix_rate = cluster_X[:, -3].mean()
    art_rate = cluster_X[:, -2].mean()

    # Predicted role distribution
    predicted_roles = Counter()
    for word in cluster_types:
        _, m = un_type_first[word]
        role = predict_role(m)
        if role:
            predicted_roles[role] += 1

    role_str = ', '.join(f"{r}:{predicted_roles[r]}" for r in sorted(predicted_roles, key=predicted_roles.get, reverse=True)[:3])
    print(f"\n  Cluster {cluster_id} (n={len(cluster_types)}):")
    print(f"    Top prefix: {dom_prefix} ({prefix_sums[dom_prefix_idx]:.0f} types)")
    print(f"    Suffix rate: {suffix_rate:.2f}, Articulator rate: {art_rate:.2f}")
    print(f"    Predicted roles: {role_str}")
    print(f"    Sample: {cluster_types[:5]}")

# ==============================================================================
# SECTION 2: HAPAX VS REPEATER ANALYSIS
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 2: HAPAX VS REPEATER ANALYSIS")
print("=" * 70)

hapax_types = [w for w, c in un_type_counts.items() if c == 1]
repeater_types = [w for w, c in un_type_counts.items() if c >= 2]

print(f"\nHapax types: {len(hapax_types)} ({len(hapax_types)/len(un_type_counts)*100:.1f}%)")
print(f"Repeater types: {len(repeater_types)} ({len(repeater_types)/len(un_type_counts)*100:.1f}%)")
print(f"Repeater tokens: {sum(un_type_counts[w] for w in repeater_types)}")

# Compare morphological profiles
hapax_morphs = [morph.extract(w) for w in hapax_types]
repeater_morphs = [morph.extract(w) for w in repeater_types]

hapax_prefix_rate = sum(1 for m in hapax_morphs if m.prefix) / len(hapax_morphs)
repeater_prefix_rate = sum(1 for m in repeater_morphs if m.prefix) / len(repeater_morphs)

hapax_suffix_rate = sum(1 for m in hapax_morphs if m.suffix) / len(hapax_morphs)
repeater_suffix_rate = sum(1 for m in repeater_morphs if m.suffix) / len(repeater_morphs)

hapax_art_rate = sum(1 for m in hapax_morphs if m.has_articulator) / len(hapax_morphs)
repeater_art_rate = sum(1 for m in repeater_morphs if m.has_articulator) / len(repeater_morphs)

hapax_lengths = [len(w) for w in hapax_types]
repeater_lengths = [len(w) for w in repeater_types]

print(f"\nMorphological comparison (type-level):")
print(f"  {'Feature':<20} {'Hapax':>10} {'Repeater':>10} {'Diff':>10}")
print(f"  {'-'*55}")
print(f"  {'PREFIX rate':<20} {hapax_prefix_rate:>9.1%} {repeater_prefix_rate:>9.1%} {hapax_prefix_rate-repeater_prefix_rate:>+9.1%}")
print(f"  {'SUFFIX rate':<20} {hapax_suffix_rate:>9.1%} {repeater_suffix_rate:>9.1%} {hapax_suffix_rate-repeater_suffix_rate:>+9.1%}")
print(f"  {'Articulator rate':<20} {hapax_art_rate:>9.1%} {repeater_art_rate:>9.1%} {hapax_art_rate-repeater_art_rate:>+9.1%}")
print(f"  {'Mean length':<20} {np.mean(hapax_lengths):>10.2f} {np.mean(repeater_lengths):>10.2f} {np.mean(hapax_lengths)-np.mean(repeater_lengths):>+10.2f}")

# Do repeaters look more like classified tokens?
# Compare predicted role distribution
hapax_roles = Counter()
for w in hapax_types:
    m = morph.extract(w)
    role = predict_role(m)
    if role:
        hapax_roles[role] += 1

repeater_roles = Counter()
for w in repeater_types:
    m = morph.extract(w)
    role = predict_role(m)
    if role:
        repeater_roles[role] += 1

print(f"\nPredicted role distribution (type-level):")
print(f"  {'Role':<6} {'Hapax':>8} {'Hapax %':>8} {'Repeater':>10} {'Repeat %':>10}")
print(f"  {'-'*45}")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    hc = hapax_roles.get(role, 0)
    rc = repeater_roles.get(role, 0)
    hp = hc / len(hapax_types) * 100 if hapax_types else 0
    rp = rc / len(repeater_types) * 100 if repeater_types else 0
    print(f"  {role:<6} {hc:>8} {hp:>7.1f}% {rc:>10} {rp:>9.1f}%")

# Mann-Whitney U test: are repeaters shorter?
u_stat, p_val = mannwhitneyu(hapax_lengths, repeater_lengths, alternative='greater')
print(f"\nLength comparison: Hapax mean={np.mean(hapax_lengths):.2f} vs Repeater mean={np.mean(repeater_lengths):.2f}")
print(f"  Mann-Whitney U (hapax > repeater): U={u_stat:.0f}, p={p_val:.4f}")
print(f"  {'Hapax ARE significantly longer' if p_val < 0.05 else 'No significant length difference'}")

# ==============================================================================
# SECTION 3: AX-UN BOUNDARY TEST
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 3: AX-UN BOUNDARY TEST")
print("=" * 70)

# AX-typical prefixes (from census: ol, lk, pch, yk, lch, te, po, so, or, ke, tch all map 100% to AX)
AX_PREFIXES = {'ol', 'lk', 'pch', 'yk', 'lch', 'te', 'po', 'so', 'or', 'ke', 'tch',
               'dch', 'se', 'de', 'pe', 'ko', 'to', 'do', 'ka', 'ta', 'sa', 'ar'}

# UN tokens with AX-typical prefixes
ax_predicted_un = [(t, m) for t, m in un_list if m.prefix in AX_PREFIXES]
non_ax_un = [(t, m) for t, m in un_list if m.prefix not in AX_PREFIXES]

print(f"\nUN tokens with AX-typical prefixes: {len(ax_predicted_un)} ({len(ax_predicted_un)/len(un_list)*100:.1f}%)")
print(f"UN tokens with non-AX prefixes: {len(non_ax_un)} ({len(non_ax_un)/len(un_list)*100:.1f}%)")

# Position distribution: compare AX-predicted UN to actual AX tokens
# Get classified AX tokens
ax_classified = [(t, m) for t, role, m in classified if role == 'AX']

# Position = ordinal position within line (0-indexed)
line_positions = defaultdict(list)
for t in b_tokens:
    line_positions[(t.folio, t.line)].append(t.word)

# Compute relative position (0=start, 1=end) for each token
def get_relative_position(token):
    """Get relative position of token within its line."""
    key = (token.folio, token.line)
    words = line_positions[key]
    n = len(words)
    if n <= 1:
        return 0.5
    try:
        # Find first occurrence of this word in the line
        idx = words.index(token.word)
        return idx / (n - 1)
    except ValueError:
        return 0.5

# Sample positions (avoid computing for every token)
np.random.seed(42)
sample_size = min(500, len(ax_predicted_un), len(ax_classified))

if sample_size > 0:
    ax_un_sample = [ax_predicted_un[i] for i in np.random.choice(len(ax_predicted_un), sample_size, replace=False)]
    ax_cls_sample = [ax_classified[i] for i in np.random.choice(len(ax_classified), sample_size, replace=False)]

    ax_un_positions = [get_relative_position(t) for t, _ in ax_un_sample]
    ax_cls_positions = [get_relative_position(t) for t, _ in ax_cls_sample]

    print(f"\nPosition distribution (relative, 0=start, 1=end):")
    print(f"  AX-predicted UN: mean={np.mean(ax_un_positions):.3f}, std={np.std(ax_un_positions):.3f}")
    print(f"  Classified AX:   mean={np.mean(ax_cls_positions):.3f}, std={np.std(ax_cls_positions):.3f}")

    u_stat, p_val = mannwhitneyu(ax_un_positions, ax_cls_positions, alternative='two-sided')
    print(f"  Mann-Whitney U: U={u_stat:.0f}, p={p_val:.4f}")
    print(f"  {'Similar positions' if p_val > 0.05 else 'DIFFERENT positions'}")

# Transition analysis: what precedes/follows AX-predicted UN vs classified AX?
print(f"\nTransition context analysis:")

# Build token sequences per line
line_seqs = defaultdict(list)
for t in b_tokens:
    line_seqs[(t.folio, t.line)].append(t)

def get_context(target_tokens, position='prev'):
    """Get the ICC role of tokens before/after targets."""
    contexts = Counter()
    for t_target in target_tokens:
        key = (t_target.folio, t_target.line)
        seq = line_seqs[key]
        for i, t in enumerate(seq):
            if t.word == t_target.word and t.folio == t_target.folio:
                if position == 'prev' and i > 0:
                    prev_word = seq[i-1].word
                    if prev_word in token_to_class:
                        cls = str(token_to_class[prev_word])
                        role = ROLE_ABBREV.get(class_to_role.get(cls, ''), '?')
                        contexts[role] += 1
                    else:
                        contexts['UN'] += 1
                elif position == 'next' and i < len(seq) - 1:
                    next_word = seq[i+1].word
                    if next_word in token_to_class:
                        cls = str(token_to_class[next_word])
                        role = ROLE_ABBREV.get(class_to_role.get(cls, ''), '?')
                        contexts[role] += 1
                    else:
                        contexts['UN'] += 1
                break
    return contexts

# Use sampled tokens for efficiency
ax_un_targets = [t for t, _ in ax_un_sample] if sample_size > 0 else []
ax_cls_targets = [t for t, _ in ax_cls_sample] if sample_size > 0 else []

if ax_un_targets:
    ax_un_prev = get_context(ax_un_targets, 'prev')
    ax_cls_prev = get_context(ax_cls_targets, 'prev')

    print(f"\n  Preceding role distribution:")
    print(f"  {'Role':<6} {'AX-UN':>8} {'AX-CLS':>8}")
    print(f"  {'-'*25}")
    all_roles = set(list(ax_un_prev.keys()) + list(ax_cls_prev.keys()))
    for role in ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']:
        un_c = ax_un_prev.get(role, 0)
        cls_c = ax_cls_prev.get(role, 0)
        un_p = un_c / sum(ax_un_prev.values()) * 100 if ax_un_prev else 0
        cls_p = cls_c / sum(ax_cls_prev.values()) * 100 if ax_cls_prev else 0
        print(f"  {role:<6} {un_p:>7.1f}% {cls_p:>7.1f}%")

    ax_un_next = get_context(ax_un_targets, 'next')
    ax_cls_next = get_context(ax_cls_targets, 'next')

    print(f"\n  Following role distribution:")
    print(f"  {'Role':<6} {'AX-UN':>8} {'AX-CLS':>8}")
    print(f"  {'-'*25}")
    for role in ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']:
        un_c = ax_un_next.get(role, 0)
        cls_c = ax_cls_next.get(role, 0)
        un_p = un_c / sum(ax_un_next.values()) * 100 if ax_un_next else 0
        cls_p = cls_c / sum(ax_cls_next.values()) * 100 if ax_cls_next else 0
        print(f"  {role:<6} {un_p:>7.1f}% {cls_p:>7.1f}%")

# Summary verdict on AX-UN boundary
print(f"\nAX-UN Boundary Verdict:")
print(f"  AX-predicted UN tokens: {len(ax_predicted_un)}")
print(f"  Classified AX tokens: {len(ax_classified)}")
print(f"  If absorbed, AX would grow from {len(ax_classified)} to {len(ax_classified)+len(ax_predicted_un)} "
      f"({(len(ax_classified)+len(ax_predicted_un))/len(b_tokens)*100:.1f}% of B)")

# ==============================================================================
# SECTION 4: FOLIO-LEVEL UN PREDICTORS
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 4: FOLIO-LEVEL UN PREDICTORS")
print("=" * 70)

# Folio-level variables
folio_list = sorted(set(t.folio for t in b_tokens))
total_by_folio = Counter(t.folio for t in b_tokens)
un_by_folio = Counter(t.folio for t, _ in un_list)

folio_un_pct = np.array([un_by_folio.get(f, 0) / total_by_folio[f] for f in folio_list])

# REGIME
folio_regime = np.array([{'REGIME_1': 1, 'REGIME_2': 2, 'REGIME_3': 3, 'REGIME_4': 4}.get(
    folio_to_regime.get(f, ''), 0) for f in folio_list])

# Escape density: count tokens with 'dy' or 'edy' suffix as escape proxy
folio_escape = defaultdict(int)
folio_total_for_escape = defaultdict(int)
for t in b_tokens:
    m = morph.extract(t.word)
    folio_total_for_escape[t.folio] += 1
    if m.suffix and ('dy' in m.suffix or 'edy' in m.suffix):
        folio_escape[t.folio] += 1

folio_escape_density = np.array([folio_escape.get(f, 0) / folio_total_for_escape.get(f, 1) for f in folio_list])

# ch_preference: proportion of tokens with ch prefix
folio_ch = defaultdict(int)
for t in b_tokens:
    m = morph.extract(t.word)
    if m.prefix == 'ch':
        folio_ch[t.folio] += 1

folio_ch_pref = np.array([folio_ch.get(f, 0) / total_by_folio[f] for f in folio_list])

# LINK density
folio_link = defaultdict(int)
for t in b_tokens:
    if 'ol' in t.word:
        folio_link[t.folio] += 1

folio_link_density = np.array([folio_link.get(f, 0) / total_by_folio[f] for f in folio_list])

# Token diversity (type/token ratio)
folio_types = defaultdict(set)
for t in b_tokens:
    folio_types[t.folio].add(t.word)
folio_ttr = np.array([len(folio_types[f]) / total_by_folio[f] for f in folio_list])

# Correlations with Bonferroni correction
print(f"\nSpearman correlations: folio UN proportion vs folio-level variables")
variables = {
    'escape_density': folio_escape_density,
    'ch_preference': folio_ch_pref,
    'link_density': folio_link_density,
    'type_token_ratio': folio_ttr,
}

n_tests = len(variables)
print(f"  {'Variable':<20} {'rho':>8} {'p':>10} {'p_bonf':>10} {'Sig':>5}")
print(f"  {'-'*55}")

for name, arr in variables.items():
    rho, p = spearmanr(folio_un_pct, arr)
    p_bonf = min(p * n_tests, 1.0)
    sig = '***' if p_bonf < 0.001 else ('**' if p_bonf < 0.01 else ('*' if p_bonf < 0.05 else ''))
    print(f"  {name:<20} {rho:>+8.3f} {p:>10.4f} {p_bonf:>10.4f} {sig:>5}")

# REGIME comparison (non-parametric)
print(f"\n  UN proportion by REGIME:")
for regime_val in [1, 2, 3, 4]:
    mask = folio_regime == regime_val
    if mask.sum() > 0:
        vals = folio_un_pct[mask]
        print(f"    REGIME_{regime_val}: mean={vals.mean():.3f}, n={mask.sum()}")

# Kruskal-Wallis test
from scipy.stats import kruskal
groups = [folio_un_pct[folio_regime == i] for i in [1, 2, 3, 4] if (folio_regime == i).sum() > 0]
if len(groups) >= 2:
    h_stat, p_val = kruskal(*groups)
    print(f"\n  Kruskal-Wallis (UN ~ REGIME): H={h_stat:.2f}, p={p_val:.4f}")
    print(f"  {'REGIME significantly affects UN proportion' if p_val < 0.05 else 'No significant REGIME effect'}")

# Does higher UN = more complex programs?
print(f"\n--- INTERPRETATION ---")
print(f"  Type-token ratio correlation with UN: ", end="")
rho_ttr, p_ttr = spearmanr(folio_un_pct, folio_ttr)
if rho_ttr > 0 and p_ttr < 0.05:
    print(f"POSITIVE (rho={rho_ttr:+.3f}, p={p_ttr:.4f})")
    print(f"  Higher UN proportion = higher lexical diversity = more unique tokens")
elif rho_ttr < 0 and p_ttr < 0.05:
    print(f"NEGATIVE (rho={rho_ttr:+.3f}, p={p_ttr:.4f})")
else:
    print(f"NOT SIGNIFICANT (rho={rho_ttr:+.3f}, p={p_ttr:.4f})")

# ==============================================================================
# SAVE RESULTS
# ==============================================================================

results = {
    'clustering': cluster_results,
    'best_k': best_k,
    'best_silhouette': round(best_sil, 3),
    'hapax_vs_repeater': {
        'hapax_types': len(hapax_types),
        'repeater_types': len(repeater_types),
        'hapax_prefix_rate': round(hapax_prefix_rate, 3),
        'repeater_prefix_rate': round(repeater_prefix_rate, 3),
        'hapax_suffix_rate': round(hapax_suffix_rate, 3),
        'repeater_suffix_rate': round(repeater_suffix_rate, 3),
        'hapax_art_rate': round(hapax_art_rate, 3),
        'repeater_art_rate': round(repeater_art_rate, 3),
        'hapax_mean_length': round(float(np.mean(hapax_lengths)), 2),
        'repeater_mean_length': round(float(np.mean(repeater_lengths)), 2),
    },
    'ax_un_boundary': {
        'ax_predicted_un': len(ax_predicted_un),
        'classified_ax': len(ax_classified),
        'ax_if_absorbed_pct': round((len(ax_classified) + len(ax_predicted_un)) / len(b_tokens) * 100, 1),
    },
}

output_path = 'phases/UN_COMPOSITIONAL_MECHANICS/results/un_population_test.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\n{'=' * 70}")
print("UN POPULATION TEST COMPLETE")
print(f"{'=' * 70}")
