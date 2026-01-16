"""
Test whether AZC constraints actually apply in Currier B.

If AZC constrains B, then:
1. MIDDLEs restricted in AZC should show restricted behavior in B
2. Position-locked AZC tokens should show position bias in B
3. AZC escape suppression should correlate with B escape rates
"""
import csv
from collections import defaultdict, Counter
import statistics

# Known morphological components
KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']
KNOWN_SUFFIXES = ['y', 'dy', 'n', 'in', 'iin', 'aiin', 'ain', 'l', 'm', 'r', 's', 'g', 'am', 'an']

def decompose_token(token):
    if not token or len(token) < 2:
        return ('', token, '')

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

# Load all tokens
azc_tokens = []
b_tokens = []
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
        line = row.get('line', '').strip()
        word_in_line = row.get('word_in_line', '').strip()

        if not word or word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        prefix, middle, suffix = decompose_token(word)

        is_azc = section in azc_sections or language not in ('A', 'B')

        if is_azc:
            azc_tokens.append({
                'token': word, 'folio': folio, 'placement': placement,
                'prefix': prefix, 'middle': middle, 'suffix': suffix
            })
        elif language == 'B':
            # Parse line position
            try:
                pos = int(word_in_line) if word_in_line else 0
            except:
                pos = 0
            b_tokens.append({
                'token': word, 'folio': folio, 'line': line,
                'word_in_line': pos,
                'prefix': prefix, 'middle': middle, 'suffix': suffix
            })

print(f"AZC tokens: {len(azc_tokens)}")
print(f"B tokens: {len(b_tokens)}")
print()

# Build AZC MIDDLE profiles
middle_azc_folios = defaultdict(set)
middle_azc_placements = defaultdict(set)
for t in azc_tokens:
    middle_azc_folios[t['middle']].add(t['folio'])
    if t['placement']:
        # Normalize to position class
        p = t['placement']
        if p.startswith('R'):
            p = 'R'
        elif p.startswith('S'):
            p = 'S'
        elif p.startswith('C'):
            p = 'C'
        middle_azc_placements[t['middle']].add(p)

# Classify MIDDLEs by restriction level
restricted_middles = set()  # 1-2 AZC folios
moderate_middles = set()    # 3-10 AZC folios
universal_middles = set()   # 10+ AZC folios

for middle, folios in middle_azc_folios.items():
    n = len(folios)
    if n <= 2:
        restricted_middles.add(middle)
    elif n <= 10:
        moderate_middles.add(middle)
    else:
        universal_middles.add(middle)

print(f"MIDDLE restriction classes:")
print(f"  Restricted (1-2 folios): {len(restricted_middles)}")
print(f"  Moderate (3-10 folios): {len(moderate_middles)}")
print(f"  Universal (10+ folios): {len(universal_middles)}")
print()

# TEST 1: Do restricted MIDDLEs show restricted B behavior?
print("=" * 60)
print("TEST 1: MIDDLE restriction -> B folio concentration")
print("=" * 60)
print()

# For each restriction class, how many B folios does the MIDDLE appear in?
def get_b_folio_spread(middle_set, b_tokens):
    middle_b_folios = defaultdict(set)
    for t in b_tokens:
        if t['middle'] in middle_set:
            middle_b_folios[t['middle']].add(t['folio'])

    spreads = [len(folios) for folios in middle_b_folios.values() if folios]
    return spreads

restricted_spreads = get_b_folio_spread(restricted_middles, b_tokens)
moderate_spreads = get_b_folio_spread(moderate_middles, b_tokens)
universal_spreads = get_b_folio_spread(universal_middles, b_tokens)

print("B folio spread by AZC restriction class:")
print("-" * 40)
if restricted_spreads:
    print(f"  Restricted: mean={statistics.mean(restricted_spreads):.1f} B folios (n={len(restricted_spreads)})")
if moderate_spreads:
    print(f"  Moderate:   mean={statistics.mean(moderate_spreads):.1f} B folios (n={len(moderate_spreads)})")
if universal_spreads:
    print(f"  Universal:  mean={statistics.mean(universal_spreads):.1f} B folios (n={len(universal_spreads)})")
print()

# Prediction: If AZC constrains B, restricted MIDDLEs should have LOWER B spread
if restricted_spreads and universal_spreads:
    r_mean = statistics.mean(restricted_spreads)
    u_mean = statistics.mean(universal_spreads)
    if r_mean < u_mean:
        print(f"[PASS] CONFIRMED: Restricted MIDDLEs have lower B spread ({r_mean:.1f} < {u_mean:.1f})")
    else:
        print(f"[FAIL] DISCONFIRMED: Restricted MIDDLEs do NOT have lower B spread ({r_mean:.1f} >= {u_mean:.1f})")
print()

# TEST 2: Do AZC position-locked MIDDLEs show position bias in B?
print("=" * 60)
print("TEST 2: AZC position -> B line position")
print("=" * 60)
print()

# Get MIDDLEs that are position-locked in AZC
early_azc_middles = set()  # Only C in AZC
late_azc_middles = set()   # Only S in AZC

for middle, placements in middle_azc_placements.items():
    if placements == {'C'}:
        early_azc_middles.add(middle)
    elif placements == {'S'}:
        late_azc_middles.add(middle)

print(f"AZC position-locked MIDDLEs:")
print(f"  C-only (early): {len(early_azc_middles)}")
print(f"  S-only (late): {len(late_azc_middles)}")
print()

# Get line positions for these MIDDLEs in B
def get_b_line_positions(middle_set, b_tokens):
    """Get normalized line positions (0-1) for MIDDLEs in B."""
    # Group by line to get line lengths
    line_tokens = defaultdict(list)
    for t in b_tokens:
        key = (t['folio'], t['line'])
        line_tokens[key].append(t)

    positions = []
    for t in b_tokens:
        if t['middle'] in middle_set and t['word_in_line'] > 0:
            key = (t['folio'], t['line'])
            line_len = len(line_tokens[key])
            if line_len > 1:
                norm_pos = (t['word_in_line'] - 1) / (line_len - 1)
                positions.append(norm_pos)
    return positions

early_b_positions = get_b_line_positions(early_azc_middles, b_tokens)
late_b_positions = get_b_line_positions(late_azc_middles, b_tokens)

print("B line position by AZC placement class:")
print("-" * 40)
if early_b_positions:
    print(f"  AZC C-only -> B mean position: {statistics.mean(early_b_positions):.3f} (n={len(early_b_positions)})")
if late_b_positions:
    print(f"  AZC S-only -> B mean position: {statistics.mean(late_b_positions):.3f} (n={len(late_b_positions)})")
print()

# Prediction: C-only should be earlier in B lines than S-only
if early_b_positions and late_b_positions:
    e_mean = statistics.mean(early_b_positions)
    l_mean = statistics.mean(late_b_positions)
    if e_mean < l_mean:
        print(f"[PASS] CONFIRMED: AZC C-only appears earlier in B ({e_mean:.3f} < {l_mean:.3f})")
    else:
        print(f"[FAIL] DISCONFIRMED: AZC position does NOT predict B position ({e_mean:.3f} >= {l_mean:.3f})")
print()

# TEST 3: AZC escape rate -> B escape rate correlation
print("=" * 60)
print("TEST 3: AZC escape profile -> B escape behavior")
print("=" * 60)
print()

# Get escape prefix rates by AZC folio
azc_folio_escape = {}
for folio in set(t['folio'] for t in azc_tokens):
    folio_tokens = [t for t in azc_tokens if t['folio'] == folio]
    if folio_tokens:
        escape_count = sum(1 for t in folio_tokens if t['prefix'] in ('qo', 'ct'))
        azc_folio_escape[folio] = escape_count / len(folio_tokens)

# Get escape rates in B, grouped by which AZC folios the B tokens activate
# (tokens that appear in high-escape AZC folios vs low-escape AZC folios)

# Build token -> AZC folio mapping
token_to_azc_folios = defaultdict(set)
for t in azc_tokens:
    token_to_azc_folios[t['token']].add(t['folio'])

# For each B token, get the mean escape rate of its AZC folios
b_token_azc_escape = []
for t in b_tokens:
    azc_folios = token_to_azc_folios.get(t['token'], set())
    if azc_folios:
        mean_azc_escape = statistics.mean(azc_folio_escape.get(f, 0) for f in azc_folios)
        is_escape = t['prefix'] in ('qo', 'ct')
        b_token_azc_escape.append((mean_azc_escape, is_escape))

# Split B tokens by AZC escape profile
low_azc_escape = [x for x in b_token_azc_escape if x[0] < 0.05]
high_azc_escape = [x for x in b_token_azc_escape if x[0] >= 0.05]

print("B escape rate by AZC escape profile:")
print("-" * 40)
if low_azc_escape:
    b_rate_low = sum(1 for x in low_azc_escape if x[1]) / len(low_azc_escape)
    print(f"  Low AZC escape (<5%): B escape rate = {b_rate_low*100:.1f}% (n={len(low_azc_escape)})")
if high_azc_escape:
    b_rate_high = sum(1 for x in high_azc_escape if x[1]) / len(high_azc_escape)
    print(f"  High AZC escape (>=5%): B escape rate = {b_rate_high*100:.1f}% (n={len(high_azc_escape)})")
print()

# Prediction: Tokens from high-escape AZC folios should have higher B escape
if low_azc_escape and high_azc_escape:
    b_rate_low = sum(1 for x in low_azc_escape if x[1]) / len(low_azc_escape)
    b_rate_high = sum(1 for x in high_azc_escape if x[1]) / len(high_azc_escape)
    if b_rate_high > b_rate_low:
        print(f"[PASS] CONFIRMED: High-escape AZC -> higher B escape ({b_rate_high*100:.1f}% > {b_rate_low*100:.1f}%)")
    else:
        print(f"[FAIL] DISCONFIRMED: AZC escape does NOT predict B escape")
print()

# Summary
print("=" * 60)
print("SUMMARY: Does AZC constrain B?")
print("=" * 60)
