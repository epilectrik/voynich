"""Analyze daiin relationships to infer its purpose."""
from pathlib import Path
from collections import Counter, defaultdict
import json

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Load ALL data (A and B) for comparison
all_data = []
a_lines = defaultdict(list)
b_lines = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            # Filter to PRIMARY transcriber (H) only
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            word = parts[0].strip('"').strip().lower()
            folio = parts[2].strip('"').strip()
            section = parts[3].strip('"').strip()
            lang = parts[6].strip('"').strip()
            line_num = parts[11].strip('"').strip()

            if word and lang in ['A', 'B']:
                entry = {'word': word, 'folio': folio, 'section': section,
                         'line': line_num, 'lang': lang}
                all_data.append(entry)

                key = f'{folio}_{line_num}'
                if lang == 'A':
                    a_lines[key].append(entry)
                else:
                    b_lines[key].append(entry)

print("=" * 70)
print("DAIIN RELATIONSHIP ANALYSIS")
print("=" * 70)

# =============================================================================
# 1. BIGRAM ANALYSIS - What comes before/after daiin?
# =============================================================================
print("\n" + "=" * 70)
print("1. BIGRAM ANALYSIS: What tokens appear adjacent to daiin?")
print("=" * 70)

# In Currier A
a_before_daiin = Counter()
a_after_daiin = Counter()
a_tokens = []

for key, entries in a_lines.items():
    tokens = [e['word'] for e in entries]
    a_tokens.extend(tokens)
    for i, tok in enumerate(tokens):
        if tok == 'daiin':
            if i > 0:
                a_before_daiin[tokens[i-1]] += 1
            if i < len(tokens) - 1:
                a_after_daiin[tokens[i+1]] += 1

print("\nIn Currier A:")
print("\nTop 15 tokens BEFORE daiin:")
for tok, ct in a_before_daiin.most_common(15):
    print(f"  {tok} -> daiin: {ct}")

print("\nTop 15 tokens AFTER daiin:")
for tok, ct in a_after_daiin.most_common(15):
    print(f"  daiin -> {tok}: {ct}")

# In Currier B
b_before_daiin = Counter()
b_after_daiin = Counter()
b_tokens = []

for key, entries in b_lines.items():
    tokens = [e['word'] for e in entries]
    b_tokens.extend(tokens)
    for i, tok in enumerate(tokens):
        if tok == 'daiin':
            if i > 0:
                b_before_daiin[tokens[i-1]] += 1
            if i < len(tokens) - 1:
                b_after_daiin[tokens[i+1]] += 1

print("\nIn Currier B:")
print("\nTop 15 tokens BEFORE daiin:")
for tok, ct in b_before_daiin.most_common(15):
    print(f"  {tok} -> daiin: {ct}")

print("\nTop 15 tokens AFTER daiin:")
for tok, ct in b_after_daiin.most_common(15):
    print(f"  daiin -> {tok}: {ct}")

# =============================================================================
# 2. MORPHOLOGICAL FAMILY - Other -iin tokens
# =============================================================================
print("\n" + "=" * 70)
print("2. MORPHOLOGICAL FAMILY: Tokens ending in -iin")
print("=" * 70)

iin_tokens_a = Counter(t for t in a_tokens if t.endswith('iin'))
iin_tokens_b = Counter(t for t in b_tokens if t.endswith('iin'))

print("\nTop 20 -iin tokens in A:")
for tok, ct in iin_tokens_a.most_common(20):
    b_ct = iin_tokens_b.get(tok, 0)
    ratio = ct / b_ct if b_ct > 0 else float('inf')
    print(f"  {tok}: A={ct}, B={b_ct}, A:B={ratio:.2f}")

print("\nTop 20 -iin tokens in B:")
for tok, ct in iin_tokens_b.most_common(20):
    a_ct = iin_tokens_a.get(tok, 0)
    ratio = a_ct / ct if ct > 0 else 0
    print(f"  {tok}: B={ct}, A={a_ct}, A:B={ratio:.2f}")

# =============================================================================
# 3. DAIIN VS OTHER DA- TOKENS
# =============================================================================
print("\n" + "=" * 70)
print("3. DA- FAMILY: How does daiin compare to other da- tokens?")
print("=" * 70)

da_tokens_a = Counter(t for t in a_tokens if t.startswith('da'))
da_tokens_b = Counter(t for t in b_tokens if t.startswith('da'))

print("\nTop 15 da- tokens in A:")
for tok, ct in da_tokens_a.most_common(15):
    print(f"  {tok}: {ct}")

print("\nTop 15 da- tokens in B:")
for tok, ct in da_tokens_b.most_common(15):
    print(f"  {tok}: {ct}")

# =============================================================================
# 4. POSITIONAL ANALYSIS - Where in line does daiin appear?
# =============================================================================
print("\n" + "=" * 70)
print("4. POSITIONAL ANALYSIS: Where does daiin appear in lines?")
print("=" * 70)

a_positions = []  # relative position (0-1)
b_positions = []

for key, entries in a_lines.items():
    tokens = [e['word'] for e in entries]
    if len(tokens) > 1:
        for i, tok in enumerate(tokens):
            if tok == 'daiin':
                rel_pos = i / (len(tokens) - 1)
                a_positions.append(rel_pos)

for key, entries in b_lines.items():
    tokens = [e['word'] for e in entries]
    if len(tokens) > 1:
        for i, tok in enumerate(tokens):
            if tok == 'daiin':
                rel_pos = i / (len(tokens) - 1)
                b_positions.append(rel_pos)

if a_positions:
    print(f"\nIn A: mean position = {sum(a_positions)/len(a_positions):.3f} (0=start, 1=end)")
    # Bin into thirds
    early = sum(1 for p in a_positions if p < 0.33)
    middle = sum(1 for p in a_positions if 0.33 <= p < 0.67)
    late = sum(1 for p in a_positions if p >= 0.67)
    total = len(a_positions)
    print(f"  Early (0-33%): {early} ({100*early/total:.1f}%)")
    print(f"  Middle (33-67%): {middle} ({100*middle/total:.1f}%)")
    print(f"  Late (67-100%): {late} ({100*late/total:.1f}%)")

if b_positions:
    print(f"\nIn B: mean position = {sum(b_positions)/len(b_positions):.3f}")
    early = sum(1 for p in b_positions if p < 0.33)
    middle = sum(1 for p in b_positions if 0.33 <= p < 0.67)
    late = sum(1 for p in b_positions if p >= 0.67)
    total = len(b_positions)
    print(f"  Early (0-33%): {early} ({100*early/total:.1f}%)")
    print(f"  Middle (33-67%): {middle} ({100*middle/total:.1f}%)")
    print(f"  Late (67-100%): {late} ({100*late/total:.1f}%)")

# =============================================================================
# 5. MARKER CORRELATION - Which markers co-occur with daiin?
# =============================================================================
print("\n" + "=" * 70)
print("5. MARKER CORRELATION: Which markers appear in daiin lines?")
print("=" * 70)

markers = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# Lines with daiin vs lines without
daiin_lines_markers = Counter()
non_daiin_lines_markers = Counter()
daiin_line_count = 0
non_daiin_line_count = 0

for key, entries in a_lines.items():
    tokens = [e['word'] for e in entries]
    has_daiin = 'daiin' in tokens

    if has_daiin:
        daiin_line_count += 1
    else:
        non_daiin_line_count += 1

    for tok in tokens:
        if tok == 'daiin':
            continue
        for m in markers:
            if tok.startswith(m):
                if has_daiin:
                    daiin_lines_markers[m] += 1
                else:
                    non_daiin_lines_markers[m] += 1
                break

print("\nMarker frequency in lines WITH daiin:")
for m in markers:
    ct = daiin_lines_markers[m]
    print(f"  {m}: {ct} ({ct/daiin_line_count:.2f} per line)")

print("\nMarker frequency in lines WITHOUT daiin:")
for m in markers:
    ct = non_daiin_lines_markers[m]
    print(f"  {m}: {ct} ({ct/non_daiin_line_count:.2f} per line)")

# Calculate enrichment
print("\nMarker enrichment in daiin lines (ratio vs non-daiin lines):")
for m in markers:
    daiin_rate = daiin_lines_markers[m] / daiin_line_count if daiin_line_count else 0
    non_rate = non_daiin_lines_markers[m] / non_daiin_line_count if non_daiin_line_count else 0
    enrichment = daiin_rate / non_rate if non_rate > 0 else float('inf')
    print(f"  {m}: {enrichment:.2f}x")

# =============================================================================
# 6. SECTION DISTRIBUTION
# =============================================================================
print("\n" + "=" * 70)
print("6. SECTION DISTRIBUTION: Is daiin more common in certain sections?")
print("=" * 70)

section_daiin = Counter()
section_total = Counter()

for key, entries in a_lines.items():
    tokens = [e['word'] for e in entries]
    section = entries[0]['section']
    section_total[section] += len(tokens)
    section_daiin[section] += tokens.count('daiin')

print("\nDaiin frequency by section:")
for section in sorted(section_total.keys()):
    total = section_total[section]
    daiin_ct = section_daiin[section]
    rate = 100 * daiin_ct / total if total else 0
    print(f"  {section}: {daiin_ct}/{total} = {rate:.2f}%")

# =============================================================================
# 7. DAIIN-DAIIN SEQUENCES
# =============================================================================
print("\n" + "=" * 70)
print("7. DAIIN SEQUENCES: What patterns involve consecutive daiin?")
print("=" * 70)

# Find what comes before/after daiin-daiin sequences
before_daiin_daiin = Counter()
after_daiin_daiin = Counter()

for key, entries in a_lines.items():
    tokens = [e['word'] for e in entries]
    for i in range(len(tokens) - 1):
        if tokens[i] == 'daiin' and tokens[i+1] == 'daiin':
            if i > 0:
                before_daiin_daiin[tokens[i-1]] += 1
            if i + 2 < len(tokens):
                after_daiin_daiin[tokens[i+2]] += 1

print("\nTop 10 tokens BEFORE daiin-daiin sequence:")
for tok, ct in before_daiin_daiin.most_common(10):
    print(f"  {tok} -> daiin daiin: {ct}")

print("\nTop 10 tokens AFTER daiin-daiin sequence:")
for tok, ct in after_daiin_daiin.most_common(10):
    print(f"  daiin daiin -> {tok}: {ct}")

# =============================================================================
# 8. COMPARISON: daiin behavior in A vs B
# =============================================================================
print("\n" + "=" * 70)
print("8. A vs B COMPARISON: Does daiin behave differently?")
print("=" * 70)

a_daiin_total = a_tokens.count('daiin')
b_daiin_total = b_tokens.count('daiin')

print(f"\nTotal occurrences:")
print(f"  A: {a_daiin_total} ({100*a_daiin_total/len(a_tokens):.2f}% of A tokens)")
print(f"  B: {b_daiin_total} ({100*b_daiin_total/len(b_tokens):.2f}% of B tokens)")

# Self-repetition rate (daiin-daiin bigram)
a_daiin_daiin = sum(1 for i in range(len(a_tokens)-1)
                    if a_tokens[i] == 'daiin' and a_tokens[i+1] == 'daiin')
b_daiin_daiin = sum(1 for i in range(len(b_tokens)-1)
                    if b_tokens[i] == 'daiin' and b_tokens[i+1] == 'daiin')

print(f"\nSelf-repetition (daiin-daiin bigram):")
print(f"  A: {a_daiin_daiin} ({100*a_daiin_daiin/a_daiin_total:.1f}% of daiin followed by daiin)")
print(f"  B: {b_daiin_daiin} ({100*b_daiin_daiin/b_daiin_total:.1f}% of daiin followed by daiin)")

# Most distinctive contexts
print("\n" + "=" * 70)
print("SYNTHESIS")
print("=" * 70)
