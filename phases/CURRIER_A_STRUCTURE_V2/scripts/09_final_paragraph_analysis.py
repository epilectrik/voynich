"""
09_final_paragraph_analysis.py

FINAL PARAGRAPH ANALYSIS

WITHOUT-RI paragraphs are 1.62x enriched in LAST position.
What's special about these final-position paragraphs?

Hypotheses:
1. They are summary/index sections
2. They are cross-reference pages linking to other folios
3. They have different content structure
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("FINAL PARAGRAPH ANALYSIS")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: COLLECT FINAL PARAGRAPHS
# =============================================================
print("\n[1/3] Collecting final paragraphs...")

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

# Collect final paragraphs
final_with_ri = []
final_without_ri = []
non_final_with_ri = []
non_final_without_ri = []

for folio, paragraphs in folio_paragraphs.items():
    if len(paragraphs) < 2:  # Skip single-paragraph folios
        continue

    # Final paragraph
    final_para = paragraphs[-1]
    final_is_with_ri = has_initial_ri(final_para, analyzer)

    # Non-final paragraphs
    for para in paragraphs[:-1]:
        para_is_with_ri = has_initial_ri(para, analyzer)
        if para_is_with_ri:
            non_final_with_ri.append((folio, para))
        else:
            non_final_without_ri.append((folio, para))

    if final_is_with_ri:
        final_with_ri.append((folio, final_para))
    else:
        final_without_ri.append((folio, final_para))

print(f"   Final WITH-RI: {len(final_with_ri)}")
print(f"   Final WITHOUT-RI: {len(final_without_ri)}")
print(f"   Non-final WITH-RI: {len(non_final_with_ri)}")
print(f"   Non-final WITHOUT-RI: {len(non_final_without_ri)}")

# =============================================================
# STEP 2: COMPARE FINAL VS NON-FINAL WITHOUT-RI PARAGRAPHS
# =============================================================
print("\n[2/3] Comparing final vs non-final WITHOUT-RI paragraphs...")

def analyze_paragraph(folio, para_tokens, analyzer, morph):
    """Analyze a paragraph's structure and content."""
    lines = sorted(set(t.line for t in para_tokens))

    all_ri = []
    all_pp = []
    linker_ri = []

    for line in lines:
        try:
            record = analyzer.analyze_record(folio, line)
            if record:
                for t in record.tokens:
                    if t.token_class == 'RI':
                        all_ri.append(t)
                        if t.word and t.word.startswith('ct'):
                            linker_ri.append(t)
                    elif t.token_class == 'PP':
                        all_pp.append(t)
        except:
            pass

    # PP prefix distribution
    pp_prefixes = Counter()
    for t in all_pp:
        if t.word:
            try:
                m = morph.extract(t.word)
                if m.prefix:
                    pp_prefixes[m.prefix] += 1
            except:
                pass

    return {
        'n_lines': len(lines),
        'n_tokens': len(para_tokens),
        'n_ri': len(all_ri),
        'n_pp': len(all_pp),
        'n_linkers': len(linker_ri),
        'linker_tokens': [t.word for t in linker_ri],
        'pp_prefixes': pp_prefixes
    }

# Analyze all final WITHOUT-RI
final_without_analyses = [analyze_paragraph(f, p, analyzer, morph) for f, p in final_without_ri]
non_final_without_analyses = [analyze_paragraph(f, p, analyzer, morph) for f, p in non_final_without_ri]

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

print(f"\nComparing final vs non-final WITHOUT-RI paragraphs:")
print(f"{'Metric':<30} {'Final':>12} {'Non-Final':>14} {'Ratio':>10}")
print("-" * 68)

# Compare metrics
metrics = [
    ('Avg lines', [a['n_lines'] for a in final_without_analyses], [a['n_lines'] for a in non_final_without_analyses]),
    ('Avg tokens', [a['n_tokens'] for a in final_without_analyses], [a['n_tokens'] for a in non_final_without_analyses]),
    ('Avg RI', [a['n_ri'] for a in final_without_analyses], [a['n_ri'] for a in non_final_without_analyses]),
    ('Avg PP', [a['n_pp'] for a in final_without_analyses], [a['n_pp'] for a in non_final_without_analyses]),
    ('Avg linkers', [a['n_linkers'] for a in final_without_analyses], [a['n_linkers'] for a in non_final_without_analyses]),
]

for name, final_vals, non_final_vals in metrics:
    final_avg = avg(final_vals)
    non_final_avg = avg(non_final_vals)
    ratio = final_avg / non_final_avg if non_final_avg > 0 else float('inf')
    ratio_str = f"{ratio:.2f}x"
    marker = ""
    if ratio >= 1.5:
        marker = ">> FINAL"
    elif ratio <= 0.67:
        marker = "<< NON-FINAL"
    print(f"{name:<30} {final_avg:>12.2f} {non_final_avg:>14.2f} {ratio_str:>8} {marker}")

# Linker presence
final_has_linker = sum(1 for a in final_without_analyses if a['n_linkers'] > 0)
non_final_has_linker = sum(1 for a in non_final_without_analyses if a['n_linkers'] > 0)

pct_final = 100 * final_has_linker / len(final_without_analyses) if final_without_analyses else 0
pct_non_final = 100 * non_final_has_linker / len(non_final_without_analyses) if non_final_without_analyses else 0
print(f"{'Has any linker (%):':<30} {pct_final:>11.1f}% {pct_non_final:>13.1f}%")

# =============================================================
# STEP 3: PREFIX PROFILE COMPARISON
# =============================================================
print("\n[3/3] Comparing PP prefix profiles...")

final_prefixes = Counter()
non_final_prefixes = Counter()

for a in final_without_analyses:
    final_prefixes.update(a['pp_prefixes'])

for a in non_final_without_analyses:
    non_final_prefixes.update(a['pp_prefixes'])

total_final = sum(final_prefixes.values())
total_non_final = sum(non_final_prefixes.values())

all_prefixes = sorted(set(final_prefixes.keys()) | set(non_final_prefixes.keys()))

print(f"\n{'PREFIX':<12} {'Final':>10} {'Non-Final':>14} {'Ratio':>10}")
print("-" * 48)

significant_diffs = []
for prefix in all_prefixes:
    pct_final = 100 * final_prefixes[prefix] / total_final if total_final > 0 else 0
    pct_non_final = 100 * non_final_prefixes[prefix] / total_non_final if total_non_final > 0 else 0
    ratio = pct_final / pct_non_final if pct_non_final > 0 else float('inf') if pct_final > 0 else 1.0

    if ratio >= 1.5 or ratio <= 0.67:
        significant_diffs.append((prefix, ratio))

    if pct_final > 2 or pct_non_final > 2:
        ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "inf"
        marker = ""
        if ratio >= 1.5:
            marker = ">> FINAL"
        elif ratio <= 0.67:
            marker = "<< NON-FIN"
        print(f"{prefix:<12} {pct_final:>9.1f}% {pct_non_final:>13.1f}% {ratio_str:>8} {marker}")

# =============================================================
# COLLECT LINKER EXAMPLES
# =============================================================
print("\n" + "="*70)
print("LINKER TOKENS IN FINAL WITHOUT-RI PARAGRAPHS")
print("="*70)

final_linkers = []
for (folio, para), analysis in zip(final_without_ri, final_without_analyses):
    if analysis['linker_tokens']:
        final_linkers.append((folio, analysis['linker_tokens']))

print(f"\n{len(final_linkers)} final paragraphs with linkers:")
for folio, tokens in final_linkers[:15]:
    print(f"   {folio}: {', '.join(tokens)}")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

# Check if final WITHOUT-RI paragraphs are special
final_linker_rate = avg([a['n_linkers'] for a in final_without_analyses])
non_final_linker_rate = avg([a['n_linkers'] for a in non_final_without_analyses])

print("\nAre final WITHOUT-RI paragraphs special?")
print("-" * 60)

if final_linker_rate > non_final_linker_rate * 1.3:
    print(f"  + Final paragraphs have {final_linker_rate/non_final_linker_rate:.1f}x MORE linkers")
    linker_verdict = "FINAL_MORE_LINKERS"
elif non_final_linker_rate > final_linker_rate * 1.3:
    print(f"  - Final paragraphs have FEWER linkers")
    linker_verdict = "FINAL_FEWER_LINKERS"
else:
    print(f"  = Similar linker rates")
    linker_verdict = "NO_DIFFERENCE"

if significant_diffs:
    print(f"\n  Significant prefix differences:")
    for prefix, ratio in sorted(significant_diffs, key=lambda x: abs(x[1]-1), reverse=True)[:5]:
        direction = "enriched" if ratio > 1 else "depleted"
        print(f"    - {prefix}: {ratio:.1f}x {direction} in final")

# Overall characterization
print("\n" + "-"*60)
print("CHARACTERIZATION OF FINAL WITHOUT-RI PARAGRAPHS:")

print("""
These are independent relational records that:
1. Appear at the END of folios (1.62x enriched)
2. Have higher linker density (from earlier test)
3. Have fewer RI tokens overall
4. Are NOT continuations of previous paragraphs

Possible functions:
- Cross-reference/index sections
- Summary/linking records
- Material relationship maps
""")

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'FINAL_PARAGRAPH_ANALYSIS',
    'counts': {
        'final_with_ri': len(final_with_ri),
        'final_without_ri': len(final_without_ri),
        'non_final_with_ri': len(non_final_with_ri),
        'non_final_without_ri': len(non_final_without_ri)
    },
    'final_vs_non_final_without_ri': {
        'avg_linkers_final': final_linker_rate,
        'avg_linkers_non_final': non_final_linker_rate,
        'linker_verdict': linker_verdict
    },
    'significant_prefix_diffs': significant_diffs[:10],
    'final_linker_examples': final_linkers[:20]
}

output_path = Path(__file__).parent.parent / 'results' / 'final_paragraph_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
