"""
Prefix Family Analysis - Exploratory

Question: Are do-, so-, sa-, etc. extended forms of the 8 marker families,
or separate families?

Tests:
1. Suffix distribution similarity (do- vs da-, so- vs sh-)
2. Context patterns (what comes before/after)
3. Role distribution (MINIMAL vs DATA ratios)
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path
import math

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'apps' / 'script_explorer'))
from ui.folio_viewer import segment_word_4component, get_a_token_role, KNOWN_SUFFIXES

CURRIER_A_FOLIOS = {
    '100r', '100v', '101r1', '101v2', '102r1', '102r2', '102v1', '102v2',
    '10r', '10v', '11r', '11v', '13r', '13v', '14r', '14v', '15r', '15v',
    '16r', '16v', '17r', '17v', '18r', '18v', '19r', '19v', '1r', '1v',
    '20r', '20v', '21r', '21v', '22r', '22v', '23r', '23v', '24r', '24v',
    '25r', '25v', '27r', '27v', '28r', '28v', '29r', '29v', '2r', '2v',
    '30r', '30v', '32r', '32v', '35r', '35v', '36r', '36v', '37r', '37v',
    '38r', '38v', '3r', '3v', '42r', '42v', '44r', '44v', '45r', '45v',
    '47r', '47v', '49r', '49v', '4r', '4v', '51r', '51v', '52r', '52v',
    '53r', '53v', '54r', '54v', '56r', '56v', '58r', '58v', '5r', '5v',
    '6r', '6v', '7r', '7v', '87r', '87v', '88r', '88v', '89r1', '89r2',
    '89v1', '89v2', '8r', '8v', '90r1', '90r2', '90v1', '90v2', '93r', '93v',
    '96r', '96v', '99r', '99v', '9r', '9v'
}

# Hypothesized family groupings to test
FAMILY_HYPOTHESES = {
    'da-family': ['da', 'do', 'sa', 'so'],  # kernel-light?
    'ch-family': ['ch', 'ck', 'ct'],  # kernel-heavy?
    'sh-family': ['sh', 'sc'],
    'ok-family': ['ok', 'oc'],
    'ot-family': ['ot', 'od'],
    'qo-family': ['qo', 'ko'],
}


def load_tokens():
    """Load all Currier A tokens."""
    data_path = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    tokens = []
    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue
            folio = row.get('folio', '').strip('"').replace('f', '')
            if folio in CURRIER_A_FOLIOS:
                word = row.get('word', '').strip('"')
                if word and not word.startswith('*') and len(word) >= 2:
                    tokens.append({
                        'word': word,
                        'prefix2': word[:2].lower(),
                        'folio': folio,
                        'line': row.get('line', ''),
                    })
    return tokens


def get_suffix(word):
    """Extract suffix from word."""
    _, _, _, suffix = segment_word_4component(word)
    return suffix if suffix else '(none)'


def cosine_similarity(counter1, counter2):
    """Calculate cosine similarity between two frequency distributions."""
    all_keys = set(counter1.keys()) | set(counter2.keys())

    dot = sum(counter1.get(k, 0) * counter2.get(k, 0) for k in all_keys)
    mag1 = math.sqrt(sum(v**2 for v in counter1.values()))
    mag2 = math.sqrt(sum(v**2 for v in counter2.values()))

    if mag1 == 0 or mag2 == 0:
        return 0
    return dot / (mag1 * mag2)


def test_suffix_similarity(tokens):
    """Test 1: Do hypothesized family members have similar suffix distributions?"""
    print("\n" + "=" * 60)
    print("TEST 1: SUFFIX DISTRIBUTION SIMILARITY")
    print("=" * 60)
    print("\nComparing suffix distributions within hypothesized families.")
    print("High similarity suggests same family.\n")

    # Get suffix distribution for each prefix
    prefix_suffixes = defaultdict(Counter)
    for t in tokens:
        prefix = t['prefix2']
        suffix = get_suffix(t['word'])
        prefix_suffixes[prefix][suffix] += 1

    # Compare within hypothesized families
    for family_name, members in FAMILY_HYPOTHESES.items():
        print(f"\n{family_name}:")

        # Filter to members that have data
        active_members = [m for m in members if prefix_suffixes[m]]

        if len(active_members) < 2:
            print("  (insufficient data)")
            continue

        # Pairwise similarity
        for i, m1 in enumerate(active_members):
            for m2 in active_members[i+1:]:
                sim = cosine_similarity(prefix_suffixes[m1], prefix_suffixes[m2])
                count1 = sum(prefix_suffixes[m1].values())
                count2 = sum(prefix_suffixes[m2].values())
                print(f"  {m1} vs {m2}: similarity={sim:.3f}  (n={count1}, {count2})")


def test_role_distribution(tokens):
    """Test 2: Do hypothesized family members have similar MINIMAL/DATA ratios?"""
    print("\n" + "=" * 60)
    print("TEST 2: ROLE DISTRIBUTION (MINIMAL vs DATA)")
    print("=" * 60)
    print("\nIf prefixes are same family, they should have similar role ratios.\n")

    # Get role distribution for each prefix
    prefix_roles = defaultdict(Counter)
    for t in tokens:
        prefix = t['prefix2']
        role = get_a_token_role(t['word'])
        prefix_roles[prefix][role] += 1

    # Show role distribution for all interesting prefixes
    all_prefixes = set()
    for members in FAMILY_HYPOTHESES.values():
        all_prefixes.update(members)

    print(f"  {'Prefix':<8} {'Total':>8} {'MINIMAL':>8} {'DATA':>8} {'%DATA':>8}")
    print("  " + "-" * 44)

    for prefix in sorted(all_prefixes):
        roles = prefix_roles[prefix]
        total = sum(roles.values())
        if total < 10:
            continue
        minimal = roles.get('MINIMAL', 0)
        data = roles.get('DATA', 0)
        pct_data = data / (minimal + data) * 100 if (minimal + data) > 0 else 0
        print(f"  {prefix:<8} {total:>8} {minimal:>8} {data:>8} {pct_data:>7.1f}%")


def test_middle_patterns(tokens):
    """Test 3: Do prefixes have similar middle component patterns?"""
    print("\n" + "=" * 60)
    print("TEST 3: MIDDLE COMPONENT PATTERNS")
    print("=" * 60)
    print("\nWhat middle components appear with each prefix?\n")

    prefix_middles = defaultdict(Counter)
    for t in tokens:
        prefix = t['prefix2']
        _, _, middle, _ = segment_word_4component(t['word'])
        if middle:
            prefix_middles[prefix][middle] += 1

    # Compare da-family
    print("da-family middle components:")
    for prefix in ['da', 'do', 'sa', 'so']:
        middles = prefix_middles[prefix]
        total = sum(middles.values())
        if total < 5:
            continue
        top3 = middles.most_common(5)
        top_str = ", ".join(f"{m}({c})" for m, c in top3)
        print(f"  {prefix}: {top_str}")

    print("\nch-family middle components:")
    for prefix in ['ch', 'ck', 'ct']:
        middles = prefix_middles[prefix]
        total = sum(middles.values())
        if total < 5:
            continue
        top3 = middles.most_common(5)
        top_str = ", ".join(f"{m}({c})" for m, c in top3)
        print(f"  {prefix}: {top_str}")


def test_cross_family_similarity(tokens):
    """Test 4: Compare similarity ACROSS families (should be lower)."""
    print("\n" + "=" * 60)
    print("TEST 4: CROSS-FAMILY COMPARISON")
    print("=" * 60)
    print("\nWithin-family similarity should be HIGHER than cross-family.\n")

    prefix_suffixes = defaultdict(Counter)
    for t in tokens:
        prefix = t['prefix2']
        suffix = get_suffix(t['word'])
        prefix_suffixes[prefix][suffix] += 1

    # Compare da vs ch (should be LOW - different families)
    print("Cross-family comparisons (expect LOW similarity):")
    cross_pairs = [
        ('da', 'ch'), ('da', 'sh'), ('da', 'ok'),
        ('ch', 'qo'), ('sh', 'ok'),
    ]
    for p1, p2 in cross_pairs:
        if prefix_suffixes[p1] and prefix_suffixes[p2]:
            sim = cosine_similarity(prefix_suffixes[p1], prefix_suffixes[p2])
            print(f"  {p1} vs {p2}: similarity={sim:.3f}")

    print("\nWithin-family comparisons (expect HIGH similarity):")
    within_pairs = [
        ('da', 'do'), ('da', 'sa'), ('do', 'so'),
        ('ch', 'ck'), ('ch', 'ct'),
    ]
    for p1, p2 in within_pairs:
        if prefix_suffixes[p1] and prefix_suffixes[p2]:
            sim = cosine_similarity(prefix_suffixes[p1], prefix_suffixes[p2])
            print(f"  {p1} vs {p2}: similarity={sim:.3f}")


def main():
    print("=" * 60)
    print("PREFIX FAMILY ANALYSIS - EXPLORATORY")
    print("=" * 60)
    print("\nQuestion: Are do-, so-, sa-, etc. extended forms of")
    print("the 8 marker families, or separate families?")

    tokens = load_tokens()
    print(f"\nLoaded {len(tokens)} tokens from Currier A")

    test_suffix_similarity(tokens)
    test_role_distribution(tokens)
    test_middle_patterns(tokens)
    test_cross_family_similarity(tokens)

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
