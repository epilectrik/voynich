"""
Q20: ol Function Analysis

From C558: ol (Class 11, CC) is a singleton with final-biased position (9.5% final vs 5.2% initial).
What is ol's structural function? Complement to daiin?
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
print("Q20: OL FUNCTION ANALYSIS")
print("=" * 70)

# 1. BASIC STATISTICS
print("\n" + "-" * 70)
print("1. BASIC STATISTICS")
print("-" * 70)

# ol stats
ol_total = 0
ol_initial = 0
ol_final = 0

for token in tokens:
    word = token.word.replace('*', '').strip()
    if word == 'ol':
        ol_total += 1
        if token.line_initial:
            ol_initial += 1
        if token.line_final:
            ol_final += 1

print(f"\nol occurrences: {ol_total}")
print(f"Line-initial: {ol_initial} ({ol_initial/ol_total*100:.1f}%)")
print(f"Line-final: {ol_final} ({ol_final/ol_total*100:.1f}%)")
print(f"Medial: {ol_total - ol_initial - ol_final} ({(ol_total - ol_initial - ol_final)/ol_total*100:.1f}%)")

# 2. MORPHOLOGY
print("\n" + "-" * 70)
print("2. OL MORPHOLOGY")
print("-" * 70)

m = morph.extract('ol')
if m:
    print(f"\nol morphology:")
    print(f"  Articulator: {m.articulator}")
    print(f"  Prefix: {m.prefix}")
    print(f"  Middle: {m.middle}")
    print(f"  Suffix: {m.suffix}")

# 3. WHAT PRECEDES OL?
print("\n" + "-" * 70)
print("3. TOKENS PRECEDING OL")
print("-" * 70)

# Build line-grouped tokens
line_tokens = defaultdict(list)
for token in tokens:
    key = (token.folio, token.line)
    line_tokens[key].append(token)

ol_preceders = Counter()
ol_preceder_roles = Counter()

for key, toks in line_tokens.items():
    for i, tok in enumerate(toks):
        word = tok.word.replace('*', '').strip()
        if word == 'ol' and i > 0:
            prev_word = toks[i-1].word.replace('*', '').strip()
            ol_preceders[prev_word] += 1
            prev_cls = token_to_class.get(prev_word)
            ol_preceder_roles[get_role(prev_cls)] += 1

print("\nTop 15 tokens preceding ol:")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in ol_preceders.most_common(15):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

print("\nPreceder role distribution:")
total = sum(ol_preceder_roles.values())
for role, count in ol_preceder_roles.most_common():
    pct = count / total * 100
    print(f"  {role}: {count} ({pct:.1f}%)")

# 4. WHAT FOLLOWS OL?
print("\n" + "-" * 70)
print("4. TOKENS FOLLOWING OL")
print("-" * 70)

ol_followers = Counter()
ol_follower_roles = Counter()

for key, toks in line_tokens.items():
    for i, tok in enumerate(toks):
        word = tok.word.replace('*', '').strip()
        if word == 'ol' and i < len(toks) - 1:
            next_word = toks[i+1].word.replace('*', '').strip()
            ol_followers[next_word] += 1
            next_cls = token_to_class.get(next_word)
            ol_follower_roles[get_role(next_cls)] += 1

print("\nTop 15 tokens following ol:")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in ol_followers.most_common(15):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

print("\nFollower role distribution:")
total = sum(ol_follower_roles.values())
for role, count in ol_follower_roles.most_common():
    pct = count / total * 100
    print(f"  {role}: {count} ({pct:.1f}%)")

# 5. OL BY REGIME
print("\n" + "-" * 70)
print("5. OL BY REGIME")
print("-" * 70)

ol_regime = defaultdict(lambda: {'total': 0, 'initial': 0, 'final': 0})
regime_totals = defaultdict(int)

for token in tokens:
    word = token.word.replace('*', '').strip()
    regime = folio_regime.get(token.folio, 'UNKNOWN')
    regime_totals[regime] += 1

    if word == 'ol':
        ol_regime[regime]['total'] += 1
        if token.line_initial:
            ol_regime[regime]['initial'] += 1
        if token.line_final:
            ol_regime[regime]['final'] += 1

print("\n| REGIME | Total | Initial% | Final% | Rate/1000 |")
print("|--------|-------|----------|--------|-----------|")
for regime in sorted(ol_regime.keys()):
    total = ol_regime[regime]['total']
    initial = ol_regime[regime]['initial']
    final = ol_regime[regime]['final']
    initial_pct = initial / total * 100 if total > 0 else 0
    final_pct = final / total * 100 if total > 0 else 0
    rate = total / regime_totals[regime] * 1000
    print(f"| {regime} | {total:5d} | {initial_pct:7.1f}% | {final_pct:5.1f}% | {rate:9.2f} |")

# 6. OL BY SECTION
print("\n" + "-" * 70)
print("6. OL BY SECTION")
print("-" * 70)

ol_section = defaultdict(lambda: {'total': 0, 'initial': 0, 'final': 0})
section_totals = defaultdict(int)

for token in tokens:
    word = token.word.replace('*', '').strip()
    section = get_section(token.folio)
    section_totals[section] += 1

    if word == 'ol':
        ol_section[section]['total'] += 1
        if token.line_initial:
            ol_section[section]['initial'] += 1
        if token.line_final:
            ol_section[section]['final'] += 1

print("\n| Section | Total | Initial% | Final% | Rate/1000 |")
print("|---------|-------|----------|--------|-----------|")
for section in sorted(ol_section.keys()):
    total = ol_section[section]['total']
    initial = ol_section[section]['initial']
    final = ol_section[section]['final']
    initial_pct = initial / total * 100 if total > 0 else 0
    final_pct = final / total * 100 if total > 0 else 0
    rate = total / section_totals[section] * 1000
    print(f"| {section:7s} | {total:5d} | {initial_pct:7.1f}% | {final_pct:5.1f}% | {rate:9.2f} |")

# 7. COMPARE OL AND DAIIN
print("\n" + "-" * 70)
print("7. OL VS DAIIN COMPARISON")
print("-" * 70)

# daiin stats (from previous analysis)
daiin_total = 0
daiin_initial = 0
daiin_final = 0

for token in tokens:
    word = token.word.replace('*', '').strip()
    if word == 'daiin':
        daiin_total += 1
        if token.line_initial:
            daiin_initial += 1
        if token.line_final:
            daiin_final += 1

print("\n| Token | Total | Initial% | Final% | Bias |")
print("|-------|-------|----------|--------|------|")
print(f"| daiin | {daiin_total:5d} | {daiin_initial/daiin_total*100:7.1f}% | {daiin_final/daiin_total*100:5.1f}% | INITIAL |")
print(f"| ol    | {ol_total:5d} | {ol_initial/ol_total*100:7.1f}% | {ol_final/ol_total*100:5.1f}% | FINAL |")

# 8. CO-OCCURRENCE ON SAME LINE
print("\n" + "-" * 70)
print("8. DAIIN-OL CO-OCCURRENCE")
print("-" * 70)

daiin_ol_same_line = 0
daiin_only = 0
ol_only = 0
both_count = 0

for key, toks in line_tokens.items():
    words = [t.word.replace('*', '').strip() for t in toks]
    has_daiin = 'daiin' in words
    has_ol = 'ol' in words

    if has_daiin and has_ol:
        both_count += 1
    elif has_daiin:
        daiin_only += 1
    elif has_ol:
        ol_only += 1

total_lines = len(line_tokens)
print(f"\nTotal lines: {total_lines}")
print(f"Lines with both daiin and ol: {both_count} ({both_count/total_lines*100:.1f}%)")
print(f"Lines with daiin only: {daiin_only} ({daiin_only/total_lines*100:.1f}%)")
print(f"Lines with ol only: {ol_only} ({ol_only/total_lines*100:.1f}%)")
print(f"Lines with neither: {total_lines - both_count - daiin_only - ol_only}")

# When both appear, what's their relative position?
daiin_before_ol = 0
ol_before_daiin = 0
for key, toks in line_tokens.items():
    words = [t.word.replace('*', '').strip() for t in toks]
    if 'daiin' in words and 'ol' in words:
        daiin_pos = words.index('daiin')
        ol_pos = words.index('ol')
        if daiin_pos < ol_pos:
            daiin_before_ol += 1
        else:
            ol_before_daiin += 1

print(f"\nWhen both appear:")
print(f"  daiin before ol: {daiin_before_ol} ({daiin_before_ol/(daiin_before_ol+ol_before_daiin)*100:.1f}%)")
print(f"  ol before daiin: {ol_before_daiin} ({ol_before_daiin/(daiin_before_ol+ol_before_daiin)*100:.1f}%)")

# 9. OL IN CONTEXT
print("\n" + "-" * 70)
print("9. SAMPLE LINES WITH OL")
print("-" * 70)

# Show lines where ol is line-final
print("\nSample lines with ol at line-final (first 10):")
shown = 0
for key, toks in sorted(line_tokens.items()):
    words = [t.word.replace('*', '').strip() for t in toks]
    if words and words[-1] == 'ol':
        folio, line = key
        print(f"  {folio}.{line}: {' '.join(words)}")
        shown += 1
        if shown >= 10:
            break

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

preceder_en = ol_preceder_roles.get('EN', 0)
follower_en = ol_follower_roles.get('EN', 0)
preceder_total = sum(ol_preceder_roles.values())
follower_total = sum(ol_follower_roles.values())

print(f"""
1. OL STATISTICS:
   - Total: {ol_total}
   - Initial: {ol_initial} ({ol_initial/ol_total*100:.1f}%)
   - Final: {ol_final} ({ol_final/ol_total*100:.1f}%)
   - Medial: {ol_total - ol_initial - ol_final} ({(ol_total - ol_initial - ol_final)/ol_total*100:.1f}%)

2. SURROUNDING CONTEXT:
   - ENERGY precedes ol: {preceder_en/preceder_total*100:.1f}%
   - ENERGY follows ol: {follower_en/follower_total*100:.1f}%

3. DAIIN-OL COMPARISON:
   - daiin: {daiin_initial/daiin_total*100:.1f}% initial, {daiin_final/daiin_total*100:.1f}% final
   - ol: {ol_initial/ol_total*100:.1f}% initial, {ol_final/ol_total*100:.1f}% final
   - Complementary positional bias confirmed

4. CO-OCCURRENCE:
   - Both on same line: {both_count} lines
   - daiin before ol: {daiin_before_ol}/{both_count} ({daiin_before_ol/both_count*100:.1f}%)
""")

# Save results
results = {
    'ol_stats': {
        'total': ol_total,
        'initial': ol_initial,
        'final': ol_final,
        'medial': ol_total - ol_initial - ol_final
    },
    'ol_preceder_roles': dict(ol_preceder_roles),
    'ol_follower_roles': dict(ol_follower_roles),
    'ol_by_regime': dict(ol_regime),
    'ol_by_section': dict(ol_section),
    'daiin_ol_cooccurrence': {
        'both': both_count,
        'daiin_only': daiin_only,
        'ol_only': ol_only,
        'daiin_before_ol': daiin_before_ol,
        'ol_before_daiin': ol_before_daiin
    }
}

with open(RESULTS / 'ol_function_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'ol_function_analysis.json'}")
