"""
KERNEL CHARACTER COVERAGE TEST (Corrected)

The kernel primitives k, h, e are CHARACTERS that appear within tokens,
not standalone tokens themselves.

Question: Does every A record have access to tokens CONTAINING k, h, or e?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("KERNEL CHARACTER COVERAGE TEST (Corrected)")
print("Testing access to tokens CONTAINING kernel characters k, h, e")
print("=" * 70)

# Define kernel characters
KERNEL_CHARS = {'k', 'h', 'e'}

# Build B token data
b_tokens = {}
b_tokens_by_kernel = {char: [] for char in KERNEL_CHARS}

for token in tx.currier_b():
    word = token.word
    if word and word not in b_tokens:
        m = morph.extract(word)
        b_tokens[word] = {
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'has_k': 'k' in word,
            'has_h': 'h' in word,
            'has_e': 'e' in word,
        }
        for char in KERNEL_CHARS:
            if char in word:
                b_tokens_by_kernel[char].append(word)

print(f"\nB tokens: {len(b_tokens)}")
for char in KERNEL_CHARS:
    count = len(b_tokens_by_kernel[char])
    pct = 100 * count / len(b_tokens)
    print(f"  Tokens containing '{char}': {count} ({pct:.1f}%)")

# Show examples
print("\nExample tokens for each kernel character:")
for char in KERNEL_CHARS:
    examples = b_tokens_by_kernel[char][:10]
    print(f"  '{char}': {examples}")

# Build A records
a_records = defaultdict(list)
for token in tx.currier_a():
    key = (token.folio, token.line)
    a_records[key].append(token)

record_morphology = {}
for (folio, line), tokens in a_records.items():
    prefixes = set()
    middles = set()
    suffixes = set()
    for t in tokens:
        m = morph.extract(t.word)
        if m.prefix:
            prefixes.add(m.prefix)
        if m.middle:
            middles.add(m.middle)
        if m.suffix:
            suffixes.add(m.suffix)
    record_morphology[(folio, line)] = (prefixes, middles, suffixes)

# B vocabulary sets for filtering
b_middles = set(info['middle'] for info in b_tokens.values() if info['middle'])
b_prefixes = set(info['prefix'] for info in b_tokens.values() if info['prefix'])
b_suffixes = set(info['suffix'] for info in b_tokens.values() if info['suffix'])

n_records = len(record_morphology)
print(f"\nA records: {n_records}")

# For each A record, determine which kernel characters are accessible
print("\n" + "=" * 70)
print("COMPUTING KERNEL CHARACTER ACCESS PER A RECORD")
print("=" * 70)

record_kernel_access = {}
for (folio, line), (prefixes, middles, suffixes) in record_morphology.items():
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    # Track which kernel characters are accessible via surviving tokens
    accessible_kernels = set()
    surviving_tokens = []

    for word, info in b_tokens.items():
        # MIDDLE filter
        if info['middle'] is None:
            middle_ok = True
        else:
            middle_ok = info['middle'] in pp_middles

        # PREFIX filter
        if info['prefix'] is None:
            prefix_ok = True
        else:
            prefix_ok = info['prefix'] in pp_prefixes

        # SUFFIX filter
        if info['suffix'] is None:
            suffix_ok = True
        else:
            suffix_ok = info['suffix'] in pp_suffixes

        if middle_ok and prefix_ok and suffix_ok:
            surviving_tokens.append(word)
            for char in KERNEL_CHARS:
                if char in word:
                    accessible_kernels.add(char)

    record_kernel_access[(folio, line)] = {
        'kernels': accessible_kernels,
        'token_count': len(surviving_tokens)
    }

# Statistics
print("\n--- Individual Kernel Character Coverage ---")
for char in KERNEL_CHARS:
    count = sum(1 for r in record_kernel_access.values() if char in r['kernels'])
    pct = 100 * count / n_records
    print(f"  '{char}': {count}/{n_records} records ({pct:.1f}%)")

# Union coverage
has_any_kernel = sum(1 for r in record_kernel_access.values() if len(r['kernels']) > 0)
has_all_kernels = sum(1 for r in record_kernel_access.values() if r['kernels'] == KERNEL_CHARS)
has_no_kernel = n_records - has_any_kernel

print(f"\n--- Union Coverage ---")
print(f"  At least one kernel char (k, h, or e): {has_any_kernel}/{n_records} ({100*has_any_kernel/n_records:.1f}%)")
print(f"  All three kernel chars: {has_all_kernels}/{n_records} ({100*has_all_kernels/n_records:.1f}%)")
print(f"  NO kernel chars: {has_no_kernel}/{n_records} ({100*has_no_kernel/n_records:.1f}%)")

# Distribution
print(f"\n--- Distribution of Kernel Character Access ---")
kernel_count_dist = defaultdict(int)
for r in record_kernel_access.values():
    kernel_count_dist[len(r['kernels'])] += 1

for count in sorted(kernel_count_dist.keys()):
    n = kernel_count_dist[count]
    pct = 100 * n / n_records
    print(f"  {count} kernel chars: {n} records ({pct:.1f}%)")

# Examine records with no kernel access
if has_no_kernel > 0:
    print(f"\n" + "=" * 70)
    print(f"EXAMINING {has_no_kernel} RECORDS WITH NO KERNEL CHARACTER ACCESS")
    print("=" * 70)

    no_kernel_records = [(r, record_morphology[r], record_kernel_access[r])
                         for r in record_kernel_access
                         if len(record_kernel_access[r]['kernels']) == 0]

    print("\nSample records with no kernel access:")
    for (folio, line), (prefixes, middles, suffixes), access in no_kernel_records[:10]:
        print(f"\n  {folio}:{line}")
        print(f"    Surviving B tokens: {access['token_count']}")
        print(f"    A-PREFIXes: {prefixes}")
        print(f"    A-MIDDLEs: {len(middles)} total")
        print(f"    A-SUFFIXes: {suffixes}")

# Also check: what about records with ANY surviving tokens?
print(f"\n" + "=" * 70)
print("RECORDS WITH ANY SURVIVING TOKENS")
print("=" * 70)

has_any_tokens = sum(1 for r in record_kernel_access.values() if r['token_count'] > 0)
has_no_tokens = n_records - has_any_tokens

print(f"\nRecords with at least 1 surviving token: {has_any_tokens}/{n_records} ({100*has_any_tokens/n_records:.1f}%)")
print(f"Records with NO surviving tokens: {has_no_tokens}/{n_records} ({100*has_no_tokens/n_records:.1f}%)")

# Token count distribution
print("\nSurviving token count distribution:")
token_count_dist = defaultdict(int)
for r in record_kernel_access.values():
    bucket = r['token_count'] // 10 * 10  # Group by tens
    token_count_dist[bucket] += 1

for bucket in sorted(token_count_dist.keys()):
    n = token_count_dist[bucket]
    pct = 100 * n / n_records
    label = f"{bucket}-{bucket+9}" if bucket < 100 else f"{bucket}+"
    print(f"  {label} tokens: {n} records ({pct:.1f}%)")

# Summary
print("\n" + "=" * 70)
print("SUMMARY: KERNEL CHARACTER COVERAGE (Corrected)")
print("=" * 70)

print(f"""
Kernel characters are k, h, e - they appear WITHIN tokens, not as standalone.

COVERAGE BY CHARACTER:
  'k' (in tokens like ok, qok, kor, kal): {sum(1 for r in record_kernel_access.values() if 'k' in r['kernels'])/n_records*100:.1f}%
  'h' (in tokens like ch, sh, che, she): {sum(1 for r in record_kernel_access.values() if 'h' in r['kernels'])/n_records*100:.1f}%
  'e' (in tokens like che, she, chey): {sum(1 for r in record_kernel_access.values() if 'e' in r['kernels'])/n_records*100:.1f}%

UNION COVERAGE:
  At least one kernel char: {100*has_any_kernel/n_records:.1f}%
  All three kernel chars: {100*has_all_kernels/n_records:.1f}%
  NO kernel chars: {100*has_no_kernel/n_records:.1f}%

ANSWER: {"YES" if has_no_kernel == 0 else "NO"} - {"Every" if has_no_kernel == 0 else "Not every"} A record has access to at least one token containing a kernel character.
""")

if has_no_kernel == 0:
    print("The kernel (k, h, e) IS universally accessible through containing tokens.")
else:
    print(f"WARNING: {has_no_kernel} records ({100*has_no_kernel/n_records:.1f}%) lack kernel character access.")
