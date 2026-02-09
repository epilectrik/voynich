"""
18_first_vs_last_without_ri.py

FIRST vs LAST WITHOUT-RI PARAGRAPHS

Question: Are FIRST-position WITHOUT-RI paragraphs different from LAST-position ones?
If WITHOUT-RI are "process annotations," why do 22% appear first?

Test: Compare PREFIX profiles, vocabulary, and structure between positions.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("FIRST vs LAST WITHOUT-RI PARAGRAPHS")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD PARAGRAPH INVENTORY BY POSITION
# =============================================================
print("\n[1/3] Building paragraph inventory by position...")

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

def analyze_paragraph(folio, para_tokens, analyzer, morph):
    """Full analysis of a paragraph."""
    lines = sorted(set(t.line for t in para_tokens))

    pp_prefixes = Counter()
    ri_prefixes = Counter()
    pp_middles = set()
    ri_tokens = []
    linker_count = 0

    for line in lines:
        try:
            record = analyzer.analyze_record(folio, line)
            if record:
                for t in record.tokens:
                    if t.token_class == 'PP' and t.word:
                        try:
                            m = morph.extract(t.word)
                            if m.prefix:
                                pp_prefixes[m.prefix] += 1
                            if m.middle:
                                pp_middles.add(m.middle)
                        except:
                            pass
                    elif t.token_class == 'RI' and t.word:
                        ri_tokens.append(t.word)
                        if t.word.startswith('ct'):
                            linker_count += 1
                        try:
                            m = morph.extract(t.word)
                            if m.prefix:
                                ri_prefixes[m.prefix] += 1
                        except:
                            pass
        except:
            pass

    return {
        'folio': folio,
        'n_lines': len(lines),
        'n_tokens': len(para_tokens),
        'pp_prefixes': pp_prefixes,
        'ri_prefixes': ri_prefixes,
        'pp_middles': pp_middles,
        'ri_tokens': ri_tokens,
        'n_ri': len(ri_tokens),
        'n_linkers': linker_count
    }

# Classify WITHOUT-RI paragraphs by position
first_without_ri = []
last_without_ri = []
middle_without_ri = []
only_without_ri = []  # Single paragraph folios

for folio, paragraphs in folio_paragraphs.items():
    n = len(paragraphs)

    for i, para_tokens in enumerate(paragraphs):
        if not para_tokens:
            continue

        if has_initial_ri(para_tokens, analyzer):
            continue  # Skip WITH-RI

        analysis = analyze_paragraph(folio, para_tokens, analyzer, morph)

        if n == 1:
            analysis['position'] = 'ONLY'
            only_without_ri.append(analysis)
        elif i == 0:
            analysis['position'] = 'FIRST'
            first_without_ri.append(analysis)
        elif i == n - 1:
            analysis['position'] = 'LAST'
            last_without_ri.append(analysis)
        else:
            analysis['position'] = 'MIDDLE'
            middle_without_ri.append(analysis)

print(f"   FIRST position: {len(first_without_ri)}")
print(f"   MIDDLE position: {len(middle_without_ri)}")
print(f"   LAST position: {len(last_without_ri)}")
print(f"   ONLY (single-para folio): {len(only_without_ri)}")

# =============================================================
# STEP 2: COMPARE FIRST vs LAST
# =============================================================
print("\n[2/3] Comparing FIRST vs LAST WITHOUT-RI paragraphs...")

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

def aggregate_prefixes(analyses):
    total = Counter()
    for a in analyses:
        total.update(a['pp_prefixes'])
    return total

print(f"\nSTRUCTURAL COMPARISON:")
print(f"{'Metric':<30} {'FIRST':>12} {'LAST':>12} {'Ratio':>10}")
print("-" * 66)

# Size metrics
avg_first = avg([a['n_tokens'] for a in first_without_ri])
avg_last = avg([a['n_tokens'] for a in last_without_ri])
ratio = avg_first / avg_last if avg_last > 0 else 0
print(f"{'Avg tokens:':<30} {avg_first:>12.1f} {avg_last:>12.1f} {ratio:>9.2f}x")

avg_first = avg([a['n_lines'] for a in first_without_ri])
avg_last = avg([a['n_lines'] for a in last_without_ri])
ratio = avg_first / avg_last if avg_last > 0 else 0
print(f"{'Avg lines:':<30} {avg_first:>12.1f} {avg_last:>12.1f} {ratio:>9.2f}x")

# RI metrics
avg_first = avg([a['n_ri'] for a in first_without_ri])
avg_last = avg([a['n_ri'] for a in last_without_ri])
ratio = avg_first / avg_last if avg_last > 0 else 0
print(f"{'Avg RI tokens:':<30} {avg_first:>12.2f} {avg_last:>12.2f} {ratio:>9.2f}x")

# Linker metrics
avg_first = avg([a['n_linkers'] for a in first_without_ri])
avg_last = avg([a['n_linkers'] for a in last_without_ri])
ratio = avg_first / avg_last if avg_last > 0 else 0
print(f"{'Avg linker (ct-) RI:':<30} {avg_first:>12.2f} {avg_last:>12.2f} {ratio:>9.2f}x")

# =============================================================
# STEP 3: PP PREFIX PROFILE COMPARISON
# =============================================================
print("\n[3/3] Comparing PP PREFIX profiles...")

first_prefixes = aggregate_prefixes(first_without_ri)
last_prefixes = aggregate_prefixes(last_without_ri)

total_first = sum(first_prefixes.values())
total_last = sum(last_prefixes.values())

all_prefixes = sorted(set(first_prefixes.keys()) | set(last_prefixes.keys()))

print(f"\nPP PREFIX DISTRIBUTION:")
print(f"{'PREFIX':<12} {'FIRST':>12} {'LAST':>12} {'Ratio':>10}")
print("-" * 48)

significant_diffs = []
for prefix in all_prefixes:
    pct_first = 100 * first_prefixes[prefix] / total_first if total_first > 0 else 0
    pct_last = 100 * last_prefixes[prefix] / total_last if total_last > 0 else 0

    if pct_first > 0 or pct_last > 0:
        ratio = pct_first / pct_last if pct_last > 0 else float('inf') if pct_first > 0 else 1.0

        if ratio >= 1.5 or ratio <= 0.67:
            significant_diffs.append((prefix, ratio, pct_first, pct_last))

        if pct_first > 2 or pct_last > 2:
            ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "inf"
            marker = ""
            if ratio >= 1.5:
                marker = ">> FIRST"
            elif ratio <= 0.67:
                marker = "<< LAST"
            print(f"{prefix:<12} {pct_first:>11.1f}% {pct_last:>11.1f}% {ratio_str:>8} {marker}")

# =============================================================
# RI TOKEN COMPARISON
# =============================================================
print("\n" + "="*70)
print("RI TOKEN COMPARISON")
print("="*70)

first_ri_tokens = []
last_ri_tokens = []
for a in first_without_ri:
    first_ri_tokens.extend(a['ri_tokens'])
for a in last_without_ri:
    last_ri_tokens.extend(a['ri_tokens'])

print(f"\nRI tokens in FIRST WITHOUT-RI (n={len(first_ri_tokens)}):")
for token, count in Counter(first_ri_tokens).most_common(10):
    print(f"   {token}: {count}")

print(f"\nRI tokens in LAST WITHOUT-RI (n={len(last_ri_tokens)}):")
for token, count in Counter(last_ri_tokens).most_common(10):
    print(f"   {token}: {count}")

# Vocabulary overlap
first_set = set(first_ri_tokens)
last_set = set(last_ri_tokens)
jaccard = len(first_set & last_set) / len(first_set | last_set) if (first_set | last_set) else 0
print(f"\nRI vocabulary Jaccard (FIRST vs LAST): {jaccard:.3f}")

# =============================================================
# SPECIFIC FOLIO EXAMPLES
# =============================================================
print("\n" + "="*70)
print("EXAMPLES: FIRST-POSITION WITHOUT-RI PARAGRAPHS")
print("="*70)

print(f"\nFolios where WITHOUT-RI paragraph appears FIRST:")
for a in first_without_ri[:10]:
    folio = a['folio']
    n_tokens = a['n_tokens']
    n_ri = a['n_ri']
    ri_sample = a['ri_tokens'][:3] if a['ri_tokens'] else ['(none)']
    print(f"   {folio}: {n_tokens} tokens, {n_ri} RI: {', '.join(ri_sample)}")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("\nAre FIRST and LAST WITHOUT-RI paragraphs different sub-types?")
print("-" * 60)

# Test 1: Size difference
size_first = avg([a['n_tokens'] for a in first_without_ri])
size_last = avg([a['n_tokens'] for a in last_without_ri])
if size_first > size_last * 1.3:
    print(f"+ FIRST paragraphs are LARGER ({size_first:.0f} vs {size_last:.0f} tokens)")
    size_diff = "FIRST_LARGER"
elif size_last > size_first * 1.3:
    print(f"+ LAST paragraphs are LARGER ({size_last:.0f} vs {size_first:.0f} tokens)")
    size_diff = "LAST_LARGER"
else:
    print(f"= Similar size ({size_first:.0f} vs {size_last:.0f} tokens)")
    size_diff = "SIMILAR"

# Test 2: PREFIX profile difference
if significant_diffs:
    print(f"+ {len(significant_diffs)} prefixes with significant (>1.5x) differences:")
    for prefix, ratio, pct_f, pct_l in sorted(significant_diffs, key=lambda x: abs(x[1]-1), reverse=True)[:5]:
        direction = "FIRST" if ratio > 1 else "LAST"
        print(f"    - {prefix}: {ratio:.1f}x enriched in {direction}")
    prefix_diff = True
else:
    print(f"- No significant PREFIX differences")
    prefix_diff = False

# Test 3: RI vocabulary overlap
if jaccard < 0.3:
    print(f"+ RI vocabularies are DISTINCT (Jaccard={jaccard:.3f})")
    ri_diff = True
else:
    print(f"- RI vocabularies OVERLAP (Jaccard={jaccard:.3f})")
    ri_diff = False

print("\n" + "-"*60)
print("VERDICT:")

if prefix_diff or ri_diff or size_diff != "SIMILAR":
    print("""
FIRST and LAST WITHOUT-RI paragraphs ARE structurally different:
- This suggests sub-types within the process-annotation category

Possible interpretation:
- FIRST WITHOUT-RI: "Opening process" records (general setup instructions)
- LAST WITHOUT-RI: "Closing process" records (summary/finalization)
""")
    verdict = "DIFFERENT_SUBTYPES"
else:
    print("""
FIRST and LAST WITHOUT-RI paragraphs are NOT significantly different.
Position may be determined by other factors (folio layout, content flow).
""")
    verdict = "SAME_TYPE"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'FIRST_VS_LAST_WITHOUT_RI',
    'counts': {
        'first': len(first_without_ri),
        'middle': len(middle_without_ri),
        'last': len(last_without_ri),
        'only': len(only_without_ri)
    },
    'structural': {
        'avg_tokens_first': avg([a['n_tokens'] for a in first_without_ri]),
        'avg_tokens_last': avg([a['n_tokens'] for a in last_without_ri]),
        'avg_ri_first': avg([a['n_ri'] for a in first_without_ri]),
        'avg_ri_last': avg([a['n_ri'] for a in last_without_ri])
    },
    'ri_vocab_jaccard': jaccard,
    'significant_prefix_diffs': [(p, r) for p, r, _, _ in significant_diffs],
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'first_vs_last_without_ri.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
