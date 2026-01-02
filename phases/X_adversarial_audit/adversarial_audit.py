#!/usr/bin/env python3
"""
ADVERSARIAL AUDIT - Model Destruction Attempt
Phase X: Falsification-First Analysis

Goal: Break the Voynich control system model through rigorous null hypothesis testing.
"""

import json
import random
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import csv

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
            # Deduplicate across transcribers - use first occurrence
            key = (folio, row['line_number'], row['line_initial'])
            if key not in seen and word and not word.startswith('*'):
                seen.add(key)
                words.append(word)
                folios[folio].append(word)

    return words, folios

def load_phase_data():
    """Load relevant phase data files."""
    data = {}

    files = [
        ('equivalence', 'phase20a_operator_equivalence.json'),
        ('grammar', 'phase20d_canonical_grammar.json'),
        ('topology', 'phase15a_internal_topology.json'),
        ('vocabulary', 'phase15d_vocabulary_structure.json'),
        ('signatures', 'phase22b_synthesis.json'),
    ]

    for key, filename in files:
        try:
            with open(filename, 'r') as f:
                data[key] = json.load(f)
        except:
            data[key] = None

    return data

# ============================================================================
# ATTACK 1: KERNEL COLLAPSE TEST
# ============================================================================

def extract_subwords(word):
    """Extract character-level subunits from a word."""
    # Use the same subword extraction as the original model
    subwords = []
    i = 0
    while i < len(word):
        # Check for known multi-char tokens
        for length in [5, 4, 3, 2, 1]:
            if i + length <= len(word):
                sub = word[i:i+length]
                subwords.append(sub)
                i += length
                break
    return subwords

def compute_token_frequencies(words):
    """Compute token (subword) frequencies."""
    freq = Counter()
    for word in words:
        for char in word:
            freq[char] += 1
    return freq

def compute_bigram_frequencies(words):
    """Compute character bigram frequencies."""
    bigrams = Counter()
    for word in words:
        for i in range(len(word) - 1):
            bigrams[(word[i], word[i+1])] += 1
    return bigrams

def compute_centrality(freq_dict, bigrams):
    """Compute simple centrality based on co-occurrence."""
    centrality = Counter()
    # Centrality = sum of bigram weights involving this token
    for (a, b), count in bigrams.items():
        centrality[a] += count
        centrality[b] += count
    return centrality

def generate_frequency_matched_surrogate(words, n_samples=1000):
    """Generate surrogate corpus preserving unigram and bigram distributions."""
    freq = compute_token_frequencies(words)
    bigrams = compute_bigram_frequencies(words)

    # Build Markov chain from bigrams
    transitions = defaultdict(Counter)
    for (a, b), count in bigrams.items():
        transitions[a][b] = count

    # Generate surrogate words using Markov chain
    surrogate_words = []
    chars = list(freq.keys())
    weights = [freq[c] for c in chars]

    for _ in range(n_samples):
        # Random length matching original distribution
        length = random.randint(2, 10)
        # Start with frequency-weighted random char
        word = random.choices(chars, weights=weights, k=1)[0]
        for _ in range(length - 1):
            current = word[-1]
            if current in transitions and transitions[current]:
                next_chars = list(transitions[current].keys())
                next_weights = list(transitions[current].values())
                word += random.choices(next_chars, weights=next_weights, k=1)[0]
            else:
                word += random.choices(chars, weights=weights, k=1)[0]
        surrogate_words.append(word)

    return surrogate_words

def attack1_kernel_collapse(words, n_surrogates=100):
    """
    Attack 1: Test if kernel centrality is an artifact of frequency alone.

    Null hypothesis: Kernel nodes (k, h, e) emerge inevitably from any corpus
    with similar frequency distributions.
    """
    print("\n" + "="*70)
    print("ATTACK 1: KERNEL COLLAPSE TEST")
    print("="*70)

    # Compute original centrality
    orig_freq = compute_token_frequencies(words)
    orig_bigrams = compute_bigram_frequencies(words)
    orig_centrality = compute_centrality(orig_freq, orig_bigrams)

    # Get top centrality nodes in original
    top_original = orig_centrality.most_common(10)
    kernel_nodes = {'k', 'h', 'e'}

    print(f"\nOriginal top 10 centrality nodes:")
    for node, score in top_original:
        marker = " [KERNEL]" if node in kernel_nodes else ""
        print(f"  {node}: {score}{marker}")

    # Check kernel positions in original
    orig_ranks = {node: i+1 for i, (node, _) in enumerate(orig_centrality.most_common(50))}
    orig_kernel_ranks = {n: orig_ranks.get(n, 999) for n in kernel_nodes}
    print(f"\nOriginal kernel ranks: {orig_kernel_ranks}")

    # Generate surrogates and compute their centrality
    surrogate_kernel_ranks = []
    surrogate_top3_matches = 0

    for i in range(n_surrogates):
        surrogate = generate_frequency_matched_surrogate(words, len(words))
        surr_freq = compute_token_frequencies(surrogate)
        surr_bigrams = compute_bigram_frequencies(surrogate)
        surr_centrality = compute_centrality(surr_freq, surr_bigrams)

        # Get surrogate ranks
        surr_ranks = {node: j+1 for j, (node, _) in enumerate(surr_centrality.most_common(50))}
        surr_kernel = {n: surr_ranks.get(n, 999) for n in kernel_nodes}
        surrogate_kernel_ranks.append(surr_kernel)

        # Check if surrogate also has k,h,e in top 3
        surr_top3 = set(n for n, _ in surr_centrality.most_common(3))
        if kernel_nodes.issubset(surr_top3):
            surrogate_top3_matches += 1

    # Analyze results
    avg_ranks = {n: sum(r[n] for r in surrogate_kernel_ranks)/n_surrogates
                 for n in kernel_nodes}

    print(f"\nSurrogate analysis ({n_surrogates} runs):")
    print(f"  Average kernel ranks in surrogates: {avg_ranks}")
    print(f"  Surrogates with k,h,e all in top 3: {surrogate_top3_matches}/{n_surrogates}")

    # Statistical test
    k_rank_original = orig_kernel_ranks.get('k', 999)
    k_ranks_surrogate = [r.get('k', 999) for r in surrogate_kernel_ranks]
    k_percentile = sum(1 for r in k_ranks_surrogate if r <= k_rank_original) / n_surrogates

    result = {
        "attack": "KERNEL_COLLAPSE",
        "null_hypothesis": "Kernel nodes emerge from frequency alone",
        "original_kernel_ranks": orig_kernel_ranks,
        "surrogate_avg_ranks": avg_ranks,
        "surrogate_top3_match_rate": surrogate_top3_matches / n_surrogates,
        "k_percentile": k_percentile,
    }

    # Verdict
    if surrogate_top3_matches / n_surrogates > 0.8:
        result["verdict"] = "KERNEL_COLLAPSES"
        result["interpretation"] = "Kernel centrality IS a frequency artifact"
        print(f"\n>>> ATTACK SUCCESSFUL: Kernel centrality collapses to frequency artifact")
    elif surrogate_top3_matches / n_surrogates < 0.1:
        result["verdict"] = "KERNEL_SURVIVES"
        result["interpretation"] = "Kernel centrality is NOT explained by frequency alone"
        print(f"\n>>> ATTACK FAILED: Kernel structure survives (surrogates rarely reproduce)")
    else:
        result["verdict"] = "INCONCLUSIVE"
        result["interpretation"] = "Partial frequency explanation"
        print(f"\n>>> INCONCLUSIVE: Kernel partially explained by frequency")

    return result

# ============================================================================
# ATTACK 2: CYCLE ILLUSION TEST
# ============================================================================

def detect_cycles(sequence, max_len=10):
    """Detect dominant cycle length in a token sequence."""
    if len(sequence) < 4:
        return None, 0

    # Use autocorrelation to find cycle length
    best_period = None
    best_score = 0

    for period in range(2, min(max_len + 1, len(sequence) // 2)):
        matches = 0
        comparisons = 0
        for i in range(len(sequence) - period):
            if sequence[i] == sequence[i + period]:
                matches += 1
            comparisons += 1
        if comparisons > 0:
            score = matches / comparisons
            if score > best_score:
                best_score = score
                best_period = period

    return best_period, best_score

def compute_cycle_signature(words):
    """Compute cycle signature for a word sequence."""
    # Join words into character sequence
    chars = ''.join(words)
    period, score = detect_cycles(list(chars))
    return period, score

def attack2_cycle_illusion(words, folios):
    """
    Attack 2: Test if 2-cycle structure is a segmentation artifact.

    Null hypothesis: 2-cycle emerges from line-breaking or layout conventions.
    """
    print("\n" + "="*70)
    print("ATTACK 2: CYCLE ILLUSION TEST")
    print("="*70)

    results = []

    # Test 1: Original folio segmentation
    folio_cycles = []
    for folio, folio_words in folios.items():
        period, score = compute_cycle_signature(folio_words)
        folio_cycles.append(period)

    cycle_counts = Counter(folio_cycles)
    dominant_original = cycle_counts.most_common(1)[0] if cycle_counts else (None, 0)
    print(f"\nOriginal folio segmentation:")
    print(f"  Dominant cycle: {dominant_original[0]} (in {dominant_original[1]} folios)")
    print(f"  All cycle counts: {dict(cycle_counts)}")

    # Test 2: Random re-segmentation (scramble folio boundaries)
    all_words = list(words)
    random.shuffle(all_words)

    # Create random-sized chunks
    random_folios = {}
    i = 0
    chunk_id = 0
    while i < len(all_words):
        chunk_size = random.randint(50, 500)
        random_folios[f"random_{chunk_id}"] = all_words[i:i+chunk_size]
        i += chunk_size
        chunk_id += 1

    random_cycles = []
    for chunk_words in random_folios.values():
        period, score = compute_cycle_signature(chunk_words)
        random_cycles.append(period)

    random_counts = Counter(random_cycles)
    dominant_random = random_counts.most_common(1)[0] if random_counts else (None, 0)
    print(f"\nRandom re-segmentation:")
    print(f"  Dominant cycle: {dominant_random[0]} (in {dominant_random[1]} chunks)")
    print(f"  All cycle counts: {dict(random_counts)}")

    # Test 3: Fixed-size chunks (100 words each)
    fixed_folios = {}
    for i in range(0, len(all_words), 100):
        fixed_folios[f"fixed_{i//100}"] = all_words[i:i+100]

    fixed_cycles = []
    for chunk_words in fixed_folios.values():
        period, score = compute_cycle_signature(chunk_words)
        fixed_cycles.append(period)

    fixed_counts = Counter(fixed_cycles)
    dominant_fixed = fixed_counts.most_common(1)[0] if fixed_counts else (None, 0)
    print(f"\nFixed 100-word chunks:")
    print(f"  Dominant cycle: {dominant_fixed[0]} (in {dominant_fixed[1]} chunks)")
    print(f"  All cycle counts: {dict(fixed_counts)}")

    # Test 4: Line-level analysis (if 2-cycle is line-based artifact)
    # Simulate line structure by looking at short subsequences
    line_cycles = []
    for i in range(0, len(all_words), 10):
        chunk = all_words[i:i+10]
        if len(chunk) >= 4:
            period, score = compute_cycle_signature(chunk)
            line_cycles.append(period)

    line_counts = Counter(line_cycles)
    print(f"\n10-word line segments:")
    print(f"  All cycle counts: {dict(line_counts)}")

    result = {
        "attack": "CYCLE_ILLUSION",
        "null_hypothesis": "2-cycle is a segmentation artifact",
        "original_dominant": dominant_original,
        "random_segment_dominant": dominant_random,
        "fixed_segment_dominant": dominant_fixed,
        "line_segment_counts": dict(line_counts),
    }

    # Verdict
    if dominant_original[0] == dominant_random[0] == dominant_fixed[0]:
        result["verdict"] = "CYCLE_SURVIVES"
        result["interpretation"] = "2-cycle persists across all segmentations"
        print(f"\n>>> ATTACK FAILED: Cycle structure survives re-segmentation")
    else:
        result["verdict"] = "CYCLE_COLLAPSES"
        result["interpretation"] = "Cycle structure is segmentation-dependent"
        print(f"\n>>> ATTACK SUCCESSFUL: Cycle structure collapses under re-segmentation")

    return result

# ============================================================================
# ATTACK 3: GRAMMAR MINIMALITY TEST
# ============================================================================

def compute_legality_rate(words, forbidden_pairs):
    """Compute rate of forbidden transitions in word sequence."""
    violations = 0
    total = 0

    for word in words:
        for i in range(len(word) - 1):
            pair = (word[i], word[i+1])
            total += 1
            if pair in forbidden_pairs:
                violations += 1

    return (total - violations) / total if total > 0 else 1.0

def attack3_grammar_minimality(words, phase_data):
    """
    Attack 3: Test if grammar is overfit - can we simplify dramatically?

    Null hypothesis: A much simpler model preserves key metrics.
    """
    print("\n" + "="*70)
    print("ATTACK 3: GRAMMAR MINIMALITY TEST")
    print("="*70)

    # Get forbidden transitions from phase data
    topology = phase_data.get('topology', {})
    forbidden_raw = topology.get('internal_forbidden', {}).get('examples', [])
    forbidden_pairs = set(tuple(pair) for pair in forbidden_raw)

    print(f"\nOriginal model complexity:")
    print(f"  Instruction classes: 49")
    print(f"  Forbidden transitions: {len(forbidden_pairs)}")

    # Compute original legality
    original_legality = compute_legality_rate(words, forbidden_pairs)
    print(f"  Original legality rate: {original_legality:.4f}")

    # Test 1: Remove ALL forbidden transitions (trivial grammar)
    trivial_legality = compute_legality_rate(words, set())
    print(f"\nTrivial grammar (no constraints):")
    print(f"  Legality rate: {trivial_legality:.4f}")

    # Test 2: Keep only top 5 most frequent forbidden pairs
    pair_violations = Counter()
    for word in words:
        for i in range(len(word) - 1):
            pair = (word[i], word[i+1])
            if pair in forbidden_pairs:
                pair_violations[pair] += 1

    top5_forbidden = set(p for p, _ in pair_violations.most_common(5))
    reduced_legality = compute_legality_rate(words, top5_forbidden)
    print(f"\nReduced grammar (5 constraints):")
    print(f"  Legality rate: {reduced_legality:.4f}")

    # Test 3: Collapse instruction classes
    # Group all tokens by first character only
    equiv = phase_data.get('equivalence', {})
    original_classes = equiv.get('equivalence_classes_found', 49)

    # Simulate collapsed classes (by first char)
    first_char_classes = defaultdict(set)
    for word in words:
        if word:
            first_char_classes[word[0]].add(word)
    collapsed_classes = len(first_char_classes)

    print(f"\nCollapsed classification (by first char):")
    print(f"  Classes: {original_classes} -> {collapsed_classes}")

    # Test 4: Random 10-class assignment
    unique_words = set(words)
    random_classes = {w: random.randint(0, 9) for w in unique_words}
    print(f"\nRandom 10-class assignment:")
    print(f"  Classes: 10")

    result = {
        "attack": "GRAMMAR_MINIMALITY",
        "null_hypothesis": "Grammar is overfit and can be simplified",
        "original_classes": original_classes,
        "original_constraints": len(forbidden_pairs),
        "original_legality": original_legality,
        "trivial_legality": trivial_legality,
        "reduced_5_constraint_legality": reduced_legality,
        "collapsed_classes": collapsed_classes,
    }

    # Verdict
    legality_drop = original_legality - trivial_legality
    if legality_drop < 0.01:
        result["verdict"] = "GRAMMAR_OVERFIT"
        result["interpretation"] = "Constraints provide <1% legality improvement - overfit"
        print(f"\n>>> ATTACK SUCCESSFUL: Grammar is overfit (constraints barely matter)")
    else:
        result["verdict"] = "GRAMMAR_SURVIVES"
        result["interpretation"] = f"Constraints provide {legality_drop:.2%} legality improvement"
        print(f"\n>>> ATTACK FAILED: Constraints provide meaningful structure")

    return result

# ============================================================================
# ATTACK 4: RANDOM CONSTRAINT SYSTEM BASELINE
# ============================================================================

def generate_random_constraint_system(n_tokens=49, n_forbidden=17):
    """Generate a random constraint system with similar parameters."""
    tokens = list(range(n_tokens))

    # Generate random forbidden pairs
    forbidden = set()
    while len(forbidden) < n_forbidden:
        a, b = random.choice(tokens), random.choice(tokens)
        if a != b:
            forbidden.add((a, b))

    return tokens, forbidden

def simulate_random_execution(tokens, forbidden, n_steps=1000):
    """Simulate execution in random constraint system."""
    # Random walk respecting forbidden transitions
    current = random.choice(tokens)
    path = [current]
    allowed = {t: [t2 for t2 in tokens if (t, t2) not in forbidden and t != t2]
               for t in tokens}

    for _ in range(n_steps):
        if allowed[current]:
            current = random.choice(allowed[current])
            path.append(current)
        else:
            break

    return path

def detect_monostate(path, window=50):
    """Check if path converges to a single dominant state."""
    if len(path) < window:
        return False, None

    final_window = path[-window:]
    counts = Counter(final_window)
    dominant, count = counts.most_common(1)[0]

    return count / window > 0.5, dominant

def attack4_random_baseline(n_systems=100):
    """
    Attack 4: Test if constraint system behavior is generic.

    Null hypothesis: Random constraint systems show similar behavior.
    """
    print("\n" + "="*70)
    print("ATTACK 4: RANDOM CONSTRAINT SYSTEM BASELINE")
    print("="*70)

    monostate_count = 0
    cycle_counts = []

    for i in range(n_systems):
        tokens, forbidden = generate_random_constraint_system(49, 17)
        path = simulate_random_execution(tokens, forbidden, 1000)

        # Check for monostate
        is_mono, dominant = detect_monostate(path)
        if is_mono:
            monostate_count += 1

        # Check for cycles
        period, score = detect_cycles(path[-100:])
        if period:
            cycle_counts.append(period)

    cycle_dist = Counter(cycle_counts)

    print(f"\nRandom system analysis ({n_systems} systems):")
    print(f"  Monostate convergence rate: {monostate_count/n_systems:.2%}")
    print(f"  Dominant cycle in random: {cycle_dist.most_common(3)}")

    # Compare to Voynich model
    voynich_monostate_rate = 1.0  # From Phase 14
    voynich_dominant_cycle = 2    # From Phase 22B

    result = {
        "attack": "RANDOM_BASELINE",
        "null_hypothesis": "Random constraint systems show similar behavior",
        "n_systems": n_systems,
        "random_monostate_rate": monostate_count / n_systems,
        "voynich_monostate_rate": voynich_monostate_rate,
        "random_cycle_distribution": dict(cycle_dist),
        "voynich_dominant_cycle": voynich_dominant_cycle,
    }

    # Check if 2-cycle dominates in random systems
    cycle_2_rate = cycle_dist.get(2, 0) / len(cycle_counts) if cycle_counts else 0

    if monostate_count / n_systems > 0.9 and cycle_2_rate > 0.5:
        result["verdict"] = "BEHAVIOR_GENERIC"
        result["interpretation"] = "Random systems also show monostate + 2-cycle"
        print(f"\n>>> ATTACK SUCCESSFUL: Behavior is generic to constraint systems")
    else:
        result["verdict"] = "BEHAVIOR_SPECIFIC"
        result["interpretation"] = "Voynich behavior is specific, not generic"
        print(f"\n>>> ATTACK FAILED: Voynich behavior is NOT generic")

    return result

# ============================================================================
# ATTACK 5: INDEPENDENCE OF FOLIOS TEST
# ============================================================================

def compute_folio_signature(words):
    """Compute a feature signature for a folio."""
    if not words:
        return {}

    freq = Counter(''.join(words))
    total = sum(freq.values())

    return {
        'length': len(words),
        'char_count': total,
        'unique_chars': len(freq),
        'top_char': freq.most_common(1)[0][0] if freq else None,
        'k_ratio': freq.get('k', 0) / total if total else 0,
        'h_ratio': freq.get('h', 0) / total if total else 0,
        'e_ratio': freq.get('e', 0) / total if total else 0,
    }

def compute_mutual_information_approx(folios):
    """Approximate mutual information between folio pairs."""
    folio_names = list(folios.keys())
    n = len(folio_names)

    mi_scores = []
    for i in range(min(50, n)):  # Sample 50 pairs
        for j in range(i+1, min(50, n)):
            f1 = ''.join(folios[folio_names[i]])
            f2 = ''.join(folios[folio_names[j]])

            # Compute char overlap
            c1 = Counter(f1)
            c2 = Counter(f2)

            shared = set(c1.keys()) & set(c2.keys())
            if shared:
                overlap = sum(min(c1[c], c2[c]) for c in shared)
                mi_approx = overlap / (len(f1) + len(f2))
                mi_scores.append(mi_approx)

    return sum(mi_scores) / len(mi_scores) if mi_scores else 0

def test_length_coherence(folios):
    """Test if family coherence is explained by length alone."""
    signatures = []
    for folio, words in folios.items():
        sig = compute_folio_signature(words)
        signatures.append(sig)

    # Group by length quintile
    lengths = [s['length'] for s in signatures]
    if not lengths:
        return 0

    quintiles = sorted(lengths)[::len(lengths)//5 + 1]

    # Check if kernel ratios are uniform across length quintiles
    length_groups = defaultdict(list)
    for sig in signatures:
        for i, q in enumerate(quintiles):
            if sig['length'] <= q:
                length_groups[i].append(sig['k_ratio'])
                break

    # Compute variance across groups
    group_means = [sum(g)/len(g) if g else 0 for g in length_groups.values()]
    overall_mean = sum(group_means) / len(group_means) if group_means else 0
    variance = sum((m - overall_mean)**2 for m in group_means) / len(group_means) if group_means else 0

    return variance

def attack5_folio_independence(folios):
    """
    Attack 5: Test if folios are meaningfully distinct.

    Null hypothesis: Folios are redundant samples from one generator.
    """
    print("\n" + "="*70)
    print("ATTACK 5: INDEPENDENCE OF FOLIOS TEST")
    print("="*70)

    n_folios = len(folios)
    print(f"\nAnalyzing {n_folios} folios...")

    # Test 1: Mutual information between folios
    mi = compute_mutual_information_approx(folios)
    print(f"\nMutual information (approx): {mi:.4f}")

    # Test 2: Signature diversity
    signatures = [compute_folio_signature(words) for words in folios.values()]

    k_ratios = [s['k_ratio'] for s in signatures]
    h_ratios = [s['h_ratio'] for s in signatures]

    k_cv = (sum((r - sum(k_ratios)/len(k_ratios))**2 for r in k_ratios) / len(k_ratios))**0.5 / (sum(k_ratios)/len(k_ratios)) if k_ratios else 0
    h_cv = (sum((r - sum(h_ratios)/len(h_ratios))**2 for r in h_ratios) / len(h_ratios))**0.5 / (sum(h_ratios)/len(h_ratios)) if h_ratios else 0

    print(f"\nKernel ratio variation:")
    print(f"  k CV: {k_cv:.4f}")
    print(f"  h CV: {h_cv:.4f}")

    # Test 3: Length-coherence test
    length_variance = test_length_coherence(folios)
    print(f"\nLength-coherence variance: {length_variance:.6f}")

    # Test 4: Can we distinguish folios by a simple Markov model?
    # Build overall Markov chain
    all_words = []
    for words in folios.values():
        all_words.extend(words)

    overall_bigrams = compute_bigram_frequencies(all_words)

    # Compute per-folio deviation from overall
    deviations = []
    for folio, words in folios.items():
        folio_bigrams = compute_bigram_frequencies(words)

        # KL-divergence approximation
        deviation = 0
        for bigram, count in folio_bigrams.items():
            expected = overall_bigrams.get(bigram, 1)
            deviation += abs(count - expected * len(words) / len(all_words))
        deviations.append(deviation)

    mean_deviation = sum(deviations) / len(deviations)
    print(f"\nMean deviation from global Markov: {mean_deviation:.2f}")

    result = {
        "attack": "FOLIO_INDEPENDENCE",
        "null_hypothesis": "Folios are redundant samples from one generator",
        "n_folios": n_folios,
        "mutual_information": mi,
        "k_ratio_cv": k_cv,
        "h_ratio_cv": h_cv,
        "length_coherence_variance": length_variance,
        "mean_markov_deviation": mean_deviation,
    }

    # Verdict
    if mi > 0.3 and k_cv < 0.1 and mean_deviation < 50:
        result["verdict"] = "FOLIOS_REDUNDANT"
        result["interpretation"] = "Folios are statistically indistinguishable"
        print(f"\n>>> ATTACK SUCCESSFUL: Folios appear to be from same generator")
    else:
        result["verdict"] = "FOLIOS_DISTINCT"
        result["interpretation"] = "Folios show meaningful statistical variation"
        print(f"\n>>> ATTACK FAILED: Folios show meaningful distinctiveness")

    return result

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("="*70)
    print("ADVERSARIAL AUDIT - MODEL DESTRUCTION ATTEMPT")
    print("Phase X: Falsification-First Analysis")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print("\nObjective: Attempt to falsify the Voynich control system model")

    # Load data
    print("\nLoading data...")
    words, folios = load_transcription()
    phase_data = load_phase_data()
    print(f"  Loaded {len(words)} words across {len(folios)} folios")

    results = {}

    # Run all attacks
    results['attack1'] = attack1_kernel_collapse(words, n_surrogates=100)
    results['attack2'] = attack2_cycle_illusion(words, folios)
    results['attack3'] = attack3_grammar_minimality(words, phase_data)
    results['attack4'] = attack4_random_baseline(n_systems=100)
    results['attack5'] = attack5_folio_independence(folios)

    # Summary
    print("\n" + "="*70)
    print("ADVERSARIAL AUDIT SUMMARY")
    print("="*70)

    attacks_successful = 0
    attacks_failed = 0
    attacks_inconclusive = 0

    for name, result in results.items():
        verdict = result.get('verdict', 'UNKNOWN')
        if 'SURVIVES' in verdict or 'DISTINCT' in verdict or 'SPECIFIC' in verdict:
            attacks_failed += 1
            status = "MODEL SURVIVES"
        elif 'COLLAPSES' in verdict or 'OVERFIT' in verdict or 'GENERIC' in verdict or 'REDUNDANT' in verdict:
            attacks_successful += 1
            status = "MODEL WEAKENED"
        else:
            attacks_inconclusive += 1
            status = "INCONCLUSIVE"

        print(f"\n{name}: {verdict}")
        print(f"  Status: {status}")
        print(f"  Interpretation: {result.get('interpretation', 'N/A')}")

    print("\n" + "-"*70)
    print(f"FINAL TALLY:")
    print(f"  Attacks where model SURVIVES: {attacks_failed}/5")
    print(f"  Attacks where model WEAKENED: {attacks_successful}/5")
    print(f"  Inconclusive: {attacks_inconclusive}/5")

    if attacks_successful >= 3:
        overall_verdict = "MODEL_FALSIFIED"
        print(f"\n>>> OVERALL: MODEL IS FALSIFIED OR SEVERELY WEAKENED")
    elif attacks_failed >= 4:
        overall_verdict = "MODEL_ROBUST"
        print(f"\n>>> OVERALL: MODEL IS ROBUST - SURVIVES ADVERSARIAL TESTING")
    else:
        overall_verdict = "MODEL_PARTIAL"
        print(f"\n>>> OVERALL: MODEL HAS WEAKNESSES BUT IS NOT FALSIFIED")

    results['overall'] = {
        "verdict": overall_verdict,
        "attacks_survived": attacks_failed,
        "attacks_weakened_by": attacks_successful,
        "attacks_inconclusive": attacks_inconclusive,
    }

    # Save results
    with open('attack_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to attack_results.json")

    return results

if __name__ == "__main__":
    main()
