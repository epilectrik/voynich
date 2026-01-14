"""
Phase S2: Single-Token A Line AZC Projection Impact

Question: Do these 10 tokens activate distinct AZC compatibility profiles?

If they trigger BROAD EXCLUSION despite having no companions,
they are "constraint activators" - mode switches, not materials.

Tests:
1. AZC folio presence (do they appear in AZC at all?)
2. AZC compatibility profile (what do they allow/forbid?)
3. Comparison to normal A tokens (are they disproportionately restrictive?)
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

# The 10 single-token line tokens (from previous analysis)
SINGLE_TOKENS = [
    'ydaraishy', 'dchaiin', 'okokchodm', 'sorain', 'samchorly',
    'okchodeey', 'sotoiiin', 'daramdal', 'ykyd', 'ker'
]


def load_all_data():
    """Load token distributions across A, B, AZC systems."""
    a_tokens = defaultdict(list)  # token -> [(folio, line)]
    b_tokens = defaultdict(list)
    azc_tokens = defaultdict(list)

    a_folio_tokens = defaultdict(set)  # folio -> set of tokens
    azc_folio_tokens = defaultdict(set)

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            folio = row['folio']
            lang = row.get('language', '')
            line_num = row.get('line_number', '0')

            if lang == 'A':
                a_tokens[token].append((folio, line_num))
                a_folio_tokens[folio].add(token)
            elif lang == 'B':
                b_tokens[token].append((folio, line_num))
            elif lang == 'NA':  # AZC
                azc_tokens[token].append((folio, line_num))
                azc_folio_tokens[folio].add(token)

    return a_tokens, b_tokens, azc_tokens, a_folio_tokens, azc_folio_tokens


def test_azc_presence(single_tokens, azc_tokens, a_tokens):
    """Test 1: Do single-token line tokens appear in AZC?"""
    print("="*70)
    print("TEST 1: AZC PRESENCE")
    print("="*70)

    print(f"\nChecking if single-token line tokens appear in AZC system:")
    print(f"{'Token':<15} {'In A':<8} {'In AZC':<8} {'In Both':<8}")
    print("-"*45)

    in_azc_count = 0
    for token in single_tokens:
        in_a = len(a_tokens.get(token, []))
        in_azc = len(azc_tokens.get(token, []))
        in_both = "YES" if in_a > 0 and in_azc > 0 else "NO"

        if in_azc > 0:
            in_azc_count += 1

        print(f"{token:<15} {in_a:<8} {in_azc:<8} {in_both:<8}")

    print(f"\nSingle-token line tokens appearing in AZC: {in_azc_count}/{len(single_tokens)}")

    # Compare to random A tokens
    all_a_tokens = list(a_tokens.keys())
    sample_size = min(100, len(all_a_tokens))
    sample = np.random.choice(all_a_tokens, sample_size, replace=False)

    sample_in_azc = sum(1 for t in sample if len(azc_tokens.get(t, [])) > 0)

    print(f"Random A token sample in AZC: {sample_in_azc}/{sample_size} ({100*sample_in_azc/sample_size:.1f}%)")

    return in_azc_count


def test_morphological_compatibility(single_tokens, a_tokens, azc_tokens):
    """Test 2: Check MIDDLE compatibility patterns."""
    print("\n" + "="*70)
    print("TEST 2: MORPHOLOGICAL STRUCTURE")
    print("="*70)

    # Extract MIDDLE (approximate: chars 2:-2 for tokens >= 4 chars)
    def get_middle(token):
        if len(token) >= 4:
            return token[2:-2] if len(token) > 4 else token[2:-1]
        return token

    def get_prefix(token):
        return token[:2] if len(token) >= 2 else token

    def get_suffix(token):
        return token[-2:] if len(token) >= 2 else token

    print(f"\nMorphological decomposition of single-token line tokens:")
    print(f"{'Token':<15} {'Prefix':<8} {'Middle':<12} {'Suffix':<8}")
    print("-"*50)

    for token in single_tokens:
        prefix = get_prefix(token)
        middle = get_middle(token)
        suffix = get_suffix(token)
        print(f"{token:<15} {prefix:<8} {middle:<12} {suffix:<8}")

    # Check if these MIDDLEs appear elsewhere
    print(f"\nMIDDLE reuse analysis:")

    single_middles = set(get_middle(t) for t in single_tokens)

    for middle in single_middles:
        # Count tokens with this MIDDLE
        matches = [t for t in a_tokens.keys() if get_middle(t) == middle]
        print(f"  '{middle}': {len(matches)} tokens in A corpus")


def test_folio_cooccurrence(single_tokens, a_tokens, a_folio_tokens, azc_folio_tokens):
    """Test 3: Which folios contain these tokens, and what else is there?"""
    print("\n" + "="*70)
    print("TEST 3: FOLIO CO-OCCURRENCE ANALYSIS")
    print("="*70)

    for token in single_tokens:
        occurrences = a_tokens.get(token, [])
        if not occurrences:
            continue

        print(f"\n{token}:")
        for folio, line in occurrences:
            # What else is in this folio?
            other_tokens = a_folio_tokens[folio] - {token}
            azc_in_folio = azc_folio_tokens.get(folio, set())

            print(f"  Folio {folio}, line {line}")
            print(f"    Other A tokens in folio: {len(other_tokens)}")
            print(f"    AZC tokens in folio: {len(azc_in_folio)}")

            # Sample of other tokens
            if other_tokens:
                sample = list(other_tokens)[:5]
                print(f"    Sample A neighbors: {', '.join(sample)}")


def test_exclusivity_profile(single_tokens, a_tokens):
    """Test 4: Compute exclusivity metrics for these tokens."""
    print("\n" + "="*70)
    print("TEST 4: EXCLUSIVITY PROFILE")
    print("="*70)

    # For each single-token line token, check:
    # - How many folios does it appear in?
    # - How exclusive is its vocabulary neighborhood?

    print(f"\nFolio exclusivity:")
    print(f"{'Token':<15} {'Folios':<8} {'Lines':<8} {'Exclusive?':<12}")
    print("-"*50)

    for token in single_tokens:
        occurrences = a_tokens.get(token, [])
        folios = set(f for f, l in occurrences)
        n_lines = len(occurrences)

        # A token is "exclusive" if it appears in only 1 folio
        exclusive = "YES" if len(folios) == 1 else "NO"

        print(f"{token:<15} {len(folios):<8} {n_lines:<8} {exclusive:<12}")

    # Compare to general A exclusivity
    folio_counts = []
    for token, occs in a_tokens.items():
        if len(occs) > 0:
            n_folios = len(set(f for f, l in occs))
            folio_counts.append(n_folios)

    single_folio_rate = sum(1 for c in folio_counts if c == 1) / len(folio_counts)
    print(f"\nGeneral A single-folio exclusivity rate: {100*single_folio_rate:.1f}%")

    single_token_exclusive = sum(1 for t in single_tokens if len(set(f for f, l in a_tokens.get(t, []))) == 1)
    print(f"Single-token line exclusivity rate: {100*single_token_exclusive/len(single_tokens):.1f}%")


def test_adjacency_patterns(single_tokens, a_tokens, a_folio_tokens):
    """Test 5: What appears adjacent to these tokens?"""
    print("\n" + "="*70)
    print("TEST 5: ADJACENCY PATTERNS")
    print("="*70)

    # Load line-level data to check what's on adjacent lines
    line_data = defaultdict(list)  # (folio, line_num) -> [tokens]

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            lang = row.get('language', '')
            if lang != 'A':
                continue

            folio = row['folio']
            line_str = row.get('line_number', '0')
            try:
                line_num = int(line_str)
            except ValueError:
                line_num = int(''.join(c for c in line_str if c.isdigit()) or '0')

            line_data[(folio, line_num)].append(token)

    print(f"\nAdjacent line analysis:")

    for token in single_tokens:
        occurrences = a_tokens.get(token, [])
        if not occurrences:
            continue

        print(f"\n{token}:")
        for folio, line_str in occurrences:
            line_num = int(line_str)

            # Previous line
            prev_tokens = line_data.get((folio, line_num - 1), [])
            # Next line
            next_tokens = line_data.get((folio, line_num + 1), [])

            print(f"  Line {line_num} in {folio}:")
            print(f"    Prev line ({line_num-1}): {len(prev_tokens)} tokens - {prev_tokens[:3] if prev_tokens else 'NONE'}...")
            print(f"    Next line ({line_num+1}): {len(next_tokens)} tokens - {next_tokens[:3] if next_tokens else 'NONE'}...")


def main():
    print("Loading data...")
    a_tokens, b_tokens, azc_tokens, a_folio_tokens, azc_folio_tokens = load_all_data()

    print(f"A vocabulary: {len(a_tokens)} unique tokens")
    print(f"AZC vocabulary: {len(azc_tokens)} unique tokens")
    print(f"Single-token line tokens to analyze: {len(SINGLE_TOKENS)}")

    # Run tests
    azc_count = test_azc_presence(SINGLE_TOKENS, azc_tokens, a_tokens)
    test_morphological_compatibility(SINGLE_TOKENS, a_tokens, azc_tokens)
    test_folio_cooccurrence(SINGLE_TOKENS, a_tokens, a_folio_tokens, azc_folio_tokens)
    test_exclusivity_profile(SINGLE_TOKENS, a_tokens)
    test_adjacency_patterns(SINGLE_TOKENS, a_tokens, a_folio_tokens)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY: AZC PROJECTION IMPACT")
    print("="*70)

    if azc_count == 0:
        print("""
FINDING: Single-token line tokens DO NOT appear in AZC.

This suggests they are NOT participating in the AZC compatibility filter.
They may be:
  - Registry control primitives (mode switches)
  - Structural markers (section boundaries)
  - Meta-level operators (not subject to AZC filtering)

This is CONSISTENT with them being "constraint activators" that
operate ABOVE the normal A→AZC→B pipeline.
""")
    else:
        print(f"""
FINDING: {azc_count}/{len(SINGLE_TOKENS)} single-token line tokens appear in AZC.

Further investigation needed to determine their compatibility profiles.
""")


if __name__ == '__main__':
    main()
