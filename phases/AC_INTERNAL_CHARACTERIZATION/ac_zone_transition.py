#!/usr/bin/env python3
"""
A/C INTERNAL CHARACTERIZATION - PROBE 3: ZONE-TRANSITION ENTROPY

Question: Do A/C contexts force more frequent zone switching (C↔P↔R↔S)
          than Zodiac?

Method:
1. For each AZC folio, extract zone sequence from token placements
2. Compute transition entropy: Shannon entropy of zone-to-zone bigrams
3. Compare A/C family vs Zodiac family
4. Correlate with HT density (extend C489 baseline r=0.24)

Prediction: A/C will show higher zone-transition entropy - punctuated checkpoints
            require more frequent context switching.
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

# Valid placement zones
ZONES = {'C', 'P', 'R', 'S'}

# Zodiac AZC folios
ZODIAC_FOLIOS = {
    'f70v1', 'f70v2',
    'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3',
    'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v',
    'f57v'
}

def get_zone(placement):
    """Extract zone from placement code."""
    if not placement:
        return None
    placement = placement.strip().upper()

    if placement.startswith('C'):
        return 'C'
    elif placement.startswith('P'):
        return 'P'
    elif placement.startswith('R'):
        return 'R'
    elif placement.startswith('S'):
        return 'S'
    return None

def compute_entropy(counts):
    """Compute Shannon entropy from a counter."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("A/C x ZONE-TRANSITION ENTROPY TEST")
print("=" * 70)
print()
print("Question: Do A/C contexts force more frequent zone switching")
print("          (C<->P<->R<->S) than Zodiac?")
print()

# Load tokens with placement data
folio_zones = defaultdict(list)
folio_family = {}
ac_folios = set()
zodiac_folios_found = set()

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        # CRITICAL: Filter to H-only transcriber track
        transcriber = row.get('transcriber', '').strip()
        if transcriber != 'H':
            continue

        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        language = row.get('language', '').strip()
        placement = row.get('placement', '').strip()
        line_num = row.get('line_number', '0')

        if not word or word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        zone = get_zone(placement)
        if not zone:
            continue

        # Identify AZC folios
        if folio in ZODIAC_FOLIOS:
            zodiac_folios_found.add(folio)
            folio_zones[folio].append({
                'zone': zone,
                'line': line_num,
                'word': word
            })
            folio_family[folio] = 'ZODIAC'
        elif language not in ('A', 'B'):
            ac_folios.add(folio)
            folio_zones[folio].append({
                'zone': zone,
                'line': line_num,
                'word': word
            })
            folio_family[folio] = 'AC'

print(f"Zodiac folios with zone data: {len(zodiac_folios_found)}")
print(f"A/C folios with zone data: {len(ac_folios)}")
print()

# ============================================================
# COMPUTE ZONE-TRANSITION ENTROPY PER FOLIO
# ============================================================

print("=" * 70)
print("COMPUTING ZONE-TRANSITION ENTROPY")
print("=" * 70)
print()

def compute_folio_zone_metrics(tokens):
    """Compute zone-related metrics for a folio."""
    if len(tokens) < 5:
        return None

    # Zone distribution (diversity)
    zone_counts = Counter(t['zone'] for t in tokens)
    zone_diversity = compute_entropy(zone_counts)
    max_diversity = math.log2(len(ZONES)) if len(ZONES) > 0 else 0

    # Zone transitions (bigrams)
    transitions = Counter()
    zone_seq = [t['zone'] for t in tokens]
    for i in range(len(zone_seq) - 1):
        bigram = (zone_seq[i], zone_seq[i+1])
        transitions[bigram] += 1

    # Transition entropy
    transition_entropy = compute_entropy(transitions)
    max_transition_entropy = math.log2(len(ZONES) ** 2) if len(ZONES) > 0 else 0

    # Count actual switches (different zone pairs)
    switches = sum(1 for i in range(len(zone_seq) - 1) if zone_seq[i] != zone_seq[i+1])
    switch_rate = switches / (len(zone_seq) - 1) if len(zone_seq) > 1 else 0

    return {
        'n_tokens': len(tokens),
        'zone_distribution': dict(zone_counts),
        'zone_diversity': zone_diversity,
        'zone_diversity_normalized': zone_diversity / max_diversity if max_diversity > 0 else 0,
        'transition_counts': {f"{k[0]}->{k[1]}": v for k, v in transitions.items()},
        'n_transitions': sum(transitions.values()),
        'transition_entropy': transition_entropy,
        'transition_entropy_normalized': transition_entropy / max_transition_entropy if max_transition_entropy > 0 else 0,
        'n_switches': switches,
        'switch_rate': switch_rate
    }

folio_results = {}
zodiac_entropies = []
zodiac_switch_rates = []
ac_entropies = []
ac_switch_rates = []

for folio, tokens in folio_zones.items():
    result = compute_folio_zone_metrics(tokens)
    if result is None:
        continue

    result['family'] = folio_family.get(folio, 'UNKNOWN')
    folio_results[folio] = result

    if result['family'] == 'ZODIAC':
        zodiac_entropies.append(result['transition_entropy'])
        zodiac_switch_rates.append(result['switch_rate'])
    elif result['family'] == 'AC':
        ac_entropies.append(result['transition_entropy'])
        ac_switch_rates.append(result['switch_rate'])

print(f"Folios with sufficient data: {len(folio_results)}")
print(f"  Zodiac: {len(zodiac_entropies)}")
print(f"  A/C: {len(ac_entropies)}")
print()

# ============================================================
# STATISTICAL COMPARISON
# ============================================================

print("=" * 70)
print("STATISTICAL COMPARISON: A/C vs ZODIAC")
print("=" * 70)
print()

# Metric 1: Transition Entropy
print("TRANSITION ENTROPY (Shannon entropy of zone bigrams):")
print()

if zodiac_entropies:
    zodiac_mean_ent = np.mean(zodiac_entropies)
    zodiac_std_ent = np.std(zodiac_entropies)
    print(f"  ZODIAC: mean = {zodiac_mean_ent:.4f}, std = {zodiac_std_ent:.4f}, n = {len(zodiac_entropies)}")
else:
    zodiac_mean_ent = 0
    print("  ZODIAC: No data")

if ac_entropies:
    ac_mean_ent = np.mean(ac_entropies)
    ac_std_ent = np.std(ac_entropies)
    print(f"  A/C:    mean = {ac_mean_ent:.4f}, std = {ac_std_ent:.4f}, n = {len(ac_entropies)}")
else:
    ac_mean_ent = 0
    print("  A/C: No data")

print()

# Metric 2: Switch Rate
print("SWITCH RATE (fraction of transitions that change zone):")
print()

if zodiac_switch_rates:
    zodiac_mean_sw = np.mean(zodiac_switch_rates)
    zodiac_std_sw = np.std(zodiac_switch_rates)
    print(f"  ZODIAC: mean = {zodiac_mean_sw:.4f}, std = {zodiac_std_sw:.4f}")
else:
    zodiac_mean_sw = 0

if ac_switch_rates:
    ac_mean_sw = np.mean(ac_switch_rates)
    ac_std_sw = np.std(ac_switch_rates)
    print(f"  A/C:    mean = {ac_mean_sw:.4f}, std = {ac_std_sw:.4f}")
else:
    ac_mean_sw = 0

print()

# Statistical tests
if len(zodiac_entropies) >= 3 and len(ac_entropies) >= 3:
    # Test 1: Transition Entropy
    u_stat_ent, p_value_ent = stats.mannwhitneyu(ac_entropies, zodiac_entropies, alternative='greater')
    n1, n2 = len(ac_entropies), len(zodiac_entropies)
    effect_ent = 1 - (2 * u_stat_ent) / (n1 * n2)

    print("Mann-Whitney U test - Transition Entropy (A/C > Zodiac):")
    print(f"  U-statistic: {u_stat_ent:.2f}")
    print(f"  P-value: {p_value_ent:.6f}")
    print(f"  Effect size (r): {effect_ent:.3f}")
    print()

    # Test 2: Switch Rate
    u_stat_sw, p_value_sw = stats.mannwhitneyu(ac_switch_rates, zodiac_switch_rates, alternative='greater')
    effect_sw = 1 - (2 * u_stat_sw) / (n1 * n2)

    print("Mann-Whitney U test - Switch Rate (A/C > Zodiac):")
    print(f"  U-statistic: {u_stat_sw:.2f}")
    print(f"  P-value: {p_value_sw:.6f}")
    print(f"  Effect size (r): {effect_sw:.3f}")
    print()

    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    # Use switch rate as primary metric (more interpretable)
    if p_value_sw < 0.01 and ac_mean_sw > zodiac_mean_sw:
        verdict = "STRONG SIGNAL"
        interpretation = "A/C folios require significantly more frequent zone switching than Zodiac"
    elif p_value_sw < 0.05 and ac_mean_sw > zodiac_mean_sw:
        verdict = "WEAK SIGNAL"
        interpretation = "A/C folios show marginally higher zone-switching frequency"
    elif p_value_sw > 0.05:
        verdict = "NO SIGNAL"
        interpretation = "A/C and Zodiac show similar zone-switching patterns"
    else:
        verdict = "UNEXPECTED"
        interpretation = "Results do not match prediction"

    print(f"Verdict: {verdict}")
    print(f"P-value (switch rate): {p_value_sw:.4f} (threshold: 0.05)")
    print(f"P-value (entropy): {p_value_ent:.4f}")
    print()
    print(f"Interpretation: {interpretation}")
else:
    u_stat_ent = u_stat_sw = 0
    p_value_ent = p_value_sw = 1.0
    effect_ent = effect_sw = 0
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

print(f"{'Folio':<12} {'Family':<10} {'Tokens':>8} {'Diversity':>10} {'Entropy':>10} {'Switches':>10}")
print("-" * 70)

for folio in sorted(folio_results.keys()):
    r = folio_results[folio]
    print(f"{folio:<12} {r['family']:<10} {r['n_tokens']:>8} {r['zone_diversity']:.4f} {r['transition_entropy']:>10.4f} {r['switch_rate']:>10.4f}")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    "probe": "AC_ZONE_TRANSITION_ENTROPY",
    "question": "Do A/C contexts force more frequent zone switching (C↔P↔R↔S)?",
    "prediction": "A/C > Zodiac (punctuated checkpoints require more context switching)",
    "method": {
        "zones": list(ZONES),
        "metrics": ["transition_entropy", "switch_rate"],
        "baseline": "C489 (HT × zone diversity r=0.24)"
    },
    "summary": {
        "zodiac_folios": len(zodiac_entropies),
        "ac_folios": len(ac_entropies),
        "transition_entropy": {
            "zodiac_mean": float(zodiac_mean_ent) if zodiac_entropies else None,
            "ac_mean": float(ac_mean_ent) if ac_entropies else None
        },
        "switch_rate": {
            "zodiac_mean": float(zodiac_mean_sw) if zodiac_switch_rates else None,
            "ac_mean": float(ac_mean_sw) if ac_switch_rates else None
        }
    },
    "statistical_tests": {
        "transition_entropy": {
            "test": "Mann-Whitney U (one-sided, A/C > Zodiac)",
            "u_statistic": float(u_stat_ent),
            "p_value": float(p_value_ent),
            "effect_size_r": float(effect_ent)
        },
        "switch_rate": {
            "test": "Mann-Whitney U (one-sided, A/C > Zodiac)",
            "u_statistic": float(u_stat_sw),
            "p_value": float(p_value_sw),
            "effect_size_r": float(effect_sw)
        }
    },
    "verdict": verdict,
    "interpretation": interpretation,
    "folio_details": folio_results
}

with open('results/ac_zone_transition.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print()
print(f"Results saved to results/ac_zone_transition.json")
