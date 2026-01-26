"""
Q17: daiin Opener Function

Why does "daiin" start 3.5% of lines? Is there a structural function to this line-initial token?
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
print("Q17: DAIIN OPENER FUNCTION")
print("=" * 70)

# 1. BASIC STATISTICS
print("\n" + "-" * 70)
print("1. BASIC STATISTICS")
print("-" * 70)

# Count line-initial tokens
line_initial_counts = Counter()
total_line_initial = 0

for token in tokens:
    if token.line_initial:
        word = token.word.replace('*', '').strip()
        line_initial_counts[word] += 1
        total_line_initial += 1

print(f"\nTotal line-initial tokens: {total_line_initial}")
print(f"\nTop 15 line-initial tokens:")
print("| Token | Count | % of Line Initials |")
print("|-------|-------|-------------------|")
for tok, count in line_initial_counts.most_common(15):
    pct = count / total_line_initial * 100
    print(f"| {tok:10s} | {count:5d} | {pct:16.1f}% |")

# daiin statistics
daiin_initial = line_initial_counts['daiin']
daiin_total = sum(1 for t in tokens if t.word.replace('*', '').strip() == 'daiin')
print(f"\ndaiin: {daiin_initial}/{daiin_total} occurrences are line-initial ({daiin_initial/daiin_total*100:.1f}%)")

# 2. DAIIN MORPHOLOGY
print("\n" + "-" * 70)
print("2. DAIIN MORPHOLOGY")
print("-" * 70)

m = morph.extract('daiin')
if m:
    print(f"\ndaiin morphology:")
    print(f"  Articulator: {m.articulator}")
    print(f"  Prefix: {m.prefix}")
    print(f"  Middle: {m.middle}")
    print(f"  Suffix: {m.suffix}")

# daiin class
daiin_class = token_to_class.get('daiin')
daiin_role = get_role(daiin_class)
print(f"\ndaiin class: {daiin_class}")
print(f"daiin role: {daiin_role}")

# 3. DAIIN BY REGIME
print("\n" + "-" * 70)
print("3. DAIIN BY REGIME")
print("-" * 70)

daiin_regime = defaultdict(lambda: {'initial': 0, 'total': 0})
regime_totals = defaultdict(int)

for token in tokens:
    word = token.word.replace('*', '').strip()
    regime = folio_regime.get(token.folio, 'UNKNOWN')
    regime_totals[regime] += 1

    if word == 'daiin':
        daiin_regime[regime]['total'] += 1
        if token.line_initial:
            daiin_regime[regime]['initial'] += 1

print("\n| REGIME | Total daiin | Initial | Initial% | Rate/1000 |")
print("|--------|-------------|---------|----------|-----------|")
for regime in sorted(daiin_regime.keys()):
    total = daiin_regime[regime]['total']
    initial = daiin_regime[regime]['initial']
    initial_pct = initial / total * 100 if total > 0 else 0
    rate = total / regime_totals[regime] * 1000
    print(f"| {regime} | {total:11d} | {initial:7d} | {initial_pct:7.1f}% | {rate:9.2f} |")

# 4. DAIIN BY SECTION
print("\n" + "-" * 70)
print("4. DAIIN BY SECTION")
print("-" * 70)

daiin_section = defaultdict(lambda: {'initial': 0, 'total': 0})
section_totals = defaultdict(int)

for token in tokens:
    word = token.word.replace('*', '').strip()
    section = get_section(token.folio)
    section_totals[section] += 1

    if word == 'daiin':
        daiin_section[section]['total'] += 1
        if token.line_initial:
            daiin_section[section]['initial'] += 1

print("\n| Section | Total daiin | Initial | Initial% | Rate/1000 |")
print("|---------|-------------|---------|----------|-----------|")
for section in sorted(daiin_section.keys()):
    total = daiin_section[section]['total']
    initial = daiin_section[section]['initial']
    initial_pct = initial / total * 100 if total > 0 else 0
    rate = total / section_totals[section] * 1000
    print(f"| {section:7s} | {total:11d} | {initial:7d} | {initial_pct:7.1f}% | {rate:9.2f} |")

# 5. WHAT FOLLOWS DAIIN-INITIAL LINES?
print("\n" + "-" * 70)
print("5. TOKENS FOLLOWING LINE-INITIAL DAIIN")
print("-" * 70)

# Build line-grouped tokens
line_tokens = defaultdict(list)
for token in tokens:
    key = (token.folio, token.line)
    line_tokens[key].append(token)

daiin_followers = Counter()
daiin_follower_roles = Counter()

for key, toks in line_tokens.items():
    if len(toks) >= 2:
        first_word = toks[0].word.replace('*', '').strip()
        if first_word == 'daiin':
            second_word = toks[1].word.replace('*', '').strip()
            daiin_followers[second_word] += 1
            second_class = token_to_class.get(second_word)
            second_role = get_role(second_class)
            daiin_follower_roles[second_role] += 1

print("\nTop 10 tokens following line-initial daiin:")
print("| Token | Count | Class | Role |")
print("|-------|-------|-------|------|")
for tok, count in daiin_followers.most_common(10):
    cls = token_to_class.get(tok)
    role = get_role(cls)
    print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

print("\nRole distribution after line-initial daiin:")
total_followers = sum(daiin_follower_roles.values())
for role, count in daiin_follower_roles.most_common():
    pct = count / total_followers * 100
    print(f"  {role}: {count} ({pct:.1f}%)")

# 6. COMPARE TO OTHER COMMON OPENERS
print("\n" + "-" * 70)
print("6. COMMON OPENER COMPARISON")
print("-" * 70)

# Get top 5 openers
top_openers = [tok for tok, _ in line_initial_counts.most_common(5)]
print(f"\nTop 5 openers: {top_openers}")

opener_follower_roles = defaultdict(Counter)

for key, toks in line_tokens.items():
    if len(toks) >= 2:
        first_word = toks[0].word.replace('*', '').strip()
        if first_word in top_openers:
            second_word = toks[1].word.replace('*', '').strip()
            second_class = token_to_class.get(second_word)
            second_role = get_role(second_class)
            opener_follower_roles[first_word][second_role] += 1

print("\nRole distribution after each opener:")
print("| Opener | EN% | CC% | FL% | FQ% | AX% | UN% |")
print("|--------|-----|-----|-----|-----|-----|-----|")

for opener in top_openers:
    roles = opener_follower_roles[opener]
    total = sum(roles.values())
    if total > 0:
        en_pct = roles['EN'] / total * 100
        cc_pct = roles['CC'] / total * 100
        fl_pct = roles['FL'] / total * 100
        fq_pct = roles['FQ'] / total * 100
        ax_pct = roles['AX'] / total * 100
        un_pct = roles['UN'] / total * 100
        print(f"| {opener:6s} | {en_pct:3.0f}% | {cc_pct:3.0f}% | {fl_pct:3.0f}% | {fq_pct:3.0f}% | {ax_pct:3.0f}% | {un_pct:3.0f}% |")

# 7. DAIIN CLASS PEERS
print("\n" + "-" * 70)
print("7. DAIIN CLASS PEERS (SAME INSTRUCTION CLASS)")
print("-" * 70)

# Find all tokens in same class as daiin
if daiin_class is not None:
    daiin_peers = [tok for tok, cls in token_to_class.items() if cls == daiin_class]
    print(f"\nClass {daiin_class} tokens ({len(daiin_peers)}): {sorted(daiin_peers)}")

    # Check line-initial rates for peers
    peer_initial_rates = {}
    for peer in daiin_peers:
        peer_total = sum(1 for t in tokens if t.word.replace('*', '').strip() == peer)
        peer_initial = sum(1 for t in tokens if t.word.replace('*', '').strip() == peer and t.line_initial)
        if peer_total >= 5:  # Minimum 5 occurrences
            peer_initial_rates[peer] = (peer_initial, peer_total, peer_initial / peer_total * 100)

    print("\nLine-initial rates for Class peers (min 5 occurrences):")
    print("| Token | Initial | Total | Initial% |")
    print("|-------|---------|-------|----------|")
    for peer, (initial, total, rate) in sorted(peer_initial_rates.items(), key=lambda x: -x[1][2]):
        print(f"| {peer:10s} | {initial:7d} | {total:5d} | {rate:7.1f}% |")

# 8. DAIIN MIDDLE ANALYSIS
print("\n" + "-" * 70)
print("8. TOKENS SHARING DAIIN'S MIDDLE")
print("-" * 70)

if m and m.middle:
    daiin_middle = m.middle
    print(f"\ndaiin MIDDLE: '{daiin_middle}'")

    # Find all tokens with same middle
    same_middle_tokens = []
    for token in tokens:
        word = token.word.replace('*', '').strip()
        m2 = morph.extract(word)
        if m2 and m2.middle == daiin_middle:
            same_middle_tokens.append(word)

    same_middle_counts = Counter(same_middle_tokens)
    print(f"\nTokens with MIDDLE='{daiin_middle}' ({len(same_middle_counts)} types):")
    print("| Token | Count | Class | Role |")
    print("|-------|-------|-------|------|")
    for tok, count in same_middle_counts.most_common(15):
        cls = token_to_class.get(tok)
        role = get_role(cls)
        print(f"| {tok:10s} | {count:5d} | {str(cls):5s} | {role} |")

# 9. LINE-INITIAL RATE COMPARISON
print("\n" + "-" * 70)
print("9. LINE-INITIAL RATE BY ROLE")
print("-" * 70)

role_initial = defaultdict(lambda: {'initial': 0, 'total': 0})

for token in tokens:
    word = token.word.replace('*', '').strip()
    cls = token_to_class.get(word)
    role = get_role(cls)
    role_initial[role]['total'] += 1
    if token.line_initial:
        role_initial[role]['initial'] += 1

print("\n| Role | Total | Initial | Initial% |")
print("|------|-------|---------|----------|")
for role in ['EN', 'CC', 'FL', 'FQ', 'AX', 'UN']:
    total = role_initial[role]['total']
    initial = role_initial[role]['initial']
    rate = initial / total * 100 if total > 0 else 0
    print(f"| {role}   | {total:5d} | {initial:7d} | {rate:7.1f}% |")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
1. DAIIN STATISTICS:
   - Total occurrences: {daiin_total}
   - Line-initial: {daiin_initial} ({daiin_initial/daiin_total*100:.1f}%)
   - Class: {daiin_class} (Role: {daiin_role})

2. DAIIN MORPHOLOGY:
   - Prefix: {m.prefix if m else 'N/A'}
   - Middle: {m.middle if m else 'N/A'}
   - Suffix: {m.suffix if m else 'N/A'}

3. POSITION COMPARISON:
   - daiin initial rate: {daiin_initial/daiin_total*100:.1f}%
   - Role {daiin_role} average initial rate: {role_initial[daiin_role]['initial']/role_initial[daiin_role]['total']*100:.1f}%

4. FOLLOWER PATTERN:
   - Most common follower: {daiin_followers.most_common(1)[0][0] if daiin_followers else 'N/A'}
   - Follower role distribution: {dict(daiin_follower_roles.most_common(3))}
""")

# Save results
results = {
    'daiin_stats': {
        'total': daiin_total,
        'initial': daiin_initial,
        'initial_rate': daiin_initial / daiin_total * 100
    },
    'daiin_class': daiin_class,
    'daiin_role': daiin_role,
    'daiin_morphology': {
        'prefix': m.prefix if m else None,
        'middle': m.middle if m else None,
        'suffix': m.suffix if m else None
    },
    'top_openers': [{'token': tok, 'count': count} for tok, count in line_initial_counts.most_common(10)],
    'daiin_followers': [{'token': tok, 'count': count} for tok, count in daiin_followers.most_common(10)],
    'daiin_by_regime': dict(daiin_regime),
    'daiin_by_section': dict(daiin_section)
}

with open(RESULTS / 'daiin_opener_function.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'daiin_opener_function.json'}")
