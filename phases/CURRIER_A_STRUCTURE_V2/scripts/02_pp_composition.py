"""
02_pp_composition.py

TEST 2: PP COMPOSITION IN NON-RI FIRST LINES

Do first lines WITH initial RI have different PP profiles than first lines WITHOUT?

If YES → Two types of paragraph openings exist
If NO → RI presence is random/content-driven
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import math

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("TEST 2: PP COMPOSITION IN FIRST LINES")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: COLLECT FIRST LINES WITH AND WITHOUT RI
# =============================================================
print("\n[1/4] Collecting first lines...")

# Build paragraph structure using par_initial markers
folio_paragraphs = defaultdict(list)
current_para_tokens = []
current_folio = None

for t in tx.currier_a():
    if not t.word or '*' in t.word:
        continue

    if t.folio != current_folio:
        if current_para_tokens:
            folio_paragraphs[current_folio].append(current_para_tokens)
        current_folio = t.folio
        current_para_tokens = []

    if t.par_initial and current_para_tokens:
        folio_paragraphs[current_folio].append(current_para_tokens)
        current_para_tokens = []

    current_para_tokens.append(t)

if current_para_tokens and current_folio:
    folio_paragraphs[current_folio].append(current_para_tokens)

# Analyze first lines of each paragraph
first_lines_with_ri = []
first_lines_without_ri = []

for folio, paragraphs in folio_paragraphs.items():
    for para_tokens in paragraphs:
        if not para_tokens:
            continue

        # Get first line number
        first_line = para_tokens[0].line

        # Analyze this line
        try:
            record = analyzer.analyze_record(folio, first_line)
            if not record:
                continue
        except:
            continue

        # Collect RI and PP tokens on first line
        first_line_ri = [t for t in record.tokens if t.token_class == 'RI']
        first_line_pp = [t for t in record.tokens if t.token_class == 'PP']

        entry = {
            'folio': folio,
            'line': first_line,
            'ri_tokens': [t.word for t in first_line_ri],
            'pp_tokens': [t.word for t in first_line_pp],
            'total_tokens': len(record.tokens)
        }

        if first_line_ri:
            first_lines_with_ri.append(entry)
        else:
            first_lines_without_ri.append(entry)

print(f"   First lines WITH initial RI: {len(first_lines_with_ri)}")
print(f"   First lines WITHOUT initial RI: {len(first_lines_without_ri)}")

# =============================================================
# STEP 2: ANALYZE PP PREFIX PROFILES
# =============================================================
print("\n[2/4] Analyzing PP PREFIX profiles...")

def get_prefix_profile(pp_tokens):
    """Extract PREFIX distribution from PP tokens."""
    prefixes = Counter()
    for word in pp_tokens:
        try:
            m = morph.extract(word)
            if m.prefix:
                prefixes[m.prefix] += 1
            else:
                prefixes['NO_PREFIX'] += 1
        except:
            prefixes['UNKNOWN'] += 1
    return prefixes

# Get prefix profiles for both groups
with_ri_prefixes = Counter()
without_ri_prefixes = Counter()

for entry in first_lines_with_ri:
    profile = get_prefix_profile(entry['pp_tokens'])
    with_ri_prefixes.update(profile)

for entry in first_lines_without_ri:
    profile = get_prefix_profile(entry['pp_tokens'])
    without_ri_prefixes.update(profile)

# Get all prefixes
all_prefixes = sorted(set(with_ri_prefixes.keys()) | set(without_ri_prefixes.keys()))

# Normalize to percentages
total_with = sum(with_ri_prefixes.values())
total_without = sum(without_ri_prefixes.values())

print(f"\n{'PREFIX':<12} {'WITH RI':>10} {'WITHOUT RI':>12} {'RATIO':>10}")
print("-" * 46)

prefix_comparison = {}
for prefix in all_prefixes:
    pct_with = 100 * with_ri_prefixes[prefix] / total_with if total_with > 0 else 0
    pct_without = 100 * without_ri_prefixes[prefix] / total_without if total_without > 0 else 0
    ratio = pct_with / pct_without if pct_without > 0 else float('inf') if pct_with > 0 else 1.0

    prefix_comparison[prefix] = {
        'with_ri_pct': pct_with,
        'without_ri_pct': pct_without,
        'ratio': ratio if ratio != float('inf') else 999
    }

    ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "∞"
    marker = ""
    if ratio >= 1.5:
        marker = "↑↑"
    elif ratio >= 1.2:
        marker = "↑"
    elif ratio <= 0.5:
        marker = "↓↓"
    elif ratio <= 0.8:
        marker = "↓"

    print(f"{prefix:<12} {pct_with:>9.1f}% {pct_without:>11.1f}% {ratio_str:>8} {marker}")

# =============================================================
# STEP 3: ANALYZE PP TOKEN DIVERSITY
# =============================================================
print("\n[3/4] Analyzing PP token diversity...")

# Unique PP tokens in each group
with_ri_pp_unique = set()
without_ri_pp_unique = set()

for entry in first_lines_with_ri:
    with_ri_pp_unique.update(entry['pp_tokens'])

for entry in first_lines_without_ri:
    without_ri_pp_unique.update(entry['pp_tokens'])

# Overlap analysis
overlap = with_ri_pp_unique & without_ri_pp_unique
only_with_ri = with_ri_pp_unique - without_ri_pp_unique
only_without_ri = without_ri_pp_unique - with_ri_pp_unique

print(f"\nPP vocabulary analysis:")
print(f"  Unique PP in lines WITH RI: {len(with_ri_pp_unique)}")
print(f"  Unique PP in lines WITHOUT RI: {len(without_ri_pp_unique)}")
print(f"  Overlap: {len(overlap)} ({100*len(overlap)/len(with_ri_pp_unique | without_ri_pp_unique):.1f}%)")
print(f"  Only in WITH RI: {len(only_with_ri)}")
print(f"  Only in WITHOUT RI: {len(only_without_ri)}")

# Jaccard similarity
jaccard = len(overlap) / len(with_ri_pp_unique | without_ri_pp_unique) if (with_ri_pp_unique | without_ri_pp_unique) else 0
print(f"  Jaccard similarity: {jaccard:.3f}")

# =============================================================
# STEP 4: FIRST TOKEN ANALYSIS
# =============================================================
print("\n[4/4] Analyzing first PP token in each line...")

# What PP token starts lines with vs without RI?
first_pp_with_ri = Counter()
first_pp_without_ri = Counter()

for entry in first_lines_with_ri:
    if entry['pp_tokens']:
        first_pp_with_ri[entry['pp_tokens'][0]] += 1

for entry in first_lines_without_ri:
    if entry['pp_tokens']:
        first_pp_without_ri[entry['pp_tokens'][0]] += 1

print("\nMost common first PP token (WITH RI lines):")
for token, count in first_pp_with_ri.most_common(10):
    print(f"  {token}: {count} ({100*count/len(first_lines_with_ri):.1f}%)")

print("\nMost common first PP token (WITHOUT RI lines):")
for token, count in first_pp_without_ri.most_common(10):
    print(f"  {token}: {count} ({100*count/len(first_lines_without_ri):.1f}%)")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

# Check for significant differences
significant_diffs = []
for prefix, data in prefix_comparison.items():
    if data['ratio'] >= 1.5 or data['ratio'] <= 0.67:
        significant_diffs.append((prefix, data['ratio']))

if significant_diffs:
    print("\nSignificant PREFIX differences found:")
    for prefix, ratio in sorted(significant_diffs, key=lambda x: abs(x[1]-1), reverse=True):
        direction = "enriched" if ratio > 1 else "depleted"
        print(f"  - {prefix} is {ratio:.2f}x {direction} in WITH-RI lines")
    verdict = "TWO_OPENING_TYPES"
else:
    print("\nNo significant PREFIX differences found")
    verdict = "SINGLE_OPENING_TYPE"

if jaccard < 0.5:
    print(f"\n→ LOW VOCABULARY OVERLAP ({jaccard:.2f}): Two distinct PP vocabularies")
    vocab_verdict = "DISTINCT_VOCABULARIES"
elif jaccard > 0.7:
    print(f"\n→ HIGH VOCABULARY OVERLAP ({jaccard:.2f}): Shared PP vocabulary")
    vocab_verdict = "SHARED_VOCABULARY"
else:
    print(f"\n→ MODERATE VOCABULARY OVERLAP ({jaccard:.2f})")
    vocab_verdict = "MODERATE_OVERLAP"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'PP_COMPOSITION_IN_FIRST_LINES',
    'n_with_ri': len(first_lines_with_ri),
    'n_without_ri': len(first_lines_without_ri),
    'prefix_comparison': prefix_comparison,
    'pp_vocabulary': {
        'with_ri_unique': len(with_ri_pp_unique),
        'without_ri_unique': len(without_ri_pp_unique),
        'overlap': len(overlap),
        'jaccard': jaccard
    },
    'first_pp_token': {
        'with_ri': dict(first_pp_with_ri.most_common(20)),
        'without_ri': dict(first_pp_without_ri.most_common(20))
    },
    'significant_differences': significant_diffs,
    'verdict': verdict,
    'vocab_verdict': vocab_verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'pp_composition_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
