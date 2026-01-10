#!/usr/bin/env python
"""
Phase 2: Morphological Comparison

Research question Q1: Do ko- tokens pattern like ok- tokens morphologically?

Tests:
- Extract suffix distributions from ko- (first tokens) vs ok- (corpus-wide)
- Calculate Jaccard similarity
- Chi-square test for suffix distribution independence

Decision threshold: J > 0.20 indicates morphological equivalence
"""
import sys
import json
from collections import Counter
from typing import List, Dict, Set
import re
from scipy import stats

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from core.transcription import TranscriptionLoader
from parsing.currier_a import A_UNIVERSAL_SUFFIXES, MARKER_FAMILIES


# =============================================================================
# SUFFIX EXTRACTION
# =============================================================================

def extract_suffix(token: str, prefix_len: int) -> str:
    """
    Extract suffix from token after removing prefix.

    Uses longest-match from A_UNIVERSAL_SUFFIXES.
    """
    remainder = token.lower()[prefix_len:]
    if not remainder:
        return ''

    # Try longest match first
    for length in range(min(len(remainder), 5), 0, -1):
        candidate = remainder[-length:]
        if candidate in A_UNIVERSAL_SUFFIXES:
            return candidate

    # Fall back to last 2 chars
    return remainder[-2:] if len(remainder) >= 2 else remainder


def extract_middle(token: str, prefix_len: int, suffix: str) -> str:
    """Extract middle component."""
    remainder = token.lower()[prefix_len:]
    if suffix and remainder.endswith(suffix):
        return remainder[:-len(suffix)]
    return remainder


# =============================================================================
# CORPUS EXTRACTION
# =============================================================================

def get_ok_tokens_from_corpus() -> List[dict]:
    """
    Extract all ok- tokens from the entire A folio corpus.

    Returns list of dicts with token, suffix, middle.
    """
    loader = TranscriptionLoader()
    loader.load_interlinear('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

    # All A folios
    a_folios = [f'{i}{side}' for i in range(1, 26) for side in ['r', 'v']]

    ok_tokens = []

    for folio_id in a_folios:
        folio = loader.get_folio(folio_id)
        if not folio or not folio.lines:
            continue

        for line in folio.lines:
            tokens = re.split(r'[\.\s]+', line.text)
            tokens = [t for t in tokens if t]

            for token in tokens:
                token_lower = token.lower()
                if len(token_lower) >= 3 and token_lower[:2] == 'ok':
                    suffix = extract_suffix(token, 2)
                    middle = extract_middle(token, 2, suffix)
                    ok_tokens.append({
                        'token': token,
                        'suffix': suffix,
                        'middle': middle,
                        'folio': folio_id,
                    })

    return ok_tokens


def load_ko_tokens_from_phase1() -> List[dict]:
    """
    Load ko- tokens from Phase 1 data.
    """
    with open('C:/git/voynich/phases/exploration/first_token_data.json', 'r') as f:
        data = json.load(f)

    ko_tokens = []
    for record in data['records']:
        if record['prefix_2char'] == 'ko':
            suffix = extract_suffix(record['token'], 2)
            middle = extract_middle(record['token'], 2, suffix)
            ko_tokens.append({
                'token': record['token'],
                'suffix': suffix,
                'middle': middle,
                'folio': record['folio_id'],
            })

    return ko_tokens


# =============================================================================
# STATISTICAL TESTS
# =============================================================================

def jaccard_similarity(set1: Set, set2: Set) -> float:
    """Calculate Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union


def chi_square_suffix_test(ko_suffixes: List[str], ok_suffixes: List[str]) -> dict:
    """
    Chi-square test for suffix distribution independence.

    Returns dict with chi2, p-value, and decision.
    """
    # Get all unique suffixes
    all_suffixes = set(ko_suffixes) | set(ok_suffixes)

    # Count frequencies
    ko_counts = Counter(ko_suffixes)
    ok_counts = Counter(ok_suffixes)

    # Build contingency table
    ko_freq = [ko_counts.get(s, 0) for s in sorted(all_suffixes)]
    ok_freq = [ok_counts.get(s, 0) for s in sorted(all_suffixes)]

    # Need at least 5 expected in each cell for chi-square
    # Use Fisher exact or skip if too sparse
    total_ko = sum(ko_freq)
    total_ok = sum(ok_freq)

    if total_ko < 5 or total_ok < 5:
        return {
            'chi2': None,
            'p_value': None,
            'decision': 'INSUFFICIENT_DATA',
            'note': f'ko={total_ko}, ok={total_ok} tokens - too few for chi-square'
        }

    # Chi-square test
    try:
        chi2, p_value = stats.chisquare(ko_freq, f_exp=ok_freq)
        decision = 'INDEPENDENT' if p_value < 0.05 else 'NOT_INDEPENDENT'
    except:
        # If expected frequencies don't match, use different approach
        # Compare distributions directly
        contingency = [ko_freq, ok_freq]
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        decision = 'INDEPENDENT' if p_value < 0.05 else 'NOT_INDEPENDENT'

    return {
        'chi2': chi2,
        'p_value': p_value,
        'decision': decision,
        'note': 'Chi-square goodness of fit'
    }


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def run_morphology_comparison():
    """Run full Phase 2 analysis."""

    print("=" * 70)
    print("PHASE 2: Morphological Comparison (ko- vs ok-)")
    print("=" * 70)

    # Load data
    ko_tokens = load_ko_tokens_from_phase1()
    ok_tokens = get_ok_tokens_from_corpus()

    print(f"\n### Data Loaded ###")
    print(f"ko- tokens (first position): {len(ko_tokens)}")
    print(f"ok- tokens (corpus-wide): {len(ok_tokens)}")

    # Suffix analysis
    ko_suffixes = [t['suffix'] for t in ko_tokens]
    ok_suffixes = [t['suffix'] for t in ok_tokens]

    print(f"\n### Suffix Distribution ###")

    print(f"\nko- suffix distribution:")
    ko_suffix_counts = Counter(ko_suffixes)
    for suffix, count in ko_suffix_counts.most_common():
        pct = 100 * count / len(ko_suffixes)
        print(f"  -{suffix:5}: {count:3} ({pct:5.1f}%)")

    print(f"\nok- suffix distribution (top 10):")
    ok_suffix_counts = Counter(ok_suffixes)
    for suffix, count in ok_suffix_counts.most_common(10):
        pct = 100 * count / len(ok_suffixes)
        print(f"  -{suffix:5}: {count:3} ({pct:5.1f}%)")

    # Jaccard similarity of suffix TYPES (not frequencies)
    ko_suffix_set = set(ko_suffixes)
    ok_suffix_set = set(ok_suffixes)

    jaccard = jaccard_similarity(ko_suffix_set, ok_suffix_set)

    print(f"\n### Jaccard Similarity ###")
    print(f"ko- suffix types: {sorted(ko_suffix_set)}")
    print(f"ok- suffix types (sample): {sorted(list(ok_suffix_set)[:15])}")
    print(f"Intersection: {sorted(ko_suffix_set & ok_suffix_set)}")
    print(f"Jaccard J = {jaccard:.3f}")

    if jaccard > 0.20:
        print(f"  --> PASS: J > 0.20 threshold (morphological similarity)")
    else:
        print(f"  --> FAIL: J <= 0.20 threshold (no morphological similarity)")

    # Middle component analysis
    ko_middles = [t['middle'] for t in ko_tokens if t['middle']]
    ok_middles = [t['middle'] for t in ok_tokens if t['middle']]

    print(f"\n### Middle Component Analysis ###")
    print(f"ko- tokens with middle: {len(ko_middles)}")
    print(f"ok- tokens with middle: {len(ok_middles)}")

    if ko_middles:
        print(f"\nko- middle distribution:")
        ko_middle_counts = Counter(ko_middles)
        for middle, count in ko_middle_counts.most_common(5):
            print(f"  {middle:8}: {count}")

    if ok_middles:
        print(f"\nok- middle distribution (top 5):")
        ok_middle_counts = Counter(ok_middles)
        for middle, count in ok_middle_counts.most_common(5):
            print(f"  {middle:8}: {count}")

    # Middle overlap
    ko_middle_set = set(ko_middles)
    ok_middle_set = set(ok_middles)
    middle_jaccard = jaccard_similarity(ko_middle_set, ok_middle_set)

    print(f"\nMiddle Jaccard J = {middle_jaccard:.3f}")

    # Full token comparison
    print(f"\n### Token-by-Token Analysis ###")
    print(f"{'ko- Token':<15} {'Remainder':<12} {'Expected ok-':<15} {'ok- Exists?'}")
    print("-" * 55)

    ok_token_set = set(t['token'].lower() for t in ok_tokens)

    for kt in ko_tokens:
        remainder = kt['token'].lower()[2:]  # After ko-
        expected_ok = 'ok' + remainder
        exists = expected_ok in ok_token_set
        print(f"{kt['token']:<15} {remainder:<12} {expected_ok:<15} {'YES' if exists else 'NO'}")

    # Count how many ko- tokens have ok- equivalents
    equivalents_found = sum(1 for kt in ko_tokens if ('ok' + kt['token'].lower()[2:]) in ok_token_set)
    equiv_rate = 100 * equivalents_found / len(ko_tokens) if ko_tokens else 0

    print(f"\nEquivalents found: {equivalents_found}/{len(ko_tokens)} ({equiv_rate:.1f}%)")

    # Summary
    print(f"\n{'=' * 70}")
    print("PHASE 2 SUMMARY")
    print(f"{'=' * 70}")
    print(f"Suffix Jaccard (ko- vs ok-): {jaccard:.3f}")
    print(f"Middle Jaccard (ko- vs ok-): {middle_jaccard:.3f}")
    print(f"Direct token equivalents: {equiv_rate:.1f}%")

    if jaccard > 0.20 and equiv_rate > 50:
        decision = "STRONG_EQUIVALENCE"
        print(f"\nDECISION: {decision}")
        print("ko- and ok- share morphological structure. ko- appears to be")
        print("a positional variant (inversion) of the ok- marker family.")
    elif jaccard > 0.20:
        decision = "WEAK_EQUIVALENCE"
        print(f"\nDECISION: {decision}")
        print("ko- shares suffix vocabulary with ok- but limited token overlap.")
        print("May be related family rather than direct variant.")
    else:
        decision = "NO_EQUIVALENCE"
        print(f"\nDECISION: {decision}")
        print("ko- and ok- do not share morphological patterns.")
        print("First-token ko- is structurally distinct from corpus ok-.")

    # Save results
    results = {
        'phase': 'first_token_morphology',
        'ko_token_count': len(ko_tokens),
        'ok_token_count': len(ok_tokens),
        'suffix_jaccard': jaccard,
        'middle_jaccard': middle_jaccard,
        'direct_equivalent_rate': equiv_rate,
        'decision': decision,
        'ko_suffixes': dict(ko_suffix_counts),
        'ok_suffixes_top10': dict(ok_suffix_counts.most_common(10)),
    }

    with open('C:/git/voynich/phases/exploration/first_token_morphology_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: phases/exploration/first_token_morphology_results.json")

    return results


if __name__ == '__main__':
    run_morphology_comparison()
