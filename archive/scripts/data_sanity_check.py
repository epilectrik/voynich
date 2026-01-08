"""
Data Sanity Check: Verify tokens are real, not parsing artifacts
"""

from collections import Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Sample raw lines to check parsing
print("=" * 80)
print("DATA SANITY CHECK")
print("=" * 80)

# Check 1: Raw line inspection
print("\n### RAW LINE SAMPLES (first 10 data lines)")
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    print(f"Header columns: {len(header.split(chr(9)))}")  # tab character
    print(f"Header: {header[:200]}...")
    print()
    for i, line in enumerate(f):
        if i < 10:
            parts = line.strip().split('\t')
            print(f"Line {i}: {len(parts)} parts")
            print(f"  Word: '{parts[0]}' | Folio: '{parts[2] if len(parts) > 2 else 'N/A'}' | Lang: '{parts[6] if len(parts) > 6 else 'N/A'}'")

# Check 2: Token length distribution
print("\n### TOKEN LENGTH DISTRIBUTION")
lengths = Counter()
short_tokens = []
long_tokens = []
weird_tokens = []

with open(filepath, 'r', encoding='utf-8') as f:
    f.readline()  # skip header
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 0:
            word = parts[0].strip('"').strip().lower()
            if word and not word.startswith('*'):
                lengths[len(word)] += 1
                if len(word) == 1:
                    short_tokens.append(word)
                if len(word) > 15:
                    long_tokens.append(word)
                # Check for weird characters
                if any(c not in 'abcdefghijklmnopqrstuvwxyz*' for c in word):
                    weird_tokens.append(word)

print(f"{'Length':<10} {'Count':>10}")
print("-" * 25)
for length in sorted(lengths.keys())[:20]:
    print(f"{length:<10} {lengths[length]:>10}")

print(f"\n### SINGLE-CHAR TOKENS (first 20 unique)")
print(sorted(set(short_tokens))[:20])

print(f"\n### VERY LONG TOKENS (>15 chars, first 20)")
print(long_tokens[:20])

print(f"\n### TOKENS WITH NON-ALPHA CHARS (first 30)")
print(weird_tokens[:30])

# Check 3: Specific cluster prefix examples
print("\n### CLUSTER PREFIX TOKEN SAMPLES")
cluster_samples = {
    'ckh': [], 'dsh': [], 'cph': [], 'ksh': [], 'tsh': [], 'psh': [],
    'ck': [], 'ds': [], 'cp': [], 'ks': [], 'ts': [], 'ps': []
}

with open(filepath, 'r', encoding='utf-8') as f:
    f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            word = parts[0].strip('"').strip().lower()
            lang = parts[6].strip('"').strip()
            if word and not word.startswith('*') and lang == 'B':
                for prefix in cluster_samples:
                    if word.startswith(prefix) and len(cluster_samples[prefix]) < 10:
                        cluster_samples[prefix].append(word)

for prefix, samples in sorted(cluster_samples.items()):
    if samples:
        print(f"{prefix}: {samples}")

# Check 4: B_SUFFIX_ONLY verification
print("\n### B_SUFFIX_ONLY SAMPLE VERIFICATION")
print("Are these real tokens or fragments?")

B_GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct', 'lch', 'lk', 'ls']
B_GRAMMAR_SUFFIXES = ['aiin', 'ain', 'dy', 'edy', 'eedy', 'ey', 'eey', 'y',
                       'ol', 'or', 'ar', 'al', 'o', 'hy', 'chy']

suffix_only_samples = []
with open(filepath, 'r', encoding='utf-8') as f:
    f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            word = parts[0].strip('"').strip().lower()
            lang = parts[6].strip('"').strip()
            folio = parts[2].strip('"').strip() if len(parts) > 2 else ''

            if word and not word.startswith('*') and lang == 'B':
                has_suffix = any(word.endswith(s) for s in B_GRAMMAR_SUFFIXES)
                has_prefix = any(word.startswith(p) for p in B_GRAMMAR_PREFIXES)

                if has_suffix and not has_prefix and len(suffix_only_samples) < 50:
                    suffix_only_samples.append((word, folio))

print(f"\nSuffix-only tokens with folio context:")
for word, folio in suffix_only_samples[:30]:
    print(f"  {word:<20} ({folio})")

# Check 5: Verify forbidden transition test logic
print("\n### FORBIDDEN TRANSITION LOGIC CHECK")
FORBIDDEN_TRANSITIONS = [
    ('ol', 'qo'), ('ol', 'ok'), ('qo', 'ol'), ('sh', 'ol'),
    ('ot', 'ch'), ('ch', 'ot'), ('da', 'sh'), ('sh', 'da'),
    ('ct', 'qo'), ('qo', 'ct'), ('ok', 'da'), ('da', 'ok'),
    ('ot', 'da'), ('da', 'ot'), ('ct', 'sh'), ('sh', 'ct'),
    ('ct', 'da')
]

print(f"Number of forbidden prefix pairs: {len(FORBIDDEN_TRANSITIONS)}")
print(f"Forbidden pairs: {FORBIDDEN_TRANSITIONS}")

# Actually check if these transitions occur
print("\n### ACTUAL FORBIDDEN TRANSITION OCCURRENCES")
forbidden_counts = Counter()
forbidden_examples = {}

with open(filepath, 'r', encoding='utf-8') as f:
    f.readline()
    prev_word = None
    prev_folio = None
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            word = parts[0].strip('"').strip().lower()
            lang = parts[6].strip('"').strip()
            folio = parts[2].strip('"').strip() if len(parts) > 2 else ''

            if word and not word.startswith('*') and lang == 'B':
                if prev_word and prev_folio == folio:
                    # Check prefix pair
                    for p1, p2 in FORBIDDEN_TRANSITIONS:
                        if prev_word.startswith(p1) and word.startswith(p2):
                            forbidden_counts[(p1, p2)] += 1
                            if (p1, p2) not in forbidden_examples:
                                forbidden_examples[(p1, p2)] = (prev_word, word, folio)

                prev_word = word
                prev_folio = folio

print(f"{'Pair':<15} {'Count':>8} {'Example':<40}")
print("-" * 65)
for pair, count in forbidden_counts.most_common():
    example = forbidden_examples.get(pair, ('?', '?', '?'))
    print(f"{str(pair):<15} {count:>8} {example[0]} -> {example[1]} ({example[2]})")

total_forbidden = sum(forbidden_counts.values())
print(f"\nTotal forbidden transitions found: {total_forbidden}")

print("\n" + "=" * 80)
