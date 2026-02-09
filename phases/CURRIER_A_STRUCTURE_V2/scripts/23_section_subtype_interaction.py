"""
23_section_subtype_interaction.py

SECTION x SUBTYPE INTERACTION

Question: Do the WITHOUT-RI sub-types differ between Section H and Section P?

Section H has 48.7% WITHOUT-RI (process-heavy)
Section P has 20.8% WITHOUT-RI (material-heavy)

Are the WITHOUT-RI paragraphs in H doing the same thing as those in P?
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("SECTION x SUBTYPE INTERACTION")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD INVENTORY WITH SECTION INFO
# =============================================================
print("\n[1/2] Building inventory with section info...")

folio_paragraphs = defaultdict(list)
folio_sections = {}
current_para_tokens = []
current_folio = None

for t in tx.currier_a():
    if not t.word or '*' in t.word:
        continue

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

def get_pp_prefixes(para_tokens, analyzer, morph):
    if not para_tokens:
        return Counter()

    folio = para_tokens[0].folio
    lines = sorted(set(t.line for t in para_tokens))
    prefixes = Counter()

    for line in lines:
        try:
            record = analyzer.analyze_record(folio, line)
            if record:
                for t in record.tokens:
                    if t.token_class == 'PP' and t.word:
                        try:
                            m = morph.extract(t.word)
                            if m.prefix:
                                prefixes[m.prefix] += 1
                        except:
                            pass
        except:
            pass
    return prefixes

# Classify by section, position, and RI type
data = defaultdict(list)  # key = (section, position, ri_type)

for folio, paragraphs in folio_paragraphs.items():
    section = folio_sections.get(folio, 'UNKNOWN')
    n = len(paragraphs)

    for i, para_tokens in enumerate(paragraphs):
        if not para_tokens:
            continue

        is_with_ri = has_initial_ri(para_tokens, analyzer)
        ri_type = 'WITH_RI' if is_with_ri else 'WITHOUT_RI'

        if n == 1:
            position = 'FIRST'
        elif i == 0:
            position = 'FIRST'
        elif i == n - 1:
            position = 'LAST'
        else:
            position = 'MIDDLE'

        prefixes = get_pp_prefixes(para_tokens, analyzer, morph)

        key = (section, position, ri_type)
        data[key].append({
            'folio': folio,
            'prefixes': prefixes
        })

# =============================================================
# STEP 2: COMPARE H vs P FOR EACH SUB-TYPE
# =============================================================
print("\n[2/2] Comparing H vs P for each sub-type...")

def aggregate_prefixes(data_list):
    total = Counter()
    for d in data_list:
        total.update(d['prefixes'])
    return total

# Focus on WITHOUT-RI comparisons
print(f"\nWITHOUT-RI PARAGRAPH COUNTS:")
print(f"{'Position':<12} {'Section H':>12} {'Section P':>12}")
print("-" * 38)

for position in ['FIRST', 'MIDDLE', 'LAST']:
    h_count = len(data.get(('H', position, 'WITHOUT_RI'), []))
    p_count = len(data.get(('P', position, 'WITHOUT_RI'), []))
    print(f"{position:<12} {h_count:>12} {p_count:>12}")

# Compare PREFIX profiles
print(f"\n" + "="*70)
print("PP PREFIX PROFILES: H vs P (WITHOUT-RI only)")
print("="*70)

major_prefixes = ['ch', 'sh', 'qo', 'ok', 'ot', 'ol', 'ct', 'da', 'yk']

for position in ['FIRST', 'MIDDLE', 'LAST']:
    h_data = data.get(('H', position, 'WITHOUT_RI'), [])
    p_data = data.get(('P', position, 'WITHOUT_RI'), [])

    if not h_data and not p_data:
        continue

    h_prefixes = aggregate_prefixes(h_data)
    p_prefixes = aggregate_prefixes(p_data)

    h_total = sum(h_prefixes.values())
    p_total = sum(p_prefixes.values())

    print(f"\n{position} WITHOUT-RI (H: {len(h_data)} paras, P: {len(p_data)} paras):")
    print(f"{'PREFIX':<8} {'H':>10} {'P':>10} {'Ratio':>10}")
    print("-" * 40)

    for prefix in major_prefixes:
        h_pct = 100 * h_prefixes[prefix] / h_total if h_total > 0 else 0
        p_pct = 100 * p_prefixes[prefix] / p_total if p_total > 0 else 0

        if h_pct > 1 or p_pct > 1:
            ratio = h_pct / p_pct if p_pct > 0 else float('inf') if h_pct > 0 else 1.0
            ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "inf"
            marker = ""
            if ratio >= 1.5:
                marker = ">> H"
            elif ratio <= 0.67:
                marker = "<< P"
            print(f"{prefix:<8} {h_pct:>9.1f}% {p_pct:>9.1f}% {ratio_str:>8} {marker}")

# =============================================================
# QUALITATIVE SUMMARY
# =============================================================
print("\n" + "="*70)
print("QUALITATIVE SUMMARY")
print("="*70)

# What makes H's WITHOUT-RI different from P's?
h_wo = []
p_wo = []
for key, items in data.items():
    section, position, ri_type = key
    if ri_type == 'WITHOUT_RI':
        if section == 'H':
            h_wo.extend(items)
        elif section == 'P':
            p_wo.extend(items)

h_prefixes = aggregate_prefixes(h_wo)
p_prefixes = aggregate_prefixes(p_wo)
h_total = sum(h_prefixes.values())
p_total = sum(p_prefixes.values())

print(f"\nOVERALL WITHOUT-RI COMPARISON:")
print(f"Section H: {len(h_wo)} paragraphs, {h_total} PP tokens")
print(f"Section P: {len(p_wo)} paragraphs, {p_total} PP tokens")

print(f"\n{'PREFIX':<8} {'H':>10} {'P':>10} {'H/P Ratio':>12}")
print("-" * 42)

differences = []
for prefix in major_prefixes:
    h_pct = 100 * h_prefixes[prefix] / h_total if h_total > 0 else 0
    p_pct = 100 * p_prefixes[prefix] / p_total if p_total > 0 else 0

    if h_pct > 0 or p_pct > 0:
        ratio = h_pct / p_pct if p_pct > 0 else float('inf') if h_pct > 0 else 1.0
        ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "inf"

        if ratio >= 1.3 or ratio <= 0.77:
            differences.append((prefix, h_pct, p_pct, ratio))

        print(f"{prefix:<8} {h_pct:>9.1f}% {p_pct:>9.1f}% {ratio_str:>10}")

print(f"\nSignificant differences (>1.3x):")
for prefix, h_pct, p_pct, ratio in sorted(differences, key=lambda x: abs(x[3]-1), reverse=True):
    direction = "H-enriched" if ratio > 1 else "P-enriched"
    print(f"  {prefix}: {ratio:.2f}x {direction}")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("""
Question: Are WITHOUT-RI paragraphs in Section H doing the same thing
          as WITHOUT-RI paragraphs in Section P?
""")

if differences:
    print("DIFFERENT: The sections use WITHOUT-RI paragraphs differently:")
    for prefix, h_pct, p_pct, ratio in differences:
        if ratio > 1.3:
            print(f"  - Section H has more {prefix} ({h_pct:.1f}% vs {p_pct:.1f}%)")
        else:
            print(f"  - Section P has more {prefix} ({p_pct:.1f}% vs {h_pct:.1f}%)")

    print("""
This suggests:
- Section H (Herbal): WITHOUT-RI serve a specific function
- Section P (Pharmaceutical): WITHOUT-RI serve a different function
""")
    verdict = "SECTION_SPECIFIC"
else:
    print("""
SIMILAR: WITHOUT-RI paragraphs have similar PP profiles across sections.
The higher count in H may reflect layout/organization, not different content.
""")
    verdict = "SECTION_INDEPENDENT"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'SECTION_SUBTYPE_INTERACTION',
    'counts': {
        'H_WITHOUT_RI': len(h_wo),
        'P_WITHOUT_RI': len(p_wo)
    },
    'differences': [(p, h, pp, r) for p, h, pp, r in differences],
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'section_subtype_interaction.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
