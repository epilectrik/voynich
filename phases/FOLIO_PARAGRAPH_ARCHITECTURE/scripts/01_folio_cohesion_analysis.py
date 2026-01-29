"""
01_folio_cohesion_analysis.py - What makes paragraphs on the same folio cohere?

Tests vocabulary, role, HT, and morphological cohesion sources.
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

def jaccard(set1, set2):
    if not set1 and not set2:
        return 0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0

def role_distance(r1, r2):
    """Euclidean distance between role distributions."""
    roles = ['EN', 'FL', 'FQ', 'CC', 'AX']
    return sum((r1.get(r, 0) - r2.get(r, 0))**2 for r in roles) ** 0.5

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

    # HT tokens = tokens NOT in class_map
    ht_tokens = set()
    for par_tokens in tokens_by_par.values():
        for t in par_tokens:
            word = t['word']
            if word and '*' not in word and word not in class_map:
                ht_tokens.add(word)

    # Build per-paragraph data
    par_vocab = {}
    par_roles = {}
    par_ht = {}
    par_prefixes = {}

    for folio_entry in census['folios']:
        for par_info in folio_entry['paragraphs']:
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])

            vocab = set()
            role_counts = Counter()
            ht_set = set()
            prefix_set = set()

            for t in tokens:
                word = t['word']
                if not word or '*' in word:
                    continue

                vocab.add(word)

                if word in class_map:
                    role = get_role(class_map[word])
                    role_counts[role] += 1
                else:
                    ht_set.add(word)
                    role_counts['HT'] = role_counts.get('HT', 0) + 1

                # Extract prefix (first 2 chars as proxy)
                if len(word) >= 2:
                    prefix_set.add(word[:2])

            par_vocab[par_id] = vocab
            par_ht[par_id] = ht_set
            par_prefixes[par_id] = prefix_set

            total = sum(role_counts.values())
            par_roles[par_id] = {r: role_counts[r]/total if total > 0 else 0
                                for r in ['EN', 'FL', 'FQ', 'CC', 'AX', 'HT']}

    # Analyze cohesion by folio
    print("=== FOLIO COHESION ANALYSIS ===\n")

    vocab_cohesion = []
    role_cohesion = []
    ht_cohesion = []
    prefix_cohesion = []

    for folio_entry in census['folios']:
        pars = folio_entry['paragraphs']
        if len(pars) < 2:
            continue

        par_ids = [p['par_id'] for p in pars]

        # Pairwise comparisons
        folio_vocab_sims = []
        folio_role_dists = []
        folio_ht_overlaps = []
        folio_prefix_sims = []

        for i in range(len(par_ids)):
            for j in range(i + 1, len(par_ids)):
                p1, p2 = par_ids[i], par_ids[j]

                # Vocabulary Jaccard
                folio_vocab_sims.append(jaccard(par_vocab[p1], par_vocab[p2]))

                # Role distance
                folio_role_dists.append(role_distance(par_roles[p1], par_roles[p2]))

                # HT overlap (absolute count)
                folio_ht_overlaps.append(len(par_ht[p1] & par_ht[p2]))

                # Prefix Jaccard
                folio_prefix_sims.append(jaccard(par_prefixes[p1], par_prefixes[p2]))

        if folio_vocab_sims:
            vocab_cohesion.append(statistics.mean(folio_vocab_sims))
            role_cohesion.append(statistics.mean(folio_role_dists))
            ht_cohesion.append(statistics.mean(folio_ht_overlaps))
            prefix_cohesion.append(statistics.mean(folio_prefix_sims))

    print("Mean intra-folio cohesion metrics:")
    print(f"  Vocabulary Jaccard: {statistics.mean(vocab_cohesion):.3f} (stdev {statistics.stdev(vocab_cohesion):.3f})")
    print(f"  Role distance: {statistics.mean(role_cohesion):.3f} (lower = more similar)")
    print(f"  Shared HT tokens: {statistics.mean(ht_cohesion):.1f}")
    print(f"  Prefix Jaccard: {statistics.mean(prefix_cohesion):.3f}")

    # Identify primary cohesion source
    print("\n=== PRIMARY COHESION SOURCE ===")
    # Normalize and compare
    # Vocab: 0-1, higher = more cohesive
    # Role: 0-~1.4, lower = more cohesive
    # HT: 0-N, higher = more cohesive
    # Prefix: 0-1, higher = more cohesive

    vocab_score = statistics.mean(vocab_cohesion)
    role_score = 1 - (statistics.mean(role_cohesion) / 1.4)  # Invert, normalize
    ht_score = min(statistics.mean(ht_cohesion) / 5, 1)  # Cap at 5
    prefix_score = statistics.mean(prefix_cohesion)

    print(f"  Vocabulary: {vocab_score:.3f}")
    print(f"  Role similarity: {role_score:.3f}")
    print(f"  HT overlap: {ht_score:.3f}")
    print(f"  Prefix overlap: {prefix_score:.3f}")

    # Rank
    sources = [('Vocabulary', vocab_score), ('Role', role_score),
               ('HT', ht_score), ('Prefix', prefix_score)]
    sources.sort(key=lambda x: x[1], reverse=True)

    print(f"\nRanked: {' > '.join(f'{s[0]}({s[1]:.3f})' for s in sources)}")
    print(f"Primary cohesion source: {sources[0][0]}")

    # Save results
    output = {
        'cohesion_metrics': {
            'vocab_jaccard_mean': statistics.mean(vocab_cohesion),
            'vocab_jaccard_stdev': statistics.stdev(vocab_cohesion),
            'role_distance_mean': statistics.mean(role_cohesion),
            'ht_overlap_mean': statistics.mean(ht_cohesion),
            'prefix_jaccard_mean': statistics.mean(prefix_cohesion)
        },
        'normalized_scores': {
            'vocabulary': vocab_score,
            'role_similarity': role_score,
            'ht_overlap': ht_score,
            'prefix_overlap': prefix_score
        },
        'primary_source': sources[0][0],
        'ranking': [s[0] for s in sources]
    }

    with open(results_dir / 'cohesion_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to cohesion_analysis.json")

if __name__ == '__main__':
    main()
