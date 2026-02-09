#!/usr/bin/env python3
"""
Test if REGIME assignments predict folio specialization.

Question: Do certain REGIMEs concentrate recovery vs distillation folios?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

# Load REGIME assignments
regime_path = Path(__file__).parent.parent / 'results' / 'regime_folio_mapping.json'
with open(regime_path) as f:
    regime_data = json.load(f)

# Build folio_to_regime from regime -> [folios] structure
folio_to_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_to_regime[folio] = regime

# From spatial analysis
RECOVERY_FOLIOS = {'f39v', 'f40r', 'f94r', 'f107v', 'f50r', 'f50v'}
DISTILL_FOLIOS = {'f34v', 'f43r', 'f46r', 'f46v', 'f57r', 'f106v', 'f95v1', 'f39r', 'f94v', 'f115v'}

# Load class map for section info
class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = {t: int(c) for t, c in class_data['token_to_class'].items()}

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

# Build paragraph data for all folios
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

# Build folio paragraph profiles
folio_profiles = {}

for folio in folio_line_tokens:
    paras = get_paragraphs(folio)
    types = []
    for p in paras:
        words = [t.word for line_num, tokens in p for t in tokens]
        ptype = classify_paragraph(words)
        if ptype:
            types.append(ptype)

    if len(types) >= 2:
        k_count = types.count('HIGH_K')
        h_count = types.count('HIGH_H')
        total = len(types)

        if k_count / total >= 0.5:
            spec = 'RECOVERY'
        elif h_count / total >= 0.7:
            spec = 'DISTILL'
        else:
            spec = 'MIXED'

        folio_profiles[folio] = {
            'k_count': k_count,
            'h_count': h_count,
            'total': total,
            'specialization': spec,
            'regime': folio_to_regime.get(folio, 'UNKNOWN'),
            'section': folio_section.get(folio, 'UNKNOWN')
        }

print("="*70)
print("REGIME vs FOLIO SPECIALIZATION")
print("="*70)

# Count specializations by REGIME
regime_specs = defaultdict(lambda: Counter())

for folio, profile in folio_profiles.items():
    regime = profile['regime']
    spec = profile['specialization']
    regime_specs[regime][spec] += 1

print(f"\n{'REGIME':<15} {'RECOVERY':<12} {'DISTILL':<12} {'MIXED':<12} {'Total':<10}")
print("-"*60)

for regime in sorted(regime_specs.keys()):
    counts = regime_specs[regime]
    total = sum(counts.values())
    r = counts.get('RECOVERY', 0)
    d = counts.get('DISTILL', 0)
    m = counts.get('MIXED', 0)
    print(f"{regime:<15} {r:<12} {d:<12} {m:<12} {total:<10}")

# Chi-square test: REGIME vs SPECIALIZATION
print(f"\n{'='*70}")
print("STATISTICAL TEST: REGIME PREDICTS SPECIALIZATION?")
print("="*70)

# Build contingency table (REGIME x SPECIALIZATION)
regimes = sorted(set(p['regime'] for p in folio_profiles.values() if p['regime'] != 'UNKNOWN'))
specs = ['RECOVERY', 'DISTILL', 'MIXED']

contingency = []
for regime in regimes:
    row = [regime_specs[regime].get(s, 0) for s in specs]
    contingency.append(row)

contingency = np.array(contingency)
print(f"\nContingency table ({len(regimes)} regimes x 3 specializations):")
print(contingency)

if contingency.shape[0] >= 2 and contingency.shape[1] >= 2:
    chi2, p_val, dof, expected = scipy_stats.chi2_contingency(contingency)
    print(f"\nChi-square = {chi2:.2f}, df = {dof}, p = {p_val:.4f}")

    if p_val < 0.05:
        print("-> *Significant: REGIME predicts folio specialization")
    else:
        print("-> Not significant: Specialization is independent of REGIME")

# Detailed breakdown: which REGIMEs have most recovery?
print(f"\n{'='*70}")
print("RECOVERY-RICH REGIMEs")
print("="*70)

regime_recovery_rate = []
for regime in regimes:
    counts = regime_specs[regime]
    total = sum(counts.values())
    if total >= 3:
        r_rate = counts.get('RECOVERY', 0) / total
        regime_recovery_rate.append((regime, r_rate, counts.get('RECOVERY', 0), total))

regime_recovery_rate.sort(key=lambda x: -x[1])

print(f"\n{'REGIME':<15} {'Recovery Rate':<15} {'R/Total':<15}")
print("-"*45)
for regime, rate, r, total in regime_recovery_rate:
    print(f"{regime:<15} {100*rate:<15.1f} {r}/{total}")

# Per-REGIME paragraph type breakdown
print(f"\n{'='*70}")
print("PARAGRAPH TYPE DISTRIBUTION BY REGIME")
print("="*70)

# Aggregate paragraph types by REGIME
regime_para_types = defaultdict(lambda: Counter())

for folio in folio_line_tokens:
    regime = folio_to_regime.get(folio, 'UNKNOWN')
    paras = get_paragraphs(folio)
    for p in paras:
        words = [t.word for line_num, tokens in p for t in tokens]
        ptype = classify_paragraph(words)
        if ptype:
            regime_para_types[regime][ptype] += 1

print(f"\n{'REGIME':<15} {'HIGH_K':<10} {'HIGH_H':<10} {'OTHER':<10} {'K/(K+H)':<12}")
print("-"*55)

for regime in sorted(regime_para_types.keys()):
    counts = regime_para_types[regime]
    k = counts.get('HIGH_K', 0)
    h = counts.get('HIGH_H', 0)
    o = counts.get('OTHER', 0)
    ratio = k / (k + h) if (k + h) > 0 else 0
    print(f"{regime:<15} {k:<10} {h:<10} {o:<10} {ratio:<12.2f}")

# Save results
output = {
    'regime_specializations': {r: dict(c) for r, c in regime_specs.items()},
    'regime_para_types': {r: dict(c) for r, c in regime_para_types.items()},
    'folio_profiles': folio_profiles
}

output_path = Path(__file__).parent.parent / 'results' / 'regime_specialization.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
