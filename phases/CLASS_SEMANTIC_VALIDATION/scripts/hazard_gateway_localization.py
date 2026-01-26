"""
Q1: Hazard Gateway Localization

Test whether hazard gateway tokens (Class 30: dar/dal) cluster in
thermal-processing sections (Section B, REGIME_1).

Hypothesis: If dar/dal mark "entering critical phase" transitions,
they should be enriched in thermally-intensive sections.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
from scipy import stats
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
tokens = list(tx.currier_b())  # Currier B only, H track, no labels

with open(CLASS_MAP) as f:
    class_data = json.load(f)

# The format is {"token_to_class": {token: class_id, ...}}
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Build reverse map: class_id -> [tokens]
class_map = defaultdict(list)
for tok, cls in token_to_class.items():
    class_map[str(cls)].append(tok)

# Load REGIME assignments (format: {REGIME: [folios]})
with open(REGIME_FILE) as f:
    regime_data = json.load(f)

# Invert: {folio: REGIME}
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

# Section B folios (balneological section f75-f84)
SECTION_B_FOLIOS = set()
for token in tokens:
    folio = token.folio
    folio_num = ''.join(c for c in folio if c.isdigit())
    if folio_num:
        num = int(folio_num)
        if 75 <= num <= 84:
            SECTION_B_FOLIOS.add(folio)

print("=" * 60)
print("Q1: HAZARD GATEWAY LOCALIZATION")
print("=" * 60)

# Find all Class 30 tokens (hazard gateways)
gateway_tokens = set(class_map.get('30', []))
print(f"\nClass 30 (gateway) tokens: {gateway_tokens}")

# Find all Class 31 tokens (hazard terminals)
terminal_tokens = set(class_map.get('31', []))
print(f"Class 31 (terminal) tokens: {terminal_tokens}")

# Classify each token
gateway_count = 0
terminal_count = 0
gateway_in_b = 0
gateway_in_regime1 = 0
total_in_b = 0
total_in_regime1 = 0

regime_counts = defaultdict(lambda: {'gateway': 0, 'terminal': 0, 'total': 0})
folio_gateways = defaultdict(int)
folio_terminals = defaultdict(int)

for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    regime = folio_regime.get(folio)
    in_b = folio in SECTION_B_FOLIOS

    if in_b:
        total_in_b += 1
    if regime == 'REGIME_1':
        total_in_regime1 += 1

    if regime:
        regime_counts[regime]['total'] += 1

    if word in gateway_tokens:
        gateway_count += 1
        folio_gateways[folio] += 1
        if in_b:
            gateway_in_b += 1
        if regime == 'REGIME_1':
            gateway_in_regime1 += 1
        if regime:
            regime_counts[regime]['gateway'] += 1

    if word in terminal_tokens:
        terminal_count += 1
        folio_terminals[folio] += 1
        if regime:
            regime_counts[regime]['terminal'] += 1

total_tokens = len(tokens)

print("\n" + "-" * 40)
print("SECTION B DISTRIBUTION")
print("-" * 40)

baseline_b_rate = total_in_b / total_tokens if total_tokens > 0 else 0
gateway_b_rate = gateway_in_b / gateway_count if gateway_count > 0 else 0

print(f"\nBaseline Section B rate: {baseline_b_rate:.1%} ({total_in_b}/{total_tokens})")
print(f"Gateway Section B rate: {gateway_b_rate:.1%} ({gateway_in_b}/{gateway_count})")

enrichment_b = gateway_b_rate / baseline_b_rate if baseline_b_rate > 0 else 0
print(f"Section B enrichment: {enrichment_b:.2f}x")

print("\n" + "-" * 40)
print("REGIME DISTRIBUTION")
print("-" * 40)

total_gateway = sum(r['gateway'] for r in regime_counts.values())
total_terminal = sum(r['terminal'] for r in regime_counts.values())
total_all = sum(r['total'] for r in regime_counts.values())
baseline_gateway = total_gateway / total_all if total_all > 0 else 0
baseline_terminal = total_terminal / total_all if total_all > 0 else 0

print("\n| REGIME | Gateways | Terminals | Total | Gateway Rate | Terminal Rate |")
print("|--------|----------|-----------|-------|--------------|---------------|")

for regime in sorted(regime_counts.keys()):
    counts = regime_counts[regime]
    gw_rate = counts['gateway'] / counts['total'] if counts['total'] > 0 else 0
    tm_rate = counts['terminal'] / counts['total'] if counts['total'] > 0 else 0
    print(f"| {regime} | {counts['gateway']:4d} | {counts['terminal']:5d} | {counts['total']:5d} | {gw_rate:.3%} | {tm_rate:.3%} |")

print(f"| BASELINE | {total_gateway:4d} | {total_terminal:5d} | {total_all:5d} | {baseline_gateway:.3%} | {baseline_terminal:.3%} |")

print("\n" + "-" * 40)
print("REGIME ENRICHMENT")
print("-" * 40)

print("\n| REGIME | Gateway Enrichment | Terminal Enrichment |")
print("|--------|-------------------|---------------------|")

for regime in sorted(regime_counts.keys()):
    counts = regime_counts[regime]
    gw_rate = counts['gateway'] / counts['total'] if counts['total'] > 0 else 0
    tm_rate = counts['terminal'] / counts['total'] if counts['total'] > 0 else 0
    gw_enrich = gw_rate / baseline_gateway if baseline_gateway > 0 else 0
    tm_enrich = tm_rate / baseline_terminal if baseline_terminal > 0 else 0
    print(f"| {regime} | {gw_enrich:.2f}x | {tm_enrich:.2f}x |")

print("\n" + "-" * 40)
print("FOLIO-LEVEL ANALYSIS")
print("-" * 40)

# Top folios by gateway count
sorted_gateways = sorted(folio_gateways.items(), key=lambda x: -x[1])
print("\nTop 10 folios by gateway (Class 30) count:")
for folio, count in sorted_gateways[:10]:
    regime = folio_regime.get(folio, 'N/A')
    in_b = 'B' if folio in SECTION_B_FOLIOS else '-'
    print(f"  {folio}: {count} gateways (REGIME: {regime}, Section B: {in_b})")

sorted_terminals = sorted(folio_terminals.items(), key=lambda x: -x[1])
print("\nTop 10 folios by terminal (Class 31) count:")
for folio, count in sorted_terminals[:10]:
    regime = folio_regime.get(folio, 'N/A')
    in_b = 'B' if folio in SECTION_B_FOLIOS else '-'
    print(f"  {folio}: {count} terminals (REGIME: {regime}, Section B: {in_b})")

print("\n" + "-" * 40)
print("GATEWAY-TERMINAL PAIRING")
print("-" * 40)

# Group by folio/line
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    lines[(token.folio, token.line)].append(word)

gateway_terminal_pairs = 0
terminal_gateway_pairs = 0
lines_with_both = 0

for (folio, line), words in lines.items():
    has_gateway = any(w in gateway_tokens for w in words)
    has_terminal = any(w in terminal_tokens for w in words)

    if has_gateway and has_terminal:
        lines_with_both += 1
        gateway_pos = None
        terminal_pos = None
        for i, w in enumerate(words):
            if w in gateway_tokens and gateway_pos is None:
                gateway_pos = i
            if w in terminal_tokens and terminal_pos is None:
                terminal_pos = i

        if gateway_pos is not None and terminal_pos is not None:
            if gateway_pos < terminal_pos:
                gateway_terminal_pairs += 1
            else:
                terminal_gateway_pairs += 1

print(f"\nLines with both gateway and terminal: {lines_with_both}")
print(f"Gateway -> Terminal order: {gateway_terminal_pairs}")
print(f"Terminal -> Gateway order: {terminal_gateway_pairs}")
if gateway_terminal_pairs + terminal_gateway_pairs > 0:
    correct_order_rate = gateway_terminal_pairs / (gateway_terminal_pairs + terminal_gateway_pairs)
    print(f"Correct order rate: {correct_order_rate:.1%}")
else:
    correct_order_rate = None

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print("\nHypothesis: Gateways cluster in thermal sections (B, REGIME_1)")

regime1_counts = regime_counts.get('REGIME_1', {'gateway': 0, 'total': 1})
regime1_rate = regime1_counts['gateway'] / regime1_counts['total'] if regime1_counts['total'] > 0 else 0
regime1_enrich = regime1_rate / baseline_gateway if baseline_gateway > 0 else 0

print(f"\n- Section B enrichment: {enrichment_b:.2f}x")
print(f"- REGIME_1 enrichment: {regime1_enrich:.2f}x")

if regime1_enrich > 1.5:
    print("\n=> SUPPORTED: Gateways are enriched in thermal contexts")
elif regime1_enrich > 1.0:
    print("\n=> WEAK SUPPORT: Slight gateway enrichment in thermal contexts")
else:
    print("\n=> NOT SUPPORTED: No gateway enrichment in thermal contexts")

# Save results
results = {
    'section_b_enrichment': enrichment_b,
    'regime_enrichment': {r: regime_counts[r]['gateway'] / regime_counts[r]['total'] / baseline_gateway
                          if regime_counts[r]['total'] > 0 and baseline_gateway > 0 else 0
                          for r in regime_counts},
    'gateway_terminal_order': {
        'correct': gateway_terminal_pairs,
        'reversed': terminal_gateway_pairs,
        'correct_rate': correct_order_rate
    },
    'top_gateway_folios': dict(sorted_gateways[:10]),
    'top_terminal_folios': dict(sorted_terminals[:10])
}

with open(RESULTS / 'hazard_gateway_localization.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'hazard_gateway_localization.json'}")
