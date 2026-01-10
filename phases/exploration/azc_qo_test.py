"""
AZC qo-escape test - Fixed EVA parsing

Check if qo-prefix (escape route) pattern holds in AZC
"""

import re
from pathlib import Path
from collections import Counter

data_path = Path(r"C:\git\voynich\data\transcriptions\voynich_eva.txt")

def parse_eva_file(filepath):
    """Parse EVA - keep digits, they're part of the alphabet"""
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

                # Split on . and spaces, but KEEP digits in tokens
                raw_tokens = re.split(r'[.\s]+', content)
                tokens = []
                for t in raw_tokens:
                    # Only remove punctuation markers, NOT digits
                    t = re.sub(r'[=\-,!?#@+*(){}[\]<>]', '', t)
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
    if 67 <= num <= 73 or 85 <= num <= 86:
        return 'AZC'
    if num <= 20:
        return 'A'
    elif num <= 116:
        return 'B'
    return 'UNK'

print("Loading EVA transcription (keeping digits)...")
records = parse_eva_file(data_path)

for r in records:
    r['currier'] = classify_currier(r['folio'])

records_a = [r for r in records if r['currier'] == 'A']
records_b = [r for r in records if r['currier'] == 'B']
records_azc = [r for r in records if r['currier'] == 'AZC']

print(f"A: {len(records_a)}, B: {len(records_b)}, AZC: {len(records_azc)}")

# Show sample tokens to verify
print("\nSample tokens (first 20):")
for r in records[:20]:
    try:
        r['token'].encode('ascii')
        print(f"  {r['folio']}.{r['line']}: {r['token']}")
    except:
        print(f"  {r['folio']}.{r['line']}: [non-ascii]")

# Check what characters appear in tokens
all_chars = set()
for r in records:
    for c in r['token']:
        try:
            c.encode('ascii')
            all_chars.add(c)
        except:
            pass
print(f"\nCharacter set ({len(all_chars)} ascii chars): {sorted(all_chars)}")

# Now look for qo- and related prefixes
print("\n" + "=" * 60)
print("PREFIX ANALYSIS (with digits)")
print("=" * 60)

def get_prefixes(tokens, n=2):
    prefixes = []
    for r in tokens:
        if len(r['token']) >= n:
            prefixes.append(r['token'][:n])
    return Counter(prefixes)

b_prefixes = get_prefixes(records_b)
a_prefixes = get_prefixes(records_a)
azc_prefixes = get_prefixes(records_azc)

# Look for q-related prefixes
def safe_print(p, c, total):
    try:
        p.encode('ascii')
        print(f"  {p}: {c} ({100*c/total:.2f}%)")
    except:
        pass

print("\nQ-related prefixes in B:")
for p, c in b_prefixes.most_common(100):
    if 'q' in p or '9' in p:
        safe_print(p, c, len(records_b))

print("\nQ-related prefixes in A:")
for p, c in a_prefixes.most_common(100):
    if 'q' in p or '9' in p:
        safe_print(p, c, len(records_a))

print("\nQ-related prefixes in AZC:")
for p, c in azc_prefixes.most_common(100):
    if 'q' in p or '9' in p:
        safe_print(p, c, len(records_azc))

# Top 15 prefixes per system
print("\n" + "=" * 60)
print("TOP 15 PREFIXES PER SYSTEM")
print("=" * 60)

print("\nCurrier B:")
for p, c in b_prefixes.most_common(15):
    safe_print(p, c, len(records_b))

print("\nCurrier A:")
for p, c in a_prefixes.most_common(15):
    safe_print(p, c, len(records_a))

print("\nAZC:")
for p, c in azc_prefixes.most_common(15):
    safe_print(p, c, len(records_azc))

# Look for specific escape-route patterns
print("\n" + "=" * 60)
print("ESCAPE ROUTE PATTERNS")
print("=" * 60)

# Common escape prefixes in Voynich: qo, do, so, etc.
escape_prefixes = ['qo', 'do', 'so', '9o', 'd9', 's9']

for prefix in escape_prefixes:
    b_count = sum(1 for r in records_b if r['token'].startswith(prefix))
    a_count = sum(1 for r in records_a if r['token'].startswith(prefix))
    azc_count = sum(1 for r in records_azc if r['token'].startswith(prefix))

    if b_count > 0 or a_count > 0 or azc_count > 0:
        print(f"\n{prefix}-:")
        print(f"  B: {b_count} ({100*b_count/len(records_b):.2f}%)")
        print(f"  A: {a_count} ({100*a_count/len(records_a):.2f}%)")
        print(f"  AZC: {azc_count} ({100*azc_count/len(records_azc):.2f}%)")
