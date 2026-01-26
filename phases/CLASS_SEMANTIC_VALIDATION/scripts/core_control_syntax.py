"""
Q3: CORE_CONTROL Syntactic Patterns

Test whether CORE_CONTROL tokens (Classes 10, 11, 17) function as
conditional triggers with detectable "if-then" patterns.

Hypothesis: If CORE_CONTROL tokens are state-checking operators,
they should:
1. Appear at line start (triggers)
2. Be followed by consistent action patterns
3. Have predictable follow-on classes
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

# The format is {"token_to_class": {token: class_id, ...}}
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Build reverse map: class_id -> [tokens]
class_map = defaultdict(list)
for tok, cls in token_to_class.items():
    class_map[str(cls)].append(tok)

# Class to role mapping
CLASS_ROLES = {
    10: 'CORE_CONTROL', 11: 'CORE_CONTROL', 17: 'CORE_CONTROL',
    32: 'ENERGY_OPERATOR', 33: 'ENERGY_OPERATOR', 36: 'ENERGY_OPERATOR',
    8: 'ENERGY_OPERATOR', 31: 'ENERGY_OPERATOR', 34: 'ENERGY_OPERATOR',
    7: 'FLOW_OPERATOR', 30: 'FLOW_OPERATOR', 38: 'FLOW_OPERATOR', 40: 'FLOW_OPERATOR',
    9: 'FREQUENT_OPERATOR', 20: 'FREQUENT_OPERATOR', 21: 'FREQUENT_OPERATOR', 23: 'FREQUENT_OPERATOR',
}

# CORE_CONTROL classes
CORE_CONTROL_CLASSES = {10, 11, 17}

print("=" * 60)
print("Q3: CORE_CONTROL SYNTACTIC PATTERNS")
print("=" * 60)

# Get CORE_CONTROL tokens
cc_tokens = set()
for cls in CORE_CONTROL_CLASSES:
    cc_tokens.update(class_map.get(str(cls), []))

print(f"\nCORE_CONTROL tokens (Classes {CORE_CONTROL_CLASSES}):")
for cls in CORE_CONTROL_CLASSES:
    cls_tokens = class_map.get(str(cls), [])
    print(f"  Class {cls}: {cls_tokens}")

# Group tokens by folio/line
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    lines[(token.folio, token.line)].append(word)

print("\n" + "-" * 40)
print("POSITIONAL ANALYSIS")
print("-" * 40)

# Where do CORE_CONTROL tokens appear in lines?
cc_positions = []
all_positions = []

for (folio, line), words in lines.items():
    n = len(words)
    if n < 2:
        continue

    for i, w in enumerate(words):
        rel_pos = i / (n - 1) if n > 1 else 0.5
        all_positions.append(rel_pos)
        if w in cc_tokens:
            cc_positions.append((rel_pos, i, w, folio, line))

print(f"\nTotal CORE_CONTROL occurrences: {len(cc_positions)}")

if cc_positions:
    positions_only = [p[0] for p in cc_positions]
    print(f"Mean position: {sum(positions_only)/len(positions_only):.3f} (0=start, 1=end)")

    initial = sum(1 for p in positions_only if p < 0.2)
    middle = sum(1 for p in positions_only if 0.2 <= p <= 0.8)
    final = sum(1 for p in positions_only if p > 0.8)

    print(f"Initial (0-0.2): {initial} ({initial/len(positions_only):.1%})")
    print(f"Middle (0.2-0.8): {middle} ({middle/len(positions_only):.1%})")
    print(f"Final (0.8-1.0): {final} ({final/len(positions_only):.1%})")

    all_initial = sum(1 for p in all_positions if p < 0.2)
    all_total = len(all_positions)
    baseline_initial = all_initial / all_total if all_total > 0 else 0

    cc_initial_rate = initial / len(positions_only)
    initial_enrichment = cc_initial_rate / baseline_initial if baseline_initial > 0 else 0

    print(f"\nBaseline initial rate: {baseline_initial:.1%}")
    print(f"CORE_CONTROL initial rate: {cc_initial_rate:.1%}")
    print(f"Initial enrichment: {initial_enrichment:.2f}x")
else:
    initial_enrichment = 0
    cc_initial_rate = 0

print("\n" + "-" * 40)
print("FOLLOW-ON PATTERN ANALYSIS")
print("-" * 40)

followon_classes = defaultdict(int)
followon_roles = defaultdict(int)
followon_tokens = defaultdict(int)

patterns_2 = defaultdict(int)
patterns_3 = defaultdict(int)

for (folio, line), words in lines.items():
    n = len(words)

    for i, w in enumerate(words):
        if w in cc_tokens and i < n - 1:
            next_word = words[i + 1]
            next_class = token_to_class.get(next_word)
            followon_tokens[next_word] += 1
            if next_class:
                followon_classes[next_class] += 1
                followon_roles[CLASS_ROLES.get(next_class, 'OTHER')] += 1

            if i < n - 2:
                next2 = words[i + 2]
                class2 = token_to_class.get(next2)
                if next_class and class2:
                    patterns_2[(next_class, class2)] += 1

            if i < n - 3:
                next3 = words[i + 3]
                class3 = token_to_class.get(next3)
                if next_class and class2 and class3:
                    patterns_3[(next_class, class2, class3)] += 1

print("\nTop 10 follow-on classes after CORE_CONTROL:")
for cls, count in sorted(followon_classes.items(), key=lambda x: -x[1])[:10]:
    role = CLASS_ROLES.get(cls, 'OTHER')
    cls_tokens = class_map.get(str(cls), [])[:3]
    print(f"  Class {cls} ({role}): {count} - tokens: {cls_tokens}")

print("\nFollow-on by role:")
total_followon = sum(followon_roles.values())
for role, count in sorted(followon_roles.items(), key=lambda x: -x[1]):
    print(f"  {role}: {count} ({count/total_followon:.1%})" if total_followon > 0 else f"  {role}: {count}")

print("\n" + "-" * 40)
print("COMMON PATTERNS AFTER CORE_CONTROL")
print("-" * 40)

print("\nTop 2-step patterns (CC -> X -> Y):")
for (c1, c2), count in sorted(patterns_2.items(), key=lambda x: -x[1])[:10]:
    r1 = CLASS_ROLES.get(c1, '?')
    r2 = CLASS_ROLES.get(c2, '?')
    print(f"  CC -> {c1}({r1}) -> {c2}({r2}): {count}")

print("\nTop 3-step patterns (CC -> X -> Y -> Z):")
for (c1, c2, c3), count in sorted(patterns_3.items(), key=lambda x: -x[1])[:10]:
    r1 = CLASS_ROLES.get(c1, '?')
    r2 = CLASS_ROLES.get(c2, '?')
    r3 = CLASS_ROLES.get(c3, '?')
    print(f"  CC -> {c1}({r1}) -> {c2}({r2}) -> {c3}({r3}): {count}")

print("\n" + "-" * 40)
print("CLASS-SPECIFIC PATTERNS")
print("-" * 40)

for cc_class in sorted(CORE_CONTROL_CLASSES):
    cc_class_tokens = set(class_map.get(str(cc_class), []))

    followon_for_class = defaultdict(int)

    for (folio, line), words in lines.items():
        n = len(words)

        for i, w in enumerate(words):
            if w in cc_class_tokens and i < n - 1:
                next_word = words[i + 1]
                next_class = token_to_class.get(next_word)
                if next_class:
                    followon_for_class[next_class] += 1

    print(f"\nClass {cc_class} follow-on classes:")
    total = sum(followon_for_class.values())
    for cls, count in sorted(followon_for_class.items(), key=lambda x: -x[1])[:5]:
        role = CLASS_ROLES.get(cls, 'OTHER')
        print(f"  -> Class {cls} ({role}): {count} ({count/total:.1%})" if total > 0 else f"  -> Class {cls}: {count}")

print("\n" + "-" * 40)
print("CONDITIONAL STRUCTURE TEST")
print("-" * 40)

lines_starting_cc = []
lines_not_starting_cc = []

for (folio, line), words in lines.items():
    if len(words) < 3:
        continue

    first_word = words[0]
    if first_word in cc_tokens:
        lines_starting_cc.append({
            'folio': folio,
            'line': line,
            'first': first_word,
            'first_class': token_to_class.get(first_word),
            'pattern': [token_to_class.get(w) for w in words[:5] if token_to_class.get(w)]
        })
    else:
        first_class = token_to_class.get(first_word)
        if first_class:
            lines_not_starting_cc.append({
                'first_class': first_class,
                'pattern': [token_to_class.get(w) for w in words[:5] if token_to_class.get(w)]
            })

print(f"\nLines starting with CORE_CONTROL: {len(lines_starting_cc)}")
print(f"Lines starting with other classes: {len(lines_not_starting_cc)}")

if lines_starting_cc:
    second_class_cc = Counter(l['pattern'][1] for l in lines_starting_cc if len(l['pattern']) > 1)
    print("\n2nd position class in CC-starting lines:")
    for cls, count in second_class_cc.most_common(5):
        role = CLASS_ROLES.get(cls, 'OTHER')
        print(f"  Class {cls} ({role}): {count}")

    second_class_other = Counter(l['pattern'][1] if len(l['pattern']) > 1 else None
                                  for l in lines_not_starting_cc)
    print("\n2nd position class in non-CC-starting lines:")
    for cls, count in second_class_other.most_common(5):
        if cls:
            role = CLASS_ROLES.get(cls, 'OTHER')
            print(f"  Class {cls} ({role}): {count}")

    print("\nExample CORE_CONTROL-starting lines:")
    for l in lines_starting_cc[:10]:
        pattern_str = ' -> '.join(str(c) for c in l['pattern'])
        print(f"  {l['folio']}:{l['line']}: [{l['first']}] {pattern_str}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print("\nHypothesis: CORE_CONTROL tokens function as conditional triggers")

if cc_positions:
    initial_rate = initial / len(cc_positions)
    energy_followon = followon_roles.get('ENERGY_OPERATOR', 0)
    energy_rate = energy_followon / total_followon if total_followon > 0 else 0

    print(f"\n1. Initial position: {initial_rate:.1%} (enrichment: {initial_enrichment:.2f}x)")
    print(f"2. Followed by ENERGY_OPERATOR: {energy_rate:.1%}")
    print(f"3. Lines starting with CC: {len(lines_starting_cc)}")

    if initial_rate > 0.25 and initial_enrichment > 1.5:
        print("\n=> SUPPORTED: CORE_CONTROL shows trigger-like behavior")
        print("   - Strong initial position preference")
        if energy_rate > 0.3:
            print("   - Followed by ENERGY operations (action pattern)")
    elif initial_rate > 0.15:
        print("\n=> PARTIAL SUPPORT: CORE_CONTROL shows some trigger characteristics")
    else:
        print("\n=> NOT SUPPORTED: CORE_CONTROL lacks trigger characteristics")
else:
    print("\n=> INSUFFICIENT DATA: No CORE_CONTROL tokens found")

# Save results
results = {
    'total_cc_occurrences': len(cc_positions),
    'position_distribution': {
        'initial': initial if cc_positions else 0,
        'middle': middle if cc_positions else 0,
        'final': final if cc_positions else 0
    },
    'initial_enrichment': initial_enrichment,
    'followon_roles': dict(followon_roles),
    'followon_classes': dict(followon_classes),
    'top_2step_patterns': {f"{c1},{c2}": count for (c1, c2), count
                           in sorted(patterns_2.items(), key=lambda x: -x[1])[:20]},
    'cc_starting_lines': len(lines_starting_cc)
}

with open(RESULTS / 'core_control_syntax.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'core_control_syntax.json'}")
