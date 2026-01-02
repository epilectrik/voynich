#!/usr/bin/env python3
"""
Prefix Role Analysis Within Entries

Analyze prefix behavior as structural markers, NOT semantic labels:
1. Positional Analysis - where prefixes appear within entries
2. Co-occurrence Analysis - which prefixes appear together
3. Sequential Patterns - common prefix sequences
4. Entry-Type Association - which prefixes correlate with entry characteristics
5. Structural Role Hypotheses - proposed functional roles

Uses folio-based entry segmentation from previous analyses.
"""

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Set, Any
from itertools import combinations


# Known prefixes from previous analysis
KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo'
]


def load_corpus() -> Tuple[List[Dict], Dict[str, List[Dict]]]:
    """Load corpus with line-level structure."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'

    all_words = []
    by_currier = {'A': [], 'B': []}

    seen = set()
    word_idx = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip().strip('"')
            folio = row.get('folio', '').strip().strip('"')
            line_num = row.get('line_number', '').strip().strip('"')
            currier = row.get('language', '').strip().strip('"')

            if not word or word.startswith('*') or len(word) < 2:
                continue

            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                entry = {
                    'word': word,
                    'folio': folio,
                    'line': line_num,
                    'currier': currier,
                    'idx': word_idx
                }
                all_words.append(entry)
                if currier in by_currier:
                    by_currier[currier].append(entry)
                word_idx += 1

    return all_words, by_currier


def get_prefix(word: str) -> str:
    """Extract prefix from word."""
    for length in [3, 2]:
        if len(word) >= length:
            prefix = word[:length]
            if prefix in KNOWN_PREFIXES:
                return prefix
    if len(word) >= 2:
        return word[:2]
    return word


def segment_into_entries(words: List[Dict]) -> List[List[Dict]]:
    """Segment corpus into entries using folio boundaries."""
    by_folio = defaultdict(list)
    for w in words:
        by_folio[w['folio']].append(w)

    entries = []
    for folio in sorted(by_folio.keys()):
        entries.append(by_folio[folio])

    return entries


# ============================================================================
# ANALYSIS 1: POSITIONAL ANALYSIS
# ============================================================================

def analyze_positional_distribution(entries: List[List[Dict]]) -> Dict:
    """
    For each prefix, calculate its distribution across entry positions.
    Position = (word position within entry) / (entry length)
    """
    print("  Analyzing positional distributions...")

    # Track positions for each prefix
    prefix_positions = defaultdict(list)

    for entry in entries:
        n = len(entry)
        if n < 5:
            continue

        for i, w in enumerate(entry):
            prefix = get_prefix(w['word'])
            normalized_pos = i / (n - 1) if n > 1 else 0.5
            prefix_positions[prefix].append(normalized_pos)

    # Calculate statistics for each prefix
    position_stats = []

    for prefix, positions in prefix_positions.items():
        if len(positions) < 20:  # Minimum count for reliable stats
            continue

        mean_pos = sum(positions) / len(positions)
        variance = sum((p - mean_pos) ** 2 for p in positions) / len(positions)
        std_pos = math.sqrt(variance)

        # Calculate quintile distribution
        quintiles = [0, 0, 0, 0, 0]  # 0-0.2, 0.2-0.4, 0.4-0.6, 0.6-0.8, 0.8-1.0
        for p in positions:
            bucket = min(int(p * 5), 4)
            quintiles[bucket] += 1

        # Normalize to percentages
        total = sum(quintiles)
        quintile_pcts = [round(q / total * 100, 1) for q in quintiles]

        # Determine position type
        if quintile_pcts[0] > 25:  # >25% in first quintile
            position_type = 'INITIAL_TENDENCY'
        elif quintile_pcts[4] > 25:  # >25% in last quintile
            position_type = 'FINAL_TENDENCY'
        elif max(quintile_pcts) - min(quintile_pcts) < 10:
            position_type = 'UNIFORM'
        else:
            position_type = 'MIXED'

        position_stats.append({
            'prefix': prefix,
            'count': len(positions),
            'mean_position': round(mean_pos, 3),
            'std_position': round(std_pos, 3),
            'quintiles': quintile_pcts,
            'position_type': position_type
        })

    # Sort by position type then mean position
    position_stats.sort(key=lambda x: (x['position_type'], x['mean_position']))

    # Categorize
    initial_prefixes = [p for p in position_stats if p['position_type'] == 'INITIAL_TENDENCY']
    final_prefixes = [p for p in position_stats if p['position_type'] == 'FINAL_TENDENCY']
    uniform_prefixes = [p for p in position_stats if p['position_type'] == 'UNIFORM']

    return {
        'all_stats': position_stats,
        'initial_prefixes': initial_prefixes,
        'final_prefixes': final_prefixes,
        'uniform_prefixes': uniform_prefixes,
        'count_by_type': {
            'INITIAL_TENDENCY': len(initial_prefixes),
            'FINAL_TENDENCY': len(final_prefixes),
            'UNIFORM': len(uniform_prefixes),
            'MIXED': len([p for p in position_stats if p['position_type'] == 'MIXED'])
        }
    }


# ============================================================================
# ANALYSIS 2: CO-OCCURRENCE ANALYSIS
# ============================================================================

def analyze_cooccurrence(entries: List[List[Dict]]) -> Dict:
    """
    Build prefix x prefix co-occurrence matrix.
    Which prefixes appear together within the same entry?
    """
    print("  Analyzing co-occurrence patterns...")

    # Count co-occurrences
    cooccur_counts = Counter()
    prefix_counts = Counter()

    for entry in entries:
        if len(entry) < 3:
            continue

        # Get unique prefixes in this entry
        entry_prefixes = set(get_prefix(w['word']) for w in entry)

        for prefix in entry_prefixes:
            prefix_counts[prefix] += 1

        # Count pairs
        for p1, p2 in combinations(sorted(entry_prefixes), 2):
            cooccur_counts[(p1, p2)] += 1

    total_entries = len(entries)

    # Calculate PMI (Pointwise Mutual Information) for top pairs
    pmi_scores = []
    for (p1, p2), co_count in cooccur_counts.items():
        if co_count < 5:
            continue

        # P(p1, p2) = co_count / total_entries
        # P(p1) = prefix_counts[p1] / total_entries
        # P(p2) = prefix_counts[p2] / total_entries
        # PMI = log2(P(p1,p2) / (P(p1) * P(p2)))

        p_joint = co_count / total_entries
        p_p1 = prefix_counts[p1] / total_entries
        p_p2 = prefix_counts[p2] / total_entries

        if p_p1 > 0 and p_p2 > 0:
            pmi = math.log2(p_joint / (p_p1 * p_p2))
        else:
            pmi = 0

        pmi_scores.append({
            'pair': (p1, p2),
            'co_count': co_count,
            'p1_count': prefix_counts[p1],
            'p2_count': prefix_counts[p2],
            'pmi': round(pmi, 3)
        })

    # Sort by PMI
    pmi_scores.sort(key=lambda x: -x['pmi'])

    # High PMI = strong positive association
    positive_associations = [p for p in pmi_scores if p['pmi'] > 0.5][:20]

    # Low PMI = repulsion (rarely co-occur)
    negative_associations = sorted(pmi_scores, key=lambda x: x['pmi'])[:20]

    # Most frequently co-occurring pairs
    top_cooccur = cooccur_counts.most_common(30)

    return {
        'positive_associations': positive_associations,
        'negative_associations': negative_associations,
        'top_cooccurring_pairs': top_cooccur,
        'prefix_entry_counts': dict(prefix_counts.most_common(30)),
        'total_entries_analyzed': total_entries
    }


# ============================================================================
# ANALYSIS 3: SEQUENTIAL PATTERNS
# ============================================================================

def analyze_sequential_patterns(entries: List[List[Dict]]) -> Dict:
    """
    What prefix sequences are common within entries?
    Are there typical progressions?
    """
    print("  Analyzing sequential patterns...")

    # Count prefix bigrams
    prefix_bigrams = Counter()
    prefix_trigrams = Counter()

    for entry in entries:
        if len(entry) < 3:
            continue

        prefixes = [get_prefix(w['word']) for w in entry]

        # Bigrams
        for i in range(len(prefixes) - 1):
            bigram = (prefixes[i], prefixes[i + 1])
            prefix_bigrams[bigram] += 1

        # Trigrams
        for i in range(len(prefixes) - 2):
            trigram = (prefixes[i], prefixes[i + 1], prefixes[i + 2])
            prefix_trigrams[trigram] += 1

    # Calculate transition probabilities
    prefix_totals = Counter()
    for (p1, p2), count in prefix_bigrams.items():
        prefix_totals[p1] += count

    transition_probs = []
    for (p1, p2), count in prefix_bigrams.most_common(100):
        if prefix_totals[p1] > 0:
            prob = count / prefix_totals[p1]
            transition_probs.append({
                'from': p1,
                'to': p2,
                'count': count,
                'probability': round(prob, 3)
            })

    # Find strong transitions (high probability)
    strong_transitions = [t for t in transition_probs if t['probability'] > 0.1 and t['count'] >= 10]
    strong_transitions.sort(key=lambda x: -x['probability'])

    # Most common entry-opening sequences (first 3 prefixes)
    opening_sequences = Counter()
    for entry in entries:
        if len(entry) >= 3:
            seq = tuple(get_prefix(w['word']) for w in entry[:3])
            opening_sequences[seq] += 1

    # Most common entry-closing sequences (last 3 prefixes)
    closing_sequences = Counter()
    for entry in entries:
        if len(entry) >= 3:
            seq = tuple(get_prefix(w['word']) for w in entry[-3:])
            closing_sequences[seq] += 1

    return {
        'top_bigrams': prefix_bigrams.most_common(30),
        'top_trigrams': prefix_trigrams.most_common(30),
        'strong_transitions': strong_transitions[:20],
        'top_opening_sequences': opening_sequences.most_common(20),
        'top_closing_sequences': closing_sequences.most_common(20)
    }


# ============================================================================
# ANALYSIS 4: ENTRY-TYPE ASSOCIATION
# ============================================================================

def analyze_entry_type_association(entries: List[List[Dict]]) -> Dict:
    """
    Which prefixes associate with which entry characteristics?
    """
    print("  Analyzing entry-type associations...")

    # Categorize entries by length
    short_entries = []  # < 100 words
    medium_entries = []  # 100-250 words
    long_entries = []  # > 250 words

    for entry in entries:
        if len(entry) < 100:
            short_entries.append(entry)
        elif len(entry) < 250:
            medium_entries.append(entry)
        else:
            long_entries.append(entry)

    # Count prefix frequencies in each category
    def get_prefix_rates(entry_list):
        all_prefixes = []
        for entry in entry_list:
            all_prefixes.extend(get_prefix(w['word']) for w in entry)
        total = len(all_prefixes)
        counts = Counter(all_prefixes)
        return {p: round(c / total * 100, 2) for p, c in counts.most_common(30)}

    short_rates = get_prefix_rates(short_entries) if short_entries else {}
    medium_rates = get_prefix_rates(medium_entries) if medium_entries else {}
    long_rates = get_prefix_rates(long_entries) if long_entries else {}

    # Find prefixes enriched in each category
    all_prefixes = set(short_rates.keys()) | set(medium_rates.keys()) | set(long_rates.keys())

    short_enriched = []
    long_enriched = []

    for prefix in all_prefixes:
        short_rate = short_rates.get(prefix, 0)
        medium_rate = medium_rates.get(prefix, 0.01)
        long_rate = long_rates.get(prefix, 0)

        if short_rate > medium_rate * 1.5:
            short_enriched.append({'prefix': prefix, 'short_rate': short_rate, 'medium_rate': medium_rate})
        if long_rate > medium_rate * 1.5:
            long_enriched.append({'prefix': prefix, 'long_rate': long_rate, 'medium_rate': medium_rate})

    short_enriched.sort(key=lambda x: -x['short_rate'])
    long_enriched.sort(key=lambda x: -x['long_rate'])

    return {
        'entry_count_by_length': {
            'short': len(short_entries),
            'medium': len(medium_entries),
            'long': len(long_entries)
        },
        'short_entry_prefix_rates': short_rates,
        'medium_entry_prefix_rates': medium_rates,
        'long_entry_prefix_rates': long_rates,
        'short_enriched_prefixes': short_enriched[:10],
        'long_enriched_prefixes': long_enriched[:10]
    }


# ============================================================================
# ANALYSIS 5: STRUCTURAL ROLE HYPOTHESES
# ============================================================================

def generate_structural_hypotheses(
    position_results: Dict,
    cooccur_results: Dict,
    sequence_results: Dict,
    association_results: Dict
) -> Dict:
    """
    Based on all analyses, propose structural roles for prefixes.
    NOT semantic meanings - structural/functional roles only.
    """
    print("  Generating structural role hypotheses...")

    hypotheses = []

    # Entry-initial markers
    for p in position_results.get('initial_prefixes', [])[:10]:
        hypotheses.append({
            'prefix': p['prefix'],
            'proposed_role': 'ENTRY_INITIAL_MARKER',
            'evidence': f"Mean position {p['mean_position']}, {p['quintiles'][0]}% in first quintile",
            'confidence': 'HIGH' if p['quintiles'][0] > 30 else 'MEDIUM'
        })

    # Entry-final markers
    for p in position_results.get('final_prefixes', [])[:10]:
        hypotheses.append({
            'prefix': p['prefix'],
            'proposed_role': 'ENTRY_FINAL_MARKER',
            'evidence': f"Mean position {p['mean_position']}, {p['quintiles'][4]}% in last quintile",
            'confidence': 'HIGH' if p['quintiles'][4] > 30 else 'MEDIUM'
        })

    # Distributed/elaborator prefixes
    for p in position_results.get('uniform_prefixes', [])[:10]:
        hypotheses.append({
            'prefix': p['prefix'],
            'proposed_role': 'ENTRY_ELABORATOR',
            'evidence': f"Uniform distribution (std={p['std_position']})",
            'confidence': 'MEDIUM'
        })

    # Strong co-occurrence pairs might indicate functional relationships
    for assoc in cooccur_results.get('positive_associations', [])[:5]:
        hypotheses.append({
            'prefix': f"{assoc['pair'][0]}+{assoc['pair'][1]}",
            'proposed_role': 'FUNCTIONAL_PAIR',
            'evidence': f"PMI={assoc['pmi']}, co-occur {assoc['co_count']} times",
            'confidence': 'MEDIUM'
        })

    # Length associations
    for p in association_results.get('short_enriched_prefixes', [])[:3]:
        hypotheses.append({
            'prefix': p['prefix'],
            'proposed_role': 'SHORT_ENTRY_MARKER',
            'evidence': f"Enriched in short entries ({p['short_rate']}% vs {p['medium_rate']}%)",
            'confidence': 'MEDIUM'
        })

    for p in association_results.get('long_enriched_prefixes', [])[:3]:
        hypotheses.append({
            'prefix': p['prefix'],
            'proposed_role': 'LONG_ENTRY_MARKER',
            'evidence': f"Enriched in long entries ({p['long_rate']}% vs {p['medium_rate']}%)",
            'confidence': 'MEDIUM'
        })

    # Organize by role
    by_role = defaultdict(list)
    for h in hypotheses:
        by_role[h['proposed_role']].append(h)

    return {
        'hypotheses': hypotheses,
        'by_role': dict(by_role),
        'disclaimer': 'These are STRUCTURAL role hypotheses, not semantic interpretations. '
                     'They describe where prefixes tend to appear and how they correlate '
                     'with entry characteristics, not what they mean.'
    }


def analyze_section(words: List[Dict], section_name: str) -> Dict:
    """Run all analyses on a section."""
    print(f"\nAnalyzing {section_name} ({len(words)} words)...")

    entries = segment_into_entries(words)
    print(f"  Segmented into {len(entries)} entries")

    results = {
        'section': section_name,
        'word_count': len(words),
        'entry_count': len(entries)
    }

    results['positional'] = analyze_positional_distribution(entries)
    results['cooccurrence'] = analyze_cooccurrence(entries)
    results['sequential'] = analyze_sequential_patterns(entries)
    results['entry_association'] = analyze_entry_type_association(entries)
    results['hypotheses'] = generate_structural_hypotheses(
        results['positional'],
        results['cooccurrence'],
        results['sequential'],
        results['entry_association']
    )

    return results


def main():
    print("=" * 70)
    print("PREFIX ROLE ANALYSIS")
    print("Analyzing prefix structural roles within entries")
    print("=" * 70)

    # Load corpus
    print("\nLoading corpus...")
    all_words, by_currier = load_corpus()
    print(f"Total words: {len(all_words)}")

    results = {
        'timestamp': datetime.now().isoformat(),
        'methodology': 'Prefix role analysis using folio-based entry segmentation'
    }

    # Analyze each section
    results['currier_a'] = analyze_section(by_currier['A'], 'Currier A')
    results['currier_b'] = analyze_section(by_currier['B'], 'Currier B')

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for section in ['currier_a', 'currier_b']:
        s = results[section]
        print(f"\n{section.upper()}:")

        pos = s['positional']
        print(f"\n  Position Types:")
        for ptype, count in pos['count_by_type'].items():
            print(f"    {ptype}: {count} prefixes")

        print(f"\n  Entry-Initial Prefixes:")
        for p in pos['initial_prefixes'][:5]:
            print(f"    {p['prefix']}: mean={p['mean_position']}, first_quintile={p['quintiles'][0]}%")

        print(f"\n  Entry-Final Prefixes:")
        for p in pos['final_prefixes'][:5]:
            print(f"    {p['prefix']}: mean={p['mean_position']}, last_quintile={p['quintiles'][4]}%")

        cooc = s['cooccurrence']
        print(f"\n  Top Positive Associations (high PMI):")
        for p in cooc['positive_associations'][:5]:
            print(f"    {p['pair'][0]} + {p['pair'][1]}: PMI={p['pmi']}")

        seq = s['sequential']
        print(f"\n  Top Entry-Opening Sequences:")
        for seq_tuple, count in seq['top_opening_sequences'][:5]:
            print(f"    {' -> '.join(seq_tuple)}: {count} times")

        hyp = s['hypotheses']
        print(f"\n  Structural Role Hypotheses ({len(hyp['hypotheses'])} total):")
        for role, items in hyp['by_role'].items():
            print(f"    {role}: {len(items)} prefixes")

    # Compare A vs B
    print("\n" + "=" * 70)
    print("CURRIER A vs B COMPARISON")
    print("=" * 70)

    # Compare initial prefixes
    a_initial = {p['prefix'] for p in results['currier_a']['positional']['initial_prefixes']}
    b_initial = {p['prefix'] for p in results['currier_b']['positional']['initial_prefixes']}

    shared_initial = a_initial & b_initial
    a_only_initial = a_initial - b_initial
    b_only_initial = b_initial - a_initial

    print(f"\nEntry-Initial Prefixes:")
    print(f"  Shared: {shared_initial if shared_initial else 'None'}")
    print(f"  A only: {a_only_initial if a_only_initial else 'None'}")
    print(f"  B only: {b_only_initial if b_only_initial else 'None'}")

    # Compare top bigrams
    a_bigrams = dict(results['currier_a']['sequential']['top_bigrams'][:20])
    b_bigrams = dict(results['currier_b']['sequential']['top_bigrams'][:20])

    shared_bigrams = set(a_bigrams.keys()) & set(b_bigrams.keys())
    print(f"\n  Shared top bigrams: {len(shared_bigrams)}/{20}")

    # Save results
    with open('prefix_role_analysis_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to prefix_role_analysis_report.json")


if __name__ == '__main__':
    main()
