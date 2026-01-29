"""
03_first_paragraph_role.py - Is paragraph 1 a "setup" that later paragraphs build on?

Tests HT rate, unique vocabulary, predictivity for Par 1 vs later.
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

    # Build per-paragraph metrics
    par_metrics = {}
    for folio_entry in census['folios']:
        for par_info in folio_entry['paragraphs']:
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])

            vocab = set()
            role_counts = Counter()
            ht_count = 0
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
                else:
                    ht_count += 1

            par_metrics[par_id] = {
                'vocab': vocab,
                'ht_rate': ht_count / total if total > 0 else 0,
                'roles': {r: role_counts[r]/total if total > 0 else 0
                         for r in ['EN', 'FL', 'FQ', 'CC', 'AX']},
                'total': total
            }

    print("=== FIRST PARAGRAPH ROLE ANALYSIS ===\n")

    # Compare Par 1 vs later
    par1_ht_rates = []
    later_ht_rates = []
    par1_vocab_sizes = []
    later_vocab_sizes = []
    par1_roles = defaultdict(list)
    later_roles = defaultdict(list)

    # Vocabulary predictivity: how much of Par 2+ vocab appears in Par 1?
    vocab_predictivity = []

    for folio_entry in census['folios']:
        pars = folio_entry['paragraphs']
        if len(pars) < 2:
            continue

        par1_id = pars[0]['par_id']
        par1_m = par_metrics[par1_id]

        par1_ht_rates.append(par1_m['ht_rate'])
        par1_vocab_sizes.append(len(par1_m['vocab']))
        for role, rate in par1_m['roles'].items():
            par1_roles[role].append(rate)

        # Later paragraphs
        later_vocab_union = set()
        for par_info in pars[1:]:
            pid = par_info['par_id']
            m = par_metrics[pid]
            later_ht_rates.append(m['ht_rate'])
            later_vocab_sizes.append(len(m['vocab']))
            for role, rate in m['roles'].items():
                later_roles[role].append(rate)
            later_vocab_union |= m['vocab']

        # What fraction of later vocab was in Par 1?
        if later_vocab_union:
            overlap = len(par1_m['vocab'] & later_vocab_union) / len(later_vocab_union)
            vocab_predictivity.append(overlap)

    print("--- HT RATE ---")
    print(f"Par 1: {statistics.mean(par1_ht_rates):.1%}")
    print(f"Later: {statistics.mean(later_ht_rates):.1%}")
    ht_ratio = statistics.mean(par1_ht_rates) / statistics.mean(later_ht_rates) if later_ht_rates else 0
    print(f"Ratio: {ht_ratio:.2f}x")

    print(f"\n--- VOCABULARY SIZE ---")
    print(f"Par 1 mean: {statistics.mean(par1_vocab_sizes):.1f} unique words")
    print(f"Later mean: {statistics.mean(later_vocab_sizes):.1f} unique words")

    print(f"\n--- ROLE DISTRIBUTION ---")
    print(f"{'Role':<6} {'Par 1':>8} {'Later':>8} {'Delta':>8}")
    for role in ['EN', 'FL', 'FQ', 'CC', 'AX']:
        p1 = statistics.mean(par1_roles[role])
        lt = statistics.mean(later_roles[role])
        delta = p1 - lt
        sign = '+' if delta > 0 else ''
        print(f"{role:<6} {p1:>8.1%} {lt:>8.1%} {sign}{delta:>7.1%}")

    print(f"\n--- VOCABULARY PREDICTIVITY ---")
    print(f"Par 1 predicts {statistics.mean(vocab_predictivity):.1%} of later paragraph vocab")

    # Verdict
    print(f"\n--- FIRST PARAGRAPH VERDICT ---")
    ht_elevated = ht_ratio > 1.2
    vocab_predictive = statistics.mean(vocab_predictivity) > 0.3
    role_different = any(abs(statistics.mean(par1_roles[r]) - statistics.mean(later_roles[r])) > 0.05
                        for r in ['EN', 'FL', 'FQ', 'CC'])

    if ht_elevated and vocab_predictive:
        print("Par 1 is STRUCTURALLY DISTINCT: elevated HT, predictive vocabulary")
        verdict = "DISTINCT_TEMPLATE"
    elif ht_elevated:
        print("Par 1 has ELEVATED HT but low vocabulary predictivity")
        verdict = "HEADER_ONLY"
    elif vocab_predictive:
        print("Par 1 VOCABULARY predicts later, but no HT elevation")
        verdict = "VOCAB_TEMPLATE"
    else:
        print("Par 1 is NOT structurally distinct from later paragraphs")
        verdict = "ORDINARY"

    # Save results
    output = {
        'ht_rate': {
            'par1_mean': statistics.mean(par1_ht_rates),
            'later_mean': statistics.mean(later_ht_rates),
            'ratio': ht_ratio
        },
        'vocab_size': {
            'par1_mean': statistics.mean(par1_vocab_sizes),
            'later_mean': statistics.mean(later_vocab_sizes)
        },
        'role_comparison': {
            role: {
                'par1': statistics.mean(par1_roles[role]),
                'later': statistics.mean(later_roles[role])
            } for role in ['EN', 'FL', 'FQ', 'CC', 'AX']
        },
        'vocab_predictivity': statistics.mean(vocab_predictivity),
        'verdict': verdict
    }

    with open(results_dir / 'first_paragraph_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to first_paragraph_analysis.json")

if __name__ == '__main__':
    main()
