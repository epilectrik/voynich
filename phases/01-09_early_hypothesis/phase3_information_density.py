#!/usr/bin/env python3
"""
PHASE 3: INFORMATION DENSITY AUTOPSY (GAMMA-FOCUSED)
=====================================================

Phase 2A isolated 77 GAMMA tokens as candidate semantic payload.
Now we test: Is this payload class information-dense enough to carry meaning?

Three possible outcomes:
1. GAMMA has capacity for full semantics -> meaning exists but is encoded
2. GAMMA has capacity for partial semantics -> mnemonic/shorthand system
3. GAMMA lacks capacity even for minimal semantics -> meaning compressed out
"""

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from itertools import combinations
from datetime import datetime

# =============================================================================
# DATA LOADING
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


def load_phase2a_results():
    """Load GAMMA tokens from Phase 2A."""
    try:
        with open('phase2a_layer_assignments.json', 'r') as f:
            assignments = json.load(f)
        gamma_tokens = set(assignments.get('layer_populations', {}).get('GAMMA', []))
        return gamma_tokens, assignments
    except FileNotFoundError:
        print("WARNING: Phase 2A results not found")
        return None, None


# =============================================================================
# MEASURE 1: GAMMA-ONLY INFORMATION CAPACITY
# =============================================================================

def measure_gamma_information_capacity(a_entries, b_entries, gamma_tokens):
    """Calculate information capacity metrics for GAMMA tokens only."""
    results = {
        'measure': 'gamma_information_capacity',
        'gamma_token_count': len(gamma_tokens),
        'metrics': {},
        'per_entry_stats': {},
        'comparison_to_full_corpus': {}
    }

    gamma_per_entry = []
    total_tokens_per_entry = []
    all_gamma_tokens = []
    all_tokens = []

    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            tokens = tokenize_entry(words)
            all_tokens.extend(tokens)

            gamma_in_entry = [t for t in tokens if t in gamma_tokens]
            all_gamma_tokens.extend(gamma_in_entry)

            gamma_per_entry.append(len(gamma_in_entry))
            total_tokens_per_entry.append(len(tokens))

    # Basic counts
    results['metrics']['total_gamma_occurrences'] = len(all_gamma_tokens)
    results['metrics']['unique_gamma_types'] = len(set(all_gamma_tokens))
    results['metrics']['gamma_vocabulary_utilization'] = (
        len(set(all_gamma_tokens)) / len(gamma_tokens)
        if gamma_tokens else 0
    )

    # Entropy of GAMMA distribution
    gamma_freq = Counter(all_gamma_tokens)
    total_gamma = sum(gamma_freq.values())

    if total_gamma > 0:
        gamma_entropy = -sum(
            (c / total_gamma) * math.log2(c / total_gamma)
            for c in gamma_freq.values() if c > 0
        )
        max_entropy = math.log2(len(gamma_freq)) if len(gamma_freq) > 1 else 1
        normalized_entropy = gamma_entropy / max_entropy if max_entropy > 0 else 0
    else:
        gamma_entropy = 0
        normalized_entropy = 0

    results['metrics']['gamma_entropy_bits'] = gamma_entropy
    results['metrics']['gamma_max_entropy_bits'] = math.log2(len(gamma_tokens)) if gamma_tokens else 0
    results['metrics']['gamma_normalized_entropy'] = normalized_entropy
    results['metrics']['bits_per_gamma_token'] = gamma_entropy

    # Per-entry statistics
    results['per_entry_stats'] = {
        'avg_gamma_per_entry': sum(gamma_per_entry) / len(gamma_per_entry) if gamma_per_entry else 0,
        'median_gamma_per_entry': sorted(gamma_per_entry)[len(gamma_per_entry)//2] if gamma_per_entry else 0,
        'max_gamma_per_entry': max(gamma_per_entry) if gamma_per_entry else 0,
        'min_gamma_per_entry': min(gamma_per_entry) if gamma_per_entry else 0,
        'entries_with_zero_gamma': sum(1 for g in gamma_per_entry if g == 0),
        'avg_total_tokens_per_entry': sum(total_tokens_per_entry) / len(total_tokens_per_entry) if total_tokens_per_entry else 0
    }

    gamma_fraction = (
        sum(gamma_per_entry) / sum(total_tokens_per_entry)
        if sum(total_tokens_per_entry) > 0 else 0
    )
    results['per_entry_stats']['gamma_fraction_of_text'] = gamma_fraction

    avg_gamma = results['per_entry_stats']['avg_gamma_per_entry']
    results['per_entry_stats']['gamma_bits_per_entry'] = avg_gamma * gamma_entropy

    # Compare to full corpus
    full_freq = Counter(all_tokens)
    total_full = sum(full_freq.values())
    full_entropy = -sum(
        (c / total_full) * math.log2(c / total_full)
        for c in full_freq.values() if c > 0
    ) if total_full > 0 else 0

    results['comparison_to_full_corpus'] = {
        'full_corpus_entropy': full_entropy,
        'gamma_entropy': gamma_entropy,
        'entropy_ratio': gamma_entropy / full_entropy if full_entropy > 0 else 0,
        'gamma_is_more_uniform': normalized_entropy > 0.8,
        'interpretation': interpret_entropy_comparison(gamma_entropy, full_entropy, normalized_entropy)
    }

    return results


def interpret_entropy_comparison(gamma_entropy, full_entropy, normalized):
    """Interpret what the entropy comparison means."""
    if normalized > 0.9:
        return "GAMMA tokens near-uniformly distributed - maximum information density"
    elif normalized > 0.7:
        return "GAMMA tokens show moderate concentration - good diversity"
    elif normalized > 0.5:
        return "GAMMA tokens show significant skew - reduced effective vocabulary"
    else:
        return "GAMMA tokens highly concentrated - very few tokens carry most load"


# =============================================================================
# MEASURE 2: THREE-TIER SEMANTIC LOAD TEST
# =============================================================================

def measure_semantic_load_capacity(gamma_capacity_results, num_entries):
    """Test whether GAMMA can carry semantic load under three models."""
    results = {
        'measure': 'semantic_load_capacity',
        'models': {},
        'gamma_capacity': {},
        'verdicts': {},
        'overall_interpretation': ''
    }

    gamma_bits_per_entry = gamma_capacity_results['per_entry_stats'].get('gamma_bits_per_entry', 0)
    avg_gamma_tokens = gamma_capacity_results['per_entry_stats'].get('avg_gamma_per_entry', 0)
    gamma_vocab_size = gamma_capacity_results['metrics'].get('unique_gamma_types', 0)

    results['gamma_capacity'] = {
        'bits_per_entry': gamma_bits_per_entry,
        'avg_tokens_per_entry': avg_gamma_tokens,
        'vocabulary_size': gamma_vocab_size,
        'theoretical_max_bits': math.log2(gamma_vocab_size) * avg_gamma_tokens if gamma_vocab_size > 1 else 0
    }

    models = {
        'ENCYCLOPEDIC': {
            'description': 'Full plant description (name, family, habitat, appearance, parts, uses, preparation, cautions)',
            'concepts': 8,
            'bits_per_concept': 10,
            'total_bits_needed': 80,
            'example': 'A complete herbal entry with all details'
        },
        'PRACTITIONER': {
            'description': 'Working notes (identification hint, primary use, preparation method)',
            'concepts': 4,
            'bits_per_concept': 8,
            'total_bits_needed': 32,
            'example': 'A physicians quick reference card'
        },
        'INDEX': {
            'description': 'Memory aid (category pointer, recall trigger)',
            'concepts': 2,
            'bits_per_concept': 6,
            'total_bits_needed': 12,
            'example': 'A mnemonic index requiring external knowledge'
        }
    }

    results['models'] = models

    for model_name, model in models.items():
        needed = model['total_bits_needed']
        available = gamma_bits_per_entry
        theoretical_max = results['gamma_capacity']['theoretical_max_bits']

        actual_sufficient = available >= needed
        theoretical_sufficient = theoretical_max >= needed
        capacity_ratio = available / needed if needed > 0 else float('inf')

        results['verdicts'][model_name] = {
            'bits_needed': needed,
            'bits_available': round(available, 2),
            'theoretical_max': round(theoretical_max, 2),
            'actual_sufficient': actual_sufficient,
            'theoretical_sufficient': theoretical_sufficient,
            'capacity_ratio': round(capacity_ratio, 3),
            'headroom_bits': round(available - needed, 2),
            'interpretation': interpret_model_fit(
                model_name, actual_sufficient, theoretical_sufficient, capacity_ratio
            )
        }

    results['overall_interpretation'] = generate_load_interpretation(results['verdicts'])

    return results


def interpret_model_fit(model_name, actual_ok, theoretical_ok, ratio):
    """Interpret capacity fit for a single model."""
    if actual_ok:
        return f"GAMMA CAN encode {model_name} content (ratio={ratio:.2f}x needed)"
    elif theoretical_ok:
        return f"GAMMA COULD theoretically encode {model_name}, but observed usage is too skewed"
    else:
        return f"GAMMA CANNOT encode {model_name} content even theoretically (only {ratio:.1%} of needed)"


def generate_load_interpretation(verdicts):
    """Generate overall semantic load interpretation."""
    enc = verdicts.get('ENCYCLOPEDIC', {})
    pra = verdicts.get('PRACTITIONER', {})
    idx = verdicts.get('INDEX', {})

    if enc.get('actual_sufficient'):
        return (
            "SURPRISING: GAMMA has capacity for full encyclopedic content. "
            "Semantics likely exist but are encoded within the 77 token vocabulary."
        )
    elif pra.get('actual_sufficient'):
        return (
            "GAMMA can encode PRACTITIONER-level content but not encyclopedic. "
            "Consistent with working notes, shorthand, or practical reference."
        )
    elif idx.get('actual_sufficient'):
        return (
            "GAMMA can only encode INDEX-level content. "
            "Text likely functions as memory aid requiring external oral tradition."
        )
    elif idx.get('theoretical_sufficient'):
        return (
            "GAMMA could theoretically encode index-level content, but observed "
            "distribution is too skewed. Semantic recovery probably blocked."
        )
    else:
        return (
            "CRITICAL: GAMMA cannot encode even minimal semantic content. "
            "The 77-token payload lacks capacity for independent meaning."
        )


# =============================================================================
# MEASURE 3: GAMMA INTERNAL STRUCTURE
# =============================================================================

def measure_gamma_internal_structure(a_entries, b_entries, gamma_tokens):
    """Analyze whether GAMMA tokens have meaningful internal structure."""
    results = {
        'measure': 'gamma_internal_structure',
        'morphological_analysis': {},
        'clustering': {},
        'cooccurrence_within_gamma': {},
        'independence_test': {},
        'interpretation': ''
    }

    gamma_list = list(gamma_tokens)

    # Prefix analysis
    prefix_groups = defaultdict(list)
    for token in gamma_list:
        if len(token) >= 2:
            prefix_groups[token[:2]].append(token)

    # Suffix analysis
    suffix_groups = defaultdict(list)
    for token in gamma_list:
        if len(token) >= 2:
            suffix_groups[token[-2:]].append(token)

    results['morphological_analysis'] = {
        'prefix_groups': {
            k: {'tokens': v, 'count': len(v)}
            for k, v in sorted(prefix_groups.items(), key=lambda x: -len(x[1]))[:10]
        },
        'suffix_groups': {
            k: {'tokens': v, 'count': len(v)}
            for k, v in sorted(suffix_groups.items(), key=lambda x: -len(x[1]))[:10]
        },
        'avg_token_length': sum(len(t) for t in gamma_list) / len(gamma_list) if gamma_list else 0,
        'length_distribution': dict(Counter(len(t) for t in gamma_list))
    }

    largest_prefix_group = max(len(v) for v in prefix_groups.values()) if prefix_groups else 0
    largest_suffix_group = max(len(v) for v in suffix_groups.values()) if suffix_groups else 0

    results['morphological_analysis']['largest_prefix_group'] = largest_prefix_group
    results['morphological_analysis']['largest_suffix_group'] = largest_suffix_group
    results['morphological_analysis']['morphology_productive'] = (
        largest_prefix_group >= 5 or largest_suffix_group >= 5
    )

    # Co-occurrence within GAMMA
    gamma_cooccurrence = defaultdict(int)
    gamma_in_same_entry = defaultdict(int)

    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            tokens = tokenize_entry(words)
            gamma_in_entry = [t for t in tokens if t in gamma_tokens]

            for i in range(len(gamma_in_entry) - 1):
                pair = tuple(sorted([gamma_in_entry[i], gamma_in_entry[i+1]]))
                gamma_cooccurrence[pair] += 1

            for t1, t2 in combinations(set(gamma_in_entry), 2):
                pair = tuple(sorted([t1, t2]))
                gamma_in_same_entry[pair] += 1

    top_adjacent = sorted(gamma_cooccurrence.items(), key=lambda x: -x[1])[:20]
    top_cooccur = sorted(gamma_in_same_entry.items(), key=lambda x: -x[1])[:20]

    results['cooccurrence_within_gamma'] = {
        'adjacent_pairs': [{'pair': list(p), 'count': c} for p, c in top_adjacent],
        'same_entry_pairs': [{'pair': list(p), 'count': c} for p, c in top_cooccur],
        'total_adjacent_pairs': len(gamma_cooccurrence),
        'total_cooccur_pairs': len(gamma_in_same_entry)
    }

    # Independence test: mutual information
    gamma_freq = Counter()
    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            tokens = tokenize_entry(words)
            gamma_freq.update(t for t in tokens if t in gamma_tokens)

    total_gamma_occ = sum(gamma_freq.values())

    mi_sum = 0
    mi_count = 0

    for (t1, t2), joint_count in gamma_cooccurrence.items():
        if joint_count >= 2:
            p_joint = joint_count / total_gamma_occ
            p_t1 = gamma_freq[t1] / total_gamma_occ
            p_t2 = gamma_freq[t2] / total_gamma_occ

            if p_t1 > 0 and p_t2 > 0 and p_joint > 0:
                mi = p_joint * math.log2(p_joint / (p_t1 * p_t2))
                mi_sum += mi
                mi_count += 1

    avg_mi = mi_sum / mi_count if mi_count > 0 else 0

    results['independence_test'] = {
        'average_mutual_information': avg_mi,
        'mi_interpretation': interpret_mutual_information(avg_mi),
        'pairs_tested': mi_count
    }

    results['interpretation'] = interpret_gamma_structure(results)

    return results


def interpret_mutual_information(mi):
    """Interpret mutual information value."""
    if mi > 0.5:
        return "HIGH mutual information - GAMMA tokens strongly predict each other"
    elif mi > 0.1:
        return "MODERATE mutual information - some predictive structure exists"
    elif mi > 0.01:
        return "LOW mutual information - weak dependencies, mostly independent"
    else:
        return "NEAR-ZERO mutual information - GAMMA tokens are essentially independent"


def interpret_gamma_structure(results):
    """Generate overall interpretation of GAMMA internal structure."""
    interpretations = []

    morph = results.get('morphological_analysis', {})
    if morph.get('morphology_productive'):
        interpretations.append(
            "GAMMA shows productive morphology (shared affixes) - compositional structure"
        )
    else:
        interpretations.append(
            "GAMMA lacks productive morphology - may be atomic labels"
        )

    indep = results.get('independence_test', {})
    mi = indep.get('average_mutual_information', 0)

    if mi > 0.1:
        interpretations.append(f"GAMMA tokens show mutual information ({mi:.3f}) - predictive sequences")
    else:
        interpretations.append(f"GAMMA tokens nearly independent (MI={mi:.3f}) - label system")

    return " | ".join(interpretations)


# =============================================================================
# MEASURE 4: GAMMA DISTRIBUTION ACROSS ENTRIES
# =============================================================================

def measure_gamma_distribution(a_entries, b_entries, gamma_tokens):
    """Analyze how GAMMA tokens distribute across entries."""
    results = {
        'measure': 'gamma_distribution',
        'entry_specificity': {},
        'section_distribution': {},
        'hub_correlation': {},
        'interpretation': ''
    }

    hub_words = {'tol', 'pol', 'sho', 'tor', 'kor', 'par', 'pchor', 'paiin'}

    gamma_to_entries = defaultdict(set)
    entry_to_gamma = defaultdict(set)
    gamma_in_a = Counter()
    gamma_in_b = Counter()
    gamma_with_hub = defaultdict(lambda: defaultdict(int))

    entry_id = 0
    for section_label, entries in [('A', a_entries), ('B', b_entries)]:
        for folio, words in entries.items():
            tokens = tokenize_entry(words)
            gamma_in_entry = [t for t in tokens if t in gamma_tokens]
            hubs_in_entry = [t for t in tokens if t in hub_words]

            for g in gamma_in_entry:
                gamma_to_entries[g].add(entry_id)
                entry_to_gamma[entry_id].add(g)

                if section_label == 'A':
                    gamma_in_a[g] += 1
                else:
                    gamma_in_b[g] += 1

                for h in hubs_in_entry:
                    gamma_with_hub[g][h] += 1

            entry_id += 1

    total_entries = entry_id

    entry_counts = [len(entries) for entries in gamma_to_entries.values()]

    results['entry_specificity'] = {
        'avg_entries_per_gamma': sum(entry_counts) / len(entry_counts) if entry_counts else 0,
        'max_entries_for_gamma': max(entry_counts) if entry_counts else 0,
        'min_entries_for_gamma': min(entry_counts) if entry_counts else 0,
        'gamma_appearing_once': sum(1 for c in entry_counts if c == 1),
        'gamma_appearing_widely': sum(1 for c in entry_counts if c >= total_entries * 0.1),
        'total_entries': total_entries
    }

    specificity = 1.0 - (
        results['entry_specificity']['avg_entries_per_gamma'] / total_entries
    ) if total_entries > 0 else 0
    results['entry_specificity']['specificity_ratio'] = specificity

    a_only = set(gamma_in_a.keys()) - set(gamma_in_b.keys())
    b_only = set(gamma_in_b.keys()) - set(gamma_in_a.keys())
    shared = set(gamma_in_a.keys()) & set(gamma_in_b.keys())

    results['section_distribution'] = {
        'a_only_gamma': len(a_only),
        'b_only_gamma': len(b_only),
        'shared_gamma': len(shared),
        'a_only_tokens': list(a_only)[:10],
        'b_only_tokens': list(b_only)[:10],
        'most_shared': [
            {'token': t, 'a_count': gamma_in_a[t], 'b_count': gamma_in_b[t]}
            for t in sorted(shared, key=lambda x: -(gamma_in_a[x] + gamma_in_b[x]))[:10]
        ]
    }

    hub_associations = []
    for gamma, hub_counts in gamma_with_hub.items():
        total = sum(hub_counts.values())
        if total >= 3:
            dominant_hub = max(hub_counts, key=hub_counts.get)
            dominance = hub_counts[dominant_hub] / total
            if dominance > 0.5:
                hub_associations.append({
                    'gamma': gamma,
                    'dominant_hub': dominant_hub,
                    'dominance': dominance,
                    'total_occurrences': total
                })

    results['hub_correlation'] = {
        'gamma_with_hub_preference': len(hub_associations),
        'associations': sorted(hub_associations, key=lambda x: -x['dominance'])[:15]
    }

    results['interpretation'] = interpret_gamma_distribution(results)

    return results


def interpret_gamma_distribution(results):
    """Interpret GAMMA distribution patterns."""
    interpretations = []

    spec = results.get('entry_specificity', {})
    specificity = spec.get('specificity_ratio', 0)

    if specificity > 0.8:
        interpretations.append("GAMMA tokens are highly entry-specific (encyclopedic pattern)")
    elif specificity > 0.5:
        interpretations.append("GAMMA tokens show moderate specificity (mix of shared/unique)")
    else:
        interpretations.append("GAMMA tokens widely shared across entries (index/shorthand)")

    sect = results.get('section_distribution', {})
    shared = sect.get('shared_gamma', 0)
    total = sect.get('a_only_gamma', 0) + sect.get('b_only_gamma', 0) + shared

    if total > 0:
        shared_ratio = shared / total
        if shared_ratio > 0.7:
            interpretations.append("Most GAMMA shared between A and B - unified vocabulary")
        elif shared_ratio < 0.3:
            interpretations.append("GAMMA vocabulary differs between A and B - distinct content")

    return " | ".join(interpretations)


# =============================================================================
# MEASURE 5: BASELINE COMPARISON
# =============================================================================

def measure_baseline_comparison(gamma_capacity, semantic_load, gamma_structure):
    """Compare GAMMA metrics to known systems."""
    results = {
        'measure': 'baseline_comparison',
        'comparisons': {},
        'best_match': '',
        'interpretation': ''
    }

    bits_per_entry = gamma_capacity['per_entry_stats'].get('gamma_bits_per_entry', 0)
    normalized_entropy = gamma_capacity['metrics'].get('gamma_normalized_entropy', 0)
    mi = gamma_structure['independence_test'].get('average_mutual_information', 0)

    baselines = {
        'NATURAL_LANGUAGE_CONTENT': {
            'description': 'Content words in natural language text',
            'expected_normalized_entropy': (0.7, 0.9),
            'expected_mi': (0.1, 0.5),
            'expected_bits_per_entry': (50, 200)
        },
        'TECHNICAL_TERMINOLOGY': {
            'description': 'Domain-specific technical vocabulary',
            'expected_normalized_entropy': (0.5, 0.8),
            'expected_mi': (0.05, 0.2),
            'expected_bits_per_entry': (20, 80)
        },
        'MNEMONIC_SYSTEM': {
            'description': 'Memory aid with limited vocabulary',
            'expected_normalized_entropy': (0.6, 0.95),
            'expected_mi': (0.01, 0.1),
            'expected_bits_per_entry': (10, 40)
        },
        'LABEL_SYSTEM': {
            'description': 'Categorical labels or markers',
            'expected_normalized_entropy': (0.8, 1.0),
            'expected_mi': (0.0, 0.05),
            'expected_bits_per_entry': (5, 20)
        },
        'CIPHER_OUTPUT': {
            'description': 'Encrypted natural language',
            'expected_normalized_entropy': (0.85, 1.0),
            'expected_mi': (0.0, 0.02),
            'expected_bits_per_entry': (30, 150)
        }
    }

    for name, baseline in baselines.items():
        scores = []

        ent_low, ent_high = baseline['expected_normalized_entropy']
        if ent_low <= normalized_entropy <= ent_high:
            scores.append(1.0)
        elif normalized_entropy < ent_low:
            scores.append(max(0, 1 - (ent_low - normalized_entropy)))
        else:
            scores.append(max(0, 1 - (normalized_entropy - ent_high)))

        mi_low, mi_high = baseline['expected_mi']
        if mi_low <= mi <= mi_high:
            scores.append(1.0)
        elif mi < mi_low:
            scores.append(max(0, 1 - (mi_low - mi) * 10))
        else:
            scores.append(max(0, 1 - (mi - mi_high) * 2))

        bits_low, bits_high = baseline['expected_bits_per_entry']
        if bits_low <= bits_per_entry <= bits_high:
            scores.append(1.0)
        elif bits_per_entry < bits_low:
            scores.append(max(0, bits_per_entry / bits_low))
        else:
            scores.append(max(0, bits_high / bits_per_entry))

        avg_score = sum(scores) / len(scores)

        results['comparisons'][name] = {
            'description': baseline['description'],
            'match_score': round(avg_score, 3),
            'component_scores': {
                'entropy': round(scores[0], 3),
                'mutual_information': round(scores[1], 3),
                'bits_per_entry': round(scores[2], 3)
            }
        }

    best = max(results['comparisons'], key=lambda x: results['comparisons'][x]['match_score'])
    results['best_match'] = {
        'system': best,
        'score': results['comparisons'][best]['match_score'],
        'description': results['comparisons'][best]['description']
    }

    results['interpretation'] = (
        f"GAMMA tokens most closely resemble {best} "
        f"(match score: {results['comparisons'][best]['match_score']:.2f})"
    )

    return results


# =============================================================================
# SYNTHESIS
# =============================================================================

def generate_phase3_synthesis(
    gamma_capacity, semantic_load, gamma_structure,
    gamma_distribution, baseline_comparison
):
    """Generate comprehensive Phase 3 synthesis."""
    synthesis = {
        'phase': 'Phase 3: Information Density Autopsy (GAMMA-Focused)',
        'timestamp': datetime.now().isoformat(),
        'central_question': 'Can the GAMMA payload carry semantic meaning?',
        'key_metrics': {},
        'verdicts': {},
        'implications': [],
        'next_steps': [],
        'resonance_assessment': {}
    }

    synthesis['key_metrics'] = {
        'gamma_vocabulary': gamma_capacity['metrics'].get('unique_gamma_types', 0),
        'bits_per_entry': round(gamma_capacity['per_entry_stats'].get('gamma_bits_per_entry', 0), 2),
        'normalized_entropy': round(gamma_capacity['metrics'].get('gamma_normalized_entropy', 0), 3),
        'mutual_information': round(gamma_structure['independence_test'].get('average_mutual_information', 0), 4),
        'specificity_ratio': round(gamma_distribution['entry_specificity'].get('specificity_ratio', 0), 3)
    }

    for model, verdict in semantic_load['verdicts'].items():
        synthesis['verdicts'][f'can_encode_{model.lower()}'] = verdict['actual_sufficient']

    synthesis['verdicts']['best_baseline_match'] = baseline_comparison['best_match']['system']
    synthesis['verdicts']['overall_semantic_capacity'] = semantic_load['overall_interpretation']

    can_encyclopedic = synthesis['verdicts'].get('can_encode_encyclopedic', False)
    can_practitioner = synthesis['verdicts'].get('can_encode_practitioner', False)
    can_index = synthesis['verdicts'].get('can_encode_index', False)

    if can_encyclopedic:
        synthesis['resonance_assessment']['semantic_capacity'] = 'GREEN - Full semantics possible'
        synthesis['implications'].append(
            "GAMMA has sufficient capacity for full semantic content"
        )
        synthesis['next_steps'].append("Attempt to map GAMMA tokens to semantic categories")
    elif can_practitioner:
        synthesis['resonance_assessment']['semantic_capacity'] = 'YELLOW - Partial semantics'
        synthesis['implications'].append(
            "GAMMA can encode practitioner-level content - shorthand system"
        )
        synthesis['next_steps'].append("Investigate what domain knowledge completes the system")
    elif can_index:
        synthesis['resonance_assessment']['semantic_capacity'] = 'YELLOW - Minimal semantics'
        synthesis['implications'].append(
            "GAMMA can only encode index-level content - memory aid"
        )
        synthesis['next_steps'].append("Treat text as scaffold, look for external meaning source")
    else:
        synthesis['resonance_assessment']['semantic_capacity'] = 'RED - Semantics probably absent'
        synthesis['implications'].append(
            "GAMMA lacks capacity for even minimal independent meaning"
        )
        synthesis['next_steps'].append("Investigate whether non-GAMMA layers carry meaning")
        synthesis['next_steps'].append("Consider that meaning may be unrecoverable by design")

    mi = synthesis['key_metrics']['mutual_information']
    if mi > 0.1:
        synthesis['resonance_assessment']['internal_structure'] = 'GREEN - Compositional'
        synthesis['implications'].append("GAMMA tokens form phrases, not isolated emissions")
    elif mi > 0.01:
        synthesis['resonance_assessment']['internal_structure'] = 'YELLOW - Weak structure'
    else:
        synthesis['resonance_assessment']['internal_structure'] = 'RED - Atomic/independent'
        synthesis['implications'].append("GAMMA tokens are independent - label system")

    green_count = sum(1 for v in synthesis['resonance_assessment'].values() if 'GREEN' in str(v))
    yellow_count = sum(1 for v in synthesis['resonance_assessment'].values() if 'YELLOW' in str(v))

    if green_count >= 2:
        synthesis['resonance_assessment']['overall'] = 'GREEN - Significant findings'
    elif green_count >= 1 or yellow_count >= 2:
        synthesis['resonance_assessment']['overall'] = 'YELLOW - Partial progress'
    else:
        synthesis['resonance_assessment']['overall'] = 'RED - Limited new insight'

    return synthesis


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_phase_3():
    """Execute Phase 3: Information Density Autopsy."""
    print("=" * 60)
    print("PHASE 3: INFORMATION DENSITY AUTOPSY (GAMMA-FOCUSED)")
    print("=" * 60)

    print("\nLoading corpus and Phase 2A results...")
    words = load_corpus()
    entries = group_by_entries(words)
    a_entries, b_entries = split_by_currier(entries)

    gamma_tokens, layer_assignments = load_phase2a_results()

    if gamma_tokens is None:
        print("ERROR: Could not load GAMMA tokens from Phase 2A")
        return None

    print(f"Loaded {len(gamma_tokens)} GAMMA tokens")
    print(f"Sample GAMMA tokens: {list(gamma_tokens)[:10]}")
    print(f"Entries: {len(a_entries)} A, {len(b_entries)} B")

    num_entries = len(a_entries) + len(b_entries)

    all_results = {}

    # Measure 1
    print("\n" + "-" * 40)
    print("Measure 1: GAMMA Information Capacity")
    print("-" * 40)
    gamma_capacity = measure_gamma_information_capacity(a_entries, b_entries, gamma_tokens)
    all_results['gamma_capacity'] = gamma_capacity

    print(f"GAMMA entropy: {gamma_capacity['metrics']['gamma_entropy_bits']:.2f} bits")
    print(f"Normalized entropy: {gamma_capacity['metrics']['gamma_normalized_entropy']:.3f}")
    print(f"Bits per entry (GAMMA only): {gamma_capacity['per_entry_stats']['gamma_bits_per_entry']:.2f}")
    print(f"GAMMA fraction of text: {gamma_capacity['per_entry_stats']['gamma_fraction_of_text']:.1%}")
    print(f"Avg GAMMA tokens per entry: {gamma_capacity['per_entry_stats']['avg_gamma_per_entry']:.1f}")

    # Measure 2
    print("\n" + "-" * 40)
    print("Measure 2: Three-Tier Semantic Load Test")
    print("-" * 40)
    semantic_load = measure_semantic_load_capacity(gamma_capacity, num_entries)
    all_results['semantic_load'] = semantic_load

    for model, verdict in semantic_load['verdicts'].items():
        status = "[OK]" if verdict['actual_sufficient'] else "[X]"
        print(f"  {status} {model}: {verdict['bits_available']:.1f} / {verdict['bits_needed']} bits "
              f"(ratio: {verdict['capacity_ratio']:.2f})")
    print(f"\nOverall: {semantic_load['overall_interpretation'][:100]}...")

    # Measure 3
    print("\n" + "-" * 40)
    print("Measure 3: GAMMA Internal Structure")
    print("-" * 40)
    gamma_structure = measure_gamma_internal_structure(a_entries, b_entries, gamma_tokens)
    all_results['gamma_structure'] = gamma_structure

    print(f"Mutual information: {gamma_structure['independence_test']['average_mutual_information']:.4f}")
    print(f"Morphology productive: {gamma_structure['morphological_analysis']['morphology_productive']}")
    print(f"Top prefix group: {list(gamma_structure['morphological_analysis']['prefix_groups'].keys())[:3]}")

    # Measure 4
    print("\n" + "-" * 40)
    print("Measure 4: GAMMA Distribution Across Entries")
    print("-" * 40)
    gamma_distribution = measure_gamma_distribution(a_entries, b_entries, gamma_tokens)
    all_results['gamma_distribution'] = gamma_distribution

    print(f"Specificity ratio: {gamma_distribution['entry_specificity']['specificity_ratio']:.3f}")
    print(f"Shared across sections: {gamma_distribution['section_distribution']['shared_gamma']}")
    print(f"Hub-associated GAMMA: {gamma_distribution['hub_correlation']['gamma_with_hub_preference']}")

    # Measure 5
    print("\n" + "-" * 40)
    print("Measure 5: Baseline System Comparison")
    print("-" * 40)
    baseline_comparison = measure_baseline_comparison(gamma_capacity, semantic_load, gamma_structure)
    all_results['baseline_comparison'] = baseline_comparison

    print(f"Best match: {baseline_comparison['best_match']['system']} "
          f"(score: {baseline_comparison['best_match']['score']:.2f})")
    for name, comp in sorted(baseline_comparison['comparisons'].items(),
                            key=lambda x: -x[1]['match_score']):
        print(f"  {name}: {comp['match_score']:.2f}")

    # Synthesis
    print("\n" + "-" * 40)
    print("Generating Phase 3 Synthesis...")
    print("-" * 40)
    synthesis = generate_phase3_synthesis(
        gamma_capacity, semantic_load, gamma_structure,
        gamma_distribution, baseline_comparison
    )
    all_results['synthesis'] = synthesis

    # Save results
    for name, data in all_results.items():
        output_path = Path(f'phase3_{name}.json')
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"[OK] Saved {output_path}")

    return all_results


if __name__ == '__main__':
    results = run_phase_3()

    if results:
        synthesis = results.get('synthesis', {})

        print("\n" + "=" * 60)
        print("PHASE 3 COMPLETE")
        print("=" * 60)

        print("\nKEY METRICS:")
        for metric, value in synthesis.get('key_metrics', {}).items():
            print(f"  {metric}: {value}")

        print("\nVERDICTS:")
        for verdict, value in synthesis.get('verdicts', {}).items():
            print(f"  {verdict}: {value}")

        print("\nIMPLICATIONS:")
        for impl in synthesis.get('implications', []):
            print(f"  * {impl}")

        print("\nNEXT STEPS:")
        for step in synthesis.get('next_steps', []):
            print(f"  > {step}")

        print("\nRESONANCE ASSESSMENT:")
        for aspect, rating in synthesis.get('resonance_assessment', {}).items():
            print(f"  {aspect}: {rating}")
