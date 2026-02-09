"""
01_extension_distribution.py - Map extension character patterns in RI vocabulary

RI = PP + extension. This script maps:
1. Overall extension character frequency
2. Section preferences (H/P/T)
3. Folio-level patterns
4. Extension position (prefix vs suffix of PP)
5. Multi-character extension patterns
"""

import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
from scipy import stats
import pandas as pd
import numpy as np
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

pp_sorted = sorted(b_middles, key=len, reverse=True)  # Longest first for matching
print(f"  PP vocabulary: {len(b_middles)} MIDDLEs")

# Extract extensions from RI
def get_extension(ri_middle):
    """Find the PP base and extension for an RI MIDDLE."""
    for pp in pp_sorted:
        if len(pp) >= 2:
            if ri_middle.startswith(pp) and len(ri_middle) > len(pp):
                return {
                    'pp_base': pp,
                    'extension': ri_middle[len(pp):],
                    'position': 'suffix'
                }
            elif ri_middle.endswith(pp) and len(ri_middle) > len(pp):
                return {
                    'pp_base': pp,
                    'extension': ri_middle[:-len(pp)],
                    'position': 'prefix'
                }
    return None

# Collect all RI tokens with extensions
print("Analyzing RI extensions...")
ri_data = []

for t in tx.currier_a():
    m = morph.extract(t.word)
    if m and m.middle and m.middle not in b_middles:
        ext_info = get_extension(m.middle)
        ri_data.append({
            'word': t.word,
            'middle': m.middle,
            'folio': t.folio,
            'section': t.section,
            'line': t.line,
            'par_initial': t.par_initial,
            'ext_info': ext_info
        })

print(f"  Total RI tokens: {len(ri_data)}")
has_extension = [r for r in ri_data if r['ext_info'] is not None]
no_extension = [r for r in ri_data if r['ext_info'] is None]
print(f"  With PP base: {len(has_extension)} ({100*len(has_extension)/len(ri_data):.1f}%)")
print(f"  No PP base: {len(no_extension)} ({100*len(no_extension)/len(ri_data):.1f}%)")

# ============================================================
# ANALYSIS 1: Overall Extension Character Frequency
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 1: EXTENSION CHARACTER FREQUENCY")
print("="*70)

# Count single-char vs multi-char extensions
single_char = Counter()
multi_char = Counter()
extension_lengths = []

for r in has_extension:
    ext = r['ext_info']['extension']
    extension_lengths.append(len(ext))
    if len(ext) == 1:
        single_char[ext] += 1
    else:
        multi_char[ext] += 1

print(f"\nExtension length distribution:")
print(f"  1 char: {sum(single_char.values())} ({100*sum(single_char.values())/len(has_extension):.1f}%)")
print(f"  2+ chars: {sum(multi_char.values())} ({100*sum(multi_char.values())/len(has_extension):.1f}%)")
print(f"  Mean length: {np.mean(extension_lengths):.2f}")

print(f"\nSingle-character extensions (top 15):")
for char, count in single_char.most_common(15):
    print(f"  '{char}': {count} ({100*count/sum(single_char.values()):.1f}%)")

print(f"\nMulti-character extensions (top 15):")
for ext, count in multi_char.most_common(15):
    print(f"  '{ext}': {count}")

# ============================================================
# ANALYSIS 2: Extension Position (Prefix vs Suffix)
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 2: EXTENSION POSITION")
print("="*70)

positions = Counter(r['ext_info']['position'] for r in has_extension)
print(f"\nExtension positions:")
for pos, count in positions.most_common():
    print(f"  {pos}: {count} ({100*count/len(has_extension):.1f}%)")

# Check if certain extensions prefer certain positions
ext_by_position = {'prefix': Counter(), 'suffix': Counter()}
for r in has_extension:
    ext = r['ext_info']['extension']
    pos = r['ext_info']['position']
    if len(ext) == 1:
        ext_by_position[pos][ext] += 1

print(f"\nSingle-char extensions by position:")
print(f"{'Char':<6} {'Suffix':<10} {'Prefix':<10} {'Suffix%':<10}")
print("-" * 40)
all_chars = set(ext_by_position['suffix'].keys()) | set(ext_by_position['prefix'].keys())
for char in sorted(all_chars, key=lambda x: -(ext_by_position['suffix'].get(x,0) + ext_by_position['prefix'].get(x,0))):
    suf = ext_by_position['suffix'].get(char, 0)
    pre = ext_by_position['prefix'].get(char, 0)
    total = suf + pre
    if total >= 5:
        print(f"'{char}'    {suf:<10} {pre:<10} {100*suf/total:.0f}%")

# ============================================================
# ANALYSIS 3: Section Preferences
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 3: SECTION PREFERENCES")
print("="*70)

section_extensions = defaultdict(Counter)
section_totals = Counter()

for r in has_extension:
    ext = r['ext_info']['extension']
    section = r['section']
    section_totals[section] += 1
    if len(ext) == 1:
        section_extensions[section][ext] += 1

print(f"\nRI tokens by section:")
for section, count in section_totals.most_common():
    print(f"  Section {section}: {count}")

print(f"\nTop extensions by section:")
for section in ['H', 'P', 'T']:
    if section in section_extensions:
        total = sum(section_extensions[section].values())
        print(f"\n  Section {section} (n={total}):")
        for ext, count in section_extensions[section].most_common(10):
            print(f"    '{ext}': {count} ({100*count/total:.1f}%)")

# Chi-square test: do sections have different extension profiles?
print(f"\nSection preference analysis:")
# Compare H vs P for top extensions
top_exts = ['o', 'd', 'a', 'e', 's', 'c', 'h', 't', 'l']
h_counts = [section_extensions['H'].get(e, 0) for e in top_exts]
p_counts = [section_extensions['P'].get(e, 0) for e in top_exts]

if sum(h_counts) > 0 and sum(p_counts) > 0:
    # Normalize to compare distributions
    h_norm = [c / sum(h_counts) for c in h_counts]
    p_norm = [c / sum(p_counts) for c in p_counts]

    print(f"\n{'Ext':<6} {'H%':<10} {'P%':<10} {'Diff':<10}")
    print("-" * 40)
    for i, ext in enumerate(top_exts):
        diff = p_norm[i] - h_norm[i]
        if h_counts[i] + p_counts[i] >= 5:
            print(f"'{ext}'    {100*h_norm[i]:.1f}%      {100*p_norm[i]:.1f}%      {100*diff:+.1f}%")

# ============================================================
# ANALYSIS 4: Folio-Level Patterns
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 4: FOLIO-LEVEL PATTERNS")
print("="*70)

folio_extensions = defaultdict(Counter)
folio_totals = Counter()

for r in has_extension:
    ext = r['ext_info']['extension']
    folio = r['folio']
    folio_totals[folio] += 1
    if len(ext) == 1:
        folio_extensions[folio][ext] += 1

# Find folios dominated by specific extensions
print(f"\nFolios with dominant extensions (>40% single extension):")
dominant_folios = []
for folio, exts in folio_extensions.items():
    total = sum(exts.values())
    if total >= 10:
        for ext, count in exts.most_common(1):
            if count / total > 0.4:
                dominant_folios.append((folio, ext, count, total, count/total))

for folio, ext, count, total, pct in sorted(dominant_folios, key=lambda x: -x[4])[:15]:
    print(f"  {folio}: '{ext}' = {count}/{total} ({100*pct:.0f}%)")

# ============================================================
# ANALYSIS 5: PP Base Patterns
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 5: PP BASE PATTERNS")
print("="*70)

# Which PP bases are most commonly extended?
pp_base_counts = Counter()
pp_base_extensions = defaultdict(Counter)

for r in has_extension:
    pp = r['ext_info']['pp_base']
    ext = r['ext_info']['extension']
    pp_base_counts[pp] += 1
    pp_base_extensions[pp][ext] += 1

print(f"\nMost commonly extended PP bases:")
for pp, count in pp_base_counts.most_common(20):
    num_exts = len(pp_base_extensions[pp])
    top_ext = pp_base_extensions[pp].most_common(1)[0][0]
    print(f"  '{pp}': {count} tokens, {num_exts} different extensions, top='{top_ext}'")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

summary = {
    'total_ri_tokens': len(ri_data),
    'with_pp_base': len(has_extension),
    'containment_rate': len(has_extension) / len(ri_data),
    'single_char_extensions': sum(single_char.values()),
    'multi_char_extensions': sum(multi_char.values()),
    'mean_extension_length': float(np.mean(extension_lengths)),
    'position_distribution': dict(positions),
    'top_single_char_extensions': dict(single_char.most_common(10)),
    'section_totals': dict(section_totals),
    'dominant_folios': [(f, e, c, t) for f, e, c, t, p in dominant_folios[:10]]
}

print(f"""
Key findings:
- Containment rate: {100*summary['containment_rate']:.1f}%
- Single-char extensions: {100*summary['single_char_extensions']/len(has_extension):.1f}%
- Position: {100*positions.get('suffix',0)/len(has_extension):.0f}% suffix, {100*positions.get('prefix',0)/len(has_extension):.0f}% prefix
- Mean extension length: {summary['mean_extension_length']:.2f} chars
- Top extensions: {', '.join(f"'{e}'" for e, c in single_char.most_common(5))}
""")

# Save results
with open('C:/git/voynich/phases/RI_EXTENSION_MAPPING/results/extension_distribution.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("Results saved to extension_distribution.json")
