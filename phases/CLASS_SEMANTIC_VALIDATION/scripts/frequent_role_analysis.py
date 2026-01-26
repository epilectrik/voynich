"""
Q21: FREQUENT Role Analysis

FREQUENT role = Classes 9, 20, 21, 23
What distinguishes FREQUENT from other high-frequency patterns?
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

FREQUENT_CLASSES = [9, 20, 21, 23]

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
print("Q21: FREQUENT ROLE ANALYSIS")
print("=" * 70)

# 1. FREQUENT CLASS MEMBERSHIP
print("\n" + "-" * 70)
print("1. FREQUENT CLASS MEMBERSHIP")
print("-" * 70)

print(f"\nFREQUENT classes: {FREQUENT_CLASSES}")

for cls in FREQUENT_CLASSES:
    toks = sorted(class_to_tokens[cls])
    print(f"\nClass {cls} ({len(toks)} tokens): {toks}")

# 2. TOKEN FREQUENCIES
print("\n" + "-" * 70)
print("2. FREQUENT TOKEN FREQUENCIES")
print("-" * 70)

# Count all token occurrences
token_counts = Counter()
for token in tokens:
    word = token.word.replace('*', '').strip()
    token_counts[word] += 1

# Get FREQUENT token frequencies
frequent_token_freqs = []
for cls in FREQUENT_CLASSES:
    for tok in class_to_tokens[cls]:
        count = token_counts[tok]
        frequent_token_freqs.append({
            'token': tok,
            'class': cls,
            'count': count
        })

frequent_token_freqs.sort(key=lambda x: -x['count'])

print("\n| Token | Class | Count | Rank in Corpus |")
print("|-------|-------|-------|----------------|")

# Get corpus-wide ranks
all_token_counts = sorted(token_counts.items(), key=lambda x: -x[1])
token_ranks = {tok: i+1 for i, (tok, _) in enumerate(all_token_counts)}

for item in frequent_token_freqs:
    rank = token_ranks.get(item['token'], 'N/A')
    print(f"| {item['token']:10s} | {item['class']:5d} | {item['count']:5d} | #{rank} |")

# Total FREQUENT tokens
total_frequent = sum(item['count'] for item in frequent_token_freqs)
total_corpus = len(tokens)
print(f"\nTotal FREQUENT tokens: {total_frequent} ({total_frequent/total_corpus*100:.1f}% of corpus)")

# 3. MORPHOLOGICAL STRUCTURE
print("\n" + "-" * 70)
print("3. FREQUENT TOKEN MORPHOLOGY")
print("-" * 70)

print("\n| Token | Class | Prefix | Middle | Suffix |")
print("|-------|-------|--------|--------|--------|")

for cls in FREQUENT_CLASSES:
    for tok in sorted(class_to_tokens[cls]):
        m = morph.extract(tok)
        if m:
            print(f"| {tok:10s} | {cls:5d} | {m.prefix or '-':6s} | {m.middle or '-':6s} | {m.suffix or '-':6s} |")
        else:
            print(f"| {tok:10s} | {cls:5d} | N/A    | N/A    | N/A    |")

# 4. POSITIONAL PATTERNS
print("\n" + "-" * 70)
print("4. FREQUENT POSITIONAL PATTERNS")
print("-" * 70)

class_positions = defaultdict(lambda: {'initial': 0, 'final': 0, 'total': 0})

for token in tokens:
    word = token.word.replace('*', '').strip()
    cls = token_to_class.get(word)
    if cls in FREQUENT_CLASSES:
        class_positions[cls]['total'] += 1
        if token.line_initial:
            class_positions[cls]['initial'] += 1
        if token.line_final:
            class_positions[cls]['final'] += 1

print("\n| Class | Tokens | Total | Initial% | Final% |")
print("|-------|--------|-------|----------|--------|")
for cls in FREQUENT_CLASSES:
    toks = ', '.join(sorted(class_to_tokens[cls])[:3])
    if len(class_to_tokens[cls]) > 3:
        toks += '...'
    total = class_positions[cls]['total']
    initial = class_positions[cls]['initial']
    final = class_positions[cls]['final']
    initial_pct = initial / total * 100 if total > 0 else 0
    final_pct = final / total * 100 if total > 0 else 0
    print(f"| {cls:5d} | {toks:12s} | {total:5d} | {initial_pct:7.1f}% | {final_pct:5.1f}% |")

# Compare to other roles
print("\nRole position comparison:")
role_positions = defaultdict(lambda: {'initial': 0, 'final': 0, 'total': 0})

for token in tokens:
    word = token.word.replace('*', '').strip()
    cls = token_to_class.get(word)
    role = get_role(cls)
    role_positions[role]['total'] += 1
    if token.line_initial:
        role_positions[role]['initial'] += 1
    if token.line_final:
        role_positions[role]['final'] += 1

print("\n| Role | Total | Initial% | Final% |")
print("|------|-------|----------|--------|")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']:
    total = role_positions[role]['total']
    initial = role_positions[role]['initial']
    final = role_positions[role]['final']
    initial_pct = initial / total * 100 if total > 0 else 0
    final_pct = final / total * 100 if total > 0 else 0
    print(f"| {role}   | {total:5d} | {initial_pct:7.1f}% | {final_pct:5.1f}% |")

# 5. FREQUENT BY REGIME
print("\n" + "-" * 70)
print("5. FREQUENT BY REGIME")
print("-" * 70)

frequent_regime = defaultdict(lambda: {'total': 0, 'frequent': 0})

for token in tokens:
    word = token.word.replace('*', '').strip()
    regime = folio_regime.get(token.folio, 'UNKNOWN')
    frequent_regime[regime]['total'] += 1
    cls = token_to_class.get(word)
    if cls in FREQUENT_CLASSES:
        frequent_regime[regime]['frequent'] += 1

print("\n| REGIME | Tokens | FREQUENT | % | Enrichment |")
print("|--------|--------|----------|---|------------|")
baseline = total_frequent / total_corpus
for regime in sorted(frequent_regime.keys()):
    total = frequent_regime[regime]['total']
    freq = frequent_regime[regime]['frequent']
    pct = freq / total * 100 if total > 0 else 0
    enrichment = (freq / total) / baseline if baseline > 0 else 0
    print(f"| {regime} | {total:6d} | {freq:8d} | {pct:4.1f}% | {enrichment:10.2f}x |")

# 6. FREQUENT BY SECTION
print("\n" + "-" * 70)
print("6. FREQUENT BY SECTION")
print("-" * 70)

frequent_section = defaultdict(lambda: {'total': 0, 'frequent': 0})

for token in tokens:
    word = token.word.replace('*', '').strip()
    section = get_section(token.folio)
    frequent_section[section]['total'] += 1
    cls = token_to_class.get(word)
    if cls in FREQUENT_CLASSES:
        frequent_section[section]['frequent'] += 1

print("\n| Section | Tokens | FREQUENT | % | Enrichment |")
print("|---------|--------|----------|---|------------|")
for section in sorted(frequent_section.keys()):
    total = frequent_section[section]['total']
    freq = frequent_section[section]['frequent']
    pct = freq / total * 100 if total > 0 else 0
    enrichment = (freq / total) / baseline if baseline > 0 else 0
    print(f"| {section:7s} | {total:6d} | {freq:8d} | {pct:4.1f}% | {enrichment:10.2f}x |")

# 7. FREQUENT SELF-CHAINING
print("\n" + "-" * 70)
print("7. FREQUENT SELF-CHAINING (REPETITION)")
print("-" * 70)

# Build line-grouped tokens
line_tokens = defaultdict(list)
for token in tokens:
    key = (token.folio, token.line)
    line_tokens[key].append(token)

# Count consecutive same-class occurrences
class_chains = defaultdict(lambda: {'chains': 0, 'total_in_chains': 0})

for key, toks in line_tokens.items():
    words = [t.word.replace('*', '').strip() for t in toks]
    classes = [token_to_class.get(w) for w in words]

    i = 0
    while i < len(classes):
        cls = classes[i]
        if cls in FREQUENT_CLASSES:
            chain_len = 1
            while i + chain_len < len(classes) and classes[i + chain_len] == cls:
                chain_len += 1
            if chain_len >= 2:
                class_chains[cls]['chains'] += 1
                class_chains[cls]['total_in_chains'] += chain_len
            i += chain_len
        else:
            i += 1

print("\n| Class | Tokens | Chains (2+) | Total in Chains | Chain Rate |")
print("|-------|--------|-------------|-----------------|------------|")
for cls in FREQUENT_CLASSES:
    toks = ', '.join(sorted(class_to_tokens[cls])[:2])
    chains = class_chains[cls]['chains']
    total_in = class_chains[cls]['total_in_chains']
    class_total = class_positions[cls]['total']
    chain_rate = total_in / class_total * 100 if class_total > 0 else 0
    print(f"| {cls:5d} | {toks:12s} | {chains:11d} | {total_in:15d} | {chain_rate:9.1f}% |")

# 8. WHAT PRECEDES FREQUENT?
print("\n" + "-" * 70)
print("8. TOKENS PRECEDING FREQUENT")
print("-" * 70)

frequent_preceders = Counter()
frequent_preceder_roles = Counter()

for key, toks in line_tokens.items():
    for i, tok in enumerate(toks):
        word = tok.word.replace('*', '').strip()
        cls = token_to_class.get(word)
        if cls in FREQUENT_CLASSES and i > 0:
            prev_word = toks[i-1].word.replace('*', '').strip()
            frequent_preceders[prev_word] += 1
            prev_cls = token_to_class.get(prev_word)
            frequent_preceder_roles[get_role(prev_cls)] += 1

print("\nTop 15 tokens preceding FREQUENT:")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in frequent_preceders.most_common(15):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

print("\nPreceder role distribution:")
total = sum(frequent_preceder_roles.values())
for role, count in frequent_preceder_roles.most_common():
    pct = count / total * 100
    print(f"  {role}: {count} ({pct:.1f}%)")

# 9. WHAT FOLLOWS FREQUENT?
print("\n" + "-" * 70)
print("9. TOKENS FOLLOWING FREQUENT")
print("-" * 70)

frequent_followers = Counter()
frequent_follower_roles = Counter()

for key, toks in line_tokens.items():
    for i, tok in enumerate(toks):
        word = tok.word.replace('*', '').strip()
        cls = token_to_class.get(word)
        if cls in FREQUENT_CLASSES and i < len(toks) - 1:
            next_word = toks[i+1].word.replace('*', '').strip()
            frequent_followers[next_word] += 1
            next_cls = token_to_class.get(next_word)
            frequent_follower_roles[get_role(next_cls)] += 1

print("\nTop 15 tokens following FREQUENT:")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in frequent_followers.most_common(15):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

print("\nFollower role distribution:")
total = sum(frequent_follower_roles.values())
for role, count in frequent_follower_roles.most_common():
    pct = count / total * 100
    print(f"  {role}: {count} ({pct:.1f}%)")

# 10. COMPARE TO HIGH-FREQUENCY NON-FREQUENT TOKENS
print("\n" + "-" * 70)
print("10. HIGH-FREQUENCY NON-FREQUENT COMPARISON")
print("-" * 70)

# Find high-frequency tokens NOT in FREQUENT role
high_freq_non_fq = []
for tok, count in all_token_counts[:50]:  # Top 50
    cls = token_to_class.get(tok)
    role = get_role(cls)
    if role != 'FQ' and count >= 50:
        high_freq_non_fq.append({'token': tok, 'count': count, 'class': cls, 'role': role})

print("\nHigh-frequency tokens NOT in FREQUENT role (top 15):")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for item in high_freq_non_fq[:15]:
    print(f"| {item['token']:10s} | {item['count']:5d} | {str(item['class']):5s} | {item['role']} |")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Calculate key statistics
fq_initial_rate = role_positions['FQ']['initial'] / role_positions['FQ']['total'] * 100
fq_final_rate = role_positions['FQ']['final'] / role_positions['FQ']['total'] * 100
en_final_rate = role_positions['EN']['final'] / role_positions['EN']['total'] * 100

print(f"""
1. FREQUENT COMPOSITION:
   - 4 classes: {FREQUENT_CLASSES}
   - {sum(len(class_to_tokens[c]) for c in FREQUENT_CLASSES)} token types
   - {total_frequent} occurrences ({total_frequent/total_corpus*100:.1f}% of corpus)

2. FREQUENT TOKENS:
   - aiin: {token_counts['aiin']} (Class 9)
   - or: {token_counts['or']} (Class 9)
   - dy: {token_counts['dy']} (Class 23)
   - y: {token_counts['y']} (Class 21)

3. POSITIONAL PATTERN:
   - Initial: {fq_initial_rate:.1f}%
   - Final: {fq_final_rate:.1f}%
   - Compared to ENERGY final: {en_final_rate:.1f}%

4. SELF-CHAINING:
   - Class 9 chain rate: {class_chains[9]['total_in_chains']/class_positions[9]['total']*100:.1f}%
   - Class 21 chain rate: {class_chains[21]['total_in_chains']/class_positions[21]['total']*100:.1f}%

5. DISTINGUISHING FEATURES:
   - Short morphology (mostly single-character or simple)
   - High self-chaining (Class 21 especially)
   - Final-biased like FLOW
   - HERBAL enriched, BIO depleted
""")

# Save results
results = {
    'frequent_classes': FREQUENT_CLASSES,
    'frequent_tokens': {str(cls): list(class_to_tokens[cls]) for cls in FREQUENT_CLASSES},
    'token_frequencies': {item['token']: item['count'] for item in frequent_token_freqs},
    'class_positions': {str(cls): dict(class_positions[cls]) for cls in FREQUENT_CLASSES},
    'role_positions': {role: dict(role_positions[role]) for role in role_positions},
    'frequent_by_regime': {r: dict(frequent_regime[r]) for r in frequent_regime},
    'frequent_by_section': {s: dict(frequent_section[s]) for s in frequent_section},
    'class_chains': {str(cls): dict(class_chains[cls]) for cls in FREQUENT_CLASSES}
}

with open(RESULTS / 'frequent_role_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'frequent_role_analysis.json'}")
