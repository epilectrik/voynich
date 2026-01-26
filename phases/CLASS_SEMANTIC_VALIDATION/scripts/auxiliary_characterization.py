"""
Q6: AUXILIARY Role Characterization

The 20 AUXILIARY classes show weak self-chaining (1.06x) unlike semantic roles.
Analyze what distinguishes AUXILIARY from semantic roles.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Class to tokens (invert mapping)
class_to_tokens = defaultdict(list)
for tok, cls in token_to_class.items():
    class_to_tokens[cls].append(tok)

# Role mapping
SEMANTIC_CLASSES = {
    # CORE_CONTROL
    10, 11, 17,
    # ENERGY_OPERATOR
    8, 31, 32, 33, 34, 36,
    # FLOW_OPERATOR
    7, 30, 38, 40,
    # FREQUENT_OPERATOR
    9, 20, 21, 23,
}

# All other classes are AUXILIARY (20 classes)
ALL_CLASSES = set(token_to_class.values())
AUXILIARY_CLASSES = ALL_CLASSES - SEMANTIC_CLASSES

print("=" * 70)
print("Q6: AUXILIARY ROLE CHARACTERIZATION")
print("=" * 70)

print(f"\nTotal classes: {len(ALL_CLASSES)}")
print(f"Semantic classes: {len(SEMANTIC_CLASSES)}")
print(f"AUXILIARY classes: {len(AUXILIARY_CLASSES)}")
print(f"\nAUXILIARY class numbers: {sorted(AUXILIARY_CLASSES)}")

# Load REGIME
with open(REGIME_FILE) as f:
    regime_data = json.load(f)

folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

# Group tokens by folio and line
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    line = token.line
    cls = token_to_class.get(word)
    role = 'SEM' if cls in SEMANTIC_CLASSES else ('AUX' if cls in AUXILIARY_CLASSES else 'UN')
    lines[(folio, line)].append({
        'word': word,
        'class': cls,
        'role': role,
        'folio': folio
    })

# 1. CLASS SIZE COMPARISON
print("\n" + "-" * 70)
print("1. CLASS SIZE (tokens per class)")
print("-" * 70)

class_counts = defaultdict(int)
for token in tokens:
    word = token.word.replace('*', '').strip()
    cls = token_to_class.get(word)
    if cls:
        class_counts[cls] += 1

semantic_sizes = [class_counts[c] for c in SEMANTIC_CLASSES if c in class_counts]
auxiliary_sizes = [class_counts[c] for c in AUXILIARY_CLASSES if c in class_counts]

print(f"\nSemantic class sizes: mean={np.mean(semantic_sizes):.1f}, median={np.median(semantic_sizes):.1f}")
print(f"AUXILIARY class sizes: mean={np.mean(auxiliary_sizes):.1f}, median={np.median(auxiliary_sizes):.1f}")

# Mann-Whitney test
stat, p = stats.mannwhitneyu(semantic_sizes, auxiliary_sizes, alternative='greater')
print(f"Mann-Whitney (semantic > auxiliary): U={stat:.0f}, p={p:.4f}")

print("\n| Role | Class | Token Count |")
print("|------|-------|-------------|")
for cls in sorted(SEMANTIC_CLASSES):
    print(f"| SEM  | {cls:4d} | {class_counts.get(cls, 0):11d} |")
print("|------|-------|-------------|")
for cls in sorted(AUXILIARY_CLASSES)[:10]:
    print(f"| AUX  | {cls:4d} | {class_counts.get(cls, 0):11d} |")
print("| ...  | ...   | ...         |")

# 2. POSITION ANALYSIS
print("\n" + "-" * 70)
print("2. POSITIONAL BEHAVIOR")
print("-" * 70)

# Track first/middle/last position for each class
class_positions = defaultdict(lambda: {'first': 0, 'middle': 0, 'last': 0, 'total': 0})

for (folio, line), word_data in lines.items():
    n = len(word_data)
    if n == 0:
        continue

    for i, wd in enumerate(word_data):
        cls = wd['class']
        if cls is None:
            continue

        class_positions[cls]['total'] += 1
        if i == 0:
            class_positions[cls]['first'] += 1
        elif i == n - 1:
            class_positions[cls]['last'] += 1
        else:
            class_positions[cls]['middle'] += 1

# Calculate positional bias for each class
print("\n| Class | Role | First% | Middle% | Last% | Bias |")
print("|-------|------|--------|---------|-------|------|")

semantic_first = []
semantic_last = []
auxiliary_first = []
auxiliary_last = []

for cls in sorted(ALL_CLASSES):
    pos = class_positions[cls]
    total = pos['total']
    if total < 10:
        continue

    first_rate = pos['first'] / total
    middle_rate = pos['middle'] / total
    last_rate = pos['last'] / total

    # Bias: > 0.5 = terminal biased, < 0.5 = initial biased
    if first_rate + last_rate > 0:
        terminal_bias = last_rate / (first_rate + last_rate)
    else:
        terminal_bias = 0.5

    role = 'SEM' if cls in SEMANTIC_CLASSES else 'AUX'
    bias = 'LAST' if terminal_bias > 0.55 else ('FIRST' if terminal_bias < 0.45 else 'MID')

    if role == 'SEM':
        semantic_first.append(first_rate)
        semantic_last.append(last_rate)
    else:
        auxiliary_first.append(first_rate)
        auxiliary_last.append(last_rate)

    if cls in SEMANTIC_CLASSES or cls in list(sorted(AUXILIARY_CLASSES))[:10]:
        print(f"| {cls:5d} | {role}  | {first_rate*100:5.1f}% | {middle_rate*100:6.1f}% | {last_rate*100:4.1f}% | {bias:5s} |")

print(f"\nSemantic classes: mean first={np.mean(semantic_first)*100:.1f}%, last={np.mean(semantic_last)*100:.1f}%")
print(f"AUXILIARY classes: mean first={np.mean(auxiliary_first)*100:.1f}%, last={np.mean(auxiliary_last)*100:.1f}%")

# 3. REGIME DISTRIBUTION
print("\n" + "-" * 70)
print("3. REGIME DISTRIBUTION")
print("-" * 70)

# Count class occurrences by REGIME
class_regime = defaultdict(lambda: defaultdict(int))
for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    cls = token_to_class.get(word)
    regime = folio_regime.get(folio)
    if cls and regime:
        class_regime[cls][regime] += 1

# Calculate REGIME uniformity (entropy) for each class
def entropy(counts):
    total = sum(counts.values())
    if total == 0:
        return 0
    probs = [c / total for c in counts.values() if c > 0]
    return -sum(p * np.log2(p) for p in probs)

max_entropy = np.log2(4)  # 4 REGIMEs

print("\n| Class | Role | R1% | R2% | R3% | R4% | Entropy |")
print("|-------|------|-----|-----|-----|-----|---------|")

semantic_entropies = []
auxiliary_entropies = []

for cls in sorted(ALL_CLASSES):
    regimes = class_regime[cls]
    total = sum(regimes.values())
    if total < 50:
        continue

    ent = entropy(regimes) / max_entropy  # Normalized 0-1
    role = 'SEM' if cls in SEMANTIC_CLASSES else 'AUX'

    if role == 'SEM':
        semantic_entropies.append(ent)
    else:
        auxiliary_entropies.append(ent)

    r1 = regimes.get('REGIME_1', 0) / total if total > 0 else 0
    r2 = regimes.get('REGIME_2', 0) / total if total > 0 else 0
    r3 = regimes.get('REGIME_3', 0) / total if total > 0 else 0
    r4 = regimes.get('REGIME_4', 0) / total if total > 0 else 0

    if cls in SEMANTIC_CLASSES or cls in list(sorted(AUXILIARY_CLASSES))[:5]:
        print(f"| {cls:5d} | {role}  | {r1*100:3.0f} | {r2*100:3.0f} | {r3*100:3.0f} | {r4*100:3.0f} | {ent:.3f}   |")

print(f"\nSemantic REGIME entropy: mean={np.mean(semantic_entropies):.3f}")
print(f"AUXILIARY REGIME entropy: mean={np.mean(auxiliary_entropies):.3f}")
stat, p = stats.mannwhitneyu(auxiliary_entropies, semantic_entropies, alternative='greater')
print(f"Mann-Whitney (auxiliary more uniform): U={stat:.0f}, p={p:.4f}")

# 4. CO-OCCURRENCE WITH SEMANTIC ROLES
print("\n" + "-" * 70)
print("4. CO-OCCURRENCE WITH SEMANTIC ROLES")
print("-" * 70)

# For each AUXILIARY class, count co-occurrence with each semantic role
aux_cooccurrence = defaultdict(lambda: defaultdict(int))

for (folio, line), word_data in lines.items():
    classes_in_line = [wd['class'] for wd in word_data if wd['class'] is not None]

    for aux_cls in AUXILIARY_CLASSES:
        if aux_cls not in classes_in_line:
            continue

        # Count which semantic roles appear in same line
        for cls in classes_in_line:
            if cls in SEMANTIC_CLASSES:
                role = 'CC' if cls in {10, 11, 17} else \
                       'EN' if cls in {8, 31, 32, 33, 34, 36} else \
                       'FL' if cls in {7, 30, 38, 40} else 'FQ'
                aux_cooccurrence[aux_cls][role] += 1

print("\nTop AUXILIARY classes by ENERGY co-occurrence:")
print("| Class | CC | EN | FL | FQ | EN% |")
print("|-------|----|----|----|----|-----|")

energy_preference = []
for aux_cls in sorted(AUXILIARY_CLASSES):
    cooc = aux_cooccurrence[aux_cls]
    total = sum(cooc.values())
    if total < 50:
        continue

    en_rate = cooc['EN'] / total if total > 0 else 0
    energy_preference.append((aux_cls, en_rate, cooc))

# Sort by ENERGY preference
energy_preference.sort(key=lambda x: x[1], reverse=True)
for aux_cls, en_rate, cooc in energy_preference[:10]:
    total = sum(cooc.values())
    print(f"| {aux_cls:5d} | {cooc['CC']:2d} | {cooc['EN']:2d} | {cooc['FL']:2d} | {cooc['FQ']:2d} | {en_rate*100:3.0f}% |")

# 5. UNIQUE VS COMMON TOKENS
print("\n" + "-" * 70)
print("5. TOKEN DIVERSITY WITHIN CLASS")
print("-" * 70)

print("\n| Class | Role | Unique Tokens | Total Occur | Ratio |")
print("|-------|------|---------------|-------------|-------|")

semantic_diversity = []
auxiliary_diversity = []

for cls in sorted(ALL_CLASSES):
    tokens_in_class = class_to_tokens.get(cls, [])
    unique = len(tokens_in_class)
    total = class_counts.get(cls, 0)

    if total < 50:
        continue

    ratio = unique / total if total > 0 else 0
    role = 'SEM' if cls in SEMANTIC_CLASSES else 'AUX'

    if role == 'SEM':
        semantic_diversity.append(ratio)
    else:
        auxiliary_diversity.append(ratio)

    if cls in SEMANTIC_CLASSES or ratio > 0.3:
        print(f"| {cls:5d} | {role}  | {unique:13d} | {total:11d} | {ratio:.3f} |")

print(f"\nSemantic token diversity: mean={np.mean(semantic_diversity):.3f}")
print(f"AUXILIARY token diversity: mean={np.mean(auxiliary_diversity):.3f}")

# 6. SUMMARY
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
Key differences between SEMANTIC and AUXILIARY roles:

1. CLASS SIZE: Semantic classes tend to be {"larger" if np.mean(semantic_sizes) > np.mean(auxiliary_sizes) else "smaller"}
   (mean {np.mean(semantic_sizes):.0f} vs {np.mean(auxiliary_sizes):.0f} tokens)

2. REGIME UNIFORMITY: AUXILIARY classes are {"more uniform" if np.mean(auxiliary_entropies) > np.mean(semantic_entropies) else "less uniform"}
   (entropy {np.mean(auxiliary_entropies):.3f} vs {np.mean(semantic_entropies):.3f})

3. TOKEN DIVERSITY: AUXILIARY classes have {"higher" if np.mean(auxiliary_diversity) > np.mean(semantic_diversity) else "lower"}
   token-per-occurrence diversity ({np.mean(auxiliary_diversity):.3f} vs {np.mean(semantic_diversity):.3f})
""")

# Save results
results = {
    'semantic_classes': list(SEMANTIC_CLASSES),
    'auxiliary_classes': list(AUXILIARY_CLASSES),
    'class_sizes': {
        'semantic_mean': float(np.mean(semantic_sizes)),
        'auxiliary_mean': float(np.mean(auxiliary_sizes)),
    },
    'regime_entropy': {
        'semantic_mean': float(np.mean(semantic_entropies)),
        'auxiliary_mean': float(np.mean(auxiliary_entropies)),
    },
    'token_diversity': {
        'semantic_mean': float(np.mean(semantic_diversity)),
        'auxiliary_mean': float(np.mean(auxiliary_diversity)),
    }
}

with open(RESULTS / 'auxiliary_characterization.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'auxiliary_characterization.json'}")
