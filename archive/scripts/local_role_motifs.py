"""
LOCAL ROLE MOTIFS ANALYSIS

Question: Are there recurring role-level patterns below the n-gram level?

We know from TRANS phase:
- 99.6% of trigrams are hapax at TOKEN level
- But role-level (6 classes) might show recurring STRUCTURAL patterns

This would reveal the "grammar skeleton" more clearly.
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import entropy

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
GRAMMAR = BASE / "results" / "canonical_grammar.json"

def load_grammar():
    """Load token -> role mapping."""
    with open(GRAMMAR, 'r', encoding='utf-8') as f:
        data = json.load(f)

    token_to_role = {}
    terminals = data.get('terminals', {}).get('list', [])
    for term in terminals:
        token_to_role[term['symbol']] = term['role']

    return token_to_role

def load_b_sequences():
    """Load Currier B token sequences by folio."""
    sequences = defaultdict(list)

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            if row.get('language') != 'B':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            folio = row['folio']
            sequences[folio].append(token)

    return sequences

def convert_to_roles(sequences, token_to_role):
    """Convert token sequences to role sequences."""
    role_sequences = {}

    for folio, tokens in sequences.items():
        roles = []
        for token in tokens:
            role = token_to_role.get(token)
            if role:
                roles.append(role)
            else:
                roles.append('UNCATEGORIZED')
        role_sequences[folio] = roles

    return role_sequences

def analyze_role_ngrams(role_sequences, n=2):
    """Analyze n-gram patterns at role level."""
    ngram_counts = Counter()
    total_ngrams = 0

    for folio, roles in role_sequences.items():
        for i in range(len(roles) - n + 1):
            ngram = tuple(roles[i:i+n])
            ngram_counts[ngram] += 1
            total_ngrams += 1

    return ngram_counts, total_ngrams

def calculate_ngram_stats(ngram_counts, total_ngrams):
    """Calculate statistics on n-gram distribution."""
    counts = list(ngram_counts.values())

    hapax = sum(1 for c in counts if c == 1)
    hapax_rate = hapax / len(counts) * 100 if counts else 0

    # Entropy
    probs = [c / total_ngrams for c in counts]
    ent = entropy(probs, base=2)

    # Top patterns
    top_patterns = ngram_counts.most_common(20)

    return {
        'unique': len(counts),
        'total': total_ngrams,
        'hapax': hapax,
        'hapax_rate': hapax_rate,
        'entropy': ent,
        'top_patterns': top_patterns
    }

def analyze_motif_reuse(role_sequences, n=3):
    """Check how many folios share the same role patterns."""
    # For each n-gram, track which folios contain it
    ngram_folios = defaultdict(set)

    for folio, roles in role_sequences.items():
        for i in range(len(roles) - n + 1):
            ngram = tuple(roles[i:i+n])
            ngram_folios[ngram].add(folio)

    # Distribution of folio coverage
    coverage_dist = Counter()
    for ngram, folios in ngram_folios.items():
        coverage_dist[len(folios)] += 1

    # Universal patterns (in >= 50% of folios)
    n_folios = len(role_sequences)
    universal = [(ng, len(f)) for ng, f in ngram_folios.items() if len(f) >= n_folios * 0.5]
    universal.sort(key=lambda x: -x[1])

    return coverage_dist, universal, ngram_folios

def compare_with_token_level(sequences, role_sequences, n=3):
    """Compare token vs role n-gram statistics."""
    # Token-level n-grams
    token_ngrams = Counter()
    for folio, tokens in sequences.items():
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i+n])
            token_ngrams[ngram] += 1

    token_hapax = sum(1 for c in token_ngrams.values() if c == 1)
    token_hapax_rate = token_hapax / len(token_ngrams) * 100 if token_ngrams else 0

    # Role-level n-grams
    role_ngrams = Counter()
    for folio, roles in role_sequences.items():
        for i in range(len(roles) - n + 1):
            ngram = tuple(roles[i:i+n])
            role_ngrams[ngram] += 1

    role_hapax = sum(1 for c in role_ngrams.values() if c == 1)
    role_hapax_rate = role_hapax / len(role_ngrams) * 100 if role_ngrams else 0

    return {
        'token': {
            'unique': len(token_ngrams),
            'total': sum(token_ngrams.values()),
            'hapax_rate': token_hapax_rate
        },
        'role': {
            'unique': len(role_ngrams),
            'total': sum(role_ngrams.values()),
            'hapax_rate': role_hapax_rate
        }
    }

def find_stereotyped_motifs(role_sequences, min_frequency=100):
    """Find role motifs that are significantly more common than expected."""
    print("\n" + "-"*70)
    print("STEREOTYPED MOTIFS (freq >= {})".format(min_frequency))
    print("-"*70)

    roles = ['ENERGY_OPERATOR', 'CORE_CONTROL', 'FREQUENT_OPERATOR',
             'FLOW_OPERATOR', 'AUXILIARY', 'HIGH_IMPACT', 'UNCATEGORIZED']

    # Calculate expected frequencies under independence
    role_freq = Counter()
    total_tokens = 0
    for folio, seq in role_sequences.items():
        for r in seq:
            role_freq[r] += 1
            total_tokens += 1

    role_probs = {r: c/total_tokens for r, c in role_freq.items()}

    # Bigrams
    bigram_counts, total_bigrams = analyze_role_ngrams(role_sequences, n=2)

    print("\nBigrams enriched > 2x expected:")
    for bigram, count in bigram_counts.most_common():
        if count < min_frequency:
            break
        expected = role_probs.get(bigram[0], 0) * role_probs.get(bigram[1], 0) * total_bigrams
        if expected > 0:
            ratio = count / expected
            if ratio > 2.0:
                print(f"  {bigram[0][:8]:>8} -> {bigram[1][:8]:<8}: {count:>5} (expected {expected:.0f}, ratio {ratio:.2f}x)")

    print("\nBigrams depleted < 0.5x expected:")
    for bigram, count in bigram_counts.items():
        if count < min_frequency:
            continue
        expected = role_probs.get(bigram[0], 0) * role_probs.get(bigram[1], 0) * total_bigrams
        if expected > 0:
            ratio = count / expected
            if ratio < 0.5:
                print(f"  {bigram[0][:8]:>8} -> {bigram[1][:8]:<8}: {count:>5} (expected {expected:.0f}, ratio {ratio:.2f}x)")

    # Trigrams
    trigram_counts, total_trigrams = analyze_role_ngrams(role_sequences, n=3)

    print("\nTop trigrams by frequency:")
    for trigram, count in trigram_counts.most_common(15):
        pct = count / total_trigrams * 100
        print(f"  {trigram[0][:6]:>6} -> {trigram[1][:6]:>6} -> {trigram[2][:6]:<6}: {count:>5} ({pct:.2f}%)")

def analyze_categorized_only(sequences, token_to_role):
    """Analyze patterns using ONLY grammar-categorized tokens."""
    print("\n" + "="*70)
    print("CATEGORIZED-ONLY ANALYSIS (excluding UNCATEGORIZED)")
    print("="*70)

    # Filter to just categorized tokens
    cat_sequences = {}
    for folio, tokens in sequences.items():
        cat_tokens = []
        for token in tokens:
            role = token_to_role.get(token)
            if role:  # Only categorized tokens
                cat_tokens.append(role)
        if cat_tokens:
            cat_sequences[folio] = cat_tokens

    total_cat = sum(len(s) for s in cat_sequences.values())
    print(f"\nFiltered to {total_cat} categorized tokens across {len(cat_sequences)} folios")

    # Role distribution (excluding UNCATEGORIZED)
    all_roles = []
    for roles in cat_sequences.values():
        all_roles.extend(roles)

    role_dist = Counter(all_roles)
    print("\nRole distribution (categorized only):")
    for role, count in role_dist.most_common():
        pct = count / len(all_roles) * 100
        print(f"  {role:<20}: {count:>5} ({pct:.1f}%)")

    # Bigram analysis
    bigram_counts = Counter()
    for folio, roles in cat_sequences.items():
        for i in range(len(roles) - 1):
            bigram = (roles[i], roles[i+1])
            bigram_counts[bigram] += 1

    total_bigrams = sum(bigram_counts.values())
    print(f"\nCategorized bigrams: {len(bigram_counts)} unique, {total_bigrams} total")

    # Calculate expected under independence
    role_probs = {r: c/len(all_roles) for r, c in role_dist.items()}

    print("\nTop bigrams (categorized only):")
    for bigram, count in bigram_counts.most_common(15):
        pct = count / total_bigrams * 100
        expected = role_probs.get(bigram[0], 0) * role_probs.get(bigram[1], 0) * total_bigrams
        ratio = count / expected if expected > 0 else float('inf')
        print(f"  {bigram[0][:8]:>8} -> {bigram[1]:<8}: {count:>4} ({pct:>5.1f}%) ratio={ratio:.2f}x")

    print("\nEnriched bigrams (>= 1.5x):")
    enriched = []
    for bigram, count in bigram_counts.items():
        expected = role_probs.get(bigram[0], 0) * role_probs.get(bigram[1], 0) * total_bigrams
        if expected > 0 and count >= 10:
            ratio = count / expected
            if ratio >= 1.5:
                enriched.append((bigram, count, ratio))
    enriched.sort(key=lambda x: -x[2])
    for bigram, count, ratio in enriched[:10]:
        print(f"  {bigram[0][:8]:>8} -> {bigram[1]:<8}: {count:>4} ({ratio:.2f}x)")

    print("\nDepleted bigrams (<= 0.67x):")
    depleted = []
    for bigram, count in bigram_counts.items():
        expected = role_probs.get(bigram[0], 0) * role_probs.get(bigram[1], 0) * total_bigrams
        if expected > 10:
            ratio = count / expected
            if ratio <= 0.67:
                depleted.append((bigram, count, expected, ratio))
    depleted.sort(key=lambda x: x[3])
    for bigram, count, expected, ratio in depleted[:10]:
        print(f"  {bigram[0][:8]:>8} -> {bigram[1]:<8}: {count:>4} (expected {expected:.0f}, ratio {ratio:.2f}x)")

    # Trigram analysis
    trigram_counts = Counter()
    for folio, roles in cat_sequences.items():
        for i in range(len(roles) - 2):
            trigram = (roles[i], roles[i+1], roles[i+2])
            trigram_counts[trigram] += 1

    total_trigrams = sum(trigram_counts.values())
    print(f"\nCategorized trigrams: {len(trigram_counts)} unique, {total_trigrams} total")

    print("\nTop trigrams (categorized only):")
    for trigram, count in trigram_counts.most_common(15):
        pct = count / total_trigrams * 100
        abbrev = " -> ".join(t[:6] for t in trigram)
        print(f"  {abbrev}: {count:>4} ({pct:.1f}%)")

    # Self-transitions
    print("\nSelf-transition rates:")
    for role in role_dist.keys():
        self_count = bigram_counts.get((role, role), 0)
        from_count = sum(c for (r1, r2), c in bigram_counts.items() if r1 == role)
        if from_count > 0:
            self_rate = self_count / from_count * 100
            print(f"  {role:<20}: {self_count:>4}/{from_count:<4} ({self_rate:.1f}%)")

def main():
    print("="*70)
    print("LOCAL ROLE MOTIFS ANALYSIS")
    print("="*70)

    token_to_role = load_grammar()
    sequences = load_b_sequences()
    role_sequences = convert_to_roles(sequences, token_to_role)

    print(f"\nLoaded {len(token_to_role)} token-role mappings")
    print(f"Loaded {len(sequences)} Currier B folios")

    # Overall role distribution
    all_roles = []
    for roles in role_sequences.values():
        all_roles.extend(roles)

    role_dist = Counter(all_roles)
    print("\nRole distribution:")
    for role, count in role_dist.most_common():
        pct = count / len(all_roles) * 100
        print(f"  {role:<20}: {count:>6} ({pct:.1f}%)")

    # Compare n-gram stats
    print("\n" + "-"*70)
    print("TOKEN vs ROLE N-GRAM COMPARISON")
    print("-"*70)

    for n in [2, 3, 4, 5]:
        comparison = compare_with_token_level(sequences, role_sequences, n=n)
        print(f"\n{n}-grams:")
        print(f"  Token level: {comparison['token']['unique']:>6} unique, {comparison['token']['hapax_rate']:.1f}% hapax")
        print(f"  Role level:  {comparison['role']['unique']:>6} unique, {comparison['role']['hapax_rate']:.1f}% hapax")
        print(f"  Compression: {comparison['token']['unique'] / comparison['role']['unique']:.1f}x")

    # Role bigram analysis
    print("\n" + "-"*70)
    print("ROLE BIGRAM PATTERNS")
    print("-"*70)

    bigram_counts, total = analyze_role_ngrams(role_sequences, n=2)
    stats = calculate_ngram_stats(bigram_counts, total)

    print(f"\nBigram statistics:")
    print(f"  Unique patterns: {stats['unique']}")
    print(f"  Total occurrences: {stats['total']}")
    print(f"  Hapax rate: {stats['hapax_rate']:.1f}%")
    print(f"  Entropy: {stats['entropy']:.2f} bits")

    print("\nTop 10 bigrams:")
    for pattern, count in stats['top_patterns'][:10]:
        pct = count / total * 100
        print(f"  {pattern[0][:8]:>8} -> {pattern[1]:<8}: {count:>5} ({pct:.1f}%)")

    # Role trigram analysis
    print("\n" + "-"*70)
    print("ROLE TRIGRAM PATTERNS")
    print("-"*70)

    trigram_counts, total = analyze_role_ngrams(role_sequences, n=3)
    stats = calculate_ngram_stats(trigram_counts, total)

    print(f"\nTrigram statistics:")
    print(f"  Unique patterns: {stats['unique']}")
    print(f"  Total occurrences: {stats['total']}")
    print(f"  Hapax rate: {stats['hapax_rate']:.1f}%")
    print(f"  Entropy: {stats['entropy']:.2f} bits")

    print("\nTop 10 trigrams:")
    for pattern, count in stats['top_patterns'][:10]:
        pct = count / total * 100
        abbrev = " -> ".join(p[:6] for p in pattern)
        print(f"  {abbrev}: {count:>5} ({pct:.1f}%)")

    # Motif reuse across folios
    print("\n" + "-"*70)
    print("MOTIF REUSE ACROSS FOLIOS")
    print("-"*70)

    for n in [2, 3, 4]:
        coverage_dist, universal, ngram_folios = analyze_motif_reuse(role_sequences, n=n)

        print(f"\n{n}-gram folio coverage:")
        total_patterns = sum(coverage_dist.values())
        for coverage in sorted(coverage_dist.keys())[:10]:
            count = coverage_dist[coverage]
            pct = count / total_patterns * 100
            print(f"  In {coverage} folios: {count} patterns ({pct:.1f}%)")

        if universal:
            print(f"\nUniversal {n}-grams (>= 50% folios):")
            for ngram, folio_count in universal[:5]:
                abbrev = " -> ".join(p[:6] for p in ngram)
                print(f"  {abbrev}: {folio_count} folios")

    # Stereotyped motifs
    find_stereotyped_motifs(role_sequences)

    # Categorized-only analysis
    analyze_categorized_only(sequences, token_to_role)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
Key findings:
- At role level, patterns are much more repetitive than at token level
- Compression ratio shows how much of token variation is role-independent
- Universal patterns reveal the "grammar skeleton"
- Enriched/depleted bigrams show structural preferences
""")

if __name__ == '__main__':
    main()
