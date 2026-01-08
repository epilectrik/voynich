"""
Token-by-token decoder for a Currier A folio.
Attempt to assign structural purpose to EVERY particle.
"""

from collections import defaultdict, Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Known structural components
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SUFFIXES = [
    'daiin', 'aiin', 'aiiin', 'ain', 'in',
    'dy', 'edy', 'ody', 'eedy',
    'or', 'eor', 'ar',
    'ol', 'eol', 'al',
    'chy', 'hy', 'y', 'ey', 'eey',
    'am', 'om',
]

# Structural primitives
STRUCTURAL_PRIMITIVES = ['daiin', 'ol', 'aiin', 'chol', 'chor', 'shol', 'shor']


def get_prefix(token):
    """Identify prefix family."""
    for p in PREFIXES:
        if token.startswith(p):
            return p
    return None


def get_suffix(token):
    """Identify suffix."""
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if token.endswith(s):
            return s
    return None


def classify_token(token):
    """Classify a single token."""
    # Check if it's a known structural primitive
    if token in STRUCTURAL_PRIMITIVES:
        return 'STRUCTURAL_PRIMITIVE', token, None, None

    prefix = get_prefix(token)
    suffix = get_suffix(token)

    if prefix and suffix:
        # Extract middle
        middle_start = len(prefix)
        middle_end = len(token) - len(suffix)
        middle = token[middle_start:middle_end] if middle_end > middle_start else ''
        return 'MARKER_TOKEN', prefix, middle, suffix
    elif prefix:
        # Has prefix but unknown suffix
        remainder = token[len(prefix):]
        return 'PREFIX_ONLY', prefix, remainder, None
    elif suffix:
        # Has suffix but unknown prefix
        remainder = token[:-len(suffix)] if suffix else token
        return 'SUFFIX_ONLY', None, remainder, suffix
    else:
        # Unknown structure
        return 'UNKNOWN', None, token, None


def load_folio(folio_id):
    """Load all tokens from a specific folio."""
    lines = defaultdict(list)

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 6:
                lang = parts[6].strip('"').strip()
                if lang == 'A':
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    if folio == folio_id:
                        word = parts[0].strip('"').strip().lower()
                        line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''
                        if word:
                            lines[line_num].append(word)

    return dict(lines)


def detect_repetition(tokens):
    """Detect if tokens form a repeating block."""
    n = len(tokens)
    if n < 4:
        return None, 0

    for block_size in range(1, n // 2 + 1):
        if n % block_size == 0:
            count = n // block_size
            if count >= 2:
                block = tokens[:block_size]
                matches = True
                for i in range(1, count):
                    chunk = tokens[i * block_size:(i + 1) * block_size]
                    mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
                    if mismatches > len(block) * 0.2:
                        matches = False
                        break
                if matches:
                    return block, count
    return None, 0


def analyze_folio(folio_id):
    """Complete token-by-token analysis of a folio."""
    lines = load_folio(folio_id)

    if not lines:
        print(f"Folio {folio_id} not found or empty")
        return

    print("=" * 80)
    print(f"TOKEN-BY-TOKEN ANALYSIS: {folio_id}")
    print("=" * 80)

    total_tokens = sum(len(toks) for toks in lines.values())
    print(f"\nTotal tokens: {total_tokens}")
    print(f"Total lines: {len(lines)}")

    # Statistics
    classifications = Counter()
    prefixes_found = Counter()
    suffixes_found = Counter()
    unknowns = []

    print("\n" + "=" * 80)
    print("LINE-BY-LINE ANALYSIS")
    print("=" * 80)

    for line_num in sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        tokens = lines[line_num]
        print(f"\n### LINE {line_num}: {' '.join(tokens)}")

        # Check for repetition
        block, rep_count = detect_repetition(tokens)
        if block:
            print(f"    [REPEATING BLOCK x{rep_count}]: {' '.join(block)}")

        # Classify each token
        print(f"    TOKEN BREAKDOWN:")
        for i, token in enumerate(tokens):
            cls, prefix, middle, suffix = classify_token(token)
            classifications[cls] += 1

            if prefix:
                prefixes_found[prefix] += 1
            if suffix:
                suffixes_found[suffix] += 1

            # Format the classification
            if cls == 'STRUCTURAL_PRIMITIVE':
                desc = f"PRIMITIVE ({prefix})"
            elif cls == 'MARKER_TOKEN':
                mid_str = f"+ [{middle}]" if middle else ""
                desc = f"{prefix.upper()}-family {mid_str} + -{suffix}"
            elif cls == 'PREFIX_ONLY':
                desc = f"{prefix.upper()}-family + UNKNOWN_TAIL({middle})"
            elif cls == 'SUFFIX_ONLY':
                desc = f"UNKNOWN_HEAD({middle}) + -{suffix}"
            else:
                desc = f"UNCLASSIFIED: {middle}"
                unknowns.append(token)

            print(f"      [{i+1}] {token:20} -> {desc}")

    # Summary
    print("\n" + "=" * 80)
    print("CLASSIFICATION SUMMARY")
    print("=" * 80)

    print(f"\nBy classification type:")
    for cls, count in classifications.most_common():
        pct = 100 * count / total_tokens
        print(f"  {cls}: {count} ({pct:.1f}%)")

    print(f"\nBy prefix family:")
    for prefix, count in prefixes_found.most_common():
        pct = 100 * count / total_tokens
        print(f"  {prefix.upper()}: {count} ({pct:.1f}%)")

    print(f"\nBy suffix:")
    for suffix, count in suffixes_found.most_common()[:10]:
        pct = 100 * count / total_tokens
        print(f"  -{suffix}: {count} ({pct:.1f}%)")

    if unknowns:
        print(f"\nUNCLASSIFIED TOKENS ({len(unknowns)}):")
        for u in set(unknowns):
            print(f"  {u}")

    # Coverage
    classified = sum(c for cls, c in classifications.items() if cls != 'UNKNOWN')
    coverage = 100 * classified / total_tokens
    print(f"\n" + "=" * 80)
    print(f"COVERAGE: {classified}/{total_tokens} = {coverage:.1f}%")
    print("=" * 80)

    return classifications, unknowns


def list_folios():
    """List all Currier A folios with token counts."""
    folios = defaultdict(list)

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 6:
                lang = parts[6].strip('"').strip()
                if lang == 'A':
                    word = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    if word and folio:
                        folios[folio].append(word)

    print("CURRIER A FOLIOS BY TOKEN COUNT:")
    print("-" * 40)
    for folio, toks in sorted(folios.items(), key=lambda x: len(x[1])):
        print(f"  {folio}: {len(toks)} tokens")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        folio_id = sys.argv[1]
        analyze_folio(folio_id)
    else:
        list_folios()
