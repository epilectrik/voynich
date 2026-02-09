"""
01_vocabulary_survival.py - Test vocabulary survival across paragraphs

Phase: B_PARAGRAPH_POSITION_STRUCTURE
Test A: Within-folio vocabulary survival

Question: Do MIDDLEs survive from paragraph to paragraph, or does each paragraph draw fresh?

Method:
1. For each folio, extract MIDDLE vocabulary per paragraph
2. Compute survival rate: % of P1 vocabulary appearing in P2, P3, etc.
3. Also compute adjacent vs non-adjacent paragraph overlap

Null model: Hypergeometric - given folio vocabulary pool and paragraph sizes,
what survival rate would independent draws produce?

Expected from C856/C859: Weak survival, mostly independent draws
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology
import json
import csv
from collections import defaultdict
from pathlib import Path
from scipy import stats
import numpy as np

GALLOWS = {'k', 't', 'p', 'f'}

def has_gallows_initial(word):
    if not word or not word.strip():
        return False
    return word[0] in GALLOWS

def load_raw_data():
    """Load raw transcript with placement info."""
    data_path = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
    folio_lines = defaultdict(lambda: defaultdict(list))

    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row['transcriber'] == 'H' and row['language'] == 'B':
                folio = row['folio']
                line = row['line_number']
                word = row['word']
                if '*' in word:
                    continue
                folio_lines[folio][line].append(word)

    return folio_lines

def detect_paragraphs(folio_data):
    """Detect paragraphs using gallows-initial heuristic."""
    paragraphs = defaultdict(list)
    lines = sorted(folio_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))

    current_para = 1
    for i, line in enumerate(lines):
        tokens = folio_data[line]
        if not tokens:
            continue

        first_word = tokens[0]
        if i > 0 and has_gallows_initial(first_word):
            current_para += 1

        paragraphs[current_para].extend(tokens)

    return paragraphs

def extract_middles(tokens, morph):
    """Extract MIDDLEs from token list."""
    middles = set()
    for token in tokens:
        m = morph.extract(token)
        if m and m.middle:
            middles.add(m.middle)
    return middles

def compute_survival_rate(vocab1, vocab2):
    """Compute what fraction of vocab1 appears in vocab2."""
    if not vocab1:
        return 0.0
    return len(vocab1 & vocab2) / len(vocab1)

def compute_jaccard(vocab1, vocab2):
    """Compute Jaccard similarity."""
    if not vocab1 and not vocab2:
        return 0.0
    union = vocab1 | vocab2
    if not union:
        return 0.0
    return len(vocab1 & vocab2) / len(union)

def hypergeometric_expected(folio_vocab_size, para1_size, para2_size):
    """
    Expected overlap under hypergeometric null model.

    If two paragraphs independently draw from the same vocabulary pool,
    what overlap would we expect by chance?
    """
    if folio_vocab_size == 0 or para1_size == 0 or para2_size == 0:
        return 0.0

    # Expected number of shared items when drawing para1_size and para2_size
    # from a pool of folio_vocab_size items
    # E[overlap] = para1_size * para2_size / folio_vocab_size
    expected = para1_size * para2_size / folio_vocab_size
    return expected

def main():
    folio_data = load_raw_data()
    morph = Morphology()

    results = {
        'folios_analyzed': 0,
        'folio_results': [],
        'aggregate': {
            'mean_survival_p1_to_p2': [],
            'mean_jaccard_adjacent': [],
            'mean_jaccard_nonadjacent': [],
            'expected_vs_observed': [],
        }
    }

    all_adjacent_jaccards = []
    all_nonadjacent_jaccards = []
    all_survival_rates = []
    all_expected_overlaps = []
    all_observed_overlaps = []

    for folio in sorted(folio_data.keys()):
        paragraphs = detect_paragraphs(folio_data[folio])

        # Need at least 2 paragraphs for comparison
        if len(paragraphs) < 2:
            continue

        results['folios_analyzed'] += 1

        # Extract MIDDLEs per paragraph
        para_vocabs = {}
        para_nums = sorted(paragraphs.keys())

        for pnum in para_nums:
            tokens = paragraphs[pnum]
            middles = extract_middles(tokens, morph)
            para_vocabs[pnum] = middles

        # Compute folio-level vocabulary
        folio_vocab = set()
        for v in para_vocabs.values():
            folio_vocab |= v

        folio_result = {
            'folio': folio,
            'paragraph_count': len(paragraphs),
            'folio_vocab_size': len(folio_vocab),
            'paragraphs': [],
            'survival': {},
            'jaccard_adjacent': [],
            'jaccard_nonadjacent': []
        }

        for pnum in para_nums:
            folio_result['paragraphs'].append({
                'number': pnum,
                'tokens': len(paragraphs[pnum]),
                'unique_middles': len(para_vocabs[pnum])
            })

        # Compute survival from P1 to each subsequent paragraph
        if 1 in para_vocabs:
            p1_vocab = para_vocabs[1]
            for pnum in para_nums:
                if pnum > 1:
                    survival = compute_survival_rate(p1_vocab, para_vocabs[pnum])
                    folio_result['survival'][f'P1_to_P{pnum}'] = survival
                    all_survival_rates.append(survival)

        # Compute pairwise Jaccard (adjacent vs non-adjacent)
        for i, pnum1 in enumerate(para_nums):
            for j, pnum2 in enumerate(para_nums):
                if pnum2 <= pnum1:
                    continue

                jaccard = compute_jaccard(para_vocabs[pnum1], para_vocabs[pnum2])

                # Expected under hypergeometric null
                expected = hypergeometric_expected(
                    len(folio_vocab),
                    len(para_vocabs[pnum1]),
                    len(para_vocabs[pnum2])
                )
                observed = len(para_vocabs[pnum1] & para_vocabs[pnum2])

                all_expected_overlaps.append(expected)
                all_observed_overlaps.append(observed)

                # Adjacent = consecutive paragraph numbers
                if pnum2 == pnum1 + 1:
                    folio_result['jaccard_adjacent'].append({
                        'pair': f'P{pnum1}_P{pnum2}',
                        'jaccard': jaccard
                    })
                    all_adjacent_jaccards.append(jaccard)
                else:
                    folio_result['jaccard_nonadjacent'].append({
                        'pair': f'P{pnum1}_P{pnum2}',
                        'jaccard': jaccard
                    })
                    all_nonadjacent_jaccards.append(jaccard)

        results['folio_results'].append(folio_result)

    # Aggregate statistics
    results['aggregate'] = {
        'folios_analyzed': results['folios_analyzed'],
        'mean_survival_p1_onward': np.mean(all_survival_rates) if all_survival_rates else 0,
        'std_survival': np.std(all_survival_rates) if all_survival_rates else 0,
        'mean_jaccard_adjacent': np.mean(all_adjacent_jaccards) if all_adjacent_jaccards else 0,
        'std_jaccard_adjacent': np.std(all_adjacent_jaccards) if all_adjacent_jaccards else 0,
        'mean_jaccard_nonadjacent': np.mean(all_nonadjacent_jaccards) if all_nonadjacent_jaccards else 0,
        'std_jaccard_nonadjacent': np.std(all_nonadjacent_jaccards) if all_nonadjacent_jaccards else 0,
        'mean_expected_overlap': np.mean(all_expected_overlaps) if all_expected_overlaps else 0,
        'mean_observed_overlap': np.mean(all_observed_overlaps) if all_observed_overlaps else 0,
    }

    # Test: Is adjacent Jaccard higher than non-adjacent?
    if all_adjacent_jaccards and all_nonadjacent_jaccards:
        tstat, pval = stats.ttest_ind(all_adjacent_jaccards, all_nonadjacent_jaccards)
        results['aggregate']['adjacent_vs_nonadjacent_ttest'] = {
            't_statistic': tstat,
            'p_value': pval,
            'adjacent_higher': np.mean(all_adjacent_jaccards) > np.mean(all_nonadjacent_jaccards)
        }

    # Test: Is observed overlap higher than expected?
    if all_expected_overlaps and all_observed_overlaps:
        # Paired t-test (same pairs)
        tstat, pval = stats.ttest_rel(all_observed_overlaps, all_expected_overlaps)
        results['aggregate']['observed_vs_expected_ttest'] = {
            't_statistic': tstat,
            'p_value': pval,
            'observed_higher': np.mean(all_observed_overlaps) > np.mean(all_expected_overlaps)
        }

    # Print results
    print("=" * 70)
    print("TEST A: VOCABULARY SURVIVAL ACROSS PARAGRAPHS")
    print("=" * 70)

    print(f"\nFolios analyzed: {results['folios_analyzed']}")

    print(f"\n--- Survival from P1 ---")
    print(f"Mean P1 vocabulary survival rate: {results['aggregate']['mean_survival_p1_onward']:.3f}")
    print(f"Std: {results['aggregate']['std_survival']:.3f}")

    print(f"\n--- Jaccard Similarity ---")
    print(f"Adjacent paragraphs:     {results['aggregate']['mean_jaccard_adjacent']:.3f} (sd={results['aggregate']['std_jaccard_adjacent']:.3f})")
    print(f"Non-adjacent paragraphs: {results['aggregate']['mean_jaccard_nonadjacent']:.3f} (sd={results['aggregate']['std_jaccard_nonadjacent']:.3f})")

    if 'adjacent_vs_nonadjacent_ttest' in results['aggregate']:
        test = results['aggregate']['adjacent_vs_nonadjacent_ttest']
        print(f"\nAdjacent vs Non-adjacent t-test:")
        print(f"  t = {test['t_statistic']:.3f}, p = {test['p_value']:.4f}")
        print(f"  Adjacent higher: {test['adjacent_higher']}")

    print(f"\n--- Null Model Comparison ---")
    print(f"Mean expected overlap (hypergeometric): {results['aggregate']['mean_expected_overlap']:.2f}")
    print(f"Mean observed overlap:                  {results['aggregate']['mean_observed_overlap']:.2f}")

    if 'observed_vs_expected_ttest' in results['aggregate']:
        test = results['aggregate']['observed_vs_expected_ttest']
        print(f"\nObserved vs Expected t-test:")
        print(f"  t = {test['t_statistic']:.3f}, p = {test['p_value']:.4f}")
        print(f"  Observed higher: {test['observed_higher']}")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    survival = results['aggregate']['mean_survival_p1_onward']
    adj_jacc = results['aggregate']['mean_jaccard_adjacent']
    nonadj_jacc = results['aggregate']['mean_jaccard_nonadjacent']

    if survival < 0.3:
        print(f"\nWEAK SURVIVAL ({survival:.1%}): Paragraphs draw mostly fresh vocabulary.")
        print("  Consistent with C855 (PARALLEL_PROGRAMS) - independent mini-programs.")
    elif survival < 0.5:
        print(f"\nMODERATE SURVIVAL ({survival:.1%}): Some vocabulary persistence.")
        print("  Suggests partial continuity, but not strong sequential dependence.")
    else:
        print(f"\nSTRONG SURVIVAL ({survival:.1%}): Significant vocabulary persistence.")
        print("  Would challenge C855 - suggests sequential rather than parallel.")

    if adj_jacc > nonadj_jacc + 0.05:
        print(f"\nADJACENT PARAGRAPHS MORE SIMILAR: May indicate sequential processing.")
    else:
        print(f"\nNO ADJACENCY EFFECT: Similarity independent of paragraph distance.")

    # Save results
    output_path = Path('C:/git/voynich/phases/B_PARAGRAPH_POSITION_STRUCTURE/results/01_vocabulary_survival.json')

    # Clean for JSON serialization
    def clean_for_json(obj):
        if isinstance(obj, (np.floating, np.integer)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_for_json(i) for i in obj]
        return obj

    clean_results = {
        'summary': {
            'folios_analyzed': results['folios_analyzed'],
            'mean_survival': float(results['aggregate']['mean_survival_p1_onward']),
            'mean_jaccard_adjacent': float(results['aggregate']['mean_jaccard_adjacent']),
            'mean_jaccard_nonadjacent': float(results['aggregate']['mean_jaccard_nonadjacent']),
            'interpretation': 'weak' if survival < 0.3 else ('moderate' if survival < 0.5 else 'strong')
        },
        'aggregate': clean_for_json(results['aggregate']),
        'folio_sample': clean_for_json(results['folio_results'][:5])  # Just first 5 for size
    }

    with open(output_path, 'w') as f:
        json.dump(clean_results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results

if __name__ == '__main__':
    main()
