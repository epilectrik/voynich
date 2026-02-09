#!/usr/bin/env python3
"""
Test if kernel signatures can discriminate thermal process types.

Hypothesis:
- HIGH_H = Distillation (phase transitions, drip monitoring)
- HIGH_K with LOW h = Boiling/Decoction (fire control without phase monitoring)
- HIGH_E = Extraction/Filtration (emphasis on equilibration, passive)

Key insight: 'h' is PHASE_MANAGER (drip timing). Distillation REQUIRES phase
transitions (liquid->vapor->liquid). Simple boiling does NOT require phase
monitoring - you just heat until done.
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

# Load class map
class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = {t: int(c) for t, c in class_data['token_to_class'].items()}
token_to_role = class_data.get('token_to_role', {})

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

# Collect all paragraphs with detailed kernel analysis
all_paragraphs = []

for folio in folio_line_tokens:
    paras = get_paragraphs(folio)
    for i, p in enumerate(paras):
        words = []
        for line_num, tokens in p:
            words.extend([t.word for t in tokens])

        if len(words) < 10:
            continue

        # Kernel character counts
        k = sum(w.count('k') for w in words)
        h = sum(w.count('h') for w in words)
        e = sum(w.count('e') for w in words)
        total_kernel = k + h + e

        if total_kernel < 10:
            continue

        k_pct = 100 * k / total_kernel
        h_pct = 100 * h / total_kernel
        e_pct = 100 * e / total_kernel

        # More granular classification
        # Original: HIGH_K (k>35%), HIGH_H (h>35%), HIGH_E (e>60%), BALANCED
        # New: Add k-dominant-low-h category

        if k_pct > 35 and h_pct < 20:
            process_type = 'HIGH_K_LOW_H'  # Possible boiling
        elif k_pct > 35:
            process_type = 'HIGH_K_MED_H'  # k-dominant but has h
        elif h_pct > 35:
            process_type = 'HIGH_H'  # Distillation
        elif e_pct > 60:
            process_type = 'HIGH_E'  # Cooling/equilibration
        else:
            process_type = 'BALANCED'

        # Role distribution
        n_tokens = len(words)
        en_count = sum(1 for w in words if token_to_role.get(w) == 'ENERGY_OPERATOR')
        fq_count = sum(1 for w in words if token_to_role.get(w) == 'FREQUENT_OPERATOR')
        flow_count = sum(1 for w in words if token_to_role.get(w) == 'FLOW_OPERATOR')
        link_count = sum(1 for w in words if token_to_class.get(w) == 29)

        all_paragraphs.append({
            'folio': folio,
            'section': folio_section.get(folio, 'UNKNOWN'),
            'para_idx': i,
            'process_type': process_type,
            'k_pct': k_pct,
            'h_pct': h_pct,
            'e_pct': e_pct,
            'n_tokens': n_tokens,
            'en_rate': en_count / n_tokens,
            'fq_rate': fq_count / n_tokens,
            'flow_rate': flow_count / n_tokens,
            'link_rate': link_count / n_tokens,
        })

print("="*70)
print("THERMAL PROCESS TYPE DISCRIMINATION")
print("="*70)

print(f"\nTotal paragraphs analyzed: {len(all_paragraphs)}")

# Group by process type
by_type = defaultdict(list)
for p in all_paragraphs:
    by_type[p['process_type']].append(p)

print(f"\nProcess type distribution:")
for ptype in ['HIGH_K_LOW_H', 'HIGH_K_MED_H', 'HIGH_H', 'HIGH_E', 'BALANCED']:
    count = len(by_type.get(ptype, []))
    print(f"  {ptype:<15}: {count:>5} paragraphs")

# ============================================================
# KEY TEST: Do HIGH_K_LOW_H paragraphs exist and differ?
# ============================================================
print(f"\n{'='*70}")
print("KEY TEST: HIGH_K_LOW_H vs HIGH_H")
print("="*70)

print("""
Hypothesis:
- HIGH_K_LOW_H = Fire control WITHOUT phase monitoring = BOILING/DECOCTION
- HIGH_H = Phase monitoring = DISTILLATION

If these are different processes:
1. HIGH_K_LOW_H should have different role profiles
2. They might concentrate in different sections/folios
""")

if 'HIGH_K_LOW_H' in by_type and len(by_type['HIGH_K_LOW_H']) > 5:
    low_h = by_type['HIGH_K_LOW_H']
    high_h = by_type['HIGH_H']

    print(f"\n{'Metric':<20} {'HIGH_K_LOW_H':<15} {'HIGH_H':<15} {'Difference':<15}")
    print("-"*65)

    # Kernel profiles
    print(f"{'k%':<20} {np.mean([p['k_pct'] for p in low_h]):<15.1f} {np.mean([p['k_pct'] for p in high_h]):<15.1f}")
    print(f"{'h%':<20} {np.mean([p['h_pct'] for p in low_h]):<15.1f} {np.mean([p['h_pct'] for p in high_h]):<15.1f}")
    print(f"{'e%':<20} {np.mean([p['e_pct'] for p in low_h]):<15.1f} {np.mean([p['e_pct'] for p in high_h]):<15.1f}")

    # Role profiles
    print(f"\n{'Role profiles:':<20}")
    print(f"{'EN rate':<20} {100*np.mean([p['en_rate'] for p in low_h]):<15.1f} {100*np.mean([p['en_rate'] for p in high_h]):<15.1f}")
    print(f"{'FQ rate':<20} {100*np.mean([p['fq_rate'] for p in low_h]):<15.1f} {100*np.mean([p['fq_rate'] for p in high_h]):<15.1f}")
    print(f"{'FLOW rate':<20} {100*np.mean([p['flow_rate'] for p in low_h]):<15.1f} {100*np.mean([p['flow_rate'] for p in high_h]):<15.1f}")
    print(f"{'LINK rate':<20} {100*np.mean([p['link_rate'] for p in low_h]):<15.1f} {100*np.mean([p['link_rate'] for p in high_h]):<15.1f}")

    # Statistical tests
    print(f"\n{'Statistical tests:':<20}")

    # EN rate
    u_stat, p_val = scipy_stats.mannwhitneyu(
        [p['en_rate'] for p in low_h],
        [p['en_rate'] for p in high_h],
        alternative='two-sided'
    )
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
    print(f"  EN rate: p = {p_val:.4f} {sig}")

    # FQ rate
    u_stat, p_val = scipy_stats.mannwhitneyu(
        [p['fq_rate'] for p in low_h],
        [p['fq_rate'] for p in high_h],
        alternative='two-sided'
    )
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
    print(f"  FQ rate: p = {p_val:.4f} {sig}")

    # LINK rate
    u_stat, p_val = scipy_stats.mannwhitneyu(
        [p['link_rate'] for p in low_h],
        [p['link_rate'] for p in high_h],
        alternative='two-sided'
    )
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
    print(f"  LINK rate: p = {p_val:.4f} {sig}")

# ============================================================
# SECTION DISTRIBUTION
# ============================================================
print(f"\n{'='*70}")
print("PROCESS TYPE BY SECTION")
print("="*70)

section_types = defaultdict(Counter)
for p in all_paragraphs:
    section_types[p['section']][p['process_type']] += 1

print(f"\n{'Section':<10} {'HIGH_K_LOW_H':<12} {'HIGH_K_MED_H':<12} {'HIGH_H':<10} {'HIGH_E':<10} {'BALANCED':<10}")
print("-"*70)

for section in sorted(section_types.keys()):
    counts = section_types[section]
    row = f"{section:<10}"
    for ptype in ['HIGH_K_LOW_H', 'HIGH_K_MED_H', 'HIGH_H', 'HIGH_E', 'BALANCED']:
        row += f" {counts.get(ptype, 0):<11}"
    print(row)

# ============================================================
# HIGH_E ANALYSIS (Possible extraction/filtration)
# ============================================================
print(f"\n{'='*70}")
print("HIGH_E ANALYSIS (e>60%)")
print("="*70)

if 'HIGH_E' in by_type and len(by_type['HIGH_E']) > 5:
    high_e = by_type['HIGH_E']

    print(f"\nHIGH_E paragraphs: {len(high_e)}")
    print(f"\nKernel profile:")
    print(f"  k%: {np.mean([p['k_pct'] for p in high_e]):.1f}")
    print(f"  h%: {np.mean([p['h_pct'] for p in high_e]):.1f}")
    print(f"  e%: {np.mean([p['e_pct'] for p in high_e]):.1f}")

    print(f"\nRole profile:")
    print(f"  EN rate: {100*np.mean([p['en_rate'] for p in high_e]):.1f}%")
    print(f"  FQ rate: {100*np.mean([p['fq_rate'] for p in high_e]):.1f}%")

    # Compare to HIGH_H
    high_h = by_type['HIGH_H']

    print(f"\n{'Comparison: HIGH_E vs HIGH_H:':<40}")
    u_stat, p_val = scipy_stats.mannwhitneyu(
        [p['en_rate'] for p in high_e],
        [p['en_rate'] for p in high_h],
        alternative='two-sided'
    )
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
    print(f"  EN rate: HIGH_E={100*np.mean([p['en_rate'] for p in high_e]):.1f}% vs HIGH_H={100*np.mean([p['en_rate'] for p in high_h]):.1f}% (p={p_val:.4f}) {sig}")

    # Section distribution
    print(f"\n{'HIGH_E by section:':<40}")
    high_e_sections = Counter(p['section'] for p in high_e)
    for section, count in high_e_sections.most_common():
        print(f"  {section}: {count} paragraphs")

# ============================================================
# INTERPRETATION
# ============================================================
print(f"\n{'='*70}")
print("INTERPRETATION")
print("="*70)

print("""
PROCESS TYPE HYPOTHESIS:

If the Voynich encodes MULTIPLE thermal processes (not just distillation):

1. HIGH_H (h>35%) = DISTILLATION
   - Requires phase monitoring (vapor->liquid)
   - Uses drip timing (PHASE_MANAGER)
   - Should have higher LINK (monitoring)

2. HIGH_K_LOW_H (k>35%, h<20%) = BOILING/DECOCTION
   - Fire control without phase transitions
   - No drip timing needed
   - Should have higher FQ (error correction during heating)

3. HIGH_E (e>60%) = EXTRACTION/FILTRATION
   - Emphasis on equilibration
   - Minimal fire operations
   - Possible passive processes (steeping, straining)

BRUNSCHWIG ALIGNMENT:
- 10 methods: 5 with fire, 5 without
- "Filtration" is explicitly listed as a method
- Balneum marie vs direct fire have different monitoring needs
""")

# Save results
output = {
    'n_paragraphs': len(all_paragraphs),
    'by_type_count': {t: len(pp) for t, pp in by_type.items()},
    'section_distribution': {s: dict(c) for s, c in section_types.items()},
}

for ptype in ['HIGH_K_LOW_H', 'HIGH_H', 'HIGH_E', 'BALANCED']:
    if ptype in by_type and len(by_type[ptype]) > 0:
        pp = by_type[ptype]
        output[f'{ptype}_profile'] = {
            'k_pct': float(np.mean([p['k_pct'] for p in pp])),
            'h_pct': float(np.mean([p['h_pct'] for p in pp])),
            'e_pct': float(np.mean([p['e_pct'] for p in pp])),
            'en_rate': float(np.mean([p['en_rate'] for p in pp])),
            'fq_rate': float(np.mean([p['fq_rate'] for p in pp])),
        }

output_path = Path(__file__).parent.parent / 'results' / 'process_type_discrimination.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
