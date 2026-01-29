"""
08_folio_template_test.py - Template model vs Parallel programs model

Template: Par 1 sets profile, later paragraphs are variations
Parallel: Paragraphs are independent programs sharing vocabulary pool
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Role classes
CC_CLASSES = {10, 11, 12, 17}
EN_CLASSES = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}
FL_CLASSES = {7, 30, 38, 40}
FQ_CLASSES = {9, 13, 14, 23}

def get_role(cls):
    if cls in CC_CLASSES: return 'CC'
    if cls in EN_CLASSES: return 'EN'
    if cls in FL_CLASSES: return 'FL'
    if cls in FQ_CLASSES: return 'FQ'
    return 'AX'

def pearson_corr(x, y):
    """Simple Pearson correlation."""
    n = len(x)
    if n < 3:
        return 0
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    std_x = (sum((xi - mean_x)**2 for xi in x) / n) ** 0.5
    std_y = (sum((yi - mean_y)**2 for yi in y) / n) ** 0.5
    if std_x == 0 or std_y == 0:
        return 0
    return cov / (n * std_x * std_y)

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load census
    with open(results_dir / 'folio_paragraph_census.json') as f:
        census = json.load(f)

    # Load paragraph tokens
    par_results = Path(__file__).resolve().parents[2] / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Load class map
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    # Build per-paragraph data
    par_vocab = {}
    par_roles = {}

    for folio_entry in census['folios']:
        for par_info in folio_entry['paragraphs']:
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])

            vocab = set()
            role_counts = Counter()
            total = 0

            for t in tokens:
                word = t['word']
                if not word or '*' in word:
                    continue
                total += 1
                vocab.add(word)

                if word in class_map:
                    role = get_role(class_map[word])
                    role_counts[role] += 1

            par_vocab[par_id] = vocab
            par_roles[par_id] = {r: role_counts[r]/total if total > 0 else 0
                                for r in ['EN', 'FL', 'FQ', 'CC', 'AX']}

    print("=== FOLIO TEMPLATE TEST ===\n")

    # Test 1: Vocabulary reuse rate
    # What fraction of Par 2+ tokens appeared in Par 1?
    vocab_reuse_rates = []

    for folio_entry in census['folios']:
        pars = folio_entry['paragraphs']
        if len(pars) < 2:
            continue

        par1_vocab = par_vocab[pars[0]['par_id']]

        for par_info in pars[1:]:
            later_vocab = par_vocab[par_info['par_id']]
            if later_vocab:
                reuse = len(par1_vocab & later_vocab) / len(later_vocab)
                vocab_reuse_rates.append(reuse)

    print("--- TEST 1: VOCABULARY REUSE FROM PAR 1 ---")
    print(f"Mean reuse rate: {statistics.mean(vocab_reuse_rates):.1%}")
    print(f"(Fraction of later paragraph vocab that appears in Par 1)")

    # Test 2: Role profile correlation
    # Does Par 1's role distribution predict later paragraphs?
    role_correlations = []

    for folio_entry in census['folios']:
        pars = folio_entry['paragraphs']
        if len(pars) < 3:
            continue

        par1_roles = par_roles[pars[0]['par_id']]
        par1_vec = [par1_roles.get(r, 0) for r in ['EN', 'FL', 'FQ', 'CC', 'AX']]

        # Average of later paragraphs
        later_vecs = []
        for par_info in pars[1:]:
            roles = par_roles[par_info['par_id']]
            later_vecs.append([roles.get(r, 0) for r in ['EN', 'FL', 'FQ', 'CC', 'AX']])

        if later_vecs:
            mean_later = [sum(v[i] for v in later_vecs) / len(later_vecs) for i in range(5)]
            corr = pearson_corr(par1_vec, mean_later)
            role_correlations.append(corr)

    print(f"\n--- TEST 2: ROLE PROFILE CORRELATION ---")
    print(f"Mean correlation (Par 1 vs mean of later): {statistics.mean(role_correlations):.3f}")

    # Test 3: Role stability (variance across paragraphs within folio)
    role_stabilities = []

    for folio_entry in census['folios']:
        pars = folio_entry['paragraphs']
        if len(pars) < 3:
            continue

        # Variance of each role across paragraphs
        role_variances = []
        for role in ['EN', 'FL', 'FQ', 'CC']:
            values = [par_roles[p['par_id']].get(role, 0) for p in pars]
            if len(values) > 1:
                role_variances.append(statistics.variance(values))

        if role_variances:
            role_stabilities.append(statistics.mean(role_variances))

    print(f"\n--- TEST 3: ROLE STABILITY ---")
    print(f"Mean role variance within folio: {statistics.mean(role_stabilities):.4f}")
    print(f"(Lower = more similar paragraphs)")

    # Test 4: Template score (vocabulary and role combined)
    print(f"\n--- TEMPLATE SCORE ---")

    vocab_score = statistics.mean(vocab_reuse_rates)
    role_score = (statistics.mean(role_correlations) + 1) / 2  # Normalize -1..1 to 0..1
    stability_score = 1 - min(statistics.mean(role_stabilities) * 10, 1)  # Invert, cap

    template_score = (vocab_score + role_score + stability_score) / 3

    print(f"Vocabulary reuse: {vocab_score:.3f}")
    print(f"Role correlation: {role_score:.3f}")
    print(f"Role stability: {stability_score:.3f}")
    print(f"Combined template score: {template_score:.3f}")

    # Verdict
    print(f"\n=== FINAL VERDICT ===")
    if template_score > 0.6:
        verdict = "TEMPLATE"
        print("TEMPLATE MODEL: Par 1 sets profile, later paragraphs are variations")
    elif template_score < 0.4:
        verdict = "PARALLEL"
        print("PARALLEL MODEL: Paragraphs are independent programs")
    else:
        verdict = "HYBRID"
        print("HYBRID MODEL: Partial template, partial independence")

    # Additional insight from probe data
    print(f"\n--- SUPPORTING EVIDENCE ---")
    print(f"From probe: 63-85% NEW vocabulary per paragraph (parallel indicator)")
    print(f"From probe: Role composition FLAT across sequence (parallel indicator)")
    print(f"From probe: Intra-folio similarity only 1.51x inter-folio (weak template)")

    # Save results
    output = {
        'tests': {
            'vocab_reuse': {
                'mean': statistics.mean(vocab_reuse_rates),
                'stdev': statistics.stdev(vocab_reuse_rates) if len(vocab_reuse_rates) > 1 else 0
            },
            'role_correlation': {
                'mean': statistics.mean(role_correlations),
                'stdev': statistics.stdev(role_correlations) if len(role_correlations) > 1 else 0
            },
            'role_stability': {
                'mean_variance': statistics.mean(role_stabilities)
            }
        },
        'scores': {
            'vocabulary': vocab_score,
            'role_correlation': role_score,
            'role_stability': stability_score,
            'combined': template_score
        },
        'verdict': verdict,
        'probe_evidence': {
            'new_vocab_per_par': '63-85%',
            'role_flatness': 'FLAT across sequence',
            'intra_inter_ratio': 1.51
        }
    }

    with open(results_dir / 'template_test.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to template_test.json")

if __name__ == '__main__':
    main()
