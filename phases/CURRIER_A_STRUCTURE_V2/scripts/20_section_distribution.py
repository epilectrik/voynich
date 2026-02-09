"""
20_section_distribution.py

SECTION DISTRIBUTION TEST

Question: Does the WITH-RI vs WITHOUT-RI split vary by section (H, P, T)?

If one section has more process annotations, that tells us what that section is for.

Currier A sections:
- H = Herbal
- P = Pharmaceutical
- T = (need to check)
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("SECTION DISTRIBUTION TEST")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD PARAGRAPH INVENTORY WITH SECTIONS
# =============================================================
print("\n[1/3] Building paragraph inventory with sections...")

folio_paragraphs = defaultdict(list)
folio_sections = {}
current_para_tokens = []
current_folio = None

for t in tx.currier_a():
    if not t.word or '*' in t.word:
        continue

    # Track section for each folio
    if t.folio not in folio_sections:
        folio_sections[t.folio] = t.section

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

# Show section distribution
section_counts = Counter(folio_sections.values())
print(f"\nSections in Currier A:")
for section, count in sorted(section_counts.items()):
    print(f"   {section}: {count} folios")

# =============================================================
# STEP 2: COUNT BY SECTION AND TYPE
# =============================================================
print("\n[2/3] Counting paragraphs by section and type...")

# Counters by section
section_with_ri = Counter()
section_without_ri = Counter()
section_folios = Counter()

for folio, paragraphs in folio_paragraphs.items():
    section = folio_sections.get(folio, 'UNKNOWN')
    section_folios[section] += 1

    for para_tokens in paragraphs:
        if not para_tokens:
            continue

        if has_initial_ri(para_tokens, analyzer):
            section_with_ri[section] += 1
        else:
            section_without_ri[section] += 1

# =============================================================
# STEP 3: ANALYZE DISTRIBUTION
# =============================================================
print("\n[3/3] Analyzing distribution by section...")

all_sections = sorted(set(section_with_ri.keys()) | set(section_without_ri.keys()))

print(f"\nPARAGRAPH TYPE DISTRIBUTION BY SECTION:")
print(f"{'Section':<12} {'Folios':>8} {'WITH-RI':>10} {'WITHOUT-RI':>12} {'% WITHOUT':>12} {'Ratio':>10}")
print("-" * 66)

section_stats = {}
overall_pct_without = 100 * sum(section_without_ri.values()) / (sum(section_with_ri.values()) + sum(section_without_ri.values()))

for section in all_sections:
    n_folios = section_folios[section]
    n_with = section_with_ri[section]
    n_without = section_without_ri[section]
    total = n_with + n_without
    pct_without = 100 * n_without / total if total > 0 else 0

    # Ratio vs overall
    ratio = pct_without / overall_pct_without if overall_pct_without > 0 else 0

    marker = ""
    if ratio > 1.2:
        marker = ">> MORE WITHOUT"
    elif ratio < 0.8:
        marker = "<< LESS WITHOUT"

    print(f"{section:<12} {n_folios:>8} {n_with:>10} {n_without:>12} {pct_without:>11.1f}% {ratio:>9.2f}x {marker}")

    section_stats[section] = {
        'folios': n_folios,
        'with_ri': n_with,
        'without_ri': n_without,
        'pct_without': pct_without,
        'ratio_vs_overall': ratio
    }

print(f"\n{'OVERALL':<12} {sum(section_folios.values()):>8} {sum(section_with_ri.values()):>10} {sum(section_without_ri.values()):>12} {overall_pct_without:>11.1f}%")

# =============================================================
# PER-FOLIO ANALYSIS
# =============================================================
print("\n" + "="*70)
print("PER-FOLIO ANALYSIS")
print("="*70)

# What's the distribution of WITHOUT-RI paragraphs per folio?
folio_without_counts = defaultdict(int)
folio_total_counts = defaultdict(int)

for folio, paragraphs in folio_paragraphs.items():
    for para_tokens in paragraphs:
        if not para_tokens:
            continue
        folio_total_counts[folio] += 1
        if not has_initial_ri(para_tokens, analyzer):
            folio_without_counts[folio] += 1

# By section
for section in all_sections:
    section_folio_list = [f for f in folio_paragraphs.keys() if folio_sections.get(f) == section]

    all_without = [folio_without_counts[f] for f in section_folio_list]
    all_total = [folio_total_counts[f] for f in section_folio_list]
    all_pct = [100 * folio_without_counts[f] / folio_total_counts[f] if folio_total_counts[f] > 0 else 0 for f in section_folio_list]

    avg_without = sum(all_without) / len(all_without) if all_without else 0
    avg_pct = sum(all_pct) / len(all_pct) if all_pct else 0

    # Folios with 0 WITHOUT-RI
    n_zero = sum(1 for f in section_folio_list if folio_without_counts[f] == 0)

    # Folios where ALL paragraphs are WITHOUT-RI
    n_all_without = sum(1 for f in section_folio_list if folio_without_counts[f] == folio_total_counts[f] and folio_total_counts[f] > 0)

    print(f"\nSection {section}:")
    print(f"  Avg WITHOUT-RI per folio: {avg_without:.1f}")
    print(f"  Avg % WITHOUT-RI per folio: {avg_pct:.1f}%")
    print(f"  Folios with 0 WITHOUT-RI: {n_zero}/{len(section_folio_list)} ({100*n_zero/len(section_folio_list):.1f}%)")
    print(f"  Folios ALL WITHOUT-RI: {n_all_without}/{len(section_folio_list)} ({100*n_all_without/len(section_folio_list):.1f}%)")

# =============================================================
# SPECIFIC EXAMPLES
# =============================================================
print("\n" + "="*70)
print("EXTREME EXAMPLES")
print("="*70)

# Folios with highest % WITHOUT-RI
folio_pcts = [(f, 100 * folio_without_counts[f] / folio_total_counts[f], folio_sections.get(f, '?'))
              for f in folio_total_counts.keys() if folio_total_counts[f] > 0]
folio_pcts.sort(key=lambda x: -x[1])

print(f"\nFolios with HIGHEST % WITHOUT-RI:")
for folio, pct, section in folio_pcts[:10]:
    total = folio_total_counts[folio]
    without = folio_without_counts[folio]
    print(f"   {folio} ({section}): {pct:.0f}% ({without}/{total} paragraphs)")

print(f"\nFolios with LOWEST % WITHOUT-RI (excluding 0):")
folio_pcts_nonzero = [(f, pct, s) for f, pct, s in folio_pcts if pct > 0]
folio_pcts_nonzero.sort(key=lambda x: x[1])
for folio, pct, section in folio_pcts_nonzero[:10]:
    total = folio_total_counts[folio]
    without = folio_without_counts[folio]
    print(f"   {folio} ({section}): {pct:.0f}% ({without}/{total} paragraphs)")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("\nQuestion: Does the WITH-RI/WITHOUT-RI split vary by section?")
print("-" * 60)

# Find sections with significant deviation
deviations = [(s, stats['ratio_vs_overall'], stats['pct_without']) for s, stats in section_stats.items()]
high_without = [s for s, r, p in deviations if r > 1.2]
low_without = [s for s, r, p in deviations if r < 0.8]

if high_without:
    print(f"+ Sections with MORE WITHOUT-RI: {', '.join(high_without)}")
if low_without:
    print(f"+ Sections with LESS WITHOUT-RI: {', '.join(low_without)}")

if high_without or low_without:
    print("""
Section-specific patterns detected:
- Different sections have different paragraph type distributions
- This may reflect different content organization strategies
""")
    verdict = "SECTION_VARIATION"
else:
    print("""
No significant section-specific patterns.
The WITH-RI/WITHOUT-RI split is consistent across sections.
""")
    verdict = "NO_SECTION_VARIATION"

# Interpretation of specific sections
print("\n" + "-"*60)
print("SECTION CHARACTERIZATION:")
for section, stats in sorted(section_stats.items()):
    pct = stats['pct_without']
    ratio = stats['ratio_vs_overall']
    if ratio > 1.2:
        print(f"  {section}: Process-heavy (more annotations)")
    elif ratio < 0.8:
        print(f"  {section}: Material-heavy (more identifications)")
    else:
        print(f"  {section}: Balanced")

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'SECTION_DISTRIBUTION',
    'overall_pct_without': overall_pct_without,
    'by_section': section_stats,
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'section_distribution.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
