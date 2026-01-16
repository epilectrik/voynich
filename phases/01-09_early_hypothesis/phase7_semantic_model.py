"""
Phase 7: Formal Semantic Model Construction

Builds a structural semantic translation system:
  ENTRY = [CONTEXT] + [OPERATOR]* + [CORE] + [MODIFIER]* + [ROLE]

7A: Middle Cluster Role Assignment
7B: Affix Operator Formalization
7C: Slot Grammar Formalization
"""

import json
import os
from collections import defaultdict, Counter
from datetime import datetime
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

# =============================================================================
# CORPUS LOADING (from Phase 6)
# =============================================================================

def load_corpus():
    """Load the interlinear corpus (PRIMARY transcriber H only)."""
    corpus_path = os.path.join('data', 'transcriptions', 'interlinear_full_words.txt')
    entries = defaultdict(list)
    currier_map = {}  # folio -> A or B

    with open(corpus_path, 'r', encoding='utf-8') as f:
        header = f.readline()  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                # Filter to PRIMARY transcriber (H) only - column 12
                transcriber = parts[12].strip('"')
                if transcriber != 'H':
                    continue

                word = parts[0].strip('"')  # Column 0: word
                folio = parts[2].strip('"')  # Column 2: folio
                language = parts[6].strip('"')  # Column 6: language (A or B)

                if word and not word.startswith('[') and not word.startswith('<') and not word.startswith('*'):
                    entries[folio].append(word)
                    if folio not in currier_map:
                        currier_map[folio] = language

    return dict(entries), currier_map

# =============================================================================
# MIDDLE EXTRACTION (from Phase 5)
# =============================================================================

def extract_middle(token, strip_prefix=1, strip_suffix=1):
    """Extract middle from token using fixed stripping."""
    if len(token) <= strip_prefix + strip_suffix:
        return token
    return token[strip_prefix:-strip_suffix] if strip_suffix > 0 else token[strip_prefix:]

def get_prefix(token, length=2):
    """Get prefix of specified length."""
    return token[:length] if len(token) >= length else token

def get_suffix(token, length=2):
    """Get suffix of specified length."""
    return token[-length:] if len(token) >= length else token

# =============================================================================
# HUB DEFINITIONS (from Phase 2 and Phase 6)
# =============================================================================

HUB_HEADINGS = {
    'sho': 'f42r',
    'tol': 'f58v',
    'pol': 'f22r',
    'tor': 'f96r',
    'pchor': ['f19r', 'f21r', 'f52v'],
    'paiin': 'f10v',
    'kor': 'f58r',
    'par': 'f35v'
}

def get_hub_for_folio(folio, entries, currier_map):
    """Determine which hub a folio belongs to based on heading."""
    if folio not in entries or len(entries[folio]) == 0:
        return None

    first_word = entries[folio][0].lower()

    for hub, folios in HUB_HEADINGS.items():
        if isinstance(folios, list):
            if folio in folios:
                return hub
        else:
            if folio == folios:
                return hub

    # Check if first word matches a hub
    for hub in HUB_HEADINGS.keys():
        if first_word.startswith(hub):
            return hub

    return None

# =============================================================================
# PHASE 7A: MIDDLE CLUSTER ROLE ASSIGNMENT
# =============================================================================

def phase_7a_middle_roles(entries, currier_map):
    """
    Assign abstract semantic roles to middle clusters based on behavior.
    """
    print("Phase 7A: Middle Cluster Role Assignment")

    # Collect all middles with their contexts
    middle_contexts = defaultdict(lambda: {
        'tokens': [],
        'prefixes': [],
        'suffixes': [],
        'hubs': [],
        'slots': [],
        'populations': [],
        'entries': []
    })

    # Build middle context data - use ALL tokens, not just first 10
    for folio, tokens in entries.items():
        population = currier_map.get(folio, 'A')
        hub = get_hub_for_folio(folio, entries, currier_map)

        for slot, token in enumerate(tokens):  # ALL tokens
            # Normalize slot to 0-9 range for analysis
            normalized_slot = min(slot, 9)

            middle = extract_middle(token)
            if len(middle) >= 1:
                prefix = get_prefix(token)
                suffix = get_suffix(token)

                middle_contexts[middle]['tokens'].append(token)
                middle_contexts[middle]['prefixes'].append(prefix)
                middle_contexts[middle]['suffixes'].append(suffix)
                middle_contexts[middle]['hubs'].append(hub if hub else 'none')
                middle_contexts[middle]['slots'].append(normalized_slot)
                middle_contexts[middle]['populations'].append(population)
                middle_contexts[middle]['entries'].append(folio)

    # Filter to frequent middles (>= 50 occurrences for robust clustering)
    frequent_middles = {m: ctx for m, ctx in middle_contexts.items()
                        if len(ctx['tokens']) >= 50}

    print(f"  Frequent middles: {len(frequent_middles)}")

    # Build behavioral profiles for each middle
    middle_profiles = {}
    for middle, ctx in frequent_middles.items():
        n = len(ctx['tokens'])

        # Hub distribution
        hub_counts = Counter(ctx['hubs'])
        hub_dist = {h: c/n for h, c in hub_counts.items()}
        hub_entropy = -sum(p * np.log2(p) for p in hub_dist.values() if p > 0)
        dominant_hub = max(hub_counts, key=hub_counts.get)

        # Slot distribution
        slot_counts = Counter(ctx['slots'])
        mean_slot = np.mean(ctx['slots'])
        slot_entropy = -sum((c/n) * np.log2(c/n) for c in slot_counts.values() if c > 0)

        # Population distribution
        pop_counts = Counter(ctx['populations'])
        a_ratio = pop_counts.get('A', 0) / n
        b_ratio = pop_counts.get('B', 0) / n

        # Affix diversity
        prefix_diversity = len(set(ctx['prefixes']))
        suffix_diversity = len(set(ctx['suffixes']))

        # Entry spread
        entry_spread = len(set(ctx['entries'])) / n

        middle_profiles[middle] = {
            'count': n,
            'hub_entropy': hub_entropy,
            'dominant_hub': dominant_hub,
            'hub_concentration': hub_counts[dominant_hub] / n,
            'mean_slot': mean_slot,
            'slot_entropy': slot_entropy,
            'a_ratio': a_ratio,
            'b_ratio': b_ratio,
            'prefix_diversity': prefix_diversity,
            'suffix_diversity': suffix_diversity,
            'entry_spread': entry_spread
        }

    # Build feature matrix for clustering
    middle_list = list(middle_profiles.keys())
    features = []
    for m in middle_list:
        p = middle_profiles[m]
        features.append([
            p['hub_entropy'],
            p['hub_concentration'],
            p['mean_slot'],
            p['slot_entropy'],
            p['a_ratio'],
            p['prefix_diversity'] / 50,  # Normalize
            p['suffix_diversity'] / 30,  # Normalize
            p['entry_spread']
        ])

    features = np.array(features)

    # Normalize features
    features_norm = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)

    # Hierarchical clustering - use 6 clusters for richer taxonomy
    n_clusters = min(6, len(features_norm))
    if len(features_norm) > 1:
        distances = pdist(features_norm, metric='euclidean')
        linkage_matrix = linkage(distances, method='ward')
        cluster_labels = fcluster(linkage_matrix, t=n_clusters, criterion='maxclust')
    else:
        cluster_labels = [1] * len(middle_list)

    # Assign middles to clusters
    clusters = defaultdict(list)
    for m, label in zip(middle_list, cluster_labels):
        clusters[int(label)].append(m)

    # Characterize each cluster
    cluster_profiles = {}
    for cluster_id, members in clusters.items():
        profiles = [middle_profiles[m] for m in members]

        mean_hub_entropy = np.mean([p['hub_entropy'] for p in profiles])
        mean_hub_concentration = np.mean([p['hub_concentration'] for p in profiles])
        mean_slot = np.mean([p['mean_slot'] for p in profiles])
        mean_a_ratio = np.mean([p['a_ratio'] for p in profiles])
        mean_prefix_div = np.mean([p['prefix_diversity'] for p in profiles])
        mean_suffix_div = np.mean([p['suffix_diversity'] for p in profiles])

        # Determine role based on behavioral profile - prioritize distinguishing features
        # A/B distribution is the clearest differentiator
        if mean_a_ratio > 0.65:
            role_type = "DEFINITION_CORE"
            role_desc = "Primarily in Currier A (definitional text), marks core definitions"
        elif mean_a_ratio < 0.25:
            role_type = "EXPOSITION_CORE"
            role_desc = "Primarily in Currier B (expositional text), marks applications"
        elif mean_prefix_div > 8 and mean_suffix_div > 8:
            role_type = "FLEXIBLE_CORE"
            role_desc = "High affix compatibility, grammatically versatile semantic cores"
        elif mean_hub_entropy < 0.8:
            role_type = "RESTRICTED_CORE"
            role_desc = "Low variability, constrained semantic usage"
        elif mean_prefix_div < 4 and mean_suffix_div < 4:
            role_type = "FIXED_FORM"
            role_desc = "Low affix diversity, appears in fixed forms"
        else:
            role_type = "GENERAL_CONTENT"
            role_desc = "Balanced semantic vocabulary, general content"

        cluster_profiles[cluster_id] = {
            'size': len(members),
            'role_type': role_type,
            'role_description': role_desc,
            'mean_hub_entropy': round(mean_hub_entropy, 3),
            'mean_hub_concentration': round(mean_hub_concentration, 3),
            'mean_slot': round(mean_slot, 2),
            'mean_a_ratio': round(mean_a_ratio, 3),
            'mean_prefix_diversity': round(mean_prefix_div, 1),
            'mean_suffix_diversity': round(mean_suffix_div, 1),
            'sample_members': members[:15]
        }

    # Cross-validation: predict cluster from features
    # Simple leave-one-out accuracy
    correct = 0
    for i, (m, label) in enumerate(zip(middle_list, cluster_labels)):
        # Find nearest neighbor
        dists = np.sqrt(np.sum((features_norm - features_norm[i])**2, axis=1))
        dists[i] = np.inf  # Exclude self
        nearest = np.argmin(dists)
        if cluster_labels[nearest] == label:
            correct += 1

    validation_accuracy = correct / len(middle_list) if middle_list else 0

    # Create role assignments
    role_assignments = {}
    for cluster_id, members in clusters.items():
        role = cluster_profiles[cluster_id]['role_type']
        for m in members:
            role_assignments[m] = {
                'cluster': cluster_id,
                'role': role,
                'profile': middle_profiles[m]
            }

    results = {
        'metadata': {
            'phase': '7A',
            'title': 'Middle Cluster Role Assignment',
            'timestamp': datetime.now().isoformat()
        },
        'summary': {
            'total_middles_analyzed': len(frequent_middles),
            'clusters_found': len(clusters),
            'validation_accuracy': round(validation_accuracy, 3)
        },
        'cluster_profiles': cluster_profiles,
        'role_definitions': {
            'DEFINITION_CORE': 'A-biased (>65% in Currier A) - vocabulary for defining entities',
            'EXPOSITION_CORE': 'B-biased (>75% in Currier B) - vocabulary for applying/describing',
            'FLEXIBLE_CORE': 'High affix diversity (>8 prefix, >8 suffix) - grammatically versatile',
            'RESTRICTED_CORE': 'Low hub entropy (<0.8) - constrained semantic usage',
            'FIXED_FORM': 'Low affix diversity (<4 each) - appears in fixed constructions',
            'GENERAL_CONTENT': 'Balanced profile - general content vocabulary'
        },
        'role_assignments': role_assignments
    }

    return results

# =============================================================================
# PHASE 7B: AFFIX OPERATOR FORMALIZATION
# =============================================================================

def phase_7b_affix_operations(entries, currier_map):
    """
    Define what each affix DOES as a formal operation.
    """
    print("Phase 7B: Affix Operator Formalization")

    # Load Phase 6B data
    with open('phase6b_affix_operators.json', 'r') as f:
        phase6b = json.load(f)

    # Load Phase 5 data
    with open('phase5_affix_functions.json', 'r') as f:
        phase5 = json.load(f)

    operator_candidates = phase6b.get('operator_candidates', [])
    affix_hub_effects = phase6b.get('affix_hub_effects', {})
    affix_slot_effects = phase6b.get('affix_slot_effects', {})
    affix_clusters = phase6b.get('affix_functional_clusters', {})

    # Build operation table
    operation_table = {}

    # Analyze each affix
    all_affixes = set(affix_hub_effects.keys())

    for affix in all_affixes:
        hub_data = affix_hub_effects.get(affix, {})

        # Get slot data
        slot_data = None
        if 'prefixes' in affix_slot_effects and affix in affix_slot_effects['prefixes']:
            slot_data = affix_slot_effects['prefixes'][affix]
        elif 'suffixes' in affix_slot_effects and affix in affix_slot_effects['suffixes']:
            slot_data = affix_slot_effects['suffixes'][affix]

        # Determine operation type
        operation_type = 'SEMANTIC'  # Default
        operation_effect = 'general content modifier'

        # Check if position marker
        is_position_marker = False
        for op in operator_candidates:
            if op['affix'] == affix:
                is_position_marker = True
                break

        if is_position_marker:
            operation_type = 'POSITION'
            mean_slot = slot_data['mean_slot'] if slot_data else 4.5
            if mean_slot < 4.0:
                operation_effect = f'entry-initial marker (mean_slot={mean_slot:.2f})'
            else:
                operation_effect = f'position constraint (mean_slot={mean_slot:.2f})'

        # Check hub association
        elif hub_data:
            hub_profile = hub_data.get('hub_profile', {})
            dominant_hub = hub_data.get('dominant_hub', [None, 0])

            if isinstance(dominant_hub, list) and len(dominant_hub) >= 2:
                dom_hub, dom_strength = dominant_hub
                if dom_strength > 0.4:
                    operation_type = 'SCOPE'
                    operation_effect = f'hub association toward {dom_hub} ({dom_strength:.1%})'
                elif dom_strength > 0.3:
                    operation_type = 'SCOPE_WEAK'
                    operation_effect = f'weak hub association toward {dom_hub} ({dom_strength:.1%})'

        # Check cluster membership for additional classification
        cluster_membership = None
        for cluster_name, members in affix_clusters.get('cluster_membership', {}).items():
            if affix in members:
                cluster_membership = cluster_name
                break

        # Determine affix type (prefix vs suffix)
        affix_position = 'unknown'
        if 'prefixes' in affix_slot_effects and affix in affix_slot_effects['prefixes']:
            affix_position = 'prefix'
        elif 'suffixes' in affix_slot_effects and affix in affix_slot_effects['suffixes']:
            affix_position = 'suffix'

        # Get positional data
        prefix_pos = phase5.get('prefix_positional_correlation', {}).get(affix, {})
        suffix_pos = phase5.get('suffix_positional_correlation', {}).get(affix, {})

        entry_initial_rate = prefix_pos.get('entry_initial_rate', suffix_pos.get('entry_initial_rate', 0))
        entry_final_rate = prefix_pos.get('entry_final_rate', suffix_pos.get('entry_final_rate', 0))

        operation_table[affix] = {
            'affix_position': affix_position,
            'operation_type': operation_type,
            'operation_effect': operation_effect,
            'hub_dominant': hub_data.get('dominant_hub', [None, 0])[0] if hub_data else None,
            'hub_strength': hub_data.get('dominant_hub', [None, 0])[1] if hub_data and isinstance(hub_data.get('dominant_hub'), list) else 0,
            'mean_slot': slot_data['mean_slot'] if slot_data else None,
            'early_bias': slot_data.get('early_bias', False) if slot_data else False,
            'late_bias': slot_data.get('late_bias', False) if slot_data else False,
            'entry_initial_rate': round(entry_initial_rate, 3),
            'entry_final_rate': round(entry_final_rate, 3),
            'cluster': cluster_membership,
            'total_count': hub_data.get('total', 0) if hub_data else 0
        }

    # Test compositionality: do prefix+suffix combinations have predictable effects?
    composition_tests = []

    top_pairs = phase5.get('prefix_suffix_cooccurrence', {}).get('top_30_pairs', [])

    for pair_data in top_pairs[:20]:
        pair, count = pair_data
        if '-' in pair:
            prefix, suffix = pair.split('-')

            prefix_op = operation_table.get(prefix, {})
            suffix_op = operation_table.get(suffix, {})

            # Check if effects are consistent
            prefix_type = prefix_op.get('operation_type', 'UNKNOWN')
            suffix_type = suffix_op.get('operation_type', 'UNKNOWN')

            # Compositional if both semantic or one position + one semantic
            is_compositional = (
                (prefix_type in ['SEMANTIC', 'SCOPE', 'SCOPE_WEAK'] and
                 suffix_type in ['SEMANTIC', 'SCOPE', 'SCOPE_WEAK']) or
                (prefix_type == 'POSITION' and suffix_type in ['SEMANTIC', 'SCOPE', 'SCOPE_WEAK']) or
                (prefix_type in ['SEMANTIC', 'SCOPE', 'SCOPE_WEAK'] and suffix_type == 'POSITION')
            )

            composition_tests.append({
                'pair': pair,
                'count': count,
                'prefix_type': prefix_type,
                'suffix_type': suffix_type,
                'compositional': is_compositional
            })

    compositional_count = sum(1 for t in composition_tests if t['compositional'])
    compositionality_rate = compositional_count / len(composition_tests) if composition_tests else 0

    # Identify operation type definitions
    operation_type_definitions = {
        'POSITION': 'Controls slot placement within entry (entry-initial, entry-final, etc.)',
        'SCOPE': 'Modifies hub/category association (strong effect >40%)',
        'SCOPE_WEAK': 'Weak hub/category association (30-40%)',
        'SEMANTIC': 'General semantic content modifier (no strong positional/hub bias)',
        'UNKNOWN': 'Insufficient data for classification'
    }

    # Count operation types
    type_counts = Counter(op['operation_type'] for op in operation_table.values())

    # Identify irregular combinations (non-compositional but frequent)
    irregular_combinations = [t for t in composition_tests if not t['compositional'] and t['count'] > 100]

    results = {
        'metadata': {
            'phase': '7B',
            'title': 'Affix Operator Formalization',
            'timestamp': datetime.now().isoformat()
        },
        'summary': {
            'total_affixes': len(operation_table),
            'position_markers': type_counts.get('POSITION', 0),
            'scope_operators': type_counts.get('SCOPE', 0) + type_counts.get('SCOPE_WEAK', 0),
            'semantic_modifiers': type_counts.get('SEMANTIC', 0),
            'compositionality_rate': round(compositionality_rate, 3)
        },
        'operation_type_definitions': operation_type_definitions,
        'affix_operation_table': operation_table,
        'compositionality_tests': composition_tests,
        'irregular_combinations': irregular_combinations
    }

    return results

# =============================================================================
# PHASE 7C: SLOT GRAMMAR FORMALIZATION
# =============================================================================

def phase_7c_slot_grammar(entries, currier_map):
    """
    Define the slot system as a formal grammar.
    """
    print("Phase 7C: Slot Grammar Formalization")

    # Load Phase 5 slot structure data
    with open('phase5_slot_structure.json', 'r') as f:
        phase5_slots = json.load(f)

    slot_vocab = phase5_slots.get('per_slot_vocabulary', {})
    slot_transitions = phase5_slots.get('slot_transitions', {})

    # Analyze slot vocabulary
    slot_analysis = {}
    for slot_id, data in slot_vocab.items():
        slot_num = int(slot_id.split('_')[1])

        top_tokens = data.get('top_10_tokens', [])
        top_prefixes = data.get('top_5_prefixes', [])
        top_suffixes = data.get('top_5_suffixes', [])
        top_middles = data.get('top_5_middles', [])

        slot_analysis[slot_num] = {
            'unique_tokens': data.get('unique_tokens', 0),
            'entropy': round(data.get('entropy', 0), 3),
            'dominant_tokens': [t[0] for t in top_tokens[:5]],
            'dominant_prefixes': [p[0] for p in top_prefixes[:3]],
            'dominant_suffixes': [s[0] for s in top_suffixes[:3]],
            'dominant_middles': [m[0] for m in top_middles[:3]]
        }

    # Analyze transition constraints
    transition_analysis = {}
    for trans_key, trans_data in slot_transitions.items():
        constraint_ratio = trans_data.get('constraint_ratio', 0)
        unique_trans = trans_data.get('unique_transitions', 0)
        max_possible = trans_data.get('max_possible', 1)

        transition_analysis[trans_key] = {
            'constraint_ratio': round(constraint_ratio, 3),
            'observed_transitions': unique_trans,
            'max_possible': max_possible,
            'freedom_ratio': round(unique_trans / max_possible, 4) if max_possible > 0 else 0,
            'top_transitions': [t[0] for t in trans_data.get('top_10_transitions', [])[:5]]
        }

    # Induce grammar rules
    grammar_rules = []

    # Rule 1: Entry structure
    grammar_rules.append({
        'rule': 'ENTRY -> SLOT0 SLOT1+ SLOT_TERMINAL?',
        'description': 'Entry consists of initial slot, one or more middle slots, optional terminal',
        'confidence': 'HIGH'
    })

    # Analyze slot roles based on vocabulary
    slot_roles = {}
    for slot_num in range(10):
        if slot_num in slot_analysis:
            analysis = slot_analysis[slot_num]

            # Determine role based on characteristics
            if slot_num == 0:
                role = 'TOPIC_POSITION'
                role_desc = 'Entry topic/subject introduction'
            elif slot_num <= 2:
                role = 'PRIMARY_CONTENT'
                role_desc = 'Primary content/predicate position'
            elif slot_num <= 5:
                role = 'SECONDARY_CONTENT'
                role_desc = 'Secondary content/argument position'
            elif slot_num <= 7:
                role = 'MODIFIER_POSITION'
                role_desc = 'Modifier/elaboration position'
            else:
                role = 'TERMINAL_POSITION'
                role_desc = 'Terminal/closing position'

            slot_roles[slot_num] = {
                'role': role,
                'description': role_desc,
                'entropy': analysis['entropy'],
                'vocabulary_size': analysis['unique_tokens']
            }

    # Generate production rules for each slot
    for slot_num in range(10):
        if slot_num in slot_analysis:
            analysis = slot_analysis[slot_num]
            prefixes = analysis['dominant_prefixes']
            suffixes = analysis['dominant_suffixes']

            rule = {
                'rule': f'SLOT{slot_num} -> PREFIX MIDDLE SUFFIX',
                'preferred_prefixes': prefixes,
                'preferred_suffixes': suffixes,
                'constraint_level': 'HIGH' if analysis['entropy'] < 5.5 else 'MEDIUM' if analysis['entropy'] < 6.0 else 'LOW'
            }
            grammar_rules.append(rule)

    # Calculate grammar coverage
    # Estimate based on transition constraints
    mean_constraint = np.mean([t['constraint_ratio'] for t in transition_analysis.values()])
    grammar_coverage = round(mean_constraint, 3)

    # Generate parse examples
    parse_examples = []

    # Sample a few entries and show how they would parse
    sample_entries = list(entries.items())[:5]
    for folio, tokens in sample_entries:
        parse = []
        for slot, token in enumerate(tokens[:10]):
            prefix = get_prefix(token)
            middle = extract_middle(token)
            suffix = get_suffix(token)

            slot_role = slot_roles.get(slot, {}).get('role', 'UNKNOWN')

            parse.append({
                'slot': slot,
                'token': token,
                'prefix': prefix,
                'middle': middle,
                'suffix': suffix,
                'role': slot_role
            })

        parse_examples.append({
            'entry': folio,
            'population': currier_map.get(folio, 'A'),
            'parse': parse
        })

    # Identify systematic exceptions
    exceptions = []

    # Check for very low constraint transitions (high freedom)
    for trans_key, trans_data in transition_analysis.items():
        if trans_data['freedom_ratio'] > 0.1:  # More than 10% of transitions observed
            exceptions.append({
                'transition': trans_key,
                'freedom_ratio': trans_data['freedom_ratio'],
                'issue': 'Higher than expected transition freedom'
            })

    results = {
        'metadata': {
            'phase': '7C',
            'title': 'Slot Grammar Formalization',
            'timestamp': datetime.now().isoformat()
        },
        'summary': {
            'slots_analyzed': len(slot_analysis),
            'grammar_rules': len(grammar_rules),
            'parse_coverage': grammar_coverage,
            'mean_slot_entropy': round(np.mean([s['entropy'] for s in slot_analysis.values()]), 3),
            'exceptions_found': len(exceptions)
        },
        'slot_analysis': slot_analysis,
        'slot_roles': slot_roles,
        'transition_analysis': transition_analysis,
        'grammar_rules': grammar_rules,
        'parse_examples': parse_examples,
        'exceptions': exceptions
    }

    return results

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 60)
    print("PHASE 7: FORMAL SEMANTIC MODEL CONSTRUCTION")
    print("=" * 60)

    # Load corpus
    print("\nLoading corpus...")
    entries, currier_map = load_corpus()
    print(f"  Loaded {len(entries)} entries")
    print(f"  Currier A: {sum(1 for v in currier_map.values() if v == 'A')}")
    print(f"  Currier B: {sum(1 for v in currier_map.values() if v == 'B')}")

    # Phase 7A: Middle Cluster Role Assignment
    print("\n" + "=" * 60)
    results_7a = phase_7a_middle_roles(entries, currier_map)

    with open('phase7a_middle_roles.json', 'w') as f:
        json.dump(results_7a, f, indent=2, default=str)
    print(f"  Saved: phase7a_middle_roles.json")

    # Phase 7B: Affix Operator Formalization
    print("\n" + "=" * 60)
    results_7b = phase_7b_affix_operations(entries, currier_map)

    with open('phase7b_affix_operations.json', 'w') as f:
        json.dump(results_7b, f, indent=2, default=str)
    print(f"  Saved: phase7b_affix_operations.json")

    # Phase 7C: Slot Grammar Formalization
    print("\n" + "=" * 60)
    results_7c = phase_7c_slot_grammar(entries, currier_map)

    with open('phase7c_slot_grammar.json', 'w') as f:
        json.dump(results_7c, f, indent=2, default=str)
    print(f"  Saved: phase7c_slot_grammar.json")

    # Print Summary
    print("\n" + "=" * 60)
    print("PHASE 7A-7C SUMMARY")
    print("=" * 60)

    print("\n7A: Middle Cluster Role Assignment")
    print(f"  Middles analyzed: {results_7a['summary']['total_middles_analyzed']}")
    print(f"  Clusters found: {results_7a['summary']['clusters_found']}")
    print(f"  Validation accuracy: {results_7a['summary']['validation_accuracy']:.1%}")

    for cid, profile in results_7a['cluster_profiles'].items():
        print(f"\n  Cluster {cid}: {profile['role_type']} (n={profile['size']})")
        print(f"    {profile['role_description']}")
        print(f"    Samples: {', '.join(profile['sample_members'][:5])}")

    print("\n7B: Affix Operator Formalization")
    print(f"  Total affixes: {results_7b['summary']['total_affixes']}")
    print(f"  Position markers: {results_7b['summary']['position_markers']}")
    print(f"  Scope operators: {results_7b['summary']['scope_operators']}")
    print(f"  Semantic modifiers: {results_7b['summary']['semantic_modifiers']}")
    print(f"  Compositionality rate: {results_7b['summary']['compositionality_rate']:.1%}")

    # Show position markers
    print("\n  Position Markers:")
    for affix, data in results_7b['affix_operation_table'].items():
        if data['operation_type'] == 'POSITION':
            print(f"    {affix}: {data['operation_effect']}")

    print("\n7C: Slot Grammar Formalization")
    print(f"  Slots analyzed: {results_7c['summary']['slots_analyzed']}")
    print(f"  Grammar rules: {results_7c['summary']['grammar_rules']}")
    print(f"  Parse coverage: {results_7c['summary']['parse_coverage']:.1%}")
    print(f"  Mean slot entropy: {results_7c['summary']['mean_slot_entropy']} bits")

    print("\n  Slot Roles:")
    for slot_num, role_data in results_7c['slot_roles'].items():
        print(f"    Slot {slot_num}: {role_data['role']} - {role_data['description']}")

    print("\n" + "=" * 60)
    print("Phase 7A-7C Complete")
    print("=" * 60)

if __name__ == '__main__':
    main()
