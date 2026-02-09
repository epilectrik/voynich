"""
12_ri_type_composition.py

RI TYPE COMPOSITION TEST

Question: Do WITHOUT-RI paragraphs have DIFFERENT RI token types?

We know:
- WITHOUT-RI paragraphs have higher linker DENSITY (1.35x)
- WITHOUT-RI paragraphs have fewer total RI

Hypothesis: WITHOUT-RI paragraphs may be dominated by linker RI,
while WITH-RI paragraphs have more diverse RI types.

Test: Compare RI prefix/morphology distribution between paragraph types.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("RI TYPE COMPOSITION TEST")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD PARAGRAPH INVENTORY
# =============================================================
print("\n[1/3] Building paragraph inventory...")

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

def has_initial_ri(para_tokens, analyzer):
    if not para_tokens:
        return False
    folio = para_tokens[0].folio
    first_line = para_tokens[0].line
    try:
        record = analyzer.analyze_record(folio, first_line)
        if record:
            for t in record.tokens:
                if t.token_class == 'RI':
                    return True
    except:
        pass
    return False

# =============================================================
# STEP 2: COLLECT ALL RI TOKENS BY PARAGRAPH TYPE
# =============================================================
print("\n[2/3] Collecting RI tokens by paragraph type...")

def get_all_ri_tokens(folio, para_tokens, analyzer, morph):
    """Get all RI tokens from a paragraph with morphology."""
    lines = sorted(set(t.line for t in para_tokens))
    ri_tokens = []

    for line in lines:
        try:
            record = analyzer.analyze_record(folio, line)
            if record:
                for t in record.tokens:
                    if t.token_class == 'RI' and t.word:
                        try:
                            m = morph.extract(t.word)
                            ri_tokens.append({
                                'word': t.word,
                                'prefix': m.prefix,
                                'middle': m.middle,
                                'suffix': m.suffix,
                                'line': line,
                                'is_linker': t.word.startswith('ct')
                            })
                        except:
                            ri_tokens.append({
                                'word': t.word,
                                'prefix': None,
                                'middle': None,
                                'suffix': None,
                                'line': line,
                                'is_linker': t.word.startswith('ct')
                            })
        except:
            pass
    return ri_tokens

with_ri_tokens = []
without_ri_tokens = []

for folio, paragraphs in folio_paragraphs.items():
    for para_tokens in paragraphs:
        if not para_tokens:
            continue

        ri_tokens = get_all_ri_tokens(folio, para_tokens, analyzer, morph)

        if has_initial_ri(para_tokens, analyzer):
            with_ri_tokens.extend(ri_tokens)
        else:
            without_ri_tokens.extend(ri_tokens)

print(f"   WITH-RI paragraphs: {len(with_ri_tokens)} RI tokens")
print(f"   WITHOUT-RI paragraphs: {len(without_ri_tokens)} RI tokens")

# =============================================================
# STEP 3: COMPARE RI COMPOSITION
# =============================================================
print("\n[3/3] Comparing RI composition...")

# Prefix distribution
with_ri_prefixes = Counter(t['prefix'] for t in with_ri_tokens if t['prefix'])
without_ri_prefixes = Counter(t['prefix'] for t in without_ri_tokens if t['prefix'])

total_with = sum(with_ri_prefixes.values())
total_without = sum(without_ri_prefixes.values())

all_prefixes = sorted(set(with_ri_prefixes.keys()) | set(without_ri_prefixes.keys()))

print(f"\nRI PREFIX DISTRIBUTION:")
print(f"{'PREFIX':<12} {'WITH-RI':>12} {'WITHOUT-RI':>14} {'Ratio':>10}")
print("-" * 50)

significant_ri_diffs = []
for prefix in all_prefixes:
    pct_with = 100 * with_ri_prefixes[prefix] / total_with if total_with > 0 else 0
    pct_without = 100 * without_ri_prefixes[prefix] / total_without if total_without > 0 else 0
    ratio = pct_without / pct_with if pct_with > 0 else float('inf') if pct_without > 0 else 1.0

    if ratio >= 1.5 or ratio <= 0.67:
        significant_ri_diffs.append((prefix, ratio, pct_with, pct_without))

    if pct_with > 2 or pct_without > 2:
        ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "inf"
        marker = ""
        if ratio >= 1.5:
            marker = "<< WITHOUT"
        elif ratio <= 0.67:
            marker = ">> WITH"
        print(f"{prefix:<12} {pct_with:>11.1f}% {pct_without:>13.1f}% {ratio_str:>8} {marker}")

# Linker proportion
linkers_with = sum(1 for t in with_ri_tokens if t['is_linker'])
linkers_without = sum(1 for t in without_ri_tokens if t['is_linker'])

pct_linker_with = 100 * linkers_with / len(with_ri_tokens) if with_ri_tokens else 0
pct_linker_without = 100 * linkers_without / len(without_ri_tokens) if without_ri_tokens else 0

print(f"\n{'LINKER (ct-)':<12} {pct_linker_with:>11.1f}% {pct_linker_without:>13.1f}%", end="")
if pct_linker_without > pct_linker_with * 1.3:
    print(f"  << WITHOUT ({pct_linker_without/pct_linker_with:.2f}x)")
elif pct_linker_with > pct_linker_without * 1.3:
    print(f"  >> WITH ({pct_linker_with/pct_linker_without:.2f}x)")
else:
    print()

# =============================================================
# STEP 4: MIDDLE ANALYSIS
# =============================================================
print("\n" + "-"*50)
print("RI MIDDLE DISTRIBUTION:")

with_ri_middles = Counter(t['middle'] for t in with_ri_tokens if t['middle'])
without_ri_middles = Counter(t['middle'] for t in without_ri_tokens if t['middle'])

total_mid_with = sum(with_ri_middles.values())
total_mid_without = sum(without_ri_middles.values())

print(f"\n{'MIDDLE':<12} {'WITH-RI':>12} {'WITHOUT-RI':>14} {'Ratio':>10}")
print("-" * 50)

# Show most common middles
all_middles = sorted(set(with_ri_middles.keys()) | set(without_ri_middles.keys()),
                    key=lambda m: -(with_ri_middles.get(m, 0) + without_ri_middles.get(m, 0)))

for middle in all_middles[:15]:
    pct_with = 100 * with_ri_middles[middle] / total_mid_with if total_mid_with > 0 else 0
    pct_without = 100 * without_ri_middles[middle] / total_mid_without if total_mid_without > 0 else 0
    ratio = pct_without / pct_with if pct_with > 0 else float('inf') if pct_without > 0 else 1.0

    ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "inf"
    marker = ""
    if ratio >= 1.5:
        marker = "<< WITHOUT"
    elif ratio <= 0.67:
        marker = ">> WITH"
    print(f"{middle:<12} {pct_with:>11.1f}% {pct_without:>13.1f}% {ratio_str:>8} {marker}")

# =============================================================
# STEP 5: SPECIFIC RI TOKENS
# =============================================================
print("\n" + "="*70)
print("MOST COMMON RI TOKENS")
print("="*70)

with_ri_words = Counter(t['word'] for t in with_ri_tokens)
without_ri_words = Counter(t['word'] for t in without_ri_tokens)

print(f"\nWITH-RI paragraphs (top 15):")
for word, count in with_ri_words.most_common(15):
    pct = 100 * count / len(with_ri_tokens)
    print(f"   {word}: {count} ({pct:.1f}%)")

print(f"\nWITHOUT-RI paragraphs (top 15):")
for word, count in without_ri_words.most_common(15):
    pct = 100 * count / len(without_ri_tokens)
    print(f"   {word}: {count} ({pct:.1f}%)")

# Unique to each type
only_with = set(with_ri_words.keys()) - set(without_ri_words.keys())
only_without = set(without_ri_words.keys()) - set(with_ri_words.keys())

print(f"\nRI tokens ONLY in WITH-RI: {len(only_with)}")
print(f"RI tokens ONLY in WITHOUT-RI: {len(only_without)}")
print(f"Shared RI tokens: {len(set(with_ri_words.keys()) & set(without_ri_words.keys()))}")

# Jaccard similarity
union = set(with_ri_words.keys()) | set(without_ri_words.keys())
intersection = set(with_ri_words.keys()) & set(without_ri_words.keys())
jaccard = len(intersection) / len(union) if union else 0
print(f"\nJaccard similarity of RI vocabulary: {jaccard:.3f}")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("\nQuestion: Do WITHOUT-RI paragraphs have different RI token types?")
print("-" * 60)

# Test 1: Linker proportion
if pct_linker_without > pct_linker_with * 1.3:
    print(f"+ WITHOUT-RI has higher LINKER proportion ({pct_linker_without:.1f}% vs {pct_linker_with:.1f}%)")
    linker_dominant = True
else:
    print(f"- Similar linker proportion ({pct_linker_without:.1f}% vs {pct_linker_with:.1f}%)")
    linker_dominant = False

# Test 2: Vocabulary overlap
if jaccard < 0.5:
    print(f"+ RI vocabularies are DISTINCT (Jaccard={jaccard:.3f})")
    distinct_vocab = True
else:
    print(f"- RI vocabularies OVERLAP significantly (Jaccard={jaccard:.3f})")
    distinct_vocab = False

# Test 3: Significant prefix differences
if significant_ri_diffs:
    print(f"+ {len(significant_ri_diffs)} prefixes with significant (>1.5x) differences")
else:
    print(f"- No significant prefix differences")

print("\n" + "-"*60)
print("VERDICT:")

if linker_dominant or distinct_vocab:
    print("""
WITHOUT-RI paragraphs have COMPOSITIONALLY DIFFERENT RI tokens:
- Different RI vocabulary (not just fewer tokens)
- This supports the "relational record" interpretation

WITHOUT-RI paragraphs appear to serve a different structural function
than WITH-RI paragraphs, not just omitting the opening RI marker.
""")
    verdict = "COMPOSITIONALLY_DIFFERENT"
else:
    print("""
WITHOUT-RI paragraphs have SIMILAR RI composition to WITH-RI.
The only difference is the absence of initial RI.
""")
    verdict = "SAME_COMPOSITION"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'RI_TYPE_COMPOSITION',
    'counts': {
        'with_ri_tokens': len(with_ri_tokens),
        'without_ri_tokens': len(without_ri_tokens)
    },
    'linker_proportion': {
        'with_ri': pct_linker_with,
        'without_ri': pct_linker_without
    },
    'jaccard_similarity': jaccard,
    'significant_prefix_diffs': significant_ri_diffs,
    'ri_vocab_only_with': len(only_with),
    'ri_vocab_only_without': len(only_without),
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'ri_type_composition.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
