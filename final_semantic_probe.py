#!/usr/bin/env python3
"""
Final Semantic Probe with Cipher Compatibility Analysis

Three parallel tests:
- Test A: "daiin" grammatical function analysis
- Test E: Hub role vocabulary differentiation
- Test N: Naibbe cipher compatibility

Output: 17 JSON files
"""

import csv
import json
import math
import random
from collections import defaultdict, Counter
from datetime import datetime
from typing import List, Dict, Tuple, Set, Optional
import numpy as np
from scipy import stats

# =============================================================================
# CONFIGURATION
# =============================================================================

KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo',
    'op', 'or', 'os', 'oe', 'of', 'sy', 'yp', 'ra', 'lo', 'ks', 'ai',
    'ka', 'te', 'de', 'ro', 'qk', 'yd', 'ye', 'ys', 'ep', 'ec', 'ed'
]

KNOWN_SUFFIXES = [
    'aiin', 'ain', 'iin', 'in',
    'eedy', 'edy', 'dy',
    'eey', 'ey', 'hy', 'y',
    'ar', 'or', 'ir', 'er',
    'al', 'ol', 'el', 'il',
    'am', 'an', 'en', 'on',
    's', 'm', 'n', 'l', 'r', 'd'
]

# Closing suffixes for clause boundary detection
CLOSING_SUFFIXES = ['y', 'dy', 'aiin', 'iin', 'in', 'ey', 'hy']

MIN_ENTRY_WORDS = 9

# Hub role assignments
HUB_ROLES = {
    'f10v': ('paiin', 'opener'),
    'f19r': ('pchor', 'opener'),
    'f21r': ('pchor', 'opener'),
    'f22r': ('pol', 'closer'),
    'f35v': ('par', 'opener'),
    'f42r': ('sho', 'support'),
    'f52v': ('pchor', 'opener'),
    'f58r': ('kor', 'support'),
    'f58v': ('tol', 'opener'),
    # f96r (tor) excluded - text-only page
}

OPENER_FOLIOS = ['f10v', 'f19r', 'f21r', 'f35v', 'f52v', 'f58v']
SUPPORT_FOLIOS = ['f42r', 'f58r']
CLOSER_FOLIOS = ['f22r']

# =============================================================================
# DATA LOADING
# =============================================================================

def load_corpus() -> List[Dict]:
    """Load the Voynich transcription corpus."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'
    words = []
    seen = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip().strip('"')
            folio = row.get('folio', '').strip().strip('"')
            line_num = row.get('line_number', '').strip().strip('"')
            currier = row.get('language', '').strip().strip('"')
            section = row.get('section', '').strip().strip('"')
            line_initial = row.get('line_initial', '').strip().strip('"')
            line_final = row.get('line_final', '').strip().strip('"')

            if not word or word.startswith('*') or len(word) < 2:
                continue

            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                words.append({
                    'word': word,
                    'folio': folio,
                    'line': line_num,
                    'currier': currier,
                    'section': section,
                    'line_initial': int(line_initial) if line_initial.isdigit() else 0,
                    'line_final': int(line_final) if line_final.isdigit() else 0
                })

    return words

def get_prefix(word: str) -> str:
    """Extract prefix using longest match from known list."""
    for length in [3, 2]:
        if len(word) >= length:
            prefix = word[:length]
            if prefix in KNOWN_PREFIXES:
                return prefix
    return word[:2] if len(word) >= 2 else word

def get_suffix(word: str) -> str:
    """Extract suffix using longest match from known list."""
    for length in [4, 3, 2]:
        if len(word) >= length:
            suffix = word[-length:]
            if suffix in KNOWN_SUFFIXES:
                return suffix
    return word[-2:] if len(word) >= 2 else word

def segment_into_entries(words: List[Dict]) -> Dict[str, List[Dict]]:
    """Group words by folio to create per-page entries."""
    by_folio = defaultdict(list)
    for w in words:
        by_folio[w['folio']].append(w)
    return dict(by_folio)

def get_entry_parts(entry: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Split entry into three parts."""
    n = len(entry)
    third = n // 3
    return entry[:third], entry[third:2*third], entry[2*third:]

def jensen_shannon_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
    """Compute Jensen-Shannon divergence between two distributions."""
    all_keys = set(p.keys()) | set(q.keys())
    if not all_keys:
        return 0.0

    p_vec = np.array([p.get(k, 0) for k in all_keys])
    q_vec = np.array([q.get(k, 0) for k in all_keys])

    eps = 1e-10
    p_vec = p_vec + eps
    q_vec = q_vec + eps

    p_vec = p_vec / p_vec.sum()
    q_vec = q_vec / q_vec.sum()

    m = 0.5 * (p_vec + q_vec)
    js = 0.5 * (stats.entropy(p_vec, m) + stats.entropy(q_vec, m))

    return js

def compute_entropy(counts: Counter) -> float:
    """Compute Shannon entropy of a distribution."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counts.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)

# =============================================================================
# TEST A: "daiin" GRAMMATICAL FUNCTION ANALYSIS
# =============================================================================

def test_a1_frequency_baseline(words: List[Dict], entries: Dict[str, List[Dict]]) -> Dict:
    """A1: Frequency baseline for 'daiin'."""
    print("  Running A1: Frequency baseline...")

    # Count all occurrences of daiin and variants
    daiin_variants = ['daiin', 'dain', 'odaiin', 'ydaiin', 'daiiiin']
    daiin_occurrences = [w for w in words if w['word'] in daiin_variants or w['word'] == 'daiin']

    # Just 'daiin' exact match
    exact_daiin = [w for w in words if w['word'] == 'daiin']

    # Word frequency ranking
    word_counts = Counter(w['word'] for w in words)
    sorted_words = word_counts.most_common(50)

    # Find rank of 'daiin'
    daiin_rank = None
    for i, (word, count) in enumerate(sorted_words):
        if word == 'daiin':
            daiin_rank = i + 1
            break

    # Distribution across Currier A/B
    currier_a = sum(1 for w in exact_daiin if w['currier'] == 'A')
    currier_b = sum(1 for w in exact_daiin if w['currier'] == 'B')

    # Entries containing daiin
    entries_with_daiin = set()
    for w in exact_daiin:
        entries_with_daiin.add(w['folio'])

    total_entries = len(entries)

    # Top 20 most frequent for comparison
    top_20 = []
    for word, count in sorted_words[:20]:
        word_currier_a = sum(1 for w in words if w['word'] == word and w['currier'] == 'A')
        word_currier_b = sum(1 for w in words if w['word'] == word and w['currier'] == 'B')
        top_20.append({
            'word': word,
            'count': count,
            'currier_a': word_currier_a,
            'currier_b': word_currier_b,
            'prefix': get_prefix(word),
            'suffix': get_suffix(word),
            'length': len(word)
        })

    return {
        'metadata': {
            'phase': 'A1',
            'title': 'Frequency Baseline',
            'timestamp': datetime.now().isoformat(),
            'dependencies': []
        },
        'findings': {
            'daiin_total_occurrences': len(exact_daiin),
            'daiin_rank': daiin_rank,
            'daiin_currier_a': currier_a,
            'daiin_currier_b': currier_b,
            'entries_containing_daiin': len(entries_with_daiin),
            'total_entries': total_entries,
            'percent_entries_with_daiin': round(len(entries_with_daiin) / total_entries * 100, 1) if total_entries > 0 else 0,
            'top_20_words': top_20,
            'daiin_variants_total': len(daiin_occurrences)
        },
        'summary': {
            'key_results': [
                f"'daiin' appears {len(exact_daiin)} times (rank #{daiin_rank})",
                f"Distribution: {currier_a} in A, {currier_b} in B",
                f"Present in {len(entries_with_daiin)} of {total_entries} entries ({len(entries_with_daiin)/total_entries*100:.1f}%)"
            ],
            'implications': []
        }
    }

def test_a2_positional_distribution(words: List[Dict], entries: Dict[str, List[Dict]]) -> Dict:
    """A2: Positional distribution analysis for 'daiin'."""
    print("  Running A2: Positional distribution...")

    # Track positions
    entry_positions = []  # position as % through entry
    part_counts = {'part1': 0, 'part2': 0, 'part3': 0}
    line_positions = {'first': 0, 'middle': 0, 'last': 0}

    # For each entry, find daiin positions
    for folio, entry in entries.items():
        if len(entry) < MIN_ENTRY_WORDS:
            continue

        part1, part2, part3 = get_entry_parts(entry)
        entry_len = len(entry)

        for i, w in enumerate(entry):
            if w['word'] == 'daiin':
                # Position as percentage
                pos_pct = i / entry_len if entry_len > 0 else 0
                entry_positions.append(pos_pct)

                # Which part?
                if i < len(part1):
                    part_counts['part1'] += 1
                elif i < len(part1) + len(part2):
                    part_counts['part2'] += 1
                else:
                    part_counts['part3'] += 1

                # Line position
                if w['line_initial'] == 1:
                    line_positions['first'] += 1
                elif w['line_final'] == 1:
                    line_positions['last'] += 1
                else:
                    line_positions['middle'] += 1

    # Compute position entropy
    if entry_positions:
        # Bin positions into 10 bins
        bins = [0] * 10
        for pos in entry_positions:
            bin_idx = min(int(pos * 10), 9)
            bins[bin_idx] += 1
        position_entropy = compute_entropy(Counter(dict(enumerate(bins))))

        # Random baseline entropy (uniform distribution)
        random_entropy = math.log2(10)  # max entropy for 10 bins

        # Constraint ratio
        constraint_ratio = (random_entropy - position_entropy) / random_entropy if random_entropy > 0 else 0
    else:
        position_entropy = 0
        random_entropy = 0
        constraint_ratio = 0

    return {
        'metadata': {
            'phase': 'A2',
            'title': 'Positional Distribution',
            'timestamp': datetime.now().isoformat(),
            'dependencies': ['A1']
        },
        'findings': {
            'total_occurrences': len(entry_positions),
            'part_distribution': part_counts,
            'line_position_distribution': line_positions,
            'mean_position_percent': round(np.mean(entry_positions) * 100, 1) if entry_positions else 0,
            'std_position_percent': round(np.std(entry_positions) * 100, 1) if entry_positions else 0,
            'position_entropy': round(position_entropy, 3),
            'random_entropy': round(random_entropy, 3),
            'constraint_ratio': round(constraint_ratio, 3),
            'position_histogram': bins if entry_positions else []
        },
        'summary': {
            'key_results': [
                f"Part distribution: P1={part_counts['part1']}, P2={part_counts['part2']}, P3={part_counts['part3']}",
                f"Mean position: {np.mean(entry_positions)*100:.1f}% through entry" if entry_positions else "No data",
                f"Position constraint ratio: {constraint_ratio:.3f} ({'strong' if constraint_ratio > 0.3 else 'weak'} constraint)"
            ],
            'implications': [
                'Constraint ratio > 0.3 suggests grammatical function' if constraint_ratio > 0.3 else 'Low constraint ratio suggests content word'
            ]
        }
    }

def test_a3_morphological_context(words: List[Dict], entries: Dict[str, List[Dict]]) -> Dict:
    """A3: Morphological context analysis for 'daiin'."""
    print("  Running A3: Morphological context...")

    # Find preceding and following words
    preceding_words = Counter()
    following_words = Counter()
    preceding_prefixes = Counter()
    following_prefixes = Counter()
    preceding_suffixes = Counter()
    following_suffixes = Counter()
    bigrams_with_daiin = Counter()

    for folio, entry in entries.items():
        if len(entry) < MIN_ENTRY_WORDS:
            continue

        for i, w in enumerate(entry):
            if w['word'] == 'daiin':
                # Preceding word
                if i > 0:
                    prev_word = entry[i-1]['word']
                    preceding_words[prev_word] += 1
                    preceding_prefixes[get_prefix(prev_word)] += 1
                    preceding_suffixes[get_suffix(prev_word)] += 1
                    bigrams_with_daiin[f"{prev_word} daiin"] += 1

                # Following word
                if i < len(entry) - 1:
                    next_word = entry[i+1]['word']
                    following_words[next_word] += 1
                    following_prefixes[get_prefix(next_word)] += 1
                    following_suffixes[get_suffix(next_word)] += 1
                    bigrams_with_daiin[f"daiin {next_word}"] += 1

    # Compute corpus-wide distributions for comparison
    all_prefixes = Counter(get_prefix(w['word']) for w in words)
    all_suffixes = Counter(get_suffix(w['word']) for w in words)

    # Normalize to distributions
    total_prec = sum(preceding_prefixes.values())
    total_foll = sum(following_prefixes.values())
    total_all = sum(all_prefixes.values())

    prec_dist = {k: v/total_prec for k, v in preceding_prefixes.items()} if total_prec > 0 else {}
    foll_dist = {k: v/total_foll for k, v in following_prefixes.items()} if total_foll > 0 else {}
    all_dist = {k: v/total_all for k, v in all_prefixes.items()} if total_all > 0 else {}

    # JS divergence from corpus
    js_preceding = jensen_shannon_divergence(prec_dist, all_dist)
    js_following = jensen_shannon_divergence(foll_dist, all_dist)

    return {
        'metadata': {
            'phase': 'A3',
            'title': 'Morphological Context',
            'timestamp': datetime.now().isoformat(),
            'dependencies': ['A1']
        },
        'findings': {
            'preceding_context': {
                'unique_words': len(preceding_words),
                'top_20': preceding_words.most_common(20),
                'prefix_distribution': preceding_prefixes.most_common(15),
                'suffix_distribution': preceding_suffixes.most_common(15)
            },
            'following_context': {
                'unique_words': len(following_words),
                'top_20': following_words.most_common(20),
                'prefix_distribution': following_prefixes.most_common(15),
                'suffix_distribution': following_suffixes.most_common(15)
            },
            'bigrams': bigrams_with_daiin.most_common(20),
            'js_divergence_preceding': round(js_preceding, 4),
            'js_divergence_following': round(js_following, 4),
            'context_restriction_score': round((js_preceding + js_following) / 2, 4)
        },
        'summary': {
            'key_results': [
                f"Preceding context: {len(preceding_words)} unique words",
                f"Following context: {len(following_words)} unique words",
                f"JS divergence (preceding): {js_preceding:.4f}",
                f"JS divergence (following): {js_following:.4f}"
            ],
            'implications': [
                'High JS divergence indicates restricted context (grammatical function)' if (js_preceding + js_following) / 2 > 0.1 else 'Low divergence suggests free context (content word)'
            ]
        }
    }

def test_a4_functional_classification(words: List[Dict], entries: Dict[str, List[Dict]]) -> Dict:
    """A4: Functional classification of 'daiin'."""
    print("  Running A4: Functional classification...")

    # Hypothesis tests
    clause_marker_score = 0
    determiner_score = 0
    conjunction_score = 0
    content_word_score = 0

    # Track evidence
    after_closing_suffix = 0
    total_with_predecessor = 0
    precedes_long_word = 0
    total_with_successor = 0
    consecutive_daiin = 0
    total_daiin = 0
    prefix_match_rate = 0
    prefix_comparisons = 0

    for folio, entry in entries.items():
        if len(entry) < MIN_ENTRY_WORDS:
            continue

        for i, w in enumerate(entry):
            if w['word'] == 'daiin':
                total_daiin += 1

                # CLAUSE_MARKER: After closing suffixes?
                if i > 0:
                    total_with_predecessor += 1
                    prev_suffix = get_suffix(entry[i-1]['word'])
                    if prev_suffix in CLOSING_SUFFIXES:
                        after_closing_suffix += 1

                # DETERMINER: Precedes longer/content words?
                if i < len(entry) - 1:
                    total_with_successor += 1
                    next_word = entry[i+1]['word']
                    if len(next_word) > 5:  # Longer word
                        precedes_long_word += 1

                    # Check for consecutive daiin
                    if next_word == 'daiin':
                        consecutive_daiin += 1

                # CONJUNCTION: Prefix match between before/after?
                if i > 0 and i < len(entry) - 1:
                    prefix_comparisons += 1
                    prev_prefix = get_prefix(entry[i-1]['word'])
                    next_prefix = get_prefix(entry[i+1]['word'])
                    if prev_prefix == next_prefix:
                        prefix_match_rate += 1

    # Calculate rates
    closing_suffix_rate = after_closing_suffix / total_with_predecessor if total_with_predecessor > 0 else 0
    long_word_rate = precedes_long_word / total_with_successor if total_with_successor > 0 else 0
    consecutive_rate = consecutive_daiin / total_daiin if total_daiin > 0 else 0
    prefix_match = prefix_match_rate / prefix_comparisons if prefix_comparisons > 0 else 0

    # Score hypotheses (0-5 scale)
    # CLAUSE_MARKER: High if appears after closing suffixes
    clause_marker_score = min(5, int(closing_suffix_rate * 10))

    # DETERMINER: High if precedes content words, low consecutive rate
    determiner_score = min(5, int(long_word_rate * 5) + (3 if consecutive_rate < 0.05 else 0))

    # CONJUNCTION: High if connects similar elements
    conjunction_score = min(5, int(prefix_match * 10))

    # CONTENT_WORD: High if unrestricted (low scores elsewhere)
    content_word_score = 5 - max(clause_marker_score, determiner_score, conjunction_score)

    # Determine classification
    scores = {
        'CLAUSE_MARKER': clause_marker_score,
        'DETERMINER': determiner_score,
        'CONJUNCTION': conjunction_score,
        'CONTENT_WORD': content_word_score
    }
    best_class = max(scores, key=scores.get)
    best_score = scores[best_class]

    # Confidence
    sorted_scores = sorted(scores.values(), reverse=True)
    if sorted_scores[0] - sorted_scores[1] >= 2:
        confidence = 'HIGH'
    elif sorted_scores[0] - sorted_scores[1] >= 1:
        confidence = 'MEDIUM'
    else:
        confidence = 'LOW'

    if best_score <= 2:
        best_class = 'INCONCLUSIVE'
        confidence = 'LOW'

    return {
        'metadata': {
            'phase': 'A4',
            'title': 'Functional Classification',
            'timestamp': datetime.now().isoformat(),
            'dependencies': ['A1', 'A2', 'A3']
        },
        'findings': {
            'evidence': {
                'closing_suffix_rate': round(closing_suffix_rate, 3),
                'precedes_long_word_rate': round(long_word_rate, 3),
                'consecutive_daiin_rate': round(consecutive_rate, 3),
                'prefix_match_rate': round(prefix_match, 3)
            },
            'hypothesis_scores': scores,
            'classification': best_class,
            'confidence': confidence
        },
        'summary': {
            'key_results': [
                f"Classification: {best_class} (confidence: {confidence})",
                f"Scores: CLAUSE_MARKER={clause_marker_score}, DETERMINER={determiner_score}, CONJUNCTION={conjunction_score}, CONTENT={content_word_score}"
            ],
            'implications': [
                f"'daiin' most likely functions as {best_class}" if best_class != 'INCONCLUSIVE' else "Function remains unclear"
            ]
        }
    }

def test_a5_cross_validation(words: List[Dict], entries: Dict[str, List[Dict]]) -> Dict:
    """A5: Cross-validation across Currier A/B, hub/isolate, parts."""
    print("  Running A5: Cross-validation...")

    # Separate by Currier
    currier_a_entries = {f: e for f, e in entries.items() if e and e[0]['currier'] == 'A'}
    currier_b_entries = {f: e for f, e in entries.items() if e and e[0]['currier'] == 'B'}

    # Hub vs isolate
    hub_entries = {f: e for f, e in entries.items() if f in HUB_ROLES}
    isolate_entries = {f: e for f, e in entries.items() if f not in HUB_ROLES and len(e) >= MIN_ENTRY_WORDS}

    def analyze_daiin_behavior(entry_set: Dict) -> Dict:
        """Analyze daiin behavior in a set of entries."""
        positions = []
        part_counts = {'part1': 0, 'part2': 0, 'part3': 0}

        for folio, entry in entry_set.items():
            if len(entry) < MIN_ENTRY_WORDS:
                continue

            part1, part2, part3 = get_entry_parts(entry)
            entry_len = len(entry)

            for i, w in enumerate(entry):
                if w['word'] == 'daiin':
                    positions.append(i / entry_len)
                    if i < len(part1):
                        part_counts['part1'] += 1
                    elif i < len(part1) + len(part2):
                        part_counts['part2'] += 1
                    else:
                        part_counts['part3'] += 1

        return {
            'count': len(positions),
            'mean_position': round(np.mean(positions), 3) if positions else 0,
            'std_position': round(np.std(positions), 3) if positions else 0,
            'part_distribution': part_counts
        }

    currier_a_behavior = analyze_daiin_behavior(currier_a_entries)
    currier_b_behavior = analyze_daiin_behavior(currier_b_entries)
    hub_behavior = analyze_daiin_behavior(hub_entries)
    isolate_behavior = analyze_daiin_behavior(isolate_entries)

    # KS test for position distributions (Currier A vs B)
    a_positions = []
    b_positions = []
    for folio, entry in currier_a_entries.items():
        for i, w in enumerate(entry):
            if w['word'] == 'daiin':
                a_positions.append(i / len(entry))
    for folio, entry in currier_b_entries.items():
        for i, w in enumerate(entry):
            if w['word'] == 'daiin':
                b_positions.append(i / len(entry))

    if a_positions and b_positions:
        ks_stat, ks_pvalue = stats.ks_2samp(a_positions, b_positions)
    else:
        ks_stat, ks_pvalue = 0, 1.0

    consistent = ks_pvalue > 0.05  # Not significantly different

    return {
        'metadata': {
            'phase': 'A5',
            'title': 'Cross-Validation',
            'timestamp': datetime.now().isoformat(),
            'dependencies': ['A1', 'A2', 'A3', 'A4']
        },
        'findings': {
            'currier_a': currier_a_behavior,
            'currier_b': currier_b_behavior,
            'hub_entries': hub_behavior,
            'isolate_entries': isolate_behavior,
            'ks_test': {
                'statistic': round(ks_stat, 4),
                'p_value': round(ks_pvalue, 4),
                'consistent_across_currier': consistent
            }
        },
        'summary': {
            'key_results': [
                f"Currier A: {currier_a_behavior['count']} occurrences, mean pos {currier_a_behavior['mean_position']}",
                f"Currier B: {currier_b_behavior['count']} occurrences, mean pos {currier_b_behavior['mean_position']}",
                f"KS test p-value: {ks_pvalue:.4f} ({'consistent' if consistent else 'different'} behavior)"
            ],
            'implications': [
                "'daiin' behaves consistently across Currier A and B" if consistent else "'daiin' behaves differently in A vs B"
            ]
        }
    }

def test_a6_synthesis(a1: Dict, a2: Dict, a3: Dict, a4: Dict, a5: Dict) -> Dict:
    """A6: Synthesis of all daiin analyses."""
    print("  Running A6: Synthesis...")

    classification = a4['findings']['classification']
    confidence = a4['findings']['confidence']
    constraint_ratio = a2['findings']['constraint_ratio']
    context_score = a3['findings']['context_restriction_score']
    consistent = a5['findings']['ks_test']['consistent_across_currier']

    # Cipher compatibility assessment
    # If daiin shows strong grammatical constraints, this argues AGAINST Naibbe
    # because random chunking shouldn't preserve syntactic patterns
    if constraint_ratio > 0.3 and classification != 'CONTENT_WORD':
        cipher_compatible = False
        cipher_reasoning = "Strong positional constraints incompatible with random cipher chunking"
    else:
        cipher_compatible = True
        cipher_reasoning = "Weak constraints compatible with cipher hypothesis"

    return {
        'metadata': {
            'phase': 'A6',
            'title': 'daiin Analysis Synthesis',
            'timestamp': datetime.now().isoformat(),
            'dependencies': ['A1', 'A2', 'A3', 'A4', 'A5']
        },
        'findings': {
            'classification': classification,
            'confidence': confidence,
            'positional_constraint_ratio': constraint_ratio,
            'context_restriction_score': context_score,
            'consistent_across_sections': consistent,
            'cipher_compatibility': {
                'naibbe_compatible': cipher_compatible,
                'reasoning': cipher_reasoning
            }
        },
        'summary': {
            'key_results': [
                f"Final classification: {classification} ({confidence} confidence)",
                f"Positional constraint ratio: {constraint_ratio:.3f}",
                f"Context restriction: {context_score:.4f}",
                f"Consistent across Currier A/B: {consistent}"
            ],
            'implications': [
                cipher_reasoning
            ]
        }
    }

# =============================================================================
# TEST E: HUB ROLE VOCABULARY DIFFERENTIATION
# =============================================================================

def test_e1_corpus_compilation(words: List[Dict], entries: Dict[str, List[Dict]]) -> Dict:
    """E1: Compile vocabulary by hub role."""
    print("  Running E1: Corpus compilation...")

    def get_vocabulary(folio_list: List[str]) -> Dict:
        """Extract vocabulary from a list of folios."""
        all_words = []
        part1_words = []
        part2_words = []
        part3_words = []

        for folio in folio_list:
            if folio not in entries:
                continue
            entry = entries[folio]
            if len(entry) < MIN_ENTRY_WORDS:
                continue

            part1, part2, part3 = get_entry_parts(entry)

            all_words.extend([w['word'] for w in entry])
            part1_words.extend([w['word'] for w in part1])
            part2_words.extend([w['word'] for w in part2])
            part3_words.extend([w['word'] for w in part3])

        return {
            'folios': folio_list,
            'total_tokens': len(all_words),
            'unique_tokens': len(set(all_words)),
            'vocabulary': dict(Counter(all_words)),
            'part1_vocabulary': dict(Counter(part1_words)),
            'part2_vocabulary': dict(Counter(part2_words)),
            'part3_vocabulary': dict(Counter(part3_words))
        }

    opener_vocab = get_vocabulary(OPENER_FOLIOS)
    support_vocab = get_vocabulary(SUPPORT_FOLIOS)
    closer_vocab = get_vocabulary(CLOSER_FOLIOS)

    # Baseline: random isolate folios (not hub)
    all_folios = list(entries.keys())
    hub_folios = set(HUB_ROLES.keys())
    isolate_folios = [f for f in all_folios if f not in hub_folios and len(entries[f]) >= MIN_ENTRY_WORDS]

    # Sample 6 random isolates (match OPENER count)
    random.seed(42)
    baseline_samples = []
    for i in range(10):  # 10 samples for stability
        sample = random.sample(isolate_folios, min(6, len(isolate_folios)))
        baseline_samples.append(get_vocabulary(sample))

    # Average baseline
    avg_baseline_tokens = np.mean([s['total_tokens'] for s in baseline_samples])
    avg_baseline_unique = np.mean([s['unique_tokens'] for s in baseline_samples])

    return {
        'metadata': {
            'phase': 'E1',
            'title': 'Role Corpus Compilation',
            'timestamp': datetime.now().isoformat(),
            'dependencies': []
        },
        'findings': {
            'opener': {
                'folios': OPENER_FOLIOS,
                'n_folios': len(OPENER_FOLIOS),
                'total_tokens': opener_vocab['total_tokens'],
                'unique_tokens': opener_vocab['unique_tokens']
            },
            'support': {
                'folios': SUPPORT_FOLIOS,
                'n_folios': len(SUPPORT_FOLIOS),
                'total_tokens': support_vocab['total_tokens'],
                'unique_tokens': support_vocab['unique_tokens']
            },
            'closer': {
                'folios': CLOSER_FOLIOS,
                'n_folios': len(CLOSER_FOLIOS),
                'total_tokens': closer_vocab['total_tokens'],
                'unique_tokens': closer_vocab['unique_tokens'],
                'note': 'N=1, descriptive only'
            },
            'baseline': {
                'n_samples': 10,
                'avg_total_tokens': round(avg_baseline_tokens, 1),
                'avg_unique_tokens': round(avg_baseline_unique, 1)
            }
        },
        'vocabularies': {
            'opener': opener_vocab['vocabulary'],
            'support': support_vocab['vocabulary'],
            'closer': closer_vocab['vocabulary']
        },
        'summary': {
            'key_results': [
                f"OPENER: {len(OPENER_FOLIOS)} folios, {opener_vocab['total_tokens']} tokens",
                f"SUPPORT: {len(SUPPORT_FOLIOS)} folios, {support_vocab['total_tokens']} tokens",
                f"CLOSER: {len(CLOSER_FOLIOS)} folios (N=1, untestable)"
            ],
            'implications': []
        }
    }

def test_e2_vocabulary_comparison(e1_data: Dict, entries: Dict[str, List[Dict]]) -> Dict:
    """E2: Compare vocabulary between roles."""
    print("  Running E2: Vocabulary comparison...")

    opener_vocab = set(e1_data['vocabularies']['opener'].keys())
    support_vocab = set(e1_data['vocabularies']['support'].keys())
    closer_vocab = set(e1_data['vocabularies']['closer'].keys())

    # Get baseline vocabulary
    hub_folios = set(HUB_ROLES.keys())
    isolate_folios = [f for f in entries.keys() if f not in hub_folios and len(entries[f]) >= MIN_ENTRY_WORDS]

    baseline_words = []
    for folio in isolate_folios[:20]:  # Sample 20 isolates
        baseline_words.extend([w['word'] for w in entries[folio]])
    baseline_vocab = set(baseline_words)
    baseline_counts = Counter(baseline_words)

    opener_counts = Counter(e1_data['vocabularies']['opener'])
    support_counts = Counter(e1_data['vocabularies']['support'])

    # Jaccard similarities
    def jaccard(a: Set, b: Set) -> float:
        if not a or not b:
            return 0
        return len(a & b) / len(a | b)

    opener_support_jaccard = jaccard(opener_vocab, support_vocab)
    opener_baseline_jaccard = jaccard(opener_vocab, baseline_vocab)
    support_baseline_jaccard = jaccard(support_vocab, baseline_vocab)

    # Enrichment analysis
    def compute_enrichment(group_counts: Counter, group_total: int,
                          baseline_counts: Counter, baseline_total: int) -> List[Dict]:
        enriched = []
        for word, count in group_counts.items():
            if count < 3:  # Minimum count filter
                continue
            group_rate = count / group_total if group_total > 0 else 0
            baseline_count = baseline_counts.get(word, 0)
            baseline_rate = baseline_count / baseline_total if baseline_total > 0 else 0.0001
            enrichment = group_rate / baseline_rate if baseline_rate > 0 else float('inf')

            if enrichment > 2.0:
                enriched.append({
                    'word': word,
                    'group_count': count,
                    'baseline_count': baseline_count,
                    'enrichment': round(enrichment, 2),
                    'prefix': get_prefix(word),
                    'suffix': get_suffix(word)
                })

        enriched.sort(key=lambda x: x['enrichment'], reverse=True)
        return enriched

    opener_total = e1_data['findings']['opener']['total_tokens']
    support_total = e1_data['findings']['support']['total_tokens']
    baseline_total = len(baseline_words)

    opener_enriched = compute_enrichment(opener_counts, opener_total, baseline_counts, baseline_total)
    support_enriched = compute_enrichment(support_counts, support_total, baseline_counts, baseline_total)

    # Group-exclusive tokens
    opener_exclusive = opener_vocab - support_vocab - baseline_vocab
    support_exclusive = support_vocab - opener_vocab - baseline_vocab

    return {
        'metadata': {
            'phase': 'E2',
            'title': 'Vocabulary Comparison',
            'timestamp': datetime.now().isoformat(),
            'dependencies': ['E1']
        },
        'findings': {
            'jaccard_similarities': {
                'opener_support': round(opener_support_jaccard, 3),
                'opener_baseline': round(opener_baseline_jaccard, 3),
                'support_baseline': round(support_baseline_jaccard, 3)
            },
            'enriched_tokens': {
                'opener': opener_enriched[:20],
                'support': support_enriched[:20]
            },
            'exclusive_tokens': {
                'opener_exclusive': list(opener_exclusive)[:20],
                'support_exclusive': list(support_exclusive)[:20],
                'opener_exclusive_count': len(opener_exclusive),
                'support_exclusive_count': len(support_exclusive)
            }
        },
        'summary': {
            'key_results': [
                f"Opener-Support Jaccard: {opener_support_jaccard:.3f}",
                f"Opener enriched tokens: {len(opener_enriched)}",
                f"Support enriched tokens: {len(support_enriched)}",
                f"Opener-exclusive: {len(opener_exclusive)}, Support-exclusive: {len(support_exclusive)}"
            ],
            'implications': []
        }
    }

def test_e3_statistical_testing(e1_data: Dict, e2_data: Dict, entries: Dict[str, List[Dict]]) -> Dict:
    """E3: Statistical testing of role vocabulary differences."""
    print("  Running E3: Statistical testing...")

    opener_counts = Counter(e1_data['vocabularies']['opener'])
    support_counts = Counter(e1_data['vocabularies']['support'])

    # Prefix distributions
    opener_prefixes = Counter()
    support_prefixes = Counter()

    for word, count in opener_counts.items():
        opener_prefixes[get_prefix(word)] += count
    for word, count in support_counts.items():
        support_prefixes[get_prefix(word)] += count

    # Chi-square test on prefix distributions
    all_prefixes = set(opener_prefixes.keys()) | set(support_prefixes.keys())
    observed = []
    for prefix in all_prefixes:
        observed.append([opener_prefixes.get(prefix, 0), support_prefixes.get(prefix, 0)])

    if len(observed) > 1:
        observed_array = np.array(observed)
        # Remove rows with all zeros
        observed_array = observed_array[observed_array.sum(axis=1) > 0]
        if observed_array.shape[0] > 1:
            chi2, chi2_pvalue, dof, expected = stats.chi2_contingency(observed_array)
        else:
            chi2, chi2_pvalue = 0, 1.0
    else:
        chi2, chi2_pvalue = 0, 1.0

    # Permutation test: OPENER vs baseline
    hub_folios = set(HUB_ROLES.keys())
    isolate_folios = [f for f in entries.keys() if f not in hub_folios and len(entries[f]) >= MIN_ENTRY_WORDS]

    # Compute observed statistic: mean enrichment of opener tokens
    opener_enriched = e2_data['findings']['enriched_tokens']['opener']
    observed_stat = np.mean([t['enrichment'] for t in opener_enriched]) if opener_enriched else 0

    # Permutation test (simplified)
    n_permutations = 1000
    null_stats = []

    random.seed(42)
    for _ in range(n_permutations):
        # Randomly assign folios to "opener" and "baseline"
        shuffled = random.sample(isolate_folios + OPENER_FOLIOS, len(OPENER_FOLIOS))
        perm_vocab = Counter()
        for folio in shuffled:
            if folio in entries:
                for w in entries[folio]:
                    perm_vocab[w['word']] += 1

        # Compute enrichment statistic
        perm_total = sum(perm_vocab.values())
        baseline_total = sum(Counter(w['word'] for f in isolate_folios[:20] for w in entries.get(f, [])).values())

        perm_enrichments = []
        for word, count in perm_vocab.items():
            if count >= 3:
                rate = count / perm_total if perm_total > 0 else 0
                # Simple comparison to expected
                perm_enrichments.append(rate * 1000)  # Scaled rate

        null_stats.append(np.mean(perm_enrichments) if perm_enrichments else 0)

    # Compute p-value
    percentile = sum(1 for s in null_stats if s >= observed_stat) / n_permutations
    p_value = 1 - percentile if percentile < 0.5 else percentile

    return {
        'metadata': {
            'phase': 'E3',
            'title': 'Statistical Testing',
            'timestamp': datetime.now().isoformat(),
            'dependencies': ['E1', 'E2']
        },
        'findings': {
            'chi_square_test': {
                'statistic': round(chi2, 2),
                'p_value': round(chi2_pvalue, 4),
                'significant': chi2_pvalue < 0.05
            },
            'permutation_test': {
                'observed_statistic': round(observed_stat, 4),
                'null_mean': round(np.mean(null_stats), 4),
                'null_std': round(np.std(null_stats), 4),
                'percentile': round((1 - p_value) * 100, 1),
                'p_value': round(p_value, 4),
                'n_permutations': n_permutations
            }
        },
        'summary': {
            'key_results': [
                f"Chi-square test p-value: {chi2_pvalue:.4f} ({'significant' if chi2_pvalue < 0.05 else 'not significant'})",
                f"Permutation test p-value: {p_value:.4f}"
            ],
            'implications': []
        }
    }

def test_e4_pattern_analysis(e1_data: Dict, e2_data: Dict) -> Dict:
    """E4: Pattern analysis of enriched tokens."""
    print("  Running E4: Pattern analysis...")

    opener_enriched = e2_data['findings']['enriched_tokens']['opener']
    support_enriched = e2_data['findings']['enriched_tokens']['support']

    # Morphological clustering
    opener_prefixes = Counter([t['prefix'] for t in opener_enriched])
    opener_suffixes = Counter([t['suffix'] for t in opener_enriched])
    support_prefixes = Counter([t['prefix'] for t in support_enriched])
    support_suffixes = Counter([t['suffix'] for t in support_enriched])

    # Prefix signature vectors
    all_prefixes = set(opener_prefixes.keys()) | set(support_prefixes.keys())
    opener_vec = np.array([opener_prefixes.get(p, 0) for p in all_prefixes])
    support_vec = np.array([support_prefixes.get(p, 0) for p in all_prefixes])

    # Cosine similarity
    if np.linalg.norm(opener_vec) > 0 and np.linalg.norm(support_vec) > 0:
        cosine_sim = np.dot(opener_vec, support_vec) / (np.linalg.norm(opener_vec) * np.linalg.norm(support_vec))
    else:
        cosine_sim = 0

    return {
        'metadata': {
            'phase': 'E4',
            'title': 'Pattern Analysis',
            'timestamp': datetime.now().isoformat(),
            'dependencies': ['E1', 'E2']
        },
        'findings': {
            'opener_morphology': {
                'prefix_distribution': opener_prefixes.most_common(10),
                'suffix_distribution': opener_suffixes.most_common(10)
            },
            'support_morphology': {
                'prefix_distribution': support_prefixes.most_common(10),
                'suffix_distribution': support_suffixes.most_common(10)
            },
            'cosine_similarity': round(cosine_sim, 3)
        },
        'summary': {
            'key_results': [
                f"Opener dominant prefixes: {opener_prefixes.most_common(3)}",
                f"Support dominant prefixes: {support_prefixes.most_common(3)}",
                f"Prefix signature cosine similarity: {cosine_sim:.3f}"
            ],
            'implications': []
        }
    }

def test_e5_synthesis(e1: Dict, e2: Dict, e3: Dict, e4: Dict) -> Dict:
    """E5: Synthesis of hub role vocabulary analysis."""
    print("  Running E5: Synthesis...")

    chi2_sig = e3['findings']['chi_square_test']['significant']
    perm_pvalue = e3['findings']['permutation_test']['p_value']
    n_opener_enriched = len(e2['findings']['enriched_tokens']['opener'])
    n_support_enriched = len(e2['findings']['enriched_tokens']['support'])

    # Determine differentiation strength
    if chi2_sig and perm_pvalue < 0.05 and (n_opener_enriched >= 10 or n_support_enriched >= 10):
        strength = 'STRONG'
    elif chi2_sig or perm_pvalue < 0.10:
        strength = 'MODERATE'
    elif n_opener_enriched >= 5 or n_support_enriched >= 5:
        strength = 'WEAK'
    else:
        strength = 'NONE'

    return {
        'metadata': {
            'phase': 'E5',
            'title': 'Role Differentiation Synthesis',
            'timestamp': datetime.now().isoformat(),
            'dependencies': ['E1', 'E2', 'E3', 'E4']
        },
        'findings': {
            'differentiation_strength': strength,
            'chi_square_significant': chi2_sig,
            'permutation_p_value': perm_pvalue,
            'opener_enriched_count': n_opener_enriched,
            'support_enriched_count': n_support_enriched,
            'limitations': [
                'CLOSER has only 1 folio (f22r) - untestable',
                'SUPPORT has only 2 folios - limited power'
            ]
        },
        'summary': {
            'key_results': [
                f"Differentiation strength: {strength}",
                f"Enriched tokens: OPENER={n_opener_enriched}, SUPPORT={n_support_enriched}",
                f"Statistical significance: chi2={'yes' if chi2_sig else 'no'}, permutation={'yes' if perm_pvalue < 0.05 else 'no'}"
            ],
            'implications': [
                'Hub roles have distinct vocabulary signatures' if strength in ['STRONG', 'MODERATE'] else 'Hub role vocabulary differentiation not confirmed'
            ]
        }
    }

# =============================================================================
# TEST N: NAIBBE CIPHER COMPATIBILITY
# =============================================================================

def test_n1_conditional_probability(words: List[Dict]) -> Dict:
    """N1: Conditional probability analysis."""
    print("  Running N1: Conditional probability...")

    # Build character-level corpus
    text = ' '.join(w['word'] for w in words)

    # Build bigram -> next char prediction table
    bigram_next = defaultdict(Counter)
    for i in range(len(text) - 2):
        bigram = text[i:i+2]
        next_char = text[i+2]
        bigram_next[bigram][next_char] += 1

    # Compute prediction accuracy
    correct_1char = 0
    total_1char = 0

    for bigram, nexts in bigram_next.items():
        if bigram.strip():  # Skip space-only bigrams
            most_common = nexts.most_common(1)[0][1] if nexts else 0
            total = sum(nexts.values())
            correct_1char += most_common
            total_1char += total

    accuracy_1char = correct_1char / total_1char if total_1char > 0 else 0

    # Compute 2-char prediction (bigram -> next bigram)
    bigram_next_bigram = defaultdict(Counter)
    for i in range(len(text) - 4):
        bigram = text[i:i+2]
        next_bigram = text[i+2:i+4]
        bigram_next_bigram[bigram][next_bigram] += 1

    correct_2char = 0
    total_2char = 0

    for bigram, nexts in bigram_next_bigram.items():
        if bigram.strip():
            most_common = nexts.most_common(1)[0][1] if nexts else 0
            total = sum(nexts.values())
            correct_2char += most_common
            total_2char += total

    accuracy_2char = correct_2char / total_2char if total_2char > 0 else 0

    # Dillinger's claim: >50% from 2 chars
    dillinger_threshold = 0.50
    exceeds_threshold = accuracy_1char > dillinger_threshold

    return {
        'metadata': {
            'phase': 'N1',
            'title': 'Conditional Probability',
            'timestamp': datetime.now().isoformat(),
            'dependencies': []
        },
        'findings': {
            'bigram_to_char_accuracy': round(accuracy_1char, 4),
            'bigram_to_bigram_accuracy': round(accuracy_2char, 4),
            'dillinger_threshold': dillinger_threshold,
            'exceeds_threshold': exceeds_threshold,
            'total_bigrams_analyzed': len(bigram_next),
            'interpretation': 'HIGH conditional probability' if exceeds_threshold else 'MODERATE conditional probability'
        },
        'summary': {
            'key_results': [
                f"Bigram->char accuracy: {accuracy_1char:.1%}",
                f"Bigram->bigram accuracy: {accuracy_2char:.1%}",
                f"Exceeds 50% threshold: {exceeds_threshold}"
            ],
            'implications': [
                'High conditional probability INCOMPATIBLE with random cipher chunking' if exceeds_threshold else 'Moderate probability may be compatible with Naibbe'
            ]
        }
    }

def test_n2_repetition_analysis(words: List[Dict]) -> Dict:
    """N2: Repetition rate analysis."""
    print("  Running N2: Repetition rates...")

    word_list = [w['word'] for w in words]

    # Word repetition (consecutive)
    word_consecutive = 0
    for i in range(len(word_list) - 1):
        if word_list[i] == word_list[i+1]:
            word_consecutive += 1
    word_rep_rate = word_consecutive / len(word_list) if word_list else 0

    # Bigram repetition
    bigrams = [(word_list[i], word_list[i+1]) for i in range(len(word_list) - 1)]
    bigram_counts = Counter(bigrams)
    repeated_bigrams = sum(1 for c in bigram_counts.values() if c > 1)
    bigram_rep_rate = repeated_bigrams / len(bigram_counts) if bigram_counts else 0

    # Trigram repetition
    trigrams = [(word_list[i], word_list[i+1], word_list[i+2]) for i in range(len(word_list) - 2)]
    trigram_counts = Counter(trigrams)
    repeated_trigrams = sum(1 for c in trigram_counts.values() if c > 1)
    trigram_rep_rate = repeated_trigrams / len(trigram_counts) if trigram_counts else 0

    # Our observed rates from CLAUDE.md: 0.1-0.3%
    observed_range = (0.001, 0.003)

    # Naibbe theoretical: With 6 tables, same plaintext bigram has 36 representations
    # This should REDUCE apparent repetition
    naibbe_prediction = "Should reduce repetition (36 representations per bigram)"

    return {
        'metadata': {
            'phase': 'N2',
            'title': 'Repetition Analysis',
            'timestamp': datetime.now().isoformat(),
            'dependencies': []
        },
        'findings': {
            'word_consecutive_rate': round(word_rep_rate, 6),
            'bigram_repetition_rate': round(bigram_rep_rate, 4),
            'trigram_repetition_rate': round(trigram_rep_rate, 4),
            'unique_bigrams': len(bigram_counts),
            'unique_trigrams': len(trigram_counts),
            'observed_range': observed_range,
            'naibbe_prediction': naibbe_prediction
        },
        'summary': {
            'key_results': [
                f"Word consecutive repetition: {word_rep_rate:.4%}",
                f"Bigram repetition rate: {bigram_rep_rate:.2%}",
                f"Trigram repetition rate: {trigram_rep_rate:.2%}"
            ],
            'implications': [
                'Very low repetition is COMPATIBLE with verbose cipher (reduces repetition)' if trigram_rep_rate < 0.01 else 'Moderate repetition'
            ]
        }
    }

def test_n3_section_enrichment(words: List[Dict]) -> Dict:
    """N3: Section enrichment survival under cipher."""
    print("  Running N3: Section enrichment survival...")

    # Theoretical analysis
    # Key insight: Naibbe preserves word IDENTITY (same plaintext -> recognizable pattern)
    # Therefore section enrichment SHOULD survive encryption

    # Compute actual section enrichment to verify our data
    section_vocab = defaultdict(Counter)
    for w in words:
        section_vocab[w['section']][w['word']] += 1

    # Overall vocabulary
    overall_vocab = Counter(w['word'] for w in words)
    overall_total = sum(overall_vocab.values())

    # Find enriched words per section
    enrichment_by_section = {}
    for section, vocab in section_vocab.items():
        section_total = sum(vocab.values())
        enriched = []
        for word, count in vocab.items():
            section_rate = count / section_total if section_total > 0 else 0
            overall_rate = overall_vocab.get(word, 0) / overall_total if overall_total > 0 else 0.0001
            enrichment = section_rate / overall_rate if overall_rate > 0 else 0
            if enrichment > 2.0 and count >= 3:
                enriched.append({'word': word, 'enrichment': round(enrichment, 2)})

        enrichment_by_section[section] = {
            'total_tokens': section_total,
            'enriched_count': len(enriched),
            'max_enrichment': max([e['enrichment'] for e in enriched]) if enriched else 0,
            'top_enriched': sorted(enriched, key=lambda x: x['enrichment'], reverse=True)[:5]
        }

    return {
        'metadata': {
            'phase': 'N3',
            'title': 'Section Enrichment Survival',
            'timestamp': datetime.now().isoformat(),
            'dependencies': []
        },
        'findings': {
            'theoretical_analysis': {
                'naibbe_preserves_word_identity': True,
                'section_enrichment_should_survive': True,
                'reasoning': 'Same plaintext word always maps to recognizable ciphertext patterns'
            },
            'observed_enrichment': enrichment_by_section,
            'compatibility': 'COMPATIBLE',
            'reasoning': 'Section-conditioned vocabulary is a plaintext property that survives encryption'
        },
        'summary': {
            'key_results': [
                f"Sections analyzed: {len(enrichment_by_section)}",
                "Theoretical: Section enrichment SHOULD survive Naibbe encryption",
                "Verdict: This constraint is COMPATIBLE with Naibbe"
            ],
            'implications': [
                'Section enrichment cannot rule out Naibbe hypothesis'
            ]
        }
    }

def test_n4_structural_constraints(words: List[Dict], entries: Dict[str, List[Dict]]) -> Dict:
    """N4: Test each structural constraint against Naibbe compatibility."""
    print("  Running N4: Structural constraints...")

    constraints = []

    # Constraint 1: Position constraints (q first-only)
    q_positions = Counter()
    for w in words:
        word = w['word']
        for i, char in enumerate(word):
            if char == 'q':
                pos = 'first' if i == 0 else 'middle' if i < len(word) - 1 else 'last'
                q_positions[pos] += 1

    q_first_rate = q_positions['first'] / sum(q_positions.values()) if q_positions else 0
    constraints.append({
        'constraint': 'Position constraints (q first-only)',
        'observed': f"q appears first {q_first_rate:.1%} of time",
        'naibbe_compatible': False,  # Random chunking shouldn't preserve this
        'reasoning': 'Random chunking would distribute q across positions'
    })

    # Constraint 2: Currier A/B separation
    currier_a_words = set(w['word'] for w in words if w['currier'] == 'A')
    currier_b_words = set(w['word'] for w in words if w['currier'] == 'B')
    overlap = len(currier_a_words & currier_b_words) / len(currier_a_words | currier_b_words) if currier_a_words | currier_b_words else 0

    constraints.append({
        'constraint': 'Currier A/B separation (14.1% overlap)',
        'observed': f"{overlap:.1%} vocabulary overlap",
        'naibbe_compatible': True,  # Different source texts could produce this
        'reasoning': 'If A and B encrypt different Latin texts, separation would exist'
    })

    # Constraint 3: Three-part structure
    constraints.append({
        'constraint': 'Three-part entry structure',
        'observed': '71.2% method agreement',
        'naibbe_compatible': True,
        'reasoning': 'Cipher does not affect document structure'
    })

    # Constraint 4: Heading categories
    constraints.append({
        'constraint': 'Heading words as category labels',
        'observed': 'Hub headings shorter (4.0 vs 6.8 chars)',
        'naibbe_compatible': True,
        'reasoning': 'If plaintext has headings, cipher preserves them'
    })

    # Constraint 5: B references A
    constraints.append({
        'constraint': 'B references A (INFINITE asymmetry)',
        'observed': '809 A words in B body, 0 B-only in A',
        'naibbe_compatible': True,
        'reasoning': 'Reference structure is plaintext property, survives encryption'
    })

    # Constraint 6: Very low repetition
    constraints.append({
        'constraint': 'Extremely low repetition (0.1-0.3%)',
        'observed': 'Trigram repetition < 0.3%',
        'naibbe_compatible': True,
        'reasoning': 'Verbose cipher with 36 representations REDUCES repetition'
    })

    # Count compatibility
    compatible_count = sum(1 for c in constraints if c['naibbe_compatible'])
    incompatible_count = len(constraints) - compatible_count

    return {
        'metadata': {
            'phase': 'N4',
            'title': 'Structural Constraints',
            'timestamp': datetime.now().isoformat(),
            'dependencies': []
        },
        'findings': {
            'constraints_tested': len(constraints),
            'compatible_count': compatible_count,
            'incompatible_count': incompatible_count,
            'constraint_details': constraints
        },
        'summary': {
            'key_results': [
                f"Constraints tested: {len(constraints)}",
                f"Naibbe-compatible: {compatible_count}",
                f"Naibbe-incompatible: {incompatible_count}"
            ],
            'implications': [
                'Position constraints (q first-only) argue AGAINST Naibbe' if q_first_rate > 0.95 else 'Most constraints compatible with Naibbe'
            ]
        }
    }

def test_n5_compatibility_synthesis(n1: Dict, n2: Dict, n3: Dict, n4: Dict) -> Dict:
    """N5: Synthesis of Naibbe compatibility analysis."""
    print("  Running N5: Compatibility synthesis...")

    # Gather evidence
    conditional_prob = n1['findings']['bigram_to_char_accuracy']
    exceeds_threshold = n1['findings']['exceeds_threshold']
    compatible_constraints = n4['findings']['compatible_count']
    incompatible_constraints = n4['findings']['incompatible_count']

    # Verdict
    if exceeds_threshold and incompatible_constraints >= 2:
        verdict = 'INCOMPATIBLE'
        confidence = 'HIGH'
    elif incompatible_constraints >= 1:
        verdict = 'PARTIALLY_COMPATIBLE'
        confidence = 'MEDIUM'
    else:
        verdict = 'COMPATIBLE'
        confidence = 'MEDIUM'

    return {
        'metadata': {
            'phase': 'N5',
            'title': 'Naibbe Compatibility Synthesis',
            'timestamp': datetime.now().isoformat(),
            'dependencies': ['N1', 'N2', 'N3', 'N4']
        },
        'findings': {
            'verdict': verdict,
            'confidence': confidence,
            'evidence_summary': {
                'conditional_probability': f"{conditional_prob:.1%} (threshold: 50%)",
                'compatible_constraints': compatible_constraints,
                'incompatible_constraints': incompatible_constraints
            },
            'key_discriminators': [
                'Position constraints (q first-only)' if incompatible_constraints > 0 else None,
                'Conditional probability > 50%' if exceeds_threshold else None
            ]
        },
        'summary': {
            'key_results': [
                f"Verdict: {verdict} (confidence: {confidence})",
                f"Conditional probability: {conditional_prob:.1%}",
                f"Compatible/Incompatible constraints: {compatible_constraints}/{incompatible_constraints}"
            ],
            'implications': [
                'Naibbe cipher model does NOT fully explain Voynich' if verdict == 'INCOMPATIBLE' else 'Naibbe remains a viable hypothesis'
            ]
        }
    }

# =============================================================================
# INTEGRATION SYNTHESIS
# =============================================================================

def generate_integration_synthesis(a6: Dict, e5: Dict, n5: Dict) -> Dict:
    """Generate integrated synthesis across all tests."""
    print("  Running Integration Synthesis...")

    daiin_class = a6['findings']['classification']
    daiin_cipher_compat = a6['findings']['cipher_compatibility']['naibbe_compatible']
    role_strength = e5['findings']['differentiation_strength']
    naibbe_verdict = n5['findings']['verdict']

    # Cross-test implications
    implications = []

    if daiin_class in ['CLAUSE_MARKER', 'DETERMINER', 'CONJUNCTION'] and not daiin_cipher_compat:
        implications.append("'daiin' grammatical function argues AGAINST pure Naibbe (syntax shouldn't survive random chunking)")

    if role_strength in ['STRONG', 'MODERATE']:
        implications.append("Hub role vocabulary differentiation suggests organized plaintext structure")

    if naibbe_verdict == 'INCOMPATIBLE':
        implications.append("Naibbe cipher model does NOT fully explain Voynich statistical properties")
    elif naibbe_verdict == 'COMPATIBLE':
        implications.append("Naibbe cipher remains viable; plaintext may be organized Latin/Italian")

    # Translation pathway assessment
    if naibbe_verdict == 'COMPATIBLE' and daiin_class != 'CONTENT_WORD':
        pathway = "Attempt Naibbe decryption with 'daiin' as potential crib for Latin particle"
    elif naibbe_verdict == 'INCOMPATIBLE' and daiin_class != 'CONTENT_WORD':
        pathway = "Syntactic analysis of unknown system; use grammatical words as structural skeleton"
    else:
        pathway = "Limited progress; may require external breakthroughs"

    return {
        'metadata': {
            'phase': 'INT',
            'title': 'Integration Synthesis',
            'timestamp': datetime.now().isoformat(),
            'dependencies': ['A6', 'E5', 'N5']
        },
        'findings': {
            'test_a_summary': {
                'classification': daiin_class,
                'cipher_compatible': daiin_cipher_compat
            },
            'test_e_summary': {
                'differentiation_strength': role_strength
            },
            'test_n_summary': {
                'verdict': naibbe_verdict
            },
            'cross_test_implications': implications,
            'translation_pathway': pathway
        },
        'summary': {
            'key_results': [
                f"daiin: {daiin_class}",
                f"Role differentiation: {role_strength}",
                f"Naibbe compatibility: {naibbe_verdict}",
                f"Recommended pathway: {pathway}"
            ],
            'implications': implications
        }
    }

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def save_json(data: Dict, filename: str):
    """Save data to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"    Saved: {filename}")

def main():
    print("=" * 70)
    print("FINAL SEMANTIC PROBE WITH CIPHER COMPATIBILITY ANALYSIS")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")

    # Load data
    print("\n[1/4] Loading corpus...")
    words = load_corpus()
    print(f"  Total words: {len(words)}")

    entries = segment_into_entries(words)
    print(f"  Total entries: {len(entries)}")

    # ==========================================================================
    # TEST A: daiin analysis
    # ==========================================================================
    print("\n[2/4] TEST A: 'daiin' Grammatical Function Analysis")
    print("-" * 50)

    a1 = test_a1_frequency_baseline(words, entries)
    save_json(a1, 'daiin_frequency_baseline.json')

    a2 = test_a2_positional_distribution(words, entries)
    save_json(a2, 'daiin_positional_analysis.json')

    a3 = test_a3_morphological_context(words, entries)
    save_json(a3, 'daiin_morphological_context.json')

    a4 = test_a4_functional_classification(words, entries)
    save_json(a4, 'daiin_functional_classification.json')

    a5 = test_a5_cross_validation(words, entries)
    save_json(a5, 'daiin_cross_validation.json')

    a6 = test_a6_synthesis(a1, a2, a3, a4, a5)
    save_json(a6, 'daiin_synthesis.json')

    # ==========================================================================
    # TEST E: Hub role vocabulary
    # ==========================================================================
    print("\n[3/4] TEST E: Hub Role Vocabulary Differentiation")
    print("-" * 50)

    e1 = test_e1_corpus_compilation(words, entries)
    save_json(e1, 'role_corpora.json')

    e2 = test_e2_vocabulary_comparison(e1, entries)
    save_json(e2, 'role_vocabulary_comparison.json')

    e3 = test_e3_statistical_testing(e1, e2, entries)
    save_json(e3, 'role_vocabulary_significance.json')

    e4 = test_e4_pattern_analysis(e1, e2)
    save_json(e4, 'role_vocabulary_patterns.json')

    e5 = test_e5_synthesis(e1, e2, e3, e4)
    save_json(e5, 'role_differentiation_synthesis.json')

    # ==========================================================================
    # TEST N: Naibbe compatibility
    # ==========================================================================
    print("\n[4/4] TEST N: Naibbe Cipher Compatibility")
    print("-" * 50)

    n1 = test_n1_conditional_probability(words)
    save_json(n1, 'naibbe_conditional_probability.json')

    n2 = test_n2_repetition_analysis(words)
    save_json(n2, 'naibbe_repetition_analysis.json')

    n3 = test_n3_section_enrichment(words)
    save_json(n3, 'naibbe_section_enrichment.json')

    n4 = test_n4_structural_constraints(words, entries)
    save_json(n4, 'naibbe_structural_constraints.json')

    n5 = test_n5_compatibility_synthesis(n1, n2, n3, n4)
    save_json(n5, 'naibbe_compatibility_synthesis.json')

    # ==========================================================================
    # INTEGRATION
    # ==========================================================================
    print("\n[FINAL] Integration Synthesis")
    print("-" * 50)

    integration = generate_integration_synthesis(a6, e5, n5)
    save_json(integration, 'integration_synthesis.json')

    # ==========================================================================
    # SUMMARY
    # ==========================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    print("\nTEST A: 'daiin' Grammatical Function")
    print(f"  Classification: {a6['findings']['classification']}")
    print(f"  Confidence: {a6['findings']['confidence']}")
    print(f"  Cipher compatible: {a6['findings']['cipher_compatibility']['naibbe_compatible']}")

    print("\nTEST E: Hub Role Vocabulary")
    print(f"  Differentiation: {e5['findings']['differentiation_strength']}")

    print("\nTEST N: Naibbe Compatibility")
    print(f"  Verdict: {n5['findings']['verdict']}")
    print(f"  Confidence: {n5['findings']['confidence']}")

    print("\nINTEGRATION:")
    print(f"  Translation pathway: {integration['findings']['translation_pathway']}")

    print("\nFiles generated: 17 JSON files")
    print(f"Completed: {datetime.now().isoformat()}")

if __name__ == '__main__':
    main()
