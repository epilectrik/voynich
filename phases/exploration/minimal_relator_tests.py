"""
Tests for MINIMAL-as-Relator Hypothesis

Predictions:
1. MINIMAL tokens don't cluster (appear between DATA, not adjacent to each other)
2. Bigrams: DATA precedes and follows MINIMAL
3. Specific MINIMAL forms have consistent prefix contexts
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'apps' / 'script_explorer'))
from ui.folio_viewer import segment_word_4component, get_a_token_role, get_a_marker_family

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


def load_lines():
    """Load tokens grouped by line."""
    data_path = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    lines = defaultdict(list)
    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue
            folio = row.get('folio', '').strip('"').replace('f', '')
            if folio in CURRIER_A_FOLIOS:
                word = row.get('word', '').strip('"')
                line_num = row.get('line', '')
                if word and not word.startswith('*'):
                    role = get_a_token_role(word)
                    prefix = get_a_marker_family(word)
                    lines[(folio, line_num)].append({
                        'word': word,
                        'role': role,
                        'prefix': prefix,
                    })
    return lines


def test_clustering(lines):
    """Test 1: Do MINIMAL tokens cluster or appear between DATA?"""
    print("\n" + "=" * 60)
    print("TEST 1: MINIMAL CLUSTERING")
    print("=" * 60)
    print("\nIf MINIMAL are relators, they shouldn't cluster.")
    print("Measuring: What follows a MINIMAL token?\n")

    after_minimal = Counter()
    after_data = Counter()

    for line_tokens in lines.values():
        for i in range(len(line_tokens) - 1):
            curr_role = line_tokens[i]['role']
            next_role = line_tokens[i + 1]['role']

            if curr_role == 'MINIMAL':
                after_minimal[next_role] += 1
            elif curr_role == 'DATA':
                after_data[next_role] += 1

    print("After MINIMAL, next token is:")
    total = sum(after_minimal.values())
    for role, count in after_minimal.most_common():
        pct = count / total * 100 if total > 0 else 0
        print(f"  {role:15s}: {count:5d} ({pct:5.1f}%)")

    print("\nAfter DATA, next token is:")
    total = sum(after_data.values())
    for role, count in after_data.most_common():
        pct = count / total * 100 if total > 0 else 0
        print(f"  {role:15s}: {count:5d} ({pct:5.1f}%)")

    # Calculate MINIMAL-MINIMAL adjacency rate
    mm_rate = after_minimal.get('MINIMAL', 0) / sum(after_minimal.values()) * 100 if after_minimal else 0
    dm_rate = after_data.get('MINIMAL', 0) / sum(after_data.values()) * 100 if after_data else 0

    print(f"\n  MINIMAL -> MINIMAL rate: {mm_rate:.1f}%")
    print(f"  DATA -> MINIMAL rate:    {dm_rate:.1f}%")

    if mm_rate < dm_rate:
        print("\n  [PASS] MINIMAL avoids clustering (supports relator hypothesis)")
    else:
        print("\n  [FAIL] MINIMAL clusters (contradicts relator hypothesis)")


def test_bigram_context(lines):
    """Test 2: What prefix families surround MINIMAL tokens?"""
    print("\n" + "=" * 60)
    print("TEST 2: MINIMAL TOKEN CONTEXT")
    print("=" * 60)
    print("\nWhat prefix families appear before/after MINIMAL tokens?\n")

    before_minimal = Counter()
    after_minimal = Counter()

    for line_tokens in lines.values():
        for i, token in enumerate(line_tokens):
            if token['role'] == 'MINIMAL':
                if i > 0:
                    before_minimal[line_tokens[i-1]['prefix']] += 1
                if i < len(line_tokens) - 1:
                    after_minimal[line_tokens[i+1]['prefix']] += 1

    print("Prefix family BEFORE MINIMAL:")
    total = sum(before_minimal.values())
    for prefix, count in before_minimal.most_common(10):
        pct = count / total * 100 if total > 0 else 0
        print(f"  {prefix:8s}: {count:5d} ({pct:5.1f}%)")

    print("\nPrefix family AFTER MINIMAL:")
    total = sum(after_minimal.values())
    for prefix, count in after_minimal.most_common(10):
        pct = count / total * 100 if total > 0 else 0
        print(f"  {prefix:8s}: {count:5d} ({pct:5.1f}%)")


def test_specific_minimal_contexts(lines):
    """Test 3: Do specific MINIMAL tokens have consistent contexts?"""
    print("\n" + "=" * 60)
    print("TEST 3: SPECIFIC MINIMAL TOKEN PATTERNS")
    print("=" * 60)
    print("\nDo specific MINIMAL forms connect specific prefix types?\n")

    # Track: for each MINIMAL token, what prefix pairs does it connect?
    minimal_bridges = defaultdict(lambda: Counter())

    for line_tokens in lines.values():
        for i, token in enumerate(line_tokens):
            if token['role'] == 'MINIMAL' and i > 0 and i < len(line_tokens) - 1:
                before_prefix = line_tokens[i-1]['prefix']
                after_prefix = line_tokens[i+1]['prefix']
                bridge = f"{before_prefix} -> {after_prefix}"
                minimal_bridges[token['word']][bridge] += 1

    # Show top MINIMAL tokens and their bridging patterns
    top_minimal = ['chol', 'chor', 'shol', 'chy', 'cthy', 'shey', 'shy']

    for word in top_minimal:
        if word in minimal_bridges:
            bridges = minimal_bridges[word]
            total = sum(bridges.values())
            print(f"\n  {word} (n={total}) bridges:")
            for bridge, count in bridges.most_common(5):
                pct = count / total * 100
                print(f"    {bridge:20s}: {count:4d} ({pct:5.1f}%)")


def test_run_lengths(lines):
    """Test 4: What's the typical run length of MINIMAL tokens?"""
    print("\n" + "=" * 60)
    print("TEST 4: RUN LENGTH ANALYSIS")
    print("=" * 60)
    print("\nIf MINIMAL are relators, runs should be short (mostly 1).\n")

    run_lengths = Counter()

    for line_tokens in lines.values():
        current_run = 0
        for token in line_tokens:
            if token['role'] == 'MINIMAL':
                current_run += 1
            else:
                if current_run > 0:
                    run_lengths[current_run] += 1
                current_run = 0
        # Don't forget last run
        if current_run > 0:
            run_lengths[current_run] += 1

    print("  MINIMAL run lengths:")
    total_runs = sum(run_lengths.values())
    for length in sorted(run_lengths.keys())[:10]:
        count = run_lengths[length]
        pct = count / total_runs * 100 if total_runs > 0 else 0
        bar = "#" * int(pct / 2)
        print(f"    {length}: {count:5d} ({pct:5.1f}%) {bar}")

    single_runs = run_lengths.get(1, 0)
    single_pct = single_runs / total_runs * 100 if total_runs > 0 else 0
    print(f"\n  Single MINIMAL tokens: {single_pct:.1f}%")

    if single_pct > 70:
        print("  [PASS] Mostly isolated (supports relator hypothesis)")
    else:
        print("  ? Mixed pattern (needs interpretation)")


def test_mutual_information(lines):
    """Test 5: Is there structure in DATA-MINIMAL-DATA triplets?"""
    print("\n" + "=" * 60)
    print("TEST 5: TRIPLET STRUCTURE (DATA-MINIMAL-DATA)")
    print("=" * 60)
    print("\nAre there preferred DATA-MINIMAL-DATA combinations?\n")

    triplets = Counter()

    for line_tokens in lines.values():
        for i in range(len(line_tokens) - 2):
            if (line_tokens[i]['role'] == 'DATA' and
                line_tokens[i+1]['role'] == 'MINIMAL' and
                line_tokens[i+2]['role'] == 'DATA'):

                t1_prefix = line_tokens[i]['prefix']
                minimal = line_tokens[i+1]['word']
                t3_prefix = line_tokens[i+2]['prefix']

                triplet = f"{t1_prefix}-{minimal}-{t3_prefix}"
                triplets[triplet] += 1

    print("  Most common DATA-MINIMAL-DATA triplets:")
    for triplet, count in triplets.most_common(15):
        print(f"    {triplet:30s}: {count:4d}")

    print(f"\n  Unique triplet patterns: {len(triplets)}")


def main():
    print("=" * 60)
    print("MINIMAL-AS-RELATOR HYPOTHESIS TESTS")
    print("=" * 60)

    lines = load_lines()
    print(f"\nLoaded {len(lines)} lines from Currier A")

    test_clustering(lines)
    test_bigram_context(lines)
    test_run_lengths(lines)
    test_specific_minimal_contexts(lines)
    test_mutual_information(lines)

    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
