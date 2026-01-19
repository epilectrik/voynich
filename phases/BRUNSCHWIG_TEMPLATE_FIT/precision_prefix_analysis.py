#!/usr/bin/env python3
"""
PRECISION PREFIX DEEP ANALYSIS

Question: The y-prefix is 2.7x enriched in PRECISION folios.
          Does this correlate with LINK/monitoring behavior in B?

If REGIME_4 = precision-constrained execution with high LINK ratio,
then y-prefixed tokens should show:
- Higher appearance in LINK-adjacent positions
- More monitoring-like behavior patterns
"""

import csv
from collections import defaultdict, Counter

# Load folio REGIME mapping
folio_regime = {}
with open('results/proposed_folio_order.txt', encoding='utf-8') as f:
    for line in f:
        parts = line.split('|')
        if len(parts) >= 3:
            folio = parts[1].strip()
            regime = parts[2].strip()
            if folio.startswith('f') and regime.startswith('REGIME'):
                folio_regime[folio] = regime

# Load B tokens with position info
b_tokens = []
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        # Filter to PRIMARY transcriber (H) only - CRITICAL for clean data
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue

        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        language = row.get('language', '').strip()
        line_num = row.get('line_number', '').strip()
        word_pos = row.get('word_in_line', '').strip()

        if language != 'B' or not word:
            continue
        if word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        try:
            pos = int(word_pos) if word_pos else 0
        except:
            pos = 0

        b_tokens.append({
            'token': word, 'folio': folio,
            'line': line_num, 'pos': pos,
            'regime': folio_regime.get(folio, 'UNKNOWN')
        })

print(f"Loaded {len(b_tokens)} B tokens")
print()

# Identify y-prefixed tokens
y_tokens = [t for t in b_tokens if t['token'].startswith('y')]
qo_tokens = [t for t in b_tokens if t['token'].startswith('qo')]
ch_tokens = [t for t in b_tokens if t['token'].startswith('ch')]

print("=" * 70)
print("PREFIX FREQUENCY BY REGIME")
print("=" * 70)
print()

for prefix, tokens in [('y', y_tokens), ('qo', qo_tokens), ('ch', ch_tokens)]:
    regime_counts = Counter(t['regime'] for t in tokens)
    total = len(tokens)
    print(f"{prefix}-prefix (n={total}):")
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        count = regime_counts.get(regime, 0)
        pct = 100 * count / total if total > 0 else 0
        folio_count = len(set(t['folio'] for t in tokens if t['regime'] == regime))
        print(f"  {regime}: {pct:5.1f}% ({count} tokens in {folio_count} folios)")
    print()

# Positional analysis - where in line do these prefixes appear?
print("=" * 70)
print("LINE POSITION BY PREFIX")
print("=" * 70)
print()

# Only analyze R4 folios for precision signal
r4_tokens = [t for t in b_tokens if t['regime'] == 'REGIME_4']

# Get max line length for normalization
line_lengths = defaultdict(int)
for t in r4_tokens:
    key = (t['folio'], t['line'])
    line_lengths[key] = max(line_lengths[key], t['pos'])

def get_position_zone(token, line_lengths):
    """Classify position as EARLY, MIDDLE, or LATE in line."""
    key = (token['folio'], token['line'])
    max_pos = line_lengths.get(key, 10)
    if max_pos <= 0:
        return 'UNKNOWN'
    ratio = token['pos'] / max_pos
    if ratio < 0.33:
        return 'EARLY'
    elif ratio < 0.67:
        return 'MIDDLE'
    else:
        return 'LATE'

print("In REGIME_4 (precision) folios:")
print()

for prefix in ['y', 'qo', 'ch', 'sh', 'd']:
    prefix_tokens = [t for t in r4_tokens if t['token'].startswith(prefix)]
    if len(prefix_tokens) < 50:
        continue

    zones = Counter(get_position_zone(t, line_lengths) for t in prefix_tokens)
    total = sum(zones.values())

    print(f"{prefix}-prefix (n={total}):")
    for zone in ['EARLY', 'MIDDLE', 'LATE']:
        pct = 100 * zones.get(zone, 0) / total if total > 0 else 0
        bar = '#' * int(pct / 3)
        print(f"  {zone:6s}: {pct:5.1f}% {bar}")
    print()

# Compare y-prefix positional pattern across regimes
print("=" * 70)
print("y-PREFIX POSITIONAL PATTERN BY REGIME")
print("=" * 70)
print()

for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    regime_tokens = [t for t in b_tokens if t['regime'] == regime]

    # Build line lengths for this regime
    regime_lengths = defaultdict(int)
    for t in regime_tokens:
        key = (t['folio'], t['line'])
        regime_lengths[key] = max(regime_lengths[key], t['pos'])

    y_regime = [t for t in regime_tokens if t['token'].startswith('y')]

    if len(y_regime) < 30:
        print(f"{regime}: insufficient data ({len(y_regime)} y-tokens)")
        continue

    zones = Counter(get_position_zone(t, regime_lengths) for t in y_regime)
    total = sum(zones.values())

    print(f"{regime} (n={total} y-tokens):")
    for zone in ['EARLY', 'MIDDLE', 'LATE']:
        pct = 100 * zones.get(zone, 0) / total if total > 0 else 0
        bar = '#' * int(pct / 3)
        print(f"  {zone:6s}: {pct:5.1f}% {bar}")
    print()

# Token diversity analysis
print("=" * 70)
print("TOKEN DIVERSITY BY PREFIX IN REGIME_4")
print("=" * 70)
print()

r4_prefix_tokens = defaultdict(list)
for t in r4_tokens:
    for prefix in ['y', 'qo', 'ch', 'sh', 'd', 'ok', 'ot']:
        if t['token'].startswith(prefix):
            r4_prefix_tokens[prefix].append(t['token'])
            break

for prefix in ['y', 'qo', 'ch', 'sh', 'd']:
    tokens = r4_prefix_tokens[prefix]
    if len(tokens) < 30:
        continue

    unique = len(set(tokens))
    ratio = unique / len(tokens)

    # Top tokens
    top = Counter(tokens).most_common(5)

    print(f"{prefix}-prefix:")
    print(f"  Total: {len(tokens)}, Unique: {unique}, Ratio: {ratio:.2f}")
    print(f"  Top tokens: {[t[0] for t in top]}")
    print()

# Conclusion
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)
print()

# Calculate y-enrichment in R4
r4_y_count = len([t for t in r4_tokens if t['token'].startswith('y')])
r4_total = len(r4_tokens)
r4_y_pct = 100 * r4_y_count / r4_total if r4_total > 0 else 0

other_y_count = len([t for t in b_tokens if t['regime'] != 'REGIME_4' and t['token'].startswith('y')])
other_total = len([t for t in b_tokens if t['regime'] != 'REGIME_4'])
other_y_pct = 100 * other_y_count / other_total if other_total > 0 else 0

enrichment = r4_y_pct / other_y_pct if other_y_pct > 0 else 0

print(f"y-prefix in REGIME_4: {r4_y_pct:.1f}%")
print(f"y-prefix in other regimes: {other_y_pct:.1f}%")
print(f"Enrichment ratio: {enrichment:.2f}x")
print()

if enrichment > 1.5:
    print("FINDING: y-prefix is significantly enriched in PRECISION folios")
    print()
    print("If REGIME_4 = precision-constrained execution (high LINK ratio),")
    print("then y-prefix may function as a MONITORING/STABILITY marker.")
    print()
    print("This would explain:")
    print("  - Why y-prefix is rare in AROMATIC_WATER (simple procedures)")
    print("  - Why y-prefix is enriched in PRECISION (exact timing required)")
    print("  - Why Brunschwig precision procedures fit REGIME_4 constraints")
else:
    print("FINDING: y-prefix enrichment is weak")
    print("         No clear correlation with precision/monitoring")
