"""
02_non_containment_cases.py - Analyze the 9.1% of RI that doesn't contain PP

These RI MIDDLEs don't have any PP MIDDLE as substring. Are they:
- Truly independent vocabulary?
- Using rare/short PP we missed?
- Label-only or text-only?
- Concentrated in specific folios/sections?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import pandas as pd
import json

tx = Transcript()
morph = Morphology()

# Build B vocabulary (PP MIDDLEs)
print("Building vocabulary...")
b_middles = set()
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        b_middles.add(m.middle)

pp_sorted = sorted(b_middles, key=len, reverse=True)
print(f"  PP vocabulary: {len(b_middles)} MIDDLEs")

# Load raw transcript for label info
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A']

def contains_pp(ri_middle, min_pp_len=2):
    """Check if RI contains any PP as substring."""
    for pp in pp_sorted:
        if len(pp) >= min_pp_len:
            if pp in ri_middle and pp != ri_middle:
                return pp
    return None

# Collect non-containment cases
print("Finding non-containment cases...")
non_containment = []

for _, row in df_a.iterrows():
    m = morph.extract(row['word'])
    if m and m.middle and m.middle not in b_middles:
        pp_found = contains_pp(m.middle)
        if pp_found is None:
            non_containment.append({
                'word': row['word'],
                'middle': m.middle,
                'prefix': m.prefix,
                'suffix': m.suffix,
                'folio': row['folio'],
                'section': row.get('section', 'Unknown'),
                'placement': row['placement'],
                'is_label': str(row['placement']).startswith('L')
            })

print(f"  Non-containment cases: {len(non_containment)}")

# ============================================================
# ANALYSIS 1: Basic Statistics
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 1: NON-CONTAINMENT STATISTICS")
print("="*70)

# Unique MIDDLEs
unique_middles = set(r['middle'] for r in non_containment)
print(f"\nTotal tokens: {len(non_containment)}")
print(f"Unique MIDDLEs: {len(unique_middles)}")

middle_counts = Counter(r['middle'] for r in non_containment)
print(f"\nMost common non-containment MIDDLEs:")
for middle, count in middle_counts.most_common(20):
    print(f"  '{middle}': {count}")

# ============================================================
# ANALYSIS 2: Label vs Text
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 2: LABEL VS TEXT")
print("="*70)

label_cases = [r for r in non_containment if r['is_label']]
text_cases = [r for r in non_containment if not r['is_label']]

print(f"\nLabel tokens: {len(label_cases)} ({100*len(label_cases)/len(non_containment):.1f}%)")
print(f"Text tokens: {len(text_cases)} ({100*len(text_cases)/len(non_containment):.1f}%)")

if label_cases:
    print(f"\nLabel non-containment examples:")
    for r in label_cases[:10]:
        print(f"  {r['folio']} {r['placement']}: {r['word']} (MIDDLE: {r['middle']})")

# ============================================================
# ANALYSIS 3: Section Distribution
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 3: SECTION DISTRIBUTION")
print("="*70)

section_counts = Counter(r['section'] for r in non_containment)
print(f"\nBy section:")
for section, count in section_counts.most_common():
    print(f"  Section {section}: {count}")

# ============================================================
# ANALYSIS 4: Folio Concentration
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 4: FOLIO CONCENTRATION")
print("="*70)

folio_counts = Counter(r['folio'] for r in non_containment)
print(f"\nFolios with most non-containment cases:")
for folio, count in folio_counts.most_common(10):
    print(f"  {folio}: {count}")

# ============================================================
# ANALYSIS 5: Morphological Analysis
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 5: MORPHOLOGICAL STRUCTURE")
print("="*70)

prefix_counts = Counter(r['prefix'] for r in non_containment if r['prefix'])
suffix_counts = Counter(r['suffix'] for r in non_containment if r['suffix'])

print(f"\nPREFIX distribution:")
for prefix, count in prefix_counts.most_common(10):
    print(f"  {prefix}: {count}")

print(f"\nSUFFIX distribution:")
for suffix, count in suffix_counts.most_common(10):
    print(f"  {suffix}: {count}")

# MIDDLE length
middle_lengths = [len(r['middle']) for r in non_containment]
print(f"\nMIDDLE length:")
print(f"  Mean: {sum(middle_lengths)/len(middle_lengths):.2f}")
print(f"  Min: {min(middle_lengths)}, Max: {max(middle_lengths)}")

# ============================================================
# ANALYSIS 6: Character Composition
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 6: CHARACTER COMPOSITION")
print("="*70)

# What characters appear in non-containment MIDDLEs?
all_chars = Counter()
for r in non_containment:
    for c in r['middle']:
        all_chars[c] += 1

print(f"\nCharacter frequency in non-containment MIDDLEs:")
for char, count in all_chars.most_common(15):
    print(f"  '{char}': {count}")

# ============================================================
# ANALYSIS 7: Short PP Check
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 7: SHORT PP CHECK")
print("="*70)

# Check if these contain 1-char PP (which we excluded)
short_pp = {pp for pp in b_middles if len(pp) == 1}
print(f"\n1-char PP MIDDLEs in B: {short_pp}")

contains_short = 0
for r in non_containment:
    for pp in short_pp:
        if pp in r['middle']:
            contains_short += 1
            break

print(f"\nNon-containment MIDDLEs containing 1-char PP: {contains_short}/{len(non_containment)}")

# What if we lower threshold to 1-char?
contains_any = 0
for r in non_containment:
    for pp in b_middles:
        if len(pp) >= 1 and pp in r['middle']:
            contains_any += 1
            break

print(f"Non-containment MIDDLEs containing any PP (1+ char): {contains_any}/{len(non_containment)}")

# ============================================================
# ANALYSIS 8: Truly Novel Cases
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 8: TRULY NOVEL CASES")
print("="*70)

# MIDDLEs that don't contain ANY PP substring (even 1-char)
truly_novel = []
for r in non_containment:
    contains = False
    for pp in b_middles:
        if pp in r['middle']:
            contains = True
            break
    if not contains:
        truly_novel.append(r)

print(f"\nTruly novel MIDDLEs (no PP substring at all): {len(truly_novel)}")
if truly_novel:
    print(f"\nExamples:")
    for r in truly_novel[:20]:
        print(f"  {r['folio']}: {r['word']} (MIDDLE: {r['middle']})")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
Non-containment cases: {len(non_containment)} tokens, {len(unique_middles)} unique MIDDLEs

Distribution:
- Labels: {len(label_cases)} ({100*len(label_cases)/len(non_containment):.1f}%)
- Text: {len(text_cases)} ({100*len(text_cases)/len(non_containment):.1f}%)

Section concentration:
{chr(10).join(f'  - Section {s}: {c}' for s, c in section_counts.most_common(3))}

Truly novel (no PP substring): {len(truly_novel)}

These cases may represent:
- Independent vocabulary outside the PP+extension system
- Very specialized/rare identifiers
- Possible transcription artifacts
""")

# Save results
output = {
    'total_non_containment': len(non_containment),
    'unique_middles': len(unique_middles),
    'label_count': len(label_cases),
    'text_count': len(text_cases),
    'section_distribution': dict(section_counts),
    'truly_novel_count': len(truly_novel),
    'top_middles': dict(middle_counts.most_common(20)),
    'truly_novel_examples': [r['middle'] for r in truly_novel[:20]]
}

with open('C:/git/voynich/phases/RI_EXTENSION_MAPPING/results/non_containment_cases.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Results saved to non_containment_cases.json")
