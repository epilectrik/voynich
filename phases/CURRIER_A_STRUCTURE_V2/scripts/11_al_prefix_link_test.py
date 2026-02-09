"""
11_al_prefix_link_test.py

FOLLOW-UP TEST: al-prefix enrichment in final WITHOUT-RI paragraphs

Finding: Final WITHOUT-RI paragraphs are 6.0x enriched for al-prefix PP.
Context: al is LINK-ATTRACTED (C373) - associated with monitoring/intervention.

Questions:
1. Are al-prefix PP tokens co-locating with linker RI tokens?
2. Do al-prefix PP tokens appear in specific line positions?
3. Is al-enrichment specific to final paragraphs, or all WITHOUT-RI?
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("AL-PREFIX LINK-ATTRACTION TEST")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD PARAGRAPH INVENTORY
# =============================================================
print("\n[1/4] Building paragraph inventory...")

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
# STEP 2: ANALYZE AL-PREFIX DISTRIBUTION BY PARAGRAPH TYPE
# =============================================================
print("\n[2/4] Analyzing al-prefix distribution...")

def analyze_paragraph_al(folio, para_tokens, analyzer, morph):
    """Analyze al-prefix presence and co-location with linkers."""
    lines = sorted(set(t.line for t in para_tokens))

    al_pp_tokens = []
    linker_ri_tokens = []
    other_pp_tokens = []
    all_ri_tokens = []

    # Per-line tracking
    line_has_al = {}
    line_has_linker = {}

    for line in lines:
        line_al = []
        line_linker = []

        try:
            record = analyzer.analyze_record(folio, line)
            if record:
                for t in record.tokens:
                    if t.token_class == 'PP' and t.word:
                        try:
                            m = morph.extract(t.word)
                            if m.prefix == 'al':
                                al_pp_tokens.append(t)
                                line_al.append(t)
                            else:
                                other_pp_tokens.append(t)
                        except:
                            other_pp_tokens.append(t)
                    elif t.token_class == 'RI':
                        all_ri_tokens.append(t)
                        if t.word and t.word.startswith('ct'):
                            linker_ri_tokens.append(t)
                            line_linker.append(t)
        except:
            pass

        line_has_al[line] = len(line_al) > 0
        line_has_linker[line] = len(line_linker) > 0

    # Co-location: lines with both al-prefix PP AND linker RI
    coloc_lines = sum(1 for l in lines if line_has_al.get(l) and line_has_linker.get(l))
    al_lines = sum(1 for l in lines if line_has_al.get(l))
    linker_lines = sum(1 for l in lines if line_has_linker.get(l))

    return {
        'n_al_pp': len(al_pp_tokens),
        'n_linker_ri': len(linker_ri_tokens),
        'n_other_pp': len(other_pp_tokens),
        'n_all_ri': len(all_ri_tokens),
        'n_lines': len(lines),
        'al_lines': al_lines,
        'linker_lines': linker_lines,
        'coloc_lines': coloc_lines,
        'al_tokens': [t.word for t in al_pp_tokens]
    }

# Classify and analyze paragraphs
final_with_ri = []
final_without_ri = []
non_final_with_ri = []
non_final_without_ri = []

for folio, paragraphs in folio_paragraphs.items():
    if len(paragraphs) < 2:
        continue

    # Final paragraph
    final_para = paragraphs[-1]
    final_analysis = analyze_paragraph_al(folio, final_para, analyzer, morph)
    final_analysis['folio'] = folio

    if has_initial_ri(final_para, analyzer):
        final_with_ri.append(final_analysis)
    else:
        final_without_ri.append(final_analysis)

    # Non-final paragraphs
    for para in paragraphs[:-1]:
        analysis = analyze_paragraph_al(folio, para, analyzer, morph)
        analysis['folio'] = folio

        if has_initial_ri(para, analyzer):
            non_final_with_ri.append(analysis)
        else:
            non_final_without_ri.append(analysis)

print(f"   Final WITH-RI: {len(final_with_ri)}")
print(f"   Final WITHOUT-RI: {len(final_without_ri)}")
print(f"   Non-final WITH-RI: {len(non_final_with_ri)}")
print(f"   Non-final WITHOUT-RI: {len(non_final_without_ri)}")

# =============================================================
# STEP 3: AL-PREFIX RATE COMPARISON
# =============================================================
print("\n[3/4] Comparing al-prefix rates...")

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

def compute_al_rate(analyses):
    """Compute al-prefix PP as % of total PP."""
    total_al = sum(a['n_al_pp'] for a in analyses)
    total_pp = sum(a['n_al_pp'] + a['n_other_pp'] for a in analyses)
    return 100 * total_al / total_pp if total_pp > 0 else 0

def compute_coloc_rate(analyses):
    """Compute % of al-lines that also have linkers."""
    total_al_lines = sum(a['al_lines'] for a in analyses)
    total_coloc = sum(a['coloc_lines'] for a in analyses)
    return 100 * total_coloc / total_al_lines if total_al_lines > 0 else 0

print(f"\nAL-PREFIX PP RATE (% of all PP):")
print(f"{'Category':<30} {'al-rate':>10} {'Total al':>10} {'Total PP':>10}")
print("-" * 62)

categories = [
    ('Final WITH-RI', final_with_ri),
    ('Final WITHOUT-RI', final_without_ri),
    ('Non-final WITH-RI', non_final_with_ri),
    ('Non-final WITHOUT-RI', non_final_without_ri)
]

al_rates = {}
for name, analyses in categories:
    al_rate = compute_al_rate(analyses)
    total_al = sum(a['n_al_pp'] for a in analyses)
    total_pp = sum(a['n_al_pp'] + a['n_other_pp'] for a in analyses)
    al_rates[name] = al_rate
    print(f"{name:<30} {al_rate:>9.2f}% {total_al:>10} {total_pp:>10}")

# Key comparison: Final WITHOUT-RI vs others
print(f"\nKey ratio: Final WITHOUT-RI / Non-final WITHOUT-RI = {al_rates['Final WITHOUT-RI'] / al_rates['Non-final WITHOUT-RI']:.2f}x")
print(f"Key ratio: Final WITHOUT-RI / Final WITH-RI = {al_rates['Final WITHOUT-RI'] / al_rates['Final WITH-RI']:.2f}x")

# =============================================================
# STEP 4: CO-LOCATION ANALYSIS
# =============================================================
print("\n[4/4] Analyzing al-linker co-location...")

print(f"\nCO-LOCATION (% of al-lines with linker RI):")
print(f"{'Category':<30} {'coloc-rate':>12} {'al-lines':>10} {'coloc':>8}")
print("-" * 62)

for name, analyses in categories:
    coloc_rate = compute_coloc_rate(analyses)
    total_al_lines = sum(a['al_lines'] for a in analyses)
    total_coloc = sum(a['coloc_lines'] for a in analyses)
    print(f"{name:<30} {coloc_rate:>11.1f}% {total_al_lines:>10} {total_coloc:>8}")

# Overall co-location test
all_with_al = [a for analyses in [final_with_ri, final_without_ri, non_final_with_ri, non_final_without_ri]
               for a in analyses if a['n_al_pp'] > 0]

coloc_with_linker = sum(1 for a in all_with_al if a['coloc_lines'] > 0)
pct_coloc = 100 * coloc_with_linker / len(all_with_al) if all_with_al else 0

print(f"\nOverall: {pct_coloc:.1f}% of paragraphs with al-prefix PP also have linker RI")

# =============================================================
# STEP 5: SPECIFIC AL TOKENS
# =============================================================
print("\n" + "="*70)
print("AL-PREFIX PP TOKENS IN FINAL WITHOUT-RI PARAGRAPHS")
print("="*70)

all_al_tokens = []
for a in final_without_ri:
    all_al_tokens.extend(a['al_tokens'])

al_counter = Counter(all_al_tokens)
print(f"\nMost common al-prefix PP tokens (n={len(all_al_tokens)}):")
for token, count in al_counter.most_common(15):
    print(f"   {token}: {count}")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("\nHypothesis: al-prefix marks LINK-related content (C373: LINK-ATTRACTED)")
print("-" * 60)

# Test 1: Is al-enrichment specific to final WITHOUT-RI?
if al_rates['Final WITHOUT-RI'] > al_rates['Non-final WITHOUT-RI'] * 1.3:
    print(f"+ al-enrichment IS specific to final position ({al_rates['Final WITHOUT-RI']:.1f}% vs {al_rates['Non-final WITHOUT-RI']:.1f}%)")
    position_specific = True
else:
    print(f"- al-enrichment is NOT position-specific ({al_rates['Final WITHOUT-RI']:.1f}% vs {al_rates['Non-final WITHOUT-RI']:.1f}%)")
    position_specific = False

# Test 2: Does al-prefix co-locate with linker RI?
coloc_final_without = compute_coloc_rate(final_without_ri)
if coloc_final_without > 20:
    print(f"+ al-prefix DOES co-locate with linker RI ({coloc_final_without:.1f}% of al-lines)")
    colocates = True
else:
    print(f"- al-prefix does NOT strongly co-locate with linker RI ({coloc_final_without:.1f}%)")
    colocates = False

# Test 3: Is al-enrichment about opening type or position?
if al_rates['Final WITHOUT-RI'] > al_rates['Final WITH-RI'] * 1.3:
    print(f"+ al-enrichment is about OPENING TYPE, not just position")
    opening_type_effect = True
else:
    print(f"- al-enrichment is about POSITION, not opening type")
    opening_type_effect = False

print("\n" + "-"*60)
print("VERDICT:")

if position_specific and opening_type_effect:
    print("""
Final WITHOUT-RI paragraphs are structurally distinct:
- Higher al-prefix rate (LINK-ATTRACTED vocabulary)
- Combined with higher linker density (1.35x from earlier test)
- Position-specific effect (final paragraphs only)

INTERPRETATION: These may be "closing index" records that:
1. Link materials to processes across the registry
2. Appear at folio endings as cross-reference summaries
3. Use al-prefix PP to mark LINK-adjacent content
""")
    verdict = "AL_CONFIRMS_LINK_FUNCTION"
else:
    print("""
al-enrichment pattern does not clearly confirm LINK function.
May be coincidental or require different interpretation.
""")
    verdict = "INCONCLUSIVE"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'AL_PREFIX_LINK_TEST',
    'al_rates': al_rates,
    'colocation': {
        'final_without_ri': compute_coloc_rate(final_without_ri),
        'final_with_ri': compute_coloc_rate(final_with_ri),
        'non_final_without_ri': compute_coloc_rate(non_final_without_ri),
        'non_final_with_ri': compute_coloc_rate(non_final_with_ri)
    },
    'al_token_counts': dict(al_counter.most_common(20)),
    'position_specific': position_specific,
    'opening_type_effect': opening_type_effect,
    'verdict': verdict
}

output_path = Path(__file__).parent.parent / 'results' / 'al_prefix_link_test.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
