"""
AZC Unique Vocabulary Analysis

Find tokens that appear ONLY or predominantly in AZC
"""

import re
from pathlib import Path
from collections import Counter

data_path = Path(r"C:\git\voynich\data\transcriptions\voynich_eva.txt")

def parse_eva_file(filepath):
    records = []
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = re.match(r'<(\w+)\.(\d+)>(.+)', line)
            if match:
                folio = match.group(1)
                content = match.group(3)
                raw_tokens = re.split(r'[.\s]+', content)
                for t in raw_tokens:
                    t = re.sub(r'[=\-,!?#@+*(){}[\]<>0-9]', '', t)
                    t = t.lower().strip()
                    if t and len(t) > 0:
                        records.append({'folio': folio, 'token': t})
    return records

def classify_currier(folio):
    match = re.match(r'f?(\d+)', folio)
    if not match:
        return 'UNK'
    num = int(match.group(1))
    if 67 <= num <= 73 or 85 <= num <= 86:
        return 'AZC'
    if num <= 20:
        return 'A'
    elif num <= 116:
        return 'B'
    return 'UNK'

records = parse_eva_file(data_path)
for r in records:
    r['currier'] = classify_currier(r['folio'])

# Get token counts per system
a_tokens = Counter(r['token'] for r in records if r['currier'] == 'A')
b_tokens = Counter(r['token'] for r in records if r['currier'] == 'B')
azc_tokens = Counter(r['token'] for r in records if r['currier'] == 'AZC')

print("=" * 60)
print("AZC-EXCLUSIVE TOKENS")
print("=" * 60)
print("\nTokens appearing ONLY in AZC (count >= 3):")
azc_exclusive = []
for token, count in azc_tokens.most_common():
    if count >= 3 and token not in a_tokens and token not in b_tokens:
        azc_exclusive.append((token, count))

for t, c in azc_exclusive[:30]:
    print(f"  {t}: {c}")

print(f"\nTotal AZC-exclusive types: {len(azc_exclusive)}")

print("\n" + "=" * 60)
print("AZC-ENRICHED TOKENS")
print("=" * 60)
print("\nTokens with >5x enrichment in AZC vs B (min 3 occurrences):")

azc_total = sum(azc_tokens.values())
b_total = sum(b_tokens.values())

enriched = []
for token, azc_count in azc_tokens.items():
    if azc_count >= 3:
        b_count = b_tokens.get(token, 0)
        azc_rate = azc_count / azc_total
        b_rate = (b_count + 0.5) / b_total  # smoothing
        ratio = azc_rate / b_rate
        if ratio > 5:
            enriched.append((token, azc_count, b_count, ratio))

enriched.sort(key=lambda x: -x[3])
for t, ac, bc, r in enriched[:20]:
    print(f"  {t}: AZC={ac}, B={bc}, ratio={r:.1f}x")

print("\n" + "=" * 60)
print("A-EXCLUSIVE IN AZC")
print("=" * 60)
print("\nTokens that appear in A and AZC but NOT in B:")

a_azc_shared = []
for token in azc_tokens:
    if token in a_tokens and token not in b_tokens:
        a_azc_shared.append((token, a_tokens[token], azc_tokens[token]))

a_azc_shared.sort(key=lambda x: -(x[1] + x[2]))
print(f"Found {len(a_azc_shared)} A+AZC exclusive tokens")
for t, ac, azcc in a_azc_shared[:15]:
    # Filter out tokens with encoding issues
    try:
        t.encode('ascii')
        print(f"  {t}: A={ac}, AZC={azcc}")
    except:
        pass

print("\n" + "=" * 60)
print("VOCABULARY OVERLAP MATRIX")
print("=" * 60)

a_types = set(a_tokens.keys())
b_types = set(b_tokens.keys())
azc_types = set(azc_tokens.keys())

print(f"\nA types: {len(a_types)}")
print(f"B types: {len(b_types)}")
print(f"AZC types: {len(azc_types)}")

print(f"\nA and B: {len(a_types & b_types)} ({100*len(a_types & b_types)/len(a_types | b_types):.1f}%)")
print(f"A and AZC: {len(a_types & azc_types)} ({100*len(a_types & azc_types)/len(a_types | azc_types):.1f}%)")
print(f"B and AZC: {len(b_types & azc_types)} ({100*len(b_types & azc_types)/len(b_types | azc_types):.1f}%)")
print(f"A and B and AZC: {len(a_types & b_types & azc_types)}")

print(f"\nAZC-only: {len(azc_types - a_types - b_types)}")
print(f"A-only: {len(a_types - b_types - azc_types)}")
print(f"B-only: {len(b_types - a_types - azc_types)}")

# System-exclusive vocabulary as % of system
azc_exclusive_pct = len(azc_types - a_types - b_types) / len(azc_types) * 100
a_exclusive_pct = len(a_types - b_types - azc_types) / len(a_types) * 100
b_exclusive_pct = len(b_types - a_types - azc_types) / len(b_types) * 100

print(f"\nExclusive vocabulary rate:")
print(f"  AZC-exclusive: {azc_exclusive_pct:.1f}% of AZC types")
print(f"  A-exclusive: {a_exclusive_pct:.1f}% of A types")
print(f"  B-exclusive: {b_exclusive_pct:.1f}% of B types")
