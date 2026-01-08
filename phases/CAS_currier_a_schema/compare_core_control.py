"""Compare CORE_CONTROL tokens (daiin, ol) in A vs B."""
from pathlib import Path
from collections import Counter, defaultdict

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Load data
a_tokens = []
b_tokens = []
a_lines = defaultdict(list)
b_lines = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 11:
            word = parts[0].strip('"').strip().lower()
            folio = parts[2].strip('"').strip()
            lang = parts[6].strip('"').strip()
            line_num = parts[11].strip('"').strip()

            if word and lang == 'A':
                a_tokens.append(word)
                a_lines[f'{folio}_{line_num}'].append(word)
            elif word and lang == 'B':
                b_tokens.append(word)
                b_lines[f'{folio}_{line_num}'].append(word)

print("=" * 70)
print("CORE_CONTROL TOKENS: daiin and ol")
print("=" * 70)

# Basic counts
for tok in ['daiin', 'ol']:
    a_ct = a_tokens.count(tok)
    b_ct = b_tokens.count(tok)
    a_pct = 100 * a_ct / len(a_tokens)
    b_pct = 100 * b_ct / len(b_tokens)
    ratio = a_ct / b_ct if b_ct > 0 else float('inf')

    print(f"\n{tok}:")
    print(f"  A: {a_ct} ({a_pct:.2f}%)")
    print(f"  B: {b_ct} ({b_pct:.2f}%)")
    print(f"  A:B ratio: {ratio:.2f}")

# Bigram analysis for both
print("\n" + "=" * 70)
print("BIGRAM ANALYSIS")
print("=" * 70)

for tok in ['daiin', 'ol']:
    print(f"\n--- {tok} ---")

    # A bigrams
    a_before = Counter()
    a_after = Counter()
    for i, t in enumerate(a_tokens):
        if t == tok:
            if i > 0:
                a_before[a_tokens[i-1]] += 1
            if i < len(a_tokens) - 1:
                a_after[a_tokens[i+1]] += 1

    print(f"\nIn A - before {tok}: {a_before.most_common(5)}")
    print(f"In A - after {tok}: {a_after.most_common(5)}")

    # B bigrams
    b_before = Counter()
    b_after = Counter()
    for i, t in enumerate(b_tokens):
        if t == tok:
            if i > 0:
                b_before[b_tokens[i-1]] += 1
            if i < len(b_tokens) - 1:
                b_after[b_tokens[i+1]] += 1

    print(f"\nIn B - before {tok}: {b_before.most_common(5)}")
    print(f"In B - after {tok}: {b_after.most_common(5)}")

# Co-occurrence: do daiin and ol appear together?
print("\n" + "=" * 70)
print("CO-OCCURRENCE: Do daiin and ol appear together?")
print("=" * 70)

# Lines with both
a_both = 0
a_daiin_only = 0
a_ol_only = 0
a_neither = 0

for key, tokens in a_lines.items():
    has_daiin = 'daiin' in tokens
    has_ol = 'ol' in tokens
    if has_daiin and has_ol:
        a_both += 1
    elif has_daiin:
        a_daiin_only += 1
    elif has_ol:
        a_ol_only += 1
    else:
        a_neither += 1

print(f"\nIn A ({len(a_lines)} lines):")
print(f"  Both daiin and ol: {a_both} ({100*a_both/len(a_lines):.1f}%)")
print(f"  daiin only: {a_daiin_only} ({100*a_daiin_only/len(a_lines):.1f}%)")
print(f"  ol only: {a_ol_only} ({100*a_ol_only/len(a_lines):.1f}%)")
print(f"  Neither: {a_neither} ({100*a_neither/len(a_lines):.1f}%)")

b_both = 0
b_daiin_only = 0
b_ol_only = 0
b_neither = 0

for key, tokens in b_lines.items():
    has_daiin = 'daiin' in tokens
    has_ol = 'ol' in tokens
    if has_daiin and has_ol:
        b_both += 1
    elif has_daiin:
        b_daiin_only += 1
    elif has_ol:
        b_ol_only += 1
    else:
        b_neither += 1

print(f"\nIn B ({len(b_lines)} lines):")
print(f"  Both daiin and ol: {b_both} ({100*b_both/len(b_lines):.1f}%)")
print(f"  daiin only: {b_daiin_only} ({100*b_daiin_only/len(b_lines):.1f}%)")
print(f"  ol only: {b_ol_only} ({100*b_ol_only/len(b_lines):.1f}%)")
print(f"  Neither: {b_neither} ({100*b_neither/len(b_lines):.1f}%)")

# Adjacent occurrence (daiin-ol or ol-daiin bigram)
print("\n" + "=" * 70)
print("ADJACENCY: Do daiin and ol appear next to each other?")
print("=" * 70)

a_daiin_ol = sum(1 for i in range(len(a_tokens)-1) if a_tokens[i] == 'daiin' and a_tokens[i+1] == 'ol')
a_ol_daiin = sum(1 for i in range(len(a_tokens)-1) if a_tokens[i] == 'ol' and a_tokens[i+1] == 'daiin')
b_daiin_ol = sum(1 for i in range(len(b_tokens)-1) if b_tokens[i] == 'daiin' and b_tokens[i+1] == 'ol')
b_ol_daiin = sum(1 for i in range(len(b_tokens)-1) if b_tokens[i] == 'ol' and b_tokens[i+1] == 'daiin')

print(f"\nIn A:")
print(f"  daiin -> ol: {a_daiin_ol}")
print(f"  ol -> daiin: {a_ol_daiin}")

print(f"\nIn B:")
print(f"  daiin -> ol: {b_daiin_ol}")
print(f"  ol -> daiin: {b_ol_daiin}")

# Summary
print("\n" + "=" * 70)
print("SYNTHESIS")
print("=" * 70)
print("""
CORE_CONTROL tokens in B grammar: daiin and ol

Both are classified as fundamental control elements in B's executable grammar.
The question: Do they serve similar functions in Currier A?
""")
