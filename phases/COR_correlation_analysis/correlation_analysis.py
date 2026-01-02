"""
Program-Plant Correlation Analysis
Phase 1: Extract folio lists and metrics
Phase 2: Cross-reference botanical vs program folios
Phase 3: Compute correlations
"""

import json
import os

# Load control signatures
with open('control_signatures.json', 'r') as f:
    signatures = json.load(f)['signatures']

# List all folios with program data
program_folios = sorted(signatures.keys())
print(f"Total folios with control signatures: {len(program_folios)}")
print("\nFolios with program data:")
for i, f in enumerate(program_folios):
    print(f, end='  ')
    if (i+1) % 10 == 0:
        print()
print("\n")

# Known botanical folios (from PIAA analysis) - Herbal sections primarily
# These are folios with plant illustrations
botanical_folios = [
    'f1r', 'f1v', 'f2r', 'f2v', 'f3r', 'f3v', 'f4r', 'f4v', 'f5r', 'f5v',
    'f6r', 'f6v', 'f7r', 'f7v', 'f8r', 'f8v', 'f9r', 'f9v', 'f10r', 'f10v',
    'f11r', 'f11v', 'f13r', 'f13v', 'f14r', 'f14v', 'f15r', 'f15v', 'f16r', 'f16v',
    'f17r', 'f17v', 'f18r', 'f18v', 'f19r', 'f19v', 'f20r', 'f20v', 'f21r', 'f21v',
    'f22r', 'f22v', 'f23r', 'f23v', 'f24r', 'f24v', 'f25r', 'f25v',
    # Herbal B section (more botanical)
    'f26r', 'f26v', 'f27r', 'f27v', 'f28r', 'f28v', 'f29r', 'f29v', 'f30r', 'f30v',
    'f31r', 'f31v', 'f32r', 'f32v', 'f33r', 'f33v', 'f34r', 'f34v', 'f35r', 'f35v',
    'f36r', 'f36v', 'f37r', 'f37v', 'f38r', 'f38v', 'f39r', 'f39v', 'f40r', 'f40v',
    'f41r', 'f41v', 'f42r', 'f42v', 'f43r', 'f43v', 'f44r', 'f44v', 'f45r', 'f45v',
    'f46r', 'f46v', 'f47r', 'f47v', 'f48r', 'f48v', 'f49r', 'f49v', 'f50r', 'f50v',
    'f51r', 'f51v', 'f52r', 'f52v', 'f53r', 'f53v', 'f54r', 'f54v', 'f55r', 'f55v',
    'f56r', 'f56v',
    # Pharmaceutical section (may have plant-related illustrations)
    'f87r', 'f88r', 'f89r1', 'f89r2', 'f90r1', 'f90r2', 'f99r', 'f99v',
    'f100r', 'f100v', 'f101r1', 'f101r2', 'f102r1', 'f102r2'
]

# Find overlap
overlap = [f for f in program_folios if f in botanical_folios or
           any(f.startswith(b.rstrip('rv')) for b in botanical_folios)]

print(f"Overlap (folios with BOTH program data AND potential botanical content): {len(overlap)}")
print("\nOverlap folios:")
for i, f in enumerate(overlap):
    print(f, end='  ')
    if (i+1) % 10 == 0:
        print()
print("\n")

# Extract key metrics for each program folio
print("\n" + "="*80)
print("KEY METRICS FOR CORRELATION ANALYSIS")
print("="*80 + "\n")

metrics_summary = []
for folio in program_folios:
    sig = signatures[folio]
    metrics_summary.append({
        'folio': folio,
        'link_density': sig['link_density'],
        'hazard_density': sig['hazard_density'],
        'kernel_contact_ratio': sig['kernel_contact_ratio'],
        'recovery_ops_count': sig['recovery_ops_count'],
        'intervention_frequency': sig['intervention_frequency'],
        'total_length': sig['total_length'],
        'near_miss_count': sig['near_miss_count']
    })

# Classify aggressiveness based on metrics
# AGGRESSIVE: high hazard density, high intervention, low link
# CONSERVATIVE: low hazard density, low intervention, high link
# MODERATE: middle values

for m in metrics_summary:
    # Aggressiveness score = hazard_density + intervention_freq/20 - link_density
    agg_score = m['hazard_density'] + m['intervention_frequency']/20 - m['link_density']
    if agg_score > 0.6:
        m['aggressiveness'] = 'AGGRESSIVE'
    elif agg_score < 0.4:
        m['aggressiveness'] = 'CONSERVATIVE'
    else:
        m['aggressiveness'] = 'MODERATE'

    # LINK class
    if m['link_density'] > 0.45:
        m['link_class'] = 'HEAVY'
    elif m['link_density'] < 0.30:
        m['link_class'] = 'SPARSE'
    else:
        m['link_class'] = 'MODERATE'

    # Hazard proximity
    if m['hazard_density'] > 0.65:
        m['hazard_proximity'] = 'HIGH'
    elif m['hazard_density'] < 0.50:
        m['hazard_proximity'] = 'LOW'
    else:
        m['hazard_proximity'] = 'MEDIUM'

    # Duration class
    if m['total_length'] > 500:
        m['duration_class'] = 'EXTENDED'
    else:
        m['duration_class'] = 'REGULAR'

    # Recovery capability
    if m['recovery_ops_count'] > 10:
        m['recovery'] = 'HIGH'
    elif m['recovery_ops_count'] < 3:
        m['recovery'] = 'LOW'
    else:
        m['recovery'] = 'MODERATE'

# Print summary table
print(f"{'Folio':<8} {'Aggress':<12} {'LINK':<10} {'Hazard':<10} {'Duration':<10} {'Recovery':<10}")
print("-"*60)
for m in metrics_summary:
    print(f"{m['folio']:<8} {m['aggressiveness']:<12} {m['link_class']:<10} {m['hazard_proximity']:<10} {m['duration_class']:<10} {m['recovery']:<10}")

# Save metrics
with open('program_role_metrics.json', 'w') as f:
    json.dump(metrics_summary, f, indent=2)

print("\n\nSaved program role metrics to program_role_metrics.json")

# Distribution summary
print("\n\nDISTRIBUTION SUMMARY:")
print("-"*40)
from collections import Counter
print(f"Aggressiveness: {dict(Counter(m['aggressiveness'] for m in metrics_summary))}")
print(f"LINK class: {dict(Counter(m['link_class'] for m in metrics_summary))}")
print(f"Hazard proximity: {dict(Counter(m['hazard_proximity'] for m in metrics_summary))}")
print(f"Duration: {dict(Counter(m['duration_class'] for m in metrics_summary))}")
print(f"Recovery: {dict(Counter(m['recovery'] for m in metrics_summary))}")
