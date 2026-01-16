"""Probe MIDDLE distribution to detect encoding resolution."""
import csv
from collections import defaultdict, Counter

# Known morphological components
KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']
KNOWN_SUFFIXES = ['y', 'dy', 'n', 'in', 'iin', 'aiin', 'ain', 'l', 'm', 'r', 's', 'g', 'am', 'an']

def decompose_token(token):
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return ('', token, '')

    original = token
    prefix = ''
    suffix = ''

    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break

    return (prefix, token, suffix)

# Load AZC tokens with placement codes
azc_tokens = []
azc_sections = {'Z', 'A', 'C'}

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
            # Filter to PRIMARY transcriber (H) only
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        section = row.get('section', '').strip()
        language = row.get('language', '').strip()
        placement = row.get('placement', '').strip()

        if not word or word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        is_azc = section in azc_sections or language not in ('A', 'B')
        if is_azc:
            prefix, middle, suffix = decompose_token(word)
            azc_tokens.append({
                'token': word,
                'folio': folio,
                'placement': placement,
                'prefix': prefix,
                'middle': middle,
                'suffix': suffix
            })

print(f"Total AZC tokens: {len(azc_tokens)}")
print()

# Analyze MIDDLE distribution
middle_counts = Counter(t['middle'] for t in azc_tokens)
print(f"Unique MIDDLEs: {len(middle_counts)}")
print()

# How many folios does each MIDDLE appear in?
middle_to_folios = defaultdict(set)
for t in azc_tokens:
    middle_to_folios[t['middle']].add(t['folio'])

folio_count_dist = Counter(len(folios) for folios in middle_to_folios.values())
print("MIDDLE by folio coverage:")
print("-" * 40)
for n_folios in sorted(folio_count_dist.keys()):
    count = folio_count_dist[n_folios]
    pct = count / len(middle_to_folios) * 100
    bar = '#' * int(pct / 2)
    print(f"  {n_folios:2d} folios: {count:4d} MIDDLEs ({pct:5.1f}%) {bar}")

print()

# Do MIDDLEs cluster by placement?
print("MIDDLE × Placement analysis:")
print("-" * 40)

# Get placement distribution for each MIDDLE
middle_placement = defaultdict(Counter)
for t in azc_tokens:
    if t['placement']:
        # Normalize placement (R1, R2, R3 -> R-series, etc.)
        p = t['placement']
        if p.startswith('R'):
            p_class = 'R-series'
        elif p.startswith('S'):
            p_class = 'S-series'
        elif p.startswith('C'):
            p_class = 'C-series'
        else:
            p_class = p
        middle_placement[t['middle']][p_class] += 1

# How many MIDDLEs are position-restricted?
position_restricted = 0
position_flexible = 0
for middle, placements in middle_placement.items():
    if len(placements) == 1:
        position_restricted += 1
    else:
        position_flexible += 1

print(f"Position-restricted MIDDLEs (1 placement class): {position_restricted} ({position_restricted/len(middle_placement)*100:.1f}%)")
print(f"Position-flexible MIDDLEs (multiple placements): {position_flexible} ({position_flexible/len(middle_placement)*100:.1f}%)")
print()

# Top MIDDLEs by frequency and their placement patterns
print("Top 20 MIDDLEs and their placement patterns:")
print("-" * 60)
for middle, count in middle_counts.most_common(20):
    placements = middle_placement[middle]
    placement_str = ", ".join(f"{p}:{c}" for p, c in placements.most_common(3))
    n_folios = len(middle_to_folios[middle])
    print(f"  {middle:<12} n={count:4d}  folios={n_folios:2d}  placements: {placement_str}")

print()

# Check if MIDDLE length correlates with anything
print("MIDDLE length distribution:")
print("-" * 40)
length_dist = Counter(len(t['middle']) for t in azc_tokens)
for length in sorted(length_dist.keys()):
    count = length_dist[length]
    pct = count / len(azc_tokens) * 100
    print(f"  len={length}: {count:4d} ({pct:5.1f}%)")

print()

# Do short MIDDLEs vs long MIDDLEs have different folio coverage?
print("MIDDLE length vs folio coverage:")
print("-" * 40)
for length in [1, 2, 3, 4, 5]:
    middles_of_length = [m for m in middle_to_folios if len(m) == length]
    if middles_of_length:
        avg_folios = sum(len(middle_to_folios[m]) for m in middles_of_length) / len(middles_of_length)
        print(f"  len={length}: {len(middles_of_length):4d} MIDDLEs, avg {avg_folios:.1f} folios each")
