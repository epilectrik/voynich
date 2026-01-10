"""
AZC Prefix Analysis - EVA notation

Check what prefixes actually appear in EVA transcription
and compare across A/B/AZC
"""

import re
from pathlib import Path
from collections import Counter, defaultdict

# Parse EVA transcription
data_path = Path(r"C:\git\voynich\data\transcriptions\voynich_eva.txt")

def parse_eva_file(filepath):
    """Parse EVA transcription into structured data"""
    records = []
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = re.match(r'<(\w+)\.(\d+)>(.+)', line)
            if match:
                folio = match.group(1)
                line_num = int(match.group(2))
                content = match.group(3)
                raw_tokens = re.split(r'[.\s]+', content)
                tokens = []
                for t in raw_tokens:
                    t = re.sub(r'[=\-,!?#@+*(){}[\]<>0-9]', '', t)
                    t = t.lower().strip()
                    if t and len(t) > 0:
                        tokens.append(t)
                for pos, token in enumerate(tokens):
                    records.append({
                        'folio': folio,
                        'line': line_num,
                        'position': pos,
                        'token': token
                    })
    return records

def classify_currier(folio):
    match = re.match(r'f?(\d+)', folio)
    if not match:
        return 'UNK'
    num = int(match.group(1))
    # Zodiac pages
    if 67 <= num <= 73:
        return 'AZC'
    elif 85 <= num <= 86:
        return 'AZC'
    # Currier split
    if num <= 20:
        return 'A'
    elif num <= 116:
        return 'B'
    return 'UNK'

print("Loading EVA transcription...")
records = parse_eva_file(data_path)

for r in records:
    r['currier'] = classify_currier(r['folio'])

records_a = [r for r in records if r['currier'] == 'A']
records_b = [r for r in records if r['currier'] == 'B']
records_azc = [r for r in records if r['currier'] == 'AZC']

print(f"A: {len(records_a)}, B: {len(records_b)}, AZC: {len(records_azc)}")

# Get 2-character prefixes
def get_prefixes(tokens, n=2):
    """Extract n-char prefixes"""
    prefixes = []
    for r in tokens:
        if len(r['token']) >= n:
            prefixes.append(r['token'][:n])
    return Counter(prefixes)

print("\n" + "=" * 60)
print("TOP 20 TWO-CHARACTER PREFIXES")
print("=" * 60)

a_prefixes = get_prefixes(records_a)
b_prefixes = get_prefixes(records_b)
azc_prefixes = get_prefixes(records_azc)

print("\nCurrier A top prefixes:")
for p, c in a_prefixes.most_common(20):
    print(f"  {p}: {c} ({100*c/len(records_a):.1f}%)")

print("\nCurrier B top prefixes:")
for p, c in b_prefixes.most_common(20):
    print(f"  {p}: {c} ({100*c/len(records_b):.1f}%)")

print("\nAZC top prefixes:")
for p, c in azc_prefixes.most_common(20):
    print(f"  {p}: {c} ({100*c/len(records_azc):.1f}%)")

# Find AZC-distinctive prefixes
print("\n" + "=" * 60)
print("AZC-DISTINCTIVE PATTERNS")
print("=" * 60)

# Normalize rates
a_rates = {p: c/len(records_a) for p, c in a_prefixes.items()}
b_rates = {p: c/len(records_b) for p, c in b_prefixes.items()}
azc_rates = {p: c/len(records_azc) for p, c in azc_prefixes.items()}

# Find prefixes enriched in AZC vs B
print("\nPrefixes ENRICHED in AZC vs B:")
for p in azc_prefixes:
    if azc_prefixes[p] >= 10:  # Minimum count
        azc_r = azc_rates.get(p, 0)
        b_r = b_rates.get(p, 0.0001)
        ratio = azc_r / b_r
        if ratio > 1.5:
            print(f"  {p}: AZC={100*azc_r:.1f}%, B={100*b_r:.1f}%, ratio={ratio:.1f}x")

print("\nPrefixes DEPLETED in AZC vs B:")
for p in b_prefixes.most_common(30):
    p = p[0]
    if b_prefixes[p] >= 100:
        azc_r = azc_rates.get(p, 0)
        b_r = b_rates.get(p, 0.0001)
        ratio = b_r / max(azc_r, 0.0001)
        if ratio > 2 and azc_r < b_r:
            print(f"  {p}: B={100*b_r:.1f}%, AZC={100*azc_r:.1f}%, ratio={ratio:.1f}x depleted")

# Check if AZC follows A or B patterns
print("\n" + "=" * 60)
print("AZC AFFINITY: A-LIKE OR B-LIKE?")
print("=" * 60)

# For each AZC prefix, check if rate is closer to A or B
a_affinity = 0
b_affinity = 0
for p, count in azc_prefixes.most_common(30):
    azc_r = azc_rates[p]
    a_r = a_rates.get(p, 0)
    b_r = b_rates.get(p, 0)

    a_dist = abs(azc_r - a_r)
    b_dist = abs(azc_r - b_r)

    if a_dist < b_dist:
        a_affinity += count
    else:
        b_affinity += count

total = a_affinity + b_affinity
print(f"\nPrefix-weighted affinity:")
print(f"  A-like: {a_affinity} ({100*a_affinity/total:.1f}%)")
print(f"  B-like: {b_affinity} ({100*b_affinity/total:.1f}%)")

# Check line position patterns in AZC
print("\n" + "=" * 60)
print("AZC LINE-POSITION PATTERNS")
print("=" * 60)

def analyze_line_positions(tokens, label):
    lines = defaultdict(list)
    for r in tokens:
        lines[(r['folio'], r['line'])].append(r)

    initial = []
    final = []

    for key, line_tokens in lines.items():
        if len(line_tokens) >= 2:
            line_tokens = sorted(line_tokens, key=lambda x: x['position'])
            initial.append(line_tokens[0]['token'])
            final.append(line_tokens[-1]['token'])

    print(f"\n{label} ({len(lines)} lines):")
    print("  Line-initial top 10:")
    for t, c in Counter(initial).most_common(10):
        print(f"    {t}: {c} ({100*c/len(initial):.1f}%)")
    print("  Line-final top 10:")
    for t, c in Counter(final).most_common(10):
        print(f"    {t}: {c} ({100*c/len(final):.1f}%)")

analyze_line_positions(records_b, "Currier B")
analyze_line_positions(records_azc, "AZC")

# Token length distribution
print("\n" + "=" * 60)
print("TOKEN LENGTH DISTRIBUTION")
print("=" * 60)

def length_dist(tokens):
    lengths = [len(r['token']) for r in tokens]
    return Counter(lengths)

for label, tokens in [("A", records_a), ("B", records_b), ("AZC", records_azc)]:
    dist = length_dist(tokens)
    mean_len = sum(l * c for l, c in dist.items()) / sum(dist.values())
    print(f"\n{label}: mean length = {mean_len:.2f}")
    for l in range(1, 10):
        if l in dist:
            print(f"  len={l}: {dist[l]} ({100*dist[l]/len(tokens):.1f}%)")
