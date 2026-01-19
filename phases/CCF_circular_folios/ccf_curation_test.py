# CCF Curation Test: Are hazard-proximal runs in CCFs unusually similar?
# Compare internal similarity of hazard runs: CCF vs non-CCF

import json
import re
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime
from itertools import combinations

print("=" * 70)
print("CCF CURATION TEST")
print("Are CCF hazard-runs unusually similar to each other?")
print("=" * 70)

# Load data
def load_corpus():
    records = []
    with open('C:/git/voynich/data/transcriptions/interlinear_full_words.txt', 'r', encoding='latin-1') as f:
        f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 12:
                # CRITICAL: Filter to H-only transcriber track
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                parts = [p.strip('"') for p in parts]
                records.append({
                    'word': parts[0],
                    'folio': parts[2],
                    'line': parts[11] if len(parts) > 11 else '0'
                })
    return records

def load_hazard_nodes():
    try:
        with open('C:/git/voynich/phase18a_forbidden_inventory.json', 'r') as f:
            data = json.load(f)
        hazard = set()
        for trans in data.get('transitions', []):
            hazard.add(trans.get('source', ''))
            hazard.add(trans.get('target', ''))
        return hazard
    except:
        return set()

print("\n[1] Loading data...")
records = load_corpus()
hazard_nodes = load_hazard_nodes()
print(f"    {len(records)} records, {len(hazard_nodes)} hazard nodes")

# Partition into CCF vs non-CCF
circular_pattern = re.compile(r'^f(67|68|69|70|71|72|73)')
ccf_folios = defaultdict(lambda: defaultdict(list))
non_ccf_folios = defaultdict(lambda: defaultdict(list))

for r in records:
    folio = r['folio']
    try:
        line = int(r['line'])
    except:
        line = 0

    if circular_pattern.match(folio):
        ccf_folios[folio][line].append(r['word'])
    else:
        non_ccf_folios[folio][line].append(r['word'])

print(f"    CCF folios: {len(ccf_folios)}")
print(f"    Non-CCF folios: {len(non_ccf_folios)}")

# =============================================================================
# EXTRACT HAZARD-PROXIMAL RUNS
# =============================================================================

def extract_hazard_runs(folios, hazard_nodes, min_hazard_density=0.05):
    """Extract line-runs with above-threshold hazard density."""
    runs = []
    for folio, lines in folios.items():
        for line_num, tokens in lines.items():
            if len(tokens) < 3:
                continue
            hazard_count = sum(1 for t in tokens if t in hazard_nodes)
            density = hazard_count / len(tokens)
            if density >= min_hazard_density:
                runs.append({
                    'folio': folio,
                    'line': line_num,
                    'tokens': tokens,
                    'hazard_density': density,
                    'length': len(tokens)
                })
    return runs

print("\n[2] Extracting hazard-proximal runs...")
ccf_hazard_runs = extract_hazard_runs(ccf_folios, hazard_nodes)
non_ccf_hazard_runs = extract_hazard_runs(non_ccf_folios, hazard_nodes)

print(f"    CCF hazard runs: {len(ccf_hazard_runs)}")
print(f"    Non-CCF hazard runs: {len(non_ccf_hazard_runs)}")

# =============================================================================
# COMPUTE PAIRWISE SIMILARITY
# =============================================================================

def compute_run_similarity(run1, run2):
    """Jaccard similarity of token sets."""
    set1 = set(run1['tokens'])
    set2 = set(run2['tokens'])
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / max(union, 1)

def compute_bigram_similarity(run1, run2):
    """Jaccard similarity of bigram sets."""
    def get_bigrams(tokens):
        return set((tokens[i], tokens[i+1]) for i in range(len(tokens)-1))
    bg1 = get_bigrams(run1['tokens'])
    bg2 = get_bigrams(run2['tokens'])
    intersection = len(bg1 & bg2)
    union = len(bg1 | bg2)
    return intersection / max(union, 1)

def sample_pairwise_similarities(runs, n_samples=1000, sim_func=compute_run_similarity):
    """Sample pairwise similarities from a list of runs."""
    if len(runs) < 2:
        return []

    similarities = []
    pairs = list(combinations(range(len(runs)), 2))

    if len(pairs) <= n_samples:
        sample_pairs = pairs
    else:
        import random
        sample_pairs = random.sample(pairs, n_samples)

    for i, j in sample_pairs:
        sim = sim_func(runs[i], runs[j])
        similarities.append(sim)

    return similarities

print("\n[3] Computing pairwise similarities...")

# Token-level similarity
ccf_token_sims = sample_pairwise_similarities(ccf_hazard_runs, n_samples=2000)
non_ccf_token_sims = sample_pairwise_similarities(non_ccf_hazard_runs, n_samples=2000)

print(f"    CCF token similarities: {len(ccf_token_sims)} pairs")
print(f"    Non-CCF token similarities: {len(non_ccf_token_sims)} pairs")

# Bigram-level similarity
ccf_bigram_sims = sample_pairwise_similarities(ccf_hazard_runs, n_samples=2000, sim_func=compute_bigram_similarity)
non_ccf_bigram_sims = sample_pairwise_similarities(non_ccf_hazard_runs, n_samples=2000, sim_func=compute_bigram_similarity)

print(f"    CCF bigram similarities: {len(ccf_bigram_sims)} pairs")
print(f"    Non-CCF bigram similarities: {len(non_ccf_bigram_sims)} pairs")

# =============================================================================
# STATISTICAL COMPARISON
# =============================================================================

print("\n[4] Statistical comparison...")

def compare_distributions(ccf_sims, non_ccf_sims, name):
    ccf_mean = np.mean(ccf_sims)
    ccf_std = np.std(ccf_sims)
    non_ccf_mean = np.mean(non_ccf_sims)
    non_ccf_std = np.std(non_ccf_sims)

    # Effect size (Cohen's d)
    pooled_std = np.sqrt((ccf_std**2 + non_ccf_std**2) / 2)
    cohens_d = (ccf_mean - non_ccf_mean) / max(pooled_std, 0.0001)

    # Mann-Whitney U test (non-parametric)
    from scipy import stats
    u_stat, p_value = stats.mannwhitneyu(ccf_sims, non_ccf_sims, alternative='two-sided')

    print(f"\n  {name}:")
    print(f"    CCF mean: {ccf_mean:.4f} (std: {ccf_std:.4f})")
    print(f"    Non-CCF mean: {non_ccf_mean:.4f} (std: {non_ccf_std:.4f})")
    print(f"    Cohen's d: {cohens_d:.3f}")
    print(f"    Mann-Whitney p: {p_value:.2e}")

    if cohens_d > 0.2:
        verdict = "CCF_MORE_SIMILAR"
    elif cohens_d < -0.2:
        verdict = "NON_CCF_MORE_SIMILAR"
    else:
        verdict = "NO_DIFFERENCE"

    print(f"    Verdict: {verdict}")

    return {
        'ccf_mean': float(ccf_mean),
        'ccf_std': float(ccf_std),
        'non_ccf_mean': float(non_ccf_mean),
        'non_ccf_std': float(non_ccf_std),
        'cohens_d': float(cohens_d),
        'p_value': float(p_value),
        'verdict': verdict
    }

token_comparison = compare_distributions(ccf_token_sims, non_ccf_token_sims, "Token-level similarity")
bigram_comparison = compare_distributions(ccf_bigram_sims, non_ccf_bigram_sims, "Bigram-level similarity")

# =============================================================================
# ADDITIONAL TEST: Vocabulary overlap
# =============================================================================

print("\n[5] Vocabulary analysis...")

ccf_vocab = Counter()
for run in ccf_hazard_runs:
    for t in run['tokens']:
        ccf_vocab[t] += 1

non_ccf_vocab = Counter()
for run in non_ccf_hazard_runs:
    for t in run['tokens']:
        non_ccf_vocab[t] += 1

ccf_types = set(ccf_vocab.keys())
non_ccf_types = set(non_ccf_vocab.keys())

overlap = ccf_types & non_ccf_types
ccf_only = ccf_types - non_ccf_types
non_ccf_only = non_ccf_types - ccf_types

print(f"    CCF hazard vocabulary: {len(ccf_types)} types")
print(f"    Non-CCF hazard vocabulary: {len(non_ccf_types)} types")
print(f"    Overlap: {len(overlap)} ({len(overlap)/len(ccf_types | non_ccf_types):.1%})")
print(f"    CCF-only: {len(ccf_only)}")
print(f"    Non-CCF-only: {len(non_ccf_only)}")

# Concentration test: do CCF runs use fewer unique tokens more repeatedly?
ccf_concentration = sum(ccf_vocab.values()) / len(ccf_vocab) if ccf_vocab else 0
non_ccf_concentration = sum(non_ccf_vocab.values()) / len(non_ccf_vocab) if non_ccf_vocab else 0

print(f"\n    CCF token concentration: {ccf_concentration:.2f} occurrences/type")
print(f"    Non-CCF token concentration: {non_ccf_concentration:.2f} occurrences/type")

if ccf_concentration > non_ccf_concentration * 1.2:
    concentration_verdict = "CCF_MORE_CONCENTRATED"
elif non_ccf_concentration > ccf_concentration * 1.2:
    concentration_verdict = "NON_CCF_MORE_CONCENTRATED"
else:
    concentration_verdict = "SIMILAR_CONCENTRATION"

print(f"    Concentration verdict: {concentration_verdict}")

# =============================================================================
# FINAL VERDICT
# =============================================================================

print("\n" + "=" * 70)
print("FINAL VERDICT")
print("=" * 70)

verdicts = {
    'token_similarity': token_comparison['verdict'],
    'bigram_similarity': bigram_comparison['verdict'],
    'concentration': concentration_verdict
}

ccf_curated_signals = sum(1 for v in verdicts.values() if 'CCF' in v and 'MORE' in v)
non_ccf_signals = sum(1 for v in verdicts.values() if 'NON_CCF' in v)
neutral_signals = sum(1 for v in verdicts.values() if 'NO_DIFFERENCE' in v or 'SIMILAR' in v)

print(f"  Token similarity: {verdicts['token_similarity']}")
print(f"  Bigram similarity: {verdicts['bigram_similarity']}")
print(f"  Vocabulary concentration: {verdicts['concentration']}")

if ccf_curated_signals >= 2:
    overall = "DELIBERATELY_CURATED"
    interpretation = "CCF hazard runs are MORE similar to each other than non-CCF hazard runs. This suggests deliberate selection of edge cases."
elif non_ccf_signals >= 2:
    overall = "RANDOM_SAMPLE"
    interpretation = "CCF hazard runs are LESS similar than non-CCF runs. CCFs may be deliberately diverse examples."
else:
    overall = "COLLECTED_EXAMPLES"
    interpretation = "CCF hazard runs show similar internal diversity to non-CCF runs. CCFs appear to be typical hazard-proximal content, not specially curated."

print(f"\n  OVERALL: {overall}")
print(f"  Interpretation: {interpretation}")

# Save results
results = {
    'metadata': {
        'timestamp': datetime.now().isoformat(),
        'ccf_hazard_runs': len(ccf_hazard_runs),
        'non_ccf_hazard_runs': len(non_ccf_hazard_runs)
    },
    'token_comparison': token_comparison,
    'bigram_comparison': bigram_comparison,
    'vocabulary': {
        'ccf_types': len(ccf_types),
        'non_ccf_types': len(non_ccf_types),
        'overlap': len(overlap),
        'ccf_concentration': float(ccf_concentration),
        'non_ccf_concentration': float(non_ccf_concentration),
        'concentration_verdict': concentration_verdict
    },
    'verdicts': verdicts,
    'overall': overall,
    'interpretation': interpretation
}

with open('C:/git/voynich/ccf_curation_test.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n  Saved: ccf_curation_test.json")
print("=" * 70)
