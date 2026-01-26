"""
Q2: qo-Chain Thermal Mapping

Test whether sustained qo-family sequences (Classes 32, 33, 36)
appear preferentially in thermal control contexts (REGIME_1, Section B).

Hypothesis: If qo-family represents "escape routes" or "venting",
they should cluster where thermal control is intensive.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

# The format is {"token_to_class": {token: class_id, ...}}
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Build reverse map: class_id -> [tokens]
class_map = defaultdict(list)
for tok, cls in token_to_class.items():
    class_map[str(cls)].append(tok)

# Load REGIME (format: {REGIME: [folios]})
with open(REGIME_FILE) as f:
    regime_data = json.load(f)

# Invert: {folio: REGIME}
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

# qo-family classes
QO_CLASSES = {32, 33, 36}
# ch/sh-family classes (for comparison)
CHSH_CLASSES = {8, 31, 34}

print("=" * 60)
print("Q2: qo-CHAIN THERMAL MAPPING")
print("=" * 60)

# Get qo-family tokens
qo_tokens = set()
for cls in QO_CLASSES:
    qo_tokens.update(class_map.get(str(cls), []))

chsh_tokens = set()
for cls in CHSH_CLASSES:
    chsh_tokens.update(class_map.get(str(cls), []))

print(f"\nqo-family tokens (Classes {QO_CLASSES}): {sorted(list(qo_tokens))[:10]}...")
print(f"ch/sh-family tokens (Classes {CHSH_CLASSES}): {sorted(list(chsh_tokens))[:10]}...")

# Group tokens by folio/line
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    line = token.line
    regime = folio_regime.get(folio)
    lines[(folio, line)].append({
        'word': word,
        'regime': regime,
        'is_qo': word in qo_tokens,
        'is_chsh': word in chsh_tokens
    })

print("\n" + "-" * 40)
print("qo-CHAIN DETECTION")
print("-" * 40)

# Detect qo-chains (2+ consecutive qo-family tokens)
chains = []
for (folio, line), word_data in lines.items():
    regime = word_data[0]['regime'] if word_data else None

    current_chain = []
    for wd in word_data:
        if wd['is_qo']:
            current_chain.append(wd['word'])
        else:
            if len(current_chain) >= 2:
                chains.append({
                    'folio': folio,
                    'line': line,
                    'regime': regime,
                    'length': len(current_chain),
                    'tokens': current_chain.copy()
                })
            current_chain = []

    if len(current_chain) >= 2:
        chains.append({
            'folio': folio,
            'line': line,
            'regime': regime,
            'length': len(current_chain),
            'tokens': current_chain.copy()
        })

print(f"\nTotal qo-chains (2+ consecutive): {len(chains)}")
if chains:
    print(f"Mean chain length: {sum(c['length'] for c in chains) / len(chains):.2f}")
    print(f"Max chain length: {max(c['length'] for c in chains)}")

# Chain length distribution
length_dist = defaultdict(int)
for c in chains:
    length_dist[c['length']] += 1

print("\nChain length distribution:")
for length in sorted(length_dist.keys()):
    print(f"  Length {length}: {length_dist[length]} chains")

print("\n" + "-" * 40)
print("REGIME DISTRIBUTION OF qo-CHAINS")
print("-" * 40)

# Count chains by REGIME
chain_by_regime = defaultdict(int)
for c in chains:
    if c['regime']:
        chain_by_regime[c['regime']] += 1

# Token distribution by REGIME for baseline
token_by_regime = defaultdict(int)
for token in tokens:
    regime = folio_regime.get(token.folio)
    if regime:
        token_by_regime[regime] += 1

total_tokens = sum(token_by_regime.values())
total_chains = sum(chain_by_regime.values())

print("\n| REGIME | qo-Chains | Total Tokens | Chain Rate | Expected | Enrichment |")
print("|--------|-----------|--------------|------------|----------|------------|")

for regime in sorted(token_by_regime.keys()):
    chains_in_regime = chain_by_regime[regime]
    tokens_in_regime = token_by_regime[regime]
    regime_fraction = tokens_in_regime / total_tokens if total_tokens > 0 else 0
    expected = total_chains * regime_fraction
    enrichment = chains_in_regime / expected if expected > 0 else 0

    print(f"| {regime} | {chains_in_regime:4d} | {tokens_in_regime:6d} | {chains_in_regime/total_chains:.1%} | {expected:.1f} | {enrichment:.2f}x |")

print("\n" + "-" * 40)
print("qo vs ch/sh FAMILY REGIME COMPARISON")
print("-" * 40)

# Count qo and chsh tokens by REGIME
qo_by_regime = defaultdict(int)
chsh_by_regime = defaultdict(int)

for token in tokens:
    word = token.word.replace('*', '').strip()
    regime = folio_regime.get(token.folio)
    if regime:
        if word in qo_tokens:
            qo_by_regime[regime] += 1
        if word in chsh_tokens:
            chsh_by_regime[regime] += 1

total_qo = sum(qo_by_regime.values())
total_chsh = sum(chsh_by_regime.values())

print("\n| REGIME | qo-tokens | ch/sh-tokens | qo Rate | ch/sh Rate | qo/ch Ratio |")
print("|--------|-----------|--------------|---------|------------|-------------|")

for regime in sorted(token_by_regime.keys()):
    qo_count = qo_by_regime[regime]
    chsh_count = chsh_by_regime[regime]
    qo_rate = qo_count / total_qo if total_qo > 0 else 0
    chsh_rate = chsh_count / total_chsh if total_chsh > 0 else 0
    ratio = qo_rate / chsh_rate if chsh_rate > 0 else float('inf')

    print(f"| {regime} | {qo_count:5d} | {chsh_count:6d} | {qo_rate:.1%} | {chsh_rate:.1%} | {ratio:.2f} |")

print("\n" + "-" * 40)
print("INTERLEAVING PATTERN BY REGIME")
print("-" * 40)

transitions = defaultdict(lambda: {'qo_to_chsh': 0, 'chsh_to_qo': 0, 'qo_to_qo': 0, 'chsh_to_chsh': 0})

for (folio, line), word_data in lines.items():
    regime = word_data[0]['regime'] if word_data else None
    if not regime:
        continue

    for i in range(len(word_data) - 1):
        curr_qo = word_data[i]['is_qo']
        curr_chsh = word_data[i]['is_chsh']
        next_qo = word_data[i+1]['is_qo']
        next_chsh = word_data[i+1]['is_chsh']

        if curr_qo and next_chsh:
            transitions[regime]['qo_to_chsh'] += 1
        elif curr_chsh and next_qo:
            transitions[regime]['chsh_to_qo'] += 1
        elif curr_qo and next_qo:
            transitions[regime]['qo_to_qo'] += 1
        elif curr_chsh and next_chsh:
            transitions[regime]['chsh_to_chsh'] += 1

print("\n| REGIME | qo->ch/sh | ch/sh->qo | qo->qo | ch/sh->ch/sh | Interleave Rate |")
print("|--------|-----------|-----------|--------|--------------|-----------------|")

for regime in sorted(transitions.keys()):
    t = transitions[regime]
    interleave = t['qo_to_chsh'] + t['chsh_to_qo']
    same = t['qo_to_qo'] + t['chsh_to_chsh']
    total_trans = interleave + same
    interleave_rate = interleave / total_trans if total_trans > 0 else 0

    print(f"| {regime} | {t['qo_to_chsh']:5d} | {t['chsh_to_qo']:5d} | {t['qo_to_qo']:4d} | {t['chsh_to_chsh']:6d} | {interleave_rate:.1%} |")

print("\n" + "-" * 40)
print("LONGEST qo-CHAINS")
print("-" * 40)

sorted_chains = sorted(chains, key=lambda x: x['length'], reverse=True)
print("\nTop 10 longest qo-chains:")
for c in sorted_chains[:10]:
    print(f"  {c['folio']}:{c['line']} ({c['regime']}): {' '.join(c['tokens'])}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print("\nHypothesis: qo-chains cluster in thermal contexts (REGIME_1)")

regime1_chains = chain_by_regime.get('REGIME_1', 0)
regime1_tokens = token_by_regime.get('REGIME_1', 1)
regime1_expected = total_chains * (regime1_tokens / total_tokens) if total_tokens > 0 else 0
regime1_enrichment = regime1_chains / regime1_expected if regime1_expected > 0 else 0

print(f"\n- REGIME_1 qo-chains: {regime1_chains}/{total_chains} ({regime1_chains/total_chains:.1%})" if total_chains > 0 else "\n- No chains found")
print(f"- Expected (by tokens): {regime1_expected:.1f}")
print(f"- Enrichment: {regime1_enrichment:.2f}x")

regime1_qo = qo_by_regime.get('REGIME_1', 0)
regime1_chsh = chsh_by_regime.get('REGIME_1', 0)
regime1_ratio = regime1_qo / regime1_chsh if regime1_chsh > 0 else float('inf')
overall_ratio = total_qo / total_chsh if total_chsh > 0 else 0

print(f"\n- REGIME_1 qo/chsh ratio: {regime1_ratio:.2f}")
print(f"- Overall qo/chsh ratio: {overall_ratio:.2f}")
if overall_ratio > 0:
    print(f"- REGIME_1 qo-preference: {regime1_ratio / overall_ratio:.2f}x")

if regime1_enrichment > 1.5 or (overall_ratio > 0 and regime1_ratio > overall_ratio * 1.3):
    print("\n=> SUPPORTED: qo-chains enriched in thermal contexts")
elif regime1_enrichment > 1.0:
    print("\n=> WEAK SUPPORT: Slight qo-chain enrichment in thermal contexts")
else:
    print("\n=> NOT SUPPORTED: No qo-chain enrichment in thermal contexts")

# Save results
results = {
    'total_chains': len(chains),
    'mean_chain_length': sum(c['length'] for c in chains) / len(chains) if chains else 0,
    'chains_by_regime': dict(chain_by_regime),
    'regime_enrichment': {r: chain_by_regime[r] / (total_chains * (token_by_regime.get(r, 0) / total_tokens))
                          if total_tokens > 0 and total_chains > 0 and token_by_regime.get(r, 0) > 0 else 0
                          for r in chain_by_regime},
    'qo_chsh_ratio_by_regime': {r: (qo_by_regime.get(r, 0) / chsh_by_regime.get(r, 1)) if chsh_by_regime.get(r, 0) > 0 else 0
                                 for r in token_by_regime},
    'top_chains': [{'folio': c['folio'], 'line': c['line'], 'regime': c['regime'],
                    'length': c['length'], 'tokens': c['tokens']} for c in sorted_chains[:20]]
}

with open(RESULTS / 'qo_chain_thermal.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'qo_chain_thermal.json'}")
