"""
06_withri_withoutri_profiles.py - Compare PP profiles in WITH-RI vs WITHOUT-RI paragraphs

From C887: WITHOUT-RI paragraphs reference preceding WITH-RI paragraphs
Question: Do WITHOUT-RI paragraphs show PP profiles matching execution operations?

If RI encodes "preparation-relevant distinctions":
- WITH-RI paragraphs = material identification phase (contain RI)
- WITHOUT-RI paragraphs = execution phase (pure PP)

Test:
1. Classify A paragraphs as WITH-RI or WITHOUT-RI
2. Compare PP PREFIX profiles between categories
3. Check if WITHOUT-RI has more execution-characteristic prefixes (qo/ok/ol for escape/auxiliary/monitor per C888)
"""

import sys
sys.path.insert(0, 'C:/git/voynich')
import pandas as pd
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
from scipy import stats
import json

tx = Transcript()
morph = Morphology()

# Build B vocabulary to identify RI (A-exclusive) vs PP (A-shared)
print("Building PP/RI classification...")
b_tokens = list(tx.currier_b())
b_middles = set()
for t in b_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        b_middles.add(m.middle)

print(f"  B vocabulary: {len(b_middles)} unique MIDDLEs")

# Get A tokens with paragraph info
a_tokens = list(tx.currier_a())
print(f"  A tokens: {len(a_tokens)}")

# Load raw transcript for paragraph data
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df = df[df['language'] == 'A']
df = df[~df['placement'].str.startswith('L', na=False)]

# Build (folio, line) -> paragraph mapping
# Paragraph breaks are indicated by line numbering patterns - we'll use par_initial/par_final
line_para = {}
current_para = 1
prev_folio = None

for t in a_tokens:
    if t.folio != prev_folio:
        current_para = 1
        prev_folio = t.folio

    line_para[(t.folio, t.line)] = current_para

    if t.par_final:
        current_para += 1

# Build paragraph RI/PP profiles
para_tokens = defaultdict(list)  # (folio, para) -> list of tokens
para_has_ri = defaultdict(bool)  # (folio, para) -> has any RI token

for t in a_tokens:
    para_num = line_para.get((t.folio, t.line), 1)
    key = (t.folio, para_num)
    para_tokens[key].append(t)
    m = morph.extract(t.word)
    if m and m.middle:
        if m.middle not in b_middles:  # RI token
            para_has_ri[key] = True

# Classify paragraphs
with_ri_paras = [k for k in para_tokens if para_has_ri[k]]
without_ri_paras = [k for k in para_tokens if not para_has_ri[k]]

print(f"\nParagraph classification:")
print(f"  WITH-RI paragraphs: {len(with_ri_paras)}")
print(f"  WITHOUT-RI paragraphs: {len(without_ri_paras)}")
print(f"  Ratio WITHOUT-RI: {100*len(without_ri_paras)/(len(with_ri_paras)+len(without_ri_paras)):.1f}%")

# ============================================================
# Collect PP vocabulary profiles for each category
# ============================================================
print("\n" + "="*70)
print("PP PROFILE COMPARISON")
print("="*70)

with_ri_pp_prefixes = Counter()
without_ri_pp_prefixes = Counter()
with_ri_pp_middles = Counter()
without_ri_pp_middles = Counter()

# Count prefixes by category
with_ri_total_pp = 0
without_ri_total_pp = 0

for key in with_ri_paras:
    for t in para_tokens[key]:
        m = morph.extract(t.word)
        if m and m.middle and m.middle in b_middles:  # PP token
            with_ri_total_pp += 1
            with_ri_pp_middles[m.middle] += 1
            if m.prefix:
                with_ri_pp_prefixes[m.prefix] += 1

for key in without_ri_paras:
    for t in para_tokens[key]:
        m = morph.extract(t.word)
        if m and m.middle and m.middle in b_middles:  # PP token
            without_ri_total_pp += 1
            without_ri_pp_middles[m.middle] += 1
            if m.prefix:
                without_ri_pp_prefixes[m.prefix] += 1

print(f"\nPP token counts:")
print(f"  WITH-RI paragraphs: {with_ri_total_pp} PP tokens")
print(f"  WITHOUT-RI paragraphs: {without_ri_total_pp} PP tokens")

# ============================================================
# PREFIX Distribution Comparison
# ============================================================
print("\n" + "-"*70)
print("PP PREFIX DISTRIBUTION")
print("-"*70)
print("From C888: qo/ok/ol are ESCAPE/AUXILIARY/MONITOR prefixes (execution-characteristic)")
print()

# Key prefixes to compare
key_prefixes = ['qo', 'ok', 'ol', 'ch', 'sh', 'da', 'do', 'ct', 'd', 's']

print(f"{'PREFIX':<10} {'WITH-RI':<15} {'WITHOUT-RI':<15} {'Diff':<10} {'Note':<20}")
print("-" * 70)

with_ri_total = sum(with_ri_pp_prefixes.values())
without_ri_total = sum(without_ri_pp_prefixes.values())

significant_diffs = []

for prefix in key_prefixes:
    wr_count = with_ri_pp_prefixes.get(prefix, 0)
    wor_count = without_ri_pp_prefixes.get(prefix, 0)

    wr_pct = 100 * wr_count / with_ri_total if with_ri_total > 0 else 0
    wor_pct = 100 * wor_count / without_ri_total if without_ri_total > 0 else 0

    diff = wor_pct - wr_pct

    note = ""
    if prefix in ['qo', 'ok', 'ol']:
        note = "ESCAPE/AUX/MON"
    elif prefix == 'ct':
        note = "LINKER"
    elif prefix in ['ch', 'sh']:
        note = "CORE"
    elif prefix in ['da', 'do']:
        note = "da-FAMILY"

    print(f"{prefix:<10} {wr_pct:>6.1f}%         {wor_pct:>6.1f}%         {diff:>+5.1f}%     {note:<20}")

    if abs(diff) > 2:
        significant_diffs.append((prefix, diff, note))

# ============================================================
# Statistical Test: Chi-square for execution-related prefixes
# ============================================================
print("\n" + "-"*70)
print("STATISTICAL TEST: EXECUTION-RELATED PREFIX ENRICHMENT")
print("-"*70)

# Group execution-related prefixes (qo, ok, ol) vs others
execution_prefixes = {'qo', 'ok', 'ol'}

wr_exec = sum(with_ri_pp_prefixes.get(p, 0) for p in execution_prefixes)
wr_other = with_ri_total - wr_exec

wor_exec = sum(without_ri_pp_prefixes.get(p, 0) for p in execution_prefixes)
wor_other = without_ri_total - wor_exec

print(f"\nExecution prefixes (qo/ok/ol):")
print(f"  WITH-RI: {wr_exec}/{with_ri_total} = {100*wr_exec/with_ri_total:.1f}%")
print(f"  WITHOUT-RI: {wor_exec}/{without_ri_total} = {100*wor_exec/without_ri_total:.1f}%")

# Chi-square test
contingency = [[wr_exec, wr_other], [wor_exec, wor_other]]
chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

print(f"\nChi-square test:")
print(f"  chi2 = {chi2:.2f}")
print(f"  p-value = {p_value:.4f}")

if p_value < 0.05:
    if wor_exec/without_ri_total > wr_exec/with_ri_total:
        print("  -> WITHOUT-RI has SIGNIFICANTLY MORE execution prefixes")
        execution_enrichment = "SUPPORTS"
    else:
        print("  -> WITH-RI has SIGNIFICANTLY MORE execution prefixes")
        execution_enrichment = "CONTRADICTS"
else:
    print("  -> No significant difference in execution prefix usage")
    execution_enrichment = "NEUTRAL"

# ============================================================
# TOP PP MIDDLEs by Category
# ============================================================
print("\n" + "-"*70)
print("TOP PP MIDDLEs BY CATEGORY")
print("-"*70)

print("\nWITH-RI paragraphs - top PP MIDDLEs:")
for middle, count in with_ri_pp_middles.most_common(10):
    print(f"  {middle}: {count}")

print("\nWITHOUT-RI paragraphs - top PP MIDDLEs:")
for middle, count in without_ri_pp_middles.most_common(10):
    print(f"  {middle}: {count}")

# ============================================================
# Check if WITHOUT-RI paragraphs are sequential followers
# ============================================================
print("\n" + "-"*70)
print("SEQUENTIAL RELATIONSHIP (per C887)")
print("-"*70)

# Count sequential patterns
ri_followed_by_ri = 0
ri_followed_by_non = 0
non_followed_by_ri = 0
non_followed_by_non = 0

folio_paras = defaultdict(list)
for key in para_tokens:
    folio_paras[key[0]].append(key[1])

for folio, paras in folio_paras.items():
    paras_sorted = sorted(set(paras))
    for i in range(len(paras_sorted) - 1):
        curr = (folio, paras_sorted[i])
        next_p = (folio, paras_sorted[i + 1])

        curr_has_ri = para_has_ri.get(curr, False)
        next_has_ri = para_has_ri.get(next_p, False)

        if curr_has_ri and next_has_ri:
            ri_followed_by_ri += 1
        elif curr_has_ri and not next_has_ri:
            ri_followed_by_non += 1
        elif not curr_has_ri and next_has_ri:
            non_followed_by_ri += 1
        else:
            non_followed_by_non += 1

print(f"\nParagraph transition patterns:")
print(f"  WITH-RI -> WITH-RI:     {ri_followed_by_ri}")
print(f"  WITH-RI -> WITHOUT-RI:  {ri_followed_by_non}")
print(f"  WITHOUT-RI -> WITH-RI:  {non_followed_by_ri}")
print(f"  WITHOUT-RI -> WITHOUT-RI: {non_followed_by_non}")

# Calculate transition probabilities
if ri_followed_by_ri + ri_followed_by_non > 0:
    prob_ri_to_non = ri_followed_by_non / (ri_followed_by_ri + ri_followed_by_non)
    print(f"\n  P(WITHOUT-RI follows WITH-RI): {100*prob_ri_to_non:.1f}%")

if non_followed_by_ri + non_followed_by_non > 0:
    prob_non_to_ri = non_followed_by_ri / (non_followed_by_ri + non_followed_by_non)
    print(f"  P(WITH-RI follows WITHOUT-RI): {100*prob_non_to_ri:.1f}%")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
Paragraph classification:
  WITH-RI:    {len(with_ri_paras)} paragraphs ({100*len(with_ri_paras)/(len(with_ri_paras)+len(without_ri_paras)):.1f}%)
  WITHOUT-RI: {len(without_ri_paras)} paragraphs ({100*len(without_ri_paras)/(len(with_ri_paras)+len(without_ri_paras)):.1f}%)

Execution prefix enrichment (qo/ok/ol):
  WITH-RI:    {100*wr_exec/with_ri_total:.1f}%
  WITHOUT-RI: {100*wor_exec/without_ri_total:.1f}%
  Chi-square p-value: {p_value:.4f}
  Result: {execution_enrichment}

Key findings from prefix analysis:
""")

for prefix, diff, note in sorted(significant_diffs, key=lambda x: -abs(x[1])):
    direction = "WITHOUT-RI" if diff > 0 else "WITH-RI"
    print(f"  {prefix}: {direction} has +{abs(diff):.1f}pp ({note})")

# Interpretation
print(f"""
INTERPRETATION:
""")

if execution_enrichment == "SUPPORTS":
    print("  WITHOUT-RI paragraphs show MORE execution-characteristic prefixes (qo/ok/ol)")
    print("  This SUPPORTS the model: WITH-RI = identification, WITHOUT-RI = execution")
elif execution_enrichment == "CONTRADICTS":
    print("  WITH-RI paragraphs show MORE execution-characteristic prefixes")
    print("  This CONTRADICTS the model: RI and execution prefixes co-occur")
else:
    print("  No significant difference in execution prefix distribution")
    print("  The WITH-RI/WITHOUT-RI distinction may not map to preparation/execution")

# Save results
output = {
    'with_ri_para_count': len(with_ri_paras),
    'without_ri_para_count': len(without_ri_paras),
    'with_ri_pp_total': with_ri_total_pp,
    'without_ri_pp_total': without_ri_total_pp,
    'execution_prefix_test': {
        'with_ri_exec_pct': 100*wr_exec/with_ri_total if with_ri_total > 0 else 0,
        'without_ri_exec_pct': 100*wor_exec/without_ri_total if without_ri_total > 0 else 0,
        'chi2': float(chi2),
        'p_value': float(p_value),
        'result': execution_enrichment
    },
    'transitions': {
        'ri_to_ri': ri_followed_by_ri,
        'ri_to_non': ri_followed_by_non,
        'non_to_ri': non_followed_by_ri,
        'non_to_non': non_followed_by_non
    }
}

with open('C:/git/voynich/phases/A_PURPOSE_INVESTIGATION/results/withri_withoutri_profiles.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to withri_withoutri_profiles.json")
