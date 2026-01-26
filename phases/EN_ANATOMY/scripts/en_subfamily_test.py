"""
Script 3: EN Subfamily Test

Test whether EN classes form genuine subfamilies or collapse like AX (C572).
Uses features from Script 2 and census from Script 1.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
FEATURES_FILE = BASE / 'phases/EN_ANATOMY/results/en_features.json'
CENSUS_FILE = BASE / 'phases/EN_ANATOMY/results/en_census.json'
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
RESULTS = BASE / 'phases/EN_ANATOMY/results'

# Load results from Phase 1
with open(FEATURES_FILE) as f:
    features_raw = json.load(f)
# Keys are strings
features = {int(k): v for k, v in features_raw.items()}

with open(CENSUS_FILE) as f:
    census = json.load(f)

EN_CLASSES = set(census['definitive_en_classes'])
QO_FAMILY = set(census['prefix_families']['QO'])
CHSH_FAMILY = set(census['prefix_families']['CH_SH'])
MINOR_FAMILY = set(census['prefix_families']['MINOR'])

# Load class map for transition analysis
with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Load transcript for transition profiles
tx = Transcript()
tokens = list(tx.currier_b())

# Assign subfamily labels
def get_subfamily(cls):
    if cls in QO_FAMILY: return 'QO'
    if cls in CHSH_FAMILY: return 'CHSH'
    if cls in MINOR_FAMILY: return 'MINOR'
    return 'UNKNOWN'

print("=" * 70)
print("EN SUBFAMILY TEST")
print("=" * 70)

# ============================================================
# 1. FEATURE MATRIX FOR CLUSTERING
# ============================================================
print("\n" + "-" * 70)
print("1. CLUSTERING ANALYSIS")
print("-" * 70)

# Build feature vectors
# Features: mean_position, var_position, initial_rate, final_rate,
#           regime_entropy, regime_1_share, regime_4_share,
#           bio_share, recipe_b_share, pharma_share,
#           prefix_rate, suffix_rate,
#           self_chain_rate, en_chain_rate

feature_names = [
    'mean_position', 'var_position', 'initial_rate', 'final_rate',
    'regime_entropy', 'regime_1_share', 'regime_4_share',
    'bio_share', 'recipe_b_share', 'pharma_share',
    'prefix_rate', 'suffix_rate',
    'self_chain_rate', 'en_chain_rate'
]

class_ids = sorted(features.keys())
X = np.zeros((len(class_ids), len(feature_names)))

for i, cls in enumerate(class_ids):
    f = features[cls]
    X[i, 0] = f['mean_position']
    X[i, 1] = f['var_position']
    X[i, 2] = f['initial_rate']
    X[i, 3] = f['final_rate']
    X[i, 4] = f['regime_entropy']
    X[i, 5] = f['regime_shares']['REGIME_1']
    X[i, 6] = f['regime_shares']['REGIME_4']
    X[i, 7] = f['section_shares']['BIO']
    X[i, 8] = f['section_shares']['RECIPE_B']
    X[i, 9] = f['section_shares']['PHARMA']
    X[i, 10] = f['prefix_rate']
    X[i, 11] = f['suffix_rate']
    X[i, 12] = f['self_chain_rate']
    X[i, 13] = f['en_chain_rate']

# Z-score normalize
means = X.mean(axis=0)
stds = X.std(axis=0)
stds[stds == 0] = 1  # prevent division by zero
X_z = (X - means) / stds

# Hierarchical clustering
Z = linkage(X_z, method='ward')

# Test k=2..6
silhouettes = {}
for k in range(2, 7):
    labels = fcluster(Z, t=k, criterion='maxclust')
    if len(set(labels)) < 2:
        continue
    # Compute silhouette manually (avoid sklearn dependency)
    dists = squareform(pdist(X_z))
    n = len(labels)
    sil_scores = []
    for idx in range(n):
        own_cluster = labels[idx]
        own_mask = labels == own_cluster
        if own_mask.sum() <= 1:
            sil_scores.append(0)
            continue
        a_i = dists[idx, own_mask].sum() / (own_mask.sum() - 1)
        b_i = float('inf')
        for other_cluster in set(labels):
            if other_cluster == own_cluster:
                continue
            other_mask = labels == other_cluster
            b_candidate = dists[idx, other_mask].mean()
            b_i = min(b_i, b_candidate)
        sil_scores.append((b_i - a_i) / max(a_i, b_i))
    silhouettes[k] = np.mean(sil_scores)

print(f"\nSilhouette scores by k:")
best_k = max(silhouettes, key=silhouettes.get)
for k, s in sorted(silhouettes.items()):
    marker = " <-- BEST" if k == best_k else ""
    print(f"  k={k}: {s:.3f}{marker}")

# Show cluster assignments for best k
best_labels = fcluster(Z, t=best_k, criterion='maxclust')
print(f"\nCluster assignments (k={best_k}):")
for cluster in sorted(set(best_labels)):
    members = [class_ids[i] for i in range(len(class_ids)) if best_labels[i] == cluster]
    subfamilies = [get_subfamily(c) for c in members]
    print(f"  Cluster {cluster}: {members} ({Counter(subfamilies)})")

# Also show k=2 for comparison with AX (which had 0.232)
labels_k2 = fcluster(Z, t=2, criterion='maxclust')
print(f"\nk=2 clusters (for AX comparison, AX silhouette was 0.232):")
print(f"  Silhouette: {silhouettes[2]:.3f}")
for cluster in sorted(set(labels_k2)):
    members = [class_ids[i] for i in range(len(class_ids)) if labels_k2[i] == cluster]
    subfamilies = [get_subfamily(c) for c in members]
    print(f"  Cluster {cluster}: {members} ({Counter(subfamilies)})")

# Check if prefix-family aligns with data-driven clusters
# Purity: what fraction of each cluster is from one subfamily?
purity_scores = []
for cluster in sorted(set(labels_k2)):
    members = [class_ids[i] for i in range(len(class_ids)) if labels_k2[i] == cluster]
    subfamilies = [get_subfamily(c) for c in members]
    sf_counter = Counter(subfamilies)
    most_common_count = sf_counter.most_common(1)[0][1]
    purity = most_common_count / len(members)
    purity_scores.append(purity)
    print(f"  Cluster {cluster} purity: {purity:.1%}")

mean_purity = np.mean(purity_scores)
print(f"  Mean purity: {mean_purity:.1%}")

# ============================================================
# 2. KRUSKAL-WALLIS: QO vs CHSH vs MINOR
# ============================================================
print("\n" + "-" * 70)
print("2. KRUSKAL-WALLIS H-TEST: QO vs CHSH (per feature)")
print("-" * 70)

# Per-token distributional comparison
# For each feature, collect per-class values by subfamily
print(f"\n{'Feature':>20} {'H-stat':>8} {'p-value':>10} {'QO_mean':>8} {'CHSH_mean':>9} {'Sig?'}")
print("-" * 65)

kw_results = {}
for j, fname in enumerate(feature_names):
    qo_vals = [X[i, j] for i, cls in enumerate(class_ids) if cls in QO_FAMILY]
    chsh_vals = [X[i, j] for i, cls in enumerate(class_ids) if cls in CHSH_FAMILY]

    if len(qo_vals) < 2 or len(chsh_vals) < 2:
        continue

    # Skip constant features (all identical values)
    if np.std(qo_vals + chsh_vals) < 1e-10:
        print(f"{fname:>20} {'CONST':>8} {'N/A':>10} {np.mean(qo_vals):8.3f} {np.mean(chsh_vals):9.3f}")
        continue

    h_stat, p_val = stats.kruskal(qo_vals, chsh_vals)
    qo_mean = np.mean(qo_vals)
    chsh_mean = np.mean(chsh_vals)
    sig = '*' if p_val < 0.05 else ''
    print(f"{fname:>20} {h_stat:8.2f} {p_val:10.4f} {qo_mean:8.3f} {chsh_mean:9.3f} {sig}")
    kw_results[fname] = {
        'h_stat': round(h_stat, 4),
        'p_value': round(p_val, 6),
        'qo_mean': round(qo_mean, 4),
        'chsh_mean': round(chsh_mean, 4),
    }

sig_features = [f for f, r in kw_results.items() if r['p_value'] < 0.05]
print(f"\nSignificant features (p<0.05): {len(sig_features)}/{len(kw_results)}")
if sig_features:
    print(f"  {sig_features}")

# ============================================================
# 3. SECTION x SUBFAMILY INDEPENDENCE
# ============================================================
print("\n" + "-" * 70)
print("3. SECTION x SUBFAMILY INDEPENDENCE TEST")
print("-" * 70)

# Count tokens by section and subfamily
lines_struct = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    if cls is not None and cls in EN_CLASSES:
        lines_struct[(token.folio, token.line)].append({
            'class': cls,
            'subfamily': get_subfamily(cls),
            'folio': token.folio,
        })

def get_section(folio):
    try:
        num = int(''.join(c for c in folio if c.isdigit())[:3])
    except:
        return 'UNKNOWN'
    if num <= 25: return 'HERBAL_A'
    elif num <= 56: return 'HERBAL_B'
    elif num <= 67: return 'PHARMA'
    elif num <= 73: return 'ASTRO'
    elif num <= 84: return 'BIO'
    elif num <= 86: return 'COSMO'
    elif num <= 102: return 'RECIPE_A'
    else: return 'RECIPE_B'

section_subfamily = defaultdict(lambda: defaultdict(int))
for token in tokens:
    word = token.word.replace('*', '').strip()
    cls = token_to_class.get(word)
    if cls is None or cls not in EN_CLASSES:
        continue
    section = get_section(token.folio)
    sf = get_subfamily(cls)
    section_subfamily[section][sf] += 1

# Build contingency table (sections x subfamilies)
sections = ['HERBAL_B', 'PHARMA', 'BIO', 'RECIPE_A', 'RECIPE_B']
subfamilies = ['QO', 'CHSH', 'MINOR']
contingency = np.zeros((len(sections), len(subfamilies)), dtype=int)

print(f"\n{'Section':>12} {'QO':>6} {'CHSH':>6} {'MINOR':>6} {'Total':>6} {'QO%':>6} {'CHSH%':>7}")
for i, sec in enumerate(sections):
    for j, sf in enumerate(subfamilies):
        contingency[i, j] = section_subfamily[sec][sf]
    total = contingency[i].sum()
    qo_pct = contingency[i, 0] / total * 100 if total > 0 else 0
    chsh_pct = contingency[i, 1] / total * 100 if total > 0 else 0
    print(f"{sec:>12} {contingency[i,0]:>6} {contingency[i,1]:>6} {contingency[i,2]:>6} {total:>6} {qo_pct:>5.1f} {chsh_pct:>6.1f}")

chi2, chi_p, dof, expected = stats.chi2_contingency(contingency)
print(f"\nChi-square: chi2={chi2:.2f}, df={dof}, p={chi_p:.6f}")
print(f"Section x Subfamily independence: {'REJECTED (dependent)' if chi_p < 0.01 else 'NOT REJECTED'}")

# Effect size: Cramer's V
n_total = contingency.sum()
min_dim = min(len(sections), len(subfamilies)) - 1
cramers_v = np.sqrt(chi2 / (n_total * min_dim))
print(f"Cramer's V: {cramers_v:.3f}")

# PHARMA focus: QO vs CHSH ratio
pharma_idx = sections.index('PHARMA')
bio_idx = sections.index('BIO')
pharma_qo = contingency[pharma_idx, 0]
pharma_chsh = contingency[pharma_idx, 1]
bio_qo = contingency[bio_idx, 0]
bio_chsh = contingency[bio_idx, 1]

print(f"\nPHARMA: QO={pharma_qo}, CHSH={pharma_chsh}, ratio={pharma_qo/(pharma_chsh+0.001):.2f}")
print(f"BIO: QO={bio_qo}, CHSH={bio_chsh}, ratio={bio_qo/(bio_chsh+0.001):.2f}")
if pharma_chsh > 0 and bio_chsh > 0:
    pharma_ratio = pharma_qo / pharma_chsh
    bio_ratio = bio_qo / bio_chsh
    print(f"PHARMA is {'QO-enriched' if pharma_ratio > bio_ratio else 'CHSH-enriched'} vs BIO")

# ============================================================
# 4. REGIME x SUBFAMILY SELECTION
# ============================================================
print("\n" + "-" * 70)
print("4. REGIME x SUBFAMILY SELECTION TEST")
print("-" * 70)

from pathlib import Path
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
with open(REGIME_FILE) as f:
    regime_data = json.load(f)
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

regime_subfamily = defaultdict(lambda: defaultdict(int))
for token in tokens:
    word = token.word.replace('*', '').strip()
    cls = token_to_class.get(word)
    if cls is None or cls not in EN_CLASSES:
        continue
    regime = folio_regime.get(token.folio, 'UNKNOWN')
    sf = get_subfamily(cls)
    regime_subfamily[regime][sf] += 1

regimes = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
contingency_r = np.zeros((len(regimes), len(subfamilies)), dtype=int)

print(f"\n{'Regime':>12} {'QO':>6} {'CHSH':>6} {'MINOR':>6} {'Total':>6} {'QO%':>6} {'CHSH%':>7}")
for i, reg in enumerate(regimes):
    for j, sf in enumerate(subfamilies):
        contingency_r[i, j] = regime_subfamily[reg][sf]
    total = contingency_r[i].sum()
    qo_pct = contingency_r[i, 0] / total * 100 if total > 0 else 0
    chsh_pct = contingency_r[i, 1] / total * 100 if total > 0 else 0
    print(f"{reg:>12} {contingency_r[i,0]:>6} {contingency_r[i,1]:>6} {contingency_r[i,2]:>6} {total:>6} {qo_pct:>5.1f} {chsh_pct:>6.1f}")

chi2_r, chi_p_r, dof_r, _ = stats.chi2_contingency(contingency_r)
cramers_v_r = np.sqrt(chi2_r / (contingency_r.sum() * (min(len(regimes), len(subfamilies)) - 1)))
print(f"\nChi-square: chi2={chi2_r:.2f}, df={dof_r}, p={chi_p_r:.6f}")
print(f"Cramer's V: {cramers_v_r:.3f}")
print(f"Regime x Subfamily independence: {'REJECTED' if chi_p_r < 0.01 else 'NOT REJECTED'}")

# ============================================================
# 5. J-S DIVERGENCE ON TRANSITION PROFILES
# ============================================================
print("\n" + "-" * 70)
print("5. JENSEN-SHANNON DIVERGENCE BETWEEN SUBFAMILIES")
print("-" * 70)

# Build transition profiles: what role/class follows each subfamily?
# Profile = distribution over next-token roles
lines_full = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    sf = get_subfamily(cls) if cls and cls in EN_CLASSES else None
    ICC_CC = {10, 11, 12, 17}
    ICC_FL = {7, 30, 38, 40}
    ICC_FQ = {9, 13, 23}
    AX_CLASSES = {1, 2, 3, 4, 5, 6, 14, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29}
    if cls in ICC_CC: role = 'CC'
    elif cls in EN_CLASSES: role = 'EN'
    elif cls in ICC_FL: role = 'FL'
    elif cls in ICC_FQ: role = 'FQ'
    elif cls in AX_CLASSES: role = 'AX'
    else: role = 'UN'
    lines_full[(token.folio, token.line)].append({
        'role': role,
        'subfamily': sf,
    })

# Right-context profiles by subfamily
right_profiles = defaultdict(Counter)
for (folio, line_id), line_tokens in lines_full.items():
    for i in range(len(line_tokens) - 1):
        sf = line_tokens[i]['subfamily']
        if sf:
            right_role = line_tokens[i+1]['role']
            right_profiles[sf][right_role] += 1

roles_list = sorted(set(r for c in right_profiles.values() for r in c))

def to_prob(counter, categories):
    total = sum(counter.values())
    if total == 0:
        return np.ones(len(categories)) / len(categories)
    return np.array([counter.get(c, 0) / total for c in categories])

def js_divergence(p, q):
    """Jensen-Shannon divergence"""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    # Add small epsilon to avoid log(0)
    p = p + 1e-10
    q = q + 1e-10
    p = p / p.sum()
    q = q / q.sum()
    m = (p + q) / 2
    return 0.5 * np.sum(p * np.log2(p / m)) + 0.5 * np.sum(q * np.log2(q / m))

print(f"\nRight-context profiles (distribution over next role):")
print(f"{'Role':>6}", end="")
for sf in ['QO', 'CHSH', 'MINOR']:
    print(f"  {sf:>7}", end="")
print()

for role in roles_list:
    print(f"{role:>6}", end="")
    for sf in ['QO', 'CHSH', 'MINOR']:
        total = sum(right_profiles[sf].values())
        pct = right_profiles[sf].get(role, 0) / total * 100 if total > 0 else 0
        print(f"  {pct:6.1f}%", end="")
    print()

# Pairwise J-S divergences
pairs = [('QO', 'CHSH'), ('QO', 'MINOR'), ('CHSH', 'MINOR')]
print(f"\nPairwise Jensen-Shannon divergences:")
js_results = {}
for sf1, sf2 in pairs:
    p1 = to_prob(right_profiles[sf1], roles_list)
    p2 = to_prob(right_profiles[sf2], roles_list)
    jsd = js_divergence(p1, p2)
    js_results[f"{sf1}_vs_{sf2}"] = round(jsd, 6)
    print(f"  {sf1} vs {sf2}: JSD = {jsd:.6f}")

# ============================================================
# 6. CONTEXT CLASSIFIER: Can context predict subfamily?
# ============================================================
print("\n" + "-" * 70)
print("6. CONTEXT PREDICTION TEST")
print("-" * 70)

# For each EN token, use left+right role context to predict subfamily
# Compare accuracy to majority baseline
context_features = []  # (left_role, right_role, subfamily)

for (folio, line_id), line_tokens in lines_full.items():
    n = len(line_tokens)
    for i, tok in enumerate(line_tokens):
        sf = tok['subfamily']
        if sf not in ('QO', 'CHSH'):
            continue
        left_role = line_tokens[i-1]['role'] if i > 0 else 'BOUNDARY'
        right_role = line_tokens[i+1]['role'] if i < n-1 else 'BOUNDARY'
        context_features.append((left_role, right_role, sf))

# Majority baseline
sf_counts = Counter(c[2] for c in context_features)
majority_class = sf_counts.most_common(1)[0][0]
majority_pct = sf_counts.most_common(1)[0][1] / len(context_features) * 100

print(f"\nTotal core EN tokens with context: {len(context_features)}")
print(f"QO: {sf_counts['QO']} ({sf_counts['QO']/len(context_features)*100:.1f}%)")
print(f"CHSH: {sf_counts['CHSH']} ({sf_counts['CHSH']/len(context_features)*100:.1f}%)")
print(f"Majority baseline: {majority_pct:.1f}% ({majority_class})")

# Simple rule-based classifier using left context
# For each left_role, predict the more common subfamily
left_predictions = {}
left_context_counts = defaultdict(Counter)
for left, right, sf in context_features:
    left_context_counts[left][sf] += 1

print(f"\nLeft-context prediction rules:")
correct = 0
for left, sf_counter in sorted(left_context_counts.items(), key=lambda x: -sum(x[1].values())):
    best_sf = sf_counter.most_common(1)[0][0]
    total = sum(sf_counter.values())
    accuracy = sf_counter[best_sf] / total * 100
    correct += sf_counter[best_sf]
    left_predictions[left] = best_sf
    print(f"  {left:>10} -> {best_sf} ({accuracy:.1f}%, n={total})")

context_accuracy = correct / len(context_features) * 100
improvement = context_accuracy - majority_pct
print(f"\nContext classifier accuracy: {context_accuracy:.1f}%")
print(f"Improvement over majority: {improvement:.1f} percentage points")
print(f"(AX context prediction was ~6.8% improvement)")

# ============================================================
# 7. OVERALL STRUCTURAL VERDICT
# ============================================================
print("\n" + "-" * 70)
print("7. STRUCTURAL VERDICT")
print("-" * 70)

# Collect evidence
best_sil = silhouettes[best_k]
sil_k2 = silhouettes[2]
n_sig_features = len(sig_features)
section_dependent = chi_p < 0.01
regime_dependent = chi_p_r < 0.01
max_jsd = max(js_results.values())
context_gain = improvement

print(f"\nEvidence summary:")
print(f"  Best silhouette: {best_sil:.3f} (k={best_k})")
print(f"  k=2 silhouette: {sil_k2:.3f} (AX was 0.232)")
print(f"  Significant KW features: {n_sig_features}/{len(kw_results)}")
print(f"  Section x Subfamily: {'DEPENDENT' if section_dependent else 'INDEPENDENT'} (V={cramers_v:.3f})")
print(f"  Regime x Subfamily: {'DEPENDENT' if regime_dependent else 'INDEPENDENT'} (V={cramers_v_r:.3f})")
print(f"  Max J-S divergence: {max_jsd:.4f}")
print(f"  Context prediction gain: {context_gain:.1f}pp")

# Verdict
if sil_k2 > 0.40 and n_sig_features >= 3 and section_dependent:
    verdict = 'GENUINE_SUBFAMILIES'
    explanation = 'Strong clustering, multiple distinguishing features, section-dependent selection'
elif sil_k2 > 0.25 and (n_sig_features >= 1 or section_dependent):
    verdict = 'PARTIAL_STRUCTURE'
    explanation = 'Moderate clustering with some distinguishing features'
else:
    verdict = 'DISTRIBUTIONAL_CONVERGENCE'
    explanation = ('Weak distributional clustering (identical positions, REGIME, context); '
                   'but vocabulary divergence (MIDDLE Jaccard) and trigger divergence (chi2) '
                   'may indicate PREFIX-gated subvocabulary access (C276, C423)')

print(f"\n  VERDICT: {verdict}")
print(f"  Explanation: {explanation}")

# ============================================================
# SAVE RESULTS
# ============================================================
results = {
    'clustering': {
        'silhouettes': {str(k): round(v, 4) for k, v in silhouettes.items()},
        'best_k': best_k,
        'best_silhouette': round(best_sil, 4),
        'k2_silhouette': round(sil_k2, 4),
        'k2_clusters': {
            str(cluster): [class_ids[i] for i in range(len(class_ids)) if labels_k2[i] == cluster]
            for cluster in sorted(set(labels_k2))
        },
        'k2_purity': round(mean_purity, 4),
    },
    'kruskal_wallis': kw_results,
    'significant_features': sig_features,
    'section_independence': {
        'chi2': round(chi2, 4),
        'p_value': round(chi_p, 8),
        'cramers_v': round(cramers_v, 4),
        'rejected': bool(section_dependent),
    },
    'regime_independence': {
        'chi2': round(chi2_r, 4),
        'p_value': round(chi_p_r, 8),
        'cramers_v': round(cramers_v_r, 4),
        'rejected': bool(regime_dependent),
    },
    'js_divergences': js_results,
    'context_prediction': {
        'accuracy': round(context_accuracy, 2),
        'majority_baseline': round(majority_pct, 2),
        'improvement_pp': round(improvement, 2),
    },
    'verdict': verdict,
    'explanation': explanation,
}

with open(RESULTS / 'en_subfamily_test.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'en_subfamily_test.json'}")
