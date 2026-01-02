# Illustration Coupling Analysis
# Pre-registered, semantics-free test for operational coupling between illustrations and execution
#
# Tests whether "illustrated folios" (IF) show different execution behavior than
# "non-illustrated folios" (NIF) - without assuming what illustrations depict

import json
import re
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime
from itertools import combinations
import random

print("=" * 70)
print("ILLUSTRATION COUPLING ANALYSIS")
print("Pre-registered test: Do illustrations affect execution behavior?")
print("=" * 70)

# =============================================================================
# FOLIO CLASSIFICATION: IF vs NIF
# =============================================================================
# Based on standard Voynich manuscript paleographic structure:
# - IF (Illustrated Folios): Pages with dominant central illustration
#   - Herbal A/B: f1-f66, f87-f102 (large botanical-style illustrations)
#   - Cosmological: f67-f73, f85-f86 (circular diagrams)
#   - Zodiac: f70-f74 (circular with figures)
#
# - NIF (Non-Illustrated Folios): Pages that are primarily text
#   - Recipe/Pharmaceutical: f103-f116 (dense text blocks, minimal imagery)
#   - Some pharmaceutical: f75-f84 (text with small marginal containers)
#
# For rigorous testing, we use CONSERVATIVE classification:
# - IF: folios where illustration is dominant visual element (>50% page area)
# - NIF: folios where text is dominant visual element

def classify_folio_type(folio_id):
    """Classify folio as IF (illustrated) or NIF (non-illustrated)."""
    # Extract base folio number
    match = re.match(r'f(\d+)', folio_id)
    if not match:
        return None

    num = int(match.group(1))

    # Herbal A: f1-f66 (illustrated)
    if 1 <= num <= 66:
        return "IF"

    # Cosmological circular: f67-f73 (illustrated - circular diagrams)
    if 67 <= num <= 73:
        return "IF"

    # Pharmaceutical: f75-f84 (borderline - has small container images)
    # Classify as NIF for conservative test (text-dominant)
    if 75 <= num <= 84:
        return "NIF"

    # Cosmological fold-outs: f85-f86 (illustrated - complex diagrams)
    if 85 <= num <= 86:
        return "IF"

    # Herbal B: f87-f102 (illustrated)
    if 87 <= num <= 102:
        return "IF"

    # Recipe text: f103-f116 (non-illustrated - dense text)
    if 103 <= num <= 116:
        return "NIF"

    return None

# =============================================================================
# DATA LOADING
# =============================================================================

print("\n[1] Loading data...")

# Load corpus
def load_corpus():
    records = []
    with open('C:/git/voynich/data/transcriptions/interlinear_full_words.txt', 'r', encoding='latin-1') as f:
        f.readline()  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 12:
                parts = [p.strip('"') for p in parts]
                records.append({
                    'word': parts[0],
                    'folio': parts[2],
                    'line': parts[11] if len(parts) > 11 else '0'
                })
    return records

# Load forbidden transitions
def load_forbidden_transitions():
    with open('C:/git/voynich/phase18a_forbidden_inventory.json', 'r') as f:
        data = json.load(f)
    forbidden = set()
    for trans in data.get('transitions', []):
        source = trans.get('source', '')
        target = trans.get('target', '')
        if source and target:
            forbidden.add((source, target))
    return forbidden

# Load semantic states (for STATE-C detection)
def load_semantic_states():
    with open('C:/git/voynich/phase13a_semantic_states.json', 'r') as f:
        data = json.load(f)
    states = {}
    for state_name, state_info in data.get('states', {}).items():
        for node in state_info.get('member_nodes', []):
            states[node] = state_name
    return states

# Load phase22 folio data
def load_folio_data():
    with open('C:/git/voynich/phase22_summary.json', 'r') as f:
        data = json.load(f)
    return {f['folio']: f for f in data.get('folios', [])}

# Load equivalence classes
def load_equivalence_classes():
    with open('C:/git/voynich/phase20a_operator_equivalence.json', 'r') as f:
        data = json.load(f)
    token_to_class = {}
    for cls in data.get('classes', []):
        class_id = cls.get('class_id')
        for member in cls.get('members', []):
            token_to_class[member] = class_id
    return token_to_class

records = load_corpus()
forbidden = load_forbidden_transitions()
semantic_states = load_semantic_states()
folio_data = load_folio_data()
token_to_class = load_equivalence_classes()

print(f"    Corpus records: {len(records)}")
print(f"    Forbidden transitions: {len(forbidden)}")
print(f"    Semantic state nodes: {len(semantic_states)}")
print(f"    Phase22 folios: {len(folio_data)}")
print(f"    Token-to-class mappings: {len(token_to_class)}")

# =============================================================================
# PARTITION FOLIOS INTO IF AND NIF
# =============================================================================

print("\n[2] Partitioning folios...")

# Group tokens by folio
folio_tokens = defaultdict(list)
for r in records:
    folio_tokens[r['folio']].append(r['word'])

# Classify folios
if_folios = []
nif_folios = []

for folio in folio_data.keys():
    ftype = classify_folio_type(folio)
    if ftype == "IF":
        if_folios.append(folio)
    elif ftype == "NIF":
        nif_folios.append(folio)

print(f"    IF (Illustrated Folios): {len(if_folios)}")
print(f"    NIF (Non-Illustrated Folios): {len(nif_folios)}")

if len(if_folios) < 5 or len(nif_folios) < 5:
    print("    WARNING: Insufficient folios in one category for robust testing")

# =============================================================================
# EXECUTION SCORING FUNCTIONS
# =============================================================================

def compute_execution_score(tokens):
    """
    Compute execution score E(T) for a token sequence.
    Returns:
        - legality: fraction of transitions that are not forbidden
        - convergence: fraction of tokens in STATE-C
        - hazard_count: number of forbidden transitions encountered
        - stability_dwell: average consecutive STATE-C runs
        - kernel_contact: fraction of tokens that are kernel-adjacent (k, h, e)
    """
    if len(tokens) < 2:
        return {
            'legality': 1.0,
            'convergence': 0.0,
            'hazard_count': 0,
            'stability_dwell': 0.0,
            'kernel_contact': 0.0
        }

    # Count forbidden transitions
    hazard_count = 0
    for i in range(len(tokens) - 1):
        if (tokens[i], tokens[i+1]) in forbidden:
            hazard_count += 1

    legality = 1.0 - (hazard_count / (len(tokens) - 1))

    # Count STATE-C membership
    state_c_count = sum(1 for t in tokens if semantic_states.get(t) == 'STATE-C')
    convergence = state_c_count / len(tokens)

    # Compute stability dwell (consecutive STATE-C runs)
    runs = []
    current_run = 0
    for t in tokens:
        if semantic_states.get(t) == 'STATE-C':
            current_run += 1
        else:
            if current_run > 0:
                runs.append(current_run)
            current_run = 0
    if current_run > 0:
        runs.append(current_run)

    stability_dwell = np.mean(runs) if runs else 0.0

    # Kernel contact (k, h, e presence - directly or via substring)
    kernel_nodes = {'k', 'h', 'e'}
    kernel_contact = sum(1 for t in tokens if any(k in t for k in kernel_nodes)) / len(tokens)

    return {
        'legality': float(legality),
        'convergence': float(convergence),
        'hazard_count': int(hazard_count),
        'stability_dwell': float(stability_dwell),
        'kernel_contact': float(kernel_contact)
    }

def compute_feature_vector(tokens):
    """
    Compute execution feature vector for distribution comparison.
    """
    if len(tokens) < 2:
        return np.zeros(10)

    # Class frequencies (normalized)
    class_counts = Counter(token_to_class.get(t, -1) for t in tokens)
    class_freq = np.zeros(50)  # 49 classes + 1 for unknown
    for cls, count in class_counts.items():
        if cls >= 0 and cls < 49:
            class_freq[cls] = count / len(tokens)
        else:
            class_freq[49] = count / len(tokens)

    # Basic metrics
    exec_score = compute_execution_score(tokens)

    # Compute additional metrics
    # Link density (tokens containing 'ol' or 'al')
    link_tokens = sum(1 for t in tokens if 'ol' in t or 'al' in t)
    link_density = link_tokens / len(tokens)

    # Run length (average consecutive identical tokens)
    runs = 1
    for i in range(1, len(tokens)):
        if tokens[i] != tokens[i-1]:
            runs += 1
    avg_run_length = len(tokens) / runs

    # Energy tokens (qo prefix)
    energy_tokens = sum(1 for t in tokens if t.startswith('qo'))
    energy_density = energy_tokens / len(tokens)

    # Build feature vector (10 features)
    features = np.array([
        exec_score['legality'],
        exec_score['convergence'],
        exec_score['stability_dwell'],
        exec_score['kernel_contact'],
        link_density,
        avg_run_length,
        energy_density,
        len(tokens),
        exec_score['hazard_count'] / max(1, len(tokens) - 1),
        len(set(tokens)) / len(tokens)  # type-token ratio
    ])

    return features

# =============================================================================
# TEST 1: SWAP INVARIANCE
# =============================================================================

print("\n[3] TEST 1: Swap Invariance...")
print("    Testing whether execution scores depend on illustration pairing")

# For each IF, compute execution score with:
# a) Its own tokens (original)
# b) Tokens from another IF (IF-IF swap)
# c) Tokens from a NIF (IF-NIF swap)

if_scores = {}
nif_scores = {}

# Compute baseline scores
for folio in if_folios:
    tokens = folio_tokens.get(folio, [])
    if len(tokens) >= 10:  # Minimum token threshold
        if_scores[folio] = compute_execution_score(tokens)

for folio in nif_folios:
    tokens = folio_tokens.get(folio, [])
    if len(tokens) >= 10:
        nif_scores[folio] = compute_execution_score(tokens)

print(f"    IF folios with sufficient data: {len(if_scores)}")
print(f"    NIF folios with sufficient data: {len(nif_scores)}")

# Swap test: Compare original scores to swapped scores
# Under H0 (no coupling), swapping should not change score distribution

swap_results = {
    'original': [],
    'if_if_swap': [],
    'if_nif_swap': [],
    'nif_nif_swap': []
}

# Original scores
for folio, score in if_scores.items():
    swap_results['original'].append(score['convergence'])

for folio, score in nif_scores.items():
    swap_results['original'].append(score['convergence'])

# IF-IF swap: assign IF text to different IF
if_list = list(if_scores.keys())
random.shuffle(if_list)
for i, folio in enumerate(if_list):
    swapped_folio = if_list[(i + 1) % len(if_list)]
    swap_results['if_if_swap'].append(if_scores[swapped_folio]['convergence'])

# IF-NIF swap: assign NIF text to IF "slot"
nif_list = list(nif_scores.keys())
for i, folio in enumerate(if_list):
    if i < len(nif_list):
        swap_results['if_nif_swap'].append(nif_scores[nif_list[i]]['convergence'])

# NIF-NIF swap
random.shuffle(nif_list)
for i, folio in enumerate(nif_list):
    swapped_folio = nif_list[(i + 1) % len(nif_list)]
    swap_results['nif_nif_swap'].append(nif_scores[swapped_folio]['convergence'])

# Statistical comparison
from scipy import stats

print("\n    Swap Invariance Results:")
print(f"    Original mean convergence: {np.mean(swap_results['original']):.4f}")
print(f"    IF-IF swap mean: {np.mean(swap_results['if_if_swap']):.4f}")
if swap_results['if_nif_swap']:
    print(f"    IF-NIF swap mean: {np.mean(swap_results['if_nif_swap']):.4f}")
print(f"    NIF-NIF swap mean: {np.mean(swap_results['nif_nif_swap']):.4f}")

# Test: Is original statistically different from swaps?
# Under H0, they should be indistinguishable

if len(swap_results['original']) > 5 and len(swap_results['if_if_swap']) > 5:
    u_stat, p_original_vs_swap = stats.mannwhitneyu(
        swap_results['original'][:len(swap_results['if_if_swap'])],
        swap_results['if_if_swap'],
        alternative='two-sided'
    )
    print(f"\n    Original vs IF-IF swap: p = {p_original_vs_swap:.4f}")
else:
    p_original_vs_swap = 1.0

if len(swap_results['if_nif_swap']) > 5:
    u_stat, p_if_nif = stats.mannwhitneyu(
        [if_scores[f]['convergence'] for f in if_list if f in if_scores][:len(swap_results['if_nif_swap'])],
        swap_results['if_nif_swap'],
        alternative='two-sided'
    )
    print(f"    IF original vs NIF swap: p = {p_if_nif:.4f}")
else:
    p_if_nif = 1.0

# Test 1 verdict
test1_verdict = "SWAP_INVARIANT" if p_original_vs_swap > 0.05 and p_if_nif > 0.05 else "SWAP_DEPENDENT"
print(f"\n    TEST 1 VERDICT: {test1_verdict}")

# =============================================================================
# TEST 2: DISTRIBUTION SHIFT
# =============================================================================

print("\n[4] TEST 2: Distribution Shift...")
print("    Testing P(X|IF) vs P(X|NIF)")

# Compute feature vectors for all folios
if_features = []
nif_features = []

for folio in if_folios:
    tokens = folio_tokens.get(folio, [])
    if len(tokens) >= 10:
        if_features.append(compute_feature_vector(tokens))

for folio in nif_folios:
    tokens = folio_tokens.get(folio, [])
    if len(tokens) >= 10:
        nif_features.append(compute_feature_vector(tokens))

if_features = np.array(if_features)
nif_features = np.array(nif_features)

print(f"    IF feature vectors: {len(if_features)}")
print(f"    NIF feature vectors: {len(nif_features)}")

# Compute Maximum Mean Discrepancy (MMD)
def compute_mmd(X, Y, gamma=1.0):
    """Compute MMD between two distributions using RBF kernel."""
    if len(X) == 0 or len(Y) == 0:
        return 0.0

    XX = np.sum(np.exp(-gamma * np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=2))) / (len(X) * len(X))
    YY = np.sum(np.exp(-gamma * np.sum((Y[:, None, :] - Y[None, :, :]) ** 2, axis=2))) / (len(Y) * len(Y))
    XY = np.sum(np.exp(-gamma * np.sum((X[:, None, :] - Y[None, :, :]) ** 2, axis=2))) / (len(X) * len(Y))

    return XX + YY - 2 * XY

# Compute Energy Distance
def compute_energy_distance(X, Y):
    """Compute energy distance between two distributions."""
    if len(X) == 0 or len(Y) == 0:
        return 0.0

    # E[||X - Y||]
    XY = np.mean([np.linalg.norm(x - y) for x in X for y in Y])
    # E[||X - X'||]
    XX = np.mean([np.linalg.norm(X[i] - X[j]) for i in range(len(X)) for j in range(i+1, len(X))]) if len(X) > 1 else 0
    # E[||Y - Y'||]
    YY = np.mean([np.linalg.norm(Y[i] - Y[j]) for i in range(len(Y)) for j in range(i+1, len(Y))]) if len(Y) > 1 else 0

    return 2 * XY - XX - YY

if len(if_features) > 0 and len(nif_features) > 0:
    # Normalize features
    all_features = np.vstack([if_features, nif_features])
    mean = np.mean(all_features, axis=0)
    std = np.std(all_features, axis=0) + 1e-8

    if_normalized = (if_features - mean) / std
    nif_normalized = (nif_features - mean) / std

    # Compute distances
    mmd = compute_mmd(if_normalized, nif_normalized, gamma=0.5)
    energy = compute_energy_distance(if_normalized, nif_normalized)

    print(f"\n    MMD (RBF kernel): {mmd:.4f}")
    print(f"    Energy distance: {energy:.4f}")

    # Permutation test for significance
    n_permutations = 1000
    mmd_null = []
    combined = np.vstack([if_normalized, nif_normalized])
    n_if = len(if_normalized)

    for _ in range(n_permutations):
        perm = np.random.permutation(len(combined))
        perm_if = combined[perm[:n_if]]
        perm_nif = combined[perm[n_if:]]
        mmd_null.append(compute_mmd(perm_if, perm_nif, gamma=0.5))

    mmd_p_value = np.mean([m >= mmd for m in mmd_null])
    print(f"    MMD permutation p-value: {mmd_p_value:.4f}")

    # Two-sample classifier test
    from sklearn.model_selection import cross_val_score
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    # Prepare data for classifier
    X = np.vstack([if_features, nif_features])
    y = np.array([1] * len(if_features) + [0] * len(nif_features))

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Cross-validated classifier
    clf = LogisticRegression(max_iter=1000, random_state=42)
    try:
        cv_scores = cross_val_score(clf, X_scaled, y, cv=min(5, min(len(if_features), len(nif_features))))
        classifier_accuracy = np.mean(cv_scores)
        classifier_std = np.std(cv_scores)
    except:
        classifier_accuracy = 0.5
        classifier_std = 0.0

    print(f"\n    Classifier accuracy: {classifier_accuracy:.3f} +/- {classifier_std:.3f}")
    print(f"    (Chance level: 0.500)")
else:
    mmd = 0.0
    energy = 0.0
    mmd_p_value = 1.0
    classifier_accuracy = 0.5
    classifier_std = 0.0

# Test 2 verdict
# Significant difference if: MMD p < 0.05 OR classifier > 0.6
if mmd_p_value < 0.05 or classifier_accuracy > 0.6:
    test2_verdict = "DISTRIBUTION_SHIFT_DETECTED"
else:
    test2_verdict = "NO_DISTRIBUTION_SHIFT"

print(f"\n    TEST 2 VERDICT: {test2_verdict}")

# =============================================================================
# PER-METRIC COMPARISON (IF vs NIF)
# =============================================================================

print("\n[5] Per-metric IF vs NIF comparison...")

if_metrics = {
    'legality': [],
    'convergence': [],
    'stability': [],
    'kernel_contact': [],
    'hazard_rate': []
}

nif_metrics = {
    'legality': [],
    'convergence': [],
    'stability': [],
    'kernel_contact': [],
    'hazard_rate': []
}

for folio, score in if_scores.items():
    tokens = folio_tokens.get(folio, [])
    if_metrics['legality'].append(score['legality'])
    if_metrics['convergence'].append(score['convergence'])
    if_metrics['stability'].append(score['stability_dwell'])
    if_metrics['kernel_contact'].append(score['kernel_contact'])
    if_metrics['hazard_rate'].append(score['hazard_count'] / max(1, len(tokens) - 1))

for folio, score in nif_scores.items():
    tokens = folio_tokens.get(folio, [])
    nif_metrics['legality'].append(score['legality'])
    nif_metrics['convergence'].append(score['convergence'])
    nif_metrics['stability'].append(score['stability_dwell'])
    nif_metrics['kernel_contact'].append(score['kernel_contact'])
    nif_metrics['hazard_rate'].append(score['hazard_count'] / max(1, len(tokens) - 1))

print("\n    Metric           IF mean    NIF mean   Cohen's d   p-value")
print("    " + "-" * 60)

metric_comparisons = {}
for metric in if_metrics.keys():
    if_vals = np.array(if_metrics[metric])
    nif_vals = np.array(nif_metrics[metric])

    if len(if_vals) > 0 and len(nif_vals) > 0:
        if_mean = np.mean(if_vals)
        nif_mean = np.mean(nif_vals)

        # Cohen's d
        pooled_std = np.sqrt((np.var(if_vals) + np.var(nif_vals)) / 2)
        cohens_d = (if_mean - nif_mean) / pooled_std if pooled_std > 0 else 0

        # Mann-Whitney U test
        try:
            _, p_value = stats.mannwhitneyu(if_vals, nif_vals, alternative='two-sided')
        except:
            p_value = 1.0

        print(f"    {metric:16} {if_mean:8.4f}  {nif_mean:8.4f}  {cohens_d:8.3f}  {p_value:.4f}")

        metric_comparisons[metric] = {
            'if_mean': float(if_mean),
            'nif_mean': float(nif_mean),
            'cohens_d': float(cohens_d),
            'p_value': float(p_value)
        }

# =============================================================================
# FINAL VERDICT
# =============================================================================

print("\n" + "=" * 70)
print("FINAL VERDICT")
print("=" * 70)

# Count signals
h0_signals = 0  # Illustrations have no operational role
h1_signals = 0  # Weak coupling (correlates but doesn't constrain)
h2_signals = 0  # Strong coupling (constrains execution)

# Test 1: Swap invariance
if test1_verdict == "SWAP_INVARIANT":
    h0_signals += 1
    print("  Test 1 (Swap Invariance): PASS -> H0 supported (no pairing effect)")
else:
    h2_signals += 1
    print("  Test 1 (Swap Invariance): FAIL -> H2 supported (pairing matters)")

# Test 2: Distribution shift
if test2_verdict == "NO_DISTRIBUTION_SHIFT":
    h0_signals += 1
    print("  Test 2 (Distribution Shift): PASS -> H0 supported (IF = NIF)")
else:
    h1_signals += 1
    print("  Test 2 (Distribution Shift): FAIL -> H1 supported (IF != NIF)")

# Per-metric analysis
significant_metrics = sum(1 for m in metric_comparisons.values() if m['p_value'] < 0.05 and abs(m['cohens_d']) > 0.5)
if significant_metrics == 0:
    h0_signals += 1
    print(f"  Metric Comparison: {significant_metrics}/5 significant -> H0 supported")
elif significant_metrics <= 2:
    h1_signals += 1
    print(f"  Metric Comparison: {significant_metrics}/5 significant -> H1 supported (weak effect)")
else:
    h2_signals += 1
    print(f"  Metric Comparison: {significant_metrics}/5 significant -> H2 supported (strong effect)")

# Overall verdict
if h0_signals >= 2:
    overall_verdict = "H0_CONFIRMED"
    interpretation = "Illustrations have NO operational role. Execution behavior is fully determined by text alone."
elif h2_signals >= 2:
    overall_verdict = "H2_SUPPORTED"
    interpretation = "Illustrations act as external constraints that affect execution legality or stability."
else:
    overall_verdict = "H1_SUPPORTED"
    interpretation = "Illustrations correlate with execution behavior but do not constrain or gate it."

print(f"\n  OVERALL: {overall_verdict}")
print(f"  H0 signals: {h0_signals}")
print(f"  H1 signals: {h1_signals}")
print(f"  H2 signals: {h2_signals}")
print(f"\n  Interpretation: {interpretation}")

# =============================================================================
# SAVE RESULTS
# =============================================================================

results = {
    'metadata': {
        'timestamp': datetime.now().isoformat(),
        'if_count': len(if_folios),
        'nif_count': len(nif_folios),
        'if_with_data': len(if_scores),
        'nif_with_data': len(nif_scores)
    },
    'test1_swap_invariance': {
        'original_mean': float(np.mean(swap_results['original'])),
        'if_if_swap_mean': float(np.mean(swap_results['if_if_swap'])) if swap_results['if_if_swap'] else None,
        'if_nif_swap_mean': float(np.mean(swap_results['if_nif_swap'])) if swap_results['if_nif_swap'] else None,
        'nif_nif_swap_mean': float(np.mean(swap_results['nif_nif_swap'])) if swap_results['nif_nif_swap'] else None,
        'p_original_vs_swap': float(p_original_vs_swap),
        'verdict': test1_verdict
    },
    'test2_distribution_shift': {
        'mmd': float(mmd),
        'energy_distance': float(energy),
        'mmd_p_value': float(mmd_p_value),
        'classifier_accuracy': float(classifier_accuracy),
        'classifier_std': float(classifier_std),
        'verdict': test2_verdict
    },
    'metric_comparisons': metric_comparisons,
    'signals': {
        'h0': h0_signals,
        'h1': h1_signals,
        'h2': h2_signals
    },
    'verdict': overall_verdict,
    'interpretation': interpretation
}

with open('C:/git/voynich/swap_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n  Saved: swap_test_results.json")

# Also save distribution test details
distribution_results = {
    'mmd': float(mmd),
    'energy_distance': float(energy),
    'mmd_p_value': float(mmd_p_value),
    'classifier_accuracy': float(classifier_accuracy),
    'classifier_std': float(classifier_std),
    'if_feature_shape': list(if_features.shape) if len(if_features) > 0 else [0, 0],
    'nif_feature_shape': list(nif_features.shape) if len(nif_features) > 0 else [0, 0],
    'features_used': [
        'legality', 'convergence', 'stability_dwell', 'kernel_contact',
        'link_density', 'avg_run_length', 'energy_density', 'token_count',
        'hazard_rate', 'type_token_ratio'
    ]
}

with open('C:/git/voynich/distribution_tests.json', 'w') as f:
    json.dump(distribution_results, f, indent=2)

print("  Saved: distribution_tests.json")
print("=" * 70)
