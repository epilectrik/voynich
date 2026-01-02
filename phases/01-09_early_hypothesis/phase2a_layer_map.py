#!/usr/bin/env python3
"""
PHASE 2A: FORBIDDEN ADJACENCY & LAYER MAP
==========================================

Phase 1 discovered that daiin avoids hubs. This suggests syntactic layers.
Before information density analysis, we need to map these layers.

This is CHEAP and directly exploits green findings from Phase 1.
"""

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from itertools import combinations
from datetime import datetime

# =============================================================================
# DATA LOADING (adapted from phase1)
# =============================================================================

def load_corpus():
    """Load corpus from interlinear_full_words.txt"""
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


def group_by_entries(words):
    """Group words into entries (one folio = one entry)."""
    entries = defaultdict(list)
    for w in words:
        entries[w['folio']].append(w)
    return dict(entries)


def split_by_currier(entries):
    """Split entries into Currier A and B."""
    a_entries = {}
    b_entries = {}

    for folio, words in entries.items():
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


def get_all_tokens(a_entries, b_entries):
    """Get all tokens with frequencies."""
    all_tokens = []
    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            all_tokens.extend(tokenize_entry(words))
    return all_tokens, Counter(all_tokens)


# =============================================================================
# STEP 1: CO-OCCURRENCE EXCLUSION MATRIX
# =============================================================================

def build_cooccurrence_matrix(a_entries, b_entries, min_freq=20, window=1):
    """
    Build adjacency co-occurrence matrix for frequent tokens.
    """
    results = {
        'parameters': {'min_freq': min_freq, 'window': window},
        'tokens_analyzed': [],
        'observed': {},
        'expected': {},
        'exclusion_scores': {},
        'strong_exclusions': [],
        'strong_attractions': []
    }

    all_tokens, freq = get_all_tokens(a_entries, b_entries)
    total_tokens = len(all_tokens)

    # Select frequent tokens
    frequent_tokens = [t for t, c in freq.most_common() if c >= min_freq]
    results['tokens_analyzed'] = frequent_tokens[:100]  # Cap for tractability

    # Count adjacencies
    adjacency_counts = defaultdict(int)
    token_adjacency_totals = defaultdict(int)

    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            tokens = tokenize_entry(words)
            for i, token in enumerate(tokens):
                if token not in results['tokens_analyzed']:
                    continue
                for j in range(max(0, i - window), min(len(tokens), i + window + 1)):
                    if i != j and tokens[j] in results['tokens_analyzed']:
                        pair = tuple(sorted([token, tokens[j]]))
                        adjacency_counts[pair] += 1
                        token_adjacency_totals[token] += 1

    # Calculate expected under independence
    total_adjacencies = sum(adjacency_counts.values())

    for t1, t2 in combinations(results['tokens_analyzed'], 2):
        pair = tuple(sorted([t1, t2]))
        observed = adjacency_counts.get(pair, 0)

        p1 = freq[t1] / total_tokens
        p2 = freq[t2] / total_tokens
        expected = p1 * p2 * total_adjacencies * 2

        results['observed'][f"{t1}|{t2}"] = observed
        results['expected'][f"{t1}|{t2}"] = expected

        if expected > 0:
            exclusion = (expected - observed) / expected
        else:
            exclusion = 0 if observed == 0 else -1

        results['exclusion_scores'][f"{t1}|{t2}"] = exclusion

    # Identify strong exclusions
    for pair_str, score in results['exclusion_scores'].items():
        t1, t2 = pair_str.split('|')
        observed = results['observed'][pair_str]
        expected = results['expected'][pair_str]

        if expected >= 5:
            if observed == 0:
                results['strong_exclusions'].append({
                    'pair': [t1, t2],
                    'observed': observed,
                    'expected': round(expected, 2),
                    'exclusion_score': score,
                    'interpretation': 'COMPLETE EXCLUSION'
                })
            elif observed < expected * 0.2:
                results['strong_exclusions'].append({
                    'pair': [t1, t2],
                    'observed': observed,
                    'expected': round(expected, 2),
                    'exclusion_score': score,
                    'interpretation': 'STRONG EXCLUSION'
                })

        if expected > 0 and observed > expected * 3:
            results['strong_attractions'].append({
                'pair': [t1, t2],
                'observed': observed,
                'expected': round(expected, 2),
                'attraction_ratio': observed / expected,
                'interpretation': 'STRONG ATTRACTION'
            })

    results['strong_exclusions'].sort(key=lambda x: x['exclusion_score'], reverse=True)
    results['strong_attractions'].sort(key=lambda x: x['attraction_ratio'], reverse=True)

    return results


# =============================================================================
# STEP 2: IDENTIFY MUTUAL EXCLUSION CLUSTERS
# =============================================================================

def identify_exclusion_clusters(cooccurrence_results, hub_words):
    """Find clusters of mutually exclusive tokens."""
    results = {
        'hub_exclusions': [],
        'daiin_exclusions': [],
        'other_exclusions': [],
        'mutual_exclusion_groups': [],
        'high_excluders': []
    }

    strong_exclusions = cooccurrence_results.get('strong_exclusions', [])

    for exc in strong_exclusions:
        t1, t2 = exc['pair']
        if t1 in hub_words or t2 in hub_words:
            results['hub_exclusions'].append(exc)
        elif 'daiin' in [t1, t2]:
            results['daiin_exclusions'].append(exc)
        else:
            results['other_exclusions'].append(exc)

    # Build exclusion graph
    exclusion_graph = defaultdict(set)
    for exc in strong_exclusions:
        t1, t2 = exc['pair']
        exclusion_graph[t1].add(t2)
        exclusion_graph[t2].add(t1)

    exclusion_counts = {token: len(excluded) for token, excluded in exclusion_graph.items()}

    high_excluders = [
        {'token': t, 'excludes_count': c, 'excludes': list(exclusion_graph[t])[:10]}
        for t, c in sorted(exclusion_counts.items(), key=lambda x: -x[1])
        if c >= 3
    ]

    results['high_excluders'] = high_excluders
    results['mutual_exclusion_groups'] = find_exclusion_groups(exclusion_graph)
    results['exclusion_graph'] = {k: list(v) for k, v in exclusion_graph.items()}

    return results


def find_exclusion_groups(exclusion_graph):
    """Find groups of tokens that mutually exclude each other."""
    groups = []
    tokens = list(exclusion_graph.keys())

    for i, t1 in enumerate(tokens):
        for j, t2 in enumerate(tokens[i+1:], i+1):
            if t2 not in exclusion_graph[t1]:
                continue
            for t3 in tokens[j+1:]:
                if t3 in exclusion_graph[t1] and t3 in exclusion_graph[t2]:
                    groups.append({
                        'tokens': [t1, t2, t3],
                        'type': 'mutual_triple'
                    })

    seen = set()
    unique_groups = []
    for g in groups:
        key = tuple(sorted(g['tokens']))
        if key not in seen:
            seen.add(key)
            unique_groups.append(g)

    return unique_groups[:20]


# =============================================================================
# STEP 3: ASSIGN PROVISIONAL SYNTACTIC LAYERS
# =============================================================================

def assign_syntactic_layers(cooccurrence_results, exclusion_clusters, freq, hub_words):
    """
    Assign tokens to provisional syntactic layers based on exclusion patterns.

    Layer ALPHA: Hubs/categories - structural organizers
    Layer BETA: daiin-class operators - grammatical particles
    Layer GAMMA: Content tokens - semantic payload
    Layer DELTA: Unknown/ambiguous
    """
    results = {
        'layer_definitions': {
            'ALPHA': 'Hubs/categories - structural organizers',
            'BETA': 'daiin-class operators - grammatical particles',
            'GAMMA': 'Content tokens - semantic payload',
            'DELTA': 'Unknown/ambiguous'
        },
        'assignments': {},
        'layer_populations': {'ALPHA': [], 'BETA': [], 'GAMMA': [], 'DELTA': []},
        'confidence_scores': {},
        'assignment_rationale': {}
    }

    # ALPHA: Hub words
    for hub in hub_words:
        if hub in [t for t, c in freq.most_common(200)]:  # Only if frequent enough
            results['assignments'][hub] = 'ALPHA'
            results['layer_populations']['ALPHA'].append(hub)
            results['confidence_scores'][hub] = 1.0
            results['assignment_rationale'][hub] = 'Known hub word'

    # BETA: daiin and similar
    results['assignments']['daiin'] = 'BETA'
    results['layer_populations']['BETA'].append('daiin')
    results['confidence_scores']['daiin'] = 1.0
    results['assignment_rationale']['daiin'] = 'Primary grammatical particle (Phase 1)'

    # Find what daiin excludes
    daiin_excludes = set()
    for exc in cooccurrence_results.get('strong_exclusions', []):
        if 'daiin' in exc['pair']:
            other = exc['pair'][0] if exc['pair'][1] == 'daiin' else exc['pair'][1]
            daiin_excludes.add(other)

    # Tokens that exclude the SAME things as daiin might be BETA
    for exc in exclusion_clusters.get('high_excluders', []):
        token = exc['token']
        if token in results['assignments']:
            continue

        token_excludes = set(exc['excludes'])
        overlap_with_daiin = len(token_excludes & daiin_excludes)

        if overlap_with_daiin >= 2 and token not in hub_words:
            results['assignments'][token] = 'BETA'
            results['layer_populations']['BETA'].append(token)
            results['confidence_scores'][token] = 0.7
            results['assignment_rationale'][token] = f'Excludes {overlap_with_daiin} same tokens as daiin'

    # GAMMA: Tokens attracted to daiin (content words)
    for att in cooccurrence_results.get('strong_attractions', []):
        t1, t2 = att['pair']
        if 'daiin' in [t1, t2]:
            content_word = t1 if t2 == 'daiin' else t2
            if content_word not in results['assignments']:
                results['assignments'][content_word] = 'GAMMA'
                results['layer_populations']['GAMMA'].append(content_word)
                results['confidence_scores'][content_word] = 0.8
                results['assignment_rationale'][content_word] = f'Strong attraction to daiin (ratio {att["attraction_ratio"]:.1f})'

    # DELTA: Remaining frequent tokens
    for token in cooccurrence_results.get('tokens_analyzed', []):
        if token not in results['assignments']:
            results['assignments'][token] = 'DELTA'
            results['layer_populations']['DELTA'].append(token)
            results['confidence_scores'][token] = 0.3
            results['assignment_rationale'][token] = 'No clear exclusion/attraction pattern'

    results['summary'] = {
        'ALPHA_count': len(results['layer_populations']['ALPHA']),
        'BETA_count': len(results['layer_populations']['BETA']),
        'GAMMA_count': len(results['layer_populations']['GAMMA']),
        'DELTA_count': len(results['layer_populations']['DELTA']),
        'total_assigned': len(results['assignments'])
    }

    return results


# =============================================================================
# STEP 4: MAP LEGAL LAYER ADJACENCIES
# =============================================================================

def map_layer_adjacencies(a_entries, b_entries, layer_assignments):
    """Determine which layers can legally touch (appear adjacent)."""
    results = {
        'adjacency_counts': {},
        'adjacency_probabilities': {},
        'legal_transitions': [],
        'forbidden_transitions': [],
        'transition_matrix': {}
    }

    assignments = layer_assignments.get('assignments', {})

    layer_bigrams = defaultdict(int)
    layer_unigrams = defaultdict(int)

    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            tokens = tokenize_entry(words)
            prev_layer = None

            for token in tokens:
                curr_layer = assignments.get(token, 'UNKNOWN')
                layer_unigrams[curr_layer] += 1

                if prev_layer is not None:
                    bigram = f"{prev_layer}->{curr_layer}"
                    layer_bigrams[bigram] += 1

                prev_layer = curr_layer

    results['adjacency_counts'] = dict(layer_bigrams)

    layers = ['ALPHA', 'BETA', 'GAMMA', 'DELTA', 'UNKNOWN']
    total_transitions = sum(layer_bigrams.values())

    for l1 in layers:
        l1_total = sum(c for bg, c in layer_bigrams.items() if bg.startswith(f"{l1}->"))
        for l2 in layers:
            bigram = f"{l1}->{l2}"
            count = layer_bigrams.get(bigram, 0)
            prob = count / l1_total if l1_total > 0 else 0

            results['adjacency_probabilities'][bigram] = {
                'count': count,
                'probability': prob,
                'l1_total': l1_total
            }

            if l1 not in results['transition_matrix']:
                results['transition_matrix'][l1] = {}
            results['transition_matrix'][l1][l2] = prob

    # Identify legal vs forbidden transitions
    total_unigrams = sum(layer_unigrams.values())
    for bigram, data in results['adjacency_probabilities'].items():
        l1, l2 = bigram.split('->')

        p_l2 = layer_unigrams.get(l2, 0) / total_unigrams if total_unigrams else 0
        observed_prob = data['probability']

        if data['count'] == 0 and data['l1_total'] >= 10:
            results['forbidden_transitions'].append({
                'transition': bigram,
                'interpretation': f'{l1} NEVER followed by {l2}'
            })
        elif observed_prob > p_l2 * 2 and data['count'] >= 5:
            results['legal_transitions'].append({
                'transition': bigram,
                'probability': observed_prob,
                'lift': observed_prob / p_l2 if p_l2 > 0 else float('inf'),
                'interpretation': f'{l1} preferentially followed by {l2}'
            })

    results['legal_transitions'].sort(key=lambda x: x.get('lift', 0), reverse=True)

    return results


# =============================================================================
# STEP 5: SYNTHESIS & INTERPRETATION
# =============================================================================

def generate_layer_synthesis(cooccurrence, exclusion_clusters, layer_assignments, adjacencies):
    """Generate overall synthesis of layer analysis."""
    synthesis = {
        'phase': 'Phase 2A: Forbidden Adjacency & Layer Map',
        'timestamp': datetime.now().isoformat(),
        'key_findings': [],
        'layer_model': {},
        'grammar_rules': [],
        'implications_for_phase3': [],
        'resonance_assessment': {}
    }

    n_exclusions = len(cooccurrence.get('strong_exclusions', []))
    n_attractions = len(cooccurrence.get('strong_attractions', []))
    synthesis['key_findings'].append(
        f"Found {n_exclusions} strong exclusions and {n_attractions} strong attractions"
    )

    summary = layer_assignments.get('summary', {})
    synthesis['layer_model'] = {
        'ALPHA (structural)': summary.get('ALPHA_count', 0),
        'BETA (grammatical)': summary.get('BETA_count', 0),
        'GAMMA (content)': summary.get('GAMMA_count', 0),
        'DELTA (unknown)': summary.get('DELTA_count', 0)
    }

    for trans in adjacencies.get('legal_transitions', [])[:5]:
        synthesis['grammar_rules'].append(
            f"LEGAL: {trans['transition']} (p={trans['probability']:.2f}, lift={trans.get('lift', 0):.1f}x)"
        )

    for trans in adjacencies.get('forbidden_transitions', [])[:5]:
        synthesis['grammar_rules'].append(
            f"FORBIDDEN: {trans['transition']}"
        )

    alpha_count = summary.get('ALPHA_count', 0)
    beta_count = summary.get('BETA_count', 0)
    gamma_count = summary.get('GAMMA_count', 0)

    if gamma_count > 0:
        synthesis['implications_for_phase3'].append(
            f"GAMMA layer ({gamma_count} tokens) is candidate semantic payload - "
            "calculate information density for GAMMA only"
        )

    if beta_count > 1:
        synthesis['implications_for_phase3'].append(
            f"BETA layer ({beta_count} tokens) may be grammatical overhead - "
            "subtract from semantic capacity calculation"
        )

    # Check for clean ALPHA-BETA separation
    forbidden = adjacencies.get('forbidden_transitions', [])
    alpha_beta_forbidden = any(
        'ALPHA->BETA' in t['transition'] or 'BETA->ALPHA' in t['transition']
        for t in forbidden
    )

    if alpha_beta_forbidden:
        synthesis['key_findings'].append(
            "CRITICAL: ALPHA and BETA layers are mutually exclusive - "
            "confirms two-layer grammatical structure"
        )
        synthesis['resonance_assessment']['layer_separation'] = 'GREEN'
    else:
        # Check if they're at least rare
        alpha_beta_prob = adjacencies['transition_matrix'].get('ALPHA', {}).get('BETA', 0)
        beta_alpha_prob = adjacencies['transition_matrix'].get('BETA', {}).get('ALPHA', 0)
        if alpha_beta_prob < 0.05 and beta_alpha_prob < 0.05:
            synthesis['key_findings'].append(
                f"ALPHA-BETA transitions rare (p={alpha_beta_prob:.3f}, {beta_alpha_prob:.3f}) - "
                "suggests weak layer separation"
            )
            synthesis['resonance_assessment']['layer_separation'] = 'YELLOW'
        else:
            synthesis['resonance_assessment']['layer_separation'] = 'RED'

    # Check for daiin-specific patterns
    daiin_exclusions = exclusion_clusters.get('daiin_exclusions', [])
    if len(daiin_exclusions) >= 5:
        synthesis['key_findings'].append(
            f"daiin has {len(daiin_exclusions)} strong exclusions - confirms distinct grammatical role"
        )
        synthesis['resonance_assessment']['daiin_isolation'] = 'GREEN'
    elif len(daiin_exclusions) >= 2:
        synthesis['resonance_assessment']['daiin_isolation'] = 'YELLOW'
    else:
        synthesis['resonance_assessment']['daiin_isolation'] = 'RED'

    # Check BETA layer discovery
    beta_tokens = layer_assignments['layer_populations'].get('BETA', [])
    if len(beta_tokens) > 1:
        synthesis['key_findings'].append(
            f"Discovered {len(beta_tokens)-1} additional BETA-class tokens: {beta_tokens[1:]}"
        )
        synthesis['resonance_assessment']['beta_expansion'] = 'GREEN'
    else:
        synthesis['resonance_assessment']['beta_expansion'] = 'YELLOW'

    # Overall resonance
    green_count = sum(1 for v in synthesis['resonance_assessment'].values() if v == 'GREEN')
    if green_count >= 2:
        synthesis['resonance_assessment']['overall'] = "GREEN - Multiple new structural insights"
    elif green_count == 1:
        synthesis['resonance_assessment']['overall'] = "YELLOW - Some new insights"
    else:
        synthesis['resonance_assessment']['overall'] = "RED - No significant new structure"

    return synthesis


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_phase_2a():
    """Execute Phase 2A: Forbidden Adjacency & Layer Map."""
    print("=" * 60)
    print("PHASE 2A: FORBIDDEN ADJACENCY & LAYER MAP")
    print("=" * 60)

    print("\nLoading corpus...")
    words = load_corpus()
    entries = group_by_entries(words)
    a_entries, b_entries = split_by_currier(entries)

    all_tokens, freq = get_all_tokens(a_entries, b_entries)
    print(f"Total tokens: {len(all_tokens)}, Unique: {len(freq)}")
    print(f"Entries: {len(a_entries)} A, {len(b_entries)} B")

    hub_words = {'tol', 'pol', 'sho', 'tor', 'kor', 'par', 'pchor', 'paiin'}

    all_results = {}

    # Step 1: Co-occurrence exclusion matrix
    print("\n" + "-" * 40)
    print("Step 1: Building co-occurrence exclusion matrix...")
    print("-" * 40)
    cooccurrence = build_cooccurrence_matrix(a_entries, b_entries, min_freq=20, window=1)
    all_results['cooccurrence'] = cooccurrence
    print(f"Tokens analyzed: {len(cooccurrence['tokens_analyzed'])}")
    print(f"Strong exclusions found: {len(cooccurrence['strong_exclusions'])}")
    print(f"Strong attractions found: {len(cooccurrence['strong_attractions'])}")

    print("\nTop 10 exclusions:")
    for exc in cooccurrence['strong_exclusions'][:10]:
        print(f"  {exc['pair'][0]} <-> {exc['pair'][1]}: "
              f"observed={exc['observed']}, expected={exc['expected']:.1f} [{exc['interpretation']}]")

    print("\nTop 10 attractions:")
    for att in cooccurrence['strong_attractions'][:10]:
        print(f"  {att['pair'][0]} <-> {att['pair'][1]}: "
              f"observed={att['observed']}, expected={att['expected']:.1f}, ratio={att['attraction_ratio']:.1f}x")

    # Step 2: Identify exclusion clusters
    print("\n" + "-" * 40)
    print("Step 2: Identifying exclusion clusters...")
    print("-" * 40)
    exclusion_clusters = identify_exclusion_clusters(cooccurrence, hub_words)
    all_results['exclusion_clusters'] = exclusion_clusters
    print(f"Hub-related exclusions: {len(exclusion_clusters['hub_exclusions'])}")
    print(f"daiin-related exclusions: {len(exclusion_clusters['daiin_exclusions'])}")
    print(f"High excluders (>=3 exclusions): {len(exclusion_clusters['high_excluders'])}")

    print("\nHigh excluders:")
    for he in exclusion_clusters['high_excluders'][:10]:
        print(f"  {he['token']}: excludes {he['excludes_count']} tokens -> {he['excludes'][:5]}...")

    # Step 3: Assign syntactic layers
    print("\n" + "-" * 40)
    print("Step 3: Assigning provisional syntactic layers...")
    print("-" * 40)
    layer_assignments = assign_syntactic_layers(
        cooccurrence, exclusion_clusters, freq, hub_words
    )
    all_results['layer_assignments'] = layer_assignments
    print("Layer populations:")
    for layer, count in layer_assignments['summary'].items():
        print(f"  {layer}: {count}")

    print("\nALPHA layer (structural/hubs):")
    for token in layer_assignments['layer_populations']['ALPHA']:
        print(f"  {token}")

    print("\nBETA layer (grammatical particles):")
    for token in layer_assignments['layer_populations']['BETA'][:15]:
        rationale = layer_assignments['assignment_rationale'].get(token, '')
        print(f"  {token}: {rationale}")

    print("\nGAMMA layer (content - attracted to daiin):")
    for token in layer_assignments['layer_populations']['GAMMA'][:10]:
        rationale = layer_assignments['assignment_rationale'].get(token, '')
        print(f"  {token}: {rationale}")

    # Step 4: Map layer adjacencies
    print("\n" + "-" * 40)
    print("Step 4: Mapping legal layer adjacencies...")
    print("-" * 40)
    adjacencies = map_layer_adjacencies(a_entries, b_entries, layer_assignments)
    all_results['adjacencies'] = adjacencies

    print("\nTransition matrix P(col|row):")
    matrix = adjacencies['transition_matrix']
    layers = ['ALPHA', 'BETA', 'GAMMA', 'DELTA', 'UNKNOWN']
    header = "         " + "  ".join(f"{l:>8}" for l in layers)
    print(header)
    for l1 in layers:
        row = f"{l1:>8} "
        for l2 in layers:
            prob = matrix.get(l1, {}).get(l2, 0)
            row += f"  {prob:>7.3f}"
        print(row)

    print(f"\nForbidden transitions ({len(adjacencies['forbidden_transitions'])}):")
    for trans in adjacencies['forbidden_transitions'][:10]:
        print(f"  {trans['transition']}: {trans['interpretation']}")

    print(f"\nPreferred transitions ({len(adjacencies['legal_transitions'])}):")
    for trans in adjacencies['legal_transitions'][:10]:
        print(f"  {trans['transition']}: lift={trans['lift']:.1f}x")

    # Step 5: Synthesis
    print("\n" + "-" * 40)
    print("Step 5: Generating synthesis...")
    print("-" * 40)
    synthesis = generate_layer_synthesis(
        cooccurrence, exclusion_clusters, layer_assignments, adjacencies
    )
    all_results['synthesis'] = synthesis

    # Save results
    output_dir = Path('.')

    for name, data in all_results.items():
        output_path = output_dir / f'phase2a_{name}.json'
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"[OK] Saved {output_path}")

    full_output = output_dir / 'phase2a_full_results.json'
    with open(full_output, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"[OK] Saved {full_output}")

    return all_results


if __name__ == '__main__':
    results = run_phase_2a()

    synthesis = results.get('synthesis', {})

    print("\n" + "=" * 60)
    print("PHASE 2A COMPLETE")
    print("=" * 60)

    print("\nKEY FINDINGS:")
    for finding in synthesis.get('key_findings', []):
        print(f"  * {finding}")

    print("\nLAYER MODEL:")
    for layer, count in synthesis.get('layer_model', {}).items():
        print(f"  {layer}: {count} tokens")

    print("\nGRAMMAR RULES DISCOVERED:")
    for rule in synthesis.get('grammar_rules', []):
        print(f"  {rule}")

    print("\nIMPLICATIONS FOR PHASE 3:")
    for impl in synthesis.get('implications_for_phase3', []):
        print(f"  > {impl}")

    print("\nRESONANCE ASSESSMENT:")
    for aspect, rating in synthesis.get('resonance_assessment', {}).items():
        print(f"  {aspect}: {rating}")
