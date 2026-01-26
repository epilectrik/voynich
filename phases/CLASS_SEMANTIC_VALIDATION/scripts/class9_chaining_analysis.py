"""
Q23: Class 9 aiin-Chaining Analysis

From C559: Class 9 (aiin, o, or) self-chains at 16.2% while other FREQUENT classes
have 0-4% chain rates. Why does Class 9 behave differently?
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
print("Q23: CLASS 9 AIIN-CHAINING ANALYSIS")
print("=" * 70)

# Build line-grouped tokens
line_tokens = defaultdict(list)
for token in tokens:
    key = (token.folio, token.line)
    line_tokens[key].append(token)

# 1. CLASS 9 MEMBERSHIP
print("\n" + "-" * 70)
print("1. CLASS 9 MEMBERSHIP")
print("-" * 70)

c9_tokens = sorted(class_to_tokens[9])
print(f"\nClass 9 tokens: {c9_tokens}")

# Token frequencies
token_counts = Counter()
for token in tokens:
    word = token.word.replace('*', '').strip()
    token_counts[word] += 1

print("\n| Token | Count | % of Class 9 |")
print("|-------|-------|---------------|")
c9_total = sum(token_counts[t] for t in c9_tokens)
for tok in c9_tokens:
    count = token_counts[tok]
    pct = count / c9_total * 100
    print(f"| {tok:5s} | {count:5d} | {pct:12.1f}% |")

# 2. CHAIN PATTERNS
print("\n" + "-" * 70)
print("2. CLASS 9 CHAIN PATTERNS")
print("-" * 70)

# Find all Class 9 chains
c9_chains = []
for key, toks in line_tokens.items():
    words = [t.word.replace('*', '').strip() for t in toks]
    classes = [token_to_class.get(w) for w in words]

    i = 0
    while i < len(classes):
        if classes[i] == 9:
            chain_start = i
            chain_tokens = [words[i]]
            while i + 1 < len(classes) and classes[i + 1] == 9:
                i += 1
                chain_tokens.append(words[i])
            if len(chain_tokens) >= 2:
                c9_chains.append({
                    'folio': key[0],
                    'line': key[1],
                    'tokens': chain_tokens,
                    'length': len(chain_tokens),
                    'section': get_section(key[0]),
                    'regime': folio_regime.get(key[0], 'UNKNOWN')
                })
        i += 1

print(f"\nTotal Class 9 chains (2+ consecutive): {len(c9_chains)}")

# Chain length distribution
chain_lengths = Counter(c['length'] for c in c9_chains)
print("\n| Chain Length | Count |")
print("|--------------|-------|")
for length in sorted(chain_lengths.keys()):
    print(f"| {length:12d} | {chain_lengths[length]:5d} |")

# 3. CHAIN COMPOSITION
print("\n" + "-" * 70)
print("3. CHAIN COMPOSITION (WHICH TOKENS CHAIN?)")
print("-" * 70)

# What token pairs appear in chains?
chain_pairs = Counter()
chain_starts = Counter()
chain_ends = Counter()

for chain in c9_chains:
    toks = chain['tokens']
    chain_starts[toks[0]] += 1
    chain_ends[toks[-1]] += 1
    for i in range(len(toks) - 1):
        pair = f"{toks[i]}->{toks[i+1]}"
        chain_pairs[pair] += 1

print("\nChain pair frequencies:")
print("| Pair | Count |")
print("|------|-------|")
for pair, count in chain_pairs.most_common(10):
    print(f"| {pair:10s} | {count:5d} |")

print("\nChain starts:")
for tok, count in chain_starts.most_common():
    print(f"  {tok}: {count}")

print("\nChain ends:")
for tok, count in chain_ends.most_common():
    print(f"  {tok}: {count}")

# 4. AIIN-AIIN SPECIFIC ANALYSIS
print("\n" + "-" * 70)
print("4. AIIN-AIIN CHAINS")
print("-" * 70)

aiin_chains = [c for c in c9_chains if 'aiin' in c['tokens']]
pure_aiin_chains = [c for c in c9_chains if all(t == 'aiin' for t in c['tokens'])]

print(f"\nChains containing 'aiin': {len(aiin_chains)}")
print(f"Pure aiin-only chains: {len(pure_aiin_chains)}")

# Sample pure aiin chains
print("\nSample pure aiin chains (first 10):")
for chain in pure_aiin_chains[:10]:
    print(f"  {chain['folio']}.{chain['line']}: {' '.join(chain['tokens'])} (len={chain['length']})")

# 5. CHAINS BY REGIME
print("\n" + "-" * 70)
print("5. CLASS 9 CHAINS BY REGIME")
print("-" * 70)

regime_chains = defaultdict(list)
for chain in c9_chains:
    regime_chains[chain['regime']].append(chain)

# Get regime token totals for rate calculation
regime_c9_totals = defaultdict(int)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if word in c9_tokens:
        regime = folio_regime.get(token.folio, 'UNKNOWN')
        regime_c9_totals[regime] += 1

print("\n| REGIME | Chains | C9 Tokens | Chain Rate |")
print("|--------|--------|-----------|------------|")
for regime in sorted(regime_chains.keys()):
    chains = len(regime_chains[regime])
    tokens_in_chains = sum(c['length'] for c in regime_chains[regime])
    c9_total_regime = regime_c9_totals[regime]
    chain_rate = tokens_in_chains / c9_total_regime * 100 if c9_total_regime > 0 else 0
    print(f"| {regime} | {chains:6d} | {c9_total_regime:9d} | {chain_rate:9.1f}% |")

# 6. CHAINS BY SECTION
print("\n" + "-" * 70)
print("6. CLASS 9 CHAINS BY SECTION")
print("-" * 70)

section_chains = defaultdict(list)
for chain in c9_chains:
    section_chains[chain['section']].append(chain)

# Get section token totals
section_c9_totals = defaultdict(int)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if word in c9_tokens:
        section = get_section(token.folio)
        section_c9_totals[section] += 1

print("\n| Section | Chains | C9 Tokens | Chain Rate |")
print("|---------|--------|-----------|------------|")
for section in sorted(section_chains.keys()):
    chains = len(section_chains[section])
    tokens_in_chains = sum(c['length'] for c in section_chains[section])
    c9_total_section = section_c9_totals[section]
    chain_rate = tokens_in_chains / c9_total_section * 100 if c9_total_section > 0 else 0
    print(f"| {section:7s} | {chains:6d} | {c9_total_section:9d} | {chain_rate:9.1f}% |")

# 7. WHAT PRECEDES CLASS 9 CHAINS?
print("\n" + "-" * 70)
print("7. CONTEXT BEFORE CLASS 9 CHAINS")
print("-" * 70)

chain_preceders = Counter()
chain_preceder_roles = Counter()

for key, toks in line_tokens.items():
    words = [t.word.replace('*', '').strip() for t in toks]
    classes = [token_to_class.get(w) for w in words]

    for i in range(1, len(classes)):
        # Check if this starts a chain
        if classes[i] == 9 and (i == 0 or classes[i-1] != 9):
            # Check if it's actually a chain (next is also 9)
            if i + 1 < len(classes) and classes[i + 1] == 9:
                prev_word = words[i-1]
                chain_preceders[prev_word] += 1
                prev_cls = token_to_class.get(prev_word)
                chain_preceder_roles[get_role(prev_cls)] += 1

print("\nTop 15 tokens preceding Class 9 chains:")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in chain_preceders.most_common(15):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

print("\nPreceder role distribution:")
total = sum(chain_preceder_roles.values())
for role, count in chain_preceder_roles.most_common():
    pct = count / total * 100 if total > 0 else 0
    print(f"  {role}: {count} ({pct:.1f}%)")

# 8. WHAT FOLLOWS CLASS 9 CHAINS?
print("\n" + "-" * 70)
print("8. CONTEXT AFTER CLASS 9 CHAINS")
print("-" * 70)

chain_followers = Counter()
chain_follower_roles = Counter()

for key, toks in line_tokens.items():
    words = [t.word.replace('*', '').strip() for t in toks]
    classes = [token_to_class.get(w) for w in words]

    for i in range(len(classes) - 1):
        # Check if this ends a chain
        if classes[i] == 9 and classes[i + 1] != 9:
            # Check if it was actually a chain (previous was also 9)
            if i > 0 and classes[i - 1] == 9:
                next_word = words[i + 1]
                chain_followers[next_word] += 1
                next_cls = token_to_class.get(next_word)
                chain_follower_roles[get_role(next_cls)] += 1

print("\nTop 15 tokens following Class 9 chains:")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in chain_followers.most_common(15):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

print("\nFollower role distribution:")
total = sum(chain_follower_roles.values())
for role, count in chain_follower_roles.most_common():
    pct = count / total * 100 if total > 0 else 0
    print(f"  {role}: {count} ({pct:.1f}%)")

# 9. SAMPLE CHAIN CONTEXTS
print("\n" + "-" * 70)
print("9. SAMPLE CHAIN CONTEXTS")
print("-" * 70)

print("\nSample lines with Class 9 chains (first 15):")
shown = 0
for key, toks in sorted(line_tokens.items()):
    words = [t.word.replace('*', '').strip() for t in toks]
    classes = [token_to_class.get(w) for w in words]

    # Check for Class 9 chain
    has_chain = False
    for i in range(len(classes) - 1):
        if classes[i] == 9 and classes[i + 1] == 9:
            has_chain = True
            break

    if has_chain:
        folio, line = key
        # Mark Class 9 tokens
        marked = []
        for w, c in zip(words, classes):
            if c == 9:
                marked.append(f"[{w}]")
            else:
                marked.append(w)
        print(f"  {folio}.{line}: {' '.join(marked)}")
        shown += 1
        if shown >= 15:
            break

# 10. MORPHOLOGICAL ANALYSIS
print("\n" + "-" * 70)
print("10. CLASS 9 MORPHOLOGY")
print("-" * 70)

print("\nClass 9 token morphology:")
for tok in c9_tokens:
    m = morph.extract(tok)
    if m:
        print(f"  {tok}: prefix={m.prefix}, middle={m.middle}, suffix={m.suffix}")

# What MIDDLEs are in Class 9?
c9_middles = set()
for tok in c9_tokens:
    m = morph.extract(tok)
    if m and m.middle:
        c9_middles.add(m.middle)

print(f"\nClass 9 MIDDLEs: {c9_middles}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

aiin_count = token_counts['aiin']
or_count = token_counts['or']
o_count = token_counts['o']

print(f"""
1. CLASS 9 COMPOSITION:
   - aiin: {aiin_count} ({aiin_count/c9_total*100:.1f}%)
   - or: {or_count} ({or_count/c9_total*100:.1f}%)
   - o: {o_count} ({o_count/c9_total*100:.1f}%)

2. CHAIN STATISTICS:
   - Total chains: {len(c9_chains)}
   - Pure aiin chains: {len(pure_aiin_chains)}
   - Most common pair: {chain_pairs.most_common(1)[0] if chain_pairs else 'N/A'}

3. CHAIN PATTERNS:
   - aiin->aiin is dominant ({chain_pairs.get('aiin->aiin', 0)} occurrences)
   - Chains are 2-3 tokens typically

4. SECTION PATTERNS:
   - Highest chain rate: {max(section_chains.keys(), key=lambda s: sum(c['length'] for c in section_chains[s])/section_c9_totals[s]*100 if section_c9_totals[s] > 0 else 0)}

5. INTERPRETATION:
   - Class 9 chaining is primarily aiin repetition
   - aiin-aiin may function as iteration/continuation marker
   - Distinct from other FREQUENT tokens (no chaining)
""")

# Save results
results = {
    'class9_tokens': c9_tokens,
    'token_frequencies': {tok: token_counts[tok] for tok in c9_tokens},
    'total_chains': len(c9_chains),
    'pure_aiin_chains': len(pure_aiin_chains),
    'chain_pairs': dict(chain_pairs),
    'chain_lengths': dict(chain_lengths),
    'chains_by_regime': {r: len(chains) for r, chains in regime_chains.items()},
    'chains_by_section': {s: len(chains) for s, chains in section_chains.items()}
}

with open(RESULTS / 'class9_chaining_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'class9_chaining_analysis.json'}")
