#!/usr/bin/env python3
"""
Test 3: PREFIX Profile Correlation

Question: Do Brunschwig instruction types correlate with B PREFIX profiles?

Method:
1. Compute instruction type proportions for each Brunschwig recipe
2. Compute PREFIX proportions for B folios in matching REGIME
3. Pearson correlation between instruction types and prefixes

Expected if H1 TRUE:
- AUX correlates with ok/ot
- FLOW correlates with da
- e_ESCAPE correlates with qo
- k_ENERGY correlates with ch/sh

Falsification:
- H1 FALSE if: all correlations |r| < 0.2
- H1 SUPPORTED if: 3+ correlations r > 0.3
"""

import json
import sys
from pathlib import Path
from collections import Counter
import pandas as pd
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

# =============================================================================
# Load Data
# =============================================================================

print("=" * 70)
print("TEST 3: PREFIX PROFILE CORRELATION")
print("=" * 70)
print()

# Load Brunschwig recipes
with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

recipes = data['recipes']
print(f"Loaded {len(recipes)} Brunschwig recipes")

# Load REGIME mapping
with open(PROJECT_ROOT / 'results' / 'regime_folio_mapping.json', 'r', encoding='utf-8') as f:
    regime_data = json.load(f)

# Load transcript
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_b = df[df['language'] == 'B'].copy()
print(f"Loaded {len(df_b)} Currier B tokens")
print()

# =============================================================================
# Compute Instruction Type Proportions per REGIME
# =============================================================================

# Map fire_degree to REGIME
regime_map = {1: 'REGIME_1', 2: 'REGIME_2', 3: 'REGIME_3', 4: 'REGIME_4'}

# Aggregate instruction types per REGIME
regime_instruction_profiles = {f'REGIME_{i}': Counter() for i in range(1, 5)}

for recipe in recipes:
    fire_degree = recipe.get('fire_degree', 0)
    seq = recipe.get('instruction_sequence') or []
    regime = regime_map.get(fire_degree)

    if regime and seq:
        regime_instruction_profiles[regime].update(seq)

print("BRUNSCHWIG INSTRUCTION PROFILES BY REGIME")
print("-" * 70)

instruction_types = ['AUX', 'FLOW', 'h_HAZARD', 'LINK', 'k_ENERGY', 'e_ESCAPE']

# Compute proportions
regime_instruction_proportions = {}
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    counts = regime_instruction_profiles[regime]
    total = sum(counts.values())
    if total > 0:
        props = {t: counts.get(t, 0) / total for t in instruction_types}
    else:
        props = {t: 0 for t in instruction_types}
    regime_instruction_proportions[regime] = props

    print(f"\n{regime} (n={total}):")
    for t in instruction_types:
        pct = 100 * props[t]
        bar = '#' * int(pct / 2)
        print(f"  {t:<12}: {pct:5.1f}% {bar}")

print()

# =============================================================================
# Compute PREFIX Proportions per REGIME in B
# =============================================================================

print("CURRIER B PREFIX PROFILES BY REGIME")
print("-" * 70)

prefix_types = ['qo', 'ok', 'ot', 'da', 'ch', 'sh']

# Get folio-to-REGIME mapping
folio_to_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_to_regime[folio] = regime

# Compute prefix counts per REGIME
regime_prefix_profiles = {f'REGIME_{i}': Counter() for i in range(1, 5)}

for _, row in df_b.iterrows():
    folio = row['folio']
    word = str(row.get('word', ''))
    regime = folio_to_regime.get(folio)

    if regime and word:
        # Check which prefix
        for prefix in prefix_types:
            if word.startswith(prefix):
                regime_prefix_profiles[regime][prefix] += 1
                break

# Compute proportions
regime_prefix_proportions = {}
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    counts = regime_prefix_profiles[regime]
    total = sum(counts.values())
    if total > 0:
        props = {p: counts.get(p, 0) / total for p in prefix_types}
    else:
        props = {p: 0 for p in prefix_types}
    regime_prefix_proportions[regime] = props

    # Also compute combined ok+ot and ch+sh
    props['aux'] = props['ok'] + props['ot']
    props['energy'] = props['ch'] + props['sh']

    regime_prefix_proportions[regime] = props

    print(f"\n{regime} (n={total}):")
    for p in prefix_types:
        pct = 100 * props[p]
        bar = '#' * int(pct)
        print(f"  {p:<6}: {pct:5.1f}% {bar}")
    print(f"  {'aux':<6}: {100*props['aux']:5.1f}% (ok+ot combined)")
    print(f"  {'energy':<6}: {100*props['energy']:5.1f}% (ch+sh combined)")

print()

# =============================================================================
# Correlation Analysis
# =============================================================================

print("=" * 70)
print("CORRELATION ANALYSIS")
print("=" * 70)
print()

# Build vectors for correlation
# For each REGIME, we have instruction proportions and prefix proportions

regimes = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']

# Expected mappings to test:
# AUX -> aux (ok+ot)
# FLOW -> da
# e_ESCAPE -> qo
# k_ENERGY -> energy (ch+sh)

correlations = []

mappings = [
    ('AUX', 'aux', 'AUX preparation -> ok/ot auxiliary prefixes'),
    ('FLOW', 'da', 'FLOW collection -> da flow prefixes'),
    ('e_ESCAPE', 'qo', 'e_ESCAPE distillation -> qo escape prefixes'),
    ('k_ENERGY', 'energy', 'k_ENERGY heat -> ch/sh energy prefixes'),
]

for instr_type, prefix_type, description in mappings:
    # Get vectors
    instr_vec = [regime_instruction_proportions[r].get(instr_type, 0) for r in regimes]
    prefix_vec = [regime_prefix_proportions[r].get(prefix_type, 0) for r in regimes]

    # Pearson correlation
    if np.std(instr_vec) > 0 and np.std(prefix_vec) > 0:
        r, p = stats.pearsonr(instr_vec, prefix_vec)
    else:
        r, p = 0, 1.0

    correlations.append({
        'instruction': instr_type,
        'prefix': prefix_type,
        'description': description,
        'r': r,
        'p': p,
        'instr_vec': instr_vec,
        'prefix_vec': prefix_vec
    })

    print(f"{description}")
    print(f"  Instruction: {[f'{x:.3f}' for x in instr_vec]}")
    print(f"  PREFIX:      {[f'{x:.3f}' for x in prefix_vec]}")
    print(f"  Correlation: r={r:.4f}, p={p:.4f}")
    print()

# =============================================================================
# Summary
# =============================================================================

print("CORRELATION SUMMARY")
print("-" * 70)
print(f"{'Mapping':<30} {'r':<10} {'p':<10} {'Significant?'}")
print("-" * 70)

significant_count = 0
strong_count = 0

for c in correlations:
    sig = "YES" if c['p'] < 0.05 else "no"
    strong = c['r'] > 0.3
    if c['p'] < 0.05:
        significant_count += 1
    if strong:
        strong_count += 1
    strength = "STRONG" if strong else ""
    print(f"{c['instruction']}->{c['prefix']:<20} {c['r']:<10.4f} {c['p']:<10.4f} {sig:<5} {strength}")

print()

# =============================================================================
# Verdict
# =============================================================================

print("=" * 70)
print("VERDICT")
print("=" * 70)
print()

# Thresholds:
# H1 FALSE if: all correlations |r| < 0.2
# H1 SUPPORTED if: 3+ correlations r > 0.3

all_weak = all(abs(c['r']) < 0.2 for c in correlations)
strong_correlations = sum(1 for c in correlations if c['r'] > 0.3)

if strong_correlations >= 3:
    verdict = "H1 SUPPORTED"
    explanation = f"{strong_correlations}/4 correlations have r > 0.3"
elif all_weak:
    verdict = "H1 FALSIFIED"
    explanation = "All correlations |r| < 0.2 - no relationship"
else:
    verdict = "INCONCLUSIVE"
    explanation = f"{strong_correlations}/4 strong correlations, mixed signals"

print(f"Result: {verdict}")
print(f"Reason: {explanation}")
print()

# Note about sample size
print("NOTE: n=4 REGIMEs is a small sample for correlation.")
print("Results should be interpreted with caution.")

# =============================================================================
# Save Results
# =============================================================================

output = {
    'test': 'Test 3: PREFIX Profile Correlation',
    'hypothesis': 'H1: Instruction types correlate with B PREFIX profiles',
    'correlations': [
        {
            'instruction': c['instruction'],
            'prefix': c['prefix'],
            'r': c['r'],
            'p': c['p']
        } for c in correlations
    ],
    'regime_instruction_proportions': {
        r: dict(regime_instruction_proportions[r]) for r in regimes
    },
    'regime_prefix_proportions': {
        r: dict(regime_prefix_proportions[r]) for r in regimes
    },
    'summary': {
        'strong_correlations': strong_correlations,
        'significant_correlations': significant_count
    },
    'verdict': verdict,
    'explanation': explanation
}

output_path = PROJECT_ROOT / 'phases' / 'INTEGRATED_PROCESS_TEST' / 'results' / 'test3_prefix_correlation.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print()
print(f"Results saved to: {output_path}")
