#!/usr/bin/env python3
"""
PHASE 1: DAIIN ABUSE BATTERY
============================
We have ONE confirmed grammatical handle. Let's break it.

CRITICAL: Experiment 0 establishes baseline before daiin-specific tests.
"""

import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime

# =============================================================================
# DATA LOADING (adapted from heading_word_analysis.py)
# =============================================================================

def load_corpus():
    """Load corpus from interlinear_full_words.txt (PRIMARY transcriber H only)."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'
    words = []
    seen = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

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


def group_by_entries(words):
    """
    Group words into entries (one folio = one entry).
    Returns dict: folio -> list of words
    """
    entries = defaultdict(list)
    for w in words:
        entries[w['folio']].append(w)
    return dict(entries)


def split_by_currier(entries):
    """Split entries into Currier A and B."""
    a_entries = {}
    b_entries = {}

    for folio, words in entries.items():
        # Determine Currier type from first word
        if words:
            currier = words[0].get('currier', '')
            if currier == 'A':
                a_entries[folio] = words
            elif currier == 'B':
                b_entries[folio] = words

    return a_entries, b_entries


def tokenize_entry(words_list):
    """Extract tokens from entry word list."""
    if isinstance(words_list, list):
        return [w['word'] if isinstance(w, dict) else str(w) for w in words_list]
    return []


# =============================================================================
# EXPERIMENT 0: RANDOM DELETION CONTROL
# =============================================================================
def experiment_0_random_deletion_control(a_entries, b_entries):
    """
    Delete a random high-frequency token (NOT daiin) and measure collapse.
    This establishes baseline severity for comparison with daiin deletion.
    """
    results = {
        'experiment': 'random_deletion_control',
        'purpose': 'Baseline for daiin deletion comparison',
        'control_tokens': [],
        'collapse_metrics': {}
    }

    # Get all tokens and frequencies
    all_tokens = []
    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            all_tokens.extend(tokenize_entry(words))

    freq = Counter(all_tokens)

    # Find high-frequency tokens similar to daiin but NOT daiin
    daiin_freq = freq.get('daiin', 0)

    # Select 3 control tokens with similar frequency (within 50%)
    control_candidates = [
        token for token, count in freq.items()
        if token != 'daiin'
        and count >= daiin_freq * 0.5
        and count <= daiin_freq * 1.5
    ]

    # If not enough similar frequency, take next 3 most frequent non-daiin
    if len(control_candidates) < 3:
        control_candidates = [
            token for token, count in freq.most_common(20)
            if token != 'daiin'
        ][:3]

    control_tokens = control_candidates[:3]
    results['control_tokens'] = control_tokens
    results['daiin_frequency'] = daiin_freq
    results['control_frequencies'] = {t: freq[t] for t in control_tokens}

    # Measure collapse metrics for each control token
    for control_token in control_tokens:
        metrics = measure_deletion_collapse(a_entries, b_entries, control_token)
        results['collapse_metrics'][control_token] = metrics

    # Also measure daiin for direct comparison
    daiin_metrics = measure_deletion_collapse(a_entries, b_entries, 'daiin')
    results['collapse_metrics']['daiin'] = daiin_metrics

    # Calculate relative severity
    control_avg = {}
    for metric_name in ['tokens_remaining_pct', 'entries_affected_pct',
                        'structure_survival_score', 'entropy_change']:
        control_values = [
            results['collapse_metrics'][t].get(metric_name, 0)
            for t in control_tokens
        ]
        if control_values:
            control_avg[metric_name] = sum(control_values) / len(control_values)

    results['control_average'] = control_avg
    results['daiin_vs_control'] = {
        metric: daiin_metrics.get(metric, 0) - control_avg.get(metric, 0)
        for metric in control_avg
    }

    # Interpretation
    results['interpretation'] = interpret_control_comparison(daiin_metrics, control_avg)

    return results


def measure_deletion_collapse(a_entries, b_entries, target_token):
    """Measure structural collapse when target_token is deleted."""
    metrics = {
        'target_token': target_token,
        'original_token_count': 0,
        'deleted_count': 0,
        'tokens_remaining_pct': 0,
        'entries_affected_pct': 0,
        'empty_entries_created': 0,
        'avg_tokens_per_entry_before': 0,
        'avg_tokens_per_entry_after': 0,
        'structure_survival_score': 0,
        'entropy_change': 0
    }

    all_entries = list(a_entries.values()) + list(b_entries.values())
    entries_affected = 0
    total_tokens_before = 0
    total_tokens_after = 0
    empty_after = 0

    for entry in all_entries:
        tokens = tokenize_entry(entry)
        total_tokens_before += len(tokens)

        # Count and remove target
        target_count = tokens.count(target_token)
        if target_count > 0:
            entries_affected += 1
            metrics['deleted_count'] += target_count

        remaining = [t for t in tokens if t != target_token]
        total_tokens_after += len(remaining)

        if len(remaining) == 0 and len(tokens) > 0:
            empty_after += 1

    metrics['original_token_count'] = total_tokens_before
    metrics['tokens_remaining_pct'] = (
        total_tokens_after / total_tokens_before * 100
        if total_tokens_before > 0 else 100
    )
    metrics['entries_affected_pct'] = (
        entries_affected / len(all_entries) * 100
        if all_entries else 0
    )
    metrics['empty_entries_created'] = empty_after
    metrics['avg_tokens_per_entry_before'] = (
        total_tokens_before / len(all_entries) if all_entries else 0
    )
    metrics['avg_tokens_per_entry_after'] = (
        total_tokens_after / len(all_entries) if all_entries else 0
    )

    # Structure survival
    metrics['structure_survival_score'] = calculate_structure_survival(
        all_entries, target_token
    )

    # Entropy change
    metrics['entropy_change'] = calculate_entropy_change(all_entries, target_token)

    return metrics


def calculate_structure_survival(entries, deleted_token):
    """Score 0-1 indicating how much structure survives deletion."""
    lengths_before = []
    lengths_after = []

    for entry in entries:
        tokens = tokenize_entry(entry)
        lengths_before.append(len(tokens))
        remaining = [t for t in tokens if t != deleted_token]
        lengths_after.append(len(remaining))

    if not lengths_before:
        return 1.0

    mean_before = sum(lengths_before) / len(lengths_before)
    mean_after = sum(lengths_after) / len(lengths_after)

    if mean_before == 0:
        return 1.0

    return min(1.0, mean_after / mean_before)


def calculate_entropy_change(entries, deleted_token):
    """Calculate change in token entropy after deletion."""
    def entropy(tokens):
        if not tokens:
            return 0
        freq = Counter(tokens)
        total = sum(freq.values())
        return -sum(
            (c/total) * math.log2(c/total)
            for c in freq.values() if c > 0
        )

    all_before = []
    all_after = []

    for entry in entries:
        tokens = tokenize_entry(entry)
        all_before.extend(tokens)
        all_after.extend([t for t in tokens if t != deleted_token])

    return entropy(all_after) - entropy(all_before)


def interpret_control_comparison(daiin_metrics, control_avg):
    """Generate interpretation of daiin vs control deletion."""
    interpretations = []

    daiin_remaining = daiin_metrics.get('tokens_remaining_pct', 100)
    control_remaining = control_avg.get('tokens_remaining_pct', 100)

    if daiin_remaining < control_remaining - 5:
        interpretations.append(
            "daiin deletion removes MORE tokens than control - "
            "suggests higher frequency or broader distribution"
        )
    elif daiin_remaining > control_remaining + 5:
        interpretations.append(
            "daiin deletion removes FEWER tokens than control - "
            "unexpected given frequency"
        )
    else:
        interpretations.append(
            "daiin deletion similar to control - frequency-proportional effect"
        )

    daiin_structure = daiin_metrics.get('structure_survival_score', 1)
    control_structure = control_avg.get('structure_survival_score', 1)

    if daiin_structure < control_structure - 0.1:
        interpretations.append(
            "IMPORTANT: daiin deletion DAMAGES STRUCTURE more than control - "
            "suggests grammatical/structural role"
        )
    elif daiin_structure > control_structure + 0.1:
        interpretations.append(
            "daiin deletion preserves structure BETTER than control - "
            "suggests content word, not structural"
        )
    else:
        interpretations.append(
            "Structure impact similar to control - no special structural role detected"
        )

    return interpretations


# =============================================================================
# EXPERIMENT 1: DAIIN DELETION
# =============================================================================
def experiment_1_daiin_deletion(a_entries, b_entries, control_results):
    """Remove all daiin tokens. What survives? Does structure collapse?"""
    results = {
        'experiment': 'daiin_deletion',
        'metrics': {},
        'relative_to_control': {},
        'structure_analysis': {},
        'interpretation': []
    }

    daiin_metrics = control_results['collapse_metrics'].get('daiin', {})
    control_avg = control_results.get('control_average', {})

    results['metrics'] = daiin_metrics
    results['relative_to_control'] = control_results.get('daiin_vs_control', {})

    results['structure_analysis'] = analyze_post_deletion_structure(
        a_entries, b_entries, 'daiin'
    )

    results['interpretation'] = interpret_daiin_deletion(
        daiin_metrics, control_avg, results['structure_analysis']
    )

    return results


def analyze_post_deletion_structure(a_entries, b_entries, deleted_token):
    """Analyze what structural patterns survive deletion."""
    analysis = {
        'three_part_survival': False,
        'hub_reference_survival': False,
        'entry_boundary_survival': True,
        'details': {}
    }

    hub_words = ['tol', 'pol', 'sho', 'tor', 'kor', 'par', 'pchor', 'paiin']

    hub_survival = defaultdict(int)
    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            tokens = tokenize_entry(words)
            remaining = [t for t in tokens if t != deleted_token]
            for hub in hub_words:
                if hub in remaining:
                    hub_survival[hub] += 1

    analysis['hub_reference_survival'] = sum(hub_survival.values()) > 0
    analysis['details']['hub_counts_after_deletion'] = dict(hub_survival)

    return analysis


def interpret_daiin_deletion(daiin_metrics, control_avg, structure_analysis):
    """Generate final interpretation of daiin deletion experiment."""
    interpretations = []

    affected_pct = daiin_metrics.get('entries_affected_pct', 0)
    if affected_pct > 90:
        interpretations.append(
            f"daiin appears in {affected_pct:.1f}% of entries - "
            "confirms ubiquitous grammatical role"
        )

    if structure_analysis.get('hub_reference_survival'):
        interpretations.append(
            "Hub references SURVIVE daiin deletion - "
            "category structure independent of daiin"
        )

    structure_score = daiin_metrics.get('structure_survival_score', 1)
    control_score = control_avg.get('structure_survival_score', 1)

    if structure_score < control_score - 0.15:
        interpretations.append(
            "SIGNIFICANT: daiin removal damages structure beyond frequency effect - "
            "strong evidence for grammatical skeleton role"
        )

    return interpretations


# =============================================================================
# EXPERIMENT 2: DAIIN AS SCOPE OPERATOR
# =============================================================================
def experiment_2_scope_operator(a_entries, b_entries):
    """
    Treat daiin as opening a "scope" that closes at next daiin or entry boundary.
    Segment text into daiin-delimited chunks and analyze.
    """
    results = {
        'experiment': 'daiin_scope_operator',
        'chunk_count': 0,
        'chunk_lengths': [],
        'chunk_length_distribution': {},
        'chunks_per_entry': [],
        'internal_patterns': {},
        'interpretation': []
    }

    all_chunks = []
    chunks_per_entry = []

    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            tokens = tokenize_entry(words)

            # Segment by daiin
            chunks = []
            current_chunk = []

            for token in tokens:
                if token == 'daiin':
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = []
                else:
                    current_chunk.append(token)

            if current_chunk:
                chunks.append(current_chunk)

            all_chunks.extend(chunks)
            chunks_per_entry.append(len(chunks))

    results['chunk_count'] = len(all_chunks)
    results['chunk_lengths'] = [len(c) for c in all_chunks]
    results['chunks_per_entry'] = chunks_per_entry

    # Length distribution
    length_dist = Counter(results['chunk_lengths'])
    results['chunk_length_distribution'] = dict(length_dist)

    # Statistics
    if results['chunk_lengths']:
        lengths = results['chunk_lengths']
        results['avg_chunk_length'] = sum(lengths) / len(lengths)
        results['median_chunk_length'] = sorted(lengths)[len(lengths)//2]
        results['max_chunk_length'] = max(lengths)
        results['min_chunk_length'] = min(lengths) if lengths else 0

    # Look for patterns within chunks
    results['internal_patterns'] = analyze_chunk_patterns(all_chunks)

    # Interpretation
    results['interpretation'] = interpret_scope_analysis(results)

    return results


def analyze_chunk_patterns(chunks):
    """Find patterns within daiin-delimited chunks."""
    patterns = {
        'first_token_freq': Counter(),
        'last_token_freq': Counter(),
        'chunk_signatures': Counter(),
        'repeated_chunks': []
    }

    for chunk in chunks:
        if chunk:
            patterns['first_token_freq'][chunk[0]] += 1
            patterns['last_token_freq'][chunk[-1]] += 1

            if len(chunk) >= 2:
                sig = f"{chunk[0]}...{chunk[-1]}"
                patterns['chunk_signatures'][sig] += 1

    # Find repeated chunks
    chunk_tuples = [tuple(c) for c in chunks if c]
    chunk_counts = Counter(chunk_tuples)
    patterns['repeated_chunks'] = [
        {'chunk': list(c), 'count': n}
        for c, n in chunk_counts.most_common(20)
        if n > 1
    ]

    patterns['first_token_freq'] = dict(patterns['first_token_freq'].most_common(20))
    patterns['last_token_freq'] = dict(patterns['last_token_freq'].most_common(20))
    patterns['chunk_signatures'] = dict(patterns['chunk_signatures'].most_common(20))

    return patterns


def interpret_scope_analysis(results):
    """Interpret scope operator hypothesis results."""
    interpretations = []

    avg_len = results.get('avg_chunk_length', 0)

    if 2 <= avg_len <= 5:
        interpretations.append(
            f"Average chunk length {avg_len:.1f} - consistent with phrase/clause scope"
        )
    elif avg_len < 2:
        interpretations.append(
            f"Average chunk length {avg_len:.1f} - daiin appears too frequently for phrase scope"
        )
    else:
        interpretations.append(
            f"Average chunk length {avg_len:.1f} - chunks larger than typical phrases"
        )

    dist = results.get('chunk_length_distribution', {})
    if dist:
        mode_length = max(dist, key=dist.get)
        mode_count = dist[mode_length]
        total = sum(dist.values())
        mode_pct = mode_count / total * 100 if total > 0 else 0

        if mode_pct > 30:
            interpretations.append(
                f"Strong mode at length {mode_length} ({mode_pct:.1f}%) - suggests regular structure"
            )

    repeated = results.get('internal_patterns', {}).get('repeated_chunks', [])
    if repeated:
        interpretations.append(
            f"Found {len(repeated)} repeated chunk patterns - possible formulaic phrases"
        )

    return interpretations


# =============================================================================
# EXPERIMENT 3: POST-DAIIN CLUSTERING
# =============================================================================
def experiment_3_post_daiin_clustering(a_entries, b_entries):
    """Cluster words by what immediately follows daiin."""
    results = {
        'experiment': 'post_daiin_clustering',
        'total_daiin_occurrences': 0,
        'post_daiin_tokens': Counter(),
        'post_daiin_by_section': {'A': Counter(), 'B': Counter()},
        'hub_alignment': {},
        'clusters': [],
        'interpretation': []
    }

    hub_words = ['tol', 'pol', 'sho', 'tor', 'kor', 'par', 'pchor', 'paiin']

    def extract_post_daiin(entries, section_label):
        post_tokens = []
        for folio, words in entries.items():
            tokens = tokenize_entry(words)
            for i, token in enumerate(tokens):
                if token == 'daiin' and i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    post_tokens.append(next_token)
                    results['post_daiin_tokens'][next_token] += 1
                    results['post_daiin_by_section'][section_label][next_token] += 1
                    results['total_daiin_occurrences'] += 1
        return post_tokens

    extract_post_daiin(a_entries, 'A')
    extract_post_daiin(b_entries, 'B')

    for hub in hub_words:
        count = results['post_daiin_tokens'].get(hub, 0)
        if count > 0:
            results['hub_alignment'][hub] = count

    # Cluster by prefix
    prefix_clusters = defaultdict(list)
    for token, count in results['post_daiin_tokens'].items():
        if len(token) >= 2:
            prefix = token[:2]
            prefix_clusters[prefix].append((token, count))

    results['clusters'] = [
        {
            'prefix': prefix,
            'members': sorted(members, key=lambda x: -x[1])[:10],
            'total_freq': sum(m[1] for m in members)
        }
        for prefix, members in sorted(
            prefix_clusters.items(),
            key=lambda x: -sum(m[1] for m in x[1])
        )[:15]
    ]

    # Convert Counters for JSON
    results['post_daiin_tokens'] = dict(results['post_daiin_tokens'].most_common(50))
    results['post_daiin_by_section']['A'] = dict(
        results['post_daiin_by_section']['A'].most_common(30)
    )
    results['post_daiin_by_section']['B'] = dict(
        results['post_daiin_by_section']['B'].most_common(30)
    )

    results['interpretation'] = interpret_post_daiin(results, hub_words)

    return results


def interpret_post_daiin(results, hub_words):
    """Interpret post-daiin clustering results."""
    interpretations = []

    hub_count = len(results.get('hub_alignment', {}))
    if hub_count > 0:
        interpretations.append(
            f"{hub_count} hub words appear after daiin - "
            "daiin may introduce category references"
        )

    unique_followers = len(results.get('post_daiin_tokens', {}))
    total_occurrences = results.get('total_daiin_occurrences', 1)
    diversity = unique_followers / total_occurrences if total_occurrences > 0 else 0

    if diversity > 0.3:
        interpretations.append(
            f"High diversity ({diversity:.2f}) in post-daiin tokens - "
            "daiin precedes many word types (determiner-like)"
        )
    elif diversity < 0.1:
        interpretations.append(
            f"Low diversity ({diversity:.2f}) in post-daiin tokens - "
            "daiin may have restricted collocations"
        )

    a_top = list(results['post_daiin_by_section']['A'].keys())[:5]
    b_top = list(results['post_daiin_by_section']['B'].keys())[:5]
    overlap = set(a_top) & set(b_top)

    if len(overlap) < 2:
        interpretations.append(
            "Different tokens follow daiin in A vs B - section-specific content patterns"
        )
    else:
        interpretations.append(
            f"Overlap in post-daiin tokens across sections ({len(overlap)}/5) - "
            "consistent grammatical role"
        )

    return interpretations


# =============================================================================
# EXPERIMENT 4: DAIIN REPLACEMENT TEST
# =============================================================================
def experiment_4_replacement_test(a_entries, b_entries):
    """Replace daiin with candidate translations and check coherence."""
    results = {
        'experiment': 'daiin_replacement',
        'candidates': {},
        'coherence_scores': {},
        'best_fit': None,
        'interpretation': []
    }

    candidates = {
        'THIS': 'demonstrative - "this plant", "this symptom"',
        'SOME': 'indefinite - "some amount", "some cases"',
        'EACH': 'distributive - "each part", "each day"',
        'FOR': 'purpose - "for fever", "for pain"',
        'RE': 'reference - "regarding X", "concerning"',
        'WITH': 'instrumental - "with water", "with honey"',
        'THE': 'definite article - "the root", "the leaf"'
    }

    results['candidates'] = candidates

    for candidate, description in candidates.items():
        score = score_replacement_coherence(
            a_entries, b_entries, 'daiin', candidate
        )
        results['coherence_scores'][candidate] = score

    if results['coherence_scores']:
        best = max(results['coherence_scores'], key=results['coherence_scores'].get)
        results['best_fit'] = {
            'candidate': best,
            'score': results['coherence_scores'][best],
            'description': candidates[best]
        }

    results['interpretation'] = interpret_replacement(results)

    return results


def score_replacement_coherence(a_entries, b_entries, target, replacement):
    """Score how well a replacement fits daiin's context patterns."""
    score = 0
    contexts = []

    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            tokens = tokenize_entry(words)
            for i, token in enumerate(tokens):
                if token == target:
                    prev_token = tokens[i-1] if i > 0 else None
                    next_token = tokens[i+1] if i + 1 < len(tokens) else None
                    contexts.append({
                        'prev': prev_token,
                        'next': next_token,
                        'position': i / len(tokens) if tokens else 0
                    })

    if not contexts:
        return 0

    hub_words = ['tol', 'pol', 'sho', 'tor', 'kor', 'par', 'pchor', 'paiin']

    if replacement in ['THIS', 'THE']:
        for ctx in contexts:
            if ctx['next'] and len(ctx['next']) > 4:
                score += 1

    elif replacement in ['FOR', 'WITH']:
        for ctx in contexts:
            if ctx['next']:
                if ctx['next'] in hub_words:
                    score += 2
                elif len(ctx['next']) > 3:
                    score += 0.5

    elif replacement == 'EACH':
        for ctx in contexts:
            if ctx['position'] < 0.3:
                score += 0.5

    elif replacement == 'SOME':
        positions = [ctx['position'] for ctx in contexts]
        if positions:
            variance = sum((p - 0.5)**2 for p in positions) / len(positions)
            if variance > 0.05:
                score += len(contexts) * 0.1

    elif replacement == 'RE':
        for ctx in contexts:
            if ctx['prev'] is None or ctx['position'] < 0.1:
                score += 1

    return score / len(contexts) if contexts else 0


def interpret_replacement(results):
    """Interpret replacement test results."""
    interpretations = []

    best = results.get('best_fit', {})
    if best:
        interpretations.append(
            f"Best fit: {best['candidate']} ({best['description']}) "
            f"with score {best['score']:.3f}"
        )

    scores = results.get('coherence_scores', {})
    if scores:
        values = list(scores.values())
        max_score = max(values)
        second_score = sorted(values)[-2] if len(values) > 1 else 0

        if max_score > second_score * 1.5:
            interpretations.append(
                "Clear winner - one interpretation notably better than others"
            )
        else:
            interpretations.append(
                "Multiple plausible interpretations - daiin is ambiguous"
            )

    return interpretations


# =============================================================================
# EXPERIMENT 5: ANTI-DAIIN WORDS
# =============================================================================
def experiment_5_anti_daiin(a_entries, b_entries):
    """Find words that NEVER appear near daiin."""
    results = {
        'experiment': 'anti_daiin_words',
        'window_size': 2,
        'daiin_neighbors': set(),
        'never_neighbors': [],
        'rare_neighbors': [],
        'interpretation': []
    }

    all_tokens = Counter()
    daiin_neighbors = Counter()

    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            tokens = tokenize_entry(words)
            all_tokens.update(tokens)

            for i, token in enumerate(tokens):
                if token == 'daiin':
                    start = max(0, i - results['window_size'])
                    end = min(len(tokens), i + results['window_size'] + 1)
                    for j in range(start, end):
                        if j != i:
                            daiin_neighbors[tokens[j]] += 1

    results['daiin_neighbors'] = set(daiin_neighbors.keys())

    min_freq = 10
    never_neighbors = []
    rare_neighbors = []

    for token, freq in all_tokens.most_common():
        if token == 'daiin':
            continue
        if freq < min_freq:
            break

        neighbor_freq = daiin_neighbors.get(token, 0)
        expected_neighbor_freq = freq * (all_tokens['daiin'] / sum(all_tokens.values())) * 2 * results['window_size']

        if neighbor_freq == 0:
            never_neighbors.append({
                'token': token,
                'frequency': freq,
                'expected_neighbor_freq': expected_neighbor_freq
            })
        elif neighbor_freq < expected_neighbor_freq * 0.2:
            rare_neighbors.append({
                'token': token,
                'frequency': freq,
                'neighbor_freq': neighbor_freq,
                'expected': expected_neighbor_freq,
                'ratio': neighbor_freq / expected_neighbor_freq if expected_neighbor_freq > 0 else 0
            })

    results['never_neighbors'] = never_neighbors[:20]
    results['rare_neighbors'] = rare_neighbors[:20]
    results['patterns'] = analyze_anti_daiin_patterns(never_neighbors + rare_neighbors)
    results['interpretation'] = interpret_anti_daiin(results)

    return results


def analyze_anti_daiin_patterns(anti_words):
    """Look for patterns in words that avoid daiin."""
    patterns = {
        'avg_length': 0,
        'common_prefixes': Counter(),
        'common_suffixes': Counter(),
        'hub_overlap': []
    }

    hub_words = {'tol', 'pol', 'sho', 'tor', 'kor', 'par', 'pchor', 'paiin'}

    if not anti_words:
        return patterns

    lengths = [len(w['token']) for w in anti_words]
    patterns['avg_length'] = sum(lengths) / len(lengths)

    for w in anti_words:
        token = w['token']
        if len(token) >= 2:
            patterns['common_prefixes'][token[:2]] += 1
        if len(token) >= 2:
            patterns['common_suffixes'][token[-2:]] += 1
        if token in hub_words:
            patterns['hub_overlap'].append(token)

    patterns['common_prefixes'] = dict(patterns['common_prefixes'].most_common(10))
    patterns['common_suffixes'] = dict(patterns['common_suffixes'].most_common(10))

    return patterns


def interpret_anti_daiin(results):
    """Interpret anti-daiin word analysis."""
    interpretations = []

    never = results.get('never_neighbors', [])
    rare = results.get('rare_neighbors', [])

    if never:
        interpretations.append(
            f"Found {len(never)} frequent words that NEVER appear near daiin - "
            "possible different grammatical class"
        )

        hub_words = {'tol', 'pol', 'sho', 'tor', 'kor', 'par', 'pchor', 'paiin'}
        anti_hubs = [w['token'] for w in never if w['token'] in hub_words]
        if anti_hubs:
            interpretations.append(
                f"Hub words {anti_hubs} avoid daiin - "
                "hubs and daiin may be complementary structural elements"
            )

    patterns = results.get('patterns', {})
    if patterns.get('hub_overlap'):
        interpretations.append(
            f"Hubs in anti-daiin set: {patterns['hub_overlap']} - "
            "structural separation between categories and determiners"
        )

    avg_len = patterns.get('avg_length', 0)
    if avg_len > 5:
        interpretations.append(
            f"Anti-daiin words are longer ({avg_len:.1f} chars) - "
            "possibly different word class"
        )
    elif avg_len < 4:
        interpretations.append(
            f"Anti-daiin words are shorter ({avg_len:.1f} chars) - "
            "possibly other grammatical particles"
        )

    return interpretations


# =============================================================================
# SYNTHESIS
# =============================================================================
def generate_phase1_synthesis(all_results):
    """Generate overall synthesis from Phase 1 experiments."""
    synthesis = {
        'phase': 'Phase 1: daiin Abuse Battery',
        'timestamp': datetime.now().isoformat(),
        'key_findings': [],
        'daiin_role_assessment': {},
        'next_directions': [],
        'resonance_score': 'PENDING_HUMAN_ASSESSMENT'
    }

    for exp_name, exp_results in all_results.items():
        if 'interpretation' in exp_results:
            for interp in exp_results['interpretation']:
                synthesis['key_findings'].append({
                    'source': exp_name,
                    'finding': interp
                })

    synthesis['daiin_role_assessment'] = {
        'grammatical': True,
        'structural': None,
        'scope_operator': None,
        'determiner_like': None,
        'avoids_hubs': None
    }

    exp0 = all_results.get('experiment_0_control', {})
    if 'daiin_vs_control' in exp0:
        structure_diff = exp0['daiin_vs_control'].get('structure_survival_score', 0)
        synthesis['daiin_role_assessment']['structural'] = structure_diff < -0.1

    exp2 = all_results.get('experiment_2_scope', {})
    avg_chunk = exp2.get('avg_chunk_length', 0)
    synthesis['daiin_role_assessment']['scope_operator'] = 2 <= avg_chunk <= 6

    exp3 = all_results.get('experiment_3_clustering', {})
    total_occ = exp3.get('total_daiin_occurrences', 1)
    unique_followers = len(exp3.get('post_daiin_tokens', {}))
    diversity = unique_followers / total_occ if total_occ > 0 else 0
    synthesis['daiin_role_assessment']['determiner_like'] = diversity > 0.2

    exp5 = all_results.get('experiment_5_anti_daiin', {})
    hub_overlap = exp5.get('patterns', {}).get('hub_overlap', [])
    synthesis['daiin_role_assessment']['avoids_hubs'] = len(hub_overlap) > 0

    if synthesis['daiin_role_assessment'].get('scope_operator'):
        synthesis['next_directions'].append(
            "Investigate chunk-internal structure - may reveal phrase grammar"
        )
    if synthesis['daiin_role_assessment'].get('avoids_hubs'):
        synthesis['next_directions'].append(
            "Map hub-daiin complementarity - may reveal syntactic layers"
        )
    if synthesis['daiin_role_assessment'].get('determiner_like'):
        synthesis['next_directions'].append(
            "Try daiin as 'the/this' in parse trees - test NP structure"
        )

    return synthesis


# =============================================================================
# MAIN EXECUTION
# =============================================================================
def run_phase_1():
    """Execute all Phase 1 experiments."""
    print("=" * 60)
    print("PHASE 1: DAIIN ABUSE BATTERY")
    print("=" * 60)

    print("\nLoading corpus...")
    words = load_corpus()
    entries = group_by_entries(words)
    a_entries, b_entries = split_by_currier(entries)
    print(f"Loaded {len(a_entries)} A entries, {len(b_entries)} B entries")

    # Count total tokens
    total_tokens = sum(len(tokenize_entry(w)) for w in a_entries.values())
    total_tokens += sum(len(tokenize_entry(w)) for w in b_entries.values())
    print(f"Total tokens: {total_tokens}")

    all_results = {}

    # Experiment 0: Control
    print("\n" + "-" * 40)
    print("Experiment 0: Random Deletion Control")
    print("-" * 40)
    exp0_results = experiment_0_random_deletion_control(a_entries, b_entries)
    all_results['experiment_0_control'] = exp0_results
    print(f"Control tokens: {exp0_results['control_tokens']}")
    print(f"daiin frequency: {exp0_results['daiin_frequency']}")
    for interp in exp0_results['interpretation']:
        print(f"  > {interp}")

    # Experiment 1: daiin Deletion
    print("\n" + "-" * 40)
    print("Experiment 1: daiin Deletion Analysis")
    print("-" * 40)
    exp1_results = experiment_1_daiin_deletion(a_entries, b_entries, exp0_results)
    all_results['experiment_1_deletion'] = exp1_results
    for interp in exp1_results['interpretation']:
        print(f"  > {interp}")

    # Experiment 2: Scope Operator
    print("\n" + "-" * 40)
    print("Experiment 2: daiin as Scope Operator")
    print("-" * 40)
    exp2_results = experiment_2_scope_operator(a_entries, b_entries)
    all_results['experiment_2_scope'] = exp2_results
    print(f"Chunks found: {exp2_results['chunk_count']}")
    print(f"Avg chunk length: {exp2_results.get('avg_chunk_length', 'N/A'):.2f}")
    for interp in exp2_results['interpretation']:
        print(f"  > {interp}")

    # Experiment 3: Post-daiin Clustering
    print("\n" + "-" * 40)
    print("Experiment 3: Post-daiin Clustering")
    print("-" * 40)
    exp3_results = experiment_3_post_daiin_clustering(a_entries, b_entries)
    all_results['experiment_3_clustering'] = exp3_results
    print(f"Total daiin occurrences: {exp3_results['total_daiin_occurrences']}")
    print(f"Unique followers: {len(exp3_results['post_daiin_tokens'])}")
    print(f"Top 5 post-daiin: {list(exp3_results['post_daiin_tokens'].items())[:5]}")
    for interp in exp3_results['interpretation']:
        print(f"  > {interp}")

    # Experiment 4: Replacement Test
    print("\n" + "-" * 40)
    print("Experiment 4: daiin Replacement Test")
    print("-" * 40)
    exp4_results = experiment_4_replacement_test(a_entries, b_entries)
    all_results['experiment_4_replacement'] = exp4_results
    print(f"Coherence scores: {exp4_results['coherence_scores']}")
    if exp4_results.get('best_fit'):
        print(f"Best fit: {exp4_results['best_fit']}")
    for interp in exp4_results['interpretation']:
        print(f"  > {interp}")

    # Experiment 5: Anti-daiin Words
    print("\n" + "-" * 40)
    print("Experiment 5: Anti-daiin Words")
    print("-" * 40)
    exp5_results = experiment_5_anti_daiin(a_entries, b_entries)
    all_results['experiment_5_anti_daiin'] = exp5_results
    print(f"Never-neighbors found: {len(exp5_results['never_neighbors'])}")
    print(f"Rare-neighbors found: {len(exp5_results['rare_neighbors'])}")
    if exp5_results['never_neighbors'][:5]:
        print(f"Top never-neighbors: {[w['token'] for w in exp5_results['never_neighbors'][:5]]}")
    for interp in exp5_results['interpretation']:
        print(f"  > {interp}")

    # Save all results
    output_path = Path('phase1_daiin_abuse_results.json')

    # Convert sets to lists for JSON
    def convert_sets(obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: convert_sets(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_sets(i) for i in obj]
        return obj

    serializable = convert_sets(all_results)
    with open(output_path, 'w') as f:
        json.dump(serializable, f, indent=2)
    print(f"\n[OK] Results saved to {output_path}")

    # Generate synthesis
    synthesis = generate_phase1_synthesis(all_results)

    synthesis_path = Path('phase1_synthesis.json')
    with open(synthesis_path, 'w') as f:
        json.dump(synthesis, f, indent=2)
    print(f"[OK] Synthesis saved to {synthesis_path}")

    return all_results, synthesis


if __name__ == '__main__':
    results, synthesis = run_phase_1()

    print("\n" + "=" * 60)
    print("PHASE 1 COMPLETE")
    print("=" * 60)
    print("\nKey findings:")
    for finding in synthesis['key_findings'][:10]:
        print(f"  * [{finding['source']}] {finding['finding']}")
    print("\nRole assessment:")
    for role, value in synthesis['daiin_role_assessment'].items():
        print(f"  - {role}: {value}")
    print("\nSuggested next directions:")
    for direction in synthesis['next_directions']:
        print(f"  > {direction}")
