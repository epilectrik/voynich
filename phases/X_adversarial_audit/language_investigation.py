#!/usr/bin/env python3
"""
Language Encoding Investigation
Phase X.5: Test remaining avenues for language encoding

Tests:
1. Phonetic clustering (mnemonic hypothesis)
2. AMBIGUOUS token analysis
3. Modifier position analysis
4. Zonal ZIPF analysis
5. Dual-use token detection
"""

import json
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import re

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, cls=NumpyEncoder)

def compute_zipf_exponent(frequencies):
    """Compute ZIPF exponent from frequency list."""
    if len(frequencies) < 2:
        return 0.0

    freqs = sorted(frequencies, reverse=True)
    ranks = np.arange(1, len(freqs) + 1)

    # Filter out zeros
    mask = np.array(freqs) > 0
    if mask.sum() < 2:
        return 0.0

    log_ranks = np.log(ranks[mask])
    log_freqs = np.log(np.array(freqs)[mask])

    # Linear regression
    slope, _ = np.polyfit(log_ranks, log_freqs, 1)
    return slope

# ============================================================================
# TEST 1: PHONETIC CLUSTERING
# ============================================================================

def analyze_phonetic_clustering():
    """Test if tokens cluster phonetically by function."""
    print("=" * 70)
    print("TEST 1: PHONETIC CLUSTERING ANALYSIS")
    print("=" * 70)

    # Load token-to-class mapping
    with open("phase20a_operator_equivalence.json") as f:
        equiv_data = json.load(f)

    # EVA phonetic features (assuming phonetic values)
    # Initial consonants, vowels, final consonants
    INITIALS = {
        'q': 'velar_stop', 'k': 'velar_stop', 'g': 'velar_stop',
        't': 'dental_stop', 'd': 'dental_stop',
        'p': 'labial_stop', 'b': 'labial_stop', 'f': 'labial_fric',
        's': 'sibilant', 'sh': 'sibilant', 'ch': 'affricate',
        'l': 'liquid', 'r': 'liquid',
        'o': 'vowel', 'a': 'vowel', 'e': 'vowel', 'i': 'vowel',
        'y': 'semivowel', 'h': 'glottal'
    }

    def get_phonetic_features(token):
        """Extract phonetic features from token."""
        if not token:
            return {'initial': 'unknown', 'final': 'unknown', 'length': 0}

        # Initial
        initial = 'unknown'
        for prefix in ['sh', 'ch', 'qo', 'ot', 'ok']:
            if token.startswith(prefix):
                initial = INITIALS.get(prefix[:2], prefix[:2])
                break
        else:
            initial = INITIALS.get(token[0], token[0])

        # Final
        final = token[-1] if token else 'unknown'
        if token.endswith('dy') or token.endswith('y'):
            final = 'y_ending'
        elif token.endswith('in') or token.endswith('n'):
            final = 'n_ending'
        elif token.endswith('r'):
            final = 'r_ending'
        elif token.endswith('l'):
            final = 'l_ending'

        return {
            'initial': initial,
            'final': final,
            'length': len(token),
            'has_aiin': 'aiin' in token or 'ain' in token,
            'has_dy': 'dy' in token,
            'starts_q': token.startswith('q'),
            'starts_o': token.startswith('o'),
            'starts_ch': token.startswith('ch'),
            'starts_sh': token.startswith('sh')
        }

    # Analyze by class
    class_phonetics = defaultdict(list)
    for cls in equiv_data['classes']:
        class_id = cls['class_id']
        role = cls.get('role', 'UNKNOWN')
        for member in cls['members']:
            features = get_phonetic_features(member)
            features['token'] = member
            features['role'] = role
            class_phonetics[class_id].append(features)

    # Aggregate by role
    role_initials = defaultdict(Counter)
    role_finals = defaultdict(Counter)
    role_q_starts = defaultdict(int)
    role_totals = defaultdict(int)

    for class_id, tokens in class_phonetics.items():
        for t in tokens:
            role = t['role']
            role_initials[role][t['initial']] += 1
            role_finals[role][t['final']] += 1
            if t.get('starts_q', False):
                role_q_starts[role] += 1
            role_totals[role] += 1

    # Compute correlations
    results = {
        'metadata': {
            'test': 'PHONETIC_CLUSTERING',
            'timestamp': datetime.now().isoformat()
        },
        'role_phonetic_profiles': {},
        'correlations': {}
    }

    for role in role_totals:
        total = role_totals[role]
        if total == 0:
            continue

        profile = {
            'total_tokens': total,
            'initial_distribution': dict(role_initials[role].most_common(5)),
            'final_distribution': dict(role_finals[role].most_common(5)),
            'q_start_ratio': role_q_starts[role] / total if total > 0 else 0
        }
        results['role_phonetic_profiles'][role] = profile

    # Test: Do different roles have different phonetic signatures?
    # Compute chi-squared-like divergence
    roles = list(role_totals.keys())
    if len(roles) >= 2:
        # Compare q-start ratio across roles
        q_ratios = [results['role_phonetic_profiles'].get(r, {}).get('q_start_ratio', 0) for r in roles]
        q_variance = np.var(q_ratios) if len(q_ratios) > 0 else 0

        results['correlations'] = {
            'q_start_variance_across_roles': float(q_variance),
            'roles_analyzed': len(roles),
            'signal': 'WEAK' if q_variance < 0.01 else 'MODERATE' if q_variance < 0.05 else 'STRONG'
        }

    # Specific test: Does 'q' prefix correlate with ENERGY roles?
    energy_q_ratio = results['role_phonetic_profiles'].get('ENERGY_OPERATOR', {}).get('q_start_ratio', 0)
    other_q_ratios = [
        results['role_phonetic_profiles'].get(r, {}).get('q_start_ratio', 0)
        for r in roles if r != 'ENERGY_OPERATOR'
    ]
    mean_other_q = np.mean(other_q_ratios) if other_q_ratios else 0

    results['q_energy_correlation'] = {
        'energy_operator_q_ratio': energy_q_ratio,
        'other_roles_mean_q_ratio': float(mean_other_q),
        'difference': energy_q_ratio - float(mean_other_q),
        'signal': 'STRONG' if (energy_q_ratio - float(mean_other_q)) > 0.1 else 'WEAK'
    }

    # Verdict
    signals = [
        results['correlations'].get('signal', 'NONE'),
        results['q_energy_correlation'].get('signal', 'NONE')
    ]

    if 'STRONG' in signals:
        verdict = 'PHONETIC_CLUSTERING_DETECTED'
    elif 'MODERATE' in signals:
        verdict = 'WEAK_PHONETIC_SIGNAL'
    else:
        verdict = 'NO_PHONETIC_CLUSTERING'

    results['VERDICT'] = verdict

    print(f"\nQ-start ratio for ENERGY_OPERATOR: {energy_q_ratio:.3f}")
    print(f"Mean Q-start ratio for other roles: {mean_other_q:.3f}")
    print(f"VERDICT: {verdict}")

    save_json(results, 'language_test1_phonetic_clustering.json')
    return results

# ============================================================================
# TEST 2: AMBIGUOUS TOKEN ANALYSIS
# ============================================================================

def analyze_ambiguous_tokens():
    """Analyze the 460 AMBIGUOUS tokens for linguistic patterns."""
    print("\n" + "=" * 70)
    print("TEST 2: AMBIGUOUS TOKEN ANALYSIS")
    print("=" * 70)

    with open("phase19a_executability_matrix.json") as f:
        exec_data = json.load(f)

    with open("phase7a_middle_roles.json") as f:
        middle_data = json.load(f)

    with open("phase15d_vocabulary_structure.json") as f:
        vocab_data = json.load(f)

    # Extract AMBIGUOUS tokens
    ambiguous = exec_data.get('ambiguous_candidates', [])
    executable = exec_data.get('sample_executable', [])

    print(f"\nAMBIGUOUS tokens: {len(ambiguous)}")
    print(f"EXECUTABLE tokens: {len(executable)}")

    results = {
        'metadata': {
            'test': 'AMBIGUOUS_TOKEN_ANALYSIS',
            'timestamp': datetime.now().isoformat()
        },
        'counts': {
            'ambiguous': len(ambiguous),
            'executable': len(executable),
            'non_executable': 0
        }
    }

    # Analyze morphological complexity
    def morphological_complexity(token):
        """Compute morphological features."""
        return {
            'length': len(token),
            'has_prefix_ch': token.startswith('ch'),
            'has_prefix_sh': token.startswith('sh'),
            'has_prefix_qo': token.startswith('qo'),
            'has_prefix_ot': token.startswith('ot'),
            'has_suffix_dy': token.endswith('dy'),
            'has_suffix_y': token.endswith('y') and not token.endswith('dy'),
            'has_suffix_in': token.endswith('in') or token.endswith('ain'),
            'has_suffix_ar': token.endswith('ar'),
            'has_suffix_or': token.endswith('or'),
            'has_suffix_al': token.endswith('al'),
            'has_daiin': 'daiin' in token or 'dain' in token or 'aiin' in token
        }

    # Compare AMBIGUOUS vs EXECUTABLE morphology
    amb_features = [morphological_complexity(t['token']) for t in ambiguous]
    exe_features = [morphological_complexity(t['token']) for t in executable]

    def aggregate_features(features):
        if not features:
            return {}
        agg = {}
        for key in features[0]:
            if key == 'length':
                agg['mean_length'] = np.mean([f[key] for f in features])
            else:
                agg[key + '_ratio'] = np.mean([f[key] for f in features])
        return agg

    amb_agg = aggregate_features(amb_features)
    exe_agg = aggregate_features(exe_features)

    results['morphological_comparison'] = {
        'ambiguous': amb_agg,
        'executable': exe_agg
    }

    # Key differences
    differences = {}
    for key in amb_agg:
        if key in exe_agg:
            diff = amb_agg[key] - exe_agg[key]
            differences[key] = {
                'ambiguous': amb_agg[key],
                'executable': exe_agg[key],
                'difference': diff,
                'significant': abs(diff) > 0.1
            }

    results['key_differences'] = differences

    # Check if AMBIGUOUS tokens are concentrated in specific roles
    middle_to_role = {}
    for cluster_id, cluster_info in middle_data.get('cluster_profiles', {}).items():
        for member in cluster_info.get('sample_members', []):
            middle_to_role[member] = cluster_info.get('role_type', 'UNKNOWN')

    amb_roles = Counter()
    for t in ambiguous:
        token = t['token']
        role = middle_to_role.get(token, 'NOT_A_MIDDLE')
        amb_roles[role] += 1

    exe_roles = Counter()
    for t in executable:
        token = t['token']
        role = middle_to_role.get(token, 'NOT_A_MIDDLE')
        exe_roles[role] += 1

    results['role_distribution'] = {
        'ambiguous': dict(amb_roles),
        'executable': dict(exe_roles)
    }

    # Check A/B text distribution
    population_bias = vocab_data.get('population_bias', {})
    a_biased_tokens = set(t['node'] for t in population_bias.get('a_biased', []))
    b_biased_tokens = set(t['node'] for t in population_bias.get('b_biased', []))

    amb_a_count = sum(1 for t in ambiguous if t['token'] in a_biased_tokens)
    amb_b_count = sum(1 for t in ambiguous if t['token'] in b_biased_tokens)

    results['ab_distribution'] = {
        'ambiguous_a_biased': amb_a_count,
        'ambiguous_b_biased': amb_b_count,
        'ambiguous_neutral': len(ambiguous) - amb_a_count - amb_b_count
    }

    # Check frequency distribution
    amb_freqs = [t['frequency'] for t in ambiguous]
    exe_freqs = [t['frequency'] for t in executable]

    results['frequency_comparison'] = {
        'ambiguous_mean_freq': float(np.mean(amb_freqs)) if amb_freqs else 0,
        'ambiguous_median_freq': float(np.median(amb_freqs)) if amb_freqs else 0,
        'executable_mean_freq': float(np.mean(exe_freqs)) if exe_freqs else 0,
        'executable_median_freq': float(np.median(exe_freqs)) if exe_freqs else 0
    }

    # Verdict
    # AMBIGUOUS tokens would be linguistic if they:
    # 1. Have different morphology than EXECUTABLE
    # 2. Concentrate in specific roles
    # 3. Show A/B bias

    significant_diffs = sum(1 for d in differences.values() if d.get('significant', False))
    role_concentration = len(amb_roles) < len(exe_roles) if exe_roles else False
    ab_bias = (amb_a_count > len(ambiguous) * 0.3) or (amb_b_count > len(ambiguous) * 0.3)

    if significant_diffs >= 3 and (role_concentration or ab_bias):
        verdict = 'LINGUISTIC_LAYER_DETECTED'
    elif significant_diffs >= 2 or role_concentration or ab_bias:
        verdict = 'WEAK_LINGUISTIC_SIGNAL'
    else:
        verdict = 'NO_LINGUISTIC_SIGNAL'

    results['VERDICT'] = verdict
    results['verdict_reasoning'] = {
        'significant_morphological_differences': significant_diffs,
        'role_concentration': role_concentration,
        'ab_bias_detected': ab_bias
    }

    print(f"\nSignificant morphological differences: {significant_diffs}")
    print(f"Role concentration: {role_concentration}")
    print(f"A/B bias: {ab_bias}")
    print(f"VERDICT: {verdict}")

    save_json(results, 'language_test2_ambiguous_tokens.json')
    return results

# ============================================================================
# TEST 3: MODIFIER POSITION ANALYSIS
# ============================================================================

def analyze_modifier_positions():
    """Test if modifier positions (6-7) behave differently."""
    print("\n" + "=" * 70)
    print("TEST 3: MODIFIER POSITION ANALYSIS")
    print("=" * 70)

    with open("phase7c_slot_grammar.json") as f:
        grammar_data = json.load(f)

    with open("phase19a_executability_matrix.json") as f:
        exec_data = json.load(f)

    results = {
        'metadata': {
            'test': 'MODIFIER_POSITION_ANALYSIS',
            'timestamp': datetime.now().isoformat()
        }
    }

    # Extract slot information from grammar
    rules = grammar_data.get('rules', [])
    slot_stats = grammar_data.get('slot_statistics', {})

    results['slot_statistics'] = slot_stats

    # Analyze by position category
    # Positions 0: TOPIC
    # Positions 1-2: PRIMARY
    # Positions 3-5: SECONDARY
    # Positions 6-7: MODIFIER
    # Positions 8-9: TERMINAL

    position_categories = {
        'TOPIC': [0],
        'PRIMARY': [1, 2],
        'SECONDARY': [3, 4, 5],
        'MODIFIER': [6, 7],
        'TERMINAL': [8, 9]
    }

    # Check if we have per-position token lists
    position_tokens = grammar_data.get('position_tokens', {})

    if not position_tokens:
        # Reconstruct from rules if possible
        print("Note: position_tokens not found, using rule analysis")
        results['position_analysis'] = 'LIMITED - need raw positional data'
        results['VERDICT'] = 'INSUFFICIENT_DATA'
        save_json(results, 'language_test3_modifier_positions.json')
        return results

    # Analyze each category
    category_profiles = {}
    for cat, positions in position_categories.items():
        tokens_in_cat = set()
        for pos in positions:
            tokens_in_cat.update(position_tokens.get(str(pos), []))

        category_profiles[cat] = {
            'unique_tokens': len(tokens_in_cat),
            'sample': list(tokens_in_cat)[:10]
        }

    results['category_profiles'] = category_profiles

    # Compare MODIFIER to PRIMARY
    modifier_unique = category_profiles.get('MODIFIER', {}).get('unique_tokens', 0)
    primary_unique = category_profiles.get('PRIMARY', {}).get('unique_tokens', 0)

    results['modifier_vs_primary'] = {
        'modifier_vocabulary': modifier_unique,
        'primary_vocabulary': primary_unique,
        'ratio': modifier_unique / primary_unique if primary_unique > 0 else 0
    }

    # Verdict
    if modifier_unique > primary_unique * 1.5:
        verdict = 'MODIFIER_SHOWS_LINGUISTIC_PROPERTIES'
    elif modifier_unique > primary_unique:
        verdict = 'WEAK_MODIFIER_SIGNAL'
    else:
        verdict = 'NO_MODIFIER_DIFFERENTIATION'

    results['VERDICT'] = verdict

    print(f"\nMODIFIER vocabulary: {modifier_unique}")
    print(f"PRIMARY vocabulary: {primary_unique}")
    print(f"VERDICT: {verdict}")

    save_json(results, 'language_test3_modifier_positions.json')
    return results

# ============================================================================
# TEST 4: ZONAL ZIPF ANALYSIS
# ============================================================================

def analyze_zonal_zipf():
    """Test if ZIPF distribution varies by zone."""
    print("\n" + "=" * 70)
    print("TEST 4: ZONAL ZIPF ANALYSIS")
    print("=" * 70)

    with open("phase15d_vocabulary_structure.json") as f:
        vocab_data = json.load(f)

    with open("phase19a_executability_matrix.json") as f:
        exec_data = json.load(f)

    # Load raw corpus for section analysis
    corpus_path = Path("data/transcriptions/interlinear_full_words.txt")

    results = {
        'metadata': {
            'test': 'ZONAL_ZIPF_ANALYSIS',
            'timestamp': datetime.now().isoformat()
        },
        'baseline': {
            'full_corpus_zipf': vocab_data['frequency_distribution']['zipf_exponent'],
            'reference': {
                'natural_language': '-1.0 to -1.2',
                'control_systems': 'typically flatter (closer to 0)',
                'random': '~0'
            }
        }
    }

    # Parse corpus by section (Currier A vs B)
    a_tokens = Counter()
    b_tokens = Counter()

    if corpus_path.exists():
        with open(corpus_path) as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    section = parts[0]
                    word = parts[2] if len(parts) > 2 else ''
                    if word and word != '???':
                        # Determine A vs B (simplified: assume section format)
                        if 'A' in section.upper() or section.startswith('f') and int(re.search(r'\d+', section).group() if re.search(r'\d+', section) else 0) < 50:
                            a_tokens[word] += 1
                        else:
                            b_tokens[word] += 1

    # Compute ZIPF by section
    if a_tokens:
        a_zipf = compute_zipf_exponent(list(a_tokens.values()))
        results['currier_a'] = {
            'unique_tokens': len(a_tokens),
            'total_tokens': sum(a_tokens.values()),
            'zipf_exponent': float(a_zipf)
        }

    if b_tokens:
        b_zipf = compute_zipf_exponent(list(b_tokens.values()))
        results['currier_b'] = {
            'unique_tokens': len(b_tokens),
            'total_tokens': sum(b_tokens.values()),
            'zipf_exponent': float(b_zipf)
        }

    # Compute ZIPF for AMBIGUOUS vs EXECUTABLE
    ambiguous = exec_data.get('ambiguous_candidates', [])
    executable = exec_data.get('sample_executable', [])

    amb_freqs = [t['frequency'] for t in ambiguous]
    exe_freqs = [t['frequency'] for t in executable]

    if amb_freqs:
        amb_zipf = compute_zipf_exponent(amb_freqs)
        results['ambiguous_tokens'] = {
            'count': len(amb_freqs),
            'zipf_exponent': float(amb_zipf)
        }

    if exe_freqs:
        exe_zipf = compute_zipf_exponent(exe_freqs)
        results['executable_tokens'] = {
            'count': len(exe_freqs),
            'zipf_exponent': float(exe_zipf)
        }

    # Compute ZIPF for kernel vs non-kernel
    kernel_tokens = {'k', 'h', 'e', 'ch', 'sh', 'ol', 't', 'd'}

    kernel_freqs = []
    non_kernel_freqs = []

    for item in vocab_data['frequency_distribution']['most_frequent']:
        if item['node'] in kernel_tokens:
            kernel_freqs.append(item['freq'])
        else:
            non_kernel_freqs.append(item['freq'])

    if kernel_freqs:
        kernel_zipf = compute_zipf_exponent(kernel_freqs)
        results['kernel_tokens'] = {
            'count': len(kernel_freqs),
            'zipf_exponent': float(kernel_zipf)
        }

    if non_kernel_freqs:
        non_kernel_zipf = compute_zipf_exponent(non_kernel_freqs)
        results['non_kernel_tokens'] = {
            'count': len(non_kernel_freqs),
            'zipf_exponent': float(non_kernel_zipf)
        }

    # Analyze variance
    exponents = []
    if 'currier_a' in results:
        exponents.append(('currier_a', results['currier_a']['zipf_exponent']))
    if 'currier_b' in results:
        exponents.append(('currier_b', results['currier_b']['zipf_exponent']))
    if 'ambiguous_tokens' in results:
        exponents.append(('ambiguous', results['ambiguous_tokens']['zipf_exponent']))
    if 'executable_tokens' in results:
        exponents.append(('executable', results['executable_tokens']['zipf_exponent']))

    if len(exponents) >= 2:
        exp_values = [e[1] for e in exponents]
        variance = float(np.var(exp_values))
        range_val = max(exp_values) - min(exp_values)

        results['zonal_variance'] = {
            'exponents': dict(exponents),
            'variance': variance,
            'range': range_val
        }

        # Verdict
        if range_val > 0.3:
            verdict = 'STRONG_ZONAL_DIFFERENTIATION'
        elif range_val > 0.15:
            verdict = 'MODERATE_ZONAL_DIFFERENTIATION'
        elif range_val > 0.05:
            verdict = 'WEAK_ZONAL_DIFFERENTIATION'
        else:
            verdict = 'UNIFORM_ZIPF_DISTRIBUTION'
    else:
        verdict = 'INSUFFICIENT_DATA'

    results['VERDICT'] = verdict

    print(f"\nZIPF Exponents by Zone:")
    for name, exp in exponents:
        print(f"  {name}: {exp:.3f}")
    if 'zonal_variance' in results:
        print(f"\nRange: {results['zonal_variance']['range']:.3f}")
    print(f"VERDICT: {verdict}")

    save_json(results, 'language_test4_zonal_zipf.json')
    return results

# ============================================================================
# TEST 5: DUAL-USE TOKEN DETECTION
# ============================================================================

def analyze_dual_use_tokens():
    """Find tokens that might encode both procedure and language."""
    print("\n" + "=" * 70)
    print("TEST 5: DUAL-USE TOKEN DETECTION")
    print("=" * 70)

    with open("phase19b_substitution_invariance.json") as f:
        subst_data = json.load(f)

    with open("phase19a_executability_matrix.json") as f:
        exec_data = json.load(f)

    results = {
        'metadata': {
            'test': 'DUAL_USE_TOKEN_DETECTION',
            'timestamp': datetime.now().isoformat()
        }
    }

    # Check substitution patterns
    invariant_pairs = subst_data.get('invariant_pairs', [])
    near_invariant = subst_data.get('near_invariant_pairs', [])

    results['substitution_analysis'] = {
        'fully_invariant_pairs': len(invariant_pairs),
        'near_invariant_pairs': len(near_invariant) if near_invariant else 0,
        'invariant_examples': invariant_pairs[:10] if invariant_pairs else [],
        'near_invariant_examples': near_invariant[:10] if near_invariant else []
    }

    # Find tokens that are AMBIGUOUS but have phonetic similarity
    ambiguous = exec_data.get('ambiguous_candidates', [])

    # Group by phonetic features
    phonetic_groups = defaultdict(list)
    for t in ambiguous:
        token = t['token']
        # Simple phonetic grouping by initial
        if token.startswith('ch'):
            group = 'ch_initial'
        elif token.startswith('sh'):
            group = 'sh_initial'
        elif token.startswith('qo'):
            group = 'qo_initial'
        elif token.startswith('ot'):
            group = 'ot_initial'
        elif token.startswith('ok'):
            group = 'ok_initial'
        elif len(token) > 0:
            group = f"{token[0]}_initial"
        else:
            group = 'empty'

        phonetic_groups[group].append({
            'token': token,
            'convergence_delta': t['convergence_delta']
        })

    # Find groups where tokens have similar convergence delta (potential synonyms)
    potential_synonyms = []
    for group, tokens in phonetic_groups.items():
        if len(tokens) >= 2:
            deltas = [t['convergence_delta'] for t in tokens]
            delta_range = max(deltas) - min(deltas)

            if delta_range < 0.02:  # Very similar impact
                potential_synonyms.append({
                    'group': group,
                    'tokens': [t['token'] for t in tokens],
                    'delta_range': delta_range,
                    'mean_delta': float(np.mean(deltas))
                })

    results['phonetic_groups'] = {
        'total_groups': len(phonetic_groups),
        'group_sizes': {k: len(v) for k, v in phonetic_groups.items()}
    }

    results['potential_synonyms'] = {
        'count': len(potential_synonyms),
        'examples': potential_synonyms[:10]
    }

    # Verdict
    if len(invariant_pairs) > 0:
        verdict = 'DUAL_USE_DETECTED'
    elif len(potential_synonyms) >= 5:
        verdict = 'POTENTIAL_DUAL_USE'
    elif len(near_invariant) > 0:
        verdict = 'WEAK_DUAL_USE_SIGNAL'
    else:
        verdict = 'NO_DUAL_USE_DETECTED'

    results['VERDICT'] = verdict

    print(f"\nInvariant pairs: {len(invariant_pairs)}")
    print(f"Potential synonym groups: {len(potential_synonyms)}")
    print(f"VERDICT: {verdict}")

    save_json(results, 'language_test5_dual_use.json')
    return results

# ============================================================================
# SYNTHESIS
# ============================================================================

def generate_synthesis(test_results):
    """Generate overall synthesis from all tests."""
    print("\n" + "=" * 70)
    print("SYNTHESIS: LANGUAGE ENCODING INVESTIGATION")
    print("=" * 70)

    synthesis = {
        'metadata': {
            'investigation': 'LANGUAGE_ENCODING',
            'timestamp': datetime.now().isoformat(),
            'phase': 'X.5'
        },
        'test_results': {}
    }

    verdicts = []
    for name, result in test_results.items():
        verdict = result.get('VERDICT', 'UNKNOWN')
        synthesis['test_results'][name] = {
            'verdict': verdict,
            'key_findings': {}
        }
        verdicts.append(verdict)

        # Extract key findings
        if name == 'phonetic_clustering':
            if 'q_energy_correlation' in result:
                synthesis['test_results'][name]['key_findings'] = {
                    'q_energy_difference': result['q_energy_correlation'].get('difference', 0)
                }
        elif name == 'ambiguous_tokens':
            if 'verdict_reasoning' in result:
                synthesis['test_results'][name]['key_findings'] = result['verdict_reasoning']
        elif name == 'zonal_zipf':
            if 'zonal_variance' in result:
                synthesis['test_results'][name]['key_findings'] = {
                    'zipf_range': result['zonal_variance'].get('range', 0),
                    'exponents': result['zonal_variance'].get('exponents', {})
                }

    # Count positive signals
    positive_signals = sum(1 for v in verdicts if 'DETECTED' in v or 'STRONG' in v)
    weak_signals = sum(1 for v in verdicts if 'WEAK' in v or 'POTENTIAL' in v or 'MODERATE' in v)
    negative_signals = sum(1 for v in verdicts if 'NO_' in v or 'UNIFORM' in v)

    synthesis['signal_summary'] = {
        'positive_signals': positive_signals,
        'weak_signals': weak_signals,
        'negative_signals': negative_signals,
        'total_tests': len(verdicts)
    }

    # Overall verdict
    if positive_signals >= 2:
        overall = 'LANGUAGE_ENCODING_SUPPORTED'
        confidence = 'HIGH'
    elif positive_signals >= 1 or weak_signals >= 3:
        overall = 'LANGUAGE_ENCODING_POSSIBLE'
        confidence = 'MODERATE'
    elif weak_signals >= 2:
        overall = 'WEAK_LINGUISTIC_SIGNAL'
        confidence = 'LOW'
    else:
        overall = 'LANGUAGE_ENCODING_NOT_SUPPORTED'
        confidence = 'HIGH'

    synthesis['OVERALL_VERDICT'] = overall
    synthesis['CONFIDENCE'] = confidence

    # Interpretation
    if overall == 'LANGUAGE_ENCODING_SUPPORTED':
        interpretation = """
The tests reveal evidence consistent with linguistic encoding:
- Tokens show non-uniform distribution patterns
- ZIPF exponents vary by zone
- Phonetic or morphological clustering detected

This does NOT mean we can translate the text, but it suggests
the manuscript may encode information in a linguistic manner,
possibly as a domain-specific language or mnemonic system.
"""
    elif overall == 'LANGUAGE_ENCODING_POSSIBLE':
        interpretation = """
Mixed signals detected. Some tests show linguistic properties,
others do not. The manuscript may represent:
- A hybrid system (procedure + language)
- A domain-specific language with unusual properties
- Noise that mimics linguistic patterns
"""
    else:
        interpretation = """
The tests do not support linguistic encoding. The manuscript
appears to be a pure operational/procedural system as previously
concluded. The ZIPF distribution and other language-like features
may be artifacts of the compositional structure rather than
evidence of natural language encoding.
"""

    synthesis['INTERPRETATION'] = interpretation.strip()

    print(f"\nOVERALL VERDICT: {overall}")
    print(f"CONFIDENCE: {confidence}")
    print(f"\n{interpretation}")

    # Save synthesis
    with open('language_investigation_synthesis.md', 'w') as f:
        f.write("# Language Encoding Investigation - Synthesis\n\n")
        f.write(f"*Generated: {datetime.now().isoformat()}*\n\n")
        f.write("---\n\n")
        f.write(f"## OVERALL VERDICT: **{overall}**\n\n")
        f.write(f"**Confidence:** {confidence}\n\n")
        f.write("---\n\n")
        f.write("## Test Results\n\n")
        f.write("| Test | Verdict |\n")
        f.write("|------|--------|\n")
        for name, result in synthesis['test_results'].items():
            f.write(f"| {name} | {result['verdict']} |\n")
        f.write("\n---\n\n")
        f.write("## Signal Summary\n\n")
        f.write(f"- Positive signals: {positive_signals}\n")
        f.write(f"- Weak signals: {weak_signals}\n")
        f.write(f"- Negative signals: {negative_signals}\n\n")
        f.write("---\n\n")
        f.write("## Interpretation\n\n")
        f.write(interpretation.strip() + "\n")

    save_json(synthesis, 'language_investigation_synthesis.json')
    return synthesis

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("LANGUAGE ENCODING INVESTIGATION")
    print("Phase X.5")
    print("=" * 70)

    results = {}

    # Run all tests
    results['phonetic_clustering'] = analyze_phonetic_clustering()
    results['ambiguous_tokens'] = analyze_ambiguous_tokens()
    results['modifier_positions'] = analyze_modifier_positions()
    results['zonal_zipf'] = analyze_zonal_zipf()
    results['dual_use'] = analyze_dual_use_tokens()

    # Generate synthesis
    synthesis = generate_synthesis(results)

    print("\n" + "=" * 70)
    print("INVESTIGATION COMPLETE")
    print("=" * 70)
    print("\nFiles generated:")
    print("  - language_test1_phonetic_clustering.json")
    print("  - language_test2_ambiguous_tokens.json")
    print("  - language_test3_modifier_positions.json")
    print("  - language_test4_zonal_zipf.json")
    print("  - language_test5_dual_use.json")
    print("  - language_investigation_synthesis.json")
    print("  - language_investigation_synthesis.md")

if __name__ == "__main__":
    main()
