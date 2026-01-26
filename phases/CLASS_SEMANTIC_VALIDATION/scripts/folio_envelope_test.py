"""
Q1b: Folio-Level Envelope Test

Test whether gateway (Class 30) and terminal (Class 31) pair at folio level
rather than line level.

Hypothesis: If gateway/terminal mark hazard zones at folio level,
folios with gateways should tend to have terminals, and vice versa.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
from scipy import stats
import numpy as np
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

class_map = defaultdict(list)
for tok, cls in token_to_class.items():
    class_map[str(cls)].append(tok)

# Gateway and terminal tokens
gateway_tokens = set(class_map.get('30', []))
terminal_tokens = set(class_map.get('31', []))

print("=" * 60)
print("Q1b: FOLIO-LEVEL ENVELOPE TEST")
print("=" * 60)

print(f"\nGateway tokens (Class 30): {gateway_tokens}")
print(f"Terminal tokens (Class 31): {terminal_tokens}")

# Count by folio
folio_data = defaultdict(lambda: {'gateway': 0, 'terminal': 0, 'total': 0})

for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    folio_data[folio]['total'] += 1

    if word in gateway_tokens:
        folio_data[folio]['gateway'] += 1
    if word in terminal_tokens:
        folio_data[folio]['terminal'] += 1

# Categorize folios
both = []
gateway_only = []
terminal_only = []
neither = []

for folio, data in folio_data.items():
    has_gw = data['gateway'] > 0
    has_tm = data['terminal'] > 0

    if has_gw and has_tm:
        both.append(folio)
    elif has_gw:
        gateway_only.append(folio)
    elif has_tm:
        terminal_only.append(folio)
    else:
        neither.append(folio)

print("\n" + "-" * 40)
print("FOLIO CATEGORIZATION")
print("-" * 40)

total_folios = len(folio_data)
print(f"\nTotal folios: {total_folios}")
print(f"Both gateway AND terminal: {len(both)} ({len(both)/total_folios:.1%})")
print(f"Gateway only: {len(gateway_only)} ({len(gateway_only)/total_folios:.1%})")
print(f"Terminal only: {len(terminal_only)} ({len(terminal_only)/total_folios:.1%})")
print(f"Neither: {len(neither)} ({len(neither)/total_folios:.1%})")

print("\n" + "-" * 40)
print("CO-OCCURRENCE ANALYSIS")
print("-" * 40)

# 2x2 contingency table
has_gw = len(both) + len(gateway_only)
has_tm = len(both) + len(terminal_only)
no_gw = len(terminal_only) + len(neither)
no_tm = len(gateway_only) + len(neither)

contingency = [
    [len(both), len(gateway_only)],
    [len(terminal_only), len(neither)]
]

print("\n| | Has Terminal | No Terminal |")
print("|------------|--------------|-------------|")
print(f"| Has Gateway | {len(both):12d} | {len(gateway_only):11d} |")
print(f"| No Gateway  | {len(terminal_only):12d} | {len(neither):11d} |")

# Fisher's exact test (better for small counts)
odds_ratio, p_value = stats.fisher_exact(contingency)

print(f"\nFisher's exact test:")
print(f"  Odds ratio: {odds_ratio:.2f}")
print(f"  p-value: {p_value:.4f}")

# Calculate correlation
gw_counts = [folio_data[f]['gateway'] for f in folio_data]
tm_counts = [folio_data[f]['terminal'] for f in folio_data]

rho, p_corr = stats.spearmanr(gw_counts, tm_counts)
print(f"\nSpearman correlation (gateway count vs terminal count):")
print(f"  rho = {rho:.3f}, p = {p_corr:.4f}")

print("\n" + "-" * 40)
print("GATEWAY-DOMINANT vs TERMINAL-DOMINANT FOLIOS")
print("-" * 40)

# Check if folios tend to be gateway-dominant or terminal-dominant
gateway_dominant = []
terminal_dominant = []
balanced = []

for folio, data in folio_data.items():
    if data['gateway'] == 0 and data['terminal'] == 0:
        continue

    ratio = data['gateway'] / (data['gateway'] + data['terminal']) if (data['gateway'] + data['terminal']) > 0 else 0.5

    if ratio > 0.6:
        gateway_dominant.append((folio, data['gateway'], data['terminal']))
    elif ratio < 0.4:
        terminal_dominant.append((folio, data['gateway'], data['terminal']))
    else:
        balanced.append((folio, data['gateway'], data['terminal']))

print(f"\nGateway-dominant (>60% gateway): {len(gateway_dominant)}")
print(f"Terminal-dominant (>60% terminal): {len(terminal_dominant)}")
print(f"Balanced (40-60%): {len(balanced)}")

if gateway_dominant:
    print("\nTop 5 gateway-dominant folios:")
    for f, gw, tm in sorted(gateway_dominant, key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {f}: {gw} gateway, {tm} terminal")

if terminal_dominant:
    print("\nTop 5 terminal-dominant folios:")
    for f, gw, tm in sorted(terminal_dominant, key=lambda x: x[2], reverse=True)[:5]:
        print(f"  {f}: {gw} gateway, {tm} terminal")

print("\n" + "-" * 40)
print("SEQUENTIAL ANALYSIS")
print("-" * 40)

# Order folios and check if gateway-heavy precedes terminal-heavy
# Get folio ordering from corpus order
folio_order = []
seen = set()
for token in tokens:
    if token.folio not in seen:
        folio_order.append(token.folio)
        seen.add(token.folio)

# Calculate running gateway/terminal balance
gw_balance = []
for folio in folio_order:
    data = folio_data[folio]
    balance = (data['gateway'] - data['terminal']) / (data['gateway'] + data['terminal'] + 1)
    gw_balance.append(balance)

# Check for trend
positions = list(range(len(gw_balance)))
trend_rho, trend_p = stats.spearmanr(positions, gw_balance)

print(f"\nGateway-terminal balance trend across manuscript:")
print(f"  Spearman rho: {trend_rho:.3f}")
print(f"  p-value: {trend_p:.4f}")

if trend_rho > 0.1 and trend_p < 0.05:
    print("  => Gateway-heavy folios tend to come LATER")
elif trend_rho < -0.1 and trend_p < 0.05:
    print("  => Gateway-heavy folios tend to come EARLIER")
else:
    print("  => No significant sequential pattern")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print(f"\n1. Folio co-occurrence: {len(both)}/{total_folios} ({len(both)/total_folios:.1%}) have BOTH")
print(f"2. Fisher's exact: odds ratio = {odds_ratio:.2f}, p = {p_value:.4f}")
print(f"3. Count correlation: rho = {rho:.3f}")

if odds_ratio > 2 and p_value < 0.05:
    print("\n=> SUPPORTED: Gateway and terminal co-occur at folio level")
elif rho > 0.3 and p_corr < 0.05:
    print("\n=> SUPPORTED: Gateway and terminal counts correlate by folio")
elif odds_ratio > 1.5 or rho > 0.2:
    print("\n=> WEAK SUPPORT: Some folio-level association")
else:
    print("\n=> NOT SUPPORTED: No folio-level envelope pattern")

# Save results
results = {
    'total_folios': total_folios,
    'both': len(both),
    'gateway_only': len(gateway_only),
    'terminal_only': len(terminal_only),
    'neither': len(neither),
    'fisher_odds_ratio': odds_ratio,
    'fisher_p_value': p_value,
    'spearman_rho': rho,
    'spearman_p': p_corr,
    'trend_rho': trend_rho,
    'trend_p': trend_p
}

with open(RESULTS / 'folio_envelope_test.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'folio_envelope_test.json'}")
