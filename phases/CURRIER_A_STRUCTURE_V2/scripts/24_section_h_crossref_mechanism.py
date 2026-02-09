"""
24_section_h_crossref_mechanism.py

SECTION H CROSS-REFERENCE MECHANISM

Question: How does the cross-reference system work in Section H?

We found:
- Section H has 3.87x more ct-LINKER in WITHOUT-RI paragraphs
- ct-prefix RI tokens are "linkers"

Investigate:
1. What specific ct-prefix RI tokens appear in Section H?
2. What do they co-occur with (in same line/paragraph)?
3. Is there an input->output pattern?
4. Do they link to specific folios/materials?
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("SECTION H CROSS-REFERENCE MECHANISM")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: COLLECT ALL CT-PREFIX TOKENS IN SECTION H
# =============================================================
print("\n[1/4] Collecting ct-prefix tokens in Section H...")

# First build paragraph structure
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

# Collect ct-prefix data from Section H
ct_data = []  # All ct-prefix occurrences with context

for folio, paragraphs in folio_paragraphs.items():
    if folio_sections.get(folio) != 'H':
        continue

    n_paras = len(paragraphs)
    for para_idx, para_tokens in enumerate(paragraphs):
        if not para_tokens:
            continue

        is_without_ri = not has_initial_ri(para_tokens, analyzer)

        if n_paras == 1:
            position = 'ONLY'
        elif para_idx == 0:
            position = 'FIRST'
        elif para_idx == n_paras - 1:
            position = 'LAST'
        else:
            position = 'MIDDLE'

        lines = sorted(set(t.line for t in para_tokens))

        for line in lines:
            try:
                record = analyzer.analyze_record(folio, line)
                if not record:
                    continue

                # Find ct-prefix tokens (both RI and PP)
                line_ri = []
                line_pp = []
                ct_tokens = []

                for t in record.tokens:
                    if t.token_class == 'RI' and t.word:
                        line_ri.append(t)
                        if t.word.startswith('ct'):
                            ct_tokens.append(('RI', t))
                    elif t.token_class == 'PP' and t.word:
                        line_pp.append(t)
                        if t.word.startswith('ct'):
                            ct_tokens.append(('PP', t))

                for token_class, ct_token in ct_tokens:
                    # Get co-occurring tokens
                    other_ri = [t.word for t in line_ri if t.word != ct_token.word]
                    pp_words = [t.word for t in line_pp if t.word != ct_token.word]

                    # Get PP prefixes
                    pp_prefixes = []
                    for t in line_pp:
                        if t.word and t.word != ct_token.word:
                            try:
                                m = morph.extract(t.word)
                                if m.prefix:
                                    pp_prefixes.append(m.prefix)
                            except:
                                pass

                    ct_data.append({
                        'folio': folio,
                        'line': line,
                        'para_position': position,
                        'is_without_ri': is_without_ri,
                        'ct_word': ct_token.word,
                        'ct_class': token_class,
                        'other_ri': other_ri,
                        'pp_words': pp_words[:5],  # Sample
                        'pp_prefixes': pp_prefixes,
                        'n_ri_on_line': len(line_ri),
                        'n_pp_on_line': len(line_pp)
                    })
            except:
                pass

print(f"   Total ct-prefix occurrences in Section H: {len(ct_data)}")
print(f"   In WITHOUT-RI paragraphs: {sum(1 for d in ct_data if d['is_without_ri'])}")
print(f"   In WITH-RI paragraphs: {sum(1 for d in ct_data if not d['is_without_ri'])}")

# =============================================================
# STEP 2: ANALYZE CT-PREFIX TOKENS
# =============================================================
print("\n[2/4] Analyzing ct-prefix tokens...")

# Most common ct-prefix tokens
ct_words = Counter(d['ct_word'] for d in ct_data)
print(f"\nMost common ct-prefix tokens in Section H:")
for word, count in ct_words.most_common(15):
    print(f"   {word}: {count}")

# Token class distribution
ct_class_dist = Counter(d['ct_class'] for d in ct_data)
print(f"\nct-prefix by token class:")
for cls, count in ct_class_dist.items():
    print(f"   {cls}: {count} ({100*count/len(ct_data):.1f}%)")

# Position distribution
ct_position_dist = Counter(d['para_position'] for d in ct_data)
print(f"\nct-prefix by paragraph position:")
for pos, count in sorted(ct_position_dist.items()):
    print(f"   {pos}: {count}")

# =============================================================
# STEP 3: WHAT DO CT-TOKENS CO-OCCUR WITH?
# =============================================================
print("\n[3/4] Analyzing co-occurrence patterns...")

# PP prefixes that co-occur with ct-tokens
cooccur_prefixes = Counter()
for d in ct_data:
    cooccur_prefixes.update(d['pp_prefixes'])

total_cooccur = sum(cooccur_prefixes.values())
print(f"\nPP prefixes co-occurring with ct-tokens on same line:")
print(f"{'PREFIX':<12} {'Count':>8} {'%':>8}")
print("-" * 30)
for prefix, count in cooccur_prefixes.most_common(15):
    pct = 100 * count / total_cooccur if total_cooccur > 0 else 0
    print(f"{prefix:<12} {count:>8} {pct:>7.1f}%")

# Other RI tokens that co-occur
cooccur_ri = Counter()
for d in ct_data:
    cooccur_ri.update(d['other_ri'])

print(f"\nOther RI tokens co-occurring with ct-tokens on same line:")
for ri, count in cooccur_ri.most_common(10):
    print(f"   {ri}: {count}")

# =============================================================
# STEP 4: SPECIFIC EXAMPLES
# =============================================================
print("\n[4/4] Examining specific examples...")

print("\n" + "="*70)
print("EXAMPLES: CT-PREFIX IN WITHOUT-RI PARAGRAPHS (Section H)")
print("="*70)

wo_ct = [d for d in ct_data if d['is_without_ri']]
print(f"\nSample ct-prefix occurrences in WITHOUT-RI paragraphs:")
for d in wo_ct[:20]:
    other_ri_str = ', '.join(d['other_ri'][:3]) if d['other_ri'] else '(none)'
    pp_str = ', '.join(d['pp_prefixes'][:5]) if d['pp_prefixes'] else '(none)'
    print(f"   {d['folio']}:{d['line']} [{d['para_position']}] {d['ct_word']} ({d['ct_class']})")
    print(f"      Other RI: {other_ri_str}")
    print(f"      PP prefixes: {pp_str}")

# =============================================================
# STEP 5: STRUCTURAL ANALYSIS
# =============================================================
print("\n" + "="*70)
print("STRUCTURAL ANALYSIS: What does ct-prefix link?")
print("="*70)

# Do ct-tokens appear alone or with other RI?
alone = sum(1 for d in ct_data if d['n_ri_on_line'] == 1 and d['ct_class'] == 'RI')
with_other_ri = sum(1 for d in ct_data if d['n_ri_on_line'] > 1 and d['ct_class'] == 'RI')
as_pp = sum(1 for d in ct_data if d['ct_class'] == 'PP')

print(f"\nct-token structural context:")
print(f"   ct as only RI on line: {alone}")
print(f"   ct with other RI on line: {with_other_ri}")
print(f"   ct as PP (not RI): {as_pp}")

# When ct appears with other RI, what are those RI?
ri_with_ct = []
for d in ct_data:
    if d['ct_class'] == 'RI' and d['other_ri']:
        ri_with_ct.extend(d['other_ri'])

print(f"\nRI tokens that appear WITH ct-prefix RI on same line:")
ri_with_ct_counter = Counter(ri_with_ct)
for ri, count in ri_with_ct_counter.most_common(10):
    print(f"   {ri}: {count}")

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

# Check for input->output pattern
print("\nHypothesis: ct-prefix links input materials to output materials")
print("-" * 60)

# Look at ct morphology
ct_middles = Counter()
for d in ct_data:
    try:
        m = morph.extract(d['ct_word'])
        if m.middle:
            ct_middles[m.middle] += 1
    except:
        pass

print(f"\nct-prefix MIDDLE components:")
for middle, count in ct_middles.most_common(10):
    print(f"   {middle}: {count}")

# Check if ct-MIDDLEs appear elsewhere as non-ct tokens
print(f"\nDo ct-MIDDLEs appear as standalone tokens elsewhere?")

# Build MIDDLE vocabulary from all of Section H
h_middles = Counter()
for folio, paragraphs in folio_paragraphs.items():
    if folio_sections.get(folio) != 'H':
        continue
    for para in paragraphs:
        for t in para:
            if t.word:
                try:
                    m = morph.extract(t.word)
                    if m.middle:
                        h_middles[m.middle] += 1
                except:
                    pass

# Check overlap
print(f"\nTop ct-MIDDLEs and their overall frequency in Section H:")
for middle, ct_count in ct_middles.most_common(10):
    total_count = h_middles.get(middle, 0)
    print(f"   {middle}: {ct_count} as ct-prefix, {total_count} total in H")

# Final interpretation
print("\n" + "-"*60)
print("CROSS-REFERENCE MECHANISM:")

if ct_class_dist.get('RI', 0) > ct_class_dist.get('PP', 0):
    print(f"""
ct-prefix tokens in Section H are primarily RI tokens ({ct_class_dist.get('RI', 0)}/{len(ct_data)}).

The pattern suggests:
1. ct-prefix RI = LINKER that references other materials
2. The MIDDLE of ct-token may identify the linked material
3. ct appears both alone and with other RI (material identification)

Common ct-tokens: {', '.join(w for w, c in ct_words.most_common(5))}
""")
else:
    print(f"""
ct-prefix tokens in Section H appear as both RI and PP.
The cross-reference function may work at the vocabulary level.
""")

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'SECTION_H_CROSSREF_MECHANISM',
    'ct_count': len(ct_data),
    'ct_in_without_ri': sum(1 for d in ct_data if d['is_without_ri']),
    'ct_words': dict(ct_words.most_common(20)),
    'ct_class_dist': dict(ct_class_dist),
    'ct_middles': dict(ct_middles.most_common(10)),
    'cooccur_prefixes': dict(cooccur_prefixes.most_common(10))
}

output_path = Path(__file__).parent.parent / 'results' / 'section_h_crossref_mechanism.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
