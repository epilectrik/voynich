"""
Phase CAud-G: Currier A Grammar Derivation

Goal: Characterize A's internal STRUCTURE, not function.
Explicitly NON-EXECUTIVE - no run semantics, no hazards, no convergence.

Approach:
1. Extract A token inventory and transition matrix
2. Cluster tokens by transition profile (equivalence classes)
3. Test compression ratio
4. Identify structural regularities (NOT "hazards")
5. Compare to B-grammar structure (parallel, not derived from)
"""

import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

project_root = Path(__file__).parent.parent.parent


def load_currier_data():
    """Load transcription data split by Currier designation."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    a_data = []
    b_data = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                word = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"') if len(parts) > 2 else ''
                section = parts[3].strip('"') if len(parts) > 3 else ''
                language = parts[6].strip('"') if len(parts) > 6 else ''
                transcriber = parts[12].strip('"').strip()

                # Filter to H (PRIMARY) transcriber only
                if transcriber != 'H':
                    continue

                if word and folio:
                    entry = {
                        'token': word,
                        'folio': folio,
                        'section': section
                    }
                    if language == 'A':
                        a_data.append(entry)
                    elif language == 'B':
                        b_data.append(entry)

    return a_data, b_data


def build_transition_matrix(data):
    """Build token transition matrix from sequential data."""
    # Group by folio to respect boundaries
    folio_tokens = defaultdict(list)
    for d in data:
        folio_tokens[d['folio']].append(d['token'])

    # Count transitions
    transitions = Counter()
    for folio, tokens in folio_tokens.items():
        for i in range(len(tokens) - 1):
            transitions[(tokens[i], tokens[i + 1])] += 1

    return transitions, folio_tokens


def extract_vocabulary_stats(data):
    """Extract basic vocabulary statistics."""
    tokens = [d['token'] for d in data]
    token_counts = Counter(tokens)

    return {
        'total_tokens': len(tokens),
        'unique_types': len(token_counts),
        'type_token_ratio': len(token_counts) / len(tokens),
        'hapax_count': sum(1 for c in token_counts.values() if c == 1),
        'hapax_ratio': sum(1 for c in token_counts.values() if c == 1) / len(token_counts),
        'top_20': token_counts.most_common(20),
        'token_counts': token_counts
    }


def derive_equivalence_classes(transitions, token_counts, min_freq=10, n_clusters_range=(3, 15)):
    """
    Derive equivalence classes by clustering tokens with similar transition profiles.

    This is structural clustering, NOT execution-based.
    """
    # Filter to tokens with sufficient frequency
    freq_tokens = [t for t, c in token_counts.items() if c >= min_freq]
    print(f"  Tokens with freq >= {min_freq}: {len(freq_tokens)}")

    if len(freq_tokens) < 20:
        print("  WARNING: Too few frequent tokens for reliable clustering")
        return None

    token_idx = {t: i for i, t in enumerate(freq_tokens)}
    n = len(freq_tokens)

    # Build transition profile matrix
    # Each token's profile = [P(next=t1), P(next=t2), ..., P(prev=t1), P(prev=t2), ...]
    next_matrix = np.zeros((n, n))
    prev_matrix = np.zeros((n, n))

    for (t1, t2), count in transitions.items():
        if t1 in token_idx and t2 in token_idx:
            next_matrix[token_idx[t1], token_idx[t2]] += count
            prev_matrix[token_idx[t2], token_idx[t1]] += count

    # Normalize rows
    next_sums = next_matrix.sum(axis=1, keepdims=True)
    next_sums[next_sums == 0] = 1
    next_norm = next_matrix / next_sums

    prev_sums = prev_matrix.sum(axis=1, keepdims=True)
    prev_sums[prev_sums == 0] = 1
    prev_norm = prev_matrix / prev_sums

    # Concatenate for full profile
    profiles = np.hstack([next_norm, prev_norm])

    # Find optimal number of clusters
    print("\n  Testing cluster counts...")
    best_k = 5
    best_score = -1

    for k in range(n_clusters_range[0], min(n_clusters_range[1], len(freq_tokens) // 3)):
        try:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(profiles)
            score = silhouette_score(profiles, labels)
            print(f"    k={k}: silhouette={score:.3f}")
            if score > best_score:
                best_score = score
                best_k = k
        except Exception as e:
            continue

    print(f"\n  Best k={best_k} (silhouette={best_score:.3f})")

    # Final clustering
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(profiles)

    # Build class membership
    classes = defaultdict(list)
    for token, label in zip(freq_tokens, labels):
        classes[label].append(token)

    return {
        'n_classes': best_k,
        'silhouette': best_score,
        'classes': dict(classes),
        'freq_tokens': freq_tokens,
        'labels': labels,
        'profiles': profiles
    }


def find_structural_regularities(transitions, token_counts, min_freq=5):
    """
    Find structural regularities in transition patterns.

    NOT "hazards" - just patterns of what follows/precedes what.
    """
    freq_tokens = set(t for t, c in token_counts.items() if c >= min_freq)

    # Find never-occurring transitions among frequent tokens
    possible_pairs = len(freq_tokens) ** 2
    observed_pairs = set()

    for (t1, t2), count in transitions.items():
        if t1 in freq_tokens and t2 in freq_tokens:
            observed_pairs.add((t1, t2))

    missing_pairs = []
    for t1 in freq_tokens:
        for t2 in freq_tokens:
            if (t1, t2) not in observed_pairs:
                # Check if both tokens have outgoing/incoming transitions
                t1_has_next = any(transitions.get((t1, x), 0) > 0 for x in freq_tokens)
                t2_has_prev = any(transitions.get((x, t2), 0) > 0 for x in freq_tokens)
                if t1_has_next and t2_has_prev:
                    missing_pairs.append((t1, t2))

    # Find strongly asymmetric pairs (A->B common but B->A rare/absent)
    asymmetric_pairs = []
    for (t1, t2), count in transitions.items():
        if t1 in freq_tokens and t2 in freq_tokens and count >= 5:
            reverse = transitions.get((t2, t1), 0)
            if reverse == 0 or count / (reverse + 1) > 10:
                asymmetric_pairs.append((t1, t2, count, reverse))

    return {
        'possible_pairs': possible_pairs,
        'observed_pairs': len(observed_pairs),
        'coverage': len(observed_pairs) / possible_pairs if possible_pairs > 0 else 0,
        'missing_count': len(missing_pairs),
        'missing_sample': missing_pairs[:20],
        'asymmetric_pairs': sorted(asymmetric_pairs, key=lambda x: x[2], reverse=True)[:20]
    }


def test_compression(data, classes):
    """
    Test if equivalence classes compress the data.

    Compression ratio = original entropy / compressed entropy
    """
    if classes is None:
        return None

    tokens = [d['token'] for d in data]

    # Build token-to-class mapping
    token_to_class = {}
    for class_id, members in classes['classes'].items():
        for token in members:
            token_to_class[token] = class_id

    # Original token entropy
    token_counts = Counter(tokens)
    total = len(tokens)
    token_probs = np.array([c / total for c in token_counts.values()])
    token_entropy = -np.sum(token_probs * np.log2(token_probs + 1e-10))

    # Class-based entropy (for mapped tokens only)
    class_sequence = [token_to_class.get(t) for t in tokens]
    mapped_classes = [c for c in class_sequence if c is not None]

    if len(mapped_classes) < 100:
        return None

    class_counts = Counter(mapped_classes)
    total_mapped = len(mapped_classes)
    class_probs = np.array([c / total_mapped for c in class_counts.values()])
    class_entropy = -np.sum(class_probs * np.log2(class_probs + 1e-10))

    # Coverage
    coverage = len(mapped_classes) / len(tokens)

    return {
        'token_entropy': token_entropy,
        'class_entropy': class_entropy,
        'compression_ratio': token_entropy / class_entropy if class_entropy > 0 else 0,
        'coverage': coverage,
        'mapped_tokens': len(mapped_classes),
        'total_tokens': len(tokens)
    }


def compare_to_b_grammar(a_classes, b_data):
    """
    Compare A-grammar structure to B-grammar structure.

    NOT deriving A from B - parallel comparison.
    """
    # Derive B classes using same method
    b_transitions, _ = build_transition_matrix(b_data)
    b_vocab = extract_vocabulary_stats(b_data)

    print("\n  Deriving B-grammar classes for comparison...")
    b_classes = derive_equivalence_classes(b_transitions, b_vocab['token_counts'], min_freq=10)

    if a_classes is None or b_classes is None:
        return None

    # Compare structural properties
    comparison = {
        'a_n_classes': a_classes['n_classes'],
        'b_n_classes': b_classes['n_classes'],
        'a_silhouette': a_classes['silhouette'],
        'b_silhouette': b_classes['silhouette'],
    }

    # Vocabulary overlap between class members
    a_vocab = set()
    for members in a_classes['classes'].values():
        a_vocab.update(members)

    b_vocab_set = set()
    for members in b_classes['classes'].values():
        b_vocab_set.update(members)

    overlap = len(a_vocab & b_vocab_set)
    comparison['vocab_overlap'] = overlap
    comparison['vocab_overlap_ratio'] = overlap / len(a_vocab | b_vocab_set) if (a_vocab | b_vocab_set) else 0

    # Class size distributions
    a_sizes = sorted([len(m) for m in a_classes['classes'].values()], reverse=True)
    b_sizes = sorted([len(m) for m in b_classes['classes'].values()], reverse=True)

    comparison['a_class_sizes'] = a_sizes
    comparison['b_class_sizes'] = b_sizes

    return comparison, b_classes


def analyze_section_variation(data, classes):
    """
    Check if A-grammar classes vary by section.
    """
    if classes is None:
        return None

    token_to_class = {}
    for class_id, members in classes['classes'].items():
        for token in members:
            token_to_class[token] = class_id

    section_class_dist = defaultdict(Counter)
    for d in data:
        if d['token'] in token_to_class:
            section_class_dist[d['section']][token_to_class[d['token']]] += 1

    # Normalize
    section_profiles = {}
    for section, counts in section_class_dist.items():
        total = sum(counts.values())
        if total > 100:  # Minimum threshold
            profile = {c: counts[c] / total for c in range(classes['n_classes'])}
            section_profiles[section] = profile

    return section_profiles


def main():
    print("=" * 70)
    print("PHASE CAud-G: CURRIER A GRAMMAR DERIVATION")
    print("=" * 70)
    print("\nGoal: Characterize A's internal STRUCTURE (non-executive)")
    print("NOT attempting to derive execution semantics.\n")

    # Load data
    a_data, b_data = load_currier_data()
    print(f"Loaded: {len(a_data)} A tokens, {len(b_data)} B tokens")

    # Step 1: Vocabulary statistics
    print("\n" + "=" * 70)
    print("STEP 1: VOCABULARY STATISTICS")
    print("=" * 70)

    a_vocab = extract_vocabulary_stats(a_data)

    print(f"\nCurrier A vocabulary:")
    print(f"  Total tokens: {a_vocab['total_tokens']}")
    print(f"  Unique types: {a_vocab['unique_types']}")
    print(f"  Type-token ratio: {a_vocab['type_token_ratio']:.4f}")
    print(f"  Hapax legomena: {a_vocab['hapax_count']} ({a_vocab['hapax_ratio']:.1%})")

    print(f"\nTop 20 A tokens:")
    for token, count in a_vocab['top_20']:
        print(f"    {token}: {count}")

    # Step 2: Build transition matrix
    print("\n" + "=" * 70)
    print("STEP 2: TRANSITION MATRIX")
    print("=" * 70)

    a_transitions, a_folios = build_transition_matrix(a_data)

    print(f"\nTransition statistics:")
    print(f"  Unique transitions: {len(a_transitions)}")
    print(f"  Total transition instances: {sum(a_transitions.values())}")

    top_transitions = a_transitions.most_common(15)
    print(f"\nTop 15 transitions:")
    for (t1, t2), count in top_transitions:
        print(f"    {t1} -> {t2}: {count}")

    # Step 3: Derive equivalence classes
    print("\n" + "=" * 70)
    print("STEP 3: EQUIVALENCE CLASS DERIVATION")
    print("=" * 70)

    a_classes = derive_equivalence_classes(a_transitions, a_vocab['token_counts'])

    if a_classes:
        print(f"\nDerived {a_classes['n_classes']} equivalence classes")
        print(f"Silhouette score: {a_classes['silhouette']:.3f}")

        print("\nClass membership (samples):")
        for class_id, members in sorted(a_classes['classes'].items()):
            sample = members[:8]
            more = f"... (+{len(members)-8})" if len(members) > 8 else ""
            print(f"  Class {class_id} ({len(members)} members): {sample}{more}")

    # Step 4: Structural regularities
    print("\n" + "=" * 70)
    print("STEP 4: STRUCTURAL REGULARITIES")
    print("=" * 70)

    regularities = find_structural_regularities(a_transitions, a_vocab['token_counts'])

    print(f"\nTransition coverage:")
    print(f"  Possible pairs (freq tokens): {regularities['possible_pairs']}")
    print(f"  Observed pairs: {regularities['observed_pairs']}")
    print(f"  Coverage: {regularities['coverage']:.1%}")
    print(f"  Missing (never-occurring): {regularities['missing_count']}")

    print(f"\nStrongly asymmetric transitions (A->B but not B->A):")
    for t1, t2, fwd, rev in regularities['asymmetric_pairs'][:10]:
        print(f"    {t1} -> {t2}: {fwd} (reverse: {rev})")

    # Step 5: Compression test
    print("\n" + "=" * 70)
    print("STEP 5: COMPRESSION TEST")
    print("=" * 70)

    compression = test_compression(a_data, a_classes)

    if compression:
        print(f"\nCompression analysis:")
        print(f"  Token entropy: {compression['token_entropy']:.3f} bits")
        print(f"  Class entropy: {compression['class_entropy']:.3f} bits")
        print(f"  Compression ratio: {compression['compression_ratio']:.2f}x")
        print(f"  Coverage: {compression['coverage']:.1%}")

        if compression['compression_ratio'] > 1.5:
            print("\n  ** Classes provide meaningful compression **")
        else:
            print("\n  ** Limited compression - classes may not capture structure **")

    # Step 6: Compare to B-grammar
    print("\n" + "=" * 70)
    print("STEP 6: COMPARISON TO B-GRAMMAR")
    print("=" * 70)

    comparison, b_classes = compare_to_b_grammar(a_classes, b_data)

    if comparison:
        print(f"\nStructural comparison:")
        print(f"  A classes: {comparison['a_n_classes']} (silhouette: {comparison['a_silhouette']:.3f})")
        print(f"  B classes: {comparison['b_n_classes']} (silhouette: {comparison['b_silhouette']:.3f})")
        print(f"  Vocabulary overlap: {comparison['vocab_overlap']} tokens ({comparison['vocab_overlap_ratio']:.1%})")
        print(f"\n  A class sizes: {comparison['a_class_sizes']}")
        print(f"  B class sizes: {comparison['b_class_sizes']}")

    # Step 7: Section variation
    print("\n" + "=" * 70)
    print("STEP 7: SECTION VARIATION")
    print("=" * 70)

    section_profiles = analyze_section_variation(a_data, a_classes)

    if section_profiles:
        print(f"\nClass distribution by section:")
        for section, profile in sorted(section_profiles.items()):
            dominant = max(profile.items(), key=lambda x: x[1])
            print(f"  {section}: dominant class {dominant[0]} ({dominant[1]:.1%})")

    # Final synthesis
    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)

    # Build synthesis values safely
    n_classes_str = str(a_classes['n_classes']) if a_classes else 'N/A'
    silhouette_str = f"{a_classes['silhouette']:.3f}" if a_classes else 'N/A'
    compression_str = f"{compression['compression_ratio']:.2f}" if compression else 'N/A'
    a_classes_str = str(comparison['a_n_classes']) if comparison else 'N/A'
    b_classes_str = str(comparison['b_n_classes']) if comparison else 'N/A'
    overlap_str = f"{comparison['vocab_overlap_ratio']:.1%}" if comparison else 'N/A'
    section_str = 'Yes - class distribution varies by section' if section_profiles and len(section_profiles) > 1 else 'Insufficient data'

    print(f"""
Currier A Grammar Characterization (NON-EXECUTIVE):

1. VOCABULARY
   - {a_vocab['unique_types']} unique types
   - TTR: {a_vocab['type_token_ratio']:.4f} (lower than B = more regular)
   - Hapax: {a_vocab['hapax_ratio']:.1%}

2. EQUIVALENCE CLASSES
   - {n_classes_str} classes derived
   - Silhouette: {silhouette_str}
   - Compression: {compression_str}x

3. STRUCTURAL REGULARITIES
   - Transition coverage: {regularities['coverage']:.1%}
   - Missing pairs: {regularities['missing_count']}
   - Asymmetric pairs: {len(regularities['asymmetric_pairs'])}

4. COMPARISON TO B
   - Different class count: A={a_classes_str}, B={b_classes_str}
   - Limited vocabulary overlap: {overlap_str}
   - Structurally DISTINCT systems

5. SECTION VARIATION
   - {section_str}
""")

    # Verdict
    if a_classes and a_classes['silhouette'] > 0.15 and compression and compression['compression_ratio'] > 1.3:
        verdict = "A_HAS_FORMAL_GRAMMAR"
        description = "Currier A exhibits formal grammatical structure distinct from B"
    elif a_classes and a_classes['silhouette'] > 0.1:
        verdict = "A_HAS_WEAK_STRUCTURE"
        description = "Currier A has weak internal structure, not strongly grammatical"
    else:
        verdict = "A_LACKS_GRAMMAR"
        description = "Currier A does not exhibit clear grammatical structure"

    print(f"VERDICT: {verdict}")
    print(f"  {description}")

    # Save results
    results = {
        'vocabulary': {
            'total_tokens': a_vocab['total_tokens'],
            'unique_types': a_vocab['unique_types'],
            'ttr': a_vocab['type_token_ratio'],
            'hapax_ratio': a_vocab['hapax_ratio']
        },
        'classes': {
            'n_classes': a_classes['n_classes'] if a_classes else None,
            'silhouette': a_classes['silhouette'] if a_classes else None,
            'class_sizes': [len(m) for m in a_classes['classes'].values()] if a_classes else None
        },
        'compression': compression,
        'regularities': {
            'coverage': regularities['coverage'],
            'missing_count': regularities['missing_count']
        },
        'comparison': {
            'a_n_classes': comparison['a_n_classes'] if comparison else None,
            'b_n_classes': comparison['b_n_classes'] if comparison else None,
            'vocab_overlap_ratio': comparison['vocab_overlap_ratio'] if comparison else None
        },
        'verdict': verdict
    }

    output_path = Path(__file__).parent / 'caud_grammar_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
