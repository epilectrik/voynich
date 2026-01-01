#!/usr/bin/env python3
"""
PHASE 4: CIPHER REVERSAL PROBE
==============================

Phase 3 found: 362 bits capacity, MI ~ 0.0006
This is cipher signature: meaning diffused, not absent.

Goal: Find transformations that INCREASE mutual information
without destroying known structural constraints.

Even a small MI increase is evidence of reversible encoding.
"""

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from itertools import combinations
from datetime import datetime
import random

# =============================================================================
# DATA LOADING
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

            if not word or word.startswith('*') or len(word) < 2:
                continue

            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                words.append({
                    'word': word,
                    'folio': folio,
                    'line': line_num,
                    'currier': currier
                })

    return words


def group_by_entries(words):
    """Group words into entries."""
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


def load_gamma_tokens():
    """Load GAMMA tokens from Phase 2A."""
    with open('phase2a_layer_assignments.json', 'r') as f:
        assignments = json.load(f)
    return set(assignments.get('layer_populations', {}).get('GAMMA', []))


def calculate_mi(token_sequence):
    """Calculate mutual information between adjacent tokens."""
    if len(token_sequence) < 2:
        return 0.0

    unigrams = Counter(token_sequence)
    bigrams = Counter(zip(token_sequence[:-1], token_sequence[1:]))

    total_unigrams = sum(unigrams.values())
    total_bigrams = sum(bigrams.values())

    if total_bigrams == 0:
        return 0.0

    mi_sum = 0.0
    for (t1, t2), joint_count in bigrams.items():
        p_joint = joint_count / total_bigrams
        p_t1 = unigrams[t1] / total_unigrams
        p_t2 = unigrams[t2] / total_unigrams

        if p_joint > 0 and p_t1 > 0 and p_t2 > 0:
            mi_sum += p_joint * math.log2(p_joint / (p_t1 * p_t2))

    return mi_sum


def calculate_entropy(token_sequence):
    """Calculate entropy of token distribution."""
    if not token_sequence:
        return 0.0

    freq = Counter(token_sequence)
    total = sum(freq.values())

    return -sum(
        (c / total) * math.log2(c / total)
        for c in freq.values() if c > 0
    )


# =============================================================================
# BASELINE MI MEASUREMENT
# =============================================================================

def measure_baseline_mi(a_entries, b_entries, gamma_tokens):
    """Establish baseline MI for GAMMA tokens."""
    results = {
        'measure': 'baseline_mi',
        'gamma_sequence': [],
        'metrics': {}
    }

    gamma_sequence = []
    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            tokens = tokenize_entry(words)
            gamma_in_entry = [t for t in tokens if t in gamma_tokens]
            gamma_sequence.extend(gamma_in_entry)

    results['gamma_sequence_length'] = len(gamma_sequence)
    results['unique_gamma'] = len(set(gamma_sequence))

    baseline_mi = calculate_mi(gamma_sequence)
    baseline_entropy = calculate_entropy(gamma_sequence)

    results['metrics'] = {
        'baseline_mi': baseline_mi,
        'baseline_entropy': baseline_entropy,
        'baseline_mi_normalized': baseline_mi / baseline_entropy if baseline_entropy > 0 else 0
    }

    results['gamma_sequence'] = gamma_sequence

    return results


# =============================================================================
# TRANSFORMATIONS
# =============================================================================

def transform_prefix_collapse(gamma_sequence, prefix_length=2):
    """Collapse tokens to their prefix."""
    results = {
        'transformation': f'prefix_collapse_{prefix_length}',
        'hypothesis': 'Cipher varies suffixes; roots carry meaning',
        'parameters': {'prefix_length': prefix_length}
    }

    transformed = [
        t[:prefix_length] if len(t) >= prefix_length else t
        for t in gamma_sequence
    ]

    new_mi = calculate_mi(transformed)
    new_entropy = calculate_entropy(transformed)

    results['metrics'] = {
        'transformed_mi': new_mi,
        'transformed_entropy': new_entropy,
        'unique_classes': len(set(transformed))
    }

    return results, transformed


def transform_suffix_collapse(gamma_sequence, suffix_length=2):
    """Collapse tokens to their suffix."""
    results = {
        'transformation': f'suffix_collapse_{suffix_length}',
        'hypothesis': 'Cipher varies prefixes; suffixes carry meaning',
        'parameters': {'suffix_length': suffix_length}
    }

    transformed = [
        t[-suffix_length:] if len(t) >= suffix_length else t
        for t in gamma_sequence
    ]

    new_mi = calculate_mi(transformed)
    new_entropy = calculate_entropy(transformed)

    results['metrics'] = {
        'transformed_mi': new_mi,
        'transformed_entropy': new_entropy,
        'unique_classes': len(set(transformed))
    }

    return results, transformed


def transform_family_collapse(gamma_sequence, gamma_tokens):
    """Collapse tokens into morphological families."""
    results = {
        'transformation': 'morphological_family_collapse',
        'hypothesis': 'Morphological families = cipher equivalence classes',
        'parameters': {}
    }

    prefix_families = defaultdict(list)
    for token in set(gamma_sequence):
        if len(token) >= 2:
            prefix_families[token[:2]].append(token)

    token_to_family = {}
    for prefix, members in prefix_families.items():
        if len(members) >= 2:
            family_name = f"FAM_{prefix}"
            for token in members:
                token_to_family[token] = family_name
        else:
            token_to_family[members[0]] = members[0]

    for token in set(gamma_sequence):
        if token not in token_to_family:
            token_to_family[token] = token

    transformed = [token_to_family.get(t, t) for t in gamma_sequence]

    new_mi = calculate_mi(transformed)
    new_entropy = calculate_entropy(transformed)

    results['metrics'] = {
        'transformed_mi': new_mi,
        'transformed_entropy': new_entropy,
        'unique_classes': len(set(transformed)),
        'families_created': len([f for f in set(transformed) if f.startswith('FAM_')])
    }

    results['family_mapping'] = {
        prefix: members for prefix, members in prefix_families.items()
        if len(members) >= 2
    }

    return results, transformed


def transform_length_collapse(gamma_sequence):
    """Collapse tokens by length."""
    results = {
        'transformation': 'length_collapse',
        'hypothesis': 'Length carries meaning; characters are noise',
        'parameters': {}
    }

    transformed = [f"LEN_{len(t)}" for t in gamma_sequence]

    new_mi = calculate_mi(transformed)
    new_entropy = calculate_entropy(transformed)

    results['metrics'] = {
        'transformed_mi': new_mi,
        'transformed_entropy': new_entropy,
        'unique_classes': len(set(transformed))
    }

    results['length_distribution'] = dict(Counter(len(t) for t in gamma_sequence))

    return results, transformed


def transform_final_char_collapse(gamma_sequence):
    """Collapse tokens by final character only."""
    results = {
        'transformation': 'final_char_collapse',
        'hypothesis': 'Final character = grammatical marker',
        'parameters': {}
    }

    transformed = [t[-1] if t else '' for t in gamma_sequence]

    new_mi = calculate_mi(transformed)
    new_entropy = calculate_entropy(transformed)

    results['metrics'] = {
        'transformed_mi': new_mi,
        'transformed_entropy': new_entropy,
        'unique_classes': len(set(transformed))
    }

    results['final_char_distribution'] = dict(Counter(transformed))

    return results, transformed


def transform_vc_pattern(gamma_sequence):
    """Collapse tokens to vowel/consonant skeleton."""
    results = {
        'transformation': 'vc_pattern_collapse',
        'hypothesis': 'Vowel/consonant pattern encodes; characters are variants',
        'parameters': {}
    }

    vowels = set('aeoyi')

    def to_vc(token):
        return ''.join('V' if c in vowels else 'C' for c in token)

    transformed = [to_vc(t) for t in gamma_sequence]

    new_mi = calculate_mi(transformed)
    new_entropy = calculate_entropy(transformed)

    results['metrics'] = {
        'transformed_mi': new_mi,
        'transformed_entropy': new_entropy,
        'unique_classes': len(set(transformed))
    }

    pattern_freq = Counter(transformed)
    results['top_patterns'] = dict(pattern_freq.most_common(20))

    return results, transformed


def transform_random_collapse(gamma_sequence, n_classes=20, seed=42):
    """CONTROL: Randomly assign tokens to equivalence classes."""
    results = {
        'transformation': 'random_collapse_control',
        'hypothesis': 'CONTROL: Random grouping should not increase MI',
        'parameters': {'n_classes': n_classes, 'seed': seed}
    }

    random.seed(seed)

    unique_tokens = list(set(gamma_sequence))
    random_mapping = {
        token: f"RAND_{random.randint(0, n_classes-1)}"
        for token in unique_tokens
    }

    transformed = [random_mapping[t] for t in gamma_sequence]

    new_mi = calculate_mi(transformed)
    new_entropy = calculate_entropy(transformed)

    results['metrics'] = {
        'transformed_mi': new_mi,
        'transformed_entropy': new_entropy,
        'unique_classes': len(set(transformed))
    }

    return results, transformed


def transform_frequency_band_collapse(gamma_sequence, n_bands=5):
    """Collapse tokens by frequency band."""
    results = {
        'transformation': 'frequency_band_collapse',
        'hypothesis': 'Frequency bands correspond to semantic classes',
        'parameters': {'n_bands': n_bands}
    }

    freq = Counter(gamma_sequence)
    sorted_tokens = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)
    band_size = max(1, len(sorted_tokens) // n_bands)

    token_to_band = {}
    for i, token in enumerate(sorted_tokens):
        band = min(i // band_size, n_bands - 1)
        token_to_band[token] = f"FREQ_{band}"

    transformed = [token_to_band[t] for t in gamma_sequence]

    new_mi = calculate_mi(transformed)
    new_entropy = calculate_entropy(transformed)

    results['metrics'] = {
        'transformed_mi': new_mi,
        'transformed_entropy': new_entropy,
        'unique_classes': len(set(transformed))
    }

    return results, transformed


def transform_positional_collapse(a_entries, b_entries, gamma_tokens):
    """Collapse tokens by their typical position in entry."""
    results = {
        'transformation': 'positional_collapse',
        'hypothesis': 'Position in entry encodes function',
        'parameters': {}
    }

    token_positions = defaultdict(list)

    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            tokens = tokenize_entry(words)
            if not tokens:
                continue

            for i, token in enumerate(tokens):
                if token in gamma_tokens:
                    relative_pos = i / len(tokens)
                    token_positions[token].append(relative_pos)

    token_to_band = {}
    for token, positions in token_positions.items():
        avg_pos = sum(positions) / len(positions)
        if avg_pos < 0.33:
            token_to_band[token] = "POS_EARLY"
        elif avg_pos < 0.66:
            token_to_band[token] = "POS_MIDDLE"
        else:
            token_to_band[token] = "POS_LATE"

    gamma_sequence = []
    for entries in [a_entries, b_entries]:
        for folio, words in entries.items():
            tokens = tokenize_entry(words)
            gamma_in_entry = [t for t in tokens if t in gamma_tokens]
            gamma_sequence.extend(gamma_in_entry)

    transformed = [token_to_band.get(t, "POS_UNK") for t in gamma_sequence]

    new_mi = calculate_mi(transformed)
    new_entropy = calculate_entropy(transformed)

    results['metrics'] = {
        'transformed_mi': new_mi,
        'transformed_entropy': new_entropy,
        'unique_classes': len(set(transformed))
    }

    return results, gamma_sequence


def transform_first_char_collapse(gamma_sequence):
    """Collapse tokens by first character only."""
    results = {
        'transformation': 'first_char_collapse',
        'hypothesis': 'First character = category marker',
        'parameters': {}
    }

    transformed = [t[0] if t else '' for t in gamma_sequence]

    new_mi = calculate_mi(transformed)
    new_entropy = calculate_entropy(transformed)

    results['metrics'] = {
        'transformed_mi': new_mi,
        'transformed_entropy': new_entropy,
        'unique_classes': len(set(transformed))
    }

    results['first_char_distribution'] = dict(Counter(transformed))

    return results, transformed


def transform_middle_collapse(gamma_sequence):
    """Collapse tokens to middle portion (remove first and last char)."""
    results = {
        'transformation': 'middle_collapse',
        'hypothesis': 'Middle carries core meaning; edges are markers',
        'parameters': {}
    }

    def get_middle(t):
        if len(t) <= 2:
            return t
        return t[1:-1]

    transformed = [get_middle(t) for t in gamma_sequence]

    new_mi = calculate_mi(transformed)
    new_entropy = calculate_entropy(transformed)

    results['metrics'] = {
        'transformed_mi': new_mi,
        'transformed_entropy': new_entropy,
        'unique_classes': len(set(transformed))
    }

    return results, transformed


# =============================================================================
# ANALYSIS
# =============================================================================

def check_constraint_preservation(original_sequence, transformed_sequence, transformation_name):
    """Verify transformation doesn't destroy structural constraints."""
    checks = {
        'transformation': transformation_name,
        'length_preserved': len(original_sequence) == len(transformed_sequence),
        'non_empty': len(transformed_sequence) > 0,
        'has_variety': len(set(transformed_sequence)) > 1
    }

    checks['all_preserved'] = all([
        checks['length_preserved'],
        checks['non_empty'],
        checks['has_variety']
    ])

    return checks


def analyze_mi_deltas(baseline_mi, transformation_results):
    """Analyze which transformations increased MI and by how much."""
    analysis = {
        'baseline_mi': baseline_mi,
        'transformations': [],
        'best_transformation': None,
        'significant_increases': [],
        'interpretation': ''
    }

    for name, result in transformation_results.items():
        if 'metrics' not in result:
            continue

        new_mi = result['metrics'].get('transformed_mi', 0)
        mi_delta = new_mi - baseline_mi
        mi_ratio = new_mi / baseline_mi if baseline_mi > 0 else float('inf')

        entry = {
            'name': name,
            'new_mi': new_mi,
            'mi_delta': mi_delta,
            'mi_ratio': mi_ratio,
            'unique_classes': result['metrics'].get('unique_classes', 0),
            'entropy': result['metrics'].get('transformed_entropy', 0)
        }

        analysis['transformations'].append(entry)

        if mi_ratio > 1.1:
            analysis['significant_increases'].append(entry)

    analysis['transformations'].sort(key=lambda x: x['mi_delta'], reverse=True)
    analysis['significant_increases'].sort(key=lambda x: x['mi_delta'], reverse=True)

    if analysis['transformations']:
        analysis['best_transformation'] = analysis['transformations'][0]

    analysis['interpretation'] = interpret_mi_deltas(analysis, baseline_mi)

    return analysis


def interpret_mi_deltas(analysis, baseline_mi):
    """Generate interpretation of MI delta results."""
    significant = analysis.get('significant_increases', [])
    best = analysis.get('best_transformation', {})

    if not significant:
        return (
            "NO transformation significantly increased MI. "
            "The cipher diffusion is robust - no obvious equivalence class structure."
        )

    random_result = None
    for t in analysis['transformations']:
        if 'random' in t['name'].lower():
            random_result = t
            break

    if random_result and significant:
        best_principled = significant[0]
        if random_result['mi_delta'] >= best_principled['mi_delta'] * 0.8:
            return (
                f"WARNING: Random collapse performed similarly to principled transforms. "
                f"MI increases may be artifacts of class reduction."
            )

    return (
        f"POTENTIAL SIGNAL: {len(significant)} transformation(s) increased MI. "
        f"Best: {best['name']} (MI: {baseline_mi:.6f} -> {best['new_mi']:.6f}, "
        f"ratio: {best['mi_ratio']:.2f}x)."
    )


def generate_phase4_synthesis(baseline_results, transformation_results, mi_analysis, constraint_checks):
    """Generate comprehensive Phase 4 synthesis."""
    synthesis = {
        'phase': 'Phase 4: Cipher Reversal Probe',
        'timestamp': datetime.now().isoformat(),
        'central_question': 'Can we find transformations that increase MI?',
        'baseline_mi': baseline_results['metrics']['baseline_mi'],
        'key_findings': [],
        'transformation_ranking': [],
        'implications': [],
        'next_steps': [],
        'resonance_assessment': {}
    }

    best = mi_analysis.get('best_transformation', {})
    significant = mi_analysis.get('significant_increases', [])

    synthesis['transformation_ranking'] = [
        {
            'rank': i + 1,
            'name': t['name'],
            'mi_delta': round(t['mi_delta'], 6),
            'mi_ratio': round(t['mi_ratio'], 2)
        }
        for i, t in enumerate(mi_analysis.get('transformations', [])[:10])
    ]

    if significant:
        synthesis['key_findings'].append(
            f"Found {len(significant)} transformation(s) that increase MI"
        )
        synthesis['key_findings'].append(
            f"Best: {best['name']} with {best['mi_ratio']:.2f}x improvement"
        )
        synthesis['resonance_assessment']['mi_increase'] = 'GREEN'
    else:
        synthesis['key_findings'].append(
            "No transformation significantly increased MI"
        )
        synthesis['resonance_assessment']['mi_increase'] = 'RED'

    # Check random control
    for t in mi_analysis.get('transformations', []):
        if 'random' in t['name'].lower() and significant:
            best_sig = significant[0]
            if t['mi_delta'] >= best_sig['mi_delta'] * 0.8:
                synthesis['key_findings'].append(
                    "WARNING: Random control performed similarly - increases may be artifacts"
                )
                synthesis['resonance_assessment']['control_comparison'] = 'RED'
            else:
                synthesis['key_findings'].append(
                    "Principled transforms outperformed random control"
                )
                synthesis['resonance_assessment']['control_comparison'] = 'GREEN'
            break

    if significant and synthesis['resonance_assessment'].get('control_comparison') == 'GREEN':
        synthesis['implications'].append(
            f"The {best['name']} transformation reveals hidden structure"
        )
        synthesis['implications'].append(
            "Equivalence classes exist in the encoding"
        )
        synthesis['next_steps'].append(
            f"Investigate {best['name']} further"
        )
    else:
        synthesis['implications'].append(
            "Cipher diffusion is robust against tested transformations"
        )
        synthesis['next_steps'].append(
            "Consider that semantic recovery may require external key"
        )

    green_count = sum(1 for v in synthesis['resonance_assessment'].values() if v == 'GREEN')
    if green_count >= 2:
        synthesis['resonance_assessment']['overall'] = 'GREEN - Potential breakthrough'
    elif green_count >= 1:
        synthesis['resonance_assessment']['overall'] = 'YELLOW - Partial signal'
    else:
        synthesis['resonance_assessment']['overall'] = 'RED - Cipher remains opaque'

    synthesis['interpretation'] = mi_analysis.get('interpretation', '')

    return synthesis


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_phase_4():
    """Execute Phase 4: Cipher Reversal Probe."""
    print("=" * 60)
    print("PHASE 4: CIPHER REVERSAL PROBE")
    print("=" * 60)
    print("\nGoal: Find transformations that increase mutual information")
    print("A positive result suggests reversible encoding structure\n")

    print("Loading corpus and GAMMA tokens...")
    words = load_corpus()
    entries = group_by_entries(words)
    a_entries, b_entries = split_by_currier(entries)
    gamma_tokens = load_gamma_tokens()
    print(f"Loaded {len(gamma_tokens)} GAMMA tokens")

    print("\n" + "-" * 40)
    print("Establishing baseline MI...")
    print("-" * 40)
    baseline = measure_baseline_mi(a_entries, b_entries, gamma_tokens)
    baseline_mi = baseline['metrics']['baseline_mi']
    gamma_sequence = baseline['gamma_sequence']

    print(f"Baseline MI: {baseline_mi:.6f}")
    print(f"Baseline entropy: {baseline['metrics']['baseline_entropy']:.2f}")
    print(f"Sequence length: {baseline['gamma_sequence_length']}")

    print("\n" + "-" * 40)
    print("Running transformations...")
    print("-" * 40)

    transformation_results = {}
    constraint_checks = {}

    transforms = [
        ('prefix_collapse_2', lambda s: transform_prefix_collapse(s, 2)),
        ('prefix_collapse_3', lambda s: transform_prefix_collapse(s, 3)),
        ('suffix_collapse_2', lambda s: transform_suffix_collapse(s, 2)),
        ('suffix_collapse_3', lambda s: transform_suffix_collapse(s, 3)),
        ('morphological_family', lambda s: transform_family_collapse(s, gamma_tokens)),
        ('length_collapse', lambda s: transform_length_collapse(s)),
        ('final_char', lambda s: transform_final_char_collapse(s)),
        ('first_char', lambda s: transform_first_char_collapse(s)),
        ('middle_collapse', lambda s: transform_middle_collapse(s)),
        ('vc_pattern', lambda s: transform_vc_pattern(s)),
        ('random_control', lambda s: transform_random_collapse(s)),
        ('frequency_band', lambda s: transform_frequency_band_collapse(s)),
    ]

    for name, transform_fn in transforms:
        print(f"  Testing {name}...")
        result, transformed = transform_fn(gamma_sequence)
        transformation_results[name] = result
        constraint_checks[name] = check_constraint_preservation(gamma_sequence, transformed, name)
        delta = result['metrics']['transformed_mi'] - baseline_mi
        print(f"    MI: {result['metrics']['transformed_mi']:.6f} (delta={delta:+.6f})")

    # Positional (needs entries)
    print(f"  Testing positional...")
    result, seq = transform_positional_collapse(a_entries, b_entries, gamma_tokens)
    transformation_results['positional'] = result
    constraint_checks['positional'] = {'all_preserved': True}
    delta = result['metrics']['transformed_mi'] - baseline_mi
    print(f"    MI: {result['metrics']['transformed_mi']:.6f} (delta={delta:+.6f})")

    print("\n" + "-" * 40)
    print("Analyzing MI changes...")
    print("-" * 40)
    mi_analysis = analyze_mi_deltas(baseline_mi, transformation_results)

    print("\n" + "-" * 40)
    print("Generating synthesis...")
    print("-" * 40)
    synthesis = generate_phase4_synthesis(
        baseline, transformation_results, mi_analysis, constraint_checks
    )

    # Save results
    all_results = {
        'baseline': {
            'metrics': baseline['metrics'],
            'gamma_sequence_length': baseline['gamma_sequence_length'],
            'unique_gamma': baseline['unique_gamma']
        },
        'transformations': transformation_results,
        'mi_analysis': mi_analysis,
        'constraint_checks': constraint_checks,
        'synthesis': synthesis
    }

    output_path = Path('phase4_cipher_reversal.json')
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"[OK] Saved {output_path}")

    return all_results


if __name__ == '__main__':
    results = run_phase_4()

    synthesis = results.get('synthesis', {})

    print("\n" + "=" * 60)
    print("PHASE 4 COMPLETE")
    print("=" * 60)

    print(f"\nBASELINE MI: {synthesis.get('baseline_mi', 0):.6f}")

    print("\nTRANSFORMATION RANKING:")
    for t in synthesis.get('transformation_ranking', [])[:8]:
        delta_str = f"+{t['mi_delta']:.6f}" if t['mi_delta'] > 0 else f"{t['mi_delta']:.6f}"
        print(f"  {t['rank']}. {t['name']}: delta={delta_str} ({t['mi_ratio']:.2f}x)")

    print("\nKEY FINDINGS:")
    for finding in synthesis.get('key_findings', []):
        print(f"  * {finding}")

    print("\nIMPLICATIONS:")
    for impl in synthesis.get('implications', []):
        print(f"  > {impl}")

    print("\nNEXT STEPS:")
    for step in synthesis.get('next_steps', []):
        print(f"  > {step}")

    print("\nRESONANCE ASSESSMENT:")
    for aspect, rating in synthesis.get('resonance_assessment', {}).items():
        print(f"  {aspect}: {rating}")

    print(f"\nINTERPRETATION: {synthesis.get('interpretation', '')}")
