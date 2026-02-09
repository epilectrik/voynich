#!/usr/bin/env python3
"""
Test 3: Paragraph Vocabulary Set as Material Scope

Question: Do paragraphs sharing kernel signatures (k-dominant, h-dominant,
balanced) share more vocabulary?

Method:
1. Extract all Currier B paragraphs (via par_initial boundaries).
2. Build MIDDLE vocabulary set per paragraph.
3. Compute kernel signature per paragraph using relative k-h balance:
   - Compute k-proportion and h-proportion of each paragraph's MIDDLE set
   - Use k-h differential to classify into tertiles: HIGH_K, HIGH_H, BALANCED
   - This yields balanced group sizes regardless of absolute character frequency
4. Within each folio, compute pairwise Jaccard similarity (MIDDLE set overlap).
5. Stratify pairs by kernel-signature match: SAME vs DIFFERENT.
6. Mann-Whitney U test: do same-kernel pairs have higher vocabulary Jaccard?
7. Compute the mean Jaccard lift: same-kernel / different-kernel.
8. Confound control: within each folio, permute paragraph kernel signatures
   while preserving MIDDLE sets (1000 permutations). Compare observed lift.
9. Test: do paragraph-initial tokens (first 3) predict kernel signature?

Pass: same-kernel Jaccard significantly higher (p < 0.01), lift > 1.15x.
Fail: lift < 1.10x.
"""

import sys
import json
import random
import numpy as np
from collections import defaultdict, Counter
from itertools import combinations
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# ============================================================
# CONSTANTS
# ============================================================
RESULTS_DIR = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/results')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = RESULTS_DIR / 'paragraph_vocabulary_scope.json'

N_PERMUTATIONS = 1000
MIN_PARAGRAPH_TOKENS = 3  # minimum tokens for a paragraph to be included
random.seed(42)
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

# Pre-compute morphology for all B tokens
all_tokens = []
for t in tx.currier_b():
    m = morph.extract(t.word)
    entry = {
        'word': t.word,
        'folio': t.folio,
        'line': t.line,
        'middle': m.middle,
        'par_initial': t.par_initial,
        'par_final': t.par_final,
    }
    all_tokens.append(entry)

print(f"Total Currier B tokens: {len(all_tokens)}")

# Build paragraphs: group tokens by (folio, paragraph_number)
# par_initial=True on first token of each paragraph
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
            'par_num': par_num_by_folio[folio],
            'tokens': [],
            'middles': set(),
        }
        paragraphs.append(current_par)

    if current_par is not None and current_par['folio'] == folio:
        current_par['tokens'].append(t)
        if t['middle'] and t['middle'] != '_EMPTY_':
            current_par['middles'].add(t['middle'])
    # If no paragraph started yet for this folio (tokens before first par_initial),
    # create an implicit paragraph
    elif current_par is None or current_par['folio'] != folio:
        par_num_by_folio[folio] += 1
        current_par = {
            'folio': folio,
            'par_num': par_num_by_folio[folio],
            'tokens': [t],
            'middles': set(),
        }
        if t['middle'] and t['middle'] != '_EMPTY_':
            current_par['middles'].add(t['middle'])
        paragraphs.append(current_par)

# Filter: minimum token count
paragraphs = [p for p in paragraphs if len(p['tokens']) >= MIN_PARAGRAPH_TOKENS]
print(f"Paragraphs (>= {MIN_PARAGRAPH_TOKENS} tokens): {len(paragraphs)}")


# ============================================================
# STEP 2: Compute kernel signature per paragraph
# ============================================================
# Strategy: Use the k-h differential (relative enrichment) to classify paragraphs
# into tertiles. This produces balanced groups regardless of absolute character
# frequency. The rationale: k and h are the two main kernel operators in BCSC;
# their relative balance in a paragraph reflects which process mode dominates.

def compute_kernel_proportions(middles_set):
    """Compute k, h, e proportions for a set of MIDDLEs."""
    if not middles_set:
        return 0.0, 0.0, 0.0, {'k': 0, 'h': 0, 'e': 0, 'total': 0}

    total = len(middles_set)
    k_count = sum(1 for m in middles_set if 'k' in m)
    h_count = sum(1 for m in middles_set if 'h' in m)
    e_count = sum(1 for m in middles_set if 'e' in m)

    return (k_count / total, h_count / total, e_count / total,
            {'k': k_count, 'h': h_count, 'e': e_count, 'total': total})


print("Computing kernel signatures...")

# First pass: compute k-h differential for all paragraphs
kh_diffs = []
for p in paragraphs:
    k_prop, h_prop, e_prop, counts = compute_kernel_proportions(p['middles'])
    p['k_prop'] = k_prop
    p['h_prop'] = h_prop
    p['e_prop'] = e_prop
    p['kernel_counts'] = counts
    p['kh_diff'] = k_prop - h_prop
    kh_diffs.append(p['kh_diff'])

# Compute tertile boundaries
kh_diffs_arr = np.array(kh_diffs)
q33 = float(np.percentile(kh_diffs_arr, 33.33))
q66 = float(np.percentile(kh_diffs_arr, 66.67))

print(f"k-h differential range: [{kh_diffs_arr.min():.3f}, {kh_diffs_arr.max():.3f}]")
print(f"k-h differential tertile cuts: q33={q33:.3f}, q66={q66:.3f}")

# Second pass: classify using tertile boundaries
for p in paragraphs:
    if p['kh_diff'] > q66:
        p['kernel_sig'] = 'HIGH_K'
    elif p['kh_diff'] < q33:
        p['kernel_sig'] = 'HIGH_H'
    else:
        p['kernel_sig'] = 'BALANCED'

sig_counts = Counter(p['kernel_sig'] for p in paragraphs)
print(f"Kernel signature distribution: {dict(sig_counts)}")

# Report mean proportions per group
for sig in ['HIGH_K', 'HIGH_H', 'BALANCED']:
    group = [p for p in paragraphs if p['kernel_sig'] == sig]
    mean_k = np.mean([p['k_prop'] for p in group])
    mean_h = np.mean([p['h_prop'] for p in group])
    mean_e = np.mean([p['e_prop'] for p in group])
    mean_vocab = np.mean([len(p['middles']) for p in group])
    print(f"  {sig}: n={len(group)}, mean k={mean_k:.3f}, h={mean_h:.3f}, "
          f"e={mean_e:.3f}, vocab_size={mean_vocab:.1f}")


# ============================================================
# STEP 3: Pairwise Jaccard within folios
# ============================================================
def jaccard(set_a, set_b):
    """Compute Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


# Group paragraphs by folio
folio_pars = defaultdict(list)
for p in paragraphs:
    folio_pars[p['folio']].append(p)

n_folios_2plus = sum(1 for pars in folio_pars.values() if len(pars) >= 2)
print(f"\nFolios with paragraphs: {len(folio_pars)}")
print(f"Folios with 2+ paragraphs (usable): {n_folios_2plus}")

# Compute pairwise Jaccard, stratified by kernel-signature match
same_kernel_jaccards = []
diff_kernel_jaccards = []

for folio, pars in folio_pars.items():
    if len(pars) < 2:
        continue

    for i, j in combinations(range(len(pars)), 2):
        j_val = jaccard(pars[i]['middles'], pars[j]['middles'])
        sig_i = pars[i]['kernel_sig']
        sig_j = pars[j]['kernel_sig']

        if sig_i == sig_j:
            same_kernel_jaccards.append(j_val)
        else:
            diff_kernel_jaccards.append(j_val)

print(f"Same-kernel pairs: {len(same_kernel_jaccards)}")
print(f"Different-kernel pairs: {len(diff_kernel_jaccards)}")


# ============================================================
# STEP 4: Statistical test
# ============================================================
from scipy.stats import mannwhitneyu

mean_same = float(np.mean(same_kernel_jaccards)) if same_kernel_jaccards else 0
mean_diff = float(np.mean(diff_kernel_jaccards)) if diff_kernel_jaccards else 0
median_same = float(np.median(same_kernel_jaccards)) if same_kernel_jaccards else 0
median_diff = float(np.median(diff_kernel_jaccards)) if diff_kernel_jaccards else 0
std_same = float(np.std(same_kernel_jaccards)) if same_kernel_jaccards else 0
std_diff = float(np.std(diff_kernel_jaccards)) if diff_kernel_jaccards else 0

lift = mean_same / mean_diff if mean_diff > 0 else float('inf')

if same_kernel_jaccards and diff_kernel_jaccards:
    u_stat, p_value = mannwhitneyu(
        same_kernel_jaccards, diff_kernel_jaccards,
        alternative='greater'
    )
    u_stat = float(u_stat)
    p_value = float(p_value)
else:
    u_stat, p_value = 0.0, 1.0

print(f"\n=== Main Result ===")
print(f"Mean Jaccard (same kernel):  {mean_same:.4f} +/- {std_same:.4f}")
print(f"Mean Jaccard (diff kernel):  {mean_diff:.4f} +/- {std_diff:.4f}")
print(f"Lift (same/diff):            {lift:.4f}")
print(f"Mann-Whitney U:              {u_stat:.0f}")
print(f"p-value (one-sided):         {p_value:.6f}")


# ============================================================
# STEP 5: Permutation null model
# ============================================================
# Permute kernel signatures within each folio while preserving
# MIDDLE sets. This tests whether the kernel-vocabulary association
# is genuine or an artifact of folio-level structure.
print(f"\nRunning {N_PERMUTATIONS} permutations (signature shuffle)...")

null_lifts = []
null_same_means = []
null_diff_means = []

for perm_i in range(N_PERMUTATIONS):
    perm_same_j = []
    perm_diff_j = []

    for folio, pars in folio_pars.items():
        if len(pars) < 2:
            continue

        # Shuffle kernel signatures within this folio
        sigs = [p['kernel_sig'] for p in pars]
        random.shuffle(sigs)

        # Compute pairwise Jaccard with original middles, shuffled signatures
        for i, j_idx in combinations(range(len(pars)), 2):
            j_val = jaccard(pars[i]['middles'], pars[j_idx]['middles'])
            if sigs[i] == sigs[j_idx]:
                perm_same_j.append(j_val)
            else:
                perm_diff_j.append(j_val)

    perm_mean_same = float(np.mean(perm_same_j)) if perm_same_j else 0
    perm_mean_diff = float(np.mean(perm_diff_j)) if perm_diff_j else 0
    perm_lift = perm_mean_same / perm_mean_diff if perm_mean_diff > 0 else 1.0

    null_lifts.append(perm_lift)
    null_same_means.append(perm_mean_same)
    null_diff_means.append(perm_mean_diff)

# How often does null produce a lift >= observed?
null_lifts = np.array(null_lifts)
null_same_means = np.array(null_same_means)
perm_p_value = float(np.mean(null_lifts >= lift))
null_mean_lift = float(np.mean(null_lifts))
null_std_lift = float(np.std(null_lifts))
null_mean_same_mean = float(np.mean(null_same_means))

z_score = float((lift - null_mean_lift) / null_std_lift) if null_std_lift > 0 else 0.0

print(f"Null lift: {null_mean_lift:.4f} +/- {null_std_lift:.4f}")
print(f"Observed lift: {lift:.4f}")
print(f"Permutation p-value: {perm_p_value:.4f}")
print(f"Z-score vs null: {z_score:.2f}")


# ============================================================
# STEP 6: Paragraph-initial token prediction
# ============================================================
print("\n=== Paragraph-Initial Token Analysis ===")

# For each paragraph, take the first 3 tokens' MIDDLEs
# Test if these initial MIDDLEs predict kernel signature
initial_features = defaultdict(list)
for p in paragraphs:
    first_3 = [t['middle'] for t in p['tokens'][:3]
                if t['middle'] and t['middle'] != '_EMPTY_']
    initial_features[p['kernel_sig']].append(set(first_3))

# Build initial MIDDLE frequency by signature type
initial_vocab_by_sig = {}
for sig_type, mid_sets in initial_features.items():
    vocab = Counter()
    for ms in mid_sets:
        for m in ms:
            vocab[m] += 1
    initial_vocab_by_sig[sig_type] = vocab

# All initial MIDDLEs across all types
all_initial_middles = set()
for v in initial_vocab_by_sig.values():
    all_initial_middles.update(v.keys())

# For each MIDDLE, compute which signature it favors
# A MIDDLE "predicts" a signature if > 50% of its appearances are in that type
sig_types = list(sig_counts.keys())
predictive_middles = {}
for m in all_initial_middles:
    counts = {sig: initial_vocab_by_sig.get(sig, Counter()).get(m, 0) for sig in sig_types}
    total = sum(counts.values())
    if total >= 3:  # minimum occurrences
        dominant = max(counts, key=counts.get)
        dominant_frac = counts[dominant] / total
        if dominant_frac > 0.5:
            predictive_middles[m] = {
                'predicts': dominant,
                'fraction': round(dominant_frac, 3),
                'total_occurrences': total,
            }

# Test prediction accuracy: for each paragraph, use majority vote of
# initial MIDDLEs' predicted types
correct = 0
total_tested = 0
for p in paragraphs:
    first_3_middles = [t['middle'] for t in p['tokens'][:3]
                       if t['middle'] and t['middle'] != '_EMPTY_']
    predictions = []
    for m in first_3_middles:
        if m in predictive_middles:
            predictions.append(predictive_middles[m]['predicts'])

    if predictions:
        # Majority vote
        vote = Counter(predictions).most_common(1)[0][0]
        if vote == p['kernel_sig']:
            correct += 1
        total_tested += 1

prediction_accuracy = correct / total_tested if total_tested > 0 else 0
# Baseline: predict most common type
baseline_type = sig_counts.most_common(1)[0][0]
baseline_accuracy = sig_counts[baseline_type] / len(paragraphs)
accuracy_lift = prediction_accuracy / baseline_accuracy if baseline_accuracy > 0 else None

print(f"Paragraphs with predictive initial tokens: {total_tested}/{len(paragraphs)}")
print(f"Prediction accuracy (majority vote): {prediction_accuracy:.3f}")
print(f"Baseline (majority class '{baseline_type}'): {baseline_accuracy:.3f}")
if accuracy_lift:
    print(f"Accuracy lift over baseline: {accuracy_lift:.3f}x")
print(f"Predictive initial MIDDLEs found: {len(predictive_middles)}")

# Initial token prediction: is it better than chance?
# If accuracy > baseline by a significant margin, initial tokens encode type
initial_predicts = prediction_accuracy > baseline_accuracy + 0.05


# ============================================================
# STEP 7: Per kernel-signature-pair breakdown
# ============================================================
print("\n=== Per Signature-Pair Breakdown ===")
pair_type_jaccards = defaultdict(list)
for folio, pars in folio_pars.items():
    if len(pars) < 2:
        continue
    for i, j in combinations(range(len(pars)), 2):
        j_val = jaccard(pars[i]['middles'], pars[j]['middles'])
        sig_i = pars[i]['kernel_sig']
        sig_j = pars[j]['kernel_sig']
        pair_label = f"{min(sig_i, sig_j)}_vs_{max(sig_i, sig_j)}"
        pair_type_jaccards[pair_label].append(j_val)

pair_type_summary = {}
for label, vals in sorted(pair_type_jaccards.items()):
    pair_type_summary[label] = {
        'n_pairs': len(vals),
        'mean_jaccard': round(float(np.mean(vals)), 4),
        'median_jaccard': round(float(np.median(vals)), 4),
        'std_jaccard': round(float(np.std(vals)), 4),
    }
    is_same = label.split('_vs_')[0] == label.split('_vs_')[1]
    marker = ' [SAME]' if is_same else ''
    print(f"  {label}: n={len(vals)}, mean={np.mean(vals):.4f}, "
          f"median={np.median(vals):.4f}{marker}")


# ============================================================
# STEP 8: Effect size (Cohen's d)
# ============================================================
if same_kernel_jaccards and diff_kernel_jaccards:
    pooled_std = np.sqrt((std_same**2 + std_diff**2) / 2)
    cohens_d = (mean_same - mean_diff) / pooled_std if pooled_std > 0 else 0.0
    cohens_d = float(cohens_d)
else:
    cohens_d = 0.0

print(f"\nCohen's d (effect size): {cohens_d:.4f}")


# ============================================================
# STEP 9: Determine verdict
# ============================================================
significant = bool(p_value < 0.01)
lift_pass = bool(lift > 1.15)
perm_significant = bool(perm_p_value < 0.05)

if significant and lift_pass and perm_significant:
    verdict = 'PASS'
elif significant and lift > 1.10:
    verdict = 'MARGINAL'
else:
    verdict = 'FAIL'

print(f"\n=== VERDICT: {verdict} ===")
if verdict == 'PASS':
    print("Same-kernel paragraphs share significantly more vocabulary,")
    print("exceeding both statistical and permutation thresholds.")
elif verdict == 'MARGINAL':
    print("Statistically significant but lift is modest.")
else:
    print("Vocabulary overlap not strongly explained by kernel signature.")


# ============================================================
# STEP 10: Build output JSON
# ============================================================
output = {
    'test': 'paragraph_vocabulary_scope',
    'test_number': 3,
    'question': 'Do paragraphs sharing kernel signatures share more MIDDLE vocabulary?',
    'method': {
        'description': (
            'Pairwise Jaccard similarity of MIDDLE vocabulary sets within folios, '
            'stratified by kernel-signature match. Kernel signature is assigned '
            'via tertile classification on the k-h differential (k-proportion minus '
            'h-proportion per paragraph MIDDLE set).'
        ),
        'kernel_classification': {
            'method': 'Tertile on k-h differential',
            'HIGH_K': f'k-h diff > {q66:.3f} (top tertile)',
            'HIGH_H': f'k-h diff < {q33:.3f} (bottom tertile)',
            'BALANCED': f'k-h diff in [{q33:.3f}, {q66:.3f}]',
        },
        'min_paragraph_tokens': MIN_PARAGRAPH_TOKENS,
        'n_permutations': N_PERMUTATIONS,
        'permutation_strategy': (
            'Shuffle kernel signatures within each folio while preserving '
            'MIDDLE sets. This tests whether kernel-vocabulary coupling is '
            'genuine or an artifact of folio structure.'
        ),
    },
    'data_summary': {
        'total_currier_b_tokens': len(all_tokens),
        'total_paragraphs': len(paragraphs),
        'folios_with_paragraphs': len(folio_pars),
        'folios_with_2plus_paragraphs': n_folios_2plus,
        'kernel_signature_distribution': {k: int(v) for k, v in sig_counts.items()},
        'kh_differential': {
            'mean': round(float(np.mean(kh_diffs_arr)), 4),
            'std': round(float(np.std(kh_diffs_arr)), 4),
            'q33': round(q33, 4),
            'q66': round(q66, 4),
        },
        'group_profiles': {
            sig: {
                'n': int(sig_counts[sig]),
                'mean_k_prop': round(float(np.mean([p['k_prop'] for p in paragraphs if p['kernel_sig'] == sig])), 4),
                'mean_h_prop': round(float(np.mean([p['h_prop'] for p in paragraphs if p['kernel_sig'] == sig])), 4),
                'mean_e_prop': round(float(np.mean([p['e_prop'] for p in paragraphs if p['kernel_sig'] == sig])), 4),
                'mean_vocab_size': round(float(np.mean([len(p['middles']) for p in paragraphs if p['kernel_sig'] == sig])), 1),
            }
            for sig in ['HIGH_K', 'HIGH_H', 'BALANCED']
        },
    },
    'pairwise_results': {
        'n_same_kernel_pairs': len(same_kernel_jaccards),
        'n_diff_kernel_pairs': len(diff_kernel_jaccards),
        'mean_jaccard_same': round(mean_same, 4),
        'mean_jaccard_diff': round(mean_diff, 4),
        'median_jaccard_same': round(median_same, 4),
        'median_jaccard_diff': round(median_diff, 4),
        'std_jaccard_same': round(std_same, 4),
        'std_jaccard_diff': round(std_diff, 4),
        'lift_same_over_diff': round(lift, 4),
        'cohens_d': round(cohens_d, 4),
    },
    'statistical_test': {
        'test': 'Mann-Whitney U (one-sided: same > diff)',
        'U_statistic': round(u_stat, 1),
        'p_value': round(p_value, 8),
        'significant_at_001': significant,
    },
    'permutation_null': {
        'n_permutations': N_PERMUTATIONS,
        'null_mean_lift': round(null_mean_lift, 4),
        'null_std_lift': round(null_std_lift, 4),
        'observed_lift': round(lift, 4),
        'z_score': round(z_score, 2),
        'permutation_p_value': round(perm_p_value, 4),
        'exceeds_null': perm_significant,
    },
    'pair_type_breakdown': pair_type_summary,
    'paragraph_initial_prediction': {
        'description': 'Can first 3 tokens predict paragraph kernel signature?',
        'paragraphs_testable': total_tested,
        'paragraphs_total': len(paragraphs),
        'prediction_accuracy': round(prediction_accuracy, 4),
        'baseline_accuracy': round(baseline_accuracy, 4),
        'accuracy_lift': round(accuracy_lift, 4) if accuracy_lift else None,
        'initial_tokens_predictive': bool(initial_predicts),
        'predictive_middles_count': len(predictive_middles),
        'top_predictive_middles': dict(sorted(
            predictive_middles.items(),
            key=lambda x: x[1]['total_occurrences'],
            reverse=True
        )[:10]),
    },
    'pass_criteria': {
        'required_p_value': '< 0.01',
        'required_lift': '> 1.15',
        'required_perm_exceed': True,
    },
    'verdict': verdict,
    'interpretation': (
        'Same-kernel paragraphs share significantly more MIDDLE vocabulary, '
        'suggesting kernel signature reflects a material scope constraint. '
        'Paragraphs with similar k-h balance draw from overlapping vocabulary pools.'
        if verdict == 'PASS' else
        'Marginal evidence for kernel-vocabulary coupling. Same-kernel paragraphs '
        'show statistically significant but modest vocabulary overlap advantage.'
        if verdict == 'MARGINAL' else
        'Vocabulary overlap is not strongly explained by kernel signature. '
        'Paragraph MIDDLE vocabulary appears driven by folio-level pool rather '
        'than by kernel process mode.'
    ),
}

with open(OUTPUT_PATH, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nOutput written to {OUTPUT_PATH}")
