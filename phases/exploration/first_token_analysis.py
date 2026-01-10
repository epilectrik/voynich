#!/usr/bin/env python
"""
Phase 1: First-Token Data Collection

Research question: 75% of first tokens in Currier A folios fail standard classification.
Do they show structural patterns worth documenting?

Collects:
- All first tokens from A folios (1r-25v range)
- Classification status for each
- Morphological decomposition attempt
- Folio section metadata

Output: JSON data file for Phase 2-3 analysis
"""
import sys
import json
from collections import Counter
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
import re

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from ui.folio_viewer import get_token_primary_system
from core.transcription import TranscriptionLoader
from parsing.currier_a import (
    MARKER_FAMILIES, EXTENDED_PREFIX_MAP, A_UNIVERSAL_SUFFIXES,
    parse_currier_a_token
)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class FirstTokenRecord:
    """Complete record for a first token."""
    folio_id: str
    token: str
    classification: str
    is_pass: bool
    prefix_2char: str
    prefix_3char: str
    suffix_2char: str
    suffix_3char: str
    length: int
    # Hypothesized morphology
    hyp_prefix_type: str  # 'C240', 'C349', 'C+vowel', 'other'
    hyp_base_family: Optional[str]  # Mapped family if C+vowel
    hyp_remainder: str  # After prefix stripped


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Known C+vowel prefix candidates (NOT C240-valid, but structured)
C_VOWEL_PATTERNS = {
    'ko': 'ok',  # Hypothesized inversion
    'to': 'ot',  # Hypothesized inversion
    'po': None,  # No obvious partner (investigate)
    'fo': None,  # No obvious partner (investigate)
    'ka': None,
    'ta': None,
    'pa': None,
    'fa': None,
}


def classify_prefix_type(token: str) -> tuple:
    """
    Classify the prefix type of a token.

    Returns: (prefix_type, base_family, prefix_len)
    - prefix_type: 'C240', 'C349', 'C+vowel', 'other'
    - base_family: The C240 family it maps to (if known)
    - prefix_len: Length of detected prefix
    """
    token_lower = token.lower()

    # Check C349 extended prefixes first (3-char)
    if len(token_lower) >= 3:
        prefix3 = token_lower[:3]
        if prefix3 in EXTENDED_PREFIX_MAP:
            return ('C349', EXTENDED_PREFIX_MAP[prefix3], 3)

    # Check C240 marker families (2-char)
    if len(token_lower) >= 2:
        prefix2 = token_lower[:2]
        if prefix2 in MARKER_FAMILIES:
            return ('C240', prefix2, 2)

    # Check C+vowel patterns (potential inversions)
    if len(token_lower) >= 2:
        prefix2 = token_lower[:2]
        if prefix2 in C_VOWEL_PATTERNS:
            return ('C+vowel', C_VOWEL_PATTERNS[prefix2], 2)

    # Check consonant + vowel/y general pattern
    if len(token_lower) >= 2:
        if token_lower[0] in 'bcdfghjklmnpqrstvwxz' and token_lower[1] in 'aeiouyw':
            return ('C+V_general', None, 2)

    return ('other', None, 0)


def extract_hypothesized_remainder(token: str, prefix_type: str, prefix_len: int) -> str:
    """Extract the remainder after hypothesized prefix."""
    if prefix_len > 0:
        return token[prefix_len:].lower()
    return token.lower()


def get_folio_section(folio_id: str) -> str:
    """
    Map folio ID to manuscript section.
    Simplified mapping based on standard folio ranges.
    """
    # Extract folio number
    match = re.match(r'(\d+)', folio_id)
    if not match:
        return 'UNKNOWN'

    num = int(match.group(1))

    # Rough section boundaries (Currier's divisions)
    if 1 <= num <= 8:
        return 'H'  # Herbal (early)
    elif 9 <= num <= 16:
        return 'H'  # Herbal (mid)
    elif 17 <= num <= 25:
        return 'H'  # Herbal (late)
    else:
        return 'OTHER'


# =============================================================================
# MAIN DATA COLLECTION
# =============================================================================

def collect_first_tokens() -> List[FirstTokenRecord]:
    """Collect all first tokens from A folios with full metadata."""

    loader = TranscriptionLoader()
    loader.load_interlinear('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

    # A folios range (1-25 both sides)
    a_folios = [f'{i}{side}' for i in range(1, 26) for side in ['r', 'v']]

    records = []

    for folio_id in a_folios:
        folio = loader.get_folio(folio_id)
        if not folio or not folio.lines:
            continue

        first_line = folio.lines[0]
        tokens = re.split(r'[\.\s]+', first_line.text)
        tokens = [t for t in tokens if t]

        if not tokens:
            continue

        first_token = tokens[0]
        classification = get_token_primary_system(first_token, 'A')

        # Determine pass/fail
        is_pass = classification in ('A', 'A_UNDERSPECIFIED', 'A-UNCERTAIN')

        # Extract prefix/suffix components
        token_lower = first_token.lower()
        prefix_2char = token_lower[:2] if len(token_lower) >= 2 else token_lower
        prefix_3char = token_lower[:3] if len(token_lower) >= 3 else token_lower
        suffix_2char = token_lower[-2:] if len(token_lower) >= 2 else token_lower
        suffix_3char = token_lower[-3:] if len(token_lower) >= 3 else token_lower

        # Classify prefix type
        prefix_type, base_family, prefix_len = classify_prefix_type(first_token)
        remainder = extract_hypothesized_remainder(first_token, prefix_type, prefix_len)

        record = FirstTokenRecord(
            folio_id=folio_id,
            token=first_token,
            classification=classification,
            is_pass=is_pass,
            prefix_2char=prefix_2char,
            prefix_3char=prefix_3char,
            suffix_2char=suffix_2char,
            suffix_3char=suffix_3char,
            length=len(first_token),
            hyp_prefix_type=prefix_type,
            hyp_base_family=base_family,
            hyp_remainder=remainder,
        )
        records.append(record)

    return records


def analyze_and_print(records: List[FirstTokenRecord]):
    """Analyze collected records and print summary."""

    print("=" * 70)
    print("PHASE 1: First-Token Data Collection Results")
    print("=" * 70)

    # Basic counts
    total = len(records)
    passed = sum(1 for r in records if r.is_pass)
    failed = total - passed

    print(f"\n### Summary ###")
    print(f"Total first tokens: {total}")
    print(f"Passed (A-valid): {passed} ({100*passed/total:.1f}%)")
    print(f"Failed (non-A): {failed} ({100*failed/total:.1f}%)")

    # Prefix type distribution
    print(f"\n### Prefix Type Distribution ###")
    prefix_types = Counter(r.hyp_prefix_type for r in records)
    for ptype, count in prefix_types.most_common():
        pct = 100 * count / total
        examples = [r.token for r in records if r.hyp_prefix_type == ptype][:3]
        print(f"  {ptype:15}: {count:3} ({pct:5.1f}%) - {', '.join(examples)}")

    # Separate analysis for failed tokens
    failed_records = [r for r in records if not r.is_pass]

    print(f"\n### Failed Token Analysis ###")
    print(f"Failed tokens: {len(failed_records)}")

    # 2-char prefix distribution for failed
    print(f"\n2-char prefix distribution (FAILED):")
    prefix2_failed = Counter(r.prefix_2char for r in failed_records)
    for prefix, count in prefix2_failed.most_common(10):
        pct = 100 * count / len(failed_records)
        examples = [r.token for r in failed_records if r.prefix_2char == prefix][:3]
        print(f"  {prefix:4}: {count:3} ({pct:5.1f}%) - {', '.join(examples)}")

    # 2-char suffix distribution for failed
    print(f"\n2-char suffix distribution (FAILED):")
    suffix2_failed = Counter(r.suffix_2char for r in failed_records)
    for suffix, count in suffix2_failed.most_common(10):
        pct = 100 * count / len(failed_records)
        print(f"  -{suffix:4}: {count:3} ({pct:5.1f}%)")

    # C+vowel analysis
    c_vowel_records = [r for r in failed_records if r.hyp_prefix_type == 'C+vowel']
    print(f"\n### C+vowel Pattern Analysis ###")
    print(f"C+vowel tokens: {len(c_vowel_records)} ({100*len(c_vowel_records)/len(failed_records):.1f}% of failed)")

    if c_vowel_records:
        print(f"\nBy hypothesized base family:")
        by_family = Counter(r.hyp_base_family for r in c_vowel_records)
        for family, count in by_family.most_common():
            family_str = family if family else 'UNMAPPED'
            examples = [r.token for r in c_vowel_records if r.hyp_base_family == family][:4]
            print(f"  -> {family_str}: {count} - {', '.join(examples)}")

    # Remainder analysis for ko- tokens specifically
    ko_records = [r for r in records if r.prefix_2char == 'ko']
    if ko_records:
        print(f"\n### ko- Tokens Detailed ###")
        print(f"Count: {len(ko_records)}")
        for r in ko_records:
            print(f"  {r.token:15} remainder={r.hyp_remainder:12} suffix_2={r.suffix_2char}")

    # Passed tokens for comparison
    passed_records = [r for r in records if r.is_pass]
    print(f"\n### Passed Token Analysis ###")
    print(f"Passed tokens: {len(passed_records)}")

    print(f"\n2-char prefix distribution (PASSED):")
    prefix2_passed = Counter(r.prefix_2char for r in passed_records)
    for prefix, count in prefix2_passed.most_common(10):
        pct = 100 * count / len(passed_records)
        examples = [r.token for r in passed_records if r.prefix_2char == prefix][:3]
        print(f"  {prefix:4}: {count:3} ({pct:5.1f}%) - {', '.join(examples)}")

    return records


def save_data(records: List[FirstTokenRecord], output_path: str):
    """Save collected data to JSON for Phase 2-3 analysis."""
    data = {
        'phase': 'first_token_analysis',
        'version': '1.0',
        'total_records': len(records),
        'passed_count': sum(1 for r in records if r.is_pass),
        'failed_count': sum(1 for r in records if not r.is_pass),
        'records': [asdict(r) for r in records],
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"\nData saved to: {output_path}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    records = collect_first_tokens()
    analyze_and_print(records)
    save_data(records, 'C:/git/voynich/phases/exploration/first_token_data.json')
