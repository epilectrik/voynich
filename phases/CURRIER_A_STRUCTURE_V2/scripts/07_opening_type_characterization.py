"""
07_opening_type_characterization.py

FOLLOW-UP TEST: Characterize the two paragraph opening types

Hypothesis: WITHOUT-RI paragraphs are relational/linking records rather than substance records.

Test:
1. Do WITHOUT-RI paragraphs contain more linker tokens than WITH-RI paragraphs?
2. What other characteristics distinguish the two opening types?
3. Do they correspond to different record functions?
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("OPENING TYPE CHARACTERIZATION")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD PARAGRAPH INVENTORY
# =============================================================
print("\n[1/5] Building paragraph inventory...")

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
# STEP 2: CLASSIFY BY OPENING TYPE AND COLLECT DETAILED DATA
# =============================================================
print("[2/5] Classifying paragraphs and collecting linker data...")

with_ri_paras = []
without_ri_paras = []

for folio, paragraphs in folio_paragraphs.items():
    for para_tokens in paragraphs:
        if not para_tokens:
            continue

        lines = sorted(set(t.line for t in para_tokens))
        if not lines:
            continue

        first_line = lines[0]

        # Analyze ALL lines in paragraph
        all_ri = []
        all_pp = []
        linker_ri = []  # ct-prefix RI tokens

        for line in lines:
            try:
                record = analyzer.analyze_record(folio, line)
                if record:
                    for t in record.tokens:
                        if t.token_class == 'RI':
                            all_ri.append((line, t))
                            if t.word and t.word.startswith('ct'):
                                linker_ri.append((line, t))
                        elif t.token_class == 'PP':
                            all_pp.append((line, t))
            except:
                pass

        # Check first line for RI
        first_line_ri = [t for l, t in all_ri if l == first_line]

        entry = {
            'folio': folio,
            'n_lines': len(lines),
            'n_tokens': len(para_tokens),
            'total_ri': len(all_ri),
            'total_pp': len(all_pp),
            'linker_ri_count': len(linker_ri),
            'linker_ri_tokens': [t.word for l, t in linker_ri],
            'has_linker': len(linker_ri) > 0,
            'first_line': first_line,
            'pp_prefixes': Counter(),
            'ri_prefixes': Counter()
        }

        # Collect PP prefixes
        for l, t in all_pp:
            if t.word:
                try:
                    m = morph.extract(t.word)
                    if m.prefix:
                        entry['pp_prefixes'][m.prefix] += 1
                except:
                    pass

        # Collect RI prefixes
        for l, t in all_ri:
            if t.word:
                try:
                    m = morph.extract(t.word)
                    if m.prefix:
                        entry['ri_prefixes'][m.prefix] += 1
                except:
                    pass

        if first_line_ri:
            with_ri_paras.append(entry)
        else:
            without_ri_paras.append(entry)

print(f"   WITH-RI paragraphs: {len(with_ri_paras)}")
print(f"   WITHOUT-RI paragraphs: {len(without_ri_paras)}")

# =============================================================
# STEP 3: LINKER TOKEN ANALYSIS
# =============================================================
print("\n[3/5] Analyzing linker token distribution...")

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

# Linker presence
with_ri_has_linker = sum(1 for p in with_ri_paras if p['has_linker'])
without_ri_has_linker = sum(1 for p in without_ri_paras if p['has_linker'])

print(f"\nLINKER RI TOKEN DISTRIBUTION:")
print(f"{'Metric':<30} {'WITH-RI':>12} {'WITHOUT-RI':>14} {'Ratio':>10}")
print("-" * 68)

# Has any linker
pct_with = 100 * with_ri_has_linker / len(with_ri_paras)
pct_without = 100 * without_ri_has_linker / len(without_ri_paras)
ratio = pct_without / pct_with if pct_with > 0 else float('inf')
print(f"{'Has linker (%):':<30} {pct_with:>11.1f}% {pct_without:>13.1f}% {ratio:>9.2f}x")

# Average linker count
avg_with = avg([p['linker_ri_count'] for p in with_ri_paras])
avg_without = avg([p['linker_ri_count'] for p in without_ri_paras])
ratio = avg_without / avg_with if avg_with > 0 else float('inf')
print(f"{'Avg linker count:':<30} {avg_with:>12.2f} {avg_without:>14.2f} {ratio:>9.2f}x")

# Linker density (linkers per RI token)
with_ri_total_ri = sum(p['total_ri'] for p in with_ri_paras)
without_ri_total_ri = sum(p['total_ri'] for p in without_ri_paras)
with_ri_linkers = sum(p['linker_ri_count'] for p in with_ri_paras)
without_ri_linkers = sum(p['linker_ri_count'] for p in without_ri_paras)

density_with = with_ri_linkers / with_ri_total_ri if with_ri_total_ri > 0 else 0
density_without = without_ri_linkers / without_ri_total_ri if without_ri_total_ri > 0 else 0
ratio = density_without / density_with if density_with > 0 else float('inf')
print(f"{'Linker density (linkers/RI):':<30} {density_with:>12.2f} {density_without:>14.2f} {ratio:>9.2f}x")

# Total linkers
print(f"{'Total linker tokens:':<30} {with_ri_linkers:>12} {without_ri_linkers:>14}")
print(f"{'Total RI tokens:':<30} {with_ri_total_ri:>12} {without_ri_total_ri:>14}")

# =============================================================
# STEP 4: PP PREFIX PROFILE COMPARISON
# =============================================================
print("\n[4/5] Comparing PP PREFIX profiles in full paragraphs...")

# Aggregate PP prefixes
with_ri_pp_prefixes = Counter()
without_ri_pp_prefixes = Counter()

for p in with_ri_paras:
    with_ri_pp_prefixes.update(p['pp_prefixes'])

for p in without_ri_paras:
    without_ri_pp_prefixes.update(p['pp_prefixes'])

total_with = sum(with_ri_pp_prefixes.values())
total_without = sum(without_ri_pp_prefixes.values())

all_prefixes = sorted(set(with_ri_pp_prefixes.keys()) | set(without_ri_pp_prefixes.keys()))

print(f"\nPP PREFIX distribution (full paragraph, not just first line):")
print(f"{'PREFIX':<12} {'WITH-RI':>10} {'WITHOUT-RI':>14} {'Ratio':>10}")
print("-" * 48)

significant_diffs = []
for prefix in all_prefixes:
    pct_with = 100 * with_ri_pp_prefixes[prefix] / total_with if total_with > 0 else 0
    pct_without = 100 * without_ri_pp_prefixes[prefix] / total_without if total_without > 0 else 0
    ratio = pct_without / pct_with if pct_with > 0 else float('inf') if pct_without > 0 else 1.0

    if ratio >= 1.5 or ratio <= 0.67:
        significant_diffs.append((prefix, ratio, pct_with, pct_without))

    if pct_with > 1 or pct_without > 1:  # Only show significant
        ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "inf"
        marker = ""
        if ratio >= 1.5:
            marker = "<< WITHOUT"
        elif ratio <= 0.67:
            marker = ">> WITH"
        print(f"{prefix:<12} {pct_with:>9.1f}% {pct_without:>13.1f}% {ratio_str:>8} {marker}")

# =============================================================
# STEP 5: STRUCTURAL COMPARISON
# =============================================================
print("\n[5/5] Structural comparison...")

print(f"\nSTRUCTURAL METRICS:")
print(f"{'Metric':<30} {'WITH-RI':>12} {'WITHOUT-RI':>14}")
print("-" * 58)

# Paragraph size
avg_lines_with = avg([p['n_lines'] for p in with_ri_paras])
avg_lines_without = avg([p['n_lines'] for p in without_ri_paras])
print(f"{'Avg lines per paragraph:':<30} {avg_lines_with:>12.2f} {avg_lines_without:>14.2f}")

# Token count
avg_tokens_with = avg([p['n_tokens'] for p in with_ri_paras])
avg_tokens_without = avg([p['n_tokens'] for p in without_ri_paras])
print(f"{'Avg tokens per paragraph:':<30} {avg_tokens_with:>12.2f} {avg_tokens_without:>14.2f}")

# RI count
avg_ri_with = avg([p['total_ri'] for p in with_ri_paras])
avg_ri_without = avg([p['total_ri'] for p in without_ri_paras])
print(f"{'Avg RI per paragraph:':<30} {avg_ri_with:>12.2f} {avg_ri_without:>14.2f}")

# PP count
avg_pp_with = avg([p['total_pp'] for p in with_ri_paras])
avg_pp_without = avg([p['total_pp'] for p in without_ri_paras])
print(f"{'Avg PP per paragraph:':<30} {avg_pp_with:>12.2f} {avg_pp_without:>14.2f}")

# RI density (RI per token)
ri_density_with = avg_ri_with / avg_tokens_with if avg_tokens_with > 0 else 0
ri_density_without = avg_ri_without / avg_tokens_without if avg_tokens_without > 0 else 0
print(f"{'RI density (RI/token):':<30} {ri_density_with:>12.3f} {ri_density_without:>14.3f}")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("\nTEST: Do WITHOUT-RI paragraphs contain more linker tokens?")
print("-" * 60)

if density_without > density_with * 1.3:
    print(f"YES - WITHOUT-RI paragraphs have {density_without/density_with:.1f}x higher linker density")
    linker_verdict = "WITHOUT_RI_MORE_LINKERS"
elif density_with > density_without * 1.3:
    print(f"NO - WITH-RI paragraphs actually have {density_with/density_without:.1f}x higher linker density")
    linker_verdict = "WITH_RI_MORE_LINKERS"
else:
    print(f"NO DIFFERENCE - Similar linker density ({density_with:.2f} vs {density_without:.2f})")
    linker_verdict = "NO_DIFFERENCE"

print(f"\nLinker presence rate:")
print(f"  WITH-RI: {pct_with:.1f}% of paragraphs have linkers")
print(f"  WITHOUT-RI: {pct_without:.1f}% of paragraphs have linkers")

# Hypothesis evaluation
print("\n" + "-"*60)
print("HYPOTHESIS EVALUATION")
print("-"*60)

print("""
Hypothesis: WITHOUT-RI paragraphs are relational/linking records
            (cross-references) rather than substance records.

Evidence:""")

# Check linker evidence
if density_without > density_with:
    print(f"  + Linker density is {density_without/density_with:.1f}x higher in WITHOUT-RI")
else:
    print(f"  - Linker density is NOT higher in WITHOUT-RI ({density_without:.2f} vs {density_with:.2f})")

# Check ct-prefix in PP
ct_with = with_ri_pp_prefixes.get('ct', 0) / total_with * 100 if total_with > 0 else 0
ct_without = without_ri_pp_prefixes.get('ct', 0) / total_without * 100 if total_without > 0 else 0
if ct_without > ct_with * 1.3:
    print(f"  + ct-prefix PP is {ct_without/ct_with:.1f}x higher in WITHOUT-RI ({ct_without:.1f}% vs {ct_with:.1f}%)")
else:
    print(f"  - ct-prefix PP is not significantly higher in WITHOUT-RI")

# Check structural differences
if avg_ri_without < avg_ri_with * 0.7:
    print(f"  + WITHOUT-RI has fewer RI overall ({avg_ri_without:.1f} vs {avg_ri_with:.1f})")
else:
    print(f"  ? Similar RI count ({avg_ri_without:.1f} vs {avg_ri_with:.1f})")

# Overall verdict
print("\nVERDICT:")
if linker_verdict == "WITHOUT_RI_MORE_LINKERS":
    print("  SUPPORTED - WITHOUT-RI paragraphs are linker-enriched relational records")
elif linker_verdict == "WITH_RI_MORE_LINKERS":
    print("  CONTRADICTED - WITH-RI paragraphs actually have MORE linkers")
    print("  Alternative: Initial RI may MARK substance records that NEED linking")
else:
    print("  INCONCLUSIVE - No clear linker difference between opening types")

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'OPENING_TYPE_CHARACTERIZATION',
    'counts': {
        'with_ri_paras': len(with_ri_paras),
        'without_ri_paras': len(without_ri_paras)
    },
    'linker_analysis': {
        'with_ri_has_linker_pct': pct_with,
        'without_ri_has_linker_pct': pct_without,
        'with_ri_linker_density': density_with,
        'without_ri_linker_density': density_without,
        'total_with_ri_linkers': with_ri_linkers,
        'total_without_ri_linkers': without_ri_linkers
    },
    'structural': {
        'avg_lines_with': avg_lines_with,
        'avg_lines_without': avg_lines_without,
        'avg_ri_with': avg_ri_with,
        'avg_ri_without': avg_ri_without
    },
    'verdict': linker_verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'opening_type_characterization.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
