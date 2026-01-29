"""
T2: Does AZC-mediated fraction predict B behavioral properties?

Test whether:
- AZC-mediated % correlates with escape rate
- AZC-mediated % correlates with LINK density
- AZC-mediated % correlates with hazard exposure
- Vocab size (which correlates with AZC-mediated %) predicts behavior

If AZC genuinely constrains B, these should show relationships.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology, RecordAnalyzer

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

print("="*70)
print("T2: DOES AZC-MEDIATED FRACTION PREDICT B BEHAVIOR?")
print("="*70)

# Load T1 results
t1_path = PROJECT_ROOT / 'phases' / 'AZC_B_CONSTRAINT_MECHANISM' / 'results' / 't1_b_azc_overlap.json'
with open(t1_path) as f:
    t1_data = json.load(f)

# Create lookup for AZC-mediated % by folio
azc_pct_by_folio = {r['folio']: r['pct_azc_mediated'] for r in t1_data['per_folio']}
vocab_size_by_folio = {r['folio']: r['total_middles'] for r in t1_data['per_folio']}

# Calculate B behavioral metrics per folio
print("\nCalculating B behavioral metrics per folio...")

# Collect per-folio metrics
folio_metrics = defaultdict(lambda: {
    'tokens': 0,
    'escape_tokens': 0,  # Tokens with 'e' suffix (escape)
    'link_tokens': 0,    # LINK class tokens
    'kernel_contact': 0, # Tokens contacting kernel (k, h, e)
    'lines': set(),
    'hazard_adjacent': 0 # Tokens adjacent to hazard positions
})

# Simple metrics we can calculate directly
for token in tx.currier_b():
    folio = token.folio
    folio_metrics[folio]['tokens'] += 1
    folio_metrics[folio]['lines'].add(token.line)

    m = morph.extract(token.word)

    # Escape suffix
    if m.suffix and 'e' in m.suffix:
        folio_metrics[folio]['escape_tokens'] += 1

    # Kernel contact (k, h, e in MIDDLE)
    if m.middle:
        if any(c in m.middle for c in ['k', 'h', 'e']):
            folio_metrics[folio]['kernel_contact'] += 1

# Calculate rates
folio_data = []
for folio, metrics in folio_metrics.items():
    if folio not in azc_pct_by_folio:
        continue

    n_tokens = metrics['tokens']
    if n_tokens == 0:
        continue

    escape_rate = 100 * metrics['escape_tokens'] / n_tokens
    kernel_rate = 100 * metrics['kernel_contact'] / n_tokens
    n_lines = len(metrics['lines'])
    tokens_per_line = n_tokens / n_lines if n_lines > 0 else 0

    folio_data.append({
        'folio': folio,
        'azc_pct': azc_pct_by_folio[folio],
        'vocab_size': vocab_size_by_folio[folio],
        'n_tokens': n_tokens,
        'n_lines': n_lines,
        'escape_rate': escape_rate,
        'kernel_rate': kernel_rate,
        'tokens_per_line': tokens_per_line
    })

df = pd.DataFrame(folio_data)

print(f"\nAnalyzing {len(df)} B folios with both AZC and behavioral data")

# Correlation analysis
print("\n" + "="*70)
print("CORRELATION ANALYSIS")
print("="*70)

metrics = ['escape_rate', 'kernel_rate', 'tokens_per_line', 'n_tokens', 'n_lines']
predictors = ['azc_pct', 'vocab_size']

results = {}

for pred in predictors:
    print(f"\n{pred.upper()} correlations:")
    results[pred] = {}
    for metric in metrics:
        r, p = stats.pearsonr(df[pred], df[metric])
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"  vs {metric:<18}: r = {r:+.3f}, p = {p:.4f} {sig}")
        results[pred][metric] = {'r': round(r, 3), 'p': round(p, 4)}

# The key test: does AZC-mediated % predict escape rate?
print("\n" + "="*70)
print("KEY TEST: AZC-MEDIATED % vs ESCAPE RATE")
print("="*70)

r, p = stats.pearsonr(df['azc_pct'], df['escape_rate'])
print(f"\nCorrelation: r = {r:.3f}, p = {p:.4f}")

if p < 0.05:
    if r > 0:
        print("FINDING: Higher AZC-mediation -> HIGHER escape rate")
        print("Interpretation: AZC-constrained folios ENABLE more escape")
    else:
        print("FINDING: Higher AZC-mediation -> LOWER escape rate")
        print("Interpretation: AZC-constrained folios RESTRICT escape")
else:
    print("FINDING: No significant relationship between AZC-mediation and escape rate")

# Scatter data for visualization
print("\n" + "="*70)
print("AZC-MEDIATED % vs ESCAPE RATE (scatter data)")
print("="*70)
print(f"\n{'Folio':<10} {'AZC %':<10} {'Escape %':<10} {'Vocab':<10}")
print("-"*40)
for _, row in df.sort_values('azc_pct').iterrows():
    print(f"{row['folio']:<10} {row['azc_pct']:<10.1f} {row['escape_rate']:<10.1f} {row['vocab_size']:<10}")

# Check if vocab_size mediates the relationship
print("\n" + "="*70)
print("MEDIATION ANALYSIS: Is vocab_size the real driver?")
print("="*70)

# Partial correlation: AZC_pct vs escape_rate controlling for vocab_size
from scipy.stats import pearsonr

# Simple approach: residualize both variables on vocab_size
from numpy.polynomial import polynomial as P

# Fit escape_rate ~ vocab_size
slope_e, intercept_e = np.polyfit(df['vocab_size'], df['escape_rate'], 1)
escape_residual = df['escape_rate'] - (slope_e * df['vocab_size'] + intercept_e)

# Fit azc_pct ~ vocab_size
slope_a, intercept_a = np.polyfit(df['vocab_size'], df['azc_pct'], 1)
azc_residual = df['azc_pct'] - (slope_a * df['vocab_size'] + intercept_a)

partial_r, partial_p = pearsonr(azc_residual, escape_residual)
print(f"\nPartial correlation (AZC % vs Escape %, controlling vocab_size):")
print(f"  r = {partial_r:.3f}, p = {partial_p:.4f}")

if partial_p < 0.05:
    print("  AZC % has INDEPENDENT effect on escape rate beyond vocab size")
else:
    print("  AZC % effect is MEDIATED by vocab size (no independent effect)")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

# Determine verdict
if results['azc_pct']['escape_rate']['p'] < 0.05:
    if abs(partial_r) > 0.1 and partial_p < 0.1:
        verdict = "AZC_INDEPENDENT_EFFECT"
        print("\nVERDICT: AZC-mediated % has INDEPENDENT predictive power")
    else:
        verdict = "VOCAB_SIZE_MEDIATES"
        print("\nVERDICT: Effect is mediated through vocabulary size")
else:
    verdict = "NO_BEHAVIORAL_PREDICTION"
    print("\nVERDICT: AZC-mediated % does not predict escape behavior")

# Save results
output = {
    'n_folios': len(df),
    'correlations': results,
    'partial_correlation': {
        'azc_vs_escape_controlling_vocab': {
            'r': round(partial_r, 3),
            'p': round(partial_p, 4)
        }
    },
    'verdict': verdict
}

output_path = PROJECT_ROOT / 'phases' / 'AZC_B_CONSTRAINT_MECHANISM' / 'results' / 't2_behavior_prediction.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: {output_path}")
