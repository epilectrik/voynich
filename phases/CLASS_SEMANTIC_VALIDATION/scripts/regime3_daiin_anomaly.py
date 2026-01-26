"""
Q18: REGIME_3 daiin Anomaly

From C557: REGIME_3 has highest daiin occurrence rate (24.22/1000) but lowest
line-initial rate (11.9% vs 28-34% elsewhere). Why?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scripts.voynich import Transcript, Morphology

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
morph = Morphology()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Load REGIME
with open(REGIME_FILE) as f:
    regime_data = json.load(f)

folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

# Role mapping
ROLE_MAP = {
    10: 'CC', 11: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 36: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 20: 'FQ', 21: 'FQ', 23: 'FQ',
}

def get_role(cls):
    if cls is None:
        return 'UN'
    return ROLE_MAP.get(cls, 'AX')

# Section definition
def get_section(folio):
    try:
        num = int(''.join(c for c in folio if c.isdigit())[:3])
    except:
        return 'UNKNOWN'
    if num <= 56:
        return 'HERBAL'
    elif num <= 67:
        return 'PHARMA'
    elif num <= 84:
        return 'BIO'
    elif num <= 86:
        return 'COSMO'
    else:
        return 'RECIPE'

print("=" * 70)
print("Q18: REGIME_3 DAIIN ANOMALY")
print("=" * 70)

# 1. REGIME_3 FOLIOS
print("\n" + "-" * 70)
print("1. REGIME_3 COMPOSITION")
print("-" * 70)

r3_folios = regime_data.get('REGIME_3', [])
print(f"\nREGIME_3 folios ({len(r3_folios)}): {r3_folios}")

r3_sections = Counter()
for f in r3_folios:
    r3_sections[get_section(f)] += 1
print(f"REGIME_3 sections: {dict(r3_sections)}")

# 2. DAIIN OCCURRENCES IN REGIME_3
print("\n" + "-" * 70)
print("2. DAIIN OCCURRENCES IN REGIME_3")
print("-" * 70)

# Build line-grouped tokens
line_tokens = defaultdict(list)
for token in tokens:
    key = (token.folio, token.line)
    line_tokens[key].append(token)

# Find daiin occurrences in REGIME_3
r3_daiin_lines = []
for key, toks in line_tokens.items():
    folio, line = key
    if folio_regime.get(folio) == 'REGIME_3':
        for i, tok in enumerate(toks):
            word = tok.word.replace('*', '').strip()
            if word == 'daiin':
                r3_daiin_lines.append({
                    'folio': folio,
                    'line': line,
                    'position': i,
                    'line_initial': i == 0,
                    'line_length': len(toks),
                    'section': get_section(folio)
                })

print(f"\nTotal daiin in REGIME_3: {len(r3_daiin_lines)}")
print(f"Line-initial daiin: {sum(1 for d in r3_daiin_lines if d['line_initial'])}")
print(f"Line-initial rate: {sum(1 for d in r3_daiin_lines if d['line_initial']) / len(r3_daiin_lines) * 100:.1f}%")

# Position distribution
print("\n| Position | Count | % |")
print("|----------|-------|---|")
position_counts = Counter(d['position'] for d in r3_daiin_lines)
for pos in sorted(position_counts.keys()):
    count = position_counts[pos]
    pct = count / len(r3_daiin_lines) * 100
    print(f"| {pos:8d} | {count:5d} | {pct:4.1f}% |")

# 3. DAIIN POSITION IN OTHER REGIMES
print("\n" + "-" * 70)
print("3. DAIIN POSITION COMPARISON BY REGIME")
print("-" * 70)

regime_daiin_positions = defaultdict(Counter)
regime_daiin_total = defaultdict(int)

for key, toks in line_tokens.items():
    folio, line = key
    regime = folio_regime.get(folio, 'UNKNOWN')
    for i, tok in enumerate(toks):
        word = tok.word.replace('*', '').strip()
        if word == 'daiin':
            regime_daiin_positions[regime][i] += 1
            regime_daiin_total[regime] += 1

print("\nDaiin position 0 (line-initial) by REGIME:")
print("| REGIME | Total daiin | Position 0 | % |")
print("|--------|-------------|------------|---|")
for regime in sorted(regime_daiin_total.keys()):
    total = regime_daiin_total[regime]
    pos0 = regime_daiin_positions[regime][0]
    pct = pos0 / total * 100 if total > 0 else 0
    print(f"| {regime} | {total:11d} | {pos0:10d} | {pct:4.1f}% |")

# 4. WHAT PRECEDES DAIIN IN REGIME_3?
print("\n" + "-" * 70)
print("4. TOKENS PRECEDING DAIIN IN REGIME_3")
print("-" * 70)

r3_daiin_preceders = Counter()
for key, toks in line_tokens.items():
    folio, line = key
    if folio_regime.get(folio) == 'REGIME_3':
        for i, tok in enumerate(toks):
            word = tok.word.replace('*', '').strip()
            if word == 'daiin' and i > 0:
                prev_word = toks[i-1].word.replace('*', '').strip()
                r3_daiin_preceders[prev_word] += 1

print("\nTokens preceding daiin in REGIME_3:")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in r3_daiin_preceders.most_common(15):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

# Compare to other regimes
print("\nTokens preceding daiin in OTHER REGIMES:")
other_preceders = Counter()
for key, toks in line_tokens.items():
    folio, line = key
    regime = folio_regime.get(folio, 'UNKNOWN')
    if regime != 'REGIME_3':
        for i, tok in enumerate(toks):
            word = tok.word.replace('*', '').strip()
            if word == 'daiin' and i > 0:
                prev_word = toks[i-1].word.replace('*', '').strip()
                other_preceders[prev_word] += 1

print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in other_preceders.most_common(15):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

# 5. WHAT FOLLOWS DAIIN IN REGIME_3?
print("\n" + "-" * 70)
print("5. TOKENS FOLLOWING DAIIN IN REGIME_3")
print("-" * 70)

r3_daiin_followers = Counter()
r3_follower_roles = Counter()
for key, toks in line_tokens.items():
    folio, line = key
    if folio_regime.get(folio) == 'REGIME_3':
        for i, tok in enumerate(toks):
            word = tok.word.replace('*', '').strip()
            if word == 'daiin' and i < len(toks) - 1:
                next_word = toks[i+1].word.replace('*', '').strip()
                r3_daiin_followers[next_word] += 1
                next_cls = token_to_class.get(next_word)
                r3_follower_roles[get_role(next_cls)] += 1

print("\nTokens following daiin in REGIME_3:")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in r3_daiin_followers.most_common(10):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

print("\nFollower role distribution in REGIME_3:")
for role, count in r3_follower_roles.most_common():
    pct = count / sum(r3_follower_roles.values()) * 100
    print(f"  {role}: {count} ({pct:.1f}%)")

# Compare to other regimes
print("\nFollower role distribution in OTHER REGIMES:")
other_follower_roles = Counter()
for key, toks in line_tokens.items():
    folio, line = key
    regime = folio_regime.get(folio, 'UNKNOWN')
    if regime != 'REGIME_3':
        for i, tok in enumerate(toks):
            word = tok.word.replace('*', '').strip()
            if word == 'daiin' and i < len(toks) - 1:
                next_word = toks[i+1].word.replace('*', '').strip()
                next_cls = token_to_class.get(next_word)
                other_follower_roles[get_role(next_cls)] += 1

for role, count in other_follower_roles.most_common():
    pct = count / sum(other_follower_roles.values()) * 100
    print(f"  {role}: {count} ({pct:.1f}%)")

# 6. LINE CONTEXT WHERE DAIIN APPEARS
print("\n" + "-" * 70)
print("6. LINE LENGTH CONTEXT")
print("-" * 70)

r3_line_lengths = [d['line_length'] for d in r3_daiin_lines]
r3_initial_line_lengths = [d['line_length'] for d in r3_daiin_lines if d['line_initial']]
r3_non_initial_line_lengths = [d['line_length'] for d in r3_daiin_lines if not d['line_initial']]

print(f"\nREGIME_3 daiin lines:")
print(f"  Mean line length: {np.mean(r3_line_lengths):.1f}")
print(f"  Initial daiin lines: {np.mean(r3_initial_line_lengths):.1f} (n={len(r3_initial_line_lengths)})")
print(f"  Non-initial daiin lines: {np.mean(r3_non_initial_line_lengths):.1f} (n={len(r3_non_initial_line_lengths)})")

# Compare to other regimes
other_daiin_lines = []
for key, toks in line_tokens.items():
    folio, line = key
    regime = folio_regime.get(folio, 'UNKNOWN')
    if regime != 'REGIME_3':
        for i, tok in enumerate(toks):
            word = tok.word.replace('*', '').strip()
            if word == 'daiin':
                other_daiin_lines.append({'line_length': len(toks), 'line_initial': i == 0})

other_line_lengths = [d['line_length'] for d in other_daiin_lines]
other_initial_line_lengths = [d['line_length'] for d in other_daiin_lines if d['line_initial']]
other_non_initial_line_lengths = [d['line_length'] for d in other_daiin_lines if not d['line_initial']]

print(f"\nOther REGIMEs daiin lines:")
print(f"  Mean line length: {np.mean(other_line_lengths):.1f}")
print(f"  Initial daiin lines: {np.mean(other_initial_line_lengths):.1f} (n={len(other_initial_line_lengths)})")
print(f"  Non-initial daiin lines: {np.mean(other_non_initial_line_lengths):.1f} (n={len(other_non_initial_line_lengths)})")

# 7. REGIME_3 SECTION BREAKDOWN
print("\n" + "-" * 70)
print("7. REGIME_3 DAIIN BY SECTION")
print("-" * 70)

r3_section_daiin = defaultdict(lambda: {'total': 0, 'initial': 0})
for d in r3_daiin_lines:
    section = d['section']
    r3_section_daiin[section]['total'] += 1
    if d['line_initial']:
        r3_section_daiin[section]['initial'] += 1

print("\n| Section | Total | Initial | Initial% |")
print("|---------|-------|---------|----------|")
for section in sorted(r3_section_daiin.keys()):
    total = r3_section_daiin[section]['total']
    initial = r3_section_daiin[section]['initial']
    pct = initial / total * 100 if total > 0 else 0
    print(f"| {section:7s} | {total:5d} | {initial:7d} | {pct:7.1f}% |")

# 8. SAMPLE REGIME_3 DAIIN LINES
print("\n" + "-" * 70)
print("8. SAMPLE REGIME_3 LINES WITH DAIIN")
print("-" * 70)

# Show first 10 lines with daiin in REGIME_3
shown = 0
print("\nSample lines (first 10):")
for key, toks in sorted(line_tokens.items()):
    folio, line = key
    if folio_regime.get(folio) == 'REGIME_3':
        words = [t.word.replace('*', '').strip() for t in toks]
        if 'daiin' in words:
            daiin_pos = words.index('daiin')
            line_str = ' '.join(words)
            print(f"  {folio}.{line}: [{daiin_pos}] {line_str}")
            shown += 1
            if shown >= 10:
                break

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

r3_initial_rate = sum(1 for d in r3_daiin_lines if d['line_initial']) / len(r3_daiin_lines) * 100
other_initial = sum(1 for d in other_daiin_lines if d['line_initial'])
other_total = len(other_daiin_lines)
other_initial_rate = other_initial / other_total * 100 if other_total > 0 else 0

r3_en_rate = r3_follower_roles.get('EN', 0) / sum(r3_follower_roles.values()) * 100 if r3_follower_roles else 0
other_en_rate = other_follower_roles.get('EN', 0) / sum(other_follower_roles.values()) * 100 if other_follower_roles else 0

print(f"""
1. REGIME_3 DAIIN STATISTICS:
   - Total: {len(r3_daiin_lines)}
   - Line-initial: {sum(1 for d in r3_daiin_lines if d['line_initial'])} ({r3_initial_rate:.1f}%)
   - Other REGIMEs: {other_initial}/{other_total} ({other_initial_rate:.1f}%)

2. FOLLOWER ROLE COMPARISON:
   - REGIME_3 ENERGY followers: {r3_en_rate:.1f}%
   - Other REGIMEs ENERGY followers: {other_en_rate:.1f}%

3. REGIME_3 SECTIONS:
   - {dict(r3_sections)}

4. KEY OBSERVATION:
   - REGIME_3 initial rate: {r3_initial_rate:.1f}%
   - Other REGIMEs initial rate: {other_initial_rate:.1f}%
   - Ratio: {other_initial_rate/r3_initial_rate:.1f}x difference
""")

# Save results
results = {
    'regime3_daiin': {
        'total': len(r3_daiin_lines),
        'initial': sum(1 for d in r3_daiin_lines if d['line_initial']),
        'initial_rate': r3_initial_rate
    },
    'other_regimes_daiin': {
        'total': other_total,
        'initial': other_initial,
        'initial_rate': other_initial_rate
    },
    'regime3_sections': dict(r3_sections),
    'regime3_follower_roles': dict(r3_follower_roles),
    'other_follower_roles': dict(other_follower_roles)
}

with open(RESULTS / 'regime3_daiin_anomaly.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'regime3_daiin_anomaly.json'}")
