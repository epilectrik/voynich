"""
06_section_paragraph_patterns.py - Do different sections organize paragraphs differently?

Tests paragraph count, size, cohesion, and first-paragraph patterns by section.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

def jaccard(set1, set2):
    if not set1 and not set2:
        return 0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load census
    with open(results_dir / 'folio_paragraph_census.json') as f:
        census = json.load(f)

    # Load paragraph tokens
    par_results = Path(__file__).resolve().parents[2] / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Load class map for HT identification
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    # Build per-paragraph data
    par_vocab = {}
    par_ht_rate = {}

    for folio_entry in census['folios']:
        for par_info in folio_entry['paragraphs']:
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])

            vocab = set()
            ht_count = 0
            total = 0

            for t in tokens:
                word = t['word']
                if not word or '*' in word:
                    continue
                total += 1
                vocab.add(word)

                if word not in class_map:
                    ht_count += 1

            par_vocab[par_id] = vocab
            par_ht_rate[par_id] = ht_count / total if total > 0 else 0

    print("=== SECTION-PARAGRAPH PATTERNS ===\n")

    # Group by section
    section_data = defaultdict(lambda: {
        'par_counts': [],
        'par_sizes': [],
        'cohesions': [],
        'par1_ht_rates': [],
        'later_ht_rates': []
    })

    for folio_entry in census['folios']:
        section = folio_entry['section']
        pars = folio_entry['paragraphs']

        section_data[section]['par_counts'].append(len(pars))

        for par_info in pars:
            section_data[section]['par_sizes'].append(par_info['tokens'])

        # Cohesion (intra-folio Jaccard)
        if len(pars) >= 2:
            par_ids = [p['par_id'] for p in pars]
            jaccards = []
            for i in range(len(par_ids)):
                for j in range(i + 1, len(par_ids)):
                    jaccards.append(jaccard(par_vocab[par_ids[i]], par_vocab[par_ids[j]]))
            if jaccards:
                section_data[section]['cohesions'].append(statistics.mean(jaccards))

            # First paragraph HT rate
            section_data[section]['par1_ht_rates'].append(par_ht_rate[par_ids[0]])
            for pid in par_ids[1:]:
                section_data[section]['later_ht_rates'].append(par_ht_rate[pid])

    # Report
    print("--- PARAGRAPH COUNT BY SECTION ---")
    print(f"{'Section':<12} {'Folios':>8} {'Mean':>8} {'Stdev':>8}")
    for section in sorted(section_data.keys()):
        counts = section_data[section]['par_counts']
        mean = statistics.mean(counts)
        stdev = statistics.stdev(counts) if len(counts) > 1 else 0
        print(f"{section:<12} {len(counts):>8} {mean:>8.1f} {stdev:>8.1f}")

    print(f"\n--- PARAGRAPH SIZE BY SECTION ---")
    print(f"{'Section':<12} {'Mean tokens':>12} {'Stdev':>8}")
    for section in sorted(section_data.keys()):
        sizes = section_data[section]['par_sizes']
        mean = statistics.mean(sizes)
        stdev = statistics.stdev(sizes) if len(sizes) > 1 else 0
        print(f"{section:<12} {mean:>12.1f} {stdev:>8.1f}")

    print(f"\n--- INTRA-FOLIO COHESION BY SECTION ---")
    print(f"{'Section':<12} {'Jaccard':>10}")
    for section in sorted(section_data.keys()):
        cohesions = section_data[section]['cohesions']
        if cohesions:
            print(f"{section:<12} {statistics.mean(cohesions):>10.3f}")

    print(f"\n--- FIRST PARAGRAPH HT RATE BY SECTION ---")
    print(f"{'Section':<12} {'Par 1 HT':>10} {'Later HT':>10} {'Ratio':>8}")
    for section in sorted(section_data.keys()):
        par1_rates = section_data[section]['par1_ht_rates']
        later_rates = section_data[section]['later_ht_rates']
        if par1_rates and later_rates:
            p1 = statistics.mean(par1_rates)
            lt = statistics.mean(later_rates)
            ratio = p1 / lt if lt > 0 else 0
            print(f"{section:<12} {p1:>10.1%} {lt:>10.1%} {ratio:>8.2f}x")

    # Find distinctive patterns
    print(f"\n--- SECTION-SPECIFIC PATTERNS ---")

    # Highest paragraph count
    section_par_means = {s: statistics.mean(d['par_counts']) for s, d in section_data.items()}
    max_par = max(section_par_means, key=section_par_means.get)
    min_par = min(section_par_means, key=section_par_means.get)
    print(f"Most paragraphs: {max_par} ({section_par_means[max_par]:.1f}/folio)")
    print(f"Fewest paragraphs: {min_par} ({section_par_means[min_par]:.1f}/folio)")

    # Highest cohesion
    section_cohesion_means = {s: statistics.mean(d['cohesions']) for s, d in section_data.items() if d['cohesions']}
    if section_cohesion_means:
        max_coh = max(section_cohesion_means, key=section_cohesion_means.get)
        min_coh = min(section_cohesion_means, key=section_cohesion_means.get)
        print(f"Highest cohesion: {max_coh} ({section_cohesion_means[max_coh]:.3f})")
        print(f"Lowest cohesion: {min_coh} ({section_cohesion_means[min_coh]:.3f})")

    # Save results
    output = {
        'sections': {}
    }

    for section, data in section_data.items():
        output['sections'][section] = {
            'folio_count': len(data['par_counts']),
            'par_count_mean': statistics.mean(data['par_counts']),
            'par_count_stdev': statistics.stdev(data['par_counts']) if len(data['par_counts']) > 1 else 0,
            'par_size_mean': statistics.mean(data['par_sizes']) if data['par_sizes'] else 0,
            'cohesion_mean': statistics.mean(data['cohesions']) if data['cohesions'] else 0,
            'par1_ht_rate': statistics.mean(data['par1_ht_rates']) if data['par1_ht_rates'] else 0,
            'later_ht_rate': statistics.mean(data['later_ht_rates']) if data['later_ht_rates'] else 0
        }

    with open(results_dir / 'section_patterns.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to section_patterns.json")

if __name__ == '__main__':
    main()
