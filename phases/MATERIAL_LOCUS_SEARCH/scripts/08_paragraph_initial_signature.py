#!/usr/bin/env python3
"""
Test 8: Paragraph-Initial Token Vocabulary Signature

Question: Do paragraph-initial tokens predict body vocabulary/section?

Method:
1. Load all Currier B tokens (H track, no labels, no uncertain).
2. Build paragraphs using par_initial boundaries; keep only paragraphs with 10+ tokens.
3. For each paragraph:
   - INITIAL vocabulary: MIDDLEs from the first 3 tokens
   - BODY vocabulary: MIDDLEs from the remaining tokens
4. Test 1: Section prediction from initial tokens
   - Build presence/absence feature vectors from initial MIDDLEs
   - Leave-one-out cross-validation with KNN (k=5) and NearestCentroid
   - Compare vs body-vocabulary classifier (positive control) and random baseline
   - Per-MIDDLE chi-square analysis for section prediction
5. Test 2: Initial-body vocabulary coupling
   - Jaccard between initial MIDDLEs and body MIDDLEs per paragraph
   - Kruskal-Wallis test for section variation

Pass criteria: Initial-token accuracy >60% (chance ~20%), >70% of body-vocabulary accuracy
Fail criteria: Near chance -- initial tokens carry no section signal
"""

import sys
import json
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# ============================================================
# CONSTANTS
# ============================================================
RESULTS_DIR = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/results')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = RESULTS_DIR / 'paragraph_initial_signature.json'

MIN_PARAGRAPH_TOKENS = 10
INITIAL_TOKEN_COUNT = 3
np.random.seed(42)


def to_native(obj):
    """Convert numpy types to native Python for JSON serialization."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


# ============================================================
# STEP 1: Load Currier B tokens and build paragraphs
# ============================================================
print("Loading Currier B tokens...")
tx = Transcript()
morph = Morphology()

# Collect all B tokens in file order (which is folio/line/position order)
all_tokens = []
for t in tx.currier_b():
    m = morph.extract(t.word)
    entry = {
        'word': t.word,
        'folio': t.folio,
        'line': t.line,
        'section': t.section,
        'middle': m.middle,
        'par_initial': t.par_initial,
    }
    all_tokens.append(entry)

print(f"Total Currier B tokens: {len(all_tokens)}")

# Build paragraphs using par_initial boundaries
paragraphs = []
current_par = None
par_num_by_folio = defaultdict(int)

for t in all_tokens:
    folio = t['folio']
    if t['par_initial']:
        # Start new paragraph
        par_num_by_folio[folio] += 1
        current_par = {
            'folio': folio,
            'section': t['section'],
            'par_num': par_num_by_folio[folio],
            'tokens': [],
        }
        paragraphs.append(current_par)

    if current_par is not None and current_par['folio'] == folio:
        current_par['tokens'].append(t)
    elif current_par is None or current_par['folio'] != folio:
        # Tokens before first par_initial in a new folio: create implicit paragraph
        par_num_by_folio[folio] += 1
        current_par = {
            'folio': folio,
            'section': t['section'],
            'par_num': par_num_by_folio[folio],
            'tokens': [t],
        }
        paragraphs.append(current_par)

print(f"Total paragraphs found: {len(paragraphs)}")

# Filter: minimum token count
paragraphs = [p for p in paragraphs if len(p['tokens']) >= MIN_PARAGRAPH_TOKENS]
print(f"Paragraphs with >= {MIN_PARAGRAPH_TOKENS} tokens: {len(paragraphs)}")


# ============================================================
# STEP 2: Extract INITIAL and BODY MIDDLEs for each paragraph
# ============================================================
print("\nExtracting initial and body vocabulary...")

for p in paragraphs:
    # First 3 tokens -> INITIAL; rest -> BODY
    initial_tokens = p['tokens'][:INITIAL_TOKEN_COUNT]
    body_tokens = p['tokens'][INITIAL_TOKEN_COUNT:]

    p['initial_middles'] = set()
    for t in initial_tokens:
        if t['middle'] and t['middle'] != '_EMPTY_':
            p['initial_middles'].add(t['middle'])

    p['body_middles'] = set()
    for t in body_tokens:
        if t['middle'] and t['middle'] != '_EMPTY_':
            p['body_middles'].add(t['middle'])

    p['all_middles'] = p['initial_middles'] | p['body_middles']

# Collect sections
sections = sorted(set(p['section'] for p in paragraphs))
n_sections = len(sections)
section_to_idx = {s: i for i, s in enumerate(sections)}

print(f"Sections represented: {sections} ({n_sections} sections)")
section_counts = Counter(p['section'] for p in paragraphs)
for s in sections:
    print(f"  {s}: {section_counts[s]} paragraphs")

chance_level = 1.0 / n_sections
majority_section = section_counts.most_common(1)[0][0]
majority_fraction = section_counts[majority_section] / len(paragraphs)
print(f"Chance level (1/n_sections): {chance_level:.3f}")
print(f"Majority class baseline ({majority_section}): {majority_fraction:.3f}")


# ============================================================
# STEP 3: Build feature vectors for classification
# ============================================================
print("\nBuilding feature vectors...")

# Collect all MIDDLEs that appear in initial positions across all paragraphs
all_initial_middles = set()
for p in paragraphs:
    all_initial_middles.update(p['initial_middles'])

# Filter to common MIDDLEs (appear in at least 3 paragraphs' initial tokens)
initial_middle_freq = Counter()
for p in paragraphs:
    for m in p['initial_middles']:
        initial_middle_freq[m] += 1

common_initial_middles = sorted([m for m, c in initial_middle_freq.items() if c >= 3])
print(f"Total unique initial MIDDLEs: {len(all_initial_middles)}")
print(f"Common initial MIDDLEs (freq >= 3): {len(common_initial_middles)}")

# Similarly for body MIDDLEs
all_body_middles = set()
for p in paragraphs:
    all_body_middles.update(p['body_middles'])

body_middle_freq = Counter()
for p in paragraphs:
    for m in p['body_middles']:
        body_middle_freq[m] += 1

common_body_middles = sorted([m for m, c in body_middle_freq.items() if c >= 3])
print(f"Total unique body MIDDLEs: {len(all_body_middles)}")
print(f"Common body MIDDLEs (freq >= 3): {len(common_body_middles)}")

# Build feature matrices
# Initial features: presence/absence of common initial MIDDLEs
initial_mid_to_idx = {m: i for i, m in enumerate(common_initial_middles)}
X_initial = np.zeros((len(paragraphs), len(common_initial_middles)), dtype=np.float64)
for i, p in enumerate(paragraphs):
    for m in p['initial_middles']:
        if m in initial_mid_to_idx:
            X_initial[i, initial_mid_to_idx[m]] = 1.0

# Body features: presence/absence of common body MIDDLEs
body_mid_to_idx = {m: i for i, m in enumerate(common_body_middles)}
X_body = np.zeros((len(paragraphs), len(common_body_middles)), dtype=np.float64)
for i, p in enumerate(paragraphs):
    for m in p['body_middles']:
        if m in body_mid_to_idx:
            X_body[i, body_mid_to_idx[m]] = 1.0

# Labels
y = np.array([section_to_idx[p['section']] for p in paragraphs])


# ============================================================
# STEP 4: Leave-one-out cross-validation
# ============================================================
print("\nRunning leave-one-out classification...")

from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from sklearn.model_selection import LeaveOneOut

loo = LeaveOneOut()


def loo_accuracy(X, y_labels, clf_class, **clf_kwargs):
    """Compute LOO-CV accuracy for a classifier."""
    correct = 0
    total = 0
    predictions = []

    for train_idx, test_idx in loo.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y_labels[train_idx], y_labels[test_idx]

        clf = clf_class(**clf_kwargs)
        try:
            clf.fit(X_train, y_train)
            pred = clf.predict(X_test)[0]
        except Exception:
            # If classifier fails (e.g., all-zero features), predict majority
            pred = Counter(y_train.tolist()).most_common(1)[0][0]

        predictions.append(pred)
        if pred == y_test[0]:
            correct += 1
        total += 1

    return correct / total if total > 0 else 0.0, predictions


# KNN k=5 on initial features
print("  KNN(k=5) on initial MIDDLEs...")
acc_initial_knn, preds_initial_knn = loo_accuracy(X_initial, y, KNeighborsClassifier, n_neighbors=5)
print(f"    Accuracy: {acc_initial_knn:.3f}")

# NearestCentroid on initial features
print("  NearestCentroid on initial MIDDLEs...")
acc_initial_nc, preds_initial_nc = loo_accuracy(X_initial, y, NearestCentroid)
print(f"    Accuracy: {acc_initial_nc:.3f}")

# KNN k=5 on body features (positive control)
print("  KNN(k=5) on body MIDDLEs (positive control)...")
acc_body_knn, preds_body_knn = loo_accuracy(X_body, y, KNeighborsClassifier, n_neighbors=5)
print(f"    Accuracy: {acc_body_knn:.3f}")

# NearestCentroid on body features (positive control)
print("  NearestCentroid on body MIDDLEs (positive control)...")
acc_body_nc, preds_body_nc = loo_accuracy(X_body, y, NearestCentroid)
print(f"    Accuracy: {acc_body_nc:.3f}")

# Use best initial classifier
best_initial_acc = max(acc_initial_knn, acc_initial_nc)
best_initial_method = 'KNN_k5' if acc_initial_knn >= acc_initial_nc else 'NearestCentroid'
best_body_acc = max(acc_body_knn, acc_body_nc)
best_body_method = 'KNN_k5' if acc_body_knn >= acc_body_nc else 'NearestCentroid'

ratio_to_body = best_initial_acc / best_body_acc if best_body_acc > 0 else 0.0

print(f"\nBest initial accuracy: {best_initial_acc:.3f} ({best_initial_method})")
print(f"Best body accuracy: {best_body_acc:.3f} ({best_body_method})")
print(f"Initial / Body ratio: {ratio_to_body:.3f}")
print(f"Chance level: {chance_level:.3f}")
print(f"Majority baseline: {majority_fraction:.3f}")


# ============================================================
# STEP 5: Per-MIDDLE chi-square analysis for section prediction
# ============================================================
print("\nPer-MIDDLE chi-square analysis (initial tokens)...")

from scipy.stats import chi2_contingency

# For each common initial MIDDLE, compute which section it most predicts
chi2_results = {}
for m in common_initial_middles:
    m_idx = initial_mid_to_idx[m]
    # Build 2 x n_sections contingency table: [has_middle, lacks_middle] x [sections]
    contingency = np.zeros((2, n_sections), dtype=int)
    for i, p in enumerate(paragraphs):
        s_idx = section_to_idx[p['section']]
        if X_initial[i, m_idx] > 0:
            contingency[0, s_idx] += 1
        else:
            contingency[1, s_idx] += 1

    # Only test if middle appears in at least 2 sections or has enough count
    total_present = contingency[0].sum()
    if total_present >= 5:
        try:
            chi2, p_val, dof, expected = chi2_contingency(contingency)
            # Which section does this MIDDLE most predict?
            # Compute observed/expected ratio per section
            ratios = {}
            for s_idx_inner, s in enumerate(sections):
                exp = expected[0, s_idx_inner]
                if exp > 0:
                    ratios[s] = contingency[0, s_idx_inner] / exp
                else:
                    ratios[s] = 0.0
            best_section = max(ratios, key=ratios.get)

            chi2_results[m] = {
                'chi2': round(float(chi2), 3),
                'p_value': float(p_val),
                'best_section': best_section,
                'enrichment_ratio': round(ratios[best_section], 3),
                'count': int(total_present),
            }
        except ValueError:
            pass  # Skip if contingency table is degenerate

# Sort by chi2 descending
chi2_sorted = sorted(chi2_results.items(), key=lambda x: x[1]['chi2'], reverse=True)

print(f"MIDDLEs tested: {len(chi2_results)}")
significant_middles = [(m, r) for m, r in chi2_sorted if r['p_value'] < 0.05]
print(f"Significant at p<0.05: {len(significant_middles)}")

print("\nTop 10 section-predictive initial MIDDLEs:")
for m, r in chi2_sorted[:10]:
    sig = '*' if r['p_value'] < 0.05 else ''
    print(f"  {m:15s} -> {r['best_section']} (chi2={r['chi2']:.1f}, "
          f"enrichment={r['enrichment_ratio']:.2f}, n={r['count']}) {sig}")


# ============================================================
# STEP 6: Initial-Body vocabulary coupling (Jaccard)
# ============================================================
print("\n=== Test 2: Initial-Body Vocabulary Coupling ===")

jaccard_by_section = defaultdict(list)
all_jaccards = []

for p in paragraphs:
    init = p['initial_middles']
    body = p['body_middles']
    if not init and not body:
        j = 0.0
    else:
        intersection = len(init & body)
        union = len(init | body)
        j = intersection / union if union > 0 else 0.0
    p['init_body_jaccard'] = j
    jaccard_by_section[p['section']].append(j)
    all_jaccards.append(j)

overall_mean_jaccard = float(np.mean(all_jaccards))
overall_std_jaccard = float(np.std(all_jaccards))
print(f"Overall initial-body Jaccard: {overall_mean_jaccard:.4f} +/- {overall_std_jaccard:.4f}")

print("\nPer-section initial-body Jaccard:")
section_jaccard_summary = {}
for s in sections:
    vals = jaccard_by_section[s]
    if vals:
        mean_j = float(np.mean(vals))
        std_j = float(np.std(vals))
        median_j = float(np.median(vals))
        section_jaccard_summary[s] = {
            'n': len(vals),
            'mean': round(mean_j, 4),
            'std': round(std_j, 4),
            'median': round(median_j, 4),
        }
        print(f"  {s}: n={len(vals)}, mean={mean_j:.4f}, std={std_j:.4f}, median={median_j:.4f}")

# Kruskal-Wallis test: does coupling vary by section?
from scipy.stats import kruskal

groups_for_kw = [jaccard_by_section[s] for s in sections if len(jaccard_by_section[s]) >= 2]
if len(groups_for_kw) >= 2:
    kw_stat, kw_p = kruskal(*groups_for_kw)
    kw_stat = float(kw_stat)
    kw_p = float(kw_p)
    print(f"\nKruskal-Wallis H={kw_stat:.3f}, p={kw_p:.6f}")
else:
    kw_stat, kw_p = 0.0, 1.0
    print("\nInsufficient groups for Kruskal-Wallis test")


# ============================================================
# STEP 7: Per-section confusion matrix for best initial classifier
# ============================================================
print("\n=== Per-Section Breakdown ===")

best_initial_preds = preds_initial_knn if best_initial_method == 'KNN_k5' else preds_initial_nc
per_section_accuracy = {}
for s in sections:
    s_idx = section_to_idx[s]
    mask = y == s_idx
    correct = sum(1 for i in range(len(y)) if mask[i] and best_initial_preds[i] == s_idx)
    total_s = mask.sum()
    acc = correct / total_s if total_s > 0 else 0.0
    per_section_accuracy[s] = {
        'n': int(total_s),
        'correct': int(correct),
        'accuracy': round(float(acc), 3),
    }
    print(f"  {s}: {correct}/{total_s} = {acc:.3f}")


# ============================================================
# STEP 8: Random baseline via permutation
# ============================================================
print("\nComputing random baseline via label permutation (100 shuffles)...")

N_PERM_BASELINE = 100
perm_accs = []
for _ in range(N_PERM_BASELINE):
    y_perm = y.copy()
    np.random.shuffle(y_perm)
    # Use NearestCentroid for speed
    correct = 0
    for train_idx, test_idx in loo.split(X_initial):
        X_train, X_test = X_initial[train_idx], X_initial[test_idx]
        y_train, y_test = y_perm[train_idx], y_perm[test_idx]
        clf = NearestCentroid()
        try:
            clf.fit(X_train, y_train)
            pred = clf.predict(X_test)[0]
        except Exception:
            pred = Counter(y_train.tolist()).most_common(1)[0][0]
        if pred == y_test[0]:
            correct += 1
    perm_accs.append(correct / len(y))

perm_mean = float(np.mean(perm_accs))
perm_std = float(np.std(perm_accs))
perm_p_value = float(np.mean(np.array(perm_accs) >= best_initial_acc))
z_vs_perm = (best_initial_acc - perm_mean) / perm_std if perm_std > 0 else 0.0

print(f"Permutation baseline: {perm_mean:.3f} +/- {perm_std:.3f}")
print(f"Observed best initial: {best_initial_acc:.3f}")
print(f"Z-score vs permutation: {z_vs_perm:.2f}")
print(f"Permutation p-value: {perm_p_value:.4f}")


# ============================================================
# STEP 9: Determine verdict
# ============================================================
print("\n" + "=" * 60)

# Pass criteria:
# - Initial-token accuracy > 60% (chance ~ 20%)
# - Initial accuracy > 70% of body-vocabulary accuracy
passes_accuracy = best_initial_acc > 0.60
passes_ratio = ratio_to_body > 0.70
passes_above_chance = best_initial_acc > chance_level + 0.10  # at least 10% above chance
coupling_varies = kw_p < 0.05

if passes_accuracy and passes_ratio:
    verdict = 'PASS'
    interpretation = (
        f"Paragraph-initial tokens carry strong section signal. "
        f"Best initial-token accuracy ({best_initial_acc:.1%}) exceeds 60% threshold "
        f"and reaches {ratio_to_body:.1%} of body-vocabulary accuracy ({best_body_acc:.1%}). "
        f"The first 3 tokens of a paragraph encode enough information to predict "
        f"which manuscript section the paragraph belongs to."
    )
elif passes_above_chance and ratio_to_body > 0.50:
    verdict = 'MARGINAL'
    interpretation = (
        f"Paragraph-initial tokens carry moderate section signal. "
        f"Best initial-token accuracy ({best_initial_acc:.1%}) exceeds chance ({chance_level:.1%}) "
        f"but falls short of 60% threshold or 70% body-accuracy ratio ({ratio_to_body:.1%}). "
        f"Initial tokens contain partial but not fully reliable section information."
    )
else:
    verdict = 'FAIL'
    interpretation = (
        f"Paragraph-initial tokens carry negligible section signal. "
        f"Best initial-token accuracy ({best_initial_acc:.1%}) is near chance ({chance_level:.1%}). "
        f"The first 3 tokens do not reliably predict which section a paragraph belongs to."
    )

print(f"=== VERDICT: {verdict} ===")
print(interpretation)

if coupling_varies:
    print(f"\nAdditional finding: Initial-body vocabulary coupling varies by section "
          f"(Kruskal-Wallis p={kw_p:.4f}), suggesting section-specific opening patterns.")
else:
    print(f"\nNo significant section variation in initial-body coupling (p={kw_p:.4f}).")


# ============================================================
# STEP 10: Build output JSON
# ============================================================
output = {
    'test': 'paragraph_initial_signature',
    'test_number': 8,
    'question': 'Do paragraph-initial tokens predict body vocabulary/section?',
    'method': {
        'description': (
            'Extract first 3 tokens (INITIAL) and remaining tokens (BODY) per paragraph. '
            'Build presence/absence feature vectors from MIDDLE vocabulary. '
            'Leave-one-out cross-validation with KNN(k=5) and NearestCentroid. '
            'Compare initial-token accuracy vs body-vocabulary accuracy and random baseline.'
        ),
        'min_paragraph_tokens': MIN_PARAGRAPH_TOKENS,
        'initial_token_count': INITIAL_TOKEN_COUNT,
        'common_middle_threshold': 3,
        'n_permutation_baseline': N_PERM_BASELINE,
    },
    'data_summary': {
        'total_currier_b_tokens': len(all_tokens),
        'total_paragraphs_raw': len([p for p in paragraphs]) + sum(
            1 for _ in []  # placeholder; actual count pre-filter logged above
        ),
        'paragraphs_after_filter': len(paragraphs),
        'sections': sections,
        'n_sections': n_sections,
        'section_distribution': {s: int(section_counts[s]) for s in sections},
        'n_common_initial_middles': len(common_initial_middles),
        'n_common_body_middles': len(common_body_middles),
    },
    'test1_section_prediction': {
        'initial_knn_k5_accuracy': round(acc_initial_knn, 4),
        'initial_nearest_centroid_accuracy': round(acc_initial_nc, 4),
        'body_knn_k5_accuracy': round(acc_body_knn, 4),
        'body_nearest_centroid_accuracy': round(acc_body_nc, 4),
        'best_initial_accuracy': round(best_initial_acc, 4),
        'best_initial_method': best_initial_method,
        'best_body_accuracy': round(best_body_acc, 4),
        'best_body_method': best_body_method,
        'initial_to_body_ratio': round(ratio_to_body, 4),
        'chance_level': round(chance_level, 4),
        'majority_baseline': round(majority_fraction, 4),
        'majority_class': majority_section,
        'permutation_baseline': {
            'n_permutations': N_PERM_BASELINE,
            'mean_accuracy': round(perm_mean, 4),
            'std_accuracy': round(perm_std, 4),
            'z_score': round(z_vs_perm, 2),
            'p_value': round(perm_p_value, 4),
        },
        'per_section_accuracy': per_section_accuracy,
    },
    'chi_square_analysis': {
        'middles_tested': len(chi2_results),
        'significant_at_005': len(significant_middles),
        'top_10_predictive': {
            m: r for m, r in chi2_sorted[:10]
        },
    },
    'test2_initial_body_coupling': {
        'overall_mean_jaccard': round(overall_mean_jaccard, 4),
        'overall_std_jaccard': round(overall_std_jaccard, 4),
        'per_section_jaccard': section_jaccard_summary,
        'kruskal_wallis': {
            'H_statistic': round(kw_stat, 3),
            'p_value': round(kw_p, 6),
            'significant_at_005': bool(kw_p < 0.05),
        },
    },
    'pass_criteria': {
        'initial_accuracy_threshold': 0.60,
        'initial_to_body_ratio_threshold': 0.70,
        'chance_level': round(chance_level, 4),
    },
    'verdict': verdict,
    'interpretation': interpretation,
}

# Clean numpy types for JSON
def clean_for_json(obj):
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(v) for v in obj]
    else:
        return to_native(obj)

output = clean_for_json(output)

with open(OUTPUT_PATH, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nOutput written to {OUTPUT_PATH}")
