"""
Q24: FLOW Role Deep-Dive

FLOW role = Classes 7, 30, 38, 40
Complete the role taxonomy analysis.
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

FLOW_CLASSES = [7, 30, 38, 40]

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
print("Q24: FLOW ROLE DEEP-DIVE")
print("=" * 70)

# 1. FLOW CLASS MEMBERSHIP
print("\n" + "-" * 70)
print("1. FLOW CLASS MEMBERSHIP")
print("-" * 70)

print(f"\nFLOW classes: {FLOW_CLASSES}")

for cls in FLOW_CLASSES:
    toks = sorted(class_to_tokens[cls])
    print(f"\nClass {cls} ({len(toks)} tokens): {toks}")

# 2. TOKEN FREQUENCIES
print("\n" + "-" * 70)
print("2. FLOW TOKEN FREQUENCIES")
print("-" * 70)

token_counts = Counter()
for token in tokens:
    word = token.word.replace('*', '').strip()
    token_counts[word] += 1

flow_token_freqs = []
for cls in FLOW_CLASSES:
    for tok in class_to_tokens[cls]:
        count = token_counts[tok]
        flow_token_freqs.append({
            'token': tok,
            'class': cls,
            'count': count
        })

flow_token_freqs.sort(key=lambda x: -x['count'])

print("\n| Token | Class | Count | Corpus Rank |")
print("|-------|-------|-------|-------------|")

all_token_counts = sorted(token_counts.items(), key=lambda x: -x[1])
token_ranks = {tok: i+1 for i, (tok, _) in enumerate(all_token_counts)}

for item in flow_token_freqs[:20]:
    rank = token_ranks.get(item['token'], 'N/A')
    print(f"| {item['token']:10s} | {item['class']:5d} | {item['count']:5d} | #{rank} |")

total_flow = sum(item['count'] for item in flow_token_freqs)
total_corpus = len(tokens)
print(f"\nTotal FLOW tokens: {total_flow} ({total_flow/total_corpus*100:.1f}% of corpus)")

# 3. MORPHOLOGICAL STRUCTURE
print("\n" + "-" * 70)
print("3. FLOW TOKEN MORPHOLOGY")
print("-" * 70)

print("\n| Token | Class | Prefix | Middle | Suffix |")
print("|-------|-------|--------|--------|--------|")

for cls in FLOW_CLASSES:
    for tok in sorted(class_to_tokens[cls]):
        m = morph.extract(tok)
        if m:
            print(f"| {tok:10s} | {cls:5d} | {m.prefix or '-':6s} | {m.middle or '-':6s} | {m.suffix or '-':6s} |")

# Analyze MIDDLE patterns
flow_middles = Counter()
flow_suffixes = Counter()
for cls in FLOW_CLASSES:
    for tok in class_to_tokens[cls]:
        m = morph.extract(tok)
        if m:
            if m.middle:
                flow_middles[m.middle] += token_counts[tok]
            if m.suffix:
                flow_suffixes[m.suffix] += token_counts[tok]

print("\nFLOW MIDDLEs by occurrence:")
for middle, count in flow_middles.most_common(10):
    print(f"  {middle}: {count}")

print("\nFLOW SUFFIXes by occurrence:")
for suffix, count in flow_suffixes.most_common(10):
    print(f"  {suffix}: {count}")

# 4. POSITIONAL PATTERNS
print("\n" + "-" * 70)
print("4. FLOW POSITIONAL PATTERNS")
print("-" * 70)

class_positions = defaultdict(lambda: {'initial': 0, 'final': 0, 'total': 0})

for token in tokens:
    word = token.word.replace('*', '').strip()
    cls = token_to_class.get(word)
    if cls in FLOW_CLASSES:
        class_positions[cls]['total'] += 1
        if token.line_initial:
            class_positions[cls]['initial'] += 1
        if token.line_final:
            class_positions[cls]['final'] += 1

print("\n| Class | Tokens | Total | Initial% | Final% |")
print("|-------|--------|-------|----------|--------|")
for cls in FLOW_CLASSES:
    toks = ', '.join(sorted(class_to_tokens[cls])[:2])
    if len(class_to_tokens[cls]) > 2:
        toks += '...'
    total = class_positions[cls]['total']
    initial = class_positions[cls]['initial']
    final = class_positions[cls]['final']
    initial_pct = initial / total * 100 if total > 0 else 0
    final_pct = final / total * 100 if total > 0 else 0
    print(f"| {cls:5d} | {toks:12s} | {total:5d} | {initial_pct:7.1f}% | {final_pct:5.1f}% |")

# Role comparison
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

# 5. FLOW BY REGIME
print("\n" + "-" * 70)
print("5. FLOW BY REGIME")
print("-" * 70)

flow_regime = defaultdict(lambda: {'total': 0, 'flow': 0})

for token in tokens:
    word = token.word.replace('*', '').strip()
    regime = folio_regime.get(token.folio, 'UNKNOWN')
    flow_regime[regime]['total'] += 1
    cls = token_to_class.get(word)
    if cls in FLOW_CLASSES:
        flow_regime[regime]['flow'] += 1

baseline = total_flow / total_corpus
print("\n| REGIME | Tokens | FLOW | % | Enrichment |")
print("|--------|--------|------|---|------------|")
for regime in sorted(flow_regime.keys()):
    total = flow_regime[regime]['total']
    flow = flow_regime[regime]['flow']
    pct = flow / total * 100 if total > 0 else 0
    enrichment = (flow / total) / baseline if baseline > 0 else 0
    print(f"| {regime} | {total:6d} | {flow:4d} | {pct:4.1f}% | {enrichment:10.2f}x |")

# 6. FLOW BY SECTION
print("\n" + "-" * 70)
print("6. FLOW BY SECTION")
print("-" * 70)

flow_section = defaultdict(lambda: {'total': 0, 'flow': 0})

for token in tokens:
    word = token.word.replace('*', '').strip()
    section = get_section(token.folio)
    flow_section[section]['total'] += 1
    cls = token_to_class.get(word)
    if cls in FLOW_CLASSES:
        flow_section[section]['flow'] += 1

print("\n| Section | Tokens | FLOW | % | Enrichment |")
print("|---------|--------|------|---|------------|")
for section in sorted(flow_section.keys()):
    total = flow_section[section]['total']
    flow = flow_section[section]['flow']
    pct = flow / total * 100 if total > 0 else 0
    enrichment = (flow / total) / baseline if baseline > 0 else 0
    print(f"| {section:7s} | {total:6d} | {flow:4d} | {pct:4.1f}% | {enrichment:10.2f}x |")

# 7. CLASS 40 SPECIAL ANALYSIS (from C546)
print("\n" + "-" * 70)
print("7. CLASS 40 SPECIAL ANALYSIS")
print("-" * 70)

c40_tokens = sorted(class_to_tokens[40])
print(f"\nClass 40 tokens: {c40_tokens}")

c40_positions = {'initial': 0, 'final': 0, 'total': 0}
for token in tokens:
    word = token.word.replace('*', '').strip()
    if word in c40_tokens:
        c40_positions['total'] += 1
        if token.line_initial:
            c40_positions['initial'] += 1
        if token.line_final:
            c40_positions['final'] += 1

c40_total = c40_positions['total']
print(f"\nClass 40 total: {c40_total}")
print(f"  Initial: {c40_positions['initial']} ({c40_positions['initial']/c40_total*100:.1f}%)")
print(f"  Final: {c40_positions['final']} ({c40_positions['final']/c40_total*100:.1f}%)")

# Token breakdown
print("\nClass 40 token breakdown:")
for tok in c40_tokens:
    count = token_counts[tok]
    initial = sum(1 for t in tokens if t.word.replace('*', '').strip() == tok and t.line_initial)
    final = sum(1 for t in tokens if t.word.replace('*', '').strip() == tok and t.line_final)
    if count > 0:
        print(f"  {tok}: {count} total, {initial/count*100:.1f}% initial, {final/count*100:.1f}% final")

# 8. WHAT PRECEDES FLOW?
print("\n" + "-" * 70)
print("8. TOKENS PRECEDING FLOW")
print("-" * 70)

line_tokens = defaultdict(list)
for token in tokens:
    key = (token.folio, token.line)
    line_tokens[key].append(token)

flow_preceders = Counter()
flow_preceder_roles = Counter()

for key, toks in line_tokens.items():
    for i, tok in enumerate(toks):
        word = tok.word.replace('*', '').strip()
        cls = token_to_class.get(word)
        if cls in FLOW_CLASSES and i > 0:
            prev_word = toks[i-1].word.replace('*', '').strip()
            flow_preceders[prev_word] += 1
            prev_cls = token_to_class.get(prev_word)
            flow_preceder_roles[get_role(prev_cls)] += 1

print("\nTop 15 tokens preceding FLOW:")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in flow_preceders.most_common(15):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

print("\nPreceder role distribution:")
total = sum(flow_preceder_roles.values())
for role, count in flow_preceder_roles.most_common():
    pct = count / total * 100
    print(f"  {role}: {count} ({pct:.1f}%)")

# 9. WHAT FOLLOWS FLOW?
print("\n" + "-" * 70)
print("9. TOKENS FOLLOWING FLOW")
print("-" * 70)

flow_followers = Counter()
flow_follower_roles = Counter()

for key, toks in line_tokens.items():
    for i, tok in enumerate(toks):
        word = tok.word.replace('*', '').strip()
        cls = token_to_class.get(word)
        if cls in FLOW_CLASSES and i < len(toks) - 1:
            next_word = toks[i+1].word.replace('*', '').strip()
            flow_followers[next_word] += 1
            next_cls = token_to_class.get(next_word)
            flow_follower_roles[get_role(next_cls)] += 1

print("\nTop 15 tokens following FLOW:")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in flow_followers.most_common(15):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

print("\nFollower role distribution:")
total = sum(flow_follower_roles.values())
for role, count in flow_follower_roles.most_common():
    pct = count / total * 100
    print(f"  {role}: {count} ({pct:.1f}%)")

# 10. FLOW VS ENERGY COMPARISON
print("\n" + "-" * 70)
print("10. FLOW VS ENERGY COMPARISON")
print("-" * 70)

ENERGY_CLASSES = [8, 31, 32, 33, 34, 36]

energy_regime = defaultdict(int)
flow_regime_counts = defaultdict(int)

for token in tokens:
    word = token.word.replace('*', '').strip()
    regime = folio_regime.get(token.folio, 'UNKNOWN')
    cls = token_to_class.get(word)
    if cls in ENERGY_CLASSES:
        energy_regime[regime] += 1
    if cls in FLOW_CLASSES:
        flow_regime_counts[regime] += 1

print("\n| REGIME | ENERGY | FLOW | EN/FL Ratio |")
print("|--------|--------|------|-------------|")
for regime in sorted(set(energy_regime.keys()) | set(flow_regime_counts.keys())):
    en = energy_regime[regime]
    fl = flow_regime_counts[regime]
    ratio = en / fl if fl > 0 else float('inf')
    print(f"| {regime} | {en:6d} | {fl:4d} | {ratio:11.2f} |")

# 11. FLOW SELF-CHAINING
print("\n" + "-" * 70)
print("11. FLOW SELF-CHAINING")
print("-" * 70)

flow_chains = defaultdict(lambda: {'chains': 0, 'total_in_chains': 0})

for key, toks in line_tokens.items():
    words = [t.word.replace('*', '').strip() for t in toks]
    classes = [token_to_class.get(w) for w in words]

    i = 0
    while i < len(classes):
        cls = classes[i]
        if cls in FLOW_CLASSES:
            chain_len = 1
            while i + chain_len < len(classes) and classes[i + chain_len] == cls:
                chain_len += 1
            if chain_len >= 2:
                flow_chains[cls]['chains'] += 1
                flow_chains[cls]['total_in_chains'] += chain_len
            i += chain_len
        else:
            i += 1

print("\n| Class | Tokens | Chains (2+) | Chain Rate |")
print("|-------|--------|-------------|------------|")
for cls in FLOW_CLASSES:
    toks = ', '.join(sorted(class_to_tokens[cls])[:2])
    chains = flow_chains[cls]['chains']
    total_in = flow_chains[cls]['total_in_chains']
    class_total = class_positions[cls]['total']
    chain_rate = total_in / class_total * 100 if class_total > 0 else 0
    print(f"| {cls:5d} | {toks:12s} | {chains:11d} | {chain_rate:9.1f}% |")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

fl_initial = role_positions['FL']['initial'] / role_positions['FL']['total'] * 100
fl_final = role_positions['FL']['final'] / role_positions['FL']['total'] * 100
c40_final = c40_positions['final'] / c40_positions['total'] * 100

print(f"""
1. FLOW COMPOSITION:
   - 4 classes: {FLOW_CLASSES}
   - {sum(len(class_to_tokens[c]) for c in FLOW_CLASSES)} token types
   - {total_flow} occurrences ({total_flow/total_corpus*100:.1f}% of corpus)

2. TOP FLOW TOKENS:
   - ar: {token_counts['ar']} (Class 7)
   - dar: {token_counts['dar']} (Class 30)
   - al: {token_counts['al']} (Class 7)
   - dal: {token_counts['dal']} (Class 30)

3. POSITIONAL PATTERN:
   - FLOW Initial: {fl_initial:.1f}%
   - FLOW Final: {fl_final:.1f}%
   - Class 40 (daly/aly/ary) Final: {c40_final:.1f}%

4. REGIME PATTERN:
   - REGIME_1 depleted (from C551)
   - REGIME_2/3/4 neutral to enriched

5. MORPHOLOGICAL PATTERN:
   - MIDDLEs: {dict(flow_middles.most_common(3))}
   - SUFFIXes: {dict(flow_suffixes.most_common(3))}

6. KEY DISTINCTION:
   - FLOW is final-biased (17.5%)
   - Class 40 is extremely final-biased ({c40_final:.1f}%)
   - FLOW depleted in REGIME_1 (thermal contexts)
""")

# Save results
results = {
    'flow_classes': FLOW_CLASSES,
    'flow_tokens': {str(cls): list(class_to_tokens[cls]) for cls in FLOW_CLASSES},
    'token_frequencies': {item['token']: item['count'] for item in flow_token_freqs},
    'class_positions': {str(cls): dict(class_positions[cls]) for cls in FLOW_CLASSES},
    'role_positions': {role: dict(role_positions[role]) for role in role_positions},
    'flow_by_regime': {r: dict(flow_regime[r]) for r in flow_regime},
    'flow_by_section': {s: dict(flow_section[s]) for s in flow_section},
    'flow_middles': dict(flow_middles),
    'flow_suffixes': dict(flow_suffixes)
}

with open(RESULTS / 'flow_role_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'flow_role_analysis.json'}")
