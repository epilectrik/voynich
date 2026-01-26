"""
Q19: Singleton Class Analysis

From C557: Class 10 is a singleton (only daiin). Are there other singleton instruction classes?
What makes singletons special?
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

print("=" * 70)
print("Q19: SINGLETON CLASS ANALYSIS")
print("=" * 70)

# 1. CLASS SIZE DISTRIBUTION
print("\n" + "-" * 70)
print("1. CLASS SIZE DISTRIBUTION")
print("-" * 70)

class_sizes = {cls: len(toks) for cls, toks in class_to_tokens.items()}
size_counts = Counter(class_sizes.values())

print("\n| Size | Count | Classes |")
print("|------|-------|---------|")
for size in sorted(size_counts.keys())[:20]:
    count = size_counts[size]
    classes = [str(cls) for cls, s in class_sizes.items() if s == size]
    classes_str = ', '.join(classes[:5])
    if len(classes) > 5:
        classes_str += f", ... (+{len(classes)-5})"
    print(f"| {size:4d} | {count:5d} | {classes_str} |")

# 2. SINGLETON CLASSES
print("\n" + "-" * 70)
print("2. SINGLETON CLASSES (size=1)")
print("-" * 70)

singletons = {cls: list(toks)[0] for cls, toks in class_to_tokens.items() if len(toks) == 1}
print(f"\nTotal singleton classes: {len(singletons)}")

print("\n| Class | Token | Role | Morphology |")
print("|-------|-------|------|------------|")
for cls, tok in sorted(singletons.items()):
    role = get_role(cls)
    m = morph.extract(tok)
    if m:
        morph_str = f"{m.prefix or '-'}/{m.middle or '-'}/{m.suffix or '-'}"
    else:
        morph_str = "N/A"
    print(f"| {cls:5d} | {tok:10s} | {role} | {morph_str:15s} |")

# 3. SINGLETON TOKEN FREQUENCIES
print("\n" + "-" * 70)
print("3. SINGLETON TOKEN FREQUENCIES")
print("-" * 70)

singleton_freqs = {}
for cls, tok in singletons.items():
    count = sum(1 for t in tokens if t.word.replace('*', '').strip() == tok)
    singleton_freqs[cls] = {'token': tok, 'count': count, 'role': get_role(cls)}

print("\n| Class | Token | Role | Count | Rank |")
print("|-------|-------|------|-------|------|")
sorted_singletons = sorted(singleton_freqs.items(), key=lambda x: -x[1]['count'])
for rank, (cls, data) in enumerate(sorted_singletons, 1):
    print(f"| {cls:5d} | {data['token']:10s} | {data['role']} | {data['count']:5d} | #{rank} |")

# 4. SINGLETON LINE-INITIAL RATES
print("\n" + "-" * 70)
print("4. SINGLETON LINE-INITIAL RATES")
print("-" * 70)

singleton_positions = {}
for cls, tok in singletons.items():
    total = 0
    initial = 0
    for t in tokens:
        word = t.word.replace('*', '').strip()
        if word == tok:
            total += 1
            if t.line_initial:
                initial += 1
    if total > 0:
        singleton_positions[cls] = {
            'token': tok,
            'total': total,
            'initial': initial,
            'rate': initial / total * 100
        }

print("\n| Class | Token | Role | Total | Initial | Rate |")
print("|-------|-------|------|-------|---------|------|")
for cls, data in sorted(singleton_positions.items(), key=lambda x: -x[1]['rate']):
    role = get_role(cls)
    print(f"| {cls:5d} | {data['token']:10s} | {role} | {data['total']:5d} | {data['initial']:7d} | {data['rate']:5.1f}% |")

# 5. COMPARE SINGLETON VS MULTI-TOKEN CLASSES
print("\n" + "-" * 70)
print("5. SINGLETON VS MULTI-TOKEN CLASS COMPARISON")
print("-" * 70)

# Calculate aggregate statistics
singleton_classes = set(singletons.keys())
multi_token_classes = {cls for cls in class_to_tokens if cls not in singleton_classes}

# Token frequency per class type
singleton_total_tokens = sum(singleton_freqs[cls]['count'] for cls in singleton_freqs)
multi_total_tokens = 0
for cls in multi_token_classes:
    for tok in class_to_tokens[cls]:
        multi_total_tokens += sum(1 for t in tokens if t.word.replace('*', '').strip() == tok)

print(f"\nSingleton classes: {len(singleton_classes)}")
print(f"Multi-token classes: {len(multi_token_classes)}")
print(f"\nSingleton total tokens: {singleton_total_tokens}")
print(f"Multi-token total tokens: {multi_total_tokens}")
print(f"\nAvg tokens per singleton class: {singleton_total_tokens / len(singleton_classes):.1f}")
print(f"Avg tokens per multi-token class: {multi_total_tokens / len(multi_token_classes):.1f}")

# Role distribution
singleton_roles = Counter(get_role(cls) for cls in singleton_classes)
multi_roles = Counter(get_role(cls) for cls in multi_token_classes)

print("\nRole distribution:")
print("| Role | Singleton | Multi-Token |")
print("|------|-----------|-------------|")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']:
    s_count = singleton_roles.get(role, 0)
    m_count = multi_roles.get(role, 0)
    s_pct = s_count / len(singleton_classes) * 100 if singleton_classes else 0
    m_pct = m_count / len(multi_token_classes) * 100 if multi_token_classes else 0
    print(f"| {role}   | {s_count} ({s_pct:4.1f}%) | {m_count} ({m_pct:4.1f}%) |")

# 6. SINGLETON LINE-FINAL RATES
print("\n" + "-" * 70)
print("6. SINGLETON LINE-FINAL RATES")
print("-" * 70)

singleton_final = {}
for cls, tok in singletons.items():
    total = 0
    final = 0
    for t in tokens:
        word = t.word.replace('*', '').strip()
        if word == tok:
            total += 1
            if t.line_final:
                final += 1
    if total > 0:
        singleton_final[cls] = {
            'token': tok,
            'total': total,
            'final': final,
            'rate': final / total * 100
        }

print("\n| Class | Token | Role | Total | Final | Rate |")
print("|-------|-------|------|-------|-------|------|")
for cls, data in sorted(singleton_final.items(), key=lambda x: -x[1]['rate']):
    role = get_role(cls)
    print(f"| {cls:5d} | {data['token']:10s} | {role} | {data['total']:5d} | {data['final']:5d} | {data['rate']:5.1f}% |")

# 7. SMALL CLASSES (SIZE 2-3)
print("\n" + "-" * 70)
print("7. SMALL CLASSES (SIZE 2-3)")
print("-" * 70)

small_classes = {cls: list(toks) for cls, toks in class_to_tokens.items() if 2 <= len(toks) <= 3}
print(f"\nTotal small classes: {len(small_classes)}")

print("\n| Class | Role | Tokens |")
print("|-------|------|--------|")
for cls, toks in sorted(small_classes.items()):
    role = get_role(cls)
    print(f"| {cls:5d} | {role} | {', '.join(sorted(toks))} |")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Key singletons
key_singletons = [(cls, singleton_freqs[cls]) for cls in singleton_freqs if singleton_freqs[cls]['count'] >= 50]
key_singletons.sort(key=lambda x: -x[1]['count'])

print(f"""
1. SINGLETON STATISTICS:
   - Total singleton classes: {len(singletons)}
   - Total small classes (2-3): {len(small_classes)}
   - Total multi-token classes: {len(multi_token_classes)}

2. KEY SINGLETONS (>= 50 occurrences):
""")
for cls, data in key_singletons:
    pos = singleton_positions.get(cls, {})
    initial_rate = pos.get('rate', 0)
    final_rate = singleton_final.get(cls, {}).get('rate', 0)
    print(f"   - Class {cls} ({data['token']}): {data['count']} occurrences, {initial_rate:.1f}% initial, {final_rate:.1f}% final")

print(f"""
3. SINGLETON ROLE DISTRIBUTION:
   - CC: {singleton_roles.get('CC', 0)} singletons
   - EN: {singleton_roles.get('EN', 0)} singletons
   - FL: {singleton_roles.get('FL', 0)} singletons
   - FQ: {singleton_roles.get('FQ', 0)} singletons
   - AX: {singleton_roles.get('AX', 0)} singletons

4. INTERPRETATION:
   - Singletons are unique vocabulary items within their instruction class
   - High-frequency singletons like daiin (Class 10) may have specialized grammatical functions
   - Low-frequency singletons may be rare operations or edge cases
""")

# Save results
results = {
    'singletons': {str(cls): {'token': tok, 'role': get_role(cls)} for cls, tok in singletons.items()},
    'singleton_frequencies': {str(cls): data for cls, data in singleton_freqs.items()},
    'singleton_positions': {str(cls): data for cls, data in singleton_positions.items()},
    'class_size_distribution': dict(size_counts),
    'role_distribution': {
        'singletons': dict(singleton_roles),
        'multi_token': dict(multi_roles)
    }
}

with open(RESULTS / 'singleton_class_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'singleton_class_analysis.json'}")
