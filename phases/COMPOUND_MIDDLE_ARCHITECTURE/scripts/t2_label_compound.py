"""
T2: L-Placement (Label) Compound Analysis

Question: Do illustration/jar labels show the same compound identification pattern
as line-1 HT tokens?

Method:
1. Extract all L-placement tokens using Transcript with exclude_labels=False
2. Analyze their MIDDLE structure
3. Check folio-uniqueness and compound rates
4. Compare to line-1 HT pattern
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Get all tokens including labels
all_tokens = list(tx.all(h_only=True))
print(f"Total H-track tokens: {len(all_tokens)}")

# Separate by placement type
text_tokens = [t for t in all_tokens if t.placement.startswith('P')]
label_tokens = [t for t in all_tokens if t.placement.startswith('L')]

print(f"P-placement (text): {len(text_tokens)}")
print(f"L-placement (labels): {len(label_tokens)}")
print()

# Get label distribution by language
label_by_lang = Counter(t.language for t in label_tokens)
print("L-placement by language:")
for lang, count in sorted(label_by_lang.items()):
    print(f"  {lang}: {count}")
print()

# Extract MIDDLEs from labels
label_middles = []
for token in label_tokens:
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        label_middles.append({
            'word': w,
            'middle': m.middle,
            'folio': token.folio,
            'language': token.language
        })

print(f"Labels with extractable MIDDLEs: {len(label_middles)}")

# Build MIDDLE -> folios mapping from B text (for core MIDDLE reference)
middle_to_folios_b = defaultdict(set)
for token in tx.currier_b():
    m = morph.extract(token.word)
    if m.middle:
        middle_to_folios_b[m.middle].add(token.folio)

core_middles_b = {mid for mid, folios in middle_to_folios_b.items() if len(folios) >= 20}
print(f"Core B MIDDLEs (20+ folios): {len(core_middles_b)}")

# Build MIDDLE -> folios mapping from labels only
label_middle_to_folios = defaultdict(set)
for item in label_middles:
    label_middle_to_folios[item['middle']].add(item['folio'])

def contains_core(middle, core_set, min_len=2):
    """Check if middle contains any core MIDDLE as substring"""
    for core in core_set:
        if len(core) >= min_len and core in middle and core != middle:
            return True
    return False

# Analyze labels by language
print("\n" + "="*60)
print("LABEL ANALYSIS BY LANGUAGE")
print("="*60)

results_by_lang = {}

for lang in ['A', 'B', 'NA']:
    lang_labels = [item for item in label_middles if item['language'] == lang]
    if not lang_labels:
        continue

    unique_middles = set(item['middle'] for item in lang_labels)

    # Check folio-uniqueness within this language's labels
    lang_mid_to_folios = defaultdict(set)
    for item in lang_labels:
        lang_mid_to_folios[item['middle']].add(item['folio'])

    folio_unique = sum(1 for mid, folios in lang_mid_to_folios.items() if len(folios) == 1)
    folio_unique_rate = 100 * folio_unique / len(unique_middles) if unique_middles else 0

    # Check compound rate (using B's core MIDDLEs as reference)
    compound_count = sum(1 for mid in unique_middles if contains_core(mid, core_middles_b))
    compound_rate = 100 * compound_count / len(unique_middles) if unique_middles else 0

    # Length stats
    lengths = [len(mid) for mid in unique_middles]
    mean_len = sum(lengths) / len(lengths) if lengths else 0

    print(f"\nLanguage {lang} Labels:")
    print(f"  Token count: {len(lang_labels)}")
    print(f"  Unique MIDDLEs: {len(unique_middles)}")
    print(f"  Folio-unique rate: {folio_unique}/{len(unique_middles)} = {folio_unique_rate:.1f}%")
    print(f"  Compound rate (contains B core): {compound_count}/{len(unique_middles)} = {compound_rate:.1f}%")
    print(f"  Mean MIDDLE length: {mean_len:.2f}")

    # Show examples
    print(f"  Sample MIDDLEs:")
    for mid in sorted(unique_middles, key=len, reverse=True)[:8]:
        is_compound = contains_core(mid, core_middles_b)
        is_folio_unique = len(lang_mid_to_folios[mid]) == 1
        markers = []
        if is_compound:
            markers.append("COMPOUND")
        if is_folio_unique:
            markers.append("FOLIO-UNIQUE")
        print(f"    '{mid}' (len={len(mid)}) {' '.join(markers)}")

    results_by_lang[lang] = {
        'token_count': len(lang_labels),
        'unique_middles': len(unique_middles),
        'folio_unique_rate': folio_unique_rate,
        'compound_rate': compound_rate,
        'mean_length': mean_len
    }

# Compare to line-1 HT reference values
print("\n" + "="*60)
print("COMPARISON TO LINE-1 HT PATTERN")
print("="*60)

print("""
Reference (Line-1 HT folio-unique MIDDLEs):
  - Folio-unique rate: 21.7% (vs 11.7% working HT)
  - Compound rate: 84.8% (contain core B MIDDLEs)
  - Mean length: 4.63 chars
  - Length-controlled baseline: 54.9% (so 84.8% is +29.9pp above chance)
""")

# Overall label statistics
all_label_middles = set(item['middle'] for item in label_middles)
all_label_compound = sum(1 for mid in all_label_middles if contains_core(mid, core_middles_b))
all_label_compound_rate = 100 * all_label_compound / len(all_label_middles) if all_label_middles else 0

print(f"All labels combined:")
print(f"  Unique MIDDLEs: {len(all_label_middles)}")
print(f"  Compound rate: {all_label_compound_rate:.1f}%")

# Check if label MIDDLEs appear in B text
label_in_b_text = sum(1 for mid in all_label_middles if mid in middle_to_folios_b)
print(f"  Label MIDDLEs also in B text: {label_in_b_text}/{len(all_label_middles)} = {100*label_in_b_text/len(all_label_middles):.1f}%")

# Verdict
print("\n" + "="*60)
print("VERDICT")
print("="*60)

# Check A labels (herbal jar labels)
if 'A' in results_by_lang:
    a_compound = results_by_lang['A']['compound_rate']
    a_folio_unique = results_by_lang['A']['folio_unique_rate']
    print(f"\nCurrier A Labels (herbal/jar labels):")
    print(f"  Compound rate: {a_compound:.1f}%")
    print(f"  Folio-unique rate: {a_folio_unique:.1f}%")
    if a_compound > 60 and a_folio_unique > 50:
        print(f"  -> STRONG identification pattern (like line-1 HT)")
    elif a_compound > 40:
        print(f"  -> MODERATE compound structure")
    else:
        print(f"  -> WEAK compound structure")

if 'B' in results_by_lang:
    b_compound = results_by_lang['B']['compound_rate']
    b_folio_unique = results_by_lang['B']['folio_unique_rate']
    print(f"\nCurrier B Labels:")
    print(f"  Compound rate: {b_compound:.1f}%")
    print(f"  Folio-unique rate: {b_folio_unique:.1f}%")

# Save results
results = {
    'label_counts': {
        'total': len(label_middles),
        'by_language': dict(label_by_lang)
    },
    'by_language': results_by_lang,
    'all_labels': {
        'unique_middles': len(all_label_middles),
        'compound_rate': all_label_compound_rate,
        'in_b_text_rate': 100 * label_in_b_text / len(all_label_middles) if all_label_middles else 0
    }
}

out_path = PROJECT_ROOT / 'phases' / 'COMPOUND_MIDDLE_ARCHITECTURE' / 'results' / 't2_label_compound.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
