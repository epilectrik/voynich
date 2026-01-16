#!/usr/bin/env python3
"""
AZC-DEEP Phase 1: Folio Feature Table
=====================================

Builds comprehensive per-folio feature vectors for clustering analysis.
All features are Tier 2-safe (no semantics).

Features extracted:
- token_count, unique_types, ttr
- a_coverage, b_coverage
- placement_vector (distribution over placement codes)
- placement_entropy
- prefix_vector, suffix_vector
- link_density
- mean_token_length
- azc_unique_rate
- ordered_subscript_depth (R1/R2/R3, S1/S2 usage)

Output: results/azc_folio_features.json
"""

import json
import os
import math
from collections import Counter, defaultdict

os.chdir('C:/git/voynich')

print("=" * 70)
print("AZC-DEEP PHASE 1: FOLIO FEATURE TABLE")
print("=" * 70)

# =============================================================================
# CONSTANTS
# =============================================================================

# Standard morphological components
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'yk', 'yt', 'kch', 'ko', 'op', 'oe', 'oa']
SUFFIXES = ['aiin', 'ain', 'iin', 'in', 'dy', 'edy', 'eedy', 'y', 'ey', 'eey', 'ol', 'al', 'or', 'ar', 'chy', 'shy', 'hy', 'eol', 'eal', 'am', 'an']

# LINK tokens (wait-state indicators)
LINK_TOKENS = {'ol', 'al', 'or', 'ar', 'aiin', 'daiin', 'chol', 'chor', 'shol', 'shor'}

# Placement codes (from C306)
PLACEMENT_CODES = ['C', 'C1', 'P', 'P1', 'R', 'R1', 'R2', 'R3', 'S', 'S1', 'S2', 'Y', 'X', 'L', 'O', 'MULTI']

# =============================================================================
# LOAD DATA
# =============================================================================

print("\nLoading transcription data...")

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Parse all tokens
all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        # Filter to PRIMARY transcriber (H) only
        if row.get('transcriber', '').strip('\"') != 'H':
            continue
        all_tokens.append(row)

print(f"Total tokens loaded: {len(all_tokens)}")

# Separate by language
azc_tokens = [t for t in all_tokens if t.get('language', '') in ('NA', '')]
a_tokens = [t for t in all_tokens if t.get('language', '') == 'A']
b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']

# Build vocabulary sets
azc_words = set(t['word'] for t in azc_tokens)
a_words = set(t['word'] for t in a_tokens)
b_words = set(t['word'] for t in b_tokens)
azc_only_words = azc_words - a_words - b_words

print(f"AZC tokens: {len(azc_tokens)} ({len(azc_words)} types)")
print(f"AZC-only vocabulary: {len(azc_only_words)} types")

# =============================================================================
# MORPHOLOGICAL DECOMPOSITION
# =============================================================================

def decompose(word):
    """Decompose word into prefix, middle, suffix."""
    prefix = ''
    for p in sorted(PREFIXES, key=len, reverse=True):
        if word.startswith(p) and len(p) < len(word):
            prefix = p
            break

    suffix = ''
    remainder = word[len(prefix):] if prefix else word
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if remainder.endswith(s) and len(s) <= len(remainder):
            suffix = s
            break

    if prefix and suffix and len(suffix) < len(word) - len(prefix):
        middle = word[len(prefix):-len(suffix)]
    elif prefix:
        middle = word[len(prefix):]
        suffix = ''
    elif suffix:
        middle = word[:-len(suffix)]
    else:
        middle = word

    return prefix or 'NONE', middle, suffix or 'NONE'

# Add morphology to AZC tokens
for t in azc_tokens:
    prefix, middle, suffix = decompose(t['word'])
    t['prefix'] = prefix
    t['suffix'] = suffix
    t['word_len'] = len(t['word'])

# =============================================================================
# GROUP BY FOLIO
# =============================================================================

print("\nGrouping tokens by folio...")

folio_tokens = defaultdict(list)
for t in azc_tokens:
    folio = t.get('folio', 'UNK')
    folio_tokens[folio].append(t)

# Sort folios for consistent ordering
folios = sorted(folio_tokens.keys())
print(f"AZC folios: {len(folios)}")

# =============================================================================
# COMPUTE FOLIO FEATURES
# =============================================================================

def compute_entropy(distribution):
    """Compute Shannon entropy of a distribution."""
    total = sum(distribution.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in distribution.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy

def normalize_distribution(counter, categories):
    """Normalize a counter to a distribution over fixed categories."""
    total = sum(counter.values())
    if total == 0:
        return {cat: 0.0 for cat in categories}
    return {cat: counter.get(cat, 0) / total for cat in categories}

print("\nComputing folio features...")

folio_features = {}

for folio in folios:
    tokens = folio_tokens[folio]
    n = len(tokens)

    if n == 0:
        continue

    # Basic counts
    words = [t['word'] for t in tokens]
    unique_types = set(words)

    # TTR
    ttr = len(unique_types) / n if n > 0 else 0

    # A/B coverage
    a_overlap = sum(1 for w in words if w in a_words)
    b_overlap = sum(1 for w in words if w in b_words)
    a_coverage = a_overlap / n if n > 0 else 0
    b_coverage = b_overlap / n if n > 0 else 0

    # AZC-unique rate
    azc_unique_count = sum(1 for w in words if w in azc_only_words)
    azc_unique_rate = azc_unique_count / n if n > 0 else 0

    # LINK density
    link_count = sum(1 for w in words if w in LINK_TOKENS)
    link_density = link_count / n if n > 0 else 0

    # Mean token length
    mean_token_length = sum(len(w) for w in words) / n if n > 0 else 0

    # Placement distribution
    placement_counts = Counter(t.get('placement', 'UNK') for t in tokens)
    placement_vector = normalize_distribution(placement_counts, PLACEMENT_CODES + ['UNK'])
    placement_entropy = compute_entropy(placement_counts)

    # Ordered subscript depth (how much R1/R2/R3 and S1/S2 are used)
    subscript_codes = ['R1', 'R2', 'R3', 'S1', 'S2']
    subscript_count = sum(placement_counts.get(code, 0) for code in subscript_codes)
    ordered_subscript_depth = subscript_count / n if n > 0 else 0

    # Prefix distribution
    prefix_counts = Counter(t['prefix'] for t in tokens)
    top_prefixes = ['ch', 'ot', 'ok', 'da', 'sh', 'qo', 'yk', 'yt', 'NONE']
    prefix_vector = normalize_distribution(prefix_counts, top_prefixes + ['OTHER'])

    # Suffix distribution
    suffix_counts = Counter(t['suffix'] for t in tokens)
    top_suffixes = ['y', 'dy', 'ar', 'al', 'aiin', 'ey', 'eey', 'ol', 'or', 'NONE']
    suffix_vector = normalize_distribution(suffix_counts, top_suffixes + ['OTHER'])

    # Get section from first token
    section = tokens[0].get('section', 'UNK') if tokens else 'UNK'

    # Store features
    folio_features[folio] = {
        'folio': folio,
        'section': section,
        'token_count': n,
        'unique_types': len(unique_types),
        'ttr': round(ttr, 4),
        'a_coverage': round(a_coverage, 4),
        'b_coverage': round(b_coverage, 4),
        'azc_unique_rate': round(azc_unique_rate, 4),
        'link_density': round(link_density, 4),
        'mean_token_length': round(mean_token_length, 2),
        'placement_entropy': round(placement_entropy, 3),
        'ordered_subscript_depth': round(ordered_subscript_depth, 4),
        'placement_vector': {k: round(v, 4) for k, v in placement_vector.items()},
        'prefix_vector': {k: round(v, 4) for k, v in prefix_vector.items()},
        'suffix_vector': {k: round(v, 4) for k, v in suffix_vector.items()},
        'placement_counts': dict(placement_counts),
        'raw_counts': {
            'link_count': link_count,
            'azc_unique_count': azc_unique_count
        }
    }

print(f"Features computed for {len(folio_features)} folios")

# =============================================================================
# SUMMARY STATISTICS
# =============================================================================

print("\n" + "=" * 70)
print("FOLIO FEATURE SUMMARY")
print("=" * 70)

# Group by section
section_groups = defaultdict(list)
for folio, features in folio_features.items():
    section_groups[features['section']].append(folio)

print(f"\n{'Section':<10} {'Folios':<8} {'Tokens':<10} {'Avg TTR':<10} {'Avg LINK%':<12}")
print("-" * 50)

for section in sorted(section_groups.keys()):
    folios_in_section = section_groups[section]
    total_tokens = sum(folio_features[f]['token_count'] for f in folios_in_section)
    avg_ttr = sum(folio_features[f]['ttr'] for f in folios_in_section) / len(folios_in_section)
    avg_link = sum(folio_features[f]['link_density'] for f in folios_in_section) / len(folios_in_section)
    print(f"{section:<10} {len(folios_in_section):<8} {total_tokens:<10} {avg_ttr:<10.3f} {avg_link*100:<10.1f}%")

# Feature ranges
print("\n" + "-" * 50)
print("Feature Ranges Across Folios:")
print("-" * 50)

numeric_features = ['token_count', 'unique_types', 'ttr', 'a_coverage', 'b_coverage',
                    'azc_unique_rate', 'link_density', 'mean_token_length',
                    'placement_entropy', 'ordered_subscript_depth']

for feat in numeric_features:
    values = [folio_features[f][feat] for f in folio_features]
    if values:
        print(f"{feat:<25} min={min(values):.3f}  max={max(values):.3f}  range={max(values)-min(values):.3f}")

# =============================================================================
# PLACEMENT CODE USAGE
# =============================================================================

print("\n" + "=" * 70)
print("PLACEMENT CODE DISTRIBUTION (ALL AZC)")
print("=" * 70)

total_placement = Counter()
for folio, features in folio_features.items():
    for code, count in features['placement_counts'].items():
        total_placement[code] += count

total = sum(total_placement.values())
print(f"\n{'Code':<10} {'Count':<10} {'Pct':<10}")
print("-" * 30)
for code, count in total_placement.most_common(20):
    pct = count / total * 100 if total > 0 else 0
    print(f"{code:<10} {count:<10} {pct:.1f}%")

# =============================================================================
# SAVE RESULTS
# =============================================================================

output_path = 'results/azc_folio_features.json'
os.makedirs('results', exist_ok=True)

output = {
    'metadata': {
        'total_folios': len(folio_features),
        'total_tokens': sum(f['token_count'] for f in folio_features.values()),
        'sections': dict(Counter(f['section'] for f in folio_features.values())),
        'feature_list': numeric_features + ['placement_vector', 'prefix_vector', 'suffix_vector']
    },
    'folios': folio_features
}

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n[OK] Results saved to: {output_path}")
print("=" * 70)
