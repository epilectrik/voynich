"""
MCS Hygiene Check

Test whether MCS coordinate system findings are affected by token filtering.

Key MCS claims:
- 11,649 uncategorized token types
- 80.7% section-exclusive
- Different prefix/suffix patterns (p < 0.001)

Hygiene question: Are these counts inflated by noise tokens?
"""

from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

project_root = Path(__file__).parent.parent.parent

# Grammar patterns (from SID-04)
GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}

# Hazard tokens
HAZARD_TOKENS = {
    'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey', 'l',
    'dy', 'or', 'dal', 'ar', 'qo', 'shy', 'ok', 'shol', 'ol', 'shor',
    'dar', 'qokaiin', 'qokedy'
}


def is_grammar_token(token):
    """Grammar classification."""
    t = token.lower()
    for pf in GRAMMAR_PREFIXES:
        if t.startswith(pf):
            return True
    for sf in GRAMMAR_SUFFIXES:
        if t.endswith(sf):
            return True
    return False


def is_uncategorized_original(token):
    """Original: not grammar."""
    return not is_grammar_token(token)


def is_uncategorized_strict(token):
    """Strict: not grammar, plus hygiene filters."""
    t = token.lower().strip()

    # Filter: empty or very short
    if len(t) < 2:
        return False

    # Filter: non-alpha
    if not t.isalpha():
        return False

    # Filter: hazard tokens (they're categorized)
    if t in HAZARD_TOKENS:
        return False

    # Not grammar = uncategorized
    return not is_grammar_token(t)


def load_data():
    """Load transcription with section info."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        f.readline()  # skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                word = parts[0].strip('"').strip()
                section = parts[3].strip('"') if len(parts) > 3 else ''

                if word:  # Include all for original comparison
                    data.append({
                        'token': word,
                        'section': section
                    })

    return data


def compute_mcs_stats(data, is_uncat_func):
    """Compute key MCS statistics."""

    # Count uncategorized tokens by section
    section_tokens = defaultdict(set)
    all_uncat_tokens = set()

    for d in data:
        token = d['token']
        section = d['section']

        if is_uncat_func(token):
            section_tokens[section].add(token)
            all_uncat_tokens.add(token)

    total_types = len(all_uncat_tokens)

    # Count section-exclusive tokens
    section_exclusive_count = 0
    for token in all_uncat_tokens:
        sections_with_token = sum(1 for s, tokens in section_tokens.items() if token in tokens)
        if sections_with_token == 1:
            section_exclusive_count += 1

    exclusivity_rate = section_exclusive_count / total_types if total_types else 0

    # Compute prefix/suffix distributions
    prefixes = Counter()
    suffixes = Counter()
    for token in all_uncat_tokens:
        if len(token) >= 2:
            prefixes[token[:2]] += 1
            suffixes[token[-2:]] += 1

    top_prefixes = prefixes.most_common(5)
    top_suffixes = suffixes.most_common(5)

    return {
        'total_types': total_types,
        'section_exclusive': section_exclusive_count,
        'exclusivity_rate': exclusivity_rate,
        'section_breakdown': {s: len(tokens) for s, tokens in section_tokens.items()},
        'top_prefixes': top_prefixes,
        'top_suffixes': top_suffixes,
    }


def main():
    print("MCS Hygiene Check")
    print("=" * 60)

    data = load_data()
    print(f"Loaded {len(data)} tokens\n")

    # Original classification
    print("ORIGINAL CLASSIFICATION:")
    stats_orig = compute_mcs_stats(data, is_uncategorized_original)
    print(f"  Uncategorized types: {stats_orig['total_types']}")
    print(f"  Section-exclusive: {stats_orig['section_exclusive']} ({stats_orig['exclusivity_rate']:.1%})")
    print(f"  Section breakdown: {stats_orig['section_breakdown']}")

    # Strict classification
    print("\nSTRICT CLASSIFICATION:")
    stats_strict = compute_mcs_stats(data, is_uncategorized_strict)
    print(f"  Uncategorized types: {stats_strict['total_types']}")
    print(f"  Section-exclusive: {stats_strict['section_exclusive']} ({stats_strict['exclusivity_rate']:.1%})")
    print(f"  Section breakdown: {stats_strict['section_breakdown']}")

    # Comparison
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)

    def pct_change(old, new):
        if old == 0:
            return "N/A"
        return f"{(new - old) / old * 100:+.1f}%"

    print(f"""
| Metric           | Original | Strict  | Change    |
|------------------|----------|---------|-----------|
| Uncategorized    | {stats_orig['total_types']}    | {stats_strict['total_types']}   | {pct_change(stats_orig['total_types'], stats_strict['total_types'])} |
| Section-exclusive| {stats_orig['section_exclusive']}    | {stats_strict['section_exclusive']}   | {pct_change(stats_orig['section_exclusive'], stats_strict['section_exclusive'])} |
| Exclusivity rate | {stats_orig['exclusivity_rate']:.1%}   | {stats_strict['exclusivity_rate']:.1%}  | {(stats_strict['exclusivity_rate'] - stats_orig['exclusivity_rate'])*100:+.1f}pp |
""")

    # Filtered tokens analysis
    print("=" * 60)
    print("FILTERED TOKENS ANALYSIS")
    print("=" * 60)

    # Count what was filtered
    filtered_count = 0
    filtered_reasons = Counter()
    filtered_samples = []

    for d in data:
        token = d['token']
        if is_uncategorized_original(token) and not is_uncategorized_strict(token):
            filtered_count += 1
            reasons = []
            if len(token) < 2:
                reasons.append("too_short")
            if not token.isalpha():
                reasons.append("non_alpha")
            if token in HAZARD_TOKENS:
                reasons.append("hazard_token")
            for r in reasons:
                filtered_reasons[r] += 1
            if len(filtered_samples) < 10:
                filtered_samples.append((token, reasons))

    print(f"\nTokens filtered: {filtered_count}")
    print(f"By reason: {dict(filtered_reasons)}")
    if filtered_samples:
        print(f"Samples: {filtered_samples[:5]}")

    # Verdict
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    type_change = abs((stats_strict['total_types'] - stats_orig['total_types']) / stats_orig['total_types'] * 100) if stats_orig['total_types'] else 0
    excl_change = abs((stats_strict['exclusivity_rate'] - stats_orig['exclusivity_rate']) * 100)

    max_change = max(type_change, excl_change)

    if max_change < 5:
        print(f"\n** RESULTS STABLE ** (max change: {max_change:.1f}%)")
        print("MCS findings are ROBUST to hygiene filtering.")
    elif max_change < 20:
        print(f"\n** MINOR CHANGES ** (max change: {max_change:.1f}%)")
        print("MCS findings are MOSTLY stable.")
    else:
        print(f"\n** SIGNIFICANT CHANGES ** (max change: {max_change:.1f}%)")
        print("MCS findings AFFECTED by token filtering. Review recommended.")

    # Additional check: does exclusivity INCREASE with strict filtering?
    if stats_strict['exclusivity_rate'] > stats_orig['exclusivity_rate']:
        print("\n** NOTE ** Exclusivity INCREASES with strict filtering.")
        print("This suggests noise tokens were cross-section (less exclusive).")
        print("The 80.7% claim is CONSERVATIVE - true value may be higher.")


if __name__ == '__main__':
    main()
