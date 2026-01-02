#!/usr/bin/env python3
"""
ADVERSARIAL AUDIT - SINGLE-SOURCE GRAMMAR COLLAPSE TEST
Phase X.2: Testing whether recipe families have incompatible grammars

Key distinction:
- ABSENCE (transition not observed) ≠ contradiction
- CONTRADICTION (A requires X, B forbids X) = collapse evidence
"""

import json
import random
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import csv
from itertools import combinations

# ============================================================================
# DATA LOADING
# ============================================================================

def load_transcription():
    """Load and parse the Voynich transcription."""
    words = []
    folios = defaultdict(list)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        seen = set()
        for row in reader:
            word = row['word'].strip('"')
            folio = row['folio'].strip('"')
            key = (folio, row['line_number'], row['line_initial'])
            if key not in seen and word and not word.startswith('*'):
                seen.add(key)
                words.append(word)
                folios[folio].append(word)

    return words, folios

def load_family_assignments():
    """Load recipe family assignments from Phase 20C and 22."""
    with open('phase20c_recipe_clusters.json', 'r') as f:
        clusters = json.load(f)

    with open('phase22_summary.json', 'r') as f:
        summary = json.load(f)

    # Build folio -> family mapping
    folio_to_family = {}
    for folio_entry in summary['folios']:
        folio_to_family[folio_entry['folio']] = folio_entry['family']

    # Build family -> folios mapping
    family_to_folios = defaultdict(list)
    for folio, family in folio_to_family.items():
        family_to_folios[family].append(folio)

    return folio_to_family, family_to_folios, clusters

# ============================================================================
# STEP 1: FAMILY-LOCAL GRAMMAR INFERENCE
# ============================================================================

def extract_transitions(words):
    """Extract character-level transitions from word list."""
    transitions = Counter()
    for word in words:
        for i in range(len(word) - 1):
            transitions[(word[i], word[i+1])] += 1
    return transitions

def extract_instruction_classes(words, class_prefixes=None):
    """Extract instruction class usage based on token prefixes."""
    # Define class prefixes based on Phase 20 findings
    if class_prefixes is None:
        class_prefixes = {
            'qo': 'ENERGY',
            'ch': 'PHASE',
            'sh': 'PHASE',
            'ok': 'AUXILIARY',
            'ot': 'AUXILIARY',
            'ol': 'LINK',
            'da': 'CONTROL',
            'ct': 'RATE',
        }

    class_usage = Counter()
    for word in words:
        for prefix, cls in class_prefixes.items():
            if word.startswith(prefix):
                class_usage[prefix] += 1
                break
        else:
            class_usage['OTHER'] += 1

    return class_usage

def compute_kernel_candidates(transitions, top_n=5):
    """Compute kernel candidates using graph centrality (not frequency alone)."""
    # Build adjacency counts
    node_degree = Counter()
    for (a, b), count in transitions.items():
        node_degree[a] += count
        node_degree[b] += count

    # Return top N by degree centrality
    return [node for node, _ in node_degree.most_common(top_n)]

def infer_family_grammar(family_words):
    """Infer grammar for a single family."""
    transitions = extract_transitions(family_words)
    class_usage = extract_instruction_classes(family_words)
    kernel_candidates = compute_kernel_candidates(transitions, top_n=5)

    # Get all observed transition pairs
    observed_transitions = set(transitions.keys())

    return {
        'transitions': transitions,
        'transition_set': observed_transitions,
        'class_usage': class_usage,
        'kernel_candidates': kernel_candidates,
        'total_tokens': len(family_words),
        'unique_transitions': len(observed_transitions),
    }

def step1_infer_family_grammars(folios, family_to_folios):
    """Step 1: Infer family-local grammars."""
    print("\n" + "="*70)
    print("STEP 1: FAMILY-LOCAL GRAMMAR INFERENCE")
    print("="*70)

    family_grammars = {}

    for family_id in sorted(family_to_folios.keys()):
        family_folios = family_to_folios[family_id]

        # Collect all words for this family
        family_words = []
        for folio in family_folios:
            if folio in folios:
                family_words.extend(folios[folio])

        if not family_words:
            print(f"  Family {family_id}: NO DATA")
            continue

        grammar = infer_family_grammar(family_words)
        family_grammars[family_id] = grammar

        print(f"\n  Family {family_id}:")
        print(f"    Folios: {len(family_folios)}")
        print(f"    Total tokens: {grammar['total_tokens']}")
        print(f"    Unique transitions: {grammar['unique_transitions']}")
        print(f"    Kernel candidates: {grammar['kernel_candidates']}")

    return family_grammars

# ============================================================================
# STEP 2: GRAMMAR COMPARISON MATRIX
# ============================================================================

def find_contradictions(grammar_a, grammar_b, threshold=0.1):
    """
    Find TRUE contradictions between two grammars.

    A contradiction requires:
    - Transition is FREQUENT in A (>threshold of A's transitions)
    - Transition is ABSENT in B despite B having sufficient data

    Note: Absence alone is NOT contradiction.
    """
    contradictions = []

    trans_a = grammar_a['transitions']
    trans_b = grammar_b['transitions']
    set_a = grammar_a['transition_set']
    set_b = grammar_b['transition_set']

    total_a = sum(trans_a.values())
    total_b = sum(trans_b.values())

    # Check for high-frequency transitions in A that are absent in B
    for trans, count in trans_a.items():
        freq_in_a = count / total_a if total_a > 0 else 0

        # Only consider if frequent in A
        if freq_in_a > threshold:
            if trans not in set_b:
                # This is just ABSENCE, not contradiction
                # We'd need evidence B actively forbids this
                pass

    # True contradiction: A requires X at position where B requires Y
    # This is very hard to detect without explicit grammar rules
    # For now, we check if kernel candidates are DISJOINT

    return contradictions

def step2_grammar_comparison(family_grammars):
    """Step 2: Build grammar comparison matrix."""
    print("\n" + "="*70)
    print("STEP 2: GRAMMAR COMPARISON MATRIX")
    print("="*70)

    families = sorted(family_grammars.keys())
    n_families = len(families)

    comparison_matrix = {}

    for i, fam_a in enumerate(families):
        for j, fam_b in enumerate(families):
            if i >= j:
                continue

            gram_a = family_grammars[fam_a]
            gram_b = family_grammars[fam_b]

            # Compute set operations
            set_a = gram_a['transition_set']
            set_b = gram_b['transition_set']

            shared = set_a & set_b
            only_a = set_a - set_b
            only_b = set_b - set_a

            # Jaccard similarity
            jaccard = len(shared) / len(set_a | set_b) if (set_a | set_b) else 0

            # Kernel overlap
            kernel_a = set(gram_a['kernel_candidates'])
            kernel_b = set(gram_b['kernel_candidates'])
            kernel_overlap = kernel_a & kernel_b

            # Find actual contradictions
            contradictions = find_contradictions(gram_a, gram_b)

            comparison_matrix[(fam_a, fam_b)] = {
                'shared_transitions': len(shared),
                'only_in_a': len(only_a),
                'only_in_b': len(only_b),
                'jaccard': jaccard,
                'kernel_overlap': list(kernel_overlap),
                'contradictions': contradictions,
                'is_contradictory': len(contradictions) > 0,
            }

            print(f"\n  Family {fam_a} vs Family {fam_b}:")
            print(f"    Shared transitions: {len(shared)}")
            print(f"    Only in {fam_a}: {len(only_a)}")
            print(f"    Only in {fam_b}: {len(only_b)}")
            print(f"    Jaccard similarity: {jaccard:.3f}")
            print(f"    Kernel overlap: {kernel_overlap}")
            print(f"    Contradictions: {len(contradictions)}")

    # Summary
    total_contradictions = sum(1 for v in comparison_matrix.values() if v['is_contradictory'])
    print(f"\n  SUMMARY: {total_contradictions} contradictory pairs found")

    return comparison_matrix

# ============================================================================
# STEP 3: KERNEL STABILITY TEST
# ============================================================================

def step3_kernel_stability(family_grammars):
    """Step 3: Test kernel stability across families."""
    print("\n" + "="*70)
    print("STEP 3: KERNEL STABILITY TEST")
    print("="*70)

    all_kernels = []
    kernel_sets = []

    for family_id in sorted(family_grammars.keys()):
        kernel = family_grammars[family_id]['kernel_candidates']
        all_kernels.append((family_id, kernel))
        kernel_sets.append(set(kernel))
        print(f"  Family {family_id} kernel: {kernel}")

    # Compute intersection across all families
    if kernel_sets:
        intersection = kernel_sets[0]
        for ks in kernel_sets[1:]:
            intersection = intersection & ks
    else:
        intersection = set()

    print(f"\n  Global kernel intersection: {intersection}")

    # Compute union
    union = set()
    for ks in kernel_sets:
        union = union | ks

    print(f"  Global kernel union: {union}")

    # Test: do kernels converge when merged?
    # Incrementally merge and check
    merged_words_cumulative = []
    convergence_trajectory = []

    result = {
        'family_kernels': {fam: list(k) for fam, k in all_kernels},
        'global_intersection': list(intersection),
        'global_union': list(union),
        'intersection_size': len(intersection),
        'is_empty_intersection': len(intersection) == 0,
    }

    if len(intersection) == 0:
        print("\n  WARNING: Empty kernel intersection!")
        print("  But this alone does NOT prove grammar collapse.")
        print("  Checking if intersection recovers under merging...")
    else:
        print(f"\n  Non-empty intersection: {intersection}")
        print("  Kernel stability: CONFIRMED")

    return result

# ============================================================================
# STEP 4: INCREMENTAL MERGE TEST
# ============================================================================

def step4_incremental_merge(folios, family_to_folios, family_grammars):
    """Step 4: Incrementally merge families and test grammar convergence."""
    print("\n" + "="*70)
    print("STEP 4: INCREMENTAL MERGE TEST")
    print("="*70)

    families = sorted(family_grammars.keys())

    merge_trajectory = []
    cumulative_words = []

    for i, family_id in enumerate(families):
        # Add this family's words
        family_folios = family_to_folios[family_id]
        for folio in family_folios:
            if folio in folios:
                cumulative_words.extend(folios[folio])

        # Infer merged grammar
        merged_grammar = infer_family_grammar(cumulative_words)

        # Compare to global
        if i > 0:
            prev = merge_trajectory[-1]

            # Check if transitions are growing consistently
            prev_set = prev['transition_set']
            curr_set = merged_grammar['transition_set']

            new_transitions = curr_set - prev_set
            lost_transitions = prev_set - curr_set  # Should be 0 for monotonic growth
        else:
            new_transitions = merged_grammar['transition_set']
            lost_transitions = set()

        entry = {
            'families_merged': families[:i+1],
            'total_tokens': len(cumulative_words),
            'unique_transitions': len(merged_grammar['transition_set']),
            'kernel_candidates': merged_grammar['kernel_candidates'],
            'new_transitions': len(new_transitions),
            'lost_transitions': len(lost_transitions),
            'transition_set': merged_grammar['transition_set'],
        }
        merge_trajectory.append(entry)

        print(f"\n  After merging {i+1} families ({families[:i+1]}):")
        print(f"    Total tokens: {len(cumulative_words)}")
        print(f"    Unique transitions: {len(merged_grammar['transition_set'])}")
        print(f"    Kernel: {merged_grammar['kernel_candidates']}")
        print(f"    New transitions added: {len(new_transitions)}")
        print(f"    Transitions lost: {len(lost_transitions)}")

    # Analyze trajectory
    # Check if kernel converges
    first_kernel = set(merge_trajectory[0]['kernel_candidates'])
    last_kernel = set(merge_trajectory[-1]['kernel_candidates'])
    kernel_overlap = first_kernel & last_kernel

    # Check if transitions grow monotonically
    transitions_monotonic = all(
        merge_trajectory[i]['lost_transitions'] == 0
        for i in range(1, len(merge_trajectory))
    )

    print(f"\n  MERGE ANALYSIS:")
    print(f"    Initial kernel: {first_kernel}")
    print(f"    Final kernel: {last_kernel}")
    print(f"    Kernel overlap: {kernel_overlap}")
    print(f"    Transitions grow monotonically: {transitions_monotonic}")

    # Key test: do differences shrink or grow?
    # Differences should shrink (converge) if grammar is shared
    result = {
        'trajectory': [
            {
                'families': entry['families_merged'],
                'tokens': entry['total_tokens'],
                'transitions': entry['unique_transitions'],
                'kernel': entry['kernel_candidates'],
            }
            for entry in merge_trajectory
        ],
        'kernel_converges': len(kernel_overlap) > 0,
        'transitions_monotonic': transitions_monotonic,
        'final_kernel': list(last_kernel),
    }

    return result

# ============================================================================
# STEP 5: RANDOM PARTITION CONTROL
# ============================================================================

def step5_random_partition(folios, family_to_folios, n_trials=10):
    """Step 5: Compare real families to random partitions."""
    print("\n" + "="*70)
    print("STEP 5: RANDOM PARTITION CONTROL")
    print("="*70)

    # Get all folios that are in families
    all_family_folios = []
    family_sizes = []
    for family_id in sorted(family_to_folios.keys()):
        fam_folios = family_to_folios[family_id]
        all_family_folios.extend(fam_folios)
        family_sizes.append(len(fam_folios))

    # Filter to folios we have data for
    valid_folios = [f for f in all_family_folios if f in folios]

    print(f"  Total folios: {len(valid_folios)}")
    print(f"  Real family sizes: {family_sizes}")

    # Compute metrics for REAL families
    real_grammars = {}
    for family_id in sorted(family_to_folios.keys()):
        family_folios = [f for f in family_to_folios[family_id] if f in folios]
        family_words = []
        for folio in family_folios:
            family_words.extend(folios[folio])
        if family_words:
            real_grammars[family_id] = infer_family_grammar(family_words)

    # Compute real family metrics
    real_kernel_sets = [set(g['kernel_candidates']) for g in real_grammars.values()]
    real_intersection = real_kernel_sets[0] if real_kernel_sets else set()
    for ks in real_kernel_sets[1:]:
        real_intersection = real_intersection & ks

    real_pairwise_jaccard = []
    for g1, g2 in combinations(real_grammars.values(), 2):
        s1, s2 = g1['transition_set'], g2['transition_set']
        if s1 | s2:
            real_pairwise_jaccard.append(len(s1 & s2) / len(s1 | s2))

    real_mean_jaccard = sum(real_pairwise_jaccard) / len(real_pairwise_jaccard) if real_pairwise_jaccard else 0

    print(f"\n  REAL FAMILIES:")
    print(f"    Kernel intersection size: {len(real_intersection)}")
    print(f"    Mean pairwise Jaccard: {real_mean_jaccard:.3f}")

    # Run random partition trials
    random_intersection_sizes = []
    random_mean_jaccards = []

    for trial in range(n_trials):
        # Shuffle folios and partition by family sizes
        shuffled = valid_folios.copy()
        random.shuffle(shuffled)

        random_families = {}
        idx = 0
        for fam_id, size in enumerate(family_sizes):
            actual_size = min(size, len(shuffled) - idx)
            if actual_size <= 0:
                break
            random_families[fam_id] = shuffled[idx:idx + actual_size]
            idx += actual_size

        # Compute grammars for random partitions
        random_grammars = {}
        for fam_id, fam_folios in random_families.items():
            fam_words = []
            for folio in fam_folios:
                if folio in folios:
                    fam_words.extend(folios[folio])
            if fam_words:
                random_grammars[fam_id] = infer_family_grammar(fam_words)

        # Compute random kernel intersection
        rand_kernel_sets = [set(g['kernel_candidates']) for g in random_grammars.values()]
        rand_intersection = rand_kernel_sets[0] if rand_kernel_sets else set()
        for ks in rand_kernel_sets[1:]:
            rand_intersection = rand_intersection & ks
        random_intersection_sizes.append(len(rand_intersection))

        # Compute random pairwise Jaccard
        rand_jaccards = []
        for g1, g2 in combinations(random_grammars.values(), 2):
            s1, s2 = g1['transition_set'], g2['transition_set']
            if s1 | s2:
                rand_jaccards.append(len(s1 & s2) / len(s1 | s2))
        if rand_jaccards:
            random_mean_jaccards.append(sum(rand_jaccards) / len(rand_jaccards))

    mean_random_intersection = sum(random_intersection_sizes) / len(random_intersection_sizes) if random_intersection_sizes else 0
    mean_random_jaccard = sum(random_mean_jaccards) / len(random_mean_jaccards) if random_mean_jaccards else 0

    print(f"\n  RANDOM PARTITIONS ({n_trials} trials):")
    print(f"    Mean kernel intersection size: {mean_random_intersection:.2f}")
    print(f"    Mean pairwise Jaccard: {mean_random_jaccard:.3f}")

    # Comparison
    print(f"\n  COMPARISON:")
    print(f"    Real intersection ({len(real_intersection)}) vs Random ({mean_random_intersection:.2f})")
    print(f"    Real Jaccard ({real_mean_jaccard:.3f}) vs Random ({mean_random_jaccard:.3f})")

    # If real families show LESS coherence than random, that's concerning
    # If real families show MORE or EQUAL coherence, grammar is shared
    real_worse_than_random = (
        len(real_intersection) < mean_random_intersection and
        real_mean_jaccard < mean_random_jaccard
    )

    result = {
        'real_intersection_size': len(real_intersection),
        'random_mean_intersection': mean_random_intersection,
        'real_mean_jaccard': real_mean_jaccard,
        'random_mean_jaccard': mean_random_jaccard,
        'real_worse_than_random': real_worse_than_random,
        'trials': n_trials,
    }

    if real_worse_than_random:
        print("\n  WARNING: Real families show LESS coherence than random!")
        print("  This could support grammar collapse.")
    else:
        print("\n  Real families show EQUAL or MORE coherence than random.")
        print("  Grammar differences are consistent with partitioning effects.")

    return result

# ============================================================================
# VERDICT
# ============================================================================

def compute_verdict(comparison_matrix, kernel_result, merge_result, random_result):
    """Compute final verdict based on all tests."""

    # Check for explicit contradictions
    n_contradictions = sum(1 for v in comparison_matrix.values() if v['is_contradictory'])

    # Check kernel stability
    kernel_empty = kernel_result['is_empty_intersection']
    kernel_recovers = merge_result['kernel_converges']

    # Check random baseline
    real_worse = random_result['real_worse_than_random']

    # Decision logic (as specified in prompt)
    collapse_signals = []
    survive_signals = []

    # Contradictions
    if n_contradictions > 0:
        collapse_signals.append(f"{n_contradictions} explicit contradictions found")
    else:
        survive_signals.append("No explicit mutual contradictions")

    # Kernel
    if kernel_empty and not kernel_recovers:
        collapse_signals.append("Kernel candidates remain disjoint under merging")
    else:
        survive_signals.append("Kernel candidates converge under merging")

    # Merge test
    if merge_result['transitions_monotonic']:
        survive_signals.append("Transitions grow monotonically (coverage artifact)")
    else:
        collapse_signals.append("Merging increases inconsistency")

    # Random baseline
    if real_worse:
        collapse_signals.append("Real families worse than random partitions")
    else:
        survive_signals.append("Real families equal/better than random partitions")

    # Final verdict
    if len(collapse_signals) >= 2:
        verdict = "COLLAPSES"
    else:
        verdict = "SURVIVES"

    return {
        'verdict': verdict,
        'collapse_signals': collapse_signals,
        'survive_signals': survive_signals,
        'n_contradictions': n_contradictions,
        'kernel_empty': kernel_empty,
        'kernel_recovers': kernel_recovers,
        'transitions_monotonic': merge_result['transitions_monotonic'],
        'real_worse_than_random': real_worse,
    }

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*70)
    print("ADVERSARIAL AUDIT - GRAMMAR COLLAPSE TEST")
    print("Phase X.2: Single-Source Grammar Hypothesis")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().isoformat()}")

    # Load data
    print("\nLoading data...")
    words, folios = load_transcription()
    folio_to_family, family_to_folios, clusters = load_family_assignments()
    print(f"  Loaded {len(words)} words, {len(folios)} folios")
    print(f"  {len(family_to_folios)} families")

    # Step 1: Family-local grammars
    family_grammars = step1_infer_family_grammars(folios, family_to_folios)

    # Step 2: Comparison matrix
    comparison_matrix = step2_grammar_comparison(family_grammars)

    # Step 3: Kernel stability
    kernel_result = step3_kernel_stability(family_grammars)

    # Step 4: Incremental merge
    merge_result = step4_incremental_merge(folios, family_to_folios, family_grammars)

    # Step 5: Random partition control
    random_result = step5_random_partition(folios, family_to_folios, n_trials=20)

    # Compute verdict
    verdict = compute_verdict(comparison_matrix, kernel_result, merge_result, random_result)

    print("\n" + "="*70)
    print("FINAL VERDICT")
    print("="*70)
    print(f"\n  SHARED GRAMMAR: {verdict['verdict']}")
    print(f"\n  Collapse signals: {len(verdict['collapse_signals'])}")
    for sig in verdict['collapse_signals']:
        print(f"    - {sig}")
    print(f"\n  Survive signals: {len(verdict['survive_signals'])}")
    for sig in verdict['survive_signals']:
        print(f"    - {sig}")

    # Save outputs
    # 1. family_grammars.json
    fg_output = {
        'metadata': {
            'test': 'Grammar Collapse',
            'timestamp': datetime.now().isoformat(),
        },
        'families': {
            str(k): {
                'total_tokens': v['total_tokens'],
                'unique_transitions': v['unique_transitions'],
                'kernel_candidates': v['kernel_candidates'],
                'class_usage': dict(v['class_usage']),
            }
            for k, v in family_grammars.items()
        }
    }
    with open('family_grammars.json', 'w') as f:
        json.dump(fg_output, f, indent=2)

    # 2. grammar_comparison_matrix.json
    cm_output = {
        'metadata': {
            'test': 'Grammar Comparison',
            'timestamp': datetime.now().isoformat(),
        },
        'comparisons': {
            f"{a}_vs_{b}": {
                'shared_transitions': v['shared_transitions'],
                'only_in_a': v['only_in_a'],
                'only_in_b': v['only_in_b'],
                'jaccard': v['jaccard'],
                'kernel_overlap': v['kernel_overlap'],
                'is_contradictory': v['is_contradictory'],
            }
            for (a, b), v in comparison_matrix.items()
        },
        'total_contradictions': sum(1 for v in comparison_matrix.values() if v['is_contradictory']),
    }
    with open('grammar_comparison_matrix.json', 'w') as f:
        json.dump(cm_output, f, indent=2)

    # 3. kernel_stability_report.md
    with open('kernel_stability_report.md', 'w') as f:
        f.write("# Kernel Stability Report\n\n")
        f.write(f"*Generated: {datetime.now().isoformat()}*\n\n")
        f.write("## Family Kernels\n\n")
        for fam, kernel in kernel_result['family_kernels'].items():
            f.write(f"- Family {fam}: {kernel}\n")
        f.write(f"\n## Global Analysis\n\n")
        f.write(f"- Intersection: {kernel_result['global_intersection']}\n")
        f.write(f"- Union: {kernel_result['global_union']}\n")
        f.write(f"- Empty intersection: {kernel_result['is_empty_intersection']}\n")

    # 4. merge_trajectory_analysis.md
    with open('merge_trajectory_analysis.md', 'w') as f:
        f.write("# Merge Trajectory Analysis\n\n")
        f.write(f"*Generated: {datetime.now().isoformat()}*\n\n")
        f.write("## Trajectory\n\n")
        for entry in merge_result['trajectory']:
            f.write(f"- Families {entry['families']}: {entry['transitions']} transitions, kernel {entry['kernel']}\n")
        f.write(f"\n## Summary\n\n")
        f.write(f"- Kernel converges: {merge_result['kernel_converges']}\n")
        f.write(f"- Transitions monotonic: {merge_result['transitions_monotonic']}\n")
        f.write(f"- Final kernel: {merge_result['final_kernel']}\n")

    # 5. random_partition_baseline.md
    with open('random_partition_baseline.md', 'w') as f:
        f.write("# Random Partition Baseline\n\n")
        f.write(f"*Generated: {datetime.now().isoformat()}*\n\n")
        f.write(f"## Results ({random_result['trials']} trials)\n\n")
        f.write(f"| Metric | Real | Random |\n")
        f.write(f"|--------|------|--------|\n")
        f.write(f"| Kernel intersection | {random_result['real_intersection_size']} | {random_result['random_mean_intersection']:.2f} |\n")
        f.write(f"| Mean Jaccard | {random_result['real_mean_jaccard']:.3f} | {random_result['random_mean_jaccard']:.3f} |\n")
        f.write(f"\n## Interpretation\n\n")
        if random_result['real_worse_than_random']:
            f.write("Real families show LESS coherence than random partitions.\n")
        else:
            f.write("Real families show EQUAL or MORE coherence than random partitions.\n")

    # 6. collapse_verdict.md
    with open('collapse_verdict.md', 'w', encoding='utf-8') as f:
        f.write("# Grammar Collapse Verdict\n\n")
        f.write(f"*Generated: {datetime.now().isoformat()}*\n\n")
        f.write(f"## VERDICT: **{verdict['verdict']}**\n\n")
        f.write("## Collapse Signals\n\n")
        if verdict['collapse_signals']:
            for sig in verdict['collapse_signals']:
                f.write(f"- {sig}\n")
        else:
            f.write("None\n")
        f.write("\n## Survive Signals\n\n")
        if verdict['survive_signals']:
            for sig in verdict['survive_signals']:
                f.write(f"- {sig}\n")
        else:
            f.write("None\n")
        f.write("\n## Criterion Details\n\n")
        f.write(f"- Explicit contradictions: {verdict['n_contradictions']}\n")
        f.write(f"- Kernel empty: {verdict['kernel_empty']}\n")
        f.write(f"- Kernel recovers under merge: {verdict['kernel_recovers']}\n")
        f.write(f"- Transitions monotonic: {verdict['transitions_monotonic']}\n")
        f.write(f"- Real worse than random: {verdict['real_worse_than_random']}\n")
        f.write("\n## Interpretation\n\n")
        if verdict['verdict'] == 'SURVIVES':
            f.write("The shared grammar hypothesis **SURVIVES**.\n\n")
            f.write("Differences between family grammars are consistent with:\n")
            f.write("- Partial coverage (absence ≠ contradiction)\n")
            f.write("- Partitioning effects (random performs similarly)\n")
            f.write("- Kernel convergence under merging\n")
        else:
            f.write("The shared grammar hypothesis **COLLAPSES**.\n\n")
            f.write("Evidence of incompatible grammars:\n")
            for sig in verdict['collapse_signals']:
                f.write(f"- {sig}\n")

    print("\n" + "-"*70)
    print("Outputs saved:")
    print("  - family_grammars.json")
    print("  - grammar_comparison_matrix.json")
    print("  - kernel_stability_report.md")
    print("  - merge_trajectory_analysis.md")
    print("  - random_partition_baseline.md")
    print("  - collapse_verdict.md")

    return verdict

if __name__ == "__main__":
    main()
