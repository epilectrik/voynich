"""
HT-AZC Boundary Test: Is HT marking label boundaries?

Key observation: AZC shows BOTH line-initial AND line-final enrichment
This is unique - A and B only show line-initial enrichment

Hypothesis: HT in AZC marks LABEL BOUNDARIES (both ends of labels)
"""

import csv
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

DATA_PATH = Path(r"C:\git\voynich\data\transcriptions\interlinear_full_words.txt")

def is_ht_token(token):
    if not token:
        return False
    t = token.lower()
    if t.startswith('y'):
        return True
    if len(t) == 1 and t in 'ydfr':
        return True
    return False

print("Loading data...")
records = []
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        word = row.get('word', '').strip().lower()
        if word and word != 'na' and '*' not in word:
            records.append({
                'token': word,
                'folio': row.get('folio', ''),
                'section': row.get('section', ''),
                'language': row.get('language', ''),
                'placement': row.get('placement', ''),
                'line': row.get('line_number', ''),
                'line_initial': row.get('line_initial', '') == '1',
                'line_final': row.get('line_final', '') == '1',
                'is_ht': is_ht_token(word)
            })

DIAGRAM_PLACEMENTS = {'R', 'R1', 'R2', 'R3', 'C', 'S', 'S1', 'S2', 'Q', 'L', 'L1', 'L2', 'X', 'Y', 'T'}
records_azc = [r for r in records if r['section'] == 'Z' or r['placement'] in DIAGRAM_PLACEMENTS]

print(f"AZC tokens: {len(records_azc)}")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 1: BOTH-BOUNDARY HT (Initial AND Final in same line)")
print("=" * 70)

# Group by folio+line
lines = defaultdict(list)
for r in records_azc:
    key = (r['folio'], r['line'])
    lines[key].append(r)

# Analyze line structures
both_boundary = 0  # Lines with HT at BOTH initial and final
initial_only = 0   # Lines with HT at initial only
final_only = 0     # Lines with HT at final only
no_ht = 0          # Lines with no HT
interior_ht = 0    # Lines with HT only in interior

for key, tokens in lines.items():
    if len(tokens) < 2:
        continue

    def line_sort_key(x):
        line = x.get('line', '0') or '0'
        # Extract numeric prefix for sorting
        num = ''.join(c for c in str(line) if c.isdigit()) or '0'
        return int(num)
    tokens = sorted(tokens, key=line_sort_key)
    first = tokens[0]
    last = tokens[-1]
    interior = tokens[1:-1] if len(tokens) > 2 else []

    first_ht = first['is_ht']
    last_ht = last['is_ht']
    interior_ht_any = any(t['is_ht'] for t in interior)

    if first_ht and last_ht:
        both_boundary += 1
    elif first_ht and not last_ht:
        initial_only += 1
    elif last_ht and not first_ht:
        final_only += 1
    elif interior_ht_any:
        interior_ht += 1
    else:
        no_ht += 1

total_lines = both_boundary + initial_only + final_only + interior_ht + no_ht
print(f"\nLine HT patterns ({total_lines} lines with 2+ tokens):")
print(f"  BOTH boundaries: {both_boundary} ({100*both_boundary/total_lines:.1f}%)")
print(f"  Initial only: {initial_only} ({100*initial_only/total_lines:.1f}%)")
print(f"  Final only: {final_only} ({100*final_only/total_lines:.1f}%)")
print(f"  Interior only: {interior_ht} ({100*interior_ht/total_lines:.1f}%)")
print(f"  No HT: {no_ht} ({100*no_ht/total_lines:.1f}%)")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 2: SHORT LINES (Likely Labels)")
print("=" * 70)

# Short lines are more likely to be labels
short_lines = {k: v for k, v in lines.items() if 1 <= len(v) <= 3}
medium_lines = {k: v for k, v in lines.items() if 4 <= len(v) <= 6}
long_lines = {k: v for k, v in lines.items() if len(v) >= 7}

def ht_rate_in_lines(line_dict):
    total = sum(len(v) for v in line_dict.values())
    ht = sum(sum(1 for t in v if t['is_ht']) for v in line_dict.values())
    return ht / total if total else 0

print(f"\nHT density by line length:")
print(f"  Short (1-3 tokens): {100*ht_rate_in_lines(short_lines):.1f}% ({len(short_lines)} lines)")
print(f"  Medium (4-6 tokens): {100*ht_rate_in_lines(medium_lines):.1f}% ({len(medium_lines)} lines)")
print(f"  Long (7+ tokens): {100*ht_rate_in_lines(long_lines):.1f}% ({len(long_lines)} lines)")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 3: HT IN SINGLE-TOKEN LINES (Pure Labels)")
print("=" * 70)

single_token_lines = [v[0] for v in lines.values() if len(v) == 1]
print(f"\nSingle-token lines: {len(single_token_lines)}")
single_ht = sum(1 for t in single_token_lines if t['is_ht'])
print(f"  HT tokens: {single_ht} ({100*single_ht/len(single_token_lines):.1f}%)")

print("\nTop single-token HT forms:")
single_ht_tokens = [t['token'] for t in single_token_lines if t['is_ht']]
for t, c in Counter(single_ht_tokens).most_common(10):
    print(f"  {t}: {c}")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 4: PLACEMENT-SPECIFIC PATTERNS")
print("=" * 70)

# L placements had highest HT - are they label positions?
for placement in ['L', 'Y', 'C', 'R']:
    p_records = [r for r in records_azc if r['placement'] == placement]
    if len(p_records) < 20:
        continue

    ht_tokens = [r for r in p_records if r['is_ht']]
    if not ht_tokens:
        continue

    init = sum(1 for r in ht_tokens if r['line_initial'])
    fin = sum(1 for r in ht_tokens if r['line_final'])

    print(f"\n{placement} placement ({len(ht_tokens)} HT tokens):")
    print(f"  Line-initial: {100*init/len(ht_tokens):.1f}%")
    print(f"  Line-final: {100*fin/len(ht_tokens):.1f}%")
    print(f"  Top forms: {dict(Counter(r['token'] for r in ht_tokens).most_common(5))}")

# ============================================================================
print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
