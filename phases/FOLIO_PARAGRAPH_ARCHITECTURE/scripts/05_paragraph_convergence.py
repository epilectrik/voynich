"""
05_paragraph_convergence.py - Do later paragraphs converge or diverge?

Tests whether vocabulary overlap and role similarity increase or decrease
across paragraph sequence.
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

    print("=== PARAGRAPH CONVERGENCE/DIVERGENCE ANALYSIS ===\n")

    # Track similarity by ordinal pair distance
    sim_by_distance = defaultdict(list)  # distance -> [jaccard values]
    role_by_distance = defaultdict(list)  # distance -> [role distances]

    # Last paragraph analysis
    last_vs_others_vocab = []
    last_vs_others_role = []

    for folio_entry in census['folios']:
        pars = folio_entry['paragraphs']
        if len(pars) < 3:
            continue

        par_ids = [p['par_id'] for p in pars]

        # Pairwise by distance
        for i in range(len(par_ids)):
            for j in range(i + 1, len(par_ids)):
                distance = j - i
                sim = jaccard(par_vocab[par_ids[i]], par_vocab[par_ids[j]])
                role_dist = role_distance(par_roles[par_ids[i]], par_roles[par_ids[j]])

                if distance <= 5:  # Cap for meaningful analysis
                    sim_by_distance[distance].append(sim)
                    role_by_distance[distance].append(role_dist)

        # Last paragraph vs others
        last_id = par_ids[-1]
        for pid in par_ids[:-1]:
            last_vs_others_vocab.append(jaccard(par_vocab[last_id], par_vocab[pid]))
            last_vs_others_role.append(role_distance(par_roles[last_id], par_roles[pid]))

    print("--- VOCABULARY SIMILARITY BY PAIR DISTANCE ---")
    for dist in sorted(sim_by_distance.keys()):
        sims = sim_by_distance[dist]
        print(f"  Distance {dist}: Jaccard = {statistics.mean(sims):.3f} (n={len(sims)})")

    # Trend analysis
    distances = sorted(sim_by_distance.keys())
    means = [statistics.mean(sim_by_distance[d]) for d in distances]
    if len(means) >= 2:
        trend = means[-1] - means[0]
        if trend > 0.01:
            vocab_trend = "INCREASING (convergent)"
        elif trend < -0.01:
            vocab_trend = "DECREASING (divergent)"
        else:
            vocab_trend = "FLAT (no trend)"
        print(f"\nVocabulary trend: {vocab_trend}")

    print(f"\n--- ROLE DISTANCE BY PAIR DISTANCE ---")
    for dist in sorted(role_by_distance.keys()):
        dists = role_by_distance[dist]
        print(f"  Distance {dist}: Role distance = {statistics.mean(dists):.3f}")

    role_means = [statistics.mean(role_by_distance[d]) for d in distances]
    if len(role_means) >= 2:
        role_trend = role_means[-1] - role_means[0]
        if role_trend > 0.01:
            role_trend_str = "INCREASING (divergent)"
        elif role_trend < -0.01:
            role_trend_str = "DECREASING (convergent)"
        else:
            role_trend_str = "FLAT (no trend)"
        print(f"\nRole distance trend: {role_trend_str}")

    # Last paragraph distinctiveness
    print(f"\n--- LAST PARAGRAPH DISTINCTIVENESS ---")
    # Compare last-vs-others to any-pair-vs-any
    all_vocab_sims = [s for sims in sim_by_distance.values() for s in sims]
    print(f"Last vs others (vocab): {statistics.mean(last_vs_others_vocab):.3f}")
    print(f"General pairs (vocab): {statistics.mean(all_vocab_sims):.3f}")

    last_distinct = statistics.mean(last_vs_others_vocab) < statistics.mean(all_vocab_sims) * 0.9
    if last_distinct:
        print("--> Last paragraph IS DISTINCT")
    else:
        print("--> Last paragraph is NOT distinct")

    # Cumulative overlap analysis
    print(f"\n--- CUMULATIVE VOCABULARY OVERLAP ---")
    cumulative_overlaps = defaultdict(list)

    for folio_entry in census['folios']:
        pars = folio_entry['paragraphs']
        if len(pars) < 4:
            continue

        par_ids = [p['par_id'] for p in pars]
        cumulative_vocab = set()

        for i, pid in enumerate(par_ids):
            if i > 0:
                # What fraction of this paragraph's vocab was seen before?
                current_vocab = par_vocab[pid]
                if current_vocab:
                    overlap = len(current_vocab & cumulative_vocab) / len(current_vocab)
                    ordinal = min(i + 1, 8)
                    cumulative_overlaps[ordinal].append(overlap)
            cumulative_vocab |= par_vocab[pid]

    for ordinal in sorted(cumulative_overlaps.keys()):
        overlaps = cumulative_overlaps[ordinal]
        print(f"  Par {ordinal}: {statistics.mean(overlaps):.1%} overlap with prior")

    # Verdict
    print(f"\n--- CONVERGENCE VERDICT ---")
    cumulative_means = [statistics.mean(cumulative_overlaps[o]) for o in sorted(cumulative_overlaps.keys())]
    if len(cumulative_means) >= 2:
        cumulative_trend = cumulative_means[-1] - cumulative_means[0]
        if cumulative_trend > 0.1:
            print("Paragraphs CONVERGE: later paragraphs reuse more vocabulary")
            verdict = "CONVERGENT"
        elif cumulative_trend < -0.1:
            print("Paragraphs DIVERGE: later paragraphs introduce more new vocabulary")
            verdict = "DIVERGENT"
        else:
            print("Paragraphs STABLE: consistent overlap rate across sequence")
            verdict = "STABLE"
    else:
        verdict = "INSUFFICIENT_DATA"
        print("Insufficient data for trend analysis")

    # Save results
    output = {
        'vocab_similarity_by_distance': {d: statistics.mean(s) for d, s in sim_by_distance.items()},
        'role_distance_by_ordinal': {d: statistics.mean(s) for d, s in role_by_distance.items()},
        'cumulative_overlap_by_ordinal': {o: statistics.mean(c) for o, c in cumulative_overlaps.items()},
        'last_paragraph_distinct': last_distinct,
        'verdict': verdict
    }

    with open(results_dir / 'convergence_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to convergence_analysis.json")

if __name__ == '__main__':
    main()
