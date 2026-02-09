#!/usr/bin/env python3
"""
Test if REGIME_4's recovery concentration is section-confounded.

Expert question: Could this be driven by section composition
(BIO in REGIME_1, PHARMA in REGIME_4)?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

# Load REGIME assignments
regime_path = Path(__file__).parent.parent / 'results' / 'regime_folio_mapping.json'
with open(regime_path) as f:
    regime_data = json.load(f)

folio_to_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_to_regime[folio] = regime

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

# Build folio-section mapping
folio_section = {}
folio_line_tokens = defaultdict(lambda: defaultdict(list))

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_line_tokens[token.folio][token.line].append(token)
    if token.folio not in folio_section:
        folio_section[token.folio] = token.section

def get_paragraphs(folio):
    lines = folio_line_tokens[folio]
    paragraphs = []
    current_para = []
    for line_num in sorted(lines.keys()):
        tokens = lines[line_num]
        if not tokens:
            continue
        first_word = tokens[0].word
        if first_word and first_word[0] in GALLOWS:
            if current_para:
                paragraphs.append(current_para)
            current_para = [(line_num, tokens)]
        else:
            current_para.append((line_num, tokens))
    if current_para:
        paragraphs.append(current_para)
    return paragraphs

def classify_paragraph(words):
    if len(words) < 10:
        return None
    k = sum(w.count('k') for w in words)
    h = sum(w.count('h') for w in words)
    e = sum(w.count('e') for w in words)
    total_kernel = k + h + e
    if total_kernel < 10:
        return None
    k_pct = 100 * k / total_kernel
    h_pct = 100 * h / total_kernel
    if k_pct > 35:
        return 'HIGH_K'
    elif h_pct > 35:
        return 'HIGH_H'
    else:
        return 'OTHER'

print("="*70)
print("SECTION-REGIME CONFOUNDING TEST")
print("="*70)

# 1. Section composition by REGIME
print("\n1. SECTION COMPOSITION BY REGIME")
print("-"*50)

regime_sections = defaultdict(Counter)

for folio in folio_section:
    regime = folio_to_regime.get(folio, 'UNKNOWN')
    section = folio_section[folio]
    regime_sections[regime][section] += 1

for regime in sorted(regime_sections.keys()):
    print(f"\n{regime}:")
    for section, count in regime_sections[regime].most_common():
        print(f"  {section}: {count} folios")

# 2. K/(K+H) by section WITHIN each REGIME
print("\n" + "="*70)
print("2. K/(K+H) BY SECTION WITHIN EACH REGIME")
print("="*70)

# Collect paragraph types by (REGIME, section)
regime_section_types = defaultdict(lambda: defaultdict(Counter))

for folio in folio_line_tokens:
    regime = folio_to_regime.get(folio, 'UNKNOWN')
    section = folio_section.get(folio, 'UNKNOWN')

    paras = get_paragraphs(folio)
    for p in paras:
        words = [t.word for line_num, tokens in p for t in tokens]
        ptype = classify_paragraph(words)
        if ptype:
            regime_section_types[regime][section][ptype] += 1

print(f"\n{'REGIME':<12} {'Section':<10} {'HIGH_K':<8} {'HIGH_H':<8} {'K/(K+H)':<10}")
print("-"*55)

for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    for section in sorted(regime_section_types[regime].keys()):
        counts = regime_section_types[regime][section]
        k = counts.get('HIGH_K', 0)
        h = counts.get('HIGH_H', 0)
        ratio = k / (k + h) if (k + h) > 0 else 0
        print(f"{regime:<12} {section:<10} {k:<8} {h:<8} {ratio:<10.2f}")

# 3. Control for section: Compare same section across REGIMEs
print("\n" + "="*70)
print("3. SAME SECTION ACROSS REGIMES (Controlling for Section)")
print("="*70)

# Find sections that appear in multiple REGIMEs
section_regimes = defaultdict(set)
for folio in folio_section:
    regime = folio_to_regime.get(folio, 'UNKNOWN')
    section = folio_section[folio]
    section_regimes[section].add(regime)

multi_regime_sections = {s: regs for s, regs in section_regimes.items()
                         if len(regs) > 1 and 'UNKNOWN' not in regs}

print(f"\nSections appearing in multiple REGIMEs: {list(multi_regime_sections.keys())}")

for section in sorted(multi_regime_sections.keys()):
    print(f"\n{section} across REGIMEs:")
    for regime in sorted(multi_regime_sections[section]):
        counts = regime_section_types[regime][section]
        k = counts.get('HIGH_K', 0)
        h = counts.get('HIGH_H', 0)
        if (k + h) > 0:
            ratio = k / (k + h)
            print(f"  {regime}: K/(K+H) = {ratio:.2f} (K={k}, H={h})")

# 4. Key test: Within section H (largest cross-REGIME section)
print("\n" + "="*70)
print("4. WITHIN SECTION H: REGIME EFFECT ON K/(K+H)")
print("="*70)

# Section H appears in which REGIMEs?
h_regimes = section_regimes.get('H', set())
print(f"\nSection H appears in: {sorted(h_regimes)}")

for regime in sorted(h_regimes):
    if regime == 'UNKNOWN':
        continue
    counts = regime_section_types[regime]['H']
    k = counts.get('HIGH_K', 0)
    h = counts.get('HIGH_H', 0)
    other = counts.get('OTHER', 0)
    total = k + h + other
    ratio = k / (k + h) if (k + h) > 0 else 0
    print(f"  {regime}: K/(K+H) = {ratio:.2f} (K={k}, H={h}, Other={other})")

print("""
INTERPRETATION:
---------------
If K/(K+H) varies by REGIME within the same section, then REGIME has
an independent effect beyond section composition.

If K/(K+H) is constant across REGIMEs within a section, then the
REGIME effect is entirely explained by section composition.
""")
