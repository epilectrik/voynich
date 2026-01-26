"""
TOKEN VARIANT DIFFERENTIATION

Material classes route to the same REGIMEs/folios but may use different TOKEN VARIANTS.
Per C506.a: PP composition affects token variants within classes (~5% variation).

Test: Within the same B instruction class, do animal and herb records
select different token variants?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("TOKEN VARIANT DIFFERENTIATION BY MATERIAL CLASS")
print("=" * 70)

# Material markers
ANIMAL_MARKERS = {
    'pp_markers': {'pch': 43.0, 'opch': 18.0, 'octh': 9.0, 'cph': 3.7, 'kch': 3.7, 'ch': 2.9, 'ckh': 2.9, 'h': 2.5},
    'positive_suffixes': {'ey', 'ol'},
    'negative_suffixes': {'y', 'dy'},
}
HERB_MARKERS = {
    'pp_markers': {'keo': 66.0, 'eok': 52.0, 'ko': 33.0, 'cho': 33.0, 'to': 33.0, 'ry': 28.0, 'eo': 3.3},
    'positive_suffixes': {'y', 'dy'},
    'negative_suffixes': {'ey', 'ol'},
}

# Build A records
a_records = defaultdict(lambda: {'middles': [], 'prefixes': [], 'suffixes': [], 'tokens': []})
for token in tx.currier_a():
    rid = f"{token.folio}:{token.line}"
    if token.word:
        m = morph.extract(token.word)
        a_records[rid]['tokens'].append(token.word)
        if m.middle: a_records[rid]['middles'].append(m.middle)
        if m.prefix: a_records[rid]['prefixes'].append(m.prefix)
        if m.suffix: a_records[rid]['suffixes'].append(m.suffix)

def score(record, markers):
    middles = record['middles']
    suffixes = record['suffixes']
    n = len(record['tokens']) or 1
    pp = sum(markers['pp_markers'].get(m, 0) for m in middles) / n
    suf = (sum(1 for s in suffixes if s in markers['positive_suffixes']) -
           sum(1 for s in suffixes if s in markers['negative_suffixes'])) / n
    return pp * 0.6 + suf * 0.4

animal_scores = {rid: score(data, ANIMAL_MARKERS) for rid, data in a_records.items()}
herb_scores = {rid: score(data, HERB_MARKERS) for rid, data in a_records.items()}

animal_vals = list(animal_scores.values())
herb_vals = list(herb_scores.values())
animal_thresh = np.mean(animal_vals) + 1.5 * np.std(animal_vals)
herb_thresh = np.mean(herb_vals) + 1.5 * np.std(herb_vals)

animal_high = {rid for rid, s in animal_scores.items() if s >= animal_thresh}
herb_high = {rid for rid, s in herb_scores.items() if s >= herb_thresh}

# Remove overlap
for rid in animal_high & herb_high:
    if animal_scores[rid] > herb_scores[rid]:
        herb_high.discard(rid)
    else:
        animal_high.discard(rid)

print(f"Animal high-confidence: {len(animal_high)}")
print(f"Herb high-confidence: {len(herb_high)}")

# Build A profiles
a_profiles = {}
for rid, data in a_records.items():
    a_profiles[rid] = {
        'middles': set(data['middles']),
        'prefixes': set(data['prefixes']) | {''},
        'suffixes': set(data['suffixes']) | {''},
    }

# Build B tokens with class info (simplified: class = PREFIX)
b_tokens = []
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        b_tokens.append({
            'word': token.word,
            'middle': m.middle or '',
            'prefix': m.prefix or '',
            'suffix': m.suffix or '',
            'class': m.prefix or 'BARE',  # Use PREFIX as class proxy
        })

print(f"Total B tokens: {len(b_tokens)}")

# Get compatible tokens for each material class
def get_compatible_tokens(records, a_profiles, b_tokens):
    compat = Counter()
    for rid in records:
        if rid in a_profiles:
            p = a_profiles[rid]
            for bt in b_tokens:
                if (bt['middle'] in p['middles'] and
                    bt['prefix'] in p['prefixes'] and
                    bt['suffix'] in p['suffixes']):
                    compat[bt['word']] += 1
    return compat

animal_tokens = get_compatible_tokens(animal_high, a_profiles, b_tokens)
herb_tokens = get_compatible_tokens(herb_high, a_profiles, b_tokens)

print(f"\nAnimal-compatible B tokens: {len(animal_tokens)}")
print(f"Herb-compatible B tokens: {len(herb_tokens)}")

# Overlap analysis
animal_set = set(animal_tokens.keys())
herb_set = set(herb_tokens.keys())

overlap = animal_set & herb_set
animal_only = animal_set - herb_set
herb_only = herb_set - animal_set

print(f"\nToken overlap:")
print(f"  Shared: {len(overlap)} ({100*len(overlap)/len(animal_set|herb_set):.1f}%)")
print(f"  Animal-only: {len(animal_only)} ({100*len(animal_only)/len(animal_set):.1f}% of animal)")
print(f"  Herb-only: {len(herb_only)} ({100*len(herb_only)/len(herb_set):.1f}% of herb)")

# Jaccard similarity
jaccard = len(overlap) / len(animal_set | herb_set)
print(f"  Jaccard similarity: {jaccard:.3f}")

# Per-class analysis
print("\n" + "=" * 70)
print("PER-CLASS TOKEN DIFFERENTIATION")
print("=" * 70)

# Group B tokens by class (PREFIX)
class_tokens = defaultdict(list)
for bt in b_tokens:
    class_tokens[bt['class']].append(bt)

print(f"\nAnalyzing {len(class_tokens)} classes (PREFIX groups)...")

class_results = []
for cls, tokens in class_tokens.items():
    # Get tokens compatible with each material class
    animal_cls = set()
    herb_cls = set()

    for bt in tokens:
        if bt['word'] in animal_set:
            animal_cls.add(bt['word'])
        if bt['word'] in herb_set:
            herb_cls.add(bt['word'])

    if len(animal_cls) > 0 and len(herb_cls) > 0:
        cls_overlap = animal_cls & herb_cls
        cls_jaccard = len(cls_overlap) / len(animal_cls | herb_cls) if (animal_cls | herb_cls) else 0

        class_results.append({
            'class': cls,
            'animal_tokens': len(animal_cls),
            'herb_tokens': len(herb_cls),
            'overlap': len(cls_overlap),
            'jaccard': cls_jaccard,
            'animal_only': list(animal_cls - herb_cls)[:3],
            'herb_only': list(herb_cls - animal_cls)[:3],
        })

# Sort by differentiation (lowest Jaccard = most different)
class_results.sort(key=lambda x: x['jaccard'])

print(f"\nClasses with MOST token differentiation (lowest Jaccard):")
print(f"{'Class':<10} {'Animal':<8} {'Herb':<8} {'Overlap':<8} {'Jaccard':<10}")
print("-" * 45)
for r in class_results[:10]:
    print(f"{r['class']:<10} {r['animal_tokens']:<8} {r['herb_tokens']:<8} {r['overlap']:<8} {r['jaccard']:.3f}")

print(f"\nClasses with LEAST token differentiation (highest Jaccard):")
print(f"{'Class':<10} {'Animal':<8} {'Herb':<8} {'Overlap':<8} {'Jaccard':<10}")
print("-" * 45)
for r in class_results[-5:]:
    print(f"{r['class']:<10} {r['animal_tokens']:<8} {r['herb_tokens']:<8} {r['overlap']:<8} {r['jaccard']:.3f}")

# Summary statistics
jaccards = [r['jaccard'] for r in class_results]
print(f"\nPer-class Jaccard statistics:")
print(f"  Mean: {np.mean(jaccards):.3f}")
print(f"  Std: {np.std(jaccards):.3f}")
print(f"  Min: {min(jaccards):.3f}")
print(f"  Max: {max(jaccards):.3f}")

# Show example differentiated tokens in most differentiated class
if class_results:
    most_diff = class_results[0]
    print(f"\nMost differentiated class: {most_diff['class']}")
    print(f"  Animal-only tokens (sample): {most_diff['animal_only']}")
    print(f"  Herb-only tokens (sample): {most_diff['herb_only']}")

# Overall interpretation
print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

mean_jaccard = np.mean(jaccards)
if mean_jaccard > 0.8:
    interpretation = """
HIGH TOKEN OVERLAP (mean Jaccard > 0.8)
Material classes use MOSTLY THE SAME token variants.
PP profiles provide minimal routing differentiation even at token level.
"""
elif mean_jaccard > 0.5:
    interpretation = """
MODERATE TOKEN DIFFERENTIATION (mean Jaccard 0.5-0.8)
Material classes use PARTIALLY DIFFERENT token variants within classes.
PP profiles provide SOME routing differentiation at token level.
This matches C506.a prediction (~5% variation).
"""
else:
    interpretation = """
STRONG TOKEN DIFFERENTIATION (mean Jaccard < 0.5)
Material classes use SUBSTANTIALLY DIFFERENT token variants.
PP profiles provide significant routing differentiation at token level.
"""

print(interpretation)

# MIDDLE-level analysis (alternative to PREFIX class)
print("\n" + "=" * 70)
print("MIDDLE-LEVEL TOKEN DIFFERENTIATION")
print("=" * 70)

# Group tokens by MIDDLE
middle_tokens = defaultdict(list)
for bt in b_tokens:
    if bt['middle']:
        middle_tokens[bt['middle']].append(bt)

# For MIDDLEs that appear in both animal and herb compatible sets
middle_diffs = []
for middle in set(animal_tokens.keys()) | set(herb_tokens.keys()):
    # Get tokens with this middle
    animal_with_middle = [bt['word'] for bt in b_tokens if bt['middle'] == middle and bt['word'] in animal_set]
    herb_with_middle = [bt['word'] for bt in b_tokens if bt['middle'] == middle and bt['word'] in herb_set]

    if animal_with_middle and herb_with_middle:
        a_set = set(animal_with_middle)
        h_set = set(herb_with_middle)
        overlap = a_set & h_set
        jaccard = len(overlap) / len(a_set | h_set) if (a_set | h_set) else 0
        middle_diffs.append({
            'middle': middle,
            'animal': len(a_set),
            'herb': len(h_set),
            'jaccard': jaccard,
        })

if middle_diffs:
    middle_diffs.sort(key=lambda x: x['jaccard'])
    middle_jaccards = [m['jaccard'] for m in middle_diffs]

    print(f"\nMIDDLEs with token differentiation:")
    print(f"  Mean Jaccard: {np.mean(middle_jaccards):.3f}")
    print(f"  Most differentiated MIDDLEs:")
    for m in middle_diffs[:5]:
        print(f"    {m['middle']}: Jaccard={m['jaccard']:.3f} (animal={m['animal']}, herb={m['herb']})")

# Save
results = {
    'overall': {
        'animal_tokens': len(animal_tokens),
        'herb_tokens': len(herb_tokens),
        'overlap': len(overlap),
        'jaccard': jaccard,
    },
    'per_class': {
        'mean_jaccard': np.mean(jaccards),
        'n_classes': len(class_results),
    },
    'per_middle': {
        'mean_jaccard': np.mean(middle_jaccards) if middle_diffs else None,
        'n_middles': len(middle_diffs),
    },
}
with open('phases/MATERIAL_REGIME_MAPPING/results/token_variant_diff.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved.")
