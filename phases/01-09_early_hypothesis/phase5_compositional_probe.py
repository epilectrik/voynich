#!/usr/bin/env python3
"""
Phase 5: Compositional Decoding Probe

Reverse-engineer the compositional encoding: MODIFIER₁ + CORE + MODIFIER₂

We're reconstructing a compiler, not guessing a language.

Experiments:
1. Middle Extraction & Clustering
2. Affix Function Analysis
3. Slot Structure Detection
4. Middle Embedding (optional)

Output: phase5_*.json files
"""

import csv
import json
import math
from collections import defaultdict, Counter
from datetime import datetime
from typing import List, Dict, Tuple, Set, Optional
import numpy as np
from itertools import combinations

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

# =============================================================================
# DATA LOADING
# =============================================================================

def load_corpus() -> List[Dict]:
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
                    'section': section
                })

    return words

def load_gamma_tokens() -> Set[str]:
    """Load GAMMA layer tokens from Phase 2A."""
    try:
        with open('phase2a_layer_assignments.json', 'r') as f:
            data = json.load(f)
            return set(data.get('layer_populations', {}).get('GAMMA', []))
    except FileNotFoundError:
        print("Warning: phase2a_layer_assignments.json not found")
        return set()

def segment_into_entries(words: List[Dict]) -> Dict[str, List[Dict]]:
    by_folio = defaultdict(list)
    for w in words:
        by_folio[w['folio']].append(w)
    return dict(by_folio)

# =============================================================================
# MUTUAL INFORMATION CALCULATION
# =============================================================================

def calculate_mi(sequence: List[str]) -> float:
    """Calculate mutual information between adjacent tokens."""
    if len(sequence) < 2:
        return 0.0

    # Count bigrams and unigrams
    bigram_counts = Counter()
    unigram_counts = Counter()

    for i in range(len(sequence) - 1):
        bigram_counts[(sequence[i], sequence[i+1])] += 1
        unigram_counts[sequence[i]] += 1
    unigram_counts[sequence[-1]] += 1

    total_bigrams = sum(bigram_counts.values())
    total_unigrams = sum(unigram_counts.values())

    if total_bigrams == 0:
        return 0.0

    # Calculate MI
    mi = 0.0
    for (a, b), count in bigram_counts.items():
        p_ab = count / total_bigrams
        p_a = unigram_counts[a] / total_unigrams
        p_b = unigram_counts[b] / total_unigrams

        if p_ab > 0 and p_a > 0 and p_b > 0:
            mi += p_ab * math.log2(p_ab / (p_a * p_b))

    return mi

def calculate_entropy(counts: Counter) -> float:
    """Calculate Shannon entropy."""
    total = sum(counts.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    return entropy

# =============================================================================
# EXPERIMENT 1: MIDDLE EXTRACTION & CLUSTERING
# =============================================================================

def extract_middle(word: str, prefix_len: int, suffix_len: int) -> Optional[str]:
    """Extract middle after removing prefix and suffix of given lengths."""
    if len(word) <= prefix_len + suffix_len:
        return None
    middle = word[prefix_len:-suffix_len] if suffix_len > 0 else word[prefix_len:]
    return middle if middle else None

def find_best_known_prefix(word: str) -> Tuple[str, int]:
    """Find the best matching known prefix."""
    for length in [3, 2]:
        if len(word) >= length:
            prefix = word[:length]
            if prefix in KNOWN_PREFIXES:
                return prefix, length
    return word[:2] if len(word) >= 2 else word, min(2, len(word))

def find_best_known_suffix(word: str) -> Tuple[str, int]:
    """Find the best matching known suffix."""
    for length in [4, 3, 2, 1]:
        if len(word) >= length:
            suffix = word[-length:]
            if suffix in KNOWN_SUFFIXES:
                return suffix, length
    return word[-1] if len(word) >= 1 else '', min(1, len(word))

def experiment1_middle_extraction(words: List[Dict]) -> Dict:
    """
    Extract semantic cores by stripping affixes.
    Test multiple stripping windows to find the method that preserves most MI.
    """
    print("\n" + "="*60)
    print("EXPERIMENT 1: Middle Extraction & Clustering")
    print("="*60)

    # Get word sequence
    word_sequence = [w['word'] for w in words]
    unique_tokens = set(word_sequence)

    # Baseline MI
    baseline_mi = calculate_mi(word_sequence)
    print(f"Baseline MI (full tokens): {baseline_mi:.4f}")
    print(f"Unique tokens: {len(unique_tokens)}")

    results = {
        'baseline_mi': baseline_mi,
        'unique_tokens': len(unique_tokens),
        'stripping_methods': {},
        'best_method': None,
        'middle_stability': {},
        'shell_analysis': {}
    }

    # Test different stripping methods
    stripping_methods = [
        ('fixed_1_1', 1, 1),
        ('fixed_2_1', 2, 1),
        ('fixed_2_2', 2, 2),
        ('fixed_3_1', 3, 1),
        ('fixed_3_2', 3, 2),
        ('known_affixes', None, None),  # Use known prefix/suffix lists
    ]

    best_mi_ratio = 0
    best_method = None

    for method_name, prefix_len, suffix_len in stripping_methods:
        print(f"\n--- Method: {method_name} ---")

        middle_sequence = []
        middle_to_shells = defaultdict(set)  # middle -> set of full tokens containing it

        for token in word_sequence:
            if method_name == 'known_affixes':
                # Use known affix lists
                _, p_len = find_best_known_prefix(token)
                _, s_len = find_best_known_suffix(token)
                middle = extract_middle(token, p_len, s_len)
            else:
                middle = extract_middle(token, prefix_len, suffix_len)

            if middle:
                middle_sequence.append(middle)
                middle_to_shells[middle].add(token)
            else:
                # Token too short, use as-is
                middle_sequence.append(token)
                middle_to_shells[token].add(token)

        # Calculate MI for middle sequence
        middle_mi = calculate_mi(middle_sequence)
        mi_ratio = middle_mi / baseline_mi if baseline_mi > 0 else 0

        unique_middles = set(middle_sequence)
        middle_counts = Counter(middle_sequence)
        middle_entropy = calculate_entropy(middle_counts)

        # Shell distribution
        shell_counts = [len(shells) for shells in middle_to_shells.values()]
        shell_distribution = Counter(shell_counts)

        print(f"  MI: {middle_mi:.4f} (ratio: {mi_ratio:.2%})")
        print(f"  Unique middles: {len(unique_middles)}")
        print(f"  Entropy: {middle_entropy:.4f}")
        print(f"  Middles in 1 shell: {shell_distribution.get(1, 0)}")
        print(f"  Middles in 2+ shells: {sum(v for k,v in shell_distribution.items() if k >= 2)}")

        results['stripping_methods'][method_name] = {
            'mi': middle_mi,
            'mi_preservation_ratio': mi_ratio,
            'unique_middles': len(unique_middles),
            'entropy': middle_entropy,
            'shell_distribution': dict(shell_distribution),
            'vocabulary_reduction': 1 - len(unique_middles) / len(unique_tokens)
        }

        if mi_ratio > best_mi_ratio:
            best_mi_ratio = mi_ratio
            best_method = method_name
            results['middle_stability'] = {
                'middles_in_multiple_shells': sum(v for k,v in shell_distribution.items() if k >= 2),
                'middles_in_single_shell': shell_distribution.get(1, 0),
                'top_multi_shell_middles': sorted(
                    [(m, len(s)) for m, s in middle_to_shells.items() if len(s) >= 3],
                    key=lambda x: -x[1]
                )[:20]
            }
            results['shell_analysis'] = {
                middle: list(shells)[:10]
                for middle, shells in sorted(middle_to_shells.items(), key=lambda x: -len(x[1]))[:30]
            }

    results['best_method'] = best_method
    results['best_mi_preservation'] = best_mi_ratio

    print(f"\n*** Best method: {best_method} (MI preservation: {best_mi_ratio:.2%}) ***")

    return results

# =============================================================================
# EXPERIMENT 2: AFFIX FUNCTION ANALYSIS
# =============================================================================

def experiment2_affix_functions(words: List[Dict], entries: Dict[str, List[Dict]]) -> Dict:
    """
    Determine what prefixes and suffixes DO statistically.
    """
    print("\n" + "="*60)
    print("EXPERIMENT 2: Affix Function Analysis")
    print("="*60)

    results = {
        'prefix_suffix_cooccurrence': {},
        'prefix_positional_correlation': {},
        'suffix_positional_correlation': {},
        'within_group_mi': {},
        'structural_vs_semantic_affixes': {}
    }

    # Extract all prefix/suffix pairs
    prefix_suffix_pairs = Counter()
    prefix_counts = Counter()
    suffix_counts = Counter()

    # Positional data
    prefix_positions = defaultdict(list)  # prefix -> list of (entry_position, word_idx)
    suffix_positions = defaultdict(list)

    # Group tokens by prefix/suffix
    tokens_by_prefix = defaultdict(list)
    tokens_by_suffix = defaultdict(list)

    for folio, entry in entries.items():
        entry_len = len(entry)
        for idx, w in enumerate(entry):
            token = w['word']
            prefix, _ = find_best_known_prefix(token)
            suffix, _ = find_best_known_suffix(token)

            prefix_suffix_pairs[(prefix, suffix)] += 1
            prefix_counts[prefix] += 1
            suffix_counts[suffix] += 1

            # Relative position in entry (0-1)
            rel_pos = idx / entry_len if entry_len > 0 else 0.5

            prefix_positions[prefix].append(rel_pos)
            suffix_positions[suffix].append(rel_pos)

            tokens_by_prefix[prefix].append(token)
            tokens_by_suffix[suffix].append(token)

    # 1. Co-occurrence matrix (top combinations)
    print("\n--- Prefix-Suffix Co-occurrence ---")
    top_pairs = prefix_suffix_pairs.most_common(30)
    print(f"Top 10 pairs: {top_pairs[:10]}")

    # Calculate expected vs observed for forbidden/preferred
    total_pairs = sum(prefix_suffix_pairs.values())
    preference_matrix = {}

    for (prefix, suffix), observed in prefix_suffix_pairs.items():
        if prefix_counts[prefix] < 10 or suffix_counts[suffix] < 10:
            continue
        expected = (prefix_counts[prefix] * suffix_counts[suffix]) / total_pairs
        if expected > 0:
            ratio = observed / expected
            preference_matrix[(prefix, suffix)] = {
                'observed': observed,
                'expected': round(expected, 2),
                'ratio': round(ratio, 3)
            }

    # Find forbidden combinations (ratio < 0.3) and preferred (ratio > 3)
    forbidden = [(k, v) for k, v in preference_matrix.items() if v['ratio'] < 0.3]
    preferred = [(k, v) for k, v in preference_matrix.items() if v['ratio'] > 3.0]

    print(f"Forbidden combinations (ratio < 0.3): {len(forbidden)}")
    print(f"Preferred combinations (ratio > 3.0): {len(preferred)}")

    results['prefix_suffix_cooccurrence'] = {
        'top_30_pairs': [(f"{p[0]}-{p[1]}", c) for p, c in top_pairs],
        'forbidden_combinations': [(f"{k[0]}-{k[1]}", v) for k, v in sorted(forbidden, key=lambda x: x[1]['ratio'])[:20]],
        'preferred_combinations': [(f"{k[0]}-{k[1]}", v) for k, v in sorted(preferred, key=lambda x: -x[1]['ratio'])[:20]]
    }

    # 2. Positional correlation
    print("\n--- Positional Correlation ---")

    for prefix, positions in prefix_positions.items():
        if len(positions) >= 50:
            mean_pos = np.mean(positions)
            std_pos = np.std(positions)
            entry_initial_rate = sum(1 for p in positions if p < 0.1) / len(positions)
            entry_final_rate = sum(1 for p in positions if p > 0.9) / len(positions)

            results['prefix_positional_correlation'][prefix] = {
                'count': len(positions),
                'mean_position': round(mean_pos, 3),
                'std_position': round(std_pos, 3),
                'entry_initial_rate': round(entry_initial_rate, 3),
                'entry_final_rate': round(entry_final_rate, 3)
            }

    for suffix, positions in suffix_positions.items():
        if len(positions) >= 50:
            mean_pos = np.mean(positions)
            std_pos = np.std(positions)
            entry_initial_rate = sum(1 for p in positions if p < 0.1) / len(positions)
            entry_final_rate = sum(1 for p in positions if p > 0.9) / len(positions)

            results['suffix_positional_correlation'][suffix] = {
                'count': len(positions),
                'mean_position': round(mean_pos, 3),
                'std_position': round(std_pos, 3),
                'entry_initial_rate': round(entry_initial_rate, 3),
                'entry_final_rate': round(entry_final_rate, 3)
            }

    # Find strongly positional affixes
    initial_prefixes = [(p, d) for p, d in results['prefix_positional_correlation'].items()
                        if d['entry_initial_rate'] > 0.15]
    final_suffixes = [(s, d) for s, d in results['suffix_positional_correlation'].items()
                      if d['entry_final_rate'] > 0.15]

    print(f"Entry-initial prefixes (>15%): {[p for p,_ in initial_prefixes]}")
    print(f"Entry-final suffixes (>15%): {[s for s,_ in final_suffixes]}")

    # 3. Within-group MI
    print("\n--- Within-Group MI ---")

    for prefix, tokens in tokens_by_prefix.items():
        if len(tokens) >= 100:
            mi = calculate_mi(tokens)
            results['within_group_mi'][f'prefix_{prefix}'] = {
                'count': len(tokens),
                'mi': round(mi, 4)
            }

    for suffix, tokens in tokens_by_suffix.items():
        if len(tokens) >= 100:
            mi = calculate_mi(tokens)
            results['within_group_mi'][f'suffix_{suffix}'] = {
                'count': len(tokens),
                'mi': round(mi, 4)
            }

    # Sort by MI
    sorted_by_mi = sorted(results['within_group_mi'].items(), key=lambda x: -x[1]['mi'])
    print(f"Top 10 by within-group MI: {sorted_by_mi[:10]}")

    # 4. Classify as structural vs semantic
    print("\n--- Structural vs Semantic Classification ---")

    # Structural: low within-group MI but strong positional bias
    # Semantic: high within-group MI, less positional constraint

    structural_affixes = []
    semantic_affixes = []

    for affix, mi_data in results['within_group_mi'].items():
        mi = mi_data['mi']
        affix_type = affix.split('_')[0]
        affix_name = affix.split('_')[1]

        if affix_type == 'prefix' and affix_name in results['prefix_positional_correlation']:
            pos_data = results['prefix_positional_correlation'][affix_name]
            positional_bias = max(pos_data['entry_initial_rate'], pos_data['entry_final_rate'])
        elif affix_type == 'suffix' and affix_name in results['suffix_positional_correlation']:
            pos_data = results['suffix_positional_correlation'][affix_name]
            positional_bias = max(pos_data['entry_initial_rate'], pos_data['entry_final_rate'])
        else:
            positional_bias = 0

        classification = {
            'affix': affix,
            'mi': mi,
            'positional_bias': round(positional_bias, 3),
            'classification': None
        }

        if mi < 0.3 and positional_bias > 0.1:
            classification['classification'] = 'STRUCTURAL'
            structural_affixes.append(classification)
        elif mi > 0.4:
            classification['classification'] = 'SEMANTIC'
            semantic_affixes.append(classification)
        else:
            classification['classification'] = 'MIXED'

    results['structural_vs_semantic_affixes'] = {
        'structural': structural_affixes,
        'semantic': semantic_affixes
    }

    print(f"Structural affixes: {len(structural_affixes)}")
    print(f"Semantic affixes: {len(semantic_affixes)}")

    return results

# =============================================================================
# EXPERIMENT 3: SLOT STRUCTURE DETECTION
# =============================================================================

def experiment3_slot_structure(words: List[Dict], entries: Dict[str, List[Dict]], gamma_tokens: Set[str]) -> Dict:
    """
    Test if GAMMA tokens fill fixed positional slots within entries.
    """
    print("\n" + "="*60)
    print("EXPERIMENT 3: Slot Structure Detection")
    print("="*60)

    results = {
        'per_slot_vocabulary': {},
        'slot_transitions': {},
        'affix_slot_correlation': {},
        'prediction_test': {}
    }

    # Extract GAMMA token positions within entries
    max_slots = 10  # Analyze first 10 GAMMA positions
    slot_vocabularies = defaultdict(Counter)
    slot_prefixes = defaultdict(Counter)
    slot_suffixes = defaultdict(Counter)
    slot_middles = defaultdict(Counter)

    # Transitions between slots
    slot_transitions = defaultdict(Counter)  # (slot_i, slot_j) -> token transitions

    all_gamma_sequences = []

    for folio, entry in entries.items():
        # Extract GAMMA tokens with positions
        gamma_positions = []
        for idx, w in enumerate(entry):
            if w['word'] in gamma_tokens:
                gamma_positions.append((idx, w['word']))

        if len(gamma_positions) < 2:
            continue

        # Record slot vocabularies
        for slot_idx, (pos, token) in enumerate(gamma_positions[:max_slots]):
            slot_vocabularies[slot_idx][token] += 1

            prefix, p_len = find_best_known_prefix(token)
            suffix, s_len = find_best_known_suffix(token)
            middle = extract_middle(token, p_len, s_len) or token

            slot_prefixes[slot_idx][prefix] += 1
            slot_suffixes[slot_idx][suffix] += 1
            slot_middles[slot_idx][middle] += 1

        # Record transitions
        for i in range(min(len(gamma_positions) - 1, max_slots - 1)):
            token_from = gamma_positions[i][1]
            token_to = gamma_positions[i + 1][1]
            slot_transitions[(i, i + 1)][(token_from, token_to)] += 1

        # Store sequence for later analysis
        all_gamma_sequences.append([t for _, t in gamma_positions])

    # 1. Per-slot vocabulary analysis
    print("\n--- Per-Slot Vocabulary ---")

    for slot in range(max_slots):
        if slot not in slot_vocabularies:
            continue

        vocab = slot_vocabularies[slot]
        entropy = calculate_entropy(vocab)

        results['per_slot_vocabulary'][f'slot_{slot}'] = {
            'unique_tokens': len(vocab),
            'total_occurrences': sum(vocab.values()),
            'entropy': round(entropy, 4),
            'top_10_tokens': vocab.most_common(10),
            'top_5_prefixes': slot_prefixes[slot].most_common(5),
            'top_5_suffixes': slot_suffixes[slot].most_common(5),
            'top_5_middles': slot_middles[slot].most_common(5)
        }

        print(f"Slot {slot}: {len(vocab)} unique tokens, entropy={entropy:.3f}")

    # 2. Slot transition analysis
    print("\n--- Slot Transitions ---")

    for (slot_from, slot_to), transitions in slot_transitions.items():
        total = sum(transitions.values())
        unique_transitions = len(transitions)

        # Calculate transition entropy
        trans_entropy = calculate_entropy(transitions)

        # Calculate constraint ratio
        max_possible = len(slot_vocabularies[slot_from]) * len(slot_vocabularies[slot_to])
        constraint_ratio = 1 - (unique_transitions / max_possible) if max_possible > 0 else 0

        results['slot_transitions'][f'{slot_from}_to_{slot_to}'] = {
            'total_transitions': total,
            'unique_transitions': unique_transitions,
            'max_possible': max_possible,
            'constraint_ratio': round(constraint_ratio, 3),
            'entropy': round(trans_entropy, 4),
            'top_10_transitions': [
                (f"{t[0]}->{t[1]}", c) for t, c in transitions.most_common(10)
            ]
        }

        print(f"Slot {slot_from}->{slot_to}: {unique_transitions}/{max_possible} transitions (constraint={constraint_ratio:.2%})")

    # 3. Affix-slot correlation
    print("\n--- Affix-Slot Correlation ---")

    # Check if certain prefixes dominate certain slots
    prefix_slot_matrix = {}
    for slot in range(max_slots):
        if slot not in slot_prefixes:
            continue
        total = sum(slot_prefixes[slot].values())
        for prefix, count in slot_prefixes[slot].items():
            rate = count / total if total > 0 else 0
            if prefix not in prefix_slot_matrix:
                prefix_slot_matrix[prefix] = {}
            prefix_slot_matrix[prefix][slot] = round(rate, 3)

    # Find prefixes with strong slot preference
    slot_preferring_prefixes = []
    for prefix, slot_rates in prefix_slot_matrix.items():
        max_rate = max(slot_rates.values())
        min_rate = min(slot_rates.values()) if len(slot_rates) > 1 else max_rate
        if max_rate > 0.3 and (max_rate - min_rate) > 0.2:
            preferred_slot = max(slot_rates.items(), key=lambda x: x[1])[0]
            slot_preferring_prefixes.append({
                'prefix': prefix,
                'preferred_slot': preferred_slot,
                'max_rate': max_rate,
                'rate_range': round(max_rate - min_rate, 3)
            })

    results['affix_slot_correlation'] = {
        'prefix_slot_matrix': prefix_slot_matrix,
        'slot_preferring_prefixes': sorted(slot_preferring_prefixes, key=lambda x: -x['rate_range'])
    }

    print(f"Prefixes with slot preference: {len(slot_preferring_prefixes)}")

    # 4. Prediction test
    print("\n--- Prediction Test ---")

    # Does (slot + middle) predict context better than token alone?
    # We'll measure whether knowing the slot improves prediction of next token

    # Token-only prediction
    token_only_transitions = Counter()
    for seq in all_gamma_sequences:
        for i in range(len(seq) - 1):
            token_only_transitions[(seq[i], seq[i+1])] += 1

    token_only_mi = calculate_mi([t for seq in all_gamma_sequences for t in seq])

    # Slot-conditioned prediction (already calculated above via slot transitions)
    slot_conditioned_mi = 0
    for slot_trans_data in results['slot_transitions'].values():
        # Weight by frequency
        slot_conditioned_mi += slot_trans_data['entropy'] * (slot_trans_data['total_transitions'] /
                              sum(d['total_transitions'] for d in results['slot_transitions'].values()))

    results['prediction_test'] = {
        'token_only_mi': round(token_only_mi, 4),
        'slot_average_entropy': round(slot_conditioned_mi, 4),
        'improvement': 'SLOT_HELPS' if slot_conditioned_mi < token_only_mi else 'NO_IMPROVEMENT'
    }

    print(f"Token-only MI: {token_only_mi:.4f}")
    print(f"Slot-average entropy: {slot_conditioned_mi:.4f}")
    print(f"Result: {results['prediction_test']['improvement']}")

    return results

# =============================================================================
# EXPERIMENT 4: MIDDLE EMBEDDING (OPTIONAL)
# =============================================================================

def experiment4_middle_embedding(words: List[Dict], entries: Dict[str, List[Dict]]) -> Dict:
    """
    Look for smooth semantic gradients in middle space via co-occurrence analysis.
    """
    print("\n" + "="*60)
    print("EXPERIMENT 4: Middle Embedding (Co-occurrence Analysis)")
    print("="*60)

    results = {
        'cooccurrence_stats': {},
        'clustering_analysis': {},
        'gradient_detection': {}
    }

    # Extract middles using best method (known_affixes)
    middle_sequence = []
    token_to_middle = {}

    for w in words:
        token = w['word']
        _, p_len = find_best_known_prefix(token)
        _, s_len = find_best_known_suffix(token)
        middle = extract_middle(token, p_len, s_len) or token
        middle_sequence.append(middle)
        token_to_middle[token] = middle

    unique_middles = list(set(middle_sequence))
    middle_counts = Counter(middle_sequence)

    # Filter to frequent middles
    min_count = 20
    frequent_middles = [m for m, c in middle_counts.items() if c >= min_count]
    print(f"Frequent middles (count >= {min_count}): {len(frequent_middles)}")

    if len(frequent_middles) < 10:
        print("Warning: Too few frequent middles for embedding analysis")
        return results

    # Build co-occurrence matrix (same-entry co-occurrence)
    middle_idx = {m: i for i, m in enumerate(frequent_middles)}
    cooccurrence = np.zeros((len(frequent_middles), len(frequent_middles)))

    for folio, entry in entries.items():
        entry_middles = []
        for w in entry:
            token = w['word']
            middle = token_to_middle.get(token, token)
            if middle in middle_idx:
                entry_middles.append(middle)

        # Count co-occurrences within entry
        for i, m1 in enumerate(entry_middles):
            for m2 in entry_middles[i+1:]:
                idx1 = middle_idx[m1]
                idx2 = middle_idx[m2]
                cooccurrence[idx1, idx2] += 1
                cooccurrence[idx2, idx1] += 1

    # Normalize by frequency
    row_sums = cooccurrence.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    cooccurrence_normalized = cooccurrence / row_sums

    results['cooccurrence_stats'] = {
        'matrix_shape': list(cooccurrence.shape),
        'total_cooccurrences': int(cooccurrence.sum() / 2),
        'sparsity': float((cooccurrence == 0).sum() / cooccurrence.size),
        'mean_cooccurrence': float(cooccurrence.mean()),
        'max_cooccurrence': float(cooccurrence.max())
    }

    print(f"Co-occurrence matrix: {cooccurrence.shape}")
    print(f"Sparsity: {results['cooccurrence_stats']['sparsity']:.2%}")

    # Simple PCA-like analysis via SVD
    try:
        # Center the matrix
        mean_vec = cooccurrence_normalized.mean(axis=0)
        centered = cooccurrence_normalized - mean_vec

        # SVD
        U, s, Vt = np.linalg.svd(centered, full_matrices=False)

        # Variance explained by top components
        total_var = (s ** 2).sum()
        var_explained = [(s[i] ** 2 / total_var) for i in range(min(10, len(s)))]
        cumulative_var = np.cumsum(var_explained)

        results['clustering_analysis'] = {
            'top_10_singular_values': [round(float(x), 4) for x in s[:10]],
            'variance_explained_top10': [round(float(x), 4) for x in var_explained],
            'cumulative_variance_top10': [round(float(x), 4) for x in cumulative_var]
        }

        print(f"Top 3 singular values: {s[:3]}")
        print(f"Variance explained (top 3): {var_explained[:3]}")
        print(f"Cumulative variance (3 components): {cumulative_var[2]:.2%}")

        # Analyze structure: clusters vs gradients
        # If top 1-2 components dominate -> likely discrete clusters
        # If variance spreads across many components -> gradients

        if var_explained[0] > 0.5:
            structure_type = 'STRONG_CLUSTERS'
        elif cumulative_var[2] > 0.7:
            structure_type = 'MODERATE_CLUSTERS'
        elif cumulative_var[4] < 0.5:
            structure_type = 'GRADIENTS'
        else:
            structure_type = 'MIXED'

        results['gradient_detection'] = {
            'structure_type': structure_type,
            'top_component_dominance': round(float(var_explained[0]), 4),
            'three_component_coverage': round(float(cumulative_var[2]), 4)
        }

        print(f"\nStructure type detected: {structure_type}")

        # Find extremes along first component (for interpretability)
        component1 = U[:, 0]
        sorted_by_c1 = sorted(zip(frequent_middles, component1), key=lambda x: x[1])

        results['gradient_detection']['component1_extremes'] = {
            'negative_end': [(m, round(float(v), 4)) for m, v in sorted_by_c1[:10]],
            'positive_end': [(m, round(float(v), 4)) for m, v in sorted_by_c1[-10:]]
        }

        print(f"Component 1 negative end: {[m for m,_ in sorted_by_c1[:5]]}")
        print(f"Component 1 positive end: {[m for m,_ in sorted_by_c1[-5:]]}")

    except Exception as e:
        print(f"SVD analysis failed: {e}")
        results['clustering_analysis'] = {'error': str(e)}

    return results

# =============================================================================
# SYNTHESIS
# =============================================================================

def generate_synthesis(exp1: Dict, exp2: Dict, exp3: Dict, exp4: Dict) -> Dict:
    """Generate integrated synthesis of all experiments."""

    synthesis = {
        'metadata': {
            'phase': 'Phase 5: Compositional Decoding Probe',
            'timestamp': datetime.now().isoformat(),
            'experiments_completed': 4
        },
        'key_findings': [],
        'resonance_assessment': {},
        'implications': []
    }

    # Experiment 1 findings
    best_method = exp1.get('best_method', 'unknown')
    best_mi = exp1.get('best_mi_preservation', 0)
    multi_shell = exp1.get('middle_stability', {}).get('middles_in_multiple_shells', 0)

    if best_mi > 0.5:
        synthesis['key_findings'].append(f"Middle extraction preserves {best_mi:.0%} MI using {best_method} method")
        synthesis['resonance_assessment']['middle_extraction'] = 'GREEN'
    else:
        synthesis['resonance_assessment']['middle_extraction'] = 'YELLOW'

    if multi_shell > 50:
        synthesis['key_findings'].append(f"{multi_shell} middles appear in multiple token shells - TRUE compositional structure")
        synthesis['resonance_assessment']['compositional_structure'] = 'GREEN'
    else:
        synthesis['resonance_assessment']['compositional_structure'] = 'YELLOW'

    # Experiment 2 findings
    forbidden = len(exp2.get('prefix_suffix_cooccurrence', {}).get('forbidden_combinations', []))
    preferred = len(exp2.get('prefix_suffix_cooccurrence', {}).get('preferred_combinations', []))
    structural = len(exp2.get('structural_vs_semantic_affixes', {}).get('structural', []))
    semantic = len(exp2.get('structural_vs_semantic_affixes', {}).get('semantic', []))

    if forbidden > 5 or preferred > 5:
        synthesis['key_findings'].append(f"Affix co-occurrence is constrained: {forbidden} forbidden, {preferred} preferred combinations")
        synthesis['resonance_assessment']['affix_constraints'] = 'GREEN'
    else:
        synthesis['resonance_assessment']['affix_constraints'] = 'YELLOW'

    if structural > 0:
        synthesis['key_findings'].append(f"{structural} structural affixes identified (low MI + positional bias)")
        synthesis['resonance_assessment']['structural_scaffolding'] = 'GREEN'
    else:
        synthesis['resonance_assessment']['structural_scaffolding'] = 'RED'

    # Experiment 3 findings
    slot_vocab = exp3.get('per_slot_vocabulary', {})
    if slot_vocab:
        entropy_values = [v['entropy'] for v in slot_vocab.values()]
        mean_slot_entropy = np.mean(entropy_values) if entropy_values else 0

        if mean_slot_entropy < 6.0:
            synthesis['key_findings'].append(f"Slots have constrained vocabulary (mean entropy={mean_slot_entropy:.2f})")
            synthesis['resonance_assessment']['slot_vocabulary'] = 'GREEN'
        else:
            synthesis['resonance_assessment']['slot_vocabulary'] = 'YELLOW'

    slot_transitions = exp3.get('slot_transitions', {})
    if slot_transitions:
        constraint_ratios = [v['constraint_ratio'] for v in slot_transitions.values()]
        mean_constraint = np.mean(constraint_ratios) if constraint_ratios else 0

        if mean_constraint > 0.5:
            synthesis['key_findings'].append(f"Slot transitions are constrained (mean ratio={mean_constraint:.2%})")
            synthesis['resonance_assessment']['transition_constraints'] = 'GREEN'
        else:
            synthesis['resonance_assessment']['transition_constraints'] = 'YELLOW'

    prediction_result = exp3.get('prediction_test', {}).get('improvement', 'UNKNOWN')
    if prediction_result == 'SLOT_HELPS':
        synthesis['key_findings'].append("Slot position improves prediction - positional grammar detected")
        synthesis['resonance_assessment']['positional_grammar'] = 'GREEN'
    else:
        synthesis['resonance_assessment']['positional_grammar'] = 'YELLOW'

    # Experiment 4 findings
    structure_type = exp4.get('gradient_detection', {}).get('structure_type', 'UNKNOWN')
    if structure_type == 'GRADIENTS':
        synthesis['key_findings'].append("Middle embedding shows GRADIENTS - continuous semantic properties")
        synthesis['resonance_assessment']['semantic_gradients'] = 'GREEN'
    elif structure_type in ['STRONG_CLUSTERS', 'MODERATE_CLUSTERS']:
        synthesis['key_findings'].append(f"Middle embedding shows {structure_type} - categorical semantics")
        synthesis['resonance_assessment']['semantic_gradients'] = 'YELLOW'
    else:
        synthesis['resonance_assessment']['semantic_gradients'] = 'YELLOW'

    # Overall assessment
    green_count = sum(1 for v in synthesis['resonance_assessment'].values() if v == 'GREEN')
    total = len(synthesis['resonance_assessment'])

    if green_count >= total * 0.7:
        synthesis['overall_status'] = 'GREEN - Strong compositional structure detected'
    elif green_count >= total * 0.4:
        synthesis['overall_status'] = 'YELLOW - Partial compositional structure'
    else:
        synthesis['overall_status'] = 'RED - Weak compositional evidence'

    # Implications
    if best_mi > 0.5 and multi_shell > 50:
        synthesis['implications'].append("Middles ARE the semantic cores - can proceed with middle-based analysis")

    if structural > 0:
        synthesis['implications'].append("Structural affixes mark positions, not meaning - separate from semantic analysis")

    if prediction_result == 'SLOT_HELPS':
        synthesis['implications'].append("Token meaning is SLOT-DEPENDENT - same middle may mean different things in different slots")

    if structure_type == 'GRADIENTS':
        synthesis['implications'].append("Semantics are continuous properties, not discrete categories")

    return synthesis

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("="*60)
    print("PHASE 5: COMPOSITIONAL DECODING PROBE")
    print("Reverse-engineering: MODIFIER1 + CORE + MODIFIER2")
    print("="*60)

    # Load data
    print("\nLoading corpus...")
    words = load_corpus()
    print(f"Loaded {len(words)} word tokens")

    entries = segment_into_entries(words)
    print(f"Segmented into {len(entries)} entries")

    gamma_tokens = load_gamma_tokens()
    print(f"Loaded {len(gamma_tokens)} GAMMA tokens")

    # Run experiments
    exp1_results = experiment1_middle_extraction(words)

    exp2_results = experiment2_affix_functions(words, entries)

    exp3_results = experiment3_slot_structure(words, entries, gamma_tokens)

    exp4_results = experiment4_middle_embedding(words, entries)

    # Generate synthesis
    synthesis = generate_synthesis(exp1_results, exp2_results, exp3_results, exp4_results)

    # Save all results
    outputs = [
        ('phase5_middle_extraction.json', exp1_results),
        ('phase5_affix_functions.json', exp2_results),
        ('phase5_slot_structure.json', exp3_results),
        ('phase5_middle_embedding.json', exp4_results),
        ('phase5_synthesis.json', synthesis)
    ]

    for filename, data in outputs:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nSaved: {filename}")

    # Print synthesis
    print("\n" + "="*60)
    print("SYNTHESIS")
    print("="*60)

    print(f"\nOverall Status: {synthesis['overall_status']}")

    print("\nKey Findings:")
    for finding in synthesis['key_findings']:
        print(f"  * {finding}")

    print("\nResonance Assessment:")
    for metric, status in synthesis['resonance_assessment'].items():
        print(f"  {metric}: {status}")

    print("\nImplications:")
    for impl in synthesis['implications']:
        print(f"  -> {impl}")

if __name__ == '__main__':
    main()
