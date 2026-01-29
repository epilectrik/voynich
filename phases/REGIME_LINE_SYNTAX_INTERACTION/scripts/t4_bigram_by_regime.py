"""
T4: Key Bigrams by REGIME

Question: Is the or->aiin directional bigram (C561) REGIME-dependent?

C561 shows or->aiin is the strongest role-transition bigram.
Does this pattern vary by REGIME?
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load class map
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
token_to_class = ctm['token_to_class']

# Load REGIME mapping
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_map = json.load(f)

folio_to_regime = {}
for regime, folios in regime_map.items():
    for f in folios:
        folio_to_regime[f] = regime

# Key bigrams to test
KEY_BIGRAMS = [
    ('or', 'aiin'),      # C561: strongest role-transition
    ('daiin', 'chol'),   # C557: daiin trigger
    ('ol', 'chedy'),     # ol -> EN_CHSH
    ('qo', 'daiin'),     # QO -> CC
]

# Also track MIDDLE-based patterns
# daiin trigger -> CHSH vs QO

# Collect line tokens
line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    regime = folio_to_regime.get(token.folio)
    if not regime:
        continue

    key = (token.folio, token.line, regime)
    tc = token_to_class.get(w)
    m = morph.extract(w)

    line_tokens[key].append({
        'word': w,
        'middle': m.middle,
        'prefix': m.prefix or '',
    })

# Count bigrams by REGIME
bigram_counts = defaultdict(lambda: defaultdict(int))  # regime -> bigram -> count
total_bigrams = defaultdict(int)  # regime -> total

# Also track specific patterns
daiin_successor_lane = defaultdict(Counter)  # regime -> {QO, CHSH, OTHER}

for key, tokens in line_tokens.items():
    folio, line, regime = key

    for i in range(len(tokens) - 1):
        curr = tokens[i]
        next_t = tokens[i + 1]

        total_bigrams[regime] += 1

        # Word-level bigrams
        bigram = (curr['word'], next_t['word'])
        bigram_counts[regime][bigram] += 1

        # MIDDLE-level bigrams
        mid_bigram = (curr['middle'], next_t['middle'])
        bigram_counts[regime][('MID:' + str(curr['middle']), 'MID:' + str(next_t['middle']))] += 1

        # daiin successor lane
        if curr['word'] == 'daiin':
            succ_prefix = next_t['prefix']
            if succ_prefix == 'qo':
                daiin_successor_lane[regime]['QO'] += 1
            elif succ_prefix in {'ch', 'sh'}:
                daiin_successor_lane[regime]['CHSH'] += 1
            else:
                daiin_successor_lane[regime]['OTHER'] += 1

print("=" * 60)
print("T4: KEY BIGRAMS BY REGIME")
print("=" * 60)

results = {}

# Test each key bigram
print("\nKEY BIGRAM RATES BY REGIME:")
print("-" * 40)

for bigram in KEY_BIGRAMS:
    print(f"\n{bigram[0]} -> {bigram[1]}:")

    rates = {}
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        count = bigram_counts[regime].get(bigram, 0)
        total = total_bigrams[regime]
        if total > 0:
            rate = count / total
            rates[regime] = (count, total, rate)
            print(f"  {regime}: {count}/{total} = {rate*1000:.2f} per 1000")

    # Chi-squared for variation
    if len(rates) >= 2:
        observed = [v[0] for v in rates.values()]
        totals = [v[1] for v in rates.values()]
        overall_rate = sum(observed) / sum(totals) if sum(totals) > 0 else 0
        expected = [t * overall_rate for t in totals]

        if all(e > 0 for e in expected):
            chi2, p = stats.chisquare(observed, expected)
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "NS"
            print(f"  Chi-squared: {chi2:.2f}, p={p:.4f} {sig}")

            results[f"{bigram[0]}->{bigram[1]}"] = {
                'chi2': float(chi2),
                'p': float(p),
                'rates': {k: float(v[2]) for k, v in rates.items()},
            }

# daiin -> lane analysis
print("\n" + "=" * 60)
print("DAIIN SUCCESSOR LANE BY REGIME:")
print("=" * 60)

for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    counts = daiin_successor_lane.get(regime, Counter())
    total = sum(counts.values())
    if total >= 5:
        qo = counts.get('QO', 0)
        chsh = counts.get('CHSH', 0)
        other = counts.get('OTHER', 0)
        print(f"\n{regime} (n={total}):")
        print(f"  QO: {qo} ({qo/total*100:.1f}%)")
        print(f"  CHSH: {chsh} ({chsh/total*100:.1f}%)")
        print(f"  OTHER: {other} ({other/total*100:.1f}%)")

# Test CHSH rate variation
print("\n" + "-" * 40)
print("DAIIN -> CHSH RATE VARIATION:")

chsh_rates = {}
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    counts = daiin_successor_lane.get(regime, Counter())
    total = sum(counts.values())
    if total >= 5:
        chsh = counts.get('CHSH', 0)
        chsh_rates[regime] = (chsh, total, chsh/total)

if len(chsh_rates) >= 2:
    observed = [v[0] for v in chsh_rates.values()]
    totals = [v[1] for v in chsh_rates.values()]
    overall_rate = sum(observed) / sum(totals)
    expected = [t * overall_rate for t in totals]

    chi2, p = stats.chisquare(observed, expected)
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "NS"
    print(f"\nChi-squared (daiin->CHSH variation): {chi2:.2f}, p={p:.4f} {sig}")

    results['daiin_chsh_chi2'] = float(chi2)
    results['daiin_chsh_p'] = float(p)

# Save results
out_path = PROJECT_ROOT / 'phases' / 'REGIME_LINE_SYNTAX_INTERACTION' / 'results' / 't4_bigram_by_regime.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path.name}")
