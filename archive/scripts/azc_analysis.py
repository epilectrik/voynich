#!/usr/bin/env python3
"""
AZC Phase Analysis: Astronomical/Zodiac/Cosmological Section Characterization

Investigates the ~7.7% of tokens (9,401) that are not classified as Currier A or B.
These tokens are concentrated in sections A (Astronomical), Z (Zodiac), C (Cosmological).

Tests whether AZC text is:
- B-LIKE (procedural grammar)
- A-LIKE (registry patterns)
- HYBRID (mixed characteristics)
- UNIQUE (third distinct system)
"""

import json
import os
from collections import Counter, defaultdict
from pathlib import Path
import math

# Change to project directory
os.chdir('C:/git/voynich')

# =============================================================================
# DATA LOADING
# =============================================================================

def load_transcription():
    """Load full transcription data."""
    data = []
    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    header = lines[0].strip().split('\t')
    header = [h.strip('"') for h in header]

    for line in lines[1:]:
        parts = line.strip().split('\t')
        if len(parts) >= len(header):
            row = {}
            for i, h in enumerate(header):
                val = parts[i].strip('"') if i < len(parts) else ''
                row[h] = val
            data.append(row)

    return data, header

def load_grammar():
    """Load 49-class canonical grammar."""
    try:
        with open('results/canonical_grammar.json', 'r') as f:
            return json.load(f)
    except:
        return None

def extract_grammar_vocabulary():
    """Extract vocabulary from grammar if available."""
    grammar = load_grammar()
    if not grammar:
        # Fall back to known high-frequency B vocabulary
        return set()

    vocab = set()
    if isinstance(grammar, dict):
        for class_data in grammar.values():
            if isinstance(class_data, dict) and 'tokens' in class_data:
                vocab.update(class_data['tokens'])
            elif isinstance(class_data, list):
                vocab.update(class_data)
    return vocab

# =============================================================================
# TOKEN EXTRACTION AND INVENTORY
# =============================================================================

def extract_azc_tokens(data):
    """Extract all tokens classified as NA (not A or B)."""
    azc_tokens = []
    azc_by_section = defaultdict(list)
    azc_by_folio = defaultdict(list)

    for row in data:
        lang = row.get('language', '')
        if lang == 'NA' or lang == '':
            token = row.get('word', '')
            if token:
                azc_tokens.append(row)
                section = row.get('section', 'UNK')
                folio = row.get('folio', 'UNK')
                azc_by_section[section].append(row)
                azc_by_folio[folio].append(row)

    return azc_tokens, azc_by_section, azc_by_folio

def extract_currier_tokens(data, currier_type):
    """Extract tokens for Currier A or B."""
    tokens = []
    for row in data:
        lang = row.get('language', '')
        if lang == currier_type:
            tokens.append(row)
    return tokens

def compute_inventory_stats(tokens):
    """Compute basic inventory statistics."""
    words = [t.get('word', '') for t in tokens]
    unique_words = set(words)

    # Tokens per folio
    by_folio = defaultdict(list)
    for t in tokens:
        by_folio[t.get('folio', '')].append(t.get('word', ''))

    tokens_per_folio = [len(v) for v in by_folio.values()]

    # Tokens per line
    by_line = defaultdict(list)
    for t in tokens:
        key = (t.get('folio', ''), t.get('line_number', ''))
        by_line[key].append(t.get('word', ''))

    tokens_per_line = [len(v) for v in by_line.values()]

    return {
        'total_tokens': len(tokens),
        'unique_types': len(unique_words),
        'ttr': len(unique_words) / len(tokens) if tokens else 0,
        'num_folios': len(by_folio),
        'num_lines': len(by_line),
        'tokens_per_folio_mean': sum(tokens_per_folio) / len(tokens_per_folio) if tokens_per_folio else 0,
        'tokens_per_line_mean': sum(tokens_per_line) / len(tokens_per_line) if tokens_per_line else 0,
        'tokens_per_line_median': sorted(tokens_per_line)[len(tokens_per_line)//2] if tokens_per_line else 0,
    }

# =============================================================================
# B-GRAMMAR TESTS
# =============================================================================

def test_b_grammar_coverage(azc_tokens, b_tokens):
    """Test coverage against B vocabulary and grammar patterns."""
    # Get B vocabulary
    b_words = set(t.get('word', '') for t in b_tokens)

    # Check how many AZC tokens appear in B vocabulary
    azc_words = [t.get('word', '') for t in azc_tokens]
    azc_in_b = sum(1 for w in azc_words if w in b_words)

    coverage = azc_in_b / len(azc_words) if azc_words else 0

    # Check for LINK tokens (common B waiting markers)
    link_tokens = {'ol', 'al', 'or', 'ar', 'aiin', 'daiin', 'chol', 'chor', 'shol', 'shor'}
    azc_unique = set(azc_words)
    link_overlap = azc_unique.intersection(link_tokens)

    # Count LINK-like tokens
    link_count = sum(1 for w in azc_words if w in link_tokens)
    link_density = link_count / len(azc_words) if azc_words else 0

    return {
        'b_vocabulary_coverage': coverage,
        'azc_tokens_in_b': azc_in_b,
        'azc_tokens_total': len(azc_words),
        'link_tokens_found': list(link_overlap),
        'link_density': link_density,
        'b_coverage_threshold': 0.70,
        'coverage_pass': coverage >= 0.70
    }

def analyze_transitions(tokens):
    """Analyze token-to-token transitions."""
    words = [t.get('word', '') for t in tokens]

    # Count bigrams
    bigrams = Counter()
    for i in range(len(words) - 1):
        bigram = (words[i], words[i+1])
        bigrams[bigram] += 1

    # Count unique bigrams vs total
    total_bigrams = sum(bigrams.values())
    unique_bigrams = len(bigrams)

    # Bigram reuse rate
    reuse_rate = 1 - (unique_bigrams / total_bigrams) if total_bigrams > 0 else 0

    # Top bigrams
    top_bigrams = bigrams.most_common(20)

    return {
        'total_bigrams': total_bigrams,
        'unique_bigrams': unique_bigrams,
        'bigram_reuse_rate': reuse_rate,
        'top_bigrams': [(f"{b[0]}->{b[1]}", c) for b, c in top_bigrams]
    }

# =============================================================================
# A-PATTERN TESTS
# =============================================================================

def test_a_patterns(azc_tokens, a_tokens):
    """Test for Currier A registry patterns."""
    results = {}

    # Marker prefixes from A
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    azc_words = [t.get('word', '') for t in azc_tokens]
    a_words = [t.get('word', '') for t in a_tokens]

    # Test 1: Marker prefix presence
    def count_prefixes(words):
        counts = {p: 0 for p in marker_prefixes}
        for w in words:
            for p in marker_prefixes:
                if w.startswith(p):
                    counts[p] += 1
                    break
        return counts

    azc_prefix_counts = count_prefixes(azc_words)
    a_prefix_counts = count_prefixes(a_words)

    azc_prefix_rate = sum(azc_prefix_counts.values()) / len(azc_words) if azc_words else 0
    a_prefix_rate = sum(a_prefix_counts.values()) / len(a_words) if a_words else 0

    results['marker_prefix_rate_azc'] = azc_prefix_rate
    results['marker_prefix_rate_a'] = a_prefix_rate
    results['marker_prefix_counts_azc'] = azc_prefix_counts
    results['prefix_similarity'] = azc_prefix_rate / a_prefix_rate if a_prefix_rate > 0 else 0

    # Test 2: A vocabulary overlap
    a_vocab = set(a_words)
    azc_in_a = sum(1 for w in azc_words if w in a_vocab)
    a_coverage = azc_in_a / len(azc_words) if azc_words else 0
    results['a_vocabulary_coverage'] = a_coverage

    # Test 3: Tokens per line (A is LINE_ATOMIC with low tokens/line)
    azc_by_line = defaultdict(list)
    for t in azc_tokens:
        key = (t.get('folio', ''), t.get('line_number', ''))
        azc_by_line[key].append(t.get('word', ''))

    azc_tpl = [len(v) for v in azc_by_line.values()]
    azc_tpl_median = sorted(azc_tpl)[len(azc_tpl)//2] if azc_tpl else 0

    a_by_line = defaultdict(list)
    for t in a_tokens:
        key = (t.get('folio', ''), t.get('line_number', ''))
        a_by_line[key].append(t.get('word', ''))

    a_tpl = [len(v) for v in a_by_line.values()]
    a_tpl_median = sorted(a_tpl)[len(a_tpl)//2] if a_tpl else 0

    results['tokens_per_line_median_azc'] = azc_tpl_median
    results['tokens_per_line_median_a'] = a_tpl_median
    results['line_atomic_similar'] = abs(azc_tpl_median - a_tpl_median) <= 2

    # Test 4: Repetition patterns (A shows block repetition)
    azc_unique = set(azc_words)
    a_unique = set(a_words)

    # Check for repeated tokens (same token appearing consecutively)
    def count_repetitions(words):
        reps = 0
        for i in range(len(words) - 1):
            if words[i] == words[i+1]:
                reps += 1
        return reps / len(words) if words else 0

    azc_rep_rate = count_repetitions(azc_words)
    a_rep_rate = count_repetitions(a_words)

    results['repetition_rate_azc'] = azc_rep_rate
    results['repetition_rate_a'] = a_rep_rate

    return results

# =============================================================================
# VOCABULARY OVERLAP ANALYSIS
# =============================================================================

def analyze_vocabulary_overlap(azc_tokens, a_tokens, b_tokens):
    """Detailed vocabulary overlap analysis."""
    azc_words = set(t.get('word', '') for t in azc_tokens)
    a_words = set(t.get('word', '') for t in a_tokens)
    b_words = set(t.get('word', '') for t in b_tokens)

    # Overlaps
    azc_only = azc_words - a_words - b_words
    azc_and_a = azc_words.intersection(a_words) - b_words
    azc_and_b = azc_words.intersection(b_words) - a_words
    azc_and_both = azc_words.intersection(a_words).intersection(b_words)

    # Token counts for each category
    azc_word_list = [t.get('word', '') for t in azc_tokens]

    azc_only_count = sum(1 for w in azc_word_list if w in azc_only)
    azc_and_a_count = sum(1 for w in azc_word_list if w in azc_and_a)
    azc_and_b_count = sum(1 for w in azc_word_list if w in azc_and_b)
    azc_and_both_count = sum(1 for w in azc_word_list if w in azc_and_both)

    total = len(azc_word_list)

    return {
        'azc_unique_types': len(azc_words),
        'azc_only_types': len(azc_only),
        'azc_and_a_only_types': len(azc_and_a),
        'azc_and_b_only_types': len(azc_and_b),
        'azc_and_both_types': len(azc_and_both),

        'azc_only_tokens': azc_only_count,
        'azc_and_a_only_tokens': azc_and_a_count,
        'azc_and_b_only_tokens': azc_and_b_count,
        'azc_and_both_tokens': azc_and_both_count,

        'azc_only_pct': azc_only_count / total if total else 0,
        'azc_and_a_only_pct': azc_and_a_count / total if total else 0,
        'azc_and_b_only_pct': azc_and_b_count / total if total else 0,
        'azc_and_both_pct': azc_and_both_count / total if total else 0,

        'sample_azc_only': list(azc_only)[:30],
        'sample_azc_and_a': list(azc_and_a)[:30],
        'sample_azc_and_b': list(azc_and_b)[:30],
    }

# =============================================================================
# MORPHOLOGICAL ANALYSIS
# =============================================================================

def analyze_morphology(tokens):
    """Analyze PREFIX/MIDDLE/SUFFIX structure."""
    # Known prefixes
    prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'yk', 'yt', 'kch', 'ko']

    # Known suffixes
    suffixes = ['aiin', 'ain', 'iin', 'in', 'dy', 'edy', 'eedy', 'y', 'ey', 'eey',
                'ol', 'al', 'or', 'ar', 'chy', 'shy', 'hy', 'eol', 'eal']

    words = [t.get('word', '') for t in tokens]

    prefix_counts = Counter()
    suffix_counts = Counter()

    for w in words:
        # Find prefix
        for p in sorted(prefixes, key=len, reverse=True):
            if w.startswith(p):
                prefix_counts[p] += 1
                break
        else:
            prefix_counts['NONE'] += 1

        # Find suffix
        for s in sorted(suffixes, key=len, reverse=True):
            if w.endswith(s):
                suffix_counts[s] += 1
                break
        else:
            suffix_counts['NONE'] += 1

    total = len(words)

    return {
        'prefix_distribution': {k: v/total for k, v in prefix_counts.most_common()},
        'suffix_distribution': {k: v/total for k, v in suffix_counts.most_common()},
        'prefix_coverage': 1 - (prefix_counts['NONE'] / total if total else 0),
        'suffix_coverage': 1 - (suffix_counts['NONE'] / total if total else 0),
        'top_prefixes': prefix_counts.most_common(10),
        'top_suffixes': suffix_counts.most_common(10),
    }

# =============================================================================
# SECTION-BY-SECTION ANALYSIS
# =============================================================================

def analyze_by_section(azc_by_section, a_tokens, b_tokens):
    """Analyze each AZC section separately."""
    results = {}

    a_words = set(t.get('word', '') for t in a_tokens)
    b_words = set(t.get('word', '') for t in b_tokens)

    for section, tokens in azc_by_section.items():
        words = [t.get('word', '') for t in tokens]
        unique = set(words)

        in_a = sum(1 for w in words if w in a_words)
        in_b = sum(1 for w in words if w in b_words)

        results[section] = {
            'total_tokens': len(words),
            'unique_types': len(unique),
            'ttr': len(unique) / len(words) if words else 0,
            'a_coverage': in_a / len(words) if words else 0,
            'b_coverage': in_b / len(words) if words else 0,
        }

    return results

# =============================================================================
# FOLIO-BY-FOLIO ANALYSIS
# =============================================================================

def analyze_by_folio(azc_by_folio, a_tokens, b_tokens):
    """Analyze each AZC folio."""
    results = {}

    a_words = set(t.get('word', '') for t in a_tokens)
    b_words = set(t.get('word', '') for t in b_tokens)

    for folio, tokens in azc_by_folio.items():
        words = [t.get('word', '') for t in tokens]
        unique = set(words)

        in_a = sum(1 for w in words if w in a_words)
        in_b = sum(1 for w in words if w in b_words)

        # Get section for this folio
        section = tokens[0].get('section', 'UNK') if tokens else 'UNK'

        results[folio] = {
            'section': section,
            'total_tokens': len(words),
            'unique_types': len(unique),
            'a_coverage': in_a / len(words) if words else 0,
            'b_coverage': in_b / len(words) if words else 0,
        }

    return results

# =============================================================================
# LINE STRUCTURE ANALYSIS
# =============================================================================

def analyze_line_structure(azc_tokens):
    """Analyze line-level structure."""
    by_line = defaultdict(list)
    for t in azc_tokens:
        key = (t.get('folio', ''), t.get('line_number', ''))
        by_line[key].append(t.get('word', ''))

    line_lengths = [len(v) for v in by_line.values()]

    # Check for line-initial patterns
    line_initials = Counter()
    line_finals = Counter()

    for key, words in by_line.items():
        if words:
            line_initials[words[0]] += 1
            line_finals[words[-1]] += 1

    return {
        'total_lines': len(by_line),
        'line_length_mean': sum(line_lengths) / len(line_lengths) if line_lengths else 0,
        'line_length_median': sorted(line_lengths)[len(line_lengths)//2] if line_lengths else 0,
        'line_length_min': min(line_lengths) if line_lengths else 0,
        'line_length_max': max(line_lengths) if line_lengths else 0,
        'top_line_initials': line_initials.most_common(15),
        'top_line_finals': line_finals.most_common(15),
        'line_initial_concentration': line_initials.most_common(1)[0][1] / len(by_line) if by_line else 0,
    }

# =============================================================================
# COMPARISON WITH HUMAN TRACK
# =============================================================================

def compare_with_human_track(azc_tokens, b_tokens):
    """Compare AZC with human track patterns in B."""
    # Human track tokens are those NOT in the 479 grammar vocabulary
    # We can approximate by checking morphological distinctness

    azc_words = [t.get('word', '') for t in azc_tokens]
    b_words = [t.get('word', '') for t in b_tokens]

    # Check for patterns typical of human track:
    # - High section exclusivity
    # - Line-initial enrichment
    # - Different morphological patterns

    # Calculate basic comparison metrics
    azc_unique = set(azc_words)
    b_unique = set(b_words)

    return {
        'azc_unique_types': len(azc_unique),
        'azc_not_in_b': len(azc_unique - b_unique),
        'azc_not_in_b_pct': len(azc_unique - b_unique) / len(azc_unique) if azc_unique else 0,
    }

# =============================================================================
# CLASSIFICATION VERDICT
# =============================================================================

def compute_verdict(b_test, a_test, vocab_analysis):
    """Compute classification verdict."""
    scores = {
        'B_LIKE': 0,
        'A_LIKE': 0,
        'HYBRID': 0,
        'UNIQUE': 0
    }

    evidence = []

    # B-grammar tests
    if b_test['b_vocabulary_coverage'] >= 0.70:
        scores['B_LIKE'] += 3
        evidence.append(f"HIGH B coverage: {b_test['b_vocabulary_coverage']:.1%}")
    elif b_test['b_vocabulary_coverage'] >= 0.30:
        scores['HYBRID'] += 2
        evidence.append(f"PARTIAL B coverage: {b_test['b_vocabulary_coverage']:.1%}")
    else:
        scores['UNIQUE'] += 2
        evidence.append(f"LOW B coverage: {b_test['b_vocabulary_coverage']:.1%}")

    # A-pattern tests
    if a_test['a_vocabulary_coverage'] >= 0.70:
        scores['A_LIKE'] += 3
        evidence.append(f"HIGH A coverage: {a_test['a_vocabulary_coverage']:.1%}")
    elif a_test['a_vocabulary_coverage'] >= 0.30:
        scores['HYBRID'] += 2
        evidence.append(f"PARTIAL A coverage: {a_test['a_vocabulary_coverage']:.1%}")
    else:
        if scores['B_LIKE'] < 3:
            scores['UNIQUE'] += 2
        evidence.append(f"LOW A coverage: {a_test['a_vocabulary_coverage']:.1%}")

    # Marker prefix test
    if a_test['prefix_similarity'] >= 0.8:
        scores['A_LIKE'] += 2
        evidence.append(f"A-like prefix pattern: {a_test['prefix_similarity']:.2f}")
    elif a_test['prefix_similarity'] <= 0.3:
        scores['B_LIKE'] += 1
        evidence.append(f"Not A-like prefixes: {a_test['prefix_similarity']:.2f}")

    # Unique vocabulary test
    if vocab_analysis['azc_only_pct'] >= 0.30:
        scores['UNIQUE'] += 3
        evidence.append(f"HIGH unique vocabulary: {vocab_analysis['azc_only_pct']:.1%}")
    elif vocab_analysis['azc_only_pct'] >= 0.15:
        scores['UNIQUE'] += 1
        evidence.append(f"MODERATE unique vocabulary: {vocab_analysis['azc_only_pct']:.1%}")

    # Mixed vocabulary test
    if vocab_analysis['azc_and_both_pct'] >= 0.40:
        scores['HYBRID'] += 2
        evidence.append(f"SHARED vocabulary (A+B): {vocab_analysis['azc_and_both_pct']:.1%}")

    # Determine winner
    max_score = max(scores.values())
    winners = [k for k, v in scores.items() if v == max_score]

    if len(winners) == 1:
        verdict = winners[0]
    elif 'HYBRID' in winners:
        verdict = 'HYBRID'
    else:
        verdict = 'INDETERMINATE'

    return {
        'verdict': verdict,
        'scores': scores,
        'evidence': evidence,
        'confidence': max_score / sum(scores.values()) if sum(scores.values()) > 0 else 0
    }

# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():
    print("=" * 60)
    print("AZC PHASE: Astronomical/Zodiac/Cosmological Analysis")
    print("=" * 60)
    print()

    # Load data
    print("Loading transcription data...")
    data, header = load_transcription()
    print(f"Total rows: {len(data)}")

    # Extract token sets
    print("\nExtracting token sets...")
    azc_tokens, azc_by_section, azc_by_folio = extract_azc_tokens(data)
    a_tokens = extract_currier_tokens(data, 'A')
    b_tokens = extract_currier_tokens(data, 'B')

    print(f"AZC tokens: {len(azc_tokens)}")
    print(f"Currier A tokens: {len(a_tokens)}")
    print(f"Currier B tokens: {len(b_tokens)}")

    # Inventory statistics
    print("\n" + "=" * 60)
    print("STEP 1: TOKEN INVENTORY")
    print("=" * 60)

    azc_stats = compute_inventory_stats(azc_tokens)
    a_stats = compute_inventory_stats(a_tokens)
    b_stats = compute_inventory_stats(b_tokens)

    print(f"\nAZC Statistics:")
    print(f"  Total tokens: {azc_stats['total_tokens']}")
    print(f"  Unique types: {azc_stats['unique_types']}")
    print(f"  TTR: {azc_stats['ttr']:.3f}")
    print(f"  Folios: {azc_stats['num_folios']}")
    print(f"  Lines: {azc_stats['num_lines']}")
    print(f"  Tokens/line (mean): {azc_stats['tokens_per_line_mean']:.2f}")
    print(f"  Tokens/line (median): {azc_stats['tokens_per_line_median']}")

    print(f"\nComparison:")
    print(f"  Currier A TTR: {a_stats['ttr']:.3f}")
    print(f"  Currier B TTR: {b_stats['ttr']:.3f}")
    print(f"  Currier A tokens/line: {a_stats['tokens_per_line_median']}")
    print(f"  Currier B tokens/line: {b_stats['tokens_per_line_median']}")

    # Section breakdown
    print("\nAZC by Section:")
    for section, tokens in sorted(azc_by_section.items(), key=lambda x: -len(x[1])):
        print(f"  {section}: {len(tokens)} tokens")

    # B-Grammar Test
    print("\n" + "=" * 60)
    print("STEP 2: B-GRAMMAR TEST")
    print("=" * 60)

    b_test = test_b_grammar_coverage(azc_tokens, b_tokens)
    print(f"\nB vocabulary coverage: {b_test['b_vocabulary_coverage']:.1%}")
    print(f"  (Threshold for B-LIKE: >= 70%)")
    print(f"  Result: {'PASS' if b_test['coverage_pass'] else 'FAIL'}")
    print(f"\nLINK density: {b_test['link_density']:.1%}")
    print(f"  (Currier B LINK density: ~6.6%)")
    print(f"  LINK tokens found: {b_test['link_tokens_found']}")

    # Transition analysis
    azc_transitions = analyze_transitions(azc_tokens)
    print(f"\nBigram reuse rate: {azc_transitions['bigram_reuse_rate']:.1%}")
    print(f"  (Currier A: ~70.7%, Currier B: lower)")

    # A-Pattern Test
    print("\n" + "=" * 60)
    print("STEP 3: A-PATTERN TEST")
    print("=" * 60)

    a_test = test_a_patterns(azc_tokens, a_tokens)
    print(f"\nA vocabulary coverage: {a_test['a_vocabulary_coverage']:.1%}")
    print(f"Marker prefix rate (AZC): {a_test['marker_prefix_rate_azc']:.1%}")
    print(f"Marker prefix rate (A): {a_test['marker_prefix_rate_a']:.1%}")
    print(f"Prefix similarity: {a_test['prefix_similarity']:.2f}")

    print(f"\nTokens/line median (AZC): {a_test['tokens_per_line_median_azc']}")
    print(f"Tokens/line median (A): {a_test['tokens_per_line_median_a']}")
    print(f"LINE_ATOMIC similar: {a_test['line_atomic_similar']}")

    print(f"\nRepetition rate (AZC): {a_test['repetition_rate_azc']:.1%}")
    print(f"Repetition rate (A): {a_test['repetition_rate_a']:.1%}")

    # Vocabulary Overlap
    print("\n" + "=" * 60)
    print("STEP 4: VOCABULARY OVERLAP")
    print("=" * 60)

    vocab = analyze_vocabulary_overlap(azc_tokens, a_tokens, b_tokens)

    print(f"\nAZC vocabulary distribution:")
    print(f"  AZC-only (unique): {vocab['azc_only_pct']:.1%} ({vocab['azc_only_types']} types)")
    print(f"  Shared with A only: {vocab['azc_and_a_only_pct']:.1%} ({vocab['azc_and_a_only_types']} types)")
    print(f"  Shared with B only: {vocab['azc_and_b_only_pct']:.1%} ({vocab['azc_and_b_only_types']} types)")
    print(f"  Shared with BOTH: {vocab['azc_and_both_pct']:.1%} ({vocab['azc_and_both_types']} types)")

    print(f"\nSample AZC-only tokens: {vocab['sample_azc_only'][:15]}")

    # Morphological Analysis
    print("\n" + "=" * 60)
    print("STEP 5: MORPHOLOGICAL ANALYSIS")
    print("=" * 60)

    azc_morph = analyze_morphology(azc_tokens)
    a_morph = analyze_morphology(a_tokens)
    b_morph = analyze_morphology(b_tokens)

    print(f"\nPrefix coverage:")
    print(f"  AZC: {azc_morph['prefix_coverage']:.1%}")
    print(f"  Currier A: {a_morph['prefix_coverage']:.1%}")
    print(f"  Currier B: {b_morph['prefix_coverage']:.1%}")

    print(f"\nSuffix coverage:")
    print(f"  AZC: {azc_morph['suffix_coverage']:.1%}")
    print(f"  Currier A: {a_morph['suffix_coverage']:.1%}")
    print(f"  Currier B: {b_morph['suffix_coverage']:.1%}")

    print(f"\nTop AZC prefixes: {azc_morph['top_prefixes'][:5]}")
    print(f"Top AZC suffixes: {azc_morph['top_suffixes'][:5]}")

    # Section-by-Section
    print("\n" + "=" * 60)
    print("STEP 6: SECTION-BY-SECTION ANALYSIS")
    print("=" * 60)

    section_analysis = analyze_by_section(azc_by_section, a_tokens, b_tokens)
    for section, stats in sorted(section_analysis.items()):
        print(f"\nSection {section}:")
        print(f"  Tokens: {stats['total_tokens']}, Types: {stats['unique_types']}, TTR: {stats['ttr']:.3f}")
        print(f"  A coverage: {stats['a_coverage']:.1%}, B coverage: {stats['b_coverage']:.1%}")

    # Line Structure
    print("\n" + "=" * 60)
    print("STEP 7: LINE STRUCTURE")
    print("=" * 60)

    line_struct = analyze_line_structure(azc_tokens)
    print(f"\nLine statistics:")
    print(f"  Total lines: {line_struct['total_lines']}")
    print(f"  Length mean: {line_struct['line_length_mean']:.2f}")
    print(f"  Length median: {line_struct['line_length_median']}")
    print(f"  Length range: {line_struct['line_length_min']}-{line_struct['line_length_max']}")

    print(f"\nTop line-initial tokens: {line_struct['top_line_initials'][:10]}")
    print(f"Line-initial concentration: {line_struct['line_initial_concentration']:.1%}")

    # Folio Analysis
    print("\n" + "=" * 60)
    print("STEP 8: FOLIO-BY-FOLIO ANALYSIS")
    print("=" * 60)

    folio_analysis = analyze_by_folio(azc_by_folio, a_tokens, b_tokens)

    # Sort by token count
    sorted_folios = sorted(folio_analysis.items(), key=lambda x: -x[1]['total_tokens'])
    print("\nTop 15 AZC folios by token count:")
    for folio, stats in sorted_folios[:15]:
        print(f"  {folio} ({stats['section']}): {stats['total_tokens']} tokens, "
              f"A={stats['a_coverage']:.1%}, B={stats['b_coverage']:.1%}")

    # VERDICT
    print("\n" + "=" * 60)
    print("CLASSIFICATION VERDICT")
    print("=" * 60)

    verdict = compute_verdict(b_test, a_test, vocab)

    print(f"\nVerdict: {verdict['verdict']}")
    print(f"Confidence: {verdict['confidence']:.1%}")
    print(f"\nScores:")
    for k, v in sorted(verdict['scores'].items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print(f"\nEvidence:")
    for e in verdict['evidence']:
        print(f"  - {e}")

    # Save results
    print("\n" + "=" * 60)
    print("SAVING RESULTS")
    print("=" * 60)

    results = {
        'inventory': azc_stats,
        'inventory_comparison': {
            'a': a_stats,
            'b': b_stats
        },
        'b_grammar_test': b_test,
        'a_pattern_test': a_test,
        'transitions': azc_transitions,
        'vocabulary_overlap': vocab,
        'morphology': {
            'azc': azc_morph,
            'comparison_a': a_morph,
            'comparison_b': b_morph
        },
        'section_analysis': section_analysis,
        'line_structure': line_struct,
        'folio_analysis': folio_analysis,
        'verdict': verdict
    }

    output_path = 'phases/AZC_astronomical_zodiac_cosmological/azc_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to: {output_path}")

    print("\n" + "=" * 60)
    print("AZC ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    main()
