#!/usr/bin/env python3
"""
Spatial analysis of paragraph kernel types across folios and sections.

Building on C893 (Paragraph Kernel Signature Predicts Operation Type):
- HIGH_K = Recovery procedures
- HIGH_H = Active distillation
- BALANCED = General procedures

Questions:
1. Do certain folios/sections concentrate certain paragraph types?
2. Is there a sequence pattern within folios (e.g., recovery before distillation)?
3. Do REGIME assignments predict paragraph type distribution?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

# Load class map for section info
class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = {t: int(c) for t, c in class_data['token_to_class'].items()}

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

# Build paragraph data
folio_line_tokens = defaultdict(lambda: defaultdict(list))
folio_section = {}

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
    """Classify paragraph by kernel signature."""
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
    e_pct = 100 * e / total_kernel

    if k_pct > 35:
        return 'HIGH_K'
    elif h_pct > 35:
        return 'HIGH_H'
    elif e_pct > 60:
        return 'HIGH_E'
    else:
        return 'BALANCED'

# Collect all paragraphs with classification
all_paragraphs = []

for folio in folio_line_tokens:
    paras = get_paragraphs(folio)
    for i, p in enumerate(paras):
        words = []
        for line_num, tokens in p:
            words.extend([t.word for t in tokens])

        ptype = classify_paragraph(words)
        if ptype is None:
            continue

        all_paragraphs.append({
            'folio': folio,
            'section': folio_section.get(folio, 'UNKNOWN'),
            'para_idx': i,
            'n_paras': len(paras),
            'ptype': ptype,
            'n_tokens': len(words)
        })

print("="*70)
print("PARAGRAPH TYPE SPATIAL ANALYSIS")
print("="*70)

print(f"\nTotal paragraphs analyzed: {len(all_paragraphs)}")

# 1. Distribution by section
print(f"\n{'='*70}")
print("PARAGRAPH TYPES BY SECTION")
print("="*70)

section_types = defaultdict(lambda: Counter())
for p in all_paragraphs:
    section_types[p['section']][p['ptype']] += 1

print(f"\n{'Section':<15} {'HIGH_K':<10} {'HIGH_H':<10} {'BALANCED':<10} {'HIGH_E':<10} {'Total':<10} {'K/(K+H)':<10}")
print("-"*75)

for section in sorted(section_types.keys()):
    counts = section_types[section]
    total = sum(counts.values())
    k_count = counts.get('HIGH_K', 0)
    h_count = counts.get('HIGH_H', 0)
    bal = counts.get('BALANCED', 0)
    e_count = counts.get('HIGH_E', 0)
    ratio = k_count / (k_count + h_count) if (k_count + h_count) > 0 else 0
    print(f"{section:<15} {k_count:<10} {h_count:<10} {bal:<10} {e_count:<10} {total:<10} {ratio:<10.2f}")

# 2. Do certain folios specialize?
print(f"\n{'='*70}")
print("FOLIO SPECIALIZATION")
print("="*70)

folio_types = defaultdict(lambda: Counter())
for p in all_paragraphs:
    folio_types[p['folio']][p['ptype']] += 1

# Find folios with strong specialization
specialized_k = []
specialized_h = []
mixed = []

for folio, counts in folio_types.items():
    total = sum(counts.values())
    if total < 3:
        continue
    k_pct = 100 * counts.get('HIGH_K', 0) / total
    h_pct = 100 * counts.get('HIGH_H', 0) / total

    if k_pct >= 50:
        specialized_k.append((folio, k_pct, total))
    elif h_pct >= 70:
        specialized_h.append((folio, h_pct, total))
    else:
        mixed.append((folio, k_pct, h_pct, total))

print(f"\nHIGH_K specialized folios (>=50% HIGH_K):")
for folio, pct, n in sorted(specialized_k, key=lambda x: -x[1])[:10]:
    sec = folio_section.get(folio, '?')
    print(f"  {folio} ({sec}): {pct:.0f}% HIGH_K ({n} paragraphs)")

print(f"\nHIGH_H specialized folios (>=70% HIGH_H):")
for folio, pct, n in sorted(specialized_h, key=lambda x: -x[1])[:10]:
    sec = folio_section.get(folio, '?')
    print(f"  {folio} ({sec}): {pct:.0f}% HIGH_H ({n} paragraphs)")

# 3. Sequence analysis within folios
print(f"\n{'='*70}")
print("WITHIN-FOLIO SEQUENCE ANALYSIS")
print("="*70)

# For each folio, check if there's a K-first or H-first pattern
sequence_patterns = []

for folio in folio_types:
    paras_in_folio = [p for p in all_paragraphs if p['folio'] == folio]
    if len(paras_in_folio) < 2:
        continue

    # Sort by paragraph index
    paras_in_folio.sort(key=lambda x: x['para_idx'])

    types_seq = [p['ptype'] for p in paras_in_folio]

    # Find position of first HIGH_K and first HIGH_H
    k_pos = next((i for i, t in enumerate(types_seq) if t == 'HIGH_K'), None)
    h_pos = next((i for i, t in enumerate(types_seq) if t == 'HIGH_H'), None)

    if k_pos is not None and h_pos is not None:
        if k_pos < h_pos:
            sequence_patterns.append('K_FIRST')
        elif h_pos < k_pos:
            sequence_patterns.append('H_FIRST')
        else:
            sequence_patterns.append('SAME')

seq_counts = Counter(sequence_patterns)
total_seq = len(sequence_patterns)
print(f"\nFirst occurrence order (folios with both HIGH_K and HIGH_H):")
print(f"  K appears first: {seq_counts.get('K_FIRST', 0)} ({100*seq_counts.get('K_FIRST', 0)/total_seq:.1f}%)")
print(f"  H appears first: {seq_counts.get('H_FIRST', 0)} ({100*seq_counts.get('H_FIRST', 0)/total_seq:.1f}%)")

# Binomial test
if total_seq > 0:
    k_first = seq_counts.get('K_FIRST', 0)
    result = scipy_stats.binomtest(k_first, total_seq, 0.5, alternative='two-sided')
    p_val = result.pvalue
    print(f"\n  Binomial test (null = 50/50): p = {p_val:.4f}")
    if p_val < 0.05:
        print("  -> Significant sequence preference!")
    else:
        print("  -> No significant sequence preference (random ordering)")

# 4. Does paragraph position predict type?
print(f"\n{'='*70}")
print("PARAGRAPH POSITION VS TYPE")
print("="*70)

# Normalized position: 0 = first paragraph, 1 = last paragraph
position_by_type = defaultdict(list)

for p in all_paragraphs:
    if p['n_paras'] > 1:
        norm_pos = p['para_idx'] / (p['n_paras'] - 1)
        position_by_type[p['ptype']].append(norm_pos)

print(f"\n{'Type':<15} {'Mean Position':<15} {'Std':<10} {'N':<10}")
print("-"*50)

for ptype in ['HIGH_K', 'HIGH_H', 'BALANCED', 'HIGH_E']:
    if ptype in position_by_type and len(position_by_type[ptype]) > 5:
        positions = position_by_type[ptype]
        mean_pos = np.mean(positions)
        std_pos = np.std(positions)
        print(f"{ptype:<15} {mean_pos:<15.3f} {std_pos:<10.3f} {len(positions):<10}")

# Mann-Whitney: HIGH_K vs HIGH_H position
if 'HIGH_K' in position_by_type and 'HIGH_H' in position_by_type:
    k_pos = position_by_type['HIGH_K']
    h_pos = position_by_type['HIGH_H']
    if len(k_pos) > 5 and len(h_pos) > 5:
        u_stat, p_val = scipy_stats.mannwhitneyu(k_pos, h_pos, alternative='two-sided')
        print(f"\nMann-Whitney HIGH_K vs HIGH_H position: U={u_stat:.0f}, p={p_val:.4f}")
        if p_val < 0.05:
            if np.mean(k_pos) < np.mean(h_pos):
                print("  -> HIGH_K tends to appear EARLIER in folios!")
            else:
                print("  -> HIGH_H tends to appear EARLIER in folios!")
        else:
            print("  -> No significant positional preference")

# 5. Section-specific patterns
print(f"\n{'='*70}")
print("SECTION-SPECIFIC SEQUENCE ANALYSIS")
print("="*70)

for section in sorted(section_types.keys()):
    section_paras = [p for p in all_paragraphs if p['section'] == section]

    # Group by folio
    folio_paras = defaultdict(list)
    for p in section_paras:
        folio_paras[p['folio']].append(p)

    # Analyze position by type
    k_positions = []
    h_positions = []

    for folio, paras in folio_paras.items():
        if len(paras) < 2:
            continue
        paras.sort(key=lambda x: x['para_idx'])
        for i, p in enumerate(paras):
            norm_pos = i / (len(paras) - 1)
            if p['ptype'] == 'HIGH_K':
                k_positions.append(norm_pos)
            elif p['ptype'] == 'HIGH_H':
                h_positions.append(norm_pos)

    if len(k_positions) > 3 and len(h_positions) > 3:
        k_mean = np.mean(k_positions)
        h_mean = np.mean(h_positions)
        u_stat, p_val = scipy_stats.mannwhitneyu(k_positions, h_positions, alternative='two-sided')
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""

        print(f"\n{section}:")
        print(f"  HIGH_K mean pos: {k_mean:.3f} (n={len(k_positions)})")
        print(f"  HIGH_H mean pos: {h_mean:.3f} (n={len(h_positions)})")
        print(f"  Mann-Whitney p={p_val:.4f} {sig}")

# 6. Summary interpretation
print(f"\n{'='*70}")
print("SUMMARY AND INTERPRETATION")
print("="*70)

print("""
FINDINGS:

1. SECTION DISTRIBUTION:
   - Do certain sections concentrate recovery (HIGH_K) or distillation (HIGH_H)?

2. FOLIO SPECIALIZATION:
   - Some folios may be dedicated recovery procedures
   - Others may be dedicated distillation procedures

3. SEQUENCE PATTERNS:
   - If K appears before H: Recovery-then-process workflow
   - If H appears before K: Process-with-recovery-fallback
   - If random: Independent procedure selection

4. POSITIONAL PATTERNS:
   - If HIGH_K earlier: Recovery is preparatory
   - If HIGH_H earlier: Distillation is primary

BRUNSCHWIG ALIGNMENT:
   - Recovery (HIGH_K) as safety-first would appear early
   - Active distillation (HIGH_H) as main process in middle
   - General (BALANCED) for standard operations throughout
""")

# Save results
output = {
    'n_paragraphs': len(all_paragraphs),
    'section_distribution': {s: dict(c) for s, c in section_types.items()},
    'specialized_k_folios': [f[0] for f in specialized_k],
    'specialized_h_folios': [f[0] for f in specialized_h],
    'sequence_pattern': dict(seq_counts),
    'position_by_type': {t: {'mean': float(np.mean(p)), 'std': float(np.std(p)), 'n': len(p)}
                         for t, p in position_by_type.items() if len(p) > 0}
}

output_path = Path(__file__).parent.parent / 'results' / 'paragraph_type_spatial.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
