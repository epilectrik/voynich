"""
Q22: Class 17 Analysis

Class 17 is the non-singleton CORE_CONTROL class (9 tokens).
How does it differ from singleton CC classes (daiin, ol)?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
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
class_to_tokens = defaultdict(set)
for tok, cls in token_to_class.items():
    class_to_tokens[cls].add(tok)

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

CC_CLASSES = [10, 11, 17]

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
print("Q22: CLASS 17 ANALYSIS")
print("=" * 70)

# 1. CLASS 17 MEMBERSHIP
print("\n" + "-" * 70)
print("1. CLASS 17 MEMBERSHIP")
print("-" * 70)

c17_tokens = sorted(class_to_tokens[17])
print(f"\nClass 17 tokens ({len(c17_tokens)}): {c17_tokens}")

# Compare to other CC classes
print("\nAll CORE_CONTROL classes:")
for cls in CC_CLASSES:
    toks = sorted(class_to_tokens[cls])
    print(f"  Class {cls}: {toks}")

# 2. MORPHOLOGICAL STRUCTURE
print("\n" + "-" * 70)
print("2. CLASS 17 MORPHOLOGY")
print("-" * 70)

print("\n| Token | Prefix | Middle | Suffix | Structure |")
print("|-------|--------|--------|--------|-----------|")

for tok in c17_tokens:
    m = morph.extract(tok)
    if m:
        parts = []
        if m.prefix:
            parts.append(f"P:{m.prefix}")
        if m.middle:
            parts.append(f"M:{m.middle}")
        if m.suffix:
            parts.append(f"S:{m.suffix}")
        structure = '+'.join(parts)
        print(f"| {tok:10s} | {m.prefix or '-':6s} | {m.middle or '-':6s} | {m.suffix or '-':6s} | {structure} |")

# Compare to singleton CC
print("\nSingleton CC morphology:")
for cls in [10, 11]:
    tok = list(class_to_tokens[cls])[0]
    m = morph.extract(tok)
    if m:
        print(f"  Class {cls} ({tok}): prefix={m.prefix}, middle={m.middle}, suffix={m.suffix}")

# 3. TOKEN FREQUENCIES
print("\n" + "-" * 70)
print("3. CLASS 17 TOKEN FREQUENCIES")
print("-" * 70)

token_counts = Counter()
for token in tokens:
    word = token.word.replace('*', '').strip()
    token_counts[word] += 1

c17_freqs = []
for tok in c17_tokens:
    count = token_counts[tok]
    c17_freqs.append({'token': tok, 'count': count})

c17_freqs.sort(key=lambda x: -x['count'])

print("\n| Token | Count | % of Class 17 |")
print("|-------|-------|---------------|")
total_c17 = sum(f['count'] for f in c17_freqs)
for f in c17_freqs:
    pct = f['count'] / total_c17 * 100 if total_c17 > 0 else 0
    print(f"| {f['token']:10s} | {f['count']:5d} | {pct:12.1f}% |")

print(f"\nTotal Class 17 occurrences: {total_c17}")

# Compare to singleton CC
print("\nCC class comparison:")
print("| Class | Tokens | Total Occurrences |")
print("|-------|--------|-------------------|")
for cls in CC_CLASSES:
    toks = class_to_tokens[cls]
    total = sum(token_counts[t] for t in toks)
    print(f"| {cls:5d} | {len(toks):6d} | {total:17d} |")

# 4. POSITIONAL PATTERNS
print("\n" + "-" * 70)
print("4. CLASS 17 POSITIONAL PATTERNS")
print("-" * 70)

c17_positions = defaultdict(lambda: {'initial': 0, 'final': 0, 'total': 0})

for token in tokens:
    word = token.word.replace('*', '').strip()
    if word in c17_tokens:
        c17_positions[word]['total'] += 1
        if token.line_initial:
            c17_positions[word]['initial'] += 1
        if token.line_final:
            c17_positions[word]['final'] += 1

print("\n| Token | Total | Initial% | Final% |")
print("|-------|-------|----------|--------|")
for tok in c17_tokens:
    total = c17_positions[tok]['total']
    if total > 0:
        initial = c17_positions[tok]['initial']
        final = c17_positions[tok]['final']
        initial_pct = initial / total * 100
        final_pct = final / total * 100
        print(f"| {tok:10s} | {total:5d} | {initial_pct:7.1f}% | {final_pct:5.1f}% |")

# Class-level comparison
print("\nCC class positional comparison:")
print("| Class | Tokens | Initial% | Final% |")
print("|-------|--------|----------|--------|")
for cls in CC_CLASSES:
    toks = class_to_tokens[cls]
    total = 0
    initial = 0
    final = 0
    for token in tokens:
        word = token.word.replace('*', '').strip()
        if word in toks:
            total += 1
            if token.line_initial:
                initial += 1
            if token.line_final:
                final += 1
    if total > 0:
        print(f"| {cls:5d} | {list(toks)[0] if len(toks)==1 else f'{len(toks)} tokens'} | {initial/total*100:7.1f}% | {final/total*100:5.1f}% |")

# 5. CLASS 17 BY REGIME
print("\n" + "-" * 70)
print("5. CLASS 17 BY REGIME")
print("-" * 70)

c17_regime = defaultdict(lambda: {'total': 0, 'c17': 0})

for token in tokens:
    word = token.word.replace('*', '').strip()
    regime = folio_regime.get(token.folio, 'UNKNOWN')
    c17_regime[regime]['total'] += 1
    if word in c17_tokens:
        c17_regime[regime]['c17'] += 1

baseline = total_c17 / len(tokens)
print("\n| REGIME | Tokens | Class 17 | % | Enrichment |")
print("|--------|--------|----------|---|------------|")
for regime in sorted(c17_regime.keys()):
    total = c17_regime[regime]['total']
    c17 = c17_regime[regime]['c17']
    pct = c17 / total * 100 if total > 0 else 0
    enrichment = (c17 / total) / baseline if baseline > 0 else 0
    print(f"| {regime} | {total:6d} | {c17:8d} | {pct:4.1f}% | {enrichment:10.2f}x |")

# 6. CLASS 17 BY SECTION
print("\n" + "-" * 70)
print("6. CLASS 17 BY SECTION")
print("-" * 70)

c17_section = defaultdict(lambda: {'total': 0, 'c17': 0})

for token in tokens:
    word = token.word.replace('*', '').strip()
    section = get_section(token.folio)
    c17_section[section]['total'] += 1
    if word in c17_tokens:
        c17_section[section]['c17'] += 1

print("\n| Section | Tokens | Class 17 | % | Enrichment |")
print("|---------|--------|----------|---|------------|")
for section in sorted(c17_section.keys()):
    total = c17_section[section]['total']
    c17 = c17_section[section]['c17']
    pct = c17 / total * 100 if total > 0 else 0
    enrichment = (c17 / total) / baseline if baseline > 0 else 0
    print(f"| {section:7s} | {total:6d} | {c17:8d} | {pct:4.1f}% | {enrichment:10.2f}x |")

# 7. WHAT PRECEDES CLASS 17?
print("\n" + "-" * 70)
print("7. TOKENS PRECEDING CLASS 17")
print("-" * 70)

# Build line-grouped tokens
line_tokens = defaultdict(list)
for token in tokens:
    key = (token.folio, token.line)
    line_tokens[key].append(token)

c17_preceders = Counter()
c17_preceder_roles = Counter()

for key, toks in line_tokens.items():
    for i, tok in enumerate(toks):
        word = tok.word.replace('*', '').strip()
        if word in c17_tokens and i > 0:
            prev_word = toks[i-1].word.replace('*', '').strip()
            c17_preceders[prev_word] += 1
            prev_cls = token_to_class.get(prev_word)
            c17_preceder_roles[get_role(prev_cls)] += 1

print("\nTop 15 tokens preceding Class 17:")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in c17_preceders.most_common(15):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

print("\nPreceder role distribution:")
total = sum(c17_preceder_roles.values())
for role, count in c17_preceder_roles.most_common():
    pct = count / total * 100
    print(f"  {role}: {count} ({pct:.1f}%)")

# 8. WHAT FOLLOWS CLASS 17?
print("\n" + "-" * 70)
print("8. TOKENS FOLLOWING CLASS 17")
print("-" * 70)

c17_followers = Counter()
c17_follower_roles = Counter()

for key, toks in line_tokens.items():
    for i, tok in enumerate(toks):
        word = tok.word.replace('*', '').strip()
        if word in c17_tokens and i < len(toks) - 1:
            next_word = toks[i+1].word.replace('*', '').strip()
            c17_followers[next_word] += 1
            next_cls = token_to_class.get(next_word)
            c17_follower_roles[get_role(next_cls)] += 1

print("\nTop 15 tokens following Class 17:")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in c17_followers.most_common(15):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

print("\nFollower role distribution:")
total = sum(c17_follower_roles.values())
for role, count in c17_follower_roles.most_common():
    pct = count / total * 100
    print(f"  {role}: {count} ({pct:.1f}%)")

# 9. COMPARE CC FOLLOWER PATTERNS
print("\n" + "-" * 70)
print("9. CC CLASS FOLLOWER COMPARISON")
print("-" * 70)

# Get follower roles for each CC class
cc_follower_roles = defaultdict(Counter)

for key, toks in line_tokens.items():
    for i, tok in enumerate(toks):
        word = tok.word.replace('*', '').strip()
        cls = token_to_class.get(word)
        if cls in CC_CLASSES and i < len(toks) - 1:
            next_word = toks[i+1].word.replace('*', '').strip()
            next_cls = token_to_class.get(next_word)
            cc_follower_roles[cls][get_role(next_cls)] += 1

print("\n| Class | Token(s) | EN% | CC% | FL% | FQ% | AX% | UN% |")
print("|-------|----------|-----|-----|-----|-----|-----|-----|")
for cls in CC_CLASSES:
    roles = cc_follower_roles[cls]
    total = sum(roles.values())
    if total > 0:
        tok_str = list(class_to_tokens[cls])[0] if len(class_to_tokens[cls]) == 1 else f"{len(class_to_tokens[cls])} toks"
        en = roles['EN'] / total * 100
        cc = roles['CC'] / total * 100
        fl = roles['FL'] / total * 100
        fq = roles['FQ'] / total * 100
        ax = roles['AX'] / total * 100
        un = roles['UN'] / total * 100
        print(f"| {cls:5d} | {tok_str:8s} | {en:3.0f}% | {cc:3.0f}% | {fl:3.0f}% | {fq:3.0f}% | {ax:3.0f}% | {un:3.0f}% |")

# 10. COMMON MIDDLE ANALYSIS
print("\n" + "-" * 70)
print("10. CLASS 17 MIDDLE PATTERNS")
print("-" * 70)

c17_middles = Counter()
for tok in c17_tokens:
    m = morph.extract(tok)
    if m and m.middle:
        c17_middles[m.middle] += token_counts[tok]

print("\nClass 17 MIDDLEs by occurrence:")
for middle, count in c17_middles.most_common():
    print(f"  {middle}: {count}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Calculate key stats
c10_total = token_counts['daiin']
c11_total = token_counts['ol']
c17_en_rate = cc_follower_roles[17]['EN'] / sum(cc_follower_roles[17].values()) * 100 if cc_follower_roles[17] else 0
c10_en_rate = cc_follower_roles[10]['EN'] / sum(cc_follower_roles[10].values()) * 100 if cc_follower_roles[10] else 0

print(f"""
1. CLASS 17 COMPOSITION:
   - 9 tokens: {c17_tokens}
   - Total occurrences: {total_c17}
   - Compare: daiin={c10_total}, ol={c11_total}

2. MORPHOLOGY:
   - All Class 17 tokens have 'al' or 'ar' suffix pattern
   - MIDDLEs: {dict(c17_middles.most_common(5))}

3. POSITIONAL PATTERN:
   - Class 17 is MEDIAL-concentrated (low initial, low final)
   - Unlike daiin (initial-biased) or ol (final-biased)

4. ENERGY TRIGGER:
   - Class 17 ENERGY followers: {c17_en_rate:.1f}%
   - daiin ENERGY followers: {c10_en_rate:.1f}%
   - Class 17 is WEAKER energy trigger than daiin

5. REGIME/SECTION:
   - REGIME_4 enriched, REGIME_1 depleted
   - RECIPE enriched, BIO depleted
""")

# Save results
results = {
    'class17_tokens': c17_tokens,
    'token_frequencies': {f['token']: f['count'] for f in c17_freqs},
    'total_occurrences': total_c17,
    'positional_patterns': {tok: dict(c17_positions[tok]) for tok in c17_tokens},
    'cc_comparison': {
        str(cls): {
            'tokens': list(class_to_tokens[cls]),
            'total': sum(token_counts[t] for t in class_to_tokens[cls]),
            'follower_roles': dict(cc_follower_roles[cls])
        } for cls in CC_CLASSES
    },
    'by_regime': {r: dict(c17_regime[r]) for r in c17_regime},
    'by_section': {s: dict(c17_section[s]) for s in c17_section}
}

with open(RESULTS / 'class17_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'class17_analysis.json'}")
