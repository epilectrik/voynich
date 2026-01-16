#!/usr/bin/env python3
"""
A/C INTERNAL CHARACTERIZATION - PROBE 1: HT PHASE-RESET FREQUENCY

Question: Do A/C folios force more frequent HT phase transitions (EARLY↔LATE)
          than Zodiac folios?

Method:
1. For each AZC folio, extract HT tokens and classify as EARLY or LATE (C413)
2. Count EARLY→LATE and LATE→EARLY transitions within each folio
3. Normalize by token count to get transition rate
4. Compare A/C family vs Zodiac family

Prediction: A/C will show higher phase-reset frequency because fine discrimination
            requires more attention resets.
"""

import csv
import json
import math
from collections import defaultdict, Counter
from scipy import stats
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

# HT phase classes from C413
HT_EARLY_PREFIXES = ['op', 'pc', 'do']
HT_LATE_PREFIXES = ['ta']

# Zodiac AZC folios
ZODIAC_FOLIOS = {
    'f70v1', 'f70v2',
    'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3',
    'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v',
    'f57v'
}

# A/C family sections
AC_SECTIONS = {'A', 'C', 'H', 'S'}

def get_ht_phase(token):
    """Classify token as EARLY, LATE, or None."""
    if not token:
        return None
    token = token.lower().strip()

    for prefix in HT_EARLY_PREFIXES:
        if token.startswith(prefix):
            return 'EARLY'
    for prefix in HT_LATE_PREFIXES:
        if token.startswith(prefix):
            return 'LATE'
    return None

def is_ht_token(token):
    """Check if token is any HT token (broader than just phase-classified)."""
    if not token:
        return False
    token = token.lower().strip()
    # HT tokens typically start with y- or specific prefixes
    ht_prefixes = ['sa', 'kch', 'pc', 'so', 'po', 'ke', 'op', 'ks',
                   'yd', 'ysh', 'ko', 'dc', 'ych', 'ka', 'ta', 'do', 'yt', 'yk']
    return any(token.startswith(p) for p in ht_prefixes) or token.startswith('y')

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("A/C x HT PHASE-RESET FREQUENCY TEST")
print("=" * 70)
print()
print("Question: Do A/C folios force more frequent HT phase transitions")
print("          (EARLY<->LATE) than Zodiac folios?")
print()

# Load tokens grouped by folio and line
folio_tokens = defaultdict(list)
ac_folios = set()
zodiac_folios_found = set()

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        language = row.get('language', '').strip()
        section = row.get('section', '').strip()
        line_num = row.get('line_number', '0')

        if not word or word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        # Identify AZC folios
        if folio in ZODIAC_FOLIOS:
            zodiac_folios_found.add(folio)
            folio_tokens[folio].append({
                'token': word,
                'line': line_num,
                'family': 'ZODIAC'
            })
        elif language not in ('A', 'B'):
            # A/C family: not Zodiac, not pure A or B
            ac_folios.add(folio)
            folio_tokens[folio].append({
                'token': word,
                'line': line_num,
                'family': 'AC'
            })

print(f"Zodiac folios: {len(zodiac_folios_found)}")
print(f"A/C folios: {len(ac_folios)}")
print()

# ============================================================
# COMPUTE PHASE TRANSITIONS PER FOLIO
# ============================================================

print("=" * 70)
print("COMPUTING HT PHASE TRANSITIONS")
print("=" * 70)
print()

def compute_folio_transitions(tokens):
    """Compute HT phase transitions within a folio."""
    # Group by line to maintain sequence
    lines = defaultdict(list)
    for t in tokens:
        lines[t['line']].append(t['token'])

    # Count phase transitions
    transitions = Counter()
    ht_tokens_classified = 0
    total_tokens = len(tokens)

    for line_tokens in lines.values():
        prev_phase = None
        for token in line_tokens:
            phase = get_ht_phase(token)
            if phase:
                ht_tokens_classified += 1
                if prev_phase and prev_phase != phase:
                    transitions[(prev_phase, phase)] += 1
                prev_phase = phase

    return {
        'total_tokens': total_tokens,
        'ht_classified': ht_tokens_classified,
        'transitions': dict(transitions),
        'total_transitions': sum(transitions.values()),
        'transition_rate': sum(transitions.values()) / total_tokens if total_tokens > 0 else 0
    }

# Compute for all AZC folios
folio_results = {}
zodiac_rates = []
ac_rates = []

for folio, tokens in folio_tokens.items():
    if len(tokens) < 10:  # Skip very sparse folios
        continue

    result = compute_folio_transitions(tokens)
    result['family'] = tokens[0]['family'] if tokens else 'UNKNOWN'
    folio_results[folio] = result

    if result['family'] == 'ZODIAC':
        zodiac_rates.append(result['transition_rate'])
    elif result['family'] == 'AC':
        ac_rates.append(result['transition_rate'])

print(f"Folios with data: {len(folio_results)}")
print(f"  Zodiac: {len(zodiac_rates)}")
print(f"  A/C: {len(ac_rates)}")
print()

# ============================================================
# STATISTICAL COMPARISON
# ============================================================

print("=" * 70)
print("STATISTICAL COMPARISON: A/C vs ZODIAC")
print("=" * 70)
print()

print("TRANSITION RATES (transitions per token):")
print()

if zodiac_rates:
    zodiac_mean = np.mean(zodiac_rates)
    zodiac_std = np.std(zodiac_rates)
    print(f"  ZODIAC: mean = {zodiac_mean:.6f}, std = {zodiac_std:.6f}, n = {len(zodiac_rates)}")
else:
    zodiac_mean = 0
    print("  ZODIAC: No data")

if ac_rates:
    ac_mean = np.mean(ac_rates)
    ac_std = np.std(ac_rates)
    print(f"  A/C:    mean = {ac_mean:.6f}, std = {ac_std:.6f}, n = {len(ac_rates)}")
else:
    ac_mean = 0
    print("  A/C: No data")

print()

# Mann-Whitney U test
if len(zodiac_rates) >= 3 and len(ac_rates) >= 3:
    u_stat, p_value = stats.mannwhitneyu(ac_rates, zodiac_rates, alternative='greater')

    print("Mann-Whitney U test (A/C > Zodiac):")
    print(f"  U-statistic: {u_stat:.2f}")
    print(f"  P-value: {p_value:.6f}")
    print()

    # Effect size (rank-biserial correlation)
    n1, n2 = len(ac_rates), len(zodiac_rates)
    effect_size = 1 - (2 * u_stat) / (n1 * n2)
    print(f"  Effect size (r): {effect_size:.3f}")
    print()

    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if p_value < 0.01 and ac_mean > zodiac_mean:
        verdict = "STRONG SIGNAL"
        interpretation = "A/C folios show significantly higher HT phase-reset frequency than Zodiac"
    elif p_value < 0.05 and ac_mean > zodiac_mean:
        verdict = "WEAK SIGNAL"
        interpretation = "A/C folios show marginally higher HT phase-reset frequency"
    elif p_value > 0.05:
        verdict = "NO SIGNAL"
        interpretation = "A/C and Zodiac show similar HT phase-reset frequencies"
    else:
        verdict = "UNEXPECTED"
        interpretation = "Results do not match prediction"

    print(f"Verdict: {verdict}")
    print(f"P-value: {p_value:.4f} (threshold: 0.05)")
    print()
    print(f"Interpretation: {interpretation}")
else:
    u_stat = 0
    p_value = 1.0
    effect_size = 0
    verdict = "INSUFFICIENT DATA"
    interpretation = "Not enough folios for statistical comparison"
    print(f"Verdict: {verdict}")

# ============================================================
# DETAILED BREAKDOWN
# ============================================================

print()
print("=" * 70)
print("DETAILED BREAKDOWN BY FOLIO")
print("=" * 70)
print()

print(f"{'Folio':<12} {'Family':<10} {'Tokens':>8} {'HT Class':>10} {'Trans':>8} {'Rate':>10}")
print("-" * 68)

for folio in sorted(folio_results.keys()):
    r = folio_results[folio]
    print(f"{folio:<12} {r['family']:<10} {r['total_tokens']:>8} {r['ht_classified']:>10} {r['total_transitions']:>8} {r['transition_rate']:>10.6f}")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    "probe": "AC_HT_PHASE_RESET_FREQUENCY",
    "question": "Do A/C folios force more frequent HT phase transitions than Zodiac?",
    "prediction": "A/C > Zodiac (fine discrimination requires more attention resets)",
    "method": {
        "ht_early_prefixes": HT_EARLY_PREFIXES,
        "ht_late_prefixes": HT_LATE_PREFIXES,
        "metric": "transitions per token"
    },
    "summary": {
        "zodiac_folios": len(zodiac_rates),
        "ac_folios": len(ac_rates),
        "zodiac_mean_rate": float(zodiac_mean) if zodiac_rates else None,
        "ac_mean_rate": float(ac_mean) if ac_rates else None,
        "zodiac_std": float(zodiac_std) if zodiac_rates else None,
        "ac_std": float(ac_std) if ac_rates else None
    },
    "statistical_test": {
        "test": "Mann-Whitney U (one-sided, A/C > Zodiac)",
        "u_statistic": float(u_stat),
        "p_value": float(p_value),
        "effect_size_r": float(effect_size)
    },
    "verdict": verdict,
    "interpretation": interpretation,
    "folio_details": folio_results
}

with open('results/ac_ht_phase_reset.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print()
print(f"Results saved to results/ac_ht_phase_reset.json")
