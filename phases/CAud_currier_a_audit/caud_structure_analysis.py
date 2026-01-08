"""
Phase CAud-S: Currier A Structure Analysis

Question: What IS Currier A? Can we derive its internal structure?

Competing Hypotheses:
H1: PREPARATION_LAYER - Material prep before machine process
H2: ALTERNATE_PRODUCTS - Different product line (moonshine, medicines, etc.)
H3: POST_PROCESSING - Steps after main process
H4: DEFINITIONAL - Names/definitions/index
H5: DIFFERENT_AUTHOR - Separate tradition with own grammar
H6: ANNOTATIONS - Notes/commentary on B

Tests:
1. Grammar derivation attempt (compression, transitions)
2. Section distribution (where is A concentrated?)
3. Vocabulary clustering (does A have internal families?)
4. Positional analysis (A before/after/interspersed with B?)
5. Morphological structure (same word-formation as B?)
6. Folio-level signatures (what makes A folios distinctive?)
"""

import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats as sp_stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

project_root = Path(__file__).parent.parent.parent


def load_data():
    """Load transcription data with Currier designation."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"') if len(parts) > 2 else ''
                section = parts[3].strip('"') if len(parts) > 3 else ''
                language = parts[6].strip('"') if len(parts) > 6 else ''

                if word and folio:
                    data.append({
                        'token': word.lower(),
                        'folio': folio,
                        'section': section,
                        'currier': language
                    })

    return data


def test_1_grammar_derivation(a_data):
    """Attempt to derive grammar from Currier A."""
    print("\n" + "=" * 70)
    print("TEST 1: GRAMMAR DERIVATION ATTEMPT")
    print("=" * 70)

    # Extract transitions
    transitions = Counter()
    tokens_by_folio = defaultdict(list)

    for d in a_data:
        tokens_by_folio[d['folio']].append(d['token'])

    for folio, tokens in tokens_by_folio.items():
        for i in range(len(tokens) - 1):
            transitions[(tokens[i], tokens[i+1])] += 1

    # Basic stats
    unique_tokens = set(d['token'] for d in a_data)
    total_tokens = len(a_data)
    unique_transitions = len(transitions)

    print(f"\nA corpus: {total_tokens} tokens, {len(unique_tokens)} unique types")
    print(f"Unique transitions: {unique_transitions}")

    # Type-token ratio (compression potential)
    ttr = len(unique_tokens) / total_tokens
    print(f"Type-token ratio: {ttr:.3f} (B was ~0.21, lower = more compressible)")

    # Transition concentration (do some transitions dominate?)
    trans_counts = list(transitions.values())
    top_10 = sum(sorted(trans_counts, reverse=True)[:10])
    top_10_pct = 100 * top_10 / sum(trans_counts)
    print(f"Top 10 transitions = {top_10_pct:.1f}% of all transitions")

    # Hapax legomena (tokens appearing once)
    token_counts = Counter(d['token'] for d in a_data)
    hapax = sum(1 for c in token_counts.values() if c == 1)
    hapax_pct = 100 * hapax / len(unique_tokens)
    print(f"Hapax legomena: {hapax} ({hapax_pct:.1f}% of vocabulary)")

    # Attempt clustering by co-occurrence
    print("\nAttempting token clustering by transition patterns...")

    # Build co-occurrence matrix for frequent tokens
    freq_tokens = [t for t, c in token_counts.most_common(100)]
    token_idx = {t: i for i, t in enumerate(freq_tokens)}

    cooc = np.zeros((len(freq_tokens), len(freq_tokens)))
    for (t1, t2), count in transitions.items():
        if t1 in token_idx and t2 in token_idx:
            cooc[token_idx[t1], token_idx[t2]] += count
            cooc[token_idx[t2], token_idx[t1]] += count

    # Normalize
    row_sums = cooc.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    cooc_norm = cooc / row_sums

    # Cluster
    if cooc_norm.sum() > 0:
        try:
            dist = pdist(cooc_norm, metric='cosine')
            dist = np.nan_to_num(dist, nan=1.0)
            Z = linkage(dist, method='ward')
            clusters = fcluster(Z, t=5, criterion='maxclust')

            cluster_sizes = Counter(clusters)
            print(f"Clustering into 5 groups: {dict(cluster_sizes)}")

            # Show sample from each cluster
            print("\nCluster samples:")
            for c in sorted(cluster_sizes.keys()):
                members = [freq_tokens[i] for i, cl in enumerate(clusters) if cl == c][:5]
                print(f"  Cluster {c}: {members}")
        except Exception as e:
            print(f"Clustering failed: {e}")

    # Verdict
    compression_possible = ttr < 0.25
    concentrated_transitions = top_10_pct > 20
    low_hapax = hapax_pct < 50

    print(f"\n--- Grammar Derivation Verdict ---")
    print(f"Compression potential (TTR < 0.25): {'YES' if compression_possible else 'NO'} ({ttr:.3f})")
    print(f"Concentrated transitions (>20%): {'YES' if concentrated_transitions else 'NO'} ({top_10_pct:.1f}%)")
    print(f"Low hapax rate (<50%): {'YES' if low_hapax else 'NO'} ({hapax_pct:.1f}%)")

    if compression_possible and concentrated_transitions:
        verdict = "GRAMMAR_POSSIBLE"
    elif compression_possible or concentrated_transitions:
        verdict = "PARTIAL_STRUCTURE"
    else:
        verdict = "NON_GRAMMATICAL"

    print(f"\nVerdict: {verdict}")

    return {
        'ttr': ttr,
        'top_10_pct': top_10_pct,
        'hapax_pct': hapax_pct,
        'verdict': verdict,
        'unique_tokens': len(unique_tokens),
        'unique_transitions': unique_transitions
    }


def test_2_section_distribution(data):
    """Where is Currier A concentrated?"""
    print("\n" + "=" * 70)
    print("TEST 2: SECTION DISTRIBUTION")
    print("=" * 70)

    section_currier = defaultdict(lambda: {'A': 0, 'B': 0, 'total': 0})

    for d in data:
        section = d['section'] or 'UNKNOWN'
        currier = d['currier']
        section_currier[section]['total'] += 1
        if currier == 'A':
            section_currier[section]['A'] += 1
        elif currier == 'B':
            section_currier[section]['B'] += 1

    print(f"\n{'Section':<12} {'Total':<10} {'A':<10} {'B':<10} {'A%':<10} {'Dominant'}")
    print("-" * 62)

    a_dominant = []
    b_dominant = []
    mixed = []

    for section in sorted(section_currier.keys()):
        stats = section_currier[section]
        a_pct = 100 * stats['A'] / stats['total'] if stats['total'] > 0 else 0
        dominant = 'A' if a_pct > 60 else ('B' if a_pct < 40 else 'MIXED')

        print(f"{section:<12} {stats['total']:<10} {stats['A']:<10} {stats['B']:<10} {a_pct:<10.1f} {dominant}")

        if dominant == 'A':
            a_dominant.append(section)
        elif dominant == 'B':
            b_dominant.append(section)
        else:
            mixed.append(section)

    print(f"\n--- Section Distribution Summary ---")
    print(f"A-dominant sections: {a_dominant}")
    print(f"B-dominant sections: {b_dominant}")
    print(f"Mixed sections: {mixed}")

    # Interpretation
    if len(a_dominant) > 0 and len(b_dominant) > 0:
        interpretation = "SECTIONALLY_SEGREGATED"
    elif len(mixed) > len(a_dominant) + len(b_dominant):
        interpretation = "INTERSPERSED"
    else:
        interpretation = "PARTIALLY_SEGREGATED"

    print(f"\nDistribution pattern: {interpretation}")

    return {
        'a_dominant': a_dominant,
        'b_dominant': b_dominant,
        'mixed': mixed,
        'interpretation': interpretation
    }


def test_3_vocabulary_clustering(a_data):
    """Does A vocabulary cluster into internal families?"""
    print("\n" + "=" * 70)
    print("TEST 3: VOCABULARY CLUSTERING (Internal A Families)")
    print("=" * 70)

    # Group by section
    section_vocab = defaultdict(set)
    section_tokens = defaultdict(list)

    for d in a_data:
        section = d['section'] or 'UNKNOWN'
        section_vocab[section].add(d['token'])
        section_tokens[section].append(d['token'])

    sections = sorted(section_vocab.keys())

    print(f"\nA vocabulary by section:")
    print(f"{'Section':<12} {'Tokens':<10} {'Unique':<10} {'Diversity'}")
    print("-" * 45)

    for section in sections:
        total = len(section_tokens[section])
        unique = len(section_vocab[section])
        diversity = unique / total if total > 0 else 0
        print(f"{section:<12} {total:<10} {unique:<10} {diversity:.3f}")

    # Section exclusivity (do sections have their own vocabulary?)
    all_tokens = set()
    for v in section_vocab.values():
        all_tokens.update(v)

    exclusive_counts = {}
    for section in sections:
        other_sections = set()
        for s, v in section_vocab.items():
            if s != section:
                other_sections.update(v)
        exclusive = section_vocab[section] - other_sections
        exclusive_counts[section] = len(exclusive)

    print(f"\nSection-exclusive A vocabulary:")
    total_exclusive = 0
    for section in sections:
        if len(section_vocab[section]) > 0:
            excl_pct = 100 * exclusive_counts[section] / len(section_vocab[section])
            print(f"  {section}: {exclusive_counts[section]} exclusive ({excl_pct:.1f}%)")
            total_exclusive += exclusive_counts[section]

    overall_exclusivity = 100 * total_exclusive / len(all_tokens) if all_tokens else 0
    print(f"\nOverall A section exclusivity: {overall_exclusivity:.1f}%")

    # Cross-section overlap
    print(f"\nCross-section vocabulary overlap (Jaccard):")
    if len(sections) >= 2:
        overlaps = []
        for i, s1 in enumerate(sections):
            for s2 in sections[i+1:]:
                if section_vocab[s1] and section_vocab[s2]:
                    intersection = len(section_vocab[s1] & section_vocab[s2])
                    union = len(section_vocab[s1] | section_vocab[s2])
                    jaccard = intersection / union if union > 0 else 0
                    overlaps.append(jaccard)
                    if jaccard > 0.1:
                        print(f"  {s1} <-> {s2}: {jaccard:.3f}")

        mean_overlap = np.mean(overlaps) if overlaps else 0
        print(f"\nMean cross-section Jaccard: {mean_overlap:.3f}")

    return {
        'overall_exclusivity': overall_exclusivity,
        'section_exclusive_counts': exclusive_counts
    }


def test_4_positional_analysis(data):
    """Is A before, after, or interspersed with B?"""
    print("\n" + "=" * 70)
    print("TEST 4: POSITIONAL ANALYSIS (A vs B Ordering)")
    print("=" * 70)

    # Get folio order
    folio_currier = {}
    folio_order = []
    seen = set()

    for d in data:
        folio = d['folio']
        if folio not in seen:
            folio_order.append(folio)
            seen.add(folio)
        if d['currier'] in ['A', 'B']:
            folio_currier[folio] = d['currier']

    # Analyze sequence
    a_positions = []
    b_positions = []

    for i, folio in enumerate(folio_order):
        if folio in folio_currier:
            if folio_currier[folio] == 'A':
                a_positions.append(i)
            else:
                b_positions.append(i)

    print(f"\nFolio positions:")
    print(f"  A folios: {len(a_positions)} (positions {min(a_positions) if a_positions else 'N/A'} to {max(a_positions) if a_positions else 'N/A'})")
    print(f"  B folios: {len(b_positions)} (positions {min(b_positions) if b_positions else 'N/A'} to {max(b_positions) if b_positions else 'N/A'})")

    if a_positions and b_positions:
        a_mean = np.mean(a_positions)
        b_mean = np.mean(b_positions)
        print(f"\nMean position: A={a_mean:.1f}, B={b_mean:.1f}")

        if a_mean < b_mean - 10:
            ordering = "A_BEFORE_B"
        elif b_mean < a_mean - 10:
            ordering = "B_BEFORE_A"
        else:
            ordering = "INTERSPERSED"

        print(f"Ordering pattern: {ordering}")

        # Check for runs
        sequence = [folio_currier.get(f, '?') for f in folio_order]
        runs = []
        current_run = sequence[0] if sequence else ''
        run_length = 1

        for c in sequence[1:]:
            if c == current_run:
                run_length += 1
            else:
                if current_run in ['A', 'B']:
                    runs.append((current_run, run_length))
                current_run = c
                run_length = 1
        if current_run in ['A', 'B']:
            runs.append((current_run, run_length))

        a_runs = [r[1] for r in runs if r[0] == 'A']
        b_runs = [r[1] for r in runs if r[0] == 'B']

        print(f"\nRun analysis:")
        print(f"  A runs: {len(a_runs)}, mean length: {np.mean(a_runs):.1f}" if a_runs else "  A runs: 0")
        print(f"  B runs: {len(b_runs)}, mean length: {np.mean(b_runs):.1f}" if b_runs else "  B runs: 0")

        # Transitions between A and B
        ab_transitions = sum(1 for i in range(len(sequence)-1)
                           if sequence[i] == 'A' and sequence[i+1] == 'B')
        ba_transitions = sum(1 for i in range(len(sequence)-1)
                           if sequence[i] == 'B' and sequence[i+1] == 'A')

        print(f"\nA->B transitions: {ab_transitions}")
        print(f"B->A transitions: {ba_transitions}")
    else:
        ordering = "INSUFFICIENT_DATA"

    return {
        'a_positions': a_positions,
        'b_positions': b_positions,
        'ordering': ordering if 'ordering' in dir() else 'UNKNOWN'
    }


def test_5_morphological_structure(a_data, b_data):
    """Does A use same word-formation patterns as B?"""
    print("\n" + "=" * 70)
    print("TEST 5: MORPHOLOGICAL STRUCTURE (A vs B Word Formation)")
    print("=" * 70)

    def extract_morphology(tokens):
        prefixes = Counter()
        suffixes = Counter()
        for t in tokens:
            if len(t) >= 2:
                prefixes[t[:2]] += 1
                suffixes[t[-2:]] += 1
            if len(t) >= 3:
                prefixes[t[:3]] += 1
                suffixes[t[-3:]] += 1
        return prefixes, suffixes

    a_tokens = [d['token'] for d in a_data]
    b_tokens = [d['token'] for d in b_data]

    a_pref, a_suff = extract_morphology(a_tokens)
    b_pref, b_suff = extract_morphology(b_tokens)

    # Compare top morphemes
    print("\nTop 10 prefixes:")
    print(f"{'A Prefix':<15} {'A Count':<10} {'B Prefix':<15} {'B Count':<10}")
    print("-" * 50)
    a_top_pref = a_pref.most_common(10)
    b_top_pref = b_pref.most_common(10)
    for i in range(10):
        a_p = a_top_pref[i] if i < len(a_top_pref) else ('', 0)
        b_p = b_top_pref[i] if i < len(b_top_pref) else ('', 0)
        print(f"{a_p[0]:<15} {a_p[1]:<10} {b_p[0]:<15} {b_p[1]:<10}")

    print("\nTop 10 suffixes:")
    print(f"{'A Suffix':<15} {'A Count':<10} {'B Suffix':<15} {'B Count':<10}")
    print("-" * 50)
    a_top_suff = a_suff.most_common(10)
    b_top_suff = b_suff.most_common(10)
    for i in range(10):
        a_s = a_top_suff[i] if i < len(a_top_suff) else ('', 0)
        b_s = b_top_suff[i] if i < len(b_top_suff) else ('', 0)
        print(f"{a_s[0]:<15} {a_s[1]:<10} {b_s[0]:<15} {b_s[1]:<10}")

    # Overlap analysis
    a_pref_set = set(p for p, c in a_pref.most_common(50))
    b_pref_set = set(p for p, c in b_pref.most_common(50))
    pref_overlap = len(a_pref_set & b_pref_set) / len(a_pref_set | b_pref_set)

    a_suff_set = set(s for s, c in a_suff.most_common(50))
    b_suff_set = set(s for s, c in b_suff.most_common(50))
    suff_overlap = len(a_suff_set & b_suff_set) / len(a_suff_set | b_suff_set)

    print(f"\nTop-50 morpheme overlap:")
    print(f"  Prefix Jaccard: {pref_overlap:.3f}")
    print(f"  Suffix Jaccard: {suff_overlap:.3f}")

    # A-exclusive morphemes
    a_only_pref = a_pref_set - b_pref_set
    a_only_suff = a_suff_set - b_suff_set
    print(f"\nA-exclusive morphemes (in A top-50, not in B top-50):")
    print(f"  Prefixes ({len(a_only_pref)}): {sorted(a_only_pref)[:10]}")
    print(f"  Suffixes ({len(a_only_suff)}): {sorted(a_only_suff)[:10]}")

    if pref_overlap > 0.6 and suff_overlap > 0.6:
        morphology_verdict = "SIMILAR_MORPHOLOGY"
    elif pref_overlap < 0.3 and suff_overlap < 0.3:
        morphology_verdict = "DIFFERENT_MORPHOLOGY"
    else:
        morphology_verdict = "PARTIAL_OVERLAP"

    print(f"\nMorphology verdict: {morphology_verdict}")

    return {
        'pref_overlap': pref_overlap,
        'suff_overlap': suff_overlap,
        'verdict': morphology_verdict
    }


def test_6_hypothesis_discrimination(results):
    """Score each hypothesis against findings."""
    print("\n" + "=" * 70)
    print("TEST 6: HYPOTHESIS DISCRIMINATION")
    print("=" * 70)

    hypotheses = {
        'H1_PREPARATION': {
            'description': 'Material prep before machine process',
            'predictions': {
                'section_segregated': True,
                'a_before_b': True,
                'different_morphology': True,
                'non_grammatical': True,
                'high_exclusivity': True
            }
        },
        'H2_ALTERNATE_PRODUCTS': {
            'description': 'Different product line (moonshine, medicines)',
            'predictions': {
                'section_segregated': True,
                'a_before_b': False,  # Could be anywhere
                'different_morphology': True,
                'non_grammatical': False,  # Might have own grammar
                'high_exclusivity': True
            }
        },
        'H3_POST_PROCESSING': {
            'description': 'Steps after main process',
            'predictions': {
                'section_segregated': True,
                'a_before_b': False,  # A should be AFTER B
                'different_morphology': True,
                'non_grammatical': True,
                'high_exclusivity': True
            }
        },
        'H4_DEFINITIONAL': {
            'description': 'Names/definitions/index',
            'predictions': {
                'section_segregated': False,  # Scattered throughout
                'a_before_b': False,
                'different_morphology': True,
                'non_grammatical': True,
                'high_exclusivity': False  # Same terms defined everywhere
            }
        },
        'H5_DIFFERENT_AUTHOR': {
            'description': 'Separate tradition with own grammar',
            'predictions': {
                'section_segregated': True,
                'a_before_b': False,
                'different_morphology': True,
                'non_grammatical': False,  # Has own grammar
                'high_exclusivity': True
            }
        },
        'H6_ANNOTATIONS': {
            'description': 'Notes/commentary on B',
            'predictions': {
                'section_segregated': False,  # Mixed with B
                'a_before_b': False,
                'different_morphology': False,  # Similar to B
                'non_grammatical': True,
                'high_exclusivity': False
            }
        }
    }

    # Extract observations from results
    observations = {
        'section_segregated': results.get('section', {}).get('interpretation') == 'SECTIONALLY_SEGREGATED',
        'a_before_b': results.get('position', {}).get('ordering') == 'A_BEFORE_B',
        'different_morphology': results.get('morphology', {}).get('verdict') in ['DIFFERENT_MORPHOLOGY', 'PARTIAL_OVERLAP'],
        'non_grammatical': results.get('grammar', {}).get('verdict') == 'NON_GRAMMATICAL',
        'high_exclusivity': results.get('vocabulary', {}).get('overall_exclusivity', 0) > 50
    }

    print("\nObservations from tests:")
    for obs, value in observations.items():
        print(f"  {obs}: {value}")

    print("\n" + "-" * 70)
    print("Hypothesis Scores:")
    print("-" * 70)

    scores = {}
    for h_id, h_data in hypotheses.items():
        matches = 0
        total = 0
        for pred, expected in h_data['predictions'].items():
            if pred in observations:
                total += 1
                if observations[pred] == expected:
                    matches += 1

        score = matches / total if total > 0 else 0
        scores[h_id] = score

        print(f"\n{h_id}: {h_data['description']}")
        print(f"  Score: {matches}/{total} = {score:.1%}")
        for pred, expected in h_data['predictions'].items():
            actual = observations.get(pred, 'N/A')
            match = 'Y' if actual == expected else 'N'
            print(f"    {match} {pred}: expected {expected}, got {actual}")

    # Rank hypotheses
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    print("\n" + "=" * 70)
    print("HYPOTHESIS RANKING")
    print("=" * 70)
    for rank, (h_id, score) in enumerate(ranked, 1):
        print(f"  {rank}. {h_id}: {score:.1%}")

    best = ranked[0]
    if best[1] >= 0.8:
        confidence = "HIGH"
    elif best[1] >= 0.6:
        confidence = "MODERATE"
    else:
        confidence = "LOW"

    print(f"\nBest fit: {best[0]} ({best[1]:.1%} match, {confidence} confidence)")

    return {
        'scores': scores,
        'ranked': ranked,
        'best': best[0],
        'confidence': confidence
    }


def main():
    print("=" * 70)
    print("PHASE CAud-S: CURRIER A STRUCTURE ANALYSIS")
    print("=" * 70)
    print("\nQuestion: What IS Currier A?")
    print("Testing 6 competing hypotheses...\n")

    # Load data
    data = load_data()
    a_data = [d for d in data if d['currier'] == 'A']
    b_data = [d for d in data if d['currier'] == 'B']

    print(f"Loaded: {len(a_data)} A tokens, {len(b_data)} B tokens")

    results = {}

    # Run all tests
    results['grammar'] = test_1_grammar_derivation(a_data)
    results['section'] = test_2_section_distribution(data)
    results['vocabulary'] = test_3_vocabulary_clustering(a_data)
    results['position'] = test_4_positional_analysis(data)
    results['morphology'] = test_5_morphological_structure(a_data, b_data)
    results['hypotheses'] = test_6_hypothesis_discrimination(results)

    # Final synthesis
    print("\n" + "=" * 70)
    print("FINAL SYNTHESIS")
    print("=" * 70)

    print(f"""
Key Findings:
1. Grammar: {results['grammar']['verdict']}
   - TTR: {results['grammar']['ttr']:.3f} (B ~0.21)
   - Hapax: {results['grammar']['hapax_pct']:.1f}%

2. Section Distribution: {results['section']['interpretation']}
   - A-dominant: {results['section']['a_dominant']}
   - B-dominant: {results['section']['b_dominant']}

3. Vocabulary: {results['vocabulary']['overall_exclusivity']:.1f}% section-exclusive

4. Position: {results['position']['ordering']}

5. Morphology: {results['morphology']['verdict']}
   - Prefix overlap: {results['morphology']['pref_overlap']:.3f}
   - Suffix overlap: {results['morphology']['suff_overlap']:.3f}

Best Hypothesis: {results['hypotheses']['best']} ({results['hypotheses']['confidence']} confidence)
""")

    # Save results
    output_path = Path(__file__).parent / 'caud_structure_results.json'
    with open(output_path, 'w') as f:
        # Convert non-serializable items
        save_results = {}
        for k, v in results.items():
            if isinstance(v, dict):
                save_results[k] = {
                    kk: (list(vv) if isinstance(vv, (set, tuple)) else vv)
                    for kk, vv in v.items()
                }
            else:
                save_results[k] = v
        json.dump(save_results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
