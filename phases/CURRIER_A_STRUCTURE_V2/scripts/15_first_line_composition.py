"""
15_first_line_composition.py

FIRST LINE COMPOSITION TEST

Question: What's on the first line of WITHOUT-RI paragraphs?

WITH-RI: First line has RI tokens (material identifier)
WITHOUT-RI: First line has ???

Hypothesis: WITHOUT-RI first lines may be:
1. Pure PP (process instructions only)
2. Linker RI (ct-prefix) instead of identifier RI
3. LINK-related PP (ol/or prefixes)
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("FIRST LINE COMPOSITION TEST")
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

# =============================================================
# STEP 2: ANALYZE FIRST LINES
# =============================================================
print("\n[2/3] Analyzing first lines...")

def analyze_first_line(folio, para_tokens, analyzer, morph):
    """Analyze composition of the first line."""
    if not para_tokens:
        return None

    first_line = para_tokens[0].line

    try:
        record = analyzer.analyze_record(folio, first_line)
        if not record:
            return None

        ri_tokens = []
        pp_tokens = []
        linker_ri = []
        link_pp = []  # ol/or prefix PP

        for t in record.tokens:
            if t.token_class == 'RI':
                ri_tokens.append(t)
                if t.word and t.word.startswith('ct'):
                    linker_ri.append(t)
            elif t.token_class == 'PP':
                pp_tokens.append(t)
                if t.word:
                    try:
                        m = morph.extract(t.word)
                        if m.prefix in ['ol', 'or', 'al', 'ar']:
                            link_pp.append(t)
                    except:
                        pass

        return {
            'folio': folio,
            'line': first_line,
            'n_ri': len(ri_tokens),
            'n_pp': len(pp_tokens),
            'n_linker_ri': len(linker_ri),
            'n_link_pp': len(link_pp),
            'ri_words': [t.word for t in ri_tokens if t.word],
            'pp_words': [t.word for t in pp_tokens if t.word],
            'has_ri': len(ri_tokens) > 0,
            'has_pp': len(pp_tokens) > 0,
            'has_linker': len(linker_ri) > 0,
            'has_link_pp': len(link_pp) > 0,
            'pure_pp': len(ri_tokens) == 0 and len(pp_tokens) > 0,
            'linker_only': len(linker_ri) > 0 and len([r for r in ri_tokens if not r.word or not r.word.startswith('ct')]) == 0
        }
    except:
        return None

# Classify paragraphs by opening type
with_ri_first_lines = []
without_ri_first_lines = []

for folio, paragraphs in folio_paragraphs.items():
    for para_tokens in paragraphs:
        if not para_tokens:
            continue

        analysis = analyze_first_line(folio, para_tokens, analyzer, morph)
        if analysis is None:
            continue

        if analysis['has_ri'] and not analysis['linker_only']:
            with_ri_first_lines.append(analysis)
        else:
            without_ri_first_lines.append(analysis)

print(f"   WITH-RI (non-linker RI on first line): {len(with_ri_first_lines)}")
print(f"   WITHOUT-RI (no RI or linker-only): {len(without_ri_first_lines)}")

# =============================================================
# STEP 3: COMPARE FIRST LINE COMPOSITION
# =============================================================
print("\n[3/3] Comparing first line composition...")

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

# Basic metrics
print(f"\nFIRST LINE COMPOSITION:")
print(f"{'Metric':<30} {'WITH-RI':>12} {'WITHOUT-RI':>14}")
print("-" * 58)

print(f"{'Avg RI tokens:':<30} {avg([a['n_ri'] for a in with_ri_first_lines]):>12.2f} {avg([a['n_ri'] for a in without_ri_first_lines]):>14.2f}")
print(f"{'Avg PP tokens:':<30} {avg([a['n_pp'] for a in with_ri_first_lines]):>12.2f} {avg([a['n_pp'] for a in without_ri_first_lines]):>14.2f}")
print(f"{'Avg linker RI:':<30} {avg([a['n_linker_ri'] for a in with_ri_first_lines]):>12.2f} {avg([a['n_linker_ri'] for a in without_ri_first_lines]):>14.2f}")
print(f"{'Avg LINK-PP (ol/or/al/ar):':<30} {avg([a['n_link_pp'] for a in with_ri_first_lines]):>12.2f} {avg([a['n_link_pp'] for a in without_ri_first_lines]):>14.2f}")

# Categorical breakdown
print(f"\nFIRST LINE STRUCTURE:")

# Pure PP (no RI at all)
pure_pp_with = sum(1 for a in with_ri_first_lines if a['pure_pp'])
pure_pp_without = sum(1 for a in without_ri_first_lines if a['pure_pp'])
print(f"{'Pure PP (no RI):':<30} {pure_pp_with:>12} ({100*pure_pp_with/len(with_ri_first_lines):.1f}%) {pure_pp_without:>8} ({100*pure_pp_without/len(without_ri_first_lines):.1f}%)")

# Has linker RI
linker_with = sum(1 for a in with_ri_first_lines if a['has_linker'])
linker_without = sum(1 for a in without_ri_first_lines if a['has_linker'])
print(f"{'Has linker (ct-):':<30} {linker_with:>12} ({100*linker_with/len(with_ri_first_lines):.1f}%) {linker_without:>8} ({100*linker_without/len(without_ri_first_lines):.1f}%)")

# Linker-only RI
linker_only_with = sum(1 for a in with_ri_first_lines if a['linker_only'])
linker_only_without = sum(1 for a in without_ri_first_lines if a['linker_only'])
print(f"{'Linker-only RI:':<30} {linker_only_with:>12} ({100*linker_only_with/len(with_ri_first_lines):.1f}%) {linker_only_without:>8} ({100*linker_only_without/len(without_ri_first_lines):.1f}%)")

# Has LINK-PP
link_pp_with = sum(1 for a in with_ri_first_lines if a['has_link_pp'])
link_pp_without = sum(1 for a in without_ri_first_lines if a['has_link_pp'])
print(f"{'Has LINK-PP (ol/or/al/ar):':<30} {link_pp_with:>12} ({100*link_pp_with/len(with_ri_first_lines):.1f}%) {link_pp_without:>8} ({100*link_pp_without/len(without_ri_first_lines):.1f}%)")

# =============================================================
# DETAILED BREAKDOWN OF WITHOUT-RI FIRST LINES
# =============================================================
print("\n" + "="*70)
print("WITHOUT-RI FIRST LINE BREAKDOWN")
print("="*70)

# What's actually on the first line?
wo_categories = Counter()
for a in without_ri_first_lines:
    if a['pure_pp']:
        wo_categories['PURE_PP'] += 1
    elif a['linker_only']:
        wo_categories['LINKER_ONLY'] += 1
    elif a['has_linker'] and a['n_ri'] > a['n_linker_ri']:
        wo_categories['MIXED_RI_WITH_LINKER'] += 1
    elif a['has_ri']:
        wo_categories['HAS_NON_LINKER_RI'] += 1
    else:
        wo_categories['OTHER'] += 1

print(f"\nCategories of WITHOUT-RI first lines:")
for cat, count in wo_categories.most_common():
    pct = 100 * count / len(without_ri_first_lines)
    print(f"   {cat}: {count} ({pct:.1f}%)")

# Specific RI words on WITHOUT-RI first lines
without_ri_words = []
for a in without_ri_first_lines:
    without_ri_words.extend(a['ri_words'])

print(f"\nRI words on WITHOUT-RI first lines (n={len(without_ri_words)}):")
ri_counter = Counter(without_ri_words)
for word, count in ri_counter.most_common(15):
    print(f"   {word}: {count}")

# PP words on WITHOUT-RI first lines
without_pp_words = []
for a in without_ri_first_lines:
    without_pp_words.extend(a['pp_words'])

print(f"\nPP words on WITHOUT-RI first lines (n={len(without_pp_words)}):")
pp_counter = Counter(without_pp_words)
for word, count in pp_counter.most_common(15):
    print(f"   {word}: {count}")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("\nWithout-RI first line composition:")
print("-" * 60)

pct_pure_pp = 100 * pure_pp_without / len(without_ri_first_lines)
pct_linker_only = 100 * linker_only_without / len(without_ri_first_lines)
pct_has_linker = 100 * linker_without / len(without_ri_first_lines)

if pct_pure_pp > 50:
    print(f"+ MAJORITY ({pct_pure_pp:.1f}%) are PURE PP - process instructions only")
    first_line_type = "PURE_PP"
elif pct_linker_only > 20:
    print(f"+ {pct_linker_only:.1f}% have LINKER-ONLY RI (ct-prefix)")
    first_line_type = "LINKER_DOMINATED"
else:
    print(f"? Mixed composition - no dominant pattern")
    first_line_type = "MIXED"

print("\nConclusion:")
if first_line_type == "PURE_PP":
    print("""
WITHOUT-RI paragraphs start with PURE PP (process instructions):
- No material identifier (RI) on first line
- Immediate jump into process vocabulary
- May be continuation-style records that reference prior material implicitly

This suggests WITHOUT-RI = "process-focused" records
vs WITH-RI = "material-focused" records
""")
elif first_line_type == "LINKER_DOMINATED":
    print("""
WITHOUT-RI paragraphs start with LINKER RI:
- ct-prefix RI on first line (cross-reference function)
- These are explicitly relational/linking records
- Connect materials or processes across the registry
""")
else:
    print("""
WITHOUT-RI paragraphs have MIXED first line composition.
Further analysis needed to characterize the pattern.
""")

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'FIRST_LINE_COMPOSITION',
    'counts': {
        'with_ri': len(with_ri_first_lines),
        'without_ri': len(without_ri_first_lines)
    },
    'first_line_metrics': {
        'avg_ri_with': avg([a['n_ri'] for a in with_ri_first_lines]),
        'avg_ri_without': avg([a['n_ri'] for a in without_ri_first_lines]),
        'avg_pp_with': avg([a['n_pp'] for a in with_ri_first_lines]),
        'avg_pp_without': avg([a['n_pp'] for a in without_ri_first_lines])
    },
    'categories': dict(wo_categories),
    'pct_pure_pp': pct_pure_pp,
    'pct_linker_only': pct_linker_only,
    'first_line_type': first_line_type
}

output_path = Path(__file__).parent.parent / 'results' / 'first_line_composition.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
