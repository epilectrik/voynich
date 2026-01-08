"""
Probe: Is there entry-level A→B correspondence?

Testing whether B programs reference SPECIFIC A entries/folios,
or just share the type system generically.

Tight coupling would show:
1. B folios have vocabulary concentrated in specific A folios
2. Similar B programs reference similar A subsets
3. A sections predict B program types
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, chi2_contingency
from itertools import combinations

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

def load_data():
    """Load A and B data separately."""
    a_data = defaultdict(lambda: {'tokens': [], 'sections': set()})
    b_data = defaultdict(lambda: {'tokens': [], 'sections': set()})

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            folio = row['folio']
            section = row.get('section', '')
            lang = row.get('language', '')

            if lang == 'A':
                a_data[folio]['tokens'].append(token)
                a_data[folio]['sections'].add(section)
            elif lang == 'B':
                b_data[folio]['tokens'].append(token)
                b_data[folio]['sections'].add(section)

    return dict(a_data), dict(b_data)

def test_vocabulary_concentration(a_data, b_data):
    """Test 1: Is B's A-vocabulary concentrated or dispersed?"""
    print("="*70)
    print("TEST 1: A-VOCABULARY CONCENTRATION IN B")
    print("="*70)

    # Build A vocabulary index: which folios have which tokens
    a_token_to_folios = defaultdict(set)
    for folio, data in a_data.items():
        for token in set(data['tokens']):
            a_token_to_folios[token].add(folio)

    # For each B folio, find how concentrated its A-references are
    concentration_scores = []

    for b_folio, b_info in b_data.items():
        b_vocab = set(b_info['tokens'])

        # Find which A folios share vocabulary
        a_folio_hits = Counter()
        shared_tokens = 0
        for token in b_vocab:
            if token in a_token_to_folios:
                shared_tokens += 1
                for a_folio in a_token_to_folios[token]:
                    a_folio_hits[a_folio] += 1

        if not a_folio_hits:
            continue

        # Concentration = how much of shared vocab comes from top N folios
        total_hits = sum(a_folio_hits.values())
        top_5_hits = sum(c for _, c in a_folio_hits.most_common(5))
        top_10_hits = sum(c for _, c in a_folio_hits.most_common(10))

        concentration_5 = top_5_hits / total_hits if total_hits > 0 else 0
        concentration_10 = top_10_hits / total_hits if total_hits > 0 else 0

        concentration_scores.append({
            'b_folio': b_folio,
            'shared_tokens': shared_tokens,
            'a_folios_referenced': len(a_folio_hits),
            'conc_5': concentration_5,
            'conc_10': concentration_10,
            'top_a_folio': a_folio_hits.most_common(1)[0] if a_folio_hits else None
        })

    # Summary statistics
    conc_5_vals = [s['conc_5'] for s in concentration_scores]
    conc_10_vals = [s['conc_10'] for s in concentration_scores]
    a_folios_vals = [s['a_folios_referenced'] for s in concentration_scores]

    print(f"\nAnalyzed {len(concentration_scores)} B folios")
    print(f"\nA-folios referenced per B folio: mean={np.mean(a_folios_vals):.1f}, std={np.std(a_folios_vals):.1f}")
    print(f"Top-5 A-folio concentration: mean={np.mean(conc_5_vals):.1%}, std={np.std(conc_5_vals):.1%}")
    print(f"Top-10 A-folio concentration: mean={np.mean(conc_10_vals):.1%}, std={np.std(conc_10_vals):.1%}")

    # Expected if uniform
    n_a_folios = len(a_data)
    expected_5 = min(5 / n_a_folios, 1.0)
    expected_10 = min(10 / n_a_folios, 1.0)

    print(f"\nExpected if uniform (random): top-5={expected_5:.1%}, top-10={expected_10:.1%}")
    print(f"Observed/Expected ratio: top-5={np.mean(conc_5_vals)/expected_5:.2f}x, top-10={np.mean(conc_10_vals)/expected_10:.2f}x")

    if np.mean(conc_5_vals) > expected_5 * 2:
        print("\n-> CONCENTRATED: B folios reference specific A folios (>2x expected)")
    else:
        print("\n-> DISPERSED: B folios reference A vocabulary broadly")

    return concentration_scores

def test_b_folio_clustering(a_data, b_data):
    """Test 2: Do similar B programs reference similar A folios?"""
    print("\n" + "="*70)
    print("TEST 2: B-FOLIO CLUSTERING BY A-REFERENCE")
    print("="*70)

    # Build A-reference profile for each B folio
    a_token_to_folios = defaultdict(set)
    for folio, data in a_data.items():
        for token in set(data['tokens']):
            a_token_to_folios[token].add(folio)

    b_profiles = {}
    for b_folio, b_info in b_data.items():
        b_vocab = set(b_info['tokens'])

        # Profile = which A folios are referenced
        a_folio_hits = Counter()
        for token in b_vocab:
            if token in a_token_to_folios:
                for a_folio in a_token_to_folios[token]:
                    a_folio_hits[a_folio] += 1

        if a_folio_hits:
            b_profiles[b_folio] = a_folio_hits

    # Compute pairwise similarity between B folios based on A-reference
    def jaccard_a_ref(p1, p2):
        """Jaccard similarity of A-reference profiles."""
        keys1 = set(p1.keys())
        keys2 = set(p2.keys())
        intersection = len(keys1 & keys2)
        union = len(keys1 | keys2)
        return intersection / union if union > 0 else 0

    # Sample pairs for analysis
    b_folios = list(b_profiles.keys())

    # Adjacent vs non-adjacent in manuscript order
    adjacent_sims = []
    nonadjacent_sims = []

    for i in range(len(b_folios) - 1):
        sim = jaccard_a_ref(b_profiles[b_folios[i]], b_profiles[b_folios[i+1]])
        adjacent_sims.append(sim)

    for i, j in combinations(range(len(b_folios)), 2):
        if abs(i - j) > 1:
            sim = jaccard_a_ref(b_profiles[b_folios[i]], b_profiles[b_folios[j]])
            nonadjacent_sims.append(sim)

    print(f"\nA-reference similarity (Jaccard):")
    print(f"  Adjacent B folios: {np.mean(adjacent_sims):.3f}")
    print(f"  Non-adjacent B folios: {np.mean(nonadjacent_sims):.3f}")
    print(f"  Ratio: {np.mean(adjacent_sims)/np.mean(nonadjacent_sims):.2f}x")

    if np.mean(adjacent_sims) > np.mean(nonadjacent_sims) * 1.2:
        print("\n-> CLUSTERED: Adjacent B programs reference similar A entries")
    else:
        print("\n-> NO CLUSTERING: A-reference is not spatially organized")

    return b_profiles

def test_section_specificity(a_data, b_data):
    """Test 3: Do A sections predict B program characteristics?"""
    print("\n" + "="*70)
    print("TEST 3: A-SECTION -> B-PROGRAM MAPPING")
    print("="*70)

    # Build A vocabulary by section
    a_section_vocab = defaultdict(set)
    for folio, data in a_data.items():
        for section in data['sections']:
            a_section_vocab[section].update(data['tokens'])

    print(f"\nA sections found: {sorted(a_section_vocab.keys())}")
    print(f"Vocabulary sizes: {', '.join(f'{s}={len(v)}' for s, v in sorted(a_section_vocab.items()))}")

    # For each B folio, compute which A section contributes most vocabulary
    b_section_profile = {}
    for b_folio, b_info in b_data.items():
        b_vocab = set(b_info['tokens'])

        section_overlaps = {}
        for section, a_vocab in a_section_vocab.items():
            overlap = len(b_vocab & a_vocab)
            section_overlaps[section] = overlap

        if sum(section_overlaps.values()) > 0:
            b_section_profile[b_folio] = section_overlaps

    # Aggregate: which A section dominates B overall?
    section_totals = Counter()
    for profile in b_section_profile.values():
        for section, count in profile.items():
            section_totals[section] += count

    total = sum(section_totals.values())
    print(f"\nA-section contribution to B vocabulary:")
    for section, count in section_totals.most_common():
        pct = count / total * 100 if total > 0 else 0
        print(f"  Section {section}: {count:,} ({pct:.1f}%)")

    # Test: Does dominant A-section vary by B folio?
    dominant_sections = Counter()
    for b_folio, profile in b_section_profile.items():
        dominant = max(profile.items(), key=lambda x: x[1])[0]
        dominant_sections[dominant] += 1

    print(f"\nDominant A-section per B folio:")
    for section, count in dominant_sections.most_common():
        print(f"  Section {section}: {count} B folios ({count/len(b_section_profile)*100:.1f}%)")

    return b_section_profile

def test_prefix_type_concordance(a_data, b_data):
    """Test 4: Do same-prefix tokens cluster across A-B?"""
    print("\n" + "="*70)
    print("TEST 4: PREFIX-TYPE CONCORDANCE")
    print("="*70)

    PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ol', 'al', 'sa', 'ct']

    def get_prefix(token):
        for p in sorted(PREFIXES, key=len, reverse=True):
            if token.startswith(p):
                return p
        return None

    # Build A vocabulary by prefix
    a_prefix_vocab = defaultdict(set)
    for folio, data in a_data.items():
        for token in data['tokens']:
            prefix = get_prefix(token)
            if prefix:
                a_prefix_vocab[prefix].add(token)

    # For each B folio, compute prefix distribution of A-referenced tokens
    prefix_concordance = []

    for b_folio, b_info in b_data.items():
        b_tokens = b_info['tokens']

        # B's prefix distribution
        b_prefix_counts = Counter(get_prefix(t) for t in b_tokens)
        b_prefix_counts = {k: v for k, v in b_prefix_counts.items() if k}

        # Which B tokens are also in A?
        a_all_vocab = set()
        for folio, data in a_data.items():
            a_all_vocab.update(data['tokens'])

        shared_tokens = [t for t in b_tokens if t in a_all_vocab]
        shared_prefix_counts = Counter(get_prefix(t) for t in shared_tokens)
        shared_prefix_counts = {k: v for k, v in shared_prefix_counts.items() if k}

        # Compare: does B's prefix usage predict A-shared prefix usage?
        if b_prefix_counts and shared_prefix_counts:
            b_total = sum(b_prefix_counts.values())
            shared_total = sum(shared_prefix_counts.values())

            b_dist = {p: b_prefix_counts.get(p, 0) / b_total for p in PREFIXES}
            shared_dist = {p: shared_prefix_counts.get(p, 0) / shared_total for p in PREFIXES}

            # Correlation between B usage and A-shared usage
            b_vec = [b_dist[p] for p in PREFIXES]
            shared_vec = [shared_dist[p] for p in PREFIXES]

            if sum(b_vec) > 0 and sum(shared_vec) > 0:
                rho, p = spearmanr(b_vec, shared_vec)
                prefix_concordance.append({'folio': b_folio, 'rho': rho, 'p': p})

    if prefix_concordance:
        rhos = [x['rho'] for x in prefix_concordance]
        print(f"\nPrefix concordance (B usage vs A-shared usage):")
        print(f"  Mean rho: {np.mean(rhos):.3f}")
        print(f"  Median rho: {np.median(rhos):.3f}")
        print(f"  Range: [{min(rhos):.3f}, {max(rhos):.3f}]")

        sig_count = sum(1 for x in prefix_concordance if x['p'] < 0.05)
        print(f"  Significant (p<0.05): {sig_count}/{len(prefix_concordance)} ({sig_count/len(prefix_concordance)*100:.1f}%)")

        if np.mean(rhos) > 0.5:
            print("\n-> STRONG CONCORDANCE: B's prefix usage predicts A-shared vocabulary")
        elif np.mean(rhos) > 0.3:
            print("\n-> MODERATE CONCORDANCE: Some prefix-type coupling")
        else:
            print("\n-> WEAK CONCORDANCE: Prefix types don't strongly predict A-reference")

def test_token_specificity(a_data, b_data):
    """Test 5: Are specific tokens A-exclusive, B-exclusive, or shared?"""
    print("\n" + "="*70)
    print("TEST 5: TOKEN SPECIFICITY ANALYSIS")
    print("="*70)

    # Build vocabulary sets
    a_vocab = set()
    for data in a_data.values():
        a_vocab.update(data['tokens'])

    b_vocab = set()
    for data in b_data.values():
        b_vocab.update(data['tokens'])

    a_only = a_vocab - b_vocab
    b_only = b_vocab - a_vocab
    shared = a_vocab & b_vocab

    print(f"\nVocabulary breakdown:")
    print(f"  A-only: {len(a_only):,} types")
    print(f"  B-only: {len(b_only):,} types")
    print(f"  Shared: {len(shared):,} types")
    print(f"  Share rate: {len(shared)/len(a_vocab | b_vocab)*100:.1f}%")

    # Token frequency analysis
    a_token_freq = Counter()
    for data in a_data.values():
        a_token_freq.update(data['tokens'])

    b_token_freq = Counter()
    for data in b_data.values():
        b_token_freq.update(data['tokens'])

    # High-frequency shared tokens
    print(f"\nTop 15 shared tokens (by combined frequency):")
    shared_combined = {t: a_token_freq[t] + b_token_freq[t] for t in shared}
    print(f"{'Token':<15} {'A freq':>8} {'B freq':>8} {'A%':>8} {'B%':>8}")
    print("-" * 50)
    for token, _ in sorted(shared_combined.items(), key=lambda x: -x[1])[:15]:
        a_f = a_token_freq[token]
        b_f = b_token_freq[token]
        a_pct = a_f / sum(a_token_freq.values()) * 100
        b_pct = b_f / sum(b_token_freq.values()) * 100
        print(f"{token:<15} {a_f:>8} {b_f:>8} {a_pct:>7.2f}% {b_pct:>7.2f}%")

    # Do shared tokens have similar frequency ranks?
    shared_list = list(shared)
    a_ranks = {t: i for i, (t, _) in enumerate(a_token_freq.most_common())}
    b_ranks = {t: i for i, (t, _) in enumerate(b_token_freq.most_common())}

    shared_a_ranks = [a_ranks.get(t, len(a_ranks)) for t in shared_list]
    shared_b_ranks = [b_ranks.get(t, len(b_ranks)) for t in shared_list]

    rho, p = spearmanr(shared_a_ranks, shared_b_ranks)
    print(f"\nFrequency rank correlation (shared tokens): rho={rho:.3f}, p={p:.2e}")

    if rho > 0.5:
        print("-> STRONG: High-frequency A tokens are also high-frequency B tokens")
    elif rho > 0.3:
        print("-> MODERATE: Some frequency coupling")
    else:
        print("-> WEAK: Token frequency is system-specific")

def main():
    print("="*70)
    print("A->B ENTRY-LEVEL CORRESPONDENCE PROBE")
    print("="*70)

    a_data, b_data = load_data()
    print(f"\nLoaded: {len(a_data)} A folios, {len(b_data)} B folios")

    # Run tests
    test_vocabulary_concentration(a_data, b_data)
    test_b_folio_clustering(a_data, b_data)
    test_section_specificity(a_data, b_data)
    test_prefix_type_concordance(a_data, b_data)
    test_token_specificity(a_data, b_data)

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
    If ENTRY-LEVEL coupling exists:
    - B vocabulary concentrated in specific A folios (Test 1)
    - Adjacent B folios reference similar A entries (Test 2)
    - A sections predict B program characteristics (Test 3)
    - Prefix types concordant across systems (Test 4)
    - Shared tokens have correlated frequencies (Test 5)

    If only TYPE-SYSTEM coupling:
    - B vocabulary dispersed across all A folios
    - No spatial clustering of A-references
    - Generic vocabulary sharing without specificity
    """)

if __name__ == '__main__':
    main()
