#!/usr/bin/env python3
"""
DIRECTION C: A<->B INTEGRATION MECHANICS

Bounded analysis of how Currier A vocabulary appears in Currier B execution.

ALLOWED:
- Measure vocabulary overlap between A and B
- Track which A-sections source shared tokens
- Test sequential vs semantic access patterns
- Measure predictive power of B-signature for A-references

NOT ALLOWED:
- Semantic interpretation of what tokens mean
- Claims about physical materials
- Reopening A/B disjunction (that's proven)

Tests:
C-1: A-vocabulary presence in B folios
C-2: A-section source identification
C-3: Sequential vs semantic access pattern
C-4: Predictive power (B-signature -> A-reference)

STOP CONDITIONS:
- A-tokens in B < 5% -> integration negligible
- No pattern survives null model -> random access
- Max 2 Tier 2 constraints
"""

import os
import json
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import spearmanr, pearsonr, chi2_contingency
from scipy.spatial.distance import cosine

os.chdir('C:/git/voynich')

print("=" * 70)
print("DIRECTION C: A<->B INTEGRATION MECHANICS")
print("Bounded analysis of A-vocabulary in B execution")
print("=" * 70)

# ==========================================================================
# LOAD DATA
# ==========================================================================

print("\nLoading data...")

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        all_tokens.append(row)

# Separate by Currier language
a_tokens = [t for t in all_tokens if t.get('language', '') == 'A']
b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']

a_words = [t.get('word', '') for t in a_tokens if t.get('word', '')]
b_words = [t.get('word', '') for t in b_tokens if t.get('word', '')]

# Get vocabularies
a_vocab = set(a_words)
b_vocab = set(b_words)
shared_vocab = a_vocab & b_vocab

print(f"\nCorpus overview:")
print(f"  Currier A tokens: {len(a_words)}")
print(f"  Currier B tokens: {len(b_words)}")
print(f"  A vocabulary size: {len(a_vocab)}")
print(f"  B vocabulary size: {len(b_vocab)}")
print(f"  Shared vocabulary: {len(shared_vocab)}")

# Get folios by language
a_folios = defaultdict(list)
b_folios = defaultdict(list)

for t in all_tokens:
    folio = t.get('folio', '')
    word = t.get('word', '')
    lang = t.get('language', '')
    section = t.get('section', '')

    if lang == 'A' and word:
        a_folios[folio].append({'word': word, 'section': section})
    elif lang == 'B' and word:
        b_folios[folio].append({'word': word, 'section': section})

print(f"  A folios: {len(a_folios)}")
print(f"  B folios: {len(b_folios)}")

# Get A-token section mapping (which section each A-token primarily comes from)
a_token_sections = defaultdict(lambda: Counter())
for t in a_tokens:
    word = t.get('word', '')
    section = t.get('section', '')
    if word and section:
        a_token_sections[word][section] += 1

# ==========================================================================
# C-1: A-VOCABULARY PRESENCE IN B FOLIOS
# ==========================================================================

print("\n" + "=" * 70)
print("C-1: A-VOCABULARY PRESENCE IN B FOLIOS")
print("Question: What % of B vocabulary overlaps with A?")
print("=" * 70)

# Overall overlap
b_tokens_in_a = sum(1 for w in b_words if w in a_vocab)
b_types_in_a = len(b_vocab & a_vocab)

print(f"\nOverall B -> A overlap:")
print(f"  B tokens that are also in A: {b_tokens_in_a} / {len(b_words)} ({100*b_tokens_in_a/len(b_words):.1f}%)")
print(f"  B types that are also in A: {b_types_in_a} / {len(b_vocab)} ({100*b_types_in_a/len(b_vocab):.1f}%)")

# Per-folio distribution
folio_overlap_pct = {}
folio_overlap_counts = {}

for folio, tokens in b_folios.items():
    words = [t['word'] for t in tokens]
    in_a = sum(1 for w in words if w in a_vocab)
    pct = 100 * in_a / len(words) if words else 0
    folio_overlap_pct[folio] = pct
    folio_overlap_counts[folio] = in_a

# Distribution stats
pcts = list(folio_overlap_pct.values())
print(f"\nPer-folio overlap distribution:")
print(f"  Mean: {np.mean(pcts):.1f}%")
print(f"  Std: {np.std(pcts):.1f}%")
print(f"  Min: {np.min(pcts):.1f}%")
print(f"  Max: {np.max(pcts):.1f}%")
print(f"  Median: {np.median(pcts):.1f}%")

# Check if overlap > 5% threshold
c1_verdict = "SUBSTANTIAL" if np.mean(pcts) >= 5 else "NEGLIGIBLE"
print(f"\nC-1 VERDICT: {c1_verdict} (threshold 5%)")

# ==========================================================================
# C-2: A-SECTION SOURCE IDENTIFICATION
# ==========================================================================

print("\n" + "=" * 70)
print("C-2: A-SECTION SOURCE IDENTIFICATION")
print("Question: Which A-sections source the shared tokens in B?")
print("=" * 70)

# For each shared token in B, determine its primary A-section
section_sources = Counter()
section_token_counts = Counter()

for folio, tokens in b_folios.items():
    for t in tokens:
        word = t['word']
        if word in a_vocab:
            # Get primary A-section for this token
            if word in a_token_sections:
                primary_section = a_token_sections[word].most_common(1)[0][0]
                section_sources[primary_section] += 1
                section_token_counts[primary_section] += 1

print(f"\nShared tokens in B by primary A-section source:")
total_shared = sum(section_sources.values())
for section, count in section_sources.most_common():
    pct = 100 * count / total_shared
    print(f"  {section}: {count} ({pct:.1f}%)")

# Compare to baseline (A-section distribution overall)
a_section_baseline = Counter(t.get('section', '') for t in a_tokens if t.get('section', ''))
print(f"\nA-section baseline distribution:")
total_a = sum(a_section_baseline.values())
for section, count in a_section_baseline.most_common():
    pct = 100 * count / total_a
    print(f"  {section}: {count} ({pct:.1f}%)")

# Chi-square test for section source vs baseline
# Build contingency table
sections = list(set(section_sources.keys()) | set(a_section_baseline.keys()))
sections = [s for s in sections if s]  # Remove empty

observed = [section_sources.get(s, 0) for s in sections]
expected_raw = [a_section_baseline.get(s, 0) for s in sections]
expected_total = sum(expected_raw)
if expected_total > 0:
    expected = [total_shared * e / expected_total for e in expected_raw]

    # Chi-square
    chi2 = sum((o - e) ** 2 / e for o, e in zip(observed, expected) if e > 0)
    dof = len([e for e in expected if e > 0]) - 1
    from scipy.stats import chi2 as chi2_dist
    p_value = 1 - chi2_dist.cdf(chi2, dof) if dof > 0 else 1.0

    print(f"\nChi-square test (observed vs A baseline):")
    print(f"  Chi2 = {chi2:.2f}, dof = {dof}, p = {p_value:.6f}")

    if p_value < 0.05:
        print("  RESULT: Section sources are NOT proportional to A baseline")
    else:
        print("  RESULT: Section sources are approximately proportional to A baseline")

# Calculate enrichment/depletion
print(f"\nSection enrichment in B's A-references:")
for section in sections:
    obs_pct = 100 * section_sources.get(section, 0) / total_shared if total_shared > 0 else 0
    exp_pct = 100 * a_section_baseline.get(section, 0) / total_a if total_a > 0 else 0
    ratio = obs_pct / exp_pct if exp_pct > 0 else 0
    status = "ENRICHED" if ratio > 1.5 else "DEPLETED" if ratio < 0.67 else "NORMAL"
    print(f"  {section}: {obs_pct:.1f}% vs {exp_pct:.1f}% expected -> {ratio:.2f}x ({status})")

# ==========================================================================
# C-3: SEQUENTIAL VS SEMANTIC ACCESS PATTERN
# ==========================================================================

print("\n" + "=" * 70)
print("C-3: SEQUENTIAL VS SEMANTIC ACCESS PATTERN")
print("Question: Does A-reference correlate with B-folio adjacency or similarity?")
print("=" * 70)

# Build A-reference vector for each B folio
# Vector = count of each shared token
shared_tokens_list = list(shared_vocab)
b_folio_vectors = {}

for folio, tokens in b_folios.items():
    vector = np.zeros(len(shared_tokens_list))
    for t in tokens:
        word = t['word']
        if word in shared_vocab:
            idx = shared_tokens_list.index(word)
            vector[idx] += 1
    b_folio_vectors[folio] = vector

# Sort B folios by folio number (approximate manuscript order)
def folio_sort_key(f):
    # Extract numeric part
    import re
    match = re.search(r'(\d+)', f)
    return int(match.group(1)) if match else 0

sorted_b_folios = sorted(b_folio_vectors.keys(), key=folio_sort_key)

# Test 1: Adjacent folio correlation
adjacent_similarities = []
for i in range(len(sorted_b_folios) - 1):
    f1 = sorted_b_folios[i]
    f2 = sorted_b_folios[i + 1]
    v1 = b_folio_vectors[f1]
    v2 = b_folio_vectors[f2]

    # Cosine similarity (handle zero vectors)
    if np.sum(v1) > 0 and np.sum(v2) > 0:
        sim = 1 - cosine(v1, v2)
        adjacent_similarities.append(sim)

# Test 2: Random (non-adjacent) folio correlation
import random
random.seed(42)
random_pairs = []
for _ in range(len(adjacent_similarities) * 10):  # More samples for stability
    f1, f2 = random.sample(sorted_b_folios, 2)
    # Ensure not adjacent
    idx1 = sorted_b_folios.index(f1)
    idx2 = sorted_b_folios.index(f2)
    if abs(idx1 - idx2) > 1:
        v1 = b_folio_vectors[f1]
        v2 = b_folio_vectors[f2]
        if np.sum(v1) > 0 and np.sum(v2) > 0:
            sim = 1 - cosine(v1, v2)
            random_pairs.append(sim)

mean_adjacent = np.mean(adjacent_similarities) if adjacent_similarities else 0
mean_random = np.mean(random_pairs) if random_pairs else 0

print(f"\nA-reference similarity between B folios:")
print(f"  Adjacent folios: {mean_adjacent:.3f} (n={len(adjacent_similarities)})")
print(f"  Non-adjacent folios: {mean_random:.3f} (n={len(random_pairs)})")

# Test significance
from scipy.stats import mannwhitneyu
if adjacent_similarities and random_pairs:
    stat, p = mannwhitneyu(adjacent_similarities, random_pairs, alternative='greater')
    print(f"\nMann-Whitney test (adjacent > random):")
    print(f"  U = {stat:.0f}, p = {p:.6f}")

    if p < 0.05 and mean_adjacent > mean_random:
        print("  RESULT: SEQUENTIAL ACCESS supported (adjacent folios more similar)")
        c3_verdict = "SEQUENTIAL"
    elif p < 0.05 and mean_adjacent < mean_random:
        print("  RESULT: ANTI-SEQUENTIAL (adjacent folios less similar)")
        c3_verdict = "ANTI_SEQUENTIAL"
    else:
        print("  RESULT: NO SEQUENTIAL PATTERN (random access)")
        c3_verdict = "RANDOM"
else:
    c3_verdict = "INSUFFICIENT_DATA"

# Test 3: Semantic similarity (based on B operational signature)
# Build operational signature for each B folio
print(f"\nBuilding B operational signatures...")

def is_link(word):
    return 'ol' in word if word else False

def get_kernel_class(word):
    if not word:
        return None
    if word.endswith('k') or word in ['ok', 'yk', 'ak', 'ek']:
        return 'k'
    if word.endswith('h') or word in ['oh', 'yh', 'ah', 'eh']:
        return 'h'
    if word.endswith('ey') or word.endswith('eey') or word.endswith('edy'):
        return 'e'
    return None

b_folio_signatures = {}
for folio, tokens in b_folios.items():
    words = [t['word'] for t in tokens]
    link_density = sum(1 for w in words if is_link(w)) / len(words) if words else 0
    kernel_contact = sum(1 for w in words if get_kernel_class(w) is not None) / len(words) if words else 0
    unique_ratio = len(set(words)) / len(words) if words else 0

    b_folio_signatures[folio] = np.array([link_density, kernel_contact, unique_ratio])

# Similar B folios should have similar A-references?
similar_b_pairs = []
dissimilar_b_pairs = []

b_folio_list = list(b_folio_signatures.keys())
for i in range(len(b_folio_list)):
    for j in range(i + 1, len(b_folio_list)):
        f1 = b_folio_list[i]
        f2 = b_folio_list[j]

        sig1 = b_folio_signatures[f1]
        sig2 = b_folio_signatures[f2]

        # B-signature similarity
        b_sim = 1 - cosine(sig1, sig2) if np.sum(sig1) > 0 and np.sum(sig2) > 0 else 0

        # A-reference similarity
        v1 = b_folio_vectors[f1]
        v2 = b_folio_vectors[f2]
        a_sim = 1 - cosine(v1, v2) if np.sum(v1) > 0 and np.sum(v2) > 0 else 0

        if b_sim > 0.8:  # Similar B folios
            similar_b_pairs.append(a_sim)
        elif b_sim < 0.5:  # Dissimilar B folios
            dissimilar_b_pairs.append(a_sim)

mean_similar_b = np.mean(similar_b_pairs) if similar_b_pairs else 0
mean_dissimilar_b = np.mean(dissimilar_b_pairs) if dissimilar_b_pairs else 0

print(f"\nA-reference similarity by B-signature similarity:")
print(f"  Similar B-signature: {mean_similar_b:.3f} (n={len(similar_b_pairs)})")
print(f"  Dissimilar B-signature: {mean_dissimilar_b:.3f} (n={len(dissimilar_b_pairs)})")

if similar_b_pairs and dissimilar_b_pairs:
    stat, p = mannwhitneyu(similar_b_pairs, dissimilar_b_pairs, alternative='greater')
    print(f"\nMann-Whitney test (similar B -> similar A-ref):")
    print(f"  U = {stat:.0f}, p = {p:.6f}")

    if p < 0.05 and mean_similar_b > mean_dissimilar_b:
        print("  RESULT: SEMANTIC ACCESS supported (similar programs use similar A-vocab)")
        c3_semantic = "SEMANTIC"
    else:
        print("  RESULT: NO SEMANTIC PATTERN")
        c3_semantic = "NONE"
else:
    c3_semantic = "INSUFFICIENT_DATA"

# ==========================================================================
# C-4: PREDICTIVE POWER (B-SIGNATURE -> A-REFERENCE)
# ==========================================================================

print("\n" + "=" * 70)
print("C-4: PREDICTIVE POWER TEST")
print("Question: Can B-signature predict which A-tokens appear?")
print("=" * 70)

# Build feature matrix and target
# Features: B operational signature (LINK density, kernel contact, unique ratio, section)
# Target: A-reference vector (which shared tokens appear)

# Get B-folio sections
b_folio_sections = {}
for folio, tokens in b_folios.items():
    sections = [t['section'] for t in tokens if t['section']]
    b_folio_sections[folio] = Counter(sections).most_common(1)[0][0] if sections else 'unknown'

# Measure mutual information between B-signature and A-reference presence
# Simplified: For each A-token, does it correlate with any B-signature feature?

print(f"\nCorrelation between B-features and A-token presence:")

# Pick top 20 most common shared tokens
shared_token_counts = Counter()
for folio, tokens in b_folios.items():
    for t in tokens:
        if t['word'] in shared_vocab:
            shared_token_counts[t['word']] += 1

top_shared = [w for w, c in shared_token_counts.most_common(20)]

# For each top shared token, correlate with B-features
correlations = []
for token in top_shared:
    # Binary presence in each folio
    token_present = [1 if any(t['word'] == token for t in b_folios[f]) else 0
                     for f in sorted_b_folios]

    # B-features
    link_densities = [b_folio_signatures[f][0] for f in sorted_b_folios]
    kernel_contacts = [b_folio_signatures[f][1] for f in sorted_b_folios]

    # Point-biserial correlation (binary vs continuous)
    if sum(token_present) > 2 and sum(token_present) < len(token_present) - 2:
        r_link, p_link = pearsonr(token_present, link_densities)
        r_kernel, p_kernel = pearsonr(token_present, kernel_contacts)
        correlations.append({
            'token': token,
            'r_link': r_link,
            'p_link': p_link,
            'r_kernel': r_kernel,
            'p_kernel': p_kernel
        })

print(f"\nTop shared tokens correlation with B-features:")
print(f"{'Token':<15} {'r(LINK)':<10} {'p':<10} {'r(kernel)':<10} {'p':<10}")
print("-" * 55)

significant_correlations = 0
for c in correlations[:10]:
    link_sig = "*" if c['p_link'] < 0.05 else ""
    kernel_sig = "*" if c['p_kernel'] < 0.05 else ""
    print(f"{c['token']:<15} {c['r_link']:>7.3f}{link_sig:<2} {c['p_link']:<10.4f} {c['r_kernel']:>7.3f}{kernel_sig:<2} {c['p_kernel']:<10.4f}")
    if c['p_link'] < 0.05 or c['p_kernel'] < 0.05:
        significant_correlations += 1

print(f"\nSignificant correlations: {significant_correlations}/{len(correlations[:10])}")

# Overall assessment
# How much variance in A-reference is explained by B-signature?
# Use regression R² as proxy

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# Build matrices
X = np.array([b_folio_signatures[f] for f in sorted_b_folios])
y = np.array([b_folio_vectors[f] for f in sorted_b_folios])

# Only use non-zero A-reference tokens
nonzero_cols = np.where(y.sum(axis=0) > 0)[0]
y_reduced = y[:, nonzero_cols]

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Fit regression for each A-token column
r2_scores = []
for col in range(y_reduced.shape[1]):
    if y_reduced[:, col].std() > 0:
        model = LinearRegression()
        model.fit(X_scaled, y_reduced[:, col])
        y_pred = model.predict(X_scaled)
        ss_res = np.sum((y_reduced[:, col] - y_pred) ** 2)
        ss_tot = np.sum((y_reduced[:, col] - y_reduced[:, col].mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        r2_scores.append(max(0, r2))  # Clip negative R²

mean_r2 = np.mean(r2_scores) if r2_scores else 0
print(f"\nPredictive power (B-signature -> A-reference):")
print(f"  Mean R² across A-tokens: {mean_r2:.3f}")
print(f"  Max R²: {max(r2_scores):.3f}" if r2_scores else "  Max R²: N/A")
print(f"  Min R²: {min(r2_scores):.3f}" if r2_scores else "  Min R²: N/A")

if mean_r2 > 0.1:
    c4_verdict = "PREDICTIVE"
    print(f"  VERDICT: B-signature has PREDICTIVE power for A-references")
else:
    c4_verdict = "NOT_PREDICTIVE"
    print(f"  VERDICT: B-signature has WEAK/NO predictive power")

# ==========================================================================
# SUMMARY AND VERDICT
# ==========================================================================

print("\n" + "=" * 70)
print("DIRECTION C: SUMMARY AND VERDICT")
print("=" * 70)

results = {
    'c1_overlap': {
        'token_pct': 100 * b_tokens_in_a / len(b_words),
        'type_pct': 100 * b_types_in_a / len(b_vocab),
        'mean_folio_pct': np.mean(pcts),
        'verdict': c1_verdict
    },
    'c2_section_source': {
        'distribution': dict(section_sources),
        'dominant_section': section_sources.most_common(1)[0][0] if section_sources else None,
        'dominant_pct': 100 * section_sources.most_common(1)[0][1] / total_shared if section_sources and total_shared > 0 else 0
    },
    'c3_access_pattern': {
        'adjacent_similarity': mean_adjacent,
        'random_similarity': mean_random,
        'sequential_verdict': c3_verdict,
        'semantic_verdict': c3_semantic,
        'similar_b_a_sim': mean_similar_b,
        'dissimilar_b_a_sim': mean_dissimilar_b
    },
    'c4_predictive': {
        'mean_r2': mean_r2,
        'significant_token_correlations': significant_correlations,
        'verdict': c4_verdict
    }
}

print(f"\nFINDINGS:")
print(f"  C-1: A-vocabulary in B = {results['c1_overlap']['mean_folio_pct']:.1f}% -> {c1_verdict}")
print(f"  C-2: Dominant A-section source = {results['c2_section_source']['dominant_section']} ({results['c2_section_source']['dominant_pct']:.1f}%)")
print(f"  C-3: Access pattern = {c3_verdict} (sequential), {c3_semantic} (semantic)")
print(f"  C-4: Predictive power = {c4_verdict} (R² = {mean_r2:.3f})")

# Hard stop evaluation
print(f"\nHARD STOP EVALUATION:")
if results['c1_overlap']['mean_folio_pct'] < 5:
    print("  STOP 1: Integration < 5% -> TRIGGERED")
    overall_verdict = "NEGLIGIBLE_INTEGRATION"
else:
    print("  STOP 1: Integration >= 5% -> NOT triggered")

    if c3_verdict == "RANDOM" and c3_semantic == "NONE" and c4_verdict == "NOT_PREDICTIVE":
        print("  STOP 2: No pattern survives -> TRIGGERED")
        overall_verdict = "RANDOM_ACCESS"
    else:
        print("  STOP 2: Pattern detected -> NOT triggered")
        overall_verdict = "STRUCTURED_INTEGRATION"

print(f"\nOVERALL VERDICT: {overall_verdict}")

# Determine constraints to add
constraints = []

if results['c1_overlap']['mean_folio_pct'] >= 5:
    constraints.append(f"A-B vocabulary integration: {results['c1_overlap']['mean_folio_pct']:.1f}% of B tokens appear in A; substantial cross-system vocabulary")

if results['c2_section_source']['dominant_pct'] > 60:
    constraints.append(f"Section H dominance in A-references: {results['c2_section_source']['dominant_pct']:.1f}% of shared tokens source from H; confirms CAS-XREF")

if c3_verdict != "RANDOM" or c3_semantic != "NONE":
    if c3_verdict == "SEQUENTIAL":
        constraints.append("Sequential A-access: Adjacent B folios share more A-vocabulary than random pairs")
    if c3_semantic == "SEMANTIC":
        constraints.append("Semantic A-access: Similar B-programs use similar A-vocabulary")

print(f"\nPROPOSED CONSTRAINTS ({len(constraints)}):")
for c in constraints:
    print(f"  - {c}")

print("\n" + "=" * 70)
print("DIRECTION C: CLOSED")
print("A<->B integration investigation is now COMPLETE.")
print("=" * 70)

# Save results
os.makedirs('phases/AB_integration_mechanics', exist_ok=True)
with open('phases/AB_integration_mechanics/ab_integration_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to phases/AB_integration_mechanics/ab_integration_results.json")
